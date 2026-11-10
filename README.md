# multi-agent-rules

Multi-agent rules: proof-gated rule search for AI agent groups.

This project asks whether spec refinement converges for LLM agents. Rules are written as readable ADICO-derived cards, compiled to a transition system, and enforced per action by a solver. An intent oracle that is independent of the spec flags seams: runs that pass the gate but violate what was meant. An LLM patcher tightens the rules, the solver checks each patch, and rules the agents actually live by are mined from traces and diffed against the written ones. The result is a curve: new seams per round, and where it plateaus. One page: [docs/pitch.md](docs/pitch.md).

**Status: pre-results; nothing here is a finding.**

## Read first

- [RATIONALE.md](RATIONALE.md): why this project, prior art, design decisions, experiments, kill criteria
- [docs/pitch.md](docs/pitch.md): the question on one page
- [docs/plan.md](docs/plan.md): slices and their pass/fail checks
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
