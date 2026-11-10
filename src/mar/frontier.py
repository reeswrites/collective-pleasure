"""Pareto frontier over (freedom, cooperation) and its chart (inline-SVG string, viz.py palette and style)."""
from matplotlib.figure import Figure

from .viz import SERIES, THEMES, _finish, _style_axes


def aggregate(points) -> dict:
    """points: [{"variant", "freedom", "cooperation", ...}] across seeds/mixes -> {variant: (mean f, mean c, n)}."""
    acc = {}
    for p in points:
        acc.setdefault(p["variant"], []).append((p["freedom"], p["cooperation"]))
    return {v: (sum(f for f, _ in xs) / len(xs), sum(c for _, c in xs) / len(xs), len(xs)) for v, xs in acc.items()}


def dominates(a, b) -> bool:
    return a[0] >= b[0] and a[1] >= b[1] and (a[0] > b[0] or a[1] > b[1])


def pareto(points) -> list:
    """Names of variants not dominated by another variant's mean point (both scores maximized), sorted by freedom."""
    agg = aggregate(points)
    front = [v for v, a in agg.items() if not any(dominates(b, a) for w, b in agg.items() if w != v)]
    return sorted(front, key=lambda v: agg[v][0])


def frontier_chart(points, theme="light") -> str:
    c, pal = THEMES[theme], SERIES[theme]
    agg = aggregate(points)
    front = pareto(points)
    fig = Figure(figsize=(6.6, 4.6))
    ax = fig.subplots()
    _style_axes(ax, c)
    ax.xaxis.grid(True, color=c["grid"], lw=0.8)
    ax.scatter([p["freedom"] for p in points], [p["cooperation"] for p in points], s=14, color=c["ink2"], alpha=0.25,
               linewidths=0)
    if len(front) > 1:
        ax.plot([agg[v][0] for v in front], [agg[v][1] for v in front], color=pal[0], lw=2, zorder=2)
    taken = []
    for v, (f, co, _) in sorted(agg.items(), key=lambda kv: kv[1][0]):
        on = v in front
        ax.scatter([f], [co], s=90, zorder=3, color=pal[0] if on else c["surface"], edgecolors=pal[0] if on else c["ink2"],
                   linewidths=2)
        dy = 12 if all(abs(co - t) > 0.05 or abs(f - tf) > 0.18 for tf, t in taken) else -18
        taken.append((f, co))
        ax.annotate(v.replace("_", " "), (f, co), textcoords="offset points", xytext=(0, dy), ha="center", fontsize=10,
                    color=c["ink"] if on else c["ink2"])
    ax.set_xlim(-0.02, 1.05)
    ax.set_ylim(-0.02, 1.05)
    ax.set_xlabel("freedom (exit and real options, higher is freer)", color=c["ink2"], fontsize=10)
    ax.set_ylabel("cooperation (needs met, household persists, no harm)", color=c["ink2"], fontsize=10)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.96, bottom=0.12)
    return _finish(fig, theme)
