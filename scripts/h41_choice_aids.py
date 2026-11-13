"""H41: choice aids against pairing pressure (docs/results/h41-choice-aids-prereg.md). The hybrid agent with each person's suffering
weight and readings run by the world (hybrid prereg Amendment 3), in the formation check's household: bills that hurt, the saturating
scale, the corrected rule, time together at the world's satiety, exit fallback F4 with items. Arms: no pressure (B), pairing pressure
at several levels (P*), and five choice aids one at a time plus all together. Held share and liberty lead; then pleasure (total and
lived), non-offsettable suffering, the worse-off partner and weeks near the top. Each aid is compared with the pressure that produces
the same share of weeks together, by interpolation. Scripted persona agents, no model calls. Wording rule: agents feel nothing;
"pleasure" is a gloss for a modeled hedonic state.

  uv run python scripts/h41_choice_aids.py --pilot      EXPLORATORY (sample seed 900; never cited as a result)
  uv run python scripts/h41_choice_aids.py --reach      "Can every verdict happen?" (synthetic verdicts, matching, the free checks)
  uv run python scripts/h41_choice_aids.py --run        the confirmatory run (at most 4 workers); rows in runs/h41-choice-aids/
  uv run python scripts/h41_choice_aids.py --analyze    prereg vs actual; writes runs/h41-choice-aids/analysis.json
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
from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import hybrid as HY  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "h41-choice-aids"
WORKERS = 4
WORLD = {**FC3.rule("hybrid"), "hybrid_w": "persona", "hybrid_readings": "world"}
TRIAL_WEEKS = 13
CHEAP_SOLO = 0.75 * 1.5            # the housing note's regime B: a solo micro-unit at 0.75 of a solo place (ULI 2014, middle of 20-30%)
INFO_K = 16                        # better information: 16 sampled futures per option of every big choice, as the held-out audit uses
AIDS = {"trial": {"h41_trial": TRIAL_WEEKS}, "cheap": {"solo_cost": CHEAP_SOLO}, "prenup": {}, "info": {"hybrid_k": INFO_K},
        "lat": {"h41_lat": True}}
AIDS["all"] = {k: v for d in AIDS.values() for k, v in d.items()}
EXIT = {"prenup": "F5", "all": "F5"}
LEVELS = (0.5, 1, 2, 4)
ARMS = {"B": (0, {}), **{f"P{lv:g}": (lv, {}) for lv in LEVELS}, **{k: (0, v) for k, v in AIDS.items()}}
AID_ARMS = tuple(AIDS)
PRESSURE_ARMS = ("B",) + tuple(f"P{lv:g}" for lv in LEVELS)
CONFIRM = {"sample_seed": 38, "n_other": 105, "seeds": (0,), "pairs_every": 1}
PILOT = {"sample_seed": 900, "n_other": 30, "seeds": (900,), "pairs_every": 3}
KNEE, TOP, BLOCK = FC3.KNEE, FC3.TOP, FC3.BLOCK
MARGIN = 0.003                     # pleasure: "raises" means above +0.003 with the interval above 0 (prereg)


def rule(arm):
    return {**WORLD, **ARMS[arm][1]}


# ---- the wide held lens -------------------------------------------------------------------------------------------------------------

def stay_reading(world, w, last):
    """pairing.stay_reading (held by pressure) plus a wider lens: held_wide = stays, but would leave with the pressure removed AND
    carrying out at least what it put in (stay_test.put_in; under F4 that is the carry already, under a prenup it may not be)."""
    from mar import stay_test as ST
    rd = PR.stay_reading(world, w, last)
    fx_free = dataclasses.replace(world.fx, pairing=PR.free(PR.active(world)))
    for r in "AB":
        carry = world.carry_out(r, 50)
        free = max(carry, ST.put_in(world, r))
        of = rd[r]["o_free"]
        if free > carry + 1e-9:
            with HD.use_fixes(fx_free):
                of = NG.outside_value(world.personas[r], r, world.p[r]["money"] + free, world.seed, world.hed[r], cx=NG._cx(world, r))[0]
            of = max(of, rd[r]["o_free"])
        stay = rd[r]["sq"] >= rd[r]["o"]
        rd[r]["o_wide"] = round(of, 5)
        rd[r]["wide"] = "held" if (stay and rd[r]["sq_free"] < of) else ("worth" if stay else "leave")
    return rd


# ---- one run -----------------------------------------------------------------------------------------------------------------------

def play(arm, a, b, seed, weeks=H.WEEKS, liberty=None):
    """One lived run (H38.play's loop, plus the trial's end and the wide lens). -> (Run, lived, readings)."""
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    level, _ = ARMS[arm]
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(level), **rule(arm))
    readings = []
    HY.STATS.update(futures=0, future_weeks=0, forks=0, choices=0, world_readings=0, future_exits=0, prenup_tied=0)
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback(EXIT.get(arm, "F4"), strip_split=True), \
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
                        readings.append((w, stay_reading(world, w, last)))
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
        world.run.final = {r: {**world.p[r], "pooled": world.pool, "put": world.put[r]} for r in "AB"}
        world.run.fix = world.fix_report()
        world.run.exits = list(world.exit_log)
        world.run.lat_weeks = lat_weeks
    return world.run, lived, readings


def record(run, lived, readings, arm, a, b, seed, secs):
    rec = FC3.record(run, lived, readings, "hybrid", arm, a, b, seed)
    outs = run.outcomes
    for r in "AB":
        rec[r]["snon"] = float(np.mean([o["hedonic"][r]["s_non"] for o in outs]))
    rec["snon"] = float(np.mean([rec[r]["snon"] for r in "AB"]))
    rec["wide"] = {c: sum(1 for _, rd in readings for r in "AB" if rd[r]["wide"] == c) for c in ("worth", "held", "leave")}
    for x in rec["readings"]:
        x["wide"] = next(rd[x["r"]]["wide"] for w, rd in readings if w == x["w"])
    rec["lat"] = run.lat_weeks / len(outs)
    rec["term0"] = lived.week0.get("term")
    rec["trials"] = list(getattr(lived, "trials", []))
    rec["retry_terms"] = [x.get("term") for x in lived.retries if x["formed"]]
    rec["stats"] = dict(HY.STATS)
    rec["secs"] = secs
    return rec


_LIB = {}


def task(args):
    arm, a, b, seeds = args
    out = []
    for s in seeds:
        t0 = time.time()
        run, lived, rd = play(arm, a, b, s, liberty=_LIB)
        out.append(record(run, lived, rd, arm, a, b, s, time.time() - t0))
    return out


def pairings(cfg):
    return H38.pairings(cfg)[::cfg.get("pairs_every", 1)]


def run_all(cfg, f, arms, workers=WORKERS):
    workers = min(workers, 4)
    f.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["g"], r["a"], r["b"]) for r in load(f)} if f.exists() else set()
    tasks = [(arm, a, b, cfg["seeds"]) for (a, b) in pairings(cfg) for arm in arms if (arm, a, b) not in done]
    print(f"{len(tasks)} tasks, {workers} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, f.open("a") as fh:
        for i, rows in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            fh.write("\n".join(json.dumps(r) for r in rows) + "\n")
            fh.flush()
            if i % 20 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {rows[-1]['secs']:.0f}s wall {time.time() - t0:.0f}s", flush=True)


def load(f):
    return [json.loads(x) for x in Path(f).read_text().splitlines() if x.strip()]


# ---- analysis ----------------------------------------------------------------------------------------------------------------------

def held_share(r, lens="held"):
    """Per run: (held readings, stay readings) under the pressure lens ("held") or the wide lens ("wide")."""
    if lens == "wide":
        n = sum(r["wide"].values())
        return r["wide"]["held"], n
    n = sum(r["stay"].values())
    return r["stay"].get("held", 0), n


MEASURES = {
    "together": lambda r: r["both_share"],
    "formed0": lambda r: float(bool(r["formed0"])),
    "held": lambda r: held_share(r)[0] / held_share(r)[1] if held_share(r)[1] else None,
    "held_wide": lambda r: held_share(r, "wide")[0] / held_share(r, "wide")[1] if held_share(r, "wide")[1] else None,
    "liberty": lambda r: r["lib"],
    "pleasure": lambda r: r["pl"],
    "lived": lambda r: r["lived"],
    "snon": lambda r: r["snon"],
    "suff": lambda r: r["suff"],
    "worse_off": lambda r: r["worse_off"],
    "top": lambda r: r["top"],
    "lat": lambda r: r["lat"],
    "ended": lambda r: float(bool(r["ended"])),
}


def per_pair(rows, arm, key):
    acc = {}
    for r in rows:
        if r["g"] == arm:
            v = MEASURES[key](r)
            if v is not None:
                acc.setdefault((r["a"], r["b"]), []).append(v)
    return {k: float(np.mean(v)) for k, v in acc.items()}


def pooled_held(rows, arm, lens="held", idx=None):
    """Held share pooled over readings (ratio of sums), optionally over a resample of pairings idx (list of (a, b))."""
    by = {}
    for r in rows:
        if r["g"] == arm:
            h, n = held_share(r, lens)
            x = by.setdefault((r["a"], r["b"]), [0, 0])
            x[0] += h
            x[1] += n
    ks = idx if idx is not None else list(by)
    h = sum(by[k][0] for k in ks if k in by)
    n = sum(by[k][1] for k in ks if k in by)
    return h / n if n else 0.0


def arm_means(rows, arm, keys, idx=None):
    out = {}
    for k in keys:
        if k in ("held", "held_wide"):
            out[k] = pooled_held(rows, arm, "held" if k == "held" else "wide", idx)
            continue
        pp = per_pair(rows, arm, k)
        ks = idx if idx is not None else list(pp)
        vs = [pp[x] for x in ks if x in pp]
        out[k] = float(np.mean(vs)) if vs else None
    return out


KEYS = ("together", "formed0", "held", "held_wide", "liberty", "pleasure", "lived", "snon", "suff", "worse_off", "top", "lat", "ended")
LEAD = ("held", "held_wide", "liberty", "pleasure", "lived", "snon", "worse_off", "top")


def match(curve, x):
    """curve: [(together, values dict)] for the pressure arms in level order (B first). Linear interpolation of every value at the
    pressure that gives together = x. -> (values, level position) or (None, reason) outside the curve's range."""
    tog = [c[0] for c in curve]
    if x < tog[0] - 1e-12:
        return None, "below no pressure"
    if x > max(tog) + 1e-12:
        return None, "above the top level"
    for i in range(len(curve) - 1):
        lo, hi = tog[i], tog[i + 1]
        if lo - 1e-12 <= x <= hi + 1e-12 and hi > lo:
            t = (x - lo) / (hi - lo)
            return {k: (None if curve[i][1][k] is None or curve[i + 1][1][k] is None
                        else (1 - t) * curve[i][1][k] + t * curve[i + 1][1][k]) for k in curve[i][1]}, i + t
    return {k: v for k, v in curve[0][1].items()}, 0.0


