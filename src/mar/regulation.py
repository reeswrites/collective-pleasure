"""Attuning versus appeasing: two partner regulation policies for the partner of a pressing persona (docs/results/regulation-prereg.md).

Theory (docs/theory.md; the author's 2026-11-10 "Attuning vs appeasing in relationships" conversation, summarized): attunement and appeasement
share an input (reading the other's emotional state) but control different variables. APPEASE capitulates to a demand, or pre-empts it, to
avoid conflict: less pain now, less pleasure later. ATTUNE reads accurately, honors what fits its own needs, declines the rest, tolerates the
other's displeasure up to a threshold, and keeps its own activation from driving what it does. Relational load is conserved: what one partner
skips lands on the other.

Extension points used (nothing in household.py is edited; every name below is ASSUMED unless it says it is the world's):
  * `WeeklyWorld.agents[role]` is a public dict and each agent is an ordinary object; `install` overrides `propose` and `consents` on the
    existing persona policy INSTANCE (the same pattern scripts/h01_control_run.py uses for the leave load). The original bound methods are
    composed, never replaced, so mode "baseline" is bit-identical to a world with no regulator.
  * the hedonic state (`world.hed[r]`) is read, never written; `world.pending`, `world.vetoes`, `world.wk` are read to build the conflict proxy.
Hooks that do NOT exist (reported in the results): a partner cannot refuse a veto or a take_shared (the world gives them no refusal action),
and there is no "state a limit" action. The only levers a partner has against a presser are consent/refusal of requests, its own action
choices, giving, and leaving; the two policies differ only through those.

Agents feel nothing. "Pleasure", "displeasure" and "load" are glosses for modeled quantities.
"""
from __future__ import annotations

from pathlib import Path

from . import hedonic as HD
from . import personas as P
from .cards import make_card
from .worlds import household as H

ROOT = Path(__file__).resolve().parents[2]
MODES = ("baseline", "appease", "attune")
PRESS_ACTS = ("request", "veto", "take_shared")      # what a presser's script does to its partner (executed rows count as pressing acts)

# ---- ASSUMED parameters (every number is an assumption; frozen in the prereg before any confirmatory run) -----------------------------
PARAMS = {
    "appease_d": 0.10,          # APPEASE concedes once the presser's displeasure is at least this (or any conflict stands)
    "appease_memory": 4,        # weeks after the last conflict during which APPEASE keeps pre-emptively conceding
    "appease_leave_n": 0.5,     # APPEASE leaves only at this non-offsettable load (the world's own trigger is 0.2) and 8 low weeks
    "appease_together": 2.0,    # APPEASE multiplies the utility of `together` time while conceding
    "appease_give": 0.14,       # utility of a pre-emptive gift to the presser (only when the world has the give mechanic)
    "attune_tol": 0.70,         # ATTUNE grants even a request that does not fit once the presser's displeasure reaches this
    "attune_fit_conn": 0.55,    # a request to stay away from the friend fits when ATTUNE's own connection level is at least this
    "attune_fit_rest": 0.45,    # a request for time fits when ATTUNE's own rest level is at least this
    "attune_cool": 2,           # ATTUNE needs its own leave trigger to hold this many consecutive weeks (own activation damps the exit)
    "attune_together": 1.3,     # ATTUNE answers a clearly unmet presser (displeasure >= 0.4) with a little more time together, if rested
}


def clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def displeasure(hed):
    """The presser's displeasure signal from its OBSERVABLE hedonic state (ASSUMED proxy): the salience-weighted unmet-need load (the
    model's own `s_need` term) plus any negative balance, clipped to [0, 1]. Read-only."""
    s_need = sum(hed.sal[n] * clip((0.5 - hed.level[n]) / 0.5) for n in HD.NEEDS)
    return clip(s_need + max(0.0, -hed.B))


