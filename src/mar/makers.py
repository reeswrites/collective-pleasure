"""H39 makers (docs/results/h39-makers-design.md, prereg docs/results/h39-makers-prereg.md): partners who make food, art and games,
or give care; what they make gives the other partner pleasure; making costs time; and making counts as contribution in the F4 exit
split under one of six crediting rules. Also the per-persona suffering weight w used by the "weighted" decision rule.

Wording rule (ADR 0010): agents feel nothing; "pleasure", "liking" and "wanting" are glosses for modeled values.

OFF by default (`ACTIVE` None): no world has a makers state and nothing here is read, so every earlier run is bit-identical
(tests/test_makers.py against tests/data/makers_off_fingerprints.json). Every number is ASSUMED unless a comment says otherwise.
Tolerance, satiety and sensitization numbers are taken from `wanting.WantParams` (ADR 0018 test 1), ported from days to weeks.

Hooks (all guarded by `world.makers`): `init_world` at WeeklyWorld creation, `week_start` at the start of each week (the making
choice; time comes out of the week's units), `week_terms` when a partner's week closes (pleasure and craving terms into the existing
extra-pleasure and friction inputs), `contribution_basis` from exit_fallback.contribution_share (the F4 "all" basis plus credit).
"""
from __future__ import annotations

import hashlib
import math
from contextlib import contextmanager
from dataclasses import dataclass, replace
from statistics import NormalDist

from .wanting import WantParams

_WP = WantParams()
KINDS = ("cook", "artist", "carer")
ENJOY = (0.0, 0.5, 1.0)
CREDIT_RULES = ("zero", "hours", "pleasure", "bp", "gift", "agreed")
TALLY = ("hours", "pleasure", "bp")           # rules with a running tally (the making choice sees the credit)
AGREE_CANDIDATES = ("bp", "hours", "pleasure")  # C-agreed: the pair agrees HOW making counts (it counts); order breaks ties
PROTECT = ("off", "negotiated", "imposed")
CHOICES = ("flat_cost", "opportunity")      # H39's choice (a flat time cost per block) and H39b's (the agent's own best other use)
ENJOY_H39B = (-1.0, 0.0, 1.0)                # H39b: enjoyment can be negative (effort enters here); same hash, same ranks as ENJOY


