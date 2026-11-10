# Bargaining with outside options: results (2026-11-10)

Prereg: docs/results/bargaining-prereg.md (committed before any code or run, not edited). Run: `uv run python scripts/bargaining_run.py` (2 regimes, 108 cells, 25 ordered agent pairings, 20 seeds; about 10 seconds, no model calls). Report with charts: runs/bargaining/report.html (git-ignored, about 130 KB, light/dark). Note on order: the module, cards and tests were committed before the run; the run script was committed after the first run; a second run after a chart-size fix (deduplicated scatter dots, 23 MB down to 130 KB) gave identical numbers.

## Verdict

**REDISCOVERED, by the committed rule (predictions 1, 2, 3 hold).** Prediction 4 (frontier) FAILS on its all-pairings clause. What was rediscovered is the theory: a backward-induction player run through the gate matches Rubinstein's split without exit and the outside option principle with exit, to under 0.001. This is not a replication of Binmore, Shaked and Sutton's human experiment, and the agreement is between two computations of one model (a table-driven equilibrium player versus closed forms I derived), so it validates the pipeline and my algebra, not nature.

## Citations (verified: yes at record and abstract level; full texts NOT read)

- Rubinstein (1982), Econometrica 50(1): 97-109, doi 10.2307/1912531: yes (bibliographic records; Econometric Society abstract gives (1 - d2)/(1 - d1 d2)). Some listings say pages 97-110.
- Binmore, Shaked, Sutton (1989), QJE 104(4): 753-770, doi 10.2307/2937866: yes (LSE repository and EconPapers records; abstract: outside options do not affect the deal unless a bargainer would otherwise go elsewhere). A ResearchGate note claims a RAND 1990 publication; unconfirmed, ignored.
- ADR 0009 said Rubinstein's statement was "from memory, not checked"; it now is checked at abstract level.

## Prereg versus actual

| # | Prediction (committed) | Actual | Holds |
|---|---|---|---|
| 1 | Exit-allowed: exit path within k=5 passes; no-exit: fails; both no-deadlock pass. | exit-allowed pass (exit permitted at periods 0..4); no-exit fail (no permitted exit at any period 0..4, no repair path within k=5); no-deadlock pass for both. | yes |
| 2 | Exit-allowed, EQ vs EQ: player-1 share within 0.02 of the closed form in all 108 cells; 49 no-change cells stay within 0.02 of Rubinstein; 36 cells with predicted change >= 0.04 move by >= 0.02; agreement at t=0 everywhere. | max error 0.0009; the 49 and 36 cells are consistent; agreement at t=0 in all 108 cells. | yes |
| 3 | No-exit, EQ vs EQ: share within 0.02 of (1-d2)/(1-d1d2) in all cells, independent of options, immediate agreement. | max error 0.0009; spread across the 36 option cells per discount pair 0.0000; agreement at t=0 everywhere. | yes |
| 4 | Frontier: (4a) EQ vs EQ exit-allowed dominates no-exit; freedom 0.833; cooperation within 0.01. (4b) all 25 pairings x 20 seeds: exit-allowed freedom higher and cooperation >= no-exit minus 0.01. | (4a) exit-allowed (0.833, 1.000) vs no-exit (0.000, 1.000): holds. (4b) exit-allowed (0.833, 0.503) vs no-exit (0.000, 0.522): cooperation lower by 0.019, so the clause FAILS (neither point dominates; both are on the frontier). | **(4a) yes, (4b) FAILS** |

Extra numbers (not predictions): mean absolute gap of the simulated share to the deal-me-out closed form 0.0001, to Rubinstein ignoring options 0.070, to split-the-difference 0.145. So within this model the rival Nash-with-options formula is clearly the worse predictor. Over all pairings: agreement rate 0.481 under exit-allowed (outcomes: 25,986 agree, 15,781 exit, 12,233 deadline) versus 0.629 under no-exit (33,941 agree, 0 exit, 20,059 deadline); fairness over agreed games 0.815 versus 0.789.

## Reading the failure of (4b)

Exit does not simply add cooperation. Pairings with an impatient or conceding heuristic lose surplus to exits that a continued negotiation would have avoided (per-pairing cooperation change from allowing exit: STUBBORN vs EQ -0.067, EQ vs STUBBORN -0.220, CONCEDER vs CONCEDER -0.266, CONCEDER vs FIFTY -0.193), while pairings that otherwise deadlock gain (STUBBORN vs STUBBORN +0.194, STUBBORN vs FIFTY +0.151). The sign depends on the heuristic mix, which I chose. My slack (0.01) was a guess, and the net -0.019 is small relative to the swings. The heuristic exit rule (exit when the offer is below your outside option, a rule that ignores what waiting would earn) is itself an ASSUMED choice that drives the exits. A rerun with a different rule or mix is a new preregistered experiment, not an edit here. The frontier conclusion that survives: with equilibrium players exit-allowed weakly dominates; with a heuristic population the two regimes trade freedom against cooperation, and freedom as defined (exit with positive value) is 0 versus 0.833 by construction.

## ASSUMED choices

- Pie 1, T=60 deadline with disagreement payoff 0, player 1 proposes first; exit payoff o_i d_i^t to the exiter and o_j d_j^t to the other; exit available to proposer and responder (Binmore et al. let the responder exit); ties accept and agree rather than exit.
- Grid o in {0,...,0.5}, discount pairs (0.9,0.9), (0.9,0.7), (0.7,0.9): neither source gives numbers I read.
- Heuristic agents (FIFTY, STUBBORN, CONCEDER, SPLITDIFF), jitter sd 0.03; a blocked proposer exit becomes an even offer, a blocked responder exit becomes a reject.
- Gate: mirror compiler over period/exit/agree (same pattern as vpgg.py; compile.py untouched). Card N1 needs the condition `exit ge 1` (an empty-condition must_not blocks everything in this mirror reading; found and fixed in tests before any run).
- Freedom: log-count of distinct positive exit payoffs, so a zero-value exit is sham (0). Because the cards are uniform over periods this reduces to 1 when exit is allowed and o_i > 0, else 0; the count is real but has no gradient here.
- Cooperation = 0.5 agreement + 0.5 total discounted payoff; fairness = 1 - |x1 - x2| over agreed games.
- The EQ player's table and the closed form are independent computations but of the same model; seeds only affect heuristic jitter (EQ is deterministic), so the 20 seeds do not add power to predictions 2 and 3.

## Not tested

Human behavior (the BSS experiment), the Binmore-Rubinstein-Wolinsky Nash-solution link (record only), exit available only to the responder, stochastic breakdown, uncertainty about the other's outside option.

## Negative-results ledger

docs/negative-results.md (owned by another agent) should get a line: "Bargaining rung 1, prediction 4b: allowing exit lowered mean cooperation by 0.019 over a heuristic mix (not within the committed 0.01 slack); the exit-allowed frontier advantage holds only for equilibrium players. Not retuned. docs/results/bargaining.md."
