"""The hybrid fixes before the many-agent world (docs/results/hybrid-exit-option-prereg.md): a reading for the member left alone
(FixConfig.hybrid_lone) and forecasts with the option to leave later (FixConfig.hybrid_exit). Known-answer checks KL2 (story 4) and KX2
(the exact model's answer: exit aids help only a chooser who values the exit option), and H41 rerun with both fixes beside the old
version. Scripted persona agents, no model calls. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled number.

  uv run python scripts/hybrid_exit_option.py --story      KL2: story 4 under hybrid_lone alone, against the old version
  uv run python scripts/hybrid_exit_option.py --kx2        KX2: trap vs baseline fixtures, week-0 forecasts, exit option on vs off
  uv run python scripts/hybrid_exit_option.py --reach      "Can every verdict happen?" for the old-vs-new sign classes (synthetic)
  uv run python scripts/hybrid_exit_option.py --run        H41's 11 arms with both fixes (at most 4 workers); runs/h41-exit-option/rows.jsonl
  uv run python scripts/hybrid_exit_option.py --old        the old version on B, trial, all with the new record (old.jsonl)
  uv run python scripts/hybrid_exit_option.py --decomp     each fix alone: lone on B, trial; exit on B, prenup (lone.jsonl, exit.jsonl)
  uv run python scripts/hybrid_exit_option.py --analyze    old vs new, the stop rule, the second measures; writes analysis.json
  uv run python scripts/hybrid_exit_option.py --life ARM A B [--version new]   one life, 13-week blocks (story check)
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
import formation_check_3 as FC3  # noqa: E402
import h38_pairing_run as H38  # noqa: E402
import h41_choice_aids as A  # noqa: E402
from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import hybrid as HY  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "h41-exit-option"
OLD_ROWS = ROOT / "runs" / "h41-choice-aids" / "rows.jsonl"
WORKERS = 4
VERSIONS = {"new": {"hybrid_lone": True, "hybrid_exit": True}, "old": {}, "lone": {"hybrid_lone": True}, "exit": {"hybrid_exit": True}}
FILES = {"new": "rows.jsonl", "old": "old.jsonl", "lone": "lone.jsonl", "exit": "exit.jsonl"}
HI = 0.5                       # E2: a lone week "in serious suffering" when the member alone has suffering (both kinds) >= 0.5
STORY = ("trial", "p-peacekeeper", "p-wanderer", 0)


# ---- one run ---------------------------------------------------------------------------------------------------------------------

def play(arm, a, b, seed, version="new", weeks=H.WEEKS, liberty=None):
    """h41_choice_aids.play under a version, tracking lone weeks and the forecast-vs-lived exit log. -> (Run, lived, readings, extra)."""
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    level, _ = A.ARMS[arm]
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(level), **A.rule(arm), **VERSIONS[version])
    readings = []
    HY.STATS.clear()
    HY.STATS.update(futures=0, future_weeks=0, forks=0, choices=0, world_readings=0, future_exits=0, prenup_tied=0)
    HY.EXIT_LOG = []
    lone = []                                   # per week: (role alone, its suffering) or None
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback(A.EXIT.get(arm, "F4"), strip_split=True), \
            EI.use_items(EI.GRID[H38.CELL]):
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=weeks, decline=True)
        world = lived.world
        if liberty is not None:
            world.run.liberty = []

            def hook(wd, wk_):
                if wk_ in (0, 52):
                    wd.run.liberty.append(H38._liberty(wd, wk_, liberty))
            world.hook = hook
        last = {"busy": {"A": False, "B": False}}
        lat_weeks = 0
        for w in range(world.weeks):
            world = lived.world
            if w and w % NG.REVIEW_EVERY == 0:
                if lived.apart and lived.decline:
                    lived.retry(w, last)
                elif all(world.p[r]["in"] for r in "AB"):
                    with NG.forward_memo():
                        readings.append((w, A.stay_reading(world, w, last)))
                        if getattr(world, "trial_end", None) == w:
                            HY.trial_reading(lived, w, last)
                        else:
                            lived.reading(w, last)
                elif any(world.p[r]["in"] for r in "AB"):
                    HY.return_reading(lived, w, last)
            else:
                lived.hybrid_week(w, last)
            if world.early_review:
                world.ladder_reviewed(w)
            lat_weeks += int(world.lat_on())
            last = {"busy": world.step_week(w, last)}
            ins = [r for r in "AB" if world.p[r]["in"]]
            if len(ins) == 1:
                h = world.run.outcomes[-1]["hedonic"][ins[0]]
                lone.append((ins[0], h["s_off"] + h["s_non"]))
            else:
                lone.append(None)
        world.run.final = {r: {**world.p[r], "pooled": world.pool, "put": world.put[r]} for r in "AB"}
        world.run.fix = world.fix_report()
        world.run.exits = list(world.exit_log)
        world.run.lat_weeks = lat_weeks
    extra = {"lone": lone, "lone_log": list(getattr(world, "lone_log", [])), "exit_log": HY.EXIT_LOG}
    HY.EXIT_LOG = None
    return world.run, lived, readings, extra


def lone_stats(lone):
    """Share of weeks with exactly one member in; the longest stretch in which the member alone has suffering >= HI."""
    share = sum(x is not None for x in lone) / len(lone)
    best = cur = 0
    for x in lone:
        cur = cur + 1 if (x is not None and x[1] >= HI) else 0
        best = max(best, cur)
    return {"lone": share, "lone_hi_max": best, "lone_hi_weeks": sum(1 for x in lone if x is not None and x[1] >= HI) / len(lone)}


def exit_pairs(exit_log, exits, weeks):
    """Second measure: per reading status quo, the share of futures with an exit within 13 and 52 weeks, and the lived world's."""
    out = []
    for e in exit_log:
        w, fut = e["w"], e["exits"]
        if not fut:
            continue
        lw = [x["week"] - w for x in exits if x["week"] >= w]
        out.append({"w": w, "f13": float(np.mean([any(t < 13 for t in f) for f in fut])),
                    "f52": float(np.mean([any(t < 52 for t in f) for f in fut])),
                    "l13": any(t < 13 for t in lw), "l52": any(t < 52 for t in lw), "room52": w + 52 <= weeks})
    return out


