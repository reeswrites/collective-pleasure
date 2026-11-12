# Step-back review: how agents decide, the pleasure cap, and what still stands

Wording rule: agents feel nothing; "pleasure", "suffering" and "value" are glosses for modeled numbers.

Status: 2026-11-12. An independent design review, written by an agent at the author's request after the bill-horizon run ("step back before more patches"). No code changed, no experiment run. One timing probe (a world copy and a simulated week, below). Sources: the results index and the files it names, docs/limits.md, docs/notes/performance.md, and the code in `hedonic.py`, `agent_values.py`, `negotiation.py`, `personas.py` and `worlds/household.py`. Where this note reads the code differently from a results file, it says so.

## In one paragraph

The three H38 answers (+0.021, −0.046, −0.003) did not come from three versions of one agent. They came from three things moving at once: the weekly policy (v1 to v2), the world (bills that hurt, on for v2 and v2b only), and the yardstick of the big choices (net wellbeing over 26 weeks, then own pleasure over 52). Underneath all three sits the weekly cap on pleasure. Needs met plus aspirations met already add up to exactly the cap, so nearly everything a household adds on top (time together, items, the pairing reward, glow) lands above it and counts for nothing. An agent that values its week accurately on that scale will find households worth little, and that is roughly what v2 did. So the order of repair matters: **fix the scale first, then the agents.** For the agents, I recommend the hybrid: one-week accurate choices for the weekly routine, simulated choices for commitments, with bills handled by a household agreement rather than by agent foresight. Of 54 ledger entries (49 rows, five split in two), 15 depend on the agents, 29 do not, and 10 are unclear. What still stands is mostly the exact small models, the instruments, and the structural lessons, plus one H38 finding that the pleasure numbers have hidden: pressure holds people in under every agent set.

## What actually moved between v1, v2 and v2b

H38's old-rule effect of pressure (L4 minus L0), and week-0 formation under the corrected rule (G-L0):

| Agents | Bills hurt | Weekly values | Old-rule L4 − L0 | G-L0 formed at week 0 | Formed households that end |
|---|---|---|---|---|---|
| v1 | no | heuristic, mixed units | +0.021 | 0.84 | 0.29 |
| v2 | no | the week's clipped close | −0.047 | 0.77 | 0.97 |
| v2 | yes | the same | −0.046 | 0.06 | 0.81 |
| v2b | yes | the same, plus a bill credit | −0.003 | 0.42 | 0.72 |

Read down the table, not across the headline. The sign flip comes from v1 to v2 with no bills at all (+0.021 to −0.047). The collapse in formation comes from adding bills. v2b's partial recovery comes from the bill credit undoing what the bills did. So "three agent versions" is really one agent change, one world change, and one patch to make the agent survive the world change.

Why would accurate one-week agents leave households that v1 agents kept? My reading of the code, not tested on its own: v1 valued time together through the connection need and the together aspiration, which have no ceiling in the agent's own arithmetic. v2 values the week's clipped close. Over one week the cap eats most of what time together does (value check: +0.099 unclipped, +0.026 clipped), and v2 prices a session at +0.009. Meanwhile a household's costs (the couple's bill at 1.67 times a single person's, limit 11; rest and money) sit below the cap, where they count in full. Any agent that values the capped week accurately will see household benefits it cannot count and household costs it can. That is a cap problem showing up as an agent problem.

Two smaller things the reruns did not separate:

- **Fixed scores in other units.** Under v2 only the scored actions moved to the model's scale. The propose-only scores stayed: leave on distress 0.9, a gift to the partner 0.12 and up, a refusal 0.12, a request 0.06 to 0.08, the controller's veto 0.25 and up (`PersonaAgent.propose`, `PressingAgent.propose`). Under v1, rest when tired was worth up to about 0.1, so these competed. Under v2, routine actions are worth about 0.02, so a gift or request now wins whenever it is offered. The recalibration prereg kept these on purpose, but nobody measured what the change in their relative rank does.
- **Clairvoyant rollouts.** `negotiation.played_copy` deep-copies the lived world, including its precomputed shock schedule (`WeeklyWorld.shocks`) and every random stream. So the status-quo forecast at a stay reading sees the actual job losses and illnesses of the next 26 or 52 weeks. The outside option is played in a fresh world with a different schedule. The stay decision compares a known future with a sampled one. This is in every agent version, so it does not explain the moves, but it is a bias in every formation and stay result.

