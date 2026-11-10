"""Builds backend-driven fishers for a run, keeps one usage ledger per backend, and estimates cost."""
import json
import math
from pathlib import Path

from .adapter import SUBROUNDS, BackendFisher
from .base import Ledger, bucket_options, report_vocabulary
from .jev import JEV_MODEL, USD_PER_M_INPUT, JevAgent
from .llm import SYSTEM, LLMAgent

BACKEND_KINDS = ("jev", "llm")
CHARS_PER_TOKEN = 3  # ASSUMED conservative (real text is nearer 4) so the estimate is an upper bound
TAG_OVERHEAD = 60


class AgentFactory:
    def __init__(self, temperature=1.0, jev_provider="openrouter", jev_model=JEV_MODEL, llm_model=None,
                 llm_temperature=0.7, llm_price_in=0.0, llm_price_out=0.0, llm_max_tokens=200,
                 cache_dir=None, max_usd=None):
        self.T, self.provider, self.jev_model, self.llm_model = temperature, jev_provider, jev_model, llm_model
        self.llm_T, self.price_in, self.price_out, self.max_tokens = (llm_temperature, llm_price_in, llm_price_out,
                                                                      llm_max_tokens)
        self.cache_dir, self.max_usd = cache_dir, max_usd
        self.ledgers = {}

    def _ledger(self, kind) -> Ledger:
        return self.ledgers.setdefault(kind, Ledger(kind, self.max_usd))

    def make(self, kind, index, rules_text=""):
        if kind == "jev":
            be = JevAgent(self.provider, self.jev_model, self.T, self._ledger("jev"),
                          cache_dir=self.cache_dir)
        elif kind == "llm":
            be = LLMAgent(self.llm_model, self.llm_T, self._ledger("llm"), self.price_in, self.price_out,
                          self.max_tokens)
        else:
            raise ValueError(f"not a backend kind: {kind!r}")
        return BackendFisher(be, kind, index, rules_text)

    def tag(self, names) -> str:
        return f"-T{self.T:g}" if "jev" in names else ""

    def summary(self) -> dict:
        return {k: l.summary() for k, l in self.ledgers.items()}

    def estimate(self, names, months, rules_text="", rounds=1) -> dict:
        """Upper bound: every agent decides every sub-round and reports once a month, nothing cached.
        -> {kind: {"calls", "input_tokens", "usd", "note"}}. LLM usd is 0 until a price is set."""
        obs = {"month": months, "subround": SUBROUNDS, "pool": 100, "month_total": 100, "own_month_total": 100,
               "n_agents": len(names)}
        out = {}
        for kind in BACKEND_KINDS:
            n = names.count(kind)
            if not n:
                continue
            ctx = BackendFisher(None, kind, n, rules_text).context(obs)
            calls = n * months * (SUBROUNDS + 1) * rounds
            if kind == "jev":
                q = json.dumps({"state": ctx, "model": self.jev_model, "questions": {
                    "action": {"type": "choice", "instructions": "x" * 60, "criteria": bucket_options()}}})
                per = math.ceil(max(len(q), len(json.dumps(report_vocabulary())) + len(ctx)) / CHARS_PER_TOKEN)
                out[kind] = {"calls": calls, "input_tokens": calls * per, "usd": calls * per * USD_PER_M_INPUT / 1e6,
                             "note": f"${USD_PER_M_INPUT}/1M input tokens, output free"}
            else:
                per = math.ceil((len(SYSTEM) + len(ctx) + len(json.dumps(bucket_options())) + TAG_OVERHEAD)
                                / CHARS_PER_TOKEN)
                usd = calls * (per * self.price_in + self.max_tokens * self.price_out) / 1e6
                note = (f"{per} input + up to {self.max_tokens} output tokens per call"
                        + ("" if (self.price_in or self.price_out) else "; no price set (--llm-price-in/--llm-price-out), usd shown as 0"))
                out[kind] = {"calls": calls, "input_tokens": calls * per, "usd": usd, "note": note}
        return out
