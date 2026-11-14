"""The hybrid agent (docs/results/hybrid-agent-prereg.md; step 2 of docs/notes/step-back-review.md).

Wording rule: agents feel nothing; "pleasure", "value" and "forecast" are glosses for modeled numbers.

Read only when FixConfig(agent_values="hybrid"). Off by default: with any other value nothing here is called and every run is as before
(tests/data/scale_off_fingerprints.json, tests/test_hybrid.py).

Three parts:
  routine     the weekly actions (work, rest, friends, together, spending) are v2's, unchanged: one week of the close's own arithmetic.
  big choices forming (week 0 and the 13-week retries), staying or leaving (the readings, and an early reading when a member is in
              distress), returning, and the week-0 stay and request commitments are chosen by simulation: each option is played over K
              sampled futures with fresh shocks and fresh random streams on BOTH sides (the household and the outside option), and scored
              on one declared yardstick, the evaluator's own measure: the member's mean weekly pleasure on the scale in force (ADR 0019).
              The old rollouts deep-copied the lived world's own shock schedule for the status quo (a known future) and sampled the
              outside option (an unknown one); here neither side sees the real future.
  bills       who pays the month's bill is a household agreement made at formation: shares proportional to income ("income", 6:5) or
              equal ("equal"), chosen by simulation like any big choice. Each member pays its share at month end as a standing
              transfer, kept as a commitment (it needs no foresight and takes no action unit).
  fixed scores the propose-only actions (request, refuse a request, veto, give, take from the pot) are valued by a one-week simulation
              in the lived world: the week replayed from its start with the action forced at the same call, against idle, own net plus
              the prosocial share of the partner's (the value check's own known answer at one week). Leave and return are valued as the
              simulated gain per week times the horizon. Inside a forecast no fork is made: forecasts assume no request, refusal, veto,
              gift or take (a declared simplification).
  misforecasting  optional persona fields of the big-choice forecast, `Persona.forecast` = {"horizon": weeks, "discount": per week,
              "outside_bias": added to the outside option}. Neutral by default (empty dict).

Amendment 4 (docs/results/hybrid-exit-option-prereg.md), two flags, both off by default:
  hybrid_lone  a member alone in the household holds the pair reading (13-week and distress, same bar; lone_reading), and once the
              household is empty the pair counts as apart so the 13-week retry runs (lone_apart).
  hybrid_exit  every forecast future holds in-future readings every 13 weeks (future_reading): a member whose last 13 future weeks fell
              short of its outside option, anchored at the choice (exit_ref, default_ref), by more than the margin twice in a row gets
              leave on its menu, so forecasts carry the option value of exit.

Amendment 5 (docs/results/hybrid-leaving-prereg.md), all off by default:
  hybrid_tally a fading running tally of each member's weekly yardstick against its outside option as last valued (tally_step); when
              it falls below the line (or fast, under "slope") the member rethinks: a lived reading (due, lone_due) and, inside
              forecasts, an in-future reading (fut_due), by the same rule, so forecasts and life look at the same moments.
  exit_fixed, exit_grow   a leaver pays a weekly pleasure cost for exit_cost_weeks after leaving, growing with its weeks in the
              household (on_leave, exit_cost_now); outside options and in-future anchors of members in price it (antic).
  hybrid_outside="lived"  the outside option of a member in a household is the lived world played on with that member gone
              (lived_outside); leave_bias lowers it (the biased-forecast arm).

Not built: project protection (H39 makers) as a simulated choice. A makers world with negotiated protection refuses to run under the hybrid.
"""
from __future__ import annotations

import copy
import random
import types
import zlib
from contextlib import contextmanager

from . import hedonic as HD

TERMS = {"income": None, "equal": {"A": 0.5, "B": 0.5}}       # None: proportional to income (V2_INCOME)
FORK_ACTS = ("request", "refuse_request", "veto", "give", "take_shared")
AUDIT = None          # a list while the held-out audit is on: every big choice also scored on AUDIT_M held-out futures
AUDIT_M = 16
STATS = {"futures": 0, "future_weeks": 0, "forks": 0, "choices": 0}
_NEUTRAL = [False]    # True while held-out values are computed: the declared yardstick, with no persona forecast trait
_MEMO = {}            # forward forecasts within one forward_memo block: (id(world), w, weeks, fx, last) -> values
_REF = [None]         # Amendment 4 (hybrid_exit): {role: (outside value, apart mode)}, the anchor of in-future readings, set by a choice
_FLOG = [None]        # a list while a reading's status quo is logged: each future's exit weeks, relative to the reading (second measure)
_OCTX = [None]        # Amendment 5: (world, w, last) of the lived choice whose outside options are being valued (outside_ctx)
EXIT_LOG = None       # a list while the forecast-vs-lived exit check is on: one entry per reading status quo (hybrid-exit-option-prereg.md)


def on(fx=None):
    fx = fx if fx is not None else HD.active_fixes()
    return fx is not None and fx.agent_values == "hybrid"


def traits(p):
    t = getattr(p, "forecast", None) or {}
    return {"horizon": t.get("horizon"), "discount": float(t.get("discount", 1.0)), "outside_bias": float(t.get("outside_bias", 0.0))}


def k_of(fx=None):
    fx = fx if fx is not None else HD.active_fixes()
    return fx.hybrid_k


def future_seed(seed, w, k, salt="fut"):
    """An integer seed for future k from week w. salt "fut" for the K futures a choice uses; "held" for the held-out audit's."""
    return zlib.crc32(f"{salt}|{seed}|{w}|{k}".encode()) % 1_000_000


# ---- the yardstick ---------------------------------------------------------------------------------------------------------------

def weight(persona, fx=None):
    """The member's suffering weight under FixConfig.hybrid_w (Amendment 3), or None (the yardstick is pleasure only). "persona": H39's
    draw (makers.suffering_weight: w = exp(z), z ~ N(0, 0.6), clipped to [0, 4]); a number: every persona that weight. A taste, not a
    misforecast: the held-out audit keeps it."""
    fx = fx if fx is not None else HD.active_fixes()
    mode = getattr(fx, "hybrid_w", None) if fx is not None else None
    if mode is None:
        return None
    if mode == "persona":
        from . import makers as _MK
        return 1.0 if persona is None else _MK.suffering_weight(persona)
    return float(mode)


