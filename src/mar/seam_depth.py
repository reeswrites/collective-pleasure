"""Seam depth: how hard is a hole in a rule set, read off the rules' own structure.

A seam is a run whose every executed action passes the gate but which the household oracle flags
(household_oracle.seam_flag: victim freedom drop or friend shut-out, relative to a reference run).
Formal model (FM) and bound, all stated in docs/results/seam-ladder-prereg.md:
  episode 2 months; a deviation is a forced move for Partner A or B at slot 0..2 of month 0 (at most one per
  role and slot); everything else follows the default cooperative script; k deviations at most; the friend C is
  passive. Search is exhaustive inside these bounds; hitting the evaluation budget gives "open", never "safe".

depth  = length of the shortest exploiting trace; agents = fewest distinct roles among exploiting traces <= k.
classify_seam(run, rules, k) -> {"kind": "predicted", "depth", "agents"} | {"kind": "inventive"} | {"kind": "open"}
(and {"kind": "none"} when the run is not a seam at all).

ASSUMED: FM leaves out spend_self and the friend's moves (they change only the actor's own state), and has no
gift_pooled; the harness supports gift_pooled so the out-of-model fixture can show an inventive seam.
"""
from itertools import combinations

from . import household_oracle as oracle
from .worlds import household as H

K_DEFAULT = 3
HORIZON = 2
FM_ROLES = ("A", "B")
MOVES = (("request", {"kind": "no_contact"}), ("request", {"kind": "stay_home"}), ("leave", {"take": 0}),
         ("leave", {"take": 100}), ("return", {}), ("refuse_request", {}))
BUDGET_DEFAULT = 40000
LADDER = ("L1_exit_lock", "L2_double_request", "L3_return_trick", "L4_joint_shutout", "L5_gift_pool")
LADDER_DIR = H.RULES / "ladder"


def load_ladder(name):
    return H.load_cards(LADDER_DIR / name)


def move_text(atom):
    r, slot, mi = atom
    a, kw = MOVES[mi]
    return f"{r} slot {slot}: {a}" + ("".join(f" {k}={v}" for k, v in kw.items()))


class Forced:
    """Default cooperative script with forced moves at month 0 (slot -> candidate)."""
    def __init__(self, forced):
        self.base, self.forced = H.Cooperator(), forced

    @property
    def rng(self):
        return self.base.rng

    @rng.setter
    def rng(self, v):
        self.base.rng = v

    def consents(self, kind):
        return self.base.consents(kind)

    def propose(self, o):
        if o["month"] == 0 and o["slot"] in self.forced:
            return [self.forced[o["slot"]]]
        return self.base.propose(o)


def _key(cards):
    return tuple(c.to_yaml() for c in cards)


_GATES, _ROLLS = {}, {}


def _gate(cards):
    k = _key(cards)
    if k not in _GATES:
        _GATES[k] = H.HouseholdGate(cards)
    return _GATES[k]


def rollout(cards, plan, seed=0, extra=None):
    """plan: tuple of atoms (role, slot, move index). extra: {role: agent} overrides (out-of-model fixtures).
    -> (run, valid) where valid = every forced move was executed (so every action passed the gate)."""
    ck = (_key(cards), tuple(plan), seed) if extra is None else None
    if ck is not None and ck in _ROLLS:
        return _ROLLS[ck]
    forced = {r: {} for r in "AB"}
    for r, slot, mi in plan:
        a, kw = MOVES[mi]
        forced[r][slot] = {"a": a, **kw}
    agents = {"A": Forced(forced["A"]), "B": Forced(forced["B"]), "C": H.Friend()}
    agents.update(extra or {})
    run = H.World(_gate(cards), agents, seed, months=HORIZON).play()
    done = {(t["role"], t["slot"], t["action"], t["take"]) for t in run.trace if t["month"] == 0 and t["executed"]}
    valid = all((r, s, MOVES[mi][0], MOVES[mi][1].get("take", 0)) in done for r, s, mi in plan)
    run.meta = {"seed": seed, "deviators": sorted({r for r, _, _ in plan}), "plan": tuple(plan)}
    if ck is not None:
        _ROLLS[ck] = (run, valid)
    return run, valid


def evaluate(cards, plan, seed=0):
    """-> (valid, flag dict). Reference = no deviation, same seed."""
    run, valid = rollout(cards, plan, seed)
    if not valid:
        return False, {"flagged": False, "harm": 0.0, "kinds": []}
    ref, _ = rollout(cards, (), seed)
    return True, oracle.seam_flag(run.outcomes, ref.outcomes, {r for r, _, _ in plan})


def atoms(roles):
    return [(r, s, m) for r in roles for s in range(3) for m in range(len(MOVES))]


def plans(roles, max_len):
    """All plans of length 1..max_len over `roles`, shortest first, one move per (role, slot)."""
    at = atoms(roles)
    for L in range(1, max_len + 1):
        for combo in combinations(at, L):
            if len({(r, s) for r, s, _ in combo}) == L:
                yield combo


