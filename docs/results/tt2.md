# TT2: gifts between partners living apart, and q = 0.3

Wording rule: agents feel nothing; "pleasure", "suffering", "gift", "value", "forecast" and "held" are glosses for modeled numbers.

**Model line (TT2):** `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit · hybrid_tally=level · tally_half=13 · tally_line=0.02 · exit_grow=0.04 · hybrid_outside=lived · friend_satiety · fresh_return · together_bg=3.3 · lat_bg_keep=0.2 · lat_travel=0.33 · together_subst · lat_gifts`, exit fallback F4 with items (F5 in the prenup and all-aids arms), corrected rule (ADR 0020). Compared with TT (`together_bg=1.1`, no `lat_gifts`) and A6.

Preregistration: [tt2-prereg.md](tt2-prereg.md) (commit a590462, before any code; Amendment 1 after the screening run, before the confirming run). Code 6ab161f. Confirming run 2026-11-16, 10:05 to 19:57 (9.9 h wall), scripted agents, no model calls, at most 6 workers under `caffeinate -s`, longest arms first. Rows in runs/tt2/ (queue.sh, status.log, analysis.json); LAT attribution in runs/lat-suffering/tt2.json and tt2_q01.json; PT-H and PT-R in runs/hybrid-passtest-tt2/ and runs/value-consistency-hybrid-world-tt2/; K1 in runs/hybrid-fix/trap-tt2.json.

## In one paragraph

**At q = 0.3 nobody in the 1,320 TT2 lives gives a gift.** The larger background value pulls almost every pair into a household (B forms 0.99 at week 0; LAT chosen by 15 of 120, was 24), and the few LAT members who go broke have a partner the gift rule does not let give (prosocial 0.41, under the rule's 0.5). LAT's extra non-offsettable suffering falls to **+0.00004 [0.00000, +0.00012]** (TT +0.00033), and that is q's doing, not gifts'. Gifts alone, at TT's q (C2), happen in 1 LAT-arm life and 5 all-aids lives; they cut LAT's extra suffering from +0.00033 to +0.00013 (paired −0.0002 [−0.0006, 0.0000]) and change nothing else that can be told from 0. Every gift-free life is TT's life exactly (KG4). **LAT is still a trade-off** of weeks together for freedom at a small pleasure cost (weeks together −0.019, liberty +0.116, pleasure −0.0003 [−0.0006, −0.0001]); this holds at every q from 0.05 to 0.6 and under A6, TT and TT2. H41 is still not supported. **Three checks fail: PT-R (T3 0.869, worse than TT's 0.898; v2 0.947), K1 (trap 0.069, bar 0.10) and KO1 (+0.055, worse than TT's +0.037).** So TT2 is not usable as the time-together version and the hybrid is not ready to freeze.

## How a gift is decided (the prereg's design, as built)

A LAT member may hand its partner 3 money units by the model's existing `give` action. It is on the member's menu only under the seed v2 gift policy: the member's prosocial value is at least 0.5, the partner holds under 4, the member holds at least 8. The hybrid then values the gift by its usual one-week fork (own net plus the prosocial share of the partner's) and gives only if that beats the action floor and ranks first. The flag opens two gates under LAT only (feasibility and the proposal); amount, thresholds and yardstick are the existing ones. Forecasts make no forks, so no choice anticipates a gift.

## Screening run (EXPLORATORY; bug checks only)

The pilot sample (10 pairings, seed 900; B, LAT, all aids; 30 lives) ran without error. **No gift was given**, so a targeted check was added (Amendment 1): in one lived LAT life where TT's rows showed a broke member beside a prosocial partner, gifts fire (4, weeks 46 to 51) under q = 0.1 and none under TT. The gifts-off twin of the pilot matched it on every week-0 term (30 of 30) and every outcome (30 of 30). No bug was found; nothing in the design changed. No screening outcome is reported.

## Known-answer checks

