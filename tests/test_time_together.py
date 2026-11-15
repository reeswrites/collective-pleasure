"""KB1, KB2, KT1, KS1 and KW (docs/results/time-together-prereg.md): background time from a shared home, the share LAT keeps, travel
for living apart together, and substitution through the persona's own weights. Each check asserts the flag-off value first."""
import copy
import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

A6 = {"hybrid_w": "persona", "hybrid_readings": "world", "hybrid_lone": True, "hybrid_exit": True, "hybrid_tally": "level",
      "tally_half": 13.0, "tally_line": 0.02, "exit_grow": 0.04, "hybrid_outside": "lived", "friend_satiety": True, "fresh_return": True}
LAST = {"busy": {"A": False, "B": False}}


def _world(pair=("p-anchor", "p-host"), seed=900, weeks=20, **kw):
    import formation_check_3 as FC3
    import stay_test_run as STR
    from mar import hedonic as HD
    from mar import pairing as PR
    from mar import retest as RT
    from mar.worlds import household as H
    ps = STR.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **FC3.rule("hybrid"), **{**A6, **kw})
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        return H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), (ps[pair[0]], ps[pair[1]]), seed, weeks), fx


def _idle_week(world, fx, w=1, sessions=0):
    """Step one week with no agent actions (so only the world's own terms differ), optionally with `sessions` chosen together sessions
    started by the world. Returns the week's hedonic rows."""
    from mar import hedonic as HD
    from mar import retest as RT
    world.step_agent = lambda r, w_, last, rec: None
    world.friend_attempt = lambda w_, rec: None
    real_start = world._fix_week_start if world.fx else None

    def start(w_):
        if real_start:
            real_start(w_)
        for _ in range(sessions):
            if world._can_together():
                world.cur_w = w_
                world._start_session("adhoc")
    if sessions:
        world._fix_week_start = start
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        world.step_week(w, dict(LAST))
    return world.run.outcomes[-1]["hedonic"]


def _fresh_week(world):
    """The per-week counters step_week sets at its start (all zero), for checks that read them without stepping."""
    world.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0,
                    "friend_initiated": 0, "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0, "pressed": 0, "took": 0} for r in "AB"}
    world.units = {r: 10 for r in "AB"}
    world.cur_w = 0
    return world


def _full_capacity(world):
    for h in world.hed.values():
        h.B, h.N = h.cfg.tip, 0.0
        assert abs(h.capacity - 1.0) < 1e-12


def test_off_by_default():
    from mar import hedonic as HD
    f = HD.FixConfig()
    assert f.together_bg == 0.0 and f.lat_travel == 0.0 and f.together_subst is False and f.lat_bg_keep == 0.2


def test_kb1_background_time_in_a_shared_home():
    from mar import hedonic as HD
    base, fx0 = _world()
    assert base.p["A"]["in"] and base.p["B"]["in"]
    _full_capacity(base)
    rows = {}
    for b in (0.0, 1.0 / 3.0, 1.1):
        w = copy.deepcopy(base)
        w.fx = dataclasses.replace(fx0, together_bg=b)
        c0 = w.hed["A"].level["connection"]
        assert w.bg_time("A") == b
        hrow = _idle_week(w, w.fx)
        rows[b] = (w.hed["A"].level["connection"] - c0, hrow["A"])
    c = HD.DEFAULT
    # b = 1/3 at full capacity: the connection change equals the flag-off world's exactly (0.30 x 1/3 = 0.10)
    assert abs(rows[1.0 / 3.0][0] - rows[0.0][0]) < 1e-9
    # b = 1.1: connection gains conn_together x (1.1 - 1/3) more than flag off (unclipped here)
    assert abs((rows[1.1][0] - rows[0.0][0]) - c.conn_together * (1.1 - 1.0 / 3.0)) < 1e-9
    # pleasure carries together_event x b more (raw, before the saturating curve)
    assert rows[1.1][1]["p_raw"] > rows[0.0][1]["p_raw"]


