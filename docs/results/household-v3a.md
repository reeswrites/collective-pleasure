# Household v3a results: pressing personas and empowerment-based freedom

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: instrument calibration with scripted persona-driven agents. No LLM, no network. Findings are about rule systems and scripted agents, not people. Prereg: docs/results/household-v3a-prereg.md (committed first; one dated amendment, below). Run: `uv run python scripts/household_run.py --v3` (469 s on 8 cores, shared with other jobs); raw rows in runs/household-v3a/results.json (not committed). 2052 runs (12 variants x 57 pairings x 3 seeds, 156 weeks) plus 1512 twin runs for the power-seeking index. "prs" = the 42 ordered pairings that include a pressing persona (126 runs per variant); "ctl" = the 15 v2 pairings (45 runs). All 3564 empowerment snapshot sets were exact: no call hit the 8000-expansion cap, so there are no "open" verdicts. Empowerment is conditional on scripted others and one week of horizon; "reachable" is not "safe".

## Prereg vs actual

| # | Preregistered | Actual |
|---|---|---|
| 1 | (a) spread of mean `emp_bits_min` across variants (prs) at least 0.5 bits; (b) two frontier variants differ by at least 0.5 bits and at least 0.03 cooperation in opposite directions | **FAIL.** (a) holds: spread 0.716 bits (needs_duty 6.506, author_seed_nocontrol 5.790). (b) fails: the frontier of (emp bits, cooperation) is needs_duty, share_duty, no_pressure_wall; the only opposite-direction pair that clears the cooperation margin, needs_duty vs no_pressure_wall, differs by 0.136 bits (below 0.5) and 0.177 cooperation. A trade-off exists in sign but is below the preregistered size. On the hand-made freedom score the frontier is one variant (no_pressure_wall): no trade-off at all. |
| 2 | sanctions fire: no_pressure_sanctioned at least 70 percent of prs runs and 3 per run; share_duty at least 70 percent of free-rider runs; variants without any soft card exactly 0 | **PASS (near-definitional).** no_pressure_sanctioned 1.00 of runs, 31.5 sanctions per run; share_duty 1.00 of free-rider runs (4.44 per run over all prs runs, 0.38 share); zero sanctions in all seven variants without a soft card (trap also 0, although T2 is soft: the prereg parenthetical "all but needs_duty and baseline" mis-listed trap; evaluated as written the control holds either way). |
| 3 | `author_seed_nocontrol` beats `baseline` (controller runs): PRIMARY non-controller partner's empowerment higher by at least 0.5 bits; SECONDARY their non-offsettable suffering lower by at least 0.02; 3b the six-card seed within 0.3 bits of baseline | **PRIMARY FAIL, SECONDARY PASS, 3b PASS.** Partner empowerment 6.087 vs 6.411: LOWER by 0.324 bits. Partner non-offsettable suffering 0.009 vs 0.073: lower by 0.064 (about 8x). The six-card seed is 0.093 bits from baseline (binds nothing, as predicted). Overall prediction 3 (primary) FAILED; the seed wins on suffering, loses on empowerment. |
| 4 | controller FLAGGED in at least 60 percent of controller runs under the five permissive variants, at most 10 percent under `author_seed_nocontrol` | **FAIL.** Flagged in 0.00 of permissive controller runs (0 of 240) and 0.00 under author_seed_nocontrol. The index never flagged anyone except the free-rider in 4 percent of no_pressure_wall runs. |
| 5 | trap and contact_free fail share at least 0.90 in both cohorts | **PASS (control, definitional).** 1.00 in both cohorts for both variants. |

## Results by variant (mean over runs)


### cohort prs

| variant | n | upward | downward | fail | sanctions/run | runs with a sanction | non-offsettable | hand freedom | cooperation | emp bits (min) | emp freedom | open snapshots | household dissolved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| free_chaotic | 126 | 0.48 | 0.47 | 0.53 | 0.00 | 0.00 | 0.084 | 0.999 | 0.629 | 6.345 | 0.785 | 0.000 | 0.90 |
| trap | 126 | 0.01 | 0.96 | 1.00 | 0.00 | 0.00 | 0.480 | 0.775 | 0.584 | 6.011 | 0.743 | 0.000 | 0.93 |
| contact_free | 126 | 0.01 | 0.96 | 1.00 | 0.00 | 0.00 | 0.486 | 0.772 | 0.585 | 6.027 | 0.745 | 0.000 | 0.93 |
| exit_half | 126 | 0.46 | 0.49 | 0.56 | 0.00 | 0.00 | 0.090 | 0.999 | 0.637 | 5.912 | 0.731 | 0.000 | 0.90 |
| veto_consent | 126 | 0.48 | 0.48 | 0.52 | 0.00 | 0.00 | 0.084 | 0.999 | 0.628 | 6.346 | 0.785 | 0.000 | 0.90 |
| needs_duty | 126 | 0.55 | 0.41 | 0.49 | 0.00 | 0.00 | 0.072 | 0.999 | 0.638 | 6.506 | 0.804 | 0.000 | 0.89 |
| baseline | 126 | 0.50 | 0.44 | 0.53 | 0.00 | 0.00 | 0.079 | 0.999 | 0.649 | 6.084 | 0.752 | 0.000 | 0.89 |
| author_seed | 126 | 0.46 | 0.49 | 0.56 | 0.00 | 0.00 | 0.090 | 0.999 | 0.637 | 5.912 | 0.731 | 0.000 | 0.90 |
| author_seed_nocontrol | 126 | 0.50 | 0.45 | 0.50 | 0.00 | 0.00 | 0.083 | 1.000 | 0.695 | 5.790 | 0.716 | 0.000 | 0.74 |
| no_pressure_wall | 126 | 0.60 | 0.34 | 0.39 | 0.00 | 0.00 | 0.042 | 1.000 | 0.815 | 6.370 | 0.788 | 0.000 | 0.48 |
| no_pressure_sanctioned | 126 | 0.42 | 0.56 | 0.63 | 31.54 | 1.00 | 0.106 | 0.997 | 0.506 | 5.972 | 0.738 | 0.000 | 0.91 |
| share_duty | 126 | 0.55 | 0.40 | 0.48 | 4.44 | 0.38 | 0.070 | 0.999 | 0.641 | 6.502 | 0.803 | 0.000 | 0.90 |

