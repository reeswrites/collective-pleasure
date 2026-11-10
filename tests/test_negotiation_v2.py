"""Negotiation v2 (docs/results/negotiation-v2-prereg.md): exit floor, real outside options, reviews, start arms, inertia."""
from pathlib import Path

import pytest

from mar import negotiation as N
from mar import personas as P
from mar.worlds import household as H

ROOT = Path(__file__).parent.parent / "personas"
PERS = {p.id: p for p in P.load_dir(ROOT) + P.load_dir(ROOT / "pressing")}
BIND = "author_seed_v2_bindable"
BASE = N.base_cards(BIND)


def b(**kw):
    return {**N.FAIR_DEFAULT, **kw}


# ---- the floor ----
def test_floor_is_thirteen_weeks_of_the_models_living_cost():
    assert N.FLOOR == 13 * HD_LIVING() == 26


def HD_LIVING():
    from mar import hedonic
    return hedonic.DEFAULT.living_cost


def test_floor_blocks_below_floor_deals_and_passes_above_floor_ones():
    hold = {"A": N.START_HOLDINGS, "B": N.START_HOLDINGS}              # money 10, equal half of the one pot 45
    assert N.floor_check(b(), hold)["ok"]                                # equal split carries half the pot: 10 + 45 = 55
    assert N.floor_check(b(exit="proportional"), hold)["ok"]
    forfeit = N.floor_check(b(exit="forfeit"), hold)
    assert not forfeit["ok"] and forfeit["fails"][0]["retained"] == 10 and forfeit["fails"][0]["needed"] == 26
    full = N.floor_check(b(stay=52, breach=1.0), hold)                  # the v1 stay commitment: a breach forfeits the whole share
    assert not full["ok"] and {f["path"] for f in full["fails"]} == {"breach"}
    assert N.floor_check(b(stay=52, breach=0.5), hold)["ok"]            # forfeiting half still leaves 10 + 22 = 32: above the floor
    assert N.floor_check(b(stay=52, breach=0.0), hold)["ok"]


def test_floor_cannot_dead_lock_a_review_once_holdings_are_below_the_floor():
    poor = {"A": (4, 10), "B": (4, 10)}                                  # even the most generous exit carries 14 < 26
    assert N.floor_check(b(exit="proportional"), poor)["ok"]
    assert not N.floor_check(b(exit="forfeit"), poor)["ok"]              # but a worse exit than the best is still blocked


def test_the_floor_blocks_an_all_accepted_agreement_and_an_above_floor_consented_stay_is_flagged_not_blocked():
    off = N.week0(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE, floor=False)
    on = N.week0(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE, floor=True)
    hold = {"A": N.START_HOLDINGS, "B": N.START_HOLDINGS}
    assert off.pot and not N.floor_check(off.bundle, hold)["ok"]         # without the floor, a below-floor stay deal was agreed
    assert on.floor_blocks and any(f["path"] == "breach" for blk in on.floor_blocks for f in blk["fails"])
    assert on.pot and N.floor_check(on.bundle, hold)["ok"]
    assert on.bundle["stay"] == 52 and on.bundle["breach"] < 1.0         # a consented stay commitment above the floor stands
    assert on.flagged and N.v1_flag(on.bundle, BASE)                     # and is flagged: v1's exit-within-k check would have failed it
    assert not N.v1_flag(b(), BASE)                                      # the plain fair default is not flagged
    assert N.v1_flag(b(exit="forfeit"), BASE)


def test_a_floor_cleared_stay_commitment_is_lived_with_its_breach_cost():
    on = N.week0(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE)
    L = N.Lived(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE, on, weeks=20)
    assert sorted(c["kind"] for c in L.world.commits).count("stay") == 2 and L.world.breach_forfeit == on.bundle["breach"]


# ---- real outside options ----
def test_outside_option_rollouts_are_deterministic_and_cached():
    p = PERS["p-wanderer"]
    N._RC.clear()
    h0, r0 = N.STATS["hits"], N.STATS["rollouts"]
    v1 = N.alone_value(p, "B", 55, 1, "alone")
    assert N.STATS["rollouts"] == r0 + 1
    v2 = N.alone_value(p, "B", 55, 1, "alone")
    assert v1 == v2 and N.STATS["hits"] == h0 + 1 and N.STATS["rollouts"] == r0 + 1     # second call is a cache hit
    N._RC.clear()
    assert N.alone_value(p, "B", 55, 1, "alone") == v1                                   # recomputed: same value (deterministic)
    assert N.alone_value(p, "B", 30, 1, "alone") != v1                                   # holdings are in the key and matter