| ID | Result | Bar | |
|---|---|---|---|
| PIN | 50 slow pins byte for byte with `lat_gifts` off (runs/tt2/pins.log, 11 min); fast suite 991 passed (runs/tt2/fast.log) | byte for byte | **PASS** |
| KG1, KG2, KG3 | gift feasible and proposed only under LAT with the flag, by the seed v2 policy; moves exactly 3, money conserved; not for a member with prosocial < 0.5; not when apart-not-LAT; households unchanged; a LAT world's forecast is equal exactly with the flag on and off (tests/test_tt2_gifts.py) | | **PASS** |
| KG4 | C2 against TT: week-0 term equal in 360 of 360 lives; all 354 gift-free lives have TT's outcomes exactly | exact | **PASS** |
| KW | w = 2 declines, w = 0 forms, TT2 flags | | **PASS** |
| KB1, KB2, KT1, KS1, KF1, KR1, KT0–KT2, KC1, KO0, KL1, KX0, KX1 | in the fast suite with their flags as written | | **PASS** |
| KX2 | DiD **+0.0043 [+0.0025, +0.0061]**; clauses i–iii hold; 35 of 48 futures with an exit each way, first at about week 26 (runs/tt2/kx2-tt2.json). TT +0.0079, A6 +0.020 | DiD > 0, interval above 0 | **PASS** |
| KL2 | story 4: no stuck stretch (runs/tt2/story-tt2.json) | ≤ 26 weeks | **PASS** |
| PT-H | H1 **+0.0032** [+0.0007, +0.0063]; H2 **0.947** (1,178 option-units); H3 **95.2%** (477); 565 choice-units | ±0.010 (interval inside ±0.015); ≥ 0.80; ≥ 80% | **PASS** |
| PT-R | T1 0.970 (v2 0.955), T2 0.973 (0.973), **T3 0.869 (0.947)**, T4 0.966 (0.959), T5 1.08; T6 holds (see_friend gap 0.0002, rest 0.0002; together 96 rows, no bar) | each no more than 0.02 below v2 | **FAIL** (T3, by 0.078; TT missed by 0.049) |
| K1 | trap **0.069** (332 staying weeks), baseline 0.000 (527). A6 0.128; not run under TT | ≥ 0.10 / ≤ 0.02 | **FAIL** |
| KO1 | **+0.055 [+0.033, +0.085]**, 68 bar exits in B (TT +0.037, A6 +0.027) | mean within ±0.02, interval inside ±0.04 | **FAIL** (worse) |

**Usable / ready to freeze? No.** PT-R and K1 fail; KO1 fails by more than before. Nothing was changed to make any pass. PT-H and PT-R's samples (the formation-check pairing harness) have no LAT, so they test q only.

**PT-R T3, as expected, still fails and is worse.** The routine's best-action share falls as q rises (A6 0.953, TT 0.898, TT2 0.869). That fits the hypothesis in time-together.md (background time enters the world's close and the routine sees it through its projection), but it is not diagnosed here; that is the next task.

**K1 is a new failure.** The trap's held share was a thin pass under A5 and A6 (0.128, three pairings). With households worth more, fewer staying weeks in the trap read as held. Not diagnosed.

**KO1 widens again.** Outside futures have no partner and so no background time; at q = 0.3 the gap between a forecast of leaving and the life lived after leaving (where most leavers re-form) is larger.

## TT, TT2 side by side (per arm, means over 120 pairings)

| Arm | Weeks together A6 → TT → TT2 | Formed at week 0 | Liberty | Pleasure | Non-offsettable suffering | LAT weeks |
|---|---|---|---|---|---|---|
| B | 0.886 → 0.929 → **0.942** | 0.80 → 0.95 → **0.99** | 2.017 → 1.907 → **1.837** | 0.9635 → 0.9765 → **0.9870** | 0.0010 → 0.0007 → 0.0006 | 0 |
| lat | 0.758 → 0.876 → **0.924** | 0.575 → 0.767 → **0.867** | 2.299 → 2.075 → **1.953** | 0.9625 → 0.9754 → **0.9867** | 0.0018 → 0.0011 → **0.0006** | 0.148 → 0.053 → **0.020** |
| all | 0.616 → 0.781 → **0.886** | 0.508 → 0.750 → **0.883** | 2.440 → 2.163 → **1.977** | 0.9608 → 0.9733 → **0.9849** | 0.0033 → 0.0022 → **0.0016** | 0.257 → 0.110 → **0.022** |

