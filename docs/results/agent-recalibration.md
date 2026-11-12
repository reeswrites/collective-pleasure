# Agent recalibration and bills that hurt: results

Wording rule: agents feel nothing; "pleasure", "suffering" and "value" are glosses for modeled numbers.

Status: run on 2026-11-11 after the preregistration ([agent-recalibration-prereg.md](agent-recalibration-prereg.md), commit 84fa28f; code 4764e88; Amendments 1 and 2 committed before the runs they touch). Follows [value-consistency.md](value-consistency.md) and the author's decision (experiments/changes.jsonl, 2026-11-11T21:53:50Z, "Yes, your leans"). Scripted agents, no model calls, every new number ASSUMED.

> **Note, 2026-11-12: the bill horizon** ([agent-bill-horizon.md](agent-bill-horizon.md)). The recommendation below was tried. `agent_values="v2b"` credits a bill payment with the settlement it feeds; it **fails** its 4-week pass test on the bill clauses (over-values a payment by 0.029; v2 under-valued it by 0.026), because the credit assumes nobody pays later and these agents do. It still brings households back about halfway (49% of check decisions inside one; here 16%), and under it the formation check's pressure harm (−0.038, −0.046) shrinks to about nothing (−0.004, −0.003). The carry-over terms were measured at 1, 4, 13 and 52 weeks: only the bill clears the bar at 4 weeks; the long run is the shared pot.

## In one paragraph

**The pass test passes, by a wide margin, and it buys accurate agents at a price.** With `agent_values="v2"` and `bills_hurt=True`, the agents' own values agree with the hedonic model's one-week answer almost exactly: rank correlation 0.99 (v1: 0.43), the agent's best action is the actual best in 97% of decisions (v1: 34%), every action's mean gap is under 0.005. Agreement over longer horizons rose too (13 weeks 0.82, was 0.30; 52 weeks 0.68, was 0.19). But a one-week forecaster pays a monthly bill only in the settlement week, and only when the partner's share tips it. With bills that hurt, the pot drains and bills hurt every month, so households mostly stop forming: 16% of sampled decisions are inside a household, against 61% with the old agents. That changes the world the two reruns measure.

**The reruns.** H39b: households almost never form; the crediting nulls survive, the tally still raises making, and "makers lower pleasure" reverses (+0.003). Formation check: C1 is within the margin but as clear harm (−0.038), C2 and C3 fail, and H38's own gain under the old rule reverses (+0.021 → −0.046). The descriptive v2-without-bills runs show the reversals come from the recalibration (accurate agents leave households that pressure holds them in), while the bills decide whether households form at all.

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

## Rerun 1: H39b under the new agents

As preregistered ([H39b Amendment 2](h39b-makers-rerun-prereg.md)): 13 arms × 120 pairings × seeds 0 to 3, 6,240 runs, both switches on. Rows in runs/h39b-makers-v2/; the comparison in runs/agent-recalibration/compare.json (`scripts/agent_recalibration_compare.py`).

**Households almost never form, so H39b's question is barely asked.** Week-0 formation is 0 in every makers arm and 0.002 in M0 (H39b: 0.29 to 0.52). Pairs come together later through the 13-week retries in 7% of weeks (makers on) to 13% (makers off), against 29% to 55%. Making happens only inside a household, so every crediting comparison is between nearly identical lives.

| | M0 | Z | BP | H | P | G | A |
|---|---|---|---|---|---|---|---|
| pleasure, v2 + bills | 0.973 | 0.976 | 0.976 | 0.976 | 0.976 | 0.976 | 0.976 |
| pleasure, H39b | 0.933 | 0.911 | 0.908 | 0.908 | 0.910 | 0.911 | 0.908 |
| weeks together, v2 + bills | 0.13 | 0.08 | 0.07 | 0.07 | 0.07 | 0.08 | 0.07 |
| weeks together, H39b | 0.55 | 0.32 | 0.29 | 0.29 | 0.31 | 0.31 | 0.29 |
| blocks per partner-week together | – | 2.03 | 2.23 | 2.30 | 2.16 | 2.03 | 2.25 |
| person-weeks in a full wanting trap | – | 0.025 | 0.026 | 0.025 | 0.025 | 0.026 | 0.024 |

