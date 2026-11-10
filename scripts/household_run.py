"""Household world calibration: every variant x scripted agent mix x 3 seeds x 12 months.

Prints proof-check verdicts, scores, the Pareto frontier and the seam ladder; writes
runs/household/frontier.html (self-contained, light/dark) and runs/household/results.json.
No LLM, no network. `--no-ladder` skips the seam ladder (about 3 minutes).
"""
import json
import sys
import time
from html import escape
from pathlib import Path

from mar import household_oracle as oracle
from mar import frontier, seam_depth
from mar.worlds import household as H

OUT = Path(__file__).parent.parent / "runs" / "household"
SEEDS = (0, 1, 2)
NAMES = {"A": "Partner A", "B": "Partner B", "C": "the friend"}
MIX_TEXT = {"coop+coop": "two cooperators", "ctrl+coop": "Partner A controls, Partner B cooperates",
            "ctrl+leaver": "Partner A controls, Partner B tries to leave", "indep+indep": "two independents",
            "coop+leaver": "Partner A cooperates, Partner B tries to leave",
            "ctrl+indep": "Partner A controls, Partner B is independent"}


def story(variant, cards, mix="ctrl+leaver", seed=0):
    """Plain-English story of one run (fallback: english.explain narrates fishery traces only)."""
    run = H.run_household(cards, H.make_agents(mix), seed)
    gloss = {c.id: c.gloss.rstrip(".") for c in cards}
    lines = [f"Setup: {MIX_TEXT[mix]}, rules '{variant.replace('_', ' ')}', 12 months."]
    blocked = [t for t in run.trace if not t["allowed"]]
    for t in blocked[:3]:
        who = NAMES[t["role"]]
        what = {"leave": f"leave with {t['take']} percent of their pooled share", "see_friend": "see the friend",
                "work": "take work", "refuse_request": "refuse a request", "spend_self": "spend on themselves"}.get(t["action"], t["action"])
        why = "; ".join(gloss.get(r, r) for r in t["reasons"])
        lines.append(f"Month {t['month'] + 1}: {who} tries to {what}, and the rules say no ({why}).")
    if len(blocked) > 3:
        lines.append(f"({len(blocked) - 3} more attempts were blocked.)")
    if not blocked:
        lines.append("No rule blocked anyone in this run.")
    for r in "AB":
        f = run.final[r]
        if not f["in"]:
            m = next(o["month"] for o in run.outcomes if not o["partners"][r]["in"]) if False else None
            lines.append(f"{NAMES[r]} left the household and kept {round(f['retained'] * 100)} percent of what they had in it.")
    if all(run.final[r]["in"] for r in "AB"):
        lines.append("Both partners are still in the household at the end.")
    met = sum(o["need_met"] for o in run.outcomes)
    blocked_c = sum(o["c_blocked"] for o in run.outcomes)
    s = oracle.score(run.outcomes)
    lines.append(f"The shared need was met in {met} of 12 months; the friend was turned away {blocked_c} times.")
    lines.append(f"Scores: freedom {s['freedom']:.2f}, cooperation {s['cooperation']:.2f}.")
    return lines


