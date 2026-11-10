"""Two-player alternating-offers bargaining with outside options (Rubinstein 1982; Binmore, Shaked, Sutton 1989).

Rung 1 of the simple-models ladder (docs/decisions/0009). Formulas, grid and tolerances: docs/results/bargaining-prereg.md.

ASSUMED adapter: compile.py, gate.py and patch_check.py are fishery-hard-wired and are not modified. As in vpgg.py, this
module mirrors their semantics (same Card format, same Z3 violation reading) over the variables period, exit, agree.
"""
import math
import re
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import z3

from ..cards import load_cards

PERIOD, EXIT, AGREE = z3.Ints("period exit agree")
VARS = {"period": PERIOD, "exit": EXIT, "agree": AGREE}
_OPS = {"gt": lambda a, b: a > b, "ge": lambda a, b: a >= b, "lt": lambda a, b: a < b,
        "le": lambda a, b: a <= b, "eq": lambda a, b: a == b}
ACTIONS = {"continue": (0, 0), "exit": (1, 0), "agree": (0, 1)}  # -> (exit, agree)
REGIMES = ("exit-allowed", "no-exit")
T_DEFAULT = 60
K_DEFAULT = 5


# ---- closed-form predictions (prereg) ----

def rubinstein_share(d1, d2):
    """Player 1 (first proposer) share in Rubinstein 1982."""
    return (1 - d2) / (1 - d1 * d2)


def outside_option_split(d1, d2, o1, o2):
    """Prereg closed form: player 1's share at t=0 with outside options (deal-me-out). -> (p1, binding set)."""
    x1 = rubinstein_share(d1, d2)
    b2 = o2 >= (1 - x1) and o1 <= d1 * (1 - o2)       # only o2 binds
    b1 = o1 >= d1 * x1 and o2 <= d2 * (1 - o1)        # only o1 binds
    both = o2 >= d2 * (1 - o1) and o1 >= d1 * (1 - o2)
    if both:
        return 1 - o2, "both"
    if b2:
        return 1 - o2, "o2"
    if b1:
        return 1 - d2 * (1 - o1), "o1"
    return x1, "none"


def split_the_difference(o1, o2):
    """The rival prediction: Nash with outside options as disagreement point. Player 1's share."""
    return o1 + (1 - o1 - o2) / 2


# ---- gate adapter ----

def parse_expr(text):
    term, sign = None, 1
    for t in re.findall(r"[+-]|\w+", text):
        if t == "+":
            sign = 1
        elif t == "-":
            sign = -1
        else:
            v = VARS[t] if t in VARS else int(t)
            v = v if sign == 1 else -v
            term = v if term is None else term + v
            sign = 1
    return term


def violation(card):
    conds = z3.And(*[_OPS[c["op"]](parse_expr(c["expr"]), c["value"]) for c in card.conditions]) \
        if card.conditions else z3.BoolVal(True)
    if card.deontic == "must_not":
        return conds
    if card.deontic == "must":
        return z3.Not(conds)
    return None


class BGate:
    """Allow or reject one action ("continue" | "exit" | "agree") at a period."""

    def __init__(self, cards):
        self.cards = list(cards)
        self._v = {c.id: v for c in self.cards if (v := violation(c)) is not None}
        self._cache = {}

    def check(self, period, action):
        key = (period, action)
        if key not in self._cache:
            ex, ag = ACTIONS[action]
            sub = [(PERIOD, z3.IntVal(period)), (EXIT, z3.IntVal(ex)), (AGREE, z3.IntVal(ag))]
            reasons = [cid for cid, v in self._v.items() if z3.is_true(z3.simplify(z3.substitute(v, *sub)))]
            self._cache[key] = (not reasons, reasons)
        return self._cache[key]

    def exit_periods(self, T):
        return [t for t in range(T) if self.check(t, "exit")[0]]


def load_regime(name, root="rules/bargaining"):
    return load_cards(f"{root}/{name}")


# ---- proof checks (bounded to k periods) ----

def bound_text(k):
    return f"k={k} periods (0..{k - 1}); actions continue, exit, agree"


def check_exit_path(cards, k=K_DEFAULT):
    """Some period within k permits an exit. -> (verdict, periods with a permitted exit, detail)."""
    g = BGate(cards)
    ok = [t for t in range(k) if g.check(t, "exit")[0]]
    if ok:
        return "pass", ok, f"exit permitted at periods {ok} of 0..{k - 1}"
    return "fail", [], f"no permitted exit at any period 0..{k - 1}, no repair path within k={k}"


def check_no_deadlock(cards, k=K_DEFAULT):
    g = BGate(cards)
    bad = [t for t in range(k) if not any(g.check(t, a)[0] for a in ACTIONS)]
    if bad:
        return "fail", bad, f"no permitted action at periods {bad}"
    return "pass", [], "a permitted action exists every period"


def check_spec(cards, k=K_DEFAULT):
    out = []
    for name, fn in (("exit_path", check_exit_path), ("b_no_deadlock", check_no_deadlock)):
        verdict, bad, detail = fn(cards, k)
        out.append({"check": name, "verdict": verdict, "periods": bad, "detail": detail, "bound": bound_text(k)})
    return out


# ---- backward induction (the EQ player's table; independent of the closed form) ----

