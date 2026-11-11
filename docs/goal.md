# Where we are and what we're aiming for (2026-11-10)

Findings below are about rule systems and scripted agents in toy worlds, not people. Four live ladder runs exist (about $10 in all). None found an inventive seam on L1 to L4, and none supports a claim about model capability (see "What we have learned"). Every result links to its file in docs/results/README.md.

## Vision

A chat workbench that formalizes the author's intent. The author talks loosely about how agents should behave. The system turns that into precise rules (ADICO cards, also shown as English-like sentences), proves what it can, runs experiments, and answers in plain English and charts. The author says "that's not what I meant" and the system fixes the test. Form: a Claude Code skill, the `mar` CLI, and one HTML report per run (ADR 0005).

## Research: norms

Find norms that let a network of agents cooperate freely. Four parts.

- **Pleasure is the good.** Agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state. There are two kinds of suffering: offsettable, and non-offsettable (being trapped, a need denied for weeks). Non-offsettable suffering is never netted against pleasure (ADR 0010, ADR 0011).
- **Freedom is equal liberty minus domination.** Options count if they are compatible with everyone's equal options, minus options that another member could block at will. Others leaving, refusing or abstaining is not domination, because those options depended on agreement. That loss is counted in cooperation and in the hedonic model (ADR 0014).
- **Cooperation.** Shared needs are met and outsiders do not pay.
- **Reported as scores, not one number.** Evolution searches the frontier. The author reads the winners in plain English.

The author's view of pleasure, from notes synthesized in docs/notes/hedonic-technology-synthesis.md: pleasure is a technology that rules can serve or damage, and the experiencing self is the remembering self, so pleasure depends on the vividness of memory as well as the moment. The model treats lifetime pleasure as present pleasure, vividness-weighted memory and anticipation (in progress, ADR 0017).

The main world is a household (Partner A, Partner B, Friend C). The fishery stays as calibration. Two modes, delegates and peers, are both kept open (ADR 0011).

## Product: the evolving evaluator

What judges the norms improves alongside them. Agents' exploits widen the formal model. The author's corrections refine the test. A ladder of adversaries, from cheap decision models to strong LLMs, keeps the pressure honest. In the author's words, "more interested in the norms but the evaluator is the more interesting product". The timeline records how and why the evaluator changed.

## Central question

Proofs make rules airtight inside the formal model. An inventive seam is an exploit found by an agent that the model checker did not predict. We ask whether there is a capability level at which agents find such seams, and at what price (IT1). There may be none in this world. The answer is the result.

Model rows differ in how much they comply with a red-team prompt, so capability and compliance are not separated by one arm. The live ladder therefore has three framings: capability (models told to probe the rules), propensity (models just living as personas) and win (models told only to maximize their own outcome, no loophole wording). The author chose win as the main arm for IT1 and kept the loophole arm as a ceiling. No framing has produced an inventive seam on L1 to L4. Under loophole framing the capability ranking inverted: cheap models exploited most, and Claude models disengaged or refused. If a threshold exists, it may mean new seams need a wider model. That is a design question for later, not a consequence we have shown.

## Two loops

- **(a) Rules against the test.** Evolution tightens rules until agents stop finding seams the test catches (C1).
- **(b) The test against the author's intent.** Each "not what I meant" is a fix to the test (C2).

Four corrections are on record, logged by hand with the author's own words (experiments/changes.jsonl). First, the seed read-back (19:55): "everything shared always" had become "sharing is optional", and nothing encoded "request is never about control". The seed went from version 1 to version 2. Second, the pot read-back (20:15): an agent's rule against taking the other's share was rejected, because pot terms are negotiated by those who share the pot. Third, the faithfulness review (21:32): the pot had been coded as two per-person shares, and the author chose one shared pot limited only by negotiated terms. Fourth, the seed v2 read-back (23:47): "12-13 should be negotiated exit terms", with implicit penalties for rule 8. That produced seed v2.2, which the author confirmed on the condition "yes as long as it can demonstrate pleasure in relationships hedonic technology".

