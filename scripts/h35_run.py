"""H35: care that grows from shared good times (docs/results/h35-prereg.md).

Exact DP over src/mar/care.py (and src/mar/convergence.py for the corrected robustness item). Deterministic, no seeds,
no model calls, $0. At most 2 workers.
  uv run python scripts/h35_run.py            solve, write runs/h35/results.json and runs/h35/report.html
  uv run python scripts/h35_run.py --report   rebuild the report from results.json
  uv run python scripts/h35_run.py --keep     also copy to experiments/kept/h35-2026-11-11/ and log the run
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

from mar import care as K  # noqa: E402
from mar import convergence as C  # noqa: E402
import h32_run as H  # noqa: E402

OUT = ROOT / "runs" / "h35"
KEEP = ROOT / "experiments" / "kept" / "h35-2026-11-11"
H32 = ROOT / "experiments" / "kept" / "h32-2026-11-11" / "results.json"
ALPHAS = [Fr(0), Fr(1, 2), Fr(1), Fr(3, 2), Fr(2), Fr(3)]
G0 = [Fr(i, 10) for i in range(11)]
LS = [2, 4, 8]
MODES = {"none": (False, ()), "cliff": (True, ()), "full": (True, C.RUNGS), "withdraw": (True, ("withdraw",))}
RIG_MODES = {"cliff": (), "full": C.RUNGS, "withdraw": ("withdraw",)}


def base(alpha, mode="none"):
    ex, lad = MODES[mode]
    return replace(C.ConvParams(), alpha=alpha, exit_on=ex, amp_on=True, give_on=False, ladder=lad)


def slim(cp, c, kind, path=False):
    e = c[kind]
    out = {"g0": float(cp.g0), "g_final": float(e["g_final"]), "conv_week": e["conv_week"], "warm": e["warm"], "spiral": e["spiral"],
           "D": float(e["D"]), "R": None if e["R"] is None else float(e["R"]), "together": float(e["together_at_end"]),
           "own": float(e["own"]), "vicarious": float(e["vicarious"]), "partner": float(e["partner"]),
           "U_pair": float(c["U"]["pair"]), "U_together": float(c["U"]["together_at_end"])}
    if path:
        out["g_path"] = [float(x) for x in e["g_path"]]
    return out


def job(args):
    kind, key, cps, kinds = args
    if kind == "rig":
        mode, w, eps, cells = cps
        res = {}
        for a, o in cells:
            p = replace(C.ConvParams(), alpha=a, o_B=o, w=w, eps=eps, ladder=RIG_MODES[mode])
            res[f"{a}|{o}"] = H.slim(C.compare(C.arm(p, True, True, False)))
        return key, res
    res = {}
    for cp in cps:
        c = K.cell(cp, kinds=kinds)
        res[str(cp.g0)] = {k: slim(cp, c, k, path=(kind == "basin")) for k in kinds}
    return key, res


def run(full: bool = False):
    """full=False (as run, 2026-11-11): basin, exit-off rupture and sensitivity only. The exit-mode rupture (C8) and the
    corrected robustness sweep (S2) were stopped on the coordinator's instruction while the H32 model is being fixed."""
    t0 = time.time()
    jobs = []
    for a in (ALPHAS[2:4] if full else []):
        for L in [0] + LS:
            for m in ("full", "withdraw", "cliff", "none"):
                cps = [K.CareParams(base=base(a, m), g0=g, rupture=(20, L) if L else None) for g in (Fr(1, 5), Fr(3, 5), Fr(1))]
                jobs.append(("exitrup", f"exitrup|{a}|{m}|{L}", cps, ("naive",)))
    for mode in (RIG_MODES if full else []):
        for w in H.WS:
            for e in H.EPS:
                jobs.append(("rig", f"rig|{mode}|{w}|{e}", (mode, w, e, [(a, o) for a in (Fr(0), Fr(1, 2), Fr(1)) for o in H.OBS]), None))
    for a in ALPHAS:
        jobs.append(("basin", f"basin|{a}", [K.CareParams(base=base(a), g0=g) for g in G0], ("naive", "sophisticated")))
    for a in ALPHAS[1:5]:
        for L in LS:
            jobs.append(("rup", f"rup|{a}|{L}", [K.CareParams(base=base(a), g0=g, rupture=(20, L)) for g in G0], ("naive",)))
    for up, down in ((2, 1), (1, 2)):
        for a in ALPHAS:
            jobs.append(("sens", f"sens|{up}|{down}|{a}", [K.CareParams(base=base(a), g0=g, up=up, down=down) for g in G0], ("naive",)))
    with Pool(2) as pool:  # machine shared with other agents: at most 2 workers
        res = dict(pool.imap_unordered(job, jobs))
    R = {"basin": {str(a): res[f"basin|{a}"] for a in ALPHAS},
         "rupture": {f"{a}|{L}": res[f"rup|{a}|{L}"] for a in ALPHAS[1:5] for L in LS},
         "exitrup": {f"{a}|{m}|{L}": res[f"exitrup|{a}|{m}|{L}"] for a in ALPHAS[2:4] for m in MODES for L in [0] + LS} if full else None,
         "sens": {f"{u}|{d}|{a}": res[f"sens|{u}|{d}|{a}"] for u, d in ((2, 1), (1, 2)) for a in ALPHAS}}
    old = json.loads(H32.read_text())
    rob = {}
    for mode in (RIG_MODES if full else []):
        for w in H.WS:
            for e in H.EPS:
                d = res[f"rig|{mode}|{w}|{e}"]
                surv = (1 - float(e)) ** 52
                cells_old, cells_new = [], []
                for k, ea in d.items():
                    amp = old["grid"][k]["arms"]["amp"]
                    conv = H.converged_d(ea) and not H.converged_d(amp)
                    if conv and ea["U"]["together_at_end"] >= 0.5:
                        cells_old.append(k)
                    if conv and ea["U"]["together_at_end"] >= 0.5 * surv:
                        cells_new.append(k)
                rob[f"{mode}|{w}|{e}"] = {"old_criterion": cells_old, "corrected": cells_new}
    R["robustness"] = rob if full else None
    R["wall_seconds"] = round(time.time() - t0, 1)
    return R


