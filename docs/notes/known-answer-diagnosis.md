# Known-answer diagnosis: PT-R T3, K1 and KO1 under the time-together versions

Wording rule: agents feel nothing; "pleasure", "value", "forecast", "held" and "worth it" are glosses for modeled numbers.

Written 2026-11-16 by an agent at the author's request ("diagnose, don't fix"). Measurement only: no model behaviour changed, no bar
changed, no parameter fitted. Scripted agents, no model calls. Code: scripts/known_answer_diagnosis.py. Rows: runs/diagnose-t3/
(queue.sh, status.log, k1-*.json, ko1-*.jsonl, ptr-*/rows.jsonl, analysis.json).

**Status: done** (2026-11-17). Every run below is complete; A6 and TT2 were reproduced exactly for each check before anything was toggled.

## The three failures, as reported

| Check | A6 | TT (q 0.1) | TT2 (q 0.3) | Bar |
|---|---|---|---|---|
| PT-R T3 (the routine picks the action that is best one week ahead) | 0.953 | 0.898 | 0.869 | no more than 0.02 below v2's 0.947 |
| K1 (the trap's held share / the baseline's) | 0.128 / 0.000 | not run | 0.069 / 0.000 | ≥ 0.10 / ≤ 0.02 |
| KO1 (outside forecast's error, lived − forecast, bar exits in B) | +0.027 | +0.037 | +0.055 | mean within ±0.02, interval inside ±0.04 |

## PT-R T3

**Label: bar (the check), not bug, not mismatch. Confidence: high.**

**What T3 counts.** For each sampled decision, the agent's own top action (or idle, when nothing it values clears its action floor of
0.003) against the action whose one-week actual is best (or idle, when no action's actual is above 0). The two sides use different
floors: 0.003 for the agent, 0 for the actual (scripts/value_consistency.passtest). An action worth between 0 and 0.003 is one the agent
rightly leaves (by its own floor) and T3 counts as a miss.

**What changed.** Background time adds `together_event × together_bg` (0.11 under TT, 0.33 under TT2, times the substitution factor) to
weekly raw pleasure in every household week. Household raw pleasure already sat above the saturating scale's knee (0.8, ADR 0019), so
each action's marginal pleasure is squeezed. On the PT-R rows, a rest in a household:

| | raw pleasure gained | pleasure gained | pleasure / raw (the scale's slope) | own net gained |
|---|---|---|---|---|
| A6 | 0.0755 | 0.0131 | 0.174 | 0.0204 |
| TT | 0.0728 | 0.0066 | 0.091 | 0.0114 |
| TT2 | 0.0793 | 0.0027 | **0.033** | 0.0093 |

Time together shows the same squeeze (0.156 → 0.088 → 0.031). The best action's one-week actual falls into (0, 0.003] in 1.0% of
decisions under A6, 5.8% under TT and **10.2%** under TT2.

**The misses, by kind** (the PT-R rows on disk, 40 pairings, seed 0):

| | T3 | decisions | floor misses | together chosen, rest best (partner share) | other | T3 with one floor (0.003 both sides) |
|---|---|---|---|---|---|---|
| v2 (reference) | 0.947 | 453 | 2 | 6 | 16 | 0.949 |
| A6 | 0.953 | 382 | 4 | 4 | 10 | 0.963 |
| TT | 0.898 | 362 | 13 | 16 | 8 | 0.934 |
| TT2 | 0.869 | 373 | **34** | 10 | 5 | **0.954** |

In the floor misses the agent's value of the best action matches its one-week actual to within 0.00004 on average (TT2: perceived
0.00142, actual 0.00142). **The routine is not mis-valuing anything there; it is right that the action is under its floor.**

**The decisive check: a perfect valuer fails too.** Replace every perceived value with the one-week actual it is held to (the
prereg's own oracle, agent-recalibration-prereg.md, which scored 99.9% on the v1 rows) and keep the 0.003 floor:

| | agent T3 | oracle T3 | agent − oracle |
|---|---|---|---|
| v2 | 0.947 | 0.989 | −0.042 |
| A6 | 0.953 | 0.990 | −0.037 |
| TT | 0.898 | 0.942 | −0.044 |
| TT2 | 0.869 | **0.898** | **−0.030** |

Under TT2 an agent that knew every one-week value exactly would score 0.898, 0.049 under v2's 0.947, and fail PT-R's bar. The
routine's distance from that oracle is about the same under every version (−0.03 to −0.04), and smallest under TT2. **All of T3's
fall is the check's ceiling falling, not the routine getting worse.**

**Two more things the T3 bar mixes in.**
- **The reference is from another world.** PT-R holds the hybrid's T3 to v2's T3 "on the same sample", but v2's rows
  (runs/value-consistency-v2-sat-world) were played without background time. Under TT and TT2 the comparison is across worlds.
  Rerun here (descriptive, not a verdict): v2 in A6's world reproduces the original v2 rows exactly (480 of 480 decisions), and **v2 in
  TT2's world scores T3 0.887** (oracle 0.936; 21 floor misses against 2). The hybrid's 0.869 is 0.018 below that same-world
  reference, inside the 0.02 bar. v2 falls with the world too.
- **The together misses (TT 16, TT2 10) are the partner share.** The agent values time together as its own net plus prosocial × the
  partner's; T3's "net" target counts only its own. Under T3's "social" target (the utility's own definition) T3 is 0.909 (TT) and
  0.879 (TT2). This was so under v2 and A6 too; it grows a little because own values shrink while the partner term stays.

**One flag at a time from A6** (PT-R's sample, 40 pairings, seed 0; rows in runs/diagnose-t3/ptr-*):

| | T3 | oracle T3 (perfect one-week values, same floor) | agent − oracle | best action under the floor | floor misses | rest's one-week value in a household |
|---|---|---|---|---|---|---|
| v2 (reference) | 0.947 | 0.989 | −0.042 | 1.1% | 2 | 0.019 |
| A6 | 0.953 | 0.990 | −0.037 | 1.0% | 4 | 0.020 |
| subst | 0.940 | 0.982 | −0.042 | 1.8% | 6 | 0.022 |
| bg 1.1 | 0.905 | 0.951 | −0.046 | 4.9% | 14 | 0.013 |
| TT | 0.898 | 0.942 | −0.044 | 5.8% | 13 | 0.011 |
| bg 3.3 | **0.856** | **0.861** | −0.005 | 13.9% | 34 | 0.008 |
| TT2 | 0.869 | 0.898 | −0.030 | 10.2% | 34 | 0.009 |

**Background time moves T3: −0.048 at q = 0.1 and −0.097 at q = 0.3, alone. Substitution alone moves it −0.013 (within the bar).**
The LAT flags cannot act here: the sample has no LAT, and they were byte-identical in K1's sample and H41's B arm.
In every row the oracle falls with T3. At q = 0.3 the oracle itself is 0.861 to 0.898. **The bar as written (v2's 0.947 − 0.02 =
0.927) cannot be met at q = 0.3 by any agent that keeps the 0.003 floor, a perfect one-week valuer included.** (With background 3.3
alone the agent is within 0.005 of the oracle.) The LAT flags are confirmed inert here as well: TT2 without them gives the same 480
decisions, byte for byte.

## K1

**Label: bar (what the check pools), plus fragility. Not a bug; not the forecast mismatch. Confidence: high.**

**What K1 counts.** The trap fixture (rules/household/trap: a leaver forfeits the pool; the higher earner can veto contact and work),
the formation check's 12 control pairings, seed 900, the stay test on every week both partners are in: K1 = held weeks / staying weeks,
pooled over all 12 runs. A staying week is held if, replayed with every exit cost removed, a partner leaves.

**Reproduced exactly** (k1-a6.json: 16/125 = 0.128; k1-tt2.json: 23/332 = 0.069). **TT, never run before, passes: 17/130 = 0.131.**

**One flag at a time from A6** (trap runs, staying/held per pairing):

| pairing | A6 | lat flags | subst | bg 1.1 | TT | bg 3.3 | TT2 |
|---|---|---|---|---|---|---|---|
| anchor / host | 9/0 | 9/0 | 28/0 | 9/0 | 9/0 | **73/0** | **137/0** |
| anchor / peacekeeper | 9/0 | 9/0 | 9/0 | 9/0 | 9/0 | 9/0 | **79/0** |
| anchor / steward | 9/0 | 9/0 | 9/0 | 9/0 | 9/0 | **112/0** | 9/0 |
| bargainer / host | 9/0 | 9/0 | 9/0 | 9/0 | 17/5 | 13/0 | 9/0 |
| bargainer / wanderer | 17/7 | 17/7 | 9/0 | 9/0 | 9/0 | 17/7 | 9/0 |
| host / peacekeeper | 13/4 | 13/4 | 12/3 | 16/7 | 21/12 | 16/7 | 24/13 |
| host / steward | 9/0 | 9/0 | 9/0 | 9/0 | 9/0 | 20/11 | 13/4 |
| host / wanderer | 14/5 | 14/5 | 11/2 | 9/0 | 9/0 | 9/0 | 16/6 |
| (5 more pairings) | 9/0 each | same | same | same | ≤ 11/0 | ≤ 12/0 | 9/0 |
| **K1** | **0.128** | **0.128** | **0.038** | **0.061** | **0.131** | **0.081** | **0.069** |
| baseline | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

The LAT flags (`lat_bg_keep`, `lat_travel`, `lat_gifts`) change nothing, byte for byte: the formation check's world has no LAT.

**Two different things move K1.**

1. **At q = 0.3, re-formed households fill the denominator.** Split each run at its first exit:

   | | first spell: held / staying | share | later spells: staying weeks (held) |
   |---|---|---|---|
   | A6 | 16 / 125 | 0.128 | 0 |
   | bg 3.3 | 25 / 143 | **0.175** | 167 (0) |
   | TT2 | 23 / 134 | **0.172** | 198 (0) |

   **In the trap as first entered, more weeks are held at q = 0.3 than under A6, not fewer.** K1 falls only because pairs now come
   back. In anchor / host under TT2, A leaves at week 9 exactly as under A6, returns, and the pair then stays 128 more weeks. None is
   held, and by the lived numbers none should be: at every reading in that spell the status quo beats the outside option for both
   (SQ − O between +0.09 and +0.68), and lived pleasure is 0.997 (A) and 0.991 (B) in the household against 0.819 and 0.657 out of it.
   Anchor / peacekeeper is the same story (0.997 / 0.974 in, 0.904 / 0.510 out). These are weeks the household is worth it, in a
   household whose rules still allow control. Under A6 and TT nobody comes back into the trap.

2. **Below q = 0.3 the share is fragile.** A6's 16 held weeks come from 3 of 12 pairings. Substitution alone (no background time)
   gives 0.038, background 1.1 alone 0.061, and both together (TT) 0.131. No later spells are involved. The flags change which of the
   few borderline pairs is held for a few weeks before leaving. A pooled share of about 16 held weeks cannot tell 0.10 from 0.13 under a
   small change to the world. A6's own result already called its pass "thin".

**Why this is not the KO1 mismatch.** If a pessimistic outside forecast were keeping people in, the long stays would be weeks the
lived numbers do not support. They are the opposite: the life lived outside is far worse than the life in the re-formed household.

**What would decide it (the author's call; nothing here changes the bar).** K1 was written for a world where nobody re-forms inside
the trap. Read on the first spell it passes under every version where re-formation happens (0.175, 0.172). Whether K1 should be read
on the first spell, on held weeks per run, or with more pairings or seeds to steady it, is a change to the check. That is not mine to
make, and it should be preregistered before anyone looks at the result it gives.

## KO1

**Label: mismatch (the outside forecast's known stand-in: it never re-forms), made larger by time together. Not a bug. Confidence:
high on the cause; the flag split is below.**

**What KO1 measures.** For each lived bar exit in H41's B arm (120 pairings), L − O: the leaver's mean yardstick (pleasure − w ×
suffering) over the 52 weeks after the exit, minus the outside value O of the reading that decided it. O is `hybrid.lived_outside`:
the lived world played on with the member gone, with no readings inside the future, so the forecast leaver never returns or
re-forms. Lived leavers do both.

**Reproduced exactly.** The instrumented reruns give the same exits and the same errors as the original rows, exit for exit
(A6 +0.0268, 73 exits; TT2 +0.0547, 68 exits). The new field is the share of the 52 post-exit weeks the leaver is back in a household.

**The error is the leavers who come back:**

| | exits | back in for half the window or more | the rest | all |
|---|---|---|---|---|
| A6 | 73 | **+0.048** [+0.028, +0.070] (50, 68%) | −0.019 [−0.055, +0.011] (23) | +0.027 |
| TT2 | 68 | **+0.066** [+0.038, +0.098] (54, 79%) | +0.012 [+0.002, +0.024] (14) | +0.055 |

Leavers who mostly stay out are forecast about right under A6 (−0.019, interval spans 0). Those who come back live better than the
forecast said, because the forecast never brings them back: their yardstick is 0.880 in a household against 0.669 out of one (A6).
**So KO1 already failed under A6 for this reason alone; the time-together flags did not create the bias.** A6's write-up named the
same two stand-ins (no re-formation, no fresh return); this is the measurement of it.

**What TT2 adds, A6 → TT2 (+0.028):**
- more leavers come back (68% → 79%): **+0.007**;
- a comeback is further from the forecast (+0.048 → +0.066): **+0.014**;
- the leavers who stay out (14 exits, n small): **+0.007**.

The first two are the hypothesis: households are worth more, so more leavers re-form and each re-formation is a bigger miss for a
forecast that never re-forms. The third is within noise for 14 exits.

**One flag at a time from A6** (B arm, 120 pairings each; the LAT flags are inert in B: the TT sweeps `tt_keep0`, `tt_keep04`,
`tt_tr017`, `tt_tr067` give B rows identical to TT's):

| | KO1 | 95% interval | exits | back in for half or more: error (n) | the rest: error (n) | leavers back in |
|---|---|---|---|---|---|---|
| A6 | +0.027 | [+0.005, +0.047] | 73 | +0.048 (50) | −0.019 (23) | 68% |
| subst | +0.028 | [−0.001, +0.057] | 73 | +0.046 (51) | −0.013 (22) | 70% |
| bg 1.1 | +0.039 | [+0.018, +0.059] | 69 | +0.046 (49) | +0.020 (20) | 71% |
| bg 3.3 | +0.051 | [+0.028, +0.081] | 70 | +0.058 (57) | +0.022 (13) | 81% |
| TT2 | +0.055 | [+0.033, +0.085] | 68 | +0.066 (54) | +0.012 (14) | 79% |

**Background time moves KO1, and more with higher q (+0.012 at 1.1, +0.025 at 3.3). Substitution moves nothing (+0.001).** Most of the
step from A6 to TT2 (+0.025 of +0.028) is background time alone. The leavers who come back are 0.046 to 0.066 better off than forecast
in every configuration: **that gap is what keeps KO1 failing, under every version including A6.** The error of the leavers who stay
out (−0.019 to +0.022) moves with small changes to the world about as much as anything else, and is a small group.

**Next step (the author's decision; a design change, not a bug fix).** The forecast of leaving would have to hold what lived leavers
do after leaving: return readings and retries inside `lived_outside`'s futures. A6's write-up named this already. It is the only change
that addresses the cause; anything that shrinks the error another way (a bias term, a shorter post window) would be fitting to the
check.

## Do the three share a cause?

**One root, three different mechanisms, and only one of them is the mismatch the previous agent guessed.** The root is the same:
background time from a shared home (`together_bg`, q) makes household weeks worth more. Each check meets it differently:

| | what q does to it | label | flag that moves it |
|---|---|---|---|
| PT-R T3 | pushes household pleasure up the saturating curve, so every action's one-week value shrinks toward the agent's 0.003 floor; T3 counts the floor's idles as misses. The routine's values stay right. | **bar** | `together_bg` |
| K1 | at q = 0.3 trap pairs come back after leaving and stay, worth it; those weeks dilute a pooled share. Below 0.3, small changes move a thin result. | **bar** (+ fragility) | `together_bg` at 3.3; any flag below it |
| KO1 | the forecast of leaving never re-forms; with households worth more, more leavers re-form and each re-formation is a bigger miss. Fails under A6 already. | **mismatch** | `together_bg` |

The hypothesis "the routine's projection, the trap reading and the outside forecasts see household value differently from how lives are
lived" holds for **KO1 only**. **The routine's projection sees it correctly** (floor misses: perceived and actual agree to 0.00004; T6
holds). **The trap reading sees it correctly too**: the long stays are worth it by the lived numbers. **No bug was found.** So no
failing test and no default-off fix are proposed. `together_subst` and the LAT flags (`lat_bg_keep`, `lat_travel`, `lat_gifts`) do not
cause any of the three: the LAT flags are inert, byte for byte, in all three samples. Substitution moves K1 within its fragility and
nothing else.

## Proposed next steps (all need the author's decision; none was taken)

1. **PT-R T3 (bar).** Either hold T3 to the same floor on both sides (the agent's 0.003, or 0), or hold the hybrid to an oracle on
   the same rows (agent − oracle, which is −0.03 to −0.04 under every version), or rerun v2's reference rows in the same world as the
   hybrid (done here descriptively: v2 in TT2's world gives 0.887, and the hybrid is 0.018 below it). Each is a change to a
   preregistered check, so it should be preregistered before it is read. Not a reason to touch the floor
   itself: the floor is the agent's, and it behaves as designed.
2. **K1 (bar).** Decide what K1 should count when pairs re-form inside the trap: the first spell only, held weeks per run, or a larger
   sample (more pairings or seeds) so the 0.10 bar is not decided by one or two pairings. Preregister before reading.
3. **KO1 (mismatch; design change).** Give `lived_outside`'s futures what lived leavers have: return readings and retries. This is the
   only change aimed at the cause. Under ADR 0020 it is a model change behind a default-off flag. Findings it could move: everything
   that runs through the hybrid's decision to leave (H41's arms and its stop rule, the exit option KX2, the quiet path, LAT's verdict
   via who leaves, the hybrid's PT-H H1 for leave choices), because a less pessimistic outside forecast could mean more exits.
4. **Freezing.** Of TT2's three failures, only KO1 shows a real gap between how a decision values something and how it is lived, and it
   fails under A6 too. Whether the hybrid can freeze with a documented KO1 stand-in is the author's call.

## Confidence, and what was not checked

- **PT-R: high.** Three independent lines agree: the floor misses are exact values below the floor, the oracle falls with T3 under
  every flag, and v2 falls with the world too. Not checked: other floors or targets as a verdict (left to the author, preregistered).
- **K1: high on the mechanism at q = 0.3** (re-formed spells, per pairing, with readings and lived pleasure). **Moderate on "fragile"
  below it:** one seed and 12 pairings, as K1 is defined. More seeds were not run, because that would be a new check.
- **KO1: high that the comeback gap is the cause of the failure under every version; moderate on the size of each flag's share**,
  because exits change with any change to the world, and the stay-out group (13 to 23 exits) moves by ±0.02 run to run.
- **No bug.** The searches that could have found one: the routine's projected close against the world's (background time enters both
  the same way: connection, the together event, the substitution factor, LAT's kept share only in a week with a session); the floor
  misses' values against their actuals; reruns reproducing the original rows exactly for A6 and TT2 in all three checks.
- **Pins and fast suite:** no file under src/ or tests/ was changed (one new script and this note), so the 50 slow pins and the fast
  suite are unaffected and were not rerun.

## Reproduction

`caffeinate -s zsh runs/diagnose-t3/queue.sh` (K1 7 configurations, about 20 min; KO1 5 × 120 B lives, about 1 h 20; PT-R 4 × 40
pairings, about 2 h; 6 workers). Then `uv run python scripts/known_answer_diagnosis.py --ptr v2_a6,v2_tt2` (about 3 min) and
`--analyze` (runs/diagnose-t3/analysis.json). The A6 and TT2 rows the original write-ups used are reproduced, not reused, by every
harness here.
