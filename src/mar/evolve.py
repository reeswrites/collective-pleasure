"""The evolution loop (ADR 0012): a population of rule sets (ADICO cards) searched by proof-filtered mutation.

One generation: pick parents (binary tournament), mutate a card, drop duplicates and oversize sets,
run the PROOF FILTER (world.check_spec must say "pass"; open is not safe) BEFORE any run, evaluate the
survivors over the training agent mixes, then select mu of mu + lambda by NSGA-II style non-dominated
sorting with feasibility (yield floor), crowding distance, and a bloat tie-break (fewer cards first).
Everything random comes from one random.Random(seed): deterministic under a seed.

The world (world_api.World) is the only place that knows the game. evolve() never touches the held-out
final exam; final_exam() is a separate function the caller runs once, after evolution.
The patch operator hands the world a failing TRACE and the cards. The oracle is never passed to it.
"""
import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path

from .cards import make_card
from .english import _cond_en

OPS = ("bound", "flip", "add_condition", "drop", "patch")
WEIGHTS = (35, 10, 15, 10, 30)
FLIPS = {"must_not": ("must", "may"), "must": ("must_not",), "may": ("must",)}


@dataclass
class Config:
    pop: int = 10
    offspring: int = 10
    generations: int = 12
    k: int = 3
    max_rules: int = 12
    attempts_factor: int = 12


@dataclass
class Individual:
    spec: tuple
    scores: dict
    yld: float | None
    seams: frozenset
    fail_trace: object = None
    op: str = "seed"
    rank: int = 0
    crowd: float = 0.0

    @property
    def n_rules(self):
        return len(self.spec)


# ------------------------------------------------------------------ multi-objective machinery

def dominates(a, b) -> bool:
    """a dominates b (both maximized): no worse everywhere, better somewhere."""
    return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))


def nondominated_sort(points, dom=dominates) -> list:
    """-> list of fronts, each a list of indices into points. Front 0 is non-dominated."""
    n = len(points)
    dominated_by = [[] for _ in range(n)]
    count = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and dom(points[i], points[j]):
                dominated_by[i].append(j)
            elif i != j and dom(points[j], points[i]):
                count[i] += 1
    fronts, cur = [], [i for i in range(n) if count[i] == 0]
    while cur:
        fronts.append(cur)
        nxt = []
        for i in cur:
            for j in dominated_by[i]:
                count[j] -= 1
                if count[j] == 0:
                    nxt.append(j)
        cur = sorted(nxt)
    return fronts


def crowding_distance(points, front) -> dict:
    """Crowding distance of each index in front; boundary points get infinity."""
    dist = {i: 0.0 for i in front}
    for m in range(len(points[front[0]])):
        order = sorted(front, key=lambda i: (points[i][m], i))
        lo, hi = points[order[0]][m], points[order[-1]][m]
        dist[order[0]] = dist[order[-1]] = math.inf
        if hi > lo:
            for a, i, b in zip(order, order[1:], order[2:]):
                dist[i] += (points[b][m] - points[a][m]) / (hi - lo)
    return dist


def hypervolume(points) -> float:
    """Volume dominated by maximized 3-D points above the origin (slice along the third axis)."""
    pts = [tuple(p) for p in points if all(x > 0 for x in p)]
    zs = sorted({p[2] for p in pts}, reverse=True)
    vol = 0.0
    for z, z_next in zip(zs, zs[1:] + [0.0]):
        area, best_y = 0.0, 0.0
        for x, y, _ in sorted((p for p in pts if p[2] >= z), key=lambda p: -p[0]):
            if y > best_y:
                area += x * (y - best_y)
                best_y = y
        vol += area * (z - z_next)
    return vol


def _cdom(world):
    """Constraint dominance: feasible beats infeasible; among infeasible, smaller shortfall wins."""
    def dom(a, b):
        (fa, va, oa), (fb, vb, ob) = a, b
        if fa != fb:
            return fa
        if not fa:
            return va < vb
        return dominates(oa, ob)
    return dom


