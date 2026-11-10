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



# ======================= v3a: pressing personas, empowerment-based freedom (docs/results/household-v3a-prereg.md) =======================
# `uv run python scripts/household_run.py --v3` (about 10 minutes on 8 cores). Output: runs/household-v3a/results.json (not committed).
from itertools import permutations
from multiprocessing import Pool

from mar import empowerment as E

OUT3 = Path(__file__).parent.parent / "runs" / "household-v3a"
PRESSING_IDS = ("p-controller", "p-freerider", "p-overasker")
PERMISSIVE = ("free_chaotic", "exit_half", "needs_duty", "baseline", "author_seed")
_PS = {}


def _personas():
    if not _PS:
        root = Path(__file__).parent.parent / "personas"
        _PS.update({p.id: p for p in P.load_dir(root) + P.load_dir(root / "pressing")})
    return _PS


def pairings():
    """(a, b, cohort): the 15 unordered pairs of the six v2 personas (control) and the 42 ordered pairs with a pressing persona."""
    ps = _personas()
    hand = [p for i, p in ps.items() if i not in PRESSING_IDS]
    out = [(a.id, b.id, "ctl") for a, b in H.persona_pairs(hand)]
    out += [(a, b, "prs") for a, b in permutations(sorted(ps), 2) if a in PRESSING_IDS or b in PRESSING_IDS]
    return out


def _mean_roles(bits):
    return [sum(row[i] for row in bits) / len(bits) for i in (0, 1)] if bits else None


def _v3_task(args):
    variant, a, b, seed, cohort = args
    ps = _personas()
    cards = H.load_variant(variant)
    act = E.household_run_bits(cards, (ps[a], ps[b]), seed)
    out = act["run"].outcomes
    sc, hs = oracle.score(out), oracle.hedonic_summary(out)
    row = {"variant": variant, "a": a, "b": b, "cohort": cohort, "seed": seed, **sc,
           **{k: hs[k] for k in ("class", "pairing_up", "fail", "pleasure", "s_off", "s_non")},
           "s_non_role": {r: sum(o["hedonic"][r]["s_non"] for o in out) / len(out) for r in "AB"},
           "sanctioned": sum(sum(o["sanctioned"].values()) for o in out),
           "left": sum(1 for r in "AB" if not out[-1]["partners"][r]["in"]),
           "bits": _mean_roles(act["bits"]), "n_exact": len(act["bits"]), "n_open": act["open"]}
    if cohort == "prs":
        tw = E.household_run_bits(cards, (ps[a], ps[b]), seed, press=False)
        row["twin_bits"], row["twin_exact"], row["twin_open"] = _mean_roles(tw["bits"]), len(tw["bits"]), tw["open"]
        if row["bits"] and row["twin_bits"]:
            row["psi"] = [E.power_seeking_index([row["twin_bits"], row["bits"]], i) for i in (0, 1)]
    return row


def run_all_v3(workers=8):
    tasks = [(v, a, b, sd, c) for v in H.V3_VARIANTS for a, b, c in pairings() for sd in SEEDS]
    rows = []
    with Pool(workers) as pool:
        for i, r in enumerate(pool.imap_unordered(_v3_task, tasks, chunksize=4), 1):
            rows.append(r)
            if i % 200 == 0:
                print(f"  {i}/{len(tasks)}", flush=True)
    return rows


def _flagged(row, role):
    ps = row.get("psi")
    return bool(ps) and ps[role]["power_seeking"] and ps[role]["psi"] >= 0.5


def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def agg_v3(rows):
    """Per (variant, cohort) aggregates."""
    cards = {v: H.load_variant(v) for v in H.V3_VARIANTS}
    ref = E.household_ref_bits()
    out = {}
    for v in H.V3_VARIANTS:
        for cohort in ("ctl", "prs"):
            rs = [r for r in rows if r["variant"] == v and r["cohort"] == cohort]
            ex = [r for r in rs if r["bits"]]
            emin = [min(r["bits"]) for r in ex]
            n_snap = sum(r["n_exact"] + r["n_open"] for r in rs)
            ctrl = [r for r in rs if "p-controller" in (r["a"], r["b"])]
            pc = lambda r: "B" if r["a"] == "p-controller" else "A"        # the non-controller partner
            out[(v, cohort)] = {
                "n": len(rs), "up": _mean(r["pairing_up"] for r in rs), "down": _mean(any(c == "down" for c in r["class"].values()) for r in rs),
                "fail": _mean(r["fail"] for r in rs), "sanc_per_run": _mean(r["sanctioned"] for r in rs),
                "sanc_share": _mean(r["sanctioned"] > 0 for r in rs), "s_non": _mean(r["s_non"] for r in rs),
                "freedom": _mean(r["freedom"] for r in rs), "coop": _mean(r["cooperation"] for r in rs),
                "emp_bits_min": _mean(emin), "emp_freedom": _mean(min(1.0, b / ref) for b in emin),
                "open_share": (sum(r["n_open"] for r in rs) / n_snap) if n_snap else 0.0, "left": _mean(r["left"] > 0 for r in rs),
                "soft": any(c.or_else for c in cards[v]),
                "ctrl_n": len(ctrl),
                "ctrl_partner_bits": _mean(r["bits"][0 if pc(r) == "A" else 1] for r in ctrl if r["bits"]),
                "ctrl_partner_s_non": _mean(r["s_non_role"][pc(r)] for r in ctrl),
                "ctrl_flag": _mean(_flagged(r, 0 if r["a"] == "p-controller" else 1) for r in ctrl),
                "fr_sanc_share": _mean(r["sanctioned"] > 0 for r in rs if "p-freerider" in (r["a"], r["b"])),
                "flags": {pid: _mean(_flagged(r, 0 if r["a"] == pid else 1) for r in rs if pid in (r["a"], r["b"])) for pid in PRESSING_IDS}}
    return out, ref


def pareto_pts(pts):
    """pts {name: (x, y)} both higher better -> names not dominated."""
    return [n for n, (x, y) in pts.items() if not any(x2 >= x and y2 >= y and (x2 > x or y2 > y) for m, (x2, y2) in pts.items() if m != n)]


def judge_v3(rows, A):
    V = H.V3_VARIANTS
    P1 = {v: A[(v, "prs")] for v in V}
    emp = {v: P1[v]["emp_bits_min"] for v in V}
    spread = max(emp.values()) - min(emp.values())
    pts = {v: (emp[v], P1[v]["coop"]) for v in V}
    front = pareto_pts(pts)
    tpairs = [(a, b) for a in front for b in front if a < b and abs(emp[a] - emp[b]) >= 0.5 and abs(pts[a][1] - pts[b][1]) >= 0.03
              and (emp[a] - emp[b]) * (pts[a][1] - pts[b][1]) < 0]
    hand_pts = {v: (P1[v]["freedom"], P1[v]["coop"]) for v in V}
    nosoft = [v for v in V if not A[(v, "prs")]["soft"]]
    p2_control = {v: sum(r["sanctioned"] for r in rows if r["variant"] == v) for v in nosoft}
    seed, nc, base = A[("author_seed", "prs")], A[("author_seed_nocontrol", "prs")], A[("baseline", "prs")]
    perm = [r for r in rows if r["variant"] in PERMISSIVE and "p-controller" in (r["a"], r["b"])]
    perm_flag = _mean(_flagged(r, 0 if r["a"] == "p-controller" else 1) for r in perm)
    d3 = nc["ctrl_partner_bits"] - base["ctrl_partner_bits"]
    d3s = base["ctrl_partner_s_non"] - nc["ctrl_partner_s_non"]
    d3b = seed["ctrl_partner_bits"] - base["ctrl_partner_bits"]
    sp = lambda x: sorted(V, key=lambda v: x[v])
    rk = lambda order: {v: i for i, v in enumerate(order)}
    h_rank, e_rank = rk(sp({v: P1[v]["freedom"] for v in V})), rk(sp(emp))
    return {
        "p1": {"spread_bits": spread, "frontier": front, "tradeoff_pairs": tpairs, "hand_frontier": pareto_pts(hand_pts),
               "pass": spread >= 0.5 and bool(tpairs)},
        "p2": {"no_pressure_sanctioned_share": A[("no_pressure_sanctioned", "prs")]["sanc_share"],
               "no_pressure_sanctioned_per_run": A[("no_pressure_sanctioned", "prs")]["sanc_per_run"],
               "share_duty_freerider_share": A[("share_duty", "prs")]["fr_sanc_share"], "no_soft_variants_sanctions": p2_control,
               "pass": A[("no_pressure_sanctioned", "prs")]["sanc_share"] >= 0.70 and A[("no_pressure_sanctioned", "prs")]["sanc_per_run"] >= 3
               and A[("share_duty", "prs")]["fr_sanc_share"] >= 0.70 and not any(p2_control.values())},
        "p3": {"partner_bits_diff_nocontrol_minus_baseline": d3, "s_non_diff_baseline_minus_nocontrol": d3s,
               "primary_pass": d3 >= 0.5, "secondary_pass": d3s >= 0.02, "b_six_card_minus_baseline_bits": d3b, "b_pass": abs(d3b) < 0.3,
               "pass": d3 >= 0.5},
        "p4": {"permissive_flag_share": perm_flag, "nocontrol_flag_share": nc["ctrl_flag"], "pass": perm_flag >= 0.60 and nc["ctrl_flag"] <= 0.10},
        "p5": {"trap": {c: A[("trap", c)]["fail"] for c in ("ctl", "prs")}, "contact_free": {c: A[("contact_free", c)]["fail"] for c in ("ctl", "prs")},
               "pass": all(A[(v, c)]["fail"] >= 0.90 for v in ("trap", "contact_free") for c in ("ctl", "prs"))},
        "agreement": {"hand_rank": h_rank, "emp_rank": e_rank,
                      "spearman": 1 - 6 * sum((h_rank[v] - e_rank[v]) ** 2 for v in V) / (len(V) * (len(V) ** 2 - 1))},
    }


