"""Negotiated pots (docs/decisions/0013-negotiated-pots.md, docs/results/negotiation-prereg.md).

The author: "i think you have to negotiate shared pots with multiple agents or creating rules for it". Pot terms are not imposed by
the seed. Everyone who shares a pot (two or more) negotiates a bundle of terms from a small finite menu; an agreement compiles to
ADICO cards, and the proof checks run BEFORE anyone lives under them. No LLM, no network.

Everything numeric here is the prereg's, fixed before any run. The evaluation of living under a bundle is a closed-form PROXY of
the persona's weights (ASSUMED, not validated against rollouts). Wording rule: agents feel nothing; "value" is a modeled gloss.
"""
import random
import re
from dataclasses import dataclass, field
from itertools import product

import numpy as np

from .cards import make_card
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
TERM_ID = {"N1": "contribution", "N2": "use", "N3": "taking", "N4": "change", "N5": "exit", "N6": "stay", "N7": "requests"}
STAY_WEEKS = 52
DEADLINE = 12
LAMBDA0 = {"competitive": 0.1, "direct": 0.4, "avoidant": 0.6, "collaborative": 1.0, "accommodating": 1.5}
THETA0 = {"competitive": 0.10, "direct": 0.06, "avoidant": 0.04, "collaborative": 0.02, "accommodating": 0.0}
LAMBDA_END = 2.0
K = 3                                       # proof-check bound (months)
STUB_EXIT_CARDS = ("R8b-exit-terms-not-less", "R8c-exit-terms-not-more")   # replaced by the negotiated exit term
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
    ("contribution", "fixed"): "A member may not spend on themselves while this month's shared need is unfunded; everyone puts in a fixed share first.",
    ("contribution", "proportional"): "The higher earner may not spend on themselves while this month's shared need is unfunded; contributions follow income.",
    ("use", "needs_only"): "A member may take from the pot only when there is a shared need open.",
    ("use", "any_use"): "Any member may use the pot for any purpose.",
    ("use", "caps"): "A member may take from the pot only while their own private money is under 10.",
    ("taking", "allowed"): "A member may take another member's share of the pot for themselves.",
    ("taking", "forbidden"): "No member may take another member's share of the pot for themselves.",
    ("taking", "repay"): "A member who takes another's share has their own spending halved for two months, until it is made good.",
    ("change", "unanimous"): "The pot terms change only when every member consents.",
    ("change", "propose_accept"): "Any member may propose a change to the pot terms and the others may accept it.",
    ("change", "frozen"): "The pot terms can never be changed.",
    ("exit", "equal_split"): "A member who leaves carries exactly half of their pooled share and leaves the rest in the pot.",
    ("exit", "proportional"): "A member who leaves carries all of their own pooled share, what they put in.",
    ("exit", "forfeit"): "A member who leaves carries none of their pooled share.",
    ("stay", STAY_WEEKS): "Every member commits to stay for 52 weeks; leaving earlier forfeits the pooled share.",
    ("requests", "mutual"): "Every member commits to honor the others' stay-home requests for 52 weeks.",
}


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
    cards = [_card("N0-members", "may", "spend_shared", [], f"The pot is shared by {_names(members)}.", src)]
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
    return cards


def base_cards(variant):
    """The v2.1 base rules of a seed variant, without the stub exit terms (the negotiated exit term replaces them)."""
    return [c for c in H.load_variant(variant) if c.id not in STUB_EXIT_CARDS]


def menu_of(base):
    """Which optional commitments the base rules let a partner choose to make."""
    gate = H.PyGate(base)
    st = {n: 0 for n in H.STATE_VARS}
    return {"stay": gate.check("partner", "commit_stay", st)[0], "requests": gate.check("partner", "commit_request", st)[0]}


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