def _point(world, ind):
    floor = getattr(world, "YIELD_FLOOR", 0.0)
    feas = world.feasible(ind.scores | {"yield": ind.yld})
    short = 0.0 if feas else max(0.0, floor - (ind.yld or 0.0))
    return (feas, short, tuple(ind.scores[o] for o in world.objectives))


def rank_population(world, pop):
    pts = [_point(world, i) for i in pop]
    for r, front in enumerate(nondominated_sort(pts, _cdom(world))):
        cd = crowding_distance([p[2] for p in pts], front)
        for i in front:
            pop[i].rank, pop[i].crowd = r, cd[i]
    return pop


# ------------------------------------------------------------------ evaluation

def evaluate(world, spec, split="train", cache=None):
    """Run the spec against every mix of the split. -> (scores, yield, seam keys, first failing trace)."""
    from .world_api import spec_key  # local: evolve has no other fishery knowledge
    key = (spec_key(spec), split)
    if cache is not None and key in cache:
        return cache[key]
    cond = world.conditions(split)
    per_mix, seams, fail_trace, yields = {}, set(), None, []
    for mix in world.mixes(split):
        runs = []
        for seed in mix.seeds:
            tr = world.run(spec, mix.make(), seed, cond, mix=mix.name)
            sc = world.score(tr)
            runs.append(sc)
            found = world.seams(tr, spec)
            for s in found:
                seams.add((s["mix"], s["kind"]))
            if found and fail_trace is None:
                fail_trace = tr
        per_mix[mix.name] = {n: _mean([r[n] for r in runs]) for n in runs[0]}
    scores = {o: _mean([m[o] for m in per_mix.values()]) for o in world.objectives}
    yields = [m["yield"] for m in per_mix.values() if m.get("yield") is not None]
    out = (scores, (_mean(yields) if yields else None), frozenset(seams), fail_trace, per_mix)
    if cache is not None:
        cache[key] = out
    return out


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def _individual(world, spec, cache, op="seed", split="train"):
    scores, yld, seams, ft, _ = evaluate(world, spec, split, cache)
    return Individual(tuple(spec), scores, yld, seams, ft, op)


# ------------------------------------------------------------------ mutation operators on cards

def _norm(expr):
    return " ".join(expr.replace("+", " + ").replace("-", " - ").split())


def _range(world, expr):
    for e, lo, hi in world.vocab():
        if _norm(e) == _norm(expr):
            return lo, hi
    return 0, 100


def _direction(card, cond):
    """+1 when raising the value makes the card forbid MORE; 0 when no direction (eq)."""
    up = cond["op"] in ("lt", "le")
    if cond["op"] == "eq":
        return 0
    return (1 if up else -1) if card.deontic == "must_not" else (-1 if up else 1)


def _gloss(d):
    conds = " and ".join(_cond_en(c) for c in d["conditions"])
    who, aim = d["attribute"], d["aim"]
    if d["deontic"] == "must_not":
        return f"When {conds}, a {who} must not {aim}." if conds else f"A {who} must never {aim}."
    if d["deontic"] == "must":
        return f"A {who} must {aim}" + (f" only when {conds}." if conds else " in every case.")
    return f"A {who} may {aim}" + (f" when {conds}." if conds else " in every case.")


def _rebuild(card, op, **changes):
    d = {"id": card.id, "attribute": card.attribute, "deontic": card.deontic, "aim": card.aim,
         "conditions": [dict(c) for c in card.conditions], "or_else": card.or_else, "gloss": card.gloss,
         "source": card.source}
    d.update(changes)
    d["gloss"] = _gloss(d)
    root = card.source.split(" | ")[-1]
    d["source"] = f"evolved ({op}) | {root}"
    return make_card(d)


def _replace(spec, i, card):
    return tuple(card if j == i else c for j, c in enumerate(spec))