def score(outcomes, role, persona=None, fx=None):
    """The declared yardstick: the member's mean weekly pleasure (the row's pleasure, on the scale in force), minus w x suffering (both
    kinds) when FixConfig.hybrid_w sets a weight (Amendment 3), over the persona's own horizon if it sets one, discounted per week if it
    sets a discount."""
    t = traits(persona) if (persona is not None and not _NEUTRAL[0]) else {"horizon": None, "discount": 1.0}
    wt = weight(persona, fx)
    if wt is None:
        xs = [o["hedonic"][role]["pleasure"] for o in outcomes]
    else:
        xs = [o["hedonic"][role]["pleasure"] - wt * (o["hedonic"][role]["s_off"] + o["hedonic"][role]["s_non"]) for o in outcomes]
    if t["horizon"]:
        xs = xs[:max(1, int(t["horizon"]))]
    d = t["discount"]
    if d == 1.0:
        return sum(xs) / len(xs)
    ws = [d ** i for i in range(len(xs))]
    return sum(w * x for w, x in zip(ws, xs)) / sum(ws)


# ---- sampled futures -------------------------------------------------------------------------------------------------------------

def copy_world(world):
    """A copy without the run log, hook or week-start snapshot (a forecast reads only the weeks it plays)."""
    from .worlds import household as H
    hook, run, snap = world.hook, world.run, getattr(world, "_wk_snap", None)
    world.hook, world.run, world._wk_snap = None, H.Run(), None
    try:
        c = copy.deepcopy(world)
    finally:
        world.hook, world.run, world._wk_snap = hook, run, snap
    c.fork_ok = False
    c._hyb_fut = True             # a forecast, not a lived world: no readings run inside it (Amendment 3)
    return c


def resample(c, w, fs, weeks):
    """Fresh futures from week w on: a new shock schedule (and bond shocks, if on) and new random streams, all from seed fs."""
    from .worlds import household as H
    pa, pb = c.personas["A"], c.personas["B"]
    c.shocks = {w + t: v for t, v in H.shock_schedule(fs, pa.id, pb.id, weeks).items()}
    lv = getattr(c, "lv", None)
    if lv and lv.network and getattr(c, "bshock", None):
        c.bshock = {w + t: v for t, v in H.bond_shock_schedule(fs, pa.id, pb.id, weeks, lv.bond_shock_rate, lv.bond_shock_dur).items()}
    for q in "ABC":
        c.agents[q].rng = random.Random(f"fut|{fs}|{q}")
    if hasattr(c, "pair_rng"):
        c.pair_rng = random.Random(f"fut|{fs}|pair")


def play_future(world, w, last, weeks, fs, fx=None, edit=None, ref=None):
    """ref (Amendment 4, hybrid_exit): the anchors of in-future readings, every REVIEW_EVERY weeks of the future; None: nobody leaves by
    a reading inside the future (the old rule)."""
    c = copy_world(world)
    if fx is not None:
        c.fx = fx
    if edit is not None:
        edit(c)
    resample(c, w, fs, weeks)
    lt = last
    every = _every() if ref else 0
    if every and leave_on(c.fx):
        fut_start(c, w, ref)
    for x in range(w, w + weeks):
        if every and x > w and fut_due(c, x, w, every):
            future_reading(c, ref, x)
        lt = {"busy": c.step_week(x, lt)}
    STATS["future_exits"] = STATS.get("future_exits", 0) + len(c.exit_log)
    STATS["futures"] += 1
    STATS["future_weeks"] += weeks
    return c


def forecast(world, w, last, weeks, fx=None, edit=None, salt="fut", n=None):
    """See _forecast. Held-out values (salt "held") are scored on the neutral yardstick: no persona forecast trait."""
    prev = _NEUTRAL[0]
    _NEUTRAL[0] = prev or salt == "held"
    try:
        return _forecast(world, w, last, weeks, fx, edit, salt, n)
    finally:
        _NEUTRAL[0] = prev


def _forecast(world, w, last, weeks, fx=None, edit=None, salt="fut", n=None):
    """-> {role: mean over n sampled futures of the yardstick}. edit: a function applied to each copy before it plays (an option)."""
    n = n or k_of(fx or world.fx)
    ref = exit_ref_for(world, fx or world.fx)
    acc = {"A": 0.0, "B": 0.0}
    for k in range(n):
        c = play_future(world, w, last, weeks, future_seed(world.seed, w, k, salt), fx, edit, ref)
        if _FLOG[0] is not None:
            _FLOG[0].append([e["week"] - w for e in c.exit_log if e["week"] >= w])
        for r in "AB":
            acc[r] += score(c.run.outcomes, r, world.personas[r], c.fx)
    return {r: v / n for r, v in acc.items()}


def forward_values(world, w, last, weeks, fx=None):
    """The status quo of the live household (negotiation.forward_values under the hybrid). Memoized inside negotiation.forward_memo."""
    from . import negotiation as NG
    use = world.fx if fx is None else fx
    key = None
    if NG._FWD is not None:
        key = (id(world), w, weeks, repr(use), repr(last)) + ((repr(_REF[0]),) if _REF[0] is not None else ())
        if key in _MEMO:
            return dict(_MEMO[key])
    if EXIT_LOG is not None and use is world.fx and all(world.p[r]["in"] for r in "AB") and _FLOG[0] is None:
        _FLOG[0] = []
        try:
            v = forecast(world, w, last, weeks, fx)
            EXIT_LOG.append({"w": w, "exits": _FLOG[0]})
        finally:
            _FLOG[0] = None
    else:
        v = forecast(world, w, last, weeks, fx)
    if key is not None:
        _MEMO[key] = dict(v)
    return v


def outside_value(p, role, holdings, seed, hed=None, cx=None, weeks=None, salt="fut", n=None):
    """See _outside_value. Held-out values (salt "held") are scored on the neutral yardstick: no persona forecast trait."""
    prev = _NEUTRAL[0]
    _NEUTRAL[0] = prev or salt == "held"
    try:
        return _outside_value(p, role, holdings, seed, hed, cx, weeks, salt, n)
    finally:
        _NEUTRAL[0] = prev


