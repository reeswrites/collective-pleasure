from html import escape
from pathlib import Path

from mar import log as explog
from mar.cli import main

ROOT = Path(__file__).parent.parent
EXP = ROOT / "experiments"
CONV = ROOT / "docs" / "conversations" / "2026-11-10-encoding-alignment-via-mechanism.md"


def mar(capsys, tmp_path, *args, exp=None):
    code = main(["--runs-dir", str(tmp_path / "runs"), "--experiments-dir", str(exp or tmp_path / "exp"), *args])
    return code, capsys.readouterr().out


def test_record_and_list_append_only(capsys, tmp_path):
    assert "No questions" in mar(capsys, tmp_path, "question", "list")[1]
    mar(capsys, tmp_path, "question", "record", "--quote", "why though?", "--topic", "why", "--led-to", "ADR 0003")
    first = (tmp_path / "exp" / "questions.jsonl").read_text()
    mar(capsys, tmp_path, "question", "record", "--quote", "and then?")
    text = (tmp_path / "exp" / "questions.jsonl").read_text()
    assert text.startswith(first) and len(text.splitlines()) == 2
    r = explog.read_rows(tmp_path / "exp" / "questions.jsonl")[0]
    assert r["quote"] == "why though?" and r["led_to"] == ["ADR 0003"] and not r["backfilled"] and r["timestamp"].endswith("Z")
    out = mar(capsys, tmp_path, "question", "list")[1]
    assert '"why though?"' in out and "ADR 0003" in out
    assert mar(capsys, tmp_path, "question", "record", "--quote", " ")[0] == 2


def test_backfill_quotes_are_verbatim_and_paraphrases_marked():
    rows = explog.read_rows(EXP / "questions.jsonl")
    conv = CONV.read_text()
    quotes = [r for r in rows if r["quote"] is not None]
    paras = [r for r in rows if r["quote"] is None]
    assert len(quotes) >= 5 and len(paras) >= 5
    assert all(r["backfilled"] and r["quote"] in conv for r in quotes)
    assert all(r["paraphrase"] and r["backfilled"] and r["text"] for r in paras)


def test_timeline_builds_self_contained_with_every_backfilled_entry(capsys, tmp_path):
    code, out = mar(capsys, tmp_path, "timeline", exp=EXP)
    assert code == 0 and "timeline:" in out
    html = (tmp_path / "runs" / "timeline.html").read_text()
    for banned in ("<script", "http://", "https://", "src=", "<link"):
        assert banned not in html
    assert "prefers-color-scheme:dark" in html and "viewport" in html and "<svg" in html
    for k in ("Question", "Decision", "Change", "Run", "Commit"):
        assert f'<span class="badge">{k}</span>' in html
    for r in explog.read_rows(EXP / "questions.jsonl"):
        assert escape(r["quote"] if r["quote"] is not None else r["text"]) in html
    assert "docs/decisions/0005-two-loops-and-workbench.md" in html.replace("\\", "/")


def test_timeline_merges_runs_and_changes(capsys, tmp_path):
    exp = tmp_path / "exp"
    rules = str(ROOT / "rules" / "fishery")
    mar(capsys, tmp_path, "run", "--spec", rules, "--note", "smoke")
    f = tmp_path / "a.yaml"
    f.write_text("x: 1\n")
    mar(capsys, tmp_path, "change", "record", "--kind", "rule", "--quote", "not like that", "--reason", "r",
        "--before", "-", "--after", str(f), "--nwim")
    mar(capsys, tmp_path, "timeline")
    html = (tmp_path / "runs" / "timeline.html").read_text()
    assert "not like that" in html and "not what I meant" in html and "fishery-exploiterx4-m6-s0" in html
    assert "report.html" in html
