import random
from fractions import Fraction as Fr

import numpy as np
import pytest

from mar import horizon as Hz


@pytest.fixture(scope="module")
def tab():
    return Hz.Table(Hz.HorizonParams())


def test_state_space_small_and_reachable(tab):
    assert 1000 < len(tab.states) < 100000
    assert tab.reward.shape == (len(tab.states), Hz.NA)


def test_backward_matches_exhaustive_search():
    q = Hz.HorizonParams()
    t = Hz.Table(q)
    for g in (Fr(9, 10), Fr(1)):
        for k in (1, 2, 3, 4):
            _, vopt = Hz.optimal_plan(t, Hz.START, k, float(g))
            _, ex = Hz.exhaustive_best(q, Hz.START, k, g)
            assert vopt == pytest.approx(float(ex), abs=1e-9)


def test_gamma_zero_greedy_is_optimal(tab):
    for K in (1, 5, 26):
        assert Hz.greedy_loss(tab, Hz.START, K, 0.0)["loss"] == pytest.approx(0, abs=1e-9)


def test_state_feedback_off_greedy_is_optimal():
    t = Hz.Table(Hz.HorizonParams().off())
    for g in (0.0, 0.5, 0.9, 1.0):
        for K in (1, 2, 4, 8, 26):
            assert Hz.greedy_loss(t, Hz.START, K, g)["loss"] == pytest.approx(0, abs=1e-9)


def test_feedback_on_greedy_loses(tab):
    assert Hz.greedy_loss(tab, Hz.START, 26, 1.0)["loss"] > 1


def test_loss_never_negative(tab):
    for g in (0.3, 0.9, 1.0):
        for K in (2, 6, 12):
            assert Hz.greedy_loss(tab, Hz.START, K, g)["loss"] >= -1e-9


def test_infinite_horizon_consistent(tab):
    r = Hz.greedy_loss_infinite(tab, Hz.START, 0.9)
    assert r["loss"] >= -1e-9 and r["opt"] > r["greedy"] - 1e-9


def test_symbolic_step_matches_concrete():
    z3 = pytest.importorskip("z3")
    q = Hz.HorizonParams()
    tab = Hz.Table(q)
    rng = random.Random(0)
    for i in rng.sample(range(len(tab.states)), 120):
        s = tab.states[i]
        for a in range(Hz.NA):
            if not Hz.feasible(q, s, a):
                continue
            r, s2 = Hz.step(q, s, a)
            rs, s2s, feas = Hz._sym_step(z3, q, tuple(z3.IntVal(v) for v in s), z3.IntVal(a))
            assert z3.is_true(z3.simplify(feas))
            assert z3.simplify(rs == z3.RealVal(str(r))) and bool(z3.simplify(rs == z3.RealVal(str(r))))
            assert tuple(z3.simplify(v).as_long() for v in s2s) == s2


@pytest.mark.parametrize("gamma", [Fr(9, 10), Fr(1)])
def test_witness_exists_and_z3_checks(gamma):
    pytest.importorskip("z3")
    q = Hz.HorizonParams()
    w = Hz.find_witness(q, gamma, kmax=6)
    assert w is not None and w["k"] <= 6 and w["best_total"] > w["greedy_total"]
    chk = Hz.z3_check_witness(q, w)
    assert chk["greedy_is_greedy_unsat"] and chk["greedy_total_matches"] and chk["best_total_matches"]
    assert chk["better_plan_exists_sat"] and chk["best_is_optimal_unsat"]


def test_no_witness_when_off():
    assert Hz.find_witness(Hz.HorizonParams().off(), Fr(1), kmax=4) is None


def test_lemma_sufficiency_random_mdps():
    """Reward depends on an uncontrolled clock x only (the controlled y moves but is not rewarded): greedy is optimal for every gamma."""
    rng = random.Random(1)
    for _ in range(100):
        nx, ny, na, K = 3, 4, 3, 5
        gx = [rng.randrange(nx) for _ in range(nx)]
        fy = {(y, a): rng.randrange(ny) for y in range(ny) for a in range(na)}
        r = {(x, a): rng.uniform(-1, 1) for x in range(nx) for a in range(na)}
        for gamma in (0.0, 0.7, 1.0):
            def best(x, y, k):
                if k == 0:
                    return 0.0
                return max(r[x, a] + gamma * best(gx[x], fy[y, a], k - 1) for a in range(na))
            x, y, tot = 0, 0, 0.0
            for t in range(K):
                a = max(range(na), key=lambda a: r[x, a])
                tot += gamma ** t * r[x, a]
                x, y = gx[x], fy[y, a]
            assert tot == pytest.approx(best(0, 0, K), abs=1e-9)


