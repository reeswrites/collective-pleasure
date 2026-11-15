"""KF1, KR1 and KW (docs/results/hybrid-a6-prereg.md; hybrid prereg Amendment 6): friend visits valued at the world's satiety
(FixConfig.friend_satiety) and no return on a stale return value (FixConfig.fresh_return). Each test shows the bug with the flag off,
then the fix with it on."""
import copy
import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

A3 = {"hybrid_w": "persona", "hybrid_readings": "world"}
A5 = {**A3, "hybrid_lone": True, "hybrid_exit": True, "hybrid_tally": "level", "tally_half": 13.0, "tally_line": 0.02, "exit_grow": 0.04,
      "hybrid_outside": "lived"}
LAST = {"busy": {"A": False, "B": False}}


def _world(weeks=40, pair=("p-anchor", "p-host"), seed=900, **kw):
    import formation_check_3 as FC3
    import stay_test_run as STR
    from mar import hedonic as HD
    from mar import pairing as PR
    from mar import retest as RT
    from mar.worlds import household as H
    ps = STR.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **FC3.rule("hybrid"), **{**A3, **kw})
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        return H.WeeklyWorld(H.PyGate(H.load_variant("baseline")), (ps[pair[0]], ps[pair[1]]), seed, weeks), fx


def _visits(world, fx, weeks):
    """Step the world; at every call where a visit is on A's menu, keep a deep copy of the world and A's observation."""
    from mar import hedonic as HD
    from mar import retest as RT
    seen = []
    orig = world.obs

    def spy(r, w, last):
        o = orig(r, w, last)
        if r == "A" and o.get("can_see_friend") and "lever" in o and o.get("v2") is not None:
            seen.append((copy.deepcopy(world), o))
        return o
    world.obs = spy
    last = dict(LAST)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        for w in range(weeks):
            last = {"busy": world.step_week(w, last)}
    world.obs = orig
    return seen


def _own_visit(world, o):
    from mar import agent_values as AV
    ag = world.agents["A"]
    ag._noise = lambda: 1.0
    parts = {}
    AV.utilities(ag, o, parts)
    return parts["see_friend"]["own_week"]


def _week_change(o, fs):
    from mar import agent_values as AV
    s = o["v2"]
    return round(AV.week_net(AV.advance(s, friends=1, scale=(fs, 1.0))) - AV.week_net(s), 6)


def test_kf1_bug_flag_off_values_a_visit_at_full_strength_while_the_world_habituates_it():
    world, fx = _world(friend_satiety=False)
    seen = _visits(world, fx, 30)
    assert len(seen) >= 5
    gaps = []
    for c, o in seen:
        lev = o["lever"]
        assert "friend_next" not in lev
        c._lever_visit("A")
        world_scale = c.lw["fr"]["A"][-1]                     # what the world records for this visit
        if not lev["adaptive"]:
            assert abs(_own_visit(c, o) - _week_change(o, 1.0)) < 2e-6     # the routine: full strength
            gaps.append(1.0 - world_scale)
    assert gaps and max(gaps) > 0.1                           # the world habituates; the routine does not see it (the bug)


def test_kf1_fix_flag_on_values_a_visit_at_exactly_the_world_scale():
    world, fx = _world(friend_satiety=True)
    seen = _visits(world, fx, 30)
    assert len(seen) >= 5
    scales = set()
    for c, o in seen:
        exp = o["lever"]["friend_next"]
        own = _own_visit(c, o)
        c._lever_visit("A")
        assert abs(c.lw["fr"]["A"][-1] - exp) < 1e-12        # friend_next is what the world gives the next visit
        assert abs(own - _week_change(o, exp)) < 2e-6         # and the routine values the visit at it
        scales.add(round(exp, 6))
    assert len(scales) >= 3 and min(scales) < 0.9


def _returned_then_left(world, fx, w):
    """A member that returned on a value from a return reading, then leaves again at week w: its return value as it leaves."""
    from mar import hedonic as HD
    from mar import retest as RT
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        world.p["A"]["in"] = False
        world.ret_value = {"A": 5.0}                          # set by a return reading during that out-spell
        world.apply("A", {"a": "return"}, w, [])
        assert world.p["A"]["in"]
        world.apply("A", {"a": "leave", "take": 50, "why": "bar"}, w, [])
        assert not world.p["A"]["in"] and world.p["B"]["in"]
        return world.obs("A", w, {"A": False, "B": False, "busy": {"A": False, "B": False}})["return_value"]


def _stepped(fresh, weeks=10):
    from mar import hedonic as HD
    from mar import retest as RT
    world, fx = _world(fresh_return=fresh)
    last = dict(LAST)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        for w in range(weeks):
            last = {"busy": world.step_week(w, last)}
    return world, fx


def test_kr1_bug_flag_off_a_stale_return_value_survives_the_next_exit_in_life_and_in_a_forecast_copy():
    from mar import hybrid as HY
    world, fx = _stepped(False)
    copy_ = HY.copy_world(world)
    assert _returned_then_left(world, fx, 10) == 5.0          # lived world: may walk straight back in (the bug)
    assert _returned_then_left(copy_, fx, 10) == 5.0          # inside a forecast copy: the same


def test_kr1_fix_flag_on_a_return_needs_a_new_return_reading():
    from mar import hybrid as HY
    world, fx = _stepped(True)
    copy_ = HY.copy_world(world)
    assert _returned_then_left(world, fx, 10) == 0.0
    assert _returned_then_left(copy_, fx, 10) == 0.0
    world.ret_value = {**world.ret_value, "A": 3.0}           # a return reading in this out-spell sets a fresh value: it counts
    assert world.ret_value["A"] == 3.0


def test_off_by_default():
    from mar import hedonic as HD
    assert HD.FixConfig().friend_satiety is False and HD.FixConfig().fresh_return is False


def test_kw_rerun_with_a6_flags_on():
    """KW (Amendment 3's known answer for w) with Amendment 6's flags on: neither touches the yardstick or the formation rule."""
    from mar import hedonic as HD
    from mar import hybrid as HY

    def rows(pl, s_off, s_non, n=10):
        return [{"hedonic": {r: {"pleasure": pl, "s_off": s_off, "s_non": s_non} for r in "AB"}} for _ in range(n)]
    home, out = rows(0.90, 0.15, 0.05), rows(0.88, 0.10, 0.00)
    for w, forms in ((2.0, False), (0.0, True), (None, True)):
        fx = dataclasses.replace(HD.FixConfig(), agent_values="hybrid", hybrid_w=w, hybrid_lone=True, hybrid_exit=True,
                                 hybrid_tally="level", exit_grow=0.04, hybrid_outside="lived", friend_satiety=True, fresh_return=True)
        V = {t: {r: HY.score(home, r, None, fx) for r in "AB"} for t in HY.TERMS}
        O = {r: HY.score(out, r, None, fx) for r in "AB"}
        assert HY.choose_term(V, O)[1] is forms, w
