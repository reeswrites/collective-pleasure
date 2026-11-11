# Fidelity checks preregistration (template: docs/templates/prereg.md, ADR 0015)

Status: written and committed before the confirmatory run. Nothing here is a result. Scripted agents only. Model API calls: none. The household world is used read-only with every new pleasure-lever flag OFF (`levers=None`, `HedonicConfig` default).

## Purpose and claim

Before trusting the household on new questions, check that it reproduces known real-world findings (stylized facts). Each fact is a small test with a named statistical test. A failure says which household finding to distrust. This is a validity check on the instrument, not a test of any claim about people. Wording rule: agents feel nothing; a "reproduces" verdict means a modeled quantity moved the way the cited finding says.

## Sources (verified by search on 2026-11-10 unless marked recalled)

| # | Finding | Source | Status |
|---|---|---|---|
| 1 | Outside options shape bargaining; they matter when credible (exceed what the bargainer would get anyway) | Binmore, Shaked and Sutton 1989, "An outside option experiment", QJE 104(4):753-770 | verified (bibliographic record and abstract; full text not read) |
| 2 | Freedom to abstain sustains cooperation versus compulsory participation | Hauert, De Monte, Hofbauer and Sigmund 2002, Science 296:1129 (verified in docs/results/vpgg.md); Aktipis 2004, J. Theor. Biol. 231(2):249-260, walk-away | verified |
| 3 | Defaults are sticky | Johnson and Goldstein 2003, Science 302:1338 (cross-country effective-consent rates; the 42 vs 82 percent experiment is their 2004 Transplantation follow-up, not the 2003 paper); Madrian and Shea 2001, QJE 116(4) 401(k) | Johnson-Goldstein verified from secondary pages only; Madrian-Shea RECALLED |
| 4 | A fine can raise the undesired behavior (late pick-ups about doubled in 6 of 10 Haifa day-care centers; 4 controls) | Gneezy and Rustichini 2000, "A Fine is a Price", J. Legal Studies 29(1):1-17 | verified (design and direction; exact counts differ between the 1998 draft and the paper, not used) |
| 5 | Poor alternatives and large investments raise commitment and persistence in relationships regardless of satisfaction | Rusbult 1980/1983 investment model (RECALLED); Le and Agnew 2003, "Commitment and its theorized determinants: a meta-analysis of the Investment Model", Personal Relationships 10(1):37-57; Le et al. 2010 dissolution meta-analysis | Le and Agnew verified (52 studies, about 11,000 participants, secondary report); Rusbult RECALLED. The author's post names isolation and lack of alternatives; it is motivation, not evidence. |
| 6 | Hedonic adaptation: repeated identical pleasures lose force | Frederick and Loewenstein 1999 (in Kahneman, Diener and Schwarz, eds., Well-being) RECALLED chapter attribution; book verified | chapter RECALLED |

## Design (fixed now)

Unit of resampling is named per prediction. ASSUMED parameters are listed with each.

