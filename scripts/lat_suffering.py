"""Where living apart together's non-offsettable suffering comes from (docs/results/lat-suffering.md). Scripted persona agents, no model
calls, no model change: an instrumented rerun of H41's B and LAT arms under Amendment 6's flags (hybrid_leaving.CFGS["a6"]), reading the
lived world's need levels each week. Wording rule: agents feel nothing; "suffering" is a gloss for a modeled number.

  uv run python scripts/lat_suffering.py --run [--arms B,lat] [--version a6] [--workers 4]   rows in runs/lat-suffering/<version>.jsonl
  uv run python scripts/lat_suffering.py --analyze [--version a6]                             tables -> runs/lat-suffering/<version>.json

What it records, per lived member-week: where the member lives (household both in, alone in the household, LAT with Friend C, LAT alone,
apart with Friend C, apart alone), the unrounded need levels, which needs are under the denied line with enough salience, and the
non-offsettable suffering each condition adds once past its onset (hedonic.HedonicState.close_week's own rule, recomputed beside it and
checked against the row's s_non).
"""
import argparse
import json
import sys
import time
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import h41_choice_aids as A  # noqa: E402
import hybrid_exit_option as XO  # noqa: E402
import hybrid_leaving  # noqa: E402,F401  (registers the a6 configurations in XO.VERSIONS)
from mar import hedonic as HD  # noqa: E402
from mar.worlds import household as H  # noqa: E402

OUT = ROOT / "runs" / "lat-suffering"
NEEDS = HD.NEEDS
_LOG = []


def _mode(world, r):
    me, o = world.p[r], world.p[world.other(r)]
    if me["in"]:
        return "household" if o["in"] else "alone_in_household"
    lat = world.lat_on()
    friend = world.with_friend(r)
    return ("lat_" if lat else "apart_") + ("friend" if friend else "alone")


def _instrument():
    if getattr(H.WeeklyWorld.step_week, "_lat_wrapped", False):
        return
    real = H.WeeklyWorld.step_week

    def wrapped(self, w, last_week):
        lived_call = sys._getframe(1).f_code is XO.play.__code__      # only the lived week stepped by the harness loop, never a forecast
        pre = {r: _mode(self, r) for r in "AB"} if lived_call else None
        out = real(self, w, last_week)
        if pre is not None:
            row = self.run.outcomes[-1]["hedonic"]
            rec = {"w": w}
            for r in "AB":
                h = self.hed[r]
                cfg = h.cfg
                low = [n for n in NEEDS if h.level[n] < cfg.denied_below and h.sal[n] >= cfg.denied_min_salience]
                rec[r] = {"mode": pre[r], "lv": {n: round(h.level[n], 5) for n in NEEDS}, "low": low,
                          "run": dict(h.run), "s_non": row[r]["s_non"], "cond": row[r]["conditions"],
                          "money": float(self.p[r]["money"]), "share": float(self.share(r))}
            _LOG.append(rec)
        return out
    wrapped._lat_wrapped = True
    H.WeeklyWorld.step_week = wrapped


def task(args):
    arm, a, b, seed, version = args
    _instrument()
    _LOG.clear()
    t0 = time.time()
    run, lived, rd, ex = XO.play(arm, a, b, seed, version)
    weeks = list(_LOG)
    _LOG.clear()
    sal = {r: {n: round(lived.world.hed[r].sal[n], 5) for n in NEEDS} for r in "AB"}
    cfg = lived.world.hed["A"].cfg
    return {"arm": arm, "a": a, "b": b, "seed": seed, "version": version, "secs": round(time.time() - t0, 1), "sal": sal,
            "intens": {"trapped": cfg.trapped_intensity, "denied": cfg.denied_intensity, "diminished": cfg.diminished_intensity},
            "onset": cfg.onset_weeks, "term0": lived.week0.get("term"), "formed0": lived.week0.get("formed"),
            "exits": [{"week": e["week"], "role": e["role"]} for e in run.exits], "weeks": weeks}


