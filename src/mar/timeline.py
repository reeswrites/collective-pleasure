"""`mar timeline`: one self-contained HTML page of how the project got here.

Merges, in time order: questions, decisions, changes, runs and git commits. Written to
<runs_dir>/timeline.html (ignored; regenerable from committed sources). Same offline rules as
report.py: inline CSS and SVG, no scripts, no network, light and dark, readable at phone width.
Date-only entries (decisions, and backfilled paraphrases) sort to the end of their day (ASSUMED).
"""
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from . import log as explog
from .report import CSS

KINDS = ("Question", "Decision", "Change", "Run", "Commit")
PAL = {"Question": ("#2a78d6", "#3987e5"), "Decision": ("#6250d6", "#9085e9"), "Change": ("#eb6834", "#d95926"),
       "Run": ("#1baf7a", "#199e70"), "Commit": ("#8a8984", "#a09f98")}  # ASSUMED: reuse viz categorical hues

def _vars(i, prefix=""):
    return "".join(f"{prefix}.k-{k}{{--kc:{c[i]}}}" for k, c in PAL.items())


EXTRA_CSS = (_vars(0) + "@media (prefers-color-scheme:dark){" + _vars(1, ':root:not([data-theme="light"]) ') + "}"
             + _vars(1, ':root[data-theme="dark"] ')) + """
.badge{display:inline-block;border:1.5px solid var(--kc);color:var(--ink);border-radius:6px;padding:0 7px;
font-size:.78rem;font-weight:700;margin-right:8px}
.badge::before{content:"";display:inline-block;width:8px;height:8px;background:var(--kc);border-radius:2px;margin-right:5px}
.ev{border-left:4px solid var(--kc);padding:4px 0 4px 12px;margin:10px 0}
.ev .when{color:var(--ink2);font-size:.85rem}.ev p{margin:.25em 0;overflow-wrap:anywhere}
.ev a{color:var(--accent);overflow-wrap:anywhere}.ev blockquote{margin:.3em 0;padding:0 0 0 10px;border-left:2px solid var(--line)}
.bar{fill:var(--kc)}.nwim{background:var(--bad-bg);color:var(--bad-ink);border-radius:6px;padding:0 6px;font-size:.78rem;margin-left:6px}
.sum{display:flex;flex-wrap:wrap;gap:6px 16px;margin:.4em 0}
"""


def _dt(ts: str) -> datetime:
    d = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _end_of_day(day: str) -> datetime:
    return datetime.fromisoformat(day + "T23:59:59+00:00")


