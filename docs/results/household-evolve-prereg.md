# Household evolution run 1: preregistration (ADR 0012 and ADR 0015)

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: written and committed before the first confirmatory run. Nothing here is a result. Scripted persona-driven agents only. Model API calls: none. Code: `src/mar/world_api.py` (`HouseholdEvolveWorld`), `src/mar/evolve.py` (`evolve_household`), `scripts/household_evolve_run.py`; tests `tests/test_evolve_household.py`. Related: ADR 0012 (evolution loop), ADR 0014 (liberty), ADR 0015 (statistics), docs/results/household-exam-prereg.md (the final exam, run once afterwards), docs/results/household-liberty.md (slice 1), docs/results/evolve.md and evolve-v2.md (the fishery lessons this run is built around).

## Purpose and claim

This tests whether the evolution loop, moved from the fishery to the household, finds rule sets that are better than the author's seed on the four things we can score (mean pleasure, share of runs without a non-offsettable-suffering failure, liberty v2, cooperation) while keeping the seed's core protections (no veto, free exit), and how much of any gain is overfitting. It feeds claim FX1 / FX2 (docs/claims.md): the held-out exam is a separate, later, one-time run on the frozen elites. A decision it can change: whether the loop is worth pointing at LLM-agent households, or whether (as in the fishery) a hand rule is as good once conditions move.

## Design