@dataclass(frozen=True)
class MakerConfig:
    credit: str = "zero"          # one of CREDIT_RULES
    protect: str = "off"          # one of PROTECT
    choice: str = "flat_cost"     # one of CHOICES. "flat_cost" is H39 (bit-identical, pinned); "opportunity" is H39b (no time_cost)
    enjoy: tuple = ENJOY          # enjoyment levels, a third each by hash rank (H39: 0, 0.5, 1; H39b: -1, 0, +1)
    trap_h: int = 3               # H39b wanting trap: tolerance at least this (of tol_cap) ...
    trap_s: int = 9               # ... and sensitization at least this (of sens_cap), in the same person-week
    block_units: float = 1.0      # time units per block (of the week's 10; half a rest or together session)
    max_blocks: int = 3
    time_cost: float = 0.02       # H39 only (choice "flat_cost"): a flat time cost per block, FITTED so makers-on matched makers-off
    #                               (H39 Amendment 1). Not read under "opportunity" (H39b): no fitted time cost anywhere.
    proc: float = 0.005           # process pleasure per block at enjoyment 1
    kappa: float = 0.007          # credit motive: pleasure-equivalent per money unit of credit, times the persona's money weight
    rho: float = 1.375            # replacement value of a block in money units (the wage for 1 time unit: 4 units earn 5 to 6)
    ref_like: float = 0.025       # a typical block's pleasure to the receiver (C-pleasure's rate is rho / ref_like)
    cook: float = 0.03            # a meal: once, this week
    care: float = 0.02            # care: once, in the moment
    care_low: float = 0.03        # care when the receiver is struggling (low mood, ill, out of work)
    art_weekly: float = 0.003     # a piece: to each partner, per week, while both live together
    art_weeks: int = 8
    ws: float = _WP.ws            # within-week satiety per extra block (wanting.WantParams.ws)
    dl: float = _WP.dl            # liking lost per tolerance level (WantParams.dl)
    tol_cap: int = _WP.H          # tolerance cap (WantParams.H)
    dose: int = _WP.dose          # blocks in a week that raise the receiver's tolerance one level (WantParams.dose)
    cue: float = 0.01             # extractive goods: wanting = liking + cue x (1 + sig x s)
    sig: float = _WP.sig          # sensitization growth per level (WantParams.sig)
    sens_cap: int = _WP.S         # sensitization cap (WantParams.S)
    boost: float = 0.2            # extractive goods are a little more liked when fresh (hyperpalatable)
    crave: float = 0.025          # craving cost (offsettable suffering) in a week without the good, at full sensitization
    extractive_share: float = 1 / 3
    proj_blocks: int = 32         # a long project (artists only)
    goal: float = 0.01            # per week while a project runs, to the artist ("having a goal"; an input, not a finding)
    work_weekly: float = 0.02     # a finished work: per week to each partner while together; the artist keeps it after a split
    proj_horizon: int = 52        # weeks of the finished work an artist counts when deciding to start
    build_rate: float = 2.0       # blocks per week an artist expects to put into a project
    hz0: float = 0.02             # perceived weekly hazard that the household splits
    hz_leave: float = 0.04        # ... plus this per past leave in this household
    hz_flag: float = 0.06         # ... plus this when the last reading said either partner would rather be apart
    trust_min: float = 0.4        # a partner agrees to protect only at or above this trust in the artist (household TRUST commit_min)
    review_every: int = 13
    paid_weeks: int = 13          # a project "paid" if the household stayed together this long after completion


DEFAULT = MakerConfig()
ACTIVE = None        # None = off; else a MakerConfig


@contextmanager
def use_makers(cfg):
    """Every WeeklyWorld built inside the block has makers under `cfg` (a MakerConfig); None turns makers off."""
    global ACTIVE
    saved, ACTIVE = ACTIVE, cfg
    try:
        yield cfg
    finally:
        ACTIVE = saved


# ---- persona traits ---------------------------------------------------------------------------------------------------------

def _u(pid, salt):
    """A uniform number in (0, 1) from a hash of the persona id and a salt (fixed per persona, independent across salts)."""
    h = int(hashlib.sha256(f"{pid}:{salt}".encode()).hexdigest()[:12], 16)
    return (h + 0.5) / 16 ** 12


def suffering_weight(persona):
    """w = exp(z), z ~ N(0, 0.6), clipped to [0, 4], drawn from the persona id alone (independent of risk tolerance and of the
    maker traits). docs/notes/decision-weights-research.md, accepted by the author 2026-11-11."""
    z = NormalDist(0.0, 0.6).inv_cdf(_u(persona.id, "w"))
    return min(4.0, max(0.0, math.exp(z)))


def traits(persona, cfg=None):
    cfg = cfg or ACTIVE or DEFAULT
    rank = int(_u(persona.id, "enjoy") * 3)
    return {"kind": KINDS[int(_u(persona.id, "kind") * 3)], "e": cfg.enjoy[rank], "e_rank": rank,
            "aim": "extractive" if _u(persona.id, "aim") < cfg.extractive_share else "safe", "w": suffering_weight(persona)}


# ---- state ------------------------------------------------------------------------------------------------------------------

