"""H32 convergence model (src/mar/convergence.py, docs/results/h32-prereg.md). Exact; no seeds, no network."""
from dataclasses import replace
from fractions import Fraction as Fr
from itertools import product

from mar import convergence as C

TOY = (C.Activity("x", Fr(1), Fr(0)), C.Activity("y", Fr(1, 2), Fr(1)))


def _total(ev):
    return ev["own"] + ev["vicarious"] + ev["partner"]


def test_all_off_control_gap_is_large():
    """The control the prereg requires (P1): with every mechanism off the egoist and utilitarian diverge."""
    c = C.compare(C.arm(C.ConvParams(), False, False, False), exact=True)
    assert c["R"] >= Fr(15, 100) and c["D"] >= Fr(8, 10) and c["Q"] <= Fr(4, 10)
    assert not C.converged(c)


def test_identity_utilitarian_is_egoist_plus_partner_term():
    """For every arm and for both optimal policies, the DP's utilitarian value equals the evaluated egoist objective
    plus the partner's lifetime pleasure, and the egoist's DP value equals its evaluated objective (exact rationals)."""
    p = C.ConvParams(T=12)
    for a in C.ARMS:
        q = C.arm(p, *a)
        pe, ve = C.solve(q, "egoist", exact=True)
        pu, vu = C.solve(q, "utilitarian", exact=True)
        E, U = C.evaluate(q, pe), C.evaluate(q, pu)
        assert ve[0] == E["actor"] and vu[0] == U["actor"] + U["partner"] == _total(U)
        assert E["total"] - E["actor"] == E["partner"]
        assert vu[0] >= E["actor"] + E["partner"] and ve[0] >= U["actor"]   # each optimum beats the other's policy on its own objective


def test_identity_when_partner_excluded_egoist_ignores_partner():
    """All switches off: the partner's welfare enters nothing the egoist sees, so changing the partner's likings leaves
    the egoist's optimal value unchanged; the utilitarian's value moves only by the partner term."""
    p = C.arm(C.ConvParams(T=10), False, False, False)
    q = replace(p, menu=tuple(C.Activity(m.name, m.lA, 1 - m.lB) for m in p.menu), sB=Fr(7, 10))
    _, ve_p = C.solve(p, "egoist", exact=True)
    _, ve_q = C.solve(q, "egoist", exact=True)
    assert ve_p[0] == ve_q[0]
    for r in (p, q):
        pe, _ = C.solve(r, "egoist", exact=True)
        pu, vu = C.solve(r, "utilitarian", exact=True)
        U = C.evaluate(r, pu)
        assert vu[0] - U["actor"] == U["partner"]


def test_float_solver_matches_exact_on_toy_and_small_default():
    for p in (C.ConvParams(menu=TOY, T=6, eps=Fr(1, 10), w=Fr(1, 2)), C.ConvParams(T=8, o_B=Fr(3, 5))):
        for a in C.ARMS:
            x, y = C.compare(C.arm(p, *a)), C.compare(C.arm(p, *a), exact=True)
            assert (x["D"], x["R"]) == (y["D"], y["R"]), a


def test_amplification_off_means_sharing_adds_nothing_for_actor():
    p = C.ConvParams(amp_on=False, give_on=False)
    for k in range(len(p.menu)):
        assert C.rewards(p, 99, True, (k, "solo"))[0] == C.rewards(p, 99, True, (k, "shared"))[0]
    q = C.ConvParams(amp_on=True, alpha=Fr(1))
    assert C.mult(q, q.menu[3]) == Fr(17, 10) and C.mult(q, q.menu[0]) == Fr(101, 100)


def test_no_exit_partner_never_leaves_and_blind_exit_is_policy_free():
    p = C.arm(C.ConvParams(T=10, o_B=Fr(9, 10)), False, True, False)
    for obj in C.OBJECTIVES:
        pol, _ = C.solve(p, obj)
        assert C.evaluate(p, pol)["together_at_end"] == 1
    # w = 0: the exit estimate ignores the partner's pleasure, so whether the partner leaves cannot depend on the policy
    b = C.arm(C.ConvParams(T=10, w=Fr(0)), True, True, False)
    ends = {C.evaluate(b, C.solve(b, obj)[0])["together_at_end"] for obj in C.OBJECTIVES}
    assert len(ends) == 1


def test_solitary_has_no_partner_and_no_upkeep():
    s = C.solitary(C.ConvParams(T=4))
    assert s["vicarious"] == 0 and s["together_at_end"] == 0
    assert s["own"] == Fr(1) + Fr(9, 10) + Fr(1) + Fr(9, 10)


def test_shapley_is_exact_and_efficient():
    vals = {a: Fr(sum(a)) + (Fr(1, 2) if a[1] and a[2] else 0) for a in product((False, True), repeat=3)}
    phi = C.shapley(vals)
    assert sum(phi.values()) == vals[(True, True, True)] - vals[(False, False, False)]
    assert phi["exit"] == 1 and phi["amp"] == phi["give"] == Fr(5, 4)


# ---------------------------------------------------------------- H32b voice ladder (docs/results/h32b-prereg.md)

def test_h32b_ladder_off_reproduces_committed_h32_defaults():
    import json
    from pathlib import Path
    kept = json.loads((Path(__file__).parent.parent / "experiments/kept/h32-2026-11-11/results.json").read_text())["default"]
    assert C.ConvParams().ladder == ()
    for a in C.ARMS:
        c = C.compare(C.arm(C.ConvParams(), *a))
        k = kept[C.arm_name(a)]
        assert abs(float(c["D"]) - k["D"]) < 1e-12 and abs(float(c["R"]) - k["R"]) < 1e-12, a


def test_h32b_empty_ladder_is_cliff_and_ladder_changes_nothing_without_exit():
    p = C.ConvParams(menu=TOY, T=8, o_B=Fr(2, 5))
    for a in C.ARMS:
        x = C.compare(C.arm(p, *a), exact=True)
        if not a[0]:   # exit off: the ladder is never consulted
            y = C.compare(C.arm(replace(p, ladder=C.RUNGS), *a), exact=True)
            assert (x["D"], x["R"], x["E"]["total"]) == (y["D"], y["R"], y["E"]["total"])


def test_h32b_ladder_mechanics():
    p = C.ConvParams(ladder=C.RUNGS, o_B=Fr(3, 5))
    s = (5, Fr(1, 2), True, 0)
    # e falls well below every threshold, but the level rises only one step a week, and nobody exits from level 0
    (pr, s2), = C.transitions(p, s, (0, "solo"), Fr(0))
    assert pr == 1 and s2[2] and s2[3] == 1
    # on the renegotiation rung, a week the partner does not like jumps it to withdrawal
    (pr, s3), = C.transitions(p, (5, Fr(1, 2), True, 2), (0, "shared"), Fr(1, 2))
    assert s3[3] == 3
    # renegotiation as the last rung: breaking the demand means exit
    q = replace(p, ladder=("renegotiate",))
    assert C.transitions(q, (5, Fr(1), True, 1), (0, "shared"), Fr(1))[0][1][2] is False
    # withdrawal halves the amplification bonus
    own_w = C.rewards(p, 99, True, (3, "shared"), 3)[0]
    own = C.rewards(p, 99, True, (3, "shared"), 0)[0]
    assert own - own_w == p.menu[3].lA * (C.mult(p, p.menu[3]) - 1) / 2
    # exit only from the top level when e < o_B
    leave = C.transitions(p, (5, Fr(1, 2), True, 3), (0, "solo"), Fr(0))
    assert leave[0][1][2] is False
