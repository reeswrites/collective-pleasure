# Two hybrid bugs fixed before the freeze: friend visits at the world's satiety, and no stale return values

Wording rule: agents feel nothing; "pleasure", "suffering", "value", "forecast", "tally" and "held" are glosses for modeled numbers.

Model (A6): `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit · hybrid_tally=level · tally_half=13 · tally_line=0.02 · exit_grow=0.04 · hybrid_outside=lived · friend_satiety · fresh_return`, exit fallback F4 with items (F5 in the prenup arm), corrected rule. Compared with old (Amendment 3), A4 and A5 (ADR 0020).

Preregistration: [hybrid-a6-prereg.md](hybrid-a6-prereg.md) (commit 870fee7, before any code or run; hybrid prereg Amendment 6). Code 7658cbd. Run 2026-11-14 to 2026-11-15, scripted agents, no model calls, every number ASSUMED, at most 4 workers under `caffeinate -i`. Rows in runs/hybrid-a6/ (queue.sh, analysis.json, analyze.log, pt-analyze.log). Label for H41: four versions now (old, A4, A5, A6).

## In one paragraph

Both bugs Amendment 5 found are fixed behind two flags, off by default (the 50 pins reproduce byte for byte). The routine now values a friend visit at the habituation the world applies, and a member that leaves can no longer walk straight back in on a return value from an earlier spell. Unit tests show each bug with its flag off and the fix with it on. **The fixes change little.** 94 of 120 B lives are identical to A5, and weeks together in B moves −0.005 [−0.011, +0.000]. PIN, KF1, KR1, KW, KX2 (+0.020 [+0.008, +0.034]), KL2, PT-H (+0.0051, rho 0.95, 93%) and PT-R pass, and K1 passes too (0.128). **KO1 fails again, and by more than under A5.** The outside forecast's mean error is +0.027 [+0.004, +0.048] (bar: mean within ±0.02, interval inside ±0.04). The tail shrank (worst −0.31 → −0.21; mean absolute error 0.076 → 0.069), but the forecast now leans pessimistic about leaving, with an interval clear of 0. **By the prereg's rule A6 is not ready to freeze as `hybrid-N/2`.** The quiet path is still nearly absent (1 of 80 B exits). Forecasts still leave about twice as often as lived agents (B 52 weeks: 41.8% against 21.5%). H41 is still not supported, and pressure still holds people in under all four versions. The author's prediction holds for moving in as preregistered (+0.050 [0.000, +0.100]), but the exit option still raises weeks together (+0.053 [+0.021, +0.094]).

## Known-answer checks (A6; bars are A5's, unchanged)

| ID | Result | Bar | |
|---|---|---|---|
| PIN | 50 slow pins byte for byte with both new flags off (runs/hybrid-a6/pins.log); fast suite passes (the one failure was a mislabelled log row, fixed at a4473dd, unrelated) | byte for byte | **PASS** |
| KF1 | flag off: the routine values a visit at scale 1 while the world records it more than 0.1 lower (the bug); flag on: valued at exactly the scale the world records (tests/test_hybrid_a6.py) | | **PASS** |
| KR1 | flag off: a member that returned and leaves again keeps return value 5.0, in the lived world and in a forecast copy (the bug); flag on: 0 until a new return reading | | **PASS** |
| KT0–KT2, KC1, KO0 | A5's unit tests, in the fast suite with the flags off | | **PASS** (not rerun with A6's flags; neither fix touches the tally, the exit cost or the outside option's arithmetic) |
| KX2 | DiD **+0.0196 [+0.008, +0.034]** (11 of 12 pairings above 0); beats outside 0.375 with no exit cost, 0.292 with it; in-future exits in 48 of 48 futures each way, first at week 17 to 18 (runs/hybrid-a6/kx2-a6.json) | DiD > 0, interval above 0 | **PASS** |
| KO1 | **+0.027 [+0.004, +0.048]**, 73 bar exits in B | mean within ±0.02, interval inside ±0.04 | **FAIL** (mean and interval) |
| KL2 | story 4: both leave at the trial's end (week 78); nobody is ever alone (story-a6.json) | no stuck stretch over 26 weeks | **PASS** (trivially, as under A5) |
| K1 | trap 0.128 (125 staying weeks), baseline 0.000 (224) (runs/hybrid-fix/trap-a6.json) | ≥ 0.10 / ≤ 0.02 | **PASS** (the same thin pass as A5) |
| PT-H | A1's sample, A6 flags: H1 **+0.0051** [+0.0025, +0.0079]; H2 **0.951** (1,246 option-units); H3 **93.5%** (458); 597 choice-units (runs/hybrid-passtest-a6/) | ±0.010 (interval inside ±0.015); ≥ 0.80; ≥ 80% | **PASS** |
| PT-R | T1 0.950 (v2 0.955), T2 0.966 (0.973), T3 95.3% (94.7%), T4 98.5% (95.9%), T5 1.04, T6 holds: see_friend gap **0.0005** (318 rows), rest 0.0006 | no more than 0.02 below v2; T5 in 0.8–1.25 | **PASS** |
| KW | w = 2 declines, w = 0 forms, with A6's flags | | **PASS** |