def test_lemma_necessity_construction():
    """If two actions lead to different states, a reward exists under which greedy strictly loses at k = 2 whenever gamma > eps."""
    gamma, eps = 0.5, 0.1
    # states: s0 --a--> u ; s0 --b--> v ; reward(s0,a)=0, reward(s0,b)=eps, reward(u,*)=1, reward(v,*)=0
    r0 = {"a": 0.0, "b": eps}
    nxt = {"a": "u", "b": "v"}
    rs = {"u": 1.0, "v": 0.0}
    greedy = max(r0, key=r0.get)
    tot = lambda act: r0[act] + gamma * rs[nxt[act]]
    assert greedy == "b" and tot("a") > tot("b")


def test_concert_spaced_positive_weekly_negative():
    q = Hz.HorizonParams()
    n = lambda m: len(range(m - 1, 26, m))
    per = {m: Hz.concert_gain(q, Hz.START, 26, 0.95, m)["net_carryover"] / n(m) for m in (1, 4)}
    assert per[4] > 0 > per[1]


def test_gap_interior_optimum_unified_self():
    b = Hz.best_gaps(Hz.GapParams())
    assert 1 < b["best_lifetime"] < 200 and b["best_remembered_old"] < b["best_experienced_old"]


def test_special_case_memory_weight_zero_is_old_experienced():
    p = Hz.GapParams()
    for g in (3, 20, 90):
        r = Hz.gap_score(p, g, Hz.PURE_PRESENT)
        assert r["lifetime"] == pytest.approx(r["experienced"], abs=1e-12)
    assert Hz.best_gaps(p, sp=Hz.PURE_PRESENT)["best_lifetime"] == Hz.best_gaps(p)["best_experienced_old"]


def test_special_case_present_weight_zero_is_old_remembered_up_to_scale():
    p = Hz.GapParams()
    ratios = [Hz.gap_score(p, g, Hz.PURE_MEMORY)["memory_cycle"] / Hz.gap_score(p, g, Hz.PURE_MEMORY)["remembered"] for g in (5, 20, 60, 120)]
    assert all(r == pytest.approx(ratios[0], rel=1e-9) for r in ratios) and ratios[0] > 0
    cyc = max(range(1, 201), key=lambda g: Hz.gap_score(p, g, Hz.PURE_MEMORY)["memory_cycle"])
    assert cyc == Hz.best_gaps(p)["best_remembered_old"]


def test_vivid_peaks_and_endings_raise_lifetime_beyond_in_moment():
    sp = Hz.SelfParams()
    assert Hz.trace_value(15.0, sp)["ratio"] > 1
    assert Hz.trace_value(15.0, sp, ending=True)["after_the_fact"] > Hz.trace_value(15.0, sp, ending=False)["after_the_fact"]
    assert Hz.trace_value(15.0, sp)["after_the_fact"] / 15.0 > Hz.trace_value(5.0, sp)["after_the_fact"] / 5.0   # intensity raises vividness


def test_low_vividness_stretch_contributes_little_and_bad_vivid_end_keeps_costing():
    assert Hz.stretch_value(30, 1.0)["memory_share"] < 0.05
    assert Hz.stretch_value(90, 1.0)["memory_share"] < Hz.stretch_value(7, 1.0)["memory_share"]
    bad = Hz.trace_value(-20.0)
    assert bad["after_the_fact"] < bad["in_moment"] < 0            # costs more after the fact than in the moment
    assert bad["after_the_fact"] < Hz.trace_value(-20.0, Hz.SelfParams(rum=1.0))["after_the_fact"]


def test_gap_deeper_friendship_longer_gap():
    gaps = [Hz.best_gaps(Hz.GapParams(H=h))["best_lifetime"] for h in (10, 20, 45, 90)]
    assert gaps == sorted(gaps) and gaps[0] < gaps[-1]


def test_gap_mismatch_costs_the_short_person():
    m = Hz.gap_mismatch(Hz.GapParams(H=20), Hz.GapParams(H=90))
    assert m["mismatch_days"] > 0 and m["short_loss_pct"] > 0
    assert m["closeness_at_meeting_long_gap"] < m["closeness_at_meeting_best"]
