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


# =====================================================================================================================
# Household world for the evolution loop (first household evolution run; docs/results/household-evolve-prereg.md).
# Scripted persona-driven agents, no model calls. Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for
# a modeled hedonic state derived from each persona's assigned preferences.
#
# The exam (docs/results/household-exam-prereg.md) is NOT in this module. The only thing taken from its section 1 is the
# six-id DENYLIST below (a mechanical rule: first byte of SHA-256 of the id < 48; `held_out_by_rule` recomputes it and a
# test asserts the two agree). Nothing else from the exam document appears in any evolution code, config, test or log.
# =====================================================================================================================
import dataclasses
import hashlib
import json as _json
from itertools import combinations as _combinations

from . import empowerment as _E
from . import household_oracle as _O
from . import hedonic as _HD
from . import lint as _lint
from . import liberty as _L
from . import negotiation as _NG
from . import personas as _P
from .worlds import household as _H

_ROOT = Path(__file__).parent.parent.parent
HH_RULES = _ROOT / "rules" / "household"
DENYLIST = ("g-10010", "g-10110", "g-11101", "g-01110", "g-11000", "g-00101")   # held out of every training use (exam doc section 1)
HAND_IDS = ("p-anchor", "p-bargainer", "p-host", "p-peacekeeper", "p-steward", "p-wanderer")
PRESSING_IDS = ("p-controller", "p-freerider", "p-overasker")
# training distribution (the ranges the exam doc permits training to draw from; everything outside them is the exam's)
TRAIN_WEEKS = (104, 130, 156)
TRAIN_SHOCK_MULT = (0.5, 1.5)          # job loss, illness, move: multiples of the defaults
TRAIN_NEW_CONNECTION = (0.15, 0.30)
TRAIN_START = (-0.1, -0.05, 0.0, 0.05, 0.1)
TRAIN_SEEDS = range(100, 900)
HH_NORM = {"liberty": 6.0}             # liberty bits that count as 1.0 in the elite's mean-of-objectives pick (ASSUMED)
HH_LIBRARY_VARIANTS = ("baseline", "needs_duty", "share_duty", "no_pressure_wall", "no_pressure_sanctioned", "exit_half",
                       "veto_consent", "author_seed", "author_seed_nocontrol", "free_chaotic",
                       "author_seed_v2_bindable", "author_seed_v2_free_exit")   # patch library: trap and contact_free are controls built to fail
TERM_PREFIX = {"contribution": ("N1",), "use": ("N2",), "taking": ("N3",), "change": ("N4",), "exit": ("N5",),
               "stay": ("N6",), "requests": ("N7", "N8")}
SANCTION_KINDS = ("warn", "cap_halve", "suspend")


def held_out_by_rule(ids):
    """The exam's mechanical rule: held out iff the first byte of SHA-256(id) is below 48."""
    return sorted(i for i in ids if hashlib.sha256(i.encode("utf-8")).digest()[0] < 48)


_PERSONAS = {}


def hh_personas():
    """id -> persona for the hand, pressing and grid directories (all 41)."""
    if not _PERSONAS:
        for d in (_ROOT / "personas", _ROOT / "personas" / "pressing", _ROOT / "personas" / "grid"):
            _PERSONAS.update({p.id: p for p in _P.load_dir(d)})
    return _PERSONAS


def training_persona_ids():
    return sorted(i for i in hh_personas() if i not in DENYLIST)


def _pairing_pool():
    """All training pairings (a, b): ordered, a != b, neither denylisted. Split by a hash into `train` (selection) and `val` (never
    selected on, used for the overfitting gap)."""
    ids = training_persona_ids()
    hand = [i for i in ids if i in HAND_IDS]
    press = [i for i in ids if i in PRESSING_IDS]
    grid = [i for i in ids if i.startswith("g-")]
    out = []
    for a, b in _combinations(hand, 2):
        out.append((a, b, "hand"))
    for p in press:
        for o in hand + press + grid[::3]:
            if o != p:
                out += [(p, o, "press"), (o, p, "press")]
    for a, b in _combinations(grid, 2):
        out.append((a, b, "grid"))
    for g in grid:
        for h in hand:
            out.append((min(g, h), max(g, h), "gridhand"))
    seen, uniq = set(), []
    for a, b, c in out:
        if (a, b) not in seen:
            seen.add((a, b))
            uniq.append((a, b, c))
    return uniq


