# H41: choice aids against pairing pressure

Wording rule: agents feel nothing; "pleasure", "suffering" and "held" are glosses for modeled numbers.

Model: `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world`, exit fallback F4 with items, corrected rule (ADR 0020). Label: **single-version** (run on the hybrid only).

**Note 2026-11-13, later.** Rerun on the hybrid with both fixes this doc asked for (`hybrid_lone`, `hybrid_exit`): [hybrid-exit-option.md](hybrid-exit-option.md). H41 is still not supported. Holds across both versions: pressure raises weeks together and holds people in; LAT and all aids lower weeks together and raise liberty; cheap solo housing never bites. Version-dependent (not patched): all aids is now harm (pleasure −0.0031), the trial lowers week-0 formation against a B that now forms more, the trial raises and the prenup lowers liberty, and better information raises weeks together (+0.019; better than matched pressure, no pleasure gain). The label of this finding is now two-version, as above. Nothing below is changed.

Status: run on 2026-11-13, after the preregistration ([h41-choice-aids-prereg.md](h41-choice-aids-prereg.md), commit 07b7c6a) and the hybrid's Amendment 3 ([hybrid-agent.md](hybrid-agent.md)). Scripted agents, no model calls, every number ASSUMED. 1,320 runs (11 arms × 120 pairings × seed 0), 11,985 s on 4 workers, kept awake with `caffeinate -i`. Rows in runs/h41-choice-aids/.

## In one paragraph

**H41 is not supported. No choice aid raised the share of weeks pairs live together, so none could fix under-commitment, better than pressure or at all.** Pressure did raise it (+0.035 at P1, +0.062 at P4), and it held people in to do so (held share 0.06 to 0.09) while narrowing liberty. The aids split three ways. The **trial, the prenup and better information** changed almost nothing: weeks together moved by +0.003, 0.000 and +0.002, and pleasure by under 0.001. **Cheaper solo housing** changed nothing at all: every one of its 120 runs is identical to the same pairing without it, because the extra cost of living alone never applied (members who live apart live with Friend C). **Living apart together** did the most, in the other direction: 40% of pairs chose it at week 0, weeks in a household fell by 0.135, liberty rose by 0.235, and pleasure fell by 0.0014. That is freedom bought with a little pleasure, chosen by agents who weigh suffering. The exact model predicted most of this before the run: an agent whose forecasts assume no leaving cannot value a cheap or safe exit, so exit-side aids cannot make it commit. The hybrid is that agent.

## The table per arm

Means over the 120 pairings. "Weeks together" is the share of weeks both partners live in the household. Held is pooled over stay readings. Liberty is the lower partner's, with powers. Pleasure is on the saturating scale.

| Arm | Weeks together | Formed at week 0 | Held (H38 lens) | Held (wide lens) | Liberty | Pleasure | Lived | Non-offsettable suffering | Worse-off partner | Near the top | LAT weeks | Seconds a run |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B (no pressure) | 0.841 | 0.75 | 0 | 0 | 2.094 | 0.9624 | 0.9624 | 0.0023 | 0.9570 | 0.816 | 0 | 20 |
| P0.5 | 0.863 | 0.78 | 0.027 | 0.027 | 2.074 | 0.9637 | 0.9629 | 0.0012 | 0.9588 | 0.827 | 0 | 31 |
| P1 | 0.876 | 0.82 | 0.058 | 0.058 | 2.014 | 0.9649 | 0.9633 | 0.0011 | 0.9605 | 0.838 | 0 | 31 |
| P2 | 0.901 | 0.87 | 0.084 | 0.084 | 1.968 | 0.9670 | 0.9634 | 0.0016 | 0.9619 | 0.869 | 0 | 39 |
| P4 | 0.903 | 0.89 | 0.092 | 0.092 | 1.976 | 0.9687 | 0.9622 | 0.0025 | 0.9642 | 0.882 | 0 | 40 |
| trial | 0.844 | 0.74 | 0 | 0 | 2.073 | 0.9633 | 0.9633 | 0.0041 | 0.9580 | 0.843 | 0 | 16 |
| cheap | 0.841 | 0.75 | 0 | 0 | 2.094 | 0.9624 | 0.9624 | 0.0023 | 0.9570 | 0.816 | 0 | 25 |
| prenup | 0.841 | 0.75 | 0 | 0.001 | 2.095 | 0.9622 | 0.9622 | 0.0025 | 0.9568 | 0.815 | 0 | 32 |
| info | 0.843 | 0.77 | 0 | 0 | 2.085 | 0.9622 | 0.9622 | 0.0039 | 0.9568 | 0.815 | 0 | 72 |
| lat | 0.706 | 0.58 | 0 | 0 | 2.330 | 0.9610 | 0.9610 | 0.0027 | 0.9559 | 0.790 | 0.149 | 22 |
| all | 0.606 | 0.51 | 0 | 0.002 | 2.429 | 0.9597 | 0.9597 | 0.0054 | 0.9545 | 0.776 | 0.253 | 71 |

