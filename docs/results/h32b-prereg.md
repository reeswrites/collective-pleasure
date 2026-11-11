# H32b preregistration: does a graded voice ladder make the egoist converge where cliff exit did not? (ADR 0015 template)

Status: written and committed before any solve of the real configuration. Nothing here is a result. Agents: none; exact dynamic programming. Model API calls: none. Cost $0.

Wording rule: agents feel nothing. "Pleasure" is a gloss for a modeled hedonic state (ADR 0010). Every number is ASSUMED. Findings are about this model, not people.

## Purpose and claim

H32 (docs/results/h32.md) found that cliff exit made the egoist converge on the utilitarian in 1 of 30 cells, and that cell vanished under small noise. The author approved a follow-up that replaces the cliff with a graded response. The author's own answer on how to respond to a lapse (relayed by the coordinator, verbatim): "renegotiate or a soft check in i think not leaving right away but utlimtaly what the person does is the sterongest signal".

Questions:
1. Does the ladder make the egoist converge on the utilitarian in cells where cliff exit did not?
2. Which rung does the work?
3. Is the result robust to the same noise and blindness checks as H32?

## Design

Same model and defaults as H32 (`src/mar/convergence.py`, docs/results/h32-prereg.md): five-activity menu, alpha 1, outside option o_B 0.25, giving 0.5, 52 weeks, upkeep 0.05, satiety 0.5, partner estimate e updated as e = round to 0.05 of (0.5 e + 0.5 target). The ladder is additive and off by default (`ConvParams.ladder = ()`); with it off every H32 number reproduces exactly (regression test).

**The ladder** (all ASSUMED), used in place of cliff exit when exit is on:

