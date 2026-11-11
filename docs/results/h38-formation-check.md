# H38 formation check: results

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Status: run once on 2026-11-11, after the preregistration ([h38-formation-check-prereg.md](h38-formation-check-prereg.md), commit 2c5259f; code 3c8a578). Follows [H38](h38-pairing-norms.md).

Setup: the H38 world, pairings and seeds (120 pairings × 4 seeds, F4, items in cell V2). Four new arms under the corrected rule, 1,920 runs (2,376 s on 3 workers). Old arms reused from H38's rows; a test shows the code reproduces them exactly with the flag off. Scripted agents, no model calls, every number ASSUMED. Run with `uv run python scripts/h38_formation_check.py --diagnose`, `--run`, `--analyze`, `--reach`.

## Verdict

**H38's gain from pressure does not survive agents who decide on pleasure.** Under the corrected rule, L4 minus L0 is **+0.003 [−0.004, +0.009]**, inside the preregistered margin of 0.007. Under the old rule it was +0.021. So H38 is effectively untested against agents who choose on the verdict's yardstick. Its headline was mostly pressure correcting a cautious formation rule.

- **C1 (key test): within margin**, as predicted. +0.0034 [−0.0037, +0.0092], Holm p 0.16. The gain falls by 0.017 [0.012, 0.023] compared with the old rule, paired by pairing.
- **C2 (withdrawal alone): holds**, as predicted. −0.017 [−0.022, −0.011], a little worse than under the old rule (−0.011).
- **C3 (the old rule under-forms): holds**, as predicted. The corrected rule alone raises pleasure by +0.028 [+0.023, +0.033] and week-0 formation from 0.51 to 0.84.

All three predictions hit. That is less impressive than it sounds: the diagnosis, run before the prereg, had already shown the formation shares.

## Why the result may be counterintuitive: we may have measured the wrong thing

The author asked that this be said plainly. Two reasons, then two smaller ones.

**1. The construct.** In the model, "pairing" means nesting only: moving in with one fixed partner, in a world of two partners and one friend. Romance is not modeled. Romantic priority (a partner outranking friends by rule) is not modeled; withdrawal is the closest proxy. Exclusivity is not modeled: the world is monogamous only because no other partner exists. Partner choice is not modeled. So H38 tested pressure to move in together, not amatonormativity in the author's sense. The author has asked for these to be separated as H38b (nesting, romantic priority and exclusivity, in a 4–6 agent world), logged in experiments/hypotheses.jsonl. Withdrawal, the part closest to the romantic ideal, is the one part that hurt, here and in H38.

**2. The decision rule.** This check. Agents decided to form on 26 weeks of net wellbeing, and the verdict judged pleasure. That rule under-forms on pleasure, and pressure was correcting it. With agents who decide on pleasure, the gain is gone.

**Smaller limits.** Pleasure is capped at 1, and 54% to 82% of person-weeks sit at the cap. Labor and care are not tracked.

## Diagnosis: what the decisions use

Every decision in the H38 household compares rollouts. Forming at week 0, retrying every 13 weeks while apart, and the stay readings all compare a 26-week rollout of living together against the member's outside option (the better of 26 weeks alone or with the friend). Both members must prefer forming. Either can block. The score is net wellbeing: pleasure minus both kinds of suffering. No discounting, no risk term.

The yardstick does most of the work, not the window:

| Rule | Forms at week 0 (L0) |
|---|---|
| old: net wellbeing, 26 weeks | 0.51 |
| net wellbeing, 52 weeks | 0.58 |
| own pleasure, 26 weeks | 0.80 |
| own pleasure, 52 weeks (corrected) | 0.84 |

The members who block under the old rule expect slightly more pleasure together (0.957 vs 0.947), but much more suffering (0.169 vs 0.113). Net says no; pleasure says yes.

The old rule is not wrong on its own terms. Forcing the 236 declined pair-seeds to form raises their 156-week pleasure by +0.014 but lowers their net wellbeing by −0.008. It is a reasonable chooser on net wellbeing, judged on pleasure.

## The numbers

Means over 120 pairings.

| | old L0 | old L4 | old W4 | G-L0 | G-L1 | G-L4 | G-W4 |
|---|---|---|---|---|---|---|---|
| pleasure (primary) | 0.928 | 0.949 | 0.917 | 0.956 | 0.957 | 0.959 | 0.940 |
| pleasure − suffering | 0.729 | 0.761 | 0.708 | 0.785 | 0.784 | 0.783 | 0.760 |
| share of weeks together | 0.53 | 0.88 | 0.44 | 0.82 | 0.86 | 0.92 | 0.73 |
| pairs formed at week 0 | 0.51 | 0.88 | 0.49 | 0.84 | 0.89 | 0.98 | 0.71 |
| households that end (of formed) | 0.60 | 0.23 | 0.67 | 0.29 | 0.28 | 0.20 | 0.35 |
| friend visits per week | 1.08 | 0.62 | 0.82 | 1.10 | 1.00 | 0.60 | 0.68 |
| stay readings held by pressure | 0 | 0.29 | 0.08 | 0 | 0.07 | 0.12 | 0.03 |
| stay readings worth it (mean per pairing; H38 pooled readings, so its 0.80 differs) | 0.69 | 0.65 | 0.57 | 0.86 | 0.84 | 0.83 | 0.77 |
| unclipped pleasure | 1.002 | 1.088 | 0.975 | 1.056 | 1.071 | 1.106 | 1.021 |
| person-weeks at the cap | 0.54 | 0.70 | 0.48 | 0.66 | 0.68 | 0.73 | 0.58 |

