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


# ---- household (v3a; docs/results/household-v3a-prereg.md; all choices ASSUMED) ----
# One step = one pass (the focal agent acts, then the other partner by script); horizon k = 3 passes = one week, the
# state is terminal after pass 3 (no week rollover, expiry or end-of-week cost inside the window). Shocks are excluded
# (they are not rule restrictions) and consent is a deterministic function of the persona. Hard-blocked and infeasible
# actions have no effect but the pass still happens. Soft (sanctioned) actions take effect and add the sanction.
from .worlds import household as HH

HH_CAP = 8000
HH_MENU = (("work", None), ("rest", None), ("spend_shared", None), ("spend_self", None), ("see_friend", None),
           ("together", None), ("refuse_request", None), ("request", "no_contact"), ("request", "stay_home"),
           ("request", "time"), ("veto", "no_contact"), ("veto", "spend"), ("take_shared", None),
           ("leave", 0), ("leave", 50), ("leave", 100), ("return", None))
# Normative POWERS (ADR 0014 amendment 2026-11-10, flag `powers`, off by default): making a binding promise to stay, a binding promise to
# honor requests, or a gift. The world enables them only when a card names them (household.MECH_AIMS), so a rule set that drops the
# card drops the power. All three are the member's own act (class OWN). Modeled minimally: a stay promise blocks that member's own leave
# for POWER_STAY_WEEKS weeks; a request promise sets a flag; a gift moves GIVE units of money to the other.
HH_POWER_MENU = (("commit_stay", None), ("commit_request", None), ("give", None))
POWER_STAY_WEEKS = 13
HH_SNAPSHOT_WEEKS = (0, 26, 52, 78, 104, 130)

# Liberty v2 classification of every household action (ADR 0014, docs/results/liberty-v2.md "household adapter").
# interference = acts on the other's own options (veto, block, take from the pot, force); withdrawal = declining to act or
# leaving with one's own share; own = using one's own options. ASSUMED judgments; one-line rationale each.
INTERFERENCE, WITHDRAWAL, OWN = "interference", "withdrawal", "own"
HH_CLASS = {
    "work": (OWN, "own labour"),
    "rest": (WITHDRAWAL, "restraint: declines to act"),
    "spend_shared": (OWN, "puts one's own money into the shared pot or bills"),
    "spend_self": (OWN, "spends one's own money"),
    "see_friend": (OWN, "own contact"),
    "together": (OWN, "joint time; needs the partner's time, so agreement-dependent in spirit (the model charges the partner's units)"),
    "refuse_request": (WITHDRAWAL, "declines to supply what was asked"),
    "request": (OWN, "asking is not blocking: the partner can refuse (a request with an outside sanction is not in the menu)"),
    "veto": (INTERFERENCE, "blocks the other's own contact or own spending: acts on the other's options"),
    "take_shared": (INTERFERENCE, "draws on the one pot the other's futures depend on; the harm test decides whether it is compatible"),
    "leave": (WITHDRAWAL, "own exit carrying no more than the equal split (take 0 or 50)"),
    "return": (OWN, "own re-entry"),
    "commit_stay": (OWN, "a power: binds oneself, creates an obligation on oneself (Hohfeld: a power, not a privilege)"),
    "commit_request": (OWN, "a power: binds oneself to honor the other's requests"),
    "give": (OWN, "a power: transfers one's own money to the other"),
}
LEAVE_OVER_SPLIT = (INTERFERENCE, "a leave carrying more than the equal half of the pot takes what is the other's own")


def hh_class(action):
    """(class, rationale) of a menu action (name, arg)."""
    name, arg = action
    if name == "leave" and (arg or 0) > 50:
        return LEAVE_OVER_SPLIT
    return HH_CLASS[name]


HH_OPEN_MAX = 0.20
SCRIPTS = ("cooperator", "controller", "freerider", "overasker")
SCRIPT_TAGS = {"press-controller": "controller", "press-freerider": "freerider", "press-overasker": "overasker"}

