from pathlib import Path
from mar.cards import load_cards, make_card
from mar.gate import Gate
from mar.fishery import run_fishery
from mar.mocks import Exploiter, Compliant
from mar.patcher import propose_patch
from mar.patch_check import check_patch, check_spec
from mar import oracle

RULES = Path(__file__).parent.parent / "rules" / "fishery"


def conflicting():
    return make_card({"id": "C1", "attribute": "fisher", "deontic": "must", "aim": "harvest",
                      "conditions": [{"expr": "catch", "op": "ge", "value": 20}], "or_else": None,
                      "gloss": "Every fisher must take at least 20 fish per harvest action.",
                      "source": "V2 fixture (deliberately conflicting patch)"})


def test_baseline_spec_passes_all_checks():
    assert all(v["verdict"] == "pass" for v in check_spec(load_cards(RULES)))


def test_patcher_gets_trace_and_cards_returns_cap_card_and_closes_seam():
    cards = load_cards(RULES)
    trace = run_fishery([Exploiter() for _ in range(4)], Gate(cards), seed=0).trace
    patch = propose_patch(trace, cards)
    assert [c.id for c in patch] == ["P1"]
    report = check_patch(cards, patch)
    assert report["accepted"], report
    run = run_fishery([Exploiter() for _ in range(4)], Gate(cards + patch), seed=0)
    assert oracle.judge(run.outcomes)["ok"]
    assert propose_patch(trace, cards + patch) == []  # no second cap


def test_patcher_leaves_compliant_trace_alone():
    cards = load_cards(RULES)
    trace = run_fishery([Compliant() for _ in range(4)], Gate(cards), seed=0).trace
    assert propose_patch(trace, cards) == []


def test_conflicting_patch_rejected_with_ids():
    cards = load_cards(RULES)
    report = check_patch(cards, [conflicting()])
    assert not report["accepted"]
    by = {v["check"]: v for v in report["verdicts"]}
    assert by["a_no_conflict"]["verdict"] == "fail" and {"C1", "F1"} <= set(by["a_no_conflict"]["cards"])
    assert by["b_no_deadlock"]["verdict"] == "fail" and "C1" in by["b_no_deadlock"]["cards"]


def test_unbounded_sanction_fails_and_long_sanction_is_open_not_pass():
    cards = load_cards(RULES)
    def sanc(kind, d):
        return make_card({"id": "S1", "attribute": "fisher", "deontic": "must_not", "aim": "harvest",
                          "conditions": [{"expr": "catch", "op": "gt", "value": 0},
                                         {"expr": "month_total + catch", "op": "gt", "value": 40}],
                          "or_else": {"kind": kind, "duration_months": d}, "gloss": "g", "source": "s"})
    by = lambda r: {v["check"]: v for v in r["verdicts"]}
    forever = check_patch(cards, [sanc("ban", None)])
    assert by(forever)["c_bounded_sanctions"]["verdict"] == "fail"
    long_ = check_patch(cards, [sanc("suspend", 5)])
    assert by(long_)["d_repair_path"]["verdict"] == "open" and not long_["accepted"]


def test_naive_cap_without_catch_gt_zero_is_a_deadlock():
    """Regression for the first V2 run: the cap card alone also blocks catch 0 when over the cap."""
    naive = make_card({"id": "N1", "attribute": "fisher", "deontic": "must_not", "aim": "harvest",
                       "conditions": [{"expr": "month_total + catch", "op": "gt", "value": 40}],
                       "or_else": None, "gloss": "g", "source": "s"})
    r = check_patch(load_cards(RULES), [naive])
    assert {v["check"]: v["verdict"] for v in r["verdicts"]}["b_no_deadlock"] == "fail"
