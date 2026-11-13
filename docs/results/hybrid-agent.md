# Hybrid agent: pass tests

Wording rule: agents feel nothing; "pleasure", "value" and "forecast" are glosses for modeled numbers.

Status: run on 2026-11-12 after the preregistration ([hybrid-agent-prereg.md](hybrid-agent-prereg.md), commit b529d24; code 929caa8; Amendment 1 committed with this file). Scripted agents, no model calls. Instrument checks, not hypothesis tests: they say whether the hybrid does what it says, not whether its choices are good.

## In one paragraph

**Both pass tests pass, the routine one narrowly and only after one bug fix.** Big-choice forecasts on four sampled futures match sixteen held-out futures almost exactly: over 2,298 choice-units (formation, retries, readings, returns) the chosen option's forecast is off by −0.0002 a week [−0.0007, +0.0002], the rank correlation of forecast with held-out value is 0.98, and the forecast picks the held-out best option in 98% of choices that are not close. The routine first **failed** PT-R (rank correlations 0.02 to 0.04 below v2's), because the partner's projection of the bill agreement double-counted a payment. With that fixed (Amendment 1), PT-R passes: T1 0.958 against v2's 0.973 on the same sample, every clause within its 0.02. What still costs the routine accuracy is time together, the same satiety misforecast v2 has on the new scale, which matters more here because the hybrid's households form and last. Under the hybrid, households form like v1's did (G-L0 0.85 at week 0, G-L4 1.00) on a scale where v2's formed 0.88 and with bills where v2's formed 0.07 to 0.09.

## PT-H: big-choice forecasts against held-out futures

As preregistered: the formation check's world under the hybrid (saturating scale, bills that hurt, the corrected rule's 52-week windows), G-L0 and G-L4, every third confirmatory pairing, seed 0, 156 weeks, the stay lens off; every choice also scored on 16 held-out futures with the neutral yardstick. 80 runs, 2,744 s on 3 workers (`scripts/hybrid_passtest.py --audit`, `--analyze`; rows in runs/hybrid-passtest/).

| Clause | Result | Bar | |
|---|---|---|---|
| H1 calibration: mean F − R, chosen option | **−0.00016** [−0.00069, +0.00024] | within ±0.010, interval inside ±0.015 | holds |
| H2 discrimination: Spearman F with R | **0.980** (4,798 option-units) | ≥ 0.80 | holds |
| H3 choice agreement (held-out margin ≥ 0.010) | **98.2%** (2,031 units) | ≥ 80% | holds |
| | **PASS** | | |

By kind of choice, F − R on the chosen option: formation at week 0 +0.0002 (160 member-units), retries +0.0007 (42), readings −0.0002 (2,052), returns −0.0013 (44). The selection bias the prereg expected (an option chosen because it looked good on four futures) is too small to see: most choices are not close.

The planted-bias check (prereg, "Can every verdict happen?") failed all three clauses with an outside-option bias of +0.05, so the instrument can see a forecast that is off.

