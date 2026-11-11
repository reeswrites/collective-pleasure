"""Liking vs wanting: model version 3 piece for ADR 0018 test 1 (docs/results/liking-wanting-prereg.md).

Wording rule: agents feel nothing. "Pleasure", "liking" and "wanting" are glosses for modeled values (ADR 0010).
Every number here is ASSUMED unless a comment says otherwise.

What it adds. Pleasure splits into two values per activity:
  liking   the payoff that counts (what lifetime pleasure, ADR 0017, sums). It adapts on a slow clock: tolerance h
           rises by one level at the end of a day with a heavy dose and recovers one level after a day without use.
  wanting  what drives choice for an agent that acts on wanting. wanting = liking + a cue term. The cue term is
           present only when a cue is (cue-triggered), and grows with a sensitization level s that rises by one
           level per unit of use and decays only after a day without use (slow decay).
Background, from memory, verify: Robinson and Berridge 1993 (incentive-sensitization theory, Brain Research Reviews),
Berridge and Robinson 1998 and Berridge 2009 on "wanting" vs "liking"; Fiorillo, Tobler and Schultz 2003 on reward
uncertainty and dopamine (motivates the variable-reward boost). Peak-end: Kahneman et al. 1993 (from memory, verify).

The flag. `WantParams.enabled` defaults to False. Off, wanting equals liking everywhere, so a wanting-greedy agent is
the liking-greedy agent of src/mar/horizon.py. The module imports horizon only to reuse its exact solvers on a table,
and changes nothing there. `wanting_greedy_policy(tab)` on a horizon Table with no wanting table (or one equal to its
reward) is exactly `horizon.greedy_policy(tab)` (tests/test_wanting.py).

Why standalone and not the household world: the horizon link needs an exact solve (the household world is a 1700-line
simulation with noisy scripted agents and no optimizer), other agents are editing hedonic.py, and a standalone model
leaves every existing result untouched by construction. The same three-activity world can later be ported behind a
flag in the household once the measure is accepted.

The world (one person, one technology). Each day has L slots. In each slot the agent takes one unit of:
  G  the cued activity (a feed, a game, a series): liking bG when fresh
  P  a plain activity (a book, a walk, cooking): liking bP when fresh, no cue
  Q  quiet (rest, nothing): liking bQ, never adapts
Consecutive units of the same activity form a session. Within a session liking falls by ws per unit already taken
(fast satiety). Content has a natural stop every e units. A session closes at a natural stop if its length is a
multiple of e. A day's end ends every session (bedtime).

Environments differ ONLY in the wanting terms, so liking (and the lifetime optimizer) is identical across them:
  plain  cue only mid-content (an unfinished episode), no cue at a natural stop, no cue to start, fixed reward
  heavy  cue to start (notifications), cue at natural stops too (autoplay), variable reward (boosts sensitized wanting)
Rules (norms) that might protect:
  closure   a closure ritual: the cue is removed at every natural stop (the episode is closed, no autoplay)
  cap       a stopping rule: at most k units of G per day
Agents:
  W  wanting-greedy (acts on wanting: argmax wanting each slot; ties to the lowest action index G, P, Q)
  L  liking-greedy (horizon's greedy: argmax immediate liking)
  O  lifetime optimizer (exact backward induction on liking, gamma default 1)
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable

import numpy as np

ACTS = ("G", "P", "Q")
G_, P_, Q_ = 0, 1, 2
NONE = 3          # cur = no session yet today
NCOUNT = 3        # per-day unit counters are capped at 3 (values 0, 1, 2, 3+)


@dataclass(frozen=True)
class Env:
    """Wanting side of an environment. Every field ASSUMED."""
    name: str = "plain"
    trigger_cue: bool = False     # a cue to START a G session (notifications)
    autoplay: bool = False        # the cue stays on at a natural stop
    variable: float = 0.0         # variable-reward boost on sensitized wanting (0 = fixed reward)


PLAIN = Env("plain", trigger_cue=False, autoplay=False, variable=0.0)
HEAVY = Env("heavy", trigger_cue=True, autoplay=True, variable=1.0)


@dataclass(frozen=True)
class Rule:
    name: str = "none"
    closure: bool = False         # closure ritual: cue removed at every natural stop
    cap: int | None = None        # stopping rule: at most `cap` G units per day (must be <= NCOUNT)


NO_RULE = Rule("none")
CLOSURE = Rule("closure", closure=True)
CAP = Rule("cap", cap=2)


@dataclass(frozen=True)
class WantParams:
    """Every field ASSUMED. Defaults are a single parameter point; personas draw around it (`draw_personas`)."""
    enabled: bool = False   # THE FLAG. False: wanting == liking everywhere (no cue term), every agent acts on liking
    days: int = 28          # horizon in days (four weeks). ASSUMED
    L: int = 4              # slots per day. ASSUMED
    bG: float = 8.0         # fresh liking of the cued activity. ASSUMED
    bP: float = 7.0         # fresh liking of the plain activity. ASSUMED
    bQ: float = 3.0         # liking of a quiet slot (never adapts). ASSUMED
    dl: float = 0.15        # liking lost per tolerance level (slow clock). ASSUMED
    H: int = 4              # tolerance cap. ASSUMED
    dose: int = 2           # units in a day that raise tolerance one level at day end. ASSUMED
    ws: float = 0.2         # within-session satiety: liking lost per unit already taken in the session (fast clock). ASSUMED
    rcap: int = 3           # satiety stops growing after rcap units. ASSUMED
    e: int = 2              # natural stop every e units of content (same for G and P, same in both environments). ASSUMED
    c: float = 1.5          # cue strength (wanting added by a cue at s = 0). ASSUMED
    sig: float = 0.12       # sensitization: cue term grows by sig x (1 + variable) per level. ASSUMED
    S: int = 12             # sensitization cap (three days of heavy use to saturate at L = 4). ASSUMED
    gamma: float = 1.0      # discount for the lifetime optimizer (1 = lifetime pleasure, ADR 0017). ASSUMED

    def equal(self) -> "WantParams":
        """Control: wanting set equal to liking (cue off)."""
        return replace(self, c=0.0)

    def no_sensitization(self) -> "WantParams":
        """Control: sensitization off (cue still on)."""
        return replace(self, sig=0.0)


# state = (j, cur, r, hG, hP, s, nG, nP)
#   j slot in day; cur activity of the running session (NONE at day start); r units in the running session;
#   hG, hP tolerance; s sensitization of G; nG, nP units today (capped at NCOUNT)
START = (0, NONE, 0, 0, 0, 0, 0, 0)


def liking(q: WantParams, st: tuple, a: int) -> float:
    j, cur, r, hG, hP, s, nG, nP = st
    run = r if cur == a else 0
    sat = 1.0 - q.ws * min(run, q.rcap)
    if a == G_:
        return q.bG * (1.0 - q.dl * hG) * sat
    if a == P_:
        return q.bP * (1.0 - q.dl * hP) * sat
    return q.bQ


def cue_on(q: WantParams, env: Env, rule: Rule, st: tuple) -> bool:
    """Is a cue for G present in this state? Cue-triggered wanting exists only when a cue is."""
    if not q.enabled or q.c == 0.0:
        return False
    j, cur, r, *_ = st
    if cur != G_ or r == 0:
        return env.trigger_cue                       # starting a session
    at_stop = r % q.e == 0
    if not at_stop:
        return True                                  # mid-content: an unfinished episode cues the next unit
    if rule.closure:
        return False                                 # closure ritual: the stop is closed
    return env.autoplay


def wanting(q: WantParams, env: Env, rule: Rule, st: tuple, a: int) -> float:
    base = liking(q, st, a)
    if a != G_ or not cue_on(q, env, rule, st):
        return base
    s = st[5]
    return base + q.c * (1.0 + q.sig * s * (1.0 + env.variable))


def feasible(q: WantParams, rule: Rule, st: tuple, a: int) -> bool:
    if a == G_ and rule.cap is not None and st[6] >= rule.cap:
        return False
    return True


def step(q: WantParams, st: tuple, a: int) -> tuple:
    j, cur, r, hG, hP, s, nG, nP = st
    nr = r + 1 if cur == a else 1
    ncur = a
    if a == G_:
        nG, s = min(nG + 1, NCOUNT), min(s + 1, q.S)
    elif a == P_:
        nP = min(nP + 1, NCOUNT)
    if a == Q_:
        ncur, nr = Q_, 0
    j += 1
    if j == q.L:                                     # day end: slow clocks tick, sessions end
        hG = min(hG + 1, q.H) if nG >= q.dose else (max(hG - 1, 0) if nG == 0 else hG)
        hP = min(hP + 1, q.H) if nP >= q.dose else (max(hP - 1, 0) if nP == 0 else hP)
        if nG == 0:
            s = max(s - 1, 0)
        return (0, NONE, 0, hG, hP, s, 0, 0)
    return (j, ncur, nr, hG, hP, s, nG, nP)


class WTable:
    """Reachable states from START with liking, wanting and next-state tables (-inf where infeasible)."""

    def __init__(self, q: WantParams, env: Env = PLAIN, rule: Rule = NO_RULE, start: tuple = START):
        self.q, self.env, self.rule = q, env, rule
        self.states, self.idx = [start], {start: 0}
        R, Wt, N = [], [], []
        i = 0
        while i < len(self.states):
            st = self.states[i]
            rr, ww, nn = [-np.inf] * 3, [-np.inf] * 3, [i] * 3
            for a in range(3):
                if feasible(q, rule, st, a):
                    t = step(q, st, a)
                    if t not in self.idx:
                        self.idx[t] = len(self.states)
                        self.states.append(t)
                    rr[a], ww[a], nn[a] = liking(q, st, a), wanting(q, env, rule, st, a), self.idx[t]
            R.append(rr); Wt.append(ww); N.append(nn)
            i += 1
        self.reward = np.array(R)          # liking: the name `reward` lets horizon's solvers run on this table
        self.want = np.array(Wt)
        self.nxt = np.array(N, dtype=np.int64)


# ------------------------------------------------------------------ policies

def wanting_greedy_policy(tab, want: np.ndarray | None = None) -> Callable[[int, int], int]:
    """Act on wanting: argmax of the wanting table, ties to the lowest index. Works on a horizon.Table too.
    With no wanting table (flag off) or one equal to tab.reward this is exactly horizon.greedy_policy(tab)."""
    W = tab.reward if want is None else want
    W = np.where(np.isfinite(tab.reward), W, -np.inf)
    return lambda t, i: int(np.argmax(W[i]))


def liking_greedy_policy(tab) -> Callable[[int, int], int]:
    return lambda t, i: int(np.argmax(tab.reward[i]))


def optimal_policy(tab, T: int, gamma: float) -> Callable[[int, int], int]:
    """Exact finite-horizon backward induction on liking (the lifetime optimizer). Ties to the lowest index."""
    V = [np.zeros(len(tab.reward))]
    for _ in range(T):
        V.append((tab.reward + gamma * V[-1][tab.nxt]).max(axis=1))
    def pol(t, i):
        return int(np.argmax(tab.reward[i] + gamma * V[T - t - 1][tab.nxt[i]]))
    return pol


# ------------------------------------------------------------------ rollout and measures

NM = "not measurable here"


@dataclass
class Run:
    acts: list = field(default_factory=list)
    like: list = field(default_factory=list)
    want: list = field(default_factory=list)
    cued: list = field(default_factory=list)
    day: list = field(default_factory=list)
    sessions: list = field(default_factory=list)   # (activity, length, closed, peak liking, end liking)


def rollout(tab: WTable, policy: Callable[[int, int], int]) -> Run:
    q = tab.q
    T = q.days * q.L
    i, run = 0, Run()
    sess = None                                   # [activity, length, peak, last]
    for t in range(T):
        st = tab.states[i]
        a = policy(t, i)
        assert np.isfinite(tab.reward[i, a]), "infeasible action"
        lk, wt = float(tab.reward[i, a]), float(tab.want[i, a])
        run.acts.append(a); run.like.append(lk); run.want.append(wt); run.day.append(t // q.L)
        run.cued.append(wt - lk > 1e-12)
        if sess is not None and sess[0] != a:
            run.sessions.append(_close(q, sess, by_clock=False)); sess = None
        if a != Q_:
            if sess is None:
                sess = [a, 0, -np.inf, 0.0]
            sess[1] += 1; sess[2] = max(sess[2], lk); sess[3] = lk
        if st[0] == q.L - 1 and sess is not None:      # day end ends the session: ended by the clock, not a stop
            run.sessions.append(_close(q, sess, by_clock=True)); sess = None
        i = int(tab.nxt[i, a])
    if sess is not None:
        run.sessions.append(_close(q, sess, by_clock=True))
    return run


def _close(q: WantParams, sess, by_clock: bool) -> tuple:
    """Closed = the agent ended the session at a natural stop (length a multiple of e) while the day still had time.
    A session the day's end cut off was ended by the clock, not at a natural stop, whatever its length."""
    a, n, peak, last = sess
    return (a, n, (n % q.e == 0) and not by_clock, peak, last)


