# Seed v2 retest preregistration: DRAFT (does seed v2.2, or v2.3, beat the baseline once the household is fixed?)

**DRAFT. Not a preregistration yet.** Seed v2.3 is now confirmed by the author (2026-11-11, with changes; docs/results/seed-v2.3-readback.md). This file stays DRAFT until (1) the fixes in docs/results/household-fixes-design.md are built and pass their manipulation checks, and (2) Amendment 1 (pilot and power check) is written. It is then copied to docs/results/v2-retest-prereg.md and committed before any confirmatory run.

Status: nothing here is a result. Scripted persona-driven agents; no model API calls. Template: docs/templates/prereg.md (ADR 0015).

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

## Purpose and claim

The author confirmed seed v2.2 on one condition, verbatim: "yes as long as it can demonstrate pleasure in relationships hedonic technology" (docs/seeds/author-household-norms-2026-11-10.md). The pleasure-levers run did not show it: with all levers on, v2.2 minus the imposed baseline was D = -0.019 [-0.051, +0.009] in mean pleasure on 15 hand pairings, and that test was underpowered (marked descriptive before the run). The author then approved fixing the household world and retesting: "yes fix then retest if that is best course of aciotn" (experiments/changes.jsonl, 2026-11-11T02:06:55Z).

Two retest decisions by the author (experiments/changes.jsonl, 2026-11-11):

- The score. "pleasure minus suffering yeah i guess if that is what is commonly held" (02:22:46Z). The condition is judged on pleasure minus suffering. Non-offsettable suffering is reported on its own line.
- The baseline. "yes pairs should be allowed to not form a househodl" (02:23:24Z). The baseline must also let pairs decline to form a household. Each person is scored at their actual outcome, living apart included.

This run asks: with the household fixed (contact that matters, money valued per persona, real outside options, opt-in fines), the levers on, and the same formation choice in every arm, does seed v2.2 leave people better off (pleasure minus suffering) than the baseline? Does seed v2.3? A decision this changes: whether the author's condition on v2.2 counts as met, and whether v2.3 replaces v2.2 as the working seed.

Claim ids in docs/claims.md: to be added after the run.

## Design

**Arms.** Every arm runs with all four levers on, as in the pleasure-levers headline (`LeverConfig(adapt=True, ritual=True, commit=True, network=True)`). Negotiated arms use the pleasure-demo protocol: negotiation v2.1, fair default, exit floor, living apart on failure. Baseline arms impose the baseline cards but, under `baseline_may_decline`, a pair forms only if both partners value living under the baseline above their outside option; otherwise both live apart under the same apart protocol as a v2.2 pair with no pot.

| Arm | Rules | Fixes | Baseline may decline |
|---|---|---|---|
| BASE-F | baseline | all four fixes on | yes |
| V22-F | author_seed_v2_bindable | all four fixes on | n/a |
| V23-F | author_seed_v23_bindable | all four fixes on, plus `roles`, `lapse_ladder`, `unhappy_ladder`, `trust_words="mostly"`, `decency` | n/a |
| BASE-0 | baseline | all fixes off (control) | yes |
| V22-0 | author_seed_v2_bindable | all fixes off (control) | n/a |
| BASE-0i | baseline | all fixes off | no (imposed, as before; replication only) |

"All four fixes on" means `contact`, `valued_money`, `real_outside`, `nash_terms`, `fines` on, and `contact_motive` and `fine_crowdout` off. The two sub-flags are behavioral assumptions or fidelity probes and stay out of the headline. Under `fines` with `roles` on, a fine on a lapsed role is on the menu but exists only if both partners accept it (v2.3 rule 17).

**Descriptive arms (smaller cohort: the 15 hand pairings plus the 25 pilot-style pairings drawn with `random.Random(901)`, at the confirmatory seeds).**

- *Trust variants* (the author: "maybe we have to test? but my intutions is mostly actions"). V23-F with `trust_words="actions"` (words move trust 0) and with `trust_words="words"` (words count until tested), against V23-F (`"mostly"`, the default).
- *Attribution.* V22 and BASE with all fixes on except one, for each of the four fixes (8 arms).
- *Ladder attribution.* V23-F with `unhappy_ladder` off (only the role-lapse ladder).

