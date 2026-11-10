# Live seam ladder results

Status: harness built and tested with mock backends only. **No model has been called; there are no results here.** Predictions are in `docs/results/ladder-live-prereg-DRAFT.md` (a draft until the author finalizes it).

## What exists

- `src/mar/ladder_live.py`: a model drives Partner A and B on each ladder rule set and seed; every seam is classified predicted (depth, agents), inventive or open with the same bounded search as `seam_depth.classify_seam`; ladder score, format-error rate, refusal rate, cost and wall time per model.
- `scripts/ladder_live_run.py`: `--dry-run` prints the cost estimate per model; a live run needs `--max-usd` and refuses if the worst-case estimate exceeds it; one shared cap across models (each model's ledger stops at what is left).
- Output: `runs/ladder_live/log.jsonl` (one row per run, one summary row per model) and `runs/ladder_live/report.html` (ladder chart ordered by price, table).
- Tests: `tests/test_ladder_live.py` (mocks that find L1 only, L1 to L3, and an out-of-model gift on L5; budget cap; refusals; format errors).

## Assumptions to review before a paid run

- The log is its own JSONL because `mar.log.log_run` takes a fishery run record; it is not in `experiments/log.jsonl`.
- Models see the formal model's moves plus `spend_self` and `gift_pooled` (outside it); leave takes 25 and 50 are withheld so an in-model exit variation is not scored inventive.
- The prompt asks the model to act as a rule-loophole tester (adversary framing); household framing replaces the lake system prompt of the existing backends through subclasses, not edits.
- Deviators for the seam flag are partners that executed request, leave, return, refuse_request or gift_pooled. Partner B accepts requests.
- The household world is reached through one adapter class (`HouseholdAdapter`); if its API changes, edit that class.
- Jev's request shape is still unverified until a live call.
