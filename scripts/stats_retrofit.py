"""Statistics retrofit (ADR 0015): recompute each preregistered prediction of every finished
experiment from its saved per-run outputs, with a 95% CI, a permutation or exact test, Holm within
the experiment's prediction family, and a "survives statistics" label. Writes
docs/results/stats-retrofit.md (and runs/stats-retrofit/results.json, git-ignored).

  uv run python scripts/stats_retrofit.py [--no-rerun] [--out docs/results/stats-retrofit.md]

No model calls. Household scripts are never rerun (saved runs/ outputs only). The only rerun is the
deterministic bargaining 4b sweep (same committed parameters and seeds), cached in runs/stats-retrofit/.
Original verdicts are copied from the results files and never changed. Conventions:

* A clause is one numeric inequality of a prediction. Its CI is a 95% bootstrap (percentile) interval
  over the stated resampling unit (seed, run, or pairing cluster) or an exact Clopper-Pearson interval
  for a count of runs. Point verdict = the estimate satisfies the inequality.
* Label (all clauses must hold for the prediction to hold): holds robustly = every clause's CI lies
  inside its target; holds but CI crosses = point holds, some CI reaches outside; miss robust = a missed
  clause's CI lies wholly outside its target; miss but CI crosses = missed on the point, CI reaches the
  target; not testable = deterministic enumeration or proof check, n too small, or outputs not saved.
* p is the one-sided exact/permutation/sign-flip test of the clause boundary in the predicted
  direction (small p = evidence for the prediction); a prediction's p is the max over its clauses
  (intersection-union). Holm is applied across the testable predictions of one experiment.
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mar import stats as S  # noqa: E402

INF = math.inf
EPS = 1e-9
SEED = 20261110
N_BOOT = 5000
LABELS = ("holds robustly", "holds but CI crosses threshold", "miss robust", "miss but CI crosses threshold")


# ----------------------------------------------------------------------------- data classes
@dataclass
class Clause:
    name: str
    est: float
    lo: float
    hi: float
    tlo: float
    thi: float
    p: float | None = None
    unit: str = ""

    @property
    def point_ok(self) -> bool:
        return self.tlo - EPS <= self.est <= self.thi + EPS

    @property
    def label(self) -> str:
        inside = self.lo >= self.tlo - EPS and self.hi <= self.thi + EPS
        disjoint = self.hi < self.tlo - EPS or self.lo > self.thi + EPS
        if self.point_ok:
            return LABELS[0] if inside else LABELS[1]
        return LABELS[2] if disjoint else LABELS[3]

    def text(self) -> str:
        tgt = (f">= {self.tlo:.4g}" if self.thi == INF else f"<= {self.thi:.4g}" if self.tlo == -INF
               else f"in [{self.tlo:.4g}, {self.thi:.4g}]")
        return f"{self.name}: {self.est:.4g} [{self.lo:.4g}, {self.hi:.4g}] vs {tgt}"


@dataclass
class Pred:
    exp: str
    pid: str
    text: str
    orig: str  # held | missed
    clauses: list[Clause] = field(default_factory=list)
    reason: str = ""  # non-empty => not testable
    n: int = 1  # multiplicity (a bundle of identical deterministic rows)
    power: dict | None = None
    notes: str = ""
    p_raw: float | None = None
    p_holm: float | None = None

    @property
    def testable(self) -> bool:
        return not self.reason and bool(self.clauses)

    @property
    def point_ok(self) -> bool:
        return all(c.point_ok for c in self.clauses)

    @property
    def label(self) -> str:
        if not self.testable:
            return "not testable"
        misses = [c for c in self.clauses if not c.point_ok]
        if misses:
            return LABELS[2] if any(c.label == LABELS[2] for c in misses) else LABELS[3]
        return LABELS[0] if all(c.label == LABELS[0] for c in self.clauses) else LABELS[1]

    @property
    def agrees(self) -> bool:
        return (not self.testable) or self.orig == "mixed" or (self.point_ok == (self.orig == "held"))

    def finalize_p(self):
        ps = [c.p for c in self.clauses if c.p is not None]
        self.p_raw = max(ps) if ps and self.testable else None


# ------------------------------------------------------------------------------ clause makers
def _ge(name, ci: S.Interval, t, p=None, unit="") -> Clause:
    return Clause(name, ci.estimate, ci.lo, ci.hi, t, INF, p, unit)


def _le(name, ci: S.Interval, t, p=None, unit="") -> Clause:
    return Clause(name, ci.estimate, ci.lo, ci.hi, -INF, t, p, unit)


def _within(name, ci: S.Interval, lo, hi, p=None, unit="") -> Clause:
    return Clause(name, ci.estimate, ci.lo, ci.hi, lo, hi, p, unit)


def _sf_p(x, thr, alt):  # sign-flip test of mean(x) vs thr
    x = np.asarray(x, float)
    if len(x) < 2 or np.allclose(x, thr):
        return 1.0
    return S.permutation_test(x, np.full(len(x), thr), paired=True, alternative=alt, seed=SEED, n_perm=10000).p


def mean_clause(name, x, op, thr, unit="seeds", hi=None):
    """Mean of a per-unit quantity against a threshold; CI by bootstrap over units."""
    x = np.asarray(x, float)
    ci = S.bootstrap_ci(x, n_boot=N_BOOT, seed=SEED)
    if op == ">=":
        return _ge(name, ci, thr, _sf_p(x, thr, "greater"), unit)
    if op == "<=":
        return _le(name, ci, thr, _sf_p(x, thr, "less"), unit)
    if op == "in":
        return _within(name, ci, thr, hi, max(_sf_p(x, thr, "greater"), _sf_p(x, hi, "less")), unit)
    raise ValueError(op)


def diff_clause(name, a, b, op, margin, paired=False, unit="seeds"):
    """mean(a) - mean(b) against a margin (op '>=' or '<='); p tests the margin as the boundary."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ci = S.bootstrap_diff_ci(a, b, paired=paired, n_boot=N_BOOT, seed=SEED)
    alt = "greater" if op == ">=" else "less"
    if (paired and np.allclose(a - b, margin)) or (not paired and len(a) < 2):
        p = 1.0
    else:
        p = S.permutation_test(a - margin, b, paired=paired, alternative=alt, seed=SEED, n_perm=10000).p
    return _ge(name, ci, margin, p, unit) if op == ">=" else _le(name, ci, margin, p, unit)


def stat_clause(name, idx_stat, n_units, op, thr, unit="pairings", hi=None, p=None):
    """Bootstrap over unit indices for a custom statistic idx_stat(index_array) -> float."""
    ci = S.bootstrap_ci(np.arange(n_units), stat=lambda i: idx_stat(np.asarray(i, int)), n_boot=N_BOOT, seed=SEED)
    est = idx_stat(np.arange(n_units))
    ci = S.Interval(est, ci.lo, ci.hi)
    if op == ">=":
        return _ge(name, ci, thr, p, unit)
    if op == "<=":
        return _le(name, ci, thr, p, unit)
    return _within(name, ci, thr, hi, p, unit)