TT2 − TT, paired: pleasure **+0.008 to +0.012 in every arm** (intervals clear of 0); liberty lower in every arm (−0.011 to −0.186), with intervals below 0 in B, cheap, P0.5, prenup, LAT and all aids and spanning 0 in P1, P2, P4, trial and info. B forms more (+0.042 [+0.008, +0.083]). The same level shift TT found, larger.

**Gifts alone and q alone** (paired; C2 = q 0.1 with gifts):

| | Arm | Weeks together | Liberty | Pleasure | Suffering |
|---|---|---|---|---|---|
| gifts alone (C2 − TT) | B | 0 | 0 | 0 | 0 (identical lives) |
| | lat | +0.0014 [0, +0.0042] | +0.0015 [0, +0.0045] | +0.00006 [0, +0.00019] | **−0.0002 [−0.0006, 0.0000]** |
| | all | +0.0007 [0, +0.0021] | +0.012 [0, +0.034] | +0.00001 | −0.0002 [−0.0006, 0.0000] |
| q alone (TT2 − C2) | B | +0.014 [−0.001, +0.028] | −0.070 [−0.124, −0.020] | +0.0105 | −0.0001 |
| | lat | +0.046 [+0.018, +0.076] | −0.124 [−0.200, −0.056] | +0.0112 | −0.0002 |
| | all | +0.104 [+0.054, +0.157] | −0.198 [−0.300, −0.104] | +0.0116 | −0.0004 [−0.0009, −0.0001] |

**Almost everything TT2 changes is q.** Gifts touch a handful of lives.

## LAT: suffering, pleasure, liberty

**LAT against B** (pairing bootstrap):

| | Weeks together | Formed | Liberty | Pleasure | Suffering | LAT at week 0 | Verdict |
|---|---|---|---|---|---|---|---|
| A6 | −0.128 − | −0.225 − | +0.282 + | −0.0010 [−0.0018, −0.0003] | +0.0008 + | 46 | trade-off |
| TT | −0.053 − | −0.183 − | +0.169 + | −0.0011 [−0.0018, −0.0005] | +0.0003 0 | 24 | trade-off |
| C2 (q 0.1 + gifts) | −0.051 − | −0.183 − | +0.170 + | −0.0010 | +0.0001 0 | 24 | trade-off |
| **TT2** | **−0.019 [−0.031, −0.010] −** | **−0.125 −** | **+0.116 [+0.065, +0.176] +** | **−0.0003 [−0.0006, −0.0001]** | **+0.00004 [0, +0.00012] 0** | **15** | **trade-off** |

**Where LAT's extra suffering went** (attribution, LAT − B per member-week, by mode):

| | Total | LAT weeks | Apart, not LAT | Household | Pairings |
|---|---|---|---|---|---|
| A6 | +0.00079 | +0.00029 | +0.00048 | 0 | 6 |
| TT | +0.00033 | +0.00011 | +0.00019 | +0.00004 | 2 |
| C2 (gifts, q 0.1) | +0.00013 | +0.00007 | +0.00003 | +0.00004 | 2 |
| TT2 | +0.00004 | +0.00004 | 0 | 0 | 1 |

Every remaining unit is still denied money. In C2, all 4 LAT-arm gifts were given in LAT weeks (none elsewhere). Under TT2 the one remaining pairing (g-00111 with g-10110) has member A at money 0 for 5 jobless LAT weeks (78 to 82) while B holds 52 to 56, and B never gives: **B's prosocial value is 0.41, under the gift rule's 0.5.** So the last of LAT's money suffering is the gift rule's prosocial gate, not the absence of a channel.

