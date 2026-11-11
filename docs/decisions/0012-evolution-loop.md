# 0012. The evolution loop: population, proof filter, Pareto selection, world interface

Status: accepted (2026-11-10)

## Context

ADR 0005 named the core: evolve alignment norms by mutating interpretable rules, proofs as the selection filter, the patcher as an operator, the seam curve as the judge, one lineage first and a population later. ADR 0007 asked for a held-out final exam. The engine itself did not exist. This ADR records the first version (src/mar/evolve.py, src/mar/world_api.py). Results: docs/results/evolve.md. Nothing here is a claim about LLM agents.

## Decisions

1. **Population of rule sets (lists of ADICO cards), not one lineage.** mu = 10, lambda = 10, 12 generations in the first run. Chosen so the whole preregistered run fits in about 4 minutes.
2. **Proof filter before any run.** A mutant is kept only if every check passes at k = 3; "open" is rejected. Rejected mutants are never evaluated. Rejections are logged by check and by operator.
3. **Mutation operators on cards:** tighten or loosen a numeric bound, flip deontic, add a condition, drop a card, add a card from a scripted patcher that sees a failing trace and the cards and never the oracle.
4. **Selection:** NSGA-II style (non-dominated sorting, crowding, constraint-dominance on a yield floor), plus a bloat tie-break (fewer cards first) and a hard card cap.
5. **World interface** (`world_api.World`): load_spec, check_spec (pass, fail, open with k), run, score, seams, plus mixes, conditions, vocab, propose_patch, feasible. The fishery adapter reuses existing modules; none was modified. The household plugs in by implementing the same interface.
6. **Held-out exam** is separate code (`final_exam`), different regrowth, longer episodes, unseen agent mixes, run once after evolution; `evolve()` has no exam argument (tested).
7. **Determinism and logging:** one seeded RNG; one JSONL record per generation under runs/evolve/ (proposed, duplicates, proof-rejected by check and operator, new seams, front, card counts, hypervolume).

## Consequences

- First run (docs/results/evolve.md): the loop works, proofs reject 14% of checked mutants, the elite stays small, but the objectives saturate (no real frontier), the seam curve falls partly by exhaustion of a finite key set, and the elite overfits the training test (exam seam_free no better than the seed spec).
- Next design needs objectives with real tension, a seam key that does not exhaust (for example seam_depth classification), a redundancy or subsumption check beside the proofs, and a harder training mix set. Household adapter requirements are listed in the results file.
- ASSUMED choices are listed in docs/results/evolve.md. Surprises and the negative-results line are to be added to docs/surprises.md and docs/negative-results.md by the owner of those files.

## Amendment 2026-11-10 (v2)

Written after the second run (docs/results/evolve-v2.md; preregistration docs/results/evolve-v2-prereg.md). Changes to the engine, all opt-in through `Config` so v1 behaviour and its tests are unchanged:

1. **Seam measure is per-candidate exploit prevalence against adversaries redrawn each generation** from a fixed 96-mix pool (`Config.adversaries`, `FisheryWorldV2.context`). It cannot fall by exhaustion. Every population member is re-scored under each generation's setting before selection; a disjoint audit sample measures the generation's elite only (`Config.audit`).
2. **Two training arms:** `arm="fixed"` (v1 conditions) and `arm="varied"` (conditions drawn per generation from a training distribution that excludes the held-out exam's conditions).
3. **Fourth proof-filter reason: redundancy** (`src/mar/redundancy.py`, `Config.redundancy`). A must / must_not card implied by the conjunction of the others over the bounded domain (catch -100..100) is redundant; mutants containing one are rejected as `e_redundancy`, except `patch` mutants, where the redundant card is pruned instead. Logical implication only; sanctions and glosses are ignored. This catches the v1 F3 / flipped-F4 restatement.
4. **Fourth objective: efficiency** (continuous), with a 4-D hypervolume. The front stayed non-trivial (3 to 4 vectors) rather than collapsing to a corner.
5. **A new held-out exam (exam 2)** (`final_exam(world, spec, "exam2")`) and a common reference score (`reference_scores`) for gaps. `evolve()` still has no exam argument (tested).

Outcome in brief (see the results file): redundancy flagged 26% of proof-passing mutants and no elite holds a redundant card; varied training gave a smaller exam-2 gap in 5 of 9 pairs (suggestive, overfitting remains large); the prevalence-falls prediction and the both-arms path-dependence prediction were not met. The run was sized for runtime (population 8, 8 generations, prereg Amendment 1).

## Amendment 2026-11-10 (household)

Written after the first household run (docs/results/household-evolve.md; preregistration docs/results/household-evolve-prereg.md; exam docs/results/household-exam.md). The household plugs into the loop, with changes that leave the fishery path and its tests untouched:

1. **Household world adapter** (`world_api.HouseholdEvolveWorld`, `evolve.evolve_household`): a separate loop function rather than a `World` Protocol implementation, because a household "mix" is a persona pairing under drawn conditions and not an agent list. Same machinery: non-dominated sorting, crowding, bloat tie-break (fewer cards first), one seeded RNG, JSONL log per generation.
2. **Operators on household cards** (bound, flip, add_condition, drop, sanction, patch from a library of the hand rule sets, and `add_term`, which swaps one negotiated-pot term of ADR 0013 compiled by `negotiation.compile_bundle`). The patcher sees counts of what happened in the parent's runs, never an objective.
3. **The pre-run filter is lint (`mar.lint`) plus the five household proof checks plus a household redundancy check** (`hh_redundant_cards`, z3 over the household bounds, must / must_not partner cards only, logical, sanctions and glosses ignored). Findings the parent already had are inherited; anything new rejects. Seeds must pass or the run stops.
4. **Four objectives** (mean pleasure, share of runs without a non-offsettable-suffering failure, liberty v2 as the lower partner's bits, cooperation), **varied training** (a fresh 6-run context of persona pairings and conditions per generation, every member re-scored on it), a training set that excludes the exam's six held-out ids (denylist only; a test recomputes them from the exam's SHA-256 rule), and a validation context from a hash-chosen fifth of the pairings for the overfitting gap. The per-line elite is fixed in advance (`pick_elite_h`).
5. **Liberty v2 enters the household** through `empowerment.HH_CLASS` (every menu action classed interference, withdrawal or own, with a rationale; ADR 0014 decision 3) and `liberty.household_run_liberty`. A whole-pot exit (take 100) is classed interference, which is what makes liberty the objective that most moves the elites.

Outcome in brief: 16 lines. The loop found members that beat the author's seed in all 16 lines (liberty and cooperation, not pleasure or the failure share); the filter rejected 13.3 percent of proposed mutants (redundancy, the exit proof check and the lint's no-exit check the main reasons); no front held a trade-off pair of 0.05; no train-minus-validation gap showed. On the held-out exam, 3 of 16 elites pass the floor against the best of 12 hand-written rule sets, none beats it by more than the margin on pleasure or cooperation, and all 16 elites dropped the seed's permission cards and with them the commitment mechanics. The elites' lead over the author's seed held on the exam (unlike the fishery's exam result). The fishery lessons that carried over: a redundancy check is needed (it rejected or flagged 57 mutants), and the elite is a moving pick under varied training. New: the objective that is cheapest to improve (liberty by capping the exit) dominates the search; a rule that reads backwards survives if the four scores do not move; the pass-the-floor rule is hard on every rule set (none of the 12 hand-written comparators passes it against the best of the 12).
