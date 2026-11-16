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

## 5. The hybrid agent (2026-11-16)

Written by an agent at the author's request (a speed-up pass on the hybrid; outputs byte-identical; never fewer rollouts or futures, never
a different number or order of random draws). Same machine, Python 3.14, one process per workload.

### Workloads

- **b_a6, b_tt**: one H41 life, arm B, pair g-01011 / p-peacekeeper (the median B life of the A6 and TT runs), seed 0, under A6's flags
  and under the time-together flags (scripts/hybrid_leaving.py `cfg_task`, as `--run` plays it).
- **lat_tt**: the same pair in the LAT arm under TT. **p2_tt**: the same pair in P2 under TT (a pressure arm: the stay lens adds a
  pressure-off rollout, so a P life costs about twice a B life).
- **pth_tt**: one PT-H audit unit (scripts/hybrid_passtest.py `play`, G-L0, the first pairing of A1's sample, TT's flags).
- **kx2_tt**: one KX2 unit (hybrid_leaving `_kx2_one`, TT flags, exit option on, exit cost 0.04, the first control pairing, seed 900).

### Where the time goes

cProfile (b_tt, 48.5 s under the profiler for a 22 s life) and, because cProfile inflates small frequent calls, an in-process stack
sampler (a thread reading the main thread's frame every 0.5 ms; py-spy needs root on macOS and was not installed):

| where (inclusive share of the b_tt life, sampled) | share |
|---|---|
| the weekly step (`WeeklyWorld.step_week`), lived and simulated | 98% |
| sampled futures (`hybrid._forecast`: status quo, return, lone readings, `lived_outside`) | 83% |
| outside options (`hybrid.outside_value`), of which solo/friend rollouts (`negotiation.alone_value`) 39%, `lived_outside` 30% | 70% |
| `default_ref` (the anchors of in-future readings: each member's outside option, valued again for every forecast no choice set) | 60% |
| the stay lens (`h41_choice_aids.stay_reading`) | 55% |
| the agents' choice (`step_agent`), of which utilities 38%, `obs` 23% (the agent-values snapshot 12%), `decide` 6% | 74% |
| the projected close (`agent_values._week_net`, about 6 calls per agent step) | 30% |
| liberty measured at weeks 0 and 52 (`h38_pairing_run._liberty`) | 4% |
| deep copies of world state | under 1% |

One b_tt life steps 20,332 simulated weeks for its 156 lived ones (about 130 per lived week): 196 sampled futures, 192 solo/friend
rollouts (704 asked for; the rest are cache hits) and 84 `lived_outside` valuations. Every one of them is the full two-agent weekly step,
and under the hybrid every agent step projects this week's close about six times (`utilities`). There is no single hotspot: the most
expensive function (`_week_net`) is 16% of own time, and nothing else is above 6%.

Rollouts that repeat exactly: a scratch check hashed every future's full starting world (after copy, option edit and reseeding) with its
week, seed, length, `last` and anchors. In b_tt 16 of 196 futures (8%) and in p2_tt 16 of 304 (5%) start from a state already played in
the same life, all of them inside `lived_outside` called outside a `forward_memo` block. Deep copies: under 1% (the hybrid's
`copy_world` already leaves the run log out).

The 6-hour figure and the long lives in the rows: the TT rows record lives of up to 14,000 s (P1, g-10010 / p-steward). Replayed alone
that life takes 32 s. The recorded seconds are wall time and include stalls (the machine sleeping, or other jobs): the 960-life TT run
took 61,053 s of wall time (17 h) on 4 workers, against about 4.5 h of compute. Without the stalls, the rows give 19.3 CPU-hours for
the 1,320-life A6 run and 22.2 for TT (each life over 5x its arm's median counted at the median): 4.8 h and 5.6 h on 4 workers.

### What changed (each commit byte-identical)

| # | commit | change | where |
|---|---|---|---|
| 1 | 90cb4ab | `_week_net` writes each clip to [0, 1] inline as `_c01` computes it and unrolls the condition loop in the close's order. Every float operation is the one it was, in the same order. | src/mar/agent_values.py |
| 2 | 8d8e0c3 | `hedonic.strand_cover_terms`: the strand cover and its (pay, suffering) memoized by (q0, bond qualities, strand sets), checked against the same levers object. Both are pure functions of those inputs. Used by the world's lever terms and the agent's projected close. | src/mar/hedonic.py, agent_values.py, worlds/household.py |
| 3 | 5926b20 | `step_agent` reads the gate state once for all candidates instead of once per candidate (`decide` and `sanction_cost` change nothing between them). | src/mar/worlds/household.py |
| 4 | 25c851b | The projected close memoizes its contact term and bought pleasure per snapshot, by the only inputs an advanced copy of the snapshot changes (contacts and partner sessions; money spent), shared by the copies as the strand memo already was. | src/mar/agent_values.py |

### How identity was checked

Before any change, from the clean checkout (058edc7), a scratch script recorded 145 full-output digests, each unit in a fresh process:

- H41 lives (hybrid_leaving `cfg_task`'s record without `secs`, plus hashes of every outcome row, trace row, final state, fix report,
  exits, stay readings, the lived reading log, retries, lone log, exit log, tally log, liberty, and the `HY.STATS` and `NG.STATS`
  deltas) under five hybrid configurations: the pre-A4 hybrid ("old", Amendment 3's flags), A4, A5, A6 and TT; arms B, P2, trial, lat
  and all; four units each (g-01011 / p-peacekeeper at seeds 0 and 1, two more pairings at seeds 0 and 2). 100 lives.
- PT-H audit units (the record without `secs`, including every audited choice): G-L0 under TT and under A6 for two pairings, G-L4 under
  TT for one.
- KX2 units: flags A4, A6 and TT, exit option off and on, exit cost 0 and 0.04, three control pairings (36 units).
- The formation check's world without the hybrid (FC3 `v2b`) and with it, G-L0 and G-L4 (outcomes, final, fix report, readings, log).

After changes 1 and 2, and again after 1 to 4, all 145 were byte-identical to the before digests. After change 1 and after 1 to 4, the 50
slow pins (`uv run pytest -m slow`) and the fast suite passed. Changes 2 to 4 were verified together and committed one by one (each is a
separate file region; the intermediate trees were not digested on their own).

### Before and after, one process per workload, two at a time, same machine

| workload | before s | after s | speedup |
|---|---|---|---|
| b_a6 | 21.8 | 19.6 | 1.11x |
| b_tt | 22.0 | 19.7 | 1.11x |
| lat_tt | 21.5 | 19.4 | 1.11x |
| p2_tt | 36.1 | 32.7 | 1.10x |
| pth_tt | 96.2 | 87.7 | 1.10x |
| kx2_tt | 2.2 | 1.9 | 1.12x |

Single runs; differences under about 5% are noise, but the gain is the same on every workload.

Projected full H41 run (1,320 lives, 4 workers, no stalls): A6 about 17.4 CPU-hours, **4.3 h** (was 4.8 h); TT about 20.0 CPU-hours,
**5.0 h** (was 5.6 h). The arms `all` and `info` are a third of it (100 to 130 s a life).

### Tried and dropped (no gain, so not committed)

- **Memoizing `PyGate.check`** by (kind, action, take, state). 80% of checks hit, and the outputs did not move, but the wall time did not
  move either: building the key costs about what evaluating the compiled card conditions costs. cProfile had overstated the gate.

### Proposals not made, and why

Ranked by expected gain, then risk.

1. **Keep the machine awake** (gain: the TT run's 17 h wall time against about 4.5 h of compute). `caffeinate -i` stops idle sleep only;
   it does not stop sleep on lid close or a sleep the user starts. `caffeinate -s` (system sleep, on AC power) or `-dimsu` keeps it
   up. Not changed: the queue scripts and the machine are the author's.
2. **Workers 4 -> 6** (about 13% more throughput, part 1's table). The cap is the author's policy for a shared machine.
3. **Order tasks longest first** (`all` and `info` lives take 4 to 5x a B life): avoids a tail where one worker runs alone. A change to the
   harness's task order, not to any output; not made because rows are appended in completion order and analyses key on (arm, a, b), so it
   is safe, but it is a harness change outside this pass.
4. **Solo rollouts step both twins** (`alone_value` is 39% of a life). The outside-option world plays the same persona in both roles and
   reads only one role's rows. Skipping the other role would roughly halve those rollouts, but nothing proves the two roles never interact
   in the world step (friend visits alternate by week, shared shock schedule), so the outputs could move. Needs a proof or a pin-checked
   model change, not a speed-up.
5. **Memo `lived_outside` across the whole reading, not only inside `forward_memo`** (5 to 8% of futures repeat exactly). Exact only if a
   hit also adds the counters a played valuation adds (`futures`, `future_weeks`, `future_exits`, `lived_outside`), which are written into
   rows; and the key would have to cover every global the forecast reads (`_REF`, `_OCTX`, `_NEUTRAL`). Gain about 5%; touches
   hybrid.py, which the next model change (gifts between partners living apart) edits. Left for after it.
6. **Stage the projected close** (compute rest, connection, money and aspiration terms once per snapshot and only the changed ones per
   action). `_week_net` is 30% of a life; this might take a third off it, but it splits a function that mirrors `Hedonic.close_week`
   line by line on purpose. Not made for readability.
7. **Caching outside rollouts across lives, fewer futures, shorter windows.** Rejected as before (part 3, items 3 and 4); fewer
   rollouts or futures is a model change the author ruled out.
