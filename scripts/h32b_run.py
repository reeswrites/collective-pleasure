"""H32b: graded voice ladder in place of cliff exit (docs/results/h32b-prereg.md).

Exact DP over src/mar/convergence.py with ConvParams.ladder. Deterministic, no seeds, no model calls, $0. At most 2 workers.
  uv run python scripts/h32b_run.py            solve, write runs/h32b/results.json and runs/h32b/report.html
  uv run python scripts/h32b_run.py --report   rebuild the report from results.json
  uv run python scripts/h32b_run.py --keep     also copy to experiments/kept/h32b-2026-11-11/ and log the run
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
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from mar import convergence as C  # noqa: E402
import h32_run as H  # noqa: E402

OUT = ROOT / "runs" / "h32b"
KEEP = ROOT / "experiments" / "kept" / "h32b-2026-11-11"
H32 = ROOT / "experiments" / "kept" / "h32-2026-11-11" / "results.json"
SUBSETS = [tuple(r for r in C.RUNGS if r in s) for n in range(4) for s in combinations(C.RUNGS, n)]
RIG_ALPHAS = [Fr(0), Fr(1, 2), Fr(1)]
EA = (True, True, False)


def sname(s):
    return "+".join(s) if s else "cliff"


def run():
    t0 = time.time()
    P = C.ConvParams()
    L = replace(P, ladder=C.RUNGS)
    jobs = [("cliff_default", P, C.ARMS, "kind"), ("ladder_default", L, C.ARMS, "kind")]
    jobs += [(f"lgrid|{a}|{o}", replace(L, alpha=a, o_B=o), C.ARMS, "kind") for a in H.ALPHAS for o in H.OBS]
    jobs += [(f"sub|{sname(s)}|{a}|{o}", replace(P, ladder=s, alpha=a, o_B=o), [EA], "kind")
             for s in SUBSETS if s != C.RUNGS for a in H.ALPHAS for o in H.OBS]
    jobs += [(f"rig|{w}|{e}|{a}|{o}", replace(L, w=w, eps=e, alpha=a, o_B=o), [EA], "kind")
             for w in H.WS for e in H.EPS for a in RIG_ALPHAS for o in H.OBS if not (w == 1 and e == 0)]
    with Pool(2) as pool:  # machine shared with other agents: at most 2 workers
        res = dict(pool.map(H.job, jobs, chunksize=4))
    old = json.loads(H32.read_text())
    R = {"cliff_default": res["cliff_default"], "ladder_default": res["ladder_default"]}
    # B0 regression: ladder off reproduces the committed H32 numbers
    keys = ("D", "R", "Q")
    diffs = [(k, m) for k in C.ARMS for m in keys
             if abs((res["cliff_default"][C.arm_name(k)][m] or 0) - (old["default"][C.arm_name(k)][m] or 0)) > 1e-12]
    diffs += [(g, m) for a in H.ALPHAS for o in H.OBS for g in [f"{a}|{o}"] for m in keys
              if abs((res[f"sub|cliff|{a}|{o}"]["exit+amp"][m] or 0) - (old["grid"][g]["arms"]["exit+amp"][m] or 0)) > 1e-12]
    R["regression_diffs"] = [str(d) for d in diffs]
    grid = {}
    for a in H.ALPHAS:
        for o in H.OBS:
            k = f"{a}|{o}"
            lad = res[f"lgrid|{k}"]
            base = old["grid"][k]["arms"]
            sub = {sname(s): (lad["exit+amp"] if s == C.RUNGS else res[f"sub|{sname(s)}|{k}"]["exit+amp"]) for s in SUBSETS}
            # rung Shapley on D: v(S) = D(cliff) - D(ladder S)
            vals = {}
            for s in SUBSETS:
                vals[tuple(r in s for r in C.RUNGS)] = Fr(sub["cliff"]["D"]).limit_denominator(10**6) - Fr(sub[sname(s)]["D"]).limit_denominator(10**6)
            phi = {C.RUNGS[i]: 0.0 for i in range(3)}
            sh = C.shapley(vals)   # keys come back as SWITCHES names in order; map to rungs
            for i, nm in enumerate(C.SWITCHES):
                phi[C.RUNGS[i]] = float(sh[nm])
            grid[k] = {"alpha": float(a), "o_B": float(o), "ladder_arms": lad, "subsets": sub, "rung_shapley_D": phi,
                       "voice_driven": H.exit_driven(lad, base), "cliff_exit_driven": H.exit_driven(base, base)}
    R["grid"] = grid
    R["voice_cells"] = [k for k, g in grid.items() if g["voice_driven"]]
    R["cliff_cells"] = [k for k, g in grid.items() if g["cliff_exit_driven"]]
    R["rung_shapley_mean"] = {r: sum(g["rung_shapley_D"][r] for g in grid.values()) / len(grid) for r in C.RUNGS}
    rig = {}
    for w in H.WS:
        for e in H.EPS:
            cells = []
            for a in RIG_ALPHAS:
                for o in H.OBS:
                    k = f"{a}|{o}"
                    d = grid[k]["ladder_arms"] if (w == 1 and e == 0) else res[f"rig|{w}|{e}|{k}"]
                    if H.exit_driven(d, old["grid"][k]["arms"]):
                        cells.append(k)
            h32 = [c for c in old["rigging"][f"{w}|{e}"]["exit_driven_cells"] if Fr(c.split("|")[0]) <= 1]
            rig[f"{w}|{e}"] = {"w": float(w), "eps": float(e), "voice_cells": cells, "cliff_cells_h32": h32}
    R["rigging"] = rig
    R["wall_seconds"] = round(time.time() - t0, 1)
    R["n_solves"] = sum(2 * len(j[2]) for j in jobs)
    return R


def verdicts(R):
    out = []
    out.append(("B0", not R["regression_diffs"], "identical" if not R["regression_diffs"] else f"{len(R['regression_diffs'])} diffs"))
    c = R["ladder_default"]["all off"]
    out.append(("B1", abs(c["R"] - 0.2307692) < 1e-6 and c["D"] == 1, f"R {c['R']:.3f} D {c['D']:.2f}"))
    out.append(("B2", len(R["voice_cells"]) <= 1, f"voice-driven cells {R['voice_cells']} (cliff {R['cliff_cells']})"))
    g = R["grid"]["1|3/5"]["subsets"]
    out.append(("B3", g["checkin+renegotiate+withdraw"]["D"] >= g["cliff"]["D"] - 1e-12,
                f"alpha 1, o_B 0.6: ladder D {g['checkin+renegotiate+withdraw']['D']:.3f} R {g['checkin+renegotiate+withdraw']['R']:.3f}; cliff D {g['cliff']['D']:.3f} R {g['cliff']['R']:.3f}"))
    rs = []
    for o in ("1/10", "1/4", "2/5", "3/5"):
        s = R["grid"][f"1/2|{o}"]["subsets"]
        rs.append((o, s["checkin+renegotiate+withdraw"]["R"], s["cliff"]["R"]))
    out.append(("B4", sum(lr >= cr - 1e-12 for _, lr, cr in rs) >= 3, "; ".join(f"o_B {o}: ladder R {lr:.3f}, cliff {cr:.3f}" for o, lr, cr in rs)))
    m = R["rung_shapley_mean"]
    out.append(("B5", m["renegotiate"] == max(m.values()) and m["checkin"] <= 0.02, ", ".join(f"{k} {v:.3f}" for k, v in m.items())))
    rg = R["rigging"]
    n = lambda w, e: len(rg[f"{w}|{e}"]["voice_cells"])  # noqa: E731
    ok = all(n("0", e) == 0 for e in ("0", "1/20", "1/10", "1/5")) and n("3/4", "0") <= n("1", "0") and n("1", "1/20") <= n("1", "0")
    out.append(("B6", ok, f"by w (1..0) at eps 0: {[n(w, '0') for w in ('1', '3/4', '1/2', '1/4', '0')]}; at w 1 by eps: {[n('1', e) for e in ('0', '1/20', '1/10', '1/5')]}"))
    diff = {k: (R["ladder_default"][k]["D"], R["cliff_default"][k]["D"]) for k in R["cliff_default"] if abs(R["ladder_default"][k]["D"] - R["cliff_default"][k]["D"]) > 1e-12}
    out.append(("B7", not diff, "all equal" if not diff else f"differ: {diff}"))
    return out


def chart_subsets(R, theme):
    V, Figure = H._charts()
    c, pal = V.THEMES[theme], V.SERIES[theme]
    fig = Figure(figsize=(6.6, 3.6))
    ax = fig.subplots()
    V._style_axes(ax, c)
    cells = ["1|3/5", "1|4/5", "1/2|1/4", "1/2|3/5"]
    names = [sname(s) for s in SUBSETS]
    for i, k in enumerate(cells):
        ax.plot(range(len(names)), [R["grid"][k]["subsets"][n]["D"] for n in names], color=pal[i], lw=2, marker="o", ms=5,
                label=f"alpha {R['grid'][k]['alpha']:g}, outside option {R['grid'][k]['o_B']:g}")
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels([n.replace("checkin", "chk").replace("renegotiate", "reneg").replace("withdraw", "wd").replace("+", "+\n") for n in names], fontsize=8)
    ax.set_ylabel("policy distance D (exit+amp arm)", color=c["ink2"], fontsize=10)
    ax.set_ylim(-0.03, 1.05)
    ax.legend(frameon=False, fontsize=8, labelcolor=c["ink2"])
    fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.24)
    return V._finish(fig, theme)


def chart_rig(R, theme):
    V, Figure = H._charts()
    c, pal = V.THEMES[theme], V.SERIES[theme]
    fig = Figure(figsize=(6.6, 3.4))
    ax = fig.subplots()
    V._style_axes(ax, c)
    wl = ["1", "3/4", "1/2", "1/4", "0"]
    for i, e in enumerate(["0", "1/20", "1/10", "1/5"]):
        ax.plot([float(Fr(w)) for w in wl], [len(R["rigging"][f"{w}|{e}"]["voice_cells"]) for w in wl], color=pal[i], lw=2, marker="o", ms=5,
                label=f"ladder, exit noise {float(Fr(e)):.2f}")
    ax.plot([float(Fr(w)) for w in wl], [len(R["rigging"][f"{w}|0"]["cliff_cells_h32"]) for w in wl], color=c["ink"], lw=1.5, ls=(0, (4, 3)), label="cliff (H32), noise 0")
    ax.invert_xaxis()
    ax.set_xlabel("how much the partner's estimate sees its own pleasure (w)", color=c["ink2"], fontsize=10)
    ax.set_ylabel("cells where exit or voice made them converge", color=c["ink2"], fontsize=9)
    ax.legend(frameon=False, fontsize=8, labelcolor=c["ink2"])
    fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.16)
    return V._finish(fig, theme)


def interpretation(R):
    g = R["grid"]
    m = R["rung_shapley_mean"]
    s = g["1|3/5"]["subsets"]
    paras = [
        f"The ladder made the egoist converge in {len(R['voice_cells'])} of 30 cells where amplification alone did not (cliff exit: {len(R['cliff_cells'])}).",
        f"At alpha 1 and outside option 0.6, cliff exit left a policy distance of {s['cliff']['D']:.2f}; the full ladder leaves {s['checkin+renegotiate+withdraw']['D']:.2f}.",
        f"Mean rung Shapley on policy distance (positive = closes the gap relative to the cliff): check-in {m['checkin']:.3f}, renegotiate {m['renegotiate']:.3f}, withdraw {m['withdraw']:.3f}.",
    ]
    w1, w8 = g["1|3/5"]["subsets"]["withdraw"], g["1|4/5"]["subsets"]["withdraw"]
    paras += [
        f"Withdrawal alone does the work: with only that rung, D is {w1['D']:.2f} at outside option 0.6 and {w8['D']:.2f} at 0.8, with the pair kept. The egoist feels withdrawal because it takes away the amplified shared weeks it values.",
        "Renegotiation undoes it: a demand that applies only on that rung is met by the egoist's next common-ground week, the partner calms down, and the egoist returns to its own passion. Check-in carries no information here (the actor already sees the partner's estimate) and only adds slack.",
        "The withdraw-only finding came out of the rung decomposition, not a headline prediction, and its robustness to noise and blindness was not tested.",
    ]
    return "".join(f"<p>{escape(p)}</p>" for p in paras)


def html(R):
    from mar import report as RP
    V = verdicts(R)
    order = H.ORDER
    rows = [[k, f"{R['cliff_default'][k]['D']:.2f}", f"{R['ladder_default'][k]['D']:.2f}", f"{R['cliff_default'][k]['R']:.3f}", f"{R['ladder_default'][k]['R']:.3f}",
             f"{R['ladder_default'][k]['Q']:.2f}"] for k in order]
    tab = RP._table(["arm", "D cliff", "D ladder", "R cliff", "R ladder", "Q ladder"], rows)
    cells = [k for k in R["grid"] if R["grid"][k]["alpha"] in (0.5, 1.0)]
    rows2 = [[f"alpha {R['grid'][k]['alpha']:g}, o_B {R['grid'][k]['o_B']:g}"] + [f"{R['grid'][k]['subsets'][sname(s)]['D']:.2f} / {R['grid'][k]['subsets'][sname(s)]['R']:.3f}" for s in SUBSETS] for k in cells]
    tab2 = RP._table(["cell"] + [sname(s) for s in SUBSETS], rows2)
    vt = RP._table(["prediction", "verdict", "numbers"], [[i, "held" if ok else "MISSED", escape(s)] for i, ok, s in V])
    held = sum(ok for _, ok, _ in V)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>H32b voice ladder</title><style>{RP.CSS}</style></head><body><main>
<h1>H32b: does a graded voice ladder make the egoist converge where cliff exit did not?</h1>
<p class="meta">Exact dynamic programming, {R['n_solves']} solves, {R['wall_seconds']} s on 2 workers, $0. Agents feel nothing; "pleasure" is a gloss for a modeled hedonic state. Every number is assumed. Prereg docs/results/h32b-prereg.md; results docs/results/h32b.md.</p>
<section><h2>Interpretation</h2>{interpretation(R)}<p class="verdict fail">{held} of {len(V)} predictions held.</p></section>
<section><h2>Each arm at the defaults: cliff against ladder</h2>{tab}</section>
<section><h2>Which rung does the work</h2><p class="note">Policy distance in the exit+amp arm (giving off) for every subset of rungs. "cliff" is H32's exit.</p>{RP._both(chart_subsets, R)}{tab2}</section>
<section><h2>Robustness: noise and a partly blind partner</h2>{RP._both(chart_rig, R)}</section>
<section><h2>Predictions</h2>{vt}</section>
</main></body></html>"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    if a.report:
        R = json.loads((OUT / "results.json").read_text())
    else:
        R = run()
        (OUT / "results.json").write_text(json.dumps(R, indent=1))
    (OUT / "report.html").write_text(html(R))
    for i, ok, s in verdicts(R):
        print(f"{i}: {'held' if ok else 'MISSED'}  {s}")
    print("wrote", OUT / "results.json", OUT / "report.html")
    if a.keep:
        KEEP.mkdir(parents=True, exist_ok=True)
        shutil.copy(OUT / "results.json", KEEP / "results.json")
        shutil.copy(OUT / "report.html", KEEP / "report.html")
        from mar import log as L
        v = verdicts(R)
        L._append(L.REPO / "experiments" / L.LOG_NAME, {
            "run_id": "h32b-" + L.now_utc(), "kind": "h32b_voice_ladder", "timestamp": L.now_utc(), "git_commit": L.git_commit(),
            "spec": "scripts/h32b_run.py " + " ".join(sys.argv[1:]), "model": None, "cost_usd": 0.0, "seeds": None,
            "verdict": f"{sum(ok for _, ok, _ in v)} of {len(v)} predictions held; voice-driven cells {len(R['voice_cells'])} of 30 (cliff {len(R['cliff_cells'])})",
            "predictions": {i: ok for i, ok, _ in v}, "kept": str(KEEP.relative_to(ROOT)),
            "note": "exact DP, docs/results/h32b-prereg.md; no model calls"})
        print("kept in", KEEP, "and logged to experiments/log.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