def cells(R, a):
    return R["basin"][str(a)]


def threshold(rows, kind="naive"):
    warm = [Fr(g) for g, v in rows.items() if v[kind]["warm"]]
    return float(min(warm)) if warm else None


def verdicts(R):
    out = []
    z = cells(R, Fr(0))
    out.append(("C1", all((not v["naive"]["warm"]) and v["naive"]["g_final"] == 0 for v in z.values()),
                f"warm {sum(v['naive']['warm'] for v in z.values())} of 11; final g {sorted({round(v['naive']['g_final'], 2) for v in z.values()})}"))
    hi = [(a, g, v["naive"]) for a in ALPHAS[3:] for g, v in cells(R, a).items()]
    ok = all(n["warm"] and n["conv_week"] <= 2 for _, _, n in hi) and all(n["spiral"] == "upward" for _, g, n in hi if Fr(g) <= Fr(4, 5))
    bad = [(str(a), g, n["spiral"], n["conv_week"]) for a, g, n in hi if not (n["warm"] and n["conv_week"] <= 2) or (Fr(g) <= Fr(4, 5) and n["spiral"] != "upward")]
    out.append(("C2", ok, "all 33 warm and upward" if ok else f"exceptions {bad[:6]}"))
    one = cells(R, Fr(1))
    th = threshold(one)
    ok = th in (0.1, 0.2) and all((not v["naive"]["warm"]) == (Fr(g) < Fr(th).limit_denominator(10)) for g, v in one.items()) and \
        all(v["naive"]["spiral"] == "upward" and v["naive"]["g_final"] >= 0.9 for g, v in one.items() if Fr(g) >= Fr(th).limit_denominator(10) and Fr(g) <= Fr(4, 5)) if th is not None else False
    out.append(("C3", ok, f"threshold {th}; " + ", ".join(f"{float(Fr(g)):.1f}:{v['naive']['spiral']}/{v['naive']['g_final']:.2f}" for g, v in one.items())))
    half = cells(R, Fr(1, 2))
    ok = all(v["naive"]["warm"] == (Fr(g) >= Fr(3, 10)) for g, v in half.items()) and not any(v["naive"]["spiral"] == "upward" for v in half.values()) and \
        all(v["naive"]["spiral"] == "stuck" and abs(v["naive"]["g_final"] - float(Fr(g))) <= 0.1 + 1e-9 for g, v in half.items() if Fr(g) < Fr(3, 10))
    out.append(("C4", ok, ", ".join(f"{float(Fr(g)):.1f}:{v['naive']['spiral']}/{v['naive']['g_final']:.2f}" for g, v in half.items())))
    sth = {str(a): (threshold(cells(R, a), "sophisticated"), threshold(cells(R, a))) for a in ALPHAS}
    ok = cells(R, Fr(1))["0"]["sophisticated"]["warm"] and all(s is not None and (n is None or s <= n) for s, n in sth.values() if n is not None)
    out.append(("C5", ok, "thresholds (sophisticated, naive) by alpha: " + ", ".join(f"{float(Fr(a)):g}: {v}" for a, v in sth.items())))
    ws = [(a, g, v["naive"]["conv_week"]) for a in ALPHAS[2:] for g, v in cells(R, a).items() if v["naive"]["warm"]]
    out.append(("C6", all(w <= 4 for _, _, w in ws), f"max convergence week {max(w for _, _, w in ws) if ws else None} over {len(ws)} warm cells"))
    tipped = {}
    for a in ALPHAS[1:5]:
        for L in LS:
            tipped[(float(a), L)] = sum(1 for g, v in R["rupture"][f"{a}|{L}"].items() if cells(R, a)[g]["naive"]["warm"] and not v["naive"]["warm"])
    ok = all(tipped[(a, L)] == 0 for a, L in tipped if a >= 1) and all(abs(tipped[(0.5, L)] - n) <= 1 for L, n in zip(LS, (1, 2, 4)))
    out.append(("C7", ok, "tipped by (alpha, L): " + ", ".join(f"{k}: {v}" for k, v in tipped.items())))
    if R.get("exitrup") is None:
        out.append(("C8", None, "NOT RUN: stopped while the H32 model is fixed (coordinator, 2026-11-11)"))
        return out
    kept = {}
    for a in ALPHAS[2:4]:
        for m in MODES:
            for L in LS:
                for g in ("3/5", "1"):
                    kept[(float(a), m, L, g)] = R["exitrup"][f"{a}|{m}|{L}"][g]["naive"]["together"] >= 0.5
    want = {2: {"none", "cliff", "full", "withdraw"}, 4: {"none", "full"}, 8: {"none"}}
    ok = all(kept[(a, m, L, g)] == (m in want[L]) for (a, m, L, g) in kept)
    summ = {L: {m: sum(kept[(a, m, L, g)] for a in (1.0, 1.5) for g in ("3/5", "1")) for m in MODES} for L in LS}
    out.append(("C8", ok, f"pair kept (of 4 cells) by L and mode: {summ}"))
    return out