Pleasure is higher everywhere (0.97 against 0.91 to 0.93): agents that value their own week accurately, living apart, do better on their own clipped pleasure than the v1 agents did together. Nothing here says living apart is better for people; it says these agents, with these bills, run a better week alone.

The planner's time cost did move as item 5 intended: 0.0048 a block in Z (H39b 0.0019), and the share of blocks made in units the plan would have left idle fell from 78% to 40%. Blocks per partner-week together did not fall (2.03 against 1.87): the households that do form are the ones where making pays.

**Which H39b findings survive** (rule fixed in Amendment 2):

| H39b finding | H39b | v2 + bills | Verdict |
|---|---|---|---|
| BP − Z, pleasure (null) | −0.0027 [−0.0055, +0.0002] | +0.0001 [−0.0006, +0.0008] | survives (null) |
| H, P, G, A − Z, pleasure (nulls) | −0.0025 to −0.0003 | −0.0002 to +0.0002, all include 0 | survive (null) |
| BP − Z, unclipped | −0.0070 [−0.0119, −0.0022] | −0.0020 [−0.0038, −0.0004] | **survives**, smaller |
| The tally's pull, BP − G, unclipped | −0.0061 [−0.0107, −0.0015] | −0.0023 [−0.0040, −0.0008] | **survives**, smaller |
| Makers lower pleasure, Z − M0 | −0.022 [−0.028, −0.017] | **+0.003 [+0.001, +0.005]** | **reverses** |
| Z − M0, net | −0.041 | +0.020 [+0.011, +0.030] | reverses |
| Z − M0, no extractive maker | −0.013 [−0.020, −0.007] | +0.003 [−0.000, +0.006] | does not survive |
| Z − M0, formation at week 0 | −0.19 | −0.002 | does not survive (nobody forms) |
| Z − M0, weeks together | −0.23 | −0.049 [−0.066, −0.033] | survives, much smaller |
| Tally raises making (P2: H, P, BP − Z) | +0.13, +0.07, +0.12 | +0.27, +0.15, +0.21 | survives, larger; P2 now holds for P too |
| BP − Z, weeks together | −0.032 | −0.010 [−0.019, −0.001] | survives, smaller |
| P3: hours draw in partners who dislike making | +0.012 [+0.002, +0.022] | −0.011 [−0.027, +0.005] | does not survive |
| Protection starts more projects (BP-PN − BP) | +0.155 [+0.056, +0.25] | +0.091 [+0.048, +0.143] | survives, smaller (below the +0.20 bar) |
| P7: the suffering-weight rule forms fewer households | −0.44 | −0.008 | does not survive (nobody forms under either rule) |
| Tally lowers the trap share (BP − Z) | −0.008 [−0.016, −0.001] | +0.001 [−0.003, +0.004] | does not survive |
| P4: imbalances even out more under a tally | +0.097 | no long-together pair-seeds | cannot be computed |

Verdicts: H39 **not supported** (as before); H20a **not supported** (as before; P6c now holds, P6a and P6b miss); extractive question **weak** (as before).

**What survives is what does not need households.** The crediting nulls survive because nothing moves. The tally still raises making and still lowers unclipped pleasure a little, inside the few households there are. H39b's headline, "makers lower pleasure", reverses: with almost nobody living together, makers on and off differ by a small amount, and now the other way. None of this says making helps; it says the H39b result needs agents that form households, and these do not.

## Rerun 2: the H38 formation check under the new agents

As preregistered ([formation check Amendment 1](h38-formation-check-prereg.md)): G-L0, G-L1, G-L4, G-W4 under the corrected rule, and H38's own L0, L4, W4 under the old rule, all with both switches on; 120 pairings × seeds 0 to 3, 3,360 runs. Rows in runs/h38-formation-v2/.

**Households form less and end almost always; pressure now pushes people into households that hurt.**

