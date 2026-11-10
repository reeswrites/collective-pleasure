# multi-agent-rules

Multi-agent rules: proof-gated rule search for AI agent groups.

This project is an AI-native workbench, used through chat, for evolving alignment norms by tweaking interpretable rules. The author talks loosely about how agents should behave; the system turns that into precise rules (ADICO cards, also English-like sentences), proves what it can, runs swarm experiments, and reports back in plain English and charts. Proof checks filter candidate rules, an LLM patcher mutates them, and a seam curve judges the evolution. There are two loops: rules against the test (do new seams per round slow, and where do they plateau?), and the test against the author's intent (do "not what I meant" moments per round fall?). One page: [docs/pitch.md](docs/pitch.md); decision: [ADR 0005](docs/decisions/0005-two-loops-and-workbench.md).

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
