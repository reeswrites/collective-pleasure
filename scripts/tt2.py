"""TT2: gifts between LAT partners and q = 0.3 (docs/results/tt2-prereg.md). Analysis only: reads TT's rows (runs/time-together/rows.jsonl),
A6's (runs/hybrid-a6/rows.jsonl) and TT2's (runs/tt2/*.jsonl, written by hybrid_leaving.py --run tt2...). No model calls. Wording rule:
agents feel nothing.

  uv run python scripts/tt2.py --screen     EXPLORATORY bug checks on runs/tt2/screen.jsonl (gifts, where, week-0 terms); no outcomes
  uv run python scripts/tt2.py --analyze    the confirming tables -> runs/tt2/analysis.json
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
import time_together as TTA  # noqa: E402

OUT = ROOT / "runs" / "tt2"
KEYS = ("together", "formed0", "liberty", "pleasure", "lived", "snon")
SAME = ("together", "formed0", "liberty", "pleasure", "lived", "snon", "lat")
Q = {"tt2_q005": 0.05, "tt2_q01": 0.1, "tt2": 0.3, "tt2_q06": 0.6}


def load(name):
    f = L.cfg_file(name)
    return A.load(f) if f.exists() else []


def gifts(rows):
    out = {}
    for arm in sorted({r["g"] for r in rows}):
        xs = [r for r in rows if r["g"] == arm]
        n = [len(r.get("gifts", [])) for r in xs]
        out[arm] = {"lives": len(xs), "lives_with_gifts": sum(1 for x in n if x), "gifts": int(sum(n)),
                    "money": 3 * int(sum(n))}
    return out


def verdict(v):
    """The prereg's rule on pleasure AND freedom (liberty): a win raises one without lowering the other; one up, one down is a trade-off.
    Pleasure is 'lowered' when its interval lies wholly below 0 (even inside the 0.003 margin); 'raised' at H41's class (+)."""
    lib, pl = v["liberty"], v["pleasure"]
    lib_up, lib_down = lib["class"] == "+", lib["class"] == "-"
    pl_up = pl["class"] == "+"
    pl_down = pl["ci"] is not None and pl["ci"][1] < 0
    if (lib_up and pl_down) or (pl_up and lib_down):
        return "trade-off"
    if (lib_up and not pl_down) or (pl_up and not lib_down):
        return "win"
    if lib_down or pl_down:
        return "harm"
    return "no gain"


def kg4(tt, c2):
    """C2 (q = 0.1 + gifts) against TT: week-0 terms match; every C2 life with no gift has TT's outcomes exactly."""
    tt_by = {(r["g"], r["a"], r["b"]): r for r in tt}
    term_mis, out_mis, nogift, n = [], [], 0, 0
    for r in c2:
        k = (r["g"], r["a"], r["b"])
        if k not in tt_by:
            continue
        n += 1
        t = tt_by[k]
        if (r.get("term0"), r.get("formed0")) != (t.get("term0"), t.get("formed0")):
            term_mis.append(k)
        if not r.get("gifts"):
            nogift += 1
            diff = [m for m in SAME if A.MEASURES[m](r) != A.MEASURES[m](t)]
            if diff:
                out_mis.append((k, diff))
    return {"lives": n, "term0_mismatch": term_mis, "no_gift_lives": nogift, "no_gift_outcome_mismatch": out_mis,
            "KG4": "PASS" if n and not term_mis and not out_mis else "FAIL"}


def screen():
    rows = load("tt2_screen")
    print("EXPLORATORY screening run (pilot sample); bug checks only, no outcomes")
    print("lives:", len(rows), "arms:", sorted({r["g"] for r in rows}))
    print("gifts:", json.dumps(gifts(rows)))
    off = {(r["g"], r["a"], r["b"]): r for r in load("tt2_screen_off")}
    if off:
        mis = [k for k, r in off.items() if any((x["g"], x["a"], x["b"]) == k and (x.get("term0"), x.get("formed0"))
                                                != (r.get("term0"), r.get("formed0")) for x in rows)]
        nog = [(x["g"], x["a"], x["b"]) for x in rows if (x["g"], x["a"], x["b"]) in off and not x.get("gifts")]
        same = [k for k in nog if all(A.MEASURES[m](next(x for x in rows if (x["g"], x["a"], x["b"]) == k)) == A.MEASURES[m](off[k])
                                      for m in SAME)]
        print(f"week-0 term mismatches vs gifts off: {len(mis)} of {len(off)}; no-gift lives identical to gifts off: {len(same)} of {len(nog)}")
    for r in rows:
        if r.get("gifts"):
            print(" ", r["g"], r["a"], r["b"], "term0", r.get("term0"), "gift weeks", r["gifts"][:12], "..." if len(r["gifts"]) > 12 else "")


