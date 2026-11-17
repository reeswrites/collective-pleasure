"""Diagnosis of three failing known-answer checks under the time-together versions (docs/notes/known-answer-diagnosis.md): PT-R T3, K1
and KO1. Measurement only: no model behaviour changes. Scripted agents, no model calls. Wording rule: agents feel nothing; "pleasure",
"value", "forecast" and "held" are glosses for modeled numbers.

Each check is rerun from A6 with one time-together flag changed at a time (DELTAS), on the check's own sample and harness, plus
instrumentation the original rows lack:
- K1: per run, the readings' status-quo and outside values (SQ, O) per member, and the pleasure of the staying weeks;
- KO1: per bar exit, the share of the 52 post-exit weeks the leaver spends back in a household, and the yardstick in and out of one;
- PT-R: the value check's rows, read by scripts/value_consistency.passtest as PT-R reads them.

  uv run python scripts/known_answer_diagnosis.py --k1 a6,tt,bg11,bg33,subst,tt2     runs/diagnose-t3/k1-<cfg>.json
  uv run python scripts/known_answer_diagnosis.py --ko1 a6,bg11,bg33,subst,tt2       runs/diagnose-t3/ko1-<cfg>.jsonl (B arm)
  uv run python scripts/known_answer_diagnosis.py --ptr bg11,bg33,subst,tt2_nolat    runs/diagnose-t3/ptr-<cfg>/rows.jsonl
  uv run python scripts/known_answer_diagnosis.py --analyze                          runs/diagnose-t3/analysis.json
"""
import argparse
import collections
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
import hybrid_fix_check as HFC  # noqa: E402
import hybrid_leaving as L  # noqa: E402
import hybrid_passtest as PT  # noqa: E402
import value_consistency as V  # noqa: E402
from mar import negotiation as NG  # noqa: E402

OUT = ROOT / "runs" / "diagnose-t3"
WORKERS = 6
LATF = {"lat_bg_keep": 0.2, "lat_travel": 0.33, "lat_gifts": True}
# One flag at a time from A6 (lat_bg_keep's default is already 0.2; it acts only when together_bg > 0 under LAT)
DELTAS = {"a6": {}, "bg11": {"together_bg": 1.1}, "bg33": {"together_bg": 3.3}, "subst": {"together_subst": True}, "lat": LATF,
          "tt": {"together_bg": 1.1, "together_subst": True, **LATF},
          "tt2": {"together_bg": 3.3, "together_subst": True, **LATF},
          "tt2_nolat": {"together_bg": 3.3, "together_subst": True, "lat_bg_keep": 0.0, "lat_travel": 0.0},
          "tt2_nosubst": {"together_bg": 3.3, **LATF}}
XO.VERSIONS.update({f"dg_{k}": {**L.A6, **v} for k, v in DELTAS.items()})


# ---- K1: the trap and baseline fixtures ----------------------------------------------------------------------------------------

_READS = []
_orig_reading = NG.BaselineLived.reading


def _reading(self, w, last):
    """The harness's reading, unchanged; its log entry (outside O and status quo per member) is also kept for this diagnosis."""
    n = len(self.log)
    out = _orig_reading(self, w, last)
    for e in self.log[n:]:
        if "outside" in e and "baseline" in e:
            _READS.append({"wid": id(self.world), "week": w, "O": {r: round(float(e["outside"][r]), 6) for r in "AB"},
                           "SQ": {r: round(float(e["baseline"][r]), 6) for r in "AB"},
                           "trust_pen": {r: round(float(NG.trust_penalty(self.world.trust[r])), 6) for r in "AB"}})
    return out


NG.BaselineLived.reading = _reading


