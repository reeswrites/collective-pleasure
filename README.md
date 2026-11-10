# multi-agent-rules

Multi-agent rules: proof-gated rule search for AI agent groups.

This project studies formally specified rule systems (rules, norms, sanctions) that govern AI agents. The pipeline is: write rules in a human-readable ADICO-derived format, compile them to a labeled transition system, check invariants with a solver or model checker (no deadlock, no rule conflicts, bounded sanctions, a reachable repair path), gate each proposed agent action with the checked rules, and measure how far real LLM-agent behavior departs from the formal rule system. A single agent is the base case (n = 1); groups add peer sanctions, collusion, emergent norms and coordinated attacks. The first experiment is single-agent (fishery-quota rules, free-text vs solver-gated), followed by the multi-agent comparison.

**Status: pre-results; nothing here is a finding.**

## Read first

- [RATIONALE.md](RATIONALE.md): why this project, prior art, design decisions, experiments, kill criteria
- [docs/plan.md](docs/plan.md): milestones and next task
- [docs/claims.md](docs/claims.md): claims register (predictions are committed before runs)

## Layout

```
RATIONALE.md          project rationale (draft)
CONTRIBUTING.md       conventions
docs/plan.md          milestones, next task
docs/claims.md        claims register
docs/decisions/       ADRs (design choices)
docs/reviews/         review-council convention and reports
docs/surprises.md     unexpected observations
docs/negative-results.md  negative results
src/                  code (placeholder)
tests/                tests (placeholder)
```

## Start locally

Placeholder; nothing is built yet. Planned stack: Python managed with [uv](https://docs.astral.sh/uv/). Tools under evaluation: mCRL2 (transition systems, bisimulation, model checking), Z3 (action gate), and a fork of GovSim (testbed).

Related: [philosophy-engine](https://github.com/reeswrites/philosophy-engine) is an input (ADICO schema, reference engine), not part of this repo.

## License

Apache-2.0. See [LICENSE](LICENSE).