**After Amendment 1** (the bill-mirror fix touches the routine, and so every forecast's later weeks): a smaller rerun, G-L0, every sixth pairing, seed 0. 20 runs, 485 s on 3 workers (runs/hybrid-passtest-a1/). **PASS**: H1 +0.0005 [−0.0003, +0.0014], H2 0.979 (1,048 option-units), H3 99.1% (425 units), over 490 choice-units. Returns, the rarest choice, carry the largest bias (+0.010, few units). Week-0 formation 0.85 as before; households that ended 0.05 (0.18 in the first run on these and other pairings).

## PT-R: the routine at one week

The value check on the hybrid sample (`scripts/value_consistency.py --hybrid --run`: H39b's M0 world, every third pairing, seed 0, six sampled weeks, last call; saturating scale, bills that hurt), against v2 on the same pairings, seed and weeks on the same scale (the step-1 rows).

| ID | Hybrid, before Amendment 1 | **Hybrid, after** | v2, same sample | Bar (no more than 0.02 below v2) |
|---|---|---|---|---|
| T1 pooled rank correlation | 0.934 | **0.958** | 0.973 | ≥ 0.953 |
| T2 within decision | 0.958 | **0.974** | 0.987 | ≥ 0.967 |
| T3 best = actual best | 92.1% | **94.7%** | 96.5% | ≥ 94.5% |
| T4 best beats next | 92.7% | **95.6%** | 96.9% | ≥ 94.9% |
| T5 slope | 1.08 | **1.09** | 1.01 | 0.8 to 1.25 |
| T6 per-action gaps | hold | **hold** | hold | |
| | FAIL | **PASS** | | |

**Why it failed first.** In a settlement week, a member's payment counts toward its own agreed share, so the world's standing transfer takes that much less from it. The member's own projection knew this; the partner's did not: it saw the payment and still expected the payer's full share on top, so it saw the bill short by less than it would be. The prosocial share of that phantom saving made paying look worth up to +0.38 when it was worth 0. 22 of 304 bill payments were off by more than 0.02. The fix is one line in `agent_values._paid`: the partner's projection counts the payment toward the payer's share. A known-answer test that fails without it (`tests/test_hybrid.py::test_partner_payment_under_the_agreement_changes_nothing_when_shares_are_covered`). After it, bill payments sit at rank correlation 0.98 and mean gap −0.0001.

**What is left.** Time together: 58 rows, rank correlation 0.03, valued 0.023 above its worth on average. It is v2's satiety misforecast on the new scale ([pleasure-scale.md](pleasure-scale.md)), here on more rows because the hybrid's households last (bill payments: 304 rows here, 77 in v2's sample). Without time together the hybrid's T1 to T4 are 0.974, 0.986, 96.9%, 98.3% (v2: 0.988, 0.992, 97.8%, 98.4%). The pass is narrow: T3 clears its bar by 0.2 points.

## What the hybrid's lives look like (descriptive, from the PT-H runs)

| | G-L0 | G-L4 |
|---|---|---|
| formed at week 0 | 0.85 | 1.00 |
| share of weeks together | 0.88 | 0.99 |
| households that ended | 0.18 | 0.00 |
| bill term chosen: income / equal | 24 / 16 | 28 / 12 |

Before Amendment 1, 40 pairings, seed 0. On the old evidence (formation check, old scale): v1 0.84, v2 0.06, v2b 0.42 at week 0. The hybrid forms like v1 while valuing its weeks like v2. Two reasons visible in the design, not separated here: the bill agreement removes the drain that made v2's households fail, and the curve gives back part of what the cap hid. Step 3 measures this properly.

## Cost

Unaudited, from the timing probe: 20.4 s per formation-check run (v1 2.0, v2 3.0, v2b 4.5). Audited PT-H runs: 102 s each on average, 318 futures of 52 weeks, 1.1 forks (one-week simulations of a propose-only action) per run. PT-R: 214 s on 3 workers for 40 lives.

## Misses and weaknesses, plainly

- **PT-R failed as preregistered.** It passes only after Amendment 1, which changed the design where the check disagreed (a projection bug), as the prereg allows; numbers before and after are both above.
- **PT-H compares the model with itself.** A forecast that is wrong in the same way in every future would pass. Forecasts omit requests, refusals, vetoes, gifts and takes; in this world they almost never come up (1.1 forks per run), so the omission is small here, not in general.
- **The lived descriptive** (lived 13 weeks against the stay forecast) was preregistered as "reported" and is not computed yet.
- **One seed**, a third of the pairings; the stay lens off in PT-H.
- **The satiety misforecast on time together** stays in the routine, on purpose (ADR 0016), and costs it accuracy.

## Can be about / cannot be about

This can be about whether the hybrid's forecasts are faithful to the hedonic model's own expectation over futures it did not use, and whether its weekly routine agrees with the model at one week as well as v2 does, in the formation check's household on the saturating scale. It cannot be about whether the hybrid's choices are good for anyone, about people, or about any H38 claim.

## Reproduction

`uv run python scripts/hybrid_passtest.py --reach` (free checks), `--audit` (about 46 minutes on 3 workers), `--analyze`; `--a1 --audit`, `--a1 --analyze` for the amendment rerun. `uv run python scripts/value_consistency.py --hybrid --run` (about 4 minutes). Tests: `uv run pytest tests/test_hybrid.py -m ""`.