Differences, paired by pairing, 95% bootstrap interval:

| Comparison | Pleasure | Net | Without the direct terms | Unclipped | Weeks together |
|---|---|---|---|---|---|
| old L4 − old L0 (H38) | +0.021 [+0.013, +0.028] | +0.032 | +0.012 | +0.086 | +0.35 |
| **G-L4 − G-L0 (C1)** | **+0.003 [−0.004, +0.009]** | −0.002 [−0.020, +0.014] | **−0.010 [−0.015, −0.005]** | +0.050 | +0.10 |
| G-L1 − G-L0 | +0.001 [−0.001, +0.004] | −0.001 | −0.001 | +0.015 | +0.04 |
| G-W4 − G-L0 (C2) | −0.017 [−0.022, −0.011] | −0.025 | −0.017 | −0.035 | −0.09 |
| old W4 − old L0 | −0.011 [−0.016, −0.007] | −0.021 | −0.011 | −0.027 | −0.09 |
| G-L0 − old L0 (C3) | +0.028 [+0.023, +0.033] | +0.056 | +0.028 | +0.054 | +0.30 |

What these say:

- **The corrected rule alone beats pressure.** G-L0 (0.956) is above old L4 (0.949). Choosing well does more than pressure did, with no stigma, no lost friend time and nobody held in.
- **With good choosers, pressure changes how people live for the worse.** Take away what the reward pays directly, and L4 lowers pleasure by 0.010. The small positive total is the reward being paid out. That is close to what H38 predicted, but it is descriptive here, not a preregistered test.
- **Unclipped pleasure still rises under pressure (+0.050).** Most of that is the reward term (0.08 per week while together) landing above the cap. It is a sensitivity line, with no verdict weight.
- **Commitment still rises.** Pressure still adds weeks together (+0.10) and pushes the last 15% of pairs in at week 0. H38's P3 likely survives, smaller.
- **Withdrawal hurts more with good choosers** (−0.017 vs −0.011). More pairs live together, so more people lose friend time.
- **Pairs pushed in by L4 under the corrected rule** (77 of 480 pair-seeds) still gain +0.032. Part of that is the reward paid to them directly. They are few, so the average barely moves.

## Misses and caveats

- **The corrected rule is not a perfect chooser.** On the declined pair-seeds, it would form 69% of them, but both members end up better off on pleasure in only 34%. It matches the verdict's yardstick; its 52-week rollout still misjudges some pairs.
- **It throws away suffering.** Agents deciding on pleasure alone ignore the extra suffering they take on together. The net line shows this costs nothing on average here (net rises +0.056 under G-L0), but whether agents should decide on pleasure or on net wellbeing is the author's call, not something this check settles.
- **One rule point.** 52 weeks and own pleasure, with unanimity. A joint rule (the pair's total) was not tested.
- **Leaving on distress** still ignores the yardstick.
- **The margin (0.007) is chosen**, a third of H38's gain. The estimate (+0.003) is well inside it, and the interval's top (+0.009) is just above it.

## Can be about / cannot be about

This can be about whether H38's pleasure gain survives scripted agents who decide to form and stay on their own clipped pleasure over 52 weeks, in the same household world (baseline rules, may decline, fixes and levers on, F4, items V2).

It cannot be about:

- people, real romantic norms, or romance at all (see the construct section above);
- good choosers in general: one rule point, and it still misjudges some pairs;
- which yardstick agents should use;
- a number as such: 52 weeks and the margin are chosen.

## What this means for H38

H38 stays **not supported**, but for a different reason than its write-up gave. The headline "pressure raises pleasure" was an artifact of a cautious formation rule. Against agents who decide on pleasure, pairing pressure does about nothing to pleasure at L4 (+0.003, within the margin), and without the reward it pays, it does slight harm. Withdrawal from friends harms under both rules. H38's own predictions (a low peak, harm at L4) were not retested under the corrected rule and remain untested.

## Recommendation for H39

**Use the corrected rule (own pleasure, 52 weeks) as H39's main formation and stay rule**, with the old rule as one descriptive sensitivity arm. H39 judges on pleasure; if agents decide on net wellbeing, any rule that pushes pairs together will look good for the same reason pressure did here. The flag is `FixConfig(decide_on="pleasure", decide_weeks=52)`. Before H39 runs, the author should confirm that agents deciding on pleasure is acceptable, since it ignores suffering at the moment of choice.

## Reproduction

`uv run python scripts/h38_formation_check.py --diagnose` (rule inputs and forced formation), `--reach`, `--run`, `--analyze`. Tests: `uv run pytest tests/test_formation_check.py`. Rows in runs/h38-formation/ (not committed).