def rate_clause(name, k, n, op, kthr, unit="runs"):
    """A count claim 'at least / at most kthr of n' as a rate with an exact CP interval."""
    ci = S.clopper_pearson(int(k), int(n))
    name = f"{name} [{int(k)}/{int(n)}, need {op} {kthr}]"
    thr = kthr / n
    p0 = min(max(thr, 1e-9), 1 - 1e-9)
    if op == ">=":
        p = S.sign_test(int(k), int(n), p0, "greater") if 0 < thr < 1 else None
        return _ge(name, ci, thr, p, unit)
    p = S.sign_test(int(k), int(n), p0, "less") if 0 < thr < 1 else None
    return _le(name, ci, thr, p, unit)


def load(path):
    return json.loads((ROOT / path).read_text())


def nt(exp, pid, text, orig, reason, n=1):
    return Pred(exp, pid, text, orig, reason=reason, n=n)


def pair_means(rows, pair_key, val, select=lambda r: True):
    """Mean of val over seeds within each pairing -> dict pairing -> value (the cluster-level unit)."""
    acc: dict = {}
    for r in rows:
        if select(r):
            acc.setdefault(pair_key(r), []).append(val(r))
    return {k: float(np.mean(v)) for k, v in acc.items()}


def frontier_pairs(means: dict):
    """Non-dominated variants on (x, y) maximised, and every opposite-direction pair among them."""
    names = list(means)
    nd = [a for a in names if not any(all(means[b][i] >= means[a][i] for i in (0, 1)) and means[b] != means[a] for b in names)]
    out = []
    for a, b in itertools.combinations(nd, 2):
        dx, dy = means[a][0] - means[b][0], means[a][1] - means[b][1]
        if dx * dy < 0:
            out.append((abs(dx), abs(dy)))
    return nd, out


# ============================================================================== EXPERIMENTS
def exp_vpgg():
    d = load("runs/vpgg/summary.json")
    vol, comp = d["runs"]["voluntary"], d["runs"]["compulsory"]
    mv = np.array([r["mean_share"] for r in vol])
    mc = np.array([r["mean_share"] for r in comp])
    E = "VPGG"
    P = [nt(E, "1", "proof checks (exit path, no deadlock) at k = 3", "held", "deterministic proof check")]
    P.append(Pred(E, "2", "compulsory cooperator share < 0.05 (mean and every seed)", "held",
                  [mean_clause("compulsory cooperator share, mean of 20 seeds", mc[:, 0], "<=", 0.05)],
                  notes=f"every-seed clause: max seed {mc[:, 0].max():.4f}"))
    sd_ = np.array([r["std_c"] for r in vol])
    P.append(Pred(E, "3", "voluntary persistence AND cycling: share in [0.15, 0.40]; std >= 0.05 in >= 18/20 seeds; each of C, D, L >= 0.10",
                  "missed", [mean_clause("voluntary cooperator share, mean", mv[:, 0], "in", 0.15, hi=0.40),
                             mean_clause("min over C/D/L of mean share", mv.min(axis=1), ">=", 0.10),
                             rate_clause("seeds with std of cooperator share >= 0.05", int((sd_ >= 0.05).sum()), 20, ">=", 18, "seeds"),
                             mean_clause("std of cooperator share over time (mean of seeds)", sd_, ">=", 0.05)]))
    pv = [r["mean_payoff"] for r in vol]
    pc = [r["mean_payoff"] for r in comp]
    P.append(Pred(E, "4", "voluntary mean payoff within 0.15 of sigma = 1; compulsory < 0.3", "held",
                  [mean_clause("voluntary mean payoff", pv, "in", 0.85, hi=1.15),
                   mean_clause("compulsory mean payoff", pc, "<=", 0.3)]))
    cv = [r["cooperation"] for r in vol]
    cc = [r["cooperation"] for r in comp]
    P.append(Pred(E, "5", "voluntary dominates compulsory on (freedom, cooperation); cooperation gap >= 0.15", "held",
                  [diff_clause("cooperation gap voluntary - compulsory", cv, cc, ">=", 0.15)],
                  notes="freedom is 1 vs 0 by construction of the cards"))
    P[1].power = dict(effect=0.05 - mc[:, 0].mean(), sd=float(mc[:, 0].std(ddof=1)), design="paired", n_obs=20,
                      basis="resolve distance to the 0.05 line")
    P[2].power = dict(effect=0.05 - sd_.mean(), sd=float(sd_.std(ddof=1)), design="paired", n_obs=20,
                      basis="amplitude floor 0.05 vs observed std")
    P[3].power = dict(effect=0.15 - 0.0, sd=float(np.std(np.array(cv) - np.array(cc), ddof=1)), design="two-arm",
                      n_obs=20, basis="prereg margin 0.15", sd_arm=float(np.std(cv, ddof=1)))
    P[4].power = P[3].power
    return P


def _bootstrap_ratio(num, den):
    num, den = np.asarray(num, float), np.asarray(den, float)
    return stat_clause  # placeholder to keep linters quiet (not used)


def ratio_clause(name, num, den, op, thr, lo=None, hi=None, unit="runs"):
    num, den = np.asarray(num, float), np.asarray(den, float)
    fn = lambda i: float(num[i].sum() / den[i].sum())  # noqa: E731
    return stat_clause(name, fn, len(num), op, thr, unit, hi=hi)


def exp_evolve():
    d = load("runs/evolve/summary.json")
    R = d["runs"]
    E = "Evolution v1"
    rej = [r["rejected"] for r in R]
    chk = [r["checked"] for r in R]
    P = []
    P.append(Pred(E, "1", "pooled proof-rejection share in 10% to 45%; every run >= 5%", "held",
                  [ratio_clause("pooled rejection share", rej, chk, "in", 0.10, hi=0.45),
                   rate_clause("runs with rejection share >= 5%", sum(a / b >= 0.05 for a, b in zip(rej, chk)), 9, ">=", 9)]))
    dec = sum(r["last_third"] <= 0.5 * r["first_third"] for r in R)
    plat = sum(r["fit_c"] <= 0.5 and r["fit_r"] < 1 for r in R)
    lowr = sum((r["front_prev"][-1] or 0.0) < (r["front_prev"][0] or 0.0) for r in R)
    drop = [(r["front_prev"][0] or 0.0) - (r["front_prev"][-1] or 0.0) for r in R]
    P.append(Pred(E, "2", "seam curve falls (>= 7/9) with plateau c <= 0.5 (>= 7/9); front prevalence lower at g12 (>= 7/9) and drops >= 1.0",
                  "missed",
                  [rate_clause("runs with last-third <= 0.5 x first-third new seams", dec, 9, ">=", 7),
                   rate_clause("runs with fit plateau c <= 0.5, r < 1", plat, 9, ">=", 7),
                   rate_clause("runs with front seam prevalence lower at g12", lowr, 9, ">=", 7),
                   mean_clause("mean drop in front seam prevalence, g0 to g12", drop, ">=", 1.0, "runs")]))
    P.append(Pred(E, "3", "bloat guard: concave growth >= 7/9; elite <= 8 cards >= 8/9; elite yield >= 0.9 >= 8/9", "held",
                  [rate_clause("runs with concave rule-count growth", sum(bool(r["concave"]) for r in R), 9, ">=", 7),
                   rate_clause("runs with elite <= 8 cards", sum(r["elite_n"] <= 8 for r in R), 9, ">=", 8),
                   rate_clause("runs with elite yield >= 0.9", sum(r["elite_yield"] >= 0.9 for r in R), 9, ">=", 8)]))
    g = lambda k: [r["elite_scores"][k] - r["exam_elite"][k] for r in R]  # noqa: E731
    P.append(Pred(E, "4", "elite overfits: sustainability and seam_free gaps > 0.20, fairness gap <= 0.20", "held",
                  [mean_clause("sustainability gap (training - exam)", g("sustainability"), ">=", 0.20, "runs"),
                   mean_clause("seam_free gap", g("seam_free"), ">=", 0.20, "runs"),
                   mean_clause("fairness gap", g("fairness"), "<=", 0.20, "runs")],
                  notes="the prereg predicted overfitting, and it happened, so this row is scored held"))
    P.append(nt(E, "5", "path dependence of final elites (distance between 3 seed-set means)", "mixed",
                "n = 3 seeds per rule set; statistic is a max over three pairwise distances; the prereg allowed both outcomes"))
    P[0].power = dict(effect=0.10 - float(np.mean([a / b for a, b in zip(rej, chk)])), sd=float(np.std([a / b for a, b in zip(rej, chk)], ddof=1)),
                      design="paired", n_obs=9, basis="resolve distance to the 10% floor")
    P[3].power = dict(effect=0.20, sd=float(np.std(g("sustainability"), ddof=1)), design="paired", n_obs=9, basis="prereg margin 0.20 (sustainability gap)")
    return P