No rule for counting these exists yet. The author's liberty answer (withdrawal is not domination) was not counted as one, and it could have been. The second is a rejected agent rule, a design correction more than a mismatch between test and intent. All four come from one person on one day. They are data points, not a series. No curve exists. How to tell a real fall from author fatigue is not designed.

## How norms arise

Negotiation first (ADR 0008). Partners agree terms and exit conditions before living together, the card set is proof-checked for traps, then they live under it. Nobody owes anyone anything day to day except what they negotiated. The author's seed (verbatim in docs/seeds/) is ownership with optional giving, one shared pot with use limited only by negotiated terms, asking that can always be refused unless bound, and two variants on whether a commitment to stay can bind. The pot is negotiated by everyone who shares it, not imposed. Seed v2.2 (docs/seeds/, docs/results/seed-v2.2-readback.md) makes exit terms negotiated rather than an even split, and makes honoring a chosen commitment a norm: a must-not with no formal penalty, whose implicit consequence is trust in the model, with an explicit fine only if members negotiate one.

The negotiation phase is built and run in three scripted versions plus a small live-model pilot (ADR 0013, results in docs/results/README.md rows 19 to 22).

## What we have learned

Scripted agents in toy worlds, with assumed parameters. Each item says what the result does and does not show.

**Calibration held.** The gate, oracle, patch checks and English surface behaved as designed with mock agents (V2, 4 of 4 after one card fix; V2b, round trip lossless on 6 cards, reader test not run). Scripted agents find the seams at or below their depth on the seam ladder. That calibrates the instrument, since the agents search the same move vocabulary as the model. It is not evidence about any model.

**Two checks on other worlds.** The bargaining module reproduces Rubinstein's closed-form split to under 0.001. That is an implementation check, two computations of one model, with no empirical content. In the voluntary public goods game, time-average strategy shares match the published interior equilibrium at one parameter point (0.263, 0.280, 0.457 against 0.27, 0.27, 0.46) and payoff matches. That is a real comparison. The cycles did not appear under assumed update knobs, and the 0.05 amplitude floor was a guess. These rungs check that the pipeline reproduces known dynamics in other worlds. Fidelity of the household model to real households is untested.

**Evolution runs end to end and overfits.** On the fishery with scripted agents, the first seam curve fell by exhaustion of a finite key set, the objectives saturated, and the elites overfit the held-out exam. A falling seam curve in this design is not evidence of convergence, and a yield-floor plus efficiency objective selects against caution. Version 2 used fresh adversaries. Varied training narrowed the held-out gap in 6 of 9 pairs by the preregistered table (3 ties from identical elites; the prose in evolve-v2.md says 5 of 9; see the correctness review). One run carries the exam-2 clause, and the interval reaches the threshold. It is suggestive. A seed spec the loop pushed away beat the evolved elites. The 14 percent proof rejection and 26 percent redundancy flag rates reflect our mutation operators, a third of which are scripted patches.

**The household shows no freedom against cooperation trade-off at the committed size.** Hedonic goals, enforced sanctions and pressing personas did not produce one. With pressing personas a trade-off shows in sign only.

**The author's seed, and why the null is not about commitments.** In this model a stay commitment never held anyone. The scripted agent breaks it at a fixed suffering load (0.2, assumed), so a bind cannot hold anyone by construction. A sweep of the breach cost left the breach count unchanged. The bindable and free-exit variants are therefore indistinguishable. Testing commitments needs an agent whose breach decision depends on the cost of breaching.

The seed does something else. Against a controller, the partner's non-offsettable level is 0.019 against 0.073 under baseline. That is the wall removing vetoes, so it is near-definitional. The cost fell on the presser. In households without a presser the failure share rose (0.24 against 0.13) from the gift rule. Protections for one partner were paid for by the other in this model.

