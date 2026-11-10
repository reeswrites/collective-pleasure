"""Negotiated pots (docs/results/negotiation-prereg.md): protocol, unanimity, outside option, cards, proof rejection."""
from itertools import combinations
from pathlib import Path

import pytest

from mar import negotiation as N
from mar import personas as P
from mar.cards import make_card
from mar.worlds import household as H

ROOT = Path(__file__).parent.parent / "personas"
PERS = {p.id: p for p in P.load_dir(ROOT) + P.load_dir(ROOT / "pressing")}
BIND = "author_seed_v2_bindable"
PAIRS = list(combinations(sorted(PERS), 2))


def table(*ids):
    return [PERS[i] for i in ids]


def test_menu_is_small_finite_and_documented():
    assert set(N.TERMS) == {"contribution", "use", "taking", "change", "exit", "stay", "requests"}
    assert len(N.bundles()) == 3 ** 5 * 2 * 2 and len(N.bundles(False, False)) == 3 ** 5
    assert all(len(v) >= 2 for v in N.TERMS.values())


@pytest.mark.parametrize("seed", (0, 1, 2))
def test_protocol_terminates_within_the_deadline_and_agreement_is_unanimous_and_beats_outside_options(seed):
    for a, b in PAIRS:
        r = N.negotiate(table(a, b), BIND, seed)
        assert r.status in ("agreed", "deadline", "no_bundle") and len(r.proposals) <= N.DEADLINE
        if r.agreed:
            last = r.proposals[-1]
            assert last["outcome"] == "agreed" and not last["rejected_by"] and sorted(last["accepted_by"]) == sorted(r.members)
            for i, pid in enumerate(r.members):               # every member's value of the agreed bundle beats its outside option
                assert N.utility(PERS[pid], r.bundle, low=i > 0) > N.outside_option(PERS[pid])
            assert N.proof_check(N.base_cards(BIND) + r.cards)["ok"]    # no agreement stands without passing the proof checks


def test_negotiation_is_deterministic_and_the_seed_only_changes_the_turn_order():
    a = N.negotiate(table("p-anchor", "p-host"), BIND, 1)
    b = N.negotiate(table("p-anchor", "p-host"), BIND, 1)
    assert (a.status, a.bundle, [p["proposer"] for p in a.proposals]) == (b.status, b.bundle, [p["proposer"] for p in b.proposals])


def test_a_member_with_a_better_outside_option_than_any_pot_blocks_the_agreement_and_no_pot_forms(monkeypatch):
    # the frozen proxy never gives a persona an outside option above every bundle, so the better option is planted
    best = max(N.utility(PERS["p-wanderer"], b, low=True) for b in N.bundles())
    real = N.outside_option
    monkeypatch.setattr(N, "outside_option", lambda p: best + 1.0 if p.id == "p-wanderer" else real(p))
    r = N.negotiate([PERS["p-anchor"], PERS["p-wanderer"]], BIND, 0)
    assert r.status == "no_bundle" and r.bundle is None and r.cards is None
    deal = N.world_deal(r)
    assert deal == {"pot": False, "commits": []}
    base = N.base_cards(BIND)
    assert N.living_cards(base, r) == base                    # no pot: members keep their own holdings, nothing is imposed
    monkeypatch.setattr(N, "outside_option", real)
    assert N.negotiate([PERS["p-anchor"], PERS["p-wanderer"]], BIND, 0).agreed


def test_proposals_are_never_below_the_proposers_own_outside_option():
    for a, b in PAIRS[:12]:
        r = N.negotiate(table(a, b), BIND, 0)
        for p in r.proposals:
            i = r.members.index(p["proposer"])
            assert N.utility(PERS[p["proposer"]], p["bundle"], low=i > 0) > N.outside_option(PERS[p["proposer"]])


def test_every_term_value_compiles_to_cards_with_gloss_source_and_an_english_round_trip():
    seen = set()
    for b in N.bundles():
        for t in N.TERM_NAMES:
            if (t, b[t]) not in seen:
                seen.add((t, b[t]))
                for c in N.compile_bundle(b, ["p-anchor", "p-host"]):
                    assert c.gloss and c.source == "negotiated, week 0, members p-anchor,p-host"
                    assert H.parse_card(H.render_card(c)) == c
    assert len(seen) == sum(len(v) for v in N.TERMS.values())