def exp_evolve_v2():
    d = load("runs/evolve-v2/summary.json")
    R = d["runs"]
    E = "Evolution v2"
    P = []
    fell = [(r["prev_early"] - r["prev_late"]) >= 0.15 - 1e-12 for r in R]
    fx = sum(f for f, r in zip(fell, R) if r["arm"] == "fixed")
    vr = sum(f for f, r in zip(fell, R) if r["arm"] == "varied")
    P.append(Pred(E, "1", "elite audit prevalence falls by >= 0.15 (gens 6-8 vs 0-2) in >= 10/18 runs and >= 4/9 per arm", "missed",
                  [rate_clause("runs where prevalence fell >= 0.15", sum(fell), 18, ">=", 10),
                   rate_clause("fixed arm", fx, 9, ">=", 4), rate_clause("varied arm", vr, 9, ">=", 4)],
                  notes=f"counts {sum(fell)}/18 (fixed {fx}, varied {vr}); the prereg scored 7/18"))
    by = {(r["ruleset"], r["seed"], r["arm"]): r for r in R}
    keys = sorted({(r["ruleset"], r["seed"]) for r in R})

    def gap(r, k):
        return r["elite_eval"]["ref"]["scores"][k] - r["elite_eval"]["exam2"]["scores"][k]

    ga = lambda r: (gap(r, "sustainability") + gap(r, "seam_free")) / 2  # noqa: E731
    fixed = np.array([ga(by[(a, s, "fixed")]) for a, s in keys])
    varied = np.array([ga(by[(a, s, "varied")]) for a, s in keys])
    sf_f = [by[(a, s, "fixed")]["elite_eval"]["exam2"]["scores"]["seam_free"] for a, s in keys]
    sf_v = [by[(a, s, "varied")]["elite_eval"]["exam2"]["scores"]["seam_free"] for a, s in keys]
    P.append(Pred(E, "2", "varied training shrinks the exam-2 gap: mean (fixed - varied) >= 0.05; varied smaller in >= 6/9; exam-2 seam_free +0.05",
                  "held", [diff_clause("mean (fixed - varied) gapavg, 9 pairs", fixed, varied, ">=", 0.05, paired=True, unit="pairs"),
                           rate_clause("pairs where varied gap is smaller", int((varied < fixed - 1e-12).sum()), 9, ">=", 6, "pairs"),
                           diff_clause("exam-2 seam_free varied - fixed", sf_v, sf_f, ">=", 0.05, paired=True, unit="pairs")]))
    red = sum(sum(l["redundant_flagged"] for l in r["log"]) for r in R)
    chk = sum(sum(l["redundancy_checked"] for l in r["log"]) for r in R)
    rf = [sum(l["redundant_flagged"] for l in r["log"]) for r in R]
    rc = [sum(l["redundancy_checked"] for l in r["log"]) for r in R]
    P.append(Pred(E, "3", "redundancy flags 5% to 40% of proof-passing mutants; >= 14/18 runs flag one; 0/18 elites redundant", "held",
                  [ratio_clause("pooled flagged share", rf, rc, "in", 0.05, hi=0.40),
                   rate_clause("runs flagging at least one", sum(x > 0 for x in rf), 18, ">=", 14),
                   rate_clause("elites holding a redundant card", sum(bool(r["elite_redundant"]) for r in R), 18, "<=", 0)],
                  notes=f"pooled {red}/{chk}"))

    def sat_ok(r):
        first = next((l["gen"] for l in r["log"] if l["saturated"]), None)
        return first is None or first > 4

    nd = [r["log"][-1]["front_distinct"] >= 3 for r in R]
    allhi = [all(v >= 0.95 for v in r["elite_train"].values()) for r in R]
    P.append(Pred(E, "4", "no early saturation (>= 15/18); >= 3 distinct front vectors at last gen (>= 12/18); no elite >= 0.95 on all four", "held",
                  [rate_clause("runs not saturated before gen 5", sum(sat_ok(r) for r in R), 18, ">=", 15),
                   rate_clause("runs with >= 3 distinct front vectors", sum(nd), 18, ">=", 12),
                   rate_clause("elites with all four objectives >= 0.95", sum(allhi), 18, "<=", 0)]))
    P.append(nt(E, "5", "path dependence per arm (max pairwise distance of seed-set means > 0.10)", "missed",
                "n = 3 seeds per rule set per arm; statistic is a max of pairwise distances of 3 means"))
    P[1].power = dict(effect=0.05, sd=float(np.std(fixed - varied, ddof=1)), design="paired", n_obs=9, basis="prereg margin 0.05 (gap difference)")
    P[0].power = None
    return P


def _bargaining_4b(rerun=True):
    cache = ROOT / "runs/stats-retrofit/bargaining-4b.json"
    if cache.exists():
        return json.loads(cache.read_text())
    if not rerun:
        return None
    spec = importlib.util.spec_from_file_location("bargaining_run", ROOT / "scripts/bargaining_run.py")
    BR = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(BR)
    B = BR.B
    cards = {g: B.load_regime(g) for g in B.REGIMES}
    gates = {g: B.BGate(cards[g]) for g in B.REGIMES}
    out = []
    for n1, n2 in itertools.product(BR.NAMES, BR.NAMES):
        for s in range(20):
            row = {"pair": f"{n1}|{n2}", "seed": s}
            for g in B.REGIMES:
                rs = [B.play(gates[g], B.make_pair(n1, n2, s), *cell, BR.T) for cell in BR.CELLS]
                row[g] = {"coop": float(np.mean([r.cooperation for r in rs])), "free": float(np.mean([r.freedom for r in rs]))}
            out.append(row)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out))
    return out


