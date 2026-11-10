"""Experiment log and change log. Append-only JSON lines, committed to git.

experiments/log.jsonl      one line per `mar run` or `mar loop`.
experiments/changes.jsonl  one line per rule or oracle change.
experiments/questions.jsonl one line per author question that redirected the project or opened a line of curiosity.
experiments/kept/<run_id>/ trace.json and report.html copied by `mar keep`.

Nothing here ever rewrites an earlier line: files are opened in append mode only.
Full traces stay in runs/ (ignored). No LLM, no network.
"""
import difflib
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import oracle

REPO = Path(__file__).resolve().parents[2]
LOG_NAME = "log.jsonl"
CHANGES_NAME = "changes.jsonl"
QUESTIONS_NAME = "questions.jsonl"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_commit() -> str | None:
    """HEAD of the repo, with '+dirty' if the working tree has uncommitted changes. None if git is unavailable."""
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, check=True)
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True,
                               check=True).stdout.strip()
        return head.stdout.strip() + ("+dirty" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return None


def cards_hash(cards) -> str:
    """Content hash of the cards used (written plus patch), independent of file order."""
    blob = json.dumps(sorted((c.to_yaml() for c in cards)), sort_keys=True)
    return "sha256:" + hashlib.sha256(blob.encode()).hexdigest()[:16]


def oracle_version() -> str:
    """ASSUMED: oracle version = hash of oracle.py source plus its three thresholds. Replace with a named
    version when loop (b) starts freezing oracle versions."""
    src = Path(oracle.__file__).read_bytes()
    thr = f"{oracle.COLLAPSE_BELOW},{oracle.STARVE_MONTHS},{oracle.GINI_ABOVE}".encode()
    return "sha256:" + hashlib.sha256(src + thr).hexdigest()[:16]


def _append(path, row: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:  # append only
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_rows(path) -> list:
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def log_run(exp_dir, rec, verdict_text, report_path, trace_path, spec, note=None,
            model=None, cost_usd=None) -> dict:
    row = {"run_id": rec.run_id, "kind": rec.kind, "timestamp": now_utc(), "git_commit": git_commit(),
           "spec": str(spec), "cards_hash": cards_hash(rec.cards), "oracle_version": oracle_version(),
           "agents": list(rec.agents), "months": rec.months, "seed": rec.seed,
           "model": model, "cost_usd": cost_usd, "verdict": verdict_text,
           "seams": sum(r["seams"] for r in rec.rounds), "report": str(report_path),
           "trace": str(trace_path), "note": note}
    _append(Path(exp_dir) / LOG_NAME, row)
    return row


def log_table(rows) -> str:
    if not rows:
        return "No log entries yet."
    head = ("when (UTC)", "run", "seams", "note")
    body = [(r["timestamp"].replace("T", " ").rstrip("Z"), r["run_id"], str(r["seams"]), r.get("note") or "")
            for r in rows]
    w = [max(len(h), *(len(b[i]) for b in body)) for i, h in enumerate(head)]
    fmt = "  ".join(f"{{:<{x}}}" for x in w)
    return "\n".join([fmt.format(*head), fmt.format(*("-" * x for x in w))] + [fmt.format(*b) for b in body])


def log_detail(r) -> str:
    order = ("run_id", "kind", "timestamp", "git_commit", "spec", "cards_hash", "oracle_version", "agents",
             "months", "seed", "model", "cost_usd", "seams", "verdict", "report", "trace", "note")
    return "\n".join(f"{k}: {r.get(k)}" for k in order)


def keep(exp_dir, runs_dir, run_id) -> Path:
    src = Path(runs_dir) / run_id
    files = [src / "trace.json", src / "report.html"]
    missing = [f.name for f in files if not f.exists()]
    if missing:
        raise FileNotFoundError(f"run {run_id!r} not found in {runs_dir} (missing {missing})")
    dest = Path(exp_dir) / "kept" / run_id
    dest.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(f, dest / f.name)
    return dest
# ---- change log ----------------------------------------------------------------------------

def _text(arg) -> str:
    return "" if arg in (None, "-") else Path(arg).read_text(encoding="utf-8")


def record_change(exp_dir, kind, quote, reason, before, after, nwim=False) -> dict:
    """before/after: file path, or '-' for none (a new file). Stores both texts and a unified diff."""
    if kind not in ("rule", "oracle"):
        raise ValueError("kind must be rule or oracle")
    if not quote.strip():
        raise ValueError("--quote is required: the author's exact words, verbatim")
    if after in (None, "-"):
        raise ValueError("--after must be a file")
    b, a = _text(before), _text(after)
    diff = "".join(difflib.unified_diff(b.splitlines(True), a.splitlines(True), "before", "after"))
    row = {"timestamp": now_utc(), "kind": kind, "quote": quote, "reason": reason,
           "files": {"before": None if before in (None, "-") else str(before), "after": str(after)},
           "before_text": b, "after_text": a, "diff": diff, "git_commit": git_commit(),
           "not_what_i_meant": bool(nwim)}
    _append(Path(exp_dir) / CHANGES_NAME, row)
    return row


def changes_text(rows) -> str:
    if not rows:
        return "No changes recorded yet."
    out = []
    for i, r in enumerate(rows, 1):
        flag = "  [NOT WHAT I MEANT]" if r["not_what_i_meant"] else ""
        out.append(f"#{i}  {r['timestamp']}  {r['kind']}{flag}\n  quote:  \"{r['quote']}\"\n  reason: {r['reason']}\n"
                   f"  file:   {r['files']['after']}\n  commit: {r['git_commit']}\n"
                   + ("\n".join("    " + l for l in r["diff"].splitlines()) or "    (no change)"))
    return "\n\n".join(out)


# ---- questions -----------------------------------------------------------------------------

def record_question(exp_dir, quote, topic=None, led_to=None, timestamp=None, backfilled=False,
                    paraphrase=None, source=None) -> dict:
    """quote: the author's exact words, or None for a backfilled paraphrase row (then `paraphrase` is the
    one-line summary and is flagged "paraphrase": true). led_to: list of ADR ids, change rows or run ids."""
    if quote is None and not paraphrase:
        raise ValueError("--quote is required: the author's exact words, verbatim")
    if quote is not None and not quote.strip():
        raise ValueError("--quote is required: the author's exact words, verbatim")
    row = {"timestamp": timestamp or now_utc(), "quote": quote, "topic": topic, "led_to": list(led_to or []),
           "backfilled": bool(backfilled), "paraphrase": quote is None, "text": paraphrase, "source": source}
    _append(Path(exp_dir) / QUESTIONS_NAME, row)
    return row


def questions_text(rows) -> str:
    if not rows:
        return "No questions recorded yet."
    out = []
    for i, r in enumerate(rows, 1):
        flags = (" [backfilled]" if r["backfilled"] else "") + (" [paraphrase]" if r["paraphrase"] else "")
        body = f'"{r["quote"]}"' if r["quote"] is not None else f'(paraphrase) {r["text"]}'
        out.append(f"#{i}  {r['timestamp']}  {r['topic'] or '-'}{flags}\n  {body}\n  led to: "
                   + (", ".join(r["led_to"]) or "-"))
    return "\n\n".join(out)
