# Bill horizon: results

Wording rule: agents feel nothing; "pleasure", "suffering" and "value" are glosses for modeled numbers.

Status: run on 2026-11-12 after the preregistration ([agent-bill-horizon-prereg.md](agent-bill-horizon-prereg.md), commit 5f18811; code e7d45cf; Amendment 1 committed after the pass test and before the formation rerun). Follows [agent-recalibration.md](agent-recalibration.md) and the author's decision ("yes let's try that"). Scripted agents, no model calls, every new number ASSUMED or measured.

## In one paragraph

**The bill horizon fails its pass test, and still changes the world a lot.** Before changing anything, the value check measured every carry-over term at 1, 4, 13 and 52 weeks: only the bill's gap clears the check's bar at 4 weeks (+0.030), money, rest and bonds stay small at every horizon, and the long run runs through the shared pot and whether the household lasts. v2b, which credits a bill payment with the settlement it feeds, then **fails at 4 weeks on the bill clauses only**: it over-values a payment by 0.029 (v2 under-valued it by 0.026). The credit assumes nobody else pays before the settlement; v2b agents do, so a payment skipped now is made later. Every other clause holds, and the one-week agreement is unchanged.

**The formation check under v2b.** Households form about halfway back toward the old agents (G-L0 at week 0: 0.42; v2 0.06, v1 0.84) and last much longer (72% of formed households end; v2 81%, v1 29%), short of the preregistered "plausible" rates (≥ 0.50, ≤ 0.67). The verdicts do not move from v2: C1 within margin, C2 fails, C3 fails. But v2's big harm from pressure was the bills: under v2b pressure is close to neutral (C1 −0.004 [−0.008, +0.000]; H38's old-rule gain −0.003 [−0.009, +0.002]), neither v1's gain nor v2's harm. A general planning horizon is not needed; a horizon on the shared pot, through a month plan for the bill, is.

## What changed

`agent_values="v2b"` (`agent_values.settle_credit`): v2, plus a credit on paying a shared bill. Before the settlement week, a payment of 3 is also worth what it does to the payer's close **in the settlement week it feeds**, projected with the month's funding as it stands (nobody else pays first), and the prosocial share of the same for the partner. In the settlement week the week's own close already holds the bill. No new number: the credit is `week_net`'s own settlement arithmetic (bill stress, the pot draw and its lost buffer, the late fee, eviction). Every other action's value is v2's exactly (test). v1 and v2 reproduce bit for bit (pins from commit dff1c4d, before v2b existed; `tests/test_agent_values.py`).

Known answers, as tests: with an empty pot and a bill of 10, each of the first three payments is credited 0.09 and the one that funds the bill more than 0.40; a couple with 12 each and an empty pot funds the bill before the settlement under v2b and carries arrears under v2; a payment into a funded bill is valued at the floor or below, as v2 values it.

## The carry-over terms, measured first