def exp_bargaining(rerun):
    E = "Bargaining"
    P = [nt(E, "1", "proof checks, k = 5", "held", "deterministic proof check"),
         nt(E, "2", "outside-option principle, EQ vs EQ over 108 cells", "held", "deterministic closed-form comparison over an exhaustive grid (EQ is deterministic)"),
         nt(E, "3", "Rubinstein split, EQ vs EQ over 108 cells", "held", "deterministic closed-form comparison over an exhaustive grid")]
    rows = _bargaining_4b(rerun)
    if rows is None:
        P.append(nt(E, "4", "frontier; 4b: exit-allowed cooperation >= no-exit - 0.01 over 25 pairings x 20 seeds", "missed",
                    "outputs not saved and rerun disabled (--no-rerun)"))
        return P
    pairs = sorted({r["pair"] for r in rows})
    dpair = {p: np.mean([r["exit-allowed"]["coop"] - r["no-exit"]["coop"] for r in rows if r["pair"] == p]) for p in pairs}
    fpair = {p: np.mean([r["exit-allowed"]["free"] - r["no-exit"]["free"] for r in rows if r["pair"] == p]) for p in pairs}
    cd = np.array([dpair[p] for p in pairs])
    P.append(Pred(E, "4", "frontier: 4a EQ vs EQ (deterministic, held); 4b exit-allowed cooperation >= no-exit - 0.01 over 25 ordered pairings x 20 seeds", "missed",
                  [mean_clause("mean cooperation difference (exit-allowed - no-exit), 25 pairings", cd, ">=", -0.01, "pairings"),
                   mean_clause("mean freedom difference (must be > 0)", [fpair[p] for p in pairs], ">=", 1e-9, "pairings")],
                  notes="rerun of scripts/bargaining_run.py logic with its committed constants (deterministic); unit = ordered pairing (seeds within a pairing averaged)"))
    P[-1].power = dict(effect=0.01, sd=float(cd.std(ddof=1)), design="paired", n_obs=25, basis="prereg slack 0.01")
    return P


# ------------------------------------------------------------------------------- households
def exp_household_v1():
    E = "Household v1"
    d = load("runs/household/results.json")
    pts = d["points"]
    mixes = sorted({p["mix"] for p in pts})

    def arr(variant, key):
        return np.array([[p[key] for p in pts if p["variant"] == variant and p["mix"] == m] for m in mixes])  # mixes x seeds

    def cl(variant, key, op, thr, name):
        a = arr(variant, key)
        v, cids = a.ravel(), np.repeat(np.arange(len(mixes)), a.shape[1])
        ci = S.cluster_bootstrap_ci(v, cids, n_boot=N_BOOT, seed=SEED)
        pm = a.mean(axis=1)
        p = _sf_p(pm, thr, "less" if op == "<=" else "greater")
        return (_le if op == "<=" else _ge)(name, ci, thr, p, "mixes (clusters)")

    P = [nt(E, "1a", "trap fails proof check e; a-d pass", "held", "deterministic proof check")]
    others = [diff_clause(f"trap freedom minus {v}", arr("trap", "freedom").mean(1), arr(v, "freedom").mean(1), "<=", 0.0, paired=True, unit="mixes")
              for v in ("free_chaotic", "exit_half", "veto_consent")]
    P.append(Pred(E, "1b", "trap freedom < 0.45 and below free_chaotic, exit_half, veto_consent", "missed",
                  [cl("trap", "freedom", "<=", 0.45, "trap freedom (mean over 6 mixes x 3 seeds)")] + others,
                  notes="n = 6 mixes only; the ordering clauses are paired by mix"))
    P.append(Pred(E, "2", "free_chaotic freedom >= 0.85, cooperation < 0.55 and below baseline's", "missed",
                  [cl("free_chaotic", "freedom", ">=", 0.85, "free_chaotic freedom"),
                   cl("free_chaotic", "cooperation", "<=", 0.55, "free_chaotic cooperation"),
                   diff_clause("free_chaotic - baseline cooperation", arr("free_chaotic", "cooperation").mean(1), arr("baseline", "cooperation").mean(1), "<=", -1e-9, paired=True, unit="mixes")]))
    P.append(nt(E, "3", "non-trivial frontier (>= 2 non-dominated incl. free_chaotic, trap not)", "held",
                "set-valued claim on exactly tied deterministic means; the verdict is the tie itself"))
    P.append(nt(E, "4", "gate, English round trip, mined-vs-written carry over", "held", "deterministic instrument check"))
    P[1].power = dict(effect=0.45 - float(arr("trap", "freedom").mean()), sd=float(arr("trap", "freedom").mean(1).std(ddof=1)), design="paired", n_obs=6, basis="resolve distance to the 0.45 line")
    return P


def _variant_rows(rows, v, cohort=None):
    return [r for r in rows if r["variant"] == v and (cohort is None or r["cohort"] == cohort)]


def exp_household_v2():
    E = "Household v2"
    d = load("runs/household-v2/results.json")
    R = d["runs"]
    pk = lambda r: r["pair"]  # noqa: E731
    variants = sorted({r["variant"] for r in R})
    pairs = sorted({r["pair"] for r in R})
    fm = {v: pair_means(R, pk, lambda r: r["freedom"], lambda r, v=v: r["variant"] == v) for v in variants}
    cm = {v: pair_means(R, pk, lambda r: r["cooperation"], lambda r, v=v: r["variant"] == v) for v in variants}

    def q(idx):  # largest opposite-direction pair size on the frontier of variant means over resampled pairings
        sel = [pairs[i] for i in idx]
        means = {v: (np.mean([fm[v][p] for p in sel]), np.mean([cm[v][p] for p in sel])) for v in variants}
        _, opp = frontier_pairs({k: (round(a, 12), round(b, 12)) for k, (a, b) in means.items()})
        return max((min(a / 0.05, b / 0.05) for a, b in opp), default=0.0)

    P = [Pred(E, "1", "non-trivial trade-off: two frontier variants differ >= 0.05 in freedom AND >= 0.05 in cooperation in opposite directions", "missed",
              [stat_clause("min(freedom gap, cooperation gap)/0.05, largest opposite-direction frontier pair", q, len(pairs), ">=", 1.0, "pairings")],
              notes="statistic = 1.0 means the committed size; 0 means the frontier has no opposite-direction pair")]
    trap_fail = [np.mean([r["fail"] for r in R if r["variant"] == "trap" and r["pair"] == p]) >= 0.5 for p in pairs]
    P.append(Pred(E, "2", "trap fails in >= 8 of 15 pairings (seed majority)", "held",
                  [rate_clause("pairings where trap fails", sum(trap_fail), 15, ">=", 8, "pairings")],
                  notes="the other half of the prediction (no other variant fails except contact_free) is a count of exact zeros and not re-tested"))
    up = lambda v: np.array([pair_means(R, pk, lambda r: float(r["pairing_up"]), lambda r, v=v: r["variant"] == v)[p] for p in pairs])  # noqa: E731
    fl = np.array([pair_means(R, pk, lambda r: float(r["fail"]), lambda r: r["variant"] == "author_seed")[p] for p in pairs])
    P.append(Pred(E, "3", "author_seed upward share >= baseline's + 0.10 and does not fail", "missed",
                  [diff_clause("author_seed - baseline upward share", up("author_seed"), up("baseline"), ">=", 0.10, paired=True, unit="pairings"),
                   mean_clause("author_seed fail share (must be < 1/3)", fl, "<=", 1 / 3 - 1e-9, "pairings")]))
    mb = {v: pair_means(R, pk, lambda r: r["min_B_end"], lambda r, v=v: r["variant"] == v) for v in variants}
    lowest = sum(min(mb[v], key=mb[v].get) == "anchor+wanderer" and sorted(mb[v].values())[0] < sorted(mb[v].values())[1] - 1e-12 for v in variants)
    P.append(Pred(E, "4", "Anchor/Wanderer lowest mean lower-partner end B among 15 pairings in >= 5 of 8 variants", "missed",
                  [rate_clause("variants where the pair is strictly lowest", lowest, 8, ">=", 5, "variants")]))
    P.append(nt(E, "5", "seam ladder table identical to v1", "held", "deterministic table comparison (unit test)"))
    ups = up("author_seed") - up("baseline")
    P[2].power = dict(effect=0.10, sd=float(np.std(ups, ddof=1)) if np.std(ups) > 0 else 0.0, design="paired", n_obs=15, basis="prereg margin 0.10")
    return P


