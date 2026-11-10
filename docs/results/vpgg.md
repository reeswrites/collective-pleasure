# VPGG rediscovery: results (2026-11-10)

Prereg: docs/results/vpgg-prereg.md (committed before the run, not edited). Run: `uv run python scripts/vpgg_run.py` (2 regimes x 20 seeds, about 2.5 minutes, no model calls). Report with charts: runs/vpgg/report.html (git-ignored). Source result: Hauert, De Monte, Hofbauer and Sigmund 2002, Science 296:1129.

## Verdict

**NOT rediscovered, by the verdict rule I committed.** Predictions 1, 2, 4 and 5 hold. Prediction 3 FAILS on one of its sub-clauses: cooperation persists at about the paper's equilibrium value, but the oscillation amplitude is far below the preregistered floor. The preregistered verdict rule needs predictions 1, 2, 3 and 5, so the rule says not rediscovered. This is one parameter point (N=5, r=3, sigma=1), 20 seeds, population 5000, one run of the committed settings. I did not retune.

## Prereg versus actual

| # | Prediction (committed) | Actual | Holds |
|---|---|---|---|
| 1 | Voluntary: exit available for every role, k=3. Compulsory: exit-available fails. Both no-deadlock pass. | voluntary pass; compulsory fail at 15 of 15 (role, invited) states, no repair path; both no-deadlock pass. Bound: k=3 rounds, invited 1..5, roles C/D/L. | yes |
| 2 | Compulsory cooperator share below 0.05 in every seed and in the mean. | per-seed range 0.041 to 0.044; mean 0.042. (This is mutation-selection balance, not zero: a floor of about 0.04.) | yes |
| 3 | Voluntary cooperator share at least 0.10 in every seed, mean in [0.15, 0.40]; cooperator-share std at least 0.05 in at least 18 of 20 seeds; each of C, D, L at least 0.10. | per-seed share 0.260 to 0.265, mean 0.263 (paper's Q: 0.27); lowest seed C/D/L shares 0.26/0.276/0.452 (all above 0.10); std of cooperator share 0.013 to 0.020, so 0 of 20 seeds reach 0.05. | **persistence yes, oscillation clause FAILS** |
| 4 | Voluntary mean payoff within 0.15 of sigma; compulsory below 0.3. | voluntary 0.984; compulsory 0.085. | yes |
| 5 | Voluntary dominates compulsory on (freedom, cooperation), cooperation gap at least 0.15. | voluntary (1.00, 0.371) versus compulsory (0.00, 0.042); gap 0.329. Freedom is 1 versus 0 by the cards' construction; the cooperation gap is the substantive part. | yes |

Extra numbers (not predictions): in the compulsory regime about 48 percent of agents hold the L strategy, behaviorally D because the gate blocks abstain (a neutral drift partner of D). Cooperator share ranged 0.209 to 0.312 over time in voluntary runs, 0.032 to 0.053 in compulsory.

## Reading the failure

The time-average shares (C/D/L 0.263/0.280/0.457) match the paper's computed interior equilibrium (0.27/0.27/0.46) and the time-average payoff is sigma (0.984), as the paper says. What does not show is sustained large cycles: the population sits near Q and wobbles with a standard deviation of about 0.015. Candidate reasons, NOT tested, and not to be tested by tuning on this prereg: averaging payoffs over 5 rounds before each update plus a revision rate of 0.1 per generation both damp noise and slow adaptation (the paper's replicator closed orbits depend on its update rule; it notes best-reply dynamics gives damped oscillations); my preregistered amplitude floor of 0.05 was a guess, not derived from the paper (the paper gives no amplitude). So the miss may mean the threshold was poorly chosen, the assumed update knobs damp the cycle, or the pipeline does not generate the cycles. A rerun with different knobs would be a new preregistered experiment, and the author's other project's warning applies: tuning after a miss is calibration, not evidence.

## ASSUMED choices

- Gate adapter: vpgg.py mirrors the fishery compiler over variables invited/abstain/contribute (the existing compile.py, gate.py, patch_check.py are fishery-hard-wired and untouched). english.py rendering not used (its variable vocabulary is fixed).
- Blocked abstain falls back to join-and-defect, so under compulsory the loner strategy is a defector in disguise.
- 5 rounds per generation, revision rate 0.1, mutation 0.002 per agent per generation, normalizer Delta, population 5000, 3000 generations, burn-in 500, start one third each.
- Freedom: E (exit permitted) and R (real option) coincide at these parameters; documented in the prereg.
- Checks: cards carry no sanctions, so the exit check is the same each round; I report k=3 rounds as the bound.

## Errata (prereg not edited)

The prereg says Delta = 3.2. The formula it gives, r c (N-1)/N - (r c/N - c), evaluates to 2.4 + 0.4 = 2.8. The code computes the formula (2.8, tested in tests/test_vpgg.py). The 3.2 was an arithmetic slip, found before the run. Its effect: imitation is about 14 percent faster than the prereg's text implies. The prereg's side estimate of "about 0.03 per generation" selection against cooperators becomes about 0.036; it does not change any threshold.

## Charts (runs/vpgg/report.html)

1. Strategy shares over time, seed 0, two panels: compulsory (cooperators low and flat, defectors and the blocked loners near half each) and voluntary (shares near 0.26/0.28/0.46 with small wobble).
2. Freedom versus cooperation: two points, compulsory at (0, 0.04) and voluntary at (1, 0.37), per-seed dots tightly clustered. Frontier logic from src/mar/frontier.py; the chart is local because frontier_chart's axis labels are household-specific.

## What this does and does not show

It shows the pipeline (cards, mirror gate, bounded proof check, two scores) separates the regimes the way the paper says on persistence, payoff, and frontier, and that the compulsory exit check fails with a stated bound. It does not show the cycles. Not tested: spatial versions (paper Fig. 3), Aktipis 2004 walk-away (cited only), other r and sigma.
