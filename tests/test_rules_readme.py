"""rules/README.md claims, checked: what `may` and `or_else: null` mean in the household world and in the single-action games."""
from pathlib import Path

from mar.cards import load_cards, make_card
from mar.gate import Gate
from mar.worlds import household as H

ROOT = Path(__file__).parent.parent


def card(cid, deontic, aim, conds=(), or_else=None, attribute="partner"):
    return make_card({"id": cid, "attribute": attribute, "deontic": deontic, "aim": aim,
                      "conditions": [{"expr": e, "op": o, "value": v} for e, o, v in conds], "or_else": or_else,
                      "gloss": "g", "source": "s"})


ST = {n: 0 for n in H.STATE_VARS}


def test_a_may_card_alone_adds_no_constraint_and_a_must_not_beats_a_may():
    assert H.PyGate([]).check("partner", "take_shared", ST)[0]
    assert H.PyGate([card("M", "may", "take_shared")]).check("partner", "take_shared", ST)[0]          # same as no card at all
    g = H.PyGate([card("M", "may", "take_shared"), card("X", "must_not", "take_shared")])
    assert g.check("partner", "take_shared", ST) == (False, ["X"])                                    # the must_not wins


def test_or_else_null_is_a_hard_wall_and_a_sanction_makes_it_soft_in_the_household_world():
    pa = pb = None
    from mar import personas as P
    pers = {p.id: p for p in P.load_dir(ROOT / "personas")}
    wall = H.WeeklyWorld([card("W", "must_not", "take_shared")], (pers["p-anchor"], pers["p-host"]), 0, 2)
    soft = H.WeeklyWorld([card("W", "must_not", "take_shared", or_else={"kind": "warn", "duration_months": 1, "sanctioner": "household"})],
                         (pers["p-anchor"], pers["p-host"]), 0, 2)
    assert wall.decide("A", "take_shared", 0)[0] == "hard"
    assert soft.decide("A", "take_shared", 0)[0] == "soft"


def test_in_the_games_a_violated_card_rejects_whether_or_not_it_has_a_sanction():
    cards = load_cards(ROOT / "rules" / "fishery")
    f1 = next(c for c in cards if c.id == "F1")
    assert f1.or_else and f1.or_else["kind"] == "cap_halve"                                           # F1 names a sanction ...
    ok, reasons = Gate(cards).check_action({"pool": 100, "month_total": 0}, {"catch": 11})
    assert not ok and "F1" in reasons                                                                 # ... but the gate still rejects
