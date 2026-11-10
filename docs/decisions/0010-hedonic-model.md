# 0010. A modeled hedonic state as the grounding of "good" in the household world

Status: accepted (2026-11-10, author decisions in conversation)

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

## Context

Household v1 (docs/results/household.md) was trivial: a gate can only forbid, scripted agents had no goals, so no rule set could raise cooperation, and sanctions were declared but not enforced. The author asked for goals, a weekly clock, rare shocks, pleasure as the grounding of "good", and a norm quality measure that is not a single score. Evidence: docs/results/household-v2-prereg.md (committed first), docs/results/household-v2.md.

## Decisions

1. **Weekly step.** 156 weeks; money settles every 4 weeks (a 4-week "month", ASSUMED simplification). The v1 monthly world and the seam ladder code stay as they were.
2. **Goals.** Needs that decay on real clocks (rest, connection, money, security; src/mar/hedonic.py) and aspirations from the persona's weights (security buffer, time together, friends, savings, autonomy). Personas gain `needs` (salience) and `aspirations` (targets) fields; defaults come from the weights by an ASSUMED mapping (personas.py); the six hand personas and the 32 grid skeletons carry them explicitly.
3. **Two hedonic channels.** Pleasure (needs met, aspirations satisfied, time together, new connections). Suffering of two kinds: offsettable (ordinary hardship, compensable by pleasure) and non-offsettable (being trapped with no real exit, a need denied for weeks, being steadily restricted by the rules). A condition held 4 consecutive weeks stops being offsettable. Non-offsettable suffering is never netted against pleasure; it lowers capacity, blocks classification as upward, and can fail a run.
4. **Spiral dynamics.** One position B per agent. Below the tipping point suffering compounds (feedback 0.08 per unit of distance), above it pleasure compounds (0.05). Capacity (how well an agent meets needs, connects and negotiates) rises with B and falls with the non-offsettable load. Motivation, not evidence for the numbers: the upward loop follows Fredrickson's broaden-and-build theory (Fredrickson 2001, American Psychologist 56(3):218-226; Fredrickson and Joiner 2002, Psychological Science 13(2):172-175; both verified by search); the downward loop follows scarcity and poverty-trap work (Mani et al. 2013, Science 341:976-980, verified by search; Carter and Barrett 2006, J. Development Studies 42(2), from memory, unverified). Tipping point and rates are ASSUMED and live in one block, `HedonicConfig`.
5. **Shocks are misalignment in the wider system, not fate.** Job loss, illness and moves are failures of the economy, the workplace, the health system and the housing market, outside the household. Their rates are low and tunable in the config block: job loss 0.12 per person-year (BLS JOLTS, layoffs and discharges about 1.0 to 1.1 percent of employment per month), illness 0.08 (ASSUMED), move 0.087 per household-year (Census CPS 2022 mover rate 8.7 percent, secondary-source reading), new connection 0.20 (ASSUMED). Schedules use common random numbers across rule variants.
6. **Enforced sanctions.** A card with an `or_else` is a soft rule: an agent may break it and pays the sanction for the declared duration (warn: an offsettable reproach; cap_halve: loses spend_self; suspend: only work, shared spending, refusing and rest remain). A card without one is a hard wall. Detection is perfect (ASSUMED).
7. **Persona-driven agents.** A utility-like policy: for each action, sum over needs of salience x marginal value x expected change in the need level (scaled by capacity), plus aspiration progress, plus a prosocial term for shared bills and time together, minus money and fatigue costs, minus an estimated sanction cost. Prosocial weight comes from the giving axis and togetherness weight. The agent attempts the best action the world allows. Seeded noise of 10 percent varies seeds.
8. **Norm quality.** Share of persona pairings (all 15 pairs of the hand personas, the mismatched Anchor and Wanderer included, 3 seeds) whose both partners end in the upward spiral; time to cross the tipping point; automatic FAIL of a run if a partner has 6 or more consecutive weeks of non-offsettable suffering, and of a norm if a third of its runs fail; average pleasure over passing runs only. Freedom and cooperation (v1 formulas) are reported alongside: they guard against "pleasure machine" norms (high pleasure, low freedom) and pleasure guards against "numb" households (low suffering, low pleasure, low cooperation). All are reported; none is collapsed into one score.

## Caveat

Scripted agents with assumed preferences are not people. Every rate and weight is a tunable assumption, listed in docs/results/household-v2.md.

## Later (version 3)

Endogenous rupture, deliberately not built now. Tension accumulates from mismatches: one partner repeatedly giving more than getting, needs left unmet, negotiated terms that stop fitting. A rupture happens when tension crosses a threshold, and each rupture is traced back to the rule that allowed it, so ruptures become seams the evaluator can see.

## Consequences

- scripts/household_run.py runs v2 by default (`--v1` keeps the old run); report: runs/household-v2/frontier.html (not committed).
- The negotiation phase of ADR 0008 is still stubbed (fixed exit terms in rules/household/author_seed/).
