# Where we are and what we're aiming for (2026-11-10)

Nothing here is a result. This page says what the project is for.

## The founding question

Can bad behavior by AI agents be made impossible by mechanism rather than training? A mechanism holds exactly as far as the formal model holds. The project measures how far that is.

## The research: norms

Find norms that let a network of agents cooperate freely. Freedom means anyone can leave and keeps real options. Cooperation means shared needs are met without outsiders paying for it. These are two scores, not one. Evolution searches the Pareto frontier between them, and the author reads the winners in plain English. The main world is a household (Partner A, Partner B, Friend C). The fishery stays as calibration.

## The product: an evaluator that evolves

What judges the norms improves alongside them. Agents' exploits widen the formal model. The author's "that's not what I meant" moments refine the test. A ladder of adversaries, from cheap decision models to strong LLMs, keeps the pressure honest. The timeline records how and why the evaluator changed. In the author's words: "more interested in the norms but the evaluator is the more interesting product". The research is the norms and the product is the evaluator. Doing the research builds the product.

## The central claim to test

Proofs make rules airtight inside the formal model. Clever enough agents step outside it. Those inventive seams are found by an agent, not predicted by the model checker, and they are where intelligence matters. The aim is the capability level, and the price, at which agents start escaping the model. Below it, formal rules hold. Above it, the human loop must keep widening the model.

## Two modes

The household runs in two modes, and the project does not settle which is right. Delegates: AI agents serve human principals, humans' welfare counts, and agents face rules at least as strict as anyone's. Peers: every member's modeled welfare counts equally, and a future where AI agents count stays open. Experiments cannot settle the metaphysics. They can show whether it matters. We report norms that win in both modes and where the modes split (ADR 0011).

## World-model framing

The project is the Guaranteed Safe AI shape in small. The world model is the household sim with counterfactuals. The specification is pleasure, non-offsettable suffering, empowerment and norms. The verifier is the proof checks, the seam ladder and the evaluator. Value alignment asks if norms produce good lives. Epistemic alignment asks if agents' appraisals match reality. Predictions about real people stay hypotheses until the household reproduces known findings.

## Why they stay

Version 3 asks why an agent stays in a bad household. Actual quality comes from counterfactual runs. Appraisal is what the agent believes. The gap is misappraisal. Switchable biases (creeping normality, sunk cost, risk aversion) can widen it. Repair after a rupture is the good reason to stay. Appraisal accuracy becomes a third score (ADR 0011).

## Two loops

The rules converge on the test. The test converges on the author's intent. That gives two curves. Where they flatten says how good "good enough" can get.

## How you work with it

- Chat with the workbench: a Claude Code skill plus the `mar` CLI.
- Reports with charts and stories.
- Experiment, change and question logs.
- A timeline with dated snapshots.

## Cost strategy

Conversation runs on the author's Claude plan. Swarm agents run through the API: Jev for screening, Haiku 5.5 for sweeps, Sonnet 5.5 and Opus 5.5 for exams, the patcher and the judge. Measured dry run: 5 Claude Haiku 5.5 agents for 12 months in the fishery cost at most about $0.09 per run ($0.045 batch, no cache). The first month of real work is estimated at roughly $80 to $130. That is an estimate, and household agents may be chattier. Agents must not run as Claude Code subagents.

## Where we are

Built and tested: the core loop, English-like rules, the workbench and reports, the logs and timeline, and the agent backends (Claude, Jev, OpenRouter), tested offline.

In progress: the household world and the seam ladder.

## Next

- Wire the household world into chat and run the 5-minute MVP demo with scripted agents.
- The author creates API access.
- First real runs: place models on the seam ladder and measure cost.

## Decided

- Talking LLM agents also file typed reports, in the same fixed vocabulary as decision-model agents, alongside free talk. Say vs do can then be compared across tiers. The backend already asks for a "report" field; this is the standing rule.
- One untouched final exam is kept for the write-up (see ADR 0007 decision 12 and claim FX1).
- Main and the branch are on GitHub (private repo), pushed by the author on 2026-11-10. Pushes from Claude Code are blocked by auto mode, so the author pushes.

## What changed

- 2026-11-10: two modes (delegates and peers), the world-model framing and the why-they-stay model added (ADR 0011). Freedom is also reported as empowerment. Shocks are read as misalignment in the wider system.

## Still open

Nothing is waiting on the author from this page.
