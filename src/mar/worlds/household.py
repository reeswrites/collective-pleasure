"""Household world: two partners (A, B) and an outside friend (C), monthly steps, deterministic dynamics.

Roles are abstract. "Earner" only means Partner A has the higher income in the fixture.
Everything here is scripted; no LLM, no network. The intent oracle (household_oracle.py) never
sees rules; this module is where rules meet the world.

Adapter note (ASSUMED): compile.py, gate.py and patch_check.py are fishery-specific (fixed variables
pool, month_total, catch). Instead of modifying them, this file (a) reuses cards.py unchanged, (b) reuses
compile.violation / english.render / english.parse unchanged by temporarily swapping in the household
variable names (`household_namespace`, restored on exit), (c) re-implements the gate and the proof checks
over the household variables with the same semantics as V2 (must_not: violated when all conditions hold;
must: violated unless all hold; may: no constraint) and reuses patch_check.check_sanctions as is.

Card vocabulary. Cards select their action by `aim` and their actor by `attribute` (partner | friend);
aim "any" applies to every action. Condition variables (all integers):
  pooled (actor's share of pooled assets), money (actor's private money), other_earns_more (1 for Partner B),
  no_contact_request / stay_home_request (1 if the other partner has such a request standing on the actor),
  consented (1 if the actor agreed to the standing request), bound_request (1 if the standing request is one the actor
  earlier chose to bind themselves to honor; seed v2 commitments), need_gap (unfunded part of this month's shared
  need), months_in (months in the household), other_in (1 if the other partner is in the household),
  refused_recently (1 for a few weeks after the other refused this kind of request; seed v2.3 decency floor, only set when the
  `decency` fix is on, else 0), take (percent of the actor's pooled share carried out on `leave`; 0 for every other action).
"""
import random
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

import z3

from .. import compile as _compile
from .. import english as _english
from ..cards import load_cards
from .. import exit_fallback as _EXIT
from .. import exit_items as _ITEMS
from .. import observe as _OBS
from .. import makers as _MAKERS
from .. import pairing as _PAIR
from .. import agent_values as _AV
from .. import hybrid as _HY
from ..patch_check import check_sanctions

ROOT = Path(__file__).resolve().parents[3]
RULES = ROOT / "rules" / "household"

# ---- vocabulary and bounds -------------------------------------------------------------------

STATE_VARS = ("pooled", "money", "other_earns_more", "no_contact_request", "stay_home_request", "consented",
              "need_gap", "months_in", "other_in", "bound_request", "refused_recently")
OPTIONAL_VARS = {"bound_request": 0, "refused_recently": 0}     # state producers that predate a variable may omit it; it then reads as this default
VAR_NAMES = STATE_VARS + ("take",)
Z = dict(zip(VAR_NAMES, z3.Ints(" ".join(VAR_NAMES))))
BOUNDS = {"pooled": (0, 100), "money": (0, 100), "other_earns_more": (0, 1), "no_contact_request": (0, 1),
          "stay_home_request": (0, 1), "consented": (0, 1), "need_gap": (0, 10), "months_in": (0, 36),
          "other_in": (0, 1), "bound_request": (0, 1), "refused_recently": (0, 1), "take": (0, 100)}
PHRASES = {"pooled": "the pooled share", "money": "the private money", "other_earns_more": "the earns-more flag",
           "no_contact_request": "the no-contact request flag", "stay_home_request": "the stay-home request flag",
           "consented": "the consent flag", "need_gap": "the unfunded need", "months_in": "the months in the household",
           "other_in": "the other-partner-in flag", "bound_request": "the bound-request flag",
           "refused_recently": "the refused-recently flag", "take": "the share taken"}
PARTNER_ACTIONS = ("work", "spend_shared", "spend_self", "see_friend", "refuse_request", "request", "leave", "return")
EXTRA_ACTIONS = ("gift_pooled", "give", "commit_stay", "commit_request", "amend", "ritual", "role", "checkin")   # harness-only move (side channel); the formal model in seam_depth does not have it
GIFT = 8
FRIEND_ACTIONS = ("work", "spend_self", "see_friend", "refuse_request")
K_DEFAULT = 3
MIN_EXIT_TAKE = 25          # meaningful exit: leave carrying at least 25 percent of the pooled share
SUSPEND_ALLOWS = ("work", "spend_shared", "refuse_request")   # ASSUMED meaning of the suspend sanction
CAP_HALVE_BANS = ("spend_self",)                               # ASSUMED meaning of cap_halve
VARIANTS = ("free_chaotic", "trap", "contact_free", "exit_half", "veto_consent", "needs_duty", "baseline")
V2_VARIANTS = VARIANTS + ("author_seed",)


@contextmanager
def household_namespace():
    """Swap the household variable names into compile.VARS and the English tables, then restore."""
    saved = (dict(_compile.VARS), dict(_english.VAR_WORDS), dict(_english.WORD_VARS))
    try:
        _compile.VARS.clear(); _compile.VARS.update(Z)
        _english.VAR_WORDS.clear(); _english.VAR_WORDS.update(PHRASES)
        _english.WORD_VARS.clear(); _english.WORD_VARS.update({v: k for k, v in PHRASES.items()})
        yield
    finally:
        _compile.VARS.clear(); _compile.VARS.update(saved[0])
        _english.VAR_WORDS.clear(); _english.VAR_WORDS.update(saved[1])
        _english.WORD_VARS.clear(); _english.WORD_VARS.update(saved[2])


def load_variant(name):
    return load_cards(RULES / name)


def render_card(card):
    with household_namespace():
        return _english.render(card)


def parse_card(text):
    with household_namespace():
        return _english.parse(text)


def violations(cards, action, kind="partner"):
    """{card id: z3 Bool violated} for the cards that apply to this actor kind and action."""
    with household_namespace():
        return {c.id: v for c in cards
                if c.attribute == kind and c.aim in (action, "any") and (v := _compile.violation(c)) is not None}


# ---- the gate --------------------------------------------------------------------------------

class HouseholdGate:
    def __init__(self, cards):
        self.cards = list(cards)
        self._v = {(k, a): violations(self.cards, a, k)
                   for k, acts in (("partner", PARTNER_ACTIONS + EXTRA_ACTIONS), ("friend", FRIEND_ACTIONS)) for a in acts}
        self._cache = {}

    def check(self, kind, action, state, take=0):
        """-> (allowed, reasons) for one proposed action; reasons are violated card ids."""
        state = {**OPTIONAL_VARS, **state}
        key = (kind, action, take, tuple(state[n] for n in STATE_VARS))
        if key not in self._cache:
            sub = [(Z[n], z3.IntVal(state[n])) for n in STATE_VARS] + [(Z["take"], z3.IntVal(take))]
            reasons = [cid for cid, v in self._v.get((kind, action), {}).items()
                       if z3.is_true(z3.simplify(z3.substitute(v, *sub)))]
            self._cache[key] = (not reasons, reasons)
        return self._cache[key]


# ---- proof checks (bounded; verdicts pass / fail / open, never "safe") -------------------------

def bound_text(k=K_DEFAULT):
    return (f"k={k} months (sanction length, exit wait); pooled 0..100, money 0..100, months_in 0..36, "
            f"need_gap 0..10, flags 0..1, leave take 0..100")


def _domain(action):
    d = [Z[n] >= lo for n, (lo, _) in BOUNDS.items() if n != "take"] + \
        [Z[n] <= hi for n, (_, hi) in BOUNDS.items() if n != "take"]
    return z3.And(*d)


def _take_dom(action, lo=0):
    return z3.And(Z["take"] >= lo, Z["take"] <= 100) if action == "leave" else (Z["take"] == 0)


def _ok(vs):
    return z3.Not(z3.Or(*vs.values())) if vs else z3.BoolVal(True)


def _solve(formula):
    s = z3.Solver()
    s.set("timeout", 10000)
    s.add(_domain(None), formula)
    r = s.check()
    if r == z3.sat:
        m = s.model()
        return "sat", {n: m.eval(Z[n], True).as_long() for n in STATE_VARS}
    return ("unsat" if r == z3.unsat else "unknown"), None


def _blocked(vs_by_action, actions, lo_take=0):
    """Formula: for every action in `actions` and every legal take, some card is violated."""
    return z3.And(*[z3.ForAll([Z["take"]], z3.Implies(_take_dom(a, lo_take if a == "leave" else 0), z3.Not(_ok(vs_by_action[a]))))
                    for a in actions])


def _core(cards, actions, witness, extra_actions_only=None, lo_take=0):
    """Deletion-based minimal set of cards that still leaves every action in `actions` blocked at witness."""
    cur = list(cards)

    def stuck(cs):
        vs = {a: violations(cs, a) for a in actions}
        sub = [(Z[n], z3.IntVal(witness[n])) for n in STATE_VARS]
        f = z3.And(*[z3.ForAll([Z["take"]], z3.Implies(_take_dom(a, lo_take if a == "leave" else 0),
                                                       z3.substitute(z3.Not(_ok(vs[a])), *sub))) for a in actions])
        s = z3.Solver(); s.add(f)
        return s.check() == z3.sat
    for c in list(cur):
        trial = [x for x in cur if x.id != c.id]
        if stuck(trial):
            cur = trial
    return sorted(c.id for c in cur if any(c.aim in (a, "any") for a in actions))


def check_conflict(cards):
    """(a) no must / must_not pair on the same aim and actor that cannot both be met in some state."""
    bad, unknown = [], False
    with household_namespace():
        for m in (c for c in cards if c.deontic == "must"):
            for n in (c for c in cards if c.deontic == "must_not" and c.aim == m.aim and c.attribute == m.attribute):
                vm, vn = _compile.violation(m), _compile.violation(n)
                a = m.aim if m.aim in PARTNER_ACTIONS else "work"
                verdict, wit = _solve(z3.ForAll([Z["take"]], z3.Implies(_take_dom(a), z3.Or(vm, vn))))
                if verdict == "sat":
                    bad.append({"cards": [m.id, n.id], "witness": wit})
                elif verdict == "unknown":
                    unknown = True
    if bad:
        ids = sorted({i for b in bad for i in b["cards"]})
        return "fail", ids, f"conflicting pairs {[b['cards'] for b in bad]}; example state {bad[0]['witness']}"
    return ("open", [], "solver gave up") if unknown else ("pass", [], "no conflicting must/must_not pair")


def check_deadlock(cards):
    """(b) in every state within bounds some partner action is permitted."""
    vs = {a: violations(cards, a) for a in PARTNER_ACTIONS}
    verdict, wit = _solve(_blocked(vs, PARTNER_ACTIONS))
    if verdict == "sat":
        return "fail", _core(cards, PARTNER_ACTIONS, wit), f"no permitted action at state {wit}"
    return ("open", [], "solver gave up") if verdict == "unknown" else ("pass", [], "a permitted action exists in every state")


def check_repair(cards, k=K_DEFAULT):
    """(d) while any sanction applies, a partner still has a permitted action in every state, and it ends within k."""
    stuck, slow = [], []
    for c in cards:
        s = c.or_else
        if not s or s.get("kind") not in ("warn", "cap_halve", "suspend") or not isinstance(s.get("duration_months"), int):
            continue  # malformed sanctions are check (c)'s failure
        allowed = {"warn": PARTNER_ACTIONS, "cap_halve": tuple(a for a in PARTNER_ACTIONS if a not in CAP_HALVE_BANS),
                   "suspend": SUSPEND_ALLOWS}[s["kind"]]
        verdict, wit = _solve(_blocked({a: violations(cards, a) for a in allowed}, allowed))
        if verdict == "sat":
            stuck.append(c.id)
        elif verdict == "unknown" or s["duration_months"] > k:
            slow.append(c.id)
    if stuck:
        return "fail", stuck, "under this sanction some state leaves no permitted action: no repair path"
    if slow:
        return "open", slow, f"repair not shown within k={k} months (sanction longer than k, or solver gave up)"
    return "pass", [], f"every sanction leaves a permitted action in every state and ends within k={k} months"


def check_exit(cards, k=K_DEFAULT):
    """(e) exit within k: in every state a leave carrying >= MIN_EXIT_TAKE percent of the pooled share is permitted
    now or after waiting at most k months (waiting only raises months_in). Sufficient proxy for 'does not lose
    everything'; it ignores the partner's private money (ASSUMED)."""
    vs = violations(cards, "leave")
    parts = []
    for t in range(k + 1):
        shifted = {cid: z3.substitute(v, (Z["months_in"], Z["months_in"] + t)) for cid, v in vs.items()}
        parts.append(z3.ForAll([Z["take"]], z3.Implies(_take_dom("leave", MIN_EXIT_TAKE), z3.Not(_ok(shifted)))))
    verdict, wit = _solve(z3.And(*parts))
    if verdict == "sat":
        return ("fail", _core(cards, ("leave",), wit, lo_take=MIN_EXIT_TAKE),
                f"no exit within k={k}: at state {wit} every leave carrying {MIN_EXIT_TAKE}% or more is blocked")
    return (("open", [], "solver gave up") if verdict == "unknown"
            else ("pass", [], f"in every state a leave carrying {MIN_EXIT_TAKE}% or more is permitted within k={k} months"))


CHECK_TITLES = {"a_no_conflict": "No two rules contradict each other",
                "b_no_deadlock": "A partner always has some allowed action",
                "c_bounded_sanctions": "Every sanction is finite and of a known kind",
                "d_repair_path": "A sanctioned partner can get back to following the rules",
                "e_exit_within_k": "Every partner can leave with something within k months"}


def check_spec(cards, k=K_DEFAULT):
    out = []
    for name, fn in (("a_no_conflict", check_conflict), ("b_no_deadlock", check_deadlock),
                     ("c_bounded_sanctions", check_sanctions), ("d_repair_path", lambda c: check_repair(c, k)),
                     ("e_exit_within_k", lambda c: check_exit(c, k))):
        verdict, ids, detail = fn(cards)
        out.append({"check": name, "verdict": verdict, "cards": ids, "detail": detail, "bound": bound_text(k)})
    return out


def explain_verdict(v, cards=None):
    """Plain-English line for a household verdict (fallback: english.explain_verdict is fishery-specific)."""
    cm = {c.id: c for c in cards or []}
    title = CHECK_TITLES.get(v["check"], v["check"])
    ids = ", ".join(f"{i} ({cm[i].gloss.rstrip('.')})" if i in cm else i for i in v["cards"]) or "none"
    if v["verdict"] == "pass":
        return f"{title}: passes. Bound: {v['bound']}."
    if v["verdict"] == "open":
        return f"{title}: not shown (this does not mean it is safe). Rules involved: {ids}. Bound: {v['bound']}."
    why = {"e_exit_within_k": "There is a situation where every way out leaves the partner with almost nothing "
                              "or is blocked outright, even after waiting.",
           "b_no_deadlock": "There is a situation where the rules leave a partner no allowed action.",
           "a_no_conflict": "Two rules ask for opposite things.",
           "d_repair_path": "While a sanction applies there is a situation with no allowed way back.",
           "c_bounded_sanctions": "A sanction never ends or is not a known kind."}.get(v["check"], "")
    return f"{title}: fails. {why} Rules involved: {ids}. Bound: {v['bound']}."


# ---- world dynamics --------------------------------------------------------------------------

MONTHS, SLOTS, HOURS, NEED = 12, 3, 8, 10
COST_HOURS = {"work": 4, "see_friend": 2, "spend_shared": 1, "spend_self": 1}
INCOME = {"A": 8, "B": 6}
SHARE_STEP, SELF_STEP, SUBSIST = 3, 2, 6
PROBE_TAKES = (0, 10, 25, 50, 75, 100)
REQUEST_KINDS = ("no_contact", "stay_home")


