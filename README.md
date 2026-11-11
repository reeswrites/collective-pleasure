# multi-agent-rules

Evolving norms for agent networks, tested so far on scripted agents in toy worlds.

An AI-native workbench, used through chat, for evolving norms for networks of AI agents by tweaking interpretable rules. The aim is alignment. Nothing here shows it yet. The author talks loosely about how agents should behave. The system turns that into precise rules (ADICO cards, also English-like sentences), proves what it can, runs experiments, and answers in plain English and charts. Proof checks filter candidate rules, a patcher mutates them, and a ladder of adversaries from cheap decision models to strong LLMs tests them.

**Research question.** Which norms let a network of agents cooperate freely, and at what agent capability and price do agents start finding exploits the formal model did not predict? Freedom here is equal liberty minus domination (ADR 0014). The good is pleasure, with two kinds of suffering (ADR 0010). Cooperation means shared needs are met and outsiders do not pay.

**Product.** An evaluator that evolves with the norms. There are two loops. Rules against the test: do new seams per round slow? The test against the author's intent: do "not what I meant" moments per round fall?

**Status: early results, scripted agents in toy worlds.** The instruments behave. Many world-level predictions missed, and the misses are recorded. Four live ladder runs (about $10) found no inventive seam on L1 to L4. The first was uninformative (a harness defect). After the fix, the capability ranking came out inverted: cheap models exploited most, and Claude models disengaged or refused under loophole framing. A review council of five found no result unsound and many sound with caveats. Nothing here is a finding about real people. Index of every run: [docs/results/README.md](docs/results/README.md).

**Hedonic technology.** The author's view is that pleasure is a technology that rules can serve or wear down, and that the experiencing self is the remembering self, through vividness of memory. The author confirmed the seed norms on the condition that they demonstrate pleasure in relationships. A scripted demonstration held all eight predictions, with caveats: the rules mostly protect, and the relational share comes from persona weights. Lifetime pleasure against greedy play is in progress (ADR 0016, ADR 0017). Notes: [docs/notes/hedonic-technology-synthesis.md](docs/notes/hedonic-technology-synthesis.md).

## Read first

- [docs/goal.md](docs/goal.md): where we are, what we have learned, what is running
- [docs/pitch.md](docs/pitch.md): the question on one page
- [docs/results/README.md](docs/results/README.md): every experiment, its prereg and its verdict
- [docs/decisions/README.md](docs/decisions/README.md): the ADRs, 0001 to 0017 (0016 and 0017 in progress)
- [docs/plan.md](docs/plan.md): queue, slices and log
- [docs/demo.md](docs/demo.md): the five-minute household demo
- [docs/claims.md](docs/claims.md): claims register (status of each claim; predictions live in the prereg files)
- [RATIONALE.md](RATIONALE.md): why this project, prior art, design decisions, kill criteria

## Layout

```
RATIONALE.md              project rationale
CONTRIBUTING.md           conventions
docs/goal.md, pitch.md    where we are; the question on one page
docs/plan.md              queue, slices, log
docs/claims.md            claims register
docs/decisions/           ADRs and their index
docs/results/             preregs, results, and an index
docs/prior-art/           prior-art checks, with an index of their confidence
docs/seeds/               the author's household norms, verbatim
docs/notes/               syntheses of the author's notes
docs/demo.md              the five-minute household demo
docs/reviews/             review-council convention and reports
docs/surprises.md         unexpected observations
docs/negative-results.md  negative results
experiments/              question, change and experiment logs; timeline snapshots
src/mar/                  harness, cards, gate, oracle, patcher, miner, worlds, evolution, scores
rules/                    ADICO cards per world (fishery, household, vpgg, bargaining)
personas/                 hand personas and a 32-skeleton grid
scripts/                  one run script per experiment
tests/                    tests
```

## Start locally

Needs [uv](https://docs.astral.sh/uv/) (Python 3.10+). Z3 gates agent actions. Scripted runs need no model calls or network.

```
uv sync
uv run pytest                      # unit tests
uv run python scripts/v2_run.py    # V2 instrument-calibration table (about 10 s)
uv run mar results                 # one-line verdict per results file
uv run mar lint                    # lint every rule set (no model calls)
uv run mar timeline --keep         # dated snapshot of the project's history
```

Live runs (`mar ladder`) need API keys in `.env` and a spend cap. They refuse to run without `--max-usd`. Pushing to GitHub now works from sessions opened in the repo: a narrow allow rule for `git push origin main` is in `.claude/settings.local.json`. Claude Code auto mode blocked pushes from the original session.

Related: [philosophy-engine](https://github.com/reeswrites/philosophy-engine) is an input (ADICO schema, reference engine), not part of this repo.

## License

Apache-2.0. See [LICENSE](LICENSE).