def test_compiled_cards_have_the_intended_effect_in_the_gate():
    base = N.base_cards(BIND)
    b = dict(contribution="none", use="needs_only", taking="forbidden", change="unanimous", exit="equal_split", stay=0, requests="none")
    g = H.PyGate(base + N.compile_bundle(b, ["a", "b"]))
    st = {n: 0 for n in H.STATE_VARS}
    assert not g.check("partner", "take_shared", st)[0]                  # taking another's share forbidden
    assert g.check("partner", "leave", {**st, "pooled": 40}, take=50)[0]
    assert not g.check("partner", "leave", {**st, "pooled": 40}, take=100)[0]
    assert g.check("partner", "spend_self", {**st, "need_gap": 4})[0]    # contribution none: no duty
    b2 = dict(b, contribution="fixed", taking="allowed", use="any_use")
    g2 = H.PyGate(base + N.compile_bundle(b2, ["a", "b"]))
    assert not g2.check("partner", "spend_self", {**st, "need_gap": 4})[0] and g2.check("partner", "take_shared", st)[0]


def test_a_three_member_pot_can_form_and_its_cards_name_all_three_members():
    r = N.negotiate(table("p-anchor", "p-peacekeeper", "p-overasker"), BIND, 0)
    assert len(r.members) == 3 and r.roles == ["A", "B", "C"]
    assert r.agreed
    assert all(c.source == "negotiated, week 0, members p-anchor,p-peacekeeper,p-overasker" for c in r.cards)
    assert "p-anchor, p-peacekeeper and p-overasker" in r.cards[0].gloss
    assert N.world_deal(r) == {"pot": False, "commits": []}          # 3-member pots are negotiated and checked, not lived (stated limit)


def test_the_proof_filter_rejects_a_planted_forfeit_exit_and_a_planted_conflict():
    base = N.base_cards(BIND)
    b = dict(contribution="none", use="needs_only", taking="forbidden", change="propose_accept", exit="forfeit", stay=0, requests="none")
    pc = N.proof_check(base + N.compile_bundle(b, ["a", "b"]))
    assert not pc["ok"] and "e_exit_within_k" in [f["check"] for f in pc["fails"]]
    assert "N5a-exit-forfeit" in [i for f in pc["fails"] for i in f["cards"]]
    frozen = N.proof_check(base + N.compile_bundle(dict(b, change="frozen"), ["a", "b"]))
    assert "f_change_or_exit" in [f["check"] for f in frozen["fails"]]
    ok = N.proof_check(base + N.compile_bundle(dict(b, exit="equal_split", change="frozen"), ["a", "b"]))
    assert ok["ok"]                                                    # frozen is fine when members can still leave with something
    clash = [make_card({"id": "X1", "attribute": "partner", "deontic": "must", "aim": "take_shared", "conditions": [], "or_else": None,
                        "gloss": "Taking is required.", "source": "planted"}),
             make_card({"id": "X2", "attribute": "partner", "deontic": "must_not", "aim": "take_shared", "conditions": [], "or_else": None,
                        "gloss": "Taking is forbidden.", "source": "planted"})]
    assert "a_no_conflict" in [f["check"] for f in N.proof_check(base + N.compile_bundle(dict(b, exit="equal_split"), ["a", "b"]) + clash)["fails"]]


def test_a_rejected_agreement_is_logged_with_its_reason_and_the_trap_is_never_proposed_again(monkeypatch):
    monkeypatch.setitem(N.TERMS, "exit", ("equal_split", "forfeit"))
    # Anchor and peacekeeper both value a lock-in exit; whichever bundle everyone accepts, a forfeit exit must be caught
    monkeypatch.setattr(N, "_raw", _forfeit_lover(N._raw))
    N._UCACHE.clear()
    r = N.negotiate(table("p-anchor", "p-peacekeeper"), BIND, 0)
    N._UCACHE.clear()
    assert r.rejections, "the planted trap was not proposed"
    rej = r.rejections[0]
    assert rej["bundle"]["exit"] == "forfeit" and "e_exit_within_k" in rej["failed"]
    assert any("every way out" in t or "no exit" in t or "leave" in t for t in rej["checks"])
    after = [p for p in r.proposals if p["k"] > rej["k"]]
    assert all(p["bundle"]["exit"] != "forfeit" for p in after)         # the combination was banned
    assert r.agreed is False or r.bundle["exit"] != "forfeit"


