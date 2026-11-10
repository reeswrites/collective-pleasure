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


# ---- workbench commands: dispatch only, the heavy scripts are mocked ----

class FakeMod:
    def __init__(self, text=""):
        self.calls, self.text = [], text

    def main(self, argv=None):
        import sys
        self.calls.append(list(argv) if argv is not None else list(sys.argv[1:]))
        if self.text:
            print(self.text)
        return 0


def patch_script(monkeypatch, mod):
    import mar.cli as cli
    names = []
    monkeypatch.setattr(cli, "_script", lambda n: names.append(n) or mod)
    return names


def test_evolve_dry_run_runs_nothing(capsys, tmp_path, monkeypatch):
    names = patch_script(monkeypatch, FakeMod())
    code, out = run(capsys, tmp_path, "evolve", "--v2", "--dry-run")
    assert code == 0 and names == [] and "no model calls" in out and "evolve-v2" in out


def test_evolve_dispatches_v1_and_v2(capsys, tmp_path, monkeypatch):
    mod = FakeMod()
    names = patch_script(monkeypatch, mod)
    run(capsys, tmp_path, "evolve")
    run(capsys, tmp_path, "evolve", "--v2")
    assert names == ["evolve_run", "evolve_v2_run"] and len(mod.calls) == 2


def test_game_dispatch_and_seeds(capsys, tmp_path, monkeypatch):
    mod = FakeMod()
    names = patch_script(monkeypatch, mod)
    code, out = run(capsys, tmp_path, "game", "vpgg", "--seeds", "3")
    assert code == 0 and names == ["vpgg_run"] and mod.calls == [["--seeds", "3"]]
    run(capsys, tmp_path, "game", "bargaining")
    assert names[-1] == "bargaining_run"


def test_game_report_only_does_not_run(capsys, tmp_path, monkeypatch):
    names = patch_script(monkeypatch, FakeMod())
    run(capsys, tmp_path, "game", "bargaining", "--report-only")
    assert names == []


def test_game_rejects_unknown_game(tmp_path):
    import pytest
    with pytest.raises(SystemExit):
        main(["game", "chess"])


def test_empower_filters_by_world(capsys, tmp_path, monkeypatch):
    text = "k=3\nVPGG row\nhand-made freedom 5\nfishery row\nP1   PASS  ok"
    names = patch_script(monkeypatch, FakeMod(text))
    _, out = run(capsys, tmp_path, "empower", "--world", "vpgg")
    assert names == ["empowerment_run"] and "VPGG row" in out and "fishery row" not in out and "PASS" in out
    _, out = run(capsys, tmp_path, "empower", "--world", "fishery")
    assert "fishery row" in out and "VPGG row" not in out


def test_ladder_dry_run_passes_dry_run_flag(capsys, tmp_path, monkeypatch):
    mod = FakeMod("estimate table")
    patch_script(monkeypatch, mod)
    code, out = run(capsys, tmp_path, "ladder", "--dry-run", "--model", "claude:claude-haiku-5-5")
    assert code == 0 and "estimate table" in out and mod.calls == [[
        "--model", "claude:claude-haiku-5-5", "--seeds", "0", "1", "2", "--attempts", "1", "--dry-run"]]


def test_ladder_live_refused_without_max_usd(capsys, tmp_path, monkeypatch):
    mod = FakeMod("estimate table")
    patch_script(monkeypatch, mod)
    code, out = run(capsys, tmp_path, "ladder", "--model", "claude:claude-haiku-5-5")
    assert code == 2 and "estimate table" in out
    assert all("--dry-run" in c for c in mod.calls)  # only the estimate ran


def test_ladder_live_with_cap_estimates_then_runs(capsys, tmp_path, monkeypatch):
    mod = FakeMod()
    patch_script(monkeypatch, mod)
    code, _ = run(capsys, tmp_path, "ladder", "--model", "claude:claude-haiku-5-5", "--max-usd", "2")
    assert code == 0 and "--dry-run" in mod.calls[0] and "--dry-run" not in mod.calls[1] and "--max-usd" in mod.calls[1]


def test_ladder_requires_a_model(capsys, tmp_path, monkeypatch):
    patch_script(monkeypatch, FakeMod())
    assert main(["ladder", "--max-usd", "1"]) == 2


def test_ladder_report_only(capsys, tmp_path, monkeypatch):
    mod = FakeMod()
    patch_script(monkeypatch, mod)
    run(capsys, tmp_path, "ladder", "--report-only")
    assert mod.calls == [["--report-only"]]


def test_results_lists_verdicts_and_reports(capsys, tmp_path):
    code, out = run(capsys, tmp_path, "results")
    assert code == 0 and "vpgg.md" in out and "NOT rediscovered" in out and "Latest reports:" in out
    assert "-prereg.md:" not in out


def test_household_stub(capsys, tmp_path):
    code, out = run(capsys, tmp_path, "household")
    assert code == 0 and "household commands land after the seed v2 run" in out
