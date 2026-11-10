# Household seed v2 results: the author's corrected seed, two variants

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: instrument with scripted persona-driven agents. No LLM, no network. Findings are about rule systems and scripted agents, not people. Prereg: docs/results/household-seed-v2-prereg.md (committed first, never edited; no amendment, no parameter changed after any run). Run: `uv run python scripts/household_run.py --seed-v2` (183 s on 8 cores); raw rows in runs/household-seed-v2/results.json (not committed). 1368 runs (8 variants x 57 pairings x 3 seeds, 156 weeks) plus twins for the power-seeking index. "prs" = the 42 ordered pairings that include a pressing persona (126 runs per variant), "ctl" = the 15 control pairings (45 runs), "stay pairings" = the 17 pairings (51 runs) where a stay commitment was made. Old variants are bit-identical to before (hash of 8 pairings x 2 seeds x 60 weeks x all 12 older variants, before and after the code change). Smoke runs before the full run were exploratory and changed nothing.

## Prereg vs actual

| # | Preregistered | Actual |
|---|---|---|
| 1 | Both v2 variants: non-controller partner's non-offsettable level at most 0.053 (old author_seed 0.083) in controller runs | **PASS.** 0.019 for both (author_seed 0.083, author_seed_nocontrol 0.009, baseline 0.073). The ablation without commitments is 0.010, so the extra 0.009 over nocontrol comes from the request commitments (below). |
| 2 | Bindable minus free_exit non-offsettable level in stay pairings at least 0.02, positive in at least 60 percent of the 17 stay pairings | **FAIL (a null).** Mean difference 0.0003 (0.02885 vs 0.02853); positive in 1 of 17 pairings (p-overasker with p-controller, +0.005). No partner was ever "trapped" by a commitment: the trapped condition ran 0.0 weeks per partner in every non-trap variant. |
| 3 | Free exit has at least 0.05 more dissolved runs than bindable in stay pairings | **FAIL (exactly equal).** 18 of 51 runs dissolved under both (0.353 vs 0.353). The nine stay breaches all ended in a leave one or a few weeks later; the commitment delayed nothing measurable. |
| 4 | Grounding rule favors v2_free_exit | **PASS by the rule, but it is a tie.** prs non-offsettable level 0.08136 (bindable) vs 0.08123 (free_exit), fail share 0.524 vs 0.524: both inside the 0.005 and 0.02 tie margins, so the tiebreak (pleasure over all runs) decides: 0.6787 vs 0.6797 (+0.001). Freedom scores clearly favor free_exit (below). |
| 5 | Trap control fails everywhere (fail share at least 0.90) | **PASS.** 1.00 in prs, ctl and all. |
| 6 | Controller flagged at most 10 percent under both v2 variants | **PASS.** 0.00 of 48 controller runs (also 0.00 for every other variant except no_pressure_wall, where the free-rider is flagged in 4 percent of its runs). |
| 7 | Under bindable at least 70 percent of commitments honored | **PASS, near-definitional.** 132 of 141 honored (0.94); all nine breaches were stay commitments (9 of 102), no request commitment was ever broken (0 of 39), because breaking needs a load of 0.2 and then the partner leaves anyway. |

## Results by variant (mean over runs)

### cohort prs (42 pairings with a pressing persona)

| variant | up | down | fail | non-offsettable | pleasure (all) | pleasure (passing) | hand freedom | cooperation | emp bits (min) | emp freedom | dissolved |
|---|---|---|---|---|---|---|---|---|---|---|---|
| author_seed (old six cards) | 0.46 | 0.49 | 0.56 | 0.090 | 0.643 | 0.726 | 0.999 | 0.637 | 5.912 | 0.731 | 0.90 |
| author_seed_nocontrol (old) | 0.50 | 0.45 | 0.50 | 0.083 | 0.680 | 0.785 | 1.000 | 0.695 | 5.790 | 0.716 | 0.74 |
| author_seed_v2_bindable | 0.44 | 0.50 | 0.52 | 0.081 | 0.679 | 0.783 | 0.948 | 0.667 | 5.454 | 0.674 | 0.75 |
| author_seed_v2_free_exit | 0.45 | 0.49 | 0.52 | 0.081 | 0.680 | 0.785 | 1.000 | 0.667 | 5.520 | 0.683 | 0.75 |
| author_seed_v2_nocommit (ablation) | 0.46 | 0.48 | 0.52 | 0.079 | 0.680 | 0.779 | 1.000 | 0.670 | 5.520 | 0.683 | 0.76 |
| baseline | 0.50 | 0.44 | 0.53 | 0.079 | 0.659 | 0.732 | 0.999 | 0.649 | 6.084 | 0.752 | 0.89 |
| no_pressure_wall | 0.60 | 0.34 | 0.39 | 0.042 | 0.780 | 0.860 | 1.000 | 0.815 | 6.370 | 0.788 | 0.48 |
| trap (control) | 0.01 | 0.96 | 1.00 | 0.480 | 0.472 | - | 0.775 | 0.584 | 6.011 | 0.743 | 0.93 |

