"""Run the bargaining rediscovery test, judge against docs/results/bargaining-prereg.md (committed first).

  uv run python scripts/bargaining_run.py [--seeds 20] [--out runs/bargaining]

Writes runs/bargaining/report.html (self-contained, light/dark) and summary.json. No model calls.
Thresholds are copied from the committed prereg; do not tune them.
"""
import argparse
import itertools
import json
from html import escape
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

from mar import frontier as F
from mar.games import bargaining as B
from mar.viz import SERIES, THEMES, _finish, _style_axes

GRID = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
DISC = [(0.9, 0.9), (0.9, 0.7), (0.7, 0.9)]
CELLS = [(d, (o1, o2)) for d in DISC for o1 in GRID for o2 in GRID]
NAMES = ("EQ", "FIFTY", "STUBBORN", "CONCEDER", "SPLITDIFF")
K, T = B.K_DEFAULT, B.T_DEFAULT
TOL, BIG, FREEDOM_EXIT, COOP_SLACK = 0.02, 0.04, 5 / 6, 0.01


def judge(checks, eq, pts_eq, pts_all):
    out = {}
    ex = {c["check"]: c["verdict"] for c in checks["exit-allowed"]}
    ne = {c["check"]: c["verdict"] for c in checks["no-exit"]}
    out["1"] = (ex["exit_path"] == "pass" and ne["exit_path"] == "fail" and ex["b_no_deadlock"] == ne["b_no_deadlock"] == "pass",
                f"exit-allowed exit path {ex['exit_path']}, no-exit exit path {ne['exit_path']}, no-deadlock {ex['b_no_deadlock']}/{ne['b_no_deadlock']} (k={K})")
    rows = []
    for (d, o) in CELLS:
        x = eq["exit-allowed"][(d, o)]
        pred, binding = B.outside_option_split(*d, *o)
        x0 = B.rubinstein_share(*d)
        rows.append((d, o, x.x1, pred, binding, x0, x.outcome, x.t))
    err = [abs(r[2] - r[3]) for r in rows if r[2] is not None]
    a = len(err) == len(rows) and max(err) <= TOL
    zero = [r for r in rows if abs(r[3] - r[5]) < 1e-9]
    big = [r for r in rows if abs(r[3] - r[5]) >= BIG]
    b = all(abs(r[2] - r[5]) <= TOL for r in zero if r[2] is not None) and all(r[2] is not None and abs(r[2] - r[5]) >= TOL for r in big)
    c = all(r[6] == "agree" and r[7] == 0 for r in rows)
    out["2"] = (a and b and c, f"(2a) max |x1 - closed form| {max(err):.4f} over {len(err)} cells (need <= {TOL}); (2b) {len(zero)} no-change cells and {len(big)} change>={BIG} cells "
                f"{'consistent' if b else 'NOT consistent'}; (2c) agreement at t=0 in all cells: {c}")
    rows3 = []
    for (d, o) in CELLS:
        x = eq["no-exit"][(d, o)]
        rows3.append((d, o, x.x1, B.rubinstein_share(*d), x.outcome, x.t))
    e3 = max(abs(r[2] - r[3]) for r in rows3 if r[2] is not None)
    spread = max(max(r[2] for r in rows3 if r[0] == d) - min(r[2] for r in rows3 if r[0] == d) for d in DISC)
    ok3 = e3 <= TOL and all(r[4] == "agree" and r[5] == 0 for r in rows3) and spread <= TOL
    out["3"] = (ok3, f"max |x1 - Rubinstein| {e3:.4f} (need <= {TOL}); spread across the 36 option cells per discount pair at most {spread:.4f}; agreement at t=0 everywhere: "
                f"{all(r[4] == 'agree' and r[5] == 0 for r in rows3)}")
    ag = F.aggregate(pts_eq)
    f_e, c_e, _ = ag["exit-allowed"]
    f_n, c_n, _ = ag["no-exit"]
    ok4a = F.dominates(ag["exit-allowed"], ag["no-exit"]) and abs(f_e - FREEDOM_EXIT) <= 0.001 and f_n == 0 and c_e >= c_n - COOP_SLACK
    ag2 = F.aggregate(pts_all)
    f2e, c2e, _ = ag2["exit-allowed"]
    f2n, c2n, _ = ag2["no-exit"]
    ok4b = f2e > f2n and c2e >= c2n - COOP_SLACK
    out["4"] = (ok4a and ok4b, f"(4a) EQ vs EQ: exit-allowed (f {f_e:.3f}, c {c_e:.3f}) vs no-exit (f {f_n:.3f}, c {c_n:.3f}), holds {ok4a}; "
                f"(4b) all pairings: exit-allowed (f {f2e:.3f}, c {c2e:.3f}) vs no-exit (f {f2n:.3f}, c {c2n:.3f}), holds {ok4b}")
    out["rediscovered"] = all(out[k][0] for k in "123")
    return out, rows, rows3


