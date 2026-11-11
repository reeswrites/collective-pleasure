"""Household checks for the rule-set lint, lifted out of lint.py on 2026-11-11 (docs/notes/repo-split-map.md).

The code is moved unchanged. Importing this module registers the household world with lint.register_world(); lint.py imports
it on first use (lint.PLUGINS), so the generic lint no longer imports the household world at module level.
No network, no model calls.
"""
import z3

from .lint import MAY_EXCEPTION_RE, RuleSet, _finding, register_world
from .worlds import household as H

VOCAB = {"attributes": ("partner", "friend"),
         "aims": H.PARTNER_ACTIONS + H.EXTRA_ACTIONS + ("veto", "take_shared", "any"),
         "vars": H.VAR_NAMES, "kind": "household"}


def bound_text(k):
    return H.bound_text(k) + "; exit = legal leave at any take now or within k months of waiting (standing requests clearable by a legal refuse_request)"


def negotiated_sets(sample=40, variant="author_seed_v2_bindable", floor=26) -> list:
    """A deterministic sample of compiled negotiated agreements (base rules + compiled bundle + exit floor), evenly spaced over
    the 729-bundle menu, always including the first and last (all-defaults and all-extremes)."""
    from . import negotiation as N
    base = N.base_cards(variant)
    menu = N.menu_of(base)
    blist = N.bundles(menu["stay"], menu["requests"])
    n = len(blist)
    idx = sorted({round(i * (n - 1) / max(1, sample - 1)) for i in range(sample)})
    out = []
    for i in idx:
        b = blist[i]
        cards = base + N.compile_bundle(b, ["p-a", "p-b"]) + N.floor_cards(floor)
        out.append(RuleSet("negotiated/" + "-".join(str(b[t]) for t in N.TERM_NAMES), "household", cards, {},
                           f"negotiation.compile_bundle on {variant}, bundle #{i} of {n}"))
    return out


# ---- household: a, b, c ------------------------------------------------------------------------------------

def _hh_deadlock(rs):
    out = []
    p = H.check_deadlock(rs.cards)
    if p[0] != "pass":
        out.append(_finding("a", p[0], p[1], "partner: " + p[2]))
    if any(c.attribute == "friend" for c in rs.cards):
        vs = {a: H.violations(rs.cards, a, "friend") for a in H.FRIEND_ACTIONS}
        verdict, wit = H._solve(H._blocked(vs, H.FRIEND_ACTIONS))
        if verdict != "unsat":
            out.append(_finding("a", "fail" if verdict == "sat" else "open",
                                [c.id for c in rs.cards if c.attribute == "friend"], f"friend: no permitted action at state {wit}"))
    return out


def _exit_formula(cards, k, min_take=0, witness=None):
    """Formula: some state (or the given witness) where no leave with take >= min_take is legal now or within k months, even after
    a legal refuse_request clears standing requests."""
    vl, vr = H.violations(cards, "leave"), H.violations(cards, "refuse_request")
    Z = H.Z
    clear = [(Z["no_contact_request"], z3.IntVal(0)), (Z["stay_home_request"], z3.IntVal(0))]

    def leave_ok(t, cleared):
        sub = [(Z["months_in"], Z["months_in"] + t)] + (clear if cleared else [])
        sh = {cid: z3.substitute(v, *sub) for cid, v in vl.items()}
        return z3.Not(z3.ForAll([Z["take"]], z3.Implies(H._take_dom("leave", min_take), z3.Not(H._ok(sh)))))

    parts = []
    for t in range(k + 1):
        parts.append(z3.Not(z3.Or(leave_ok(t, False), z3.And(H._ok(vr), leave_ok(t, True)))))
    f = z3.And(*parts)
    if witness is not None:
        f = z3.substitute(f, *[(Z[n], z3.IntVal(witness[n])) for n in H.STATE_VARS])
    return f


def _exit_core(cards, k, wit, min_take=0):
    cur = list(cards)
    for c in list(cur):
        trial = [x for x in cur if x.id != c.id]
        s = z3.Solver()
        s.set("timeout", 10000)
        s.add(_exit_formula(trial, k, min_take, wit))
        if s.check() == z3.sat:
            cur = trial
    return [c.id for c in cur if c.aim in ("leave", "refuse_request", "any")]


def _hh_exit(rs, k):
    out = []
    for name, min_take, sev in (("b", 0, "fail"), ("b2", H.MIN_EXIT_TAKE, "note")):
        with_ns = H._solve(_exit_formula(rs.cards, k, min_take))
        verdict, wit = with_ns
        if verdict == "sat":
            core = _exit_core(rs.cards, k, wit, min_take)
            what = "no legal exit (leave at any take)" if min_take == 0 else f"no meaningful exit (leave carrying >= {min_take}%)"
            out.append(_finding(name, sev, core, f"{what} within k={k} at state {wit}"))
        elif verdict == "unknown":
            out.append(_finding(name, "open" if sev == "fail" else "note", [], "solver gave up"))
    return out


def _may_blocked(rs):
    """A `may` card whose action is wholly blocked (every take) by other HARD walls (a violated card with no or_else; a card with
    an or_else is soft in the household worlds, rules/README.md) in some state where the may applies."""
    out = []
    Z = H.Z
    with H.household_namespace():
        for m in (c for c in rs.cards if c.deontic == "may" and c.aim in H.PARTNER_ACTIONS):
            if MAY_EXCEPTION_RE.search(m.gloss):
                continue
            vs = {c.id: v for c in rs.cards if c.id != m.id and c.deontic != "may" and c.attribute == m.attribute
                  and c.or_else is None and c.aim in (m.aim, "any") and (v := H._compile.violation(c)) is not None}
            if not vs:
                continue
            applies = H._compile.conditions_expr(m)
            f = z3.And(z3.Exists([Z["take"]], z3.And(H._take_dom(m.aim), applies)),
                       z3.ForAll([Z["take"]], z3.Implies(z3.And(H._take_dom(m.aim), applies), z3.Not(H._ok(vs)))))
            verdict, wit = H._solve(f)
            if verdict == "sat":
                blockers = [cid for cid, v in vs.items()
                            if z3.is_true(z3.simplify(z3.substitute(v, *[(Z[n], z3.IntVal(wit[n])) for n in H.STATE_VARS],
                                                                    (Z["take"], z3.IntVal(0)))))] or sorted(vs)
                out.append(_finding("c", "fail", [m.id] + blockers,
                                    f"`may {m.aim}` ({m.id}) is wholly blocked by {sorted(blockers)} at state {wit}, and the may's gloss "
                                    f"declares no exception"))
            elif verdict == "unknown":
                out.append(_finding("c", "open", [m.id], "solver gave up on may-versus-must_not"))
    return out


def _household_checks(rs, k):
    out = _hh_deadlock(rs) + _hh_exit(rs, k)
    v = H.check_conflict(rs.cards)
    if v[0] != "pass":
        out.append(_finding("c", v[0], v[1], v[2]))
    out += _may_blocked(rs)
    spec = {c["check"]: c for c in H.check_spec(rs.cards, k)}
    for key in ("c_bounded_sanctions", "d_repair_path"):
        if spec[key]["verdict"] != "pass":
            out.append(_finding("x", spec[key]["verdict"], spec[key]["cards"], spec[key]["detail"]))
    return out




register_world("household", VOCAB, _household_checks, bound_text)
