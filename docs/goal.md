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

## Still open

- Should LLM agents also file typed reports? Recommended: yes.
- Keep one untouched final exam? Recommended: yes.
- Pushing the branch to GitHub needs the author's yes.
