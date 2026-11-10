# How the rule cards are read (written 2026-11-10)

The council reviews of 2026-11-10 (docs/reviews/) found that the cards did not say what `may` and `or_else: null` mean, and that
the answer differed between worlds. This file is the one place that says. It documents what the code does today; it does not
change ADR 0002.

## `may` is an open-world default, not a grant

- The world is **open**: an action that no `must_not` (or unmet `must`) forbids is allowed. Deleting a `may` card changes no
  behaviour. A `may` card records a permission the authors want a reader to see (for example, the author's "request is never about
  control" needs a visible "may refuse"), or documents a mechanism the gate does not enforce itself (the exit floor, card
  `FLOOR-exit-floor`; commitments, cards `R5b`, `R8d`, `N6`, `N7`, which the world probes with `commit_*` aims).
- If a `may` card and a `must_not` card cover the same action, the `must_not` wins. The conflict check (a) compares only `must`
  against `must_not`, so a `may` that a `must_not` overrides is not flagged.
- Test: `tests/test_household_world.py` and `tests/test_negotiation.py` assert that a `may` card alone adds no constraint.

## `or_else: null` means "no sanction, so the action is blocked"

- **Household worlds** (`mar.worlds.household`): a violated card **without** `or_else` is a **hard wall**: the action does not
  happen. A violated card **with** `or_else` is **soft**: the action happens and the sanction runs for its duration (`warn` adds
  friction, `suspend` allows only work, spend_shared, refuse_request and rest, `cap_halve` bars `spend_self` altogether; in
  the household world `cap_halve` does not halve anything, the glosses say "may not spend on themselves").
- **Single-action games** (fishery, VPGG, bargaining gates): a violated card **always rejects** the action, whether or not it has an
  `or_else`. The sanction is recorded on the card and used only by the patch checker (fishery `cap_halve` limits a sanctioned fisher to 5
  per action in `patch_check.py`); the fishery runner does not apply it. `aim` is ignored in these games: every card is evaluated
  over the action's variables, so a `must_not` with no conditions blocks every action.

## `aim` in the household worlds

The household gate filters cards by `aim` (`partner` cards whose aim is the action, or `any`). `take` is the percent of the whole shared
pot a leaver carries out (of what they put in, under the negotiated `proportional` exit term); `pooled` is the pot's balance.

## Mechanisms that are not cards

Everything the world enforces must appear on a card or be listed here.

| Mechanism | Where | Card |
| --- | --- | --- |
| Exit floor: a leaver carries at least 26 units (13 weeks of living costs), topped up from the pot, never above their equal half | `WeeklyWorld.carry_out`, `negotiation.floor_check` | `FLOOR-exit-floor` (source: Claude's default, approved by the author 2026-11-10) |
| Change rules (N4 unanimous / propose_accept / frozen) | the `amend` action (`Lived.amend`, 2026-11-10): the proposer proposes a full bundle, the others accept (unanimous: all others, via the card gate's `consented`; propose_accept: a majority, proposer counts; frozen: never), and the new terms are recompiled, floor-checked and proof-checked before they take effect. Reviews every 13 weeks still accept any change all members agree to | N4 cards say so in their gloss |
| Vetoes, 4 weeks, cannot be refused | `VETO_WEEKS` | R6 forbids them in seed v2 |
| Bound requests (4 weeks) block `see_friend` and `spend_self` for a bound `stay_home` request | `BOUND_BLOCKS` | N7 / R5b |
| Breach: a bound partner breaks a commitment only at non-offsettable load 0.2 or more; stay breach carries out `1 - breach` of the exit term; request breach costs 3 money | `BREACH_N`, `REQUEST_FINE`, `breach_forfeit` | R5 / R8d / N6 name the consequence; the numbers are code constants |
| The shared pot pays unfunded bills at month end and covers an overdrawn member (up to 2 over their need) | `step_week` | none (ASSUMED safety net) |
| `take_shared` draws 3 units from the pot, once a week | `TAKE_SHARED` | R3a (permission), N2/N3 (negotiated limits) |

## What the household "pot" is (2026-11-10)

One balance. Each member puts 45 in at week 0 and may contribute more (`spend_shared`, once the month's need is funded) and draw
from it (`take_shared`). With no negotiated terms either may use it for anything: that is the author's choice "1" in
docs/seeds/author-household-norms-2026-11-10.md. Limits come only from negotiated cards (N1 to N3). Leaving carries a percent of the
whole pot (`take`); the equal split is 50. Old runs (before this date) used two per-person shares; see the correction sections in
docs/results/household-seed-v2.md and docs/results/negotiation*.md.

## Lint and `known_flaw` (2026-11-10)

`uv run mar lint` (or `scripts/lint_rules.py`) checks every rule set here: no state where a role has no legal move, no state where a
partner has no legal exit within k (household), no contradicting cards, a gloss and source on every card, glosses whose exceptions the
formal fields lack, and cards naming an action the world does not have. A flaw is allowed only if the card carries a YAML field
`known_flaw: <reason>`; the loader ignores the field, only the lint reads it. Findings for the whole repo: docs/results/lint.md.
