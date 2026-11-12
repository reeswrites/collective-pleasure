# Bill horizon: design and preregistration

Wording rule: agents feel nothing; "pleasure", "suffering" and "value" are glosses for modeled numbers.

Status: written and committed before any run of the new agents. Nothing here about v2b is a result. Scripted agents, no model calls. Follows [agent-recalibration.md](agent-recalibration.md) ("What is still inconsistent", "Recommendation") and the author's decision ("yes let's try that", logged in experiments/changes.jsonl): (1) a bill horizon, so v2 values a shared-bill payment by the month-end settlement it feeds rather than only this week, preregistered with the value check at its 4-week horizon as the pass test; (2) then the H38 formation check reruns first.

What I knew when writing this, stated plainly: the code for v2b (below) and its known-answer tests were written and run before this commit (unit worlds only; no value-check or experiment run of v2b). The step-2 measurements below are the value check rerun under **v2** (not v2b) with a 4-week horizon added; their numbers set the "before" line and are the target. No v2b number was seen.

**Can be about / cannot be about (required).** This can be about whether scripted v2 agents that also credit a shared-bill payment with its effect on the month's settlement agree with the hedonic model's own 4-week answer in the H39b M0 household, and, through the formation-check rerun, whether H38's and the formation check's findings depend on the one-week view of bills. It cannot be about how people budget or plan, about any carry-over stock other than the month's bill (money, rest, connection, bonds and the pot's long run are measured below, not fixed), or about worlds other than this household. Limits that apply: 1, 2, 9, 12, 13.

## The switch

`FixConfig.agent_values = "v2b"`: v2 exactly, plus the bill horizon on the value of `spend_shared`. `"v1"` stays the default; `"v2"` stays as it is. Pinned before any change (commit d2e5f08): `tests/data/agent_values_v2_fingerprints.json`, v2 with and without bills that hurt (H39b Z, BP, M0; formation G-L0, G-L4; one value-check decision), tested by `tests/test_agent_values.py::test_v2_reproduces_pinned_fingerprints`. The v1 pins (`agent_values_off_fingerprints.json` and the older ones) must still pass.

## The bill-horizon design

A payment of 3 into the month's bills is worth, to the payer:

u(spend_shared) = ΔW_week(payment) + C_own + prosocial × C_partner, times the same ±10% noise,

