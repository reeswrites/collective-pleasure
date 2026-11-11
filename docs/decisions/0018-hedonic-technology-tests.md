# 0018. The three tests of hedonic technology are evaluator criteria

Status: proposed (2026-11-10). Not yet accepted by the author.

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

## Context

docs/theory.md states a theory of hedonic technology and three tests of whether a technology is good (section 2). The evaluator today reports pleasure, freedom and cooperation. None of the three tests is a measure there. A rule set can score well on pleasure while failing a test: by raising wanting without liking, by holding people through exit cost, or by needing constant reassurance. The author said the evaluator is the more interesting product ("more interested in the norms but the evaluator is the more interesting product", docs/goal.md), so the tests belong in it.

The tests come from the author's notes (liking vs wanting; derived vs extracted, why it persists) and the author's raising of reassurance seeking in the 2026-11-10 claude.ai conversation "Attuning vs appeasing in relationships" (not archived in the repo). Grouping them as a test set is Claude's framing and is the thing the author is asked to accept.

## Decision

Each test becomes a named measure that the evaluator computes for any rule set. A measure that its world cannot yet compute is reported as "not measurable here", never as zero.

1. **Liking vs wanting.** Needs version 3 of the model, where pleasure splits into a wanting value (drives action choice) and a liking value (the experienced payoff, adapting on a slower clock). Measure: liking per unit of wanting-driven activity, closure rate (share of sessions that end at a natural stop), and next-day verdict (a lagged liking check). Flag a rule set when wanting-driven activity rises while mean liking does not (synthesis M7 and M9). Until version 3 exists the evaluator reports "not measurable here".
2. **Worth it vs hard to leave.** Two parts. (a) The counterfactual "why they stay": for each household week, replay with the exit cost removed (breach load, forfeit, commitment bind) and ask whether the pair would still stay, using the existing bar max(outside option, status quo value). Report the share of staying weeks that survive the removal. (b) Dissolution analysis: for pairs that stay and have low or falling pleasure, record the exit cost that holds them. Report: stay-worth-it share, stay-held-by-cost share, and the pleasure of each group.
3. **Lasting security vs checking.** Needs a reassurance-seeking or checking cost in the model: an action that restores a security reading briefly and recurs, with the threshold for needing it falling each time it is used (the loop in the conversation, paraphrased from Claude). Measure: checking actions per week, the share of security that comes from checking, and lifetime pleasure net of checking time. Compare against households whose security is built by history. Until the model has the loop, report "not measurable here".

## What the evaluator reports for any rule set

For a rule set R on a pairing set, one block with these lines, each with the ADR 0015 interval:

- Lifetime pleasure (ADR 0017 measure), freedom and cooperation, as now.
- Liking-to-wanting ratio, closure rate, next-day verdict (or "not measurable here").
- Stay-worth-it share and stay-held-by-cost share.
- Checking share of security and net lifetime pleasure after checking (or "not measurable here").
- A one-line reading in plain English that names which test, if any, R fails.

A rule set is not rejected by one failing test. The tests are reported beside the scores, as freedom is, so the author can read them.

## Consequences

- The model gains version 3 pieces (wanting and liking split, a checking loop) before tests 1 and 3 can run. Test 2 can run on the current negotiation and exit machinery.
- The evaluator can warn about a trap quadrant that pleasure scores hide, as the horizon study showed greedy scoring hides carried-over loss.
- Risk: the measures are built from assumed parameters and will show what the model puts in. Each needs a sweep and, where possible, a control with the mechanism off.
- Not decided: thresholds for "fails a test", and whether the first build is test 2 (cheapest) or test 1 (the author's central worry).
- Related hypotheses: H24 to H28 in docs/hypotheses.md.