| | old L0 | old L4 | old W4 | G-L0 | G-L1 | G-L4 | G-W4 |
|---|---|---|---|---|---|---|---|
| pleasure, v2 + bills | 0.974 | 0.928 | 0.973 | 0.978 | 0.969 | 0.941 | 0.977 |
| pleasure, before | 0.928 | 0.949 | 0.917 | 0.956 | 0.957 | 0.959 | 0.940 |
| formed at week 0, v2 + bills | 0.16 | 0.49 | 0.15 | 0.06 | 0.08 | 0.53 | 0.12 |
| formed at week 0, before | 0.51 | 0.88 | 0.49 | 0.84 | 0.89 | 0.98 | 0.71 |
| weeks together, v2 + bills | 0.16 | 0.31 | 0.13 | 0.19 | 0.22 | 0.43 | 0.18 |
| households that end (of formed), v2 + bills | 0.96 | 0.88 | 0.98 | 0.81 | 0.85 | 0.84 | 0.80 |
| stay readings held by pressure, v2 + bills | 0 | 0.49 | 0.05 | 0 | 0.27 | 0.46 | 0.09 |

Differences, paired by pairing, 95% bootstrap:

| Comparison | Before | v2 + bills | Verdict (rule fixed in Amendment 1) |
|---|---|---|---|
| **C1** G-L4 − G-L0, pleasure | +0.003 [−0.004, +0.009], within margin | **−0.038 [−0.043, −0.033]**, within margin (Holm p 1.0) | C1 "within margin" **survives**, but now as clear harm |
| C1 without the direct terms | −0.010 [−0.015, −0.005] | −0.009 [−0.012, −0.005] | survives |
| C1 weeks together | +0.10 | +0.24 [+0.20, +0.27] | survives, larger |
| C1 net | −0.002 [−0.020, +0.014] | −0.103 [−0.121, −0.086] | now an effect (harm) |
| **C2** G-W4 − G-L0, pleasure | −0.017 [−0.022, −0.011], holds | −0.001 [−0.003, +0.001], **fails** | does not survive |
| **C3** G-L0 − old L0, pleasure | +0.028 [+0.023, +0.033] | +0.005 [+0.002, +0.008] | survives, much smaller |
| C3 formation at week 0 | +0.33 | **−0.10 [−0.16, −0.04]** | reverses, so **C3 fails** |
| H38's gain, old L4 − old L0 | +0.021 [+0.013, +0.028] | **−0.046 [−0.053, −0.040]** | **reverses** |
| H38's withdrawal, old W4 − old L0 | −0.011 [−0.016, −0.007] | −0.001 [−0.003, +0.002] | does not survive |
| G-L1 − G-L0 | +0.001 (null) | −0.009 [−0.011, −0.007] | now an effect (harm) |

Verdicts: C1 within margin (as before), C2 fails (was holds), C3 fails (was holds).

What this says, plainly:

- **H38's headline reverses.** With agents that value their weeks accurately and bills that hurt, pairing pressure lowers pleasure under either formation rule (−0.046 under the old rule, −0.038 under the corrected one). It still adds weeks together, and about half the stay readings under pressure are held by it. Taking away the direct terms leaves −0.009, about what the formation check already found; the rest is stigma paid by the many who stay apart.
- **Withdrawal stops mattering**, because few people live together long enough for it to bite.
- **The corrected rule no longer forms more households.** Under v2 agents both rules see household weeks that cost bills and stress, and the pleasure rule is the more cautious one here (0.06 against 0.16 at week 0). It still yields slightly more pleasure.
- **Households that form mostly end** (80% to 98%), against 20% to 67% before.

## Descriptive: what the recalibration does without the bills

Amendment 2's arm sets, `agent_values="v2"` with `bills_hurt=False`. No verdicts.

**The check.** Every third pairing, seeds 0 and 1, 960 decisions: the pass test's bars all hold here too (T1 0.99, T2 0.98, T3 95%, T4 87%, T5 1.02, every gap under 0.005), and 36% of decisions are inside a household (v1 61%, v2 with bills 16%). Paying a shared bill is now a pure loss to the payer (−0.029 over one week), as gap 5 of the check said it would be.

**Formation without bills.** Households form at week 0 as often as before (0.77 to 0.95) and then end almost always (96% to 99% of formed households). Pressure harms just as much: G-L4 − G-L0 −0.042 [−0.047, −0.036], old L4 − L0 −0.047 [−0.053, −0.041], without the direct terms −0.010 under both. The corrected rule still beats the old one (+0.022 [+0.017, +0.028]).

