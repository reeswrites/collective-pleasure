# Decisions

One line per ADR. Status as of 2026-11-10. ADRs 0001 to 0009 and 0015 carry dated status notes where later results or reviews changed how to read them. ADRs 0010 to 0014 are amended by their owner. ADR 0012 is being amended by the household evolution agent. Overview of where the project stands: docs/goal.md. Evidence for each decision: docs/results/README.md.

| ADR | Title | Status | In one line |
|---|---|---|---|
| 0001 | New repo and stack | accepted | A new repo. philosophy-engine is an input, not the core. Labeled transition systems are the semantic core |
| 0002 | ADICO as authoring layer | accepted, conditional | ADICO is the human-readable rule format, dropped if it makes no measured difference |
| 0003 | The research question is convergence of spec refinement | accepted | Does the count of new seams per round slow? Kept as loop (a), claim C1 |
| 0004 | Rule format is decided by experiment | proposed | Four formats (ADICO, structured, English-like, text) compared after the swarm setup is fixed |
| 0005 | Two loops, a chat workbench, and evolved norms | accepted | Rules against the test, and the test against the author's intent, used through chat |
| 0006 | When can a cheap decision model stand in for an LLM? | proposed | Jev vs LLM rank-agreement study. Not run |
| 0007 | Norms as research, evaluator as product, inventive seams as the central measure | accepted | Two scores, the household, the seam and model ladders, typed reports, one untouched final exam. A capability threshold is a question, not a presupposition (status note 2026-11-10) |
| 0008 | Personas, negotiation-first households, and the pattern atlas | accepted | Two-layer personas; households negotiate, check, live, exit. Pot negotiation follows in ADR 0013 |
| 0009 | Simple-models ladder | accepted | Check the pipeline against known results (bargaining, VPGG) before LLM households. VPGG cycles absent; bargaining closed forms reproduced (an implementation check). Household fidelity stays untested |
| 0010 | A modeled hedonic state as the grounding of "good" | accepted | Pleasure is the good; two kinds of suffering; spirals; enforced sanctions; weekly household |
| 0011 | Two modes, world-model framing, and why agents stay | accepted | Delegates and peers left open; Guaranteed Safe AI shape; version 3 scope. Freedom part amended by 0014 |
| 0012 | The evolution loop | accepted, amended (v2) | Population, proof filter, Pareto selection, world interface. v2 adds fresh adversaries and a redundancy check |
| 0013 | Negotiated pots | accepted, amended (v2, v2.1, LLM pilot) | Pot terms are negotiated by those who share the pot, not imposed. The amendments record that the disagreement point changed the conclusion |
| 0014 | Freedom is equal liberty minus domination | accepted | Compatible options minus options held at another's sufferance; withdrawal is not domination |
| 0015 | Formal statistics | accepted | A statistics layer (bootstrap, permutation, exact binomial, Holm, power), a retrofit of today's results, and new prereg rules. Template in docs/templates/prereg.md |
| 0016 | Pleasure levers | in progress (another agent; the file may still be uncommitted) | Adaptation and anticipation, commitment as a converter, unbundled networks, each behind a default-off flag. Prereg committed, run in progress. Not yet verified here |
| 0017 | Horizon: lifetime pleasure | results in (docs/results/horizon.md), amplification amendment run | Lifetime pleasure as present pleasure, vividness-weighted memory and anticipation, tested against greedy play by exact dynamic programming. Prereg committed (docs/results/horizon-prereg.md) |
| 0018 | Hedonic technology tests as evaluator criteria | proposed (awaiting the author) | Liking vs wanting, worth it vs hard to leave, security vs checking become evaluator measures. Theory in docs/theory.md |
