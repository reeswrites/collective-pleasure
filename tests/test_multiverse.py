"""Tests for the multiverse sweep (src/mar/multiverse.py). Fast: design helpers, labels, and the default points of the exact solves."""
import math

import pytest

from mar import multiverse as MV


def test_param_mapping_and_ends():
    p = MV.Param("x", 1.0, 0.5, 2.0)
    assert p.at(0.0) == pytest.approx(0.5)
    assert p.at(0.5) == pytest.approx(1.0)
    assert p.ends() == (0.5, 2.0)
    assert p.position(1.0) == pytest.approx(0.5)
    q = MV.Param("k", 3, 2, 4, "int")
    assert {q.at(u / 10) for u in range(10)} == {2, 3, 4}
    s = MV.Param("s", 26, values=(13, 26, 52), kind="set")
    assert s.at(0.99) == 52 and s.ends() == (13, 52)


def test_lhs_is_stratified_and_seeded():
    ps = (MV.Param("a", 1.0, 0.5, 2.0, "lin"), MV.Param("b", 1.0, 0.5, 2.0))
    pts = MV.lhs(ps, 20, seed=1)
    assert len(pts) == 20
    # one draw per stratum on the linear axis
    strata = sorted(int((pt["a"] - 0.5) / 1.5 * 20) for pt in pts)
    assert strata == list(range(20))
    assert pts == MV.lhs(ps, 20, seed=1)
    assert pts != MV.lhs(ps, 20, seed=2)


def test_oat_rows():
    ps = (MV.Param("a", 1.0, 0.5, 2.0), MV.Param("b", 3.0, 1.0, 9.0))
    rows = MV.oat(ps, extra={"a": [7.0]})
    assert [(n, v) for n, v, _ in rows] == [("a", 0.5), ("a", 2.0), ("a", 7.0), ("b", 1.0), ("b", 9.0)]
    assert rows[0][2] == {"a": 0.5, "b": 3.0}


def test_spearman():
    assert MV.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert MV.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)
    assert MV.spearman([1, 1, 1], [1, 2, 3]) == 0.0


def test_labels():
    assert MV.label([True] * 10, []) == "robust"
    assert MV.label([True] * 10, ["x = 1"]) == "fragile"
    assert MV.label([True] * 7 + [False] * 3, []) == "fragile"
    assert MV.label([True] * 4 + [False] * 6, []) == "flips"
    assert MV.label([True] * 10, [], default_holds=False) == "not reproduced at HEAD"


def test_summarize_names_the_driver():
    ps = (MV.Param("a", 1.0, 0.5, 2.0, "lin"), MV.Param("b", 1.0, 0.5, 2.0, "lin"))
    pts = MV.lhs(ps, 30, seed=3)
    margins = [pt["a"] - 1.2 for pt in pts]
    s = MV.summarize(ps, pts, margins, [("a", 0.5, -0.7), ("a", 2.0, 0.8)], default_margin=-0.2)
    assert s["top_param"] == "a" and s["top_rho"] > 0.9
    assert s["oat_flips"] == ["a = 0.5"]
    assert s["label"] == "not reproduced at HEAD"


def test_set_default_rebinds_in_memory():
    def f(x, weeks=26, *, cfg=None):
        return weeks, cfg
    MV._set_default(f, "weeks", 13)
    MV._set_default(f, "cfg", "c")
    assert f(0) == (13, "c")
    assert MV._get_default(f, "weeks") == 13


def test_horizon_default_point_reproduces_published_numbers():
    r = MV.horizon_point(MV.defaults(MV.HORIZON_PARAMS))
    assert r["loss95_26"] == pytest.approx(15.5, abs=0.1)      # docs/results/horizon.md section 3
    assert r["loss1_52"] == pytest.approx(28.6, abs=0.1)
    assert r["net"][1] == pytest.approx(-5.6, abs=0.1)          # section 5
    assert r["net"][4] == pytest.approx(2.2, abs=0.1)
    assert r["mstar"] == 3
    assert r["c1_margin"] > 0 and r["c2_margin"] > 0


def test_gap_default_point_reproduces_amendment():
    r = MV.gap_point(MV.defaults(MV.GAP_PARAMS))
    assert r["best"] == {10: 4, 20: 5, 45: 6, 90: 7}               # horizon.md amendment table
    assert r["best_ctrl"] == {10: 6, 20: 7, 45: 10, 90: 12}
    assert r["c3_margin"] > 0 and r["c3_7_margin"] > 0 and r["min_shortening"] == 2


def test_vpgg_freedom_default_point():
    r = MV.vpgg_freedom_point((3.0, 0.5, 3))
    assert r["lib_sum"] == pytest.approx(5.263, abs=0.001)         # liberty-v2.md
    assert r["lib_wins"] == 11 and r["emp_wins"] == 11             # liberty-v2.md, empowerment.md
    assert r["lib_holds"] and r["emp_holds"]


def test_household_patch_is_reversible():
    from mar import hedonic as HD
    from mar import negotiation as NG
    from mar.worlds import household as H
    MV.apply_household({"living_cost": 3.0, "BREACH_N": 0.3, "FLOOR": 40.0, "OUT_WEEKS": 13})
    assert HD.DEFAULT.living_cost == 3.0 and H.BREACH_N == 0.3 and NG.FLOOR == 40.0
    assert MV._get_default(H.WeeklyWorld.__init__, "cfg").living_cost == 3.0
    assert MV._get_default(NG.alone_value, "weeks") == 13
    MV.apply_household({})
    o = MV._STATE["orig"]
    assert HD.DEFAULT is o["cfg"] or HD.DEFAULT == o["cfg"]
    assert H.BREACH_N == o["BREACH_N"] and NG.FLOOR == o["FLOOR"]
    assert MV._get_default(NG.alone_value, "weeks") == o["OUT_WEEKS"]
    assert MV._get_default(NG.floor_check, "floor") == o["FLOOR"]
