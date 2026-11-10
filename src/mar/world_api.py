"""World interface for the evolution loop, plus the fishery adapter (ADR 0012).

A world is anything evolve.py can search rules in. It must supply: load_spec, check_spec (proof
checks -> pass / fail / open, with k), run, score, seams, plus the small amount of vocabulary the
mutation operators need (mixes, vocab, propose_patch, feasible). Nothing here edits an existing
module; the fishery adapter reuses fishery, gate, patch_check, oracle, mocks, patcher.

ASSUMED (builder choices, listed in docs/results/evolve.md):
- run_fishery_regrow below is a copy of fishery.run_fishery with the regrowth factor as a parameter
  (the original hard-codes doubling); tests/test_evolve.py checks it matches the original at x2.
- Seam key = (mix, finding kind); score() returns the raw per-run scores evolve.py averages per mix.
- The patcher adapter reads only trace rows and cards; it never imports or calls the oracle.
"""
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

from . import oracle
from .cards import Card, load_cards, make_card
from .fishery import CAPACITY, Run
from .gate import Gate
from .mocks import Compliant, Exploiter
from .patch_check import check_spec as _check_spec
from .patcher import propose_patch as _scripted_patch

RULES = Path(__file__).parent.parent.parent / "rules" / "fishery"
K_DEFAULT = 3


@dataclass(frozen=True)
class CheckResult:
    verdict: str          # "pass" | "fail" | "open"; open never means safe
    k: int
    checks: tuple         # the per-check verdict dicts from patch_check
    failed: tuple         # names of checks that did not pass

    @property
    def ok(self):
        return self.verdict == "pass"


@dataclass(frozen=True)
class Mix:
    name: str
    make: Callable[[], list]   # fresh agents each call
    seeds: tuple = (0,)        # only stochastic mixes need more than one


@dataclass(frozen=True)
class Conditions:
    months: int = 6
    regrowth: float = 2.0
    subrounds: int = 12


class World(Protocol):
    name: str
    objectives: tuple          # score names to maximize in selection

    def load_spec(self, path) -> list: ...
    def check_spec(self, spec, k: int = K_DEFAULT) -> CheckResult: ...
    def run(self, spec, agents, seed: int, conditions: Conditions | None = None) -> Any: ...
    def score(self, trace) -> dict: ...
    def seams(self, trace, spec) -> list: ...
    def mixes(self, split: str) -> list: ...
    def conditions(self, split: str) -> Conditions: ...
    def vocab(self) -> list: ...
    def propose_patch(self, trace, spec, rng) -> list: ...
    def feasible(self, scores: dict) -> bool: ...


# ---------------------------------------------------------------- scripted agents (adapter-local)

class Steady:
    """Same catch every sub-round (size 1 is the trickle)."""
    def __init__(self, size=1):
        self.size = size

    def propose(self, obs):
        return self.size


class Sleeper:
    """Compliant (5 at sub-round 0) until start_month, then max-size every sub-round."""
    def __init__(self, start_month=3, size=10):
        self.start, self.size = start_month, size

    def propose(self, obs):
        if obs["month"] < self.start:
            return 5 if obs["subround"] == 0 else None
        return self.size


class Jitter:
    """Seeded random catch 2..8 with probability 0.5 per sub-round."""
    def propose(self, obs):
        return self.rng.randint(2, 8) if self.rng.random() < 0.5 else None


class LateBurst:
    """Max-size catch only in the last two sub-rounds of each month."""
    def __init__(self, size=10):
        self.size = size

    def propose(self, obs):
        return self.size if obs["subround"] >= 10 else None


class Alternator:
    """Max-size catch on even sub-rounds only."""
    def propose(self, obs):
        return 10 if obs["subround"] % 2 == 0 else None


