"""Run records and the one-file HTML report.

execute(...)       run the fishery under a spec and gather everything the report needs.
build_report(...)  write runs/<run_id>/report.html (self-contained) and trace.json.
load_record(...)   read trace.json back, so `mar report <run_id>` can rebuild with no re-run.

Thin glue over fishery, gate, oracle, miner and viz. No LLM, no network.
"""
import json
from dataclasses import dataclass, field, asdict
from functools import lru_cache
from html import escape
from pathlib import Path

from . import oracle, viz
from .cards import load_cards, make_card
from .fishery import Run, run_fishery
from .gate import Gate
from .miner import action_class, dejure_edges, diff, mine, phase, pool_bucket
from .mocks import Compliant, Explorer, Exploiter

AGENT_KINDS = {"exploiter": Exploiter, "compliant": Compliant, "explorer": Explorer}
OPS = {"gt": ">", "ge": ">=", "lt": "<", "le": "<=", "eq": "="}
MINE_SEEDS = range(10)  # ASSUMED: lived rules are mined from 10 gated explorer runs, 4 explorers each


@dataclass
class RunRecord:
    run_id: str
    spec_name: str
    agents: list
    months: int
    seed: int
    cards: list                      # written cards, including any patch cards
    patch_ids: list = field(default_factory=list)
    trace: list = field(default_factory=list)
    outcomes: list = field(default_factory=list)
    rounds: list = field(default_factory=list)    # seam curve: [{"round", "seams", ...}]
    history: list = field(default_factory=list)   # loop: per-round notes and stories
    checks: list = field(default_factory=list)    # patch_check verdicts, if run
    analysis: dict = field(default_factory=dict)  # lived rules and edges
    kind: str = "run"

    def as_run(self) -> Run:
        return Run(trace=self.trace, outcomes=self.outcomes)


def parse_agents(text: str) -> list:
    """'exploiter,compliant' or 'exploiter*4' -> ['exploiter', 'compliant'] / four exploiters."""
    names = []
    for part in (p.strip() for p in text.split(",") if p.strip()):
        name, _, count = part.partition("*")
        if name not in AGENT_KINDS:
            raise ValueError(f"unknown agent kind {name!r}; choose from {sorted(AGENT_KINDS)}")
        names += [name] * (int(count) if count else 1)
    if not names:
        raise ValueError("no agents given")
    return names


def agents_slug(names) -> str:
    """['exploiter']*4 -> 'exploiterx4'; mixed teams keep order: 'exploiter-compliant'."""
    out, prev = [], None
    for n in names:
        if out and prev == n:
            out[-1][1] += 1
        else:
            out.append([n, 1])
        prev = n
    return "-".join(n if k == 1 else f"{n}x{k}" for n, k in out)


def make_agents(names):
    return [AGENT_KINDS[n]() for n in names]


@lru_cache(maxsize=16)
def _analyse(card_yaml: tuple) -> dict:
    import yaml
    cards = [make_card(yaml.safe_load(y)) for y in card_yaml]
    rows = []
    for s in MINE_SEEDS:
        rows += run_fishery([Explorer() for _ in range(4)], Gate(cards), seed=s).trace
    mined = mine(rows)
    d = diff(cards, mined)
    return {"bounds": d["bounds"], "jure_edges": sorted(map(list, dejure_edges(cards))),
            "mined_edges": sorted(map(list, mined["edges"])), "mined_cards": [asdict(c) for c in mined["cards"]],
            "n_rows": mined["n_rows"]}


def analyse(cards) -> dict:
    return json.loads(json.dumps(_analyse(tuple(c.to_yaml() for c in cards))))


def execute(spec, agent_names, months=6, seed=0, patch_cards=(), run_id=None) -> RunRecord:
    base = load_cards(spec)
    cards = base + list(patch_cards)
    run = run_fishery(make_agents(agent_names), Gate(cards), months=months, seed=seed)
    seam = oracle.is_seam(run.trace, run.outcomes)
    spec_name = Path(spec).name
    rid = run_id or f"{spec_name}-{agents_slug(agent_names)}-m{months}-s{seed}" + ("-patched" if patch_cards else "")
    rec = RunRecord(rid, spec_name, list(agent_names), months, seed, cards, [c.id for c in patch_cards],
                    run.trace, run.outcomes, analysis=analyse(cards))
    rec.rounds = [{"round": len(patch_cards), "seams": int(seam), "note": "this run only"}]
    return rec


