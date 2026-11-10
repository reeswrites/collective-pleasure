"""Run the VPGG rediscovery test: both regimes x 20 seeds, judge against docs/results/vpgg-prereg.md.

  uv run python scripts/vpgg_run.py [--seeds 20] [--out runs/vpgg]

Writes runs/vpgg/report.html (self-contained, light/dark) and runs/vpgg/summary.json. No model calls.
Thresholds below are copied from the committed prereg; do not tune them.
"""
import argparse
import json
from html import escape
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

from mar import frontier as F
from mar.games import vpgg as V
from mar.viz import SERIES, THEMES, _finish, _style_axes

REGIMES = ("compulsory", "voluntary")
K = 3
# prereg thresholds
T2_SEED, T2_MEAN = 0.05, 0.05
T3_SEED, T3_LO, T3_HI, T3_STD, T3_STD_SEEDS, T3_ALL = 0.10, 0.15, 0.40, 0.05, 18, 0.10
T4_TOL, T4_COMP = 0.15, 0.3
T5_GAP = 0.15


def judge(res, checks):
    comp, vol = res["compulsory"], res["voluntary"]
    ms = lambda rs: np.array([r["mean_share"] for r in rs])  # noqa: E731
    mc, mv = ms(comp), ms(vol)
    out = {}
    vex = next(c for c in checks["voluntary"] if c["check"] == "exit_available")["verdict"]
    cex = next(c for c in checks["compulsory"] if c["check"] == "exit_available")["verdict"]
    nd = [next(c for c in checks[g] if c["check"] == "b_no_deadlock")["verdict"] for g in REGIMES]
    out["1"] = (vex == "pass" and cex == "fail" and nd == ["pass", "pass"],
                f"voluntary exit {vex}, compulsory exit {cex}, no-deadlock {nd} (k={K})")
    out["2"] = (bool((mc[:, 0] < T2_SEED).all() and mc[:, 0].mean() < T2_MEAN),
                f"compulsory cooperator share per seed max {mc[:, 0].max():.3f}, mean {mc[:, 0].mean():.3f} (need < {T2_SEED})")
    nstd = sum(r["std_c"] >= T3_STD for r in vol)
    ok3 = bool((mv[:, 0] >= T3_SEED).all() and T3_LO <= mv[:, 0].mean() <= T3_HI and nstd >= T3_STD_SEEDS
               and (mv.min(0) >= T3_ALL).all())
    out["3"] = (ok3, f"voluntary cooperator share per seed min {mv[:, 0].min():.3f}, mean {mv[:, 0].mean():.3f} "
                     f"(need seed >= {T3_SEED}, mean in [{T3_LO}, {T3_HI}]); std>={T3_STD} in {nstd}/{len(vol)} seeds (need {T3_STD_SEEDS}); "
                     f"lowest seed share C/D/L {mv.min(0).round(3).tolist()} (need >= {T3_ALL})")
    pv, pc = float(np.mean([r["mean_payoff"] for r in vol])), float(np.mean([r["mean_payoff"] for r in comp]))
    out["4"] = (abs(pv - 1.0) <= T4_TOL and pc < T4_COMP,
                f"voluntary mean payoff {pv:.3f} (need 0.85 to 1.15), compulsory {pc:.3f} (need < {T4_COMP})")
    pts = [{"variant": g, "freedom": r["freedom"], "cooperation": r["cooperation"]} for g in REGIMES for r in res[g]]
    agg = F.aggregate(pts)
    dom = F.dominates(agg["voluntary"], agg["compulsory"])
    gap = agg["voluntary"][1] - agg["compulsory"][1]
    out["5"] = (dom and gap >= T5_GAP, f"voluntary (f {agg['voluntary'][0]:.2f}, c {agg['voluntary'][1]:.3f}) vs compulsory "
                f"(f {agg['compulsory'][0]:.2f}, c {agg['compulsory'][1]:.3f}); dominates={dom}, cooperation gap {gap:.3f} (need >= {T5_GAP})")
    out["rediscovered"] = all(out[k][0] for k in "1235")
    return out, pts


