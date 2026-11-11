# Stay test preregistration (ADR 0018 test 2, "worth it vs hard to leave")

Status: written and committed before the confirmatory run. Nothing here is a result. Scripted agents: the persona-driven household agents of ADR 0010 (no model). Model API calls: none.

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state (ADR 0010).

## Purpose and claim

ADR 0018 test 2 asks whether a household persists because staying is worth it or because leaving costs too much (docs/theory.md, section 2: "persists because worth it, not because hard to leave"). This experiment builds that test as an evaluator measure (`src/mar/stay_test.py`) and runs it once on the household world. It answers two questions. Does the measure separate a rule set with strong exit costs from one with none? And under the author's confirmed seed v2.2, what share of staying is held by cost? If the measure cannot separate the trap fixture from the baseline, it is not usable as an evaluator line. If seed v2.2 shows a large held-by-cost share, the seed fails test 2 in this model and the author should see that next to its pleasure score.

## The measure (defined before the run)

Two lenses. The behavioral lens is primary because it is what the code does.

1. **Behavioral lens (primary).** For every week a pair starts together, the week is replayed on a deep copy of the world (same random states) with every exit cost removed. A staying week (both in at the start and the end of the week, in fact) is **held by cost** if a partner leaves in the replay. Otherwise it is **worth it**. Each cost is then removed alone to name which one holds the partner ("joint" when no single removal is enough).
2. **Bar lens (secondary).** Every 13 weeks while both are in, each member's status-quo value SQ (the 26-week forward value under the current terms, minus the trust penalty, exactly as the 13-week review computes it) is compared with the outside option (better of living alone and with Friend C, 26-week rollout) at two holdings: what they could carry out with the exit costs (O_cost) and with them removed (O_free, at least the equal half of the pot). Worth: SQ >= O_free. Held: O_cost <= SQ < O_free. Bar-leave: SQ < O_cost. The pair takes the worst member verdict.

**The code's real bar differs from the ADR's wording, and we use what the code does.** The ADR names the bar max(outside option, status-quo value). In the code that bar only sets the terms at the 13-week reviews (`negotiation.negotiate_v2`); it never ends a household. Leaving is decided by the agent: "leave" goes on its menu only when distressed (4 or more low weeks, non-offsettable load N >= 0.2, or trust below 0.15), and the world executes it unless something blocks it. No outside option enters that decision. So the primary lens replays the agent's decision; the bar lens reports what the bar would say.

**Exit costs the code has**, all listed (`stay_test.EXIT_COSTS`, `NOT_REMOVED`):