# ---- plain English -------------------------------------------------------------------------

def verdict(rec) -> tuple:
    """-> (kind, sentence). kind: ok | seam | fail."""
    j = oracle.judge(rec.outcomes)
    blocked = sum(1 for r in rec.trace if not r["allowed"])
    if j["ok"]:
        return "ok", (f"The outcome check passed: the lake never collapsed, nobody starved and catches were "
                      f"fairly even. The gate blocked {blocked} of {len(rec.trace)} proposals.")
    parts = []
    for f in j["findings"]:
        if f["kind"] == "collapse":
            parts.append(f"Pool collapsed in month {f['month']}.")
        elif f["kind"] == "starvation":
            parts.append(f"A fisher starved ({f['detail']}).")
        else:
            parts.append(f"Catches were very unequal ({f['detail']}).")
    if oracle.is_seam(rec.trace, rec.outcomes):
        impossible = [r for r in rec.trace if not r["allowed"] and r["proposed"] > r["pool_before"]]
        if blocked and len(impossible) == blocked:
            parts.append(f"The gate blocked {blocked} proposals, but only ones asking for more fish than the pool "
                         "held. Every other action passed the gate, so this is a seam.")
        elif blocked:
            parts.append(f"The gate blocked {blocked} proposals; every action it let through passed the rules, "
                         "so this is a seam.")
        else:
            parts.append("Every action passed the gate, so this is a seam.")
        return "seam", " ".join(parts)
    parts.append(f"The gate blocked {blocked} proposals but the outcome still failed, "
                 "so the rules held back some actions and still missed the harm.")
    return "fail", " ".join(parts)


def _fallback_story(rec):
    j = oracle.judge(rec.outcomes)
    if not j["findings"]:
        return ["No seam in this run: the outcome check passed."]
    if oracle.is_seam(rec.trace, rec.outcomes):
        return [f"Seam: every executed action was allowed by the written rules, yet {f['detail']}." for f in j["findings"]]
    return [f"The outcome failed ({f['detail']}) although the gate blocked some proposals." for f in j["findings"]]


def stories(rec) -> list:
    """-> [(title, [paragraph, ...])]. Uses mar.english.explain when available."""
    out = []
    try:
        from .english import explain  # lazy: another module owns it and may not exist
    except ImportError:
        explain = None
    if explain is None:
        out.append(("This run", _fallback_story(rec)))
    else:
        try:
            out.append(("This run", explain(rec.as_run(), rec.cards).split("\n")))
        except Exception:  # a story must never break the report
            out.append(("This run", _fallback_story(rec)))
    for h in rec.history:
        if h.get("story"):
            out.append((f"Round {h['round']}: the seam that was found", h["story"].split("\n")))
    for v in rec.checks:
        if v["verdict"] == "fail":
            text = None
            if explain is not None:
                try:
                    text = explain(v, rec.cards)
                except Exception:
                    text = None
            out.append((f"Counterexample: check {v['check']}", [text or f"{v['check']} fails: {v['detail']}"]))
    return out


def cond_text(card) -> str:
    return " and ".join(f"{p['expr']} {OPS[p['op']]} {p['value']}" for p in card["conditions"]) or "always"


def sanction_text(s) -> str:
    return "none" if not s else f"{s['kind']} for {s['duration_months']} month(s), by {s.get('sanctioner', '?')}"


# ---- trace.json ----------------------------------------------------------------------------

def write_trace(rec, out_dir) -> Path:
    d = Path(out_dir) / rec.run_id
    d.mkdir(parents=True, exist_ok=True)
    data = asdict(rec)
    p = d / "trace.json"
    p.write_text(json.dumps(data, indent=1, default=list))
    return p


def load_record(run_id, out_dir) -> RunRecord:
    data = json.loads((Path(out_dir) / run_id / "trace.json").read_text())
    data["cards"] = [make_card(c) for c in data["cards"]]
    return RunRecord(**data)


# ---- HTML ----------------------------------------------------------------------------------

