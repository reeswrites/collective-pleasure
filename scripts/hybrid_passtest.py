"""Hybrid agent pass tests (docs/results/hybrid-agent-prereg.md). Scripted agents, no model calls.

PT-H, the held-out check: lived runs of the formation check's world (G-L0 and G-L4, the corrected rule: 52-week windows) under the hybrid
on the saturating scale with bills that hurt. Every big choice is also scored on AUDIT_M = 16 held-out futures, never used in the choice.
H1 calibration, H2 discrimination and H3 choice agreement compare the K-future forecast with the held-out value (bars in the prereg).
PT-R, the routine: scripts/value_consistency.py --hybrid (the one-week value check on the hybrid sample), read here against v2 on the
same sample (runs/value-consistency-v2-sat/rows.jsonl).

  uv run python scripts/hybrid_passtest.py --audit       PT-H runs (at most 3 workers); rows in runs/hybrid-passtest/
  uv run python scripts/hybrid_passtest.py --reach       free checks that every clause can fail (3 pairings, a planted bias)
  uv run python scripts/hybrid_passtest.py --analyze     both pass tests against their bars; writes runs/hybrid-passtest/analysis.json
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
import h38_pairing_run as H38  # noqa: E402
from mar import hybrid as HY  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402

OUT = ROOT / "runs" / "hybrid-passtest"
RULE = {"agent_values": "hybrid", "bills_hurt": True, "pleasure_scale": "sat", "decide_on": "pleasure", "decide_weeks": 52}
ARMS = {"G-L0": PR.dial(0), "G-L4": PR.dial(4)}
SAMPLE = {"pairs_every": 3, "seeds": (0,)}
BARS = {"H1": 0.010, "H1_ci": 0.015, "H2": 0.80, "H3": 0.80, "H3_margin": 0.010}


def play(arm, a, b, seed, bias=None, weeks=None):
    """One audited lived run. bias: an outside-option bias planted on every persona (the --reach check only)."""
    HY.AUDIT = []
    HY.STATS.update(futures=0, future_weeks=0, forks=0, choices=0)
    saved = None
    if bias is not None:
        ps = RT.personas()
        saved = {pid: dict(p.forecast) for pid, p in ps.items()}
        for p in ps.values():
            p.forecast = {"outside_bias": bias}
    t0 = time.time()
    try:
        run, lived, _ = H38.play(ARMS[arm], a, b, seed, stay=False, rule=RULE, **({"weeks": weeks} if weeks else {}))
    finally:
        if saved is not None:
            for pid, p in RT.personas().items():
                p.forecast = saved[pid]
    rec = {"arm": arm, "a": a, "b": b, "seed": seed, "bias": bias, "audit": HY.AUDIT, "stats": dict(HY.STATS), "secs": time.time() - t0,
           "both_share": float(np.mean([o["both_in"] for o in run.outcomes])), "term": lived.week0.get("term"),
           "formed0": lived.week0.get("formed"),
           "ended": not run.outcomes[-1]["both_in"] and any(o["both_in"] for o in run.outcomes)}
    HY.AUDIT = None
    return rec


def task(args):
    return play(*args)


A1 = {"pairs_every": 6, "seeds": (0,), "arms": ("G-L0",)}      # Amendment 1: a smaller PT-H rerun after the bill-mirror fix


def audit_run(workers=3, out=None, sample=None):
    out = out or OUT
    sample = sample or {**SAMPLE, "arms": tuple(ARMS)}
    out.mkdir(parents=True, exist_ok=True)
    f = out / "rows.jsonl"
    done = {(r["arm"], r["a"], r["b"], r["seed"]) for r in load(f)} if f.exists() else set()
    pairs = H38.pairings(H38.CONFIRM)[::sample["pairs_every"]]
    tasks = [(arm, a, b, s) for (a, b) in pairs for s in sample["seeds"] for arm in sample["arms"] if (arm, a, b, s) not in done]
    print(f"{len(tasks)} tasks, {min(3, workers)} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(min(3, workers)) as pool, f.open("a") as fh:
        for i, rec in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            if i % 5 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {rec['secs']:.0f}s wall {time.time() - t0:.0f}s", flush=True)


def load(f):
    return [json.loads(x) for x in Path(f).read_text().splitlines() if x.strip()]


# ---- the held-out clauses -------------------------------------------------------------------------------------------------------

def _units(recs):
    """Flatten the audit: one row per (choice, member). Status-quo entries without options are skipped (they are inside a choice)."""
    rows = []
    for rec in recs:
        cl = (rec["a"], rec["b"], rec["seed"])
        for e in rec["audit"]:
            if "options" not in e:
                continue
            for r in "AB":
                ch = e["chosen"][r] if isinstance(e["chosen"], dict) else e["chosen"]
                opts = {k: (v["F"][r], v["R"][r]) for k, v in e["options"].items()}
                rows.append({"cl": cl, "kind": e["kind"], "chosen": ch, "opts": opts})
    return rows


def _chosen_pair(u):
    """The (forecast, held-out) of the option the member's choice took. For a formation the household under its term, or the outside."""
    return u["opts"][u["chosen"]]