**Cohort.** The last headline had 15 pairings, which was the binding constraint: more seeds shrink each pairing's noise but not the number of pairings. This run adds the 32 grid personas (personas/grid). The population is every non-pressing pairing of the 6 hand personas and the 32 grid personas: 15 hand pairings plus 496 grid pairings plus 192 hand-grid pairings, 703 in all. The confirmatory sample is all 15 hand pairings plus a random sample of the rest, drawn with `random.Random(20261111)` in sorted order, of the size set by the power check. Pressing personas are excluded, as before.

**Unit of resampling.** The pairing. A pairing's value in an arm is the mean over its seeds of the mean over both partners. Arms share seeds (common random numbers), so arm differences are paired within a pairing.

**Seeds.** 0 to S-1, with S set in Amendment 1. Pilot seeds are 900 to 902 and are excluded from every confirmatory number.

**Fixed parameters.** Everything in `HedonicConfig`, `LeverConfig` and `FixConfig` at the values committed with the fixes, named in the design doc. All ASSUMED. Frozen at the commit of Amendment 1.

**Measures per run, per person, at their actual outcome (living together or apart).**

- **Primary: net wellbeing.** Mean over 156 weeks of pleasure minus offsettable suffering minus non-offsettable suffering (the `negotiation.wellbeing` quantity, which the negotiation itself already uses).
- **Its own line: non-offsettable suffering.** Mean weekly non-offsettable suffering, and the share of person-weeks with any.
- **Secondary: mean pleasure** (the measure of every earlier report).
- Formation status (agreed, stood, no_pot; for baseline arms, formed or declined).
- Share of partner-windows flagged slid-into (evaluator, if `slid_flag` is built).
- Stay-worth-it share and stay-held-by-cost share from test 2 (src/mar/stay_test.py, `play_with_stay_test` and `run_summary`), only if stay_test.py is committed before Amendment 1; otherwise those lines are dropped and the report says so.
- Counts of check-ins, early renegotiations and leaves after a ladder, per arm (v2.3 only).
- The gap between the partners' gains over their outside options (Q4: reported as information, not as a failure).

## Manipulation checks (must pass before the confirmatory run; deterministic or descriptive, outside the Holm family)

| ID | Check | Pass |
|---|---|---|
| M1 | Contact veto bites: `trap` vs `contact_free`, fix 1 on, pressing-controller cohort and hand cohort with `contact_motive` on | runs differ, and the restricted partner's mean pleasure is lower under `trap` |
| M2 | Money valued per persona: a persona with money weight 0 gains no pleasure from surplus money; subsistence shortfall still costs it | unit tests pass |
| M3 | Outside options move terms: fidelity P1a rerun with `real_outside` and `nash_terms` on | U_A with outside option +0.15 minus baseline is at least +0.02 among formed pairs |
| M4 | Fines only by choice: in V22-F and V23-F, a fine term (any scope, role lapse included) exists only where both partners accepted it; none in baseline arms | count is exact |
| M5 | Regression: tests/test_levers_regression.py and the new fixes-off tests pass; BASE-0i reproduces the saved pleasure-levers `base_on` records on the shared cells | all green |
| M6 | Baseline may decline: in BASE-F and BASE-0, a pair forms iff both partners' baseline value exceeds their outside option | unit test on constructed cases; count of declines reported |
| M7 | Unhappiness ladder: under V23-F no partner leaves without a prior check-in and early review, except at non-offsettable load `skip_n` or above | exact count of exceptions, each at or above `skip_n` |
| M8 | Trust variants: with `trust_words="actions"` a word event never moves trust; with `"words"` its gain is removed after a lapse within the window | unit tests pass |

If a check fails because of a bug, the bug is fixed and noted in an amendment. No parameter is retuned after seeing outcomes. If M1 or M3 fails for a non-bug reason, the fix is reported as not working and the retest still runs, with that stated.

## Exploratory pilot plan (labeled EXPLORATORY; not a result; changes no threshold)

