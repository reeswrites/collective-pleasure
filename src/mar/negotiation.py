"""Negotiated pots (docs/decisions/0013-negotiated-pots.md, docs/results/negotiation-prereg.md).

The author: "i think you have to negotiate shared pots with multiple agents or creating rules for it". Pot terms are not imposed by
the seed. Everyone who shares a pot (two or more) negotiates a bundle of terms from a small finite menu; an agreement compiles to
ADICO cards, and the proof checks run BEFORE anyone lives under them. No LLM, no network.

Everything numeric here is the prereg's, fixed before any run. The evaluation of living under a bundle is a closed-form PROXY of
the persona's weights (ASSUMED, not validated against rollouts). Wording rule: agents feel nothing; "value" is a modeled gloss.
"""
import contextlib
import copy
import random
import re
from dataclasses import dataclass, field
from itertools import product

import numpy as np

from .cards import make_card
from . import exit_items as _ITEMS
from . import hedonic as HD
from . import observe as _OBS
from . import pairing as _PAIR
from .worlds import household as H

# ---- the terms menu -------------------------------------------------------------------------------------------------
TERMS = {
    "contribution": ("none", "fixed", "proportional"),
    "use": ("needs_only", "any_use", "caps"),
    "taking": ("allowed", "forbidden", "repay"),
    "change": ("unanimous", "propose_accept", "frozen"),
    "exit": ("equal_split", "proportional", "forfeit"),
    "stay": (0, 52),                       # weeks, mutual; only where the base rules let a partner choose to bind
    "requests": ("none", "mutual"),        # accept the others' stay_home requests for 52 weeks
}
TERM_NAMES = tuple(TERMS)
TERM_ID = {"N1": "contribution", "N2": "use", "N3": "taking", "N4": "change", "N5": "exit", "N6": "stay", "N7": "requests", "N8": "requests"}   # N8 (fine) only exists with requests, so a failing N8 bans the requests term
STAY_WEEKS = 52
DEADLINE = 12
LAMBDA0 = {"competitive": 0.1, "direct": 0.4, "avoidant": 0.6, "collaborative": 1.0, "accommodating": 1.5}
THETA0 = {"competitive": 0.10, "direct": 0.06, "avoidant": 0.04, "collaborative": 0.02, "accommodating": 0.0}
LAMBDA_END = 2.0
K = 3                                       # proof-check bound (months)
STUB_EXIT_CARDS = ()      # seed v2.2: the even-split stand-in cards R8b/R8c are gone (git history); R8b-exit-terms-negotiated is a `may` and stays in the base
IMPOSED = {"contribution": "none", "use": "needs_only", "taking": "forbidden", "change": "propose_accept",
           "exit": "equal_split", "stay": 0, "requests": "none"}      # what the rejected R3b-era seed imposed (reference only)


def key(b):
    return tuple(b[t] for t in TERM_NAMES)


def bundles(allow_stay=True, allow_requests=True):
    """All bundles of the menu, in a fixed lexicographic order. Each is a dict term -> value."""
    vals = [TERMS[t] if (t not in ("stay", "requests") or (t == "stay" and allow_stay) or (t == "requests" and allow_requests))
            else (TERMS[t][0],) for t in TERM_NAMES]
    return [dict(zip(TERM_NAMES, v)) for v in product(*vals)]


# ---- persona evaluation (closed-form proxy; ASSUMED) ------------------------------------------------------------------

def _raw(p, low):
    w = p.weights
    s, a, t, m, o, r = w["security"], w["autonomy"], w["togetherness"], w["money"], w["other_connections"], p.risk_tolerance
    F, C, O = ("press-freerider" in p.tags), ("press-controller" in p.tags), ("press-overasker" in p.tags)
    L = 1 if low else 0
    return {
        "contribution": {"none": 0.25 * a + 0.15 * m - 0.35 * s, "fixed": 0.20 * s - 0.15 * a - 0.05 * m + 0.05 * t,
                         "proportional": 0.25 * s - 0.10 * a + 0.05 * t + (0.10 if L else -0.10)},
        "use": {"needs_only": 0.30 * s + 0.15 * t - 0.20 * a - 0.10 * m, "any_use": 0.30 * a + 0.25 * m - 0.30 * s + (0.30 if F else 0),
                "caps": 0.15 * s + 0.10 * a + 0.05},
        "taking": {"allowed": 0.15 * a + 0.10 * m - 0.45 * s + (0.50 if F else 0),
                   "forbidden": 0.40 * s + 0.10 * t - 0.10 * a + (0.10 if C else 0) - (0.45 if F else 0),
                   "repay": 0.15 * s + 0.05 * a - (0.10 if F else 0)},
        "change": {"unanimous": 0.25 * s + 0.10 * a + (0.10 if C else 0), "propose_accept": 0.20 * a + 0.10 * r - 0.05 * s,
                   "frozen": 0.30 * s - 0.25 * a - 0.15 * r + (0.15 if C else 0)},
        "exit": {"equal_split": 0.10 + 0.10 * a - 0.05 * m, "proportional": 0.15 * m + 0.10 * a - 0.05 * t - (0.05 if L else 0),
                 "forfeit": 0.35 * s * t - 0.50 * a - 0.20 * o + (0.20 if C else 0)},
        "stay": {0: 0.0, STAY_WEEKS: 0.25 * s + 0.15 * t - 0.35 * a - 0.10 * o},
        "requests": {"none": 0.0, "mutual": 0.10 * s + 0.15 * t - 0.35 * a - 0.10 * o + (0.10 if O else 0)},
    }


def term_values(p, low=False):
    """Centered term values: {term: {value: float}}. Only differences between a term's values matter."""
    out = {}
    for term, d in _raw(p, low).items():
        mean = sum(d.values()) / len(d)
        out[term] = {v: x - mean for v, x in d.items()}
    return out


def pot_value(p, n=2):
    w = p.weights
    v2 = 0.15 + 0.30 * w["security"] + 0.30 * w["togetherness"] + 0.10 * w["money"] - 0.10 * w["autonomy"]
    return v2 if n == 2 else 0.8 * v2 - 0.05 - 0.10 * w["security"]


def outside_option(p):
    """What a member gets by not forming or not joining the pot (keeps own holdings; bills still split). Closed-form proxy."""
    w = p.weights
    return 0.05 + 0.15 * w["autonomy"] + 0.15 * w["other_connections"] + 0.05 * w["money"] - 0.05 * w["security"]


def utility(p, b, low=False, n=2):
    tv = term_values(p, low)
    return pot_value(p, n) + sum(tv[t][b[t]] for t in TERM_NAMES)


_UCACHE = {}


def utilities(p, blist, low, n, menu):
    ck = (p.id, low, n, menu)
    if ck not in _UCACHE:
        tv = term_values(p, low)
        _UCACHE[ck] = np.array([pot_value(p, n) + sum(tv[t][b[t]] for t in TERM_NAMES) for b in blist])
    return _UCACHE[ck]


# ---- compiling an agreement to cards -------------------------------------------------------------------------------

_SOFT_WARN = {"kind": "warn", "duration_months": 1, "sanctioner": "household"}
_SOFT_HALVE = {"kind": "cap_halve", "duration_months": 2, "sanctioner": "household"}
GLOSS = {
    ("contribution", "none"): "Nobody owes the pot anything day to day; each member puts in what they choose.",
    ("contribution", "fixed"): "While this month's shared need is unfunded, a member should not spend on themselves; breaking this earns a one-month warning. (No fixed amount is set; the rule only restricts self-spending.)",
    ("contribution", "proportional"): "While this month's shared need is unfunded, the higher earner should not spend on themselves; breaking this earns a one-month warning. (Only the higher earner is restricted; no amount is tied to income.)",
    ("use", "needs_only"): "A member may draw from the pot only when there is a shared need open.",
    ("use", "any_use"): "Any member may draw from the pot for any purpose.",
    ("use", "caps"): "A member may draw from the pot only while their own private money is under 10.",
    ("taking", "allowed"): "A member may draw from the pot for themselves.",
    ("taking", "forbidden"): "No member may draw from the pot for themselves; it pays the shared bills and what a leaver carries out.",
    ("taking", "repay"): "A member who draws from the pot for themselves may not spend on themselves at all for two months (the code's cap_halve sanction bars self-spending; nothing models making it good).",
    ("change", "unanimous"): "The pot terms change only when every other member accepts the proposed change and the new terms pass the proof checks (the `amend` action; reviews every 13 weeks also accept any change all members agree to).",
    ("change", "propose_accept"): "Any member may propose a change to the pot terms; it takes effect when a majority of members (the proposer counts) accept it and the new terms pass the proof checks (the `amend` action).",
    ("change", "frozen"): "The pot terms can never be changed by an amend action. (Reviews every 13 weeks still accept any change all members agree to; the card matters in the proof check that a frozen pot needs an exit.)",
    ("exit", "equal_split"): "A member who leaves carries half of the whole pot and leaves the other half in it.",
    ("exit", "proportional"): "A member who leaves carries what they put into the pot (at most what it holds) and leaves the rest in it. A floor may top this up (card FLOOR-exit-floor).",
    ("exit", "forfeit"): "A member who leaves carries none of the pot, except what the exit floor tops up (card FLOOR-exit-floor).",
    ("stay", STAY_WEEKS): "Every member commits to stay for 52 weeks; leaving earlier forfeits the breach share of what the exit term would let them carry (the breach cost term sets that share; the whole of it by default).",
    ("requests", "mutual"): "Every member commits to honor the others' stay-home requests for 52 weeks (a bound stay-home request bars seeing the friend and spending on oneself).",
    ("fine", "some"): "A member who breaks a request commitment they chose pays the wronged member a fine of 3 money (the code's REQUEST_FINE); without this term breaking it carries no fine, only the loss of the other member's trust.",
    ("fine", "big"): "A member who breaks a commitment they chose (a request commitment, a stay, or an agreed role) pays the wronged member a fine of 6 money. Both members chose this term; while it stands both pay a small scorekeeping cost each week.",
    ("roles", "earner_planner"): "Partner A holds the earning role (works and keeps the bills funded); Partner B holds the planning role (plans time together). A role holder gets better at the job over time. A lapse leads to a soft check-in, then an early renegotiation; no penalty unless both chose a fine.",
    ("roles", "swapped"): "Partner B holds the earning role (works and keeps the bills funded); Partner A holds the planning role (plans time together). A role holder gets better at the job over time. A lapse leads to a soft check-in, then an early renegotiation; no penalty unless both chose a fine.",
    ("roles", "shared"): "Both partners share every recurring job; nobody holds a role.",
}
FIX_FINES = ("none", "some", "big")       # fix 4: opt-in fines; "some" = 3 money (REQUEST_FINE), "big" = 6
ROLES = ("none", "earner_planner", "swapped", "shared")    # seed v2.3 rule 14 (roles as a negotiated term)



