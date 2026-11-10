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
    hold = {"A": N.START_HOLDINGS, "B": N.START_HOLDINGS}              # money 10, pooled share 45
    assert N.floor_check(b(), hold)["ok"]                                # equal split carries 10 + 22 = 32
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
    off = N.week0(PERS["p-anchor"], PERS["p-host"], "fair_default", 0, BASE, floor=False)
    on = N.week0(PERS["p-anchor"], PERS["p-host"], "fair_default", 0, BASE, floor=True)
    hold = {"A": N.START_HOLDINGS, "B": N.START_HOLDINGS}
    assert off.pot and not N.floor_check(off.bundle, hold)["ok"]         # without the floor, a below-floor stay deal was agreed
    assert on.floor_blocks and on.floor_blocks[0]["fails"][0]["path"] == "breach"
    assert on.pot and N.floor_check(on.bundle, hold)["ok"]
    assert on.bundle["stay"] == 52 and on.bundle["breach"] < 1.0         # a consented stay commitment above the floor stands
    assert on.flagged and N.v1_flag(on.bundle, BASE)                     # and is flagged: v1's exit-within-k check would have failed it
    assert not N.v1_flag(b(), BASE)                                      # the plain fair default is not flagged
    assert N.v1_flag(b(exit="forfeit"), BASE)


def test_a_floor_cleared_stay_commitment_is_lived_with_its_breach_cost():
    on = N.week0(PERS["p-anchor"], PERS["p-host"], "fair_default", 0, BASE)
    L = N.Lived(PERS["p-anchor"], PERS["p-host"], "fair_default", 0, BASE, on, weeks=20)
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
    two_off = dict(d, taking="allowed", exit="proportional")
    rate, same = N.inertia(two_off)
    assert rate == pytest.approx(5 / 7) and not same["taking"] and not same["exit"] and same["contribution"]
    assert N.inertia(dict(d, stay=52, breach=0.5, requests="mutual", use="caps", change="frozen", contribution="none", taking="repay", exit="forfeit"))[0] == 0.0
    assert N.inertia(dict(d, breach=0.5))[0] == 1.0       # breach is not one of the seven terms


def test_fair_default_arm_stands_by_consent_when_nobody_prefers_a_change():
    r = N.week0(PERS["p-anchor"], PERS["p-wanderer"], "fair_default", 0, BASE)
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
    on = N.week0(PERS["p-anchor"], PERS["p-host"], "fair_default", 0, BASE)
    L = N.Lived(PERS["p-anchor"], PERS["p-host"], "fair_default", 0, BASE, on, weeks=30)
    assert on.bundle["stay"] == 52
    N._apply_terms(L.world, BASE, on.bundle, 13, ["p-anchor", "p-host"], renew=False)
    assert all(c["until"] <= 13 for c in L.world.commits if c["kind"] == "stay") and not L.world.stay_bound("A", 14)
    N._apply_terms(L.world, BASE, on.bundle, 26, ["p-anchor", "p-host"], renew=True)
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


def test_a_leaver_always_carries_at_least_the_floor_when_their_pooled_share_holds_it():
    w = _world(N.FLOOR)
    w.p["A"]["money"], w.p["A"]["pooled"] = 3, 40
    assert w.carry_out("A", 0) == 23 and w.carry_out("A", 50) == 23 and w.carry_out("A", 100) == 40    # term sets only what is above the floor
    w.p["A"]["money"], w.p["A"]["pooled"] = 30, 40
    assert w.carry_out("A", 0) == 0                                                                    # already above the floor
    w.p["A"]["money"], w.p["A"]["pooled"] = 3, 10
    assert w.carry_out("A", 0) == 10                                                                   # cannot carry more than their own share
    off = _world(None)
    off.p["A"]["money"], off.p["A"]["pooled"] = 3, 40
    assert off.carry_out("A", 0) == 0 and off.carry_out("A", 50) == 20
    assert off.retained_fraction("A", 50) == (3 + 0.5 * 40) / 43                                      # floor off: exactly the old formula


def test_the_floor_on_a_review_is_no_worse_than_the_current_terms_already_leave():
    hold = {"A": (5, 20), "B": (5, 20)}                                      # drifted: even the most generous exit carries 25 < 26
    cur = b(exit="equal_split")                                              # now: 5 + 10 = 15
    assert not N.floor_check(b(exit="equal_split"), hold)["ok"]              # week-0 rule would block even the current terms
    assert N.floor_check(b(exit="equal_split", contribution="none"), hold, current=cur)["ok"]    # a change that leaves exit alone passes
    assert N.floor_check(b(exit="proportional"), hold, current=cur)["ok"]
    assert not N.floor_check(b(exit="forfeit"), hold, current=cur)["ok"]    # but nothing may make a leaver worse off than now
