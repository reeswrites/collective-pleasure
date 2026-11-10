# 0014. Freedom is equal liberty minus domination, and withdrawal is not domination

Status: accepted (2026-11-10, author decisions in conversation)

## Context

ADR 0007 made freedom one of two scores for a network of agents. ADR 0011 added empowerment (the number of distinct futures an agent can reach) as a second reading beside the hand-made score. Empowerment counts options, not whose they are. A wall that stops a partner vetoing you lowers the partner's empowerment, and a kind master who never vetoes you leaves yours untouched. The author was asked what freedom should mean here. The questions and answers are in experiments/questions.jsonl (topics freedom-conception, freedom-decision, exit-not-unfreedom). Evidence: docs/results/liberty.md and docs/results/liberty-v2.md. Nothing here is a claim about real people.

## The author's words (verbatim)

On what freedom is (topic freedom-conception, 2026-11-10 19:58 UTC):

> i think only that dont shrink someone eleses unless there are other conceptions of it in philosophy

On whether to combine it with the republican reading, when asked (topic freedom-decision):

> yes both

On whether another member leaving counts as lost freedom (topic exit-not-unfreedom, 20:08 UTC). The log entry is cut off mid-word, so the sentence below is quoted as the liberty v2 results file records it:

> there is something being lost there literally in the world and also affects two people but idk if we can count of it as loss of freedom when technically it was only possible thru agreement in the first place

## Decision

1. **Freedom is options compatible with everyone's equal options.** An option counts for an agent only if taking it leaves no other member with fewer reachable futures than that member would have if the agent had held back. This is the author's "don't shrink someone else's". It follows the shape of Kant's universal principle of right, Rawls's first principle and Mill's harm principle (docs/references.md, conceptions of freedom).
2. **Minus a domination penalty.** Subtract every compatible option the agent holds that another member could block at will, whether or not they ever do. This is Pettit's freedom as non-domination: the kind master is still a master. The score is bits of compatible futures minus bits of exposure, with the weight on exposure set to 1 and reported at 0.5 and 2.
3. **Withdrawal is not domination.** Another member leaving, refusing or abstaining does not count as blocking. An option that depends on someone else's agreement was never the agent's to hold, so it is taken out of the count and reported separately (agreement-dependent options, "ado"). Interference means acting on the agent's own options (a veto, a block, a force, taking from a shared pool). Withdrawal means declining to act. Each action in each world is classed by an assumed table with a one-line reason.
4. **The loss from withdrawal is real but booked elsewhere.** The author said something is lost "literally in the world". It is counted in cooperation and in the hedonic model (pleasure and non-offsettable suffering, ADR 0010), not in freedom. This keeps exit-at-will from scoring as a loss of freedom and keeps the freedom score from charging members for each other's choices.
5. **Relational autonomy is a later check.** Autonomy that is socially constituted (Mackenzie and Stoljar 2000) needs household version 3 (appraisal, rupture and repair, ADR 0011) and is not scored yet.
6. **Reported alongside, not instead.** Liberty is reported next to the hand-made freedom score and plain empowerment. None is collapsed into another, and none replaces the Pareto frontier of ADR 0007.

## Evidence so far (scripted worlds, no model, no household)

- **Version 1 (decision 1 and 2 only).** Docs/results/liberty.md: 6 of 9 predictions held, 3 missed. The toy kind-master world behaved as designed (granting an unused veto cuts the owner's liberty by 2 bits, a wall restores it, and the other partner's liberty is unchanged where plain empowerment falls). The fishery patch raised liberty in all 16 agent-months. It failed on the voluntary public goods game: voluntary beat compulsory in only 4 of 15 compositions, lost in 10, summed difference -19.6 bits. The cause was that others' ability to abstain counted as domination. That failure is what led to decision 3.
- **Version 2 (decision 3 added).** Docs/results/liberty-v2.md: 6 of 10 held, 4 missed. The VPGG sum flipped to +5.263 bits, strict in 11 of 15, with no domination term left in any composition. Missed: two compositions (CCLL, CDLL) still reverse, because plain count-based reach is already lower under voluntary there; the fishery patched-over-seamed check held in 12 of 16 agent-months (one exploiter sits at 0.000 in both specs); the prediction that version 2 equals version 1 on the fishery was wrong (12 of 40 agent-months differ, because forcing a member to catch 0 changes counts); and agreement-dependent options showed in 7 of 15 voluntary compositions against a threshold of 8.
- **What still disagrees.** Equal liberty does not flatten seat order in the fishery; non-domination widens it (prediction F3 missed in both versions). The count-based test cannot tell a smaller shared good from a lost option. Blocking is judged on the first step only.

## Consequences

- Liberty is built for the toy, VPGG, fishery and a hand partner world, not yet for the household. The household needs `noop`, `force_policy` and `classify` on its adapter (docs/results/liberty-v2.md, last section). This is queued in docs/plan.md.
- ADR 0011's "freedom as empowerment" is amended: empowerment stays as the plain count, and liberty is the main freedom reading. The hand-made score stays as the third.
- The ASSUMED parts are the weight, the classification tables, the first-step blocking limit and the count-based harm test. Each is listed in the prereg files.
- References for the conceptions (Berlin, Kant, Rawls, Mill, Pettit, Mackenzie and Stoljar) are in docs/references.md, marked verified or recalled.