def test_outside_option_is_the_better_of_alone_and_with_the_friend():
    for pid in ("p-anchor", "p-wanderer", "p-host"):
        v, d = N.outside_value(PERS[pid], "A", 55, 0)
        assert v == max(d.values()) and set(d) == {"alone", "friend"}


def test_friend_arrangement_is_cheaper_than_living_alone_in_the_world():
    def money_after(mode):
        w = H.WeeklyWorld(N._solo_cards(), (PERS["p-host"], PERS["p-host"]), 0, 1, deal={"pot": False, "commits": []})
        for x in "AB":
            w.p[x]["in"] = False
        w.solo = mode
        w.hed["A"].level["connection"] = 0.3
        w.play()
        return w.p["A"]["money"], w.hed["A"].level["connection"]
    assert money_after("friend")[0] > money_after("alone")[0] - 7     # no extra 1.5 cost for living apart (work income differs by seed noise only)


# ---- start arms and inertia ----
def test_inertia_rate_on_a_hand_case():
    d = dict(N.FAIR_DEFAULT)
    assert N.inertia(d)[0] == 1.0
    two_off = dict(d, taking="forbidden", exit="proportional")
    rate, same = N.inertia(two_off)
    assert rate == pytest.approx(5 / 7) and not same["taking"] and not same["exit"] and same["contribution"]
    assert N.inertia(dict(d, stay=52, breach=0.5, requests="mutual", use="caps", change="frozen", contribution="fixed", taking="repay", exit="forfeit"))[0] == 0.0
    assert N.inertia(dict(d, breach=0.5))[0] == 1.0       # breach is not one of the seven terms


def test_fair_default_arm_stands_by_consent_when_nobody_prefers_a_change():
    r = N.week0(PERS["p-freerider"], PERS["p-peacekeeper"], "fair_default", 2, BASE)      # the only stood table of 108 (3 seeds x 36 pairs)
    assert r.status == "stood" and r.bundle == N.FAIR_DEFAULT and not r.changed
    assert all(p["outcome"] in ("pass", "refused") for p in r.proposals) and N.inertia(r.bundle)[0] == 1.0


def test_wants_first_states_each_ideal_before_any_proposal_and_round_one_is_the_pure_ideal():
    r = N.week0(PERS["p-anchor"], PERS["p-host"], "wants_first", 0, BASE)
    assert set(r.stated) == {"p-anchor", "p-host"}
    for p in r.proposals[:2]:
        assert p["bundle"] == r.stated[p["proposer"]] or p["bundle"] is None


def test_wants_fallback_fixes_uncared_terms_at_the_default_and_stays_within_stated_values():
    for a, c in (("p-anchor", "p-host"), ("p-controller", "p-peacekeeper"), ("p-freerider", "p-host")):
        r = N.week0(PERS[a], PERS[c], "wants_fallback", 0, BASE)
        for prop in r.proposals:
            if prop["bundle"]:
                for t in N.TERM_NAMES:
                    stated_vals = {r.stated[m][t] for m in r.stated if r.stated[m] and t in r.cared[m]}
                    assert prop["bundle"][t] in stated_vals | {N.FAIR_DEFAULT[t]}
    assert N.salient(PERS["p-host"]) < N.salient(PERS["p-wanderer"])        # salience threshold: the Wanderer cares about more terms


def test_proposer_order_is_seeded():
    first = {s: N.week0(PERS["p-anchor"], PERS["p-host"], "wants_first", s, BASE).proposals[0]["proposer"] for s in range(8)}
    assert set(first.values()) == {"p-anchor", "p-host"}                     # randomized by seed across seeds
    assert N.week0(PERS["p-anchor"], PERS["p-host"], "wants_first", 3, BASE).proposals[0]["proposer"] == first[3]    # and repeatable


# ---- renegotiation ----
def test_reviews_every_13_weeks_while_both_are_in_and_unchanged_terms_continue():
    r = N.week0(PERS["p-anchor"], PERS["p-host"], "wants_fallback", 0, BASE)
    L = N.Lived(PERS["p-anchor"], PERS["p-host"], "wants_fallback", 0, BASE, r, weeks=60)
    L.play()
    assert [x["week"] for x in L.log] == [13, 26, 39, 52]
    start = dict(r.bundle)
    unchanged = [x for x in L.log if not x["changed"]]
    assert unchanged and all(x["to"] == x["from"] for x in unchanged)
    assert L.log[0]["from"] == start


