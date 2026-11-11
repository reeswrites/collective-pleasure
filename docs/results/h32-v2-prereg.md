# H32-v2 and H32b-v2 preregistration: egoist against utilitarian on the fixed model (ADR 0015 template, with the 2026-11-11 reachability section)

Status: written and committed before the confirmatory run. The reachability check below was run first, as the template now requires. Agents: none; exact dynamic programming. Model API calls: none. Cost $0.

Wording rule: agents feel nothing. "Pleasure" is a gloss for a modeled hedonic state (ADR 0010). Every number is ASSUMED. Findings are about this model, not people.

## Purpose and claim

H32: under free exit and shared-experience amplification, an egoist chooses nearly the same policy as a utilitarian; remove free exit or amplification and the policies diverge. The first test (docs/results/h32.md) was flawed: the correctness review (docs/reviews/2026-11-11-correctness.md, findings 1, 2, 9) found that "supported" could not be reached (at most 6 of the 16 cells it needed were open), that the leave threshold and the living-apart payoff were one parameter, that with amplification and giving off a week together only cost the egoist, and that the partner's smoothed estimate let the egoist alternate selfish and generous weeks. This rerun fixes the model and asks the same question, plus H32b's: does a ladder do better than a cliff exit?

## Model changes (src/mar/convergence.py, commit 7f67a3d; all flags, default off, so H32 and H32b reproduce)

- **(a) Threat split from payoff.** `o_leave`: the partner leaves when its estimate falls below this. `o_B`: what it gets each week living apart. In H32 they were one number.
- **(b) A bond worth something.** `companion`: each member gets this much per week together, whatever the activity. With 0.1 against an upkeep of 0.05 a week together is worth +0.05 to each, so the partner leaving is a loss to the egoist even with amplification and giving off.
- **(c) A partner harder to game.** `est = "mean"`, `window`: the partner judges the mean of its last `window` weeks, each rounded to 0.05. Window 1 means it judges each week on its own, so one bad week below the threat ends the pair. The H32 EMA (weight 0.5) is kept as `est = "ema"`.

## Design

