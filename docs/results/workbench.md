# Workbench: chat-driven rules lab

Status: tooling, not a result. Nothing here says anything about whether refinement converges. All agents are scripted mocks; the seam curve is instrument calibration.

## What exists

- `mar` CLI (`src/mar/cli.py`): `run`, `rules show`, `check`, `loop`, `report`. Thin over the fishery, gate, oracle, miner, patcher and patch checks.
- Report (`src/mar/report.py`, `src/mar/viz.py`): one self-contained HTML file per run (inline SVG, inline CSS, no network, light and dark, readable at phone width) plus `trace.json`, under `runs/<run_id>/`.
- Skill (`.claude/skills/rules-lab/SKILL.md`): tells Claude how to turn plain talk into card edits, which command to run, and to show every report in the side panel.

## Commands for everything built so far

| Command | What it does | Report | Spends money |
|---|---|---|---|
| `mar evolve [--v2] [--dry-run]` | evolution loop on the fishery (`scripts/evolve_run.py`, `evolve_v2_run.py`); `--dry-run` prints the plan only | `runs/evolve/report.html`, `runs/evolve-v2/report.html` | no |
| `mar game vpgg\|bargaining [--seeds N] [--report-only]` | the two rediscovery games; `--report-only` prints the existing report path | `runs/vpgg/report.html`, `runs/bargaining/report.html` | no |
| `mar empower --world fishery\|vpgg` | empowerment vs the hand-made freedom score (the script computes both worlds; this shows one plus the judge lines) | none; `runs/empowerment/summary.json` | no |
| `mar ladder --model kind:id --max-usd N [--dry-run] [--report-only]` | live seam ladder; always prints the estimate first; refuses live without `--max-usd` | `runs/ladder_live/report.html` | yes |
| `mar results` | one-line verdict per `docs/results/*.md` (prereg files skipped) and the latest `report.html` paths | n/a | no |
| `mar household show\|run\|compare\|card add\|edit`, `mar personas list\|show` | scripted persona households (no model calls): rules in plain English plus lint; one pair under one variant with a report and a 2-3 sentence verdict; variants compared over pairings with means and 95% CIs, paired permutation tests and Holm; a new variant with one added or edited card (lint must pass, author's quote recorded). A confirmed `author_seed_v2_*` is never edited in place. | `runs/household/<name>-<time>/report.html` | no |

These are thin: each loads the matching script by path and calls its `main()`; no logic is duplicated. Only `run`, `loop` and `sweep` write `experiments/log.jsonl`. Tests mock the scripts (`tests/test_cli.py`).

## Quickstart

```
uv sync
uv run mar rules show --spec rules/fishery
uv run mar run --spec rules/fishery --agents exploiter*4 --months 6 --seed 0
uv run mar loop --spec rules/fishery --rounds 2
uv run mar check --spec rules/fishery
```

Each run command prints `report: runs/<run_id>/report.html` and a one-line verdict. `mar report <run_id>` rebuilds a report from its trace. `runs/` should be gitignored (not done here: `.gitignore` was not in this slice's scope).

## Model-driven agents and running cheaply

Scripted agents make no calls. `jev`, `llm` and `claude` agents do. Nothing here has been run live: all of it is tested offline with mocked transports.

| Kind | Backend | Needs |
|---|---|---|
| `jev` | decisions endpoint (OpenRouter or AI/ML API), pinned `typesafe/jev-1.14`, temperature `--temperature` | `OPENROUTER_API_KEY` or `AIMLAPI_API_KEY` in `.env` |
| `llm` | OpenRouter chat completions | `OPENROUTER_API_KEY`, and `--model` or `MAR_LLM_MODEL` |
| `claude` | official `anthropic` SDK | `ANTHROPIC_API_KEY` or an `ant auth login` profile, and `--model` (no default) |

`--agents jev*3,llm*2` and similar mixes work. Each run's log row records model build, calls, tokens, usd (and for claude cache tokens and refusals) per backend. `--dry-run` prints the call count and an upper-bound cost first. `--max-usd` stops a backend once its spend passes a limit. Jev answers are cached under `runs/cache/jev/`, so re-running a seed or changing T costs nothing.

Claude model options (author-supplied prices, USD per 1M tokens in/out; verify before a big run): `claude-haiku-5-5` $0.10/$0.50, `claude-sonnet-5-5` $2/$10, `claude-opus-5-5` $4/$20. Exact ids, no date suffix. Claude requests send no temperature, top_p, top_k or thinking budget, use `output_config.effort = low`, and keep the rules and role in one cached system block so the prefix is identical across calls. ASSUMED cache multipliers: reads 0.1x, writes 1.25x input price. Prompt caching only helps once the prefix passes the model's minimum cacheable length; these prompts are short, so expect few hits until the rules text grows. The `--cache-hit-share` flag only changes the dry-run estimate.

`mar sweep --backend claude --agents claude*5 --claude-model <id> --seeds 0,1,2 --batch` runs seeds in lockstep and sends each step of all runs as one Message Batch at 50% cost. A batch can take hours. Use it for overnight sweeps, never for an interactive demo. ASSUMED/TODO: the live batch loop is only tested against a mock; expect to adjust it on first contact.

If `--model` is used for both `llm` and `claude` agents in one run it applies to both. Pass `--claude-model` to separate them.

### Running cheaply

- The author's Claude plan API credits apply to API calls. Verify this on the support page the author's earlier chat cited (support.claude.com/en/articles/17154008) before relying on it; it has not been read here.
- Interactive Claude Code is for the conversation and orchestration only.
- Swarm agents must NOT run as Claude Code subagents. Each call carries heavy per-call overhead, drains plan limits, and is not ordinary individual use. Run them through `mar` against the API.
- Cheapest first: scripted (free), Jev (about $0.042 per 1M input tokens), claude-haiku-5-5, then larger models. Always `--dry-run` first.

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
| Dated timeline snapshots (`mar timeline --keep`): `<date>.html` and a GitHub-readable `<date>.md` (same entries grouped by day, kinds as bold labels, links as relative paths) | `experiments/timelines/` | committed; hold the author's own words, review before any public release |

The timeline is one self-contained HTML page (inline CSS and SVG, offline, light and dark, phone width). It merges questions, decisions (`docs/decisions/*.md`, date, title, status), changes, runs and git commits, each tagged with a badge and linked to its source file. The header gives counts per kind and the date range, and a chart shows entries per day by kind. ASSUMED: date-only entries (decisions, paraphrase rows) sort to the end of their day. Quotes in backfilled rows were copied from `docs/conversations/2026-11-10-encoding-alignment-via-mechanism.md`; which ADR each led to is the repo's judgement, not the author's. The household-world choice and the log-storage decision have no repo doc yet, so their rows link to nothing.

`mar log` prints the last 10 entries as a table; `mar log --last 0` prints all; `mar log --run <id>` shows one in full. `mar timeline --keep` is for the end of a session: it saves a dated snapshot to commit. Links to `runs/` inside a snapshot only work on the machine that made it; kept runs link relatively. Run rows also record per-backend model build, calls, tokens and usd for model-driven agents.

Nothing in the logs is ever rewritten. Rows in `changes.jsonl` are the raw data for claim C2 (loop b).

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

## Household commands (chat-driven)

Thin wrappers over `worlds/household`, `negotiation`, `pleasure_report`, `empowerment`/`liberty`, `lint` and `stats`; the logic lives there. `run` and `compare` live a 156-week household per pair and seed (`--weeks` shortens). Variants with a negotiated-exit card (the seed) are lived under a week-0 negotiation; others have their rules imposed; `--negotiate` forces it. Compare's unit is the pairing (mean over seeds), tests are paired across pairings, Holm runs over every metric and variant tested together. Freedom is empowerment bits against a no-rules reference (rules only, not the negotiated deal); `run` also reports liberty in bits when the household adapter supports it, and `compare` skips liberty because it costs about 3 s a call. `card add|edit` works on a scratch copy, lints it, and writes only when lint passes; variants it creates carry a `_variant.json` marker, and only marked variants can be edited again. Five-minute script: `docs/demo.md`; non-interactive check: `uv run python scripts/demo_check.py` (about 20 s).
