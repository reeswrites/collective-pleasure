"""H35: care that grows from shared good times. The H32 model (src/mar/convergence.py, used read-only) with the actor's
giving weight g as a state variable.

Wording rule: agents feel nothing; "pleasure" and "care" are glosses for a modeled hedonic state (ADR 0010). Every number
is ASSUMED.

g lives on a grid of g_step. After each week together: if the week was an AMPLIFIED shared week (shared, and the
amplification bonus M - 1, after any withdrawal, is at least amp_min) g rises by up steps; otherwise it falls by down steps.
Apart, g falls by down steps a week. The actor's vicarious pleasure is g x the partner's pleasure while together.

Two egoists:
  naive          acts each week as if its current g were fixed for life (the H32 egoist at that g). Care grows as a side
                 effect of what it does, not as a plan. Primary: "care grown by an environment, not chosen".
  sophisticated  exact DP with g in the state: it foresees that shared weeks raise its own future vicarious pleasure.
Reference utilitarian (H35): maximizes the actor's own experience + the partner's pleasure, WITHOUT the vicarious term, so
growing g cannot inflate the benchmark (in H32 the utilitarian counted the partner twice when giving was on). Its policy
does not depend on g.
Rupture (start week, length): during those weeks shared activities are unavailable; the pair can only do solo weeks.
Agents know the schedule (exact, deterministic).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, replace
from fractions import Fraction as Fr
from functools import lru_cache

from mar import convergence as C


@dataclass(frozen=True)
class CareParams:
    """Every field is ASSUMED."""
    base: C.ConvParams = replace(C.ConvParams(), exit_on=False, amp_on=True, give_on=False)
    g0: Fr = Fr(0)              # starting care (cold start)
    g_step: Fr = Fr(1, 20)      # grid of g. ASSUMED
    up: int = 1                 # steps gained per amplified shared week. ASSUMED, swept
    down: int = 1               # steps lost per other week. ASSUMED, swept
    amp_min: Fr = Fr(3, 10)     # an amplified shared week has M - 1 >= amp_min. ASSUMED
    rupture: tuple | None = None  # (first week, length) with shared activities unavailable


def _level(s):
    return s[3] if len(s) > 3 else 0


def in_rupture(cp: CareParams, t: int) -> bool:
    return cp.rupture is not None and cp.rupture[0] <= t < cp.rupture[0] + cp.rupture[1]


def actions(cp: CareParams, t: int, together: bool):
    acts = C.actions(cp.base, together)
    if together and in_rupture(cp, t):
        acts = [a for a in acts if a[1] != "shared"]
    return acts


def amplified(cp: CareParams, s: tuple, a) -> bool:
    if a[1] != "shared":
        return False
    p = cp.base
    M = C.mult(p, p.menu[a[0]])
    if C._level_name(p, _level(s)) == "withdraw":
        M = 1 + (1 - p.withdraw) * (M - 1)
    return M - 1 >= cp.amp_min


def g_next(cp: CareParams, g: Fr, s: tuple, a) -> Fr:
    if s[2] and amplified(cp, s, a):
        return min(Fr(1), g + cp.up * cp.g_step)
    return max(Fr(0), g - cp.down * cp.g_step)


def week(cp: CareParams, s: tuple, g: Fr, a):
    """-> (own, vicarious, partner) for the base state s with care g."""
    own, _, pb = C.rewards(replace(cp.base, give_on=False), s[0], s[2], a, _level(s))
    vic = g * pb if s[2] else Fr(0)
    return own, vic, pb


OBJ = ("egoist", "util")


def solve(cp: CareParams, objective: str, g_fixed: Fr | None = None, exact: bool = False):
    """Backward induction over (t, base state, g). g_fixed: g never changes (the naive egoist's view at that g; also used
    for the utilitarian, whose objective ignores g). -> policy {(t, base state, g): action}."""
    assert objective in OBJ
    num = (lambda x: x) if exact else float
    p = cp.base
    pol = {}

    @lru_cache(maxsize=None)
    def V(t: int, s: tuple, g: Fr):
        if t == p.T:
            return (num(0), num(0))
        best, best_a = None, None
        for a in actions(cp, t, s[2]):
            own, vic, pb = week(cp, s, g, a)
            m0 = num(own + vic) if objective == "egoist" else num(own + pb)
            m1 = num(pb)
            g2 = g if g_fixed is not None else g_next(cp, g, s, a)
            for pr, s2 in C.transitions(p, s, a, pb):
                v2 = V(t + 1, s2, g2)
                m0 += num(pr) * v2[0]
                m1 += num(pr) * v2[1]
            if C._better((m0, m1), best, exact):
                best, best_a = (m0, m1), a
        pol[(t, s, g)] = best_a
        return best

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old, 10 * p.T + 1000))
    try:
        V(0, C.start_state(p), cp.g0 if g_fixed is None else g_fixed)
    finally:
        sys.setrecursionlimit(old)
    return pol


def g_grid(cp: CareParams) -> list[Fr]:
    n = int(1 / cp.g_step)
    return [cp.g_step * i for i in range(n + 1)]


_FIXED: dict = {}


class Naive:
    """The naive egoist's policy: at (t, s, g) do what the fixed-g egoist would. Fixed-g DPs are solved lazily per g and
    cached per process (they do not depend on g0, up, down or amp_min)."""
    def __init__(self, cp: CareParams, exact: bool = False):
        self.cp, self.exact = cp, exact
        self.key = (replace(cp, g0=Fr(0), up=1, down=1, amp_min=Fr(0)), exact)

    def __call__(self, t, s, g):
        k = (self.key, g)
        if k not in _FIXED:
            _FIXED[k] = solve(replace(self.cp, g0=g), "egoist", g_fixed=g, exact=self.exact)
        return _FIXED[k][(t, s, g)]


_UTIL: dict = {}


def policies(cp: CareParams, exact: bool = False, sophisticated: bool = True) -> dict:
    uk = (replace(cp, g0=Fr(0), up=1, down=1, amp_min=Fr(0)), exact)
    if uk not in _UTIL:
        _UTIL[uk] = solve(replace(cp, g0=Fr(0)), "util", g_fixed=Fr(0), exact=exact)
    util = _UTIL[uk]
    out = {"util": lambda t, s, g: util[(t, s, Fr(0))], "naive": Naive(cp, exact)}
    if sophisticated:
        soph = solve(cp, "egoist", exact=exact)
        out["sophisticated"] = lambda t, s, g: soph[(t, s, g)]
    return out


def run_path(cp: CareParams, pol, ref=None) -> dict:
    """Forward pass with dynamic g. ref: the utilitarian policy, to score week-by-week agreement."""
    p = cp.base
    dist = {(C.start_state(p), cp.g0): Fr(1)}
    own = vic = pb = Fr(0)
    occ, agree, gs = {}, [], []
    for t in range(p.T):
        nd = {}
        ag = Fr(0)
        for (s, g), pr in dist.items():
            a = pol(t, s, g)
            o, v, b = week(cp, s, g, a)
            own += pr * o
            vic += pr * v
            pb += pr * b
            lab = f"{p.menu[a[0]].name} | {a[1]}"
            occ[lab] = occ.get(lab, Fr(0)) + pr
            if ref is not None and ref(t, s, g) == a:
                ag += pr
            g2 = g_next(cp, g, s, a)
            for q, s2 in C.transitions(p, s, a, b):
                nd[(s2, g2)] = nd.get((s2, g2), Fr(0)) + pr * q
        dist = nd
        agree.append(ag)
        gs.append(sum((pr * g for (s, g), pr in dist.items()), Fr(0)))
    together = sum((pr for (s, g), pr in dist.items() if s[2]), Fr(0))
    return {"own": own, "vicarious": vic, "partner": pb, "pair": own + pb, "occupancy": {k: v / p.T for k, v in occ.items()},
            "agree": agree, "g_path": gs, "g_final": gs[-1], "together_at_end": together}


def conv_week(agree: list, T: int, tail: int = 2) -> int | None:
    """First week from which the egoist agrees with the utilitarian in every remaining week, ignoring the last `tail`
    weeks (end-game). None if never."""
    last = T - tail
    for t0 in range(last):
        if all(x == 1 for x in agree[t0:last]):
            return t0
    return None


def cell(cp: CareParams, kinds=("naive", "sophisticated"), exact: bool = False) -> dict:
    pols = policies(cp, exact, sophisticated="sophisticated" in kinds)
    U = run_path(cp, pols["util"])
    out = {"U": U}
    for k in kinds:
        E = run_path(cp, pols[k], ref=pols["util"])
        cw = conv_week(E["agree"], cp.base.T)
        out[k] = {**E, "conv_week": cw, "D": C.tv(E["occupancy"], U["occupancy"]),
                  "R": 1 - E["pair"] / U["pair"] if U["pair"] > 0 else None,
                  "warm": cw is not None and cw <= cp.base.T // 2,
                  "spiral": classify(cp, E, cw)}
    return out


def classify(cp: CareParams, E: dict, cw) -> str:
    """upward: converges by mid-life and care ends above where it started (by at least 0.1); stable: converges, care flat
    or lower; downward: never converges and care ends below where it started (or at 0); stuck: neither."""
    T = cp.base.T
    gf = E["g_final"]
    if cw is not None and cw <= T // 2:
        return "upward" if gf >= cp.g0 + Fr(1, 10) else "stable"
    if gf < cp.g0 or gf == 0:
        return "downward"
    return "stuck"
