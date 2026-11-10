import itertools

import pytest

from mar.games import bargaining as B

G = [0, 0.1, 0.2, 0.3, 0.4, 0.5]
D = [(0.9, 0.9), (0.9, 0.7), (0.7, 0.9)]


def gate(name):
    return B.BGate(B.load_regime(name))


def test_cards_have_gloss_and_both_sources():
    for r in B.REGIMES:
        cs = B.load_regime(r)
        assert len(cs) == 3
        assert all(c.gloss and "Rubinstein" in c.source and "Binmore" in c.source for c in cs)


def test_proof_checks_separate_regimes():
    ex = {c["check"]: c for c in B.check_spec(B.load_regime("exit-allowed"))}
    ne = {c["check"]: c for c in B.check_spec(B.load_regime("no-exit"))}
    assert ex["exit_path"]["verdict"] == "pass" and ex["exit_path"]["periods"] == [0, 1, 2, 3, 4]
    assert ne["exit_path"]["verdict"] == "fail" and "k=5" in ne["exit_path"]["bound"]
    assert ex["b_no_deadlock"]["verdict"] == ne["b_no_deadlock"]["verdict"] == "pass"


def test_rubinstein_known_value():
    assert B.rubinstein_share(0.9, 0.9) == pytest.approx(1 / 1.9)
    assert B.rubinstein_share(0.5, 0.5) == pytest.approx(2 / 3)


def test_closed_form_matches_fixed_point_iteration():
    for (d1, d2), o1, o2 in itertools.product(D, G, G):
        p1 = p2 = 0.5
        for _ in range(3000):
            p1, p2 = 1 - max(o2, d2 * p2), 1 - max(o1, d1 * p1)
        assert B.outside_option_split(d1, d2, o1, o2)[0] == pytest.approx(p1, abs=1e-9)


def test_gate_blocks_exit_only_under_no_exit():
    assert gate("exit-allowed").check(0, "exit")[0]
    ok, why = gate("no-exit").check(3, "exit")
    assert not ok and why == ["N1-must-not-exit"]
    assert gate("no-exit").check(3, "agree")[0]


def test_freedom_zero_without_exit_or_without_value():
    ex, ne = gate("exit-allowed"), gate("no-exit")
    assert B.freedom(ne, (0.9, 0.9), (0.4, 0.4)) == 0
    assert B.freedom(ex, (0.9, 0.9), (0.0, 0.0)) == 0      # sham exit
    assert B.freedom(ex, (0.9, 0.9), (0.3, 0.3)) == pytest.approx(1.0)
    assert B.freedom(ex, (0.9, 0.9), (0.3, 0.0)) == pytest.approx(0.5)


def test_ultimatum_at_last_period():
    th, vp, _, _ = B.table(0.9, 0.9, 0, 0, 3, False)
    assert th[2] == 0 and vp[2] == 1          # last proposer keeps everything
    assert vp[1] == pytest.approx(1 - 0.9)     # responder can get d * 1 by waiting


def test_blocked_exit_falls_back_and_is_counted():
    r = B.play(gate("no-exit"), (B.Stubborn(), B.Stubborn()), (0.9, 0.9), (0.5, 0.5), T=10)
    assert r.outcome == "deadline" and r.blocked > 0 and r.u1 == r.u2 == 0
    r = B.play(gate("exit-allowed"), (B.Stubborn(), B.Stubborn()), (0.9, 0.9), (0.5, 0.5), T=10)
    assert r.outcome == "exit" and r.u1 == pytest.approx(0.5)


def test_eq_no_exit_is_rubinstein_independent_of_options():
    ne = gate("no-exit")
    for d in D:
        for o in [(0, 0), (0.5, 0.5), (0.1, 0.5)]:
            r = B.play(ne, (B.EQ(), B.EQ()), d, o)
            assert r.outcome == "agree" and r.t == 0
            assert r.x1 == pytest.approx(B.rubinstein_share(*d), abs=0.02)
