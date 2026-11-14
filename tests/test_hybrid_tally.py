"""KT0, KT1, KT2 (docs/results/hybrid-leaving-prereg.md; hybrid prereg Amendment 5): the fading tally that calls a rethink
(FixConfig.hybrid_tally), off by default."""
import dataclasses
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

A3 = {"hybrid_w": "persona", "hybrid_readings": "world"}
LAST = {"busy": {"A": False, "B": False}}


def _world(weeks=40, **kw):
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


def _play(world, fx, weeks):
    from mar import hedonic as HD
    from mar import retest as RT
    last = {"busy": {"A": False, "B": False}}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        for w in range(weeks):
            last = {"busy": world.step_week(w, last)}


def _rows(world):
    return [(o["both_in"], {r: (o["hedonic"][r]["pleasure"], o["hedonic"][r]["s_off"], o["hedonic"][r]["s_non"]) for r in "AB"})
            for o in world.run.outcomes]


def test_kt0_a_line_no_tally_reaches_leaves_the_lived_world_as_it_was():
    """Lived side of KT0, with forecasts that hold no in-future readings (hybrid_exit off), so only the tally itself could differ."""
    off_w, off_fx = _world()
    on_w, on_fx = _world(hybrid_tally="level", tally_line=99.0)
    off_w.tally_ref = on_w.tally_ref = None
    from mar import hybrid as HY
    on_w.tally_ref = {"A": 0.5, "B": 0.5}
    _play(off_w, off_fx, 30)
    _play(on_w, on_fx, 30)
    assert _rows(on_w) == _rows(off_w)
    assert on_w.exit_log == off_w.exit_log
    assert any(v is not None for v in on_w.tally.values())          # the tally ran
    assert not getattr(on_w, "tally_log", [])
    assert not HY.tally_flag(on_w)


def test_kt0_forecasts_read_only_at_marks_and_distress_weeks(monkeypatch):
    """Forecast side of KT0: with the tally on but a line no tally reaches, in-future readings fire only at 13-week marks and on a
    distress flag (the lived rule's timing)."""
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import retest as RT
    world, fx = _world(hybrid_exit=True, hybrid_tally="level", tally_line=99.0)
    seen = []
    real = HY.future_reading

    def spy(c, ref, x=None):
        seen.append((x, bool(getattr(c, "hyb_due", False)), HY.tally_flag(c)))
        return real(c, ref, x)
    monkeypatch.setattr(HY, "future_reading", spy)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        HY.play_future(world, 0, LAST, 52, HY.future_seed(world.seed, 0, 0), None, None, {r: (-99.0, "alone") for r in "AB"})
    assert seen
    for x, distress, tally in seen:
        assert x % 13 == 0 or distress
        assert not tally


def test_kt1_the_tally_calls_a_lived_reading_at_once_and_every_gap_weeks(monkeypatch):
    from mar import hybrid as HY
    monkeypatch.setattr(HY, "set_tally_ref", lambda world, O: None)    # keep the planted reference: the tally stays below the line
    world, fx = _world(hybrid_tally="level")
    world.tally_ref = {"A": 10.0, "B": 10.0}                           # an outside option far above any week: y - O far below the line
    _play(world, fx, 12)
    weeks = [x["week"] for x in getattr(world, "tally_log", [])]
    assert weeks[:2] == [1, 5]                                         # the week after it crosses, then every hybrid_gap = 4 weeks
    assert weeks[2:3] == [9] or (world.exit_log and world.exit_log[0]["week"] < 9)   # ... until a member leaves on the bar
    assert len(world.bar_log) >= 2                                     # each was a real reading (the bar rule ran)


def test_kt1_inside_a_forecast_the_tally_reads_before_week_13_and_a_member_can_leave():
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import retest as RT
    world, fx = _world(hybrid_exit=True, hybrid_tally="level")
    high = {r: (10.0, "friend") for r in "AB"}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        c = HY.play_future(world, 0, LAST, 52, HY.future_seed(world.seed, 0, 0), None, None, high)
    assert c.exit_log and min(e["week"] for e in c.exit_log) < 13     # A4's 13-week grid could not leave before week 26
    off_w, off_fx = _world(hybrid_exit=True)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(off_fx):
        c0 = HY.play_future(off_w, 0, LAST, 52, HY.future_seed(off_w.seed, 0, 0), None, None, high)
    assert min(e["week"] for e in c0.exit_log) == 26


def _fake(mode, line=0.02, half=13.0):
    from mar import hedonic as HD
    fx = dataclasses.replace(HD.FixConfig(), agent_values="hybrid", hybrid_tally=mode, tally_line=line, tally_half=half)
    w = types.SimpleNamespace(fx=fx, p={"A": {"in": True}, "B": {"in": False}}, personas={"A": None, "B": None},
                              tally_ref={"A": 0.5})
    return w


def _feed(w, ys):
    from mar import hybrid as HY
    out = []
    for y in ys:
        HY.tally_step(w, {"hedonic": {r: {"pleasure": y, "s_off": 0.0, "s_non": 0.0} for r in "AB"}})
        out.append((w.tally["A"], w.tally_due["A"]))
    return out


def test_kt2_the_tally_fades_and_recovers():
    w = _fake("level")
    xs = _feed(w, [0.40] * 20 + [0.60] * 40)              # 0.1 below the outside option, then 0.1 above it
    assert xs[0][0] < 0 and not xs[0][1]                   # starts at 0, moves a little
    assert any(d for _, d in xs[:20])                      # crosses the line
    assert xs[-1][0] > 0 and not xs[-1][1]                 # good weeks bring it back: thinking about leaving is reversible
    assert w.tally_hist["A"][-1] == xs[-1][0]


def test_kt2_level_fires_on_a_slow_drift_slope_does_not():
    ys = [0.5 - 0.0015 * i for i in range(80)]              # a slow slide to the same depth
    lv = _feed(_fake("level"), ys)
    sl = _feed(_fake("slope"), ys)
    assert any(d for _, d in lv)
    assert not any(d for _, d in sl)


def test_kt2_slope_fires_on_a_sharp_drop():
    ys = [0.5] * 10 + [0.0] * 6
    sl = _feed(_fake("slope"), ys)
    assert any(d for _, d in sl)
    both = _feed(_fake("both"), ys)
    assert any(d for _, d in both)


def test_off_by_default():
    from mar import hedonic as HD
    from mar import hybrid as HY
    assert HD.FixConfig().hybrid_tally is None
    assert not HY.tally_on(HD.FixConfig(agent_values="hybrid"))
    assert not HY.leave_on(HD.FixConfig(agent_values="hybrid"))