**Story (the gift life, C2's LAT arm, g-00000 with g-11110).** Under TT, B loses its job, runs to money 0 at week 47 while LAT, and stays there through the end of LAT (week 52) and 9 more weeks apart: 12 weeks of denied money. Under C2, A (prosocial 0.8, holding about 190) gives 3 in weeks 46, 48, 49 and 51, which keeps B at 2 to 4 through LAT. At week 52 the pair stops being LAT (a reading), gifts stop, and B hits 0 at week 53: 7 weeks denied instead of 12. The measure matches the story: gifts end suffering only while the pair is LAT, and the gift is small (3 a time, only while the partner holds under 4).

## H41 under TT2

**Not supported** (no aid raises weeks together). LAT and all aids are trade-offs (liberty up, pleasure interval below 0). All aids against B: weeks together −0.057, liberty +0.140 [+0.069, +0.222], pleasure −0.0021 [−0.0034, −0.0009] (class 0 at H41's margin; TT −0.0032, class −), suffering +0.0010 [+0.0003, +0.0017].

**Stop rule, sign classes against B (A6 → TT → TT2).** The same under all three:
- pressure holds people in (held + at P0.5, P1, P2, P4);
- the trial lowers weeks together and raises liberty;
- LAT and all aids lower weeks together and formation and raise liberty; LAT's pleasure 0;
- cheap housing changes nothing;
- H41 not supported.

**Version-dependent, TT → TT2 (not patched):**
- P1: liberty 0 → + (+0.038 [+0.013, +0.072]); held stays +, so freedom's two measures now disagree for P1. Not a win.
- P2: weeks together + → 0; liberty − → 0; worse-off partner + → 0.
- P4: pleasure + → 0; liberty − → 0; suffering 0 → − (−0.0004).
- Better information: weeks together + → 0.
- The trial: suffering + → 0.
- All aids: pleasure − → 0 (still below 0 in interval), lived pleasure − → 0.
- LAT's suffering: + (A6) → 0 (TT) → 0 (TT2).

## The predictions

| ID | Expected | Actual | |
|---|---|---|---|
| G1 | gifts in C1's and C2's LAT arms; only in LAT weeks | C2: 1 LAT-arm life (4 gifts), 5 all-aids lives (16); **C1 (TT2): none in 1,320 lives**; every recorded gift in a LAT week | **misses** (C1) / property holds |
| G2 | gifts alone cut LAT's extra suffering in LAT weeks; total falls, need not reach 0 | LAT weeks +0.00011 → +0.00007; total +0.00033 → +0.00013; paired −0.0002 [−0.0006, 0.0000]. The apart part fell too (+0.00019 → +0.00003), through a changed later path | holds (direction) |
| G3 | TT2: LAT − B suffering class 0, at or below TT's; the rest in apart-not-LAT or household weeks | +0.00004 [0, +0.00012], class 0; the rest is **in LAT weeks** (a non-giving partner, prosocial 0.41) | first clause holds; second **misses** |
| G4 | gifts do not change week-0 choices | KG4 PASS | holds |
| Q1 | fewer or as many choose LAT; LAT weeks ≤ 0.053 | 24 → 15; 0.053 → 0.020 | holds |
| Q2 | B forms at least as often; pleasure + and liberty − in every arm | 0.95 → 0.99; pleasure + everywhere; liberty lower everywhere but class − only in 6 of 11 arms | holds on point estimates; liberty class misses in 5 arms |
| L1 | LAT vs B: liberty +, pleasure 0 or −, weeks together − or 0 | +0.116, −0.0003 (0), −0.019 (−) | holds |
| L2 | LAT: trade-off | trade-off | holds |
| L3 | all aids: trade-off with a pleasure cost | trade-off; pleasure interval below 0 but class 0 at H41's margin | holds by the verdict rule; H41 class moved |
| H | H41 not supported | not supported | holds |
| S | q sweep: sizes shrink with q; signs keep | below | mostly; not monotone at 0.6 |

## q sweep (gifts on; B and LAT; 120 pairings each; descriptive)

| q (`together_bg`) | LAT − B weeks together | Liberty | Pleasure | Suffering | LAT at week 0 | LAT weeks | B formed at week 0 | Gifts (LAT arm) |
|---|---|---|---|---|---|---|---|---|
| 0.05 (0.55) | −0.083 − | +0.214 + | −0.0012 0 | +0.0003 0 | 30 | 0.082 | 0.89 | 10 in 4 lives |
| 0.1 (1.1) | −0.051 − | +0.170 + | −0.0010 0 | +0.0001 0 | 24 | 0.051 | 0.95 | 4 in 1 life |
| **0.3 (3.3)** | **−0.019 −** | **+0.116 +** | **−0.0003 0** | **0.0000 0** | **15** | **0.020** | **0.99** | **0** |
| 0.6 (6.6) | −0.025 − | +0.131 + | −0.0003 0 | 0.0000 0 | 18 | 0.028 | 1.00 | 3 in 1 life |

**No sign class changes across q** for LAT's weeks together, liberty, pleasure or suffering, and the verdict is a trade-off at every q. Sizes fall from 0.05 to 0.3 and turn back slightly at 0.6 (B already forms 100%, and a few more pairs pick LAT). Gifts fire mostly where LAT is common (low q).

## ADR 0020 labels for the findings touched

| Finding | Label after TT2 |
|---|---|
| LAT is a trade-off (weeks together −, liberty +, pleasure 0 with interval below 0) | **holds across versions** (A6, TT, TT2; every q 0.05–0.6) |
| LAT's extra non-offsettable suffering | **version-dependent** (A6 +, TT 0, TT2 0) |
| LAT's extra suffering is denied money, not missing the partner or two rents | **holds across versions** (A6, TT, TT2) |
| Gifts between LAT partners cut LAT's money suffering | **single-version** (C2 only; too few gifts at q = 0.3 to show anything) |
| Pressure holds people in | **holds across versions** |
| H41 not supported | **holds across versions** |
| All aids costs pleasure | **version-dependent** (H41 class: A6 0, TT −, TT2 0; the interval is below 0 in all three) |
| P1 liberty, P2 weeks together and liberty, P4 pleasure, info weeks together, the trial's suffering | **version-dependent** (TT → TT2) |
| Background time is a level shift (pleasure up, liberty down, more formation) | **holds across versions** (TT, TT2), larger at q = 0.3 |

## New gaps

- **The gift rule's prosocial gate leaves the last of LAT's money suffering.** The seed v2 policy lets only members with prosocial ≥ 0.5 propose a gift; half the personas never can. That is an existing ASSUMED rule reused unchanged. Whether a less prosocial partner should be able to give, valued by the fork alone, is the author's question.
- **Apart-not-LAT pairs get no gifts** by design (the author's words were "LAT partners").
- **Forecasts do not see gifts**, so gifts cannot make LAT more attractive at a choice.
- **PT-R T3 worsens as q rises; K1 now fails; KO1 widens.** All three point to households being worth more than the routine's projection, the trap reading and the outside futures see. Not diagnosed.
- **At q = 0.3 almost everyone forms** (B 0.99), so H41's aids have little to act on. Any H41 statement under TT2 is a statement about a near-ceiling world.
- **The story check of TT** is still owed; one gift story is told above.

## Can be about / cannot be about

This can be about how H41's LAT result, its suffering and the hybrid's checks move when LAT partners can hand each other money by the model's existing gift rule and a background hour is valued at the sourced 0.3 of a planned one. It cannot be about real couples, their money, job loss, the value of time with a partner, or the many-agent world. Limits 1, 4, 5, 6, 10, 11, 12 and 13 apply.

## Reproduction

`caffeinate -s zsh runs/tt2/queue.sh` (about 10 h on 6 workers). `uv run python scripts/tt2.py --analyze`; `uv run python scripts/lat_suffering.py --analyze --version tt2` (and `tt2_q01`); `uv run python scripts/hybrid_passtest.py --tt2 --analyze`. Screening: `uv run python scripts/hybrid_leaving.py --run tt2_screen,tt2_screen_off --arms all,lat,B`, then `scripts/tt2.py --screen`. Tests: `uv run pytest tests/test_tt2_gifts.py`; pins `uv run pytest -m slow`.
