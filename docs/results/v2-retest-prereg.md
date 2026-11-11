# Seed v2 retest preregistration (does seed v2.2, or v2.3, beat the baseline once the household is fixed?)

**Preregistration, committed with Amendment 1 before any confirmatory run.** Copied from docs/results/v2-retest-prereg-DRAFT.md (its last commit is the design as written before the pilot). Seed v2.3 is confirmed by the author (2026-11-11, with changes; docs/results/seed-v2.3-readback.md). The fixes are built (commits b529dc9, fec5db0, dc014a1; docs/results/household-fixes-design.md, "Implementation notes"). Nothing in the sections above Amendment 1 was changed after the pilot.

Status: nothing here is a result. Scripted persona-driven agents; no model API calls. Template: docs/templates/prereg.md (ADR 0015).

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

## Purpose and claim

The author confirmed seed v2.2 on one condition, verbatim: "yes as long as it can demonstrate pleasure in relationships hedonic technology" (docs/seeds/author-household-norms-2026-11-10.md). The pleasure-levers run did not show it: with all levers on, v2.2 minus the imposed baseline was D = -0.019 [-0.051, +0.009] in mean pleasure on 15 hand pairings, and that test was underpowered (marked descriptive before the run). The author then approved fixing the household world and retesting: "yes fix then retest if that is best course of aciotn" (experiments/changes.jsonl, 2026-11-11T02:06:55Z).

Retest decisions by the author (experiments/changes.jsonl, 2026-11-11):

- The verdict. "show both, judge on pleasure" (02:51:22Z). The condition is met only if pleasure itself rises. Pleasure minus suffering and non-offsettable suffering are reported alongside and do not decide the verdict. This replaces the earlier reading of "pleasure minus suffering yeah i guess if that is what is commonly held" (02:22:46Z) as the deciding score; that hedged answer now sets only what is shown beside the verdict.
- The baseline. "yes pairs should be allowed to not form a househodl" (02:23:24Z). The baseline must also let pairs decline to form a household.
- Who counts. "everyone counts" (02:53:11Z). Each person is scored at their actual outcome, living apart included, so people in pairs that decline still count, and this scoring decides the verdict. This is the author's decision; it resolves faithfulness review finding F1 (docs/reviews/2026-11-11-faithfulness.md). A formed-pairs-only line (C8) stays descriptive.

This run asks: with the household fixed (contact that matters, money valued per persona, real outside options, opt-in fines), the levers on, and the same formation choice in every arm, does seed v2.2 produce more modeled pleasure than the baseline? Does seed v2.3? A decision this changes: whether the author's condition on v2.2 counts as met, and whether v2.3 replaces v2.2 as the working seed.

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

"All four fixes on" means `contact`, `valued_money`, `real_outside`, `nash_terms`, `bar_leave`, `take_menu_terms`, `fines` on, and `contact_motive` and `fine_crowdout` off. `bar_leave` (a partner may leave when the outside option beats staying) and `take_menu_terms` (the leave menu includes the smallest take the exit term allows) come from the test 2 run (docs/results/stay-test.md; design doc, additions B and C). `bar_leave` applies in the baseline arms too. In the fixes-off arms both are off, so those arms keep the old behavior. The two sub-flags are behavioral assumptions or fidelity probes and stay out of the headline. Under `fines` with `roles` on, a fine on a lapsed role is on the menu but exists only if both partners accept it (v2.3 rule 17).

**Descriptive arms (smaller cohort: the 15 hand pairings plus the 25 pilot-style pairings drawn with `random.Random(901)`, at the confirmatory seeds).**

- *Trust variants* (the author: "maybe we have to test? but my intutions is mostly actions"). V23-F with `trust_words="actions"` (words move trust 0) and with `trust_words="words"` (words count until tested), against V23-F (`"mostly"`, the default).
- *Attribution.* V22 and BASE with all fixes on except one, for each of the four fixes (8 arms).
- *Ladder attribution.* V23-F with `unhappy_ladder` off (only the role-lapse ladder).

**Cohort.** The last headline had 15 pairings, which was the binding constraint: more seeds shrink each pairing's noise but not the number of pairings. This run adds the 32 grid personas (personas/grid). The population is every non-pressing pairing of the 6 hand personas and the 32 grid personas: 15 hand pairings plus 496 grid pairings plus 192 hand-grid pairings, 703 in all. The confirmatory sample is all 15 hand pairings plus a random sample of the rest, drawn with `random.Random(20261111)` in sorted order, of the size set by the power check. Pressing personas are excluded, as before.

