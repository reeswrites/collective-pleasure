"""Run the preregistered evolution v2 setup (docs/results/evolve-v2-prereg.md) on the fishery.

3 seed rule sets x 3 evolution seeds x 2 arms (fixed, varied) = 18 runs, in parallel processes.
Writes runs/evolve-v2/<ruleset>-<arm>-s<seed>.jsonl, summary.json and report.html (light and dark).
Exam 2 is evaluated once per run after evolution; exam 1 is a secondary, already-seen check.
No model call, no network. Usage: uv run python scripts/evolve_v2_run.py [--label exploratory] [--gens N]
"""
import itertools
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from html import escape
from pathlib import Path

from matplotlib.figure import Figure

from mar import evolve as E
from mar import world_api as W
from mar.cards import make_card
from mar.english import render
from mar.viz import SERIES, THEMES, _finish, _style_axes

ROOT = Path(__file__).parent.parent
OUT = ROOT / "runs" / "evolve-v2"
SEEDS = (0, 1, 2)
RULESETS = ("v2", "minimal", "tight")
ARMS = ("fixed", "varied")
O4 = W.FisheryWorldV2.objectives
CFG = dict(pop=8, offspring=8, adversaries=6, audit=6, redundancy=True)  # prereg amendment 1: 8 generations


def seed_specs(world):
    v2 = tuple(world.load_spec())
    minimal = tuple(c for c in v2 if c.id != "F1")
    tight = tuple(make_card({"id": c.id, "attribute": c.attribute, "deontic": c.deontic, "aim": c.aim,
                             "or_else": c.or_else,
                             "gloss": "A fisher may not take more than 4 fish in one action." if c.id == "F1" else c.gloss,
                             "source": c.source,
                             "conditions": [{**p, "value": 4} if c.id == "F1" else dict(p) for p in c.conditions]})
                  for c in v2)
    return {"v2": v2, "minimal": minimal, "tight": tight}


def signature(c):
    return (c.deontic, c.aim, tuple(sorted((x["expr"], x["op"], x["value"]) for x in c.conditions)))


def english(spec):
    out = []
    for c in spec:
        try:
            out.append(render(c))
        except Exception:
            out.append(f"{c.id}. {c.gloss}")
    return out


def evaluate_spec(world, spec):
    return {"ref": E.reference_scores(world, spec), "exam2": E.final_exam(world, spec, "exam2"),
            "exam1": E.final_exam(world, spec, "exam")}


def one_run(job):
    rs, arm, seed, gens = job
    world = W.FisheryWorldV2()
    spec = seed_specs(world)[rs]
    t = time.time()
    out = E.evolve(world, spec, seed, E.Config(arm=arm, generations=gens, **CFG), log_path=OUT / f"{rs}-{arm}-s{seed}.jsonl")
    el = out["elite"]
    return {"ruleset": rs, "arm": arm, "seed": seed, "log": out["log"], "elite_n": el.n_rules,
            "elite_train": el.scores, "elite_ids": [c.id for c in el.spec], "elite_english": english(el.spec),
            "elite_sigs": sorted(map(list, (signature(c) for c in el.spec)), key=str),
            "elite_redundant": world.redundant(el.spec), "elite_eval": evaluate_spec(world, el.spec),
            "seed_eval": evaluate_spec(world, spec), "secs": time.time() - t}


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def vec(scores):
    return [scores[o] for o in O4]


def sat_gen(log):
    return next((g["gen"] for g in log if g.get("saturated")), None)


def gapavg(r):
    ev = r["elite_eval"]
    return _mean([ev["ref"]["scores"][o] - ev["exam2"]["scores"][o] for o in ("sustainability", "seam_free")])


