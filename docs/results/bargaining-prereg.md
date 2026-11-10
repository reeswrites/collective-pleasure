# Bargaining with outside options: preregistration (2026-11-10)

Status: written and committed BEFORE any code for this rung exists and before the first run. Never edited after. Results go in `docs/results/bargaining.md`. Nothing here is a result.

Purpose: rung 1 of the simple-models ladder (ADR 0009). Does the pipeline (ADICO cards, mirror gate, bounded proof checks, freedom and cooperation scores, frontier) recover two known bargaining results, with formulas taken from the literature and not tuned?

## Citations (what I verified)

- Rubinstein, A. (1982). "Perfect equilibrium in a bargaining model." *Econometrica* 50(1): 97-109, doi 10.2307/1912531. VERIFIED at bibliographic-record and abstract level (web search, 2026-11-10); I did not read the full text. (Some listings give pages 97-110; 97-109 is the majority.) Claim used: alternating offers, fixed discount factors d1, d2, unique subgame-perfect equilibrium; player 1 (first proposer) gets (1 - d2) / (1 - d1 d2), accepted at once.
- Binmore, K., Shaked, A., Sutton, J. (1989). "An outside option experiment." *Quarterly Journal of Economics* 104(4): 753-770, doi 10.2307/2937866. VERIFIED at record and abstract level; full text not read. Claim used: the strategic ("deal-me-out") analysis says an outside option does not affect the deal unless the bargainer would otherwise go elsewhere; the "split-the-difference" (Nash with options as disagreement point) prediction is the rival. The paper is a human experiment; I do not reproduce it.

What this rung tests: the THEORY (the outside option principle), by comparing a backward-induction computation (simulated, with the gate in the loop) against closed-form formulas derived below. It is not a test of human behavior.

## Game (ASSUMED where the sources are silent; fixed now)

- Pie of 1. Players 1 and 2 alternate proposals, player 1 first, periods t = 0..T-1, T = 60 (finite deadline; at the deadline without agreement both get 0). The responder accepts, or rejects. Payoffs are discounted by d_i^t at the period of the outcome. A proposal is the share y offered to the other player.
- Outside options o1, o2 (fractions of the pie). EXIT: a player who may exit takes the exit at its own decision node (as responder instead of accepting, or as proposer instead of proposing); the exiter gets o_i d_i^t and the other player gets o_j d_j^t (both "go elsewhere"). Exit value is discounted like the pie (ASSUMED).
- Ties: accept when offered exactly the continuation value; agree rather than exit when equal.
- Grid: o1, o2 each in {0, 0.1, 0.2, 0.3, 0.4, 0.5} (36 cells, o1 + o2 <= 1 always); discount pairs (d1, d2) in {(0.9, 0.9), (0.9, 0.7), (0.7, 0.9)} (108 cells in all). Grid and discounts are ASSUMED (the sources give general d, no numbers I read).
- Agents (scripted, no model calls): EQ (backward-induction subgame-perfect player for the regime in force); FIFTY (demands 0.5, accepts >= 0.5); STUBBORN (demands 0.7, accepts >= 0.7); CONCEDER (demand max(0.3, 0.7 - 0.05 t), accepts >= its current demand); SPLITDIFF (the split-the-difference rival: demands o_i + (1 - o1 - o2)/2, accepts >= that). Heuristics exit, when exit is permitted, if rejecting an offer below their own outside option; they never exit as proposers. Heuristic demands get Gaussian jitter (sd 0.03, per run, from the seed). Seeds 0..19. EQ is deterministic.
- Gate: a mirror of the fishery compiler (the existing compile/gate are hard-wired; same pattern as VPGG) over variables period, exit, agree. A blocked exit falls back to continuing the bargaining.

## Regimes (ADICO cards, rules/bargaining/)

- EXIT-ALLOWED: "A player may exit and take their outside option" (plus may continue, may agree).
- NO-EXIT: "A player must not exit; keep bargaining until agreement or the deadline" (plus may continue, may agree).

## Closed-form predictions (derived by me from the model above; the derivation is the prediction)

