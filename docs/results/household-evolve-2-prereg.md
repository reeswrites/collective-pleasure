# Household evolution run 2: preregistration (ADR 0012, ADR 0014 amendment, ADR 0015)

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: written and committed before the first run-2 evolution run. Nothing here is a result. Scripted persona-driven agents only. Model API calls: none. Code: `scripts/household_evolve2_run.py`, `src/mar/world_api.py`, `src/mar/evolve.py`, `src/mar/empowerment.py`, `src/mar/liberty.py`, `src/mar/loss_report.py`; tests `tests/test_evolve_household2.py`. Parent: docs/results/household-evolve-prereg.md and household-evolve.md (run 1), docs/results/household-loss-report.md. The final exam for this run is a NEW exam, defined and committed first: docs/results/household-exam-2-prereg.md (exam 1 is spent).

**Can be about / cannot be about.** Can be about: what a rule-search loop does to scripted agents in a stated toy world, when its liberty score counts normative powers and its episodes are a lifetime long with the pleasure levers on; exact facts (proof and lint checks, which cards an elite holds). Cannot be about (docs/limits.md): people, LLM delegates, or a partner who adapts (limit 1: the partner is a script, so "commitment pays later" is a property of the modeled payoff stock); isolation as the cause of harm (2); crowding out (3); a number as such (5: the lever parameters are assumed, so only patterns count); other authors or models (6); felt experience (10). Limit 8 (a verdict that cannot happen) is addressed by the free check below. Limits 4, 7 and 9 are not touched (no negotiation, no exit-moves-the-egoist cell, no ladder).

## Purpose and claim