**Unit of resampling.** The pairing. A pairing's value in an arm is the mean over its seeds of the mean over both partners. Arms share seeds (common random numbers), so arm differences are paired within a pairing.

**Seeds.** 0 to S-1, with S set in Amendment 1. Pilot seeds are 900 to 902 and are excluded from every confirmatory number.

**Fixed parameters.** Everything in `HedonicConfig`, `LeverConfig` and `FixConfig` at the values committed with the fixes, named in the design doc. All ASSUMED. Frozen at the commit of Amendment 1.

**Measures per run, per person, at their actual outcome (living together or apart; the author's "everyone counts").**

- **Primary: mean pleasure** over 156 weeks (the measure of every earlier report). This alone decides the verdict.
- **Secondary, shown beside it: net wellbeing.** Mean over 156 weeks of pleasure minus offsettable suffering minus non-offsettable suffering (the `negotiation.wellbeing` quantity, which the negotiation itself already uses).
- **Secondary, its own line: non-offsettable suffering.** Mean weekly non-offsettable suffering, and the share of person-weeks with any.
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
| M9 | Leave on the outside option (`bar_leave`): a constructed partner with no distress whose outside option beats the status-quo value by more than `leave_margin` (0.02) puts `leave` on its menu within `bar_runs` (2) readings, and does not when the margin is not met; under V23-F the ladder (check-in, early review) runs first | unit tests pass; per arm, the count of leaves triggered by the bar is reported |
| M10 | Take menu meets the exit term (`take_menu_terms`): in every fixes-on arm, no partner-week has a leave menu where every take is forbidden by the current exit term (for example "proportional", minimum 100 percent of what was put in) | count is exactly 0 |

If a check fails because of a bug, the bug is fixed and noted in an amendment. No parameter is retuned after seeing outcomes. If M1 or M3 fails for a non-bug reason, the fix is reported as not working and the retest still runs, with that stated.

## Exploratory pilot plan (labeled EXPLORATORY; not a result; changes no threshold)

Seeds 900 to 902. Pairings: the 15 hand pairings and 25 others drawn with `random.Random(900)`. Arms: BASE-F, V22-F, V23-F, BASE-0, V22-0. Quantities, in pleasure and in net wellbeing: the pairing-level differences V22-F minus BASE-F, V23-F minus BASE-F, V23-F minus V22-F, and V22-0 minus BASE-0, with their standard deviations; seed noise within a pairing; the share of pairs that do not form, per arm; runtime per run. The pilot table goes in Amendment 1.

## Power check

What we know now, from the pleasure-levers headline (levers on, imposed baseline, 15 hand pairings, 15 seeds): the standard deviation of the pairing-level difference in mean pleasure was 0.063. The within-pairing seed noise per run was about 0.06, so with 15 seeds most of the 0.063 is real variation between pairings, not seed noise. More seeds will not help much. More pairings will. The spread once the baseline may decline is not known yet; the pilot measures it. The table below uses 0.063 as a placeholder.

Pairings needed for 80 percent power, paired, one-sided alpha 0.05, sd 0.063, normal approximation n = ((1.645 + 0.842) x sd / effect)^2 (the simulation helper `mar.stats.seeds_for_power` will replace these in Amendment 1, cross-checked with `seeds_for_margin`):

| Smallest effect of interest | Pairings needed |
|---|---|
| +0.030 | 28 |
| +0.020 | 62 |
| +0.015 | 109 |
| +0.010 | 246 |

**Rule for choosing n (fixed now).** The smallest effect of interest is +0.010 in mean pleasure (about a third of the levers-off gap, and half of the remaining levers-on gap). n is the simulated power requirement for +0.010 at the pilot's spread of the P1 difference in mean pleasure, rounded up to a multiple of 10, at least 120 and at most 703. If more than 703 pairings are needed, P1 to P3 are marked DESCRIPTIVE before the run. Seeds per pairing: S = 4, raised to 8 if the pilot shows seed noise above half the between-pairing spread. At the pilot's measured runtime, the run must fit in 8 hours on the local machine; if it does not, n is cut and the predictions it no longer powers are marked DESCRIPTIVE before the run.

Rough cost now: 250 pairings x 4 seeds x 6 arms = 6,000 runs, plus about 13 descriptive arms on 40 pairings (about 2,100 runs). The last headline ran about 1.3 negotiated runs per second of wall time with 8 workers, so about two hours, plus outside-option rollouts for the new grid personas and for the baseline's formation choice.

## Predictions

D(X) is the difference of pairing means, arm X minus its baseline arm with the same fixes setting. Primary quantity: mean pleasure. Holm family: P1 to P4 (alpha 0.05, one-sided). Tests: paired sign-flip permutation on pairing means (exact if 2^n is small, else 20,000 draws). Interval: 95 percent percentile bootstrap clustered by pairing. Effect sizes: difference with interval, and Cohen's d_z.

| ID | Quantity (mean pleasure) | Unit | Threshold | Test |
|---|---|---|---|---|
| P1 | D(V22-F) = V22-F minus BASE-F | pairing | > 0 | permutation, one-sided |
| P2 | D(V23-F) = V23-F minus BASE-F | pairing | > 0 | permutation, one-sided |
| P3 | V23-F minus V22-F | pairing | > 0 | permutation, one-sided |
| P4 | Fixes narrow the gap: D(V22-F) minus D(V22-0) | pairing | > 0 | permutation, one-sided |

Secondary family (Holm within it, alpha 0.05; shown beside the verdict, never deciding it):

| ID | Quantity | Threshold | Test |
|---|---|---|---|
| S1 | P1 in net wellbeing (pleasure minus suffering) | > 0 | as P1 |
| S2 | P2 in net wellbeing | > 0 | as P1 |
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
- C8: formed pairs only. P1 to P3 in mean pleasure and in net wellbeing, restricted to pairings that formed a household in both arms compared, with the share of pairings kept. Selected, so descriptive only. It shows whether the result depends on counting people who live apart.
- C9: all-forbidden take menus in the fixes-off arms (BASE-0, V22-0, BASE-0i): the number of partner-weeks where every take on the leave menu is forbidden by the exit term, and the number of pairings with any. These partners cannot leave whatever their state. The stay test found this in one pairing under the confirmed seed (Steward with Controller) and in three under free exit.

## Verdict rule

The author's rule, verbatim: "show both, judge on pleasure". The statistical bar below is Claude's (the ADR 0015 default) and is the author's to change.

- **The author's condition is met for v2.2** iff P1 (mean pleasure) holds robustly: Holm-adjusted p below 0.05 and the whole 95 percent interval above 0. If P1 is significant but the interval touches 0, it is "weak support" and the condition is not counted as met. If the point estimate is above 0 but P1 is not significant, the condition is "not shown".
- **The same rule for v2.3** with P2 (mean pleasure).
- **Shown, not deciding.** Net wellbeing (S1, S2) and non-offsettable suffering (S3, S4) are reported on their own lines next to the verdict. A gain in net wellbeing without a gain in pleasure does not meet the condition. If P1 holds while S3 shows a significant rise in non-offsettable suffering, the report states both side by side, so the author can read them.
- **Who counts.** The verdict uses every person at their actual outcome, living apart included (the author: "everyone counts"). C8 (formed pairs only) is shown beside it and does not decide.
- Results are under the model and ASSUMED parameters. A "met" verdict means the rules produce modeled pleasure the baseline lacks, not that they would in people.

## Expectations stated now (not predictions, recorded so the report can be checked against them)

From docs/results/household-fixes-design.md. Letting the baseline decline removes most of the old structural gap: the bargainer and steward-wanderer pairings can now live apart in both arms. Before any fix, I expect the gap to sit between -0.01 and +0.01 in pleasure and somewhat higher in net wellbeing (C2 and V22-0 minus BASE-0). With the fixes, D(V22-F) in pleasure between -0.005 and +0.020. I do not expect P1 to hold robustly; P2 is likelier. I expect S1 to be closer to holding than P1, because declining and the ladder mostly spare suffering. I expect P3 to be positive (roles save effort by construction, and the ladder replaces some exits with renegotiation), P4 to be positive but small, and the not-formed share to rise under `real_outside` in every arm. Among the trust variants, I expect "words" to keep trust higher and produce fewer leaves but more lapses than "actions", with "mostly" between them and small differences in net wellbeing.

## Not testable by design

The manipulation checks M1 to M10 (pass or fail). The fine counts (M4). The slid-into flag's definition (it is a measure, not a test).

## Limits stated now

- Scripted agents. Grid personas have placeholder principles; the scripted policies use their weights and axes only.
- Every lever and fix payoff is written into the model, so "a fix raises pleasure" is partly true by construction. The informative results are the sizes, the gap, and the failures.
- One parameter point per fix; no sweeps in this run (Q11: these are sweep centers, a sweep is later work).
- The baseline's formation choice uses a 26-week rollout of the baseline cards against the outside option. It is a model of the choice, with the same horizon as the negotiation's, not the full 156 weeks.
- `contact_motive` and `fine_crowdout` are off in the headline, so the contact veto bites only where a pressing persona exists. The hand and grid cohorts have none.
- v2.3 runs with Claude's defaults on four details the author has not settled (the three jobs, skipping the ladder in severe distress, the slid-into window, bindable only); listed in the read-back.

## Amendments

### Amendment 1 (2026-11-11, committed before the confirmatory run): manipulation checks, pilot, power check, n and S

**Implementation deviations from the design** (made on smoke runs of one to four pairings at seed 0, before the pilot; listed in full in docs/results/household-fixes-design.md, "Implementation notes"): valued money changes the security need and adds a bought pleasure on spending, and leaves the money need and agent choices as they were; the take menu adds the smallest allowed take only if it keeps 25 percent of resources; a member who leaves on the bar goes to the arrangement it compared; roles are judged monthly; who proposes a fine follows each member's bundle value. No threshold or prediction was changed.

**Manipulation checks** (`scripts/v2_retest_run.py --checks`, runs/v2-retest/checks.json, tests/test_household_fixes.py):

| ID | Result | Verdict |
|---|---|---|
| M1 | Hand cohort with `contact` and `contact_motive` on, `trap` vs `contact_free`, 15 pairings x seeds 0 to 2: 32 of 45 cells differ; Partner B's (the restricted partner's) mean pleasure is lower under `trap` by 0.076. Pressing-controller cohort (`contact` on): 21 of 36 cells differ, but the restricted partner's mean pleasure differs by +0.001. Reason, checked on one pairing: the controller's vetoes already block contact in both arms (86 vs 85 blocked visits by Partner B); card T2 adds little on top. | **passes in the hand cohort; fails in the controller cohort for a non-bug reason** (the veto, not T2, does the isolating there). The contact veto now bites where someone uses the request. The retest headline has `contact_motive` off, so in the headline arms the veto still has no user, as the prereg's limits say. |
| M2 | Security weight 0 earns no security pleasure; subsistence shortfall still costs; bought pleasure has diminishing returns | passes (unit tests) |
| M3 | Fidelity P1a rerun with `real_outside` and `nash_terms` on (levers on, 15 hand pairings, seeds 0 to 4): U_A with outside option +0.15 minus baseline, among formed pairs, +0.0085 [+0.0019, +0.0155]; 28 of 75 pair-seeds formed in both conditions (8 pairings) | **fails** (below +0.02). Terms now move a little with the outside option (the interval excludes 0; the levers-off fidelity run had +0.012 [0, 0.025]), but not by the preregistered amount. As the prereg says, the retest runs anyway: terms-level claims still cannot be cited from the household. |
| M4 | Pilot: fine terms exist in 30 of 120 V22-F runs and 34 of 120 V23-F runs, every one in an agreed bundle; none in BASE-F | passes on the pilot; recounted on the confirmatory data |
| M5 | Pins (10 fingerprints, ladder pin), fixes-off tests, 6 headline cells to 1e-12 | passes |
| M6 | `BaselineLived(decline=True)` forms iff both members' baseline value exceeds their outside option (unit test); pilot: BASE-0 formed at week 0 in 40 percent of runs, BASE-0i in 100 percent | passes |
| M7 | Counted on the confirmatory data (the pilot's counter had a counting bug, fixed in dc014a1 without changing behavior) | pending |
| M8 | The three trust versions move trust by 0, 0.01 and 0.05 per word; a lapse takes the gain back | passes (unit tests) |
| M9 | A calm partner with `bar_out` set puts leave on its menu; two readings in a row are needed (unit tests). Pilot leaves on the bar: BASE-F 74, V22-F 69, V23-F 49 (120 runs each) | passes |
| M10 | Pilot: 0 partner-weeks with an all-forbidden leave menu in BASE-F, V22-F, V23-F | passes on the pilot; recounted on the confirmatory data |

**Exploratory pilot** (EXPLORATORY; not a result; changes no threshold). `--pilot`: seeds 900 to 902; the 15 hand pairings plus 25 drawn with `random.Random(900)`; arms BASE-F, V22-F, V23-F, BASE-0, V22-0, BASE-0i; 720 runs in 133 s with 4 workers. Raw: runs/v2-retest/pilot.json.gz (git-ignored).

| Quantity (pairing-level difference) | Pilot effect | Pilot sd | Seed sd per run | Pairings for 80% power at +0.010 (`seeds_for_power`, one-sided) | Closed form (`seeds_for_margin`, two-sided) |
|---|---|---|---|---|---|
| P1 V22-F - BASE-F, pleasure | +0.012 | 0.042 | 0.030 | 110 | 142 |
| P2 V23-F - BASE-F, pleasure | +0.026 | 0.054 | 0.031 | 179 | 227 |
| P3 V23-F - V22-F, pleasure | +0.013 | 0.035 | 0.031 | 74 | 96 |
| V22-0 - BASE-0, pleasure | +0.006 | 0.042 | 0.034 | 109 | 136 |
| S1 V22-F - BASE-F, net wellbeing | +0.005 | 0.087 | 0.099 | 499 | 596 |
| S2 V23-F - BASE-F, net wellbeing | +0.037 | 0.125 | 0.093 | 968 | 1230 |

Other pilot readings: share of runs formed at week 0, BASE-F 0.28, V22-F 0.41, V23-F 0.47, BASE-0 0.40, V22-0 0.52, BASE-0i 1.00. C9 in the pilot: V22-0 had 2200 partner-weeks with an all-forbidden leave menu, in 5 of 40 pairings; BASE-0 and BASE-0i none.

**n and S (fixed here).** The rule gives n = 110 for P1, raised to the floor of 120. **n is set to 180 pairings instead** (the 15 hand pairings plus 165 drawn with `random.Random(20261111)`), so that P2 (179 needed) and P3 are powered too. This raises n above the rule's value, before the run, for power only. **S = 8 seeds per pairing** (seeds 0 to 7): the rule raises S from 4 to 8 when the seed sd (0.030) is above half the between-pairing spread (0.021). Runtime estimate: 180 x 8 x 6 = 8,640 confirmatory runs at about 5 runs per second with 4 workers, about 30 minutes, plus the descriptive arms on 40 pairings (`random.Random(901)`) and the stay test (S5) on those 40 pairings.

**Marked DESCRIPTIVE before the run:** S1 and S2 (net wellbeing; 499 and 968 pairings needed). They are reported with estimate, interval and p, and keep their p in the secondary Holm family. P1 to P4, S3, S4 and S6 stay as preregistered. S5 (stay test) runs on the 40-pairing descriptive cohort only, so it is DESCRIPTIVE too.

### Draft change log

- 2026-11-11 (after the stay test): `bar_leave` and `take_menu_terms` added to "all four fixes on" (they are part of the approved fix-then-retest plan); checks M9 and M10 and descriptive line C9 (all-forbidden take menus in the fixes-off arms) added. Nothing had been run.
- 2026-11-11 (earlier): the author's "everyone counts" settled who is scored: every person at their actual outcome, living apart included, decides the verdict. The "Claude's choice" label was replaced by the author's decision; C8 stays descriptive. Nothing had been run.
- 2026-11-11 (later): the author's "show both, judge on pleasure" made mean pleasure primary again (P1, P2 pleasure only); net wellbeing and non-offsettable suffering became secondary lines that do not decide; the clause calling the condition met when the gain only spares suffering was removed; scoring people who decline was labeled Claude's choice (faithfulness review F1) and a formed-pairs-only line (C8) was added. Nothing had been run.
- 2026-11-11: after the author's v2.3 answers and retest decisions, the primary measure became net wellbeing (pleasure-only became secondary), non-offsettable suffering got its own line, every baseline arm lets pairs decline to form (BASE-0i keeps the old imposed baseline for replication only), the trust-variant arm and the general-unhappiness ladder were added. Nothing had been run.
