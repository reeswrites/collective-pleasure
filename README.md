# multi-agent-rules

Evolving norms for agent networks, tested so far on scripted agents in toy worlds.

An AI-native workbench, used through chat, for evolving norms for networks of AI agents by tweaking interpretable rules. The aim is alignment. Nothing here shows it yet. The author talks loosely about how agents should behave. The system turns that into precise rules (ADICO cards, also English-like sentences), proves what it can, runs experiments, and answers in plain English and charts. Proof checks filter candidate rules, a patcher mutates them, and a ladder of adversaries from cheap decision models to strong LLMs tests them.

**Research question.** Which norms let a network of agents cooperate freely, and at what agent capability and price do agents start finding exploits the formal model did not predict? Freedom here is equal liberty minus domination (ADR 0014). The good is pleasure, with two kinds of suffering (ADR 0010). Cooperation means shared needs are met and outsiders do not pay.

**Product.** An evaluator that evolves with the norms. There are two loops. Rules against the test: do new seams per round slow? The test against the author's intent: do "not what I meant" moments per round fall?

**Status (2026-11-11): early results, scripted agents in toy worlds.** Nothing here is a finding about real people, and agents feel nothing. Read [docs/limits.md](docs/limits.md) before citing anything. Index of every run, with corrections: [docs/results/README.md](docs/results/README.md). One-page summary: [docs/one-pager.md](docs/one-pager.md).

- **Inventive seams (the central claim, IT1): untested so far, now being tested.** The earlier "none found" on ladder rungs L1 to L4 was a design artifact: the formal model already reached every harm there. A rerun on rungs where a paying inventive seam is reachable (checked first by a free gate) is running under an $8 cap. Candidates count only after the author reads them.
- **Loop a (rules against the test): it works, and it exploits the test.** Household evolution beat the author's seed on liberty but dropped every commitment power, because the test did not value them. The evaluator is being fixed (a plain-English loss report, liberty that counts normative powers, a lifetime horizon) and evolution rerun.
- **Loop b (the test against the author's intent): not yet measurable.** The first count found the rule not operational, because the log never recorded what the author was shown. A per-read-back log (experiments/readbacks.jsonl) started on 2026-11-11.
- **Corrections are part of the record.** Two designs could not produce the verdict they tested (IT1 on L1 to L4, the first H32), several headlines were softened by review, and a third of the sensitivity-swept conclusions are fragile. Every prereg now has to show, with a free check, that each verdict can happen ([docs/templates/prereg.md](docs/templates/prereg.md)). See [docs/negative-results.md](docs/negative-results.md) and [docs/reviews/](docs/reviews/).

**Hedonic technology.** The author holds that pleasure is the good, and that relationships and rules are technology that can produce it, not only protect it. The theory and the three tests the evaluator uses (liking vs wanting, worth it vs hard to leave, security vs checking) are in [docs/theory.md](docs/theory.md) and ADR 0018; tests 1 and 2 are built. The author's seed norms (v2.2, and a partly confirmed v2.3) are judged on one condition, that they produce pleasure in relationships; a retest with the household fixes is designed and waits on the fixes (judged on pleasure, net shown, everyone counts). The author's answers to the open questions: [docs/notes/hedonic-technology-synthesis.md](docs/notes/hedonic-technology-synthesis.md), section 5.

## Read first

- [docs/goal.md](docs/goal.md): where we are, what we have learned, what is running
- [docs/pitch.md](docs/pitch.md): the question on one page
- [docs/results/README.md](docs/results/README.md): every experiment, its prereg and its verdict
- [docs/one-pager.md](docs/one-pager.md): one page, what held and what was corrected
- [docs/limits.md](docs/limits.md): what results here can and cannot be about
- [docs/theory.md](docs/theory.md): hedonic technology, the theory being tested
- [docs/decisions/README.md](docs/decisions/README.md): the ADRs, 0001 to 0018
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
docs/limits.md            limits of the model world
docs/theory.md            hedonic technology theory
docs/plans/               plans for upcoming experiments
docs/surprises.md         unexpected observations
docs/negative-results.md  negative results
experiments/              question, change, read-back and experiment logs; timeline snapshots
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
uv run pytest                      # unit tests (slow tests skipped; full run: -m "")
uv run python scripts/v2_run.py    # V2 instrument-calibration table (about 10 s)
uv run mar results                 # one-line verdict per results file
uv run mar lint                    # lint every rule set (no model calls)
uv run mar timeline --keep         # dated snapshot of the project's history
```

Live runs (`mar ladder`, `scripts/it1_run.py`) need API keys in `.env` and a spend cap. They refuse to run without `--max-usd` and an approved prereg. Full-suite test runs queue behind a lock (tests/conftest.py) because several agents share one checkout.

Related: [philosophy-engine](https://github.com/reeswrites/philosophy-engine) is an input (ADICO schema, reference engine), not part of this repo.

## License

Apache-2.0. See [LICENSE](LICENSE).