def compare(rows, aid, idx=None):
    """The aid against the baseline and against matched pressure. -> dict of differences (None where not matched)."""
    a = arm_means(rows, aid, KEYS, idx)
    b = arm_means(rows, "B", KEYS, idx)
    curve = [(arm_means(rows, p, ("together",), idx)["together"], arm_means(rows, p, KEYS, idx)) for p in PRESSURE_ARMS]
    curve = [(t, v) for t, v in curve if t is not None]
    m, pos = match(curve, a["together"])
    vsB = {k: (a[k] - b[k]) if (a[k] is not None and b[k] is not None) else None for k in KEYS}
    vsP = {k: (a[k] - m[k]) if (m is not None and a[k] is not None and m[k] is not None) else None for k in KEYS}
    return {"aid": a, "B": b, "vsB": vsB, "vsP": vsP, "matched_at": pos}


def boot(rows, aid, n=2000, seed=0):
    """Pairing bootstrap of compare(): 95% percentile intervals for vsB and vsP of every key, and the share of resamples matched."""
    pairs = sorted({(r["a"], r["b"]) for r in rows})
    rng = np.random.default_rng(seed)
    vsB = {k: [] for k in KEYS}
    vsP = {k: [] for k in KEYS}
    matched = 0
    for _ in range(n):
        idx = [pairs[i] for i in rng.integers(0, len(pairs), len(pairs))]
        c = compare(rows, aid, idx)
        for k in KEYS:
            if c["vsB"][k] is not None:
                vsB[k].append(c["vsB"][k])
            if c["vsP"][k] is not None:
                vsP[k].append(c["vsP"][k])
        matched += c["vsP"]["together"] is not None
    ci = lambda xs: [float(np.percentile(xs, 2.5)), float(np.percentile(xs, 97.5))] if len(xs) > 10 else None  # noqa: E731
    return {"vsB": {k: ci(v) for k, v in vsB.items()}, "vsP": {k: ci(v) for k, v in vsP.items()}, "matched_share": matched / n}


