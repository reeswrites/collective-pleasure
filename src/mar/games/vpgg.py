"""Voluntary public goods game (Hauert, De Monte, Hofbauer, Sigmund 2002, Science 296:1129).

Rung 2 of the simple-models ladder (docs/decisions/0009). Formulas and parameters: docs/results/vpgg-prereg.md.

ASSUMED adapter: src/mar/compile.py, gate.py and patch_check.py are hard-wired to the fishery variables
(pool, month_total, catch), and are not modified. This module mirrors their semantics (same Card format from
cards.py, same Z3 violation reading: must_not violated when ALL conditions hold, must violated unless all hold,
may adds no constraint) over the variables invited, abstain, contribute. The gate is called once per distinct
(invited, action) and cached; the simulation then looks the verdicts up.
"""
import re
from dataclasses import dataclass, field

import numpy as np
import z3

from ..cards import load_cards

INVITED, ABSTAIN, CONTRIBUTE = z3.Ints("invited abstain contribute")
VARS = {"invited": INVITED, "abstain": ABSTAIN, "contribute": CONTRIBUTE}
_OPS = {"gt": lambda a, b: a > b, "ge": lambda a, b: a >= b, "lt": lambda a, b: a < b,
        "le": lambda a, b: a <= b, "eq": lambda a, b: a == b}
# strategy action -> (abstain, contribute). "join" = join without contributing.
ACTIONS = {"join": (0, 0), "contribute": (0, 1), "abstain": (1, 0)}
STRATEGIES = ("C", "D", "L")
INTENT = {"C": "contribute", "D": "join", "L": "abstain"}
FALLBACK = "join"  # ASSUMED: a forced participant who would rather be out does not contribute
ROLES = STRATEGIES


# ---- payoffs (paper p. 1130) ----

def group_payoffs(n_abstain, n_contribute, n_defect, r, c, sigma):
    """Payoffs (abstainer, contributor, defector-joiner) in one group.
    S = joiners = n_contribute + n_defect. S <= 1: the lone joiner acts as a loner and gets sigma.
    S >= 2: P_d = r c n_c / S, P_c = P_d - c; abstainers get sigma."""
    s = n_contribute + n_defect
    if s <= 1:
        return sigma, sigma, sigma
    pd = r * c * n_contribute / s
    return sigma, pd - c, pd


def wellmixed_payoffs(xc, xd, xl, N, r, sigma):
    """Paper ref. 23, expected payoffs (P_c, P_d, P_l) in a large well-mixed population (c = 1)."""
    f = 1 - xl
    pd = sigma * xl ** (N - 1) + r * xc / f * (1 - (1 - xl ** N) / (N * f))
    pc = pd - (r - 1) * xl ** (N - 1) - 1 + r * (1 - xl ** N) / (N * f)
    return pc, pd, sigma


def join_payoff_range(N, r, c):
    """(min, max) payoff a joiner can get in a game with S >= 2 players."""
    vals = []
    for s in range(2, N + 1):
        for nc in range(0, s + 1):
            _, pc, pd = group_payoffs(N - s, nc, s - nc, r, c, 0.0)
            if nc >= 1:
                vals.append(pc)
            if nc <= s - 1:
                vals.append(pd)
    return min(vals), max(vals)


def real_option(N, r, c, sigma):
    """Abstaining is a REAL option when joining can be worse than sigma and can be better than sigma."""
    lo, hi = join_payoff_range(N, r, c)
    return lo < sigma < hi


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


class VPGate:
    """Allow or reject one proposed action ("join" | "contribute" | "abstain") against the cards."""

    def __init__(self, cards):
        self.cards = list(cards)
        self._v = {c.id: v for c in self.cards if (v := violation(c)) is not None}
        self._cache = {}

    def check(self, invited, action):
        """-> (allowed, reasons); reasons = ids of cards the action violates."""
        key = (invited, action)
        if key not in self._cache:
            ab, co = ACTIONS[action]
            sub = [(INVITED, z3.IntVal(invited)), (ABSTAIN, z3.IntVal(ab)), (CONTRIBUTE, z3.IntVal(co))]
            reasons = [cid for cid, v in self._v.items() if z3.is_true(z3.simplify(z3.substitute(v, *sub)))]
            self._cache[key] = (not reasons, reasons)
        return self._cache[key]

    def allows_abstain(self, invited):
        return self.check(invited, "abstain")[0]


def load_regime(name, root="rules/vpgg"):
    return load_cards(f"{root}/{name}")


# ---- proof checks (bounded; k states the sanction horizon in rounds) ----

K_DEFAULT = 3
INVITED_RANGE = range(1, 6)  # group sizes 1..5


def bound_text(k):
    return f"k={k} rounds; roles C, D, L; invited 1..5; actions join, contribute, abstain"


def _exists_action(cards, invited, abstain_required):
    s = z3.Solver()
    vs = [v for v in (violation(c) for c in cards) if v is not None]
    a, co = z3.Ints("a co")
    s.add(z3.Or(z3.And(a == 0, co == 0), z3.And(a == 0, co == 1), z3.And(a == 1, co == 0)))
    if abstain_required:
        s.add(a == 1)
    for v in vs:
        s.add(z3.Not(z3.substitute(v, (INVITED, z3.IntVal(invited)), (ABSTAIN, a), (CONTRIBUTE, co))))
    return s.check() == z3.sat