def chart_basin(R, theme):
    V, Figure = H._charts()
    c, pal = V.THEMES[theme], V.SERIES[theme]
    fig = Figure(figsize=(6.6, 3.6))
    ax = fig.subplots()
    V._style_axes(ax, c)
    col = {"upward": pal[2], "stable": pal[0], "stuck": pal[3], "downward": pal[7]}
    for i, a in enumerate(ALPHAS):
        for g, v in cells(R, a).items():
            ax.scatter(i, float(Fr(g)), s=150, color=col[v["naive"]["spiral"]], marker="s", edgecolors=c["surface"])
    for k, cc in col.items():
        ax.scatter([], [], color=cc, marker="s", label=k)
    ax.set_xticks(range(len(ALPHAS)))
    ax.set_xticklabels([f"{float(a):g}" for a in ALPHAS])
    ax.set_xlabel("amplification strength alpha", color=c["ink2"], fontsize=10)
    ax.set_ylabel("starting care g0", color=c["ink2"], fontsize=10)
    ax.legend(frameon=False, fontsize=9, labelcolor=c["ink2"], loc="center left", bbox_to_anchor=(1, 0.5))
    fig.subplots_adjust(left=0.1, right=0.8, top=0.95, bottom=0.15)
    return V._finish(fig, theme)