def boot_clustered(vals, cls, n=4000, seed=0):
    by = {}
    for v, c in zip(vals, cls):
        by.setdefault(c, []).append(v)
    keys = list(by)
    sums = np.array([sum(by[k]) for k in keys])
    cnts = np.array([len(by[k]) for k in keys])
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n):
        idx = rng.integers(0, len(keys), len(keys))
        bs.append(sums[idx].sum() / cnts[idx].sum())
    return float(np.mean(vals)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def _spearman(x, y):
    sys.path.insert(0, str(ROOT / "scripts"))
    import value_consistency as VCS
    return VCS.spearman(x, y)


def held_out(recs):
    units = _units(recs)
    if not units:
        return {"n": 0}
    d = [_chosen_pair(u)[0] - _chosen_pair(u)[1] for u in units]
    m, lo, hi = boot_clustered(d, [u["cl"] for u in units])
    F = [f for u in units for f, _ in u["opts"].values()]
    R = [r for u in units for _, r in u["opts"].values()]
    rho = _spearman(F, R)
    agree = []
    for u in units:
        if len(u["opts"]) < 2:
            continue
        best_r = max(u["opts"], key=lambda k: u["opts"][k][1])
        rs = sorted((v[1] for v in u["opts"].values()), reverse=True)
        if rs[0] - rs[1] >= BARS["H3_margin"]:
            best_f = max(u["opts"], key=lambda k: u["opts"][k][0])
            agree.append(best_f == best_r)
    h3 = float(np.mean(agree)) if agree else None
    by_kind = {}
    for u, x in zip(units, d):
        by_kind.setdefault(u["kind"], []).append(x)
    out = {"n_units": len(units), "n_choices_by_kind": {k: len(v) for k, v in by_kind.items()},
           "H1": {"mean": round(m, 5), "ci": [round(lo, 5), round(hi, 5)],
                  "holds": abs(m) <= BARS["H1"] and -BARS["H1_ci"] <= lo and hi <= BARS["H1_ci"]},
           "H1_by_kind": {k: round(float(np.mean(v)), 5) for k, v in by_kind.items()},
           "H2": {"rho": None if rho is None else round(rho, 4), "n": len(F), "holds": rho is not None and rho >= BARS["H2"]},
           "H3": {"share": None if h3 is None else round(h3, 4), "n": len(agree), "holds": h3 is not None and h3 >= BARS["H3"]}}
    out["verdict"] = "PASS" if all(out[k]["holds"] for k in ("H1", "H2", "H3")) else "FAIL"
    return out


def routine():
    """PT-R: the hybrid's one-week value check against v2 on the same pairings and seed, both on the saturating scale."""
    import value_consistency as VCS
    hf = ROOT / "runs" / "value-consistency-hybrid" / "rows.jsonl"
    vf = ROOT / "runs" / "value-consistency-v2-sat" / "rows.jsonl"
    if not hf.exists():
        return {"note": "no hybrid value-check rows yet"}
    hyb = VCS.load(hf)
    keep = {(r["a"], r["b"], r["seed"]) for r in hyb}
    ref = [r for r in VCS.load(vf) if (r["a"], r["b"], r["seed"]) in keep]
    ph, pv = VCS.passtest(hyb, "net"), VCS.passtest(ref, "net")
    hold = {t: ph[t] is not None and pv[t] is not None and ph[t] >= pv[t] - 0.02 for t in ("T1", "T2", "T3", "T4")}
    hold["T5"], hold["T6"] = ph["holds"]["T5"], ph["holds"]["T6"]
    return {"hybrid": ph, "v2_same_sample": pv, "holds": hold, "verdict": "PASS" if all(hold.values()) else "FAIL"}


def reach():
    """Free checks that each held-out clause can fail: a planted outside-option bias of +0.05 on every persona (H1 must fail), and the
    forecasts shuffled across units (H2 and H3 must fail). 3 pairings, G-L0, 78 weeks."""
    pairs = H38.pairings(H38.CONFIRM)[:3]
    recs = [play("G-L0", a, b, 0, bias=0.05, weeks=78) for a, b in pairs]
    res = {"bias": held_out(recs)}
    units = _units(recs)
    rng = np.random.default_rng(0)
    F = [f for u in units for f, _ in u["opts"].values()]
    perm = list(rng.permutation(len(F)))
    i = 0
    for rec in recs:
        for e in rec["audit"]:
            if "options" not in e:
                continue
            for v in e["options"].values():
                for r in "AB":
                    v["F"][r] = F[perm[i % len(F)]]
                    i += 1
    res["shuffled"] = held_out(recs)
    (OUT / "reach.json").parent.mkdir(parents=True, exist_ok=True)
    (OUT / "reach.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return res


def analyze(out=None):
    out = out or OUT
    recs = load(out / "rows.jsonl")
    res = {"PT-H": held_out(recs), "PT-R": routine(),
           "cost": {"runs": len(recs), "mean_secs": round(float(np.mean([r["secs"] for r in recs])), 1),
                    "mean_futures": round(float(np.mean([r["stats"]["futures"] for r in recs])), 1),
                    "mean_forks": round(float(np.mean([r["stats"]["forks"] for r in recs])), 2),
                    "note": "audited runs: every choice also plays 16 held-out futures, so these are dearer than an unaudited run"},
           "lives": {arm: {"both_share": round(float(np.mean([r["both_share"] for r in recs if r["arm"] == arm])), 4),
                           "terms": {t: sum(1 for r in recs if r["arm"] == arm and r["term"] == t) for t in HY.TERMS}} for arm in ARMS if any(r["arm"] == arm for r in recs)}}
    (out / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--reach", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--a1", action="store_true", help="Amendment 1: the smaller PT-H rerun; runs/hybrid-passtest-a1/")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    if a.a1:
        OUT_A1 = ROOT / "runs" / "hybrid-passtest-a1"
        if a.audit:
            audit_run(a.workers, OUT_A1, A1)
        if a.analyze:
            analyze(OUT_A1)
        sys.exit(0)
    if a.audit:
        audit_run(a.workers)
    if a.reach:
        reach()
    if a.analyze:
        analyze()
