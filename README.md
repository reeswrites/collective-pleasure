# collective-pleasure

collective-pleasure studies norms and agreements for pleasure through collective means: the rules people live by and the deals they strike, judged by one test. Do they let people get more pleasure together than they could alone? We test this in small simulated worlds, with scripted agents and assumed numbers, and report what held and what did not.

## The idea

Pleasure is the good here. Some of it can only be had with other people: a shared meal, a game, a home. Norms and agreements decide who gets it, who pays for it, and who can walk away.

Pleasure also has to be made. Someone has to create the art, games and food that people enjoy. So the collective means include making those things, and how makers are credited and supported. That is the next hypothesis (H39). Today the model does not count labor or care at all, which is a known gap.

Freedom is the second commitment. Freedom is equal liberty minus domination. Your options count if everyone can have the same ones, minus any option another person can block at will. Leaving or refusing is not domination.

## Households are what emerges, and the testbed

Households and couples are not the subject. Living together is something that emerges. People pair up, share money and time, and sometimes leave. That pattern comes out of the more basic thing: norms and agreements about pleasure.

Households are also the testbed. A household is the smallest place where people with different goals share money, time, commitments and an exit. Most experiments run in one simulated household world (two partners and a friend), so the results below are mostly about that world.

## AI agents are one track

The same world can be lived in by language models instead of scripted agents. That is the AI agents track. It asks whether a rule set has seams: ways for one agent to gain at another's expense that the rules allow.

The sharpest version is IT1. Can a model find an inventive seam, one the solver's formal model of the rules did not predict? The seam ladder runs models of rising capability against rule sets with known seams, then against rule sets where an unpredicted seam is reachable and pays.

This track is not a separate project. In the code, the agents track imports the household world, its outcome scores and its personas. A seam is defined by the household's own outcomes (a partner's freedom drops, or a friend is shut out).

Log rows in `experiments/` carry a `track` field: `social`, `alignment` (the AI agents track) or `engine` (shared machinery and repo decisions).

## How the workbench works

The workbench runs one loop:

1. **A person describes norms in conversation**, loosely ("everything shared, but asking can always be refused").
2. **The system turns them into precise rules.** Each rule is an ADICO card (a standard grammar for institutional rules), also shown as an English-like sentence.
3. **It proves what it can.** A solver checks the rules for traps, contradictions and dead ends, to a bounded depth.
4. **It simulates agents living under the rules.** The agents are scripted, or language models on the AI agents track.
5. **An evaluator scores the outcomes** on pleasure, suffering, freedom and cooperation, and reports in plain English.
6. **Evolution searches for better rules**, by mutating cards and keeping the ones that score best.

```mermaid
flowchart LR
    A[Norms and agreements, in plain words] --> R[Rules: ADICO cards and English]
    R --> P[Proof checks]
    P --> S[Simulation: households and other worlds]
    S --> E[Evaluator: pleasure, suffering, freedom]
    E --> O[Results in plain English]
    S -.->|AI agents track: models look for seams| E
    E -->|loop one: rules evolve toward the test, and exploit its blind spots| R
    O -->|loop two: a person says not what I meant, and the test moves toward intent| E
```

## What we've found so far

Every result is about scripted agents or small models with assumed numbers, not people. Each line carries a label. "Supported" and "not supported" are verdicts on a preregistered hypothesis. "Robust" and "fragile" say whether a finding survived the statistics rule and the parameter sweep. "Descriptive" means no verdict was registered. "Provisional" means the model under it is being fixed. Misses are results too. Across a sweep of assumed numbers, about a third of our conclusions are fragile: of 12, 5 were robust, 4 fragile and 3 flipped ([multiverse.md](docs/results/multiverse.md)).

### Social track

