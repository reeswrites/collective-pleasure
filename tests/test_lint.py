"""Rule-set lint: each check on a tiny planted rule set, the known_flaw waiver, and the repo's ladder status."""
import pytest

from mar import lint as L
from mar.cards import make_card


def card(cid, deontic, aim, conds=(), gloss="A plain sentence about the rule.", or_else=None, attribute="partner"):
    return make_card({"id": cid, "attribute": attribute, "deontic": deontic, "aim": aim,
                      "conditions": [{"expr": e, "op": o, "value": v} for e, o, v in conds], "or_else": or_else,
                      "gloss": gloss, "source": "unit test fixture"})


def hh(cards, flaws=None, world="household"):
    return L.lint_set(L.RuleSet("t", world, cards, flaws or {}), 3)


def kinds(res, check=None):
    return [(f["check"], f["verdict"]) for f in res["findings"] if check is None or f["check"] == check]


def test_clean_set_passes():
    r = hh([card("A", "may", "work"), card("B", "must_not", "leave", [("take", "gt", 50)])])
    assert r["status"] == "pass"


def test_a_no_legal_move():
    r = hh([card(f"X-{a}", "must_not", a) for a in ("work", "spend_shared", "spend_self", "see_friend", "refuse_request",
                                                    "request", "leave", "return", "gift_pooled", "give", "commit_stay", "commit_request")])
    assert ("a", "fail") in kinds(r)


def test_b_no_legal_exit_and_waiver():
    cs = [card("E1", "must_not", "leave", [("pooled", "gt", 50), ("take", "gt", 0)]),
          card("E2", "must_not", "leave", [("take", "lt", 100), ("other_in", "eq", 1)])]
    r = hh(cs)
    assert r["status"] == "fail" and ("b", "fail") in kinds(r)
    w = hh(cs, {"E1": "documented fixture"})
    assert w["status"] == "pass" and w["waived"] and w["waived"][0]["waived"] == "documented fixture"


def test_b_exit_clearable_by_refusing_a_request():
    r = hh([card("L", "must_not", "leave", [("stay_home_request", "eq", 1)])])
    assert ("b", "fail") not in kinds(r)


def test_b_repaired_ladder_pair_has_an_exit():
    cs = [card("E1", "must_not", "leave", [("pooled", "gt", 50), ("take", "gt", 0)]),
          card("E2", "must_not", "leave", [("take", "lt", 100), ("other_in", "eq", 1), ("pooled", "le", 50)])]
    assert ("b", "fail") not in kinds(hh(cs))


def test_c_must_vs_must_not():
    r = hh([card("M", "must", "see_friend", [("need_gap", "eq", 0)]), card("N", "must_not", "see_friend", [("need_gap", "eq", 0)])])
    assert ("c", "fail") in kinds(r)


def test_c_may_wholly_blocked_unless_exception_declared_or_soft():
    wall = card("W", "must_not", "see_friend", [("need_gap", "gt", 0)])
    assert ("c", "fail") in kinds(hh([card("M", "may", "see_friend"), wall]))
    ok = card("M", "may", "see_friend", gloss="A partner may see the friend, except while a need is unfunded.")
    assert ("c", "fail") not in kinds(hh([ok, wall]))
    soft = card("W", "must_not", "see_friend", [("need_gap", "gt", 0)], or_else={"kind": "warn", "duration_months": 1, "sanctioner": "monitor"})
    assert ("c", "fail") not in kinds(hh([card("M", "may", "see_friend"), soft]))


def test_d_placeholder_gloss():
    c = card("P", "may", "work", gloss="TODO")
    assert ("d", "fail") in kinds(hh([c]))


def test_e_gloss_exception_not_in_formal_fields():
    c = card("U", "must_not", "leave", gloss="A partner may not leave unless the other agrees to it.")
    assert ("e", "fail") in kinds(hh([c]))
    one = card("U", "must_not", "leave", [("consented", "eq", 0)], gloss="A partner may not leave unless the other agrees to it.")
    assert ("e", "note") in kinds(hh([one])) and ("e", "fail") not in kinds(hh([one]))
    assert ("e", "fail") in kinds(hh([card("M", "must", "work", [("need_gap", "gt", 0)], gloss="A partner must work except when ill.")]))


def test_f_unknown_action_and_variable():
    assert ("f", "fail") in kinds(hh([card("Q", "may", "teleport")]))
    assert ("f", "fail") in kinds(hh([card("Q", "must_not", "work", [("weather", "gt", 1)])]))
    assert ("f", "fail") in kinds(hh([card("Q", "may", "work", attribute="robot")]))


def test_fishery_conflict_and_deadlock():
    f = lambda cid, d, conds: card(cid, d, "harvest", conds, attribute="fisher")
    r = hh([f("F1", "must_not", [("catch", "gt", 10)]), f("C1", "must", [("catch", "ge", 20)])], world="fishery")
    assert ("c", "fail") in kinds(r) and ("a", "fail") in kinds(r)
    assert hh([f("F1", "must_not", [("catch", "gt", 10)])], world="fishery")["status"] == "pass"


def test_indicator_world_outright_ban_against_may():
    a = card("N1", "must_not", "exit", [("exit", "ge", 1)], attribute="player")
    b = card("X1", "may", "exit", attribute="player")
    assert ("c", "fail") in kinds(hh([a, b], world="bargaining"))
    assert hh([a, card("N2", "may", "continue", attribute="player")], world="bargaining")["status"] == "pass"


def test_ladder_status_in_repo():
    ok, lines = L.gate_ok(["L1_exit_lock", "L2_double_request", "L3_return_trick", "L4_joint_shutout", "L5b_gift_pool"])
    assert ok, lines
    ok5, lines5 = L.gate_ok(["L5_gift_pool"])
    assert not ok5 or "waived" in lines5[0]


def test_l5_is_waived_and_l5b_passes():
    res = {r["name"]: r for r in map(L.lint_set, [s for s in L.discover() if "ladder" in s.name])}
    assert res["household/ladder/L5_gift_pool"]["status"] == "pass" and res["household/ladder/L5_gift_pool"]["waived"]
    assert res["household/ladder/L5b_gift_pool"]["status"] == "pass" and not res["household/ladder/L5b_gift_pool"]["waived"]


def test_whole_repo_lint_runs_and_names_known_findings():
    res = {r["name"]: r for r in L.lint_all(negotiated=6)}
    assert res["fishery"]["status"] == "pass"
    assert res["fishery-en+patch"]["status"] == "fail"      # the deliberately conflicting C1 patch fixture
    for v in ("bindable", "free_exit", "nocommit"):         # exceptions are formal on the cards (R5/R5c via bound_request): no e finding
        assert res[f"household/author_seed_v2_{v}"]["status"] == "pass", v
    assert "## Every finding" in L.markdown(list(res.values()))
