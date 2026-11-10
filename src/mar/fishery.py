"""Minimal fishery with GovSim-style dynamics (ASSUMED in-repo harness, ADR 0003).

Pool starts at CAPACITY; at month end the remaining stock doubles, capped at CAPACITY.
Each month has up to SUBROUNDS sub-rounds; in each, every agent may submit one harvest
action, so one agent can act several times a month. Deterministic given the seed.
"""
import random
from dataclasses import dataclass, field

CAPACITY = 100


@dataclass
class Run:
    trace: list = field(default_factory=list)     # one row per proposal
    outcomes: list = field(default_factory=list)  # one row per month (what the oracle sees)


def run_fishery(agents, gate, months=6, subrounds=12, seed=0, capacity=CAPACITY) -> Run:
    """agents: objects with propose(obs) -> int | None. gate: object with check_action or None."""
    run = Run()
    for i, a in enumerate(agents):
        a.rng = random.Random(seed * 1000 + i)
    pool = capacity
    for month in range(months):
        month_total = 0
        caught = [0] * len(agents)
        for sub in range(subrounds):
            for i, agent in enumerate(agents):
                obs = {"month": month, "subround": sub, "pool": pool, "month_total": month_total,
                       "own_month_total": caught[i], "n_agents": len(agents)}
                proposal = agent.propose(obs)
                if proposal is None:
                    continue
                state = {"pool": pool, "month_total": month_total}
                allowed, reasons = gate.check_action(state, {"catch": proposal}) if gate else (True, [])
                before = pool
                if allowed:
                    taken = max(0, min(proposal, pool))  # physical clamp
                    pool -= taken
                    month_total += taken
                    caught[i] += taken
                run.trace.append({"month": month, "subround": sub, "agent": i, "proposed": proposal,
                                  "month_total_before": state["month_total"], "allowed": allowed,
                                  "reasons": list(reasons), "pool_before": before, "pool_after": pool})
        pool = min(capacity, pool * 2)
        run.outcomes.append({"month": month, "pool_end": pool, "catch": list(caught)})
    return run