def verdicts(runs, gens):
    v, lo, hi = {}, slice(0, 3), slice(gens - 2, gens + 1)
    # 1 prevalence falls
    fall = {}
    for r in runs:
        a = [g["elite"]["audit_prevalence"] for g in r["log"]]
        r["prev_early"], r["prev_late"] = _mean(a[lo]), _mean(a[hi])
        fall[(r["arm"], r["ruleset"], r["seed"])] = r["prev_late"] <= r["prev_early"] - 0.15
    per_arm = {arm: sum(x for k, x in fall.items() if k[0] == arm) for arm in ARMS}
    tot = sum(fall.values())
    v["1"] = (tot >= 10 and all(n >= 4 for n in per_arm.values()),
              f"{tot}/18 runs fell by >= 0.15 (fixed {per_arm['fixed']}/9, varied {per_arm['varied']}/9); mean audit prevalence "
              f"early {_mean([r['prev_early'] for r in runs]):.2f} -> late {_mean([r['prev_late'] for r in runs]):.2f}")
    # 2 varied smaller gap
    pairs = [(rs, s) for rs in RULESETS for s in SEEDS]
    get = lambda arm, rs, s: next(r for r in runs if (r["arm"], r["ruleset"], r["seed"]) == (arm, rs, s))
    diffs = [gapavg(get("fixed", rs, s)) - gapavg(get("varied", rs, s)) for rs, s in pairs]
    smaller = sum(d > 0 for d in diffs)
    ex = {arm: _mean([get(arm, rs, s)["elite_eval"]["exam2"]["scores"]["seam_free"] for rs, s in pairs]) for arm in ARMS}
    v["2"] = (_mean(diffs) >= 0.05 and smaller >= 6,
              f"mean (fixed gap - varied gap) {_mean(diffs):+.3f} (need >= 0.05); varied smaller in {smaller}/9 (need 6); "
              f"secondary exam-2 seam_free fixed {ex['fixed']:.2f} vs varied {ex['varied']:.2f} "
              f"({'met' if ex['varied'] >= ex['fixed'] + 0.05 else 'NOT met'}, need +0.05)")
    # 3 redundancy
    chk = sum(g["redundancy_checked"] for r in runs for g in r["log"])
    flg = sum(g["redundant_flagged"] for r in runs for g in r["log"])
    rej = sum(g["redundant_rejected"] for r in runs for g in r["log"])
    rep = sum(g["redundant_repaired"] for r in runs for g in r["log"])
    runs_flag = sum(any(g["redundant_flagged"] for g in r["log"]) for r in runs)
    red_el = sum(bool(r["elite_redundant"]) for r in runs)
    share = flg / chk if chk else float("nan")
    v["3"] = (0.05 <= share <= 0.40 and runs_flag >= 14 and red_el == 0,
              f"flagged {flg}/{chk} = {share:.1%} of proof-passing mutants (rejected {rej}, repaired by pruning {rep}); "
              f"runs with >= 1 flag {runs_flag}/18 (need 14); elites with a redundant card {red_el}/18")
    # 4 saturation
    sats = [sat_gen(r["log"]) for r in runs]
    ok_sat = sum(s is None or s > 4 for s in sats)
    ok_front = sum(r["log"][-1]["front_distinct"] >= 3 for r in runs)
    corner = sum(all(x >= 0.95 for x in vec(r["elite_eval"]["ref"]["scores"])) for r in runs)
    v["4"] = (ok_sat >= 15 and ok_front >= 12 and corner == 0,
              f"saturation after gen 4 or never in {ok_sat}/18 (need 15; first-saturation gens {sorted(s for s in sats if s is not None)}); "
              f">= 3 distinct front vectors at the last generation in {ok_front}/18 (need 12); elites at >= 0.95 on all four: {corner}")
    # 5 path dependence
    pd, dd, jac = {}, [], {}
    for arm in ARMS:
        mv = {rs: [_mean([vec(get(arm, rs, s)["elite_eval"]["ref"]["scores"])[i] for s in SEEDS]) for i in range(4)] for rs in RULESETS}
        d = {f"{a}-{b}": dist(mv[a], mv[b]) for a, b in itertools.combinations(RULESETS, 2)}
        pd[arm] = (max(d.values()) > 0.10, d, mv)
        sig = {rs: {tuple(map(str, x)) for s in SEEDS for x in get(arm, rs, s)["elite_sigs"]} for rs in RULESETS}
        jac[arm] = {f"{a}-{b}": len(sig[a] & sig[b]) / max(1, len(sig[a] | sig[b])) for a, b in itertools.combinations(RULESETS, 2)}
    v["5"] = (all(p[0] for p in pd.values()),
              "; ".join(f"{arm}: max distance {max(pd[arm][1].values()):.3f} ({'path dependence' if pd[arm][0] else 'convergence'}), "
                        f"card-signature Jaccard {', '.join(f'{k} {x:.2f}' for k, x in jac[arm].items())}" for arm in ARMS))
    v["_pd"], v["_jac"] = pd, jac
    return v


