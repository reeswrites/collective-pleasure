"""H39b makers rerun (docs/results/h39b-makers-rerun-prereg.md): H39 with no fitted time cost. A block of making is chosen against
the agent's own best other use of the time (the opportunity choice in src/mar/makers.py), enjoyment of making can be negative, and
two wanting-trap measures sit beside pleasure. Everything else is H39 (scripts/h39_makers_run.py): arms, pairings, seeds, analysis.
Scripted persona agents, no model calls. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

  uv run python scripts/h39b_makers_rerun.py --pilot      EXPLORATORY (pilot pairings, seeds 900-901; for the power check only)
  uv run python scripts/h39b_makers_rerun.py --power      the power check on the pilot rows
  uv run python scripts/h39b_makers_rerun.py --reach      the free checks for "Can every verdict happen?"
  uv run python scripts/h39b_makers_rerun.py --run        13 arms x 120 pairings x 4 seeds (at most 3 workers)
  uv run python scripts/h39b_makers_rerun.py --analyze    prereg vs actual plus the H39b measures; runs/h39b-makers/analysis.json
  uv run python scripts/h39b_makers_rerun.py --observe    observer sample: 20 pairings, seed 0, M0 / Z / BP
  uv run python scripts/h39b_makers_rerun.py --stories    the five H39 story picks, under H39b
  add --v2 to --run / --analyze: Amendment 2, the recalibrated agents and bills that hurt (rows in runs/h39b-makers-v2/)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import h38_pairing_run as H38  # noqa: E402
import h39_makers_run as H39  # noqa: E402
from mar import makers as MK  # noqa: E402

OUT = ROOT / "runs" / "h39b-makers"
OVR = {"choice": "opportunity", "enjoy": MK.ENJOY_H39B}
H39.OUT = OUT
H39.BASE_OVERRIDES = OVR
STORIES = "Z|p-anchor|p-bargainer|0;BP|p-anchor|p-bargainer|0;BP-PN|g-11011|p-host|0;BP|g-00010|p-host|0;A|g-00001|p-anchor|0"
PILOT_ARMS = ("Z", "H", "P", "BP", "BP-PN", "M0")


def _sum(d):
    return float(sum(d.values()))


EXTRA = {
    "lost": lambda r: _sum(r["mk"]["lost_tol"]) if r.get("mk") else None,
    "lost_share": lambda r: (_sum(r["mk"]["lost_tol"]) / (_sum(r["mk"]["lost_tol"]) + _sum(r["mk"]["like_got"])))
    if r.get("mk") and (_sum(r["mk"]["lost_tol"]) + _sum(r["mk"]["like_got"])) > 0 else (0.0 if r.get("mk") else None),
    "trap": lambda r: _sum(r["mk"]["trap_weeks"]) / (2 * r["mk"]["weeks_seen"]) if r.get("mk") and r["mk"]["weeks_seen"] else None,
    "tol": lambda r: _sum(r["mk"]["tol_weeks"]) / (2 * r["mk"]["weeks_seen"]) if r.get("mk") and r["mk"]["weeks_seen"] else None,
    "l2w": lambda r: _sum(r["mk"]["like_got"]) / _sum(r["mk"]["want_got"]) if r.get("mk") and _sum(r["mk"]["want_got"]) > 0 else None,
    "slack": lambda r: r["mk"]["dec"]["slack_blocks"] / r["mk"]["dec"]["blocks"] if r.get("mk") and r["mk"]["dec"]["blocks"] else None,
    "made_any": lambda r: float(sum(r["mk"]["blocks"].values()) > 0) if r.get("mk") else None,
}
H39.K.update(EXTRA)


def trap_while_happy(rows, arm):
    """Person-level disagreement check: a partner with a trap share >= 0.25 of their weeks whose clipped pleasure is >= 0.95."""
    n = k = 0
    for r in rows:
        if r["arm"] != arm or not r.get("mk") or not r["mk"]["weeks_seen"]:
            continue
        for x in "AB":
            if r["mk"]["trap_weeks"][x] / r["mk"]["weeks_seen"] >= 0.25:
                n += 1
                k += r[x]["pl"] >= 0.95 if isinstance(r.get(x), dict) and "pl" in r[x] else 0
    return {"trapped_persons": n, "of_them_pleasure_ge_095": k}


def decomposition(rows, arm, keep=None):
    xs = [r["mk"]["dec"] for r in rows if r["arm"] == arm and r.get("mk") and (keep is None or keep(r))]
    if not xs:
        return None
    tot = {k: float(sum(x[k] for x in xs)) for k in ("maker_weeks", "blocks", "v_proc", "v_care", "v_own", "v_motive", "alt_cost",
                                                     "slack_blocks", "zero_weeks")}
    disp = {}
    for x in xs:
        for a, v in x["displaced"].items():
            disp[a] = disp.get(a, 0) + v
    b = tot["blocks"] or 1.0
    return {"maker_weeks": tot["maker_weeks"], "blocks_per_maker_week": tot["blocks"] / (tot["maker_weeks"] or 1),
            "zero_share": tot["zero_weeks"] / (tot["maker_weeks"] or 1), "slack_share_of_blocks": tot["slack_blocks"] / b,
            "per_block": {k[2:]: round(tot[k] / b, 5) for k in ("v_proc", "v_care", "v_own", "v_motive")},
            "alt_cost_per_block": round(tot["alt_cost"] / b, 5),
            "displaced_per_100_blocks": {a: round(100 * v / b, 2) for a, v in sorted(disp.items(), key=lambda t: -t[1])}}


def analyze(rows, write=True, path=None):
    res = H39.analyze(rows, write=False)
    arms = sorted({r["arm"] for r in rows})
    C = res["comps"]
    have = set(arms)

    def c(name, hi, lo, key, alt=None, keep=None):
        if hi in have and lo in have:
            C[name] = H39.comp(rows, hi, lo, H39.K[key], alt, keep)
    for a in arms:
        xs = [r for r in rows if r["arm"] == a]
        for k in EXTRA:
            res["arms"][a][k] = H39._mean([EXTRA[k](r) for r in xs])
        res["arms"][a]["lost_ext"] = H39._mean([EXTRA["lost"](r) for r in xs if H39.ANY_EXT(r)])
        res["arms"][a]["lost_noext"] = H39._mean([EXTRA["lost"](r) for r in xs if r.get("mk") and not H39.ANY_EXT(r)])
        res["arms"][a]["trap_ext"] = H39._mean([EXTRA["trap"](r) for r in xs if H39.ANY_EXT(r)])
        res["arms"][a]["trap_noext"] = H39._mean([EXTRA["trap"](r) for r in xs if r.get("mk") and not H39.ANY_EXT(r)])
        res["arms"][a]["decomposition"] = decomposition(rows, a)
        res["arms"][a]["decomposition_ext_makers"] = decomposition(rows, a, H39.ANY_EXT)
    for a in ("BP", "H", "P", "G", "A"):
        for k in ("lost", "trap", "lost_share"):
            c(f"{a}-Z {k}", a, "Z", k)
    c("P-H lost ext", "P", "H", "lost", None, H39.ANY_EXT)
    c("P-H trap ext", "P", "H", "trap", None, H39.ANY_EXT)
    c("Z-M0 net", "Z", "M0", "net")
    c("Z-M0 formed0", "Z", "M0", "formed0")
    c("Z-M0 together", "Z", "M0", "together")
    c("BP-M0 p_raw", "BP", "M0", "p_raw")
    c("BP-G p_raw (motive)", "BP", "G", "p_raw")
    c("BP-G bpw (motive)", "BP", "G", "bpw")
    res["trap_while_happy"] = {a: trap_while_happy(rows, a) for a in arms}
    if write:
        (path or OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    return res


def pilot():
    H39.run(PILOT_ARMS, H38.pairings(H38.PILOT), H38.PILOT["seeds"], OUT / "pilot.jsonl", overrides=OVR)
    res = analyze(H38.load(OUT / "pilot.jsonl"), path=OUT / "pilot-analysis.json")
    print(json.dumps({a: {k: res["arms"][a].get(k) for k in ("pleasure", "p_raw", "formed0", "together", "bpw", "lost", "trap", "slack")}
                      for a in res["arms"]}, indent=1, default=str))
    print(json.dumps({k: v for k, v in res["comps"].items() if "est" in v}, indent=1, default=str))


def power():
    rows = H38.load(OUT / "pilot.jsonl")
    from mar import stats as ST
    out = {}
    for name, hi, lo, key, keep, eff in (("P1", "BP", "Z", "pleasure", None, H39.MARGIN), ("P3", "H", "Z", "e0_share", H39.ANY_E0, 0.03),
                                         ("P5", "H", "P", H39.ext_share, H39.ONE_EXT, 0.05),
                                         ("P5b", "P", "H", "pleasure", H39.ANY_EXT, None), ("P6a", "BP-PN", "BP", "started", H39.ANY_ART, 0.20),
                                         ("P6b", "BP-PN", "BP", "paid", H39.ANY_ART, 0.10), ("P6c", "BP-PN", "BP", "pleasure", H39.ANY_ART, None)):
        d, ks, _, _ = H39.paired(rows, hi, lo, H39.K[key] if isinstance(key, str) else key, keep)
        sd = float(d.std(ddof=1)) if len(d) > 1 else None
        e = eff if eff is not None else max(abs(float(d.mean())), 1e-4)
        out[name] = {"pilot_est": float(d.mean()) if len(d) else None, "pilot_sd": sd, "n_pilot": len(ks), "effect_used": e,
                     "units_80": ST.seeds_for_power(e, sd, target=0.8, alpha=0.05, paired=True) if sd else None}
    print(json.dumps(out, indent=1))
    (OUT / "power.json").write_text(json.dumps(out, indent=1))
    return out


def reach():
    out = H39.reach()       # relabelled pilot rows and parameter flips, with the opportunity choice (BASE_OVERRIDES)
    rows = H38.load(OUT / "pilot.jsonl")
    ex = [r for r in rows if r.get("mk")]
    out["h39b_measures_pilot"] = {
        "made_nothing_runs": sum(1 for r in ex if sum(r["mk"]["blocks"].values()) == 0), "runs": len(ex),
        "made_full_max": max(r["mk"]["bpw"] or 0 for r in ex),
        "trap_zero_runs": sum(1 for r in ex if EXTRA["trap"](r) == 0), "trap_pos_runs": sum(1 for r in ex if (EXTRA["trap"](r) or 0) > 0),
        "lost_zero_runs": sum(1 for r in ex if EXTRA["lost"](r) == 0), "lost_pos_runs": sum(1 for r in ex if (EXTRA["lost"](r) or 0) > 0),
        "trap_pos_without_ext": sum(1 for r in ex if (EXTRA["trap"](r) or 0) > 0 and not H39.ANY_EXT(r)),
    }
    print(json.dumps(out["h39b_measures_pilot"], indent=1))
    (OUT / "reach.json").write_text(json.dumps(out, indent=1, default=str))
    return out


SAMPLE = []
TIME = ("work", "rest", "see_friend", "together", "spend_self", "spend_shared")


def fidelity(n=10, seeds=(900,)):
    """Known-answer check of the planner against the world itself (makers off, the M0 world): at each week's start, while both
    partners live together, plan each partner's week (a) from fixed start-of-week utilities and (b) with the WeekPlanner, and
    compare with the time actions the agent then executes (own initiations; a partner-initiated session counts for the partner).
    Reported: exact match of the action multiset, and mean units planned minus units used."""
    from collections import Counter
    from mar.worlds import household as H
    pairs = H38.pairings(H38.PILOT)[:n]
    acc = {"fixed": {"match": 0, "units_diff": 0.0}, "planner": {"match": 0, "units_diff": 0.0}, "weeks": 0}
    orig_agent = H.WeeklyWorld.step_agent
    store = {}

    def step_agent(self, r, w, last, rec):
        before = len(self.run.trace)
        orig_agent(self, r, w, last, rec)
        if id(self) in store and len(self.run.trace) > before and self.run.trace[-1]["executed"]:
            store[id(self)]["acts"][r].append(self.run.trace[-1]["action"])
    H.WeeklyWorld.step_agent = step_agent
    try:
        for a, b in pairs:
            for sd in seeds:
                def hook(world, w):
                    prev = store.get(id(world))
                    if prev and prev["plans"]:
                        _score(prev)
                    store[id(world)] = {"plans": None, "acts": {"A": [], "B": []}}
                    if all(world.p[x]["in"] for x in "AB"):
                        wp = {r: MK.WeekPlanner(world, r, w) for r in "AB"}
                        k = {r: MK.plan_week(wp[world.other(r)], world.units[world.other(r)])[1].count("together") for r in "AB"}
                        store[id(world)]["plans"] = {
                            r: {"fixed": MK.plan_week(MK.week_utilities(world, r, w), world.units[r])[1],
                                "planner": [x for x in MK.plan_value(wp[r], world.units[r], partner_sessions=k[r])[1]
                                            if x != "partner_together"]} for r in "AB"}

                def _score(rec):
                    acc["weeks"] += 1
                    for r in "AB":
                        done = Counter(x for x in rec["acts"][r] if x in TIME)
                        for k in ("fixed", "planner"):
                            pl = Counter(rec["plans"][r][k])
                            acc[k]["match"] += int(pl == done) / 2
                            if k == "planner" and len(SAMPLE) < 25 and pl != done:
                                SAMPLE.append((dict(pl), dict(done)))
                            acc[k]["units_diff"] += (sum(H.V2_COST[x] * c for x, c in pl.items())
                                                     - sum(H.V2_COST[x] * c for x, c in done.items())) / 2
                H39.BASE_OVERRIDES = {}
                import h38_pairing_run as _H38
                from mar import pairing as PR
                orig_ww = H.WeeklyWorld.__init__

                def init(self, *x, **k):
                    orig_ww(self, *x, **k)
                    self.hook = hook
                H.WeeklyWorld.__init__ = init
                try:
                    _H38.play(PR.dial(0), a, b, sd, stay=False, rule=H39.RULE_W, weeks=52)
                finally:
                    H.WeeklyWorld.__init__ = orig_ww
                    H39.BASE_OVERRIDES = OVR
    finally:
        H.WeeklyWorld.step_agent = orig_agent
    n_w = acc["weeks"] or 1
    out = {k: {"match": acc[k]["match"] / n_w, "units_planned_minus_used": acc[k]["units_diff"] / n_w} for k in ("fixed", "planner")}
    out["partner_weeks"] = acc["weeks"]
    out["mismatch_sample"] = SAMPLE
    print(json.dumps({k: v for k, v in out.items() if k != "mismatch_sample"}, indent=1))
    (OUT / "fidelity.json").write_text(json.dumps(out, indent=1))
    return out


def observe():
    out = H39.observe_sample()
    rows = H38.load(OUT / "rows.jsonl")
    keys = {tuple(p) for p in H38.pairings(H38.CONFIRM)[:20]}
    sample = [r for r in rows if (r["a"], r["b"]) in keys and r["seed"] == 0]
    out["making_decisions"] = {a: decomposition(sample, a) for a in ("Z", "BP")}
    print(json.dumps(out["making_decisions"], indent=1))
    (OUT / "observer-sample.json").write_text(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    for f in ("pilot", "power", "reach", "run", "analyze", "observe", "fidelity"):
        ap.add_argument(f"--{f}", action="store_true")
    ap.add_argument("--arms", default=",".join(H39.ARMS))
    ap.add_argument("--seeds", type=int, default=4)
    ap.add_argument("--stories", nargs="?", const=STORIES, default="")
    ap.add_argument("--v2", action="store_true", help="Amendment 2: agent_values v2 and bills_hurt; runs/h39b-makers-v2/")
    ap.add_argument("--v2nobills", action="store_true", help="descriptive: v2 with bills off, arms M0, Z, BP; runs/h39b-makers-v2-nobills/")
    a = ap.parse_args()
    global OUT
    fix = None
    if a.v2:
        OUT = ROOT / "runs" / "h39b-makers-v2"
        H39.OUT = OUT
        fix = {"agent_values": "v2", "bills_hurt": True}
    if a.v2nobills:
        OUT = ROOT / "runs" / "h39b-makers-v2-nobills"
        H39.OUT = OUT
        fix = {"agent_values": "v2"}
        if a.arms == ",".join(H39.ARMS):
            a.arms = "M0,Z,BP"
    OUT.mkdir(parents=True, exist_ok=True)
    if a.fidelity:
        fidelity()
    if a.pilot:
        pilot()
    if a.power:
        power()
    if a.reach:
        reach()
    if a.run:
        H39.run(a.arms.split(","), H38.pairings(H38.CONFIRM), tuple(range(a.seeds)), OUT / "rows.jsonl", overrides=OVR, fix=fix)
    if a.analyze:
        res = analyze(H38.load(OUT / "rows.jsonl"), path=OUT / "analysis.json")
        print(json.dumps(res["verdicts"], indent=1))
    if a.observe:
        observe()
    if a.stories:
        H39.stories([(x.split("|")[0], x.split("|")[1], x.split("|")[2], int(x.split("|")[3])) for x in a.stories.split(";")])


if __name__ == "__main__":
    main()