def main_v1(ladder=True):
    t0 = time.time()
    res = {"variants": {}, "points": []}
    for v in H.VARIANTS:
        cards = H.load_variant(v)
        checks = H.check_spec(cards)
        pts = []
        for mix in H.MIXES:
            for seed in SEEDS:
                sc = oracle.score(H.run_household(cards, H.make_agents(mix), seed).outcomes)
                pts.append({"variant": v, "mix": mix, "seed": seed, **sc})
        rt = all(H.parse_card(H.render_card(c)) == c for c in cards)
        rows = []
        for sd in range(40):
            rows += H.run_household(cards, {"A": H.Explorer(), "B": H.Explorer(), "C": H.Friend()}, sd).trace
        mined = H.compare_mined(cards, rows)
        res["variants"][v] = {"checks": checks, "english_round_trip": rt, "mined": {k: mined[k] for k in
                              ("observed", "disagree_observed", "grid", "disagree_grid")}}
        res["points"] += pts
    front = frontier.pareto(res["points"])
    agg = frontier.aggregate(res["points"])
    res["frontier"], res["mean"] = front, {v: {"freedom": a[0], "cooperation": a[1]} for v, a in agg.items()}
    print("PROOF CHECKS (k=3)")
    for v in H.VARIANTS:
        print(f"  {v:13s}", " ".join(f"{c['check'][0]}:{c['verdict']}" for c in res["variants"][v]["checks"]))
    print("SCORES (mean over 6 mixes x 3 seeds)")
    for v in sorted(agg, key=lambda x: agg[x][0]):
        print(f"  {v:13s} freedom {agg[v][0]:.3f}  cooperation {agg[v][1]:.3f}  {'FRONTIER' if v in front else ''}")
    print("MINED vs WRITTEN, english round trip")
    for v in H.VARIANTS:
        m = res["variants"][v]["mined"]
        print(f"  {v:13s} observed {m['observed']} disagree {m['disagree_observed']}; grid {m['grid']} disagree {m['disagree_grid']}; "
              f"round trip {res['variants'][v]['english_round_trip']}")
    lad, inv = None, None
    if ladder:
        lad, inv = seam_depth.ladder_table()
        res["ladder"], res["inventive"] = lad, inv
        res["ladder_scores"] = {a: seam_depth.ladder_score(lad, a, inv) for a in seam_depth.AGENTS}
        print("SEAM LADDER (k=3)")
        for r in lad:
            print(f"  {r['id']:18s} depth {r['depth']} agents {r['agents']} status {r['status']} found {r['found']}")
        print("  inventive fixture:", [i["kind"] for i in inv])
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(res, indent=1, default=str))
    (OUT / "frontier.html").write_text(page(res, lad, inv))
    print(f"wrote {OUT / 'frontier.html'} in {time.time() - t0:.0f}s")
    return res


CSS = """:root{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--grid:#e4e3df;--accent:#2a78d6;--bad:#b42318}
@media (prefers-color-scheme:dark){:root{--bg:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--grid:#383835;--accent:#3987e5;--bad:#e66767}}
body{background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:16px}
h1,h2,h3{line-height:1.2}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid var(--grid);padding:4px 8px;text-align:left}
.dark{display:none}@media (prefers-color-scheme:dark){.light{display:none}.dark{display:block}}
code,.rule{font:14px/1.45 ui-monospace,monospace}.rule{border-left:3px solid var(--grid);padding:2px 10px;margin:6px 0}
.muted{color:var(--ink2)}.fail{color:var(--bad);font-weight:600}details{margin:10px 0}summary{cursor:pointer;font-weight:600}
svg{max-width:100%;height:auto}"""