CSS = """
:root{color-scheme:light;--bg:#fcfcfb;--card:#f5f4f1;--ink:#0b0b0b;--ink2:#52514e;--line:#dddcd7;--accent:#2a78d6;
--on-accent:#fff;--warn-bg:#fdecc8;--warn-ink:#5a3b00;--bad-bg:#fbdcdc;--bad-ink:#6b1111;--good-bg:#d9f0d9;--good-ink:#0b4a0b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#1a1a19;--card:#242423;--ink:#f0efec;
--ink2:#c3c2b7;--line:#3b3b38;--accent:#3987e5;--on-accent:#0b0b0b;--warn-bg:#4a3500;--warn-ink:#ffe2a0;--bad-bg:#561b1b;
--bad-ink:#ffd2d2;--good-bg:#17421a;--good-ink:#c9f0c9}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#1a1a19;--card:#242423;--ink:#f0efec;--ink2:#c3c2b7;--line:#3b3b38;
--accent:#3987e5;--on-accent:#0b0b0b;--warn-bg:#4a3500;--warn-ink:#ffe2a0;--bad-bg:#561b1b;--bad-ink:#ffd2d2;
--good-bg:#17421a;--good-ink:#c9f0c9}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:860px;margin:0 auto;padding:20px 16px 56px}
h1{font-size:1.45rem;margin:.2em 0 .1em;overflow-wrap:anywhere}
h2{font-size:1.15rem;margin:0 0 .3em}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:16px 0}
.meta{color:var(--ink2);margin:0 0 12px;font-size:.92rem}
.verdict{border-radius:10px;padding:12px 14px;font-weight:600;margin:10px 0 0}
.verdict.seam,.verdict.fail{background:var(--bad-bg);color:var(--bad-ink)}
.verdict.ok{background:var(--good-bg);color:var(--good-ink)}
.note{color:var(--ink2);font-size:.9rem;margin:.2em 0 .8em}
.calib{background:var(--warn-bg);color:var(--warn-ink);border-radius:8px;padding:8px 10px;font-size:.9rem;margin:.4em 0 .8em}
.t-dark{display:none}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .t-light{display:none}
:root:not([data-theme="light"]) .t-dark{display:block}}
:root[data-theme="dark"] .t-light{display:none}:root[data-theme="dark"] .t-dark{display:block}
svg text{font-family:inherit!important}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.88rem}
th,td{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--line)}
th{color:var(--ink2);font-weight:600}
.cards td:first-child{font-weight:700;white-space:nowrap}
.rule{border:1px solid var(--line);border-radius:8px;padding:8px 12px;margin:8px 0;background:var(--bg)}.rid{font-weight:700}.rule p{margin:.3em 0}.rule dl{display:grid;grid-template-columns:auto 1fr;gap:2px 12px;margin:0;font-size:.85rem;color:var(--ink2)}.rule dt{font-weight:600}.rule dd{margin:0;overflow-wrap:anywhere}
.diff{background:var(--warn-bg);color:var(--warn-ink);font-weight:700}
.tag{display:inline-block;border:1px solid var(--ink2);border-radius:6px;padding:0 6px;font-size:.78rem;margin-left:6px}
details{margin-top:8px}summary{cursor:pointer;color:var(--ink2)}
.story{margin:.2em 0 1em}.story p{margin:.25em 0}
.key{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.85rem;color:var(--ink2);margin:6px 0}
.sw{display:inline-block;width:22px;height:14px;border-radius:4px;vertical-align:-2px;margin-right:5px;border:1.5px solid var(--ink)}
.sw.used{background:var(--accent)}.sw.blocked{border-style:dashed;border-color:var(--ink2)}
.sm-node{fill:var(--bg);stroke:var(--line);stroke-width:1.5}
.sm-title,.sm-axis{fill:var(--ink2);font-size:12px}.sm-count{fill:var(--ink);font-size:12px;font-weight:700;paint-order:stroke;stroke:var(--card);stroke-width:4px}
.sm-edge{fill:none;stroke:var(--ink2);stroke-width:1.6}.sm-head{fill:var(--ink2)}
.sm-chip text{font-size:12px;fill:var(--ink)}.sm-chip rect{fill:none;stroke:var(--ink);stroke-width:1.5}
.sm-used rect{fill:var(--accent);stroke:var(--accent)}.sm-used text{fill:var(--on-accent);font-weight:700}
.sm-blocked rect{stroke:var(--ink2);stroke-dasharray:3 2}.sm-blocked text{fill:var(--ink2);text-decoration:line-through}
"""


