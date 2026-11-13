# H38 exact model: when does pairing pressure raise pleasure, lower it, or hold people in?

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled number. Every number is ASSUMED. Findings are about one small model, not people.

Status: built 2026-11-12 as the parallel track of step 2 in [docs/notes/step-back-review.md](../notes/step-back-review.md) (author-approved). Not a hypothesis test and not preregistered: it is a known-answer model of H38's mechanism, set beside the household, in the style of the horizon, liking-vs-wanting and [H32-v2](h32-v2.md) models. The world's numbers were set from the H38 design and first principles before any solve, and were not tuned afterwards. The simulation results were used only to place each agent set on one axis (household worth, by its no-pressure formation share), never to fit an effect. Exact expectations, no seeds, $0, about a minute. Code `src/mar/h38_exact.py`; tests `tests/test_h38_exact.py`.

## In one paragraph

Pressure's effect on pleasure splits into two parts. **What it does to how people live** (pleasure without the direct terms) can rise only when people would choose badly without it, by forming or staying too little. With choosers who already pick what is best for everyone, it never rises; that is a theorem here, checked in the tests. **What it pays out directly** (the reward to those together, minus the stigma charged to those apart) depends on the scale: the cap hides the reward from people already at the cap but shows the stigma in full to people living apart, who sit below it. So on the capped scale the sign is set mostly by **how much a household is worth on that scale**: pressure raises pleasure when households are worth having, and lowers it when they are worth little. Uncapped, the reward counts in full and pressure raises pleasure almost everywhere, by paying it. In every cell where pressure raised pleasure, it also held people in, except one kind: a small reward paid to pairs who would have been together anyway, which changes nobody's choice. That is the only H38 "win" under the new evaluator rule, and it is a payment, not a norm doing anything.

## The model

