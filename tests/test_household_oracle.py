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


def hrow(week, B, s_non=0.0, tip=0.0, pleasure=0.5):
    h = {"pleasure": pleasure, "s_off": 0.1, "s_non": s_non, "B": B, "tip": tip}
    return {"week": week, "hedonic": {"A": dict(h), "B": dict(h)}}


def test_spiral_classes_and_time_to_cross():
    up = [hrow(w, -0.2 + 0.05 * w) for w in range(20)]          # crosses at week 5 and keeps rising
    assert O.spiral_class(up, "A") == "up" and O.time_to_cross(up, "A") == 5
    down = [hrow(w, 0.2 - 0.05 * w) for w in range(20)]
    assert O.spiral_class(down, "A") == "down"
    flat = [hrow(w, 0.05) for w in range(20)]
    assert O.spiral_class(flat, "A") == "stalled" and O.time_to_cross(flat, "A") is None


def test_non_offsettable_blocks_upward_and_fails_the_run():
    rows = [hrow(w, 0.9, s_non=0.5 if 4 <= w < 11 else 0.0) for w in range(30)]
    assert O.longest_nonoff(rows, "A") == 7 and O.hedonic_summary(rows)["fail"]
    rows2 = [hrow(w, 0.9, s_non=0.5 if w >= 25 else 0.0) for w in range(30)]
    assert O.spiral_class(rows2, "A") == "stalled"                # pleasure cannot buy it back
    ok = O.hedonic_summary([hrow(w, 0.9) for w in range(30)])
    assert ok["pairing_up"] and not ok["fail"]


def test_norm_quality_averages_pleasure_over_passing_runs_only():
    good = O.hedonic_summary([hrow(w, 0.9, pleasure=0.8) for w in range(30)])
    bad = O.hedonic_summary([hrow(w, 0.9, s_non=0.5, pleasure=1.0) for w in range(30)])
    q = O.norm_quality([good, good, bad])
    assert abs(q["pleasure_passing"] - 0.8) < 1e-9 and q["fail_share"] > 0.3 and q["fails"]
    assert O.norm_quality([good, good, good])["fails"] is False
