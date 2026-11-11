# Fidelity checks: results (2026-11-10)

Prereg: docs/results/fidelity-prereg.md (committed before the run, not edited). Run: `uv run python scripts/fidelity_run.py` (about 2 minutes, no model calls); numbers in runs/fidelity/results.json (git-ignored). Code: src/mar/fidelity.py, tests/test_fidelity.py. Household used read-only with all pleasure levers OFF. Agents feel nothing; "reproduces" means a modeled quantity moved as the cited finding says.

## Verdicts

Holm family of six (P1a, P1b, P2, P3, P4, P6), one-sided permutation tests, 95% percentile bootstrap intervals.

| Fact | Test | Estimate [95% CI] | Holm p | Verdict |
|---|---|---|---|---|
| 1 Outside options shape terms, household negotiation (P1a) | U_A, outside option +0.15 minus baseline, 14 pairings, threshold +0.02 | +0.012 [0, 0.025] | 0.375 | **does not reproduce** (right sign, below threshold, not significant) |
| 1 Outside options, bargaining game (P1b) | player-2 payoff, o2 0.6 vs 0.1, 9 cells, threshold +0.05 | +0.125 [0.108, 0.142] | 0.010 | **reproduces** (no-exit control: exactly 0) |
| 2 Freedom to leave sustains cooperation (P2) | contribution, voluntary minus compulsory, 12 seeds per arm, threshold +0.10 | +0.208 [0.203, 0.212] | 0.0003 | **reproduces** (re-check of the vpgg pipeline at smaller scale; not independent of it) |
| 3 Defaults are sticky (P3) | own-default share, D1 minus D2, 11 pairings, threshold +0.15 | +0.197 [0.045, 0.364] | 0.250 | **does not reproduce by the rule** (point above threshold, interval crosses it, exact p cannot get below 0.0625 with 11 pairings and ties; underpowered, not evidence of absence) |
| 4 A fine crowds out compliance (P4) | need-met share, needs_duty minus free_chaotic, 15 pairings, threshold -0.05 | +0.025 [0.007, 0.044] | 1.0 | **does not reproduce** (opposite sign, interval excludes the threshold) |
| 5 Isolation lowers exit | deterministic checks, no interval | trap and contact_free identical in all 45 runs; exits per distressed partner-week 21/5871 (trap), 6/12 (exit_half) | n/a | **not testable** |
| 6 Hedonic adaptation (P6) | relative decline of an identical weekly pleasure, 9 personas, threshold 0.10 | 0.000 [0, 0] | 1.0 | **does not reproduce**, as preregistered (positive control: the lever's own satiety falls from 1.0 to 0.33 over 20 weeks) |

Matches the preregistered expectations: P2 reproduced, P4 and P6 failed, P1a failed. P3 was marked uncertain.

## What each failure implies

- **P1a (and what it shows).** In the household's negotiation, a better outside option mostly changes whether the household forms at all, not the terms inside it: in 38 of 75 pair-seeds one of the two conditions ended with no pot together (so the terms comparison covers only the other 37). Terms-level claims such as "a partner with more money or better prospects gets better terms" should not be cited from the household. Claims that outside options decide whether people stay together are supported by the mechanism (the bar is max(outside option, value of the status quo)). The game (P1b) does reproduce the finding with rational players, so the bargaining pipeline itself is sound.
- **P2.** The household findings that rest on "freedom to leave sustains cooperation" lean on a pipeline that passes this check. Same code as the earlier run, so no new independence.
- **P3.** Whatever default effect shows up in the household is the status quo acting as a threat point in a rational bargain, not inertia under costless switching. Do not cite household results as evidence for a behavioral default effect, or design on the assumption that a good default will be sticky for people.
- **P4.** There is no crowd-out channel: a sanction only adds a reason to comply. Household conclusions of the form "a sanction or fine improves compliance" are biased toward looking good and must not be trusted where crowd-out is the live risk (for example the negotiated fine card N8-fine-some). This test used a `warn` sanction, not a money fine, because no household rule set has a money fine outside negotiated v2.2 cards; that is a limit on this verdict.
- **P5.** The contact veto is inert for the scripted persona agents (trap and contact_free produce identical weeks, hedonic rows included), so any household finding that attributes the trap's harm to the isolating contact veto is unsupported; the harm there comes from the other trap terms. Exits are rare even under sustained distress (0.36 percent of distressed partner-weeks end in exit under the trap), which is qualitatively staying-despite-suffering, but with no comparison arm that is a description, not a reproduction of the investment-model finding.
- **P6.** With levers off the base model has no adaptation, so levers-off pleasure from repeated identical pleasures is overstated; any levers-off pleasure number that depends on repetition (time together, friend visits) should be read as an upper bound. The lever's satiety component does produce adaptation, so the levers-on arms are the ones to use for that question.

## Limits

Scripted agents; six hand personas; one parameter point per fact; assumed thresholds (the sources give directions and, for defaults and fines, field magnitudes much larger than my thresholds); the household negotiation is a rational-agent model so behavioral-bias findings (3, 4, 6) were expected to fail by construction, and the value of the test is naming which results cannot lean on them. P2 reuses the vpgg code. P3 and P1a drop pair-seeds with no pot (about half); selected pairs are not a random sample of pairings. Sources: Madrian-Shea, Rusbult and the Frederick-Loewenstein chapter are cited from memory (marked RECALLED in the prereg); Johnson-Goldstein figures were checked on secondary pages only.