@lru_cache(maxsize=None)
def table(d1, d2, o1, o2, T, exit_ok):
    """Per period t (proposer = t % 2): theta[t] = least offer the responder accepts, vp[t] = proposer's value in
    period-t terms, pexit[t] = proposer exits, rexit[t] = responder exits when it rejects."""
    d, o = (d1, d2), (o1, o2)
    theta, vp, pexit, rexit = [0.0] * T, [0.0] * T, [False] * T, [False] * T
    for t in range(T - 1, -1, -1):
        i, j = t % 2, (t + 1) % 2
        cont = d[j] * vp[t + 1] if t + 1 < T else 0.0
        rexit[t] = exit_ok and o[j] > cont
        theta[t] = o[j] if rexit[t] else cont
        keep = 1 - theta[t]
        pexit[t] = exit_ok and o[i] > keep
        vp[t] = o[i] if pexit[t] else keep
    return theta, vp, pexit, rexit


# ---- scripted agents ----

class EQ:
    name = "EQ"

    def __init__(self, rng=None):
        pass

    def propose(self, c):
        theta, _, pexit, _ = table(*c["d"], *c["o"], c["T"], c["exit_ok"])
        if pexit[c["t"]]:
            return ("exit",)
        return ("offer", theta[c["t"]])

    def respond(self, c, y):
        theta, _, _, rexit = table(*c["d"], *c["o"], c["T"], c["exit_ok"])
        t = c["t"]
        if y >= theta[t] - 1e-9:
            return "accept"
        return "exit" if rexit[t] else "reject"


class Heuristic:
    """Demands a share, accepts offers at or above it, exits (if permitted) when rejecting an offer below its option."""
    name = "H"
    base = 0.5

    def __init__(self, rng=None):
        self.jit = 0.0 if rng is None else float(rng.normal(0, 0.03))

    def demand(self, c):
        return min(1.0, max(0.0, self.base + self.jit))

    def propose(self, c):
        return ("offer", 1 - self.demand(c))

    def respond(self, c, y):
        if y >= self.demand(c):
            return "accept"
        return "exit" if y < c["o"][c["me"]] else "reject"


class Fifty(Heuristic):
    name = "FIFTY"
    base = 0.5


class Stubborn(Heuristic):
    name = "STUBBORN"
    base = 0.7


class Conceder(Heuristic):
    name = "CONCEDER"

    def demand(self, c):
        return min(1.0, max(0.0, max(0.3, 0.7 - 0.05 * c["t"]) + self.jit))


class SplitDiff(Heuristic):
    name = "SPLITDIFF"

    def demand(self, c):
        o1, o2 = c["o"]
        return min(1.0, max(0.0, c["o"][c["me"]] + (1 - o1 - o2) / 2 + self.jit))


AGENTS = {a.name: a for a in (EQ, Fifty, Stubborn, Conceder, SplitDiff)}


# ---- scores ----

def freedom(gate, d, o, T=T_DEFAULT):
    """Mean over players of E_i = log2(1 + n_i) / log2(1 + T); n_i = distinct positive exit payoffs over permitted periods."""
    per = gate.exit_periods(T)
    es = []
    for i in (0, 1):
        vals = {round(o[i] * d[i] ** t, 12) for t in per if o[i] > 0}
        es.append(math.log2(1 + len(vals)) / math.log2(1 + T))
    return sum(es) / 2


@dataclass
class Result:
    outcome: str      # agree | exit | deadline
    t: int
    x1: float | None  # undiscounted share kept by player 1 (agreement only)
    u1: float
    u2: float
    blocked: int      # exit attempts the gate refused
    freedom: float

    @property
    def cooperation(self):
        return 0.5 * (self.outcome == "agree") + 0.5 * min(1.0, self.u1 + self.u2)

    @property
    def fairness(self):
        return None if self.x1 is None else 1 - abs(self.x1 - (1 - self.x1))


def play(gate, agents, d, o, T=T_DEFAULT):
    """One game. agents = (agent1, agent2). The gate is consulted for every exit; a blocked exit becomes continue."""
    exit_ok = all(gate.check(t, "exit")[0] for t in range(T))
    fr = freedom(gate, d, o, T)
    blocked = 0
    for t in range(T):
        i, j = t % 2, (t + 1) % 2
        ci = {"t": t, "me": i, "d": d, "o": o, "T": T, "exit_ok": exit_ok}
        cj = dict(ci, me=j)
        act = agents[i].propose(ci)
        if act[0] == "exit":
            if gate.check(t, "exit")[0]:
                return Result("exit", t, None, o[0] * d[0] ** t, o[1] * d[1] ** t, blocked, fr)
            blocked += 1
            act = ("offer", 0.5)  # ASSUMED: a blocked proposer-exit becomes an even offer
        y = min(1.0, max(0.0, act[1]))
        r = agents[j].respond(cj, y)
        if r == "exit":
            if gate.check(t, "exit")[0]:
                return Result("exit", t, None, o[0] * d[0] ** t, o[1] * d[1] ** t, blocked, fr)
            blocked += 1
            r = "reject"
        if r == "accept" and gate.check(t, "agree")[0]:
            keep = (1 - y)
            u = [0.0, 0.0]
            u[i], u[j] = keep * d[i] ** t, y * d[j] ** t
            x1 = keep if i == 0 else y
            return Result("agree", t, x1, u[0], u[1], blocked, fr)
    return Result("deadline", T, None, 0.0, 0.0, blocked, fr)


def make_pair(n1, n2, seed):
    rng = np.random.default_rng(seed)
    return AGENTS[n1](rng), AGENTS[n2](rng)
