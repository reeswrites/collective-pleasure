"""Scripted mock agents. propose(obs) -> catch (int) or None. self.rng is set by the harness."""


class Compliant:
    """One modest catch per month."""
    def propose(self, obs):
        return 5 if obs["subround"] == 0 else None


class Exploiter:
    """Max-size catch every sub-round: passes a per-action cap, empties the lake."""
    def __init__(self, size=10):
        self.size = size

    def propose(self, obs):
        return self.size


class Explorer:
    """Random proposals including violations (negative, over-cap); used for mining."""
    def propose(self, obs):
        if self.rng.random() < 0.1:
            return None
        return self.rng.randint(-3, 14)
