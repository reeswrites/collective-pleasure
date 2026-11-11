# Value consistency: the agents' own action values against the hedonic model

Wording rule: agents feel nothing; "pleasure", "suffering" and "value" are glosses for modeled numbers.

> **Note, 2026-11-11 (later): recalibrated.** Option (b) with (c) decided ran as [agent-recalibration.md](agent-recalibration.md). With `FixConfig(agent_values="v2", bills_hurt=True)` this same check passes its preregistered bars: one-week rank correlation 0.99 (was 0.43), the agent's best = the actual best in 97% of decisions (was 35%), every per-action mean gap under 0.005; 13 weeks 0.82, 52 weeks 0.68. The numbers below are the v1 agents, still the default. What is left is the horizon (paying a bill is worth +0.005 over one week and +1.0 over 52), and the recalibrated agents with bills that hurt form far fewer households.

Status: run once on 2026-11-11, approved by the author before any more experiments (log line 9a4a6cd). A known-answer check, not a hypothesis test: no prereg, no verdict, no parameter changed. Measurement code `src/mar/valuecheck.py`, run by `scripts/value_consistency.py`; tests `tests/test_valuecheck.py`. Scripted agents, no model calls, every number ASSUMED.

## Why

H39b ([h39b-makers-rerun.md](h39b-makers-rerun.md), "Why makers still lower pleasure") found two yardsticks. The agents' own plans valued a block of making at +0.019 and priced its time at 0.002, so 78% of blocks went into units the agent had planned to leave idle. The hedonic model, over 52-week rollouts, scored making at +0.03 against about 0.07 in money, rest and friends.

Agents choose by one yardstick and are scored by another. Every result where agents allocate time rests on how far apart the two are. This check measures it.

## How it was measured

The world is H39b's makers-off arm (M0): the H38 baseline at L0, exit fallback F4 with items, the per-persona suffering-weight rule over 52 weeks. All 120 confirmatory pairings, seeds 0 to 3, six sampled weeks per run (weeks 1 to 104), both partners: 5,760 decisions, 20,306 measured actions.

At each sampled decision the agent's own score for every action it scores is read without noise, minus the sanction estimate it subtracts when a soft rule would be broken. That is the number it chooses on. Call it **perceived**. Doing nothing at the call is 0, the agent's own floor.

Then each action is forced in an isolated copy of the world at that call, and compared with a copy in which the agent does nothing there. The difference in the agent's own modeled outcome, summed over the next 1, 13 and 52 weeks, is the **actual** value. The rest of the world plays on as it would: the partner, later weeks, later choices. After the decision week every random stream restarts from the same seed in both copies, so the copies differ by the decision, not by shifted draws.

The main sample uses the week's last call (the third pass). Everything earlier in the week is then the same in both copies, so the difference is one unit of that action against idle. Two smaller samples check the design:

- **harness**: the formation retries and 13-week stay readings also run inside the copies (40 pairings, seed 0, 3 weeks; 240 decisions).
- **first call**: the week's first call, so the rest of the week re-plans (40 pairings, seed 0, 4 weeks; 320 decisions).

"Net" below is pleasure minus both kinds of suffering, the evaluator's net line. Clipped pleasure (the verdict measure) and unclipped pleasure are in `runs/value-consistency/analysis.json` and quoted where they differ.

Checks: the measurement leaves the live world bit-identical; forcing the action the world chose reproduces the world exactly; a soft rule's sanction estimate is in the perceived value (tests 1 to 6).

## In one paragraph

**The agents' values and the hedonic model agree on direction only loosely, and not by a single scale.** Over one week the rank correlation between perceived and actual value is 0.43 (0.39 within a decision). Over 13 weeks it is 0.30, over 52 weeks 0.19. The agent's own best action is also the best by actual one-week value in 35% of decisions. When it picks between its best and its next best, it is right 40% of the time at one week and 51% at 52 weeks: a coin flip. The gaps are not one fixed exchange rate. Work is underpriced about sixfold, friends about twofold, rest is about right on average but wrong by level, and paying the shared bills and spending on oneself have the wrong sign. **Most of the gap traces to four things in the agents' code, and one to a modeling choice in the hedonic model.**

