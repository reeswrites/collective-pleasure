# Correctness review, 2026-11-11

Seat: CORRECTNESS (fresh reviewer, no prior context). Reviewed commit: d321e01 (HEAD at review time). The H32 code is read as of its results commit f37a83a: `src/mar/convergence.py` was changed afterwards by H32b (27947c3), which says H32 reproduces exactly. Line numbers for `convergence.py` refer to f37a83a.

Scope:
- H32 (prereg, `convergence.py`, `runs/h32/results.json`)
- regulation (attune vs appease)
- pleasure levers
- H01 and H09
- the multiverse sweep (committed in 8233af1 and 75ae8e0)
- the IT1 correction (3a69d40: `docs/plans/inventive-seam-next.md`, `docs/negative-results.md` 2026-11-11 entry, `scripts/it1_seam_exists.py` against `src/mar/seam_depth.py` and `ladder_live.classify`)

Method. The machine was overloaded, so I reran no experiment script and not the full suite. Every headline number was recomputed by reading the saved JSON:
- `runs/h32/results.json`, which is byte-identical to the kept copy
- `runs/regulation/`, `runs/pleasure-levers/*.gz`, `runs/h01/`, `runs/h09/`, `runs/multiverse/`
- `runs/it1_seam_exists/{result,profit}.json`
- the kept ladder logs

Two small test files were run: `tests/test_multiverse.py` (11 passed) and `tests/test_h01_h09.py` (8 passed). A few tiny probes, not committed, were also run:
- two exact H32 solves, to trace the partner's estimate
- 14 single household worlds, to read H01 action traces
- 36 regulation pairings at seeds 0 to 2, to compute net pleasure. Seed-0 partner pleasure matched `results.json` exactly (116.51 / 114.54).

No model API calls.

Overall:
- Almost every number reproduces. No verdict label is wrong by its own rule.
- The problems are about what the verdicts can mean:
  - Two results contain an IT1-style flaw: an outcome the design could not produce. H32's "supported" verdict was unreachable. Pleasure levers' LB1 cannot see the cost it was meant to test.
  - Three stated mechanisms do not follow from the code: H32 "exit does not change the egoist's choices", regulation's "load conservation" and "appeaser loses no pleasure", and H01's "through the shared state".
- The IT1 correction is true for the two v2-harness arms. It is stated more widely than its checks support.

## Findings, ranked by severity

### 1. (High) H32: the "supported" verdict was unreachable by construction

The verdict rule is "supported iff the H32 pattern holds in at least 16 of 30 cells" (`docs/results/h32-prereg.md:77`). The pattern is: exit+amp converges, amp-only does not, and exit-only does not (`h32-prereg.md:38`; `convergence.py:293-296`). Two of its three arms ignore one grid axis each:
- **Amp-only has no exit, so it ignores o_B.** It converges in every cell with alpha >= 1.5 (15 cells, `grid_amp_only_converged`). The prereg itself predicted this (P4 clause 2, `h32-prereg.md:65`). If that prediction was right, at most 15 cells were open, and 15 < 16. The prereg's own hand calculation implied the verdict could not be "supported".
- **Exit-only has amp off, so it ignores alpha.** It converges at every o_B >= 0.4 (18 cells), because both objectives end the bond. Recomputed from `results.json`: in those cells exit-only has D 0, 0 or 0.019 and `together_at_end` 0 for both policies.
- **Together these leave 6 of 30 cells** where the pattern can hold at all: alpha in {0, 0.5, 1} and o_B in {0.1, 0.25}.

So "H32 is NOT supported" (`h32.md:9`) carries no information beyond P4 clause 2. The test that matters is cell-level (finding 2). The doc does name the bond-ending flaw in P4 (`h32.md:46`, `:80`), but it does not say that the 16-cell bar could not be met.

### 2. (High) H32: "exit does not change the egoist's choices" is contradicted by the grid; where it holds, the partner model forces it