def record(run, lived, readings, extra, arm, a, b, seed, version, secs):
    rec = A.record(run, lived, readings, arm, a, b, seed, secs)
    rec["version"] = version
    rec.update(lone_stats(extra["lone"]))
    rec["lone_log"] = extra["lone_log"]
    rec["exit_pairs"] = exit_pairs(extra["exit_log"], run.exits, len(run.outcomes))
    rec["exits"] = [{"week": e["week"], "role": e["role"]} for e in run.exits]
    rec["retries"] = [{"week": x["week"], "formed": x["formed"]} for x in lived.retries]
    return rec


_LIB = {}


def task(args):
    arm, a, b, seeds, version = args
    out = []
    for s in seeds:
        t0 = time.time()
        run, lived, rd, ex = play(arm, a, b, s, version, liberty=_LIB)
        out.append(record(run, lived, rd, ex, arm, a, b, s, version, time.time() - t0))
    return out


def run_all(version, arms, workers=WORKERS, cfg=None):
    cfg = cfg or A.CONFIRM
    workers = min(workers, 4)
    f = OUT / FILES[version]
    f.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["g"], r["a"], r["b"]) for r in A.load(f)} if f.exists() else set()
    tasks = [(arm, a, b, cfg["seeds"], version) for (a, b) in A.pairings(cfg) for arm in arms if (arm, a, b) not in done]
    print(f"{version}: {len(tasks)} tasks, {workers} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as fh:
        for i, rows in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            fh.write("\n".join(json.dumps(r) for r in rows) + "\n")
            fh.flush()
            if i % 20 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {rows[-1]['secs']:.0f}s wall {time.time() - t0:.0f}s", flush=True)


# ---- KL2: story 4 --------------------------------------------------------------------------------------------------------------

def story():
    arm, a, b, seed = STORY
    pair = next(((x, y) for x, y in A.pairings(A.CONFIRM) if {x, y} == {a, b}), None)
    a, b = pair
    t0 = time.time()
    res = {}
    for v in ("old", "lone", "new"):
        run, lived, rd, ex = play(arm, a, b, seed, v)
        res[v] = {"rows": [[o["both_in"]] + [[round(o["hedonic"][r][k], 6) for k in ("pleasure", "s_off", "s_non")] for r in "AB"]
                           for o in run.outcomes],
                  "exits": [{"week": e["week"], "role": e["role"]} for e in run.exits], "lone_log": ex["lone_log"],
                  "retries": [{"week": x["week"], "formed": x["formed"]} for x in lived.retries], **lone_stats(ex["lone"]),
                  "lone": ex["lone"]}
    old_rows = [json.loads(x) for x in OLD_ROWS.read_text().splitlines() if x.strip()]
    ref = next(r for r in old_rows if r["g"] == arm and r["a"] == a and r["b"] == b)
    first_leave = min((e["week"] for e in res["old"]["exits"]), default=None)
    same = res["old"]["rows"][:first_leave + 1] == res["lone"]["rows"][:first_leave + 1] if first_leave is not None else None
    log = res["lone"]["lone_log"]
    # KL2: the member alone holds lone readings, and it does not stay alone more than 26 weeks past the first of two readings in a
    # row beyond the margin (two readings then the bar)
    m = 0.02
    beyond = [x["out"] > x["stay"] + m for x in log]
    stuck = False
    for i in range(1, len(log)):
        if beyond[i - 1] and beyond[i]:
            start = log[i - 1]["week"]
            alone_after = sum(1 for wk, x in enumerate(res["lone"]["lone"]) if wk >= start and x is not None)
            stuck = alone_after > 26
            break
    kl2 = bool(same) and bool(log) and not stuck
    out = {"pair": [a, b], "old_matches_h41": abs(ref["both_share"] - float(np.mean([x[0] for x in res["old"]["rows"]]))) < 1e-12,
           "first_leave": first_leave, "identical_until_first_leave": same, "lone_readings": log, "stuck": stuck,
           "KL2": "PASS" if kl2 else "FAIL", "secs": round(time.time() - t0)}
    for v in res:
        out[v] = {k: res[v][k] for k in ("exits", "retries", "lone", "lone_hi_max", "lone_hi_weeks")}
        out[v]["lone"] = lone_stats(res[v]["lone"])["lone"]
        out[v]["suff_blocks"] = {r: [round(float(np.mean([x[1 + i][1] + x[1 + i][2] for x in res[v]["rows"][k:k + 13]])), 3)
                                     for k in range(0, len(res[v]["rows"]), 13)] for i, r in enumerate("AB")}
        out[v]["in_blocks"] = [round(float(np.mean([x[0] for x in res[v]["rows"][k:k + 13]])), 2) for k in range(0, len(res[v]["rows"]), 13)]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "story.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("old", "lone", "new")}, indent=1))
    for v in ("old", "lone", "new"):
        print(v, out[v])
    return out


# ---- KX2: the exact model's answer --------------------------------------------------------------------------------------------

def _kx2_one(args):
    import stay_test_run as STR
    exit_on, arm, a, b, seed = args
    ps = STR.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **FC3.rule("hybrid"), hybrid_w="persona", hybrid_readings="world",
                             hybrid_lone=True, hybrid_exit=exit_on)
    last = {"busy": {"A": False, "B": False}}
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        world = H.WeeklyWorld(H.PyGate(H.load_variant(arm)), (ps[a], ps[b]), seed, H.WEEKS)
        HY._FLOG[0] = []
        try:
            V = HY.forecast(world, 0, last, NG.decide_weeks(NG.FORWARD_WEEKS))
            fut = HY._FLOG[0]
        finally:
            HY._FLOG[0] = None
        O = {r: NG.outside_value(world.personas[r], r, world.p[r]["money"], seed, world.hed[r], cx=NG._cx(world, r))[0] for r in "AB"}
    return {"exit": exit_on, "arm": arm, "a": a, "b": b, "V": V, "O": O, "futures_with_exit": sum(1 for f in fut if f), "futures": len(fut)}


