# Loss report for the run-1 elites (step 1 of the author's "all three" fixes)

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Status: reporting only; no score changes. Code `src/mar/loss_report.py` (`loss_report`, `render`), printed by `uv run python scripts/household_evolve_run.py --report` for every elite (the evaluator's output), test `tests/test_evolve_household.py::test_loss_report_lists_powers_mechanics_and_backwards_cards`. Context: the author said run 1's dropping of the seed's `may` cards and commitment mechanics was "not what I meant" (loop-b correction in experiments/changes.jsonl).

For each elite the report lists: powers lost (a `may` card of the seed on an aim that the elite has no `may` card for), mechanics switched off (the world enables `commit_stay`, `commit_request` and `give` only when a card names them), cards removed, cards changed, cards added, and a WARNING for a card whose deontic differs from the hand-written card of the same id (the `flip` operator).

## Powers lost, against `author_seed_v2_bindable`, over the 16 run-1 elites

| power (aim) | elites that lost it |
|---|---|
| bind a request (commit_request) | 16 of 16 |
| bind a stay (commit_stay) | 16 of 16 |
| give or trade, a gift or transfer (give) | 16 of 16 |
| refuse a request not bound to (refuse_request) | 16 of 16 |
| ask for anything (request) | 16 of 16 |
| keep and spend own money (spend_self) | 16 of 16 |
| put money in the shared pot (spend_shared) | 15 of 16 |
| draw from the shared pot (take_shared) | 15 of 16 |
| leave whenever one likes (leave) | 14 of 16 |
| see anyone freely (see_friend) | 9 of 16 (7 keep an explicit may-see, B4) |

"Lost" means no card grants the power explicitly. Where the elite has no card about the action at all, the gate still permits it, so for keep, ask, refuse, see and leave the loss is a loss of the written permission, not of the ability. For the three mechanics (bind a stay, bind a request, gift) it is a real loss: with no card naming them the world switches them off.

## Cards added

W1-no-veto 13, E1-at-most-half 13, D1-needs-first 11, E2-at-least-half 8, B4-may-see 7, W2-no-request 6, W3-no-take 4, the equal-split exit pair 2, N1-contribution-fixed 2, S5-may-share 1, S2-may-leave 1, N5a-exit-proportional 1.

## Warnings: cards that read backwards

- Lines 3 and 7: **D1-needs-first** went must_not -> must. The hand-written card said "a partner may not spend on themselves while this month's shared need is unfunded"; the elite's says "must spend self only when the unfunded need is more than 0", which the gate reads as a violation to spend on yourself when the need is funded. It is close to the opposite rule.
- Line 4: **E2-at-least-half** went must_not -> may. The hand-written card said a leaver must take at least half; the elite's says a partner may leave when the pot exceeds 10 and the take is under 50. A requirement became a permission with different conditions.

Full per-elite lists (cards removed with their glosses, changed, added, warnings) are the `--report` output; the plain-English card lists are in docs/results/household-evolve.md.
