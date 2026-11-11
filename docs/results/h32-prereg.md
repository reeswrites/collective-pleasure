# H32 preregistration: do the egoist and the utilitarian converge under free exit and amplification? (ADR 0015 template)

Status: written and committed before the first run of the default model or any grid. Nothing here is a result. Agents: none; exact dynamic programming over a small model. Model API calls: none. Cost $0.

Wording rule: agents feel nothing. "Pleasure" is a gloss for a modeled hedonic state (ADR 0010). Every number is ASSUMED. Findings are about this model, not people.

## Purpose and claim

H32 (experiments/hypotheses.jsonl): under free exit and shared-experience amplification, an agent that maximizes only its own lifetime pleasure (the egoist) chooses nearly the same policy as one that maximizes the pair's total (the utilitarian). The partner's pleasure keeps the partner staying, and shared activities need both people to enjoy them. Remove free exit or amplification and the two policies diverge.

It comes from the author's essay thesis: egoistic hedonists and hedonistic utilitarians alike must attend to others' pleasure, and a life of only solitary pleasures is valid but not optimal. It also bears on the founding question: can a mechanism, rather than training, make a self-interested agent attend to another's welfare?

What would change a decision: if the convergence holds only in a narrow parameter band, or only because the partner's exit rule reads the partner's own pleasure, then "free exit makes egoists care" is not a design principle we can lean on for the household rules.

## Design

Code: `src/mar/convergence.py` (written before this prereg and smoke-tested only on a toy menu; see the pilot section). Script: `scripts/h32_run.py` (written after this commit).

- **Two agents.** The actor picks each week's activity from a menu of five and whether to do it solo or shared. The partner has one move: stay or leave.
- **Menu (likings for actor, partner; ASSUMED):** actor's passion (1.0, 0.1), actor's second (0.9, 0.2), common ground A (0.6, 0.8), common ground B (0.7, 0.7), partner's passion (0.1, 1.0). In a week the actor goes solo while they are together the partner gets 0.1. Repeating last week's activity halves both likings (satiety 0.5). Each member pays a bond upkeep of 0.05 per week together.
- **Objectives.** Egoist: the actor's own lifetime pleasure (its own experiences, plus vicarious pleasure when giving is on). Utilitarian: the egoist's objective plus the partner's lifetime pleasure. Sum over T weeks, no discount.
- **Switches (each on or off, 2 x 2 x 2 = 8 arms, each solved for both objectives = 16 solves per parameter point):**
  - *Free exit.* After each week the partner updates an estimate e of its weekly pleasure in the pair: e = round to 0.05 of (0.5 e + 0.5 target), target = w x (its pleasure that week) + (1 - w) x 0.5. It leaves if e < o_B, its outside option per week. Start e = 0.5. Leaving is permanent; then the actor does solo activities and the partner gets o_B each week. Off: the partner never leaves.
  - *Amplification.* A shared activity's pleasure is multiplied, for both, by M = 1 + alpha x min(lA, lB) x (1 - |lA - lB|). M is large only when both like the activity and their tastes for it overlap. Off: M = 1, so sharing gives the actor exactly what doing it alone gives.
  - *Giving pleasure.* The actor's own pleasure includes g x the partner's pleasure while they are together.