| Cost | Where in the code | Removed in the replay? |
|---|---|---|
| bind: stay commitment, a hard wall below the breach load N < 0.2 | `WeeklyWorld.commit_decide`, `breaks`, `BREACH_N` | yes ("bind"; the breach load is the bind's threshold) |
| rule: cards on `leave` the gate enforces (trap T1-forfeit; negotiated exit terms N5a/N5b) | `PyGate.check` via `decide` | yes ("rule") |
| sanction: a standing `suspend` sanction blocks leave | `decide`, `SUSPEND_ALLOWS` | yes ("sanction") |
| forfeit: breach forfeit of the carry-out, and the trust drop on a breach | `WeeklyWorld.breach`, `breach_forfeit`, `TRUST["breach_drop"]` | yes ("forfeit"); expected inert in the behavioral lens because the agent does not weigh it |
| 1.5 extra living cost alone | `step_week` | no: part of the outside option, not an exit cost |
| request fine N8-fine-some | `WeeklyWorld.fine` | no: request breaches only |
| vetoes and bound requests | `decide`, `BOUND_BLOCKS` | no: they block contact and spending, not leaving |

## Design

- World: weekly household world, 156 weeks, the common shock schedule. Hedonic model, negotiation and world used read-only. The stay test plays the same weeks as an untested run (a test checks that the fact is unchanged).
- Arms (`scripts/stay_test_run.py`):
  - `v22_bindable`: the author's confirmed seed v2.2, bindable variant, negotiation v2.1 protocol (fair default, exit floor on, a failed negotiation means living apart, reviews and retries every 13 weeks). The pleasure demonstration's set-up.
  - `v22_free_exit`: the confirmed free-exit variant, same protocol.
  - `v22_locked` (stronger exit cost): week-0 negotiation as in bindable, then a mutual stay commitment for the whole run with full breach forfeit imposed, terms frozen (no reviews). Pots formed later by a retry are locked when they form.
  - `v22_locked_hard` (stronger exit cost): `v22_locked` with a breach load of 0.5 instead of 0.2 (ASSUMED).
  - `trap` (strong exit cost, imposed fixture): T1 forbids any take above 0 while the pot is not empty, and the agent only asks for 50, 25 or 12 percent, so it is a wall.
  - `baseline` (exit-cost control, imposed fixture): even exit split, no wall.
  - The author's seed files are not modified. The locked arms change the deal and the breach load inside the run script only.
- Pairings: the 57 of the pleasure demonstration (15 hand pairs, 42 ordered pairs with a pressing persona).
- **Unit of resampling: the pairing**, its seeds clustered together. Shares are ratios of summed weeks; intervals are percentile bootstraps resampling whole pairings (`stay_test.ratio_ci`, 4000 draws). Paired comparisons use pairing-level shares, over the pairings that have staying weeks in both arms (households that never form have none).
- Fixed and ASSUMED: every hedonic, trust and world constant; the leave rule; the breach load 0.2 (code) and 0.5 (locked_hard only); persona weights. "Low" partner-week: pleasure below the 25th percentile of all staying partner-weeks of `v22_bindable` (computed in the run). "Falling": the mean of the last 4 staying weeks is at least 0.05 below the mean of the 4 before.
- Seeds: 0 to 9 (10 per pairing), from the power check. 57 x 6 x 10 = 3420 runs. Each run clears the negotiation rollout caches first.

## Exploratory pilot (EXPLORATORY; not a result; changes no threshold after this commit)

Disclosure: the pilot ran the real configuration (all six arms, 57 pairings) on seeds 900 and 901, before this prereg, to get spreads for the power check. It is excluded from the confirmatory data. After seeing it, two definitions were changed before this commit: (1) the bar lens's cost-free holdings had used the whole pot (a bug: removing a cost should give at least the equal half, not everything); fixed to max(equal half, best permitted carry); the pilot's bar numbers are therefore biased toward "held". (2) "Falling" was tightened from a drop of 0.02 to 0.05, because 0.02 marked about 45 percent of all partner-weeks as low or falling. Also smoke-run on toy fixtures in tests/test_stay_test.py.

| Quantity (pilot, seeds 900-901) | Estimate [95% CI, pairing bootstrap] | Pairing-level sd |
|---|---|---|
| held share, trap | 0.703 [0.626, 0.777] | 0.272 |
| held share, v22_bindable | 0.000 [0.000, 0.000] (0 of 8245 staying weeks) | 0 |
| held share, v22_free_exit | 0.009 [0.000, 0.030] (73 weeks, one pairing, cause "rule") | 0.134 |
| held share, v22_locked | 0.001 [0.000, 0.002] | 0.004 |
| held share, v22_locked_hard | 0.004 [0.002, 0.006] | 0.048 |
| held share, baseline | 0.000 | 0 |
| trap minus bindable, paired (39 pairings) | +0.779 | 0.210 |
| locked_hard minus bindable, paired (39) | +0.024 | 0.048 |
| locked minus bindable, paired (39) | +0.0007 | 0.004 |
| pair pleasure, trap, worth weeks / held weeks (pooled) | 0.821 / 0.774 | |
| same, within-pairing difference worth minus held (57) | -0.025 | 0.060 |

The pilot shows a reversal risk for P7: pooled over weeks, held weeks have lower pleasure, but within a pairing they have slightly higher pleasure. P7 is written on the pooled quantity, as ADR 0018 states it ("the pleasure of each group"); the within-pairing difference is reported beside it as a secondary line.

The free-exit "rule" holds come from the negotiated "proportional" exit term: its card forbids leaving with less than 100 percent of what one put in, and the agent never asks for 100. That is an artifact of the agent's fixed take menu, recorded now so it is not read later as a finding about free exit.

## Power check

`mar.stats.seeds_for_power(effect - margin, sd, paired=True)` (simulated) and `seeds_for_margin` (closed form), units = pairings with staying weeks in both arms (39 of 57 in the pilot for the v2.2 arms, 57 for trap).

| Prediction | Margin | Spread used | Pairings for 80% power | Pairings available | Seeds chosen |
|---|---|---|---|---|---|
| P2 trap held share vs 0.50 | 0.50 | 0.272 | 14 | 57 | 10 |
| P3 trap minus bindable | 0.40 | 0.210 | 6 (closed form 3) | about 39 | 10 |
| P5 locked_hard minus bindable | 0.001 | 0.048 | 38 (closed form 36) | about 39 | 10 |
| P6 locked minus bindable, below 0.005 | 0.005 | 0.004 | about 8 | about 39 | 10 |
| P7 trap pleasure, worth minus held | 0.02 | pooled; cluster bootstrap | n/a | 57 | 10 |

P5 is at the edge: 38 needed with about 39 available. Ten seeds (instead of two) should shrink the pairing-level spread, which is the reason for 10. If fewer than 38 pairings have staying weeks in both arms, P5 is reported as DESCRIPTIVE. Cost: about 65 minutes on 8 workers, no money.

## Predictions

Holm family: P2, P3, P4, P5, P6, P7, P9a, P9b. Alpha 0.05. "Holds robustly" needs the point estimate, the 95% interval and the Holm-adjusted p all on the right side.

| ID | Quantity | Unit | Threshold | Test | Interval |
|---|---|---|---|---|---|
| P1 | held share, baseline (sanity control) | run | exactly 0 | deterministic, no test (not testable) | none |
| P2 | held share, trap | pairing | >= 0.50 | one-sided sign-flip permutation of pairing shares minus 0.50 | ratio, pairing bootstrap |
| P3 | held share, trap minus v22_bindable | pairing, paired | >= 0.40 | one-sided paired permutation | pairing bootstrap of the paired mean |
| P4 | held share, v22_bindable (the confirmed seed passes test 2) | pairing | <= 0.02 | one-sided permutation, pairing shares minus 0.02 below 0 | ratio, pairing bootstrap |
| P5 | held share, v22_locked_hard minus v22_bindable | pairing, paired | >= 0.001 | one-sided paired permutation | pairing bootstrap |
| P6 | held share, v22_locked minus v22_bindable (a bind at the code's breach load holds almost nobody) | pairing, paired | <= 0.005 | one-sided paired permutation, below | pairing bootstrap |
| P7 | pair pleasure in worth-it weeks minus held weeks, trap, pooled over weeks | pairing (cluster) | >= 0.02 | one-sided: share of pairing-bootstrap draws <= 0.02 as p | pairing bootstrap |
| P8a | among held low-or-falling partner-weeks in trap, share whose cause is "rule" | pairing (cluster) | >= 0.95 | interval only (lower bound >= 0.95 for robust) | pairing bootstrap |
| P8b | among held low-or-falling partner-weeks in v22_locked_hard, share whose cause includes "bind" | pairing (cluster) | >= 0.80 | interval only | pairing bootstrap |
| P9a | bar lens worth share, v22_bindable | pairing (cluster) | >= 0.50 | one-sided, bootstrap p | pairing bootstrap |
| P9b | bar lens worth share, trap | pairing (cluster) | <= 0.25 | one-sided, bootstrap p | pairing bootstrap |

Effect sizes: paired differences with intervals; Cliff's delta for P3, P5, P6.

Also reported, no verdict: worth share (1 minus held) and pleasure per group for every arm; v22_free_exit held share and cause; the bar-leave share (the bar would say leave, the code keeps them) per arm; the within-pairing pleasure difference for P7; breaches and exits per arm.

## Verdict rule

The measure **separates** iff P1, P2 and P3 hold. The confirmed seed **passes test 2 in this model** iff P4 holds. P5 and P6 together say whether a bind can hold anyone at the code's breach load. P7 says whether held weeks are worse weeks. A "holds but CI crosses threshold" is weak support, not a hold.

## Not testable by design

P1 (the replay of a world with no exit cost is the fact, by construction). The unit tests: zero-cost world gives held share 0; a constructed bind-only case and a rule-only case are flagged with the right cause; the forfeit alone never flips the behavioral lens; the fact is unchanged by the test.

## Limits stated now

- **The contact veto is inert** (docs/results/fidelity.md, P5): trap and contact_free give identical weeks. Isolation as an exit cost (cutting outside ties lowers the outside option) cannot operate here, so "held by isolation" is not measurable here. The trap's held share comes from its forfeit wall, not from isolation.
- **No outside option in the leave decision.** The behavioral lens has no outside option at all: a partner who is not distressed never considers leaving, however good the outside is, and a distressed one leaves however bad it is. So "worth it" in the primary lens means "not distressed enough to want out", not "better than the alternative". The bar lens supplies the comparison but is not acted on by the code. The fidelity finding that outside options shape whether a household forms, not its terms, also means the bar lens mostly reads the same few values.
- The forfeit is invisible to the agent, so the behavioral lens will attribute nothing to it by construction.
- Scripted agents, a fixed take menu (50, 25, 12), one parameter point, assumed thresholds.

## Amendments

None yet.
