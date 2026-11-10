# Claims register

Predictions must be committed before runs. Do not edit a prediction after its run starts; add a new row or an amendment note instead.

## Active

| ID | Claim | Status | Evidence | Sources |
|---|---|---|---|---|
| C1 | Loop (a): under the refinement loop (ADR 0003, ADR 0005), new seams per round decrease across rounds toward a plateau, on at least 3 seeds, without the bloat guard tripping | untested - preregister exact fit, rounds, seeds and thresholds before V4 | none | docs/pitch.md |
| C2 | Loop (b), ADR 0005: the author's "not what I meant" moments per round decrease toward a plateau, one curve per oracle version, with a preregistered way to tell real convergence from author fatigue or a narrowing conversation | untested - preregister before V4 | none | ADR 0005 |
| C1-bloat | Rule count grows sublinearly in rounds and agent action space stays above a preregistered floor | untested - preregister with C1 | none | ADR 0003 decision 7 |
| N1 | No published work measures the per-round rate of new gate-passing intent violations ("seams") in a solver-checked, LLM-patched rule loop for a multi-agent LLM commons, with the patcher blinded to an independent environment-plus-frozen-judge oracle, and diffs the written rules against rules mined from traces. "LLM patches rules, solver rejects conflicts" alone is not claimed (VEPA, AutoCedar do it) | narrowed, V1 pass (2026-11-10) | docs/prior-art/2026-11-10-v1-convergence.md | ADR 0003 |
| D2a | Under the format experiment (ADR 0004), ADICO ties STRUCT on outcomes and seam curve | draft prediction - finalize and commit before the format run (ADR 0004) | none | ADR 0004 |
| D2b | ADICO beats STRUCT on mined-norm expressibility, because it separates sanctioned rules from unsanctioned norms and names the sanctioner | draft prediction - finalize and commit before the format run (ADR 0004) | none | ADR 0004 |
| D2c | TEXT shows more seams and more post-translation failures than both gated formats | draft prediction - finalize and commit before the format run (ADR 0004) | none | ADR 0004 |
| D2d | F-EN (English-like controlled sentences compiling to the same cards and gate) ties F-ADICO on outcomes and seam curve and beats ADICO YAML on the card-only reader test (V2b: lossless round trip on 6 cards; reader test not yet run, gloss caveat in ADR 0004) | draft prediction - finalize and commit before the format run (ADR 0004) | V2b feasibility only: docs/results/v2b.md | ADR 0004 |
| SI1 | Stand-in study (ADR 0006): rank agreement between Jev swarms and LLM swarms over ~50 rule sets is moderate (Spearman rho near the preregistered threshold of 0.7, author to confirm) | draft prediction - finalize and commit before the first paid run | none | ADR 0006 |
| SI2 | Jev swarms look more orderly than LLM swarms: lower behavior spread (entropy of actions per state) | draft prediction - finalize and commit before the first paid run | none | ADR 0006 |
| SI3 | Jev swarms find fewer seams and show fewer emergent norms than LLM swarms | draft prediction - finalize and commit before the first paid run | none | ADR 0006 |
| IT1 | Inventive seams (ADR 0007): below some agent capability there are zero inventive seams; above it they appear. The threshold and its price are the result | draft prediction - finalize and commit before the first paid run | none | ADR 0007 |
| ML1 | Model ladder (ADR 0007): rules evolved against a cheaper model transfer to the next rung up but not two rungs up | draft prediction - finalize and commit before the first paid run | none | ADR 0007 |
| MU1 | Two modes (ADR 0011): norms that are robust across peer and delegate modes exist. We report where the modes split | draft prediction - finalize before the run | none | ADR 0011 |
| AP1 | The author's seed norms show less misappraisal (gap between appraisal and counterfactual actual quality) than norms without their features | draft prediction - finalize before the run | none | ADR 0011 |
| DM1 | A delegate that exploits its principal's appraisal biases (sunk cost, creeping normality) is detectable as a seam | draft prediction - finalize before the run | none | ADR 0011 |
| FX1 | Process requirement (ADR 0007): the final exam (held-out conditions, unseen agent model, unused judge rubric version) is defined and committed before the first evolution run, used once, and never fed back into selection or tuning | process requirement - commit before the first evolution run | none | ADR 0007 |

## Follow-ups (not preregistered)

| ID | Claim | Notes |
|---|---|---|
| F1 | Crowding out: agents under a hard gate fail worse than sanctioned agents when the gate is removed or misses a case | from the 2026-11-10 interview; unseen in prior art |
| F2 | AI-patched and human-patched specs converge to different plateaus | arm option, ADR 0003 decision 4 |
| F3 | The de jure vs de facto distance predicts collapse earlier than violation counts | replaces E3 |

## Superseded 2026-11-10 (ADR 0003)

S1 (single agent, gated vs free-text; now replication-grade, see Agent-C and Winston et al.), E0, E1, E2, E3, E4. Original wording is in git history at commit 78de81b and in RATIONALE.md's history.
