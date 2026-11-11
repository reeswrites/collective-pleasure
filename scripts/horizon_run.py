"""Horizon study: lifetime pleasure versus greedy, solved exactly (ADR 0017, docs/results/horizon-prereg.md).

  uv run python scripts/horizon_run.py

Deterministic, no seeds, no model calls. Writes runs/horizon/results.json and runs/horizon/report.html (self-contained SVG, no libraries).
Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.
"""
import json
import sys
from dataclasses import replace
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import horizon as Hz  # noqa: E402

OUT = ROOT / "runs" / "horizon"
Q0 = Hz.HorizonParams()
S0 = Hz.START
GAMMAS = [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, .95, .99, 1.0]
KS = [1, 2, 3, 4, 6, 8, 12, 16, 26, 52]
DELTAS = [0, .05, .1, .15, .2, .3, .4]
BETAS = [0, .5, 1, 1.5, 2, 3]
SPACINGS = [1, 2, 3, 4, 5, 6, 8, 13, 26]
HORIZON = 26


def fr(x):
    return Fr(str(x))


def first_at(xs, ys, thr):
    for x, y in zip(xs, ys):
        if y >= thr:
            return x
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    R = {"params": {k: str(v) for k, v in Q0.__dict__.items()}, "start": list(S0), "horizon_default": HORIZON}
    tab = Hz.Table(Q0)
    R["n_states"] = len(tab.states)

    # ---- P1: state feedback off => greedy loss zero
    off = Hz.Table(Q0.off())
    gs, ks = (0, .25, .5, .75, .9, .99, 1.0), (1, 2, 3, 4, 6, 8, 12, 26)
    R["p1_max_abs_loss_off"] = max(abs(Hz.greedy_loss(off, S0, k, g)["loss"]) for g in gs for k in ks)
    R["p1_cells"] = len(gs) * len(ks)
    part = Hz.Table(replace(Q0, delta=Fr(0), beta=Fr(0)))      # adaptation and commitment off only; anticipation, memory, pot, need still on
    R["p1b_adapt_commit_off_only"] = {str(g): Hz.greedy_loss(part, S0, HORIZON, g)["pct"] for g in (.9, 1.0)}

    # ---- sweep A: gamma
    A = {"gamma": GAMMAS, "pct_finite": [], "loss_finite": [], "opt": [], "pct_infinite": []}
    for g in GAMMAS:
        r = Hz.greedy_loss(tab, S0, HORIZON, g)
        A["pct_finite"].append(r["pct"]); A["loss_finite"].append(r["loss"]); A["opt"].append(r["opt"])
        A["pct_infinite"].append(Hz.greedy_loss_infinite(tab, S0, g)["pct"] if g < 1 else None)
    R["sweep_gamma"] = A
    R["gamma_large10"] = first_at(GAMMAS, A["pct_finite"], 10.0)

    # ---- sweep B: horizon
    B = {"K": KS}
    for g in (.9, 1.0):
        rr = [Hz.greedy_loss(tab, S0, k, g) for k in KS]
        B[f"pct_g{g}"] = [r["pct"] for r in rr]; B[f"loss_g{g}"] = [r["loss"] for r in rr]
    R["sweep_horizon"] = B
    R["horizon_large10_g1"] = first_at(KS, B["pct_g1.0"], 10.0)
    R["horizon_large10_g0.9"] = first_at(KS, B["pct_g0.9"], 10.0)

    # ---- critical discount
    R["critical_gamma"] = {str(k): Hz.critical_gamma(tab, S0, k) for k in (2, 4, 6, 12, 26, 52)}
    R["critical_gamma_vs_delta"] = {}
    R["critical_gamma_vs_beta"] = {}

    # ---- sweep C, D
    C = {"delta": DELTAS, "pct": [], "loss": [], "gstar": []}
    for d in DELTAS:
        t = Hz.Table(replace(Q0, delta=fr(d)))
        r = Hz.greedy_loss(t, S0, HORIZON, .95); C["pct"].append(r["pct"]); C["loss"].append(r["loss"])
        C["gstar"].append(Hz.critical_gamma(t, S0, HORIZON))
    D = {"beta": BETAS, "pct": [], "loss": [], "gstar": [], "H_in_first6": [], "H_total": []}
    for b in BETAS:
        t = Hz.Table(replace(Q0, beta=fr(b)))
        r = Hz.greedy_loss(t, S0, HORIZON, .9); D["pct"].append(r["pct"]); D["loss"].append(r["loss"])
        D["gstar"].append(Hz.critical_gamma(t, S0, HORIZON))
        D["H_in_first6"].append(sum(1 for a in r["opt_plan"][:6] if a == Hz.H_)); D["H_total"].append(sum(1 for a in r["opt_plan"] if a == Hz.H_))
    R["sweep_delta"], R["sweep_beta"] = C, D
    R["delta_large10"] = first_at(DELTAS, C["pct"], 10.0); R["beta_large10"] = first_at(BETAS, D["pct"], 10.0)

    # ---- DESCRIPTIVE, added after the confirmatory run (not preregistered): the discount at which the optimal plan first honors the commitment
    lo, hi = 0.5, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if any(a == Hz.H_ for a in Hz.greedy_loss(tab, S0, HORIZON, mid)["opt_plan"][:6]):
            hi = mid
        else:
            lo = mid
    R["gamma_commitment_accepted"] = hi

    # ---- optimal plans and heuristics
    R["plans"] = {}
    for g in (.9, 1.0):
        r = Hz.greedy_loss(tab, S0, HORIZON, g)
        R["plans"][str(g)] = {"optimal": Hz.plan_str(r["opt_plan"]), "greedy": Hz.plan_str(r["greedy_plan"]), "opt": r["opt"], "greedy_total": r["greedy"],
                              "H_in_first6": sum(1 for a in r["opt_plan"][:6] if a == Hz.H_)}
    heur = {"rotate-1": Hz.rotate_policy(tab, 1), "rotate-2": Hz.rotate_policy(tab, 2), "rotate-4": Hz.rotate_policy(tab, 4),
            "ritual-weekly": Hz.ritual_policy(tab, 1), "ritual-every-2": Hz.ritual_policy(tab, 2), "ritual-every-4": Hz.ritual_policy(tab, 4),
            "greedy": Hz.greedy_policy(tab)}
    R["heuristics"] = {}
    for g in (.9, 1.0):
        _, vopt = Hz.optimal_plan(tab, S0, HORIZON, g)
        rows = {}
        for nm, pol in heur.items():
            _, tot = Hz.run_policy(tab, S0, HORIZON, g, pol) if True else (None, None)
            rows[nm] = {"total": tot, "pct_of_optimal": 100 * tot / vopt, "loss": vopt - tot}
        rows["optimal"] = {"total": vopt, "pct_of_optimal": 100.0, "loss": 0.0}
        R["heuristics"][str(g)] = rows

    # ---- P3: witness, exhaustive in exact rationals, then z3
    R["witness"] = {}
    for g in (Fr(9, 10), Fr(1)):
        w_any = Hz.find_witness(Q0, g, kmax=6)
        w_start = Hz.find_witness(Q0, g, kmax=6, from_start_only=True)
        entry = {}
        for nm, w in (("minimal_k_any_reachable_state", w_any), ("from_start", w_start)):
            if w is None:
                entry[nm] = None
                continue
            chk = Hz.z3_check_witness(Q0, w)
            entry[nm] = {"state": list(w["state"]), "state_text": Hz.describe_state(w["state"]), "k": w["k"], "gamma": str(w["gamma"]),
                         "greedy_plan": Hz.plan_str(w["greedy_plan"]), "greedy_total": str(w["greedy_total"]), "greedy_total_float": float(w["greedy_total"]),
                         "best_plan": Hz.plan_str(w["best_plan"]), "best_total": str(w["best_total"]), "best_total_float": float(w["best_total"]),
                         "z3": {k: v for k, v in chk.items()}}
        R["witness"][str(g)] = entry

    # ---- concert: net carryover and dose/spacing
    R["concert"] = {}
    for g in (.95, 1.0):
        rows = []
        for m in SPACINGS:
            n = len(range(m - 1, HORIZON, m))
            x = Hz.concert_gain(Q0, S0, HORIZON, g, m)
            x["n_scheduled"] = n; x["net_carryover_per_concert"] = x["net_carryover"] / n
            rows.append(x)
        R["concert"][str(g)] = rows
    # ---- the worked case
    people = {str(h): Hz.GapParams(H=float(h)) for h in (10, 20, 45, 90)}
    G = {}
    for h, p in people.items():
        b = Hz.best_gaps(p)
        G[h] = {"best_lifetime": b["best_lifetime"], "best_experienced_old": b["best_experienced_old"], "best_remembered_old": b["best_remembered_old"],
                "ratio_remembered_to_experienced": b["ratio_remembered_old_to_experienced_old"],
                "at_best": {k: v for k, v in Hz.gap_score(p, b["best_lifetime"]).items()},
                "curve": [[r["gap"], r["lifetime"], r["experienced"], r["remembered"]] for r in b["curve"]]}
    R["gap"] = G
    R["gap_mismatch_unified"] = Hz.gap_mismatch(people["20"], people["90"])
    R["gap_mismatch_old_experienced"] = Hz.gap_mismatch(people["20"], people["90"], sp=Hz.PURE_PRESENT)
    sp = Hz.SelfParams()
    R["gap_vividness"] = {
        "good_reunion_15": Hz.trace_value(15.0, sp), "bad_betrayal_-20": Hz.trace_value(-20.0, sp),
        "bad_-20_no_rumination": Hz.trace_value(-20.0, replace(sp, rum=1.0)),
        "peak_15_not_an_ending": Hz.trace_value(15.0, sp, ending=False), "mild_5": Hz.trace_value(5.0, sp),
        "stretch": {str(L): Hz.stretch_value(L, 1.0) for L in (7, 30, 90, 365)}}
    # sensitivity of the best gap to the vividness weights
    R["gap_vividness_sensitivity"] = {nm: Hz.best_gaps(people["45"], sp=s)["best_lifetime"] for nm, s in (
        ("default", sp), ("memory weight 0 (old experienced)", Hz.PURE_PRESENT), ("memory weight x3", replace(sp, nu=0.03)),
        ("no ending boost", replace(sp, w_end=0.0)), ("no rumination", replace(sp, rum=1.0)), ("fast forgetting (tau 10)", replace(sp, tau_m=10.0)))}

    def conv(o):
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(v) for v in o]
        if hasattr(o, "item"):
            return o.item()
        return o
    R = conv(R)
    (OUT / "results.json").write_text(json.dumps(R, indent=1))
    (OUT / "report.html").write_text(html(R))
    print(json.dumps({k: R[k] for k in ("n_states", "p1_max_abs_loss_off", "p1b_adapt_commit_off_only", "gamma_large10", "horizon_large10_g1", "critical_gamma", "gamma_commitment_accepted",
                                         "delta_large10", "beta_large10", "plans")}, indent=1))
    print("wrote", OUT / "results.json", OUT / "report.html")