**Ready to freeze? No.** The rule needs every check but K1 to pass. KO1 fails, and under A6 it fails on its mean as well as its interval. Nothing was changed to make it pass. No further run was needed: every preregistered check has a result.

## Did the fixes bite?

| Arm | Lives identical to A5 (pleasure to the last digit) | A6 − A5 in B (paired, 95%) |
|---|---|---|
| B | 94 of 120 | weeks together −0.005 [−0.011, +0.000]; formed 0; liberty +0.001; pleasure +0.0001; non-offsettable suffering −0.0004 [−0.0009, −0.0000] |
| P2 | 105 of 120 | |
| trial | 84 of 120 | |
| LAT | 95 of 120 | |

The friend fix bites only in long runs of visits to the same friend. In the H41 harness these are rare, and PT-R's see_friend gap was already small (0.0005 under A5, 0.0005 now). The return fix bites only when a member leaves a second time while holding a value from an earlier spell. Lived exits per B run went from 0.75 to 0.67 and lived readings from 1,592 to 1,552. Story 4's starved lone member (A4) never comes up under A5 or A6, because the lived outside option sends both members out at the trial's end. So the friend fix could not be checked against the life that found it, and KL2 still passes only trivially.

## The step-5 exit paths again (does the quiet path appear?)

Slice (b)'s classifier on the A6 rows (bar exits, primary windows; second windows in brackets):

| Version: arm | Exits | Suffering | Quiet | Mixed | No fall | Short spell |
|---|---|---|---|---|---|---|
| A5: B | 90 | 54 | **1** (1) | 6 | 15 | 14 |
| A6: B | 80 | 48 (44) | **1** (1) | 4 (5) | 15 (18) | 12 |
| A5: P2 | 74 | 44 | **0** (1) | 2 | 12 | 16 |
| A6: P2 | 68 | 42 (38) | **0** (1) | 2 (2) | 14 (17) | 10 |
| A5: trial | 156 | 58 | **1** (3) | 4 | 10 | 83 |
| A6: trial | 145 | 45 (40) | **1** (1) | 2 (5) | 8 (10) | 89 |

**No: the quiet path does not appear.** Across B, P2 and trial there are 2 of 293 exits on the primary windows and 3 on the second. In this model people still leave when suffering rises. The prereg expected this, because A5 traced the cause to the saturating pleasure scale (weekly pleasure sits near 0.96 and has little room to fade), not to either bug. It stays a gap (see "New gaps").

## Forecast against lived leaving (lv-same; not a target)

Share of reading status quos whose forecast had a member leave, against the lived world:

| Arm | Within 13 weeks: forecast / lived | Within 52 weeks: forecast / lived |
|---|---|---|
| B, A5 | 28.6% / 9.4% | 42.0% / 22.3% |
| **B, A6** | **27.9% / 8.1%** | **41.8% / 21.5%** |
| P1, A6 | 20.3% / 8.6% | 32.8% / 20.1% |
| trial, A6 | 12.7% / 11.6% | 28.9% / 23.0% |
| prenup, A6 | 28.4% / 9.3% | 41.7% / 22.5% |

Unchanged in substance. Forecasts still leave about twice as often as lived agents at 52 weeks in B (gap 0.20; the prereg calls anything over 0.10 a weakness). The cause is A5's in-future look-back: it judges staying on the last 13 future weeks, while a lived reading forecasts 52 weeks ahead. Neither fix touches it.

Rethink episodes in B: 91, of which 38 ended in leaving, 35 came back and 18 were still open at the end (A5: 96, 41, 38, 17). Lone weeks in B: 3.5% of weeks; no stretch over 26 weeks in serious suffering (longest 4 weeks); 80 lone readings, 11 lone leaves, 16 re-formations.

## The outside forecast (KO1) and its tail

