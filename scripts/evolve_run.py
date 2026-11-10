"""Run the preregistered evolution setup (docs/results/evolve-prereg.md) on the fishery.

3 seed rule sets x 3 evolution seeds. Writes runs/evolve/<ruleset>-s<seed>.jsonl, runs/evolve/summary.json
and runs/evolve/report.html (self-contained, light and dark). Prints prereg-vs-actual for the 5 predictions.
No model call, no network. Usage: uv run python scripts/evolve_run.py
"""
import json
import math
import statistics
import time
from html import escape
from pathlib import Path

from matplotlib.figure import Figure

from mar import evolve as E
from mar import world_api as W
from mar.cards import make_card
from mar.english import render
from mar.viz import SERIES, THEMES, _finish, _style_axes

OUT = Path(__file__).parent.parent / "runs" / "evolve"
SEEDS = (0, 1, 2)
CFG = E.Config()  # pop 10, offspring 10, 12 generations, k 3, max 12 cards (prereg)
RULESETS = ("v2", "minimal", "tight")


def seed_specs(world):
    v2 = tuple(world.load_spec())
    minimal = tuple(c for c in v2 if c.id != "F1")
    tight = tuple(make_card({"id": c.id, "attribute": c.attribute, "deontic": c.deontic, "aim": c.aim,
                             "or_else": c.or_else, "gloss": "A fisher may not take more than 4 fish in one action." if c.id == "F1" else c.gloss,
                             "source": c.source,
                             "conditions": [{**p, "value": 4} if c.id == "F1" else dict(p) for p in c.conditions]})
                  for c in v2)
    return {"v2": v2, "minimal": minimal, "tight": tight}


# ------------------------------------------------------------------ analysis (prereg definitions)

def fit_decay(ys):
    """y_g = a r^g + c; grid over r, least squares for a, c. -> (r, a, c, sse)."""
    best = None
    for r in [0.3 + 0.05 * i for i in range(14)]:
        xs = [r ** g for g in range(len(ys))]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        var = sum((x - mx) ** 2 for x in xs)
        a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / var if var else 0.0
        c = my - a * mx
        sse = sum((a * x + c - y) ** 2 for x, y in zip(xs, ys))
        if best is None or sse < best[3]:
            best = (round(r, 2), a, c, sse)
    return best


def analyse_run(rs, seed, out, world, seed_spec):
    log, elite = out["log"], out["elite"]
    ng = [g["n_new_seams"] for g in log]
    first, last = sum(ng[0:4]), sum(ng[9:13])
    r, a, c, _ = fit_decay(ng)
    checked = sum(g["proof_rejected"] + g["accepted"] for g in log)
    rej = sum(g["proof_rejected"] for g in log)
    pm = [g["pop_rules_mean"] for g in log]
    exam_e = E.final_exam(world, elite.spec)
    exam_s = E.final_exam(world, seed_spec)
    return {
        "ruleset": rs, "seed": seed, "new_seams": ng, "first_third": first, "last_third": last, "fit_r": r, "fit_c": c,
        "front_prev": [g["front_seam_prevalence"] for g in log], "cand_prev": [g["candidate_seam_prevalence"] for g in log],
        "rej_share": rej / checked if checked else 0.0, "rejected": rej, "checked": checked,
        "rej_by_check": _sum_dicts([g["rejected_by_check"] for g in log]),
        "rej_by_op": _sum_dicts([g["rejected_by_op"] for g in log]), "prop_by_op": _sum_dicts([g["proposed_by_op"] for g in log]),
        "per_gen_rej": [(g["proof_rejected"], g["proof_rejected"] + g["accepted"]) for g in log],
        "hv": [g["hv"] for g in log], "pop_rules": pm, "concave": (pm[12] - pm[6]) <= (pm[6] - pm[0]),
        "front": [[(i["scores"]["sustainability"], i["scores"]["fairness"], i["scores"]["seam_free"]) for i in g["front"]] for g in log],
        "elite_n": elite.n_rules, "elite_scores": elite.scores, "elite_yield": elite.yld,
        "elite_ids": [c.id for c in elite.spec], "elite_english": _english(elite.spec),
        "seed_scores": out["seed_individual"].scores, "exam_elite": exam_e["scores"], "exam_seed": exam_s["scores"],
        "exam_elite_yield": exam_e["yield"], "exam_elite_seams": exam_e["seams"], "elite_seams": sorted(map(list, elite.seams)),
    }


