# Liking vs wanting: results (ADR 0018 test 1)

Date: 2026-11-10. Prereg: docs/results/liking-wanting-prereg.md (commit dbac2db, pushed before the run). Code: src/mar/wanting.py, scripts/liking_wanting_run.py, tests/test_wanting.py. Report: experiments/kept/liking-wanting-2026-11-10/report.html.

Wording rule: agents feel nothing. "Liking" and "wanting" are glosses for modeled values (ADR 0010). Scripted agents, exact solves, no model calls, cost 0. Every parameter is assumed, and the intervals describe spread over an assumed parameter box, not sampling of people.

## Verdict table

80 personas, every one run in every cell, all comparisons paired by persona. Intervals are 95% percentile bootstrap over personas (Clopper-Pearson for P8a). Holm across the 15 tests.

| ID | Quantity | Threshold | Mean [95% CI] | Holm p | Label |
|---|---|---|---|---|---|
| P0 | O's liking identical across plain, heavy and the closure ritual | identical | identical for all 80 | n/a | pass |
| P1 | wanting = liking: gap exactly 0, ratio 1, no cued units, W plan = L plan | exact | all 80 x 6 cells | n/a | pass |
| P1b | flag off: same as P1; wanting-greedy = horizon greedy | exact | all cells; horizon test passes | n/a | pass |
| P2 | sensitization off: divergence 0 | within 1e-9 | max 8.9e-16 (318 of 320 measurable) | n/a | pass |
| P3 | WC(heavy) - WC(plain), no rule, points | >= 5 | 15.6 [13.0, 18.4] | 0.00075 | holds robustly |
| P4a | WC(heavy, none) - WC(heavy, closure) | >= 10 | 18.7 [16.3, 21.0] | 0.00075 | holds robustly |
| P4b | WC(heavy, closure) - WC(plain, none) | <= 3 | -3.1 [-5.0, -1.0] | 0.00075 | holds robustly |
| P5a | W loss(heavy, cap) - W loss(heavy, closure) | >= 5 | 11.7 [10.3, 13.0] | 0.00075 | holds robustly |
| P5b | O loss under the cap | >= 2 | 7.3 [6.8, 7.7] | 0.00075 | holds robustly |
| P5c | W loss(heavy, none) - W loss(heavy, cap) | >= 2 | 7.0 [4.7, 9.3] | 0.00075 | holds robustly |
| P6a | W loss(heavy, none), % of lifetime optimum | >= 20 | 48.8 [46.3, 51.4] | 0.00075 | holds robustly |
| P6b | wanting share of W's loss, heavy | >= 0.2 | 0.30 [0.25, 0.35] | 0.00075 | holds robustly |
| P6c | O cued units / W cued units, heavy | <= 0.7 | 0.45 [0.43, 0.46] | 0.00075 | holds robustly |
| P6d | WC(plain, none) | <= 3 | 0.16 [-0.23, 0.55] | 0.00075 | holds robustly |
| P7a | closure rate, W: plain - heavy | >= 0.2 | 0.52 [0.47, 0.57] | 0.00075 | holds robustly |
| P7b | next-day verdict, W: plain - heavy | >= 0.5 | 1.22 [1.07, 1.37] | 0.00075 | holds robustly |
| P7c | closure rate, W in heavy: closure - none | >= 0.2 | 0.47 [0.44, 0.48] | 0.00075 | holds robustly |
| P8a | flag rate, W, heavy, no rule | >= 0.8 | 0.89 [0.80, 0.95] (71 of 80) | 0.029 | holds but CI crosses threshold |
| P8b | flag rate, W, heavy: none - closure | >= 0.4 | 0.63 [0.51, 0.73] | 0.00075 | holds robustly |

14 of 15 tested predictions hold robustly. P8a is weak support: its lower bound is 0.797 against 0.8. All 4 deterministic checks pass. No prediction missed.

WC is the wanting cost: the wanting agent's liking loss minus the liking-greedy agent's loss in the same cell, in points of the lifetime optimum.

## How much gap each cell allows

Mean over 80 personas [95% CI]. Liking lost is percent of the lifetime optimum's liking with no rule.

| Environment and rule | Agent | Liking lost % | Gap per unit | Liking per cued unit | Closure rate | Next-day verdict | Flag rate |
|---|---|---|---|---|---|---|---|
| plain | acts on wanting | 33.2 [31.0, 35.4] | 0.85 | 3.50 | 0.55 | 4.05 | 0.39 [0.28, 0.50] |
| plain | greedy on liking | 33.0 [31.0, 35.1] | 0.27 | 4.63 (35 not measurable) | 0.14 | 4.23 | 0 |
| plain | lifetime optimizer | 0 | 0.54 | 6.28 | 0.41 | 7.26 | 0 |
| plain + cap | acts on wanting | 37.7 [35.8, 39.5] | 0.81 | 3.53 | 0.95 | 3.94 | 0.06 |
| plain + cap | lifetime optimizer | 7.2 [6.7, 7.8] | 0 | not measurable here | 0.00 | 7.66 | 0 |
| cue-heavy | acts on wanting | 48.8 [46.3, 51.4] | 6.40 | 2.77 | 0.03 | 2.83 | 0.89 [0.80, 0.95] |
| cue-heavy | greedy on liking | 33.0 [31.0, 35.1] | 2.92 | 4.20 | 0.14 | 4.23 | 0 |
| cue-heavy | lifetime optimizer | 0 | 2.40 | 7.15 | 0.41 | 7.26 | 0 |
| cue-heavy + closure | acts on wanting | 30.1 [27.5, 32.8] | 4.93 | 3.42 | 0.49 | 3.47 | 0.26 [0.17, 0.37] |
| cue-heavy + cap | acts on wanting | 41.8 [39.7, 43.9] | 3.19 | 3.33 | 0.99 | 3.34 | 0.45 [0.34, 0.57] |
| cue-heavy + cap | lifetime optimizer | 7.2 [6.7, 7.8] | 1.36 | 7.66 | 0.00 | 7.66 | 0 |

