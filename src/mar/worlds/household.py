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
  consented (1 if the actor agreed to the standing request), need_gap (unfunded part of this month's shared
  need), months_in (months in the household), other_in (1 if the other partner is in the household),
  take (percent of the actor's pooled share carried out on `leave`; 0 for every other action).
"""
import random
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path

import z3

from .. import compile as _compile
from .. import english as _english
from ..cards import load_cards
from ..patch_check import check_sanctions

ROOT = Path(__file__).resolve().parents[3]
RULES = ROOT / "rules" / "household"

# ---- vocabulary and bounds -------------------------------------------------------------------

STATE_VARS = ("pooled", "money", "other_earns_more", "no_contact_request", "stay_home_request", "consented",
              "need_gap", "months_in", "other_in")
VAR_NAMES = STATE_VARS + ("take",)
Z = dict(zip(VAR_NAMES, z3.Ints(" ".join(VAR_NAMES))))
BOUNDS = {"pooled": (0, 100), "money": (0, 100), "other_earns_more": (0, 1), "no_contact_request": (0, 1),
          "stay_home_request": (0, 1), "consented": (0, 1), "need_gap": (0, 10), "months_in": (0, 36),
          "other_in": (0, 1), "take": (0, 100)}
PHRASES = {"pooled": "the pooled share", "money": "the private money", "other_earns_more": "the earns-more flag",
           "no_contact_request": "the no-contact request flag", "stay_home_request": "the stay-home request flag",
           "consented": "the consent flag", "need_gap": "the unfunded need", "months_in": "the months in the household",
           "other_in": "the other-partner-in flag", "take": "the share taken"}
PARTNER_ACTIONS = ("work", "spend_shared", "spend_self", "see_friend", "refuse_request", "request", "leave", "return")
EXTRA_ACTIONS = ("gift_pooled",)   # harness-only move (side channel); the formal model in seam_depth does not have it
GIFT = 8
FRIEND_ACTIONS = ("work", "spend_self", "see_friend", "refuse_request")
K_DEFAULT = 3
MIN_EXIT_TAKE = 25          # meaningful exit: leave carrying at least 25 percent of the pooled share
SUSPEND_ALLOWS = ("work", "spend_shared", "refuse_request")   # ASSUMED meaning of the suspend sanction
CAP_HALVE_BANS = ("spend_self",)                               # ASSUMED meaning of cap_halve
VARIANTS = ("free_chaotic", "trap", "contact_free", "exit_half", "veto_consent", "needs_duty", "baseline")


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
