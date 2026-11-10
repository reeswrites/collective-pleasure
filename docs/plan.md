# Plan

Status: pre-results. Direction set 2026-11-10 (ADR 0003, docs/pitch.md). Every slice ends in a pass/fail check that takes minutes to read. A failed check narrows or stops the project; that is a result, recorded in docs/negative-results.md.

## Slices

| Slice | What | Budget | Validation (pass / fail) |
|---|---|---|---|
| V0 | Prior-art check, repeated | done | docs/prior-art/2026-11-10.md: full pipeline not pre-empted; gating, prompt-vs-gate and conflict-checking are prior art |
| V1 | Adversarial novelty search on the convergence loop | hours | Done 2026-11-10: PASS with a narrower claim; no paper pre-empts the full design (docs/prior-art/2026-11-10-v1-convergence.md). Pass: no work measures seams-per-round convergence of a refinement loop for LLM agents with an independent oracle. Fail: narrow the claim to what survives, or stop |
| V2 | Done 2026-11-10: PASS (4 of 4 checks; scripted patch needed one card fix, docs/results/v2.md). The loop on a scripted mock agent: tiny fishery, ADICO cards to Z3 gate, planted seam (per-catch cap, no per-month cap), outcome oracle, scripted patch, solver patch checks | half a day | Pass: oracle flags the planted seam; patch closes it; solver rejects a deliberately conflicting patch; mined de facto rules equal the written ones under the gate |
| V3 | Instrument calibration with one real LLM agent (cheap open model), same harness | a day | Pass: all four V2 checks hold with a real model; measured $ and minutes per round. No claims about convergence |
| V4 | First curve: five-agent swarm, ~10 rounds, 3 seeds, LLM patcher, outcome oracle (judge rubric optional). Preregister C1 before the first run | two to three days | Result either way: slope, plateau with uncertainty, rule count per round. Bloat guard checked |
| V5 | One-page write-up with the curve; fresh-agent review council | a day or two | Council finds no claim beyond the evidence; card-only reader can follow every rule |

## Decisions waiting on the author

- At V4: keep the in-repo harness or port to GovSim (running GovSim locally needs the author's OK; ADR 0003 ASSUMED note).
- Before V4: model choice for agents and patcher, and the spend ceiling.
- After V4: whether to add the frozen LLM-judge curve, human-vs-AI patching arms, or the crowding-out follow-up.

## Superseded

The earlier milestones (ADICO to LTS export cross-checked against philosophy-engine; mCRL2 invariant; check_action gate in GovSim; S1; E0 and E2) are folded into V2 to V4 where needed or kept as follow-ups. mCRL2 is deferred until a slice needs bisimulation; V2 to V4 use Z3 and a direct state-machine diff.

## Log

- 2026-11-10: repo scaffolded; prior-art check repeated; interview set the convergence question (ADR 0003); V1 launched.
- 2026-11-10: V1 done. Pass with a narrower claim (N1 reworded in docs/claims.md). RvB and Kumar et al. have partial per-round curves; full text of VEPA and RvB still to read before any write-up.
- 2026-11-10: V2 done. Gate, oracle, patch checks and miner behave as predicted on the planted-seam fishery with scripted mocks (docs/results/v2.md); one preregistered card failed its first run and was fixed. Instrument calibration only. V3 next.
