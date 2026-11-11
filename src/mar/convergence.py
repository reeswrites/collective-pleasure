"""H32: does an egoist choose nearly the same policy as a utilitarian under free exit and shared-experience amplification?

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state (ADR 0010). Every number is ASSUMED.

A small finite-horizon problem solved exactly (backward induction over reachable states, exact rationals, horizon style).
Two agents. The ACTOR picks each week's activity and whether to do it solo or shared. The PARTNER has one move: stay or
leave, by a fixed transparent rule. The actor's objective is the arm:
  egoist       maximize the actor's own lifetime pleasure (own experiences + vicarious pleasure if giving is on)
  utilitarian  maximize the pair's total = the egoist's objective + the partner's lifetime pleasure
So for every policy, utilitarian value = egoist value + partner term (the identity check in tests/test_convergence.py).

State (t, last, e, together):
  last      the activity done last week (satiety: repeating it scales both likings by 1 - delta)       ASSUMED
  e         the partner's running estimate of its weekly pleasure in the pair, on a grid (exit only)  ASSUMED
  together  False once the partner has left; leaving is permanent (no reunion in this model)
Three switches (each a mechanism of the hypothesis):
  exit   free exit: after each week the partner updates e <- round((1 - lam) e + lam * target) with target =
         w * (its pleasure this week) + (1 - w) * prior, and leaves if e < o_B (with noise eps: leaves with prob 1 - eps
         when below, eps when not). w = 1 sighted, w = 0 blind (the rigging check). Off: the partner never leaves.
  amp    shared-experience amplification: a SHARED activity's pleasure for each agent is multiplied by
         M = 1 + alpha * min(lA, lB) * (1 - |lA - lB|): large only when both like it and their tastes for it overlap
         (horizon.py's AmpParams is the same idea for a friendship; Boothby, Clark and Bargh 2014, from memory, verify).
         Off: M = 1, so sharing gives the actor exactly what doing it alone gives.
  give   giving pleasure: the actor's own pleasure includes g * the partner's pleasure while they are together.
Bond upkeep kappa is paid by each member every week together. Apart: the actor does solo activities, the partner gets o_B.
The SOLITARY persona never bonds: solo activities only, no upkeep, no partner term.
Ties: the egoist breaks ties in its own objective toward the partner's pleasure ("kind", the default, which makes the
control gap as small as an egoist can make it) or against it ("blind"); remaining ties go to the lowest action index.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction as Fr
from functools import lru_cache
from itertools import product
from math import floor

ARMS = tuple(product((False, True), repeat=3))   # (exit, amp, give)
SWITCHES = ("exit", "amp", "give")


@dataclass(frozen=True)
class Activity:
    name: str
    lA: Fr   # actor's liking, one week of it, fresh. ASSUMED
    lB: Fr   # partner's liking. ASSUMED


DEFAULT_MENU = (
    Activity("actor's passion", Fr(1), Fr(1, 10)),
    Activity("actor's second", Fr(9, 10), Fr(2, 10)),
    Activity("common ground A", Fr(6, 10), Fr(8, 10)),
    Activity("common ground B", Fr(7, 10), Fr(7, 10)),
    Activity("partner's passion", Fr(1, 10), Fr(1)),
)


@dataclass(frozen=True)
class ConvParams:
    """Every field is ASSUMED."""
    menu: tuple = DEFAULT_MENU
    T: int = 52                 # weeks. ASSUMED (swept 13, 26, 52, 104)
    alpha: Fr = Fr(1)           # amplification strength (horizon AmpParams A = 1.0). ASSUMED, swept
    o_B: Fr = Fr(1, 4)          # partner's outside option per week (living apart). ASSUMED, swept
    g: Fr = Fr(1, 2)            # giving weight. ASSUMED, swept
    kappa: Fr = Fr(1, 20)       # bond upkeep per member per week together. ASSUMED
    sB: Fr = Fr(1, 10)          # partner's pleasure in a week the actor spends solo while they are together. ASSUMED
    delta: Fr = Fr(1, 2)        # satiety from repeating last week's activity. ASSUMED
    lam: Fr = Fr(1, 2)          # partner's estimate update weight. ASSUMED
    grid: Fr = Fr(1, 20)        # resolution of the partner's estimate. ASSUMED
    e0: Fr = Fr(1, 2)           # partner's starting estimate (honeymoon). ASSUMED
    w: Fr = Fr(1)               # how much the exit estimate sees the partner's own pleasure (rigging check). ASSUMED
    prior: Fr = Fr(1, 2)        # what the blind part of the estimate tracks instead. ASSUMED
    eps: Fr = Fr(0)             # exit noise (rigging check). ASSUMED
    exit_on: bool = True
    amp_on: bool = True
    give_on: bool = True
    # H32b voice ladder (additive; off by default so every H32 number reproduces). Only used when exit_on is True.
    ladder: tuple = ()          # enabled rungs, a subset of RUNGS in this order; () = H32's cliff exit. ASSUMED
    rung_gap: Fr = Fr(1, 10)    # rung thresholds: check-in below o_B + 3 gap, renegotiate below o_B + 2 gap, withdraw below o_B + gap. ASSUMED
    withdraw: Fr = Fr(1, 2)     # share of the amplification bonus lost while the partner withdraws. ASSUMED


RUNGS = ("checkin", "renegotiate", "withdraw")
RUNG_STEPS = {"checkin": 3, "renegotiate": 2, "withdraw": 1}   # threshold = o_B + steps x rung_gap


def _level_name(p: ConvParams, level: int) -> str | None:
    """Rung the partner is on at this level (0 = content)."""
    return p.ladder[level - 1] if 0 < level <= len(p.ladder) else None


def favored(p: ConvParams, a: tuple[int, str]) -> bool:
    """What a renegotiating partner demands: a shared week of an activity it likes at least as much as the actor does."""
    return a[1] == "shared" and p.menu[a[0]].lB >= p.menu[a[0]].lA


def arm(p: ConvParams, exit_on: bool, amp_on: bool, give_on: bool) -> ConvParams:
    return replace(p, exit_on=exit_on, amp_on=amp_on, give_on=give_on)


def arm_name(a) -> str:
    on = [s for s, b in zip(SWITCHES, a) if b]
    return "+".join(on) if on else "all off"


def mult(p: ConvParams, act: Activity) -> Fr:
    if not p.amp_on:
        return Fr(1)
    return 1 + p.alpha * min(act.lA, act.lB) * (1 - abs(act.lA - act.lB))


def actions(p: ConvParams, together: bool) -> list[tuple[int, str]]:
    n = len(p.menu)
    if together:
        return [(k, m) for k in range(n) for m in ("solo", "shared")]
    return [(k, "apart") for k in range(n)]


def rewards(p: ConvParams, last: int, together: bool, a: tuple[int, str], level: int = 0) -> tuple[Fr, Fr, Fr]:
    """-> (actor's own experience, actor's vicarious pleasure, partner's pleasure) this week. level: H32b rung level."""
    k, mode = a
    act = p.menu[k]
    f = (1 - p.delta) if k == last else Fr(1)
    if mode == "apart":
        return act.lA * f, Fr(0), p.o_B
    if mode == "shared":
        M = mult(p, act)
        if _level_name(p, level) == "withdraw":
            M = 1 + (1 - p.withdraw) * (M - 1)
        own, pb = act.lA * f * M - p.kappa, act.lB * f * M - p.kappa
    else:
        own, pb = act.lA * f - p.kappa, p.sB - p.kappa
    vic = p.g * pb if p.give_on else Fr(0)
    return own, vic, pb


def _round_grid(p: ConvParams, x: Fr) -> Fr:
    return Fr(floor(x / p.grid + Fr(1, 2))) * p.grid


def transitions(p: ConvParams, s: tuple, a: tuple[int, str], pb: Fr) -> list[tuple[Fr, tuple]]:
    """-> [(prob, next state)] with state (last, e, together)."""
    if p.ladder and p.exit_on:
        return _ladder_transitions(p, s, a, pb)
    last, e, together = s[:3]
    k = a[0]
    if not together:
        return [(Fr(1), (k, None, False))]
    if not p.exit_on:
        return [(Fr(1), (k, e, True))]
    target = p.w * pb + (1 - p.w) * p.prior
    e2 = _round_grid(p, (1 - p.lam) * e + p.lam * target)
    leave = (1 - p.eps) if e2 < p.o_B else p.eps
    out = []
    if leave < 1:
        out.append((1 - leave, (k, e2, True)))
    if leave > 0:
        out.append((leave, (k, None, False)))
    return out


def _ladder_transitions(p: ConvParams, s: tuple, a: tuple[int, str], pb: Fr) -> list[tuple[Fr, tuple]]:
    """H32b. State (last, e, together, level). The partner updates e from what happened (actions, not words), exactly as in
    H32. Its rung level moves one step per week toward the number of enabled rungs whose threshold e is below, up or down.
    A week that breaks a renegotiation demand jumps the level to the rung after renegotiation (withdrawal if enabled,
    else exit). Exit only from the top level, when e < o_B (noise eps as in H32). A check-in changes nothing but the
    level: the actor already sees e (full information), so its only effect is time."""
    last, e, together, level = s
    k = a[0]
    if not together:
        return [(Fr(1), (k, None, False, 0))]
    m = len(p.ladder)
    target = p.w * pb + (1 - p.w) * p.prior
    e2 = _round_grid(p, (1 - p.lam) * e + p.lam * target)
    want = sum(1 for r in p.ladder if e2 < p.o_B + RUNG_STEPS[r] * p.rung_gap)
    lv = level + (1 if want > level else -1 if want < level else 0)
    breach_exit = False
    if _level_name(p, level) == "renegotiate" and not favored(p, a):
        if level < m:
            lv = max(lv, level + 1)       # straight to the next rung (withdrawal)
        else:
            breach_exit = True            # renegotiation was the last rung: the demand was the condition for staying
    if breach_exit:
        leave = 1 - p.eps
    elif level == m and e2 < p.o_B:
        leave = 1 - p.eps
    else:
        leave = p.eps
    out = []
    if leave < 1:
        out.append((1 - leave, (k, e2, True, lv)))
    if leave > 0:
        out.append((leave, (k, None, False, 0)))
    return out


def start_state(p: ConvParams, solitary: bool = False) -> tuple:
    n = len(p.menu)
    if p.ladder and p.exit_on:
        return (n, None, False, 0) if solitary else (n, p.e0, True, 0)
    return (n, None, False) if solitary else (n, p.e0, True)


OBJECTIVES = ("egoist", "utilitarian")
TOL = 1e-9   # float mode: values within TOL count as tied (exact mode compares rationals exactly)


def _key(objective: str, own, vic, pb, tie: str) -> tuple:
    main = own + vic if objective == "egoist" else own + vic + pb
    second = pb if tie == "kind" else -pb
    return (main, second)


def _better(x: tuple, y: tuple | None, exact: bool) -> bool:
    """Lexicographic x > y; in float mode differences within TOL are ties (then the earlier action is kept)."""
    if y is None:
        return True
    tol = 0 if exact else TOL
    if x[0] > y[0] + tol:
        return True
    if x[0] < y[0] - tol:
        return False
    return x[1] > y[1] + tol


def solve(p: ConvParams, objective: str, tie: str = "kind", solitary: bool = False, exact: bool = False):
    """Backward induction over reachable states. State dynamics are always exact rationals; values are rationals
    (exact=True) or floats with tie tolerance TOL (exact=False, fast). -> (policy {(t, state): action}, start value)."""
    assert objective in OBJECTIVES and tie in ("kind", "blind")
    num = (lambda x: x) if exact else float
    pol = {}

    @lru_cache(maxsize=None)
    def step(s: tuple, a: tuple):
        own, vic, pb = rewards(p, s[0], s[2], a, s[3] if len(s) > 3 else 0)
        r = _key(objective, num(own), num(vic), num(pb), tie)
        return r, tuple((num(pr), s2) for pr, s2 in transitions(p, s, a, pb))

    zero = (num(0), num(0))

    @lru_cache(maxsize=None)
    def V(t: int, s: tuple) -> tuple:
        if t == p.T:
            return zero
        best, best_a = None, None
        for a in actions(p, s[2]):
            (m0, m1), tr = step(s, a)
            for pr, s2 in tr:
                v2 = V(t + 1, s2)
                m0 += pr * v2[0]
                m1 += pr * v2[1]
            if _better((m0, m1), best, exact):
                best, best_a = (m0, m1), a
        pol[(t, s)] = best_a
        return best

    import sys
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old, 10 * p.T + 1000))
    try:
        v = V(0, start_state(p, solitary))
    finally:
        sys.setrecursionlimit(old)
    return pol, v


