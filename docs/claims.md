# Claims register

Predictions must be committed before runs. Do not edit a prediction after its run starts; add a new row or an amendment note instead.

Status words: held, missed, null (ran, no effect), mixed, running, untested, process, superseded. Statuses updated 2026-11-10 from the results files; prediction wording is unchanged. Index of every run: docs/results/README.md.

## Active

| ID | Claim | Status | Evidence | Sources |
|---|---|---|---|---|
| C1 | Loop (a): under the refinement loop (ADR 0003, ADR 0005), new seams per round decrease across rounds toward a plateau, on at least 3 seeds, without the bloat guard tripping | untested with LLM agents. Scripted-agent proxies only: the fishery evolution falls by exhaustion (v1) and misses its fresh-adversary prediction (v2) | docs/results/evolve.md, docs/results/evolve-v2.md (not tests of C1: scripted agents, no LLM patcher) | docs/pitch.md |
| C2 | Loop (b), ADR 0005: the author's "not what I meant" moments per round decrease toward a plateau, one curve per oracle version, with a preregistered way to tell real convergence from author fatigue or a narrowing conversation | untested. Two moments are recorded as the first data points: the seed read-back and the pot-negotiation read-back. No curve yet; the fatigue check is not designed | experiments/changes.jsonl (19:55 and 20:15), docs/seeds/author-household-norms-2026-11-10.md | ADR 0005 |
| C1-bloat | Rule count grows sublinearly in rounds and agent action space stays above a preregistered floor | untested for LLM loops. Scripted fishery runs: no bloat (cards fall from about 4.3 to about 3; elites 1 to 4 cards), but the tie-break favours fewer cards | docs/results/evolve.md, docs/results/evolve-v2.md | ADR 0003 decision 7 |
| N1 | No published work measures the per-round rate of new gate-passing intent violations ("seams") in a solver-checked, LLM-patched rule loop for a multi-agent LLM commons, with the patcher blinded to an independent environment-plus-frozen-judge oracle, and diffs the written rules against rules mined from traces. "LLM patches rules, solver rejects conflicts" alone is not claimed (VEPA, AutoCedar do it) | narrowed, V1 pass (2026-11-10). Re-run the prior-art check before any write-up | docs/prior-art/2026-11-10-v1-convergence.md | ADR 0003 |
| D2a | Under the format experiment (ADR 0004), ADICO ties STRUCT on outcomes and seam curve | draft prediction, untested - finalize and commit before the format run (ADR 0004) | none | ADR 0004 |
| D2b | ADICO beats STRUCT on mined-norm expressibility, because it separates sanctioned rules from unsanctioned norms and names the sanctioner | draft prediction, untested - finalize and commit before the format run (ADR 0004) | none | ADR 0004 |
| D2c | TEXT shows more seams and more post-translation failures than both gated formats | draft prediction, untested - finalize and commit before the format run (ADR 0004) | none | ADR 0004 |
| D2d | F-EN (English-like controlled sentences compiling to the same cards and gate) ties F-ADICO on outcomes and seam curve and beats ADICO YAML on the card-only reader test (V2b: lossless round trip on 6 cards; reader test not yet run, gloss caveat in ADR 0004) | draft prediction, partly supported: the round trip and gate agreement held (V2b 4 of 4). The reader test is untested | docs/results/v2b.md | ADR 0004 |
| SI1 | Stand-in study (ADR 0006): rank agreement between Jev swarms and LLM swarms over ~50 rule sets is moderate (Spearman rho near the preregistered threshold of 0.7, author to confirm) | draft prediction, untested. Jev is one rung of the live ladder, which is a different test | none | ADR 0006 |
| SI2 | Jev swarms look more orderly than LLM swarms: lower behavior spread (entropy of actions per state) | draft prediction, untested | none | ADR 0006 |
| SI3 | Jev swarms find fewer seams and show fewer emergent norms than LLM swarms | draft prediction, untested. The live ladder gives a first look at Jev's seam rate | none | ADR 0006 |
| IT1 | Inventive seams (ADR 0007): below some agent capability there are zero inventive seams; above it they appear. The threshold and its price are the result | running. Finalized for the capability arm (six models, L1 to L5, cap $12); no result yet. Scripted calibration held: only the out-of-model gifter fixture is classed inventive | docs/results/ladder-live-prereg.md, docs/results/seam-ladder.md | ADR 0007 |
| ML1 | Model ladder (ADR 0007): rules evolved against a cheaper model transfer to the next rung up but not two rungs up | untested. Not covered by the capability arm; needs evolution against each rung and its own prereg and cap | docs/results/ladder-live-prereg.md (Finalization) | ADR 0007 |
| MU1 | Two modes (ADR 0011): norms that are robust across peer and delegate modes exist. We report where the modes split | draft prediction, untested. Modes are not built | none | ADR 0011 |
| AP1 | The author's seed norms show less misappraisal (gap between appraisal and counterfactual actual quality) than norms without their features | draft prediction, untested. Needs version 3 (appraisal, counterfactual runs). The seed v2 run measured suffering and dissolution, not misappraisal | none | ADR 0011 |
| DM1 | A delegate that exploits its principal's appraisal biases (sunk cost, creeping normality) is detectable as a seam | draft prediction, untested. Needs version 3 | none | ADR 0011 |
| FX1 | Process requirement (ADR 0007): the final exam (held-out conditions, unseen agent model, unused judge rubric version) is defined and committed before the first evolution run, used once, and never fed back into selection or tuning | household exam defined and committed (2026-11-10, docs/results/household-exam-prereg.md); fishery exams were separate. Process held so far: the household exam is defined, not run. The fishery exam 1 was seen before v2 and is reported as seen | docs/results/household-exam-prereg.md, docs/results/evolve-v2.md | ADR 0007 |
| FX2 | The household exam (docs/results/household-exam-prereg.md) is used exactly once, after evolution finishes; its result is reported whatever it is | process requirement, not yet run | docs/results/household-exam-prereg.md | ADR 0007 |