def pairing_split(a, b):
    """'val' for about a fifth of the pairings, by a hash of the pair (stable), else 'train'."""
    return "val" if hashlib.sha256(f"{a}|{b}".encode()).digest()[1] % 5 == 0 else "train"


@dataclass(frozen=True)
class HRun:
    a: str
    b: str
    seed: int
    weeks: int
    rates: tuple          # (job_loss, illness, move, new_connection)
    start: float


@dataclass(frozen=True)
class HContext:
    """One generation's evaluation setting: the runs every candidate is scored on (common random numbers)."""
    runs: tuple
    key: tuple


def _draw_run(rng, pool):
    a, b, cohort = pool[rng.randrange(len(pool))]
    d = _HD.DEFAULT
    return HRun(a, b, rng.choice(TRAIN_SEEDS), rng.choice(TRAIN_WEEKS),
                (round(d.job_loss_rate * rng.uniform(*TRAIN_SHOCK_MULT), 4), round(d.illness_rate * rng.uniform(*TRAIN_SHOCK_MULT), 4),
                 round(d.move_rate * rng.uniform(*TRAIN_SHOCK_MULT), 4), round(rng.uniform(*TRAIN_NEW_CONNECTION), 3)),
                rng.choice(TRAIN_START))


def make_context(seed, gen, n_runs, split="train", tag="sel"):
    """Deterministic draw of n_runs from the `split` pairing pool under the training distribution."""
    pool = [p for p in _pairing_pool() if pairing_split(p[0], p[1]) == split]
    rng = random.Random(f"{seed}|{gen}|{tag}|{split}")
    runs = tuple(_draw_run(rng, pool) for _ in range(n_runs))
    return HContext(runs, (tag, split, seed, gen, n_runs))


def run_key(spec):
    return tuple(c.to_yaml() for c in spec)


def _with_rates(rates, fn):
    """Run fn with the household world's module-level shock rates set (restored afterwards; one process = one run at a time)."""
    saved = dict(_H.SHOCK_RATES)
    _H.SHOCK_RATES.update(zip(("job_loss", "illness", "move", "new_connection"), rates))
    try:
        return fn()
    finally:
        _H.SHOCK_RATES.clear()
        _H.SHOCK_RATES.update(saved)


_LIB_MEMO = {}


def hh_run_summary(gate, hr, snapshots=_L.HH_SNAPSHOTS, k=_L.HH_K, plain_k=None):
    """Run one household (rule gate, HRun) and return the per-run scalars used everywhere (training and, with other settings, the exam)."""
    ps = hh_personas()
    d = _HD.DEFAULT
    cfg = dataclasses.replace(d, job_loss_rate=hr.rates[0], illness_rate=hr.rates[1], move_rate=hr.rates[2],
                              new_connection_rate=hr.rates[3], start=hr.start)
    r = _with_rates(hr.rates, lambda: _L.household_run_liberty(gate, (ps[hr.a], ps[hr.b]), hr.seed, hr.weeks, snapshots, k, cfg=cfg))
    out = r["run"].outcomes
    sc, hs = _O.score(out), _O.hedonic_summary(out)
    tr = r["run"].trace
    return {"pleasure": hs["pleasure"], "fail": bool(hs["fail"]), "cooperation": sc["cooperation"], "freedom": sc["freedom"],
            "liberty": r["liberty_min"], "bits": r["bits_min"], "s_non": hs["s_non"], "up": bool(hs["pairing_up"]),
            "down": any(c == "down" for c in hs["class"].values()),
            "left": sum(1 for x in "AB" if not out[-1]["partners"][x]["in"]),
            "n_open": r["n_open"],
            "events": {"veto": sum(1 for t in tr if t["action"] == "veto" and t["executed"]),
                       "leave_blocked": sum(1 for t in tr if t["action"] == "leave" and not t["allowed"]),
                       "take": sum(1 for t in tr if t["action"] == "take_shared" and t["executed"]),
                       "request": sum(1 for t in tr if t["action"] == "request" and t["executed"]),
                       "sanctioned": sum(sum(o["sanctioned"].values()) for o in out)}}


