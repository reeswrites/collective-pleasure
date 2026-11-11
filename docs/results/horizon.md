# Horizon: lifetime pleasure versus being greedy (results)

Status: results of the run preregistered in docs/results/horizon-prereg.md (committed first). Deterministic, exact, no seeds, no model calls. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state (ADR 0010). Every number below holds for the ASSUMED parameters in `src/mar/horizon.py` and says nothing about real people. Citations marked "from memory, verify" have not been checked.

Code: `src/mar/horizon.py`, `tests/test_horizon.py` (21 tests), `scripts/horizon_run.py`. Report with charts: `experiments/kept/horizon-2026-11-10/report.html` (also `results.json`; the run copy is `runs/horizon/`, git-ignored).

## Verdict table

| ID | Prediction | Result |
|---|---|---|
| P1 | greedy loss 0 when all carried-over state is off | **held** (max |loss| 3e-14 over 56 cells) |
| P1b | adaptation and commitment off only (descriptive) | loss still 8.4% (gamma .9) and 13.9% (gamma 1): other carried state remains |
| P2 | loss positive at gamma 1; nondecreasing in gamma and in horizon | **missed** on one clause: positive and nondecreasing in gamma (yes), nondecreasing in horizon at gamma 1 (yes), but NOT at gamma .9 (it peaks at 5.3 over 6 to 8 weeks and falls to 3.0 by 16 weeks) |
| P3 | a witness with k <= 6, machine-checked | **held** (k = 2 from a reachable state, k = 3 from the start; z3 agrees) |
| P4 | optimal plan accepts commitment friction within 6 weeks at gamma .9; never at beta = 0 | **missed** on the first clause (no commitment at gamma .9; accepted from gamma 0.903 up, and at beta >= 2 for gamma .9); the beta = 0 clause held |
| P5 | concert net carryover negative weekly, positive every 4 weeks | **held** (-5.6 and +2.2 at gamma .95; boundary m* = 3 weeks) |
| P6 | one-self special cases, vivid peaks/endings, low-vividness stretches, bad endings keep costing | **held** |
| P7 | gap case: interior best gap growing with depth; remembered below experienced; mismatch costs the short-optimum person | **held** |
| P8 | critical discount below 0.95 | **held** (0.378) |

Two of eight predictions missed in a clause each, and both misses are informative (below). Deterministic checks get pass or fail, not intervals (ADR 0015 point 4).

## 1. The lemma (standard dynamic programming), in plain math

Setting: a deterministic decision problem. State s, action a, next state f(s, a), reward r(s, a) (the pleasure of that step, using the state before the action). Discount gamma in [0, 1]. The value of k steps left is V_0 = 0 and V_k(s) = max over a of [ r(s, a) + gamma V_{k-1}(f(s, a)) ]. The greedy policy picks the action with the largest r(s, a) now. The infinite-horizon case is the same with a limit.

**"Future situation" in plain words:** anything that carries over from this step to the next: tolerance, resources, energy and needs, memories, anticipation, tastes, bonds. A choice can lower some of it (using up the pot, getting used to a pleasure, forgetting to eat) and raise some of it (anticipation, a vivid memory, a bond, a taste). Carryover is two-sided. Whether a concert "steals from future pleasures" is the sign of the sum of those two sides, and it depends on how often you go (section 5).

**Theorem 1 (sufficiency).** Split the state into (x, y). Suppose x evolves on its own, x' = g(x) whatever the action, y evolves however the actions say, and the reward depends on the state only through x: r(s, a) = rho(x, a). Then greedy is optimal for every gamma in [0, 1] and every horizon.
*Proof.* Show by induction on k that V_k(x, y) depends on x only, call it U_k(x). U_0 = 0. If it holds for k - 1, then V_k(x, y) = max over a of [ rho(x, a) + gamma U_{k-1}(g(x)) ]. The second term does not contain a, so the best a is the one that maximizes rho(x, a), which is the greedy action, and V_k = U_k(x) is attained by it. QED.

