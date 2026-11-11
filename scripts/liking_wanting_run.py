"""Liking vs wanting (ADR 0018 test 1), confirmatory run. Prereg: docs/results/liking-wanting-prereg.md.

  uv run python scripts/liking_wanting_run.py            # full run (about 10 minutes of CPU), writes runs/liking-wanting/
  uv run python scripts/liking_wanting_run.py --keep     # also copy results and report to experiments/kept/ and log the run
  uv run python scripts/liking_wanting_run.py --report-only [results.json]

Scripted agents, exact solves, no model calls. Wording rule: agents feel nothing; "liking" and "wanting" are glosses.
"""
import json
import shutil
import sys
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import log as LG  # noqa: E402
from mar import report as RP  # noqa: E402
from mar import stats as St  # noqa: E402
from mar import viz  # noqa: E402
from mar import wanting as Wg  # noqa: E402

OUT = ROOT / "runs" / "liking-wanting"
KEPT = ROOT / "experiments" / "kept" / "liking-wanting-2026-11-10"
RUN_ID = "liking-wanting-2026-11-10"
N_PERSONAS, SEED = 80, 20261110
BASE = Wg.WantParams(enabled=True)
if "--toy" in sys.argv:                       # smoke fixture only: 4 personas, 14 days, separate output folder, never kept
    N_PERSONAS, SEED, BASE, OUT = 4, 999, Wg.WantParams(enabled=True, days=14), ROOT / "runs" / "liking-wanting-toy"
ENVS = (Wg.PLAIN, Wg.HEAVY)
RULES = (Wg.NO_RULE, Wg.CLOSURE, Wg.CAP)
KEYS = ("total_liking", "mean_liking", "G_units", "cued_units", "liking_per_cued_unit", "liking_to_wanting", "gap_per_unit",
        "G_sessions", "closure_rate", "next_day_verdict", "divergence", "escalation", "plan")


def _slim(m):
    return {k: m[k] for k in KEYS}


def persona_record(q):
    rec = {"params": {k: getattr(q, k) for k in Wg.PERSONA_BOX}, "cells": {}, "twin": {}, "nosens": {}, "checks": {}}
    for e in ENVS:
        for u in RULES:
            rec["cells"][f"{e.name}/{u.name}"] = {a: _slim(m) for a, m in Wg.solve_all(q, e, u).items()}
            tw = Wg.solve_all(q.equal(), e, u)                      # P1: wanting = liking
            off = Wg.solve_all(replace(q, enabled=False), e, u)      # P1b: flag off
            rec["twin"][f"{e.name}/{u.name}"] = {a: _slim(m) for a, m in tw.items()}
            ok1 = all(tw[a]["gap_per_unit"] == 0.0 and tw[a]["cued_units"] == 0 and tw[a]["liking_to_wanting"] == 1.0
                      and tw[a]["liking_per_cued_unit"] == Wg.NM for a in Wg.AGENTS) and tw["W"]["plan"] == tw["L"]["plan"]
            ok1b = all(off[a]["gap_per_unit"] == 0.0 and off[a]["cued_units"] == 0 for a in Wg.AGENTS) and off["W"]["plan"] == off["L"]["plan"]
            rec["checks"][f"P1 {e.name}/{u.name}"] = bool(ok1)
            rec["checks"][f"P1b {e.name}/{u.name}"] = bool(ok1b)
        ns = Wg.solve_all(q.no_sensitization(), e, Wg.NO_RULE)
        rec["nosens"][e.name] = {a: _slim(m) for a, m in ns.items()}
    return rec