def _card(cid, deontic, aim, conds, gloss, source, or_else=None):
    return make_card({"id": cid, "attribute": "partner", "deontic": deontic, "aim": aim,
                      "conditions": [{"expr": e, "op": o, "value": v} for e, o, v in conds], "or_else": or_else,
                      "gloss": gloss, "source": source})


def _names(members):
    return ", ".join(members[:-1]) + " and " + members[-1] if len(members) > 1 else members[0]


def compile_bundle(b, members):
    """Bundle -> ADICO cards (gloss + source 'negotiated, week 0, members X,Y,Z'). members: list of persona ids."""
    src = f"negotiated, week 0, members {','.join(members)}"
    g = lambda term: GLOSS[(term, b[term])]
    cards = [_card("N0-members", "may", "spend_shared", [], f"There is one pot, shared by {_names(members)}; each may put money into it and draw from it, subject only to the terms below.", src)]
    c = b["contribution"]
    if c == "none":
        cards.append(_card("N1-contribution-none", "may", "spend_self", [], g("contribution"), src))
    elif c == "fixed":
        cards.append(_card("N1-contribution-fixed", "must_not", "spend_self", [("need_gap", "gt", 0)], g("contribution"), src, _SOFT_WARN))
    else:
        cards.append(_card("N1-contribution-proportional", "must_not", "spend_self", [("need_gap", "gt", 0), ("other_earns_more", "eq", 0)],
                           g("contribution"), src, _SOFT_WARN))
    u = b["use"]
    cards.append({"needs_only": lambda: _card("N2-use-needs_only", "must_not", "take_shared", [("need_gap", "eq", 0)], g("use"), src),
                  "any_use": lambda: _card("N2-use-any_use", "may", "take_shared", [], g("use"), src),
                  "caps": lambda: _card("N2-use-caps", "must_not", "take_shared", [("money", "ge", 10)], g("use"), src)}[u]())
    t = b["taking"]
    cards.append({"allowed": lambda: _card("N3-taking-allowed", "may", "take_shared", [], g("taking"), src),
                  "forbidden": lambda: _card("N3-taking-forbidden", "must_not", "take_shared", [], g("taking"), src),
                  "repay": lambda: _card("N3-taking-repay", "must_not", "take_shared", [], g("taking"), src, _SOFT_HALVE)}[t]())
    ch = b["change"]
    cards.append({"unanimous": lambda: _card("N4-change-unanimous", "must_not", "amend", [("consented", "eq", 0)], g("change"), src),
                  "propose_accept": lambda: _card("N4-change-propose_accept", "may", "amend", [], g("change"), src),
                  "frozen": lambda: _card("N4-change-frozen", "must_not", "amend", [], g("change"), src)}[ch]())
    e = b["exit"]
    if e == "equal_split":
        cards.append(_card("N5a-exit-equal_split", "must_not", "leave", [("pooled", "gt", 0), ("take", "lt", 50)], g("exit"), src))
        cards.append(_card("N5b-exit-equal_split", "must_not", "leave", [("pooled", "gt", 0), ("take", "gt", 50)], g("exit"), src))
    elif e == "proportional":
        cards.append(_card("N5a-exit-proportional", "must_not", "leave", [("pooled", "gt", 0), ("take", "lt", 100)], g("exit"), src))
    else:
        cards.append(_card("N5a-exit-forfeit", "must_not", "leave", [("pooled", "gt", 0), ("take", "gt", 0)], g("exit"), src))
    if b["stay"]:
        cards.append(_card("N6-stay-52", "may", "commit_stay", [], g("stay"), src))
    if b["requests"] == "mutual":
        cards.append(_card("N7-requests-mutual", "may", "commit_request", [], g("requests"), src))
        if b.get("fine", "none") == "some":
            # a `may commit_request` like N7 and R8d: the consequence of breaking the commitment is stated on the card and enforced by the
            # world (WeeklyWorld.fine reads this card's id); the shared sanction check knows only warn / cap_halve / suspend
            cards.append(_card("N8-fine-some", "may", "commit_request", [], g("fine"), src))
    if b.get("roles", "none") != "none":
        cards.append(_card(f"N9-roles-{b['roles']}", "may", "role", [], g("roles"), src))
    f = b.get("fine", "none")
    if f != "none" and not (b["requests"] == "mutual" and f == "some"):
        # fix 4: an opt-in fine on any chosen commitment (stay, requests or roles); the world reads the card id (WeeklyWorld.fine_amount)
        aim = "commit_request" if b["requests"] == "mutual" else ("commit_stay" if b["stay"] else "role")
        cards.append(_card(f"N8-fine-{f}", "may", aim, [], GLOSS[("fine", "big")] if f == "big" else g("fine"), src))
    return cards


FLOOR_SOURCE = "Claude's default, approved by the author 2026-11-10 (the author asked for a floor under negotiation; 13 weeks of living costs = 26 units is Claude's number, approved by the author's \"yes\")"


def floor_cards(floor):
    """The exit floor as an explicit card (empty list when the floor is off). The world enforces it when a member leaves (carry_out
    tops the carry up, never beyond the member's equal half of the pot) and negotiation checks every proposal against it; the card
    is a `may leave` (see rules/README.md: a `may` card documents a permission or a mechanism the gate does not enforce itself)."""
    if floor is None:
        return []
    return [_card("FLOOR-exit-floor", "may", "leave", [],
                  f"Whatever the exit term, a member who leaves always carries at least {floor:g} units of their own (about {FLOOR_WEEKS} weeks of "
                  f"living costs), topped up from the pot but never beyond their equal half of it, or less if there is less to carry.",
                  FLOOR_SOURCE)]


def base_cards(variant):
    """The v2.1 base rules of a seed variant, without the stub exit terms (the negotiated exit term replaces them)."""
    return [c for c in H.load_variant(variant) if c.id not in STUB_EXIT_CARDS]


def menu_of(base):
    """Which optional commitments the base rules let a partner choose to make."""
    gate = H.PyGate(base)
    st = {n: 0 for n in H.STATE_VARS}
    out = {"stay": gate.check("partner", "commit_stay", st)[0], "requests": gate.check("partner", "commit_request", st)[0]}
    fx = HD.active_fixes()
    if fx and fx.roles:     # seed v2.3: roles are on the menu only where a base card permits agreeing roles
        out["roles"] = any(c.aim == "role" and c.deontic == "may" for c in base)
    return out


# ---- proof checks BEFORE living ------------------------------------------------------------------------------------

_PCACHE = {}


def proof_check(cards, k=K):
    """-> {"ok", "checks": [{check, verdict, cards, detail}], "fails": [failing checks]}. The five household checks at bound k
    plus (f) a frozen pot with no exit within k is unrepairable. A check that is 'open' also rejects ('open' never means safe)."""
    sig = (tuple(sorted(c.id for c in cards)), k)
    if sig in _PCACHE:
        return _PCACHE[sig]
    checks = [dict(c) for c in H.check_spec(cards, k)]
    exit_v = next(c for c in checks if c["check"] == "e_exit_within_k")
    frozen = [c.id for c in cards if c.id.startswith("N4-change-frozen")]
    if frozen and exit_v["verdict"] != "pass":
        checks.append({"check": "f_change_or_exit", "verdict": "fail", "cards": sorted(set(frozen + exit_v["cards"])),
                       "detail": "the terms can never be changed and there is no exit within k: no repair path", "bound": exit_v["bound"]})
    else:
        checks.append({"check": "f_change_or_exit", "verdict": "pass", "cards": [],
                       "detail": "the terms can be changed, or an exit exists within k", "bound": exit_v["bound"]})
    fails = [c for c in checks if c["verdict"] != "pass"]
    out = {"ok": not fails, "checks": checks, "fails": fails}
    _PCACHE[sig] = out
    return out


def failure_text(chk, cards):
    cm = {c.id: c for c in cards}
    why = {"f_change_or_exit": "the terms can never be changed and no member can leave with something: no way to repair the pot"}
    head = why.get(chk["check"]) or H.explain_verdict(chk, cards).split(": fails. ", 1)[-1].split(" Rules involved")[0]
    ids = "; ".join(f"{i} ({cm[i].gloss.rstrip('.')})" if i in cm else i for i in chk["cards"])
    return f"{H.CHECK_TITLES.get(chk['check'], chk['check'])}: {head} [{ids}]"


def _ban_from(chk, b):
    """The combination of this bundle's term values that the failing cards came from (members learn it and ban it)."""
    terms = sorted({TERM_ID[m.group(1)] for i in chk["cards"] if (m := re.match(r"(N\d)", i))}, key=TERM_NAMES.index)
    if not terms:
        terms = list(TERM_NAMES)
    return frozenset((t, b[t]) for t in terms)


# ---- the protocol --------------------------------------------------------------------------------------------------

@dataclass
class Negotiation:
    members: list                 # persona ids, table order
    roles: list
    seed: int
    variant: str
    status: str                   # "agreed" | "deadline" | "no_bundle"
    bundle: dict | None
    proposals: list = field(default_factory=list)      # every proposal: k, proposer, bundle, accepted_by, rejected_by, outcome
    rejections: list = field(default_factory=list)     # proof-filter rejections: k, proposer, bundle, checks (text), cards
    cards: list | None = None
    outside: dict = field(default_factory=dict)
    utilities: dict = field(default_factory=dict)      # agreed bundle's value to each member

    @property
    def agreed(self):
        return self.status == "agreed"