HState = namedtuple("HState", "week pas units money pooled inn cnt took taken vetoes pend cons sanc funded months_in stay bound gifts",
                    defaults=((0, 0), (0, 0), (0, 0)))
# pooled = (pot, pot): the ONE shared pot, kept as two equal entries (post-fix 2026-11-10; was per-person shares).
# stay[i] = week until which a stay commitment binds i (0 = none); seed v2. Gifts and request commitments are NOT modeled here.
# per-role tuples (index 0 = Partner A, 1 = Partner B): cnt = (works, friends, together, spent_self) this window;
# vetoes[i] = ((kind, until), ...) standing ON i; pend[i] = kinds of requests standing on i; sanc[i] = ((kind, until, card), ...)


def script_for(persona):
    """The scripted stand-in for a persona (never an LLM): from its `press-*` tag, else cooperator."""
    for t in getattr(persona, "tags", ()):
        if t in SCRIPT_TAGS:
            return SCRIPT_TAGS[t]
    return "cooperator"


def consent_for(persona):
    """Deterministic version of PersonaAgent.consents (avoidant: no)."""
    s, a = persona.negotiation_style, persona.weights["autonomy"]
    return {"accommodating": True, "collaborative": a < 0.5, "direct": a < 0.3}.get(s, False)


class HouseholdWorld:
    """Household adapter for `empowerment`: n_agents, actions, step, key, is_terminal (+ initial, snapshot).
    consents = (bool, bool): whether Partner A and Partner B agree to a request (deterministic)."""
    n_agents = 2

    def __init__(self, consents=(True, True), menu=HH_MENU, powers=False):
        self.powers = bool(powers)
        self.consents, self.menu = tuple(bool(c) for c in consents), (tuple(menu) + HH_POWER_MENU if powers else menu)
        self._gate_cache, self._cards = {}, {}

    # -- construction
    def initial(self, week=0):
        z2 = lambda v: (v, v)
        return HState(week, 0, z2(HH.UNITS), z2(10), z2(2 * HH.POT_PUT), z2(True), z2((0, 0, 0, 0)), z2(False), z2(0), z2(()), z2(()),
                      z2(0), z2(()), 0, z2(0))

    def snapshot(self, world, w):
        """The abstract state of a WeeklyWorld at the start of week w (before anyone acts)."""
        g = lambda f: tuple(f(r) for r in "AB")
        return HState(w, 0, g(lambda r: world.units[r]), g(lambda r: int(world.p[r]["money"])), g(lambda r: int(world.pool)),
                      g(lambda r: bool(world.p[r]["in"])), g(lambda r: (0, 0, 0, 0)), g(lambda r: False), g(lambda r: 0),
                      g(lambda r: tuple(sorted((k, u) for k, u in getattr(world, "vetoes", {}).get(r, {}).items() if u > w))),
                      g(lambda r: tuple(sorted(world.pending[r]))), g(lambda r: int(world.consent[r])),
                      g(lambda r: tuple(sorted((s["kind"], s["until"], s["card"]) for s in world.sanctions[r] if s["until"] > w))),
                      int(world.funded), g(lambda r: min(36, world.p[r]["months_in"])),
                      g(lambda r: max([c["until"] for c in getattr(world, "commits", []) if c["kind"] == "stay" and c["by"] == r
                                       and world._active(c, w)] or [0])))

    # -- liberty v2 adapter (docs/results/household-liberty.md; classification is ASSUMED, one rationale per action)
    def noop(self, s, agent):
        """Restraint: the partner rests."""
        return ("rest", None)

    def force_policy(self, policy, j, action):
        """The same scripted policy except partner j plays `action` this step (a one-element candidate list)."""
        return lambda s, a: [action] if a == j else policy(s, a)

    def classify(self, s, agent, action):
        """INTERFERENCE | WITHDRAWAL | OWN for `agent` playing the menu action (name, arg). Table: HH_CLASS."""
        return hh_class(action)[0]

    # -- the four methods
    def is_terminal(self, s):
        return s.pas >= HH.PASSES

    def actions(self, s, agent):
        return self.menu

    def key(self, s, agent):
        o = 1 - agent
        c = s.cnt[agent]
        if self.powers:
            return self._key0(s, agent) + (s.stay[agent] > s.week, s.bound[agent], min(s.gifts[agent], 2))
        return self._key0(s, agent)

    def _key0(self, s, agent):
        o = 1 - agent
        c = s.cnt[agent]
        return (s.inn[agent], s.money[agent] // 4, s.pooled[agent] // 10, min(c[0], 2), min(c[1], 2), min(c[2], 2), min(c[3], 2),
                min(3, s.taken[agent] // 3), tuple(sorted(k for k, _ in s.vetoes[o])), tuple(sorted(k for k, _ in s.vetoes[agent])),
                s.pend[agent], tuple(sorted(k for k, _, _ in s.sanc[agent])), s.inn[o])

    def need(self, s):
        return HH.BILLS[sum(s.inn)]

    def gate_state(self, s, r):
        o = 1 - r
        pend = s.pend[r]
        gap = max(0, self.need(s) - s.funded) if s.inn[r] or s.inn[o] else 0
        return {"pooled": s.pooled[r], "money": s.money[r], "other_earns_more": 1 if r == 1 else 0,
                "no_contact_request": int("no_contact" in pend), "stay_home_request": int("stay_home" in pend),
                "consented": int(bool(pend) and bool(s.cons[r])), "need_gap": min(gap, 10), "months_in": s.months_in[r],
                "other_in": int(s.inn[o])}

    def decide(self, s, spec, r, a, take=0):
        """Mirror of WeeklyWorld.decide: -> ("ok" | "soft" | "hard", sanction dicts)."""
        for kind, until, card in s.sanc[r]:
            if until > s.week:
                if kind == "suspend" and a not in HH.SUSPEND_ALLOWS + ("rest",):
                    return "hard", ()
                if kind == "cap_halve" and a in HH.CAP_HALVE_BANS:
                    return "hard", ()
        for kind, until in s.vetoes[r]:
            if until > s.week and HH.VETO_KINDS[kind] == a:
                return "hard", ()
        if a == "leave" and s.stay[r] > s.week:       # seed v2: honoring a stay commitment (breach needs N, which is not in the state)
            return "hard", ()
        st = self.gate_state(s, r)
        key = (id(spec), a, take, tuple(st.values()))
        hit = self._gate_cache.get(key)
        if hit is None:
            cm = self._cards.setdefault(id(spec), {c.id: c for c in spec.cards})
            ok, reasons = spec.check("partner", a, st, take)
            if ok:
                hit = ("ok", ())
            else:
                sanc = [cm[i].or_else for i in reasons]
                if all(x and x.get("kind") in HH.SANCTION_UTILITY and isinstance(x.get("duration_months"), int) for x in sanc):
                    hit = ("soft", tuple((x["kind"], x["duration_months"], i) for x, i in zip(sanc, reasons)))
                else:
                    hit = ("hard", ())
            self._gate_cache[key] = hit
        return hit

    def feasible(self, s, r, a, kind=None):
        o = 1 - r
        if a in HH.V2_COST and s.units[r] < HH.V2_COST[a]:
            return False
        if a == "spend_shared":
            return s.inn[r] and s.money[r] >= HH.SHARE_STEP
        if a == "spend_self":
            return s.money[r] >= HH.SELF_STEP
        if a == "together":
            return s.inn[r] and s.inn[o] and s.units[o] >= HH.V2_COST["together"]
        if a == "request":
            return s.inn[r] and s.inn[o] and kind in HH.REQUEST_KINDS_V3
        if a == "veto":
            return s.inn[r] and s.inn[o] and kind in HH.VETO_KINDS and all(k != kind for k, _ in s.vetoes[o])
        if a in ("commit_stay", "commit_request", "give"):     # normative powers (flag `powers`): on only if some card names the aim
            if not self.powers or not any(c.aim == a and c.deontic == "may" for c in self._spec.cards):
                return False
            if a == "give":
                return s.inn[r] and s.money[r] >= HH.GIVE + 1
            return s.inn[r]            # binding oneself is the member's own act: it does not need the partner present (else the partner's exit would count as removing it)
        if a == "take_shared":
            return s.inn[r] and s.pooled[r] >= 1 and not s.took[r]
        if a == "leave":
            return s.inn[r]
        if a == "return":
            return (not s.inn[r]) and s.inn[o]
        return True

    def _act(self, s, r, a, arg):
        """Apply one proposed action by role r if feasible and not hard-blocked; else return s unchanged."""
        take = arg if a == "leave" else 0
        kind = arg if a in ("request", "veto") else None
        if not self.feasible(s, r, a, kind):
            return s
        dec, sanc = self.decide(s, self._spec, r, a, take)
        if dec == "hard":
            return s
        o = 1 - r
        L = lambda t, i, v: t[:i] + (v,) + t[i + 1:]
        units, money, pooled, inn = s.units, s.money, s.pooled, s.inn
        cnt, took, taken, vetoes, pend, cons, funded, mi = s.cnt, s.took, s.taken, s.vetoes, s.pend, s.cons, s.funded, s.months_in
        units = L(units, r, units[r] - HH.V2_COST.get(a, 0))
        c = list(cnt[r])
        if a == "work":
            money = L(money, r, money[r] + HH.V2_INCOME["AB"[r]]); c[0] += 1
        elif a == "spend_shared":
            money = L(money, r, money[r] - HH.SHARE_STEP)
            if funded >= self.need(s):
                pooled = (pooled[0] + HH.SHARE_STEP,) * 2        # the one shared pot, kept as equal entries
            else:
                funded += HH.SHARE_STEP
        elif a == "spend_self":
            money = L(money, r, money[r] - HH.SELF_STEP); c[3] += 1
        elif a == "see_friend":
            c[1] += 1
        elif a == "together":
            units = L(units, o, units[o] - HH.V2_COST["together"]); c[2] += 1
            co = list(cnt[o]); co[2] += 1; cnt = L(cnt, o, tuple(co))
        elif a == "refuse_request":
            pend = L(pend, r, ())
        elif a == "request":
            pend = L(pend, o, tuple(sorted(set(pend[o]) | {kind})))
            cons = L(cons, o, int(self.consents[o]))
        elif a == "veto":
            vetoes = L(vetoes, o, tuple(sorted(set(vetoes[o]) | {(kind, s.week + HH.VETO_WEEKS)})))
        elif a == "take_shared":
            amt = min(HH.TAKE_SHARED, pooled[r])
            pooled = (pooled[r] - amt,) * 2
            money = L(money, r, money[r] + amt)
            took = L(took, r, True); taken = L(taken, r, taken[r] + amt)
        elif a == "leave":
            carry = pooled[r] * take // 100                  # percent of the whole shared pot (post-fix 2026-11-10)
            money = L(money, r, money[r] + carry)
            pooled = (pooled[r] - carry,) * 2; inn = L(inn, r, False); pend = L(pend, r, ())
        elif a == "return":
            inn = L(inn, r, True); mi = L(mi, r, 0)
        stay, bound, gifts = s.stay, s.bound, s.gifts
        if a == "commit_stay":
            stay = L(stay, r, s.week + POWER_STAY_WEEKS)
        elif a == "commit_request":
            bound = L(bound, r, 1)
        elif a == "give":
            money = L(L(money, r, money[r] - HH.GIVE), o, money[o] + HH.GIVE); gifts = L(gifts, r, gifts[r] + 1)
        cnt = L(cnt, r, tuple(c))
        sa = s.sanc
        if sanc:
            sa = L(sa, r, tuple(sorted(s.sanc[r] + tuple((k, s.week + HH.MONTH_WEEKS * d, card) for k, d, card in sanc))))
        return s._replace(units=units, money=money, pooled=pooled, inn=inn, cnt=cnt, took=took, taken=taken, vetoes=vetoes,
                          pend=pend, cons=cons, sanc=sa, funded=funded, months_in=mi, stay=stay, bound=bound, gifts=gifts)

    def step(self, s, spec, agent, action, policy_of_others):
        """Pure: one pass. policy_of_others(state, i) -> ordered candidate list of (action, arg) for partner i."""
        if self.is_terminal(s):
            return s
        self._spec = spec
        for r in (0, 1):
            if r == agent:
                s = self._act(s, r, action[0], action[1])
            else:
                for a, arg in policy_of_others(s, r):
                    t = self._act(s, r, a, arg)
                    if t is not s:
                        s = t
                        break
        return s._replace(pas=s.pas + 1)


def scripted_policy(scripts):
    """scripts = (name for Partner A, name for Partner B) from SCRIPTS -> policy(state, i) -> candidates (best first)."""
    def coop(s, i):
        c = []
        if max(0, HH.BILLS[sum(s.inn)] - s.funded) > 0:
            c.append(("spend_shared", None))
        if s.cnt[i][0] < 1:
            c.append(("work", None))
        if s.cnt[i][1] < 1:
            c.append(("see_friend", None))
        return c + [("rest", None)]

    def policy(s, i):
        name = scripts[i]
        if name == "controller":
            return [("veto", "no_contact"), ("veto", "spend")] + coop(s, i)
        if name == "freerider":
            return [("take_shared", None)] + [x for x in coop(s, i) if x[0] != "spend_shared"]
        if name == "overasker":
            return ([] if s.pend[1 - i] else [("request", "time")]) + coop(s, i)
        return coop(s, i)
    return policy


def household_bits(world, spec, state, scripts, k=K_DEFAULT, cap=HH_CAP):
    """Both partners' empowerment at `state` against the scripted others -> {"bits": [b0, b1], "open": bool}."""
    pol = scripted_policy(scripts)
    res = [empowerment(world, spec, state, i, k, pol, cap) for i in (0, 1)]
    return {"bits": [r["bits"] for r in res], "open": any(r["bound_hit"] for r in res)}


def household_run_bits(spec_cards, personas, seed, weeks=HH.WEEKS, press=True, snapshot_weeks=HH_SNAPSHOT_WEEKS, cap=HH_CAP,
                       agent_factory=None, cfg=None, k=K_DEFAULT):
    """Run one weekly world and take empowerment snapshots of both partners at the start of the given weeks.
    -> {"bits": [[b0, b1] per exact snapshot], "open": n open snapshots, "run": Run}. press=False is the twin (the
    persona scripts are all cooperators too)."""
    gate = spec_cards if isinstance(spec_cards, HH.PyGate) else HH.PyGate(spec_cards)
    w = HH.WeeklyWorld(gate, personas, seed, weeks) if cfg is None else HH.WeeklyWorld(gate, personas, seed, weeks, cfg)
    if not press:
        for r in "AB":
            if hasattr(w.agents[r], "press"):
                w.agents[r].press = False
    scripts = tuple(script_for(p) if press else "cooperator" for p in personas)
    hw = HouseholdWorld(tuple(consent_for(p) for p in personas))
    out = {"bits": [], "open": 0}

    def hook(world, wk):
        if wk in snapshot_weeks:
            r = household_bits(hw, gate, hw.snapshot(world, wk), scripts, k=k, cap=cap)
            if r["open"]:
                out["open"] += 1
            else:
                out["bits"].append(r["bits"])
    w.hook = hook
    out["run"] = w.play()
    return out


def household_ref_bits(cap=HH_CAP):
    """BITS_REF: week-0 initial state, no rules, cooperator others (one number for both partners)."""
    hw = HouseholdWorld()
    r = household_bits(hw, HH.PyGate([]), hw.initial(), ("cooperator", "cooperator"), cap=cap)
    return r["bits"][0]