def run_all(arms, version="a6", workers=4):
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f"{version}.jsonl"
    done = set()
    if f.exists():
        done = {(r["arm"], r["a"], r["b"]) for r in map(json.loads, f.open())}
    pairs = A.pairings(A.CONFIRM)
    tasks = [(arm, a, b, s, version) for (a, b) in pairs for arm in arms for s in A.CONFIRM["seeds"] if (arm, a, b) not in done]
    print(f"{version}: {len(tasks)} tasks, {min(workers, 4)} workers -> {f}", flush=True)
    t0 = time.time()
    with Pool(min(workers, 4)) as pool, f.open("a") as fh:
        for i, rec in enumerate(pool.imap_unordered(task, tasks, chunksize=1), 1):
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            if i % 20 == 0 or i == len(tasks):
                print(f"  {i}/{len(tasks)} last {rec['secs']:.0f}s wall {time.time() - t0:.0f}s", flush=True)


# ---- analysis --------------------------------------------------------------------------------------------------------------------

def contributions(rec):
    """Per member-week: the non-offsettable suffering each condition adds (close_week's rule: on, and on for at least onset weeks;
    clipped at 1 in total), and for denied, which needs were under the line. -> list of (role, week dict, {cond: amount}, recomputed)."""
    out = []
    for wk in rec["weeks"]:
        for r in "AB":
            m = wk[r]
            add = {}
            for k, on in m["cond"].items():
                if on and m["run"][k] >= rec["onset"]:
                    add[k] = rec["intens"][k]
            tot = min(1.0, sum(add.values()))
            out.append((r, wk["w"], m, add, tot))
    return out