def negotiate(personas, variant="author_seed_v2_bindable", seed=0, roles=None, base=None, deadline=DEADLINE):
    """Alternating offers generalized to N members with a deadline (docs/results/negotiation-prereg.md).
    personas: list of Persona (2 or more); roles default A, B, C, ... (A is the higher earner; others count as lower earners).
    No agreement -> status deadline/no_bundle -> no pot (members keep their own holdings)."""
    n = len(personas)
    roles = list(roles or "ABCDEFG"[:n])
    base = base if base is not None else base_cards(variant)
    menu = menu_of(base)
    blist = bundles(menu["stay"], menu["requests"])
    ukey = (menu["stay"], menu["requests"])
    U = {p.id: utilities(p, blist, roles[i] != "A", n, ukey) for i, p in enumerate(personas)}
    O = {p.id: outside_option(p) for p in personas}
    ids = [p.id for p in personas]
    order = list(range(n))
    random.Random(f"{seed}|{','.join(ids)}").shuffle(order)
    keys = [key(b) for b in blist]
    bans, alive = [], np.ones(len(blist), dtype=bool)
    res = Negotiation(ids, roles, seed, variant, "deadline", None, outside=dict(O))

    def banned_mask(ban):
        return np.array([all(b[t] == v for t, v in ban) for b in blist])

    for k in range(deadline):
        c = k / (deadline - 1)
        i = order[k % n]
        me = personas[i]
        lam = LAMBDA0[me.negotiation_style] + (LAMBDA_END - LAMBDA0[me.negotiation_style]) * c
        score = U[me.id].copy()
        for j, q in enumerate(personas):
            if j != i:
                score = score + lam * np.minimum(0.0, U[q.id] - O[q.id])
        ok = alive & (U[me.id] > O[me.id])
        if not ok.any():
            res.status = "no_bundle"
            break
        score = np.where(ok, np.round(score, 9), -np.inf)
        idx = int(np.argmax(score))
        b = blist[idx]
        acc, rej = [me.id], []
        for j, q in enumerate(personas):
            if j == i:
                continue
            theta = THETA0[q.negotiation_style] * (1 - c)
            (acc if U[q.id][idx] > O[q.id] + theta else rej).append(q.id)
        prop = {"k": k, "proposer": me.id, "bundle": dict(b), "accepted_by": acc, "rejected_by": rej, "outcome": "refused" if rej else "all accept"}
        res.proposals.append(prop)
        if rej:
            continue
        cards = compile_bundle(b, ids)
        pc = proof_check(base + cards)
        if pc["ok"]:
            prop["outcome"] = "agreed"
            res.status, res.bundle, res.cards = "agreed", dict(b), cards
            res.utilities = {q.id: float(U[q.id][idx]) for q in personas}
            return res
        prop["outcome"] = "rejected by the proof checks"
        res.rejections.append({"k": k, "proposer": me.id, "bundle": dict(b), "cards": cards,
                               "checks": [failure_text(f, base + cards) for f in pc["fails"]],
                               "failed": [f["check"] for f in pc["fails"]]})
        for f in pc["fails"]:
            ban = _ban_from(f, b)
            bans.append(ban)
            alive &= ~banned_mask(ban)
        alive[idx] = False
    return res


# ---- into the weekly world, and into words -----------------------------------------------------------------------------

def world_deal(res):
    """The weekly world's week-0 deal for a 2-member table: {"pot": bool, "commits": [...]}. No agreement -> no pot, no commitments."""
    if not res.agreed or len(res.members) != 2:
        return {"pot": False, "commits": []}
    b, commits = res.bundle, []
    oth = {"A": "B", "B": "A"}
    for who in "AB":
        if b["stay"]:
            commits.append({"kind": "stay", "by": who, "to": oth[who], "type": None, "from": 0, "until": b["stay"], "breached": 0})
        if b["requests"] == "mutual":
            commits.append({"kind": "requests", "by": who, "to": oth[who], "type": "stay_home", "from": 0, "until": STAY_WEEKS, "breached": 0})
    return {"pot": True, "commits": commits}


def living_cards(base, res):
    """Cards the household lives under: the base rules plus the agreement's cards (just the base rules when there is no pot)."""
    return list(base) + (list(res.cards) if res.agreed else [])


def describe(res):
    """Plain-English lines of a negotiation outcome."""
    if not res.agreed:
        why = "ran out of proposals" if res.status == "deadline" else "ran out of bundles anyone would propose"
        return [f"No agreement ({why}): {', '.join(res.members)} keep their own holdings and share no pot."]
    lines = [f"Agreed at proposal {next(p['k'] for p in res.proposals if p['outcome'] == 'agreed') + 1} of {DEADLINE}, made by "
             f"{next(p['proposer'] for p in res.proposals if p['outcome'] == 'agreed')}:"]
    seen = []
    for c in res.cards:
        if c.gloss not in seen:
            seen.append(c.gloss)
    return lines + [f"- {g}" for g in seen]


# =====================================================================================================================
# Negotiation v2 (docs/results/negotiation-v2-prereg.md): exit floor, simulated outside options, 13-week reviews, three
# start arms, inertia. Everything above is v1 and is unchanged. Constants are the prereg's. Wording rule: agents feel
# nothing; "value" is a modeled gloss.
# =====================================================================================================================
ARMS = ("fair_default", "wants_first", "wants_fallback")
FINES = ("none", "some")                                    # seed v2.2 menu option: a fine (REQUEST_FINE money to the wronged partner) for breaking a request commitment; only where requests are agreed
BREACH = (1.0, 0.5, 0.0)                                    # share of the carry-out a stay breach forfeits (only with a stay)
# The fair default (post-fix 2026-11-10, author's choice "1" on the pot): one shared pot, open use, equal exit split, no commitments,
# unanimous change. The earlier default (fixed contribution, needs-only use, taking forbidden) imposed the reading the author rejected.
FAIR_DEFAULT = {"contribution": "none", "use": "any_use", "taking": "allowed", "change": "unanimous",
                "exit": "equal_split", "stay": 0, "requests": "none", "breach": 1.0, "fine": "none"}
FAIR_DEFAULT_V1 = {"contribution": "fixed", "use": "needs_only", "taking": "forbidden", "change": "unanimous",
                   "exit": "equal_split", "stay": 0, "requests": "none", "breach": 1.0, "fine": "none"}   # SUPERSEDED 2026-11-10; kept for the record
FLOOR_WEEKS = 13
FLOOR_LIVING = HD.DEFAULT.living_cost                      # the hedonic model's one consumption-as-need: 2.0 per week
FLOOR = FLOOR_WEEKS * FLOOR_LIVING                         # 26 money units (ASSUMED, constant)
EXIT_TAKE = {"equal_split": 50, "proportional": 100, "forfeit": 0}
START_HOLDINGS = (10, 45)                                   # (private money, what each puts into the one shared pot) at week 0
OUT_WEEKS = 26
FORWARD_WEEKS = 26
REVIEW_EVERY = 13
DEADLINE_REVIEW = 6
TERM_SCALE = 0.2
SALIENCE_TAU = 0.30
V1_TERMS = TERM_NAMES                                       # the seven v1 terms (inertia is measured over these)
STATS = {"rollouts": 0, "hits": 0, "rollout_weeks": 0}


def default_key():
    return key(FAIR_DEFAULT)


def bundles_v2(allow_stay=True, allow_requests=True, allow_roles=False, fines=False):
    """v1's menu with the breach-cost term (1.0 / 0.5 / 0.0) added where a stay is agreed; otherwise breach is inert (1.0).
    allow_roles / fines (household fixes, default off): the roles term and opt-in fines on any chosen commitment."""
    if allow_roles or fines:
        out = []
        for b in bundles(allow_stay, allow_requests):
            for ro in (ROLES if allow_roles else ("none",)):
                committed = b["stay"] or b["requests"] == "mutual" or ro in ("earner_planner", "swapped")
                for f in (BREACH if b["stay"] else (1.0,)):
                    for fine in ((FIX_FINES if fines else FINES) if (committed if fines else b["requests"] == "mutual") else ("none",)):
                        x = dict(b, breach=f, fine=fine)
                        if allow_roles:
                            x["roles"] = ro
                        out.append(x)
        return out
    out = []
    for b in bundles(allow_stay, allow_requests):
        for f in (BREACH if b["stay"] else (1.0,)):
            for fine in (FINES if b["requests"] == "mutual" else ("none",)):
                out.append(dict(b, breach=f, fine=fine))
    return out


def breach_values(p):
    w = p.weights
    x = 0.30 * w["security"] + 0.20 * w["togetherness"] - 0.40 * w["autonomy"] - 0.10 * w["other_connections"]
    return {f: (f - 0.5) * x for f in BREACH}


def fine_values(p):
    """Value of a fine for breaking a request commitment (ASSUMED proxy, same sign structure as the breach cost: members who value
    security and togetherness like it, members who value autonomy do not)."""
    w = p.weights
    x = 0.30 * w["security"] + 0.20 * w["togetherness"] - 0.40 * w["autonomy"] - 0.10 * w["other_connections"]
    return {"none": 0.0, "some": 0.5 * x, "big": 1.0 * x}


def role_values(p, low=False):
    """Value of the roles term (seed v2.3; ASSUMED proxy): members who value togetherness and security like specializing, members who
    value autonomy less so. Partner A is the higher earner, so the earner_planner split fits the incomes slightly better."""
    w = p.weights
    x = 0.15 * w["togetherness"] + 0.10 * w["security"] - 0.15 * w["autonomy"] + 0.05
    return {"none": 0.0, "earner_planner": x + 0.02, "swapped": x - 0.02, "shared": 0.5 * x}


_TV = {}


def term_sum(p, low, b):
    tk = (p.id, low, tuple(sorted(p.weights.items())), p.risk_tolerance, tuple(p.tags))     # term_values reads only these
    tv = _TV.get(tk)
    if tv is None:
        tv = _TV[tk] = term_values(p, low)
    base = (sum(tv[t][b[t]] for t in TERM_NAMES) + (breach_values(p)[b["breach"]] if b["stay"] else 0.0)
            + (fine_values(p)[b.get("fine", "none")] if b["requests"] == "mutual" else 0.0))
    if "roles" in b or (b.get("fine", "none") != "none" and b["requests"] != "mutual"):     # household fixes only
        base += role_values(p, low)[b.get("roles", "none")]
        if b["requests"] != "mutual":
            base += fine_values(p)[b.get("fine", "none")]
    return base


_DCACHE = {}


def deltas(p, low, blist, ref, ukey):
    """TERM_SCALE x (term_sum(b) - term_sum(ref)) for every bundle (array)."""
    ck = (p.id, low, ukey, key(ref), ref.get("breach"), ref.get("fine", "none"), ref.get("roles"))
    if ck not in _DCACHE:
        r = term_sum(p, low, ref)
        _DCACHE[ck] = TERM_SCALE * np.array([term_sum(p, low, b) - r for b in blist])
    return _DCACHE[ck]


def salient(p, low=False):
    """Terms the persona cares about: spread of raw term values at least SALIENCE_TAU (before any run, from the weights)."""
    out = {t for t, d in _raw(p, low).items() if max(d.values()) - min(d.values()) >= SALIENCE_TAU}
    return out


def inertia(bundle):
    """Share of the 7 v1 terms identical to the fair default, and the per-term identity."""
    same = {t: bundle[t] == FAIR_DEFAULT[t] for t in V1_TERMS}
    return sum(same.values()) / len(V1_TERMS), same


# ---- the exit floor ---------------------------------------------------------------------------------------------------

