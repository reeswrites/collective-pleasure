"""Claude backend, batch coordinator and sweep, all against a mocked client. No real calls."""
import json
from pathlib import Path
from types import SimpleNamespace as NS

import anthropic
import httpx2 as httpx
import pytest

from mar.agents import base, http
from mar.agents.base import AgentError, Ledger
from mar.agents.batch import BatchCoordinator, run_lockstep
from mar.agents.claude import ClaudeAgent, claude_cost
from mar.cli import main

RULES = str(Path(__file__).parent.parent / "rules" / "fishery")
OPTS = base.bucket_options()
STATE = "\n\nCurrent state:\n"


def msg(text='{"action":"1-10","report":"1-10","talk":"hi"}', stop="end_turn", usage=None, cat=None, blocks=None):
    u = usage or dict(input_tokens=100, output_tokens=20, cache_read_input_tokens=0, cache_creation_input_tokens=0)
    return NS(model="claude-haiku-5-5", stop_reason=stop, usage=NS(**u),
              stop_details=NS(category=cat) if cat else None,
              content=blocks if blocks is not None else [NS(type="text", text=text)])


class FakeClient:
    def __init__(self, replies):
        self.replies, self.calls = replies, []
        self.messages = NS(create=self.create)

    def create(self, **kw):
        self.calls.append(kw)
        r = self.replies(kw) if callable(self.replies) else self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return r


def status_error(cls, code):
    resp = httpx.Response(code, request=httpx.Request("POST", "http://x"))
    return cls("boom", response=resp, body=None)


def test_requires_explicit_model_and_lists_prices():
    with pytest.raises(ValueError, match="claude-haiku-5-5 \\$0.1/\\$0.5"):
        ClaudeAgent(None)


def test_request_shape_no_forbidden_params_and_cached_stable_prefix():
    c = FakeClient(lambda kw: msg())
    a = ClaudeAgent("claude-haiku-5-5", client=c)
    ctx1 = "Rules: F1.\nYou are fisher 0." + STATE + "Month 0, round 1."
    ctx2 = "Rules: F1.\nYou are fisher 0." + STATE + "Month 3, round 7. Different."
    assert a.decide(ctx1, OPTS)["1-10"] == 1.0
    a.decide(ctx2, OPTS)
    k1, k2 = c.calls
    assert k1["model"] == "claude-haiku-5-5" and k1["max_tokens"] == 1024 and k1["output_config"] == {"effort": "low"}
    for bad in ("temperature", "top_p", "top_k", "thinking"):
        assert bad not in k1
    sys1 = k1["system"]
    assert sys1[0]["type"] == "text" and sys1[0]["cache_control"] == {"type": "ephemeral"}
    assert sys1 == k2["system"] and "Rules: F1." in sys1[0]["text"] and "Month" not in sys1[0]["text"]
    assert "Month 0" in k1["messages"][0]["content"] and "Month 3" in k2["messages"][0]["content"]


def test_message_and_usage_cost_with_cache_tokens():
    u = dict(input_tokens=1000, output_tokens=100, cache_read_input_tokens=5000, cache_creation_input_tokens=2000)
    c = FakeClient([msg('{"report":"11-20","talk":"more"}', usage=u)])
    led = Ledger("claude")
    rep = ClaudeAgent("claude-sonnet-5-5", ledger=led, client=c).message("c" + STATE + "s", base.BUCKET_LABELS)
    assert (rep.value, rep.talk) == ("11-20", "more")
    s = led.summary()
    expect = (1000 * 2 + 5000 * 2 * 0.1 + 2000 * 2 * 1.25 + 100 * 10) / 1e6
    assert s["usd"] == pytest.approx(expect) and s["cache_read_tokens"] == 5000 and s["cache_write_tokens"] == 2000
    assert s["model_builds"] == ["claude-haiku-5-5"] and s["input_tokens"] == 1000 and s["refusals"] == 0
    assert claude_cost("claude-opus-5-5", 1_000_000, 1_000_000, batch=True) == pytest.approx(12.0)
    assert claude_cost("unknown", 1, 1) is None