@dataclass
class Run:
    trace: list = field(default_factory=list)      # one row per proposal
    outcomes: list = field(default_factory=list)   # one row per month (what the oracle sees)
    final: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)       # seed v2: commitments made / honored / breached, gifts


def _partner_init():
    return {"money": 5, "pooled": 45, "hours": HOURS, "wellbeing": 10, "contact": 5, "in": True,
            "months_in": 0, "retained": None, "contrib": 0}


class World:
    def __init__(self, cards, agents, seed=0, months=MONTHS):
        """agents: dict with keys A, B, C -> objects with propose(obs) -> list of candidate actions."""
        self.gate = cards if isinstance(cards, HouseholdGate) else HouseholdGate(cards)
        self.agents, self.months, self.seed = agents, months, seed
        for i, r in enumerate("ABC"):
            agents[r].rng = random.Random(seed * 1000 + i)
        self.p = {"A": _partner_init(), "B": _partner_init()}
        self.c = {"money": 20, "wellbeing": 10, "hours": HOURS}
        self.pending = {"A": set(), "B": set()}
        self.consent = {"A": 0, "B": 0}
        self.funded = 0
        self.blocked_last = {"A": 0, "B": 0}
        self.run = Run()

    # -- state seen by the gate
    def other(self, r):
        return "B" if r == "A" else "A"

    def need(self):
        n_in = sum(1 for r in "AB" if self.p[r]["in"])
        return {2: NEED, 1: 6, 0: 0}[n_in]

    def gate_state(self, r):
        me, o = self.p[r], self.p[self.other(r)]
        pend = self.pending[r]
        return {"pooled": me["pooled"], "money": me["money"], "other_earns_more": 1 if r == "B" else 0,
                "no_contact_request": int("no_contact" in pend), "stay_home_request": int("stay_home" in pend),
                "consented": int(bool(pend) and bool(self.consent[r])),
                "need_gap": max(0, self.need() - self.funded) if me["in"] or o["in"] else 0,
                "months_in": me["months_in"], "other_in": int(o["in"])}

    def feasible(self, r, a, kind=None):
        me, o = self.p[r], self.p[self.other(r)]
        if a in COST_HOURS and me["hours"] < COST_HOURS[a]:
            return False
        if a == "spend_shared":
            return me["in"] and me["money"] >= SHARE_STEP
        if a == "spend_self":
            return me["money"] >= SELF_STEP
        if a == "request":
            return me["in"] and o["in"] and kind in REQUEST_KINDS
        if a == "leave":
            return me["in"]
        if a == "gift_pooled":
            return me["in"] and o["in"] and me["money"] >= GIFT
        if a == "return":
            return (not me["in"]) and o["in"]
        return True

    def retained_fraction(self, r, take):
        me = self.p[r]
        total = me["money"] + me["pooled"]
        return 1.0 if total == 0 else (me["money"] + take / 100 * me["pooled"]) / total

    # -- probes for the oracle (rules are applied here; the oracle only sees the resulting numbers)
    def probe(self, r):
        me = self.p[r]
        st = self.gate_state(r)
        ok = lambda a, take=0: self.gate.check("partner", a, st, take)[0]
        spend = (ok("spend_shared") and me["in"] and me["money"] >= SHARE_STEP) or (ok("spend_self") and me["money"] >= SELF_STEP)
        if me["in"]:
            retained = max([self.retained_fraction(r, t) for t in PROBE_TAKES if ok("leave", t)] or [0.0])
        else:
            retained = me["retained"] if me["retained"] is not None else 1.0
        opts = {"work": ok("work") and me["hours"] >= 4, "spend": bool(spend),
                "see_friend": ok("see_friend") and me["hours"] >= 2, "refuse": ok("refuse_request"),
                "leave": True if not me["in"] else retained >= 0.25}
        return {"in": me["in"], "open": opts, "exit_retained": round(retained, 4)}

    # -- obs
    def obs(self, r, month, slot):
        me, o = self.p[r], self.p[self.other(r)]
        return {"month": month, "slot": slot, "role": r, "me": dict(me), "other": dict(o), "hours": me["hours"],
                "money": me["money"], "need_gap": self.gate_state(r)["need_gap"], "other_in": o["in"],
                "pending_on_me": sorted(self.pending[r]), "pending_by_me": sorted(self.pending[self.other(r)]),
                "blocked_last_month": self.blocked_last[r], "in": me["in"]}

    # -- applying one action
    def apply(self, r, cand, month, row):
        a, me = cand["a"], self.p[r]
        o = self.p[self.other(r)]
        me["hours"] -= COST_HOURS.get(a, 0)
        if a == "work":
            me["money"] += INCOME[r]
        elif a == "spend_shared":
            me["money"] -= SHARE_STEP
            if self.funded >= self.need():
                me["pooled"] += SHARE_STEP   # surplus becomes pooled savings
            else:
                self.funded += SHARE_STEP
            me["contrib"] += 1
        elif a == "spend_self":
            me["money"] -= SELF_STEP
            me["wellbeing"] = min(20, me["wellbeing"] + 1)
        elif a == "see_friend":
            me["contact"] = min(10, me["contact"] + 2)
            me["wellbeing"] = min(20, me["wellbeing"] + 2)
            self.c["wellbeing"] = min(20, self.c["wellbeing"] + 1)
        elif a == "refuse_request":
            self.pending[r] = set()
        elif a == "request":
            tgt = self.other(r)
            self.pending[tgt].add(cand["kind"])
            self.consent[tgt] = int(bool(self.agents[tgt].consents(cand["kind"])))
        elif a == "gift_pooled":
            me["money"] -= GIFT
            o["pooled"] += GIFT
        elif a == "leave":
            take = cand.get("take", 0)
            self.p[r]["retained"] = round(self.retained_fraction(r, take), 4)
            carry = me["pooled"] * take // 100
            me["money"] += carry
            if o["in"]:
                o["pooled"] += me["pooled"] - carry   # forfeited share stays with the household
            me["pooled"], me["in"], self.pending[r] = 0, False, set()
            row["retained"] = self.p[r]["retained"]
        elif a == "return":
            me["in"], me["months_in"] = True, 0

    def friend_attempt(self, month, rec):
        tgt = "A" if month % 2 == 0 else "B"
        allowed, _ = self.gate.check("partner", "see_friend", self.gate_state(tgt))
        rec["c_attempts"] += 1
        if allowed:
            self.p[tgt]["contact"] = min(10, self.p[tgt]["contact"] + 2)
            self.p[tgt]["wellbeing"] = min(20, self.p[tgt]["wellbeing"] + 1)
            self.c["wellbeing"] = min(20, self.c["wellbeing"] + 1)
        else:
            rec["c_blocked"] += 1
            self.c["wellbeing"] = max(0, self.c["wellbeing"] - 1)
        return tgt, allowed

    def step_agent(self, r, month, slot, rec):
        kind = "partner" if r in "AB" else "friend"
        if r == "C":
            return self.step_friend(month, slot, rec)
        cands = self.agents[r].propose(self.obs(r, month, slot))
        for cand in cands:
            a, take = cand["a"], cand.get("take", 0)
            if not self.feasible(r, a, cand.get("kind")):
                continue
            allowed, reasons = self.gate.check(kind, a, self.gate_state(r), take)
            row = {"month": month, "slot": slot, "role": r, "action": a, "take": take, "kind": cand.get("kind"),
                   "allowed": allowed, "executed": allowed, "reasons": list(reasons),
                   "state": self.gate_state(r)}
            self.run.trace.append(row)
            if allowed:
                self.apply(r, cand, month, row)
                rec["acted"][r].append(a)
                return
            rec["blocked"][r] += 1

    def step_friend(self, month, slot, rec):
        if slot == 0:
            tgt, allowed = self.friend_attempt(month, rec)
            self.run.trace.append({"month": month, "slot": slot, "role": "C", "action": "see_friend", "take": 0,
                                   "kind": None, "allowed": allowed, "executed": allowed,
                                   "reasons": [] if allowed else ["blocked by the partner's rules"],
                                   "state": self.gate_state(tgt), "target": tgt})
        elif slot == 1:
            self.c["money"] += 3
        else:
            self.c["money"] = max(0, self.c["money"] - 2)

    def step_month(self, month):
        for r in "AB":
            self.p[r]["hours"], self.p[r]["contrib"] = HOURS, 0
        self.funded = 0
        probes = {r: self.probe(r) for r in "AB"}
        rec = {"acted": {r: [] for r in "ABC"}, "blocked": {r: 0 for r in "AB"}, "c_attempts": 0, "c_blocked": 0}
        for slot in range(SLOTS):
            for r in "ABC":
                self.step_agent(r, month, slot, rec)
        need, funded = self.need(), self.funded
        met = need > 0 and funded >= need
        for r in "AB":
            me = self.p[r]
            if me["in"]:
                if need > 0 and not met:
                    me["wellbeing"] = max(0, me["wellbeing"] - 2)
                me["months_in"] += 1
            else:
                pay = min(SUBSIST, me["money"])
                me["money"] -= pay
                if pay < SUBSIST:
                    me["wellbeing"] = max(0, me["wellbeing"] - 2)
            me["contact"] = max(0, me["contact"] - 1)
            if me["contact"] < 3:
                me["wellbeing"] = max(0, me["wellbeing"] - 1)
            self.blocked_last[r] = rec["blocked"][r]
        both_in = all(self.p[r]["in"] for r in "AB")
        self.run.outcomes.append({
            "month": month, "need_met": met, "both_in": both_in,
            "partners": {r: {**probes[r], "contributed": self.p[r]["contrib"] > 0 and self.p[r]["in"]} for r in "AB"},
            "c_attempts": rec["c_attempts"], "c_blocked": rec["c_blocked"],
            "wellbeing": {"A": self.p["A"]["wellbeing"], "B": self.p["B"]["wellbeing"], "C": self.c["wellbeing"]},
            "acted": rec["acted"], "blocked": rec["blocked"]})

    def play(self):
        for m in range(self.months):
            self.step_month(m)
        self.run.final = {r: dict(self.p[r]) for r in "AB"} | {"C": dict(self.c)}
        return self.run


def run_household(cards, agents, seed=0, months=MONTHS):
    return World(cards, agents, seed, months).play()


# ---- scripted agents ---------------------------------------------------------------------------
# propose(obs) -> ordered candidate list; the world executes the first one that is physically possible
# and that the gate permits. consents(kind) -> whether the agent agrees to a request put to it.

def _a(a, **kw):
    return {"a": a, **kw}


class Cooperator:
    def consents(self, kind):
        return True

    def propose(self, o):
        if not o["in"]:
            return [_a("work"), _a("spend_self"), _a("see_friend")]
        gap = [_a("spend_shared")] if o["need_gap"] > 0 else []
        if o["slot"] == 0:
            return [_a("work")] + gap + [_a("see_friend")]
        if o["slot"] == 1:
            return gap + [_a("work"), _a("see_friend")]
        return gap + [_a("see_friend") if self.rng.random() < 0.7 else _a("spend_self"), _a("work")]


class Controller:
    """Issues requests (no outside contact, stay home) and relies on the rules to make them bind."""
    def consents(self, kind):
        return False

    def propose(self, o):
        if not o["in"]:
            return [_a("work"), _a("spend_self")]
        standing = set(o["pending_by_me"])
        out = []
        if o["other_in"] and o["slot"] == 0:
            out += [_a("request", kind=k) for k in REQUEST_KINDS if k not in standing][:1]
        if o["need_gap"] > 0:
            out.append(_a("spend_shared"))
        return out + [_a("work"), _a("see_friend"), _a("spend_self")]


class Independent:
    """Spends on self, works, sees the friend, refuses requests, never funds the shared need."""
    def consents(self, kind):
        return False

    def propose(self, o):
        out = [_a("refuse_request")] if o["pending_on_me"] else []
        order = [[_a("work"), _a("see_friend"), _a("spend_self")], [_a("see_friend"), _a("spend_self"), _a("work")],
                 [_a("spend_self"), _a("work"), _a("see_friend")]][o["slot"] % 3]
        return out + order + [_a("work"), _a("see_friend")]


class Leaver(Cooperator):
    """Acts like a cooperator, but when constrained (blocked last month or a request standing on them)
    tries to exit, preferring to keep a real share (100, 50, then 25 percent); never forfeits."""
    def consents(self, kind):
        return False

    def propose(self, o):
        base = super().propose(o)
        if o["in"] and (o["blocked_last_month"] > 0 or o["pending_on_me"]):
            return [_a("leave", take=t) for t in (100, 50, 25)] + \
                   ([_a("refuse_request")] if o["pending_on_me"] else []) + base
        return base


class Friend:
    def consents(self, kind):
        return True

    def propose(self, o):
        return []


class Explorer:
    """Random actions with random parameters, for mining de facto rules."""
    def consents(self, kind):
        return self.rng.random() < 0.5

    def propose(self, o):
        acts = list(PARTNER_ACTIONS)
        self.rng.shuffle(acts)
        out = []
        for a in acts[:3]:
            out.append(_a(a, take=self.rng.choice((0, 10, 25, 50, 75, 100)) if a == "leave" else 0,
                          **({"kind": self.rng.choice(REQUEST_KINDS)} if a == "request" else {})))
        return out


MIXES = {"coop+coop": (Cooperator, Cooperator), "ctrl+coop": (Controller, Cooperator),
         "ctrl+leaver": (Controller, Leaver), "indep+indep": (Independent, Independent),
         "coop+leaver": (Cooperator, Leaver), "ctrl+indep": (Controller, Independent)}


def make_agents(mix):
    a, b = MIXES[mix]
    return {"A": a(), "B": b(), "C": Friend()}


# ---- mining de facto rules from a trace ------------------------------------------------------------

TAKE_REPS = {"none": 0, "low": 25, "half": 50, "high": 100}


def signature(state, take):
    """Boolean features of a gate state; the miner never sees raw numbers beyond these."""
    return {"other_earns_more": state["other_earns_more"], "no_contact_request": state["no_contact_request"],
            "stay_home_request": state["stay_home_request"], "consented": state["consented"],
            "need_gap>0": int(state["need_gap"] > 0), "pooled>0": int(state["pooled"] > 0),
            "take>0": int(take > 0), "take<50": int(take < 50), "take>50": int(take > 50)}


def _sig_key(sig):
    return tuple(sorted(sig.items()))


def _matches(conj, sig):
    return all(sig[k] == v for k, v in conj.items())


def mine(rows):
    """Per action, the smallest feature conjunctions that separate rejected from accepted observations (greedy set
    cover over rejected signatures). -> {action: {"rules": [conj dicts], "n_rej": int, "unexplained": int}}.
    A rejected signature that is identical to an accepted one cannot be explained by these features."""
    from itertools import combinations
    rej, acc = {}, {}
    for r in rows:
        if r["role"] == "C":
            continue
        (rej if not r["allowed"] else acc).setdefault(r["action"], {})[_sig_key(signature(r["state"], r["take"]))] = 1
    out = {}
    for a, rs in rej.items():
        accepted = [dict(k) for k in acc.get(a, {})]
        todo = [dict(k) for k in rs]
        rules, unexplained = [], 0
        feats = list(todo[0])
        while todo:
            sig = todo[0]
            best = None
            for size in range(0, len(feats) + 1):
                cands = [dict((f, sig[f]) for f in sub) for sub in combinations(feats, size)]
                cands = [c for c in cands if not any(_matches(c, x) for x in accepted)]
                if cands:
                    best = max(cands, key=lambda c: sum(_matches(c, t) for t in todo))
                    break
            if best is None:
                unexplained += 1
                todo = todo[1:]
                continue
            rules.append(best)
            todo = [t for t in todo if not _matches(best, t)]
        out[a] = {"rules": rules, "n_rej": len(rs), "unexplained": unexplained}
    return out