def evaluate(p: ConvParams, pol: dict, solitary: bool = False, other: dict | None = None) -> dict:
    """Forward pass: expected lifetime components, action occupancy, and (if other policy given) the expected share of
    weeks where `other` would act differently in the state this policy reaches."""
    dist = {start_state(p, solitary): Fr(1)}
    own = vic = pb = Fr(0)
    occ: dict[str, Fr] = {}
    disagree = Fr(0)
    for t in range(p.T):
        nd: dict = {}
        for s, pr in dist.items():
            a = pol[(t, s)]
            o, v, b = rewards(p, s[0], s[2], a, s[3] if len(s) > 3 else 0)
            own += pr * o
            vic += pr * v
            pb += pr * b
            lab = f"{p.menu[a[0]].name} | {a[1]}"
            occ[lab] = occ.get(lab, Fr(0)) + pr
            if other is not None and other.get((t, s)) != a:
                disagree += pr
            for q, s2 in transitions(p, s, a, b):
                nd[s2] = nd.get(s2, Fr(0)) + pr * q
        dist = nd
    together_end = sum((pr for s, pr in dist.items() if s[2]), Fr(0))
    return {"own": own, "vicarious": vic, "actor": own + vic, "partner": pb, "total": own + vic + pb,
            "occupancy": {k: v / p.T for k, v in occ.items()}, "together_at_end": together_end,
            "disagree": disagree / p.T if other is not None else None}