def init_world(world):
    cfg = ACTIVE
    t = {r: traits(world.personas[r], cfg) for r in "AB"}
    return {"cfg": cfg, "traits": t, "rule": None if cfg.credit == "agreed" else cfg.credit, "agreed": None,
            "blocks": {"A": 0, "B": 0}, "liking_given": {"A": 0.0, "B": 0.0}, "comp": {"A": 0.0, "B": 0.0},
            "recv": {r: {"h": 0, "s": 0, "n": 0} for r in "AB"},        # as receiver: tolerance, sensitization, blocks got this week
            "week": {r: {"blocks": 0, "like": 0.0, "proj": False} for r in "AB"},
            "pieces": [], "works": [], "project": {"A": None, "B": None},
            "proj": {"started": 0, "protected": 0, "asked": 0, "agreed": 0, "refused": 0, "completed": 0, "abandoned": 0,
                     "comp_paid": 0.0, "log": []},
            "cum52": None, "weeks_made": 0, "weeks_together": 0, "by_kind": {k: 0 for k in KINDS},
            "e0_blocks": 0, "pleasure_got": {"A": 0.0, "B": 0.0}, "proc_got": {"A": 0.0, "B": 0.0},
            "crave_got": {"A": 0.0, "B": 0.0}, "exit_shares": [],
            # H39b measures (bookkeeping only; recorded under both choices, read by nothing in the world)
            "like_got": {"A": 0.0, "B": 0.0}, "want_got": {"A": 0.0, "B": 0.0}, "lost_tol": {"A": 0.0, "B": 0.0},
            "trap_weeks": {"A": 0, "B": 0}, "tol_weeks": {"A": 0, "B": 0}, "weeks_seen": 0, "w": 0,
            "dec": {"maker_weeks": 0, "blocks": 0, "v_proc": 0.0, "v_care": 0.0, "v_own": 0.0, "v_motive": 0.0, "alt_cost": 0.0,
                    "slack_blocks": 0, "zero_weeks": 0, "displaced": {}}}


def _both_in(world):
    return all(world.p[x]["in"] for x in "AB")


def _struggling(world, r):
    p = world.p[r]
    return world.hed[r].B < 0 or p["ill"] > 0 or p["jobless"] > 0


def block_like(world, m, k, recv=None):
    """Liking of maker m's k-th block this week (k = 1, 2, ...) to the receiver: per block for a cook or carer; a piece's lifetime
    value to the partner for an artist."""
    st, cfg = world.makers, world.makers["cfg"]
    o = world.other(m)
    tr = st["traits"][m]
    rv = recv or st["recv"][o]
    if tr["kind"] == "cook":
        base = cfg.cook
    elif tr["kind"] == "carer":
        base = cfg.care_low if _struggling(world, o) else cfg.care
    else:
        base = cfg.art_weekly * cfg.art_weeks
    if tr["aim"] == "extractive":
        base *= 1.0 + cfg.boost
    return base * max(0.0, 1.0 - cfg.dl * rv["h"]) * (1.0 - cfg.ws) ** (k - 1)


def block_want(world, m, k, recv=None):
    st, cfg = world.makers, world.makers["cfg"]
    like = block_like(world, m, k, recv)
    if st["traits"][m]["aim"] != "extractive":
        return like
    rv = recv or st["recv"][world.other(m)]
    return like + cfg.cue * (1.0 + cfg.sig * rv["s"])


def credit_per_block(rule, cfg, like):
    if rule == "hours":
        return cfg.rho
    if rule == "pleasure":
        return cfg.rho / cfg.ref_like * like
    if rule in ("bp", "gift"):
        return 0.5 * cfg.rho + 0.5 * cfg.rho / cfg.ref_like * like
    return 0.0


def choose_blocks(world, m, rule=None, recv=None, util=None):
    """The scripted weekly choice -> number of blocks (0 to max_blocks).

    "flat_cost" (H39): make block k while e x proc + care x g_k (+ own share of an artist's piece) + motive - time cost > 0.
    "opportunity" (H39b): no time cost; the n that maximizes the summed block values minus what the agent's own planned week loses
    when n units are taken away (`opportunity`). g_k is the receiver's liking (safe aim) or wanting (extractive aim). The motive is
    kappa x money weight x credit per block, only under a rule with a running tally."""
    st, cfg = world.makers, world.makers["cfg"]
    if cfg.choice == "opportunity":
        return opportunity(world, m, rule, recv, util)[0]
    tr, p = st["traits"][m], world.personas[m]
    rule = st["rule"] if rule is None else rule
    care, mw = float(p.weights.get("togetherness", 0.0)), float(p.weights.get("money", 0.0))
    n = 0
    for k in range(1, cfg.max_blocks + 1):
        like = block_like(world, m, k, recv)
        g = block_want(world, m, k, recv) if tr["aim"] == "extractive" else like
        own = like if tr["kind"] == "artist" else 0.0
        motive = cfg.kappa * mw * credit_per_block(rule, cfg, like) if rule in TALLY else 0.0
        if tr["e"] * cfg.proc + care * g + own + motive - cfg.time_cost > 0:
            n = k
        else:
            break
    return n