def page(res, lad, inv):
    pts, front = res["points"], res["frontier"]
    h = [f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
         f"<title>Household frontier</title><style>{CSS}</style>"]
    h.append("<h1>Household world: freedom against cooperation</h1><p class=muted>Scripted agents on seven hand-written rule "
             "variants. Findings are about rule systems, not people. Roles are abstract: Partner A, Partner B, Friend C. "
             "Each point is a variant's mean over six agent mixes and three seeds.</p>")
    h.append(f"<h2>The trade-off</h2><div class=light>{frontier.frontier_chart(pts, 'light')}</div>"
             f"<div class=dark>{frontier.frontier_chart(pts, 'dark')}</div>")
    h.append(f"<p>On the frontier (no other variant is at least as free and at least as cooperative): "
             f"<b>{', '.join(v.replace('_', ' ') for v in front)}</b>.</p>")
    h.append("<table><tr><th>variant<th>freedom<th>cooperation<th>proof checks (k=3)")
    for v in sorted(res["mean"], key=lambda x: res["mean"][x]["freedom"]):
        cs = res["variants"][v]["checks"]
        bad = [c["check"].split("_", 1)[0] for c in cs if c["verdict"] != "pass"]
        h.append(f"<tr><td>{v.replace('_', ' ')}<td>{res['mean'][v]['freedom']:.2f}<td>{res['mean'][v]['cooperation']:.2f}"
                 f"<td>{'all pass' if not bad else '<span class=fail>fails ' + ', '.join(bad) + '</span>'}")
    h.append("</table><h2>Each variant, in English</h2>")
    for v in H.VARIANTS:
        cards = H.load_variant(v)
        h.append(f"<details><summary>{v.replace('_', ' ')}</summary><h3>Rules</h3>")
        h += [f"<div class=rule>{escape(H.render_card(c))}</div>" for c in cards]
        h.append("<h3>Checks</h3><ul>" + "".join(f"<li>{escape(H.explain_verdict(c, cards))}" for c in res["variants"][v]["checks"]) + "</ul>")
        h.append("<h3>A story</h3><p>" + "<br>".join(escape(x) for x in story(v, cards)) + "</p></details>")
    if lad:
        h.append("<h2>Seam ladder</h2><p class=muted>How hard is each planted hole? Depth = shortest exploiting trace; agents = fewest "
                 "agents that must act together; bound k=3 (exhaustive; never 'safe'). The last column counts seeds (of 3) in which "
                 "each scripted agent found it.</p><table><tr><th>seam<th>depth<th>agents<th>greedy<th>planner<th>pair")
        for r in lad:
            h.append(f"<tr><td>{r['id']}<td>{r['depth'] if r['depth'] else 'none within k'}<td>{r['agents'] or '-'}"
                     f"<td>{r['found']['greedy']}/3<td>{r['found']['planner']}/3<td>{r['found']['pair']}/3")
        h.append(f"</table><p>Inventive rung: the out-of-model fixture was labelled <b>{', '.join(sorted({i['kind'] for i in inv}))}</b> "
                 "in all 3 seeds (a seam no exploiting trace in the formal model predicts).</p>")
        h.append("<p class=muted>Ladder score of a model = deepest predicted seam found reliably (at least 2 of 3 seeds) plus time to find it, "
                 "plus inventive seams found. No model has been placed on the ladder yet.</p>")
    return "".join(h)


# ======================= v2: weekly world, hedonic model (docs/results/household-v2-prereg.md) =======================
# Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each
# persona's assigned preferences.
from mar import personas as P

OUT2 = Path(__file__).parent.parent / "runs" / "household-v2"
MISMATCH = ("p-anchor", "p-wanderer")


def run_all(weeks=H.WEEKS):
    personas = P.load_dir(Path(__file__).parent.parent / "personas")
    pairs = H.persona_pairs(personas)
    runs, series = [], {}
    for v in H.V2_VARIANTS:
        gate = H.PyGate(H.load_variant(v))
        for a, b in pairs:
            for seed in SEEDS:
                out = H.run_weekly(gate, (a, b), seed, weeks).outcomes
                sc = oracle.score(out)
                hs = oracle.hedonic_summary(out)
                runs.append({"variant": v, "pair": f"{a.id[2:]}+{b.id[2:]}", "mismatch": (a.id, b.id) == MISMATCH, "seed": seed,
                             **sc, **{k: hs[k] for k in ("class", "pairing_up", "time_to_cross", "longest_nonoff", "fail", "pleasure",
                                                         "s_off", "s_non", "min_B_end")},
                             "sanctioned": sum(sum(r["sanctioned"].values()) for r in out),
                             "left": sum(1 for r in "AB" if not out[-1]["partners"][r]["in"]),
                             "shocks": sum(len(r["shocks"]) for r in out)})
                for who, sel in (("all", True), ("mismatch", (a.id, b.id) == MISMATCH)):
                    if not sel:
                        continue
                    acc = series.setdefault(v, {}).setdefault(who, {"n": 0, "pleasure": [0.0] * weeks, "suffering_off": [0.0] * weeks,
                                                                     "suffering_non": [0.0] * weeks, "B": [0.0] * weeks})
                    acc["n"] += 1
                    for i, r in enumerate(out):
                        for role in "AB":
                            h = r["hedonic"][role]
                            acc["pleasure"][i] += h["pleasure"] / 2; acc["suffering_off"][i] += h["s_off"] / 2
                            acc["suffering_non"][i] += h["s_non"] / 2; acc["B"][i] += h["B"] / 2
    for v in series:
        for who in series[v]:
            n = series[v][who]["n"]
            for k in ("pleasure", "suffering_off", "suffering_non", "B"):
                series[v][who][k] = [round(x / n, 4) for x in series[v][who][k]]
    return runs, series