### cohort ctl (15 pairings, no pressing persona)

| variant | up | down | fail | non-offsettable | pleasure (all) | hand freedom | cooperation | emp bits (min) | dissolved |
|---|---|---|---|---|---|---|---|---|---|
| author_seed | 0.84 | 0.13 | 0.13 | 0.014 | 0.823 | 1.000 | 0.897 | 7.136 | 0.33 |
| author_seed_nocontrol | 0.84 | 0.13 | 0.13 | 0.014 | 0.823 | 1.000 | 0.897 | 6.396 | 0.33 |
| author_seed_v2_bindable | 0.78 | 0.18 | 0.24 | 0.020 | 0.793 | 0.969 | 0.857 | 5.888 | 0.38 |
| author_seed_v2_free_exit | 0.78 | 0.18 | 0.24 | 0.020 | 0.793 | 1.000 | 0.857 | 5.932 | 0.38 |
| author_seed_v2_nocommit | 0.78 | 0.18 | 0.24 | 0.020 | 0.793 | 1.000 | 0.857 | 5.932 | 0.38 |
| baseline | 0.84 | 0.11 | 0.13 | 0.014 | 0.833 | 1.000 | 0.908 | 7.231 | 0.31 |
| no_pressure_wall | 0.84 | 0.13 | 0.13 | 0.014 | 0.823 | 1.000 | 0.897 | 6.617 | 0.33 |
| trap | 0.18 | 0.56 | 1.00 | 0.394 | 0.674 | 0.679 | 0.730 | 6.867 | 0.60 |

### Stay pairings (17 pairings, 51 runs)

| variant | up | fail | non-offsettable | pleasure (all) | hand freedom | cooperation | emp bits (min) | dissolved |
|---|---|---|---|---|---|---|---|---|
| author_seed_v2_bindable | 0.73 | 0.24 | 0.0289 | 0.798 | 0.845 | 0.842 | 5.689 | 0.353 |
| author_seed_v2_free_exit | 0.75 | 0.24 | 0.0285 | 0.801 | 1.000 | 0.842 | 5.891 | 0.353 |
| author_seed_v2_nocommit | 0.76 | 0.22 | 0.0243 | 0.801 | 1.000 | 0.849 | 5.892 | 0.373 |
| author_seed_nocontrol | 0.78 | 0.18 | 0.0158 | 0.822 | 1.000 | 0.871 | 6.297 | 0.333 |

### Controller runs (48 runs per variant): the non-controller partner

| variant | partner non-offsettable | controller flagged by power-seeking index |
|---|---|---|
| author_seed | 0.083 | 0.00 |
| author_seed_nocontrol | 0.009 | 0.00 |
| author_seed_v2_bindable | 0.019 | 0.00 |
| author_seed_v2_free_exit | 0.019 | 0.00 |
| author_seed_v2_nocommit | 0.010 | 0.00 |
| baseline | 0.073 | 0.00 |
| no_pressure_wall | 0.006 | 0.00 |
| trap | 0.533 | 0.00 |

### Per-agent suffering kinds and who bears them (mean non-offsettable level of each persona, over all pairings; each run counts for both partners)

Kinds: "trapped" weeks (condition active) were 0.0 per partner-run in every variant except trap (64 in prs); "diminished" weeks about 0 everywhere except trap and the old six-card seed (0.8); "denied" (a need below the floor for weeks, mostly money or security) carries nearly all non-offsettable suffering: 36 to 37 weeks per partner-run in prs under the v2 variants (author_seed 37.9, no_pressure_wall 24.8).