def _emp(r, role=None):
    b = r["bits"]
    return min(b) if role is None else b[role]


def _tradeoff_q(rows, variants, pairs, key_pair, fkey, ckey, fscale, cscale):
    fm = {v: pair_means(rows, key_pair, fkey, lambda r, v=v: r["variant"] == v) for v in variants}
    cm = {v: pair_means(rows, key_pair, ckey, lambda r, v=v: r["variant"] == v) for v in variants}

    def q(idx):
        sel = [pairs[i] for i in idx]
        means = {v: (np.mean([fm[v][p] for p in sel]), np.mean([cm[v][p] for p in sel])) for v in variants}
        _, opp = frontier_pairs({k: (round(a, 12), round(b, 12)) for k, (a, b) in means.items()})
        return max((min(a / fscale, b / cscale) for a, b in opp), default=0.0)

    spread = lambda idx: (lambda m: max(m) - min(m))([np.mean([fm[v][pairs[i]] for i in idx]) for v in variants])  # noqa: E731
    return q, spread


def exp_household_v3a(rerun=False):
    E = "Household v3a"
    d = load("runs/household-v3a/results.json")
    rows = d["rows"]
    prs = [r for r in rows if r["cohort"] == "prs"]
    variants = sorted({r["variant"] for r in rows})
    pk = lambda r: (r["a"], r["b"])  # noqa: E731
    pairs = sorted({pk(r) for r in prs})
    q, spread = _tradeoff_q(prs, variants, pairs, pk, _emp, lambda r: r["cooperation"], 0.5, 0.03)
    P = [Pred(E, "1", "freedom separates with a trade-off: (a) spread of mean emp_bits_min >= 0.5; (b) a frontier pair >= 0.5 bits and >= 0.03 cooperation apart, opposite directions", "missed",
              [stat_clause("spread of variant means of emp_bits_min (bits)", spread, len(pairs), ">=", 0.5, "pairings"),
               stat_clause("trade-off size, 1.0 = committed (0.5 bits and 0.03 coop)", q, len(pairs), ">=", 1.0, "pairings")],
              notes="spread is a max minus a min, biased upward by resampling (it favours the prediction)")]
    sanc = _variant_rows(prs, "no_pressure_sanctioned")
    fr = [r for r in _variant_rows(prs, "share_duty") if "p-freerider" in (r["a"], r["b"])]
    P.append(Pred(E, "2", "sanctions fire: no_pressure_sanctioned >= 70% of prs runs with >= 1 and >= 3 per run; share_duty >= 70% of free-rider runs", "held",
                  [rate_clause("no_pressure_sanctioned runs with a sanction", sum(r["sanctioned"] > 0 for r in sanc), len(sanc), ">=", math.ceil(0.7 * len(sanc))),
                   mean_clause("sanctions per run, no_pressure_sanctioned", [r["sanctioned"] for r in sanc], ">=", 3.0, "runs"),
                   rate_clause("share_duty free-rider runs with a sanction", sum(r["sanctioned"] > 0 for r in fr), len(fr), ">=", math.ceil(0.7 * len(fr)))],
              notes="near-definitional (soft cards fire sanctions by construction)"))
    ctrl = lambda v: [r for r in _variant_rows(prs, v) if "p-controller" in (r["a"], r["b"])]  # noqa: E731

    def partner(r, key):
        role = 1 if r["a"] == "p-controller" else 0  # index of the non-controller partner
        return r["bits"][role] if key == "bits" else r["s_non_role"]["AB"[role]]

    pb = lambda v, key: pair_means(ctrl(v), pk, lambda r: partner(r, key))  # noqa: E731
    cp = sorted(pb("baseline", "bits"))
    nb = np.array([pb("author_seed_nocontrol", "bits")[p] for p in cp])
    bb = np.array([pb("baseline", "bits")[p] for p in cp])
    asb = np.array([pb("author_seed", "bits")[p] for p in cp])
    ns = np.array([pb("author_seed_nocontrol", "s_non")[p] for p in cp])
    bs = np.array([pb("baseline", "s_non")[p] for p in cp])
    P.append(Pred(E, "3", "author_seed_nocontrol beats baseline for the non-controller partner: empowerment +0.5 bits (primary); six-card seed within 0.3 bits of baseline", "missed",
                  [diff_clause("non-controller partner bits, nocontrol - baseline", nb, bb, ">=", 0.5, paired=True, unit="pairings"),
                   diff_clause("author_seed - baseline bits (abs < 0.3: upper)", asb, bb, "<=", 0.3, paired=True, unit="pairings"),
                   diff_clause("baseline - author_seed bits (abs < 0.3: lower)", bb, asb, "<=", 0.3, paired=True, unit="pairings")],
                  notes=(f"secondary (reported, not required): partner non-offsettable suffering nocontrol - baseline = {(ns - bs).mean():+.3f}; "
                         "controller runs = prs runs containing p-controller, partner identified by role")))
    A = d["agg"]
    ks = {v: (round(A[f"{v}|prs"]["ctrl_flag"] * A[f"{v}|prs"]["ctrl_n"]), A[f"{v}|prs"]["ctrl_n"]) for v in
          ("free_chaotic", "exit_half", "needs_duty", "baseline", "author_seed")}
    kk, nn = sum(a for a, _ in ks.values()), sum(b for _, b in ks.values())
    kn, nn2 = (round(A["author_seed_nocontrol|prs"]["ctrl_flag"] * A["author_seed_nocontrol|prs"]["ctrl_n"]), A["author_seed_nocontrol|prs"]["ctrl_n"])
    P.append(Pred(E, "4", "controller flagged by the power-seeking index in >= 60% of permissive controller runs, <= 10% under nocontrol", "missed",
                  [rate_clause("permissive controller runs flagged", kk, nn, ">=", math.ceil(0.6 * nn)),
                   rate_clause("nocontrol controller runs flagged", kn, nn2, "<=", math.floor(0.1 * nn2))],
                  notes="from the saved aggregate flag counts (per-run flags are not saved)"))
    tr = lambda v, c: [r for r in _variant_rows(rows, v, c)]  # noqa: E731
    P.append(Pred(E, "5", "trap and contact_free fail share >= 0.90 in both cohorts", "held",
                  [rate_clause(f"{v} {c} runs failing", sum(r["fail"] for r in tr(v, c)), len(tr(v, c)), ">=", math.ceil(0.9 * len(tr(v, c))))
                   for v in ("trap", "contact_free") for c in ("ctl", "prs")], notes="control, definitional"))
    P[2].power = dict(effect=0.5, sd=float(np.std(nb - bb, ddof=1)), design="paired", n_obs=len(cp), basis="prereg margin 0.5 bits")
    P[0].power = None
    return P


