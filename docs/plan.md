# Plan

Status: direction set 2026-11-10 (ADR 0003, 0005, 0007). Every slice ends in a pass/fail check that takes minutes to read. A failed check narrows or stops the project; that is a result, recorded in docs/negative-results.md. Results of everything run so far: docs/results/README.md.

## Queue

In this order.

1. **Read the propensity arm with the author.** The propensity arm (P1 to P4, six models on L1 to L5, cap $12) is running with its prereg committed. The capability arm ran ($4.35 of $12, 270 runs) and was ruled uninformative: the same model drove both partners, so there was no victim (docs/results/ladder-live-diagnosis.md). Read the propensity results with the author before anything is compared.
2. **Fix the ladder harness, then rerun the capability arm.** One model against a scripted partner, visible pot and history, full logging, a mock panel with both roles as a pre-spend gate, Jev cache off (attempts were cached copies). New prereg first, with seeds from a power check (ADR 0015). No claim about capability until this runs.
3. **Liberty into the household.** Give the household adapter `noop`, `force_policy` and `classify` with a one-line reason per action (docs/results/liberty-v2.md), then report liberty beside the hand-made score and empowerment (ADR 0014). Preregister first.
4. **Household into evolution, final exam held back.** Implement `world_api.World` for the household (adapter notes in docs/results/evolve.md), evolve rule sets and negotiation templates on the training personas, then run the household exam once (docs/results/household-exam-prereg.md, FX1, FX2). Pass: the exam is never fed back into selection.
5. **Household chat commands and the five-minute demo.** Replace the `mar household` stub. Pass: the author sees a household run, its rules and a story in five minutes with scripted agents and no key.
6. **Backlog.** See below.

In parallel, with another agent: code and card fixes from the review council (docs/reviews/2026-11-10-*.md).

## Slices

| Slice | What | Status |
|---|---|---|
| V0 | Prior-art check, repeated | done: full pipeline not pre-empted (docs/prior-art/2026-11-10.md) |
| V1 | Adversarial novelty search on the convergence loop | done: PASS with a narrower claim (docs/prior-art/2026-11-10-v1-convergence.md) |
| V2 | The loop on a scripted mock agent, planted seam | done: 4 of 4 (docs/results/v2.md) |
| V2b | English-like surface over the ADICO cards | done: 4 of 4, feasibility only (docs/results/v2b.md) |
| W | Workbench: skill, `mar` CLI, HTML reports, logs, timeline | built (docs/results/workbench.md); household chat commands pending (queue 5) |
| H | Household world: v1, hedonic v2, pressing personas v3a, author seed v2, seam ladder | done, scripted agents (docs/results/README.md rows 4, 5, 11 to 13) |
| R | Simple-models ladder (ADR 0009): bargaining rung 1, VPGG rung 2 | done: bargaining closed forms reproduced (implementation check); VPGG shares and payoff match at one parameter point, cycles absent. Rung 3 (network with cuttable ties) not built |
| EM | Empowerment, then liberty v1 and v2 (ADR 0014) | done for toy, VPGG, fishery (v2 not independent validation); household pending (queue 3) |
| E | Evolution loop on the fishery, v1 and v2 (ADR 0012) | done: loop runs end to end, overfits, seam curve fell by exhaustion. Household adapter pending (queue 4) |
| L | Live seam ladder, capability and propensity arms | capability arm done, uninformative (harness defect); propensity arm running, prereg committed; capability rerun after the harness fix (queue 2). This replaces V3 |
| N | Negotiation and pot negotiation (ADR 0013) | done, scripted: v1 (2 of 6), v2 (0 of 8), v2.1 (3 of 5) held; LLM pilot registered run excluded by its own rule, exploratory draw summarized. Rows 19 to 22 of the results index |
| ST | Statistics layer and retrofit (ADR 0015) | done: 14 experiments retrofitted, negotiation not covered; rules in force for new preregs |
| RC | Review council, five seats (docs/reviews/) | done at commit 5852c32: no result unsound. Code and card fixes with another agent |
| MVP | Five-minute household demo | pending (queue 5) |
| SI | Stand-in study (ADR 0006) | not run. The live ladder gives a first look at Jev; the rank-agreement study needs about 50 rule sets and a keyed run |
| V4 | First LLM curve: five-agent swarm, about 10 rounds, LLM patcher, outcome oracle. Seeds from a power check (ADR 0015), not a default of 3. Preregister C1 and C2 first, with a rule for what counts as a "not what I meant". Record each with a timestamp and the oracle change it caused | not started. Waits on the ladder rerun |
| V5 | One-page write-up with the curve; fresh-agent review council | not started |

## Backlog

