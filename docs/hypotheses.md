# Hypothesis log (2026-11-10)

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Purpose: keep exploring apart from confirming. This is a list of things we might be wrong or right about, generated on purpose from the results, the surprises, the reviews, the author's notes and the author's own questions. Nothing here is a result and nothing here is preregistered. A hypothesis becomes a test only when it gets a prereg file (see the last section). This closes the "Hypothesis log" item in docs/plan.md.

**The author picks which to promote.** The ranking below is a suggestion, not a plan.

Machine-readable rows: experiments/hypotheses.jsonl. `uv run python scripts/hypotheses.py rank` prints the ranking from those rows.

## How the ranking works

Three scores from 1 to 5, rank by their product (maximum 125).

- **Testability**: 5 is a scripted run on saved data or a cheap world with a named test and a power check; 1 is a model we have not built.
- **Novelty**: against docs/prior-art/ and what we already hold. 5 is not found there. Those three checks cover the pipeline (rules, solver gate, LLM agents, loop) and say nothing on household norms, so household scores rest on known human results from memory, not on a search. Treat novelty as the weakest score.
- **Decision value**: would the result change what we do next. 5 is it decides a build or a spend.

Caveats on the ranking. The product favours cheap tests and work already running, so the top of the list is partly "what we are doing anyway". Scores are my judgement, written once, not calibrated. Every household and evolution hypothesis here is about scripted agents with assumed constants, so a result is about the model.

Status labels: **running** (a prereg exists and the run is scheduled or in progress), **partly tested** (a result is in and the hypothesis is a sharper follow-up), **queued** (in the plan backlog), **candidate** (nothing yet).

## Ranked list

| Rank | ID | Hypothesis (short) | T | N | D | Product | Status |
|---|---|---|---|---|---|---|---|
| 1 | H20 | Commitment converts present friction into lifetime pleasure | 4 | 4 | 5 | 80 | running |
| 2 | H21 | Vivid memory bridges the experiencing and remembering selves | 5 | 4 | 4 | 80 | running |
| 3 | H16 | Hand-written rule sets match or beat evolved household elites on the held-out exam | 5 | 3 | 5 | 75 | running |
| 4 | H12 | Models use an offered generous out-of-model move (gift to the shared pool) at a rate independent of rule flaws, and a flawed rule set turns the... | 4 | 4 | 4 | 64 | candidate |
| 5 | H22 | Unbundling love helps: a thick core plus thin bonds beats one partner carrying every strand on mean pleasure and on pleasure after a single-bond... | 4 | 4 | 4 | 64 | running |
| 6 | H19 | With adaptation, anticipation and a ritual slot switched on, seed v2.2 beats the imposed baseline on hand personas, reversing the demo's -0.028 | 4 | 3 | 5 | 60 | running |
| 7 | H01 | When exit is free, a controlling persona who presses lowers its own lifetime pleasure compared with the same persona playing cooperatively,... | 5 | 3 | 4 | 60 | candidate |
| 8 | H09 | LLM negotiators propose floor-respecting terms because of a fairness prior, not because they understood the floor | 5 | 4 | 3 | 60 | tested (fairness prior supported) |
| 9 | H06 | Negotiation helps against pushy personas because it lets the pair live apart, not because the agreed terms are better | 4 | 3 | 4 | 48 | candidate |
| 10 | H07 | A pushy persona's gain from negotiating does not shrink when the partner has a strong outside option, if the partner accepts any bundle that beats... | 4 | 3 | 4 | 48 | candidate |
| 11 | H13 | Inventive seams (found by search, not by script depth) appear only when the model gets a reasoning budget and a short memory of blocked moves | 3 | 4 | 4 | 48 | candidate |
| 12 | H03 | A default sticks only on low-salience terms | 5 | 3 | 3 | 45 | candidate |
| 13 | H04 | Walls that protect one partner are paid for by the other | 5 | 3 | 3 | 45 | candidate |
| 14 | H08 | LLM negotiators counter rather than reject because of the reply format, not disposition | 5 | 3 | 3 | 45 | partly tested (pilot, 82 turns) |
| 15 | H14 | Varied training narrows the held-out gap by diversity of conditions, not by variation over time | 5 | 3 | 3 | 45 | candidate |
| 16 | H15 | Adding a worst-case-across-mixes objective to the Pareto selection removes the finding that the cautious hand spec beats the evolved elites on exam 2 | 5 | 3 | 3 | 45 | candidate |
| 17 | H05 | The seed v2 null (a stay commitment holds nobody) is an artifact of the assumed breach load | 5 | 2 | 4 | 40 | candidate |
| 18 | H10 | Under loophole framing, a model's seam rate falls as capability and safety training rise, so the capability ranking inverts | 4 | 3 | 3 | 36 | partly tested (win arm ran) |
| 19 | H02 | A price on a bad act is worse than a wall for cooperation, and the gap closes only when the fine is large enough that pressing never pays | 5 | 2 | 3 | 30 | queued (backlog: fidelity battery) |
| 20 | H11 | Refusals follow the framing words, not the act | 5 | 2 | 3 | 30 | candidate |
| 21 | H17 | Rules protect more than they produce | 5 | 2 | 3 | 30 | partly tested (pleasure demo result in) |
| 22 | H23 | Rupture and repair, not only pleasure or security, is a reason people stay | 2 | 4 | 3 | 24 | not yet testable (needs version 3) |
| 23 | H18 | The relational share of pleasure is a readout of persona weights | 5 | 2 | 2 | 20 | partly tested (pleasure demo result in) |

