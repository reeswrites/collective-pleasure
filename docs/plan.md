# Plan

Status: direction set 2026-11-10 (ADR 0003, 0005, 0007). Every slice ends in a pass/fail check that takes minutes to read. A failed check narrows or stops the project; that is a result, recorded in docs/negative-results.md. Results of everything run so far: docs/results/README.md.

## Queue

Rebalanced 2026-11-11 at the author's word ("Rebalance"), after the scope review (docs/reviews/2026-11-11-scope.md) found the hedonic thread had displaced the evaluator thread. **Freeze:** no new hedonic hypotheses or levers until items 1 to 3 have results. Running hedonic work finishes (H35, ADR 0018 tests 1 and 2, the v2.3 retest). In this order:

1. **IT1, the central claim, on rungs where an inventive seam is reachable and pays.** Free harness work and the "every label reachable" gate first (in progress), then the paid run, capped at $8, only on the author's yes. Plan: docs/plans/inventive-seam-next.md. Draft prereg: docs/results/ladder-it1-prereg-DRAFT.md. Folds H10 to H13.
2. **Household evolution to a result, then the final exam once** (loop a in the main world; docs/results/household-evolve-prereg.md, household-exam-prereg.md). Folds H14 and H15 into H16.
3. **Loop b counting.** A written rule for what counts as a "not what I meant", applied to the logged corrections, with a fatigue control. Needs no model.
4. **H05, the breach-cost agent** (free, scripted), once the machine load allows.
5. **The v2.3 retest** after the household fixes (pleasure minus suffering; baseline may decline). Then pause the hedonic list.

Deferred by the freeze: H02, H25 to H31, H33, H32c. H35 runs because it had already started. The attune-style ladder variant (H32d: the partner calms only when its own pleasure improves, never on a concession) was approved by the author separately and runs after H35.

## Slices

| Slice | What | Status |
|---|---|---|
| V0 | Prior-art check, repeated | done: full pipeline not pre-empted (docs/prior-art/2026-11-10.md) |
| V1 | Adversarial novelty search on the convergence loop | done: PASS with a narrower claim (docs/prior-art/2026-11-10-v1-convergence.md) |
| V2 | The loop on a scripted mock agent, planted seam | done: 4 of 4 (docs/results/v2.md) |
| V2b | English-like surface over the ADICO cards | done: 4 of 4, feasibility only (docs/results/v2b.md) |
| W | Workbench: skill, `mar` CLI, HTML reports, logs, timeline | done (docs/results/workbench.md); household commands built (docs/demo.md) |
| H | Household world: v1, hedonic v2, pressing personas v3a, author seed v2, seam ladder | done, scripted agents (docs/results/README.md rows 4, 5, 11 to 13) |
| R | Simple-models ladder (ADR 0009): bargaining rung 1, VPGG rung 2 | done: bargaining closed forms reproduced (implementation check); VPGG shares and payoff match at one parameter point, cycles absent. Rung 3 (network with cuttable ties) not built |
| EM | Empowerment, then liberty v1 and v2 (ADR 0014) | done for toy, VPGG, fishery (v2 not independent validation); household descriptive check done (docs/results/household-liberty.md) |
| E | Evolution loop on the fishery, v1 and v2 (ADR 0012) | done: loop runs end to end, overfits, seam curve fell by exhaustion. Household run 1 in progress |
| L | Live seam ladder: capability (twice), propensity, win | done. First capability arm uninformative; propensity 20 fixture candidates; rerun inverted the ranking; win arm found almost nothing. No inventive seam on L1 to L4, but that zero is automatic: the classifier could not have labelled one there, so IT1 is untested. docs/results/README.md rows 16, 17, 23, 24. This replaces V3 |
| N | Negotiation and pot negotiation (ADR 0013) | done, scripted: v1 (2 of 6), v2 (0 of 8), v2.1 (3 of 5) held; LLM pilot registered run excluded by its own rule, exploratory draw summarized. Rows 19 to 22 of the results index |
| ST | Statistics layer and retrofit (ADR 0015) | done: 14 experiments retrofitted, negotiation not covered; rules in force for new preregs |
| RC | Review council, five seats (docs/reviews/) | done at commit 5852c32: no result unsound. Code and card fixes complete |
| MVP | Five-minute household demo | done (docs/demo.md, `scripts/demo_check.py`) |
| SI | Stand-in study (ADR 0006) | not run. The live ladder gives a first look at Jev; the rank-agreement study needs about 50 rule sets and a keyed run |
| LT | Rule-set lint and pre-spend gates | done (docs/results/lint.md; `mar lint`; live runs refuse to spend until it passes) |
| PD | Seed v2.2 and the pleasure demonstration | done: author confirmed v2.2 on condition; 8 of 8 held robustly with caveats (docs/results/pleasure-demo.md) |
| PL | Pleasure levers and horizon (ADR 0016, 0017) | done: levers did not show the author's condition (D = -0.019 [-0.051, +0.009]); horizon mostly held (docs/results/pleasure-levers.md, horizon.md) |
| V4 | First LLM curve: five-agent swarm, about 10 rounds, LLM patcher, outcome oracle. Seeds from a power check (ADR 0015), not a default of 3. Preregister C1 and C2 first, with a rule for what counts as a "not what I meant". Record each with a timestamp and the oracle change it caused | not started. The ladder rerun and win arm are done and found no inventive seam, so V4 waits on the author's call on a framing for the strong models |
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

