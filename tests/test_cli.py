import json
from pathlib import Path

from mar import cli
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


# ---- household commands: parsing, dispatch and the guards (the heavy run functions are mocked) ----

HH = Path(__file__).parent.parent / "rules" / "household"


def hh_root(tmp_path):
    import shutil
    root = tmp_path / "hh"
    root.mkdir()
    for v in ("author_seed_v2_bindable", "baseline"):
        shutil.copytree(HH / v, root / v)
    return root


def runh(capsys, tmp_path, root, *args):
    code = main(["--runs-dir", str(tmp_path), "--experiments-dir", str(tmp_path / "exp"), "--household-rules", str(root), *args])
    cap = capsys.readouterr()
    return code, cap.out, cap.err


def test_household_requires_a_subcommand(tmp_path):
    import pytest
    with pytest.raises(SystemExit):
        main(["--runs-dir", str(tmp_path), "household"])


def test_household_show_is_plain_english_with_lint(capsys, tmp_path):
    code, out, _ = runh(capsys, tmp_path, hh_root(tmp_path), "household", "show", "--variant", "baseline")
    assert code == 0 and "In plain words:" in out and "Lint: PASS" in out and "A partner may always see the friend" in out


def test_household_show_confirmed_seed_warns_and_unknown_variant_errors(capsys, tmp_path):
    root = hh_root(tmp_path)
    _, out, _ = runh(capsys, tmp_path, root, "household", "show", "--variant", "author_seed_v2_bindable")
    assert "confirmed seed" in out
    code, _, err = runh(capsys, tmp_path, root, "household", "show", "--variant", "nope")
    assert code == 2 and "no household variant 'nope'" in err


def test_personas_list_and_show(capsys, tmp_path):
    code, out = run(capsys, tmp_path, "personas", "list")
    assert code == 0 and "anchor" in out and "pressing" in out
    code, out = run(capsys, tmp_path, "personas", "show", "wanderer")
    assert code == 0 and "Wanderer" in out
    code, _ = run(capsys, tmp_path, "personas", "show", "nobody")
    assert code == 2


def test_pair_parsing():
    ps = cli._personas()
    (a, b), = cli._pairs(ps, "anchor,The Wanderer")
    assert (a.id, b.id) == ("p-anchor", "p-wanderer")
    assert len(cli._pairs(ps, "hand")) == 15 and len(cli._pairs(ps, "pressing")) == 42 and len(cli._pairs(ps, "all")) == 57
    import pytest
    with pytest.raises(ValueError):
        cli._pairs(ps, "anchor")


def test_household_run_dispatches_and_writes_report(capsys, tmp_path, monkeypatch):
    seen = []
    rec = {"arm": "v22_baseline", "a": "p-anchor", "b": "p-wanderer", "seed": 0, "up": "up", "pleasure": 0.9, "s_off": 0.1, "s_non": 0.0,
           "trust_mean": 0.7, "together_weeks": 156, "weeks": 156, "pairing_up": True}
    monkeypatch.setattr(cli, "_hh_run_one", lambda v, d, pa, pb, seed, weeks, neg: seen.append((v, pa.id, pb.id, seed, weeks, neg)) or (rec, []))
    monkeypatch.setattr(cli, "_hh_freedom", lambda *a, **k: {"freedom": 0.9, "open": 0, "liberty": None})
    monkeypatch.setattr(cli, "_hh_page", lambda *a: "<html>fake</html>")
    code, out, _ = runh(capsys, tmp_path, hh_root(tmp_path), "household", "run", "--variant", "baseline", "--pair", "anchor,wanderer",
                        "--seeds", "2", "--weeks", "20")
    assert code == 0 and [s[3] for s in seen] == [0, 1] and seen[0][4:] == (20, False)
    assert Path(out.split("report: ")[1].splitlines()[0]).read_text() == "<html>fake</html>"
    assert "upward spiral" in out and "offsettable" in out and "liberty is not available" in out


def test_household_run_auto_negotiates_seed_variants(tmp_path):
    root = hh_root(tmp_path)
    a = cli.parser().parse_args(["--household-rules", str(root), "household", "run", "--variant", "x", "--pair", "a,b"])
    assert cli._negotiated(a, "author_seed_v2_bindable", False) and not cli._negotiated(a, "baseline", False)
    assert cli._negotiated(a, "baseline", True)