- **Ties.** The egoist breaks ties in its own objective toward the partner's pleasure ("kind tie-break", primary). This makes the control gap as small as any egoist can make it. A "blind" tie-break (against the partner) is reported as a sensitivity. Remaining ties go to the lowest action index.
- **Defaults (ASSUMED):** T = 52 weeks, alpha = 1.0 (the horizon study's amplification strength), o_B = 0.25, g = 0.5, w = 1 (partner fully sees its own pleasure), exit noise eps = 0.
- **Sweeps.** alpha in {0, 0.5, 1, 1.5, 2, 3} x o_B in {0.1, 0.25, 0.4, 0.6, 0.8} (30 cells, g = 0.5, T = 52). g in {0, 0.25, 0.5, 0.75, 1}. T in {13, 26, 52, 104}. Rigging check: w in {1, 0.75, 0.5, 0.25, 0} x eps in {0, 0.05, 0.1, 0.2}, over the 30-cell grid.
- **Solitary baseline.** A persona that never bonds: solo activities only, no upkeep, no partner. Its lifetime pleasure is compared with the egoist actor's lifetime pleasure in each paired arm.

### Measures (exact rationals from a forward pass over the optimal policies)

- **D, policy distance:** total variation distance between the egoist's and the utilitarian's expected action-occupancy distributions over T weeks (labels: activity x solo, shared or apart). 0 = the same mix of weeks, 1 = disjoint.
- **Disagreement:** the share of weeks, along the egoist's path, where the utilitarian would act differently in that state. Reported.
- **R, the pleasure gap:** 1 - total(egoist policy) / total(utilitarian policy), where total = actor + partner. R >= 0 by optimality.
- **Q, the partner's share:** partner's lifetime pleasure under the egoist policy / under the utilitarian policy.
- **Converged** at a point: D <= 0.2 and R <= 0.05.
- **H32 pattern** at a point (giving off): the exit+amp arm converges, and neither the amp-only arm nor the exit-only arm does.
- **Decomposition:** exact Shapley values over the three switches of the game v(S) = gap(all off) - gap(S), for R and for D.

- **Unit of resampling: none.** The model is deterministic and has no seeds. Every prediction is a deterministic check of a computed number, reported as pass or fail (ADR 0015 point 4). The grid is the sample of conditions and is fixed above.

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

Disclosure of everything run before this commit. I solved only a toy fixture: a two-activity menu, x = (1.0, 0.0) and y = (0.5, 1.0), at T = 4, 6 and 104, all 8 arms, to check that the code runs, that the float solver agrees with the exact-rational solver on every arm (it did, at T = 6 with w = 0.5 and eps = 0.1), and the runtime (under 1 second per solve at T = 104). On that toy, the all-off arm had D = 0 (the toy's egoist and utilitarian coincide; it is not a control), and the exit-only arm had D = 0.5 and R = 0.27. Nothing on the default menu or the grid was solved. The default menu and parameters were chosen by hand reasoning so that the all-off control should show a large gap; the predictions below come from hand calculation on the model as specified, not from any run.

| Quantity | Pilot value | Spread | Source |
|---|---|---|---|
| float vs exact agreement, toy, 8 arms | all equal | none (deterministic) | scratch smoke script, not kept |
| solve time, toy, T = 104 | under 1 s | none | scratch smoke script, not kept |

## Power check

Not applicable: no sampling, so no power. Every claim is a deterministic computation.

## Predictions

Defaults unless stated. "Hand value" is my calculation before any run. Thresholds are numbers.

| ID | Quantity | Comparison and threshold | Test |
|---|---|---|---|
| P1 (control) | all-off arm: R, D, Q | R >= 0.15 AND D >= 0.8 AND Q <= 0.4 (hand: 0.23, 1.0, 0.14). If this fails the setup is broken and the study stops | deterministic |
| P2 | D in each of the 8 arms | each within 0.05 of the hand value: all off 1, exit 1, amp 0.5, give 0.5, exit+amp 0.5, exit+give 0.5, amp+give 0, all three 0 | deterministic |
| P3 | H32 as stated, at the defaults | the H32 pattern does NOT hold at the defaults (hand: exit does not bind at o_B = 0.25 and alpha = 1, so exit+amp equals amp-only) | deterministic |
| P4 | H32 pattern over the 30-cell alpha x o_B grid | holds in at least 1 and at most 4 cells, all at alpha = 1 and o_B >= 0.6. Amp-only converges in every cell with alpha >= 1.5 (so removing exit does not diverge there) | deterministic |
| P5 | Shapley split of the R gap at the defaults | give > amp > exit, and exit's share below 0.3 of the all-off R | deterministic |
| P6 | Shapley split of the D gap, averaged over the 30 cells | amp's mean share is the largest of the three; exit's is the smallest | deterministic |
| P7 | exit-only arm at the defaults | the egoist's partner leaves (together at end = 0), R falls below 0.12 from the all-off R, and D stays >= 0.8: exit closes the pleasure gap by ending the bond, not by changing the egoist's policy | deterministic |
| P8 | give-only arm, g sweep at alpha = 1, o_B = 0.25 | converged at g in {0.75, 1}, not converged at g in {0, 0.25, 0.5} | deterministic |
| P9 | horizon, the exit+amp arm at alpha = 1, o_B = 0.8 | converged at T = 52 and T = 104, and D at T = 13 is larger than D at T = 104 (end-game: the egoist stops caring in the last weeks) | deterministic |
| P10 (rigging) | number of cells where exit+amp converges and amp-only does not, with the utilitarian keeping the pair together to the end with probability >= 0.5 | at w = 1, eps = 0: >= 1. At w = 0: exactly 0 for every eps. Nonincreasing as w falls (1, 0.75, 0.5, 0.25, 0) at eps = 0. At eps = 0.2 no larger than at eps = 0 (w = 1) | deterministic |
| P11 (solitary) | egoist actor's lifetime pleasure in each arm vs the solitary persona's | solitary higher in the all-off and exit-only arms; paired higher by at least 5% in all four amp-on arms; paired higher (any margin) in give-only (hand: solitary 49.4; all off 46.8; exit 49.3; amp 54.6; give 50.7; amp+give 81.0) | deterministic |
| Identity | tests | in every arm and for every policy evaluated, utilitarian value = egoist value + partner term; with all switches off, the egoist's optimal own value does not change when the partner's likings change | unit test, pass or fail |

## Verdict rule

H32 is supported as stated iff P4 shows the H32 pattern in a majority of the grid (16 or more of 30 cells). My prediction (P3, P4) is that it is not: convergence will come mostly from amplification alone at high alpha, and from giving, with exit doing work only in a narrow band. "Rigged" is judged by P10: if the exit-driven convergence cells vanish once the partner is half blind (w = 0.5), the exit mechanism's contribution is called fragile.

## Not testable by design

Everything here is deterministic. The identity check and the float-versus-exact agreement are instrument checks.

## Limits stated now

- One small menu, chosen by hand. The menu decides which activities are "common ground"; another menu could move every threshold.
- The partner is a fixed rule, not an optimizer. It does not bargain, threaten or learn the actor's policy. Leaving is permanent; no reunion.
- The actor chooses every week's activity. The partner's only say is exit. This is the extreme of asymmetric power within the pair.
- "Total" counts the actor's vicarious pleasure as pleasure, so with giving on the utilitarian counts the partner's pleasure twice (once as the partner's, once as the actor's vicarious share). Stated now; it slightly favors partner-friendly policies in the utilitarian's objective.
- Upkeep 0.05 makes pairing cost something. Without it, a paired actor could never do worse than solitary (it can always go solo), so P11's all-off clause depends on it.
- No discount, one horizon at a time, no memory or anticipation terms (ADR 0017 levers off).

## Amendments

None yet.
