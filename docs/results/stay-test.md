# Stay test: results (ADR 0018 test 2, "worth it vs hard to leave")

Prereg: docs/results/stay-test-prereg.md, committed (c8bef76) before the confirmatory run started. The exploratory pilot (seeds 900 and 901) ran before the prereg and is disclosed there. No prediction was changed after the run. Run: `uv run python scripts/stay_test_run.py --run --seeds 10` then `--analyze` (3420 runs, 44 minutes on 8 workers, no model calls). Per-run outputs: runs/stay-test/results.json.gz (git-ignored). Summary numbers: experiments/kept/stay-test-2026-11-10/results.json. Code: src/mar/stay_test.py, tests/test_stay_test.py.

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state (ADR 0010).

## What the measure does

For every week a pair stays together, the week is replayed with every exit cost removed (the stay bind with its breach load, rule cards on leaving, a suspend sanction, the breach forfeit). If a partner leaves in the replay but not in fact, that week is "held by cost". Otherwise it is "worth it". Then each cost is removed alone to name the one that holds them.

The code's real stay bar is not the ADR's max(outside option, status-quo value). In this code that bar only sets terms at the 13-week reviews and never ends a household. A partner leaves only when distressed (4 low weeks, non-offsettable load at 0.2, or trust below 0.15), and the world carries it out unless something blocks it. So the primary lens replays that decision. A second lens reads the ADR's bar every 13 weeks, as "what the bar would say".

## Headline numbers (57 pairings x 10 seeds per arm, 95% CI resampling whole pairings)

| Arm | Staying weeks | Stay-worth-it share | Stay-held-by-cost share | Pleasure, worth-it weeks | Pleasure, held weeks | Held cause |
|---|---|---|---|---|---|---|
| v22_bindable (confirmed seed) | 43677 | 0.985 [0.946, 1.000] | 0.015 [0.000, 0.054] | 0.861 [0.850, 0.872] | 0.630 [0.559, 0.630] | rule (one pairing, see below) |
| v22_free_exit | 44087 | 0.979 [0.941, 1.000] | 0.021 [0.000, 0.059] | 0.861 [0.849, 0.872] | 0.625 [0.595, 0.752] | rule |
| v22_locked (stronger cost) | 43015 | 1.000 [0.999, 1.000] | 0.0003 [0.000, 0.001] | 0.861 [0.849, 0.872] | 0.549 [0.505, 0.685] | bind |
| v22_locked_hard (stronger cost, breach load 0.5) | 43797 | 0.996 [0.994, 0.998] | 0.004 [0.002, 0.006] | 0.861 [0.849, 0.872] | 0.647 [0.594, 0.714] | bind (126), joint (13) |
| trap (strong cost, imposed) | 46161 | 0.267 [0.208, 0.328] | 0.733 [0.672, 0.792] | 0.823 [0.800, 0.843] | 0.770 [0.740, 0.797] | rule (all) |
| baseline (no exit cost, control) | 43583 | 1.000 | 0.000 | 0.854 [0.840, 0.865] | not measurable here (no held weeks) | none |

Dissolution analysis (partner-weeks that are low, below 0.792, or falling by 0.05 over 4 weeks):

| Arm | Low or falling partner-weeks | Share held by cost | Which cost |
|---|---|---|---|
| v22_bindable | 29481 | 0.033 [0.000, 0.107] | rule 973, bind 1 |
| v22_free_exit | 30096 | 0.045 [0.000, 0.120] | rule 1353 |
| v22_locked | 28332 | 0.0005 [0.000, 0.001] | bind 14 |
| v22_locked_hard | 29049 | 0.005 [0.003, 0.008] | bind 126, joint 13 |
| trap | 47654 | 0.715 [0.646, 0.774] | rule 34069 |
| baseline | 29758 | 0.000 | none |

Bar lens (every 13 weeks while both are in; share of pair-readings):