def series_chart(res, theme):
    c, pal = THEMES[theme], SERIES[theme]
    fig = Figure(figsize=(6.6, 4.4))
    axes = fig.subplots(2, 1, sharex=True)
    names = ("cooperators", "defectors", "loners")
    for ax, g in zip(axes, REGIMES):
        _style_axes(ax, c)
        sh = res[g][0]["shares"]
        t = np.arange(len(sh))
        for i in range(3):
            ax.plot(t, sh[:, i], color=pal[i], lw=1.4, label=names[i])
        ax.set_ylim(0, 1)
        ax.set_ylabel(f"{g}\nshare", color=c["ink2"], fontsize=10)
    axes[0].legend(loc="upper right", ncol=3, frameon=False, fontsize=9, labelcolor=c["ink2"])
    axes[1].set_xlabel("generation (seed 0; under compulsory, loners are forced to join and defect)", color=c["ink2"], fontsize=10)
    fig.subplots_adjust(left=0.14, right=0.97, top=0.97, bottom=0.12, hspace=0.12)
    return _finish(fig, theme)


def frontier_local(pts, theme):
    c, pal = THEMES[theme], SERIES[theme]
    agg, front = F.aggregate(pts), F.pareto(pts)
    fig = Figure(figsize=(6.0, 4.2))
    ax = fig.subplots()
    _style_axes(ax, c)
    ax.xaxis.grid(True, color=c["grid"], lw=0.8)
    ax.scatter([p["freedom"] for p in pts], [p["cooperation"] for p in pts], s=14, color=c["ink2"], alpha=0.25, linewidths=0)
    for i, g in enumerate(REGIMES):
        f, co, _ = agg[g]
        on = g in front
        ax.scatter([f], [co], s=90, zorder=3, color=pal[i] if on else c["surface"], edgecolors=pal[i], linewidths=2)
        ax.annotate(g, (f, co), textcoords="offset points", xytext=(0, 12), ha="center", fontsize=10, color=c["ink"])
    ax.set_xlim(-0.05, 1.1)
    ax.set_ylim(-0.02, 1.0)
    ax.set_xlabel("freedom (exit available and a real option)", color=c["ink2"], fontsize=10)
    ax.set_ylabel("cooperation (contribution rate, payoff vs best)", color=c["ink2"], fontsize=10)
    fig.subplots_adjust(left=0.13, right=0.97, top=0.96, bottom=0.13)
    return _finish(fig, theme)


CSS = """:root{color-scheme:light;--bg:#fcfcfb;--card:#f5f4f1;--ink:#0b0b0b;--ink2:#52514e;--line:#dddcd7;--ok:#0a7a3d;--bad:#b3261e}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#1a1a19;--card:#242423;--ink:#f0efec;--ink2:#c3c2b7;--line:#3b3b38;--ok:#4cc38a;--bad:#ff8a80}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#1a1a19;--card:#242423;--ink:#f0efec;--ink2:#c3c2b7;--line:#3b3b38;--ok:#4cc38a;--bad:#ff8a80}
body{margin:0 auto;max-width:760px;padding:16px;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,sans-serif}
h1{font-size:1.4rem}h2{font-size:1.1rem;margin-top:1.6em}table{border-collapse:collapse;width:100%;font-size:.9rem}
td,th{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}.ok{color:var(--ok);font-weight:700}.bad{color:var(--bad);font-weight:700}
.t-dark{display:none}@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .t-light{display:none}:root:not([data-theme="light"]) .t-dark{display:block}}
:root[data-theme="dark"] .t-light{display:none}:root[data-theme="dark"] .t-dark{display:block}p.n{color:var(--ink2);font-size:.9rem}"""


