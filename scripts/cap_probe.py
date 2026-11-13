"""Does the weekly cap explain why accurate agents leave households? (docs/results/pleasure-scale.md; step 1 of
docs/notes/step-back-review.md). A mechanism probe, not a hypothesis test: no verdict, no parameter changed.

World: the H38 formation check's G-L0 arm (H38 baseline, pairing dial 0, F4 with items, the corrected rule: decide on pleasure over
52 weeks). Pairings: H38's 120 confirmatory pairings, seed 0. Scripted agents, no model calls.

Part A, the household's benefit, measured on one set of lives (old scale): at week 0, the household under the baseline (the rule's own
52-week rollout) against each member's outside option (the better of alone and with Friend C). Each week's raw pleasure is read from the
rows, and the benefit (household minus outside, per member) is computed on three scales: raw (no cap), the old clip, and the saturating
curve (ADR 0019). The share of the raw benefit above the cap is 1 - clip/raw.
Part B, the formation rule run on each scale: week-0 formation with the agents, the spiral and the rule all on the old or the new scale.
Part C, leaving: formation forced at week 0, lived 52 weeks with the readings at 13, 26 and 39; the share of readings whose outside
option beats staying, and households ended by week 52, on each scale.

Agent sets: v1, v2 (no bills), v2 with bills that hurt.

  uv run python scripts/cap_probe.py --run       (at most 3 workers; rows in runs/cap-probe/)
  uv run python scripts/cap_probe.py --analyze
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
from mar import exit_fallback as EF  # noqa: E402
from mar import exit_items as EI  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import negotiation as NG  # noqa: E402
from mar import pairing as PR  # noqa: E402
from mar import retest as RT  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "cap-probe"
GOOD = {"decide_on": "pleasure", "decide_weeks": 52}
AGENTS = {"v1": {}, "v2": {"agent_values": "v2"}, "v2+bills": {"agent_values": "v2", "bills_hurt": True}}
SCALES = {"clip": {}, "sat": {"pleasure_scale": "sat"}}
KNEE = HD.FixConfig().sat_knee


def _fx(agents, scale):
    return dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **GOOD, **AGENTS[agents], **SCALES[scale])


def _ctx(fx):
    return (HD.use_levers(RT.LEVERS), HD.use_fixes(fx), EF.use_exit_fallback("F4", strip_split=True), EI.use_items(EI.GRID[H38.CELL]))


def _raws(run, role):
    return [o["hedonic"][role]["p_raw"] for o in run.outcomes]


def _three(xs):
    return {"raw": float(np.mean(xs)), "clip": float(np.mean([min(1.0, max(0.0, x)) for x in xs])),
            "sat": float(np.mean([HD.saturate(x, KNEE) for x in xs]))}


def part_a(a, b, seed, agents):
    """Week-0 household and outside rollouts on the old scale; their weekly raw pleasure read on three scales."""
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    fx = _fx(agents, "clip")
    cms = _ctx(fx)
    for cm in cms:
        cm.__enter__()
    try:
        weeks = 52
        wd = H.WeeklyWorld(H.load_variant("baseline"), (ps[a], ps[b]), seed, weeks)
        hh = wd.play()
        out = {}
        hold = NG.START_HOLDINGS[0] + NG.START_HOLDINGS[1]
        for r, pid in (("A", a), ("B", b)):
            best = None
            for mode in ("alone", "friend"):
                w = H.WeeklyWorld(NG._solo_cards(), (ps[pid], ps[pid]), seed, weeks, deal={"pot": False, "commits": []})
                for x in "AB":
                    w.p[x]["in"], w.p[x]["money"] = False, hold
                w.pool, w.put = 0, {"A": 0, "B": 0}
                w.solo = mode
                run = w.play()
                v = _three(_raws(run, r))
                if best is None or v["clip"] > best["clip"]:         # the old rule's own choice of arrangement
                    best = v
            hv = _three(_raws(hh, r))
            out[r] = {"hh": hv, "out": best, "hh_top_old": float(np.mean([x >= 1.0 for x in _raws(hh, r)])),
                      "hh_top_new": float(np.mean([HD.saturate(x, KNEE) >= 0.95 for x in _raws(hh, r)]))}
        return out
    finally:
        for cm in reversed(cms):
            cm.__exit__(None, None, None)


def part_b(a, b, seed, agents, scale):
    """The week-0 formation rule with agents, spiral and rule on one scale. -> {"formed": bool, "W", "O"}."""
    ps = RT.personas()
    for c in (NG._RC, NG._PC, NG._BC):
        c.clear()
    cms = _ctx(_fx(agents, scale))
    for cm in cms:
        cm.__enter__()
    try:
        lived = NG.BaselineLived(ps[a], ps[b], seed, H.load_variant("baseline"), weeks=H.WEEKS, decline=True)
        return {"formed": not lived.apart, "W": lived.week0["W"], "O": lived.week0["O"]}
    finally:
        for cm in reversed(cms):
            cm.__exit__(None, None, None)


def part_c(a, b, seed, agents, scale):
    """Formation forced at week 0, 52 weeks lived with readings: readings whose outside option beats staying, and the end."""
    run, lived, _ = H38.play(PR.dial(0), a, b, seed, stay=False, weeks=52, rule={**GOOD, **AGENTS[agents], **SCALES[scale]},
                             decline=False)
    reads = [(x["outside"][r] > x["baseline"][r]) for x in lived.log for r in "AB"]
    both = [o["both_in"] for o in run.outcomes]
    return {"readings": len(reads), "outside_wins": int(sum(reads)), "ended": not both[-1], "weeks_together": float(np.mean(both)),
            "pl": float(np.mean([o["hedonic"][r]["pleasure"] for o in run.outcomes for r in "AB"]))}


def task(args):
    a, b, seed = args
    t0 = time.time()
    rec = {"a": a, "b": b, "seed": seed, "A": {}, "B": {}, "C": {}}
    for ag in AGENTS:
        rec["A"][ag] = part_a(a, b, seed, ag)
        rec["B"][ag] = {sc: part_b(a, b, seed, ag, sc) for sc in SCALES}
        rec["C"][ag] = {sc: part_c(a, b, seed, ag, sc) for sc in SCALES}
    return rec, time.time() - t0


def run(workers=3, seeds=(0,)):
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / "rows.jsonl"
    done = {(r["a"], r["b"], r["seed"]) for r in load(f)} if f.exists() else set()
    tasks = [(a, b, s) for (a, b) in H38.pairings(H38.CONFIRM) for s in seeds if (a, b, s) not in done]
    print(f"{len(tasks)} tasks, {min(3, workers)} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(min(3, workers)) as pool, f.open("a") as fh:
        for i, (rec, dt) in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            if i % 10 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {dt:.1f}s wall {time.time() - t0:.0f}s", flush=True)


def load(f):
    return [json.loads(x) for x in Path(f).read_text().splitlines() if x.strip()]


def boot(xs, n=4000, seed=0):
    xs = np.asarray(xs, dtype=float)
    rng = np.random.default_rng(seed)
    bs = [xs[rng.integers(0, len(xs), len(xs))].mean() for _ in range(n)]
    return [round(float(xs.mean()), 4), round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]


def analyze():
    rows = load(OUT / "rows.jsonl")
    res = {"n_pairings": len(rows)}
    for ag in AGENTS:
        A = [x["A"][ag][r] for x in rows for r in "AB"]
        ben = {sc: [m["hh"][sc] - m["out"][sc] for m in A] for sc in ("raw", "clip", "sat")}
        pos = [i for i, x in enumerate(ben["raw"]) if x > 0]
        tot_raw = sum(ben["raw"][i] for i in pos)
        part = {"benefit": {sc: boot(v) for sc, v in ben.items()},
                "household_pleasure": {sc: boot([m["hh"][sc] for m in A]) for sc in ("raw", "clip", "sat")},
                "outside_pleasure": {sc: boot([m["out"][sc] for m in A]) for sc in ("raw", "clip", "sat")},
                "share_above_cap_old": round(1 - sum(ben["clip"][i] for i in pos) / tot_raw, 4) if tot_raw else None,
                "share_above_curve_new": round(1 - sum(ben["sat"][i] for i in pos) / tot_raw, 4) if tot_raw else None,
                "members_gain": {sc: round(float(np.mean([v > 0 for v in ben[sc]])), 4) for sc in ben},
                "pairs_form_static": {sc: round(float(np.mean([x["A"][ag]["A"]["hh"][sc] > x["A"][ag]["A"]["out"][sc]
                                                               and x["A"][ag]["B"]["hh"][sc] > x["A"][ag]["B"]["out"][sc] for x in rows])), 4)
                                      for sc in ("raw", "clip", "sat")},
                "hh_weeks_at_top": {"old_cap": round(float(np.mean([m["hh_top_old"] for m in A])), 4),
                                    "new_ge_0.95": round(float(np.mean([m["hh_top_new"] for m in A])), 4)}}
        partb = {sc: round(float(np.mean([x["B"][ag][sc]["formed"] for x in rows])), 4) for sc in SCALES}
        partc = {}
        for sc in SCALES:
            cs = [x["C"][ag][sc] for x in rows]
            partc[sc] = {"outside_wins_share": round(sum(c["outside_wins"] for c in cs) / max(1, sum(c["readings"] for c in cs)), 4),
                         "ended_by_52": round(float(np.mean([c["ended"] for c in cs])), 4),
                         "weeks_together": round(float(np.mean([c["weeks_together"] for c in cs])), 4),
                         "pleasure": round(float(np.mean([c["pl"] for c in cs])), 4)}
        res[ag] = {"A_static": part, "B_formed_week0": partb, "C_forced_52wk": partc}
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    if a.run:
        run(a.workers)
    if a.analyze:
        analyze()