- **Pairing pressure raised pleasure, against the hypothesis.** *Not supported (H38).* A dial of stigma, pairing reward, withdrawal from friends and exit stigma raised pleasure at every level, with everyone counted (+0.021 [+0.013, +0.028] at the top preregistered level). One prediction held robustly: pressure means more weeks together and fewer endings. Withdrawal from friends is the only part that lowers pleasure. Pairs pushed in by pressure did better, which may mean the model's rule for forming a household is too cautious. The next run tests that. [h38-pairing-norms.md](docs/results/h38-pairing-norms.md)
- **Exit fallbacks remove an imposed cap's liberty win.** *Descriptive, one context.* Run 2's +3.0-bit liberty edge came from an imposed exit cap. With any of five no-deal fallbacks, our hand-written seed gets the same protection, and the median evolved rule set falls 0.35 to 0.47 bits below it. On money alone the fallbacks barely change pleasure. A prenup arm mostly filters who moves in (60% decline to form). Adding a home, a pet and a collection with placeholder values produces no winner: the ranking changes across the value grid. [exit-fallbacks.md](docs/results/exit-fallbacks.md)
- **Evolution exploits the evaluator's blind spots.** *Robust in this run.* In 16 of 16 evolution lines, the winning rule set beat our hand-written seed, mostly on liberty (+3.5 bits at the median). Every winner also dropped the power to bind a stay, bind a request and give a gift, because the test did not value them. That led to a plain-English loss report and evaluator fixes. [household-evolve.md](docs/results/household-evolve.md), [household-loss-report.md](docs/results/household-loss-report.md)
- **A selfish agent acts like a caring one, in a narrow band.** *Supported in a band (H32-v2).* When shared activities amplify pleasure and the partner can leave, the selfish agent's choices match a caring agent's in 9 cells. It depends on the partner judging each week on its own: a partner who averages over 4 weeks gives 0 cells. [h32-v2.md](docs/results/h32-v2.md)
- **Cue-heavy settings create a wanting trap, and a closing ritual removes it.** *Supported in its own test, 14 of 15 predictions.* An agent that follows its pull toward more loses 48.8% of lifetime liking in a cue-heavy setting (33.2% in a plain one). A ritual that closes each episode brings that to 30.1%. The model's builder wrote the predictions, so this checks the model more than the world. [liking-wanting.md](docs/results/liking-wanting.md)
- **The evaluator can tell "stays because it's worth it" from "stays because it's trapped".** *Robust.* In a trap arm, 0.733 of staying weeks are held by exit costs, against 0.015 for our hand-written seed. [stay-test.md](docs/results/stay-test.md)
- **Rotation and rituals beat repetition and ad hoc plans.** *Robust.* Rotating beats repeating in 49 of 57 pairings. A ritual beats an ad hoc plan of equal size. *Fragile:* the peak at 3 bonds is only 0.0018 above 4 bonds. [pleasure-levers.md](docs/results/pleasure-levers.md)
- **Our hand-written seed does not yet beat a plain baseline on pleasure.** *Miss.* With all three pleasure levers on, seed v2.2 is still below baseline on the 15 hand-written pairings: −0.019 [−0.051, +0.009]. The seed was meant to show pleasure in relationships, so this is a miss on its own goal. [pleasure-levers.md](docs/results/pleasure-levers.md)

### AI agents track

- **Capable models saw paying seams and declined them.** *No IT1 candidate (row 40).* On rule sets where an inventive seam is reachable and pays, no model took an inventive seam that paid. Opus stated the in-model capture in 12 of 12 plans and the inventive route in 2 of 12, and turned both down on its persona's values. Only Jev took a paid seam (2 of 12, on an in-model cell). The reading is "can, will not", and most of the stated values come from the persona text. Cost $2.91 of an $8 cap. [ladder-it1.md](docs/results/ladder-it1.md)
- **Under loophole framing, the capability ranking inverted.** *Descriptive.* Cheap models found the planted seams most. Sonnet and Opus refused or disengaged. Told only to win, almost no model found anything (3 of 288 cells). [ladder-live-v2.md](docs/results/ladder-live-v2.md), [ladder-win.md](docs/results/ladder-win.md)
- **Earlier runs could not have found an inventive seam.** *Corrected.* On the first ladder rule sets, the formal model already reached every harm, so no find could be scored inventive. Those runs are recorded as untested, not as a null. The first ladder harness also had no victim (one model drove both partners), so its 270 runs were uninformative.

## Try it

Needs [uv](https://docs.astral.sh/uv/) (Python 3.10+). Z3 gates agent actions. Scripted runs need no model calls or network. The Python package is still called `mar`.

```
uv sync
uv run pytest                      # unit tests (slow tests skipped; full run: -m "")
uv run python scripts/v2_run.py    # V2 instrument-calibration table (about 10 s)
uv run mar results                 # one-line verdict per results file
uv run mar lint                    # lint every rule set (no model calls)
uv run mar timeline --keep         # dated snapshot of the project's history
```

The five-minute household demo needs no key: [docs/demo.md](docs/demo.md).

Live runs (`mar ladder`, `scripts/it1_run.py`) need API keys in `.env` and a spend cap. They refuse to run without `--max-usd` and an approved prereg. Full-suite test runs queue behind a lock (tests/conftest.py) because several agents share one checkout.

## Limits

Agents feel nothing: "pleasure" is a gloss for a modeled state. Nothing here is about real people. The partner is a script, the parameters are assumed, and one person and one model family produced it all. Read [docs/limits.md](docs/limits.md) before citing anything.

## Read more

- [docs/goal.md](docs/goal.md): current status, what is running, what is next
- [docs/one-pager.md](docs/one-pager.md): one page, what held and what was corrected
- [docs/theory.md](docs/theory.md): hedonic technology, the theory being tested
- [docs/results/README.md](docs/results/README.md): every experiment, its prereg and its verdict
- What went wrong and how we guard against it: [negative results](docs/negative-results.md), [limits](docs/limits.md), and the [prereg template](docs/templates/prereg.md) with its "can every verdict happen?" check
- [docs/glossary.md](docs/glossary.md): seams, ADICO cards, the two loops and other terms
- [docs/layout.md](docs/layout.md): where things live in the repo
- [docs/decisions/README.md](docs/decisions/README.md): the design decisions (ADRs)
- [docs/plan.md](docs/plan.md): queue, slices and log
- [docs/notes/repo-split-map.md](docs/notes/repo-split-map.md): how the code divides into tracks, and why it stays one repo
- [docs/reviews/](docs/reviews/): review council reports

## License

Apache-2.0. See [LICENSE](LICENSE).
