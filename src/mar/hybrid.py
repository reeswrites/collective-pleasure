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

Not built: project protection (H39 makers) as a simulated choice. A makers world with negotiated protection refuses to run under the hybrid.
"""
from __future__ import annotations

import copy
import random
import zlib

from . import hedonic as HD

TERMS = {"income": None, "equal": {"A": 0.5, "B": 0.5}}       # None: proportional to income (V2_INCOME)
FORK_ACTS = ("request", "refuse_request", "veto", "give", "take_shared")
AUDIT = None          # a list while the held-out audit is on: every big choice also scored on AUDIT_M held-out futures
AUDIT_M = 16
STATS = {"futures": 0, "future_weeks": 0, "forks": 0, "choices": 0}
_NEUTRAL = [False]    # True while held-out values are computed: the declared yardstick, with no persona forecast trait
_MEMO = {}            # forward forecasts within one forward_memo block: (id(world), w, weeks, fx, last) -> values


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

def score(outcomes, role, persona=None):
    """The declared yardstick: the member's mean weekly pleasure (the row's pleasure, on the scale in force), over the persona's own
    horizon if it sets one, discounted per week if it sets a discount."""
    t = traits(persona) if (persona is not None and not _NEUTRAL[0]) else {"horizon": None, "discount": 1.0}
    xs = [o["hedonic"][role]["pleasure"] for o in outcomes]
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


def play_future(world, w, last, weeks, fs, fx=None, edit=None):
    c = copy_world(world)
    if fx is not None:
        c.fx = fx
    if edit is not None:
        edit(c)
    resample(c, w, fs, weeks)
    lt = last
    for x in range(w, w + weeks):
        lt = {"busy": c.step_week(x, lt)}
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
    acc = {"A": 0.0, "B": 0.0}
    for k in range(n):
        c = play_future(world, w, last, weeks, future_seed(world.seed, w, k, salt), fx, edit)
        for r in "AB":
            acc[r] += score(c.run.outcomes, r, world.personas[r])
    return {r: v / n for r, v in acc.items()}


def forward_values(world, w, last, weeks, fx=None):
    """The status quo of the live household (negotiation.forward_values under the hybrid). Memoized inside negotiation.forward_memo."""
    from . import negotiation as NG
    use = world.fx if fx is None else fx
    key = None
    if NG._FWD is not None:
        key = (id(world), w, weeks, repr(use), repr(last))
        if key in _MEMO:
            return dict(_MEMO[key])
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
    own rollout, seeded per future); the better of the two; plus the persona's outside-option bias."""
    from . import negotiation as NG
    n = n or k_of()
    kw = {"weeks": weeks} if weeks else {}
    d = {}
    for m in ("alone", "friend"):
        d[m] = sum(NG.alone_value(p, role, holdings, future_seed(seed, int(holdings), k, salt + "|out"), m, hed, cx=cx, **kw)
                   for k in range(n)) / n
    return max(d.values()) + (0.0 if _NEUTRAL[0] else traits(p)["outside_bias"]), d


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
        resample(c, 0, future_seed(seed, 0, k, salt), weeks)
        lt = {"busy": {"A": False, "B": False}}
        for x in range(weeks):
            lt = {"busy": c.step_week(x, lt)}
        STATS["futures"] += 1
        STATS["future_weeks"] += weeks
        for r in "AB":
            acc[r] += score(c.run.outcomes, r, c.personas[r])
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
    """values: {term: {role: v}}; outside: {role: v}. The household's term: the one whose worse-off member gains most over the outside
    option (ties: income first). -> (term, formed)."""
    best = max(TERMS, key=lambda t: (min(values[t][r] - outside[r] for r in "AB"), t == "income"))
    return best, all(values[best][r] > outside[r] for r in "AB")


def set_agreement(world, term):
    world.agree = {"term": term, "share": shares(term)}


# ---- formation, retries, readings, returns --------------------------------------------------------------------------------------

def _o_both(personas, holdings, seed, heds=None, cxs=None, salt="fut", n=None):
    from . import negotiation as NG
    O, det = {}, {}
    for r in "AB":
        O[r], det[r] = outside_value(personas[r], r, holdings[r], seed, (heds or {}).get(r), (cxs or {}).get(r),
                                     weeks=NG.decide_weeks(0) or None, salt=salt, n=n)
    return O, det


