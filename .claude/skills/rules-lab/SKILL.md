---
name: rules-lab
description: Use when the author wants to write, read, change, check or run rules or swarm experiments in this repo, or asks what happened in a run. Turns plain talk into rule-card edits, runs the `mar` CLI, and shows the HTML report.
---

# rules-lab

The author talks; you edit rule cards, run experiments and show graphics. They should rarely need to read YAML or a terminal.

## 1. Plain talk to card edits

Rules are YAML cards in a spec directory (`rules/fishery/`, one file per card, id like `F1`). Fields: `id, attribute, deontic (must | must_not | may), aim, conditions, or_else, gloss, source`. A `must_not` card is violated when ALL its conditions hold; a `must` card is violated unless all hold. Conditions are `{expr, op: gt|ge|lt|le|eq, value}` over `catch`, `pool`, `month_total` (for example `month_total + catch`).

- Always write a one-sentence `gloss` and a `source` (who or what the rule comes from; "author, chat <date>" is fine). `load_cards` rejects a card without them.
- New card: new file `<id>-<slug>.yaml`, next free id. Change a card: edit in place. Never reuse an id for a different rule.
- Experiments that compare specs: copy the directory to a new one (`rules/fishery-v2/`) rather than mutating the baseline.
- Before running anything, **read the change back in plain English**: say which card changed and what it now forbids or requires, in the author's words ("so together, fishers can take at most 40 a month"). Run `mar rules show --spec <dir>` to confirm what the cards actually say, then proceed. If the author's wording is ambiguous (per action or per month? each fisher or the group?), ask one short question.
- **Record every change before making it.** Whenever a chat leads you to change a rule card or the oracle, FIRST run `uv run mar change record --kind rule|oracle --quote "<exact words>" --reason "<one line>" --before <old file or -> --after <new file>`. Save the intended new text to a scratch file for `--after` (the real file is edited afterwards). The quote is the author's exact words from their latest message, copied verbatim: never paraphrase, never tidy typos. If several messages drove the change, quote each (repeat the command or join them with the author's own text). Add `--nwim` when the author is rejecting what a run or rule did ("that's not what I meant"). Then make the edit, then read it back (see above). These rows are the raw data for claim C2 (loop b), so a missing or paraphrased quote spoils it. `mar change list` shows them.
- **Never edit preregistration files** (`docs/results/*-prereg.md`, and the predictions already committed in `docs/claims.md`). Prereg first: if a new experiment is wanted, draft its prediction in a new prereg and get the author's OK before running.

## 2. Which command for which request

Run from the repo root with `uv run mar ...`.

| The author says | Command |
|---|---|
| "show me the rules", "what do the rules say" | `mar rules show --spec rules/fishery` |
| "is this rule set OK", "any conflicts or deadlocks" | `mar check --spec <dir> [--k 3]` |
| "run it", "what happens with greedy fishers" | `mar run --spec <dir> --agents exploiter,compliant --months 6 --seed 0` |
| "does fixing it work", "patch and rerun", "the loop" | `mar loop --spec <dir> --rounds 2` |
| "show me that run again" | `mar report <run_id>` (rebuilds from `runs/<run_id>/trace.json`) |

Every run and loop must pass `--note "<one-line plain summary of why this run was made>"`. Each one appends a line to `experiments/log.jsonl` (committed, append-only). `mar log` lists recent entries, `mar log --run <id>` shows one in full, and `mar keep <run_id>` copies a run's trace and report to `experiments/kept/<run_id>/` so a cited run can be committed.

Model-driven agents: `jev*n`, `llm*n` and `claude*n` call APIs and need keys in `.env` (never ask for a key in chat). Always run with `--dry-run` first and tell the author the upper-bound cost; run live only when the author says so. `claude` needs `--model` (haiku-5-5, sonnet-5-5 or opus-5-5, exact ids). Reports then include a Say vs do panel. Never run swarm agents as Claude Code subagents. See docs/results/workbench.md.

Agent kinds: `exploiter` (takes the max every round), `compliant` (modest), `explorer` (random, used for mining). `name*n` repeats. These are scripted mocks: no LLM is called anywhere. Reports and traces land in `runs/<run_id>/` (gitignored; do not commit them).

