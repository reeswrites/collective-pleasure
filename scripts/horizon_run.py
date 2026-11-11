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

    # ---- amended 2026-11-10: shared-experience amplification (prereg amendment; mechanism off in everything above)
    R["amp"] = amp_results(people)

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


HS = (10, 20, 45, 90)
OVS = (0.1, 0.3, 0.5, 0.7, 0.9)


def per_occasion(ap, a, ov, x=0.8, g=7):
    m = Hz.share_multiplier(ap, a, x, g, ov)
    mb = 1 + ap.amp_bad * (m - 1)
    good, bad = (1 - a.p_bad) * a.base * (m - 1), -a.p_bad * a.u_bad * (mb - 1)
    return {"mult": m, "gain": good + bad, "good": good, "bad": bad}


def amp_results(people):
    ap = Hz.AmpParams()
    A = {"params": {k: str(v) for k, v in ap.__dict__.items() if k != "activities"},
         "activities": [dict(a.__dict__) for a in ap.activities], "hs": list(HS), "overlaps": list(OVS)}
    A["old_best"] = {str(h): Hz.best_gaps(Hz.GapParams(H=h))["best_lifetime"] for h in HS}
    ctrl = Hz.AmpParams(activities=())
    A["c1_release_only"] = {str(h): Hz.amp_best(Hz.GapParams(H=h), ap=ctrl)["best_gap"] for h in HS}
    A["grid"] = {}
    for h in HS:
        for o in OVS:
            b = Hz.amp_best(Hz.GapParams(H=h), ap=ap, overlap=o)
            ab = b["at_best"]
            A["grid"][f"{h}|{o}"] = {"best_gap": b["best_gap"], "release_share": ab["release_share"], "lifetime": ab["lifetime"],
                                    "base_lifetime": ab["base_lifetime"], "shared": [n for n, v in ab["activities"].items() if v["shared"]],
                                    "closeness_at_meeting": ab["closeness_at_meeting"]}
            f = Hz.amp_best(Hz.GapParams(H=h), ap=Hz.AmpParams(choose=False), overlap=o)
            A["grid"][f"{h}|{o}"]["forced_best_gap"] = f["best_gap"]
            A["grid"][f"{h}|{o}"]["forced_lifetime"] = f["at_best"]["lifetime"]
    A["reset"] = {str(r): Hz.amp_best(Hz.GapParams(H=45, reset=r), ap=ap, overlap=0.7)["best_gap"] for r in (0.3, 0.6, 0.9)}
    A["reset_c1"] = {str(r): Hz.amp_best(Hz.GapParams(H=45, reset=r), ap=ctrl)["best_gap"] for r in (0.3, 0.6, 0.9)}
    A["per_occasion"] = {a.name: {str(o): per_occasion(ap, a, o) for o in (0.1, 0.3, 0.5, 0.7, 0.9)} for a in ap.activities}
    A["break_even_overlap"] = {}
    for a in ap.activities:
        pts = [o / 100 for o in range(0, 101) if per_occasion(ap, a, o / 100)["gain"] > 0]
        A["break_even_overlap"][a.name] = min(pts) if pts else None
    A["a5_movies"] = {"bad_part_amplified": per_occasion(ap, ap.activities[1], 0.7)["bad"],
                      "bad_part_not_amplified": per_occasion(replace(ap, amp_bad=0.0), ap.activities[1], 0.7)["bad"]}
    A["a6_max_diff_off"] = max(abs(Hz.amp_score(Hz.GapParams(H=h), g, ap=Hz.AmpParams(on=False))["lifetime"] - Hz.gap_score(Hz.GapParams(H=h), g)["lifetime"])
                               for h in HS for g in range(1, 201))
    A["curves"] = {}
    for o in (0.1, 0.5, 0.9):
        c = Hz.amp_best(Hz.GapParams(H=45), ap=ap, overlap=o)["curve"]
        A["curves"][str(o)] = [[r["gap"], r["lifetime"]] for r in c]
    return A


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
    rows = "".join(f"<tr><td>{k}</td><td>{v['total']:.1f}</td><td>{v['pct_of_optimal']:.1f}%</td></tr>" for k, v in R["heuristics"]["0.9"].items())
    caps = captions(R)
    css = ("""
:root{--bg:#fff;--fg:#1d1d1f;--mut:#555;--grid:#ddd;--c0:#1f5fbf;--c1:#c25a00;--c2:#2a7d4f;--card:#f6f6f7;--box:#eef3fb;--edge:#1f5fbf}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#15161a;--fg:#ececf0;--mut:#a6a6b0;--grid:#33343b;--c0:#7aa8ff;--c1:#ffa45c;--c2:#6fd19b;--card:#1d1e24;--box:#1a2233;--edge:#7aa8ff}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0 auto;max-width:1100px;padding:20px 16px;overflow-wrap:anywhere}
h1{font-size:22px}h2{font-size:17px;margin-top:28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:12px}
.card{background:var(--card);border-radius:8px;padding:8px;min-width:0}svg{width:100%;height:auto}.t{fill:var(--fg);font-size:13px;font-weight:600}.a{fill:var(--mut);font-size:10.5px}
.g{stroke:var(--grid)}.v{stroke:var(--mut);stroke-dasharray:3 3}path{stroke-width:2}.s0{stroke:var(--c0)}.s1{stroke:var(--c1)}.s2{stroke:var(--c2)}
.l0{fill:var(--c0);font-size:11px}.l1{fill:var(--c1);font-size:11px}.l2{fill:var(--c2);font-size:11px}
table{border-collapse:collapse}td,th{padding:3px 10px;border-bottom:1px solid var(--grid);text-align:left}code{font-size:13px}
.box{background:var(--box);border-left:4px solid var(--edge);border-radius:6px;padding:4px 14px;margin:14px 0}.box h2{margin:10px 0 4px}
.cap{margin:6px 4px 4px;font-size:14px}.cap b{display:block;font-size:13px;color:var(--mut)}.tw{overflow-x:auto}
""")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Horizon: lifetime pleasure</title><style>{css}</style></head><body>
<h1>Lifetime pleasure versus greedy (horizon study)</h1>
{asked(R)}
<p>A small household decision problem solved exactly ({R['n_states']} reachable states, 7 actions). Every parameter is assumed; see docs/results/horizon.md. Agents feel nothing; pleasure is a gloss for a modeled hedonic state.</p>
<p>With all carried-over state switched off, greedy loses exactly {R['p1_max_abs_loss_off']:.0f} over {R['p1_cells']} grid cells. With it on, greedy loses up to {max(A['pct_finite']):.1f}% of lifetime pleasure at gamma 1 over 26 weeks.</p>
<div class="grid">{''.join(f'<div class="card">{c}<div class="cap"><b>What this shows</b>{t}</div></div>' for c, t in zip(charts[:5], caps[:5]))}</div>
{amp_section(R)}
<h2>Before amplification: the friendship gap with rationed reunions only</h2>
<p>These two figures are the earlier worked case, kept as it was. A friend is modeled as missing, then release. It gave best gaps of {R['gap']['10']['best_lifetime']} to {R['gap']['90']['best_lifetime']} days, and the author said that undercounts wanting to hang out with a friend.</p>
<div class="grid">{''.join(f'<div class="card">{c}<div class="cap"><b>What this shows</b>{t}</div></div>' for c, t in zip(charts[5:], caps[5:]))}</div>
<h2>Heuristics against the optimum (gamma 0.9, 26 weeks)</h2><div class="tw"><table><tr><th>policy</th><th>total</th><th>% of optimal</th></tr>{rows}</table></div>
{proof(R)}
{answers(R)}
{surprised(R)}
{trust(R)}
{alignment(R)}
</body></html>"""


def amp_charts(R):
    A = R["amp"]
    g = A["grid"]
    hs, ovs = A["hs"], A["overlaps"]
    charts = [
        svg_lines("Best contact rhythm: before and after amplification", "friendship half-life, days (log)", "best days between contacts (log)",
                  [("before: rationed reunions", [(h, A["old_best"][str(h)]) for h in hs]),
                   ("release layer alone, smaller", [(h, A["c1_release_only"][str(h)]) for h in hs]),
                   ("with sharing (overlap 0.7)", [(h, g[f"{h}|0.7"]["best_gap"]) for h in hs])], xs_log=True),
        svg_lines("Best rhythm against taste overlap", "taste overlap with the friend", "best days between contacts",
                  [(f"half-life {h}", [(o, g[f"{h}|{o}"]["best_gap"]) for o in ovs]) for h in (10, 45, 90)]),
        svg_lines("Best rhythm against closeness level", "how much each meeting closes the gap", "best days between contacts",
                  [("with sharing", [(float(r), v) for r, v in A["reset"].items()]), ("release layer alone", [(float(r), v) for r, v in A["reset_c1"].items()])]),
        svg_lines("What sharing does to one occasion", "taste overlap for that activity", "pleasure gained or lost per occasion",
                  [(n, [(float(o), v["gain"]) for o, v in d.items()]) for n, d in list(A["per_occasion"].items())[:3]] + [("reading or solo hobby", [(float(o), v["gain"]) for o, v in A["per_occasion"]["reading or solo hobby"].items()])]),
        svg_lines("Share of friendship pleasure from the reunion release", "taste overlap", "release share at the best rhythm",
                  [(f"half-life {h}", [(o, g[f"{h}|{o}"]["release_share"]) for o in ovs]) for h in (10, 45, 90)]),
    ]
    c = A["curves"]
    def nrm(v):
        lo, hi = min(y for _, y in v), max(y for _, y in v)
        return [(x, (y - lo) / ((hi - lo) or 1)) for x, y in v if x <= 60]
    charts.append(svg_lines("Contact rhythm curve, half-life 45 days", "days between contacts (first 60)", "score, scaled 0 to 1 per line",
                            [(f"overlap {o}", nrm(c[o])) for o in ("0.1", "0.5", "0.9")]))
    h90 = g["90|0.7"]["best_gap"]
    caps = [
        f"Orange is the old answer: wait {A['old_best']['10']} to {A['old_best']['90']} days. Green is what is left if you only shrink the reunion release without adding sharing, {A['c1_release_only']['10']} to {A['c1_release_only']['90']} days, so part of the shift is just a smaller release. "
        f"Blue adds sharing meals, movies and walks: {g['10|0.7']['best_gap']} to {h90} days, about weekly or more for everyone. The deepest friendship goes from {A['old_best']['90']} days to {h90}.",
        f"More in common with the friend means seeing them more often. At half-life 45 the best gap goes from {g['45|0.1']['best_gap']} days at overlap 0.1 to {g['45|0.9']['best_gap']} days at 0.9. "
        f"At very low overlap nothing is worth sharing, so the rhythm falls back to the reunion layer alone.",
        f"Closeness level is how much each meeting closes the distance. At half-life 45 and overlap 0.7 the best gap goes from {A['reset']['0.3']} days at 0.3 to {A['reset']['0.9']} at 0.9, so closer friends are seen more often. Without sharing (the lower line) the change is {A['reset_c1']['0.3']} to {A['reset_c1']['0.9']}.",
        "Each line is what one shared occasion is worth compared with doing it alone. Meals, movies and walks gain when you have taste in common and lose when you do not. "
        f"A solo hobby is worse shared at every overlap, the thing you do better alone. Break-even overlap: meals {A['break_even_overlap']['meals']}, movies {A['break_even_overlap']['movies']}, walks {A['break_even_overlap']['walks']}.",
        f"The reunion release is still there but it is not most of the friendship. At overlap 0.7 it is {100*g['45|0.7']['release_share']:.0f}% of the pleasure at the best rhythm (half-life 45), {100*g['45|0.9']['release_share']:.0f}% at overlap 0.9. "
        "At overlap 0.1 nothing is shared, so the release is all there is (100%).",
        "Each line scores every contact rhythm up to 60 days, scaled 0 to 1. High overlap peaks early and the curve slopes down quickly after, because sharing needs frequent contact to keep the amplifier up. Low overlap is flat and low.",
    ]
    return charts, caps


def amp_section(R):
    if "amp" not in R:
        return ""
    A = R["amp"]
    ch, cp = amp_charts(R)
    cards = "".join(f'<div class="card">{c}<div class="cap"><b>What this shows</b>{t}</div></div>' for c, t in zip(ch, cp))
    return (f'<h2>After amplification: doing ordinary things together</h2>'
            "<p>The author's correction: a friend is not only someone you miss. If you like eating with others, or watching movies, sharing can amplify the pleasure. "
            "Here the person has ordinary liked activities on their own schedule (meals, movies, walks, a solo hobby). Doing one with the friend multiplies its pleasure by a factor that depends on closeness, on taste overlap for that activity, and on how social the activity is. "
            "Bad occasions are amplified too. The reunion release stays, as a smaller layer. Every number is assumed; see docs/results/horizon-prereg.md (amendment).</p>"
            f'<div class="grid">{cards}</div>')


def _box(title, *paras):
    return f'<div class="box"><h2>{title}</h2>' + "".join(f"<p>{p}</p>" for p in paras) + "</div>"


def asked(R):
    return _box("What this study asked",
                "You said lifetime pleasure is the right measure, and that caring about the whole future should mean you plan instead of grabbing the best thing now. "
                "The question: is grabbing the most pleasure right now ever worse than planning for a whole life? "
                "This study builds a small model and solves it exactly, so the answer is a computation, not a guess.")


def proof(R):
    w = R["witness"]["9/10"]["minimal_k_any_reachable_state"]
    return _box("The proof in plain words",
                "The lemma: grabbing the best thing now is guaranteed to be the best plan only if nothing you do today changes tomorrow. "
                "If a choice leaves any trace that later pleasure can see, some situation exists where greedy loses.",
                f"A computer checked one case. You can have the concert now, or a solo treat now and the concert next week. "
                f"Concert twice in a row totals {w['greedy_total_float']:.2f}. Treat then concert totals {w['best_total_float']:.2f}.",
                "Greedy cannot see this because it looks one step ahead. Waiting a week makes the concert worth more, "
                "and that anticipation pays off later, where greedy never looks. "
                "Discounting the future does not fix it. It only changes how much each later week counts.")


def answers(R):
    con = R["concert"]["0.95"]
    net = {r["every"]: r["net_carryover"] for r in con}
    ms = sorted(net)
    star = next(m for m in ms if net[m] > 0)
    best_m = max(ms, key=lambda m: net[m])
    g = R["gap"]
    hs = sorted(g, key=float)
    gu = R["gap_mismatch_unified"]
    v = R["gap_vividness"]
    sens = R["gap_vividness_sensitivity"]
    return ('<h2>Your questions, answered by this model</h2>'
            + _box("The concert",
                   f"Does a concert steal from future pleasures? It depends on how often you go. Going every week is a net loss of {abs(net[1]):.1f} pleasure units over 26 weeks.",
                   f"Going every 3 to 4 weeks is a net gain, about +{net[3]:.1f} at 3 weeks and +{net[best_m]:.1f} at {best_m}. The boundary is about {star} weeks.",
                   "The costs are real but small. The benefits are anticipation, a vivid memory and a bond. Spaced out, the benefits win.")
            + _box("Seeing someone",
                   f"The best gap between meetings grows with how deep the friendship is: {g[hs[0]]['best_lifetime']} days for a quick-fading bond, {g[hs[-1]]['best_lifetime']} days for a deep one "
                   f"(half-lives of {hs[0]} and {hs[-1]} days).",
                   f"The old remembered-self score says meet every {g[hs[0]]['best_remembered_old']} to {g[hs[-1]]['best_remembered_old']} days. It counts the big reunion and ignores the days apart, so it always wants more meetings.",
                   f"If two friends have different bonds, one gap cannot suit both. At {gu['best_b']} days the faster-fading friend gets {gu['short_loss_pct']:.0f}% less value than at their own best gap ({gu['best_a']} days). That is the slow fade.",
                   f"How much memory counts is the biggest lever. Tripling it moves the best gap for the middle friendship from {sens['default']} to {sens['memory weight x3']} days.")
            + _box("The one-self view",
                   "You said the experiencing self is the remembering self. So each moment counts what you feel now, plus vivid memories you re-live, plus anticipation.",
                   f"A good reunion worth {v['good_reunion_15']['in_moment']:.0f} in the moment is worth {v['good_reunion_15']['after_the_fact']:.1f} once remembered. "
                   f"A betrayal costing {abs(v['bad_betrayal_-20']['in_moment']):.0f} keeps costing, {abs(v['bad_betrayal_-20']['after_the_fact']):.1f} in total. Long mild stretches fade from memory fast.",
                   "The two old scores are special cases of this one. Switch memory off and you get the experienced score. Switch the present off and you get the remembered score."))


def surprised(R):
    h = R["heuristics"]["0.9"]
    return _box("What surprised us",
                f"Simple rules of thumb did worse than greedy. At gamma 0.9, greedy reaches {h['greedy']['pct_of_optimal']:.0f}% of the best total, weekly ritual {h['ritual-weekly']['pct_of_optimal']:.0f}%, rotating every week {h['rotate-1']['pct_of_optimal']:.0f}%. Planning is not the same as rotating.",
                f"A long commitment only pays when the future counts at least about {R['gamma_commitment_accepted']:.3f}. We predicted it would pay at 0.9, and it did not (prediction P4 missed).",
                f"Loss does not always grow with the horizon either. At gamma 0.9 it peaks near {max(R['sweep_horizon']['pct_g0.9']):.0f}% and falls back to {R['sweep_horizon']['pct_g0.9'][R['sweep_horizon']['K'].index(26)]:.1f}% by 26 weeks (prediction P2 missed).")


def trust(R):
    return _box("How much to trust this",
                "This is a toy model. The numbers are assumed, chosen to stand for your ideas, and they are not measured from real people.",
                "It proves the logic and the shape of the answer. It does not give facts about how any real life goes.",
                "The philosophical choices (lifetime as the measure, one self, how memory counts) are stated in ADR 0017, where you can change them.")


def alignment(R):
    A = R["sweep_gamma"]
    return _box("Why it matters for AI alignment",
                "An AI that optimizes the next reply or the next step is a greedy agent. It can drain things its reward does not show, such as trust or the other person's patience. That is reward hacking.",
                f"Here is a small exact case of when that costs and how much: up to {max(A['pct_finite']):.0f}% of lifetime pleasure, and it starts once the future counts at all ({R['critical_gamma']['26']:.2f} and up).")


def captions(R):
    A, B, C, D = R["sweep_gamma"], R["sweep_horizon"], R["sweep_delta"], R["sweep_beta"]
    gi = lambda x: A["gamma"].index(x)
    ki = lambda k: B["K"].index(k)
    con = {r["every"]: r["net_carryover"] for r in R["concert"]["0.95"]}
    best_m = max(con, key=con.get)
    gp = R["gap"]
    out = [
        f"Left means only now counts. Right means the whole future counts as much as now. Greedy loses nothing at the far left, about {A['pct_finite'][gi(0.9)]:.1f}% at 0.9, {A['pct_finite'][gi(0.95)]:.1f}% at 0.95, and {A['pct_finite'][gi(1.0)]:.1f}% over 26 weeks when the future counts fully. "
        f"Greedy first loses at a discount of {R['critical_gamma']['26']:.2f}. The more you care about your whole life, the more planning matters.",
        f"Left is a short plan, right is a long one. At gamma 1 the loss climbs from {B['pct_g1.0'][ki(3)]:.1f}% at 3 weeks to {B['pct_g1.0'][ki(52)]:.1f}% at a year, so longer lives need more planning. "
        f"At gamma 0.9 it peaks at {max(B['pct_g0.9']):.1f}% then falls to {B['pct_g0.9'][ki(26)]:.1f}%, because the best plan settles into the same routine greedy finds. Weeks 1 and 2 show no loss at all.",
        f"Delta is how fast a pleasure wears off with repeats. Loss runs from {C['pct'][0]:.0f}% with no wearing off to {C['pct'][-1]:.0f}% with strong wearing off, and it is not a smooth line. "
        f"Wearing off alone is not the whole story. Turning off every carried-over effect is what drives the loss to zero.",
        f"Beta is the payoff for sticking with a commitment. Up to beta 1.5 loss stays at {D['pct'][0]:.1f}% because the best plan ignores commitments. At beta 2 it jumps to {D['pct'][4]:.1f}% and at beta 3 to {D['pct'][5]:.1f}%. "
        f"Commitment is worth it only past a threshold. A greedy agent never takes it.",
        f"Each point is a concert every m weeks. Weekly is a net loss of {abs(con[1]):.1f}. Every 3 to 4 weeks is a net gain, peaking at +{con[best_m]:.1f} at {best_m} weeks. "
        f"The orange line is the costs alone, always negative. So a concert is worth it when spaced, not when it is constant.",
    ]
    for h in ("20", "90"):
        g = gp[h]
        out.append(f"Each line scores a gap between meetings, scaled to run from 0 to 1. The dashed line marks the best gap for the one-self score, {g['best_lifetime']} days. "
                   f"The old remembered score peaks at {g['best_remembered_old']} days because it ignores the wait. A deeper friendship (half-life {h} days) wants a longer gap, and one gap does not fit two different friends.")
    return out


if __name__ == "__main__":
    if "--report-only" in sys.argv:
        src = Path(sys.argv[sys.argv.index("--report-only") + 1]) if len(sys.argv) > sys.argv.index("--report-only") + 1 else OUT / "results.json"
        R = json.loads(src.read_text())
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "report.html").write_text(html(R))
        print("wrote", OUT / "report.html")
    else:
        main()
