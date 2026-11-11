"""World interface for the evolution loop, plus the fishery adapter (ADR 0012).

A world is anything evolve.py can search rules in. It must supply: load_spec, check_spec (proof
checks -> pass / fail / open, with k), run, score, seams, plus the small amount of vocabulary the
mutation operators need (mixes, vocab, propose_patch, feasible). Nothing here edits an existing
module; the fishery adapter reuses fishery, gate, patch_check, oracle, mocks, patcher. The household evolution world is in
household_world_api.py and is re-exported here lazily (module __getattr__ at the bottom).

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
    start_pool: int = 100


@dataclass(frozen=True)
class Context:
    """One generation's evaluation setting (v2): conditions plus the mixes to run (T1 to T8 and the
    adversary sample). `hostile` names the mixes counted in exploit prevalence. `key` identifies it for caches."""
    conditions: Conditions
    mixes: tuple
    hostile: tuple
    key: tuple


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


class Timed:
    """Adversary family (v2 pool): catches `size` on the sub-rounds its pattern names, from start_month on;
    before that it is compliant (5 at sub-round 0). Patterns: every, even, late (last two), front (first three)."""
    PATTERNS = {"every": lambda sr: True, "even": lambda sr: sr % 2 == 0,
                "late": lambda sr: sr >= 10, "front": lambda sr: sr <= 2}

    def __init__(self, size=10, pattern="every", start_month=0):
        self.size, self.pattern, self.start = size, pattern, start_month

    def propose(self, obs):
        if obs["month"] < self.start:
            return 5 if obs["subround"] == 0 else None
        return self.size if self.PATTERNS[self.pattern](obs["subround"]) else None


class FrontLoad:
    """Exam 2 only: `size` in the first three sub-rounds of every month."""
    def __init__(self, size=8):
        self.size = size

    def propose(self, obs):
        return self.size if obs["subround"] <= 2 else None


class Ramp:
    """Exam 2 only: catch min(10, 1 + 2 * month) every sub-round."""
    def propose(self, obs):
        return min(10, 1 + 2 * obs["month"])


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

# ---- v2 (docs/results/evolve-v2-prereg.md)
def _adv(size, n, pattern, start):
    return Mix(f"adv_s{size}_n{n}_{pattern}_m{start}",
               lambda: [Timed(size, pattern, start) for _ in range(n)] + [Compliant() for _ in range(4 - n)])


ADVERSARY_POOL = tuple(_adv(size, n, pat, start) for size in (5, 7, 10) for n in (1, 2, 3, 4)
                       for pat in ("every", "even", "late", "front") for start in (0, 2))
TRAIN_DIST = {"regrowth": (1.5, 2.0, 2.5, 3.0), "months": (5, 6, 7), "start_pool": (100, 80)}
EXAM2_CONDITIONS = Conditions(months=9, regrowth=1.7, start_pool=60)
EXAM2_MIXES = (
    Mix("all_compliant", lambda: [Compliant() for _ in range(4)]),
    Mix("steady_four", lambda: [Steady(4) for _ in range(4)]),
    Mix("front_load", lambda: [FrontLoad(8) for _ in range(4)]),
    Mix("ramp", lambda: [Ramp(), Ramp(), Compliant(), Compliant()]),
    Mix("late_sleeper", lambda: [Sleeper(start_month=4, size=7), Sleeper(start_month=4, size=7), Compliant(), Compliant()]),
    Mix("mixed_two", lambda: [FrontLoad(8), Steady(2), Compliant(), Compliant()]),
)
REFERENCE_SEED = 7777
EFFICIENCY_REF = 40.0  # total fish per month that counts as full efficiency

# expression -> value range used by the mutation operators
VOCAB = (("catch", 0, 100), ("month_total + catch", 0, 100), ("catch - pool", -100, 100),
         ("pool", 0, 100), ("month_total", 0, 100))


# ---------------------------------------------------------------- harness copy with regrowth parameter

def run_fishery_regrow(agents, gate, months=6, subrounds=12, seed=0, capacity=CAPACITY, regrowth=2.0,
                       start=None) -> Run:
    """fishery.run_fishery with regrowth as a parameter (x2.0 gives identical traces; tested)."""
    run = Run()
    for i, a in enumerate(agents):
        a.rng = random.Random(seed * 1000 + i)
    pool = capacity if start is None else min(capacity, start)
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
    """Propose new cards from a failing trace's rows and the current cards ONLY."""
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
                                 seed=seed, regrowth=cond.regrowth, start=cond.start_pool)
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
                "efficiency": min(1.0, sum(totals) / len(outs) / EFFICIENCY_REF),
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