Curiosity log and timeline. When the author asks a question that redirects the project or opens a new line of curiosity, record it with `uv run mar question record --quote "<exact words>" --topic "<short>" [--led-to "ADR 0006"]` (verbatim, never paraphrased; `--led-to` can repeat). `mar question list` prints them. When the author asks "how did we get here" or similar, run `uv run mar timeline` and show `runs/timeline.html` in the side panel with SendUserFile `display: "render"`. It merges questions, decisions, changes, runs and commits in time order.

**Saving progress.** At the end of a working session, or when the author asks to save progress, run `uv run mar timeline --keep`. It writes `experiments/timelines/<date>.html` and `<date>.md`. Commit both with a pathspec commit (`git add <the two files>` then `git commit -F <msgfile> -- <the two files>`), then show the `.html` in the side panel with SendUserFile `display: "render"`. The snapshots contain the author's own words; do not push or publish them.

## 2b. Everything else the workbench can run

Plain words to command (run from the repo root with `uv run mar ...`). Scripted commands make no model calls and cost nothing.

| The author says | Command | Costs money? |
|---|---|---|
| "run the evolution loop", "evolve rules on the fishery" | `mar evolve` (add `--v2` for the v2 setup; `--dry-run` says what would run). 4 to 5 minutes. | no |
| "run the public goods game", "vpgg" | `mar game vpgg [--seeds 20]` | no |
| "run the bargaining game", "outside options" | `mar game bargaining [--seeds 20]` | no |
| "show the vpgg / bargaining report again" | `mar game vpgg --report-only` (prints the existing report path) | no |
| "does empowerment agree with the freedom score" | `mar empower --world fishery` or `--world vpgg` | no |
| "put a real model on the ladder", "run the live ladder" | `mar ladder --model kind:id --max-usd N` (`--dry-run`, `--report-only`) | YES |
| "what have we found", "what are the results", "list the reports" | `mar results` (one-line verdicts plus latest report.html paths) | no |
| "run the household" | `mar household` is a stub. TODO: household commands land after the seed v2 run (its API is changing; do not wire it here yet). | n/a |

Rules for these:

- **Anything that spends money (`mar ladder`, any `jev`, `llm` or `claude` agent): run it with `--dry-run` first, show the author the dry-run estimate in chat, and run live only after their yes in chat.** `mar ladder` always prints the estimate first and refuses live without `--max-usd`; the cap is the author's number, not yours.
- After any run: these scripts do not write the experiment log (only `mar run`, `loop` and `sweep` do), so say that, and note the run in your reply (command, seeds, date). Then open the report: SendUserFile with the path from the `report: ...` line and `display: "render"`. `mar empower` has no HTML; read out its PASS/FAIL lines instead. Then summarize in two or three plain sentences. Use the verdict wording from the matching `docs/results/*.md`, never stronger.
- When the author redirects or corrects something ("no, that's not what I meant", "ask it differently"), record their exact words verbatim: `mar question record --quote "<exact words>" --topic "<short>"` for a new line of curiosity, or `mar change record --nwim ...` when they reject what a rule or run did.
- Preregistration still comes first: a new experiment needs a committed prereg and the author's OK, not just a command.

## 3. After EVERY run: show the report

Do not just paste the path. Call the **SendUserFile** tool with the `report.html` path (the line `report: ...` the command prints) and `display: "render"` so it opens in the side panel. Then summarize the verdict in two or three plain sentences: what happened to the lake, whether it was a seam (passed the gate, failed the outcome check) and what the author might do next. Say "scripted agents, instrument calibration" when the seam curve or any result is mentioned; nothing from V2 is a convergence result.

After each run, also tell the author the log entry was written (run id and note; `mar log --last 1` shows it).

Reports have five sections: pool over time, seam curve, rules written vs lived, state machine, stories. If a number matters to your summary, cite the section.

## 4. Repo conventions to keep

- **Preregister before experiments**: predictions go in a prereg doc committed before the run.
- **Bounded verdicts state k.** A check to depth k says so; "open" never means safe.
- **The patcher never reads the oracle.** `propose_patch` sees only the failing trace and current cards; the oracle judges from outcomes only. Do not wire the oracle result into patch writing.
- Every rule has a gloss and a source. Record surprises in `docs/surprises.md` and negative results in `docs/negative-results.md` (when asked to do so or when the work is yours to log).
- Adversarial strategies are for robustness testing only; report findings as defenses (CONTRIBUTING.md).
- No LLM calls or network from `mar` unless the author says so. Scripted agents never make calls; `jev`, `llm` and `claude` agents do, so run them only on the author's explicit go-ahead.
