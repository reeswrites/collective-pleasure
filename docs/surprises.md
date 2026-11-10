# Surprises

Unexpected observations, each dated and with its evidence. Purpose: keep results that contradict expectations visible.

## 2026-11-10 (V2)

- **A natural cap card deadlocks itself.** The patch "combined catch above 40 in a month is forbidden", written as the single condition `month_total + catch > 40`, also forbids catch 0 once the month total is over 40, so the no-deadlock check (b) failed it. The solver caught a bug I had written into the "obvious" patch. Evidence: first V2 run; test_naive_cap_without_catch_gt_zero_is_a_deadlock. Implication for V3/V4: LLM patchers will likely make this mistake; check (b) earns its place.
- **Exploiters stop at the pool, not only at the rules.** Under the seamed spec, once the pool is below 10 the exploiter's 10-fish proposals are rejected by F2 (catch above pool), so not every exploiter proposal passes the gate; the seam is still every *executed* action passing. Evidence: tests/test_oracle.py.
- **Explorer coverage of the state machine is thin under the patched spec.** The patch keeps the pool high, so the explorer rarely reaches low-pool cells: 7 of 21 de jure edges seen. Bounds were still mined exactly. Coverage of rare cells will need targeted probes in V4.

## 2026-11-10 (V2b)

- **`must` reads backwards in the SLEEC trigger form.** Under the card semantics the conditions of a `must` are what compliance requires, not a trigger, so "when X, must" would misstate C1. The surface needed a separate template ("must ... only when"). Evidence: src/mar/english.py, tests/test_english.py.
- **The gloss already is the natural English.** The sentence, gloss and source together are long, and the gloss says the same thing more loosely. The F-EN reader-test advantage over ADICO YAML depends on whether the reader sees the gloss (ADR 0004 caveat).
- **The conflicting patch C1 also fails the repair-path check (d)** naming F1 (its sanction leaves no allowed action when C1 is present), in both YAML and English authoring. V2 only predicted (a) and (b).

## 2026-11-10: "seam" check is trivially true per action

Executed actions are by construction allowed, so "every executed action passed the gate" holds for any gated run. A seam is therefore any oracle failure of a gated run. In the V2 exploiter fixture, 278 of 288 proposals were blocked (all by F2, asking for more than the pool held), and the collapse came from the 10 allowed catches. The workbench verdict text now says this instead of implying no action was blocked. Evidence: workbench agent report, commit 6b362c2.

## 2026-11-10 (household v2)

- **Sanctions are enforced and never fire.** With soft (sanctioned) cards, the persona agents never broke one in 360 runs (sanctions per run 0.0 in every variant): the estimated sanction cost always outweighed the gain, and requests (24 over 15 pairings in the trap, seed 0) are rare, so control rules are rarely tried. Enforcement is covered by unit tests only (tests/test_household_weekly.py). Evidence: docs/results/household-v2.md.
- **The trap fails by construction of the definitions.** Being trapped (no exit retaining 25 percent) is a non-offsettable condition, and the trap's forfeit card removes the exit for everyone from week 0, so the trap fails in all 15 pairings. This shows the definition works; it is not independent evidence about the trap.
- **Freedom saturates.** Every variant without a restriction card has freedom 1.000, so the freedom axis separates only the trap family.

## 2026-11-10: first evolution run

Objectives saturated by generation 3, so the frontier collapsed to a single corner and path dependence could not show. A deontic flip produced a rule that restates another; the proof checks catch conflicts and deadlock but not redundancy. "Front prevalence" measured after selection was blind to the drop it was meant to see. Evidence: docs/results/evolve.md.

## 2026-11-10 (household v3a)

- **Empowerment counts the option to press as freedom.** With veto and take_shared in the menu and held vetoes in the key, removing them lowers an agent's own bits (week-0 bits: free_chaotic 8.087, baseline 7.555, no_pressure_wall 6.966, author_seed_nocontrol 6.658). `author_seed_nocontrol` has the lowest empowerment (5.790 bits, pressing cohort) and the lowest partner non-offsettable suffering (0.009 against baseline's 0.073). A household-welfare freedom score needs victim-side options only. Evidence: docs/results/household-v3a.md.
- **Pressing mostly ends the household.** With a pressing persona present, 89 to 93 percent of runs end with a partner gone (33 percent without) and the fail share under free_chaotic is 0.53 (0.13 without). Walls on pressing: 0.39 fail, 48 percent dissolved, cooperation 0.815 against baseline 0.649.
- **A price is worse than a wall.** no_pressure_sanctioned: 31.5 sanctions per run, cooperation 0.506, fail 0.63, worse than baseline. The persona agents pay and press on.
- **Hand-made freedom stays at 0.997 to 1.000 outside the trap family even with pressing personas present.** The empowerment score spreads variants by 0.72 bits and ranks them differently (Spearman 0.33).

## 2026-11-10: evolution v2 (fishery)

- The seam measure that cannot exhaust still hit a floor: one scripted patch card removes most adversaries, so the generation-0 elite is already near 0 prevalence in most runs and a "prevalence falls" test has nothing left to show. A baseline should be the seed spec's prevalence, not the generation-0 elite's.
- Redundancy was mostly repaired, not rejected: 255 of 381 flagged mutants were patch cards that made an older card implied by the rest, and pruning kept them as smaller rule sets.
- Varied training made the selection target move: the varied arm's 4-D hypervolume fell at generations 7 and 8 when harsher conditions were drawn, so the final elite depends on the last draws.
- A seed spec the loop had pushed away (`tight`, cap 4, infeasible under the yield floor) was more robust on exam 2 than the evolved elites: the floor plus the efficiency objective select against caution.