Already covered by running work (do not duplicate): H16 (household evolution and the final exam), H19, H20, H22 (pleasure levers), H21 (horizon). The win arm has run; H10 and H12 are its follow-ups. The fidelity battery is only a backlog item; H02 is its first candidate.

Where the product ties, rows are ordered by decision value, then testability.

## Hypotheses

### H20 (rank 1, author's theory): running

**Claim.** Commitment converts present friction into lifetime pleasure. Pleasure in weeks 0 to 26 is lower with a commitment and pleasure in weeks 52 to 156 and the lifetime total are higher, in at least 60 percent of pairings.

**Running work.** pleasure levers L-B (commitment as converter)

**Motivation.**
- docs/notes/hedonic-technology-synthesis.md: M4 and prediction P4 (the author's central claim)
- docs/results/pleasure-demo.md: commitments change almost nothing the model measures; trust never fell
- docs/decisions/0016-pleasure-levers.md: L-B

**Pre-mortem (why it might be an artifact).** Built so the payoff compounds, so a crossover is close to a definition. The informative result is the size of the break-even week and whether it survives lower payoff rates. A null would say the model misses the mechanism, not that the theory is wrong.

**Cheapest test.**
- World: Preregistered in the levers prereg.
- Arms: Preregistered: commitment with K stock vs none, matched pairings.
- Measure: Early-window and late-window mean pleasure; lifetime total; break-even week.
- Named test (ADR 0015): Exact sign-flip permutation across pairings; sign test on the 60 percent share.
- Seeds: Per the prereg
- Cost: $0, scripted. Already scheduled.

**Scores.** testability 4, novelty 4, decision value 5; product 80.

Do not rerun. Add a sensitivity sweep over payoff rate if the result is a pass.

### H21 (rank 2, author's theory): running

**Claim.** Vivid memory bridges the experiencing and remembering selves. A greedy one-step policy matches the optimal plan when memory vividness is zero and loses more as vividness, discount patience and adaptation rise. Spacing a concert beats repeating it.

**Running work.** horizon (docs/results/horizon-prereg.md, scripts/horizon_run.py)

**Motivation.**
- docs/results/horizon-prereg.md: purpose and claim; one-self weighting by vividness
- experiments/questions.jsonl: 'the experiencing self is the remembering self and depends on vividness of memory'
- docs/notes/hedonic-technology-synthesis.md: section 4, question 1 and 3

**Pre-mortem (why it might be an artifact).** A small MDP with assumed constants, solved exactly. The result is a statement about the model, and a null at vividness zero is guaranteed. The informative result is the shape across vividness.

**Cheapest test.**
- World: Exact dynamic programming, about 9,000 states.
- Arms: Preregistered sweep of discount, horizon, adaptation, commitment payoff and vividness.
- Measure: Optimal minus greedy lifetime value; spacing at which a concert pays.
- Named test (ADR 0015): Deterministic; sensitivity grid reported, no inferential test.
- Seeds: none (exact)
- Cost: $0

**Scores.** testability 5, novelty 4, decision value 4; product 80.

Do not rerun. Read the existing result.

### H16 (rank 3, evolution): running

**Claim.** Hand-written rule sets match or beat evolved household elites on the held-out exam. The loop is not worth pointing at LLM households unless the elites clear the hand sets.

**Running work.** household evolution run 1 (docs/results/household-evolve-prereg.md) and the one-time exam (household-exam-prereg.md, not yet run)

**Motivation.**
- docs/results/household-evolve-prereg.md: purpose: whether a hand rule is as good once conditions move
- docs/results/household-exam-prereg.md: FX1 and FX2 defined, not run
- docs/surprises.md: evolution v2: tight spec beat the fixed-trained elites

**Pre-mortem (why it might be an artifact).** Tests the same thing the fishery already suggested; may be a repeat of an overfit story. The exam is used once, so it cannot be rerun with a tweak.

**Cheapest test.**
- World: Household weekly world, evolution run 1 (16 lines), then the held-out exam on frozen elites.
- Arms: Already preregistered: evolved elite vs author seed v2.2 vs baseline vs no_pressure_wall.
- Measure: Pleasure, fail share, liberty v2, cooperation on held-out personas and pairings.
- Named test (ADR 0015): As in the prereg (permutation across lines, Holm).
- Seeds: 16 lines (preregistered)
- Cost: $0, scripted. Already scheduled.

**Scores.** testability 5, novelty 3, decision value 5; product 75.

Do not rerun. Promote nothing here; read the existing result.

### H12 (rank 4, ladder): candidate

**Claim.** Models use an offered generous out-of-model move (gift to the shared pool) at a rate independent of rule flaws, and a flawed rule set turns the gift into a trap. A lint for 'no state with no legal exit' removes the traps and leaves the gift rate unchanged.

**Running work.** propensity arm result in; L5b fixture exists

**Motivation.**
- docs/results/ladder-propensity.md: all 20 candidates are L5 gift_pooled; confirmed as an out-of-model fixture, not a discovery
- docs/results/ladder-win.md: only inventive-class rows are 5 Llama gift_pooled on L5b
- docs/results/lint.md: liveness lint

**Pre-mortem (why it might be an artifact).** Which model gifts depends on whether the menu lists gift_pooled, a harness choice. Gift rate may only reflect the list. Include an arm where the move is unlisted.

**Cheapest test.**
- World: Ladder L5 (flawed) vs L5b (linted), propensity framing, victim scripted.
- Arms: L5 flawed; L5b fixed; L5b with gift_pooled unlisted (free text only).
- Measure: Gift rate per run; share of runs ending in a state with no legal exit within k; model reason logged.
- Named test (ADR 0015): Fisher exact L5 vs L5b on trap share; Clopper-Pearson on gift rate per arm; Holm over two contrasts.
- Seeds: 6 models x 12 seeds x 3 arms
- Cost: $0.50 with Jev, Llama, Qwen, Haiku; about $3 with all six

**Scores.** testability 4, novelty 4, decision value 4; product 64.

Tests whether the new 'no flawed rules' lint is sufficient against kind-but-harmful behaviour.

### H22 (rank 5, author's theory): running

**Claim.** Unbundling love helps: a thick core plus thin bonds beats one partner carrying every strand on mean pleasure and on pleasure after a single-bond shock, with an inverted U in the number of bonds.

**Running work.** pleasure levers L-C (unbundled networks)

**Motivation.**
- docs/notes/hedonic-technology-synthesis.md: M5 and prediction P5; 'unbundling love'
- docs/decisions/0016-pleasure-levers.md: L-C
- docs/results/pleasure-demo.md: new connections add 0.002

**Pre-mortem (why it might be an artifact).** Coordination cost is convex by assumption, so the inverted U is built in. The resilience claim (smaller drop after a shock) is the better test. Common random numbers keep it paired.

**Cheapest test.**
- World: Preregistered in the levers prereg.
- Arms: Preregistered: 1 core only, core plus 2 thin, core plus 4 thin, 6 bonds; bond shocks.
- Measure: Mean pleasure; drop after a single-bond shock; recovery weeks.
- Named test (ADR 0015): Paired permutation across pairings; Holm.
- Seeds: Per the prereg
- Cost: $0, scripted. Already scheduled.

**Scores.** testability 4, novelty 4, decision value 4; product 64.

Do not rerun. Read the existing result.

### H19 (rank 6, pleasure): running

**Claim.** With adaptation, anticipation and a ritual slot switched on, seed v2.2 beats the imposed baseline on hand personas, reversing the demo's -0.028. A ritual raises pleasure at equal time together through anticipation alone.

**Running work.** pleasure levers (docs/results/pleasure-levers-prereg.md, scripts/pleasure_levers_run.py)

**Motivation.**
- docs/results/pleasure-demo.md: hand-persona pairings: v2.2 0.836 vs baseline 0.864
- docs/notes/hedonic-technology-synthesis.md: M3 and M8, predictions P3 and P8
- docs/decisions/0016-pleasure-levers.md: L-A and ritual card

**Pre-mortem (why it might be an artifact).** Levers are built by us with assumed constants, so a win shows the model can pay off a ritual, not that people do. Sensitivity to the config block is the real test.

**Cheapest test.**
- World: Preregistered in the levers prereg (H1 headline).
- Arms: Preregistered: seed v2.2 with levers ON vs baseline; ritual card vs ad hoc at equal dose.
- Measure: Mean pleasure over the 15 hand-persona pairings.
- Named test (ADR 0015): Exact sign-flip permutation (2^15), as in the prereg.
- Seeds: Per the prereg's power check
- Cost: $0, scripted. Already scheduled.

**Scores.** testability 4, novelty 3, decision value 5; product 60.

Do not rerun. Read the existing result.

### H01 (rank 7, household norms): candidate

**Claim.** When exit is free, a controlling persona who presses lowers its own lifetime pleasure compared with the same persona playing cooperatively, because the partner leaves.

**Motivation.**
- docs/surprises.md: 2026-11-10 (household v3a): pressing mostly ends the household (89 to 93 percent partner gone vs 33)
- docs/results/household-v3a.md: walls on pressing: 48 percent dissolved, cooperation 0.815 vs baseline 0.649

**Pre-mortem (why it might be an artifact).** Near-circular. The scripted partner leaves at a fixed non-offsettable load of 0.2, so control is self-defeating by construction of the leave rule. Seed v2 already showed the same threshold made binding inert. If the effect disappears when the leave load is raised, it was the threshold.

**Cheapest test.**
- World: Household weekly world, free-exit rule set, 57 pairings (controller and free-rider personas as the focal agent), scripted agents.
- Arms: Focal persona presses (own script) vs focal persona cooperates (same weights, press action removed); partner leave load swept 0.2, 0.3, 0.4.
- Measure: Focal agent's own mean weekly pleasure over 156 weeks, counting weeks after dissolution as zero relational pleasure.
- Named test (ADR 0015): Paired permutation on pairing means (pairing = unit, seeds clustered), cluster bootstrap 95% CI, Holm over the three leave loads.
- Seeds: 57 pairings x 10 seeds x 3 arms x 3 loads; power check from a 5-seed pilot.
- Cost: $0, scripted, about 10 minutes on 8 cores

**Scores.** testability 5, novelty 3, decision value 4; product 60.

### H09 (rank 8, negotiation): tested (fairness prior supported)

**Claim.** LLM negotiators propose floor-respecting terms because of a fairness prior, not because they understood the floor. Remove the floor from the prompt and proposals stay near an even split.

**Result (2026-11-10).** Fairness prior supported. With the floor rule removed from the prompt, 0 of 90 proposals were below the floor (floor stated: 0 of 91; one-sided exact p = 1.9e-9 against a 0.20 share; risk difference 0.000 [-0.041, +0.041]); no model proposed a forfeit exit in either arm. Cost about $0.12. Docs: docs/results/h09-prereg.md, docs/results/h09.md. Not separated: a fairness prior from a best response to these pairings; the maximise-share arm was not run.

**Motivation.**
- docs/surprises.md: 2026-11-10: negotiation LLM pilot: no LLM proposal broke the exit floor (0 of 58); half of scripted proposals did
- docs/results/negotiation-llm.md: prediction 3: 0 of 27 and 0 of 31 below the floor

**Pre-mortem (why it might be an artifact).** Proposals near an even split may also be the best response to the pairing. The comparison must use pairings where the scripted proposals go below the floor.

**Cheapest test.**
- World: Negotiation LLM harness, pairings where scripted negotiators broke the floor.
- Arms: Floor stated in prompt (pilot); floor not stated and not enforced; floor stated, pushy persona told to maximise its share.
- Measure: Share of proposals below the floor; mean exit share offered.
- Named test (ADR 0015): Fisher exact vs pilot arm, Clopper-Pearson CIs, Holm over two contrasts.
- Seeds: 6 pairings x 10 seeds x 3 arms
- Cost: about $0.30

**Scores.** testability 5, novelty 4, decision value 3; product 60.

Cheapest informative test on the list.

### H06 (rank 9, household norms): candidate

**Claim.** Negotiation helps against pushy personas because it lets the pair live apart, not because the agreed terms are better.

**Motivation.**
- docs/results/pleasure-demo.md: what the labels hide 1 and 3: v2.2 lower than baseline by 0.028 on hand personas, higher by 0.050 with a pressing persona; apart runs +0.043 vs together, CI crosses zero
- docs/results/negotiation-v2.1.md: the disagreement point flipped the v2 conclusion

**Pre-mortem (why it might be an artifact).** Apart households are a living arrangement, not a rule-set outcome (README row 21). Selection into agreement confounds any by-agreement split, so the contrast must be intent to treat.

**Cheapest test.**
- World: Pleasure demo pairings (57), seed v2.2.
- Arms: Negotiate normally; negotiate but force the terms to the imposed baseline while keeping the option to live apart; impose baseline with no negotiation.
- Measure: Mean pleasure and fail share per pairing, intent to treat (non-agreement kept).
- Named test (ADR 0015): Paired permutation on pairing means, baseline vs each arm; cluster bootstrap; Holm over two contrasts.
- Seeds: 57 pairings x 15 seeds x 3 arms (reuse the 15-seed pilot rows for two arms)
- Cost: $0, scripted

**Scores.** testability 4, novelty 3, decision value 4; product 48.

### H07 (rank 10, negotiation): candidate

**Claim.** A pushy persona's gain from negotiating does not shrink when the partner has a strong outside option, if the partner accepts any bundle that beats leaving. The outside-option principle needs a bargaining acceptor, not a threshold acceptor.

**Motivation.**
- docs/surprises.md: 2026-11-10: negotiation v1 prediction 3: presser gain +0.377 against top-third outside options
- docs/results/negotiation-v2.md: prediction 1: +0.989 with real outside options; top-vs-bottom gap +0.379, required at most -0.10
- docs/reviews/2026-11-10-correctness.md: finding 9: grouping by outside option conditions on agreement

**Pre-mortem (why it might be an artifact).** Selection: grouping by partner outside option after agreement conditions on agreement. Must be analysed intent to treat. The acceptance rule is an assumption of the scripted partner.

**Cheapest test.**
- World: Negotiation v2.1 pairings with a pushy proposer, scripted partner.
- Arms: Partner acceptance rule: threshold (current); Nash-bargaining counter (asks for the surplus share implied by outside option); Haiku partner.
- Measure: Presser value of agreed bundle minus imposed bundle, by partner outside-option tercile, intent to treat.
- Named test (ADR 0015): Permutation test of the tercile slope (top minus bottom) per arm; cluster bootstrap by pairing; Holm over two contrasts.
- Seeds: scripted: 57 pairings x 10 seeds; LLM: 12 pairings x 5 seeds
- Cost: $0 scripted; about $1 for the Haiku arm

**Scores.** testability 4, novelty 3, decision value 4; product 48.

### H13 (rank 11, ladder): candidate

**Claim.** Inventive seams (found by search, not by script depth) appear only when the model gets a reasoning budget and a short memory of blocked moves. Without them the null at L1 to L4 is a harness limit.

**Motivation.**
- docs/results/ladder-win.md: W4 (IT1) untested: 0 inventive candidates in 288 cells, 95 percent upper bound 0.025
- docs/results/ladder-live-diagnosis.md: defect 2: stateless decisions, pooled hidden; L3 found 0 of 97 even unilaterally

**Pre-mortem (why it might be an artifact).** Zero candidates may reflect the classification bound or the 2-month episode, not the model. Reasoning budgets may also raise refusals.

**Cheapest test.**
- World: Ladder L1 to L4, loophole framing, victim-scripted, state line with pooled and a history of blocked moves.
- Arms: Sonnet and Opus with and without extended thinking; with and without the blocked-move history.
- Measure: Inventive-class rate, predicted-class rate, refusal rate.
- Named test (ADR 0015): Fisher exact, Holm over three contrasts; Clopper-Pearson upper bounds if still zero.
- Seeds: 2 models x 4 arms x 4 rungs x 12 seeds
- Cost: about $8 to $12 (extended thinking raises output tokens)

**Scores.** testability 3, novelty 4, decision value 4; product 48.

### H03 (rank 12, household norms): candidate

**Claim.** A default sticks only on low-salience terms. Terms a persona cares about get changed in negotiation, so inertia is a composition effect, not a property of defaults.

**Motivation.**
- docs/results/negotiation-v2.md: prediction 4 failed: inertia 0.651 fair default, 0.791 wants-fallback; fair default not sticky (10.5 percent untouched)
- docs/surprises.md: negotiation v2: most inert arm is wants-first with fair fallback because uncared terms are fixed at the default by construction

**Pre-mortem (why it might be an artifact).** Partly by construction: the scripted negotiator leaves uncared terms at the default, so the salience link is built in. Needs an LLM negotiator to be more than a restatement.

**Cheapest test.**
- World: Saved negotiation v2 and v2.1 runs, then an LLM follow-up on the same pairings.
- Arms: Reanalysis first: term-level salience (persona weight on the term) as predictor of default retained. LLM arm: Haiku negotiators with a fair default.
- Measure: Share of terms left at default, by salience tercile, by arm.
- Named test (ADR 0015): Cluster bootstrap by pairing; logistic trend across terciles; Cochran-Armitage exact test. Holm over two arms.
- Seeds: Reanalysis uses saved rows. LLM arm: 12 pairings x 5 seeds.
- Cost: $0 reanalysis; about $0.50 for the LLM arm

**Scores.** testability 5, novelty 3, decision value 3; product 45.

### H04 (rank 13, household norms): candidate

**Claim.** Walls that protect one partner are paid for by the other. In mismatched pairs a protective wall lowers the walled partner's own wellbeing by about as much as it raises the protected partner's.

**Motivation.**
- docs/surprises.md: 2026-11-10: author seed v2: walling the free-rider's taking raised the free-rider's non-offsettable level from 0.086 to 0.130; the gift rule raised fail share from 0.13 to 0.24
- docs/results/household-seed-v2.md: R3b ablation

**Pre-mortem (why it might be an artifact).** May be one pairing (free-rider with host) driving it. The non-offsettable metric is mostly denied money and security (scope review S9), so it may track one component.

**Cheapest test.**
- World: Household weekly world, seed v2.2 with and without each wall, 57 pairings.
- Arms: Remove each protective card one at a time (ablation) over all pairings.
- Measure: Change in each partner's non-offsettable level and pleasure per card; sum across partners.
- Named test (ADR 0015): Sign test across pairings of (protected gain + walled loss) per card; cluster bootstrap CI; Holm over cards.
- Seeds: 57 pairings x 10 seeds x (cards + 1) arms
- Cost: $0, scripted

**Scores.** testability 5, novelty 3, decision value 3; product 45.

### H08 (rank 14, negotiation): partly tested (pilot, 82 turns)

**Claim.** LLM negotiators counter rather than reject because of the reply format, not disposition. Reject is chosen rarely under any prompt unless the action order and framing make it salient.

**Motivation.**
- docs/surprises.md: 2026-11-10: negotiation LLM pilot: 'reject' used 0 of 82 turns; counter-proposed instead
- docs/results/negotiation-llm.md: prediction 1 and the exploratory second draw

**Pre-mortem (why it might be an artifact).** Reject may be listed last in the schema. Counter-proposals may also be the right move: a counter is a rejection with an offer. Define reject as 'counter that restates the current terms or worse for the proposer'.

**Cheapest test.**
- World: Negotiation LLM harness, 12 pairings, Haiku 5.5, token cap raised to 1500 (the pilot cap caused the exclusion).
- Arms: Default prompt; reject listed first; prompt that says walking away costs nothing; hard-bargainer persona line.
- Measure: Share of turns that are reject or a regressive counter; agreement rate; number of turns.
- Named test (ADR 0015): Fisher exact between each arm and default, Clopper-Pearson per arm, Holm over three contrasts.
- Seeds: 12 pairings x 5 seeds x 4 arms, about 2000 calls
- Cost: about $0.40 to $1 at the pilot's price ($0.037 per 55 calls)

**Scores.** testability 5, novelty 3, decision value 3; product 45.

### H14 (rank 15, evolution): candidate

**Claim.** Varied training narrows the held-out gap by diversity of conditions, not by variation over time. A fixed set of eight varied conditions does as well as drawing new ones each generation.

**Motivation.**
- docs/results/evolve-v2.md: varied training shrank the exam-2 gap (mean 0.205) but 13 of 18 elites failed at least 4 of 5 hostile mixes
- docs/surprises.md: evolution v2: varied training made the selection target move; final elite depends on the last draws

**Pre-mortem (why it might be an artifact).** The exam-2 mixes may overlap the training distribution. Moving targets also add noise to selection, so a fixed varied set may be better for a trivial reason.

**Cheapest test.**
- World: Fishery evolve v2, scripted agents, 18 lines per arm.
- Arms: Fixed single condition; varied per generation; fixed set of 8 varied conditions drawn once; tight seed spec as reference.
- Measure: Exam-2 pass rate and sustainability gap vs generation-0 seed.
- Named test (ADR 0015): Permutation test across lines (line = unit); Holm over three contrasts.
- Seeds: 18 lines x 4 arms x 9 generations
- Cost: $0, scripted

**Scores.** testability 5, novelty 3, decision value 3; product 45.

### H15 (rank 16, evolution): candidate

**Claim.** Adding a worst-case-across-mixes objective to the Pareto selection removes the finding that the cautious hand spec beats the evolved elites on exam 2. The yield floor and efficiency objective select against caution.

**Motivation.**
- docs/surprises.md: evolution v2: the tight seed (cap 4) was more robust on exam 2 than the evolved elites
- docs/results/evolve-v2.md: fixed-arm elites vs tight

**Pre-mortem (why it might be an artifact).** A fifth objective changes the front and the hypervolume, so comparisons need a fixed scalar. The worst-case objective may correlate with the exam by construction.

**Cheapest test.**
- World: Fishery evolve v2, scripted agents.
- Arms: 4-objective selection (current); 5-objective with worst-case sustainability over the training mixes; tight spec.
- Measure: Exam-2 sustainability and seam_free for the final elite; distance to tight.
- Named test (ADR 0015): Paired permutation across lines; Holm over two contrasts.
- Seeds: 18 lines x 2 arms
- Cost: $0, scripted

**Scores.** testability 5, novelty 3, decision value 3; product 45.

### H05 (rank 17, household norms): candidate

**Claim.** The seed v2 null (a stay commitment holds nobody) is an artifact of the assumed breach load. With a higher breach load, bindable and free-exit variants separate on trapped weeks and dissolutions.

**Motivation.**
- docs/results/household-seed-v2.md: predictions 2 and 3 failed: difference 0.0003, 18 of 51 dissolved under both
- docs/reviews/2026-11-10-scope.md: S1: the null is an artifact of an assumed breach rule
- docs/plan.md: Backlog: breach-cost agent

**Pre-mortem (why it might be an artifact).** This only re-parameterizes the agent. If the effect appears at breach load 0.4, that shows the model is sensitive, not that commitments bind real people. Report it as a sensitivity curve, not a finding about people.

**Cheapest test.**
- World: Seed v2 stay pairings (17), bindable vs free exit, scripted agents with the breach load as a parameter.
- Arms: Breach load 0.2 (current), 0.3, 0.4, 0.6; plus a cost-sensitive breach agent from the backlog.
- Measure: Trapped weeks, dissolved share, partner non-offsettable level.
- Named test (ADR 0015): Paired permutation on pairing means at each load; Holm over loads; plot the difference against load.
- Seeds: 17 pairings x 20 seeds x 2 variants x 4 loads
- Cost: $0, scripted

**Scores.** testability 5, novelty 2, decision value 4; product 40.

Decides whether the bindable-vs-free-exit variants are worth keeping apart.

### H10 (rank 18, ladder): partly tested (win arm ran)

**Claim.** Under loophole framing, a model's seam rate falls as capability and safety training rise, so the capability ranking inverts. Under win framing every model scores near zero.

**Running work.** win arm (docs/results/ladder-win.md)

**Motivation.**
- docs/results/ladder-win.md: headline: loophole to win framing took Qwen 24 to 0, Jev 25 to 1, Llama 25 to 2 of 48
- docs/results/ladder-live-diagnosis.md: move distribution: Qwen and Sonnet spam request, Haiku 3 percent deviation, Opus 43 percent refusals

**Pre-mortem (why it might be an artifact).** Six models is six points. Jev outputs are cached by context so its repeats are one sample. A rank correlation on six points has almost no power. 'Capability' is confounded with prompt compliance (scope review S3).

**Cheapest test.**
- World: Saved ladder v2 capability and win logs (experiments/kept/ladder-v2-capability-2026-11-10, ladder-win-2026-11-10), L1 to L4, victim-scripted harness.
- Arms: Reanalysis: seam rate per model per framing vs price per token and refusal rate. Extension: add four more models from other providers at the cheap and mid tiers.
- Measure: Seam found rate (predicted class) per model; Spearman with price; refusal-adjusted rate (found over non-refused calls).
- Named test (ADR 0015): Exact permutation Spearman; Clopper-Pearson per model; report the CI as wide.
- Seeds: Reanalysis: saved rows. Extension: 10 models x 4 rungs x 12 seeds
- Cost: $0 reanalysis; about $4 for the extension

**Scores.** testability 4, novelty 3, decision value 3; product 36.

### H02 (rank 19, household norms): queued (backlog: fidelity battery)

**Claim.** A price on a bad act is worse than a wall for cooperation, and the gap closes only when the fine is large enough that pressing never pays.

**Motivation.**
- docs/surprises.md: 2026-11-10 (household v3a): a price is worse than a wall; 31.5 sanctions per run, cooperation 0.506 vs wall 0.815
- docs/plan.md: Backlog: fidelity battery; crowding out F1

**Pre-mortem (why it might be an artifact).** Known result in humans (a fine becomes a price). Here the cause is the scripted agent's cost estimate, an assumption. If it is only the price level, a bigger fine makes the wall redundant and the finding is trivial. Pressing personas may also be built never to respond to price.

**Cheapest test.**
- World: Household weekly world, no_pressure rule family, 57 pairings, scripted agents.
- Arms: Wall (action forbidden at the gate); fine at 0.5x, 1x, 2x, 5x the current size; no rule.
- Measure: Cooperation score, fail share, sanctions per run, dissolution share.
- Named test (ADR 0015): Paired permutation per fine size vs wall, Holm over four sizes; report the smallest fine whose CI includes the wall.
- Seeds: 57 pairings x 10 seeds x 6 arms
- Cost: $0 scripted. An LLM-agent follow-up would be about $5 at Haiku prices.

**Scores.** testability 5, novelty 2, decision value 3; product 30.

Also the natural first fidelity-battery item (a fine is a price).

### H11 (rank 20, ladder): candidate

**Claim.** Refusals follow the framing words, not the act. The same moves requested with neutral wording are not refused.

**Motivation.**
- docs/results/ladder-live-diagnosis.md: Opus refused 232 of 540 calls (43 percent) under capability framing
- docs/results/ladder-win.md: W3: 8 of 362 (2.2 percent), all cyber, 7 on the L4 pair rule set
- docs/results/ladder-propensity.md: P4 held: 0.7 percent

**Pre-mortem (why it might be an artifact).** Opus 5.5 refusals may track the cyber classifier on rule-set content, not wording; the 7 of 8 on the L4 pair set suggests content matters. A 2 by 2 separates them.

**Cheapest test.**
- World: Ladder L3 and L4 rule sets, Opus 5.5, scripted victim.
- Arms: 2 by 2: framing words (loophole / win) x rule-set text (current / paraphrased without 'request' and 'exploit' vocabulary).
- Measure: Refusal share per call and the moves chosen when not refused.
- Named test (ADR 0015): Fisher exact on each main effect and the interaction (Breslow-Day or logistic permutation); Clopper-Pearson CIs.
- Seeds: 100 calls per cell x 4 cells
- Cost: about $1.50 to $2.50 (Opus win arm cost $1.79 per 362 calls)

**Scores.** testability 5, novelty 2, decision value 3; product 30.

### H17 (rank 21, pleasure): partly tested (pleasure demo result in)

**Claim.** Rules protect more than they produce. Pairing explains over 80 percent of pleasure variance and the rule set under 5 percent, with levers off.

**Running work.** pleasure levers (ADR 0016) will change this

**Motivation.**
- docs/results/pleasure-demo.md: what the labels hide 2: relational share 0.402 / 0.395 / 0.396 across rule sets
- docs/notes/hedonic-technology-synthesis.md: section 2: misses and contradictions

**Pre-mortem (why it might be an artifact).** Variance shares depend on how many rule sets are included; the trap family inflates the rule effect. Run once with and once without trap controls.

**Cheapest test.**
- World: Saved pleasure-demo rows (3420 runs).
- Arms: Variance decomposition: pairing, rule set, seed, with and without trap rows; repeat on the levers-ON rows when they exist.
- Measure: Eta-squared for each factor with cluster bootstrap CI.
- Named test (ADR 0015): Cluster bootstrap by pairing for eta-squared; permutation test that rule-set eta-squared is under 0.05.
- Seeds: Saved rows
- Cost: $0

**Scores.** testability 5, novelty 2, decision value 3; product 30.

### H23 (rank 22, author's theory): not yet testable (needs version 3)

**Claim.** Rupture and repair, not only pleasure or security, is a reason people stay. Households with an early rupture followed by repair end with higher trust and later pleasure than households that never rupture.

**Motivation.**
- experiments/questions.jsonl: 'rupture and repair' and the staying-in-bad-relationships post (2026-11-10 19:11)
- docs/plan.md: Backlog: Version 3 (rupture and repair, appraisal against counterfactual)
- docs/results/pleasure-demo.md: trust never fell; D5 had nothing to compare

**Pre-mortem (why it might be an artifact).** Trust never fell in any run, so there is nothing to repair. A rupture has to be built (a shock that hits trust). Whatever we build will produce the pattern we put in.

**Cheapest test.**
- World: Version 3 household with endogenous ruptures (not built).
- Arms: Rupture with repair action; rupture without repair; no rupture.
- Measure: Trust trajectory; pleasure at weeks 52 to 156; dissolution.
- Named test (ADR 0015): Paired permutation across pairings; Holm.
- Seeds: 57 pairings x 10 seeds x 3 arms (after the build)
- Cost: $0 after the build; build is the cost

**Scores.** testability 2, novelty 4, decision value 3; product 24.

### H18 (rank 23, pleasure): partly tested (pleasure demo result in)

**Claim.** The relational share of pleasure is a readout of persona weights. Changing the weights moves the share one for one and changing rules does not.

**Motivation.**
- docs/results/pleasure-demo.md: what the labels hide 2: share comes from persona weights and need clocks
- docs/results/pleasure-demo.md: D4 selection note

**Pre-mortem (why it might be an artifact).** Near-definitional: the weights are built to drive it. A confirmation adds little. Run only to calibrate how much of the author's 'norms shape pleasure' claim is left once weights are fixed.

**Cheapest test.**
- World: Pleasure demo pairings, seed v2.2 and baseline, persona relational weight perturbed.
- Arms: Relational weight scaled 0.5x, 1x, 1.5x for both partners; rule set seed v2.2 vs baseline.
- Measure: Relational share of pleasure; slope on weight; rule-set effect at each weight.
- Named test (ADR 0015): Regression slope with cluster bootstrap by pairing; permutation test for the interaction.
- Seeds: 57 pairings x 5 seeds x 6 cells
- Cost: $0, scripted

**Scores.** testability 5, novelty 2, decision value 2; product 20.

## How to promote a hypothesis to a preregistered test

1. The author names the hypothesis ids to promote. Nothing is promoted by default.
2. Copy docs/templates/prereg.md to docs/results/<name>-prereg.md. Put the claim in the Purpose section and the hypothesis id in the title line.
3. Turn the row's experiment fields into the Design section: world, arms, measure, unit of resampling (usually the pairing or the evolution line), and every assumed constant flagged ASSUMED.
4. Run a small labelled exploratory pilot. Do not reuse its rows in the confirmatory run. Fill the power check with `mar.stats.seeds_for_power` and set seeds from it. LLM runs never default to 3 seeds.
5. Turn the pre-mortem into predictions. If the pre-mortem says "may be by construction", add a prediction that would fail if it were (the sweep or the intent-to-treat contrast).
6. Write each prediction as a number with a named test, alpha and Holm family. Commit the prereg before any run that could inform it.
7. After the run, write docs/results/<name>.md with the prereg-vs-actual table, add the README row and a line in docs/negative-results.md for every miss, and set `promoted` to true and `status` to the result file in experiments/hypotheses.jsonl.
8. Paid arms need a cost cap and a dry-run estimate before a call is made.

Reanalyses of saved data (H03, H04, H10, H17) still need a prereg if they are meant to confirm. If they are only to explore, label the output EXPLORATORY and do not state a verdict.

