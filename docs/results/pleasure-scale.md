# The saturating pleasure scale: the value check, and whether the cap explains the leaving

Wording rule: agents feel nothing; "pleasure", "suffering" and "value" are glosses for modeled numbers.

Status: run on 2026-11-12, after ADR 0019 ([0019-saturating-pleasure-scale.md](../decisions/0019-saturating-pleasure-scale.md); commit 95c9954) and the flag (commit 465d070). Step 1 of the step-back plan ([step-back-review.md](../notes/step-back-review.md)). Two measurements, no hypothesis test, no verdict, no parameter changed or fitted. Scripted agents, no model calls, every number ASSUMED.

## In one paragraph

**On the new scale, v2's one-week values still agree with the model almost exactly, except for time together, which the cap had been hiding.** The rank correlations barely move (pooled 0.990 to 0.975; the agent's best is the actual best in 97% of decisions either way). But the check now fails one clause: time together is valued at +0.023 and is worth +0.006, because a session the agent counts in full is scaled down by satiety in the world, and on the old scale that error sat above the cap where neither side could see it. **The cap explains some of why accurate agents leave households, not most of it.** Without bills, 88% of the household's raw weekly advantage at formation sat above the cap; the curve keeps a little over twice as much of it (+0.045 a week against +0.019). Week-0 formation under v2 rises from 0.76 to 0.88, and forced households end by week 52 a little less often (0.60 to 0.51). Half still end. With bills that hurt, the household is worse than the outside option before any cap (raw −0.021 a week), so the cap explains none of that collapse.

## 1. The value check on the new scale

The check as the recalibration ran it ([agent-recalibration.md](agent-recalibration.md), "The pass test"): H39b's M0 world, H38's 120 confirmatory pairings × seeds 0 to 3, six sampled weeks, both partners, the week's last call; v2 agents with bills that hurt. Only the scale changed (`pleasure_scale="sat"`, knee 0.8). 5,760 decisions, 19,107 measured actions, 1,323 s on 3 workers (`scripts/value_consistency.py --v2sat --run`, `--passtest`, `--analyze`; rows in runs/value-consistency-v2-sat/). Old-scale numbers are the recalibration's own rows (runs/value-consistency-v2/).

| ID | Quantity | Old scale (clip) | New scale (curve) | Bar |
|---|---|---|---|---|
| T1 | pooled rank correlation | 0.990 | **0.975** | ≥ 0.70 |
| T2 | within-decision rank correlation | 0.991 | **0.987** | ≥ 0.60 |
| T3 | agent's best = actual best | 97.1% | **96.5%** | ≥ 60% |
| T4 | best beats next best | 91.4% | **97.2%** | ≥ 60% |
| T5 | slope of actual on perceived | 1.02 | **1.01** | 0.8 to 1.25 |
| T6 | every action's mean gap within its bar | all hold | **together fails** | max(0.015, a quarter of actual) |
| | verdict | PASS | **FAIL (T6, one action)** | |

Per action, own net at one week on the new scale:

| Action | n | Perceived | Actual | Gap | Old-scale gap |
|---|---|---|---|---|---|
| work | 1,540 | +0.026 | +0.026 | +0.001 | +0.000 |
| rest | 5,388 | +0.020 | +0.019 | +0.000 | +0.000 |
| see a friend | 5,298 | +0.015 | +0.014 | +0.001 | +0.001 |
| time together | 298 | **+0.023** | **+0.006** | **+0.017** | +0.005 |
| pay shared bills | 984 | +0.017 | +0.013 | +0.004 | +0.004 |
| spend on oneself, no rule | | −0.034 | −0.034 | 0.000 | 0.000 |

**Why time together fails.** The world plays each session at its satiety scale for everyone once the levers' adaptation is on; v2 expects a full session unless the persona's variety policy is "adaptive" (a choice the recalibration kept on purpose, ADR 0016). A forced session at a week's last call, read beside the world's close (two pairings, a diagnostic script in the scratchpad, not committed): the agent's projected raw pleasure was 0.03 to 0.06 above the world's, for both partners. On the old scale both numbers were above 1.0 and read 1.0, so the error was invisible; on the curve it lands where it counts. The observer groups say the same: the session's own pleasure is +0.026 and the curve takes back 0.022. The gap shows under every variety policy (repeat +0.032, rotate +0.023, adaptive +0.013); I traced only the non-adaptive cases. This is a chosen misforecast that the cap had made harmless, not a new bug, but it now moves the agent: it prices a session at four times its worth.

**The other measures of the same rows:**

- **Unclipped** (raw pleasure − suffering): T1 0.70 on the old scale, **0.85** on the new. Still a fail (rest and friends underpriced by 0.033 and 0.017), but the agents are closer to the uncapped answer, as the curve intends.
- **The old capped line**, the new-scale rows held to clipped pleasure (`p_clip`): T1 0.86, T3 75%, T4 66%; time together's gap +0.020. Agents that value the curve look less accurate when scored on the cap, mainly on the best-action clauses.