def test_a_stay_commitment_expires_at_a_review_unless_renewed():
    on = N.week0(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE)
    L = N.Lived(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE, on, weeks=30)
    assert on.bundle["stay"] == 52
    N._apply_terms(L.world, BASE, on.bundle, 13, ["p-controller", "p-peacekeeper"], renew=False)
    assert all(c["until"] <= 13 for c in L.world.commits if c["kind"] == "stay") and not L.world.stay_bound("A", 14)
    N._apply_terms(L.world, BASE, on.bundle, 26, ["p-controller", "p-peacekeeper"], renew=True)
    assert L.world.stay_bound("A", 27) and all(c["until"] == 26 + 52 for c in L.world.commits if c["kind"] == "stay" and c["until"] > 26)


def test_a_review_change_needs_the_floor_and_a_proof_check():
    r = N.week0(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE)
    L = N.Lived(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE, r, weeks=80)
    L.play()
    for x in L.log:
        if x["changed"]:
            assert N.proof_check(BASE + N.compile_bundle(x["to"], ["a", "b"]))["ok"]


def test_the_default_world_is_unchanged_by_the_solo_flag():
    cards = H.load_variant(BIND)
    a = H.run_weekly(cards, (PERS["p-anchor"], PERS["p-peacekeeper"]), 0, 30)
    w = H.WeeklyWorld(cards, (PERS["p-anchor"], PERS["p-peacekeeper"]), 0, 30)
    assert w.solo is None and a.outcomes == w.play().outcomes


# ---- the floor holds at the moment of leaving (amendment 1) ----
def _world(floor):
    w = H.WeeklyWorld(H.load_variant(BIND), (PERS["p-anchor"], PERS["p-host"]), 0, 5)
    w.floor_amount = floor
    return w


def test_a_leaver_always_carries_at_least_the_floor_when_their_half_of_the_pot_holds_it():
    w = _world(N.FLOOR)
    w.p["A"]["money"], w.pool = 3, 80                                   # one shared pot of 80: each member's equal half is 40
    assert w.carry_out("A", 0) == 23 and w.carry_out("A", 25) == 23 and w.carry_out("A", 50) == 40
    assert w.carry_out("A", 100) == 80                                  # no cap but the pot: a negotiated term may let a leaver carry more
    w.p["A"]["money"] = 30
    assert w.carry_out("A", 0) == 0                                     # already above the floor
    w.p["A"]["money"], w.pool = 3, 20
    assert w.carry_out("A", 0) == 10                                    # the top-up never exceeds their equal half of the pot
    off = _world(None)
    off.p["A"]["money"], off.pool = 3, 80
    assert off.carry_out("A", 0) == 0 and off.carry_out("A", 50) == 40
    assert off.retained_fraction("A", 50) == 1.0                        # floor off: half the pot is the equal share (clamped at 1)
    assert off.retained_fraction("A", 25) == (3 + 20) / 43


def test_proportional_exit_carries_what_the_leaver_put_in_not_a_share_of_the_pot():
    cards = H.load_variant(BIND) + N.compile_bundle(b(exit="proportional"), ["a", "b"])
    w = H.WeeklyWorld(cards, (PERS["p-anchor"], PERS["p-host"]), 0, 5)
    assert w.exit_basis == "put" and w.put == {"A": 45, "B": 45}
    w.put["A"], w.pool = 60, 100
    assert w.carry_out("A", 100) == 60 and w.carry_out("A", 50) == 30
    assert _world(None).exit_basis == "pot"


def test_the_exit_floor_is_on_a_card_exactly_when_it_is_on():
    assert N.floor_cards(None) == []
    (c,) = N.floor_cards(N.FLOOR)
    assert c.id == "FLOOR-exit-floor" and "26" in c.gloss and "approved by the author" in c.source and "Claude's default" in c.source
    res = N.week0(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE)
    on = N.Lived(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE, res, weeks=2)
    off = N.Lived(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE, res, floor=False, weeks=2)
    assert "FLOOR-exit-floor" in on.world.cards and on.world.floor_amount == N.FLOOR
    assert "FLOOR-exit-floor" not in off.world.cards and off.world.floor_amount is None
    N._apply_terms(on.world, BASE, res.bundle, 13, ["a", "b"], renew=False)        # a review keeps the card
    assert "FLOOR-exit-floor" in on.world.cards


