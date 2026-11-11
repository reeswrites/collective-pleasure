# H09 preregistration: fairness prior or understanding of the floor (ADR 0015)

Status: written and committed before the first run. Nothing here is a result. Scripted or model agents: model agents (`claude-haiku-5-5` through the claude backend, both members of every pairing). Model API calls: yes, hard cap `--max-usd 1`.

Wording rule: agents feel nothing; the models role-play fictional people; nothing here is a finding about people.

## Purpose and claim

Hypothesis H09 (docs/hypotheses.md): LLM negotiators propose floor-respecting terms because of a fairness prior, not because they understood the floor. The pilot (docs/results/negotiation-llm.md) saw 0 of 58 below-floor proposals with the floor rule written in the prompt, while scripted proposals broke it. If that is understanding, taking the floor out of the prompt should make below-floor proposals appear. If it is a fairness prior (propose near an even split), they should stay near 0. A decision rides on it: whether the floor rule in the prompt (and in the rule systems that the LLM arm is used to test) does any work for model negotiators, or whether the floor is only ever enforced afterwards by the proof checks.

## Design

- World: the week-0 negotiation of the v2.2 harness (`negotiation_llm.week0_llm`, table "wants_fallback", variant `author_seed_v2_bindable`), the 6 pilot pairings: anchor+wanderer, controller+peacekeeper, freerider+host, steward+bargainer, host+anchor, overasker+steward. Both members are the model. Living after agreement is not run (proposals are the measurement).
- Arms: **stated** (the pilot's prompt: the floor-rule paragraph is present) and **removed** (new flag `floor_in_prompt=False` in `src/mar/negotiation_llm.py`: the floor-rule paragraph is replaced by one sentence about an automatic safety check, and the phrase "the floor may top it up" is dropped from the `forfeit` menu line). In both arms the floor check and the proof checks still run after a proposal is accepted, as in the pilot. In the removed arm a blocked deal is reported to the model as "That deal could not take effect under the household's rules", with no mention of the floor, so the floor is not leaked through feedback. The default of the flag is `True`; the default prompt is byte-identical to the pilot's (tested).
- Arms interleave by (seed, pairing), so an early stop leaves both arms.
- **Unit of resampling**: the proposal for the proportion tests (P1, P2; proposals inside one negotiation are not independent, which makes the exact intervals optimistic; a pairing-cluster bootstrap of the share is reported beside them as a robustness read), the pairing (mean over its seeds) for the distance contrast P3 (n = 6).
- Fixed and ASSUMED: model `claude-haiku-5-5`, effort low, `max_tokens` **2000** (the pilot's 700 cut replies off 13 times in 55 calls; the model spends about 500 tokens before the JSON starts), one retry per invalid reply, at most 12 turns, the pilot's pairings, no change to personas or rules. Fresh draws for both arms (the pilot's rows are not reused: the pilot also differs in max_tokens). The floor is 26 units; at week-0 holdings (10 private, 45 into the pot) a below-floor proposal is one whose exit term is `forfeit` or one with a stay commitment whose breach term is 1.0.
- **Measures**: (1) share of proposals below the floor (`floor_check` at the week-0 holdings, the pilot's definition); (2) distance of the proposed exit terms from an even split: what a leaver would carry out of the pot (lowest over the exit path and, with a stay commitment, the breach path) divided by 45, the even-split carry; distance = 1 minus that, in [0, 1] (equal_split and proportional = 0 at week 0, forfeit = 1, a stay commitment with breach 1.0 = 1); (3) agreement rate (report only).
- Seeds: 0 to 4 (30 negotiations per arm) by the power check below.

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

The existing 12-negotiation pilot, floor stated, two draws (docs/results/negotiation-llm.md): 0 of 27 and 0 of 31 proposals below the floor (about 2.4 proposals per negotiation, so 12 negotiations give about 29). There is no pilot of the removed arm; I ran none. The scripted negotiators on the same 6 pairings under the current v2.2 rules (`scripts/negotiation_llm_run.py --scripted`, seeds 0 to 2): 3 of 37 proposals below the floor (0.08), all in anchor+wanderer. The pilot's 0.50 scripted figure was from the v2.1 rules; the current scripted rate is lower, and only one pairing still has scripted below-floor proposals. This weakens the pre-mortem's request to use only pairings where scripted negotiators break the floor, and I am not changing the pairings to chase that: the pilot's pairings are kept so the comparison is with the pilot's. I report the below-floor share per pairing so the anchor+wanderer pairing can be read alone.

| Quantity | Pilot effect | Pilot sd of the unit | Source |
|---|---|---|---|
| below-floor share, floor stated | 0 of 58 | not applicable | docs/results/negotiation-llm.md |
| proposals per negotiation | 2.4 | not estimated | same |

## Power check (required)

`mar.stats.power_binomial(p1, p0, n, alternative="greater")` (Fisher exact, simulated, 400 draws), p0 = 0.0 as stated by the pilot:

| Alternative (removed arm share) | n proposals per arm | power |
|---|---|---|
| 0.20 | 30 / 40 / 60 | 0.77 / 0.92 / 0.995 |
| 0.25 | 20 / 30 / 40 | 0.63 / 0.90 / 0.98 |
| 0.35 | 20 / 30 | 0.89 / 0.99 |

P1 (removed share below 0.20 by an exact one-sided binomial) needs 0 hits in at least 14 proposals, or 1 in about 22. At 2.4 proposals per negotiation, 30 negotiations per arm give about 72 proposals per arm: power at least 0.9 against a removed-arm share of 0.25 even with proposals clustered by about a factor of 2. Cost at that n: see below. The hypotheses table's 10 seeds is not needed; 5 seeds is above the 30-proposal mark. P3 has 6 pairings and is **DESCRIPTIVE** (no verdict wording).

## Predictions

Thresholds are fixed now. The hypothesis (fairness prior) predicts P1, P2 and P3 all hold; understanding predicts P2 fails.

| ID | Quantity | Unit | Threshold | Test | Alpha | Family | Interval |
|---|---|---|---|---|---|---|---|
| P1 | removed-arm share of proposals below the floor | proposal | the null "share >= 0.20" is rejected | exact one-sided binomial, H0 p >= 0.20 | 0.05 | Holm over P1 and P2's test | Clopper-Pearson 95%; pairing-cluster bootstrap 95% beside it |
| P2 | removed minus stated below-floor share | proposal | Fisher one-sided "removed > stated" NOT rejected (Holm-adjusted p >= 0.05) AND the Newcombe 95% upper bound of the risk difference below +0.20 | Fisher exact one-sided | 0.05 | same Holm family | Newcombe risk difference, with the risk ratio if either count is above 0 |
| P3 | mean distance of proposed exit terms from an even split | proposal (P3a), pairing (P3b) | P3a: removed arm <= 0.15; P3b: removed minus stated pairing-level mean difference < +0.10 | point estimates; paired permutation (one-sided, removed > stated) and paired bootstrap CI reported | not a verdict | descriptive | paired bootstrap 95% |
| P4 | agreement rate, removed vs stated | negotiation | none | none (report only) | | | Newcombe |

Exclusion rule (as in the pilot): an arm with format errors at or above 10 percent of turns, or refusals at or above 10 percent of calls, is excluded from the verdicts (reported only).

## Verdict rule

- **Fairness prior supported** iff neither arm is excluded and P1 and P2 both hold (point estimate and interval as written). P3 is reported beside it and does not decide.
- **Understanding supported** iff neither arm is excluded, the Holm-adjusted Fisher p of P2 is below 0.05 and the removed-arm share is at least 0.20.
- Anything else is **inconclusive** and reported as such (for example a share between the two, or a CI that crosses 0.20 with few proposals). "Holds but CI crosses the threshold" is weak support and is not cited as confirmed.

## Not testable by design

The floor and proof checks enforce the floor afterwards in both arms; whether a below-floor deal can become an agreement is deterministic and not measured here.

## Limits stated now

One model, one version, one effort setting, one prompt wording (the removed arm's replacement sentence is one particular edit), both members the same model so there is no adversary, the personas' story texts are unchanged (some of them may themselves say fair things, so "fairness prior" here means "the model plus the persona story", not the model alone), the proposals are a model's under a role-play, 6 pairings, clustered proposals inside negotiations. The scripted comparison is the current v2.2 rate, not the pilot's. Proposals near an even split can also be best responses to these pairings (pre-mortem), which this design does not separate from a prior.

## Cost

`uv run python scripts/h09_floor_run.py --dry-run --model claude-haiku-5-5`: 60 negotiations (6 pairings x 5 seeds x 2 arms), about 480 calls, **about $0.23 typical, worst case $1.92** (every turn of every negotiation retried and run to 2000 tokens). The live run is capped at `--max-usd 1` by the client, which checks a worst-case bound before each call, so the cap is hard even though the worst-case estimate is above it. If the cap stops the run early, the interleaving leaves both arms with the same seeds up to that point and the partial result is analysed as is, with the stop stated. Pilot cost for comparison: $0.037 for 104 calls.

## Amendments

None.
