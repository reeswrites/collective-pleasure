"""A small household decision problem that can be solved exactly: does maximizing lifetime pleasure differ from being greedy?

A finite deterministic MDP derived from the ideas in docs/notes/hedonic-technology-synthesis.md (not the full household world).
Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state (ADR 0010). Every number is ASSUMED.

State s = (aF, aR, w, n, p, c, m, t, b, z); "future situation" = anything that carries over from one week to the next
  aF, aR  adaptation (tolerance/satiety) of the favorite and the alternative, 0..A        NEGATIVE carryover   [synthesis M1]
  w       weeks since the last event (ritual or concert), capped at W: anticipation        POSITIVE (savoring)  [synthesis M3]
  n       connection need, coarse bucket 0 (starved) .. 2 (met); decays; fatigue/neglect   NEGATIVE if starved [ADR 0010]
  p       shared-pot level 0..P (resources; spending is limited by what was saved)         NEGATIVE (depletion) [ADR 0013]
  c       commitment age: honored weeks so far, 0..C (a long project's progress)           friction now, POSITIVE later [M4]
  m       memory glow 0..M: set to M by a shared peak (ritual, concert), decays 1/week     POSITIVE (reminiscence)
  t       acquired taste 0..T: exposure to the complex alternative raises its future liking POSITIVE (sensitization)
  b       bond 0..B: shared events build it; it raises later shared pleasure               POSITIVE (bond-building)
  z       bad-memory glow 0..Z: set when a week is lived starved; decays 1/week; re-costs it (rumination) NEGATIVE memory
Memory is the one self (author, 2026-11-10): each week's total pleasure = present + vividness-weighted memory re-experienced now (m good, z bad).
Vividness by event: a ritual sets m to vS, a concert (peak, shared, novel) to vK; ordinary weeks leave no trace.
Actions: 0 F repeat the favorite, 1 R rotate to the alternative, 2 S shared ritual, 3 X solo spend from the pot,
         4 V save to the pot, 5 H honor the commitment, 6 K "concert": costly, shared, big one-off event (spends pot, builds
         memory and bond, but raises tolerance for ordinary pleasures by contrast and does not refresh the need).
Reward r(s, a) uses the state BEFORE the action: base(a) - deprivation(n) + beta * c + mu * m.
Spacing restores adaptation: an unused activity recovers one level per week and a ritual gives the favorite one more level of recovery
(Nelson and Meyvis 2008, interruption raises enjoyment; from memory, verify). Loewenstein 1987 (savoring) and Kahneman's peak-end
work motivate w and m (from memory, verify).

The module offers the transition table, exact finite-horizon backward induction, discounted value iteration, the greedy policy
and simple heuristics, a bounded exhaustive witness search, and a z3 check of the witness over exact rationals.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from itertools import product
from typing import Callable, Sequence

import numpy as np

ACTIONS = ("F", "R", "S", "X", "V", "H", "K")
NA = len(ACTIONS)
F_, R_, S_, X_, V_, H_, K_ = range(NA)


@dataclass(frozen=True)
class HorizonParams:
    """Every field is ASSUMED. Rationals so the z3 check and the float tables describe the same model."""
    bF: Fraction = Fraction(10)         # favorite activity, fresh. ASSUMED (scale only)
    bR: Fraction = Fraction(7)          # alternative activity, fresh (second best). ASSUMED
    bS: Fraction = Fraction(6)          # shared ritual base. ASSUMED
    bX: Fraction = Fraction(12)         # solo spend from the pot: a treat, not repeated enough to adapt. ASSUMED
    bV: Fraction = Fraction(1)          # saving: small comfort. ASSUMED
    delta: Fraction = Fraction(1, 5)    # adaptation strength: value lost per level of tolerance (synthesis M1: sensory-specific satiety). ASSUMED
    A: int = 4                          # adaptation cap. ASSUMED
    rho: Fraction = Fraction(1, 4)      # anticipation: ritual value grows by rho per week of spacing (synthesis M3). ASSUMED
    W: int = 3                          # anticipation cap in weeks. ASSUMED
    nuD: Fraction = Fraction(2)         # deprivation cost per week while the connection need is starved (ADR 0010). ASSUMED
    P: int = 3                          # pot capacity. ASSUMED
    pot_matters: bool = True            # False: X and K always allowed, the pot never changes (state-independent switch)
    beta: Fraction = Fraction(3, 2)     # commitment recall payoff per week per honored week (synthesis M4). ASSUMED
    f: Fraction = Fraction(3)           # commitment friction at c = 0, falling linearly to 0 at c = C (friction early). ASSUMED
    C: int = 3                          # commitment cap (long-project length). ASSUMED
    bK: Fraction = Fraction(12)         # concert base = the solo treat bX, so with no carryover a concert is worth exactly a free treat. ASSUMED
    M: int = 2                          # memory cap. ASSUMED
    mu: Fraction = Fraction(1, 2)       # reminiscence payoff per week per memory unit (peak-end; Kahneman, from memory, verify). ASSUMED
    T: int = 2                          # acquired-taste cap. ASSUMED
    theta: Fraction = Fraction(1, 10)   # alternative's liking gain per taste unit (sensitization/acquired taste). ASSUMED
    B: int = 2                          # bond cap. ASSUMED
    kappa: Fraction = Fraction(1, 2)    # shared-event pleasure gain per bond unit. ASSUMED
    vS: int = 1                         # memory vividness a ritual leaves (shared, ordinary). ASSUMED
    vK: int = 2                         # memory vividness a concert leaves (peak, shared, novel). ASSUMED
    Z: int = 2                          # bad-memory cap. ASSUMED
    muz: Fraction = Fraction(1)         # rumination cost per bad-memory unit per week (painful memories re-cost). ASSUMED
    kcost: int = 1                      # pot units a concert costs ("affordable"). ASSUMED
    kcontrast: int = 1                  # tolerance a concert adds to both ordinary activities (contrast). ASSUMED
    ritual_rest: int = 1                # extra tolerance recovery of the favorite after a ritual (spacing/interruption). ASSUMED

    def off(self) -> "HorizonParams":
        """All state feedback off: the reward depends on no state the actions change (Theorem 1 applies)."""
        return replace(self, delta=Fraction(0), rho=Fraction(0), nuD=Fraction(0), beta=Fraction(0), mu=Fraction(0), muz=Fraction(0),
                       theta=Fraction(0), kappa=Fraction(0), pot_matters=False)


START = (0, 0, 0, 2, 2, 0, 0, 0, 0, 0)   # fresh activities, no spacing yet, need met, pot 2, no commitment. ASSUMED


def feasible(q: HorizonParams, s: tuple, a: int) -> bool:
    if not q.pot_matters:
        return True
    return not ((a == X_ and s[4] < 1) or (a == K_ and s[4] < q.kcost))


def step(q: HorizonParams, s: tuple, a: int):
    """Concrete transition: returns (reward, next_state). Works with Fraction or float parameters."""
    aF, aR, w, n, p, c, m, t, b, z = s
    # unused activities recover one level; the used one adapts one level
    nF, nR = max(aF - 1, 0), max(aR - 1, 0)
    nw, nn, np_, nc, nm, nt, nb = min(w + 1, q.W), max(n - 1, 0), p, c, max(m - 1, 0), t, b
    nz = q.Z if n == 0 else max(z - 1, 0)
    if a == F_:
        base = q.bF * (1 - q.delta * aF); nF = min(aF + 1, q.A)
    elif a == R_:
        base = q.bR * (1 - q.delta * aR + q.theta * t); nR = min(aR + 1, q.A); nt = min(t + 1, q.T)
    elif a == S_:
        base = q.bS * (1 + q.rho * w) + q.kappa * b
        nw, nn, nm, nb = 0, 2, max(nm, q.vS), min(b + 1, q.B); nF = max(aF - 1 - q.ritual_rest, 0)
    elif a == X_:
        base = q.bX
        if q.pot_matters:
            np_ = p - 1
    elif a == V_:
        base = q.bV
        if q.pot_matters:
            base = q.bV if p < q.P else 0 * q.bV
            np_ = min(p + 1, q.P)
    elif a == H_:
        base = -q.f * (q.C - c) / q.C; nc = min(c + 1, q.C)
    elif a == K_:
        base = q.bK * (1 + q.rho * w) + q.kappa * b
        nw, nm, nb = 0, max(nm, q.vK), min(b + 1, q.B)
        nF, nR = min(aF + q.kcontrast, q.A), min(aR + q.kcontrast, q.A)
        if q.pot_matters:
            np_ = p - q.kcost
    else:
        raise ValueError(a)
    r = base - (q.nuD if n == 0 else 0) + q.beta * c + q.mu * m - q.muz * z
    return r, (nF, nR, nw, nn, np_, nc, nm, nt, nb, nz)


class Table:
    """Dense float tables over the states reachable from START: reward[s, a] (-inf if infeasible), nxt[s, a] (state index)."""

    def __init__(self, q: HorizonParams, start: tuple = START):
        self.q = q
        qf = HorizonParams(**{k: (float(v) if isinstance(v, Fraction) else v) for k, v in q.__dict__.items()})
        self.states, self.idx = [start], {start: 0}
        rows_r, rows_n = [], []
        i = 0
        while i < len(self.states):
            s = self.states[i]
            rr, nn = [-np.inf] * NA, [i] * NA
            for a in range(NA):
                if feasible(q, s, a):
                    r, t = step(qf, s, a)
                    if t not in self.idx:
                        self.idx[t] = len(self.states)
                        self.states.append(t)
                    rr[a], nn[a] = r, self.idx[t]
            rows_r.append(rr)
            rows_n.append(nn)
            i += 1
        self.reward = np.array(rows_r)
        self.nxt = np.array(rows_n, dtype=np.int64)

    def reachable(self, start: tuple = START) -> list[int]:
        return list(range(len(self.states)))


def backward_values(tab: Table, K: int, gamma: float) -> list[np.ndarray]:
    """V[k][s] = optimal discounted pleasure with k steps left. V[0] = 0."""
    V = [np.zeros(len(tab.states))]
    for _ in range(K):
        Q = tab.reward + gamma * V[-1][tab.nxt]
        V.append(Q.max(axis=1))
    return V


def optimal_plan(tab: Table, s0: tuple, K: int, gamma: float) -> tuple[list[int], float]:
    V = backward_values(tab, K, gamma)
    i, plan = tab.idx[s0], []
    for k in range(K, 0, -1):
        Q = tab.reward[i] + gamma * V[k - 1][tab.nxt[i]]
        a = int(np.argmax(Q))
        plan.append(a)
        i = int(tab.nxt[i, a])
    return plan, float(V[K][tab.idx[s0]])


def greedy_action(tab: Table, i: int) -> int:
    """Highest immediate reward; ties go to the lowest action index (declared tie-break)."""
    return int(np.argmax(tab.reward[i]))


def run_policy(tab: Table, s0: tuple, K: int, gamma: float, policy: Callable[[int, int], int]) -> tuple[list[int], float]:
    """policy(t, state_index) -> action. Total discounted pleasure over K steps."""
    i, tot, plan = tab.idx[s0], 0.0, []
    for t in range(K):
        a = policy(t, i)
        assert np.isfinite(tab.reward[i, a]), "infeasible action"
        tot += gamma ** t * tab.reward[i, a]
        plan.append(a)
        i = int(tab.nxt[i, a])
    return plan, tot


def greedy_policy(tab: Table):
    return lambda t, i: greedy_action(tab, i)


def _first_feasible(tab: Table, i: int, prefs: Sequence[int]) -> int:
    for a in prefs:
        if np.isfinite(tab.reward[i, a]):
            return a
    return greedy_action(tab, i)


def rotate_policy(tab: Table, n: int):
    """Rotate-every-n: favorite for n weeks, then the alternative for n weeks, and so on."""
    return lambda t, i: F_ if (t // n) % 2 == 0 else R_


def ritual_policy(tab: Table, m: int):
    """Ritual every m weeks (m = 1 is ritual-weekly), alternate favorite and alternative in between."""
    return lambda t, i: S_ if t % m == 0 else (F_ if (t // m + t) % 2 == 0 else R_)


def greedy_loss(tab: Table, s0: tuple, K: int, gamma: float) -> dict:
    plan, vopt = optimal_plan(tab, s0, K, gamma)
    gplan, vg = run_policy(tab, s0, K, gamma, greedy_policy(tab))
    loss = vopt - vg
    return {"opt": vopt, "greedy": vg, "loss": loss, "pct": (100.0 * loss / abs(vopt)) if abs(vopt) > 1e-12 else 0.0,
            "opt_plan": plan, "greedy_plan": gplan}


def infinite_values(tab: Table, gamma: float, tol: float = 1e-10, max_iter: int = 100000) -> np.ndarray:
    V = np.zeros(len(tab.states))
    for _ in range(max_iter):
        Vn = (tab.reward + gamma * V[tab.nxt]).max(axis=1)
        if np.max(np.abs(Vn - V)) < tol:
            return Vn
        V = Vn
    return V


def greedy_infinite_value(tab: Table, gamma: float, tol: float = 1e-10, max_iter: int = 100000) -> np.ndarray:
    g = np.array([greedy_action(tab, i) for i in range(len(tab.states))])
    rows = np.arange(len(tab.states))
    r, nx = tab.reward[rows, g], tab.nxt[rows, g]
    V = np.zeros(len(tab.states))
    for _ in range(max_iter):
        Vn = r + gamma * V[nx]
        if np.max(np.abs(Vn - V)) < tol:
            return Vn
        V = Vn
    return V


def greedy_loss_infinite(tab: Table, s0: tuple, gamma: float) -> dict:
    vo, vg = infinite_values(tab, gamma)[tab.idx[s0]], greedy_infinite_value(tab, gamma)[tab.idx[s0]]
    return {"opt": float(vo), "greedy": float(vg), "loss": float(vo - vg), "pct": float(100 * (vo - vg) / abs(vo)) if abs(vo) > 1e-12 else 0.0}


def critical_gamma(tab: Table, s0: tuple, K: int, eps: float = 1e-9) -> float | None:
    """Smallest discount at which greedy strictly loses from s0 over K steps (bisection; loss is 0 below it). None if no loss at gamma = 1."""
    if greedy_loss(tab, s0, K, 1.0)["loss"] <= eps:
        return None
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if greedy_loss(tab, s0, K, mid)["loss"] > eps:
            hi = mid
        else:
            lo = mid
    return hi


# ------------------------------------------------------------------ bounded exhaustive witness search

def exact_total(q: HorizonParams, s0: tuple, plan: Sequence[int], gamma: Fraction) -> Fraction:
    s, tot = s0, Fraction(0)
    for t, a in enumerate(plan):
        assert feasible(q, s, a)
        r, s = step(q, s, a)
        tot += gamma ** t * r
    return tot


def exact_greedy_plan(q: HorizonParams, s0: tuple, K: int) -> list[int]:
    s, plan = s0, []
    for _ in range(K):
        best, ba = None, None
        for a in range(NA):
            if feasible(q, s, a):
                r, _ = step(q, s, a)
                if best is None or r > best:
                    best, ba = r, a
        plan.append(ba)
        s = step(q, s, ba)[1]
    return plan


def exhaustive_best(q: HorizonParams, s0: tuple, K: int, gamma: Fraction) -> tuple[list[int], Fraction]:
    """Enumerate every feasible plan of length K (6^K at most) in exact arithmetic."""
    best: list = [None, None]

    def rec(s, t, tot, plan):
        if t == K:
            if best[1] is None or tot > best[1]:
                best[0], best[1] = list(plan), tot
            return
        for a in range(NA):
            if feasible(q, s, a):
                r, s2 = step(q, s, a)
                plan.append(a)
                rec(s2, t + 1, tot + gamma ** t * r, plan)
                plan.pop()

    rec(s0, 0, Fraction(0), [])
    return best[0], best[1]


def find_witness(q: HorizonParams, gamma: Fraction, kmax: int = 6, start: tuple = START, from_start_only: bool = False) -> dict | None:
    """Smallest k (then smallest-index state) such that some reachable state s has greedy strictly below the best plan over k steps.
    Exhaustive in exact rationals; reachable states are enumerated by BFS from START."""
    tab = Table(q, start)
    g = float(gamma)
    rows = np.arange(len(tab.states))
    ga = np.argmax(tab.reward, axis=1)
    rg, ng = tab.reward[rows, ga], tab.nxt[rows, ga]
    V, G = [np.zeros(len(tab.states))], [np.zeros(len(tab.states))]
    for _ in range(kmax):
        V.append((tab.reward + g * V[-1][tab.nxt]).max(axis=1))
        G.append(rg + g * G[-1][ng])
    for k in range(1, kmax + 1):
        cand = [i for i in range(len(tab.states)) if V[k][i] - G[k][i] > 1e-7]     # float screen; confirmed below in exact rationals
        if from_start_only:
            cand = [i for i in cand if i == 0]
        for i in cand:
            s = tab.states[i]
            gp = exact_greedy_plan(q, s, k)
            tg = exact_total(q, s, gp, gamma)
            bp, tb = exhaustive_best(q, s, k, gamma)
            if tb > tg:
                return {"state": s, "k": k, "gamma": gamma, "greedy_plan": gp, "greedy_total": tg, "best_plan": bp, "best_total": tb}
    return None


# ------------------------------------------------------------------ z3 (machine-checked, exact rationals)

def _z3():
    import z3
    return z3


def _sym_step(z3, q: HorizonParams, s, a):
    """Symbolic mirror of step(): s is a tuple of z3 Ints, a a z3 Int. Returns (reward, next_state, feasible)."""
    aF, aR, w, n, p, c, m, t, b, z = s
    R = lambda x: z3.RealVal(str(Fraction(x))) if not isinstance(x, int) else z3.RealVal(x)
    ite, mn, mx = z3.If, (lambda x, y: z3.If(x < y, x, y)), (lambda x, y: z3.If(x > y, x, y))
    isF, isR, isS, isX, isV, isH, isK = (a == F_), (a == R_), (a == S_), (a == X_), (a == V_), (a == H_), (a == K_)
    nF = ite(isF, mn(aF + 1, q.A), ite(isS, mx(aF - 1 - q.ritual_rest, 0), ite(isK, mn(aF + q.kcontrast, q.A), mx(aF - 1, 0))))
    nR = ite(isR, mn(aR + 1, q.A), ite(isK, mn(aR + q.kcontrast, q.A), mx(aR - 1, 0)))
    ev = z3.Or(isS, isK)
    nw = ite(ev, 0, mn(w + 1, q.W))
    nn = ite(isS, 2, mx(n - 1, 0))
    nm = ite(isS, mx(mx(m - 1, 0), q.vS), ite(isK, mx(mx(m - 1, 0), q.vK), mx(m - 1, 0)))
    nz = ite(n == 0, q.Z, mx(z - 1, 0))
    nt = ite(isR, mn(t + 1, q.T), t)
    nb = ite(ev, mn(b + 1, q.B), b)
    if q.pot_matters:
        np_ = ite(isX, p - 1, ite(isK, p - q.kcost, ite(isV, mn(p + 1, q.P), p)))
        vreward = ite(p < q.P, R(q.bV), R(0))
        feas = z3.And(z3.Or(a != X_, p >= 1), z3.Or(a != K_, p >= q.kcost))
    else:
        np_, vreward, feas = p, R(q.bV), z3.BoolVal(True)
    nc = ite(isH, mn(c + 1, q.C), c)
    f = lambda x: z3.ToReal(x)
    base = ite(isF, R(q.bF) * (1 - R(q.delta) * f(aF)),
           ite(isR, R(q.bR) * (1 - R(q.delta) * f(aR) + R(q.theta) * f(t)),
           ite(isS, R(q.bS) * (1 + R(q.rho) * f(w)) + R(q.kappa) * f(b),
           ite(isX, R(q.bX),
           ite(isV, vreward,
           ite(isK, R(q.bK) * (1 + R(q.rho) * f(w)) + R(q.kappa) * f(b),
               -R(q.f) * f(q.C - c) / q.C))))))
    r = base - ite(n == 0, R(q.nuD), R(0)) + R(q.beta) * f(c) + R(q.mu) * f(m) - R(q.muz) * f(z)
    return r, (nF, nR, nw, nn, np_, nc, nm, nt, nb, nz), feas


def z3_check_witness(q: HorizonParams, wit: dict, timeout_ms: int = 120000) -> dict:
    """Machine-check the witness with z3 over exact rationals. Three facts:
    (1) the greedy plan really is greedy: at every step no feasible action has a strictly larger immediate reward;
    (2) its total discounted pleasure equals the claimed value; (3) EXISTS a plan with strictly larger total (sat, with a model);
    (4) NO plan beats the claimed best total (unsat), so best_total is the optimum over all plans of length k."""
    z3 = _z3()
    s0, k, gamma = wit["state"], wit["k"], Fraction(wit["gamma"])
    gam = z3.RealVal(str(gamma))
    out = {}

    def unroll(acts):
        s = tuple(z3.IntVal(v) for v in s0)
        tot, feas, rs = z3.RealVal(0), [], []
        for t in range(k):
            r, s, f = _sym_step(z3, q, s, acts[t])
            feas.append(f)
            rs.append(r)
            tot = tot + gam ** t * r
        return tot, feas

    # (1) greedy-ness, stepwise (concrete states along the greedy plan, symbolic comparison over all 6 actions)
    s, ok = tuple(s0), True
    for t, ga in enumerate(wit["greedy_plan"]):
        sv = tuple(z3.IntVal(v) for v in s)
        rg, _, _ = _sym_step(z3, q, sv, z3.IntVal(ga))
        sol = z3.Solver()
        a = z3.Int("a")
        r2, _, f2 = _sym_step(z3, q, sv, a)
        sol.add(a >= 0, a < NA, f2, r2 > rg)
        ok = ok and sol.check() == z3.unsat
        s = step(q, s, ga)[1]
    out["greedy_is_greedy_unsat"] = ok

    # (2) total of the greedy plan
    acts = [z3.IntVal(a) for a in wit["greedy_plan"]]
    tot_g, _ = unroll(acts)
    out["greedy_total_matches"] = bool(z3.simplify(tot_g == z3.RealVal(str(wit["greedy_total"]))))
    acts = [z3.IntVal(a) for a in wit["best_plan"]]
    tot_b, _ = unroll(acts)
    out["best_total_matches"] = bool(z3.simplify(tot_b == z3.RealVal(str(wit["best_total"]))))

    # (3) exists a plan strictly better than greedy
    vars_ = [z3.Int(f"a{t}") for t in range(k)]
    tot, feas = unroll(vars_)
    sol = z3.Solver()
    sol.set("timeout", timeout_ms)
    sol.add(*[z3.And(v >= 0, v < NA) for v in vars_], *feas, tot > z3.RealVal(str(wit["greedy_total"])))
    res = sol.check()
    out["better_plan_exists_sat"] = res == z3.sat
    if res == z3.sat:
        m = sol.model()
        out["z3_plan"] = [m.eval(v, model_completion=True).as_long() for v in vars_]

    # (4) no plan beats the best total
    sol2 = z3.Solver()
    sol2.set("timeout", timeout_ms)
    sol2.add(*[z3.And(v >= 0, v < NA) for v in vars_], *feas, tot > z3.RealVal(str(wit["best_total"])))
    out["best_is_optimal_unsat"] = sol2.check() == z3.unsat
    return out


def describe_state(s: tuple) -> str:
    aF, aR, w, n, p, c, m, t, b, z = s
    return (f"favorite tolerance {aF}, alternative tolerance {aR}, {w} weeks since the last event, connection need {n}/2, pot {p}, "
            f"commitment {c}, good-memory glow {m}, bad-memory glow {z}, acquired taste {t}, bond {b}")


def plan_str(plan: Sequence[int]) -> str:
    return " ".join(ACTIONS[a] for a in plan)


# ------------------------------------------------------------------ the concert: net carryover and the dose/spacing boundary

def constrained_value(tab: Table, s0: tuple, K: int, gamma: float, mask: Callable[[int], np.ndarray]) -> float:
    """Optimal discounted pleasure when at step t only the actions with mask(t)[a] True may be taken (if none is feasible: -inf)."""
    V = [np.zeros(len(tab.states))]
    for k in range(1, K + 1):
        t = K - k                                      # time index of the decision with k steps left
        rew = np.where(mask(t)[None, :], tab.reward, -np.inf)
        V.append((rew + gamma * V[-1][tab.nxt]).max(axis=1))
    return float(V[K][tab.idx[s0]])


def no_concert_mask(t: int) -> np.ndarray:
    m = np.ones(NA, dtype=bool); m[K_] = False
    return m


def schedule_value(tab: Table, s0: tuple, K: int, gamma: float, every: int) -> float:
    """A concert every `every` weeks (weeks every-1, 2*every-1, ...), every other week anything except a concert.
    A scheduled week whose pot cannot pay falls back to the best non-concert action."""
    V = [np.zeros(len(tab.states))]
    for k in range(1, K + 1):
        t = K - k
        scheduled = (t % every) == every - 1
        r_k = tab.reward[:, K_]
        rew_other = tab.reward.copy(); rew_other[:, K_] = -np.inf
        Qother = (rew_other + gamma * V[-1][tab.nxt]).max(axis=1)
        if scheduled:
            Qk = r_k + gamma * V[-1][tab.nxt[:, K_]]
            V.append(np.where(np.isfinite(r_k), Qk, Qother))
        else:
            V.append(Qother)
    return float(V[K][tab.idx[s0]])


def concert_gain(q: HorizonParams, s0: tuple, K: int, gamma: float, every: int) -> dict:
    """Lifetime gain of a spaced concert schedule over never going, in the full model and in the zero-carryover model (q.off(),
    where the concert is a free one-off with only its base pleasure). net_carryover = gain(full) - gain(zero carryover):
    positive means the concert adds more through anticipation, memory and bonding than it costs through tolerance, resources and
    neglected needs. Also reports each side in isolation (negative channels only, positive channels only)."""
    def gain(qq):
        tab = Table(qq, s0)
        return schedule_value(tab, s0, K, gamma, every) - constrained_value(tab, s0, K, gamma, no_concert_mask)
    zero = Fraction(0)
    neg_only = replace(q, rho=zero, mu=zero, theta=zero, kappa=zero)        # keep tolerance, depletion, need displacement
    pos_only = replace(q, delta=zero, nuD=zero, pot_matters=False)          # keep anticipation, memory, taste, bond
    g_full, g_off, g_neg, g_pos = gain(q), gain(q.off()), gain(neg_only), gain(pos_only)
    return {"every": every, "gain_full": g_full, "gain_zero_carryover": g_off, "net_carryover": g_full - g_off,
            "gain_negative_only": g_neg, "gain_positive_only": g_pos}


# ------------------------------------------------------------------ worked case: the optimal gap between seeing someone

@dataclass(frozen=True)
class GapParams:
    """One person's side of a recurring meeting with a friend. All ASSUMED; the shape is the author's 2026-09-10 claude.ai conversation on
    the optimal time between seeing someone (not archived in the repo), the numbers are placeholders."""
    H: float = 30.0       # half-life of closeness while apart, days = depth of the friendship (deeper = slower decay)
    tau_w: float = 7.0    # days for the want-to-see term to saturate: want(d) = 1 - exp(-d / tau_w)
    tau_a: float = 60.0   # days for absence to become normal: adaptation factor exp(-d / tau_a) (Helson adaptation level; from memory, verify)
    M: float = 30.0       # tension scale: tension(d) = M * closeness(d) * want(d) * adaptation(d)
    thr: float = 6.0      # tension up to thr feels like anticipation (pleasant); above it, like pain
    lam: float = 1.5      # pain slope above the threshold
    rel: float = 1.5      # release at reunion = rel * (tension dropping to zero) (opponent process; Solomon and Corbit 1974; from memory, verify)
    joy: float = 0.0      # the meeting's own flat pleasure; 0 = relativity: the pleasure of a meeting is the release (ASSUMED)
    cost: float = 24.0    # each meeting costs time and logistics
    reset: float = 0.6    # a meeting closes this share of the closeness gap
    omega: float = 0.5    # peak-end: share of the worst moment that colors the memory (Kahneman et al. 1993; from memory, verify)


@dataclass(frozen=True)
class SelfParams:
    """The one self (author, 2026-11-10: "the experiencing self is the remembering self and depends on vividness of memory etc").
    Each day's total = pi * present feeling + nu * (memory traces re-experienced now, each weighted by its vividness) + scheduled anticipation.
    Lifetime pleasure = the sum of that total over all days. Old scores are special cases: nu = 0 and a_sched = 0 is the old EXPERIENCED
    score; pi = 0 with all vividness weights 0 and rum = 1 is the old REMEMBERED score up to a positive scale and per cycle. ALL ASSUMED."""
    pi: float = 1.0        # weight of present feeling
    nu: float = 0.01       # weight of re-experienced memory (per unit of vividness x valence per day)
    tau_m: float = 45.0    # days over which a memory's vividness decays: vividness(age) = V0 * exp(-age / tau_m)
    base: float = 1.0      # baseline vividness of a trace
    w_int: float = 0.5     # intensity / peak: + w_int * min(|valence| / scale, 2)
    w_end: float = 0.5     # ending: + w_end for the trace that closes an episode (the reunion; peak-end)
    w_nov: float = 0.5     # novelty: + w_nov * g / (g + 14) (rarer episodes stand out; routine blurs)
    w_emo: float = 0.5     # emotion/arousal: + w_emo * min(tension / thr, 1) at the event
    w_sh: float = 0.5      # shared with others: + w_sh for shared episodes (the reunion), 0 for pain borne alone
    rum: float = 1.5       # rumination: a painful trace re-costs rum times its valence (painful vivid memories cost extra)
    scale: float = 10.0    # valence that counts as a full-intensity event
    a_sched: float = 0.15  # anticipation of a scheduled meeting: a_sched * expected release * exp(-days_to_go / tau_ant)
    tau_ant: float = 3.0


PURE_PRESENT = SelfParams(nu=0.0, a_sched=0.0)                                     # the old EXPERIENCED self
PURE_MEMORY = SelfParams(pi=0.0, a_sched=0.0, w_int=0.0, w_end=0.0, w_nov=0.0, w_emo=0.0, w_sh=0.0, rum=1.0)  # the old REMEMBERED self (per cycle)


def _recall_mass(tau_m: float) -> float:
    """Total discounted re-experience of one trace over all later days: sum_{age >= 1} exp(-age / tau_m). Independent of the gap, by stationarity."""
    return 1.0 / (np.exp(1.0 / tau_m) - 1.0)


def _vividness(sp: SelfParams, valence: float, g: int, arousal: float, ending: bool, shared: bool) -> float:
    return sp.base * (1 + sp.w_int * min(abs(valence) / sp.scale, 2.0) + sp.w_end * (1.0 if ending else 0.0)
                      + sp.w_nov * g / (g + 14.0) + sp.w_emo * arousal + sp.w_sh * (1.0 if shared else 0.0))


def _gap_start_closeness(p: GapParams, g: int) -> float:
    d = 0.5 ** (g / p.H)
    return p.reset / (1 - d * (1 - p.reset))      # fixed point of the repeating cycle


def gap_score(p: GapParams, g: int, sp: SelfParams = SelfParams()) -> dict:
    """Steady-state cycle: g days apart, then a meeting. Per cycle, in order:
    present = sum of daily feeling (anticipation while tension <= thr, pain above it) + release + joy - cost at the reunion;
    traces (consolidated when the episode closes, at the reunion): the reunion trace (valence release + joy - cost; shared, an ending) and
    the pain trace (valence -omega x worst pain; borne alone; re-costs rum times);
    memory = nu x recall_mass x sum of vividness x valence; scheduled anticipation = a_sched x release x sum exp(-days_to_go / tau_ant).
    lifetime per day = (pi x present + memory + anticipation) / g. Also returns the two old scores for comparison."""
    x0 = _gap_start_closeness(p, g)
    tot, worst, tension = 0.0, 0.0, 0.0
    for d in range(1, g + 1):
        x = x0 * 0.5 ** (d / p.H)
        tension = p.M * x * (1 - np.exp(-d / p.tau_w)) * np.exp(-d / p.tau_a)
        feel = tension if tension <= p.thr else p.thr - p.lam * (tension - p.thr)
        tot += feel
        worst = max(worst, p.lam * max(tension - p.thr, 0.0))
    release = p.rel * tension
    reun = release + p.joy * x0 - p.cost
    present = tot + reun
    v_end = reun
    v_pain = -p.omega * worst
    arousal_end = min(tension / p.thr, 1.0)
    V_end = _vividness(sp, v_end, g, arousal_end, True, True)
    V_pain = _vividness(sp, v_pain, g, 1.0, False, False)
    S = _recall_mass(sp.tau_m)
    memory = sp.nu * S * (V_end * v_end + V_pain * v_pain * (sp.rum if v_pain < 0 else 1.0))
    ant = sp.a_sched * release * sum(np.exp(-(g - d) / sp.tau_ant) for d in range(1, g + 1))
    return {"gap": g, "lifetime": float((sp.pi * present + memory + ant) / g), "present_part": float(sp.pi * present / g),
            "memory_part": float(memory / g), "anticipation_part": float(ant / g), "memory_cycle": float(memory),
            "experienced": float(present / g), "remembered": float(reun - p.omega * worst), "release": float(release),
            "worst_pain": float(worst), "closeness_at_meeting": float(x0 * 0.5 ** (g / p.H)), "closeness_after": float(x0)}


def gap_curve(p: GapParams, gmax: int = 200, sp: SelfParams = SelfParams()) -> list[dict]:
    return [gap_score(p, g, sp) for g in range(1, gmax + 1)]


def best_gaps(p: GapParams, gmax: int = 200, sp: SelfParams = SelfParams()) -> dict:
    """Best gap for the unified self (lifetime), and for the two old scores as special cases."""
    c = gap_curve(p, gmax, sp)
    bl = max(c, key=lambda r: r["lifetime"])
    be = max(c, key=lambda r: r["experienced"])      # old experienced self (present only, per day)
    br = max(c, key=lambda r: r["remembered"])       # old remembered self (peak-end, per cycle, duration neglected)
    return {"best_lifetime": bl["gap"], "best_experienced_old": be["gap"], "best_remembered_old": br["gap"],
            "ratio_remembered_old_to_experienced_old": br["gap"] / be["gap"], "curve": c}


def gap_mismatch(pa: GapParams, pb: GapParams, gmax: int = 200, sp: SelfParams = SelfParams()) -> dict:
    """Two people with different parameters who meet at one shared gap, both scored by the unified self. Each person's best gap, the mismatch, and
    what the shorter-optimum person gives up (percent of their best lifetime value, and how far closeness has faded at the meeting) at the longer gap."""
    A, B = best_gaps(pa, gmax, sp), best_gaps(pb, gmax, sp)
    short, long_ = (pa, pb) if A["best_lifetime"] <= B["best_lifetime"] else (pb, pa)
    gs, gl = min(A["best_lifetime"], B["best_lifetime"]), max(A["best_lifetime"], B["best_lifetime"])
    sbest, sat = gap_score(short, gs, sp), gap_score(short, gl, sp)
    return {"best_a": A["best_lifetime"], "best_b": B["best_lifetime"], "mismatch_days": gl - gs,
            "short_best_value": sbest["lifetime"], "short_value_at_long_gap": sat["lifetime"],
            "short_loss_pct": 100 * (sbest["lifetime"] - sat["lifetime"]) / abs(sbest["lifetime"]) if sbest["lifetime"] else 0.0,
            "closeness_at_meeting_best": sbest["closeness_at_meeting"], "closeness_at_meeting_long_gap": sat["closeness_at_meeting"]}


def trace_value(valence: float, sp: SelfParams = SelfParams(), *, g: int = 30, arousal: float = 1.0, ending: bool = True, shared: bool = True) -> dict:
    """What one episode is worth after the fact (all later days) against what it was worth in the moment (its valence)."""
    V = _vividness(sp, valence, g, arousal, ending, shared)
    after = sp.nu * _recall_mass(sp.tau_m) * V * valence * (sp.rum if valence < 0 else 1.0)
    return {"vividness": V, "in_moment": valence, "after_the_fact": after, "ratio": after / valence if valence else 0.0}


def stretch_value(L: int, level: float, sp: SelfParams = SelfParams()) -> dict:
    """A stretch of L days at a steady mild `level` (no peak, no ending event, not shared, not novel). Present = level x L; it leaves one low-vividness trace."""
    V = _vividness(replace(sp, w_end=0.0, w_nov=0.0, w_emo=0.0, w_sh=0.0), level, 10 ** 9, 0.0, False, False)
    mem = sp.nu * _recall_mass(sp.tau_m) * V * level
    return {"present": level * L, "memory": mem, "memory_share": mem / (level * L + mem)}