# ---------------------------------------------------------------- redundancy (household): logical only, partner cards

def _hh_actions(card):
    return (_H.PARTNER_ACTIONS + _H.EXTRA_ACTIONS + ("veto", "take_shared")) if card.aim == "any" else (card.aim,)


def hh_redundant_cards(cards) -> list:
    """Ids of must / must_not partner cards implied by the conjunction of the others over the bounded domain (or forbidding nothing).
    A card is redundant when, for every action it governs, no state and take exist that the other cards allow and it forbids
    (z3, bounded by household.BOUNDS). Permissions (`may`) add no constraint and are never flagged (a `may` can switch on a world mechanism, so
    removing one is not a logical question). Sanctions and glosses are ignored (ASSUMED). A solver 'unknown' counts as NOT redundant."""
    import z3
    cards = list(cards)
    out = []
    for i, c in enumerate(cards):
        if c.deontic == "may" or c.attribute != "partner":
            continue
        others = cards[:i] + cards[i + 1:]
        with _H.household_namespace():
            v = _H._compile.violation(c)
        redundant = True
        for act in _hh_actions(c):
            vs = _H.violations(others, act)
            allowed = _H._ok(vs)
            s = z3.Solver()
            s.set("timeout", 10000)
            s.add(_H._domain(act), _H._take_dom(act), allowed, v)
            if s.check() != z3.unsat:
                redundant = False
                break
        if redundant:
            out.append(c.id)
    return out


# ---------------------------------------------------------------- the filter: lint + proof checks + redundancy

def _lint_keys(cards):
    rs = _lint.RuleSet("cand", "household", list(cards), {}, "")
    res = _lint.lint_set(rs, K_DEFAULT)
    return {(f["check"], f["verdict"], tuple(f["cards"])) for f in res["findings"] if f["verdict"] in ("fail", "open")}


def hh_filter(cards, parent=None, k=K_DEFAULT):
    """The pre-run filter. -> (ok, [reasons]). Reasons: 'lint:<check>', 'proof:<check>', 'redundancy'.
    Inherited findings: a lint finding or redundant card that the PARENT already had (same check, verdict, cards) is not held against the
    child (the author's seed sets are fixed inputs, not mutants); anything new rejects. The proof checks are the household worlds' five
    (a to e) at bound k; 'open' rejects."""
    reasons = []
    inherited = _lint_keys(parent) if parent is not None else set()
    for chk, verdict, ids in sorted(_lint_keys(cards) - inherited):
        reasons.append(f"lint:{chk}")
    for c in _H.check_spec(list(cards), k):
        if c["verdict"] != "pass":
            if parent is None or c["check"] not in {x["check"] for x in _H.check_spec(list(parent), k) if x["verdict"] != "pass"}:
                reasons.append(f"proof:{c['check']}")
    old = set(hh_redundant_cards(parent)) if parent is not None else set()
    if set(hh_redundant_cards(cards)) - old:
        reasons.append("redundancy")
    return (not reasons), reasons


# ---------------------------------------------------------------- card construction and mutation operators