def share_chart(rows, rows3, theme):
    c, pal = THEMES[theme], SERIES[theme]
    fig = Figure(figsize=(6.8, 7.2))
    axes = fig.subplots(3, 1, sharex=True)
    for ax, d in zip(axes, DISC):
        _style_axes(ax, c)
        sel = [r for r in rows if r[0] == d and r[1][0] == 0]
        sel3 = [r for r in rows3 if r[0] == d and r[1][0] == 0]
        xs = [r[1][1] for r in sel]
        ax.plot(xs, [1 - r[3] for r in sel], color=pal[0], lw=2, label="theory: player 2 share")
        ax.plot(xs, [1 - r[2] for r in sel], "o", color=pal[1], ms=6, label="exit-allowed (sim)")
        ax.plot(xs, [1 - r[2] for r in sel3], "s", color=pal[2], ms=5, mfc="none", label="no-exit (sim)")
        ax.plot(xs, [1 - B.split_the_difference(0, o2) for o2 in xs], "--", color=c["ink2"], lw=1.2, label="split-the-difference")
        ax.set_ylim(0, 0.8)
        ax.set_ylabel(f"d={d}\nplayer 2 share", color=c["ink2"], fontsize=9)
    axes[0].legend(loc="upper left", frameon=False, fontsize=8, labelcolor=c["ink2"])
    axes[2].set_xlabel("player 2 outside option o2 (o1 = 0)", color=c["ink2"], fontsize=10)
    fig.subplots_adjust(left=0.14, right=0.97, top=0.98, bottom=0.07, hspace=0.1)
    return _finish(fig, theme)


def frontier_local(pts, theme):
    c, pal = THEMES[theme], SERIES[theme]
    agg, front = F.aggregate(pts), F.pareto(pts)
    fig = Figure(figsize=(6.0, 4.2))
    ax = fig.subplots()
    _style_axes(ax, c)
    ax.xaxis.grid(True, color=c["grid"], lw=0.8)
    uniq = sorted({(round(p["freedom"], 2), round(p["cooperation"], 2)) for p in pts})  # keeps the SVG small
    ax.scatter([u[0] for u in uniq], [u[1] for u in uniq], s=10, color=c["ink2"], alpha=0.3, linewidths=0)
    for i, g in enumerate(B.REGIMES):
        f, co, _ = agg[g]
        ax.scatter([f], [co], s=90, zorder=3, color=pal[i] if g in front else c["surface"], edgecolors=pal[i], linewidths=2)
        ax.annotate(g, (f, co), textcoords="offset points", xytext=(0, 12), ha="center", fontsize=10, color=c["ink"])
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("freedom (reachable exit outcomes, normalized)", color=c["ink2"], fontsize=10)
    ax.set_ylabel("cooperation (agreement, total surplus)", color=c["ink2"], fontsize=10)
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


def html(checks, verdict, rows, rows3, pts_all, pair_tab):
    vr = "".join(f"<tr><td>{k}</td><td class='{'ok' if verdict[k][0] else 'bad'}'>{'holds' if verdict[k][0] else 'FAILS'}</td><td>{escape(verdict[k][1])}</td></tr>" for k in "1234")
    chk = "".join(f"<tr><td>{g}</td><td>{c['check']}</td><td>{c['verdict']}</td><td>{escape(c['detail'])}<br><small>{escape(c['bound'])}</small></td></tr>" for g in B.REGIMES for c in checks[g])
    both = lambda fn, *a: f"<div class='t-light'>{fn(*a, 'light')}</div><div class='t-dark'>{fn(*a, 'dark')}</div>"  # noqa: E731
    pt = "".join(f"<tr><td>{r}</td><td>{f:.3f}</td><td>{c:.3f}</td><td>{fa:.3f}</td><td>{ag:.3f}</td></tr>" for r, (f, c, fa, ag) in pair_tab.items())
    head = "REDISCOVERED" if verdict["rediscovered"] else "NOT rediscovered"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bargaining rediscovery</title><style>{CSS}</style></head><body>