def classify(est, ci, margin=0.0):
    """+ if the estimate is above margin and the interval above 0; - if below -margin and the interval below 0; else 0."""
    if est is None or ci is None:
        return None
    if est > margin and ci[0] > 0:
        return "+"
    if est < -margin and ci[1] < 0:
        return "-"
    return "0"


def verdict_vs_baseline(c, ci):
    """The evaluator rule against no pressure: a win raises pleasure (P_up) without raising domination (held, held_wide up; liberty
    down). -> "win", "trade-off", "harm", "no gain"."""
    up = classify(c["pleasure"], ci["pleasure"], MARGIN) == "+"
    down = classify(c["pleasure"], ci["pleasure"], MARGIN) == "-"
    dom = any(classify(c[k], ci[k], 0.005) == "+" for k in ("held", "held_wide")) or classify(c["liberty"], ci["liberty"], 0.02) == "-"
    if up and not dom:
        return "win"
    if up:
        return "trade-off"
    if down:
        return "harm"
    return "no gain"


def verdict_vs_pressure(c, ci, matched_share):
    """Better than matched pressure iff matched in at least 80% of resamples, pleasure not lower than pressure's (not '-' at MARGIN),
    held share lower (pressure lens, '-'), and liberty not lower (not '-' at 0.02). -> "better", "not better", "no match"."""
    if c["together"] is None or matched_share < 0.8:
        return "no match"
    p_ok = classify(c["pleasure"], ci["pleasure"], MARGIN) != "-"
    held_lower = classify(c["held"], ci["held"], 0.005) == "-"
    lib_ok = classify(c["liberty"], ci["liberty"], 0.02) != "-"
    return "better" if (p_ok and held_lower and lib_ok) else "not better"