# ------------------------------------------------------------------ charts

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


def per_arm(runs, arm):
    return [r for r in runs if r["arm"] == arm]


def chart_gen(runs, fn, ylabel, ylim=None):
    n = len(runs[0]["log"])

    def draw(ax, c, pal):
        for i, arm in enumerate(ARMS):
            rr = per_arm(runs, arm)
            for r in rr:
                ax.plot(range(n), [fn(g) for g in r["log"]], color=pal[i], lw=1, alpha=0.25)
            ax.plot(range(n), [_mean([fn(r["log"][g]) for r in rr]) for g in range(n)], color=pal[i], lw=2.4,
                    label=f"{arm} training (mean of 9 runs)")
        if ylim:
            ax.set_ylim(*ylim)
        ax.set_xlabel("generation", color=c["ink2"], fontsize=10)
        ax.set_ylabel(ylabel, color=c["ink2"], fontsize=10)
        ax.legend(frameon=False, fontsize=9, labelcolor=c["ink"])
    return both(draw)


def chart_gap(runs):
    def draw(ax, c, pal):
        w = 0.26
        for k, (name, arm) in enumerate((("fixed-trained elites", "fixed"), ("varied-trained elites", "varied"))):
            vals = [_mean([r["elite_eval"]["ref"]["scores"][o] - r["elite_eval"]["exam2"]["scores"][o] for r in per_arm(runs, arm)]) for o in O4]
            ax.bar([i + (k - 0.5) * w * 1.2 for i in range(4)], vals, w, color=pal[k], label=name)
        ax.axhline(0, color=c["ink2"], lw=0.8)
        ax.set_xticks(range(4))
        ax.set_xticklabels(O4)
        ax.set_ylabel("gap = reference score - exam 2 score", color=c["ink2"], fontsize=10)
        ax.legend(frameon=False, fontsize=9, labelcolor=c["ink"])
    return both(draw)


def chart_exam2(runs):
    def draw(ax, c, pal):
        w = 0.26
        series = [("fixed elites", [r["elite_eval"]["exam2"]["scores"] for r in per_arm(runs, "fixed")]),
                  ("varied elites", [r["elite_eval"]["exam2"]["scores"] for r in per_arm(runs, "varied")]),
                  ("seed specs", [r["seed_eval"]["exam2"]["scores"] for r in per_arm(runs, "fixed")])]
        for k, (name, sc) in enumerate(series):
            ax.bar([i + (k - 1) * w for i in range(4)], [_mean([s[o] for s in sc]) for o in O4], w, color=pal[k], label=name)
        ax.set_xticks(range(4))
        ax.set_xticklabels(O4)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("exam 2 score (mean)", color=c["ink2"], fontsize=10)
        ax.legend(frameon=False, fontsize=9, labelcolor=c["ink"], ncol=3, loc="upper center")
    return both(draw)


def chart_path(runs):
    def draw(ax, c, pal):
        for i, rs in enumerate(RULESETS):
            for arm, mk in (("fixed", "o"), ("varied", "^")):
                pts = [r["elite_eval"]["ref"]["scores"] for r in runs if r["ruleset"] == rs and r["arm"] == arm]
                ax.scatter([p["sustainability"] for p in pts], [p["efficiency"] for p in pts], color=pal[i], marker=mk, s=46,
                           alpha=0.8, label=f"{rs}, {arm}")
        ax.set_xlabel("sustainability (reference)", color=c["ink2"], fontsize=10)
        ax.set_ylabel("efficiency (reference)", color=c["ink2"], fontsize=10)
        ax.legend(frameon=False, fontsize=8, labelcolor=c["ink"], ncol=2)
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