# --------------------------------------------------------------------------- report

def svg_lines(title, xlabel, ylabel, series, xs_log=False, W=520, H=300, vlines=(), note=""):
    """series: list of (label, [(x, y), ...]). Plain SVG; colors from CSS classes so dark mode works."""
    pad_l, pad_r, pad_t, pad_b = 52, 14, 28, 44
    pts = [p for _, s in series for p in s if p[1] is not None]
    xmin, xmax = min(p[0] for p in pts), max(p[0] for p in pts)
    ymin, ymax = min(0.0, min(p[1] for p in pts)), max(p[1] for p in pts)
    ymin = 0.0 if abs(ymin) < 1e-9 else ymin
    if ymax == ymin:
        ymax = ymin + 1
    import math
    fx = (lambda x: math.log(x)) if xs_log else (lambda x: x)
    X = lambda x: pad_l + (fx(x) - fx(xmin)) / ((fx(xmax) - fx(xmin)) or 1) * (W - pad_l - pad_r)
    Y = lambda y: H - pad_b - (y - ymin) / (ymax - ymin) * (H - pad_t - pad_b)
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{title}"><text x="{pad_l}" y="16" class="t">{title}</text>']
    for i in range(5):
        yv = ymin + (ymax - ymin) * i / 4
        o.append(f'<line x1="{pad_l}" x2="{W-pad_r}" y1="{Y(yv):.1f}" y2="{Y(yv):.1f}" class="g"/><text x="{pad_l-6}" y="{Y(yv)+4:.1f}" class="a" text-anchor="end">{yv:.3g}</text>')
    xt = sorted({p[0] for p in pts})
    if len(xt) > 7:
        xt = [xt[round(i * (len(xt) - 1) / 6)] for i in range(7)]
    for xv in xt:
        o.append(f'<text x="{X(xv):.1f}" y="{H-pad_b+16}" class="a" text-anchor="middle">{xv:.3g}</text>')
    for xv, lab in vlines:
        o.append(f'<line x1="{X(xv):.1f}" x2="{X(xv):.1f}" y1="{pad_t}" y2="{H-pad_b}" class="v"/><text x="{X(xv)+3:.1f}" y="{pad_t+10}" class="a">{lab}</text>')
    o.append(f'<text x="{(pad_l+W-pad_r)/2:.0f}" y="{H-6}" class="a" text-anchor="middle">{xlabel}</text><text x="12" y="{(pad_t+H-pad_b)/2:.0f}" class="a" transform="rotate(-90 12 {(pad_t+H-pad_b)/2:.0f})" text-anchor="middle">{ylabel}</text>')
    for i, (lab, s) in enumerate(series):
        d = " ".join(f"{'M' if j == 0 else 'L'}{X(x):.1f},{Y(y):.1f}" for j, (x, y) in enumerate([p for p in s if p[1] is not None]))
        o.append(f'<path d="{d}" class="s{i}" fill="none"/>')
        o.append(f'<text x="{W-pad_r-4}" y="{pad_t+14+14*i}" class="l{i}" text-anchor="end">{lab}</text>')
    if note:
        o.append(f'<text x="{pad_l}" y="{H-pad_b-6}" class="a">{note}</text>')
    o.append("</svg>")
    return "".join(o)


