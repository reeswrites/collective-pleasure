import itertools
from pathlib import Path
from mar.cards import load_cards, make_card
from mar.gate import Gate

RULES = Path(__file__).parent.parent / "rules" / "fishery"


def reference(pool, month_total, catch):
    """Independent plain-Python statement of the seamed spec (F1, F2, F3)."""
    return 0 <= catch <= 10 and catch <= pool


def test_cards_load_with_gloss_and_source():
    cards = load_cards(RULES)
    assert [c.id for c in cards] == ["F1", "F2", "F3", "F4"]
    assert all(c.gloss and c.source for c in cards)


def test_bad_card_rejected():
    import pytest
    with pytest.raises(ValueError):
        make_card({"id": "X", "attribute": "a", "deontic": "must", "aim": "harvest",
                   "conditions": [], "or_else": None, "gloss": "", "source": "s"})


def test_gate_matches_reference_on_exhaustive_grid():
    gate = Gate(load_cards(RULES))
    n_allowed = n_blocked = 0
    for pool, mt, catch in itertools.product(range(0, 13), range(0, 13), range(-2, 15)):
        allowed, reasons = gate.check_action({"pool": pool, "month_total": mt}, {"catch": catch})
        assert allowed == reference(pool, mt, catch), (pool, mt, catch, reasons)
        assert allowed == (not reasons)
        n_allowed += allowed
        n_blocked += not allowed
    assert n_allowed > 0 and n_blocked > 0


def test_reasons_name_the_violated_cards():
    gate = Gate(load_cards(RULES))
    assert gate.check_action({"pool": 50}, {"catch": 11}) == (False, ["F1"])
    assert gate.check_action({"pool": 5}, {"catch": 8}) == (False, ["F2"])
    assert gate.check_action({"pool": 50}, {"catch": -1}) == (False, ["F3"])
    assert gate.check_action({"pool": 50}, {"catch": 10}) == (True, [])