Seeds 900 to 902. Pairings: the 15 hand pairings and 25 others drawn with `random.Random(900)`. Arms: BASE-F, V22-F, V23-F, BASE-0, V22-0. Quantities, in net wellbeing and in pleasure: the pairing-level differences V22-F minus BASE-F, V23-F minus BASE-F, V23-F minus V22-F, and V22-0 minus BASE-0, with their standard deviations; seed noise within a pairing; the share of pairs that do not form, per arm; runtime per run. The pilot table goes in Amendment 1.

## Power check

What we know now, from the pleasure-levers headline (levers on, imposed baseline, 15 hand pairings, 15 seeds): the standard deviation of the pairing-level difference in mean pleasure was 0.063. The within-pairing seed noise per run was about 0.06, so with 15 seeds most of the 0.063 is real variation between pairings, not seed noise. More seeds will not help much. More pairings will. The spread of net wellbeing, and the spread once the baseline may decline, are not known yet; the pilot measures them. The table below uses 0.063 as a placeholder.

Pairings needed for 80 percent power, paired, one-sided alpha 0.05, sd 0.063, normal approximation n = ((1.645 + 0.842) x sd / effect)^2 (the simulation helper `mar.stats.seeds_for_power` will replace these in Amendment 1, cross-checked with `seeds_for_margin`):

| Smallest effect of interest | Pairings needed |
|---|---|
| +0.030 | 28 |
| +0.020 | 62 |
| +0.015 | 109 |
| +0.010 | 246 |

**Rule for choosing n (fixed now).** The smallest effect of interest is +0.010 in net wellbeing. n is the simulated power requirement for +0.010 at the pilot's spread of the P1 difference in net wellbeing, rounded up to a multiple of 10, at least 120 and at most 703. If more than 703 pairings are needed, P1 to P3 are marked DESCRIPTIVE before the run. Seeds per pairing: S = 4, raised to 8 if the pilot shows seed noise above half the between-pairing spread. At the pilot's measured runtime, the run must fit in 8 hours on the local machine; if it does not, n is cut and the predictions it no longer powers are marked DESCRIPTIVE before the run.

Rough cost now: 250 pairings x 4 seeds x 6 arms = 6,000 runs, plus about 13 descriptive arms on 40 pairings (about 2,100 runs). The last headline ran about 1.3 negotiated runs per second of wall time with 8 workers, so about two hours, plus outside-option rollouts for the new grid personas and for the baseline's formation choice.

## Predictions

D(X) is the difference of pairing means, arm X minus its baseline arm with the same fixes setting. Primary quantity: net wellbeing. Holm family: P1 to P4 (alpha 0.05, one-sided). Tests: paired sign-flip permutation on pairing means (exact if 2^n is small, else 20,000 draws). Interval: 95 percent percentile bootstrap clustered by pairing. Effect sizes: difference with interval, and Cohen's d_z.

| ID | Quantity (net wellbeing) | Unit | Threshold | Test |
|---|---|---|---|---|
| P1 | D(V22-F) = V22-F minus BASE-F | pairing | > 0 | permutation, one-sided |
| P2 | D(V23-F) = V23-F minus BASE-F | pairing | > 0 | permutation, one-sided |
| P3 | V23-F minus V22-F | pairing | > 0 | permutation, one-sided |
| P4 | Fixes narrow the gap: D(V22-F) minus D(V22-0) | pairing | > 0 | permutation, one-sided |

Secondary family (Holm within it, alpha 0.05):

| ID | Quantity | Threshold | Test |
|---|---|---|---|
| S1 | P1 in mean pleasure only | > 0 | as P1 |
| S2 | P2 in mean pleasure only | > 0 | as P1 |
| S3 | Non-offsettable suffering, V22-F minus BASE-F | <= 0 | as P1, one-sided for > 0 (a rise is the finding) |
| S4 | Non-offsettable suffering, V23-F minus BASE-F | <= 0 | as S3 |
| S5 | Stay-worth-it share, V22-F minus BASE-F (only if stay_test.py is committed) | > 0 | as P1 |
| S6 | Slid-into share, V23-F minus V22-F (only if `slid_flag` is built) | < 0 | as P1 |

