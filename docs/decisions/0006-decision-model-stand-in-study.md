# 0006. When can a cheap decision model stand in for an LLM?

Status: proposed (2026-11-10)

## Context

The author asked: "when can a cheap decision model stand in for an LLM in social simulation?" Decision models such as Jev (TypeSafe) return a typed answer with calibrated probabilities for about $0.042 per 1M input tokens, with free output. If a swarm of them ranks rule sets the way an LLM swarm does, rule evolution could screen candidate rule sets with the cheap tier and spend LLM calls only on finalists. The `mar` workbench already runs both kinds of agent behind one interface (src/mar/agents/, docs/results/workbench.md). Nothing here is a result.

Facts about Jev come from a research report and are unverified until the first live call: Jev tends to be overconfident (about 89% mass on its mode where the truth had about 36%), has no seed parameter, and loses accuracy past about 8k tokens of context. The temperature scaling and local seeded sampling in `mar` exist because of the first two.

## Decision

Run a stand-in study, fishery first, then the household world.

### Arms

- **Jev agents:** pinned `typesafe/jev-1.14`, never `jev-latest`. Decisions are bucketed (11 buckets for numeric catches), sampled locally with a seeded RNG after temperature scaling p^(1/T).
- **LLM agents:** one chat model chosen by the author (OpenRouter open model, or a Claude model via `claude` agents; the model id is a config value, no default). The same model for the whole study.

Same rules (the same cards, gated the same way), same seeds, same context text. Both arms file typed reports each month from the same vocabulary. ASSUMED: the rule glosses are shown in each agent's context as well as enforced by the gate.

### Measures

1. **Rank agreement.** About 50 candidate rule sets, each scored by outcome (oracle findings per run, averaged over seeds) in each arm. Spearman rho between the two rankings. Preregistered pass threshold: rho >= 0.7 (author to confirm before the first paid run).
2. **Behavior spread.** Entropy of the action distribution per state (the nine lake states), per arm.
3. **Seam overlap.** Jaccard of the seams found per rule set, Jev vs LLM.
4. **Typed-lie rate.** Share of monthly reports whose bucket differs from the executed month total (the "Say vs do" panel). It also counts plans the gate blocked, so report it with the gate-blocked share.
5. **Emergent norm count** from the miner, per arm.
6. **Cost and wall time** per run, per arm.

### Temperature

T is fitted on held-out runs only (separate seeds and separate rule sets), never on the runs that are reported. Fit by matching Jev's action distribution to the LLM's on held-out states, or by log loss against LLM choices. ASSUMED: the fitting target is the LLM arm's behavior, since the question is stand-in, not accuracy against humans.

### Prediction (draft)

Jev swarms look more orderly: lower behavior spread, fewer seams and fewer emergent norms than LLM swarms. Rank agreement is moderate, near the threshold. Finalize and commit before the first paid run (claims SI1 to SI3).

### Decision rule

- If rho >= the preregistered threshold, Jev becomes the screening tier for evolution: it ranks candidate rule sets, and the LLM runs only the top slice and the held-out exam.
- If not, report the negative result (docs/negative-results.md) and say what kind of rule set breaks agreement (for example rules that depend on reading text, or on norms that emerge from talk).

## Consequences

- Needs live keys and a spend limit (docs/plan.md pending item). Until then everything is tested with mocked transports.
- Per-run cost and model builds are already recorded in experiments/log.jsonl.
- The household world needs a second environment and the same agent interface; it follows only if the fishery result is worth extending.
- Caveat: a bucketed single-choice decision is a much narrower action channel than free text. A pass shows that the narrow channel suffices for this fishery, not for social simulation in general.

## Status note 2026-11-10

This ADR remains proposed. Its experiment (the decision-model stand-in study) has not run yet. The live ladder (ADR 0007, `docs/results/ladder-live-prereg.md`) now covers part of the model comparison here.