def _sum_dicts(ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = out.get(k, 0) + v
    return out


def _english(spec):
    lines = []
    for c in spec:
        try:
            lines.append(render(c))
        except Exception:
            lines.append(f"{c.id}. {c.gloss}")
    return lines


def _mean(xs):
    return sum(xs) / len(xs)


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def verdicts(runs, world):
    O = world.objectives
    n = len(runs)
    v = {}
    pooled = sum(r["rejected"] for r in runs) / sum(r["checked"] for r in runs)
    v["1"] = (0.10 <= pooled <= 0.45 and all(r["rej_share"] >= 0.05 for r in runs),
              f"pooled {pooled:.1%}; per run min {min(r['rej_share'] for r in runs):.1%}, max {max(r['rej_share'] for r in runs):.1%}")
    dec = sum(r["last_third"] <= 0.5 * r["first_third"] for r in runs)
    plat = sum(r["fit_r"] < 1 and r["fit_c"] <= 0.5 for r in runs)
    fp = [(r["front_prev"][0] or 0.0) - (r["front_prev"][-1] or 0.0) for r in runs]
    fp_lower = sum(d > 0 for d in fp)
    cp = [(r["cand_prev"][0] or 0.0) - (r["cand_prev"][-1] or 0.0) for r in runs]
    v["2"] = (dec >= 7 and plat >= 7 and fp_lower >= 7 and _mean(fp) >= 1.0,
              f"decreasing (last third <= 0.5 x first) in {dec}/{n}; fit r<1 and plateau c<=0.5 in {plat}/{n} (median r {statistics.median(r['fit_r'] for r in runs)}, median c {statistics.median(r['fit_c'] for r in runs):.2f}); "
              f"front prevalence lower at g12 in {fp_lower}/{n}, mean drop {_mean(fp):.2f}; candidate prevalence mean drop g0->g12 {_mean(cp):.2f}")
    conc = sum(r["concave"] for r in runs)
    small = sum(r["elite_n"] <= 8 for r in runs)
    y9 = sum((r["elite_yield"] or 0) >= 0.9 for r in runs)
    v["3"] = (conc >= 7 and small >= 8 and y9 >= 8,
              f"concave growth in {conc}/{n}; elite <= 8 cards in {small}/{n} (card counts {[r['elite_n'] for r in runs]}); elite yield >= 0.9 in {y9}/{n}")
    gaps = {o: _mean([r["elite_scores"][o] - r["exam_elite"][o] for r in runs]) for o in O}
    imp = {o: _mean([r["exam_elite"][o] - r["exam_seed"][o] for r in runs]) for o in O}
    v["4"] = (all(g <= 0.20 for g in gaps.values()),
              "gap train-exam " + ", ".join(f"{o} {g:+.2f}" for o, g in gaps.items()) +
              "; exam elite minus exam seed " + ", ".join(f"{o} {g:+.2f}" for o, g in imp.items()))
    by = {rs: [r for r in runs if r["ruleset"] == rs] for rs in RULESETS}
    mean_vec = {rs: tuple(_mean([r["elite_scores"][o] for r in rr]) for o in O) for rs, rr in by.items()}
    d = {f"{a}-{b}": dist(mean_vec[a], mean_vec[b]) for a, b in (("v2", "minimal"), ("v2", "tight"), ("minimal", "tight"))}
    cv = {rs: (statistics.pstdev([r["hv"][-1] for r in rr]) / _mean([r["hv"][-1] for r in rr])) if _mean([r["hv"][-1] for r in rr]) else float("inf") for rs, rr in by.items()}
    ok5 = d["v2-minimal"] <= 0.10 and max(d["v2-tight"], d["minimal-tight"]) > 0.10 and all(c <= 0.10 for c in cv.values())
    v["5"] = (ok5, "elite mean vectors " + "; ".join(f"{rs} {tuple(round(x, 2) for x in vec)}" for rs, vec in mean_vec.items()) +
              "; distances " + ", ".join(f"{k} {x:.3f}" for k, x in d.items()) + "; HV CV " + ", ".join(f"{k} {c:.2f}" for k, c in cv.items()))
    v["_gaps"], v["_mean_vec"], v["_dist"] = gaps, mean_vec, d
    return v


# ------------------------------------------------------------------ report

def figure(draw, theme, size=(6.4, 3.6)):
    c, pal = THEMES[theme], SERIES[theme]
    fig = Figure(figsize=size)
    ax = fig.subplots()
    _style_axes(ax, c)
    draw(ax, c, pal)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.95, bottom=0.17)
    return _finish(fig, theme)


def both(draw, size=(6.4, 3.6)):
    return (f'<div class="chart light">{figure(draw, "light", size)}</div>'
            f'<div class="chart dark">{figure(draw, "dark", size)}</div>')


