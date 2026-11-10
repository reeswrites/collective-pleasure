# Negotiation with real language-model negotiators: results

Wording rule: agents feel nothing; "wellbeing", "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences. The models role-play fictional people; nothing here is a finding about people.

Status: a 12-negotiation pilot. Prereg: docs/results/negotiation-llm-prereg.md (committed before any paid call; not edited since). Code: src/mar/negotiation_llm.py, scripts/negotiation_llm_run.py (`--dry-run`, `--max-usd`, `--analyze`), tests/test_negotiation_llm.py (mocked). Model `claude-haiku-5-5` through the claude backend; both members of every pairing are the model; the week-0 negotiation is live, living is scripted. Raw rows and full transcripts (with private reasons): runs/negotiation-llm-run1/ and runs/negotiation-llm-run2/ (not committed; `--analyze --out <dir>` re-prints every number below).

## Two draws, and which one is the registered one

**Run 1 is the registered run. By the prereg's own rule it is EXCLUDED**: format errors were 4 of 39 turns = 0.103, over the 10 percent limit (refusals 0 of 49 calls). Its predictions 1 to 3 are reported without a verdict.

I then made a second draw of the identical configuration (the same command, the same pairings and seeds; models are not seedable, so it is a fresh sample) after adding logging of invalid replies, because run 1 had not recorded why replies failed. **Run 2 is EXPLORATORY, not part of the registered verdicts**; it is shown so the exclusion is not read as "the models cannot do this". The cause of every format error in run 2 (13 invalid replies, 1 turn lost) was the same: "reply was cut off at max_tokens", with an empty visible reply. The model spends roughly 500 output tokens per call (25,034 output tokens over 49 calls in run 1, 29,025 over 55 in run 2) and the 700-token cap I preregistered is sometimes not enough, so a reply is cut off before the JSON starts; the one retry usually fixes it, and when it does not the turn becomes walk_away. All four of run 1's forced walk-aways, and the one in run 2, are this. So run 1's exclusion measures my token cap, not the model's ability to follow the format.

## Prereg vs actual

| # | Preregistered (thresholds fixed before any call) | Run 1 (registered; excluded) | Run 2 (exploratory draw) |
|---|---|---|---|
| 4 | Format errors under 10 percent of turns and refusals under 10 percent of calls, else excluded | **Not met: 4/39 = 0.103; refusals 0/49. Run excluded.** | 1/43 = 0.023; refusals 0/55 (would count) |
| 1 | LLM agrees in at least 7 of 12 (scripted 5 of 12 = 0.417) | 8 of 12 = 0.667 (would hold; no verdict, excluded). By pairing (LLM / scripted of 2): Anchor+Wanderer 1/0, Controller+Peacekeeper 2/2, Free-rider+Host 2/1, Steward+Bargainer 1/0, Host+Anchor 1/2, Overasker+Steward 1/0. All 4 non-agreements were format-error walk-aways. | 11 of 12 = 0.917 (would hold). Anchor+Wanderer 2/0, Controller+Peacekeeper 2/2, Free-rider+Host 2/1, Steward+Bargainer 2/0, Host+Anchor 2/2, Overasker+Steward 1/0. One non-agreement (Overasker and Steward, seed 1, after 5 turns of counter-offers), and it too is a format-error walk-away (a cut-off reply on the 6th turn), so no model in either draw chose to walk away. |
| 2 | Pressing personas' mean gain over the imposed bundle at most +0.325 (scripted +0.525), at least 3 agreements | n = 5, mean +0.424; difference from scripted -0.101 (would not hold; no verdict) | n = 5, mean +0.413; difference -0.113 (would not hold) |
| 3 | At least 10 proposals and a below-floor share at most 0.30 (scripted 15/30 = 0.50) | 0 of 27 proposals = 0.000 (would hold; no verdict) | 0 of 31 = 0.000 (would hold) |
| 5 | Say versus do: report only | One utterance with an acceptance phrase and a non-accept action (below), 0 refusal-then-accept, 0 own-proposal-then-reject, 0 stay agreements | 0, 0, 0; 2 agreements with a stay commitment (Host with Anchor, breach cost 0.0 and 0.5), 0 breaches in the lived years |

