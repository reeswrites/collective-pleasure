# Voluntary public goods game (VPGG): preregistration (2026-11-10)

Status: written and committed BEFORE the first run. Never edited after. Results go in `docs/results/vpgg.md`. Nothing here is a result.

Purpose: rung 2 of the simple-models ladder (ADR 0009), chosen first as a REDISCOVERY test. Does the pipeline (ADICO cards, gate, proof checks, two scores, frontier) recover a known result from the literature, with parameters taken from the paper and not tuned?

## The cited result (read from the paper; yes, verified)

Hauert, C., De Monte, S., Hofbauer, J., Sigmund, K. (2002). "Volunteering as Red Queen mechanism for cooperation in public goods games." *Science* 296(5570): 1129-1132, 10 May 2002, doi 10.1126/science.1070582. I read the Science text (pp. 1129-1131).

What the paper claims, paraphrased:
- In a compulsory public goods game with r smaller than the group size, defecting beats cooperating in every group, so groups end up all-defector and the public good is lost (p. 1129).
- Add a "loner" option: a player may decline to join and takes a fixed side income sigma. Cooperators, defectors and loners then do not settle. Cooperators beat defectors only when loners are common (small groups, a Simpson's-paradox effect); defectors beat cooperators when cooperators are common; loners beat defectors when defectors are common. The three types cycle in a rock-scissors-paper pattern (p. 1130).
- Model (p. 1130): a random sample of N individuals is offered the game; loners refuse and each get P_l = sigma; the S joiners hold n_c cooperators; if S = 1 that player acts as a loner; investment normalized to 1; P_d = r n_c / S; P_c = P_d - 1; assume r > 1 and 0 < sigma < r - 1.
- Fig. 1 parameters: N = 5; panels B to D r = 3, sigma = 1 (panel A r = 1.8, sigma = 0.5); panel D is an individual-based simulation, population 5000, 10^6 interactions, "the strategy of a randomly picked individual is imitated whenever it performs better", and it confirms stable cycles. For r > 2 the replicator dynamics has an interior equilibrium Q surrounded by closed orbits. The time average of the payoff of every strategy equals sigma. "In the long run [individuals] do no better than if the public goods option had never existed."
- Dynamics hold under imitation (replicator), perturbations (random sigma, r, N, errors), and spatial lattices. Fig. 3 (p. 1131) is the SPATIAL comparison (compulsory persists only at r above about 3.90; voluntary for all r > sigma + 1). That is a different regime from ours and is NOT what we test.

Related, cite only, not built: Aktipis, C. A. (2004). "Know when to walk away: contingent movement and the evolution of cooperation." *Journal of Theoretical Biology* 231(2): 249-260, doi 10.1016/j.jtbi.2004.06.020. Citation confirmed from bibliographic records (abstract level; I did not read the full text). Its claim, as far as I verified: a simple walk-away rule can outperform more complex strategies and resists invasion.

What we test is the WELL-MIXED claim only: compulsory collapses; voluntary persists with cycles; time-average payoff about sigma.

## Game parameters (from the paper, fixed)

- Group size N = 5. Multiplication r = 3 (1 < r < N). Cost c = 1. Loner payoff sigma = 1 (0 < sigma < (r - 1)c = 2). Strategies: C (join and contribute), D (join and do not contribute), L (abstain).
- Payoffs: S joiners, n_c contributors. S >= 2: P_d = r c n_c / S, P_c = P_d - c. S <= 1: that player gets sigma. Abstainer: sigma.
- Expected interior equilibrium from the paper's well-mixed formulas (ref. 23), solved by me before any run: x_c about 0.27, x_d about 0.27, x_l about 0.46 (payoffs all about 1.00 = sigma). The paper says time averages correspond to Q.

## Simulation design (ASSUMED where the paper is silent; fixed now)

- Population 5000 (the paper's Fig. 1D). Generations 3000; first 500 are burn-in and are not counted. 20 seeds (0 to 19), both regimes, same seeds.
- Each generation: R = 5 rounds; each round shuffles the population into 1000 groups of 5; each agent's payoff is averaged over its 5 rounds. (ASSUMED: the paper does not say how many games per update.)
- Imitation: each agent revises with probability 0.1; it picks a random model and adopts the model's strategy with probability (P_model - P_self) / Delta if positive, Delta = max payoff - min payoff = r c (N-1)/N - (r c/N - c) = 3.2. (Paper's rule: proportional to payoff difference. Delta and rate ASSUMED.)
- Mutation: each agent, each generation, with probability 0.002 is reset to a uniformly random strategy (ASSUMED; needed so a finite population does not freeze in an absorbing state). Chosen small: in the compulsory regime selection removes cooperators at about 0.03 per generation times the defector share against an injection of about 0.0007, so mutation alone supports a cooperator share near 0.02.
- Start: one third each.

## Two rule regimes (ADICO cards, rules/vpgg/)

- COMPULSORY: "A player must not abstain when invited"; may join; may contribute.
- VOLUNTARY: "A player may abstain and then receives sigma"; may join; may contribute.
- Gate adapter (ASSUMED, in src/mar/games/vpgg.py): the existing compile/gate/patch_check are hard-wired to the fishery's variables (pool, month_total, catch), so vpgg.py carries a small mirror compiler over the variables invited, abstain, contribute, using the same Card format and the same Z3 violation semantics. Under COMPULSORY a blocked abstain falls back to join-and-defect (ASSUMED: a forced participant who would rather be out does not contribute). So under COMPULSORY the L strategy is behaviorally D. Gate verdicts are cached per distinct (invited, action) pair.

## Scores (formulas)

- Freedom per agent-round = 0.5 E + 0.5 R. E = 1 if the gate permits abstain for that agent that round (exit available), else 0. R = 1 if E = 1 and abstaining is a real option, meaning joining is not strictly better or strictly worse than sigma in every possible group (some group composition gives a join payoff below sigma and some above). R guards against a sham exit (sigma outside (0, (r-1)c)); at the paper's parameters R equals E, so the two parts coincide here. Freedom = mean over agent-rounds counted.
- Cooperation = 0.5 K + 0.5 W. K = time-average contribution rate = contributions made per agent-round. W = mean payoff per agent-round divided by the all-cooperate maximum (r - 1)c = 2, clipped to [0, 1].
- Frontier: mean over seeds per regime; "dominates" as in src/mar/frontier.py.

## Predictions (numeric, committed before any run)

k for proof checks: 3 rounds (sanction horizon). State bound: group size invited in 1..5, roles C, D, L. The cards carry no sanctions, so the checks are the same every round, and I report k = 3 as the bound actually checked.

1. Proof checks. (1a) VOLUNTARY: "exit available" passes for every role (C, D, L) in every invited state in 1..5, within k = 3. (1b) COMPULSORY: "exit available" FAILS for every role at every invited state, within k = 3 (no card ever permits abstain; no repair path). (1c) Both regimes pass "no deadlock" (some permitted action in every state).
2. COMPULSORY collapse: in every one of the 20 seeds, the time-average cooperator share over generations 500 to 3000 is below 0.05; mean across seeds below 0.05.
3. VOLUNTARY persistence: in every one of the 20 seeds the time-average cooperator share is at least 0.10; the mean across seeds is between 0.15 and 0.40 (paper's Q: 0.27). Cycling: in at least 18 of 20 seeds the standard deviation over time of the cooperator share is at least 0.05, and each of C, D, L has seed time-average share at least 0.10.
4. Payoff (the paper's "no better than without the option"): VOLUNTARY mean payoff per agent-round across seeds is within 0.15 of sigma (0.85 to 1.15); COMPULSORY mean payoff is below 0.3.
5. Frontier: the VOLUNTARY mean point (freedom, cooperation) dominates the COMPULSORY mean point, with cooperation strictly higher by at least 0.15. Note: freedom is 1 versus 0 by construction of the cards, so the substantive content is the cooperation gap.

## Verdict rule

REDISCOVERED = predictions 1, 2, 3 and 5 all hold. Prediction 4 is reported separately (it is a second, independent claim of the paper). Any failed prediction is reported as failed with its numbers; the prereg is not edited. A pass here is a statement about this pipeline at 20 seeds and one parameter point (r = 3, sigma = 1, N = 5), not about the paper.

## Calibration warning

Parameters come from the paper (Fig. 1) and from nothing else; assumed knobs (rounds, revision rate, mutation, Delta) are fixed above and will not be changed after seeing results. A rediscovery tuned after seeing misses is calibration, not evidence (ADR 0009).
