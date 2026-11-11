# H38 pairing norms: results

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Status: run once on 2026-11-11, after the preregistration and its Amendment 1 ([h38-pairing-norms-prereg.md](h38-pairing-norms-prereg.md), commits 15b2a96 and c69a56e; code dd7d4ce). Design: [h38-pairing-norms-design.md](h38-pairing-norms-design.md).

Setup: 120 pairings × 4 seeds × 14 arms = 6,720 runs (3,634 s on 3 workers). The world is the v2-retest household: baseline rules, pairs may decline to form, fixes and levers on, exit fallback F4 with items. Scripted agents, no model calls, every number ASSUMED. Run with `uv run python scripts/h38_pairing_run.py --run`, then `--analyze`, `--extras`, `--liberty`. Per-run rows are in runs/h38-pairing/ (not committed).

## Verdict

**Not supported.** In this model, pairing pressure raises pleasure with everyone counted, at every level tested. It does not peak low.

- **P1 misses.** Pleasure rises all the way up the dial. The top preregistered level (L4) is the best, and the descriptive L8 is higher still.
- **P2 misses.** At L4, pleasure is **+0.021** above no pressure [+0.013, +0.028]. It was predicted to fall.
- **P3 holds robustly.** Pressure helps coordination and commitment, as predicted. Weeks lived together rise by 0.35, and households that end fall by 0.37.
- **P4 is not shown.** Agents who value pairing least gain slightly *more* than those who value it most (+0.005 [−0.011, +0.021]). P4 was marked underpowered before the run.

One part of the dial does behave as H38 says: **withdrawal from friends.** It is the only part that lowers pleasure. The dial as a whole rises anyway, because the other three parts help more than withdrawal hurts.

## Pleasure by dial level

Means over 120 pairings. At level L, stigma, reward and exit stigma are each 0.02 × L per week, and withdrawal is min(0.6, 0.15 × L).

| | L0 | L0.5 | L1 | L2 | L4 | L8 (descriptive) |
|---|---|---|---|---|---|---|
| pleasure (primary) | 0.928 | 0.932 | 0.936 | 0.941 | 0.949 | 0.957 |
| pleasure − suffering | 0.729 | 0.737 | 0.746 | 0.754 | 0.761 | 0.764 |
| non-offsettable suffering | 0.023 | 0.020 | 0.018 | 0.016 | 0.015 | 0.017 |
| share of weeks lived together | 0.53 | 0.60 | 0.66 | 0.77 | 0.88 | 0.92 |
| pairs formed at week 0 | 0.51 | 0.58 | 0.65 | 0.71 | 0.88 | 0.98 |
| households that end (of those formed) | 0.60 | 0.56 | 0.47 | 0.36 | 0.23 | 0.20 |
| friend visits per week | 1.08 | 1.05 | 1.01 | 0.89 | 0.62 | 0.62 |
| stay readings held by pressure | 0 | 0.09 | 0.14 | 0.22 | 0.29 | 0.31 |
| stay readings worth it | 0.80 | 0.76 | 0.74 | 0.71 | 0.67 | 0.67 |
| unclipped pleasure | 1.002 | 1.015 | 1.028 | 1.052 | 1.088 | 1.165 |
| person-weeks at the cap | 0.54 | 0.56 | 0.58 | 0.63 | 0.70 | 0.82 |

Each level minus L0, paired by pairing, with a 95% bootstrap interval:

| Level | Pleasure | Net | Pleasure without the direct terms |
|---|---|---|---|
| L0.5 | +0.004 [+0.001, +0.007] | +0.008 [−0.001, +0.018] | +0.005 [+0.002, +0.008] |
| L1 | +0.007 [+0.004, +0.011] | +0.017 [+0.006, +0.029] | +0.009 [+0.006, +0.013] |
| L2 | +0.013 [+0.009, +0.017] | +0.025 [+0.012, +0.039] | +0.013 [+0.010, +0.017] |
| L4 | +0.021 [+0.013, +0.028] | +0.032 [+0.011, +0.051] | +0.012 [+0.006, +0.018] |
| L8 | +0.028 [+0.016, +0.039] | +0.035 [+0.006, +0.060] | +0.013 [+0.005, +0.019] |

**The gain is not just the reward being paid.** "Pleasure without the direct terms" takes away the reward and adds back the stigma, week by week, inside the cap. It still rises by about +0.012 at L4. Pressure changes how people live, and in this model that change raises pleasure.

