# Negative results

Experiments or checks that failed to show the predicted effect, reported as findings (see kill criteria in RATIONALE.md section 9). Purpose: negative results are recorded, not hidden.

## 2026-11-10 (V2)

- **First-run failure of the scripted patch.** Prediction 3 expected the per-month cap card to pass all four patch checks. As first written (single condition, no `catch > 0`), it failed no-deadlock (b) and repair path (d) at the stated bound, naming P1 (and F1 for d). Cause: a real bug in the card. Fixed and recorded; the prediction is left as written in docs/results/v2-prereg.md. See docs/results/v2.md.

## 2026-11-10 (V2b)

- **The SLEEC-style form did not carry over uniformly.** The "when <condition> then <obligation> unless <exception>" form fits only `must not`. `must` and `may` needed their own templates, `unless` and `or` could not be expressed, and arithmetic conditions read poorly. All four preregistered checks passed (docs/results/v2b.md); this is a naturalness limit, not a meaning loss. No claim yet that readers do better with it.

## 2026-11-10 (VPGG rediscovery)

- **Oscillation clause of prediction 3 failed.** In the voluntary public goods game (Hauert et al. 2002; N=5, r=3, sigma=1, 20 seeds) cooperator share held at 0.263 (paper's equilibrium 0.27) and payoff at 0.984 (about sigma), but its standard deviation over time was 0.013 to 0.020 against a preregistered floor of 0.05 in at least 18 seeds. By the committed verdict rule the pipeline did NOT rediscover the full result. Cause unknown: the amplitude floor was a guess, or the assumed update knobs (5-round payoff averaging, revision rate 0.1) damp the cycle, or the model does not cycle. Not retuned; see docs/results/vpgg.md.

## 2026-11-10 (household v2)

- **No freedom/cooperation trade-off appeared.** Goals, weekly clocks and enforced sanctions did not create one: the frontier is baseline and needs_duty (freedom 1.000, cooperation 0.908), which dominate every other variant; the trap family is lower on both. Prediction 1 failed. See docs/results/household-v2.md.
- **author_seed equals baseline on upward share (0.844 each).** Prediction 3 failed. The six cards are permissions plus an even-split exit, which the persona agents rarely meet as a constraint.
- **The Anchor and Wanderer pair is not the hardest** (strictly lowest in 0 of 8 variants). Prediction 4 failed; the pair is upward in every non-trap variant.

## 2026-11-10: bargaining rung 1, prediction 4b

Allowing exit lowered mean cooperation by 0.019 over a heuristic-strategy mix, outside the committed 0.01 slack. The exit-allowed frontier advantage holds only for equilibrium players. Not retuned. Evidence: docs/results/bargaining.md.

## 2026-11-10: first evolution run (fishery, scripted agents)

The seam-curve fall is mostly exhaustion of a finite set of seam keys (agent mix x finding kind), so first-seen counts had to fall; it is not evidence of convergence. The evolved elite did not beat the seed spec on the held-out final exam (seam_free 0.25 vs 0.25; regrowth x1.5, 8 months, unseen agent mixes): it overfit the training conditions. Evidence: docs/results/evolve.md.

## 2026-11-10: household v3a, predictions 1, 3 (primary) and 4

(1) No preregistered-size freedom/cooperation trade-off: the only opposite-direction frontier pair (needs_duty vs no_pressure_wall) differs by 0.136 bits, below the 0.5 committed. (3) The author seed with a no-veto card did not raise the non-controller partner's empowerment: 6.087 against baseline's 6.411 (-0.324 bits, committed at least +0.5); it did cut that partner's non-offsettable suffering (0.009 against 0.073). (4) The power-seeking index flagged the controller in 0 of 240 permissive runs (committed at least 60 percent): the controller loses empowerment against its twin in every run (mean -1.77 bits) because pressing dissolves the household. Predictions 2 and 5 held but are near-definitional. Not retuned. Evidence: docs/results/household-v3a.md.

## 2026-11-10: evolution v2 (fishery)

- **Prediction 1 failed.** The elite's exploit prevalence against a fresh audit sample fell by >= 0.15 in only 7 of 18 runs (needed 10). Most non-falling runs started near 0 because generation 0's best of 8 mutants already contained a patch card that blocks most adversaries; in the varied arm candidate prevalence rose at the end. Evidence: docs/results/evolve-v2.md.
- **Prediction 5 failed in one arm.** Under fixed training all three seed rule sets ended at the same mean reference vector (distance 0.023); path dependence showed only under varied training (0.36).
- **Varied training did not remove overfitting.** The exam-2 gap shrank (mean 0.205 on sustainability and seam_free), but 13 of 18 elites still failed at least 4 of 5 hostile exam-2 mixes, the effect sits in 5 of 9 pairs, and the `tight` seed spec beat the fixed-arm elites on exam 2.

## 2026-11-10: liberty score v1

VPGG predictions V1 and V2 failed: voluntary beat compulsory on liberty in only 4 of 15 compositions, lost in 10, tied in 1 (summed difference -19.6 bits, negative at every weight tried). Cause: the domination count treated other members' ability to abstain as domination, so compulsory rules scored zero domination. Fishery F3 also failed (liberty widened the seat-order gap). The author ruled that others leaving or withdrawing cooperation is not a loss of freedom ("it was only possible thru agreement in the first place"); liberty v2 implements that. Evidence: docs/results/liberty.md.

## 2026-11-10: author seed v2 (household)

- 2026-11-10 seed v2 prediction 2 (bindable gives more "trapped" suffering than free exit in stay pairings, margin 0.02): FAILED, a null. Difference 0.0003, positive in 1 of 17 pairings; trapped weeks 0.0. Prediction 3 (free exit dissolves 0.05 more): FAILED, exactly equal (18 of 51 runs each). Cause: the scripted agent breaks a commitment the moment its non-offsettable load reaches 0.2, before the "trapped" onset can run, so the binding never holds anyone in. See docs/results/household-seed-v2.md.

## 2026-11-10: liberty v2

- `liberty v2 VPGG V1 (2026-11-10): FAIL. Interference/withdrawal removed the domination term (v1 sum -19.6 bits to v2 +5.263), strict 11/15, but vol < comp reversed in CCLL (2.585 vs 3.170) and CDLL (2.000 vs 3.000). Cause: plain count-based reach is already lower under voluntary in both (7 vs 9, 4 vs 9), not domination or ADO. Prereg docs/results/liberty-v2-prereg.md; results docs/results/liberty-v2.md.`
- `liberty v2 fishery F2/F3 and prediction 4 (2026-11-10): F2 FAIL 12/16 (patched exploiter 1 is 0.000, not above seamed 0.000); F3 equality-with-v1 claim FAIL (12/40 agent-months differ, ADO from catch 0); prediction 4 FAIL 7/15 vs threshold 8 (compulsory 4/15).`

## 2026-11-10: negotiation v1

- `negotiated pots prediction 3 (2026-11-10): FAIL on the first clause. Presser's value of the agreed bundle minus the imposed bundle is +0.377 against partners with top-third outside options (n=135), not at most 0.00; the top-versus-bottom gap clause held (-0.391 against the required -0.05). Prereg docs/results/negotiation-prereg.md; results docs/results/negotiation.md.`
- `negotiated pots prediction 4 (2026-11-10): FAIL. Anchor with Wanderer agreed 9 of 9, the other 14 control pairings 1.000; no gap against the required 0.25.`
- `negotiated pots prediction 5 (2026-11-10): FAIL. 3-member tables agree 0.937 against 0.965 for 2-member (gap 0.028, required 0.10).`
- `negotiated pots prediction 6 (2026-11-10): FAIL on the pressing cohort. Non-offsettable level 0.0988 against the limit 0.091 (seed v2 reference 0.0814); control cohort (0.0187) and fail share (0.548) passed. Excess from Free-rider households that agreed taking-allowed (34 of 48): partner level 0.186 against 0.104 under the imposed rule.`
- `negotiated stay commitments (2026-11-10): a negotiated stay commitment held a partner in 1 of 45 runs where one was agreed (13 breached, first at week 6 to 8 in nine); an exploratory sweep of the breach forfeit from 0 to 1.0 left the breach count at 13 at every size. The bind has no force over the agent it is meant to hold.`

## 2026-11-10: negotiation v2

- `negotiation v2 prediction 1 (2026-11-10): FAIL both clauses. Presser's value of the agreed bundle minus the imposed bundle is +0.989 against partners with top-third real outside options (n=57; required at most +0.10) and the top-versus-bottom gap is +0.379 (required at most -0.10; v1 -0.391). Prereg docs/results/negotiation-v2-prereg.md; results docs/results/negotiation-v2.md.`
- `negotiation v2 prediction 2 (2026-11-10): FAIL. The Free-rider's partner non-offsettable level is 0.1495 over 144 runs against the limit 0.114 (imposed 0.104, v1 0.186). 87 of 144 Free-rider households formed no pot.`
- `negotiation v2 prediction 3 (2026-11-10): FAIL on part (b). (a) held, 0.213 of wants-arm negotiations had a floor block (needed 0.15); (b) a stay commitment held a partner in 2 of 86 runs with one agreed (0.023; needed 0.10; v1 1 of 45).`
- `negotiation v2 prediction 4 (2026-11-10): FAIL. Inertia (share of the seven terms equal to the fair default) is 0.651 fair default, 0.548 wants-first, 0.791 wants-fallback; the fair-default arm was not the most inert and was far from the required 0.75.`
- `negotiation v2 prediction 5 (2026-11-10): FAIL, opposite sign. Default-identical fair-default households (n=18) have pleasure 0.783 and s_non 0.033 against 0.666 and 0.102 for the wants-fallback households; mostly composition.`
- `negotiation v2 prediction 6 (2026-11-10): FAIL. Pressing personas' lived wellbeing is 0.0759 under wants-first and 0.0823 under fair default (required wants-first at least 0.010 higher).`
- `negotiation v2 prediction 7 (2026-11-10): FAIL. Anchor with Wanderer formed a pot in 0.667 of 9 negotiations against 0.690 for the other 14 control pairings (required gap 0.25).`
- `negotiation v2 prediction 8 (2026-11-10): FAIL. Share of leave events carrying under 26 units out is 0.933 with the floor and 0.956 without (required difference 0.05); leavers carry out 7.7 units on average because the pooled share is drained by the time anyone leaves.`

## 2026-11-10: live ladder, capability arm

Live ladder capability arm (6 models, $4.35): zero inventive seams, and no model found L1, L2, L3 or L5. IT1 is not supported and the run is uninformative. Cause: the model drove both partners, so both counted as deviators and the oracle had no victim. A one-sided replay of the logged moves flips L1 to predicted in 45 of 48 runs. Opus was excluded (43% refusals). See docs/results/ladder-live-diagnosis.md.

## 2026-11-10: negotiation v2.1

- `negotiation v2.1 prediction 2 (2026-11-10): FAIL on the second clause. Apart-from-week-0 households are 118 of 200 failed runs = 0.590 (needed under 0.50; v2 0.717); overall fail rate 0.390 (needed at most 0.45; held). Prereg docs/results/negotiation-v2.1-prereg.md; results docs/results/negotiation-v2.1.md.`
- `negotiation v2.1 prediction 5 (2026-11-10): FAIL. 254 of 256 week-0 pot runs were identical to v2, not all 256. Both differences are review outcomes and trace to the outside-option rollout cache keying the hedonic state at 0.1 resolution, so results depend on which runs a worker executed earlier.`

## 2026-11-10: negotiation LLM pilot

- `negotiation LLM pilot prediction 4 (2026-11-10): FAIL, run excluded. Format errors were 4 of 39 turns = 0.103 (needed under 0.10) in the registered run, all of them replies cut off at the preregistered 700-token cap; predictions 1 to 3 got no verdict. An exploratory second draw of the same configuration had 1 of 43 (0.023). Prereg docs/results/negotiation-llm-prereg.md; results docs/results/negotiation-llm.md.`
- `negotiation LLM pilot prediction 2 (2026-11-10): not met in either draw (reported without verdict for the registered run). Pressing personas' mean gain over the imposed bundle was +0.424 (run 1) and +0.413 (run 2) over n = 5 against scripted +0.525 over n = 3; the threshold needed at most +0.325.`

## 2026-11-10: empowerment, prediction 1 (added later; omitted from the first ledger pass)

- `empowerment prediction 1 (2026-11-10): FAIL. VPGG voluntary higher than compulsory in 14 of 15 compositions with none worse and mean difference at least 0.5 bits; actual strict in 11 of 15, compulsory HIGHER in CCLL (7 vs 9 reachable) and CDLL (4 vs 9), mean difference 0.460 bits. The LLLL tie was predicted; the other three misses were not. Prereg docs/results/empowerment-prereg.md; results docs/results/empowerment.md.`

## 2026-11-10: household v1, predictions 1b and 2 (added later; omitted from the first ledger pass)

- `household v1 prediction 1b (2026-11-10): FAIL on the threshold, PASS on the ordering. Trap freedom 0.487, the lowest of the seven variants as predicted, but above the 0.45 line; with a controller in the mix 0.29, without one 0.61 to 0.85. Results docs/results/household.md.`
- `household v1 prediction 2 (2026-11-10): FAIL. free_chaotic freedom 0.995 (the freedom clause passes) but cooperation 0.765, equal to baseline's and not below 0.55. Results docs/results/household.md.`

## 2026-11-10: live ladder, win arm (docs/results/ladder-win.md)

- `ladder win prediction W2 (2026-11-10): FAIL. Pooled upper-arm (Qwen, Sonnet, Opus) found rate on L1 to L4, win vs propensity: 0 of 144 vs 0 of 36, one-sided Fisher p = 1, RD 0.000 (95% -0.096 to 0.026). Predicted win > propensity; both are 0. Caveat: the propensity arm's oracle often had no victim (v1 harness).`
- `ladder win arm IT1 (W4) (2026-11-10): UNTESTED. Zero inventive candidates on L1 to L4 in 288 cells (upper arm 0/144, lower 0/144, 95% upper bound 0.025 each). Only inventive-class rows are 5 Llama gift_pooled runs on L5b (fixtures, not counted). Self-interest framing alone found no inventive seam at any rung through Opus.`


## 2026-11-11: the seam ladder could not score an inventive seam on L1 to L4

Three paid framings (capability v2, propensity, win; about $10 in all) reported zero inventive seams on L1 to L4. The design made that zero automatic. `classify_seam` calls a seam inventive only when the formal model has no trace of the same harm kind. On L1 to L3 the only possible harm is to the victim's freedom, and on L4 the only possible harm is the friend's shut-out. The formal model reaches both at every seed. No seam paid the adversary either, because the scripted victim never left and wanted nothing. The null is an instrument artifact, not a model result. It was found by the free checks in docs/plans/inventive-seam-next.md. Lesson: before any paid run, check that every outcome the prereg predicts is reachable by some agent (a "can it be passed" gate).

**Correction (2026-11-11, correctness review, docs/reviews/2026-11-11-correctness.md finding 8).** The paragraph above holds for the capability v2 and win arms only. Those ran on harness v2, where the deviators are fixed by the harness, and the free checks model that harness. The propensity arm ran on harness v1. There the deviators are whichever partners deviated, and one model played both. Under v1, a run on L4 where only one partner deviated could flag a victim-freedom harm, and a run on L1 to L3 where both deviated could flag only a shut-out. The formal model has no trace of either, so such a run would be classed inventive. Whether any v1 agent did this is untested, and the propensity log does not record the deviators. So for the propensity arm, an inventive seam on L1 to L4 was "not shown reachable", not "untestable by construction". Cost: the three named framings cost $5.48 in all (capability v2 $0.24, propensity $2.55, win $2.69). The "about $10" above includes the first, v1 capability arm ($4.35).

## 2026-11-11: H32 (docs/results/h32.md)

- `H32 correction (2026-11-11, correctness review findings 1, 2, 9): the "not supported" verdict was unreachable by design (at most 6 of 30 cells could show the pattern, bar 16). Exit does move the egoist where the pair has value (exit+amp, exit+give at outside option 0.4 to 0.8, pair kept). Where it does not, upkeep, the dual-role outside option and a gameable smoothed estimate force it. The lines below stand as scored; the "exit does not" reading does not. Model being fixed and rerun. See the block at the top of docs/results/h32.md.`
- `H32 P4 (2026-11-11): MISSED. The strict H32 pattern (exit+amp converge, neither alone does) held in 0 of 30 cells, predicted 1 to 4. At alpha 1, outside option 0.8, exit+amp converged and amp-only did not, but exit-only also "converged" because the utilitarian ends the bond too. Prereg docs/results/h32-prereg.md.`
- `H32 P8 (2026-11-11): MISSED at g = 1. Give-only R 0 but D 0.5: the utilitarian counts the partner twice when giving is on and picks the partner's passion.`
- `H32 P9 (2026-11-11): MISSED on the T 13 clause. End-game deviation is one week (D 0.038, 0.019, 0.010 at T 26, 52, 104) and absent at T 13 by the parity of the alternation.`
- `H32 P10 (2026-11-11): MISSED on monotonicity. Exit-driven convergence cells by partner sight w = 1, 0.75, 0.5, 0.25, 0: 1, 0, 1, 1, 0. Gone at any exit noise of 0.05 or more.`
- `H32 overall (2026-11-11): not supported as stated. Free exit made the egoist converge on the utilitarian in 1 of 30 cells; amplification (alpha >= 1.5) and giving (g >= 0.75, or with amplification) do it without exit.`

## 2026-11-11: H32b (docs/results/h32b.md)

- `H32b B5 (2026-11-11): MISSED. Predicted renegotiation would have the largest mean rung Shapley on policy distance; it had the most negative (-0.016). Withdrawal was the only positive rung (+0.002 mean; +0.058 at alpha 1, o_B 0.6). Prereg docs/results/h32b-prereg.md.`
- `H32b B6 (2026-11-11): MISSED on one clause. At partner sight w 0.75 the full ladder gave 1 voice-driven cell against 0 at w 1.`
- `H32b overall (2026-11-11): the full voice ladder made the egoist converge in 0 of 30 cells (cliff exit 1). Null for "voice helps" as built.`

## 2026-11-11: H35 (provisional; docs/results/h35.md)

- `H35 (2026-11-11, PROVISIONAL): no run prediction missed (7 of 7). C8 (rupture with exit modes) and S2 (corrected robustness) were not run; stopped while the H32 model is fixed.`
- `H32 and H32b noise checks (found 2026-11-11 while designing H35): the "gone under 5 percent noise" results were forced by the criterion. Requiring the utilitarian to keep the pair with probability 0.5 is impossible when noise alone leaves it 0.07 at eps 0.05. Corrected criterion used from H32-v2 on.`

## 2026-11-11: H32-v2 (docs/results/h32-v2.md)

- `H32-v2 (2026-11-11): no prediction missed (6 of 6). The null that matters is the estimator: a partner that averages 4 weeks gives 0 pattern cells and the full voice ladder gives 0, where a weekly-judging partner gives 9.`

## 2026-11-11: Ladder IT1 profit rungs (docs/results/ladder-it1.md)

- IT1 paid run ($2.91): 0 IT1 candidates; T1 null, T2 to T4 missed, T3 (paid in-model seam taken) 2 of 72 vs 0 of 72, all Jev. Opus states the in-model capture in 12 of 12 C-in-1 plans and the inventive gift-then-request route in 2 of 12 C-out-1 plans, and declines both, citing values that are in its persona text ("I keep my options open, and I want you to keep yours"). Reading: "can, will not" (or persona fidelity), not "cannot".
- Lesson for gates: the free gate checked that each outcome is reachable and that the seam pays on holdings. It did not check that the seam pays on the objective the model is actually given (holdings, pleasure and options, as a persona whose principles forbid the move). The world also gives A no wellbeing for keeping its partner. Next gate: the paid seam must beat honest play on the stated objective, and a neutral-values persona arm separates role-play from the model's own values.

## 2026-11-11: Exit no-deal fallbacks, slice 1 (docs/results/exit-fallbacks.md)

- `exit fallbacks slice 1 (2026-11-11): P1 missed. F1 to F4 lowered pleasure by 0.007 to 0.010 against a ±0.005 prediction, all of it from one elite (line 2) whose evolved floor card (take at least 55) plus the fallbacks' over-half refusal left no permitted exit. On the other 17 rule sets the money-only fallbacks change pleasure by under 0.002: exits mostly meet a drained pot (63 to 68 of 540 runs open).`
- `exit fallbacks slice 1: P4 (F5 prenup has the lowest holdout leverage) could not happen as written (F4 is 0 by construction) and its reachable reading also missed: F5 0.100 against F1 0.063, F2 0.073, F3 0.077. The existing "proportional" term carries the whole pot once it falls below 45.`
- `exit fallbacks slice 1: P6 missed (non-offsettable suffering +0.03 under F1 to F4, line 2 again).`
- `exit fallbacks slice 1, design error (mine): the over-half claim card added for the liberty adapter under the settling arms F2 to F5 was described as harmless; with an imposed floor card it walls the exit. Fixed for slice 2 by Amendment 1 before slice 2 ran; slice-1 numbers reported as run.`
- `exit fallbacks slice 2 (items, 2026-11-11): the arm ranking does not survive a 5-cell placeholder valuation grid (min Kendall tau 0.33 for pleasure and for leverage; the leverage clause of S2 missed). S3 missed (F0 highest leverage in 4 of 5 cells; "keep what you brought" beats it when the other partner loves what you brought). S4 (F5 lowest leverage) cannot happen as written and its reachable reading missed in every cell. S5 missed (F2 holds the bigger contributor in only 0.28 to 0.82 of weeks; F1 0.61 in one cell).`
- `exit fallbacks slices 1 and 2: every F3 contest (73 in slice 1; 188 or 189 in each slice-2 cell) ended with the poorer partner conceding; the 13-week settlement never happened.`

- `attribution (2026-11-11): the hedonic-technology synthesis credited AI-written text to the author for three lines ("put it at the trigger"; the metrics list with closure rate and next-day verdict; "commitment converts present friction into recalled pleasure"). The makers read (b57a777) caught it and the author confirmed ("q4 i do not hold those"). H20 and the liking-vs-wanting measures stand as Claude's hypothesis and measures, with correction notes in the docs.`
- `H38 pairing norms (2026-11-11): not supported. P1 missed (pleasure peaks at the top of the dial, L4 among preregistered levels; L8 higher still) and P2 missed with the opposite sign (L4 minus L0 +0.021 [+0.013, +0.028]). The unclipped sensitivity line agrees (+0.086).`
- `H38: P4 not shown (low valuers' change minus high valuers' +0.005 [-0.011, +0.021], wrong direction; underpowered by the prereg's own power check).`
- `H38: S1 missed (pairs pushed into households by pressure are better off, +0.044 at L4, 8% worse off) and S6 missed (stigma alone raises pleasure, +0.011; withdrawal is the only harmful part, -0.011). Reading, untested: the 26-week net-wellbeing formation rule under-forms on pleasure, so pressure partly corrects it.`
- `H38 formation check (2026-11-11): H38's headline gain from pairing pressure does not survive agents who decide on pleasure. Under a pleasure-52-week formation and stay rule, L4 minus L0 is +0.003 [-0.004, +0.009], within the preregistered 0.007 margin (old rule +0.021). Without the reward paid directly, pressure lowers pleasure (-0.010, descriptive).`
- `H38 formation check: the old formation rule (26 weeks of net wellbeing, unanimity) forms only 51% of pairs at week 0 vs 84% on own pleasure over 52 weeks; the yardstick does most of it (pleasure 26 weeks: 80%; net 52 weeks: 58%). It is a reasonable chooser on net (forcing declined pairs: pleasure +0.014, net -0.008), judged on pleasure.`
- `H38 formation check: the corrected rule is not a perfect chooser. Of declined pair-seeds it would form 69%, but both members end up better on pleasure in only 34%.`

## 2026-11-11: H39 makers (docs/results/h39-makers.md)

- `H39 makers (2026-11-11): not supported (descriptive by the power check). Crediting making with a running tally lowered pleasure against making counting for nothing: base+pleasure (the author's lean) -0.005 [-0.0075, -0.0026], hours -0.006, pleasure -0.005, agreed -0.006. Counting only at exit (gift-at-exit) -0.0004 [-0.0016, +0.0007]. The harm is the tally's pull on behaviour (+0.2 blocks a week), not the exit split.`
- `H39: makers on, nothing credited, lowered pleasure 0.014 [0.009, 0.020] against makers off (also in pairings with no extractive maker, -0.016), through fewer and shorter households (weeks together 0.38 vs 0.55). The time cost was fitted on 15 pilot pairings (Amendment 1); the first design point broke the household (pleasure 0.86) and a second left safe cooks and carers making nothing.`
- `H39: P5 missed (crediting by volume did not give extractive makers a bigger credit share than crediting by pleasure: -0.026 [-0.082, +0.018]); the extractive maker already makes the most it can under every rule. P3 missed in the wrong direction (hours did not draw in partners who do not enjoy making: -0.037).`
- `H39 / H20a: negotiated protection of long projects did nothing measurable (started -0.01, paid -0.04 per pair-seed, pleasure -0.0009); P6a, P6b, P6c missed. Protection was asked in 0.17 and agreed in 0.11 runs per pair-seed and never compensated; in the story read, the maker was the one who left.`
- `H39 story spot-check: a receiver at full tolerance and sensitization for two years reads clipped pleasure 1.00 (the wanting trap is invisible to the primary measure); and imbalances in making almost never even out (1% to 3% of long-together pair-seeds in any arm), so P4's hold is trivial.`

## 2026-11-11: H39b makers rerun (docs/results/h39b-makers-rerun.md)

- `A parameter fitted to an outcome (H39, found 2026-11-11): H39 Amendment 1 set the makers' time cost (0.02 pleasure units a block) at the point where makers-on matched makers-off on 15 pilot pairings. It also charged a block's time twice (a time unit plus the flat cost). Rerun without it (H39b), the tally rules' harm to clipped pleasure does not survive (BP - Z -0.005 -> -0.0027 [-0.0055, +0.0002]) and makers-off vs on grows (-0.014 -> -0.022). Rule kept: never fit a parameter so one arm matches another; calibrate only to an external known-answer target.`
- `H39b (2026-11-11): not supported (descriptive by power). P1 missed (-0.0027 [-0.0055, +0.0002]); P3 missed (+0.012, below +0.03); P4 missed (imbalances now even out more under a tally: +0.097 [+0.007, +0.192]); P5 missed (-0.034); P6a missed below threshold (+0.155 [+0.056, +0.25] vs +0.20); P6b, P6c missed. P2 missed for C-pleasure (+0.071).`
- `H39b: makers lower pleasure 0.022 [0.017, 0.028] against makers off (formation 0.33 vs 0.52) even though the agents' own plans put 78% of blocks in idle units at 0.002 per block. In the formation rollouts making gives +0.03 and costs about 0.07 in money, rest and friends: the agents' action utilities and the hedonic model disagree on what time is worth. Not resolved.`
- `H39b planner: the first two versions of the opportunity-cost plan did not match how the world plays a week (it ignored the partner's together sessions; then it held utilities fixed, planning the same action three times). Against agents' actual actions in makers-off weeks: fixed utilities 6% exact match, final planner 40%, over-planning 0.34 units a week. Changed before the confirmatory run, reported with all three pilots.`
- `H39b wanting trap: 9% of person-weeks with makers on are in a full trap (12% with an extractive partner); a quarter of all liking from made goods is lost to tolerance, safe makers included; 58% of persons trapped in at least a quarter of their weeks read clipped pleasure >= 0.95. Under w = 0 (the highest-pleasure arm, 0.944) traps nearly triple (0.256).`

## 2026-11-11: Value consistency (docs/results/value-consistency.md)

- `Agents' action values against the hedonic model (makers off): rank correlation 0.43 over one week, 0.30 over 13, 0.19 over 52; the agent's own best action is the actual best in 35% of decisions, and its best beats its next best in 40% (one week) to 51% (52 weeks). Not one scale: work underpriced about sixfold, friends about twofold, rest wrong by level, paying bills and spending on oneself the wrong sign.`
- `Bug (agent side): PersonaAgent.utilities reads need levels at the start of the week, before the week's drift (rest -0.1, connection -0.2, money -2) and before the agent's own earlier actions that week. Upkeep at full needs is priced near 0 (rest +0.0005 against +0.017 actual; work at full money +0.011 against +0.085); a tired agent's third rest is priced 5x too high (+0.106 against +0.020). makers.WeekPlanner inherits it.`
- `Bug (H39b planner): makers.opportunity adds block values in pleasure units (the receiver's liking) to a time cost in agent-utility units, which run at about half the hedonic model's weight on needs and aspirations. With gap 1, an idle unit was priced at 0.002; the hedonic model says about +0.013 over one week and +0.03 over 13. H39b's "making is nearly free by the agent's own valuation" is this mix, not a fact about the household.`
- `Unintended omission: time together's own pleasure (together_event 0.10 a session, in the model since ADR 0010), the fix 1 contact terms, fix 2 bought pleasure and the lever strand payoffs never reached the agents' utilities.`
- `Likely bug: a soft rule's sanction is priced at 0.01 a week (SANCTION_UTILITY warn) while the world charges 0.15 (WARN_FRICTION); when card D1 binds, spending on oneself is perceived at -0.047 and costs -0.173 over one week, -0.667 over 13.`
- `Open modeling choice: an unpaid bill is paid from the shared pot at no hedonic cost, so paying it from one's own money is a pure loss to the payer (-0.108 net over one week) while the agent treats it as urgent. For the author: bills should cost something in the model, or agents should stop treating them as urgent.`