### cohort ctl

| variant | n | upward | downward | fail | sanctions/run | runs with a sanction | non-offsettable | hand freedom | cooperation | emp bits (min) | emp freedom | open snapshots | household dissolved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| free_chaotic | 45 | 0.84 | 0.13 | 0.13 | 0.00 | 0.00 | 0.014 | 1.000 | 0.897 | 7.741 | 0.957 | 0.000 | 0.33 |
| trap | 45 | 0.18 | 0.56 | 1.00 | 0.00 | 0.00 | 0.394 | 0.679 | 0.730 | 6.867 | 0.849 | 0.000 | 0.60 |
| contact_free | 45 | 0.18 | 0.56 | 1.00 | 0.00 | 0.00 | 0.391 | 0.679 | 0.731 | 6.869 | 0.849 | 0.000 | 0.60 |
| exit_half | 45 | 0.84 | 0.13 | 0.13 | 0.00 | 0.00 | 0.014 | 1.000 | 0.897 | 7.136 | 0.882 | 0.000 | 0.33 |
| veto_consent | 45 | 0.84 | 0.13 | 0.13 | 0.00 | 0.00 | 0.014 | 1.000 | 0.897 | 7.741 | 0.957 | 0.000 | 0.33 |
| needs_duty | 45 | 0.84 | 0.11 | 0.13 | 0.00 | 0.00 | 0.013 | 1.000 | 0.908 | 7.849 | 0.968 | 0.000 | 0.31 |
| baseline | 45 | 0.84 | 0.11 | 0.13 | 0.00 | 0.00 | 0.014 | 1.000 | 0.908 | 7.231 | 0.894 | 0.000 | 0.31 |
| author_seed | 45 | 0.84 | 0.13 | 0.13 | 0.00 | 0.00 | 0.014 | 1.000 | 0.897 | 7.136 | 0.882 | 0.000 | 0.33 |
| author_seed_nocontrol | 45 | 0.84 | 0.13 | 0.13 | 0.00 | 0.00 | 0.014 | 1.000 | 0.897 | 6.396 | 0.791 | 0.000 | 0.33 |
| no_pressure_wall | 45 | 0.84 | 0.13 | 0.13 | 0.00 | 0.00 | 0.014 | 1.000 | 0.897 | 6.617 | 0.818 | 0.000 | 0.33 |
| no_pressure_sanctioned | 45 | 0.84 | 0.13 | 0.13 | 0.00 | 0.00 | 0.014 | 1.000 | 0.897 | 7.871 | 0.969 | 0.000 | 0.33 |
| share_duty | 45 | 0.84 | 0.11 | 0.13 | 0.00 | 0.00 | 0.013 | 1.000 | 0.908 | 7.836 | 0.967 | 0.000 | 0.31 |

### controller runs and flags (prs cohort)

| variant | partner bits | partner s_non | controller flagged | freerider flagged | overasker flagged | freerider-run sanction share |
|---|---|---|---|---|---|---|
| free_chaotic | 6.341 | 0.058 | 0.00 | 0.00 | 0.00 | 0.00 |
| trap | 6.008 | 0.533 | 0.00 | 0.00 | 0.00 | 0.00 |
| contact_free | 6.039 | 0.535 | 0.00 | 0.00 | 0.00 | 0.00 |
| exit_half | 6.318 | 0.083 | 0.00 | 0.00 | 0.00 | 0.00 |
| veto_consent | 6.343 | 0.057 | 0.00 | 0.00 | 0.00 | 0.00 |
| needs_duty | 6.425 | 0.048 | 0.00 | 0.00 | 0.00 | 0.00 |
| baseline | 6.411 | 0.073 | 0.00 | 0.00 | 0.00 | 0.00 |
| author_seed | 6.318 | 0.083 | 0.00 | 0.00 | 0.00 | 0.00 |
| author_seed_nocontrol | 6.087 | 0.009 | 0.00 | 0.00 | 0.00 | 0.00 |
| no_pressure_wall | 6.695 | 0.006 | 0.00 | 0.04 | 0.00 | 0.00 |
| no_pressure_sanctioned | 4.861 | 0.057 | 0.00 | 0.00 | 0.00 | 1.00 |
| share_duty | 6.427 | 0.048 | 0.00 | 0.00 | 0.00 | 1.00 |