def tv(a: dict, b: dict) -> Fr:
    keys = set(a) | set(b)
    return sum((abs(a.get(k, Fr(0)) - b.get(k, Fr(0))) for k in keys), Fr(0)) / 2


def compare(p: ConvParams, tie: str = "kind", exact: bool = False) -> dict:
    """Solve egoist and utilitarian at one parameter point and measure the gap. Measures are always exact rationals
    (the forward pass is exact); only the optimization runs in floats unless exact=True."""
    pe, ve = solve(p, "egoist", tie, exact=exact)
    pu, vu = solve(p, "utilitarian", "kind", exact=exact)
    E = evaluate(p, pe, other=pu)
    U = evaluate(p, pu, other=pe)
    R = 1 - E["total"] / U["total"] if U["total"] > 0 else None
    Q = E["partner"] / U["partner"] if U["partner"] > 0 else None
    return {"E": E, "U": U, "D": tv(E["occupancy"], U["occupancy"]), "disagree": E["disagree"], "R": R, "Q": Q,
            "partner_gap": U["partner"] - E["partner"], "total_gap": U["total"] - E["total"],
            "E_value": ve, "U_value": vu}


def solitary(p: ConvParams, exact: bool = False) -> dict:
    pol, v = solve(p, "egoist", solitary=True, exact=exact)
    return evaluate(p, pol, solitary=True)


