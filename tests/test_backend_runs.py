"""mar run with jev and llm agents, offline: the HTTP function is replaced by a fake."""
import json
from pathlib import Path

import pytest

from mar.agents import env, http
from mar.cli import main

RULES = str(Path(__file__).parent.parent / "rules" / "fishery")


@pytest.fixture(autouse=True)
def offline(monkeypatch, tmp_path):
    monkeypatch.setattr(env, "ENV_PATH", tmp_path / "no.env")
    monkeypatch.setattr(http, "sleep", lambda s: None)
    monkeypatch.setenv("OPENROUTER_API_KEY", "k-test")
    monkeypatch.delenv("MAR_LLM_MODEL", raising=False)
    monkeypatch.setattr(http, "post_json", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no transport")))


def fake_transport(monkeypatch, calls):
    def post(url, headers, body, timeout=60.0):
        calls.append((url, body))
        if "decisions" in url:
            qk = next(iter(body["questions"]))
            crit = body["questions"][qk]["criteria"]
            top = "1-10" if qk == "action" else "41-50"  # reports will mismatch actions
            probs = {k: (0.9 if k == top else 0.1 / (len(crit) - 1)) for k in crit}
            return {"model": "typesafe/jev-1.14-test", "answers": {qk: {"choice": top, "confidence": 0.9,
                    "probabilities": probs}}, "usage": {"input_tokens": 400, "output_tokens": 2}, "meta": {}}
        content = json.dumps({"action": "1-10", "report": "1-10", "talk": "I will be careful"})
        return {"model": "vendor/llm-build", "choices": [{"message": {"content": content}}],
                "usage": {"prompt_tokens": 300, "completion_tokens": 30, "cost": 0.0001}}
    monkeypatch.setattr(http, "post_json", post)


def mar(capsys, tmp_path, *args):
    code = main(["--runs-dir", str(tmp_path / "runs"), "--experiments-dir", str(tmp_path / "exp"), *args])
    return code, capsys.readouterr()


def test_dry_run_prints_calls_and_cost_and_calls_nothing(capsys, tmp_path):
    code, out = mar(capsys, tmp_path, "run", "--spec", RULES, "--agents", "jev*3,llm*2", "--months", "2",
                    "--dry-run", "--llm-price-in", "0.1", "--llm-price-out", "0.4")
    assert code == 0 and "Dry run" in out.out
    assert "jev: up to 78 calls" in out.out and "llm: up to 52 calls" in out.out and "Total upper bound: $" in out.out
    assert not (tmp_path / "exp").exists() and not (tmp_path / "runs").exists()


def test_dry_run_scripted_and_unpriced_llm(capsys, tmp_path):
    assert "no model calls" in mar(capsys, tmp_path, "run", "--spec", RULES, "--dry-run")[1].out
    assert "no price set" in mar(capsys, tmp_path, "run", "--spec", RULES, "--agents", "llm*1", "--dry-run")[1].out


def test_mixed_jev_and_llm_run_logs_usage_and_shows_say_vs_do(capsys, tmp_path, monkeypatch):
    calls = []
    fake_transport(monkeypatch, calls)
    code, out = mar(capsys, tmp_path, "run", "--spec", RULES, "--agents", "jev*2,llm*1,compliant*1", "--months", "2",
                    "--seed", "1", "--model", "vendor/llm", "--temperature", "2", "--note", "offline test")
    assert code == 0, out.err
    row = json.loads((tmp_path / "exp" / "log.jsonl").read_text().splitlines()[0])
    b = row["backends"]
    assert b["jev"]["model_builds"] == ["typesafe/jev-1.14-test"] and b["llm"]["model_builds"] == ["vendor/llm-build"]
    n_jev = sum(1 for u, _ in calls if "decisions" in u)
    assert b["jev"]["calls"] + b["jev"]["cache_hits"] == n_jev
    assert b["jev"]["input_tokens"] == 400 * b["jev"]["calls"] and b["llm"]["input_tokens"] == 300 * b["llm"]["calls"]
    assert row["cost_usd"] == pytest.approx(b["jev"]["usd"] + b["llm"]["usd"]) and row["cost_usd"] > 0
    assert "typesafe/jev-1.14-test" in row["model"] and "-T2-" in row["run_id"]
    trace = json.loads(next((tmp_path / "runs").glob("*/trace.json")).read_text())
    assert len(trace["reports"]) == 6 and trace["backends"]["llm"]["calls"] > 0
    assert all(r["lie"] for r in trace["reports"] if r["kind"] == "jev")
    assert all(r["talk"] == "I will be careful" for r in trace["reports"] if r["kind"] == "llm")
    html = next((tmp_path / "runs").glob("*/report.html")).read_text()
    assert "Say vs do" in html and "TYPED LIE" in html and "I will be careful" in html and "Free talk" in html
    assert "jev: typesafe/jev-1.14-test" in out.out and "typed reports:" in out.out


def test_cached_rerun_makes_no_new_jev_calls_and_same_trace(capsys, tmp_path, monkeypatch):
    calls = []
    fake_transport(monkeypatch, calls)
    args = ("run", "--spec", RULES, "--agents", "jev*2", "--months", "1", "--seed", "3")
    mar(capsys, tmp_path, *args)
    n = len(calls)
    t1 = json.loads(next((tmp_path / "runs").glob("*/trace.json")).read_text())["trace"]
    mar(capsys, tmp_path, *args)
    rows = [json.loads(l) for l in (tmp_path / "exp" / "log.jsonl").read_text().splitlines()]
    t2 = json.loads(next((tmp_path / "runs").glob("*/trace.json")).read_text())["trace"]
    assert len(calls) == n and rows[1]["backends"]["jev"]["calls"] == 0 and rows[1]["cost_usd"] == 0
    assert t1 == t2


def test_missing_key_and_missing_model_exit_2_with_clear_message(capsys, tmp_path, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY")
    code, out = mar(capsys, tmp_path, "run", "--spec", RULES, "--agents", "jev*1", "--months", "1")
    assert code == 2 and "OPENROUTER_API_KEY" in out.err
    code, out = mar(capsys, tmp_path, "run", "--spec", RULES, "--agents", "llm*1", "--months", "1")
    assert code == 2 and "MAR_LLM_MODEL" in out.err
    assert not (tmp_path / "exp" / "log.jsonl").exists()


def test_scripted_runs_unchanged_no_say_vs_do_panel(capsys, tmp_path):
    mar(capsys, tmp_path, "run", "--spec", RULES, "--agents", "exploiter*2", "--months", "2")
    assert "Say vs do" not in next((tmp_path / "runs").glob("*/report.html")).read_text()
    row = json.loads((tmp_path / "exp" / "log.jsonl").read_text().splitlines()[0])
    assert row["backends"] == {} and row["model"] is None and row["cost_usd"] is None


def test_old_trace_without_new_fields_still_loads(tmp_path, capsys):
    from mar.report import load_record
    mar(capsys, tmp_path, "run", "--spec", RULES, "--months", "1")
    p = next((tmp_path / "runs").glob("*/trace.json"))
    d = json.loads(p.read_text())
    d.pop("reports"), d.pop("backends")
    p.write_text(json.dumps(d))
    assert load_record(p.parent.name, tmp_path / "runs").reports == []


def test_budget_limit_stops_run(capsys, tmp_path, monkeypatch):
    fake_transport(monkeypatch, [])
    code, out = mar(capsys, tmp_path, "run", "--spec", RULES, "--agents", "llm*1", "--months", "1",
                    "--model", "m", "--max-usd", "0.0002")
    assert code == 2 and "limit" in out.err
