"""Pleasure demonstration instrument and report (docs/results/pleasure-demo-prereg.md). Wording rule: agents feel nothing; pleasure is a
gloss on a modeled hedonic state."""
import sys
from pathlib import Path

import pytest

from mar import pleasure_report as PR
from mar import personas as P
from mar.worlds import household as H

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import pleasure_demo as D  # noqa: E402

PERS = {p.id: p for p in P.load_dir(ROOT / "personas") + P.load_dir(ROOT / "personas" / "pressing")}


def play(variant="baseline", a="p-host", b="p-peacekeeper", seed=0, weeks=52, instr=True):
    w = H.WeeklyWorld(H.PyGate(H.load_variant(variant)), (PERS[a], PERS[b]), seed, weeks)
    if instr:
        PR.instrument(w)
    return w, w.play()


def test_terms_add_up_to_the_models_pleasure_every_week():
    w, run = play()
    for r in "AB":
        terms = w.hed[r].terms
        assert len(terms) == 52
        for t, o in zip(terms, run.outcomes):
            assert sum(t.values()) == pytest.approx(o["hedonic"][r]["pleasure"], abs=2e-4)
        assert w.hed[r].max_err < 2e-4


def test_instrument_does_not_change_the_worlds_results():
    _, a = play(instr=True)
    _, b = play(instr=False)
    assert [o["hedonic"] for o in a.outcomes] == [o["hedonic"] for o in b.outcomes]
    assert [(t["week"], t["role"], t["action"]) for t in a.trace] == [(t["week"], t["role"], t["action"]) for t in b.trace]


def test_every_source_has_a_group_and_a_category():
    assert set(PR.SOURCES) == set(PR.SOURCE_GROUP) == set(PR.CATEGORY)
    assert set(PR.SOURCE_GROUP.values()) == set(PR.SUBGROUPS)
    assert set(PR.CATEGORY.values()) == set(PR.CATEGORIES)


def test_relational_share_splits_individual_from_relational():
    src = {k: 0.0 for k in PR.SOURCES}
    src["need:rest"], src["event:together"], src["need:connection"], src["asp:savings_per_week"] = 0.2, 0.1, 0.2, 0.1
    assert PR.relational_share(src) == pytest.approx(0.3 / 0.6)
    assert PR.relational_share({k: 0.0 for k in PR.SOURCES}) == 0.0


def test_spiral_label_is_up_only_when_both_are_up_and_down_if_either_is():
    assert PR.spiral_label({"A": "up", "B": "up"}) == "up"
    assert PR.spiral_label({"A": "up", "B": "stalled"}) == "stalled"
    assert PR.spiral_label({"A": "up", "B": "down"}) == "down"


def test_household_record_has_the_trust_and_event_series():
    w, run = play(variant="author_seed_v2_bindable")
    rec = PR.household_record(w, run)
    assert len(rec["pl"]["A"]) == 52 and len(rec["trust"][0]) == 52 and len(rec["pool"]) == 52
    assert set(rec["grp"]["A"]) == set(PR.SUBGROUPS)
    assert 0.0 <= rec["rel_share"] <= 1.0 and rec["trust_min"] <= rec["trust_mean"]
    assert sum(rec["src"].values()) == pytest.approx(rec["pleasure"], abs=2e-3)


def test_terms_english_reads_a_bundle():
    from mar import negotiation as NG
    s = PR.terms_english({**NG.FAIR_DEFAULT, "stay": 52, "requests": "mutual"})
    assert "any thing" not in s and "anything" in s and "52 weeks" in s and "stay-home" in s
    assert PR.terms_english(None) == "no agreement"


@pytest.fixture(scope="module")
def v22_rows():
    rows = [D.run_task(("v22_bindable", "p-host", "p-peacekeeper", 900, "ctl")), D.run_task(("v22_free_exit", "p-host", "p-peacekeeper", 900, "ctl")),
            D.run_task(("baseline", "p-host", "p-peacekeeper", 900, "ctl")), D.run_task(("trap", "p-host", "p-peacekeeper", 900, "ctl"))]
    return rows


def test_vignette_is_built_from_traced_events(v22_rows):
    rec = next(r for r in v22_rows if r["arm"] == "v22_bindable")
    names = {"A": "Host", "B": "Peacekeeper"}
    v = PR.narrate_month(rec, PR.best_month(rec), names, PR.VARIANT_TEXT["v22_bindable"])
    text = " ".join(v["lines"])
    assert "Host" in v["title"] and "pleasure" in text and "shared pot" in text and "Trust" in text
    m = PR.month_stats(rec, v["month"])
    assert str(m["n_together"]) in text or m["n_together"] == 0
    assert 0 <= v["rel_share"] <= 1


def test_vignettes_pick_distinct_pairings(v22_rows):
    v = PR.vignettes(v22_rows)
    assert all(x["mood"] in ("good", "down") for x in v)
    pairs = [x["pairing"] for x in v if x["mood"] == "good"]
    assert len(pairs) == len(set(pairs))


def test_report_is_self_contained_and_themed(v22_rows):
    html = PR.build_report(v22_rows, [{"id": "D1a", "quantity": "q", "estimate": "e", "p": "0.01", "verdict": "holds robustly"}])
    assert "prefers-color-scheme:dark" in html and 'name="viewport"' in html and "<svg" in html
    assert "http://" not in html.replace("http://www.w3.org", "") and "https://" not in html and "<script" not in html
    assert "D1a" in html and "Modeled pleasure, not felt pleasure" in html


def test_demo_verdict_labels_follow_the_template():
    assert D.label(True, True, False, True) == "holds robustly"
    assert D.label(True, False, False, True) == "holds but CI crosses threshold"
    assert D.label(True, True, False, False) == "holds but CI crosses threshold"
    assert D.label(False, False, True, False) == "miss robust"
    assert D.label(False, False, False, False) == "miss but CI crosses threshold"


def test_demo_pairings_are_the_57_of_negotiation_v2_1():
    prs = D.pairings()
    assert len(prs) == 57 and sum(1 for p in prs if p[2] == "ctl") == 15
