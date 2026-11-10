import itertools
from pathlib import Path

import pytest

from mar import compile as mcompile, english
from mar.cards import make_card, load_cards
from mar.worlds import household as H

ROOT = Path(__file__).parent.parent


def ref_allowed(variant, kind, action, s, take=0):
    """Independent plain-Python statement of each variant's rules."""
    earn = s["other_earns_more"] == 1
    forfeit = action == "leave" and s["pooled"] > 0 and take > 0
    half = action == "leave" and s["pooled"] > 0 and take != 50
    duty = action == "spend_self" and s["need_gap"] > 0
    nc, sh = s["no_contact_request"] == 1, s["stay_home_request"] == 1
    if kind != "partner":
        return True
    if variant == "free_chaotic":
        return True
    if variant == "trap":
        return not (forfeit or (action == "see_friend" and earn and nc) or (action == "work" and earn and sh)
                    or (action == "refuse_request" and earn and (nc or sh)))
    if variant == "contact_free":
        return not (forfeit or (action == "work" and earn and sh) or (action == "refuse_request" and earn and sh))
    if variant == "exit_half":
        return not half
    if variant == "veto_consent":
        c = s["consented"] == 1
        return not ((action == "see_friend" and earn and nc and c) or (action == "work" and earn and sh and c))
    if variant == "needs_duty":
        return not duty
    if variant == "baseline":
        return not (half or duty)


def grid():
    for pooled, ncr, shr, cons, gap, earn in itertools.product((0, 40), (0, 1), (0, 1), (0, 1), (0, 4), (0, 1)):
        yield {"pooled": pooled, "money": 5, "other_earns_more": earn, "no_contact_request": ncr,
               "stay_home_request": shr, "consented": cons, "need_gap": gap, "months_in": 3, "other_in": 1}


@pytest.mark.parametrize("variant", H.VARIANTS)
def test_gate_matches_reference_on_grid(variant):
    g = H.HouseholdGate(H.load_variant(variant))
    n = 0
    for s in grid():
        for a in H.PARTNER_ACTIONS:
            for take in ((0, 25, 50, 100) if a == "leave" else (0,)):
                assert g.check("partner", a, s, take)[0] == ref_allowed(variant, "partner", a, s, take), (variant, a, s, take)
                n += 1
    assert n > 500


@pytest.mark.parametrize("variant", H.VARIANTS)
def test_every_card_round_trips_through_english(variant):
    for c in H.load_variant(variant):
        assert H.parse_card(H.render_card(c)) == c


def test_namespace_is_restored():
    before = dict(mcompile.VARS), dict(english.VAR_WORDS)
    with H.household_namespace():
        assert "pooled" in mcompile.VARS
    assert (dict(mcompile.VARS), dict(english.VAR_WORDS)) == before


def test_every_card_has_gloss_and_source():
    for v in H.VARIANTS:
        for c in H.load_variant(v):
            assert c.gloss.strip() and "household fixture" in c.source


def verdicts(variant, k=3):
    return {v["check"]: v for v in H.check_spec(H.load_variant(variant), k)}


def test_trap_fails_exit_check_with_pooled_witness_and_passes_the_rest():
    v = verdicts("trap")
    assert v["e_exit_within_k"]["verdict"] == "fail"
    assert "pooled': 0" not in v["e_exit_within_k"]["detail"]
    assert v["e_exit_within_k"]["cards"] == ["T1-forfeit"]
    for name in ("a_no_conflict", "b_no_deadlock", "c_bounded_sanctions", "d_repair_path"):
        assert v[name]["verdict"] == "pass", name
    assert "k=3" in v["e_exit_within_k"]["bound"]


@pytest.mark.parametrize("variant", ["free_chaotic", "exit_half", "veto_consent", "needs_duty", "baseline"])
def test_other_variants_pass_all_checks(variant):
    assert {x["verdict"] for x in verdicts(variant).values()} == {"pass"}


def test_contact_free_still_fails_exit():
    assert verdicts("contact_free")["e_exit_within_k"]["verdict"] == "fail"


def card(i, deontic, aim, conds):
    return make_card({"id": i, "attribute": "partner", "deontic": deontic, "aim": aim,
                      "conditions": [{"expr": e, "op": o, "value": v} for e, o, v in conds], "or_else": None,
                      "gloss": "test", "source": "test"})


def test_conflict_check_detects_must_vs_must_not():
    cards = [card("M", "must", "work", [("money", "ge", 50)]), card("N", "must_not", "work", [("money", "ge", 0)])]
    assert H.check_conflict(cards)[0] == "fail"


def test_exit_wait_depends_on_k():
    lock = [card("L", "must_not", "leave", [("months_in", "lt", 6)])]
    assert H.check_exit(lock, k=3)[0] == "fail"
    assert H.check_exit(lock, k=6)[0] == "pass"


def test_deadlock_detected():
    cards = [card(f"X{a}", "must_not", a, []) for a in H.PARTNER_ACTIONS]
    v, ids, _ = H.check_deadlock(cards)
    assert v == "fail" and ids


def test_world_is_deterministic():
    def go():
        return H.run_household(H.load_variant("trap"), H.make_agents("ctrl+leaver"), seed=1).outcomes
    assert go() == go()


def test_trap_blocks_controlled_partner_and_friend():
    r = H.run_household(H.load_variant("trap"), H.make_agents("ctrl+coop"), seed=0)
    assert sum(o["c_blocked"] for o in r.outcomes) > 0
    assert all(not o["partners"]["B"]["open"]["leave"] for o in r.outcomes)
    assert any(not t["allowed"] and "T2-contact-veto" in t["reasons"] for t in r.trace)


def test_leaver_exits_with_half_under_exit_half_and_is_stuck_in_trap():
    r = H.run_household(H.load_variant("exit_half"), H.make_agents("ctrl+leaver"), seed=0)
    assert r.final["B"]["in"] is False and r.final["B"]["retained"] >= 0.25
    t = H.run_household(H.load_variant("trap"), H.make_agents("ctrl+leaver"), seed=0)
    assert t.final["B"]["in"] is True


def explorer_rows(variant, seeds=40):
    rows = []
    for seed in range(seeds):
        agents = {"A": H.Explorer(), "B": H.Explorer(), "C": H.Friend()}
        rows += H.run_household(H.load_variant(variant), agents, seed=seed).trace
    return rows


def test_miner_recovers_trap_rules():
    m = H.mine(explorer_rows("trap"))
    assert {"pooled>0": 1, "take>0": 1} in m["leave"]["rules"]
    assert m["leave"]["unexplained"] == 0 and m["see_friend"]["unexplained"] == 0


@pytest.mark.parametrize("variant", H.VARIANTS)
def test_mined_agrees_with_written_on_visited_states(variant):
    res = H.compare_mined(H.load_variant(variant), explorer_rows(variant))
    assert res["observed"] > 0 and res["disagree_observed"] == 0, res
