"""KC1 (docs/results/hybrid-leaving-prereg.md; hybrid prereg Amendment 5): the exit cost that grows with weeks together
(FixConfig.exit_grow) and the KX2 fixture's pure exit cost (FixConfig.exit_fixed), both off by default."""
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


def _play(world, fx, w0, w1, before=None):
    from mar import hedonic as HD
    from mar import retest as RT
    last = {"busy": {"A": False, "B": False}}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        for w in range(w0, w1):
            if before:
                before(world, w)
            last = {"busy": world.step_week(w, last)}


def _no_return(monkeypatch):
    from mar.worlds import household as H
    real = H.WeeklyWorld.feasible
    monkeypatch.setattr(H.WeeklyWorld, "feasible", lambda self, r, a, kind=None: False if a == "return" else real(self, r, a, kind))


def test_kc1_the_leaver_pays_for_13_weeks_at_the_size_its_weeks_in_set(monkeypatch):
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import retest as RT
    _no_return(monkeypatch)
    world, fx = _world(exit_grow=0.04, hybrid_readings="harness")
    _play(world, fx, 0, 26)
    assert world.wks_in == {"A": 26, "B": 26}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        world.apply("A", {"a": "leave", "take": 50, "why": "bar"}, 26, [])
    assert world.xcost["A"] == (26, 0.04 * 26 / 52)
    _play(world, fx, 26, 45)
    paid = [o["hedonic"]["A"]["fix"].get("exit_cost", 0.0) for o in world.run.outcomes[26:45]]
    assert paid[:13] == [0.02] * 13 and paid[13:] == [0.0] * 6         # 13 weeks, then nothing
    assert all("exit_cost" not in o["hedonic"]["B"]["fix"] for o in world.run.outcomes)   # only the leaver pays
    assert all("exit_cost" not in o["hedonic"]["A"]["fix"] for o in world.run.outcomes[:26])


def test_kc1_off_by_default_nothing_is_kept():
    from mar import hedonic as HD
    from mar import hybrid as HY
    world, fx = _world(hybrid_readings="harness")
    _play(world, fx, 0, 5)
    assert not hasattr(world, "wks_in") and not hasattr(world, "xcost")
    assert HD.FixConfig().exit_grow == 0.0 and HD.FixConfig().exit_fixed == 0.0
    assert HY.antic(world, "A") == 0.0


def test_kc1_the_exit_priced_at_formation_is_cheaper_than_the_one_faced_later():
    from mar import hybrid as HY
    world, fx = _world(exit_grow=0.04)
    world.wks_in = {"A": 26, "B": 104}
    assert HY.exit_size(world, "A") == 0.02 and HY.exit_size(world, "B") == 0.08
    assert HY.antic(world, "A") < HY.antic(world, "B")
    world2, fx2 = _world(exit_fixed=0.04)
    world2.wks_in = {"A": 0, "B": 104}
    assert HY.exit_size(world2, "A") == HY.exit_size(world2, "B") == 0.04     # the pure cost does not grow


def test_kc1_an_in_future_reading_prices_the_cost_at_its_own_week(monkeypatch):
    """The anchor carries the anticipation at the choice; a future reading replaces it with the anticipation at its own week."""
    from mar import hedonic as HD
    from mar import hybrid as HY
    from mar import retest as RT
    world, fx = _world(hybrid_exit=True, exit_grow=0.04)
    world.wks_in = {"A": 52, "B": 52}
    seen = []
    real = HY.bar_one

    def spy(c, r, s, O, mode):
        seen.append((c.wks_in[r], O))
        return real(c, r, s, O, mode)
    monkeypatch.setattr(HY, "bar_one", spy)
    ref = {r: HY.ref_entry(world, r, 0.5 - HY.antic(world, r), "alone") for r in "AB"}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        HY.play_future(world, 0, LAST, 27, HY.future_seed(world.seed, 0, 0), None, None, ref)
    n = 52.0
    for wk_in, O in seen:
        assert abs(O - (0.5 - 0.04 * wk_in / 52 * 13 / n)) < 1e-12
    assert seen and seen[0][0] > 52


def test_kc1_with_the_flag_off_a_ref_entry_is_the_old_pair():
    from mar import hybrid as HY
    world, fx = _world()
    assert HY.ref_entry(world, "A", 0.3, "alone") == (0.3, "alone")