| Arm | Worth (SQ >= O_free) | Held (O_cost <= SQ < O_free) | Bar would say leave (SQ < O_cost) |
|---|---|---|---|
| v22_bindable | 0.710 [0.619, 0.788] | 0.000 [0.000, 0.001] | 0.290 [0.211, 0.381] |
| v22_free_exit | 0.702 [0.611, 0.780] | 0.000 [0.000, 0.001] | 0.297 [0.220, 0.389] |
| v22_locked | 0.712 [0.619, 0.787] | 0.027 [0.017, 0.038] | 0.261 [0.190, 0.350] |
| v22_locked_hard | 0.712 [0.617, 0.788] | 0.027 [0.017, 0.037] | 0.262 [0.189, 0.353] |
| trap | 0.087 [0.050, 0.125] | 0.008 [0.004, 0.012] | 0.905 [0.865, 0.943] |
| baseline | 0.595 [0.468, 0.708] | 0.000 | 0.405 [0.292, 0.532] |

## Verdicts against the prereg

Holm family P2 to P7, P9a, P9b. One-sided tests. "Holds robustly" needs the point, the 95% interval and the Holm p on the right side.

| ID | Quantity | Threshold | Estimate [95% CI] | Holm p | Verdict |
|---|---|---|---|---|---|
| P1 | held weeks, baseline (control) | exactly 0 | 0 | n/a | pass (not testable, deterministic) |
| P2 | held share, trap | >= 0.50 | 0.733 [0.672, 0.792] | 0.0004 | **holds robustly** |
| P3 | trap minus v22_bindable, paired (48 pairings) | >= 0.40 | +0.691 [0.607, 0.769], Cliff's delta 0.72 | 0.0004 | **holds robustly** |
| P4 | held share, v22_bindable | <= 0.02 | 0.015 [0.000, 0.054] | 1.0 | holds but CI crosses threshold (weak) |
| P5 | v22_locked_hard minus v22_bindable, paired (48) | >= 0.001 | +0.0004 [-0.041, +0.030] | 1.0 | **miss** (CI crosses) |
| P6 | v22_locked minus v22_bindable, paired (48) | <= 0.005 | -0.018 [-0.057, +0.005] | 0.003 | **holds robustly** |
| P7 | trap pleasure, worth-it minus held weeks, pooled | >= 0.02 | +0.053 [0.031, 0.075] | 0.005 | **holds robustly** |
| P8a | trap: held low/falling weeks caused by rule | >= 0.95 | 1.000 [1.000, 1.000] | interval only | **holds robustly** |
| P8b | locked_hard: held low/falling weeks caused by bind | >= 0.80 | 0.906 [0.769, 1.000] | interval only | holds but CI crosses threshold (weak) |
| P9a | bar worth share, v22_bindable | >= 0.50 | 0.710 [0.617, 0.788] | 0.0006 | **holds robustly** |
| P9b | bar worth share, trap | <= 0.25 | 0.087 [0.050, 0.126] | 0.0006 | **holds robustly** |

Verdict rule: the measure **separates** (P1, P2, P3 hold). The confirmed seed **passes test 2 only weakly** (P4 point under 0.02, interval up to 0.054). A bind at the code's breach load holds almost nobody (P6 holds), and raising the breach load did not separate from the confirmed seed (P5 missed).

## Honest misses and surprises

