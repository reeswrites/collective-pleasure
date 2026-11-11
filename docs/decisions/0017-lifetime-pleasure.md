# 0017. Lifetime pleasure is the measure

Status: accepted (2026-11-10, author decisions in conversation)

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

## Context

ADR 0010 grounds "good" in a modeled hedonic state, scored week by week. The hedonic synthesis (docs/notes/hedonic-technology-synthesis.md) found the model has no adaptation, no anticipation, and treats commitment as a constraint, and asked the author whether personas should have a lifetime horizon or a present-weighted one. The horizon study (docs/results/horizon-prereg.md, docs/results/horizon.md, src/mar/horizon.py) builds a small exactly solvable decision problem to see what the answer changes. Citations here are from memory, verify.

## The author's words (verbatim)

On the measure (2026-11-10):

> lifetime pleasure seems obvious to me and also i feel like present value maximization infers that you need to optimize over time and not be greedy but idk if we can prove that somehow

On what a choice does to later pleasure (2026-11-10):

> well dont change our future situatioun in what way? bc like i think a concert here if it diminishes pleasures a little bit is it stealing from future pleasures or no sicentiically

On which self counts (2026-11-10):

> i think the experieicing self is the remembering self and depends onf vividness of memory etc

## Decision

1. **The measure is lifetime pleasure**: the sum over all moments of a total that is the present pleasure, plus remembered pleasure and pain re-experienced now (each memory trace weighted by its vividness), plus anticipation of scheduled events. Present-weighted (greedy) scoring is not the measure; it is a special case that is exact only when nothing carries over.
2. **The proof the author asked for exists** (docs/results/horizon.md section 1): greedy is optimal for every reward and every discount in [0, 1] exactly when actions leave no trace in state the reward sees (sufficiency) and, over all reward functions, only then (necessity, horizon of at least 2 steps). Discounting does not remove the need to plan. In the model, planning starts to matter at gamma 0.378, and a machine-checked witness (z3, exact rationals) shows greedy losing from a reachable state at horizon 2.
3. **"Future situation" means everything that carries over** (adaptation level, resources, energy and needs, memories, anticipation, tastes, bonds), with both signs: tolerance, depletion, neglected needs and bad memories cost later pleasure; anticipation, vivid memories, acquired taste and bonds add to it; spacing restores tolerance. A choice "steals from the future" only if the sum is negative, and in the model a concert's net carryover is negative weekly and positive at three to four weeks apart.
4. **One self.** The author's position is that the experiencing self is the remembering self, with vividness as the bridge. The old "experienced" and "remembered" scores are kept only as named special cases (memory weight 0, present weight 0). (Note added 2026-11-11: the author's words were "i think the experieicing self is the remembering self". The experienced versus remembered utility distinction these special cases name is from Kahneman, Wakker and Sarin 1997, "Back to Bentham?", per docs/references-check-2026-11-11.md row 6.) Painful vivid memories re-cost (rumination). Vividness parameters are assumed, in one block (`SelfParams`).

## Open questions for the author

- **Which self counts.** Decision 4 records the author's answer (one self). The earlier open question, whether "lifetime pleasure" counts the experiencing or the remembering self, is closed by it. What stays open: how strongly memory should count against the present (the memory weight; the best gap for one friendship moves from 86 to 108 days if it is tripled), and whether vivid pain should keep costing as long as it stays vivid (rumination) or fade faster.
- **Discounting.** Does the household world use a hazard-style discount (the future may not arrive) or none?
- **Intense-short versus mild-long.** Should a persona prefer a short intense life to a long mild one with equal sums? The measure as written does not say.

## Consequences

- The household world's weekly pleasure needs memory and anticipation terms (synthesis M1, M3, M4) before its pleasure scores can be called lifetime pleasure; until then they are the present-weighted special case, and findings from them carry that caveat.
- Policy evaluators that score rules by short-horizon outcomes can systematically favor rules that drain carried-over state. The alignment connection: a short-horizon optimizer is a reward hacker of the state its reward does not show.
- Not decided: the memory weight, the rumination factor, and the discount, all assumed.
- Verdicts of the study (docs/results/horizon.md): P1, P3, P5 to P8 held; P2 (monotone in horizon at gamma .9) and P4 (commitment accepted at gamma .9) missed in one clause each.

## Amendment 2026-11-10 (second): shared experience amplifies pleasure

The author corrected the friendship-gap case (latest row of `experiments/changes.jsonl`, quoted in docs/results/horizon-prereg.md): the case treated a friend as rationed reunions and missed that eating, watching films and the like can be amplified by doing them with someone. Decision: lifetime pleasure for the worked case includes a shared-experience layer, a per-activity multiplier on pleasant and unpleasant occasions that depends on closeness, taste overlap for that activity and the activity's sociability, with smaller logistics than a special meeting. The reunion release stays as a smaller layer. The earlier result is kept as "Before amplification". With it on, the best contact rhythm for people with shared tastes is 4 to 7 days (against 19 to 139), though most of that drop is due to shrinking the release layer; the sharing-specific part is 2 to 5 days. Preregistered A2(b), that closer friends are seen more often, missed: the model gives a longer best gap. Open: should sharing raise closeness itself, and should the multiplier have a different form? All parameters assumed. Details: docs/results/horizon.md section 5.