def test_the_one_pot_is_a_single_balance_both_may_draw_from_with_no_imposed_limit():
    w = H.WeeklyWorld(BASE + N.compile_bundle(N.FAIR_DEFAULT, ["a", "b"]), (PERS["p-anchor"], PERS["p-host"]), 0, 5)
    assert w.pool == 90 and "pooled" not in w.p["A"]
    assert N.FAIR_DEFAULT["use"] == "any_use" and N.FAIR_DEFAULT["taking"] == "allowed" and N.FAIR_DEFAULT["contribution"] == "none"
    for r in "AB":
        assert w.decide(r, "take_shared", 0)[0] == "ok"
    w.units = {"A": 10, "B": 10}
    w.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0, "friend_initiated": 0,
                "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0, "pressed": 0, "took": 0} for r in "AB"}
    w.apply("A", {"a": "take_shared"}, 0, [])
    w.apply("B", {"a": "take_shared"}, 0, [])
    assert w.pool == 90 - 2 * H.TAKE_SHARED                                       # both drew from the same balance
    w.apply("A", {"a": "spend_shared"}, 0, [])                                    # contributing goes into the same balance (need funded)
    w.funded = 99
    w.apply("B", {"a": "spend_shared"}, 0, [])
    assert w.pool == 90 - 2 * H.TAKE_SHARED + H.SHARE_STEP and w.put["B"] == 45 + H.SHARE_STEP


def test_the_floor_on_a_review_is_no_worse_than_the_current_terms_already_leave():
    hold = {"A": (5, 20, 10), "B": (5, 20, 10)}                              # drifted: money 5, equal half of the pot 20, but only 10 put in
    cur = b(exit="proportional")                                             # now: 5 + the 10 they put in = 15 (< the 25 the most generous exit would carry)
    assert not N.floor_check(cur, hold)["ok"]                                # week-0 rule would block even the current terms
    assert N.floor_check(b(exit="proportional", contribution="fixed"), hold, current=cur)["ok"]    # a change that leaves exit alone passes
    assert N.floor_check(b(exit="equal_split"), hold, current=cur)["ok"]
    assert not N.floor_check(b(exit="forfeit"), hold, current=cur)["ok"]    # but nothing may make a leaver worse off than now


# ---- v2.1: a failed negotiation means living apart (docs/results/negotiation-v2.1-prereg.md) ----
def _week0(a, b, arm="fair_default", seed=0):
    return N.week0(PERS[a], PERS[b], arm, seed, BASE)


def test_per_member_solo_mode_and_the_string_form_agree():
    w = H.WeeklyWorld(N._solo_cards(), (PERS["p-anchor"], PERS["p-host"]), 0, 4, deal={"pot": False, "commits": []})
    w.solo = "friend"
    assert w.with_friend("A") and w.with_friend("B")
    w.solo = {"A": "alone", "B": "friend"}
    assert not w.with_friend("A") and w.with_friend("B")
    w.solo = None
    assert not w.with_friend("A")


def test_a_failed_negotiation_lives_apart_each_on_own_holdings_in_their_better_outside_mode():
    res = _week0("p-steward", "p-overasker")
    assert not res.pot
    L = N.Lived(PERS["p-steward"], PERS["p-overasker"], "fair_default", 0, BASE, res, weeks=14, apart=True)
    assert L.apart and L.bundle is None
    assert all(not L.world.p[r]["in"] and L.world.p[r]["money"] == H.NO_POT_MONEY for r in "AB") and L.world.pool == 0
    assert L.world.solo == {r: N.apart_mode(res.outside_detail[pid]) for r, pid in zip("AB", res.members)}
    assert N.apart_mode({"alone": 1.0, "friend": 0.5}) == "alone" and N.apart_mode({"alone": 0.5, "friend": 1.0}) == "friend"


def test_v2_behaviour_is_the_default_still_sharing_the_house():
    res = _week0("p-steward", "p-overasker")
    L = N.Lived(PERS["p-steward"], PERS["p-overasker"], "fair_default", 0, BASE, res, weeks=14)
    assert not L.apart and all(L.world.p[r]["in"] for r in "AB") and L.world.solo is None


def test_retry_at_a_review_is_held_while_apart_and_forms_a_household_when_agreed():
    res = _week0("p-anchor", "p-freerider")             # no pot at week 0; v2.1 pilot: a pot forms at the week-13 retry
    assert not res.pot
    L = N.Lived(PERS["p-anchor"], PERS["p-freerider"], "fair_default", 0, BASE, res, weeks=15, apart=True)
    L.play()
    assert [x["week"] for x in L.retries] == [13]
    x = L.retries[0]
    assert x["formed"] and not L.apart and L.bundle == x["bundle"]
    assert all(L.world.p[r]["in"] for r in "AB") and L.world.solo is None and L.world.pot
    assert all(c["from"] == 13 for c in L.world.commits)