def default_point():
    q = BASE
    D = {"cells": {f"{e.name}/{u.name}": {a: _slim(m) for a, m in Wg.solve_all(q, e, u).items()} for e in ENVS for u in RULES}}
    D["twin"] = {f"{e.name}/{u.name}": {a: _slim(m) for a, m in Wg.solve_all(q.equal(), e, u).items()} for e in ENVS for u in RULES}
    D["gamma09"] = {f"{e.name}/none": _slim(Wg.solve(replace(q, gamma=0.9), e, Wg.NO_RULE, "O")) for e in ENVS}
    O = D["cells"]["plain/none"]["O"]["total_liking"]
    sweep = []
    for name, vals in (("sig", (0.0, 0.06, 0.12, 0.2, 0.3)), ("c", (0.0, 0.75, 1.5, 2.5)), ("variable", (0.0, 0.5, 1.0, 2.0))):
        for v in vals:
            qq, env = q, Wg.HEAVY
            if name == "variable":
                env = replace(Wg.HEAVY, variable=v)
            else:
                qq = replace(q, **{name: v})
            r = Wg.solve_all(qq, env, Wg.NO_RULE)
            sweep.append({"param": name, "value": v, "W_loss": 100 * (O - r["W"]["total_liking"]) / O,
                          "L_loss": 100 * (O - r["L"]["total_liking"]) / O, "W_closure": r["W"]["closure_rate"],
                          "W_ndv": r["W"]["next_day_verdict"], "W_cued": r["W"]["cued_units"], "W_gap": r["W"]["gap_per_unit"]})
    D["sweep"] = sweep
    return D


# --------------------------------------------------------------------------- analysis

def loss(rec, cell, a):
    O = rec["cells"]["plain/none"]["O"]["total_liking"]
    return 100 * (O - rec["cells"][cell][a]["total_liking"]) / O


def WC(rec, cell):
    return loss(rec, cell, "W") - loss(rec, cell, "L")


def num(x):
    return None if isinstance(x, str) else float(x)


