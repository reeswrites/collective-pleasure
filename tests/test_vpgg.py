import numpy as np
import pytest

from mar.cards import load_cards
from mar.games import vpgg as V

P = V.Params()


def cards(name):
    return load_cards(f"rules/vpgg/{name}")


def test_cards_have_gloss_and_paper_source():
    for name in ("compulsory", "voluntary"):
        cs = cards(name)
        assert len(cs) == 3
        assert all(c.gloss and "Hauert" in c.source and "2002" in c.source for c in cs)


def test_group_payoffs_hand_computed():
    # 5 joiners, 2 contributors, r=3, c=1: P_d = 3*2/5 = 1.2, P_c = 0.2
    a, pc, pd = V.group_payoffs(0, 2, 3, 3, 1, 1)
    assert (a, round(pc, 10), round(pd, 10)) == (1, 0.2, 1.2)
    # 1 abstainer, 4 joiners, 3 contributors: P_d = 9/4 = 2.25, P_c = 1.25
    a, pc, pd = V.group_payoffs(1, 3, 1, 3, 1, 1)
    assert (a, pc, pd) == (1, 1.25, 2.25)
    # all cooperate, S=5: P_c = r - 1 = 2 ; all defect: 0
    assert V.group_payoffs(0, 5, 0, 3, 1, 1)[1] == 2.0
    assert V.group_payoffs(0, 0, 5, 3, 1, 1)[2] == 0.0
    # S=1: the single joiner acts as a loner
    assert V.group_payoffs(4, 1, 0, 3, 1, 1) == (1, 1, 1)
    assert V.group_payoffs(4, 0, 1, 3, 1, 1) == (1, 1, 1)


def test_defector_always_beats_cooperator_in_a_group():
    for s in range(2, 6):
        for nc in range(1, s):
            _, pc, pd = V.group_payoffs(5 - s, nc, s - nc, 3, 1, 1)
            assert pd - pc == pytest.approx(1.0)


def test_paper_example_footnote_24():
    # footnote 24: N=10, r=5. Group A 8C+2D: cooperators $3, defectors $4. Group B 2C+8D: C $0, D $1.
    _, pc, pd = V.group_payoffs(0, 8, 2, 5, 1, 0.5)
    assert (pc, pd) == (3.0, 4.0)
    _, pc, pd = V.group_payoffs(0, 2, 8, 5, 1, 0.5)
    assert (pc, pd) == (0.0, 1.0)


def test_wellmixed_formula_matches_group_payoffs_by_monte_carlo():
    rng = np.random.default_rng(1)
    xc, xd, xl = 0.3, 0.3, 0.4
    sums = {"C": [0.0, 0], "D": [0.0, 0]}
    for _ in range(40000):
        grp = rng.choice(3, size=5, p=[xc, xd, xl])
        na, nco, nd = int((grp == 2).sum()), int((grp == 0).sum()), int((grp == 1).sum())
        _, pc, pd = V.group_payoffs(na, nco, nd, 3, 1, 1)
        for who, pay, n in (("C", pc, nco), ("D", pd, nd)):
            sums[who][0] += pay * n
            sums[who][1] += n
    pc_f, pd_f, _ = V.wellmixed_payoffs(xc, xd, xl, 5, 3, 1)
    assert sums["C"][0] / sums["C"][1] == pytest.approx(pc_f, abs=0.03)
    assert sums["D"][0] / sums["D"][1] == pytest.approx(pd_f, abs=0.03)


def test_paper_equilibrium_payoffs_equal_sigma():
    pc, pd, pl = V.wellmixed_payoffs(0.27, 0.27, 0.46, 5, 3, 1)
    assert pc == pytest.approx(1.0, abs=0.01) and pd == pytest.approx(1.0, abs=0.01) and pl == 1


def test_gate_blocks_abstain_only_under_compulsory():
    comp, vol = V.VPGate(cards("compulsory")), V.VPGate(cards("voluntary"))
    for n in V.INVITED_RANGE:
        ok, why = comp.check(n, "abstain")
        assert not ok and why == ["C1-must-join"]
        assert comp.check(n, "join")[0] and comp.check(n, "contribute")[0]
        assert all(vol.check(n, a)[0] for a in ("join", "contribute", "abstain"))


def test_effective_actions_fall_back_to_join_when_blocked():
    eff, blocked = V.effective_actions(V.VPGate(cards("compulsory")), 5)
    assert eff == {"C": "contribute", "D": "join", "L": "join"} and blocked == ["L"]
    eff, blocked = V.effective_actions(V.VPGate(cards("voluntary")), 5)
    assert eff["L"] == "abstain" and blocked == []


def test_proof_checks():
    vol = {c["check"]: c for c in V.check_spec(cards("voluntary"), 3)}
    comp = {c["check"]: c for c in V.check_spec(cards("compulsory"), 3)}
    assert vol["exit_available"]["verdict"] == "pass" and "k=3" in vol["exit_available"]["bound"]
    assert comp["exit_available"]["verdict"] == "fail"
    assert len(comp["exit_available"]["failing"]) == 15  # 3 roles x 5 invited states
    assert vol["b_no_deadlock"]["verdict"] == comp["b_no_deadlock"]["verdict"] == "pass"


def test_real_option_guard():
    assert V.real_option(5, 3, 1, 1.0)
    assert not V.real_option(5, 3, 1, 2.5)  # sigma above any join payoff: loner always wins
    lo, hi = V.join_payoff_range(5, 3, 1)
    assert lo == pytest.approx(-0.4) and hi == pytest.approx(2.4)
    # Delta by the prereg formula r c (N-1)/N - (r c/N - c) = 2.4 + 0.4 = 2.8 (the prereg text says 3.2: arithmetic slip)
    assert V.Params().delta() == pytest.approx(2.8)


def test_params_reject_out_of_range():
    with pytest.raises(AssertionError):
        V.Params(sigma=2.5).check()
    with pytest.raises(AssertionError):
        V.Params(r=5.0).check()


def test_run_is_deterministic_and_small_run_scores():
    p = V.Params(pop=500, generations=60, burn_in=20)
    a = V.run(cards("voluntary"), 3, p)
    b = V.run(cards("voluntary"), 3, p)
    assert np.array_equal(a["shares"], b["shares"])
    assert a["freedom"] == 1.0 and 0 <= a["cooperation"] <= 1
    c = V.run(cards("compulsory"), 3, p)
    assert c["freedom"] == 0.0 and c["blocked_share"] >= 0
    assert np.allclose(a["shares"].sum(1), 1)