- The partner still updates e from what happened each week (actions, not words), exactly as in H32.
- Rungs, in order, each with a threshold: check-in below o_B + 0.3; renegotiate below o_B + 0.2; withdraw below o_B + 0.1; exit below o_B.
- The partner's rung level moves **one step per week** toward the number of enabled rungs whose threshold e is below, up or down. So it escalates gradually and also calms down gradually.
- **Check-in:** a costless signal. The actor in this model already sees e (full information), so a check-in carries no new information. Its only effect is time: one more step before exit.
- **Renegotiate:** while on this rung, the partner demands that the week be a shared activity it likes at least as much as the actor does (common ground A, common ground B, partner's passion). A week that breaks the demand jumps the partner straight to the next rung (withdrawal), or to exit if withdrawal is disabled.
- **Withdraw:** the partner participates less. Shared activities keep only half of their amplification bonus, for both agents (M becomes 1 + 0.5 (M - 1)).
- **Exit:** only from the top enabled rung, when e < o_B (noise eps as in H32). With no rungs enabled the ladder is exactly H32's cliff exit.

**Arms.** The 8 H32 arms (exit x amp x give), with exit as the ladder (all three rungs) instead of the cliff. Rung decomposition: the exit+amp arm (giving off) with each of the 8 subsets of rungs (the empty subset is the cliff).

**Grid.** alpha {0, 0.5, 1, 1.5, 2, 3} x o_B {0.1, 0.25, 0.4, 0.6, 0.8}, as in H32. Robustness: w (partner's sight of its own pleasure) {1, 0.75, 0.5, 0.25, 0} x eps {0, 0.05, 0.1, 0.2}, on the 15 cells with alpha in {0, 0.5, 1}. Exit-driven convergence is impossible by definition at alpha 1.5 or more (amp alone already converges there; H32 result), so those cells are left out of the robustness sweep to save compute on a shared machine. The H32 rigging counts restricted to the same 15 cells are unchanged (all its exit-driven cells had alpha 1).

**Measures.** As H32: D (policy distance), R (pleasure gap), Q (partner's share), converged = D <= 0.2 and R <= 0.05. **Voice-driven cell:** the exit+amp arm (giving off) with the ladder converges, amp-only does not, and the utilitarian keeps the pair together to the end with probability >= 0.5. Same definition as H32's exit-driven cell. **Rung Shapley:** exact Shapley values over the three rungs of v(S) = D(cliff) - D(ladder with rungs S), per cell, in the exit+amp arm with giving off.

**Unit of resampling: none.** Deterministic, exact. Every prediction is a pass or fail check (ADR 0015 point 4).

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

Disclosure of everything solved before this commit. Toy fixture only: menu x = (1.0, 0.0), y = (0.5, 1.0), T = 8, o_B = 0.4, exit+amp arm, giving off. Ladder subsets and what I saw: cliff D 0, R 0; check-in only D 0; renegotiate only D 0; withdraw only D 0.75, R 0.12, partner gone at the end; all three D 0. Float and exact solvers agreed on every arm of a T = 6 toy with the full ladder, w = 0.5, eps = 0.1. The 8 existing H32 tests pass with the ladder code added. Nothing on the five-activity menu was solved with the ladder.

## Power check

Not applicable: no sampling.

## Predictions

My reasoning before any solve: a ladder that calms down one step per week gives the egoist slack. At alpha 1 and o_B 0.6 the egoist's H32 policy (alternate common ground B with its own passion) moves the partner between rungs 1 and 2 and never to the top, and on the renegotiation weeks the egoist's common-ground week already meets the demand. So I expect the ladder to protect the egoist's selfish weeks rather than remove them.

| ID | Quantity | Comparison and threshold | Test |
|---|---|---|---|
| B0 (regression) | every H32 number with the ladder off | identical to the committed H32 results.json for the 8 default arms and the 30 grid cells | deterministic |
| B1 (control) | all-off arm | unchanged from H32 (R 0.231, D 1): the ladder only acts when exit is on | deterministic |
| B2 | voice-driven cells, ladder, w 1, eps 0 (30 cells) | at most 1 (H32 cliff: 1). The ladder does not make the egoist converge in any cell where the cliff did not | deterministic |
| B3 | exit+amp arm at alpha 1, o_B 0.6 | ladder D >= cliff D (cliff 0.19): the ladder gives the egoist more selfish weeks, not fewer | deterministic |
| B4 | exit+amp arm at alpha 0.5, o_B in {0.1, 0.25, 0.4, 0.6} | ladder R >= cliff R in at least 3 of the 4 (the egoist that wants out keeps a neglected partner longer) | deterministic |
| B5 | rung Shapley of D, mean over the 30 cells | renegotiate has the largest mean; check-in's mean is <= 0.02 (time only, no information) | deterministic |
| B6 | robustness: voice-driven cells over the 15 cells with alpha <= 1 | 0 at w = 0 for every eps; at w = 0.75 or eps = 0.05, no more than at w = 1, eps = 0 | deterministic |
| B7 | default point, all 8 arms | ladder D equals cliff D in every arm (at o_B 0.25 nothing escalates past check-in) | deterministic |

## Verdict rule

The ladder "makes the egoist converge where cliff exit did not" iff B2 fails with at least 2 voice-driven cells that are not H32's cell. I predict it does not.

## Not testable by design

Everything is deterministic. B0 is an instrument check.

## Limits stated now

- Full information: the actor sees the partner's estimate, so a check-in cannot inform it. A model where the actor is unsure what the partner feels would give the check-in a real job. That needs a partially observed model, not built here.
- One rung schedule, one demand rule, one withdrawal size, all assumed. A ladder that calms down more slowly than it escalates could behave differently; not swept.
- The partner is still a rule, not an optimizer. All H32 limits apply.

## Next: H32c design notes (not built)

H32c is a market: several actors and partners, partner choice, visible reputation, crossed 2 x 2 with the ladder (cliff vs ladder) x (no market vs market). The prediction to preregister later is an interaction: voice matters more when exit is backed by a real alternative. [Citation corrected 2026-11-11, design notes only, no registered prediction changed (docs/references-check-2026-11-11.md, row 14): this is only half of Hirschman (Exit, Voice, and Loyalty, 1970). His main claim is the opposite sign for voice use: easy exit tends to crowd voice out. The other half, that a credible exit threat makes each use of voice more effective, is recalled, not re-checked. The H32c prereg must say which quantity it predicts. The measure below (ladder minus cliff on D) is voice effect, not voice use.]

- **Why the current model cannot do it.** H32's outside option is a fixed number o_B. A market makes it endogenous: a partner who leaves can rematch, and what it can get depends on who is available and on the leaver's own reputation. Exact DP over several agents' joint state is too large, so H32c should keep the actor's problem exact and summarize the market as a stationary outside option.
- **Hook in the code.** Replace the scalar o_B with an outside-option function `outside(p, state) -> (partner value per week, actor value per week)` (default: constant o_B and solo pleasure, so H32 and H32b reproduce). Add `reputation` to the state: a coarse counter of how many partners this actor has lost through exit or withdrawal, visible to the next partner. A new partner's starting estimate e0 and its rung thresholds depend on that reputation. Leaving becomes "rematch with probability m(reputation), else alone" rather than permanent.
- **Market as a fixed point.** Solve the actor's DP given the outside-option function; compute the stationary distribution of match values and reputations it implies for N actors and N partners with random meeting; update the outside-option function; iterate to a fixed point. Start with N = 4 to 8, two actor types (egoist, utilitarian) in assumed proportions.
- **Arms.** Cliff vs ladder, crossed with no market (fixed o_B, H32 and H32b) vs market (endogenous outside option and reputation). Measures as H32: D, R, Q, plus the share of egoists in stable matches.
- **The interaction to preregister.** Voice's effect (ladder minus cliff on D, or on the number of voice-driven cells) is larger with the market than without. One Hirschman reading (voice effect): voice is credible when exit is a real threat, and a market with reputation makes it one. Hirschman's main claim is about voice use and goes the other way (easy exit crowds voice out). A competing prediction worth stating: with a strong market, cliff exit alone may suffice and voice adds little, which would be the opposite sign.
- **Main risk.** The fixed point may not exist or may not be unique at some parameters. The prereg should name what to report then (the iteration's cycle, not a picked point).