def analyse(P):
    rows, checks = [], {}
    # deterministic checks
    checks["P0"] = all(len({p["cells"][c]["O"]["total_liking"] for c in ("plain/none", "plain/closure", "heavy/none", "heavy/closure")}) == 1
                       and len({p["cells"][c]["O"]["plan"] for c in ("plain/none", "plain/closure", "heavy/none", "heavy/closure")}) == 1 for p in P)
    checks["P1"] = all(v for p in P for k, v in p["checks"].items() if k.startswith("P1 "))
    checks["P1b"] = all(v for p in P for k, v in p["checks"].items() if k.startswith("P1b "))
    divs = [num(p["nosens"][e][a]["divergence"]) for p in P for e in ("plain", "heavy") for a in ("W", "O")]
    measurable = [d for d in divs if d is not None]
    checks["P2"] = bool(measurable) and all(abs(d) <= 1e-9 for d in measurable)
    checks["P2_detail"] = {"measurable": len(measurable), "of": len(divs), "max_abs": max((abs(d) for d in measurable), default=None)}

    def A(f):
        return np.array([f(p) for p in P], dtype=float)

    share_vals = [WC(p, "heavy/none") / loss(p, "heavy/none", "W") for p in P if loss(p, "heavy/none", "W") > 0]
    preds = [
        ("P3", "WC(heavy, none) - WC(plain, none), points", A(lambda p: WC(p, "heavy/none") - WC(p, "plain/none")), ">=", 5.0),
        ("P4a", "WC(heavy, none) - WC(heavy, closure), points", A(lambda p: WC(p, "heavy/none") - WC(p, "heavy/closure")), ">=", 10.0),
        ("P4b", "WC(heavy, closure) - WC(plain, none), points", A(lambda p: WC(p, "heavy/closure") - WC(p, "plain/none")), "<=", 3.0),
        ("P5a", "W loss(heavy, cap) - W loss(heavy, closure), points", A(lambda p: loss(p, "heavy/cap", "W") - loss(p, "heavy/closure", "W")), ">=", 5.0),
        ("P5b", "O loss(heavy, cap), points", A(lambda p: loss(p, "heavy/cap", "O")), ">=", 2.0),
        ("P5c", "W loss(heavy, none) - W loss(heavy, cap), points", A(lambda p: loss(p, "heavy/none", "W") - loss(p, "heavy/cap", "W")), ">=", 2.0),
        ("P6a", "W loss(heavy, none), % of lifetime optimum", A(lambda p: loss(p, "heavy/none", "W")), ">=", 20.0),
        ("P6b", "wanting share of W's loss, heavy", np.array(share_vals, dtype=float), ">=", 0.2),
        ("P6c", "O cued units / W cued units, heavy, none",
         A(lambda p: p["cells"]["heavy/none"]["O"]["cued_units"] / p["cells"]["heavy/none"]["W"]["cued_units"]), "<=", 0.7),
        ("P6d", "WC(plain, none), points", A(lambda p: WC(p, "plain/none")), "<=", 3.0),
    ]
    nm = {}
    for pid, cell_a, cell_b, key, thr, label in (("P7a", "plain/none", "heavy/none", "closure_rate", 0.2, "closure rate, W: plain - heavy"),
                                                  ("P7b", "plain/none", "heavy/none", "next_day_verdict", 0.5, "next-day verdict, W: plain - heavy"),
                                                  ("P7c", "heavy/closure", "heavy/none", "closure_rate", 0.2, "closure rate, W in heavy: closure - none")):
        vals = [(num(p["cells"][cell_a]["W"][key]), num(p["cells"][cell_b]["W"][key])) for p in P]
        ok = [a - b for a, b in vals if a is not None and b is not None]
        nm[pid] = len(vals) - len(ok)
        preds.append((pid, label, np.array(ok, dtype=float), ">=", thr))
    raw = []
    for pid, label, x, op, thr in preds:
        if len(x) == 0:
            raw.append({"id": pid, "quantity": label, "n": 0, "estimate": Wg.NM, "p": 1.0})
            continue
        sh = (x - thr) if op == ">=" else (thr - x)
        t = St.permutation_test(sh, np.zeros(len(sh)), paired=True, alternative="greater", n_perm=20000, seed=0)
        ci = St.bootstrap_ci(x, np.mean, n_boot=10000, seed=0)
        sd = float(np.std(x, ddof=1)) if len(x) > 1 else 0.0
        raw.append({"id": pid, "quantity": label, "n": int(len(x)), "op": op, "threshold": thr, "estimate": float(np.mean(x)),
                    "lo": ci.lo, "hi": ci.hi, "p": t.p, "cohen_d": (float(np.mean(x)) / sd) if sd > 0 else None,
                    "min": float(np.min(x)), "max": float(np.max(x)), "dropped": nm.get(pid, len(P) - len(x))})
    # flags
    def flagW(p, cell):
        return Wg.flag(p["cells"][cell]["W"], p["twin"][cell]["W"])
    fn = np.array([flagW(p, "heavy/none") for p in P], dtype=float)
    fc = np.array([flagW(p, "heavy/closure") for p in P], dtype=float)
    k, n = int(fn.sum()), len(fn)
    cp = St.clopper_pearson(k, n)
    raw.append({"id": "P8a", "quantity": "flag rate, W, heavy/none", "n": n, "op": ">=", "threshold": 0.8, "estimate": k / n,
                "lo": cp.lo, "hi": cp.hi, "p": St.sign_test(k, n, p0=0.8, alternative="greater"), "k": k, "dropped": 0})
    d = fn - fc
    t = St.permutation_test(d - 0.4, np.zeros(n), paired=True, alternative="greater", n_perm=20000, seed=0)
    ci = St.bootstrap_ci(d, np.mean, n_boot=10000, seed=0)
    raw.append({"id": "P8b", "quantity": "flag rate, W, heavy: none - closure", "n": n, "op": ">=", "threshold": 0.4, "estimate": float(d.mean()),
                "lo": ci.lo, "hi": ci.hi, "p": t.p, "dropped": 0})
    adj = St.holm([r["p"] for r in raw])
    for r, a in zip(raw, adj):
        r["p_holm"] = a
        if isinstance(r["estimate"], str):
            r["label"] = "miss: not measurable here"
            continue
        meets = r["estimate"] >= r["threshold"] if r["op"] == ">=" else r["estimate"] <= r["threshold"]
        inside = (r["lo"] >= r["threshold"]) if r["op"] == ">=" else (r["hi"] <= r["threshold"])
        if meets and inside and a <= 0.05:
            r["label"] = "holds robustly"
        elif meets:
            r["label"] = "holds but CI crosses threshold"
        elif not meets and ((r["hi"] < r["threshold"]) if r["op"] == ">=" else (r["lo"] > r["threshold"])):
            r["label"] = "miss robust"
        else:
            r["label"] = "miss but CI crosses threshold"
        rows.append(r)
    return checks, raw