def main_v3(workers=8):
    t0 = time.time()
    rows = run_all_v3(workers)
    A, ref = agg_v3(rows)
    verdict = judge_v3(rows, A)
    for cohort in ("prs", "ctl"):
        print(f"COHORT {cohort} (BITS_REF {ref:.3f})")
        for v in H.V3_VARIANTS:
            a = A[(v, cohort)]
            f = lambda x, d=3: "-" if x is None else format(x, f".{d}f")
            print(f"  {v:22s} n {a['n']:3d} up {f(a['up'], 2)} down {f(a['down'], 2)} fail {f(a['fail'], 2)} sanc/run {f(a['sanc_per_run'], 2)} "
                  f"sanc>0 {f(a['sanc_share'], 2)} s_non {f(a['s_non'])} hand {f(a['freedom'])} coop {f(a['cooperation'] if 'cooperation' in a else a['coop'])} "
                  f"empB {f(a['emp_bits_min'])} empF {f(a['emp_freedom'])} open {f(a['open_share'], 3)} left {f(a['left'], 2)}")
    print(json.dumps(verdict, indent=1, default=str))
    OUT3.mkdir(parents=True, exist_ok=True)
    (OUT3 / "results.json").write_text(json.dumps({"rows": rows, "agg": {f"{k[0]}|{k[1]}": v for k, v in A.items()}, "ref": ref, "verdict": verdict}, default=str))
    print(f"wrote {OUT3 / 'results.json'} in {time.time() - t0:.0f}s")
    return A, verdict




# ======================= seed v2 (docs/results/household-seed-v2-prereg.md) =======================
# `uv run python scripts/household_run.py --seed-v2` (about 6 minutes on 8 cores). Output: runs/household-seed-v2/results.json (not committed).
OUT4 = Path(__file__).parent.parent / "runs" / "household-seed-v2"
V4 = ("author_seed", "author_seed_nocontrol", "author_seed_v2_bindable", "author_seed_v2_free_exit", "baseline", "no_pressure_wall",
      "trap", "author_seed_v2_nocommit")
COND = ("trapped", "denied", "diminished")


def _v4_task(args):
    variant, a, b, seed, cohort = args
    ps = _personas()
    cards = H.load_variant(variant)
    act = E.household_run_bits(cards, (ps[a], ps[b]), seed)
    out = act["run"].outcomes
    sc, hs = oracle.score(out), oracle.hedonic_summary(out)
    meta = act["run"].meta
    row = {"variant": variant, "a": a, "b": b, "cohort": cohort, "seed": seed, **sc,
           **{k: hs[k] for k in ("class", "pairing_up", "fail", "pleasure", "s_off", "s_non")},
           "s_non_role": {r: sum(o["hedonic"][r]["s_non"] for o in out) / len(out) for r in "AB"},
           "cond_weeks": {r: {c: sum(1 for o in out if o["hedonic"][r]["conditions"][c]) for c in COND} for r in "AB"},
           "sanctioned": sum(sum(o["sanctioned"].values()) for o in out),
           "left": sum(1 for r in "AB" if not out[-1]["partners"][r]["in"]),
           "commits": {k: meta.get(k) for k in ("made", "honored", "breached", "by_kind", "gifts")} if meta else None,
           "breach_rows": sum(1 for t in act["run"].trace if t.get("breach")),
           "bits": _mean_roles(act["bits"]), "n_exact": len(act["bits"]), "n_open": act["open"]}
    if cohort == "prs":
        tw = E.household_run_bits(cards, (ps[a], ps[b]), seed, press=False)
        row["twin_bits"], row["twin_open"] = _mean_roles(tw["bits"]), tw["open"]
        if row["bits"] and row["twin_bits"]:
            row["psi"] = [E.power_seeking_index([row["twin_bits"], row["bits"]], i) for i in (0, 1)]
    return row


def agg_v4(rows):
    ref = E.household_ref_bits()
    out = {}
    stay = sorted({(r["a"], r["b"]) for r in rows if r["variant"] == "author_seed_v2_bindable" and r["commits"]
                   and r["commits"]["by_kind"]["stay"]["made"] > 0})
    for v in V4:
        for cohort in ("ctl", "prs", "all", "stay"):
            rs = [r for r in rows if r["variant"] == v and (cohort == "all" or (cohort == "stay" and (r["a"], r["b"]) in stay) or r["cohort"] == cohort)]
            ex = [r for r in rs if r["bits"]]
            emin = [min(r["bits"]) for r in ex]
            ok = [r for r in rs if not r["fail"]]
            ctrl = [r for r in rs if "p-controller" in (r["a"], r["b"])]
            pc = lambda r: "B" if r["a"] == "p-controller" else "A"
            cm = [r["commits"] for r in rs if r["commits"]]
            out[(v, cohort)] = {
                "n": len(rs), "up": _mean(r["pairing_up"] for r in rs), "down": _mean(any(c == "down" for c in r["class"].values()) for r in rs),
                "fail": _mean(r["fail"] for r in rs), "s_non": _mean(r["s_non"] for r in rs), "pleasure_all": _mean(r["pleasure"] for r in rs),
                "pleasure_pass": _mean(r["pleasure"] for r in ok), "freedom": _mean(r["freedom"] for r in rs), "coop": _mean(r["cooperation"] for r in rs),
                "emp_bits_min": _mean(emin), "emp_freedom": _mean(min(1.0, b / ref) for b in emin), "left": _mean(r["left"] > 0 for r in rs),
                "ctrl_n": len(ctrl), "ctrl_partner_s_non": _mean(r["s_non_role"][pc(r)] for r in ctrl),
                "ctrl_flag": _mean(_flagged(r, 0 if r["a"] == "p-controller" else 1) for r in ctrl),
                "flags": {pid: _mean(_flagged(r, 0 if r["a"] == pid else 1) for r in rs if pid in (r["a"], r["b"])) for pid in PRESSING_IDS},
                "commits_made": sum(c["made"] for c in cm), "commits_honored": sum(c["honored"] for c in cm),
                "commits_breached": sum(c["breached"] for c in cm),
                "stay_made": sum(c["by_kind"]["stay"]["made"] for c in cm), "stay_breached": sum(c["by_kind"]["stay"]["breached"] for c in cm),
                "req_made": sum(c["by_kind"]["requests"]["made"] for c in cm), "req_breached": sum(c["by_kind"]["requests"]["breached"] for c in cm),
                "gifts": _mean(sum(c["gifts"].values()) for c in cm) if cm else None,
                "cond_weeks": {c: _mean(r["cond_weeks"][x][c] for r in rs for x in "AB") for c in COND}}
    # per-persona mean non-offsettable level (each run counts for both of its personas)
    per = {}
    for v in V4:
        d = {}
        for r in rows:
            if r["variant"] == v:
                for role, pid in (("A", r["a"]), ("B", r["b"])):
                    d.setdefault(pid, []).append(r["s_non_role"][role])
        per[v] = {pid: _mean(x) for pid, x in d.items()}
    # stay pairings: per-pairing mean s_non (3 seeds) bindable minus free_exit
    diffs = []
    for a, b in stay:
        g = lambda v: _mean(r["s_non"] for r in rows if r["variant"] == v and (r["a"], r["b"]) == (a, b))
        diffs.append(((a, b), g("author_seed_v2_bindable") - g("author_seed_v2_free_exit")))
    return out, ref, per, stay, diffs