def analyze(version="a6"):
    rows = [json.loads(x) for x in (OUT / f"{version}.jsonl").open()]
    res = {"version": version, "n": {}, "check": {}, "by_arm": {}}
    for arm in sorted({r["arm"] for r in rows}):
        rr = [r for r in rows if r["arm"] == arm]
        n_mw = 0
        tot = 0.0
        mismatch = 0
        by_cond = defaultdict(float)
        by_need = defaultdict(float)           # denied amount split equally among the needs under the line that week
        by_combo = defaultdict(float)
        by_mode = defaultdict(float)
        weeks_mode = defaultdict(int)
        by_mode_need = defaultdict(lambda: defaultdict(float))
        by_persona = defaultdict(float)
        persona_weeks = defaultdict(int)
        lone_cases = {"member_weeks": 0, "snon": 0.0, "runs": 0}
        runs_with = 0
        low_any = defaultdict(int)               # member-weeks with a need under the line (salient), by mode and need
        for rec in rr:
            has = False
            lone_run = False
            for r, w, m, add, t in contributions(rec):
                n_mw += 1
                weeks_mode[m["mode"]] += 1
                pid = rec["a"] if r == "A" else rec["b"]
                persona_weeks[pid] += 1
                for n in m["low"]:
                    low_any[(m["mode"], n)] += 1
                if abs(t - m["s_non"]) > 1e-3:
                    mismatch += 1
                if m["mode"] == "alone_in_household":
                    lone_cases["member_weeks"] += 1
                    lone_cases["snon"] += t
                    lone_run = True
                if t <= 0:
                    continue
                has = True
                tot += t
                by_mode[m["mode"]] += t
                by_persona[pid] += t
                for k, v in add.items():
                    by_cond[k] += v
                if "denied" in add:
                    low = m["low"] or ["(none recorded)"]
                    by_combo["+".join(sorted(low))] += add["denied"]
                    for n in low:
                        by_need[n] += add["denied"] / len(low)
                        by_mode_need[m["mode"]][n] += add["denied"] / len(low)
            runs_with += has
            lone_cases["runs"] += lone_run
        # per-run mean s_non (A.record's snon: mean over weeks of each member, then over both) for the check against the rows
        denom = n_mw                      # member-weeks
        scale = 1.0 / denom
        res["by_arm"][arm] = {
            "runs": len(rr), "runs_with_snon": runs_with, "member_weeks": n_mw, "recompute_mismatches": mismatch,
            "snon_per_member_week": tot * scale,
            "by_condition": {k: v * scale for k, v in by_cond.items()},
            "denied_by_need": {k: v * scale for k, v in sorted(by_need.items(), key=lambda x: -x[1])},
            "denied_by_combo": {k: v * scale for k, v in sorted(by_combo.items(), key=lambda x: -x[1])},
            "by_mode": {k: {"snon": by_mode.get(k, 0.0) * scale, "share_of_weeks": weeks_mode[k] / n_mw,
                            "snon_per_week_in_mode": by_mode.get(k, 0.0) / weeks_mode[k],
                            "by_need": {n: v * scale for n, v in by_mode_need[k].items()}} for k in sorted(weeks_mode)},
            "low_need_weeks": {f"{k[0]}:{k[1]}": v for k, v in sorted(low_any.items())},
            "by_persona": {p: {"snon": by_persona.get(p, 0.0) * scale, "per_week": by_persona.get(p, 0.0) / persona_weeks[p],
                               "weeks": persona_weeks[p]}
                           for p in sorted(persona_weeks, key=lambda p: -by_persona.get(p, 0.0)) if by_persona.get(p, 0.0) > 0},
            "lone": {"member_weeks": lone_cases["member_weeks"], "share_of_weeks": lone_cases["member_weeks"] / n_mw,
                     "snon": lone_cases["snon"] * scale, "runs": lone_cases["runs"]},
        }
    # the check: per-run snon as A.record computes it, against the A6 rows
    a6 = {(r["g"], r["a"], r["b"]): r["snon"] for r in A.load(ROOT / "runs" / "hybrid-a6" / "rows.jsonl")}
    for rec in rows:
        per = {r: np.mean([wk[r]["s_non"] for wk in rec["weeks"]]) for r in "AB"}
        mine = float(np.mean([per["A"], per["B"]]))
        key = (rec["arm"], rec["a"], rec["b"])
        if key in a6 and version == "a6":
            res["check"].setdefault(rec["arm"], []).append(abs(mine - a6[key]) < 1e-9)
    res["check"] = {k: f"{sum(v)} of {len(v)} runs match the A6 rows' snon" for k, v in res["check"].items()}
    (OUT / f"{version}.json").write_text(json.dumps(res, indent=1))
    show(res)
    return res


def show(res):
    print("check:", res["check"])
    for arm, d in res["by_arm"].items():
        print(f"\n== {arm}: {d['runs']} runs, {d['runs_with_snon']} with any; s_non per member-week {d['snon_per_member_week']:.5f}; "
              f"recompute mismatches {d['recompute_mismatches']}")
        print("  by condition:", {k: round(v, 5) for k, v in d["by_condition"].items()})
        print("  denied by need:", {k: round(v, 5) for k, v in d["denied_by_need"].items()})
        print("  denied by combo:", {k: round(v, 5) for k, v in d["denied_by_combo"].items()})
        for k, m in d["by_mode"].items():
            print(f"  mode {k:<20} weeks {m['share_of_weeks']:.3f}  snon {m['snon']:.5f}  per week in mode {m['snon_per_week_in_mode']:.5f}  "
                  f"{ {n: round(v, 5) for n, v in m['by_need'].items()} }")
        print("  low-need weeks:", d["low_need_weeks"])
        print("  personas:", {p: (round(v['snon'], 5), round(v['per_week'], 4)) for p, v in list(d["by_persona"].items())[:12]})
        print("  lone:", d["lone"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--arms", default="B,lat")
    ap.add_argument("--version", default="a6")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.run:
        run_all(a.arms.split(","), a.version, a.workers)
    if a.analyze:
        analyze(a.version)


if __name__ == "__main__":
    main()