## Preregistered experiments (rows added 2026-11-10)

One row per prereg file. The prediction text is in the prereg file. Counts are rows of that file's table as scored in the results file. Added after the runs, so they carry no wording of their own beyond a short label.

| ID | Prereg and what it predicted | Status | Evidence |
|---|---|---|---|
| V2 | docs/results/v2-prereg.md: gate, oracle, patch checks and miner behave on a planted-seam fishery | held, 4 of 4 (one card fixed after its first run) | docs/results/v2.md |
| V2b | docs/results/v2b-prereg.md: English surface is lossless and the gate agrees | held, 4 of 4 | docs/results/v2b.md |
| HH1 | docs/results/household-prereg.md: the trap fails the proofs, a freedom and cooperation trade-off exists | mixed, 3 held and 2 missed. Trap fails the proofs; the trade-off is trivial | docs/results/household.md |
| SL1 | docs/results/seam-ladder-prereg.md: each scripted agent finds exactly the seams at or below its depth | held, 4 of 4 (calibration only) | docs/results/seam-ladder.md |
| RD-VPGG | docs/results/vpgg-prereg.md: the pipeline rediscovers Hauert et al. 2002 | missed on one clause: 4 held, 1 missed; not rediscovered by the committed rule (no cycles) | docs/results/vpgg.md |
| RD-BARG | docs/results/bargaining-prereg.md: the pipeline rediscovers Rubinstein and the outside-option principle | held on theory, 3 held and 1 missed (frontier clause 4b); rediscovered by the committed rule | docs/results/bargaining.md |
| EM1 | docs/results/empowerment-prereg.md: empowerment agrees with the hand-made freedom score | mixed, 8 held and 1 missed (VPGG 11 of 15, not 14 of 15) | docs/results/empowerment.md |
| EV1 | docs/results/evolve-prereg.md: the fishery evolution loop, seam curve falls, elite overfits | mixed, 3 held, 1 missed, 1 mixed. The curve fell by exhaustion; objectives saturated | docs/results/evolve.md |
| EV2 | docs/results/evolve-v2-prereg.md: fresh-adversary prevalence falls, varied training shrinks the exam gap | mixed, 3 held and 2 missed. Varied gap smaller in 6 of 9 pairs by the threshold (weak) | docs/results/evolve-v2.md |
| HH2 | docs/results/household-v2-prereg.md: hedonic model gives a trade-off; the author seed beats baseline | missed on the substance, 2 held and 3 missed | docs/results/household-v2.md |
| HH3a | docs/results/household-v3a-prereg.md: pressing personas create a trade-off; the no-control seed helps the partner | missed, 2 held and 3 missed (primary of 3 failed, secondary held) | docs/results/household-v3a.md |
| SV2 | docs/results/household-seed-v2-prereg.md: binding commitments trap partners and dissolve fewer households | mixed, 5 held and 2 missed. Binding is a null: 0.0003 difference | docs/results/household-seed-v2.md |
| LB1 | docs/results/liberty-prereg.md: equal liberty plus non-domination (ADR 0014) | mixed, 6 held and 3 missed. VPGG missed badly (4 of 15) | docs/results/liberty.md |
| LB2 | docs/results/liberty-v2-prereg.md: interference vs withdrawal repairs VPGG without breaking the toy | mixed, 6 held and 4 missed. VPGG sum +5.263 bits; V1 reversed in 2 compositions | docs/results/liberty-v2.md |
| PR1 to PR4 | docs/results/ladder-propensity-prereg.md: persona play finds fewer seams than red-team play (P1), inventive threshold the same or higher (P2), most seams on L4 (P3), fewer refusals (P4) | running. Comparison only after the capability arm finishes | docs/results/ladder-propensity-prereg.md |

## Follow-ups (not preregistered)

| ID | Claim | Notes |
|---|---|---|
| F1 | Crowding out: agents under a hard gate fail worse than sanctioned agents when the gate is removed or misses a case | from the 2026-11-10 interview; unseen in prior art. Untested; backlog (docs/plan.md) |
| F2 | AI-patched and human-patched specs converge to different plateaus | arm option, ADR 0003 decision 4. Untested |
| F3 | The de jure vs de facto distance predicts collapse earlier than violation counts | replaces E3. Untested; the miner exists (V2) but no LLM traces yet |

## Superseded 2026-11-10 (ADR 0003)

S1 (single agent, gated vs free-text; now replication-grade, see Agent-C and Winston et al.), E0, E1, E2, E3, E4. Original wording is in git history at commit 78de81b and in RATIONALE.md's history.