Let x1* = (1 - d2) / (1 - d1 d2) (Rubinstein) and x2* = 1 - x1* = d2 (1 - d1) / (1 - d1 d2). Stationary values p_i = what proposer i keeps in current-period terms; the responder j accepts y iff y >= max(o_j, d_j p_j). So p1 = 1 - max(o2, d2 p2), p2 = 1 - max(o1, d1 p1). Solving the four cases:
- Neither binds (o2 <= x2*, o1 <= d1 x1*): p1 = x1*. Options are irrelevant.
- Only o2 binds (o2 >= x2*, o1 <= d1 (1 - o2)): p1 = 1 - o2. Player 2 gets its outside option.
- Only o1 binds (o1 >= d1 x1*, o2 <= d2 (1 - o1)): p1 = 1 - d2 (1 - o1).
- Both bind: p1 = 1 - o2.
Player 1 proposes first, so its realized share at t = 0 is p1 and agreement is immediate (delay 0). o2 binds iff o2 >= x2* (the outside option principle: it matters only if it exceeds what the player would get anyway). The threshold for player 1's option is d1 x1* (what 1 would get as responder next period).

Counts from this formula over the grid (computed from the formulas before any simulation, no run): cells where p1 differs from x1* by at least 0.04: 36 of 108; cells where p1 = x1* exactly: 49 of 108; the other 23 differ by less than 0.04.

## Scores (formulas)

- Freedom, per player i: empowerment-like count of reachable distinct outcomes. n_i = number of distinct strictly positive payoffs o_i d_i^t over periods t < T in which the gate permits exit (those are outcomes player i can cause alone beyond the deadline outcome 0). E_i = log2(1 + n_i) / log2(1 + T). Freedom = mean of E_1 and E_2. So a permitted exit with o_i = 0 is a sham and counts 0.
- Cooperation = 0.5 A + 0.5 W: A = 1 if agreement was reached; W = u1 + u2 (total discounted payoff, at most 1; delay and exit both reduce it).
- Fairness (reported, not in the frontier): 1 - |x1 - x2| over agreed games, x the undiscounted division.
- Frontier: src/mar/frontier.py aggregate/pareto/dominates on (freedom, cooperation), per regime.

## Predictions (numeric, committed before any run)

Proof-check bound: k = 5 periods (periods 0..4), both regimes, "exit path" = some permitted exit within k periods.

1. Proof checks. (1a) EXIT-ALLOWED: exit path within k = 5 passes (exit permitted at every period 0..4). (1b) NO-EXIT: exit path within k = 5 FAILS (no permitted exit at any period 0..4; no repair path). (1c) Both pass no-deadlock (a permitted continue or agree exists every period).
2. Outside option principle (EXIT-ALLOWED, EQ vs EQ, 108 cells, T = 60). (2a) Realized player-1 share at t = 0 is within 0.02 of the closed-form p1 in every cell. (2b) In the 49 cells where the formula says no change, |x1 - x1*| <= 0.02; in the 36 cells where it says change >= 0.04, |x1 - x1*| >= 0.02. (2c) Agreement at t = 0 in every cell.
3. Rubinstein split (NO-EXIT, EQ vs EQ, 108 cells). The share x1 is within 0.02 of (1 - d2)/(1 - d1 d2) in every cell, independent of (o1, o2) (the 36 outside-option cells per discount pair have identical shares within 0.02), and agreement is at t = 0.
4. Frontier. (4a) EQ vs EQ over the grid: the exit-allowed mean point dominates the no-exit mean point (freedom 5/6 = 0.833 within 0.001 versus 0; cooperation not lower by more than 0.01). (4b) All 25 ordered agent pairings x 108 cells x 20 seeds: exit-allowed freedom above no-exit and exit-allowed cooperation at least no-exit cooperation minus 0.01.

## Verdict rule

REDISCOVERED = predictions 1, 2 and 3 all hold. Prediction 4 is reported separately. A failed prediction is reported with its numbers; the prereg is not edited; no retuning. A pass is a statement about this pipeline at this grid and T = 60, and about the theory's internal consistency, not about human subjects.

## Calibration warning

Closed forms come from the model; the tolerances (0.02, 0.04, 0.01) and grid are fixed here. A rerun with other knobs is a new preregistered experiment.