def retained(b, money, share, path="exit", put=None):
    """Own resources a member leaves with under the bundle: own money + what the exit term lets them carry out of the pot.
    share = the member's equal half of the pot (the whole pot is 2 x share); put = what they put in (default: share)."""
    take = EXIT_TAKE[b["exit"]]
    if path == "breach":
        take = min(take, int(round(100 * (1 - b["breach"]))))
    base = min(2 * share, share if put is None else put) if b["exit"] == "proportional" else 2 * share
    return money + base * take // 100


def floor_check(b, holdings, floor=FLOOR, current=None):
    """-> {"ok", "fails": [{role, path, retained, needed}]}. holdings: {role: (money, equal share of the pot[, put in])}. Needed =
    min(floor, the most generous exit would carry), so a review cannot dead-lock once holdings have fallen below the floor. At a
    review (current = the terms now in force) a change may not leave a member below the floor or further below it than the current
    terms already do (amendment 1)."""
    fails = []
    for role, h in holdings.items():
        money, share = h[0], h[1]
        put = h[2] if len(h) > 2 else None
        base_needed = min(floor, money + share)
        for path in ["exit"] + (["breach"] if b["stay"] else []):
            needed = base_needed
            if current is not None:
                needed = min(needed, retained(current, money, share, path if current["stay"] else "exit", put))
            r = retained(b, money, share, path, put)
            if r < needed:
                fails.append({"role": role, "path": path, "retained": r, "needed": needed})
    return {"ok": not fails, "fails": fails}


_V1READ = None


def v1_flag(b, base):
    """Would v1's exit-within-k check have failed this deal? Its own cards (a forfeit-like exit) or a stay commitment read as a rule
    that blocks leaving within k months (the v1 reading of a bind; ASSUMED). Floor-clearing deals that fail are FLAGGED, not blocked."""
    cards = compile_bundle(b, ["a", "b"])
    if not proof_check(base + cards)["ok"]:
        return True
    if b["stay"]:
        read = _card("V1-stay-reading", "must_not", "leave", [("months_in", "lt", 12)], "A stay commitment blocks leaving for its term.", "v1 reading")
        return any(f["check"] == "e_exit_within_k" for f in proof_check(base + cards + [read])["fails"])
    return False


# ---- simulated outside options and in-pot baselines -----------------------------------------------------------------------

def wellbeing(outcomes, role, persona=None):
    """Persona evaluation of a stretch of weeks: mean of pleasure - offsettable suffering - non-offsettable suffering. Under the
    formation-check flag (FixConfig.decide_on == "pleasure") it is the member's own mean clipped pleasure instead. Under
    decide_on == "weighted" (H39) it is pleasure - w x (both kinds of suffering), w the persona's own suffering weight
    (makers.suffering_weight; docs/notes/decision-weights-research.md)."""
    xs = [o["hedonic"][role] for o in outcomes]
    fx = HD.active_fixes()
    if fx is not None and fx.agent_values == "hybrid":      # the hybrid's one declared yardstick (mar.hybrid.score)
        from . import hybrid as _HY
        return _HY.score(outcomes, role, persona)
    if fx is not None and fx.decide_on == "pleasure":
        return sum(h["pleasure"] for h in xs) / len(xs)
    if fx is not None and fx.decide_on == "weighted":
        from . import makers as _MAKERS
        wt = 1.0 if persona is None else _MAKERS.suffering_weight(persona)   # no persona (an observer record): the plain net score
        return sum(h["pleasure"] - wt * (h["s_off"] + h["s_non"]) for h in xs) / len(xs)
    return sum(h["pleasure"] - h["s_off"] - h["s_non"] for h in xs) / len(xs)


def decide_weeks(default):
    """The rollout window a decision uses: `default` (26) unless the formation-check flag sets FixConfig.decide_weeks, which then
    overrides every decision window (the multiverse patches the defaults below, so they stay as they were)."""
    fx = HD.active_fixes()
    return (fx.decide_weeks or default) if fx is not None else default


_RC = {}
_SOLO_CARDS = []


def _solo_cards():
    if not _SOLO_CARDS:
        _SOLO_CARDS.extend(H.load_variant("author_seed_v2_bindable"))
    return _SOLO_CARDS


def alone_value(p, role, holdings, seed, mode, hed=None, weeks=OUT_WEEKS, cx=None):
    """Persona evaluation of a short rollout of living alone (mode "alone") or with Friend C (mode "friend") with the given holdings.
    Cached by (persona, role, holdings, seed, mode, hedonic-state signature); deterministic given the key."""
    sig = None if hed is None else (round(hed.B, 1), round(hed.N, 1))
    fk = HD.fix_key()
    if fk is not None and cx is not None:
        sig = (sig, round(cx["cf"], 1))
    ck = (p.id, role, int(holdings), seed, mode, weeks, sig) + ((fk,) if fk is not None else ())
    if ck in _RC:
        STATS["hits"] += 1
        return _RC[ck]
    w = H.WeeklyWorld(_solo_cards(), (p, p), seed, weeks, deal={"pot": False, "commits": []})
    for x in "AB":
        w.p[x]["in"], w.p[x]["money"] = False, int(holdings)
        w.pool, w.put = 0, {"A": 0, "B": 0}
    w.solo = mode
    if hed is not None:
        w.hed[role] = copy.deepcopy(hed)
    if cx is not None and w.fx is not None and w.fx.real_outside:    # fix 3: the outside rollout starts from current closeness to friends
        w.cx[role]["cf"] = cx["cf"]
    run = w.play()
    STATS["rollouts"] += 1
    STATS["rollout_weeks"] += weeks
    _RC[ck] = wellbeing(run.outcomes, role, p)
    if w.hed[role].parts_on:                    # observer layer: the rollout's parts, kept beside the value
        _RC_P[ck] = _OBS.rollout_parts(w.hed[role], 0)
    return _RC[ck]


_RC_P = {}


def _alone_key(p, role, holdings, seed, mode, hed=None, weeks=OUT_WEEKS, cx=None):
    """alone_value's cache key (the same computation, for reading the parts kept beside a cached value)."""
    sig = None if hed is None else (round(hed.B, 1), round(hed.N, 1))
    fk = HD.fix_key()
    if fk is not None and cx is not None:
        sig = (sig, round(cx["cf"], 1))
    return (p.id, role, int(holdings), seed, mode, weeks, sig) + ((fk,) if fk is not None else ())


def outside_parts(p, role, holdings, seed, hed=None, cx=None):
    """Observer layer: the parts of outside_value's two rollouts, {"alone": groups, "friend": groups} (None where not recorded)."""
    kw = {"weeks": decide_weeks(0)} if decide_weeks(0) else {}
    return {m: _RC_P.get(_alone_key(p, role, holdings, seed, m, hed, cx=cx, **kw)) for m in ("alone", "friend")}


def _recording(world=None):
    return HD.PARTS or (world is not None and getattr(world, "observer", None) is not None)


def outside_value(p, role, holdings, seed, hed=None, cx=None):
    """The member's real outside option: the better of living alone and living with Friend C, by its own evaluation.
    cx (fix 3, real_outside): the member's current closeness state, carried into the rollout. -> (value, {"alone": x, "friend": y})."""
    kw = {"weeks": decide_weeks(0)} if decide_weeks(0) else {}
    fx = HD.active_fixes()
    if fx is not None and fx.agent_values == "hybrid":      # K fresh futures per arrangement (mar.hybrid)
        from . import hybrid as _HY
        return _HY.outside_value(p, role, holdings, seed, hed, cx, kw.get("weeks"))
    d = {m: alone_value(p, role, holdings, seed, m, hed, cx=cx, **kw) for m in ("alone", "friend")}
    return max(d.values()), d


_PC = {}


def pot_baseline(pa, pb, seed, base, weeks=OUT_WEEKS):
    """Persona evaluation of living together under the fair default for 26 weeks: {"A": x, "B": y}. Cached by (pair, seed)."""
    weeks = decide_weeks(weeks)
    ck = (pa.id, pb.id, seed, weeks, tuple(sorted(c.id for c in base)))
    if HD.fix_key() is not None:
        ck = ck + (HD.fix_key(),)
    fx = HD.active_fixes()
    if ck not in _PC and fx is not None and fx.agent_values == "hybrid":
        from . import hybrid as _HY
        cards = list(base) + compile_bundle(FAIR_DEFAULT, [pa.id, pb.id])
        _PC[ck] = _HY.fresh_value(lambda: H.WeeklyWorld(cards, (pa, pb), seed, weeks, deal=deal_from_bundle(FAIR_DEFAULT),
                                                        breach_forfeit=FAIR_DEFAULT["breach"]), seed, weeks)
    if ck not in _PC:
        cards = list(base) + compile_bundle(FAIR_DEFAULT, [pa.id, pb.id])
        wd = H.WeeklyWorld(cards, (pa, pb), seed, weeks, deal=deal_from_bundle(FAIR_DEFAULT), breach_forfeit=FAIR_DEFAULT["breach"])
        run = wd.play()
        STATS["rollouts"] += 1
        STATS["rollout_weeks"] += weeks
        _PC[ck] = {r: wellbeing(run.outcomes, r, q) for r, q in zip("AB", (pa, pb))}
        if wd.hed["A"].parts_on:
            _PC_P[ck] = {r: _OBS.rollout_parts(wd.hed[r], 0) for r in "AB"}
    _LAST_KEY["pot"] = ck
    return _PC[ck]


_PC_P, _BC_P, _LAST_KEY = {}, {}, {}


def deal_from_bundle(b):
    """The weekly world's deal for a 2-member bundle (like world_deal, from a bundle rather than a Negotiation)."""
    commits, oth = [], {"A": "B", "B": "A"}
    for who in "AB":
        if b["stay"]:
            commits.append({"kind": "stay", "by": who, "to": oth[who], "type": None, "from": 0, "until": b["stay"], "breached": 0})
        if b["requests"] == "mutual":
            commits.append({"kind": "requests", "by": who, "to": oth[who], "type": "stay_home", "from": 0, "until": STAY_WEEKS, "breached": 0})
    return {"pot": True, "commits": commits}


def forward_values(world, w, last, weeks=FORWARD_WEEKS, parts=None):
    """Persona evaluation of the next 26 weeks of the live household under its current terms (a copy of the world plays them).
    parts (observer layer): a dict that receives each member's rollout parts, when the world's Hedonic records them."""
    weeks = decide_weeks(weeks)
    if world.fx is not None and world.fx.agent_values == "hybrid":     # K sampled futures, not the lived world's own (mar.hybrid)
        from . import hybrid as _HY
        return _HY.forward_values(world, w, last, weeks)
    c = played_copy(world, w, last, weeks)
    STATS["rollouts"] += 1                      # counted as asked for, also when forward_memo serves the copy (counters stay as they were)
    STATS["rollout_weeks"] += weeks
    if parts is not None:
        for r in "AB":
            parts[r] = _OBS.rollout_parts(c.hed[r], 0)
    return {r: wellbeing(c.run.outcomes, r, world.personas[r]) for r in "AB"}