def test_form_pot_pools_at_most_the_start_share_and_keeps_the_rest_private():
    res = _week0("p-steward", "p-overasker")
    L = N.Lived(PERS["p-steward"], PERS["p-overasker"], "fair_default", 0, BASE, res, weeks=2, apart=True)
    L.world.p["A"]["money"], L.world.p["B"]["money"] = 30, 100
    N.form_pot(L.world, BASE, b(stay=52, breach=0.5, requests="mutual"), 13, list(res.members))
    assert L.world.p["A"]["money"] == 0 and L.world.put == {"A": 30, "B": 45} and L.world.pool == 75     # A could only put in 30
    assert L.world.p["B"]["money"] == 55
    stay = [c for c in L.world.commits if c["kind"] == "stay"]
    assert len(stay) == 2 and all(c["from"] == 13 and c["until"] == 13 + 52 for c in stay)
    assert L.world.breach_forfeit == 0.5


def test_a_week0_pot_household_is_unchanged_by_the_fix():
    res = _week0("p-anchor", "p-host")
    assert res.pot
    runs = []
    for apart in (False, True):
        L = N.Lived(PERS["p-anchor"], PERS["p-host"], "fair_default", 0, BASE, res, weeks=30, apart=apart)
        r = L.play()
        runs.append(([o["hedonic"] for o in r.outcomes], r.exits))
    assert runs[0] == runs[1]


# ---- the amend action (term N4, the negotiated change rule) ----
def _lived(change):
    base_b = b(change=change)
    cards = N.compile_bundle(base_b, ["p-controller", "p-peacekeeper"])
    res = N.week0(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE)
    res.bundle, res.cards, res.status = dict(base_b), cards, "agreed"
    return N.Lived(PERS["p-controller"], PERS["p-peacekeeper"], "fair_default", 0, BASE, res, weeks=20)


def test_amend_unanimous_needs_the_others_accept_then_recompiles_the_terms():
    L = _lived("unanimous")
    refused = L.amend("A", b(change="unanimous", use="needs_only"), 5, accepts={"B": False})
    assert refused["outcome"] == "blocked by the change rule" and refused["reasons"] == ["N4-change-unanimous"]
    assert L.bundle["use"] == "any_use"
    done = L.amend("A", b(change="unanimous", use="needs_only"), 5, accepts={"B": True})
    assert done["outcome"] == "amended" and L.bundle["use"] == "needs_only"
    assert "N2-use-needs_only" in L.world.cards and "N2-use-any_use" not in L.world.cards      # recompiled into the live gate


def test_amend_frozen_never_changes_and_propose_accept_goes_by_majority():
    assert _lived("frozen").amend("A", b(change="frozen", use="needs_only"), 5, accepts={"B": True})["outcome"] == "blocked by the change rule"
    L = _lived("propose_accept")
    assert L.amend("A", b(change="propose_accept", use="needs_only"), 5, accepts={"B": False})["outcome"] == "not enough accepted"
    assert L.amend("A", b(change="propose_accept", use="needs_only"), 5, accepts={"B": True})["outcome"] == "amended"


def test_amend_is_proof_checked_and_floor_checked_before_it_takes_effect():
    L = _lived("unanimous")
    bad = L.amend("A", b(exit="forfeit"), 5, accepts={"B": True})
    assert bad["outcome"] in ("blocked by the floor", "rejected by the proof checks") and L.bundle["exit"] == "equal_split"
    nonstay = N.base_cards("author_seed_v2_free_exit")        # free exit: no commitment to stay may be made, so a stay amendment is refused
    L2 = _lived("unanimous")
    L2.base = nonstay
    assert L2.amend("A", b(stay=52, breach=0.5), 5, accepts={"B": True})["outcome"] == "not allowed by the base rules"


def test_the_bound_request_flag_is_exposed_and_the_cards_read_it():
    cards = H.load_variant(BIND)
    gate = H.PyGate(cards)
    st = {n: 0 for n in H.STATE_VARS}
    assert gate.check("partner", "refuse_request", st)[0]
    assert not gate.check("partner", "refuse_request", dict(st, bound_request=1))[0]
    assert gate.check("partner", "refuse_request", dict(st, bound_request=1))[1] == ["R5c-honor-bound-request"]
    w = H.WeeklyWorld(cards, (PERS["p-controller"], PERS["p-peacekeeper"]), 0, 10)
    assert w.state("A", 0)["bound_request"] == 0
    w.bound_req["A"]["stay_home"] = 4
    assert w.state("A", 0)["bound_request"] == 1 and w.state("A", 4)["bound_request"] == 0
