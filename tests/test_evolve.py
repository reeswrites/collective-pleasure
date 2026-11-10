import copy
import inspect
import random

import pytest

from mar import evolve as E
from mar import world_api as W
from mar.cards import make_card
from mar.english import render
from mar.fishery import run_fishery
from mar.gate import Gate
from mar.mocks import Exploiter

SMALL = E.Config(pop=4, offspring=4, generations=2)


@pytest.fixture(scope="module")
def world():
    return W.FisheryWorld()


@pytest.fixture(scope="module")
def seed_spec(world):
    return tuple(world.load_spec())


def conflicting():
    return make_card({"id": "C1", "attribute": "fisher", "deontic": "must", "aim": "harvest",
                      "conditions": [{"expr": "catch", "op": "ge", "value": 20}], "or_else": None,
                      "gloss": "Every fisher must take at least 20 fish per harvest action.",
                      "source": "test fixture (deliberately conflicting)"})


def valid(spec):
    ids = [c.id for c in spec]
    assert len(ids) == len(set(ids))
    for c in spec:
        d = {"id": c.id, "attribute": c.attribute, "deontic": c.deontic, "aim": c.aim,
             "conditions": [dict(x) for x in c.conditions], "or_else": c.or_else, "gloss": c.gloss, "source": c.source}
        assert make_card(d) == c
        assert render(c).startswith(c.id + ".")  # has an English form
        for p in c.conditions:
            assert isinstance(p["value"], int)


def test_operators_produce_valid_cards(world, seed_spec):
    rng = random.Random(1)
    trace = world.run(seed_spec, [Exploiter() for _ in range(4)], 0, mix="all_exploit")
    seen_ops, spec = set(), seed_spec
    for _ in range(300):
        new, op = E.mutate(spec, world, rng, trace)
        if new is None:
            continue
        seen_ops.add(op)
        valid(new)
        spec = new if len(new) <= 8 else seed_spec
    assert seen_ops == set(E.OPS)


def test_proof_filter_rejects_planted_conflict(world, seed_spec):
    res = world.check_spec(seed_spec + (conflicting(),))
    assert res.verdict == "fail" and not res.ok and "a_no_conflict" in res.failed and res.k == 3
    assert world.check_spec(seed_spec).ok


def test_open_is_not_accepted(world, seed_spec):
    f1 = seed_spec[0]
    long = make_card({"id": f1.id, "attribute": f1.attribute, "deontic": f1.deontic, "aim": f1.aim,
                      "conditions": [dict(c) for c in f1.conditions],
                      "or_else": {"kind": "cap_halve", "duration_months": 5, "sanctioner": "monitor"},
                      "gloss": f1.gloss, "source": f1.source})
    res = world.check_spec((long,) + seed_spec[1:])
    assert res.verdict == "open" and not res.ok


def test_rejected_mutants_are_never_run(seed_spec, monkeypatch):
    class Counting(W.FisheryWorld):
        runs = 0

        def run(self, *a, **k):
            Counting.runs += 1
            return super().run(*a, **k)
    w = Counting()
    monkeypatch.setitem(E.OPERATORS, "bound", lambda spec, world, rng, trace=None: tuple(spec) + (conflicting(),))
    monkeypatch.setattr(E, "WEIGHTS", (1, 0, 0, 0, 0))
    out = E.evolve(w, seed_spec, 0, E.Config(pop=3, offspring=3, generations=1))
    g0 = out["log"][0]
    assert g0["accepted"] == 0 and g0["proof_rejected"] > 0
    assert g0["rejected_by_check"].get("a_no_conflict", 0) > 0
    assert Counting.runs == 9  # only the seed spec was ever run (8 mixes, jitter on 2 seeds)


def test_nondominated_sort_hand_case():
    pts = [(3, 1), (1, 3), (2, 2), (1, 1), (0, 0)]
    fronts = E.nondominated_sort(pts)
    assert [sorted(f) for f in fronts] == [[0, 1, 2], [3], [4]]
    cd = E.crowding_distance(pts, fronts[0])
    assert cd[0] == cd[1] == float("inf") and cd[2] == pytest.approx(2.0)
    assert not E.dominates((1, 1), (1, 1))