def test_refusal_is_noop_and_counted_and_never_reads_content():
    c = FakeClient([msg(stop="refusal", cat="cyber", blocks=[])])
    led = Ledger("claude")
    a = ClaudeAgent("claude-haiku-5-5", ledger=led, client=c)
    assert a.decide("c" + STATE + "s", OPTS)["0"] == 1.0
    s = led.summary()
    assert s["refusals"] == 1 and s["refusal_categories"] == ["cyber"]
    c2 = FakeClient([msg(stop="refusal", blocks=[])])
    assert ClaudeAgent("claude-haiku-5-5", client=c2).message("c", base.BUCKET_LABELS).talk == "[refused]"


def test_max_tokens_and_bad_json_retry_once_then_error():
    c = FakeClient([msg(stop="max_tokens", text="{\"act"), msg('{"action":"0"}')])
    assert ClaudeAgent("claude-haiku-5-5", client=c).decide("c" + STATE + "s", OPTS)["0"] == 1.0
    assert len(c.calls) == 2 and "invalid" in c.calls[1]["messages"][-1]["content"]
    c = FakeClient([msg("not json"), msg("still not")])
    with pytest.raises(base.ParseError):
        ClaudeAgent("claude-haiku-5-5", client=c).decide("c" + STATE + "s", OPTS)


def test_only_text_blocks_are_read():
    blocks = [NS(type="thinking", thinking="x"), NS(type="text", text='{"action":"1-10"}')]
    c = FakeClient([msg(blocks=blocks)])
    assert ClaudeAgent("claude-haiku-5-5", client=c).decide("c" + STATE + "s", OPTS)["1-10"] == 1.0


def test_error_handling_order(monkeypatch):
    monkeypatch.setattr(http, "sleep", lambda s: None)
    c = FakeClient([status_error(anthropic.InternalServerError, 500), msg()])
    assert ClaudeAgent("claude-haiku-5-5", client=c).decide("c" + STATE + "s", OPTS)
    assert len(c.calls) == 2  # 5xx retried
    c = FakeClient(lambda kw: status_error(anthropic.RateLimitError, 429))
    with pytest.raises(AgentError, match="rate limit"):
        ClaudeAgent("claude-haiku-5-5", client=c).decide("c", OPTS)
    assert len(c.calls) == 1
    c = FakeClient(lambda kw: status_error(anthropic.AuthenticationError, 401))
    with pytest.raises(AgentError, match="ANTHROPIC_API_KEY"):
        ClaudeAgent("claude-haiku-5-5", client=c).decide("c", OPTS)
    c = FakeClient(lambda kw: anthropic.APIConnectionError(request=httpx.Request("POST", "http://x")))
    with pytest.raises(AgentError, match="reach"):
        ClaudeAgent("claude-haiku-5-5", client=c).decide("c", OPTS)
    c = FakeClient(lambda kw: status_error(anthropic.InternalServerError, 503))
    with pytest.raises(AgentError, match="503"):
        ClaudeAgent("claude-haiku-5-5", client=c).decide("c", OPTS)
    assert len(c.calls) == 3


# ---- batch ---------------------------------------------------------------------------------

class FakeBatches:
    def __init__(self, answer, polls_before_end=1, reverse=True):
        self.answer, self.polls, self.reverse = answer, polls_before_end, reverse
        self.created, self.retrieved = [], 0

    def create(self, requests):
        self.created.append(requests)
        return NS(id=f"b{len(self.created)}")

    def retrieve(self, bid):
        self.retrieved += 1
        return NS(processing_status="ended" if self.retrieved > self.polls else "in_progress")

    def results(self, bid):
        reqs = self.created[int(bid[1:]) - 1]
        out = [NS(custom_id=r["custom_id"], result=NS(type="succeeded", message=self.answer(r))) for r in reqs]
        return reversed(out) if self.reverse else out  # shuffled: results must be matched by custom_id


def batch_client(batches):
    return NS(messages=NS(batches=batches))