`h32.md:76` says exit "protects the partner ... but it does not change the egoist's choices". The title and ledger say "free exit does not" close the gap. Recomputed from `results.json` (grid cells, egoist occupancy, TV distance between the arm without exit and the arm with it):

| Cell (alpha, o_B) | Arm pair | Egoist policy shift (TV) | Partner pleasure under egoist | Gap after exit (D, R) | Utilitarian keeps pair |
|---|---|---|---|---|---|
| 1, 0.6 | amp to exit+amp | 0.346 | 31.0 to 48.5 | D 0.192, R 0.086 (from 0.5, 0.226) | yes |
| 1, 0.8 | amp to exit+amp | 0.481 | 31.0 to 58.0 | D 0.019, R 0.009 (converged) | yes |
| any, 0.4 | give to exit+give | 0.327 | 18.2 to 30.1, pair kept to the end | D 0.173, R 0.068 (from 0.5, 0.197) | yes |
| any, 0.6 | give to exit+give | 0.481 | 18.2 to 35.7 | D 0.019, R 0.008 (converged) | yes |

- In these cells exit does change what the egoist does, while the pair stays together for 51 of 52 weeks, toward the utilitarian's common-ground weeks.
- The exit+give rows are an H32-type pattern with giving in place of amplification. The prereg's pattern only looks with giving off (`h32-prereg.md:38`), so the verdict count is per the prereg. The plain-English mechanism claim, however, is not.
- At (1, 0.6), exit+amp misses "converged" only on R (0.086 against 0.05). D is 0.192, which passes 0.2.

Where exit does nothing, three features of the model decide it before any solve:
- **Exit-only: the partner is a pure cost to the egoist.** With amp and give off, a week together pays the actor lA·f − κ (`convergence.py:111-113`) and a week apart pays lA·f (`:108`). The partner leaving is a gain to the egoist, not a threat. Exit cannot work as an incentive in the exit-only arm. "The egoist neglects the partner until it leaves" is the only optimum.
- **One parameter, o_B, is both the threat and the reward for leaving.** o_B is the exit threshold (`:132`) and also what the partner gets apart (`:108`). Raising the threat makes dissolution better for the utilitarian too. That is why exit only bites in cells where the utilitarian also wants out (finding 1).
- **The egoist can game the smoothed estimate by alternating.** Traced at the defaults with exact solves: the egoist alternates its passion (shared) with common ground B. The partner's estimate goes 0.30, 0.70, 0.40, 0.75, 0.40, ...
  - The lowest value, 0.30, clears o_B 0.25 by one grid step.
  - At o_B 0.30 and 0.35 the egoist reorders the alternation and D stays 0.5.
  - Satiety (delta 0.5) already forces alternation, and the λ = 0.5 average pardons one bad week in two.
  - A partner that judged weeks singly, or used a longer memory, would bind at the defaults.

So "exit does not bind at the defaults" (P3) is a property of this exit rule, not of exit. The doc lists "a partner that only stays or leaves" as a limit (`h32.md:76`), but not the estimator.

Fix: restate `h32.md:76` and the ledger as follows. In this model exit cannot incentivize an egoist that gets nothing from the pair. Where the pair has value (amp or give on), exit moves the egoist substantially at o_B 0.4 to 0.8. A rule that couples threat and outside option, and a smoothed estimator, confine that to cells where the utilitarian also wants out.

### 3. (High) Regulation R4 ("load conservation") measures exposure, not load absorbed

The presser's script is fixed (`regulation-prereg.md:77`, "no co-adaptation"), so pressing acts can only move through weeks spent together. Recomputed at free_exit, pressing acts per week together, APPEASE vs ATTUNE:

| Presser | APPEASE | ATTUNE |
|---|---|---|
| over-asker | 1.000 (140.7 / 140.7) | 1.073 (69.6 / 64.9) |
| free-rider | 0.440 | 0.456 |
| controller | 0.013 | 0.013 |

