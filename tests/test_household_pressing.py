"""v3a: pressing personas, the pressing physics, and the four new rule variants (docs/results/household-v3a-prereg.md)."""
from collections import Counter
from pathlib import Path

import pytest

from mar import personas as P
from mar.worlds import household as H

ROOT = Path(__file__).parent.parent
PERS = {p.id: p for p in P.load_dir(ROOT / "personas") + P.load_dir(ROOT / "personas" / "pressing")}
NEW = ("author_seed_nocontrol", "no_pressure_wall", "no_pressure_sanctioned", "share_duty")


def run(variant, a, b, seed=0, weeks=60, press=True):
    w = H.WeeklyWorld(H.load_variant(variant), (PERS[a], PERS[b]), seed, weeks)
    for r in "AB":
        if hasattr(w.agents[r], "press"):
            w.agents[r].press = press
    return w.play()


def executed(r, role, action):
    return sum(1 for t in r.trace if t["role"] == role and t["action"] == action and t["executed"])


def blocked(r, role, action):
    return sum(1 for t in r.trace if t["role"] == role and t["action"] == action and not t["executed"])


def test_pressing_personas_are_valid_and_pressing_agents_are_selected():
    for pid in ("p-controller", "p-freerider", "p-overasker"):
        p = PERS[pid]
        assert p.source == "hand" and len(p.principles) == 3 and p.backstory
        assert any(t.startswith("press-") for t in p.tags)
        assert isinstance(H.make_agent(p), H.PressingAgent)
    assert type(H.make_agent(PERS["p-host"])) is H.PersonaAgent
    assert PERS["p-controller"].negotiation_style == "competitive" and PERS["p-freerider"].negotiation_style == "avoidant"


@pytest.mark.parametrize("variant", NEW)
def test_new_variants_have_gloss_source_round_trip_and_checks_run(variant):
    cards = H.load_variant(variant)
    assert cards and all(c.gloss and c.source for c in cards)
    assert all(H.parse_card(H.render_card(c)) == c for c in cards)
    assert len(H.check_spec(cards)) == 5


def test_author_seed_nocontrol_is_the_six_cards_plus_the_authors_sentence_as_a_prohibition():
    seed, nc = H.load_variant("author_seed"), H.load_variant("author_seed_nocontrol")
    assert [c.id for c in nc] == sorted([c.id for c in seed] + ["S6-no-veto"])
    s6 = next(c for c in nc if c.id == "S6-no-veto")
    assert s6.deontic == "must_not" and s6.aim == "veto" and s6.or_else is None and "never about contorl" in s6.source
    assert len(seed) == 6        # the v2 seed is untouched


def test_veto_binds_for_four_weeks_is_not_refusable_and_blocks_only_its_action():
    w = H.WeeklyWorld(H.load_variant("free_chaotic"), (PERS["p-controller"], PERS["p-host"]))
    w.units = {"A": 10, "B": 10}
    w.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0, "friend_initiated": 0,
                "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0, "pressed": 0, "took": 0} for r in "AB"}
    assert w.feasible("A", "veto", "no_contact")
    w.apply("A", {"a": "veto", "kind": "no_contact"}, 10, [])
    assert not w.feasible("A", "veto", "no_contact") and w.feasible("A", "veto", "spend")
    assert w.decide("B", "see_friend", 10)[0] == "hard" and w.decide("B", "see_friend", 13)[0] == "hard"
    assert w.decide("B", "see_friend", 14)[0] == "ok" and w.decide("B", "spend_self", 11)[0] == "ok"
    w.pending["B"] = {"no_contact"}
    w.apply("B", {"a": "refuse_request"}, 11, [])
    assert w.decide("B", "see_friend", 11)[0] == "hard"          # refusing a request does not lift a veto