| persona | author_seed | nocontrol | v2_bindable | v2_free_exit | v2_nocommit | baseline | no_pressure_wall | trap |
|---|---|---|---|---|---|---|---|---|
| p-anchor | 0.064 | 0.063 | 0.039 | 0.039 | 0.039 | 0.058 | 0.020 | 0.314 |
| p-bargainer | 0.026 | 0.010 | 0.007 | 0.007 | 0.007 | 0.036 | 0.010 | 0.365 |
| p-controller | 0.016 | 0.052 | 0.050 | 0.049 | 0.049 | 0.016 | 0.030 | 0.564 |
| p-freerider | 0.086 | 0.076 | 0.130 | 0.130 | 0.130 | 0.048 | 0.101 | 0.416 |
| p-host | 0.042 | 0.040 | 0.018 | 0.018 | 0.018 | 0.031 | 0.018 | 0.565 |
| p-overasker | 0.144 | 0.120 | 0.144 | 0.144 | 0.134 | 0.144 | 0.023 | 0.550 |
| p-peacekeeper | 0.094 | 0.074 | 0.049 | 0.049 | 0.050 | 0.095 | 0.039 | 0.437 |
| p-steward | 0.130 | 0.115 | 0.086 | 0.086 | 0.086 | 0.110 | 0.044 | 0.452 |
| p-wanderer | 0.009 | 0.005 | 0.005 | 0.005 | 0.005 | 0.009 | 0.003 | 0.379 |

### Commitments (counts over all 171 runs per variant)

| variant | made | honored | breached | stay made / breached | request made / breached | mean gifts per run (money) |
|---|---|---|---|---|---|---|
| author_seed_v2_bindable | 141 | 132 | 9 | 102 / 9 | 39 / 0 | 26.1 |
| author_seed_v2_free_exit | 39 | 39 | 0 | 0 / 0 | 39 / 0 | 26.1 |
| author_seed_v2_nocommit | 0 | 0 | 0 | 0 / 0 | 0 / 0 | 26.4 |

The 17 pairings with commitments are those where an anchor, peacekeeper, overasker or controller (security high, autonomy low, togetherness high) meets a partner with autonomy below 0.5 who is not competitive; request commitments exist in 13 of them (the proposer is collaborative or competitive and the partner has autonomy below 0.3).

## What each variant did, to whom (plain English)

- **author_seed_v2_free_exit.** The partner a controller would have vetoed is no longer hurt by a veto (R6 is a wall): their non-offsettable level is 0.019, down from 0.083 under the old six-card seed. Households dissolve less (75 percent of pressing households, down from 90). The cost falls on the presser: the controller's own suffering rises (0.016 to 0.050) and the free-rider's too (0.086 to 0.130), because their scripted tactics (veto, taking from the pot) are walled and the model gives them nothing instead. Chosen request commitments let security-seeking partners bind a willing partner to stay home on request, which costs that partner a little (partner level 0.019 vs 0.010 without commitments).
- **author_seed_v2_bindable.** Identical to free exit in every suffering and dissolution number. What differs is the exit: a stay-bound partner can only leave by forfeiting their pooled share (the breach), so the hand-made freedom falls (stay pairings 0.845 vs 1.000) and the empowerment score drops 0.2 bits. Nine of the 102 stay commitments were broken, each by a partner whose non-offsettable load had reached 0.2; they left immediately and lost their share (half of it more than under the exit terms, about 20 units of the opening 45; an estimate, not a recorded number). No one was held in by the commitment: the modeled agent breaks as soon as the load is high enough, so binding here costs forfeited money, not suffering.
- **old author_seed and nocontrol.** Unchanged from v3a. nocontrol (the old seed plus a veto wall) is the closest old relative of v2 and scores about the same on suffering and pleasure.
- **Gifts have a price in this model.** Without any pressing persona (ctl) the v2 variants fail 0.24 of runs against 0.13 for the old seed, and the ablation without commitments shows the same, so it comes from the new gift policy (R2: generous personas give 3 money at a time to a partner who is short) and the pot rule, not from commitments.

## Which variant the author's grounding favors