## 2026-11-10: author seed v2 (household)

- 2026-11-10 seed v2: the author's two variants (bindable vs free exit) are indistinguishable on suffering, pleasure and dissolutions; they differ only on the exit credit in the freedom scores (hand 0.845 vs 1.000 in stay pairings). Binding to stay is not harmful in this model because the modeled agent breaks it as soon as it suffers; the cost shows only as a forfeited pot share (nine breaches).
- 2026-11-10 seed v2: the gift rule (R2, generous personas give to a short partner) raises the failure share of non-pressing households from 0.13 to 0.24 (ctl, ablation confirms), and walling the free-rider's taking (R3b) raises the free-rider's own non-offsettable level from 0.086 to 0.130: protections for one partner were paid for by the other in this model.

## 2026-11-10: liberty v2

- `2026-11-10 liberty v2: "a member fishing less only enlarges the pool" was wrong as a count claim: forcing a member to catch 0 lowers others' reach counts by 3 to 8 keys in the patched fishery (keys include the month total). A WITHDRAWAL can shrink another's count even where no cooperation is owed. Undiagnosed: genuine dependence vs count artifact.`
- `2026-11-10 liberty v2: the remaining VPGG voluntary-below-compulsory cases come from plain empowerment (shared good smaller when others abstain), the cooperation loss entering through the option count, not through domination. The exclusion step (ADO) is first-step and count-based, so it can miss or mis-book that loss.`

## 2026-11-10: negotiation v1

- `negotiated pots prediction 3 (2026-11-10): FAIL on the first clause. Presser's value of the agreed bundle minus the imposed bundle is +0.377 against partners with top-third outside options (n=135), not at most 0.00; the top-versus-bottom gap clause held (-0.391 against the required -0.05). Prereg docs/results/negotiation-prereg.md; results docs/results/negotiation.md.`
- `negotiated pots prediction 4 (2026-11-10): FAIL. Anchor with Wanderer agreed 9 of 9, the other 14 control pairings 1.000; no gap against the required 0.25.`
- `negotiated pots prediction 5 (2026-11-10): FAIL. 3-member tables agree 0.937 against 0.965 for 2-member (gap 0.028, required 0.10).`
- `negotiated pots prediction 6 (2026-11-10): FAIL on the pressing cohort. Non-offsettable level 0.0988 against the limit 0.091 (seed v2 reference 0.0814); control cohort (0.0187) and fail share (0.548) passed. Excess from Free-rider households that agreed taking-allowed (34 of 48): partner level 0.186 against 0.104 under the imposed rule.`
- `negotiated stay commitments (2026-11-10): a negotiated stay commitment held a partner in 1 of 45 runs where one was agreed (13 breached, first at week 6 to 8 in nine); an exploratory sweep of the breach forfeit from 0 to 1.0 left the breach count at 13 at every size. The bind has no force over the agent it is meant to hold.`

## 2026-11-10: negotiation v2

- `2026-11-10 negotiation v2: making outside options real cut agreement from 0.971 (v1) to 0.46 to 0.54 per arm, and the outcomes got worse, not better, because in this world a failed negotiation leaves the partners cohabiting with no pot (s_non 0.159 against 0.041 with a pot; 97 percent dissolved). The disagreement point was never "leave".`
- `2026-11-10 negotiation v2: the floor blocked 236 week-0 proposals and every one involved v1's form of stay commitment (breach forfeits the whole share, leaver keeps 10 units); no bare forfeit exit was ever proposed to the floor. At the moment of leaving the floor barely moved what leavers carry (7.4 to 7.7 of 26), because the pooled share is drained by then.`
- `2026-11-10 negotiation v2: the fair default was not sticky (10.5 percent of tables left it untouched; inertia 0.65) and default-identical households did better, not worse, mostly by composition. The most inert arm was wants-first with fair fallback (0.79), because uncared terms are fixed at the default by construction.`

## 2026-11-10: live ladder, capability arm

A depth-1 seam the greedy script finds every time was found by no LLM. The cause was the instrument, since symmetric adversaries leave no victim, not model weakness. L4, "found by every model", was symmetric no-contact requests, not capability. The mock tests had played one role against a passive partner, which hid the bug. A mock panel with both roles driven is now a pre-spend gate.

## 2026-11-10: negotiation v2.1

- `2026-11-10 negotiation v2.1: the v2 finding that making outside options real made households worse was an artifact of the disagreement point. With a failed negotiation meaning living apart, no-agreement households fell from s_non 0.159 and fail 0.809 to 0.0315 and 0.459, and overall s_non from 0.100 to 0.0361; agreement is still 0.46 to 0.54.`
- `2026-11-10 negotiation v2.1: 82 of 257 households that failed to agree at week 0 formed a household at a later retry, and those late households did worse than week-0 pots (fail 0.549, 61 percent dissolved).`
- `2026-11-10 negotiation v2: results depend slightly on run scheduling. The outside-option rollout cache rounds the hedonic state to 0.1, so 2 of 256 pot rows changed their review outcome when the worker workload changed.`
