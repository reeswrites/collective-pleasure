# H38 formation check: preregistration

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Status: written and committed before the confirmatory run. The diagnosis below was run first and is stated here so the reader knows what I knew. Scripted persona agents. No model calls.

This is a small follow-up to H38 ([prereg](h38-pairing-norms-prereg.md), [results](h38-pairing-norms.md)). The author said "Yes, check first", before H39.

## Why

H38 found that pairing pressure raised pleasure at every dial level (L4 +0.021 [+0.013, +0.028]). It was predicted to lower it. The H38 write-up gave a reading it did not test: agents decide to form by comparing 26 weeks of net wellbeing, together against apart, and that rule may under-form on pleasure. Pressure then pushes pairs over the line, and they do better.

If that is right, H38 tested a cautious formation rule, not pairing norms.

## Diagnosis (exploratory, done before this prereg)

**What the decisions use.** Every decision in the H38 household is a rollout comparison:

- **Forming at week 0** (`negotiation.BaselineLived.__init__`): each member's value of living together (`baseline_value`, a 26-week rollout) against their outside option (`outside_value`: the better of 26 weeks alone or 26 weeks with the friend). The pair forms only if neither member's outside option is higher. Unanimity, each member on their own score.
- **Retries every 13 weeks while apart** (`retry`): the same comparison, with a 26-week forward rollout of the household as it would be.
- **Staying** (`reading`, then `bar_reading`): a 26-week forward rollout against the outside option. A member whose outside option wins by more than 0.02 in two readings in a row may leave.
- **The score** (`negotiation.wellbeing`): the mean over the rollout of pleasure minus offsettable suffering minus non-offsettable suffering. That is net wellbeing, not pleasure.

There is no discounting and no risk term: each rollout is a plain mean. The verdict scores clipped pleasure, both members, over 156 weeks.

**Week-0 formation share under each rule** (all 120 H38 pairings × 4 seeds, L0, `scripts/h38_formation_check.py --diagnose`):

| Rule | Forms at week 0 |
|---|---|
| old: net wellbeing, 26 weeks | 0.51 |
| net wellbeing, 52 weeks | 0.58 |
| own pleasure, 26 weeks | 0.80 |
| own pleasure, 52 weeks (the corrected rule) | 0.84 |

So the yardstick does most of the work. The window adds a little.

**Why net under-forms on pleasure.** The members who block formation under the old rule (294 member-readings) expect a little *more* pleasure together than apart (0.957 vs 0.947 over 26 weeks), but much more suffering together (0.169 vs 0.113). Net wellbeing says no; pleasure says yes. The other members expect both more pleasure and less suffering together.

**Is the old rule wrong on its own terms?** No. Among the 236 pair-seeds that decline at L0, forcing them to form at week 0 (old rule otherwise, `F-L0`) changes their 156-week outcomes like this:

- pleasure: +0.014 on average; 62% of pair-seeds better off; in only 34% are both members better off;
- net wellbeing: −0.008 on average.

So the old rule is a reasonable chooser on net wellbeing. It is a cautious chooser on pleasure, the verdict's yardstick. H38 judged a net-wellbeing chooser on pleasure.

**The corrected rule is not a perfect chooser either.** On the declined pair-seeds, it would form 69% of them, but both members end up better on pleasure in only 34%. Its 52-week rollout over-predicts the together life for some. It matches the verdict's yardstick; it does not see the future.

## The flag

`FixConfig.decide_on` ("net", the default, or "pleasure") and `FixConfig.decide_weeks` (0, the default, meaning the old 26-week windows; or a number of weeks). Under `decide_on="pleasure", decide_weeks=52`:

- `negotiation.wellbeing` scores each member's own mean clipped pleasure (the verdict's measure, from that member's point of view; unanimity is kept);
- the formation, retry, reading and outside-option rollouts are 52 weeks long, and so are the stay lens's rollouts and the spread of the exit-stigma anticipation.

Leaving on distress is not a yardstick decision and is unchanged. With the defaults, every earlier run is bit-identical (test: `tests/test_formation_check.py::test_flag_off_reproduces_h38_rows_exactly`, four H38 confirmatory rows copied before the flag existed).

## Design