def op_bound(spec, world, rng, trace=None):
    slots = [(i, j) for i, c in enumerate(spec) if c.deontic in ("must_not", "must")
             for j, cond in enumerate(c.conditions) if _direction(c, cond)]
    if not slots:
        return None
    i, j = rng.choice(slots)
    card, cond = spec[i], spec[i].conditions[j]
    mode, step = rng.choice((1, -1)), rng.choice((1, 2, 5, 10))  # +1 tighten, -1 loosen
    lo, hi = _range(world, cond["expr"])
    value = max(lo, min(hi, cond["value"] + _direction(card, cond) * mode * step))
    if value == cond["value"]:
        return None
    conds = [dict(c) for c in card.conditions]
    conds[j]["value"] = value
    return _replace(spec, i, _rebuild(card, "tighten" if mode == 1 else "loosen", conditions=conds))


def op_flip(spec, world, rng, trace=None):
    if not spec:
        return None
    i = rng.randrange(len(spec))
    card = spec[i]
    return _replace(spec, i, _rebuild(card, "flip", deontic=rng.choice(FLIPS[card.deontic])))


def op_add_condition(spec, world, rng, trace=None):
    slots = [i for i, c in enumerate(spec) if c.deontic in ("must_not", "must")]
    if not slots:
        return None
    i = rng.choice(slots)
    expr, lo, hi = rng.choice(world.vocab())
    cond = {"expr": expr, "op": rng.choice(("gt", "ge", "lt", "le")), "value": rng.randrange(lo, hi + 1, 5)}
    conds = [dict(c) for c in spec[i].conditions] + [cond]
    return _replace(spec, i, _rebuild(spec[i], "add_condition", conditions=conds))


def op_drop(spec, world, rng, trace=None):
    if len(spec) < 2:
        return None
    i = rng.randrange(len(spec))
    return tuple(c for j, c in enumerate(spec) if j != i)


def op_patch(spec, world, rng, trace=None):
    """Ask the scripted patcher for cards. It gets the failing trace and the cards, never the oracle."""
    if trace is None:
        return None
    new = world.propose_patch(trace, list(spec), rng)
    return tuple(spec) + tuple(new) if new else None


OPERATORS = dict(zip(OPS, (op_bound, op_flip, op_add_condition, op_drop, op_patch)))


def mutate(spec, world, rng, trace=None):
    """-> (new spec, op name) or (None, op name) when the chosen operator did not apply."""
    name = rng.choices(OPS, WEIGHTS)[0]
    return OPERATORS[name](spec, world, rng, trace), name


# ------------------------------------------------------------------ the loop

def _tournament(pop, rng):
    a, b = rng.sample(range(len(pop)), 2) if len(pop) > 1 else (0, 0)
    pa, pb = pop[a], pop[b]
    return pa if (pa.rank, -pa.crowd) <= (pb.rank, -pb.crowd) else pb


def _survive(world, pool, mu):
    rank_population(world, pool)
    pool.sort(key=lambda i: (i.rank, i.n_rules, -i.crowd))  # bloat tie-break: fewer cards before crowding
    keep = pool[:mu]
    rank_population(world, keep)
    return keep


def _log_record(world, gen, stats, pop, new_keys, seen, introduced, cand_prev):
    front = [i for i in pop if i.rank == 0 and world.feasible(i.scores | {"yield": i.yld})]
    objs = [tuple(i.scores[o] for o in world.objectives) for i in front]
    return {"gen": gen, **stats, "n_new_seams": len(new_keys), "new_seams": sorted(map(list, new_keys)),
            "seams_seen": len(seen), "introduced_seams_mean": introduced, "candidate_seam_prevalence": cand_prev,
            "front_size": len(front), "front_seam_prevalence": _mean([len(i.seams) for i in front]),
            "hv": hypervolume(objs), "pop_rules_mean": _mean([i.n_rules for i in pop]),
            "pop_rules_max": max(i.n_rules for i in pop),
            "front": [{"n_rules": i.n_rules, "ids": [c.id for c in i.spec], "scores": i.scores, "yield": i.yld,
                       "seams": sorted(map(list, i.seams))} for i in front],
            "feasible": sum(world.feasible(i.scores | {"yield": i.yld}) for i in pop)}


