# Hybrid fixes: the member left alone, and forecasts with the option to leave

Wording rule: agents feel nothing; "pleasure", "suffering", "value", "forecast" and "held" are glosses for modeled numbers.

Model: `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit`, exit fallback F4 with items (F5 in the prenup arms), corrected rule (ADR 0020). The version before: the same without the last two flags (H41's).

Status: run on 2026-11-13 after the preregistration ([hybrid-exit-option-prereg.md](hybrid-exit-option-prereg.md), commit 5d5b4f1; code ac90cc5; free checks noted in the prereg at dd454d4, before the confirmatory run). Scripted agents, no model calls, every number ASSUMED. H41 rerun: 1,320 runs (11 arms × 120 pairings × seed 0), 11,542 s on 4 workers under `caffeinate -i`; the old version rerun on B, trial and all (360 runs) and each fix alone (480 runs) beside it. Rows in runs/h41-exit-option/. Label for H41 under ADR 0020: two versions now, see "Old against new".

## In one paragraph

**Both fixes do what they say, and the hybrid is still not ready to freeze.** The member left alone now gets the pair's reading and can leave: story 4's member leaves 24 weeks after its partner instead of staying 78, no run in any arm has a lone stretch over 26 weeks in serious suffering (old trial arm: two runs, up to 59 weeks), and emptied households re-form at retries. Forecasts now carry the option to leave, and it shows: pairs that never formed now form knowing one of them will leave at week 26, and do. The old checks still pass (pins byte for byte, PT-H, PT-R, KW), K1 fails as before, and **KX2, the exact model's known answer, fails**: in the trap fixture the cheaper exit did not raise the value of forming more with the exit option than without (DiD −0.011 [−0.069, +0.041]), because that fixture's cost falls on staying. **H41 stays not supported** under the new version. Its pressure finding holds across both versions (pressure raises weeks together and holds people in); several smaller signs are version-dependent, most visibly **all aids together is now harm** (pleasure −0.0031, interval below the margin's zero) and the trial now **lowers week-0 formation** against a B that forms more. One aid, better information, now raises weeks together (+0.019) and beats matched pressure, but raises no pleasure, so it is not a win. A new gap: story 4's member's suffering did not come from being stuck alone; it continues after it leaves.

## Known-answer checks

| ID | What | Result | Bar | |
|---|---|---|---|---|
| PIN | Old results reproduce with both flags off | all 50 slow pin tests pass (every fingerprint file) | byte for byte | **PASS** |
| KL1 | The lone reading runs where it says (unit) | 5 tests pass (tests/test_hybrid_lone.py) | | **PASS** |
| KL2 | Story 4 | identical to H41's life to week 78; the member left alone holds lone readings at weeks 91 and 102 and leaves at 102 (24 weeks alone, was 78) | no stuck stretch over 26 weeks | **PASS** |
| KX0 | No future self would leave: forecasts equal the flag off (unit) | equal exactly | | **PASS** |
| KX1 | Every future self would leave: it leaves at the second in-future reading (unit) | leaves at w + 26; future plays all 52 weeks | | **PASS** |
| KX2 | The exact model's answer: a cheaper exit raises the value of forming only with the exit option | DiD **−0.011** [−0.069, +0.041]; formation not lower with the cheap exit (0.08 vs 0.00); in-future exits in 48/48 trap and 45/48 baseline futures | DiD > 0, interval above 0 | **FAIL** |
| K1 | The trap's held share | trap **0.077**, baseline 0.000 (unchanged from Amendment 3) | ≥ 0.10 / ≤ 0.02 | **FAIL** (as before) |
| PT-H | Forecasts against 16 held-out futures (Amendment 1's sample, all four flags) | H1 **+0.0051** [+0.0022, +0.0083]; H2 **0.937** (1,032 option-units); H3 **93.2%** (426 units); 494 choice-units incl. 12 lone readings (+0.0071) | ±0.010 (interval in ±0.015); ≥ 0.80; ≥ 80% | **PASS** |
| PT-R | The routine at one week (40 lives) | T1 0.958, T2 0.974, T3 95.5%, T4 97.8%, T5 1.07, T6 holds; v2 same sample 0.955, 0.973, 94.7%, 95.9% | no more than 0.02 below v2; T5 in 0.8–1.25 | **PASS** |
| KW | The suffering weight's known answer, new flags on | w = 2 declines, w = 0 forms | | **PASS** |

**Ready to freeze? No.** The prereg's rule needs every check but K1 to pass; KX2 fails.

**Why KX2 fails.** In the stay test's fixtures the trap card (nothing may be carried out of the pot) costs a member mostly while it stays: the freedom probe lowers autonomy every week (D = V(baseline) − V(trap) is +0.326 with no exit option). With the exit option nearly every future exits in both fixtures at week 26, which cuts the trap's weekly cost short as much as it cuts the baseline's bad weeks, and the carry the trap denies is a few units of a small pot. So the fixture is not a pure exit cost, and the two choosers the exact model separates are not separated here (D with the option +0.315). The code does what the prereg says (traced: takes 0 against 50, exits at week 26). The prereg allows no change for this, and none was made. What it means: the exit option is in the forecasts and moves them, but this check could not show the exact model's signature, so "the hybrid now values exit as the exact model's optimal chooser does" is **not shown**.

**K1** fails as in Amendment 3: the hybrid can pay to leave the trap, so it is not held there. Each new flag alone: lone only, trap 0.049; exit only, trap 0.077; baseline 0 throughout (runs/hybrid-fix/trap-a4.json).

**PT-H** still passes with about the room Amendment 3 had (H1 +0.0058 then, +0.0051 now). Lone readings are calibrated like the rest (+0.007). PT-H compares the policy with itself on more futures; whether the in-future leave rule matches what lived agents do is the second measure below.

## H41 with both fixes: the table per arm, old > new

Means over 120 pairings, seed 0. Old: H41's rows (the version before). New: both fixes on.

| Arm | Weeks together | Formed at week 0 | Held (H38 lens) | Liberty | Pleasure | Lived | Non-offsettable suffering | Ended | Seconds a run |
|---|---|---|---|---|---|---|---|---|---|
| B | 0.841 > **0.865** | 0.75 > **0.82** | 0 > 0 | 2.094 > **2.000** | 0.9624 > 0.9640 | 0.9624 > 0.9640 | 0.0023 > 0.0020 | 0.08 > 0.13 | 20 > 18 |
| P0.5 | 0.863 > 0.898 | 0.78 > 0.85 | 0.027 > 0.035 | 2.074 > 1.957 | 0.9637 > 0.9653 | 0.9629 > 0.9643 | 0.0012 > 0.0010 | 0.08 > 0.13 | 31 > 33 |
| P1 | 0.876 > 0.923 | 0.82 > 0.87 | 0.058 > 0.071 | 2.014 > 1.937 | 0.9649 > 0.9671 | 0.9633 > 0.9649 | 0.0011 > 0.0012 | 0.09 > 0.10 | 31 > 38 |
| P2 | 0.901 > 0.933 | 0.87 > 0.89 | 0.084 > 0.087 | 1.968 > 1.922 | 0.9670 > 0.9690 | 0.9634 > 0.9646 | 0.0016 > 0.0010 | 0.06 > 0.08 | 39 > 35 |
| P4 | 0.903 > 0.945 | 0.89 > 0.91 | 0.092 > 0.099 | 1.976 > 1.922 | 0.9687 > 0.9713 | 0.9622 > 0.9623 | 0.0025 > 0.0009 | 0.08 > 0.05 | 40 > 32 |
| trial | 0.844 > 0.856 | 0.74 > 0.74 | 0 > 0 | 2.073 > 2.085 | 0.9633 > 0.9644 | 0.9633 > 0.9644 | 0.0041 > 0.0030 | 0.18 > 0.12 | 16 > 16 |
| cheap | 0.841 > 0.865 | 0.75 > 0.82 | 0 > 0 | 2.094 > 2.000 | 0.9624 > 0.9640 | 0.9624 > 0.9640 | 0.0023 > 0.0020 | 0.08 > 0.13 | 25 > 19 |
| prenup | 0.841 > 0.869 | 0.75 > 0.82 | 0 > 0 | 2.095 > 1.962 | 0.9622 > 0.9640 | 0.9622 > 0.9640 | 0.0025 > 0.0020 | 0.09 > 0.13 | 32 > 24 |
| info | 0.843 > 0.884 | 0.77 > 0.82 | 0 > 0 | 2.085 > 1.984 | 0.9622 > 0.9637 | 0.9622 > 0.9637 | 0.0039 > 0.0022 | 0.08 > 0.13 | 72 > 76 |
| lat | 0.706 > 0.727 | 0.58 > 0.59 | 0 > 0 | 2.330 > 2.286 | 0.9610 > 0.9623 | 0.9610 > 0.9623 | 0.0027 > 0.0029 | 0.08 > 0.12 | 22 > 19 |
| all | 0.606 > 0.625 | 0.51 > 0.51 | 0 > 0 | 2.429 > 2.423 | 0.9597 > 0.9609 | 0.9597 > 0.9609 | 0.0054 > 0.0048 | 0.09 > 0.04 | 71 > 76 |

**The version change itself, in B** (new minus old, paired by pairing, 95% bootstrap): weeks together +0.024 [+0.010, +0.041], formed at week 0 +0.067 [+0.025, +0.117], pleasure +0.0016 [+0.0006, +0.0029] (lived the same: no pressure), liberty −0.095 [−0.154, −0.044]. More households form and they narrow liberty (liberty is lower inside a household in this measure). Each fix alone in B: lone only, weeks together 0.853, formed 0.75, liberty unchanged (2.094); exit only, weeks together 0.828, formed 0.82, liberty 2.003, ended 0.19. So the formation gain and the liberty fall come from the exit option; the lone reading adds weeks together by re-forming emptied households.

**Reproduction.** The old version rerun with the new record on B, trial and all (360 runs) equals H41's rows on every recorded field: 0 differences.

## Each arm against B, and the verdicts (new version)

Classes as H41 classes them ("+"/"−": beyond the margin with the 95% pairing-bootstrap interval clear of 0; margins: weeks together and formation 0.01, held 0.005, liberty 0.02, pleasure and lived 0.003).

| Aid | Weeks together | Held | Liberty | Pleasure | Lived | Non-off. suffering | Against no pressure | Against matched pressure | H41 |
|---|---|---|---|---|---|---|---|---|---|
| trial | −0.009 [−0.032, +0.015] | 0 | **+0.086** [+0.007, +0.169] | +0.0004 | +0.0004 | +0.0009 [+0.0001, +0.0019] | no gain | no match (below B) | not supported |
| cheap | 0 (identical to B in every run) | 0 | 0 | 0 | 0 | 0 | no gain | not better | not supported |
| prenup | +0.003 [−0.007, +0.014] | 0 (wide +0.003) | **−0.038** [−0.071, −0.013] | −0.0000 | −0.0000 | −0.0000 | no gain | no match (73%) | not supported |
| info | **+0.019** [+0.003, +0.036] | 0 | −0.016 | −0.0003 | −0.0003 | +0.0002 | no gain | **better** (matched at P0.57 in 99%: held −0.020, pleasure −0.0010) | not supported |
| lat | **−0.138** [−0.191, −0.091] | 0 | **+0.287** [+0.200, +0.382] | −0.0017 | −0.0017 | +0.0008 [+0.0001, +0.0017] | no gain | no match | not supported |
| all | **−0.240** [−0.304, −0.182] | 0 (wide +0.001) | **+0.423** [+0.309, +0.542] | **−0.0031** [−0.0045, −0.0020] | −0.0031 | **+0.0028** [+0.0012, +0.0047] | **harm** | no match | not supported |

Formation-gain tests (one-sided sign-flip by pairing, Holm across the six aids): info p 0.011 (Holm 0.064), prenup 0.31, trial 0.77, others 1.0. **H41 overall: not supported** (all aids lower weeks together).

Read on pleasure AND freedom together: no aid is a win. LAT and all aids raise freedom (liberty) and cost pleasure: a trade-off, and for all aids the pleasure cost now clears the margin (harm by H41's rule). The trial raises liberty a little with no pleasure change and slightly more non-offsettable suffering: not a win either. Better information raises weeks together without holding anyone and without raising pleasure: it ties more pairs together for nothing measurable in pleasure, and costs a little liberty (−0.016, interval across 0). Pressure: P2 and P4 raise pleasure (+0.005, +0.007) while holding people in (0.087, 0.099) and narrowing liberty: **trade-off**, as before; lived pleasure moves by −0.0017 to +0.0009, so the gain is still the reward paid. Being held still goes with more suffering: 0.099 in the 13 weeks after a held reading against 0.069 after a worth one (ratio 1.4; old 1.5).

## Old against new (ADR 0020, stop rule)

Sign class against B, old / new. Everything not listed keeps its class.

| Arm | Same class in both versions | Version-dependent (old → new) |
|---|---|---|
| P0.5 to P4 | weeks together +, held + at every level; pleasure + at P2, P4; worse-off + at P1 to P4; lived 0 | formed at week 0: P0.5 0 → +, P1 + → 0; liberty: P0.5 0 → −, P4 − → 0; pleasure P1 0 → + |
| trial | weeks together 0, pleasure 0, held 0 | formed at week 0 0 → −; liberty 0 → +; non-offsettable suffering 0 → + |
| cheap | everything (identical to B in both) | none |
| prenup | weeks together 0, pleasure 0 | liberty 0 → − |
| info | pleasure 0, held 0 | weeks together 0 → + |
| lat | weeks together −, formed −, liberty + | non-offsettable suffering 0 → + |
| all | weeks together −, formed −, liberty +, non-offsettable + | pleasure, lived and the worse-off partner 0 → − (all aids is now harm) |

**Holds across versions (two versions):** pairing pressure raises weeks together and holds people in, at every level; living apart together and all aids lower weeks together and raise liberty; cheap solo housing never bites; H41 is not supported. **Version-dependent**, not patched: the trial's and the prenup's effect on liberty, the trial's effect on week-0 formation, better information's effect on weeks together, the all-aids pleasure sign, and pressure's effect on formation and liberty at single levels (the pattern across levels holds).

## Expectations written before the run

| ID | Expected | Actual | |
|---|---|---|---|
| E1 | Pressure raises weeks together and holds people in | + and + at every level; held 0.035 to 0.099 | holds |
| E2 | Lone weeks fall wherever old > 0.01, and no lone stretch over 26 weeks at suffering ≥ 0.5 | stretches: none over 26 in any arm (old trial: 2 runs, up to 59). Lone weeks: trial 0.058 → 0.047, but B 0.027 → 0.064 and all 0.018 → 0.019 | **misses** (half): the exit option forms households one member then leaves (story 2 below), and the one left stays because staying is worth it to it |
| E3 | B forms more at week 0 | 0.75 → 0.82 (+0.067 [+0.025, +0.117]) | holds |
| E4 | No exit-side aid gets a "+" formation gain; H41 not supported | trial, prenup, cheap 0; H41 not supported (info, not exit-side, is +) | holds |
| E5 | Prenup and trial formed-at-week-0 gain against B ≥ 0 | prenup 0.000; trial **−0.075** (B rose, the trial did not) | **misses** for the trial |
| E6 | Cheap identical to B | identical in every run | holds |
| E7 | Non-offsettable suffering falls in trial and all aids | trial 0.0041 → 0.0030, all 0.0054 → 0.0048 (paired intervals cross 0) | holds in point estimate only |

## The second measures

**The stand-in against the lived (Fix 2).** In B, over 842 reading status quos with 52 weeks of room, the forecasts had a member leave within 52 weeks in 13.4% of futures; the lived world had one leave in 14.8% of those 52-week spans (P1 11.9% against 9.5%, trial 12.2% against 16.2%, prenup 13.3% against 13.9%). The gap is under the prereg's 0.10 everywhere. Within 13 weeks the forecasts leave never (0% by construction: the first in-future reading is at week 13) and the lived world 4.5% (trial 7.6%): the lived reading acts at once, the stand-in a quarter later. So the stand-in gets the rate of leaving about right over a year and its timing late.

**Lone weeks (Fix 1)** in the table of E2. Lone readings in the new B arm: 83, of which 2 put a member past the bar; 8 emptied households re-formed at a retry.

## Story check (four lives)

1. **Story 4 again, both fixes (trial, p-peacekeeper with p-wanderer).** At the trial's end (week 78) both leave at once; neither is ever alone. A's suffering stays near 0.12 a week to the end, where under the lone reading alone it climbed to 1.11 after week 90. So with the exit option the bad spiral never starts in this life; with only the lone reading, A leaves into it. Matches the measures; it also shows the new gap below is about the routine, not the readings.
2. **B, p-bargainer with p-wanderer.** Under the old version they never form. Now they form at week 0 (equal bills): every one of the four futures at week 13 has B leaving at week 26, and B leaves at week 26. A stays alone the rest of the run, with its stay value (0.74 to 0.80) at or above its outside option (0.76 to 0.80) at all nine lone readings, suffering 0.067. **A planned short household**: this is the option value of exit, working as designed, and it is also why lone weeks rose in B (E2) and why "weeks together" rose by formation followed by exit. The same happens with p-wanderer and four other partners.
3. **Prenup, g-01011 with g-01100.** Old: formed only at a later retry (weeks together 0.83). New: formed at week 0 under equal bills and an equal split; together to week 130, when B leaves; A's lone reading at 143 says stay (0.89 against 0.85). Matches.
4. **Trial (story 4's pair is the trial life).** The trial's lower week-0 formation against B comes from B rising, not the trial falling (0.74 in both versions): a trial is scored over 13 weeks, and the first in-future reading is at week 13, so the exit option never enters a trial's formation value. That is a property of the design (stand-in (c)), and it explains E5's miss.

## A new gap found reading story 4

The lone reading works: the member left alone (A, p-peacekeeper) now leaves 24 weeks after its partner instead of staying 78. **But leaving does not end its suffering.** From about week 95 its rest and connection fall to 0, the "denied" condition puts non-offsettable suffering at 0.50, and its suffering stays at 1.11 a week to week 156, out of the household exactly as it was in it. The outside option it compared at week 102 was 0.80 on its yardstick (w = 0.81); what it lived after leaving is about 0.81 − 0.81 × 1.11 ≈ −0.09. So story 4's suffering was not caused by being stuck alone, and the outside-option rollout does not foresee a spiral the lived member is already in. That is a gap in the routine (rest and connection starved) and in the outside forecast, not in the readings. Not patched.

## Is the hybrid ready for the many-agent world?

**Not yet, and the reason changed.** The two gaps named after H41 are closed in the sense the prereg defined: a member left alone has a reading, and forecasts let future selves leave. Every old check still passes except K1, which failed before. What stands in the way now:

- **KX2 failed.** The known answer that should show the exit option at work did not separate in its fixture. Either the fixture is wrong for the question (likely: its cost falls on staying) or the option is too weak to see; this run cannot say which. A fixture with a pure exit cost (a one-off cost paid only on leaving, as in the exact model) is the next check; it needs its own prereg.
- **The in-future rule leaves late.** Over a year it leaves about as often as lived agents do; within 13 weeks never. Trials and any 13-week choice cannot see the exit option at all.
- **The routine can starve rest and connection** (story 4's member, new gap above), and neither the household nor the outside forecast sees it.
- **Cost.** Unchanged: 16 to 76 s a run (B 18 s), as in H41.

So the many-agent spec keeps the H41 version frozen for now, with this version named as the candidate.

## Misses and weaknesses, plainly

- KX2 failed; K1 failed (as before). E2 and E5 missed in part.
- One seed per pairing; formation effects under about 0.08 are below what 120 pairings resolve (prereg power check); E7 holds only in point estimate.
- The in-future rule is a look-back with an anchored outside option, not a forecast of the future self's forecast; PT-H cannot see whether it is right, only the second measure can, and it says "about right over a year, late within a quarter".
- Re-forming after an emptied household uses the old retry on a world that has already settled an exit; items are not re-initialised.
- The new gap (starved rest and connection) is unexplained; not patched.

## Can be about / cannot be about

This can be about whether the hybrid, given a reading when alone and forecasts with an option to leave, still passes its known-answer checks, and how H41's arms move in the formation check's household when it has both. It cannot be about people, real exits or real prenups, about an agent that forecasts its own future choices, or about the many-agent world.

## Reproduction

`uv run python scripts/hybrid_exit_option.py --story`, `--kx2`, `--reach`, `--run` (about 3.2 hours on 4 workers), `--old`, `--decomp`, `--analyze` (writes runs/h41-exit-option/analysis.json), `--life ARM A B [--version new|old|lone|exit]`. `uv run python scripts/hybrid_fix_check.py --trap --a4`; `uv run python scripts/hybrid_passtest.py --a4 --audit` then `--a4 --analyze`; `uv run python scripts/value_consistency.py --hybrid --world --a4 --run`. Tests: `uv run pytest tests/test_hybrid_lone.py tests/test_hybrid_exit.py`; pins `uv run pytest -m slow`.