def table_by_cell(P):
    """Mean [95% CI] of every measure per environment x rule x agent (the 'how much gap each allows' table)."""
    out = {}
    for e in ENVS:
        for u in RULES:
            c = f"{e.name}/{u.name}"
            for a in Wg.AGENTS:
                row = {}
                for key, f in (("loss", lambda p: loss(p, c, a)),
                               ("WC", (lambda p: WC(p, c)) if a == "W" else None),
                               ("gap_per_unit", lambda p: p["cells"][c][a]["gap_per_unit"]),
                               ("liking_to_wanting", lambda p: num(p["cells"][c][a]["liking_to_wanting"])),
                               ("liking_per_cued_unit", lambda p: num(p["cells"][c][a]["liking_per_cued_unit"])),
                               ("closure_rate", lambda p: num(p["cells"][c][a]["closure_rate"])),
                               ("next_day_verdict", lambda p: num(p["cells"][c][a]["next_day_verdict"])),
                               ("cued_units", lambda p: p["cells"][c][a]["cued_units"]),
                               ("G_units", lambda p: p["cells"][c][a]["G_units"]),
                               ("divergence", lambda p: num(p["cells"][c][a]["divergence"]))):
                    if f is None:
                        continue
                    xs = [f(p) for p in P]
                    vals = np.array([x for x in xs if x is not None], dtype=float)
                    if len(vals) == 0:
                        row[key] = {"estimate": Wg.NM, "n": 0}
                        continue
                    ci = St.bootstrap_ci(vals, np.mean, n_boot=4000, seed=0)
                    row[key] = {"estimate": float(vals.mean()), "lo": ci.lo, "hi": ci.hi, "n": int(len(vals)), "nm": len(xs) - len(vals)}
                fl = [Wg.flag(p["cells"][c][a], p["twin"][c][a]) for p in P]
                cp = St.clopper_pearson(sum(fl), len(fl))
                row["flag_rate"] = {"estimate": sum(fl) / len(fl), "lo": cp.lo, "hi": cp.hi, "n": len(fl)}
                out[f"{c}/{a}"] = row
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    qs = Wg.draw_personas(BASE, N_PERSONAS, SEED)
    with Pool() as pool:
        P = pool.map(persona_record, qs)
    R = {"run_id": RUN_ID, "n_personas": N_PERSONAS, "seed": SEED, "base": {k: getattr(BASE, k) for k in BASE.__dataclass_fields__},
         "persona_box": Wg.PERSONA_BOX, "n_states_default_heavy": len(Wg.WTable(BASE, Wg.HEAVY, Wg.NO_RULE).states)}
    R["checks"], R["predictions"] = analyse(P)
    R["cells"] = table_by_cell(P)
    R["default_point"] = default_point()
    R["personas"] = P
    (OUT / "results.json").write_text(json.dumps(R, indent=1))
    (OUT / "report.html").write_text(html(R))
    print(json.dumps(R["checks"], indent=1))
    for r in R["predictions"]:
        est = r["estimate"] if isinstance(r["estimate"], str) else f"{r['estimate']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]"
        print(f"{r['id']:4s} {est:32s} {r.get('op', '')} {r.get('threshold', '')}  p_holm={r['p_holm']:.4g}  {r['label']}  n={r['n']}")
    print("wrote", OUT / "results.json", OUT / "report.html")
    if "--keep" in sys.argv and "--toy" not in sys.argv:
        keep(R)


def keep(R):
    KEPT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT / "report.html", KEPT / "report.html")
    slim = {k: v for k, v in R.items() if k != "personas"}
    slim["personas"] = [{"params": p["params"], "cells": {c: {a: {k: v for k, v in m.items() if k != "plan"} for a, m in d.items()}
                                                          for c, d in p["cells"].items()}} for p in R["personas"]]
    (KEPT / "results.json").write_text(json.dumps(slim, indent=1))
    held = sum(r["label"] == "holds robustly" for r in R["predictions"])
    det = sum(bool(R["checks"][k]) for k in ("P0", "P1", "P1b", "P2"))
    row = {"run_id": RUN_ID, "kind": "liking-wanting", "timestamp": LG.now_utc(), "git_commit": LG.git_commit(),
           "spec": "docs/results/liking-wanting-prereg.md", "cards_hash": None, "oracle_version": None, "agents": ["W", "L", "O"],
           "months": None, "seed": SEED, "model": None, "cost_usd": 0.0, "backends": {"solver": "exact backward induction"},
           "verdict": f"{held} of {len(R['predictions'])} tested predictions hold robustly; {det} of 4 deterministic checks pass",
           "seams": 0, "report": str((KEPT / "report.html").relative_to(ROOT)), "trace": str((KEPT / "results.json").relative_to(ROOT)),
           "note": f"ADR 0018 test 1, scripted, {N_PERSONAS} personas x 2 environments x 3 rules x 3 agents, no model calls"}
    LG._append(ROOT / "experiments" / LG.LOG_NAME, row)
    print("kept", KEPT, "and logged to experiments/log.jsonl")