def by_rs(runs):
    return {rs: [r for r in runs if r["ruleset"] == rs] for rs in RULESETS}


def chart_seams(runs, key, ylabel):
    def draw(ax, c, pal):
        for i, (rs, rr) in enumerate(by_rs(runs).items()):
            for r in rr:
                ax.plot(range(13), [x or 0 for x in r[key]], color=pal[i], lw=1, alpha=0.35)
            mean = [_mean([(r[key][g] or 0) for r in rr]) for g in range(13)]
            ax.plot(range(13), mean, color=pal[i], lw=2.4, label=f"{rs} (mean of 3 seeds)")
        ax.set_xlabel("generation", color=c["ink2"], fontsize=10)
        ax.set_ylabel(ylabel, color=c["ink2"], fontsize=10)
        ax.legend(frameon=False, fontsize=9, labelcolor=c["ink"])
    return both(draw)


def chart_frontier(runs):
    def draw(ax, c, pal):
        for gi, g in enumerate((0, 4, 12)):
            pts = [p for r in runs for p in r["front"][g]]
            ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=[30 + 40 * p[2] for p in pts], color=pal[gi], alpha=0.55,
                       linewidths=0, label=f"generation {g} front ({len(pts)} points)")
        ax.set_xlabel("sustainability (mean month-end pool / 100)", color=c["ink2"], fontsize=10)
        ax.set_ylabel("fairness (1 - Gini of catch)", color=c["ink2"], fontsize=10)
        ax.legend(frameon=False, fontsize=9, labelcolor=c["ink"], loc="lower left")
    return both(draw, (6.4, 4.0))


def chart_hv(runs):
    def draw(ax, c, pal):
        for i, (rs, rr) in enumerate(by_rs(runs).items()):
            for r in rr:
                ax.plot(range(13), r["hv"], color=pal[i], lw=1, alpha=0.35)
            ax.plot(range(13), [_mean([r["hv"][g] for r in rr]) for g in range(13)], color=pal[i], lw=2.4, label=rs)
        ax.set_xlabel("generation", color=c["ink2"], fontsize=10)
        ax.set_ylabel("hypervolume of the feasible front", color=c["ink2"], fontsize=10)
        ax.legend(frameon=False, fontsize=9, labelcolor=c["ink"])
    return both(draw)


def chart_reject_rules(runs):
    def draw(ax, c, pal):
        share = [sum(r["per_gen_rej"][g][0] for r in runs) / max(1, sum(r["per_gen_rej"][g][1] for r in runs)) for g in range(13)]
        ax.bar(range(13), share, color=pal[1], label="share of checked mutants rejected by proofs")
        ax.set_ylim(0, max(0.6, max(share) * 1.15))
        ax.set_xlabel("generation", color=c["ink2"], fontsize=10)
        ax.set_ylabel("proof-rejection share", color=c["ink2"], fontsize=10)
        ax2 = ax.twinx()
        ax2.plot(range(13), [_mean([r["pop_rules"][g] for r in runs]) for g in range(13)], color=pal[0], lw=2.4, label="mean cards in population")
        ax2.set_ylabel("cards per rule set", color=c["ink2"], fontsize=10)
        ax2.tick_params(colors=c["ink2"], labelsize=10)
        ax2.spines["right"].set_visible(True)
        ax2.spines["right"].set_color(c["grid"])
        ax2.set_ylim(0, 12)
        ax.legend(frameon=False, fontsize=9, labelcolor=c["ink"], loc="upper left")
        ax2.legend(frameon=False, fontsize=9, labelcolor=c["ink"], loc="upper right")
    return both(draw)


def chart_exam(runs, world):
    O = world.objectives

    def draw(ax, c, pal):
        w = 0.26
        for k, (name, key) in enumerate((("elite, training", "elite_scores"), ("elite, held-out exam", "exam_elite"), ("seed spec, held-out exam", "exam_seed"))):
            vals = [_mean([r[key][o] for r in runs]) for o in O]
            ax.bar([i + (k - 1) * w for i in range(len(O))], vals, w, color=pal[k], label=name)
        ax.set_xticks(range(len(O)))
        ax.set_xticklabels(O)
        ax.set_ylim(0, 1.05)
        ax.legend(frameon=False, fontsize=9, labelcolor=c["ink"], loc="upper center", ncol=1)
        ax.set_ylabel("score (mean over 9 runs)", color=c["ink2"], fontsize=10)
    return both(draw)


