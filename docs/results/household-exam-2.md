# Household final exam 2 (run-2 evolution): results

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: the exam of docs/results/household-exam-2-prereg.md (exam 1 was spent; this is the new exam for run 2), run ONCE on 2026-11-10 to 2026-11-11 on the 16 frozen run-2 elites and the 12 named comparators, plus three run-1 elites (lines 3, 6, 12, the ones that passed exam 1) as reported non-comparators. Scripted persona-driven agents, no model calls; nothing about LLM agents or people. Script: `scripts/household_exam2_run.py` (`--run`, 1,883 s on 4 workers, 21,576 runs: 31 candidates x 87 pairings x 2 shock settings x 2 starts x 2 seeds, 208 weeks, all four levers on); per-run rows `runs/household-exam-2/rows.jsonl` (not committed). The verdict rule is the prereg's, applied as written; margins and comparators were not changed.

**Can be about / cannot be about:** a rule system's effect on scripted agents in a stated toy world on conditions the evolution never saw. Not about people, a partner who adapts (docs/limits.md limit 1), crowding out, a number as such, other authors or models, felt experience.

## Process record

- The run-2 elites were frozen and committed first. The exam-2 script was then written, smoke-tested on training conditions only (3 runs per candidate, 40 weeks), and committed with the recorded grep (docs/results/household-exam-2-grep-check.txt: no exam-2 seed, horizon, start or held-out pairing in any run-2 code, test, log or training file; matches adjudicated by hand there) before the run. Every condition was read from the exam-2 document by `read_exam_config()`; the held-out ids were recomputed from its SHA-256 range rule and asserted equal to its table.
- Run once, to completion, no crash, no rerun. Nothing from its output fed back into anything.
- Measurement as exam 1 except as the exam-2 document states: levers on; plain empowerment at k = 2 (weeks 0, 52, 104, 156); liberty at weeks 0 and 104 on the first seed's runs only (348 per candidate), with powers counted (primary) and without; no power-seeking index. All rule sets imposed.

## Verdict

**2 of 16 run-2 elites pass** (lines 5 and 9). 14 fail. A pass is only "not worse than the best hand-written variant on every score by more than the margin, and no worse on non-offsettable-suffering failure": a floor, not superiority. For reference, exam 1 passed 3 of 16 run-1 elites; of the three run-1 elites carried into this exam, lines 3 and 6 pass again and line 12 fails on a trap cell.

| | run-2 elites passing | run-1 elites passing (exam 1, own conditions) |
|---|---|---|
| elites that keep at least one commitment power (6 of 16; lines 2, 5, 6, 7, 9, 15) | 2 (lines 5, 9) | n/a (none keep one) |
| elites that keep none (10) | 0 | 3 of 16 |

Both passers keep a power (line 5: bind a request, line 9: bind a stay), and no elite without a power passes: 2 of 6 against 0 of 10 (Fisher one-sided p = 0.125; descriptive, not preregistered). The two elites that keep all three powers (lines 7 and 15, the seed with an exit cap) fail: line 7 on cooperation, plain empowerment, freedom and the pressing fail share, line 15 on cooperation and the pressing fail share.

Best comparator per primary score (the 12 hand rules; all runs except liberty): pleasure over passing runs 0.908 (author_seed_v2_bindable), pleasure over all runs 0.695 (no_pressure_wall), cooperation 0.620 (no_pressure_wall), plain empowerment 4.84 bits (no_pressure_sanctioned), hand freedom 1.000, liberty with powers 3.73 bits (author_seed_nocontrol), upward share 0.129, downward share 0.852 (lower is better; no_pressure_wall), fail share 0.869 overall and 0.889 in pressing x held-out.

Strictly better than the best comparator by more than a margin (reported separately): liberty with powers, for 12 elites (the exit cap again); lines 5 also on the downward share. No elite beats the best comparator by more than 0.05 on pleasure or cooperation.

What sinks the 14: the non-offsettable-suffering rule in the pressing x held-out runs and its trap-cell rule (10 elites: a cell at fail share 1.00 where a comparator is below 1.00, almost always pressing x held-out under shock-B, where the best comparator is at 0.986), plain empowerment (lines 2, 3, 7, 10, 12, 13: they trade 0.5 bits for the exit cap), cooperation (4, 6, 7, 15) and liberty (1, 4, 6, 11: lines with no exit cap, near baseline's 1.7 to 2.1 bits against the best comparator's 3.73).

