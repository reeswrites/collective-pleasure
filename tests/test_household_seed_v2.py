"""Seed v2 (docs/results/household-seed-v2-prereg.md): cards, give, negotiation stub, commitments, breach."""
from itertools import product
from pathlib import Path

import pytest

from mar import empowerment as E
from mar import personas as P
from mar.worlds import household as H

ROOT = Path(__file__).parent.parent / "personas"
PERS = {p.id: p for p in P.load_dir(ROOT) + P.load_dir(ROOT / "pressing")}
V2 = H.SEED_V2_VARIANTS
BIND, FREE = "author_seed_v2_bindable", "author_seed_v2_free_exit"


def world(variant, a, b, seed=0, weeks=156):
    return H.WeeklyWorld(H.load_variant(variant), (PERS[a], PERS[b]), seed, weeks)


def fresh(w):
    w.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0, "friend_initiated": 0,
                "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0, "pressed": 0, "took": 0} for r in "AB"}
    w.units = {"A": 10, "B": 10}
    return w


# ---- cards ----
@pytest.mark.parametrize("variant", V2)
def test_cards_have_gloss_source_round_trip_and_pass_checks(variant):
    cards = H.load_variant(variant)
    assert all(c.gloss and c.source for c in cards)
    assert all(H.parse_card(H.render_card(c)) == c for c in cards)
    assert all(v["verdict"] == "pass" for v in H.check_spec(cards))


def test_the_eight_rules_carry_the_authors_read_back_sentences_and_cite_the_seed():
    cards = {c.id: c for c in H.load_variant(BIND)}
    assert cards["R1-may-keep"].gloss == "A partner may keep their own money and things."
    assert cards["R2-may-give"].gloss == "A partner may give or trade anything they own to anyone, on any terms both accept."
    assert cards["R3a-pot-use"].gloss.startswith("Anything in the shared pot belongs to both: either may draw from it for any use unless")
    assert cards["R3a-pot-use"].aim == "take_shared" and cards["R3a2-pot-put"].aim == "spend_shared"     # formal fields match the gloss
    assert "shared needs" not in cards["R3a-pot-use"].gloss and "\"1\"" in cards["R3a-pot-use"].source
    assert cards["R4-may-ask"].gloss == "A partner may ask the other for anything."
    assert cards["R5-may-refuse"].gloss.startswith("A partner may always refuse a request, unless they earlier chose to bind")
    assert cards["R6-no-veto"].gloss == "A partner must not veto the other's contact, money or time, except through a commitment the other chose."
    assert cards["R7-may-see"].gloss == "A partner may always see anyone."
    assert cards["R8a-may-leave"].gloss == "A partner may leave whenever they like."
    assert all("author-household-norms-2026-11-10.md" in c.source for c in cards.values())


def test_variants_differ_only_in_the_stay_commitment_card():
    b = {c.id: c for c in H.load_variant(BIND)}
    f = {c.id: c for c in H.load_variant(FREE)}
    assert set(b) - set(f) == {"R8d-may-commit-stay"} and set(f) - set(b) == {"R8d-no-commit-stay"}
    assert f["R8d-no-commit-stay"].deontic == "must_not" and f["R8d-no-commit-stay"].or_else is None


def states():
    for pooled, ncr, shr, cons, gap in product((0, 40), (0, 1), (0, 1), (0, 1), (0, 4)):
        yield {"pooled": pooled, "money": 5, "other_earns_more": 0, "no_contact_request": ncr, "stay_home_request": shr,
               "consented": cons, "need_gap": gap, "months_in": 3, "other_in": 1}


@pytest.mark.parametrize("variant", V2)
def test_pygate_matches_z3_gate_on_the_new_aims_too(variant):
    cards = H.load_variant(variant)
    z, py = H.HouseholdGate(cards), H.PyGate(cards)
    for s in states():
        for a in H.PARTNER_ACTIONS + H.EXTRA_ACTIONS + ("veto", "take_shared", "rest", "together"):
            for take in ((0, 25, 50, 100) if a == "leave" else (0,)):
                if a in H.PARTNER_ACTIONS + H.EXTRA_ACTIONS:
                    assert z.check("partner", a, s, take) == py.check("partner", a, s, take)


def test_old_variants_do_not_use_the_new_mechanics_and_seed_v2_does():
    for v in H.V3_VARIANTS:
        assert not world(v, "p-anchor", "p-peacekeeper").mech
    for v in V2:
        assert world(v, "p-anchor", "p-peacekeeper").mech


