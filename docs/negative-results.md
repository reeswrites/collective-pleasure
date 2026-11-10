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
