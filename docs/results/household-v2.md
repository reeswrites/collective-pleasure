# Household v2 results: goals, a hedonic model and enforced sanctions

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: instrument calibration with scripted persona-driven agents. No LLM, no network. Findings are about rule systems and scripted agents, not people. Predictions: docs/results/household-v2-prereg.md (committed before any run, not edited). Design: docs/decisions/0010-hedonic-model.md. Run: `uv run python scripts/household_run.py` (about 3 minutes with the seam ladder, 30 s with `--no-ladder`); report page runs/household-v2/frontier.html (not committed). 360 runs: 8 variants x 15 persona pairings x 3 seeds x 156 weeks. Shocks (job loss, illness, move) are misalignment in the wider system outside the household, at low rates from the config block; mean 2.2 shock events per run.

## Prereg vs actual

| # | Preregistered | Actual |
|---|---|---|
| 1 | non-trivial trade-off (frontier of 2 or more with two points differing by 0.05 in both scores, in opposite directions) | FAIL. Frontier = baseline and needs_duty (they tie: freedom 1.000, cooperation 0.908); they dominate everything. No trade-off. |
| 2 | trap fails in at least 8 of 15 pairings; no other variant fails except possibly contact_free | PASS, but near-definitional: trap fails in 15 of 15 (fail share 1.00); contact_free also fails (1.00); no other variant fails |
| 3 | author_seed upward share at least 0.10 above baseline's and does not fail | FAIL. Both 0.844; author_seed does not fail (fail share 0.13, same as baseline) |
| 4 | Anchor/Wanderer lowest in at least 5 of 8 variants | FAIL. Strictly lowest in 0 of 8; the pair is upward (1.00) in every non-trap variant |
| 5 | seam ladder identical to v1 | PASS. Table identical to the pre-change run (the v1 world and seam_depth are untouched; tests pass) |

## Spiral results per variant (mean over 45 runs)

| variant | upward share | downward share | fail share | time to cross | pleasure (passing) | suffering off / non | freedom | cooperation |
|---|---|---|---|---|---|---|---|---|
| needs_duty | 0.844 | 0.111 | 0.133 | 0 | 0.857 | 0.151 / 0.013 | 1.000 | 0.908 |
| baseline | 0.844 | 0.111 | 0.133 | 0 | 0.857 | 0.151 / 0.014 | 1.000 | 0.908 |
| free_chaotic | 0.844 | 0.133 | 0.133 | 0 | 0.848 | 0.157 / 0.014 | 1.000 | 0.897 |
| exit_half | 0.844 | 0.133 | 0.133 | 0 | 0.848 | 0.157 / 0.014 | 1.000 | 0.897 |
| veto_consent | 0.844 | 0.133 | 0.133 | 0 | 0.848 | 0.157 / 0.014 | 1.000 | 0.897 |
| author_seed | 0.844 | 0.133 | 0.133 | 0 | 0.848 | 0.157 / 0.014 | 1.000 | 0.897 |
| trap | 0.178 | 0.556 | 1.000 (FAILS) | 3.5 | none passing (all runs: 0.674) | 0.425 / 0.394 | 0.679 | 0.730 |
| contact_free | 0.178 | 0.556 | 1.000 (FAILS) | 3.5 | none passing (all runs: 0.675) | 0.422 / 0.391 | 0.679 | 0.731 |

Time to cross is 0 for most upward runs because all agents start at the tipping point (start position 0.0, ASSUMED) and drift up at once. Five pairings (bargainer+steward, host+peacekeeper, host+steward, peacekeeper+steward, peacekeeper+wanderer) fail in every non-trap variant; shocks hit these pairs the same way in every variant (common random numbers), so those fails are not caused by the rules.

## Author-seed result

author_seed (six cards, the negotiation phase stubbed as an even-split exit, ASSUMED) is indistinguishable from exit_half, free_chaotic and veto_consent, and slightly below baseline on cooperation (0.897 against 0.908) because it has no needs duty. It does not put more pairings in the upward spiral than baseline (0.844 each). Prediction 3 failed. A reading consistent with the data, not tested here: with these scripted agents, nothing in the seed ever binds.

## What surprised

- Sanctions are enforced and no agent ever broke a soft rule (0 sanctions per run in all variants). Control attempts (requests) are rare, so veto_consent never differs from free_chaotic. Enforcement is verified by unit tests only.
- Freedom is exactly 1.000 for every variant without a restriction card, so it separates only the trap family.
- The trap fails by definition: no exit retaining 25 percent is the non-offsettable "trapped" condition, and the forfeit card creates it from week 0. contact_free is identical to the trap for the same reason.
- Goals did not create the missing trade-off: the cooperation gain from the needs duty is 0.011, because persona agents already fund the shared bills. A trade-off needs rules that bind agents who want something else; these personas rarely want to violate anything.

## Parameter block (all ASSUMED unless cited; HedonicConfig in src/mar/hedonic.py)

Spiral: tipping point 0.0, start 0.0, flow gain 0.30, upward feedback 0.05, downward feedback 0.08, capacity clip(1 + 0.6 (B - tip), 0.5, 1.3) x (1 - 0.5 N), up margin 0.20, tail 8 weeks. Clocks per week: rest decay 0.50, base refill 0.40, rest action 0.30, work fatigue 0.10; connection decay 0.30, cohabitation 0.10, friend 0.35, together 0.30, friend-initiated 0.15; money level = money / 8, living cost 2; security decay 0.01, refill 0.03 x clip(assets / 25). Non-offsettable: onset 4 weeks, denied below 0.15 for a need of salience at least 0.12, intensities trapped 0.5, denied 0.5, diminished 0.4, load decay 0.25, fail 6 weeks. Mix: pleasure 0.5 needs, 0.5 aspirations, unmet aspiration 0.3. World: incomes 6 (Partner A) and 5 (B) per work block, 10 units of time a week, bills 10 per 4 weeks (6 alone), warn reproach 0.15 per week, pooled savings of 45 each as a safety net. Shock rates per person-year: job loss 0.12 (BLS JOLTS, about 1.0 to 1.1 percent per month; durations 8 to 26 weeks ASSUMED), illness 0.08 (ASSUMED, 3 to 8 weeks), new connection 0.20 (ASSUMED), move 0.087 per household-year (Census CPS 2022 mover rate 8.7 percent; secondary-source reading). Not sourced, ASSUMED: all time-use proportions (the American Time Use Survey was not read), the loneliness-based connection clock (motivated by the US Surgeon General's 2023 advisory, known from news coverage only), the utility policy constants.

## Calibration deviations from the prereg parameter block (made after the first test runs, before the first full run)

The first test runs collapsed every household (security reached 0 within a year even with money in hand). Changed: security refill reference assets 60 to 25 and decay 0.02 to 0.01; incomes raised from 4 and 3 to 6 and 5 per block; "need denied" now requires salience of at least 0.12 (a need a persona barely cares about is not denied); the contribution utility was raised. The prereg's other parameters are unchanged. These were tuned for viability, not to move a prediction, and the predictions were not revisited.

## Limits

Scripted agents; assumed rates; saturated pleasure (many runs reach the ceiling of the position scale, so upward shares and pleasure separate norms poorly outside the trap family); one pair ordering (the lower id is Partner A and earns more); seeds vary only utility noise and shocks. Verdicts about rules hold only for these agents. Superseding the pre-registered ADR 0008 negotiation phase is not attempted.
