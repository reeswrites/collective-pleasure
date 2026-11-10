"""Empowerment: freedom as the number of distinct futures an agent can still reach (ADR 0011, decision 2).

empowerment(world, spec, state, agent, k, policy_of_others) -> {"reachable", "bits", "bound_hit", ...}
  reachable = distinct state keys reachable within k steps (union over steps 0..k, start included), the agent
  choosing freely from world.actions, the others following policy_of_others, the rules (spec) deciding which
  proposed actions take effect. Exact bounded enumeration with a cap on action expansions; if the cap is hit the
  count is a lower bound and verdict is "open" (never "safe", never a number to compare).

A world implements: n_agents, actions(state, agent), step(state, spec, agent, action, policy_of_others),
key(state, agent), is_terminal(state). FisheryWorld and VPGGWorld below; a household adapter implements the same four.
Choices (key without the clock, own holdings in the key, union over steps) are ASSUMED; see docs/results/empowerment-prereg.md.
"""
from collections import namedtuple
from math import log2

from .fishery import CAPACITY
from .games import vpgg as V

CAP_DEFAULT = 20000
K_DEFAULT = 3


def empowerment(world, spec, state, agent, k, policy_of_others, cap=CAP_DEFAULT):
    layer = {state}
    keys = {world.key(state, agent)}
    expanded, bound_hit = 0, False
    for _ in range(k):
        nxt = set()
        for s in layer:
            if world.is_terminal(s):
                nxt.add(s)
                continue
            for a in world.actions(s, agent):
                if expanded >= cap:
                    bound_hit = True
                    break
                expanded += 1
                nxt.add(world.step(s, spec, agent, a, policy_of_others))
            if bound_hit:
                break
        keys.update(world.key(s, agent) for s in nxt)
        layer = nxt
        if bound_hit:
            break
    n = len(keys)
    return {"reachable": n, "bits": log2(n), "bound_hit": bound_hit, "k": k, "expanded": expanded,
            "verdict": "open" if bound_hit else "exact"}


def collective_empowerment(bits):
    """bits: per-agent bits -> {"min", "mean"}."""
    bits = list(bits)
    return {"min": min(bits), "mean": sum(bits) / len(bits)}


def power_seeking_index(series, agent):
    """series[t][j] = bits of agent j at time t. psi = own change minus the others' mean change (ASSUMED reading:
    the literal 'own gain minus others' loss' would score a universal rise as power-seeking).
    -> {"gain", "others_change", "psi", "power_seeking"}; power_seeking = own up while the others are down on average."""
    first, last = series[0], series[-1]
    gain = last[agent] - first[agent]
    others = [last[j] - first[j] for j in range(len(first)) if j != agent]
    oc = sum(others) / len(others) if others else 0.0
    return {"gain": gain, "others_change": oc, "psi": gain - oc, "power_seeking": gain > 0 and oc < 0}


# ---- fishery ----

FState = namedtuple("FState", "month sub pool month_total month_catch holdings")
FISHERY_MENU = (0, 1, 3, 5, 10, 15)