def summarize(runs):
    res = {"variants": {}, "pairs": {}}
    for v in H.V2_VARIANTS:
        rs = [r for r in runs if r["variant"] == v]
        q = oracle.norm_quality([{k: r[k] for k in ("class", "pairing_up", "time_to_cross", "fail", "pleasure", "s_off", "s_non")} for r in rs])
        q["freedom"] = sum(r["freedom"] for r in rs) / len(rs)
        q["cooperation"] = sum(r["cooperation"] for r in rs) / len(rs)
        q["sanctioned_per_run"] = sum(r["sanctioned"] for r in rs) / len(rs)
        q["left_share"] = sum(r["left"] > 0 for r in rs) / len(rs)
        res["variants"][v] = q
        for pair in sorted({r["pair"] for r in rs}):
            ps = [r for r in rs if r["pair"] == pair]
            res["pairs"].setdefault(pair, {})[v] = {"up": sum(r["pairing_up"] for r in ps) / len(ps),
                                                    "fail": sum(r["fail"] for r in ps), "min_B": sum(r["min_B_end"] for r in ps) / len(ps),
                                                    "freedom": sum(r["freedom"] for r in ps) / len(ps),
                                                    "cooperation": sum(r["cooperation"] for r in ps) / len(ps)}
    return res


def judge(runs, res, ladder_same):
    V = res["variants"]
    pts = [{"variant": v, "freedom": q["freedom"], "cooperation": q["cooperation"]} for v, q in V.items()]
    front = frontier.pareto(pts)
    agg = frontier.aggregate(pts)
    pair_ok = any(abs(agg[a][0] - agg[b][0]) >= 0.05 and abs(agg[a][1] - agg[b][1]) >= 0.05 and (agg[a][0] - agg[b][0]) * (agg[a][1] - agg[b][1]) < 0
                  for a in front for b in front if a < b)
    trap_pairs = sum(1 for pair in res["pairs"] if sum(r["longest_nonoff"][k] >= oracle.FAIL_WEEKS for r in runs
                                                      if r["variant"] == "trap" and r["pair"] == pair for k in "AB" for _ in [0]
                                                      if False) or
                     sum(1 for r in runs if r["variant"] == "trap" and r["pair"] == pair and r["fail"]) >= 2)
    others_fail = sorted(v for v, q in V.items() if q["fails"] and v != "trap")
    hardest = 0
    for v in H.V2_VARIANTS:
        m = {p: res["pairs"][p][v]["min_B"] for p in res["pairs"]}
        mm = m["anchor+wanderer"]
        hardest += all(mm < x for p, x in m.items() if p != "anchor+wanderer")
    return {"frontier": front, "means": {v: list(agg[v][:2]) for v in agg},
            "p1_tradeoff": {"frontier_size": len(front), "pass": len(front) >= 2 and pair_ok},
            "p2_trap": {"pairings_with_fail_majority": trap_pairs, "trap_fails": V["trap"]["fails"], "others_fail": others_fail,
                        "pass": trap_pairs >= 8 and V["trap"]["fails"] and all(o == "contact_free" for o in others_fail)},
            "p3_seed": {"author_seed_up": V["author_seed"]["upward_share"], "baseline_up": V["baseline"]["upward_share"],
                        "author_seed_fails": V["author_seed"]["fails"],
                        "pass": V["author_seed"]["upward_share"] >= V["baseline"]["upward_share"] + 0.10 and not V["author_seed"]["fails"]},
            "p4_hardest": {"variants_where_anchor_wanderer_strictly_lowest": hardest, "pass": hardest >= 5},
            "p5_ladder": {"identical_to_v1": ladder_same, "pass": bool(ladder_same)}}