- **ΔW_week** is v2's term unchanged: the change the payment makes to this week's close (the payer's money and security refill this week; in the settlement week, the bill itself).
- **C**, the settlement credit (`agent_values.settle_credit`), in any week before the settlement week, for a member who is in: the change the payment makes to that member's close **in the settlement week it feeds**, projected now. Both projections are `week_net` with `settle` on: one with the month's funding as it stands (nobody else pays before the settlement), one with this payment added (to the bill while it is unfunded, else to the pot, as the world applies it). The week's levels and counts so far stand in for the settlement week's; money is held (the money cost is in ΔW_week, counted once). In the settlement week C is 0, because the week's own close already holds the bill.
- **The partner's share** is C for the partner before the settlement week, and in the settlement week v2's own partner term (now also when bills do not hurt, so the switch means the same thing in both worlds).

So in a bills-that-hurt world the credit is the model's own settlement arithmetic: the bill stress the payment removes (0.30 × 3/need × dryness), the pot draw and its lost buffer (security) it saves, the late fee, and, for the payment that completes the bill, the eviction friction (0.30) and the 0.15 security hit. A payment into an already funded bill only moves money into the pot, which the settlement does not need; its credit is the pot's tiny share in security.

**Nothing is fitted.** There is no new number. Every term is `week_net`'s, which the recalibration's own known-answer test ties to the model's close. The target is the check's measured 4-week actual. If the pass test fails, the design may be changed only where it disagrees with what the check measures over 4 weeks (each change documented with the check's numbers before and after), never against the formation check's outcome.

**Known answers (tests, run before this commit):**

- K0. Empty pot, nothing funded, a couple's bill of 10: each of the first three payments is credited exactly 0.09 (bill stress at full dryness, 0.30 × 3/10); the fourth, which funds the bill, also lifts the eviction friction and the security hit (> 0.40). In the settlement week the credit is 0.
- K1. A couple with money (12 each) and an empty pot, playing a month: v2b agents fund the bill before the settlement and nothing carries; v2 agents pay one share in the settlement week and the rest carries as arrears.
- K2. The bill already funded, pot at 30: v2b values a further payment at or below the 0.003 floor, within 0.002 of v2.
- K3. Every other action's v2b value equals v2's, exactly.

## Step 2: the carry-over terms, measured (before any change)

The value check rerun under **v2 with bills that hurt**, exactly as the recalibration's pass test, with a 4-week horizon added (`--v2h4 --run`, 5,760 decisions, 20,351 measured actions, 1,453 s on 3 workers; rows in runs/value-consistency-v2-h4/). The 1-, 13- and 52-week numbers reproduce the recalibration's exactly. Per action, the actual effect on the agent's own net is split by the observer groups that carry each stock (`--gaps`, gaps.json). The **gap** of a term at k weeks is its k-week effect minus its 1-week effect: what a one-week valuer cannot see. Rows where a soft rule binds are left out.

| Carry-over term (observer group) | work | rest | see a friend | together | pay shared bills | spend on oneself |
|---|---|---|---|---|---|---|
| **4 weeks** | | | | | | |
| money (money) | −0.007 | +0.006 | +0.000 | −0.001 | +0.003 | +0.004 |
| pot, lost buffer (security) | +0.002 | +0.001 | +0.000 | −0.003 | **+0.030** | −0.000 |
| pot, bill stress (friction) | +0.001 | +0.000 | +0.000 | +0.000 | **+0.010** | +0.000 |
| rest (rest) | −0.011 | +0.004 | −0.001 | −0.001 | +0.000 | −0.006 |
| connection (connection, partner, friends) | −0.004 | +0.011 | +0.000 | −0.008 | +0.001 | −0.004 |
| bonds (levers) | −0.000 | +0.001 | +0.005 | +0.002 | +0.000 | −0.000 |
| clip | +0.016 | −0.013 | −0.001 | +0.007 | −0.015 | +0.001 |
| **net gap, 4 weeks** | −0.004 | +0.010 | +0.003 | −0.003 | **+0.030** | −0.006 |
| **13 weeks**: net gap | +0.011 | +0.014 | +0.005 | −0.019 | **+0.142** | −0.010 |
| of which pot (security + friction) | +0.011 | +0.004 | +0.001 | −0.019 | +0.180 | −0.001 |
| **52 weeks**: net gap | +0.086 | +0.063 | +0.004 | **−0.382** | **+1.001** | −0.019 |
| of which pot (security + friction) | +0.023 | +0.016 | +0.003 | −0.181 | +0.720 | −0.003 |
| of which conditions (trapped, denied) | +0.025 | +0.010 | −0.001 | −0.118 | +0.204 | −0.006 |
| of which connection (all three) | +0.029 | +0.036 | −0.002 | −0.131 | +0.233 | −0.006 |
| of which money | −0.000 | +0.010 | −0.001 | −0.008 | −0.017 | +0.003 |
| of which rest | −0.016 | +0.010 | +0.000 | −0.011 | +0.027 | −0.007 |
| of which bonds | +0.001 | +0.002 | +0.010 | +0.001 | +0.002 | −0.001 |
| n | 2,490 | 5,468 | 5,381 | 396 | 1,042 | 4,303 |

Trust is not a hedonic term: it changes net only through what partners then do, so it shows up inside the other rows. Reading the table:

- **At 4 weeks only the bill clears the T6 bar** (0.015): +0.030, nearly all the pot (lost buffer +0.030, bill stress +0.010, less the clip). Every other action's 4-week gap is within ±0.010.
- **Money, rest and bonds are small stocks at every horizon** (each within ±0.03 for every action at 52 weeks; bonds at most +0.010, from seeing a friend; money at most 0.017).
- **The long-run gaps run through the pot and the household**, not through separate stocks: at 52 weeks the bill's +1.00 is pot +0.72, then the household's knock-ons (conditions +0.20, connection +0.23); time together's −0.38 is the same channels with the other sign (pot −0.18, conditions −0.12, connection −0.13), because sampled together-sessions sit in households that later drain and end.

This decides the scope: a bill-only fix to the month is what the 4-week check can test; the pot's long run is the open question for "Is a general planning horizon needed?" in the results.

## Pass test: the value check at 4 weeks

World and sample exactly as the recalibration's pass test (H39b M0, `bills_hurt`, 120 confirmatory pairings × seeds 0 to 3, six sampled weeks, both partners, the week's last call; 5,760 decisions), now with `agent_values="v2b"` and horizons 1, 4, 13, 52 (`scripts/value_consistency.py --v2b --run`, then `--v2b --passtest`). Main measure: own net. A row is held to its 4-week actual; a row where a soft rule binds to its 13-week actual (as Amendment 1 of the recalibration).

| ID | Quantity | v2 (before) | Bar |
|---|---|---|---|
| U1 | pooled rank correlation, perceived vs actual, 4 weeks | 0.89 | ≥ 0.70 |
| U2 | mean within-decision rank correlation, 4 weeks | 0.86 | ≥ 0.60 |
| U3 | agent's best (or idle) = best by 4-week actual | 75% | ≥ 60% |
| U4 | best beats next best by 4-week actual | 77% | ≥ 60% |
| U5 | slope of actual on perceived, through 0 | 1.03 | in [0.8, 1.25] |
| **U6** | paying a shared bill: \|mean perceived − mean 4-week actual\| | perceived +0.009, actual +0.035, gap 0.026 (fails) | ≤ max(0.015, 0.25 × \|mean actual\|) |
| **U6b** | the same, payments made before the settlement week only | perceived +0.009, actual +0.035, gap 0.026 (fails)B | same bar |
| O1 to O4 | T1 to T4 at 1 week, rows of the five other actions | 0.993, 0.992, 97.7%, 92.0% | each no more than 0.05 (5 points) below v2's |
| O5 | T5 at 1 week, same rows | 1.02 | in [0.8, 1.25] |
| O6 | T6 at 1 week, each of the five other actions | all hold | all hold |

v2 as it is: **FAIL** on U6 and U6b only (`--v2h4 --passtest`, passtest4.json). The O rows leave out the bill's own rows: paying a bill is held to 4 weeks on purpose, and the reach check below showed that an agent valuing bills at exactly their 4-week actual moves the all-rows one-week T3 and T4 to within 0.001 of a 0.05 tolerance. The all-rows one-week numbers are reported, with no bar.

**PASS** iff U1 to U6b and O1 to O6 all hold. Anything else is FAIL, reported clause by clause. U6 and U6b are the clauses the bill horizon is for; the U and O rows guard against breaking what v2 got right. The one-week T6 for paying a bill is reported, not barred: v2b values it past the week on purpose. The other five actions' 4-week gaps are reported with no bar (they are the general-horizon question, step 2).

**Iteration rule.** If the test fails, at most three iterations, each a change to the design above where it disagrees with the check's 4-week actual (read from the check's rows, per term and per week of the month), each preregistered here as a dated amendment with the check's numbers before and after, then the check rerun in full. The formation check runs on the last version whatever its verdict, labelled with it.