def conflict(world, r):
    """Conflict proxy at the partner r right now (ASSUMED): demands standing on r (requests pending, vetoes active) plus time requests
    received this week plus a take from the shared pot by the other partner this week. 0 means no visible pressing."""
    o = world.other(r)
    wk = getattr(world, "wk", None) or {}
    return (len(world.pending[r]) + len(world.vetoes[r]) + (wk.get(r, {}).get("pressed", 0)) + (wk.get(o, {}).get("took", 0)))


def fits(world, r, kind, params=PARAMS):
    """Does honoring this request fit r's own needs (ASSUMED reading, from r's own hedonic levels only)? ATTUNE's test."""
    h = world.hed[r]
    if kind == "time":
        return h.level["rest"] >= params["attune_fit_rest"]
    if kind == "no_contact":
        return h.level["connection"] >= params["attune_fit_conn"] or h.sal["connection"] < 0.2
    if kind == "stay_home":
        return (h.level["connection"] >= params["attune_fit_conn"] or h.sal["connection"] < 0.2) and h.level["money"] >= 0.3
    return False


class Regulator:
    """Per-partner bookkeeping and the two policy bodies. One per installed agent; reads the world, writes only its own counters."""

    def __init__(self, world, role, mode, params=PARAMS):
        if mode not in MODES:
            raise ValueError(mode)
        self.world, self.role, self.mode, self.p = world, role, mode, dict(params)
        self.agent = world.agents[role]
        self._propose, self._consents = self.agent.propose, self.agent.consents      # the persona policy (composed, never replaced)
        self.last_conflict = -99
        self.trigger_run = 0
        self.yield_weeks, self.leave_blocked = set(), set()
        self.reads = []                                                              # (week, displeasure, conflict) at each propose call
        if mode != "baseline":
            self.agent.propose, self.agent.consents = self.propose, self.consents

    # -- reading the presser
    @property
    def other(self):
        return self.world.other(self.role)

    def read(self, w):
        d, c = displeasure(self.world.hed[self.other]), conflict(self.world, self.role)
        if c > 0:
            self.last_conflict = w
        return d, c

    # -- the response to a request
    def consents(self, kind):
        d, c = displeasure(self.world.hed[self.other]), conflict(self.world, self.role)
        if self.mode == "appease":
            if c >= 1 or d >= self.p["appease_d"]:
                return True                                   # capitulate, whatever it costs
            return self._consents(kind)
        return fits(self.world, self.role, kind, self.p) or d >= self.p["attune_tol"]     # attune: honor what fits; tolerate the rest

    # -- the action ranking
    def propose(self, o):
        w, r, p = o["week"], self.role, self.p
        out = list(self._propose(o))
        d, c = self.read(w)
        self.reads.append((w, round(d, 4), c))
        if not o["in_hh"] or not o["other_in"]:
            return sorted(out, key=lambda t: -t[0])
        h = o["hed"]
        trigger = o["low_weeks"] >= 4 or h.N >= 0.2 or o.get("trust", 1.0) < H.TRUST["leave_below"]
        self.trigger_run = self.trigger_run + 1 if trigger else 0
        if self.mode == "appease":
            conceding = (w - self.last_conflict) <= p["appease_memory"] or d >= p["appease_d"]
            if conceding:
                n0 = len(out)
                out = [(u * p["appease_together"], cand) if cand["a"] == "together" else (u, cand)
                       for u, cand in out if cand["a"] not in ("see_friend", "spend_self")]
                if len(out) != n0:                              # a candidate the persona wanted was given up
                    self.yield_weeks.add(w)
                if o.get("mech") and o["partner_money"] < 6 and o["own_money"] >= 8:
                    out.append((p["appease_give"], {"a": "give", "kind": "partner"}))
            if not (h.N >= p["appease_leave_n"] and o["low_weeks"] >= 8):
                if any(cand["a"] == "leave" for _, cand in out):
                    self.leave_blocked.add(w)
                out = [(u, cand) for u, cand in out if cand["a"] != "leave"]
        else:                                                   # attune
            if d >= 0.4 and h.level["rest"] >= p["attune_fit_rest"]:
                out = [(u * p["attune_together"], cand) if cand["a"] == "together" else (u, cand) for u, cand in out]
            if self.trigger_run < p["attune_cool"]:             # own activation damps the exit: the trigger must have held for a while
                if any(cand["a"] == "leave" for _, cand in out):
                    self.leave_blocked.add(w)
                out = [(u, cand) for u, cand in out if cand["a"] != "leave"]
        return sorted(out, key=lambda t: -t[0])