- Answer the 13 open questions in the hedonic technology synthesis (summarized in docs/goal.md), and read the levers and horizon results.
- A framing for the strong Claude models, or drop the ladder as the IT1 test.
- ML1: the model and the spend cap for evolution against each rung.
- SI: whether to run the stand-in study, and confirm the rho threshold.
- At V4: keep the in-repo harness or port to GovSim (running GovSim locally needs the author's OK; ADR 0003 ASSUMED note).
- Pushes: GitHub push now works from sessions opened in the repo (a narrow allow rule for `git push origin main` is in `.claude/settings.local.json`). The original session was blocked by auto mode.

## Decided (2026-11-10)

- Talking LLM agents also file typed reports (ADR 0007 decision 12).
- One untouched final exam, defined and committed before the first evolution run (FX1). Defined for the household in docs/results/household-exam-prereg.md.
- Run the live ladder now, with the author's go-ahead, two arms, $12 cap each. (Done: capability uninformative, propensity done.)
- Win framing is the main ladder arm for IT1; the loophole arm is the ceiling (author, "1").
- Seed v2.2 confirmed "as long as it can demonstrate pleasure in relationships hedonic technology". Exit terms are negotiated, rule 8 is a norm with trust (author, seed read-back).
- Lifetime pleasure, and the experiencing self is the remembering self through vividness of memory (author).
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
- 2026-11-10: council fixes complete (pot as one balance, honest labels, no hidden rules, independent Jev samples, dated corrections).
- 2026-11-10: rule-set lint (`mar lint`) and pre-spend gates. Ladder harness v2 and the capability rerun prereg.
- 2026-11-10: ladder v2 capability rerun (about $0.24): cheap models exploited most, Sonnet stopped and Opus excluded on `cyber` refusals, ranking inverted, no inventive seam (docs/results/ladder-live-v2.md). Corrected 2026-11-11: IT1 is untested, not "not supported"; the classifier could not have labelled a seam inventive on L1 to L4 (docs/plans/inventive-seam-next.md).
- 2026-11-10: the author's win-framing question and decision; win arm preregistered and run ($2.69): almost no seams, none inventive.
- 2026-11-10: propensity arm result: 20 candidates, one move, read by the author as a fixture. Fourth "not what I meant" (exit terms); seed v2.2; the author confirms it on condition.
- 2026-11-10: pleasure demonstration (8 of 8 held robustly, with caveats). Hedonic technology synthesis. The author's lifetime-pleasure and one-self answers recorded.
- 2026-11-10: household commands and the five-minute demo; liberty v2 in the household.
- 2026-11-10: pleasure levers (ADR 0016) and horizon (ADR 0017) preregistered and in progress; household evolution run 1 in progress.
- 2026-11-10: docs pass 2: goal, plan, claims, results index, pitch, README, decisions index.
