"""Household evolution: world adapter, filter, operators, loop, and the exam-isolation checks (docs/results/household-exam-prereg.md section 4)."""
import inspect
import random
import re
from pathlib import Path

import pytest

from mar import evolve as EV
from mar import world_api as W

ROOT = Path(__file__).parent.parent
WORLD = W.HouseholdEvolveWorld()


def test_denylist_is_the_mechanical_rule_and_is_excluded_everywhere():
    grid = [i for i in W.hh_personas() if i.startswith("g-")]
    assert len(grid) == 32
    assert W.held_out_by_rule(grid) == sorted(W.DENYLIST) and len(W.DENYLIST) == 6
    assert not set(W.DENYLIST) & set(W.training_persona_ids())
    assert len(W.training_persona_ids()) == 35
    for a, b, _ in W._pairing_pool():
        assert a not in W.DENYLIST and b not in W.DENYLIST
    for split in ("train", "val"):
        ctx = W.make_context(1, 3, 40, split=split)
        assert all(r.a not in W.DENYLIST and r.b not in W.DENYLIST for r in ctx.runs)


def test_train_and_val_pairings_are_disjoint():
    tr = {(r.a, r.b) for g in range(5) for r in W.make_context(1, g, 20, split="train").runs}
    va = {(r.a, r.b) for g in range(5) for r in W.make_context(1, g, 20, split="val").runs}
    assert tr and va and not tr & va


def test_training_conditions_stay_inside_the_permitted_training_distribution():
    d = W._HD.DEFAULT
    for g in range(30):
        for r in W.make_context(2, g, 20).runs:
            assert r.weeks in W.TRAIN_WEEKS and max(W.TRAIN_WEEKS) <= 156
            assert not 9000 <= r.seed <= 9999
            jl, ill, mv, nc = r.rates
            assert 0.5 * d.job_loss_rate - 1e-3 <= jl <= 1.5 * d.job_loss_rate + 1e-3
            assert 0.5 * d.illness_rate - 1e-3 <= ill <= 1.5 * d.illness_rate + 1e-3
            assert 0.5 * d.move_rate - 1e-3 <= mv <= 1.5 * d.move_rate + 1e-3
            assert 0.15 <= nc <= 0.25 + 0.05
            assert -0.1 <= r.start <= 0.1


def test_context_is_deterministic():
    assert W.make_context(5, 2, 8) == W.make_context(5, 2, 8)
    assert W.make_context(5, 2, 8) != W.make_context(5, 3, 8)


def test_evolve_household_has_no_exam_argument():
    params = inspect.signature(EV.evolve_household).parameters
    assert not any("exam" in p for p in params)
    assert not hasattr(EV, "household_exam")


def test_no_exam_condition_value_in_evolution_code():
    """The recorded grep, scoped to the household evolution code. The tokens are built by arithmetic so this file does not contain them."""
    seeds = [str(9000 + i) for i in range(1, 6)]
    shock = [f"{0.12 * 2:.2f}", f"{0.12 * 3:.2f}", f"{0.087 * 2:.3f}", f"{0.087 * 3:.3f}"]
    horizon = [str(130 * 2)]
    starts = [r"-0\.3" + "0", r"\+0\.3" + "0"]
    pats = [rf"\b{t}\b" for t in seeds + horizon] + [re.escape(t) for t in shock] + starts
    marker = "# Household world for the evolution loop"
    texts = {"world_api.py": (ROOT / "src/mar/world_api.py").read_text().split(marker, 1)[1],
             "evolve.py": (ROOT / "src/mar/evolve.py").read_text().split("# Household evolution (first household run", 1)[1],
             "household_evolve_run.py": (ROOT / "scripts/household_evolve_run.py").read_text()}
    for name, txt in texts.items():
        for p in pats:
            assert not re.search(p, txt), (name, p)


def test_seeds_pass_the_filter_and_protections():
    for n in ("author_seed_v2_bindable", "author_seed_v2_free_exit", "baseline", "needs_duty", "no_pressure_wall"):
        ok, why = WORLD.check(WORLD.load_spec(n), None)
        assert ok, (n, why)
    assert W.hh_protections(WORLD.load_spec("author_seed_v2_bindable")) == {"no_veto": True, "free_exit": True}
    assert W.hh_protections(WORLD.load_spec("trap"))["free_exit"] is False
    assert W.hh_protections(WORLD.load_spec("baseline"))["no_veto"] is False


def _card(cid, deontic, aim, conds=(), or_else=None, gloss="A fixture rule for the test only."):
    return W.make_card({"id": cid, "attribute": "partner", "deontic": deontic, "aim": aim, "conditions": list(conds),
                        "or_else": or_else, "gloss": gloss, "source": "test fixture, never a rule"})


def test_filter_rejects_a_deadlock_and_a_contradiction():
    base = WORLD.load_spec("baseline")
    ok, why = WORLD.check(base + (_card("X1", "must_not", "any"),), base)
    assert not ok and any(r.startswith(("lint", "proof")) for r in why)
    ok, why = WORLD.check(base + (_card("X2", "must", "leave", [{"expr": "take", "op": "ge", "value": 60}]),), base)
    assert not ok                                           # contradicts E1-at-most-half or leaves no exit


