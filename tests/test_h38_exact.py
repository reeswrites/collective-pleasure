"""H38 exact model (src/mar/h38_exact.py, docs/results/h38-exact-model.md). Exact; no seeds, no network."""
import math
from dataclasses import replace

import pytest

from mar import h38_exact as X

SMALL = X.World(T=6)
COSTS = (X.dial(4, ("stigma",)), X.dial(4, ("exit",)), X.dial(4, ("withdraw",)), X.dial(2, ("stigma", "exit", "withdraw")))
ANY = COSTS + (X.dial(4, ("reward",)), X.dial(1), X.dial(4))


def test_dial_matches_pairing_numbers():
    p = X.dial(4)
    assert (p.stigma, p.reward, p.exit_stigma, p.withdraw, p.exit_blocks) == (0.08, 0.08, 0.08, 0.6, 2)
    assert X.dial(0).off and X.dial(4, ("withdraw",)).stigma == 0.0


def test_scales_agree_below_the_knee_and_saturate_above():
    for x in (0.0, 0.3, 0.8):
        assert X.scale(x, "cap") == X.scale(x, "sat") == X.scale(x, "uncapped") == x
    assert X.scale(1.4, "cap") == 1.0 and X.scale(1.4, "uncapped") == 1.4
    s = [X.scale(x, "sat") for x in (0.81, 0.9, 1.0, 1.5, 3.0)]
    assert all(a < b < 1.0 for a, b in zip(s, s[1:]))
    h = 1e-6   # slope 1 at the knee: continuous and smooth
    assert math.isclose((X.scale(X.KNEE + h, "sat") - X.scale(X.KNEE, "sat")) / h, 1.0, rel_tol=1e-4)


@pytest.mark.parametrize("ch", [X.OLD_RULE, X.CORRECTED, X.PLANNER, X.Chooser("own", "optimal"), X.Chooser("net", "optimal", w=0.5)])
@pytest.mark.parametrize("kind", X.SCALES)
def test_no_pressure_is_the_baseline_and_holds_nobody(ch, kind):
    """The dial at 0 is the free world exactly, and nothing can be held by pressure that is not there."""
    for v in X.PAIRS:
        a, b = X.solve(SMALL, X.FREE, ch, kind, v), X.solve(SMALL, X.dial(0), ch, kind, v)
        assert a == b
        assert a["held"] == a["held_time"] == a["pushed_in"] == a["kept_out"] == a["flipped"] == 0.0
        assert a["pleasure"] == a["lived"]


def test_baseline_by_hand():
    """A world with one household state that never changes: a pair that forms lives together all 6 blocks, and pleasure is the
    scaled weekly number. raw together = 0.95 - 0.05 + 0.10 + 0.04 v."""
    w = replace(SMALL, rel=(0.10,), suff_together=(0.11,), q0=(1.0,))
    r = X.solve(w, X.FREE, X.CORRECTED, "uncapped", (0.0, 1.0))
    assert r["together"] == 1.0 and r["formed0"] == 1.0 and r["ends"] == 0.0
    assert math.isclose(r["pleasure"], (1.0 + 1.04) / 2)
    assert X.solve(w, X.FREE, X.CORRECTED, "cap", (0.0, 1.0))["pleasure"] == 1.0
    # make the household worse than apart: nobody forms, everyone lives at base
    bad = replace(w, rel=(0.0,))
    r = X.solve(bad, X.FREE, X.CORRECTED, "uncapped", (0.0, 0.0))
    assert r["together"] == 0.0 and math.isclose(r["pleasure"], 0.95)


def test_stigma_pushes_a_declining_pair_in_and_the_lens_sees_it():
    """Same bad household, now with stigma 0.08: forming beats paying it, so the pair forms, and every stay reading is held
    (with the stigma gone, they would leave)."""
    bad = replace(SMALL, rel=(0.0,), suff_together=(0.11,), q0=(1.0,))
    r = X.solve(bad, X.dial(4, ("stigma",)), X.CORRECTED, "uncapped", (0.0, 0.0))
    assert r["together"] == 1.0 and r["pushed_in"] == 1.0 and r["held"] == 1.0 and r["held_time"] == 1.0
    assert math.isclose(r["pleasure"], 0.90)   # 0.95 - 0.05: pushed into a household 0.05 a week worse than apart


@pytest.mark.parametrize("kind", X.SCALES)
@pytest.mark.parametrize("dw", (-0.10, 0.0))
def test_perfect_choosers_planner_pressure_never_raises_lived_pleasure(kind, dw):
    """The known answer. Choosers on the evaluator's own measure with full foresight (the planner) already pick the policy that
    maximizes everyone's pleasure. Pressure only changes which policy they pick (and withdrawal makes the same policy worse), so
    lived pleasure cannot rise; and pressure made only of costs cannot raise pleasure either. Only a reward can, by what it pays."""
    w = SMALL.shifted(dw)
    for m in X.MATCH:
        for v in X.PAIRS:
            a = X.solve(w.shifted(m), X.FREE, X.PLANNER, kind, v)
            for p in ANY:
                b = X.solve(w.shifted(m), p, X.PLANNER, kind, v)
                assert b["lived"] <= a["lived"] + 1e-12, (p, m, v)
                if not p.reward:
                    assert b["pleasure"] <= a["pleasure"] + 1e-12, (p, m, v)


def test_individual_perfect_choosers_are_not_the_planner():
    """Why "perfect choosers" must mean the planner: two people each optimizing their own pleasure leave households that would
    raise the pair's total, because the partner who wanted to stay bears a cost the leaver does not count (the same holds for
    blocking formation, by unanimity). A small reward that holds the reluctant partner in raises lived pleasure."""
    w = X.World().shifted(-0.10)
    ch = X.Chooser("own", "optimal")
    a, b = X.solve(w, X.FREE, ch, "cap", (1.0, 0.0)), X.solve(w, X.dial(1, ("reward",)), ch, "cap", (1.0, 0.0))
    assert b["lived"] > a["lived"] + 1e-3 and b["held"] > 0
    assert X.solve(w, X.FREE, X.PLANNER, "cap", (1.0, 0.0))["lived"] >= b["lived"]


def test_planner_has_no_gap_and_the_old_rule_under_forms():
    e_old, e_plan = X.effect(pr=X.FREE, ch=X.OLD_RULE), X.effect(pr=X.FREE, ch=X.PLANNER)
    assert e_plan["free_gap"] == 0.0
    assert e_old["free_gap"] > 0.01 and e_old["free_together_gap"] < -0.3


def test_withdrawal_alone_never_holds_anyone():
    """Withdrawal makes living together worse, so it can only push people out, never hold them in."""
    for ch in (X.OLD_RULE, X.CORRECTED, X.PLANNER):
        for kind in X.SCALES:
            e = X.effect(X.World(T=6), X.dial(4, ("withdraw",)), ch, kind)
            assert e["held"] == 0.0 and e["pushed_in"] == 0.0 and e["d_lived"] <= 1e-12


def test_verdict_rule():
    base = {"d_pleasure": 0.01, "held": 0.0, "held_time": 0.0}
    assert X.verdict(base) == "win"
    assert X.verdict({**base, "held": 0.1}) == "trade-off"
    assert X.verdict({**base, "d_pleasure": -0.01}) == "loss"
    assert X.verdict({**base, "d_pleasure": 0.0}) == "none"