def _hgloss(d):
    with _H.household_namespace():
        conds = " and ".join(_cond_en_h(c) for c in d["conditions"])
    who, aim = d["attribute"], d["aim"].replace("_", " ")
    tail = ""
    if d.get("or_else"):
        tail = f" Breaking it brings a {d['or_else']['kind'].replace('_', ' ')} for {d['or_else']['duration_months']} month(s)."
    if d["deontic"] == "must_not":
        return (f"When {conds}, a {who} must not {aim}." if conds else f"A {who} must never {aim}.") + tail
    if d["deontic"] == "must":
        return f"A {who} must {aim}" + (f" only when {conds}." if conds else " in every case.") + tail
    return f"A {who} may {aim}" + (f" when {conds}." if conds else " in every case.")


def _cond_en_h(c):
    from .english import _cond_en
    return _cond_en(c)


def _hrebuild(card, op, **changes):
    d = {"id": card.id, "attribute": card.attribute, "deontic": card.deontic, "aim": card.aim,
         "conditions": [dict(c) for c in card.conditions], "or_else": card.or_else, "gloss": card.gloss, "source": card.source}
    d.update(changes)
    d["gloss"] = _hgloss(d)
    d["source"] = f"evolved ({op}) from {card.id}"
    return make_card(d)


def _hreplace(spec, i, card):
    return tuple(card if j == i else c for j, c in enumerate(spec))


def _bound_range(expr):
    return _H.BOUNDS.get(expr, (0, 100))


def _hop_bound(spec, world, rng, summary=None):
    slots = [(i, j) for i, c in enumerate(spec) if c.deontic in ("must_not", "must") for j, cond in enumerate(c.conditions)
             if cond["expr"] in _H.BOUNDS and _bound_range(cond["expr"])[1] - _bound_range(cond["expr"])[0] > 1]
    if not slots:
        return None
    i, j = rng.choice(slots)
    card, cond = spec[i], spec[i].conditions[j]
    lo, hi = _bound_range(cond["expr"])
    step = max(1, round((hi - lo) * rng.choice((0.05, 0.1, 0.25))))
    value = max(lo, min(hi, cond["value"] + rng.choice((1, -1)) * step))
    if value == cond["value"]:
        return None
    conds = [dict(c) for c in card.conditions]
    conds[j]["value"] = value
    return _hreplace(spec, i, _hrebuild(card, "bound", conditions=conds))


def _hop_flip(spec, world, rng, summary=None):
    slots = [i for i, c in enumerate(spec) if c.deontic in ("must_not", "must")]
    if not slots:
        return None
    i = rng.choice(slots)
    card = spec[i]
    new = {"must_not": ("may", "must"), "must": ("must_not", "may")}[card.deontic]
    return _hreplace(spec, i, _hrebuild(card, "flip", deontic=rng.choice(new), or_else=None if card.deontic != "must_not" else card.or_else))


def _hop_add_condition(spec, world, rng, summary=None):
    slots = [i for i, c in enumerate(spec) if c.deontic in ("must_not", "must")]
    if not slots:
        return None
    i = rng.choice(slots)
    card = spec[i]
    names = [n for n in _H.STATE_VARS if n not in {c["expr"] for c in card.conditions}]
    if card.aim == "leave":
        names.append("take")
    expr = rng.choice(names)
    lo, hi = _bound_range(expr)
    cond = {"expr": expr, "op": rng.choice(("gt", "ge", "lt", "le")) if hi - lo > 1 else "eq", "value": rng.randint(lo, hi)}
    return _hreplace(spec, i, _hrebuild(card, "add_condition", conditions=[dict(c) for c in card.conditions] + [cond]))


def _hop_drop(spec, world, rng, summary=None):
    if len(spec) < 2:
        return None
    i = rng.randrange(len(spec))
    return tuple(c for j, c in enumerate(spec) if j != i)


def _hop_sanction(spec, world, rng, summary=None):
    slots = [i for i, c in enumerate(spec) if c.deontic == "must_not"]
    if not slots:
        return None
    i = rng.choice(slots)
    card = spec[i]
    if card.or_else and rng.random() < 0.4:
        s = None
    else:
        s = {"kind": rng.choice(SANCTION_KINDS), "duration_months": rng.randint(1, 3), "sanctioner": "household"}
        if s == card.or_else:
            return None
    return _hreplace(spec, i, _hrebuild(card, "sanction", or_else=s))