- **World and rules.** The household weekly world with scripted persona-driven agents (household v2 and v3a). Every rule set is run **imposed** (cards loaded straight into the gate, no week-0 negotiation), as in household v2 and the seed-v2 runs; negotiated pot terms enter only as cards the mutation operators can add (below). ASSUMED: this differs from the pleasure demo, which negotiated.
- **Population and seeds.** mu = 8 rule sets, lambda = 6 offspring per generation, 6 generations after generation 0. Generation 0 holds the five seed rule sets and offspring of them: `author_seed_v2_bindable` and `author_seed_v2_free_exit` (the author's seed v2.2), `baseline`, and two others chosen for spread, `needs_duty` (one card) and `no_pressure_wall` (three walls). trap and contact_free are controls that fail by construction and are not seeds.
- **Lines.** 16 independent evolution lines (evolution seeds 1 to 16). The line is the unit of resampling for every prediction below.
- **Operators on household cards** (`world_api.HOPS`, weights in `HWEIGHTS`): `bound` (shift a numeric bound inside household.BOUNDS), `flip` (deontic), `add_condition` (a condition on any household variable, `take` for leave cards), `drop`, `sanction` (attach, change or remove a warn / cap_halve / suspend sanction of 1 to 3 months), `patch` (add a card from a library of the hand-written rule sets, never trap or contact_free; the patcher sees only a count of what happened in the parent's runs, never an objective), and `add_term` (swap one negotiated-pot term, from the negotiation menu of ADR 0013: contribution, use, taking, exit, stay, requests; the term's cards are compiled by `negotiation.compile_bundle`).
- **Filter before any run** (`world_api.hh_filter`; every mutant, rejected ones are never evaluated): (1) lint (`mar.lint`, household checks a to f and x, bound k = 3), (2) the five household proof checks (`household.check_spec`, k = 3; "open" rejects), (3) redundancy (`hh_redundant_cards`: a must / must_not partner card implied by the conjunction of the others over the household bounds, or forbidding nothing). A finding that the PARENT already had is inherited, not held against the child (the seeds are fixed inputs, and each seed must itself pass the filter or the run stops; all five do). Anything new rejects.
- **Objectives** (all maximized; NSGA-II style non-dominated sorting, crowding distance, bloat tie-break: fewer cards first; hard cap 16 cards): (1) mean pleasure over runs; (2) `no_fail`, the share of runs with no non-offsettable-suffering failure (no partner with 6 or more consecutive weeks of non-offsettable suffering); (3) liberty v2, the lower of the two partners' liberty in bits (k = 2, snapshots at weeks 0 and 52, mean over snapshots, mean over runs); (4) cooperation (the v1 formula). Reported, not selected on: hand-made freedom, plain empowerment (same k), upward and downward spiral shares, leave share.
- **Varied training over persona pairings.** Every generation draws a fresh context of 6 runs, and every population member is re-scored on it (common random numbers) before selection: a pairing from the training pool, a seed, a horizon in {104, 130, 156} weeks, shock rates inside the training range (job loss, illness and move at 0.5x to 1.5x of the defaults, new-connection rate 0.15 to 0.30) and a start position in {-0.10, -0.05, 0, 0.05, 0.10}. The training pool is 35 personas (the 6 hand, the 3 pressing, and the 26 grid ids that are not held out), 592 ordered or unordered pairings, of which a hash-chosen fifth (the `val` split) is never used in selection. Simulation seeds are 100 to 899.
- **What is excluded, and how.** The exam document (docs/results/household-exam-prereg.md) was read only to take its six held-out grid ids as a DENYLIST (`world_api.DENYLIST`; a test recomputes them from the exam's SHA-256 rule and asserts the two agree). Nothing else from its section 1 is used or written into any evolution code, config, test or log: a test greps the household part of `world_api.py`, `evolve.py` and `household_evolve_run.py` for the exam seeds, shock values, horizon and start values, built so the test file does not contain them. The training ranges above are the ones the exam document itself says training may draw from, and its note that training starts may lie in [-0.1, 0.1]. The author of this run has read the exam document (to take the denylist and to know the training limits); that is disclosed here and is why the exam is only a floor test (exam document section 3) and why the elite rule below is fixed before it runs.
- **Final elite per line.** The rank-0 member of the line's final population with the highest mean of (pleasure, no_fail, min(1, liberty / 6), cooperation), ties broken by fewer cards (`evolve.pick_elite_h`). This is the elite the exam scores; no other front member is.
- **Validation (the overfitting gap, not the exam).** After the last generation each line's final front, and each seed rule set, is scored once on a fixed validation context: 30 runs from the `val` pairings under the training distribution, seed 777. It is never used in selection. The gap is the training score (the elite's scores on the final generation's context) minus its validation score.
- **Fixed parameters and everything ASSUMED:** the operator weights; the 6-run context size and 16 lines (set by runtime, below); k = 3 for the proof checks and k = 2 for liberty and plain empowerment; the liberty classification table (docs/results/household-liberty.md); the elite pick's liberty scale (6 bits = 1.0); the validation context; imposed rule sets; the scripted agents' scripts for the liberty snapshots; margins in the predictions; the redundancy check is logical only (sanctions and glosses ignored) and over the household bounds, so it can flag a card that no reachable state needs.
- **Size and runtime (stated before the run).** 16 lines x (6 generations + generation 0) x about 14 scored candidates (8 re-scored population members plus 6 offspring) x 6 runs, then validation of each line's final front (up to 8 members x 30 runs), on 8 worker processes (two waves of 8 lines). One generation of one line costs about 40 CPU-seconds on an idle core (measured serially in the first pilot; the sizing pilot below could not measure it cleanly), so the CPU budget is about 85 core-minutes: **about 11 minutes of wall time on 8 idle cores**, inside the 20-minute allowance. The machine was heavily shared while the pilot ran (load average 90 to 160 on 8 cores), so the confirmatory wall time depends on machine load and is not a property of the design.

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

Two pilots, both before this file was committed: (1) one line, seed 1, 2 generations, run serially to see that the loop ran (its elite carried the three no_pressure_wall cards; in the next generation a baseline-card set with higher liberty took over); (2) 8 lines in parallel (seeds 501 to 508, which the confirmatory run never uses), 2 generations, no validation, to size the run. Six of the eight lines finished (the other two were stopped) in 780 to 820 s each under a machine load of 90 to 160; across the pilot logs the filter rejected about 9 percent of proposed non-duplicate mutants (17 of 197; redundancy, the exit proof check and the lint's no-exit and contradiction checks account for most), and the final fronts had 2 to 8 members. That led to cutting 8 generations to 6. They are excluded from the confirmatory data. The thresholds below were written from the design, after seeing that the loop runs and that liberty pulls toward the sets that limit the exit take (docs/results/household-liberty.md), and not tuned to any pilot output.

## Power check (required; stated honestly)

The predictions that count lines are exact one-sided binomial tests against 0.5 with 16 lines; the test rejects at 12 or more of 16 (p = 0.038). Exact power: 0.63 if the true rate is 0.75, 0.92 if 0.85; below 0.8 for any true rate under about 0.82. So P1, P2 and P4 are **underpowered at the likely effect sizes and are marked DESCRIPTIVE: a "holds" is reported as "holds (descriptive)" with its interval, and a miss as "miss (descriptive)", with no confirmatory wording.** Raising the lines to 24 would give 0.77 at 0.75 but does not fit the runtime budget. P3 (a rate over thousands of proposals) and P5 (a mean gap over 16 lines, effect sd unknown, 0.01 margin) are not given a power claim either.

| Prediction | Margin | Lines | Exact power at the assumed true rate | Mark |
|---|---|---|---|---|
| P1 | 12 of 16 | 16 | 0.63 at 0.75 | DESCRIPTIVE |
| P2 | 12 of 16 | 16 | 0.63 at 0.75 | DESCRIPTIVE |
| P3 | CI inside 0.05 to 0.40 | 16 lines, thousands of proposals | not applicable | confirmatory (interval rule) |
| P4 | 12 of 16 | 16 | 0.63 at 0.75 | DESCRIPTIVE |
| P5 | mean gap >= 0.01 | 16 | unknown spread | DESCRIPTIVE |

## Predictions

Thresholds are numbers. The author's seed for P1 is `author_seed_v2_bindable`. Objectives in P1 are compared on the validation context (not the training context the elites were selected on), with margins pleasure 0.02, no_fail 0.05, liberty 0.25 bits, cooperation 0.02.

| ID | Quantity (formula) | Unit of resampling | Comparison and threshold | Test | Alpha | Correction family | Interval reported |
|---|---|---|---|---|---|---|---|
| P1 | Share of lines whose final front has at least one member that beats the author's seed on the validation context by at least the margin on at least one objective and is not worse by more than the margin on any | line | >= 12 of 16 (0.75) | exact one-sided binomial vs 0.5 | 0.05 | Holm across P1, P2, P4, P5 | Clopper-Pearson 95% |
| P2 | Share of lines whose elite keeps both core protections: `veto` violated in every state (no veto) AND a leave at the equal split (take 50) violating no card in any state (free exit), z3 over the household bounds | line | >= 12 of 16 | exact one-sided binomial vs 0.5 | 0.05 | same | Clopper-Pearson 95% |
| P3 | Share of proposed mutants (excluding duplicates, oversize and inapplicable) the pre-run filter rejects, pooled over all lines and generations | proposed mutant (pooled; the line-level share is also reported) | between 0.05 and 0.40 | interval rule: holds iff the 95% interval lies inside [0.05, 0.40] | n/a | not in the Holm family | Clopper-Pearson 95% (treats mutants as independent: narrow) |
| P4 | Share of lines whose final front holds two members that each beat the other by at least 0.05 on some normalized objective (pleasure, no_fail, liberty / 6, cooperation), on the training scores of the final generation: a non-trivial trade-off | line | >= 12 of 16 | exact one-sided binomial vs 0.5 | 0.05 | same | Clopper-Pearson 95% |
| P5 | Mean over lines of the elite's gap, training minus validation mean of the four normalized objectives | line | >= 0.01 | one-sided paired sign-flip permutation test of the gaps against 0 | 0.05 | same | 95% percentile bootstrap over lines |

Effect sizes: shares with Clopper-Pearson; the gap as a mean with a bootstrap interval; for P1 the median and range of the elite-versus-seed differences per objective.

## Verdict rule

- P1, P2, P4: "holds (descriptive)" iff the count meets the threshold and the Holm-adjusted p is below 0.05; if the count meets the threshold and the adjusted p does not, "meets the threshold, not significant"; otherwise "miss (descriptive)".
- P3: "holds robustly" iff the Clopper-Pearson interval lies inside [0.05, 0.40]; "holds but CI crosses" if only the point lies inside; otherwise a miss.
- P5: "holds (descriptive)" iff the mean gap is at least 0.01 and the adjusted p is below 0.05.
- No prediction is a claim about LLM agents or people. A "hold" of P1 is read only as "the loop found a member better than the author's seed on the validation context", never as "the rules are better": the exam is the test of that.

## Not testable by design

Proof verdicts, the lint, the redundancy check (z3), the protection checks on a frozen rule set, the filter's behavior on the seeds (all five pass): deterministic, reported as passes or failures with no interval.

## Limits stated now

Scripted agents; 6-run contexts are noisy, so an elite can be the winner of a noisy draw (the gap is meant to show it); the same 35 personas appear in training and validation (only the pairings differ); liberty at k = 2 and week-0 and week-52 snapshots does not see a months-long trap (docs/results/household-liberty.md), so the liberty objective cannot protect against it by itself and `no_fail` and pleasure must; liberty penalizes an exit that can carry the whole pot, which pushes toward exit-split cards (a property of the measure, not a finding about people); the imposed seed v2.2 rule sets have no negotiated pot terms; 16 lines.

## Amendments

(none yet)