def _forfeit_lover(orig):
    def raw(p, low):
        d = orig(p, low)
        d["exit"]["forfeit"] += 5.0                                      # make forfeit overwhelmingly attractive to everyone (a planted trap)
        return d
    return raw


def test_a_rejection_that_leaves_no_agreeable_bundle_ends_with_no_pot(monkeypatch):
    monkeypatch.setitem(N.TERMS, "exit", ("forfeit",))
    N._UCACHE.clear()
    r = N.negotiate(table("p-anchor", "p-peacekeeper"), BIND, 0)
    N._UCACHE.clear()
    assert r.status in ("no_bundle", "deadline") and r.bundle is None and r.rejections
    assert N.world_deal(r)["pot"] is False


def test_commitments_are_on_the_menu_only_where_the_base_rules_allow_them():
    assert N.menu_of(N.base_cards("author_seed_v2_bindable")) == {"stay": True, "requests": True}
    assert N.menu_of(N.base_cards("author_seed_v2_free_exit")) == {"stay": False, "requests": True}
    assert N.menu_of(N.base_cards("author_seed_v2_nocommit")) == {"stay": False, "requests": False}
    for v, k, off in (("author_seed_v2_free_exit", "stay", 0), ("author_seed_v2_nocommit", "requests", "none")):
        for a, b in PAIRS[:10]:
            r = N.negotiate(table(a, b), v, 0)
            assert not r.agreed or r.bundle[k] == off


def test_stub_exit_terms_are_replaced_not_stacked():
    ids = [c.id for c in N.base_cards(BIND)]
    assert "R8b-exit-terms-not-less" not in ids and "R8a-may-leave" in ids and "R3b-pot-no-take" not in ids


# ---- the weekly world at week 0 ----
def lived(a, b, seed=0, weeks=20, **kw):
    r = N.negotiate(table(a, b), BIND, seed)
    cards = N.living_cards(N.base_cards(BIND), r)
    return r, H.WeeklyWorld(cards, (PERS[a], PERS[b]), seed, weeks, deal=N.world_deal(r), **kw)


def test_the_negotiated_deal_replaces_the_commitment_stub_and_the_agreed_terms_are_lived():
    r, w = lived("p-anchor", "p-peacekeeper")
    assert r.agreed and r.bundle["stay"] == 52 and w.pot
    assert sorted((c["kind"], c["by"]) for c in w.commits) == [("requests", "A"), ("requests", "B"), ("stay", "A"), ("stay", "B")]
    assert all(c["until"] == 52 for c in w.commits)
    w.units = {"A": 10, "B": 10}
    assert w.decide("A", "take_shared", 0)[0] == "hard"            # the negotiated "taking forbidden" is a wall
    assert w.decide("A", "leave", 60, take=50)[0] == "ok" and w.decide("A", "leave", 60, take=100)[0] == "hard"   # negotiated exit: half
    w.play()


def test_no_pot_means_own_holdings_no_pooled_share_and_nothing_to_take():
    w = H.WeeklyWorld(N.base_cards(BIND), (PERS["p-freerider"], PERS["p-host"]), 0, 30, deal={"pot": False, "commits": []})
    assert not w.pot and (w.p["A"]["money"], w.p["A"]["pooled"]) == (H.NO_POT_MONEY, 0) and w.commits == []
    w.wk = {r: {"took": 0} for r in "AB"}
    w.units = {"A": 10, "B": 10}
    assert not w.feasible("A", "take_shared")
    run = w.play()
    assert all(t["action"] != "take_shared" for t in run.trace)


def test_default_world_is_unchanged_without_a_deal_and_breach_forfeit_one_is_the_seed_v2_value():
    cards = H.load_variant(BIND)
    a = H.run_weekly(cards, (PERS["p-anchor"], PERS["p-peacekeeper"]), 0, 40)
    b = H.run_weekly(cards, (PERS["p-anchor"], PERS["p-peacekeeper"]), 0, 40, breach_forfeit=1.0)
    assert a.outcomes == b.outcomes and a.meta == b.meta


def test_a_partial_breach_forfeit_lets_the_leaver_keep_part_of_the_share():
    r, w = lived("p-anchor", "p-peacekeeper", breach_forfeit=0.5)
    assert w.breach("A", "leave", 3, {"a": "leave", "take": 100})["take"] == 50
    assert w.breach("A", "leave", 3, {"a": "leave", "take": 25})["take"] == 25