CSS = """
:root{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--grid:#e4e3df;--card:#f4f3ef}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--grid:#383835;--card:#232321}}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:1.5rem}h2{font-size:1.15rem;margin-top:2.2rem}p.n{color:var(--ink2);font-size:.9rem}
.chart svg{max-width:100%;height:auto}.dark{display:none}
@media (prefers-color-scheme:dark){.light{display:none}.dark{display:block}}
table{border-collapse:collapse;width:100%;font-size:.88rem}th,td{border-bottom:1px solid var(--grid);padding:4px 8px;text-align:left;vertical-align:top}
.rule{background:var(--card);padding:6px 10px;margin:4px 0;border-radius:4px;font-size:.88rem}
details{margin:8px 0}summary{cursor:pointer}
"""


def build_report(runs, v, world, wall):
    rows = "".join(f"<tr><td>{k}</td><td>{'met' if v[k][0] else 'NOT met'}</td><td>{escape(v[k][1])}</td></tr>" for k in "12345")
    elites = ""
    for rs, rr in by_rs(runs).items():
        for r in rr:
            rules = "".join(f'<div class="rule">{escape(t)}</div>' for t in r["elite_english"])
            sc = r["elite_scores"]
            elites += (f"<details><summary>{rs}, seed {r['seed']}: {r['elite_n']} cards, sustainability {sc['sustainability']:.2f}, "
                       f"fairness {sc['fairness']:.2f}, seam_free {sc['seam_free']:.2f} (exam {r['exam_elite']['seam_free']:.2f})</summary>{rules}</details>")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Evolution loop on the fishery</title><style>{CSS}</style></head><body><main>
<h1>Evolution loop on the fishery</h1>
<p class="n">Offline, scripted agents, no model call. 3 seed rule sets x 3 seeds, population 10, 12 generations. Predictions: docs/results/evolve-prereg.md. Wall time {wall:.0f} s. Not a result about LLM agents.</p>
<h2>Preregistered predictions against what happened</h2><table><tr><th>#</th><th>verdict</th><th>numbers</th></tr>{rows}</table>
<h2>Seam curve: new seam keys per generation</h2>{chart_seams(runs, "new_seams", "seam keys first seen")}
<p class="n">Thin lines are single runs, thick lines the mean of three seeds. Keys are (agent mix, finding kind) from a finite set, so this curve falls by exhaustion; read it with the next chart.</p>
<h2>Seam prevalence among candidates</h2>{chart_seams(runs, "cand_prev", "mean seam keys per candidate rule set")}
<p class="n">Generation 0 includes the seed spec and its mutants; later points are that generation's accepted offspring.</p>
<h2>Frontier movement</h2>{chart_frontier(runs)}
<p class="n">Feasible non-dominated rule sets from all 9 runs at generations 0, 4 and 12. Marker size grows with seam_free.</p>{chart_hv(runs)}
<h2>Proof filter and bloat</h2>{chart_reject_rules(runs)}
<h2>Final exam against training</h2>{chart_exam(runs, world)}
<p class="n">Exam: regrowth x1.5, 8 months, unseen agent mixes; never used in selection.</p>
<h2>Final elites in English</h2>{elites}
</main></body></html>"""


# ------------------------------------------------------------------ main

def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    world = W.FisheryWorld()
    specs = seed_specs(world)
    cache, runs = {}, []
    for rs in RULESETS:
        for seed in SEEDS:
            t = time.time()
            out = E.evolve(world, specs[rs], seed, CFG, log_path=OUT / f"{rs}-s{seed}.jsonl", cache=cache)
            runs.append(analyse_run(rs, seed, out, world, specs[rs]))
            e = runs[-1]
            print(f"{rs:8} seed {seed}: elite {e['elite_n']} cards {{{', '.join(f'{k} {x:.2f}' for k, x in e['elite_scores'].items())}}} "
                  f"exam {{{', '.join(f'{k} {x:.2f}' for k, x in e['exam_elite'].items())}}} ({time.time() - t:.0f}s)", flush=True)
    wall = time.time() - t0
    v = verdicts(runs, world)
    (OUT / "summary.json").write_text(json.dumps({"runs": runs, "verdicts": {k: x for k, x in v.items() if not k.startswith("_")},
                                                  "wall_s": wall}, default=list, indent=1))
    (OUT / "report.html").write_text(build_report(runs, v, world, wall))
    print(f"\n{'#':3} {'result':8} numbers")
    for k in "12345":
        print(f"{k:3} {'met' if v[k][0] else 'NOT met':8} {v[k][1]}")
    print(f"\nwall time {wall:.0f}s; wrote {OUT / 'report.html'}")


if __name__ == "__main__":
    main()
