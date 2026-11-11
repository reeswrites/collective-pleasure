"""Value consistency check (docs/results/value-consistency.md): does an agent's own value of an action agree with what the action
does to that agent's modeled pleasure?

Measurement only. Nothing here changes how a world runs: every branch is a deep copy of a world at the start of a week, the live
world is never touched, and the hooks below are set on copies only.

Two numbers per action, at one sampled decision (week w, role r, the k-th call of step_agent that week):
  perceived  the agent's own score for the action at that call, without noise: PersonaAgent.utilities for the utility actions, the
             fixed propose() score for the others (request, refuse_request, give, leave), minus the sanction estimate step_agent
             subtracts when a soft rule would be broken. Idle (doing nothing at that call) is 0, the agent's own floor. Actions a
             hard rule blocks are not measured.
  actual     the difference in the agent's own modeled outcome between a copy in which it takes that action at that call and a copy
             in which it does nothing at that call, summed over the next 1, 13 and 52 weeks. The rest of the week, the partner and every
             later week play on as the world plays them (so the agent's other calls that week may fill the freed units).

The copies make the same random draws up to the decision (the forced call still runs propose() in full, so the agent's stream is not
shifted). After it, branches diverge as the world would. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled value.
"""
from __future__ import annotations

import copy

from . import observe as OB

HORIZONS = (1, 13, 52)
MEASURES = ("pl", "raw", "net", "wnet")      # clipped pleasure, unclipped pleasure, pleasure - suffering, pleasure - w x suffering


def _one():
    return 1.0


def perceived_menu(agent, o):
    """The agent's own scores at observation o, noise off, with no draw left on its stream. -> (utilities {action: u},
    candidates [(score, cand)] as propose() ranks them)."""
    st = agent.rng.getstate()
    had, old = "_noise" in agent.__dict__, agent.__dict__.get("_noise")
    agent._noise = _one
    saved_req = agent.last_request
    try:
        u = agent.utilities(dict(o))
        cands = type(agent).propose(agent, dict(o))      # the class method: a tap may sit on the instance
    finally:
        if had:
            agent._noise = old
        else:
            del agent._noise
        agent.rng.setstate(st)
        agent.last_request = saved_req
    return u, cands


def snapshot(world):
    """A deep copy of the world at the start of a week, without its run log or hook (as observe.Observer._copy)."""
    from .worlds import household as H
    run, hook = world.run, world.hook
    world.run, world.hook = H.Run(), None
    try:
        return copy.deepcopy(world)
    finally:
        world.run, world.hook = run, hook


def _key(c):
    return (c["a"], c.get("kind"), c.get("take", 0))


class _Tap:
    """Installed on one copy's agent: at call k of week w it records the menu (probe), forces one candidate first, or returns no
    candidate (idle). Every call runs the agent's own propose() first, so the draws are the same as in the live world."""

    def __init__(self, world, r, w, k, mode, cand=None):
        self.world, self.r, self.w, self.k, self.mode, self.cand = world, r, w, k, mode, cand
        self.n, self.menu, self.trace_at = 0, None, None
        ag = world.agents[r]
        self.orig = type(ag).propose
        ag.propose = self

    def __call__(self, o):
        ag = self.world.agents[self.r]
        hit = o["week"] == self.w and self.n == self.k
        if o["week"] == self.w:
            self.n += 1
        if hit:
            u, cands = perceived_menu(ag, o)
            self.menu = {"u": u, "cands": cands, "o": {"in_hh": o["in_hh"], "other_in": o["other_in"], "B": o["hed"].B,
                                                        "N": o["hed"].N, "cap": o["hed"].capacity,
                                                        "levels": dict(o["hed"].level), "gap": o["gap"],
                                                        "asp": dict(o["asp"]), "units": self.world.units[self.r],
                                                        "money": self.world.p[self.r]["money"]},
                         "feasible": {_key(c): bool(self.world.feasible(self.r, c["a"], c.get("kind")))
                                      for c in [c for _, c in cands] + [{"a": a} for a in u]}}
            from .worlds import household as H
            rule = {}
            for kk in self.menu["feasible"]:     # the rule check step_agent makes: a soft rule costs its estimated sanction (pure here)
                dec, sanc, _ = self.world.decide(self.r, kk[0], self.w, kk[2])
                pen = self.world.sanction_cost(self.r, self.w, sanc) if dec == "soft" else 0.0
                rule[kk] = (dec, pen)
            self.menu["rule"] = rule
            self.trace_at = len(self.world.run.trace)
        out = self.orig(ag, o)
        if not hit:
            return out
        if self.mode == "idle":
            return []
        if self.mode == "force":
            hit_c = next(((s, c) for s, c in out if _key(c) == _key(self.cand)), None)
            if hit_c is None:                     # an action the agent scores at or below its floor: put it on the list
                return [(99.0, dict(self.cand))] + out
            return [(99.0, hit_c[1])] + [x for x in out if x is not hit_c]
        return out

    def executed(self):
        """The action executed at the tapped call (None when the agent did nothing there)."""
        if self.trace_at is None:
            return None
        for t in self.world.run.trace[self.trace_at:]:
            if t["week"] == self.w and t["role"] == self.r:
                if t.get("executed"):
                    return (t["action"], t.get("kind"), t.get("take", 0))
            elif t["role"] == self.world.other(self.r):
                return None                       # the other partner's call came first: this call executed nothing
        return None


