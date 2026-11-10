"""Solver checks on a proposed spec, bounded to a small state space.

Verdicts: pass / fail / open. "open" = the bound was hit or the solver gave up; it
never means safe. Every report states the bound.
State bound: pool 0..100, month_total 0..100, pool + month_total <= 100 (reachable
states), catch 0..100. Sanction horizon k months.
"""
import z3
from .compile import POOL, MONTH_TOTAL, CATCH, violation

K_DEFAULT = 3
MAX_SANCTION_MONTHS = 6
ALLOWED_SANCTIONS = ("warn", "cap_halve", "suspend")
HALF_CAP = 5  # ASSUMED fixture constant: cap_halve limits a sanctioned fisher to 5 per action
STATE_OK = z3.And(POOL >= 0, POOL <= 100, MONTH_TOTAL >= 0, MONTH_TOTAL <= 100, POOL + MONTH_TOTAL <= 100)
CATCH_OK = z3.And(CATCH >= 0, CATCH <= 100)


def bound_text(k):
    return (f"k={k} sanction months; pool 0..100, month_total 0..100 (pool+month_total<=100), "
            f"catch 0..100")


def _stuck_state(violations, extra_ok=None):
    """Exists a state where EVERY catch in range is a violation (or breaks extra_ok)?
    -> (verdict, witness_state_or_None)."""
    ok = z3.Not(z3.Or(*violations)) if violations else z3.BoolVal(True)
    if extra_ok is not None:
        ok = z3.And(ok, extra_ok)
    s = z3.Solver()
    s.set("timeout", 10000)
    s.add(STATE_OK, z3.ForAll([CATCH], z3.Implies(CATCH_OK, z3.Not(ok))))
    r = s.check()
    if r == z3.sat:
        m = s.model()
        return "sat", {"pool": m.eval(POOL, True).as_long(), "month_total": m.eval(MONTH_TOTAL, True).as_long()}
    return ("unsat" if r == z3.unsat else "unknown"), None


def _stuck_at(violations_by_id, witness, extra_ok=None):
    """Concrete state: is every catch in range blocked by these cards (+extra_ok)?"""
    sub = [(POOL, z3.IntVal(witness["pool"])), (MONTH_TOTAL, z3.IntVal(witness["month_total"]))]
    vs = [z3.substitute(v, *sub) for v in violations_by_id.values()]
    ok = z3.Not(z3.Or(*vs)) if vs else z3.BoolVal(True)
    if extra_ok is not None:
        ok = z3.And(ok, z3.substitute(extra_ok, *sub))
    s = z3.Solver()
    s.add(CATCH_OK, ok)
    return s.check() == z3.unsat


def _minimal_core(violations_by_id, witness, extra_ok=None):
    """Deletion-based: smallest subset of cards that still blocks every action at the witness."""
    core = dict(violations_by_id)
    for cid in list(core):
        trial = {k: v for k, v in core.items() if k != cid}
        if _stuck_at(trial, witness, extra_ok):
            core = trial
    return sorted(core)


def check_conflict(cards):
    """(a) no must / must_not pair on the same aim that cannot both be satisfied in some state."""
    bad, unknown = [], False
    for m in (c for c in cards if c.deontic == "must"):
        for n in (c for c in cards if c.deontic == "must_not" and c.aim == m.aim):
            vm, vn = violation(m), violation(n)
            verdict, wit = _stuck_state([vm, vn])
            if verdict == "sat":
                bad.append({"cards": [m.id, n.id], "witness": wit})
            elif verdict == "unknown":
                unknown = True
    if bad:
        ids = sorted({i for b in bad for i in b["cards"]})
        return "fail", ids, f"conflicting pairs {[b['cards'] for b in bad]}; example state {bad[0]['witness']}"
    return ("open", [], "solver gave up") if unknown else ("pass", [], "no conflicting must/must_not pair")


def check_deadlock(cards):
    """(b) in every state within bounds some action (catch 0 counts) is permitted."""
    vs = {c.id: violation(c) for c in cards if violation(c) is not None}
    verdict, wit = _stuck_state(list(vs.values()))
    if verdict == "sat":
        return "fail", _minimal_core(vs, wit), f"no permitted action at state {wit}"
    return ("open", [], "solver gave up") if verdict == "unknown" else ("pass", [], "a permitted action exists in every state")


def check_sanctions(cards):
    """(c) every or_else is None or a finite sanction from the allowed set."""
    bad = []
    for c in cards:
        s = c.or_else
        if s is None:
            continue
        d = s.get("duration_months")
        if s.get("kind") not in ALLOWED_SANCTIONS or not isinstance(d, int) or not (1 <= d <= MAX_SANCTION_MONTHS):
            bad.append(c.id)
    if bad:
        return "fail", bad, f"sanction not finite (1..{MAX_SANCTION_MONTHS} months) or not in {ALLOWED_SANCTIONS}"
    return "pass", [], f"all sanctions finite (<= {MAX_SANCTION_MONTHS} months) and in {ALLOWED_SANCTIONS}"


def check_repair(cards, k=K_DEFAULT):
    """(d) a sanctioned agent can act compliantly in every state and the sanction ends within k months."""
    vs = {c.id: violation(c) for c in cards if violation(c) is not None}
    stuck, slow = [], []
    for c in cards:
        s = c.or_else
        if not s or s.get("kind") not in ALLOWED_SANCTIONS or not isinstance(s.get("duration_months"), int):
            continue  # malformed sanctions are check (c)'s failure
        restr = {"warn": None, "cap_halve": CATCH <= HALF_CAP, "suspend": CATCH == 0}[s["kind"]]
        verdict, wit = _stuck_state(list(vs.values()), restr)
        if verdict == "sat":
            stuck.append(c.id)
        elif verdict == "unknown" or s["duration_months"] > k:
            slow.append(c.id)
    if stuck:
        return "fail", stuck, "under this sanction some state leaves no permitted action: no repair path"
    if slow:
        return "open", slow, f"repair not shown within k={k} months (sanction longer than k, or solver gave up)"
    return "pass", [], f"every sanction leaves a permitted action in every state and ends within k={k} months"


def check_spec(cards, k=K_DEFAULT):
    out = []
    for name, fn in (("a_no_conflict", check_conflict), ("b_no_deadlock", check_deadlock),
                     ("c_bounded_sanctions", check_sanctions), ("d_repair_path", lambda c: check_repair(c, k))):
        verdict, ids, detail = fn(cards)
        out.append({"check": name, "verdict": verdict, "cards": ids, "detail": detail, "bound": bound_text(k)})
    return out


def check_patch(cards, patch_cards, k=K_DEFAULT):
    """Accept only if every check is 'pass' (open is not safe)."""
    verdicts = check_spec(list(cards) + list(patch_cards), k)
    return {"accepted": all(v["verdict"] == "pass" for v in verdicts), "verdicts": verdicts,
            "bound": bound_text(k), "patch_ids": [c.id for c in patch_cards]}
