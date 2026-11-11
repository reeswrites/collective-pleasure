"""H35 care dynamics (src/mar/care.py, docs/results/h35-prereg.md). Exact; no seeds."""
from dataclasses import replace
from fractions import Fraction as Fr

from mar import care as K
from mar import convergence as C

TOY = (C.Activity("x", Fr(1), Fr(0)), C.Activity("y", Fr(1, 2), Fr(1)))
TB = replace(C.ConvParams(menu=TOY, T=8, alpha=Fr(2)), exit_on=False, amp_on=True, give_on=False)


def test_frozen_care_reproduces_the_h32_egoist():
    """With up = down = 0 care never moves, so both egoists are the H32 egoist (giving on at g = g0)."""
    for g0 in (Fr(0), Fr(1, 2)):
        cp = K.CareParams(base=TB, g0=g0, up=0, down=0)
        h = C.solve(replace(TB, give_on=True, g=g0), "egoist")[0]
        for kind in ("naive", "sophisticated"):
            pol = K.policies(cp)[kind]
            ev = K.run_path(cp, pol)
            ref = C.evaluate(replace(TB, give_on=True, g=g0), h)
            assert ev["own"] == ref["own"] and ev["vicarious"] == ref["vicarious"] and ev["partner"] == ref["partner"]


def test_care_steps_and_rupture():
    cp = K.CareParams(base=TB, rupture=(2, 2))
    s = C.start_state(TB)
    assert K.amplified(cp, s, (1, "shared")) and not K.amplified(cp, s, (1, "solo")) and not K.amplified(cp, s, (0, "shared"))
    assert K.g_next(cp, Fr(1), s, (1, "shared")) == 1 and K.g_next(cp, Fr(0), s, (0, "solo")) == 0
    assert K.g_next(cp, Fr(1, 2), s, (1, "shared")) == Fr(11, 20)
    assert all(a[1] == "solo" for a in K.actions(cp, 2, True)) and any(a[1] == "shared" for a in K.actions(cp, 4, True))


def test_utilitarian_ignores_care_and_float_matches_exact():
    for g0 in (Fr(0), Fr(1)):
        cp = K.CareParams(base=TB, g0=g0, rupture=(3, 2))
        a, b = K.cell(cp), K.cell(cp, exact=True)
        assert a["U"]["pair"] == b["U"]["pair"]
        for k in ("naive", "sophisticated"):
            assert a[k]["D"] == b[k]["D"] and a[k]["g_final"] == b[k]["g_final"]
    u0 = K.cell(K.CareParams(base=TB, g0=Fr(0)))["U"]
    u1 = K.cell(K.CareParams(base=TB, g0=Fr(1)))["U"]
    assert u0["occupancy"] == u1["occupancy"]


def test_withdrawal_can_unamplify_a_week():
    p = replace(TB, exit_on=True, ladder=("withdraw",), alpha=Fr(6, 5))   # bonus 0.3 at full, 0.15 withdrawn
    cp = K.CareParams(base=p)
    assert K.amplified(cp, (2, Fr(1), True, 0), (1, "shared"))
    assert not K.amplified(cp, (2, Fr(1), True, 1), (1, "shared"))
