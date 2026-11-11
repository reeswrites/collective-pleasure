"""Seed v2 retest (docs/results/v2-retest-prereg.md; DRAFT until Amendment 1). Scripted persona agents, no model calls.

  uv run python scripts/v2_retest_run.py --checks                 manipulation checks M1, M3, M6, M9 (M2, M5, M8, M10 are tests/counts)
  uv run python scripts/v2_retest_run.py --pilot                  EXPLORATORY pilot: seeds 900-902, 40 pairings, five arms + BASE-0i
  uv run python scripts/v2_retest_run.py --power                  power check from the pilot (for Amendment 1)
  uv run python scripts/v2_retest_run.py --run --pairs N --seeds S   confirmatory arms, then descriptive arms on 40 pairings
  uv run python scripts/v2_retest_run.py --stay --seeds S          S5: stay test (behavioral lens) on the 40-pairing cohort
  uv run python scripts/v2_retest_run.py --analyze                 predictions P1-P4, S1-S6, descriptive C1-C9, checks M4, M7, M10

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar import stats as S  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "v2-retest"
PILOT_SEEDS = (900, 901, 902)
PILOT_ARMS = ("BASE-F", "V22-F", "V23-F", "BASE-0", "V22-0", "BASE-0i")
SAMPLE_SEED, DESC_SEED, PILOT_SAMPLE_SEED = 20261111, 901, 900


def task(args):
    arm, a, b, seed = args
    run, lived, world = RT.play_cell(arm, a, b, seed)
    rec = RT.metrics(run, lived, world)
    rec["gap"] = RT.gains_gap(run, lived)
    rec.update(arm=arm, a=a, b=b, seed=seed)
    return rec


def stay_task(args):
    from mar import stay_test as ST
    arm, a, b, seed = args
    run, lived, world, weeks = RT.play_cell(arm, a, b, seed, stay=True)
    summ = ST.run_summary(weeks)
    return {"arm": arm, "a": a, "b": b, "seed": seed, "staying_weeks": summ["staying_weeks"], "held_weeks": summ["held_weeks"],
            "worth_weeks": summ["worth_weeks"]}


def run_tasks(fn, tasks, workers=4, tag=""):
    t0, out = time.time(), []
    with Pool(workers) as pool:
        for i, r in enumerate(pool.imap_unordered(fn, tasks, chunksize=2)):
            out.append(r)
            if (i + 1) % 200 == 0:
                print(f"  {tag} {i + 1}/{len(tasks)} {time.time() - t0:.0f}s", flush=True)
    print(f"{tag}: {len(out)} runs in {time.time() - t0:.0f}s", flush=True)
    return out


def save(rows, name):
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT / name, "wt") as f:
        json.dump(rows, f, default=str)


def load(name):
    with gzip.open(OUT / name, "rt") as f:
        return json.load(f)


# ---- pairing-level helpers ---------------------------------------------------------------------------------------------------

def pm(rows, arm, key="pl", pairs=None, sub=None):
    """{(a, b): mean over seeds of rows[key]} for one arm."""
    d = {}
    for r in rows:
        if r["arm"] == arm and (pairs is None or (r["a"], r["b"]) in pairs):
            v = r[key] if sub is None else (r.get(key) or {}).get(sub)
            if v is not None:
                d.setdefault((r["a"], r["b"]), []).append(v)
    return {k: float(np.mean(v)) for k, v in d.items()}


def paired(x, y):
    ks = sorted(set(x) & set(y))
    return np.array([x[k] for k in ks]), np.array([y[k] for k in ks]), ks


def dtest(pid, quantity, xa, ya, alternative="greater", n_boot=4000):
    x, y, ks = paired(xa, ya)
    if len(ks) < 3:
        return {"id": pid, "quantity": quantity, "n": len(ks), "note": "fewer than 3 pairings"}
    d = x - y
    t = S.permutation_test(x, y, paired=True, alternative=alternative, seed=0)
    ci = S.bootstrap_diff_ci(x, y, paired=True, seed=0)
    sd = float(d.std(ddof=1)) if len(d) > 1 else 0.0
    return {"id": pid, "quantity": quantity, "n": len(ks), "est": float(d.mean()), "lo": float(ci.lo), "hi": float(ci.hi),
            "p": float(t.p), "dz": float(d.mean() / sd) if sd > 0 else None, "sd": sd, "pos_share": float((d > 0).mean())}


def holm(rows):
    ok = [r for r in rows if "p" in r]
    ps = [r["p"] for r in ok]
    adj = S.holm(ps) if ps else []
    for r, a in zip(ok, adj):
        r["p_holm"] = float(a)
    return rows


def label(r, direction=+1):
    if "p_holm" not in r:
        return "not testable"
    lo, hi = (r["lo"], r["hi"]) if direction > 0 else (-r["hi"], -r["lo"])
    est = r["est"] * direction
    if r["p_holm"] < 0.05 and est > 0 and lo > 0:
        return "holds robustly"
    if r["p_holm"] < 0.05 and est > 0:
        return "weak support"
    if est > 0:
        return "not shown (point on the predicted side)"
    return "miss"


# ---- manipulation checks -------------------------------------------------------------------------------------------------------

def m1_task(args):
    variant, a, b, seed, cohort = args
    fx = HD.FixConfig(contact=True, contact_motive=(cohort == "hand"))
    ps = {**RT.personas(), **{p.id: p for p in RT.P.load_dir(ROOT / "personas" / "pressing")}}
    with HD.use_levers(RT.LEVERS):
        run = H.run_weekly(H.load_variant(variant), (ps[a], ps[b]), seed, fixes=fx)
    pl = {k: float(np.mean([o["hedonic"][k]["pleasure"] for o in run.outcomes])) for k in "AB"}
    return {"variant": variant, "a": a, "b": b, "seed": seed, "cohort": cohort, "pl": pl,
            "sig": __import__("hashlib").sha256(json.dumps(run.outcomes, sort_keys=True, default=str).encode()).hexdigest()}


def m3_task(args):
    from mar import fidelity as FID
    a, b, seed = args
    ps = RT.personas()
    NG._RC.clear(); NG._PC.clear()
    with HD.use_levers(RT.LEVERS), HD.use_fixes(HD.FixConfig(contact=True, valued_money=True, real_outside=True, nash_terms=True)):
        r = FID.p1a_one(ps[a], ps[b], seed, NG.base_cards(RT.V22))
    return {"a": a, "b": b, "seed": seed, "r": r}


def checks(workers):
    hand = RT.hand_ids()
    hp = [(a, b) for a, b in RT.population() if a in hand and b in hand]
    tasks = [(v, a, b, s, "hand") for v in ("trap", "contact_free") for a, b in hp for s in range(3)]
    ctrl = "p-controller"
    tasks += [(v, ctrl, h, s, "controller") for v in ("trap", "contact_free") for h in hand for s in range(3)]
    tasks += [(v, h, ctrl, s, "controller") for v in ("trap", "contact_free") for h in hand for s in range(3)]
    m1 = run_tasks(m1_task, tasks, workers, "M1")
    by = {}
    for r in m1:
        by.setdefault((r["cohort"], r["a"], r["b"], r["seed"]), {})[r["variant"]] = r
    res = {}
    for cohort in ("hand", "controller"):
        cells = [v for k, v in by.items() if k[0] == cohort and len(v) == 2]
        differ = sum(1 for v in cells if v["trap"]["sig"] != v["contact_free"]["sig"])
        # the restricted partner: the one who is not the requester. Hand cohort: T2 binds Partner B (the lower earner); controller
        # cohort: the controller's partner (a controller vetoes and requests; as Partner A its requests also bind through T2)
        def restricted(v):
            r0 = v["trap"]
            return "B" if cohort == "hand" else ("B" if r0["a"] == "p-controller" else "A")
        dB = [v["trap"]["pl"][restricted(v)] - v["contact_free"]["pl"][restricted(v)] for v in cells]
        res[cohort] = {"cells": len(cells), "differ": differ, "mean_restricted_trap_minus_free": float(np.mean(dB)) if dB else None}
    m3 = run_tasks(m3_task, [(a, b, s) for a, b in hp for s in range(5)], workers, "M3")
    pairs = {}
    for r in m3:
        if r["r"] is not None:
            pairs.setdefault((r["a"], r["b"]), []).append(r["r"][1] - r["r"][0])
    diffs = np.array([np.mean(v) for v in pairs.values()]) if pairs else np.array([])
    ci = S.bootstrap_ci(diffs, seed=0) if len(diffs) > 2 else None
    res["M3"] = {"pairings_formed": len(pairs), "pair_seeds_formed": sum(1 for r in m3 if r["r"] is not None), "pair_seeds": len(m3),
                 "est": float(diffs.mean()) if len(diffs) else None, "lo": float(ci.lo) if ci else None, "hi": float(ci.hi) if ci else None,
                 "pass": bool(len(diffs) and diffs.mean() >= 0.02)}
    res["M1_pass"] = all(res[c]["differ"] > 0 and (res[c]["mean_restricted_trap_minus_free"] or 0) < 0 for c in ("hand", "controller"))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "checks.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


# ---- pilot and power -----------------------------------------------------------------------------------------------------------

def pilot(workers):
    pairs = RT.sample(25, PILOT_SAMPLE_SEED)
    tasks = [(arm, a, b, s) for arm in PILOT_ARMS for a, b in pairs for s in PILOT_SEEDS]
    t0 = time.time()
    rows = run_tasks(task, tasks, workers, "pilot")
    save(rows, "pilot.json.gz")
    print(f"pilot wall {time.time() - t0:.0f}s for {len(tasks)} runs")


def power():
    rows = load("pilot.json.gz")
    out = {}
    for name, x, y in (("P1 V22-F - BASE-F", "V22-F", "BASE-F"), ("P2 V23-F - BASE-F", "V23-F", "BASE-F"),
                       ("P3 V23-F - V22-F", "V23-F", "V22-F"), ("V22-0 - BASE-0", "V22-0", "BASE-0")):
        for key in ("pl", "net"):
            xa, ya, ks = paired(pm(rows, x, key), pm(rows, y, key))
            d = xa - ya
            sd = float(d.std(ddof=1))
            seed_sd = float(np.mean([np.std([r[key] for r in rows if r["arm"] == x and (r["a"], r["b"]) == k], ddof=1) for k in ks]))
            n_sim = S.seeds_for_power(0.010, sd, target=0.8, alpha=0.05, paired=True, alternative="greater", n_max=1024, n_sim=200)
            n_cf = S.seeds_for_margin(sd, 0.010)
            out[f"{name} [{key}]"] = {"pilot_effect": float(d.mean()), "sd_pairing_diff": sd, "seed_sd_per_run": seed_sd,
                                      "n_for_0.010_sim": n_sim, "n_for_0.010_closed_two_sided": n_cf, "n_pairings": len(ks)}
    for arm in PILOT_ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        out[f"formed0 share {arm}"] = float(np.mean([r["formed0"] for r in rs]))
        out[f"both_share {arm}"] = float(np.mean([r["both_share"] for r in rs]))
    (OUT / "power.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


# ---- confirmatory run ------------------------------------------------------------------------------------------------------------

def confirm(n_pairs, seeds, workers, desc=True):
    pairs = RT.sample(n_pairs - 15, SAMPLE_SEED)
    tasks = [(arm, a, b, s) for arm in RT.CONFIRM_ARMS for a, b in pairs for s in range(seeds)]
    save(run_tasks(task, tasks, workers, "confirm"), "confirm.json.gz")
    if desc:
        dp = RT.sample(25, DESC_SEED)
        dt = [(arm, a, b, s) for arm in RT.DESCRIPTIVE_ARMS for a, b in dp for s in range(seeds)]
        dt += [(arm, a, b, s) for arm in RT.CONFIRM_ARMS for a, b in dp if (a, b) not in set(pairs) for s in range(seeds)]
        save(run_tasks(task, dt, workers, "descriptive"), "descriptive.json.gz")


def stay(seeds, workers):
    dp = RT.sample(25, DESC_SEED)
    tasks = [(arm, a, b, s) for arm in ("V22-F", "BASE-F") for a, b in dp for s in range(seeds)]
    save(run_tasks(stay_task, tasks, workers, "stay"), "stay.json.gz")


# ---- analysis --------------------------------------------------------------------------------------------------------------------

def analyze():
    rows = load("confirm.json.gz")
    drows = load("descriptive.json.gz") if (OUT / "descriptive.json.gz").exists() else []
    allr = rows + drows
    A = {}
    prim = [dtest("P1", "V22-F - BASE-F, mean pleasure", pm(rows, "V22-F"), pm(rows, "BASE-F")),
            dtest("P2", "V23-F - BASE-F, mean pleasure", pm(rows, "V23-F"), pm(rows, "BASE-F")),
            dtest("P3", "V23-F - V22-F, mean pleasure", pm(rows, "V23-F"), pm(rows, "V22-F"))]
    x, y, ks = paired(pm(rows, "V22-F"), pm(rows, "BASE-F"))
    x0, y0, ks0 = paired(pm(rows, "V22-0"), pm(rows, "BASE-0"))
    gF = dict(zip(ks, x - y)); g0 = dict(zip(ks0, x0 - y0))
    prim.append(dtest("P4", "D(V22-F) - D(V22-0), mean pleasure", gF, g0))
    A["primary"] = holm(prim)
    for r in A["primary"]:
        r["label"] = label(r)
    sec = [dtest("S1", "V22-F - BASE-F, net wellbeing", pm(rows, "V22-F", "net"), pm(rows, "BASE-F", "net")),
           dtest("S2", "V23-F - BASE-F, net wellbeing", pm(rows, "V23-F", "net"), pm(rows, "BASE-F", "net")),
           dtest("S3", "non-offsettable suffering, V22-F - BASE-F (a rise is the finding)", pm(rows, "V22-F", "snon"), pm(rows, "BASE-F", "snon")),
           dtest("S4", "non-offsettable suffering, V23-F - BASE-F (a rise is the finding)", pm(rows, "V23-F", "snon"), pm(rows, "BASE-F", "snon"))]
    if (OUT / "stay.json.gz").exists():
        st = load("stay.json.gz")
        def share(arm):
            d = {}
            for r in st:
                if r["arm"] == arm:
                    k = (r["a"], r["b"])
                    d.setdefault(k, [0, 0]); d[k][0] += r["worth_weeks"]; d[k][1] += r["staying_weeks"]
            return {k: v[0] / v[1] for k, v in d.items() if v[1] > 0}
        sec.append(dtest("S5", "stay-worth-it share, V22-F - BASE-F (40-pairing cohort)", share("V22-F"), share("BASE-F")))
    slid = lambda arm: {k: v for k, v in _slid_share(allr, arm).items()}
    sec.append(dtest("S6", "slid-into share, V23-F - V22-F", slid("V23-F"), slid("V22-F"), alternative="less"))
    A["secondary"] = holm(sec)
    for r in A["secondary"]:
        r["label"] = label(r, -1 if r["id"] == "S6" else +1)
    hand = set(RT.hand_ids())
    hp = {k for k in pm(rows, "V22-0") if k[0] in hand and k[1] in hand}
    C = {}
    C["C1"] = dtest("C1", "V22-0 - BASE-0i, mean pleasure, hand pairings (pleasure-levers H1 was -0.019)", pm(rows, "V22-0", pairs=hp), pm(rows, "BASE-0i", pairs=hp))
    C["C2"] = {k: dtest("C2", f"BASE-0 - BASE-0i, {k}", pm(rows, "BASE-0", k), pm(rows, "BASE-0i", k)) for k in ("pl", "net")}
    C["C3"] = {arm: 1.0 - float(np.mean([r["formed0"] for r in rows if r["arm"] == arm])) for arm in RT.CONFIRM_ARMS}
    C["C3_both_share"] = {arm: float(np.mean([r["both_share"] for r in rows if r["arm"] == arm])) for arm in RT.CONFIRM_ARMS}
    C["C3_ended"] = {arm: float(np.mean([r["ended"] for r in rows if r["arm"] == arm])) for arm in RT.CONFIRM_ARMS}
    C["C4"] = {arm: {"pl": _mean(allr, arm, "pl"), "net": _mean(allr, arm, "net"), "leaves": _mean(allr, arm, "leaves"),
                     "trust_min": _mean_trust(allr, arm)} for arm in ("V23-F", "V23-F-actions", "V23-F-words")}
    C["C5"] = {}
    dpairs = set(tuple(p) for p in RT.sample(25, DESC_SEED))
    for arm in RT.DESCRIPTIVE_ARMS:
        if arm.startswith(("V22-F-no", "BASE-F-no", "V23-F-noUL")):
            ref = "V22-F" if arm.startswith("V22") else ("BASE-F" if arm.startswith("BASE") else "V23-F")
            C["C5"][arm] = dtest("C5", f"{arm} - {ref}, mean pleasure", pm(allr, arm, pairs=dpairs), pm(allr, ref, pairs=dpairs))
    C["C6"] = {pid: dtest(pid, f"{pid} on the 15 hand pairings", pm(rows, x1, pairs=hp), pm(rows, y1, pairs=hp))
               for pid, x1, y1 in (("P1", "V22-F", "BASE-F"), ("P2", "V23-F", "BASE-F"))}
    C["C7"] = {arm: _mean(rows, arm, "gap") for arm in RT.CONFIRM_ARMS}
    formed = lambda arm: {(r["a"], r["b"], r["seed"]) for r in rows if r["arm"] == arm and r["both_share"] > 0.9}
    C["C8"] = {}
    for pid, x1, y1 in (("P1", "V22-F", "BASE-F"), ("P2", "V23-F", "BASE-F"), ("P3", "V23-F", "V22-F")):
        keep = formed(x1) & formed(y1)
        sel = [r for r in rows if (r["a"], r["b"], r["seed"]) in keep]
        for k in ("pl", "net"):
            C["C8"][f"{pid} {k}"] = {**dtest(pid, f"{x1} - {y1}, formed both (>90% of weeks together), {k}", pm(sel, x1, k), pm(sel, y1, k)),
                                     "share_kept": len(keep) / max(1, len({(r['a'], r['b'], r['seed']) for r in rows if r['arm'] == x1}))}
    C["C9"] = {arm: {"forbidden_weeks": int(sum((r.get("diag") or {}).get("menu_forbidden_weeks", 0) for r in rows if r["arm"] == arm)),
                     "pairings_with_any": len({(r["a"], r["b"]) for r in rows if r["arm"] == arm and (r.get("diag") or {}).get("menu_forbidden_weeks", 0)})}
               for arm in ("BASE-0", "V22-0", "BASE-0i")}
    A["descriptive"] = C
    M = {}
    M["M4"] = {arm: {"fine_runs": sum(1 for r in rows if r["arm"] == arm and (r.get("fix") or {}).get("fine_amount")),
                     "bundle_fine_runs": sum(1 for r in rows if r["arm"] == arm and (r.get("bundle") or {}).get("fine", "none") != "none")}
               for arm in ("BASE-F", "V22-F", "V23-F")}
    skips = [(r["a"], r["b"], r["seed"]) for r in rows if r["arm"] == "V23-F" and (r.get("fix") or {}).get("skip_leaves")]
    sk = [x for r in rows if r["arm"] == "V23-F" for x in r.get("skip_N", [])]
    M["M7"] = {"v23_runs_with_skip_leaves": len(skips), "skip_leaves": len(sk), "skip_below_skip_n": sum(1 for x in sk if x < HD.FixConfig().skip_n),
               "ladder_leaves": int(sum((r.get("fix") or {}).get("ladder_leaves", 0) for r in rows if r["arm"] == "V23-F"))}
    M["M9"] = {arm: int(sum((r.get("fix") or {}).get("bar_leaves", 0) for r in rows if r["arm"] == arm)) for arm in ("BASE-F", "V22-F", "V23-F")}
    M["M10"] = {arm: int(sum((r.get("diag") or {}).get("menu_forbidden_weeks", 0) for r in rows if r["arm"] == arm)) for arm in ("BASE-F", "V22-F", "V23-F")}
    A["checks"] = M
    A["means"] = {arm: {k: _mean(allr, arm, k) for k in ("pl", "net", "snon", "snon_share", "both_share")} for arm in RT.ALL_ARMS}
    A["n_pairings"] = len({(r["a"], r["b"]) for r in rows})
    A["seeds"] = sorted({r["seed"] for r in rows})
    (OUT / "analysis.json").write_text(json.dumps(A, indent=1, default=str))
    for r in A["primary"] + A["secondary"]:
        print(f"{r['id']:3s} {r['quantity'][:70]:70s} est {r.get('est', float('nan')):+.4f} [{r.get('lo', float('nan')):+.4f}, {r.get('hi', float('nan')):+.4f}] "
              f"p_holm {r.get('p_holm', float('nan')):.4f} n {r['n']} {r.get('label')}")
    print(json.dumps({k: A[k] for k in ("checks", "means", "n_pairings", "seeds")}, indent=1, default=str)[:4000])


def _mean(rows, arm, key):
    v = [r[key] for r in rows if r["arm"] == arm and r.get(key) is not None]
    return float(np.mean(v)) if v else None


def _mean_trust(rows, arm):
    v = [min(r["trust"].values()) for r in rows if r["arm"] == arm and r.get("trust")]
    return float(np.mean(v)) if v else None


def _slid_share(rows, arm):
    d = {}
    for r in rows:
        if r["arm"] == arm and r.get("slid") and r["slid"]["assessed"]:
            k = (r["a"], r["b"])
            d.setdefault(k, [0, 0]); d[k][0] += r["slid"]["slid"]; d[k][1] += r["slid"]["assessed"]
    return {k: v[0] / v[1] for k, v in d.items()}


def main():
    ap = argparse.ArgumentParser()
    for f in ("checks", "pilot", "power", "run", "stay", "analyze"):
        ap.add_argument(f"--{f}", action="store_true")
    ap.add_argument("--pairs", type=int, default=120)
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-desc", action="store_true")
    a = ap.parse_args()
    if a.checks:
        checks(a.workers)
    if a.pilot:
        pilot(a.workers)
    if a.power:
        power()
    if a.run:
        confirm(a.pairs, a.seeds, a.workers, desc=not a.no_desc)
    if a.stay:
        stay(a.seeds, a.workers)
    if a.analyze:
        analyze()


if __name__ == "__main__":
    main()