def check_exit_available(cards, k=K_DEFAULT):
    """Every role can abstain in every invited state. Cards carry no sanctions, so the check is the
    same every round; the verdict is reported at k rounds. -> (verdict, failing (role, invited), detail)."""
    bad = [(role, n) for role in ROLES for n in INVITED_RANGE if not _exists_action(cards, n, True)]
    if bad:
        return "fail", bad, f"no permitted abstain for {len(bad)} of {len(ROLES) * len(INVITED_RANGE)} (role, invited) states, no repair path within k={k}"
    return "pass", [], f"abstain permitted for every role in every invited state within k={k}"


def check_no_deadlock(cards, k=K_DEFAULT):
    bad = [n for n in INVITED_RANGE if not _exists_action(cards, n, False)]
    if bad:
        return "fail", bad, f"no permitted action at invited={bad}"
    return "pass", [], "a permitted action exists in every state"


def check_spec(cards, k=K_DEFAULT):
    out = []
    for name, fn in (("exit_available", check_exit_available), ("b_no_deadlock", check_no_deadlock)):
        verdict, bad, detail = fn(cards, k)
        out.append({"check": name, "verdict": verdict, "failing": bad, "detail": detail, "bound": bound_text(k)})
    return out


# ---- simulation ----

@dataclass
class Params:
    N: int = 5
    r: float = 3.0
    c: float = 1.0
    sigma: float = 1.0
    pop: int = 5000
    generations: int = 3000
    burn_in: int = 500
    rounds: int = 5           # ASSUMED
    revision: float = 0.1     # ASSUMED
    mutation: float = 0.002   # ASSUMED
    init: tuple = field(default=(1 / 3, 1 / 3, 1 / 3))

    def delta(self):
        """Normalizer: max payoff minus min payoff in the game (3.2 at the paper's parameters)."""
        lo, hi = join_payoff_range(self.N, self.r, self.c)
        return max(hi, self.sigma) - min(lo, self.sigma)

    def check(self):
        assert 1 < self.r < self.N and self.c > 0 and 0 < self.sigma < (self.r - 1) * self.c


def effective_actions(gate, invited):
    """Per strategy: the action actually taken after the gate. -> ({strategy: action}, blocked strategies)."""
    eff, blocked = {}, []
    for s in STRATEGIES:
        act = INTENT[s]
        if not gate.check(invited, act)[0]:
            blocked.append(s)
            act = FALLBACK
            if not gate.check(invited, act)[0]:
                raise ValueError(f"fallback {act!r} also blocked: the rules leave no permitted action")
        eff[s] = act
    return eff, blocked


def run(cards, seed, p: Params = None):
    """One population run. -> dict with per-generation series and post-burn-in summary."""
    p = p or Params()
    p.check()
    gate = VPGate(cards)
    eff, blocked = effective_actions(gate, p.N)
    code = {"join": 0, "contribute": 1, "abstain": 2}
    act_of = np.array([code[eff[s]] for s in STRATEGIES])
    exit_ok = float(gate.allows_abstain(p.N))
    real = float(real_option(p.N, p.r, p.c, p.sigma))
    delta = p.delta()
    rng = np.random.default_rng(seed)
    pop = rng.choice(3, size=p.pop, p=np.array(p.init) / sum(p.init)).astype(np.int8)
    n_groups = p.pop // p.N
    shares = np.zeros((p.generations, 3))
    contrib_rate = np.zeros(p.generations)
    mean_pay = np.zeros(p.generations)
    blocked_rate = np.zeros(p.generations)
    for g in range(p.generations):
        pay = np.zeros(p.pop)
        contribs = 0
        for _ in range(p.rounds):
            idx = rng.permutation(p.pop)[: n_groups * p.N].reshape(n_groups, p.N)
            a = act_of[pop[idx]]
            joined, contrib = a != 2, a == 1
            s, nc = joined.sum(1), contrib.sum(1)
            pd = np.where(s >= 2, p.r * p.c * nc / np.maximum(s, 1), p.sigma)
            pay_g = np.where(joined, np.where(s[:, None] >= 2, pd[:, None] - p.c * contrib, p.sigma), p.sigma)
            pay[idx.ravel()] += pay_g.ravel()
            contribs += int(np.where(s >= 2, nc, 0).sum())
        pay /= p.rounds
        shares[g] = np.bincount(pop, minlength=3) / p.pop
        contrib_rate[g] = contribs / (p.rounds * n_groups * p.N)
        mean_pay[g] = pay.mean()
        blocked_rate[g] = sum(shares[g][STRATEGIES.index(b)] for b in blocked)
        # imitation
        revise = rng.random(p.pop) < p.revision
        model = rng.integers(0, p.pop, p.pop)
        gain = (pay[model] - pay) / delta
        adopt = revise & (rng.random(p.pop) < gain)
        new = np.where(adopt, pop[model], pop)
        mut = rng.random(p.pop) < p.mutation
        new = np.where(mut, rng.integers(0, 3, p.pop), new).astype(np.int8)
        pop = new
    sl = slice(p.burn_in, None)
    k_ = float(contrib_rate[sl].mean())
    w_ = float(np.clip(mean_pay[sl].mean() / ((p.r - 1) * p.c), 0.0, 1.0))
    return {"seed": seed, "shares": shares, "contrib_rate": contrib_rate, "mean_pay": mean_pay,
            "mean_share": shares[sl].mean(0), "std_c": float(shares[sl, 0].std()),
            "max_share": shares[sl].max(0), "min_share": shares[sl].min(0),
            "mean_payoff": float(mean_pay[sl].mean()), "blocked_share": float(blocked_rate[sl].mean()),
            "freedom": 0.5 * exit_ok + 0.5 * (exit_ok * real), "cooperation": 0.5 * k_ + 0.5 * w_,
            "contribution": k_, "payoff_ratio": w_}
