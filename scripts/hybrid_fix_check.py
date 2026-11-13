"""The hybrid's Amendment 3 pass test K1 (docs/results/hybrid-agent-prereg.md): the stay test's trap and baseline fixtures under the
hybrid in the step-3 world, the formation check's 12 control pairings and seed 900, with the suffering weight (hybrid_w) and readings
run by the world (hybrid_readings) off, each alone, and both on. K1 passes iff, with both on, the held share is at least 0.10 in the trap
and at most 0.02 in the baseline. Scripted agents, no model calls. Wording rule: agents feel nothing.

  uv run python scripts/hybrid_fix_check.py --trap      rows in runs/hybrid-fix/trap.json (at most 4 workers)
"""
import argparse
import dataclasses
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import formation_check_3 as FC3  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import pairing as PR  # noqa: E402

OUT = ROOT / "runs" / "hybrid-fix"
CONFIGS = {"off": {}, "readings": {"hybrid_readings": "world"}, "w": {"hybrid_w": "persona"},
           "both": {"hybrid_readings": "world", "hybrid_w": "persona"}}
A4 = {"both": {"hybrid_readings": "world", "hybrid_w": "persona"},
      "a4": {"hybrid_readings": "world", "hybrid_w": "persona", "hybrid_lone": True, "hybrid_exit": True},
      "a4_lone": {"hybrid_readings": "world", "hybrid_w": "persona", "hybrid_lone": True},
      "a4_exit": {"hybrid_readings": "world", "hybrid_w": "persona", "hybrid_exit": True}}   # Amendment 4 (hybrid-exit-option-prereg.md)
BARS = {"trap_min": 0.10, "baseline_max": 0.02}


def _one(args):
    from mar import retest as RT
    from mar import stay_test as ST
    from mar.worlds import household as H
    import stay_test_run as STR
    cfg, arm, a, b, seed = args
    ps = STR.personas()
    fx = dataclasses.replace(RT.FIXES_ON, pairing=PR.dial(0), **FC3.rule("hybrid"), **{**CONFIGS, **A4}[cfg])
    t0 = time.time()
    with HD.use_levers(RT.LEVERS), HD.use_fixes(fx):
        world = H.WeeklyWorld(H.PyGate(H.load_variant(arm)), (ps[a], ps[b]), seed, H.WEEKS)
        run, weeks = ST.play_with_stay_test(world, bar=False)
    rec = STR.compact(weeks)
    flags = STR.held_week_flags(rec)
    return {"cfg": cfg, "arm": arm, "a": a, "b": b, "staying": len(flags), "held": int(sum(flags)), "secs": round(time.time() - t0, 1),
            "exits": len(run.exits), "ended": not run.outcomes[-1]["both_in"]}


def trap(workers=4, n_pairs=12, configs=None, key="both", fname="trap.json"):
    """K1. configs: the configurations to run (Amendment 3: CONFIGS, K1 read on "both"; Amendment 4: A4, K1 read on "a4")."""
    import stay_test_run as STR
    configs = configs or CONFIGS
    pairs = [(a, b) for a, b, c in STR.pairings() if c == "ctl"][:n_pairs]
    tasks = [(c, arm, a, b, 900) for c in configs for arm in ("trap", "baseline") for a, b in pairs]
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(min(workers, 4)) as p:
        recs = p.map(_one, tasks, chunksize=1)
    out = {"rows": recs, "secs": round(time.time() - t0), "summary": {}}
    for c in configs:
        out["summary"][c] = {}
        for arm in ("trap", "baseline"):
            xs = [r for r in recs if r["cfg"] == c and r["arm"] == arm]
            n, h = sum(r["staying"] for r in xs), sum(r["held"] for r in xs)
            out["summary"][c][arm] = {"held_share": h / n if n else None, "staying_weeks": n, "runs": len(xs),
                                      "ended": sum(r["ended"] for r in xs), "secs_mean": sum(r["secs"] for r in xs) / len(xs)}
        print(c, out["summary"][c], flush=True)
    s = out["summary"][key]
    out["K1"] = "PASS" if (s["trap"]["held_share"] or 0) >= BARS["trap_min"] and (s["baseline"]["held_share"] or 0) <= BARS["baseline_max"] \
        else "FAIL"
    print("K1", out["K1"])
    (OUT / fname).write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--trap", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--a4", action="store_true", help="Amendment 4: K1 with all four flags; each new flag alone beside; trap-a4.json")
    a = ap.parse_args()
    if a.trap and a.a4:
        trap(a.workers, configs=A4, key="a4", fname="trap-a4.json")
    elif a.trap:
        trap(a.workers)
