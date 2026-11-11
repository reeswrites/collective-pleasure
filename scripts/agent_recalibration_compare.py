"""Agent recalibration (docs/results/agent-recalibration-prereg.md): which H39b and formation-check findings survive the recalibrated agents
and bills that hurt. Reads the analyses the two scripts write (old: runs/h39b-makers, runs/h38-formation; new: their -v2 directories;
descriptive: the -v2-nobills directories) and applies the survival rule fixed in H39b Amendment 2 and the formation check's Amendment 1.
Writes runs/agent-recalibration/compare.json and prints the tables. Wording rule: agents feel nothing; "pleasure" is a gloss.

  uv run python scripts/agent_recalibration_compare.py
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT / "runs" / "agent-recalibration"

H39B_ROWS = ["BP-Z pleasure", "H-Z pleasure", "P-Z pleasure", "G-Z pleasure", "A-Z pleasure", "BP-Z p_raw", "BP-G pleasure (motive)",
             "BP-G p_raw (motive)", "G-Z pleasure (exit split)", "Z-M0 pleasure", "Z-M0 pleasure no-ext", "Z-M0 net", "Z-M0 formed0",
             "Z-M0 together", "BP-M0 pleasure", "H-Z bpw", "P-Z bpw", "BP-Z bpw", "BP-Z together", "H-Z e0_share", "P4 evens BP-Z",
             "H-P ext_share", "P-H pleasure ext", "BP-PN-BP started", "BP-PN-BP paid", "BP-PN-BP pleasure", "BP-BP-w0 formed0",
             "BP-w0-Z-w0 pleasure", "BP-net-Z-net pleasure", "BP-Z trap", "BP-Z lost"]
FC_ROWS = [("C1 G-L4 - G-L0", "pleasure"), ("C2 G-W4 - G-L0", "pleasure"), ("C3 G-L0 - L0", "pleasure"), ("C3 G-L0 - L0", "formed0"),
           ("old L4 - L0", "pleasure"), ("old W4 - L0", "pleasure"), ("C1 G-L4 - G-L0", "pleasure_wo_direct"),
           ("C1 G-L4 - G-L0", "together_share"), ("C1 G-L4 - G-L0", "net"), ("C1 G-L4 - G-L0", "p_raw"), ("G-L1 - G-L0", "pleasure")]


def survives(old, new):
    """The rule fixed before the runs: an interval excluding 0 survives if the new one excludes 0 with the same sign, reverses with the
    opposite sign, else does not survive; a null survives if the new interval includes 0."""
    if old is None or new is None or old.get("ci") is None or new.get("ci") is None:
        return "n/a"
    lo, hi = old["ci"]
    nlo, nhi = new["ci"]
    old_null = lo <= 0 <= hi
    new_null = nlo <= 0 <= nhi
    if old_null:
        return "survives (null)" if new_null else "does not survive (now an effect)"
    if new_null:
        return "does not survive"
    return "survives" if np.sign(old["est"]) == np.sign(new["est"]) else "reverses"


def _load(p):
    p = Path(p)
    return json.loads(p.read_text()) if p.exists() else None


def _fmt(x):
    if x is None:
        return "–"
    return f"{x['est']:+.4f} [{x['ci'][0]:+.4f}, {x['ci'][1]:+.4f}]"


def h39b():
    old = _load(ROOT / "runs" / "h39b-makers" / "analysis.json")
    new = _load(ROOT / "runs" / "h39b-makers-v2" / "analysis.json")
    nob = _load(ROOT / "runs" / "h39b-makers-v2-nobills" / "analysis.json")
    if not (old and new):
        return None
    out = {"rows": {}, "arms": {}, "verdicts": {"old": old.get("verdicts"), "new": new.get("verdicts")}}
    for k in H39B_ROWS:
        o, n = old["comps"].get(k), new["comps"].get(k)
        b = nob["comps"].get(k) if nob else None
        out["rows"][k] = {"old": o and {"est": o["est"], "ci": o.get("ci")}, "new": n and {"est": n["est"], "ci": n.get("ci")},
                          "nobills": b and {"est": b["est"], "ci": b.get("ci")}, "verdict": survives(o, n)}
    for a in sorted(set(old["arms"]) | set(new["arms"])):
        out["arms"][a] = {k: {"old": old["arms"].get(a, {}).get(k), "new": new["arms"].get(a, {}).get(k),
                              "nobills": (nob["arms"].get(a, {}).get(k) if nob else None)}
                          for k in ("pleasure", "p_raw", "net", "formed0", "together", "bpw", "trap", "lost_share")}
    return out


def formation():
    old = _load(ROOT / "runs" / "h38-formation" / "analysis.json")
    new = _load(ROOT / "runs" / "h38-formation-v2" / "analysis.json")
    nob = _load(ROOT / "runs" / "h38-formation-v2-nobills" / "analysis.json")
    if not (old and new):
        return None
    out = {"rows": {}, "verdicts": {"old": old["verdicts"], "new": new.get("verdicts")}, "table": {"old": old["table"], "new": new["table"],
                                                                                              "nobills": nob["table"] if nob else None}}
    for name, key in FC_ROWS:
        o = old["diffs"].get(name, {}).get(key)
        n = new["diffs"].get(name, {}).get(key)
        b = nob["diffs"].get(name, {}).get(key) if nob else None
        out["rows"][f"{name} | {key}"] = {"old": o and {"est": o["est"], "ci": o["ci"]}, "new": n and {"est": n["est"], "ci": n["ci"]},
                                          "nobills": b and {"est": b["est"], "ci": b["ci"]}, "verdict": survives(o, n)}
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"h39b": h39b(), "formation": formation()}
    for name, r in res.items():
        if not r:
            print(f"== {name}: missing analysis")
            continue
        print(f"== {name}")
        print("| Comparison | old agents | v2 + bills | v2, no bills (descriptive) | verdict |")
        print("|---|---|---|---|---|")
        for k, v in r["rows"].items():
            print(f"| {k} | {_fmt(v['old'])} | {_fmt(v['new'])} | {_fmt(v['nobills'])} | {v['verdict']} |")
        print(json.dumps(r["verdicts"], indent=1))
    (OUT / "compare.json").write_text(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