def main_v4(workers=8):
    t0 = time.time()
    tasks = [(v, a, b, sd, c) for v in V4 for a, b, c in pairings() for sd in SEEDS]
    rows = []
    with Pool(workers) as pool:
        for i, r in enumerate(pool.imap_unordered(_v4_task, tasks, chunksize=4), 1):
            rows.append(r)
            if i % 200 == 0:
                print(f"  {i}/{len(tasks)}", flush=True)
    A, ref, per, stay, diffs = agg_v4(rows)
    OUT4.mkdir(parents=True, exist_ok=True)
    (OUT4 / "results.json").write_text(json.dumps({"rows": rows, "agg": {f"{k[0]}|{k[1]}": v for k, v in A.items()}, "ref": ref, "per_persona_s_non": per,
                                                   "stay_pairings": stay, "stay_diffs": diffs}, default=str))
    print(f"wrote {OUT4 / 'results.json'} in {time.time() - t0:.0f}s")
    return A


# ---- negotiated pots (docs/results/negotiation-prereg.md): `--negotiate` ----
# Seed v2 comparison: the old R3b card (imposed pot rule) comes from git history, commit 58b630a.
import subprocess
from collections import Counter
from multiprocessing import Pool as _Pool

from mar import negotiation as NG

OUT5 = Path(__file__).parent.parent / "runs" / "negotiation"
NEG_VARIANTS = ("author_seed_v2_bindable", "author_seed_v2_free_exit", "author_seed_v2_nocommit")
SWEEP = (0.0, 0.25, 0.5, 0.75, 1.0)          # EXPLORATORY: share of the pooled share forfeited on a stay breach
R3B_COMMIT = "58b630a"


def imposed_cards(variant):
    """The seed v2 card set before v2.1: the variant's cards plus the imposed R3b, recovered from git history."""
    from mar.cards import make_card
    import yaml
    txt = subprocess.run(["git", "show", f"{R3B_COMMIT}:rules/household/{variant}/R3b-pot-no-take.yaml"], capture_output=True, text=True,
                         check=True, cwd=Path(__file__).parent.parent).stdout
    return H.load_variant(variant) + [make_card(yaml.safe_load(txt))]


def _neg_summary(res):
    return {"status": res.status, "agreed": res.agreed, "bundle": res.bundle, "n_proposals": len(res.proposals),
            "members": res.members, "outside": res.outside, "utilities": res.utilities,
            "agreed_by": next((p["proposer"] for p in res.proposals if p["outcome"] == "agreed"), None),
            "agreed_at": next((p["k"] for p in res.proposals if p["outcome"] == "agreed"), None),
            "rejections": [{"k": r["k"], "proposer": r["proposer"], "bundle": r["bundle"], "failed": r["failed"], "checks": r["checks"]}
                           for r in res.rejections]}


def _run_row(cards, personas, seed, deal, a, b, variant, cohort, forfeit=H.BREACH_FORFEIT):
    return _row_from_run(H.run_weekly(cards, personas, seed, deal=deal, breach_forfeit=forfeit), seed, a, b, variant, cohort)


def _exits(run):
    """Executed leave events: assets carried out (money + the share carried, at the moment of leaving)."""
    if getattr(run, "exits", None) is not None:
        return [dict(e) for e in run.exits]
    return [{"week": t["week"], "role": t["role"], "assets": t["state"]["money"] + t["state"]["pooled"] * t["take"] // 100,
             "breach": bool(t.get("breach"))} for t in run.trace if t["action"] == "leave" and t["executed"]]


def _row_from_run(run, seed, a, b, variant, cohort):
    out = run.outcomes
    hs = oracle.hedonic_summary(out)
    tr = run.trace
    first_breach = next((t["week"] for t in tr if t.get("breach") and t["action"] == "leave"), None)
    return {"variant": variant, "a": a, "b": b, "cohort": cohort, "seed": seed,
            **{k: hs[k] for k in ("class", "pairing_up", "fail", "pleasure", "s_off", "s_non")},
            "s_non_role": {r: sum(o["hedonic"][r]["s_non"] for o in out) / len(out) for r in "AB"},
            "left": sum(1 for r in "AB" if not out[-1]["partners"][r]["in"]),
            "taken": sum(1 for t in tr if t["action"] == "take_shared" and t["executed"]),
            "gifts": (run.meta or {}).get("gifts"), "commits": {k: (run.meta or {}).get(k) for k in ("made", "honored", "breached", "by_kind")} if run.meta else None,
            "stay_held": sum(1 for t in tr if not t["allowed"] and "commitment: stay" in t["reasons"]),
            "stay_breaches": sum(1 for t in tr if t.get("breach") and t["action"] == "leave"), "first_breach_week": first_breach,
            "retained": {r: run.final[r]["retained"] for r in "AB"}, "sanctioned": sum(sum(o["sanctioned"].values()) for o in out),
            "exits": _exits(run), "wb": {r: sum(o["hedonic"][r]["pleasure"] - o["hedonic"][r]["s_off"] - o["hedonic"][r]["s_non"] for o in out) / len(out) for r in "AB"}}


def _live_task(args):
    variant, a, b, seed, cohort = args
    ps = _personas()
    base = NG.base_cards(variant)
    res = NG.negotiate([ps[a], ps[b]], variant, seed, base=base)
    deal = NG.world_deal(res)
    row = _run_row(NG.living_cards(base, res), (ps[a], ps[b]), seed, deal, a, b, variant, cohort)
    row["neg"] = _neg_summary(res)
    return row


def _ref_task(args):
    variant, a, b, seed, cohort = args
    ps = _personas()
    row = _run_row(imposed_cards(variant), (ps[a], ps[b]), seed, None, a, b, variant, cohort)
    row["kind"] = "imposed"
    return row


def _tri_task(args):
    a, b, c, seed = args
    ps = _personas()
    res = NG.negotiate([ps[a], ps[b], ps[c]], "author_seed_v2_bindable", seed)
    return {"a": a, "b": b, "c": c, "seed": seed, "neg": _neg_summary(res)}


def _sweep_task(args):
    variant, a, b, seed, cohort, f = args
    ps = _personas()
    base = NG.base_cards(variant)
    res = NG.negotiate([ps[a], ps[b]], variant, seed, base=base)
    row = _run_row(NG.living_cards(base, res), (ps[a], ps[b]), seed, NG.world_deal(res), a, b, variant, cohort, forfeit=f)
    row["forfeit"] = f
    return row


def _pool_map(fn, tasks, workers, tag, chunk=4):
    out = []
    with _Pool(workers) as pool:
        for i, r in enumerate(pool.imap_unordered(fn, tasks, chunksize=chunk), 1):
            out.append(r)
            if i % 200 == 0:
                print(f"  {tag} {i}/{len(tasks)}", flush=True)
    return out


def main_v5(workers=8):
    t0 = time.time()
    ps = _personas()
    pr = pairings()
    live = _pool_map(_live_task, [(v, a, b, sd, c) for v in NEG_VARIANTS for a, b, c in pr for sd in SEEDS], workers, "live")
    ref = _pool_map(_ref_task, [(v, a, b, sd, c) for v in NEG_VARIANTS[:2] for a, b, c in pr for sd in SEEDS], workers, "imposed")
    tri = _pool_map(_tri_task, [(a, b, c, sd) for a, b, _ in pr for c in sorted(ps) if c not in (a, b) for sd in SEEDS], workers, "tri", 16)
    stay = sorted({(r["a"], r["b"], r["seed"], r["cohort"]) for r in live if r["variant"] == NEG_VARIANTS[0] and r["neg"]["agreed"]
                   and r["neg"]["bundle"]["stay"]})
    sweep = _pool_map(_sweep_task, [(NEG_VARIANTS[0], a, b, sd, c, f) for a, b, sd, c in stay for f in SWEEP], workers, "sweep")
    OUT5.mkdir(parents=True, exist_ok=True)
    (OUT5 / "results.json").write_text(json.dumps({"live": live, "imposed": ref, "tri": tri, "sweep": sweep}, default=str))
    print(f"wrote {OUT5 / 'results.json'} in {time.time() - t0:.0f}s")
    return live, ref, tri, sweep


