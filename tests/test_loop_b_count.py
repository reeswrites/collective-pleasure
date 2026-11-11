"""Loop b counting: rule mechanics and the prereg's "Can every verdict happen?" fixtures (synthetic, no model)."""
import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("loop_b_count", ROOT / "scripts" / "loop_b_count.py")
lb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lb)

T0 = datetime(2026, 11, 10, 20, 0, tzinfo=timezone.utc)


def synth(rates, n_per_half, quotes=("i think it should be more like this other thing instead", ) * 2,
          pass2_second=False, seed_order=True):
    """Opportunity items, one per event, first half then second half. rates = (first, second)."""
    items = []
    for h, (r, q) in enumerate(zip(rates, quotes)):
        k = round(r * n_per_half)
        for i in range(n_per_half):
            kind = "B2" if i < k else "C"
            items.append({"event": f"e{h}_{i}", "ts": T0 + timedelta(minutes=len(items)), "kind": kind,
                          "quote": q, "pass": 2 if (pass2_second and h == 1) else 1, "topic": None})
    return items


GOOD = {"kappa_opp": 0.9, "kappa_corr": 0.9}


# ---------------------------------------------------------------- every verdict is reachable

def test_converging_reachable():
    assert lb.analyze(synth((0.6, 0.1), 50), GOOD)["verdict"] == "converging"


def test_not_converging_reachable():
    assert lb.analyze(synth((0.4, 0.4), 50), GOOD)["verdict"] == "not converging"


def test_fatigue_reachable():
    res = lb.analyze(synth((0.6, 0.1), 50, quotes=("i think it should be more like this other thing", "yes")), GOOD)
    assert res["verdict"] == "falling, fatigue not excluded"
    assert not res["P2a"] and not res["P2b"]


def test_underpowered_reachable():
    assert lb.analyze(synth((0.6, 0.1), 10), GOOD)["verdict"].startswith("descriptive only, underpowered")


def test_rule_not_operational_reachable():
    assert lb.analyze(synth((0.6, 0.1), 50), {"kappa_opp": 0.3, "kappa_corr": 0.9})["verdict"] == \
        "rule not operational"


# ---------------------------------------------------------------- every clause can fail

def test_p1_fails_on_margin():
    res = lb.analyze(synth((0.5, 0.35), 50), GOOD)
    assert not res["P1"]["holds"] and res["P1"]["drop"] < 0.2


def test_p1_fails_on_test_with_big_drop():
    res = lb.analyze(synth((0.5, 0.25), 12), GOOD)
    assert res["P1"]["drop"] >= 0.2 and res["P1"]["p"] >= 0.05 and not res["P1"]["holds"]


def test_p2a_fails_on_length_alone():
    res = lb.analyze(synth((0.6, 0.1), 50, quotes=("one two three four five six seven eight nine ten",
                                                    "one two three four five")), GOOD)
    assert not res["P2a"] and res["P2b"]


def test_p2b_fails_on_bare_share_alone():
    first = synth((0.6, 0.1), 50, quotes=("yes that matches", "yes that matches"))
    for i, it in enumerate(first):
        if it["event"].startswith("e0") and i % 2:
            it["quote"] = "no that one changes"  # same length (3 words), not bare
    res = lb.analyze(first, GOOD)
    assert res["P2a"] and not res["P2b"]


def test_p3_fails_when_fall_is_only_reshown_items():
    res = lb.analyze(synth((0.6, 0.1), 50, pass2_second=True), GOOD)
    assert res["P1"]["holds"] and not res["P3"]["holds"]


def test_p0_fails_on_rater_disagreement():
    ev = [{"id": f"x{i}", "ts": T0, "quote": "q"} for i in range(20)]
    lab1 = {f"x{i}": (["B1"] if i % 2 else ["C"]) for i in range(20)}
    lab2 = {f"x{i}": (["S"] if i % 2 else ["C"]) for i in range(20)}   # opportunity flips on half
    a = lb.agreement(ev, lab1, lab2)
    assert a["kappa_opp"] < 0.6
    res = lb.analyze(synth((0.6, 0.1), 50), a)
    assert res["verdict"] == "rule not operational"


# ---------------------------------------------------------------- mechanics

def test_bare():
    assert lb.is_bare("yes and yes") and lb.is_bare("Yes, that matches") and lb.is_bare("1")
    assert not lb.is_bare("everyone counts") and not lb.is_bare("") and not lb.is_bare("yeah add both now ok")


def test_kappa_perfect_and_chance():
    assert lb.kappa([1, 0, 1, 0], [1, 0, 1, 0]) == 1.0
    assert lb.kappa([1, 1, 0, 0], [1, 0, 1, 0]) == 0.0


def test_sessions_split_on_gap():
    ev = [{"id": "a", "ts": T0}, {"id": "b", "ts": T0 + timedelta(minutes=59)},
          {"id": "c", "ts": T0 + timedelta(minutes=59 + 61)}]
    assert lb.sessions(ev) == {"a": 1, "b": 1, "c": 2}


def test_pass_numbers():
    items = [{"event": "a", "kind": "B1", "topic": "t", "quote": "", "ts": T0},
             {"event": "b", "kind": "S", "topic": None, "quote": "", "ts": T0},
             {"event": "c", "kind": "C", "topic": "t", "quote": "", "ts": T0}]
    opp = lb.opportunity_items(items)
    assert [it["pass"] for it in opp] == [1, 2]


def test_real_logs_fully_labeled_and_deduped():
    events = lb.load_events()
    ids = [e["id"] for e in events]
    assert len(ids) == len(set(ids))
    items = lb.attach(events, lb.LABELS, lb.TOPICS)   # raises if any event lacks a label
    assert set(lb.LABELS) >= set(ids)
    assert all(len(lb.TOPICS[e]) == len(lb.LABELS[e]) for e in lb.TOPICS)
    opp = [it for it in items if it["kind"] in lb.OPPORTUNITY]
    assert all(it["topic"] is not None for it in opp)


def test_nwim_rows_are_corrections():
    """Every changes row flagged not_what_i_meant is labeled as a loop b correction (rule B1 / T2)."""
    for e in lb.load_events():
        if e.get("nwim"):
            assert any(k in lb.CORRECTION for k in lb.LABELS[e["id"]]), e["id"]