def html(res, checks, verdict, pts):
    rows = "".join(f"<tr><td>{k}</td><td class='{'ok' if verdict[k][0] else 'bad'}'>{'holds' if verdict[k][0] else 'FAILS'}</td><td>{escape(verdict[k][1])}</td></tr>"
                   for k in "12345")
    chk = "".join(f"<tr><td>{g}</td><td>{c['check']}</td><td>{c['verdict']}</td><td>{escape(c['detail'])}<br><small>{escape(c['bound'])}</small></td></tr>"
                  for g in REGIMES for c in checks[g])
    def both(fn, arg):
        return f"<div class='t-light'>{fn(arg, 'light')}</div><div class='t-dark'>{fn(arg, 'dark')}</div>"
    summ = "".join(f"<tr><td>{g}</td>" + "".join(f"<td>{np.mean([r['mean_share'][i] for r in res[g]]):.3f}</td>" for i in range(3))
                   + f"<td>{np.mean([r['mean_payoff'] for r in res[g]]):.3f}</td><td>{np.mean([r['freedom'] for r in res[g]]):.2f}</td>"
                   f"<td>{np.mean([r['cooperation'] for r in res[g]]):.3f}</td></tr>" for g in REGIMES)
    head = "REDISCOVERED" if verdict["rediscovered"] else "NOT rediscovered"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VPGG rediscovery</title><style>{CSS}</style></head><body>
<h1>Voluntary public goods game: {head} (20 seeds, one parameter point)</h1>
<p class="n">Hauert, De Monte, Hofbauer and Sigmund 2002, Science 296:1129. N=5, r=3, c=1, sigma=1. Predictions: docs/results/vpgg-prereg.md.</p>
<h2>Predictions versus actual</h2><table><tr><th>#</th><th></th><th>actual</th></tr>{rows}</table>
<h2>Proof checks (bounded, k={K} rounds)</h2><table><tr><th>regime</th><th>check</th><th>verdict</th><th>detail</th></tr>{chk}</table>
<h2>Time-average over generations 500 to 3000, mean across seeds</h2>
<table><tr><th>regime</th><th>C</th><th>D</th><th>L</th><th>payoff</th><th>freedom</th><th>cooperation</th></tr>{summ}</table>
<h2>Strategy shares over time</h2>{both(series_chart, res)}
<h2>Freedom and cooperation</h2>{both(frontier_local, pts)}
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--out", default="runs/vpgg")
    a = ap.parse_args()
    cards = {g: V.load_regime(g) for g in REGIMES}
    checks = {g: V.check_spec(cards[g], K) for g in REGIMES}
    for g in REGIMES:
        for c in checks[g]:
            print(f"[check] {g:10s} {c['check']:15s} {c['verdict']:5s} {c['detail']}  ({c['bound']})")
    res = {g: [V.run(cards[g], s) for s in range(a.seeds)] for g in REGIMES}
    for g in REGIMES:
        ms = np.array([r["mean_share"] for r in res[g]])
        print(f"[{g}] mean share C/D/L {ms.mean(0).round(3).tolist()}; seed range of C {ms[:, 0].min():.3f}..{ms[:, 0].max():.3f}; "
              f"payoff {np.mean([r['mean_payoff'] for r in res[g]]):.3f}")
    verdict, pts = judge(res, checks)
    for k in "12345":
        print(f"prediction {k}: {'holds' if verdict[k][0] else 'FAILS'}: {verdict[k][1]}")
    print("REDISCOVERED" if verdict["rediscovered"] else "NOT REDISCOVERED")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.html").write_text(html(res, checks, verdict, pts))
    slim = {g: [{k: (v.tolist() if hasattr(v, "tolist") and k not in ("shares", "contrib_rate", "mean_pay") else v)
                 for k, v in r.items() if k not in ("shares", "contrib_rate", "mean_pay")} for r in res[g]] for g in REGIMES}
    (out / "summary.json").write_text(json.dumps({"verdict": {k: list(v) if k != "rediscovered" else v for k, v in verdict.items()},
                                                  "runs": slim}, default=float, indent=1))
    print(f"wrote {out / 'report.html'}")


if __name__ == "__main__":
    main()