def html(R):
    A, B, C, D = R["sweep_gamma"], R["sweep_horizon"], R["sweep_delta"], R["sweep_beta"]
    charts = [
        svg_lines("Greedy loss vs discount", "discount gamma (0 = pure greed)", "loss, % of optimal",
                  [("26 weeks", list(zip(A["gamma"], A["pct_finite"]))), ("infinite horizon", [(g, p) for g, p in zip(A["gamma"], A["pct_infinite"]) if p is not None])]),
        svg_lines("Greedy loss vs horizon", "weeks planned (log scale)", "loss, % of optimal",
                  [("gamma 0.9", list(zip(B["K"], B["pct_g0.9"]))), ("gamma 1.0", list(zip(B["K"], B["pct_g1.0"])))], xs_log=True),
        svg_lines("Greedy loss vs adaptation strength", "tolerance per level (delta)", "loss, % (gamma .95, 26 wk)", [("loss", list(zip(C["delta"], C["pct"])))]),
        svg_lines("Greedy loss vs commitment payoff", "payoff per honored week (beta)", "loss, % (gamma .9, 26 wk)", [("loss", list(zip(D["beta"], D["pct"])))]),
    ]
    con = R["concert"]["0.95"]
    charts.append(svg_lines("Concert: net carryover by spacing", "a concert every m weeks", "net carryover, total (gamma .95)",
                            [("net carryover", [(r["every"], r["net_carryover"]) for r in con]),
                             ("negative channels only", [(r["every"], r["gain_negative_only"]) for r in con])], xs_log=True))
    def norm(c, i):
        v = [r[i] for r in c]; lo, hi = min(v), max(v)
        return [(r[0], (r[i] - lo) / ((hi - lo) or 1)) for r in c]
    for h in ("20", "90"):
        c = R["gap"][h]["curve"]
        charts.append(svg_lines(f"Gap between meetings, friendship half-life {h} days", "days between meetings", "score, scaled 0 to 1 per line",
                                [("one self (lifetime)", norm(c, 1)), ("old experienced", norm(c, 2)), ("old remembered", norm(c, 3))],
                                vlines=[(R["gap"][h]["best_lifetime"], "best")]))
    rows = "".join(f"<tr><td>{k}</td><td>{v['total']:.1f}</td><td>{v['pct_of_optimal']:.1f}%</td></tr>" for k, v in R["heuristics"]["0.95"].items()) if "0.95" in R["heuristics"] else \
        "".join(f"<tr><td>{k}</td><td>{v['total']:.1f}</td><td>{v['pct_of_optimal']:.1f}%</td></tr>" for k, v in R["heuristics"]["0.9"].items())
    w = R["witness"]["9/10"]["minimal_k_any_reachable_state"] or {}
    css = ("""
:root{--bg:#fff;--fg:#1d1d1f;--mut:#555;--grid:#ddd;--c0:#1f5fbf;--c1:#c25a00;--c2:#2a7d4f;--card:#f6f6f7}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#15161a;--fg:#ececf0;--mut:#a6a6b0;--grid:#33343b;--c0:#7aa8ff;--c1:#ffa45c;--c2:#6fd19b;--card:#1d1e24}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:20px 16px}
h1{font-size:22px}h2{font-size:17px;margin-top:28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.card{background:var(--card);border-radius:8px;padding:8px}svg{width:100%;height:auto}.t{fill:var(--fg);font-size:13px;font-weight:600}.a{fill:var(--mut);font-size:10.5px}
.g{stroke:var(--grid)}.v{stroke:var(--mut);stroke-dasharray:3 3}path{stroke-width:2}.s0{stroke:var(--c0)}.s1{stroke:var(--c1)}.s2{stroke:var(--c2)}
.l0{fill:var(--c0);font-size:11px}.l1{fill:var(--c1);font-size:11px}.l2{fill:var(--c2);font-size:11px}
table{border-collapse:collapse}td,th{padding:3px 10px;border-bottom:1px solid var(--grid);text-align:left}code{font-size:13px}
""")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Horizon: lifetime pleasure</title><style>{css}</style></head><body>
<h1>Lifetime pleasure versus greedy (horizon study)</h1>
<p>A small household decision problem solved exactly ({R['n_states']} reachable states, 7 actions). Every parameter is assumed; see docs/results/horizon.md. Agents feel nothing; pleasure is a gloss for a modeled hedonic state.</p>
<p>With all carried-over state switched off, greedy loses exactly {R['p1_max_abs_loss_off']:.0f} over {R['p1_cells']} grid cells. With it on, greedy loses up to {max(A['pct_finite']):.1f}% of lifetime pleasure at gamma 1 over 26 weeks.</p>
<div class="grid">{''.join(f'<div class="card">{c}</div>' for c in charts)}</div>
<h2>Heuristics against the optimum (gamma 0.9, 26 weeks)</h2><table><tr><th>policy</th><th>total</th><th>% of optimal</th></tr>{rows}</table>
<h2>Machine-checked witness (gamma 9/10)</h2><p>State: {w.get('state_text','')}. k = {w.get('k','')}. Greedy plan <code>{w.get('greedy_plan','')}</code> totals {w.get('greedy_total_float','')}; plan <code>{w.get('best_plan','')}</code> totals {w.get('best_total_float','')}. z3 results: {w.get('z3','')}.</p>
</body></html>"""


if __name__ == "__main__":
    main()