def lat_attr(version):
    f = ROOT / "runs" / "lat-suffering" / f"{version}.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    return {"vs_B": d.get("vs_B"), "by_arm": d.get("by_arm")}


def gift_modes(version):
    """From the instrumented rows: every gift by the giver's mode that week, and denied-money weeks by mode (LAT arm)."""
    f = ROOT / "runs" / "lat-suffering" / f"{version}.jsonl"
    if not f.exists():
        return None
    modes, denied = {}, {}
    for line in f.open():
        rec = json.loads(line)
        for wk in rec["weeks"]:
            for r in "AB":
                m = wk[r]
                if m.get("gave"):
                    modes[m["mode"]] = modes.get(m["mode"], 0) + m["gave"]
                if rec["arm"] == "lat" and "money" in m["low"]:
                    denied[m["mode"]] = denied.get(m["mode"], 0) + 1
    return {"gifts_by_mode": modes, "lat_arm_money_under_line_weeks_by_mode": denied}


def analyze():
    a6, tt, t2 = A.load(L.cfg_file("a6")), A.load(L.cfg_file("tt")), load("tt2")
    have = [x for x in A.ARMS if any(r["g"] == x for r in t2)]
    res = {"n_tt2": len(t2), "arms_present": have, "gifts": {name: gifts(load(name)) for name in Q}}
    res["arms"] = {v: {arm: A.arm_means(rows, arm, A.KEYS) for arm in have} for v, rows in (("a6", a6), ("tt", tt), ("tt2", t2))}
    res["paired_tt2_minus_tt"] = {arm: {k: L.paired_diff(t2, tt, arm, k) for k in KEYS} for arm in have}
    for d in res["paired_tt2_minus_tt"].values():
        for k, v in d.items():
            if v:
                v["class"] = A.classify(v["d"], v["ci"], XO.CLASS_KEYS.get(k, 0.01))
    arms = [x for x in have if x != "B"]
    if arms and "B" in have:
        vs = {v: {arm: XO.vs_b(rows, arm) for arm in arms} for v, rows in (("a6", a6), ("tt", tt), ("tt2", t2))}
        res["vsB"] = vs
        res["stop_rule_tt_tt2"] = XO.stop_rule(vs["tt"], vs["tt2"])
        res["three"] = L.three_way({"a6": vs["a6"], "tt": vs["tt"], "tt2": vs["tt2"]})
        res["verdict"] = {v: {arm: verdict(vs[v][arm]) for arm in arms} for v in vs}
    if set(have) == set(A.ARMS):
        res["h41_tt2"] = A.analyze_rows(t2)
    res["term0"] = {v: TTA.term0_lat(rows) for v, rows in (("a6", a6), ("tt", tt), ("tt2", t2))}
    res["term0_all"] = {v: TTA.term0_lat(rows, "all") for v, rows in (("a6", a6), ("tt", tt), ("tt2", t2))}
    res["KO1"] = {"tt": L.ko1(tt, "B"), "tt2": L.ko1(t2, "B") if t2 else None}
    c2 = load("tt2_q01")
    res["KG4"] = kg4(tt, c2) if c2 else None
    # gifts alone (C2 - TT) and q alone (TT2 - C2), LAT and all arms against B and paired
    res["decomp"] = {}
    for lab, x, y in (("gifts_alone_c2_minus_tt", c2, tt), ("q_alone_tt2_minus_c2", t2, c2)):
        out = {}
        for arm in ("B", "lat", "all"):
            if any(r["g"] == arm for r in x) and any(r["g"] == arm for r in y):
                out[arm] = {k: L.paired_diff(x, y, arm, k) for k in KEYS}
        res["decomp"][lab] = out
    if c2 and any(r["g"] == "lat" for r in c2):
        res["vsB_c2"] = {arm: XO.vs_b(c2, arm) for arm in ("lat", "all") if any(r["g"] == arm for r in c2)}
    # q sweep (gifts on): LAT against B at each q, B's formation, LAT take-up
    res["q_sweep"] = {}
    for name, q in Q.items():
        rows = load(name)
        if not (any(r["g"] == "lat" for r in rows) and any(r["g"] == "B" for r in rows)):
            continue
        v = XO.vs_b(rows, "lat")
        res["q_sweep"][name] = {"q": q, "lat_vs_B": {k: {"d": x["d"], "ci": x["ci"], "class": x["class"]} for k, x in v.items()},
                                "verdict": verdict(v), "B": A.arm_means(rows, "B", KEYS), "lat": A.arm_means(rows, "lat", KEYS),
                                "term0": TTA.term0_lat(rows), "n": len({(r["a"], r["b"]) for r in rows if r["g"] == "lat"})}
    res["lat_attr"] = {v: lat_attr(v) for v in ("a6", "tt", "tt2", "tt2_q01")}
    res["gift_modes"] = {v: gift_modes(v) for v in ("tt2", "tt2_q01")}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "analysis.json").write_text(json.dumps(res, indent=1, default=str))
    show(res)
    return res


