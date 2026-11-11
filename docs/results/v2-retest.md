# Seed v2 retest: results (2026-11-11)

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Prereg: docs/results/v2-retest-prereg.md, committed with Amendment 1 (c9634a4) before the confirmatory run. Code: src/mar/retest.py, scripts/v2_retest_run.py; the fixes in src/mar/hedonic.py, src/mar/worlds/household.py, src/mar/negotiation.py (design: docs/results/household-fixes-design.md). Run: `--run --pairs 180 --seeds 8` (8,640 confirmatory runs in 30 minutes, 4,480 descriptive runs in 22 minutes), `--stay --seeds 8` (640 runs), `--analyze`. Raw records: runs/v2-retest/*.json.gz and analysis.json (git-ignored). Scripted persona agents, no model calls, every parameter ASSUMED.

## Headline

**By the preregistered rule, the author's condition is met for seed v2.2 and for seed v2.3, under this model.** The rule is the author's: "show both, judge on pleasure"; "everyone counts". With the household fixes on and the levers on, across 180 pairings:

- P1: v2.2 minus the baseline, mean pleasure: **+0.024 [+0.017, +0.031]**, Holm p 0.0002, d_z 0.48. Holds robustly.
- P2: v2.3 minus the baseline: **+0.038 [+0.030, +0.045]**, Holm p 0.0002, d_z 0.69. Holds robustly.
- P3: v2.3 minus v2.2: **+0.014 [+0.010, +0.017]**. Holds robustly.

Read it with four caveats. Each comes from a preregistered line.

1. **The fixes did not close the gap. Letting the baseline decline did.** P4 (the fixes narrow the gap) is +0.0004 [-0.005, +0.005], not shown. With the fixes off, v2.2 is already +0.024 above a baseline that may decline (V22-0 0.883 vs BASE-0 0.860). It is level with the old imposed baseline (V22-0 0.883 vs BASE-0i 0.885). Letting the baseline decline costs it 0.025 in pleasure (C2: -0.025 [-0.029, -0.020]). So the earlier negative gap came mostly from comparing a free-to-decline v2.2 with a baseline that could not decline. The author's decision to give both arms the same choice ("yes pairs should be allowed to not form a househodl") is what flips the sign.
2. **On the 15 hand pairings alone, the condition is not shown.** P1 there is +0.002 [-0.017, +0.021] and P2 is +0.018 [-0.007, +0.044] (C6). The confirmatory win comes from the grid personas, which are 165 of the 180 pairings. Their principles are placeholders, and the scripted policy reads only their weights and axes.
3. **Many households do not form, or they end.** Share of weeks lived together: baseline 0.33, v2.2 0.43, v2.3 0.57, against 0.94 under the old imposed baseline. Leaving on the outside option (`bar_leave`) ends about half of the households in the fixes-on arms. "Everyone counts", so people living apart are scored where they are. Among pairs that formed in both arms (12 to 27 percent of pair-seeds), the gaps are larger: P1 +0.036, P2 +0.040 (C8, descriptive).
4. **The pleasure is partly written into the model.** Turning contact off lowers mean pleasure by 0.030 (v2.2) and 0.037 (baseline) (C5). Specialization's saving is by construction. What the run shows is that the confirmed seed produces more modeled pleasure than the baseline, by a stated amount, once both face the same choice to form. It does not show that it would in people.

## Prereg vs actual

Primary family (Holm, one-sided, paired sign-flip permutation on pairing means, 95 percent percentile bootstrap; 180 pairings, seeds 0 to 7):

| ID | Quantity | Estimate [95% CI] | Holm p | Label |
|---|---|---|---|---|
| P1 | V22-F minus BASE-F, mean pleasure | +0.0239 [+0.0169, +0.0311] | 0.0002 | holds robustly |
| P2 | V23-F minus BASE-F, mean pleasure | +0.0375 [+0.0297, +0.0454] | 0.0002 | holds robustly |
| P3 | V23-F minus V22-F, mean pleasure | +0.0136 [+0.0100, +0.0173] | 0.0002 | holds robustly |
| P4 | D(V22-F) minus D(V22-0), mean pleasure | +0.0004 [-0.0046, +0.0053] | 0.44 | not shown |

Secondary (shown beside the verdict, not deciding it):

| ID | Quantity | Estimate [95% CI] | Holm p | Label |
|---|---|---|---|---|
| S1 (descriptive) | P1 in net wellbeing | +0.0288 [+0.0150, +0.0431] | 0.0004 | interval above 0 |
| S2 (descriptive) | P2 in net wellbeing | +0.0577 [+0.0413, +0.0747] | 0.0003 | interval above 0 |
| S3 | non-offsettable suffering, V22-F minus BASE-F (a rise would be the finding) | -0.0023 [-0.0058, +0.0012] | 1.0 | no rise |
| S4 | non-offsettable suffering, V23-F minus BASE-F | -0.0067 [-0.0108, -0.0027] | 1.0 | no rise (it falls) |
| S5 (descriptive, 35 usable pairings) | stay-worth-it share, V22-F minus BASE-F | -0.0042 [-0.0089, -0.0004] | 1.0 | miss: slightly lower under v2.2 |
| S6 | slid-into share, V23-F minus V22-F | -0.0295 [-0.0370, -0.0224] | 0.0003 | holds robustly (fewer slid-into partner-windows under v2.3) |

Non-offsettable suffering on its own line (mean weekly; share of person-weeks with any): baseline 0.028 (5.6 percent), v2.2 0.026 (5.1), v2.3 0.022 (4.3), fixes-off baseline 0.022, old imposed baseline 0.014 (2.8). The fixes-on arms carry more non-offsettable suffering than the old imposed baseline. That is mostly the cost of households ending. It is not a v2.2 or v2.3 effect.

## Descriptive lines

- **C1 (replication).** V22-0 minus BASE-0i, hand pairings: -0.015 [-0.048, +0.015]. Pleasure-levers H1 was -0.019 at seeds 0 to 14. The difference is within the 0.005 expected.
- **C2 (the effect of letting the baseline decline).** Pleasure -0.025 [-0.029, -0.020]; net wellbeing -0.031 [-0.040, -0.021].
- **C3 (formation).** Not formed at week 0: BASE-F 0.71, V22-F 0.41, V23-F 0.38, BASE-0 0.57, V22-0 0.35, BASE-0i 0. Ended by week 156: BASE-F 0.50, V22-F 0.49, V23-F 0.35, fixes-off arms 0.18 to 0.19.
- **C4 (trust variants, 40 pairings).** Mean pleasure: only actions 0.914, mostly actions 0.918, words count until tested 0.915. Lowest trust at week 156: 0.76, 0.80, 0.86. Leaves per run: 0.50, 0.52, 0.46. Words keep trust higher and cut leaves a little; pleasure barely moves. The author's "maybe we have to test" gets this answer: in this model the choice hardly matters for pleasure.
- **C5 (one fix off at a time, 40 pairings, versus the same arm with all fixes).** Contact off: -0.030 (v2.2), -0.037 (baseline). Valued money off: -0.009, -0.006. Outside options off (real_outside, nash_terms, bar_leave together): +0.006, +0.014. Fines off: 0.000, 0.000. v2.3 without the unhappiness ladder: -0.003. Contact is the largest lever. The outside-option fix lowers pleasure in both arms, more in the baseline: people leave for alternatives that score well on net wellbeing but lower on pleasure, as the design predicted. Fines do nothing for pleasure, as predicted.
- **C6 (hand pairings only).** P1 +0.002 [-0.017, +0.021]; P2 +0.018 [-0.007, +0.044]. Not shown.
- **C7 (gap between partners' gains over their outside options).** About 0.14 to 0.15 in every arm.
- **C8 (formed in both arms, selected).** P1 +0.036 (pleasure) and +0.037 (net), on 12 percent of pair-seeds; P2 +0.040 and +0.046, on 13 percent; P3 +0.005 and +0.017, on 27 percent.
- **C9 (all-forbidden leave menus, fixes off).** V22-0: 16,222 partner-weeks in 13 of 180 pairings. These partners could not leave at all, because their "proportional" exit term forbids every take the old agent asks for. BASE-0 and BASE-0i: none. Under `take_menu_terms` (fixes on) the count is 0 (M10).

## Manipulation checks

M1 passes in the hand cohort, but in the controller cohort it fails for a design reason (the controller's own vetoes isolate in both arms). M3 fails: terms move +0.0085 against a +0.02 bar. M2, M5, M6, M8 and M9 pass. On the confirmatory data:

- **M4.** Fine terms in 544 of 1,440 V22-F runs and 608 of 1,440 V23-F runs, all in agreed bundles; none in BASE-F. Passes.
- **M7.** Of the 774 leaves under v2.3 (237 + 537), 537 came after a check-in and an early review. 237 skipped the ladder, all at a non-offsettable load of 0.4 or more. Passes.
- **M9.** Leaves on the outside option: BASE-F 767, V22-F 747, V23-F 509.
- **M10.** 0 partner-weeks with an all-forbidden leave menu in the fixes-on arms. Passes.

## Against the expectations stated before the run

I expected P1 not to hold robustly, and D(V22-F) between -0.005 and +0.020. P1 came in above that range (+0.024) and holds. I expected P4 to be positive but small; it is zero. Most of the change came from the baseline-decline rule, which I had estimated at -0.01 to +0.01 for the fixes-off gap; it was +0.024. I expected P3 positive: it is. I expected the not-formed share to rise under `real_outside` in every arm: it did, and much more than I guessed. The fixes' predicted signs held in the ablations: contact up, valued money small, outside options down, fines zero.

## What this says about the author's condition

"yes as long as it can demonstrate pleasure in relationships hedonic technology". Under this model, by the author's rule (judge on pleasure, everyone counts), seed v2.2 and seed v2.3 produce more modeled pleasure than a baseline that faces the same choice to form. v2.3 produces more than v2.2. Non-offsettable suffering does not rise, and slid-into sacrifice is rarer under v2.3. The win does not come from the fixes. It comes from comparing like with like. It does not show on the six hand personas alone. And more than half of all weeks are lived apart, so "pleasure in relationships" here includes the pleasure people find in their friendships and in living apart. Whether that counts is the author's reading to make.

## Limits

- Scripted agents; 38 personas, 32 of them grid personas with placeholder principles; one parameter point per fix; no sweeps.
- Every fix and lever payoff is written into the model. The informative results are sizes, signs and the failures (P4, S5, M3, C6).
- The outside option is a 26-week rollout, and the bar compares net wellbeing while the verdict scores pleasure. A partner can leave for a life that scores lower on pleasure. The `bar_leave` fix makes this mismatch act much more often than before.
- The design was changed in five places before the pilot (Amendment 1 and the design doc's implementation notes). Valued money is weaker than designed.
- S5 used the 40-pairing descriptive cohort; S1 and S2 were marked descriptive before the run (underpowered for net wellbeing).
- Pairings within the 180 share personas, so they are not fully independent units. The interval treats them as independent.

## Reproduction

`uv run python scripts/v2_retest_run.py --checks`, `--pilot`, `--power`, `--run --pairs 180 --seeds 8`, `--stay --seeds 8`, `--analyze`. Tests: `uv run pytest -m '' tests/test_household_fixes.py tests/test_levers_regression.py tests/test_ladder_pin.py tests/test_exit_log_breach.py`.