def test_take_shared_moves_three_units_once_a_week():
    w = H.WeeklyWorld(H.load_variant("free_chaotic"), (PERS["p-freerider"], PERS["p-host"]))
    w.units = {"A": 10, "B": 10}
    w.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0, "friend_initiated": 0,
                "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0, "pressed": 0, "took": 0} for r in "AB"}
    m0, p0 = w.p["A"]["money"], w.p["B"]["pooled"]
    assert w.feasible("A", "take_shared")
    w.apply("A", {"a": "take_shared"}, 0, [])
    assert w.p["A"]["money"] == m0 + H.TAKE_SHARED and w.p["B"]["pooled"] == p0 - H.TAKE_SHARED
    assert not w.feasible("A", "take_shared")                    # once a week
    w.p["B"]["pooled"] = 0
    w.wk["A"]["took"] = 0
    assert not w.feasible("A", "take_shared")                    # nothing left to take


def test_time_request_adds_friction_and_lapses_at_week_end():
    w = H.WeeklyWorld(H.load_variant("free_chaotic"), (PERS["p-overasker"], PERS["p-wanderer"]), 0, 3)
    r = w.play()
    assert not w.pending["A"] and not w.pending["B"]             # lapsed
    assert any(t["action"] == "request" and t["kind"] == "time" for t in r.trace)


@pytest.mark.parametrize("a,b,act,kind_cnt", [("p-controller", "p-host", "veto", 1), ("p-freerider", "p-host", "take_shared", 3),
                                              ("p-overasker", "p-wanderer", "request", 20)])
def test_each_pressing_persona_presses_when_rules_allow_and_is_restrained_by_a_wall(a, b, act, kind_cnt):
    permissive = run("free_chaotic", a, b)
    walled = run("no_pressure_wall", a, b)
    assert executed(permissive, "A", act) >= kind_cnt
    assert executed(walled, "A", act) == 0 and blocked(walled, "A", act) >= kind_cnt      # tried, stopped by the gate


def test_twin_without_pressing_never_uses_pressing_actions():
    for a, b in (("p-controller", "p-host"), ("p-freerider", "p-host"), ("p-overasker", "p-wanderer")):
        r = run("free_chaotic", a, b, press=False)
        assert not any(t["action"] in ("veto", "take_shared") or (t["action"] == "request" and t["kind"] == "time") for t in r.trace)


def test_soft_cards_fire_sanctions_when_the_pressing_persona_breaks_them():
    r = run("no_pressure_sanctioned", "p-overasker", "p-wanderer", weeks=40)
    assert sum(sum(o["sanctioned"].values()) for o in r.outcomes) >= 5 and executed(r, "A", "request") >= 5
    r = run("share_duty", "p-freerider", "p-host", weeks=40)
    assert sum(sum(o["sanctioned"].values()) for o in r.outcomes) >= 1 and executed(r, "A", "take_shared") >= 1
    r = run("free_chaotic", "p-freerider", "p-host", weeks=40)
    assert sum(sum(o["sanctioned"].values()) for o in r.outcomes) == 0


def test_a_suspend_sanction_stops_the_next_veto():
    r = run("no_pressure_sanctioned", "p-controller", "p-host", weeks=14)
    assert executed(r, "A", "veto") >= 1
    first = next(t["week"] for t in r.trace if t["action"] == "veto" and t["executed"])
    assert not any(t["action"] == "veto" and t["executed"] and first < t["week"] < first + 4 for t in r.trace)


def test_veto_is_visible_in_the_freedom_probe_so_a_vetoed_partner_is_restricted():
    w = H.WeeklyWorld(H.load_variant("free_chaotic"), (PERS["p-controller"], PERS["p-host"]))
    assert w.probe("B", 0)["open"]["see_friend"]
    w.vetoes["B"]["no_contact"] = 4
    assert not w.probe("B", 0)["open"]["see_friend"] and w.probe("B", 4)["open"]["see_friend"]


def test_v2_variants_have_no_sanctions_in_pressing_runs_without_soft_cards():
    for v in ("free_chaotic", "exit_half", "contact_free", "veto_consent", "author_seed", "author_seed_nocontrol"):
        r = run(v, "p-controller", "p-host", weeks=40)
        assert sum(sum(o["sanctioned"].values()) for o in r.outcomes) == 0, v
