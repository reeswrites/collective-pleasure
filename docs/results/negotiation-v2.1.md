# Negotiation v2.1 results: a failed negotiation means living apart

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: instrument with scripted persona-driven agents. No LLM, no network. Findings are about rule systems and scripted agents, not people. Prereg: docs/results/negotiation-v2.1-prereg.md (committed first; not edited since). Code: src/mar/negotiation.py (`Lived(..., apart=True)`, `form_pot`, `apart_mode`), src/mar/worlds/household.py (`with_friend`, per-member solo modes), `uv run python scripts/household_run.py --negotiate-v2-1` (48 seconds wall, 8 cores; `--analyze` re-prints every number below; raw rows in runs/negotiation-v2.1/results.json, not committed). Only one pilot was run before the full run: 12 pairings x 3 arms x seed 0 (36 runs, 6 seconds), a code-path smoke run that changed no constant and fixed one bug (the lived-modes record was None for households that later formed a pot).

What was run: v2's design with floor ON only: variant author_seed_v2_bindable; 57 pairings x 3 start arms x seeds 0, 1, 2 = 513 runs, negotiated at week 0, lived 156 weeks, reviews every 13 weeks. The one change: a failed week-0 negotiation means the two members live separately (each in the better of alone and with Friend C by their own week-0 rollout) with 55 units of their own, and retry negotiation at each 13-week review. v2 comparison numbers are the floor-ON rows of runs/negotiation-v2/results.json.

## Prereg vs actual

**Three of five held. Prediction 2 failed on its second clause; prediction 5 failed by two runs, and the reason is a finding about v2 itself.**