def _table(head, rows, cls=""):
    th = "".join(f"<th>{escape(str(h))}</th>" for h in head)
    body = "".join("<tr>" + "".join(c if c.startswith("<td") else f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="scroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def _both(fn, *a):
    return f'<div class="t-light">{fn(*a, "light")}</div><div class="t-dark">{fn(*a, "dark")}</div>'


def moves_of(rec) -> dict:
    mv, last = {}, {}
    for r in rec.trace:
        if not r["executed"]:
            continue
        a = (pool_bucket(r["pool_before"]), phase(r["month_total_before"]))
        taken = r["pool_before"] - r["pool_after"]
        b = (pool_bucket(r["pool_after"]), phase(r["month_total_before"] + taken))
        mv[(a, b)] = mv.get((a, b), 0) + 1
        last[r["month"]] = b
    for o in rec.outcomes:
        if o["month"] in last:
            a, b = last[o["month"]], (pool_bucket(o["pool_end"]), "untouched")
            mv[(a, b)] = mv.get((a, b), 0) + 1
    return mv


def used_edges_of(rec) -> set:
    return {(pool_bucket(r["pool_before"]), phase(r["month_total_before"]), action_class(r["proposed"]))
            for r in rec.trace if r["executed"]}


def _sec_header(rec):
    kind, text = verdict(rec)
    label = {"ok": "OK", "seam": "SEAM", "fail": "FAILED"}[kind]
    agents = ", ".join(f"Fisher {i}: {n}" for i, n in enumerate(rec.agents))
    n_blocked = sum(1 for r in rec.trace if not r["allowed"])
    return (f'<header><h1>Run {escape(rec.run_id)}</h1><p class="meta">Spec: {escape(rec.spec_name)} '
            f'({len(rec.cards)} rules{", patched with " + escape(", ".join(rec.patch_ids)) if rec.patch_ids else ""}) '
            f'&middot; Agents: {escape(agents)} &middot; {rec.months} months &middot; seed {rec.seed} '
            f'&middot; {len(rec.trace)} proposals, {n_blocked} blocked</p>'
            f'<p class="verdict {kind}"><span class="tag">{label}</span> {escape(text)}</p></header>')


def _sec_pool(rec):
    rows = []
    for o in rec.outcomes:
        b = sum(1 for r in rec.trace if r["month"] == o["month"] and not r["allowed"])
        rows.append([str(o["month"])] + [str(c) for c in o["catch"]] + [str(o["pool_end"]), str(b)])
    head = ["Month"] + [f"Fisher {i} catch" for i in range(len(rec.agents))] + ["Pool at month end", "Blocked"]
    return ('<section id="pool"><h2>Pool over time</h2><p class="note">Bars: fish each agent caught that month. '
            'Line: pool at month end, after regrowth. Dashed line: the collapse line (pool below 5). '
            'The strip under the chart counts proposals the gate blocked.</p>'
            + _both(viz.pool_chart, rec.outcomes, rec.trace, rec.agents)
            + "<details><summary>Table view</summary>" + _table(head, rows) + "</details></section>")


def _sec_seam(rec):
    rounds = rec.rounds or [{"round": 0, "seams": 0}]
    hist = ""
    if rec.history:
        hist = "<details open><summary>What happened each round</summary>" + _table(
            ["Round", "Seams", "What happened"], [[str(h["round"]), str(h["seams"]), escape(h["note"])]
                                                  for h in rec.history]) + "</details>"
    return ('<section id="seams"><h2>Seam curve</h2>'
            '<p class="calib">Instrument calibration with scripted agents. One planted scenario, not a '
            'convergence result: it checks that the loop can find a seam and close it, nothing more.</p>'
            '<p class="note">A seam is a run that passes the gate but fails the outcome check. Seams found per '
            'refinement round; round 0 is the rules as first written.</p>'
            + _both(viz.seam_chart, rounds) + hist + "</section>")


def _sec_rules(rec):
    a = rec.analysis
    patch = set(rec.patch_ids)
    written = "".join(
        f'<div class="rule"><div class="rid">{escape(c.id)}<span class="tag">{c.deontic.replace("_", " ")}</span>'
        f'<span class="tag">{escape(c.aim)}</span>'
        + ('<span class="tag">added by patch</span>' if c.id in patch else "") + "</div>"
        f"<p>{escape(c.gloss)}</p><dl><dt>Conditions</dt><dd>{escape(cond_text(asdict(c)))}</dd>"
        f"<dt>Or else</dt><dd>{escape(sanction_text(c.or_else))}</dd><dt>Source</dt><dd>{escape(c.source)}</dd></dl></div>"
        for c in rec.cards)
    brow = []
    for b in a["bounds"]:
        name = b["bound"].replace("_", " ")
        w = "none" if b["written"] is None else b["written"]
        m = "none" if b["mined"] is None else b["mined"]
        brow.append([escape(name), f"<td>{w}</td>", f"<td>{m}</td>",
                     '<td>same</td>' if b["equal"] else '<td class="diff">DIFFERENT</td>'])
    lived = _table(["Bound", "Written", "Lived", "Match"], brow)
    mined = "".join(f"<li><strong>{escape(c['id'])}</strong>: {escape(c['gloss'])}</li>" for c in a["mined_cards"])
    jure, seen = set(map(tuple, a["jure_edges"])), set(map(tuple, a["mined_edges"]))
    never = sorted(jure - seen)
    extra = sorted(seen - jure)
    return ('<section id="rules"><h2>Rules: written vs lived</h2>'
            '<p class="note">Written rules gate the agents. Lived rules are mined from gated explorer traces '
            f'({a["n_rows"]} proposals over {len(MINE_SEEDS)} seeds) without looking at the card ids. A row that '
            'differs is a seam or an emergent norm.</p><h3>Written</h3>' + written + '<h3>Lived (mined)</h3><ul>'
            + mined + "</ul>" + lived +
            f'<p class="note">Edges (state and action class) the written rules permit: {len(jure)}. Seen in '
            f'exploration: {len(seen)}. Written but never seen: {len(never)}. Seen but not written: '
            f'{len(extra)}{" (lived rules the cards do not state)" if extra else ""}.</p></section>')


def _sec_machine(rec):
    a = rec.analysis
    used = used_edges_of(rec)
    jure = set(map(tuple, a["jure_edges"]))
    svg = viz.state_machine_svg(jure, used, moves_of(rec))
    status = viz.edge_status(jure, used)
    rows = []
    for p in viz.POOLS:
        for ph in viz.PHASES:
            def pick(s):
                return ", ".join(viz.CLASS_LABEL[c] for c in viz.CLASSES if status[(p, ph, c)] == s) or "-"
            rows.append([f"pool {p}, month total {ph}", pick("used"), pick("open"), pick("blocked")])
    n_used, n_open = sum(v == "used" for v in status.values()), sum(v == "open" for v in status.values())
    return ('<section id="machine"><h2>State machine</h2><p class="note">Nine lake states (pool level by month '
            'total so far). Each box lists five action sizes, in fish. Arrows show moves between states this run '
            f'took, with counts. {n_used} edges used, {n_open} permitted but never used by these agents.</p>'
            '<div class="key"><span><i class="sw used"></i>taken in this run</span>'
            '<span><i class="sw"></i>permitted, never taken</span>'
            '<span><i class="sw blocked"></i>blocked by the written rules</span></div>'
            f'<div class="scroll">{svg}</div><details><summary>Table view</summary>'
            + _table(["State", "Used", "Permitted, unused", "Blocked"], rows) + "</details></section>")


def _sec_stories(rec):
    parts = []
    for title, paras in stories(rec):
        parts.append(f'<h3>{escape(title)}</h3><div class="story">' + "".join(f"<p>{escape(p)}</p>" for p in paras if p)
                     + "</div>")
    return '<section id="stories"><h2>Stories</h2>' + "".join(parts) + "</section>"


def build_report(rec, out_dir) -> Path:
    """Write <out_dir>/<run_id>/report.html and trace.json; return the report path."""
    d = Path(out_dir) / rec.run_id
    d.mkdir(parents=True, exist_ok=True)
    write_trace(rec, out_dir)
    body = "".join(f(rec) for f in (_sec_header, _sec_pool, _sec_seam, _sec_rules, _sec_machine, _sec_stories))
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>mar run {escape(rec.run_id)}</title><style>{CSS}</style></head><body><main>{body}</main></body></html>')
    p = d / "report.html"
    p.write_text(html)
    return p
