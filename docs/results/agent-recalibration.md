# Agent recalibration and bills that hurt: results

Wording rule: agents feel nothing; "pleasure", "suffering" and "value" are glosses for modeled numbers.

Status: run on 2026-11-11 after the preregistration ([agent-recalibration-prereg.md](agent-recalibration-prereg.md), commit 84fa28f; code 4764e88; Amendments 1 and 2 committed before the runs they touch). Follows [value-consistency.md](value-consistency.md) and the author's decision (experiments/changes.jsonl, 2026-11-11T21:53:50Z, "Yes, your leans"). Scripted agents, no model calls, every new number ASSUMED.

## In one paragraph

**The pass test passes, by a wide margin, and it buys accurate agents at a price.** With `agent_values="v2"` and `bills_hurt=True`, the agents' own values agree with the hedonic model's one-week answer almost exactly: rank correlation 0.99 (v1: 0.43), the agent's best action is the actual best in 97% of decisions (v1: 34%), every action's mean gap is under 0.005. Agreement over longer horizons rose too (13 weeks 0.82, was 0.30; 52 weeks 0.68, was 0.19). But a one-week forecaster pays a monthly bill only in the settlement week, and only when the partner's share tips it. With bills that hurt, the pot drains and bills hurt every month, so households mostly stop forming: 16% of sampled decisions are inside a household, against 61% with the old agents. That changes the world the two reruns measure.

## What changed

Two switches, both fields of `hedonic.FixConfig`, both off by default. Every past run reproduces with them off (`tests/test_agent_values.py`, pinned from commit 36a6460 before any change, and the older pins).

**`bills_hurt`** ([prereg](agent-recalibration-prereg.md), section (c); `WeeklyWorld._settle_hurt`). Before, an unfunded bill was paid from the shared pot at month end and nobody felt it. Now, at settlement, when the month's contributions fell short by `short` of `need`:

