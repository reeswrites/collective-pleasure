# 0005. Two loops, a chat workbench, and evolved norms

Status: accepted (2026-11-10, by conversation with the author, after ADR 0003 and 0004)

## Context

ADR 0003 set the question as convergence of spec refinement. ADR 0004 set the format experiment. In conversation on 2026-11-10 the author restated the project in terms of what it is for and what it measures. This ADR records that framing. Nothing here is a result.

## Decisions

1. **Vision: a workbench used through chat.** The author talks loosely about how agents should behave. The system translates that into precise rules (ADICO cards, also rendered as English-like sentences per V2b), runs proofs and swarm experiments, and translates everything back into plain English and charts. The author checks that the system understood, and tweaks it in conversation. Chatting captures something abstract. The system does the cognitive translation that formalizes it into something calcified but still generated from, and readable as, the abstract. Form: a Claude Code skill plus a small `mar` CLI, with a self-contained HTML report per run. Status: in progress; see docs/results/workbench.md.
2. **Core: evolve alignment norms by tweaking interpretable rules.** Proof checks are the selection filter: candidates with conflicts, deadlock or no repair path are discarded before they run. The patcher is the mutation operator. The seam curve judges the evolution. Single lineage first (V3, V4). A population is later.
3. **Two loops.** Evolution is always reverse-engineering the test. So there are two loops:
   - **(a) Rules against the test.** Evolution tightens rules until agents stop finding seams the test catches.
   - **(b) The test against the author's intent.** The author reads the winning rules and run stories in plain English. Every "that's not what I meant" becomes a fix to the test (the oracle). The evolved rules are a readable mirror of what the test actually rewards.

   Two curves are reported: seams per round (rules vs test) and "not what I meant" moments per round (test vs intent). The second is the more original result: how well a person's intent can be formalized through conversation.
4. **Proven vs measured.** Proven: properties of the rules (no conflicts, no deadlock, bounded sanctions, repair path) and gate soundness (forbidden actions cannot execute). Both are bounded, with k stated. Measured: the gap between "safe by the rules" and "safe by what the author meant".
5. **Later.** The format experiment (ADR 0004, four arms including F-EN) runs after V4's setup is fixed. Computational Liberation's institutions as a second domain is a moonshot, to show the learnings carry over. It is not a priority.

## Pending author decisions

- Whether to keep one untouched held-out final exam (an oracle version never used during evolution or by the author's loop (b) edits) for the write-up. Recommended: yes, it is cheap, and without it the final score is judged by a test the author tuned.
- Model and spend ceiling for V3.
- Deferred: whose conversation is formalized first. The author's own conversation is formalized by using the workbench. The agents' own conversation (the say vs do gap in the swarm) is a later target.

## Consequences

- ADR 0003's convergence question is kept as loop (a), claim C1.
- ADR 0003 decision 3 ("the patcher never sees the oracle") still holds for the patcher. But the oracle is now itself refined by the author through loop (b). Each oracle version gets its own curve, as ADR 0003 already required for rubric versions. Curves across oracle versions are not pooled.
- New claim C2 (loop b): "not what I meant" moments per round decrease toward a plateau. Untested; preregister before V4.
- Plan: V3, V4 and V5 stay. The workbench is added as built-in-progress. V4 is run through the workbench and must record each of the author's "not what I meant" moments with a timestamp and the oracle change it caused.
- Risk, stated plainly: a falling "not what I meant" curve can also mean the author got tired or the conversation got narrower. C2's preregistration must say how that is told apart (for example, fresh probe scenarios shown to the author each round). ASSUMED: this is not yet designed.
- The pitch and RATIONALE sections 1b, 2, 3, 7 and 11 are updated to lead with this framing. Other RATIONALE sections are unchanged.
