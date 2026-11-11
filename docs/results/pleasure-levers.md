# Pleasure levers results: do adaptation and anticipation, commitment payoff and unbundled bonds make seed v2.2 produce pleasure?

> **Correction (2026-11-11, correctness review).** A fresh review (docs/reviews/2026-11-11-correctness.md, finding 5 and the low items) checked this result. The numbers reproduce. The original text is kept unchanged below this block.
>
> - **LB1's metric cannot see the commitment friction.** The friction a commitment adds goes to suffering (`s_off`), not to `pleasure`. LB1 and LB2 measure mean `pleasure`. So the early cost LB1 was registered to test never reaches its metric. LB1 could fail only through side effects on behaviour, which are -0.009 early at k_pay 0. The LB1 miss is not evidence about whether commitment costs early. The sentence below about the payoff stock building "faster than the friction (0.04 per week for two commitments)" names a mechanism that does not act on the metric. The friction is also 0.02 per agent, not 0.04. The break-even near k_pay 0.03 is a side-effect number, not friction against payoff.
> - The same applies to `care_suffer` in the unbundled-network lever. Its non-coordination costs are missing from LC1a and LC2.
> - **Holm p-values are misquoted in the table below.** No label changes. LA1 and LB2: 0.0299, not 0.021. LA2a, LA2b, LC1a and LC2: 0.00055, not 0.0004.
> - H2's "miss robust" has an upper bound of 0.0287 against a bar of 0.03, a knife edge. LB1 and LB2 had no power check. LA1 was powered as a mean difference but tested as a share. LC2's peak (3 bonds) is only 0.0018 above 4 bonds and was picked from the data before D was tested.
> - **What this result can claim now.** LB2 (the later gain) stands on the pleasure measure. LB1 says nothing about an early cost. Testing it needs an outcome that includes suffering.

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Status: scripted persona-driven agents, assumed parameters, no model calls. Prereg: docs/results/pleasure-levers-prereg.md (committed first, 84b42b2; Amendment 1 with pilot, power check and seed counts committed before the confirmatory run, 9082092; nothing else edited). Code: `src/mar/hedonic.py` (`LeverConfig`), `src/mar/worlds/household.py`, `src/mar/personas.py`, `scripts/pleasure_levers_run.py`, tests `tests/test_levers.py`, `tests/test_levers_regression.py`. Run: `--run --seeds 8` (14592 controlled runs, 749 s) and `--headline --seeds 15` (1800 negotiated runs, 1387 s), `--analyze`. Raw records: runs/pleasure-levers/*.json.gz and analysis.json (git-ignored). ADR 0016.

## Headline

**The author's condition is NOT shown by these levers.** With all three levers ON, seed v2.2 is still below the imposed baseline on the 15 hand-persona pairings: D = -0.019 [95% CI -0.051, +0.009] (v2.2 0.851, baseline 0.870; v2.2 higher in 6 of 15 pairings). The lever-OFF gap re-measured on these seeds is -0.028 [-0.042, -0.015] (v2.2 0.836, baseline 0.864; reproduces the earlier -0.028). So the levers closed about a third of the gap (the all-lever effect is +0.015 for v2.2 [-0.003, +0.030] and +0.006 for the baseline [-0.011, +0.024]) but did not reverse it, and the interval includes zero. H1 was marked DESCRIPTIVE before the run (the pilot could not power it at 15 pairings), so the honest wording is: not shown, point estimate on the wrong side, interval crosses zero.

What the rules did produce: the ritual lever raises v2.2 pleasure by +0.015 [+0.003, +0.029] (H2 asked for more than +0.03: **miss robust**), and unbundled bonds alone raise v2.2 by +0.043 [+0.029, +0.055], the largest single effect. Adaptation alone lowers the level (-0.05 with the ritual; it is a cost to every source, and rituals recover about a third of it). Commitment payoff alone moves v2.2 by +0.002 [0.000, +0.007], because few households negotiate a commitment.

## Prereg vs actual (controlled mechanism runs: 57 pairings, 8 seeds; headline: 15 pairings, 15 seeds)

Unit: the pairing. Holm over the 11 tests. "Descriptive" means marked in Amendment 1 before the run (no verdict wording).

| ID | Preregistered | Actual (estimate [95% CI]) | Holm p | Label |
|---|---|---|---|---|
| LA1 | rotate beats repeat in >= 70% of pairings, adaptation ON | 49 of 57 = 0.860 [0.742, 0.937] | 0.021 | holds robustly |
| LA1c | (descriptive) repeat beats rotate with adaptation off | 0.0 of pairings, but uninformative: with hab_rate 0 no variant is ever more satiated than another, so the rotate policy never switches and the arms are identical (means 0.75098 and 0.75098). The prediction "repeat wins when adaptation is off" was not tested; a design flaw of the control, not a result | n/a | descriptive |
| LA2a | ritual minus ad hoc at equal dose > +0.01, adaptation OFF | +0.0190 [+0.0161, +0.0217]; dz 1.74. Dose per week 0.7448 vs 0.7459 (equal within 0.2%) | 0.0004 | holds robustly |
| LA2b | the ritual gap is larger with adaptation ON | +0.0037 [+0.0024, +0.0050] (gap 0.0227 ON vs 0.0190 OFF) | 0.0004 | holds robustly |
| LB1 | committed households lower in weeks 0 to 25 in >= 60% of pairings | 14 of 57 = 0.246 [0.141, 0.378] | 1.0 | miss robust |
| LB2 | committed higher in weeks 52 to 155 in >= 60% of pairings | 44 of 57 = 0.772 [0.642, 0.873] | 0.021 | holds robustly |
| LC1a | 3 bonds minus 1 bond, mean pleasure > 0 | +0.0318 [+0.0216, +0.0430]; dz 0.76 | 0.0004 | descriptive |
| LC1b | non-offsettable share, 1 bond minus 3 bonds > 0 | -0.0114 [-0.0291, +0.0049] (3 bonds have slightly more) | 1.0 | descriptive |
| LC2 | maximum at 3 to 5 bonds and 8 bonds below it | maximum at 3 bonds; curve (bonds: mean) 1: 0.787, 2: 0.788, 3: 0.819, 4: 0.817, 5: 0.768, 6: 0.706, 8: 0.457; max minus 8 bonds +0.362 [+0.336, +0.387] | 0.0004 | holds robustly |
| LC3 | shock loss smaller with 3 bonds than 1 | wrong sign: loss 0.0029 (1 bond) vs 0.0061 (3 bonds), difference -0.0032 [-0.0048, -0.0018] | 1.0 | descriptive |
| H1 | v2.2 minus baseline, levers ON, 15 hand pairings > 0 | -0.019 [-0.051, +0.009] | 1.0 | descriptive; condition not shown |
| H2 | ritual ON minus OFF in v2.2 > +0.03 | +0.0151 [+0.0030, +0.0287] | 1.0 | miss robust |

Break-even payoff for L-B (descriptive; sweep of k_pay, committed minus uncommitted, mean pleasure): early (weeks 0 to 25) / late (52 to 155) / lifetime. k_pay 0: -0.009 / -0.007 / -0.007. 0.02: -0.005 / -0.001 / -0.002. 0.04: -0.002 / +0.003 / +0.003. 0.06: +0.001 / +0.008 / +0.007. 0.10 (preregistered): +0.007 / +0.017 / +0.016. 0.20: +0.022 / +0.034 / +0.035. The share of pairings with committed above uncommitted in the late window rises from 0.25 at k_pay 0 to 0.70 at 0.02 and 0.81 at 0.15 and 0.20. The "pay now less, later more" crossing the author's note predicts appears only for k_pay between about 0.03 and 0.05 (a narrow window); above 0.06 commitment never costs on average because the payoff stock builds faster than the friction (0.04 per week for two commitments) outweighs, and the early window already shows a gain. The break-even for the late window is k_pay about 0.03; for the lifetime sum, about 0.03.

## Which levers produced pleasure

- **Anticipation (ritual): yes, by construction and in measurable size.** +0.019 over ad hoc time at equal dose with adaptation off, +0.023 with it on. In the negotiated v2.2 households the effect is +0.015 (not +0.03). The falsifier in the synthesis ("equal pleasure at equal dose") was not met, but note that the model gives the ritual its anticipation term directly (0.04 per week); the run shows the size after costs and cancellations, not that anticipation exists.
- **Rotation under adaptation: yes (86 percent of pairings), but adaptation itself lowers every arm's level (0.751 to 0.618 when repeating).** Rotating recovers 0.027 of 0.133 and spacing (the adaptive policy) 0.021; the levers are a defense against a loss that the lever creates.
- **Commitment converter: yes in the late window (77 percent of pairings), the early-cost crossover did not appear at the preregistered payoff.** In negotiated households it moves the mean little because most households make no commitment.
- **Unbundled bonds: yes up to 3 or 4 bonds in total, then a sharp fall.** The coordination cost (0.2 times n^1.7 units per week) overwhelms gains beyond 5 bonds. Bond shocks cost the 3-bond network more than the single bond in absolute terms (more bonds, more exposure): the diversification claim for shocks failed here.

## What this says about the author's condition

Under the model and these parameters, rules that create rituals, make commitments and widen the network add modeled pleasure, and in the v2.2 negotiated households the sum is +0.015 above the lever-off level, a third of the earlier gap to the imposed baseline. The baseline still leads on the 15 non-pressing pairings (higher in 9 of 15). Why the baseline stays ahead is not tested here; two untested readings: v2.2 households sometimes dissolve or live apart (the earlier demo's finding), and the ritual stub is accepted only by some persona pairs. The ritual formation rate and commitment stock in the negotiated households were not recorded (the `lever` summary is attached by `WeeklyWorld.play`, which the negotiation's lived household does not call), so the share of v2.2 households that actually got a ritual is unknown from this run. That gap is a limit of the instrument, noted for the next run.

## Limits

- **Modeled gloss.** Every lever payoff is written into the model, so LA2, LB2 and LC1 are partly true by construction. The informative results are the sizes, the L-B crossing window, the 3-to-4-bond ceiling and the failures (LB1, LC3, H2, H1).
- **Scripted agents, assumed parameters at one point** (no sweeps beyond k_pay, bond count and the ritual/adaptation arms; the prereg promised secondary sweeps of antic_gain, hab_rate and the coordination exponent, and they were not run).
- Adaptation applies to time together and friend contacts only, not aspirations or other sources.
- The ritual in negotiated runs is a week-0 stub agreement, not a term in the negotiation bundle (negotiation.py not extended); the pressing cohort was not run for the headline.
- LA1c control flawed (above); ablation numbers in the headline paragraph are versus the lever-off v2.2 level and are not preregistered tests.
- Load on the machine was high during the run; results are deterministic given seeds, so this affects time only.

## Bearing on the author's 13 open questions (synthesis section 4)

- **Q1 (lifetime or present-weighted):** the L-B comparison depends on the window; at the preregistered payoff commitment already pays in weeks 0 to 25, and only at low payoffs does it cost first. A lifetime horizon favors commitment for every payoff above about 0.03. The answer is parameter-dependent, so the number to ask the author about is the payoff, not the horizon.
- **Q2 and Q3 (enforcement versus reliance; chosen friction):** L-B splits them (friction and payoff stock versus trust and fines) but no persona-level reliance/enforcement trait was tested (P4b untested). Friction is modeled as offsettable, which is the answer to Q3 the model assumes, not one it tests.
- **Q6 (how thick, how many bonds):** with these costs the ceiling is 3 to 4 bonds in total (partner plus 2 or 3); 8 is far worse. The cost curve, not the benefit, sets this. A life with no core was not tested.
- **Q9 (pleasure includes security and money):** coordination units are taken from the same weekly budget as work, so many bonds lower pleasure mostly through money and rest, which illustrates how the pleasure score is also a poverty-and-time measure.
- **Q11 (adaptation rates as parameters):** the rates were assumed, and the size of the adaptation penalty (-0.13) shows how much the level depends on them. They should be swept, not endorsed.
- Not addressed: Q4, Q5, Q7, Q8, Q10, Q12, Q13.

## Reproduction

`uv run python scripts/pleasure_levers_run.py --pilot` (exploratory), `--run --seeds 8`, `--headline --seeds 15`, `--analyze`. Tests: `uv run pytest tests/test_levers.py tests/test_levers_regression.py`.
