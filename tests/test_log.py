import json
from pathlib import Path

import pytest

from mar import log as explog
from mar.cli import main

RULES = str(Path(__file__).parent.parent / "rules" / "fishery")


def mar(capsys, tmp_path, *args):
    code = main(["--runs-dir", str(tmp_path / "runs"), "--experiments-dir", str(tmp_path / "exp"), *args])
    return code, capsys.readouterr().out


def rows(tmp_path):
    return explog.read_rows(tmp_path / "exp" / "log.jsonl")


def test_run_appends_one_line_with_every_field(capsys, tmp_path):
    code, out = mar(capsys, tmp_path, "run", "--spec", RULES, "--note", "why not")
    assert code == 0 and "logged:" in out
    r, = rows(tmp_path)
    for k in ("run_id", "timestamp", "git_commit", "spec", "cards_hash", "oracle_version", "agents", "months",
              "seed", "model", "cost_usd", "verdict", "seams", "report", "trace", "note"):
        assert k in r
    assert r["model"] is None and r["cost_usd"] is None and r["note"] == "why not"
    assert r["seams"] == 1 and "seam" in r["verdict"] and r["timestamp"].endswith("Z")
    assert len((tmp_path / "exp" / "log.jsonl").read_text().splitlines()) == 1


def test_log_is_append_only(capsys, tmp_path):
    mar(capsys, tmp_path, "run", "--spec", RULES, "--note", "first")
    first = (tmp_path / "exp" / "log.jsonl").read_text()
    mar(capsys, tmp_path, "run", "--spec", RULES, "--seed", "1", "--note", "second")
    both = (tmp_path / "exp" / "log.jsonl").read_text()
    assert both.startswith(first) and len(both.splitlines()) == 2


def test_loop_logs_with_patch_in_cards_hash(capsys, tmp_path):
    mar(capsys, tmp_path, "run", "--spec", RULES)
    mar(capsys, tmp_path, "loop", "--spec", RULES, "--rounds", "2")
    a, b = rows(tmp_path)
    assert b["kind"] == "loop" and "loop" in b["run_id"] and a["cards_hash"] != b["cards_hash"]
    assert a["oracle_version"] == b["oracle_version"]


def test_hashes_are_stable():
    from mar.cards import load_cards
    c = load_cards(RULES)
    assert explog.cards_hash(c) == explog.cards_hash(list(reversed(c)))
    assert explog.oracle_version() == explog.oracle_version()


def test_log_table_and_detail(capsys, tmp_path):
    mar(capsys, tmp_path, "run", "--spec", RULES, "--note", "alpha")
    mar(capsys, tmp_path, "run", "--spec", RULES, "--seed", "3", "--note", "beta")
    _, out = mar(capsys, tmp_path, "log", "--last", "1")
    assert "beta" in out and "alpha" not in out
    _, out = mar(capsys, tmp_path, "log")
    assert "alpha" in out and "beta" in out
    rid = rows(tmp_path)[1]["run_id"]
    _, out = mar(capsys, tmp_path, "log", "--run", rid)
    assert f"run_id: {rid}" in out and "oracle_version:" in out and "verdict:" in out


def test_log_empty_and_unknown_run(capsys, tmp_path):
    _, out = mar(capsys, tmp_path, "log")
    assert "No log entries" in out
    assert mar(capsys, tmp_path, "log", "--run", "nope")[0] == 2


def test_keep_copies_trace_and_report(capsys, tmp_path):
    mar(capsys, tmp_path, "run", "--spec", RULES)
    rid = rows(tmp_path)[0]["run_id"]
    code, out = mar(capsys, tmp_path, "keep", rid)
    assert code == 0
    d = tmp_path / "exp" / "kept" / rid
    assert (d / "trace.json").exists() and (d / "report.html").exists()
    json.loads((d / "trace.json").read_text())
    assert mar(capsys, tmp_path, "keep", "missing")[0] == 2