**H39b without bills** (M0, Z, BP): week-0 formation 0.74 (M0), 0.41 (Z), 0.35 (BP); weeks together 0.20, 0.13, 0.11. Makers on is above makers off (Z − M0 +0.005 [+0.001, +0.010]) and the tally is now above nothing credited (BP − Z +0.003 [+0.002, +0.006]); the tally still adds blocks (+0.22).

So the two switches do different things. **The recalibration alone reverses H38** (pressure harms) and **H39b's "makers lower pleasure"**: v2 agents, who value their own weeks accurately, leave households they would have stayed in, and pressure that holds them there costs pleasure. **The bills decide whether households form at all**: with them, a one-week forecaster lets the pot drain and few pairs move in.

## Story spot-check

The prereg asked for three runs; two were read week by week (single replays, 13-week blocks), plus the first one again under v1 and under v2 without bills:

- **H39b BP, p-anchor with p-bargainer, seed 0, v2 + bills.** Never forms. Each partner settles into the same week, every week: work, rest, a friend; pleasure 0.97 and 1.00, suffering 0.11 to 0.13, for three years. With v2 and no bills, the same. With v1, they live together for 39 weeks and pay the bills, then A leaves. The measure's story (accurate agents doing well apart) is what happens.
- **Formation G-L4, p-anchor with p-host, seed 0, v2 + bills.** Pushed in at week 0. Lots of time together, pleasure at the cap; they pay about a third of the bills, the pot drains, suffering rises from 0.08 to 0.16 over a year; A's stay readings say "held" from week 13 and "leave" from week 52; A leaves at week 65 with nothing. After the split pleasure falls to 0.8 to 0.95 and suffering rises (stigma, bills alone). That is the C1 harm, seen in one life.

They look like what the measure claims: households that underpay their bills and come apart. The match is close because the measure and the story are the same mechanism, not two independent checks.

## What is still inconsistent

- **The horizon.** v2 sees one week. Paying a shared bill is worth +0.005 over one week and +1.01 over 52. Formation and stay decisions already use 52-week rollouts, but the weeks inside those rollouts are played by one-week agents, so the rollouts forecast households that underpay. This is limit 13's open half, and it now decides the household results.
- **Time together** at one week (rank correlation 0.54 within the action): it uses the partner's units and the partner reacts.
- **The partner's consent to time together** still uses the v1 threshold (`together_utility` ≥ 0.02), in v1 units.
- **Unclipped pleasure.** v2 values only what the clipped close counts; at the cap, rest, friends and time together look worthless to it for the week.
- **The bill numbers** are ASSUMED, one point each.

## Recommendation

Do not cite any v2 result that runs through forming or keeping a household until the horizon is decided. The smallest next step is a bill horizon: let v2 value a shared-bill payment by the settlement it feeds (the month's close, not the week's), a known answer the check can test at its 4-week horizon, preregistered the same way. Then rerun the formation check first (it is the cheaper of the two and the one whose verdicts moved most). Option (b2), a persona's own discounting, comes after: a chosen bias is a finding; the one-week horizon is an accident of the recalibration's scope.

## Can be about / cannot be about

This can be about whether scripted persona agents that value their actions by the hedonic model's one-week answer agree with it (they do), and what H39b and the H38 formation check show under such agents in this household, with and without bills that hurt.

It cannot be about how people forecast, pay bills or decide to live together; about any horizon past one week for the agents' own choices; or about the bill numbers, which are ASSUMED.

## Reproduction

`uv run python scripts/value_consistency.py --v2 --run`, `--v2 --passtest`, `--v2 --analyze`, `--reach`, `--v2nobills --run`; `uv run python scripts/h39b_makers_rerun.py --v2 --run` and `--analyze` (and `--v2nobills`); `uv run python scripts/h38_formation_check.py --v2 --run` and `--analyze` (and `--v2nobills`); `uv run python scripts/agent_recalibration_compare.py`. Tests: `uv run pytest tests/test_agent_values.py -m ""`. Rows in runs/ (not committed). Wall time on 3 workers: check 36 minutes, H39b about 4 hours, formation check about 80 minutes.