def test_redundancy_flags_a_restated_card_and_not_a_distinct_one():
    base = WORLD.load_spec("no_pressure_wall")
    assert W.hh_redundant_cards(base) == []
    dup = base[0]
    clone = W.make_card({**{k: getattr(dup, k) for k in ("attribute", "deontic", "aim", "conditions", "or_else", "gloss", "source")}, "id": "CLONE"})
    assert set(W.hh_redundant_cards(base + (clone,))) == {dup.id, "CLONE"}      # each is implied by the other
    ok, why = WORLD.check(base + (clone,), base)
    assert not ok and "redundancy" in why
    # a parent's own redundancy is inherited, not held against the child
    ok2, why2 = WORLD.check(base + (clone,), base + (clone,))
    assert "redundancy" not in why2


def test_operators_return_valid_cards_with_plain_glosses():
    rng = random.Random(0)
    seen = set()
    for i in range(500):
        spec = WORLD.load_spec(("author_seed_v2_bindable", "baseline", "needs_duty")[i % 3])
        child, op = WORLD.mutate(spec, rng, {"veto": 1, "leave_blocked": 1})
        if child is None:
            continue
        seen.add(op)
        ids = [c.id for c in child]
        assert len(ids) == len(set(ids))
        for c in child:
            assert c.gloss.strip() and c.source.strip() and c.attribute in ("partner", "friend")
            if c.source.startswith("evolved"):
                assert not re.search(r"\b(unless|except)\b", c.gloss, re.I)
    assert seen == set(W.HOPS)


def test_negotiated_term_operator_swaps_a_term_and_never_duplicates_it():
    spec = WORLD.load_spec("author_seed_v2_free_exit")
    out = W._hop_add_term(spec, WORLD, random.Random(3))
    assert out is None or len({c.id for c in out}) == len(out)
    assert [c.id for c in W._term_cards("exit", "forfeit")] == ["N5a-exit-forfeit"]
    assert [c.id for c in W._term_cards("use", "caps")] == ["N2-use-caps"]
    assert W._term_cards("stay", 0) == [] and W._term_cards("requests", "none") == []


def test_spec_diff_plain():
    a, b = WORLD.load_spec("baseline"), WORLD.load_spec("needs_duty")
    d = W.spec_diff_plain(a, b)
    assert any(x.startswith("REMOVED") for x in d) and W.spec_diff_plain(a, a) == []


def test_mini_evolution_is_deterministic_and_logs(tmp_path):
    cfg = EV.HConfig(pop=4, offspring=2, generations=1, runs=2)
    seeds = {n: WORLD.load_spec(n) for n in ("baseline", "needs_duty")}
    r1 = EV.evolve_household(WORLD, seeds, 3, cfg, log_path=tmp_path / "a.jsonl")
    r2 = EV.evolve_household(W.HouseholdEvolveWorld(), seeds, 3, cfg)
    assert [c.id for c in r1["elite"].spec] == [c.id for c in r2["elite"].spec]
    assert r1["elite"].scores == r2["elite"].scores
    assert len((tmp_path / "a.jsonl").read_text().splitlines()) == 2
    g = r1["log"][1]
    assert g["proposed"] >= g["accepted"] + g["filter_rejected"]
    assert set(r1["elite"].scores) >= set(WORLD.objectives)


def test_a_seed_that_fails_the_filter_stops_the_run():
    with pytest.raises(ValueError):
        EV.evolve_household(WORLD, {"bad": (_card("X1", "must_not", "any"),)}, 1, EV.HConfig(pop=2, offspring=1, generations=0, runs=1))


def test_nondominated_selection_and_bloat_tiebreak_for_household():
    mk = lambda n, s: EV.Individual(tuple(range(n)), s, None, frozenset(), {}, "seed")
    a = mk(5, {"pleasure": .8, "no_fail": 1.0, "liberty": 2.0, "cooperation": .8})
    b = mk(2, {"pleasure": .8, "no_fail": 1.0, "liberty": 2.0, "cooperation": .8})     # same scores, fewer cards
    c = mk(3, {"pleasure": .7, "no_fail": .9, "liberty": 1.0, "cooperation": .7})      # dominated
    keep = EV._hsurvive(WORLD, [a, c, b], 2)
    assert keep[0] is b and c not in keep


def _script():
    import importlib.util
    spec = importlib.util.spec_from_file_location("household_evolve_run", ROOT / "scripts" / "household_evolve_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_prereg_verdict_can_happen_on_synthetic_fronts():
    """Free check that P1 and P4 can both pass and fail (docs/results/household-evolve.md, 'Can every verdict happen')."""
    R = _script()
    seed = {"pleasure": .80, "no_fail": .90, "liberty": 1.0, "cooperation": .80}
    better = {"pleasure": .80, "no_fail": .90, "liberty": 1.5, "cooperation": .80}            # +0.5 bits, nothing lost
    worse = {"pleasure": .70, "no_fail": .90, "liberty": 3.0, "cooperation": .80}             # gains liberty but loses pleasure by more than the margin
    assert R.p1_line([{"val": better}], seed) is True
    assert R.p1_line([{"val": seed}], seed) is False                                          # the seed itself is not better than the seed
    assert R.p1_line([{"val": worse}], seed) is False                                         # a loss beyond the margin blocks it
    a = {"pleasure": .9, "no_fail": .8, "liberty": 3.0, "cooperation": .8}
    b = {"pleasure": .8, "no_fail": .8, "liberty": 4.8, "cooperation": .8}                    # a beats b on pleasure, b beats a on liberty / 6 by 0.3
    assert R.p4_line([{"train": a}, {"train": b}]) is True
    assert R.p4_line([{"train": a}, {"train": dict(a, liberty=3.1)}]) is False                # near-ties are not a trade-off
    assert R.p4_line([{"train": a}]) is False
