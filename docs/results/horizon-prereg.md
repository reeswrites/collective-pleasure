# Horizon preregistration: is lifetime pleasure different from being greedy? (ADR 0015 template, ADR 0017)

Status: written and committed before the confirmatory run (`scripts/horizon_run.py`). Nothing here is a result. Scripted or model agents: none (exact dynamic programming over a small model). Model API calls: none.

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

## Purpose and claim

The author said (2026-11-10): "lifetime pleasure seems obvious to me and also i feel like present value maximization infers that you need to optimize over time and not be greedy but idk if we can prove that somehow". Then, on what "changing the future situation" means: "if it diminishes pleasures a little bit is it stealing from future pleasures or no". Then, on who counts: "the experiencing self is the remembering self and depends on vividness of memory etc" (typos as written, quoted in ADR 0017).

This study asks, in a model small enough to solve exactly: (1) when is a greedy one-step policy as good as the optimal plan, (2) how much does greedy lose when carried-over state matters, as a function of discount, horizon, adaptation and commitment payoff, and (3) does a "concert" that lowers some later pleasures but raises others pay off in total, and at what spacing. It also gives a worked case, the best gap between seeing someone, scored by one self whose moments include re-experienced memories weighted by vividness. It changes a decision: whether ADR 0017 (lifetime pleasure is the measure) needs a planning evaluator, and what the household world's pleasure score must carry (memory and anticipation, not only the present week).

New claim ids are not yet in docs/claims.md; they are added with the results.

## Design