# --------------------------------------------------------------------------- report

E = RP.escape if hasattr(RP, "escape") else __import__("html").escape
CELL_LABEL = {"plain/none": "plain", "plain/closure": "plain + closure ritual", "plain/cap": "plain + stopping rule",
              "heavy/none": "cue-heavy", "heavy/closure": "cue-heavy + closure ritual", "heavy/cap": "cue-heavy + stopping rule"}
AGENT_LABEL = {"W": "acts on wanting", "L": "greedy on liking", "O": "lifetime optimizer"}


def fmt(d, nd=1):
    if d is None:
        return ""
    if isinstance(d.get("estimate"), str):
        return d["estimate"]
    s = f"{d['estimate']:.{nd}f} [{d['lo']:.{nd}f}, {d['hi']:.{nd}f}]"
    if d.get("nm"):
        s += f" ({d['nm']} not measurable)"
    return s


def chart_loss(R, theme):
    c, col = viz.THEMES[theme], viz.SERIES[theme]
    from matplotlib.figure import Figure
    fig = Figure(figsize=(7.2, 3.6))
    ax = fig.add_subplot(111)
    viz._style_axes(ax, c)
    cells = list(CELL_LABEL)
    x = np.arange(len(cells))
    for k, a in enumerate(("W", "L", "O")):
        m = [R["cells"][f"{cl}/{a}"]["loss"] for cl in cells]
        est = np.array([v["estimate"] for v in m])
        err = np.array([[v["estimate"] - v["lo"] for v in m], [v["hi"] - v["estimate"] for v in m]])
        ax.bar(x + (k - 1) * 0.27, est, 0.25, yerr=err, color=col[k], ecolor=c["ink2"], capsize=2, label=AGENT_LABEL[a])
    ax.set_xticks(x)
    ax.set_xticklabels(["plain", "plain\n+closure", "plain\n+cap", "cue-heavy", "cue-heavy\n+closure", "cue-heavy\n+cap"], color=c["ink2"], fontsize=9)
    ax.set_ylabel("liking lost, % of lifetime optimum", color=c["ink2"], fontsize=10)
    leg = ax.legend(frameon=False, fontsize=9, labelcolor=c["ink"], loc="upper left")
    leg.get_frame().set_alpha(0)
    fig.tight_layout()
    return viz._finish(fig, theme)


def chart_sweep(R, theme):
    c, col = viz.THEMES[theme], viz.SERIES[theme]
    from matplotlib.figure import Figure
    fig = Figure(figsize=(7.2, 2.8))
    for k, name in enumerate(("sig", "c", "variable")):
        ax = fig.add_subplot(1, 3, k + 1)
        viz._style_axes(ax, c)
        pts = [s for s in R["default_point"]["sweep"] if s["param"] == name]
        ax.plot([s["value"] for s in pts], [s["W_loss"] for s in pts], "o-", color=col[0], label="acts on wanting")
        ax.plot([s["value"] for s in pts], [s["L_loss"] for s in pts], "s--", color=col[1], label="greedy on liking")
        ax.set_xlabel({"sig": "sensitization", "c": "cue strength", "variable": "variable reward"}[name], color=c["ink2"], fontsize=9)
        if k == 0:
            ax.set_ylabel("% lost", color=c["ink2"], fontsize=9)
            ax.legend(frameon=False, fontsize=8, labelcolor=c["ink"])
    fig.tight_layout()
    return viz._finish(fig, theme)