# ---- H39b: the opportunity-cost choice --------------------------------------------------------------------------------------

def block_values(world, m, rule=None, recv=None):
    """-> [(v_k, parts)] for k = 1..max_blocks: a block's value to its maker, with no time cost (H39b)."""
    st, cfg = world.makers, world.makers["cfg"]
    tr, p = st["traits"][m], world.personas[m]
    rule = st["rule"] if rule is None else rule
    care, mw = float(p.weights.get("togetherness", 0.0)), float(p.weights.get("money", 0.0))
    out = []
    for k in range(1, cfg.max_blocks + 1):
        like = block_like(world, m, k, recv)
        g = block_want(world, m, k, recv) if tr["aim"] == "extractive" else like
        parts = {"proc": tr["e"] * cfg.proc, "care": care * g, "own": like if tr["kind"] == "artist" else 0.0,
                 "motive": cfg.kappa * mw * credit_per_block(rule, cfg, like) if rule in TALLY else 0.0}
        out.append((sum(parts.values()), parts))
    return out


def _one():
    return 1.0


_STEP = {"see_friend": 0, "together": 1, "work": 2, "spend_self": 3, "spend_shared": 4, "rest": 5}     # which count an action moves
#        (rests are read only by agent values v2; under v1 the sixth count changes nothing)


class WeekPlanner:
    """The agent's own valuation of each use of time, as the week goes: PersonaAgent.utilities on the start-of-week observation,
    updated after each planned action the way the world's next observation would be (friends and together counts, the week's net
    income, the unpaid bill gap) and with an action dropped when the money for it is gone. No noise (so no draw is made from the
    agent's stream). Called with a state (friends, together, works, self spends, bill payments) -> {action: utility}. Memoized."""

    def __init__(self, world, m, w):
        from .worlds.household import SELF_STEP, SHARE_STEP, V2_INCOME
        self.ag = world.agents[m]
        self.o = world.obs(m, w, {"busy": {"A": False, "B": False}})
        self.inc, self.share, self.self_step = V2_INCOME[m], SHARE_STEP, SELF_STEP
        self.money = world.p[m]["money"]
        self.gap = max(0, world.need_month() - world.funded) if (world.p[m]["in"] or world.p[world.other(m)]["in"]) else 0
        self.memo = {}

    def __call__(self, st=(0, 0, 0, 0, 0, 0)):
        if st in self.memo:
            return self.memo[st]
        f, t, wk, ss, sp = st[:5]
        o = dict(self.o)
        a0 = self.o["asp"]
        o["asp"] = {"friends": a0["friends"] + f, "together": a0["together"] + t,
                    "net": a0["net"] + self.inc * wk - self.self_step * ss}
        o["gap"] = min(max(0, self.gap - self.share * sp), 10)
        if "v2" in self.o:              # agent values v2: the week so far moves with the plan (counts, rests, money, the bill funded)
            from . import agent_values as AV
            lev = self.o.get("lever")
            sc = (lev["friend_scale"], lev["together_scale"]) if (lev and lev["adaptive"]) else (1.0, 1.0)
            o["v2"] = AV.advance(self.o["v2"], friends=f, together=t, works=wk, self_spends=ss, shared=sp, rests=st[5] if len(st) > 5 else 0,
                                 inc=self.inc, self_step=self.self_step, share_step=self.share, scale=sc)
            if self.o.get("v2_partner") is not None:
                o["v2_partner"] = AV.advance(self.o["v2_partner"], together=t, scale=(1.0, sc[1]))
        ag = self.ag
        had, old = "_noise" in ag.__dict__, ag.__dict__.get("_noise")
        ag._noise = _one
        try:
            u = ag.utilities(o)
        finally:
            if had:
                ag._noise = old
            else:
                del ag._noise
        money = self.money + self.inc * wk - self.share * sp - self.self_step * ss
        if money < self.share:
            u.pop("spend_shared", None)
        if money < self.self_step:
            u.pop("spend_self", None)
        self.memo[st] = u
        return u


