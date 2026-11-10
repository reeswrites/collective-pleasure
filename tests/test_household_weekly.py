from itertools import product
from pathlib import Path

import pytest

from mar import personas as P
from mar.worlds import household as H

PERS = {p.id: p for p in P.load_dir(Path(__file__).parent.parent / "personas")}


def states():
    for pooled, ncr, shr, cons, gap, earn in product((0, 40), (0, 1), (0, 1), (0, 1), (0, 4), (0, 1)):
        yield {"pooled": pooled, "money": 5, "other_earns_more": earn, "no_contact_request": ncr, "stay_home_request": shr,
               "consented": cons, "need_gap": gap, "months_in": 3, "other_in": 1}


@pytest.mark.parametrize("variant", H.V2_VARIANTS)
def test_pygate_matches_z3_gate(variant):
    cards = H.load_variant(variant)
    z, py = H.HouseholdGate(cards), H.PyGate(cards)
    for s in states():
        for a in H.PARTNER_ACTIONS:
            for take in ((0, 25, 50, 100) if a == "leave" else (0,)):
                assert z.check("partner", a, s, take) == py.check("partner", a, s, take)


def test_author_seed_cards_quote_the_seed_and_pass_checks():
    cards = H.load_variant("author_seed")
    assert len(cards) == 6 and all("author-household-norms-2026-11-10.md" in c.source for c in cards)
    assert all(v["verdict"] == "pass" for v in H.check_spec(cards))


def test_shocks_are_common_random_numbers_and_rates_come_from_config():
    a = H.shock_schedule(0, "p-anchor", "p-wanderer")
    assert a == H.shock_schedule(0, "p-anchor", "p-wanderer") and a != H.shock_schedule(1, "p-anchor", "p-wanderer")
    n = sum(len(H.shock_schedule(s, "x", "y")) for s in range(200))
    assert 0 < n < 200 * 156 * 0.1          # rare: a few per decade, not every week


def test_sanctions_are_enforced():
    w = H.WeeklyWorld(H.load_variant("baseline"), (PERS["p-anchor"], PERS["p-host"]))
    st = {**w.state("A", 0), "need_gap": 4}
    dec, sanc, _ = w.decide("A", "spend_self", 0, st=st)
    assert dec == "soft" and sanc[0]["kind"] == "warn"          # a card with a sanction can be broken, at a price
    assert w.decide("A", "leave", 0, take=10, st=st)[0] == "hard"   # a card without one is a wall
    w.sanctions["A"].append({"kind": "suspend", "until": 12, "card": "T2"})
    assert w.decide("A", "see_friend", 5)[0] == "hard" and w.decide("A", "work", 5)[0] == "ok"
    assert w.decide("A", "see_friend", 12)[0] == "ok"
    w.sanctions["A"] = [{"kind": "cap_halve", "until": 8, "card": "X"}]
    assert w.decide("A", "spend_self", 3)[0] == "hard" and w.decide("A", "spend_self", 8)[0] != "hard"


def test_breaking_a_soft_rule_costs_the_sanction():
    w = H.WeeklyWorld(H.load_variant("trap"), (PERS["p-anchor"], PERS["p-wanderer"]))
    st = {**w.state("B", 0), "no_contact_request": 1}
    dec, sanc, _ = w.decide("B", "see_friend", 0, st=st)
    assert dec == "soft" and sanc[0]["kind"] == "suspend"
    w.units = {"A": 10, "B": 10}
    w.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0,
                "friend_initiated": 0, "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0} for r in "AB"}
    w.apply("B", {"a": "see_friend"}, 0, sanc)
    assert w.sanctions["B"][0]["until"] == 12 and w.wk["B"]["sanctioned"] == 1


def test_run_is_deterministic_and_rows_have_hedonic_state():
    cards = H.load_variant("baseline")
    r1 = H.run_weekly(cards, (PERS["p-anchor"], PERS["p-wanderer"]), 1, weeks=30)
    r2 = H.run_weekly(cards, (PERS["p-anchor"], PERS["p-wanderer"]), 1, weeks=30)
    assert r1.outcomes == r2.outcomes and len(r1.outcomes) == 30
    row = r1.outcomes[-1]
    assert set(row["hedonic"]) == {"A", "B"} and {"pleasure", "s_off", "s_non", "B", "tip"} <= set(row["hedonic"]["A"])


def test_personas_drive_different_behaviour():
    cards = H.load_variant("free_chaotic")
    r = H.run_weekly(cards, (PERS["p-anchor"], PERS["p-wanderer"]), 0, weeks=52)
    n = lambda who, a: sum(1 for t in r.trace if t["role"] == who and t["action"] == a and t["allowed"])
    assert n("A", "together") > n("B", "together") or n("B", "see_friend") > n("A", "see_friend")


def test_trap_creates_non_offsettable_suffering_that_free_rules_do_not():
    pair = (PERS["p-anchor"], PERS["p-wanderer"])
    worst = lambda v: max(max(o["hedonic"][k]["nonoff_run"] for o in H.run_weekly(H.load_variant(v), pair, 0).outcomes) for k in "AB")
    assert worst("trap") >= 6 > worst("free_chaotic")