def chart_paths(R, theme):
    V, Figure = H._charts()
    c, pal = V.THEMES[theme], V.SERIES[theme]
    fig = Figure(figsize=(6.6, 3.4))
    ax = fig.subplots()
    V._style_axes(ax, c)
    for i, (a, g) in enumerate([(Fr(1), "0"), (Fr(1), "1/5"), (Fr(1, 2), "3/10"), (Fr(0), "1"), (Fr(3, 2), "0")]):
        v = cells(R, a)[g]["naive"]
        ax.plot(range(1, 53), v["g_path"], color=pal[i], lw=2, label=f"alpha {float(a):g}, g0 {float(Fr(g)):g}")
    ax.set_xlabel("week", color=c["ink2"], fontsize=10)
    ax.set_ylabel("care g (naive egoist)", color=c["ink2"], fontsize=10)
    ax.set_ylim(-0.03, 1.05)
    ax.legend(frameon=False, fontsize=8, labelcolor=c["ink2"])
    fig.subplots_adjust(left=0.1, right=0.98, top=0.95, bottom=0.15)
    return V._finish(fig, theme)


def html(R):
    from mar import report as RP
    V = verdicts(R)
    rows = []
    for a in ALPHAS:
        rows.append([f"{float(a):g}"] + [f"{v['naive']['spiral']} {v['naive']['g_final']:.2f}" for v in cells(R, a).values()])
    tab = RP._table(["alpha"] + [f"g0 {float(g):g}" for g in G0], rows)
    rows_s = [[f"{float(a):g}"] + [f"{v['sophisticated']['spiral']} {v['sophisticated']['g_final']:.2f}" for v in cells(R, a).values()] for a in ALPHAS]
    tab_s = RP._table(["alpha"] + [f"g0 {float(g):g}" for g in G0], rows_s)
    rr = []
    for a in (ALPHAS[2:4] if R.get("exitrup") else []):
        for g in ("1/5", "3/5", "1"):
            rr.append([f"alpha {float(a):g}, g0 {float(Fr(g)):g}"] + [f"{'kept' if R['exitrup'][f'{a}|{m}|{L}'][g]['naive']['together'] >= 0.5 else 'ended'} / {R['exitrup'][f'{a}|{m}|{L}'][g]['naive']['spiral']}"
                                                                   for L in [0] + LS for m in MODES])
    tab_r = RP._table(["cell"] + [f"L{L} {m}" for L in [0] + LS for m in MODES], rr)
    rob = R["robustness"] or {}
    rows_rb = [] if not rob else [[m, f"{float(Fr(w)):g}"] + [f"{len(rob[f'{m}|{w}|{e}']['corrected'])} ({len(rob[f'{m}|{w}|{e}']['old_criterion'])})" for e in ("0", "1/20", "1/10", "1/5")]
               for m in RIG_MODES for w in ("1", "3/4", "1/2", "1/4", "0")]
    tab_rb = RP._table(["exit mode", "partner sight w", "eps 0", "eps 0.05", "eps 0.1", "eps 0.2"], rows_rb)
    vt = RP._table(["prediction", "verdict", "numbers"], [[i, "not run" if ok is None else "held" if ok else "MISSED", escape(s)] for i, ok, s in V])
    held = sum(bool(ok) for _, ok, _ in V)
    interp = "".join(f"<p>{escape(p)}</p>" for p in R.get("interpretation", []))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>H35 care spirals</title><style>{RP.CSS}</style></head><body><main>