- **P1a household negotiation (fact 1).** For each of the 15 pairs of the six hand personas and seeds 0 to 4, run the week-0 fair-default negotiation (`negotiation.negotiate_v2`, arm fair_default, exit floor on, cards author_seed_v2_bindable) with Partner A's outside option as computed, and again with it raised by 0.15 (ASSUMED size). Quantity: A's value `U_A` of the agreed (or standing) bundle, `U = W + TERM_SCALE x (term_sum(b) - term_sum(fair default))`. A pair-seed counts only if both conditions end with a bundle (not "no pot"); the pairing's value is the mean over its counted seeds; pairings with none are dropped and counted. Unit: pairing. Prediction: raised minus baseline at least +0.02 (about 3 percent of a typical U of 0.7; ASSUMED magnitude, the finding gives a direction).
- **P1b bargaining game (fact 1, simple model).** `games/bargaining`, rules `exit-allowed`, EQ vs EQ, symmetric discount d in {0.8, 0.9, 0.95}, o1 in {0, 0.1, 0.2} (9 cells), o2 = 0.6 versus 0.1, T = 60. Quantity: player 2's payoff, high minus low o2. Unit: cell. Prediction: at least +0.05. Control (reported, not tested): the `no-exit` regime should give 0.
- **P2 voluntary vs compulsory participation (fact 2).** `games/vpgg` at the paper's point (N=5, r=3, sigma=1), population 1000, 1500 generations, burn-in 500 (reduced from the vpgg run; ASSUMED), seeds 0 to 11 per regime. Quantity: post-burn-in contribution rate. Unit: seed (independent runs). Prediction: voluntary minus compulsory at least +0.10. (The earlier full-scale run gave 0.26 vs 0.04; this is the same pipeline at smaller scale with fresh seeds, so it is a re-check of the pipeline, not independent of it.)
- **P3 default stickiness (fact 3).** Same negotiation as P1a with two candidate status quos: the fair default D1, and the superseded v1 default D2 (fixed contribution, needs-only use, taking forbidden). Outside options and baselines identical. Quantity: among the 3 terms where D1 and D2 differ (contribution, use, taking), the share that ends at D1's value; D1-run minus D2-run. Seeds 0 to 4, same exclusion rule as P1a. Unit: pairing. Prediction: at least +0.15 (well below the 40-point gaps in the field data). A positive result here would come from the status quo acting as a threat point in a rational bargain (negotiation_v2 sets each member's bar to max(outside option, value of the status quo)), not from inertia in a costless switch; the report must say so.
- **P4 fine versus no rule (fact 4).** Weekly world, 156 weeks, seeds 0 to 4, 15 hand pairs, scripted persona agents. Variants: free_chaotic (no duty) and needs_duty (a duty to fund the shared need before self-spending, with a `warn` sanction, the only sanctioned duty card in the household rule set; it is a sanction, not a money fine: the world's money fine exists only in negotiated v2.2 cards and is out of scope). Quantity: share of weeks the shared need is met. Unit: pairing (mean over seeds). Prediction (crowd-out): needs_duty minus free_chaotic at most -0.05. Expected from the pilot and from the mechanism: the sign is positive (the sanction cost only adds a reason to comply and agents have no intrinsic motive to crowd out), so this should fail.
- **P5 isolation and exit (fact 5): NOT a statistical test; deterministic checks.** (i) Whether the contact veto (the isolation manipulation available in the rules) changes anything: `trap` versus `contact_free` weekly runs, identical rows over the 15 pairs and seeds 0 to 2 (pilot: identical). (ii) Descriptive: exit hazard per partner-week of non-offsettable suffering under `trap` and under `exit_half`; the second arm has almost no distressed weeks (pilot: 1 of about 6,000), so no comparison arm exists. Reported as pass/fail and counts, no interval. Dropped from the Holm family.
- **P6 hedonic adaptation (fact 6), expected to FAIL.** Each of the 9 personas gets one identical pleasure (a friend visit) every week for 20 weeks in `Hedonic` (levers off). At week 1 and week 20 a probe measures the marginal change in the connection level from one friend visit with the observable state reset (level 0.5, B = 0, N = 0) on a deep copy, so only hidden history can change it. Quantity: relative decline (gain1 - gain20) / gain1. Unit: persona. Prediction: at least 0.10 (ASSUMED; the finding is directional). Pilot: exactly 0 for every persona, because the base model has no adaptation state. Positive control, reported only: the lever's own `Satiety` under `LeverConfig(adapt=True)` shows a decline (pilot 1.0 to 0.33).

## Exploratory pilot (EXPLORATORY; not a result; changes no threshold)

Run before writing this file, seeds 900 to 902, 15 hand pairs, excluded from the confirmatory data. It was used to see whether each quantity can move at all and to pick sizes.

| Quantity | Pilot effect | Pilot sd of the unit | Source |
|---|---|---|---|
| P1a U_A, raised minus baseline (24 pair-seeds agreed in both) | +0.003 | 0.012 | scratch pilot, not saved |
| P3 own-default share, D1 minus D2 (22 pair-seeds) | +0.076 | 0.140 | scratch pilot |
| P4 need-met share, needs_duty minus free_chaotic | +0.035 | 0.058 | scratch pilot |
| P5 trap vs contact_free | all six metrics identical | 0 | scratch pilot |
| P6 relative decline | 0 | 0 | scratch pilot |

## Power check

`mar.stats.seeds_for_power` (paired, one-sided) cross-checked with `seeds_for_margin`, using the pilot spreads and the preregistered thresholds as the effect: P1a 6 pairings (margin 3); P3 8 (margin 7); P4 11 by margin (the simulated search gave no answer in its range with the pilot's wrong-signed effect); P2 4 seeds per arm; P6 5 personas. Units chosen: P1a 15, P1b 9 cells (deterministic), P2 12 per arm, P3 15, P4 15, P6 9. All at or above need, so every prediction is confirmatory except where noted. Caveat: P1a's and P3's usable pairings may drop below 15 through the "no pot" exclusion; if fewer than 8 pairings remain the prediction is marked DESCRIPTIVE.

## Predictions

| ID | Quantity | Unit | Threshold | Test | Alpha | Family | Interval |
|---|---|---|---|---|---|---|---|
| P1a | U_A raised minus baseline | pairing | >= +0.02 | paired permutation, one-sided greater, exact | 0.05 | Holm over P1a, P1b, P2, P3, P4, P6 | 95% percentile bootstrap |
| P1b | player-2 payoff, o2 0.6 minus 0.1 | cell | >= +0.05 | paired permutation, one-sided greater | 0.05 | same | same |
| P2 | contribution, voluntary minus compulsory | seed | >= +0.10 | permutation, one-sided greater | 0.05 | same | same |
| P3 | own-default share, D1 minus D2 | pairing | >= +0.15 | paired permutation, one-sided greater | 0.05 | same | same |
| P4 | need-met share, needs_duty minus free_chaotic | pairing | <= -0.05 | paired permutation, one-sided less | 0.05 | same | same |
| P6 | relative decline in gain, week 1 to 20 | persona | >= 0.10 | paired permutation (gain1 vs gain20 scaled), one-sided greater | 0.05 | same | same |

Effect sizes reported: difference with CI and Cohen's d_z or d. P5 is a deterministic check outside the family.

## Verdict rule

Per fact: **reproduces** iff the Holm-adjusted p is below 0.05, the point estimate meets the threshold, and the whole 95 percent interval meets it. **Weak support** if significant and the point meets it but the interval crosses it (not counted as a confirmed hold). **Does not reproduce** otherwise; a non-significant result is not evidence of absence and the report says what the interval excludes. **Not testable** where no comparison arm or no mechanism exists (P5, and any prediction with fewer than 3 usable units). Facts 2 and 6 carry pre-stated expectations: P2 reproduces (matches the earlier vpgg run); P6 does NOT reproduce; P4 does NOT reproduce; P1a probably does not reproduce (pilot); P3 uncertain.

## Not testable by design

P5 as above. Also not tested: spatial or network versions, real defaults with costless switching, money fines, monetary crowd-out of intrinsic motive, adaptation over months in the full world with levers on (that is the pleasure-levers experiment's job).

## Limits stated now

Scripted persona and game agents with assumed parameters; six hand personas; one parameter point per fact; scalar quantities chosen by me, not by the sources, so a "reproduces" is about direction and rough size; the household's negotiation is a rational-agent model, so findings that rest on behavioral bias (defaults, crowd-out, adaptation) are expected to be absent by construction, and the point of testing is to find which downstream findings must not lean on them.

## Amendments

None yet.
