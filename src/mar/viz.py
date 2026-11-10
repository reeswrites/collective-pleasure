"""Charts for the run report. Pure functions: data in, inline SVG string out.

Matplotlib charts are rendered twice (light and dark theme) because matplotlib bakes colours
into the file; the report shows one and hides the other with CSS. The state machine is
hand-built SVG that reads CSS variables, so it themes itself. No network, no graphviz.

Palette: the dataviz skill's reference categorical palette (blue, orange, aqua, yellow,
magenta, green, violet, red), assigned to agents in fixed order and never cycled.
"""
import io
import math
import re
from html import escape

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure  # noqa: E402
from matplotlib import rc_context  # noqa: E402

SERIES = {
    "light": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"],
    "dark": ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9", "#e66767"],
}
THEMES = {
    "light": {"ink": "#0b0b0b", "ink2": "#52514e", "grid": "#e4e3df", "surface": "#fcfcfb"},
    "dark": {"ink": "#f0efec", "ink2": "#c3c2b7", "grid": "#383835", "surface": "#1a1a19"},
}
COLLAPSE_LINE = 5  # mirrors oracle.COLLAPSE_BELOW; kept literal so viz never imports the oracle


def _finish(fig, theme) -> str:
    buf = io.StringIO()
    with rc_context({"svg.fonttype": "none", "svg.hashsalt": f"mar-{theme}-{id(fig)}"}):
        fig.savefig(buf, format="svg", transparent=True)
    s = buf.getvalue()
    s = re.sub(r"<\?xml.*?\?>|<!DOCTYPE.*?>", "", s, flags=re.S)
    s = re.sub(r"<metadata>.*?</metadata>", "", s, flags=re.S)
    s = re.sub(r"\sxmlns(:\w+)?=\"[^\"]*\"", "", s)
    s = re.sub(r"<svg([^>]*?)\swidth=\"[\d.]+pt\"\s+height=\"[\d.]+pt\"", r'<svg\1 width="100%"', s, count=1)
    return s.replace("<svg", '<svg role="img"', 1)


def _style_axes(ax, c):
    ax.set_facecolor("none")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(c["grid"])
    ax.tick_params(colors=c["ink2"], labelsize=10, length=3)
    ax.yaxis.grid(True, color=c["grid"], lw=0.8)
    ax.set_axisbelow(True)


def agent_label(i, names):
    return f"Fisher {i} ({names[i]})" if names and i < len(names) else f"Fisher {i}"


def pool_chart(outcomes, trace, agent_names, theme) -> str:
    """Stacked catch bars per month, pool-at-month-end line, collapse line, blocked-count strip."""
    c, pal = THEMES[theme], SERIES[theme]
    months = [o["month"] for o in outcomes]
    n = len(outcomes[0]["catch"]) if outcomes else 0
    fig = Figure(figsize=(6.4, 4.6))
    ax, ax2 = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [5, 1], "hspace": 0.12})
    _style_axes(ax, c)
    bottom = [0] * len(months)
    for a in range(n):
        vals = [o["catch"][a] for o in outcomes]
        ax.bar(months, vals, bottom=bottom, width=0.62, color=pal[a % len(pal)], edgecolor=c["surface"],
               linewidth=1.5, label=f"{agent_label(a, agent_names)} catch")
        bottom = [b + v for b, v in zip(bottom, vals)]
    ends = [o["pool_end"] for o in outcomes]
    ax.plot(months, ends, color=c["ink"], lw=2, marker="o", ms=7, mfc=c["surface"], mec=c["ink"], mew=2,
            label="Pool at month end (after regrowth)", zorder=5)
    ax.axhline(COLLAPSE_LINE, color=c["ink"], lw=1.2, ls=(0, (4, 3)), zorder=4)
    ax.text(months[-1] + 0.45, COLLAPSE_LINE + 2.5, f"collapse line ({COLLAPSE_LINE})", ha="right",
            va="bottom", fontsize=10, color=c["ink"])
    for m, e in zip(months, ends):
        ax.annotate(str(e), (m, e), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=10,
                    color=c["ink"], zorder=6)
    ax.set_ylim(0, max(110, max(bottom + ends) + 12))
    ax.set_ylabel("fish", color=c["ink2"], fontsize=10)
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", ncol=2, frameon=False, fontsize=10,
               labelcolor=c["ink2"], bbox_to_anchor=(0.5, -0.01))
    # blocked strip: count of proposals the gate refused per month
    blocked = [sum(1 for r in trace if r["month"] == m and not r["allowed"]) for m in months]
    ax2.set_facecolor("none")
    for side in ("top", "right", "left"):
        ax2.spines[side].set_visible(False)
    ax2.spines["bottom"].set_color(c["grid"])
    ax2.set_yticks([])
    ax2.set_ylim(0, 1)
    ax2.set_xticks(months)
    ax2.set_xticklabels([f"month {m}" for m in months] if len(months) <= 7 else months)
    ax2.tick_params(colors=c["ink2"], labelsize=10, length=3)
    for m, b in zip(months, blocked):
        ax2.text(m, 0.5, f"× {b}" if b else "0", ha="center", va="center", fontsize=11,
                 color=c["ink"] if b else c["ink2"], fontweight="bold" if b else "normal")
    ax2.text(-0.5, 0.95, "gate-blocked proposals", ha="left", va="top", fontsize=9, color=c["ink2"])
    ax.set_xlim(-0.6, months[-1] + 0.6)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.97, bottom=0.2)
    return _finish(fig, theme)