_FWD = None          # forward_memo's store while one is open: [(world, w, weeks, fx, last, played copy)]; None = off


@contextlib.contextmanager
def forward_memo():
    """Within the block, a rollout of the same world from the same week, for as many weeks, under an equal FixConfig and an equal `last`
    is played once and its copy reused (docs/notes/performance.md). Open it only around calls that do not change the world between them:
    the stay lens and the reading that follows it (scripts/h38_pairing_run.py play). A rollout is deterministic given those inputs (the
    copy carries every random stream), so the reused copy is the one a second rollout would play."""
    global _FWD
    from . import hybrid as _HY
    prev, _FWD = _FWD, []
    _HY._MEMO.clear()                           # the hybrid's forecasts, memoized the same way (mar.hybrid.forward_values)
    try:
        yield
    finally:
        _FWD = prev
        _HY._MEMO.clear()


def played_copy(world, w, last, weeks, fx=None):
    """A copy of the world (no hook, a fresh run log: the rollout reads only the weeks it plays) that has played weeks w .. w+weeks-1
    from `last`. fx: the FixConfig the copy plays under (None = the world's own)."""
    use = world.fx if fx is None else fx
    if _FWD is not None:
        for wd, w0, n, f, lt0, c in _FWD:
            if wd is world and w0 == w and n == weeks and f == use and lt0 == last:
                return c
    hook, run = world.hook, world.run
    world.hook, world.run = None, H.Run()
    try:
        c = copy.deepcopy(world)
    finally:
        world.hook, world.run = hook, run
    if fx is not None:
        c.fx = fx
    lt = last
    for x in range(w, w + weeks):
        lt = {"busy": c.step_week(x, lt)}
    if _FWD is not None:
        _FWD.append((world, w, weeks, use, copy.deepcopy(last), c))
    return c


# ---- the v2 protocol -------------------------------------------------------------------------------------------------------

@dataclass
class Result2:
    members: list
    arm: str
    seed: int
    week: int
    status: str                   # "agreed" | "stood" (terms unchanged: the default at week 0, current terms at a review) | "deadline" | "no_bundle" | "no_pot"
    bundle: dict | None
    changed: bool = False
    proposals: list = field(default_factory=list)
    floor_blocks: list = field(default_factory=list)   # all-accepted proposals the floor blocked
    rejections: list = field(default_factory=list)     # proof-filter rejections
    cards: list | None = None
    stated: dict = field(default_factory=dict)         # member -> the ideal bundle (wants arms) stated before any proposal
    cared: dict = field(default_factory=dict)
    outside: dict = field(default_factory=dict)
    outside_detail: dict = field(default_factory=dict)
    baseline: dict = field(default_factory=dict)
    flagged: bool = False
    renewed: bool | None = None

    @property
    def pot(self):
        return self.bundle is not None and self.status in ("agreed", "stood")

    @property
    def agreed(self):
        return self.pot


def trust_penalty(t):
    """How much less a member values the current terms at a review when their trust in the other is t (0 at or above H.TRUST["full"])."""
    return H.TRUST["review_penalty"] * max(0.0, H.TRUST["full"] - t) / H.TRUST["full"]


def _ids_key(b):
    return key(b) + (b["breach"], b.get("fine", "none")) + ((b["roles"],) if "roles" in b else ())


def negotiate_v2(personas, arm, seed, *, base, W, O, ref=None, status_quo=None, holdings=None, floor=True, review=False, week=0,
                 deadline=None, roles=("A", "B"), trust=None, only=None, detail=False):
    """One negotiation round of v2. personas: 2 Persona; W: {persona id: in-pot value}; O: {persona id: outside option}.
    ref: the bundle U is measured against (default; at a review the current terms). status_quo: the bundle that stands if
    nothing is agreed (the fair default at week 0 in FAIR_DEFAULT; the current terms at a review); None means no agreement = no pot.
    trust (seed v2.2): {persona id: that member's trust in the other, in [0, 1]} from the live world, or None (no effect). Lower trust
    (a) lowers the member's value of the CURRENT terms at a review (so they are readier to change them), and (b) below
    H.TRUST["commit_min"] the member neither proposes nor accepts a NEW commitment (stay or requests). Constants ASSUMED."""
    ids = [p.id for p in personas]
    n = len(personas)
    deadline = deadline or (DEADLINE_REVIEW if review else DEADLINE)
    menu = menu_of(base)
    fx = HD.active_fixes()
    if fx and (fx.fines or menu.get("roles")):
        blist = bundles_v2(menu["stay"], menu["requests"], bool(menu.get("roles")), bool(fx.fines))
        ukey = (menu["stay"], menu["requests"], bool(menu.get("roles")), bool(fx.fines))
    else:
        blist = bundles_v2(menu["stay"], menu["requests"])
        ukey = (menu["stay"], menu["requests"])
    ref = ref or FAIR_DEFAULT
    if "roles" in blist[0]:          # seed v2.3 menu: bundles carry a roles term; a status quo without one has none
        ref = dict(ref, roles=ref.get("roles", "none"))
        status_quo = dict(status_quo, roles=status_quo.get("roles", "none")) if status_quo is not None else None
    holdings = holdings or {r: START_HOLDINGS for r in roles}
    keys = [_ids_key(b) for b in blist]
    kindex = {k: i for i, k in enumerate(keys)}
    U = {p.id: W[p.id] + deltas(p, roles[i] != "A", blist, ref, ukey) for i, p in enumerate(personas)}
    sq = kindex[_ids_key(status_quo)] if status_quo is not None else None
    cm_new = np.array([bool(b["stay"]) or b["requests"] == "mutual" for b in blist])
    if sq is not None:
        cm_new[sq] = False                              # commitments already standing are not "new"
    no_commit = {pid: bool(trust) and trust.get(pid, 1.0) < H.TRUST["commit_min"] for pid in ids}
    if trust and sq is not None and review:
        for pid in ids:
            U[pid][sq] -= trust_penalty(trust.get(pid, 1.0))
    bar = {pid: max(O[pid], float(U[pid][sq])) if sq is not None else O[pid] for pid in ids}
    res = Result2(ids, arm, seed, week, "deadline", None, outside=dict(O), baseline=dict(W))
    mask = np.ones(len(blist), dtype=bool)
    stated_arm = (not review) and arm in ("wants_first", "wants_fallback")
    if stated_arm:
        for i, p in enumerate(personas):               # stated wants, before any proposal: the member's own ideal over the whole menu
            ok = U[p.id] > O[p.id]
            res.stated[p.id] = dict(blist[int(np.argmax(np.where(ok, np.round(U[p.id], 9), -np.inf)))]) if ok.any() else None
    if not review and arm == "wants_fallback":
        res.cared = {p.id: sorted(salient(p, i > 0), key=TERM_NAMES.index) for i, p in enumerate(personas)}
        allowed = {t: {FAIR_DEFAULT[t]} for t in TERM_NAMES}
        for p in personas:
            if res.stated.get(p.id):
                for t in res.cared[p.id]:
                    allowed[t].add(res.stated[p.id][t])
        stay_open = any("stay" in res.cared[p.id] for p in personas)
        mask = np.array([all(b[t] in allowed[t] for t in TERM_NAMES) and (stay_open or not b["stay"]) and (b["breach"] == 1.0 or b["stay"]) and b["fine"] == "none"
                         for b in blist])
        # terms nobody cares about are fixed at the default (their allowed set is just the default)
    if only is not None:      # exit fallback F5 (prenup): bargain over the terms in `only`; every other term stays at the fair default
        mask = mask & np.array([all(b[t] == v for t, v in FAIR_DEFAULT.items() if t not in only) and b.get("roles", "none") == "none"
                                for b in blist])
    order = list(range(n))
    random.Random(f"{seed}|{week}|{','.join(ids)}").shuffle(order)
    alive = np.ones(len(blist), dtype=bool)
    passes = 0
    for k in range(deadline):
        c = k / (deadline - 1)
        i = order[k % n]
        me = personas[i]
        lam = 0.0 if (stated_arm and k < n) else LAMBDA0[me.negotiation_style] + (LAMBDA_END - LAMBDA0[me.negotiation_style]) * c
        score = U[me.id].copy()
        for j, q in enumerate(personas):
            if j != i:
                score = score + lam * np.minimum(0.0, U[q.id] - bar[q.id])
        ok = alive & mask & (U[me.id] > bar[me.id]) & (~cm_new if no_commit[me.id] else True)
        if not ok.any():
            if sq is None:
                res.status = "no_bundle"
                break
            res.proposals.append({"k": k, "proposer": me.id, "bundle": None, "accepted_by": [], "rejected_by": [], "outcome": "pass"})
            passes += 1
            if passes >= n:
                break
            continue
        passes = 0
        idx = int(np.argmax(np.where(ok, np.round(score, 9), -np.inf)))
        if fx and fx.nash_terms:
            # fix 3: among bundles every member values above their bar, propose the Nash bargaining point with disagreement point O
            both = ok.copy()
            for q in personas:
                both &= U[q.id] > bar[q.id]
            if both.any():
                nash = np.zeros(len(blist))
                for j, q in enumerate(personas):
                    a_q = fx.nash_alpha if j == i else (1.0 - fx.nash_alpha) / max(1, n - 1)
                    nash = nash + a_q * np.log(np.maximum(U[q.id] - O[q.id], 1e-9))
                idx = int(np.argmax(np.where(both, np.round(nash, 9), -np.inf)))
        b = blist[idx]
        acc, rej = [me.id], []
        for j, q in enumerate(personas):
            if j != i:
                theta = THETA0[q.negotiation_style] * (1 - c)
                (acc if U[q.id][idx] > bar[q.id] + theta and not (no_commit[q.id] and cm_new[idx]) else rej).append(q.id)
        prop = {"k": k, "proposer": me.id, "bundle": dict(b), "accepted_by": acc, "rejected_by": rej, "outcome": "refused" if rej else "all accept"}
        if detail:                      # observer layer (D6): each member's value of the offer, bar and acceptance threshold
            prop["detail"] = _round_detail(personas, roles, U, bar, idx, b, ref, c, i)
        res.proposals.append(prop)
        if rej:
            continue
        if floor:
            fc = floor_check(b, holdings, current=status_quo if review else None)
            if not fc["ok"]:
                prop["outcome"] = "blocked by the floor"
                res.floor_blocks.append({"k": k, "proposer": me.id, "bundle": dict(b), "fails": fc["fails"]})
                for f in fc["fails"]:
                    ban = {("exit", b["exit"])} | ({("stay", b["stay"]), ("breach", b["breach"])} if f["path"] == "breach" else set())
                    alive &= ~np.array([all(x[t] == v for t, v in ban) for x in blist])
                alive[idx] = False
                continue
        cards = compile_bundle(b, ids)
        pc = proof_check(base + cards)
        if pc["ok"]:
            prop["outcome"] = "agreed"
            res.status, res.bundle, res.cards, res.changed = "agreed", dict(b), cards, True
            res.flagged = v1_flag(b, base)
            return res
        prop["outcome"] = "rejected by the proof checks"
        res.rejections.append({"k": k, "proposer": me.id, "bundle": dict(b), "checks": [failure_text(f, base + cards) for f in pc["fails"]],
                               "failed": [f["check"] for f in pc["fails"]]})
        for f in pc["fails"]:
            ban = _ban_from(f, b)
            alive &= ~np.array([all(x[t] == v for t, v in ban) for x in blist])
        alive[idx] = False
    if sq is not None and status_quo is not None:
        sqb = blist[sq]
        if review or all(float(U[pid][sq]) > O[pid] for pid in ids):
            res.status, res.bundle = "stood", dict(sqb)
            res.cards = compile_bundle(sqb, ids)
            res.flagged = v1_flag(sqb, base)
        else:
            res.status = "no_pot"           # the default stood but it is worse than someone's outside option
    return res


