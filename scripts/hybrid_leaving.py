"""How the hybrid decides to leave (docs/results/hybrid-leaving-prereg.md; hybrid prereg Amendment 5). Scripted persona agents, no model
calls. Wording rule: agents feel nothing; "pleasure", "suffering", "tally" and "forecast" are glosses for modeled numbers.

  uv run python scripts/hybrid_leaving.py --paths            slice (b): lived exit paths and the outside-forecast error (A4 on B, trial,
                                                             P2; old on B); runs/hybrid-leaving/paths-<version>.jsonl
  uv run python scripts/hybrid_leaving.py --paths-analyze    slice (b) tables -> runs/hybrid-leaving/paths.json
  uv run python scripts/hybrid_leaving.py --reach            "Can every verdict happen?" (synthetic exits, three-version labels, P-AUTH)
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
import h41_choice_aids as A  # noqa: E402
import hybrid_exit_option as XO  # noqa: E402
from mar import makers as MK  # noqa: E402
from mar import retest as RT  # noqa: E402

OUT = ROOT / "runs" / "hybrid-leaving"
WORKERS = 4
WIN = 13            # the two windows a path compares (weeks)
FLAT = 0.25         # quiet path: weighted suffering moved by at most this share of the pleasure fall (ASSUMED, prereg)
POST_MAX, POST_MIN = 52, 13


# ---- slice (b): how lived exits come about ------------------------------------------------------------------------------------

def in_flags(run, lone):
    """Per week, the set of roles in the household: both (both_in), the one alone (lone), or none."""
    out = []
    for o, x in zip(run.outcomes, lone):
        out.append({"A", "B"} if o["both_in"] else ({x[0]} if x is not None else set()))
    return out


def ys(run, role, w):
    """The leaver's weekly yardstick, pleasure and suffering (both kinds)."""
    h = [o["hedonic"][role] for o in run.outcomes]
    p = [x["pleasure"] for x in h]
    s = [x["s_off"] + x["s_non"] for x in h]
    so = [x["s_off"] for x in h]
    sn = [x["s_non"] for x in h]
    return p, s, so, sn, [a - w * b for a, b in zip(p, s)]


def classify(p, s, w, early, late):
    """slice (b)'s classes from mean pleasure and suffering in two windows (lists of week indices)."""
    dp = float(np.mean([p[i] for i in late]) - np.mean([p[i] for i in early]))
    ds = float(np.mean([s[i] for i in late]) - np.mean([s[i] for i in early]))
    cp, cs = -dp, w * ds
    if cp + cs <= 0:
        c = "no_fall"
    elif cs >= cp:
        c = "suffering"
    elif abs(cs) <= FLAT * cp:
        c = "quiet"
    else:
        c = "mixed"
    return c, {"dp": round(dp, 6), "ds": round(ds, 6), "cp": round(cp, 6), "cs": round(cs, 6)}


def exit_paths(run, lived, lone, events, weights):
    """One record per lived exit: classes under both window pairs, the partner's class, the outside-forecast error."""
    flags = in_flags(run, lone)
    n = len(run.outcomes)
    why = {}
    for wk, r, ev in events:
        if isinstance(ev, str) and ev.startswith("leave_"):
            why[(wk, r)] = ev[6:]
    pair_log = list(lived.log)
    lone_log = list(getattr(lived.world, "lone_log", []))
    out = []
    for e in run.exits:
        wk, r = e["week"], e["role"]
        q = "B" if r == "A" else "A"
        start = wk
        while start > 0 and r in flags[start - 1]:
            start -= 1
        rec = {"week": wk, "role": r, "why": why.get((wk, r)), "spell_start": start, "spell": wk - start, "w": weights[r]}
        p, s, so, sn, y = ys(run, r, weights[r])
        late = list(range(wk - WIN, wk))
        if wk - start >= 2 * WIN:
            rec["primary"], rec["primary_d"] = classify(p, s, weights[r], list(range(start, start + WIN)), late)
            rec["second"], rec["second_d"] = classify(p, s, weights[r], list(range(wk - 2 * WIN, wk - WIN)), late)
            rec["kinds"] = {"s_off": round(float(np.mean([so[i] for i in late]) - np.mean([so[i] for i in range(start, start + WIN)])), 6),
                            "s_non": round(float(np.mean([sn[i] for i in late]) - np.mean([sn[i] for i in range(start, start + WIN)])), 6)}
            pp, ps_, _, _, _ = ys(run, q, weights[q])
            rec["partner"], _ = classify(pp, ps_, weights[q], list(range(start, start + WIN)), late)
        else:
            rec["primary"] = rec["second"] = "short_spell"
        # outside-forecast error: the deciding reading's O against the life lived after the exit
        cands = [(x["week"], x["outside"][r]) for x in pair_log if x["week"] <= wk] + \
                [(x["week"], x["out"]) for x in lone_log if x["role"] == r and x["week"] <= wk]
        if cands:
            rw, O = max(cands, key=lambda t: t[0])
            post = list(range(wk + 1, min(n, wk + 1 + POST_MAX)))
            rec["reading_week"], rec["O"] = rw, round(O, 6)
            if len(post) >= POST_MIN:
                L = float(np.mean([y[i] for i in post]))
                rec["L"], rec["err"], rec["post_weeks"] = round(L, 6), round(L - O, 6), len(post)
        out.append(rec)
    return out


def path_task(args):
    arm, a, b, seed, version = args
    t0 = time.time()
    run, lived, rd, ex = XO.play(arm, a, b, seed, version)
    ps = RT.personas()
    weights = {"A": MK.suffering_weight(ps[a]), "B": MK.suffering_weight(ps[b])}
    events = run.fix.get("events", []) if isinstance(run.fix, dict) else []
    return {"g": arm, "a": a, "b": b, "seed": seed, "version": version, "exits": exit_paths(run, lived, ex["lone"], events, weights),
            "both_share": float(np.mean([o["both_in"] for o in run.outcomes])), "secs": round(time.time() - t0, 1)}