## Can every verdict happen? (required)

Checked free on the v2 4-week rows (`--v2h4 --reach`, runs/value-consistency-v2-h4/reach4.json):

| Case (perceived replaced by) | Verdict | Clauses that fail |
|---|---|---|
| v2 as it is | FAIL | U6, U6b |
| v2, bills at their 4-week actual (a perfect bill horizon) | **PASS** | none |
| v2, bills at twice their 4-week actual | FAIL | U6, U6b |
| oracle at 1 week for every action | FAIL | U6, U6b |
| oracle at 4 weeks for every action | FAIL | O1 to O4 (one-week line falls: T1 0.92, T3 78%) |
| v2 halved | FAIL | U5, O5 (slope 2.06), U6, U6b, O6 |
| v2 with ±0.03 alternating noise | FAIL | U1, U3, U6, U6b, O1 to O4 |

Every clause fails in at least one case except U2 and U4 alone (U2 reaches 0.63 against 0.60 under noise); PASS is reachable. The metric sees the mechanism: every term of the credit is a term of `week_net`, and the 4-week actual holds the settlement week.

## Are we measuring what we say? (required)

- **Construct card.** "Perceived" = v2b's number at that call, noise off, minus its sanction price. "Actual (4 weeks)" = the change in the agent's own modeled net summed over the decision week and the next three, against doing nothing at that call, the world playing on. A decision week always reaches its month's settlement within those four weeks (settlement is every fourth week), so the 4-week actual of a payment holds the settlement it feeds. v2b encodes "the agent forecasts this week, plus what this payment does to this month's settlement if nobody else pays first". It does not encode the pot's long run (a drained pot hurting next month and after), money held over the month, or any other stock.
- **Where it can mislead.** The 4-week actual is measured in a world of v2b agents. If they pay early, not paying now is often made up later in the month, so the actual of paying now can be small while the perceived credit (which assumes nobody else pays) is large. U6b catches that. It is a real disagreement, not noise: it would mean the credit is right about the settlement and wrong about the counterfactual.
- **Known-answer cases.** K0 to K3 above, as tests.
- **One other way to measure it.** U1 to U6b also reported (no bar) on own + prosocial × partner net and on unclipped pleasure − suffering.
- **What the formation rerun measures.** The same as before (Amendment 1 of the formation check): mean weekly clipped pleasure of both members over 156 weeks, paired by pairing.

## The formation-check rerun (Amendment 2 of [h38-formation-check-prereg.md](h38-formation-check-prereg.md))

