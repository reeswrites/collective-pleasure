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


@dataclass(frozen=True)
class MakerConfig:
    credit: str = "zero"          # one of CREDIT_RULES
    protect: str = "off"          # one of PROTECT
    block_units: float = 1.0      # time units per block (of the week's 10; half a rest or together session)
    max_blocks: int = 3
    time_cost: float = 0.02       # a block's time cost in pleasure units, as the maker weighs it (calibrated, Amendment 1)
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
    return {"kind": KINDS[int(_u(persona.id, "kind") * 3)], "e": ENJOY[int(_u(persona.id, "enjoy") * 3)],
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
            "crave_got": {"A": 0.0, "B": 0.0}, "exit_shares": []}


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


def choose_blocks(world, m, rule=None, recv=None):
    """The scripted weekly choice: make block k while e x proc + care x g_k (+ own share of an artist's piece) + motive - time cost
    > 0. g_k is the receiver's liking (safe aim) or wanting (extractive aim). The motive is kappa x money weight x credit per block,
    only under a rule with a running tally."""
    st, cfg = world.makers, world.makers["cfg"]
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
        if tr["e"] == 0.0:
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
