"""KO0 (docs/results/hybrid-leaving-prereg.md; hybrid prereg Amendment 5): the outside option of a member in a household as the lived
world played on with that member gone (FixConfig.hybrid_outside="lived"), and the bias arm (FixConfig.leave_bias); both off by default."""
import dataclasses
import sys
import types
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
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(1), **FC3.rule("hybrid"), **{**A3, **kw})
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        return H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), (ps["p-anchor"], ps["p-host"]), 900, weeks), fx


def _outside(world, fx, r, ctx=True):
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import negotiation as NG
    from mar import retest as RT
    hold = world.p[r]["money"] + (world.carry_out(r, 50) if world.p[r]["in"] else 0)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        if ctx:
            with HY.outside_ctx(world, 0, LAST):
                return NG.outside_value(world.personas[r], r, hold, world.seed, world.hed[r], cx=NG._cx(world, r)), hold
        return NG.outside_value(world.personas[r], r, hold, world.seed, world.hed[r], cx=NG._cx(world, r)), hold


def test_ko0_the_lived_outside_option_is_the_world_played_on_with_the_member_gone():
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import negotiation as NG
    from mar import pairing as PR
    from mar import retest as RT
    world, fx = _world(hybrid_outside="lived")
    (v, d), hold = _outside(world, fx, "A")
    mode = NG.apart_mode(d)

    def gone(c):
        if "A" not in c.wk:
            c.wk = {x: {"sanctioned": 0} for x in "AB"}
            c.units = {x: 99 for x in "AB"}
        c.bar_mode["A"] = mode
        c.apply("A", {"a": "leave", "take": 50, "why": "bar"}, 0, [])
        c.p["A"]["money"] = hold
        solo = dict(c.solo) if isinstance(c.solo, dict) else {x: c.solo for x in "AB"}
        solo["A"] = mode
        c.solo = solo
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), HY.exit_ref({}):
        hand = HY.forecast(world, 0, LAST, NG.decide_weeks(NG.OUT_WEEKS), fx=fx, edit=gone)["A"]
        ea = PR.exit_anticipation(types.SimpleNamespace(fx=fx))
    assert ea > 0                                       # pressure dial 1: the lived futures pay the exit stigma, callers subtract it
    assert abs(v - (hand + ea)) < 1e-12
    (v_solo, d_solo), _ = _outside(world, fx, "A", ctx=False)
    assert d_solo == d and v_solo != v                  # without a lived choice in view: the old rollout


def test_the_lived_outside_does_not_return_on_a_stale_return_value():
    """A return value set at an earlier spell (world.ret_value) must not send the counterfactual leaver straight back in."""
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import retest as RT
    world, fx = _world(hybrid_outside="lived")
    world.ret_value = {"A": 5.0}
    seen = []
    real = HY.play_future

    def spy(*a, **k):
        c = real(*a, **k)
        if (a[6] if len(a) > 6 else k.get("edit")) is not None:      # an outside future (the member's exit forced by an edit)
            seen.append(sum(o["both_in"] for o in c.run.outcomes))
        return c
    import pytest
    mp = pytest.MonkeyPatch()
    mp.setattr(HY, "play_future", spy)
    try:
        _outside(world, fx, "A")
    finally:
        mp.undo()
    assert seen and all(n == 0 for n in seen)            # the leaver stays out in every outside future
    assert world.ret_value == {"A": 5.0}                 # the lived world is untouched


def test_ko0_a_member_out_keeps_the_old_value():
    world, fx = _world(hybrid_outside="lived")
    world.p["B"]["in"] = False
    old_w, old_fx = _world()
    old_w.p["B"]["in"] = False
    assert _outside(world, fx, "B") == _outside(old_w, old_fx, "B")


def test_solo_default_is_unchanged_inside_a_context():
    world, fx = _world()
    assert _outside(world, fx, "A") == _outside(world, fx, "A", ctx=False)


def test_leave_bias_lowers_the_outside_of_a_member_in_only():
    world, fx = _world(leave_bias=0.05)
    old, _ = _outside(world, _world()[1], "A")
    (v, _), _ = _outside(world, fx, "A")
    assert abs(v - (old[0] - 0.05)) < 1e-12
    world.p["B"]["in"] = False
    (vb, _), _ = _outside(world, fx, "B")
    w0, f0 = _world()
    w0.p["B"]["in"] = False
    (vb0, _), _ = _outside(w0, f0, "B")
    assert vb == vb0


def test_off_by_default():
    from mar import hedonic as HD
    assert HD.FixConfig().hybrid_outside == "solo" and HD.FixConfig().leave_bias == 0.0
