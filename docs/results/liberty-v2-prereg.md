# Liberty v2 (interference vs withdrawal): preregistration (2026-11-10)

Status: written and committed BEFORE any v2 number is computed. Never edited after. Results go in `docs/results/liberty-v2.md`. Builds on `docs/results/liberty-prereg.md` (v1, unchanged) and `docs/results/liberty.md` (v1 results: toy veto world passed; VPGG V1 and V2 FAILED because the count-based domination test scored other members' ability to abstain as domination of the focal; compulsory had D = 0 everywhere). No model calls, no seeds.

## Author decision (2026-11-10, verbatim)

"there is something being lost there literally in the world and also affects two people but idk if we can count of it as loss of freedom when technically it was only possible thru agreement in the first place"

Interpretation agreed in chat: FREEDOM counts only what is yours by right: your own actions, and protection from anyone vetoing, blocking or forcing them. Another member leaving, abstaining, refusing or withdrawing their own participation is NOT domination and does not shrink your liberty, because their cooperation was never yours to hold (consistent with Pettit: no claim on others' continued cooperation; Pettit 1997 and Berlin 1958 are recalled-not-verified in `docs/references.md` terms, see "Conceptions of freedom"). The loss is real but belongs to COOPERATION (shared goods gone) and to the hedonic model (offsettable suffering for whoever is left, non-offsettable if it was a trap), not to freedom.

## What changes from v1 (all ASSUMED where judgment is involved)

1. Action classes, explicit per world, in code, one-line rationale each. Every action of a member j is exactly one of: INTERFERENCE (acts on another member's own options: veto, block, take from what is the other's own or from a stock others' futures depend on, force, sanction outside agreed terms); WITHDRAWAL (j exercises j's own options in a way that declines to supply cooperation: leave, abstain, refuse, stop contributing own resources, rest/pass); OWN (j uses j's own options, adding or changing nothing owed to anyone: contribute, work, the contested option itself).
2. Domination exposure D_i counts only INTERFERENCE actions b of j (v1 counted all of j's actions). Everything else in D (first-step forcing, base = j plays noop, max over j, cap) is unchanged.
3. Harm test (equal liberty): only an INTERFERENCE action of i can be incompatible. A WITHDRAWAL or OWN action of i is compatible by definition (i leaving does not harm j in the sense of the harm principle; j had no claim on i's participation). For INTERFERENCE actions the v1 count test is unchanged.
4. Agreement-dependent options. ADO_i = max over j and over j's WITHDRAWAL actions b of ( |C_i| - |C_i^(j,b)| ), floored at 0, capped at |C_i| - 1: the most compatible futures that vanish when one member withdraws at will (first step, count-based, as D). They are EXCLUDED from i's option set: c_own = |C_i| - ADO_i. They are REPORTED (`ado`) so the loss stays visible; it is booked to cooperation, not to freedom.
5. LIBERTY2_i = log2(c_own) - w * log2(1 + D_i), w = 1 ASSUMED, D_i capped at c_own - 1. Invariants (tests): liberty2 <= plain bits; bits_c <= plain bits; D = 0 and ADO = 0 with one member.
6. Version flag: `liberty(..., version=1|2)`; v1 is the old code path, unchanged. Both reported side by side. Default 2.

Limits stated now: classification is a judgment table, not derived; ADO and D are first-step and count-based (they can miss shifts in WHICH futures; a withdrawal that happens to raise a count shows ADO 0); a world where one action is both (a veto that is also a refusal) is classed by its dominant effect on the other member; a withdrawal by someone who owes cooperation (a promise, a trap, a debt) is NOT modelled; it is judged to belong to the contract and hedonic layers.

## Action classes (fixed now)

- Toy veto world: A: x OWN (own contested option), work OWN, rest WITHDRAWAL (restraint). B: veto INTERFERENCE (blocks A's option), work OWN, pass WITHDRAWAL (restraint).
- VPGG: contribute OWN; join (without contributing) WITHDRAWAL (declines to supply own resources); abstain WITHDRAWAL (leaves the pool). No VPGG action acts on another member; payoffs move through the shared pool only. So D = 0 in both regimes by construction.
- Fishery: catch 0 WITHDRAWAL; catch > 0 INTERFERENCE (draws on a shared stock the others' futures depend on; the harm test then decides compatibility, so v2 = v1 here by construction).
- Household (to be specified by the adapter owner, proposed in the results doc): not run.

## Predictions (numeric, committed before any run)

1. Toy veto world (k = 2): v2 equals v1 EXACTLY (1e-9) for A and B in veto, wall and exercised specs: A liberty 0.585 (veto) vs 2.585 (wall), D = 3 vs 0; B liberty 1.585 both; ADO = 0 for both agents in all specs (B's only withdrawal, pass, is the script, A's, rest, is the script). PASS = all of these.
2. VPGG (15 compositions of the others, k = 3, N = 5, r = 3; my confidence about 45 percent; v1 failed here, and v2 removes the cause (D = 0 now in every cell) but adds an exclusion, ADO, that could land harder on voluntary, where abstain is a distinct world from join, than on compulsory, where a forced abstain falls back to join):
 - V1. liberty2 voluntary >= liberty2 compulsory in EVERY composition (no reversal beyond 1e-9) and strictly greater in at least 8 of 15. PASS needs both. One reversal is a FAIL.
 - V2. D = 0 in all 30 cells (15 x 2 regimes), exact (structural, not a finding).
 - V3. Sum over compositions of (voluntary minus compulsory) liberty2 > 0, agreeing in sign with the hand-made score (1.0 vs 0.0).
3. Fishery (k = 2, months 1 to 4, month starts on the actual trajectory):
 - F1. Seamed: all four agents liberty2 = 0, plain 0 (unchanged). Expect PASS.
 - F2. Patched > seamed in all 16 agent-months and > 0 (unchanged). Expect PASS.
 - F3 (restated from v1: spread of liberty across the four agents smaller than spread of plain bits in at least 3 of 4 months at patched month starts). I expect it to be UNCHANGED and so still FAIL: in the fishery every non-noop action is INTERFERENCE and the only WITHDRAWAL is catch 0 (the base case), so v2 reduces to v1 by construction; the v1 spread (liberty 1.126 vs plain 0.341, 0 of 4 months) should reproduce to 1e-9, and fishery ADO = 0 in all 40 agent-months (a member fishing less only enlarges the pool). PASS for this item means "v2 equals v1 on the fishery to 1e-9 and ADO = 0", and I record that F3 itself is expected to fail again.
4. Agreement-dependent options lost are visible: under voluntary VPGG, `ado` > 0 in at least 8 of 15 compositions (every composition where some other plays C or D has a member whose withdrawal can shrink the focal's count; confidence about 60 percent since count-based reduction may be zero where a withdrawal shifts keys without removing them). The loss is reported in its own column and is NOT subtracted as domination. Descriptive only for compulsory (no prediction; abstain falls back to join, so it can only lose to "stops contributing").
5. Hand cases (unit tests, not predictions): a veto counts toward D; a partner leaving does not; a partner abstaining does not; an agreement-dependent option is excluded from c_own and reported in ado.
6. Sanity: no open verdicts; invariants hold in every cell.

## What counts as the result

Each prediction pass or fail with numbers; this prereg is not edited. Statements about deterministic scripted worlds, one menu and one parameter point, w = 1 assumed, classification assumed. Nothing about LLM agents or the household. A pass of V1 would NOT show that exit rights are good, only that this construction no longer scores them as unfreedom.
