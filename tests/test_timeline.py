"""mar timeline --keep: dated, committed, GitHub-readable snapshot."""
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from mar import log as explog
from mar import timeline
from mar.cli import main


def make_repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "docs" / "decisions").mkdir(parents=True)
    (repo / "docs" / "decisions" / "0001-x.md").write_text("# 0001. A decision\n\nStatus: accepted (2026-11-10)\n")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "first commit"],
                   cwd=repo, check=True)
    exp = repo / "experiments"
    explog.record_question(exp, "why is the sky <blue>?\nsecond line", "sky", ["ADR 0001"], timestamp="2026-11-10T10:00:00Z")
    explog.record_question(exp, None, "para", paraphrase="a paraphrase", timestamp="2026-11-09T10:00:00Z", backfilled=True)
    (exp / "kept" / "run1").mkdir(parents=True)
    (exp / "kept" / "run1" / "report.html").write_text("<html>")
    explog._append(exp / "log.jsonl", {"run_id": "run1", "timestamp": "2026-11-10T11:00:00Z", "verdict": "ok", "note": "n",
                                       "report": "runs/run1/report.html"})
    return repo, exp


def test_keep_writes_dated_html_and_markdown(tmp_path, monkeypatch):
    repo, exp = make_repo(tmp_path)
    monkeypatch.chdir(repo)
    today = datetime(2026, 11, 10, tzinfo=timezone.utc)
    h, m = timeline.keep_snapshot(exp, repo, today)
    assert h == (exp / "timelines" / "2026-11-10.html").resolve() and m.name == "2026-11-10.md"
    md, html = m.read_text(), h.read_text()
    assert "# How we got here (snapshot 2026-11-10)" in md and "review before any public release" in md
    assert md.index("## 2026-11-09") < md.index("## 2026-11-10")  # grouped by day, oldest first
    assert "- **Question** " in md and "`paraphrase`" in md and "`backfilled`" in md
    assert "  > why is the sky <blue>?" in md and "  > second line" in md
    assert "- **Decision** date only" in md and "**0001. A decision**" in md and "git commit `" in md
    assert "Led to: ADR 0001" in md
    assert "[report.html](../kept/run1/report.html)" in md  # kept run linked relatively
    assert "[0001-x.md](../../docs/decisions/0001-x.md)" in md
    assert "<!doctype html>" in html and 'href="../kept/run1/report.html"' in html and "<script" not in html


def test_cli_keep_flag_writes_snapshot_and_plain_run_does_not(capsys, tmp_path):
    exp = tmp_path / "exp"
    explog.record_question(exp, "q", "t")
    args = ["--runs-dir", str(tmp_path / "runs"), "--experiments-dir", str(exp), "timeline"]
    assert main(args) == 0 and not (exp / "timelines").exists()
    capsys.readouterr()
    assert main(args + ["--keep"]) == 0
    out = capsys.readouterr().out
    files = sorted(p.name for p in (exp / "timelines").iterdir())
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    assert files == [f"{day}.html", f"{day}.md"] and "kept:" in out
    assert (tmp_path / "runs" / "timeline.html").exists()


def test_committed_readme_and_skill_mention_keep():
    root = Path(__file__).parent.parent
    assert "own words" in (root / "experiments" / "timelines" / "README.md").read_text()
    assert "mar timeline --keep" in (root / ".claude" / "skills" / "rules-lab" / "SKILL.md").read_text()
