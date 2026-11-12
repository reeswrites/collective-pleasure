# Performance of the household simulator

Status 2026-11-12. Written by an agent at the author's request ("profile the simulator after the current run"). Part 1 is the profile. Later
sections record each speedup made, its proof that outputs did not move, and before/after timings on the same workloads.

**Hard rule kept throughout: outputs are byte-identical.** Every change below was checked against every pinned fingerprint in
tests/data/*fingerprints*.json (observer off and on, makers off and flat-cost, agent values v1 and v2 with and without bills, H38 pairing
off, levers off, the retest cells) and against a wider set of full-output digests taken from the code before any change (see "How identity
was checked"). A speedup that would move any output was not made; it is listed under "Proposals not made".

## 1. Where the time goes

Machine: the author's Mac (8 cores: 4 performance, 4 efficiency), Python 3.14, one process. Profiled with cProfile (py-spy is not
installed). cProfile inflates small, frequent calls, so the shares below are a guide to where time goes, not exact wall-clock splits.

Workloads (all at the fixed seeds of the pins, pair p-anchor / p-host, seed 0, the full 156-week life):

- **h38_L0, h38_L4**: one H38 run (scripts/h38_pairing_run.py `play`, stay readings on, the old rule) at dial 0 and 4.
- **fc_L4**: one formation-check run (the corrected rule: decide on pleasure, 52-week windows), dial 4; **fc_L4_v2b** the same under
  agent_values v2b with bills that hurt.
- **makers_M0**: one H39b makers run (arm M0, opportunity choice; scripts/h39b_makers_rerun.py), and **makers_M0_v2b** under v2b.
- **vc_v1, vc_v2b**: one value-consistency pair (scripts/value_consistency.py `run_pair`, 2 sampled weeks, k = 2; the v2b run uses the
  four horizons 1, 4, 13, 52).
- **ef_items**: one exit-fallback run with items (F4, items V2; exit_fallbacks_run.play_items).

Plain wall time per run (one process, before any change): h38_L0 1.6 s, h38_L4 1.9 s, h38_L4 under v2 2.1 s and under v2b 3.9 s;
fc_L0 2.8 s, fc_L4 3.5 s, fc_L4 v2 3.3 s, fc_L4 v2b 7.3 s; makers_M0 1.5 s, v2 1.1 s, v2b 3.4 s; vc v1 1.5 s, v2 2.2 s, v2b 2.8 s;
ef_items 0.16 s.

### The shape of a run: most simulated weeks are rollouts

A lived H38 run plays 156 weeks. At each 13-week reading (11 of them while both are in), the stay lens and the reading together play:

| what | rollouts per reading | weeks each | simulated weeks in one h38_L4 run |
|---|---|---|---|
| the lived run itself | | | 156 |
| status-quo rollout, stay lens (`NG.forward_values`) | 1 | 26 | 286 |
| status-quo rollout, the reading (`NG.forward_values`) | 1 | 26 | 286 |
| pressure-off rollout, stay lens (`pairing._forward`) | 1 | 26 | 286 |
| outside rollouts (`NG.alone_value`: alone and with Friend C, each member, with and without pressure; cached) | up to 8 | 26 | 2,210 (84 played) |
| **total** | | | **3,224** |

So one lived week costs about 20 simulated weeks. Under the corrected rule (52-week windows) the rollouts double (fc_L4: 6,292 weeks). The
status-quo rollout of the stay lens and the one of the reading that follows it are the same computation: same world, same week, same
config (nothing changes the world between them). At dial 0 the pressure-off rollout is the same computation too (free(dial 0) is dial 0).

### Shares of total time (cProfile, cumulative, before any change)

| workload | total s (cProfile) | outside rollouts (alone_value) | status-quo rollouts (forward_values) | pressure-off rollouts (pairing._forward) | value-check branches | deep copies for rollouts | gate `eval` | agent_values v2 |
|---|---|---|---|---|---|---|---|---|
| h38_L0 | 5.0 | 22% | 42% | 22% | 0% | 14% | 20% | 0% |
| h38_L4 | 4.2 | 36% | 35% | 17% | 0% | 12% | 16% | 0% |
| fc_L4 | 9.2 | 40% | 35% | 17% | 0% | 7% | 18% | 0% |
| fc_L4_v2b | 16.7 | 48% | 30% | 15% | 0% | 3% | 9% | 39% |
| makers_M0 | 4.7 | 46% | 38% | 0% | 0% | 5% | 16% | 0% |
| makers_M0_v2b | 8.7 | 53% | 33% | 0% | 0% | 3% | 8% | 39% |
| vc_v1 | 4.3 | 18% | 10% | 0% | 62% | 2% | 24% | 0% |
| vc_v2b | 7.6 | 24% | 12% | 0% | 55% | 1% | 12% | 36% |
| ef_items | 0.5 | 0% | 0% | 0% | 0% | 0% | 4% | 0% |

The columns overlap (a rollout's time includes its gate evals and agent-value calls). The rest of each total is the lived run itself.
`WeeklyWorld.step_week` is 81 to 95% of every workload's time: everything is the weekly step, played many times.

### Top functions by own time

h38_L4 (v1 agents):

| function | own time share | what it is |
|---|---|---|
| builtins `eval` (from `PyGate._viol`) | 16% | each card condition is a Python expression string, compiled again at every check (165,666 calls per run) |
| `WeeklyWorld.state` | 6% | the gate's state dict, rebuilt at each check |
| `copy.deepcopy` (internals) | 9% | 33 deep copies of the whole world per run, each about 15 ms; each copy carries the full run log (every trace and outcome row so far), which the rollout never reads |
| `step_week`, `decide`, `utilities`, `check`, `step_agent`, `obs` | 2 to 4% each | the weekly step |

fc_L4_v2b (v2b agents): `agent_values._week_net` 16% own time (298,830 calls; about 8 per utilities call), builtins `eval` 9%,
`agent_values.snapshot` 4%, `hedonic.strand_cover` 4%, `WeeklyWorld.state` 4%, `agent_values._c01` 3%. v2b roughly doubles the cost of a
week against v1: the projected close is recomputed for every candidate action, twice more for the bill horizon's settlement credit.

### What the profile says about the suspected hotspots

- **Nested formation/stay rollouts** (src/mar/negotiation.py): yes, the biggest cost. Outside rollouts are 22 to 53% and status-quo plus
  pressure-off rollouts another 35 to 64% of the H38, formation-check and makers runs. One third of the status-quo rollouts are exact
  repeats (the reading replays the stay lens's), and at dial 0 two thirds are.
- **The observer's counterfactual replays** (src/mar/observe.py): not in any production workload. The observer is off in every experiment
  run; it costs only when attached (docs/notes/observer-schema.md has its own cost).
- **The value check's forks** (src/mar/valuecheck.py): 55 to 62% of a value-check pair. Each fork plays up to 52 weeks; the cost is the
  weekly step again, not the fork. The fork's deep copy is about 2%.
- **Deep copies of world state**: 3 to 14%. Each rollout copy also copies the run log, which grows through the run (late readings copy
  more than early ones).

## 2. What changed (each commit byte-identical)

| # | commit | change | where |
|---|---|---|---|
| 1 | c273638 | `PyGate` compiles each card condition expression once (a class-level cache of code objects) instead of `eval` recompiling the string at every check. Same evaluation: the compiled code is evaluated with the same empty builtins and the same env; leading blanks are stripped as `eval` strips them. | src/mar/worlds/household.py |
| 2 | 605e871 | Rollout copies without the run log: `negotiation.played_copy` deep-copies the world with a fresh `Run` (and no hook), as `observe` and `valuecheck` already did. The rollout reads only the weeks it plays, so the copy no longer carries every trace and outcome row so far. `forward_values` and `pairing._forward` both use it. | src/mar/negotiation.py, src/mar/pairing.py |
| 3 | 605e871 | `negotiation.forward_memo()`: inside the block, a rollout of the same world from the same week, for as many weeks, under an equal FixConfig and an equal `last`, is played once and its copy reused. Opened only in `h38_pairing_run.play` around the stay lens and the reading that follows it (nothing changes the world between them). The reading reuses the stay lens's status-quo rollout; at dial 0 the pressure-off rollout is the same one too. A rollout is deterministic given those inputs (the copy carries every random stream), so the reused copy is the one a second rollout would have played. `NG.STATS` still counts every rollout asked for, so the counters written into run rows do not move. H38, the formation check and H39/H39b all play through `h38_pairing_run.play`, so all get it. | src/mar/negotiation.py, scripts/h38_pairing_run.py |

### How identity was checked

Before any change, from the clean checkout (28e636e), a scratch script recorded:

- every pinned family: `agent_values_fingerprint` under v1, v2 + bills, v2, and (no pin exists yet) v2b + bills and v2b;
  `h38_fingerprint`; `makers_fingerprint` (makers off and flat-cost); `levers_fingerprint`; `observer_fingerprint` with the observer off
  and on (replays at rate 0.25). All matched tests/data/*fingerprints*.json before the change.
- full-output digests (every outcome row, trace row, final state, commit and fix reports, exit log, the stay readings, the reading and
  retry logs, the bar log, and the `NG.STATS` deltas) of: H38 at dials 0 and 4 and the formation check at dials 0 and 4 for three pairs,
  makers arms Z and M0 for three pairs, value-check pairs with and without the harness for two pairs, each under v1, v2 + bills and
  v2b + bills; three exit-fallback runs with items; and two H38 stay runs per agent version with an observer attached, digesting every
  observer row (this covers the rollout parts the observer records from the shared rollout).

After change 1 alone, and again after changes 1 to 3, every group was byte-identical to the before digests. The targeted tests
(test_household_weekly, which checks PyGate against the z3 gate; test_pairing; test_formation_check; test_negotiation_v2; test_observer;
test_valuecheck) pass, and the full suite passes before the push.

### Before and after, one process, same workloads

| workload | before s | after 1 s | after 1-3 s | speedup |
|---|---|---|---|---|
| h38_L0 | 1.63 | 1.10 | 0.64 | 2.5x |
| h38_L4 | 1.92 | 1.33 | 1.07 | 1.8x |
| h38_L4 v2 + bills | 2.14 | 1.80 | 1.61 | 1.3x |
| h38_L4 v2b + bills | 3.92 | 3.27 | 2.80 | 1.4x |
| fc_L0 | 2.85 | 1.79 | 1.06 | 2.7x |
| fc_L4 | 3.52 | 2.39 | 1.99 | 1.8x |
| fc_L4 v2 + bills | 3.33 | 2.83 | 2.53 | 1.3x |
| fc_L4 v2b + bills | 7.24 | 6.23 | 5.28 | 1.4x |
| makers_M0 | 1.47 | 1.08 | 1.04 | 1.4x |
| makers_M0 v2 + bills | 1.11 | 0.99 | 1.02 | 1.1x |
| makers_M0 v2b + bills | 3.28 | 2.91 | 2.94 | 1.1x |
| vc v1 | 1.46 | 0.89 | 0.93 | 1.6x |
| vc v2 + bills | 2.28 | 1.99 | 2.01 | 1.1x |
| vc v2b + bills | 2.83 | 2.33 | 2.37 | 1.2x |
| ef_items | 0.08 | 0.07 | 0.07 | 1.1x |
| **all 15** | **39.1** | **31.0** | **27.3** | **1.4x** |

Single runs, so differences under about 5% are noise. The makers and value-check runs play no stay lens, so change 3 does not reach them.

Under v2 and v2b the agents' own arithmetic is now the largest cost (about 40% of a v2b run): `agent_values.utilities` recomputes the
projected week close (`_week_net`) about 7 times per agent step, once per candidate action and twice more for the bill horizon. The
gate eval that change 1 removed was a larger share of a v1 week than of a v2b week, which is why v1 gains most.

### Parallel throughput (H38 tasks, one seed each, alternating L0 and L4, 48 tasks)

| tree | workers | wall s | runs per second |
|---|---|---|---|
| before | 3 | 24.1 | 2.0 |
| after | 1 | 34.5 | 1.4 |
| after | 3 | 12.6 | 3.8 |
| after | 4 | 10.0 | 4.8 |
| after | 6 | 8.8 | 5.4 |

The machine has 4 performance cores. A fourth worker adds about 25%; workers 5 and 6 land on efficiency cores and add about 13% more
together (each task runs about a third slower there).

### Expected wall time for a typical 6,000-run experiment (3 workers)

The 6,720-run experiment that took about an hour on 3 workers was about 1.6 s per run per worker. After these changes:

- v1 agents, stay readings on (H38, the formation check's old-rule and corrected-rule arms): about 1.8 to 2.7x faster, so about 25 to 35
  minutes instead of an hour.
- v2b agents with stay readings (the formation check under v2b): about 1.4x, about 45 minutes.
- v2/v2b makers or value-check runs (no stay lens): about 1.1 to 1.2x, about 50 to 55 minutes.

With 4 workers instead of 3, take a further fifth off each.

## 3. Proposals not made, and why

Ranked by expected gain, then risk.

1. **Worker cap 3 -> 4** (gain about 25% on any experiment, no output risk). Not changed: the cap is a policy for a shared machine
   (other agents and the author's own work), not a code question. When the machine is free, 4 is the sweet spot; 6 adds little more.
2. **Faster v2/v2b agent arithmetic** (gain estimated 10 to 15% of a v2b run, low output risk but a readability cost). `_week_net`
   mirrors the hedonic close line by line on purpose ("same arithmetic"); inlining `_c01` (about 21 calls per evaluation, 3 million per
   run), hoisting the config lookups, and computing the partner's base close once per call would keep every float operation in the same
   order. Not made: the mirrored form is what lets a reader check it against `Hedonic.close_week`, and the gain is modest. Worth doing
   if v2b stays the main agent model and runs stay long.
3. **Caching outside rollouts across runs** (gain about 5%: the four week-0 outside rollouts and the baseline rollout of each run). Not
   made: the caches are cleared at every run because their keys round the hedonic state (B and N to 0.1), so a cached value is the
   first caller's. That is exact only for the week-0 calls (no hedonic state), and the key would also need the lever, exit-fallback,
   items and makers contexts it now omits. Small gain, real risk of a stale hit.
4. **Shortening rollouts** (gain up to 2x on rollout-heavy runs). Not made: any shorter window changes the values recorded in the
   reading logs and so the outputs, even where no decision flips. It would need its own preregistered check that no decision changes,
   and new pins.
5. **Pressure-invariant outside rollouts** (would halve the outside rollouts of the stay lens). Not possible exactly: the stigma part
   applies to a member living alone, so the pressure-off outside rollout really differs.
6. **NumPy or Numba for inner loops.** Not made: the weekly step is branchy dict-and-object code with many small decisions, not array
   arithmetic; the profile has no vectorizable loop. Numba would need the world rewritten into typed arrays, which is a rewrite, not a
   speedup.
7. **Copy-on-write world state.** Not made: after change 2 the deep copies are 1 to 5% of a run; copy-on-write would touch every
   mutation site in the world for that.

## 4. What else would help

- **Smaller pilots.** A pilot exists to find a broken arm or to size the main run. Piloting the extreme arms only (for example dial 0 and the
  top level) under one agent version cuts it by more than half; the middle arms rarely break when the ends work.
- **Order tasks longest first.** Tasks under v2b with stay readings take about 5x a v1 makers task; queueing the slow arms first avoids a
  long tail where one worker finishes alone.
- **The value check's horizons.** Each sampled decision forks up to 52 weeks per candidate action; the fork count, not the fork's copy, is
  the cost. Fewer sampled weeks per pair with more pairs gives the same number of decisions at the same cost, but more independent ones.