- World, pairings, seeds: as H38. `negotiation.BaselineLived(decline=True)` on the baseline rule set, `retest.FIXES_ON`, `retest.LEVERS`, exit fallback F4 with `strip_split`, items in cell V2, 156 weeks. The 120 H38 pairings (15 hand plus `retest.sample(105, seed=38)`), seeds 0 to 3. Unit of resampling: the pairing, seeds averaged first.
- New arms, all under the corrected rule: **G-L0**, **G-L4** (the full dial at L4), **G-W4** (withdrawal alone at L4). Descriptive: **G-L1**.
- Old arms are reused from H38's rows (runs/h38-pairing/rows.jsonl): L0, L1, L4, W4. The flag-off reproduction test shows they are what the code now produces.
- Run: `uv run python scripts/h38_formation_check.py --run` (3 workers), then `--analyze`.

## Predictions

Primary measure: H38's, mean weekly clipped pleasure, both members, all 156 weeks. Differences paired by pairing; 95% percentile bootstrap by pairing; one-sided paired sign-flip p; Holm across C1 to C3.

**The margin.** 0.007, a third of H38's L4 gain. Chosen before the run.

| ID | Quantity | Outcomes |
|---|---|---|
| C1 (the key test) | G-L4 − G-L0 | **survives**: estimate ≥ 0.007, interval above 0, Holm p < 0.05. **Within margin**: estimate < 0.007 (this includes a negative estimate). **Weak**: estimate ≥ 0.007 but the interval crosses 0 or Holm p ≥ 0.05 |
| C2 (withdrawal alone) | G-W4 − G-L0 | **holds**: below 0, interval below 0, Holm p < 0.05 |
| C3 (how much the old rule under-forms) | G-L0 − L0, pleasure; and week-0 formation share | **holds**: pleasure above 0 robustly AND formation share higher, interval above 0 |

What I expect:

- **C1: within margin.** At G-L0 the pairs already form at about the rate pressure pushed them to in H38 (0.84 at week 0, against 0.88 at old L4). What is left for pressure is mostly the reward paid directly to people living together (R4 alone gave +0.020 in H38, about half of it direct). I expect the estimate between 0 and +0.010, most likely under 0.007. I am not confident: the reward term alone could keep it above the margin.
- **C2: holds.** Withdrawal cuts friend contact whatever the formation rule.
- **C3: holds.** The formation clause is close to certain from the diagnosis (0.84 vs 0.51). The pleasure clause can fail: forced formation raised pleasure by +0.014 on average, but the corrected rule over-forms for some pairs.

Shown beside the primary, no verdict weight: net wellbeing, share of weeks together, households that end, pleasure without the direct terms, unclipped pleasure, pairs pushed in by L4 under the corrected rule, G-L1, and G-L4's gain minus old L4's gain, paired.

## What each outcome means

- **C1 within margin:** H38 is effectively untested against agents who choose well on pleasure. Its headline (+0.021) is mostly pressure correcting a cautious formation rule.
- **C1 survives:** pressure helps in this model even with agents who choose on pleasure. The reason is then not under-forming, and the next suspect is the direct reward term.
- **C1 weak:** neither; report the estimate and the interval.

## Can every verdict happen?

`uv run python scripts/h38_formation_check.py --reach` runs the same analysis on H38's own rows relabelled as G arms (no new runs):

| Case | C1 | C2 | C3 |
|---|---|---|---|
| G = old L0, L4, W4 | survives (+0.021) | holds | fails (G-L0 = L0) |
| G-L4 = old L0.5 | within margin (+0.004) | holds | fails |
| G-L4 = old W4 | within margin (−0.011) | holds | fails |
| synthetic: G-L4 = L0 + 0.008 ± 0.08 by pairing | weak (+0.008, interval crosses 0) | holds | fails |
| G-W4 = old R4, G-L0 = old W4 | survives | fails | fails |
| G-L0 = old L1 | survives | holds | holds |

Every outcome of C1, C2 and C3 is reachable through the analysis code. In the model itself: the diagnosis shows forced formation lowers pleasure for 38% of declined pair-seeds, so C3's pleasure clause can fail; H38's own W1 crossed zero, so C2 can fail.

## Can be about / cannot be about

**Can be about:** whether H38's pleasure gain from pairing pressure survives when the scripted agents decide to form and stay on the verdict's yardstick, in the same household world (baseline rules, may decline, fixes and levers on, F4, items V2), at one rule point (own pleasure, 52 weeks).