# ---- R1 to R3: private holdings vs the shared pot ----
def test_pot_terms_are_not_imposed_by_the_seed_and_vetoes_are_walls():
    w = fresh(world(BIND, "p-controller", "p-host"))
    assert w.decide("A", "take_shared", 0)[0] == "ok"          # v2.1: R3b removed; taking is whatever the members negotiate
    assert "R3b-pot-no-take" not in {c.id for c in H.load_variant(BIND)}
    assert w.decide("A", "spend_shared", 0)[0] == "ok"          # R3a
    assert w.decide("A", "veto", 0)[0] == "hard"                # R6
    assert w.decide("A", "spend_self", 0)[0] == "ok" and w.decide("A", "see_friend", 0)[0] == "ok"   # R1, R7


# ---- R2: give ----
def test_give_moves_private_money_to_the_partner_or_the_friend_and_a_card_can_forbid_it():
    w = fresh(world(BIND, "p-anchor", "p-host"))
    w.p["A"]["money"], w.p["B"]["money"] = 10, 2
    assert w.feasible("A", "give", "partner") and w.feasible("A", "give", "friend") and not w.feasible("A", "give", "x")
    assert w.decide("A", "give", 0)[0] == "ok"
    w.apply("A", {"a": "give", "kind": "partner"}, 0, [])
    assert (w.p["A"]["money"], w.p["B"]["money"], w.units["A"]) == (7, 5, 9) and w.gifts["partner"] == 3
    w.apply("A", {"a": "give", "kind": "friend"}, 0, [])
    assert w.p["A"]["money"] == 4 and w.gifts["friend"] == 3 and w.p["B"]["money"] == 5
    w.p["A"]["money"] = 3
    assert not w.feasible("A", "give", "partner")               # needs money above the gift
    from mar.cards import make_card
    ban = make_card({"id": "X", "attribute": "partner", "deontic": "must_not", "aim": "give", "conditions": [], "or_else": None,
                     "gloss": "No gifts.", "source": "test"})
    w2 = fresh(H.WeeklyWorld(H.load_variant(BIND) + [ban], (PERS["p-anchor"], PERS["p-host"])))
    assert w2.decide("A", "give", 0)[0] == "hard"
    assert not world("baseline", "p-anchor", "p-host").mech


def test_a_generous_persona_gives_to_a_partner_who_is_short():
    w = fresh(world(BIND, "p-anchor", "p-host"))
    w.p["A"]["money"], w.p["B"]["money"] = 12, 1
    o = w.obs("A", 0, {"busy": {"A": False, "B": False}})
    assert o["mech"] and o["partner_money"] == 1
    acts = [c["a"] + str(c.get("kind")) for _, c in w.agents["A"].propose(o)]
    assert "givepartner" in acts
    w.p["B"]["money"] = 9
    o = w.obs("A", 0, {"busy": {"A": False, "B": False}})
    assert "givepartner" not in [c["a"] + str(c.get("kind")) for _, c in w.agents["A"].propose(o)]


# ---- negotiation stub ----
def test_persona_proposals_and_acceptance_are_fixed_by_the_profile():
    assert P.commitment_proposal(PERS["p-anchor"]) == {"stay": 52, "requests": "stay_home"}
    assert P.commitment_proposal(PERS["p-peacekeeper"]) == {"stay": 52, "requests": None}      # accommodating: stay only
    for pid in ("p-wanderer", "p-bargainer", "p-steward", "p-freerider"):
        assert P.commitment_proposal(PERS[pid]) == {"stay": 0, "requests": None}                # autonomy-seeking: nothing
    assert P.accepts_commitment(PERS["p-peacekeeper"], "requests") and not P.accepts_commitment(PERS["p-host"], "requests")
    assert P.accepts_commitment(PERS["p-host"], "stay") and not P.accepts_commitment(PERS["p-wanderer"], "stay")
    assert not P.accepts_commitment(PERS["p-controller"], "stay")


def test_a_commitment_is_made_only_if_both_accept_and_the_rules_permit():
    b = world(BIND, "p-anchor", "p-peacekeeper")
    assert sorted((c["kind"], c["by"]) for c in b.commits) == [("requests", "B"), ("stay", "A"), ("stay", "B")]
    assert all(c["until"] == 52 for c in b.commits)
    assert [c["kind"] for c in world(FREE, "p-anchor", "p-peacekeeper").commits] == ["requests"]     # exit cannot be signed away
    assert world("author_seed_v2_nocommit", "p-anchor", "p-peacekeeper").commits == []
    assert world(BIND, "p-anchor", "p-wanderer").commits == []                      # the other side declines
    assert world(BIND, "p-wanderer", "p-bargainer").commits == []                   # nobody proposes
    assert [c["kind"] for c in world(BIND, "p-controller", "p-host").commits] == ["stay", "stay"]   # host declines requests