Descriptive (no verdict wording):

- C1: V22-0 minus BASE-0i in mean pleasure on the hand pairings, compared with the pleasure-levers H1 value of -0.019. Expected equal to within 0.005 at the same seeds; this checks that nothing else moved.
- C2: the effect of letting the baseline decline: BASE-0 minus BASE-0i, in net wellbeing and in pleasure, and the share of baseline pairs that decline.
- C3: not-formed share per arm; V22-F minus V22-0.
- C4: the trust variants: V23-F under "actions", "mostly" and "words", in net wellbeing, trust at week 156, and leaves.
- C5: the attribution arms (one fix off at a time) and V23-F without `unhappy_ladder`.
- C6: P1 and P2 on the 15 hand pairings alone, for continuity with earlier reports.
- C7: the gap between partners' gains over their outside options, per arm.

## Verdict rule

- **The author's condition is met for v2.2** iff P1 holds robustly: Holm-adjusted p below 0.05 and the whole 95 percent interval above 0. If P1 is significant but the interval touches 0, it is "weak support" and the condition is not counted as met. If the point estimate is above 0 but P1 is not significant, the condition is "not shown".
- **The same rule for v2.3** with P2.
- **Non-offsettable suffering is read on its own line.** If P1 holds but S3 shows a significant rise in non-offsettable suffering, the report states both and does not call the condition met without the author's reading. Suffering that cannot be offset is not supposed to be bought back with pleasure (ADR 0010).
- **If P1 holds and S1 fails**, the report says so plainly: v2.2 leaves people better off by pleasure minus suffering, mainly by sparing suffering, not by adding pleasure.
- Results are under the model and ASSUMED parameters. A "met" verdict means the rules produce modeled wellbeing the baseline lacks, not that they would in people.

## Expectations stated now (not predictions, recorded so the report can be checked against them)

From docs/results/household-fixes-design.md. Letting the baseline decline removes most of the old structural gap: the bargainer and steward-wanderer pairings can now live apart in both arms. Before any fix, I expect the gap in net wellbeing to sit between -0.01 and +0.01 (C2 and V22-0 minus BASE-0). With the fixes, D(V22-F) between -0.005 and +0.020. I expect P3 to be positive (roles save effort by construction, and the ladder replaces some exits with renegotiation), P2 to be the likeliest of P1 and P2 to hold, P4 to be positive but small, and the not-formed share to rise under `real_outside` in every arm. Among the trust variants, I expect "words" to keep trust higher and produce fewer leaves but more lapses than "actions", with "mostly" between them and small differences in net wellbeing.

## Not testable by design

The manipulation checks M1 to M8 (pass or fail). The fine counts (M4). The slid-into flag's definition (it is a measure, not a test).

## Limits stated now

- Scripted agents. Grid personas have placeholder principles; the scripted policies use their weights and axes only.
- Every lever and fix payoff is written into the model, so "a fix raises wellbeing" is partly true by construction. The informative results are the sizes, the gap, and the failures.
- One parameter point per fix; no sweeps in this run (Q11: these are sweep centers, a sweep is later work).
- The baseline's formation choice uses a 26-week rollout of the baseline cards against the outside option. It is a model of the choice, with the same horizon as the negotiation's, not the full 156 weeks.
- `contact_motive` and `fine_crowdout` are off in the headline, so the contact veto bites only where a pressing persona exists. The hand and grid cohorts have none.
- v2.3 runs with Claude's defaults on four details the author has not settled (the three jobs, skipping the ladder in severe distress, the slid-into window, bindable only); listed in the read-back.

## Amendments

None yet. Amendment 1 (pilot table, power check, n and S, runtime) is committed before the confirmatory run.

### Draft change log

- 2026-11-11: after the author's v2.3 answers and retest decisions, the primary measure became net wellbeing (pleasure-only became secondary), non-offsettable suffering got its own line, every baseline arm lets pairs decline to form (BASE-0i keeps the old imposed baseline for replication only), the trust-variant arm and the general-unhappiness ladder were added. Nothing had been run.