Run 1 found elites that dropped every `may` card of the author's seed and with it the commitment mechanics (bind a stay, bind a request, gift): 0 of 16 kept any. The author said that was "not what I meant" and approved three fixes (loss report, liberty counts normative powers, lifetime horizon with levers on). Run 2 tests whether the fixes change what the loop keeps: **the key prediction is that elites keep commitment powers because the test now values them** (liberty counts them; commitment pays later under the levers). It also re-asks run 1's questions (does the loop beat the author's seed on the validation context; do elites keep no-veto and free exit; what does the filter reject). Claims: FX1 / FX2 for the exam. A decision it can change: whether the evaluator, not the loop, was the problem.

## Design

- **World and rule sets.** As run 1 (`HouseholdEvolveWorld`; imposed rule sets; same five seeds: `author_seed_v2_bindable`, `author_seed_v2_free_exit`, `baseline`, `needs_duty`, `no_pressure_wall`; same operators, filter, objectives, elite rule, 16 lines, population 8, 6 offspring, 6 generations after generation 0, 6 runs per candidate per generation, hard cap 16 cards). Changes, all three approved by the author:
  1. **Liberty counts normative powers** (`HouseholdWorld(powers=True)`; ADR 0014 amendment): commit_stay, commit_request and give are in the menu and key, and exist only where a `may` card names them. Liberty is still the lower partner's bits at k = 2, weeks 0 and 52.
  2. **Lifetime horizon:** every run is 156 weeks (run 1 drew 104, 130 or 156). The loss report (docs/results/household-loss-report.md) is part of the evaluator's output for every elite.
  3. **All four pleasure levers ON** for every run (adaptation, ritual, commitment, network; `LeverConfig` defaults; ADR 0016). The commitment lever only pays where a commitment exists, which needs a card that names it.
- **Training and validation:** the same varied training distribution (a fresh 6-run context per generation, every member re-scored; shocks 0.5x to 1.5x, starts in [-0.1, 0.1], simulation seeds 100 to 899). The training pool excludes BOTH held-out sets: exam 1's six ids and exam 2's six (`DENYLIST2`, the mechanical rule of the exam-2 document; a test recomputes it): 29 personas remain. Nothing else from exam 2 appears in any run-2 code, config, test or log (a test greps for its seeds, shock values, horizon and starts). Validation is the same hash-chosen fifth of the pairings (never selected on), 30 runs, seed 777, 156 weeks, levers on.
- **Unit of resampling:** the evolution line (16; seeds 1 to 16). At most 4 worker processes (shared machine).
- **A power is "kept"** iff the elite has a `may` card naming that aim (commit_stay, commit_request, give), because the world switches the mechanic on only then (`loss_report`, `household.MECH_AIMS`).
- **Runtime.** One generation of one line cost about 35 CPU-seconds in an exploratory timing pilot (one line, one generation, serial; excluded from the data). 16 lines x 7 scored generations plus validation is about 100 core-minutes: **about 25 minutes of wall time on 4 idle cores**; the machine is shared, so wall time will be longer.
- **ASSUMED (flagged):** everything run 1 assumed; the power modeling (a stay promise blocks the member's own leave for 13 weeks inside the window, a gift moves 3 units, a request promise is a flag; the powers need only the member present, found in testing: ADR 0014 note); the lever parameters; the 156-week lifetime; the validation context; P3 margins (pleasure 0.02, no_fail 0.05, liberty 0.25 bits, cooperation 0.02).

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

One line, seed 501 (never used in the confirmatory run), 1 generation after generation 0, serial, to time the run: 70 s for 2 generations; its elite carried B4-may-see, D1-needs-first, E1-at-most-half and E2-at-least-half, no commitment card (one generation says little). Before this pilot, in a unit test of the power modeling, a version in which powers needed the partner present made liberty FALL for a rule set that kept them; that was fixed before any run (ADR 0014 note). No effect size or spread was estimated from it.

| Quantity | Pilot effect | Pilot sd of the unit | Source file |
|---|---|---|---|
| (none estimated; timing only) | n/a | n/a | runs/household-evolve-2/pilot.jsonl |

## Power check (required)

Run 1's table applies: 16 lines, exact one-sided binomial rejecting at 12 of 16 (p = 0.038), power 0.63 at a true rate of 0.75, 0.92 at 0.85. Counting predictions P1, P3 and P5 are **DESCRIPTIVE**. P2 compares run 2's counts with run 1's 0 of 16 by Fisher's exact test (one-sided): 8 of 16 against 0 of 16 gives p = 0.0013, so P2 is powered for a large effect (it has its own threshold, 8 of 16 for each power). P4 is a mean over 16 lines with unknown spread: DESCRIPTIVE.

| Prediction | Margin | Lines | Power at the assumed rate | Mark |
|---|---|---|---|---|
| P1 | 12 of 16 | 16 | 0.63 at 0.75 | DESCRIPTIVE |
| P2 | 8 of 16 each (vs 0 of 16) | 16 | high for a large shift | confirmatory for the threshold; the verdict still needs Holm |
| P3 | 12 of 16 | 16 | 0.63 at 0.75 | DESCRIPTIVE |
| P4 | +0.01 | 16 | unknown spread | DESCRIPTIVE |
| P5 | 12 of 16 | 16 | 0.63 at 0.75 | DESCRIPTIVE |
| P6 | interval inside 5 to 40% | thousands of proposals | n/a | interval rule |

## Predictions

| ID | Quantity (formula) | Unit of resampling | Comparison and threshold | Test | Alpha | Correction family | Interval reported |
|---|---|---|---|---|---|---|---|
| P1 (KEY) | Share of the 16 elites that keep at least one of the three powers (a `may` card on commit_stay, commit_request or give) | line | >= 12 of 16 (run 1: 0 of 16) | exact one-sided binomial vs 0.5 | 0.05 | Holm across P1, P2a, P2b, P2c, P3, P4, P5 | Clopper-Pearson 95% |
| P2 | Per power (a: commit_stay, b: commit_request, c: give), number of elites keeping it | line | each >= 8 of 16 | one-sided Fisher exact, run 2 vs run 1's 0 of 16 | 0.05 | same | Clopper-Pearson 95% per power |
| P3 | Share of lines whose final front has a member that beats the author's seed on the validation context by the margin on >= 1 objective (liberty counted with powers) and loses none beyond its margin | line | >= 12 of 16 | exact one-sided binomial vs 0.5 | 0.05 | same | Clopper-Pearson 95% |
| P4 | Mean over lines of (elite validation pleasure, lifetime, levers on) minus (the author's seed's) | line | >= +0.01 | one-sided paired sign-flip permutation against 0 | 0.05 | same | 95% percentile bootstrap |
| P5 | Share of elites that keep both core protections (no veto violated in every state; a leave at the equal split never blocked) | line | >= 12 of 16 (run 1: 12 of 16) | exact one-sided binomial vs 0.5 | 0.05 | same | Clopper-Pearson 95% |
| P6 | Share of proposed mutants (duplicates, oversize, inapplicable excluded) the pre-run filter rejects | proposed mutant (pooled) | between 0.05 and 0.40 | interval rule | n/a | not in the family | Clopper-Pearson 95% |

Reported, no threshold: counts per power against run 1; the loss-report summary for every elite (powers lost, mechanics off, backwards-reading cards); elite minus author's seed per objective; cards that recur.

## Can every verdict happen? (required; run BEFORE any confirmatory run)

Free check: `uv run pytest -q tests/test_evolve_household2.py -m "slow or not slow"` (5 tests, run before this commit; all pass). The counting and verdict functions are the ones the analysis uses (`scripts/household_evolve2_run.py`).

- **Every verdict is reachable.** P1 / P2 "miss": the real run-1 frozen elites give 0 of 16 on every power (`p1_count`, `p2_counts` on docs/results/household-evolve-elites). P1 / P2 "hold": the author's seed repeated 16 times gives 16 of 16. The labels "holds", "meets threshold, not significant" and "miss" are each produced by `verdicts(...)` on synthetic counts (hold: 16 of 16 and p small; miss: all zeros; the threshold-only label on 12 of 16 with a large p). P3 hold and fail: a synthetic member 0.5 bits better than the seed, and the seed itself. P5 hold and fail: the author's seed (both protections) and the trap rule set (neither). P6: a 10% rejection (holds robustly) and 80% (miss).
- **Every prediction clause can fail.** P1 failed for run 1's elites (0 of 16), so the clause is a real test and not a property of the code. P2's three clauses are separate counts, each failing at 0. P4 fails at a negative mean (-0.01 in the synthetic call). No clause holds whatever the agents do.
- **Open cells.** The key prediction needs elites able to keep a power: a `may commit_stay`, `may commit_request` or `may give` card exists in the seeds (`author_seed_v2_bindable` and `free_exit` carry some), in the patch library (the same seed cards) and nowhere else, so a power can be kept only if a seed lineage or a `patch` of a seed card survives; it is reachable (the seed itself holds all three) but not guaranteed by the operators. The `drop` operator can remove it, so the loop can lose the powers again.
- **The metric can see the mechanism.** Liberty with powers: for the bindable seed, liberty at the initial state is 3.26 and 0.92 bits (the two partners) with the powers counted and the cards present, against 2.96 and 0.51 with the same rules minus the power cards, and identical with the flag off (pinned in `tests/test_liberty.py`; the check in `test_the_metric_sees_the_mechanism`). The commitment lever: it pays through the payoff stock only where commitments exist, which needs the card (ADR 0016; the loss report shows which elites lost it). One thing the metric cannot see: a power that is kept but never exercised by the scripted partners still raises liberty (an option) while adding nothing to pleasure.

| Verdict or clause | Free check | File | Result |
|---|---|---|---|
| P1 / P2 miss | run-1 elites through `p1_count`, `p2_counts` | tests/test_evolve_household2.py | reached (0 of 16) |
| P1 / P2 hold | the seed x 16 | same | reached |
| P3 hold / fail, P5 hold / fail, P6 both | synthetic and trap/seed inputs | same | reached |
| "meets threshold, not significant" | 12 of 16 and a large Holm p | same | reached |
| P4 fail | synthetic negative mean | same | reached |
| power visible to liberty | seed vs seed minus the power cards | tests/test_liberty.py, tests/test_evolve_household2.py | reached |

## Verdict rule

P1, P3, P5: "holds (descriptive)" iff the count meets its threshold and the Holm-adjusted p < 0.05; "meets threshold, not significant" if the count meets it and the adjusted p does not; else "miss (descriptive)". P2 holds iff all three counts are at least 8 of 16 and each adjusted Fisher p < 0.05. P4 holds (descriptive) iff the mean is at least +0.01 and the adjusted p < 0.05. P6 holds robustly iff the interval lies inside [0.05, 0.40]. The key prediction is P1 together with P2: "elites keep commitment powers" is rediscovered iff both hold. The comparison with run 1 is the Fisher test; run 1's counts are exact (0 of 16 each, loss report).

## Not testable by design

Proof and lint verdicts, the redundancy check, the protection checks, the power-card counts on a frozen rule set: deterministic, reported as facts without intervals.

## Limits stated now

Scripted agents; the partner never learns (limit 1), so "commitment pays later" is the modeled payoff stock, not people; the pleasure measure includes lever terms but the commitment friction goes to suffering, not to pleasure (docs/results/pleasure-levers.md correction), so pleasure alone cannot show an early cost; liberty counts a power as one reachable key like any option; the elite pick still weighs liberty (6 bits = 1.0), and with powers counted liberty may exceed 6 and saturate; 6-run contexts are noisy; 16 lines; imposed rule sets; training and validation share the same 29 personas.

## Amendments

(none yet)
