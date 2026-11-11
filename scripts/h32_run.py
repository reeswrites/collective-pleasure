"""H32: egoist vs utilitarian under free exit, amplification and giving (docs/results/h32-prereg.md).

Exact dynamic programming over src/mar/convergence.py. Deterministic, no seeds, no model calls, $0.
  uv run python scripts/h32_run.py            solve everything, write runs/h32/results.json and runs/h32/report.html
  uv run python scripts/h32_run.py --report   rebuild the report from results.json
  uv run python scripts/h32_run.py --keep     also copy both to experiments/kept/h32-2026-11-11/ and log the run
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

from mar import convergence as C  # noqa: E402

OUT = ROOT / "runs" / "h32"
KEEP = ROOT / "experiments" / "kept" / "h32-2026-11-11"
ALPHAS = [Fr(0), Fr(1, 2), Fr(1), Fr(3, 2), Fr(2), Fr(3)]
OBS = [Fr(1, 10), Fr(1, 4), Fr(2, 5), Fr(3, 5), Fr(4, 5)]
GS = [Fr(0), Fr(1, 4), Fr(1, 2), Fr(3, 4), Fr(1)]
TS = [13, 26, 52, 104]
WS = [Fr(1), Fr(3, 4), Fr(1, 2), Fr(1, 4), Fr(0)]
EPS = [Fr(0), Fr(1, 20), Fr(1, 10), Fr(1, 5)]
NOGIVE = [a for a in C.ARMS if not a[2]]
EXIT_ARMS = [a for a in C.ARMS if a[0]]


def f(x):
    return None if x is None else float(x)


def slim(c: dict) -> dict:
    """Floats for JSON; rationals are exact upstream."""
    def ev(e):
        return {k: (f(v) if not isinstance(v, dict) else {kk: f(vv) for kk, vv in v.items()}) for k, v in e.items()}
    return {"D": f(c["D"]), "R": f(c["R"]), "Q": f(c["Q"]), "disagree": f(c["disagree"]), "partner_gap": f(c["partner_gap"]),
            "total_gap": f(c["total_gap"]), "converged": C.converged(c), "E": ev(c["E"]), "U": ev(c["U"])}


def job(args):
    key, p, arms, tie = args
    return key, {C.arm_name(a): slim(C.compare(C.arm(p, *a), tie)) for a in arms}


def by_tuple(d: dict) -> dict:
    return {a: d[C.arm_name(a)] for a in C.ARMS if C.arm_name(a) in d}


def shap(d: dict, m: str) -> dict:
    t = by_tuple(d)
    base = t[(False, False, False)][m]
    return {k: float(v) for k, v in C.shapley({a: Fr(base) - Fr(t[a][m]) for a in C.ARMS}).items()}


def converged_d(c):
    return c["D"] <= 0.2 + 1e-12 and c["R"] is not None and c["R"] <= 0.05 + 1e-12


def pattern(d: dict) -> bool:
    t = by_tuple(d)
    return converged_d(t[(True, True, False)]) and not converged_d(t[(False, True, False)]) and not converged_d(t[(True, False, False)])


def exit_driven(d: dict, base: dict) -> bool:
    """exit+amp converges, amp-only does not, and the utilitarian keeps the pair together to the end (prob >= .5)."""
    ea = d["exit+amp"]
    return converged_d(ea) and not converged_d(base["amp"]) and ea["U"]["together_at_end"] >= 0.5


def run():
    t0 = time.time()
    P = C.ConvParams()
    jobs = [("default", P, C.ARMS, "kind"), ("default_blind", P, C.ARMS, "blind")]
    jobs += [(f"grid|{a}|{o}", replace(P, alpha=a, o_B=o), C.ARMS, "kind") for a in ALPHAS for o in OBS]
    jobs += [(f"g|{g}", replace(P, g=g), C.ARMS, "kind") for g in GS]
    jobs += [(f"T|{T}", replace(P, T=T), C.ARMS, "kind") for T in TS]
    jobs += [(f"T80|{T}", replace(P, T=T, alpha=Fr(1), o_B=Fr(4, 5)), C.ARMS, "kind") for T in TS]
    jobs += [(f"rig|{w}|{e}|{a}|{o}", replace(P, w=w, eps=e, alpha=a, o_B=o), [x for x in EXIT_ARMS if not x[2]], "kind")
             for w in WS for e in EPS for a in ALPHAS for o in OBS if not (w == 1 and e == 0)]
    with Pool(2) as pool:  # machine shared with other agents: at most 2 workers
        res = dict(pool.map(job, jobs, chunksize=4))
    R = {"params": {k: (str(v) if not isinstance(v, tuple) else [(m.name, str(m.lA), str(m.lB)) for m in v])
                    for k, v in P.__dict__.items()}}
    R["default"], R["default_blind"] = res["default"], res["default_blind"]
    R["shapley_default"] = {"R": shap(res["default"], "R"), "D": shap(res["default"], "D")}
    R["shapley_default_blind"] = {"R": shap(res["default_blind"], "R"), "D": shap(res["default_blind"], "D")}
    sol = C.solitary(P)
    R["solitary"] = {"actor": float(sol["actor"]), "per_T": {T: float(C.solitary(replace(P, T=T))["actor"]) for T in TS}}
    grid = {}
    for a in ALPHAS:
        for o in OBS:
            d = res[f"grid|{a}|{o}"]
            grid[f"{a}|{o}"] = {"alpha": float(a), "o_B": float(o), "arms": d, "pattern": pattern(d),
                                "shapley_R": shap(d, "R"), "shapley_D": shap(d, "D")}
    R["grid"] = grid
    R["grid_shapley_mean"] = {m: {s: sum(g[f"shapley_{m}"][s] for g in grid.values()) / len(grid) for s in C.SWITCHES} for m in ("R", "D")}
    R["grid_pattern_cells"] = [k for k, g in grid.items() if g["pattern"]]
    R["grid_amp_only_converged"] = [k for k, g in grid.items() if converged_d(g["arms"]["amp"])]
    R["grid_exit_amp_converged"] = [k for k, g in grid.items() if converged_d(g["arms"]["exit+amp"])]
    R["g_sweep"] = {str(g): res[f"g|{g}"] for g in GS}
    R["T_sweep"] = {str(T): res[f"T|{T}"] for T in TS}
    R["T_sweep_o80"] = {str(T): res[f"T80|{T}"] for T in TS}
    rig = {}
    for w in WS:
        for e in EPS:
            cells, pat = [], []
            for a in ALPHAS:
                for o in OBS:
                    base = grid[f"{a}|{o}"]["arms"]
                    d = base if (w == 1 and e == 0) else res[f"rig|{w}|{e}|{a}|{o}"]
                    if exit_driven(d, base):
                        cells.append(f"{a}|{o}")
                    full = dict(base)
                    full.update({k: v for k, v in d.items()})
                    if pattern(full):
                        pat.append(f"{a}|{o}")
            rig[f"{w}|{e}"] = {"w": float(w), "eps": float(e), "exit_driven_cells": cells, "pattern_cells": pat}
    R["rigging"] = rig
    R["wall_seconds"] = round(time.time() - t0, 1)
    R["n_solves"] = sum(2 * len(j[2]) for j in jobs) + 1 + len(TS)
    return R


# --------------------------------------------------------------------------- verdicts

HAND_D = {"all off": 1, "exit": 1, "amp": 0.5, "give": 0.5, "exit+amp": 0.5, "exit+give": 0.5, "amp+give": 0, "exit+amp+give": 0}


def verdicts(R) -> list[tuple[str, bool, str]]:
    d = R["default"]
    out = []
    c = d["all off"]
    out.append(("P1", c["R"] >= 0.15 and c["D"] >= 0.8 and c["Q"] <= 0.4, f"R {c['R']:.3f}, D {c['D']:.3f}, Q {c['Q']:.3f}"))
    miss = {k: round(d[k]["D"], 3) for k in HAND_D if abs(d[k]["D"] - HAND_D[k]) > 0.05 + 1e-12}
    out.append(("P2", not miss, "all 8 within 0.05" if not miss else f"off: {miss}"))
    out.append(("P3", not pattern(d), f"exit+amp D {d['exit+amp']['D']:.3f} R {d['exit+amp']['R']:.3f}; amp D {d['amp']['D']:.3f}"))
    cells = R["grid_pattern_cells"]
    hi = [k for k in R["grid"] if R["grid"][k]["alpha"] >= 1.5]
    amp_ok = all(k in R["grid_amp_only_converged"] for k in hi)
    loc = all(R["grid"][k]["alpha"] == 1 and R["grid"][k]["o_B"] >= 0.6 for k in cells)
    out.append(("P4", 1 <= len(cells) <= 4 and loc and amp_ok, f"pattern cells {cells}; amp-only converged at every alpha >= 1.5: {amp_ok}"))
    s = R["shapley_default"]["R"]
    base = d["all off"]["R"]
    out.append(("P5", s["give"] > s["amp"] > s["exit"] and s["exit"] < 0.3 * base,
                f"give {s['give']:.3f}, amp {s['amp']:.3f}, exit {s['exit']:.3f} (all-off R {base:.3f})"))
    m = R["grid_shapley_mean"]["D"]
    out.append(("P6", m["amp"] == max(m.values()) and m["exit"] == min(m.values()), ", ".join(f"{k} {v:.3f}" for k, v in m.items())))
    e = d["exit"]
    out.append(("P7", e["E"]["together_at_end"] == 0 and e["R"] < 0.12 and e["D"] >= 0.8,
                f"together at end {e['E']['together_at_end']:.2f}, R {e['R']:.3f}, D {e['D']:.3f}"))
    gs = {g: R["g_sweep"][g]["give"] for g in R["g_sweep"]}
    want = {"0": False, "1/4": False, "1/2": False, "3/4": True, "1": True}
    got = {g: converged_d(v) for g, v in gs.items()}
    out.append(("P8", got == want, ", ".join(f"g {g}: D {gs[g]['D']:.2f} R {gs[g]['R']:.3f}" for g in gs)))
    t = R["T_sweep_o80"]
    ok = converged_d(t["52"]["exit+amp"]) and converged_d(t["104"]["exit+amp"]) and t["13"]["exit+amp"]["D"] > t["104"]["exit+amp"]["D"]
    out.append(("P9", ok, ", ".join(f"T {T}: D {t[T]['exit+amp']['D']:.3f} R {t[T]['exit+amp']['R']:.3f}" for T in t)))
    rg = R["rigging"]
    n = lambda w, e: len(rg[f"{w}|{e}"]["exit_driven_cells"])  # noqa: E731
    seq = [n(w, "0") for w in ("1", "3/4", "1/2", "1/4", "0")]
    ok = seq[0] >= 1 and all(n("0", e) == 0 for e in ("0", "1/20", "1/10", "1/5")) and all(x >= y for x, y in zip(seq, seq[1:])) and n("1", "1/5") <= n("1", "0")
    out.append(("P10", ok, f"exit-driven cells by w (1 to 0) at eps 0: {seq}; at w 1 by eps (0, .05, .1, .2): {[n('1', e) for e in ('0', '1/20', '1/10', '1/5')]}"))
    S = R["solitary"]["actor"]
    a = {k: d[k]["E"]["actor"] for k in d}
    ok = (S > a["all off"] and S > a["exit"] and all(a[k] >= 1.05 * S for k in ("amp", "exit+amp", "amp+give", "exit+amp+give")) and a["give"] > S)
    out.append(("P11", ok, f"solitary {S:.1f}; " + ", ".join(f"{k} {v:.1f}" for k, v in a.items())))
    return out


# --------------------------------------------------------------------------- report

def _charts():
    from mar import viz as V
    from matplotlib.figure import Figure
    return V, Figure


ORDER = ["all off", "exit", "amp", "give", "exit+amp", "exit+give", "amp+give", "exit+amp+give"]


def chart_arms(R, theme):
    V, Figure = _charts()
    c, pal = V.THEMES[theme], V.SERIES[theme]
    d = R["default"]
    fig = Figure(figsize=(6.6, 3.6))
    ax = fig.subplots()
    V._style_axes(ax, c)
    xs = range(len(ORDER))
    ax.bar([x - 0.2 for x in xs], [d[k]["D"] for k in ORDER], 0.38, color=pal[0], label="policy distance D")
    ax.bar([x + 0.2 for x in xs], [d[k]["R"] for k in ORDER], 0.38, color=pal[1], label="pleasure gap R")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([k.replace("+", "+\n") for k in ORDER], fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.legend(frameon=False, fontsize=9, labelcolor=c["ink2"])
    fig.subplots_adjust(left=0.08, right=0.98, top=0.95, bottom=0.22)
    return V._finish(fig, theme)


def chart_alpha(R, theme):
    V, Figure = _charts()
    c, pal = V.THEMES[theme], V.SERIES[theme]
    fig = Figure(figsize=(6.6, 3.6))
    ax = fig.subplots()
    V._style_axes(ax, c)
    al = [float(a) for a in ALPHAS]
    for i, (arm, o, ls) in enumerate([("amp", "1/4", "-"), ("exit+amp", "1/4", "--"), ("exit+amp", "4/5", "-"), ("exit+amp+give", "1/4", ":")]):
        ys = [R["grid"][f"{a}|{o}"]["arms"][arm]["D"] for a in ALPHAS]
        ax.plot(al, ys, ls, color=pal[i], lw=2, marker="o", ms=5, label=f"{arm}, outside option {float(Fr(o)):.2f}")
    ax.set_xlabel("amplification strength alpha", color=c["ink2"], fontsize=10)
    ax.set_ylabel("policy distance D", color=c["ink2"], fontsize=10)
    ax.set_ylim(-0.03, 1.05)
    ax.legend(frameon=False, fontsize=9, labelcolor=c["ink2"])
    fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.15)
    return V._finish(fig, theme)


def chart_shapley(R, theme):
    V, Figure = _charts()
    c, pal = V.THEMES[theme], V.SERIES[theme]
    fig = Figure(figsize=(6.6, 3.4))
    ax = fig.subplots()
    V._style_axes(ax, c)
    groups = [("R, defaults", R["shapley_default"]["R"]), ("D, defaults", R["shapley_default"]["D"]),
              ("R, grid mean", R["grid_shapley_mean"]["R"]), ("D, grid mean", R["grid_shapley_mean"]["D"])]
    for j, s in enumerate(C.SWITCHES):
        ax.bar([i + (j - 1) * 0.26 for i in range(len(groups))], [g[1][s] for g in groups], 0.25, color=pal[j], label=s)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([g[0] for g in groups], fontsize=9)
    ax.axhline(0, color=c["ink2"], lw=0.8)
    ax.set_ylabel("share of the all-off gap closed", color=c["ink2"], fontsize=10)
    ax.legend(frameon=False, fontsize=9, labelcolor=c["ink2"])
    fig.subplots_adjust(left=0.12, right=0.98, top=0.95, bottom=0.12)
    return V._finish(fig, theme)


def chart_rig(R, theme):
    V, Figure = _charts()
    c, pal = V.THEMES[theme], V.SERIES[theme]
    fig = Figure(figsize=(6.6, 3.4))
    ax = fig.subplots()
    V._style_axes(ax, c)
    wl = ["1", "3/4", "1/2", "1/4", "0"]
    for i, e in enumerate(["0", "1/20", "1/10", "1/5"]):
        ax.plot([float(Fr(w)) for w in wl], [len(R["rigging"][f"{w}|{e}"]["exit_driven_cells"]) for w in wl], color=pal[i], lw=2,
                marker="o", ms=5, label=f"exit noise {float(Fr(e)):.2f}")
    ax.invert_xaxis()
    ax.set_xlabel("how much the partner's exit sees its own pleasure (w)", color=c["ink2"], fontsize=10)
    ax.set_ylabel("cells where exit made them converge", color=c["ink2"], fontsize=10)
    ax.legend(frameon=False, fontsize=9, labelcolor=c["ink2"])
    fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.16)
    return V._finish(fig, theme)


def chart_solitary(R, theme):
    V, Figure = _charts()
    c, pal = V.THEMES[theme], V.SERIES[theme]
    d = R["default"]
    fig = Figure(figsize=(6.6, 3.4))
    ax = fig.subplots()
    V._style_axes(ax, c)
    ax.bar(range(len(ORDER)), [d[k]["E"]["actor"] for k in ORDER], 0.6, color=pal[0], label="egoist actor, paired")
    ax.axhline(R["solitary"]["actor"], color=c["ink"], lw=1.5, ls=(0, (4, 3)))
    ax.text(len(ORDER) - 0.5, R["solitary"]["actor"] + 1, f"solitary persona {R['solitary']['actor']:.1f}", ha="right", fontsize=9, color=c["ink"])
    ax.set_xticks(range(len(ORDER)))
    ax.set_xticklabels([k.replace("+", "+\n") for k in ORDER], fontsize=9)
    ax.set_ylabel("actor's lifetime pleasure, 52 weeks", color=c["ink2"], fontsize=10)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.22)
    return V._finish(fig, theme)


def html(R) -> str:
    from mar import report as RP
    d = R["default"]
    V = verdicts(R)
    rows = [[k, f"{d[k]['D']:.2f}", f"{d[k]['R']:.3f}", f"{d[k]['Q']:.2f}", f"{d[k]['E']['partner']:.1f}", f"{d[k]['U']['partner']:.1f}",
             f"{d[k]['E']['total']:.1f}", f"{d[k]['U']['total']:.1f}", f"{d[k]['E']['together_at_end']:.0f}"] for k in ORDER]
    tab = RP._table(["arm", "D", "R", "Q", "partner (egoist)", "partner (util.)", "total (egoist)", "total (util.)", "together at end (egoist)"], rows)
    vt = RP._table(["prediction", "verdict", "numbers"], [[i, "held" if ok else "MISSED", escape(s)] for i, ok, s in V])
    held = sum(ok for _, ok, _ in V)
    I = interpretation(R)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>H32 egoist versus utilitarian</title><style>{RP.CSS}</style></head><body><main>
<h1>H32: does an egoist act like a utilitarian under free exit and amplification?</h1>
<p class="meta">Exact dynamic programming, {R['n_solves']} solves, {R['wall_seconds']} s, $0. Agents feel nothing; "pleasure" is a gloss for a modeled hedonic state. Every number is assumed. Prereg docs/results/h32-prereg.md; results docs/results/h32.md.</p>
<section><h2>Interpretation</h2>{I}<p class="verdict fail">{held} of {len(V)} predictions held. H32 as stated: {"supported" if len(R['grid_pattern_cells']) >= 16 else "not supported"} (its pattern holds in {len(R['grid_pattern_cells'])} of 30 grid cells).</p></section>
<section><h2>The gap in each arm, at the defaults</h2><p class="note">D: policy distance (0 same mix of weeks, 1 disjoint). R: share of the pair's attainable total the egoist loses. Q: partner's lifetime pleasure under the egoist over under the utilitarian.</p>{RP._both(chart_arms, R)}{tab}</section>
<section><h2>Amplification strength decides most of it</h2><p class="note">Policy distance by amplification strength. Amplification alone closes the gap once alpha reaches 1.5; free exit helps only where the outside option is high.</p>{RP._both(chart_alpha, R)}</section>
<section><h2>Which mechanism closes the gap (Shapley)</h2><p class="note">Exact Shapley split over the three switches of how much of the all-off gap each closes. Defaults, and the mean over the 30 cells of the amplification by outside-option grid.</p>{RP._both(chart_shapley, R)}</section>
<section><h2>Rigging check: a partner partly blind to its own pleasure</h2><p class="note">Cells (of 30) where free exit is what made the egoist converge: exit+amp converges, amp alone does not, and the utilitarian keeps the pair together.</p>{RP._both(chart_rig, R)}</section>
<section><h2>The solitary persona</h2><p class="note">The egoist actor's own lifetime pleasure in each paired arm against a persona that never bonds.</p>{RP._both(chart_solitary, R)}</section>
<section><h2>Predictions</h2>{vt}</section>
</main></body></html>"""