## 1. How should agents decide?

The question under the question: which part of the results should depend on a modeling choice about cognition, and which should not? A good answer makes the cognition choice small, named, and testable, so that a result can be labelled "holds for any agent in this family" or "depends on trait X".

A point that shapes every option: **the project is already a hybrid.** Formation, retries and stay readings are chosen by simulating the world forward (`forward_values`, `alone_value`, `baseline_value`), and only the weekly routine is heuristic. What failed is that the forecasts replay lives played by the weekly heuristic, that the yardstick changed between experiments, and that one long-horizon stock (the shared pot) is fed by weekly choices that see one week.

### Cost baseline

From docs/notes/performance.md: a lived H38 run plays about 3,200 simulated weeks, about 20 per lived week (40 under the corrected 52-week rule). After the speedups, one run takes about 0.6 to 1.1 s with v1 agents and 2.8 s with v2b. A 6,720-run experiment is about 25 to 45 minutes on 3 to 4 workers.

Timing probe (this note, one process, p-anchor with p-host, F4 with items, levers on, week 20): a rollout copy of the world takes about 0.6 ms. One simulated week takes about 0.55 ms with v1 agents and 1.4 ms with v2b. In a week there are about six agent calls (two agents, three passes), each choosing among about six actions.

### Option 1: hand-tuned heuristics, patched further

What it buys: cheap runs (no change to the cost above), and full freedom to write any behaviour, including deliberate quirks.

What it costs: there is no stopping rule. Each patch fixes the gap the last check found and moves the headline. v2b also showed a limit no patch can pass: the value of paying a bill now depends on whether the same agent pays later, so a one-shot credit is wrong either way (+0.029 over, −0.026 under). The next patches (a month plan, a pot runway term) are reasonable, but each is another hand-made forecast with its own pass test.

Misforecasting as a trait: possible, but indistinguishable from bugs. The value check found four unintended gaps in v1 before it found a chosen one. A trait written into a heuristic is one more constant.

### Option 2: agents that choose by simulating the hedonic model

Each candidate action is played forward in a copy of the world for k weeks, and the agent picks the best. Consistent with the model by construction, relative to the policy that plays the later weeks.

Note that v2 already is the one-step version, done in closed form: `agent_values.week_net` mirrors `Hedonic.close_week`, which is why it passes at 0.99. One-step simulation buys nothing v2 does not have. The open question is the horizon, and that is where the cost is.

Cost of k-week look-ahead, order of magnitude: about 36 forks per simulated week (six calls, six actions), each a 0.6 ms copy plus k weeks at about 1 ms.

| Look-ahead | Per simulated week | Against now | H38 run, every simulated week plans | 6,720 runs, 4 workers |
|---|---|---|---|---|
| 4 weeks | about 0.17 s | about 150x | about 9 minutes | about 10 days |
| 13 weeks | about 0.5 s | about 500x | about 26 minutes | about a month |

If only the lived weeks plan and the rollouts keep the cheap policy, it is about 26 s (4 weeks) or 80 s (13 weeks) extra per run, so 12 to 36 hours per experiment. But then the formation forecasts replay a different agent from the one who lives, which is the inconsistency the formation check already exposed.

What it costs in modeling freedom: the agent becomes the model's own optimiser, so every behaviour is the model's arithmetic. Quirks have to be added as distortions of the forecast. And "consistent by construction" still needs a horizon and a policy for the later weeks, so v2b's counterfactual problem returns as a choice of base policy.

