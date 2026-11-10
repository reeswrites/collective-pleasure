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


def main(ladder=True):
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


if __name__ == "__main__":
    main(ladder="--no-ladder" not in sys.argv)