# ---- observer layer (src/mar/observe.py; docs/notes/observer-schema.md): records of the harness's decisions, built only while recording

def _reading_rec(kind, w, W, O, det, wparts, oparts, **kw):
    """A formation, retry, reading or review decision as an observer `reading` row: per member the household value W (a rollout of the
    household), the outside value O (the better of alone and with Friend C), the margin W - O, and both values' parts (rollout means of
    observe.groups; None where the rollout's parts were not recorded, e.g. a value read from a cache filled before recording began)."""
    out = {"t": "reading", "kind": kind, "w": w, "m": {}}
    for r in "AB":
        o_parts = (oparts or {}).get(r) or {}
        d = (det or {}).get(r) if det else None
        mode = (kw.get("modes") or {}).get(r) or (apart_mode(d) if d else None)
        if mode is None and o_parts.get("alone") is not None and o_parts.get("friend") is not None:
            mode = "friend" if sum(o_parts["friend"].values()) > sum(o_parts["alone"].values()) else "alone"
        out["m"][r] = {"W": W[r], "O": O[r], "margin": W[r] - O[r], "O_alone_friend": d, "mode": mode,
                       "W_parts": (wparts or {}).get(r), "O_parts": o_parts.get(mode) if mode else None}
    out.update(kw)
    return out


def _neg_rec(w, kind, prop, personas):
    rec = {"t": "negotiation", "w": w, "kind": kind, "k": prop["k"], "proposer": prop["proposer"], "bundle": prop.get("bundle"),
           "accepted_by": prop["accepted_by"], "rejected_by": prop["rejected_by"], "outcome": prop["outcome"]}
    if "detail" in prop:
        rec.update(prop["detail"])
    return rec


def _round_detail(personas, roles, U, bar, idx, b, ref, c, i):
    """D6: per member the offer's value U, the bar (max of outside option and the status quo), the acceptance threshold theta, and the
    per-term value differences against `ref`; the term with the largest gap between the members' differences."""
    per, tdiff = {}, {}
    for j, p in enumerate(personas):
        low = roles[j] != "A"
        tv = term_values(p, low)
        tdiff[p.id] = {t: TERM_SCALE * (tv[t][b[t]] - tv[t][ref[t]]) for t in TERM_NAMES if t in b and t in ref and ref[t] in tv[t]}
        per[p.id] = {"U": float(U[p.id][idx]), "bar": float(bar[p.id]),
                     "theta": None if j == i else float(THETA0[p.negotiation_style] * (1 - c)), "terms": tdiff[p.id]}
    gap = None
    if len(personas) == 2:
        a, bb = (p.id for p in personas)
        gaps = {t: abs(tdiff[a].get(t, 0.0) - tdiff[bb].get(t, 0.0)) for t in TERM_NAMES}
        gap = max(gaps, key=gaps.get) if any(gaps.values()) else None
    return {"members": per, "gap_term": gap}


# ---- household fixes: shared helpers (docs/results/household-fixes-design.md) ------------------------------------------------------

def _cx(world, r):
    """The member's closeness state for the outside rollout (fix 3, real_outside), or None."""
    return world.cx[r] if (world.fx is not None and world.fx.real_outside and world.fx.contact) else None


def bar_reading(world, sq, out, modes=None):
    """Fix 3, bar_leave: one reading of the ADR 0018 bar. sq: {role: status-quo value (minus the trust penalty)}; out: {role: outside
    option}. A member whose outside option beats staying by more than leave_margin in bar_runs readings in a row gets `leave` on its menu."""
    fx = world.fx
    runs = getattr(world, "bar_runs", None)
    if runs is None:
        runs = world.bar_runs = {"A": 0, "B": 0}
    world.bar_log = getattr(world, "bar_log", [])
    if fx.agent_values == "hybrid":
        world.bar_gain = {r: out[r] - sq[r] for r in "AB"}     # the hybrid's leave value reads it (mar.hybrid.leave_value)
        world.hyb_last, world.hyb_due = getattr(world, "cur_reading", None) or getattr(world, "hyb_last", -99), False
    for r in "AB":
        better = out[r] > sq[r] + fx.leave_margin
        runs[r] = runs[r] + 1 if better else 0
        world.bar_out[r] = runs[r] >= fx.bar_runs
        if modes:
            world.bar_mode[r] = modes[r]          # a member who leaves on the bar goes to the alternative it compared (alone or with Friend C)
    world.bar_log.append({"sq": dict(sq), "out": dict(out), "bar_out": dict(world.bar_out)})


class BaselineLived:
    """The imposed baseline lived the same way as a negotiated household (docs/results/v2-retest-prereg-DRAFT.md). The baseline's cards
    are imposed; with decline=True (`baseline_may_decline`, the author: "yes pairs should be allowed to not form a househodl") a pair forms
    only if both members value living under the baseline (a 26-week rollout) above their outside option, else both live apart as a v2.2
    pair with no pot does and may form at a later 13-week reading. With bar_leave, a 13-week reading of the bar can put `leave` on a
    member's menu. decline=False and no fixes is the old imposed baseline, bit for bit."""

    def __init__(self, pa, pb, seed, cards, weeks=H.WEEKS, decline=True):
        self.pa, self.pb, self.seed, self.cards, self.decline = pa, pb, seed, list(cards), decline
        self.world = H.WeeklyWorld(self.cards, (pa, pb), seed, weeks)
        self.apart, self.log, self.retries = False, [], []
        fx = self.world.fx
        if fx is not None and fx.agent_values == "hybrid":
            self._hybrid_init(weeks)
            return
        if decline:
            W = baseline_value(pa, pb, seed, self.cards)
            O, det = {}, {}
            for r, p in zip("AB", (pa, pb)):
                O[r], det[r] = outside_value(p, r, START_HOLDINGS[0] + START_HOLDINGS[1], seed)
            self.week0 = {"W": W, "O": O}
            if _recording():
                _OBS.harness_record(None, self, _reading_rec("formation0", 0, W, O, det, _BC_P.get(_LAST_KEY.get("base")),
                                                             {r: outside_parts(p, r, START_HOLDINGS[0] + START_HOLDINGS[1], seed)
                                                              for r, p in zip("AB", (pa, pb))},
                                                             formed=not any(O[r] > W[r] for r in "AB")))
            if any(O[r] > W[r] for r in "AB"):
                self.apart = True
                self.world = H.WeeklyWorld(self.cards, (pa, pb), seed, weeks, deal={"pot": False, "commits": []})
                self.world.solo = {r: apart_mode(det[r]) for r in "AB"}
                for r in "AB":
                    self.world.p[r]["in"] = False

    def _hybrid_init(self, weeks):
        """The hybrid agent's week 0 (mar.hybrid.formation0): the bill term and formation chosen by simulation."""
        from . import hybrid as _HY
        formed, term, O, det, V = _HY.formation0(self)
        self.week0 = {"W": V[term], "O": O, "term": term, "formed": formed}
        self.trials = []
        if not formed or term == "lat":
            self.apart = True
            self.world = H.WeeklyWorld(self.cards, (self.pa, self.pb), self.seed, weeks, deal={"pot": False, "commits": []})
            self.world.solo = {r: apart_mode(det[r]) for r in "AB"}
            for r in "AB":
                self.world.p[r]["in"] = False
            if formed:                     # H41: living apart together chosen at week 0
                _HY.make_lat(self.world, self.world.solo)
        else:
            _HY.set_agreement(self.world, term)
            if self.world.fx.h41_trial:    # H41: a trial household, decided again at its end (hybrid.trial_reading)
                self.world.trial_end = self.world.fx.h41_trial
        self.world.fork_ok = True
        self.world.harness = True          # this harness runs the 13-week readings (hybrid.world_readings reads it; Amendment 3)

    def hybrid_week(self, w, last):
        """The hybrid's extra harness steps at the start of week w (not a 13-week mark): an early reading on distress."""
        from . import hybrid as _HY
        if _HY.due(self.world, w):
            self.world.cur_reading = w
            self.reading(w, last)
        elif _HY.lone_due(self.world, w):          # Amendment 4 (hybrid_lone): an early reading for a member alone in the household
            _HY.lone_reading(self, w, last)
        _HY.lone_apart(self)                       # Amendment 4: an emptied household's pair counts as apart (13-week retries)

    def retry(self, w, last):
        world = self.world
        if world.fx is not None and world.fx.agent_values == "hybrid":
            from . import hybrid as _HY
            return _HY.retry(self, w, last)
        O, modes = {}, {}
        for r, p in zip("AB", (self.pa, self.pb)):
            O[r], d = outside_value(p, r, world.p[r]["money"], self.seed, world.hed[r], cx=_cx(world, r))
            modes[r] = apart_mode(d)
        hyp = copy.deepcopy(world)
        hyp.hook = None
        _form_baseline(hyp, w)
        fp = {} if _recording(world) else None
        fwd = forward_values(hyp, w, last, parts=fp)
        formed = all(fwd[r] > O[r] for r in "AB")
        self.retries.append({"week": w, "formed": formed, "outside": dict(O), "baseline": dict(fwd)})
        if fp is not None:
            _OBS.harness_record(world, self, _reading_rec(
                "retry", w, fwd, O, None, fp,
                {r: outside_parts(p, r, world.p[r]["money"], self.seed, world.hed[r], cx=_cx(world, r)) for r, p in zip("AB", (self.pa, self.pb))},
                formed=formed, modes=modes))
        if formed:
            before = world.observer.balances() if world.observer is not None else None
            _form_baseline(world, w)
            if before is not None:
                world.observer.flow_diff(w, "formation", None, before)
            self.apart = False
            if world.fx:
                for r in "AB":
                    world.events.append((w, r, "formed"))
        else:
            world.solo = modes

    def reading(self, w, last):
        world = self.world
        fp = {} if _recording(world) else None
        fwd = forward_values(world, w, last, parts=fp)
        O, modes, op = {}, {}, {}
        for r, p in zip("AB", (self.pa, self.pb)):
            carry = world.p[r]["money"] + world.carry_out(r, 50)
            O[r], d = outside_value(p, r, carry, self.seed, world.hed[r], cx=_cx(world, r))
            O[r] -= _PAIR.exit_anticipation(world)      # H38 exit stigma (0 when the pairing switch is off)
            modes[r] = apart_mode(d)
            if fp is not None:
                op[r] = outside_parts(p, r, carry, self.seed, world.hed[r], cx=_cx(world, r))
        self.log.append({"week": w, "outside": dict(O), "baseline": dict(fwd)})
        if world.fx is not None and world.fx.agent_values == "hybrid":
            from . import hybrid as _HY
            world.cur_reading = w
            _HY.reading_audit(world, w, last, {r: fwd[r] - trust_penalty(world.trust[r]) for r in "AB"}, O,
                              {r: world.p[r]["money"] + world.carry_out(r, 50) for r in "AB"}, decide_weeks(FORWARD_WEEKS))
        bar_reading(world, {r: fwd[r] - trust_penalty(world.trust[r]) for r in "AB"}, O, modes)
        if fp is not None:
            _OBS.harness_record(world, self, _reading_rec(
                "reading", w, fwd, O, None, fp, op, modes=modes, trust_pen={r: trust_penalty(world.trust[r]) for r in "AB"},
                exit_anticipation=_PAIR.exit_anticipation(world), bar_out=dict(world.bar_out),
                bar_runs=dict(getattr(world, "bar_runs", {}) or {})))

    def play(self):
        world = self.world
        last = {"busy": {"A": False, "B": False}}
        bar = world.fx is not None and world.fx.bar_leave
        hyb = world.fx is not None and world.fx.agent_values == "hybrid"
        for w in range(world.weeks):
            if w and w % REVIEW_EVERY == 0:
                if self.apart and self.decline:
                    self.retry(w, last)
                elif bar and all(world.p[r]["in"] for r in "AB"):
                    self.reading(w, last)
                elif hyb and any(world.p[r]["in"] for r in "AB"):
                    from . import hybrid as _HY
                    _HY.return_reading(self, w, last)
            elif hyb:
                self.hybrid_week(w, last)
            if world.early_review:
                world.ladder_reviewed(w)
            last = {"busy": world.step_week(w, last)}
        world.run.final = {r: {**world.p[r], "pooled": world.pool, "put": world.put[r]} for r in "AB"}
        if world.mech:
            world.run.meta = world.commit_report()
        if world.fx:
            world.run.fix = world.fix_report()
        world.run.exits = list(world.exit_log)
        return world.run


