"""Value consistency check (src/mar/valuecheck.py): the measurement leaves the live world alone, reads the agent's own scores without
noise or draws, and its branches do what they say (idle does nothing at the call; force executes the action; forcing the action the
world chose reproduces the world)."""
import random

from mar import valuecheck as VC
from mar.retest import personas
from mar.worlds import household as H

PAIR = ("g-00010", "p-host")
WEEKS = 30


def _world(seed=0):
    ps = personas()
    return H.WeeklyWorld(H.load_variant("baseline"), (ps[PAIR[0]], ps[PAIR[1]]), seed, WEEKS)


def _play_to(world, w):
    last = {"busy": {"A": False, "B": False}}
    for x in range(w):
        last = {"busy": world.step_week(x, last)}
    return last


def _fingerprint(world):
    return [(o["week"], {r: (o["hedonic"][r]["pleasure"], o["hedonic"][r]["s_off"], o["hedonic"][r]["B"]) for r in "AB"})
            for o in world.run.outcomes]


def test_measurement_leaves_live_world_unchanged():
    ref = _world()
    ref.play()
    live = _world()
    last = _play_to(live, 6)
    snap = VC.snapshot(live)
    VC.measure_decision(snap, dict(last), 6, "A", 2, horizons=(1, 5))
    for x in range(6, WEEKS):
        last = {"busy": live.step_week(x, last)}
    assert _fingerprint(live) == _fingerprint(ref)
    assert [t["action"] for t in live.run.trace] == [t["action"] for t in ref.run.trace]


def test_perceived_menu_is_noise_free_and_draws_nothing():
    world = _world()
    last = _play_to(world, 4)
    ag = world.agents["A"]
    o = world.obs("A", 4, last)
    st = ag.rng.getstate()
    u, cands = VC.perceived_menu(ag, o)
    assert ag.rng.getstate() == st
    assert "_noise" not in ag.__dict__
    u2, _ = VC.perceived_menu(ag, o)
    assert u == u2                                   # no noise: the same scores twice
    for s, c in cands:
        if c["a"] in u and c["a"] != "spend_shared":
            assert abs(s - u[c["a"]]) < 1e-12


def test_idle_executes_nothing_and_force_executes_the_action():
    world = _world()
    last = _play_to(world, 5)
    snap = VC.snapshot(world)
    tap, _ = VC.branch(snap, dict(last), 5, "B", 2, "idle", weeks=1)
    assert tap.menu is not None and tap.executed() is None
    rec = VC.measure_decision(snap, dict(last), 5, "B", 2, horizons=(1,))
    assert rec["items"], "some action should be measurable"
    assert any(it["applied"] for it in rec["items"])
    for it in rec["items"]:
        assert set(it["actual"][1]) == {"own", "partner"}
        assert set(it["actual"][1]["own"]) == set(VC.MEASURES)


def test_forcing_the_worlds_own_choice_reproduces_the_world():
    """Known answer: with common random numbers off, forcing at a call the action the live world executed there gives the live world."""
    ref = _world()
    ref.play()
    w, r = 7, "A"
    acts = [t for t in ref.run.trace if t["week"] == w and t["role"] == r and t["executed"]]
    assert acts
    world = _world()
    last = _play_to(world, w)
    snap = VC.snapshot(world)
    cand = {"a": acts[0]["action"], **({"kind": acts[0]["kind"]} if acts[0].get("kind") else {})}
    if acts[0].get("take"):
        cand["take"] = acts[0]["take"]
    tap, rows = VC.branch(snap, dict(last), w, r, 0, "force", cand, weeks=WEEKS - w, crn=False)
    assert tap.executed()[0] == acts[0]["action"]
    got = [x["pl"] for x in rows[r]]
    want = [o["hedonic"][r]["pleasure"] for o in ref.run.outcomes[w:]]
    assert got == want


def test_common_random_numbers_make_branches_repeatable():
    world = _world(seed=3)
    last = _play_to(world, 4)
    snap = VC.snapshot(world)
    _, r1 = VC.branch(snap, dict(last), 4, "A", 1, "idle", weeks=10)
    _, r2 = VC.branch(snap, dict(last), 4, "A", 1, "idle", weeks=10)
    assert [x["net"] for x in r1["A"]] == [x["net"] for x in r2["A"]]
    VC.reseed(world, 9)
    assert isinstance(world.agents["A"].rng, random.Random)


def test_perceived_includes_the_sanction_estimate():
    """Baseline card D1 makes spend_self a soft rule while bills are unpaid (warn, one month): the agent's choice subtracts its estimate
    0.01 x 4 weeks, and so does the measured perceived value."""
    world = _world()
    last = {"busy": {"A": False, "B": False}}
    found = None
    for w in range(WEEKS - 2):
        snap = VC.snapshot(world)
        for r in "AB":
            rec = VC.measure_decision(snap, dict(last), w, r, 0, horizons=(1,))
            for it in (rec or {}).get("items", []):
                if it["a"] == "spend_self" and it["rule"] == "soft":
                    found = it
        if found:
            break
        last = {"busy": world.step_week(w, last)}
    assert found is not None
    assert abs(found["sanction_est"] - H.SANCTION_UTILITY["warn"] * H.MONTH_WEEKS) < 1e-12
    assert abs(found["perceived"] - (found["score"] - found["sanction_est"])) < 1e-12
