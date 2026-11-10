from pathlib import Path
from mar.cards import load_cards
from mar.gate import Gate
from mar.fishery import run_fishery


class Fixed:
    def __init__(self, c): self.c = c
    def propose(self, obs): return self.c if obs["subround"] < 3 else None


def test_dynamics_and_determinism():
    rules = Path(__file__).parent.parent / "rules" / "fishery"
    g = Gate(load_cards(rules))
    r1 = run_fishery([Fixed(5), Fixed(5)], g, months=3, seed=1)
    r2 = run_fishery([Fixed(5), Fixed(5)], g, months=3, seed=1)
    assert r1.trace == r2.trace
    # 2 agents * 3 sub-rounds * 5 = 30 taken; 70 left doubles, capped at 100
    assert r1.outcomes[0]["pool_end"] == 100 and sum(r1.outcomes[0]["catch"]) == 30
    assert r1.trace[0]["pool_before"] == 100 and r1.trace[0]["pool_after"] == 95