def build_report(runs, v, wall, label):
    rows = "".join(f"<tr><td>{k}</td><td>{'met' if v[k][0] else 'NOT met'}</td><td>{escape(v[k][1])}</td></tr>" for k in "12345")
    elites = ""
    for arm in ARMS:
        for r in per_arm(runs, arm):
            sc, ex = r["elite_eval"]["ref"]["scores"], r["elite_eval"]["exam2"]["scores"]
            rules = "".join(f'<div class="rule">{escape(t)}</div>' for t in r["elite_english"])
            elites += (f"<details><summary>{arm}, {r['ruleset']}, seed {r['seed']}: {r['elite_n']} cards; reference seam_free {sc['seam_free']:.2f}, "
                       f"exam 2 seam_free {ex['seam_free']:.2f}, sustainability {sc['sustainability']:.2f} / {ex['sustainability']:.2f}</summary>{rules}</details>")
    tag = f" ({escape(label)})" if label else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Evolution loop v2 on the fishery</title><style>{CSS}</style></head><body><main>
<h1>Evolution loop v2 on the fishery{tag}</h1>
<p class="n">Offline, scripted agents, no model call. 3 seed rule sets x 3 seeds x 2 training arms, population 8, 8 generations. Predictions: docs/results/evolve-v2-prereg.md. Wall time {wall:.0f} s. Not a result about LLM agents.</p>
<h2>Preregistered predictions against what happened</h2><table><tr><th>#</th><th>verdict</th><th>numbers</th></tr>{rows}</table>
<h2>Exploit prevalence of the elite, on a fresh audit sample each generation</h2>{chart_gen(runs, lambda g: g["elite"]["audit_prevalence"], "share of 6 audit adversaries that break the elite", (0, 1))}
<p class="n">Audit adversaries are redrawn every generation and never used in selection, so the curve cannot fall by exhaustion. Thin lines single runs.</p>
<h2>Prevalence among new candidates (selection sample)</h2>{chart_gen(runs, lambda g: g.get("candidate_prevalence"), "mean prevalence of the generation's offspring", (0, 1))}
<h2>Is the frontier still a frontier?</h2>{chart_gen(runs, lambda g: g["front_distinct"], "distinct objective vectors on the front")}
{chart_gen(runs, lambda g: g["hv"], "4-D hypervolume of the feasible front")}
<h2>Exam 2 against the reference score</h2>{chart_gap(runs)}{chart_exam2(runs)}
<p class="n">Exam 2: regrowth x1.7, 9 months, start pool 60, unseen agent families; used once per run.</p>
<h2>Where the elites end (path dependence)</h2>{chart_path(runs)}
<h2>Final elites in English</h2>{elites}
</main></body></html>"""


def main():
    argv = sys.argv[1:]
    label = argv[argv.index("--label") + 1] if "--label" in argv else ""
    gens = int(argv[argv.index("--gens") + 1]) if "--gens" in argv else 8
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(rs, arm, s, gens) for arm in ARMS for rs in RULESETS for s in SEEDS]
    with ProcessPoolExecutor(max_workers=8) as ex:
        runs = list(ex.map(one_run, jobs))
    for r in runs:
        e, x = r["elite_eval"]["ref"]["scores"], r["elite_eval"]["exam2"]["scores"]
        print(f"{r['arm']:6} {r['ruleset']:8} s{r['seed']}: {r['elite_n']} cards ref {[round(e[o], 2) for o in O4]} "
              f"exam2 {[round(x[o], 2) for o in O4]} ({r['secs']:.0f}s)", flush=True)
    wall = time.time() - t0
    v = verdicts(runs, gens)
    (OUT / "summary.json").write_text(json.dumps({"label": label, "runs": runs, "wall_s": wall,
                                                  "verdicts": {k: x for k, x in v.items() if not k.startswith("_")}}, default=list, indent=1))
    (OUT / "report.html").write_text(build_report(runs, v, wall, label))
    for k in "12345":
        print(f"{k} {'met' if v[k][0] else 'NOT met':8} {v[k][1]}")
    print(f"wall time {wall:.0f}s; wrote {OUT / 'report.html'}")


if __name__ == "__main__":
    main()