def k1_one(args):
    import stay_test_run as STR
    from mar import hedonic as HD
    from mar import pairing as PR
    from mar import retest as RT
    from mar import stay_test as ST
    from mar.worlds import household as H
    import formation_check_3 as FC3
    cfg, arm, a, b, seed = args
    _READS.clear()
    ps = STR.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **FC3.rule("hybrid"), **HFC.A6["a6"], **DELTAS[cfg])
    t0 = time.time()
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        world = H.WeeklyWorld(H.PyGate(H.load_variant(arm)), (ps[a], ps[b]), seed, H.WEEKS)
        run, weeks = ST.play_with_stay_test(world, bar=False)
    rec = STR.compact(weeks)
    flags = STR.held_week_flags(rec)
    both = [o["both_in"] for o in run.outcomes]
    pl = {r: [o["hedonic"][r]["pleasure"] for o in run.outcomes] for r in "AB"}
    return {"cfg": cfg, "arm": arm, "a": a, "b": b, "staying": len(flags), "held": int(sum(flags)), "secs": round(time.time() - t0, 1),
            "exits": len(run.exits), "exit_weeks": [(e["week"], e["role"]) for e in run.exits], "ended": not run.outcomes[-1]["both_in"],
            "first_exit": run.exits[0]["week"] if run.exits else None, "both_weeks": int(sum(both)),
            "pl_in": {r: round(float(np.mean([p for p, x in zip(pl[r], both) if x])), 5) if any(both) else None for r in "AB"},
            "pl_out": {r: round(float(np.mean([p for p, x in zip(pl[r], both) if not x])), 5) if not all(both) else None for r in "AB"},
            "held_weeks": [s for s, f in zip(rec["week"], flags) if f],
            "reads": [{k: v for k, v in x.items() if k != "wid"} for x in _READS if x["wid"] == id(world)]}     # lived readings only


def k1(cfgs, workers=WORKERS):
    import stay_test_run as STR
    OUT.mkdir(parents=True, exist_ok=True)
    pairs = [(a, b) for a, b, c in STR.pairings() if c == "ctl"][:12]
    for cfg in cfgs:
        f = OUT / f"k1-{cfg}.json"
        if f.exists():
            continue
        tasks = [(cfg, arm, a, b, 900) for arm in ("trap", "baseline") for a, b in pairs]
        t0 = time.time()
        with Pool(min(workers, 6)) as p:
            rows = p.map(k1_one, tasks, chunksize=1)
        out = {"rows": rows, "secs": round(time.time() - t0), "summary": {}}
        for arm in ("trap", "baseline"):
            xs = [r for r in rows if r["arm"] == arm]
            n, h = sum(r["staying"] for r in xs), sum(r["held"] for r in xs)
            out["summary"][arm] = {"held_share": h / n if n else None, "staying_weeks": n, "held_weeks": h}
        s = out["summary"]
        out["K1"] = "PASS" if (s["trap"]["held_share"] or 0) >= HFC.BARS["trap_min"] and \
            (s["baseline"]["held_share"] or 0) <= HFC.BARS["baseline_max"] else "FAIL"
        f.write_text(json.dumps(out, indent=1))
        print(cfg, "K1", out["K1"], s, f"{out['secs']}s", flush=True)


# ---- KO1: the outside forecast against the life lived after a bar exit -----------------------------------------------------------

def ko1_one(args):
    arm, a, b, seed, cfg = args
    import mar.makers as MK
    from mar import retest as RT
    t0 = time.time()
    L._TLOG.clear()
    run, lived, rd, ex = XO.play(arm, a, b, seed, f"dg_{cfg}", liberty=XO._LIB)
    ps = RT.personas()
    weights = {"A": MK.suffering_weight(ps[a]), "B": MK.suffering_weight(ps[b])}
    events = run.fix.get("events", []) if isinstance(run.fix, dict) else []
    paths = L.exit_paths(run, lived, ex["lone"], events, weights)
    flags = L.in_flags(run, ex["lone"])
    n = len(run.outcomes)
    for p in paths:
        if "err" not in p:
            continue
        r, wk = p["role"], p["week"]
        post = list(range(wk + 1, min(n, wk + 1 + L.POST_MAX)))
        _, _, _, _, y = L.ys(run, r, weights[r])
        inn = [i for i in post if r in flags[i]]
        out = [i for i in post if r not in flags[i]]
        both = [i for i in post if run.outcomes[i]["both_in"]]
        p["post_in_share"] = round(len(inn) / len(post), 4)
        p["post_both_share"] = round(len(both) / len(post), 4)
        p["y_in"] = round(float(np.mean([y[i] for i in inn])), 6) if inn else None
        p["y_out"] = round(float(np.mean([y[i] for i in out])), 6) if out else None
        p["pl_both"] = round(float(np.mean([run.outcomes[i]["hedonic"][r]["pleasure"] for i in both])), 6) if both else None
        p["pl_out"] = round(float(np.mean([run.outcomes[i]["hedonic"][r]["pleasure"] for i in out])), 6) if out else None
    return {"g": arm, "a": a, "b": b, "seed": seed, "cfg": cfg, "paths": paths, "secs": round(time.time() - t0, 1),
            "both_share": float(np.mean([o["both_in"] for o in run.outcomes])), "exits": len(run.exits)}