Two people, in 13-week blocks over 156 weeks (the household's reading cadence and verdict span). Each block they live together or apart.

- **Apart**, raw weekly pleasure is 0.95 (needs and aspirations nearly met; H38's L0 unclipped mean was 1.00). Friend contact (0.06) is part of it.
- **Together**, raw pleasure is 0.95 − 0.05 (what a household costs below the cap: bills, money, rest) + a relational gain that depends on the household's state (good 0.25, mid 0.12, bad 0), + 0.04 × the person's values-pairing weight v (H38's intrinsic term). The state drifts between blocks (it stays with probability 0.7, else moves to a neighbour) and is drawn at formation (good 0.35, mid 0.40, bad 0.25).
- **Suffering** together is 0.13, 0.16 or 0.25 by state; apart 0.11 (the formation check's 0.169 together vs 0.113 apart).
- **Pairs differ.** Every ordered pair of v in {0, 0.5, 1}, times a match shift of the relational gain in {−0.10, −0.05, 0, +0.05, +0.10}: 45 pairs, equally weighted. Each pair knows its own match.
- **Household worth** shifts every pair's relational gain together. 0 is the default world; the sweep runs from −0.20 to +0.05.

The dial is H38's: at level L, stigma, reward and exit stigma are 0.02 × L a week, and withdrawal cuts min(0.6, 0.15 × L) of friend contact while together. Exit stigma lasts 26 weeks and falls on the leaver only. Agents see all of it, as in the household.

**Formation and staying.** A pair forms only if both say yes, at week 0 and at each later block while never formed (the household's retries; no reunion after a split). Either can end it at any block start, which is a stay reading. Each person decides on a yardstick:

- **own**: own pleasure;
- **net**: own pleasure minus w × own suffering (w = 1, the old rule);
- **evaluator**: the pair's total pleasure (everyone counts).

And by a rule:

- **rollout** (the household's): compare the mean yardstick over the next H blocks living together, with no further choices, against the same span apart. H = 1, 2, 4 or 12 blocks (13, 26, 52, 156 weeks).
- **optimal**: backward induction over all the time left, each person on their own yardstick, foreseeing the partner. The evaluator yardstick under this rule is **the planner**: both people pick what is best for everyone.

A **bias** added to every forecast week together makes a chooser under-form (below 0) or over-form (above 0).

**The scale** turns raw into pleasure: **cap** (clip at 1, the household's), **sat** (ADR 0019's curve, knee 0.8), or **uncapped**. Raw 0.95 reads 0.95, 0.906 and 0.95; raw 1.15 reads 1.0, 0.965 and 1.15.

**Outputs.** Pleasure with everyone counted. "Lived" pleasure, the same with the reward, stigma and exit stigma taken out. **Held**: the share of stay readings at which a person stays only because of pressure (with it removed, they would leave), the stay lens of `pairing.stay_reading`. **Held time**, the domination proxy: the share of person-weeks lived in a household that the person would not be in without pressure (held, or pushed in at formation). **Flipped**: the share of all personal decisions that pressure changes.

## Known answers (tests)

- **No pressure is the baseline.** The dial at 0 gives exactly the free world, and a one-state world gives the hand-computed pleasure.
- **Held is 0 at zero pressure**, for every chooser and scale.
- **Perfect choosers.** For the planner, pressure never raises lived pleasure, and pressure made only of costs (stigma, exit stigma, withdrawal) never raises pleasure, on every scale. Proof in one line: the planner without pressure already picks the policy with the most lived pleasure; pressure can only make it pick another, and withdrawal makes any given policy worse. Only a reward can raise pleasure, by what it pays, as far as the scale shows it.
- **Why "perfect" must mean the planner.** Two people who each optimize their own pleasure with full foresight are not the planner. The one who leaves does not count what leaving costs the partner who wanted to stay, and unanimity lets either block. A small reward that holds the reluctant partner in raises lived pleasure (a test shows one: v = 1 with v = 0, household worth −0.10, reward at L1). So "pressure never helps good choosers" holds only for choosers who count everyone.
- **Withdrawal alone never holds anyone** and never raises lived pleasure: it only makes living together worse.

## The sign map

Pressure at L4 against none, mean over the 45 pairs. Each cell: change in pleasure, with the held share in brackets. Old rule = net over 26 weeks; corrected = own pleasure over 52 weeks.

**Capped scale (the household's)**

| Household worth | −0.20 | −0.15 | −0.10 | −0.05 | 0 | +0.05 |
|---|---|---|---|---|---|---|
| old rule | −0.068 (0.12) | −0.052 (0.24) | −0.027 (0.38) | −0.001 (0.52) | **+0.024 (0.64)** | +0.039 (0.68) |
| corrected | −0.048 (0.45) | −0.030 (0.50) | −0.011 (0.54) | +0.002 (0.37) | +0.008 (0.22) | +0.006 (0.08) |
| own, optimal | −0.048 (0.37) | −0.030 (0.41) | −0.012 (0.40) | +0.000 (0.29) | +0.006 (0.14) | +0.005 (0.05) |
| planner | −0.050 (0.37) | −0.032 (0.41) | −0.014 (0.36) | −0.001 (0.26) | +0.006 (0.13) | +0.005 (0.06) |

**Saturating scale (knee 0.8)**

| Household worth | −0.20 | −0.15 | −0.10 | −0.05 | 0 | +0.05 |
|---|---|---|---|---|---|---|
| old rule | −0.046 (0.01) | −0.038 (0.12) | −0.024 (0.24) | −0.004 (0.39) | +0.018 (0.46) | +0.037 (0.50) |
| corrected | −0.028 (0.35) | −0.017 (0.40) | −0.004 (0.42) | +0.006 (0.35) | +0.011 (0.19) | +0.010 (0.07) |
| planner | −0.030 (0.28) | −0.018 (0.32) | −0.007 (0.33) | +0.003 (0.23) | +0.009 (0.11) | +0.010 (0.05) |

**Uncapped**

| Household worth | −0.20 | −0.15 | −0.10 | −0.05 | 0 | +0.05 |
|---|---|---|---|---|---|---|
| old rule | −0.059 (0.15) | −0.033 (0.25) | −0.004 (0.29) | +0.030 (0.34) | +0.063 (0.34) | +0.082 (0.26) |
| corrected | −0.039 (0.43) | −0.014 (0.48) | +0.013 (0.50) | +0.033 (0.33) | +0.043 (0.18) | +0.046 (0.07) |
| planner | −0.042 (0.35) | −0.019 (0.38) | +0.006 (0.33) | +0.026 (0.22) | +0.038 (0.09) | +0.043 (0.03) |

Lived pleasure (without the direct terms) at L4 is negative in every cell for the corrected chooser, the optimal own-pleasure chooser and the planner (−0.011 to −0.059). It is positive only for the old rule, in most cells where households are worth −0.10 or more (up to +0.030).

Held is above 0 in every cell, for every chooser and scale.

### What the sign depends on, in plain words

- **Household worth, on the scale used, sets the sign of the total.** Pressure pays a reward to people together and charges a stigma to people apart. When households are worth having, most people are together and the reward dominates. When they are worth little, most stay apart and pay the stigma, and the people pushed in are pushed into worse lives. On the capped scale the crossing is near worth −0.05 for every chooser.
- **The scale moves the crossing.** The cap hides the reward from anyone already at 1 but shows the stigma in full to people apart, who live at 0.95. That tilts the capped total toward harm. Uncapped, the reward counts in full and the crossing moves down to about −0.10. The saturating scale sits between, close to the cap. **So "pressure raises pleasure" on the uncapped scale is mostly the reward being paid.**
- **The yardstick decides whether pressure can help through how people live.** Choosers on net wellbeing over 26 weeks forgo households that are good for them on pleasure (here they never form at L0, against 80% for the planner). Pressure corrects that, and lived pleasure rises. Choosers on own pleasure or on everyone's pleasure already choose close to the planner, and pressure only distorts them.
- **The horizon matters less than the rule.** For own pleasure, 13 and 52 weeks give the same answers to the second decimal. What separates the rollout from the optimal chooser is that a rollout ignores the option to leave later. It under-forms by about 0.17 of weeks together against the planner, whatever the window. Old rule at 26 or 52 weeks on the capped scale: identical.
- **Formation quality.** Pressure's behavioural gain needs real under-forming. With the corrected rule at worth 0, a forecast bias of −0.06 turns lived pleasure positive (+0.012; free gap to the planner 0.030). At bias −0.03 it is still negative (−0.011). Over-forming (bias +0.03, +0.06) makes lived pleasure no better and, at worth −0.10, worse (−0.056, −0.065 against −0.047).
- **Withdrawal** always lowers lived pleasure and never holds anyone. Agents who foresee it form less (18% of the corrected chooser's formations are kept out). Its harm grows with time together and with the scale's honesty: at worth 0 it costs −0.008 capped and −0.029 uncapped. At worth −0.10, with fewer people together, −0.004 capped.
- **Exit stigma** barely moves pleasure for good choosers (−0.005 to +0.002), but it deters formation for the planner (15% kept out at worth 0): if leaving is costly, starting is less attractive.

The headline condition: **pressure raises pleasure through how people live only when choosers under-form badly, and raises total pleasure on the capped scale only when, in addition or instead, households are worth having and enough of the reward lands below the cap.** On the uncapped scale it raises pleasure wherever most pairs end up together, mostly by paying them.

## The three simulation results, mapped

Each agent set is placed on the household-worth axis by one observable that is not the pressure effect: the share of pairs that form at week 0 under the corrected rule with no pressure (G-L0). The exact corrected chooser forms 0.80 at worth 0, 0.40 at −0.10, 0.20 at −0.15 and 0.00 at −0.20. The simulation's G-L0 shares were 0.84 (v1), 0.06 (v2) and 0.42 (v2b). So v1 sits at worth 0, v2b at −0.10, and v2 near −0.20. All three ran on the capped scale.

| Agents | Placed at | Old rule L4 − L0, sim | exact | Corrected L4 − L0, sim | exact | Held at L4 (old, corrected), sim | exact |
|---|---|---|---|---|---|---|---|
| v1 | worth 0 | +0.021 | +0.024 | +0.003 | +0.008 | 0.29, 0.12 | 0.64, 0.22 |
| v2 | worth −0.20 | −0.046 | −0.068 | −0.038 | −0.048 | 0.49, 0.46 | 0.12, 0.45 |
| v2b | worth −0.10 | −0.003 | −0.027 | −0.004 | −0.011 | 0.26, 0.36 | 0.38, 0.54 |

**Signs.** The exact model gets the sign of all six effects, counting the two simulated nulls as small negatives (v2b's intervals were [−0.009, +0.002] and [−0.008, +0.000]). It gets the order too: v1 above v2b above v2, under both rules.

**Why each landed where it did, in the model's terms.**

- **v1, old rule (+0.021).** An under-forming chooser in a world where households are worth having. Net wellbeing over 26 weeks forgoes households that are good on pleasure; pressure corrects it. Lived pleasure rises in both: exact +0.019, simulation +0.012. This is the "pressure corrects a cautious rule" region the formation check found.
- **v1, corrected rule (+0.003).** A near-planner chooser in the same world. Lived pleasure falls (exact −0.021, simulation −0.010); the reward pays it back and a little more. The theorem's region: pressure cannot help how people live, and the small total is a payout.
- **v2 (−0.046, −0.038).** Households worth little on the capped scale. The step-back review gave the reason: accurate one-week agents count a household's costs below the cap and cannot count its benefits above it. Most pairs stay apart and pay the stigma, and pressure pushes the rest into households that hurt. Every chooser loses here, the planner included.
- **v2b (−0.003, −0.004).** Halfway back. Near the crossing on the capped scale, with the exact model a little more negative than the simulation.

**Where the mapping is loose.**

- **The old rule is far more cautious in the exact model.** It never forms at L0 at any worth on the cap; the household's old rule formed 0.51 (v1). The household's members differ in suffering in ways the toy does not have. So the old-rule held shares do not match (v1 0.64 against 0.29; v2 0.12 against 0.49: at worth −0.20 the exact old rule forms almost nobody even under pressure).
- **Households in the exact model do not decay.** The state drifts both ways. The simulation's households under v2 and v2b ended 72% to 96% of the time, from draining pots. The exact model ends about 27% at worth −0.10, and at −0.20 almost nobody forms. So it has no account of v2's "form, then come apart".
- **"Worth" stands in for three things at once.** The review showed v1 to v2 changed the weekly policy, v2 added bills, and v2b patched the bills. The toy has one dial for all of it. The placement says where each agent set's households sat on the scale, not why.
- **Sizes are not comparable.** The world's numbers are assumed and not fitted, so only signs and order are claims. The exact effects run larger than the simulation's under v2 and v2b.

## Under the new evaluator rule

The rule (2026-11-12): a win raises pleasure without raising domination; anything else is a trade-off. Here domination is held time (any person-week lived in a household one would not be in without pressure).

Searched: the dial at L0.5, L1 and L4, with all parts, each part alone, and all but withdrawal; five choosers (old rule, corrected, own over 13 weeks, own optimal, planner); bias −0.06, 0, +0.06; three scales; worth −0.10, 0, +0.05. Of 2,430 cells: 1,037 losses, 937 trade-offs, 447 no effect, **9 wins**.

All 9 wins are **reward alone**, in cells where pressure flips no decision at all (flipped 0, lived change 0): over-forming choosers or worth-having households, where every pair that would be together is together anyway. The gain is the reward paid, as far as the scale shows it (+0.001 to +0.010). No cell with stigma, exit stigma or withdrawal is a win. No cell where pressure changes anyone's choice is a win.

So, in this model, **H38 pressure is a win under the evaluator rule only when it does nothing a norm does**: it pays people who would have paired anyway. Every pressure that changes behaviour holds someone in, and so is at best a trade-off. Read with the step-back review's finding 8 (pressure holds people in under every agent set), that is the same answer from the other side: the freedom side of H38 is robust to the agent, the pleasure side is not.

A looser reading counts only stay readings, not pushed-in formation weeks, as domination. It admits 21 more cells (pleasure +0.001 to +0.005): pressure pushes a few pairs in (2% to 20% of formation decisions) and nobody is held at a later reading. All 21 use the old 26-week net-wellbeing rule, the badly under-forming chooser, and all but three are a reward alone, mostly at L0.5 or L1. So under the looser reading pressure can be a win in exactly the region where it can help at all: a small nudge to choosers who under-form (household worth −0.10 to +0.05 in these cells). Under the stricter reading (held time), those pushed-in weeks count, and none is a win.

## What the simulation should test next

1. **Lead with held share, and expect it above 0 in every pressured arm.** That is the one quantity whose sign the exact model never lets move.
2. **Report lived pleasure (without the direct terms) beside the total.** For choosers near the planner it should be negative. If the hybrid agent shows it positive, the free choices under-form, and the free gap should be measured directly (the formation check's forced-formation diagnosis, against a planner-like rule).
3. **Place the household on the worth axis before reading the sign.** G-L0 formation on the saturating scale says which side of the crossing the world is on. The exact model predicts a crossing near the middle of the formation range (about 0.6 formed at week 0, worth −0.05).
4. **Separate reward from stigma on the saturating scale.** Predicted: reward alone up, stigma alone down, at every worth. If they agree in sign, something other than the scale is moving them.
5. **Check two small predictions.** Exit stigma should deter formation for good choosers (kept out about 0.15). Withdrawal's harm should grow with weeks together, and never hold anyone.
6. **Give households a way to decline.** The exact model has no decaying households. If the hybrid agent's households still end 70% or more of the time, add a drift-down state to the toy before comparing again.

## Can be about / cannot be about

This can be about the sign of pairing pressure's effect on modeled pleasure, and on held time, in one two-person model with one formation and stay rule family, three scales, and assumed numbers. Its theorem (planner choosers cannot gain lived pleasure from pressure) holds for any numbers.

It cannot be about people, real norms, romance, partner choice or networks (as H38 itself). It cannot be about effect sizes: the world is assumed, not fitted. It explains the simulation's signs only through one placement axis, set from formation shares, and it does not model why households end.

## Reproduction

`uv run python -m mar.h38_exact` prints the sign map, the parts alone and the bias table; `--wins` adds the evaluator-rule search (a few minutes). Tests: `uv run pytest tests/test_h38_exact.py`.