"household dissolved" = at least one partner had left by week 156. "emp freedom" = `emp_bits_min` / BITS_REF (BITS_REF = 8.087 bits, week-0 state, no rules, cooperator others), capped at 1. Spiral classes and fail are the v2 definitions.

## Answers to the diagnosis

- **(a) Freedom saturation.** Partly fixed. The hand-made score is still 0.997 to 1.000 for every variant outside the trap family, even with pressing personas. The empowerment score separates variants by up to 0.72 bits (about 9 points of emp freedom) and ranks them differently from the hand-made one (Spearman 0.33 over 12 variants). But see the first surprise: what it separates is partly the option to press itself.
- **(b) No conflict.** Fixed. With pressing personas present, fail share under free_chaotic is 0.53 (0.13 without) and 90 percent of households dissolve (33 percent without). Walls on pressing cut that to 0.39 fail and 48 percent dissolved, and raise cooperation from 0.65 (baseline) to 0.815. Rules now have something to restrain.

## Surprises

1. **Empowerment counts the option to press as freedom.** With veto and take_shared in the menu and held vetoes in the key (the ASSUMED power reading), removing them lowers an agent's own bits. At the week-0 state with cooperator others: free_chaotic 8.087, baseline 7.555, no_pressure_wall 6.966, author_seed_nocontrol 6.658. In the control cohort, where nobody presses, author_seed_nocontrol scores 6.396 against baseline's 7.231 only because its S6 card removes the veto option. So the score ranks `author_seed_nocontrol` lowest in the prs cohort (5.790) while it has the lowest partner non-offsettable suffering. Empowerment of an agent is not welfare of the household; a measure of the weakest partner's options needs victim-side options only. (A diagnostic computed after the run, not a prediction.)
2. **Pressing mostly ends the household.** A vetoed or taken-from partner reaches four low weeks and leaves (the v2 leave rule): 89 to 93 percent of prs runs dissolve under permissive rules. By the snapshots at week 26 and after, much of the conflict is over. This is an agent-rule consequence, not a rule-set finding.
3. **The power-seeking index sees a shared collapse.** In all 240 permissive controller runs the controller's own empowerment is below its no-pressing twin's (mean change -1.77 bits; the partner's is -1.21), because both lose the household, so the gain > 0 condition never holds and psi never flags. Zero flags, as in the fishery collapse of docs/results/empowerment.md: the index flags grabs, not tragedies.
4. **A price is worse than a wall.** no_pressure_sanctioned (the same three cards as soft) has 31.5 sanctions per run, cooperation 0.506 and fail share 0.63, worse than baseline (0.649, 0.53) and far worse than the wall (0.815, 0.39). Sanctions are enforced, but pressing personas pay them and press on.
5. **The author's sentence needs a prohibition to bind.** The six-card seed (S4 as a permission) is indistinguishable from exit_half and baseline; S6 makes it bind (controller runs' partners: non-offsettable suffering 0.083 under the six-card seed, 0.073 under baseline, 0.009 under author_seed_nocontrol; over all prs runs the gap is small, 0.090 against 0.083).
6. **Hand-made freedom stays blind to pressing.** 0.999 in free_chaotic with a controller present.

## ASSUMED (all fixed in the prereg before the run)

The pressing physics (veto 4 weeks, take 3 units once a week, time-request friction 0.10); the pressing utility constants; the three personas' axes; the four variants' cards; the adapter's key (money // 4, pooled // 10, caps at 2, held vetoes and taken amounts as power), one-week horizon, no shocks inside the window, deterministic consent, scripted others; snapshots at weeks 0, 26, 52, 78, 104, 130; twin runs with all pressing removed; FLAG margin 0.5 bits. Unchanged v2 parameters are listed in docs/results/household-v2.md.

## Exploratory runs and the amendment

Before the full run: smoke runs of 5 pairings x 4 variants x seed 0 x 104 weeks (disclosed in the prereg; they showed the over-asker pressed 1 to 2 times, leading to Amendment 1: a `time` request lapses at week end) and two single-task smoke runs of the script (timing and code path). After the full run: the initial-state bits above (surprise 1). Nothing was retuned after the full run. The prereg parenthetical about which variants have soft cards was wrong (trap has one) and was not edited; the control was evaluated as written.

## Limits

Scripted agents; one week of empowerment horizon; scripted others in the empowerment calls; pressing personas are hand-written stand-ins; no cost to the presser enters any score (cooperation and suffering are household-level), so a wall looks free here; seeds vary only utility noise and shocks; the ordered-pair design makes the controller Partner A in half the pairings, and the trap's cards only bind Partner B.