- Model: `src/mar/horizon.py`. A deterministic MDP, state = (adaptation of favorite, adaptation of alternative, weeks since the last event, connection need 0..2, pot 0..3, commitment 0..3, good-memory glow, acquired taste, bond, bad-memory glow), 7 actions (repeat favorite, rotate, shared ritual, solo spend, save, honor commitment, concert). About 9,000 reachable states. Every number is ASSUMED and sits in one dataclass `HorizonParams` with the source idea from docs/notes/hedonic-technology-synthesis.md next to it (adaptation: M1; anticipation: M3; commitment friction early and recall payoff later: M4; pot: ADR 0013).
- "Future situation" means anything that carries over from one step to the next: tolerance, resources, energy and needs, memories, anticipation, tastes, bonds. Carryover is two-sided: tolerance, depletion, neglected needs and bad memories cost later pleasure; anticipation, vivid good memories, acquired taste and bonds add later pleasure; spacing restores tolerance.
- One self (author, 2026-11-10): each step's pleasure is the present pleasure plus remembered pleasure or pain re-experienced now, weighted by vividness, plus anticipation. In the MDP this is the good- and bad-memory glow (vividness by event: ritual 1, concert 2; a starved week leaves a bad memory that re-costs, rumination). In the gap case it is `SelfParams` (below).
- Conditions: gamma in {0, .1, ..., .9, .95, .99, 1}, horizons {1, 2, 3, 4, 6, 8, 12, 16, 26, 52} weeks (default 26), adaptation strength delta in {0 .. .4} (default .2), commitment payoff beta in {0 .. 3} (default 1.5). Start state: fresh activities, need met, pot 2, no commitment.
- Heuristics compared with greedy and optimal: rotate-every-n (n = 1, 2, 4), ritual-weekly, ritual-every-2, ritual-every-4.
- Greedy loss = optimal minus greedy total discounted pleasure from the start state (absolute and percent of optimal). Greedy breaks ties by the lowest action index. "Large" is declared now as 10% of optimal.
- **Unit of resampling: none.** The model is deterministic and has no seeds. Nothing here gets an interval; every prediction is a deterministic check of a computed table, reported as pass or fail (ADR 0015 point 4).
- Worked case, the gap between seeing someone (the author's 2026-09-10 claude.ai conversation on the optimal time between seeing someone, not archived in the repo): closeness halves every H days while apart; tension = M x closeness x want-to-see (saturating) x absence-becomes-normal factor; tension up to a threshold feels like anticipation, above it like pain; release at reunion is the drop from tension to zero; a meeting closes part of the closeness gap and has a cost; steady-state cycle. Four friendships of half-life 10, 20, 45 and 90 days. One self: lifetime per day = (present + vividness-weighted memory + scheduled anticipation) / g. Vividness = base + intensity + ending + novelty + emotion + shared; it decays with a time constant; a painful trace is re-costed by a rumination factor. Special cases: memory weight 0 is the old "experienced" score, present weight 0 (with vividness weights 0) is the old "remembered" score up to scale per cycle. All parameters ASSUMED in `GapParams` and `SelfParams`.
- Citations used for motivation, all from memory, verify before relying on them: Loewenstein 1987 (savoring), Kahneman et al. 1993 (peak-end), Nelson and Meyvis 2008 (interruption), Solomon and Corbit 1974 (opponent process), Helson (adaptation level), Parfit 1984 (temporal neutrality).

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

While building the model the author asked for design changes (two-sided carryover, a concert, a worked case, one self). I ran quick pilots to check the model was not degenerate and to fix defaults. What they showed, with defaults then set: greedy loses about 3% at gamma 0.9 over 26 weeks and about 25% at gamma 1; the optimal plan honors the commitment in the first three weeks; a concert is worth a free solo treat when carryover is off (so any gain is carryover); with the pilot's concert numbers, weekly concerts had negative net carryover and spacing of four weeks positive; the unified self's best gap grows with friendship depth (about 19, 42, 86, 139 days for half-lives 10, 20, 45, 90) while the old remembered self wanted 6 to 13 days. Early pilot versions had a flat meeting joy that made the best gap the minimum; I set it to 0 (relativity: the pleasure of a meeting is the release) and raised the meeting cost to 24 so the optimum is interior. These are parameter choices made by looking at pilot output, so the model is tuned to be non-degenerate, not tuned to a prediction's threshold; the predictions below were written after that and could still fail. Pilot data are not used as confirmatory data (the confirmatory run is the committed script, deterministic, so "excluded" means only that I do not count the pilot as having tested anything).

| Quantity | Pilot value | Spread | Source |
|---|---|---|---|
| greedy loss, gamma .9, 26 wk | about 3% | none (deterministic) | scratch pilot, not kept |
| greedy loss, gamma 1, 26 wk | about 25% | none | scratch pilot, not kept |
| critical gamma | about 0.38 | none | scratch pilot, not kept |

## Power check

Not applicable: no sampling, so no power. Every claim is a deterministic computation, reported as pass or fail. The grid sizes are the sample of conditions and are stated above.

## Predictions

Each is a deterministic check. A clause-wise prediction holds only if every clause holds.

| ID | Quantity | Comparison and threshold | Test | Interval |
|---|---|---|---|---|
| P1 | Greedy loss with all carried-over state off (adaptation, anticipation, need deprivation, commitment payoff, memory, taste, bond, rumination off; pot never binds) | exactly 0 on every cell of gamma in {0, .25, .5, .75, .9, .99, 1} x horizon in {1, 2, 3, 4, 6, 8, 12, 26} (56 cells), within 1e-9 | exhaustive grid | none (deterministic) |
| P1b | Greedy loss with only adaptation and commitment payoff off (anticipation, memory, pot, need still on) at gamma .9 and 1, 26 weeks | DESCRIPTIVE: reported, no verdict. The lemma predicts it can be positive because other carried state remains | grid | none |
| P2 | Greedy loss with default parameters | strictly positive at gamma 1 and 26 weeks; nondecreasing in gamma at 26 weeks over the gamma grid; nondecreasing in horizon at gamma .9 and at gamma 1 over the horizon grid (violations of more than 1e-9 are counted and reported, any violation fails the monotone clause) | grid | none |
| P3 | A witness: a reachable state s and horizon k <= 6 where greedy's total discounted pleasure is strictly below some other plan's | exists for gamma = 9/10 and gamma = 1, found by exhaustive search in exact rationals, then machine-checked by z3 over exact rationals (greedy plan is greedy at each step: unsat; a better plan exists: sat; no plan beats the stated best: unsat) | exhaustive plus z3 | none |
| P4 | Commitment | at gamma 0.9 over 26 weeks the optimal plan from the start state honors the commitment (accepts friction) at least once within the first 6 weeks when beta = 1.5; and with beta = 0 it never does | grid | none |
| P5 | Concert, net carryover (full-model gain of a concert every m weeks over never going, minus the same gain in the zero-carryover model, where a concert is exactly a free treat) at gamma .95, 26 weeks | negative at m = 1 (weekly), positive at m = 4; the dose boundary (smallest m with net carryover above 0 and staying above 0 up to m = 6) is reported; both clauses must hold | grid | none |
| P6 | One-self scoring in the gap case | (a) memory weight 0 reproduces the old experienced score exactly (to 1e-12) and present weight 0 with vividness weights 0 gives the old remembered score up to a positive constant per cycle (ratio constant to 1e-9) and the same best gap; (b) a vivid ending and a peak raise the after-the-fact value of an episode above its in-the-moment value (ratio above 1 for a +15 reunion); (c) a mild steady stretch contributes under 5% of its total through memory at 30 days and its share falls with length; (d) a vivid bad episode (-20) costs more after the fact than in the moment (ratio above 1), and more with rumination than without | closed-form and grid | none |
| P7 | The worked case, best gap | the one-self best gap is interior (between 1 and 200 days) for all four friendships and nondecreasing in friendship depth; the old remembered self's best gap is shorter than the old experienced self's best gap for all four; two people of half-lives 20 and 90 who must share one gap: the shorter-optimum person loses more than 0% of their best lifetime value at the longer person's gap, and closeness at the meeting is lower | grid | none |
| P8 | Present value still needs planning | the smallest gamma at which greedy strictly loses (critical gamma) over 26 weeks is below 0.95 at default parameters, i.e. a discounter with gamma = 0.95 still loses by being greedy | bisection on the table | none |

## Verdict rule

The lemma is a proof in docs/results/horizon.md (not a prediction). P1 to P8 are scored held or missed. The worked-case claims (P6, P7) and the concert claim (P5) hold for this ASSUMED parameter set only; none of them says anything about real people or real friendships. P3 holding means our model contains a case where greedy provably loses, not that any real choice does.

## Not testable by design

All rows. Deterministic proofs, exhaustive enumerations and exact dynamic programming are reported as passes or failures (ADR 0015).

## Limits stated now

One parameter point per sweep with the others at defaults (no interaction map). Assumed numbers; the model is deterministic, one agent, no partner's choice. The concert's "zero-carryover" comparison sets the concert equal to a free solo treat by assumption. The gap case is a steady-state cycle with closed-form recall mass (independent of the gap by stationarity); consolidation of every trace at the reunion is a simplification. The discounting and temporal-neutrality questions are philosophical and not settled by the numbers.

## Amendments

- 2026-11-10, before the confirmatory run: three author steers arrived while the model was being built and are folded into the design above, not applied after any confirmatory run: (1) carryover must be two-sided, with a concert prediction (P5); (2) a worked case on the gap between seeing someone; (3) one self, "the experiencing self is the remembering self", replacing the plan to report two selves separately (P6, P7). The two old selves stay as named special cases.