TRAIN_MIXES = (
    Mix("all_compliant", lambda: [Compliant() for _ in range(4)]),
    Mix("all_exploit", lambda: [Exploiter() for _ in range(4)]),
    Mix("one_exploit", lambda: [Exploiter(), Compliant(), Compliant(), Compliant()]),
    Mix("two_exploit", lambda: [Exploiter(), Exploiter(), Compliant(), Compliant()]),
    Mix("sleeper", lambda: [Sleeper(), Compliant(), Compliant(), Compliant()]),
    Mix("trickle", lambda: [Steady(1) for _ in range(4)]),
    Mix("jitter_mix", lambda: [Jitter(), Jitter(), Compliant(), Compliant()], seeds=(0, 1)),
    Mix("trickle_plus", lambda: [Steady(1), Steady(1), Exploiter(), Compliant()]),
)
EXAM_MIXES = (
    Mix("all_compliant", lambda: [Compliant() for _ in range(4)]),
    Mix("tiny_hoarder", lambda: [Steady(3) for _ in range(4)]),
    Mix("last_minute", lambda: [LateBurst() for _ in range(4)]),
    Mix("mixed_unseen", lambda: [Alternator(), Steady(1), Compliant(), Sleeper(start_month=1)]),
)
TRAIN_CONDITIONS = Conditions(months=6, regrowth=2.0)
EXAM_CONDITIONS = Conditions(months=8, regrowth=1.5)

# expression -> value range used by the mutation operators
VOCAB = (("catch", 0, 100), ("month_total + catch", 0, 100), ("catch - pool", -100, 100),
         ("pool", 0, 100), ("month_total", 0, 100))


# ---------------------------------------------------------------- harness copy with regrowth parameter

def run_fishery_regrow(agents, gate, months=6, subrounds=12, seed=0, capacity=CAPACITY, regrowth=2.0) -> Run:
    """fishery.run_fishery with regrowth as a parameter (x2.0 gives identical traces; tested)."""
    run = Run()
    for i, a in enumerate(agents):
        a.rng = random.Random(seed * 1000 + i)
    pool = capacity
    for month in range(months):
        month_total = 0
        caught = [0] * len(agents)
        for sub in range(subrounds):
            for i, agent in enumerate(agents):
                obs = {"month": month, "subround": sub, "pool": pool, "month_total": month_total,
                       "own_month_total": caught[i], "n_agents": len(agents)}
                proposal = agent.propose(obs)
                if proposal is None:
                    continue
                state = {"pool": pool, "month_total": month_total}
                allowed, reasons = gate.check_action(state, {"catch": proposal}) if gate else (True, [])
                before = pool
                if allowed:
                    taken = max(0, min(proposal, pool))
                    pool -= taken
                    month_total += taken
                    caught[i] += taken
                run.trace.append({"month": month, "subround": sub, "agent": i, "proposed": proposal,
                                  "month_total_before": state["month_total"], "allowed": allowed, "executed": allowed,
                                  "reasons": list(reasons), "pool_before": before, "pool_after": pool})
        pool = min(capacity, int(pool * regrowth))
        run.outcomes.append({"month": month, "pool_end": pool, "catch": list(caught)})
    return run


@dataclass
class FisheryTrace:
    run: Run
    mix: str
    roles: list = field(default_factory=list)   # agent class names, for the yield score
    conditions: Conditions = TRAIN_CONDITIONS


def spec_key(spec) -> tuple:
    return tuple(c.to_yaml() for c in spec)


# ---------------------------------------------------------------- the patcher adapter (never sees the oracle)

