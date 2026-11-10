# Evolution loop on the fishery: results

Status: first offline run of the core engine (ADR 0012). Scripted agents, no model call. Predictions: docs/results/evolve-prereg.md (commit ec21084; one erratum, 9ac39b5, made before any evolution run). Run: `uv run python scripts/evolve_run.py` (wall time 217 s on a laptop; under the 10 minute budget, so no setup was shrunk). Report: `runs/evolve/report.html` (gitignored, regenerate with the script); logs `runs/evolve/<ruleset>-s<seed>.jsonl`. Tests: `uv run pytest -q tests/test_evolve.py` (14 pass).

## Prereg vs actual

| # | Preregistered | Actual | Verdict |
|---|---|---|---|
| 1 | Proof-rejection share 10% to 45% pooled, >= 5% each run | 14.0% pooled; per run 9.8% to 17.8%. Most rejections: bound steps 106, flips 77, add-condition 6 (of 539 / 178 / 294 proposed). Failed checks: deadlock and repair path (same mutants), conflict | Met (every run is above 5%) |
| 2 | New seams per generation fall (last third <= 0.5 x first, >= 7/9); fit plateau c <= 0.5; front prevalence lower at g12 in >= 7/9 and drops by >= 1.0 | Decreasing 9/9; fit r = 0.3 (grid edge), c = 0.01 median, 9/9. Front prevalence lower in only 1/9, mean drop 0.16 | Discovery curve met; substantive companion NOT met (see below). Overall NOT met |
| 3 | Concave rule-count growth >= 7/9; elite <= 8 cards >= 8/9; elite yield >= 0.9 >= 8/9 | Concave 7/9; elite cards 3,5,2,3,4,2,1,3,4 (all <= 8); yield 1.0 in 9/9 | Met |
| 4 | Overfits: sustainability and seam_free gaps > 0.20, fairness gap <= 0.20 | Gaps (training minus exam): sustainability +0.50, seam_free +0.72, fairness -0.09. Exam elite minus exam seed: sustainability +0.07, fairness +0.07, seam_free -0.06 | Prediction (overfit) correct. By the "no overfitting" test: NOT met, i.e. reported as overfitting |
| 5 | v2 and minimal within 0.10; tight further than 0.10 or reported as convergence; HV CV <= 0.10 | All three rule sets end at the same mean vector (sustainability 1.00, fairness 0.84, seam_free 1.00); distances <= 0.001; HV CV 0.01 to 0.02 | Convergence (the branch the prereg allowed), but the directional guess (tight lags) missed. Script prints NOT met because it encoded the lag; the numbers above are the result |

## What actually happened

- **The seam curve fell**, but mostly by exhaustion. New seam keys: 11 to 15 at generation 0 (all the seed's and its mutants' seams), then 0 to 4 per generation with nothing structural after generation 4. The fit hits the grid floor r = 0.3. Candidate seam prevalence (mean seam keys per candidate) fell from about 7 at generation 0 to 1 to 4 at generation 12, with noise (some generations back up at 2 to 5 as loosening mutants reopen seams).
- **Prediction 2's companion test was badly defined.** "Front prevalence" is measured after selection, so the generation 0 front is already seam-free (0.0), and the test cannot show a drop. The candidate prevalence is the measure that should have been named. Reported as a prereg miss, not rewritten.
- **The objectives saturate, so there is no real frontier.** Every run's elite has sustainability 1.00, seam_free 1.00 and fairness 0.84. The front fills with 10 tied members from generation 3 (log: front_size 10), hypervolume moves only 0.829 to 0.854. Fairness 0.84 looks like a ceiling set by the training mixes (the exploiter mixes). So the "frontier movement" in this run is one small step to a corner, not a trade-off curve. This is the main weakness of this first design: the training scores are too easy to max. For the household, objectives must have a real tension (freedom vs cooperation).
- **Path dependence: none visible.** `tight` (infeasible start) escaped in every seed (one run ends with a single card, P1, a month cap of 40); `minimal` and `v2` end in the same place. Because the objectives saturate this says little.
- **The elite is mostly one idea:** a month cap of about 40 (P1) with F3 and F4, sometimes F2. It does well in training (doubling regrowth) and collapses under the exam (regrowth x1.5, 8 months, unseen agents): last_minute, tiny_hoarder and mixed_unseen all collapse in nearly every run. Exam seam_free 0.25 for the elite equals the seed spec's 0.25 (v2, minimal); only `minimal` seed 1 does better (0.50). Evolution under the training test did not buy exam robustness: the test was reverse-engineered, as the pitch predicts.
- **Bloat did not happen.** Mean cards per rule set falls from about 4.3 to about 3 in most runs. Part of that is the tie-break favouring fewer cards; the drift to F3 + F4 + P1 is partly that pressure, not only the test.
- **Surprise: a flip produced a duplicate.** Elites contain F4 flipped from `may` to `must` ("a fisher must harvest only when the catch is at least 0"), which is F3 restated. The proof filter passes it (no conflict, no deadlock) and the scores cannot tell, so semantic no-ops and redundancy are not caught. A redundancy check (subsumption) would help.
- **A tighten step can loosen:** "bound" mutations that clamp or hit a direction ambiguity were not examined; P1 in the elite appears as `catch > 1` (loosen) rather than `catch > 0`. Not a bug found, noted for the next pass.

