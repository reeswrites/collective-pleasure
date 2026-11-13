"""KL1 (docs/results/hybrid-exit-option-prereg.md; hybrid prereg Amendment 4): the reading for a member left alone in the household
(FixConfig.hybrid_lone), off by default."""
import dataclasses
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

A3 = {"hybrid_w": "persona", "hybrid_readings": "world"}


def _lone_world(weeks=40, **kw):
    """The formation check's household under the hybrid, no harness, with B moved out at week 0: A is alone in the household."""
    import formation_check_3 as FC3
    import stay_test_run as STR
    from mar import hedonic as HD
    from mar import pairing as PR
    from mar import retest as RT
    from mar.worlds import household as H
    ps = STR.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **FC3.rule("hybrid"), **{**A3, **kw})
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        world = H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), (ps["p-anchor"], ps["p-host"]), 900, weeks)
    world.p["B"]["in"] = False
    world.solo = {"A": None, "B": "friend"}
    return world, fx


def _no_return(monkeypatch):
    """B stays out (no return), so A stays alone and every reading A gets is a lone reading."""
    from mar.worlds import household as H
    real = H.WeeklyWorld.feasible
    monkeypatch.setattr(H.WeeklyWorld, "feasible", lambda self, r, a, kind=None: False if a == "return" else real(self, r, a, kind))


def _play(world, fx, weeks):
    from mar import hedonic as HD
    from mar import retest as RT
    last = {"busy": {"A": False, "B": False}}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        for w in range(weeks):
            last = {"busy": world.step_week(w, last)}


def test_flag_off_the_member_alone_never_gets_a_reading(monkeypatch):
    _no_return(monkeypatch)
    world, fx = _lone_world()
    _play(world, fx, 30)
    assert not getattr(world, "lone_log", [])
    assert getattr(world, "bar_runs", {"A": 0})["A"] == 0
    assert world.p["A"]["in"]


def test_flag_on_the_member_alone_is_read_at_each_mark_and_on_distress_never_inside_a_forecast(monkeypatch):
    from mar import hybrid as HY
    _no_return(monkeypatch)
    world, fx = _lone_world(hybrid_lone=True)
    weeks_seen = []
    real = HY.lone_reading

    def spy(lived, w, last):
        weeks_seen.append((w, HY.lived(lived.world)))
        return real(lived, w, last)
    monkeypatch.setattr(HY, "lone_reading", spy)
    _play(world, fx, 30)
    log = getattr(world, "lone_log", [])
    assert log, "no lone reading ran"
    ws = [x["week"] for x in log]
    assert 13 in ws and (26 in ws or not world.p["A"]["in"])
    assert all(ok for _, ok in weeks_seen)                         # only lived worlds read
    assert all(b - a >= fx.hybrid_gap for a, b in zip(ws, ws[1:]))  # early readings at most every hybrid_gap weeks
    assert all(x["role"] == "A" for x in log)


def test_a_lone_member_whose_outside_option_beats_staying_twice_leaves(monkeypatch):
    from mar import negotiation as NG
    _no_return(monkeypatch)
    world, fx = _lone_world(hybrid_lone=True)
    monkeypatch.setattr(NG, "outside_value", lambda *a, **k: (10.0, {"alone": 10.0, "friend": 9.0}))
    _play(world, fx, 30)
    log = world.lone_log
    assert [x["bar_out"] for x in log[:2]] == [False, True]
    left = [e for e in world.exit_log if e["role"] == "A"]
    assert left and left[0]["week"] >= log[1]["week"] and not world.p["A"]["in"]


def test_flag_off_a_lone_member_with_a_better_outside_option_stays(monkeypatch):
    from mar import negotiation as NG
    _no_return(monkeypatch)
    world, fx = _lone_world()
    monkeypatch.setattr(NG, "outside_value", lambda *a, **k: (10.0, {"alone": 10.0, "friend": 9.0}))
    _play(world, fx, 30)
    assert world.p["A"]["in"]


def test_an_emptied_household_counts_as_apart_only_with_the_flag():
    from mar import hybrid as HY
    for flag, want in ((False, False), (True, True)):
        world, fx = _lone_world(hybrid_lone=flag)
        world.p["A"]["in"] = False
        lived = types.SimpleNamespace(world=world, apart=False)
        HY.lone_apart(lived)
        assert lived.apart is want
        world.lat = True
        lived = types.SimpleNamespace(world=world, apart=False)
        HY.lone_apart(lived)
        assert lived.apart is False                                  # living apart together is not an emptied household