def fishery_patch(trace_rows, cards, rng) -> list:
    """Propose new cards from a failing trace's rows and the current cards ONLY. No oracle access."""
    if rng.random() < 1 / 3:
        got = _scripted_patch(trace_rows, cards)
        if got:
            return got
    month_totals = {}
    for r in trace_rows:
        if r["executed"]:
            month_totals[r["month"]] = month_totals.get(r["month"], 0) + (r["pool_before"] - r["pool_after"])
    n = 1 + max([int(c.id[1:]) for c in cards if c.id.startswith("P") and c.id[1:].isdigit()] + [0])
    src = "evolve fixture, scripted patch adapter (ASSUMED); dynamics from GovSim, Piatti et al. 2024, arXiv 2404.16698"
    if month_totals and rng.random() < 0.5:
        cap = max(10, min(90, round(max(month_totals.values()) * rng.choice((0.4, 0.5, 0.6, 0.7)))))
        return [make_card({"id": f"P{n}", "attribute": "fisher", "deontic": "must_not", "aim": "harvest",
                           "conditions": [{"expr": "catch", "op": "gt", "value": 0},
                                          {"expr": "month_total + catch", "op": "gt", "value": cap}],
                           "or_else": {"kind": "suspend", "duration_months": 1, "sanctioner": "monitor"},
                           "gloss": f"Together, fishers may take no more than {cap} fish in one month.", "source": src})]
    r = rng.choice((10, 20, 30, 40))
    return [make_card({"id": f"P{n}", "attribute": "fisher", "deontic": "must_not", "aim": "harvest",
                       "conditions": [{"expr": "catch", "op": "gt", "value": 0}, {"expr": "pool", "op": "lt", "value": r}],
                       "or_else": None,
                       "gloss": f"Fishers may not harvest while the lake holds fewer than {r} fish.", "source": src})]


# ---------------------------------------------------------------- the fishery world

class FisheryWorld:
    name = "fishery"
    objectives = ("sustainability", "fairness", "seam_free")
    YIELD_FLOOR = 0.8

    def __init__(self):
        self._gates = {}

    def load_spec(self, path=RULES):
        return load_cards(path)

    def check_spec(self, spec, k=K_DEFAULT) -> CheckResult:
        checks = tuple(_check_spec(list(spec), k))
        failed = tuple(c["check"] for c in checks if c["verdict"] != "pass")
        verdict = ("fail" if any(c["verdict"] == "fail" for c in checks)
                   else "open" if failed else "pass")
        return CheckResult(verdict, k, checks, failed)

    def _gate(self, spec):
        key = spec_key(spec)
        if key not in self._gates:
            self._gates[key] = Gate(spec)
        return self._gates[key]

    def run(self, spec, agents, seed, conditions=None, mix="?") -> FisheryTrace:
        cond = conditions or TRAIN_CONDITIONS
        roles = [type(a).__name__ for a in agents]
        run = run_fishery_regrow(agents, self._gate(spec), months=cond.months, subrounds=cond.subrounds,
                                 seed=seed, regrowth=cond.regrowth)
        return FisheryTrace(run, mix, roles, cond)

    def score(self, trace) -> dict:
        outs = trace.run.outcomes
        n = len(outs[0]["catch"])
        totals = [sum(o["catch"][a] for o in outs) for a in range(n)]
        # yield floor is measured only where every agent is compliant: the rules must not block
        # compliant behaviour (see the erratum in docs/results/evolve-prereg.md)
        pure = bool(trace.roles) and all(r == "Compliant" for r in trace.roles)
        yld = min(1.0, sum(totals) / (n * len(outs) * 5)) if pure else None
        return {"sustainability": sum(o["pool_end"] for o in outs) / (len(outs) * CAPACITY),
                "fairness": 1.0 - oracle.gini(totals),
                "seam_free": 0.0 if self.seams(trace, None) else 1.0,
                "yield": yld}

    def seams(self, trace, spec=None) -> list:
        """Seam = every executed action passed the gate but the oracle fails the run."""
        if not oracle.is_seam(trace.run.trace, trace.run.outcomes):
            return []
        return [{"mix": trace.mix, "kind": f["kind"], "month": f["month"], "detail": f["detail"]}
                for f in oracle.judge(trace.run.outcomes)["findings"]]

    def mixes(self, split):
        return list(TRAIN_MIXES if split == "train" else EXAM_MIXES)

    def conditions(self, split):
        return TRAIN_CONDITIONS if split == "train" else EXAM_CONDITIONS

    def vocab(self):
        return list(VOCAB)

    def propose_patch(self, trace, spec, rng):
        return fishery_patch(trace.run.trace, spec, rng)

    def feasible(self, scores):
        return scores.get("yield") is None or scores["yield"] >= self.YIELD_FLOOR