**The cap does not hide a reversal.** The same tests on unclipped pleasure give the same shape: L4 is +0.086 [+0.072, +0.100] above L0. With 54% to 82% of person-weeks at the cap, the clipped primary understates the gain; it does not hide a loss.

## Each part alone

Each part alone at L4, minus L0:

| Part alone at L4 | Pleasure | Net | Without the direct terms | Weeks together | Friend visits per week |
|---|---|---|---|---|---|
| S4 stigma | +0.011 [+0.006, +0.015] | +0.027 | +0.022 | +0.28 | +0.03 |
| R4 reward | +0.020 [+0.017, +0.023] | +0.024 | +0.010 | +0.11 | +0.02 |
| W4 withdrawal | **−0.011 [−0.016, −0.007]** | −0.021 | −0.011 | **−0.09** | −0.27 |
| X4 exit stigma | +0.009 [+0.006, +0.012] | +0.022 | +0.011 | +0.17 | −0.01 |

At L1, the parts are smaller and run the same way: stigma +0.001 (interval crosses 0), reward +0.005, withdrawal −0.003 (crosses 0), exit stigma +0.003.

- **Withdrawal does the harm, and only withdrawal.** It cuts friend visits by a quarter and lowers pleasure and net pleasure. It also *lowers* pairing: agents foresee the lost friend time in their formation rollouts, so fewer pairs form (−0.09 weeks together). The romantic ideal makes pairing less attractive, not more.
- **Stigma helps, even after paying its own sting.** Stigma alone pushes 28% more weeks into households, and those households do better. Net of the stigma paid, pleasure rises +0.022. I predicted stigma would do the most harm (S6). That is a miss.

## Why pressure helps here: pushed-in pairs do better

Among pair-seeds that decline at L0 but form at week 0 under pressure:

| Level | Pairs pushed in (of 480) | Their pleasure change | Net change | Without direct terms | Share worse off |
|---|---|---|---|---|---|
| L0.5 | 54 | +0.032 | +0.054 | +0.034 | 0.28 |
| L1 | 82 | +0.037 | +0.068 | +0.038 | 0.30 |
| L4 | 185 | +0.044 | +0.074 | +0.030 | 0.08 |
| S4 (stigma only) | 190 | +0.026 | +0.053 | +0.039 | 0.28 |

H38's first channel predicted these pairs would be worse off (S1). They are better off. That is a miss.

My reading, not tested here: at L0, pairs decline too often for their own pleasure. The formation rule compares 26 weeks of net wellbeing, together against apart. The life they would actually live together is better than that comparison says. The v2 retest flagged this mismatch as a limit: the bar scores net wellbeing over a short window, the verdict scores pleasure over 156 weeks. Pressure tilts the comparison toward forming, and so it partly corrects that under-forming. **If that reading is right, this result is about a cautious formation rule, not about pairing norms.** The next step tests it.

## Who bears it (P4, S9)

Pleasure change at L4 minus L0, per agent, by assigned values-pairing weight:

| Values pairing | Agents | Pleasure change | Net change | Share losing more than 0.01 | Stigma and exit stigma paid per week |
|---|---|---|---|---|---|
| low (v = 0) | 105 | +0.025 | +0.045 | 0.15 | 0.011 |
| mid (v = 0.5) | 65 | +0.013 | +0.008 | 0.32 | 0.015 |
| high (v = 1) | 70 | +0.021 | +0.036 | 0.24 | 0.011 |

- **No group bears a net harm on average**, and the low valuers gain the most. P4 predicted the reverse.
- **There are losers in every group.** About one agent in four loses more than 0.01, most of all in the mid group.
- **Under withdrawal alone (W4), 40% to 48% of agents in every group lose**, and the low and high groups lose about equally (−0.012, −0.013).
- The v groups are unbalanced (105, 65, 70 agents), because v comes from a hash of the persona id. The weight is assigned, not elicited.

## Exit is harder (S2), and contact shrinks (S3)

- **Exit is harder.** At L4, 29% of stay readings are "held by pressure": the pair stays only because of the pressure. With the pressure removed, they would leave. The share that stays because it is worth it falls from 0.80 to 0.67, and the share that would leave anyway falls from 0.20 to 0.03. So H38's second channel shows: commitment rises partly by holding people in, and the worth-it share falls. In this model, the held weeks are still good weeks on pleasure.
- **Friend contact shrinks.** Friend visits per week fall from 1.08 to 0.62 at L4, and from 1.12 to 0.54 while living together. That is close to built in, since withdrawal scales the wish to see friends, so it is a manipulation check. Pleasure still rises, because time with the partner and the shared life replace the lost friend time.