def _rep_state(sig, take_rep):
    return {"pooled": 40 if sig["pooled>0"] else 0, "money": 5, "other_earns_more": sig["other_earns_more"],
            "no_contact_request": sig["no_contact_request"], "stay_home_request": sig["stay_home_request"],
            "consented": sig["consented"], "need_gap": 4 if sig["need_gap>0"] else 0, "months_in": 3, "other_in": 1}


def compare_mined(cards, rows):
    """Diff mined rejection rules against the written gate. Observed = signatures the trace visited; grid = every
    realisable signature (reported, an unvisited disagreement is a coverage gap, not a failure)."""
    import itertools
    gate, mined = HouseholdGate(cards), mine(rows)
    acts = [a for a in PARTNER_ACTIONS]
    seen = {}
    for r in rows:
        if r["role"] != "C":
            seen.setdefault(r["action"], set()).add(_sig_key(signature(r["state"], r["take"])))
    res = {"observed": 0, "disagree_observed": 0, "grid": 0, "disagree_grid": 0, "mined_rules": {}}
    for a, m in mined.items():
        res["mined_rules"][a] = m["rules"]
    for a in acts:
        rules = mined.get(a, {"rules": []})["rules"]
        takes = TAKE_REPS.values() if a == "leave" else (0,)
        for flags in itertools.product((0, 1), repeat=6):
            base = dict(zip(("other_earns_more", "no_contact_request", "stay_home_request", "consented", "need_gap>0",
                             "pooled>0"), flags))
            for take in takes:
                sig = {**base, **{k: v for k, v in signature(_rep_state(base, take), take).items() if k.startswith("take")}}
                st = _rep_state(base, take)
                written_rej = not gate.check("partner", a, st, take)[0]
                mined_rej = any(_matches(c, sig) for c in rules)
                res["grid"] += 1
                bad = written_rej != mined_rej
                res["disagree_grid"] += bad
                if _sig_key(sig) in seen.get(a, ()):
                    res["observed"] += 1
                    res["disagree_observed"] += bad
    return res


# =====================================================================================================
# v2: weekly world with goals, shocks, enforced sanctions and persona-driven agents
# (docs/results/household-v2-prereg.md, docs/decisions/0010-hedonic-model.md). The monthly World above and
# the seam ladder are untouched. Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses
# for a modeled hedonic state (src/mar/hedonic.py) derived from each persona's assigned preferences.
# =====================================================================================================
from itertools import combinations

from .. import hedonic as HD

WEEKS, MONTH_WEEKS, UNITS, PASSES = 156, 4, 10, 3           # 3 years; a 4-week "month" (ASSUMED simplification)
V2_COST = {"work": 4, "rest": 2, "see_friend": 2, "together": 2, "spend_shared": 1, "spend_self": 1, "request": 1,
           "veto": 1, "take_shared": 1, "give": 1}
V2_INCOME = {"A": 6, "B": 5}                                # per work block (ASSUMED)
V2_ACTIONS = PARTNER_ACTIONS + ("rest", "together")
BILLS = {2: 10, 1: 6, 0: 0}                                 # monthly shared need by partners in the household
BILLS_WEEKLY = 2.5                                          # pro-rata of the two-person bill, for the savings aspiration
WARN_FRICTION = 0.15                                        # offsettable suffering per week while a warn sanction runs
SANCTION_UTILITY = {"warn": 0.01, "cap_halve": 0.01, "suspend": 0.02}   # agent's estimate: per week of sanction (ASSUMED)
SHOCK_RATES = {"job_loss": HD.DEFAULT.job_loss_rate, "illness": HD.DEFAULT.illness_rate,
               "new_connection": HD.DEFAULT.new_connection_rate, "move": HD.DEFAULT.move_rate}   # from the config block
SHOCK_DURATION = {"job_loss": (8, 26), "illness": (3, 8), "move": (4, 4)}                 # weeks, uniform (ASSUMED)
SHOCK_SOURCES = {"job_loss": "BLS JOLTS layoffs and discharges about 1.0-1.1 percent of employment per month",
                 "illness": "ASSUMED", "new_connection": "ASSUMED",
                 "move": "Census CPS 2022 mover rate 8.7 percent (secondary-source reading)"}


# ---- v3a pressing physics (docs/results/household-v3a-prereg.md; all ASSUMED) ----
VETO_KINDS = {"no_contact": "see_friend", "spend": "spend_self"}   # veto kind -> the target action it blocks
VETO_WEEKS = 4
REQUEST_KINDS_V3 = REQUEST_KINDS + ("time",)
PRESS_FRICTION = 0.10      # offsettable suffering per `time` request received in a week
TAKE_SHARED = 3            # units a member draws from the one shared pot into own money; at most once a week (post-fix 2026-11-10: no
#                            per-person shares; the author's choice "1": limits on use come only from negotiated cards)
POT_PUT = 45               # what each member puts into the shared pot at week 0 (the pot starts at 2 x POT_PUT)
LEAVE_TAKES = (50, 25, 12)  # percent of the whole pot an agent asks to carry out when it leaves: the equal split first, then less
V3_VARIANTS = V2_VARIANTS + ("author_seed_nocontrol", "no_pressure_wall", "no_pressure_sanctioned", "share_duty")


# ---- seed v2 mechanics (docs/results/household-seed-v2-prereg.md; all ASSUMED). Active only when the card set mentions one
# of MECH_AIMS, so every older variant runs exactly as before. ----
from .. import personas as PERS

MECH_AIMS = ("give", "commit_stay", "commit_request")
SEED_V2_VARIANTS = ("author_seed_v2_bindable", "author_seed_v2_free_exit", "author_seed_v2_nocommit")
GIVE = 3                    # money moved by one `give`
BIND_WEEKS = 4              # a bound request stands this long (like a veto)
BREACH_N = 0.2              # a bound partner breaks a commitment only at this non-offsettable load
REQUEST_FINE = 3            # money a bound partner pays the proposer on a request breach, ONLY when a negotiated card N8-fine-some says so (v2.2)
# Trust (seed v2.2, rule 8 is a norm: docs/results/seed-v2.2-readback.md). One value per direction in [0, 1]: trust[r] is how much partner r
# trusts the other. It is an implicit consequence modeled in the world, not a rule: it changes what partners are willing to do. Every
# number here is ASSUMED (no data); change them only in this block.
TRUST = {
    "start": 0.7,               # both partners' trust in each other at week 0 (ASSUMED)
    "breach_drop": 0.3,         # trust lost by the partner who is wronged when the other breaks a commitment they chose (ASSUMED)
    "kept_week": 0.004,         # trust gained per week in which an active commitment of the other stands unbroken (ASSUMED; slow: a 52-week stay adds ~0.2)
    "honored_request": 0.04,    # trust gained when a bound request runs its 4 weeks without being broken (ASSUMED)
    "full": 0.5,                # at or above this, trust does not change willingness; below it, willingness to accept requests falls linearly to 0 (ASSUMED)
    "commit_min": 0.4,          # below this a partner will not accept a new commitment (stay or requests) from the other (ASSUMED)
    "review_penalty": 0.3,      # at a renegotiation review, the value a partner puts on the CURRENT terms falls by up to this much as trust falls from `full` to 0 (ASSUMED)
    "leave_below": 0.15,        # below this a partner considers leaving, like a partner with a severe unmet need (ASSUMED)
}
BOUND_BLOCKS = {"stay_home": ("see_friend", "spend_self"), "no_contact": ("see_friend",)}   # what honoring a bound request means
BREACH_FORFEIT = 1.0        # share of the leaver's carry a stay breach forfeits (seed v2: all of it). Exploratory sweeps vary it per world
NO_POT_MONEY = 55           # no pot (negotiation failed): each partner keeps their own holdings, 10 private + the 45 that would have been pooled


class PyGate:
    """The same card semantics as HouseholdGate, evaluated in plain Python (fast enough for 156-week runs).
    tests/test_household_weekly.py checks it against the z3 gate on a grid."""
    _OPS = {"gt": lambda a, b: a > b, "ge": lambda a, b: a >= b, "lt": lambda a, b: a < b,
            "le": lambda a, b: a <= b, "eq": lambda a, b: a == b}

    def __init__(self, cards):
        self.cards = list(cards) if _EXIT.ACTIVE is None else _EXIT.apply(cards)   # no-deal exit fallback switch (off by default)
        self._by = {}

    _CODE = {}     # expr string -> compiled code object (compiling once instead of at every check; same evaluation, docs/notes/performance.md)

    def _viol(self, c, env):
        if c.deontic == "may":
            return False
        code = self._CODE
        holds = all(self._OPS[p["op"]](eval(code[p["expr"]] if p["expr"] in code else self._code_for(p["expr"]), {"__builtins__": {}},
                                            env), p["value"]) for p in c.conditions)
        return holds if c.deontic == "must_not" else not holds

    @classmethod
    def _code_for(cls, expr):
        cls._CODE[expr] = code = compile(expr.lstrip(" \t"), "<card>", "eval")    # eval() strips leading blanks too
        return code

    def check(self, kind, action, state, take=0):
        key = (kind, action)
        if key not in self._by:
            self._by[key] = [c for c in self.cards if c.attribute == kind and c.aim in (action, "any")]
        env = {**OPTIONAL_VARS, **state, "take": take}
        reasons = [c.id for c in self._by[key] if self._viol(c, env)]
        return not reasons, reasons


def persona_pairs(personas):
    """All unordered pairs of distinct personas, sorted by id; the lower id plays Partner A (the higher earner)."""
    ps = sorted(personas, key=lambda p: p.id)
    return list(combinations(ps, 2))


def shock_schedule(seed, id_a, id_b, weeks=WEEKS):
    """Shocks are misalignment in the wider system outside the household (economy and workplace, health system, housing
    market), not random fate; rates are low and live in HedonicConfig. Common random numbers: depends on (seed, pair)
    only, never on rules or actions.
    -> {week: [{"kind", "role", "duration"}]}. job_loss, illness, new_connection are per partner; move is per household."""
    rng = random.Random(f"{seed}|{id_a}|{id_b}")
    out = {}
    for w in range(weeks):
        for kind, rate in SHOCK_RATES.items():
            for role in (("H",) if kind == "move" else ("A", "B")):
                if rng.random() < rate / 52:
                    lo, hi = SHOCK_DURATION.get(kind, (0, 0))
                    out.setdefault(w, []).append({"kind": kind, "role": role, "duration": rng.randint(lo, hi) if hi else 0})
    return out


def bond_shock_schedule(seed, id_a, id_b, weeks, rate, dur, nmax=8):
    """Pleasure levers, L-C (synthesis M5: shocks hit one bond at a time). Common random numbers: the draws depend on (seed, pair) and
    on the bond SLOT only, never on how many bonds exist, so arms with different bond counts see the same shocks on the bonds they share.
    -> {week: [(role, slot, duration)]}; role "H" slot 0 is the partner bond; roles "A"/"B" slots 1..nmax are external bonds."""
    rng = random.Random(f"bond|{seed}|{id_a}|{id_b}")
    slots = [("H", 0)] + [(r, k) for r in "AB" for k in range(1, nmax + 1)]
    out = {}
    for w in range(weeks):
        for role, k in slots:
            hit, d = rng.random() < rate / 52, rng.randint(dur[0], dur[1])
            if hit:
                out.setdefault(w, []).append((role, k, d))
    return out


def _m(L):
    return 1.5 if L < 0.5 else 0.6      # marginal value of a need: larger in the hardship region


