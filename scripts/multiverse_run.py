"""Multiverse sensitivity sweep (docs/results/multiverse-prereg.md). No model calls.

  uv run python scripts/multiverse_run.py horizon     C1, C2 (exact MDP)                 about 3 minutes on 8 cores
  uv run python scripts/multiverse_run.py gap         C3 (friend-contact gap)            about 2 minutes
  uv run python scripts/multiverse_run.py vpggfree    C7 (liberty v2, empowerment)       about 1 minute
  uv run python scripts/multiverse_run.py vpggosc     C8 (VPGG oscillation)              a few minutes
  uv run python scripts/multiverse_run.py negotiation C4                                 longer (household runs)
  uv run python scripts/multiverse_run.py pleasure    C5
  uv run python scripts/multiverse_run.py seedv2      C6
  uv run python scripts/multiverse_run.py summary     prints the table and writes experiments/kept/multiverse-2026-11-10/

Each part writes runs/multiverse/<part>.json (git-ignored). Existing modules are used read-only (see src/mar/multiverse.py).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import multiverse as MV  # noqa: E402

OUT = ROOT / "runs" / "multiverse"
KEPT = ROOT / "experiments" / "kept" / "multiverse-2026-11-10"
WORKERS = 8


def save(part, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{part}.json").write_text(json.dumps(obj, indent=1, default=str))


def load(part):
    p = OUT / f"{part}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _design(params, n, extra=None):
    pts = [("default", None, MV.defaults(params))]
    pts += [(f"oat:{nm}={MV._fmt(v)}", (nm, v), d) for nm, v, d in MV.oat(params, extra)]
    pts += [(f"lhs:{i}", None, d) for i, d in enumerate(MV.lhs(params, n))]
    return pts


def _summ(params, pts, margin_of):
    """pts: list of (key, oat, values, result). margin_of(result) -> float."""
    lhs = [(v, r) for k, o, v, r in pts if k.startswith("lhs:")]
    oatr = [(o[0], o[1], margin_of(r)) for k, o, v, r in pts if o is not None]
    dflt = next(r for k, o, v, r in pts if k == "default")
    return MV.summarize(params, [v for v, _ in lhs], [margin_of(r) for _, r in lhs], oatr, margin_of(dflt))


# ---------------------------------------------------------------------------------------------------------- exact parts

def part_horizon():
    pts = _design(MV.HORIZON_PARAMS, 128)
    res = MV._pool_map(MV.horizon_point, [v for _, _, v in pts], WORKERS)
    rows = [(k, o, v, r) for (k, o, v), r in zip(pts, res)]
    out = {"points": [{"key": k, "values": v, **r} for k, o, v, r in rows]}
    for c in ("c1_margin", "c2_margin", "c2b_margin"):
        out[c] = _summ(MV.HORIZON_PARAMS, rows, lambda r, c=c: r[c])
    lhs = [r for k, o, v, r in rows if k.startswith("lhs:")]
    out["loss1_52_lhs"] = sorted(r["loss1_52"] for r in lhs)
    out["loss95_lhs"] = sorted(r["loss95_26"] for r in lhs)
    out["mstar_counts"] = {str(m): sum(1 for r in lhs if r["mstar"] == m) for m in [None, *MV.CONCERT_MS]}
    save("horizon", out)


def part_gap():
    pts = _design(MV.GAP_PARAMS, 128, MV.GAP_EXTRA)
    res = MV._pool_map(MV.gap_point, [v for _, _, v in pts], WORKERS)
    rows = [(k, o, v, r) for (k, o, v), r in zip(pts, res)]
    out = {"points": [{"key": k, "values": v, **r} for k, o, v, r in rows]}
    for c in ("c3_margin", "c3_7_margin", "c3_ctrl_margin"):
        out[c] = _summ(MV.GAP_PARAMS, rows, lambda r, c=c: r[c])
    lhs = [r for k, o, v, r in rows if k.startswith("lhs:")]
    out["max_best_lhs"] = sorted(r["max_best"] for r in lhs)
    # the per-contact cost alone, finer: everything else at default
    base = MV.defaults(MV.GAP_PARAMS)
    costs = [0.0, 1.8, 3.6, 5.4, 7.2, 10.8, 14.4, 21.6, 24.0, 28.8, 43.2, 57.6]
    cres = MV._pool_map(MV.gap_point, [{**base, "cost_sess": c} for c in costs], WORKERS)
    out["cost_sess_line"] = [{"cost_sess": c, "best": r["best"], "max_best": r["max_best"]} for c, r in zip(costs, cres)]
    save("gap", out)


def part_vpggfree():
    grid = [(r, s, k) for r in MV.VPGG_RS for s in MV.VPGG_SIGMA_SHARES for k in MV.VPGG_KS]
    res = MV._pool_map(MV.vpgg_freedom_point, grid, WORKERS)
    out = {"points": res, "share": sum(r["c7_margin"] > 0 for r in res) / len(res),
           "share_lib": sum(r["lib_holds"] for r in res) / len(res), "share_emp": sum(r["emp_holds"] for r in res) / len(res),
           "default": next(r for r in res if r["r"] == 3.0 and r["sigma_share"] == 0.5 and r["k"] == 3)}
    # OAT through the default: vary one of r, sigma share, k
    out["oat_flips"] = sorted({f"r = {r['r']}" if r["sigma_share"] == 0.5 and r["k"] == 3 else
                               f"sigma share = {r['sigma_share']}" if r["r"] == 3.0 and r["k"] == 3 else f"k = {r['k']}"
                               for r in res if r["c7_margin"] <= 0 and sum([r["r"] == 3.0, r["sigma_share"] == 0.5, r["k"] == 3]) >= 2})
    out["label"] = MV.label([r["c7_margin"] > 0 for r in res], out["oat_flips"], out["default"]["c7_margin"] > 0)
    save("vpggfree", out)


def part_vpggosc():
    pts = _design(MV.VPGG_OSC_PARAMS, 24)
    tasks = [(k, v, s) for k, _, v in pts for s in MV.OSC_SEEDS]
    t0 = time.time()
    res = MV._pool_map(MV.vpgg_osc_task, tasks, WORKERS)
    print(f"vpggosc {len(res)} runs in {time.time() - t0:.0f}s")
    by = {}
    for r in res:
        by.setdefault(r["key"], []).append(r)
    rows = []
    for k, o, v in pts:
        rr = by[k]
        mx = max(x["std_c"] for x in rr)
        rows.append((k, o, v, {"std_c": [x["std_c"] for x in rr], "max_std": mx, "c8_margin": MV.OSC_FLOOR - mx,
                               "mean_share": rr[0]["mean_share"]}))
    out = {"points": [{"key": k, "values": v, **r} for k, o, v, r in rows], "c8_margin": _summ(MV.VPGG_OSC_PARAMS, rows, lambda r: r["c8_margin"])}
    save("vpggosc", out)


# ---------------------------------------------------------------------------------------------------------- household parts

def _household(part, params, n_lhs, make_tasks, task_fn, agg, margin_keys):
    pts = _design(params, n_lhs)
    tasks = [t for k, _, v in pts for t in make_tasks(k, v)]
    t0 = time.time()
    res = MV._pool_map(task_fn, tasks, WORKERS)
    print(f"{part} {len(res)} runs in {time.time() - t0:.0f}s")
    by = {}
    for r in res:
        by.setdefault(r["key"], []).append(r)
    rows = [(k, o, v, agg(by[k])) for k, o, v in pts]
    out = {"points": [{"key": k, "values": v, **r} for k, o, v, r in rows]}
    for c in margin_keys:
        out[c] = _summ(params, rows, lambda r, c=c: r[c])
    save(part, out)


def part_negotiation():
    prs = MV.pairings()
    # Amendment 1 (prereg): one arm, fair_default (the v2.2 protocol's arm), and 8 LHS points, for compute.
    _household("negotiation", MV.NEG_PARAMS, 8,
               lambda k, v: [(k, v, "fair_default", a, b, 0) for a, b, _ in prs],
               MV.negotiation_task, MV.negotiation_aggregate, ("c4_margin",))


def part_pleasure():
    prs = MV.pairings()
    # Amendment 1 (prereg): seed 0 only and 8 LHS points, for compute.
    _household("pleasure", MV.PLEASURE_PARAMS, 8,
               lambda k, v: [(k, v, arm, a, b, s) for arm in ("v22_bindable", "baseline") for a, b, _ in prs for s in (0,)],
               MV.pleasure_task, MV.pleasure_aggregate, ("c5_margin", "c5_d3_margin"))


def part_seedv2():
    prs = MV.pairings()
    _household("seedv2", MV.SEEDV2_PARAMS, 16,
               lambda k, v: [(k, v, var, a, b, s) for var in ("author_seed_v2_bindable", "author_seed_v2_free_exit") for a, b, _ in prs for s in (0, 1, 2)],
               MV.seedv2_task, MV.seedv2_aggregate, ("c6_margin",))


# ---------------------------------------------------------------------------------------------------------- summary

ROWS = (
    ("C1", "horizon", "c1_margin", "Greedy loses at least 10% of optimal (gamma .95, 26 weeks)"),
    ("C2", "horizon", "c2_margin", "Concert: net carryover negative weekly, positive every 4 weeks"),
    ("C2b", "horizon", "c2b_margin", "Concert boundary m* is 2 to 4 weeks"),
    ("C3", "gap", "c3_margin", "Best friend-contact gap at most 14 days for every half-life (overlap .7)"),
    ("C3b", "gap", "c3_7_margin", "Best friend-contact gap at most 7 days (the '4 to 7 days' headline)"),
    ("C3c", "gap", "c3_ctrl_margin", "Sharing shortens the gap against the reunion-only control by at least 1 day"),
    ("C4", "negotiation", "c4_margin", "Living apart beats cohabiting with no pot on s_non by at least 0.02"),
    ("C5", "pleasure", "c5_margin", "Seed v2.2 beats the imposed baseline on pleasure (D2a)"),
    ("C5b", "pleasure", "c5_d3_margin", "Relational share of v2.2 households above 0.40 (D3)"),
    ("C6", "seedv2", "c6_margin", "Binding a stay commitment changes s_non by less than 0.02 (the null)"),
    ("C8", "vpggosc", "c8_margin", "VPGG: no oscillation (std below 0.05 in all seeds)"),
)


def summary():
    table = []
    for cid, part, key, text in ROWS:
        d = load(part)
        if d is None:
            table.append({"id": cid, "claim": text, "status": "not run"})
            continue
        s = d[key]
        table.append({"id": cid, "claim": text, "share": s["share"], "n": s["n"], "label": s["label"], "oat_flips": s["oat_flips"],
                      "top_param": s["top_param"], "top_rho": s["top_rho"], "default_margin": s["default_margin"]})
    d = load("vpggfree")
    if d:
        table.insert(-1, {"id": "C7", "claim": "VPGG voluntary beats compulsory on liberty v2 and empowerment", "share": d["share"],
                          "n": len(d["points"]), "label": d["label"], "oat_flips": d["oat_flips"], "top_param": None, "top_rho": None,
                          "default_margin": d["default"]["c7_margin"], "share_lib": d["share_lib"], "share_emp": d["share_emp"]})
    for t in table:
        if "share" in t:
            print(f"{t['id']:4} {t['label']:24} share {t['share']:.2f} (n {t['n']})  OAT flips: {', '.join(t['oat_flips']) or 'none'}"
                  f"  top: {t['top_param']} {'' if t['top_rho'] is None else f'{t['top_rho']:+.2f}'}")
        else:
            print(f"{t['id']:4} {t['status']}")
    KEPT.mkdir(parents=True, exist_ok=True)
    full = {"table": table}
    for part in ("horizon", "gap", "vpggfree", "vpggosc", "negotiation", "pleasure", "seedv2"):
        d = load(part)
        if d is not None:
            full[part] = d
    (KEPT / "results.json").write_text(json.dumps(full, indent=1, default=str))
    (KEPT / "report.html").write_text(report_html(table))
    return table


def report_html(table) -> str:
    import html
    colors = {"robust": "#1a7f37", "fragile": "#9a6700", "flips": "#cf222e"}
    rows = []
    for t in table:
        if "share" not in t:
            rows.append(f"<tr><td>{t['id']}</td><td>{html.escape(t['claim'])}</td><td colspan=4>not run</td></tr>")
            continue
        c = colors.get(t["label"], "#57606a")
        bar = f"<div class=bar><div style='width:{100 * t['share']:.0f}%;background:{c}'></div></div>"
        top = "" if t["top_param"] is None else f"{t['top_param']} ({t['top_rho']:+.2f})"
        rows.append(f"<tr><td>{t['id']}</td><td>{html.escape(t['claim'])}</td><td style='color:{c};font-weight:600'>{t['label']}</td>"
                    f"<td>{t['share']:.2f} of {t['n']}{bar}</td><td>{html.escape(', '.join(t['oat_flips']) or 'none')}</td><td>{html.escape(top)}</td></tr>")
    return f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Multiverse sweep</title><style>
:root{{--bg:#fff;--fg:#1f2328;--line:#d0d7de;--track:#eaeef2}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0d1117;--fg:#e6edf3;--line:#30363d;--track:#21262d}}}}
body{{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:16px}}
table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid var(--line);padding:6px;text-align:left;vertical-align:top}}
.bar{{background:var(--track);height:6px;margin-top:4px;width:120px}}.bar div{{height:6px}}
.wrap{{overflow-x:auto}}</style></head><body>
<h1>Multiverse sensitivity sweep, 2026-11-10</h1>
<p>Share of the multiverse (Latin hypercube points, or the full grid for C7) where each headline conclusion still holds when its
assumed parameters move over the preregistered ranges (docs/results/multiverse-prereg.md). Robust: at least 0.90 and no single parameter
endpoint flips it. Fragile: 0.50 to 0.90, or a single endpoint flips it. Flips: below 0.50. Scripted agents and exact solves, no model calls.
Agents feel nothing; pleasure is a gloss for a modeled state. Plain-English reading: docs/results/multiverse.md.</p>
<div class=wrap><table><tr><th>ID</th><th>Conclusion</th><th>Label</th><th>Holds in</th><th>Single parameters that flip it</th><th>Strongest driver (Spearman)</th></tr>
{''.join(rows)}</table></div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=["horizon", "gap", "vpggfree", "vpggosc", "negotiation", "pleasure", "seedv2", "summary"])
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    global WORKERS
    WORKERS = a.workers
    t0 = time.time()
    import os
    marker = OUT / f"{a.part}.started"
    if a.part in ("negotiation", "pleasure") and marker.exists() and not os.environ.get("MV_FORCE"):
        print(f"{a.part}: already started elsewhere ({marker}); skipping")
        return
    if a.part in ("negotiation", "pleasure"):
        OUT.mkdir(parents=True, exist_ok=True)
        marker.write_text(time.strftime("%Y-%m-%dT%H:%M:%S"))
    if a.part == "summary":
        summary()
    else:
        globals()[f"part_{a.part}"]()
    print(f"{a.part} done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
