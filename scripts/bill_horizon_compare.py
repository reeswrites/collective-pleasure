"""Bill horizon (docs/results/agent-bill-horizon-prereg.md): the formation check's findings under v1 (as first run), v2 (Amendment 1) and
v2b (Amendment 2), with the survival labels fixed in the prereg, plus the descriptive no-bills arms. Reads rows only; runs nothing.

  uv run python scripts/bill_horizon_compare.py      -> runs/agent-bill-horizon/compare.json and the tables for the write-up
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import h38_formation_check as FC  # noqa: E402
import h38_pairing_run as H38  # noqa: E402

OUT = ROOT / "runs" / "agent-bill-horizon"
FORM_MIN, END_MAX = 0.50, 0.67          # prereg: "households form and persist at plausible rates" (descriptive)
FINDINGS = (("H38's gain, old L4 - L0", "old L4 - L0", "pleasure"), ("withdrawal, old W4 - L0", "old W4 - L0", "pleasure"),
            ("C1 pleasure", "C1 G-L4 - G-L0", "pleasure"), ("C1 without the direct terms", "C1 G-L4 - G-L0", "pleasure_wo_direct"),
            ("C1 weeks together", "C1 G-L4 - G-L0", "together_share"), ("C1 net", "C1 G-L4 - G-L0", "net"),
            ("C2 pleasure", "C2 G-W4 - G-L0", "pleasure"), ("C3 pleasure", "C3 G-L0 - L0", "pleasure"),
            ("C3 formation at week 0", "C3 G-L0 - L0", "formed0"), ("G-L1 - G-L0", "G-L1 - G-L0", "pleasure"))


def _split(d):
    rows = H38.load(d / "rows.jsonl")
    new = [r for r in rows if r["arm"] in FC.ARMS]
    old = [{**r, "arm": FC.OLD_ARMS[r["arm"]]} for r in rows if r["arm"] in FC.OLD_ARMS]
    return new, old


def versions():
    out = {"v1": FC.analyze(write=False)}
    for v, d in (("v2", "h38-formation-v2"), ("v2b", "h38-formation-v2b")):
        f = ROOT / "runs" / d
        if (f / "rows.jsonl").exists():
            new, old = _split(f)
            out[v] = FC.analyze(new, write=False, old=old)
    return out


def sig(x):
    """+1 / -1 when the interval excludes 0, else 0."""
    lo, hi = x["ci"]
    return 1 if lo > 0 else -1 if hi < 0 else 0


def label(s1, s2, sb):
    if s1 == s2 == sb:
        return "stable"
    if sb == s1 and s2 != s1:
        return "v1 restored"
    if sb == s2 and s1 != s2:
        return "v2 confirmed"
    return "neither"


def compare(res):
    out = {"verdicts": {v: r.get("verdicts") for v, r in res.items()}, "findings": {}, "tables": {}}
    if "v2b" not in res:
        return out
    for c in ("C1", "C2", "C3"):
        v1, v2, vb = (res[v]["verdicts"][c] for v in ("v1", "v2", "v2b"))
        out["findings"][f"{c} verdict"] = {"v1": v1, "v2": v2, "v2b": vb, "label": label(v1, v2, vb)}
    for name, d, k in FINDINGS:
        xs = {v: res[v]["diffs"][d][k] for v in ("v1", "v2", "v2b")}
        s = {v: sig(x) for v, x in xs.items()}
        out["findings"][name] = {**{v: {"est": round(x["est"], 4), "ci": [round(c, 4) for c in x["ci"]]} for v, x in xs.items()},
                                 "label": label(s["v1"], s["v2"], s["v2b"])}
    for v, r in res.items():
        out["tables"][v] = {a: {k: (round(x, 3) if isinstance(x, float) else x) for k, x in t.items()
                                if k in ("pleasure", "net", "formed0", "together_share", "ended_if_formed", "held_share", "p_raw")}
                            for a, t in r["table"].items()}
    g = res["v2b"]["table"]["G-L0"]
    out["plausible"] = {"G-L0 formed at week 0": round(g["formed0"], 3), "G-L0 ended of formed": round(g["ended_if_formed"], 3),
                        "forms": g["formed0"] >= FORM_MIN, "persists": g["ended_if_formed"] <= END_MAX}
    return out


def nobills():
    """Descriptive: v2 and v2b with bills off (G-L0, G-L4, O-L0, O-L4)."""
    out = {}
    for v, d in (("v2 no bills", "h38-formation-v2-nobills"), ("v2b no bills", "h38-formation-v2b-nobills")):
        f = ROOT / "runs" / d
        if not (f / "rows.jsonl").exists():
            continue
        new, old = _split(f)
        r = FC.analyze(new, write=False, old=old)
        out[v] = {"table": {a: {k: (round(x, 3) if isinstance(x, float) else x) for k, x in t.items()
                                if k in ("pleasure", "net", "formed0", "together_share", "ended_if_formed")} for a, t in r["table"].items()},
                  "diffs": {n: {k: {"est": round(x["est"], 4), "ci": [round(c, 4) for c in x["ci"]]} for k, x in dd.items()}
                            for n, dd in r["diffs"].items() if n in ("C1 G-L4 - G-L0", "C3 G-L0 - L0", "old L4 - L0")}}
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = compare(versions())
    res["no_bills"] = nobills()
    (OUT / "compare.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
