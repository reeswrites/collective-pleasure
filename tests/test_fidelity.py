import numpy as np

from mar import fidelity as F
from mar import negotiation as NG
from mar import stats as S


def test_verdict_rule():
    ci_in = S.Interval(0.2, 0.15, 0.25)
    ci_cross = S.Interval(0.2, 0.05, 0.35)
    assert F.verdict(0.2, ci_in, 0.01, +1, 0.1) == "reproduces"
    assert F.verdict(0.2, ci_cross, 0.01, +1, 0.1) == "weak support"
    assert F.verdict(0.2, ci_in, 0.2, +1, 0.1) == "does not reproduce"
    assert F.verdict(-0.2, S.Interval(-0.2, -0.25, -0.15), 0.01, -1, 0.1) == "reproduces"
    assert F.verdict(0.2, ci_in, 0.01, -1, 0.1) == "does not reproduce"


def test_bargaining_outside_option_binds_only_with_exit():
    hi, lo = F.p1b_cell("exit-allowed", 0.9, 0.1)
    assert hi - lo > 0.05
    chi, clo = F.p1b_cell("no-exit", 0.9, 0.1)
    assert abs(chi - clo) < 1e-9


def test_hand_pairs_and_personas():
    assert len(F.hand_pairs()) == 15
    assert len(F.personas9()) == 9


def test_default_terms_differ_in_three():
    assert F.DIFF_TERMS == ["contribution", "use", "taking"]


def test_p1a_p3_run_and_default_nonnegative():
    a, b = F.hand_pairs()[3]
    base = NG.base_cards("author_seed_v2_bindable")
    r = F.p1a_one(a, b, 900, base)
    assert r is None or r[1] >= r[0] - 1e-9          # raising a member's outside option never lowers their agreed value in the pilot pair
    r3 = F.p3_one(a, b, 900, base)
    assert r3 is None or all(0.0 <= x <= 1.0 for x in r3)


def test_base_model_has_no_adaptation_but_lever_does():
    p = F.personas9()[0]
    first, last, rel = F.p6_persona(p)
    assert first > 0 and abs(rel) < 1e-9
    s1, s20 = F.adaptation_control()
    assert s20 < 0.5 * s1


def test_contact_veto_inert_on_pilot_pair():
    a, b = F.hand_pairs()[0]
    assert F.same_run(F.weekly("trap", a, b, 0), F.weekly("contact_free", a, b, 0))
