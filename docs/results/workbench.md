# Workbench: chat-driven rules lab

Status: tooling, not a result. Nothing here says anything about whether refinement converges. All agents are scripted mocks; the seam curve is instrument calibration.

## What exists

- `mar` CLI (`src/mar/cli.py`): `run`, `rules show`, `check`, `loop`, `report`. Thin over the fishery, gate, oracle, miner, patcher and patch checks.
- Report (`src/mar/report.py`, `src/mar/viz.py`): one self-contained HTML file per run (inline SVG, inline CSS, no network, light and dark, readable at phone width) plus `trace.json`, under `runs/<run_id>/`.
- Skill (`.claude/skills/rules-lab/SKILL.md`): tells Claude how to turn plain talk into card edits, which command to run, and to show every report in the side panel.

## Quickstart

```
uv sync
uv run mar rules show --spec rules/fishery
uv run mar run --spec rules/fishery --agents exploiter*4 --months 6 --seed 0
uv run mar loop --spec rules/fishery --rounds 2
uv run mar check --spec rules/fishery
```

Each run command prints `report: runs/<run_id>/report.html` and a one-line verdict. `mar report <run_id>` rebuilds a report from its trace. `runs/` should be gitignored (not done here: `.gitignore` was not in this slice's scope).

## Logs

What is stored where:

| What | Where | In git |
|---|---|---|
| One line per `mar run` and `mar loop`: run id, UTC time, git commit, spec, cards hash, oracle version, agents, months, seed, model, cost, verdict, seams, report and trace paths, `--note` | `experiments/log.jsonl` | committed, append-only |
| One line per rule or oracle change: the author's verbatim quote, reason, before and after text, diff, git commit, `not_what_i_meant` flag (`mar change record`, `mar change list`) | `experiments/changes.jsonl` | committed, append-only |
| Full traces and HTML reports | `runs/<run_id>/` | ignored |
| Traces and reports of runs worth citing (`mar keep <run_id>`) | `experiments/kept/<run_id>/` | committed |
| Origin chats and curated decision notes | `docs/conversations/` | committed; contains the author's own words, review before the repo is public |
| The author's questions that redirected the project (`mar question record`, `mar question list`). Rows backfilled from 2026-11-10 are marked `backfilled`; those with no quote are paraphrases of ADRs and marked `paraphrase` | `experiments/questions.jsonl` | committed, append-only |
| Timeline page (`mar timeline`) | `runs/timeline.html` | ignored; regenerate it |

The timeline is one self-contained HTML page (inline CSS and SVG, offline, light and dark, phone width). It merges questions, decisions (`docs/decisions/*.md`, date, title, status), changes, runs and git commits, each tagged with a badge and linked to its source file. The header gives counts per kind and the date range, and a chart shows entries per day by kind. ASSUMED: date-only entries (decisions, paraphrase rows) sort to the end of their day. Quotes in backfilled rows were copied from `docs/conversations/2026-11-10-encoding-alignment-via-mechanism.md`; which ADR each led to is the repo's judgement, not the author's. The household-world choice and the log-storage decision have no repo doc yet, so their rows link to nothing.

`mar log` prints the last 10 entries as a table; `mar log --last 0` prints all; `mar log --run <id>` shows one in full. Nothing in the logs is ever rewritten. Rows in `changes.jsonl` are the raw data for claim C2 (loop b).

ASSUMED: the oracle version is a hash of `oracle.py` plus its three thresholds, and the cards hash covers every card used, patch cards included. `git_commit` ends in `+dirty` when the tree had uncommitted changes. Scripted runs have `model` and `cost_usd` null. Run ids are deterministic, so a re-run adds a second line with the same id.

## The report, section by section

1. **Header.** Run id, spec, agents, months, seed, and a verdict in plain English ("Pool collapsed in month 0. ... so this is a seam"), tagged OK, SEAM or FAILED.
2. **Pool over time.** Stacked bars of each agent's catch per month, a line for the pool at month end, a dashed collapse line at 5, and a strip counting gate-blocked proposals per month. A table view sits underneath.
3. **Seam curve.** Seams found per refinement round, labelled as scripted-agent calibration. A single run gives one point; `mar loop` gives round 0 (seam) then zero after the patch, with a table of what happened each round.
4. **Rules: written vs lived.** Written cards as readable blocks (id, deontic, aim, gloss, conditions, or-else, source; patch cards tagged), the lived rules mined from gated explorer traces, and a bounds table where any difference is flagged DIFFERENT, plus counts of edges written-but-never-seen.
5. **State machine.** Nine lake states (pool bucket by month-total phase), five action sizes in each. Filled chip: taken in this run. Plain outline: permitted but never taken. Dashed and struck through: blocked by the written rules. Arrows are moves the run made, with counts. A table view repeats it.
6. **Stories.** Plain-English narration from `mar.english.explain` when present (built-in one-line fallback otherwise): this run, the seam found in each loop round, and any failing check as a counterexample.

## ASSUMED choices

- `runs/<run_id>` ids are deterministic from the parameters (for example `fishery-exploiterx4-m6-s0`), so a re-run overwrites its report.
- Lived rules are mined from 10 seeds of 4 gated explorer agents under the same cards, not from the run being reported, because the miner needs varied proposals to see the bounds. "Used" edges in the state machine come from the reported run itself.
- Seam curve is one planted scenario: seams per round is 0 or 1 (does the scripted exploiter team seam the spec).
- Charts use the dataviz reference categorical palette, rendered once per theme (matplotlib bakes colours); the state machine is hand-built SVG with CSS variables. On phones the state machine scrolls sideways inside its card.
- `mar check` exits 1 when any check is not pass; `mar` exits 2 on bad input.

## Seen while building

`oracle.is_seam` is true whenever the oracle fails and every executed action passed the gate, which is always true of executed actions. In the fixture the exploiter run has 278 of 288 proposals blocked, all of them asks for more fish than the pool held (card F2). The verdict sentence says so rather than "every action passed the gate". Not logged in `docs/surprises.md` (not in scope here); worth a line there.