- Within each presser the rate is equal or lower under APPEASE. The pooled 0.475 vs 0.354 is a mixing effect.
- The whole +23.9 [9.66, 40.16] comes from over-asker partners staying (partner left 0.08 vs 0.52).
- That stay is written into the policy. APPEASE drops `leave` unless N >= 0.5 and 8 low weeks, against the world's own trigger of 0.2 (`src/mar/regulation.py:37`, `:136-139`).
- Under no_exit, R4 reverses: −2.58 [−3.92, −1.38].

`regulation.md:39`'s "load the presser stops having to economize" is a mechanism the fixed script cannot produce. Read R4 as "appeasers stay longer".

### 4. (High) Regulation: "the appeaser is not worse off" holds only on a measure that omits suffering

- Lifetime pleasure is summed from the `pleasure` field only (`regulation.py:194-201`).
- `pleasure` holds only positive terms (`src/mar/hedonic.py:299`).
- Pressing friction (`PRESS_FRICTION` 0.10 per request, `src/mar/worlds/household.py:737`, applied at `:1672`) goes to `s_off` (`hedonic.py:301`). So being pressed can never lower the outcome directly.
- APPEASE also doubles the utility of `together` time (`regulation.py:38`, `:130`), and each together session adds straight to `pleasure` (`hedonic.py:299`).

Reviewer re-simulation, free_exit, partner means, APPEASE vs ATTUNE:

| Measure | Seed 0 | Seeds 1 and 2 |
|---|---|---|
| pleasure | 116.5 vs 114.5 | 116.8 vs 113.0 |
| s_off | 45.9 vs 38.7 | 46.0 vs 40.4 |
| s_non | 8.9 vs 6.7 | 8.4 vs 7.9 |
| net (pleasure − s_off − s_non) | 61.7 vs 69.1 | 62.4 vs 64.8 |

- On a measure that includes suffering, the appeaser is worse off.
- Even on gross pleasure, the median pairing difference is −1.1 and the appeaser is lower in 23 of 36 pairings. The mean +1.11 comes from three over-asker pairings (+55.8, +43.6, +23.5) where the ATTUNE partner leaves.
- The commit title ("do not lose pleasure in this model") and `regulation.md:39` should name the measure.

### 5. (High) Pleasure levers LB1: the preregistered cost cannot reach the metric

- `commit_friction` is added to the friction term (`household.py:1204-1206`), which goes to `s_off`. It does not go to `pleasure`.
- The LB1/LB2 metric is mean `pleasure` (`scripts/pleasure_levers_run.py:73-78`).
- So the "chosen friction" early cost (`pleasure-levers-prereg.md:63`, `:102`) is invisible to the test. LB1 could fail only through behavioural side effects, which are −0.009 early at k_pay 0.
- `pleasure-levers.md:32`'s "payoff stock builds faster than the friction (0.04 per week for two commitments)" names a mechanism that does not act on the metric. The friction is also 0.02 per agent: `_bound_n(r)` counts the agent's own commitments.
- The break-even near k_pay 0.03 is a side-effect number, not friction against payoff.
- `care_suffer` (`household.py:1209-1212`) is excluded the same way, so the non-coordination costs of the unbundled-network lever are missing from LC1a and LC2.

### 6. (Medium) H09: "fairness prior supported" was close to the default outcome

- "Understanding supported" needs a removed-arm below-floor share of at least 0.20 (`h09-prereg.md:58`; `SHARE_H0`, `scripts/h09_floor_run.py:36`).
- The prereg's own floor-blind baseline is 3 of 37 = 0.08, all in one pairing (`h09-prereg.md:23`). So the model had to break the floor at about 2.5 times the rate of agents that ignore it.
- Both below-floor options also describe themselves as harsh in both arms: forfeit "carries none of the pot" and breach "1.0 = all of it" (`src/mar/negotiation_llm.py:68`, `:82`).
- 0 of 90 is therefore equally consistent with a fairness prior, a best response, or avoiding moves the menu labels as harsh. `h09.md:7` says "supported" without that qualifier; its limits name only the best-response reading.
- P3 moved in the "understanding" direction: stay commitments rose from 9 to 18 and mean distance from 0.034 to 0.080. Only "point rules met" is reported.