def test_household_compare_dispatch_and_stats(capsys, tmp_path, monkeypatch):
    def fake(a, variants, pairs, seeds, weeks, neg):
        keys = [f"{x.id}+{y.id}" for x, y in pairs]
        base = {k: 0.5 + 0.01 * i for i, k in enumerate(keys)}
        up = {"baseline": base, "other": {k: v + 0.1 + 0.001 * i for i, (k, v) in enumerate(base.items())}}
        data = {v: {m: dict(up[v]) for m, _ in cli.HH_METRICS} for v in variants}
        return data, {v: False for v in variants}
    monkeypatch.setattr(cli, "_hh_compare_data", fake)
    code, out, _ = runh(capsys, tmp_path, hh_root(tmp_path), "household", "compare", "--variants", "baseline,other", "--pairs", "hand")
    assert code == 0 and "Holm" in out and "95% bootstrap CIs" in out and "holds up after Holm" in out
    assert Path(out.split("report: ")[1].splitlines()[0]).exists()


def test_household_compare_needs_two_variants(capsys, tmp_path):
    code, _, err = runh(capsys, tmp_path, hh_root(tmp_path), "household", "compare", "--variants", "baseline")
    assert code == 2 and "at least two" in err


CARD = ["--attribute", "partner", "--deontic", "must_not", "--aim", "take_shared", "--cond", "consented:eq:0",
        "--gloss", "The pot is for shared needs unless both agree.", "--source", "author, chat", "--quote", "shared pot unless both agree"]


def test_card_add_copies_base_lints_and_records_quote(capsys, tmp_path):
    root = hh_root(tmp_path)
    code, out, _ = runh(capsys, tmp_path, root, "household", "card", "add", "--variant", "newv", "--id", "R9-x", *CARD)
    assert code == 0 and "lint passes" in out and "In plain English" in out
    assert (root / "newv" / "R9-x.yaml").exists() and (root / "newv" / "R6-no-veto.yaml").exists()
    assert not (root / "author_seed_v2_bindable" / "R9-x.yaml").exists()
    rows = [json.loads(x) for x in (tmp_path / "exp" / "changes.jsonl").read_text().splitlines()]
    assert rows[-1]["quote"] == "shared pot unless both agree" and rows[-1]["kind"] == "rule"
    code, out, _ = runh(capsys, tmp_path, root, "household", "card", "edit", "--variant", "newv", "--id", "R9-x", "--gloss", "New gloss.", "--quote", "tweak")
    assert code == 0 and "New gloss." in (root / "newv" / "R9-x.yaml").read_text()
    assert len((tmp_path / "exp" / "changes.jsonl").read_text().splitlines()) == 2


def test_card_never_touches_confirmed_seed_or_foreign_variants(capsys, tmp_path):
    root = hh_root(tmp_path)
    before = (root / "author_seed_v2_bindable" / "R6-no-veto.yaml").read_text()
    code, _, err = runh(capsys, tmp_path, root, "household", "card", "edit", "--variant", "author_seed_v2_bindable", "--id", "R6-no-veto", "--gloss", "x", "--quote", "q")
    assert code == 2 and "never edited in place" in err
    assert (root / "author_seed_v2_bindable" / "R6-no-veto.yaml").read_text() == before
    code, _, err = runh(capsys, tmp_path, root, "household", "card", "edit", "--variant", "baseline", "--id", "B4-may-see", "--gloss", "x", "--quote", "q")
    assert code == 2 and "not made by this command" in err
    assert not (tmp_path / "exp" / "changes.jsonl").exists()


def test_card_refused_when_lint_fails_and_writes_nothing(capsys, tmp_path):
    root = hh_root(tmp_path)
    bad = ["--attribute", "partner", "--deontic", "must_not", "--aim", "leave", "--gloss", "Nobody may ever leave.", "--source", "t", "--quote", "no leaving"]
    code, _, err = runh(capsys, tmp_path, root, "household", "card", "add", "--variant", "badv", "--id", "R9-bad", *bad)
    assert code == 1 and "refused" in err
    assert not (root / "badv").exists() and not (tmp_path / "exp" / "changes.jsonl").exists()


def test_card_needs_quote_and_valid_cond(capsys, tmp_path):
    import pytest
    root = hh_root(tmp_path)
    with pytest.raises(SystemExit):
        main(["household", "card", "add", "--variant", "v", "--id", "R9"])
    code, _, err = runh(capsys, tmp_path, root, "household", "card", "add", "--variant", "v", "--id", "R9", *CARD[:6], "--cond", "bad", *CARD[8:])
    assert code == 2 and "expr:op:value" in err