## Each arm against no pressure

Differences from B, 95% pairing bootstrap. "+" and "−" as preregistered (formation: above 0.01 with the interval above 0; pleasure: above 0.003 with the interval above 0).

| Arm | Weeks together | Held (H38 lens) | Liberty | Pleasure | Lived | Non-offsettable suffering | Worse-off |
|---|---|---|---|---|---|---|---|
| P0.5 | **+0.022** [+0.006, +0.040] | **+0.027** [+0.018, +0.038] | −0.020 [−0.079, +0.033] | +0.0013 [+0.0005, +0.0024] | +0.0005 [−0.0003, +0.0016] | −0.0010 | +0.0017 |
| P1 | **+0.035** [+0.012, +0.058] | **+0.058** [+0.043, +0.073] | **−0.081** [−0.143, −0.027] | +0.0026 [+0.0011, +0.0040] | +0.0009 [−0.0005, +0.0023] | −0.0011 | +0.0034 |
| P2 | **+0.060** [+0.036, +0.088] | **+0.084** [+0.064, +0.106] | **−0.127** [−0.192, −0.066] | **+0.0046** [+0.0023, +0.0068] | +0.0010 [−0.0010, +0.0031] | −0.0007 | +0.0049 |
| P4 | **+0.062** [+0.031, +0.095] | **+0.092** [+0.067, +0.116] | **−0.119** [−0.208, −0.043] | **+0.0063** [+0.0033, +0.0093] | −0.0002 [−0.0021, +0.0018] | +0.0002 | +0.0071 |
| trial | +0.003 [−0.023, +0.029] | 0 | −0.021 [−0.077, +0.032] | +0.0009 [−0.0003, +0.0021] | +0.0009 | +0.0018 [−0.0001, +0.0042] | +0.0010 |
| cheap | 0 (identical in every run) | 0 | 0 | 0 | 0 | 0 | 0 |
| prenup | 0.000 [−0.003, +0.003] | 0 (wide +0.001) | +0.000 | −0.0001 [−0.0003, −0.0000] | −0.0001 | +0.0002 | −0.0002 |
| info | +0.002 [−0.015, +0.017] | 0 | −0.009 [−0.059, +0.046] | −0.0002 [−0.0009, +0.0005] | −0.0002 | +0.0016 [−0.0005, +0.0045] | −0.0003 |
| lat | **−0.135** [−0.188, −0.089] | 0 | **+0.235** [+0.159, +0.319] | −0.0014 [−0.0024, −0.0006] | −0.0014 | +0.0005 | −0.0011 |
| all | **−0.236** [−0.302, −0.176] | 0 (wide +0.002) | **+0.335** [+0.232, +0.444] | −0.0026 [−0.0041, −0.0013] | −0.0026 | **+0.0031** [+0.0009, +0.0060] | −0.0025 [−0.0045, −0.0007] |

Formation-gain tests (one-sided sign-flip by pairing, Holm across the six aids): every adjusted p is 1.0; unadjusted, trial 0.42, info 0.42, prenup 0.59, cheap, LAT and all 1.0.

## Verdicts

| Aid | Formation gain | Against no pressure | Against matched pressure | H41 |
|---|---|---|---|---|
| trial | 0 | no gain | no match (matched in 61% of resamples, near P0.13) | not supported |
| cheap | 0 | no gain | not better (matched at B itself: held 0 against 0) | not supported |
| prenup | 0 | no gain | no match (58%) | not supported |
| info | 0 | no gain | no match (57%) | not supported |
| lat | − | no gain (pleasure −0.0014 within the margin; liberty +0.235) | no match (below no pressure) | not supported |
| all | − | no gain (pleasure −0.0026; liberty +0.335) | no match (below no pressure) | not supported |

**H41 overall: not supported.** The all-aids arm lowers weeks together.

Read against the evaluator's rule rather than H41's verdict function, LAT and all-aids raise freedom (liberty) and cost a little pleasure: a **trade-off**, the opposite way round from pressure. Pressure under the same rule: P0.5 and P1 raise pleasure by less than the margin and hold people in; P2 and P4 raise pleasure (+0.005, +0.006) and hold people in: **trade-off**. Almost all of pressure's gain is the reward being paid: lived pleasure moves by −0.0002 to +0.0010, none distinguishable from 0.

