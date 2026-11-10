# Pitch: evolving norms for agent networks, and checking the test against intent

Status: direction set 2026-11-10 (ADR 0003, 0005, 0007). Early results from scripted agents in toy worlds are in docs/results/README.md. One live capability run exists and was uninformative (harness defect), so no live-model result supports a claim yet.

## The vision

An AI-native workbench used through chat. The author talks loosely about how agents should behave. The system turns that into precise rules (ADICO cards, also shown as English-like sentences), runs proofs and swarm experiments, and turns everything back into plain English and charts. The author checks it understood, and tweaks it in conversation. Chat captures something abstract. The system does the translation into something exact, still readable as the abstract it came from. Form: a Claude Code skill, a small `mar` CLI, and one HTML report per run (in progress: docs/results/workbench.md).

## The core

Evolve norms for agent networks by tweaking interpretable rules. "Alignment" is the aim, not something shown so far. Proof checks are the selection filter: candidates with conflicts, deadlock or no repair path are dropped before they run. The patcher is the mutation operator. The seam curve judges the evolution. One lineage first, a population later.

Mechanism can rule out only what the spec states. Proofs do not remove Goodhart's law, they move it to the gap between spec and intent. Most gating papers we found (Agent-C, Winston et al., AgentLTL, TRAC) measure agents under one fixed spec. VEPA patches its rules with a verifier, so it is not a fixed-spec paper. In an abstract-level search (about 70 percent confidence) we found no study of the per-round rate of new gate-passing seams under an independent oracle. Partial per-round curves exist (RvB, Kumar et al.). Absences are search results, not proofs (docs/prior-art/README.md).

## Two loops

Evolution always reverse-engineers the test. So there are two loops.

- **(a) Rules against the test.** Evolution tightens rules until agents stop finding seams the test catches. Curve: seams per round (claim C1).
- **(b) The test against the author's intent.** The author reads the winning rules and run stories in plain English. Each "that's not what I meant" is a fix to the test. The evolved rules are a readable mirror of what the test rewards. Curve: "not what I meant" moments per round (claim C2).

Loop (b) asks how well a person's intent can be formalized through conversation. We did not search for prior work on it, so we make no originality claim for it. A flat curve in either loop is as publishable as a falling one. Three corrections are logged by hand (the seed read-back, the pot read-back, the single-pot choice). No rule for counting them exists yet, and the author's liberty answer was not counted. They are data points, not a curve.

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

Checked to depth k = 3 (months or rounds) within the compiled model: the rule sets we ran have no conflict, deadlock or lost repair path. Some of these checks run over mirror compilers written by the builder. The gate's correctness on our worlds is tested, not proved. A proof says nothing about actions outside the formal model, which is what IT1 asks about. Measured: the gap between "safe by the rules" and "safe by what the author meant".

## Why it might be new

Formal-methods people know counterexample-guided refinement (CEGAR, CEGIS) but do not run LLM agents. LLM-agent people run fixed specs. RvB (2601.19726) and Kumar et al. (2602.00755) show per-round curves for simpler loops. The seam count against an oracle the patcher never sees, and the second loop that tests the oracle against a person's intent, were not found in snippet-level searches (docs/prior-art/2026-11-10-v1-convergence.md, docs/prior-art/README.md).

## For researchers: the norms

Readable rules for AI agent networks, evolved under pressure.

The aim is norms that let agents cooperate freely. Pleasure is the good, with two kinds of suffering, one that pleasure can offset and one that it cannot (ADR 0010). Freedom is the options compatible with everyone's equal options, minus options another member could block at will. Others leaving, refusing or abstaining is not counted as domination, since those options depended on agreement (ADR 0014). Cooperation means shared needs are met without outsiders paying. Evolution maps the frontier between the scores, and the author reads the winners in plain English. We ask whether there is a capability level, and a price, at which agents find inventive seams: exploits the model checker did not predict (ADR 0007, claims IT1 and ML1). There may be none in this world. Model rows also differ in compliance with a red-team prompt, so one arm cannot separate capability from compliance. Norms arise by negotiation first: partners agree terms and exit conditions, the card set is proof-checked, then they live under it (ADR 0008).

## For builders: the evaluator

The evaluator is the more interesting product. It evolves with the norms. Agent exploits widen the formal model, the author's "that's not what I meant" moments refine the test, and a ladder of adversaries from cheap decision models to strong LLMs keeps the pressure honest. The timeline records how and why it changed. Used through chat (see docs/goal.md).

## The world-model framing

In small, this resembles the Guaranteed Safe AI shape, as an analogy (Dalrymple, Skalse, Bengio, Russell, Tegmark et al. 2024, arXiv:2405.06624). The household sim with counterfactuals is the world model. Pleasure, non-offsettable suffering, liberty and norms are the specification. Proof checks, the seam ladder and the evaluator are the verifier. That separates value alignment (norms produce good lives) from epistemic alignment (agents' appraisals match reality). The household is our model, so claims about real people wait on fidelity checks (ADR 0011).

## What we've learned so far

On scripted agents in toy worlds, with assumed parameters.

- **Calibration held.** Gate, oracle, patch checks and English surface behaved with mock agents (V2 4 of 4 after one card fix; V2b round trip lossless on 6 cards, reader test not run). Scripted agents find the seams at or below their depth, which calibrates the instrument and says nothing about any model.
- **Rung checks.** The bargaining module reproduces Rubinstein's closed form (an implementation check, no empirical content). In VPGG the strategy shares and payoff match the published equilibrium at one parameter point and the cycles did not appear.
- **Evolution on the fishery** runs end to end and overfits. The first seam curve fell by exhaustion. Varied training narrowed the held-out gap in 6 of 9 pairs by the preregistered table, with an interval that reaches the threshold.
- **The household** shows no freedom against cooperation trade-off at the committed size. In this model a stay commitment never held anyone, because the scripted agent breaks it at a fixed suffering load. That is a property of the agent's breach rule, not a finding about commitments. The non-offsettable suffering headline is mostly denied money and security, and trapped weeks are about zero outside the trap control.
- **Liberty.** The author's answer that withdrawal is not domination removes the VPGG sign reversal in 11 of 15 compositions. The classification was chosen after the failure, so this is not independent validation, and in VPGG the domination term is zero by construction. Two compositions still reverse and the fishery check misses.
- **Negotiation.** The disagreement point flipped the conclusion. v1 held 2 of 6, v2 0 of 8, v2.1 3 of 5. Real outside options looked harmful in v2 and harmless in v2.1, only because failure was modeled as sharing a house in v2 and as living apart in v2.1. Every disagreement model here is assumed.
- **Live seam ladder, capability arm.** It ran (six models, $4.35) and was uninformative: the same model drove both partners, so the oracle had no victim. It is not the real test. A corrected rerun needs a new preregistration. The propensity arm is running.
- **How sure.** Of 30 testable preregistered rows, 11 hold robustly, 5 hold but the interval reaches the threshold, 11 are robust misses and 3 are misses whose interval reaches the threshold. 51 of 81 rows are not testable. Negotiation is not covered by the retrofit. Of the world-level predictions in the tallies, a large share missed (about 37 of 88 by a rough count of the scored tables), and each miss is logged.

## Next

See docs/plan.md. The queue is the propensity read, the ladder harness fix and capability rerun, liberty into the household, household into evolution with the final exam held back, then chat commands and a five-minute demo. Later: the format experiment (ADR 0004), version 3 (why agents stay), and Computational Liberation's institutions as a second domain (a moonshot).
