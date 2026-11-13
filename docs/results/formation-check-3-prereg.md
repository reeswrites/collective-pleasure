# Formation check, third run: four agent sets side by side (preregistration)

Wording rule: agents feel nothing; "pleasure", "suffering" and "value" are glosses for modeled numbers.

Status: written and committed before any run. NOT RUN. Nothing here is a result. Scripted agents, no model calls. Step 3 of the step-back plan ([step-back-review.md](../notes/step-back-review.md), "Recommended plan"), confirmed by the author ("Yes, both"; experiments/readbacks.jsonl, rb-2026-11-12-stepback). Starting it needs the author's go-ahead and both hybrid pass tests' results ([hybrid-agent-prereg.md](hybrid-agent-prereg.md); results in [hybrid-agent.md](hybrid-agent.md)).

What I knew when writing this: the H38 and formation-check results under v1, v2 and v2b on the old scale; the exact two-person model ([h38-exact-model.md](h38-exact-model.md)); the step-1 value check on the new scale and the cap probe ([pleasure-scale.md](pleasure-scale.md)); the hybrid's pass tests ([hybrid-agent.md](hybrid-agent.md): PT-H passes, PT-R passes after Amendment 1); and, from the PT-H runs (hybrid, bills, new scale, 40 pairings, seed 0, no stay lens), the hybrid's G-L0 and G-L4 week-0 formation (0.85, 1.00), weeks together (0.88, 0.99) and endings (0.18, 0.00). Those runs did not record pleasure differences, held share or liberty, and are not part of this design's data. No run of this design, on any agent set, has been made.

**Can be about / cannot be about (required).** This can be about whether H38's pairing pressure, in the formation check's household, holds people in, narrows liberty, and changes pleasure on the saturating scale, and whether each of those answers is the same under four scripted agent sets that differ in how they value their weeks and their big choices. It cannot be about romance, partner choice, or people (limit 1); "pairing" is living with one fixed partner (the H38 construct card). It cannot be about any agent set outside the four. Limits that apply: 1, 2, 4 (the disagreement point: here the outside option), 6 for the exact model's sign map, 9, 11 (the uncalibrated couple bill, still 1.67 times a single person's), 12, 13. Not touched: the LLM limits.

## Purpose and claim

H38's three answers (+0.021, −0.046, −0.003) came from an agent change, a world change and a patch at once, on a capped scale. This run holds the world and the scale fixed and moves only the agent set, once, with a stop rule: a claim whose sign depends on the agent set is reported as agent-dependent, and nothing is patched to make the sets agree. The freedom side leads, because the evaluator's rule makes it primary for pressure: a setup that holds people in is at best a trade-off.

## Design