def _decisions(repo: Path):
    for p in sorted((repo / "docs" / "decisions").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        title = (re.search(r"^# (.+)$", text, re.M) or [None, p.stem])[1]
        status = (re.search(r"^Status:\s*(.+)$", text, re.M) or [None, ""])[1]
        m = re.search(r"(\d{4}-\d{2}-\d{2})", status)
        yield {"kind": "Decision", "when": _end_of_day(m.group(1)) if m else None, "date_only": True,
               "title": title, "text": status, "src": p}


def _commits(repo: Path):
    try:
        out = subprocess.run(["git", "log", "--format=%h%x09%aI%x09%s"], cwd=repo, capture_output=True, text=True,
                             check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return
    for line in out.splitlines():
        h, ts, subj = line.split("\t", 2)
        yield {"kind": "Commit", "when": _dt(ts), "title": subj, "text": h, "src": None}


def collect(exp_dir, runs_dir=None, repo: Path = explog.REPO) -> list:
    exp = Path(exp_dir)
    ev = []
    for r in explog.read_rows(exp / explog.QUESTIONS_NAME):
        date_only = r["paraphrase"]
        when = _end_of_day(r["timestamp"][:10]) if date_only else _dt(r["timestamp"])
        ev.append({"kind": "Question", "when": when, "date_only": date_only, "quote": r["quote"],
                   "title": r["topic"] or "", "text": r["text"] or "", "paraphrase": r["paraphrase"],
                   "backfilled": r["backfilled"], "led_to": r["led_to"], "src": exp / explog.QUESTIONS_NAME})
    ev += list(_decisions(repo))
    for r in explog.read_rows(exp / explog.CHANGES_NAME):
        ev.append({"kind": "Change", "when": _dt(r["timestamp"]), "quote": r["quote"], "title": r["kind"],
                   "text": r["reason"], "nwim": r["not_what_i_meant"], "src": exp / explog.CHANGES_NAME})
    for r in explog.read_rows(exp / explog.LOG_NAME):
        ev.append({"kind": "Run", "when": _dt(r["timestamp"]), "title": r["run_id"], "text": r["verdict"],
                   "note": r.get("note"), "src": Path(r["report"]) if r.get("report") else exp / explog.LOG_NAME})
    ev += list(_commits(repo))
    ev = [e for e in ev if e["when"] is not None]
    ev.sort(key=lambda e: (e["when"], KINDS.index(e["kind"])))
    return ev


def _link(src, out_dir: Path) -> str:
    if not src:
        return ""
    src = Path(src)
    if not src.is_absolute():
        src = Path.cwd() / src
    rel = os.path.relpath(src, out_dir)
    return f'<a href="{escape(rel)}">{escape(src.name)}</a>'


def _entry(e, out_dir) -> str:
    k = e["kind"]
    when = e["when"].strftime("%Y-%m-%d") if e.get("date_only") else e["when"].strftime("%Y-%m-%d %H:%M UTC")
    flags = ""
    if e.get("backfilled"):
        flags += '<span class="tag">backfilled</span>'
    if e.get("paraphrase"):
        flags += '<span class="tag">paraphrase</span>'
    if e.get("nwim"):
        flags += '<span class="nwim">not what I meant</span>'
    body = ""
    if e.get("quote"):
        body += f"<blockquote>{escape(e['quote'])}</blockquote>"
    if e["title"]:
        body += f"<p><b>{escape(e['title'])}</b></p>"
    if e.get("text"):
        body += f"<p>{escape(e['text'])}</p>"
    if e.get("note"):
        body += f"<p>Note: {escape(e['note'])}</p>"
    if e.get("led_to"):
        body += f"<p>Led to: {escape(', '.join(e['led_to']))}</p>"
    link = _link(e.get("src"), out_dir)
    body += f"<p>Source: {link}</p>" if link else "<p>Source: git log</p>"
    return (f'<div class="ev k-{k}"><div class="when"><span class="badge">{k}</span>{escape(when)}{flags}</div>'
            f"{body}</div>")


def _chart(ev) -> str:
    days = sorted({e["when"].strftime("%Y-%m-%d") for e in ev})
    per = {d: Counter(e["kind"] for e in ev if e["when"].strftime("%Y-%m-%d") == d) for d in days}
    peak = max((sum(c.values()) for c in per.values()), default=1)
    bw, gap, h, left = 46, 14, 140, 34
    width = left + len(days) * (bw + gap) + 10
    parts = [f'<svg viewBox="0 0 {width} {h + 40}" role="img" aria-label="Entries per day by kind" '
             f'width="{width}" style="max-width:none">']
    for i, d in enumerate(days):
        x, y = left + i * (bw + gap), h
        for k in KINDS:
            n = per[d][k]
            if n:
                bh = n / peak * (h - 10)
                y -= bh
                parts.append(f'<rect class="bar k-{k}" x="{x}" y="{y:.1f}" width="{bw}" height="{bh:.1f}">'
                             f"<title>{d} {k}: {n}</title></rect>")
        parts.append(f'<text class="sm-axis" x="{x + bw / 2}" y="{h + 16}" text-anchor="middle">{d[5:]}</text>')
    parts.append(f'<text class="sm-axis" x="2" y="14">{peak}</text></svg>')
    rows = "".join(f"<tr><td>{d}</td>" + "".join(f"<td>{per[d][k]}</td>" for k in KINDS) + "</tr>" for d in days)
    table = ("<details><summary>Table view</summary><div class=\"scroll\"><table><tr><th>Day</th>"
             + "".join(f"<th>{k}</th>" for k in KINDS) + f"</tr>{rows}</table></div></details>")
    key = '<div class="key">' + "".join(f'<span class="k-{k}"><span class="sw" style="background:var(--kc)"></span>{k}</span>'
                                       for k in KINDS) + "</div>"
    return f'<div class="scroll">{"".join(parts)}</div>{key}{table}'


def build_timeline(exp_dir, runs_dir="runs", repo: Path = explog.REPO):
    ev = collect(exp_dir, runs_dir, repo)
    out_dir = Path(runs_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = Counter({k: 0 for k in KINDS})
    counts.update(e["kind"] for e in ev)
    span = (f"{ev[0]['when']:%Y-%m-%d} to {ev[-1]['when']:%Y-%m-%d}" if ev else "no entries")
    summ = '<div class="sum">' + "".join(
        f'<span class="k-{k}"><span class="badge">{k}</span>{counts[k]}</span>' for k in KINDS) + "</div>"
    body = (f'<section><h1>How we got here</h1><p class="meta">{escape(span)}. Questions, decisions, changes, runs '
            f"and commits in time order. Date-only entries sit at the end of their day. Built from committed "
            f"sources by <code>mar timeline</code>.</p>{summ}</section>"
            f'<section><h2>Entries per day</h2>{_chart(ev)}</section>'
            f'<section><h2>Timeline</h2>{"".join(_entry(e, out_dir.resolve()) for e in ev)}</section>')
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><title>mar timeline</title>'
            f"<style>{CSS}{EXTRA_CSS}</style></head><body><main>{body}</main></body></html>")
    p = out_dir / "timeline.html"
    p.write_text(html, encoding="utf-8")
    return p, dict(counts)