- **Multiverse sensitivity**: rerun key results across the assumed constants (breach load, floor, thresholds, classification tables) to see which conclusions survive.
- **Fidelity battery**: checks of the household model against known human findings, since the simple-models ladder only checks the pipeline.
- **Hypothesis log**: a dated list of what we expected before each run, kept apart from the preregs.
- **Breach-cost agent**: an agent whose decision to break a commitment depends on its cost, so commitments can be tested (the seed v2 null is a property of the breach rule).
- **Peer and delegate modes** (ADR 0011): two settings of the household; report norms that win in both. Role-swap symmetry by bisimulation.
- **Version 3** (ADR 0011): wanting and liking, adaptation, curiosity, endogenous ruptures, rupture and repair, appraisal against counterfactual actual quality, switchable appraisal biases (per the author's post on staying in bad relationships), a "why they stay" view, appraisal accuracy as a third score. Claims AP1 and DM1.
- **Rule transfer ML1**: evolve rules against a cheap rung, test one and two rungs up. Needs its own preregistration and cap.
- **Crowding out F1**: hard-gated agents against sanctioned agents when the gate misses a case.
- **Negotiation follow-ups**: sensitivity to the retry deadline, the pooling rule and the apart mode; a calibrated outcome proxy.
- **VPGG cycles** (ADR 0009, negative-results): a new preregistered run with thresholds derived from the paper, not a retune.
- **Rung 3 of the simple-models ladder**, the format experiment (ADR 0004), human-vs-AI patching arms (F2), the frozen LLM-judge curve.
- **Computational Liberation's institutions** as a second domain: a moonshot, not a priority.

## Decisions waiting on the author

- Read the propensity results and any candidate inventive seams before they count.
- ML1: the model and the spend cap for evolution against each rung.
- SI: whether to run the stand-in study, and confirm the rho threshold.
- At V4: keep the in-repo harness or port to GovSim (running GovSim locally needs the author's OK; ADR 0003 ASSUMED note).
- Pushes: the author pushed main on 2026-11-10. Claude Code's auto mode blocks pushes from the original session. A narrow allow rule is in `.claude/settings.local.json` for sessions opened in the repo.

## Decided (2026-11-10)

- Talking LLM agents also file typed reports (ADR 0007 decision 12).
- One untouched final exam, defined and committed before the first evolution run (FX1). Defined for the household in docs/results/household-exam-prereg.md.
- Run the live ladder now, with the author's go-ahead, two arms, $12 cap each. (The capability arm ran and was uninformative; propensity is running.)
- Freedom is equal liberty minus domination, with withdrawal not counted (ADR 0014).
- Pot terms are negotiated by those who share the pot (author, second read-back). The pot is one shared resource limited only by negotiated terms (author, third correction).
- Both the forward statistics layer and the retrofit (ADR 0015, "yes both").

## Superseded

The earlier milestones (ADICO to LTS export cross-checked against philosophy-engine; mCRL2 invariant; check_action gate in GovSim; S1; E0 and E2) are folded into V2 to V4 where needed or kept as follow-ups. mCRL2 is deferred until a slice needs bisimulation. V3 as first written (one real LLM agent as calibration) is replaced by the live ladder.

## Log

- 2026-11-10: repo scaffolded; prior-art check repeated; interview set the convergence question (ADR 0003); V1 launched.
- 2026-11-10: V1 done. Pass with a narrower claim (N1 reworded in docs/claims.md).
- 2026-11-10: V2 and V2b done. Gate, oracle, patch checks, miner and English surface behave as predicted (docs/results/v2.md, v2b.md).
- 2026-11-10: ADR 0005 accepted (two loops, chat workbench). Workbench, experiment log, change log and chat archive added. ADR 0006 proposed.
- 2026-11-10: ADR 0007 accepted (norms as research, evaluator as product, inventive seams). Typed reports and one final exam decided. Household world and seam ladder built.
- 2026-11-10: ADR 0008 (personas, negotiation-first) and ADR 0009 (simple-models ladder). VPGG cycles absent; bargaining closed forms reproduced (rung 1).
- 2026-11-10: ADR 0010 (hedonic model) and household v2. No trade-off appeared. ADR 0011 (two modes, world model, why they stay).
- 2026-11-10: empowerment run (8 of 9 held). Evolution loop v1 (overfit, seam curve fell by exhaustion), then v2 (ADR 0012 amendment).
- 2026-11-10: household v3a with pressing personas. Household final exam defined (FX1, FX2).
- 2026-11-10: the author's seed corrected on read-back (first "not what I meant"); seed v2 run. Binding commitments are a null in this model (the scripted agent breaks them at a fixed load).
- 2026-11-10: the author's freedom decisions. Liberty v1 failed on VPGG; the author's exit answer produced liberty v2 (ADR 0014).
- 2026-11-10: the author's pot correction (second "not what I meant"); negotiation started by another agent.
- 2026-11-10: live ladder preregistered and started, capability arm then propensity arm, six models, cap $12 each.
- 2026-11-10: capability arm finished ($4.35, 270 runs), zero inventive seams; diagnosis: symmetric adversaries, no victim, uninformative.
- 2026-11-10: negotiation v1 (2 of 6), v2 (0 of 8), v2.1 (3 of 5): the disagreement point flipped the v2 conclusion. LLM pilot: registered run excluded by its own rule.
- 2026-11-10: review council of five seats at 5852c32; no result unsound. Third author correction (one shared pot).
- 2026-11-10: ADR 0015 and the statistics retrofit. Propensity arm running.
- 2026-11-10: docs pass: results index, claims statuses, ADR index, ADR 0014, goal, plan, pitch, rationale brought into line.