def _outside_value(p, role, holdings, seed, hed=None, cx=None, weeks=None, salt="fut", n=None):
    """The member's outside option under the hybrid: for each of alone and with Friend C, the mean over n fresh futures (alone_value's
    own rollout, seeded per future); the better of the two; plus the persona's outside-option bias.
    Amendment 5, for a member in the household of the lived choice being valued (outside_ctx): under hybrid_outside="lived" the value
    is the lived world played on with the member gone (lived_outside; the arrangement still ranked by the rollouts above); else, under
    an exit cost, the rollout value minus the cost's anticipation (antic). Under leave_bias, minus the bias (not in held-out values)."""
    from . import negotiation as NG
    n = n or k_of()
    kw = {"weeks": weeks} if weeks else {}
    d = {}
    for m in ("alone", "friend"):
        d[m] = sum(NG.alone_value(p, role, holdings, future_seed(seed, int(holdings), k, salt + "|out"), m, hed, cx=cx, **kw)
                   for k in range(n)) / n
    v = max(d.values())
    ctx = _OCTX[0]
    fx = HD.active_fixes()
    if ctx is not None and fx is not None and ctx[0].p[role]["in"] and (leave_on(fx) or fx.hybrid_outside != "solo" or fx.leave_bias):
        world, w, last = ctx
        if fx.hybrid_outside == "lived":
            from . import pairing as PR
            v = lived_outside(world, role, holdings, w, last, NG.apart_mode(d), fx, weeks or NG.decide_weeks(NG.OUT_WEEKS), salt, n) \
                + PR.exit_anticipation(types.SimpleNamespace(fx=fx))      # callers subtract the stigma; the lived futures already pay it
        else:
            v -= antic(world, role, fx)
        if not _NEUTRAL[0]:
            v -= fx.leave_bias
    return v + (0.0 if _NEUTRAL[0] else traits(p)["outside_bias"]), d


def fresh_value(make_world, seed, weeks, salt="fut", n=None):
    """See _fresh_value. Held-out values (salt "held") are scored on the neutral yardstick: no persona forecast trait."""
    prev = _NEUTRAL[0]
    _NEUTRAL[0] = prev or salt == "held"
    try:
        return _fresh_value(make_world, seed, weeks, salt, n)
    finally:
        _NEUTRAL[0] = prev


def _fresh_value(make_world, seed, weeks, salt="fut", n=None):
    """A world built from scratch (week 0) and played over n fresh futures: the formation-time status quo. -> {role: value}."""
    n = n or k_of()
    acc = {"A": 0.0, "B": 0.0}
    for k in range(n):
        c = make_world()
        c.fork_ok = False
        c._hyb_fut = True
        resample(c, 0, future_seed(seed, 0, k, salt), weeks)
        ref = _REF[0] if exit_on(c.fx) else None
        every = _every() if ref else 0
        if every and leave_on(c.fx):
            fut_start(c, 0, ref)
        lt = {"busy": {"A": False, "B": False}}
        for x in range(weeks):
            if every and x > 0 and fut_due(c, x, 0, every):
                future_reading(c, ref, x)
            lt = {"busy": c.step_week(x, lt)}
        STATS["future_exits"] = STATS.get("future_exits", 0) + len(c.exit_log)
        STATS["futures"] += 1
        STATS["future_weeks"] += weeks
        for r in "AB":
            acc[r] += score(c.run.outcomes, r, c.personas[r], c.fx)
    return {r: v / n for r, v in acc.items()}


# ---- the held-out audit (pass test HB, docs/results/hybrid-agent-prereg.md) -----------------------------------------------------

def audit_choice(kind, w, pair, options, chosen):
    """options: {name: {"F": {role: v}, "R": {role: v}}}."""
    if AUDIT is not None:
        AUDIT.append({"kind": kind, "w": w, "pair": pair, "options": options, "chosen": chosen})


# ---- bills as a household agreement --------------------------------------------------------------------------------------------

def shares(term):
    from .worlds import household as H
    if TERMS[term] is not None:
        return dict(TERMS[term])
    z = H.V2_INCOME["A"] + H.V2_INCOME["B"]
    return {r: H.V2_INCOME[r] / z for r in "AB"}


def owed(world, r, need):
    """What member r owes this month under the agreement, net of what it already paid by action (shares over the members who are in)."""
    from .worlds import household as H
    ag = getattr(world, "agree", None)
    if not ag or not world.p[r]["in"]:
        return 0.0
    inn = [x for x in "AB" if world.p[x]["in"]]
    z = sum(ag["share"][x] for x in inn)
    return max(0.0, ag["share"][r] / z * need - H.SHARE_STEP * world.contrib_month[r])


def pay_agreed(world, w):
    """At settlement, before the bill is checked: each member in pays what it owes, up to its money and the unfunded rest (a standing
    transfer; kept as a commitment, no action unit)."""
    need = world.need_month()
    for r in "AB":
        left = need - world.funded
        if left <= 0:
            break
        x = min(owed(world, r, need), max(0.0, float(world.p[r]["money"])), left)
        if x > 0:
            world.p[r]["money"] -= x
            world.funded += x
            world.money_in[r] += x
            world.wk[r]["agreed_paid"] = world.wk[r].get("agreed_paid", 0.0) + x


def choose_term(values, outside):
    """values: {option: {role: v}} (the bill terms, and under H41 "lat" or prenup combinations); outside: {role: v}. The household's
    option: the one whose worse-off member gains most over the outside option (ties: income first, then the order given). -> (option,
    formed)."""
    best = max(values, key=lambda t: (min(values[t][r] - outside[r] for r in "AB"), t == "income"))
    return best, all(values[best][r] > outside[r] for r in "AB")


def set_agreement(world, term):
    """term: a bill term ("income", "equal"), or "income|forfeit"-style with an H41 prenup exit term after the bar."""
    bill, _, exit_term = term.partition("|")
    world.agree = {"term": bill, "share": shares(bill)}
    if exit_term:
        world.prenup_exit = exit_term


# ---- H41 choice aids (docs/results/h41-choice-aids-prereg.md) ----------------------------------------------------------------------

PRENUP_TERMS = ("equal_split", "proportional", "forfeit")      # exit fallback F5's terms; equal split first (F5's own default)


def prenup_on():
    from . import exit_fallback as EF
    return EF.ACTIVE == "F5"


def window(fx=None, default=None):
    """The window a formation is scored over: the trial's length under FixConfig.h41_trial, else the decision window."""
    from . import negotiation as NG
    fx = fx if fx is not None else HD.active_fixes()
    t = getattr(fx, "h41_trial", 0) if fx is not None else 0
    return t if t else NG.decide_weeks(NG.FORWARD_WEEKS if default is None else default)


def _lat_on(fx=None):
    fx = fx if fx is not None else HD.active_fixes()
    return bool(getattr(fx, "h41_lat", False)) if fx is not None else False


def make_lat(world, modes):
    """An apart world becomes living apart together: both out, no pot, each in its own apart mode, time together allowed."""
    for r in "AB":
        world.p[r]["in"] = False
    world.solo = dict(modes)
    world.lat = True


def score_options(value_of, terms):
    """value_of(term) -> {role: v}. Under a prenup (exit fallback F5) the exit term is chosen with the bill term: every bill term is
    scored with every F5 exit term. The term reaches a forecast even when nobody leaves in it, through the weekly freedom probe (what a
    member could carry out sets its exit_retained, which feeds autonomy). -> {option: values}."""
    if not prenup_on():
        return {t: value_of(t) for t in terms}
    out = {}
    for t in terms:
        if t == "lat":
            out[t] = value_of(t)
            continue
        for e in PRENUP_TERMS:
            out[f"{t}|{e}"] = value_of(f"{t}|{e}")
    return out


