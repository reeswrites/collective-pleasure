from pathlib import Path
from mar.cards import load_cards
from mar.gate import Gate
from mar.fishery import run_fishery
from mar.mocks import Exploiter, Explorer
from mar.patcher import propose_patch
from mar.miner import mine, diff, written_bounds

RULES = Path(__file__).parent.parent / "rules" / "fishery"


def explore(cards, seeds=range(50)):
    rows = []
    for s in seeds:
        rows += run_fishery([Explorer() for _ in range(4)], Gate(cards), seed=s).trace
    return rows


def patched():
    cards = load_cards(RULES)
    return cards + propose_patch(run_fishery([Exploiter() for _ in range(4)], Gate(cards)).trace, cards)


def test_written_bounds():
    assert written_bounds(load_cards(RULES)) == {"per_action_min": 0, "per_action_max": 10, "per_month_max": None}
    assert written_bounds(patched())["per_month_max"] == 40


def test_mined_equals_written_both_specs():
    for cards in (load_cards(RULES), patched()):
        m = mine(explore(cards))
        d = diff(cards, m)
        assert d["bounds_equal"], d["bounds"]
        assert not d["edges_mined_not_jure"], d["edges_mined_not_jure"]


def test_miner_detects_a_difference_when_rules_differ():
    seamed = load_cards(RULES)
    m = mine(explore(patched(), seeds=range(20)))  # lived under the patched rules
    assert not diff(seamed, m)["bounds_equal"]     # ...differs from the seamed written spec
