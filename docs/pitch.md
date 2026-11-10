# Pitch: does spec refinement converge?

Status: direction set 2026-11-10 by interview (ADR 0003). Nothing here is a result.

## The question

Mechanism can rule out only what the spec states. Proofs don't remove Goodhart's law, they move it. An agent that cannot break the checker exploits the gap between the spec and what we meant, and bugs move to the seams.

The optimistic bet is that this is still a hill-climb: find a seam, tighten the spec, repeat, and the spec gets good enough. **Nobody has measured whether that loop converges for LLM agents.** Every gating paper found (Agent-C, Winston et al., AgentLTL, TRAC, VEPA) measures agents under one fixed spec.

> Run the loop. Count new seams per round. Does the curve slow, and where does it plateau?

The plateau is the answer to "how good can good enough get" for a given spec language, testbed and model. A flat curve is as publishable as a falling one.

## The loop

```
written rules (ADICO cards) --compile--> transition system --gate--> agents act (Z3 per action)
        ^                                                                  |
        |  patcher writes cards; solver rejects conflicts, deadlock,       v
        |  lost repair path; human audits a sample                     traces
        |                                                                  |
        +---- seams: runs that pass the gate but fail the intent oracle <--+
        |                                                                  |
        +---- emergent norms: mined de facto rules, human-gated adoption <-+
```

- **Intent oracle,** independent of the spec: environment outcomes (resource survives, nobody starves, catch inequality), plus a frozen, versioned LLM-judge rubric for deception. Rubrics are tuned between experiments, never during one. The patcher never sees the oracle.
- **Two-way binding:** the written (de jure) rules gate the swarm; the lived (de facto) rules are mined from traces and diffed against them. The diff shows seams and emergent norms. Distance between the two state machines is where bisimulation earns its place.
- **Bloat guard:** a slowing seam curve that comes from an exploding rule count, or from agents barely able to act, counts as failure.

## Why it might be new, and why others may not have done it

- Formal-methods people know counterexample-guided refinement (CEGAR, CEGIS) and its convergence results for finite systems, but don't run LLM agents. LLM-agent people run fixed specs. The pieces exist; the loop with an independent intent oracle, LLM counterexample generators, and rules that can grow from agent behavior was not found (see docs/prior-art/).
- RvB (2601.19726) and Kumar et al. (2602.00755) already show per-round curves for simpler loops (defense rate, constitution fitness). The new measure is the seam count against an oracle the patcher never sees, plus the de jure vs de facto diff (V1, docs/prior-art/2026-11-10-v1-convergence.md).
- Measuring a seam needs intent separated from spec. Most work uses the spec as its own judge, so "zero violations" is circular.

## Fastest validations

See docs/plan.md. In order: an adversarial novelty search (hours); the loop on a scripted mock agent (half a day); one real LLM agent as instrument calibration (a day); the first five-agent curve (two to three days); a one-page write-up (a day or two).