- **v2 configuration (every new value ASSUMED):** o_B 0.25 (apart payoff, fixed), companion 0.1, est "mean" with window 1 (weekly judging). Everything else as H32: five-activity menu, 52 weeks, upkeep 0.05, satiety 0.5, giving 0.5, partner sight w 1, noise 0, kind tie-break.
- **Grid.** alpha {0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3} x threat o_leave {0.1, 0.25, 0.4, 0.6, 0.8}: 45 cells. Finer in alpha than H32 because the open cells sit below alpha 1.5.
- **Arms.** The 8 H32 arms (exit x amp x give). Exit modes for the exit arms: cliff, withdraw-only, full ladder (H32b's rungs and rules).
- **Estimator sensitivity.** The cliff exit+amp and exit-only arms rerun with window 4 and with the H32 EMA.
- **Robustness.** Partner sight w {1, 0.5, 0} x noise eps {0, 0.05}, on the 25 cells with alpha 0.25 to 1.25, for each exit mode, with the corrected noise criterion below.
- **Measures.** As H32: D, R, Q, converged = D <= 0.2 and R <= 0.05.
- **The pattern, restated (review finding 1).** At a cell, with giving off: (1) exit+amp converges AND the utilitarian keeps the pair together to the end with probability at least 0.5 x (1 - eps)^52; (2) amp-only does not converge; (3) exit-only does not converge with the pair kept. Both objectives ending the bond does not count as convergence. The (1 - eps)^52 factor is the correction of the noise criterion found while designing H35 (docs/results/h35.md): noise alone leaves the pair with probability 0.07 at eps 0.05.
- **Does exit move the egoist.** TV distance between the egoist's occupancy in amp-only and in exit+amp, in each cell.
- **Unit of resampling: none.** Deterministic, exact. Every prediction is a pass or fail check (ADR 0015 point 4).

## Can every verdict happen? (required; run before this prereg was written)

Command: `uv run python scripts/h32v2_run.py --check` (writes runs/h32v2/check.json; under 1 second). It uses exit-free quantities and probes at threats outside the grid (o_leave 0 and 1.0). It does not solve any grid cell with exit on. I looked at all of its output. That includes the probe results for the exit arms at o_leave 1.0, which tell me where exit can work at an extreme threat. The predictions below are written knowing that.

- **Open cells.** Amp-only ignores the threat. It converges at alpha 1.5, 2 and 3 (exit-free, as in H32), so those 15 cells cannot show the pattern. At alpha 0, exit+amp and exit-only are the same arm, so the pattern is impossible there. Open: alpha 0.25, 0.5, 0.75, 1, 1.25, i.e. 25 cells.
- **Reachable at all (probe, threat 1.0, weekly judging).** The pattern appears at alpha 0.75, 1 and 1.25. It does not appear at 0.25 or 0.5: there, at the maximal threat, the egoist prefers to let the partner go rather than give it the weeks it demands. So 3 open alpha values can reach "supported".
- **Verdict rule (set from the count above).** Supported iff the pattern holds at some grid threat for at least 2 of the 3 reachable alpha values. "Supported" is reachable: the max-threat probe shows it at all 3. "Not supported" is reachable: the toothless probe (o_leave 0) shows the pattern at none.

| Verdict or clause | Free check that reaches it (or makes it fail) | Command or file | Result |
|---|---|---|---|
| supported | max-threat probe, o_leave 1.0 | runs/h32v2/check.json `probe_max` | reached (alpha 0.75, 1, 1.25) |
| not supported | toothless probe, o_leave 0 | `probe_toothless` | reached (no alpha) |
| Q1 control fails | H32's toy fixture (x 1.0/0.0, y 0.5/1.0): all-off D 0 | docs/results/h32-prereg.md pilot | reached |
| Q3 fails | toothless probe: 0 pattern cells, against 9 predicted | `probe_toothless` | reached |
| Q4 fails | at alpha 1.5 the max-threat probe has an egoist shift of 0 (exit cannot move an egoist that already converged); in the toothless probe exit never binds, shift 0 | `probe_max_exit_shift` | reached |
| Q5 fails | companion 1.0, threat 1.6, alpha 0: exit-only converges with the pair kept (D 0.019, R 0.002) | scratch probe, disclosed here | reached |
| V1 fails | toothless probe: full ladder 0 cells = cliff 0 cells, so "fewer" fails | `probe_toothless` | reached |
| D1, D2 | estimator and withdraw-vs-cliff comparisons: no free input found that makes a clean directional prediction fail | `probe_ema`, `probe_withdraw` | marked descriptive, no verdict |

Also seen in the check, and disclosed: at threat 1.0 withdraw-only shows the pattern at the same 3 alpha values as the cliff, the full ladder only at 0.75, and the H32 EMA at none.

**The metric can see the mechanism.** Companionship enters own and partner pleasure in every week together (`rewards`), so it is in D's labels (activities) only through choices, and in R through the totals. The threat enters only the leave decision (`leave_at`). Apart weeks pay o_B, which enters the utilitarian's total.

## Exploratory pilot

None beyond the check and the H35 toy runs. No grid cell with exit on was solved.

## Power check

Not applicable: no sampling.

## Predictions

Hand reasoning, informed by the check. Judged weekly, a partner bans any week below the threat. At threat 0.25 the egoist can still use its second passion as a shared week (partner pleasure about 0.26), so it alternates that with common ground B and does not converge. At 0.4 and above only common-ground or partner weeks pass. At alpha 0.75 to 1.25 the pair is still worth more to the egoist than living alone, so it gives in. At alpha 0.5 and below it is not, so it lets the partner go.

| ID | Quantity | Comparison and threshold | Test |
|---|---|---|---|
| Q1 (control) | all-off arm | R >= 0.15 AND D >= 0.8 | deterministic |
| Q2 (verdict) | reachable alphas with a pattern cell at some grid threat | at least 2 of 3 (prediction: 3 of 3, supported) | deterministic |
| Q3 | the set of pattern cells (cliff) | symmetric difference with {alpha 0.75, 1, 1.25} x {threat 0.4, 0.6, 0.8} of at most 2 cells | deterministic |
| Q4 (exit moves the egoist) | egoist occupancy shift, amp-only to exit+amp, in every pattern cell | at least 0.25 in each | deterministic |
| Q5 | exit-only arm, all 45 cells | never converged with the pair kept (companionship 0.1 is too little for the egoist to give the partner its weeks) | deterministic |
| V1 (H32b-v2) | pattern cells, full ladder against cliff | full ladder strictly fewer | deterministic |
| D1 (descriptive) | pattern cells by estimator: weekly, mean of 4, EMA | reported | deterministic |
| D2 (descriptive) | withdraw-only against cliff pattern cells | reported | deterministic |
| D3 (descriptive) | robustness counts by exit mode, w and eps, corrected criterion | reported | deterministic |

## Limits stated now

- A partner that judges each week singly is a strong partner. It is close to a hard demand. The H32 EMA partner was weak in the opposite direction. D1 shows how much the estimator decides.
- Companionship 0.1 and the apart payoff 0.25 are assumed. Q5 depends on companionship being small.
- One menu, a rule-following partner, full information, no discount. All H32 limits apply except the three fixed here.

## Amendments

None yet.