- **P5 missed, and the reason is a confound in the comparison, not a clean null.** v22_locked_hard does hold some partners by its bind (0.004, with an interval that excludes 0). But v22_bindable's own held share (0.015) is larger, and it comes from somewhere else entirely, so the paired difference is about zero. The bindable comparison arm was not a zero-cost baseline, which the prereg assumed it would be (the pilot showed 0 held weeks for it).
- **All of the confirmed seed's held weeks come from one pairing and one artifact.** 675 of 676 held weeks are Steward with Controller. Their reviewed bundle switched to the "proportional" exit term, whose card forbids leaving with less than 100 percent of what one put in. The scripted agent only ever asks for 50, 25 or 12 percent, so a distressed Steward cannot leave at all. Free-exit shows the same artifact (three pairings). This is the take-menu artifact the prereg named in advance. It is a property of the agent, not of the seed's words. The fix would be an agent that asks for what the terms allow. Until then, the seed's held share is an upper bound set by one agent quirk. Without that pairing it would be about 0.
- **The locked arms barely hold anyone.** A whole-run stay commitment with full forfeit held 14 staying weeks out of 43015 at breach load 0.2, and 163 at 0.5. The leave rule fires mostly when the non-offsettable load reaches 0.2, which is exactly where the bind breaks, so the bind rarely stands between a distressed partner and the door. This repeats the seed v2 null (results row 13) by a different method. Breaches did happen (140 and 129 breached stay commitments).
- **P7 holds pooled, but reverses within a pairing.** Pooled over weeks, trap households have lower pleasure in held weeks (0.770) than in worth-it weeks (0.823). Within one pairing, held weeks have slightly higher pleasure (worth minus held -0.019 [-0.032, -0.005], 57 pairings). The pooled gap is a composition effect: pairings that spend more weeks held are the less pleasant ones. The prereg flagged this risk and kept the pooled quantity, as the ADR words it.
- **The bar says "leave" far more often than anyone leaves.** Under the confirmed seed the bar would say leave in 29 percent of review readings, and under the baseline 41 percent, but very few households end. The code never acts on the bar.
- A side finding in shared code (not changed here): `WeeklyWorld.apply` logs `breach` on an exit from `cand.get("breach")`, but `WeeklyWorld.breach` never sets that key, so `exit_log[...]["breach"]` is always False. Breaches are counted here from the commitments' `breached` field instead.

## Do the known limits weaken the test?

- **The inert contact veto (fidelity P5).** It weakens one channel, not the measure. Isolation, cutting outside ties so leaving looks worse, is the classic way a relationship holds people by cost. Here a veto on contact changes nothing for scripted agents, so "held by isolation" is not measurable here, and a rule set that isolates would pass test 2. The trap's 0.73 comes entirely from its forfeit wall (P8a: all "rule"). So a pass on test 2 in this world says nothing about isolation.
- **No outside option in the decision to leave.** This is the bigger limit. In the primary lens "worth it" means "not distressed enough to want out", not "better than the alternatives". A partner with a much better life outside but no distress counts as staying because it is worth it. The bar lens fills the gap on paper, and it does separate the trap (0.09 worth) from the seed (0.71). But it is never acted on, so it describes what a value-comparing partner would do, not what happens. And because the exit floor tops up any carry, O_cost and O_free are nearly equal under v2.2 (bar "held" about 0.000): in this model the floor removes the money side of the exit cost almost completely.
- The forfeit is invisible to the agent, so the behavioral lens can never blame it, by construction. It shows up only in the bar lens (the locked arms' 0.027).

## Plain-English reading

The test works as a separator. When leaving means losing everything (the trap), about three in four weeks of staying together are kept by that cost, and those weeks are less pleasant on average. When there is no cost (the baseline), none are. Under the author's confirmed seed, about 98.5 percent of staying weeks look worth it. The other 1.5 percent come from one couple who are stuck by a quirk: their agreed exit terms say "take all you put in", and the simulated person only knows how to ask for half or less. A stay commitment, even a whole-run one with full forfeit, keeps almost nobody here, because the simulated people only try to leave when things are already bad enough to break the commitment. Two things this test cannot see in this world: being kept by isolation (cutting someone off from friends does nothing to these agents), and staying out of habit when life outside would be better (no one here compares their life with the alternatives before deciding to leave).

## Evaluator lines for seed v2.2 (ADR 0018 format)

- Stay-worth-it share: 0.985 [0.946, 1.000]. Stay-held-by-cost share: 0.015 [0.000, 0.054] (one pairing, take-menu artifact).
- Pleasure, worth-it weeks: 0.861 [0.850, 0.872]; held weeks: 0.630 [0.559, 0.630].
- Held by isolation: not measurable here. Held by better outside options ignored: not measurable here in the primary lens; the bar lens says 0.29 of readings would leave.
- Reading: v2.2 passes test 2 weakly in this model; the trap fails it.