| # | Preregistered | Actual |
|---|---|---|
| 1 | Mean s_non over all 513 runs at most 0.070 (v2 0.100); households apart from week 0 at most 0.100 (v2 no-pot 0.159) | **PASS.** All runs 0.0361; apart from week 0 0.0315 (n = 257); pot households 0.0408 (n = 256). Per arm 0.0353, 0.0366, 0.0365. The apart households are not worse off than the pot households on non-offsettable suffering. |
| 2 | Apart-from-week-0 households under 50 percent of failed runs AND overall fail rate at most 0.45 (v2 0.717 and 0.565) | **FAIL (one clause of two).** Overall fail rate 0.390 (holds). Apart households are 118 of 200 failed runs = 0.590 (needed under 0.50). Their fail rate fell from 0.809 to 0.459 but is above the pot households' 0.320, and they are half of all runs. |
| 3 | Re-run of v2's P1: unchanged to the digit, still fails both clauses | **PASS (as a prediction of no change).** Top third +0.989 (n = 57), bottom third +0.609 (n = 63), gap +0.379; the v2 P1 verdict stands: FAIL both clauses. Week-0 negotiations are identical in v2.1 (pot flag equal in all 513 runs). |
| 4 | Re-run of v2's P2: Free-rider's partner s_non at most 0.114 (v2 0.1495) | **PASS.** 0.0500 over the 144 runs (apart 0.0161, n = 87; pot 0.1016, n = 57). The partner is much better off living apart from the Free-rider. Note the partner in a pot household is still at 0.1016, close to v2's pressed level. |
| 5 | All 256 week-0 pot runs have outcomes identical to v2 | **FAIL: 254 of 256 identical.** Both differing runs are review outcomes: in one (wants-fallback, Controller with Wanderer, seed 2) v2 changed the terms at week 143 and v2.1 did not; in the other (wants-fallback, Host with Free-rider, seed 0) v2.1 changed them at week 13 and v2 did not. Cause: the outside-option rollout cache (`alone_value`) keys the hedonic state by (B, N) rounded to 0.1, so a cached rollout is reused for a nearby state, and what is in the cache depends on which runs a worker process executed earlier. v2.1's retry rollouts put different entries in the cache. This means v2's own results depend on worker scheduling to this small degree (2 of 256 pot rows flip when the workload changes); it is not a bug in the fix (the fix does not touch a pot household's path), and the v2 headline conclusions are not affected. |

## What the run shows

**Making the disagreement point real removed the damage.** The 257 households that failed to agree at week 0 (week-0 pot rate unchanged: 0.538, 0.503, 0.456; apart 79, 85, 93 per arm) now average s_non 0.0315, pleasure 0.716 and fail 0.459, against 0.159, 0.553 and 0.809 as cohabiting no-pot households in v2. The 175 that stayed apart for all 156 weeks: s_non 0.0233, pleasure 0.712, fail 0.417, mean wellbeing (pleasure less suffering) 0.544, equal to the pot households' 0.538. Of the 257, 95 put one member alone and one with Friend C, 162 both with Friend C. Living apart is, by construction, the outside option the member chose; a member whose outside option beat the pot now actually gets it.

**Pressing cohort and control cohort.** Pressing pairings: s_non 0.0421 (v2 0.1234), fail 0.423 (v2 0.659), pleasure 0.7345 (v2 0.6341). Control pairings: 0.0194 (v2 0.0345), fail 0.296 (v2 0.304), pleasure 0.8079 (v2 0.7697). Partners of the pressing personas (s_non, v2.1 / v2): Controller's 0.0118 / 0.0452, Free-rider's 0.0500 / 0.1495, Overasker's 0.0245 / 0.0975. The weaker partner of each pair (lower real outside option) has lived wellbeing 0.445 (v2 0.095). The pot households' pressing-partner levels are unchanged from v2 by construction; what changed is that fewer partners are in them.

**Retries.** 2244 retry rounds were held (13-week reviews while apart); 82 of the 257 households (0.32) formed a household later (26 at week 13, 10 at 26, 19 at 52, 7 at 78, 3 at 91, 9 at 104, 2 at 117, 3 at 143, others), so a failed week-0 table is often just a pair who needed time apart first by this model's valuations. Late-forming households did not do well: s_non 0.0491, fail 0.549, and 61 percent of them dissolved after forming (v2 pot households at week 0: 40 percent). I read that cautiously: a household formed late has a retry agreement made against a fair-default baseline that the live state does not always match.

**The 82 retry-formed and the 175 apart-forever households are not rule-system outcomes.** Comparing them with pot households compares living arrangements, not rule sets (prereg limit). The honest summary of the fix is: the v2 conclusion that making outside options real made households worse was an artifact of the broken disagreement point; with it fixed, making outside options real halves agreement (0.54 to 0.46 across arms against v1's 0.97) and does not hurt wellbeing.

## ASSUMED

All of v2's (closed-form terms, 26-week rollouts, TERM_SCALE 0.2, the floor of 26, the friend arrangement's cost 2.0 and cohabiting connection, fresh state at week 0); plus, fixed in the prereg: the pooling rule at a retry (min(45, own money) each), retry W and O as 26-week forward rollouts from the live state, one retry round per review, the alone-or-Friend-C choice re-made only at retries. Not tested: sensitivity to the retry deadline (6 proposals), to the pooling rule, or to keeping the week-0 mode for all 156 weeks.

## Limits

A household "apart" for 156 weeks is an outcome of the world's solo mode (alone costs 3.5 a week with no bills; with Friend C costs 2.0 with weekly contact), a mode designed in v2 as an outside-option valuation, not as a long-run living arrangement. Friend C is available to every member at no negotiation (a flat assumption). Fail is six consecutive weeks of non-offsettable suffering, a household-level criterion that does not say whether the person is better off apart. Scripted agents, one variant, one persona set, three seeds. Two pot rows differ from v2 because of cache history (prediction 5).

## Cost and runtime

513 lived runs: 48 seconds on 8 workers; at each worker's last run about 59,000 simulated rollout weeks and 2,281 rollouts (retry rounds are 3 to 4 rollouts each).

## Ledger lines (appended to docs/negative-results.md and docs/surprises.md in separate commits)

docs/negative-results.md, under "## 2026-11-10: negotiation v2.1":

- `negotiation v2.1 prediction 2 (2026-11-10): FAIL on the second clause. Apart-from-week-0 households are 118 of 200 failed runs = 0.590 (needed under 0.50; v2 0.717); overall fail rate 0.390 (needed at most 0.45; held). Prereg docs/results/negotiation-v2.1-prereg.md; results docs/results/negotiation-v2.1.md.`
- `negotiation v2.1 prediction 5 (2026-11-10): FAIL. 254 of 256 week-0 pot runs were identical to v2, not all 256. Both differences are review outcomes and trace to the outside-option rollout cache keying the hedonic state at 0.1 resolution, so results depend on which runs a worker executed earlier.`

docs/surprises.md, under "## 2026-11-10: negotiation v2.1":

- `2026-11-10 negotiation v2.1: the v2 finding that making outside options real made households worse was an artifact of the disagreement point. With a failed negotiation meaning living apart, no-agreement households fell from s_non 0.159 and fail 0.809 to 0.0315 and 0.459, and overall s_non from 0.100 to 0.0361; agreement is still 0.46 to 0.54.`
- `2026-11-10 negotiation v2.1: 82 of 257 households that failed to agree at week 0 formed a household at a later retry, and those late households did worse than week-0 pots (fail 0.549, 61 percent dissolved).`
- `2026-11-10 negotiation v2: results depend slightly on run scheduling. The outside-option rollout cache rounds the hedonic state to 0.1, so 2 of 256 pot rows changed their review outcome when the worker workload changed.`
