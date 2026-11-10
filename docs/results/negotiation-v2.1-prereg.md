# Negotiation v2.1 preregistration (2026-11-10, committed BEFORE any v2.1 run, pilot or full)

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: instrument, scripted persona-driven agents, no LLM, no network. Findings are about rule systems and scripted agents, not people. Builds on docs/results/negotiation-v2.md (0 of 8 predictions held) and docs/decisions/0013-negotiated-pots.md. Author decision (2026-11-10, "yes take ur rec"): fix the no-agreement flaw first, then run a small real-agent negotiation test (docs/results/negotiation-llm-prereg.md). Other household mechanics are paused.

## The flaw being fixed

In v2 a failed negotiation ("no pot") left the partners living together in one house with their own holdings and no pooled share. Those households were the worst in the study (non-offsettable level s_non 0.159 against 0.041 with a pot; pleasure 0.553 against 0.787; 97 percent dissolved), and the outside option that made them fail to agree (living alone or with Friend C, simulated for 26 weeks) was one the member could not actually take. That made "making outside options real" look harmful. It is a bug in the disagreement point, not a finding about outside options.

## The fix (the only change; same design as v2 otherwise)

1. A failed negotiation at week 0 (status no_pot, deadline or no_bundle) means the members do NOT form a shared household. Each lives separately for the horizon, on their own holdings (money 55: the 10 private plus the 45 that would have been pooled; nothing pooled), in the world's existing solo mode: both partners out of the household, no bills, Friend C still reaches out. Each member lives in whichever of the two outside arrangements their own week-0 rollout valued higher (alone, or with Friend C: cost 2.0 a week, cohabiting connection, weekly contact). So a no-pot household is now lived exactly as the outside option was valued (the world gets per-member solo modes; solo as one string for both members is unchanged).
2. They may retry negotiation at each 13-week review (weeks 13, 26, ..., 143) while apart. At a retry: each member re-picks the better of alone and with Friend C from a 26-week rollout of its live state (that value is its outside option O); the in-pot value W is a 26-week rollout of a copy of the live world turned into a household under the fair default (each member puts min(45, own money) into the pooled share, the rest stays private); the protocol is v2's review protocol (at most 6 proposals, seeded order, floor and proof checks, the floor measured on the holdings after pooling), with no status quo (no agreement means they stay apart). If a bundle is agreed they move in together at that week under its cards and commitments (a stay runs from that week), the pooled share is formed as above, and the normal 13-week reviews of the terms follow.
3. Households that formed a pot at week 0 are untouched. Their lived runs must be bit-identical to v2 (checked, not predicted).

ASSUMED (fixed here): the pooling rule at a retry (min(45, own money)); the retry's W and O as 26-week forward rollouts from the live state (the same scale as v2 reviews); one retry round per review; the mode choice (alone or Friend C) is re-made at each retry only; living apart for 156 weeks is not "dissolved" in the dissolution rate (reported separately as "apart from week 0", and "dissolved" is reported for households that began together).

## Runs

Same as v2, floor ON only (the floor-OFF ablation and the v1 and imposed references are not rerun; their v2 values are quoted): variant author_seed_v2_bindable; 57 pairings (15 control, 42 pressing) x 3 start arms x seeds 0, 1, 2 = 513 runs, 156 weeks, reviews every 13 weeks. Command: `uv run python scripts/household_run.py --negotiate-v2-1` (analysis re-printed by `--negotiate-v2-1 --analyze`). v2 numbers quoted for comparison are from docs/results/negotiation-v2.md (floor ON rows of runs/negotiation-v2/results.json).

## Predictions (floor ON, all arms pooled; confidence is mine, stated before any run)

1. Non-offsettable suffering falls. Mean s_non over all 513 runs is at most 0.070 (v2: 0.100). Households apart from week 0 have mean s_non at most 0.100 (v2 no-pot households: 0.159). About 50 percent: living apart removes the shared-house friction, but solo living has its own suffering (cost 3.5 a week alone, no partner) that I have not measured on this scale.
2. Failures are no longer dominated by no-agreement households. In v2, 71.7 percent of failed runs (290 failures; fail = 6 consecutive weeks of non-offsettable suffering) were no-pot households (257 of 513 runs, fail rate 0.809). Holds if households apart from week 0 account for under 50 percent of failed runs AND the overall fail rate is at most 0.45 (v2: 0.565). About 45 percent.
3. P1 of v2 (presser's gain over the imposed bundle, top-third versus bottom-third partner outside option) is re-run with the fix. Expected to be UNCHANGED, to the digit: the measure is the closed-form value of the agreed week-0 bundle, and week-0 negotiations are identical in v2.1. So it still FAILS both clauses (top third +0.989, n = 57; bottom third +0.609, n = 63; gap +0.379). If any digit moves, that is a bug in the fix, not a result. About 90 percent.
4. P2 of v2 (the Free-rider's partner's s_non, at most 0.114; v2: 0.1495 over 144 runs, 87 of them no-pot) is re-run with the fix. Expected to CHANGE and to now hold: the 87 no-pot households' partners are no longer sharing a house with the Free-rider. Holds if at most 0.114. About 50 percent: the partner who is out is not pressed, but may suffer from living alone.
5. Bit-identity: every one of the 256 week-0 pot runs of v2 (floor ON) has identical outcomes (s_non, pleasure, left, exits) in v2.1. About 95 percent (it is a check on the code path, not on the world).

## Reported either way

Per arm: week-0 pot rate (must equal v2's 0.538, 0.503, 0.456), apart-from-week-0 rate, retries held and pots formed by retry (count, week, terms), households apart for all 156 weeks, mix of alone versus with Friend C, s_non, pleasure, fail and wellbeing of apart households against pot households and against v2's no-pot households, pressing cohort and control cohort numbers, the pressing personas' partners' s_non, the weak partner's wellbeing, rollout counts and wall time.

## Limits (stated now)

A household that is apart is not one household: comparing its wellbeing with a pot household's compares two living arrangements, not two rule sets. The no-pot outcome is now the outside option by construction, so its level depends on the world's solo mode (costs 3.5 alone and 2.0 with Friend C, ASSUMED in v2) and on TERM_SCALE-free rollouts only. Scripted agents, one variant, one persona set, three seeds.