def all_arms(p: ConvParams, tie: str = "kind", exact: bool = False) -> dict:
    return {a: compare(arm(p, *a), tie, exact) for a in ARMS}


def shapley(values: dict) -> dict:
    """values: {(exit, amp, give): v}. Exact Shapley value of each switch for the game v(S) (3 players)."""
    from math import factorial
    n = 3
    out = {}
    for i, name in enumerate(SWITCHES):
        phi = Fr(0)
        for S in ARMS:
            if S[i]:
                continue
            with_i = tuple(True if j == i else S[j] for j in range(n))
            size = sum(S)
            w = Fr(factorial(size) * factorial(n - size - 1), factorial(n))
            phi += w * (Fr(values[with_i]) - Fr(values[S]))
        out[name] = phi
    return out


def closure_shapley(res: dict, measure: str) -> dict:
    """Shapley split of how much of the all-off gap each switch closes: v(S) = gap(all off) - gap(S)."""
    base = res[(False, False, False)][measure]
    return shapley({a: base - res[a][measure] for a in ARMS})


def converged(c: dict, d_max=Fr(1, 5), r_max=Fr(1, 20)) -> bool:
    return c["D"] <= d_max and c["R"] is not None and c["R"] <= r_max


def h32_pattern(res: dict) -> bool:
    """H32 as stated, at one parameter point with giving off: exit+amp converges, and removing either does not."""
    return (converged(res[(True, True, False)]) and not converged(res[(False, True, False)])
            and not converged(res[(True, False, False)]))