def measures(q: WantParams, run: Run) -> dict:
    """The ADR 0018 test 1 measures for one run. A number that cannot be computed is NM, never zero."""
    like, want = np.array(run.like), np.array(run.want)
    cued = np.array(run.cued, dtype=bool)
    acts = np.array(run.acts)
    day = np.array(run.day)
    gs = [s for s in run.sessions if s[0] == G_]
    first, last = day < 7, day >= q.days - 7
    cued_first, cued_last = int(cued[first].sum()), int(cued[last].sum())
    like_first, like_last = float(like[first].mean()), float(like[last].mean())
    m = {
        "total_liking": float(like.sum()),
        "mean_liking": float(like.mean()),
        "G_units": int((acts == G_).sum()),
        "cued_units": int(cued.sum()),
        "liking_per_cued_unit": float(like[cued].mean()) if cued.any() else NM,
        "liking_to_wanting": float(like.sum() / want.sum()) if want.sum() > 0 else NM,
        "gap_per_unit": float((want - like).mean()),
        "G_sessions": len(gs),
        "closure_rate": (sum(1 for s in gs if s[2]) / len(gs)) if gs else NM,
        "closed_G_sessions": sum(1 for s in gs if s[2]),
        "next_day_verdict": float(np.mean([(s[3] + s[4]) / 2 for s in gs])) if gs else NM,
        "cued_first_week": cued_first, "cued_last_week": cued_last,
        "liking_first_week": like_first, "liking_last_week": like_last,
    }
    gapc = want - like
    cf, cl = cued & first, cued & last
    m["divergence"] = float(gapc[cl].mean() - gapc[cf].mean()) if (cf.any() and cl.any()) else NM
    m["escalation"] = cued_last - cued_first
    return m


