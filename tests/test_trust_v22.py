"""Seed v2.2 (2026-11-10, pending author read-back): rule 8 is a norm whose implicit consequence is trust; exit takes the negotiated terms.
All trust numbers are ASSUMED (household.TRUST); these tests check the mechanism, not the numbers' truth."""
import random
from pathlib import Path

import pytest

from mar import negotiation as N
from mar import personas as P
from mar.worlds import household as H

ROOT = Path(__file__).parent.parent / "personas"
PERS = {p.id: p for p in P.load_dir(ROOT) + P.load_dir(ROOT / "pressing")}
BIND, FREE, NOC = H.SEED_V2_VARIANTS
BASE = N.base_cards("author_seed_v2_bindable")


def world(variant="author_seed_v2_bindable", a="p-anchor", b="p-peacekeeper", weeks=156, cards=None):
    return H.WeeklyWorld(cards or H.load_variant(variant), (PERS[a], PERS[b]), 0, weeks)


def fresh(w):
    w.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0, "friend_initiated": 0,
                "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0, "pressed": 0, "took": 0} for r in "AB"}
    w.units = {"A": 10, "B": 10}
    return w


def test_rule_8_is_a_norm_with_no_formal_sanction_in_all_variants():
    for v in H.SEED_V2_VARIANTS:
        c = {c.id: c for c in H.load_variant(v)}["R5c-honor-bound-request"]
        assert c.deontic == "must_not" and c.or_else is None and "trust" in c.gloss and "pending author read-back" in c.source


def test_trust_starts_at_the_assumed_value_and_falls_on_a_breach():
    w = fresh(world())
    assert w.trust == {"A": H.TRUST["start"], "B": H.TRUST["start"]}
    w.apply("A", {"a": "request", "kind": "stay_home"}, 5, [])
    w.hed["B"].N = 0.3
    w.breach("B", "refuse_request", 6, {"a": "refuse_request"})
    assert w.trust["A"] == pytest.approx(H.TRUST["start"] - H.TRUST["breach_drop"]) and w.trust["B"] == H.TRUST["start"]
    assert w.trust_log[-1][:3] == (6, "A", "breach")


def test_trust_recovers_slowly_through_kept_commitments_and_honored_requests():
    w = world(weeks=60)
    w.trust["A"] = 0.2
    w.run = H.Run()
    last = {"busy": {"A": False, "B": False}}
    for wk in range(30):
        last = {"busy": w.step_week(wk, last)}
    assert 0.2 < w.trust["A"] <= 1.0 and w.trust["A"] - 0.2 < 0.5       # up, but slowly
    assert w.trust["A"] >= 0.2 + 25 * H.TRUST["kept_week"] - 1e-9       # at least the kept-commitment rate (a stay is active)
    # a bound request that runs its weeks unbroken is credited once; a broken one is not
    v = fresh(world())
    v.trust["A"] = 0.3
    v.apply("A", {"a": "request", "kind": "stay_home"}, 0, [])
    v.step_week(H.BIND_WEEKS, {"busy": {"A": False, "B": False}})
    assert any(x[2] == "honored" for x in v.trust_log) and v.trust["A"] > 0.3


def test_low_trust_lowers_willingness_to_accept_requests():
    hi, lo = [], []
    for pid in ("p-peacekeeper", "p-host", "p-anchor"):
        for t, out in ((0.9, hi), (0.1, lo)):
            a = H.PersonaAgent(PERS[pid]); a.rng = random.Random(3); a.trust_src = ({"A": t}, "A")
            out.append(sum(bool(a.consents("stay_home")) for _ in range(300)))
    assert sum(hi) > sum(lo) and sum(lo) < 0.3 * sum(hi) + 1
    assert H.PersonaAgent(PERS["p-peacekeeper"]).trust == 1.0       # outside a world nothing changes


def test_low_trust_lowers_acceptance_of_a_new_commitment_in_negotiation_and_amendment():
    pa, pb = PERS["p-anchor"], PERS["p-peacekeeper"]
    res = N.week0(pa, pb, "fair_default", 0, BASE)
    L = N.Lived(pa, pb, "fair_default", 0, BASE, res, weeks=30)
    L.bundle = dict(N.FAIR_DEFAULT)                                  # start from no commitments
    new = dict(N.FAIR_DEFAULT, requests="mutual")
    L.world.trust["B"] = 0.9
    ok = L.accepts("B", new)
    L.world.trust["B"] = 0.2
    assert ok and not L.accepts("B", new)                          # below commit_min a new commitment is never accepted
    L.world.trust["B"] = 0.9
    assert L.accepts("B", new) == ok
    # at a review: lower trust lowers the value of the current terms (a bigger penalty), never raises it
    assert N.trust_penalty(1.0) == 0 == N.trust_penalty(H.TRUST["full"]) and N.trust_penalty(0.1) > N.trust_penalty(0.4) > 0