def aid_verdict(form_gain, vb, vp):
    """H41 for one aid: supported iff it raises weeks together (form_gain '+'), wins against no pressure, and beats matched pressure."""
    if form_gain != "+":
        return "not supported (does not raise weeks together)"
    if vb == "win" and vp == "better":
        return "supported"
    return f"not supported ({vb} against no pressure; {vp} against matched pressure)"


def analyze_rows(rows, n_boot=2000):
    res = {"arms": {}, "aids": {}}
    for arm in ARMS:
        if any(r["g"] == arm for r in rows):
            res["arms"][arm] = {**arm_means(rows, arm, KEYS), "runs": sum(1 for r in rows if r["g"] == arm),
                                "secs": float(np.mean([r["secs"] for r in rows if r["g"] == arm]))}
    for aid in AID_ARMS:
        if not any(r["g"] == aid for r in rows):
            continue
        c = compare(rows, aid)
        bt = boot(rows, aid, n_boot)
        fg = classify(c["vsB"]["together"], bt["vsB"]["together"], 0.01)
        vb = verdict_vs_baseline(c["vsB"], bt["vsB"])
        vp = verdict_vs_pressure(c["vsP"], bt["vsP"], bt["matched_share"])
        res["aids"][aid] = {"vsB": c["vsB"], "vsB_ci": bt["vsB"], "vsP": c["vsP"], "vsP_ci": bt["vsP"], "matched_at": c["matched_at"],
                            "matched_share": bt["matched_share"], "formation_gain": fg, "vs_baseline": vb, "vs_pressure": vp,
                            "verdict": aid_verdict(fg, vb, vp)}
    ps = {}
    for aid in res["aids"]:
        x, y = per_pair(rows, aid, "together"), per_pair(rows, "B", "together")
        d = np.array([x[k] - y[k] for k in sorted(set(x) & set(y))])
        ps[aid] = H38.signflip_p(d, "greater") if len(d) else 1.0
    for aid, padj in zip(ps, H38.holm(list(ps.values()))):
        res["aids"][aid]["formation_p"], res["aids"][aid]["formation_p_holm"] = ps[aid], padj
    pb = {}
    for p in PRESSURE_ARMS[1:]:
        if any(r["g"] == p for r in rows):
            pb[p] = {k: arm_means(rows, p, (k,))[k] for k in KEYS}
    res["pressure"] = pb
    res["held_vs_suffering"] = held_suffering(rows)
    allv = res["aids"].get("all", {}).get("verdict", "")
    res["H41"] = "supported" if allv == "supported" else f"not supported (all aids: {allv})"
    return res


def held_suffering(rows):
    """Suffering in the 13 weeks after a reading classed held against worth (pressure lens), pooled over the pressure arms."""
    out = {}
    for lens in ("v", "wide"):
        acc = {"held": [], "worth": []}
        for r in rows:
            for x in r["readings"]:
                c = x["v"] if lens == "v" else x.get("wide")
                if c in acc:
                    acc[c].append(x["suff"])
        out[lens] = {c: (float(np.mean(v)) if v else None, len(v)) for c, v in acc.items()}
    return out