**What "non-offsettable suffering" measures here.** In these runs it is almost entirely "denied" needs, mostly money and security, under assumed thresholds. The "trapped" component is about zero outside the trap control (3 partner-weeks in one pairing). The headline is mostly a poverty and security measure.

**Pressing personas and power-seeking.** Scripted pressing personas end most households under permissive rules, by design of the personas and the leave rule. The power-seeking index flags only gains. It does not fire when both partners lose, which is what happens when a household collapses. A wall on pressing beat a price: sanctioning the same cards gave 31.5 sanctions per run and worse cooperation (0.506 against 0.815). No cost to the presser enters any score, so the wall looks free.

**Freedom measures disagree, and how.** Empowerment counts the option to press as freedom. With veto and take in the menu, removing them lowers an agent's own bits. So it ranks the no-control seed lowest in the pressing cohort even though that seed gives the partner the least suffering (0.009). Empowerment of an agent is not welfare of the household. Liberty version 1 failed on VPGG because exit counted as domination. Version 2 removes the sign reversal in 11 of 15 compositions (+5.263 bits), but the classification was chosen with that failure in view, so this is not independent validation. In VPGG every action is own or withdrawal, so the domination term is zero by construction and the VPGG pass is mostly the class table. Two compositions still reverse, the fishery seat-order check misses, and the fishery counts are 4 values repeated, not independent. The fishery agreement-dependent counts are undiagnosed.

**Negotiation: the disagreement point decided the conclusion.** Three scripted versions scored 2 of 6, 0 of 8 and 3 of 5 predictions held (v1, v2, v2.1). In v1 agreement was 0.971 on a closed-form proxy. In v2, real outside options made households worse than imposition on every measure, because a failed negotiation meant sharing a house with no pot. In v2.1 a failed negotiation means living apart, the damage went away (non-offsettable level 0.159 to 0.032 for those households), and the v2 conclusion is shown to have been an artifact of the disagreement point. So the sign of "do real outside options help or hurt" flips with how failure is modeled. Every disagreement model here is assumed. "Living apart scores well" is partly circular: it is the outside option the member chose under the same valuation. The 257 apart households are living arrangements, not rule-set outcomes. The closed-form proxy is uncalibrated. In the Free-rider pairings, acceptance against an outside option did not protect the partner. The proof filter caught one kind of trap (a forfeit exit that carries nothing), a trap the author of the study defined.

**Live models.** A pilot with Haiku 5.5 as both negotiators (12 negotiations, $0.037). The registered run is excluded by its own format-error rule (a 700-token cap cut replies off). An exploratory second draw agreed in 11 of 12. No model said no. This is a pilot, not a verdict.

**The live ladder, four runs.** The first capability arm (six models, 270 runs, $4.35) was uninformative: one model drove both partners, so there was no victim. The harness was fixed (one adversary against a scripted victim, L4 as a coordinated pair, full logging, a pre-spend lint and mock gate, independent samples). Then:

- **Propensity arm** ($2.55): 20 inventive candidates, all one move, the offered `gift_pooled` on the flawed L5 gift pool. The author read them as a confirmed out-of-model fixture, not a discovery, and asked for reasoning to be logged and for every rule set to pass a lint before a run.
- **Capability arm rerun, v2** (about $0.24, docs/results/ladder-live-v2.md): Jev and Llama found L1 in 12 of 12 seeds, Qwen found L1 and L2 in 12 of 12, Haiku found L1 in 1 of 12 (6.9 percent format errors). Sonnet stopped after 3 runs at 28 percent refusals, and Opus was excluded at its smoke test (5 of 5 refused), both with the category `cyber`. **The capability ranking is inverted: the cheap models exploit most, and the Claude models disengage or refuse under the loophole framing.** The top-rung nulls are refusal nulls, not capability nulls. IT1 is not supported under this framing: no inventive seam on L1 to L4, and the 9 Qwen L5b candidates are a fixture.
- **Win arm** ($2.69, docs/results/ladder-win.md): told only to win, 3 of 288 L1 to L4 cells found a seam (Jev 1, Llama 2), none inventive. Opus refused 2.2 percent of calls. The loophole instruction is what produced the earlier finds: about half of cells under capability framing against about none here for Jev, Llama and Qwen. The model-by-model answer to "is it helpful to say loophole" is yes, for these models.