PATH_RUNS = (("new", ("B", "trial", "P2")), ("old", ("B",)))      # "new" is A4 here (hybrid_exit_option.VERSIONS)


def paths(workers=WORKERS):
    OUT.mkdir(parents=True, exist_ok=True)
    for version, arms in PATH_RUNS:
        f = OUT / f"paths-{'a4' if version == 'new' else version}.jsonl"
        done = {(r["g"], r["a"], r["b"]) for r in A.load(f)} if f.exists() else set()
        tasks = [(arm, a, b, s, version) for (a, b) in A.pairings(A.CONFIRM) for arm in arms for s in A.CONFIRM["seeds"]
                 if (arm, a, b) not in done]
        print(f"{version}: {len(tasks)} tasks -> {f}", flush=True)
        t0 = time.time()
        with Pool(min(workers, 4)) as pool, f.open("a") as fh:
            for i, rec in enumerate(pool.imap_unordered(path_task, tasks, chunksize=1), 1):
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                if i % 40 == 0 or i == len(tasks):
                    print(f"  {i}/{len(tasks)} wall {time.time() - t0:.0f}s", flush=True)


CLASSES = ("suffering", "quiet", "mixed", "no_fall", "short_spell")


def boot_mean(vals, groups, n=2000, seed=0):
    """Mean and a 95% bootstrap interval resampling groups (pairings)."""
    if not vals:
        return None
    by = {}
    for v, g in zip(vals, groups):
        by.setdefault(g, []).append(v)
    keys = list(by)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n):
        pick = [keys[i] for i in rng.integers(0, len(keys), len(keys))]
        xs = [v for k in pick for v in by[k]]
        bs.append(float(np.mean(xs)))
    return {"mean": float(np.mean(vals)), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "n": len(vals)}


def path_table(rows):
    ex = [(r, e) for r in rows for e in r["exits"]]
    t = {"runs": len(rows), "exits": len(ex), "by_why": {}}
    for key in ("primary", "second"):
        t[key] = {c: sum(1 for _, e in ex if e[key] == c) for c in CLASSES}
    for _, e in ex:
        t["by_why"][str(e["why"])] = t["by_why"].get(str(e["why"]), 0) + 1
    t["partner"] = {c: sum(1 for _, e in ex if e.get("partner") == c) for c in CLASSES}
    suf = [e for _, e in ex if e["primary"] == "suffering"]
    t["suffering_kinds"] = {"s_off_up": sum(1 for e in suf if e["kinds"]["s_off"] > 0), "s_non_up": sum(1 for e in suf if e["kinds"]["s_non"] > 0),
                            "n": len(suf)}
    err = [(e["err"], (r["a"], r["b"])) for r, e in ex if "err" in e and e["why"] == "bar"]
    t["outside_error_bar"] = boot_mean([x for x, _ in err], [g for _, g in err])
    err_all = [(e["err"], (r["a"], r["b"])) for r, e in ex if "err" in e]
    t["outside_error_all"] = boot_mean([x for x, _ in err_all], [g for _, g in err_all])
    t["worst_errors"] = sorted(([round(e["err"], 3), r["g"], r["a"], r["b"], e["week"], e["role"], e["why"]] for r, e in ex if "err" in e),
                               key=lambda x: x[0])[:5]
    return t


def paths_analyze():
    res = {}
    for f in sorted(OUT.glob("paths-*.jsonl")):
        rows = A.load(f)
        v = f.stem.split("-", 1)[1]
        for arm in sorted({r["g"] for r in rows}):
            res[f"{v}:{arm}"] = path_table([r for r in rows if r["g"] == arm])
    (OUT / "paths.json").write_text(json.dumps(res, indent=1))
    for k, t in res.items():
        print(k, "exits", t["exits"], "why", t["by_why"])
        print("   primary", t["primary"])
        print("   second ", t["second"])
        print("   partner", t["partner"], "suffering kinds", t["suffering_kinds"])
        print("   outside error (bar exits)", t["outside_error_bar"], " all", t["outside_error_all"])
        print("   worst", t["worst_errors"])
    return res


# ---- can every verdict happen? -------------------------------------------------------------------------------------------------

def reach():
    res = {}
    # step-5 classes: a planted suffering rise, a planted pleasure fade at flat suffering, a flat life
    p = [0.9] * 26 + [0.9] * 13
    s_up = [0.0] * 26 + [0.2] * 13
    res["suffering"] = classify(p, s_up, 1.0, list(range(13)), list(range(26, 39)))[0]
    p_fade = [0.9] * 26 + [0.8] * 13
    res["quiet"] = classify(p_fade, [0.0] * 39, 1.0, list(range(13)), list(range(26, 39)))[0]
    res["mixed"] = classify(p_fade, [0.0] * 26 + [0.05] * 13, 1.0, list(range(13)), list(range(26, 39)))[0]
    res["no_fall"] = classify(p, [0.0] * 39, 1.0, list(range(13)), list(range(26, 39)))[0]
    assert res == {"suffering": "suffering", "quiet": "quiet", "mixed": "mixed", "no_fall": "no_fall"}, res
    print("step-5 classes reachable:", res)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "reach.json").write_text(json.dumps(res))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", action="store_true")
    ap.add_argument("--paths-analyze", action="store_true")
    ap.add_argument("--reach", action="store_true")
    ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    if a.reach:
        reach()
    if a.paths:
        paths(a.workers)
    if a.paths_analyze:
        paths_analyze()


if __name__ == "__main__":
    main()