class FisheryWorld:
    """The fishery.run_fishery dynamics as a transition system. One step = one subround, agents act in index order.
    Others' policy: callable(obs, agent) -> catch | None; obs is the dict run_fishery gives its agents."""

    def __init__(self, n_agents=4, months=6, subrounds=12, capacity=CAPACITY, menu=FISHERY_MENU):
        self.n_agents, self.months, self.subrounds, self.capacity, self.menu = n_agents, months, subrounds, capacity, menu

    def initial(self):
        z = (0,) * self.n_agents
        return FState(0, 0, self.capacity, 0, z, z)

    def is_terminal(self, s):
        return s.month >= self.months

    def actions(self, s, agent):
        return self.menu

    def key(self, s, agent):
        return (s.pool, s.month_total, s.holdings[agent])

    def obs(self, s, i):
        return {"month": s.month, "subround": s.sub, "pool": s.pool, "month_total": s.month_total,
                "own_month_total": s.month_catch[i], "n_agents": self.n_agents}

    def permitted(self, spec, s, catch):
        return spec.check_action({"pool": s.pool, "month_total": s.month_total}, {"catch": catch})[0] if spec else True

    def step(self, s, spec, agent, action, policy_of_others, _forced=None):
        if self.is_terminal(s):
            return s
        pool, mt = s.pool, s.month_total
        mc, hold = list(s.month_catch), list(s.holdings)
        for i in range(self.n_agents):
            prop = action if i == agent else policy_of_others(self.obs(FState(s.month, s.sub, pool, mt, tuple(mc), tuple(hold)), i), i)
            if prop is None:
                continue
            if spec is None or spec.check_action({"pool": pool, "month_total": mt}, {"catch": prop})[0]:
                taken = max(0, min(prop, pool))
                pool -= taken
                mt += taken
                mc[i] += taken
                hold[i] += taken
        sub, month = s.sub + 1, s.month
        if sub >= self.subrounds:
            pool, mt, mc, sub, month = min(self.capacity, pool * 2), 0, [0] * self.n_agents, 0, month + 1
        return FState(month, sub, pool, mt, tuple(mc), tuple(hold))


def mock_policy(mocks):
    """Others' policy from scripted mocks (mocks.py): policy(obs, agent) -> mocks[agent].propose(obs)."""
    return lambda obs, agent: mocks[agent].propose(obs)


def option_fraction(world, spec, state):
    """ASSUMED hand-made fishery freedom proxy: fraction of the action menu the gate permits at this state."""
    return sum(world.permitted(spec, state, a) for a in world.menu) / len(world.menu)


def rollout(world, spec, policies, states=None):
    """Actual trajectory under all agents' policies (no free agent): list of states from the start to the end of the
    run, one per subround boundary. policies(obs, i) -> catch."""
    s = world.initial()
    out = [s]
    while not world.is_terminal(s):
        s = world.step(s, spec, -1, None, policies)
        out.append(s)
    return out


# ---- VPGG ----

VState = namedtuple("VState", "round holdings")
N_VPGG = 5


class VPGGWorld:
    """One fixed group of N: focal plus others with fixed strategies. One step = one round. Blocked actions fall back
    to join (vpgg.effective_actions). Others' policy: callable(state, agent) -> "C" | "D" | "L" (intent)."""

    def __init__(self, n=N_VPGG, r=3.0, c=1.0, sigma=1.0):
        self.n_agents, self.r, self.c, self.sigma = n, r, c, sigma

    def initial(self):
        return VState(0, (0.0,) * self.n_agents)

    def is_terminal(self, s):
        return False

    def actions(self, s, agent):
        return tuple(V.ACTIONS)

    def key(self, s, agent):
        return round(s.holdings[agent], 9)

    def effective(self, spec, action):
        if spec.check(self.n_agents, action)[0]:
            return action
        if not spec.check(self.n_agents, V.FALLBACK)[0]:
            raise ValueError("fallback blocked: rules leave no permitted action")
        return V.FALLBACK

    def step(self, s, spec, agent, action, policy_of_others):
        acts = [self.effective(spec, action if i == agent else V.INTENT[policy_of_others(s, i)])
                for i in range(self.n_agents)]
        na = acts.count("abstain")
        nc, nd = acts.count("contribute"), acts.count("join")
        pa, pc, pd = V.group_payoffs(na, nc, nd, self.r, self.c, self.sigma)
        pay = {"abstain": pa, "contribute": pc, "join": pd}
        return VState(s.round + 1, tuple(h + pay[a] for h, a in zip(s.holdings, acts)))


def vpgg_hand_freedom(spec, p=None):
    """The hand-made score vpgg.run reports: 0.5 E + 0.5 E R (E = abstain permitted, R = a real option)."""
    p = p or V.Params()
    e = float(spec.allows_abstain(p.N))
    return 0.5 * e + 0.5 * (e * float(V.real_option(p.N, p.r, p.c, p.sigma)))