# ---- stay commitments (bindable R8) ----
def test_a_stay_commitment_blocks_leaving_until_the_load_is_high_then_breach_forfeits_the_pot_share():
    w = fresh(world(BIND, "p-anchor", "p-peacekeeper"))
    assert w.decide("A", "leave", 3, take=50)[0] == "hard"                     # honored by default
    assert w.decide("A", "leave", 60, take=50)[0] == "ok"                      # R8 applies after it ends (exit terms)
    w.hed["A"].N = 0.25
    dec, _, reasons = w.decide("A", "leave", 3, take=100)
    assert dec == "breach" and "commitment: stay" in reasons[0]
    cand = w.breach("A", "leave", 3, {"a": "leave", "take": 100})
    assert cand["take"] == 0 and w.commit_report()["breached"] == 1
    w.apply("A", cand, 3, [])
    assert w.pool == 90 and w.p["A"]["money"] == 10 and not w.p["A"]["in"]      # breach: nothing is carried out, the whole pot stays


def test_free_exit_never_binds_leaving_and_exit_terms_hold():
    w = fresh(world(FREE, "p-anchor", "p-peacekeeper"))
    assert w.decide("A", "leave", 3, take=50)[0] == "ok" and w.decide("A", "leave", 3, take=100)[0] == "hard"   # half the pot each


def test_bound_stay_shows_the_breach_exit_to_the_probe_and_counts_as_trapped_only_when_unhappy():
    w = fresh(world(BIND, "p-anchor", "p-peacekeeper"))
    pr = w.probe("A", 3)
    assert pr["exit_retained"] == round(w.retained_fraction("A", 0), 4) < 0.25 and not pr["open"]["leave"]
    assert world(FREE, "p-anchor", "p-peacekeeper").probe("A", 3)["exit_retained"] > 0.5
    run = world(BIND, "p-anchor", "p-peacekeeper", weeks=30).play()
    assert all(o["hedonic"][r]["conditions"]["trapped"] is False for o in run.outcomes for r in "AB")    # content and bound: not trapped


# ---- request commitments (R5) ----
def test_a_request_commitment_forces_consent_binds_for_four_weeks_and_cannot_be_refused():
    w = fresh(world(BIND, "p-anchor", "p-peacekeeper"))
    w.apply("A", {"a": "request", "kind": "stay_home"}, 5, [])
    assert w.consent["B"] == 1 and w.bound_req["B"] == {"stay_home": 5 + H.BIND_WEEKS}
    for a in ("see_friend", "spend_self", "refuse_request"):
        assert w.decide("B", a, 6)[0] == "hard"
    assert w.decide("B", "work", 6)[0] == "ok" and w.decide("A", "see_friend", 6)[0] == "ok"
    assert w.decide("B", "see_friend", 9)[0] == "ok"                           # lapsed (first week it no longer binds)
    w2 = fresh(world(BIND, "p-anchor", "p-host"))                               # host did not choose to be bound
    w2.apply("A", {"a": "request", "kind": "stay_home"}, 5, [])
    assert w2.bound_req["B"] == {} and w2.decide("B", "see_friend", 6)[0] == "ok" and w2.decide("B", "refuse_request", 6)[0] == "ok"


def test_breaking_a_request_commitment_costs_the_agreed_fine():
    w = fresh(world(BIND, "p-anchor", "p-peacekeeper"))
    w.apply("A", {"a": "request", "kind": "stay_home"}, 5, [])
    w.hed["B"].N = 0.3
    assert w.decide("B", "see_friend", 6)[0] == "breach"
    before = (w.p["B"]["money"], w.p["A"]["money"])
    w.breach("B", "see_friend", 6, {"a": "see_friend"})
    assert (w.p["B"]["money"], w.p["A"]["money"]) == (before[0] - 3, before[1] + 3)
    rep = w.commit_report()
    assert rep["made"] == 3 and rep["breached"] == 1 and rep["honored"] == 2 and rep["by_kind"]["requests"]["breached"] == 1


def test_end_to_end_runs_report_commitments_and_free_exit_has_no_stay_breach():
    for v in (BIND, FREE):
        r = world(v, "p-controller", "p-peacekeeper", weeks=60).play()
        assert r.meta["made"] == len(r.meta["log"]) and r.meta["honored"] + r.meta["breached"] == r.meta["made"]
        assert (r.meta["by_kind"]["stay"]["made"] > 0) == (v == BIND)
    r = world("baseline", "p-anchor", "p-host", weeks=10).play()
    assert r.meta == {}


# ---- empowerment adapter ----
def test_empowerment_mirror_blocks_leaving_while_a_stay_commitment_binds():
    w = fresh(world(BIND, "p-anchor", "p-peacekeeper"))
    hw = E.HouseholdWorld()
    s = hw.snapshot(w, 0)
    assert s.stay == (52, 52)
    hw._spec = w.gate
    assert hw.decide(s, w.gate, 0, "leave", 50)[0] == "hard"
    free = fresh(world(FREE, "p-anchor", "p-peacekeeper"))
    assert hw.snapshot(free, 0).stay == (0, 0) and hw.initial().stay == (0, 0)
