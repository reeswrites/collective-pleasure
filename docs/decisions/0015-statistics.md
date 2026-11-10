# 0015. Formal statistics: a statistics layer, and a retrofit of today's results

Status: accepted (2026-11-10, author decision in conversation)

## Context

By the end of 2026-11-10 the repository had 19 indexed experiments and about 80 preregistered predictions, each scored held or missed by comparing a point estimate with a threshold (docs/results/README.md, docs/claims.md). Several of those numbers came from 3 seeds, 9 pairings or 18 runs, and a few misses were small (a cooperation difference of 0.019 against a slack of 0.01). Nothing in the repository gave an interval, a test, a correction for the many predictions in one experiment, or a way to choose how many seeds a run needs. The live ladder, which cost real money, used 3 seeds and a default because nothing told us otherwise. The author asked whether we were doing formal statistical analyses and, when offered both a forward-looking layer and a backward-looking retrofit, took both.

## The author's words (verbatim)

On whether the project does formal statistics (topic formal-statistics, 2026-11-10 21:22 UTC, experiments/questions.jsonl):

> are we doing formal statistical analyses

On the offer of building the statistics layer for future work and also retrofitting today's results (relayed in the task brief; the log entry for this answer was not yet written when this ADR was drafted):

> yes both

## Decision

1. **A statistics layer in the library.** `src/mar/stats.py`, pure numpy, seeded. Percentile and BCa bootstrap intervals, a cluster bootstrap that resamples whole pairings, two-arm and paired permutation tests (exact when small, Monte Carlo otherwise, one- or two-sided), exact Clopper-Pearson and Newcombe/Katz intervals for rates, Cliff's delta and Cohen's d, Holm-Bonferroni, and power by simulation (`seeds_for_power`) with a closed-form cross-check. No scipy.
2. **A retrofit of every finished experiment** that left usable per-run outputs. `scripts/stats_retrofit.py` recomputes each preregistered prediction's quantity with a 95% CI and a test, applies Holm within the experiment, and labels it: holds robustly, holds but CI crosses threshold, miss robust, miss but CI crosses threshold, or not testable. Output: docs/results/stats-retrofit.md. The committed verdicts are not changed; the label is an added reading. Non-household experiments that lacked saved outputs may be rerun with unchanged parameters (done once, for bargaining 4b); household experiments use saved outputs only.
3. **New rules for future work** (CONTRIBUTING.md, docs/templates/prereg.md). Every prediction names its quantity, unit of resampling, test, alpha and correction family. A labeled exploratory pilot feeds a power check before seeds are chosen. Effect sizes are reported with intervals. LLM runs take their seed counts from the power check, never a default of 3.
4. **Deterministic is not a sample.** Proof checks, exhaustive enumerations (empowerment and liberty over 15 compositions) and scripted calibrations are reported as "not testable", not given a spurious interval.
5. **Scope.** Negotiation experiments and the negotiation LLM pilot were in progress under another agent and are not retrofitted here; they adopt the new rules when finished. The household exam (not run) and the propensity arm (running) have nothing to retrofit yet.

## What the retrofit showed (docs/results/stats-retrofit.md)

- No committed verdict flips: all 30 testable recomputed point verdicts agree. Of those 30, 11 hold robustly, 5 hold but the interval crosses, 11 miss robustly, 3 miss but the interval crosses. 51 of 81 rows are not testable, mostly deterministic.
- The weakest committed results are the Evolution v2 holds (every held row has an interval reaching its threshold; the varied-training gap would need about 240 pairs to resolve a 0.05 margin at its spread) and three misses that are not robust (bargaining 4b, Evolution v2 prediction 1, household v1 1b).
- The robust misses are the findings that stand: no VPGG oscillation, the author-seed binding null, no household trade-off at the committed size, the controller never flagged.
- Seeds needed for 80% power at the preregistered margin: a median of 6 for the scripted, low-variance effects, and 14 (household v3a partner empowerment) to 240 or more (Evolution v2 gap, household v1 trap freedom) for contested comparisons, with bargaining 4b out of reach (more than 512 pairings for a 0.01 slack). These are the numbers the next run's seed count is checked against.

## Consequences

- A verdict worded as "held" in a README, a claims row or a paper needs its statistical label next to it. "Holds but CI crosses threshold" is weak support and is not counted as a confirmed hold for any citation.
- Future preregistrations are longer: a pilot, a power table, and a row per prediction with its test. That cost is the point.
- Per-run outputs must be saved (they are under git-ignored runs/ for now; the retrofit md holds the numbers). Experiments that keep only aggregates cannot be given intervals later.
- Limits of the retrofit, stated: rate intervals treat runs as independent (they share seeds within rule sets, so intervals are somewhat narrow); the power numbers assume normal data and use the observed spread, which for bounded or discrete outcomes is optimistic; "every run" claims can never be robust on a finite sample; a few per-run quantities (power-seeking flags) exist only as saved aggregate counts.
- Not decided here: whether to move to a Bayesian reading, and whether multiple experiments should share one Holm family across the repository. Both stay open.

## Status note 2026-11-10 (scope)

The retrofit covers 14 experiments. Negotiation v1, v2, v2.1 and the LLM pilot (docs/results/README.md rows 19 to 22) are not covered and are marked "not covered by retrofit" in docs/claims.md. They adopt these rules when next run. Cached or near-deterministic model output counts less than its row count (Jev's three attempts in the first live run were cached copies), so seeds for the ladder rerun come from a power check on independent draws.