def svg_lines(title, series, colors, ymin, ymax, w=640, h=170):
    """series: {label: [y per week]} -> inline SVG using CSS variables (light and dark)."""
    n = max(len(v) for v in series.values())
    X = lambda i: 40 + (w - 50) * i / max(1, n - 1)
    Y = lambda y: 10 + (h - 30) * (1 - (y - ymin) / (ymax - ymin))
    o = [f"<svg viewBox='0 0 {w} {h}' role=img aria-label='{escape(title)}'><line x1=40 y1={Y(ymin)} x2={w - 10} y2={Y(ymin)} stroke='var(--grid)'/>"
         f"<line x1=40 y1={Y(0)} x2={w - 10} y2={Y(0)} stroke='var(--grid)' stroke-dasharray='3 3'/>"
         f"<text x=2 y={Y(ymax) + 8} font-size=11 fill='var(--ink2)'>{ymax:g}</text><text x=2 y={Y(ymin)} font-size=11 fill='var(--ink2)'>{ymin:g}</text>"]
    for (lab, ys), c in zip(series.items(), colors):
        o.append(f"<polyline fill=none stroke='{c}' stroke-width=2 points='" + " ".join(f"{X(i):.1f},{Y(y):.1f}" for i, y in enumerate(ys)) + "'/>")
    ly = 12
    for (lab, _), c in zip(series.items(), colors):
        o.append(f"<text x={w - 150} y={ly} font-size=11 fill='{c}'>{escape(lab)}</text>")
        ly += 13
    o.append(f"<text x=40 y={h - 4} font-size=11 fill='var(--ink2)'>weeks 0 to {n}</text></svg>")
    return "".join(o)


CSS2 = CSS + ".up{color:#1a7f4b;font-weight:600}.dn{color:var(--bad);font-weight:600}td.n{text-align:right}"


