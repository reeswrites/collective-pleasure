"""Liking vs wanting (ADR 0018 test 1, src/mar/wanting.py). Controls and the required reproduction test."""
import numpy as np
import pytest

from mar import horizon as Hz
from mar import wanting as Wg

SMALL = Wg.WantParams(enabled=True, days=7, L=3)
ENVS = (Wg.PLAIN, Wg.HEAVY)
RULES = (Wg.NO_RULE, Wg.CLOSURE, Wg.CAP)


@pytest.fixture(scope="module")
def htab():
    return Hz.Table(Hz.HorizonParams())


@pytest.mark.parametrize("gamma", [0.5, 0.9, 1.0])
@pytest.mark.parametrize("K", [4, 26])
def test_flag_off_reproduces_horizon_greedy(htab, gamma, K):
    """Required: with no wanting table (flag off) or wanting equal to liking, the wanting-greedy agent IS horizon's greedy."""
    ref = Hz.run_policy(htab, Hz.START, K, gamma, Hz.greedy_policy(htab))
    off = Hz.run_policy(htab, Hz.START, K, gamma, Wg.wanting_greedy_policy(htab))
    eq = Hz.run_policy(htab, Hz.START, K, gamma, Wg.wanting_greedy_policy(htab, htab.reward.copy()))
    assert off == ref and eq == ref


def test_horizon_greedy_loss_unchanged(htab):
    """The horizon study's headline numbers are untouched (module imports horizon, changes nothing)."""
    r = Hz.greedy_loss(htab, Hz.START, 26, 1.0)
    assert r["pct"] == pytest.approx(24.5, abs=0.05)
    assert Hz.greedy_loss(htab, Hz.START, 26, 0.9)["pct"] == pytest.approx(3.2, abs=0.05)


@pytest.mark.parametrize("env", ENVS)
@pytest.mark.parametrize("rule", RULES)
def test_flag_off_means_wanting_equals_liking(env, rule):
    q = Wg.WantParams(enabled=False, days=7, L=3)
    tab = Wg.WTable(q, env, rule)
    assert np.array_equal(tab.want, tab.reward)
    r = Wg.solve_all(q, env, rule)
    assert r["W"]["plan"] == r["L"]["plan"]
    assert r["W"]["gap_per_unit"] == 0.0 and r["W"]["liking_to_wanting"] == 1.0
    assert r["W"]["liking_per_cued_unit"] == Wg.NM


@pytest.mark.parametrize("env", ENVS)
@pytest.mark.parametrize("rule", RULES)
def test_wanting_equal_liking_gap_exactly_zero(env, rule):
    q = SMALL.equal()
    r = Wg.solve_all(q, env, rule)
    for ag in Wg.AGENTS:
        assert r[ag]["gap_per_unit"] == 0.0
        assert r[ag]["cued_units"] == 0
        assert r[ag]["liking_per_cued_unit"] == Wg.NM
    assert r["W"]["plan"] == r["L"]["plan"]


@pytest.mark.parametrize("env", ENVS)
def test_sensitization_off_no_divergence(env):
    q = Wg.WantParams(enabled=True, days=14, L=3).no_sensitization()
    r = Wg.solve_all(q, env, Wg.NO_RULE)
    for ag in ("W", "O"):
        d = r[ag]["divergence"]
        assert d == Wg.NM or abs(d) < 1e-9


def test_sensitization_on_does_diverge_in_heavy():
    r = Wg.solve_all(Wg.WantParams(enabled=True, days=14, L=4), Wg.HEAVY, Wg.NO_RULE)
    assert r["W"]["divergence"] != Wg.NM and r["W"]["divergence"] > 0


def test_environments_and_closure_change_only_wanting():
    """P0: liking tables (so the optimizer) are identical across environments and the closure ritual."""
    tabs = [Wg.WTable(SMALL, e, u) for e in ENVS for u in (Wg.NO_RULE, Wg.CLOSURE)]
    for t in tabs[1:]:
        assert t.states == tabs[0].states and np.array_equal(t.reward, tabs[0].reward)
    plans = {Wg.solve(SMALL, e, u, "O")["plan"] for e in ENVS for u in (Wg.NO_RULE, Wg.CLOSURE)}
    assert len(plans) == 1


def test_cap_rule_enforced():
    r = Wg.solve_all(SMALL, Wg.HEAVY, Wg.CAP)
    for ag in Wg.AGENTS:
        plan = r[ag]["plan"]
        for d in range(SMALL.days):
            assert plan[d * SMALL.L:(d + 1) * SMALL.L].count("G") <= 2


def test_optimizer_beats_greedy_agents():
    for e in ENVS:
        r = Wg.solve_all(SMALL, e, Wg.NO_RULE)
        assert r["O"]["total_liking"] >= r["L"]["total_liking"] - 1e-9
        assert r["O"]["total_liking"] >= r["W"]["total_liking"] - 1e-9


def test_optimizer_matches_horizon_backward_values():
    """The optimizer's rollout total equals horizon's exact backward-induction value on the same table."""
    q = SMALL
    tab = Wg.WTable(q, Wg.HEAVY, Wg.NO_RULE)
    T = q.days * q.L
    V = Hz.backward_values(tab, T, 1.0)
    assert Wg.solve(q, Wg.HEAVY, Wg.NO_RULE, "O", tab)["total_liking"] == pytest.approx(V[T][0], abs=1e-9)


def test_not_measurable_never_zero():
    m = Wg.measures(SMALL, Wg.Run(acts=[Wg.Q_] * 21, like=[3.0] * 21, want=[3.0] * 21, cued=[False] * 21,
                                  day=[t // 3 for t in range(21)], sessions=[]))
    for k in ("liking_per_cued_unit", "closure_rate", "next_day_verdict", "divergence"):
        assert m[k] == Wg.NM


def test_closure_counts_clock_cutoffs_as_open():
    q = Wg.WantParams(enabled=True, days=1, L=4)
    tab = Wg.WTable(q, Wg.HEAVY, Wg.NO_RULE)
    run = Wg.rollout(tab, lambda t, i: Wg.G_)              # GGGG until bedtime: one session cut by the clock
    assert Wg.measures(q, run)["closure_rate"] == 0.0
    run2 = Wg.rollout(tab, lambda t, i: [Wg.G_, Wg.G_, Wg.Q_, Wg.Q_][t])   # stop after one episode
    assert Wg.measures(q, run2)["closure_rate"] == 1.0


def test_flag_against_twin():
    a = {"G_units": 10, "mean_liking": 4.0}
    assert Wg.flag(a, {"G_units": 5, "mean_liking": 4.5})
    assert not Wg.flag(a, {"G_units": 5, "mean_liking": 3.0})
    assert not Wg.flag(a, {"G_units": 10, "mean_liking": 5.0})


def test_personas_deterministic():
    a = Wg.draw_personas(Wg.WantParams(enabled=True), 5, 1)
    b = Wg.draw_personas(Wg.WantParams(enabled=True), 5, 1)
    assert a == b and all(x.enabled for x in a)
