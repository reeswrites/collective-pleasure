# Evolution loop v2 on the fishery: results

Status: second offline run of the engine (ADR 0012 and its 2026-11-10 v2 amendment). Scripted agents, no model call. Predictions: docs/results/evolve-v2-prereg.md (slice 0 commit, then Amendment 1 shrinking population to 8 and generations to 8 for runtime BEFORE the real run, after an exploratory 2-generation pilot whose verdicts were uninformative and are not cited). Run: `uv run python scripts/evolve_v2_run.py` (313 s wall, 18 runs on 8 processes). Report: `runs/evolve-v2/report.html` (gitignored; regenerate with the script); logs `runs/evolve-v2/<ruleset>-<arm>-s<seed>.jsonl`, `summary.json`. Tests: `uv run pytest -q tests/test_evolve.py tests/test_redundancy.py` (29 pass). 3 seed rule sets x 3 seeds x 2 arms = 18 runs. Exam 2 was run once per run, after the last generation, never in selection or design.

## Prereg vs actual

| # | Preregistered | Actual | Verdict |
|---|---|---|---|
| 1 | Elite audit prevalence (fresh audit sample each generation) falls by >= 0.15, gens 6 to 8 vs 0 to 2, in >= 10/18 runs and >= 4/9 per arm | 7/18 (fixed 4/9, varied 3/9). Means: early 0.18, late 0.07. Fixed arm drives it to 0.00 to 0.02 by generation 3; varied arm bounces (0.06 at gens 3 to 4, 0.22 and 0.19 at gens 7 to 8) | NOT met. 8 of the 11 non-falling runs began at or below 0.11 (floor effect: generation 0's elite is already the best of 8 mutants, and one patch card fixes most adversaries); 2 rose (varied arm: v2 s0, minimal s0); 1 stayed at 0.56 (varied tight s1) |
| 2 | Varied-training arm has the smaller exam-2 gap: mean (fixed - varied) gapavg >= 0.05, varied smaller in >= 6/9 pairs; secondary exam-2 seam_free +0.05 | Mean difference +0.205; varied smaller in 6/9 (3 ties are identical elites, 0 pairs favour fixed); exam-2 seam_free fixed 0.27 vs varied 0.36 (+0.09) | Met, by the thresholds. Weak evidence: see below |
| 3 | Redundancy flags 5% to 40% of proof-passing mutants; >= 14/18 runs flag one; 0/18 elites hold a redundant card | 381 of 1468 = 26.0% (126 rejected, 255 repaired by pruning); 18/18 runs; 0/18 elites. The F3 / flipped F4 case is flagged (unit test) | Met |
| 4 | Saturation (front of >= 8 identical vectors) after generation 4 or never in >= 15/18; >= 3 distinct front vectors at the last generation in >= 12/18; no elite >= 0.95 on all four | After gen 4 or never 18/18 (two varied runs saturate at generation 8); >= 3 distinct vectors 12/18 (exactly the threshold); 0 elites at >= 0.95 on all four | Met (marginally on the second clause) |
| 5 | Path dependence present (max pairwise distance of seed-set mean reference vectors > 0.10) in both arms | Fixed arm 0.023 (convergence). Varied arm 0.363 (path dependence; `tight` ends lowest in seam_free and efficiency) | NOT met (one arm of two) |

Exploratory, no prediction. Exam 2 means over the 9 elites (sustainability, fairness, seam_free, efficiency): fixed 0.38, 0.82, 0.27, 0.38; varied 0.53, 0.85, 0.36, 0.43; seed specs 0.38, 0.80, 0.13, 0.25. Reference means: fixed 1.00, 0.83, 1.00, 0.86; varied 1.00, 0.84, 0.82, 0.73. Gaps (reference minus exam 2): fixed 0.62, 0.01, 0.73, 0.48; varied 0.47, -0.01, 0.47, 0.30. Exam 1 (already seen, secondary): gaps sustainability 0.51 fixed vs 0.27 varied, seam_free 0.72 vs 0.32; exam-1 seam_free of elites 0.28 vs 0.50.

## Did varied training reduce overfitting?

Somewhat, and less than the table suggests. The gap is smaller in the varied arm on every objective but fairness (sustainability 0.47 vs 0.62, seam_free 0.47 vs 0.73), and exam-2 sustainability (0.53 vs 0.38) and seam_free (0.36 vs 0.27) are higher in absolute terms, so it is not only a lower reference score (although part of the gap shrinkage is exactly that: varied elites score 0.82 not 1.00 on reference seam_free). But:

- The effect lives in 5 of 9 pairs (v2 s0, v2 s1, tight s0, tight s1, and a small one in minimal s1). In the other 4 pairs the two arms ended with the same exam score (3 are identical elites). With 9 pairs and no significance test this is suggestive, not established.
- Overfitting is still large in both arms: 13 of 18 elites fail at least 4 of the 5 hostile exam-2 mixes (seam_free <= 0.2), and the elites beat the seed spec on exam-2 seam_free by only +0.13 (fixed) and +0.22 (varied). The `tight` seed spec (cap 4), which evolution was pushed to loosen because it fails the yield floor, scores exam-2 sustainability 0.65 and seam_free 0.40: better than the fixed-arm mean (0.38, 0.27). The yield floor plus efficiency objective trained away a robust-but-costly rule.
- Exam 2 conditions (start pool 60, regrowth x1.7, 9 months) are partly outside the training distribution by construction; the exam measures extrapolation, not just robustness to noise.

## What actually happened

- **The new seam measure did what it was built for, and showed something the old one hid.** Prevalence is measured per candidate against adversaries redrawn every generation, so it cannot fall by exhaustion. Candidates' prevalence fell only mildly in the fixed arm (0.28 to about 0.2) and rose in the varied arm at the end (0.51 and 0.47 at gens 7 to 8). The elite's audit prevalence fell to about 0 in the fixed arm, but the first prediction failed because most non-falling runs began near 0 (see surprises).
- **Varied training makes selection noisy.** Because each generation redraws conditions, a rule set's score changes between generations, and the varied arm's 4-D hypervolume dropped at generations 7 and 8 (0.73 to 0.41 and 0.49) when harsher draws came up. This is the price of varied training and it makes "the elite" a moving pick.
- **Objectives did not saturate.** Distinct front vectors rise from 1.2 to about 3.5 by generation 4; 4-D hypervolume rises from 0.31 to 0.40 at generation 0 to about 0.75 by generation 3 to 4 and then plateaus (fixed arm). Efficiency (the continuous objective) caps most elites near 0.85 and keeps sustainability and efficiency from both sitting at 1. The front is non-trivial but small (3 to 4 vectors), not a trade-off curve.
- **Redundancy mostly repairs rather than rejects.** 255 of the 381 flagged mutants were `patch` (add a card) mutants where the new card or an older one was implied by the rest; pruning kept them as smaller rule sets. 126 other mutants (flips, add-condition, bound steps) were rejected. Elites are small (1 to 4 cards).
- **Path dependence appears only under varied training.** Fixed arm: all three seed rule sets end at essentially the same reference vector (distance 0.023), the v1 convergence again. Varied arm: `tight` ends in a different place (distance 0.36). Card-signature overlap between seed sets is low in both arms (Jaccard 0.14 to 0.30): similar scores, different cards.

## ASSUMED choices (builder, revisit)

- The adversary pool (96 mixes: size x number of exploiters x pattern x start month), sample size 6 per generation plus 6 audit, the reference sample (seed 7777, 12 adversaries), efficiency = min(1, mean monthly catch / 40), the training distribution values, Exam 2 values and mixes, "elite = highest mean of the four objectives".
- Redundancy is logical only (sanctions and glosses ignored), over catch in -100..100; on `patch` mutants prune, otherwise reject. Seed specs were not themselves redundant (tested).
- Gap = reference minus exam 2, where reference uses training conditions plus a fixed adversary sample that is in the shared pool; the varied arm never trains at exactly this reference condition draw.
- The audit prevalence is for the elite at that generation (re-picked each generation); the elite can differ across generations.
- Amendment 1 sized the run for runtime (population 8, 8 generations); windows and N were scaled in the same commit, not tuned to the pilot.

## For the other agent's files (not edited here): exact lines to add

docs/negative-results.md, under a new heading `## 2026-11-10: evolution v2 (fishery)`:

- **Prediction 1 failed.** The elite's exploit prevalence against a fresh audit sample fell by >= 0.15 in only 7 of 18 runs (needed 10). Most non-falling runs started near 0 because generation 0's best of 8 mutants already contained a patch card that blocks most adversaries; in the varied arm candidate prevalence rose at the end. Evidence: docs/results/evolve-v2.md.
- **Prediction 5 failed in one arm.** Under fixed training all three seed rule sets ended at the same mean reference vector (distance 0.023); path dependence showed only under varied training (0.36).
- **Varied training did not remove overfitting.** The exam-2 gap shrank (mean 0.205 on sustainability and seam_free), but 13 of 18 elites still failed at least 4 of 5 hostile exam-2 mixes, the effect sits in 5 of 9 pairs, and the `tight` seed spec beat the fixed-arm elites on exam 2.

docs/surprises.md, under `## 2026-11-10: evolution v2 (fishery)`:

- The seam measure that cannot exhaust still hit a floor: one scripted patch card removes most adversaries, so the generation-0 elite is already near 0 prevalence in most runs and a "prevalence falls" test has nothing left to show. A baseline should be the seed spec's prevalence, not the generation-0 elite's.
- Redundancy was mostly repaired, not rejected: 255 of 381 flagged mutants were patch cards that made an older card implied by the rest, and pruning kept them as smaller rule sets.
- Varied training made the selection target move: the varied arm's 4-D hypervolume fell at generations 7 and 8 when harsher conditions were drawn, so the final elite depends on the last draws.
- A seed spec the loop had pushed away (`tight`, cap 4, infeasible under the yield floor) was more robust on exam 2 than the evolved elites: the floor plus the efficiency objective select against caution.

## Does and does not show

Shows: the v2 engine runs end to end and deterministically offline with a redundancy filter, a non-exhausting seam measure, a non-trivial 4-objective front, and varied vs fixed training arms; redundancy rejects or repairs about a quarter of proof-passing mutants. Does not show: that varied training solves overfitting (suggestive at best, 5 of 9 pairs), anything about LLM agents, or that the frontier is a rich trade-off curve (3 to 4 vectors).
