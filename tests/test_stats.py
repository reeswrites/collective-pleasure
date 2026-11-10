import math

import numpy as np
import pytest

from mar import stats as S


def test_clopper_pearson_known_values():
    # R: binom.test(3, 10)$conf.int -> 0.0667, 0.6525
    ci = S.clopper_pearson(3, 10)
    assert ci.lo == pytest.approx(0.0667, abs=5e-4) and ci.hi == pytest.approx(0.6525, abs=5e-4)
    z = S.clopper_pearson(0, 10)
    assert z.lo == 0.0 and z.hi == pytest.approx(1 - 0.025 ** (1 / 10), abs=1e-6)
    f = S.clopper_pearson(10, 10)
    assert f.hi == 1.0 and f.lo == pytest.approx(0.025 ** (1 / 10), abs=1e-6)


def test_clopper_pearson_contains_wilson_centre():
    for k, n in [(1, 6), (5, 6), (20, 40)]:
        cp, w = S.clopper_pearson(k, n), S.wilson(k, n)
        assert cp.lo <= w.lo + 1e-9 and cp.hi >= w.hi - 1e-9


def test_permutation_exact_hand_case():
    # a = [4,5,6], b = [1,2,3]: only 1 of C(6,3)=20 arrangements is as extreme one-sided
    r = S.permutation_test([4, 5, 6], [1, 2, 3], alternative="greater")
    assert r.exact and r.p == pytest.approx(1 / 20)
    r2 = S.permutation_test([4, 5, 6], [1, 2, 3])
    assert r2.p == pytest.approx(2 / 20)
    assert S.permutation_test([4, 5, 6], [1, 2, 3], alternative="less").p == 1.0


def test_paired_sign_flip_exact():
    r = S.permutation_test([2, 3, 4, 5], [1, 1, 1, 1], paired=True, alternative="greater")
    assert r.exact and r.p == pytest.approx(1 / 16)
    assert S.permutation_test([2, 3, 4, 5], [1, 1, 1, 1], paired=True).p == pytest.approx(2 / 16)


def test_permutation_calibrated_under_null():
    rng = np.random.default_rng(1)
    ps = [S.permutation_test(rng.standard_normal(15), rng.standard_normal(15), n_perm=499, seed=i).p for i in range(300)]
    assert np.mean(np.array(ps) <= 0.05) < 0.09


def test_permutation_monte_carlo_matches_exact():
    a, b = [1.0, 2, 2, 3, 5, 8], [1.0, 1, 2, 2, 3, 3, 4]
    ex = S.permutation_test(a, b)
    mc = S.permutation_test(a, b, exact_limit=0, n_perm=40000, seed=3)
    assert ex.exact and not mc.exact and mc.p == pytest.approx(ex.p, abs=0.012)


def test_bootstrap_ci_covers_known_mean_and_is_seeded():
    rng = np.random.default_rng(0)
    x = rng.normal(10, 2, 60)
    ci = S.bootstrap_ci(x, seed=5)
    assert ci.lo < 10 < ci.hi and ci == S.bootstrap_ci(x, seed=5)
    se = 2 / math.sqrt(60)
    assert (ci.hi - ci.lo) == pytest.approx(2 * 1.96 * se, rel=0.3)
    bca = S.bootstrap_ci(x, method="bca", seed=5)
    assert bca.lo < 10 < bca.hi


def test_bootstrap_coverage():
    rng = np.random.default_rng(2)
    hits = sum(S.bootstrap_ci(rng.normal(0, 1, 25), n_boot=400, seed=i).contains(0.0) for i in range(200))
    assert 0.88 <= hits / 200 <= 0.99


def test_bootstrap_degenerate():
    ci = S.bootstrap_ci([3.0, 3.0, 3.0])
    assert ci.lo == ci.hi == 3.0 and "degenerate" in ci.method
    assert S.bootstrap_ci([1.0]).lo == 1.0