def kx2(workers=WORKERS, n_pairs=12, seed=900):
    import stay_test_run as STR
    pairs = [(a, b) for a, b, c in STR.pairings() if c == "ctl"][:n_pairs]
    tasks = [(e, arm, a, b, seed) for e in (False, True) for arm in ("trap", "baseline") for a, b in pairs]
    t0 = time.time()
    with Pool(min(workers, 4)) as p:
        recs = p.map(_kx2_one, tasks, chunksize=1)
    get = {(r["exit"], r["arm"], r["a"], r["b"]): r for r in recs}
    did = {}
    for a, b in pairs:
        dd = []
        for r in "AB":
            D = {e: get[(e, "baseline", a, b)]["V"][r] - get[(e, "trap", a, b)]["V"][r] for e in (False, True)}
            dd.append(D[True] - D[False])
        did[(a, b)] = float(np.mean(dd))
    vals = np.array(list(did.values()))
    rng = np.random.default_rng(0)
    bs = [float(np.mean(vals[rng.integers(0, len(vals), len(vals))])) for _ in range(4000)]
    ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    D = {e: float(np.mean([get[(e, "baseline", a, b)]["V"][r] - get[(e, "trap", a, b)]["V"][r] for a, b in pairs for r in "AB"]))
         for e in (False, True)}
    forms = {(e, arm): float(np.mean([get[(e, arm, a, b)]["V"][r] > get[(e, arm, a, b)]["O"][r] for a, b in pairs for r in "AB"]))
             for e in (False, True) for arm in ("trap", "baseline")}
    fut = {arm: sum(get[(True, arm, a, b)]["futures_with_exit"] for a, b in pairs) for arm in ("trap", "baseline")}
    fut_off = {arm: sum(get[(False, arm, a, b)]["futures_with_exit"] for a, b in pairs) for arm in ("trap", "baseline")}
    c1 = float(np.mean(vals)) > 0 and ci[0] > 0
    c2 = forms[(True, "baseline")] >= forms[(True, "trap")]
    c3 = all(v >= 1 for v in fut.values())
    out = {"pairs": pairs, "D_off": D[False], "D_on": D[True], "DiD": float(np.mean(vals)), "DiD_ci": ci, "DiD_by_pair": list(vals),
           "beats_outside": {f"{'on' if e else 'off'}:{arm}": v for (e, arm), v in forms.items()},
           "futures_with_exit_on": fut, "futures_with_exit_off": fut_off, "clauses": {"i": c1, "ii": c2, "iii": c3},
           "KX2": "PASS" if (c1 and c2 and c3) else ("FAIL" if c3 else "CANNOT FAIL (no in-future exits)"),
           "rows": recs, "secs": round(time.time() - t0)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "kx2.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, default=str))
    return out


# ---- analysis: old vs new -------------------------------------------------------------------------------------------------------

CLASS_KEYS = {"together": 0.01, "formed0": 0.01, "held": 0.005, "held_wide": 0.005, "liberty": 0.02, "pleasure": A.MARGIN,
              "lived": A.MARGIN, "snon": 0.0, "worse_off": A.MARGIN}
SIDE = ("together", "formed0", "held", "held_wide", "liberty", "pleasure", "lived", "snon", "worse_off", "ended", "lat")


def vs_b(rows, arm, n=2000, seed=0):
    """Each CLASS_KEYS measure: arm minus B, pairing bootstrap 95% interval, and H41's sign class at the key's margin."""
    pairs = sorted({(r["a"], r["b"]) for r in rows if r["g"] == arm})
    keys = tuple(CLASS_KEYS)
    est = {k: (A.arm_means(rows, arm, (k,))[k] or 0.0) - (A.arm_means(rows, "B", (k,))[k] or 0.0) for k in keys}
    rng = np.random.default_rng(seed)
    bs = {k: [] for k in keys}
    for _ in range(n):
        idx = [pairs[i] for i in rng.integers(0, len(pairs), len(pairs))]
        ma, mb = A.arm_means(rows, arm, keys, idx), A.arm_means(rows, "B", keys, idx)
        for k in keys:
            if ma[k] is not None and mb[k] is not None:
                bs[k].append(ma[k] - mb[k])
    ci = {k: ([float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) > 10 else None) for k, v in bs.items()}
    return {k: {"d": est[k], "ci": ci[k], "class": A.classify(est[k], ci[k], CLASS_KEYS[k])} for k in keys}


def stop_rule(old, new):
    """Per arm and key: same sign class in both versions -> 'holds across versions', else 'version-dependent'."""
    out = {}
    for arm in new:
        if arm not in old:
            continue
        out[arm] = {k: {"old": old[arm][k]["class"], "new": new[arm][k]["class"],
                        "label": "holds across versions" if old[arm][k]["class"] == new[arm][k]["class"] else "version-dependent"}
                    for k in new[arm]}
    return out


def reach():
    """Synthetic: both stop-rule labels are reachable, and the classifier sees a planted sign flip."""
    def rows(shift):
        rng = np.random.default_rng(1)
        rs = []
        for i in range(60):
            for g, mu in (("B", 0.5), ("X", 0.5 + shift)):
                v = float(rng.normal(mu, 0.02))
                rs.append({"g": g, "a": f"s{i}", "b": f"t{i}", "both_share": v, "formed0": True, "stay": {"held": 0, "worth": 5},
                           "wide": {"held": 0, "worth": 5, "leave": 0}, "lib": 2.0, "pl": 0.9, "lived": 0.9, "snon": 0.0, "suff": 0.0,
                           "worse_off": 0.9, "top": 0.5, "lat": 0.0, "ended": False})
        return rs
    old = {"X": vs_b(rows(+0.05), "X", 300)}
    same = {"X": vs_b(rows(+0.06), "X", 300)}
    flip = {"X": vs_b(rows(-0.05), "X", 300)}
    res = {"same": stop_rule(old, same)["X"]["together"]["label"], "flip": stop_rule(old, flip)["X"]["together"]["label"]}
    print(res)
    assert res == {"same": "holds across versions", "flip": "version-dependent"}
    (OUT / "reach.json").parent.mkdir(parents=True, exist_ok=True)
    (OUT / "reach.json").write_text(json.dumps(res))
    return res


def second_measure(rows, arm="B"):
    xs = [x for r in rows if r["g"] == arm for x in r.get("exit_pairs", [])]
    if not xs:
        return None
    x52 = [x for x in xs if x["room52"]]
    return {"readings": len(xs), "forecast13": float(np.mean([x["f13"] for x in xs])), "lived13": float(np.mean([x["l13"] for x in xs])),
            "readings52": len(x52), "forecast52": float(np.mean([x["f52"] for x in x52])) if x52 else None,
            "lived52": float(np.mean([x["l52"] for x in x52])) if x52 else None}


def lone_summary(rows, arm):
    xs = [r for r in rows if r["g"] == arm and "lone" in r]
    if not xs:
        return None
    return {"lone": float(np.mean([r["lone"] for r in xs])), "lone_hi_weeks": float(np.mean([r["lone_hi_weeks"] for r in xs])),
            "lone_hi_max": int(max(r["lone_hi_max"] for r in xs)), "runs_hi_over_26": sum(r["lone_hi_max"] > 26 for r in xs),
            "lone_readings": sum(len(r.get("lone_log", [])) for r in xs),
            "lone_leaves": sum(1 for r in xs for x in r.get("lone_log", []) if x["bar_out"]),
            "refor": sum(1 for r in xs for i, x in enumerate(r.get("retries", [])) if x["formed"] and r.get("exits") and
                         x["week"] > min(e["week"] for e in r["exits"]))}


def reproduction(old_rows, rerun_rows):
    """PIN at run level: the old version's rerun must equal H41's rows on every field H41 recorded (seconds and stats aside)."""
    ref = {(r["g"], r["a"], r["b"]): r for r in old_rows}
    skip = {"secs", "stats"}
    bad = []
    for r in rerun_rows:
        o = ref.get((r["g"], r["a"], r["b"]))
        if o is None:
            continue
        for k in o:
            if k not in skip and json.dumps(o[k], sort_keys=True) != json.dumps(r.get(k), sort_keys=True):
                bad.append((r["g"], r["a"], r["b"], k))
    return {"compared": sum(1 for r in rerun_rows if (r["g"], r["a"], r["b"]) in ref), "differences": bad[:20], "n_diff": len(bad)}


def analyze():
    old_rows = A.load(OLD_ROWS)
    new_rows = A.load(OUT / FILES["new"])
    res = {"new": A.analyze_rows(new_rows), "arms_old": {}, "arms_new": {}}
    arms = [a for a in A.ARMS if a != "B" and any(r["g"] == a for r in new_rows)]
    vs_old = {arm: vs_b(old_rows, arm) for arm in arms}
    vs_new = {arm: vs_b(new_rows, arm) for arm in arms}
    res["vsB_old"], res["vsB_new"] = vs_old, vs_new
    res["stop_rule"] = stop_rule(vs_old, vs_new)
    for arm in A.ARMS:
        res["arms_old"][arm] = A.arm_means(old_rows, arm, A.KEYS)
        res["arms_new"][arm] = A.arm_means(new_rows, arm, A.KEYS)
        res["arms_new"][arm]["secs"] = float(np.mean([r["secs"] for r in new_rows if r["g"] == arm] or [0]))
        res["arms_old"][arm]["secs"] = float(np.mean([r["secs"] for r in old_rows if r["g"] == arm] or [0]))
    res["lone_new"] = {arm: lone_summary(new_rows, arm) for arm in A.ARMS}
    extra = {}
    for v in ("old", "lone", "exit"):
        f = OUT / FILES[v]
        if f.exists():
            extra[v] = A.load(f)
            res[f"lone_{v}"] = {arm: lone_summary(extra[v], arm) for arm in A.ARMS if any(r["g"] == arm for r in extra[v])}
            res[f"arms_{v}_rerun"] = {arm: A.arm_means(extra[v], arm, A.KEYS) for arm in A.ARMS if any(r["g"] == arm for r in extra[v])}
    if "old" in extra:
        res["reproduction"] = reproduction(old_rows, extra["old"])
    res["second_measure"] = {arm: second_measure(new_rows, arm) for arm in ("B", "P1", "trial", "prenup")}
    res["paired_new_minus_old"] = paired(old_rows, new_rows)
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    show(res)
    return res


def paired(old_rows, new_rows):
    """Per arm, new minus old, paired by pairing, with a pairing bootstrap interval."""
    out = {}
    for arm in A.ARMS:
        out[arm] = {}
        for k in ("together", "formed0", "liberty", "pleasure", "lived", "snon", "ended"):
            po, pn = A.per_pair(old_rows, arm, k), A.per_pair(new_rows, arm, k)
            ks = sorted(set(po) & set(pn))
            if not ks:
                continue
            d = np.array([pn[x] - po[x] for x in ks])
            rng = np.random.default_rng(0)
            bs = [float(np.mean(d[rng.integers(0, len(d), len(d))])) for _ in range(2000)]
            out[arm][k] = {"d": float(np.mean(d)), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "n": len(ks)}
        ho, hn = A.pooled_held(old_rows, arm), A.pooled_held(new_rows, arm)
        out[arm]["held"] = {"old": ho, "new": hn}
    return out


def show(res):
    print(f"{'arm':<7}" + "".join(f"{k:>18}" for k in ("together", "formed0", "held", "liberty", "pleasure", "lived", "snon")))
    for arm in A.ARMS:
        o, n = res["arms_old"][arm], res["arms_new"][arm]
        if n.get("together") is None:
            continue
        print(f"{arm:<7}" + "".join(f"  {o[k] if o[k] is not None else float('nan'):7.4f}>{n[k] if n[k] is not None else float('nan'):7.4f}"
                                    for k in ("together", "formed0", "held", "liberty", "pleasure", "lived", "snon")))
    for arm, d in res["stop_rule"].items():
        vd = {k: (v["old"], v["new"]) for k, v in d.items() if v["label"] == "version-dependent"}
        print(f"{arm:<7} version-dependent: {vd}")
    for aid, v in res["new"]["aids"].items():
        print(f"== {aid}: {v['verdict']}")
    print("H41 new:", res["new"]["H41"])
    print("lone new:", json.dumps(res["lone_new"]))
    print("second measure:", json.dumps(res["second_measure"]))
    if "reproduction" in res:
        print("reproduction:", res["reproduction"]["compared"], "compared,", res["reproduction"]["n_diff"], "differences")


# ---- one life, for the story check ----------------------------------------------------------------------------------------------

def life(arm, a, b, version="new", seed=0):
    run, lived, rd, ex = play(arm, a, b, seed, version)
    outs = run.outcomes
    print(f"{arm} {a} x {b} ({version}): week0 {lived.week0.get('term')} formed {lived.week0.get('formed')}; exits {run.exits}; "
          f"retries {[(x['week'], x['formed'], x.get('term')) for x in lived.retries]}; trials {getattr(lived, 'trials', [])}")
    print("lone readings:", ex["lone_log"])
    for k in range(0, len(outs), 13):
        blk = outs[k:k + 13]
        s = " ".join(f"{r}: pl {np.mean([o['hedonic'][r]['pleasure'] for o in blk]):.3f} su {np.mean([o['hedonic'][r]['s_off'] + o['hedonic'][r]['s_non'] for o in blk]):.3f} "
                     f"non {np.mean([o['hedonic'][r]['s_non'] for o in blk]):.3f}" for r in "AB")
        lo = [x for x in ex["lone"][k:k + 13] if x is not None]
        print(f"  wk {k:>3}: both-in {np.mean([o['both_in'] for o in blk]):.2f} lone {len(lo):>2}  {s}")
    for e in ex["exit_log"][:12]:
        fut = e["exits"]
        print(f"  reading wk {e['w']}: futures with an exit {sum(1 for f in fut if f)}/{len(fut)} at {fut}")


def main():
    ap = argparse.ArgumentParser()
    for f in ("story", "kx2", "reach", "run", "old", "decomp", "analyze"):
        ap.add_argument(f"--{f}", action="store_true")
    ap.add_argument("--life", nargs=3)
    ap.add_argument("--version", default="new")
    ap.add_argument("--arms", default=",".join(A.ARMS))
    ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    if a.story:
        story()
    if a.kx2:
        kx2(a.workers)
    if a.reach:
        reach()
    if a.run:
        run_all("new", [x for x in a.arms.split(",") if x], a.workers)
    if a.old:
        run_all("old", ["B", "trial", "all"], a.workers)
    if a.decomp:
        run_all("lone", ["B", "trial"], a.workers)
        run_all("exit", ["B", "prenup"], a.workers)
    if a.analyze:
        analyze()
    if a.life:
        life(*a.life, version=a.version)


if __name__ == "__main__":
    main()
