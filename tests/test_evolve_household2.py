"""Household evolution run 2: exam-2 isolation, and the free check that every prereg verdict can happen (docs/results/household-evolve-2-prereg.md)."""
import importlib.util
import re
from pathlib import Path

import pytest

from mar import world_api as W
from mar.cards import load_cards

ROOT = Path(__file__).parent.parent


def _script():
    spec = importlib.util.spec_from_file_location("household_evolve2_run", ROOT / "scripts" / "household_evolve2_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def _reset_deny():
    yield
    W.use_extra_deny(())


def test_exam2_denylist_is_the_mechanical_rule_disjoint_from_exam1_and_excluded():
    grid = [i for i in W.hh_personas() if i.startswith("g-")]
    assert W.held_out_range(grid, 48, 96) == sorted(W.DENYLIST2) and len(W.DENYLIST2) == 6
    assert not set(W.DENYLIST2) & set(W.DENYLIST)
    base = set(W.training_persona_ids())
    W.use_extra_deny(W.DENYLIST2)
    now = set(W.training_persona_ids())
    assert len(base) == 35 and len(now) == 29 and not now & set(W.DENYLIST2)
    for a, b, _ in W._pairing_pool():
        assert a not in W.DENYLIST2 and b not in W.DENYLIST2 and a not in W.DENYLIST and b not in W.DENYLIST
    W.use_extra_deny(())
    assert len(W.training_persona_ids()) == 35          # default reproduces run 1


def test_no_exam2_condition_value_in_run2_evolution_code():
    seeds = [str(9100 + i) for i in (1, 2)]
    shock = [f"{0.087 * 2.5:.3f}", f"{0.087 * 4:.3f}", f"{0.12 * 4:.2f}", f"{0.08 * 4:.2f}"]
    pats = [rf"\b{t}\b" for t in seeds + [str(52 * 4)]] + [re.escape(t) for t in shock] + [r"[-+]0\.2" + "0"]
    texts = {"household_world_api": (ROOT / "src/mar/household_world_api.py").read_text().split("# Household world for the evolution loop", 1)[1],
             "evolve": (ROOT / "src/mar/evolve.py").read_text().split("# Household evolution (first household run", 1)[1],
             "run2": (ROOT / "scripts/household_evolve2_run.py").read_text()}
    for name, t in texts.items():
        for p in pats:
            assert not re.search(p, t), (name, p)


def test_run2_world_has_levers_powers_and_lifetime_horizon():
    S = _script()
    w = S.new_world()
    assert w.powers and w.levers.commit and w.levers.network and S.CFG.weeks == 156 == S.LIFETIME and S.WORKERS <= 4


def test_every_prereg_verdict_can_happen():
    S = _script()
    run1 = [load_cards(d) for d in sorted((ROOT / "docs/results/household-evolve-elites").glob("line-*"))]
    seed = tuple(W.HouseholdEvolveWorld().load_spec("author_seed_v2_bindable"))
    # P1 / P2 can MISS: the real run-1 elites keep no mechanic power (0 of 16); and HOLD: the author's seed keeps all three
    assert S.p1_count(run1) == 0 and S.p2_counts(run1) == {"commit_stay": 0, "commit_request": 0, "give": 0}
    assert S.p1_count([seed] * 16) == 16 and S.p2_counts([seed] * 16) == {p: 16 for p in S.POWERS}
    # P3 can hold and fail
    sd = {"pleasure": .8, "no_fail": .9, "liberty": 1.0, "cooperation": .8}
    assert S.p3_line([{"val": dict(sd, liberty=1.5)}], sd) and not S.p3_line([{"val": sd}], sd)
    # P5 can hold and fail (the author's seed has both protections; trap has not)
    assert S.p5_count([seed] * 16) == 16 and S.p5_count([tuple(W.HouseholdEvolveWorld().load_spec("trap"))]) == 0
    # the verdict labels: a hold, a threshold-met-not-significant, and misses
    hold, _ = S.verdicts(16, {p: 16 for p in S.POWERS}, 16, 0.02, 0.001, 16, 100, 1000)
    assert hold["P1"].startswith("holds") and hold["P2"] == "holds" and hold["P6"] == "holds robustly"
    miss, _ = S.verdicts(0, {p: 0 for p in S.POWERS}, 0, -0.01, 0.9, 0, 800, 1000)
    assert miss["P1"].startswith("miss") and miss["P2"] == "miss" and miss["P6"] == "miss" and miss["P4"].startswith("miss")
    weak, _ = S.verdicts(12, {p: 8 for p in S.POWERS}, 12, 0.02, 0.5, 12, 100, 1000)
    assert weak["P1"] == "meets threshold, not significant" or weak["P1"].startswith("holds")


def test_the_metric_sees_the_mechanism():
    """Liberty with powers rises when a card names a power (tests/test_liberty.py has the exact pins); the lever world changes scores."""
    from mar import empowerment as E
    from mar.worlds import household as H
    seed = H.load_variant("author_seed_v2_bindable")
    no_power = [c for c in seed if c.aim not in ("commit_stay", "commit_request", "give")]
    hw = E.HouseholdWorld(powers=True)
    from mar import liberty as L
    a = L.household_liberty(hw, H.PyGate(seed), hw.initial(), ("cooperator", "cooperator"), k=2)
    b = L.household_liberty(hw, H.PyGate(no_power), hw.initial(), ("cooperator", "cooperator"), k=2)
    assert all(x["liberty"] > y["liberty"] for x, y in zip(a, b))