def ko1(cfgs, workers=WORKERS):
    OUT.mkdir(parents=True, exist_ok=True)
    pairs = A.pairings(A.CONFIRM)
    for cfg in cfgs:
        f = OUT / f"ko1-{cfg}.jsonl"
        done = {(r["a"], r["b"]) for r in A.load(f)} if f.exists() else set()
        tasks = [("B", a, b, s, cfg) for (a, b) in pairs for s in A.CONFIRM["seeds"] if (a, b) not in done]
        t0 = time.time()
        print(f"ko1 {cfg}: {len(tasks)} tasks", flush=True)
        with Pool(min(workers, 6)) as pool, f.open("a") as fh:
            for i, rec in enumerate(pool.imap_unordered(ko1_one, tasks, chunksize=1), 1):
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                if i % 20 == 0 or i == len(tasks):
                    print(f"  {i}/{len(tasks)} wall {time.time() - t0:.0f}s", flush=True)


# ---- PT-R: the routine's one-week value check ----------------------------------------------------------------------------------

def ptr_extra(cfg):
    base = {**V.HYBRID, "satiety_expect": "world", **PT.A6}
    return {**base, **DELTAS[cfg]}


def ptr(cfgs, workers=WORKERS):
    """cfgs: DELTAS names (the hybrid from A6), or "v2_<name>": PT-R's reference agents (v2, bills, saturating scale, satiety=world)
    in the world of that delta (only the world's flags act on v2), on the hybrid's sample."""
    for cfg in cfgs:
        d = OUT / f"ptr-{cfg}"
        d.mkdir(parents=True, exist_ok=True)
        print(f"ptr {cfg}", flush=True)
        extra = {**V.V2SAT, "satiety_expect": "world", **DELTAS[cfg[3:]]} if cfg.startswith("v2_") else ptr_extra(cfg)
        V.collect(V.HSAMPLE, d / "rows.jsonl", workers, extra)


# ---- analysis --------------------------------------------------------------------------------------------------------------------

PTR_ROWS = {"v2": "value-consistency-v2-sat-world", "a6": "value-consistency-hybrid-world-a6", "tt": "value-consistency-hybrid-world-tt",
            "tt2": "value-consistency-hybrid-world-tt2"}
FLOOR = 0.003           # the agent's action floor (an action below it is not taken; valuecheck and the T3 code use the same number)


def t3_parts(recs):
    """T3 as PT-R computes it, and its misses split by kind. A floor miss: the agent's best perceived value is at or under FLOOR, so it
    idles, and the best action's one-week actual is in (0, FLOOR]: T3 names that action the right one, the agent's own floor names idle."""
    tf = V.target_fn("net")
    rows = V.items(recs)
    byd = collections.defaultdict(list)
    for r in rows:
        byd[r["dk"]].append(r)
    cat, n, same, best, rest_in = collections.Counter(), 0, 0, [], []
    for v in byd.values():
        if len(v) < 2:
            continue
        n += 1
        a1 = lambda r: tf(r, 13 if r["rule"] == "soft" else 1)      # noqa: E731
        bp = max(v, key=lambda r: r["p"])
        own = bp["a"] if bp["p"] > FLOOR else "idle"
        ba = max(v, key=a1)
        act = ba["a"] if a1(ba) > 0 else "idle"
        same += own == (ba["a"] if a1(ba) > FLOOR else "idle")
        best.append(max(a1(ba), 0.0))
        if own == act:
            cat["agree"] += 1
        elif own == "idle" and a1(ba) <= FLOOR:
            cat["floor"] += 1
        elif bp["a"] == "together" and act != "idle":
            cat["together_partner_share"] += 1
        else:
            cat["other"] += 1
    for d in recs:
        if d["ctx"]["in_hh"] and d["ctx"]["other_in"]:
            rest_in += [i["actual"]["1"]["own"]["net"] for i in d["items"] if i["applied"] and i["a"] == "rest"]
    pt = V.passtest(recs, "net")
    ba = np.array(best)
    return {"T3": round(pt["T3"], 4), "decisions": n, "misses": {k: c for k, c in cat.items() if k != "agree"},
            "T3_same_floor": round(same / max(1, n), 4), "best_actual_median": round(float(np.median(ba)), 5),
            "best_actual_under_floor_share": round(float(np.mean((ba > 0) & (ba <= FLOOR))), 4),
            "rest_in_household_actual_mean": round(float(np.mean(rest_in)), 5) if rest_in else None,
            "T1": round(pt["T1"], 4), "T2": round(pt["T2"], 4), "T4": round(pt["T4"], 4), "T5": round(pt["T5"], 3)}


