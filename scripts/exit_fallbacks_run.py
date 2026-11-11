"""Exit no-deal fallbacks F0-F5, slice 1 (money pot only): docs/results/exit-fallbacks-prereg.md. Re-scores the frozen run-2 elites
and the author's seeds v2.2 and v2.3 under each arm. No evolution, no model calls. Wording rule: agents feel nothing; "pleasure" is
a gloss for a modeled hedonic state.

  uv run python scripts/exit_fallbacks_run.py --pilot      EXPLORATORY: training context, 4 candidates (never cited as a result)
  uv run python scripts/exit_fallbacks_run.py --run        the confirmatory run (val context, 18 candidates x 6 arms, at most 3 workers)
  uv run python scripts/exit_fallbacks_run.py --analyze    prereg vs actual; writes runs/exit-fallbacks/analysis.json

Per run, two plays of the same household (the world is deterministic given seed and rules, checked):
  A. world_api.hh_run_summary with levers on and liberty counting powers: exactly the scoring of household evolution run 2's
     validation (pleasure, fail, liberty, cooperation, s_non).
  B. a plain play with a weekly hook (no liberty): holdout leverage, the stay test's exit cost per partner, the F3 contest, the F5
     prenup term, net pleasure (pleasure - offsettable - non-offsettable suffering), both partners every week.
"""
import argparse
import dataclasses
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from mar import exit_fallback as EF  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import stay_test as ST  # noqa: E402
from mar import world_api as W  # noqa: E402
from mar.cards import load_cards  # noqa: E402
from mar.worlds import household as H  # noqa: E402

W.use_extra_deny(W.DENYLIST2)          # as household evolution run 2 (its validation context excludes the exam-2 personas)

OUT = ROOT / "runs" / "exit-fallbacks"
ELITES = ROOT / "docs" / "results" / "household-evolve-2-elites"
LEVERS = HD.LeverConfig(adapt=True, ritual=True, commit=True, network=True)
LIFETIME, VAL_SEED, VAL_RUNS = 156, 777, 30          # household evolution run 2's validation context
PILOT_SEED, PILOT_RUNS = 4242, 6                      # a TRAINING-split context, never the validation one
ARMS = EF.ARMS
SEEDS = ("author_seed_v2_bindable", "author_seed_v23_bindable")
WORKERS = 3


def candidates():
    out = [(n, str(H.RULES / n)) for n in SEEDS]
    out += [(f"r2-{d.name}", str(d)) for d in sorted(ELITES.glob("line-*"))]
    return out


def ctx(kind):
    if kind == "val":
        return W.make_context(VAL_SEED, 0, VAL_RUNS, split="val", tag="val", weeks=LIFETIME)
    return W.make_context(PILOT_SEED, 0, PILOT_RUNS, split="train", tag="pilot", weeks=LIFETIME)


def play_b(gate, hr):
    """Run B: the same household, plain, with the weekly measures. -> dict."""
    ps = W.hh_personas()
    cfg = dataclasses.replace(HD.DEFAULT, job_loss_rate=hr.rates[0], illness_rate=hr.rates[1], move_rate=hr.rates[2],
                              new_connection_rate=hr.rates[3], start=hr.start)
    lev, cost = [], {"big": [], "small": [], "big_pos": 0, "big_n": 0}

    pools = {}

    def hook(world, w):
        pools[w] = world.pool
        if not all(world.p[r]["in"] for r in "AB"):
            return
        h = EF.holdout_leverage(world, w)
        if h is not None:
            lev.append(h)
        mi = world.money_in
        if mi["A"] != mi["B"] and world.pool > 0:
            big = "A" if mi["A"] > mi["B"] else "B"
            for r, k in ((big, "big"), ("B" if big == "A" else "A", "small")):
                c = ST.exit_cost(world, r, w)
                cost[k].append(c["cost"] / world.pool)
                if k == "big":
                    cost["big_n"] += 1
                    cost["big_pos"] += c["cost"] > 1e-9

    def go():
        with HD.use_levers(LEVERS):
            wk = H.WeeklyWorld(gate, (ps[hr.a], ps[hr.b]), hr.seed, hr.weeks, cfg)
            wk.hook = hook
            run = wk.play()
        return wk, run
    wk, run = W._with_rates(hr.rates, go)
    out = run.outcomes
    pl = np.array([[o["hedonic"][r]["pleasure"] for r in "AB"] for o in out])
    so = np.array([[o["hedonic"][r]["s_off"] for r in "AB"] for o in out])
    sn = np.array([[o["hedonic"][r]["s_non"] for r in "AB"] for o in out])
    return {"pleasure_b": float(pl.mean()), "net": float((pl - so - sn).mean()), "s_off": float(so.mean()),
            "leverage": float(np.mean(lev)) if lev else None, "leverage_max": float(max(lev)) if lev else None,
            "cost_big": float(np.mean(cost["big"])) if cost["big"] else None,
            "cost_small": float(np.mean(cost["small"])) if cost["small"] else None,
            "big_held_share": cost["big_pos"] / cost["big_n"] if cost["big_n"] else None, "big_weeks": cost["big_n"],
            "exits": len(wk.exit_log), "exits_with_pot": sum(1 for e in wk.exit_log if pools.get(e["week"], 0) > 0), "contests": [c["how"] for c in wk.contest_log] + (["open"] if wk.contest else []),
            "prenup": getattr(wk, "prenup", None) and {k: wk.prenup[k] for k in ("status", "exit")},
            "formed": bool(wk.pot), "pool_end": float(wk.pool)}