def _rows(c, n_weeks, weights):
    """Per role, per week: clipped pleasure, unclipped pleasure, net, weighted net, and the week's net groups (observer groups)."""
    out = {}
    for r in "AB":
        acc = []
        parts = c.hed[r].parts_acc
        for i, o in enumerate(c.run.outcomes[:n_weeks]):
            h = o["hedonic"][r]
            p = parts[i] if i < len(parts) else None
            raw = h["pleasure"] - p["clip_p"] if p is not None else h["pleasure"]
            suf = h["s_off"] + h["s_non"]
            acc.append({"pl": h["pleasure"], "raw": raw, "net": h["pleasure"] - suf, "wnet": h["pleasure"] - weights[r] * suf,
                        "g": OB.groups(p, "net") if p is not None else None})
        out[r] = acc
    return out


def reseed(c, x):
    """Common random numbers across branches: from week x on, every stream the world draws from restarts from a seed that depends on
    the world's seed and the week only, so two branches differ by what the decision changed, not by shifted draws."""
    import random
    for q in "ABC":
        c.agents[q].rng = random.Random(f"vc|{c.seed}|{x}|{q}")
    if hasattr(c, "pair_rng"):
        c.pair_rng = random.Random(f"vc|{c.seed}|{x}|pair")


def branch(snap, last, w, r, k, mode, cand=None, weeks=52, lived=None, crn=True):
    """Play `weeks` weeks from a snapshot taken at the start of week w with the tap set. lived: a BaselineLived whose world is `snap`
    (the formation retries and stay readings then run in the branch as they do in the live loop; None = the world alone, as
    observe's replays). crn: reseed every stream at each later week (common random numbers). -> (tap, rows)."""
    from . import negotiation as NG
    from .makers import suffering_weight
    if lived is not None:
        lv = copy.deepcopy(lived)
        c = lv.world
    else:
        lv, c = None, copy.deepcopy(snap)
    for x in "AB":
        c.hed[x].parts_on, c.hed[x].parts_acc = True, []
    tap = _Tap(c, r, w, k, mode, cand)
    lt = last
    end = min(c.weeks, w + weeks)
    for x in range(w, end):
        if crn and x > w:
            reseed(c, x)
        if lv is not None and x > w and x % NG.REVIEW_EVERY == 0:
            if lv.apart and lv.decline:
                lv.retry(x, lt)
            elif all(c.p[q]["in"] for q in "AB"):
                lv.reading(x, lt)
        if c.early_review:
            c.ladder_reviewed(x)
        lt = {"busy": c.step_week(x, lt)}
    weights = {q: suffering_weight(c.personas[q]) for q in "AB"}
    return tap, _rows(c, end - w, weights)


def _sums(rows, h):
    return {m: sum(x[m] for x in rows[:h]) for m in MEASURES}


def _gsum(rows, h):
    g = {}
    for x in rows[:h]:
        for k, v in (x["g"] or {}).items():
            g[k] = g.get(k, 0.0) + v
    return g


def measure_decision(snap, last, w, r, k, horizons=HORIZONS, lived=None, skip=("leave", "return"), crn=True):
    """One sampled decision: the menu with each action's perceived score and its actual effect against idle.
    -> {"w", "r", "k", "ctx", "chosen", "items": [{a, kind, perceived, applied, actual{H: {who: {measure: x}}}, groups{H: {...}}}]}
    or None when the call never happened (no menu)."""
    H = max(horizons)
    tap0, base = branch(snap, last, w, r, k, "idle", weeks=H, lived=lived, crn=crn)
    if tap0.menu is None:
        return None
    menu = tap0.menu
    o = r, ("B" if r == "A" else "A")
    cands = menu["cands"]
    real = [c for s, c in cands if s > 0.003 or c["a"] in ("leave", "return")]
    listed = {_key(c) for _, c in cands}
    # every action the agent scores (utilities), listed or not (an action at or below the floor is still a use of the time), then the
    # propose-only candidates (request, refuse_request, give, leave)
    menu_all = list(cands) + [(v, {"a": a}) for a, v in menu["u"].items() if (a, None, 0) not in listed]
    chosen = None
    items = []
    seen = set()
    for s, c in menu_all:
        kk = _key(c)
        dec, pen = menu["rule"].get(kk, ("ok", 0.0))
        if kk in seen or c["a"] in skip or not menu["feasible"].get(kk) or dec == "hard":
            continue
        seen.add(kk)
        tap, rows = branch(snap, last, w, r, k, "force", c, weeks=H, lived=lived, crn=crn)
        ex = tap.executed()
        it = {"a": c["a"], "kind": c.get("kind"), "perceived": float(s) - pen, "score": float(s), "rule": dec, "sanction_est": pen, "listed": kk in listed, "applied": ex == kk, "actual": {}, "groups": {}}
        for h in horizons:
            it["actual"][h] = {who: {m: _sums(rows[x], h)[m] - _sums(base[x], h)[m] for m in MEASURES}
                               for who, x in (("own", o[0]), ("partner", o[1]))}
            g1, g0 = _gsum(rows[o[0]], h), _gsum(base[o[0]], h)
            it["groups"][h] = {g: g1.get(g, 0.0) - g0.get(g, 0.0) for g in set(g1) | set(g0)}
        items.append(it)
    if real:
        chosen = real[0]["a"]           # the noise-free top choice (the live choice also has noise and the rule check)
    return {"w": w, "r": r, "k": k, "ctx": menu["o"], "chosen_noise_free": chosen, "idle_applied": tap0.executed() is None,
            "items": items}