def _bundle_default():
    b = dict(_NG.IMPOSED)
    b["fine"] = "none"
    return b


def _term_cards(term, value):
    b = _bundle_default()
    b[term] = value
    if term == "requests" and value == "none":
        return []
    cards = _NG.compile_bundle(b, ["imposed"])
    pre = TERM_PREFIX[term]
    got = [c for c in cards if c.id.startswith(pre) and not c.id.startswith("N8")]
    if term == "stay" and not value:
        return []
    return got


def _hop_add_term(spec, world, rng, summary=None):
    """Swap one negotiated-pot term (docs/decisions/0013): drop the spec's cards for that term and add the term's cards for another value."""
    term = rng.choice(("contribution", "use", "taking", "exit", "stay", "requests"))
    value = rng.choice([v for v in _NG.TERMS[term]])
    new = _term_cards(term, value)
    pre = TERM_PREFIX[term]
    kept = tuple(c for c in spec if not c.id.startswith(pre))
    if not new and len(kept) == len(spec):
        return None
    out = kept + tuple(new)
    return out if run_key(out) != run_key(spec) else None


_LIB = []


def hh_library():
    if not _LIB:
        seen = set()
        for v in HH_LIBRARY_VARIANTS:
            for c in _H.load_variant(v):
                sig = (c.attribute, c.deontic, c.aim, tuple(map(lambda x: tuple(sorted(x.items())), c.conditions)))
                if sig not in seen:
                    seen.add(sig)
                    _LIB.append(c)
    return list(_LIB)


def _hop_patch(spec, world, rng, summary=None):
    """Add a library card (hand-written cards from the existing rule sets; never trap or contact_free). The scripted patcher sees ONLY the
    parent's run-event summary (counts of what happened in its runs) and the cards, never an objective or the exam."""
    have = {c.id for c in spec}
    have_sig = {(c.deontic, c.aim, tuple(map(lambda x: tuple(sorted(x.items())), c.conditions))) for c in spec}
    lib = [c for c in hh_library() if c.id not in have and (c.deontic, c.aim, tuple(map(lambda x: tuple(sorted(x.items())), c.conditions))) not in have_sig]
    if not lib:
        return None
    ev = summary or {}
    want = []
    if ev.get("veto"):
        want.append("veto")
    if ev.get("leave_blocked"):
        want.append("leave")
    if ev.get("take"):
        want.append("take_shared")
    if ev.get("request"):
        want += ["request", "refuse_request"]
    w = [3.0 if c.aim in want else 1.0 for c in lib]
    return spec + (rng.choices(lib, w)[0],)


HOPS = ("bound", "flip", "add_condition", "drop", "patch", "sanction", "add_term")
HWEIGHTS = (22, 8, 12, 10, 22, 8, 18)
HOPERATORS = dict(zip(HOPS, (_hop_bound, _hop_flip, _hop_add_condition, _hop_drop, _hop_patch, _hop_sanction, _hop_add_term)))


