# Hybrid agent: design and pass tests (preregistration)

Wording rule: agents feel nothing; "pleasure", "value" and "forecast" are glosses for modeled numbers.

Status: written and committed before either pass test ran. Nothing here about the hybrid is a result. Scripted agents, no model calls. Step 2 of the step-back plan ([step-back-review.md](../notes/step-back-review.md), "Recommended plan"), confirmed by the author ("Yes, both"; experiments/readbacks.jsonl, rb-2026-11-12-stepback). Follows ADR 0019 (the saturating pleasure scale) and its value check ([pleasure-scale.md](pleasure-scale.md)).

What I knew when writing this, stated plainly: the code (`src/mar/hybrid.py` and its hooks) and its known-answer tests (`tests/test_hybrid.py`) were written and run before this commit, on unit worlds and one 30-week life. A timing probe of three lives per agent set (below) was run for the cost table. The step-1 value check of v2 on the new scale was run and read ([pleasure-scale.md](pleasure-scale.md): it fails T6 on time together, which is PT-R's reference). The free reachability check (`--reach`) was run twice on three pairings, 78 weeks, with a planted outside-option bias of +0.05. The first time, a bug put the bias into the held-out values too, so it cancelled: that run read as an unbiased audit of 36 choice-units and passed (H1 +0.003, H2 0.92, H3 8 of 8). That is the only audit-like number I saw. The bug was fixed (held-out values are scored on the neutral yardstick, `hybrid._NEUTRAL`) and the check rerun; its result is under "Can every verdict happen?". No PT-R or PT-H run was made.

**Can be about / cannot be about (required).** This can be about whether the hybrid agent's two halves agree with the hedonic model's own answers in the formation check's household: its weekly routine at one week, and its big-choice forecasts against futures it did not use. It cannot be about how people decide, whether the hybrid's choices are good for anyone, or any hypothesis: no H38 or formation-check claim is tested here (that is step 3, [formation-check-3-prereg.md](formation-check-3-prereg.md)). Limits that apply (docs/limits.md): 1 (scripted agents), 2 (small persona set), 6 (passing predictions about the builder's own equations are code checks: both pass tests are), 9, 12 and 13. Not touched: the LLM limits.

## Purpose

The step-back review found three things moving at once between v1, v2 and v2b: the weekly policy, the world (bills that hurt) and the yardstick of the big choices. It also found that every status-quo forecast saw the lived world's own future. The hybrid fixes the agent once: an accurate routine, simulated big choices on one yardstick with fresh futures, bills as an agreement, every score on one scale, and misforecasting in one named place. The pass tests say whether it does what it says before any experiment uses it.

## The switch

`FixConfig.agent_values = "hybrid"`, off by default (v1 stays the default). With any other value no hybrid code runs: the pinned fingerprints of v1, v2, v2 with bills and v2b with bills (tests/data/scale_off_fingerprints.json, commit ae80dad) must still pass, and `tests/test_hybrid.py::test_hybrid_off_is_untouched_by_the_hooks` checks that the hooks leave no trace.

## Design

**Routine weeks.** v2, unchanged: an action is worth the change it makes to this week's close in the model's own arithmetic (`agent_values.week_net`), on the scale in force. Run on the saturating scale (ADR 0019) with bills that hurt. Kept: one-week horizon, the 0.003 floor, the ±10% noise, H38's withdrawal, the variety policy.

**Big choices**, chosen by simulation (`mar.hybrid`):

| Choice | Options | When |
|---|---|---|
| Form at week 0 | the household under each bill term; each member's outside option | week 0 |
| Form later | the same, from the current state | every 13 weeks while apart |
| Stay or leave | staying; each member's outside option | every 13 weeks while both are in, and an early reading when a member is in distress (at most every `hybrid_gap` = 4 weeks) |
| Return | staying out; the member back in | every 13 weeks while one is out |
| Week-0 stay and request commitments | with; without | at the world's start (only where the cards allow them) |

- **K sampled futures per option, fresh on both sides.** Each option is played over K = 4 futures (`FixConfig.hybrid_k`). A future has a new shock schedule (job loss, illness, moves, new connections; bond shocks if on) and new random streams for every agent, drawn from a seed of (world seed, week, k). The status quo no longer deep-copies the lived world's own schedule; the outside option is K of `alone_value`'s rollouts with K seeds (it was one). Neither side sees the real future.
- **One declared yardstick.** The member's mean weekly pleasure on the scale in force: the evaluator's own measure (`hybrid.score`). Suffering does not enter it, as under the formation check's corrected rule. The window is the decision window (`decide_weeks`, 52 in the formation check).
- **Choosing.** Form iff every member's household value beats its outside option. Leave on the reading rule already in force (`bar_reading`: the outside option beats staying by more than 0.02 at two readings in a row), with leave valued at its simulated gain per week times the window, so it competes with the routine on one scale. Return iff both members gain. A commitment is made iff both members gain.

**Bills as an agreement.** At formation the household agrees who pays the month's bill: shares proportional to income (6:5, the two earners' block pay) or equal. The term is chosen with the formation choice: the household under each term is scored on the same K futures, and the term is the one whose worse-off member gains most over the outside option. At month end each member in pays its share of the bill, less what it already paid that month by action, as a standing transfer (up to its money; no action unit). It is kept like a commitment, without breach mechanics: the agents do not need to foresee settlements. The routine's one-week arithmetic includes the transfer in the settlement week. If a member leaves, the one still in pays the whole (shares over the members in).

**Fixed scores.** Request, refusing a request, veto, give and taking from the pot (the propose-only actions with fixed scores 0.06 to 0.55 under v1 and v2) are valued by a one-week simulation in the lived world: the week replayed from its start with the action forced at the same call, against idle there; own net plus the prosocial share of the partner's net. That is the value check's own known answer at one week. Leave and return are valued as above. Inside a forecast no such fork is made: forecasts assume no request, refusal, veto, gift or take. This is a declared simplification; the gap it leaves is measured by H1 on readings (a forecast without these actions against held-out futures also without them would not show it, so see "Weaknesses").

**Misforecasting.** Optional persona fields `Persona.forecast`: `horizon` (weeks the member scores), `discount` (per week), `outside_bias` (added to the outside option). Empty by default, so every member forecasts neutrally. The weekly routine has no trait.

**Not built.** Project protection (H39 makers) as a simulated choice: a makers world with negotiated protection refuses to run under the hybrid. Neither pass test nor step 3 uses makers.

**Nothing is fitted.** K = 4 and the gap of 4 weeks are the review's cost-led choices, ASSUMED. The terms (income, equal) are the author's two examples. The yardstick is the evaluator's. No number was set from an outcome.

## Pass test PT-R: the routine, one week

The value check (`scripts/value_consistency.py --hybrid --run`): H39b's M0 world as in every earlier value check, a third of H38's 120 confirmatory pairings (every third), seed 0, six sampled weeks per run, both partners, the week's last call, on the saturating scale with bills that hurt. Reference: v2 on the same pairings, seed and weeks on the same scale (the step-1 rows, `runs/value-consistency-v2-sat/`). Measures and bars are the recalibration prereg's T1 to T6 on own net.

| Clause | Bar |
|---|---|
| R1 to R4 | the hybrid's T1 (pooled rank correlation), T2 (within decision), T3 (best is the actual best), T4 (best beats next) are each no more than 0.02 below v2's on the same sample |
| R5 | T5, the slope of actual on perceived, in 0.8 to 1.25 |
| R6 | every action's mean gap within its T6 bar (max of 0.015 and a quarter of the actual) |

PT-R passes iff R1 to R6 all hold.

## Pass test PT-H: big-choice forecasts against held-out futures

Lived runs of the formation check's world under the hybrid (saturating scale, bills that hurt, the corrected rule: 52-week windows), arms G-L0 and G-L4, every third confirmatory pairing, seed 0, 156 weeks: 80 runs. Every big choice is also scored on M = 16 held-out futures (a different seed family, never used by any choice). For each choice, member and option there is a forecast F (the mean of the K = 4 futures the choice used) and a held-out value R (the mean of the 16). The unit of resampling is the pairing.

| Clause | Quantity | Bar |
|---|---|---|
| H1 calibration | mean over (choice, member) of F − R for the option chosen | within ±0.010, and its 95% bootstrap interval (clustered by pairing) inside ±0.015 |
| H2 discrimination | Spearman rank correlation of F with R over every (choice, member, option) | ≥ 0.80 |
| H3 choice agreement | among (choice, member) units whose two best options differ by at least 0.010 in R, the share where the best option by F is the best by R | ≥ 0.80 |

PT-H passes iff H1, H2 and H3 all hold.

Why these bars, stated before any audit row: a week of pleasure on this scale moves by a few hundredths across futures, so a mean of four futures carries a standard error of about 0.01 for one choice; a bias of 0.01 a week is a third of the formation check's whole L4 − L0 effect under v1, which is the size a forecast error must stay under to leave step 3 readable. The chosen option's forecast is biased upward by selection (it won on those four futures); H1 is where that shows. 0.80 is the recalibration's T1-style bar for a ranking, raised because the forecaster and the held-out futures share the same model.

**If a test fails.** The design may change only where the audit disagrees (for example K, if the selection bias is the cause), each change documented with the numbers before and after, and the test rerun on the same sample. Never against a formation-check outcome. A failure that is not fixed is reported, and step 3 then reads the hybrid arm as descriptive.

## Can every verdict happen? (required)

- **PASS** is reachable: the clauses are bars on agreement, and a forecaster that is the held-out value itself meets them (H1 = 0, H2 = 1, H3 = 1).
- **H1 can fail**: a planted outside-option bias of +0.05 on every persona (`hybrid_passtest.py --reach`, three pairings, 78 weeks, 36 choice-units): H1 +0.036 [+0.029, +0.050], **fails**; H2 0.64 and H3 0.40 fail too. Run; runs/hybrid-passtest/reach.json.
- **H2 and H3 can fail**: the same rows with forecasts shuffled across units: H2 −0.04, H3 0.55, **fail**. Run.
- **R1 to R6 can fail**: they failed for v1 (T1 0.43, T3 34%) on the old scale, and the hybrid's routine is not v2 where the bill agreement changes the settlement week.
- **The metric sees the mechanism**: the audit records every option's F and R at the point of choice (`hybrid.audit_choice`), so a forecast that drifts from the futures it claims to stand for lands in H1 directly.

## Are we measuring what we say? (required)

- **Construct card.** "Forecast" = the mean yardstick over K sampled futures of this model, with the routine playing every later week and no propose-only actions. "Held-out" = the same, over 16 other futures. PT-H checks that a K-sample choice is a faithful estimate of the model's own expectation. It does not check that the model's futures look like the lived one (the lived run is one more future, read below as a descriptive), and it does not check that the choice is wise. "Routine one week" = the value check's actual, as before.
- **Known-answer case.** `tests/test_hybrid.py`: futures differ from the lived world's schedule and are reproducible; agreed shares pay 6/11 and 5/11 of a bill of 10; the term choice maximizes the worse-off member's gain; a persona horizon, discount and outside bias change the yardstick exactly as stated; forecasts drop the propose-only actions and keep the value check's forced marker.
- **One other way to measure it.** For readings where both stayed, the lived 13 weeks that followed against the stay forecast's first 13 weeks is reported as a descriptive (one lived future per choice, so noisy).
- **Story spot-check.** Not applicable to an instrument check; the step-3 prereg carries one.

## Verdict rule

These are instrument checks, not hypothesis tests: they say PASS or FAIL, and nothing about pleasure or freedom. The evaluator's rule (pleasure and freedom, "trade-off" when they part) applies to step 3. The hybrid enters step 3 as a confirmatory arm only if both pass tests pass.

## Cost

Timing probe (one process, pairings p-anchor/p-host, g-00000/g-11111, g-01010/p-wanderer, seed 0, G-L4 with the stay lens on, 156 weeks, the corrected rule, saturating scale, bills that hurt, unaudited):

| Agent set | Seconds per run (mean of 3) | Weeks together in these three |
|---|---|---|
| v1 | 2.0 | 1.00, 1.00, 1.00 |
| v2 | 3.0 | 0.33, 0.25, 0.75 |
| v2b | 4.5 | 1.00, 0.42, 1.00 |
| hybrid | **20.4** | 1.00, 1.00, 1.00 |

A hybrid run played 96 futures of 52 weeks (4,992 simulated weeks: 8 at week 0, then 8 per reading, the stay lens and the reading sharing the status quo) and made no fork (no propose-only action came up in the baseline world). About 7x v2b. PT-H's audit adds 16 held-out futures to every choice, so its runs cost several times more; PT-R costs about what v2's check costs per run.

## Limits stated now

Scripted agents; the H38 persona sample; one parameter point; K = 4 is small; the yardstick ignores suffering by declaration; forecasts omit the propose-only actions; the bill agreement has no breach and no renegotiation yet; project protection is not built.

## Weaknesses

- PT-H compares the model with itself. A forecast that is wrong in the same way in every future (for example, because forecasts omit requests and refusals that the lived run has) passes PT-H. The lived descriptive is the only check on that, and it is noisy.
- The term choice and the formation choice share the same four futures, so the chosen term's value carries a little selection bias into H1. That is part of what H1 measures.

## Amendments

**Amendment 1 (2026-11-12, after PT-R's first run, before any step-3 run).** PT-R failed as preregistered: T1 0.934, T2 0.958, T3 92.1%, T4 92.7% against v2's 0.973, 0.987, 96.5%, 96.9% on the same sample (each more than 0.02 below). Cause: in the settlement week, the partner's projection of a bill payment (`agent_values._paid`, used for the prosocial share) added the payment to the month's funding but still expected the payer's full agreed share on top, while the world counts the payment toward that share. Paying looked worth up to +0.38 to the partner's side when it was worth 0. Fix: the partner's projection counts the payment toward the payer's share (one line), with a known-answer test that fails without it. Rerun on the same sample: T1 0.958, T2 0.974, T3 94.7%, T4 95.6%, T5 1.09, T6 holds: PASS. This changed the design only where the check disagreed (a projection error, not a parameter), as "If a test fails" allows; no bar moved. PT-H had already run on the code before the fix (PASS); because the fix changes the routine that plays every forecast's later weeks, a smaller PT-H rerun (G-L0, every sixth pairing, seed 0; `hybrid_passtest.py --a1`) is added and reported beside the main run. The main PT-H result stands as run.

**Amendment 2 (2026-11-12, written before the change; before any step-3 run). Time together valued at the world's satiety.** The author chose "Fix the time-together error first, then run" (experiments/changes.jsonl, 2026-11-13T03:38:14Z). The error: the routine (v2's arithmetic, so v2, v2b and the hybrid alike) values one more session of time together at a full session unless the persona's variety policy is "adaptive", while the world plays every session at its satiety scale. On the saturating scale it is the one clause the value check fails (+0.023 perceived against +0.006 actual; [pleasure-scale.md](pleasure-scale.md)), and the clause that costs PT-R most (58 rows, rank correlation 0.03).

- **Was the old rule deliberate?** Yes. ADR 0016 made the variety policy a persona trait ('adaptive' personas foresee satiety; 'repeat' and 'rotate' do not), and the recalibration prereg kept it "on purpose" ("Kept as they are": only an adaptive persona expects a satiated source to pay less). So it is a chosen misforecast, not a coding slip. It was harmless on the cap, where both numbers read 1.0.
- **Why change it for step 3 anyway.** The hybrid's own design puts every misforecast in one named place (`Persona.forecast`) and says "the weekly routine has no trait". This trait is a misforecast inside the routine, so it contradicts the hybrid's design, and it moves v2 and v2b on the new scale (a session priced at four times its worth). Even the adaptive persona's expectation is not the world's: it reads its own best variant and no switch cost, while the world uses the host's pick (the partner whose week it is) and charges the switch.
- **The change, behind a flag.** `FixConfig.satiety_expect`: `"persona"` (the default: the old rule, exactly) or `"world"`. Under `"world"`, every v2, v2b and hybrid agent values one more session at the scale the world would give the next session this week: the host's variant (`_pick_variant`), its satiety and tolerance, and the switch cost (`Satiety.use`'s own arithmetic, read without changing anything). The same number goes into the partner's projection, since the session is shared. It is a mirror of the world's arithmetic; no number is chosen. v1 keeps its own heuristics and does not read the flag. Seeing a friend is left as it is: its clause holds (gap +0.001), and an adaptive persona's friend scale is already the world's own; a non-adaptive persona's friend misforecast stays a persona trait. The makers' week planner reads the same helper, so a makers run with the flag on would be consistent (no makers run uses it).
- **Old results reproduce with the flag off.** Fingerprints pinned at commit b3e9fc0, before the change: tests/data/satiety_off_fingerprints.json (v1, v2 with bills, v2b with bills and the hybrid with bills, all on the saturating scale; the formation check's G-L0 and G-L4, the value check's decision record, and H39b's arms except under the hybrid). The clipped-scale pins (scale_off_fingerprints.json) must still pass too.
- **Pass test (bars unchanged).** (a) The value check on the saturating scale, v2 with bills, the full sample (`value_consistency.py --v2sat --world --run`; rows in runs/value-consistency-v2-sat-world/): T1 to T6 at the recalibration's bars. (b) PT-R for the hybrid (`--hybrid --world --run`; runs/value-consistency-hybrid-world/): R1 to R6 against v2 with the same flag on the same pairings, seed and weeks (the reference moves because both share the routine), and also shown against the old v2 rows; the hybrid's own T1 to T6 at the recalibration's absolute bars. Both must pass every clause. Before and after numbers are reported side by side. (c) Added: a small PT-H rerun on Amendment 1's sample with the flag on (`hybrid_passtest.py --a2`), reported beside, because the routine plays every forecast's later weeks.
- **If it fails.** As before: the mapping may change only where it disagrees with the model's arithmetic, documented with numbers before and after, never against a step-3 outcome. A failure not fixed is reported, and step 3 then reads the routine as it is.

**Amendment 3 (2026-11-13, written before the change; before any H41 run). The suffering weight in big choices, and readings run by the world.** The author answered "1" to "give the hybrid each person's suffering weight, then run H41" (experiments/changes.jsonl, 2026-11-13T13:38:43Z). Two changes, each behind its own flag, both off by default.

- **(a) The suffering weight, `FixConfig.hybrid_w`.** `None` (the default) keeps the yardstick as declared above: mean weekly pleasure. `"persona"` makes it mean weekly pleasure − w × suffering (both kinds, `s_off + s_non`), on the scale in force, with w the persona's own weight: w = exp(z), z ~ N(0, 0.6), clipped to [0, 4], drawn from the persona id. That is H39's weighted rule and its draw (`makers.suffering_weight`, [decision-weights-research.md](../notes/decision-weights-research.md)), reused, not rewritten. A number (0.0 or 1.0) gives every persona that weight: the two sensitivity arms the author named. The weight is the persona's taste, not a misforecast, so the held-out audit scores with it too; the persona forecast traits (horizon, discount, outside bias) stay off in held-out values as before. It applies wherever the yardstick does: forming, retries, readings, returns, the week-0 commitments and the outside option. w = 0 gives the same numbers as the flag off (a test checks this). Why: in the formation check's third run, members held by pressure had about three times the suffering in the next 13 weeks (0.24 against 0.09), and one stayed through about 100 weeks of non-offsettable suffering of 0.5, because the yardstick could not see it.
- **(b) Readings run by the world, `FixConfig.hybrid_readings`.** `"harness"` (the default) is today's rule. `"world"`: at the start of each week of a lived world, the world itself runs whatever hybrid reading no harness ran. (1) An early reading on distress: the existing trigger (4 low weeks, non-offsettable load at least 0.2, or trust below the leave line), at most every `hybrid_gap` weeks. (2) In a world no harness drives (`world.harness` unset): the 13-week reading while both are in, and the return reading while one is out. The arithmetic is the harness's own (`BaselineLived.reading`, `hybrid.return_reading`): the status quo over K futures minus the trust penalty, the outside option at the carry, exit anticipation, and the bar rule (two readings in a row beyond the margin). It runs in lived worlds only, never inside a forecast or a one-week fork, so forecasts still assume no leaving (declared above).
  - **What the formation check actually showed, stated precisely.** The harness already ran early readings on distress (`BaselineLived.hybrid_week`, in the design table above). The stay test's trap fixture has no harness, so the hybrid there ran no reading at all, and it never left. Under a harness (every formation-check and H41 run), (b) changes nothing; a test checks that.
- **Pass tests (written now; bars not moved later).**
  - **K1, the trap's known answer.** The stay test's trap and baseline fixtures under the hybrid, the 12 control pairings and seed 900 of the formation check's reach check (`formation_check_3.reach_trap`), step-3 world, with both flags on. Passes iff the held share is at least 0.10 in the trap and at most 0.02 in the baseline. Before (formation-check-3 reach, both flags off): 0 and 0. Each flag alone is reported too, descriptively, to show which part separates it.
  - **PT-H on the new yardstick.** Amendment 1's sample (G-L0, every sixth pairing, seed 0), the step-3 world, `hybrid_w="persona"`, `hybrid_readings="world"` (`hybrid_passtest.py --a3`). Bars unchanged: H1 within ±0.010 with its interval inside ±0.015, H2 ≥ 0.80, H3 ≥ 0.80.
  - **PT-R unchanged.** Neither flag is read by the weekly routine (no line of `agent_values` changes). Rerun anyway with both flags on (`value_consistency.py --hybrid --world --a3`), because the lives change when formation and leaving change: R1 to R6 against v2 with the same satiety flag on the same pairings, seed and weeks (Amendment 2's reference rows), bars unchanged.
  - **KW, a known answer for w.** A household that gives a member 0.02 a week more pleasure than its outside option and 0.10 a week more suffering: with w = 2 the member declines (0.02 − 2 × 0.10 < 0); with w = 0 it forms. Checked on the yardstick and the formation choice (`hybrid.score`, `hybrid.choose_term`), and under `"persona"` with a persona whose drawn w is high.
  - **Old results reproduce.** With both flags at their defaults, fingerprints pinned at commit 660a34d before the change (tests/data/h41_off_fingerprints.json: the formation check's arms under all four agent sets in the step-3 world, and the trap and baseline fixtures under the hybrid) reproduce byte for byte, and so do the earlier pins.
- **Expected, written before:** the research note expects a median weight of 1 to form about as few pairs as the old net rule (51% in the first formation check, against 84% on pleasure). So the hybrid's G-L0 formation (0.91 in step 3) should fall. That is a consequence, not a bar.
- **Findings this could move (ADR 0020).** Rows 52 and 53 of the results index (the hybrid's pass tests and its column in the third formation check). They ran with both flags off and stand as run; nothing is rerun under this amendment except the pass tests above. The limits note on the hybrid's yardstick (docs/limits.md, update 2026-11-13).
- **If a test fails.** As before: the design may change only where the test disagrees, with numbers before and after, never against an H41 outcome. A failure not fixed is reported, and H41 then reads the hybrid as it is.