<h1>H35 (PROVISIONAL): does care grow from shared good times?</h1>
<p class="calib">PROVISIONAL. This runs on the H32 model, which a correctness review (docs/reviews/2026-11-11-correctness.md, findings 1, 2, 9) found flawed in its exit rule, upkeep and partner estimate. The basin and exit-off rupture use no exit, so the exit rule does not enter, but the upkeep assumption does. The exit-mode rupture (C8) and the robustness item (S2) were not run.</p>
<p class="meta">Exact dynamic programming, {R['wall_seconds']} s on 2 workers, $0. Agents feel nothing; "pleasure" and "care" are glosses for a modeled hedonic state. Every number is assumed. Prereg docs/results/h35-prereg.md; results docs/results/h35.md.</p>
<section><h2>Interpretation</h2>{interp}<p class="verdict fail">{held} of {len(V)} predictions held.</p></section>
<section><h2>The basin: where care takes off (naive egoist, exit off)</h2>{RP._both(chart_basin, R)}{tab}</section>
<section><h2>Care over a lifetime</h2>{RP._both(chart_paths, R)}</section>
<section><h2>Sophisticated egoist (foresees its own care)</h2>{tab_s}</section>
<section><h2>Rupture from week 20, with exit modes (outside option 0.25)</h2><p class="note">L0 = no rupture. Pair kept or ended, and spiral class.</p>{tab_r}</section>
<section><h2>Corrected robustness of exit-driven convergence (H32 model)</h2><p class="note">Cells of 15 (alpha up to 1) where exit, the full ladder or withdraw-only made the egoist converge. Corrected criterion, with the old H32/H32b criterion in brackets.</p>{tab_rb}</section>
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
        ip = OUT / "interpretation.json"
        if ip.exists():
            R["interpretation"] = json.loads(ip.read_text())
    else:
        R = run()
        (OUT / "results.json").write_text(json.dumps(R, indent=1))
    (OUT / "report.html").write_text(html(R))
    for i, ok, s in verdicts(R):
        print(f"{i}: {'not run' if ok is None else 'held' if ok else 'MISSED'}  {s}")
    print("wrote", OUT / "results.json", OUT / "report.html")
    if a.keep:
        KEEP.mkdir(parents=True, exist_ok=True)
        (KEEP / "results.json").write_text(json.dumps(R, indent=1))
        shutil.copy(OUT / "report.html", KEEP / "report.html")
        from mar import log as L
        v = verdicts(R)
        L._append(L.REPO / "experiments" / L.LOG_NAME, {
            "run_id": "h35-" + L.now_utc(), "kind": "h35_care_spirals", "timestamp": L.now_utc(), "git_commit": L.git_commit(),
            "spec": "scripts/h35_run.py " + " ".join(sys.argv[1:]), "model": None, "cost_usd": 0.0, "seeds": None,
            "verdict": f"PROVISIONAL: {sum(bool(ok) for _, ok, _ in v)} of {sum(ok is not None for _, ok, _ in v)} run predictions held (C8 and S2 not run)",
            "predictions": {i: ok for i, ok, _ in v}, "status": "PROVISIONAL", "kept": str(KEEP.relative_to(ROOT)),
            "note": "exact DP, docs/results/h35-prereg.md; no model calls"})
        print("kept in", KEEP, "and logged to experiments/log.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
