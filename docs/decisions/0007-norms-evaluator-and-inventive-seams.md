# 0007. Norms as research, evaluator as product, inventive seams as the central measure

Status: accepted (2026-11-10)

## Context

The author's conversation of 2026-11-10 moved the project. The questions are recorded verbatim in experiments/questions.jsonl (topics network-alignment, cognition-price, seam-ladder, inventive-seams, evolving-evaluator, norms-vs-evaluator). This ADR collects the decisions. Overview: docs/goal.md. Nothing here is a result.

## Decisions

1. **Research is norms; product is the evaluator.** The author: "more interested in the norms but the evaluator is the more interesting product". Doing the research builds the product.
2. **Network-alignment objective is two scores.** Freedom (anyone can leave and keeps real options) and cooperation (shared needs met, outsiders do not pay). Evolution maps the Pareto frontier between them. The author chose this over a single "voluntary cooperation" score. Single-agent alignment stays a separate line of work.
3. **Subfield:** cooperative AI (Dafoe et al., Open Problems in Cooperative AI; the Cooperative AI Foundation).
4. **Main world is the household** (Partner A, Partner B, Friend C). The fishery stays as calibration.
5. **The evaluator evolves.** Agent exploits widen the formal model. The author's "that's not what I meant" moments refine the test. A ladder of adversaries keeps pressure honest. The timeline records how and why it changed.
6. **Central claim: inventive seams.** Proofs make rules airtight inside the formal model. An inventive seam is an exploit found by an agent and not predicted by the model checker. The measure is the capability level and price at which they appear. Below it formal rules hold. Above it the human loop must keep widening the model.
7. **Seam ladder.** Graded planted seams. Formal depth is the shortest exploiting trace plus the minimum number of coordinating agents. The top rung is the inventive seam.
8. **Model ladder.** Jev, a small free or local model, Haiku 5.5, a mid open model, Sonnet 5.5, Opus 5.5. Transfer tests follow "evolve cheaply, test expensively": each generation's best rules face a stronger adversary.
9. **Typed talk for deception.** Decision-model agents talk in a fixed vocabulary. A typed lie is a mismatch between report and action. LLM agents also talk freely. The formal vocabulary grows when LLMs deceive outside it.
10. **Cost strategy.** Conversation on the author's Claude plan. Swarm agents via API: Jev for screening, Haiku 5.5 for sweeps, Sonnet 5.5 and Opus 5.5 for exams, the patcher and the judge. Agents never run as Claude Code subagents. Measured dry run: at most about $0.09 per 5-agent, 12-month fishery run with Haiku 5.5. First month estimated at $80 to $130.
11. **Guardrail.** Evolving deceptive strategies is robustness testing only, reported as defenses (CONTRIBUTING.md).

## Prior art to check

Dynabench (Kiela et al. 2021), a human-and-model-in-the-loop benchmark. Named from memory; unverified. Check before any write-up.

## Predictions

Drafts IT1 and ML1 in docs/claims.md. Finalize and commit before the first paid run.

## Consequences

- docs/plan.md gains the MVP demo slice and pending items.
- ADR 0006's stand-in study is the screening-tier question inside the model ladder.
- Open for the author: typed reports from LLM agents, one untouched final exam, and pushing the branch.