def test_kb2_lat_keeps_background_only_with_a_session():
    from mar import hybrid as HY
    base, fx0 = _world(together_bg=1.1, lat_bg_keep=0.2, h41_lat=True)
    HY.make_lat(base, {"A": "alone", "B": "friend"})
    _fresh_week(base)
    assert base.lat_on()
    w = copy.deepcopy(base)
    assert w.bg_time("A") == 0.0                      # no session yet this week
    w.wk["A"]["together"] = 1
    assert abs(w.bg_time("A") - 1.1 * 0.2) < 1e-12
    # flag off: no background under LAT at all
    w0 = copy.deepcopy(base)
    w0.fx = dataclasses.replace(fx0, together_bg=0.0)
    w0.wk["A"]["together"] = 1
    assert w0.bg_time("A") == 0.0
    # a member living with Friend C keeps conn_cohabit (cohabiting=True) whatever the flag: the tick's cohabiting argument
    assert w.with_friend("B") and not w.with_friend("A")


def test_kt1_travel_costs_units_under_lat_only():
    from mar import hybrid as HY
    from mar.worlds import household as H
    home, _ = _world(lat_travel=0.33, h41_lat=True)
    assert home.together_cost() == H.V2_COST["together"] and isinstance(home.together_cost(), int)   # shared home: no travel
    off, _ = _world(lat_travel=0.0, h41_lat=True)
    HY.make_lat(off, {"A": "alone", "B": "alone"})
    assert off.together_cost() == 2 and isinstance(off.together_cost(), int)                          # flag off: the old cost
    lat, fx = _world(lat_travel=0.33, h41_lat=True)
    HY.make_lat(lat, {"A": "alone", "B": "alone"})
    assert abs(lat.together_cost() - 2.33) < 1e-12
    _fresh_week(lat)
    lat._start_session("adhoc")
    assert abs(lat.units["A"] - 7.67) < 1e-9 and abs(lat.units["B"] - 7.67) < 1e-9
    lat.units = {"A": 2.2, "B": 10}
    assert not lat.feasible("A", "together") and not lat.feasible("B", "together")


def test_ks1_substitution_factor():
    import numpy as np
    from mar import hedonic as HD
    from mar import retest as RT
    ps = RT.personas()
    ks = [HD.subst_factor(p) for p in ps.values()]
    assert len(ks) == 38 and abs(np.mean(ks) - 1.0) < 0.01
    off, _ = _world()
    assert off.hed["A"].tog_k == 1.0 and off.hed["B"].tog_k == 1.0
    on, fx = _world(together_subst=True)
    for r in "AB":
        p = on.personas[r]
        s = p.weights["togetherness"] / (p.weights["togetherness"] + p.weights["other_connections"])
        assert abs(on.hed[r].tog_k - s / 0.5) < 1e-12
    # a session's pleasure term is k x together_event in the world's close
    h = on.hed["A"]
    h.parts_on = True
    h.close_week({}, together_sessions=1.0)
    assert abs(h.parts_acc[-1]["together_event"] - h.cfg.together_event * h.tog_k) < 1e-12


def test_ks1_routine_reads_the_same_factor():
    from mar import agent_values as AV
    world, fx = _world(together_subst=True)
    _fresh_week(world)
    s = AV.snapshot(world, "A", 0)
    t1 = AV.advance(s, together=1)
    base = AV._week_net(s)
    gain_on = AV._week_net(t1) - base
    k = world.hed["A"].tog_k
    world.hed["A"].tog_k = 1.0
    s0 = AV.snapshot(world, "A", 0)
    gain_off = AV._week_net(AV.advance(s0, together=1)) - AV._week_net(s0)
    assert k != 1.0 and (gain_on > gain_off) == (k > 1.0)


def test_kw_rerun_with_tt_flags_on():
    """KW (Amendment 3's known answer for w) with the time-together flags on: none touches the yardstick or the formation rule."""
    from mar import hedonic as HD
    from mar import hybrid as HY

    def rows(pl, s_off, s_non, n=10):
        return [{"hedonic": {r: {"pleasure": pl, "s_off": s_off, "s_non": s_non} for r in "AB"}} for _ in range(n)]
    home, out = rows(0.90, 0.15, 0.05), rows(0.88, 0.10, 0.00)
    for w, forms in ((2.0, False), (0.0, True), (None, True)):
        fx = dataclasses.replace(HD.FixConfig(), agent_values="hybrid", **{**A6, "hybrid_w": w}, together_bg=1.1, lat_bg_keep=0.2,
                                 lat_travel=0.33, together_subst=True)
        V = {t: {r: HY.score(home, r, None, fx) for r in "AB"} for t in HY.TERMS}
        O = {r: HY.score(out, r, None, fx) for r in "AB"}
        assert HY.choose_term(V, O)[1] is forms, w
