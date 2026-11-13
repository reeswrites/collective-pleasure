"""KX0 and KX1 (docs/results/hybrid-exit-option-prereg.md; hybrid prereg Amendment 4): forecasts with the option to leave later
(FixConfig.hybrid_exit), off by default."""
import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

A3 = {"hybrid_w": "persona", "hybrid_readings": "world"}
LAST = {"busy": {"A": False, "B": False}}


def _world(weeks=60, **kw):
    import formation_check_3 as FC3
    import stay_test_run as STR
    from mar import hedonic as HD
    from mar import pairing as PR
    from mar import retest as RT
    from mar.worlds import household as H
    ps = STR.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **FC3.rule("hybrid"), **{**A3, **kw})
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        return H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), (ps["p-anchor"], ps["p-host"]), 900, weeks), fx


def _forecast(world, fx, ref=None, weeks=52):
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import retest as RT
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), HY.exit_ref(ref):
        return HY.forecast(world, 0, LAST, weeks)


def test_kx0_an_anchor_no_future_reaches_gives_the_flag_off_forecast_exactly():
    from mar import hybrid as HY
    off_w, off_fx = _world()
    on_w, on_fx = _world(hybrid_exit=True)
    low = {r: (-99.0, "alone") for r in "AB"}
    n0 = HY.STATS.get("future_readings", 0)
    v_on = _forecast(on_w, on_fx, low)
    assert HY.STATS.get("future_readings", 0) > n0                # the in-future readings ran
    assert v_on == _forecast(off_w, off_fx)


def test_flag_off_ignores_any_anchor():
    off_w, off_fx = _world()
    high = {r: (10.0, "alone") for r in "AB"}
    assert _forecast(off_w, off_fx, high) == _forecast(off_w, off_fx)


def test_kx1_an_anchor_every_future_beats_leaves_at_the_second_in_future_reading():
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import retest as RT
    world, fx = _world(hybrid_exit=True)
    high = {r: (10.0, "friend") for r in "AB"}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        c = HY.play_future(world, 0, LAST, 52, HY.future_seed(world.seed, 0, 0), None, None, high)
    assert len(c.run.outcomes) == 52                              # the future plays all its weeks
    first = min(e["week"] for e in c.exit_log)
    assert first == 26                                            # readings at 13 (one run) and 26 (two in a row: the bar)
    assert not any(o["both_in"] for o in c.run.outcomes[26:])     # the leaver's last 26 weeks are lived outside
    assert all(o["both_in"] for o in c.run.outcomes[:26])
    v_hi = _forecast(world, fx, high)
    v_lo = _forecast(world, fx, {r: (-99.0, "alone") for r in "AB"})
    assert v_hi != v_lo                                           # the option reaches the value a choice compares


def test_default_anchor_is_the_readings_outside_option():
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import negotiation as NG
    from mar import retest as RT
    world, fx = _world(hybrid_exit=True)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        ref = HY.exit_ref_for(world, fx)
        for r in "AB":
            carry = world.p[r]["money"] + world.carry_out(r, 50)
            O, d = NG.outside_value(world.personas[r], r, carry, world.seed, world.hed[r], cx=NG._cx(world, r))
            assert ref[r] == (O, NG.apart_mode(d))
        assert HY.exit_ref_for(world, dataclasses.replace(fx, hybrid_exit=False)) is None
        with HY.exit_ref({"A": (1.0, "alone")}):
            assert HY.exit_ref_for(world, fx) == {"A": (1.0, "alone")}


def test_kw_rerun_with_both_new_flags_on():
    """KW (Amendment 3's known answer for w), rerun with hybrid_lone and hybrid_exit on: neither flag touches the yardstick or the rule."""
    from mar import hedonic as HD
    from mar import hybrid as HY

    def rows(pl, s_off, s_non, n=10):
        return [{"hedonic": {r: {"pleasure": pl, "s_off": s_off, "s_non": s_non} for r in "AB"}} for _ in range(n)]
    home, out = rows(0.90, 0.15, 0.05), rows(0.88, 0.10, 0.00)
    for w, forms in ((2.0, False), (0.0, True), (None, True)):
        fx = dataclasses.replace(HD.FixConfig(), agent_values="hybrid", hybrid_w=w, hybrid_lone=True, hybrid_exit=True)
        V = {t: {r: HY.score(home, r, None, fx) for r in "AB"} for t in HY.TERMS}
        O = {r: HY.score(out, r, None, fx) for r in "AB"}
        assert HY.choose_term(V, O)[1] is forms, w