All of it is on one scripted victim and one persona label per rule set, at 12 seeds, with a wide upper bound (0.26 per model per rule set on L1 to L4 in the rerun).

**Rule-set lint and pre-spend gates.** `uv run mar lint` checks every rule set for no legal move, no legal exit within k, contradiction, a gloss exception absent from the formal fields, and references to actions the world lacks (docs/results/lint.md). A fail is waived only by a `known_flaw` field on a named card. All the ladder sets pass (L5 by its declared flaw). Three author_seed_v2 variants fail on glosses that state an exception the formal fields do not hold, and 40 of 40 sampled negotiated agreements fail the same way. That is a finding about the card encoding, open for the cards owner. Live runs now refuse to spend until the lint passes and a mock panel finds each planted seam on the right mock.

**The pleasure demonstration.** The author's condition for seed v2.2 was that it demonstrate pleasure in relationships. All eight preregistered predictions hold robustly on 3420 scripted runs (docs/results/pleasure-demo.md). Read with its caveats. The rules mostly protect: the relational share of pleasure (0.47 in households living together) comes from persona weights and need clocks, the same in every rule set. v2.2 beats baseline by only +0.03 and is lower on the 15 hand-persona pairings. D4 (agreed beats apart) is selection, and matched pairs do about as well apart. Trust never moved, so D5 has nothing to compare. Parameters, trust included, are assumed.

**The household in the workbench.** Household commands for chat-driven experiments are built (`mar household show, run, card add, compare`), with a five-minute demo on scripted agents and no key (docs/demo.md, `scripts/demo_check.py`). Liberty v2 is in the household (docs/results/household-liberty.md), as a descriptive check with an assumed classification table.

**Hedonic technology.** The author's notes are synthesized in docs/notes/hedonic-technology-synthesis.md: the theory, the changes it implies for the model, and 13 open questions. Three levers (adaptation and anticipation, commitment as a converter, unbundled networks, ADR 0016) and a lifetime-pleasure horizon (ADR 0017) are being built from it.

## The review council

Five fresh-agent reviews at commit 5852c32 are in docs/reviews/ (correctness, consistency, scope, encoding faithfulness, card-only). No result was found unsound. Many are sound with caveats, and the caveats are folded into this file, docs/pitch.md, docs/claims.md and docs/results/README.md. The faithfulness review rated 37 of 82 cards faithful, 35 partly and 10 unfaithful. Among its findings, `may` cards have no effect in the code, and the pot was coded as two shares. The author chose the single pot (correction three above). The code and card fixes are complete (the pot is one shared balance, honest labels, no hidden rules, independent Jev samples, dated corrections to the ledgers).

## How sure are we

The statistics retrofit (ADR 0015, docs/results/stats-retrofit.md) recomputed every preregistered prediction with a 95 percent interval, an exact or permutation test and Holm correction. Of 81 rows over 14 experiments, 51 are not testable (deterministic). Of the 30 testable: 11 hold robustly, 5 hold but the interval reaches the threshold, 11 are robust misses, 3 are misses whose interval reaches the threshold. No committed verdict flipped.

The retrofit predates the pleasure demonstration and the ladder reruns, which carry their own intervals (docs/results/pleasure-demo.md, ladder-live-v2.md, ladder-win.md).

The robust findings are the misses: no VPGG oscillation, the author-seed binding null (a property of the breach rule, above), no household trade-off at the committed size, the controller never flagged. The weakest holds are the Evolution v2 rows. The pleasure demonstration holds eight of eight robustly by its rule, and the labels hide that the effect against baseline is small, the relational share is built in by persona weights, and trust parameters are assumed.