**Cannot be about:**

- people, or real romantic norms (limits 1 and 10);
- "good choosers" in general: the corrected rule matches the verdict's yardstick but still forecasts with a 52-week rollout, and the diagnosis shows it over-forms for some pairs;
- a joint rule (deciding on the pair's total): each member still decides on their own pleasure, and either can block;
- whether pleasure or net wellbeing is the right yardstick for agents. That is the author's call (the verdict judges on pleasure); this check only lines the two up;
- a number as such (limit 5): 52 weeks and the 0.007 margin are chosen, not derived.

## Limits

One alternative rule point. Leaving on distress still ignores the yardstick. The pleasure cap binds on most person-weeks, and the corrected rule decides on clipped pleasure, so it too is blind above the cap. Labor and care are not tracked.

## Amendments

### Amendment 1 (2026-11-11): rerun under the recalibrated agents and bills that hurt

Committed before the run. Follows [agent-recalibration-prereg.md](agent-recalibration-prereg.md) and the author's decision (experiments/changes.jsonl, 2026-11-11T21:53:50Z): rerun the formation check before citing it again.

**What changes.** Every world, rollouts included, runs with `FixConfig(agent_values="v2", bills_hurt=True)`. The old-rule arms can no longer be reused from H38's rows (they were played by the old agents), so H38's L0, L4 and W4 rerun under the new agents too, as arms O-L0, O-L4, O-W4 (`--v2 --run`; rows in runs/h38-formation-v2/). G-L1 reruns as before; the old L1 does not (it only feeds a descriptive row). **Nothing else changes**: pairings, seeds 0 to 3, world, the corrected rule, C1 to C3, the margin 0.007, the tests and Holm.

**Which findings survive** (fixed now): C1 "within margin" survives if the rerun's C1 estimate is again below 0.007; C2 and C3 "hold" survive if they hold again by their own rules. H38's own gain under the old rule (old L4 − L0, +0.021 [+0.013, +0.028]) and withdrawal under the old rule (old W4 − L0, −0.011) survive by the H39b rule (same sign, interval excluding 0). The pleasure-without-the-direct-terms line for G-L4 − G-L0 (−0.010 [−0.015, −0.005]) is compared the same way, descriptive.

**What I expect, no verdict weight.** None strongly. Bills that hurt make living together cost more when the pot runs dry, and agents that value rest and friends at full levels may spend weeks differently in the rollouts, so formation shares under both rules may move.

**Can every verdict happen?** Unchanged: the same analysis code, and `--reach` above.

### Amendment 2 (2026-11-12): rerun under the bill horizon

Committed before the run. Follows [agent-bill-horizon-prereg.md](agent-bill-horizon-prereg.md) and the author's decision ("yes let's try that"): the bill horizon, then this check first.

**What changes.** Every world, rollouts included, runs with `FixConfig(agent_values="v2b", bills_hurt=True)`: v2 plus a shared-bill payment credited by the settlement it feeds. Arms as Amendment 1 (G-L0, G-L4, G-W4, G-L1, O-L0, O-L4, O-W4; `--v2b --run`; rows in runs/h38-formation-v2b/). Descriptive, no verdicts: v2b with bills off, G-L0, G-L4, O-L0, O-L4 (`--v2bnobills --run`). **Nothing else changes**: pairings, seeds 0 to 3, world, the corrected rule, C1 to C3, the margin 0.007, the tests and Holm. It runs after the bill horizon's pass test, whatever its verdict, on the last version the pass test checked.

**Which findings survive** (fixed now; the full rule is in the bill-horizon prereg, "Survival rules"): C1 to C3 by their own rules; signed findings (H38's old-rule gain, old-rule withdrawal, C1 without the direct terms, C1 weeks together, C1 net, C2, C3 pleasure and formation share, G-L1 − G-L0) by the H39b rule (same sign, interval excluding 0); each labelled v1 restored, v2 confirmed, stable or neither across v1, v2 and v2b (`scripts/bill_horizon_compare.py`). Households "form and persist at plausible rates" (descriptive) if G-L0 forms at week 0 in at least 50% of pair-seeds and at most 67% of formed households end.