## Charts (in runs/evolve/report.html)

Seam keys first seen per generation (thin per run, thick mean per seed rule set); candidate seam prevalence per generation; frontier scatter at generations 0, 4 and 12 across all runs, plus hypervolume per generation; proof-rejection share per generation with mean card count; held-out exam vs training bars (elite training, elite exam, seed exam); each final elite rendered with `english.render`. Light and dark, no network.

## ASSUMED choices (builder, revisit)

- Own copy of the fishery loop with a regrowth parameter (original hard-codes doubling); tested equal at x2.
- Seam key = (mix, finding kind): a finite set, so discovery counts must fall by exhaustion.
- Yield floor measured on the all-compliant mix only (prereg erratum); floor 0.8.
- Objectives and weights (sustainability, fairness, seam_free), operator weights, step sizes, population 10, 12 generations, bloat tie-break as the primary within-front order, hard cap 12 cards.
- Patcher adapter: one third the existing scripted month-cap-40 patcher, else a trace-derived cap or a stock reserve rule. Sanctions are not enforced by the fishery harness, so sanction fields are inert.
- Gloss and source of mutated cards are auto-generated (`evolved (op) | root source`).
- Elite = highest mean objective on the final feasible front.
- Proof rejection share counts proof-checked mutants (excludes duplicates and oversize).

## What the household adapter needs

Implement `world_api.World` for the household: `load_spec` (rules/household dirs), `check_spec` (household proof checks with k, mapped to pass/fail/open), `run(spec, agents, seed, conditions)` and a trace type, `score` returning freedom and cooperation (plus a feasibility floor, e.g. the household persists and agents can act), `seams` (household_oracle.seam_flag; seam_depth.classify_seam gives predicted / inventive and could replace the (mix, kind) key), `mixes("train"/"exam")` with persona and exploiter mixes and held-out shocks, `vocab()` of expressions and ranges for the card operators, `propose_patch(trace, spec, rng)` from a failing trace without the oracle, and `feasible`. `evolve.py` also assumes cards are `cards.Card` with numeric conditions; household cards with other condition shapes need matching `op_bound` and `op_add_condition` slots. Objectives must be chosen so they do not saturate (see above).

## For the other agent's files (not edited here)

Add a line to docs/negative-results.md: the seam-curve fall in the first evolution run is mostly exhaustion of a finite key set, and the evolved elite did not beat the seed spec on the held-out exam (seam_free 0.25 vs 0.25). Add to docs/surprises.md: objectives saturated so the frontier collapsed to a corner; a deontic flip produced a redundant duplicate that proofs cannot catch; "front prevalence" measured after selection is blind to the drop.

## Does and does not show

Shows: the loop runs end to end, deterministically, offline, with proofs gating mutants before any run, and logs everything. Does not show: that refinement converges on a meaningful frontier, anything about LLM agents, or exam robustness (it overfit).