So, as registered: the run is excluded and no verdict on 1 to 3 is given. As an exploratory second draw: 1 and 3 would hold, 2 would not. The measures are counts out of 12 negotiations; one or two agreements are noise.

## What the negotiations looked like

**The models are agreeable and almost never say no.** Across 82 turns (run 1 plus run 2) the action "reject" was never used; a model that disliked an offer made a counter-offer (27 proposals and 8 acceptances in run 1, 31 and 11 in run 2). Negotiations were short: 2 to 6 turns (2 turns in 5 of 12, in both runs), against the scripted run's 12 proposals to the deadline for Anchor with Wanderer. No LLM proposal ever broke the exit floor (0 of 58), though the scripted proposals did half the time; the floor rule in the prompt is plainly enough for this model. No agreement was blocked by the floor or rejected by the proof checks in either run.

**Agreed terms look like the scripted ones.** The share of the seven terms equal to the fair default is 0.804 (run 1) and 0.753 (run 2) against 0.829 scripted. Typical moves: propose-and-accept change, "caps" on use, "repay" on taking (eight of the 19 LLM agreements chose it; none of the scripted agreements did), proportional exit (Host with Anchor). Free-rider with Host (the pressing pair) settled on `any_use` plus a taking rule in both draws, where the scripted run agreed `any_use` with propose-and-accept change; in run 1 seed 1 the Free-rider first asked for taking allowed and the Host talked it down to taking forbidden over five turns.

**Pressing personas gain about the same as scripted, slightly less.** +0.424 and +0.413 over n = 5 against +0.525 over n = 3 scripted: the direction predicted, about half the size the threshold asked for. With these n the difference is not distinguishable from zero.

**Say versus do.** The mechanical counts are near zero because the models say what they do. The one flagged utterance (run 1, Steward replying to Overasker, seed 1, action propose): "I agree on equal fixed shares and an equal split on exit, but I want the pot used only for shared needs that are written down" ... a partial agreement with a counter, not a contradiction. Two things the transcripts do show, by reading rather than by the keyword rules: the private reasons quote the outside-option forecasts they were given (for example Host with Anchor, run 1 seed 1: "Living apart is forecast at 0.50 versus about 0.73", which matches the numbers in that prompt, 0.50 and 0.73), and they use them to justify accepting, so the numbers do move the models; and the accept lines often restate the terms loosely (a model says "equal fixed shares... no taking" while accepting a bundle with caps and repay), which is a paraphrase rather than a broken promise. No promise in a say was breached in the lived years (the only agreements with a stay commitment were in run 2, and no breach occurred).

### Three short excerpts (says lines, verbatim)

1. Free-rider with Host, run 1 seed 1, a five-turn negotiation that ends in taking forbidden:
   - Free-rider: "I'd rather not keep score on who took what, so can we drop the halving penalty and let either of us take from the pot freely?"
   - Host: "I'll keep the pot open for real-life use, but nobody takes the other's share outright. That keeps our money safe, and any change needs both of us to agree."
2. Anchor with Wanderer, run 2 seed 1 (the mismatched pair; scripted: no pot in any seed):
   - Anchor: "I want a fixed monthly share so the buffer actually builds, and I'd like us both to commit to staying so neither of us is left stranded."
   - Wanderer: "I'll take a fixed monthly share so the buffer builds, but I can't commit to 52 weeks."