# ---------------------------------------------------------------- v2 world (four objectives, fresh adversaries)

class FisheryWorldV2(FisheryWorld):
    """Fishery with an efficiency objective, a seam measure that is exploit prevalence against adversaries
    drawn afresh each generation, and the redundancy check. Same runs, scores and patcher as FisheryWorld."""
    name = "fishery-v2"
    objectives = ("sustainability", "fairness", "seam_free", "efficiency")

    def __init__(self):
        super().__init__()
        self._red = {}

    def mixes(self, split):
        return list(EXAM2_MIXES) if split == "exam2" else super().mixes(split)

    def conditions(self, split):
        return EXAM2_CONDITIONS if split == "exam2" else super().conditions(split)

    def hostile(self, split):
        return tuple(m.name for m in EXAM2_MIXES if m.name != "all_compliant") if split == "exam2" else None

    def aggregate(self, per_mix, hostile=None):
        """sustainability, fairness, efficiency: mean over all mixes; seam_free: mean over hostile mixes only."""
        out = {o: _avg([m[o] for m in per_mix.values()]) for o in ("sustainability", "fairness", "efficiency")}
        names = [n for n in per_mix if hostile is None or n in hostile]
        out["seam_free"] = _avg([per_mix[n]["seam_free"] for n in names])
        return out

    def _draw(self, seed, gen, n_sel, n_audit):
        rng = random.Random(f"{seed}-{gen}-adv")
        idx = rng.sample(range(len(ADVERSARY_POOL)), n_sel + n_audit)
        return [ADVERSARY_POOL[i] for i in idx[:n_sel]], [ADVERSARY_POOL[i] for i in idx[n_sel:]]

    def _ctx(self, cond, adv, tag):
        return Context(cond, tuple(TRAIN_MIXES) + tuple(adv), tuple(m.name for m in adv),
                       (tag, cond, tuple(m.name for m in adv)))

    def context(self, seed, gen, arm="fixed", n_sel=6, n_audit=6):
        """-> (selection context, audit context) for one generation. The audit adversaries are disjoint
        from the selection ones; both are redrawn every generation from the fixed pool."""
        sel, aud = self._draw(seed, gen, n_sel, n_audit)
        if arm == "varied":
            rng = random.Random(f"{seed}-{gen}-cond")
            cond = Conditions(months=rng.choice(TRAIN_DIST["months"]), regrowth=rng.choice(TRAIN_DIST["regrowth"]),
                              start_pool=rng.choice(TRAIN_DIST["start_pool"]))
        else:
            cond = TRAIN_CONDITIONS
        return self._ctx(cond, sel, "sel"), self._ctx(cond, aud, "aud")

    def reference_context(self, n=12):
        rng = random.Random(f"{REFERENCE_SEED}-ref")
        adv = [ADVERSARY_POOL[i] for i in rng.sample(range(len(ADVERSARY_POOL)), n)]
        return self._ctx(TRAIN_CONDITIONS, adv, "ref")

    def redundant(self, spec):
        from .redundancy import redundant_cards
        key = spec_key(spec)
        if key not in self._red:
            self._red[key] = redundant_cards(spec)
        return self._red[key]

    def prune(self, spec, prefer_remove=()):
        from .redundancy import prune
        return tuple(prune(spec, prefer_remove))


def _avg(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


# The household evolution world lives in household_world_api.py (split 2026-11-11, docs/notes/repo-split-map.md).
# Its names are re-exported here lazily, so old imports (`world_api.HouseholdEvolveWorld`, `W.hh_run_summary`, ...) keep
# working without this engine module importing the household world at module level.
def __getattr__(name):
    if name.startswith("__"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from . import household_world_api as _hh
    try:
        return getattr(_hh, name)
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