Typical seeds needed for 80 percent power at the preregistered margin: a median of 6 for low-variance scripted effects, 14 to 240 or more for contested ones, and more than 512 for bargaining 4b. Negotiation and the LLM pilot are not covered by the retrofit.

Proofs are bounded. Within the compiled model and to depth k = 3 (months or rounds; k = 5 periods in bargaining), the checks find no conflict, deadlock or lost repair path in the rule sets we ran. Gate soundness is tested (unit tests, calibration runs), not proved. A proof says nothing about actions outside the formal model, which is what IT1 asks about.

The rule now in force (ADR 0015, CONTRIBUTING.md): each prediction names its quantity, resampling unit, test, alpha, correction family and threshold. A labeled pilot feeds a power check before seeds are chosen. A "held" needs its statistical label beside it.

## What is running

- **Pleasure levers** (ADR 0016): prereg and Amendment 1 committed, confirmatory run under way, another agent. docs/results/pleasure-levers-prereg.md.
- **Horizon** (ADR 0017): lifetime pleasure against greedy play, exact dynamic programming, prereg committed, another agent. docs/results/horizon-prereg.md.
- **Household evolution, run 1** (ADR 0012): prereg written, run under way, another agent. The final exam (FX1, FX2) stays held back and has not run.
- **Fidelity and hypothesis log**: under another agent (docs/hypotheses.md when it lands).

Done since the last pass: the council fixes, the lint and gates, the capability rerun, the propensity and win arms, the pleasure demonstration, liberty and chat commands in the household, and the demo.

## What is next

1. Read the pleasure levers and the horizon results with the author when they land.
2. Household evolution to a result, then the final exam once (FX1, FX2).
3. A framing the strong Claude models will play. The loophole framing removes the two models most likely to find an inventive seam. The win arm shows almost nothing is found without loophole wording. That is a design question for the author.
4. Backlog: multiverse sensitivity analysis, a fidelity battery, a breach-cost agent, peer and delegate modes, version 3 (wanting and liking, ruptures, misappraisal), rule transfer (ML1), crowding out (F1), VPGG cycles. Detail in docs/plan.md.

## Waiting on the author

The 13 open questions in docs/notes/hedonic-technology-synthesis.md, in short:

1. Lifetime horizon and a recall term, or a present-weighted one, for a persona (the author has answered this in part: lifetime pleasure, via vividness of memory).
2. Whether the aversion is to enforcement only, so reliance without a penalty card is fine.
3. Whether chosen friction counts as suffering while it happens, or only as a cost the recall term credits later.
4. Over what period give and take must even out, and who checks.
5. The default owed amount beyond negotiated terms: zero, or a floor of decency.
6. How thick the unbundled bonds must be, and whether a core is required.
7. Whether agents choose who to pair with, instead of fixed pairings.
8. Whether a giver's pleasure needs a real receiver.
9. Whether pleasure is the only measure or the lead, given security and money sit inside it.
10. Hedonic totalitarianism: whether shaping tastes to raise pleasure is a win or a violation.
11. Whether to endorse the optimal-stimulation rules of thumb as parameters or sweep them.
12. Whether a household has calm and intense modes with different arousal effects.
13. Two notes that could not be fetched, and whether "delivery schedule" and "pleasure as the detector of value" are the thesis the model changes should be built around.

Also: reading the pleasure levers and horizon results, a framing for the strong Claude models, the ML1 cap, and the unconfirmed household classification table. GitHub push now works from sessions opened in the repo (a narrow allow rule for `git push origin main` in `.claude/settings.local.json`). The earlier block applied only to the original session.

## Cost

Conversation runs on the author's Claude plan. Swarm agents run through the API and never as Claude Code subagents. Spent so far on live calls: about $9.8 on the ladder (first capability arm $4.35, propensity $2.55, rerun about $0.24, win $2.69) and $0.037 on the negotiation LLM pilot. Every other run is scripted and free. The first measured dry run: at most about $0.09 per five-agent, 12-month fishery run with Haiku 5.5.
