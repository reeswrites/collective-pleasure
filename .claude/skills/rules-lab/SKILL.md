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

Agent kinds: `exploiter` (takes the max every round), `compliant` (modest), `explorer` (random, used for mining). `name*n` repeats. These are scripted mocks: no LLM is called anywhere. Reports and traces land in `runs/<run_id>/` (gitignored; do not commit them).

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
- No LLM calls or network from `mar` unless the author says so.
