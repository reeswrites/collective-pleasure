"""Value consistency check (docs/results/value-consistency.md): the agents' own action values against the hedonic model's known
answer, in makers-off worlds. Measurement only; no model behaviour changes (src/mar/valuecheck.py).

World: H39b's M0 arm, which is the H38 baseline at L0 (pairing dial 0), exit fallback F4 with items (V2-split-loves), the per-persona
suffering-weight rule over 52 weeks, makers off. Pairings: H38's 120 confirmatory pairings. Scripted agents, no model calls.

At sampled weeks, for each partner, at the week's last decision call (the third pass), every action the agent scores is forced in
turn in an isolated copy, and compared with a copy in which the agent does nothing at that call. The rest of the week up to that call is
the same in every copy, so the difference is one unit of that action against idle. Later weeks use common random numbers.

  uv run python scripts/value_consistency.py --run          the main sample (world-only branches; at most 3 workers)
  uv run python scripts/value_consistency.py --harness      a smaller sample with the formation retries and stay readings inside the branches
  uv run python scripts/value_consistency.py --first        a smaller sample at the week's first call (the rest of the week re-plans)
  uv run python scripts/value_consistency.py --analyze      runs/value-consistency/analysis.json and the tables for the write-up

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.
"""
import argparse
import copy
import dataclasses
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import h38_pairing_run as H38  # noqa: E402
from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar import valuecheck as VC  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "value-consistency"
WORKERS = 3
RULE = {"decide_on": "weighted", "decide_weeks": 52}          # H39b's main rule (M0 arm)
LAST_START = H.WEEKS - max(VC.HORIZONS)                         # a sampled week leaves room for the 52-week horizon
MAIN = {"pairs_every": 1, "seeds": (0, 1, 2, 3), "weeks": 6, "k": 2, "harness": False}
HARNESS = {"pairs_every": 3, "seeds": (0,), "weeks": 3, "k": 2, "harness": True}
FIRST = {"pairs_every": 3, "seeds": (0,), "weeks": 4, "k": 0, "harness": False}


def sample_weeks(a, b, seed, n):
    rng = random.Random(f"vc-weeks|{a}|{b}|{seed}")
    return sorted(rng.sample(range(1, LAST_START + 1), n))


def _ctx():
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **RULE)
    return fx


def _lived_snapshot(lived):
    world = lived.world
    run, hook = world.run, world.hook
    world.run, world.hook = H.Run(), None
    try:
        return copy.deepcopy(lived)
    finally:
        world.run, world.hook = run, hook


def run_pair(a, b, seed, n_weeks, k, harness):
    """Play one makers-off life as H39b's M0 arm does and measure the sampled decisions. -> list of decision records."""
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    weeks = set(sample_weeks(a, b, seed, n_weeks))
    out = []
    with HD.use_levers(RT.LEVERS), HD.use_fixes(_ctx()), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[H38.CELL]):
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        world = lived.world
        last = {"busy": {"A": False, "B": False}}
        for w in range(max(weeks) + 1):
            if w and w % NG.REVIEW_EVERY == 0:
                if lived.apart and lived.decline:
                    lived.retry(w, last)
                elif all(world.p[r]["in"] for r in "AB"):
                    lived.reading(w, last)
            if world.early_review:
                world.ladder_reviewed(w)
            if w in weeks:
                snap = VC.snapshot(world)
                sl = _lived_snapshot(lived) if harness else None
                for r in "AB":
                    rec = VC.measure_decision(snap, dict(last), w, r, k, lived=sl)
                    if rec is not None:
                        rec.update(a=a, b=b, seed=seed, persona=a if r == "A" else b,
                                   both_in=all(world.p[x]["in"] for x in "AB"))
                        out.append(rec)
            last = {"busy": world.step_week(w, last)}
    return out


def task(args):
    a, b, seed, n_weeks, k, harness = args
    t0 = time.time()
    recs = run_pair(a, b, seed, n_weeks, k, harness)
    return recs, time.time() - t0


