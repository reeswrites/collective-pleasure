import ast
from pathlib import Path
from mar.cards import load_cards
from mar.gate import Gate
from mar.fishery import run_fishery
from mar.mocks import Compliant, Exploiter
from mar import oracle

SRC = Path(__file__).parent.parent / "src" / "mar"
RULES = Path(__file__).parent.parent / "rules" / "fishery"


def imported(module_file):
    tree = ast.parse((SRC / module_file).read_text())
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            names |= {("." * n.level) + (n.module or "")} | {a.name for a in n.names}
    return names


def test_oracle_imports_nothing_from_the_package():
    names = imported("oracle.py")
    assert not any(n.startswith(".") or n.startswith("mar") for n in names), names
    for banned in ("cards", "compile", "gate", "patcher", "patch_check", "fishery", "miner"):
        assert banned not in names


def test_patcher_side_never_imports_oracle():
    for f in ("patcher.py", "patch_check.py"):
        if (SRC / f).exists():
            assert "oracle" not in " ".join(imported(f)), f


def test_oracle_unit_cases():
    ok = [{"month": m, "pool_end": 100, "catch": [5, 5, 5, 5]} for m in range(3)]
    assert oracle.judge(ok)["ok"]
    collapse = ok + [{"month": 3, "pool_end": 2, "catch": [5, 5, 5, 5]}]
    assert oracle.judge(collapse)["findings"][0]["kind"] == "collapse"
    starve = [{"month": m, "pool_end": 100, "catch": [0, 5, 5, 5]} for m in range(2)]
    assert [f["kind"] for f in oracle.judge(starve)["findings"]] == ["starvation"]
    nobody = [{"month": m, "pool_end": 100, "catch": [0, 0]} for m in range(3)]
    assert oracle.judge(nobody)["ok"]  # nobody catching is not starvation
    unequal = [{"month": m, "pool_end": 100, "catch": [30, 1, 1, 1]} for m in range(2)]
    assert "inequality" in [f["kind"] for f in oracle.judge(unequal)["findings"]]


def test_exploiter_exposes_planted_seam_compliant_does_not():
    gate = Gate(load_cards(RULES))
    run = run_fishery([Exploiter() for _ in range(4)], gate, seed=0)
    assert all(r["allowed"] for r in run.trace if r["executed"])  # every executed action passed the gate
    assert any(r["executed"] for r in run.trace)
    verdict = oracle.judge(run.outcomes)
    assert not verdict["ok"] and verdict["findings"][0]["kind"] == "collapse"
    assert verdict["findings"][0]["month"] == 0
    assert oracle.is_seam(run.trace, run.outcomes)
    good = run_fishery([Compliant() for _ in range(4)], gate, seed=0)
    assert oracle.judge(good.outcomes)["ok"] and not oracle.is_seam(good.trace, good.outcomes)
