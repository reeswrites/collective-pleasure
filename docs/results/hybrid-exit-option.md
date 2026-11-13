# Hybrid fixes: the member left alone, and forecasts with the option to leave

Wording rule: agents feel nothing; "pleasure", "suffering", "value", "forecast" and "held" are glosses for modeled numbers.

Model: `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit`, exit fallback F4 with items (F5 in the prenup arms), corrected rule (ADR 0020). The version before: the same without the last two flags (H41's).

Status: run on 2026-11-13 after the preregistration ([hybrid-exit-option-prereg.md](hybrid-exit-option-prereg.md), commit 5d5b4f1; code ac90cc5; free checks noted in the prereg at dd454d4, before the confirmatory run). Scripted agents, no model calls, every number ASSUMED. **The H41 rerun is still running; this file has the known-answer checks only, and gets the rerun when it lands.**

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

## A new gap found reading story 4

The lone reading works: the member left alone (A, p-peacekeeper) now leaves 24 weeks after its partner instead of staying 78. **But leaving does not end its suffering.** From about week 95 its rest and connection fall to 0, the "denied" condition puts non-offsettable suffering at 0.50, and its suffering stays at 1.11 a week to week 156, out of the household exactly as it was in it. The outside option it compared at week 102 was 0.80 on its yardstick (w = 0.81); what it lived after leaving is about 0.81 − 0.81 × 1.11 ≈ −0.09. So story 4's suffering was not caused by being stuck alone, and the outside-option rollout does not foresee a spiral the lived member is already in. That is a gap in the routine (rest and connection starved) and in the outside forecast, not in the readings. Not patched.