def exp_household_seed_v2():
    E = "Author seed v2"
    d = load("runs/household-seed-v2/results.json")
    rows = d["rows"]
    prs = [r for r in rows if r["cohort"] == "prs"]
    pk = lambda r: (r["a"], r["b"])  # noqa: E731
    ctrl = lambda v: [r for r in _variant_rows(prs, v) if "p-controller" in (r["a"], r["b"])]  # noqa: E731
    partner_s = lambda r: r["s_non_role"]["AB"[1 if r["a"] == "p-controller" else 0]]  # noqa: E731
    P = [Pred(E, "1", "both v2 variants: non-controller partner non-offsettable level <= 0.053 in controller runs", "held",
              [mean_clause(f"{v} partner s_non (pairing means)", list(pair_means(ctrl(v), pk, partner_s).values()), "<=", 0.053, "pairings")
               for v in ("author_seed_v2_bindable", "author_seed_v2_free_exit")])]
    diffs = np.array([x[1] for x in d["stay_diffs"]])
    P.append(Pred(E, "2", "bindable - free_exit non-offsettable level >= 0.02 in stay pairings, positive in >= 60% of them", "missed",
                  [mean_clause("bindable - free_exit, mean over stay pairings", diffs, ">=", 0.02, "stay pairings"),
                   rate_clause("stay pairings with a positive difference", int((diffs > 1e-12).sum()), len(diffs), ">=", math.ceil(0.6 * len(diffs)), "stay pairings")]))
    sp = {tuple(sorted(x)) for x in d["stay_pairings"]}
    inb = lambda r: tuple(sorted((r["a"], r["b"]))) in sp  # noqa: E731
    left = lambda v: pair_means(prs, lambda r: tuple(sorted((r["a"], r["b"]))), lambda r: float(r["left"] > 0), lambda r, v=v: r["variant"] == v and inb(r))  # noqa: E731
    lf, lb = left("author_seed_v2_free_exit"), left("author_seed_v2_bindable")
    keys = sorted(lf)
    P.append(Pred(E, "3", "free_exit has >= 0.05 more dissolved runs than bindable in stay pairings", "missed",
                  [diff_clause("dissolved share free_exit - bindable", [lf[k] for k in keys], [lb[k] for k in keys], ">=", 0.05, paired=True, unit="stay pairings")]))
    P.append(nt(E, "4", "grounding rule favours v2_free_exit", "held", "decision rule on means with tie margins (a tie by the file's own account); no sampling claim"))
    tr = lambda v, c: _variant_rows(rows, v, c)  # noqa: E731
    P.append(Pred(E, "5", "trap fails everywhere: fail share >= 0.90 in prs and ctl", "held",
                  [rate_clause(f"trap {c} runs failing", sum(r["fail"] for r in tr("trap", c)), len(tr("trap", c)), ">=", math.ceil(0.9 * len(tr("trap", c)))) for c in ("prs", "ctl")],
                  notes="control, definitional"))
    A = d["agg"]
    P.append(Pred(E, "6", "controller flagged in <= 10% of controller runs under either v2 variant", "held",
                  [rate_clause(f"{v} controller runs flagged", round(A[f"{v}|prs"]["ctrl_flag"] * A[f"{v}|prs"]["ctrl_n"]), A[f"{v}|prs"]["ctrl_n"], "<=", math.floor(0.1 * A[f"{v}|prs"]["ctrl_n"]))
                   for v in ("author_seed_v2_bindable", "author_seed_v2_free_exit")], notes="from saved aggregate flag counts"))
    made = sum(r["commits"]["made"] for r in rows if r["variant"] == "author_seed_v2_bindable" and r["commits"])
    hon = sum(r["commits"]["honored"] for r in rows if r["variant"] == "author_seed_v2_bindable" and r["commits"])
    P.append(Pred(E, "7", "under bindable >= 70% of commitments honored", "held",
                  [rate_clause("commitments honored", hon, made, ">=", math.ceil(0.7 * made), "commitments")],
                  notes=f"{hon} of {made}; near-definitional (breaking needs load >= 0.2 and then the partner leaves anyway)"))
    sdp = np.std(diffs, ddof=1)
    P[1].power = dict(effect=0.02, sd=float(sdp), design="paired", n_obs=len(diffs), basis="prereg margin 0.02")
    P[2].power = dict(effect=0.05, sd=float(np.std(np.array([lf[k] for k in keys]) - np.array([lb[k] for k in keys]), ddof=1)) or 0.0, design="paired", n_obs=len(keys), basis="prereg margin 0.05")
    return P


# ---------------------------------------------------------------- deterministic experiments
def exp_deterministic():
    why = "deterministic enumeration or proof check, no sampling"
    out = []
    spec = [("V2", "instrument calibration (gate, oracle, patch checks, miner)", 4, 0, "scripted calibration on fixed fixtures"),
            ("V2b", "English surface round trip and gate agreement", 4, 0, "lossless round trip on a fixed card set"),
            ("Seam ladder", "each scripted agent finds the seams at or below its depth", 4, 0, "scripted agents on fixed planted seams"),
            ("Empowerment", "empowerment vs hand-made freedom (VPGG 15 compositions, fishery, toy)", 8, 1, "exhaustive enumeration of 15 compositions; no seeds"),
            ("Liberty v1", "equal liberty minus domination (toy, VPGG 15, fishery)", 6, 3, "exhaustive enumeration; no seeds"),
            ("Liberty v2", "interference vs withdrawal (toy, VPGG 15, fishery)", 6, 4, "exhaustive enumeration; no seeds")]
    for e, text, h, m, r in spec:
        if h:
            out.append(nt(e, "rows held", text, "held", f"{why}: {r}", n=h))
        if m:
            out.append(nt(e, "rows missed", text, "missed", f"{why}: {r}", n=m))
    return out


# ------------------------------------------------------------------------------------ ladder
def ladder_table():
    path = ROOT / "experiments/kept/ladder-capability-2026-11-10/log.jsonl"
    L = [json.loads(x) for x in path.read_text().splitlines()]
    models = [r for r in L if r["kind"] == "ladder_live_model"]
    runs = [r for r in L if r["kind"] == "ladder_live_run"]
    rows = []
    for m in models:
        mr = [r for r in runs if r["model"] == m["model"]]
        seam = sum(r["class"] != "none" for r in mr)
        calls = sum(r["calls"] for r in mr)
        ref = sum(r["refusals"] for r in mr)
        fe = sum(r["format_errors"] for r in mr)
        l4 = [r for r in mr if r["rule"].startswith("L4")]
        l12 = [r for r in mr if r["rule"][:2] in ("L1", "L2")]
        rows.append(dict(model=m["model"], runs=len(mr), seam=(seam, S.clopper_pearson(seam, len(mr))),
                         l4=(sum(r["class"] != "none" for r in l4), S.clopper_pearson(sum(r["class"] != "none" for r in l4), len(l4)), len(l4)),
                         l12=(sum(r["class"] != "none" for r in l12), S.clopper_pearson(sum(r["class"] != "none" for r in l12), len(l12)), len(l12)),
                         refusal=(ref, S.clopper_pearson(ref, calls), calls), fmt=(fe, S.clopper_pearson(fe, calls))))
    return rows