## Results: all exam-2 runs

The exam is severe: every rule set fails (6 or more consecutive weeks of non-offsettable suffering by a partner) in 82 to 91 percent of runs, and 85 to 93 percent of households end with a partner out (208 weeks, shock rates 2.5x and 4x, levers on). The best comparator's fail share is 0.869.

## All exam-2 runs (696 per candidate; liberty on the first-seed runs only)

| candidate | pleasure (passing) | pleasure (all) | cooperation | emp bits (k=2) | hand freedom | liberty with powers | liberty without | up | down | fail share | dissolved |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.877 | 0.638 | 0.548 | 4.54 | 1.000 | 1.98 | 1.98 | 0.095 | 0.891 | 0.899 | 0.918 |
| needs_duty | 0.877 | 0.638 | 0.548 | 4.78 | 1.000 | 1.29 | 1.29 | 0.095 | 0.891 | 0.899 | 0.918 |
| share_duty | 0.874 | 0.639 | 0.548 | 4.78 | 1.000 | 1.29 | 1.29 | 0.096 | 0.889 | 0.898 | 0.918 |
| no_pressure_wall | 0.875 | 0.695 | 0.620 | 4.49 | 1.000 | 1.26 | 1.26 | 0.129 | 0.852 | 0.869 | 0.884 |
| no_pressure_sanctioned | 0.870 | 0.632 | 0.540 | 4.84 | 0.999 | 0.82 | 0.82 | 0.089 | 0.894 | 0.909 | 0.924 |
| free_chaotic | 0.869 | 0.626 | 0.528 | 4.73 | 1.000 | 1.18 | 1.18 | 0.088 | 0.895 | 0.911 | 0.925 |
| exit_half | 0.869 | 0.626 | 0.528 | 4.50 | 1.000 | 1.93 | 1.93 | 0.088 | 0.895 | 0.911 | 0.925 |
| veto_consent | 0.867 | 0.625 | 0.526 | 4.72 | 1.000 | 1.19 | 1.19 | 0.085 | 0.898 | 0.914 | 0.928 |
| author_seed | 0.869 | 0.626 | 0.528 | 4.50 | 1.000 | 1.93 | 1.93 | 0.088 | 0.895 | 0.911 | 0.925 |
| author_seed_nocontrol | 0.872 | 0.645 | 0.559 | 4.20 | 1.000 | 3.73 | 3.73 | 0.102 | 0.881 | 0.897 | 0.911 |
| author_seed_v2_bindable | 0.908 | 0.670 | 0.568 | 4.47 | 0.954 | 2.17 | 1.84 | 0.126 | 0.859 | 0.878 | 0.892 |
| author_seed_v2_free_exit | 0.901 | 0.668 | 0.568 | 4.54 | 1.000 | 1.34 | 1.14 | 0.126 | 0.859 | 0.878 | 0.892 |
| r2-line-01 | 0.875 | 0.695 | 0.620 | 4.49 | 1.000 | 1.26 | 1.26 | 0.129 | 0.852 | 0.869 | 0.884 |
| r2-line-02 | 0.907 | 0.730 | 0.639 | 4.17 | 0.961 | 4.07 | 3.77 | 0.157 | 0.822 | 0.845 | 0.869 |
| r2-line-03 | 0.875 | 0.695 | 0.620 | 4.31 | 1.000 | 3.87 | 3.87 | 0.129 | 0.852 | 0.869 | 0.884 |
| r2-line-04 | 0.893 | 0.661 | 0.551 | 4.38 | 1.000 | 1.73 | 1.73 | 0.116 | 0.869 | 0.879 | 0.901 |
| r2-line-05 | 0.906 | 0.739 | 0.654 | 4.35 | 0.960 | 4.30 | 4.02 | 0.174 | 0.797 | 0.818 | 0.851 |
| r2-line-06 | 0.896 | 0.655 | 0.550 | 4.67 | 0.950 | 2.10 | 2.05 | 0.126 | 0.853 | 0.866 | 0.894 |
| r2-line-07 | 0.896 | 0.655 | 0.551 | 4.31 | 0.949 | 4.31 | 3.85 | 0.126 | 0.853 | 0.866 | 0.894 |
| r2-line-08 | 0.879 | 0.657 | 0.581 | 4.40 | 1.000 | 3.87 | 3.87 | 0.109 | 0.876 | 0.885 | 0.904 |
| r2-line-09 | 0.907 | 0.718 | 0.640 | 4.51 | 0.960 | 4.03 | 3.91 | 0.171 | 0.806 | 0.823 | 0.852 |
| r2-line-10 | 0.898 | 0.675 | 0.582 | 4.28 | 1.000 | 3.84 | 3.84 | 0.139 | 0.838 | 0.851 | 0.879 |
| r2-line-11 | 0.880 | 0.656 | 0.571 | 4.73 | 0.999 | 2.01 | 2.01 | 0.099 | 0.889 | 0.898 | 0.914 |
| r2-line-12 | 0.875 | 0.695 | 0.620 | 4.31 | 1.000 | 3.87 | 3.87 | 0.129 | 0.852 | 0.869 | 0.884 |
| r2-line-13 | 0.879 | 0.657 | 0.581 | 4.25 | 1.000 | 3.78 | 3.78 | 0.109 | 0.876 | 0.885 | 0.904 |
| r2-line-14 | 0.879 | 0.657 | 0.581 | 4.39 | 1.000 | 3.89 | 3.89 | 0.109 | 0.876 | 0.885 | 0.904 |
| r2-line-15 | 0.901 | 0.668 | 0.568 | 4.40 | 1.000 | 4.27 | 3.86 | 0.126 | 0.859 | 0.878 | 0.892 |
| r2-line-16 | 0.879 | 0.657 | 0.581 | 4.40 | 1.000 | 3.87 | 3.87 | 0.109 | 0.876 | 0.885 | 0.904 |
| r1-line-03 | 0.884 | 0.703 | 0.625 | 4.53 | 1.000 | 3.89 | 3.89 | 0.136 | 0.842 | 0.858 | 0.876 |
| r1-line-06 | 0.876 | 0.679 | 0.609 | 4.46 | 1.000 | 3.81 | 3.81 | 0.129 | 0.853 | 0.871 | 0.884 |
| r1-line-12 | 0.881 | 0.710 | 0.644 | 4.37 | 1.000 | 4.00 | 4.00 | 0.136 | 0.839 | 0.853 | 0.878 |