def trial_reading(lived, w, last):
    """The end of a trial household (FixConfig.h41_trial): each member stays only if staying (the status quo over K futures, the
    decision window, minus the trust penalty) beats its outside option at the carry, at this one reading, with no margin. A member who
    does not leaves now, by the world's own leave (its pot and items settle as the exit rule says)."""
    from . import negotiation as NG
    world = lived.world
    STATS["choices"] += 1
    world.trial_end = None
    weeks = NG.decide_weeks(NG.FORWARD_WEEKS)
    Os = {}
    with outside_ctx(world, w, last):
        if exit_on(world.fx):              # Amendment 4: the outside options first; they anchor the forecast's in-future readings
            for r in "AB":
                carry = world.p[r]["money"] + world.carry_out(r, 50)
                Os[r] = outside_value(world.personas[r], r, carry, world.seed, world.hed[r], cx=NG._cx(world, r),
                                      weeks=NG.decide_weeks(0) or None)
            with exit_ref({r: ref_entry(world, r, Os[r][0] - NG._PAIR.exit_anticipation(world), NG.apart_mode(Os[r][1]))
                           for r in "AB"}):
                sq = forecast(world, w, last, weeks)
        else:
            sq = forecast(world, w, last, weeks)
        out = []
        tref = {}
        for r in "AB":
            carry = world.p[r]["money"] + world.carry_out(r, 50)
            O, d = Os[r] if r in Os else outside_value(world.personas[r], r, carry, world.seed, world.hed[r], cx=NG._cx(world, r),
                                                       weeks=NG.decide_weeks(0) or None)
            O -= NG._PAIR.exit_anticipation(world)
            tref[r] = O
            if O > sq[r] - NG.trust_penalty(world.trust[r]):
                out.append((r, NG.apart_mode(d)))
    set_tally_ref(world, tref)
    lived.trials.append({"week": w, "left": [r for r, _ in out]})
    for r, mode in out:
        if world.p[r]["in"]:
            world.apply(r, {"a": "leave", "take": 50, "why": "trial"}, w, [])
            solo = dict(world.solo) if isinstance(world.solo, dict) else {x: world.solo for x in "AB"}
            solo[r] = mode
            world.solo = solo


# ---- formation, retries, readings, returns --------------------------------------------------------------------------------------

def _o_both(personas, holdings, seed, heds=None, cxs=None, salt="fut", n=None, weeks=None):
    from . import negotiation as NG
    O, det = {}, {}
    for r in "AB":
        O[r], det[r] = outside_value(personas[r], r, holdings[r], seed, (heds or {}).get(r), (cxs or {}).get(r),
                                     weeks=weeks or NG.decide_weeks(0) or None, salt=salt, n=n)
    return O, det


def formation0(lived):
    """Week 0 under the hybrid: score the household under each bill term (and, under H41, living apart together and the prenup's exit
    terms) and each member's outside option on K fresh futures; form under the chosen option iff both gain (decline=True), or always
    (decline=False). -> (formed, term, O, det, V)."""
    from . import negotiation as NG
    from .worlds import household as H
    STATS["choices"] += 1
    fx = HD.active_fixes()
    weeks = window(fx, NG.OUT_WEEKS)
    trial = bool(getattr(fx, "h41_trial", 0))
    ps = {"A": lived.pa, "B": lived.pb}
    hold = NG.START_HOLDINGS[0] + NG.START_HOLDINGS[1]
    O, det = _o_both(ps, {"A": hold, "B": hold}, lived.seed, weeks=weeks if trial else None)
    modes = {r: NG.apart_mode(det[r]) for r in "AB"}

    def mk(term):
        def make():
            if term == "lat":
                wd = H.WeeklyWorld(list(lived.cards), (lived.pa, lived.pb), lived.seed, max(weeks, 1), deal={"pot": False, "commits": []})
                make_lat(wd, modes)
                return wd
            wd = H.WeeklyWorld(list(lived.cards), (lived.pa, lived.pb), lived.seed, max(weeks, 1))
            set_agreement(wd, term)
            return wd
        return make

    terms = tuple(TERMS) + (("lat",) if _lat_on(fx) else ())

    def vals(salt, n=None):
        return score_options(lambda t: fresh_value(mk(t), lived.seed, weeks, salt, n), terms)

    with exit_ref({r: (O[r], modes[r]) for r in "AB"}):          # read only under hybrid_exit (Amendment 4)
        V = vals("fut")
        term, formed = choose_term(V, O)
        if AUDIT is not None:
            Vh = {t: fresh_value(mk(t), lived.seed, weeks, "held", AUDIT_M) for t in V}
            Oh, _ = _o_both(ps, {"A": hold, "B": hold}, lived.seed, salt="held", n=AUDIT_M, weeks=weeks if trial else None)
            opts = {t: {"F": V[t], "R": Vh[t]} for t in V}
            opts["outside"] = {"F": O, "R": Oh}
            audit_choice("formation0", 0, (lived.pa.id, lived.pb.id), opts, (term if formed else "outside"))
    if not lived.decline:
        formed = True
        if term == "lat":                      # forced formation means a household: the best household option
            term = max((t for t in V if t != "lat"), key=lambda t: min(V[t][r] - O[r] for r in "AB"))
    return formed, term, O, det, V


