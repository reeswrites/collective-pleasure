"""Statistics layer (ADR 0015). Pure numpy plus the standard library.

Everything is seeded and deterministic. Conventions:

* A *unit of resampling* is chosen by the caller and named in the prereg: the
  seed (independent runs), or a pairing/cluster (all seeds of one pairing move
  together). `cluster_bootstrap_ci` resamples clusters.
* Permutation tests are exact when the number of arrangements is at most
  `exact_limit`, Monte Carlo (with the +1 correction) otherwise.
* Intervals are two-sided at `1 - alpha`. A one-sided test is reported by its
  p-value, not by a one-sided interval.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from statistics import NormalDist
from typing import Callable, Sequence

import numpy as np

_N = NormalDist()


@dataclass(frozen=True)
class Interval:
    estimate: float
    lo: float
    hi: float
    alpha: float = 0.05
    method: str = ""

    def contains(self, x: float) -> bool:
        return self.lo <= x <= self.hi

    def __str__(self) -> str:
        return f"{self.estimate:.4g} [{self.lo:.4g}, {self.hi:.4g}]"


@dataclass(frozen=True)
class TestResult:
    statistic: float
    p: float
    alternative: str
    exact: bool
    n_perm: int


def _arr(x) -> np.ndarray:
    return np.asarray(x, dtype=float).ravel()


# ---------------------------------------------------------------- bootstrap

def _bca_interval(x: np.ndarray, stat: Callable, boots: np.ndarray, theta: float, alpha: float) -> tuple[float, float]:
    prop = float(np.mean(boots < theta)) + 0.5 * float(np.mean(boots == theta))
    prop = min(max(prop, 1e-6), 1 - 1e-6)
    z0 = _N.inv_cdf(prop)
    n = len(x)
    jack = np.array([stat(np.delete(x, i)) for i in range(n)]) if n > 2 else np.array([theta])
    d = jack.mean() - jack
    den = 6.0 * (np.sum(d ** 2) ** 1.5)
    a = float(np.sum(d ** 3) / den) if den > 0 else 0.0
    out = []
    for q in (alpha / 2, 1 - alpha / 2):
        zq = _N.inv_cdf(q)
        adj = _N.cdf(z0 + (z0 + zq) / (1 - a * (z0 + zq)))
        out.append(float(np.quantile(boots, min(max(adj, 0.0), 1.0))))
    return out[0], out[1]


def bootstrap_ci(x, stat: Callable = np.mean, *, n_boot: int = 10000, alpha: float = 0.05,
                 seed: int = 0, method: str = "percentile") -> Interval:
    """Bootstrap CI for `stat(x)`, resampling the elements of x (the unit is one element,
    usually one seed). method: 'percentile' or 'bca'. A single observation gives a
    degenerate interval and should be reported as not testable by the caller."""
    x = _arr(x)
    theta = float(stat(x))
    if len(x) < 2 or np.all(x == x[0]):
        return Interval(theta, theta, theta, alpha, method + "-degenerate")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    boots = np.array([stat(x[i]) for i in idx]) if stat is not np.mean else x[idx].mean(axis=1)
    if method == "bca":
        lo, hi = _bca_interval(x, stat, boots, theta, alpha)
    elif method == "percentile":
        lo, hi = (float(v) for v in np.quantile(boots, [alpha / 2, 1 - alpha / 2]))
    else:
        raise ValueError(method)
    return Interval(theta, lo, hi, alpha, method)


def cluster_bootstrap_ci(values, clusters, stat: Callable = np.mean, *, n_boot: int = 10000,
                         alpha: float = 0.05, seed: int = 0, within: bool = False) -> Interval:
    """Bootstrap resampling whole clusters (e.g. pairings, each holding several seeds).
    The statistic is computed on the pooled values of the drawn clusters. With
    within=True a second stage also resamples values inside each drawn cluster
    (use when seeds inside a pairing are themselves a sample)."""
    v = _arr(values)
    c = np.asarray(clusters)
    keys = list(dict.fromkeys(c.tolist()))
    groups = [v[c == k] for k in keys]
    theta = float(stat(v))
    if len(groups) < 2:
        return Interval(theta, theta, theta, alpha, "cluster-degenerate")
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, len(groups), size=len(groups))
        parts = []
        for j in pick:
            g = groups[j]
            parts.append(g[rng.integers(0, len(g), size=len(g))] if within else g)
        boots[b] = stat(np.concatenate(parts))
    lo, hi = (float(q) for q in np.quantile(boots, [alpha / 2, 1 - alpha / 2]))
    return Interval(theta, lo, hi, alpha, "cluster-percentile")


def bootstrap_diff_ci(a, b, *, paired: bool = False, n_boot: int = 10000, alpha: float = 0.05,
                      seed: int = 0, method: str = "percentile") -> Interval:
    """CI for mean(a) - mean(b). Paired: resample the pair differences. Unpaired: resample
    each arm independently."""
    a, b = _arr(a), _arr(b)
    if paired:
        if len(a) != len(b):
            raise ValueError("paired arms need equal length")
        return bootstrap_ci(a - b, np.mean, n_boot=n_boot, alpha=alpha, seed=seed, method=method)
    theta = float(a.mean() - b.mean())
    if len(a) < 2 or len(b) < 2:
        return Interval(theta, theta, theta, alpha, "diff-degenerate")
    rng = np.random.default_rng(seed)
    ia = rng.integers(0, len(a), size=(n_boot, len(a)))
    ib = rng.integers(0, len(b), size=(n_boot, len(b)))
    boots = a[ia].mean(axis=1) - b[ib].mean(axis=1)
    lo, hi = (float(q) for q in np.quantile(boots, [alpha / 2, 1 - alpha / 2]))
    return Interval(theta, lo, hi, alpha, "diff-percentile")


# ------------------------------------------------------------- permutation

def _p_from(perm_stats: np.ndarray, obs: float, alternative: str, eps: float = 1e-12) -> int:
    if alternative == "two-sided":
        return int(np.sum(np.abs(perm_stats) >= abs(obs) - eps))
    if alternative == "greater":
        return int(np.sum(perm_stats >= obs - eps))
    if alternative == "less":
        return int(np.sum(perm_stats <= obs + eps))
    raise ValueError(alternative)


def permutation_test(a, b, *, paired: bool = False, alternative: str = "two-sided",
                     n_perm: int = 20000, exact_limit: int = 200000, seed: int = 0) -> TestResult:
    """Test mean(a) - mean(b) = 0. alternative: 'two-sided', 'greater' (a > b), 'less'.

    Two-arm: relabel pooled values (exact by enumerating combinations when
    C(n_a + n_b, n_a) <= exact_limit). Paired: randomly flip the sign of each pair
    difference (exact when 2**n <= exact_limit)."""
    a, b = _arr(a), _arr(b)
    if paired:
        if len(a) != len(b):
            raise ValueError("paired arms need equal length")
        d = a - b
        n = len(d)
        obs = float(d.mean())
        if 2 ** n <= exact_limit:
            signs = np.array(list(itertools.product((-1.0, 1.0), repeat=n)))
            stats = (signs * d).mean(axis=1)
            return TestResult(obs, _p_from(stats, obs, alternative) / len(stats), alternative, True, len(stats))
        rng = np.random.default_rng(seed)
        signs = rng.choice((-1.0, 1.0), size=(n_perm, n))
        stats = (signs * d).mean(axis=1)
        return TestResult(obs, (_p_from(stats, obs, alternative) + 1) / (n_perm + 1), alternative, False, n_perm)
    pooled = np.concatenate([a, b])
    na, n = len(a), len(a) + len(b)
    obs = float(a.mean() - b.mean())
    total = math.comb(n, na)
    if total <= exact_limit:
        idx = np.array(list(itertools.combinations(range(n), na)))
        sa = pooled[idx].sum(axis=1)
        stats = sa / na - (pooled.sum() - sa) / (n - na)
        return TestResult(obs, _p_from(stats, obs, alternative) / total, alternative, True, total)
    rng = np.random.default_rng(seed)
    perm = np.argsort(rng.random((n_perm, n)), axis=1)[:, :na]
    sa = pooled[perm].sum(axis=1)
    stats = sa / na - (pooled.sum() - sa) / (n - na)
    return TestResult(obs, (_p_from(stats, obs, alternative) + 1) / (n_perm + 1), alternative, False, n_perm)


def sign_test(successes: int, n: int, p0: float = 0.5, alternative: str = "greater") -> float:
    """Exact one-sample binomial test p-value, e.g. 'true in >= 10 of 18 runs'."""
    pmf = [math.comb(n, k) * p0 ** k * (1 - p0) ** (n - k) for k in range(n + 1)]
    if alternative == "greater":
        return float(sum(pmf[successes:]))
    if alternative == "less":
        return float(sum(pmf[: successes + 1]))
    obs = pmf[successes]
    return float(min(1.0, sum(p for p in pmf if p <= obs + 1e-12)))


# ------------------------------------------------------------ rates (binomial)

def _binom_cdf(k: int, n: int, p: float) -> float:
    if p <= 0:
        return 1.0
    if p >= 1:
        return 1.0 if k >= n else 0.0
    return float(sum(math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                              + i * math.log(p) + (n - i) * math.log1p(-p)) for i in range(0, k + 1)))


def _bisect(f: Callable[[float], float], lo: float = 0.0, hi: float = 1.0) -> float:
    for _ in range(80):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> Interval:
    """Exact (conservative) Clopper-Pearson interval for a rate k / n."""
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= k <= n:
        raise ValueError("k out of range")
    lo = 0.0 if k == 0 else _bisect(lambda p: (1 - _binom_cdf(k - 1, n, p)) - alpha / 2)
    hi = 1.0 if k == n else _bisect(lambda p: -(_binom_cdf(k, n, p) - alpha / 2))
    return Interval(k / n, lo, hi, alpha, "clopper-pearson")


def wilson(k: int, n: int, alpha: float = 0.05) -> Interval:
    z = _N.inv_cdf(1 - alpha / 2)
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return Interval(p, max(0.0, centre - half), min(1.0, centre + half), alpha, "wilson")


def risk_difference(k1: int, n1: int, k0: int, n0: int, alpha: float = 0.05) -> Interval:
    """p1 - p0 with the Newcombe hybrid-score interval (built from Wilson intervals)."""
    w1, w0 = wilson(k1, n1, alpha), wilson(k0, n0, alpha)
    p1, p0 = k1 / n1, k0 / n0
    d = p1 - p0
    lo = d - math.sqrt((p1 - w1.lo) ** 2 + (w0.hi - p0) ** 2)
    hi = d + math.sqrt((w1.hi - p1) ** 2 + (p0 - w0.lo) ** 2)
    return Interval(d, lo, hi, alpha, "newcombe")


def risk_ratio(k1: int, n1: int, k0: int, n0: int, alpha: float = 0.05) -> Interval:
    """p1 / p0 with the Katz log interval (0.5 added to every cell when a count is 0)."""
    a, b, c, d = k1, n1 - k1, k0, n0 - k0
    if 0 in (a, c):
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    n1c, n0c = a + b, c + d
    rr = (a / n1c) / (c / n0c)
    se = math.sqrt(1 / a - 1 / n1c + 1 / c - 1 / n0c)
    z = _N.inv_cdf(1 - alpha / 2)
    est = (k1 / n1) / (k0 / n0) if k0 > 0 and k1 > 0 else rr
    return Interval(est, rr * math.exp(-z * se), rr * math.exp(z * se), alpha, "katz-log")


def fisher_exact_p(k1: int, n1: int, k0: int, n0: int, alternative: str = "two-sided") -> float:
    """Exact two-arm test of two proportions (hypergeometric)."""
    K, N = k1 + k0, n1 + n0
    lo, hi = max(0, K - n0), min(n1, K)
    pmf = {x: math.comb(K, x) * math.comb(N - K, n1 - x) / math.comb(N, n1) for x in range(lo, hi + 1)}
    if alternative == "greater":
        return sum(p for x, p in pmf.items() if x >= k1)
    if alternative == "less":
        return sum(p for x, p in pmf.items() if x <= k1)
    return min(1.0, sum(p for p in pmf.values() if p <= pmf[k1] * (1 + 1e-9)))


# -------------------------------------------------------------- effect sizes

def mean_difference(a, b, *, paired: bool = False, alpha: float = 0.05, seed: int = 0, n_boot: int = 10000) -> Interval:
    return bootstrap_diff_ci(a, b, paired=paired, alpha=alpha, seed=seed, n_boot=n_boot)


def cohens_d(a, b, *, paired: bool = False) -> float:
    """Standardised mean difference. Pooled sd (unpaired) or sd of differences (paired, d_z)."""
    a, b = _arr(a), _arr(b)
    if paired:
        d = a - b
        sd = d.std(ddof=1)
        return float(d.mean() / sd) if sd > 0 else math.copysign(math.inf, d.mean()) if d.mean() else 0.0
    na, nb = len(a), len(b)
    sp = math.sqrt(((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2))
    diff = a.mean() - b.mean()
    return float(diff / sp) if sp > 0 else math.copysign(math.inf, diff) if diff else 0.0


def cliffs_delta(a, b) -> float:
    """P(a > b) - P(a < b), in [-1, 1]. Needs no normality."""
    a, b = _arr(a), _arr(b)
    gt = (a[:, None] > b[None, :]).sum()
    lt = (a[:, None] < b[None, :]).sum()
    return float((gt - lt) / (len(a) * len(b)))


def cliffs_delta_ci(a, b, *, n_boot: int = 5000, alpha: float = 0.05, seed: int = 0) -> Interval:
    a, b = _arr(a), _arr(b)
    theta = cliffs_delta(a, b)
    rng = np.random.default_rng(seed)
    boots = np.array([cliffs_delta(a[rng.integers(0, len(a), len(a))], b[rng.integers(0, len(b), len(b))])
                      for _ in range(n_boot)])
    lo, hi = (float(q) for q in np.quantile(boots, [alpha / 2, 1 - alpha / 2]))
    return Interval(theta, lo, hi, alpha, "cliff-bootstrap")


# ----------------------------------------------------------------- correction

def holm(pvals: Sequence[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values (monotone, capped at 1), in input order.
    None entries (untestable) are passed through and not counted in the family."""
    idx = [i for i, p in enumerate(pvals) if p is not None]
    m = len(idx)
    order = sorted(idx, key=lambda i: pvals[i])
    adj: list = [None] * len(pvals)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