def analyze():
    res = {"PT-R": {}, "K1": {}, "KO1": {}}
    keep = {(r["a"], r["b"], r["seed"]) for r in V.load(ROOT / "runs" / PTR_ROWS["a6"] / "rows.jsonl")}
    srcs = {k: ROOT / "runs" / d / "rows.jsonl" for k, d in PTR_ROWS.items()}
    srcs.update({p.name[4:]: p / "rows.jsonl" for p in sorted(OUT.glob("ptr-*")) if (p / "rows.jsonl").exists()})
    for k, f in srcs.items():
        recs = [r for r in V.load(f) if (r["a"], r["b"], r["seed"]) in keep]
        res["PT-R"][k] = {"runs": len({(r["a"], r["b"]) for r in recs}), **t3_parts(recs)}
    for f in sorted(OUT.glob("k1-*.json")):
        d = json.loads(f.read_text())
        trap = [r for r in d["rows"] if r["arm"] == "trap"]
        res["K1"][f.stem[3:]] = {**d["summary"], "K1": d["K1"],
                                  "trap_runs": {f"{r['a']}|{r['b']}": [r["staying"], r["held"]] for r in trap}}
    for f in sorted(OUT.glob("ko1-*.jsonl")):
        rows = A.load(f)
        ex = [(p, (r["a"], r["b"])) for r in rows for p in r["paths"] if "err" in p and p["why"] == "bar"]
        m = L.boot_mean([p["err"] for p, _ in ex], [g for _, g in ex])
        e = {"lives": len(rows), "n": len(ex), "mean": round(m["mean"], 4) if m else None, "ci": [round(x, 4) for x in m["ci"]] if m else None}
        for tag, keep_ in (("back_in_ge_half", lambda p: p["post_in_share"] >= 0.5), ("back_in_lt_half", lambda p: p["post_in_share"] < 0.5)):
            xs = [(p, g) for p, g in ex if keep_(p)]
            mm = L.boot_mean([p["err"] for p, _ in xs], [g for _, g in xs]) if xs else None
            e[tag] = {"n": len(xs), "mean": round(mm["mean"], 4) if mm else None, "ci": [round(x, 4) for x in mm["ci"]] if mm else None}
        e["post_in_share_mean"] = round(float(np.mean([p["post_in_share"] for p, _ in ex])), 4) if ex else None
        if ex:
            x = np.array([p["post_in_share"] for p, _ in ex])
            y = np.array([p["err"] for p, _ in ex])
            e["slope_err_on_post_in"] = round(float(np.polyfit(x, y, 1)[0]), 4) if np.std(x) > 0 else None
            e["intercept_err_at_post_in_0"] = round(float(np.polyfit(x, y, 1)[1]), 4) if np.std(x) > 0 else None
        res["KO1"][f.stem[4:]] = e
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k1", default="")
    ap.add_argument("--ko1", default="")
    ap.add_argument("--ptr", default="")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    if a.k1:
        k1([x for x in a.k1.split(",") if x], a.workers)
    if a.ko1:
        ko1([x for x in a.ko1.split(",") if x], a.workers)
    if a.ptr:
        ptr([x for x in a.ptr.split(",") if x], a.workers)
    if a.analyze:
        analyze()
