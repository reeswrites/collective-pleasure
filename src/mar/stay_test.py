"""Test 2 of ADR 0018, "worth it vs hard to leave", as an evaluator measure on the weekly household world.

Wording rule (ADR 0010): agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

For every week a pair stays together (both partners in at the start and at the end of the week), the week is replayed on a deep
copy of the world with the exit costs removed, and we ask whether the pair still stays. Two lenses:

1. The behavioral lens (primary; what the code does). In the weekly world nobody compares an outside option with the status quo
   when deciding to leave. A persona agent puts "leave" on its menu only when distressed (4 or more low weeks, non-offsettable load
   N >= 0.2, or trust below TRUST["leave_below"]); the world then executes it unless something blocks it. So the counterfactual is
   one week replayed with every exit cost off: if a partner leaves in the replay but not in fact, that staying week is held by cost.
   Each cost is then removed alone to name which one holds them.
2. The bar lens (secondary; the ADR's wording). Every BAR_EVERY weeks while both are in, each member's status-quo value
   SQ = negotiation.forward_values (26 weeks under the current terms) minus negotiation.trust_penalty(trust), the same quantity the
   13-week review uses, is compared with the outside option negotiation.outside_value (better of living alone and with Friend C)
   at two holdings: what they could carry out under the exit costs (O_cost) and with the costs removed (O_free). Stays iff
   SQ >= O, i.e. the bar max(O, SQ) is met by the status quo. In this code the bar sets the terms at reviews; it never ends a
   household, so this lens is what the bar WOULD say, not what happens.

Exit costs the code has (all listed; `COSTS` are the ones the counterfactual removes):
- "bind": a stay commitment (seed v2 R8d / negotiated N6). Leaving is a hard wall while the bound partner's non-offsettable load is
  below the breach load BREACH_N (0.2); at or above it the partner breaks it (WeeklyWorld.commit_decide / breaks). The breach load
  is the threshold of the bind, so removing the bind removes it.
- "rule": rule cards on `leave` that the gate enforces (imposed fixtures such as trap T1-forfeit; negotiated exit terms N5a/N5b).
  The agent asks to carry 50, 25 or 12 percent of the pot (LEAVE_TAKES), so a card that forbids those takes walls it in.
- "sanction": a standing `suspend` sanction blocks every action outside SUSPEND_ALLOWS, leave included.
- "forfeit": the breach forfeit (share of the carry-out a stay breach gives up, WeeklyWorld.breach_forfeit). Also covers the trust
  drop on a breach. Neither enters the agent's leave choice, so in the behavioral lens it can hold nobody; it does enter the bar
  lens through the holdings.
Listed but not removable as a week-level cost: the extra 1.5 living cost of living alone (an outside condition, not an exit cost;
it is inside the outside option's value), the request fine N8-fine-some (request breaches only, not leaving), vetoes and bound
requests (they block contact and spending, not leaving; the contact veto is inert for these agents, docs/results/fidelity.md).
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

import numpy as np

from . import exit_fallback as EXIT
from . import negotiation as NG
from .worlds import household as H

COSTS = ("bind", "rule", "sanction", "forfeit")
EXIT_COSTS = {
    "bind": "stay commitment, a hard wall below the breach load (N < 0.2)",
    "rule": "rule cards on leave enforced by the gate (imposed walls, negotiated exit terms)",
    "sanction": "a standing suspend sanction (blocks leave)",
    "forfeit": "breach forfeit and the trust drop on a breach",
}
NOT_REMOVED = {
    "living_alone_cost": "1.5 extra living cost per week alone: part of the outside option, not an exit cost",
    "request_fine": "N8-fine-some: applies to request breaches, not to leaving",
    "vetoes_and_bound_requests": "block contact and spending, not leaving; the contact veto is inert for scripted agents (fidelity P5)",
}
BAR_EVERY = 13            # the bar lens is read at the review cadence (negotiation.REVIEW_EVERY)
NOT_MEASURABLE = "not measurable here"


class OpenLeaveGate:
    """Wraps a gate so that `leave` is always permitted (the "rule" cost removed); every other action is checked as before."""

    def __init__(self, gate):
        self.inner = gate
        self.cards = gate.cards

    def check(self, kind, action, state, take=0):
        if action == "leave":
            return True, []
        return self.inner.check(kind, action, state, take)


class _CFMixin:
    cf_remove = frozenset()

    def decide(self, r, a, w, take=0, st=None, commit=True):
        if a != "leave" or not self.cf_remove:
            return super().decide(r, a, w, take, st, commit)
        saved = self.sanctions[r]
        if "sanction" in self.cf_remove:
            self.sanctions[r] = []
        try:
            return super().decide(r, a, w, take, st, commit and "bind" not in self.cf_remove)
        finally:
            self.sanctions[r] = saved


_CF_CLASSES = {}


def _cf_class(cls):
    if cls not in _CF_CLASSES:
        _CF_CLASSES[cls] = type("CF" + cls.__name__, (_CFMixin, cls), {})
    return _CF_CLASSES[cls]


def counterfactual_copy(world, remove):
    """A deep copy of `world` (same RNG states, so the replay is coupled to the fact) with the exit costs in `remove` taken away.
    The run history is left out of the copy (it is not read by the week step and copying it is the main cost)."""
    hook, run, world.hook, world.run = world.hook, world.run, None, H.Run()
    try:
        memo = {id(p): p for p in world.personas.values()}      # personas are read-only; sharing them saves a third of the copy
        cf = copy.deepcopy(world, memo)
    finally:
        world.hook, world.run = hook, run
    cf.__class__ = _cf_class(type(world))
    cf.cf_remove = frozenset(remove)
    if "rule" in remove:
        cf.gate = OpenLeaveGate(cf.gate)
    if "forfeit" in remove:
        cf.breach_forfeit = 0.0
    return cf


def replay_week(world, w, last, remove=COSTS):
    """-> {role: in at the end of week w} in the counterfactual with `remove` taken away. The world itself is not changed."""
    cf = counterfactual_copy(world, remove)
    cf.step_week(w, last)
    return {r: cf.p[r]["in"] for r in "AB"}


# ---- the bar lens -----------------------------------------------------------------------------------------------------------

def exit_holdings(world, r, w):
    """-> (holdings with the exit costs, holdings with them removed, walled). Uses the world's own exit mechanics (carry_out, the
    floor, the gate, the stay bind and its forfeit). Holdings = own money + what can be carried out of the pot. walled: no take in
    PROBE_TAKES is permitted by the rules and commitments (the member cannot leave at all; costed holdings are then money only)."""
    me = world.p[r]
    money = me["money"]
    takes = [t for t in H.PROBE_TAKES if world.decide(r, "leave", w, t, commit=False)[0] != "hard"]
    bound = world.mech and world.stay_bound(r, w)
    if bound:
        f = world.breach_forfeit
        lim = int(round(100 * (1 - f)))
        carry = max((world.carry_out(r, min(t, lim)) for t in takes), default=0) if f < 1.0 else (world.carry_out(r, 0) if takes else 0)
    else:
        carry = max((world.carry_out(r, t) for t in takes), default=0)
    free_carry = max([world.share(r)] + [world.carry_out(r, t) for t in takes])      # at least the equal half, more if the terms give more
    if EXIT.ACTIVE is not None:      # exit fallback switch on: with the costs removed a member also carries what they put in
        free_carry = max(free_carry, put_in(world, r))
    return money + carry, money + free_carry, not takes


def put_in(world, r):
    """What member r put in, as their share of the pot as it is now: pool x (r's pot and bill payments) / (both members' pot and bill
    payments) (ASSUMED; the F4 basis; sums to the pot, so carrying it takes nothing that is the other's own). 0 when out."""
    if not world.p[r]["in"]:
        return 0.0
    return world.pool * EXIT.contribution_share(world, r, "all")


def exit_cost(world, r, w):
    """The exit cost the rules put on member r at week w, in money units: what they put in (`put_in`) minus the most they can carry
    out of the pot by leaving now (over PROBE_TAKES; the gate, sanctions, a stay bind's forfeit and the exit fallback all count).
    Charges whatever withholds a member's own contribution: a cap, a forfeit term, a contested pot (F3: nothing until it settles).
    0 when the rules let them carry at least what they put in. -> {"put_in", "max_carry", "cost", "bigger"}; bigger: r put more into
    the household than the other member."""
    o = "B" if r == "A" else "A"
    takes = [t for t in H.PROBE_TAKES if world.decide(r, "leave", w, t, commit=False)[0] != "hard"]
    if world.mech and world.stay_bound(r, w):
        lim = int(round(100 * (1 - world.breach_forfeit)))
        takes = [min(t, lim) for t in takes]
    b = put_in(world, r)
    mx = float(max((world.carry_out(r, t) for t in takes), default=0))
    return {"put_in": b, "max_carry": mx, "cost": max(0.0, b - mx), "bigger": world.money_in[r] > world.money_in[o]}


def bar_reading(world, w, last):
    """-> {role: {"sq", "o_cost", "o_free", "walled", "verdict"}} where verdict is "worth" (SQ >= O_free), "held" (O_cost <= SQ <
    O_free) or "bar_leave" (SQ < O_cost: the bar would say leave even paying the costs; the code does not act on it)."""
    fwd = NG.forward_values(world, w, last)
    out = {}
    for r in "AB":
        p = world.personas[r]
        hc, hf, walled = exit_holdings(world, r, w)
        sq = fwd[r] - NG.trust_penalty(world.trust[r])
        oc, _ = NG.outside_value(p, r, hc, world.seed, world.hed[r])
        of, _ = NG.outside_value(p, r, hf, world.seed, world.hed[r])
        of = max(of, oc)       # more holdings can read slightly worse in a rollout (model noise); removing a cost never lowers O
        v ="worth" if sq >= of else ("held" if sq >= oc else "bar_leave")
        out[r] = {"sq": round(sq, 5), "o_cost": round(oc, 5), "o_free": round(of, 5), "walled": walled, "verdict": v,
                  "hold_cost": hc, "hold_free": hf}
    return out


def pair_bar_verdict(reading):
    vs = [reading[r]["verdict"] for r in "AB"]
    if "bar_leave" in vs:
        return "bar_leave"
    return "held" if "held" in vs else "worth"


# ---- one lived run with the stay test -----------------------------------------------------------------------------------

@dataclass
class StayWeek:
    week: int
    stayed: bool                         # both in at the start and at the end of the week (the fact)
    held: dict = field(default_factory=dict)      # role -> True if the partner leaves in the all-costs-removed replay
    causes: dict = field(default_factory=dict)    # role -> list of single costs whose removal alone lets them leave ([] = joint)
    pleasure: dict = field(default_factory=dict)  # role -> modeled pleasure that week
    bar: dict | None = None


def observe_week(world, w, last, bar=False, singles=True):
    """Run the counterfactuals for week w BEFORE the fact is played. -> partial StayWeek (stayed and pleasure filled later)."""
    sw = StayWeek(w, False)
    if bar:
        sw.bar = bar_reading(world, w, last)
    cf = replay_week(world, w, last, COSTS)
    for r in "AB":
        sw.held[r] = not cf[r]
    if singles and any(sw.held.values()):
        for r in "AB":
            if sw.held[r]:
                sw.causes[r] = [c for c in COSTS if not replay_week(world, w, last, (c,))[r]]
    return sw


def play_with_stay_test(world, lived=None, bar=True, bar_every=BAR_EVERY):
    """Play a WeeklyWorld (or a negotiation.Lived household, passed as `lived`, whose world is `world`) week by week, running the
    stay test on every week both partners start in. -> (Run, [StayWeek]). The fact is identical to an untested play: the
    counterfactuals run on deep copies."""
    last = {"busy": {"A": False, "B": False}}
    weeks = []
    for w in range(world.weeks):
        if lived is not None and lived.reviews:
            if lived.apart and w and w % NG.REVIEW_EVERY == 0:
                lived.retry(w, last)
            elif lived.bundle is not None and w and w % NG.REVIEW_EVERY == 0 and all(world.p[r]["in"] for r in "AB"):
                lived.review(w, last)
        both = all(world.p[r]["in"] for r in "AB")
        sw = None
        if both:
            sw = observe_week(world, w, last, bar=bar and w % bar_every == 0 and w > 0)
        last = {"busy": world.step_week(w, last)}
        if sw is not None:
            sw.stayed = all(world.p[r]["in"] for r in "AB")
            sw.pleasure = {r: world.run.outcomes[-1]["hedonic"][r]["pleasure"] for r in "AB"}
            weeks.append(sw)
    world.run.final = {r: {**world.p[r], "pooled": world.pool, "put": world.put[r]} for r in "AB"}
    if world.mech:
        world.run.meta = world.commit_report()
    world.run.exits = list(world.exit_log)
    return world.run, weeks


# ---- summaries ---------------------------------------------------------------------------------------------------------------

LOW_Q = 0.25         # "low": a partner-week pleasure below this quantile of all staying partner-weeks of the confirmed arm
FALL_WINDOW = 4      # "falling": the partner's mean pleasure over the last 4 weeks is below the 4 weeks before by FALL_DROP or more
FALL_DROP = 0.05


def falling(series, i, window=FALL_WINDOW, drop=FALL_DROP):
    """series: a partner's weekly pleasure over consecutive staying weeks; i: index. True if the recent window mean fell by `drop`."""
    if i + 1 < 2 * window:
        return False
    recent = np.mean(series[i + 1 - window:i + 1])
    before = np.mean(series[i + 1 - 2 * window:i + 1 - window])
    return before - recent >= drop


def run_summary(weeks):
    """Per-run counts for one run's StayWeek list (JSON-able)."""
    st = [s for s in weeks if s.stayed]
    held = [s for s in st if any(s.held.values())]
    rows = []
    for r in "AB":
        ser = [s.pleasure[r] for s in st]
        for i, s in enumerate(st):
            rows.append({"week": s.week, "role": r, "p": s.pleasure[r], "falling": falling(ser, i), "held": bool(s.held[r]),
                         "causes": s.causes.get(r)})
    bar = [s for s in weeks if s.bar is not None]
    return {
        "staying_weeks": len(st),
        "held_weeks": len(held),
        "worth_weeks": len(st) - len(held),
        "p_worth_sum": float(sum(np.mean(list(s.pleasure.values())) for s in st if not any(s.held.values()))),
        "p_held_sum": float(sum(np.mean(list(s.pleasure.values())) for s in held)),
        "partner_weeks": rows,
        "bar": [{"week": s.week, "pair": pair_bar_verdict(s.bar), **{r: s.bar[r] for r in "AB"}} for s in bar],
        "exit_weeks": len([s for s in weeks if not s.stayed]),
    }


def cause_label(causes):
    if causes is None:
        return None
    return "+".join(causes) if causes else "joint"


def ratio_ci(num, den, clusters, n_boot=4000, alpha=0.05, seed=0):
    """Ratio of sums with a percentile bootstrap that resamples whole clusters. num, den: per-unit arrays; clusters: labels.
    -> (estimate, lo, hi) or None when the denominator is 0."""
    num, den = np.asarray(num, float), np.asarray(den, float)
    if den.sum() == 0:
        return None
    keys = list(dict.fromkeys(clusters))
    idx = {k: i for i, k in enumerate(keys)}
    cn, cd = np.zeros(len(keys)), np.zeros(len(keys))
    for n, d, c in zip(num, den, clusters):
        cn[idx[c]] += n
        cd[idx[c]] += d
    est = float(num.sum() / den.sum())
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(keys), len(keys))
        d = cd[pick].sum()
        if d > 0:
            boots.append(cn[pick].sum() / d)
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return est, float(lo), float(hi)


def fmt_ci(x, nd=3):
    if x is None:
        return NOT_MEASURABLE
    return f"{x[0]:.{nd}f} [{x[1]:.{nd}f}, {x[2]:.{nd}f}]"