**Theorem 2 (necessity, over all reward functions).** If some action changes the state in a way the reward can see, in other words if there are a state s and actions a, a' with f(s, a) = u different from f(s, a') = v (and neither u nor v equals s), then for every gamma > 0 and every horizon of at least 2 steps there is a reward function under which greedy is strictly worse than another plan.
*Proof.* Pick 0 < eps < gamma. Set r(s, a) = 0, r(s, a') = eps, r(u, anything) = 1, and 0 everywhere else. Greedy at s takes a' because eps > 0, then earns r(v, anything) = 0 next, total eps. The plan "a, then anything" earns 0 + gamma times 1 = gamma. Since gamma > eps, greedy loses. QED.

So "greedy is optimal for all rewards" holds exactly when actions leave no trace in the state, and "for this reward" when the reward is blind to the traces. This is what the author asked for: yes, it can be proved, and the proof shows what "not greedy" is really about. It is not about discounting. Discounting gamma < 1 only changes how much each future step weighs; it never removes a trace. The two theorems are checked numerically in `tests/test_horizon.py` (100 random small MDPs for Theorem 1, the construction for Theorem 2). **Present value with gamma < 1 still needs planning whenever state matters**, and in our model the smallest discount at which greedy loses is 0.378 (section 3). A heavy discounter who forgets nothing has to plan.

## 2. The machine-checked witness (P3)

Model: `HorizonParams`, gamma = 9/10, exact rationals. A reachable state and horizon where greedy yields strictly less than another plan, found by exhaustive search (every plan of length k) and then checked with z3 over exact rationals (three facts: greedy's action is a best immediate reward at every step, unsat for "some action has strictly more"; a strictly better plan exists, sat; no plan beats the stated best, unsat):

- **Smallest k, any reachable state (k = 2).** State: favorite tolerance 1, alternative tolerance 0, 1 week since the last event, connection need 1 of 2, pot 2, no commitment, no memory glow, no taste, no bond. Greedy takes the concert twice (K K) for 25.35. The plan "solo treat, then concert" (X K) gets 26.4. Reason in plain words: going to the concert right now wastes the anticipation, because one more week since the last event raises the concert's value, and the treat now is nearly as good. Greedy cannot see that waiting one week raises the value of what it will do. At gamma = 1 the same state gives 26.5 against 28.
- **From the natural start state (k = 3).** Fresh activities, need met, pot 2. Greedy: treat, concert, favorite (X K F) = 31.17. Better: treat, favorite, concert (X F K) = 33.96 (at gamma = 1: 34 against 38 with F X K). Same reason: spacing builds anticipation.

All z3 checks passed (greedy_is_greedy unsat, better plan sat, best_is_optimal unsat) for both gammas and both states. Scope: this is a counterexample for our model at gamma 9/10 and 1, not for the world.

## 3. How much greedy loses (measurement)

Start state fresh, 26 weeks, defaults. Loss = optimal minus greedy total discounted pleasure, percent of optimal.

| gamma | 0 to .3 | .4 | .5 | .6 | .7 | .8 | .9 | .95 | .99 | 1 |
|---|---|---|---|---|---|---|---|---|---|---|
| loss % | 0 | 0.1 | 0.6 | 1.3 | 2.2 | 2.7 | 3.2 | 15.5 | 23.0 | 24.5 |
| infinite horizon, % | 0 | 0.1 | 0.6 | 1.3 | 2.2 | 2.7 | 5.2 | 20.6 | 30.1 | n/a |

- **gamma = 0: zero loss, by definition.** Critical gamma (the smallest discount where greedy strictly loses) is 0.378 for horizons of 12 or more weeks (0.375 at 4, none at 2).
- **Where it becomes large (10% of optimal, the declared line):** at gamma = 0.95 over 26 weeks (15.5%). The jump between 0.9 (3.2%) and 0.95 comes from commitment: the optimal plan starts honoring the commitment at gamma 0.903, and a three-week front-loaded friction is worth it only for a planner who weighs the later payoff almost fully. Below that, greedy is within 3%.
- **Horizon (gamma = 1):** 0% at 1 and 2 weeks, 10.5% at 3, 18% at 4, then 17, 13, 13, 19, 24.5 and 28.6% at 52 weeks. In absolute terms the loss is 4, 8.5, 11, 11, 16.5, 34.5, 79.5 and 196.5 pleasure units at 3, 4, 6, 8, 12, 16, 26 and 52 weeks. At gamma = 0.9 it is a hump (13% at 4 weeks, 3.2% at 26): early transients cost greedy, and the optimal plan settles into the same ritual and favorite cycle that greedy finds.
- **Adaptation strength** (gamma .95): 22% at delta 0 (other carried state is still on), 24, 23, 24, 15.5, 16, 14% at delta .05, .1, .15, .2, .3, .4. It is not monotone: stronger tolerance also changes what greedy happens to do, and the commitment threshold interacts. The preregistered idea that loss vanishes when adaptation is off is true only if every carried-over channel is off (P1), not adaptation alone (P1b: 8 to 14%).
- **Commitment payoff** (gamma .9): loss is 3.2% for beta up to 1.5, 13.1% at beta 2 (the optimal plan now honors three weeks of friction), 28.7% at beta 3.
- **Heuristics against the optimum** (gamma .9, 26 weeks, percent of optimal): greedy 96.8, ritual-every-2 86.7, ritual-every-4 76.3, ritual-weekly 74.1, rotate-1 61.4, rotate-2 53.7, rotate-4 38.9. At gamma 1: greedy 75.5, ritual-every-2 71.2, rotate-1 44.2. Simple rules of thumb from the notes (rotate often, ritual weekly) do worse than greedy here, because they discard the one-step information that is useful. Planning is not "rotate".

What P2 and P4 missing teaches: the loss is not a smooth function of the horizon at gamma < 1, and whether a long project is worth starting is a threshold in the discount (0.903 here), not a gradual effect. Both were stated as smooth predictions and failed in one clause.

## 4. The one self, and the worked case: the best gap between seeing someone

The author's decision (2026-11-10): "i think the experieicing self is the remembering self and depends onf vividness of memory etc". So there are not two selves to report. Each moment's pleasure is present pleasure plus re-experienced memory (good and bad), each trace weighted by its vividness, plus anticipation. Lifetime pleasure is the sum of that total over all moments. Vividness (ASSUMED block `SelfParams`): intensity or peak, being an ending, novelty, emotion, being shared; it decays with time (45 days); a painful trace re-costs by a rumination factor (1.5).

Old scores are special cases (tested): memory weight 0 and no scheduled anticipation is exactly the old EXPERIENCED score; present weight 0 with the vividness weights 0 is the old REMEMBERED score (peak-end, duration neglected) up to a positive constant per cycle, with the same best gap.

The worked case, "the optimal gap between seeing someone" (the author's 2026-09-10 claude.ai conversation on the optimal time between seeing someone, not archived in the repo; the parameters are placeholders). Closeness halves every H days apart. Missing is tension = closeness x a saturating want-to-see x an absence-becomes-normal factor. Tension up to a threshold feels like anticipation; above it, like pain. At reunion the release is the drop from tension to zero (relativity, opponent process; Helson; Solomon and Corbit 1974; from memory, verify), a meeting closes part of the closeness gap and costs something.

| friendship half-life (days) | best gap, one self | old experienced self | old remembered self |
|---|---|---|---|
| 10 | 19 days | 18 | 6 |
| 20 | 42 | 39 | 8 |
| 45 | 86 | 80 | 11 |
| 90 | 139 | 128 | 13 |

(Remembered-to-experienced ratio of best gaps: 0.33, 0.21, 0.14, 0.10.) The old remembered self, which counts peak and ending and ignores duration, wants to meet every one to two weeks, because the bigger the release, the better the memory, and it never pays for the days apart. The one self sits close to the old experienced self (the days apart are lived and also re-lived), a little longer, because vivid good reunions are re-experienced for weeks. Scaling the memory weight x3 moves the best gap for the half-life 45 friendship from 86 to 108 days; removing the ending boost moves it to 85, and fast forgetting (tau 10 days) to 80, the old experienced value. Reading: how much memory counts is the main lever on the answer.

**Two people, one gap.** Half-life 20 days (best 42) and half-life 90 days (best 139): a mismatch of 97 days. At 139 days the short-optimum person's closeness has faded to 0.5% at the meeting instead of 15%, and they get 56% less lifetime value than at their own best gap: the "slow fade" for the person whose optimum is shorter. (With the old experienced self: 39 and 128 days, 89 days apart, 56% loss: the finding does not depend on the self chosen.)

**Vividness predictions (P6, tested):** a +15 reunion is worth 24.0 after the fact against 15 in the moment (ratio 1.6; without the ending boost 20.6, 1.4); a mild +5 episode 6.9 (1.4). A -20 betrayal costs 51.3 after the fact, 2.6 times its in-the-moment cost, against 34.2 without rumination: **it keeps costing**. A mild steady stretch (+1 per day) gets 6.3% of its total value through memory at 7 days, 1.5% at 30, 0.5% at 90, 0.1% at 365: **long low-vividness stretches contribute little after the fact.**

Plain-English illustration of carryover from this case: a longer gap lowers closeness (negative carryover: fade) and raises tension then release (positive carryover: missing someone makes the reunion bigger, and the reunion is remembered). Neither is "stealing"; the best gap is where the two sides balance for this person.

## 5. Is a concert stealing from future pleasures? (P5)

The concert in the MDP: base value equal to the solo treat, costs a pot unit, is shared, leaves a vivid memory (vividness 2), builds a bond, raises tolerance for ordinary pleasures by contrast, and does not refresh the connection need. With every carryover off a concert is exactly a free treat, so any gain over never going is carryover. Net carryover of a concert every m weeks, total over 26 weeks, gamma .95:

| m (weeks) | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 13 | 26 |
|---|---|---|---|---|---|---|---|---|---|
| net carryover | -5.6 | -0.8 | +1.1 | +2.2 | +0.4 | +0.4 | 0.0 | +0.7 | +0.8 |
| negative channels alone | -7.1 | -5.1 | -3.1 | -2.0 | -1.2 | -0.7 | -0.7 | 0 | 0 |
| positive channels alone | +2.6 | +28.1 | +28.8 | +29.3 | +21.6 | +15.7 | +13.4 | +7.0 | +2.6 |

Answer in the model: **it depends on the dose.** Alone, the costs (tolerance, resources, a neglected need, the bad memory of a starved week) are always negative and the benefits (anticipation, vivid memory, bond) always positive and much larger; the sum is negative weekly and every second week, becomes positive at spacing of three weeks or more (boundary m* = 3), is largest around four weeks (about +2.2), and is small and flat beyond. At gamma = 1 the pattern is irregular (-12, -4.5, 0, +2.5, -1.5, +0.5, +0.5, +4.5, +5.5 for the same spacings), partly because 26 weeks does not divide evenly. The concert is worth it occasionally, spaced, and affordable; the same action at high frequency, or when it displaces the need that ritual would have met, costs net. This is a statement about the model, and the boundary moves with the assumed numbers.

## 6. Alignment connection: short-horizon optimization and reward hacking

A policy that maximizes the next step's reward is the greedy policy. Theorem 1 says it is safe only if nothing it does leaves a trace that the reward later cares about. Theorem 2 says that any action with a trace the reward sees can be punished by some reward. In the model the harm is not exotic: spending a pot, wearing out a pleasure, neglecting a need, skipping a long project. Agents trained on single-turn reward, or on a short effective horizon (small gamma, a reward model scoring one reply at a time), will drain state the reward does not show them: trust, tolerance, resources, the other party's expectations. Here that cost is up to a quarter of lifetime pleasure at gamma 1. It is a miniature of the usual story: a proxy that is right one step at a time can be wrong over time. Two cautions the numbers add: heuristics are not a substitute (every simple rule did worse than greedy), and discounting does not cure it (loss appears at gamma 0.38 and grows with gamma).

## 7. Philosophical caveats (not settled by numbers)

- **Discounting.** A discount can be pure time preference or a hazard rate (the future may not arrive). The author's wording, present-value maximization, is the second; the lemma holds for both. Whether pure time preference is rational is a dispute, not a calculation.
- **Temporal neutrality.** Treating a pleasure the same whenever it occurs (gamma = 1) is the lifetime view. Parfit argued against bias toward the near, and also noted that we are not neutral about pain already past (Parfit 1984, Reasons and Persons; from memory, verify). Our one-self scoring puts the past into the present through vividness, so it is not time-neutral by construction: a vivid past matters now, and a faded one does not.
- **Intense-short versus mild-long lives.** A sum over moments can prefer a long mild life to a short intense one if the total is larger. The vividness weights and the peak/ending terms make intense moments count more after the fact, but they do not settle the dispute; the repugnant-conclusion style worry (Parfit 1984; from memory, verify) stays.
- **Which self.** Kahneman and colleagues' distinction between experienced and remembered utility (Kahneman, Wakker and Sarin 1997, "Back to Bentham?", Quarterly Journal of Economics; corrected 2026-11-11 from "Kahneman et al. 1993", which is the peak-end cold-pressor paper and does not set up the distinction; docs/references-check-2026-11-11.md row 6) is retained as two named special cases; the author's position is that there is one self. Whether memory can be both a real cost to the present (rumination) and a "mere" representation of the past is a modelling choice recorded in ADR 0017.
- **Rumination is a cost of memory, not just of events.** In the model a vivid betrayal keeps costing for as long as it stays vivid. Whether lifetime pleasure should count that, or only pains as they happened, is the open question in ADR 0017.

## 8. Limits

One parameter point per sweep. Assumed numbers, a deterministic one-agent model, an arbitrary 26-week default. Greedy ties break to the lowest action index. The concert's zero-carryover baseline is a free solo treat by assumption. The gap case consolidates all traces at the reunion and uses a steady-state cycle; its best gaps depend on the assumed meeting cost (24) and memory weight (0.01). The monotonicity and boundary findings should not be read as laws; P2 and P4 each missed in a clause. The commitment-acceptance discount (0.903) was computed after the confirmatory run and is descriptive. Notation for a later reader: the two theorems are standard dynamic programming, not new.

## Reproduce

`uv run python scripts/horizon_run.py` (about 80 seconds) and `uv run pytest tests/test_horizon.py` (about 25 seconds).

## 5. Amendment 2026-11-10: shared-experience amplification (preregistered in the amendment to docs/results/horizon-prereg.md, commit 0161425)

The author's correction (latest row of `experiments/changes.jsonl`, verbatim): "well we ight have to think harder baout how we do things like if you like eating with others then it makes sense that it could amplioify or channel pelasure iwth eating with a nother person or if you like watfching movies and it would be cooler to share and wathc with someone else". The friendship-gap case in section 4 treated a friend as rationed reunions and undercounted companionship. Section 4 stays as it was ("Before amplification"; the old figures are in `experiments/kept/horizon-2026-11-10/report-before-amplification.html`, `results-before-amplification.json`). The new run adds the `amp` key to `results.json`; every old key is unchanged (checked), and with amplification off the score equals the old one exactly (max difference 0.0 over g 1..200, four friendships). Code: `Activity`, `AmpParams`, `share_multiplier`, `amp_score`, `amp_curve`, `amp_best` in `src/mar/horizon.py`; 6 new tests (27 total). Everything is for the ASSUMED parameters in the amendment, not real friendships. The model was smoke-run before the amendment was written and two settings changed after that look; this is disclosed in the amendment.

Best days between contacts (default overlap 0.7), one-self scoring:

| friendship half-life (days) | before (rationed reunions) | smaller reunion layer alone (control) | with shared activities |
|---|---|---|---|
| 10 | 19 | 6 | 4 |
| 20 | 42 | 7 | 5 |
| 45 | 86 | 10 | 6 |
| 90 | 139 | 12 | 7 |

Best gap by taste overlap (0.1, 0.3, 0.5, 0.7, 0.9): half-life 10: 6, 6, 6, 4, 3; half-life 20: 7, 7, 6, 5, 4; half-life 45: 10, 10, 7, 6, 5; half-life 90: 12, 12, 8, 7, 6. At overlap 0.1 and 0.3 no activity beats its logistics (at 0.3 only meals and walks marginally; the person shares none at 0.1), so the rhythm is the reunion layer's. Reading or a solo hobby is never shared.

| ID | Prediction | Result |
|---|---|---|
| A1 | much more frequent: (a) H = 90, overlap 0.7 at most 7 days; (b) at most 14 days for every H at overlap 0.5, 0.7, 0.9; (c) at overlap 0.7 and 0.9 at least 1 day shorter than the reunion-only control | **held** (a) 7 days exactly, (b) max 10, (c) shorter by 2 to 5 days |
| A2 | (a) nonincreasing gap as overlap rises; (b) nonincreasing gap as closeness level rises; (c) descriptive: slower fading gives a longer gap | **missed on (b)**. (a) held for all four H. (b) gap goes 5, 6, 7 for closeness level 0.3, 0.6, 0.9 (control 8, 10, 11): closer friends here want a LONGER gap, the opposite. (c) as stated: longer gap with larger H |
| A3 | (a) sharing gain negative for the solo hobby at every overlap and for meals, movies, walks at overlap 0.1; (b) forcing all sharing lowers value | **held**. Per-occasion gain at overlap 0.1: meals -0.44, movies -1.56, walks -0.39, hobby -3.78; break-even overlap about 0.22, 0.32, 0.21 and none for the hobby. Forced sharing lowers lifetime at overlap 0.7 for every H (for example 6.81 to 5.90 at H = 45) |
| A4 | release share of friendship pleasure above 0 and below 0.5 at overlap 0.7, no larger at 0.9 | **held**: 43.6, 43.7, 43.6, 43.3% at overlap 0.7 for the four H; 33.8 to 35.1% at 0.9. At overlap 0.1 and 0.3 it is 100% (nothing shared) |
| A5 | shared bad occasions amplified | **held** (movies at overlap 0.7: bad part -0.62 against 0 with amplification off) |
| A6 | regression | **held** |

What it teaches. Amplification makes the best rhythm weekly or better for people who share tastes (4 to 7 days against 19 to 139), but most of the drop from the old answer is the smaller reunion layer, not sharing: shrinking release alone already gives 6 to 12 days. The sharing-specific shortening is 2 to 5 days at overlap 0.7 and it grows with overlap. So the old long gaps were produced by a model in which the only value of a friend was a large release after absence; once that is demoted, the data-free answer is "weekly". A2(b) missed because in this model deeper or closer friendships keep the amplifier up through a gap and the release layer still favors some absence; frequent contact is wanted most where sharing is most valuable per contact (high overlap), not where closeness is highest. If the author thinks closer friends should be seen more often, something is missing: sharing should itself raise closeness (not modeled), and companionship should have value that the gap does not dilute. That is an open design question, not a finding.

Report: `experiments/kept/horizon-2026-11-10/report.html` (new "After amplification" section with six charts and plain-English captions; the two old gap figures sit under "Before amplification").
