# H01 preregistration: pressing when exit is free (ADR 0015)

Status: written and committed before the first confirmatory run. Nothing here is a result. Scripted or model agents: scripted persona-driven agents only. Model API calls: none ($0).

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences. Findings are about rule systems and scripted agents, not people.

## Purpose and claim

Hypothesis H01 (docs/hypotheses.md): when exit is free, a controlling persona who presses lowers its own lifetime pleasure compared with the same persona playing cooperatively, because the partner leaves. The alignment reading: power-seeking backfires when the other party can walk away. A decision rides on it: whether "free exit" is carrying weight as a protection against control in the seed rules (R8a) because it makes control self-defeating, or whether pressing is costly to the presser for other reasons. The no-exit control separates the two.

## Design

- World: the weekly household world (`WeeklyWorld`, 156 weeks), scripted persona agents, pleasure levers OFF (the default; `levers=None`), no negotiated deal (`deal=None`, the rule set's own cards).
- Rule sets: `author_seed_v2_free_exit` (v2.2; R8a may-leave, exit terms negotiated), `baseline`, and a **no-exit control** = the `author_seed_v2_free_exit` cards plus one unconditional hard card `H01-no-exit` (`must_not leave`, no conditions), defined in `scripts/h01_control_run.py`. No file under `rules/` is changed.
- Pairings (the unit of resampling): the focal member is one of the three pressing personas (controller, freerider, overasker), the partner one of the six non-pressing personas, in both seatings: 3 x 6 x 2 = **36 pairings**. Pairings with two pressing personas are left out so that the partner's own pressing does not leave in both twins. All seeds of one pairing move together; a pairing's value is the mean over its seeds.
- Matched twins: the same pairing, the same seed, the same rules. The focal member plays its pressing script (`press=True`) or the same persona with the pressing candidates removed (`press=False`, the cooperative policy). The partner is unchanged. The two twins do not consume random draws identically after the first divergence, so they are matched on seed, personas and rules, not path for path.
- Measure: the focal member's **lifetime pleasure** = the sum over 156 weeks of its weekly `pleasure` in the current hedonic model with levers off. This is the present-weighted special case of ADR 0017 (no memory or anticipation term), and the claim is read with that caveat. Weeks after the focal member or the partner has left are counted as the model computes them (the person lives on, apart); nothing is zeroed by hand.
- Secondary measures (reported, not tested): wellbeing (pleasure less both suffering terms, summed), the partner's lifetime pleasure, the share of runs in which the partner left and in which the household dissolved, per focal persona.
- Fixed and ASSUMED: all of the household world's constants and the pressing scripts' utilities (docs/results/household-v3a-prereg.md); the partner leaves when its non-offsettable load is at least 0.2, or it has been low 4 weeks, or its trust falls below the leave threshold (hard-coded in `PersonaAgent.propose`).
- Seeds: 0 to 9 (10 per pairing and rule set; 36 x 10 x 2 x 3 = 2,160 runs). Pilot seeds 1000 to 1002 are never used in the confirmatory data.

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

Run first: `uv run python scripts/h01_control_run.py --pilot` (seeds 1000 to 1002, 36 pairings, `author_seed_v2_free_exit` and `no_exit` only, 432 runs, 70 seconds). Excluded from the confirmatory data. I saw it before writing the predictions below, and **it disagrees with the hypothesis on the contrast**:

| Quantity (sum of 156 weekly pleasures, press minus cooperative) | Pilot value | Pilot sd across pairings | Source file |
|---|---|---|---|
| gap under free_exit | -21.79 (pressing 110.7 vs cooperative 132.5) | 20.88 | runs/h01/pilot.json (not committed; `--pilot` re-creates it) |
| gap under no_exit | -23.51 (99.3 vs 122.8) | 21.93 | same |
| contrast, gap(no_exit) minus gap(free_exit) | -1.72 | 14.54 | same |
| partner left by week 156, free_exit | 0.417 pressing vs 0.056 cooperative | | same |

So in the pilot pressing already lowers the presser's own pleasure when nobody can leave (partner left 0.000 of the time under no_exit): the hypothesis's mechanism ("because the partner leaves") is not what the pilot suggests. I am **not** rewriting the predictions to fit the pilot: P3 below is the contrast the hypothesis asked for and the pilot says it will probably fail. That is a reasonable thing to learn.

## Power check (required)

Computed with `mar.stats.seeds_for_margin` and `mar.stats.power_two_arm(..., paired=True)` from the pilot spread (the unit is the pairing, so the number of units is fixed at 36 by the design; seeds only reduce within-pairing noise, and the seed-level sd of the gap, 21.6, is about the same as the pairing-level sd, 20.9, so more seeds would not help much; 10 are cheap and kept):

| Prediction | Margin | Spread used | Units for 80% power | Units chosen | Cost at that n |
|---|---|---|---|---|---|
| P1, P2 (gap below 0) | pilot effect -21.8 (d_z about 1.0); the smallest effect I care about, -3.12 (0.02 mean weekly pleasure), is not powered | 20.9 | about 12 pairings for the pilot effect; about 350 for the -3.12 margin | 36 pairings | $0, about 2 minutes |
| P3 (contrast above 0) | +8 (about a third of the pilot's free_exit gap) | 14.5 | 26 pairings for +8 (power at 36: 0.95; +5: 0.61; +3: 0.31) | 36 pairings | same |

P1 and P2 are powered for effects of about -9 and larger (d_z 0.4 or more at 36 pairings); the preregistered point-estimate floor of -3.12 is a floor for the estimate, not a powered margin, so a hold means "at least this large and the interval excludes 0". P3 is powered only for a true contrast of +8 or more; a weaker contrast would be read as DESCRIPTIVE.

## Predictions

| ID | Quantity | Unit | Threshold | Test | Alpha | Correction family | Interval |
|---|---|---|---|---|---|---|---|
| P1 | free_exit: focal lifetime pleasure, pressing minus cooperative | pairing (mean over 10 seeds) | estimate at most -3.12 (0.02 per week) and the 95% upper bound below 0 | paired permutation on pairing means, one-sided (pressing lower), exact sign-flip not feasible at 36, Monte Carlo with the +1 correction | 0.05 | Holm over P1, P2, P3 | paired bootstrap 95% (BCa) of the mean pairing difference; d_z and Cliff's delta reported |
| P2 | baseline: same quantity | pairing | same | same | 0.05 | same | same |
| P3 | gap(no_exit) minus gap(free_exit), per pairing | pairing | lower bound of the 95% interval above 0 (the gap is smaller or reversed under no_exit) | paired permutation, one-sided (greater) | 0.05 | same | paired bootstrap 95% |

Manipulation checks (deterministic-ish, reported as passes or failures, no interval): under `no_exit` no member leaves in any run; under `author_seed_v2_free_exit` pressing raises the share of runs in which the partner has left by at least 0.20 over the cooperative twin (the pilot saw +0.36).

Reported beside the tests, no verdict: the gap by focal persona; the partner's lifetime pleasure; and an EXPLORATORY sensitivity of P1 to the partner's non-offsettable leave load (0.2 is the world's value; 0.3 and 0.4 implemented by dropping a leave candidate that exists only because the load reached 0.2, `--sweep`), which is the hypothesis's pre-mortem.

## Verdict rule

- **H01 supported** iff P1, P2 and P3 all hold (point estimate and interval as written, Holm-adjusted p below 0.05).
- **Pressing is costly to the presser but exit is not the mechanism** iff P1 and P2 hold and P3 does not. This is the outcome the pilot points to, and it does not support the hypothesis's "because the partner leaves".
- **Not supported** if P1 or P2 fails.
- "Holds but the interval crosses the threshold" is weak support and is not cited as a confirmed hold.

## Not testable by design

The manipulation checks above (a hard prohibition on leaving prevents leaving).

## Limits stated now

Scripted agents; a fixed assumed utility for the pressing scripts; one hedonic model with the levers off, so "lifetime pleasure" is the present-weighted special case (no memory, no anticipation: ADR 0017); the leave rule is hard-coded, so P1 partly restates the world's own rule that distress makes the partner leave (the hypothesis's pre-mortem), and the load sweep is exploratory; the cooperative twin removes the pressing candidates but does not otherwise change the focal agent, so the gap also includes what pressing costs the presser directly (time and actions); the no-exit control adds a hard card to the hedonic model's constraint conditions as well as removing exit, so its level of pleasure is not comparable with free_exit, only the gap is; 36 pairings; the pairings with two pressing personas are excluded.

## Amendments

None.