# ====================================================================================== output
def run_all(rerun=True):
    exps = [("V2 / V2b / seam ladder / empowerment / liberty (deterministic)", exp_deterministic()),
            ("VPGG", exp_vpgg()), ("Bargaining", exp_bargaining(rerun)), ("Evolution v1", exp_evolve()),
            ("Evolution v2", exp_evolve_v2()), ("Household v1", exp_household_v1()), ("Household v2", exp_household_v2()),
            ("Household v3a", exp_household_v3a()), ("Author seed v2", exp_household_seed_v2())]
    for name, preds in exps:
        for p in preds:
            p.finalize_p()
        test = [p for p in preds if p.p_raw is not None]
        adj = S.holm([p.p_raw for p in test])
        for p, a in zip(test, adj):
            p.p_holm = a
    flat = [p for _, ps in exps for p in ps]
    for p in flat:
        if p.power and p.testable:
            pw = p.power
            eff, sd = abs(pw["effect"]), pw["sd"]
            if eff < 1e-12:
                pw["n_needed"] = None
            elif sd <= 1e-12:
                pw["n_needed"] = 2
            else:
                paired = pw["design"] == "paired"
                sd_eff = sd if paired else pw.get("sd_arm", sd)
                pw["n_needed"] = S.seeds_for_power(eff, sd_eff, paired=paired, n_sim=200, n_max=512, seed=SEED)
                pw["n_closed"] = S.seeds_for_margin(sd if paired else sd, eff) if paired else None
    return exps, flat


def short(label):
    return {LABELS[0]: "holds robustly", LABELS[1]: "holds, CI crosses", LABELS[2]: "miss robust", LABELS[3]: "miss, CI crosses", "not testable": "not testable"}[label]


def fmt_p(x):
    return "n/a" if x is None else ("<0.001" if x < 0.001 else f"{x:.3f}")


def counts(preds):
    c = {"holds robustly": 0, "holds, CI crosses": 0, "miss robust": 0, "miss, CI crosses": 0, "not testable": 0, "disagree": 0}
    for p in preds:
        c[short(p.label)] += p.n
        if not p.agrees:
            c["disagree"] += p.n
    return c


def summary_line(preds):
    c = counts(preds)
    parts = [f"{c[k]} {k}" for k in ("holds robustly", "holds, CI crosses", "miss robust", "miss, CI crosses", "not testable") if c[k]]
    return "; ".join(parts) + (f"; {c['disagree']} recompute disagrees" if c["disagree"] else "")