| Version (B) | Bar exits | Mean L − O | Mean abs error | Worst | Share below −0.2 |
|---|---|---|---|---|---|
| old | 48 | +0.014 | 0.109 | −0.96 | 0.06 |
| A4 | 54 | +0.044 | 0.094 | −0.81 | 0.02 |
| A5 | 79 | +0.016 [−0.010, +0.044] | 0.076 | −0.31 | 0.05 |
| **A6** | 73 | **+0.027 [+0.004, +0.048]** | **0.069** | **−0.21** | 0.03 |
| A6, P2 | 58 | +0.038 [+0.011, +0.067] | | | |
| A6, trial | 60 | +0.023 [−0.008, +0.053] | | | |

Fixing the stale return removed the outside futures' error in one direction: a counterfactual leaver could no longer walk back in on an old value, while lived leavers could. What is left points the other way. Lived leavers do somewhat better than the forecast says. Two reasons, both known stand-ins and both untouched:

- A lived leaver re-forms (16 re-formations in B), while an outside future never does.
- A lived leaver returns on a fresh reading (story 2 below), while an outside future holds no readings.

So the remaining KO1 miss is the stand-in's known error, not a bug of the kind fixed here. It is not fitted away.

## H41 under A6, beside old, A4 and A5

**Per arm, old > A4 > A5 > A6** (means over 120 pairings):

| Arm | Weeks together | Formed at week 0 | Held (H38 lens) | Liberty | Pleasure | Lived |
|---|---|---|---|---|---|---|
| B | 0.841 > 0.865 > 0.891 > **0.886** | 0.75 > 0.82 > 0.80 > **0.80** | 0 | 2.094 > 2.000 > 2.016 > 2.017 | 0.9624 > 0.9640 > 0.9634 > 0.9635 | same as pleasure |
| P0.5 | 0.863 > 0.898 > 0.901 > 0.895 | 0.78 > 0.85 > 0.83 > 0.83 | 0.027 > 0.035 > 0.042 > 0.043 | 2.074 > 1.957 > 1.988 > 1.998 | 0.9637 > 0.9653 > 0.9645 > 0.9645 | 0.9629 > 0.9643 > 0.9636 > 0.9636 |
| P1 | 0.876 > 0.923 > 0.903 > 0.898 | 0.82 > 0.87 > 0.86 > 0.86 | 0.058 > 0.071 > 0.066 > 0.062 | 2.014 > 1.937 > 1.987 > 1.998 | 0.9649 > 0.9671 > 0.9660 > 0.9660 | 0.9633 > 0.9649 > 0.9641 > 0.9642 |
| P2 | 0.901 > 0.933 > 0.914 > 0.910 | 0.87 > 0.89 > 0.90 > 0.89 | 0.084 > 0.087 > 0.086 > 0.086 | 1.968 > 1.922 > 1.932 > 1.938 | 0.9670 > 0.9690 > 0.9681 > 0.9678 | 0.9634 > 0.9646 > 0.9644 > 0.9642 |
| P4 | 0.903 > 0.945 > 0.922 > 0.924 | 0.89 > 0.91 > 0.91 > 0.91 | 0.092 > 0.099 > 0.093 > 0.098 | 1.976 > 1.922 > 1.941 > 1.938 | 0.9687 > 0.9713 > 0.9697 > 0.9698 | 0.9622 > 0.9623 > 0.9624 > 0.9624 |
| trial | 0.844 > 0.856 > 0.840 > 0.836 | 0.74 (all four) | 0 | 2.073 > 2.085 > 2.105 > 2.117 | 0.9633 > 0.9644 > 0.9642 > 0.9643 | same |
| cheap | identical to B in every version | | | | | |
| prenup | 0.841 > 0.869 > 0.893 > 0.888 | 0.75 > 0.82 > 0.81 > 0.81 | 0 | 2.095 > 1.962 > 2.014 > 2.015 | 0.9622 > 0.9640 > 0.9634 > 0.9637 | same |
| info | 0.843 > 0.884 > 0.898 > 0.897 | 0.77 > 0.82 > 0.86 > 0.85 | 0 | 2.085 > 1.984 > 1.963 > 1.978 | 0.9622 > 0.9637 > 0.9634 > 0.9635 | same |
| lat | 0.706 > 0.727 > 0.769 > 0.758 | 0.58 > 0.59 > 0.58 > 0.58 | 0 | 2.330 > 2.286 > 2.293 > 2.299 | 0.9610 > 0.9623 > 0.9624 > 0.9625 | same |
| all | 0.606 > 0.625 > 0.619 > 0.616 | 0.51 (all four) | 0 | 2.429 > 2.423 > 2.439 > 2.440 | 0.9597 > 0.9609 > 0.9607 > 0.9608 | same |