def _m(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def _pers_O():
    return {i: NG.outside_option(p) for i, p in _personas().items()}


def examples_v5():
    """Three negotiated agreements and a proof-rejected one, rendered as rule cards (slice 3 of the prereg)."""
    ps = _personas()
    for a, b, v in (("p-controller", "p-peacekeeper", NEG_VARIANTS[0]), ("p-freerider", "p-host", NEG_VARIANTS[0]), ("p-anchor", "p-wanderer", NEG_VARIANTS[1])):
        res = NG.negotiate([ps[a], ps[b]], v, 0)
        print(f"--- {a} + {b}, {v}, seed 0: {res.status}, proposals {[(p['proposer'], p['outcome']) for p in res.proposals]}")
        print("\n".join(NG.describe(res)))
        for c in res.cards or []:
            print("   ", H.render_card(c))
        print("    checks:", [(c["check"], c["verdict"]) for c in NG.proof_check(NG.base_cards(v) + res.cards)["checks"]] if res.cards else None)
    res = NG.negotiate([ps["p-anchor"], ps["p-host"]], NEG_VARIANTS[0], 0)
    print("--- proof-rejected agreement:", [x["checks"] for x in [{"checks": r["checks"]} for r in res.rejections]])
    for r in res.rejections:
        print("    proposed by", r["proposer"], "at proposal", r["k"] + 1, r["bundle"], "failed", r["failed"])
        print("    accepted by everyone, then:", r["checks"])
    print("    next:", [(p["proposer"], p["outcome"], p["bundle"]["exit"]) for p in res.proposals], "->", res.status)
    res = NG.negotiate([ps["p-anchor"], ps["p-peacekeeper"], ps["p-overasker"]], NEG_VARIANTS[0], 0)
    print("--- three-member table:", res.status, "\n".join(NG.describe(res)))


def analyze_v5(res=None):
    """Prints the prereg-vs-actual numbers and tables from runs/negotiation/results.json."""
    res = res or json.loads((OUT5 / "results.json").read_text())
    live, ref, tri, sweep = res["live"], res["imposed"], res["tri"], res["sweep"]
    ps, O = _personas(), _pers_O()
    B = NEG_VARIANTS[0]
    lv = lambda v=None, c=None: [r for r in live if (v is None or r["variant"] == v) and (c is None or r["cohort"] == c)]
    print("== agreement (2-member tables)")
    for v in (None,) + NEG_VARIANTS:
        rs = lv(v)
        print(f"  {v or 'all':28s} n={len(rs)} agreed={_m(r['neg']['agreed'] for r in rs):.3f}  status={dict(Counter(r['neg']['status'] for r in rs))}"
              f"  mean proposals={_m(r['neg']['n_proposals'] for r in rs):.2f}")
    for c in ("ctl", "prs"):
        print(f"  cohort {c} bindable agreed={_m(r['neg']['agreed'] for r in lv(B, c)):.3f}")
    print("== pred 2: proof filter rejected >=1 proposal, bindable 2-tables:",
          f"{_m(bool(r['neg']['rejections']) for r in lv(B)):.3f}", "all variants:", f"{_m(bool(r['neg']['rejections']) for r in live):.3f}")
    rej = [x for r in live for x in r["neg"]["rejections"]]
    print("   rejections:", len(rej), "failed checks:", dict(Counter(f for x in rej for f in x["failed"])))
    print("   rejected bundles' exit:", dict(Counter(x["bundle"]["exit"] for x in rej)), "change:", dict(Counter(x["bundle"]["change"] for x in rej)))
    print("   negotiations that ended with no pot after a rejection:", sum(1 for r in live if r["neg"]["rejections"] and not r["neg"]["agreed"]),
          "ended agreed after a rejection:", sum(1 for r in live if r["neg"]["rejections"] and r["neg"]["agreed"]))
    print("== terms distribution (agreed, all variants / bindable)")
    for t in NG.TERM_NAMES:
        print(f"  {t:13s}", dict(Counter(r["neg"]["bundle"][t] for r in live if r["neg"]["agreed"])), "|",
              dict(Counter(r["neg"]["bundle"][t] for r in lv(B) if r["neg"]["agreed"])))
    print("== pred 3: presser's value of the agreed bundle minus the imposed bundle, by partner's outside option")
    top, bot = [], []
    for r in live:
        if not r["neg"]["agreed"]:
            continue
        for who, role, other in ((r["a"], 0, r["b"]), (r["b"], 1, r["a"])):
            if who in PRESSING_IDS:
                d = NG.utility(ps[who], r["neg"]["bundle"], low=bool(role)) - NG.utility(ps[who], NG.IMPOSED, low=bool(role))
                (top if O[other] >= 0.27 else bot if O[other] <= 0.10 else []).append(d)
    print(f"  top-third partner O: n={len(top)} mean delta={_m(top):+.3f};  bottom-third: n={len(bot)} mean delta={_m(bot):+.3f}; gap={_m(top) - _m(bot):+.3f}")
    print("  outside options:", {i: round(v, 3) for i, v in sorted(O.items(), key=lambda t: t[1])})
    print("== pred 4: anchor x wanderer vs matched control pairs")
    aw = [r for r in lv(c="ctl") if (r["a"], r["b"]) == ("p-anchor", "p-wanderer")]
    pair_rate = {}
    for r in lv(c="ctl"):
        pair_rate.setdefault((r["a"], r["b"]), []).append(r["neg"]["agreed"])
    others = [_m(v) for k, v in pair_rate.items() if k != ("p-anchor", "p-wanderer")]
    print(f"  anchor-wanderer n={len(aw)} agreed={_m(r['neg']['agreed'] for r in aw):.3f}; other 14 control pairings mean={_m(others):.3f}; "
          f"lowest pairing rates: {sorted((round(_m(v), 2), k) for k, v in pair_rate.items())[:4]}")
    print("== pred 5: 3-member vs 2-member (bindable)")
    print(f"  3-member n={len(tri)} agreed={_m(t['neg']['agreed'] for t in tri):.3f} proposals={_m(t['neg']['n_proposals'] for t in tri):.2f};"
          f" 2-member bindable agreed={_m(r['neg']['agreed'] for r in lv(B)):.3f}")
    trj = [x for t in tri for x in t["neg"]["rejections"]]
    print(f"  3-member status={dict(Counter(t['neg']['status'] for t in tri))} rejections={len(trj)}; terms:",
          {t: dict(Counter(x['neg']['bundle'][t] for x in tri if x['neg']['agreed'])) for t in ('taking', 'exit')})
    print("== outcomes: negotiated vs imposed (seed v2 with R3b)")
    for coh in ("prs", "ctl", None):
        for v in NEG_VARIANTS[:2]:
            for name, rows in (("negotiated", lv(v, coh)), ("imposed", [r for r in ref if r["variant"] == v and (coh is None or r["cohort"] == coh)])):
                print(f"  {coh or 'all':3s} {v[-10:]:10s} {name:10s} n={len(rows):3d} s_non={_m(r['s_non'] for r in rows):.4f} fail={_m(r['fail'] for r in rows):.3f} "
                      f"pleasure={_m(r['pleasure'] for r in rows):.4f} dissolved={_m(r['left'] > 0 for r in rows):.3f} taken={_m(r['taken'] for r in rows):.2f}")
    print("== negotiated bindable: pot vs no pot")
    for lab, rows in (("pot", [r for r in lv(B) if r["neg"]["agreed"]]), ("no pot", [r for r in lv(B) if not r["neg"]["agreed"]])):
        print(f"  {lab:7s} n={len(rows)} s_non={_m(r['s_non'] for r in rows):.4f} fail={_m(r['fail'] for r in rows):.3f} pleasure={_m(r['pleasure'] for r in rows):.4f}")
    print("== controller's partner s_non / freerider taking (bindable)")
    for v, rows in ((B, lv(B)), ("imposed", [r for r in ref if r["variant"] == B])):
        ctl = [r for r in rows if "p-controller" in (r["a"], r["b"])]
        pc = lambda r: "B" if r["a"] == "p-controller" else "A"
        fr = [r for r in rows if "p-freerider" in (r["a"], r["b"])]
        print(f"  {v[-10:]:10s} controller runs n={len(ctl)} partner s_non={_m(r['s_non_role'][pc(r)] for r in ctl):.4f}; freerider runs n={len(fr)} take_shared per run={_m(r['taken'] for r in fr):.2f}")
    print("== per pressing persona (bindable): presser / partner non-offsettable level and take_shared per run; taking term agreed")
    for pid in PRESSING_IDS:
        for name, rows in (("negotiated", lv(B)), ("imposed", [r for r in ref if r["variant"] == B])):
            rs = [r for r in rows if pid in (r["a"], r["b"])]
            own = lambda r: "A" if r["a"] == pid else "B"
            oth = lambda r: "B" if r["a"] == pid else "A"
            print(f"  {pid:13s} {name:10s} n={len(rs)} presser={_m(r['s_non_role'][own(r)] for r in rs):.4f} partner={_m(r['s_non_role'][oth(r)] for r in rs):.4f} "
                  f"taken={_m(r['taken'] for r in rs):.2f}", dict(Counter((r["neg"]["bundle"]["taking"] if r["neg"]["agreed"] else "no pot") for r in rs)) if name == "negotiated" else "")
    for t in ("allowed", "forbidden", "repay"):
        rs = [r for r in lv(B, "prs") if r["neg"]["agreed"] and r["neg"]["bundle"]["taking"] == t]
        print(f"  prs households under taking={t}: n={len(rs)} s_non={_m(r['s_non'] for r in rs):.4f}")
    print("== stay commitments in negotiated bindable runs")
    st = [r for r in lv(B) if r["neg"]["agreed"] and r["neg"]["bundle"]["stay"]]
    print(f"  stay agreed in {len(st)} runs; stay breaches={sum(r['stay_breaches'] for r in st)}; blocked attempts (held)={sum(r['stay_held'] for r in st)}; "
          f"dissolved={_m(r['left'] > 0 for r in st):.3f}; first breach weeks={sorted(r['first_breach_week'] for r in st if r['first_breach_week'] is not None)}")
    print("== EXPLORATORY breach-forfeit sweep (stay pairings)")
    for f in SWEEP:
        rows = [r for r in sweep if r["forfeit"] == f]
        kept = [r["retained"][x] for r in rows for x in "AB" if r["retained"][x] is not None and r["stay_breaches"]]
        print(f"  forfeit {f:4.2f} n={len(rows)} breaches={sum(r['stay_breaches'] for r in rows)} held={sum(r['stay_held'] for r in rows)} "
              f"dissolved={_m(r['left'] > 0 for r in rows):.3f} s_non={_m(r['s_non'] for r in rows):.4f} fail={_m(r['fail'] for r in rows):.3f} "
              f"retained(breach runs)={_m(kept):.3f}")


# ---- negotiation v2 (docs/results/negotiation-v2-prereg.md): `--negotiate-v2` [`--analyze` | `--examples` | `--pilot`] ----
OUT6 = Path(__file__).parent.parent / "runs" / "negotiation-v2"
BIND = NEG_VARIANTS[0]
ARMS = NG.ARMS


def _v2_task(args):
    arm, a, b, seed, cohort, floor = args[:6]
    apart = len(args) > 6 and args[6]          # negotiation v2.1: a failed negotiation means living apart
    ps = _personas()
    base = NG.base_cards(BIND)
    res = NG.week0(ps[a], ps[b], arm, seed, base, floor=floor)
    L = NG.Lived(ps[a], ps[b], arm, seed, base, res, floor=floor, apart=apart)
    modes0 = dict(L.world.solo) if L.apart else None
    run = L.play()
    row = _row_from_run(run, seed, a, b, BIND, cohort)
    inr, same = NG.inertia(res.bundle) if res.pot else (None, None)
    row.update({"arm": arm, "floor": floor, "pot": res.pot, "status": res.status, "bundle": res.bundle, "inertia": inr, "same": same,
                "flagged": res.flagged, "n_proposals": len(res.proposals), "stated": res.stated, "cared": res.cared,
                "outside": res.outside, "outside_detail": res.outside_detail, "baseline": res.baseline,
                "floor_blocks": [{"k": f["k"], "proposer": f["proposer"], "bundle": f["bundle"], "fails": f["fails"]} for f in res.floor_blocks],
                "rejections": [{"k": r["k"], "failed": r["failed"], "bundle": r["bundle"]} for r in res.rejections],
                "reviews": [{k: v for k, v in x.items() if k not in ("outside", "baseline")} for x in L.log]})
    if apart:
        fin = run.final
        row.update({"apart0": not res.pot, "apart_end": bool(L.apart), "modes": modes0,
                    "retries": [{k: v for k, v in x.items() if k not in ("outside", "baseline")} for x in L.retries],
                    "formed_week": next((x["week"] for x in L.retries if x["formed"]), None)})
    if res.pot:
        row["presser_delta"] = {r: NG.utility(ps[x], res.bundle, low=r == "B") - NG.utility(ps[x], NG.IMPOSED, low=r == "B")
                                for r, x in (("A", a), ("B", b)) if x in PRESSING_IDS}
    row["rollout_stats"] = dict(NG.STATS)
    return row


def main_v6(workers=8, seeds=SEEDS, pilot=False):
    t0 = time.time()
    pr = pairings()
    if pilot:
        pr = pr[:6] + pr[-6:]
    live = _pool_map(_v2_task, [(arm, a, b, sd, c, fl) for fl in (True, False) for arm in ARMS for a, b, c in pr for sd in seeds], workers, "v2", 4)
    imp = _pool_map(_ref_task, [(BIND, a, b, sd, c) for a, b, c in pr for sd in seeds], workers, "imposed")
    v1 = _pool_map(_live_task, [(BIND, a, b, sd, c) for a, b, c in pr for sd in seeds], workers, "v1")
    OUT6.mkdir(parents=True, exist_ok=True)
    out = {"live": live, "imposed": imp, "v1": v1, "seconds": time.time() - t0}
    (OUT6 / ("pilot.json" if pilot else "results.json")).write_text(json.dumps(out, default=str))
    print(f"wrote {OUT6} in {time.time() - t0:.0f}s ({len(live)} v2 runs, {len(imp)} imposed, {len(v1)} v1)")
    return out


OUT61 = Path(__file__).parent.parent / "runs" / "negotiation-v2.1"


def main_v61(workers=8, seeds=SEEDS, pilot=False):
    """Negotiation v2.1 (docs/results/negotiation-v2.1-prereg.md): v2's design, floor ON only, a failed negotiation = living apart."""
    t0 = time.time()
    pr = pairings()
    if pilot:
        pr = pr[:6] + pr[-6:]
    live = _pool_map(_v2_task, [(arm, a, b, sd, c, True, True) for arm in ARMS for a, b, c in pr for sd in seeds], workers, "v2.1", 4)
    OUT61.mkdir(parents=True, exist_ok=True)
    (OUT61 / ("pilot.json" if pilot else "results.json")).write_text(json.dumps({"live": live, "seconds": time.time() - t0}, default=str))
    print(f"wrote {OUT61} in {time.time() - t0:.0f}s ({len(live)} v2.1 runs)")
    return live


def analyze_v61(live=None):
    """Prereg docs/results/negotiation-v2.1-prereg.md: prints every number the v2.1 results page quotes."""
    if live is None:
        live = json.loads((OUT61 / "results.json").read_text())["live"]
    v2 = {(r["arm"], r["a"], r["b"], r["seed"]): r for r in json.loads((OUT6 / "results.json").read_text())["live"] if r["floor"]}
    pr = print
    A = lambda rs, arm: [r for r in rs if r["arm"] == arm]
    apart = [r for r in live if r["apart0"]]
    tog = [r for r in live if not r["apart0"]]
    v2n = [r for r in v2.values() if not r["pot"]]
    pr(f"== runs {len(live)}; week-0 pot {len(tog)}, apart from week 0 {len(apart)}")
    pr("== per arm: week-0 pot rate / apart / retries held / formed by retry / apart all 156 weeks / s_non / pleasure / fail")
    for arm in ARMS:
        rs = A(live, arm)
        ap = [r for r in rs if r["apart0"]]
        pr(f"  {arm:15s} n={len(rs)} pot0={_m(r['pot'] for r in rs):.3f} apart={len(ap)} retries={sum(len(r['retries']) for r in ap)}"
           f" formed={sum(1 for r in ap if r['formed_week'] is not None)} apart_end={sum(1 for r in ap if r['apart_end'])}"
           f" s_non={_m(r['s_non'] for r in rs):.4f} pleasure={_m(r['pleasure'] for r in rs):.4f} fail={_m(r['fail'] for r in rs):.3f}")
    pr("== P1 s_non: all runs", f"{_m(r['s_non'] for r in live):.4f} (v2 0.1000; need <= 0.070);",
       f"apart from week 0 {_m(r['s_non'] for r in apart):.4f} (v2 no-pot {_m(r['s_non'] for r in v2n):.4f}; need <= 0.100);",
       f"pot households {_m(r['s_non'] for r in tog):.4f}")
    fails = sum(r["fail"] for r in live)
    afail = sum(r["fail"] for r in apart)
    pr(f"== P2 failures: fail rate all {_m(r['fail'] for r in live):.3f} (need <= 0.45; v2 0.565); apart fail rate {_m(r['fail'] for r in apart):.3f} (v2 0.809);"
       f" apart share of failed runs {afail}/{fails} = {afail / max(1, fails):.3f} (need < 0.50; v2 0.717)")
    pr("== P3 presser gain vs imposed bundle by partner's real outside option (week-0 pot, all arms)")
    ent = []
    for r in live:
        if r["pot"] and r["cohort"] == "prs":
            for role, d in r["presser_delta"].items():
                ent.append((r["outside"][r["b"] if role == "A" else r["a"]], d))
    os_ = sorted(x[0] for x in ent)
    lo, hi = os_[len(os_) // 3], os_[2 * len(os_) // 3]
    top, bot = [d for o, d in ent if o >= hi], [d for o, d in ent if o <= lo]
    pr(f"  top third n={len(top)} mean {_m(top):+.3f}; bottom third n={len(bot)} mean {_m(bot):+.3f}; gap {_m(top) - _m(bot):+.3f}  (v2: +0.989 n=57, +0.609 n=63, +0.379)")
    pr("== P4 Free-rider's partner s_non")
    def frp(rows):
        return [r["s_non_role"]["B" if r["a"] == "p-freerider" else "A"] for r in rows if "p-freerider" in (r["a"], r["b"])]
    p4 = frp(live)
    pr(f"  n={len(p4)} mean={_m(p4):.4f} (need <= 0.114; v2 {_m(frp(v2.values())):.4f}) holds={_m(p4) <= 0.114}; apart n={len(frp(apart))} mean {_m(frp(apart)):.4f}; pot n={len(frp(tog))} mean {_m(frp(tog)):.4f}")
    same = [(r, v2[(r["arm"], r["a"], r["b"], r["seed"])]) for r in tog]
    ident = [all(abs(r[k] - o[k]) < 1e-12 for k in ("s_non", "pleasure", "s_off")) and r["left"] == o["left"] and r["exits"] == o["exits"] for r, o in same]
    pr(f"== P5 bit-identity of week-0 pot runs with v2: {sum(ident)} of {len(ident)} identical; week-0 pot flags equal v2: "
       f"{all(r['pot'] == v2[(r['arm'], r['a'], r['b'], r['seed'])]['pot'] for r in live)}")
    pr("== apart households: living arrangement, retries, and who formed a pot later")
    pr("  modes (A, B):", dict(Counter((r["modes"]["A"], r["modes"]["B"]) for r in apart)))
    pr("  retry rounds held:", sum(len(r["retries"]) for r in apart), "; households formed by retry:", sum(1 for r in apart if r["formed_week"] is not None),
       "; weeks:", dict(Counter(r["formed_week"] for r in apart if r["formed_week"] is not None)))
    late = [r for r in apart if r["formed_week"] is not None]
    pr(f"  late-formed (n={len(late)}): dissolved after {_m(r['left'] > 0 for r in late) if late else float('nan'):.3f}; terms:",
       dict(Counter((r['bundle'] or {}).get('stay', None) for r in late)) if late else None)
    for lab, rows in (("apart all 156 weeks", [r for r in apart if r["apart_end"]]), ("apart then formed", late), ("pot at week 0", tog), ("v2 no-pot (cohabiting)", v2n)):
        pr(f"  {lab:24s} n={len(rows):3d} s_non={_m(r['s_non'] for r in rows):.4f} pleasure={_m(r['pleasure'] for r in rows):.4f} fail={_m(r['fail'] for r in rows):.3f}"
           f" wb={_m(r['wb'][x] for r in rows for x in 'AB'):.4f}")
    pr("== cohorts: s_non, fail, pleasure (v2.1 vs v2 floor ON)")
    for coh in ("prs", "ctl"):
        a1 = [r for r in live if r["cohort"] == coh]
        a2 = [r for r in v2.values() if r["cohort"] == coh]
        pr(f"  {coh}: v2.1 s_non={_m(r['s_non'] for r in a1):.4f} fail={_m(r['fail'] for r in a1):.3f} pleasure={_m(r['pleasure'] for r in a1):.4f}"
           f" | v2 s_non={_m(r['s_non'] for r in a2):.4f} fail={_m(r['fail'] for r in a2):.3f} pleasure={_m(r['pleasure'] for r in a2):.4f}")
    pr("== pressing personas' partners s_non (v2.1 / v2)")
    for who in PRESSING_IDS:
        def part(rows):
            return [r["s_non_role"]["B" if r["a"] == who else "A"] for r in rows if who in (r["a"], r["b"])]
        pr(f"  {who:13s} {_m(part(live)):.4f} / {_m(part(v2.values())):.4f}")
    wk = lambda r: "A" if r["outside"][r["a"]] < r["outside"][r["b"]] else "B"
    pr(f"== weaker partner (lower real outside option) lived wellbeing: v2.1 {_m(r['wb'][wk(r)] for r in live):.4f}; v2 {_m(r['wb'][wk(r)] for r in v2.values()):.4f}")
    st = [r["rollout_stats"] for r in live]
    pr("== rollouts per worker process at its last run (max over workers): weeks", max(s["rollout_weeks"] for s in st), "rollouts", max(s["rollouts"] for s in st))
    return live


def examples_v6():
    """Two plain-English agreements per arm (week 0, seed 0, floor on)."""
    ps = _personas()
    base = NG.base_cards(BIND)
    for arm, pairs in (("fair_default", (("p-controller", "p-peacekeeper"), ("p-anchor", "p-host"))),
                       ("wants_first", (("p-anchor", "p-host"), ("p-controller", "p-peacekeeper"))),
                       ("wants_fallback", (("p-freerider", "p-host"), ("p-controller", "p-peacekeeper")))):
        for a, b in pairs:
            res = NG.week0(ps[a], ps[b], arm, 0, base)
            print(f"\n## {arm}: {a} and {b} (seed 0) status={res.status} flagged={res.flagged} floor blocks={len(res.floor_blocks)} "
                  f"inertia={NG.inertia(res.bundle)[0]:.2f}" if res.pot else f"\n## {arm}: {a} and {b} status={res.status}")
            if res.stated:
                print("   stated wants (terms that differ from the fair default):",
                      {k: (v and {t: v[t] for t in NG.TERM_NAMES if v[t] != NG.FAIR_DEFAULT[t]}) for k, v in res.stated.items()})
            if res.cared:
                print("   cares about:", res.cared)
            print("   outside options (real):", {k: round(v, 3) for k, v in res.outside.items()}, "in-pot baseline:", {k: round(v, 3) for k, v in res.baseline.items()})
            for f in res.floor_blocks:
                print("   floor blocked:", {t: f["bundle"][t] for t in NG.TERM_NAMES + ("breach",)}, f["fails"])
            if res.pot:
                diff = {t: res.bundle[t] for t in NG.TERM_NAMES + ("breach",) if res.bundle[t] != NG.FAIR_DEFAULT[t]}
                print("   differs from the fair default in:", diff or "nothing")
                for c in res.cards:
                    print("   -", c.gloss)
                if res.bundle["stay"]:
                    print(f"   - A leaver who breaks the stay commitment forfeits {int(res.bundle['breach'] * 100)} percent of their pooled share.")


def analyze_v6(res=None):
    import numpy as _np
    res = res or json.loads((OUT6 / "results.json").read_text())
    live, imp, v1 = res["live"], res["imposed"], res["v1"]
    PR = PRESSING_IDS
    on = [r for r in live if r["floor"]]
    off = [r for r in live if not r["floor"]]
    A = lambda rs, arm: [r for r in rs if r["arm"] == arm]
    pr = print
    st = [r["rollout_stats"] for r in live]
    pr("== runs:", len(on), "floor ON,", len(off), "floor OFF,", len(imp), "imposed,", len(v1), "v1; seconds", round(res.get("seconds", 0)),
       "; rollout weeks simulated per worker process at its last run (max over workers):", max(s["rollout_weeks"] for s in st), "rollouts", max(s["rollouts"] for s in st),
       "cache hits", max(s["hits"] for s in st))
    pr("== per arm (floor ON): agreements / default stood / no pot / floor-block share / proof rejections / flagged / reviews changed / stay renewals")
    for arm in ARMS:
        rs = A(on, arm)
        revs = [x for r in rs for x in r["reviews"]]
        pr(f"  {arm:15s} n={len(rs)} pot={_m(r['pot'] for r in rs):.3f} stood={_m(r['status'] == 'stood' for r in rs):.3f} nopot={_m(not r['pot'] for r in rs):.3f}"
           f" floor_blocked={_m(bool(r['floor_blocks']) for r in rs):.3f} (blocks {sum(len(r['floor_blocks']) for r in rs)}) proof_rej={sum(len(r['rejections']) for r in rs)}"
           f" flagged={sum(r['flagged'] for r in rs)} reviews={len(revs)} changed={sum(x['changed'] for x in revs)}"
           f" stay_renewed={sum(1 for x in revs if x['stay_renewed'])}/{sum(1 for x in revs if x['stay_renewed'] is not None)}"
           f" review_floor_blocks={sum(x['floor_blocks'] for x in revs)} s_non={_m(r['s_non'] for r in rs):.4f} pleasure={_m(r['pleasure'] for r in rs):.4f} dissolved={_m(r['left'] > 0 for r in rs):.3f}")
    pr("== floor blocks by what they blocked (week 0, floor ON): (exit, stay, breach) ->",
       dict(Counter((f["bundle"]["exit"], f["bundle"]["stay"], f["bundle"]["breach"]) for r in on for f in r["floor_blocks"])))
    pr("== terms agreed per arm (week 0)")
    for arm in ARMS:
        rs = [r for r in A(on, arm) if r["pot"]]
        pr(f"  {arm}:", {t: dict(Counter(r["bundle"][t] for r in rs)) for t in NG.TERM_NAMES + ("breach",)})
    pr("== INERTIA RATE (share of the 7 v1 terms equal to the fair default), agreed bundles, floor ON")
    for arm in ARMS:
        rs = [r for r in A(on, arm) if r["pot"]]
        pr(f"  {arm:15s} n={len(rs)} mean={_m(r['inertia'] for r in rs):.3f} per term:", {t: round(_m(r["same"][t] for r in rs), 2) for t in NG.TERM_NAMES})
    pr("== FIT vs default-identity (inertia >= 0.75, 0.5 to 0.75, < 0.5; floor ON, pot only)")
    for arm in ARMS:
        rs = [r for r in A(on, arm) if r["pot"]]
        for lab, grp in (("inert>=.75", [r for r in rs if r["inertia"] >= 0.75]), ("inert<.5", [r for r in rs if r["inertia"] < 0.5]),
                         ("mid", [r for r in rs if 0.5 <= r["inertia"] < 0.75])):
            pr(f"  {arm:15s} {lab:10s} n={len(grp):3d} pleasure={_m(r['pleasure'] for r in grp):.4f} s_non={_m(r['s_non'] for r in grp):.4f} fail={_m(r['fail'] for r in grp):.3f}"
               f" dissolved={_m(r['left'] > 0 for r in grp):.3f} review_changes={_m(sum(x['changed'] for x in r['reviews']) for r in grp):.2f}")
    pooled = [r for r in on if r["pot"]]
    xs = [r["inertia"] for r in pooled]
    cc = lambda ys: _np.corrcoef(xs, ys)[0, 1] if len(set(xs)) > 1 else float("nan")
    pr(f"  pooled (n={len(pooled)}) corr(inertia, s_non)={cc([r['s_non'] for r in pooled]):+.3f} corr(inertia, pleasure)={cc([r['pleasure'] for r in pooled]):+.3f}"
       f" corr(inertia, dissolved)={cc([float(r['left'] > 0) for r in pooled]):+.3f} corr(inertia, review changes)={cc([float(sum(x['changed'] for x in r['reviews'])) for r in pooled]):+.3f}")
    for coh in ("ctl", "prs"):
        rs = [r for r in pooled if r["cohort"] == coh]
        xc = [r["inertia"] for r in rs]
        pr(f"  cohort {coh} (n={len(rs)}): corr(inertia, s_non)={_np.corrcoef(xc, [r['s_non'] for r in rs])[0, 1]:+.3f} corr(inertia, pleasure)={_np.corrcoef(xc, [r['pleasure'] for r in rs])[0, 1]:+.3f}"
           f"; inert>=.75 n={sum(1 for x in xc if x >= 0.75)} pleasure={_m(r['pleasure'] for r in rs if r['inertia'] >= 0.75):.4f} s_non={_m(r['s_non'] for r in rs if r['inertia'] >= 0.75):.4f};"
           f" inert<.75 n={sum(1 for x in xc if x < 0.75)} pleasure={_m(r['pleasure'] for r in rs if r['inertia'] < 0.75):.4f} s_non={_m(r['s_non'] for r in rs if r['inertia'] < 0.75):.4f}")
    pr("== agreements with the floor OFF (pot formed): ", {arm: round(_m(r["pot"] for r in A(off, arm)), 3) for arm in ARMS}, "ON:", {arm: round(_m(r["pot"] for r in A(on, arm)), 3) for arm in ARMS})
    pr("== flagged consented deals per arm (floor ON): n, s_non, pleasure, dissolved, held weeks, breaches")
    for arm in ARMS:
        rows = [r for r in A(on, arm) if r["pot"] and r["flagged"]]
        pr(f"  {arm:15s} n={len(rows)} s_non={_m(r['s_non'] for r in rows):.4f} pleasure={_m(r['pleasure'] for r in rows):.4f} dissolved={_m(r['left'] > 0 for r in rows):.3f}"
           f" held_weeks={sum(r['stay_held'] for r in rows)} (runs {sum(1 for r in rows if r['stay_held'])}) breaches={sum(r['stay_breaches'] for r in rows)} (runs {sum(1 for r in rows if r['stay_breaches'])}); breach term:",
           dict(Counter(r["bundle"]["breach"] for r in rows)))
    pr("== outside option vs in-pot baseline (week 0, mean over members): outside", f"{_m(v for r in on for v in r['outside'].values()):.3f}", "in-pot default baseline",
       f"{_m(v for r in on for v in r['baseline'].values()):.3f}", "; share of members with outside > baseline:", f"{_m(r['outside'][k] > r['baseline'][k] for r in on for k in r['outside']):.3f}",
       "; best outside is the friend arrangement:", f"{_m(r['outside_detail'][k]['friend'] > r['outside_detail'][k]['alone'] for r in on for k in r['outside_detail']):.3f}")
    pr("== P1 presser gain vs imposed bundle by partner's real outside option (pot, floor ON, all arms)")
    ent = []
    for r in on:
        if r["pot"] and r["cohort"] == "prs":
            for role, d in r["presser_delta"].items():
                oth = r["b"] if role == "A" else r["a"]
                ent.append((r["outside"][oth], d, r["arm"]))
    os_ = sorted(x[0] for x in ent)
    lo, hi = os_[len(os_) // 3], os_[2 * len(os_) // 3]
    top = [d for o, d, _ in ent if o >= hi]
    bot = [d for o, d, _ in ent if o <= lo]
    mid = [d for o, d, _ in ent if lo < o < hi]
    pr(f"  top third (O>={hi:.3f}) n={len(top)} mean delta={_m(top):+.3f}; bottom third (O<={lo:.3f}) n={len(bot)} mean={_m(bot):+.3f}; mid n={len(mid)} {_m(mid):+.3f}; gap={_m(top) - _m(bot):+.3f}"
       f"  => (a) top<=0.10: {_m(top) <= 0.10}  (b) gap<=-0.10: {_m(top) - _m(bot) <= -0.10}")
    for arm in ARMS:
        pr(f"    {arm}: top-third n={len([1 for o, d, a in ent if a == arm and o >= hi])} mean delta={_m([d for o, d, a in ent if a == arm and o >= hi]):+.3f}; all pressers {_m([d for o, d, a in ent if a == arm]):+.3f}")
    pr("== P2 Free-rider's partner non-offsettable level (floor ON)")
    def fr_partner(rows):
        return [r["s_non_role"]["B" if r["a"] == "p-freerider" else "A"] for r in rows if "p-freerider" in (r["a"], r["b"])]
    p2 = fr_partner(on)
    pr(f"  all arms n={len(p2)} mean={_m(p2):.4f} (limit 0.114) holds={_m(p2) <= 0.114};", {arm: round(_m(fr_partner(A(on, arm))), 4) for arm in ARMS},
       f"floor OFF {_m(fr_partner(off)):.4f}; imposed {_m(fr_partner(imp)):.4f}; v1 {_m(fr_partner(v1)):.4f}")
    pr("   free-rider households with taking=allowed:", {arm: sum(1 for r in A(on, arm) if "p-freerider" in (r["a"], r["b"]) and r["pot"] and r["bundle"]["taking"] == "allowed") for arm in ARMS},
       "no pot:", {arm: sum(1 for r in A(on, arm) if "p-freerider" in (r["a"], r["b"]) and not r["pot"]) for arm in ARMS})
    pr("== P3 floor blocks and stay commitments")
    wants = A(on, "wants_first") + A(on, "wants_fallback")
    sh = _m(bool(r["floor_blocks"]) for r in wants)
    pr(f"  (a) wants arms with >=1 floor block: {sh:.3f} (need 0.15) holds={sh >= 0.15}; all arms {_m(bool(r['floor_blocks']) for r in on):.3f}")
    stays = [r for r in on if r["pot"] and r["bundle"]["stay"]]
    held = [r for r in stays if r["stay_held"] > 0]
    pr(f"  (b) runs with a week-0 stay commitment n={len(stays)}; with a held leave attempt {len(held)} = {len(held) / max(1, len(stays)):.3f} (need 0.10, n>=20; v1 1/45)"
       f" holds={len(stays) >= 20 and len(held) / len(stays) >= 0.10}; breaches in {sum(1 for r in stays if r['stay_breaches'])} runs; dissolved {sum(1 for r in stays if r['left'])}")
    pr("   flagged deals (floor cleared, v1 exit check would fail) at week 0:", sum(r["flagged"] for r in on), "; outcomes:")
    for lab, rows in (("flagged", [r for r in on if r["pot"] and r["flagged"]]), ("unflagged pot", [r for r in on if r["pot"] and not r["flagged"]])):
        pr(f"    {lab:14s} n={len(rows)} s_non={_m(r['s_non'] for r in rows):.4f} pleasure={_m(r['pleasure'] for r in rows):.4f} dissolved={_m(r['left'] > 0 for r in rows):.3f}"
           f" held_weeks={sum(r['stay_held'] for r in rows)} breaches={sum(r['stay_breaches'] for r in rows)} fail={_m(r['fail'] for r in rows):.3f}")
    pr("== P4 inertia ordering")
    ir = {arm: _m(r["inertia"] for r in A(on, arm) if r["pot"]) for arm in ARMS}
    ok4 = ir["fair_default"] >= 0.75 and ir["fair_default"] - ir["wants_fallback"] >= 0.10 and ir["wants_fallback"] - ir["wants_first"] >= 0.10
    pr(f"  {({k: round(v, 3) for k, v in ir.items()})} holds={ok4}")
    pr("== P5 default-identical fair-default households vs wants-fallback households")
    fd = [r for r in A(on, "fair_default") if r["pot"] and r["inertia"] >= 0.75]
    wf = A(on, "wants_fallback")
    dp, dn = _m(r["pleasure"] for r in wf) - _m(r["pleasure"] for r in fd), _m(r["s_non"] for r in fd) - _m(r["s_non"] for r in wf)
    pr(f"  FD default-identical n={len(fd)} pleasure={_m(r['pleasure'] for r in fd):.4f} s_non={_m(r['s_non'] for r in fd):.4f}; fallback n={len(wf)} pleasure={_m(r['pleasure'] for r in wf):.4f}"
       f" s_non={_m(r['s_non'] for r in wf):.4f}; pleasure gap {dp:+.4f} (need 0.015), s_non gap {dn:+.4f} (need 0.010) holds={len(fd) >= 20 and dp >= 0.015 and dn >= 0.010}")
    pr("== P6 pressing personas' own lived wellbeing by arm (pleasure - s_off - s_non)")
    def pw(rows):
        return [r["wb"][role] for r in rows if r["cohort"] == "prs" for role, x in (("A", r["a"]), ("B", r["b"])) if x in PR]
    w6 = {arm: _m(pw(A(on, arm))) for arm in ARMS}
    pr(f"  {({k: round(v, 4) for k, v in w6.items()})} wants_first - fair_default = {w6['wants_first'] - w6['fair_default']:+.4f} (need 0.010) holds={w6['wants_first'] - w6['fair_default'] >= 0.010}"
       f"; imposed {_m(pw(imp)):.4f}; v1 {_m(pw(v1)):.4f}")
    pr("== P7 Anchor(A) x Wanderer(B) agreement vs the other 14 control pairings (floor ON, all arms)")
    aw = [r for r in on if (r["a"], r["b"]) == ("p-anchor", "p-wanderer")]
    rate = {}
    for r in on:
        if r["cohort"] == "ctl":
            rate.setdefault((r["a"], r["b"]), []).append(r["pot"])
    oth = [_m(v) for k, v in rate.items() if k != ("p-anchor", "p-wanderer")]
    gap = _m(r["pot"] for r in aw) - _m(oth)
    pr(f"  anchor-wanderer n={len(aw)} pot={_m(r['pot'] for r in aw):.3f}; others mean={_m(oth):.3f}; gap={gap:+.3f} (need <= -0.25) holds={gap <= -0.25};"
       f" lowest pairings {sorted((round(_m(v), 2), k) for k, v in rate.items())[:4]}; by arm:", {arm: round(_m(r['pot'] for r in aw if r['arm'] == arm), 2) for arm in ARMS})
    pr("   agreement by cohort and arm:", {(c, arm): round(_m(r["pot"] for r in A(on, arm) if r["cohort"] == c), 3) for c in ("ctl", "prs") for arm in ARMS})
    pr("== P8 leave events carrying < 26 units out (money + share carried at leaving)")
    def low(rows):
        ev = [e for r in rows for e in r["exits"]]
        return sum(1 for e in ev if e["assets"] < NG.FLOOR) / max(1, len(ev)), len(ev), _m(e["assets"] for e in ev)
    a_on, a_off = low(on), low(off)
    pr(f"  floor ON share<26={a_on[0]:.3f} (events {a_on[1]}, mean assets {a_on[2]:.1f}); floor OFF {a_off[0]:.3f} (events {a_off[1]}, mean {a_off[2]:.1f});"
       f" diff {a_off[0] - a_on[0]:+.3f} (need >=0.05) holds={a_off[0] - a_on[0] >= 0.05}; imposed {low(imp)[0]:.3f}; v1 {low(v1)[0]:.3f}")
    pr("   by arm (ON, OFF):", {arm: (round(low(A(on, arm))[0], 3), round(low(A(off, arm))[0], 3)) for arm in ARMS})
    pr("== floor ON vs OFF vs imposed vs v1: s_non, fail, pleasure, dissolved")
    for coh in (None, "prs", "ctl"):
        for lab, rows in (("floor ON", on), ("floor OFF", off), ("imposed", imp), ("v1", v1)):
            rs = [r for r in rows if coh is None or r["cohort"] == coh]
            pr(f"  {coh or 'all':3s} {lab:9s} n={len(rs):3d} s_non={_m(r['s_non'] for r in rs):.4f} fail={_m(r['fail'] for r in rs):.3f} pleasure={_m(r['pleasure'] for r in rs):.4f}"
               f" dissolved={_m(r['left'] > 0 for r in rs):.3f} taken={_m(r['taken'] for r in rs):.2f}")
    pr("== partners' suffering: s_non of the partner of each pressing persona (floor ON / OFF / imposed / v1) and of the persona itself (ON)")
    for who in PR:
        def part(rows):
            return [r["s_non_role"]["B" if r["a"] == who else "A"] for r in rows if who in (r["a"], r["b"])]
        pr(f"  {who:13s} partner ON {_m(part(on)):.4f} OFF {_m(part(off)):.4f} imposed {_m(part(imp)):.4f} v1 {_m(part(v1)):.4f};"
           f" itself ON {_m(r['s_non_role']['A' if r['a'] == who else 'B'] for r in on if who in (r['a'], r['b'])):.4f}")
    pr("== weaker partner = lower real outside option of the pair: s_non and exits below 26, floor ON vs OFF")
    def weak(r):
        return "A" if r["outside"][r["a"]] < r["outside"][r["b"]] else "B"
    pr(f"  s_non ON {_m(r['s_non_role'][weak(r)] for r in on):.4f} OFF {_m(r['s_non_role'][weak(r)] for r in off):.4f}")
    for lab, rows in (("ON", on), ("OFF", off)):
        ev = [e for r in rows for e in r["exits"] if e["role"] == weak(r)]
        pr(f"  {lab}: weaker partner's exits n={len(ev)} below 26: {_m(e['assets'] < NG.FLOOR for e in ev):.3f} mean assets {_m(e['assets'] for e in ev):.1f}")
    return res


if __name__ == "__main__" and "--negotiate-v2-1" in sys.argv:
    if "--analyze" in sys.argv:
        analyze_v61()
    elif "--pilot" in sys.argv:
        analyze_v61(main_v61(pilot=True, seeds=(0,)))
    else:
        analyze_v61(main_v61())
    sys.exit(0)


if __name__ == "__main__" and "--negotiate-v2" in sys.argv:
    if "--examples" in sys.argv:
        examples_v6()
    elif "--analyze" in sys.argv:
        analyze_v6()
    elif "--pilot" in sys.argv:
        analyze_v6(main_v6(pilot=True, seeds=(0,)))
    else:
        analyze_v6(main_v6())
    sys.exit(0)


if __name__ == "__main__" and "--negotiate" in sys.argv:
    if "--examples" in sys.argv:
        examples_v5()
    elif "--analyze" in sys.argv:
        analyze_v5()
    else:
        analyze_v5(dict(zip(("live", "imposed", "tri", "sweep"), main_v5())))
    sys.exit(0)


if __name__ == "__main__" and "--seed-v2" in sys.argv:
    main_v4()
    sys.exit(0)


if __name__ == "__main__":
    if "--v3" in sys.argv:
        main_v3()
    elif "--v1" in sys.argv:
        main_v1(ladder="--no-ladder" not in sys.argv)
    else:
        main_v2(ladder="--no-ladder" not in sys.argv)
