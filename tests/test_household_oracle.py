import ast
from pathlib import Path
from mar import household_oracle as O

SRC = Path(__file__).parent.parent / "src" / "mar"


def row(opens=5, retained=1.0, need=True, both=True, contributed=True, att=1, blocked=0):
    opt = dict(zip(O.OPTIONS, [i < opens for i in range(5)]))
    p = {"in": True, "open": opt, "exit_retained": retained, "contributed": contributed}
    return {"month": 0, "need_met": need, "both_in": both, "c_attempts": att, "c_blocked": blocked,
            "partners": {"A": dict(p), "B": dict(p)}}


def test_oracle_imports_nothing_from_the_package():
    tree = ast.parse((SRC / "household_oracle.py").read_text())
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            names |= {("." * n.level) + (n.module or "")} | {a.name for a in n.names}
    assert not any(n.startswith(".") or n.startswith("mar") for n in names), names
    for banned in ("cards", "compile", "gate", "household", "english", "patch_check"):
        assert banned not in names


def test_extremes():
    assert O.score([row()]) == {"freedom": 1.0, "cooperation": 1.0, "months": 1}
    s = O.score([row(opens=0, retained=0.0, need=False, both=False, contributed=False, att=1, blocked=1)])
    assert s["freedom"] == 0 and s["cooperation"] == 0


def test_formulas():
    s = O.score([row(opens=4, retained=0.25)])
    assert abs(s["freedom"] - (0.5 * 0.8 + 0.5 * 0.5)) < 1e-9
    s = O.score([row(need=False, contributed=False, blocked=1)])
    assert abs(s["cooperation"] - (0 + 0.25 + 0 + 0)) < 1e-9


def test_findings():
    assert O.findings([row()]) == []
    kinds = {f["kind"] for f in O.findings([row(opens=1, retained=0.0, blocked=1)])}
    assert {"low_freedom", "harm_to_outsider"} <= kinds