# ----------------------------------------------------------------------- power

def power_two_arm(effect: float, sd: float, n: int, *, alpha: float = 0.05, paired: bool = False,
                  alternative: str = "two-sided", n_sim: int = 400, n_perm: int = 399, seed: int = 0,
                  noise: Callable | None = None) -> float:
    """Simulated power of the permutation test: normal data (or `noise(rng, size)` scaled by sd),
    true mean difference `effect`, per-arm (or per-difference) spread `sd`. For paired data sd is
    the sd of the pair differences."""
    rng = np.random.default_rng(seed)
    draw = noise or (lambda r, size: r.standard_normal(size))
    hits = 0
    for s in range(n_sim):
        if paired:
            d = effect + sd * draw(rng, n)
            res = permutation_test(d, np.zeros(n), paired=True, alternative=alternative, n_perm=n_perm, seed=s)
        else:
            a = effect + sd * draw(rng, n)
            b = sd * draw(rng, n)
            res = permutation_test(a, b, alternative=alternative, n_perm=n_perm, exact_limit=0, seed=s)
        hits += res.p <= alpha
    return hits / n_sim


def seeds_for_power(effect: float, sd: float, *, target: float = 0.8, alpha: float = 0.05,
                    paired: bool = False, alternative: str = "two-sided", n_max: int = 256,
                    n_sim: int = 300, seed: int = 0) -> int | None:
    """Smallest per-arm n (or number of pairs) reaching `target` power by simulation, searched by
    doubling then bisection. None if n_max is not enough. effect/sd come from a labeled exploratory pilot."""
    if effect == 0 or sd < 0:
        return None
    if sd == 0:
        return 2

    def ok(n: int) -> bool:
        return power_two_arm(effect, sd, n, alpha=alpha, paired=paired, alternative=alternative,
                             n_sim=n_sim, seed=seed) >= target

    lo, hi = 2, 2
    while not ok(hi):
        lo, hi = hi, hi * 2
        if hi > n_max:
            return None if not ok(n_max) else n_max
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi if ok(hi) else lo


def power_binomial(p1: float, p0: float, n: int, *, alpha: float = 0.05, alternative: str = "two-sided",
                   n_sim: int = 500, seed: int = 0) -> float:
    """Simulated power of Fisher's exact test, n per arm."""
    rng = np.random.default_rng(seed)
    k1 = rng.binomial(n, p1, n_sim)
    k0 = rng.binomial(n, p0, n_sim)
    return float(np.mean([fisher_exact_p(int(x), n, int(y), n, alternative) <= alpha for x, y in zip(k1, k0)]))


def seeds_for_margin(sd: float, margin: float, *, target: float = 0.8, alpha: float = 0.05) -> int:
    """Normal-approximation seeds needed to detect a one-sample/paired mean shift of `margin` (two-sided,
    z test): n = ((z_{1-a/2} + z_{target}) * sd / margin)**2. A closed-form cross-check on the simulation."""
    if margin == 0:
        raise ValueError("margin must be non-zero")
    z = _N.inv_cdf(1 - alpha / 2) + _N.inv_cdf(target)
    return max(2, math.ceil((z * sd / abs(margin)) ** 2))