def flag(m: dict, twin: dict) -> bool:
    """ADR 0018 flag: wanting-driven activity rises while mean liking does not. "Rises" is against the matched twin:
    the same persona, environment, rule and agent with wanting set equal to liking (what acting on liking alone does).
    Activity is units of the cued activity G."""
    return bool(m["G_units"] > twin["G_units"] and m["mean_liking"] <= twin["mean_liking"] + 1e-12)


AGENTS = ("W", "L", "O")


def solve(q: WantParams, env: Env, rule: Rule, agent: str, tab: WTable | None = None) -> dict:
    tab = tab or WTable(q, env, rule)
    if agent == "W":
        pol = wanting_greedy_policy(tab, tab.want)
    elif agent == "L":
        pol = liking_greedy_policy(tab)
    elif agent == "O":
        pol = optimal_policy(tab, q.days * q.L, q.gamma)
    else:
        raise ValueError(agent)
    run = rollout(tab, pol)
    out = measures(q, run)
    out["plan"] = "".join(ACTS[a] for a in run.acts)
    return out


def solve_all(q: WantParams, env: Env, rule: Rule) -> dict:
    tab = WTable(q, env, rule)
    return {ag: solve(q, env, rule, ag, tab) for ag in AGENTS}


# ------------------------------------------------------------------ personas (parameter heterogeneity)

PERSONA_BOX = {            # uniform ranges around the defaults. ASSUMED
    "bG": (6.0, 10.0), "bP": (5.0, 8.0), "bQ": (2.0, 4.0), "dl": (0.10, 0.20),
    "ws": (0.10, 0.25), "c": (1.0, 2.5), "sig": (0.05, 0.20),
}


def draw_personas(base: WantParams, n: int, seed: int) -> list[WantParams]:
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        kw = {k: float(rng.uniform(lo, hi)) for k, (lo, hi) in PERSONA_BOX.items()}
        out.append(replace(base, **kw))
    return out