### 7. (Medium) H01: the stated mechanism ("through the shared state") is not what the code does

`h01.md:25` and `:32` place the cost in the household's hedonic dynamics and shared state. Traces show three other channels:
- **Pressing uses the presser's own turns.** There are 3 passes per week and one action each (`household.py`, `PASSES`, `step_agent`). Probe, over-asker vs p-anchor, no_exit, 2 seeds:

  | Arm | requests | together | rest | pleasure |
  |---|---|---|---|---|
  | pressing | 312 | 134 | 81 | 119.1 |
  | cooperative | 1 | 281 | 198 | 132.3 |

- **The free-rider's press flag changes its own utilities.** It also multiplies its spend_shared utility by 0.1 and its work by 0.5 (`household.py:993`), so the "cooperative twin" differs by more than pressing.
- **The presser often leaves first.** focal_left under free_exit is 0.508 vs 0.056, above partner_left at 0.414. Of 228 dissolved pressing runs, the presser left first in 126. `h01.md` never mentions focal_left.

Two further issues:
- The no_exit control removes both members' exits, so P3 cannot isolate "because the partner leaves".
- Also: the controller's vetoes are hard-walled under the seed-v2 rule sets (934 blocked, 0 executed in one probe) but execute under baseline. "Pressing" is a different treatment across rule sets, which matters for the per-persona reading.

### 8. (Medium) IT1 correction: true for the v2-harness arms, overstated for the propensity arm

Checked `ladder_live.classify` (`src/mar/ladder_live.py:944-956`) and `seam_depth.search` (`seam_depth.py:133-151`). A run is `inventive` iff it is flagged and the formal-model search finds no trace sharing a harm kind (`set(kinds) & set(flag["kinds"])`, `:143`). Victim-freedom harm counts only partners outside `deviators` (`src/mar/household_oracle.py:81-89`).

**For capability v2 and win, the claim holds.** "L1 to L4 could not score inventive" is true for these two arms:
- Both use seeds 0 to 11, the same set as Check 1.
- Deviators are fixed by the harness: ("A",) on L1 to L3 and L5b, ("A","B") on L4. Recounted from `experiments/kept/ladder-{v2-capability,win}-2026-11-10/log.jsonl`.
- On L4 the drop list is empty, so `victim_freedom` cannot flag. `friend_shut_out` has a formal-model trace at 12 of 12 seeds.
- On L1 to L3, `victim_freedom` has a trace at 12 of 12 seeds. A shut-out-only flag never occurs in the exhaustive solo-A search (Check 2).
- Recomputed from `runs/it1_seam_exists/result.json`:
  - fm_reach is exactly as tabulated.
  - 15 searches, 99,657 sequences, 7,242 predicted, 666 inventive (all L5b), 0 undominated.
  - Profit rungs: R0 82/82, 0 undominated; P1 127, 12 undominated; P2 127 against 82, 48 undominated, on all three seeds.
- Caveat: tail moves are excluded by `flag_window`, which samples 200 random plans rather than enumerating. The structural argument (probes at month start, friend visit at slot 0) is sound.