_BC = {}


def baseline_value(pa, pb, seed, cards, weeks=OUT_WEEKS):
    """Persona evaluation of living together under imposed cards for 26 weeks: {"A": x, "B": y}. Cached."""
    weeks = decide_weeks(weeks)
    ck = (pa.id, pb.id, seed, weeks, tuple(sorted(c.id for c in cards)), HD.fix_key())
    fx = HD.active_fixes()
    if ck not in _BC and fx is not None and fx.agent_values == "hybrid":
        from . import hybrid as _HY
        _BC[ck] = _HY.fresh_value(lambda: H.WeeklyWorld(list(cards), (pa, pb), seed, weeks), seed, weeks)
    if ck not in _BC:
        wd = H.WeeklyWorld(list(cards), (pa, pb), seed, weeks)
        run = wd.play()
        STATS["rollouts"] += 1
        _BC[ck] = {r: wellbeing(run.outcomes, r, q) for r, q in zip("AB", (pa, pb))}
        if wd.hed["A"].parts_on:
            _BC_P[ck] = {r: _OBS.rollout_parts(wd.hed[r], 0) for r in "AB"}
    _LAST_KEY["base"] = ck
    return _BC[ck]


def _form_baseline(world, w):
    """Two partners living apart move in together under the imposed baseline cards: each puts min(POOL_SHARE, own money) in the pot."""
    pr = world.fx is not None and world.fx.pairing is not None
    for r in "AB":
        p = world.p[r]
        put = min(POOL_SHARE, int(p["money"]))
        p["money"] -= put
        world.pool += put
        world.put[r] += put
        if pr:                                  # H38 harness repair: a later formation records what each put in (exit fallback F4)
            world.money_in[r] += put
        p["in"], p["months_in"], p["weeks_out"] = True, 0, 0
    world.solo, world.pot = None, True
    world.pending = {"A": set(), "B": set()}
    if pr and _ITEMS.ACTIVE is not None and world.items is None:
        _ITEMS.init_world(world)                # ... and gets its items, as a week-0 pair does


# ---- a lived v2 household: week-0 negotiation, then reviews every 13 weeks -------------------------------------------------------

def week0(pa, pb, arm, seed, base, floor=True):
    """The week-0 negotiation of a pair. -> Result2. Outside options and the in-pot baseline come from rollouts (cached)."""
    W = pot_baseline(pa, pb, seed, base)
    O, det = {}, {}
    for r, p in zip("AB", (pa, pb)):
        v, d = outside_value(p, r, START_HOLDINGS[0] + START_HOLDINGS[1], seed)
        O[p.id], det[p.id] = v, d
    res = negotiate_v2([pa, pb], arm, seed, base=base, W={pa.id: W["A"], pb.id: W["B"]}, O=O, floor=floor,
                       status_quo=FAIR_DEFAULT if arm == "fair_default" else None, detail=_recording())
    res.outside_detail = det
    return res


def _apply_terms(world, base, bundle, w, ids, renew):
    """A review's outcome goes into the live world: new cards, the breach cost, and the commitments (stay only if renewed)."""
    cards = list(base) + compile_bundle(bundle, ids) + floor_cards(world.floor_amount)
    world.gate = H.PyGate(cards)
    world.cards = {c.id: c for c in cards}
    world.breach_forfeit = bundle["breach"]
    for c in world.commits:
        if c["kind"] == "stay":
            c["until"] = w + bundle["stay"] if (bundle["stay"] and renew) else min(c["until"], w)
        elif c["kind"] == "requests":
            c["until"] = w + STAY_WEEKS if bundle["requests"] == "mutual" else min(c["until"], w)
    have = {c["kind"] for c in world.commits if c["until"] > w}
    oth = {"A": "B", "B": "A"}
    for who in "AB":
        if bundle["stay"] and renew and "stay" not in have:
            world.commits.append({"kind": "stay", "by": who, "to": oth[who], "type": None, "from": w, "until": w + bundle["stay"], "breached": 0})
        if bundle["requests"] == "mutual" and "requests" not in have:
            world.commits.append({"kind": "requests", "by": who, "to": oth[who], "type": "stay_home", "from": w, "until": w + STAY_WEEKS, "breached": 0})


POOL_SHARE = START_HOLDINGS[1]      # what each member puts into the pooled share when a household forms later than week 0 (ASSUMED)


def apart_mode(detail):
    """The better of the two outside arrangements by the member's own rollouts ({"alone": x, "friend": y}); alone if unknown."""
    return "friend" if detail and detail["friend"] > detail["alone"] else "alone"


def form_pot(world, base, bundle, w, ids):
    """v2.1: two partners living apart move in together at week w under `bundle` (a shared household with a pot). Each puts
    min(POOL_SHARE, own money) into the one shared pot; the agreed cards and commitments (a stay runs from w) take effect."""
    for r in "AB":
        p = world.p[r]
        put = min(POOL_SHARE, int(p["money"]))
        p["money"] -= put
        world.pool += put
        world.put[r] += put
        p["in"], p["months_in"], p["weeks_out"] = True, 0, 0
    world.solo, world.pot = None, True
    world.pending = {"A": set(), "B": set()}
    cards = list(base) + compile_bundle(bundle, ids) + floor_cards(world.floor_amount)
    world.gate = H.PyGate(cards)
    world.cards = {c.id: c for c in cards}
    world.breach_forfeit = bundle["breach"]
    world.commits = [dict(c, **{"from": w, "until": w + (bundle["stay"] if c["kind"] == "stay" else STAY_WEEKS)})
                     for c in deal_from_bundle(bundle)["commits"]]