## Per action: perceived against actual

Own net value, main sample. Actual is the summed difference over the horizon, with a 95% bootstrap interval resampling runs. "rho" is the rank correlation within that action. "Sign" is the share of cases where the agent wants the action (perceived above its floor) and the action lowers net, or the reverse.

| Action | n | Perceived | Actual, 1 week | Actual, 13 weeks | Actual, 52 weeks | rho (1 wk) | Sign disagrees (1 wk) |
|---|---|---|---|---|---|---|---|
| work | 2,574 | +0.018 | +0.110 [+0.102, +0.117] | +0.154 [+0.127, +0.180] | +0.148 [+0.048, +0.253] | 0.44 | 26% |
| see a friend | 4,342 | +0.022 | +0.050 [+0.048, +0.052] | +0.058 [+0.051, +0.065] | +0.055 [+0.027, +0.079] | 0.62 | 25% |
| time together | 1,373 | +0.026 | +0.041 [+0.037, +0.045] | +0.041 [+0.025, +0.059] | +0.055 [−0.008, +0.141] | 0.45 | 25% |
| rest | 4,423 | +0.030 | +0.027 [+0.026, +0.028] | +0.094 [+0.079, +0.109] | +0.083 [+0.034, +0.130] | 0.02 | 48% |
| pay shared bills | 2,798 | +0.005 | −0.108 [−0.116, −0.100] | −0.131 [−0.162, −0.103] | −0.109 [−0.195, −0.030] | 0.06 | 42% |
| spend on oneself | 4,795 | −0.019 | −0.113 [−0.118, −0.107] | −0.356 [−0.382, −0.331] | −0.431 [−0.507, −0.365] | 0.36 | 33% |

Requests, refusals and gifts almost never came up at the last call (one request), so they are not measured here.

Pooled over all actions:

| Horizon | rho, pooled | rho, within a decision | Slope of actual on perceived | Agent's best = actual best | Best beats next best |
|---|---|---|---|---|---|
| 1 week | 0.43 | 0.39 | 1.2 | 35% | 40% |
| 13 weeks | 0.30 | 0.29 | 3.1 | 30% | 50% |
| 52 weeks | 0.19 | 0.22 | 3.7 | 27% | 51% |

On clipped pleasure, the verdict's measure, agreement is lower still: rho 0.19 at one week, 0.10 at 52. The cap at 1 eats most of what time together does (one week: unclipped +0.099, clipped +0.026).

The two design checks agree. With the formation retries and stay readings inside the copies, rho is 0.43, 0.30 and 0.20 at the three horizons, and the per-action means move little at one week (work +0.105, pay bills −0.100, spend on oneself −0.111). The 52-week numbers are noisier there (rest +0.40, pay bills +0.50, wide intervals). At the first call the rest of the week re-plans around the forced action, and agreement is lower (rho 0.33, 0.23, 0.14). The best-against-next-best share there (8%) mostly counts ties: the agent does both actions that week anyway, in a different order.

## What the agent leaves idle

In 17% of last calls nothing clears the agent's floor and it does nothing. In those calls resting would have been worth +0.027 net over one week [+0.023, +0.030] and +0.057 over 13 weeks, and seeing a friend +0.016 over one week. Over 13 weeks the best available action beats idle in 58% of them.

This is the H39b number seen from the other side. A block of making takes 1 unit, half a rest. By the hedonic model an idle unit is worth roughly +0.013 over one week and +0.03 over 13 weeks. The planner priced it at 0.002. A block worth +0.019 to its maker is then roughly break-even or a loss, not nearly free.

## Where the gaps come from