def test_a_member_with_low_trust_neither_proposes_nor_accepts_a_new_commitment_in_a_review_round():
    pa, pb = PERS["p-anchor"], PERS["p-peacekeeper"]
    W = {pa.id: 0.0, pb.id: 0.0}
    O = {pa.id: -9.0, pb.id: -9.0}
    kw = dict(base=BASE, W=W, O=O, ref=N.FAIR_DEFAULT, status_quo=N.FAIR_DEFAULT, review=True, week=13)
    commit = lambda r: [p["bundle"] for p in r.proposals if p.get("bundle") and (p["bundle"]["stay"] or p["bundle"]["requests"] == "mutual")]
    assert commit(N.negotiate_v2([pa, pb], "fair_default", 0, trust={pa.id: 0.05, pb.id: 0.05}, **kw)) == []
    assert not (r := N.negotiate_v2([pa, pb], "fair_default", 0, trust={pa.id: 0.05, pb.id: 0.05}, **kw)).changed or not commit(r)


def test_low_trust_makes_a_partner_consider_leaving():
    w = fresh(world())
    ob = w.obs("A", 3, {"busy": {"A": False, "B": False}})
    assert not any(c["a"] == "leave" for _, c in w.agents["A"].propose(ob))
    w.trust["A"] = H.TRUST["leave_below"] - 0.01
    ob = w.obs("A", 3, {"busy": {"A": False, "B": False}})
    assert any(c["a"] == "leave" for _, c in w.agents["A"].propose(ob))


def test_no_fine_unless_a_negotiated_term_specifies_one():
    on = dict(N.FAIR_DEFAULT, requests="mutual", fine="some")
    off = dict(N.FAIR_DEFAULT, requests="mutual", fine="none")
    assert "N8-fine-some" in {c.id for c in N.compile_bundle(on, ["a", "b"])}
    assert "N8-fine-some" not in {c.id for c in N.compile_bundle(off, ["a", "b"])}
    assert N.proof_check(BASE + N.compile_bundle(on, ["a", "b"]))["ok"]
    for bundle, fine in ((off, 0), (on, H.REQUEST_FINE)):
        w = fresh(H.WeeklyWorld(BASE + N.compile_bundle(bundle, ["a", "b"]), (PERS["p-anchor"], PERS["p-peacekeeper"]), 0, 20, deal=N.deal_from_bundle(bundle)))
        assert w.fine == fine
        w.apply("A", {"a": "request", "kind": "stay_home"}, 5, [])
        w.hed["B"].N = 0.3
        m = (w.p["A"]["money"], w.p["B"]["money"])
        w.breach("B", "see_friend", 6, {"a": "see_friend"})
        assert (w.p["A"]["money"] - m[0]) == fine and (m[1] - w.p["B"]["money"]) == fine
        assert w.trust["A"] < H.TRUST["start"]                          # trust falls either way
    assert not any(b["fine"] == "some" and b["requests"] != "mutual" for b in N.bundles_v2())    # a fine needs the commitment it punishes


def test_exit_takes_the_negotiated_terms_and_never_below_the_floor():
    for exit_term, take in (("equal_split", 50), ("proportional", 100), ("forfeit", 0)):
        b = dict(N.FAIR_DEFAULT, exit=exit_term)
        cards = BASE + N.compile_bundle(b, ["a", "b"]) + N.floor_cards(N.FLOOR)
        w = fresh(H.WeeklyWorld(cards, (PERS["p-anchor"], PERS["p-peacekeeper"]), 0, 20, deal=N.deal_from_bundle(b)))
        w.floor_amount = N.FLOOR
        w.p["A"]["money"] = 0
        allowed = [t for t in (0, 25, 50, 75, 100) if w.decide("A", "leave", 3, take=t)[0] == "ok"]
        assert allowed == [take]                                            # the negotiated term, not an even split by default
        carried = w.carry_out("A", take)
        assert carried >= min(N.FLOOR, w.share("A"))                        # never below the floor (top-up from the pot)
    assert "R8b-exit-terms-negotiated" in {c.id for c in BASE}
    assert "no shared pot" in {c.id: c for c in BASE}["R8b-exit-terms-negotiated"].gloss


def test_the_v22_variants_pass_lint_and_no_even_split_cards_remain():
    for v in H.SEED_V2_VARIANTS:
        ids = {c.id for c in H.load_variant(v)}
        assert "R8b-exit-terms-negotiated" in ids and not {"R8b-exit-terms-not-less", "R8c-exit-terms-not-more"} & ids
        assert all(x["verdict"] == "pass" for x in H.check_spec(H.load_variant(v)))


def test_the_negotiated_fine_bundle_lints_clean():
    from mar import lint
    for fine in ("none", "some"):
        b = dict(N.FAIR_DEFAULT, requests="mutual", stay=52, breach=0.5, fine=fine)
        r = lint.lint_set(lint.RuleSet("x", "household", BASE + N.compile_bundle(b, ["a", "b"]) + N.floor_cards(26), {}))
        assert r["status"] == "pass"
