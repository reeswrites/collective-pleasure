"""Plugs a backend into the fishery harness (which only calls propose(obs)).

Each sub-round the agent decides a catch bucket, a number is sampled inside it, and that is the proposal.
At the first sub-round of a month it also files a typed report of its intended month total. Reports are
kept in self.reports for the trace; report.py adds what the agent actually did.
"""
from .base import BUCKET_LABELS, bucket_options, report_vocabulary, sample_in_bucket, sample_label

SUBROUNDS = 12  # fishery.run_fishery default
STATE_MARK = "\n\nCurrent state:\n"  # everything before this is stable per agent (cacheable); after it changes each step


class BackendFisher:
    def __init__(self, backend, kind, index, rules_text=""):
        self.backend, self.kind, self.index, self.rules_text = backend, kind, index, rules_text
        self.reports = []

    def context(self, obs) -> str:
        head = f"Rules: {self.rules_text}\n" if self.rules_text else ""
        return (f"{head}You are fisher {self.index} of {obs['n_agents']} sharing a lake (at most 100 fish; the stock "
                f"left at month end doubles, up to 100). Each month has {SUBROUNDS} rounds."
                f"{STATE_MARK}Month {obs['month']}, round {obs['subround'] + 1} of {SUBROUNDS}. "
                f"The lake holds {obs['pool']} fish. The group has caught {obs['month_total']} this month; "
                f"you have caught {obs['own_month_total']}.")

    def propose(self, obs):
        self.backend.rng = self.rng
        ctx = self.context(obs)
        if obs["subround"] == 0:
            rep = self.backend.message(ctx, report_vocabulary())
            self.reports.append({"month": obs["month"], "agent": self.index, "kind": self.kind,
                                 "report": rep.value, "report_kind": rep.kind, "talk": rep.talk})
        probs = self.backend.decide(ctx, bucket_options())
        return sample_in_bucket(sample_label(probs, self.rng), self.rng)