def test_coordinator_lockstep_one_batch_per_step_matched_by_custom_id():
    # each run's agent echoes its own custom_id's run number in "talk"
    def answer(req):
        who = req["custom_id"].split("-")[0]
        return msg(json.dumps({"report": "0", "talk": who}))
    fb = FakeBatches(answer)
    waits = []
    coord = BatchCoordinator(batch_client(fb), 3, poll_s=5, sleep=waits.append)

    def job(seed):
        def go():
            a = ClaudeAgent("claude-haiku-5-5", transport=lambda p: coord.request(f"r{seed}-a0-c{n[0]}", p), batch=True)
            n = [0]
            talks = []
            for step in range(2):
                n[0] += 1
                rep = a.message("c" + STATE + f"step{step}", ["0"])
                talks.append(rep.talk)
            return talks, a.ledger.summary()
        return go
    out = run_lockstep(coord, [job(s) for s in (7, 8, 9)])
    assert [r[0][0] for r in out] == [["r7", "r7"], ["r8", "r8"], ["r9", "r9"]] and all(r[1] is None for r in out)
    assert len(fb.created) == 2 and all(len(b) == 3 for b in fb.created)  # one batch per step, one request per run
    assert waits  # polled
    expect = claude_cost("claude-haiku-5-5", 100, 20, batch=True)
    assert out[0][0][1]["usd"] == pytest.approx(2 * expect)  # 50% price recorded


def test_coordinator_failed_batch_raises_in_each_run():
    class Boom(FakeBatches):
        def create(self, requests):
            raise RuntimeError("down")
    coord = BatchCoordinator(batch_client(Boom(None)), 2, sleep=lambda s: None)

    def go():
        return coord.request("r0-a0-c1", {})
    out = run_lockstep(coord, [go, lambda: coord.request("r1-a0-c1", {})])
    assert all(isinstance(e, AgentError) and "batch failed" in str(e) for _, e in out)


def test_sweep_non_batch_and_batch_via_cli(capsys, tmp_path, monkeypatch):
    fb = FakeBatches(lambda r: msg())
    monkeypatch.setattr(anthropic, "Anthropic", lambda *a, **k: batch_client(fb))
    monkeypatch.setattr("mar.agents.batch.time.sleep", lambda s: None)
    code = main(["--runs-dir", str(tmp_path / "r"), "--experiments-dir", str(tmp_path / "e"), "sweep", "--spec", RULES,
                 "--agents", "claude*2", "--claude-model", "claude-haiku-5-5", "--months", "1", "--seeds", "0,1",
                 "--batch", "--poll-seconds", "0"])
    out = capsys.readouterr()
    assert code == 0, out.err
    rows = [json.loads(l) for l in (tmp_path / "e" / "log.jsonl").read_text().splitlines()]
    assert len(rows) == 2 and rows[0]["backends"]["claude"]["model_builds"] == ["claude-haiku-5-5"]
    assert len(fb.created) == 13 * 2  # one batch per agent-step, 2 agents act in turn, 13 calls each
    assert all(len(b) == 2 for b in fb.created)  # two seeds per step
    custom = {r["custom_id"] for b in fb.created for r in b}
    assert all(c.startswith(("r0-", "r1-")) for c in custom)


def test_claude_dry_run_prices_batch_and_cache_share(capsys, tmp_path):
    def dry(*extra):
        main(["--runs-dir", str(tmp_path), "--experiments-dir", str(tmp_path), "run", "--spec", RULES, "--agents",
              "claude*5", "--months", "6", "--dry-run", "--claude-model", "claude-sonnet-5-5", *extra])
        return capsys.readouterr().out

    o1, o2 = dry(), dry("--cache-hit-share", "0.8")
    assert "claude: up to 390 calls" in o1 and "with --batch $" in o1 and "cache hit share 0" in o1
    def usd(o):
        return float(o.split("cost $")[1].split(";")[0])
    assert usd(o2) < usd(o1)
    b = float(o1.split("with --batch $")[1].split(" ")[0])
    assert b == pytest.approx(usd(o1) / 2, abs=1e-4)
    assert main(["--runs-dir", str(tmp_path), "run", "--spec", RULES, "--agents", "claude*1", "--dry-run"]) == 2


def test_claude_run_via_cli_needs_model_and_logs_refusals(capsys, tmp_path, monkeypatch):
    args = ["--runs-dir", str(tmp_path / "r"), "--experiments-dir", str(tmp_path / "e"), "run", "--spec", RULES,
            "--agents", "claude*1", "--months", "1"]
    assert main(args) == 2 and "--model" in capsys.readouterr().err
    client = FakeClient(lambda kw: msg(stop="refusal", cat="x", blocks=[]))
    monkeypatch.setattr(anthropic, "Anthropic", lambda *a, **k: client)
    assert main(args + ["--model", "claude-haiku-5-5"]) == 0
    row = json.loads((tmp_path / "e" / "log.jsonl").read_text().splitlines()[0])
    assert row["backends"]["claude"]["refusals"] == 13 and row["cost_usd"] > 0