def task(args):
    (label, path), arm, kind = args
    rows = []
    t0 = time.time()
    with EF.use_exit_fallback(arm):
        gate = H.PyGate(load_cards(path))
        for i, hr in enumerate(ctx(kind).runs):
            a = W.hh_run_summary(gate, hr, levers=LEVERS, powers=True)
            b = play_b(gate, hr)
            assert abs(a["pleasure"] - b["pleasure_b"]) < 1e-9, (label, arm, i, a["pleasure"], b["pleasure_b"])
            rows.append({"cand": label, "arm": arm, "run": i, "a": hr.a, "b": hr.b, **{k: a[k] for k in ("pleasure", "fail", "liberty",
                         "cooperation", "s_non", "left")}, **{k: v for k, v in b.items() if k != "pleasure_b"}})
    return label, arm, rows, time.time() - t0


def run(kind="val", cands=None, workers=WORKERS):
    workers = min(workers, 3)
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / ("rows.jsonl" if kind == "val" else "pilot.jsonl")
    done = set()
    if f.exists():
        for x in f.read_text().splitlines():
            r = json.loads(x)
            done.add((r["cand"], r["arm"]))
    cs = cands or candidates()
    tasks = [(c, a, kind) for c in cs for a in ARMS if (c[0], a) not in done]
    print(f"{len(tasks)} tasks ({kind}), {workers} workers", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as out:
        for i, (label, arm, rows, dt) in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            out.write("\n".join(json.dumps(r) for r in rows) + "\n")
            out.flush()
            print(f"  {i}/{len(tasks)} {label} {arm} {dt:.0f}s (wall {time.time() - t0:.0f}s)", flush=True)


def pilot():
    cs = [c for c in candidates() if c[0] in ("author_seed_v2_bindable", "r2-line-05", "r2-line-12", "r2-line-01")]
    run("pilot", cs)
    rows = [json.loads(x) for x in (OUT / "pilot.jsonl").read_text().splitlines()]
    summarize(rows, "PILOT (EXPLORATORY, training context; not a result)")


def by_arm(rows, key, cands=None):
    """-> {arm: per-run vector (mean over candidates within each run)}; None values dropped per run."""
    out = {}
    for arm in ARMS:
        rr = [r for r in rows if r["arm"] == arm and (cands is None or r["cand"] in cands)]
        runs = sorted({r["run"] for r in rr})
        v = []
        for i in runs:
            xs = [r[key] for r in rr if r["run"] == i and r[key] is not None]
            v.append(float(np.mean(xs)) if xs else np.nan)
        out[arm] = np.array(v)
    return out


def summarize(rows, title):
    print(title)
    for key in ("pleasure", "net", "s_non", "liberty", "leverage", "cost_big", "big_held_share"):
        v = by_arm(rows, key)
        print(f"  {key:15s} " + "  ".join(f"{a} {np.nanmean(v[a]):.4f}" for a in ARMS))
        if key in ("pleasure", "net"):
            for a in ARMS[1:]:
                d = v[a] - v["F0"]
                print(f"      {a}-F0 mean {np.nanmean(d):+.5f} sd {np.nanstd(d, ddof=1):.5f} (unit: run, n={np.sum(~np.isnan(d))})")
    f5 = [r["prenup"] for r in rows if r["arm"] == "F5"]
    print("  F5 prenup terms:", {k: sum(1 for p in f5 if p and p["exit"] == k) for k in ("equal_split", "proportional", "forfeit", None)})


NO_POWER = ("r2-line-01", "r2-line-03", "r2-line-04", "r2-line-08", "r2-line-10", "r2-line-11", "r2-line-12", "r2-line-13",
            "r2-line-14", "r2-line-16")         # the 10 run-2 elites that keep no commitment power (household-evolve-2.md)
SEED22 = "author_seed_v2_bindable"
LIB_MARGIN = 0.25                               # run 2's liberty margin (household_evolve2_run.MARGINS)


def _paired(d, seed=0):
    from mar import stats as S
    d = d[~np.isnan(d)]
    if len(d) == 0 or np.allclose(d, 0):
        return {"mean": float(np.mean(d)) if len(d) else None, "lo": 0.0, "hi": 0.0, "p": 1.0, "n": int(len(d))}
    ci = S.bootstrap_ci(d, np.mean, seed=seed)
    p = S.permutation_test(d, np.zeros_like(d), paired=True, alternative="two-sided")
    p = p.p if hasattr(p, "p") else p
    lo, hi = (ci.lo, ci.hi) if hasattr(ci, "lo") else (ci[1], ci[2])
    return {"mean": float(np.mean(d)), "lo": float(lo), "hi": float(hi), "p": float(p), "n": int(len(d))}


def analyze():
    from mar import stats as S
    rows = [json.loads(x) for x in (OUT / "rows.jsonl").read_text().splitlines() if x.strip()]
    cands = [c for c, _ in candidates()]
    assert len(rows) == len(cands) * len(ARMS) * VAL_RUNS, len(rows)
    man = json.loads((ELITES / "manifest.json").read_text())
    res = {"arms": {}, "P1": {}, "P2": {}, "P3": {}, "P4": {}, "P5": {}, "P6": {}, "checks": {}}
    cand_mean = lambda arm, c, k: float(np.nanmean([r[k] if r[k] is not None else np.nan for r in rows if r["arm"] == arm and r["cand"] == c]))
    # reproduction: F0 liberty of every elite equals the frozen manifest
    res["checks"]["F0_reproduces_manifest_liberty"] = all(abs(cand_mean("F0", f"r2-{l}", "liberty") - man["lines"][l]["val"]["liberty"]) < 1e-9
                                                          for l in man["lines"])
    res["checks"]["F0_reproduces_seed_liberty"] = abs(cand_mean("F0", SEED22, "liberty") - man["seeds_val"][SEED22]["liberty"]) < 1e-9
    for key in ("pleasure", "net", "s_non", "liberty", "leverage", "cost_big", "cost_small", "big_held_share"):
        v = by_arm(rows, key)
        res["arms"][key] = {a: float(np.nanmean(v[a])) for a in ARMS}
    # P1 pleasure vs F0, Holm over five arms
    v = by_arm(rows, "pleasure")
    tests = {a: _paired(v[a] - v["F0"]) for a in ARMS[1:]}
    adj = S.holm([tests[a]["p"] for a in ARMS[1:]])
    for a, h in zip(ARMS[1:], adj):
        tests[a]["p_holm"] = float(h)
    res["P1"] = tests
    vn = by_arm(rows, "net")
    res["P1_net"] = {a: _paired(vn[a] - vn["F0"]) for a in ARMS[1:]}
    # P2 liberty edge: median over the 16 elites of (elite - seed v2.2) liberty, per arm
    elites = [c for c in cands if c.startswith("r2-")]
    for a in ARMS:
        seed = cand_mean(a, SEED22, "liberty")
        d = [cand_mean(a, e, "liberty") - seed for e in elites]
        res["P2"][a] = {"median_edge": float(np.median(d)), "range": [float(min(d)), float(max(d))], "seed": seed}
    # P3 power-dropping elites beating the seed on liberty by more than the margin
    for a in ARMS:
        seed = cand_mean(a, SEED22, "liberty")
        res["P3"][a] = {"beat_liberty": sum(cand_mean(a, e, "liberty") - seed > LIB_MARGIN for e in NO_POWER),
                        "beat_pleasure": sum(cand_mean(a, e, "pleasure") - cand_mean(a, SEED22, "pleasure") > 0.02 for e in NO_POWER)}
    # P4 holdout leverage per arm (mean over runs of the candidate-mean); lowest arm
    lv = res["arms"]["leverage"]
    res["P4"] = {"by_arm": lv, "lowest": min(lv, key=lv.get), "F5_lowest": lv["F5"] <= min(lv[a] for a in ARMS if a != "F5"),
                 "F5_lowest_excl_F4": lv["F5"] <= min(lv[a] for a in ARMS if a not in ("F5", "F4"))}
    # P5 stay test, bigger contributor
    res["P5"] = {a: {"cost_big": res["arms"]["cost_big"][a], "held_share": res["arms"]["big_held_share"][a]} for a in ARMS}
    # P6 non-offsettable suffering vs F0
    vs = by_arm(rows, "s_non")
    res["P6"] = {a: _paired(vs[a] - vs["F0"]) for a in ARMS[1:]}
    # open cells and F3/F5 records
    res["open_cells"] = {a: sum(1 for r in rows if r["arm"] == a and r["exits_with_pot"]) for a in ARMS}   # runs where an exit met a non-empty pot
    res["contests"] = {}
    for r in rows:
        if r["arm"] == "F3":
            for h in r["contests"]:
                k = h.split("_")[0]
                res["contests"][k] = res["contests"].get(k, 0) + 1
    f5 = [r for r in rows if r["arm"] == "F5"]
    res["F5_terms"] = {str(k): sum(1 for r in f5 if (r["prenup"] or {}).get("exit") == k) for k in ("equal_split", "proportional", "forfeit", None)}
    res["F5_formed_share"] = sum(r["formed"] for r in f5) / len(f5)
    res["exits"] = {a: sum(r["exits"] for r in rows if r["arm"] == a) for a in ARMS}
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("pilot", "run", "analyze"):
        ap.add_argument(f"--{k}", action="store_true")
    a = ap.parse_args()
    if a.pilot:
        pilot()
    if a.run:
        run("val")
    if a.analyze:
        analyze()
