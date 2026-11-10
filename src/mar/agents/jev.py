"""Jev (TypeSafe) through a decisions endpoint. ASSUMED request and response shapes from a research report,
unverified until a live call: POST {state, questions:{key:{type:"choice", instructions, criteria}}} ->
{model, answers:{key:{choice, confidence, probabilities}}, usage:{input_tokens, output_tokens}, meta:{usd_spent}}.

Pin jev-1.14; "latest" is refused. Jev is overconfident, so probabilities are temperature scaled before
sampling. Raw responses are cached on disk keyed by hash(model, context, questions), so changing T or
re-running a seed costs nothing. There is no seed parameter: sampling happens locally with self.rng.
"""
import hashlib
import json
import random
from pathlib import Path

from . import env, http
from .base import Agent, Ledger, ParseError, Report, sample_label, temperature_scale

JEV_MODEL = "typesafe/jev-1.14"
USD_PER_M_INPUT = 0.042  # output tokens are free
PROVIDERS = {"openrouter": ("https://openrouter.ai/api/alpha/decisions", "OPENROUTER_API_KEY"),
             "aimlapi": ("https://api.aimlapi.com/v1/decisions", "AIMLAPI_API_KEY")}
ACTION_INSTR = "Choose the action this person takes next."
REPORT_INSTR = "Choose the total number of fish this person says they intend to catch this month."


def input_cost(tokens: int) -> float:
    return tokens * USD_PER_M_INPUT / 1e6


class JevAgent(Agent):
    def __init__(self, provider="openrouter", model=JEV_MODEL, temperature=1.0, ledger=None, cache_dir=None,
                 rng=None):
        if provider not in PROVIDERS:
            raise ValueError(f"unknown provider {provider!r}; choose from {sorted(PROVIDERS)}")
        if "latest" in model:
            raise ValueError("pin a build such as typesafe/jev-1.14; jev-latest is refused so runs stay comparable")
        self.provider, self.model, self.T = provider, model, temperature
        self.ledger = ledger or Ledger("jev")
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.rng = rng or random.Random(0)

    def _request(self, context, questions) -> dict:
        key = hashlib.sha256(json.dumps([self.model, context, questions], sort_keys=True).encode()).hexdigest()
        path = self.cache_dir / f"{key}.json" if self.cache_dir else None
        if path and path.exists():
            resp = json.loads(path.read_text(encoding="utf-8"))
            self.ledger.record(resp.get("model"), 0, 0, 0.0, cached=True)
            return resp
        url, key_name = PROVIDERS[self.provider]
        headers = {"Authorization": f"Bearer {env.require_key(key_name)}"}
        resp = http.post_with_retry(url, headers, {"model": self.model, "state": context, "questions": questions})
        usage = resp.get("usage") or {}
        tokens_in = int(usage.get("input_tokens") or 0)
        usd = (resp.get("meta") or {}).get("usd_spent")
        self.ledger.record(resp.get("model"), tokens_in, usage.get("output_tokens"),
                           input_cost(tokens_in) if usd is None else usd)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(resp), encoding="utf-8")
        return resp

    @staticmethod
    def _probs(resp, qkey, options) -> dict:
        try:
            raw = resp["answers"][qkey]["probabilities"]
            probs = {k: float(raw.get(k, 0.0)) for k in options}
            extra = set(raw) - set(options)
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            raise ParseError(f"Jev response has no usable answers[{qkey!r}].probabilities: {e!r}")
        if extra or min(probs.values()) < 0 or sum(probs.values()) <= 0:
            raise ParseError(f"Jev probabilities do not match the options (extra={sorted(extra)}): {raw}")
        return probs

    def decide(self, context, options):
        q = {"action": {"type": "choice", "instructions": ACTION_INSTR, "criteria": dict(options)}}
        return temperature_scale(self._probs(self._request(context, q), "action", options), self.T)

    def message(self, context, vocabulary):
        vocab = dict(vocabulary) if isinstance(vocabulary, dict) else {v: v for v in vocabulary}
        q = {"report": {"type": "choice", "instructions": REPORT_INSTR, "criteria": vocab}}
        probs = temperature_scale(self._probs(self._request(context, q), "report", vocab), self.T)
        return Report(sample_label(probs, self.rng), "intent")
