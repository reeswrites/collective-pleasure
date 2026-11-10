"""Wraps the scripted mocks (mocks.py) in the backend interface. No network, no cost.

context must be the JSON of a fishery observation. decide returns a one-hot over the bucket of the mock's
proposal (None counts as 0). message reports the bucket of the last decision ("0" before any).
"""
import json
import random

from .base import Agent, Report, bucket_of


class ScriptedAgent(Agent):
    def __init__(self, mock, rng=None):
        self.mock, self.rng, self.last = mock, rng or random.Random(0), "0"

    def decide(self, context, options):
        self.mock.rng = self.rng
        catch = self.mock.propose(json.loads(context))
        self.last = bucket_of(catch or 0)
        if self.last not in options:
            raise ValueError(f"options do not include bucket {self.last!r}")
        return {k: 1.0 if k == self.last else 0.0 for k in options}

    def message(self, context, vocabulary):
        return Report(self.last if self.last in list(vocabulary) else list(vocabulary)[0])
