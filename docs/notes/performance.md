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