def retry(lived, w, last):
    """A 13-week retry of a pair living apart: the household under each term (a copy formed now), and under H41 living apart together,
    against each member's outside option."""
    from . import negotiation as NG
    world = lived.world
    STATS["choices"] += 1
    fx = world.fx
    weeks = window(fx)
    trial = bool(getattr(fx, "h41_trial", 0))
    O, modes, det = {}, {}, {}
    for r, p in zip("AB", (lived.pa, lived.pb)):
        O[r], d = outside_value(p, r, world.p[r]["money"], lived.seed, world.hed[r], cx=NG._cx(world, r),
                                weeks=(weeks if trial else NG.decide_weeks(0)) or None)
        modes[r], det[r] = NG.apart_mode(d), d
    hyp = copy_world(world)
    hyp.lat = False
    NG._form_baseline(hyp, w)

    def value_of(t, salt="fut", n=None):
        if t == "lat":
            lat = copy_world(world)
            make_lat(lat, modes)
            return forecast(lat, w, last, weeks, salt=salt, n=n)
        return forecast(hyp, w, last, weeks, edit=lambda c, t=t: set_agreement(c, t), salt=salt, n=n)

    terms = tuple(TERMS) + (("lat",) if _lat_on(fx) else ())
    with exit_ref({r: (O[r], modes[r]) for r in "AB"}):          # read only under hybrid_exit (Amendment 4)
        V = score_options(value_of, terms)
        term, formed = choose_term(V, O)
        if AUDIT is not None:
            Vh = {t: value_of(t, "held", AUDIT_M) for t in V}
            Oh = {r: outside_value(p, r, world.p[r]["money"], lived.seed, world.hed[r], cx=NG._cx(world, r),
                                   weeks=(weeks if trial else NG.decide_weeks(0)) or None, salt="held", n=AUDIT_M)[0]
                  for r, p in zip("AB", (lived.pa, lived.pb))}
            opts = {t: {"F": V[t], "R": Vh[t]} for t in V}
            opts["outside"] = {"F": O, "R": Oh}
            audit_choice("retry", w, (lived.pa.id, lived.pb.id), opts, term if formed else "outside")
    lived.retries.append({"week": w, "formed": formed, "outside": dict(O), "baseline": dict(V[term]), "term": term})
    if formed and term == "lat":
        make_lat(world, modes)
    elif formed:
        world.lat = False
        NG._form_baseline(world, w)
        set_agreement(world, term)
        set_tally_ref(world, O)
        lived.apart = False
        if trial:
            world.trial_end = w + fx.h41_trial
        if world.fx:
            for r in "AB":
                world.events.append((w, r, "formed"))
    else:
        world.lat = False
        world.solo = modes


def reading_audit(world, w, last, sq, O, carry, weeks):
    """Held-out values of a reading's two options (stay, the outside option) for the audit."""
    from . import negotiation as NG
    if AUDIT is None:
        return
    R = forecast(world, w, last, weeks, salt="held", n=AUDIT_M)
    Oh = {r: outside_value(world.personas[r], r, carry[r], world.seed, world.hed[r], cx=NG._cx(world, r),
                           weeks=NG.decide_weeks(0) or None, salt="held", n=AUDIT_M)[0] for r in "AB"}
    chosen = {r: ("outside" if O[r] > sq[r] else "stay") for r in "AB"}
    audit_choice("reading", w, (world.personas["A"].id, world.personas["B"].id),
                 {"stay": {"F": sq, "R": R}, "outside": {"F": O, "R": Oh}}, chosen)


def leave_value(world, r):
    """Leaving, on the routine's scale: the simulated gain per week (outside option minus staying, at the last reading) times the horizon."""
    from . import negotiation as NG
    g = getattr(world, "bar_gain", {}).get(r, 0.0)
    return max(0.0, g) * NG.decide_weeks(NG.FORWARD_WEEKS)


def return_reading(lived, w, last):
    """One member out, the other in: is a return worth it to both? Scored on K futures each way; sets world.ret_value."""
    from . import negotiation as NG
    world = lived.world
    out = [r for r in "AB" if not world.p[r]["in"]]
    if len(out) != 1:
        return
    r = out[0]
    STATS["choices"] += 1
    weeks = NG.decide_weeks(NG.FORWARD_WEEKS)

    def back(c):
        c.p[r]["in"], c.p[r]["months_in"] = True, 0
        if isinstance(c.solo, dict):
            c.solo = None

    with exit_ref(default_ref(world, world.fx, "AB") if exit_on(world.fx) else None):   # Amendment 4: either member may leave later
        sq = forecast(world, w, last, weeks)
        rv = forecast(world, w, last, weeks, edit=back)
        gain = {x: rv[x] - sq[x] for x in "AB"}
        world.ret_value = {r: (gain[r] * weeks if all(g > 0 for g in gain.values()) else 0.0)}
        if AUDIT is not None:
            audit_choice("return", w, (world.personas["A"].id, world.personas["B"].id),
                         {"stay_out": {"F": sq, "R": forecast(world, w, last, weeks, salt="held", n=AUDIT_M)},
                          "return": {"F": rv, "R": forecast(world, w, last, weeks, edit=back, salt="held", n=AUDIT_M)}},
                         "return" if world.ret_value[r] > 0 else "stay_out")
    if lone_on(world.fx):
        lone_reading(lived, w, last)         # Amendment 4: the member left in holds its own reading at the same mark


def due(world, w):
    """An early reading is due: a member in distress flagged it, both are in, and the last reading is at least hybrid_gap weeks back."""
    fx = world.fx
    return ((bool(getattr(world, "hyb_due", False)) or tally_flag(world)) and all(world.p[x]["in"] for x in "AB")
            and w - getattr(world, "hyb_last", -99) >= fx.hybrid_gap)


# ---- Amendment 4: the member left alone, and forecasts with the option to leave (docs/results/hybrid-exit-option-prereg.md) ----------

def lone_on(fx=None):
    """FixConfig.hybrid_lone: a member alone in the household holds the pair reading, and an emptied household may re-form."""
    fx = fx if fx is not None else HD.active_fixes()
    return bool(getattr(fx, "hybrid_lone", False)) if fx is not None else False


def exit_on(fx=None):
    """FixConfig.hybrid_exit: forecast futures hold in-future readings, so future selves may leave (the option value of exit)."""
    fx = fx if fx is not None else HD.active_fixes()
    return bool(getattr(fx, "hybrid_exit", False)) if fx is not None else False


def _every():
    from . import negotiation as NG
    return NG.REVIEW_EVERY


def _lone(world):
    ins = [r for r in "AB" if world.p[r]["in"]]
    return ins[0] if len(ins) == 1 else None


def lone_due(world, w):
    """An early lone reading is due: hybrid_lone, exactly one member in, it flagged distress, and the last reading is hybrid_gap back."""
    fx = world.fx
    return (lone_on(fx) and _lone(world) is not None and (bool(getattr(world, "hyb_due", False)) or tally_flag(world, _lone(world)))
            and w - getattr(world, "hyb_last", -99) >= fx.hybrid_gap)


def bar_one(world, r, s, O, mode):
    """The bar rule of negotiation.bar_reading for one member: s its stay value (minus the trust penalty), O its outside option."""
    fx = world.fx
    runs = getattr(world, "bar_runs", None)
    if runs is None:
        runs = world.bar_runs = {"A": 0, "B": 0}
    gain = dict(getattr(world, "bar_gain", None) or {})
    gain[r] = O - s
    world.bar_gain = gain
    runs[r] = runs[r] + 1 if O > s + fx.leave_margin else 0
    world.bar_out[r] = runs[r] >= fx.bar_runs
    if mode:
        world.bar_mode[r] = mode
    world.bar_log = getattr(world, "bar_log", [])
    world.bar_log.append({"role": r, "sq": s, "out": O, "bar_out": world.bar_out[r]})