The value check rerun under v2 with bills, a 4-week horizon added (5,760 decisions; the 1-, 13- and 52-week numbers reproduce the recalibration's exactly). Each action's effect on the agent's own net, split by the observer groups that carry the model's stocks; the **gap** is the k-week effect minus the 1-week one, what a one-week valuer cannot see. Full table in the prereg (step 2); the summary:

| Gap, v2 world | work | rest | see a friend | together | pay shared bills | spend on oneself |
|---|---|---|---|---|---|---|
| 4 weeks, net | −0.004 | +0.010 | +0.003 | −0.003 | **+0.030** | −0.006 |
| 13 weeks, net | +0.011 | +0.014 | +0.005 | −0.019 | **+0.142** | −0.010 |
| 52 weeks, net | +0.086 | +0.063 | +0.004 | **−0.382** | **+1.001** | −0.019 |
| 52 weeks: pot (security + bill friction) | +0.023 | +0.016 | +0.003 | −0.181 | +0.720 | −0.003 |
| 52 weeks: money | −0.000 | +0.010 | −0.001 | −0.008 | −0.017 | +0.003 |
| 52 weeks: rest | −0.016 | +0.010 | +0.000 | −0.011 | +0.027 | −0.007 |
| 52 weeks: connection (need, partner, friends) | +0.029 | +0.036 | −0.002 | −0.131 | +0.233 | −0.006 |
| 52 weeks: bonds (strands) | +0.001 | +0.002 | +0.010 | +0.001 | +0.002 | −0.001 |
| 52 weeks: conditions (trapped, denied) | +0.025 | +0.010 | −0.001 | −0.118 | +0.204 | −0.006 |

Trust is not a hedonic term; it reaches net only through what partners then do, inside the rows above. At 4 weeks only the bill clears the check's 0.015 bar. Money, rest and bonds are small at every horizon. The long run runs through the pot and through whether the household lasts.

## The pass test: FAIL, on the bill clauses only

`--v2b --run`, `--v2b --passtest` (runs/value-consistency-v2b/, 5,760 decisions, 20,937 measured actions, 1,844 s on 3 workers). Rows held to 4 weeks (soft-rule rows to 13).

| ID | Quantity | v2 (before) | v2b | Bar | |
|---|---|---|---|---|---|
| U1 | pooled rank correlation, 4 weeks | 0.89 | 0.81 | ≥ 0.70 | holds |
| U2 | within-decision rank correlation | 0.86 | 0.78 | ≥ 0.60 | holds |
| U3 | agent's best = actual best | 75% | 62% | ≥ 60% | holds |
| U4 | best beats next best | 77% | 69% | ≥ 60% | holds |
| U5 | slope | 1.03 | 1.04 | 0.8 to 1.25 | holds |
| **U6** | paying a shared bill, perceived vs 4-week actual | +0.009 vs +0.035 (gap 0.026) | **−0.022 vs −0.051 (gap 0.029)** | ≤ 0.015 | **fails** |
| **U6b** | same, before the settlement week | −0.014 vs +0.022 (gap 0.036) | **−0.017 vs −0.054 (gap 0.037)** | ≤ 0.015 | **fails** |
| O1 to O4 | one week, the five other actions | 0.993, 0.992, 97.7%, 92.0% | 0.986, 0.989, 97.0%, 92.2% | within 0.05 | hold |
| O5 | one-week slope | 1.02 | 1.03 | 0.8 to 1.25 | holds |
| O6 | one-week gap per other action | all < 0.005 | all < 0.004 | ≤ 0.015 | holds |

**FAIL.** The gap is the same size as before with the sign turned: v2 under-valued a bill payment by 0.026 to 0.036, v2b over-values it by 0.029 to 0.037. On own + prosocial × partner net the verdict is the same (U6 gap 0.021, U6b 0.029); on unclipped pleasure − suffering it fails more widely, as v2 did. All rows at one week (bills included, no bar): 0.93, 0.94, 86%, 79%.

**Why.** By week of the month (prereg Amendment 1): in v2's world nobody pays early, so a payment made before the settlement is one the settlement would otherwise miss, worth +0.011 to +0.030 over 4 weeks against −0.014 in its own week. In v2b's world the agents do pay early, so a payment skipped at this call is made at a later call, and paying now is worth only its own week's cost (−0.047 to −0.059: money, and the denial condition for the poorer payers). The credit assumes nobody else pays first; v2b agents are the somebody. The disagreement is in the counterfactual, not in the settlement arithmetic, and it moves with the agents.

**No iteration** (Amendment 1). The prereg allowed up to three, each only where the design disagrees with the check. The check's answer here depends on the agents' own later calls: a credit that assumes no later payment over-values by 0.037, a credit of 0 under-values by 0.036. Picking a rule in between so the world it makes lands inside the bar is fitting a number to the check's outcome through the agents' behaviour. What is missing is a plan (the household fixing the month's payments once), and that is a new design.

**What v2b does to the world.** 49% of sampled decisions are inside a household (v2 16%, v1 61%). Payments are measured at 2,740 decisions (v2 1,042). Over 52 weeks, time together is now worth +0.000 on average (v2 −0.38) and paying a bill +0.26 (v2 +1.01): with bills paid, households stop draining.

## The formation check under v2b

As preregistered (formation check Amendment 2): G-L0, G-L4, G-W4, G-L1 under the corrected rule and H38's L0, L4, W4 under the old rule, all with `agent_values="v2b"` and `bills_hurt`; 120 pairings × seeds 0 to 3, 3,360 runs (rows in runs/h38-formation-v2b/; `scripts/bill_horizon_compare.py` sets it beside v1 and v2). It runs on v2b as tested, so on agents that **fail** the 4-week pass test by over-valuing bill payments.

**Households come back about halfway, and hold together better, but not at the preregistered "plausible" rates.**

| | old L0 | old L4 | old W4 | G-L0 | G-L1 | G-L4 | G-W4 |
|---|---|---|---|---|---|---|---|
| pleasure, v1 | 0.928 | 0.949 | 0.917 | 0.956 | 0.957 | 0.959 | 0.940 |
| pleasure, v2 | 0.974 | 0.928 | 0.973 | 0.978 | 0.969 | 0.941 | 0.977 |
| pleasure, v2b | 0.975 | 0.972 | 0.980 | 0.985 | 0.982 | 0.981 | 0.986 |
| formed at week 0, v1 | 0.51 | 0.88 | 0.49 | 0.84 | 0.89 | 0.98 | 0.71 |
| formed at week 0, v2 | 0.16 | 0.49 | 0.15 | 0.06 | 0.08 | 0.53 | 0.12 |
| formed at week 0, v2b | 0.47 | 0.74 | 0.41 | 0.42 | 0.58 | 0.94 | 0.49 |
| weeks together, v1 | 0.53 | 0.88 | 0.44 | 0.82 | 0.86 | 0.92 | 0.73 |
| weeks together, v2 | 0.16 | 0.31 | 0.13 | 0.19 | 0.22 | 0.43 | 0.18 |
| weeks together, v2b | 0.41 | 0.71 | 0.38 | 0.47 | 0.55 | 0.85 | 0.52 |
| households that end (of formed), v1 | 0.60 | 0.23 | 0.67 | 0.29 | 0.28 | 0.20 | 0.35 |
| households that end, v2 | 0.96 | 0.88 | 0.98 | 0.81 | 0.85 | 0.84 | 0.80 |
| households that end, v2b | 0.86 | 0.34 | 0.70 | 0.72 | 0.67 | 0.35 | 0.47 |
| stay readings held by pressure, v2b | 0 | 0.26 | 0.03 | 0 | 0.26 | 0.36 | 0.10 |

Plausibility rule (fixed in the prereg): G-L0 forms at week 0 in 0.42 of pair-seeds (bar 0.50) and 0.72 of formed households end (bar 0.67). **Neither clause holds**, though both moved most of the way from v2 (0.06, 0.81) toward v1 (0.84, 0.29). Under pressure (L4) households now form and last much as they did under v1 (G-L4 0.94 formed, 0.35 end).

Differences, paired by pairing, 95% bootstrap:

| Finding | v1 | v2 | v2b | Survival label (prereg) |
|---|---|---|---|---|
| **C1** G-L4 − G-L0, pleasure | +0.003 [−0.004, +0.009], within margin | −0.038 [−0.043, −0.033], within margin | **−0.004 [−0.008, +0.000]**, within margin (Holm p 1.0) | verdict stable; estimate **v1 restored** (no clear effect) |
| C1 net | −0.002 [−0.020, +0.014] | −0.103 [−0.121, −0.086] | +0.002 [−0.012, +0.015] | v1 restored |
| C1 without the direct terms | −0.010 [−0.015, −0.005] | −0.009 [−0.012, −0.005] | −0.001 [−0.004, +0.003] | neither (now null) |
| C1 weeks together | +0.10 | +0.24 | +0.38 [+0.34, +0.43] | stable (larger) |
| **C2** G-W4 − G-L0, pleasure | −0.017 [−0.022, −0.011], holds | −0.001 [−0.003, +0.001], fails | **+0.001 [−0.000, +0.003], fails** | v2 confirmed |
| **C3** G-L0 − old L0, pleasure | +0.028 [+0.023, +0.033] | +0.005 [+0.002, +0.008] | +0.010 [+0.007, +0.013] | stable |
| C3 formation at week 0 | +0.33 [+0.26, +0.39] | −0.10 [−0.16, −0.04] | **−0.05 [−0.11, +0.01]** | neither; **C3 fails** (v2 confirmed) |
| H38's gain, old L4 − L0 | +0.021 [+0.013, +0.028] | −0.046 [−0.053, −0.040] | **−0.003 [−0.009, +0.002]** | neither (now null) |
| old L4 − L0 without the direct terms | | | +0.007 [+0.003, +0.011] | descriptive |
| H38's withdrawal, old W4 − L0 | −0.011 [−0.016, −0.007] | −0.001 [−0.003, +0.002] | **+0.005 [+0.002, +0.008]** | neither (sign flips) |
| G-L1 − G-L0 | +0.001 (null) | −0.009 [−0.011, −0.007] | −0.003 [−0.005, −0.001] | v2 confirmed, smaller |

Verdicts under v2b: **C1 within margin, C2 fails, C3 fails**, the same as under v2. Pressure's 52-week formation push (pairs pushed in by L4: 249 of 480, mean change −0.005) is near zero in pleasure.

What this says, plainly:

- **The v2 harm from pressure was mostly the bills.** With bills paid, pressure neither helps nor hurts pleasure much, under either rule (−0.004 corrected, −0.003 old). H38's original gain (+0.021) does not come back; v2's reversal (−0.046) does not hold either. Without its direct terms, pressure now nudges pleasure up a little under the old rule (+0.007) because it forms households that now last; the stigma on those who stay apart takes it back.
- **C1 is "within margin" under all three agent sets.** That verdict is the one result here that has not moved.
- **Withdrawal stays harmless or slightly positive** (+0.005 under the old rule): C2 does not come back with the households.
- **The corrected rule still does not form more households at week 0** (−0.05, interval crossing 0), so C3 fails as under v2, though the corrected rule still yields more pleasure (+0.010).
- **Pleasure is high everywhere (0.97 to 0.99)** and the arms differ by less than 0.015: with accurate one-week agents who also pay their bills, the household world sits near the pleasure cap whatever the pairing norm. Unclipped pleasure still separates them (C1 +0.080 [+0.070, +0.090]).

**Descriptive, v2b without bills** (G-L0, G-L4, O-L0, O-L4): running at the time of writing; added below when done.

## Is a general planning horizon needed?

Measured twice: in v2's world (above) and in v2b's, where households live (49% of decisions inside one).

| Gap, v2b world | work | rest | see a friend | together | pay shared bills | spend on oneself |
|---|---|---|---|---|---|---|
| 4 weeks, net | −0.004 | **+0.023** | +0.001 | −0.004 | −0.003 | −0.009 |
| of which money | −0.007 | +0.028 | +0.000 | −0.004 | +0.005 | +0.003 |
| 13 weeks, net | +0.010 | +0.030 | +0.001 | −0.009 | +0.017 | −0.017 |
| 52 weeks, net | **+0.232** | **+0.167** | +0.008 | −0.003 | **+0.303** | −0.070 |
| of which pot (security + bill friction) | +0.129 | +0.081 | −0.001 | −0.076 | +0.189 | −0.019 |
| of which conditions | +0.068 | +0.034 | +0.002 | +0.022 | +0.088 | −0.021 |
| of which connection | +0.064 | +0.055 | +0.007 | +0.011 | +0.077 | −0.024 |
| of which money, rest, bonds (each) | ≤ 0.004 | ≤ 0.052 | ≤ 0.009 | ≤ 0.024 | ≤ 0.022 | ≤ 0.011 |

Three things follow.

1. **The separate stocks do not need a horizon.** Money, rest and bonds carry over little in either world: each at most about 0.05 over 52 weeks for any action (bonds at most +0.010, from a friend's visit), against +0.72 for the pot on a bill payment. A general planning horizon over every stock would buy little and cost a rollout per decision.
2. **The pot does, and it is not one action's problem.** Once households last, the long-run gap moves from paying the bill into earning and resting: work +0.23 over 52 weeks, of which the pot +0.13, then the conditions and connection that a household with a funded pot keeps. Every action that changes how much money reaches the pot (work, spending on oneself, paying) carries the pot's future.
3. **The 4-week check cannot test a horizon on its own.** The actual of paying now depends on whether the same agents pay later (the pass test's failure). Rest's new 4-week gap (+0.023, mostly money) is the same thing: the unit not spent resting is spent paying.

**Proposal.** Not a general planning horizon. Two pieces, in order:

- **(a) A month plan for the bill.** At the month's first call, the household sets each member's share of the month's bill from the model's own numbers (their money and income), and an agent values a payment by whether it keeps the plan whole; skipping a planned payment is valued as the settlement shortfall it leaves at the agent's last call before the settlement. This gives "not paying now" a defined later, which the bill horizon lacked. Pass test: this check at 4 weeks, unchanged bars.
- **(b) A pot runway term.** Value a change to the pot (a surplus payment, a safety-net draw, money that will fund the plan) by the months of bills it covers, read through the model's own bill-stress dryness (pot ÷ 30) and lost-buffer terms over the next three settlements, with the plan held fixed. Pass test: the check at 13 weeks for work, spending on oneself and paying bills, with the one- and four-week lines as guards.

Option (b2) from the recalibration, a persona's own discounting, stays a separate question: it is a chosen bias to be studied, not a repair.

## What is still inconsistent

- **The bill's counterfactual.** v2b over-values a payment by 0.03 at 4 weeks (v2 under-valued it by as much). A household plan for the month is the missing piece (proposal (a) above).
- **The pot's long run.** In v2b's world, work and rest carry +0.23 and +0.17 over 52 weeks, mostly through the pot. No agent sees it.
- **Time together** stays the weakest one-week match (inherited from v2), and the partner's consent still uses v1's threshold.
- **Unclipped pleasure.** Pleasure is at 0.97 to 0.99 in every formation arm; the clip hides most of what pressure and bills do (unclipped C1 +0.080).
- **The bill numbers** are ASSUMED, one point each.

## Recommendation

Do not cite H38's or the formation check's direction as settled: across three agent sets the old-rule effect of pressure went +0.021, −0.046, −0.003, each time for a modeling reason, not a norm. What has held across all three is C1 "within margin" and C3's pleasure gain from the corrected rule.

Next, the smallest step: **a month plan for the bill** (proposal (a)): the household sets each member's share at the month's first call, agents value keeping it, preregistered with this same 4-week check and unchanged bars. It gives "not paying now" a defined later, which is exactly where v2b failed. Rerun the formation check only if it passes. The pot runway term (b) comes after, with a 13-week pass test.

## Can be about / cannot be about

This can be about whether v2 agents that credit a shared-bill payment with the settlement it feeds agree with the hedonic model over 4 weeks (they do not, by 0.03, the other way round), what the carry-over terms are worth at 1, 4, 13 and 52 weeks in this household, and what the H38 formation check shows under such agents.

It cannot be about how people budget, plan or decide to live together; about any stock other than the month's bill being fixed (the others are measured, not changed); or about the bill numbers, which are ASSUMED.

## Reproduction

`uv run python scripts/value_consistency.py --v2h4 --run` then `--v2h4 --gaps`, `--v2h4 --passtest`, `--v2h4 --reach`; the same with `--v2b`. `uv run python scripts/h38_formation_check.py --v2b --run` and `--v2b --analyze`; `--v2bnobills --run`. `uv run python scripts/bill_horizon_compare.py`. Tests: `uv run pytest tests/test_agent_values.py -m ""`. Rows in runs/ (not committed). Wall time on 3 workers: each check about 25 to 31 minutes; formation check about 1.6 hours of compute (6.4 hours wall: the machine slept for 4.7 of them).