def collect(cfg, f, workers=WORKERS):
    workers = min(workers, 3)
    OUT.mkdir(parents=True, exist_ok=True)
    pairs = H38.pairings(H38.CONFIRM)[::cfg["pairs_every"]]
    done = set()
    if f.exists():
        done = {(r["a"], r["b"], r["seed"]) for r in load(f)}
    tasks = [(a, b, s, cfg["weeks"], cfg["k"], cfg["harness"]) for (a, b) in pairs for s in cfg["seeds"] if (a, b, s) not in done]
    print(f"{len(tasks)} tasks, {workers} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as fh:
        for i, (recs, dt) in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            if recs:
                fh.write("\n".join(json.dumps(r) for r in recs) + "\n")
                fh.flush()
            if i % 20 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {dt:.1f}s wall {time.time() - t0:.0f}s", flush=True)


def load(f):
    return [json.loads(x) for x in Path(f).read_text().splitlines() if x.strip()]


# ---- analysis ----------------------------------------------------------------------------------------------------------------

def items(recs, applied=True):
    """Flatten to one row per (decision, action): perceived, actual per horizon and measure (own and partner), the decision's key."""
    out = []
    for d in recs:
        dk = (d["a"], d["b"], d["seed"], d["w"], d["r"])
        for it in d["items"]:
            if applied and not it["applied"]:
                continue
            out.append({"dk": dk, "run": (d["a"], d["b"], d["seed"]), "a": it["a"], "kind": it.get("kind"),
                        "p": it["perceived"], "listed": it.get("listed", True), "in": d["ctx"]["in_hh"] and d["ctx"]["other_in"],
                        "act": {int(h): v for h, v in it["actual"].items()}, "g": {int(h): v for h, v in it["groups"].items()},
                        "levels": d["ctx"]["levels"]})
    return out


def _ranks(x):
    """Ranks with ties averaged (as scipy.stats.rankdata)."""
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    xs = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1
        i = j + 1
    return r


def spearman(x, y):
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return None
    rx, ry = _ranks(x), _ranks(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def boot_mean(rows, f, n=1000, seed=0):
    """Mean of f over rows with a 95% bootstrap interval, resampling runs (a run's decisions are not independent)."""
    by = {}
    for r in rows:
        by.setdefault(r["run"], []).append(f(r))
    keys = list(by)
    if not keys:
        return None
    est = float(np.mean([v for k in keys for v in by[k]]))
    rng = np.random.default_rng(seed)
    sums = np.array([sum(by[k]) for k in keys])
    cnts = np.array([len(by[k]) for k in keys])
    bs = []
    for _ in range(n):
        idx = rng.integers(0, len(keys), len(keys))
        bs.append(sums[idx].sum() / cnts[idx].sum())
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"est": round(est, 5), "lo": round(float(lo), 5), "hi": round(float(hi), 5), "n": int(cnts.sum())}


def act_of(r, h, m="net", who="own"):
    return r["act"][h][who][m]


def analyze(recs, horizons=VC.HORIZONS, measures=("net", "pl", "raw", "wnet")):
    rows = items(recs)
    res = {"decisions": len(recs), "items": len(rows), "applied_share": None, "per_action": {}, "overall": {}, "idle": {},
           "groups": {}, "top_agree": {}}
    allit = [it for d in recs for it in d["items"]]
    res["applied_share"] = round(sum(it["applied"] for it in allit) / max(1, len(allit)), 4)
    acts = sorted({r["a"] for r in rows}, key=lambda a: -sum(1 for r in rows if r["a"] == a))
    for a in acts:
        xs = [r for r in rows if r["a"] == a]
        e = {"n": len(xs), "listed_share": round(float(np.mean([r["listed"] for r in xs])), 3),
             "perceived": boot_mean(xs, lambda r: r["p"])}
        for h in horizons:
            for m in measures:
                e[f"actual_{m}_{h}"] = boot_mean(xs, lambda r, h=h, m=m: act_of(r, h, m))
            e[f"partner_net_{h}"] = boot_mean(xs, lambda r, h=h: act_of(r, h, "net", "partner"))
            e[f"rho_net_{h}"] = spearman([r["p"] for r in xs], [act_of(r, h) for r in xs])
            e[f"gap_net_{h}"] = boot_mean(xs, lambda r, h=h: act_of(r, h) - r["p"])
            e[f"sign_disagree_{h}"] = round(float(np.mean([(r["p"] > 0.003) != (act_of(r, h) > 0) for r in xs])), 3)
        e["in_hh_share"] = round(float(np.mean([r["in"] for r in xs])), 3)
        res["per_action"][a] = e
        res["groups"][a] = {h: {g: round(float(np.mean([r["g"][h].get(g, 0.0) for r in xs])), 5)
                                for g in sorted({g for r in xs for g in r["g"][h]})} for h in horizons}
    for h in horizons:
        for m in measures:
            p = np.array([r["p"] for r in rows])
            y = np.array([act_of(r, h, m) for r in rows])
            slope = float((p @ y) / (p @ p)) if p @ p > 0 else None
            # within-decision rank agreement (decisions with 3 or more measured actions)
            byd = {}
            for r in rows:
                byd.setdefault(r["dk"], []).append(r)
            wr = [spearman([r["p"] for r in v], [act_of(r, h, m) for r in v]) for v in byd.values() if len(v) >= 3]
            wr = [x for x in wr if x is not None]
            res["overall"][f"{m}_{h}"] = {"rho_pooled": spearman(list(p), list(y)), "rho_within_mean": round(float(np.mean(wr)), 4) if wr else None,
                                          "n_within": len(wr), "slope_through_0": round(slope, 4) if slope is not None else None,
                                          "mean_perceived": round(float(p.mean()), 5), "mean_actual": round(float(y.mean()), 5)}
            # top choice: does the agent's own best action (or idle when nothing clears the floor) match the best by actual?
            agree = n = 0
            for v in byd.values():
                if len(v) < 2:
                    continue
                n += 1
                best_p = max(v, key=lambda r: r["p"])
                own = best_p["a"] if best_p["p"] > 0.003 else "idle"
                best_a = max(v, key=lambda r: act_of(r, h, m))
                act = best_a["a"] if act_of(best_a, h, m) > 0 else "idle"
                agree += own == act
            res["top_agree"][f"{m}_{h}"] = {"share": round(agree / max(1, n), 4), "n": n}
    # idle units: decisions where nothing clears the agent's floor (the agent leaves the call idle)
    byd = {}
    for r in rows:
        byd.setdefault(r["dk"], []).append(r)
    idle = [v for v in byd.values() if max(r["p"] for r in v) <= 0.003]
    res["idle"]["decisions"] = len(idle)
    res["idle"]["share_of_decisions"] = round(len(idle) / max(1, len(byd)), 4)
    for h in horizons:
        best = [max(act_of(r, h) for r in v) for v in idle]
        res["idle"][f"best_actual_net_{h}"] = round(float(np.mean(best)), 5) if best else None
        res["idle"][f"share_best_positive_{h}"] = round(float(np.mean([b > 0 for b in best])), 4) if best else None
        for a in ("rest", "see_friend", "work", "together", "spend_self"):
            xs = [r for v in idle for r in v if r["a"] == a]
            res["idle"][f"{a}_net_{h}"] = boot_mean(xs, lambda r, h=h: act_of(r, h)) if xs else None
    return res


def table(res, h=1, m="net"):
    lines = [f"| action | n | perceived | actual {m} {h}w | gap | rho | sign disagree |", "|---|---|---|---|---|---|---|"]
    for a, e in res["per_action"].items():
        p, y, g = e["perceived"], e[f"actual_{m}_{h}"], e[f"gap_net_{h}"]
        lines.append(f"| {a} | {e['n']} | {p['est']:+.4f} | {y['est']:+.4f} [{y['lo']:+.4f}, {y['hi']:+.4f}] | {g['est']:+.4f} | "
                     f"{e[f'rho_net_{h}'] if e[f'rho_net_{h}'] is None else round(e[f'rho_net_{h}'], 3)} | {e[f'sign_disagree_{h}']} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--harness", action="store_true")
    ap.add_argument("--first", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    if a.run:
        collect(MAIN, OUT / "rows.jsonl", a.workers)
    if a.harness:
        collect(HARNESS, OUT / "harness.jsonl", a.workers)
    if a.first:
        collect(FIRST, OUT / "first.jsonl", a.workers)
    if a.analyze:
        res = {}
        for name in ("rows", "harness", "first"):
            f = OUT / f"{name}.jsonl"
            if f.exists():
                res[name] = analyze(load(f))
                print(f"== {name}: {res[name]['decisions']} decisions, {res[name]['items']} items, applied {res[name]['applied_share']}")
                for h in VC.HORIZONS:
                    print(table(res[name], h))
                print(json.dumps({"overall": res[name]["overall"], "top": res[name]["top_agree"], "idle": res[name]["idle"]}, indent=1))
        (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