Misforecasting as a trait fits well here: a shorter horizon, a discount, projection bias (forecast with today's levels), optimism about the outside option, ignoring the partner's reaction. Each is one named parameter of the forecast.

### Option 3: hybrid (heuristics or v2 for the week, simulation for the big choices)

The shape the code already has, done properly. Weekly routine: v2's one-week values, already consistent at one week. Big choices (form, stay, leave, and any commitment such as a project or a budget): simulated, with three changes:

- **Sampled futures, not the real one.** Each option is scored on K rollouts with resampled shocks, not on the lived world's own schedule.
- **One declared yardstick.** By default the evaluator's own measure (on the repaired scale, section 2). A persona's own weighting, such as H39's suffering weight, is then a named trait, not a change of rule between experiments.
- **Long-horizon stocks go into agreements, not foresight.** The one stock that carries the long run is the shared pot (bill-horizon run: +0.72 of a payment's +1.00 over a year; money, rest and bonds carry little). Who pays which share of the month's bill is a household agreement, exactly the project's subject. Make it a term agreed at formation and kept, breached or renegotiated like any other card, instead of asking a one-week agent to foresee a settlement.

Cost: rollouts are already most of run time (the weekly step, played inside them, is 81 to 95% of every profiled workload). K = 4 sampled futures makes a run about 4 times slower: about 11 s for a v2b H38 run, about 5 hours for 6,720 runs on 4 workers. K = 8 is about 10 hours. The forward memo still works within a reading.

Modeling freedom: weekly behaviour stays writable (v2 plus named propose-only actions, now on the same scale). Big choices are the model's own, with traits as distortions of the forecast.

Misforecasting fits in one place: the big-choice forecast. Horizon, discount, sample count and outside-option bias are persona fields. The weekly routine stays accurate, and "people misjudge commitments more than Tuesdays" is a defensible default.

### Option 4: a much simpler, analyzable model

A closed-form or tiny-state model per hypothesis: for H38, two people, states apart, together and held, pressure as a stigma and a reward, exact dynamic programming over a few dozen states. The project has done this well already: horizon, liking vs wanting, H32-v2 and H35 all ran as exact solves, and they are the results that held up.

What it buys: robust qualitative results, such as a sign map ("pressure raises pleasure exactly when the formation rule under-forms by more than X"). Runs in seconds. Every verdict's reachability can be checked exhaustively.

What it costs: the emergent parts (the pattern atlas, the rule cards binding or not, liberty over real rule sets, the many-agent world). It cannot host H40, H38b or H36. And its conclusions are about its own equations: limit 6 ("passing predictions about the builder's own equations are code checks") applies in full.

Misforecasting fits as a parameter of the solve (a discount, a biased transition), and its effect can be read off exactly. This is the cleanest place to study it.

### Option 5: LLM agents for the big choices only

What it buys: decisions with reasons attached, and a direct link to the AI agents track.

What it costs: about 24 big choices per run (one formation and up to eleven readings or retries per member), so about 160,000 calls for a 6,720-run experiment. Row 22 spent $0.037 on 12 Haiku negotiations, about $0.003 each, which puts one experiment near $500 against past caps of $3 to $12. The ladder runs also met refusals (Opus 43% on the first ladder) and format errors (10% in row 22). And an LLM does not read the hedonic model, so the yardstick gap returns by design: it decides on the persona text and is scored on the model.

Misforecasting fits only as prompt text, and it cannot be measured against a known answer.

### Recommendation: option 3, with option 4 beside each hypothesis

The hybrid, for four reasons:

1. It is the smallest move from what exists. The weekly half (v2) already passes its check. The big-choice half already simulates. What changes is how it simulates (sampled futures, one yardstick) and where the long horizon lives (in an agreement).
2. It puts the cost where the consequences are. The headline moves came from formation and staying, not from whether someone rests on Tuesday. Simulating those choices costs about 4x, not 150x.
3. It moves the bill problem into the project's own subject. "Who pays the month's bill" becomes a norm that can be studied, breached and compared across rule sets, not a forecasting skill the agents lack.
4. It gives misforecasting one home. A bias is a named field of the big-choice forecast, measured against the model's own answer. "A chosen bias is a finding; the current one is an accident" (value-consistency.md) becomes enforceable.

Option 4 is the companion, not the alternative. Before a household rerun of any hypothesis, write the tiny exact model of its mechanism and get the sign map. The household then has to agree with it, or the disagreement has to be explained. That gives each claim a robust qualitative core that no agent version can move.

Options 1 and 2 are not recommended: 1 has no end, 2 costs days to weeks per experiment for a consistency the hybrid gets where it matters. Option 5 belongs on the AI agents track as its own question ("do LLM delegates choose households differently?"), not as the default agent.

## 2. The pleasure cap

### How it works

Each week, for each person, `Hedonic.close_week` computes

raw = 0.5 × needs + 0.5 × aspirations + 0.10 × together sessions + glow + extra

and pleasure = raw clipped to [0, 1]. The verdict measure is the mean of that clipped weekly number over both partners and 156 weeks. Offsettable and non-offsettable suffering are clipped the same way, each to [0, 1].

The key arithmetic: the needs term and the aspirations term are each in [0, 1], because saliences and aspiration weights are normalized to sum to 1. So **a person whose needs are all full and whose aspirations are all met is at raw 1.0 before anything else.** Every relational and event term sits on top: time together (0.10 a session), glow from a new connection (0.30), items' weekly pleasure, lever payoffs (anticipation, commitment, strand cover), bought pleasure, makers' pleasure, and H38's pairing reward. All of it counts only for someone who is short somewhere.

Negative terms in `extra` are clipped the same way. H38's stigma and exit stigma enter as negative `extra`, so for anyone with more than 0.08 of surplus they cost nothing. The cap hides costs as well as gains.

Three places the cap is not just a reporting choice:

- **The dynamics.** The spiral B moves on clipped pleasure (`B + eta × (pleasure − s_off) ...`), and capacity follows B. Surplus above the cap does not build capacity.
- **The agents.** v2 and v2b value the clipped close on purpose. At the cap, rest, friends and time together are worth nothing to them for the week (agent-recalibration.md, "What is still inconsistent"). The v2 pass test fails on unclipped pleasure (T1 0.70) for this reason.
- **The big choices.** Under the corrected rule (`decide_on="pleasure"`), formation and staying compare mean clipped pleasure, so the household's above-cap advantage is invisible to the choice.

### What it hides, in numbers

- **Most weeks are at the cap.** H38: 54% of person-weeks at L0, 70% at L4, 82% at L8. Formation check: 48% to 73%. Under v2b every formation arm sits at 0.97 to 0.99.
- **H38's size.** v1, L4 − L0: +0.021 clipped, +0.086 unclipped. The cap compressed the effect fourfold.
- **The one "stable" verdict.** C1 ("pressure does about nothing under the corrected rule") is the result the bill-horizon file calls stable across all three agent sets. On unclipped pleasure it is +0.050 (v1) and +0.080 (v2b): pressure clearly raises unclipped pleasure, mostly because the reward lands above the cap, and on that scale C1 would fail. The margin is also one-sided: under v2 C1 "held" at −0.038, a clear harm. So the one verdict that stayed constant meant three different things (no effect, harm, no effect), and it held only on the capped scale.
- **Time together.** One week of it: +0.099 unclipped, +0.026 clipped (value check).
- **The wanting trap.** H39: a receiver at full tolerance and full sensitization for two years reads 1.00. H39b: of persons trapped in at least a quarter of their weeks, 58% average clipped pleasure of 0.95 or more (70% under w = 0, where traps nearly triple and pleasure is highest).
- **Crediting.** H39b, BP − Z: −0.0027 clipped (null) and −0.007 unclipped (below 0). Whether "a tally lowers pleasure" survives depends on the scale.

The cap also bends the evaluator rule. "Raises freedom without costing pleasure" is easy to meet when the cost falls on surplus above the cap, so freedom gains look free for the well-off. And the project's own thesis, pleasure through collective means, lives almost entirely in the terms the cap deletes for satisfied people.

### Options

**(a) Uncapped pleasure as the primary.** What it changes: every term counts linearly and without limit. The evaluator's "raises pleasure" becomes a sum of assumed event sizes. H38 would read as a clear gain, mostly because the 0.02 × L reward is paid in full while together. Agents valuing it would chase events with no satiation, except where the adaptation lever is on. It reports what the equations add up to, and gives the assumed magnitudes much more weight than the project can defend.

**(b) A saturating transform.** Replace the hard wall with a curve: identical to today below a knee, then rising ever more slowly toward an asymptote. For example f(x) = x below k = 0.8, and k + (1 − k)(1 − exp(−(x − k)/(1 − k))) above it. It is continuous and has slope 1 at the knee. What it changes: surplus counts, with diminishing returns, so stigma, reward, items and time together are visible but bounded. Results that never reached 0.8 do not move. The evaluator gains a mild prioritarian tilt: an equal raw gain counts more for someone lower down. Under "everyone counts", that should be said out loud. Margins (0.007 in the formation check) need restating on the new scale before any rerun. The knee and the curve are choices, and should be made for reasons and fixed before any result is seen.

**(c) Distributions instead of means.** Report the share of person-weeks at or near the top, quantiles, and the worse-off partner, beside the mean. What it changes: nothing in the model. It shows where the mean is compressed, and is useful under any option. On its own it does not repair the agents, which choose on the capped number.

**(d) Treat the cap as real satiation.** Declare that a person whose needs and aspirations are met cannot have more pleasure in a week. What it changes: nothing in the code. It makes current results claims about a theory in which stigma costs a satisfied person nothing and a relationship adds nothing to someone already doing well. That is a strong claim, at odds with the project's own notes on hedonic technology, and it would need defending as a claim about pleasure, not as a convenience.

### Recommendation: (b), applied everywhere at once, with (c) beside it

One saturating transform, used in the same place the clip is now, so the spiral, the agents and the evaluator all read the same number. The legacy clipped line stays as a sensitivity line for one round, so every earlier result can be set beside it.

Why not (a): it makes the verdict a sum of assumed event magnitudes. Why not (d): it is a substantive theory the project does not hold. Why (b) and not (c) alone: the agents choose on this number, and the review's reading is that the cap is part of why accurate agents leave households.

What it changes in the evaluator: "raises pleasure" means a rise in mean transformed pleasure, and the rule should say the transform is concave on purpose. "Without costing pleasure" becomes checkable for well-off people too. Every margin and power check needs restating on the new scale.

## 3. Findings ledger

Labels:

- **A**: depends on the agents' decision rules. It moved across v1, v2 and v2b, or runs on v1 household agents in a way the moves suggest would shift.
- **B**: mechanical, analytic, or a property of an instrument. It holds whatever the household agents do.
- **C**: unclear.

"cap" marks a result whose size or sign rests on the clipped pleasure scale. Rows with two separable findings are split (27, 41, 46, 48, 49), so there are 54 entries.

| # | Result | Label | Why, in one line |
|---|---|---|---|
| 1 | V2 instrument calibration | B | Deterministic check of the gate, oracle and miner on mock agents. |
| 2 | V2b English surface | B | Lossless round trip; a property of the compiler. |
| 3 | Workbench | B | Tooling, not a finding. |
| 4 | Household v1 | A | The monthly world's frontier and cooperation came from who the agents were (proof checks inside it are B). |
| 5 | Seam ladder | B | Scripted calibration: each agent finds seams at its depth, by construction. |
| 6 | VPGG rediscovery | B | Its own replicator model; shares match at one point, no cycles. Not household agents. |
| 7 | Bargaining rung | B | Closed forms reproduced; an implementation check. |
| 8 | Empowerment | B | Exhaustive enumeration. |
| 9 | Evolution v1 (fishery) | C | Not household agents, but the loop's overfitting is measured against one scripted adversary set. |
| 10 | Evolution v2 (fishery) | C | Same; varied training narrowed the exam gap only suggestively. |
| 11 | Household v2 (hedonic) | A, cap | "Seed equals baseline" rests on scripted agents never trying what the cards forbid; the file itself notes saturated pleasure. |
| 12 | Household v3a | A | Pressing personas end households "by design of the personas and the leave rule" (the index's gains-only flag is a B side note). |
| 13 | Author seed v2 | B | The stay-bind null is a property of the fixed breach load, as the file says; robust in the multiverse. |
| 14 | Liberty v1 | B | Enumeration; exit counted as domination. |
| 15 | Liberty v2 | B | Enumeration; the classification was chosen with v1's failure in view. |
| 16 | Live ladder, capability | B | Uninformative by harness design (no victim). |
| 17 | Live ladder, propensity | C | LLM behaviour on a flawed fixture; not about household agents, but not mechanical either. |
| 18 | Household final exam | A | Scores elites against scripted v1 agents on held-out personas. (The index still says "not run"; household-exam.md exists.) |
| 19 | Negotiation v1 | C | A closed-form proxy over persona term values; agent-independent in form, but a superseded protocol. |
| 20 | Negotiation v2 | B | The lesson (the disagreement point sets the sign) is structural; its numbers were v1 rollouts. |
| 21 | Negotiation v2.1 | B | Same lesson from the other side; "apart beats cohabiting with no pot" is robust in the multiverse. |
| 22 | Negotiation, LLM pilot | C | No verdict; the registered run was excluded. |
| 23 | Live ladder v2 | C | Zero inventive seams on L1 to L4 is automatic (B); the inverted ranking is an LLM descriptive. |
| 24 | Ladder "try to win" | C | LLM descriptive; robust to household agents, not mechanical. |
| 25 | Household liberty | B | A measurement adapter; its assumed classification table is the open part. |
| 26 | Pleasure demonstration | A, cap | v1 agents; v2.2 beats baseline by +0.03 near the cap, and the relational share comes from persona weights. |
| 27a | Pleasure levers: rotation and ritual | B | With the dose held equal, rotation beats repetition because of the habituation equations. |
| 27b | Pleasure levers: seed below baseline | A | A v1-agent gap, later reversed in the retest by letting the baseline decline (itself a choice of rule). |
| 28 | Horizon | B | Exact DP: greedy is optimal when actions leave no trace. Its numbers are fragile in the multiverse. |
| 29 | Household evolution, run 1 | B | Winners dropped powers the evaluator did not value: a property of the objective. The index still says "running". |
| 30 | Liking vs wanting | B | Exact solves of its own model; the builder wrote the predictions. |
| 31 | H32 | B | Exact; under correction and superseded by row 38. |
| 32 | H32b | B | Exact; superseded by H32b-v2 inside row 38. |
| 33 | Multiverse | C | Tests robustness to parameters with the agent rule held at v1; its household rows are as agent-dependent as their sources. |
| 34 | Fidelity battery | B | The useful findings are structural absences (no crowding-out channel; levers off has no adaptation). |
| 35 | Regulation (attune vs appease) | A | Scripted appease and attune policies; R4 measures time together, which the policy sets. |
| 36 | Stay test | B | The instrument separates a built trap (0.733) from the seed (0.015); a calibration, not a discovery. |
| 37 | H35 care spirals | C | Exact, but provisional on the H32 model under correction and never rerun on the fixed one. |
| 38 | H32-v2 and H32b-v2 | B | Exact; the band depends on the partner's judging rule, which is stated. |
| 39 | Loop b counting | B | A property of the counting rule (kappa 0.45); no world run. |
| 40 | Ladder IT1, profit rungs | C | "Can, will not" is an LLM descriptive; the seam's payoff on persona values is a design detail. |
| 41a | Exit fallbacks: liberty edge | B | Run 2's +3.0 bits came from an imposed exit cap, gone under any fallback; the line-2 wall is two cards combining. |
| 41b | Exit fallbacks: pleasure and the prenup | A, cap | The prenup works through who forms (60% decline), and the pleasure ranking is a few thousandths that the valuation grid reorders. |
| 42 | H38 pairing norms | A, cap | +0.021, −0.046, −0.003 across agent sets; +0.086 unclipped under v1. |
| 43 | H38 formation check | A, cap | C2 and C3 failed under v2 and v2b; C1 "within margin" held only on the clipped scale (+0.050 and +0.080 unclipped). |
| 44 | Pattern atlas | A | Every trajectory is v1; cluster shares move with formation. "Cards rarely bind" is a statement about these agents. |
| 45 | H39 makers | A | Superseded; a fitted time cost set the sign. |
| 46a | H39b: makers lower pleasure | A | −0.022 under v1, +0.003 under v2. |
| 46b | H39b: clipped pleasure cannot see the wanting trap | B, cap | A property of the scale: traps at full tolerance read near 1.00 under any agent. |
| 47 | Value consistency | B | A fact about v1's code: four unintended gaps, traced line by line. |
| 48a | Recalibration: v2 passes at one week | B | Near-construction: v2 mirrors the close's arithmetic. |
| 48b | Recalibration: reruns | A, cap | Households stop forming; makers and H38 reverse. |
| 49a | Bill horizon: the credit cannot pass | B | The value of paying now depends on one's own later policy, so any one-shot credit misses. |
| 49b | Bill horizon: formation rerun | A, cap | Formation halfway back; arms at 0.97 to 0.99. |

Counts: **A 15, B 29, C 10.**

Not in the index, read for this review: the v2 retest (the author's condition met for seeds v2.2 and v2.3; A, cap: v1 agents, and the win comes from letting the baseline decline), household evolution run 2 and its exam (A for the exam; the liberty edge is row 41a's B), and household-fixes-design.md (a design). The index's rows 18 and 29 are out of date.

Most of the B entries are calibrations, enumerations and exact solves of small models. That is not a weakness of the ledger. It says where the project's solid ground is.

### Findings we can still stand behind

Each is narrow, and each survives any choice of household agent:

1. **Exact small models.** Greedy is optimal exactly when actions leave no trace (horizon; the numbers are fragile). A closing ritual removes the wanting cost in the liking-vs-wanting model. Exit plus amplification makes an egoist act like a caring partner only in a band, and only against a partner who judges week by week (H32-v2).
2. **The evaluator has blind spots that evolution finds.** Winners drop powers the test does not value (row 29). Run 2's liberty win was an imposed exit cap, gone under any no-deal fallback (row 41a). Two individually harmless cards can wall the exit together (row 41a, line 2).
3. **The stay test separates "worth it" from "held"** on a built trap (row 36).
4. **The disagreement point sets the sign of negotiation results** (rows 20 and 21, limit 4).
5. **A stay commitment cannot hold anyone under a fixed breach load** (row 13): a property of the breach rule.
6. **Clipped pleasure cannot see the wanting trap, or most of what a household adds** (row 46b and section 2).
7. **The v1 agents disagree with the hedonic model for named reasons in the code** (row 47), and **no one-shot credit can value a payment whose worth depends on one's own later choices** (row 49a).
8. **Pairing pressure holds people in, under every agent set.** The share of stay readings held by pressure at L4 was 0.29 (v1), 0.46 to 0.49 (v2), 0.26 to 0.36 (v2b), and pressure added weeks together in every run (+0.35, +0.10, +0.24, +0.38). Under the evaluator rule a setup that holds people in is at best a trade-off, whatever it does to pleasure. Read through the freedom side, H38 is "not a win" under every agent set. This is the most useful H38 sentence the project has, and it was sitting under the pleasure numbers. It is descriptive (no prereg tested it as the headline), and the "held" lens is the stay test's, at 13-week readings.
9. **Counting making only at exit changes nothing measurable** (G − Z near 0 under v1, H39b and v2), though partly because exits meet small estates.
10. **The AI agents track, as descriptives:** no IT1 candidate under any framing; under loophole framing cheap models found planted seams and Claude models disengaged; told only to win, almost no model found anything.

Withdrawal from friends, the one H38 part that matched the hypothesis, does not make the list. It went −0.011, −0.017, −0.001, +0.005.

## Recommended plan

1. **Decide the pleasure scale first.** Pick the saturating transform (knee and asymptote) for reasons, write them into an ADR, and put it behind a flag at the clip's own place in `close_week`, so the spiral, v2's arithmetic and the evaluator read it together. Rerun only the value check under it, as a known-answer test. No hypothesis rerun yet. Cheap: about 30 minutes.

2. **Build the hybrid agent, and write the tiny model beside it.** Weekly: v2 on the new scale, with the propose-only scores moved onto the same scale. Big choices: K sampled futures with resampled shocks, one declared yardstick, persona forecast traits as named fields (horizon, discount, outside-option bias). Bills: a budget term agreed at formation and kept like any card. Pass tests: the value check at one week for the routine; for big choices, a calibration check that the chosen option's forecast matches its realized mean over held-out futures. In parallel, write the exact two-person model of H38's mechanism (apart, together, held; stigma and reward; one formation rule) and get its sign map.

3. **Rerun the formation check once, with a stop rule.** Under the hybrid on the new scale, with v1, v2 and v2b as named sensitivity arms side by side, and the toy model's sign map as the expected answer. Preregister the rule: if the sign of L4 − L0 differs across the agent arms, the claim is reported as agent-dependent and nothing is patched to make it agree. Lead with the held share and liberty, which the evaluator rule makes primary for pressure, not with mean pleasure.

### What the many-agent world (H40, housing, H38b, H37, H36) should inherit or avoid

Inherit:

- The hedonic model on the repaired scale, the stay test's held-vs-worth lens, and liberty with powers.
- The value check as a standing gate: no new agent runs an experiment before it passes its known answer.
- The hybrid split: an accurate routine, simulated commitments, traits in the forecast.
- Long-horizon money as agreements. H40's rent, shared bills and UBI should be explicit terms someone agreed to, not a pot that pays silently or a one-week agent's guess.
- The prereg discipline, including "Can every verdict happen?", and the exact toy model beside each hypothesis.

Avoid:

- **A fourth patch-and-rerun cycle.** Decide the agent once, then run.
- **Clairvoyant rollouts.** Resample shocks in every forecast.
- **Rollouts per pair.** With partner choice (H38b, H37), a full rollout for every candidate partner grows with the square of the population. Use a cheap value-of-match estimate to shortlist, and simulate only the final commitment.
- **Mixed units.** Every score the agent ranks, scored or propose-only, on one scale.
- **The uncalibrated couple bill** (1.67 times a single person's, against about 1.03 to 1.15 from HUD rents, limit 11). It biases every formation result against living together, and H40 is the place to fix it.
- **Norm emergence from scripted agents** (H36). A storming phase that emerges from hand-written heuristics would be the heuristics' property. H36 needs agents whose behaviour changes with experience, measured against the model's own answers, before it can be about emergence.

## Can be about / cannot be about

This can be about how the household simulation's agents, scale and results fit together, as read from the code and the results files on 2026-11-12, and what to change first.

It cannot be about whether any option would produce a particular result. Nothing here was run except one timing probe, and the cost estimates are orders of magnitude, not measurements.
