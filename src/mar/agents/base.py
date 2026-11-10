"""Backend interface, shared helpers and the usage ledger.

  decide(context, options)     -> {option: probability}
  message(context, vocabulary) -> Report (typed talk: one word from a fixed vocabulary, plus optional free talk)

Numeric catches are bucketed (11 buckets: 0, 1-10, ..., 91-100); a bucket is sampled, then a number is
sampled uniformly inside it. Sampling uses a caller-supplied seeded RNG, never a global one.
"""
import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass


class AgentError(ValueError):
    """Base for errors the CLI should print plainly (exit code 2)."""


class MissingKeyError(AgentError):
    pass


class ParseError(AgentError):
    pass


class BudgetExceeded(AgentError):
    pass


# ---- buckets -------------------------------------------------------------------------------

BUCKETS = [(0, 0)] + [(10 * i + 1, 10 * (i + 1)) for i in range(10)]


def _label(lo, hi) -> str:
    return "0" if hi == 0 else f"{lo}-{hi}"


BUCKET_LABELS = [_label(lo, hi) for lo, hi in BUCKETS]


def bucket_options() -> dict:
    """option -> description, in order, for numeric catches."""
    return {lab: ("Take no fish." if lab == "0" else f"Take between {lab.split('-')[0]} and {lab.split('-')[1]} fish.")
            for lab in BUCKET_LABELS}


def bucket_of(n: int) -> str:
    n = max(0, min(100, int(n)))
    for (lo, hi), lab in zip(BUCKETS, BUCKET_LABELS):
        if lo <= n <= hi:
            return lab
    raise AssertionError("unreachable")


def sample_in_bucket(label: str, rng: random.Random) -> int:
    if label not in BUCKET_LABELS:
        raise ValueError(f"unknown bucket {label!r}")
    lo, hi = BUCKETS[BUCKET_LABELS.index(label)]
    return rng.randint(lo, hi)


# ---- probabilities -------------------------------------------------------------------------

def temperature_scale(probs: dict, T: float) -> dict:
    """p^(1/T), renormalized. T > 1 flattens (use it on an overconfident model), T < 1 sharpens."""
    if T <= 0:
        raise ValueError("temperature must be positive")
    w = {k: (p ** (1.0 / T) if p > 0 else 0.0) for k, p in probs.items()}
    total = sum(w.values())
    if total <= 0 or not math.isfinite(total):
        raise ParseError("probabilities are all zero or not finite")
    return {k: v / total for k, v in w.items()}


def sample_label(probs: dict, rng: random.Random) -> str:
    """Draw one key. Key order is the tie-break, so the draw is deterministic for a given RNG state."""
    total = sum(probs.values())
    x = rng.random() * total
    acc, last = 0.0, None
    for k, p in probs.items():
        if p <= 0:
            continue
        acc += p
        last = k
        if x < acc:
            return k
    if last is None:
        raise ParseError("no option has positive probability")
    return last


# ---- typed report --------------------------------------------------------------------------

@dataclass
class Report:
    value: str          # one word from the vocabulary
    kind: str = "intent"
    talk: str = ""      # free text; only LLM backends fill it


# ---- usage ---------------------------------------------------------------------------------

class Ledger:
    """Records every backend call: exact model build, tokens, usd, cached or not."""

    def __init__(self, backend: str, limit_usd: float | None = None):
        self.backend, self.limit_usd, self.calls = backend, limit_usd, []

    def record(self, model_build, input_tokens, output_tokens, usd, cached=False):
        self.calls.append({"model_build": model_build, "input_tokens": int(input_tokens or 0),
                           "output_tokens": int(output_tokens or 0), "usd": float(usd or 0.0), "cached": bool(cached)})
        if self.limit_usd is not None and self.total_usd() > self.limit_usd:
            raise BudgetExceeded(f"{self.backend}: spend ${self.total_usd():.4f} passed the limit "
                                 f"${self.limit_usd:.4f}; stopping.")

    def total_usd(self) -> float:
        return sum(c["usd"] for c in self.calls)

    def summary(self) -> dict:
        live = [c for c in self.calls if not c["cached"]]
        return {"model_builds": sorted({c["model_build"] for c in self.calls if c["model_build"]}),
                "calls": len(live), "cache_hits": len(self.calls) - len(live),
                "input_tokens": sum(c["input_tokens"] for c in live),
                "output_tokens": sum(c["output_tokens"] for c in live),
                "usd": round(self.total_usd(), 6)}


class Agent(ABC):
    rng: random.Random

    @abstractmethod
    def decide(self, context: str, options: dict) -> dict:
        """options: {key: description}. Returns {key: probability} over the same keys, summing to 1."""

    @abstractmethod
    def message(self, context: str, vocabulary) -> Report:
        """vocabulary: list of words, or {word: description}. Returns a typed report with value in vocabulary."""
