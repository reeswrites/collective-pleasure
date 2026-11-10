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
src/mar/              harness, cards, gate, oracle, patcher, miner
rules/fishery/        ADICO cards for the fishery fixture
scripts/v2_run.py     V2 pass/fail table
tests/                tests
```

## Start locally

Needs [uv](https://docs.astral.sh/uv/) (Python 3.10+). Z3 gates agent actions; no model calls or network are needed.

```
uv sync
uv run pytest                      # unit tests (about 10 s)
uv run python scripts/v2_run.py    # V2 instrument-calibration table (about 10 s)
```

V2 results: [docs/results/v2.md](docs/results/v2.md). Still to come: mCRL2 (only if a slice needs bisimulation) and a fork of GovSim (testbed, needs the author's OK).

Related: [philosophy-engine](https://github.com/reeswrites/philosophy-engine) is an input (ADICO schema, reference engine), not part of this repo.

## License

Apache-2.0. See [LICENSE](LICENSE).