Each large gap, traced to code. "Side" says which side is out of line with the repo's stated theory: the agent is "a utility-like policy over the hedonic model" (`PersonaAgent` docstring; ADR 0010, decision 7), and the evaluator judges on pleasure, everyone counted. Agents may misforecast on purpose; a gap nobody chose is a bug.

### 1. The agent reads its needs at the start of the week (timing; agent side; bug)

`PersonaAgent.utilities` (`src/mar/worlds/household.py`) values a need gain as `salience x marginal x min(gain, 1 - level)`, with `level` the start-of-week need level. The hedonic model reads the level at the end of the week, after `Hedonic.tick` (`src/mar/hedonic.py`) has applied the weekly drift: rest −0.1, connection −0.2 when living together, money −2 of living cost (a quarter of the money scale). The agent's own earlier actions that week are not in the level either.

So the agent prices upkeep at zero when a need is full, and prices a second or third rest as if the first had not happened:

| | Perceived | Actual, 1 week |
|---|---|---|
| rest, rest level ≥ 0.9 | +0.0005 | +0.017 |
| rest, rest level < 0.5 | +0.106 | +0.020 |
| friend or together, connection ≥ 0.9 | +0.019 | +0.048 |
| work, money level 1 | +0.011 | +0.085 |
| work, money level 0.5 to 1 | +0.037 | +0.202 |

This is why rest has a rank correlation of 0.02: the agent overvalues it when tired and undervalues it when rested. The H39b planner (`makers.WeekPlanner`) inherits it: it updates counts and money after each planned action, but not need levels.

### 2. Need and aspiration terms are about half the hedonic model's weight (units; agent side; bug where mixed with pleasure units)

Above half full, the hedonic model turns one unit of need level into `salience` of net value (pleasure `0.5 x salience x 2`); below half, into `2 x salience` (suffering falls). The agent uses `0.6 x salience` and `1.5 x salience` (`_m`), then divides by 1.2 (rest, friends, together) or 1.5 (work). An aspiration step is worth `0.8 x weight` to the hedonic model (0.5 pleasure plus 0.3 less suffering); the agent counts 0.5 (friends, together, before the 1.2) or 0.3 (savings). One week of an aspiration or a need is worth roughly half as much to the agent as to the model.