class Lived:
    """A household living under a negotiated bundle, with a review every REVIEW_EVERY weeks while both partners are in."""

    def __init__(self, pa, pb, arm, seed, base, res, floor=True, reviews=True, weeks=H.WEEKS, apart=False):
        """apart=True is negotiation v2.1: a failed negotiation means the partners live separately (and may retry at reviews).
        The default False is v2's behaviour (no pot, still sharing the house), kept so the v2 results stay reproducible."""
        self.pa, self.pb, self.arm, self.seed, self.base, self.floor, self.reviews = pa, pb, arm, seed, base, floor, reviews
        self.res, self.log = res, []
        self.bundle = dict(res.bundle) if res.pot else None
        cards = list(base) + (res.cards if res.pot else []) + floor_cards(FLOOR if floor else None)
        deal = deal_from_bundle(res.bundle) if res.pot else {"pot": False, "commits": []}
        self.world = H.WeeklyWorld(cards, (pa, pb), seed, weeks, deal=deal, breach_forfeit=res.bundle["breach"] if res.pot else 1.0)
        self.world.floor_amount = FLOOR if floor else None     # amendment 1: the floor also holds at the moment of leaving
        self.apart, self.retries = apart and not res.pot, []
        if _recording():
            W0 = getattr(res, "baseline", None) or {}
            O0 = getattr(res, "outside", None) or {}
            if W0 and O0:
                _OBS.harness_record(None, self, dict(_reading_rec(
                    "formation0", 0, {r: W0[p.id] for r, p in zip("AB", (pa, pb))}, {r: O0[p.id] for r, p in zip("AB", (pa, pb))},
                    {r: (getattr(res, "outside_detail", {}) or {}).get(p.id) for r, p in zip("AB", (pa, pb))},
                    _PC_P.get(_LAST_KEY.get("pot")),
                    {r: outside_parts(p, r, START_HOLDINGS[0] + START_HOLDINGS[1], seed) for r, p in zip("AB", (pa, pb))},
                    formed=bool(res.pot)), status=res.status, bundle=res.bundle))
                for pr in res.proposals:
                    _OBS.harness_record(None, self, _neg_rec(0, "formation0", pr, (pa, pb)))
        if self.apart:
            self.world.solo = {r: apart_mode(res.outside_detail.get(p.id)) for r, p in zip("AB", (pa, pb))}
            for r in "AB":                                       # v2.1: no agreement = no shared household
                self.world.p[r]["in"] = False

    def review(self, w, last):
        world, ps = self.world, (self.pa, self.pb)
        hold = {r: world.hold(r) for r in "AB"}
        rec_on = _recording(world)
        fp = {} if rec_on else None
        fwd = forward_values(world, w, last, parts=fp)
        cur = self.bundle
        O, det, op = {}, {}, {}
        for r, p in zip("AB", ps):
            money, share, put = hold[r]
            v, d = outside_value(p, r, retained(cur, money, share, "exit", put), self.seed, world.hed[r], cx=_cx(world, r))
            O[p.id], det[p.id] = v, d
            if rec_on:
                op[r] = outside_parts(p, r, retained(cur, money, share, "exit", put), self.seed, world.hed[r], cx=_cx(world, r))
        if world.fx and world.fx.bar_leave:
            bar_reading(world, {r: fwd[r] - trust_penalty(world.trust[r]) for r in "AB"}, {r: O[p.id] for r, p in zip("AB", ps)},
                        {r: apart_mode(det[p.id]) for r, p in zip("AB", ps)})
        res = negotiate_v2(list(ps), self.arm, self.seed, base=self.base, W={self.pa.id: fwd["A"], self.pb.id: fwd["B"]}, O=O,
                           ref=cur, status_quo=cur, holdings=hold, floor=self.floor, review=True, week=w, trust=self.trust_by_id(),
                           detail=rec_on)
        if rec_on:
            _OBS.harness_record(world, self, dict(_reading_rec(
                "review", w, fwd, {r: O[p.id] for r, p in zip("AB", ps)}, {r: det[p.id] for r, p in zip("AB", ps)}, fp, op,
                trust_pen={r: trust_penalty(world.trust[r]) for r in "AB"}, bar_out=dict(world.bar_out)),
                status=res.status, changed=res.changed, bundle=res.bundle))
            for pr in res.proposals:
                _OBS.harness_record(world, self, _neg_rec(w, "review", pr, ps))
        if world.fx:
            if res.changed:
                for r in "AB":
                    world.events.append((w, r, "terms"))        # a choice event: both members accepted new terms
            if res.status in ("agreed", "stood"):
                for r in "AB":
                    world._word(r, w)                          # trust_words: agreeing to terms is a word, not an action
        new = res.bundle if res.changed else cur
        renew = False
        if cur["stay"] or new["stay"]:
            if res.changed:
                renew = bool(new["stay"])
            else:     # every member votes on renewing the expiring stay by its own centered stay value
                renew = all(term_values(p, r == "B")["stay"][STAY_WEEKS] > 0 for r, p in zip("AB", ps))
        before = dict(cur)
        if res.changed or cur["stay"] or cur["requests"] == "mutual":
            _apply_terms(world, self.base, new, w, [self.pa.id, self.pb.id], renew)
        if res.changed:
            self.bundle = dict(new)
        self.log.append({"week": w, "changed": res.changed, "from": before, "to": dict(new), "stay_renewed": renew if (cur["stay"] or new["stay"]) else None,
                         "floor_blocks": len(res.floor_blocks), "rejections": len(res.rejections), "status": res.status,
                         "outside": res.outside, "baseline": res.baseline, "flagged": res.flagged})

    def trust_by_id(self):
        """{persona id: that member's trust in the other} from the live world."""
        return {self.pa.id: self.world.trust["A"], self.pb.id: self.world.trust["B"]}

    def accepts(self, r, new):
        """Does member r accept a change to `new`? Their own closed-form term values (ASSUMED proxy): strictly better than now,
        and (seed v2.2) a new commitment is accepted only while their trust in the other is at least H.TRUST["commit_min"]."""
        p = self.pa if r == "A" else self.pb
        adds = (new["stay"] and not self.bundle["stay"]) or (new["requests"] == "mutual" and self.bundle["requests"] != "mutual")
        if adds and self.world.trust[r] < H.TRUST["commit_min"]:
            return False
        return term_sum(p, r == "B", new) > term_sum(p, r == "B", self.bundle)

    def amend(self, proposer, new, w, accepts=None):
        """The negotiated change rule (term N4) as an action. proposer ("A" | "B") proposes the full bundle `new`; the others accept
        (accepts: {role: bool}, default each member's own closed-form value) per the change rule; the card gate decides whether the
        rule lets the change be made (unanimous: only with the others' consent; frozen: never); the new terms are recompiled and
        proof-checked (plus the exit floor and the base rules' menu) BEFORE anyone lives under them. -> a log dict with `outcome`:
        "amended" | "blocked by the change rule" | "not enough accepted" | "rejected by the proof checks" | "blocked by the floor"
        | "not allowed by the base rules" | "no pot"."""
        world, ids = self.world, [self.pa.id, self.pb.id]
        rec = {"week": w, "proposer": proposer, "from": dict(self.bundle) if self.bundle else None, "to": dict(new)}
        self.amendments = getattr(self, "amendments", [])
        self.amendments.append(rec)
        if self.bundle is None:
            rec["outcome"] = "no pot"
            return rec
        acc = {r: (r == proposer) or bool(accepts[r] if accepts and r in accepts else self.accepts(r, new)) for r in "AB"}
        rec["accepted"] = dict(acc)
        everyone_else = all(v for r, v in acc.items() if r != proposer)
        st = world.state(proposer, w)
        st["consented"] = int(everyone_else)
        ok, reasons = world.gate.check("partner", "amend", st)
        if not ok:
            rec["outcome"], rec["reasons"] = "blocked by the change rule", reasons
            return rec
        if not (everyone_else if self.bundle["change"] == "unanimous" else sum(acc.values()) * 2 > len(acc)):
            rec["outcome"] = "not enough accepted"
            return rec
        menu = menu_of(self.base)
        if (new["stay"] and not menu["stay"]) or (new["requests"] == "mutual" and not menu["requests"]):
            rec["outcome"] = "not allowed by the base rules"
            return rec
        hold = {r: world.hold(r) for r in "AB"}
        if self.floor and not floor_check(new, hold, current=self.bundle)["ok"]:
            rec["outcome"] = "blocked by the floor"
            return rec
        pc = proof_check(list(self.base) + compile_bundle(new, ids) + floor_cards(FLOOR if self.floor else None))
        if not pc["ok"]:
            rec["outcome"], rec["checks"] = "rejected by the proof checks", [c["check"] for c in pc["fails"]]
            return rec
        _apply_terms(world, self.base, new, w, ids, bool(new["stay"]))
        self.bundle = dict(new)
        rec["outcome"] = "amended"
        return rec

    def retry(self, w, last):
        """v2.1: partners who live apart try again (docs/results/negotiation-v2.1-prereg.md). Outside option = the better of alone and
        with Friend C over the next 26 weeks from the live state; in-pot value = the same evaluation of a copy of the live world turned
        into a household under the fair default. Agreement -> they move in together at this week under the agreed terms."""
        world, ps = self.world, (self.pa, self.pb)
        ids = [self.pa.id, self.pb.id]
        O, modes = {}, {}
        for r, p in zip("AB", ps):
            O[p.id], d = outside_value(p, r, world.p[r]["money"], self.seed, world.hed[r], cx=_cx(world, r))
            modes[r] = apart_mode(d)
        hyp = copy.deepcopy(world)
        hyp.hook = None
        form_pot(hyp, self.base, FAIR_DEFAULT, w, ids)
        rec_on = _recording(world)
        fp = {} if rec_on else None
        fwd = forward_values(hyp, w, last, parts=fp)
        hold = {r: hyp.hold(r) for r in "AB"}
        res = negotiate_v2(list(ps), self.arm, self.seed, base=self.base, W={self.pa.id: fwd["A"], self.pb.id: fwd["B"]}, O=O,
                           ref=FAIR_DEFAULT, status_quo=None, holdings=hold, floor=self.floor, review=True, week=w, trust=self.trust_by_id(),
                           detail=rec_on)
        if rec_on:
            _OBS.harness_record(world, self, dict(_reading_rec(
                "retry", w, fwd, {r: O[p.id] for r, p in zip("AB", ps)}, None, fp,
                {r: outside_parts(p, r, world.p[r]["money"], self.seed, world.hed[r], cx=_cx(world, r)) for r, p in zip("AB", ps)},
                formed=bool(res.pot), modes=modes), status=res.status, bundle=res.bundle))
            for pr in res.proposals:
                _OBS.harness_record(world, self, _neg_rec(w, "retry", pr, ps))
        self.retries.append({"week": w, "formed": res.pot, "status": res.status, "bundle": dict(res.bundle) if res.pot else None,
                             "floor_blocks": len(res.floor_blocks), "rejections": len(res.rejections), "outside": dict(O),
                             "baseline": {self.pa.id: fwd["A"], self.pb.id: fwd["B"]}, "modes": dict(modes)})
        if res.pot:
            before = world.observer.balances() if world.observer is not None else None
            form_pot(world, self.base, res.bundle, w, ids)
            if before is not None:
                world.observer.flow_diff(w, "formation", None, before)
            self.bundle, self.apart = dict(res.bundle), False
            if world.fx:
                for r in "AB":
                    world.events.append((w, r, "formed"))
        else:
            world.solo = modes

    def play(self):
        world = self.world
        last = {"busy": {"A": False, "B": False}}
        for w in range(world.weeks):
            if self.reviews and self.apart and w and w % REVIEW_EVERY == 0:
                self.retry(w, last)
            elif self.reviews and self.bundle is not None and w and w % REVIEW_EVERY == 0 and all(world.p[r]["in"] for r in "AB"):
                self.review(w, last)
                if world.early_review:
                    world.ladder_reviewed(w)
            elif world.early_review:          # seed v2.3 ladders: an early renegotiation (household fixes only)
                if self.reviews and self.bundle is not None and all(world.p[r]["in"] for r in "AB"):
                    self.review(w, last)
                world.ladder_reviewed(w)
            last = {"busy": world.step_week(w, last)}
        world.run.final = {r: {**world.p[r], "pooled": world.pool, "put": world.put[r]} for r in "AB"}
        if world.mech:
            world.run.meta = world.commit_report()
        if world.fx:
            world.run.fix = world.fix_report()
        world.run.exits = list(world.exit_log)
        return world.run