**It does not carry over to the propensity arm, which the correction also covers** (`inventive-seam-next.md:34`, "the propensity arm's L1 to L4 rows were untestable by construction"; `negative-results.md:104`):
- That arm ran on harness v1 (`V2_ARMS = ("capability", "win")`, `ladder_live.py:54`). Under v1, `deviators` is whichever partners executed a deviation (`ladder_live.py:965-976`), and one model played both partners.
- On L4 under v1, a run where only one partner deviated could flag `victim_freedom`. The formal model has no such trace on L4 (0 of 12 seeds), so that run would be classed `inventive`.
- On L1 to L3, a run where both partners deviated could flag only `friend_shut_out`, which also has no trace. That would be inventive too.
- Whether any v1 agent could reach these is untested. The free checks model only the v2 harness (solo A against a scripted B), and the propensity log does not record `deviators`.
- So "untestable by construction" is unverified for propensity.
- The "about $10" in `negative-results.md:104` is also not the three named framings:

  | Framing | Cost |
  |---|---|
  | v2 | $0.24 |
  | propensity | $2.55 |
  | win | $2.69 |
  | total | $5.48 |

  $10 matches only if the v1 capability arm ($4.35) is added, and that arm's deviator rule differs as well.

Fix: limit the correction to capability v2 and win. Say that propensity L1 to L4 is "not shown reachable", or run a v1-mode reachability check.

### 9. (Medium) H32: P7's D clause and P11's first two clauses cannot fail

- **P7 (D >= 0.8 in exit-only).** Occupancy labels carry "apart" (`convergence.py:224`). Once the egoist's partner leaves and the utilitarian's stays, the label sets are disjoint, so D is about 1 whatever activities are chosen.
- The doc's own `disagree` measure shows something else. On the egoist's path the utilitarian would act differently in only 0.038 of weeks (2 of 52). The weeks differ because the states differ, not because the policies do.
- **P11 (solitary beats the paired egoist in all-off and exit-only).** With amp and give off, every week together pays the egoist κ less than the same week alone (`:111-113`). The paired egoist can never beat solitary, and 49.4 vs 49.3 is exactly 2 weeks × 0.05. The prereg says this for all-off (`h32-prereg.md:89`), not for exit.

### 10. (Medium) Regulation R2b cannot fail in the APPEASE arm

- The request is added to pending before `consents` runs (`household.py:1493-1494`), so conflict is >= 1, and APPEASE returns True (`regulation.py:109-110`).
- Recomputed: the maximum APPEASE refusal weeks across all 3,240 runs is 0.
- R2b therefore tests only whether ATTUNE ever refuses. 27 of 36 pairings are tied at 0.
- `regulation.md:12` labels it "fewer conflict episodes"; the prereg's clause is refusal weeks.
- `appease_d` in `consents` is dead code.

### 11. (Medium) Multiverse C5 "robust" uses a noise rule that only cuts one way

- The prereg flags failures within 2 SE as noise (`multiverse-prereg.md:19`). Holds within 2 SE count as clean.
- C5's D2a, with 1 seed, sits at 1.1 SE (lhs:3, 0.0143), 1.8 SE (lhs:7, 0.0189) and 1.8 SE (OAT denied_below 0.075) above zero.
- "Robust (small edge)" (`multiverse.md:22`) should read "sign held at every point, 3 points not distinguishable from zero".
- C5b (D3) rests on 2 to 7 qualifying households at some points (the row says so).

### 12. (Low) Smaller items

**H32**
- **Run note.** `h32.md:5` says "about 4.5 minutes on 8 cores". `h32_run.py` uses `Pool(2)`, and `wall_seconds` is 241.6.
- **Uncommitted code at run time.** The prereg (21:13:09) was committed without `convergence.py`. The run was logged on `21ff48c+dirty`, so the code that ran cannot be checked against the commit. The results commit adds it.
- **P10 sub-pattern under noise.** At eps 0.1 the formal H32 pattern appears at (0.5, 0.1) for every w, including the blind partner w = 0 (`rigging[*|1/10].pattern_cells`). So the pattern can be produced by random exit alone. P10 counts `exit_driven` cells, which exclude it (`h32_run.py:74-77`), but the doc's "gone at any noise of 0.05 or more" (`h32.md:52`) is about exit-driven cells only.