def show(res):
    print("arms:", res["arms_present"], "n", res["n_tt2"])
    print("gifts:", json.dumps(res["gifts"]))
    for arm in res["arms_present"]:
        a, t, n = res["arms"]["a6"][arm], res["arms"]["tt"][arm], res["arms"]["tt2"][arm]
        print(f"{arm:<7}" + "  ".join(f"{k} {a[k]:.4f}->{t[k]:.4f}->{n[k]:.4f}" for k in ("together", "formed0", "liberty", "pleasure", "snon", "lat")
                                       if None not in (a.get(k), t.get(k), n.get(k))))
    for arm, d in res["paired_tt2_minus_tt"].items():
        print(f"TT2-TT {arm:<7}", {k: (round(v["d"], 4), [round(x, 4) for x in v["ci"]], v["class"]) for k, v in d.items() if v})
    if "vsB" in res:
        for arm in res["vsB"]["tt2"]:
            print(f"vsB {arm:<7}", {k: (res["vsB"]["a6"][arm][k]["class"], res["vsB"]["tt"][arm][k]["class"], round(v["d"], 4),
                                        [round(x, 4) for x in (v["ci"] or [0, 0])], v["class"])
                                    for k, v in res["vsB"]["tt2"][arm].items()}, "verdict", {v: res["verdict"][v][arm] for v in res["verdict"]})
    if "h41_tt2" in res:
        for aid, v in res["h41_tt2"]["aids"].items():
            print(f"== {aid}: {v['verdict']}")
        print("H41 tt2:", res["h41_tt2"]["H41"])
    print("term0:", res["term0"], res["term0_all"])
    print("KO1:", json.dumps(res["KO1"], default=str))
    print("KG4:", json.dumps({k: v for k, v in (res["KG4"] or {}).items()}, default=str)[:600])
    print("decomp:", json.dumps({lab: {arm: {k: (round(v["d"], 5), [round(x, 5) for x in v["ci"]]) for k, v in d.items() if v}
                                        for arm, d in x.items()} for lab, x in res["decomp"].items()}))
    for k, v in res["q_sweep"].items():
        print("q", v["q"], v["verdict"], {kk: (round(x["d"], 4), x["class"]) for kk, x in v["lat_vs_B"].items()}, "term0", v["term0"],
              "B formed0", round(v["B"]["formed0"], 3))
    print("lat_attr:", json.dumps({v: (x or {}).get("vs_B") for v, x in res["lat_attr"].items()}, default=str))
    print("gift_modes:", json.dumps(res["gift_modes"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--screen", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.screen:
        screen()
    if a.analyze:
        analyze()
