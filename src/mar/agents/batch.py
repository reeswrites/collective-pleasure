"""Message Batches for overnight sweeps (`mar sweep --backend claude --batch`). 50% cost, can take a long time
(a batch may take up to 24 hours to end), so this is NOT for interactive demos.

Lockstep: each simulation run lives in its own thread. When a run's agent needs a decision it calls
BatchCoordinator.request(); once every live run is waiting, the coordinator submits ONE batch holding one request
per run (custom_id per run, agent and call), polls until processing_status is "ended", and hands each result back
by custom_id, never by position.

ASSUMED / TODO: the request and result handling below is exercised only against a mocked client. The live loop has
never run; expect to adjust it on first contact (result types other than "succeeded" are treated as errors).
"""
import re
import threading
import time

from .base import AgentError

CUSTOM_ID_OK = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


class BatchCoordinator:
    def __init__(self, client, n_runs, poll_s=30.0, sleep=time.sleep, max_polls=None):
        self.client, self.alive, self.poll_s, self.sleep, self.max_polls = client, n_runs, poll_s, sleep, max_polls
        self.cond = threading.Condition()
        self.pending, self.results, self.batches = {}, {}, []

    # -- called from run threads ------------------------------------------------------------
    def request(self, custom_id, params):
        if not CUSTOM_ID_OK.match(custom_id):
            raise ValueError(f"bad custom_id {custom_id!r}")
        with self.cond:
            self.pending[custom_id] = params
            self.cond.notify_all()
            self.cond.wait_for(lambda: custom_id in self.results)
            ok, val = self.results.pop(custom_id)
        if not ok:
            raise AgentError(val)
        return val

    def run_finished(self):
        with self.cond:
            self.alive -= 1
            self.cond.notify_all()

    # -- coordinator (main thread) -----------------------------------------------------------
    def serve(self):
        while True:
            with self.cond:
                self.cond.wait_for(lambda: self.alive == 0 or len(self.pending) >= self.alive)
                if not self.pending:
                    if self.alive == 0:
                        return
                    continue
                batch, self.pending = self.pending, {}
            outcome = self._run_batch(batch)
            with self.cond:
                self.results.update(outcome)
                self.cond.notify_all()

    def _run_batch(self, batch) -> dict:
        try:
            b = self.client.messages.batches.create(
                requests=[{"custom_id": cid, "params": p} for cid, p in batch.items()])
            self.batches.append(b.id)
            polls = 0
            while True:
                cur = self.client.messages.batches.retrieve(b.id)
                if cur.processing_status == "ended":
                    break
                polls += 1
                if self.max_polls is not None and polls >= self.max_polls:
                    raise AgentError(f"batch {b.id} did not end after {polls} polls")
                self.sleep(self.poll_s)
            out = {}
            for entry in self.client.messages.batches.results(b.id):
                r = entry.result
                if r.type == "succeeded":
                    out[entry.custom_id] = (True, r.message)
                else:
                    out[entry.custom_id] = (False, f"batch request {entry.custom_id} {r.type}")
            for cid in batch:  # never trust position: anything missing is an error
                out.setdefault(cid, (False, f"batch result for {cid} missing"))
            return {cid: v for cid, v in out.items() if cid in batch}
        except Exception as e:
            msg = e if isinstance(e, AgentError) else AgentError(f"batch failed: {e}")
            return {cid: (False, str(msg)) for cid in batch}


def run_lockstep(coordinator, jobs):
    """jobs: list of zero-argument callables, one per run. Returns [(result, error)] in job order."""
    out = [None] * len(jobs)

    def wrap(i, job):
        try:
            out[i] = (job(), None)
        except BaseException as e:  # reported to the caller, never swallowed
            out[i] = (None, e)
        finally:
            coordinator.run_finished()

    threads = [threading.Thread(target=wrap, args=(i, j), daemon=True) for i, j in enumerate(jobs)]
    for t in threads:
        t.start()
    coordinator.serve()
    for t in threads:
        t.join()
    return out