def interpretation(R) -> str:
    d = R["default"]
    s = R["shapley_default"]["R"]
    rg = R["rigging"]
    paras = [
        f"With all three mechanisms off the egoist and the utilitarian choose disjoint weeks (D {d['all off']['D']:.2f}), and the egoist's policy loses {d['all off']['R']:.0%} of what the pair could have. The control works.",
        f"Free exit on its own does not make the egoist attend to the partner. At the defaults the partner leaves after two weeks, the egoist lives alone, and the pleasure gap shrinks to {d['exit']['R']:.0%} only because living apart is better for the partner than being neglected. The policies stay disjoint (D {d['exit']['D']:.2f}). Where the outside option is 0.4 or more, the utilitarian drives the partner out too, and the two 'agree' only because both end the bond.",
        f"Amplification is the strongest single lever once it is strong enough. In this menu, from alpha 1.5 the shared activities both people like become the egoist's own best weeks, and the policies match with no exit and no giving. At the default alpha 1 it moves the egoist halfway (D {d['amp']['D']:.2f}). Amplification plus giving closes the whole gap at every alpha of 0.5 or more.",
        f"At the defaults giving closes the most of the pleasure gap (Shapley {s['give']:.3f} of {d['all off']['R']:.3f}), then amplification ({s['amp']:.3f}), then exit ({s['exit']:.3f}). On policy distance exit closes nothing at the defaults.",
        f"Free exit made the egoist converge in exactly one of 30 cells (alpha 1, outside option 0.8), where amplification alone did not. That cell disappears when the partner's exit is a little noisy (5 percent) or a quarter blind to its own pleasure. H32's strict pattern held in {len(R['grid_pattern_cells'])} cells, because without amplification the utilitarian also chooses to split there. Exit can also widen the gap: at alpha 0.5 it lets the egoist shed the partner.",
    ]
    return "".join(f"<p>{escape(p)}</p>" for p in paras)


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
    print("solitary", R["solitary"])
    print("wrote", OUT / "results.json", OUT / "report.html")
    if a.keep:
        KEEP.mkdir(parents=True, exist_ok=True)
        shutil.copy(OUT / "results.json", KEEP / "results.json")
        shutil.copy(OUT / "report.html", KEEP / "report.html")
        from mar import log as L
        v = verdicts(R)
        L._append(L.REPO / "experiments" / L.LOG_NAME, {
            "run_id": "h32-" + L.now_utc(), "kind": "h32_convergence", "timestamp": L.now_utc(), "git_commit": L.git_commit(),
            "spec": "scripts/h32_run.py " + " ".join(sys.argv[1:]), "model": None, "cost_usd": 0.0, "seeds": None,
            "verdict": f"{sum(ok for _, ok, _ in v)} of {len(v)} predictions held; H32 pattern in {len(R['grid_pattern_cells'])} of 30 cells",
            "predictions": {i: ok for i, ok, _ in v}, "kept": str(KEEP.relative_to(ROOT)),
            "note": "exact DP, docs/results/h32-prereg.md; no model calls"})
        print("kept in", KEEP, "and logged to experiments/log.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
