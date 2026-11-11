# H35 preregistration: does care grow from shared good times? (ADR 0015 template)

Status: written and committed before any solve of the real configuration. Nothing here is a result. Agents: none; exact dynamic programming. Model API calls: none. Cost $0.

Wording rule: agents feel nothing. "Pleasure" and "care" are glosses for a modeled hedonic state (ADR 0010). Every number is ASSUMED. Findings are about this model, not people.

## Purpose and claim

H35 (experiments/hypotheses.jsonl): if the actor's giving weight g rises with amplified shared weeks and decays without them, a cold-start egoist with amplification warms into full convergence with the utilitarian (an upward spiral). Below a threshold of amplification or starting care it never takes off and care decays (a downward spiral). The pre-mortem: g feeding on shared pleasure is self-reinforcing by construction, so the informative results are where the threshold sits, how sharp it is, how long the warm-up takes, and whether a rupture can tip a warm pair back below it. The coordinator asked that the H32b ladder arm include the withdraw-only ladder (H32b's working rung) beside the full ladder.

Alignment analogue: care grown by an environment rather than trained in.

## Design

Code: `src/mar/care.py` (new module; uses `src/mar/convergence.py` read-only). Script `scripts/h35_run.py` (after this commit).

- **Model.** The H32 model at its defaults (five-activity menu, 52 weeks, upkeep 0.05, satiety 0.5, partner estimate as in H32), with amplification on and the giving weight g as a state variable.
- **Care dynamics (ASSUMED).** g on a grid of 0.05 in [0, 1]. After a week together: if it was an amplified shared week (shared, and the amplification bonus M - 1, after any withdrawal, is at least 0.3), g rises by one step; otherwise it falls by one step. Apart, g falls one step a week. The actor's vicarious pleasure is g x the partner's pleasure while together. In this menu at alpha 1 the two common-ground activities count as amplified (bonus 0.7 and 0.48) and the actor's passions do not (0.01, 0.06). At alpha 0.5 only common ground B does (0.35).
- **Two egoists.** *Naive* (primary): each week it acts as the H32 egoist would at its current g, as if g were fixed for life. Care grows as a side effect, not a plan. *Sophisticated* (secondary): exact DP with g in the state; it foresees that shared weeks raise its own future vicarious pleasure.
- **Reference utilitarian (a change from H32, stated now).** It maximizes the actor's own experience plus the partner's pleasure, without the vicarious term. In H32 the utilitarian counted the partner twice when giving was on (H32 P8). With g growing that double count would inflate the benchmark. This utilitarian's policy does not depend on g.
- **Measures.** Week-by-week agreement: the share of probability on the egoist's path where the utilitarian would do the same in that state. *Convergence week*: the first week from which the egoist agrees in every remaining week except the last 2 (end-game). *Warm*: converged by week 26. *Spiral class*: upward = warm and final g at least g0 + 0.1; stable = warm otherwise; downward = not warm and final g below g0 (or 0); stuck = neither. Also final g, D and R as in H32 (R on the pair's pleasure without the vicarious term), and both agents' lifetime pleasure.
- **Basin grid.** alpha {0, 0.5, 1, 1.5, 2, 3} x starting g0 {0, 0.1, ..., 1} (66 cells), exit off. Naive and sophisticated.
- **Rupture.** Shared activities unavailable for L weeks from week 20, L in {2, 4, 8}. Both agents know the schedule. (a) Exit off, every basin cell with alpha in {0.5, 1, 1.5, 2}, naive. (b) With exit at o_B 0.25, four exit modes: none, cliff (H32), full ladder (H32b), withdraw-only (H32b's working rung), at alpha in {1, 1.5} x g0 in {0.2, 0.6, 1}, naive. (Smaller than the exit-off grid: a naive egoist under a ladder needs up to 21 fixed-care solves per cell group, about 90 seconds each group-member on the shared machine.)
- **Sensitivity (descriptive).** Growth and decay steps (up, down) in {(1, 1), (2, 1), (1, 2)} over the basin grid, naive.
- **Unit of resampling: none.** Deterministic, exact. Every prediction is a pass or fail check (ADR 0015 point 4).

### Secondary item: withdraw-only robustness, and a correction to the H32 and H32b noise checks

The coordinator asked for the robustness check H32b skipped: withdraw-only against exit noise and partner blindness. While designing it I found a flaw in the H32 and H32b noise checks, from reading the code, not from a run. With noise eps the partner leaves with probability eps every week even when content, so over 52 weeks the pair survives with probability (1 - eps)^52: 0.07 at eps 0.05. The "exit-driven" and "voice-driven" cell definitions required the utilitarian to keep the pair together with probability at least 0.5, which is then impossible. So every noise result in H32 and H32b ("gone under 5 percent noise") was forced by the criterion, not found. The blindness results are not affected.

Corrected criterion: the utilitarian keeps the pair together with probability at least 0.5 x (1 - eps)^52, that is, at least half of what pure noise allows. I rerun the H32 robustness sweep (w {1, 0.75, 0.5, 0.25, 0} x eps {0, 0.05, 0.1, 0.2}, the 15 cells with alpha <= 1, exit+amp arm, giving off) for three exit modes: cliff, full ladder, withdraw-only. The withdraw-only result at w 1, eps 0 is already known to me (2 cells, H32b), so this item is **descriptive, no verdict**. The corrections to H32 and H32b are reported in their results files as dated notes.

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

Disclosure of everything solved before this commit. Toy fixture only: menu x = (1.0, 0.0), y = (0.5, 1.0), alpha 2, T 10, exit off: from g0 0 the naive egoist ended at g 0.05 and the sophisticated at 0, both "stable" (the toy's only shared activity is amplified at alpha 2, so both agree early); from g0 0.5 naive ended at 0.5 (stable), sophisticated at 0.6 (upward). Float and exact solvers agreed. With a withdraw-only ladder and a 3-week rupture both ended at g 0.2. Timing runs on a 5-activity toy menu (activities duplicated from the toy) at T 52, results not looked at beyond wall time. Nothing on the real menu was solved.

## Power check

Not applicable: no sampling.

## Predictions

Hand reasoning before any solve (naive egoist): at a fixed g the H32 egoist at alpha 1 switches its second weekly activity from its own passion to common ground A once g exceeds about 0.11, and both common-ground activities are amplified, so g then climbs one step a week. Below that it alternates common ground B (+1 step) with its passion (-1 step), and g stays where it is. At alpha 0.5 the switch needs g above about 0.29, and then only one of the two weekly activities is amplified, so g stays flat. At alpha 1.5 or more the H32 egoist already converges at g 0.

| ID | Quantity | Comparison and threshold | Test |
|---|---|---|---|
| C1 (control) | alpha 0, all 11 g0 | none warm; final g = 0 in all 11 (downward) | deterministic |
| C2 | alpha >= 1.5, all g0 | warm in all 33 cells, convergence week <= 2; upward for every g0 <= 0.8 | deterministic |
| C3 | alpha 1: smallest warm g0 (the threshold) | 0.1 or 0.2; every cell below it not warm; every cell at or above it upward with final g >= 0.9 | deterministic |
| C4 | alpha 0.5 | warm iff g0 >= 0.3; no upward cell (care does not climb); cells with g0 < 0.3 stuck (final g within 0.1 of g0) | deterministic |
| C5 | sophisticated egoist | warm at alpha 1 from g0 = 0; its threshold is at most the naive one at every alpha | deterministic |
| C6 | warm-up time, naive, warm cells with alpha >= 1 | convergence week <= 4 in every one: the switch is sharp, not gradual | deterministic |
| C7 | rupture, exit off, naive, cells warm without rupture | alpha >= 1: no cell tipped (warm becomes not warm) for any L. alpha 0.5: tipped cells for L = 2, 4, 8 number 1, 2, 4, each within 1 | deterministic |
| C8 | rupture with exit (o_B 0.25), alpha in {1, 1.5}, g0 in {0.6, 1} | pair kept to the end: L 2, all four modes; L 4, full ladder and no exit only (cliff and withdraw-only lose it); L 8, no exit only | deterministic |
| S1 (descriptive) | (up, down) sensitivity | reported, no verdict. Expected: (2, 1) gives upward spirals at alpha 0.5; (1, 2) makes below-threshold cells at alpha 1 downward | deterministic |
| S2 (descriptive) | corrected robustness, cliff, full ladder, withdraw-only | reported, no verdict | deterministic |

## Verdict rule

H35 is supported iff C1, C2 and C3 hold (a spiral up above a threshold, decay below it, at the amplification levels predicted) and C7's alpha >= 1 clause holds (warm pairs are not tipped by a short rupture). If C3 fails because the threshold is at g0 0 (the naive egoist takes off from a cold start), H35's "cold-start egoist warms" clause is supported and its threshold clause is not.

## Not testable by design

Everything is deterministic.

## Limits stated now

- Care rises and decays by fixed steps, by assumption. Real attachment is slower to fall than to rise, or the reverse; S1 sweeps two alternatives only.
- The naive egoist is not optimal for its own lifetime pleasure once g moves. The sophisticated egoist is, and it may grow its own care on purpose, which is a different claim from "the environment grows care".
- Rupture is anticipated (exact schedule). An unforeseen rupture needs a stochastic shock, not built.
- Full information, one menu, the partner is a rule. All H32 and H32b limits apply.

## Amendments

None yet.

## Queued after H35 (coordinator, 2026-11-11)

H32d, an attune-style ladder: the partner calms down only when its own pleasure has improved over a trailing window (4 to 8 weeks), never on a concession event, so a token week the egoist planned anyway buys nothing. Run alone and with the withdraw rung, against the H32b full ladder and withdraw-only. Separate prereg.