def search(cards, k=K_DEFAULT, seed=0, budget=BUDGET_DEFAULT, kinds=None):
    """Exhaustive bounded search of FM. -> {"status": "found"|"none"|"open", "depth", "agents", "example",
    "n_traces", "evaluated", "k", "bound"}. `kinds` restricts to flags of those harm kinds."""
    n, best, agents_min, count, example = 0, None, None, 0, None
    for plan in plans(FM_ROLES, k):
        if n >= budget:
            return {"status": "open", "depth": best, "agents": agents_min, "example": example, "n_traces": count,
                    "evaluated": n, "k": k, "bound": bound_text(k)}
        n += 1
        valid, flag = evaluate(cards, plan, seed)
        if valid and flag["flagged"] and (kinds is None or set(kinds) & set(flag["kinds"])):
            count += 1
            roles = len({r for r, _, _ in plan})
            if best is None:
                best, example = len(plan), plan
            agents_min = roles if agents_min is None else min(agents_min, roles)
    status = "found" if best is not None else "none"
    return {"status": status, "depth": best, "agents": agents_min, "example": example, "n_traces": count,
            "evaluated": n, "k": k, "bound": bound_text(k)}


def bound_text(k):
    return (f"k={k} deviations; {HORIZON}-month episode; moves for partners A and B at slot 0..2 of month 0: "
            f"{', '.join(a + (str(kw) if kw else '') for a, kw in MOVES)}; friend passive; exhaustive")


def classify_seam(run, rules, k=K_DEFAULT, budget=BUDGET_DEFAULT) -> dict:
    """Label a run found by an agent. `run` needs .outcomes and .meta {"seed", "deviators"} (set by rollout or the
    agents here). predicted: FM has an exploiting trace of the same harm kind within k. inventive: it searched to
    k exhaustively and found none. open: budget ran out first. none: the run is not a seam."""
    meta = getattr(run, "meta", {})
    seed = meta.get("seed", 0)
    ref, _ = rollout(rules, (), seed)
    flag = oracle.seam_flag(run.outcomes, ref.outcomes, set(meta.get("deviators", ())))
    all_pass = all(t["allowed"] for t in run.trace if t.get("executed") and t["role"] != "C")
    if not (flag["flagged"] and all_pass):
        return {"kind": "none", "flag": flag}
    res = search(rules, k, seed, budget, kinds=flag["kinds"])
    if res["status"] == "found":
        return {"kind": "predicted", "depth": res["depth"], "agents": res["agents"], "flag": flag, "bound": res["bound"]}
    if res["status"] == "none":
        return {"kind": "inventive", "flag": flag, "bound": res["bound"]}
    return {"kind": "open", "flag": flag, "bound": res["bound"]}


# ---- scripted agents of graded sophistication ------------------------------------------------------------

AGENTS = {"greedy": (("A",), 1), "planner": (("A",), 3), "pair": (("A", "B"), 3)}


def run_agent(name, cards, seed):
    """The agent looks ahead by rollouts in the real harness (its own role set, its depth), stops at the first plan
    the oracle flags. -> {"found", "plan", "evaluated" (rollouts until found, or all if none), "run"}."""
    roles, depth = AGENTS[name]
    n = 0
    for plan in plans(roles, depth):
        n += 1
        valid, flag = evaluate(cards, plan, seed)
        if valid and flag["flagged"]:
            run, _ = rollout(cards, plan, seed)
            return {"found": True, "plan": plan, "evaluated": n, "run": run}
    return {"found": False, "plan": None, "evaluated": n, "run": None}


class Gifter(Forced):
    """Out-of-model fixture: uses harness move gift_pooled (not in FM) at slot 1 of month 0."""
    def __init__(self):
        super().__init__({1: {"a": "gift_pooled"}})


def run_gifter(cards, seed=0):
    run, _ = rollout(cards, (), seed, extra={"A": Gifter()})
    run.meta = {"seed": seed, "deviators": ["A"], "plan": ("gift_pooled",)}
    return run


def ladder_table(seeds=(0, 1, 2), k=K_DEFAULT, budget=BUDGET_DEFAULT):
    """-> rows [{id, depth, agents, status, found: {agent: n_seeds_found}, time: {agent: mean evaluated}}]
    and the inventive rows from the fixture."""
    rows = []
    for name in LADDER:
        cards = load_ladder(name)
        formal = search(cards, k, 0, budget)
        found = {a: [run_agent(a, cards, s) for s in seeds] for a in AGENTS}
        rows.append({"id": name, "depth": formal["depth"], "agents": formal["agents"], "status": formal["status"],
                     "example": formal["example"], "n_traces": formal["n_traces"], "bound": formal["bound"],
                     "found": {a: sum(r["found"] for r in rs) for a, rs in found.items()},
                     "time": {a: (sum(r["evaluated"] for r in rs if r["found"]) / max(1, sum(r["found"] for r in rs)))
                              for a, rs in found.items()},
                     "classes": {a: [classify_seam(r["run"], cards, k, budget)["kind"] for r in rs if r["found"]]
                                 for a, rs in found.items()}})
    inv = []
    cards = load_ladder("L5_gift_pool")
    for s in seeds:
        c = classify_seam(run_gifter(cards, s), cards, k, budget)
        inv.append({"seed": s, "kind": c["kind"]})
    return rows, inv


def ladder_score(rows, agent, inventive=()):
    """Deepest predicted seam found reliably (>= 2 of 3 seeds), its time, and the inventive seams found."""
    reliable = [r for r in rows if r["found"][agent] >= 2 and r["depth"] is not None]
    top = max(reliable, key=lambda r: (r["depth"], r["agents"]), default=None)
    return {"agent": agent, "deepest": None if top is None else {"id": top["id"], "depth": top["depth"],
            "agents": top["agents"], "time": top["time"][agent]},
            "max_agents": max([r["agents"] for r in reliable], default=0),
            "inventive": [i for i in inventive if i["kind"] == "inventive"]}
