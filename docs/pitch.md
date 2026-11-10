# Pitch: evolving alignment norms, and checking the test against intent

Status: direction set 2026-11-10 (ADR 0003, ADR 0005). Nothing here is a result.

## The vision

An AI-native workbench used through chat. The author talks loosely about how agents should behave. The system turns that into precise rules (ADICO cards, also shown as English-like sentences), runs proofs and swarm experiments, and turns everything back into plain English and charts. The author checks it understood, and tweaks it in conversation. Chat captures something abstract. The system does the translation into something exact, still readable as the abstract it came from. Form: a Claude Code skill, a small `mar` CLI, and one HTML report per run (in progress: docs/results/workbench.md).

## The core

Evolve alignment norms by tweaking interpretable rules. Proof checks are the selection filter: candidates with conflicts, deadlock or no repair path are dropped before they run. The patcher is the mutation operator. The seam curve judges the evolution. One lineage first, a population later.

Mechanism can rule out only what the spec states. Proofs do not remove Goodhart's law, they move it to the gap between spec and intent. Every gating paper found (Agent-C, Winston et al., AgentLTL, TRAC, VEPA) measures agents under one fixed spec. Nobody has measured whether refinement converges.

## Two loops

Evolution always reverse-engineers the test. So there are two loops.

- **(a) Rules against the test.** Evolution tightens rules until agents stop finding seams the test catches. Curve: seams per round (claim C1).
- **(b) The test against the author's intent.** The author reads the winning rules and run stories in plain English. Each "that's not what I meant" is a fix to the test. The evolved rules are a readable mirror of what the test rewards. Curve: "not what I meant" moments per round (claim C2).

Loop (b) is the more original result: how well a person's intent can be formalized through conversation. A flat curve in either loop is as publishable as a falling one.

## The loop

```
written rules (ADICO cards) --compile--> transition system --gate--> agents act (Z3 per action)
        ^                                                                  |
        |  patcher writes cards; solver rejects conflicts, deadlock,       v
        |  lost repair path; human audits a sample                     traces
        |                                                                  |
        +---- (a) seams: runs that pass the gate but fail the test <-------+
        |                                                                  |
        +---- emergent norms: mined de facto rules, human-gated adoption <-+
                                                                           |
   author's intent <-- (b) plain-English rules and run stories, read by    |
        |              the author; "not what I meant" fixes the test       |
        +--------------------> intent oracle (the test) <------------------+
```

- **Intent oracle (the test):** environment outcomes (resource survives, nobody starves, catch inequality), plus a frozen, versioned LLM-judge rubric for deception. The patcher never sees it. The author refines it through loop (b); each oracle version gets its own curve.
- **Two-way binding:** written (de jure) rules gate the swarm; lived (de facto) rules are mined from traces and diffed against them.
- **Bloat guard:** a slowing seam curve from an exploding rule count, or from agents barely able to act, counts as failure.

## Proven and measured

Proven (bounded, k stated): the rules have no conflicts, no deadlock, bounded sanctions and a repair path; forbidden actions cannot execute. Measured: the gap between "safe by the rules" and "safe by what the author meant".

## Why it might be new

Formal-methods people know counterexample-guided refinement (CEGAR, CEGIS) but do not run LLM agents. LLM-agent people run fixed specs. RvB (2601.19726) and Kumar et al. (2602.00755) show per-round curves for simpler loops. The seam count against an oracle the patcher never sees, and the second loop that tests the oracle against a person's intent, were not found (docs/prior-art/2026-11-10-v1-convergence.md).

## Next

See docs/plan.md. Later: the format experiment (ADR 0004), and Computational Liberation's institutions as a second domain (a moonshot).
