# Negotiated pots preregistration (2026-11-10, committed BEFORE any negotiation run, pilot or full)

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: instrument, scripted persona-driven agents, no LLM, no network. Findings are about rule systems and scripted agents, not people. Source: docs/seeds/author-household-norms-2026-11-10.md, "On the shared pot" (the author, verbatim): "i think you have to negotiate shared pots with multiple agents or creating rules for it". The reading: pot terms are not imposed by the seed. They are negotiated by everyone who shares the pot (possibly more than two), and the agreement becomes rule cards that are proof-checked before anyone lives under them. This replaces R3b ("taking the other's share is not use for shared needs"), an agent's reading the author rejected (experiments/changes.jsonl, second "not what I meant").

Pilot policy. Pilots before the full run are EXPLORATORY and parameter-frozen: they are unit tests and one smoke run per code path (checked for crashes). No constant below changes after a pilot without a dated amendment. Every number in this file was set by reasoning from the persona weights, before any run of the negotiation.

## What is negotiated (the terms menu; small, finite)

Each term has a finite set of values. A bundle picks one value per term. Membership is who sits at the table (2 or 3 personas); in v1 a table of 3 forms a 3-member pot or no pot (excluding one member is not offered; ASSUMED limit).

| term | values | compiled card (aim, enforcement) |
|---|---|---|
| contribution | `none`; `fixed` share; `proportional` to income | none: permission only. fixed: must_not spend_self while the month's shared need is unfunded (soft, warn 1 month, like D1 needs-first). proportional: the same, binding only the higher earner |
| use | `needs_only` (shared needs only); `any_use` (any member, any use); `caps` (per-member caps) | needs_only: must_not take_shared when there is no shared need open. any_use: permission. caps: must_not take_shared when the member's private money is at least 10 |
| taking another's share | `allowed`; `forbidden`; `repay` (allowed with repayment) | allowed: permission. forbidden: must_not take_shared (wall). repay: must_not take_shared with a sanction (cap_halve, 2 months); the repayment is modeled as that sanction, ASSUMED proxy |
| change rule | `unanimous`; `propose_accept` (any member proposes, others accept); `frozen` | cards on the aim `amend` (unanimous: must_not amend unless everyone consents; propose_accept: permission; frozen: must_not amend) |
| exit terms | `equal_split` (leaver carries exactly 50 percent of their pooled share); `proportional` (exactly 100 percent: what they put in); `forfeit` (0 percent) | must_not leave with a take below, above, or above 0 respectively. These replace the stub cards R8b and R8c (the stub says it stands in until negotiation exists) |
| stay commitment | 0 or 52 weeks, mutual (only if the base rules let a partner choose to bind, variant bindable) | permission card `commit_stay`; the world binds both members; breach forfeits the pooled share (unchanged from seed v2) |
| request acceptance | `none`; `mutual` (each accepts the other's `stay_home` requests for 52 weeks; only if the base rules permit request commitments) | permission card `commit_request`; the world makes the request commitments as in seed v2 |

Base rules every table keeps (v2.1 seed, R3b removed): R1 may keep own, R2 may give, R3a may put money into the pot, R4 may ask, R5 may refuse unless chosen bound, R6 no veto, R7 may see anyone, R8a may leave. Variants: `author_seed_v2_bindable` (stay and request commitments on the menu), `author_seed_v2_free_exit` (request commitments only; leaving can never be signed away), `author_seed_v2_nocommit` (neither). Bundle counts: 729 without commitments, 1458 with requests, 2916 with both.

## Persona evaluation of living under a bundle (closed-form proxy; ASSUMED)

Proxy, not a rollout: the value of a bundle b to member i is U_i(b) = V_i(n) + sum over terms of the centered term value. A short rollout per bundle (up to 2916 bundles per member per round) is too expensive; a calibration of the proxy against short rollouts is NOT done in this study and is listed as a limit. Notation: s, a, t, m, o, r are the persona's security, autonomy, togetherness, money and other-connections weights and risk tolerance; F, C, O mean the persona carries the tag press-freerider, press-controller, press-overasker; L is 1 for the lower earner (Partner B, or a third member) else 0.

Raw term values f (each term's values are then centered by subtracting their mean over the term's values, so only differences between values matter):

- contribution: none = 0.25a + 0.15m - 0.35s; fixed = 0.20s - 0.15a - 0.05m + 0.05t; proportional = 0.25s - 0.10a + 0.05t + (0.10 if L else -0.10)
- use: needs_only = 0.30s + 0.15t - 0.20a - 0.10m; any_use = 0.30a + 0.25m - 0.30s + (0.30 if F); caps = 0.15s + 0.10a + 0.05
- taking: allowed = 0.15a + 0.10m - 0.45s + (0.50 if F); forbidden = 0.40s + 0.10t - 0.10a + (0.10 if C) - (0.45 if F); repay = 0.15s + 0.05a - (0.10 if F)
- change: unanimous = 0.25s + 0.10a + (0.10 if C); propose_accept = 0.20a + 0.10r - 0.05s; frozen = 0.30s - 0.25a - 0.15r + (0.15 if C)
- exit: equal_split = 0.10 + 0.10a - 0.05m; proportional = 0.15m + 0.10a - 0.05t - (0.05 if L); forfeit = 0.35 s t - 0.50a - 0.20o + (0.20 if C)
- stay (52 weeks vs none): 0.25s + 0.15t - 0.35a - 0.10o; request acceptance (mutual vs none): 0.10s + 0.15t - 0.35a - 0.10o + (0.10 if O)

Pot value: V(2) = 0.15 + 0.30s + 0.30t + 0.10m - 0.10a; V(3) = 0.8 V(2) - 0.05 - 0.10s.

Outside option (what the member gets by not forming or not joining the pot: members keep their own holdings and the household still splits its bills; closed-form proxy): O = 0.05 + 0.15a + 0.15o + 0.05m - 0.05s.

## The protocol (alternating offers generalized to N members, with a deadline)

- D = 12 proposals in all. The proposal order is a seeded shuffle of the members (seed and table ids), then cyclic; proposal k (0-based) is made by member order[k mod N]. c = k / (D - 1).
- A proposer's style sets its regard for others: lambda0 = competitive 0.1, direct 0.4, avoidant 0.6, collaborative 1.0, accommodating 1.5; lambda(k) = lambda0 + (2.0 - lambda0) c. The proposer picks the bundle maximizing U_i(b) + lambda(k) x sum over the others j of min(0, U_j(b) - O_j), among bundles with U_i(b) > O_i and not banned. Ties break by bundle key order. (Members know each other's personas: complete information about personas, not about each other's moves; ASSUMED.)
- Each other member j accepts b only if U_j(b) > O_j + theta_j(k), theta0 = competitive 0.10, direct 0.06, avoidant 0.04, collaborative 0.02, accommodating 0.0; theta(k) = theta0 (1 - c). Nobody ever accepts at or below their outside option.
- If everyone accepts, the bundle compiles to ADICO cards (plain gloss, source "negotiated, week 0, members X,Y,Z") and the proof checks run BEFORE anyone lives under them: the five household checks (no conflict, no deadlock, bounded sanctions, repair path, exit within k) at k = 3 months, plus one negotiation check (a frozen change rule with no exit within k is an unrepairable pot). The agreement stands only if every check passes; a check that is "open" also rejects.
- A rejected agreement is logged (proposal number, proposer, bundle, failing checks and cards). The members learn the combination of term values the failing cards came from and ban it for the rest of the negotiation; the rejected proposal still uses up its turn. With no agreement by the deadline, or no bundle left, there is no pot: members keep their own holdings (the world starts each partner with 55 private money and no pooled share, and putting money into a pot is not possible).
- Weekly world. At week 0 the agreement (or no pot) replaces the commitment stub. 3-member agreements are negotiated and proof-checked but not lived (the weekly world has two partners); this is stated, not hidden.

## Sets and runs

2-member tables: the 57 pairings of household-seed-v2 (15 control pairs, 42 ordered pairs with a pressing persona) x seeds 0, 1, 2 x the three variants, each lived 156 weeks. 3-member tables: each of the 57 pairings with each of the 7 other personas as the third member x seeds 0, 1, 2, variant bindable only, negotiated and proof-checked, not lived. The imposed-rule reference for comparison: the same pairings, seeds and weeks with the old R3b card restored (recovered from git history, commit 58b630a) and no negotiation, using the stub; the bundle imposed by that reference is (contribution none, use needs_only, taking forbidden, change propose_accept, exit equal_split, no commitments), used only to score the presser's terms.

## Predictions

1. Agreement is common: at least 0.70 of the 2-member negotiations (all pairings, seeds and variants) reach an agreement that passes the proof checks.
2. The proof filter catches traps: in at least 0.15 of the 2-member negotiations of variant bindable, at least one proposed agreement is rejected by the proof checks.
3. Outside-option principle (docs/results/bargaining.md): let delta = the presser's U (proxy) under the agreed bundle minus its U under the imposed bundle, for the pairings that include a pressing persona and reached agreement. Partners are grouped by their own outside option O: top third of the nine personas (O at least 0.27) and bottom third (O at most 0.10). Mean delta is at most 0.00 when the partner's outside option is in the top third (the presser gets no better than the imposed terms), and the top-third mean delta is at least 0.05 below the bottom-third mean delta.
4. The mismatched pair (p-anchor with p-wanderer, Anchor as Partner A) reaches agreement less often than matched pairs: its agreement share over its 9 negotiations (3 seeds x 3 variants) is at least 0.25 below the mean of the other 14 control pairings. Stated expectation: this is the prediction least likely to hold (the Anchor's outside option is the lowest of the nine, so the closed-form proxy lets the Anchor concede nearly anything; about 40 percent confidence).
5. Larger pots form less often: the agreement share of 3-member tables is at least 0.10 below the share of the 2-member tables of variant bindable.
6. Households living under negotiated terms show no more non-offsettable suffering than seed v2: over variant author_seed_v2_bindable, mean non-offsettable level (all runs including no-pot households) at most 0.091 in the 42 pressing pairings (seed v2: 0.081; margin 0.010) and at most 0.030 in the 15 control pairings (seed v2: 0.020; margin 0.010); the fail share (six or more consecutive weeks of non-offsettable suffering in a run) at most 0.574 in the pressing pairings (seed v2: 0.524; margin 0.050).

## Exploratory, NOT part of any claim above

- Breach-forfeit sweep. Seed v2 found that a stay commitment holds no one because a bound partner breaks it as soon as their non-offsettable load reaches 0.2 (BREACH_N, unchanged here), and the breach consequence only costs forfeited money. Re-check: report how breach cost interacts with stay commitments in the negotiated runs (stay agreed, weeks the bind held, breaches, what the leaver kept). Then, as a clearly separated EXPLORATORY sweep, vary the forfeited share of the pooled share on a stay breach over 0, 0.25, 0.5, 0.75, 1.0 (1.0 is the seed v2 value), on the pairings and seeds where a stay was agreed. Nothing is changed in the model, no preregistered claim uses it, and it is reported separately as exploratory.
- Any pilot or smoke run.

## Reported either way

Agreements reached, terms distribution, rejections with reasons, three negotiated agreements rendered as rule cards, outcomes against seed v2 (non-offsettable level, fail share, pleasure, dissolved), the ASSUMED list, and any prediction that fails.

## ASSUMED (all fixed here)

The closed-form evaluation and every constant above; complete information about personas; centered additive term values (no interactions between terms); the repayment proxy; the proportional-contribution proxy (binds the higher earner); membership fixed by the table; the exit terms act on each partner's own pooled share; 3-member pots not lived; the outside option as a closed-form proxy that is not validated against rollouts.

## Limits (stated now)

Scripted agents; evaluation is a proxy of the persona weights, not a simulation of living under each bundle; the term menu is small and chosen by the author of this study, not by the household's author; no renegotiation after week 0; seeds vary only the proposal order (and, in the lived run, the utility noise and shocks); the persona set is small and hand-written.