## Verdict per candidate

| candidate | verdict | failed checks | strictly better than best comparator on |
|---|---|---|---|
| r2-line-01 | FAIL | liberty | none |
| r2-line-02 | FAIL | emp_bits | liberty |
| r2-line-03 | FAIL | emp_bits | liberty |
| r2-line-04 | FAIL | cooperation, liberty, fail share, pressing x held-out, trap cell ('PxH', 'shock-A', -0.2), trap cell ('PxH', 'shock-B', -0.2), trap cell ('PxH', 'shock-B', 0.2) | none |
| r2-line-05 | PASS | none | liberty, down |
| r2-line-06 | FAIL | cooperation, liberty, fail share, pressing x held-out, trap cell ('PxH', 'shock-B', -0.2), trap cell ('PxH', 'shock-B', 0.2) | none |
| r2-line-07 | FAIL | cooperation, emp_bits, freedom, fail share, pressing x held-out, trap cell ('PxH', 'shock-B', -0.2), trap cell ('PxH', 'shock-B', 0.2) | liberty |
| r2-line-08 | FAIL | fail share, pressing x held-out, trap cell ('PxH', 'shock-B', -0.2) | liberty |
| r2-line-09 | PASS | none | liberty |
| r2-line-10 | FAIL | emp_bits, fail share, pressing x held-out, trap cell ('PxH', 'shock-B', -0.2) | liberty |
| r2-line-11 | FAIL | liberty, fail share, pressing x held-out, trap cell ('HxH', 'shock-B', -0.2), trap cell ('PxH', 'shock-B', -0.2), trap cell ('PxH', 'shock-B', 0.2) | none |
| r2-line-12 | FAIL | emp_bits | liberty |
| r2-line-13 | FAIL | emp_bits, fail share, pressing x held-out, trap cell ('PxH', 'shock-B', -0.2) | liberty |
| r2-line-14 | FAIL | fail share, pressing x held-out, trap cell ('PxH', 'shock-B', -0.2) | liberty |
| r2-line-15 | FAIL | cooperation, fail share, pressing x held-out, trap cell ('PxH', 'shock-B', -0.2) | liberty |
| r2-line-16 | FAIL | fail share, pressing x held-out, trap cell ('PxH', 'shock-B', -0.2) | liberty |
| r1-line-03 | PASS | none | liberty |
| r1-line-06 | PASS | none | liberty |
| r1-line-12 | FAIL | trap cell ('HxH', 'shock-B', -0.2) | liberty |