def lone_reading(lived, w, last):
    """Fix 1 (hybrid_lone): the member alone in the household holds the pair reading's arithmetic. Staying: the status quo over K futures
    over the decision window, minus the trust penalty; the outside option at the carry, minus exit anticipation; the bar in force."""
    from . import negotiation as NG
    world = lived.world
    r = _lone(world)
    if r is None or not lone_on(world.fx) or not world.fx.bar_leave or not lived_world(world):
        return
    STATS["choices"] += 1
    STATS["lone_readings"] = STATS.get("lone_readings", 0) + 1
    weeks = NG.decide_weeks(NG.FORWARD_WEEKS)
    carry = world.p[r]["money"] + world.carry_out(r, 50)
    with outside_ctx(world, w, last):
        O, d = NG.outside_value(world.personas[r], r, carry, world.seed, world.hed[r], cx=NG._cx(world, r))
    O -= NG._PAIR.exit_anticipation(world)
    mode = NG.apart_mode(d)
    tp = NG.trust_penalty(world.trust[r])
    with exit_ref({r: ref_entry(world, r, O, mode)}):
        sq = forecast(world, w, last, weeks)
        s = sq[r] - tp
        if AUDIT is not None:
            Rs = forecast(world, w, last, weeks, salt="held", n=AUDIT_M)[r] - tp
            with outside_ctx(world, w, last):
                Oh = outside_value(world.personas[r], r, carry, world.seed, world.hed[r], cx=NG._cx(world, r),
                                   weeks=NG.decide_weeks(0) or None, salt="held", n=AUDIT_M)[0] - NG._PAIR.exit_anticipation(world)
            audit_choice("lone", w, (world.personas["A"].id, world.personas["B"].id),
                         {"stay": {"F": {r: s}, "R": {r: Rs}}, "outside": {"F": {r: O}, "R": {r: Oh}}},
                         {r: ("outside" if O > s else "stay")})
            AUDIT[-1]["roles"] = r
    world.hyb_last, world.hyb_due = w, False
    set_tally_ref(world, {r: O})
    bar_one(world, r, s, O, mode)
    world.lone_log = getattr(world, "lone_log", [])
    world.lone_log.append({"week": w, "role": r, "stay": round(s, 5), "out": round(O, 5), "bar_out": bool(world.bar_out[r])})


def lone_apart(lived):
    """Fix 1: once the household is empty (and the pair is not living apart together), the pair counts as apart, so the harness's
    13-week retry runs for it."""
    world = lived.world
    if lone_on(world.fx) and not lived.apart and not any(world.p[r]["in"] for r in "AB") and not getattr(world, "lat", False):
        lived.apart = True
        STATS["lone_apart"] = STATS.get("lone_apart", 0) + 1


@contextmanager
def exit_ref(ref):
    """The anchors a choice gives its forecasts' in-future readings (read only under hybrid_exit)."""
    prev = _REF[0]
    _REF[0] = ref
    try:
        yield
    finally:
        _REF[0] = prev


def default_ref(world, fx, roles=None):
    """The anchors of a forecast no choice set: each member's outside option as a reading values it (members in: at the carry, money
    plus the 50% take; members out: at their money), minus exit anticipation, with its apart mode. Valued under fx."""
    from . import negotiation as NG
    from . import pairing as PR
    ref = {}
    ctx = _OCTX[0] if (_OCTX[0] is not None and _OCTX[0][0] is world) else (world, len(world.run.outcomes),
                                                                             {"busy": {"A": False, "B": False}})
    with HD.use_fixes(fx), outside_ctx(*ctx):
        ea = PR.exit_anticipation(types.SimpleNamespace(fx=fx))
        for r in (roles or [x for x in "AB" if world.p[x]["in"]]):
            hold = world.p[r]["money"] + (world.carry_out(r, 50) if world.p[r]["in"] else 0)
            O, d = NG.outside_value(world.personas[r], r, hold, world.seed, world.hed[r], cx=NG._cx(world, r))
            ref[r] = ref_entry(world, r, O - ea, NG.apart_mode(d), fx)
    return ref


def exit_ref_for(world, fx):
    """The anchors a forecast of `world` uses: None without hybrid_exit; else the choice's own (exit_ref), or default_ref."""
    if not exit_on(fx):
        return None
    if _REF[0] is not None:
        return _REF[0]
    return default_ref(world, fx)


def future_reading(c, ref, x=None):
    """Fix 2 (hybrid_exit): an in-future reading inside a forecast copy. Each member in (a lone member only under hybrid_lone) compares
    its yardstick over the REVIEW_EVERY future weeks just played (no horizon or discount trait), minus the trust penalty, with its
    anchored outside option, on the lived bar. Past the bar, the routine may leave as in a lived world."""
    from . import negotiation as NG
    fx = c.fx
    ins = [r for r in "AB" if c.p[r]["in"]]
    if not ins or (len(ins) == 1 and not lone_on(fx)):
        return
    rows = c.run.outcomes[-_every():]
    if not rows:
        return
    STATS["future_readings"] = STATS.get("future_readings", 0) + 1
    if leave_on(fx):
        c.hyb_due, c._fut_last = False, x
    for r in ins:
        if r not in ref:
            continue
        wt = weight(c.personas[r], fx)
        h = [o["hedonic"][r] for o in rows]
        ys = [y["pleasure"] - (wt * (y["s_off"] + y["s_non"]) if wt is not None else 0.0) for y in h]
        O, mode = ref[r][0], ref[r][1]
        if leave_on(fx):                   # Amendment 5: the exit cost as it stands at this future week, not at the choice
            O += (ref[r][2] if len(ref[r]) > 2 else 0.0) - antic(c, r, fx)
        bar_one(c, r, sum(ys) / len(ys) - NG.trust_penalty(c.trust[r]), O, mode)


# ---- Amendment 5: how the hybrid decides to leave (docs/results/hybrid-leaving-prereg.md) ------------------------------------------

def tally_on(fx=None):
    """FixConfig.hybrid_tally: a fading running tally calls readings (None: off)."""
    fx = fx if fx is not None else HD.active_fixes()
    return fx is not None and getattr(fx, "hybrid_tally", None) is not None


def xcost_on(fx=None):
    """FixConfig.exit_fixed / exit_grow: leaving costs weekly pleasure for exit_cost_weeks after it."""
    fx = fx if fx is not None else HD.active_fixes()
    return fx is not None and bool(getattr(fx, "exit_fixed", 0.0) or getattr(fx, "exit_grow", 0.0))


def leave_on(fx=None):
    """Any Amendment 5 world rule (the tally or the exit cost) is on: the world keeps weeks in, tallies and exit costs."""
    return tally_on(fx) or xcost_on(fx)