## Liberty with powers (S8)

Subsample: the 15 hand pairings, seed 0, measured at weeks 0 and 52 (`--liberty`).

| | L0 | L4 | S4 | R4 | W4 | X4 |
|---|---|---|---|---|---|---|
| liberty (bits, the lower partner) | 2.25 | 1.92 | 1.79 | 2.12 | 2.63 | 2.17 |

Pressure changes no rule, so liberty can move only through the household's state: who lives where, and how much money is in the pot. The pattern fits living together under the baseline cards giving fewer options than living apart. Pressure that pairs people up lowers liberty, and withdrawal, which pairs fewer people, raises it. I did not check that reading state by state. This is 15 pairings and one seed: descriptive.

## Prereg vs actual

| ID | Prediction | Actual | Verdict |
|---|---|---|---|
| P1 | peak at L0.5 or L1, above L0 | peak at L4 (L8 higher still) | miss |
| P2 | L4 below L0 | +0.021 [+0.013, +0.028] | miss (robust, opposite sign) |
| P3 | more weeks together AND fewer endings at L4 | +0.35 [+0.30, +0.40]; −0.37 [−0.43, −0.30]; Holm p 0.0004 | holds robustly |
| P4 | low valuers bear more of the change than high valuers | +0.005 [−0.011, +0.021] | not shown (underpowered; point estimate in the wrong direction) |
| S1 | pushed-in pairs worse off | +0.044 at L4 | miss |
| S2 | held by pressure rises with L | 0 → 0.29 | holds (0 at L0 cannot fail) |
| S3 | fewer friend visits under withdrawal | 1.08 → 0.62 (L4), 0.81 (W4) | holds (manipulation check) |
| S6 | stigma does the most harm | withdrawal is the only part that harms; stigma helps (+0.011) | miss |
| unclipped | (sensitivity, no weight) | same shape, L4 +0.086 | agrees with the primary |

By the preregistered rule, H38 is **not supported**. Partly supported would have needed P2.

## Surprises

- **Pressure corrects under-forming.** The pairs that pressure pushes in are better off, not worse. That is the opposite of H38's main channel.
- **The romantic ideal works against pairing.** Agents who foresee losing their friends pair less.
- **Pleasure rises while friend contact nearly halves.** Something in the shared life (time with the partner, the items, intrinsic pairing value) makes up for it. I did not break that down.
- **Liberty falls as pressure rises,** through where people live, not through any rule.

## Known model limits (from the exit-fallback agent)

- **The pleasure cap.** Partly fixed: the unclipped value is recorded, and the same tests run on it. Most person-weeks are at the cap (54% at L0, 70% at L4), so the clipped primary is a compressed scale. The unclipped line agrees in sign and shape.
- **Labor and care are not tracked.** Not fixed. A pairing norm that loads unpaid care onto one partner would be invisible here. That is a real blind spot for this question.
- **A stay-commitment breach bypasses the forfeit under settling arms.** Not touched: the baseline rule set has no stay commitment.

## Can be about / cannot be about

This can be about a fixed, external pressure dial acting on scripted agents in one household world, with one formation rule, one exit fallback (F4) and one item valuation.

It cannot be about:

- people or real romantic norms;
- pressure that comes from peers or grows as more people pair (there is no network);
- unpaid care inside pairs;
- a number as such: the 0.02 unit, the withdrawal rate and the 0.04 intrinsic weight are assumed;
- formation in general. The result leans on how agents decide to form (a 26-week net-wellbeing rollout against an outside option), and the evidence above suggests that rule under-forms on pleasure.

## Next step

Test the reading behind the main result. Rerun L0 and L4 with agents deciding to form and stay on the same yardstick the verdict uses: pleasure, over a longer window (for example a 52-week rollout scored on pleasure).

- If pressure's gain disappears, this result is about a cautious formation rule, and H38 is untested against agents who already choose well.
- If the gain survives, pressure helps in this model for a reason not yet found.

Withdrawal is the part that matched H38. It deserves its own small test with friend contact valued per persona: the author's rule counts contact only as each persona values it.

## Reproduction

`uv run python scripts/h38_pairing_run.py --reach` (verdict reachability and the model-level low peak), `--run`, `--analyze`, `--extras`, `--liberty`. Tests: `uv run pytest tests/test_pairing.py`.
