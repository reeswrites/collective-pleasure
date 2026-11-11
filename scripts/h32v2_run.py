"""H32-v2 and H32b-v2: the egoist-utilitarian test rerun on the fixed model (docs/results/h32-v2-prereg.md).

Fixes (docs/reviews/2026-11-11-correctness.md findings 1, 2, 9), all flags in ConvParams, default off:
  o_leave    the partner's leave threshold (the threat), separate from o_B (what it gets living apart)
  companion  a value per member per week together, so a bond is worth something with amp and give off
  est/window the partner judges the mean of its last `window` weeks (window 1 = each week on its own), not an EMA
Exact DP, no seeds, $0, at most 2 workers.
  uv run python scripts/h32v2_run.py --check    the reachability check (run before the prereg's predictions)
  uv run python scripts/h32v2_run.py            the confirmatory run: runs/h32v2/results.json, report.html
  uv run python scripts/h32v2_run.py --report | --keep
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from dataclasses import replace
from fractions import Fraction as Fr
from html import escape
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from mar import convergence as C  # noqa: E402
import h32_run as H  # noqa: E402

OUT = ROOT / "runs" / "h32v2"
KEEP = ROOT / "experiments" / "kept" / "h32-v2-2026-11-11"
ALPHAS = [Fr(0), Fr(1, 4), Fr(1, 2), Fr(3, 4), Fr(1), Fr(5, 4), Fr(3, 2), Fr(2), Fr(3)]
THREATS = [Fr(1, 10), Fr(1, 4), Fr(2, 5), Fr(3, 5), Fr(4, 5)]
V2 = replace(C.ConvParams(), o_B=Fr(1, 4), companion=Fr(1, 10), est="mean", window=1)   # every new value ASSUMED
LADDERS = {"cliff": (), "withdraw": ("withdraw",), "full": C.RUNGS}
ESTS = {"weekly": dict(est="mean", window=1), "mean4": dict(est="mean", window=4), "ema": dict(est="ema")}
EA, A_, E_ = (True, True, False), (False, True, False), (True, False, False)


def job(args):
    key, p, arms = args
    return key, {C.arm_name(a): H.slim(C.compare(C.arm(p, *a))) for a in arms}


def conv_pair(c, eps=0.0, T=52):
    """Converged AND the utilitarian keeps the pair (at least half of what exit noise alone allows). Both objectives
    ending the bond is not convergence (review finding 1)."""
    return H.converged_d(c) and c["U"]["together_at_end"] >= 0.5 * (1 - eps) ** T


def pattern(arms: dict, eps=0.0) -> bool:
    """exit+amp converges with the pair kept; amp-only does not converge; exit-only does not converge with the pair kept."""
    return conv_pair(arms["exit+amp"], eps) and not H.converged_d(arms["amp"]) and not conv_pair(arms["exit"], eps)


def shift(a: dict, b: dict) -> float:
    """TV distance between two egoist occupancies (how much exit moves the egoist)."""
    keys = set(a) | set(b)
    return sum(abs(a.get(k, 0) - b.get(k, 0)) for k in keys) / 2


# --------------------------------------------------------------------------- reachability check

def check():
    """Free check before predictions. Exit-free quantities, plus two probes at threats OUTSIDE the grid:
    toothless (o_leave 0: exit can never bind, so the pattern must fail) and maximal (o_leave 1.0, judged weekly)."""
    jobs = [(f"amp|{a}", replace(V2, alpha=a), [A_]) for a in ALPHAS]
    for a in ALPHAS:
        jobs.append((f"probe0|{a}", replace(V2, alpha=a, o_leave=Fr(0)), [EA, A_, E_]))
        jobs.append((f"probe1|{a}", replace(V2, alpha=a, o_leave=Fr(1)), [EA, A_, E_]))
    with Pool(2) as pool:
        res = dict(pool.map(job, jobs))
    out = {"open_alphas": [str(a) for a in ALPHAS if a > 0 and not H.converged_d(res[f"amp|{a}"]["amp"])]}
    out["probe_toothless"] = {str(a): pattern(res[f"probe0|{a}"]) for a in ALPHAS}
    out["probe_max"] = {str(a): pattern(res[f"probe1|{a}"]) for a in ALPHAS}
    out["probe_max_detail"] = {str(a): {k: (round(v["D"], 3), round(v["R"], 3), v["U"]["together_at_end"], v["E"]["together_at_end"])
                                        for k, v in res[f"probe1|{a}"].items()} for a in ALPHAS}
    out["reachable_alphas"] = [a for a in out["open_alphas"] if out["probe_max"][a]]
    return out


# --------------------------------------------------------------------------- confirmatory run

def run():
    t0 = time.time()
    jobs = []
    for a in ALPHAS:
        for o in THREATS:
            jobs.append((f"grid|cliff|weekly|{a}|{o}", replace(V2, alpha=a, o_leave=o), C.ARMS))
            for lad in ("withdraw", "full"):
                jobs.append((f"grid|{lad}|weekly|{a}|{o}", replace(V2, alpha=a, o_leave=o, ladder=LADDERS[lad]), [x for x in C.ARMS if x[0]]))
            for est in ("mean4", "ema"):
                jobs.append((f"grid|cliff|{est}|{a}|{o}", replace(V2, alpha=a, o_leave=o, **ESTS[est]), [EA, E_]))
    for lad in LADDERS:
        for w in (Fr(1), Fr(1, 2), Fr(0)):
            for eps in (Fr(0), Fr(1, 20)):
                if w == 1 and eps == 0:
                    continue
                for a in ALPHAS[1:6]:
                    for o in THREATS:
                        jobs.append((f"rob|{lad}|{w}|{eps}|{a}|{o}", replace(V2, alpha=a, o_leave=o, ladder=LADDERS[lad], w=w, eps=eps), [EA, E_]))
    with Pool(2) as pool:  # machine shared with other agents: at most 2 workers
        res = dict(pool.imap_unordered(job, jobs, chunksize=2))
    R = {"params": {k: str(v) for k, v in V2.__dict__.items() if k != "menu"}, "grid": {}, "rob": {}}
    for a in ALPHAS:
        for o in THREATS:
            cell = {}
            base = res[f"grid|cliff|weekly|{a}|{o}"]
            for lad in LADDERS:
                arms = dict(base)
                if lad != "cliff":
                    arms.update(res[f"grid|{lad}|weekly|{a}|{o}"])
                cell[lad] = {"arms": arms, "pattern": pattern(arms),
                             "pattern_give": conv_pair(arms["exit+give"]) and not H.converged_d(arms["give"]) and not conv_pair(arms["exit"]),
                             "shift_amp": shift(arms["amp"]["E"]["occupancy"], arms["exit+amp"]["E"]["occupancy"]),
                             "shift_give": shift(arms["give"]["E"]["occupancy"], arms["exit+give"]["E"]["occupancy"])}
            for est in ("mean4", "ema"):
                arms = dict(base)
                arms.update(res[f"grid|cliff|{est}|{a}|{o}"])
                cell[f"cliff_{est}"] = {"arms": {k: arms[k] for k in ("exit+amp", "amp", "exit")}, "pattern": pattern(arms)}
            R["grid"][f"{a}|{o}"] = {"alpha": float(a), "o_leave": float(o), **cell}
    for lad in LADDERS:
        for w in (Fr(1), Fr(1, 2), Fr(0)):
            for eps in (Fr(0), Fr(1, 20)):
                n = []
                for a in ALPHAS[1:6]:
                    for o in THREATS:
                        k = f"{a}|{o}"
                        if w == 1 and eps == 0:
                            arms = R["grid"][k][lad]["arms"]
                        else:
                            arms = dict(R["grid"][k]["cliff"]["arms"])
                            arms.update(res[f"rob|{lad}|{w}|{eps}|{k}"])
                        if pattern(arms, float(eps)):
                            n.append(k)
                R["rob"][f"{lad}|{w}|{eps}"] = n
    R["wall_seconds"] = round(time.time() - t0, 1)
    return R


def cells_with(R, lad="cliff", key="pattern"):
    return [k for k, v in R["grid"].items() if v[lad][key]]


def alphas_with(R, lad="cliff"):
    return sorted({R["grid"][k]["alpha"] for k in cells_with(R, lad)})


# --------------------------------------------------------------------------- verdicts (filled from the prereg)

def verdicts(R, chk):
    out = []
    g = R["grid"]
    off = g["0|1/4"]["cliff"]["arms"]["all off"]
    out.append(("Q1 control", off["R"] >= 0.15 and off["D"] >= 0.8, f"all off R {off['R']:.3f} D {off['D']:.2f}"))
    reach = [float(Fr(a)) for a in chk["reachable_alphas"]]
    got = alphas_with(R)
    need = (len(reach) + 1) // 2 if reach else None
    hit = [a for a in reach if a in got]
    out.append(("Q2 verdict", need is not None and len(hit) >= need,
                f"reachable alphas {reach}; alphas with a pattern cell {got}; needed {need}"))
    pc = cells_with(R)
    want = {(a, o) for a in (0.75, 1.0, 1.25) for o in (0.4, 0.6, 0.8)}
    have = {(g[k]["alpha"], g[k]["o_leave"]) for k in pc}
    out.append(("Q3 cells", len(have ^ want) <= 2, f"pattern cells {sorted(have)}; symmetric difference with prediction {sorted(have ^ want)}"))
    sh = [g[k]["cliff"]["shift_amp"] for k in pc]
    out.append(("Q4 exit moves", bool(sh) and min(sh) >= 0.25, f"egoist shift amp to exit+amp in pattern cells: min {min(sh) if sh else None}"))
    ex = [g[k]["cliff"]["arms"]["exit"] for k in g]
    out.append(("Q5 exit-only", all(not conv_pair(c) for c in ex), f"exit-only converged with pair kept in {sum(conv_pair(c) for c in ex)} of {len(ex)} cells"))
    n = {e: len(cells_with(R, f"cliff_{e}")) if e != "weekly" else len(pc) for e in ("weekly", "mean4", "ema")}
    out.append(("Q6 estimator", n["ema"] <= n["weekly"] and n["mean4"] <= n["weekly"], f"pattern cells by estimator {n}"))
    nl = {lad: len(cells_with(R, lad)) for lad in LADDERS}
    out.append(("V1 ladders", nl["cliff"] >= nl["withdraw"] >= nl["full"], f"pattern cells by exit mode {nl}"))
    out.append(("V2 full ladder", nl["full"] <= 2, f"full ladder pattern cells {nl['full']}"))
    return out


def html(R, chk):
    from mar import report as RP
    V = verdicts(R, chk)
    d = R["grid"]["1|3/5"]
    order = H.ORDER
    rows = [[k] + [f"{d[l]['arms'][k]['D']:.2f} / {d[l]['arms'][k]['R']:.3f}" if k in d[l]["arms"] else "" for l in LADDERS] for k in order]
    tab = RP._table(["arm (alpha 1, threat 0.6)", "cliff D / R", "withdraw-only", "full ladder"], rows)
    grid_rows = [[f"{float(a):g}"] + ["".join(s for s, lad in (("C", "cliff"), ("W", "withdraw"), ("F", "full")) if R["grid"][f"{a}|{o}"][lad]["pattern"]) or "." for o in THREATS] for a in ALPHAS]
    tab2 = RP._table(["alpha"] + [f"threat {float(o):g}" for o in THREATS], grid_rows)
    vt = RP._table(["prediction", "verdict", "numbers"], [[i, "held" if ok else "MISSED", escape(s)] for i, ok, s in V])
    rob = RP._table(["exit mode", "w", "eps", "pattern cells (25, alpha 0.25 to 1.25)"], [[*k.split("|"), str(len(v))] for k, v in R["rob"].items()])
    held = sum(ok for _, ok, _ in V)
    interp = "".join(f"<p>{escape(p)}</p>" for p in R.get("interpretation", []))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>H32 v2 rerun</title><style>{RP.CSS}</style></head><body><main>
<h1>H32-v2 and H32b-v2: egoist against utilitarian on the fixed model</h1>
<p class="meta">Exact DP, {R['wall_seconds']} s on 2 workers, $0. Agents feel nothing; "pleasure" is a gloss for a modeled hedonic state. Every number is assumed. Prereg docs/results/h32-v2-prereg.md; results docs/results/h32-v2.md.</p>
<section><h2>Interpretation</h2>{interp}<p class="verdict fail">{held} of {len(V)} predictions held.</p></section>
<section><h2>Reachability check (run before the predictions)</h2><p class="note">Open alphas (amp alone does not converge): {', '.join(chk['open_alphas'])}. Pattern under the maximal threat probe: {', '.join(a for a, v in chk['probe_max'].items() if v) or 'none'}. Under the toothless probe: {', '.join(a for a, v in chk['probe_toothless'].items() if v) or 'none'}.</p></section>
<section><h2>Where the pattern holds (C cliff, W withdraw-only, F full ladder)</h2>{tab2}</section>
<section><h2>Each arm at alpha 1, threat 0.6</h2>{tab}</section>
<section><h2>Robustness (corrected noise criterion)</h2>{rob}</section>
<section><h2>Predictions</h2>{vt}</section>
</main></body></html>"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    if a.check:
        chk = check()
        (OUT / "check.json").write_text(json.dumps(chk, indent=1))
        print(json.dumps({k: v for k, v in chk.items() if k != "probe_max_detail"}, indent=1))
        return 0
    chk = json.loads((OUT / "check.json").read_text())
    if a.report:
        R = json.loads((OUT / "results.json").read_text())
    else:
        R = run()
        (OUT / "results.json").write_text(json.dumps(R, indent=1))
    ip = OUT / "interpretation.json"
    if ip.exists():
        R["interpretation"] = json.loads(ip.read_text())
    (OUT / "report.html").write_text(html(R, chk))
    for i, ok, s in verdicts(R, chk):
        print(f"{i}: {'held' if ok else 'MISSED'}  {s}")
    if a.keep:
        KEEP.mkdir(parents=True, exist_ok=True)
        (KEEP / "results.json").write_text(json.dumps(R, indent=1))
        (KEEP / "check.json").write_text(json.dumps(chk, indent=1))
        shutil.copy(OUT / "report.html", KEEP / "report.html")
        from mar import log as L
        v = verdicts(R, chk)
        L._append(L.REPO / "experiments" / L.LOG_NAME, {
            "run_id": "h32v2-" + L.now_utc(), "kind": "h32v2_convergence", "timestamp": L.now_utc(), "git_commit": L.git_commit(),
            "spec": "scripts/h32v2_run.py " + " ".join(sys.argv[1:]), "model": None, "cost_usd": 0.0, "seeds": None,
            "verdict": f"{sum(ok for _, ok, _ in v)} of {len(v)} predictions held", "predictions": {i: ok for i, ok, _ in v},
            "kept": str(KEEP.relative_to(ROOT)), "note": "exact DP, docs/results/h32-v2-prereg.md; no model calls"})
        print("kept in", KEEP, "and logged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