def evolve(world, seed_spec, seed, config=None, log_path=None, cache=None):
    """Run the loop on the TRAINING split only. -> dict(pop, elite, log, seed_individual)."""
    cfg, rng = config or Config(), random.Random(seed)
    cache = {} if cache is None else cache
    log, seen = [], set()
    out = Path(log_path) if log_path else None
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("")
    seed_ind = _individual(world, tuple(seed_spec), cache)
    seed_check = world.check_spec(seed_spec, cfg.k)
    pop = [seed_ind]
    have = {tuple(c.to_yaml() for c in seed_ind.spec)}
    for gen in range(cfg.generations + 1):
        target = cfg.pop - 1 if gen == 0 else cfg.offspring
        stats = {"proposed": 0, "duplicates": 0, "oversize": 0, "inapplicable": 0, "proof_rejected": 0,
                 "accepted": 0, "rejected_by_check": {}, "proposed_by_op": {}, "rejected_by_op": {}}
        kids, introduced = [], []
        attempts = 0
        while len(kids) < target and attempts < target * cfg.attempts_factor:
            attempts += 1
            parent = _tournament(pop, rng) if gen else seed_ind
            spec, op = mutate(parent.spec, world, rng, parent.fail_trace)
            if spec is None:
                stats["inapplicable"] += 1
                continue
            stats["proposed"] += 1
            stats["proposed_by_op"][op] = stats["proposed_by_op"].get(op, 0) + 1
            key = tuple(c.to_yaml() for c in spec)
            if key in have:
                stats["duplicates"] += 1
                continue
            if len(spec) > cfg.max_rules:
                stats["oversize"] += 1
                continue
            res = world.check_spec(spec, cfg.k)  # proof filter, before any run
            if not res.ok:
                stats["proof_rejected"] += 1
                stats["rejected_by_op"][op] = stats["rejected_by_op"].get(op, 0) + 1
                for name in res.failed:
                    stats["rejected_by_check"][name] = stats["rejected_by_check"].get(name, 0) + 1
                have.add(key)  # do not re-propose a known-bad mutant
                continue
            have.add(key)
            child = _individual(world, spec, cache, op=op)
            introduced.append(len(child.seams - parent.seams))
            kids.append(child)
            stats["accepted"] += 1
        keys = set().union(*[i.seams for i in (kids + ([seed_ind] if gen == 0 else []))]) if (kids or gen == 0) else set()
        new_keys = keys - seen
        seen |= keys
        pop = _survive(world, pop + kids, cfg.pop)
        cands = kids + ([seed_ind] if gen == 0 else [])
        rec = _log_record(world, gen, stats, pop, new_keys, seen, _mean(introduced),
                          _mean([len(i.seams) for i in cands]))
        rec["seed_check"] = seed_check.verdict if gen == 0 else None
        log.append(rec)
        if out:
            with out.open("a") as f:
                f.write(json.dumps(rec) + "\n")
    return {"pop": pop, "elite": pick_elite(world, pop), "log": log, "seed_individual": seed_ind}


def pick_elite(world, pop) -> Individual:
    """Feasible front member with the highest mean objective; ties by fewer cards. Falls back to least infeasible."""
    feas = [i for i in pop if world.feasible(i.scores | {"yield": i.yld})]
    if feas:
        return max(feas, key=lambda i: (round(_mean([i.scores[o] for o in world.objectives]), 9), -i.n_rules))
    return max(pop, key=lambda i: (i.yld or 0.0))


def final_exam(world, spec) -> dict:
    """The held-out exam: conditions and agent mixes the loop never sees. Run once, after evolution."""
    scores, yld, seams, _, per_mix = evaluate(world, spec, "exam", None)
    return {"scores": scores, "yield": yld, "seams": sorted(map(list, seams)), "per_mix": per_mix}