def week_utilities(world, m, w):
    """The agent's start-of-week utilities (WeekPlanner at the empty state). -> {action: utility}."""
    return WeekPlanner(world, m, w)()


def plan_week(util, budget, cost=None, passes=None, floor=0.003, start=(0, 0, 0, 0, 0, 0)):
    """The week as the world plays it: `passes` passes, each taking the highest-utility action above the agent's floor that fits in
    the units left. `util` is a WeekPlanner (utilities move after each action, as the world's do) or a fixed {action: utility}.
    -> (summed utility, [actions])."""
    if cost is None or passes is None:
        from .worlds.household import PASSES, V2_COST
        cost, passes = cost or V2_COST, passes or PASSES
    tot, acts, b, st = 0.0, [], budget, list(start)
    for _ in range(passes):
        u = util(tuple(st)) if callable(util) else util
        best = None
        for a, v in u.items():
            if v > floor and cost.get(a, 0) <= b + 1e-9 and (best is None or v > best[0]):
                best = (v, a)
        if best is None:
            break
        tot += best[0]
        acts.append(best[1])
        b -= cost[best[1]]
        if best[1] in _STEP:
            st[_STEP[best[1]]] += 1
    return tot, acts


def plan_value(util, budget, step=1, partner_sessions=0, together_cost=None):
    """V(b): the best planned week with at most b units. The partner's planned together sessions come first (they use this agent's
    units too, and this agent cannot plan them away), each worth this agent's own utility of time together at the start of the
    week; the agent's own plan fills the rest. Maximized over budgets b' <= b (an agent can always leave units idle, so V never
    falls when a unit is added). -> (value, [actions])."""
    if together_cost is None:
        from .worlds.household import V2_COST
        together_cost = V2_COST["together"]
    u0 = util() if callable(util) else util
    u_tog = max(0.0, u0.get("together", 0.0))
    best = (0.0, [])
    b = budget
    while b >= -1e-9:
        k = min(partner_sessions, int((b + 1e-9) // together_cost))
        v, acts = plan_week(util, b - k * together_cost, start=(0, k, 0, 0, 0, 0))
        v += k * u_tog
        if v > best[0] + 1e-12:
            best = (v, ["partner_together"] * k + acts)
        b -= step
    return best


def opportunity(world, m, rule=None, recv=None, util=None, partner_util=None):
    """H39b making choice. -> (n, info). n maximizes sum_{k<=n} v_k - [V(B) - V(B - n x block_units)], ties to fewer, where V(b)
    is the agent's best planned week with at most b units (`plan_value` on `week_utilities`, or `util` when given), counting the
    together sessions in the partner's own planned week (`partner_util`, computed from the world when `util` is not given)."""
    st, cfg = world.makers, world.makers["cfg"]
    vals = block_values(world, m, rule, recv)
    units = getattr(world, "units", None)
    if util is None:
        w = st.get("w", 0)
        util = WeekPlanner(world, m, w)
        partner_util = WeekPlanner(world, world.other(m), w)
    B = units[m] if units is not None else 10
    k_tog = 0
    if partner_util:
        pB = units[world.other(m)] if units is not None else 10
        k_tog = plan_week(partner_util, pB)[1].count("together")
    V0, acts0 = plan_value(util, B, partner_sessions=k_tog)
    best_n, best, cum, info = 0, 0.0, 0.0, {"n": 0, "alt": 0.0, "parts": {}, "displaced": [], "plan": acts0}
    for n in range(1, cfg.max_blocks + 1):
        if n * cfg.block_units > B + 1e-9:
            break
        cum += vals[n - 1][0]
        Vn, actsn = plan_value(util, B - n * cfg.block_units, partner_sessions=k_tog)
        net = cum - (V0 - Vn)
        if net > best + 1e-12:
            rest = list(actsn)
            disp = []
            for a in acts0:
                if a in rest:
                    rest.remove(a)
                else:
                    disp.append(a)
            best_n, best = n, net
            info = {"n": n, "alt": V0 - Vn, "displaced": disp, "plan": acts0,
                    "parts": {k: sum(v[1][k] for v in vals[:n]) for k in vals[0][1]}}
    return best_n, info


def _agree(world):
    """C-agreed: each partner projects each rule's credit share at a fresh start; same favourite -> that rule; else the most equal."""
    st = world.makers
    fresh = {"h": 0, "s": 0, "n": 0}
    shares = {}
    for rule in AGREE_CANDIDATES:
        c = {}
        for m in "AB":
            n = choose_blocks(world, m, rule, fresh)
            c[m] = sum(credit_per_block(rule, st["cfg"], block_like(world, m, k, fresh)) for k in range(1, n + 1))
        tot = c["A"] + c["B"]
        shares[rule] = {m: (c[m] / tot if tot > 0 else 0.5) for m in "AB"}
    fav = {m: max(AGREE_CANDIDATES, key=lambda r: (shares[r][m], -AGREE_CANDIDATES.index(r))) for m in "AB"}
    if fav["A"] == fav["B"]:
        pick = fav["A"]
    else:
        pick = max(AGREE_CANDIDATES, key=lambda r: (shares[r]["A"] * shares[r]["B"], -AGREE_CANDIDATES.index(r)))
    st["rule"], st["agreed"] = pick, {"pick": pick, "fav": fav, "shares": shares}


# ---- long projects ----------------------------------------------------------------------------------------------------------

def _p_complete(world, m, protected):
    st, cfg = world.makers, world.makers["cfg"]
    hz = cfg.hz0 + cfg.hz_leave * len(world.exit_log) + (cfg.hz_flag if any(world.bar_out.values()) else 0.0)
    hz *= 1.5 - float(world.personas[m].risk_tolerance)
    if protected:
        hz *= 1.0 - world.trust[m]                    # the artist believes the promise as far as they trust the partner
    T = math.ceil(cfg.proj_blocks / cfg.build_rate)
    return max(0.0, 1.0 - min(1.0, hz)) ** T, T


def project_values(world, m, w, protected):
    """(value of a long project, value of the same blocks as pieces), as the artist weighs them now."""
    cfg = world.makers["cfg"]
    care = float(world.personas[m].weights.get("togetherness", 0.0))
    p, T = _p_complete(world, m, protected)
    after = max(0, min(cfg.proj_horizon, world.weeks - w - T))
    long_v = cfg.goal * T + p * cfg.work_weekly * after * (1.0 + care)
    short_v = cfg.proj_blocks * cfg.art_weekly * cfg.art_weeks * (1.0 + care)
    return long_v, short_v


def _consider_project(world, m, w):
    st, cfg = world.makers, world.makers["cfg"]
    o = world.other(m)
    if cfg.protect == "imposed":
        lv, sv = project_values(world, m, w, True)
        if lv > sv:
            _start(world, m, w, True)
        return
    lv, sv = project_values(world, m, w, False)
    if lv > sv:
        _start(world, m, w, False)
        return
    if cfg.protect == "negotiated":
        lp, _ = project_values(world, m, w, True)
        if lp > sv:
            st["proj"]["asked"] += 1
            if world.trust[o] >= cfg.trust_min and not world.bar_out[o]:
                st["proj"]["agreed"] += 1
                _start(world, m, w, True)
            else:
                st["proj"]["refused"] += 1


def _start(world, m, w, protected):
    st = world.makers
    st["project"][m] = {"done": 0, "protected": protected, "from": w}
    st["proj"]["started"] += 1
    st["proj"]["protected"] += int(protected)
    st["proj"]["log"].append({"week": w, "who": m, "event": "start", "protected": protected})


def _abandon(world, w):
    """The household has split: running projects are lost. A protected project's blocks count for the artist if the partner is the
    one who is out (the promise was the partner's)."""
    st, cfg = world.makers, world.makers["cfg"]
    for m in "AB":
        pj = st["project"][m]
        if pj is None:
            continue
        if pj["protected"] and not world.p[world.other(m)]["in"]:
            st["comp"][m] += cfg.rho * pj["done"]
            st["proj"]["comp_paid"] += cfg.rho * pj["done"]
        st["project"][m] = None
        st["proj"]["abandoned"] += 1
        st["proj"]["log"].append({"week": w, "who": m, "event": "abandoned", "done": pj["done"], "protected": pj["protected"]})


# ---- weekly hooks -----------------------------------------------------------------------------------------------------------

def week_start(world, w):
    st, cfg = world.makers, world.makers["cfg"]
    for r in "AB":                                    # the receiver's clocks, from last week's dose
        rv = st["recv"][r]
        ext = st["traits"][world.other(r)]["aim"] == "extractive"
        if rv["n"] >= cfg.dose:
            rv["h"] = min(cfg.tol_cap, rv["h"] + 1)
        elif rv["n"] == 0:
            rv["h"] = max(0, rv["h"] - 1)
        if ext and rv["n"] > 0:
            rv["s"] = min(cfg.sens_cap, rv["s"] + rv["n"])
        elif rv["n"] == 0:
            rv["s"] = max(0, rv["s"] - 1)
        rv["n"] = 0
        st["tol_weeks"][r] += int(rv["h"] >= cfg.trap_h)
        st["trap_weeks"][r] += int(rv["h"] >= cfg.trap_h and rv["s"] >= cfg.trap_s)
    st["weeks_seen"] += 1
    st["w"] = w
    st["pieces"] = [(m, left - 1, q) for m, left, q in st["pieces"] if left > 1]     # (maker, weeks left, quality factor)
    st["week"] = {r: {"blocks": 0, "like": 0.0, "proj": False} for r in "AB"}
    if not _both_in(world):
        _abandon(world, w)
        return
    st["weeks_together"] += 1
    for wk in st["works"]:
        if wk["paid_count"] is not None:
            wk["paid_count"] += 1
    if st["rule"] is None:
        _agree(world)
    for m in "AB":
        tr = st["traits"][m]
        if tr["kind"] == "artist" and st["project"][m] is None and w % cfg.review_every == 0:
            _consider_project(world, m, w)
        if cfg.choice == "opportunity":
            n, info = opportunity(world, m)
            dec = st["dec"]
            dec["maker_weeks"] += 1
            dec["zero_weeks"] += int(n == 0)
            if n > 0:
                dec["blocks"] += n
                dec["alt_cost"] += info["alt"]
                dec["slack_blocks"] += n if info["alt"] <= 1e-12 else 0
                for k, v in info["parts"].items():
                    dec["v_" + k] += v
                for a in info["displaced"]:
                    dec["displaced"][a] = dec["displaced"].get(a, 0) + 1
        else:
            n = choose_blocks(world, m)
        pj = st["project"][m]
        if pj is not None:
            n = max(1, n)
        n = min(n, int(world.units[m] // cfg.block_units))
        if n <= 0:
            continue
        world.units[m] -= n * cfg.block_units
        st["blocks"][m] += n
        st["by_kind"][tr["kind"]] += n
        if tr["e_rank"] == 0:                 # the lowest-enjoyment third (H39: e = 0; H39b: e = -1)
            st["e0_blocks"] += n
        o = world.other(m)
        st["week"][m]["blocks"] = n
        if pj is not None:
            st["week"][m]["proj"] = True
            pj["done"] += n
            if pj["done"] >= cfg.proj_blocks:
                st["works"].append({"owner": m, "week": w, "paid_count": 0})
                st["project"][m] = None
                st["proj"]["completed"] += 1
                st["proj"]["log"].append({"week": w, "who": m, "event": "completed", "protected": pj["protected"]})
            continue
        likes = [block_like(world, m, k) for k in range(1, n + 1)]
        rv0 = dict(st["recv"][o], h=0)                # H39b: liking lost to tolerance (ADR 0018 test 1, the liking side)
        st["lost_tol"][o] += sum(block_like(world, m, k, rv0) for k in range(1, n + 1)) - sum(likes)
        st["like_got"][o] += sum(likes)
        st["want_got"][o] += sum(block_want(world, m, k) for k in range(1, n + 1))
        if tr["kind"] == "artist":
            st["pieces"].extend((m, cfg.art_weeks, lk / (cfg.art_weeks * cfg.art_weekly)) for lk in likes)
        else:
            st["week"][m]["like"] = sum(likes)
        st["recv"][o]["n"] += n
    st["weeks_made"] += 1
    if w == 51 or (st["cum52"] is None and w >= 51):
        st["cum52"] = dict(st["blocks"])


def week_terms(world, r, w=None):
    """-> (extra pleasure, extra friction) for partner r this week."""
    st, cfg = world.makers, world.makers["cfg"]
    o = world.other(r)
    both = _both_in(world)
    pl, fr = 0.0, 0.0
    if both:
        got = st["week"][o]["like"]                       # a meal or care from the partner
        for m, _, q in st["pieces"]:                      # pieces: shared while together
            pl += cfg.art_weekly * q
            if m == o:
                got += cfg.art_weekly * q
        for wk in st["works"]:
            pl += cfg.work_weekly
            if wk["owner"] == o:
                got += cfg.work_weekly
        pl += st["week"][o]["like"]
        st["liking_given"][o] += got
        proc = st["traits"][r]["e"] * cfg.proc * st["week"][r]["blocks"]
        if st["project"][r] is not None or st["week"][r]["proj"]:
            proc += cfg.goal
        pl += proc
        st["proc_got"][r] += proc
        rv = st["recv"][r]
        if st["traits"][o]["aim"] == "extractive" and rv["s"] > 0 and st["week"][o]["blocks"] == 0:
            fr = cfg.crave * rv["s"] / cfg.sens_cap
    else:
        for wk in st["works"]:                            # after a split the artist keeps the finished work
            if wk["owner"] == r:
                pl += cfg.work_weekly
    st["pleasure_got"][r] += pl
    st["crave_got"][r] += fr
    return pl, fr


# ---- credit and the exit split -----------------------------------------------------------------------------------------------

def credit(world, r, rule=None):
    """Making credit of partner r in money units under the world's crediting rule (C-gift-at-exit counts as base + pleasure)."""
    st = world.makers
    cfg = st["cfg"]
    rule = rule or st["rule"] or "zero"
    b, lk = st["blocks"][r], st["liking_given"][r]
    if rule == "hours":
        c = cfg.rho * b
    elif rule == "pleasure":
        c = cfg.rho / cfg.ref_like * lk
    elif rule in ("bp", "gift"):
        c = 0.5 * cfg.rho * b + 0.5 * cfg.rho / cfg.ref_like * lk
    else:
        c = 0.0
    return c + st["comp"][r]


def contribution_basis(world, leaver):
    """The F4 'all' basis with making: money put in + making credit, from the point of view of `leaver` (whose share is asked).
    A protected project still running counts for its artist if the leaver is the partner who promised."""
    st, cfg = world.makers, world.makers["cfg"]
    src = {x: world.money_in[x] + credit(world, x) for x in "AB"}
    for m in "AB":
        pj = st["project"][m]
        if pj is not None and pj["protected"] and leaver != m:
            src[m] += cfg.rho * pj["done"]
    return src


def config(credit="zero", protect="off", **kw):
    return replace(DEFAULT, credit=credit, protect=protect, **kw)