def test_cluster_bootstrap_wider_than_naive_when_clustered():
    # 6 pairings, perfectly constant within pairing: naive treats 36 values as independent
    vals, cl = [], []
    for k, level in enumerate([0.1, 0.3, 0.5, 0.7, 0.9, 0.2]):
        vals += [level] * 6
        cl += [k] * 6
    naive = S.bootstrap_ci(vals, seed=1)
    clustered = S.cluster_bootstrap_ci(vals, cl, seed=1)
    assert clustered.estimate == pytest.approx(np.mean(vals))
    assert (clustered.hi - clustered.lo) > (naive.hi - naive.lo) * 1.5


def test_diff_ci_paired_and_unpaired():
    ci = S.bootstrap_diff_ci([5, 6, 7, 8], [1, 2, 3, 4], paired=True)
    assert ci.estimate == 4 and ci.lo == ci.hi == 4  # constant differences
    ci2 = S.bootstrap_diff_ci([5, 6, 7, 8], [1, 2, 3, 4])
    assert ci2.estimate == 4 and ci2.lo < 4 < ci2.hi


def test_effect_sizes_hand_cases():
    assert S.cliffs_delta([4, 5, 6], [1, 2, 3]) == 1.0
    assert S.cliffs_delta([1, 2, 3], [1, 2, 3]) == 0.0
    assert S.cliffs_delta([1, 2], [2, 3]) == pytest.approx(-0.75)
    assert S.cohens_d([2, 4, 6], [1, 3, 5]) == pytest.approx(0.5)
    assert math.isfinite(S.cohens_d([3, 5, 8], [1, 2, 3], paired=True))
    ci = S.cliffs_delta_ci([4, 5, 6, 7], [1, 2, 3, 4])
    assert ci.lo <= ci.estimate <= ci.hi


def test_risk_difference_and_ratio():
    rd = S.risk_difference(30, 50, 10, 50)
    assert rd.estimate == pytest.approx(0.4) and 0.2 < rd.lo < 0.4 < rd.hi < 0.6
    rr = S.risk_ratio(30, 50, 10, 50)
    assert rr.estimate == pytest.approx(3.0) and rr.lo < 3 < rr.hi and rr.lo > 1.4
    assert S.risk_ratio(0, 10, 5, 10).hi > 0  # zero cell handled


def test_fisher_known():
    # classic tea-tasting: 3/4 vs 1/4 -> one-sided p = 17/70... here 4 vs 0 of 4: p = 1/70
    assert S.fisher_exact_p(4, 4, 0, 4, "greater") == pytest.approx(1 / 70)
    assert S.fisher_exact_p(4, 4, 0, 4) == pytest.approx(2 / 70)


def test_sign_test():
    assert S.sign_test(10, 10) == pytest.approx(1 / 1024)
    assert S.sign_test(5, 10, alternative="two-sided") == 1.0


def test_holm():
    adj = S.holm([0.01, 0.04, 0.03])
    assert adj == pytest.approx([0.03, 0.06, 0.06])
    assert S.holm([0.5, None, 0.01]) == pytest.approx([0.5, None, 0.02])
    assert all(a >= p for a, p in zip(S.holm([0.2, 0.3, 0.001]), [0.2, 0.3, 0.001]))


def test_power_increases_with_n_and_effect():
    lo = S.power_two_arm(1.0, 1.0, 5, n_sim=150, n_perm=199)
    hi = S.power_two_arm(1.0, 1.0, 30, n_sim=150, n_perm=199)
    assert lo < hi and hi > 0.9
    null = S.power_two_arm(0.0, 1.0, 20, n_sim=300, n_perm=199)
    assert null < 0.1


def test_seeds_for_power_matches_closed_form():
    # two-sample d = 1: classic answer about 17 per arm for 80% power at alpha .05
    n = S.seeds_for_power(1.0, 1.0, n_sim=200)
    assert 12 <= n <= 24
    # paired d_z = 0.5 -> about 32 pairs by z-approx
    zn = S.seeds_for_margin(1.0, 0.5)
    assert zn == 32
    assert S.seeds_for_power(0.0, 1.0) is None
    assert S.seeds_for_power(5.0, 0.0) == 2


def test_power_binomial():
    assert S.power_binomial(0.9, 0.1, 10, n_sim=200) > 0.9
    assert S.power_binomial(0.5, 0.5, 20, n_sim=400) < 0.08