The closure ritual changes nothing in the plain environment, because plain content already has no cue at a stop. The full table, with every interval and the liking-to-wanting ratio, is in the report and in results.json.

## The horizon link

Acting on wanting is the greedy move, and the lifetime optimizer avoids the trap. In the cue-heavy environment the wanting agent loses 48.8% of lifetime liking. The optimizer loses nothing, by definition. It also takes far less of the cued activity: 46 units against 105 in four weeks (P6c, 0.45).

The loss splits into two parts:
- About two thirds is plain greed. The liking-greedy agent, which ignores wanting, already loses 33%.
- About a third is wanting: 15.8 points, a share of 0.30 (P6b).

In the plain environment the wanting part is near zero (0.2 points, P6d). There, all of the wanting agent's loss is greed.

An optimizer that discounts (gamma 0.9) loses 6.2% of undiscounted lifetime liking at the default persona. It is far from the wanting agent's 56%. So even a short-sighted planner escapes most of the trap. Being greedy on the next slot is what costs, not discounting.

## Honest misses and surprises

No preregistered prediction missed. What did not go as the framing expected:

1. **The closure ritual did more than "protect".** Under it, the wanting agent in the cue-heavy world loses less than in the plain world (30.1% against 33.2%, P4b). It also beats the liking-greedy agent (WC -2.9). Stopping at every episode pushes the wanting agent into a "two episodes, then the plain activity" rhythm, and that rhythm happens to be good here. This is a property of the assumed numbers, not a general claim.
2. **Closure rate does not track liking for the optimizer.** The optimizer's closure rate is only 0.41, and 0 under the cap. The cap rule's closure rate is near 1 by construction (cap = one episode). So closure rate distinguishes the wanting agent's environments well (P7a, P7c), but it is not a measure of good outcomes on its own. The next-day verdict does track liking in every cell (optimizer 7.3, wanting agent in the cue-heavy world 2.8).
3. **The flag is not specific to the cue-heavy world.** It fires for 39% of personas in the plain world and 45% under the cap. It says "more activity, no more liking than acting on liking alone". The plain environment's mid-episode cue is enough to trigger that for some personas.
4. **Divergence is not an agent measure.** The gap per cued unit grows more for the optimizer (3.4) than for the wanting agent (1.3), because the optimizer starts with less sensitization. Divergence works as the sensitization-off control (P2) and nothing more.
5. **The trap is a threshold, not a slope.** At the default persona, the wanting agent's loss in the cue-heavy world is 30 to 40% for low sensitization, cue strength or variable reward, then jumps to 56 to 58%. The jump comes when the cue keeps the agent on G past every stop for the whole day. This matches the horizon study, where planning starts to matter at a threshold.
6. **Greed is large in this model.** The liking-greedy agent loses a third of lifetime liking even with no wanting. That comes from the strong slow-clock tolerance assumed here. A weaker tolerance would shrink both the greed part and the absolute trap.
7. **Sensitization carries most of the wanting cost.** With sensitization off but the cue on, the wanting agent loses 35.3% in the cue-heavy world, against 48.8% with it on. A cue alone costs about 2 points beyond greed. Sensitization adds about 13.5.

## Plain-English reading

In this model, wanting and liking are split. A pull toward more that grows with use is enough to cost a person who follows it about half of what they could have liked over four weeks. That happens only where cues are everywhere and the reward is variable. In a plain environment the same person loses no more than a person who simply takes the best thing in front of them.

The rule that helps is the closure ritual, not the stopping rule. Closing each episode removes the pull at the natural stop. It gives back the whole wanting cost and does not cost anyone who did not need it. The stopping rule (at most two units a day) helps the wanting agent less. It also takes 7% from the lifetime optimizer, who needed no protection. In the notes' terms, friction at the trigger or the stop works better than a dose limit.

A person who plans their lifetime liking does not fall in. That is true even if they discount the future.

For the evaluator (ADR 0018), the measures behave as follows:
- Liking per unit of wanting-driven activity separates the cells well.
- The next-day verdict separates them well.
- Closure rate separates environments for the wanting agent, but does not track good outcomes on its own.
- The flag is a coarse alarm that also fires in plain settings.

## Limits

- One person, one cued activity, one plain activity, a quiet option, 28 days. No household, partner or money.
- Every parameter is assumed, including the persona box. The intervals are over that box. They are not about people.
- Wanting is liking plus a cue term. That is a simplification of incentive salience. The literature is about drugs and conditioned cues over weeks: Robinson and Berridge 1993 and Berridge 2009, from memory, verify.
- The cue-heavy environment differs in three ways at once (trigger cue, autoplay, variable reward). The sweep at the default persona varies each one alone, but only descriptively.
- The wanting agent is fully greedy on wanting. A mixed agent is not tested.
- The next-day verdict is one choice (peak-end on liking). The ADR does not fix it.
- The pilot that set the defaults ran on toy fixtures (7 and 14 days). Three model changes were made after looking at toy output, all disclosed in the prereg before the run.
- The model is not yet in the household world. Porting it behind a flag there is the next step if the evaluator is to report test 1 for rule sets.