def test_hypervolume_hand_case():
    assert E.hypervolume([(1, 1, 1)]) == pytest.approx(1.0)
    assert E.hypervolume([(2, 1, 1), (1, 2, 1)]) == pytest.approx(3.0)
    assert E.hypervolume([(1, 1, 2), (2, 2, 1)]) == pytest.approx(1 * 1 * 2 + (4 - 1) * 1)


def test_constraint_dominance_feasible_first(world):
    a = E.Individual((), {"sustainability": 0.0, "fairness": 0.0, "seam_free": 0.0}, 1.0, frozenset())
    b = E.Individual((), {"sustainability": 1.0, "fairness": 1.0, "seam_free": 1.0}, 0.0, frozenset())
    E.rank_population(world, [a, b])
    assert a.rank == 0 and b.rank == 1


def test_determinism(world, seed_spec):
    a = E.evolve(world, seed_spec, 7, SMALL)["log"]
    b = E.evolve(W.FisheryWorld(), seed_spec, 7, SMALL)["log"]
    assert a == b
    c = E.evolve(world, seed_spec, 8, SMALL)["log"]
    assert a != c


def test_log_written_as_jsonl(world, seed_spec, tmp_path):
    import json
    p = tmp_path / "x" / "run.jsonl"
    E.evolve(world, seed_spec, 0, SMALL, log_path=p)
    rows = [json.loads(line) for line in p.read_text().splitlines()]
    assert [r["gen"] for r in rows] == [0, 1, 2]
    for key in ("proposed", "proof_rejected", "n_new_seams", "front", "pop_rules_mean", "hv"):
        assert key in rows[0]


def test_bloat_cap_and_floor(world, seed_spec):
    out = E.evolve(world, seed_spec, 3, E.Config(pop=4, offspring=4, generations=3, max_rules=5))
    assert all(i.n_rules <= 5 for i in out["pop"])
    assert out["elite"].yld >= world.YIELD_FLOOR


def test_exam_is_separate_from_selection():
    assert "exam" not in inspect.getsource(E.evolve).lower()
    assert "exam" not in inspect.signature(E.evolve).parameters
    import re
    assert not re.search(r"oracle\.\w|import oracle", inspect.getsource(E))
    assert "oracle" not in inspect.getsource(W.fishery_patch)


def test_regrowth_copy_matches_original_fishery(seed_spec):
    g = Gate(seed_spec)
    a = run_fishery([Exploiter() for _ in range(4)], g, seed=3)
    b = W.run_fishery_regrow([Exploiter() for _ in range(4)], g, seed=3, regrowth=2.0)
    assert a.trace == b.trace and a.outcomes == b.outcomes
    slow = W.run_fishery_regrow([W.Steady(1) for _ in range(4)], g, regrowth=1.5)
    assert slow.outcomes != W.run_fishery_regrow([W.Steady(1) for _ in range(4)], g).outcomes


def test_world_scores_seams_and_floor(world, seed_spec):
    tr = world.run(seed_spec, [Exploiter() for _ in range(4)], 0, mix="all_exploit")
    assert [s["kind"] for s in world.seams(tr, seed_spec)] == ["collapse"]
    assert world.score(tr)["seam_free"] == 0.0
    s, y, keys, _, _ = E.evaluate(world, seed_spec)
    assert y == 1.0 and world.feasible({"yield": y}) and ("all_exploit", "collapse") in keys
    tight = tuple(make_card({**{"id": c.id, "attribute": c.attribute, "deontic": c.deontic, "aim": c.aim,
                                "or_else": c.or_else, "gloss": c.gloss, "source": c.source},
                             "conditions": [{**p, "value": 4} if c.id == "F1" else dict(p) for p in c.conditions]})
                  for c in seed_spec)
    _, y2, _, _, _ = E.evaluate(world, tight)
    assert y2 == 0.0 and not world.feasible({"yield": y2})


def test_patch_adapter_sees_trace_only(world, seed_spec):
    tr = world.run(seed_spec, [Exploiter() for _ in range(4)], 0, mix="all_exploit")
    for s in range(20):
        new = W.fishery_patch(tr.run.trace, list(seed_spec), random.Random(s))
        assert new and new[0].id == "P1"
        valid(tuple(seed_spec) + tuple(new))
        assert world.check_spec(tuple(seed_spec) + tuple(new)).ok