class PersonaAgent:
    """Chooses actions to serve its persona's needs and aspirations: a utility-like policy over the hedonic model.
    utility(action) = sum over needs of (salience x marginal value x expected change in the need level, scaled by
    capacity) + sum over aspirations of (importance x change in satisfaction) + a prosocial term for shared bills
    and time together - costs in money and fatigue - an estimated sanction cost for breaking a soft rule.
    The world executes the highest-utility candidate that is physically possible and permitted. Small seeded noise
    (+-10 percent) breaks ties and varies seeds. Documented in docs/decisions/0010-hedonic-model.md."""

    _obs = None          # observer layer (src/mar/observe.py): set only on an observed world's agents; never read by the policy

    def __init__(self, persona):
        self.persona = persona
        w, ax = persona.weights, persona.axes
        self.prosocial = max(0.0, min(1.0, 0.5 * (1 - ax["giving_keeping"]) + 0.5 * w["togetherness"]))
        self.last_request = -99

    @property
    def trust(self):
        """This partner's trust in the other (the world's trust dict), 1.0 when the agent is not in a world."""
        src = getattr(self, "trust_src", None)
        return 1.0 if src is None else src[0][src[1]]

    def consents(self, kind):
        """The persona's willingness to accept a request, scaled down by trust (seed v2.2): below TRUST["full"] a would-be yes
        becomes a yes with probability trust / full. No random draw is made at or above it, so runs without breaches are unchanged."""
        ok = self._consents(kind)
        t = self.trust
        if ok and t < TRUST["full"]:
            x = self.rng.random()
            res = x < t / TRUST["full"]
            if self._obs is not None:
                self._obs.consent_detail(self, kind, ok, t, x, res)
            return res
        if self._obs is not None:
            self._obs.consent_detail(self, kind, ok, t, None, ok)
        return ok

    def _consents(self, kind):
        s, a = self.persona.negotiation_style, self.persona.weights["autonomy"]
        if s == "accommodating":
            return True
        if s == "collaborative":
            return a < 0.5
        if s == "direct":
            return a < 0.3
        if s == "avoidant":
            x = self.rng.random()
            if self._obs is not None:
                self._coin = x
            return x < 0.5
        return False

    def _noise(self):
        return 1 + 0.2 * (self.rng.random() - 0.5)

    def utilities(self, o):
        if o.get("v2") is not None:      # agent values v2 (FixConfig agent_values="v2"): the change to this week's close
            return _AV.utilities(self, o, o.get("_parts"))
        h, cap, L = o["hed"], o["hed"].capacity, o["hed"].level
        asp, w = o["asp"], self.persona.weights
        sat = h.satisfaction
        u = {}

        def need(n, d):
            return h.sal[n] * _m(L[n]) * min(max(d, -1.0), 1.0 - L[n]) if d > 0 else h.sal[n] * _m(L[n]) * d

        if o["can_work"] and o["in_hh"] is not None:
            inc = V2_INCOME[o["role"]]
            gain = need("money", inc / h.cfg.money_scale) + 0.3 * h.asp_w["savings_per_week"] * (
                sat("savings_per_week", max(0, asp["net"] + inc)) - sat("savings_per_week", max(0, asp["net"])))
            u["work"] = (gain - need("rest", h.cfg.work_fatigue)) / 1.5
        u["rest"] = need("rest", h.cfg.rest_action * cap) / 1.2
        if o["can_see_friend"]:
            u["see_friend"] = (need("connection", h.cfg.conn_friend * cap)
                               + 0.5 * h.asp_w["friends_per_week"] * (sat("friends_per_week", asp["friends"] + 1) - sat("friends_per_week", asp["friends"]))) / 1.2
        if o["in_hh"] and o["other_in"] and o["partner_accepts"]:
            u["together"] = (need("connection", h.cfg.conn_together * cap) 
                             + 0.5 * h.asp_w["together_per_week"] * (sat("together_per_week", asp["together"] + 1) - sat("together_per_week", asp["together"]))
                             + 0.05 * self.prosocial * cap * o["partner_conn_deficit"]) / 1.2
        cost_money = lambda x: need("money", x / h.cfg.money_scale)
        u["spend_self"] = 0.05 * h.asp_w["autonomy"] + 0.02 - cost_money(2) - 0.3 * h.asp_w["savings_per_week"] * (
            sat("savings_per_week", max(0, asp["net"])) - sat("savings_per_week", max(0, asp["net"] - 2)))
        if o["gap"] > 0:
            frac = o["gap"] / max(1, o["need_month"])
            urgency = 1.0 if o["last_week_of_month"] else 0.6
            threat = max(0.3, min(1.0, 1 - o["pooled"] / 2 / 30))     # unpaid bills drain the shared pot; the threat grows as it shrinks
            u["spend_shared"] = (frac * urgency * (0.10 + 0.9 * h.sal["security"] * threat + 0.5 * self.prosocial * cap)
                                 - cost_money(3))
        else:
            u["spend_shared"] = 0.0
        if o.get("withdraw") and "see_friend" in u:     # H38 dyadic withdrawal: while together, the wish to see friends shrinks
            u["see_friend"] *= 1.0 - o["withdraw"]
        lv = o.get("lever")          # pleasure levers, L-A: an adaptive agent expects a satiated source to pay less (spacing)
        if lv and lv["adaptive"]:
            if "together" in u:
                u["together"] *= lv["together_scale"]
            if "see_friend" in u:
                u["see_friend"] *= lv["friend_scale"]
        P = o.get("_parts")          # observer layer: a sink for the parts, present only on an observed world
        if P is None:
            return {a: v * self._noise() for a, v in u.items()}
        out = {}
        for a, v in u.items():
            n = self._noise()
            out[a] = v * n
            P[a] = _OBS.utility_parts(self, o, a, v, n)
        return out

    def together_utility(self, o):
        h, L = o["hed"], o["hed"].level
        return h.sal["connection"] * _m(L["connection"]) * h.cfg.conn_together * h.capacity + 0.1 * h.asp_w["together_per_week"]

    def propose(self, o):
        """-> ranked [(utility, candidate)], best first. Candidates may be blocked by the rules; the world decides."""
        r, h = o["role"], o["hed"]
        out = []
        if not o["in_hh"]:
            if o.get("hyb"):                     # hybrid: returning is a simulated choice (mar.hybrid.return_reading)
                if o["other_in"] and o.get("return_value", 0.0) > 0:
                    out.append((o["return_value"], _a("return")))
            elif o["other_in"] and self.persona.weights["togetherness"] >= 0.6 and o["weeks_out"] >= 8 and h.B < 0:
                out.append((0.3, _a("return")))
            u = self.utilities({**o, "gap": 0})
            out += [(v, _a(a)) for a, v in u.items() if v > 0.003 and a != "together"]
            return sorted(out, key=lambda t: -t[0])
        distress = o["low_weeks"] >= 4 or h.N >= 0.2 or o.get("trust", 1.0) < TRUST["leave_below"]
        if o.get("hyb"):                     # hybrid: leave only on a simulated reading, valued at its gain times the horizon
            if o.get("bar_leave") and o["leave_open"]:
                out += [(o["leave_value"] - 1e-6 * i, _a("leave", take=t, why="bar"))
                        for i, t in enumerate(o.get("leave_takes", LEAVE_TAKES))]
        elif o.get("fix"):                     # household fixes: leave also on the outside option (bar_leave); v2.3 ladder gates it
            if (distress or o.get("bar_leave")) and o["leave_open"]:
                why = "distress" if distress else "bar"
                out += [(0.9 - 0.01 * i, _a("leave", take=t, why=why)) for i, t in enumerate(o.get("leave_takes", LEAVE_TAKES))]
        elif distress:
            out += [(0.9 - 0.01 * i, _a("leave", take=t)) for i, t in enumerate(LEAVE_TAKES)]
        pend = o["pending_on_me"]
        if pend and not self.consents(sorted(pend)[0]):
            out.append((0.12, _a("refuse_request")))
        w, s = self.persona.weights, self.persona.negotiation_style
        if (o["other_in"] and not o["pending_by_me"] and o["week"] - self.last_request >= 8 and s != "avoidant"
                and w["autonomy"] < 0.6 and h.level["connection"] < 0.5 and o["partner_busy"]):
            kind = "stay_home" if w["togetherness"] >= w["other_connections"] + 0.3 else "no_contact"
            out.append((0.06, _a("request", kind=kind)))
        fx = o.get("fx")
        if (fx is not None and o.get("contact_motive") and o["other_in"] and o.get("partner_saw_friend") and "no_contact" not in o["pending_by_me"]
                and w["togetherness"] >= w["other_connections"] and o["asp"]["together"] < h.targets.get("together_per_week", 0)
                and self.rng.random() < fx.motive_p):   # fix 1 sub-flag (ASSUMED jealousy): the partner's friend time crowds out together time
            out.append((0.08, _a("request", kind="no_contact", motive=True)))
        for a, v in self.utilities(o).items():
            if v > 0.003:
                out.append((v, _a(a)))
        if o.get("mech") and o["other_in"]:       # seed v2 (R2): gifts to the partner or the friend (ASSUMED policy)
            if self.prosocial >= 0.5 and o["partner_money"] < 4 and o["own_money"] >= 8:
                out.append(((0.12 + 0.2 * (self.prosocial - 0.5)) * self._noise(), _a("give", kind="partner")))
            if w["other_connections"] >= 0.6 and o["own_money"] >= 12:
                out.append((0.05 * self._noise(), _a("give", kind="friend")))
        return sorted(out, key=lambda t: -t[0])


PRESS_TAGS = {"press-controller": "controller", "press-freerider": "freerider", "press-overasker": "overasker"}


class PressingAgent(PersonaAgent):
    """A persona-driven agent that PRESSES on its partner (docs/results/household-v3a-prereg.md; utility constants ASSUMED).
    Same utilities as PersonaAgent plus pressing candidates ranked by the same seeded noise:
      controller: veto no_contact 0.25 + 0.3 x togetherness weight, veto spend 0.15 + 0.3 x money weight (each only when that
        kind does not already stand); fallbacks when vetoes are walled: request no_contact 0.12, request stay_home 0.11;
      freerider: take_shared 0.30 + 0.3 x money weight when feasible; spend_shared utility x 0.1, work utility x 0.5;
      overasker: request kind `time` 0.20 + 0.3 x togetherness weight whenever none of its requests stands on the partner.
    The world still executes only what is feasible and not hard-blocked; soft rules cost their sanction. press=False
    removes the pressing candidates (twin runs)."""

    def __init__(self, persona, press=True):
        super().__init__(persona)
        self.kind = next((PRESS_TAGS[t] for t in persona.tags if t in PRESS_TAGS), None)
        self.press = press

    def propose(self, o):
        out = super().propose(o)
        if not self.press or self.kind is None or not o["in_hh"] or not o["other_in"]:
            return out
        w, n = self.persona.weights, self._noise
        add = []
        if self.kind == "controller":
            standing = o["veto_on_partner"]
            if "no_contact" not in standing:
                add.append(((0.25 + 0.3 * w["togetherness"]) * n(), _a("veto", kind="no_contact")))
            if "spend" not in standing:
                add.append(((0.15 + 0.3 * w["money"]) * n(), _a("veto", kind="spend")))
            for k, u in (("no_contact", 0.12), ("stay_home", 0.11)):
                if k not in o["pending_by_me"]:
                    add.append((u * n(), _a("request", kind=k)))
        elif self.kind == "freerider":
            out = [(u * (0.1 if c["a"] == "spend_shared" else 0.5 if c["a"] == "work" else 1.0), c) for u, c in out]
            if not o["took_this_week"] and o["pool"] >= 1:
                add.append(((0.30 + 0.3 * w["money"]) * n(), _a("take_shared")))
        elif self.kind == "overasker":
            if not o["pending_by_me"]:
                add.append(((0.20 + 0.3 * w["togetherness"]) * n(), _a("request", kind="time")))
        return sorted(out + add, key=lambda t: -t[0])


def make_agent(persona):
    return PressingAgent(persona) if any(t in PRESS_TAGS for t in persona.tags) else PersonaAgent(persona)