**Each arm against B under A6** (H41's classes; margins: weeks together and formation 0.01, held 0.005, liberty 0.02, pleasure 0.003):

| Aid / level | Weeks together | Formed at week 0 | Held | Liberty | Pleasure | Lived | Worse-off | H41 |
|---|---|---|---|---|---|---|---|---|
| P0.5 | +0.009 0 | **+0.033 +** | **+0.043 +** | −0.020 0 | +0.0010 0 | +0.0001 0 | 0 | (pressure) |
| P1 | +0.012 0 | **+0.058 +** | **+0.062 +** | −0.020 0 | +0.0025 0 | +0.0007 0 | **+** | (pressure) |
| P2 | +0.024 [−0.010, +0.056] 0 | **+0.092 +** | **+0.086 +** | **−0.080 −** | **+0.0043 +** | +0.0007 0 | **+** | (pressure) |
| P4 | **+0.038 [+0.000, +0.075] +** | **+0.108 +** | **+0.098 +** | **−0.079 −** | **+0.0063 +** | −0.0011 0 | **+** | (pressure) |
| trial | **−0.050 −** | −0.058 0 | 0 | **+0.099 +** | +0.0008 0 | +0.0008 0 | 0 | not supported |
| cheap | 0 (identical) | 0 | 0 | 0 | 0 | 0 | 0 | not supported |
| prenup | +0.002 0 | +0.008 0 | 0 | −0.003 0 | 0 | 0 | 0 | not supported |
| info | +0.010 0 | +0.050 [0.000, +0.100] 0 | 0 | −0.039 0 | 0 | 0 | 0 | not supported |
| lat | **−0.128 −** | **−0.225 −** | 0 | **+0.282 +** | −0.0010 0 | −0.0010 0 | 0 | not supported |
| all | **−0.270 −** | **−0.292 −** | 0 | **+0.423 +** | −0.0027 0 | −0.0027 0 | 0 | not supported |

**H41 under A6: not supported** (no aid raises weeks together). Judging pleasure AND freedom together, no aid is a win:

- LAT and all aids buy liberty with weeks together at a small pleasure cost inside the margin: a trade-off.
- The trial raises liberty, lowers weeks together and leaves pleasure flat.
- Better information no longer moves anything beyond the margins.
- Pressure P2 and P4 raise pleasure while holding people in and narrowing liberty: a trade-off, as under every version. Lived pleasure is flat, so the gain is the reward paid.

**Four versions, stop rule.** These hold across all four versions (old, A4, A5, A6):

- Pressure holds people in at every level (held +).
- P2 and P4 raise pleasure.
- LAT and all aids lower weeks together and formation and raise liberty.
- The prenup and cheap housing change nothing.
- H41 is not supported.

**Version-dependent** (not patched; classes in the order old, A4, A5, A6):

- **Pressure raises weeks together**: P0.5, P1, P2 +, +, 0, 0; P4 +, +, 0, **+** (the interval's low end is +0.0002, so it is barely + under A6).
- Formation at week 0 under pressure: P0.5 0, +, +, +; P1 +, 0, +, +.
- Liberty under pressure: P0.5 0, −, 0, 0; P1 −, −, 0, 0; P4 −, 0, 0, −.
- Pleasure at P1: 0, +, 0, 0.
- The trial: weeks together 0, 0, −, −; formed 0, −, 0, 0; liberty 0, +, +, +; non-offsettable suffering 0, +, 0, +.
- Better information: weeks together 0, +, 0, 0; formed 0, 0, +, 0; liberty 0, 0, −, 0; non-offsettable suffering 0, 0, 0, +.
- All aids: pleasure, lived and worse-off 0, −, 0, 0.
- The prenup's liberty: 0, −, 0, 0.
- LAT's non-offsettable suffering: 0, +, +, +.

A5 and A6 agree on every class except P4's weeks together and liberty, better information's formation, liberty and non-offsettable suffering, and the trial's non-offsettable suffering. Each of these sits at a margin's edge.

## The author's prediction (P-AUTH): does knowing you could leave later make people more willing to try living together?

B arm, exit option in forecasts against without it, 120 pairings, paired:

| Version | Formed at week 0 | Weeks together | P-AUTH |
|---|---|---|---|
| A4 (no lock-in, solo outside) | +0.067 [+0.025, +0.117] (+) | +0.012 [+0.002, +0.024] (+) | missed |
| A5 | +0.050 [0.000, +0.100] (0) | +0.047 [+0.017, +0.088] (+) | held |
| **A6** | **+0.050 [0.000, +0.100] (0)** | **+0.053 [+0.021, +0.094] (+)** | **held** |

**The prediction holds for moving in, as preregistered.** The formation gain does not clear its margin with an interval clear of 0. The result is DESCRIPTIVE: the power check resolves only about 0.065 and up, and the point estimate leans toward "a little". **For time together it does not hold**: with the exit option, pairs spend more weeks together, because more form and those who leave re-form more. In this model lock-in takes some of the option value of exit at formation, not all of it. The agent has no sunk-cost reasoning, so this says nothing about sunk cost.

## Story check (four lives, A6)

1. **Story 4 (trial, p-peacekeeper with p-wanderer).** As under A5, both leave at the trial's end (week 78) and nobody is ever alone. Matches, but it means the friend fix's target life never arises under A5 or A6.
2. **B, p-anchor with p-steward (a lived exit and a fresh return).** A leaves at week 84 on the bar with a flat yardstick (class "no fall": the outside option rose). B, alone, holds a lone reading and a return reading at week 91. A returns on that new valuation and both live better afterwards (L − O +0.13). This is the fresh-return rule working as written: the return comes from a reading made in this out-spell, not from an old value. It is also why the forecast is pessimistic about leaving: the outside futures cannot return.
3. **B, g-10000 with g-10010 (the worst miss).** A's suffering rises around week 52 and again from week 78 (0.29 to 0.42). Its tally calls rethinks at weeks 60, 64 and 95, and it leaves at 95. After leaving it lives worse than forecast (L 0.42 against O 0.62). It returns at about week 117 and leaves again at 137 into suffering of 0.55 to 0.72 (L − O −0.21). Matches the measures: the worst tail misses are optimistic outside forecasts for a member whose suffering follows it out. This is the kind of hard life after leaving the author chose to keep (gap-after).
4. **P2, p-bargainer with p-wanderer (pressure with lock-in).** A leaves at 34 and returns at 39 after a fresh return reading. B suffers 0.3 to 0.45 a week for about 110 weeks with its tally near −0.3. It rethinks every 4 weeks and never leaves: each fresh forecast says staying with the reward beats leaving. Same as under A5: it matches "pressure holds people in", and the mismatch named then still stands (monthly rethinks with nothing changing).

## Expectations written before the run

| ID | Expected | Actual | |
|---|---|---|---|
| F1 | the friend fix moves units from visits to rest in same-friend streaks and lowers non-offsettable suffering a little | B non-offsettable suffering −0.0004 [−0.0009, −0.0000]; 94 of 120 B lives unchanged | holds, weakly |
| F2 | fewer immediate re-entries; lived exits last longer | exits per B run 0.75 → 0.67; no immediate re-entry was measured directly | not measured as stated (indirect only) |
| F3 | KO1's tail does not grow | worst −0.31 → −0.21; share below −0.2 0.05 → 0.03 | holds |
| F4 | pressure still holds people in | held + at every level | holds |
| (measures) | quiet path still rare; forecast/lived gap stays | 1 of 80 in B; 41.8% vs 21.5% | holds |

## New gaps

- **KO1 is now a stand-in error, not a bug.** With both bugs fixed, the outside forecast is somewhat pessimistic about leaving (+0.027). Outside futures never re-form or return, while lived leavers do. Fixing that would mean holding readings and retries inside outside futures: a design change, not a bug fix, and the author's call.
- **The quiet path is still absent** (2 of 293 exits). Not caused by either bug.
- **The in-future look-back still leaves too often** (52-week gap 0.20).
- **The friend fix's own story could not be checked.** The life that showed the bug (story 4 under A4) no longer arises, and in H41's harness the fix changes few lives. It is tested by its unit check only.
- **Monthly rethinks under pressure lead nowhere** (story 4 of the check): a held member can rethink 25 times in two years with nothing changing. This matches the model's rule. Whether that is true to life is open.

## Can be about / cannot be about

This can be about whether the hybrid, with the friend-visit and stale-return bugs fixed, passes A5's known-answer checks, and how H41's arms and the exit-option prediction move under it beside three earlier versions, in the formation check's two-person household. It cannot be about people, friendship or habituation in real life, how people time their exits, sunk cost, or the many-agent world.

## Reproduction

`zsh runs/hybrid-a6/queue.sh` (KX2, story, K1, PT-H, PT-R, H41 B, B without the exit option, all arms, analysis). `uv run python scripts/hybrid_leaving.py --analyze --version a6`; `--life ARM A B --version a6`. Tests: `uv run pytest tests/test_hybrid_a6.py`; pins `uv run pytest -m slow`.
