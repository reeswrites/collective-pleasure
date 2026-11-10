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