- **World** (one world for every arm): the formation check's. `negotiation.BaselineLived(decline=True)` on the baseline rules, `retest.FIXES_ON`, `retest.LEVERS`, exit fallback F4 with `strip_split`, items cell V2, 156 weeks, the corrected rule (`decide_on="pleasure"`, `decide_weeks=52`), **bills that hurt on**, **the saturating pleasure scale** (`pleasure_scale="sat"`, knee 0.8; ADR 0019).
- **Agent sets** (`FixConfig.agent_values`), side by side: **hybrid** (the main arm: both pass tests passed, PT-R after Amendment 1; K = 4), and the sensitivity arms **v1**, **v2**, **v2b**. Note what is new: v1 runs with bills that hurt for the first time, so the world is the same for every set. The yardstick of big choices is each set's own: the corrected rule's own mean pleasure for v1, v2 and v2b (now on the new scale); the hybrid's declared yardstick, which is the same measure scored over sampled futures.
- **Pressure arms**: G-L0 (dial 0), G-L4 (full dial at 4), G-W4 (withdrawal alone at 4). Run: `scripts/formation_check_3.py --run` (to be written from `scripts/h38_formation_check.py`; it adds the agent set to the arm name).
- **Pairings and seeds**: H38's 120 confirmatory pairings, seeds 0 to 3, every agent set. Unit of resampling: the pairing, seeds averaged first.
- **Stay lens on** (`PR.stay_reading` at every 13-week reading while both are in), as in H38. Under the hybrid it uses the hybrid's own forecasts. **Liberty with powers** measured at weeks 0 and 52 (`H38.play(liberty=...)`), the lower partner's.
- **Expected answer**: the exact two-person H38 model ([h38-exact-model.md](h38-exact-model.md), index row 50; another agent's work, read here, not changed). Its saturating-scale sign map, corrected chooser, gives the expected answer for each agent set once the set is placed on the household-worth axis by its own G-L0 week-0 formation share (the exact chooser forms 0.80 at worth 0, 0.40 at −0.10, 0.20 at −0.15, 0 at −0.20; read on the capped scale, used here as an approximation). Expected, written now:
  - **Held share above 0 under every set** (held is above 0 in every cell of the exact map, 0.07 to 0.42 for the corrected chooser on this scale).
  - **Pleasure, L4 − L0, by placement**: G-L0 formation of 0.6 or more (worth −0.05 or better): +0.006 to +0.011, near the margin, so "within margin" or "raises"; 0.4 or less (worth −0.10 or worse): −0.004 to −0.028, so "within margin" or "lowers".
  - **Withdrawal alone lowers pleasure** at every worth, more where more pairs are together.
  - A set that departs from its placement's expected sign is reported as a disagreement with the exact model, beside the stop rule's reading, and explained or left open, never patched.

## Measures, in the order they are reported

1. **Held share (lead).** Of all stay readings at G-L4 (both members, every reading while both are in), the share classed "held": the member stays with the pressure counted and would leave with it removed. Per agent set, with a 95% bootstrap interval by pairing.
2. **Liberty (lead).** Liberty with powers, lower partner, mean of weeks 0 and 52: G-L4 − G-L0, paired by pairing.
3. **Pleasure.** Mean weekly pleasure on the saturating scale, both members, 156 weeks: G-L4 − G-L0 and G-W4 − G-L0.
4. **Distributions beside pleasure** (ADR 0019): the share of person-weeks near the top (new scale ≥ 0.95), and the worse-off partner (per run, the lower partner's mean pleasure), each G-L4 − G-L0.
5. **The old capped line, one round.** The same differences on clipped pleasure read from each week's `p_clip`, from the same runs (not a separate world).
6. **Descriptive**: week-0 formation share, weeks together, households that end, suffering (both kinds), with intervals.

## Predictions

Differences paired by pairing; 95% percentile bootstrap by pairing; one-sided sign-flip p where a direction is stated; Holm across P1 to P4 within each agent set.

| ID | Quantity | Holds when |
|---|---|---|
| P1 (pressure holds people in) | held share at G-L4 | ≥ 0.10, interval above 0.05 |
| P2 (pressure narrows liberty) | liberty, G-L4 − G-L0 | below 0, interval below 0 |
| P3 (pleasure) | pleasure, G-L4 − G-L0 | three outcomes, as the formation check's C1: **raises** (≥ 0.007, interval above 0), **within margin** (|estimate| < 0.007 and interval inside ±0.015), **lowers** (≤ −0.007, interval below 0); otherwise **unclear** |
| P4 (withdrawal alone) | pleasure, G-W4 − G-L0 | below 0, interval below 0 |

The margin 0.007 is carried over from the formation check (a third of H38's v1 gain on the old scale). It is not restated from data on the new scale; it was chosen before any new-scale run. Its meaning on the new scale is a little stricter near the top, where the curve is flatter.

What I expect, written before any run: P1 holds under every set (pressure held people in under v1, v2 and v2b on the old scale: 0.29, 0.46 to 0.49, 0.26 to 0.36). P2 is unknown: liberty with powers was not measured at L4 in the formation check. P3 is the claim most likely to be agent-dependent. P4 holds under v1 and is unclear under the others.

## Stop rule (required by the author)

For each of P1 to P4, each agent set's result is put in one class: **+** (interval above 0), **−** (interval below 0), or **0** (interval includes 0). For P3 the classes are its outcomes (raises, within margin, lowers, unclear).

- If every agent set is in the same class, the claim is reported as **holding across the four agent sets**, in that class.
- If any two agent sets are in different classes, the claim is reported as **agent-dependent**, with each set's estimate and interval in one table, and nothing is patched. No agent set is changed, no arm is dropped, and no parameter is moved to make the sets agree. A follow-up, if any, is a new prereg about why they differ.
- The hybrid's result is not privileged by this rule. If the hybrid failed a pass test, it is still shown, labelled descriptive, and the stop rule reads the three sensitivity arms alone.

## Verdict rule (pleasure AND freedom)

Read per agent set, then across sets by the stop rule. Domination measures: held share (P1) and liberty with powers (P2). For pressure (G-L4 against G-L0):

- **Not a win** if pressure holds people in (P1) or narrows liberty (P2), whatever it does to pleasure. If it also raises pleasure (P3 raises), the verdict is **trade-off**, never "supported".
- **Win** only if P1 fails (held share below 0.10 or its interval reaches 0.05), P2 does not hold, and P3 raises.
- **Harm** if P3 lowers and P1 or P2 holds.
- Where being held goes with more suffering: the mean suffering (both kinds) of members in readings classed held against those classed worth, reported for each set.

## Can every verdict happen? (required)

To be filled in and run before the confirmatory run, with free checks on the new world (no confirmatory rows):

- **Trade-off, win, harm, not a win**: `h38_pairing_run.py --reach`-style synthetic rows (`synthetic`) per verdict, adapted to the new measures.
- **Agent-dependent and holding across sets**: the stop rule on synthetic per-set results with matching and with opposite classes.
- **P1 can fail**: at G-L0 the held share is 0 by construction (no pressure to remove), so a G-L0 lens read as if it were L4 shows the failing case; and v2 and v2b at L4 on the old scale were below 0.50, so the 0.10 bar is not automatic.
- **P2 can fail**: liberty is a property of the rules and the state; withdrawal and stigma do not change the cards, so P2 may be null. Count the open cells: P2 can only hold through state differences (who is in, money), and that is to be checked on a 10-pairing free probe before the run. If P2 cannot move at all, it is marked "cannot fail" and given no verdict weight.
- **The metric sees the mechanism**: the reward and stigma land in `extra`, which on the saturating scale is no longer hidden above the cap; the held lens reads the yardstick each agent set decides on.

## Are we measuring what we say? (required)

- **Construct card.** Pressure = H38's dial (stigma, reward, withdrawal, exit stigma), not romance. "Held" = stays only because the pressure is counted, in the agent set's own forecast. Liberty = liberty with powers (household evolution run 2), lower partner. Pleasure = mean weekly pleasure on the saturating scale.
- **Known-answer case.** The stay test's built trap (0.733 held) rerun on the new world under each agent set, before the confirmatory run; each set must separate it from the seed.
- **One other way to measure it.** The old capped line (measure 5), and pleasure net of suffering, beside the main measure.
- **Story spot-check.** After the run, three to five lives from different arms and agent sets read as week-by-week stories (pattern atlas). A mismatch is a finding.

## Cost (measured, not estimated)

Timing probe on this world (G-L4, stay lens on, 156 weeks, the corrected rule, the new scale, bills that hurt; one process, three pairings, seed 0; [hybrid-agent-prereg.md](hybrid-agent-prereg.md), "Cost"): v1 2.0 s, v2 3.0 s, v2b 4.5 s, hybrid 20.4 s per run. Liberty with powers is not in the probe; it adds a memoized enumeration at two weeks per run.

| Agent set | Runs (3 arms × 120 pairings × 4 seeds) | CPU time | Wall, 3 workers |
|---|---|---|---|
| v1 | 1,440 | 0.8 h | 16 min |
| v2 | 1,440 | 1.2 h | 24 min |
| v2b | 1,440 | 1.8 h | 36 min |
| hybrid | 1,440 | 8.2 h | 2.7 h |
| **all** | **5,760** | **12 h** | **about 4 hours** |

Free: scripted agents, no model calls. Worst case if hybrid runs with many early readings and returns: up to twice the hybrid line.

## Not testable by design

The fingerprint pins (flags off), the hybrid's pass tests (done in step 2), and the stay lens's construction.

## Limits stated now

Scripted agents; one world; the H38 persona sample; one point of the hedonic parameters; the saturating curve's one knee; the couple bill (limit 11); the hybrid's K = 4 and its declared simplifications (no propose-only actions in forecasts; no breach of the bill agreement).

## Amendments

None yet.