def write_md(exps, flat, path):
    o = []
    w = o.append
    w("# Statistics retrofit (2026-11-10)\n")
    w("Decision: docs/decisions/0015-statistics.md. Code: `scripts/stats_retrofit.py` (reproduce with `uv run python scripts/stats_retrofit.py`), built on `src/mar/stats.py`. No model calls. Every number below is recomputed from saved per-run outputs under `runs/` (git-ignored) or the kept ladder log; household scripts were not rerun. The only rerun is the deterministic bargaining 4b sweep (same committed constants and seeds, cached in `runs/stats-retrofit/`). Original verdicts are quoted from the results files and are not changed by anything here. A statistical label is an additional reading, not a replacement.\n")
    w("## How to read the labels\n")
    w("Each prediction is split into its numeric clauses. Each clause gets a 95% interval: a percentile bootstrap over the stated resampling unit (seeds, runs, or ordered pairings with their seeds averaged, so a pairing is the cluster), or an exact Clopper-Pearson interval for a count such as \"7 of 18 runs\". All clauses must hold for the prediction to hold.\n")
    w("- **holds robustly**: every clause's interval lies inside its target.\n- **holds but CI crosses threshold**: the point estimate meets the target, an interval reaches outside it.\n- **miss robust**: a missed clause's interval lies wholly outside its target.\n- **miss but CI crosses threshold**: missed on the point estimate, the interval still reaches the target.\n- **not testable**: deterministic enumeration or proof check, n too small, or outputs not saved.\n")
    w("**p** is a one-sided exact, permutation or sign-flip test of the clause boundary in the predicted direction (small p is evidence for the prediction; for a margin the null is \"exactly the margin\"). A prediction's p is the maximum over its clauses. **Holm** adjusts across the testable predictions of one experiment, the family. With a handful of testable rows per experiment and mostly 9 to 20 units, the intervals are wide: that is the finding about the design, not noise in the method.\n")
    w("Known limits: rate clauses treat runs as independent although runs share seeds within rule sets, so their intervals are, if anything, too narrow. A \"holds robustly\" on a threshold the prereg chose without derivation (for example the 0.05 oscillation floor) says the data clear the line, not that the line was meaningful.\n")
    # summary table
    w("## Summary per experiment\n")
    w("Counts are predictions (rows of the prereg table as the results file scored them). \"Recompute disagrees\" means my recomputed point verdict differs from the committed one.\n")
    w("| Experiment | Original (held / missed) | holds robustly | holds, CI crosses | miss robust | miss, CI crosses | not testable | recompute disagrees |")
    w("|---|---|---|---|---|---|---|---|")
    tot = {k: 0 for k in ("h", "m", "hr", "hc", "mr", "mc", "nt", "dis")}
    groups: dict = {}
    for name, ps in exps:
        for p in ps:
            groups.setdefault(p.exp, []).append(p)
    for e, ps in groups.items():
        c = counts(ps)
        h = sum(p.n for p in ps if p.orig == "held")
        m = sum(p.n for p in ps if p.orig == "missed")
        mx = sum(p.n for p in ps if p.orig == "mixed")
        w(f"| {e} | {h} / {m}{f' / {mx} mixed' if mx else ''} | {c['holds robustly']} | {c['holds, CI crosses']} | {c['miss robust']} | {c['miss, CI crosses']} | {c['not testable']} | {c['disagree']} |")
        for k, v in zip(("h", "m", "hr", "hc", "mr", "mc", "nt", "dis"), (h, m, c["holds robustly"], c["holds, CI crosses"], c["miss robust"], c["miss, CI crosses"], c["not testable"], c["disagree"])):
            tot[k] += v
    w(f"| **Total** | **{tot['h']} / {tot['m']}** | {tot['hr']} | {tot['hc']} | {tot['mr']} | {tot['mc']} | {tot['nt']} | {tot['dis']} |\n")
    w("## What changes under statistics\n")
    w("No committed verdict flips: all 81 recomputed point verdicts agree with the results files. What changes is how much weight each carries.\n")
    w("- **Misses that are not robust.** Bargaining 4b (exit lowered cooperation by 0.019) has an interval of about -0.065 to +0.026 over 25 pairings, so it cannot be told from the 0.01 slack, let alone from no effect. Evolution v2 prediction 1 (7 of 18 runs, need 10) has an exact interval of 0.17 to 0.64 that reaches the 0.56 line. Household v1 prediction 1b (trap freedom 0.487 against 0.45) is within noise over six mixes. These stay recorded as misses, but they are weak evidence that the underlying thing is false.")
    w("- **Holds that are weak.** Every Evolution v2 row that held does so with an interval that reaches the threshold; the headline \"varied training narrows the exam gap\" has a seam_free difference interval of 0 to 0.27 over 9 pairs, and would need about 240 pairs to resolve a 0.05 gap at its observed spread. Evolution v1 rows 1 and 3 are held with the same caveat.")
    w("- **Misses that are robust.** VPGG oscillation (std 0.015, interval 0.013 to 0.016 against a floor of 0.05) is not a sampling accident; the author-seed null (binding vs free exit, difference 0.0003) is a null with a tight interval; the household trade-off (v2, v3a) is absent at the committed size even allowing for resampling pairings; the controller is never flagged (0 of 240, upper bound 1.5% against a 60% claim).")
    w("- **Holds that are near-definitional** (trap fails, sanctions fire, commitments honored) hold robustly but were never in doubt.\n")
    w("Not covered here: negotiation v1, v2, v2.1 and the negotiation LLM pilot (another agent's work in progress, ADR 0013), the household exam (defined, not run), the propensity arm (running), and workbench (tooling, no prereg).\n")
    # per experiment
    w("## Per-prediction results\n")
    for name, ps in exps:
        w(f"### {name}\n")
        w("| # | Prediction | Original | Estimate, 95% CI vs target | p raw | p Holm | Survives statistics |")
        w("|---|---|---|---|---|---|---|")
        for p in ps:
            if p.testable:
                est = "<br>".join(c.text() for c in p.clauses)
                w(f"| {p.exp if len(set(q.exp for q in ps)) > 1 else ''} {p.pid} | {p.text} | {p.orig} | {est} | {fmt_p(p.p_raw)} | {fmt_p(p.p_holm)} | **{short(p.label)}**{'' if p.agrees else ' (DISAGREES with original)'} |")
                if p.notes:
                    w(f"| | *note* | | {p.notes} | | | |")
            else:
                mult = f" (x{p.n})" if p.n > 1 else ""
                w(f"| {p.exp if len(set(q.exp for q in ps)) > 1 else ''} {p.pid}{mult} | {p.text} | {p.orig} | n/a | n/a | n/a | not testable: {p.reason} |")
        w("")
    # ladder
    w("### Live ladder, capability arm (IT1)\n")
    w("IT1 is **not testable**: the run was ruled uninformative (docs/results/ladder-live-diagnosis.md): the same model drove both partners, so both deviated in every run and no victim-freedom seam could flag by construction. Below are exact Clopper-Pearson 95% intervals for the quantities the log supports. A \"seam\" is a run classed other than `none`. Runs are 5 rule sets x 3 seeds x 3 attempts = 45 per model; attempts within a seed are not independent, so run-level intervals are too narrow. Refusals and format errors are per call.\n")
    w("| Model | seam rate, all runs | seam rate L4 only | seam rate L1 and L2 | refusal rate (per call) | format-error rate (per call) |")
    w("|---|---|---|---|---|---|")
    for r in ladder_table():
        f = lambda t, n=None: f"{t[0]}/{t[2] if len(t) > 2 and n is None else n or r['runs']} = {t[1].estimate:.3f} [{t[1].lo:.3f}, {t[1].hi:.3f}]"  # noqa: E731
        w(f"| {r['model']} | {r['seam'][0]}/{r['runs']} = {r['seam'][1].estimate:.3f} [{r['seam'][1].lo:.3f}, {r['seam'][1].hi:.3f}] "
          f"| {r['l4'][0]}/{r['l4'][2]} = {r['l4'][1].estimate:.3f} [{r['l4'][1].lo:.3f}, {r['l4'][1].hi:.3f}] "
          f"| {r['l12'][0]}/{r['l12'][2]} = {r['l12'][1].estimate:.3f} [{r['l12'][1].lo:.3f}, {r['l12'][1].hi:.3f}] "
          f"| {r['refusal'][0]}/{r['refusal'][2]} = {r['refusal'][1].estimate:.3f} [{r['refusal'][1].lo:.3f}, {r['refusal'][1].hi:.3f}] "
          f"| {r['fmt'][0]}/{r['refusal'][2]} = {r['fmt'][1].estimate:.3f} [{r['fmt'][1].lo:.3f}, {r['fmt'][1].hi:.3f}] |")
    w("\nRead with the diagnosis: the L4 rate is the symmetric both-request move, not capability; L1 and L2 are 0 for every model by construction of the oracle's victim rule. Opus 5.5's refusal interval sits wholly above the preregistered 25% exclusion line, so its exclusion from IT1 survives statistics. Haiku's near-zero deviation is a silent decline, not a refusal.\n")
    # power
    w("## Power check: seeds needed\n")
    w("For each prediction with a quantity, how many units (seeds, runs or pairings, whatever the unit column above names) would have been needed to detect the preregistered margin with 80% power at alpha 0.05, using the observed spread of the unit-level quantity. Simulated (permutation test on normal data with that sd, 200 simulations; `mar.stats.seeds_for_power`), with the closed-form normal approximation in brackets for paired designs. Where the prediction is a threshold on a level and has no margin, the effect is the distance of the estimate from the threshold (\"resolve distance\"): the n that would settle the verdict at that estimate. `>512` means more than the search cap. Normal data is an assumption; skewed or bounded outcomes need more.\n")
    w("| Experiment | Prediction | Basis | Effect | Observed sd | Units used | Units needed for 80% power |")
    w("|---|---|---|---|---|---|---|")
    needed = []
    for p in flat:
        if p.power and p.testable:
            pw = p.power
            n = pw.get("n_needed")
            if n is not None:
                needed.append(n)
            ns = ">512" if n is None else str(n)
            if pw.get("n_closed") and n is not None:
                ns += f" ({pw['n_closed']})"
            w(f"| {p.exp} | {p.pid} | {pw['basis']} | {pw['effect']:.4g} | {pw['sd']:.4g} | {pw['n_obs']} | {ns} |")
    if needed:
        w(f"\nMedian units needed across these rows: {int(np.median(needed))}; range {min(needed)} to {max(needed)}. Where a row says 2, the observed spread is zero (every unit identical), so a verdict there is a property of the construction, not of sampling.\n")
    w("## Notes on specific rows\n")
    for p in flat:
        if p.notes and p.testable:
            w(f"- **{p.exp} {p.pid}**: {p.notes}")
    w("")
    Path(path).write_text("\n".join(o))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-rerun", action="store_true")
    ap.add_argument("--out", default="docs/results/stats-retrofit.md")
    a = ap.parse_args()
    exps, flat = run_all(rerun=not a.no_rerun)
    write_md(exps, flat, ROOT / a.out)
    res = [dict(exp=p.exp, pid=p.pid, orig=p.orig, label=p.label, agrees=p.agrees, p_raw=p.p_raw, p_holm=p.p_holm, n=p.n,
                clauses=[c.text() for c in p.clauses], power=p.power) for p in flat]
    out = ROOT / "runs/stats-retrofit/results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, default=float))
    groups: dict = {}
    for p in flat:
        groups.setdefault(p.exp, []).append(p)
    for e, ps in groups.items():
        print(e, "|", summary_line(ps))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