| Term | Size | Source |
|---|---|---|
| Late fee | 5% of the shortfall, paid from the pot with the bill | ASSUMED |
| Lost buffer | each member in loses security equal to their share of the draw ÷ 25 (the assets at which the model's security refill is full) | ASSUMED, in the model's own unit |
| Bill stress | friction that week, each member in: 0.30 × short/need × dryness; dryness = 1 − pot/30 (three months of the couple's bill) | ASSUMED; context: 37% of US adults could not cover $400 from cash (Fed SHED 2025), median family holds about five weeks of income in the bank (SCF 2025), docs/notes/economy-calibration.md |
| Arrears and eviction risk | what the pot cannot pay carries into next month (one month); 0.30 friction and the old 0.15 security hit | ASSUMED |

Known answers, as tests: a pair with no money and an empty pot feels 0.60 of friction in the settlement week and the bill carries; a pair with a full pot feels no stress, loses 0.21 security each, and the pot pays a 0.5 late fee; a bill funded by contributions costs nothing.

**`agent_values="v2"`** (`src/mar/agent_values.py`). An action is worth the change it makes to this week's close in the hedonic model's own arithmetic (`week_net`): needs at their levels after the week's drift and after every action already taken this week, on the model's scale (no `_m`, no divisors); aspirations at the model's weights; time together's own pleasure; fix 1 contact amplification, release and missing pain; fix 2 bought pleasure; the strand payoff through this week's bond quality; the bill terms; pleasure and offsettable suffering clipped as the model clips them. Plus a prosocial share of the partner's change for time together and shared bills. A soft rule's sanction is priced at the friction it adds (a warning 0.15 for each week beyond one already running). The H39b planner reads the same values, so a block of making is set against a time cost in the same units. Kept on purpose: one-week horizon, the variety policy (only "adaptive" personas expect satiety), H38's withdrawal, the 0.003 floor, the partner's consent rule, every propose-only score. A test checks that at the week's very last call v2's value of every action equals the change in the agent's own net that week, to the 4-decimal rounding of the hedonic rows.

## The pass test

The value-consistency check rerun as preregistered: H39b's M0 world with both switches on, H38's 120 confirmatory pairings × seeds 0 to 3, six sampled weeks, both partners, the week's last call: 5,760 decisions, 20,351 measured actions (2,158 s on 3 workers). Rows in runs/value-consistency-v2/ (`--v2 --run`, `--v2 --passtest`, `--v2 --analyze`). Soft-rule rows are held to their 13-week actual in every row (Amendment 1).

| ID | Quantity | v1 | v2 + bills | Bar | |
|---|---|---|---|---|---|
| T1 | pooled rank correlation | 0.43 | **0.99** | ≥ 0.70 | holds |
| T2 | within-decision rank correlation | 0.39 | **0.99** | ≥ 0.60 | holds |
| T3 | agent's best = actual best | 34% | **97%** | ≥ 60% | holds |
| T4 | best beats next best | 40% | **91%** | ≥ 60% | holds |
| T5 | slope of actual on perceived | 2.48 | **1.02** | 0.8 to 1.25 | holds |
| T6 | every action's mean gap within its bar | fails 4 of 6 | **all hold** | see below | holds |

**PASS.** No iteration on the mapping was needed.

Per action, own net, perceived against actual (T6 rows; actual with a 95% bootstrap interval over runs):

| Action | n | Perceived | Actual, 1 week | Gap | v1 gap | Actual, 13 weeks | Actual, 52 weeks |
|---|---|---|---|---|---|---|---|
| work | 2,490 | +0.023 | +0.022 [+0.020, +0.024] | +0.000 | −0.092 | +0.033 | +0.108 |
| rest | 5,468 | +0.024 | +0.024 [+0.023, +0.025] | +0.000 | +0.003 | +0.038 | +0.087 |
| see a friend | 5,381 | +0.022 | +0.021 [+0.021, +0.022] | +0.001 | −0.028 | +0.026 | +0.026 |
| time together | 396 | +0.009 | +0.004 [+0.002, +0.006] | +0.005 | −0.014 | −0.015 | −0.38 |
| pay shared bills | 1,042 | +0.009 | +0.005 [−0.003, +0.012] | +0.004 | +0.112 | +0.147 | +1.01 |
| spend on oneself, no rule | 4,303 | −0.039 | −0.039 | 0.000 | +0.069 | | |
| spend on oneself, D1 binds (13 weeks) | 1,271 | −0.617 | −0.632 | +0.015 | +0.620 | | |

The two lines of "One other way to measure it" (prereg): on own + prosocial × partner net, the utility's own definition, T1 to T6 all hold too (0.99, 0.99, 97%, 92%, 1.03). On unclipped pleasure − suffering the test **fails** (T1 0.70 just under its bar; rest, friends and together underpriced by 0.016 to 0.066). That is by design, not a miss: v2 values what the clipped close counts, and the clip eats most of what rest, friends and time together add above the cap. It says the pass depends on the clip being part of the scale.

## Where agreement still fails

**Past one week, bills.** Paying a shared bill is worth +0.005 to the payer this week and +1.01 over 52 weeks: a drained pot means a year of bill stress, lost buffer and arrears. v2 sees the week. This is the horizon gap of limit 13, now concentrated in one action, and it is what changes the world: the households that form drain their pot.

**Time together.** The weakest action at one week (rank correlation 0.54 within the action, sign disagreement 24%), because it uses the partner's units and the partner's later call reacts. Its 52-week value is negative on average (−0.38, wide), mostly through households that later end.

**Idle.** In 11.5% of last calls nothing clears the floor (v1: 17%). There, the best action is worth −0.009 over one week (idle was right) and +0.012 over 13 weeks: small upkeep the one-week view skips.

## The world changes: households form less

| Sampled decisions | v1 | v2 + bills |
|---|---|---|
| inside a household (both in) | 61% | 16% |
| decisions where paying a shared bill was measured | 2,798 | 1,042 |
| spending on oneself while D1 binds | 2,065 | 1,271 |

A free probe of the week-0 formation rule, 12 pairings (Amendment 2): 9 of 12 form with v1, 9 with v1 and bills that hurt, 7 with v2 alone, 0 with v2 and bills that hurt. Each switch alone leaves formation near where it was; together they collapse it. The reruns below, and the descriptive v2-without-bills arms, show how much.

## The reruns

Running at the time of this commit: H39b (13 arms) and the formation check (G arms plus H38's L0, L4, W4 as O arms), both under v2 + bills; then the descriptive v2-without-bills sets. Results follow in this file.