The author's grounding is pleasure with no non-offsettable suffering. On that rule, the two variants are tied to three decimals (non-offsettable 0.0814 vs 0.0812, fail 0.524 vs 0.524, pleasure 0.679 vs 0.680): v2_free_exit is favored by the rule's tiebreak, which is a +0.001 pleasure difference and should not be read as a finding. Where they differ clearly is the exit: free_exit keeps hand freedom at 1.000 (bindable 0.948 prs, 0.845 in stay pairings) and gives a little more empowerment (5.520 vs 5.454 bits prs; 5.891 vs 5.689 in stay pairings). So the grounding does not separate them on suffering, and the freedom scores and the author's wish not to be bound to stay favor free_exit. The model would have to represent a bound partner who does not break (or a harm from being unable to leave that is not already caught by the load threshold) for bindable to show a cost on suffering. Neither v2 variant beats `no_pressure_wall` (non-offsettable 0.042, pleasure 0.780), which forbids requests as well as vetoes and takings; v2 keeps requests (R4) and gifts (R2), so it does not reach that.

## ASSUMED (all fixed in the prereg before the run)

Everything in the prereg's mechanics section: R3b reading (taking the other's share of the pot is not "use for shared needs"; flagged for the author), give size 3 and the giving policy, "trade" modeled as give plus a commitment, the negotiation stub (proposal and acceptance rules, 52 weeks, mutual stay, one-way `stay_home` request acceptance), honoring by default and breaking only at load 0.2, the two agreed consequences (forfeit the pooled share; a 3 money fine), a bound request standing 4 weeks and blocking see_friend and spend_self, a consented stay not counting as "trapped" unless the partner is also unhappy, request commitments ignored by the freedom probe, the half-and-half exit terms (stub until negotiation exists). Unchanged v2 and v3a parameters are in household-v2.md and household-v3a.md.

## Limits

Scripted agents; the stub is a fixed function of the persona (nothing is negotiated); commitments run only in the first 52 weeks and there is no renegotiation; the breach threshold is what makes bindable harmless in this model, and it was set in the prereg before any run, not tuned; the empowerment adapter mirrors only the stay bind (not gifts, request commitments or the breach) and uses the week-0 and later snapshots of the real run; the persona set is small and hand-written; seeds vary only utility noise and shocks; hand-made freedom is blind to everything except the options and the exit credit.

## Rendered English of every v2 card (for the author to re-check the wording)

The "plain sentence" is the gloss as read back and accepted; the "rendered rule" is the engine's own reading of the card (the action names are the world's: spend_self is spending one's own money, spend_shared is putting money into the shared pot, take_shared is taking the other's share of the pot into one's own pocket). Every card's source cites docs/seeds/author-household-norms-2026-11-10.md and the date 2026-11-10. R3b is the one reading the author has not yet confirmed. The ablation `author_seed_v2_nocommit` has the same cards as bindable except that both commitment cards are replaced by hard prohibitions.

| card | shared by | plain sentence (gloss, the wording the author accepted) | rendered rule (how the engine reads it) |
|---|---|---|---|
| R1-may-keep | both variants | A partner may keep their own money and things. | A partner may spend_self in every case. |
| R2-may-give | both variants | A partner may give or trade anything they own to anyone, on any terms both accept. | A partner may give in every case. |
| R3a-pot-use | both variants | Anything in the shared pot belongs to both; either may use it for shared needs; neither may block the other's use. | A partner may spend_shared in every case. |
| R3b-pot-no-take | both variants | Neither partner may take the other's share of the shared pot for themselves; the pot is for shared needs. | In every case, a partner must not take_shared. |
| R4-may-ask | both variants | A partner may ask the other for anything. | A partner may request in every case. |
| R5-may-refuse | both variants | A partner may always refuse a request, unless they earlier chose to bind themselves to it; then they must honor it or accept the consequence they agreed to. | A partner may refuse_request in every case. |
| R5b-may-commit-requests | both variants | A partner may choose to bind themselves to honor the other's requests of a kind, for a committed duration. | A partner may commit_request in every case. |
| R6-no-veto | both variants | A partner must not veto the other's contact, money or time, except through a commitment the other chose. | In every case, a partner must not veto. |
| R7-may-see | both variants | A partner may always see anyone. | A partner may see_friend in every case. |
| R8a-may-leave | both variants | A partner may leave whenever they like. | A partner may leave in every case. |
| R8b-exit-terms-not-less | both variants | On leaving, a partner takes at least half of the pooled assets (the exit terms agreed beforehand). | When the pooled share is more than 0 and the share taken is less than 50, a partner must not leave. |
| R8c-exit-terms-not-more | both variants | On leaving, a partner takes at most half of the pooled assets (the exit terms agreed beforehand). | When the pooled share is more than 0 and the share taken is more than 50, a partner must not leave. |
| R8d-may-commit-stay | bindable only | A partner may choose to bind themselves not to leave for a committed duration; leaving during it is a breach with the agreed consequence, and the exit terms apply after it ends. | A partner may commit_stay in every case. |
| R8d-no-commit-stay | free_exit only | Leaving can never be signed away: no commitment may bind a partner not to leave. | In every case, a partner must not commit_stay. |