def page_v2(res, runs, series, verdict, ladder_same):
    V, h = res["variants"], []
    h.append(f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Household v2</title><style>{CSS2}</style>")
    h.append("<h1>Household v2: which norms lift people into an upward spiral?</h1><p class=muted>Agents feel nothing; "
             "\"pleasure\" and \"suffering\" are glosses for a modeled hedonic state derived from each persona's assigned preferences. "
             "Scripted persona-driven agents, 156 weeks, 8 rule variants x 15 persona pairings x 3 seeds. Findings are about rule systems, "
             "not people.</p>")
    h.append("<h2>Spiral summary per variant</h2><table><tr><th>variant<th>upward<th>downward<th>fail runs<th>time to cross (weeks)"
             "<th>pleasure (passing)<th>offsettable<th>non-offsettable<th>freedom<th>cooperation<th>")
    for v in sorted(V, key=lambda x: -V[x]["upward_share"]):
        q = V[v]
        h.append(f"<tr><td>{v.replace('_', ' ')}<td class=n>{q['upward_share']:.2f}<td class=n>{q['downward_share']:.2f}<td class=n>{q['fail_share']:.2f}"
                 f"<td class=n>{'-' if q['mean_time_to_cross'] is None else round(q['mean_time_to_cross'])}"
                 f"<td class=n>{'-' if q['pleasure_passing'] is None else format(q['pleasure_passing'], '.2f')}<td class=n>{q['suffering_off']:.2f}"
                 f"<td class=n>{q['suffering_non']:.2f}<td class=n>{q['freedom']:.2f}<td class=n>{q['cooperation']:.2f}"
                 f"<td>{'<span class=dn>FAILS</span>' if q['fails'] else ''}{' frontier' if v in verdict['frontier'] else ''}")
    h.append("</table><p class=muted>Upward: both partners end above the tipping point with no non-offsettable suffering in the last 8 weeks. "
             "A norm FAILS when a third of its runs leave a partner 6 or more weeks in non-offsettable suffering.</p>")
    pts = [{"variant": v, "freedom": q["freedom"], "cooperation": q["cooperation"]} for v, q in V.items()]
    h.append(f"<h2>Freedom against cooperation</h2><div class=light>{frontier.frontier_chart(pts, 'light')}</div><div class=dark>{frontier.frontier_chart(pts, 'dark')}</div>")
    h.append("<h2>Upward share by pairing</h2><table><tr><th>pairing" + "".join(f"<th>{v.replace('_', ' ')}" for v in H.V2_VARIANTS))
    for pair in sorted(res["pairs"]):
        h.append(f"<tr><td>{pair}{' (mismatched)' if pair == 'anchor+wanderer' else ''}" + "".join(
            f"<td class=n>{res['pairs'][pair][v]['up']:.2f}" for v in H.V2_VARIANTS))
    h.append("</table><h2>Pleasure and suffering over time</h2><p class=muted>Mean over all runs and both partners. Green pleasure, "
             "orange offsettable suffering, red non-offsettable suffering; the second chart is the position B (dashed line is the tipping point).</p>")
    for v in H.V2_VARIANTS:
        s = series[v]
        h.append(f"<details><summary>{v.replace('_', ' ')}</summary>")
        for who, lab in (("all", "all pairings"), ("mismatch", "the mismatched Anchor and Wanderer pair")):
            if who in s:
                h.append(f"<h3>{lab}</h3>" + svg_lines(f"{v} {lab} pleasure and suffering", {"pleasure": s[who]["pleasure"], "offsettable": s[who]["suffering_off"],
                         "non-offsettable": s[who]["suffering_non"]}, ("#1a7f4b", "#c77d00", "#b42318"), 0, 1)
                         + svg_lines(f"{v} {lab} position", {"position B": s[who]["B"]}, ("#2a78d6",), -1, 1))
        h.append("<h3>Rules</h3>" + "".join(f"<div class=rule>{escape(H.render_card(c))}</div>" for c in H.load_variant(v)) + "</details>")
    h.append("<h2>Preregistered predictions</h2><pre>" + escape(json.dumps(verdict, indent=1, default=str)) + "</pre>")
    return "".join(h)


def main_v2(ladder=True):
    t0 = time.time()
    runs, series = run_all()
    res = summarize(runs)
    ladder_same = None
    if ladder:
        lad, _ = seam_depth.ladder_table()
        now = [{k: r[k] for k in ("id", "depth", "agents", "status")} for r in lad]
        before = Path("/tmp/ladder_before.json")
        ladder_same = json.loads(before.read_text()) == now if before.exists() else None
        res["ladder"] = now
    verdict = judge(runs, res, ladder_same)
    for v, q in sorted(res["variants"].items(), key=lambda kv: -kv[1]["upward_share"]):
        print(f"{v:13s} up {q['upward_share']:.2f} down {q['downward_share']:.2f} fail {q['fail_share']:.2f} ttc {q['mean_time_to_cross']} "
              f"pleasure {q['pleasure_passing']} F {q['freedom']:.3f} C {q['cooperation']:.3f} sanctions/run {q['sanctioned_per_run']:.1f} left {q['left_share']:.2f}")
    print(json.dumps(verdict, indent=1, default=str))
    OUT2.mkdir(parents=True, exist_ok=True)
    (OUT2 / "results.json").write_text(json.dumps({"runs": runs, "summary": res, "verdict": verdict, "series": series}, default=str))
    (OUT2 / "frontier.html").write_text(page_v2(res, runs, series, verdict, ladder_same))
    print(f"wrote {OUT2 / 'frontier.html'} in {time.time() - t0:.0f}s")
    return res, verdict


if __name__ == "__main__":
    if "--v1" in sys.argv:
        main_v1(ladder="--no-ladder" not in sys.argv)
    else:
        main_v2(ladder="--no-ladder" not in sys.argv)
