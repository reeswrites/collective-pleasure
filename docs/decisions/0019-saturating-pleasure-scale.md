# 0019. A saturating pleasure scale in place of the weekly cap

Status: accepted (2026-11-12). The author answered "Yes, both" to the step-back review's two proposals (experiments/readbacks.jsonl, rb-2026-11-12-stepback). This ADR is proposal 1. Proposal 2, the hybrid agent, is preregistered separately (docs/results/hybrid-agent-prereg.md).

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

## Context

Each week `Hedonic.close_week` adds up

raw = 0.5 × needs + 0.5 × aspirations + 0.10 × together sessions + glow + extra

and clips it to [0, 1]. Needs met and aspirations met already reach 1.0 between them, so everything a household adds on top (time together, items, the pairing reward, glow, lever payoffs) counts only for someone who is short somewhere. Costs in `extra` (H38's stigma and exit stigma) vanish the same way. Half or more of all person-weeks sit at the cap in H38 and the formation check, and up to 0.99 under v2b. The clip is read in three places: the spiral (B moves on clipped pleasure), the agents (v2 and v2b value the clipped close on purpose), and the evaluator (mean clipped pleasure). The step-back review (docs/notes/step-back-review.md, section 2) reads the cap as part of why accurate one-week agents leave households: the household's gains land above the cap and its costs below it.

The review weighed four options: uncapped pleasure, a saturating curve, distributions only, and declaring the cap real satiation. It recommended the curve, applied where the clip is, with distributions beside it.

## Decision

1. **The curve.** With raw pleasure x and a knee k,

   s(x) = 0 for x ≤ 0; s(x) = x for 0 ≤ x ≤ k; s(x) = k + (1 − k)(1 − exp(−(x − k) / (1 − k))) for x > k.

   It is continuous, has slope 1 at the knee, rises ever more slowly above it, and tends to 1. Nothing below the knee moves. The lower clip at 0 stays.

2. **Parameters, ASSUMED.** Knee k = 0.8. Asymptote 1. The curve's scale above the knee is (1 − k) = 0.2, so the slope at the knee is 1 and the curve keeps the old range. One free number, the knee. Some readings of the curve, all fixed by the formula: raw 0.9 reads 0.879; raw 1.0 (needs and aspirations fully met, nothing else) reads 0.926; raw 1.2 reads 0.973; raw 1.5 reads 0.994.

3. **Why these values.** The knee is the review's own example, chosen before any result on the new scale was seen. Three reasons, none of them a fit to an outcome:
   - 0.8 leaves every week that never reached 0.8 exactly as it was, so results lived mostly below it (the spirals, most suffering-side findings, households in trouble) do not move.
   - 0.8 is below 1.0, where needs and aspirations alone put a satisfied person, so a satisfied person is no longer at the ceiling. The step from 0.8 to 1.0 raw is where most of the review's hidden quantities live (time together +0.10 a session, the pairing reward 0.02 × L, glow 0.30).
   - An asymptote of 1 and a scale of 1 − k keep the scale's range, so old and new numbers sit on the same axis and a reader can set them side by side.

   No other knee was tried. A sensitivity sweep over the knee is not part of this decision; if one is wanted it gets its own prereg.

4. **Where it applies.** In `Hedonic.close_week`, in place of the clip, behind a flag: `FixConfig.pleasure_scale` ("clip", the default, or "sat") with `FixConfig.sat_knee` (0.8). The spiral, the agents' own week (`agent_values._week_net`) and the evaluator all read the same transformed number, because all three read the row's `pleasure`. Offsettable and non-offsettable suffering stay clipped to [0, 1]: the author's decision was about pleasure. Like `agent_values`, the flag is read only in worlds where the fixes are on, which covers every household experiment since the retest.

5. **The old line as a side check, for one round.** With the flag on, each weekly row also carries `p_clip`, the clipped number the old scale would have read for the same week. Results on the new scale report the old capped line beside the new one, from the same runs. (The two lines are not two separate worlds: the dynamics run on the new scale. The old-scale world is the flag off, and every old result reproduces exactly with it off: tests/data/scale_off_fingerprints.json, pinned at commit ae80dad before the flag existed.)

6. **Distributions beside the mean.** Every result on the new scale reports, beside mean pleasure: the share of person-weeks near the top (new scale ≥ 0.95; old scale at the cap, raw ≥ 1.0) and the worse-off partner (per run, the lower of the two partners' mean pleasure).

## What the curve says about value, said plainly

The curve is concave on purpose. The author accepted both consequences when he said yes:

- **An equal raw gain counts more for someone worse off.** Below the knee a raw gain counts in full; above it, less and less. Mean transformed pleasure is a mildly prioritarian measure, not a plain sum. "Everyone counts" still holds: everyone's pleasure enters, but a well-off person's extra counts less.
- **Costs to the well-off stop being free.** Under the clip, a cost that only shaved surplus above 1.0 read as zero. Under the curve it reads as a loss, smaller than the same loss lower down. The evaluator's "raises freedom without costing pleasure" becomes checkable for people who are doing well.

## Consequences

- "Raises pleasure" in a verdict means a rise in mean transformed pleasure. Every margin and power check written on the clipped scale needs restating on the new one before a rerun (for example the formation check's 0.007).
- A person at raw 1.0 reads 0.926, not 1.0. Means of satisfied populations fall on the new scale. Comparisons are within a scale, never across.
- The spiral moves on the transformed number. Surplus above the knee now builds a little capacity, with diminishing returns.
- v2's one-week arithmetic mirrors the close, so it reads the curve too. The value check is rerun on the new scale as a known-answer test (docs/results/pleasure-scale.md).
- The H39b finding that clipped pleasure cannot see the wanting trap (ledger row 46b) may soften: a trap at full tolerance now reads below 1. Not rerun here.
- Not changed: the hedonic parameters, the suffering clips, the lower clip at 0, any experiment's design. No hypothesis is rerun under this ADR alone.

## Not decided here

- Whether the curve is right about people. It is a modeling choice made for stated reasons, not a finding.
- Whether to drop the old capped line after one round. Decide after the step-3 formation check.