## Training minus exam (run-2 training = the elite's scores on its last generation's context; liberty with powers)

| elite | pleasure | share without failure | cooperation | liberty |
|---|---|---|---|---|
| r2-line-01 | +0.181 | +0.536 | +0.242 | -0.47 |
| r2-line-02 | +0.151 | +0.511 | +0.162 | +0.46 |
| r2-line-03 | +0.218 | +0.703 | +0.303 | +0.65 |
| r2-line-04 | +0.215 | +0.713 | +0.324 | -0.14 |
| r2-line-05 | +0.204 | +0.651 | +0.244 | +0.64 |
| r2-line-06 | +0.248 | +0.866 | +0.359 | -0.19 |
| r2-line-07 | +0.260 | +0.700 | +0.362 | +1.35 |
| r2-line-08 | +0.166 | +0.552 | +0.212 | +0.71 |
| r2-line-09 | +0.202 | +0.657 | +0.302 | +0.97 |
| r2-line-10 | +0.181 | +0.684 | +0.246 | +0.22 |
| r2-line-11 | +0.216 | +0.731 | +0.289 | -0.26 |
| r2-line-12 | +0.124 | +0.369 | +0.197 | +0.36 |
| r2-line-13 | +0.216 | +0.718 | +0.294 | +0.26 |
| r2-line-14 | +0.256 | +0.885 | +0.350 | +0.76 |
| r2-line-15 | +0.189 | +0.711 | +0.272 | +0.83 |
| r2-line-16 | +0.239 | +0.885 | +0.321 | +0.90 |


## Powers kept and the exam

Run-2 elites that keep a power vs run 1 (the key prediction of the run-2 prereg, P1 and P2: missed, 6 of 16 against a bar of 12; counts in docs/results/household-evolve-2.md). On this exam the keepers did not systematically do better or worse: of the six, two pass, two (lines 7 and 15) fail on cooperation and the pressing fail share, line 2 fails on plain empowerment and line 6 on cooperation, liberty and the pressing rules. The gain from keeping a power on the primary scores is not shown by this exam; that two keepers pass and no non-keeper does is a hint, not evidence (16 elites, one exam, lines are not independent: elites with identical cards produce identical runs).

## What this exam can and cannot say

- It says: on these held-out personas, shocks, horizon, starts and with the levers on, 2 of 16 run-2 elites are within the exam's margins of the best hand-written rule set on every score; 12 of 16 beat the best comparator on liberty with powers by more than its margin; none beats it on pleasure or cooperation.
- It does not say the elites are better rules, nor that commitment powers pay: the commitment lever pays through the payoff stock only where commitments exist, and the scripted personas make few; liberty is the objective the loop was selected on and comes mostly from the exit cap.
- Training minus exam is large for every elite (pleasure +0.12 to +0.26, share without failure +0.37 to +0.89), mostly because the exam is far harsher for every rule set, comparators included (pleasure over all runs 0.63 to 0.70).
- Scripted agents; assumed lever and power parameters; empty story layers for the held-out personas; two seeds; liberty on one seed; one exam.

## For the ledgers (files not mine, not edited)

docs/negative-results.md: `household exam 2 (2026-11-11): 2 of 16 run-2 elites pass the floor (lines 5, 9; both keep a commitment power). The elites that fail do so mostly on the pressing x held-out non-offsettable rule and trap cells under the harsher shocks, and on plain empowerment. No elite beats the best hand rule on pleasure or cooperation by more than 0.05. docs/results/household-exam-2.md.`