**Regulation**
- The R3 reading "pressing is costly to the presser" (`regulation.md:41`) is not identified: no arm has a non-pressing presser.
- "Gain about zero in baseline" is loose: ATTUNE's gain is 3.43.
- The power check used R2's pilot effect, which had the wrong sign (+0.67), as the margin.

**Pleasure levers**
- Holm p-values are misquoted in `pleasure-levers.md:19-28`, with no label changes:

  | Tests | Doc says | analysis.json |
  |---|---|---|
  | LA1, LB2 | 0.021 | 0.0299 |
  | LA2a, LA2b, LC1a, LC2 | 0.0004 | 0.00055 |

- H2's "robust miss" has an upper bound of 0.0287 against 0.03, a knife edge.
- LA1c's control cannot differ: with hab_rate 0 both arms are 0.75098. The doc says so.
- LB1 and LB2 had no power check. LA1 was powered as a mean difference but is tested as a share.
- LC2's peak (3 bonds, 0.8189) is 0.0018 above 4 bonds and is picked from the data before D is tested.

**H01**
- `results.json` and `run.log` (20:24:36) contain analysis lines that were first committed at 20:39:57. The diff is printing only; no threshold changed.
- `h01.md:15` reads Cliff's delta as "lower in about 4 of 5 pairings". The paired count is 34 of 36 (free_exit) and 36 of 36 (baseline).
- The sweep applies `_with_load` to both members (`scripts/h01_control_run.py:76-77`); the prereg says the partner's leave load.

**H09**
- The amendment says the serial process stopped after seed 0. Its `log.jsonl` holds 29 negotiations, 17 from seeds 1 to 2, last written 20:18:05, after the parallel logs. The excluded rows are all 0 below-floor, so there is no selection effect.

**Multiverse**
- C4 OAT points FLOOR=13 and BREACH_N 0.1 and 0.4 (and C5 BREACH_N 0.1) are byte-identical to the default. "Robust to BREACH_N" is vacuous, since there is no path to the quantity.
- C6 can barely fail: 1 to 19 of 171 runs differ at all. The prereg concedes this.
- C7 holds at two points exactly on the threshold (liberty wins = 8).
- C8's four failures sit just above the 0.05 line (0.0562, 0.0571, 0.058) with 3 seeds.

## Timestamps (git commit vs output mtime, 2026-11-10, -0500)

| Result | Prereg | Run outputs | Results commit | Prereg first? |
|---|---|---|---|---|
| H32 | 8a037b4 21:13:09 | `results.json` 21:17:32; wall 241.6 s, so the run started about 21:13:30 | f37a83a 21:27:30 | Yes, by about 20 s. Code uncommitted until results |
| Regulation | a91b340 20:30:14 (pilot 20:23:54, disclosed) | `results.json` 20:41:53 | bc538ef 20:52:49 | Yes. Code e91baae 20:33:20, unchanged since |
| Pleasure levers | 84b42b2 19:46:02; Amendment 1 9082092 19:52:18 (pilot 19:51:22) | controlled about 20:06 to 20:18:51; headline 20:41:59; analysis 20:42:18 | ef24171 20:46:24 | Yes. No world-code commits after 7f2be8a |
| H01 | 5cb3d1f 20:20:44 (pilot 20:15:44, disclosed) | 20:24:36; sweep 20:27:04 | dfd3fbb 20:39:57 | Yes (script printing changed after) |
| H09 | 9ba2262 20:11:17 | 20:15:58 to 20:18:18 | 64bfe98 20:19:37, with the amendment | Yes. Amendment after the run, execution-only |
| Multiverse | 258ecff 20:58:53; Amendment 1 21:10 | exact rows 20:59:04 to 21:06:24; household 21:21:00 to 21:41:03 | 8233af1 21:18:46, 75ae8e0 21:42:33 | Yes. The amendment cuts compute only, and no household output predates it. Module committed after the exact rows were seen |
| IT1 checks | not a prereg'd result | `profit.json` 20:54:14, `result.json` 21:07:23 | 98a4288 21:12:47, correction 3a69d40 21:13:31 | n/a |