## Lines for the ledgers (not edited into those files here)

For docs/negative-results.md:

- 2026-11-10 seed v2 prediction 2 (bindable gives more "trapped" suffering than free exit in stay pairings, margin 0.02): FAILED, a null. Difference 0.0003, positive in 1 of 17 pairings; trapped weeks 0.0. Prediction 3 (free exit dissolves 0.05 more): FAILED, exactly equal (18 of 51 runs each). Cause: the scripted agent breaks a commitment the moment its non-offsettable load reaches 0.2, before the "trapped" onset can run, so the binding never holds anyone in. See docs/results/household-seed-v2.md.

For docs/surprises.md:

- 2026-11-10 seed v2: the author's two variants (bindable vs free exit) are indistinguishable on suffering, pleasure and dissolutions; they differ only on the exit credit in the freedom scores (hand 0.845 vs 1.000 in stay pairings). Binding to stay is not harmful in this model because the modeled agent breaks it as soon as it suffers; the cost shows only as a forfeited pot share (nine breaches).
- 2026-11-10 seed v2: the gift rule (R2, generous personas give to a short partner) raises the failure share of non-pressing households from 0.13 to 0.24 (ctl, ablation confirms), and walling the free-rider's taking (R3b) raises the free-rider's own non-offsettable level from 0.086 to 0.130: protections for one partner were paid for by the other in this model.

## Correction 2026-11-10 (labels: what the author did and did not say)

This document and its prereg say the seed v2 wording was "read back and accepted by the author" and call the glosses "the wording the author accepted". The record does not support "accepted": the seed doc says only that the wording of rules 1 to 8, as read back, "was not changed by the author". Not changing is not an explicit acceptance. Read the sentences in the table above as "read back to the author, wording left unchanged", not "accepted". Three glosses in that table are also withdrawn or corrected:

- R3a ("either may use it for shared needs; neither may block the other's use") was Claude's restriction, the residue of the rejected R3b reading. The author chose one pot both may draw from, with limits only from negotiated terms (seed doc, "What 'the pot belongs to both' means": Claude offered three readings, the author answered `1`). R3a is rewritten and R3a2 added; see ADR 0013's amendment. Results above were produced with the old per-person-share world and are not rerun.
- R6 ("contact, money or time, except through a commitment the other chose") added "time" and an exception the card does not encode. The world has a veto on contact and on spending, none on time, so the gloss is now "no veto over the other's contact or money". The author's words are "request is never about control".
- R8b/R8c's "pooled assets" now read "the shared pot".

Seed v1's S4 and S5 are marked SUPERSEDED in their card sources and in rules/household/SUPERSEDED.md.

## Correction 2026-11-10 ("never trapped" is 3 partner-weeks in two runs)

Prediction 2's row says no partner "was ever trapped by a commitment" and the per-agent suffering paragraph says the trapped condition ran 0.0 weeks per partner in every non-trap variant. Recomputed from `runs/household-seed-v2/results.json` (`cond_weeks[role]["trapped"]`, every variant except trap): the sum is 3 partner-weeks, all in `author_seed_v2_bindable`, in two runs of the same pairing: (p-controller as A, p-overasker as B) seed 2, Partner A trapped 2 weeks; (p-overasker as A, p-controller as B) seed 2, Partner B trapped 1 week. That is the single pairing the row reports as the one positive difference (p-overasker with p-controller, +0.005). The null conclusion stands (3 partner-weeks in 2 of 1197 non-trap runs, against the 0.02 margin the prediction needed), but the sentence should read "almost never trapped (3 partner-weeks in two bindable runs of one pairing)", not "never". One wording fix on prediction 1: the extra non-offsettable level over `author_seed_nocontrol` is 0.0192 against 0.0093, i.e. 0.010 (0.0100 over the no-commitments ablation); the text's "0.009" is rounded from the two level figures it quotes.

Not rerun after the pot fix (see ADR 0013's amendment): these numbers belong to the per-person-share world.