Runs after the pass test. Same design as Amendment 1 (G-L0, G-L4, G-W4, G-L1, O-L0, O-L4, O-W4; 120 pairings × seeds 0 to 3; C1 to C3, margin 0.007, Holm), with `FixConfig(agent_values="v2b", bills_hurt=True)`; rows in runs/h38-formation-v2b/. Plus a descriptive arm set, no verdicts: v2b with bills off, G-L0, G-L4, O-L0, O-L4 (runs/h38-formation-v2b-nobills/), so that v2b + bills, v2b alone and v2 alone (from the recalibration) can be set side by side.

**Survival rules, fixed now.** Each finding is compared across v1 (the formation check as first run, with H38's own rows), v2 (Amendment 1) and v2b:

- C1, C2, C3 get their verdicts by their own rules. A verdict "survives under v2b" if v2b gives the same verdict as the version compared.
- A signed finding (H38's gain old L4 − L0; withdrawal old W4 − L0; C1 without the direct terms; C1 weeks together; C3's formation share; G-L1 − G-L0) "survives" by the H39b rule: same sign and the 95% interval excludes 0.
- Each finding is then labelled: **v1 restored** (v2b agrees with v1 where v2 did not), **v2 confirmed** (v2b agrees with v2 where v1 did not), **stable** (all three agree), **neither** (v2b agrees with neither).
- **Households form and persist at plausible rates**, descriptive, fixed now so it cannot drift: under v2b + bills, G-L0's week-0 formation share is at least 0.50 and the share of formed households that end is at most 0.67 (the top of v1's range across the arms, 0.20 to 0.67). Both thresholds are reference points, not hypotheses; 0.50 is about the old rule's own week-0 share under v1 (0.51).

What I expect, no verdict weight: v2b funds bills, so the pot drains less and formation rises from v2's levels; I do not know by how much. If it rises near v1's, the v2 reversals that came from the bills (formation, C3) may undo, while the reversals the recalibration itself produced (H38's gain, from accurate agents leaving) should stay, since the v2-without-bills arms showed them there.

## Not testable by design

The pins. The known-answer tests. Every number in the step-2 table (measurements).

## Limits stated now

One world for the pass test. One bill horizon: to the month's settlement, not the pot's long run. The settlement projection assumes nobody else pays first and uses this week's levels as the settlement week's. Bill numbers ASSUMED, one point each. The 4-week target is measured in v2b's own world, so it moves with the agents.

## Amendments

**Amendment 1 (2026-11-12, after the pass test, before the formation rerun): the pass test fails; no iteration.** The pass test ran as written (runs/value-consistency-v2b/, 5,760 decisions, 1,844 s). **FAIL on U6 and U6b only**: paying a shared bill is perceived at −0.022 and is worth −0.051 over 4 weeks (gap 0.029, bar 0.015); before the settlement week −0.017 against −0.054 (gap 0.037). U1 to U5 and O1 to O6 hold. The rows say why, by week of the month (unfunded bill, payments before the settlement week):

| | v2 world: perceived | v2 world: 1 week | v2 world: 4 weeks | v2b world: perceived | v2b world: 1 week | v2b world: 4 weeks |
|---|---|---|---|---|---|---|
| week 0 of the month | −0.015 | −0.015 | +0.011 | +0.014 | −0.047 | −0.049 |
| week 1 | −0.014 | −0.014 | +0.024 | −0.024 | −0.053 | −0.058 |
| week 2 | −0.014 | −0.014 | +0.030 | −0.040 | −0.059 | −0.057 |

In v2's world nobody pays early, so a payment made now is a payment the settlement would otherwise miss: the 4-week actual is above the 1-week one by +0.03, the credit v2b adds. In v2b's world the agents pay early, so a payment not made at this call is made at a later call before the settlement, and the 4-week actual of paying now is its 1-week cost (money, and the denial condition for poorer agents), nothing more. The credit is right about the settlement and wrong about the counterfactual, the case "Where it can mislead" named. In the settlement week the credit is 0 and the agents agree with the check (perceived −0.037, 4 weeks −0.045).

Why no iteration: the iteration rule allows a change only where the design disagrees with the check's 4-week actual. Here the actual depends on what the same agents do at their later calls. A credit that assumes nobody pays later (v2b) over-values by 0.037; a credit of 0 before the settlement (v2) under-values by 0.036 in the world it makes. Any rule in between is a number chosen so the world it makes lands on the bar, which is fitting a parameter to the check's outcome through the agents' own behaviour. The rule this design does not have, and would need, is a plan: the household deciding the month's payments once, so "not paying now" has a defined later. That is a new design, not an iteration. The formation rerun runs on v2b as tested, labelled with this FAIL. No formation number had been seen when this was written.