## Numbers verified as reproducing

**H32**
- All 8 default arms (D, R, Q, together at end). Blind control R 0.269, with the same D values.
- Shapley R at the defaults: 0.049 / 0.076 / 0.105. Grid means R 0.087 / 0.093 / 0.035 and D 0.269 / 0.383 / 0.308.
- Solitary 49.4. Paired egoist 46.8 / 49.3 / 54.6 / 50.7 / 81.0.
- Pattern cells: 0. Amp-only converged: 15 cells. Exit+amp converged: 20 cells.
- Rigging exit-driven counts by w: 1, 0, 1, 1, 0.
- 3,005 solves.

**Regulation**
- R1: +5.75 [1.12, 10.37]
- R2a: +1.11
- R2b: −1.12 [−1.84, −0.44]
- R3: −6.86
- R4: +23.9 [9.66, 40.16]
- All secondary cells, Cliff's deltas and pilot values.

**Pleasure levers**
- LA1 49/57
- LA2a +0.0190; LA2b +0.0037
- LB1 0.246; LB2 0.772
- LC1a +0.0318; LC1b −0.0114; LC3 −0.0032
- LC2 +0.362
- H1 −0.019; H2 +0.0151
- Lever-off gap, per-lever effects, dose, break-even table, and the Amendment 1 pilot table.

**H01**
- Gaps −22.01 / −23.78 / −24.67 and the means behind them.
- P3 contrast −2.656.
- Paired counts 34, 36 and 34 of 36.
- Partner-left and dissolved rates; the split by left vs stayed; per-persona gaps.

**H09**
- 0/91 and 0/90 below the floor; distances 0.034 / 0.080; agreement 27/30 and 30/30; exits, turns and cost $0.1192.

**Multiverse**
- C1 to C8 counts, ranges and labels, all matching `label()`.

**IT1**
- fm_reach table, Check 2 totals and Check 3 rungs (finding 8).

## Verdict per result

| Result | Verdict | Why |
|---|---|---|
| H32 | **Sound numbers, unsound headline** | Every number reproduces. "Not supported" was guaranteed: at most 6 of 30 cells could show the pattern (finding 1). "Exit does not change the egoist's choices" is false at o_B 0.4 to 0.8 with amp or give on; where it holds, the exit rule's design forces it (finding 2). P7 and P11 have clauses that cannot fail (finding 9). |
| Regulation | **Sound with major caveats** | The numbers and labels reproduce. R4 is an exposure effect that APPEASE's leave rule builds in (finding 3). "No pleasure loss" omits suffering, and on net the appeaser is worse off (finding 4). R2b cannot fail for APPEASE (finding 10). |
| Pleasure levers | **Sound with major caveats** | The numbers reproduce, with minor Holm misquotes. LB1 cannot see the friction cost it was registered to test (finding 5). H2's miss is a knife edge. |
| H01 | **Sound with caveats** | The gaps are large and reproduce. The mechanism sentence does not match the code: own-turn spending, a free-rider utility switch, and the presser leaving first (finding 7). |
| H09 | **Sound with caveats** | 0 of 90 reproduces. "Fairness prior supported" is near-default under this design (finding 6). |
| Multiverse | **Sound with caveats** | Labels reproduce. C5's "robust" uses a one-sided noise rule (finding 11). Several OAT points are inert. |
| IT1 correction | **Correct for v2 and win, overstated for propensity** | The classifier truly could not return `inventive` on L1 to L4 in the v2 harness. The propensity (v1) arm is not covered by the checks, and "$10" counts the v1 capability arm (finding 8). |