On its own a common scale would not change any choice. It matters wherever the agent's number is set against a number in pleasure units: the floor of 0.003 that decides idle, the sanction estimates (gap 4), and H39b's making choice, which adds block values in pleasure units (`makers.block_values`, the receiver's liking) to a time cost in agent units (`makers.opportunity`, `plan_value`). That mix is the main reason the planner found making nearly free.

### 3. Terms the hedonic model pays and the agent does not see (missing terms; agent side)

- **Time together's own pleasure**: `together_event` 0.10 per session (`Hedonic.close_week`) is in the model since ADR 0010 and in no agent utility. The partner's share of the session is in the agent only as `0.05 x prosocial x capacity x partner deficit`. Over one week the partner gains +0.021 from a session the agent starts.
- **Later additions**: fix 1 contact amplification and release (`_contact_terms`), fix 2 bought pleasure from spending (`bought_pleasure`, about 0.038 for one spend), and the lever strand payoffs from bond quality (`_lever_terms`). None reached `utilities`.
- **Stocks that carry over**: money, rest, connection, bond quality and the spiral (B, capacity) all persist. The agent counts one week. Work's value grows from +0.110 at one week to +0.154 at 13 weeks; for the partner it grows from −0.001 to +0.090 at 52 weeks (shared money, the pot).

Whether an agent should foresee these is partly the author's choice (people misforecast). But the together pleasure and the fix and lever terms were not left out on purpose: they were added to the model without touching the agent. That is unintended.

### 4. Sanctions are priced at a fifteenth of what they cost (units; agent side; likely bug)

Baseline card D1 makes spending on oneself while bills are unpaid a soft rule with a one-month warning. The agent's estimate is `SANCTION_UTILITY["warn"]` 0.01 a week, 0.04 in all. The world charges `WARN_FRICTION` 0.15 a week of offsettable suffering, 0.6 in all. When the rule binds, perceived is −0.047 and actual −0.173 over one week and −0.667 over 13 weeks. Both constants are marked ASSUMED; nobody chose the ratio.

### 5. Paying the shared bills helps nobody the agent can see (sign; hedonic side or a modeling choice)

The agent values paying a bill for the month's gap, the threat to the shared pot, its security salience and a prosocial share (`utilities`, `spend_shared`). In the hedonic model an unpaid bill is paid from the shared pot at month end at no hedonic cost (`step_week`, settlement). Security is hit only when the pot itself cannot cover it. So paying from one's own money is a pure loss to the payer: −0.108 net over one week, mostly money and the "money denied" condition. The partner gains +0.002 over one week and +0.045 over 52; the pair together still loses.

Here the agent's view (bills matter; a draining pot is a threat) is closer to the repo's stated theory of a household than the model's (the pot pays silently). This is a modeling choice for the author: either a covered bill should cost something in the hedonic model (stress, security), or agents should stop treating bills as urgent.

A related meaning gap: the agent's `spend_self` adds `0.05 x autonomy weight`, but the hedonic model's autonomy aspiration measures how open the rules are, not spending. Spending on oneself is worth +0.002 to the agent when no rule binds, and −0.067 actual over one week (money, net of the bought pleasure).

### What the gap is, by kind

| Kind | Where | Size | Side |
|---|---|---|---|
| Timing (levels before the week's drift and before earlier actions) | `PersonaAgent.utilities`, `need()`; `WeekPlanner` | upkeep at full needs priced near 0 against +0.02 to +0.09 a week; tired rest priced 5x too high | agent; bug |
| Units (half weight on needs and aspirations) | `_m`, the /1.2 and /1.5 divisors, the 0.5 and 0.3 aspiration weights | about 2x; matters where mixed with pleasure units | agent; bug in `makers.opportunity` |
| Units (sanction estimate) | `SANCTION_UTILITY` against `WARN_FRICTION` | 15x | agent; likely bug |
| Missing terms (together pleasure, contact, bought pleasure, levers, the partner) | `utilities` against `close_week`, `_fix_terms`, `_lever_terms` | together +0.10 a session raw; partner +0.02 | agent; unintended |
| Horizon (stocks carry over) | one-week utilities against persistent levels, money, bonds, B | work +0.11 → +0.15; rest +0.03 → +0.09 | agent; partly a choice |
| Sign (bills; autonomy) | `spend_shared` and `spend_self` against the pot's silent cover and the rules-openness autonomy aspiration | −0.11 a payment | model or choice; for the author |

Formation and stay are a third yardstick, already the hedonic one: `negotiation.forward_values`, `baseline_value` and `alone_value` play the world forward and score it with `wellbeing`. So households form on the hedonic model's forecast of lives whose weeks are chosen on the agents' utilities. The H38 formation check fixed the yardstick for formation; this check is about the weeks.

## Options for the author

None is applied. Each would change model behaviour, so each needs its own prereg and rerun.

**(a) Agents choose on the hedonic model's forecast.** Each action is scored by a copy of the agent's own `Hedonic` played one week (or a few) forward with that action, as this check does. Agents become near-perfect one-week forecasters; misforecasting would have to be added back on purpose. Likely changes: every result where agents allocate time. Bills would rarely be paid from private money while the pot pays them (gap 5), so pot dynamics and exits move: the exit fallbacks (F4 contribution shares come from bill payments) and H38 most. H39 and H39b would change most of all: the making choice would set block values against a real time cost. The formation check and the retest move through the rollouts, which replay the agents' weeks. Cost: much slower runs.

**(b) Keep the heuristics; recalibrate them to the hedonic model's known answers.** Read levels after the week's drift and after the agent's earlier actions that week (gap 1); put needs, aspirations and the together pleasure on the model's scale (gaps 2 and 3); price sanctions at the friction they cost (gap 4). The target is this check's one-week values, an external known answer, never an experiment's outcome. Pass bar: one-week rank correlation and slope near 1 per action. Likely changes: the same results as (a), smaller. H39b most (the time cost of a block rises from 0.002 to about 0.01 to 0.03, so fewer blocks and likely a smaller harm from makers), then H38 and the formation check (more rest and friends at full levels, so different weeks in the rollouts), then the exit fallbacks (spending on oneself drops when rules bind). Bills (gap 5) need (c) or a decision first.

**(b2) Keep a deliberate forecasting bias as a persona trait.** After (b), add one named, documented bias per persona (for example, a present bias that discounts carried-over stocks, or underweighting others' pleasure). Its size would come from the literature, not from fitting. Likely changes: the same as (b) for the default, plus a new axis that could explain heterogeneity. It does not by itself fix the unintended gaps, which are not traits.

**(c) Fix the hedonic model where it is the wrong side.** Two candidates, both the author's call: a bill the pot covers could cost something (security or friction), and the autonomy aspiration's meaning could be settled one way for both sides. Clipping at 1 is a known limit, not part of this. Likely changes: exit fallbacks and H38 (pot draw-downs and bill payments), the formation check (household rollouts look different when bills bite), and anything read on clipped pleasure near the cap. Makers results move only through the pot.

| Past result | (a) | (b) | (b2) | (c) |
|---|---|---|---|---|
| H38 pairing norms | likely changes | may change | as (b) | may change |
| H38 formation check | likely changes | may change | as (b) | likely changes |
| Exit fallbacks (F3 to F5) | likely changes | may change | as (b) | likely changes |
| H39 | likely changes | likely changes | as (b) | small |
| H39b | likely changes | likely changes | as (b) | small |
| Retest | likely changes | may change | as (b) | may change |

"Likely changes" means the result rests on the gap directly; "may change" means through rollouts or second-order behaviour. None of these were rerun here.

## Recommendation

Do (b) first, with (c) decided for bills. Gaps 1 to 4 are unintended and fixable in the agent without making it a perfect forecaster. Pre-register the recalibration against this check's one-week known answers, rerun this check as the pass test, then rerun H39b and the formation check before citing either again. Decide (b2) only after: a bias that is chosen is a finding; the current one is an accident.

Until then, treat any result that depends on how agents spend their week as conditional on these agents. The H39b claim "makers lower pleasure" stands as measured, but its explanation is now clear: the making choice mixed pleasure units with agent units and priced idle time at near zero.

## Misses and weaknesses, plainly

- **The perceived value changed once after a look at the data.** A preview showed spending on oneself costing mostly friction. The first version read the propose() score; step_agent also subtracts the sanction estimate. The definition was corrected to the number the agent actually chooses on, and the main sample rerun. The first version's rows are kept (`runs/value-consistency/rows-pre-sanction.jsonl`).
- **52-week effects are noisy.** One unit of action changes later choices, and the branches drift apart even with common random numbers. The 52-week intervals are wide, and the harness sample's 52-week means differ from the main sample's for rest and bills.
- **The last call favours some actions.** At the third pass few units are left, so work (4 units) is measured less often, and the agent is already partly through its week. The first-call sample answers a different question (the week re-plans).
- **"Actual" is the model's answer, not the truth.** The check asks whether agents agree with the hedonic model, not whether either is right about people.
- **One world.** The M0 arm only: no makers, no pressing personas, the baseline cards.

## Can be about / cannot be about

This can be about how the scripted persona agents' action utilities compare with what the same actions do to their modeled pleasure in the H38/H39b makers-off household, and where in the code the two part.

It cannot be about how people value their time, or about whether any result that rests on agents' weeks is wrong: only about which ones rest on this gap.

## Reproduction

`uv run python scripts/value_consistency.py --run` (main, about 11 minutes on 3 workers), `--harness`, `--first`, `--analyze`. Rows in runs/value-consistency/ (not committed). Tests: `uv run pytest tests/test_valuecheck.py`.