def exit_size(world, r, fx=None):
    """The weekly cost member r would pay if it left now: exit_fixed + exit_grow x (weeks in this household spell) / 52."""
    fx = fx if fx is not None else world.fx
    if not xcost_on(fx):
        return 0.0
    n = (getattr(world, "wks_in", None) or {}).get(r, 0)
    return fx.exit_fixed + fx.exit_grow * n / 52.0


def antic(world, r, fx=None):
    """The exit cost as a mean weekly cost over the outside window (as pressure's exit stigma is anticipated): 0 for a member out."""
    from . import negotiation as NG
    fx = fx if fx is not None else world.fx
    if not xcost_on(fx) or not world.p[r]["in"]:
        return 0.0
    n = NG.decide_weeks(NG.OUT_WEEKS)
    return exit_size(world, r, fx) * min(fx.exit_cost_weeks, n) / n


def ref_entry(world, r, O, mode, fx=None):
    """An in-future anchor: (outside value, apart mode, the exit-cost anticipation the value already includes)."""
    fx = fx if fx is not None else world.fx
    return (O, mode, antic(world, r, fx)) if xcost_on(fx) else (O, mode)


def on_leave(world, r, w):
    """Called when r leaves a household (exit cost on): the cost it pays from this week, sized at its weeks in."""
    world.xcost = dict(getattr(world, "xcost", None) or {})
    world.xcost[r] = (w, exit_size(world, r))


def exit_cost_now(world, r, w):
    """The exit cost member r pays this week (0 unless it left within exit_cost_weeks and is still out)."""
    x = (getattr(world, "xcost", None) or {}).get(r)
    if x is None or world.p[r]["in"]:
        return 0.0
    return x[1] if 0 <= w - x[0] < world.fx.exit_cost_weeks else 0.0


@contextmanager
def outside_ctx(world, w, last):
    """The lived choice whose members' outside options are being valued (read by _outside_value only under Amendment 5 flags)."""
    prev = _OCTX[0]
    _OCTX[0] = (world, w, last)
    try:
        yield
    finally:
        _OCTX[0] = prev


def lived_outside(world, r, holdings, w, last, mode, fx, weeks, salt="fut", n=None):
    """hybrid_outside="lived": member r's outside option as the lived world played on over n futures (the status quo's own seeds)
    with r leaving now (take 50, as a reading assumes), its money set to the holdings the caller values, living in `mode`. No in-future
    readings inside these futures. Memoized inside negotiation.forward_memo."""
    from . import negotiation as NG
    key = None
    if NG._FWD is not None:
        key = ("out", id(world), w, r, round(float(holdings), 6), mode, weeks, repr(fx), salt, n, _NEUTRAL[0])
        if key in _MEMO:
            return _MEMO[key]

    def gone(c):
        if r not in c.wk:                      # a world that has not played a week yet (week 0): the week's books are not open
            c.wk = {x: {"sanctioned": 0} for x in "AB"}
            c.units = {x: 99 for x in "AB"}
        c.bar_mode[r] = mode
        c.apply(r, {"a": "leave", "take": 50, "why": "bar"}, w, [])
        c.p[r]["money"] = holdings
        solo = dict(c.solo) if isinstance(c.solo, dict) else {x: c.solo for x in "AB"}
        solo[r] = mode
        c.solo = solo

    with exit_ref({}):
        prev, flog = _OCTX[0], _FLOG[0]
        _OCTX[0] = _FLOG[0] = None             # not a choice's status quo: its forced exit is not logged as a forecast exit
        try:
            v = forecast(world, w, last, weeks, fx=fx, edit=gone, salt=salt, n=n)[r]
        finally:
            _OCTX[0], _FLOG[0] = prev, flog
    STATS["lived_outside"] = STATS.get("lived_outside", 0) + 1
    if key is not None:
        _MEMO[key] = v
    return v


def set_tally_ref(world, O):
    """The outside option each member's tally compares against, as last valued (formation, retry, reading)."""
    if not tally_on(world.fx):
        return
    world.tally_ref = {**(getattr(world, "tally_ref", None) or {}), **{r: float(v) for r, v in O.items()}}


def _yard(row, r, persona, fx):
    h = row["hedonic"][r]
    wt = weight(persona, fx)
    return h["pleasure"] - (wt * (h["s_off"] + h["s_non"]) if wt is not None else 0.0)


def tally_trig(fx, hist):
    """Does a tally history (oldest first) trigger a rethink now? level: below -line; slope: fell by more than line over hybrid_gap
    weeks; both: either."""
    if not hist:
        return False
    mode, line = fx.hybrid_tally, fx.tally_line
    lvl = hist[-1] < -line
    slp = len(hist) > fx.hybrid_gap and hist[-1] - hist[-1 - fx.hybrid_gap] < -line
    return lvl if mode == "level" else slp if mode == "slope" else (lvl or slp)


def tally_step(world, row):
    """One week of each member's tally: tau <- a tau + (1 - a)(y - O), a = 2^(-1/tally_half); dropped while out, 0 at a spell's start."""
    fx = world.fx
    a = 0.5 ** (1.0 / fx.tally_half)
    T = world.tally = dict(getattr(world, "tally", None) or {"A": None, "B": None})
    H = world.tally_hist = {r: list(v) for r, v in (getattr(world, "tally_hist", None) or {"A": [], "B": []}).items()}
    ref = getattr(world, "tally_ref", None) or {}
    due = {}
    for r in "AB":
        if not world.p[r]["in"] or r not in ref:
            T[r], H[r], due[r] = None, [], False
            continue
        t = 0.0 if T[r] is None else T[r]
        T[r] = a * t + (1.0 - a) * (_yard(row, r, world.personas[r], fx) - ref[r])
        H[r] = (H[r] + [T[r]])[-(fx.hybrid_gap + 1):]
        due[r] = tally_trig(fx, H[r])
    world.tally_due = due


def tally_flag(world, r=None):
    """A member's tally (or either member's, r None) calls a rethink this week (False unless hybrid_tally)."""
    d = getattr(world, "tally_due", None)
    if not d or not tally_on(world.fx):
        return False
    return bool(d.get(r)) if r is not None else any(d.values())


def note_rethink(world, w):
    """Log a lived reading the tally called (not the distress flag), for the second measures."""
    if tally_flag(world) and not getattr(world, "hyb_due", False):
        world.tally_log = getattr(world, "tally_log", [])
        world.tally_log.append({"week": w, "roles": [r for r in "AB" if world.tally_due.get(r)],
                                "tally": {r: (round(v, 5) if v is not None else None) for r, v in world.tally.items()}})