**What this means for the hybrid.** The hybrid's routine is v2. PT-R (its pass test, [hybrid-agent-prereg.md](hybrid-agent-prereg.md)) compares it with v2 on the same scale, so this failure is its baseline, not a bar it must clear. The satiety expectation is left as it is: changing it would be a patch the step-back plan said not to make before the hybrid exists, and it is a persona-level choice (ADR 0016).

## 2. Is the cap why accurate agents leave households?

`scripts/cap_probe.py --run` then `--analyze` (rows in runs/cap-probe/; 120 confirmatory pairings, seed 0; 231 s on 3 workers). The formation check's G-L0 world (corrected rule: own mean pleasure over 52 weeks), three agent sets. Three parts:

- **A, the household's benefit, on one set of lives.** At week 0, the household's 52-week rollout against each member's outside option, both on the old scale. Each week's raw pleasure read three ways: no cap, the old clip, the curve. Benefit = household minus outside option, per member.
- **B, the formation rule run on each scale**: agents, spiral and rule all on the old scale, then all on the new one.
- **C, leaving**: formation forced at week 0, 52 weeks lived with readings at 13, 26 and 39 weeks; the share of member-readings where the outside option beats staying, and households ended by week 52.

| | v1 | v2 | v2 + bills |
|---|---|---|---|
| **A. Benefit a week at formation**: no cap | +0.184 [+0.175, +0.194] | +0.180 [+0.170, +0.189] | −0.021 [−0.035, −0.006] |
| old clip | +0.075 | +0.019 | −0.068 |
| new curve | +0.072 | +0.045 | −0.045 |
| share of the raw benefit above the cap (members who gain) | 59% | **88%** | (no raw gain) |
| share above the curve | 61% | 75% | |
| household person-weeks at the top: old (raw ≥ 1) / new (≥ 0.95) | 72% / 56% | 95% / 87% | 56% / 33% |
| pairs where both gain: no cap / clip / curve | 1.00 / 0.85 / 0.98 | 0.90 / 0.76 / 0.89 | 0.27 / 0.07 / 0.12 |
| **B. Formed at week 0**: old scale / new scale | 0.85 / 0.98 | **0.76 / 0.88** | 0.07 / 0.09 |
| **C. Forced households**: readings where the outside option wins, old / new | 0.08 / 0.03 | **0.52 / 0.36** | 0.78 / 0.66 |
| ended by week 52, old / new | 0.11 / 0.02 | **0.60 / 0.51** | 0.97 / 0.95 |

Intervals are 95% bootstrap over members (A). Parts B and C are shares of 120 pairings.

**Reading it:**

- **The review's mechanism is real.** Without bills, households add about +0.18 a week of raw pleasure for both v1 and v2, the same size. The cap leaves v1 with +0.075 and v2 with +0.019: v2's agents live closer to the top on their own (outside option 0.976 clipped against v1's 0.892), so almost all of the household's advantage lands above the cap for them. That is why the same household is worth four times less to a v2 agent.
- **The curve gives back part of it.** +0.045 instead of +0.019, and 0.88 instead of 0.76 forming. Forced v2 households see the outside option win in 36% of readings instead of 52%.
- **It does not explain most of the leaving.** On the new scale half of forced v2 households still end within a year (0.51, against v1's 0.02). The curve still compresses 75% of the advantage (v2's households live at raw 1.17, deep in the flat part), and the rest of the gap between v1 and v2 is not the scale. The review's "that is a cap problem showing up as an agent problem" is about a third right by these numbers.
- **With bills that hurt, the cap is not the story.** The household is worse than living apart before any cap (raw −0.021). The curve moves formation from 0.07 to 0.09.

## Distributions (ADR 0019, decision 6)

From part A: the share of household person-weeks at the top falls on the new scale (v2: 95% at the cap, 87% at 0.95 or more), so "near the top" still describes most of v2's household life. The worse-off partner is reported in step 3, where it is a preregistered measure.

## Misses and weaknesses, plainly

- **The value check fails on the new scale, on one clause.** It is reported as a fail, not adjusted.
- **The probe is seed 0 only** and one world. Part A scores the old-scale lives on the new scale, so it ignores what the curve does to the spiral and to choices; parts B and C include it.
- **Part C reads a 52-week life**, not the formation check's 156 weeks, and only with formation forced.
- **The knee was not varied.** Another knee would give other numbers; the ADR fixed it before any of these runs.
- **The together diagnosis** was traced in two pairings, by a script that is not committed.

## Can be about / cannot be about

This can be about how v2's one-week values agree with the hedonic model on the saturating scale in the H39b M0 household, and how much of a household's modeled advantage the weekly cap and the curve each hide at formation in the formation check's world. It cannot be about people, or about any H38 claim: no hypothesis was rerun.

## Reproduction

`uv run python scripts/value_consistency.py --v2sat --run` (about 22 minutes on 3 workers), then `--v2sat --passtest` and `--v2sat --analyze`. `uv run python scripts/cap_probe.py --run` (about 4 minutes), then `--analyze`. Tests: `uv run pytest tests/test_pleasure_scale.py -m ""`.
