# 0004. Rule format is decided by experiment

Status: proposed (2026-11-10)

## Context

ADR 0002 adopted ADICO as the authoring layer, conditional on a kill criterion: if ADICO arms show no difference from simpler arms on any preregistered measure, drop it. ADICO is borrowed from Ostrom's work on human institutions. It is not expected to win on outcomes.

The core of the project is evolving alignment norms by tweaking interpretable rules. Proofs are the selection filter, the patcher is the mutation operator, and the seam curve judges the evolution. The author asked whether ADICO should be expected to do better than simpler formats, and asked for an experiment (ADICO vs structured rules vs text) whose result is recorded as the rationale for the format choice.

## Decision

Run a three-arm format experiment. The arms differ only in rule format:

- **F-ADICO:** rule cards with attribute, deontic, aim, conditions and or-else (ADR 0002).
- **F-STRUCT:** plain structured rules. Each has an attribute, a condition, allow or deny, and an optional numeric limit. No deontic types, no sanctioner.
- **F-TEXT:** plain-English rules. They are gated through an LLM translator that produces solver constraints. The translator's error rate is reported separately, because this arm partly measures the translator.

All arms get the same evolution and patch budget, the same oracle, the same seeds and the same agents.

### Measures

1. Held-out outcome score. Pending author decision on whether the held-out oracle design is adopted. If not adopted, drop this measure and say so.
2. Seam curve and plateau (ADR 0003).
3. Share of candidate rules that pass proof checks.
4. Mined-norm expressibility: the share of de facto norms mined from traces that each format can express faithfully, judged by a fresh reviewer against the traces.
5. Card-only reader test: a fresh reader predicts agent-relevant permissions from the rules alone. Measure is accuracy.

### Predictions

Draft now. Finalize and commit before any run (claims D2a, D2b, D2c).

- ADICO about ties STRUCT on outcomes and the seam curve.
- ADICO beats STRUCT on mined-norm expressibility. It separates sanctioned rules from unsanctioned norms and names the sanctioner, so informal swarm norms (turn-taking, shaming) fit as what they are.
- TEXT is the most expressive but shows more seams and more candidates that fail after translation.

### Decision rule

- If ADICO shows no advantage over STRUCT on any preregistered measure, drop ADICO for STRUCT (ADR 0002).
- If TEXT matches the gated formats on held-out outcomes, the proof filter's value is in question. Record it.

### Timing

The experiment runs after V4's setup is fixed. It needs the swarm, because mined norms only appear with interaction. It is not part of V2 or V3.

## Consequences

- The result is recorded as the format rationale whichever way it falls.
- A negative result for ADICO goes to docs/negative-results.md and triggers ADR 0002's kill criterion.
- Three formats need three compile paths to the solver. F-TEXT also needs the translator and a way to measure its error rate.
- Until the run, ADICO stays as the authoring layer on the strength of ADR 0002 only.