def html(R):
    preds = R["predictions"]
    ch = R["checks"]
    prow = [[E(r["id"]), E(r["quantity"]),
             E(r["estimate"] if isinstance(r["estimate"], str) else f"{r['estimate']:.3f} [{r['lo']:.3f}, {r['hi']:.3f}]"),
             E(f"{r.get('op', '')} {r.get('threshold', '')}"), E(f"{r['p_holm']:.3g}"), E(r["label"])] for r in preds]
    crow = [[E(k), "pass" if ch[k] else "FAIL"] for k in ("P0", "P1", "P1b", "P2")]
    cells_rows = []
    for cl in CELL_LABEL:
        for a in ("W", "L", "O"):
            m = R["cells"][f"{cl}/{a}"]
            cells_rows.append([E(CELL_LABEL[cl]), E(AGENT_LABEL[a]), fmt(m["loss"]), fmt(m["gap_per_unit"], 2),
                               fmt(m["liking_per_cued_unit"], 2), fmt(m["closure_rate"], 2), fmt(m["next_day_verdict"], 2),
                               fmt(m["flag_rate"], 2)])
    dp = R["default_point"]["cells"]
    O = dp["plain/none"]["O"]["total_liking"]
    drows = [[E(CELL_LABEL[cl]), E(AGENT_LABEL[a]), f"{100 * (O - dp[cl][a]['total_liking']) / O:.1f}", E(dp[cl][a]["plan"][:28])]
             for cl in ("plain/none", "heavy/none", "heavy/closure", "heavy/cap") for a in ("W", "L", "O")]
    interp = R.get("interpretation", [])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Liking vs wanting</title><style>{RP.CSS}</style></head><body><main>
<h1>Liking vs wanting: how much gap each environment and rule allows</h1>
<p class="meta">ADR 0018 test 1. Scripted agents, exact solves, {R['n_personas']} personas drawn from an assumed parameter box (seed {R['seed']}), 28 days of 4 slots. Agents feel nothing: "liking" and "wanting" are glosses for modeled values. Every parameter is assumed. Prereg: docs/results/liking-wanting-prereg.md. Results: docs/results/liking-wanting.md.</p>
<section><h2>What was asked</h2><p>Pleasure is split in two. Liking is the payoff that counts. Wanting is what drives choice for an agent that acts on it: liking plus a pull from cues that grows with use (sensitization). A loop built to diverge will diverge, so the question is comparative: how much liking does acting on wanting lose in a cue-heavy, variable-reward environment against a plain one, and how much do a closure ritual and a stopping rule give back? And does the lifetime optimizer of the horizon study avoid the trap?</p></section>
<section><h2>Interpretation</h2>{''.join(f'<p>{E(p)}</p>' for p in interp) or '<p class="note">Added after the run.</p>'}</section>
<section><h2>Liking lost, by environment, rule and agent</h2><p class="note">Percent of the lifetime optimum's liking (no rule). Bars: mean over personas, 95% bootstrap interval.</p>{RP._both(chart_loss, R)}</section>
<section><h2>Preregistered predictions</h2>{RP._table(["ID", "Quantity", "Mean [95% CI]", "Threshold", "Holm p", "Label"], prow)}
<p class="note">Deterministic checks (pass or fail, no interval):</p>{RP._table(["Check", "Result"], crow)}</section>
<section><h2>The measures, every cell</h2><p class="note">Mean [95% CI] over personas. Flag rate with an exact interval. "Not measurable here" when a number cannot be computed.</p>
{RP._table(["Environment and rule", "Agent", "Liking lost %", "Gap per unit", "Liking per cued unit", "Closure rate", "Next-day verdict", "Flag rate"], cells_rows)}</section>
<section><h2>Default persona, solved exactly</h2><p class="note">First 7 days of each plan (G cued activity, P plain activity, Q quiet). Deterministic, no interval.</p>
{RP._table(["Environment and rule", "Agent", "Liking lost %", "Plan, first week"], drows)}</section>
<section><h2>Sensitivity at the default persona (descriptive)</h2><p class="note">Cue-heavy, no rule. One parameter varied at a time.</p>{RP._both(chart_sweep, R)}</section>
</main></body></html>"""


if __name__ == "__main__":
    if "--report-only" in sys.argv:
        i = sys.argv.index("--report-only")
        src = Path(sys.argv[i + 1]) if len(sys.argv) > i + 1 and not sys.argv[i + 1].startswith("--") else OUT / "results.json"
        R = json.loads(src.read_text())
        (OUT / "report.html").write_text(html(R))
        print("wrote", OUT / "report.html")
        if "--keep" in sys.argv:
            keep(R)
    else:
        main()