def analyze(f=OUT / "rows.jsonl"):
    res = analyze_rows(load(f))
    (Path(f).parent / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    show(res)
    return res


def show(res):
    print(f"{'arm':<7}" + "".join(f"{k:>10}" for k in KEYS) + "      secs")
    for arm, v in res["arms"].items():
        print(f"{arm:<7}" + "".join(f"{(v[k] if v[k] is not None else float('nan')):>10.4f}" for k in KEYS) + f"  {v['secs']:8.1f}")
    for aid, v in res["aids"].items():
        print(f"== {aid}: {v['verdict']}  (matched at {v['matched_at']}, share {v['matched_share']:.2f})")
        for k in ("together",) + LEAD:
            print(f"   {k:<10} vs B {_f(v['vsB'][k])} {v['vsB_ci'][k]}   vs P {_f(v['vsP'][k])} {v['vsP_ci'][k]}")
    print("H41:", res["H41"])


def _f(x):
    return "   n/a  " if x is None else f"{x:+.4f}"


# ---- "Can every verdict happen?" ------------------------------------------------------------------------------------------------

def synthetic(spec, pairs=40, seed=0):
    """Synthetic rows: spec {arm: {measure: (mean, sd)}} over `pairs` pairings, one seed. Readings carry held counts from 'held'."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(pairs):
        a, b = f"s{i}", f"t{i}"
        for arm, m in spec.items():
            g = {k: float(rng.normal(mu, sd)) for k, (mu, sd) in m.items()}
            n = 20
            h = int(round(max(0.0, min(1.0, g["held"])) * n))
            hw = int(round(max(0.0, min(1.0, g.get("held_wide", g["held"]))) * n))
            rows.append({"g": arm, "a": a, "b": b, "seed": 0, "both_share": g["together"], "formed0": g["together"] > 0.5,
                         "stay": {"held": h, "worth": n - h}, "wide": {"held": hw, "worth": n - hw, "leave": 0},
                         "lib": g["liberty"], "pl": g["pleasure"], "lived": g["pleasure"], "snon": 0.1, "suff": 0.2,
                         "worse_off": g["pleasure"] - 0.02, "top": 0.3, "lat": 0.0, "ended": False, "readings": [], "secs": 0.0})
    return rows


def _spec(aid_tog, aid_pl, aid_held, aid_lib=2.0, p_pl=(0.80, 0.805, 0.81, 0.815, 0.82)):
    sd = 0.01
    spec = {"B": {"together": (0.40, sd), "held": (0.0, 0.0), "liberty": (2.0, 0.05), "pleasure": (0.80, sd)}}
    for i, p in enumerate(PRESSURE_ARMS[1:], 1):
        spec[p] = {"together": (0.40 + 0.1 * i, sd), "held": (0.05 * i, 0.01), "liberty": (2.0 - 0.05 * i, 0.05),
                   "pleasure": (p_pl[i], sd)}
    for aid in AID_ARMS:
        spec[aid] = {"together": (aid_tog, sd), "held": (aid_held, 0.005), "liberty": (aid_lib, 0.05), "pleasure": (aid_pl, sd)}
    return spec


def reach_verdicts():
    cases = {"supported": _spec(0.60, 0.82, 0.0), "trade-off (held up)": _spec(0.60, 0.82, 0.15),
             "harm": _spec(0.60, 0.78, 0.0), "no gain": _spec(0.60, 0.80, 0.0),
             "not better (pleasure below pressure)": _spec(0.60, 0.805, 0.0, p_pl=(0.80, 0.83, 0.86, 0.87, 0.88)),
             "no formation gain": _spec(0.40, 0.82, 0.0), "no match (above the top)": _spec(0.95, 0.82, 0.0)}
    out = {}
    for name, spec in cases.items():
        res = analyze_rows(synthetic(spec), n_boot=300)
        v = res["aids"]["trial"]
        out[name] = {"verdict": v["verdict"], "vs_baseline": v["vs_baseline"], "vs_pressure": v["vs_pressure"], "H41": res["H41"]}
        print(f"  {name:<40} {v['verdict']}")
    return out


def reach(workers=WORKERS):
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"verdicts": reach_verdicts()}
    res["secs"] = round(time.time() - t0)
    (OUT / "reach.json").write_text(json.dumps(res, indent=1, default=str))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--reach", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--workers", type=int, default=WORKERS)
    a = ap.parse_args()
    arms = [x for x in a.arms.split(",") if x]
    if a.pilot:
        run_all(PILOT, OUT / "pilot.jsonl", arms, a.workers)
        analyze(OUT / "pilot.jsonl")
    if a.reach:
        reach(a.workers)
    if a.run:
        run_all(CONFIRM, OUT / "rows.jsonl", arms, a.workers)
    if a.analyze:
        analyze()


if __name__ == "__main__":
    main()
