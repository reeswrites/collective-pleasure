# Where we are and what we're aiming for (2026-11-10)

Findings below are about rule systems and scripted agents, not people, and none has been tested on a live model yet. The live ladder is running. Every result links to its file in docs/results/README.md.

## Vision

A chat workbench that formalizes the author's intent. The author talks loosely about how agents should behave. The system turns that into precise rules (ADICO cards, also shown as English-like sentences), proves what it can, runs experiments, and answers in plain English and charts. The author says "that's not what I meant" and the system fixes the test. Form: a Claude Code skill, the `mar` CLI, and one HTML report per run (ADR 0005).

## Research: norms

Find norms that let a network of agents cooperate freely. Four parts.

- **Pleasure is the good.** Agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state. There are two kinds of suffering: offsettable, and non-offsettable (being trapped, a need denied for weeks). Non-offsettable suffering is never netted against pleasure (ADR 0010, ADR 0011).
- **Freedom is equal liberty minus domination.** Options count if they are compatible with everyone's equal options, minus options that another member could block at will. Others leaving, refusing or abstaining is not domination, because those options depended on agreement. That loss is counted in cooperation and in the hedonic model (ADR 0014).
- **Cooperation.** Shared needs are met and outsiders do not pay.
- **Reported as scores, not one number.** Evolution searches the frontier. The author reads the winners in plain English.

The main world is a household (Partner A, Partner B, Friend C). The fishery stays as calibration. Two modes, delegates and peers, are both kept open (ADR 0011).

## Product: the evolving evaluator

What judges the norms improves alongside them. Agents' exploits widen the formal model. The author's corrections refine the test. A ladder of adversaries, from cheap decision models to strong LLMs, keeps the pressure honest. In the author's words, "more interested in the norms but the evaluator is the more interesting product". The timeline records how and why the evaluator changed.

## Central claim

Proofs make rules airtight inside the formal model. Clever enough agents step outside it. An inventive seam is an exploit found by an agent that the model checker did not predict. The aim is the capability level, and the price, at which agents start finding them (IT1). Below it, formal rules hold. Above it, the human loop must keep widening the model. Two arms of the live ladder separate capability (models told to probe the rules) from propensity (models just living as personas, no red-team wording).

## Two loops

- **(a) Rules against the test.** Evolution tightens rules until agents stop finding seams the test catches (C1).
- **(b) The test against the author's intent.** Each "not what I meant" is a fix to the test (C2). Two are recorded and are the first data points of loop (b): the seed read-back, where "everything shared always" had become "sharing is optional" and nothing encoded "request is never about control", and the pot read-back, where an agent's rule against taking the other's share was rejected because pot terms must be negotiated by those who share the pot. No curve exists yet. How to tell a real fall from author fatigue is not designed.

## How norms arise

Negotiation first (ADR 0008). Partners agree terms and exit conditions before living together, the card set is proof-checked for traps, then they live under it. Nobody owes anyone anything day to day except what they negotiated. The author's seed (verbatim in docs/seeds/) has a second version after the read-back: ownership with optional giving, a shared pot, asking that can always be refused unless bound, and two variants on whether a commitment to stay can bind. The pot is negotiated by everyone who shares it, not imposed. A negotiation phase and pot negotiation are being built by another agent (ADR 0013, in progress).

## What we have learned

Calibration held. The gate, oracle, patch checks and English surface behave as designed (V2, V2b), and scripted agents find exactly the seams at or below their depth on the seam ladder.

Two rediscovery checks split. Bargaining with outside options rediscovered Rubinstein's split and the outside-option principle, apart from one clause (allowing exit lowered mean cooperation by 0.019 over heuristic mixes). The voluntary public goods game was not rediscovered: cooperation persists at about the paper's value, the cycles do not show.

The evolution loop works and overfits. On the fishery, proofs reject about 14 percent of mutants, and a redundancy check flags 26 percent of those that pass. The first run's seam curve fell by exhaustion. Version 2 fixed that with fresh adversaries. Varied training narrowed the held-out gap in 5 of 9 pairs, which is suggestive. Elites still fail most hostile exam mixes, and the seed specs often do as well.

The household has been hard to make interesting. Hedonic goals, enforced sanctions and pressing personas did not produce a freedom against cooperation trade-off at the committed size. The author's seed equals baseline, and binding commitments to stay trapped nobody (a null). The trap rules fail in every pairing, but near-definitionally. Pressing personas raise failures a lot, and the power-seeking index never flags the controller.

Freedom measures disagree, and that is informative. Empowerment agrees with the hand-made score on coarse regimes, but ranks voluntary above compulsory in only 11 of 15 VPGG compositions. Liberty version 1 failed badly on VPGG because exit counted as domination. Version 2 repaired the sign (+5.263 bits) but two compositions still reverse and the fishery seat-order check misses.

## What is running

The live seam ladder, six models (Jev, Llama 3.1 8B, Haiku 5.5, Qwen3 235B, Sonnet 5.5, Opus 5.5) on ladder rule sets L1 to L5. Two arms, capability and propensity, each with its preregistration committed first and a cap of $12. Each runs on a frozen copy of the code. The author reads every candidate inventive seam before it counts.

## What is next

1. Negotiation: finish the phase and pot negotiation (ADR 0013).
2. Liberty into the household (needs `noop`, `force_policy` and `classify` on the adapter).
3. Household into evolution, with the final exam held back (defined, not run; claims FX1 and FX2).
4. Household chat commands and the five-minute demo with scripted agents.
5. Backlog: peer and delegate modes, version 3 (wanting and liking, ruptures, misappraisal), rule transfer (ML1), crowding out (F1), the missing VPGG cycles. Detail in docs/plan.md.

## Waiting on the author

Pushing to GitHub. Claude Code's auto mode blocks pushes from the session that did this work, so nothing from it is pushed. A narrow allow rule for `git push origin main` exists in the repo's `.claude/settings.local.json`, so future sessions opened in the repo can push once the author asks. Also: reading the candidate inventive seams, and deciding the ML1 cap.

## Cost

Conversation runs on the author's Claude plan. Swarm agents run through the API and never as Claude Code subagents. The first measured dry run: at most about $0.09 per five-agent, 12-month fishery run with Haiku 5.5. Estimated live ladder: about $5 per arm, worst case about $10.
