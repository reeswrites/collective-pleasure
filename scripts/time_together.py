"""Time together in two kinds: analysis (docs/results/time-together-prereg.md). Reads H41's rows under A6 (runs/hybrid-a6/rows.jsonl)
and under TT (runs/time-together/*.jsonl, written by hybrid_leaving.py --run tt...). No model calls. Wording rule: agents feel nothing.

  uv run python scripts/time_together.py --analyze      -> runs/time-together/analysis.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import h41_choice_aids as A  # noqa: E402
import hybrid_exit_option as XO  # noqa: E402
import hybrid_leaving as L  # noqa: E402
from mar import hedonic as HD  # noqa: E402
from mar import retest as RT  # noqa: E402

OUT = ROOT / "runs" / "time-together"
KEYS = ("together", "formed0", "liberty", "pleasure", "lived", "snon")


def s_of(pid):
    w = RT.personas()[pid].weights
    return w["togetherness"] / (w["togetherness"] + w["other_connections"])


def term0_lat(rows, arm="lat"):
    xs = [r for r in rows if r["g"] == arm]
    return {"n": len(xs), "lat_at_week0": sum(1 for r in xs if r.get("term0") == "lat"),
            "lat_weeks": float(np.mean([r["lat"] for r in xs])) if xs else None}


def slope_tt4(rows, arm="lat", n=2000):
    """TT4: per member, (pleasure in the LAT arm) - (pleasure in B), regressed on s; pairing bootstrap. Only pairings in both arms."""
    b = {(r["a"], r["b"]): r for r in rows if r["g"] == "B"}
    pts = []
    for r in rows:
        if r["g"] != arm or (r["a"], r["b"]) not in b:
            continue
        rb = b[(r["a"], r["b"])]
        for role, pid in (("A", r["a"]), ("B", r["b"])):
            pts.append(((r["a"], r["b"]), s_of(pid), r[role]["pl"] - rb[role]["pl"]))
    if len(pts) < 4:
        return None
    keys = sorted({k for k, _, _ in pts})
    by = {k: [(s, d) for kk, s, d in pts if kk == k] for k in keys}

    def fit(sel):
        xs = np.array([s for k in sel for s, _ in by[k]])
        ys = np.array([d for k in sel for _, d in by[k]])
        return float(np.polyfit(xs, ys, 1)[0]) if len(set(xs)) > 1 else 0.0
    est = fit(keys)
    rng = np.random.default_rng(0)
    bs = [fit([keys[i] for i in rng.integers(0, len(keys), len(keys))]) for _ in range(n)]
    # members by tercile of s
    ss = np.array([s for _, s, _ in pts])
    ds = np.array([d for _, _, d in pts])
    cuts = np.quantile(ss, [1 / 3, 2 / 3])
    terc = {name: float(ds[m].mean()) for name, m in (("low s", ss <= cuts[0]), ("mid s", (ss > cuts[0]) & (ss <= cuts[1])),
                                                      ("high s", ss > cuts[1])) if m.any()}
    return {"slope": est, "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "members": len(pts), "by_tercile": terc}


def within_life(version="tt"):
    """TT4's second measure: from the instrumented LAT-arm rows (lat_suffering.py --version X), each member's mean weekly pleasure in
    LAT weeks minus in household weeks, against s."""
    f = ROOT / "runs" / "lat-suffering" / f"{version}.jsonl"
    if not f.exists():
        return None
    pts = []
    for line in f.open():
        rec = json.loads(line)
        if rec["arm"] != "lat":
            continue
        for role, pid in (("A", rec["a"]), ("B", rec["b"])):
            lat = [wk[role]["pl"] for wk in rec["weeks"] if wk[role]["mode"].startswith("lat") and "pl" in wk[role]]
            hh = [wk[role]["pl"] for wk in rec["weeks"] if wk[role]["mode"] == "household" and "pl" in wk[role]]
            if len(lat) >= 13 and len(hh) >= 13:
                pts.append((s_of(pid), float(np.mean(lat)) - float(np.mean(hh))))
    if len(pts) < 4:
        return {"members": len(pts)}
    xs, ys = np.array([p[0] for p in pts]), np.array([p[1] for p in pts])
    return {"members": len(pts), "slope": float(np.polyfit(xs, ys, 1)[0]), "mean": float(ys.mean())}


def analyze():
    a6 = A.load(L.cfg_file("a6"))
    tt = A.load(L.cfg_file("tt")) if L.cfg_file("tt").exists() else []
    have = [x for x in A.ARMS if any(r["g"] == x for r in tt)]
    res = {"n_tt": len(tt), "arms_present": have}
    res["arms"] = {v: {arm: A.arm_means(rows, arm, A.KEYS) for arm in have} for v, rows in (("a6", a6), ("tt", tt))}
    res["paired_tt_minus_a6"] = {arm: {k: L.paired_diff(tt, a6, arm, k) for k in KEYS} for arm in have}
    for arm, d in res["paired_tt_minus_a6"].items():
        for k, v in d.items():
            if v:
                v["class"] = A.classify(v["d"], v["ci"], XO.CLASS_KEYS.get(k, 0.01) if hasattr(XO, "CLASS_KEYS") else 0.01)
    arms = [x for x in have if x != "B"]
    if arms and "B" in have:
        vs = {v: {arm: XO.vs_b(rows, arm) for arm in arms} for v, rows in (("a6", a6), ("tt", tt))}
        res["vsB"] = vs
        res["stop_rule"] = XO.stop_rule(vs["a6"], vs["tt"])
    if set(have) == set(A.ARMS):
        res["h41_tt"] = A.analyze_rows(tt)
    res["term0"] = {v: term0_lat(rows) for v, rows in (("a6", a6), ("tt", tt))}
    res["term0_all"] = {v: term0_lat(rows, "all") for v, rows in (("a6", a6), ("tt", tt))}
    res["TT4"] = {"tt": slope_tt4(tt), "a6": slope_tt4(a6)}
    res["TT4_within_life"] = {v: within_life(v) for v in ("a6", "tt")}
    res["KO1"] = {"a6": L.ko1(a6, "B"), "tt": L.ko1(tt, "B") if tt else None}
    res["sweeps"] = {}
    for name in L.TT_SWEEPS:
        f = L.cfg_file(name)
        if not f.exists():
            continue
        rows = A.load(f)
        pairs = sorted({(r["a"], r["b"]) for r in rows if r["g"] == "lat"} & {(r["a"], r["b"]) for r in rows if r["g"] == "B"})
        if not pairs:
            continue
        sub = [r for r in tt if (r["a"], r["b"]) in set(pairs)]
        out = {"cfg": {k: v for k, v in L.CFGS[name].items() if L.TT.get(k) != v}, "n": len(pairs)}
        for lab, rr in (("sweep", rows), ("tt_same_pairs", sub)):
            v = XO.vs_b(rr, "lat") if any(r["g"] == "lat" for r in rr) else None
            out[lab] = {"lat_vs_B": {k: {"d": x["d"], "class": x["class"]} for k, x in v.items()} if v else None,
                        "B": A.arm_means(rr, "B", KEYS), "lat": A.arm_means(rr, "lat", KEYS), "term0": term0_lat(rr),
                        "TT4": slope_tt4(rr)}
        res["sweeps"][name] = out
    reach = {}
    for name in ("tt_reach0", "tt_reach3"):
        f = L.cfg_file(name)
        if f.exists():
            rows = A.load(f)
            reach[name] = {"B": A.arm_means(rows, "B", ("formed0", "together", "pleasure")), "term0": term0_lat(rows)}
    res["reach"] = reach
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    show(res)
    return res


def show(res):
    print("arms:", res["arms_present"], "n_tt", res["n_tt"])
    for arm in res["arms_present"]:
        a, t = res["arms"]["a6"][arm], res["arms"]["tt"][arm]
        print(f"{arm:<7}" + "  ".join(f"{k} {a[k]:.4f}->{t[k]:.4f}" for k in ("together", "formed0", "liberty", "pleasure", "snon")
                                       if a.get(k) is not None and t.get(k) is not None))
    for arm, d in res["paired_tt_minus_a6"].items():
        print(f"TT-A6 {arm:<7}", {k: (round(v["d"], 4), [round(x, 4) for x in v["ci"]], v["class"]) for k, v in d.items() if v})
    if "vsB" in res:
        for arm in res["vsB"]["tt"]:
            print(f"vsB {arm:<7}", {k: (res["vsB"]["a6"][arm][k]["class"], round(v["d"], 4), v["class"])
                                     for k, v in res["vsB"]["tt"][arm].items()})
    if "h41_tt" in res:
        for aid, v in res["h41_tt"]["aids"].items():
            print(f"== {aid}: {v['verdict']}")
        print("H41 tt:", res["h41_tt"]["H41"])
    print("term0:", res["term0"], res["term0_all"])
    print("TT4:", json.dumps(res["TT4"]), json.dumps(res["TT4_within_life"]))
    print("KO1:", json.dumps(res["KO1"], default=str))
    for k, v in res["sweeps"].items():
        print("sweep", k, v["cfg"], json.dumps({lab: {"lat_vs_B": v[lab]["lat_vs_B"], "term0": v[lab]["term0"],
                                                      "TT4": (v[lab]["TT4"] or {}).get("slope")} for lab in ("sweep", "tt_same_pairs")},
                                                default=str))
    print("reach:", json.dumps(res["reach"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze:
        analyze()