def install(world, role, mode, params=PARAMS):
    """Put the regulation policy `mode` on the partner `role` of a built (not yet played) WeeklyWorld. Returns the Regulator."""
    return Regulator(world, role, mode, params)


# ---- running a pairing ----------------------------------------------------------------------------------------------------------------

PRESSERS = ("p-controller", "p-freerider", "p-overasker")
RULESETS = ("author_seed_v2_free_exit", "baseline", "no_exit")
NO_EXIT_CARD = {"id": "REG-no-exit", "attribute": "partner", "deontic": "must_not", "aim": "leave", "conditions": [], "or_else": None,
                "gloss": "A partner may never leave.",
                "source": "regulation control (docs/results/regulation-prereg.md): the free_exit cards plus one unconditional hard prohibition on leaving."}
_PS: dict = {}


def personas():
    if not _PS:
        _PS.update({p.id: p for p in P.load_dir(ROOT / "personas") + P.load_dir(ROOT / "personas" / "pressing")})
    return _PS


def cards_for(ruleset):
    if ruleset == "no_exit":
        return H.load_variant("author_seed_v2_free_exit") + [make_card(NO_EXIT_CARD)]
    return H.load_variant(ruleset)


def pairings():
    """(presser, partner, presser_role): 3 pressers x 6 non-pressing personas x 2 seatings = 36."""
    ps = personas()
    others = sorted(i for i in ps if i not in PRESSERS)
    return [(f, o, role) for f in PRESSERS for o in others for role in "AB"]


def run_pair(ruleset, presser, partner, role, seed, mode, weeks=H.WEEKS, params=PARAMS):
    """One run: the presser (its own pressing script, unchanged) plays Partner `role`; the partner gets regulation `mode`.
    -> dict of per-run measures (lifetime pleasure = sum over weeks of the weekly modeled pleasure, levers off)."""
    ps = personas()
    other = "B" if role == "A" else "A"
    pa, pb = (ps[presser], ps[partner]) if role == "A" else (ps[partner], ps[presser])
    w = H.WeeklyWorld(cards_for(ruleset), (pa, pb), seed, weeks)
    reg = install(w, other, mode, params)
    run = w.play()
    out = run.outcomes
    hr = lambda r, k: sum(o["hedonic"][r][k] for o in out)
    acts = [t for t in run.trace if t["role"] == role and t["action"] in PRESS_ACTS and t["executed"]]
    refused = {t["week"] for t in run.trace if t["role"] == other and t["action"] == "refuse_request" and t["executed"]}
    left = {r: not out[-1]["partners"][r]["in"] for r in "AB"}
    leave_wk = {r: next((t["week"] for t in run.trace if t["role"] == r and t["action"] == "leave" and t["executed"]), None) for r in "AB"}
    return {"ruleset": ruleset, "presser": presser, "partner": partner, "role": role, "seed": seed, "mode": mode,
            "presser_pleasure": hr(role, "pleasure"), "partner_pleasure": hr(other, "pleasure"),
            "gain": hr(role, "pleasure") - hr(other, "pleasure"),
            "pressing_acts": len(acts), "conflict_weeks": len({t["week"] for t in acts}), "refusal_weeks": len(refused),
            "yield_weeks": len(reg.yield_weeks), "leave_blocked_weeks": len(reg.leave_blocked),
            "partner_left": left[other], "presser_left": left[role], "partner_leave_week": leave_wk[other],
            "weeks_together": sum(1 for o in out if o["both_in"])}