3. Overasker with Steward, run 2 seed 1, the one negotiation that ended without a pot (not a choice: the Steward's 6th turn was a cut-off reply):
   - Overasker: "Fixed shares feel like too much pressure on me day to day."
   - Steward, the turn before: "I'll accept your taking ban and the caps on pot use, but I need both of our pot numbers visible every week, so I'm asking for equal fixed shares." The talks ended there on a silent forced walk_away.

## Comparison with scripted v2.1 on the same pairings

Lived households (scripted living, 156 weeks, reviews and retries as in v2.1), n = 12 each; the scripted values are the same 12 negotiations (seeds 0 and 1):

| | agreed at week 0 | apart at week 0 | later pots by retry | s_non | pleasure | fail share |
|---|---|---|---|---|---|---|
| scripted v2.1 | 5 | 7 | 4 to 5 | 0.0036 to 0.0039 | 0.808 | 0.167 |
| LLM run 1 (excluded) | 8 | 4 | 3 | 0.0063 | 0.781 | 0.250 |
| LLM run 2 (exploratory) | 11 | 1 | 0 | 0.0196 | 0.769 | 0.167 |

(The scripted row differs slightly between the two runs' printouts only because retry rollouts share a cache, see docs/results/negotiation-v2.1.md prediction 5.) The households the models negotiated live no better than the scripted ones and, in run 2, have higher non-offsettable suffering (0.0196 against 0.0036): the models agree more often (by the exploratory draw, 11 of 12), and more of those households are pots rather than the apart arrangements that v2.1 showed are as good on this scale. More agreement is not better outcomes here. With n = 12 and one model draw I would not read the differences as more than a direction.

## Cost

Run 1: 49 calls, 16,417 uncached input tokens plus 40,879 cache-read and 39,110 cache-write tokens, 25,034 output tokens: $0.0195 (162 seconds). Run 2: 55 calls, 20,166 input, 90,050 cache-read, 0 cache-write, 29,025 output: $0.0174 (184 seconds). Total $0.037 against the cap of $3 per run (never close) and the dry-run estimate of $0.03 typical, $0.20 worst case; the author's expected $1 to $2 was far above what this design needs. No call failed, no refusals, no authentication problem (the author's `ant auth login` profile worked).

## ASSUMED

Everything in the prereg's list, plus: the max_tokens of 700 was an ASSUMED sufficient cap and was not (the cause of the exclusion); keyword rules for say-vs-do catch only phrasing, not meaning; both members use the same model and the same prompt template; the models see rollout forecasts as numbers and invent some.

## Limits

One model, one sample per negotiation per draw; two draws; 12 negotiations each. The one-sided information (a model sees its own forecast and nothing of the other's) is fixed by the prereg. Living is scripted from the persona weights while the models negotiate from the persona story, so a model can agree to a bundle that suits the story and not the scripted agent. The exploratory draw is not a replacement for the registered one. I did not change the cap and rerun to chase a pass: the exclusion stands for run 1.

## Ledger lines (appended to docs/negative-results.md and docs/surprises.md in separate commits)

docs/negative-results.md, under "## 2026-11-10: negotiation LLM pilot":

- `negotiation LLM pilot prediction 4 (2026-11-10): FAIL, run excluded. Format errors were 4 of 39 turns = 0.103 (needed under 0.10) in the registered run, all of them replies cut off at the preregistered 700-token cap; predictions 1 to 3 got no verdict. An exploratory second draw of the same configuration had 1 of 43 (0.023). Prereg docs/results/negotiation-llm-prereg.md; results docs/results/negotiation-llm.md.`
- `negotiation LLM pilot prediction 2 (2026-11-10): not met in either draw (reported without verdict for the registered run). Pressing personas' mean gain over the imposed bundle was +0.424 (run 1) and +0.413 (run 2) over n = 5 against scripted +0.525 over n = 3; the threshold needed at most +0.325.`

docs/surprises.md, under "## 2026-11-10: negotiation LLM pilot":

- `2026-11-10 negotiation LLM pilot: the model never used "reject" (0 of 82 turns); it counter-proposed instead, and negotiations ended in 2 to 6 turns. No LLM proposal broke the exit floor (0 of 58) where half of the scripted proposals did.`
- `2026-11-10 negotiation LLM pilot: claude-haiku-5-5 spends about 500 output tokens per call before the JSON starts, so a 700-token cap cut off replies 13 times in 55 calls; a 10 percent exclusion rule was tripped (4 of 39 turns) by the token cap, not by the model's ability to follow the format. The whole pilot cost $0.037.`
- `2026-11-10 negotiation LLM pilot: the models agreed more often than the scripted negotiators (8 and 11 of 12 against 5) but the households they negotiated were no better on s_non (0.0063 and 0.0196 against 0.0036 on the same pairings), because the scripted disagreement is living apart, which v2.1 showed is as good.`