<h1>Bargaining with outside options: {head}</h1>
<p class="n">Rubinstein 1982; Binmore, Shaked and Sutton 1989. Theory-versus-simulation check, not a human experiment. Prereg: docs/results/bargaining-prereg.md. T={T}, 108 cells, 20 seeds.</p>
<h2>Predictions versus actual</h2><table><tr><th>#</th><th></th><th>actual</th></tr>{vr}</table>
<h2>Proof checks (bounded, k={K})</h2><table><tr><th>regime</th><th>check</th><th>verdict</th><th>detail</th></tr>{chk}</table>
<h2>Player 2 share against its outside option</h2><p class="n">Flat while the option does not bind, then equal to o2. The dashed split-the-difference rival rises from the start.</p>{both(share_chart, rows, rows3)}
<h2>Freedom and cooperation, all pairings</h2>{both(frontier_local, pts_all)}
<h2>Mean scores by regime, all pairings</h2><table><tr><th>regime</th><th>freedom</th><th>cooperation</th><th>agreement rate</th><th>fairness</th></tr>{pt}</table>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--out", default="runs/bargaining")
    a = ap.parse_args()
    cards = {g: B.load_regime(g) for g in B.REGIMES}
    gates = {g: B.BGate(cards[g]) for g in B.REGIMES}
    checks = {g: B.check_spec(cards[g], K) for g in B.REGIMES}
    for g in B.REGIMES:
        for c in checks[g]:
            print(f"[check] {g:12s} {c['check']:14s} {c['verdict']:5s} {c['detail']}  ({c['bound']})")
    eq = {g: {cell: B.play(gates[g], B.make_pair("EQ", "EQ", 0), *cell, T) for cell in CELLS} for g in B.REGIMES}
    pts_eq = [{"variant": g, "freedom": r.freedom, "cooperation": r.cooperation} for g in B.REGIMES for r in eq[g].values()]
    pts_all, acc, per_pair = [], {g: [] for g in B.REGIMES}, {}
    for g in B.REGIMES:
        for n1, n2 in itertools.product(NAMES, NAMES):
            for s in range(a.seeds):
                for cell in CELLS:
                    r = B.play(gates[g], B.make_pair(n1, n2, s), *cell, T)
                    pts_all.append({"variant": g, "freedom": r.freedom, "cooperation": r.cooperation})
                    acc[g].append(r)
                    per_pair.setdefault((g, n1, n2), []).append(r.cooperation)
    verdict, rows, rows3 = judge(checks, eq, pts_eq, pts_all)
    for k in "1234":
        print(f"prediction {k}: {'holds' if verdict[k][0] else 'FAILS'}: {verdict[k][1]}")
    print("REDISCOVERED" if verdict["rediscovered"] else "NOT REDISCOVERED")
    pair_tab = {}
    for g in B.REGIMES:
        rs = acc[g]
        fair = [r.fairness for r in rs if r.fairness is not None]
        pair_tab[g] = (float(np.mean([r.freedom for r in rs])), float(np.mean([r.cooperation for r in rs])),
                       float(np.mean([r.outcome == "agree" for r in rs])), float(np.mean(fair)))
        print(f"[{g}] freedom {pair_tab[g][0]:.3f} cooperation {pair_tab[g][1]:.3f} agreement {pair_tab[g][2]:.3f} fairness {pair_tab[g][3]:.3f}; "
              f"outcomes {dict((o, sum(r.outcome == o for r in rs)) for o in ('agree', 'exit', 'deadline'))}")
    print("[pairing cooperation exit-allowed minus no-exit]")
    for n1, n2 in itertools.product(NAMES, NAMES):
        print(f"  {n1:9s} {n2:9s} {np.mean(per_pair[('exit-allowed', n1, n2)]) - np.mean(per_pair[('no-exit', n1, n2)]):+.3f}")
    xs = [(r[2], r[3], r[5], B.split_the_difference(*r[1])) for r in rows if r[2] is not None]
    print(f"[extra] mean |sim - deal-me-out| {np.mean([abs(x[0] - x[1]) for x in xs]):.4f}; mean |sim - Rubinstein ignoring options| "
          f"{np.mean([abs(x[0] - x[2]) for x in xs]):.4f}; mean |sim - split-the-difference| {np.mean([abs(x[0] - x[3]) for x in xs]):.4f}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.html").write_text(html(checks, verdict, rows, rows3, pts_all, pair_tab))
    (out / "summary.json").write_text(json.dumps({"verdict": {k: (list(v) if k != "rediscovered" else v) for k, v in verdict.items()},
                                                  "exit_allowed_eq": [[list(r[0]), list(r[1]), r[2], r[3], r[4]] for r in rows]}, default=float, indent=1))
    print(f"wrote {out / 'report.html'}")


if __name__ == "__main__":
    main()