**Aid against matched pressure, where a match exists.** The trial, matched to about P0.13: held −0.004 [−0.046, −0.001], pleasure +0.0007 [−0.0006, +0.0013], lived +0.0008 [+0.0001, +0.0017], non-offsettable suffering +0.0019 [+0.0002, +0.0051], liberty −0.019 [−0.066, +0.042]. So against the pressure that would give it the same (tiny) formation, the trial holds fewer people and lives slightly better, but carries slightly more non-offsettable suffering. With a match in only 61% of resamples, this is descriptive.

## Expectations written before the run

| ID | Expected | Actual | |
|---|---|---|---|
| E1 | Pressure raises weeks together and holds people in | P1 +0.035, held 0.058; P4 +0.062, held 0.092 | holds |
| E2 | Cheap and prenup do not raise weeks together | 0 (identical) and 0.000 | holds |
| E3 | The trial raises weeks together and is the one aid that can be supported | +0.003 [−0.023, +0.029] | **misses** (the pilot's +0.05 on 10 pairings did not replicate) |
| E4 | LAT lowers household weeks together and raises liberty | −0.135; +0.235 | holds |
| E5 | Better information reads 0 | +0.002; pleasure −0.0002 | holds |
| E6 | All aids together lower weeks together; H41 not supported | −0.236; not supported | holds |
| E7 | Pressure's total gain exceeds its lived gain | P2 +0.0046 against +0.0010; P4 +0.0063 against −0.0002 | holds |

## Reading it

**There was little under-commitment to fix.** Without pressure, 75% of pairs form at week 0 and 84% of all weeks are lived together; 8% of households end. Pressure at its strongest adds 6 points of weeks together, and its curve is flat from P2 to P4. The suffering weight did lower formation here (step 3's hybrid, without it, formed 91% at week 0), but it left a world where most pairs who can live together already do.

**Exit-side aids cannot work through this agent.** The H41 claim ends: "freedom to leave makes people more willing to commit." For that, an agent has to foresee leaving when it decides to stay or form. The hybrid's forecasts play futures in which nobody leaves (declared in its prereg). So a cheaper or safer exit cannot change what it expects from forming, and it did not. The exact model shows the same split in closed form: removing an exit cost raises time together for the planner (+0.033 at worth 0) and not for a rollout chooser (−0.006).

**The trial does what a trial does, without changing totals.** In 117 trials, a member left at the end of 31 (26%). Mostly that is a short stop, not an end: in the first story below, the leaver returns at the next 13-week reading and the pair lives together for the rest of the run. So exits rise (households that ended 0.175 against 0.083) while weeks together stay put.

**LAT is the aid people take, and it is a trade.** 48 of 120 pairs chose living apart together at week 0 (story 2 re-chose it at all eleven retries). Their pleasure falls a little (−0.0014) and their liberty rises a lot (+0.235). Agents who weigh suffering give up a little pleasure to avoid the household's bills and frictions. The evaluator counts pleasure, not suffering, so it reads this as a loss on the pleasure side. Some pairs that would form and stay a full household under B chose LAT for all 156 weeks.

**Cheap solo housing is a null by construction of this world.** The extra cost of living alone applies only to someone apart and not with Friend C. In all 120 runs the arm is identical to B, so that cost never applied to anyone. The prereg's pilot showed this; the arm was kept as preregistered.

**The prenup always chose equal split.** Every week-0 choice picked an equal split (with whichever bill term), never forfeit or proportional. Forfeit costs autonomy every week through the freedom probe, and proportional changes little when two earners put in about the same. With few exits and equal splits, nothing moved.

**Being held still goes with more suffering, less than before.** Pooled over the pressure arms, members in readings classed held had suffering of 0.103 in the next 13 weeks, against 0.068 for readings classed worth (ratio 1.5; step 3, without the weight: 0.24 against 0.09, ratio 2.7).

## Against the exact model

The exact side model (`src/mar/h41_exact.py`, written and run before the confirmatory run; tables in the prereg) places the hybrid between household worth −0.05 and 0 for the corrected chooser (exact formed at week 0: 0.6 and 0.8; simulation 0.75).

| Prediction (rollout chooser) | Exact | Simulated | Agree? |
|---|---|---|---|
| Removing an exit cost: weeks together | −0.006 (planner +0.033) | cheap 0, prenup 0.000 | yes (as a rollout chooser) |
| Cheaper solo housing lowers weeks together | −0.047 | 0 | **no**: in the simulation nobody lives alone, so the lever never bites |
| Trial: weeks together | +0.008 | +0.003 [−0.023, +0.029] | yes (both small) |
| Aids move pleasure by less than 0.001 | yes | trial +0.0009, prenup −0.0001, info −0.0002 (LAT −0.0014, not modeled) | yes |
| Pressure raises weeks together and holds people in | P1 +0.135, held 0.06 | P1 +0.035, held 0.058 | yes in sign; sizes larger in the exact model |
| Pressure's gain is the reward (lived below total) | lived −0.001 to −0.016 | lived −0.0002 to +0.0010 | yes in direction; lived is near 0, not below |

## Story spot-check (four lives, read week by week)

1. **Trial, p-anchor with p-steward.** They form an equal-bill trial at week 0. At its end (week 13) B's stay value is 0.812 against an outside option of 0.856, and B leaves by the trial's one reading. B returns at week 26, and the pair lives together to week 156 with both near 0.97. One trial end, one short stop. Matches "exits rise, weeks together do not".
2. **LAT, g-10011 with g-11100.** LAT at week 0, re-chosen at all eleven retries. Both live apart with Friend C all 156 weeks at 0.93 to 0.98, suffering 0.04 to 0.10. Under B the same pair lives in a household all 156 weeks. Matches "the aid people take".
3. **P4, p-anchor with p-bargainer.** Together throughout. B is classed held at 9 of 11 readings: its stay value (0.66 to 0.74) beats its outside option (0.61) only with the pressure counted. From week 42, B's suffering runs at 0.15 to 0.17 in long stretches, against A's 0.04 to 0.09. Matches the held-with-suffering pattern.
4. **Trial, p-peacekeeper with p-wanderer: a mismatch, and a finding.** Under B this pair never forms. Under the trial it forms at the week-65 retry, and B leaves at the trial's end (week 78). A stays in the household alone. From week 90, A's suffering climbs to 1.11 with non-offsettable suffering at 0.50, and A stays there to week 156. **The hybrid has no reading for a member left alone in the household**: the distress reading needs both in, and the return reading is for the one outside. So A never considers leaving. This is a gap in the hybrid's readings, not a trial effect. It can happen in any arm where one member leaves, and it is part of why non-offsettable suffering is higher in the trial (+0.0018) and all-aids (+0.0031) arms.

## Is the hybrid ready for the many-agent world?

**Not yet.** What is better: it now weighs each person's suffering in its big choices, and it runs its own readings where no harness does. Its forecasts still pass PT-H on the new yardstick, its routine still passes PT-R, and the weight's known answer holds. Three things stand in the way:

- **A member left alone has no reading** (story 4). In a many-agent world, every agent will sometimes be the one left. A reading to leave a household one is alone in has to come first.
- **Its forecasts assume no leaving.** It cannot value an exit option, so it cannot test any claim about freedom to leave making people commit. A forecast that lets future selves leave, at least by a cheap stand-in, is the next design question; it needs its own prereg and pass tests.
- **Cost.** About 36 s a run on 4 workers in this design (B 20 s; better information, 16 futures, 72 s; all aids 71 s), for two people and 156 weeks. That is close to its 34 s in step 3, against about 5 s for v1, v2 and v2b there, and it grows with the number of big choices. A many-agent world needs a cost probe before it uses this agent.

The trap's known answer (K1) also failed (held 0.077 against 0, bar 0.10), so held share under this agent is read with "known answer only partly met".

## Misses and weaknesses, plainly

- **H41 not supported, and its central mechanism not tested.** This agent cannot see the option value of an exit, so "freedom to leave makes people more willing to commit" was not put to a fair test. A null here says the hybrid does not commit more when leaving is easier; it does not say people would not.
- **E3 missed.** The pilot's trial gain (+0.05 on 10 pairings) did not replicate on 120.
- **Cheap solo housing never bit.** A lever with no one to act on cannot fail or succeed. A world where people live alone would be needed to test it.
- **Better information is only more sampled futures**, for an agent that already knows its partner exactly.
- **One seed** per pairing, chosen by the power check. Formation gains below about 0.03 are below what this sample resolves.
- **The matching rarely applied.** Only the trial, the prenup and better information had any formation to match, and each was matched in under 80% of resamples.
- **K1 failed**: the held lens's known answer is only partly met under this agent.
- **LAT has no costs of its own** (travel, coordination) beyond the world's.

## Can be about / cannot be about

This can be about whether, in the formation check's household under the hybrid agent with each person's suffering weight, five choice aids raise the share of weeks pairs live together, and what they do to pleasure and domination, beside H38's pressure. It cannot be about people, romance, real prenups or housing markets, or about agents that foresee leaving.

## Reproduction

`uv run python scripts/h41_choice_aids.py --reach` (seconds), `--pilot` (about 30 minutes), `--run` (about 3.3 hours on 4 workers), `--analyze` (about 10 minutes; writes runs/h41-choice-aids/analysis.json). Exact side model: `uv run python -m mar.h41_exact`. Tests: `uv run pytest tests/test_h41.py tests/test_hybrid_fix.py`.