def week_end(world, w, row):
    """End of a week in a hybrid world under Amendment 5: weeks in the household spell, and the tally."""
    wi = world.wks_in = dict(getattr(world, "wks_in", None) or {"A": 0, "B": 0})
    for r in "AB":
        wi[r] = wi[r] + 1 if world.p[r]["in"] else 0
    if tally_on(world.fx):
        tally_step(world, row)


def fut_start(c, w, ref):
    """A forecast copy starts: its last in-future reading is the choice itself; its tally compares against the choice's anchors."""
    c._fut_last = w
    if tally_on(c.fx):
        c.tally_ref = {**(getattr(c, "tally_ref", None) or {}), **{r: v[0] for r, v in ref.items()}}


def fut_due(c, x, w, every):
    """An in-future reading is due at future week x: a 13-week mark, or (hybrid_tally) a tally rethink or distress flag at least
    hybrid_gap weeks after the last in-future reading, the same rule the lived world follows."""
    if (x - w) % every == 0:
        return True
    if not tally_on(c.fx) or x - getattr(c, "_fut_last", w) < c.fx.hybrid_gap:
        return False
    return bool(getattr(c, "hyb_due", False)) or tally_flag(c)


# ---- the week-0 commitment stub -------------------------------------------------------------------------------------------------

def negotiate(world):
    """Under the hybrid the persona still proposes what personas.commitment_proposal says, but both members accept only if the
    commitment raises each one's yardstick over K futures (52 weeks, the commitments' own length)."""
    from . import personas as PERS
    STATS["choices"] += 1
    weeks = PERS.COMMIT_WEEKS
    last = {"busy": {"A": False, "B": False}}
    for r in "AB":
        q, prop = world.other(r), PERS.commitment_proposal(world.personas[r])
        cands = []
        if prop["stay"] and world._commit_ok(r, "commit_stay") and world._commit_ok(q, "commit_stay") \
                and not any(c["kind"] == "stay" for c in world.commits):
            cands.append([{"kind": "stay", "by": who, "to": world.other(who), "type": None, "from": 0, "until": prop["stay"], "breached": 0}
                          for who in (r, q)])
        if prop["requests"] and world._commit_ok(q, "commit_request"):
            cands.append([{"kind": "requests", "by": q, "to": r, "type": prop["requests"], "from": 0, "until": PERS.COMMIT_WEEKS,
                           "breached": 0}])
        for cs in cands:
            base = forecast(world, 0, last, weeks)
            withc = forecast(world, 0, last, weeks, edit=lambda c, cs=cs: c.commits.extend(dict(x) for x in cs))
            ok = all(withc[x] > base[x] for x in "AB")
            if AUDIT is not None:
                audit_choice("commit", 0, (world.personas["A"].id, world.personas["B"].id),
                             {"without": {"F": base, "R": forecast(world, 0, last, weeks, salt="held", n=AUDIT_M)},
                              "with": {"F": withc, "R": forecast(world, 0, last, weeks, salt="held", n=AUDIT_M,
                                                                  edit=lambda c, cs=cs: c.commits.extend(dict(x) for x in cs))}},
                             "with" if ok else "without")
            if ok:
                world.commits.extend(dict(x) for x in cs)


# ---- fixed scores derived from simulation ---------------------------------------------------------------------------------------

def lived(world):
    """A lived world: not a forecast copy, a fresh formation world or a one-week fork."""
    return not getattr(world, "_hyb_fut", False)


lived_world = lived       # the same test, for functions whose harness argument is called `lived`


def world_readings(world, w, last):
    """Amendment 3 (FixConfig.hybrid_readings="world"): any hybrid reading no harness ran this week. An early reading on distress
    (hybrid.due); and, in a world no harness drives (world.harness unset), the 13-week reading while both are in and the return reading
    while one is out. The arithmetic is the harness's own (negotiation.BaselineLived.reading, return_reading)."""
    import types
    from . import negotiation as NG
    n_in = sum(1 for x in "AB" if world.p[x]["in"])
    mark = bool(w) and w % NG.REVIEW_EVERY == 0 and not getattr(world, "harness", False)
    shim = types.SimpleNamespace(world=world, pa=world.personas["A"], pb=world.personas["B"], seed=world.seed, log=[])
    if n_in == 2 and (mark or due(world, w)):
        STATS["world_readings"] = STATS.get("world_readings", 0) + 1
        if not mark:
            note_rethink(world, w)
        world.cur_reading = w
        NG.BaselineLived.reading(shim, w, last)
    elif n_in == 1 and mark:
        return_reading(shim, w, last)
    elif n_in == 1 and lone_due(world, w):
        STATS["world_readings"] = STATS.get("world_readings", 0) + 1
        note_rethink(world, w)
        lone_reading(shim, w, last)


def week_start(world, w, last):
    """Called at the start of each week of a hybrid world: reset the call counter and, in a lived world, keep a snapshot for forks."""
    if world.fx.hybrid_readings == "world" and lived(world):
        world_readings(world, w, last)
    world._ncall = {"A": 0, "B": 0}
    world._wk_snap = None
    if getattr(world, "fork_ok", False):
        world._fmemo = {}
        from . import valuecheck as VC
        snap = VC.snapshot(world)
        snap.fork_ok = False
        snap._hyb_fut = True
        world._wk_snap, world._wk_last = snap, dict(last)


def _key(c):
    return (c["a"], c.get("kind"), c.get("take", 0))


def rescore(world, r, w, cands):
    """Replace the propose-only scores with values derived from a one-week simulation (lived world), or a memo of them (a replay of
    this week), or drop them (inside a forecast). A score of 99 or more is the value check's forced marker and is left alone."""
    from . import valuecheck as VC
    k = world._ncall[r] - 1
    out = []
    snap = getattr(world, "_wk_snap", None)
    memo = getattr(world, "_fmemo", {})
    idle = None
    for s, c in cands:
        if c["a"] not in FORK_ACTS or s >= 99.0:
            out.append((s, c))
            continue
        mk = (w, r, k, _key(c))
        if mk in memo:
            v = memo[mk]
        elif snap is not None:
            snap._fmemo = dict(memo)
            if idle is None:
                _, idle = VC.branch(snap, world._wk_last, w, r, k, "idle", weeks=1)
            _, rows = VC.branch(snap, world._wk_last, w, r, k, "force", dict(c), weeks=1)
            o = world.other(r)
            pro = world.agents[r].prosocial
            v = (rows[r][0]["net"] - idle[r][0]["net"]) + pro * (rows[o][0]["net"] - idle[o][0]["net"])
            STATS["forks"] += 1
            memo[mk] = v
        else:
            continue
        out.append((v, c))
    world._fmemo = memo
    return sorted(out, key=lambda t: -t[0])
