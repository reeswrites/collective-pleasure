import json
from pathlib import Path

from mar.cli import main

RULES = str(Path(__file__).parent.parent / "rules" / "fishery")


def run(capsys, tmp_path, *args):
    code = main(["--runs-dir", str(tmp_path), "--experiments-dir", str(tmp_path / "exp"), *args])
    return code, capsys.readouterr().out


def test_run_writes_report_and_prints_verdict(capsys, tmp_path):
    code, out = run(capsys, tmp_path, "run", "--spec", RULES, "--agents", "exploiter*4", "--months", "6", "--seed", "0")
    assert code == 0
    assert "Pool collapsed in month 0." in out and "this is a seam" in out
    path = Path(out.split("report: ")[1].splitlines()[0])
    assert path.exists() and path.name == "report.html" and (path.parent / "trace.json").exists()


def test_run_with_mixed_agents(capsys, tmp_path):
    code, out = run(capsys, tmp_path, "run", "--spec", RULES, "--agents", "exploiter,compliant", "--months", "3")
    assert code == 0 and "report:" in out


def test_rules_show_prints_every_card_with_gloss(capsys, tmp_path):
    code, out = run(capsys, tmp_path, "rules", "show", "--spec", RULES)
    assert code == 0
    for cid in ("F1", "F2", "F3", "F4"):
        assert cid in out
    assert "No fisher may take more than 10 fish" in out and "source:" in out


def test_check_passes_on_baseline_and_states_bound(capsys, tmp_path):
    code, out = run(capsys, tmp_path, "check", "--spec", RULES, "--k", "3")
    assert code == 0 and out.count("[PASS]") == 4 and "k=3" in out


def test_loop_curve_goes_one_then_zero_and_report_exists(capsys, tmp_path):
    code, out = run(capsys, tmp_path, "loop", "--spec", RULES, "--rounds", "2")
    assert code == 0
    assert "round 0: 1, round 1: 0, round 2: 0" in out
    path = Path(out.split("report: ")[1].splitlines()[0])
    html = path.read_text()
    assert "Seam curve" in html and "What happened each round" in html and "added by patch" in html


def test_report_rebuilds_from_run_id(capsys, tmp_path):
    _, out = run(capsys, tmp_path, "run", "--spec", RULES, "--months", "3")
    path = Path(out.split("report: ")[1].splitlines()[0])
    path.unlink()
    code, out2 = run(capsys, tmp_path, "report", path.parent.name)
    assert code == 0 and path.exists()
    assert json.loads((path.parent / "trace.json").read_text())["months"] == 3


def test_bad_inputs_exit_2(capsys, tmp_path):
    assert main(["--runs-dir", str(tmp_path), "run", "--spec", RULES, "--agents", "wizard"]) == 2
    assert main(["--runs-dir", str(tmp_path), "report", "nope"]) == 2
