# Plan

Status: pre-results. Direction set 2026-11-10 (ADR 0003, ADR 0005, docs/pitch.md). Every slice ends in a pass/fail check that takes minutes to read. A failed check narrows or stops the project; that is a result, recorded in docs/negative-results.md.

## Slices

| Slice | What | Budget | Validation (pass / fail) |
|---|---|---|---|
| V0 | Prior-art check, repeated | done | docs/prior-art/2026-11-10.md: full pipeline not pre-empted; gating, prompt-vs-gate and conflict-checking are prior art |
| V1 | Adversarial novelty search on the convergence loop | hours | Done 2026-11-10: PASS with a narrower claim; no paper pre-empts the full design (docs/prior-art/2026-11-10-v1-convergence.md). Pass: no work measures seams-per-round convergence of a refinement loop for LLM agents with an independent oracle. Fail: narrow the claim to what survives, or stop |
| V2 | Done 2026-11-10: PASS (4 of 4 checks; scripted patch needed one card fix, docs/results/v2.md). The loop on a scripted mock agent: tiny fishery, ADICO cards to Z3 gate, planted seam (per-catch cap, no per-month cap), outcome oracle, scripted patch, solver patch checks | half a day | Pass: oracle flags the planted seam; patch closes it; solver rejects a deliberately conflicting patch; mined de facto rules equal the written ones under the gate |
| V2b | Done 2026-11-10: PASS (4 of 4; English surface is lossless over 6 cards and 5756 grid points, but `must`, `may`, sanctions and arithmetic read less naturally than SLEEC style, docs/results/v2b.md). English-like (SLEEC-style) surface over the ADICO cards, render and parse, stories for counterexamples and traces | an hour or two | Pass: round trip identical; gate from parsed cards agrees on the V2 grid; conflicting set still fails the same checks; every counterexample and seam trace renders as plain English (mechanical test only) |
| V3 | Instrument calibration with one real LLM agent (cheap open model), same harness | a day | Pass: all four V2 checks hold with a real model; measured $ and minutes per round. No claims about convergence |
| SI | Stand-in study (ADR 0006, proposed): can a cheap decision model (Jev) stand in for an LLM? Same fishery, same rules and seeds, Jev vs LLM arms, ~50 candidate rule sets. Needs a live key and spend limit. Backends, typed reports and the Say vs do panel are built and mocked-tested | a day or two once keyed | Pass: Spearman rho >= the preregistered threshold (0.7 draft, author to confirm) on rule-set ranking; then Jev is the screening tier for evolution. Fail: report the negative result and what breaks agreement. Predictions SI1 to SI3 finalized before the first paid run |
| W | Workbench: Claude Code skill plus small `mar` CLI, self-contained HTML report per run (ADR 0005). Built-in-progress, see docs/results/workbench.md | in progress | Pass: the author can run a loop and read rules, stories and curves in plain English without reading code |
| MVP | 5-minute demo (ADR 0007): wire the household world into chat and run it with scripted agents, report in plain English | in progress | Pass: the author sees a household run, its rules and a story in five minutes, with no API key |
| V4 | First curve: five-agent swarm, ~10 rounds, 3 seeds, LLM patcher, outcome oracle (judge rubric optional). Run through the workbench. Preregister C1 and C2 before the first run. Record every "not what I meant" moment with a timestamp and the oracle change it caused | two to three days | Result either way: slope, plateau with uncertainty, rule count per round (loop a); "not what I meant" moments per round, one curve per oracle version (loop b). Bloat guard checked |
| V5 | One-page write-up with the curve; fresh-agent review council | a day or two | Council finds no claim beyond the evidence; card-only reader can follow every rule |

## Decisions waiting on the author

- At V4: keep the in-repo harness or port to GovSim (running GovSim locally needs the author's OK; ADR 0003 ASSUMED note).
- Before V3: model and spend ceiling for V3 (and later for V4 agents and patcher).
- Before the V5 write-up: whether to keep one untouched held-out final exam (recommended, cheap; ADR 0005).
- Deferred: whose conversation is formalized first. The author's own is formalized by using the workbench; the agents' say vs do gap is a later target.
- After V4: whether to add the frozen LLM-judge curve, human-vs-AI patching arms, or the crowding-out follow-up.
- Before SI: the author creates an OpenRouter key, sets a spend limit, and puts it in `.env` (never in chat). For claude agents: an `ANTHROPIC_API_KEY` or `ant auth login`, plus a model choice. Also confirm the rho threshold.
- Before the first real runs: the author creates API access; then place models on the seam ladder and measure cost (ADR 0007).
- Decided 2026-11-10: talking LLM agents also file typed reports (standing rule). Keep one untouched final exam, defined and committed before the first evolution run (FX1). Before the first evolution run: define and commit that exam.

## Later

The format experiment (ADR 0004, four arms including F-EN), after V4's setup is fixed. Computational Liberation's institutions as a second domain: a moonshot, to show the learnings carry over; not a priority.

## Superseded

The earlier milestones (ADICO to LTS export cross-checked against philosophy-engine; mCRL2 invariant; check_action gate in GovSim; S1; E0 and E2) are folded into V2 to V4 where needed or kept as follow-ups. mCRL2 is deferred until a slice needs bisimulation; V2 to V4 use Z3 and a direct state-machine diff.

## Log

- 2026-11-10: repo scaffolded; prior-art check repeated; interview set the convergence question (ADR 0003); V1 launched.
- 2026-11-10: V1 done. Pass with a narrower claim (N1 reworded in docs/claims.md). RvB and Kumar et al. have partial per-round curves; full text of VEPA and RvB still to read before any write-up.
- 2026-11-10: V2 done. Gate, oracle, patch checks and miner behave as predicted on the planted-seam fishery with scripted mocks (docs/results/v2.md); one preregistered card failed its first run and was fixed. Instrument calibration only. V3 next.
- 2026-11-10: V2b done. An English-like controlled grammar round trips all six V2 cards, gives the same gate and the same patch-check verdicts; ADR 0004 gains arm F-EN and plain-English counterexamples in every arm (draft D2d). Feasibility only; no reader test.
- 2026-11-10: ADR 0005 accepted. Two loops (rules vs test, test vs intent), the chat workbench, claim C2. Workbench added as built-in-progress; V4 runs through it.
- 2026-11-10: Experiment log (experiments/log.jsonl), change log (experiments/changes.jsonl) and chat archive (docs/conversations/) added to the workbench; every run and every rule or oracle change is now recorded with the author's verbatim words.
- 2026-11-10: ADR 0006 proposed (decision-model stand-in study). Agent backends (scripted, Jev, OpenRouter LLM, Claude), typed reports, Say vs do panel, dry-run pricing and a Message Batch sweep built, offline-tested only; no live call made.
- 2026-11-10: ADR 0007 accepted. Research is norms (freedom and cooperation, household world), product is an evolving evaluator, central measure is inventive seams across a seam ladder and a model ladder. docs/goal.md added; claims IT1 and ML1 drafted. Household world and seam ladder in progress.
- 2026-11-10: author decided typed reports for LLM agents and one untouched final exam (ADR 0007, FX1). Branch pushed to GitHub (private repo) at the author's request.