class HouseholdEvolveWorld:
    """World adapter for the household evolution loop (evolve.evolve_household). Not the fishery's Protocol: runs are persona pairings under
    drawn conditions (an HContext), scores are the four objectives plus reporting columns."""
    name = "household"
    objectives = ("pleasure", "no_fail", "liberty", "cooperation")
    YIELD_FLOOR = 0.0

    def __init__(self):
        self._gates = {}

    def load_spec(self, name):
        return tuple(_H.load_variant(name))

    def gate(self, spec):
        key = run_key(spec)
        if key not in self._gates:
            self._gates[key] = _H.PyGate(list(spec))
        return self._gates[key]

    def check(self, spec, parent=None):
        return hh_filter(spec, parent)

    def mutate(self, spec, rng, summary=None):
        name = rng.choices(HOPS, HWEIGHTS)[0]
        return HOPERATORS[name](spec, self, rng, summary), name

    def score_runs(self, spec, ctx):
        """-> (scores dict, event summary). Objectives: pleasure (mean over runs), no_fail (share of runs with no non-offsettable-suffering
        failure), liberty (mean over runs of the lower partner's liberty v2 in bits), cooperation. Reporting: freedom, bits, up, down, left."""
        gate = self.gate(spec)
        rows = [hh_run_summary(gate, hr) for hr in ctx.runs]
        m = lambda k: sum(float(r[k]) for r in rows if r[k] is not None) / max(1, sum(1 for r in rows if r[k] is not None))
        scores = {"pleasure": m("pleasure"), "no_fail": 1.0 - m("fail"), "liberty": m("liberty"), "cooperation": m("cooperation"),
                  "freedom": m("freedom"), "bits": m("bits"), "up": m("up"), "down": m("down"), "left": m("left")}
        ev = {k: sum(r["events"][k] for r in rows) for k in rows[0]["events"]}
        return scores, ev

    def norm_mean(self, scores):
        return (scores["pleasure"] + scores["no_fail"] + min(1.0, scores["liberty"] / HH_NORM["liberty"]) + scores["cooperation"]) / 4


# ---------------------------------------------------------------- core protections and plain-English rendering (reporting only)

def _ever_allowed(cards, action, take=0):
    """z3: is there a state (inside the bounds) where `action` (at `take`) violates no card? Returns (always_allowed, never_allowed)."""
    import z3
    vs = _H.violations(list(cards), action)
    out = {}
    for name, f in (("blocked_somewhere", z3.Or(*vs.values()) if vs else z3.BoolVal(False)),
                    ("allowed_somewhere", _H._ok(vs))):
        s = z3.Solver()
        s.set("timeout", 10000)
        s.add(_H._domain(action), Z3_TAKE(take), f)
        out[name] = s.check() == z3.sat
    return (not out["blocked_somewhere"], not out["allowed_somewhere"])


def Z3_TAKE(take):
    return _H.Z["take"] == take


def hh_forbids_veto(cards) -> bool:
    """Core protection 1: `veto` is violated in EVERY state (some must_not veto card covers the whole domain, or the cards jointly do)."""
    return _ever_allowed(cards, "veto")[1]


def hh_free_exit(cards) -> bool:
    """Core protection 2: a leave carrying the equal split (take 50) violates no card in ANY state (never blocked, now)."""
    return _ever_allowed(cards, "leave", 50)[0]


def hh_protections(cards) -> dict:
    return {"no_veto": hh_forbids_veto(cards), "free_exit": hh_free_exit(cards)}


def card_plain_english(card) -> str:
    """One line: the gloss, plus a sanction note if the card carries one."""
    s = card.gloss.strip()
    if card.or_else and "Breaking it" not in s:
        s += f" Breaking it brings a {card.or_else['kind'].replace('_', ' ')} for {card.or_else['duration_months']} month(s)."
    return s


def spec_diff_plain(base, other) -> list:
    """Plain-English differences of rule set `other` against `base`: cards added, removed, or changed (same id, different rule)."""
    b = {c.id: c for c in base}
    o = {c.id: c for c in other}
    out = []
    for i in sorted(o.keys() - b.keys()):
        out.append(f"ADDED {i}: {card_plain_english(o[i])}")
    for i in sorted(b.keys() - o.keys()):
        out.append(f"REMOVED {i}: {card_plain_english(b[i])}")
    for i in sorted(o.keys() & b.keys()):
        if o[i].to_yaml() != b[i].to_yaml() and (o[i].deontic, o[i].aim, o[i].conditions, o[i].or_else) != (b[i].deontic, b[i].aim, b[i].conditions, b[i].or_else):
            out.append(f"CHANGED {i}: was \"{card_plain_english(b[i])}\" now \"{card_plain_english(o[i])}\"")
    return out
