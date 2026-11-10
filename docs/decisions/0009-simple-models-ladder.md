# 0009. Simple-models ladder: rediscover known results before LLM households

Status: accepted (2026-11-10)

## Context

The author decided on 2026-11-10 to run a ladder of simple models before the LLM households. Each rung adds one complication to the one below it, and each has a published result the pipeline should rediscover. Overview: docs/goal.md. ADR 0007 set the household as the main world and the seam ladder as the central measure; this ADR puts a cheap validation ladder in front of them. Nothing here is a result.

## Decisions

1. **The ladder.** Rung 1: bargaining with outside options. Rung 2: voluntary public goods game. Rung 3: network with cuttable ties. Rung 4: household. Each rung adds one complication: an exit value that sets your share (1), a group game with a loner option (2), a choice of whom to be tied to (3), several linked needs and an outsider (4).
2. **Rediscovery first, rung 2 first.** Before spending on agents that talk, check that the pipeline (ADICO cards, gate, bounded proof checks, freedom and cooperation scores, frontier) reproduces a result somebody else already established. Rung 2 goes first because its result is about exactly our two scores: optional participation (exit) keeps cooperation alive. Rung 2 ran on 2026-11-10: docs/results/vpgg-prereg.md, docs/results/vpgg.md. Outcome: persistence, payoff and frontier claims held; the oscillation clause of prediction 3 failed, so by the committed verdict rule it is NOT rediscovered (a negative result, in docs/negative-results.md).
3. **Predictions first; parameters from the paper, not tuned.** The author's other project taught that a rediscovery tuned after seeing misses is calibration, not evidence. So the prereg is committed before the first run, parameters come from the paper (N=5, r=3, sigma=1 from Fig. 1), knobs the paper leaves open are fixed and marked ASSUMED before the run, and a miss is recorded as a miss. A rerun with other knobs is a new preregistered experiment, not an edit.
4. **A failed rung is information, not a blocker.** The rung-2 miss is about cycle amplitude, a thing the paper does not quantify, and about our assumed update knobs. It does not stop rung 1 or 3. It does mean the next rung's prereg should derive its thresholds from the source or from a stated analytic calculation, and not from a guess.
5. **Later: abstraction and bisimulation carry results between rungs.** Open aim, nothing built. If a rung-k model is a bisimulation-quotient (or a stated abstraction) of rung k+1 with respect to the properties the proof checks verify (exit available, repair within k), a proof at the lower rung can be lifted to the higher one, and a result found there can be tested at the higher one. First step when we get there: define the property set, show on the VPGG that the abstraction from agent-level to strategy shares preserves "exit available" and the sign of the cooperation gap, and state what it does not preserve (the cycle shape is not preserved by a mean-field quotient).

## Rung plans (citations checked against bibliographic records; full texts not read unless noted)

**Rung 1: bargaining with outside options.** What you get by walking away sets your share, but only when the walk-away value is high enough to bind.
- Rubinstein, A. (1982). "Perfect equilibrium in a bargaining model." *Econometrica* 50(1): 97-109. From memory, not checked here: alternating offers with discounting have a unique subgame-perfect split.
- Binmore, K., Shaked, A., Sutton, J. (1989). "An outside option experiment." *Quarterly Journal of Economics* 104(4): 753-770. Checked: the experimental result favors the "deal-me-out" prediction (outside option matters only when a bargainer would otherwise go elsewhere) over "split-the-difference".
- Binmore, K., Rubinstein, A., Wolinsky, A. (1986). "The Nash bargaining solution in economic modelling." *RAND Journal of Economics* 17(2): 176-188. Bibliographic entry seen, results not checked.
- To rediscover: (a) with an outside option below the no-option split, the split does not move; (b) with an outside option above it, the share equals the outside option (the outside option principle); (c) the exit card's "exit available" check separates regimes where walking away is blocked.
- Prereg before run: closed-form predictions are available, so thresholds can be set from the formulas, unlike rung 2.

**Rung 3: network with cuttable ties.**
- Santos, F. C., Pacheco, J. M., Lenaerts, T. (2006). "Cooperation prevails when individuals adjust their social ties." *PLoS Computational Biology* 2(10): e140, doi 10.1371/journal.pcbi.0020140. Checked: individuals self-organize both strategy and ties by self-interest; cooperation thrives with high average connectivity when partners can be adjusted quickly enough; resulting networks are heterogeneous.
- Santos, F. C., Pacheco, J. M. (2005). "Scale-free networks provide a unifying framework for the emergence of cooperation." *Physical Review Letters* 95: 098104. Checked at abstract level: on scale-free contact networks cooperation dominates in prisoner's dilemma and snowdrift games. A later critique (Wu, Xu, Wang, arXiv physics/0508220) says the result depends strongly on the update dynamics: a reason to preregister the update rule.
- To rediscover: cooperation under adjustable ties (the exit card as "cut a tie") exceeds cooperation on fixed ties at the same average degree, and the benefit shrinks as tie-adjustment slows. Parameters from the paper; the cut-rate threshold gets stated before running.

Also cited only (not built): Aktipis, C. A. (2004). "Know when to walk away: contingent movement and the evolution of cooperation." *Journal of Theoretical Biology* 231(2): 249-260. A simple walk-away rule can do well and resist invasion (abstract level).

## Consequences

- Rung 1 and rung 3 each get a prereg, a game module under src/mar/games/, rules under rules/<name>/, and a results file, using the same shape as rung 2.
- The existing compile, gate and patch_check are hard-wired to the fishery. Rung 2 carries a mirror compiler in src/mar/games/vpgg.py (ASSUMED adapter). When a second game needs the same, factor a variable-set parameter into compile.py rather than copying a second time (changing it is outside this ADR).
- The household work (ADR 0007, 0008) proceeds on its own track; rungs do not block it.