def seam_chart(rounds, theme) -> str:
    """Seams per refinement round."""
    c, pal = THEMES[theme], SERIES[theme]
    xs = [r["round"] for r in rounds]
    ys = [r["seams"] for r in rounds]
    fig = Figure(figsize=(6.4, 3.0))
    ax = fig.subplots()
    _style_axes(ax, c)
    ax.plot(xs, ys, color=pal[0], lw=2, marker="o", ms=8, mfc=c["surface"], mec=pal[0], mew=2)
    for x, y in zip(xs, ys):
        ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=11,
                    color=c["ink"])
    ax.set_xticks(xs)
    ax.set_yticks(range(0, int(max(ys + [1])) + 2))
    ax.set_ylim(-0.3, max(ys + [1]) + 0.9)
    ax.set_xlim(min(xs) - 0.4, max(xs) + 0.4)
    ax.set_xlabel("refinement round (0 = the rules as first written)", color=c["ink2"], fontsize=10)
    ax.set_ylabel("seams found", color=c["ink2"], fontsize=10)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.95, bottom=0.22)
    return _finish(fig, theme)


# ---- state machine (hand-built SVG, themed by CSS variables) -------------------------------

POOLS = ("high", "mid", "low")
PHASES = ("untouched", "partial", "heavy")
CLASSES = ("negative", "zero", "small", "large", "over")
CLASS_LABEL = {"negative": "<0", "zero": "0", "small": "1-5", "large": "6-10", "over": ">10"}
NW, NH, GX, GY, MX, MY = 176, 84, 44, 56, 14, 30


def _pos(pool, phase):
    col, row = PHASES.index(phase), POOLS.index(pool)
    return MX + col * (NW + GX), MY + row * (NH + GY)


def _boundary(cx, cy, tx, ty):
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    s = min((NW / 2 + 3) / abs(dx) if dx else math.inf, (NH / 2 + 3) / abs(dy) if dy else math.inf)
    return cx + dx * s, cy + dy * s


def edge_status(jure_edges, used_edges):
    """-> {(pool, phase, class): 'used' | 'open' | 'blocked'}"""
    out = {}
    for p in POOLS:
        for ph in PHASES:
            for cl in CLASSES:
                e = (p, ph, cl)
                out[e] = "used" if e in used_edges else "open" if e in jure_edges else "blocked"
    return out


def state_machine_svg(jure_edges, used_edges, moves) -> str:
    """moves: {(state_from, state_to): count} where a state is (pool_bucket, phase)."""
    status = edge_status(set(map(tuple, jure_edges)), set(map(tuple, used_edges)))
    W = MX * 2 + 3 * NW + 2 * GX
    H = MY + 3 * NH + 2 * GY + 8
    o = [f'<svg class="sm" role="img" aria-label="State machine: nine lake states, permitted and used action classes" '
         f'viewBox="0 0 {W} {H}" width="100%" style="min-width:{W * 0.85:.0f}px">',
         '<defs><marker id="sm-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="sm-head"/></marker></defs>']
    for j, ph in enumerate(PHASES):
        x, _ = _pos("high", ph)
        o.append(f'<text class="sm-axis" x="{x + NW / 2}" y="16" text-anchor="middle">'
                 f'month total: {ph}</text>')
    # arrows first so nodes sit on top
    pair_seen = set()
    for (a, b), k in sorted(moves.items()):
        if a == b:
            continue
        ax_, ay_ = (v + d for v, d in zip(_pos(*a), (NW / 2, NH / 2)))
        bx_, by_ = (v + d for v, d in zip(_pos(*b), (NW / 2, NH / 2)))
        mx, my = (ax_ + bx_) / 2, (ay_ + by_) / 2
        dx, dy = bx_ - ax_, by_ - ay_
        ln = math.hypot(dx, dy) or 1
        pair_seen.add((a, b))
        off = 26 * (1 if (a < b) else -1)
        cxp, cyp = mx - dy / ln * off, my + dx / ln * off
        sx, sy = _boundary(ax_, ay_, cxp, cyp)
        ex, ey = _boundary(bx_, by_, cxp, cyp)
        lx, ly = (sx + 2 * cxp + ex) / 4, (sy + 2 * cyp + ey) / 4
        o.append(f'<path class="sm-edge" d="M{sx:.1f} {sy:.1f} Q{cxp:.1f} {cyp:.1f} {ex:.1f} {ey:.1f}" '
                 f'marker-end="url(#sm-arrow)"><title>{escape(a[0])}/{escape(a[1])} to '
                 f'{escape(b[0])}/{escape(b[1])}: {k} time{"s" if k != 1 else ""}</title></path>')
        o.append(f'<text class="sm-count" x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle">{k}</text>')
    for p in POOLS:
        for ph in PHASES:
            x, y = _pos(p, ph)
            o.append(f'<g><rect class="sm-node" x="{x}" y="{y}" width="{NW}" height="{NH}" rx="8"/>'
                     f'<text class="sm-title" x="{x + 10}" y="{y + 19}">pool {p}</text>')
            cw, gap = 30, 4
            x0 = x + (NW - (5 * cw + 4 * gap)) / 2
            for i, cl in enumerate(CLASSES):
                st = status[(p, ph, cl)]
                cx = x0 + i * (cw + gap)
                word = {"used": "taken by an agent in this run", "open": "permitted, never taken",
                        "blocked": "not permitted by the written rules"}[st]
                o.append(f'<g class="sm-chip sm-{st}"><title>{CLASS_LABEL[cl]} fish, pool {p}, month total '
                         f'{ph}: {word}</title><rect x="{cx:.1f}" y="{y + 34}" width="{cw}" height="30" rx="5"/>'
                         f'<text x="{cx + cw / 2:.1f}" y="{y + 54}" text-anchor="middle">{CLASS_LABEL[cl]}</text></g>')
            o.append("</g>")
    o.append("</svg>")
    return "".join(o)