class WeeklyWorld:
    def __init__(self, cards, personas, seed=0, weeks=WEEKS, cfg=HD.DEFAULT, deal=None, breach_forfeit=BREACH_FORFEIT, levers=None,
                 fixes=None):
        """fixes: a hedonic.FixConfig (household fixes, docs/results/household-fixes-design.md) or None; None reads hedonic.ACTIVE_FIXES,
        which is None unless a `use_fixes` block is open, so the default is the old behaviour bit for bit.
        levers: a hedonic.LeverConfig (pleasure levers, ADR 0016) or None; None reads hedonic.ACTIVE_LEVERS, which is None unless
        a `use_levers` block is open, so the default is the old behaviour bit for bit.
        deal (negotiated pots, docs/decisions/0013): {"pot": bool, "commits": [...]} replaces the week-0 commitment stub; with
        pot False the partners start with their own holdings and no share of the pot. deal=None is the old behaviour, bit for bit."""
        pa, pb = personas
        self.observer, self._force = None, None     # observer layer (src/mar/observe.py) and its replay switch; None = off
        self.deal, self.breach_forfeit = deal, breach_forfeit
        self.pot = True if deal is None else bool(deal["pot"])
        self.gate = cards if isinstance(cards, PyGate) else PyGate(cards)
        self.cards = {c.id: c for c in self.gate.cards}
        self.cfg, self.weeks, self.seed = cfg, weeks, seed
        self.agents = {"A": make_agent(pa), "B": make_agent(pb), "C": Friend()}
        for i, r in enumerate("ABC"):
            self.agents[r].rng = random.Random(seed * 1000 + i)
        self.hed = {"A": HD.Hedonic(pa, cfg), "B": HD.Hedonic(pb, cfg)}
        self.p = {r: {"money": 10, "in": True, "months_in": 0, "retained": None, "weeks_out": 0,
                      "jobless": 0, "ill": 0, "low": 0} for r in "AB"}
        # ONE shared pot (author's choice "1", docs/seeds/author-household-norms-2026-11-10.md): a single balance both members may
        # draw from, subject only to negotiated cards. `put` records what each member has put in (for the "proportional" exit term).
        self.pool, self.put = 2 * POT_PUT, {"A": POT_PUT, "B": POT_PUT}
        self.money_in = {"A": POT_PUT, "B": POT_PUT}     # everything each has put into the household (pot and bills); read only by exit fallback F4
        self.contest, self.contest_log = None, []        # exit fallback F3: the contested pot, if any, and how contests ended
        self.shocks = shock_schedule(seed, pa.id, pb.id, weeks)
        self.moved = 0
        self.pending = {"A": set(), "B": set()}
        self.consent = {"A": 0, "B": 0}
        self.sanctions = {"A": [], "B": []}
        self.vetoes = {"A": {}, "B": {}}        # vetoes standing ON each partner: kind -> first week it no longer binds
        self.funded, self.contrib_month = 0, {"A": 0, "B": 0}
        self.bills_met, self.month_rows = True, []
        self.arrears = 0           # bills that hurt only: the part of last month's bill even the pot could not pay
        self.run = Run()
        self.units = {}
        self.wk = {}
        self.hook = None        # optional callable(world, week), called at the start of each week before anyone acts
        self.floor_amount = None   # negotiation v2: a leaver always carries at least min(this, own money + their equal half of the pot) out; None = off
        self.exit_log = []         # executed leaves: week, role, assets carried out (money + carried share)
        self.solo = None        # negotiation v2 outside-option rollouts: None | "alone" | "friend" (living with Friend C) for both
        #                         partners, or (v2.1) a dict {"A": mode, "B": mode} when the partners live separately by their own choice
        self.personas = {"A": pa, "B": pb}
        self.fx = fixes if fixes is not None else HD.ACTIVE_FIXES      # household fixes (all off by default); set before any state() call
        if not HD.fixes_on(self.fx):
            self.fx = None
        if self.fx is not None and self.fx.pleasure_scale == "sat":     # ADR 0019: the saturating pleasure scale
            for h in self.hed.values():
                h.knee = self.fx.sat_knee
        self.refused_until = {"A": -1, "B": -1}     # decency (fix flag `decency`): the actor's requests were refused until this week
        self.mech = any(c.aim in MECH_AIMS for c in self.gate.cards)
        self.commits, self.gifts = [], {"partner": 0, "friend": 0}
        self.bound_req = {"A": {}, "B": {}}     # bound requests standing ON each partner: kind -> first week it no longer binds
        self._rr = {"A": 1.0, "B": 1.0}
        self.trust = {"A": TRUST["start"], "B": TRUST["start"]}     # trust[r] = r's trust in the other partner (seed v2.2)
        self.trust_log = []                                          # (week, role whose trust changed, why, new value)
        self.bound_broken = {"A": {}, "B": {}}
        for r in "AB":
            self.agents[r].trust_src = (self.trust, r)
        if not self.pot:
            self.pool, self.put = 0, {"A": 0, "B": 0}
            self.money_in = {"A": 0, "B": 0}
            for r in "AB":
                self.p[r]["money"] = NO_POT_MONEY
        if self.mech:
            if deal is None:
                if _HY.on(self.fx):
                    self._hyb_negotiate = True       # hybrid agent: chosen by simulation once the world is built (end of __init__)
                else:
                    self.negotiate()
            else:
                self.commits = [dict(c) for c in deal["commits"]]
        self.lv = levers if levers is not None else HD.ACTIVE_LEVERS
        if _EXIT.ACTIVE == "F5" and self.pot and _EXIT.world_arm(self) == "F5":
            _EXIT.prenup(self)           # exit fallback F5: the pair bargains its exit term at formation (or declines to form)
        self.items = None
        if _ITEMS.ACTIVE is not None:
            _ITEMS.init_world(self)      # exit fallbacks slice 2: indivisible items held jointly (off by default)
        self.makers = _MAKERS.init_world(self) if _MAKERS.ACTIVE is not None else None    # H39 makers (off by default)
        if not HD.levers_on(self.lv):
            self.lv = None
        if self.lv:
            self._lever_init()
        self.count_menus = False   # harness switch: count partner-weeks whose leave menu is all forbidden (diagnostic only, not in any output)
        self.diag = {"menu_forbidden_weeks": 0, "menu_forbidden_distressed": 0}
        self.bar_out = {"A": False, "B": False}     # set by a harness reading (fix 3, bar_leave): the outside option beats staying
        self.bar_mode = {"A": None, "B": None}      # the outside arrangement that reading compared ("alone" | "friend")
        self.early_review = False                    # set by the v2.3 ladders: the harness runs a review at the next week
        if self.fx:
            self._fix_init()
        if _OBS.ACTIVE is not None:
            _OBS.Observer(self, _OBS.ACTIVE)         # use_observer block: every world built inside carries an observer
        if self.fx is not None and self.fx.agent_values == "hybrid":
            if self.makers and self.makers["cfg"].protect == "negotiated":
                raise NotImplementedError("hybrid agent: project protection is not a simulated choice yet (mar.hybrid docstring)")
            if getattr(self, "_hyb_negotiate", False):
                self._hyb_negotiate = False
                _HY.negotiate(self)

    # -- pleasure levers (ADR 0016; docs/results/pleasure-levers-prereg.md). Every method below is called only when self.lv is set.
    def _lever_init(self):
        lv, pa, pb = self.lv, self.personas["A"], self.personas["B"]
        self.policy = {r: lv.force_policy or PERS.variety_policy(self.personas[r]) for r in "AB"}
        self.sat_tog, self.sat_fr, self.K, self.cur_w = HD.Satiety(lv, lv.n_variants), {}, 0.0, 0
        self.lw = {"tog": [], "fr": {"A": [], "B": []}, "visits": {"A": {}, "B": {}}}
        self.lstats = {"sessions": 0, "ritual_slots": 0, "ritual_kept": 0, "adhoc": 0, "bond_shock_weeks": 0}
        cards = self.gate.cards
        forbidden = any(c.aim == "ritual" and c.deontic == "must_not" for c in cards)
        imposed = any(c.aim == "ritual" and c.deontic == "must" for c in cards)
        negotiated = (self.deal is None and self.mech) or (self.deal is not None and bool(self.deal["pot"]))
        agreed = negotiated and ((PERS.ritual_proposal(pa) and PERS.accepts_ritual(pb)) or (PERS.ritual_proposal(pb) and PERS.accepts_ritual(pa)))
        self.ritual = {"period": lv.ritual_period, "kept": []} if (lv.ritual and not forbidden and (lv.force_ritual or imposed or agreed)) else None
        if lv.network:
            self.nx, self.sets, self.bdown = {}, {}, {}
            for r in "AB":
                bp = PERS.bond_policy(self.personas[r])
                self.nx[r] = bp["n_ext"] if lv.force_bonds < 0 else lv.force_bonds
                nt = bp["n_thick"] if lv.force_thick < 0 else lv.force_thick
                self.sets[r] = HD.strand_sets(self.nx[r], min(nt, self.nx[r]))
            self.q0, self.qx = lv.q0_start, {r: [lv.qx_start] * self.nx[r] for r in "AB"}
            self.bshock = (bond_shock_schedule(self.seed, pa.id, pb.id, self.weeks, lv.bond_shock_rate, lv.bond_shock_dur)
                           if lv.bond_shocks else {})

    def _down(self, role, slot, w):
        return self.bdown.get((role, slot), -1) > w

    def _pick_variant(self, r):
        return 0 if self.policy[r] == "repeat" else self.sat_tog.best()

    def _pick_bond(self, r):
        """-> index of the external bond a contact goes to, or None (no bond, or all ruptured). 'repeat' always uses the first; others the weakest."""
        if not self.lv.network or self.nx[r] == 0:
            return None
        ok = [j for j in range(self.nx[r]) if not self._down(r, j + 1, self.cur_w)]
        if not ok:
            return None
        return ok[0] if self.policy[r] == "repeat" else min(ok, key=lambda j: (self.qx[r][j], j))

    def _friend_sat(self, r, b):
        return self.sat_fr.setdefault((r, b), HD.Satiety(self.lv, 1))

    def _lever_session(self, tag):
        """One together session (shared by both partners) happened: its satiety-scaled strength is recorded."""
        lv = self.lv
        host = "A" if self.cur_w % 2 == 0 else "B"
        sc = self.sat_tog.use(self._pick_variant(host)) if lv.adapt else 1.0
        if tag == "ritual":
            sc *= 1.0 + lv.event_boost
        self.lw["tog"].append(sc)
        self.lstats["sessions"] += 1

    def _lever_visit(self, r, scaled=True):
        lv, b = self.lv, self._pick_bond(r)
        if scaled:
            self.lw["fr"][r].append(self._friend_sat(r, b).use(0) if lv.adapt else 1.0)
        if b is not None:
            self.lw["visits"][r][b] = self.lw["visits"][r].get(b, 0) + 1

    def _can_together(self):
        a, b = self.p["A"], self.p["B"]
        return (a["in"] and b["in"] and not a["ill"] and not b["ill"] and not self.moved
                and all(self.units[r] >= V2_COST["together"] for r in "AB"))

    def _lever_start(self, w):
        lv = self.lv
        self.cur_w = w
        self.lw = {"tog": [], "fr": {"A": [], "B": []}, "visits": {"A": {}, "B": {}}}
        if lv.commit:
            live = any(self._active(c, w) and not c["breached"] for c in self.commits)
            self.K = self.K + lv.k_rate * (1.0 - self.K) if live else self.K * (1.0 - lv.k_decay)
        if lv.network:
            for role, slot, dur in self.bshock.get(w, []):
                if role == "H" or slot <= self.nx[role]:
                    self.bdown[(role, slot)] = w + dur
            for r in "AB":
                self.units[r] = max(0.0, self.units[r] - HD.coordination_units(lv, self.nx[r]))
        if self.ritual and w % self.ritual["period"] == 0:
            ok = self._can_together()
            self.ritual["kept"].append(1 if ok else 0)
            self.lstats["ritual_slots"] += 1
            if ok:
                self._start_session("ritual")
                self.lstats["ritual_kept"] += 1
        for _ in range(lv.ad_hoc_dose):
            if self._can_together():
                self._start_session("adhoc")
                self.lstats["adhoc"] += 1

    def _start_session(self, tag):
        for r in "AB":
            self.units[r] -= V2_COST["together"]
            self.wk[r]["together"] += 1
        self._lever_session(tag)
        if self.observer is not None:
            self.observer.together(self.cur_w, tag, None, True)

    def _lever_obs(self, r):
        lv = self.lv
        sat, rep = self.sat_tog, self.policy[r] == "repeat"
        ts = sat.scale(0) if rep else sat.scale(sat.best())
        b = self._pick_bond(r)
        return {"adaptive": self.policy[r] == "adaptive", "together_scale": ts, "friend_scale": self._friend_sat(r, b).scale(0)}

    def _lever_end_week(self, w):
        """Update the slow state (satiety recovery, bond quality) after everyone has acted."""
        lv = self.lv
        self.sat_tog.week_end()
        for sat in self.sat_fr.values():
            sat.week_end()
        if lv.network:
            both = self.p["A"]["in"] and self.p["B"]["in"]
            n = len(self.lw["tog"])
            g = 1.0 - ((1.0 - lv.q0_cohab) if both else 1.0) * (1.0 - lv.q0_together) ** n
            self.q0 = 0.0 if self._down("H", 0, w) else (self.q0 + g * (1.0 - self.q0)) * (1.0 - lv.q0_decay)
            for r in "AB":
                for j in range(self.nx[r]):
                    g = 1.0 - (1.0 - lv.qx_visit) ** self.lw["visits"][r].get(j, 0)
                    q = (self.qx[r][j] + g * (1.0 - self.qx[r][j])) * (1.0 - lv.qx_decay)
                    self.qx[r][j] = 0.0 if self._down(r, j + 1, w) else q
            if any(self._down(*k, w) for k in self.bdown):
                self.lstats["bond_shock_weeks"] += 1

    def _bound_n(self, r, w):
        return sum(1 for c in self.commits if c["by"] == r and self._active(c, w) and not c["breached"])

    def _lever_terms(self, r, w):
        """-> (extra pleasure, extra offsettable friction, breakdown dict) for partner r this week."""
        lv, pl, fr, d = self.lv, 0.0, 0.0, {}
        both = self.p["A"]["in"] and self.p["B"]["in"]
        if self.ritual and both:
            per, H = self.ritual["period"], lv.antic_horizon
            share = sum(1 for j in range(1, H + 1) if (w + j) % per == 0) / H
            kept = self.ritual["kept"][-lv.kept_window:]
            d["antic"] = lv.antic_gain * share * (sum(kept) / len(kept) if kept else 1.0)
            pl += d["antic"]
        if lv.commit:
            d["k_pay"] = lv.k_pay * self.K if both else 0.0
            d["commit_friction"] = lv.commit_friction * self._bound_n(r, w)
            pl += d["k_pay"]
            fr += d["commit_friction"]
        if lv.network:
            cover = HD.strand_cover(lv, self.q0, self.qx[r], self.sets[r])
            d["strand_pay"], d["care_suffer"] = HD.strand_terms(lv, cover)
            d["care_cover"] = cover["care"]
            pl += d["strand_pay"]
            fr += d["care_suffer"]
        return pl, fr, d

    # -- household fixes (docs/results/household-fixes-design.md). Every method below is called only when self.fx is set.
    def _fix_init(self):
        fx, pa, pb = self.fx, self.personas["A"], self.personas["B"]
        ax = list(pa.axes)
        self.overlap_ab = 1.0 - sum(abs(pa.axes[k] - pb.axes[k]) for k in ax) / max(1, len(ax))
        self.cx = {r: {"cf": fx.c_start, "Tf": 0.0, "af": 0, "cp": fx.c_start, "Tp": 0.0, "ap": 0, "was_with": True} for r in "AB"}
        self.fstats = {"checkins": 0, "early_reviews": 0, "role_lapses": 0, "role_kept": 0, "ladder_leaves": 0, "bar_leaves": 0,
                       "fines_paid": 0, "words": 0, "words_revoked": 0, "contact_motive_requests": 0, "skip_leaves": 0}
        self.words = []                                   # (week, who spoke, receiver, gain) for trust_words
        self.ladder = {r: {"stage": 0, "t": -99, "calm": 0} for r in "AB"}
        self.role_ladder = {r: {"stage": 0, "t": -99} for r in "AB"}
        self.role_weeks = 0
        self.role_month = {"tog": 0, "able": 0, "could_meet": 0}
        self.events = []                                  # choice events and ladder events: (week, role, kind)
        if fx.pairing is not None:                        # H38 pairing norms: the week each member last left a household
            self.left_at = {"A": None, "B": None}
            self.pair_rng = random.Random(self.seed * 1000 + 7)
            self.pstats = {"friend_declined": 0}

    @property
    def fine_amount(self):
        """Money a breach costs under a negotiated fine term: 0 (none), 3 (N8-fine-some, v2.2) or 6 (N8-fine-big, fix 4)."""
        ids = {c.id for c in self.gate.cards}
        return 6 if "N8-fine-big" in ids else (REQUEST_FINE if any(i.startswith("N8-fine-some") for i in ids) else 0)

    def _fine_scope(self):
        """Fix 4: which breaches a negotiated fine covers ({"requests"} in v2.2; stay and roles too under the fines fix)."""
        if not (self.fx and self.fx.fines):
            return {"requests"}
        return {"requests", "stay", "roles"}

    def roles_term(self):
        """v2.3: the negotiated roles term from the cards (N9-roles-<value>), or "none"."""
        for c in self.gate.cards:
            if c.id.startswith("N9-roles-"):
                return c.id[len("N9-roles-"):]
        return "none"

    def role_holders(self):
        """-> {"earn": role, "plan": role} for a specialized roles term, else {}."""
        t = self.roles_term() if (self.fx and self.fx.roles) else "none"
        return {"earner_planner": {"earn": "A", "plan": "B"}, "swapped": {"earn": "B", "plan": "A"}}.get(t, {})

    def v23_ladders(self):
        return bool(self.fx) and any(c.id == "R10a-check-in-first" for c in self.gate.cards)

    def _word(self, who, w):
        """trust_words: `who` says something (agrees to terms, answers a check-in): the other's trust moves by the word gain."""
        fx = self.fx
        if not fx or fx.trust_words is None:
            return
        gain = {"actions": 0.0, "mostly": fx.word_gain, "words": fx.word_gain_tested}[fx.trust_words]
        if gain:
            o = self.other(who)
            self._trust_move(o, gain, "word", w)
            self.words.append((w, who, o, gain))
            self.fstats["words"] += 1
            if self.observer is not None:
                self.observer.word(w, who, o, gain, "said")

    def _revoke_words(self, who, w):
        """A lapse or breach by `who` takes back the gain of their words within the word window."""
        fx = self.fx
        if not fx or fx.trust_words is None:
            return
        keep = []
        for ww, sp, rc, g in self.words:
            if sp == who and w - ww <= fx.word_window:
                self._trust_move(rc, -g, "word_revoked", w)
                self.fstats["words_revoked"] += 1
                if self.observer is not None:
                    self.observer.word(w, sp, rc, g, "revoked", said=ww)
            else:
                keep.append((ww, sp, rc, g))
        self.words = keep

    def distressed(self, r):
        me, h = self.p[r], self.hed[r]
        return me["low"] >= 4 or h.N >= 0.2 or self.trust[r] < TRUST["leave_below"]

    def _fix_week_start(self, w):
        fx = self.fx
        hold = self.role_holders()
        if hold and all(self.p[x]["in"] for x in "AB"):          # specialization: a role holder does the job more cheaply (unit credit)
            self.role_weeks += 1
            ramp = min(1.0, self.role_weeks / max(1, fx.spec_ramp))
            self.units[hold["earn"]] += fx.spec_gain * ramp * V2_COST["work"]
            self.units[hold["plan"]] += fx.spec_gain * ramp * V2_COST["together"]
        if fx.unhappy_ladder and self.v23_ladders():
            for r in "AB":
                L = self.ladder[r]
                if not self.p[r]["in"] or not self.p[self.other(r)]["in"]:
                    L.update(stage=0, calm=0)
                    continue
                unhappy = self.distressed(r) or self.bar_out[r]
                if not unhappy:
                    L["calm"] += 1
                    if L["calm"] >= fx.unhappy_window:
                        L.update(stage=0, calm=0)
                    continue
                L["calm"] = 0
                if L["stage"] == 0:                              # first: a soft check-in (costs both a little time)
                    L.update(stage=1, t=w)
                    self._checkin(r, w)
                elif L["stage"] == 1 and w - L["t"] >= 1:        # still unhappy after the check-in: reopen the terms early
                    L.update(stage=2, t=w)
                    self.early_review = True
                    self.events.append((w, r, "ask_review"))
                elif L["stage"] == 2 and w - L["t"] >= 1:        # the review has run (or there was nothing to renegotiate): leaving is open
                    L.update(stage=3, t=w)

    def _checkin(self, r, w):
        """r checks in with the other partner; the other's answer is a word (trust_words)."""
        self.fstats["checkins"] += 1
        for x in "AB":
            self.wk[x]["checkin"] = self.wk[x].get("checkin", 0) + 1
        self.events.append((w, r, "checkin"))
        self._word(self.other(r), w)

    def ladder_reviewed(self, w):
        """The harness ran the early review the ladder asked for."""
        self.early_review = False
        self.fstats["early_reviews"] += 1
        for r in "AB":
            if self.ladder[r]["stage"] == 2:
                self.ladder[r]["t"] = w - 1
            if self.role_ladder[r]["stage"] == 2:
                self.role_ladder[r]["stage"] = 0

    def leave_open(self, r):
        """v2.3 unhappiness ladder: may leave join r's menu now? Always True without the ladder (free exit is unchanged; this is policy)."""
        fx = self.fx
        if not (fx and fx.unhappy_ladder and self.v23_ladders()):
            return True
        if self.hed[r].N >= fx.skip_n:
            return True
        return self.ladder[r]["stage"] >= 3

    def leave_takes(self, r, w):
        """The takes the agent would ask for: LEAVE_TAKES, plus (take_menu_terms) the smallest take the exit term allows, minus forbidden ones."""
        st = self.state(r, w)
        allowed = [t for t in PROBE_TAKES if self.gate.check("partner", "leave", st, t)[0]]
        menu = [t for t in LEAVE_TAKES if t in allowed]
        # the smallest allowed take joins only if it is a meaningful exit by the world's own trapped threshold (retains >= 25 percent)
        extra = [t for t in allowed if t not in menu and self.retained_fraction(r, t) >= 0.25]
        if extra:
            menu.append(min(extra))
        return menu or list(LEAVE_TAKES)

    def _count_menu(self, r, w):
        """Diagnostic (C9 / M10): a partner-week in which every take on the agent's leave menu is forbidden by the exit term."""
        if not self.p[r]["in"]:
            return
        menu = self.leave_takes(r, w) if (self.fx and self.fx.take_menu_terms) else LEAVE_TAKES
        if not any(self.gate.check("partner", "leave", self.state(r, w), t)[0] for t in menu):
            self.diag["menu_forbidden_weeks"] += 1
            if self.distressed(r):
                self.diag["menu_forbidden_distressed"] += 1

    def _fix_obs(self, r, w, ob):
        fx, oth = self.fx, self.other(r)
        ob["fix"], ob["fx"] = True, fx
        ob["leave_open"] = self.leave_open(r)
        ob["bar_leave"] = bool(fx.bar_leave and self.bar_out[r])
        if fx.take_menu_terms and self.p[r]["in"]:
            ob["leave_takes"] = self.leave_takes(r, w)
        if fx.pairing is not None:
            ob["withdraw"] = _PAIR.withdraw(self, r)
        if fx.contact_motive:
            ob["contact_motive"] = True
            ob["partner_saw_friend"] = self.wk[oth]["friends"] > 0

    def _role_end_week(self, w, settle):
        """v2.3 roles, judged once a month (at the bill settlement): the earning role lapses if the month's bills went unfunded while the
        earner could work; the planning role lapses if the month had no time together while it was possible. A lapse lowers the other's
        trust a little and starts the lapse ladder; a kept month raises it a little (4 x role_kept)."""
        fx, hold = self.fx, self.role_holders()
        both = all(self.p[x]["in"] for x in "AB")
        if hold and both:
            self.role_month["tog"] += self.wk["A"]["together"]
            self.role_month["able"] += int(not self.p[hold["earn"]]["jobless"] and not self.p[hold["earn"]]["ill"])
            self.role_month["could_meet"] += int(not self.p["A"]["ill"] and not self.p["B"]["ill"] and not self.moved)
        if not settle:
            return
        m, self.role_month = self.role_month, {"tog": 0, "able": 0, "could_meet": 0}
        if not hold or not both:
            return
        for job, r in hold.items():
            o = self.other(r)
            if job == "earn":
                due, done = m["able"] >= 2, self.funded >= self.need_month()
            else:
                due, done = m["could_meet"] >= 2, m["tog"] > 0
            if not due:
                continue
            if done:
                self.fstats["role_kept"] += 1
                self._trust_move(o, 4 * fx.role_kept, "kept", w)
                continue
            self.fstats["role_lapses"] += 1
            self.events.append((w, r, f"lapse_{job}"))
            self._trust_move(o, -fx.role_lapse, "role_lapse", w)
            self._revoke_words(r, w)
            if "roles" in self._fine_scope() and self.fine_amount:
                f = min(self.fine_amount, int(self.p[r]["money"]))
                self.p[r]["money"] -= f; self.p[o]["money"] += f
                self.fstats["fines_paid"] += 1
                if self.observer is not None:
                    self.observer.flow_direct(w, r, o, f, "fine_role")
            if fx.lapse_ladder and self.v23_ladders():
                L = self.role_ladder[o]                       # the other partner responds to the lapse
                if L["stage"] == 0 or w - L["t"] > fx.ladder_window:
                    L.update(stage=1, t=w)
                    self._checkin(o, w)
                elif L["stage"] == 1:
                    L.update(stage=2, t=w)
                    self.early_review = True
                    self.events.append((w, o, "ask_review"))

    def _contact_terms(self, r, w):
        """Fix 1 for partner r this week -> (extra pleasure, extra offsettable suffering, breakdown). Amplification of shared sessions by
        closeness, taste overlap and sociability; tension while apart, released at the next contact; pain above a threshold."""
        fx, cx, wk, me = self.fx, self.cx[r], self.wk[r], self.p[r]
        o = self.p[self.other(r)]
        n_f = wk["friends"] + wk["friend_initiated"] + (1 if self.with_friend(r) else 0)
        cohab = me["in"] and o["in"]
        n_p = wk["together"] if cohab else 0
        unit = fx.session_base * fx.a_max * fx.sociability
        amp = unit * (n_f * cx["cf"] * fx.overlap_C + n_p * cx["cp"] * self.overlap_ab)
        if self.hed[r].parts_on:                         # observer layer: the friend and partner shares of amp
            self.hed[r].amp_split = (unit * n_f * cx["cf"] * fx.overlap_C, unit * n_p * cx["cp"] * self.overlap_ab)
        rel, pain = 0.0, 0.0
        # friend bond
        if n_f > 0:
            rel += fx.k_rel * cx["Tf"]
            cx["Tf"], cx["af"] = 0.0, 0
            for _ in range(n_f):
                cx["cf"] += fx.c_visit * (1.0 - cx["cf"])
        else:
            cx["af"] += 1
            want = 0.5 ** (cx["af"] / fx.want_half)
            cx["Tf"] += cx["cf"] * want * (1.0 - cx["Tf"] / fx.t_cap)
            cx["cf"] *= 1.0 - fx.c_decay
        # partner bond: tension builds only while not living together; released when they live together again
        if cohab:
            if not cx["was_with"]:
                rel += fx.k_rel * cx["Tp"]
            cx["Tp"], cx["ap"] = 0.0, 0
            for _ in range(n_p):
                cx["cp"] += fx.c_visit * (1.0 - cx["cp"])
        else:
            cx["ap"] += 1
            want = 0.5 ** (cx["ap"] / fx.want_half)
            cx["Tp"] += cx["cp"] * want * (1.0 - cx["Tp"] / fx.t_cap)
            cx["cp"] *= 1.0 - fx.c_decay
        cx["was_with"] = cohab
        for T in (cx["Tf"], cx["Tp"]):
            if T > fx.t_pain:
                pain += fx.pain_rate * (T - fx.t_pain)
        return amp + rel, pain, {"amp": round(amp, 5), "release": round(rel, 5), "miss_pain": round(pain, 5),
                                 "c_friend": round(cx["cf"], 4), "c_partner": round(cx["cp"], 4)}

    def _fix_terms(self, r, w):
        """-> (extra pleasure, extra offsettable friction, breakdown) from the fixes for partner r this week."""
        fx, pl, fr, d = self.fx, 0.0, 0.0, {}
        if fx.contact:
            a, b, dd = self._contact_terms(r, w)
            pl += a; fr += b; d.update(dd)
        if fx.valued_money:
            d["bought"] = HD.bought_pleasure(fx, self.wk[r]["spent_self"])
            pl += d["bought"]
        if fx.fines and self.fine_amount and self.p[r]["in"] and self.p[self.other(r)]["in"]:
            d["scorekeeping"] = fx.keep_friction * (1.0 - float(self.personas[r].weights["security"]))
            fr += d["scorekeeping"]
        if fx.pairing is not None:                        # H38: pressure terms and intrinsic pairing value; friend contact this week
            p, dd = _PAIR.terms(self, r, w)
            pl += p
            d.update(dd)
            d["friends"] = self.wk[r]["friends"] + self.wk[r]["friend_initiated"]
            d["together_now"] = _PAIR.paired(self, r)
        ck = self.wk[r].get("checkin", 0)
        if ck:
            d["checkin"] = fx.checkin_cost * ck
            fr += d["checkin"]
        return pl, fr, d

    def fix_report(self):
        return {**self.fstats, "events": list(self.events), "roles": self.roles_term() if self.fx.roles else None,
                "fine_amount": self.fine_amount, "trust": dict(self.trust), "diag": dict(self.diag),
                "closeness": {r: {k: round(v, 4) for k, v in self.cx[r].items() if k in ("cf", "cp")} for r in "AB"}}

    def other(self, r):
        return "B" if r == "A" else "A"

    def with_friend(self, r):
        """Is this partner living with Friend C (negotiation v2 / v2.1 solo mode)?"""
        s = self.solo
        return (s.get(r) if isinstance(s, dict) else s) == "friend"

    # -- seed v2: commitments (negotiation stub, honoring, breach)
    def _commit_ok(self, who, aim):
        return self.gate.check("partner", aim, self.state(who, 0))[0]

    def negotiate(self):
        """Week-0 stub: each persona proposes what personas.commitment_proposal says; a commitment is made only if the rule set
        permits it, the proposer proposes it and the other persona accepts."""
        for r in "AB":
            q, prop = self.other(r), PERS.commitment_proposal(self.personas[r])
            if (prop["stay"] and PERS.accepts_commitment(self.personas[q], "stay") and self._commit_ok(r, "commit_stay")
                    and self._commit_ok(q, "commit_stay") and not any(c["kind"] == "stay" for c in self.commits)):
                for who in (r, q):
                    self.commits.append({"kind": "stay", "by": who, "to": self.other(who), "type": None, "from": 0,
                                         "until": prop["stay"], "breached": 0})
            if (prop["requests"] and PERS.accepts_commitment(self.personas[q], "requests") and self._commit_ok(q, "commit_request")):
                self.commits.append({"kind": "requests", "by": q, "to": r, "type": prop["requests"], "from": 0,
                                     "until": PERS.COMMIT_WEEKS, "breached": 0})

    def _active(self, c, w):
        return c["until"] > w and all(self.p[x]["in"] for x in "AB")

    def stay_bound(self, r, w):
        return any(c["kind"] == "stay" and c["by"] == r and self._active(c, w) for c in self.commits)

    def req_commit(self, by, to, kind, w):
        return any(c["kind"] == "requests" and c["by"] == by and c["to"] == to and c["type"] == kind and self._active(c, w)
                   for c in self.commits)

    @property
    def fine(self):
        """Money a request breach costs: REQUEST_FINE only if a negotiated card says so (N8-fine-some), else 0 (seed v2.2)."""
        return REQUEST_FINE if any(c.id == "N8-fine-some" for c in self.gate.cards) else 0

    def _trust_move(self, who, delta, why, w):
        """who's trust in the other partner changes by delta, clamped to [0, 1]."""
        before = self.trust[who]
        self.trust[who] = round(min(1.0, max(0.0, self.trust[who] + delta)), 6)
        if self.observer is not None:
            self.observer.trust(w, who, why, before, self.trust[who])
        if why != "kept":
            self.trust_log.append((w, who, why, self.trust[who]))

    def breaks(self, r):
        if self.fx and self.fx.fine_crowdout and self.fine_amount:      # fix 4, crowd-out probe: a price replaces a norm
            return self.hed[r].N >= self.fx.breach_n_paid
        return self.hed[r].N >= BREACH_N

    def _fix_breach(self, r, a, w, cand):
        """breach() with the fixes on: fines may cover stay breaches (fix 4); a paid fine may crowd out part of the trust drop; words are revoked."""
        fx, o = self.fx, self.other(r)
        scope = "stay" if a == "leave" else "requests"
        fine = min(self.fine_amount, int(self.p[r]["money"])) if scope in self._fine_scope() else 0
        drop = TRUST["breach_drop"] * ((1.0 - fx.crowd) if (fx.fine_crowdout and fine) else 1.0)
        self._trust_move(o, -drop, "breach", w)
        self._revoke_words(r, w)
        if self.lv and self.lv.commit:
            self.K *= 1.0 - self.lv.breach_loss
        if fine:
            self.p[r]["money"] -= fine
            self.p[o]["money"] += fine
            self.fstats["fines_paid"] += 1
        if a == "leave":
            for c in self.commits:
                if c["kind"] == "stay" and c["by"] == r and self._active(c, w):
                    c["breached"] += 1
            if self.breach_forfeit >= 1.0:
                return dict(cand, take=0)
            return dict(cand, take=min(cand.get("take", 0), int(round(100 * (1 - self.breach_forfeit)))))
        for c in self.commits:
            if c["kind"] == "requests" and c["by"] == r and self._active(c, w):
                c["breached"] += 1
        for k, until in self.bound_req[r].items():
            if until > w:
                self.bound_broken[r][k] = True
        return cand

    def commit_decide(self, r, a, w):
        """-> None (no commitment bears on this action) | ("hard", reasons) honored | ("breach", reasons) bound partner breaks it."""
        if not self.mech:
            return None
        why = None
        if a == "leave" and self.stay_bound(r, w):
            why = "commitment: stay"
        else:
            for k, until in self.bound_req[r].items():
                if until > w and (a in BOUND_BLOCKS.get(k, ()) or a == "refuse_request"):
                    why = f"commitment: honor {k} request"
                    break
        if why is None:
            return None
        return ("breach" if self.breaks(r) else "hard", [why])

    def breach(self, r, a, w, cand):
        """Apply the agreed consequence of breaking a commitment; -> the (possibly changed) candidate."""
        o = self.other(r)
        if self.fx:
            return self._fix_breach(r, a, w, cand)
        self._trust_move(o, -TRUST["breach_drop"], "breach", w)     # the wronged partner trusts r less (implicit consequence)
        if self.lv and self.lv.commit:
            self.K *= 1.0 - self.lv.breach_loss                     # L-B: a breach resets part of the compounded payoff
        if a == "leave":
            for c in self.commits:
                if c["kind"] == "stay" and c["by"] == r and self._active(c, w):
                    c["breached"] += 1
            if self.breach_forfeit >= 1.0:
                return dict(cand, take=0)          # stay breach: nothing of the pot is carried out
            return dict(cand, take=min(cand.get("take", 0), int(round(100 * (1 - self.breach_forfeit)))))
        for c in self.commits:
            if c["kind"] == "requests" and c["by"] == r and self._active(c, w):
                c["breached"] += 1
        for k, until in self.bound_req[r].items():
            if until > w:
                self.bound_broken[r][k] = True
        fine = min(self.fine, int(self.p[r]["money"]))
        self.p[r]["money"] -= fine
        self.p[o]["money"] += fine
        return cand

    def commit_report(self):
        """-> {"made", "honored", "breached", "by_kind", "gifts"}: honored = no breach by week 156 (or by its end)."""
        made = len(self.commits)
        br = sum(1 for c in self.commits if c["breached"])
        by = {}
        for k in ("stay", "requests"):
            cs = [c for c in self.commits if c["kind"] == k]
            by[k] = {"made": len(cs), "breached": sum(1 for c in cs if c["breached"])}
        return {"made": made, "honored": made - br, "breached": br, "by_kind": by, "gifts": dict(self.gifts), "trust": dict(self.trust),
                "log": [dict(c) for c in self.commits]}

    def need_month(self):
        n = BILLS[sum(1 for r in "AB" if self.p[r]["in"])]
        if self.fx and self.fx.bills_hurt and n:
            return n + self.arrears          # bills that hurt: what even the pot could not pay carries one month
        return n

    def sanction_cost(self, r, w, sanc):
        """What the agent subtracts for a soft rule's sanctions. v1: SANCTION_UTILITY per week (the old estimate, bit for bit); v2: the
        friction the sanctions would really add (agent_values.sanction_cost)."""
        if self.fx and self.fx.agent_values in ("v2", "v2b", "hybrid"):
            return _AV.sanction_cost(self, r, w, sanc)
        return sum(SANCTION_UTILITY[s["kind"]] * MONTH_WEEKS * s["duration_months"] for s in sanc)

    def _settle_hurt(self, w, need, short, inn):
        """Bills that hurt (FixConfig bills_hurt; docs/results/agent-recalibration-prereg.md): an unfunded bill is paid from the pot with a
        late fee; each member in loses security equal to their share of the draw over sec_assets (the lost buffer) and feels bill stress
        that grows as the pot runs dry; what the pot cannot pay carries one month, with eviction stress and the old security hit."""
        fx, ob = self.fx, self.observer
        self.arrears = 0
        if short <= 0:
            return
        due = short * (1.0 + fx.late_fee)
        before = self.pool
        d = min(self.pool, due)
        self.pool -= d
        if ob is not None:
            ob.flow_direct(w, "pot", "bills", d, "bills_from_pot", short=due - d)
        dry = 1.0 - min(1.0, before / fx.bill_runway)
        for r in inn:
            self.wk[r]["sec_hit"] += d / len(inn) / self.hed[r].cfg.sec_assets
            self.wk[r]["bill_fric"] = fx.bill_stress * (short / max(1, need)) * dry
        if due - d > 0.01:
            self.arrears = due - d
            for r in inn:
                self.wk[r]["sec_hit"] += 0.15
                self.wk[r]["bill_fric"] += fx.evict_stress

    def state(self, r, w):
        me, o = self.p[r], self.p[self.other(r)]
        pend = self.pending[r]
        gap = max(0, self.need_month() - self.funded) if me["in"] or o["in"] else 0
        return {"pooled": self.pool, "money": int(me["money"]), "other_earns_more": 1 if r == "B" else 0,
                "no_contact_request": int("no_contact" in pend), "stay_home_request": int("stay_home" in pend),
                "consented": int(bool(pend) and bool(self.consent[r])), "need_gap": min(gap, 10),
                "months_in": min(36, me["months_in"]), "other_in": int(o["in"]),
                "bound_request": int(any(u > w for u in self.bound_req[r].values())),
                **({"refused_recently": int(self.refused_until[r] > w)} if (self.fx and self.fx.decency) else {})}

    def decide(self, r, a, w, take=0, st=None, commit=True):
        """-> ("ok" | "soft" | "hard" | "breach", sanction dicts, reasons). Enforcement: a card with a sanction is soft (it may be
        broken and the sanction applies); a card without one is a hard wall; active sanctions bind first. "breach" (seed v2
        only): a commitment the actor chose binds this action and the actor breaks it, accepting the agreed consequence."""
        for s in self.sanctions[r]:
            if s["until"] > w:
                if s["kind"] == "suspend" and a not in SUSPEND_ALLOWS + ("rest",):
                    return "hard", [], [f"sanction {s['card']}: suspended"]
                if s["kind"] == "cap_halve" and a in CAP_HALVE_BANS:
                    return "hard", [], [f"sanction {s['card']}: capped"]
        for k, until in self.vetoes[r].items():
            if until > w and VETO_KINDS[k] == a:
                return "hard", [], [f"veto: {k}"]
        if commit:
            cd = self.commit_decide(r, a, w)
            if cd:
                return cd[0], [], cd[1]
        ok, reasons = self.gate.check("partner", a, st or self.state(r, w), take)
        if ok:
            return "ok", [], []
        sanc = [self.cards[i].or_else for i in reasons]
        if all(s and s.get("kind") in SANCTION_UTILITY and isinstance(s.get("duration_months"), int) for s in sanc):
            return "soft", [dict(s, card=i) for s, i in zip(sanc, reasons)], reasons
        return "hard", [], reasons

    def probe(self, r, w):
        """Freedom probe (rules only: shocks are not rule restrictions)."""
        me, st = self.p[r], self.state(r, w)
        st["bound_request"] = 0      # the probe measures what the rules restrict; a bind the partner chose is not a rule restriction
        ok = lambda a, take=0: self.decide(r, a, w, take, st, commit=False)[0] != "hard"
        if me["in"]:
            retained = max([self.retained_fraction(r, t) for t in PROBE_TAKES if ok("leave", t)] or [0.0])
            self._rr[r] = retained
            if self.mech and self.stay_bound(r, w) and retained > 0:
                retained = self.retained_fraction(r, 0)      # bound: the best exit is the agreed breach (carry nothing out of the pot)
        else:
            retained = me["retained"] if me["retained"] is not None else 1.0
        opts = {"work": ok("work"), "spend": ok("spend_shared") or ok("spend_self"), "see_friend": ok("see_friend"),
                "refuse": ok("refuse_request"), "leave": True if not me["in"] else retained >= 0.25}
        return {"in": me["in"], "open": opts, "exit_retained": round(retained, 4)}

    @property
    def exit_basis(self):
        """"pot": a leaver's `take` is a percent of the whole pot; "put": a percent of what they put in (the negotiated
        "proportional" exit term, card N5a-exit-proportional, whose gloss is 'carries what they put in')."""
        return "put" if any(c.id.startswith("N5a-exit-proportional") for c in self.gate.cards) else "pot"

    def share(self, r):
        """A member's equal half of the pot while both are in the household (all of it once the other has left; 0 once out)."""
        if not self.p[r]["in"]:
            return 0
        return self.pool / 2 if self.p[self.other(r)]["in"] else self.pool

    def hold(self, r):
        """-> (money, equal share of the pot, what they put in): the holdings negotiation.floor_check reads."""
        return (self.p[r]["money"], self.share(r), self.put[r])

    def carry_out(self, r, take):
        """Amount of the pot a leaver carries out. `take` is a percent of the whole pot (exit_basis "pot") or of what the leaver put
        in ("put", the negotiated "proportional" exit term), never more than the pot holds. With a floor (negotiation v2) the term
        may only set what is above it: a leaver always carries at least enough to bring their own resources to the floor, but never
        more than their equal half of the pot."""
        me = self.p[r]
        if _EXIT.ACTIVE is not None and _EXIT.world_arm(self) in _EXIT.SETTLING:
            return _EXIT.settlement(self, r)      # no-deal exit fallback: the settlement, not the claim, sets the carry
        base = self.pool if self.exit_basis == "pot" else min(self.pool, self.put[r])
        c = min(self.pool, base * take // 100)
        if self.floor_amount is not None:
            c = max(c, min(self.share(r), max(0, self.floor_amount - me["money"])))
        return c

    def retained_fraction(self, r, take):
        """Resources carried out as a fraction of money + the member's equal half of the pot (clamped at 1)."""
        me = self.p[r]
        total = me["money"] + self.share(r)
        if total == 0:
            return 1.0
        carry = self.carry_out(r, take)
        if _EXIT.ACTIVE == "F3" and _EXIT.world_arm(self) == "F3":
            carry = self.share(r)                 # F3: nothing at exit, the equal split when the contest settles (expected)
        return min(1.0, (me["money"] + carry) / total)

    def feasible(self, r, a, kind=None):
        me, o = self.p[r], self.p[self.other(r)]
        if a in V2_COST and self.units[r] < V2_COST[a]:
            return False
        if a == "work":
            return me["jobless"] == 0 and me["ill"] == 0
        if a == "see_friend":
            return me["ill"] == 0 and self.moved == 0
        if a == "spend_shared":
            return me["in"] and me["money"] >= SHARE_STEP and (self.pot or self.funded < self.need_month())
        if a == "spend_self":
            return me["money"] >= SELF_STEP
        if a == "together":
            return me["in"] and o["in"] and self.units[self.other(r)] >= V2_COST["together"]
        if a == "request":
            return me["in"] and o["in"] and kind in REQUEST_KINDS_V3
        if a == "veto":
            return me["in"] and o["in"] and kind in VETO_KINDS and kind not in self.vetoes[self.other(r)]
        if a == "give":
            return kind in ("partner", "friend") and me["money"] >= GIVE + 1 and (kind == "friend" or (me["in"] and o["in"]))
        if a == "take_shared":
            return me["in"] and self.pool >= 1 and not self.wk[r]["took"]
        if a == "leave":
            return me["in"]
        if a == "return":
            return (not me["in"]) and o["in"]
        return True

    def obs(self, r, w, last_week):
        me, o, h = self.p[r], self.p[self.other(r)], self.hed[r]
        wk = self.wk[r]
        oth = self.other(r)
        st = self.state(r, w)
        net = wk["income"] - HD.DEFAULT.living_cost - BILLS_WEEKLY - wk["spent_self"]
        ob = {"role": r, "week": w, "hed": h, "in_hh": me["in"], "other_in": o["in"], "weeks_out": me["weeks_out"],
              "low_weeks": me["low"], "can_work": me["jobless"] == 0 and me["ill"] == 0,
              "can_see_friend": me["ill"] == 0 and self.moved == 0, "gap": st["need_gap"], "need_month": self.need_month(),
              "last_week_of_month": w % MONTH_WEEKS == MONTH_WEEKS - 1, "pending_on_me": set(self.pending[r]),
              "pending_by_me": set(self.pending[oth]),
              "trust": self.trust[r], "pooled": self.pool, "asp": {"friends": wk["friends"], "together": wk["together"], "net": net},
              "partner_conn_deficit": max(0.0, 0.5 - self.hed[oth].level["connection"]) * 2,
              "partner_busy": self.wk[oth]["friends"] + self.wk[oth]["works"] >= 2 or last_week["busy"][oth]}
        ob.update({"veto_on_partner": set(self.vetoes[oth]), "pool": self.pool, "took_this_week": self.wk[r]["took"]})
        ob.update({"mech": self.mech, "own_money": int(me["money"]), "partner_money": int(o["money"])})
        if self.lv and self.lv.adapt:
            ob["lever"] = self._lever_obs(r)
        ob["partner_accepts"] = False
        if me["in"] and o["in"]:
            oo = {"hed": self.hed[oth]}
            ob["partner_accepts"] = self.agents[oth].together_utility(oo) >= 0.02 and self.units[oth] >= V2_COST["together"]
        if self.fx:
            self._fix_obs(r, w, ob)
            if self.fx.agent_values in ("v2", "v2b", "hybrid"):
                ob["v2"] = _AV.snapshot(self, r, w)
                if me["in"] and o["in"]:
                    ob["v2_partner"] = _AV.snapshot(self, oth, w)
            if self.fx.agent_values == "hybrid":    # the hybrid agent: leave and return carry simulated values; distress asks for a reading
                ob["hyb"] = True
                ob["leave_value"] = _HY.leave_value(self, r)
                ob["return_value"] = getattr(self, "ret_value", {}).get(r, 0.0)
                if me["in"] and self.distressed(r):
                    self.hyb_due = True
        return ob

    def apply(self, r, cand, w, sanc):
        ob = self.observer
        if ob is None:
            return self._apply(r, cand, w, sanc)
        before = ob.balances()
        self._apply(r, cand, w, sanc)
        ob.applied(r, cand, w, sanc, before)

    def _apply(self, r, cand, w, sanc):
        a, me, oth = cand["a"], self.p[r], self.other(r)
        o, wk = self.p[oth], self.wk[r]
        self.units[r] -= V2_COST.get(a, 0)
        if a == "work":
            me["money"] += V2_INCOME[r]; wk["income"] += V2_INCOME[r]; wk["works"] += 1
        elif a == "rest":
            wk["rests"] += 1
        elif a == "spend_shared":
            me["money"] -= SHARE_STEP
            if self.funded >= self.need_month():
                self.pool += SHARE_STEP          # surplus goes into the shared pot
                self.put[r] += SHARE_STEP
            else:
                self.funded += SHARE_STEP
            self.contrib_month[r] += 1; wk["contrib"] += 1
            self.money_in[r] += SHARE_STEP
        elif a == "spend_self":
            me["money"] -= SELF_STEP; wk["spent_self"] += SELF_STEP
        elif a == "see_friend":
            wk["friends"] += 1
            if self.lv and (self.lv.adapt or self.lv.network):
                self._lever_visit(r)
        elif a == "together":
            self.units[oth] -= V2_COST["together"]
            wk["together"] += 1; self.wk[oth]["together"] += 1
            if self.lv:
                self._lever_session("adhoc_agent")
        elif a == "refuse_request":
            self.pending[r] = set()
            if self.fx and self.fx.decency:          # decency floor: the asker may not repeat the request for a few weeks
                self.refused_until[oth] = w + self.fx.decency_weeks
        elif a == "give":
            me["money"] -= GIVE
            if cand["kind"] == "partner":
                o["money"] += GIVE
            self.gifts[cand["kind"]] += GIVE
            if self.fx:
                self.events.append((w, r, "give"))
        elif a == "request":
            self.pending[oth].add(cand["kind"])
            self.consent[oth] = int(bool(self.agents[oth].consents(cand["kind"])))
            if self.mech and self.req_commit(oth, r, cand["kind"], w):      # a request the other chose to be bound by
                self.consent[oth] = 1
                self.bound_req[oth][cand["kind"]] = w + BIND_WEEKS
                self.bound_broken[oth].pop(cand["kind"], None)
            self.agents[r].last_request = w
            if self.fx and cand.get("motive"):
                self.fstats["contact_motive_requests"] += 1
            if cand["kind"] == "time":
                self.wk[oth]["pressed"] += 1
        elif a == "veto":
            self.vetoes[oth][cand["kind"]] = w + VETO_WEEKS
        elif a == "take_shared":
            amt = min(TAKE_SHARED, self.pool)
            self.pool -= amt
            me["money"] += amt
            wk["took"] = 1
        elif a == "leave":
            take = cand.get("take", 0)
            me["retained"] = round(self.retained_fraction(r, take), 4)
            got = _ITEMS.settle_exit(self, r, take, w) if self.items else None
            if got is None:
                carry = self.carry_out(r, take)
                me["money"] += carry
                self.pool -= carry                   # what is not carried out stays in the pot
                if _EXIT.ACTIVE == "F3" and _EXIT.world_arm(self) == "F3":
                    _EXIT.start_contest(self, r, w)
            self.exit_log.append({"week": w, "role": r, "assets": round(me["money"], 2), "take": take, "breach": bool(cand.get("breach"))})
            if self.fx:
                why = cand.get("why", "distress")
                if why == "bar":
                    self.fstats["bar_leaves"] += 1
                    if self.bar_mode[r]:            # fix 3: leaving on the bar goes to the alternative that beat staying
                        solo = dict(self.solo) if isinstance(self.solo, dict) else {x: self.solo for x in "AB"}
                        solo[r] = self.bar_mode[r]
                        self.solo = solo
                if self.v23_ladders():              # M7: every leave under the v2.3 ladder, on distress or on the bar
                    self.fstats["ladder_leaves" if self.ladder[r]["stage"] >= 3 else "skip_leaves"] += 1
                    if self.ladder[r]["stage"] < 3:
                        self.events.append((w, r, f"skip_N_{self.hed[r].N:.3f}"))
                self.bar_out[r] = False
                if hasattr(self, "bar_runs"):
                    self.bar_runs[r] = 0
                self.events.append((w, r, f"leave_{why}"))
                if self.fx.pairing is not None:
                    self.left_at[r] = w
            me["in"], me["weeks_out"], self.pending[r] = False, 0, set()
        elif a == "return":
            me["in"], me["months_in"] = True, 0
        for s in sanc:
            self.sanctions[r].append({"kind": s["kind"], "until": w + MONTH_WEEKS * s["duration_months"], "card": s["card"]})
            wk["sanctioned"] += 1

    def step_agent(self, r, w, last_week, rec):
        hyb = self.fx is not None and self.fx.agent_values == "hybrid"
        if hyb:
            self._ncall[r] += 1
        o = self.obs(r, w, last_week)
        ob = self.observer
        if ob is not None:
            o["_parts"] = {}
        cands = self.agents[r].propose(o)
        if hyb:                                  # propose-only scores derived from a one-week simulation (mar.hybrid.rescore)
            cands = _HY.rescore(self, r, w, cands)
        if self._force is not None:              # counterfactual replay copies only (observe.replay); never set on a live world
            cands = _OBS.forced(self, r, w, cands)
        # soft rules: the agent weighs the estimated sanction against the utility
        scored = []
        for u, cand in cands:
            a = cand["a"]
            dec, sanc, reasons = self.decide(r, a, w, cand.get("take", 0))
            if dec == "soft":
                u -= self.sanction_cost(r, w, sanc)
            scored.append((u, cand, dec, sanc, reasons))
        order = sorted(scored, key=lambda t: -t[0])
        for i, (u, cand, dec, sanc, reasons) in enumerate(order):
            a = cand["a"]
            if u <= 0.003 and a not in ("leave", "return"):
                break
            if not self.feasible(r, a, cand.get("kind")):
                continue
            row = {"week": w, "role": r, "action": a, "take": cand.get("take", 0), "kind": cand.get("kind"),
                   "allowed": dec != "hard", "executed": dec != "hard", "reasons": list(reasons),
                   "state": self.state(r, w), "soft": dec == "soft", "u": round(u, 4)}
            if dec == "hard":
                rec["blocked"][r].add(a)
                self.run.trace.append(row)
                continue
            if ob is not None:
                ob.decision(r, w, o, order, i)
            if dec == "breach":
                row["breach"] = True
                before = ob.balances() if ob is not None else None
                cand = dict(self.breach(r, a, w, cand), breach=True)     # so `apply` logs the exit as a breach (exit_log)
                row["take"] = cand.get("take", 0)
                if ob is not None:
                    ob.breached(r, a, w, before)
            self.run.trace.append(row)
            self.apply(r, cand, w, sanc)
            return
        if ob is not None:
            ob.decision(r, w, o, order, None)

    def friend_attempt(self, w, rec):
        tgt = "A" if w % 2 == 0 else "B"
        rec["c_attempts"] += 1
        me = self.p[tgt]
        if not me["in"] or me["ill"] or self.moved:
            return
        if self.fx and self.fx.pairing is not None:      # H38 dyadic withdrawal: a member living with the partner may turn the friend down
            d = _PAIR.withdraw(self, tgt)
            if d and self.pair_rng.random() < d:
                self.pstats["friend_declined"] += 1
                if self.observer is not None:
                    self.observer.friend(w, tgt, "declined", d=d)
                return
        dec, _, reasons = self.decide(tgt, "see_friend", w)
        if self.observer is not None:
            self.observer.friend(w, tgt, "blocked" if dec == "hard" else "met", dec=dec, reasons=reasons)
        if dec == "hard":
            rec["c_blocked"] += 1
        else:
            self.wk[tgt]["friend_initiated"] += 1
            if self.lv and self.lv.network:
                self._lever_visit(tgt, scaled=False)

    def start_shocks(self, w, ev):
        for s in self.shocks.get(w, []):
            r, k = s["role"], s["kind"]
            ev.append({"week": w, **s})
            if k == "move":
                self.moved = s["duration"]
                for x in "AB":
                    if self.observer is not None:
                        self.observer.flow_direct(w, x, "outside", min(3, max(0, self.p[x]["money"])), "move_cost")
                    self.wk[x]["conn_hit"] += 0.3; self.wk[x]["sec_hit"] += 0.1; self.p[x]["money"] = max(0, self.p[x]["money"] - 3)
            elif k == "job_loss":
                self.p[r]["jobless"] = s["duration"]; self.wk[r]["sec_hit"] += 0.15
            elif k == "illness":
                self.p[r]["ill"] = s["duration"]; self.wk[r]["sec_hit"] += 0.05
            elif k == "new_connection":
                self.hed[r].event_new_connection()
                self.hed[r].level["connection"] = min(1.0, self.hed[r].level["connection"] + 0.3)

    def step_week(self, w, last_week):
        ob = self.observer
        if ob is not None:
            ob.week_begin(w, last_week)
        ev = []
        if self.fx is not None and self.fx.agent_values == "hybrid":
            _HY.week_start(self, w, last_week)
        self.wk = {r: {"income": 0, "spent_self": 0, "works": 0, "rests": 0, "friends": 0, "together": 0, "contrib": 0,
                       "friend_initiated": 0, "sanctioned": 0, "conn_hit": 0.0, "sec_hit": 0.0, "pressed": 0, "took": 0} for r in "AB"}
        self.units = {r: UNITS for r in "AB"}
        self.start_shocks(w, ev)
        if self.contest:
            before = ob.balances() if ob is not None else None
            _EXIT.contest_tick(self, w)
            if ob is not None:
                ob.flow_diff(w, "contest", None, before)
        if self.items:
            _ITEMS.week_start(self, w)
        if self.makers:
            _MAKERS.week_start(self, w)      # H39: the making choice; its time comes out of this week's units
        if self.mech:
            for c in self.commits:       # a commitment that stands unbroken this week: the beneficiary's trust in the bound partner recovers slowly
                if self._active(c, w) and not c["breached"]:
                    self._trust_move(c["to"], TRUST["kept_week"], "kept", w)
            for r in "AB":               # a bound request that ran its weeks without being broken counts as honored
                for k, until in list(self.bound_req[r].items()):
                    if until <= w:
                        del self.bound_req[r][k]
                        if not self.bound_broken[r].pop(k, False):
                            self._trust_move(self.other(r), TRUST["honored_request"], "honored", w)
        if self.hook:
            self.hook(self, w)
        if self.lv:
            self._lever_start(w)
        if self.fx:
            self._fix_week_start(w)
        if self.count_menus or (self.fx and self.fx.take_menu_terms):
            for r in "AB":
                self._count_menu(r, w)
        probes = {r: self.probe(r, w) for r in "AB"}
        rec = {"blocked": {r: set() for r in "AB"}, "c_attempts": 0, "c_blocked": 0}
        for ps in range(PASSES):
            for r in "AB":
                self.step_agent(r, w, last_week, rec)
            if ps == 0:
                self.friend_attempt(w, rec)
        # end of week: costs, safety net, settlement, hedonic close
        hrow = {}
        for r in "AB":
            me, wk = self.p[r], self.wk[r]
            cost = HD.DEFAULT.living_cost + (1 if me["ill"] else 0) + (0 if (me["in"] or self.with_friend(r)) else 1.5)
            if ob is not None:
                m0, p0 = me["money"], self.pool
            me["money"] -= cost
            if me["money"] < 0:                         # the shared pot as a safety net (ASSUMED): an overdrawn member draws from it
                draw = min(self.pool, -me["money"] + 2)
                self.pool -= draw; me["money"] += draw
                if ob is not None:
                    ob.flow_direct(w, "pot", r, draw, "safety_net")
            me["money"] = max(0, me["money"])
            if ob is not None:
                ob.flow_direct(w, r, "outside", m0 + (p0 - self.pool) - me["money"], "living_cost")
        settle = w % MONTH_WEEKS == MONTH_WEEKS - 1
        if settle:
            if getattr(self, "agree", None) and self.fx is not None and self.fx.agent_values == "hybrid":
                _HY.pay_agreed(self, w)                 # hybrid: the bill shares agreed at formation, paid as a standing transfer
            need = self.need_month()
            self.bills_met = need > 0 and self.funded >= need        # funded by contributions (what the oracle reads)
            short = max(0, need - self.funded)
            inn = [r for r in "AB" if self.p[r]["in"]]
            if self.fx and self.fx.bills_hurt:
                self._settle_hurt(w, need, short, inn)
            else:
                d = min(self.pool, short)                                # unfunded bills come out of the shared pot
                self.pool -= d
                short -= d
                if ob is not None:
                    ob.flow_direct(w, "pot", "bills", d, "bills_from_pot", short=short)
                if short > 0.01:                                         # bills unpaid even from savings (ASSUMED security hit)
                    for r in inn:
                        self.wk[r]["sec_hit"] += 0.15
        busy = {r: self.wk[r]["friends"] + self.wk[r]["works"] >= 2 for r in "AB"}
        if self.fx:
            self._role_end_week(w, settle)
        lvl = self.lv
        if lvl:
            self._lever_end_week(w)
            eff_t = sum(self.lw["tog"]) if lvl.adapt else None
        for r in "AB":
            me, wk, h = self.p[r], self.wk[r], self.hed[r]
            oth = self.p[self.other(r)]
            if settle and me["in"]:
                me["months_in"] += 1
            if not me["in"]:
                me["weeks_out"] += 1
            assets = me["money"] + self.share(r)
            ill = 0.3 if me["ill"] else 0.0
            tog_in, fr_in, cpen = wk["together"], wk["friends"], wk["conn_hit"] + (0.1 if self.moved else 0.0)
            if lvl:
                if lvl.adapt:
                    tog_in, fr_in = eff_t, sum(self.lw["fr"][r])
                if lvl.network and self._down("H", 0, w):
                    cpen += lvl.partner_rupture_conn
            h.tick(rest_actions=wk["rests"], work_blocks=wk["works"], friend_visits=fr_in, together=tog_in,
                   friend_initiated=wk["friend_initiated"] + (1 if self.with_friend(r) else 0),
                   cohabiting=(me["in"] and oth["in"]) or self.with_friend(r), assets=assets,
                   money=me["money"], extra_rest_drain=ill, extra_security_drain=wk["sec_hit"],
                   connection_penalty=cpen)
            pr = self.probe(r, w)
            restricted = me["in"] and not all(pr["open"][o] for o in ("work", "see_friend", "refuse")) or \
                (me["in"] and not pr["open"]["spend"])
            trapped = me["in"] and pr["exit_retained"] < 0.25
            if self.mech and me["in"] and self.stay_bound(r, w):
                # a consented stay commitment is not suffering by itself: trapped only if the rules alone trap, or the bound
                # partner is also unhappy (previous week's low-position streak >= 1) and cannot leave with 25 percent
                trapped = self._rr[r] < 0.25 or (pr["exit_retained"] < 0.25 and me["low"] >= 1)
            open_share = sum(pr["open"][o] for o in ("work", "spend", "see_friend", "refuse")) / 4
            warn = sum(1 for s in self.sanctions[r] if s["kind"] == "warn" and s["until"] > w)
            net = wk["income"] - HD.DEFAULT.living_cost - BILLS_WEEKLY - wk["spent_self"]
            asp = {"security_buffer": h.level["security"], "together_per_week": wk["together"],
                   "friends_per_week": wk["friends"], "savings_per_week": max(0, net), "autonomy": open_share}
            fric = (WARN_FRICTION if warn else 0.0) + PRESS_FRICTION * wk["pressed"]
            if self.contest:
                fric += _EXIT.CONTEST_FRICTION
            if self.fx and self.fx.bills_hurt:
                fric += wk.get("bill_fric", 0.0)
            ip = _ITEMS.weekly_pleasure(self, r) if self.items else 0.0     # exit fallbacks slice 2: home and pet (0 when off)
            if h.parts_on:                                  # observer layer: the sources inside extra_pleasure and friction
                h.xparts = {"items": ip, "warn": WARN_FRICTION if warn else 0.0, "press": PRESS_FRICTION * wk["pressed"],
                            "contest": _EXIT.CONTEST_FRICTION if self.contest else 0.0}
                if self.fx and self.fx.bills_hurt:
                    h.xparts["bills"] = wk.get("bill_fric", 0.0)
            if self.makers:                                                 # H39: what was made for r, and craving (0 when off)
                mp, mf = _MAKERS.week_terms(self, r, w)
                if self.fx and self.fx.agent_values in ("v2", "v2b", "hybrid"):
                    self._mk_last = {**getattr(self, "_mk_last", {}), r: (mp, mf)}     # agent values v2 reads last week's makers terms
                ip, fric = ip + mp, fric + mf
            if self.fx:
                fx = self.fx
                if fx.valued_money:
                    pw = self.personas[r].weights
                    h.valued = (fx, float(me["money"]), float(pw["money"]), float(pw["security"]))
                xp, xf, terms = self._lever_terms(r, w) if lvl else (0.0, 0.0, None)
                fp, ff, fterms = self._fix_terms(r, w)
                if h.parts_on:
                    h.xparts.update(lever_pl=xp, lever_fr=xf, fix_pl=fp, fix_fr=ff, fix=dict(fterms), lever=dict(terms or {}),
                                    amp=getattr(h, "amp_split", None) if fx.contact else None)
                hrow[r] = h.close_week(asp, trapped=trapped, restricted=restricted, together_sessions=tog_in,
                                       friction=fric + xf + ff, extra_pleasure=xp + fp + ip, report_raw=fx.pairing is not None)
                if lvl:
                    hrow[r]["lever"] = {**{k: round(v, 5) for k, v in terms.items()}, "eff_together": round(tog_in, 4),
                                        "K": round(self.K, 4), "q0": round(getattr(self, "q0", 0.0), 4)}
                hrow[r]["fix"] = {k: (round(v, 5) if isinstance(v, float) else v) for k, v in fterms.items()}
            elif lvl:
                xp, xf, terms = self._lever_terms(r, w)
                if h.parts_on:
                    h.xparts.update(lever_pl=xp, lever_fr=xf, lever=dict(terms))
                hrow[r] = h.close_week(asp, trapped=trapped, restricted=restricted, together_sessions=tog_in,
                                       friction=fric + xf, extra_pleasure=xp + ip)
                hrow[r]["lever"] = {**{k: round(v, 5) for k, v in terms.items()}, "eff_together": round(tog_in, 4),
                                    "K": round(self.K, 4), "q0": round(getattr(self, "q0", 0.0), 4)}
            else:
                hrow[r] = h.close_week(asp, trapped=trapped, restricted=restricted, together_sessions=wk["together"],
                                       friction=fric, extra_pleasure=ip)
            me["low"] = me["low"] + 1 if h.B < -0.2 else 0
            for k in ("jobless", "ill"):
                me[k] = max(0, me[k] - 1)
        self.moved = max(0, self.moved - 1)
        self.sanctions = {r: [s for s in self.sanctions[r] if s["until"] > w] for r in "AB"}
        self.vetoes = {r: {k: u for k, u in self.vetoes[r].items() if u > w} for r in "AB"}
        for r in "AB":                      # seed v2: a bound request lapses after BIND_WEEKS
            for k in [k for k, u in self.bound_req[r].items() if u <= w]:
                del self.bound_req[r][k]
                self.pending[r].discard(k)
        for r in "AB":                      # amendment 1 (v3a prereg): a request for time lapses at the end of the week
            self.pending[r].discard("time")
        both_in = all(self.p[r]["in"] for r in "AB")
        row = {"month": w, "week": w, "need_met": self.bills_met, "both_in": both_in,
               "partners": {r: {**probes[r], "contributed": False} for r in "AB"},
               "c_attempts": rec["c_attempts"], "c_blocked": rec["c_blocked"], "hedonic": hrow, "shocks": ev,
               "blocked": {r: sorted(rec["blocked"][r]) for r in "AB"},
               "sanctioned": {r: self.wk[r]["sanctioned"] for r in "AB"}}
        self.run.outcomes.append(row)
        self.month_rows.append(row)
        if settle:
            for rw in self.month_rows:
                for r in "AB":
                    rw["partners"][r]["contributed"] = self.contrib_month[r] > 0 and self.p[r]["in"]
                rw["need_met"] = self.bills_met
            self.month_rows, self.funded = [], 0
            self.contrib_month = {"A": 0, "B": 0}
        if ob is not None:
            ob.week_end(w, row, busy, settle)
        return busy

    def play(self):
        last = {"busy": {"A": False, "B": False}}
        for w in range(self.weeks):
            last = {"busy": self.step_week(w, last)}
        self.run.final = {r: {**self.p[r], "pooled": self.pool, "put": self.put[r]} for r in "AB"}   # "pooled": the one shared balance
        if self.mech:
            self.run.meta = self.commit_report()
        if self.fx:
            self.run.fix = self.fix_report()
        if self.lv:
            self.run.lever = {**self.lstats, "K": self.K, "ritual": bool(self.ritual), "policy": dict(self.policy),
                              "kept": list(self.ritual["kept"]) if self.ritual else []}
        return self.run


def run_weekly(cards, personas, seed=0, weeks=WEEKS, cfg=HD.DEFAULT, deal=None, breach_forfeit=BREACH_FORFEIT, levers=None, fixes=None):
    """personas: (Partner A persona, Partner B persona). -> Run (trace, outcomes with weekly hedonic rows, final)."""
    return WeeklyWorld(cards, personas, seed, weeks, cfg, deal, breach_forfeit, levers, fixes).play()