def formation0(lived):
    """Week 0 under the hybrid: score the household under each bill term and each member's outside option on K fresh futures; form
    under the chosen term iff both gain (decline=True), or always (decline=False). -> (formed, term, O, det)."""
    from . import negotiation as NG
    from .worlds import household as H
    STATS["choices"] += 1
    weeks = NG.decide_weeks(NG.OUT_WEEKS)
    ps = {"A": lived.pa, "B": lived.pb}
    hold = NG.START_HOLDINGS[0] + NG.START_HOLDINGS[1]

    def mk(term):
        def make():
            wd = H.WeeklyWorld(list(lived.cards), (lived.pa, lived.pb), lived.seed, max(weeks, 1))
            set_agreement(wd, term)
            return wd
        return make

    def vals(salt, n=None):
        return {t: fresh_value(mk(t), lived.seed, weeks, salt, n) for t in TERMS}

    V = vals("fut")
    O, det = _o_both(ps, {"A": hold, "B": hold}, lived.seed)
    term, formed = choose_term(V, O)
    if AUDIT is not None:
        Vh = vals("held", AUDIT_M)
        Oh, _ = _o_both(ps, {"A": hold, "B": hold}, lived.seed, salt="held", n=AUDIT_M)
        opts = {t: {"F": V[t], "R": Vh[t]} for t in TERMS}
        opts["outside"] = {"F": O, "R": Oh}
        audit_choice("formation0", 0, (lived.pa.id, lived.pb.id), opts, (term if formed else "outside"))
    if not lived.decline:
        formed = True
    return formed, term, O, det, V


def retry(lived, w, last):
    """A 13-week retry of a pair living apart: the household under each term (a copy formed now) against each member's outside option."""
    from . import negotiation as NG
    world = lived.world
    STATS["choices"] += 1
    weeks = NG.decide_weeks(NG.FORWARD_WEEKS)
    O, modes, det = {}, {}, {}
    for r, p in zip("AB", (lived.pa, lived.pb)):
        O[r], d = outside_value(p, r, world.p[r]["money"], lived.seed, world.hed[r], cx=NG._cx(world, r), weeks=NG.decide_weeks(0) or None)
        modes[r], det[r] = NG.apart_mode(d), d
    hyp = copy_world(world)
    NG._form_baseline(hyp, w)

    def edit(term):
        return lambda c: set_agreement(c, term)

    V = {t: forecast(hyp, w, last, weeks, edit=edit(t)) for t in TERMS}
    term, formed = choose_term(V, O)
    if AUDIT is not None:
        Vh = {t: forecast(hyp, w, last, weeks, edit=edit(t), salt="held", n=AUDIT_M) for t in TERMS}
        Oh = {r: outside_value(p, r, world.p[r]["money"], lived.seed, world.hed[r], cx=NG._cx(world, r),
                               weeks=NG.decide_weeks(0) or None, salt="held", n=AUDIT_M)[0] for r, p in zip("AB", (lived.pa, lived.pb))}
        opts = {t: {"F": V[t], "R": Vh[t]} for t in TERMS}
        opts["outside"] = {"F": O, "R": Oh}
        audit_choice("retry", w, (lived.pa.id, lived.pb.id), opts, term if formed else "outside")
    lived.retries.append({"week": w, "formed": formed, "outside": dict(O), "baseline": dict(V[term]), "term": term})
    if formed:
        NG._form_baseline(world, w)
        set_agreement(world, term)
        lived.apart = False
        if world.fx:
            for r in "AB":
                world.events.append((w, r, "formed"))
    else:
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

    sq = forecast(world, w, last, weeks)
    rv = forecast(world, w, last, weeks, edit=back)
    gain = {x: rv[x] - sq[x] for x in "AB"}
    world.ret_value = {r: (gain[r] * weeks if all(g > 0 for g in gain.values()) else 0.0)}
    if AUDIT is not None:
        audit_choice("return", w, (world.personas["A"].id, world.personas["B"].id),
                     {"stay_out": {"F": sq, "R": forecast(world, w, last, weeks, salt="held", n=AUDIT_M)},
                      "return": {"F": rv, "R": forecast(world, w, last, weeks, edit=back, salt="held", n=AUDIT_M)}},
                     "return" if world.ret_value[r] > 0 else "stay_out")


def due(world, w):
    """An early reading is due: a member in distress flagged it, both are in, and the last reading is at least hybrid_gap weeks back."""
    fx = world.fx
    return (bool(getattr(world, "hyb_due", False)) and all(world.p[x]["in"] for x in "AB")
            and w - getattr(world, "hyb_last", -99) >= fx.hybrid_gap)


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

def week_start(world, w, last):
    """Called at the start of each week of a hybrid world: reset the call counter and, in a lived world, keep a snapshot for forks."""
    world._ncall = {"A": 0, "B": 0}
    world._wk_snap = None
    if getattr(world, "fork_ok", False):
        world._fmemo = {}
        from . import valuecheck as VC
        snap = VC.snapshot(world)
        snap.fork_ok = False
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
