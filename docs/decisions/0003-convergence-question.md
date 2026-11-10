# 0003. The research question is convergence of spec refinement

Status: accepted (2026-11-10, by interview with the author)

## Context

The prior-art check (docs/prior-art/2026-11-10.md) found that solver-gating agent actions, gated vs prompt-only comparisons (Agent-C, Winston et al.), weighted compliance scores (AgentLTL), and conflict-checking rule sets before use (VEPA) all exist. The original S1 would have been replication. The author asked for a question that comes from today's thinking and is not yet proven. The author also asked that today's decisions take priority over earlier plans, including Computational Liberation's worth-it slice, which this repo does not wait for.

## Decisions

1. **Question.** Does iterative spec refinement converge for LLM agents: does the count of new seams per round slow, and where does it plateau? Chosen over "does mechanism crowd out normative competence" (kept as a follow-up) and "imposed vs chosen rules" (dropped).
2. **Seam.** A run that passes the gate but fails an intent oracle independent of the spec.
3. **Intent oracle.** Environment outcomes plus a frozen LLM-judge rubric, human-readable and tunable between experiments only; each rubric version gets its own curve. The patcher never sees the oracle.
4. **Patcher.** An LLM writes new rules as ADICO cards; the solver rejects patches that add conflicts, deadlock, or remove a repair path; the author audits a sample. Human-vs-AI patching arms are a later option.
5. **Two-way binding.** Forward: written rules gate agents. Backward: de facto rules are mined from traces and diffed against the written ones. Seams flow back automatically through the patcher. Emergent norms become proposed cards that wait for the author's yes, with solver checks attached; accept/reject decisions are logged as data.
6. **Agents.** One agent only as an instrument smoke test with no claims; the first real experiment is a five-agent swarm.
7. **Success.** A slowing curve, reported with its plateau and uncertainty, on at least three seeds. Zero is a bonus, not the bar. Bloat guard: slowing driven by an exploding rule count or agents unable to act is failure.
8. **Pace.** Small slices with quick pass/fail validations (docs/plan.md), aiming at a demo-able curve, not a full study first.

## Consequences

- RATIONALE.md sections 2, 3, 7 and 11 are rewritten; S1 and E0-E4 are superseded as primary experiments (kept in claims.md as superseded or follow-ups).
- ADICO's first concrete job is making the patcher's changes readable (ADR 0002 kill criterion still applies).
- Bisimulation moves from optional (D7) to the measure of de jure vs de facto distance, still dropped if it adds nothing over simpler diffs.
- The write-up must position against counterexample-guided refinement (CEGAR/CEGIS) and say what differs: LLM counterexample generators, an independent intent oracle, and rules that can grow from agent behavior.
- ASSUMED (builder choice, revisit at V4): early slices use a minimal in-repo fishery harness with GovSim's dynamics rather than GovSim itself, because GovSim is dormant since Jan 2025, pins old Python/numpy, and needs code changes for one agent. Running GovSim locally needs the author's OK.
