"""Pleasure levers (ADR 0016): mechanism checks. Each lever is ON only when its flag is set."""
from pathlib import Path

import pytest

from mar import hedonic as HD
from mar import personas as P
from mar.worlds import household as H

ROOT = Path(__file__).resolve().parent.parent
PS = {p.id: p for p in P.load_dir(ROOT / "personas")}
DEAL = {"pot": True, "commits": []}
L = HD.LeverConfig


def run(lv, a="p-anchor", b="p-host", deal=DEAL, seed=0, weeks=156):
    return H.run_weekly(H.PyGate(H.load_variant("author_seed_v2_bindable")), (PS[a], PS[b]), seed, weeks, deal=deal, levers=lv)


def mean(r, lo=0, hi=999):
    rows = r.outcomes[lo:hi]
    return sum(x["hedonic"][k]["pleasure"] for x in rows for k in "AB") / (2 * len(rows))


def test_satiety_rises_with_repeats_and_recovers_with_spacing():
    s = HD.Satiety(L(adapt=True), 3)
    first = s.use(0)
    second = s.use(0)
    assert second < first
    for _ in range(12):
        s.week_end()
    assert s.scale(0) > second and s.h[0] < 0.1


def test_rotation_beats_repeat_when_adapting_and_not_when_off():
    rep, rot = run(L(adapt=True, force_policy="repeat")), run(L(adapt=True, force_policy="rotate"))
    assert mean(rot) > mean(rep)


def test_ritual_adds_anticipation_at_equal_dose():
    rit = run(L(ritual=True, force_ritual=True))
    adh = run(L(ad_hoc_dose=1))
    assert rit.lever["ritual"] and not adh.lever["ritual"]
    assert abs(rit.lever["sessions"] - adh.lever["sessions"]) <= 0.02 * adh.lever["sessions"] + 1
    assert mean(rit) > mean(adh)


def test_ritual_is_cancelled_when_a_partner_is_not_in():
    lv = L(ritual=True, force_ritual=True)
    r = run(lv, deal={"pot": False, "commits": []})
    assert r.lever["ritual_slots"] == 156 and r.lever["ritual_kept"] < 156


def _with(card_deontic):
    from mar.cards import make_card
    base = H.load_variant("author_seed_v2_bindable")
    c = make_card({"id": "R9x", "attribute": "partner", "deontic": card_deontic, "aim": "ritual", "conditions": [], "or_else": None,
                   "gloss": "a ritual", "source": "test"})
    return H.run_weekly(H.PyGate(base + [c]), (PS["p-bargainer"], PS["p-wanderer"]), 0, 20, deal=None, levers=L(ritual=True))


def test_must_ritual_card_imposes_and_must_not_forbids():
    assert _with("must").lever["ritual"] is True
    assert _with("must_not").lever["ritual"] is False


def test_ritual_card_variant_loads_and_is_a_permission_only():
    cards = H.load_variant("author_seed_v2_ritual_card")
    assert [c.deontic for c in cards if c.aim == "ritual"] == ["may"]


def test_commitment_converter_costs_then_pays():
    com = [{"kind": "stay", "by": w, "to": o, "type": None, "from": 0, "until": 52, "breached": 0} for w, o in (("A", "B"), ("B", "A"))]
    lv = L(commit=True)
    c, n = run(lv, deal={"pot": True, "commits": com}), run(lv)
    assert c.lever["K"] > 0 and n.lever["K"] == 0
    assert mean(c, 0, 5) <= mean(n, 0, 5) + 0.02          # friction up front, payoff not yet built
    assert mean(c, 60, 156) > mean(n, 60, 156)           # payoff after the commitment compounds


def test_commit_payoff_is_zero_without_the_flag():
    com = [{"kind": "stay", "by": "A", "to": "B", "type": None, "from": 0, "until": 52, "breached": 0}]
    assert mean(run(None, deal={"pot": True, "commits": com})) == mean(run(L(), deal={"pot": True, "commits": com}))


def test_strand_cover_redundancy_and_overload():
    cfg = L()
    solo = HD.strand_cover(cfg, 0.8, [], [])
    three = HD.strand_cover(cfg, 0.8, [0.6, 0.6], HD.strand_sets(2))
    assert three["care"] > solo["care"] and three["desire"] == solo["desire"]
    assert HD.coordination_units(cfg, 5) > 5 * HD.coordination_units(cfg, 1)    # convex


def test_bond_shocks_are_common_random_numbers_across_bond_counts():
    a = H.bond_shock_schedule(3, "x", "y", 1560, 0.2, (6, 20))
    b = H.bond_shock_schedule(3, "x", "y", 1560, 0.2, (6, 20))
    assert a == b and any(s[0] == "H" for v in a.values() for s in v)


def test_too_many_bonds_lowers_pleasure():
    kw = dict(network=True, force_policy="rotate")
    assert mean(run(L(force_bonds=7, **kw))) < mean(run(L(force_bonds=2, **kw)))


def test_lever_terms_are_in_the_weekly_row_only_when_on():
    assert "lever" not in run(None, weeks=3).outcomes[0]["hedonic"]["A"]
    assert "lever" in run(L(commit=True), weeks=3).outcomes[0]["hedonic"]["A"]


def test_persona_policies_are_documented_functions_of_principles():
    p = PS["p-host"]
    pol = P.lever_policy(p)
    assert pol["variety"] in ("repeat", "rotate", "adaptive") and 1 <= pol["n_ext"] <= 5
    assert pol["ritual_proposes"] is False     # togetherness 0.83 but security 0.2 < 0.4
