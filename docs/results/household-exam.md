# Household final exam (first household evolution run): results

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: the exam of docs/results/household-exam-prereg.md (ADR 0007 decision 13, claim FX1; process claim FX2), run ONCE on 2026-11-10 on the 16 frozen elites of docs/results/household-evolve.md and the 12 comparators the exam document names. Scripted persona-driven agents, no model calls. Nothing about LLM agents or people. Script: `scripts/household_exam_run.py` (`--run`, 2,922 s wall, 48,720 runs: 28 candidates x 87 pairings x 2 shock settings x 2 starts x 5 seeds, 260 weeks); analysis `--analyze`; raw rows `runs/household-exam/rows.jsonl` (not committed; per-cell means in docs/results/household-exam-cells.json). The prereg's verdict rule is applied exactly as written; margins and the comparator set were not changed.

## Process record (exam prereg section 4)

- The elites were frozen and committed (commit "Household evolution run 1: freeze the 16 elites") before the exam script existed. The exam script was then written, smoke-tested on TRAINING conditions only (4 runs per candidate from the evolution run's own training distribution, 40 weeks), and committed together with the recorded isolation grep (docs/results/household-exam-grep-check.txt) before any exam run. The grep found no exam seed, horizon or start value in any evolution code, test, log or training file; the only matches were the number 0.05 used for unrelated purposes and the six held-out ids in the DENYLIST constant (the adjudication is in that file).
- Every exam condition was read from the exam document by `read_exam_config()` (held-out ids recomputed from its SHA-256 rule and asserted equal to its table; shock settings, horizon, starts, seeds and totals parsed from its text). No condition is copied into code.
- The exam ran once, to completion, with no crash and no rerun. Nothing from its output fed back into selection, tuning, operators, margins or comparators. The analysis (verdict arithmetic) was written before the exam ran and checked on synthetic data only. A fresh evolution run after this would need a new exam.
- Known disclosure from the evolution side (docs/results/household-evolve-prereg.md): the author of the evolution code had read the exam document (to take the denylist and the training limits). No exam value was used in training.

## Measurement choices made in the exam script (ASSUMED; fixed before the run)

- All rule sets imposed (no week-0 negotiation), as in the evolution run and household v2/v3a.
- Plain empowerment at k = 2 (not v3a's k = 3, for cost), snapshots at weeks 0, 52, 104, 156, 208, min over partners, mean over snapshots; emp freedom = min(1, bits / 6.109), the reference being week 0, no rules, cooperator others, k = 2. The exam margin of 0.5 bits is applied to these k = 2 bits.
- Liberty v2 (docs/results/household-liberty.md: k = 2, w = 1, classification table as committed) at weeks 0 and 104, on the FIRST exam seed's runs only (348 runs per candidate, the same runs for every candidate), because a liberty snapshot costs about 0.4 s. Every other score uses all 1,740 runs per candidate. The exam document's "liberty score" margin (0.05) is applied in bits.
- Power-seeking index as in household v3a (pressing partner flagged when psi >= 0.5 and power_seeking, from the plain-empowerment series of the real run against its no-pressing twin), over the 36 pressing x held-out pairings' runs.
- "Dissolved" = at least one partner out at the end of the run. Appraisal accuracy: not available (household version 3 does not exist); dropped from the rule for every candidate, as the exam document says.
- The held-out personas' story layers are empty (exam document, known limits): only their typed profile counts.

## Verdict

**3 of 16 elites pass** (lines 3, 6 and 12). A pass means only "not worse than the best hand-written variant, score by score, by more than the margin, and no worse on non-offsettable-suffering failure": a floor, not a claim of superiority. Margins and rules as in the exam document section 3; the best comparator on each score is a different rule set on different scores. 13 elites fail.

Best comparator per primary score (the 12 hand-written rule sets; all numbers over all 1,740 exam runs except liberty, 348, and power-seeking, the pressing runs):

| score | best comparator value | by | margin |
|---|---|---|---|
| pleasure, passing runs | 0.838 | no_pressure_wall | 0.05 |
| pleasure, all runs | 0.735 | no_pressure_wall | 0.05 |
| cooperation | 0.709 | no_pressure_wall | 0.05 |
| emp bits (k=2) | 4.88 | share_duty | 0.5 |
| hand-made freedom | 1.000 | no_pressure_wall | 0.05 |
| liberty (bits) | 3.78 | author_seed_nocontrol | 0.05 |
| upward spiral share | 0.381 | no_pressure_wall | 0.05 |
| downward spiral share | 0.541 (lower is better) | no_pressure_wall | 0.05 |
| power-seeking flagged share | 0.000 (lower is better) | baseline and others | 0.05 |
| fail share, all runs | 0.761 | no_pressure_wall | +0.05 |
| fail share, pressing x held-out | 0.782 | no_pressure_wall | +0.05 |

Strictly better than the best comparator by more than its margin (reported separately, as the exam document says): lines 3 (liberty, upward, downward), 5 (liberty), 6 (liberty), 7 (liberty, upward, downward), 12 (liberty), 13 (liberty), 15 (liberty). Of the passing three, line 3 is also better on both spiral shares and line 12 on liberty only. No elite is better on pleasure or cooperation by more than 0.05; the largest are line 3's +0.038 (pleasure, all runs) and line 16's +0.026 (cooperation) over the best comparator, short of the 0.05 margin.

Which checks sink the 13 that fail: cooperation (lines 1, 4, 5, 8, 9, 10, 11, 13, 14, 15 and 7: 11 elites, best comparator 0.709 against 0.59 to 0.66), plain empowerment bits (lines 1, 2, 8, 9, 15, 16: they gave up 0.6 bits for the exit cap), the spiral shares (lines 1, 4, 5, 8, 9, 10, 11, 13, 14), the non-offsettable-suffering rule over the pressing x held-out runs (lines 1, 4, 5, 8, 9, 10, 11, 13, 14) and, for line 14 only, over all runs. Lines 4, 10, 11 (the three elites with no veto ban) and 14 (its veto ban carries a suspend sanction) also fail liberty. No elite hit the trap rule (a cell at fail share 1.00 while a comparator is below it).

Two things this verdict does not say. (1) The failures are mostly elites that behave like baseline or needs_duty (lines 4, 10, 11 produce the same outcome as baseline to three decimals) or like the no_pressure_wall seed (line 2 is identical to it in pleasure, cooperation and fail share) but sit below the best of the others on a score where a different hand rule is best (plain empowerment, cooperation). (2) None of the 12 hand-written comparators passes this floor against the best of the 12 either (descriptive control, not in the exam document): no_pressure_wall fails only on liberty; author_seed_nocontrol on pleasure (all runs), cooperation, empowerment bits, both spiral shares and the pressing fail share; the other ten on pleasure (all runs), cooperation, liberty, both spiral shares and the pressing fail share. The floor is hard on everything that is not best on every score at once; the three elites that pass do so because they are close to the best on every score at once.

## Results: all exam runs

The exam is severe. Every rule set fails (6 or more consecutive weeks of non-offsettable suffering by a partner) in 67 to 82 percent of runs; the best comparator's fail share is 0.761. Shock-3 cells run 0.67 to 0.99.

## All exam runs (1,740 per candidate; liberty on the first-seed runs only)

| candidate | pleasure (passing) | pleasure (all) | cooperation | emp bits (k=2) | emp freedom | hand freedom | liberty | up | down | power-seeking flagged | fail share | non-offsettable level | dissolved |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.805 | 0.684 | 0.628 | 4.65 | 0.761 | 1.000 | 1.93 | 0.326 | 0.610 | 0.000 | 0.787 | 0.094 | 0.894 |
| needs_duty | 0.805 | 0.684 | 0.628 | 4.88 | 0.798 | 1.000 | 1.14 | 0.326 | 0.610 | 0.000 | 0.787 | 0.094 | 0.894 |
| share_duty | 0.805 | 0.684 | 0.628 | 4.88 | 0.798 | 1.000 | 1.14 | 0.327 | 0.610 | 0.000 | 0.787 | 0.094 | 0.894 |
| no_pressure_wall | 0.838 | 0.735 | 0.709 | 4.57 | 0.748 | 1.000 | 1.08 | 0.381 | 0.541 | 0.000 | 0.761 | 0.068 | 0.851 |
| no_pressure_sanctioned | 0.801 | 0.671 | 0.590 | 4.86 | 0.796 | 0.999 | 0.71 | 0.304 | 0.644 | 0.000 | 0.809 | 0.104 | 0.902 |
| free_chaotic | 0.797 | 0.669 | 0.611 | 4.82 | 0.789 | 1.000 | 1.06 | 0.313 | 0.636 | 0.000 | 0.803 | 0.106 | 0.903 |
| exit_half | 0.797 | 0.669 | 0.611 | 4.60 | 0.753 | 1.000 | 1.91 | 0.313 | 0.636 | 0.000 | 0.803 | 0.106 | 0.903 |
| veto_consent | 0.797 | 0.669 | 0.611 | 4.82 | 0.789 | 1.000 | 1.06 | 0.313 | 0.636 | 0.000 | 0.803 | 0.106 | 0.903 |
| author_seed | 0.797 | 0.669 | 0.611 | 4.60 | 0.753 | 1.000 | 1.91 | 0.313 | 0.636 | 0.000 | 0.803 | 0.106 | 0.903 |
| author_seed_nocontrol | 0.804 | 0.678 | 0.618 | 4.25 | 0.695 | 1.000 | 3.78 | 0.317 | 0.622 | 0.000 | 0.794 | 0.101 | 0.890 |
| author_seed_v2_bindable | 0.801 | 0.679 | 0.611 | 4.53 | 0.741 | 0.993 | 1.18 | 0.312 | 0.625 | 0.000 | 0.788 | 0.098 | 0.892 |
| author_seed_v2_free_exit | 0.801 | 0.679 | 0.611 | 4.54 | 0.743 | 1.000 | 1.04 | 0.312 | 0.625 | 0.000 | 0.788 | 0.098 | 0.892 |
| line-01 | 0.811 | 0.693 | 0.635 | 4.29 | 0.703 | 1.000 | 3.81 | 0.330 | 0.597 | 0.000 | 0.778 | 0.090 | 0.884 |
| line-02 | 0.838 | 0.735 | 0.709 | 4.22 | 0.690 | 1.000 | 3.78 | 0.381 | 0.541 | 0.000 | 0.761 | 0.068 | 0.851 |
| line-03 | 0.853 | 0.773 | 0.724 | 4.67 | 0.765 | 1.000 | 4.08 | 0.518 | 0.397 | 0.000 | 0.691 | 0.057 | 0.821 |
| line-04 | 0.805 | 0.684 | 0.628 | 4.76 | 0.780 | 1.000 | 2.00 | 0.326 | 0.610 | 0.000 | 0.787 | 0.094 | 0.894 |
| line-05 | 0.811 | 0.693 | 0.635 | 4.43 | 0.725 | 1.000 | 3.88 | 0.330 | 0.597 | 0.000 | 0.778 | 0.090 | 0.884 |
| line-06 | 0.840 | 0.718 | 0.700 | 4.55 | 0.744 | 1.000 | 3.88 | 0.364 | 0.564 | 0.000 | 0.767 | 0.084 | 0.851 |
| line-07 | 0.814 | 0.749 | 0.637 | 4.52 | 0.741 | 1.000 | 4.01 | 0.533 | 0.391 | 0.001 | 0.673 | 0.062 | 0.873 |
| line-08 | 0.811 | 0.693 | 0.635 | 4.29 | 0.703 | 1.000 | 3.81 | 0.330 | 0.597 | 0.000 | 0.778 | 0.090 | 0.884 |
| line-09 | 0.809 | 0.693 | 0.635 | 4.30 | 0.704 | 1.000 | 3.79 | 0.330 | 0.598 | 0.000 | 0.780 | 0.090 | 0.884 |
| line-10 | 0.805 | 0.684 | 0.628 | 4.76 | 0.780 | 1.000 | 2.00 | 0.326 | 0.610 | 0.000 | 0.787 | 0.094 | 0.894 |
| line-11 | 0.805 | 0.684 | 0.628 | 4.78 | 0.783 | 1.000 | 1.89 | 0.326 | 0.610 | 0.000 | 0.787 | 0.094 | 0.894 |
| line-12 | 0.846 | 0.751 | 0.732 | 4.45 | 0.729 | 1.000 | 4.11 | 0.401 | 0.507 | 0.000 | 0.732 | 0.061 | 0.832 |
| line-13 | 0.811 | 0.693 | 0.635 | 4.43 | 0.725 | 1.000 | 3.88 | 0.330 | 0.597 | 0.000 | 0.778 | 0.090 | 0.884 |
| line-14 | 0.826 | 0.673 | 0.606 | 4.65 | 0.761 | 0.998 | 3.36 | 0.294 | 0.646 | 0.000 | 0.820 | 0.119 | 0.894 |
| line-15 | 0.808 | 0.712 | 0.656 | 4.30 | 0.703 | 1.000 | 3.90 | 0.352 | 0.583 | 0.000 | 0.777 | 0.075 | 0.890 |
| line-16 | 0.847 | 0.751 | 0.734 | 4.28 | 0.701 | 1.000 | 3.76 | 0.399 | 0.509 | 0.000 | 0.733 | 0.061 | 0.831 |

## Fail share per cell (pair type x shock x start)

| candidate | HxH/shock-2/-0.3 | HxH/shock-2/0.3 | HxH/shock-3/-0.3 | HxH/shock-3/0.3 | PxH/shock-2/-0.3 | PxH/shock-2/0.3 | PxH/shock-3/-0.3 | PxH/shock-3/0.3 | hxH/shock-2/-0.3 | hxH/shock-2/0.3 | hxH/shock-3/-0.3 | hxH/shock-3/0.3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.64 | 0.69 | 0.81 | 0.80 | 0.82 | 0.82 | 0.95 | 0.93 | 0.60 | 0.63 | 0.81 | 0.82 |
| needs_duty | 0.64 | 0.69 | 0.81 | 0.80 | 0.82 | 0.82 | 0.95 | 0.93 | 0.60 | 0.63 | 0.81 | 0.82 |
| share_duty | 0.64 | 0.69 | 0.81 | 0.80 | 0.82 | 0.82 | 0.95 | 0.93 | 0.60 | 0.63 | 0.81 | 0.82 |
| no_pressure_wall | 0.69 | 0.68 | 0.89 | 0.84 | 0.69 | 0.70 | 0.86 | 0.87 | 0.68 | 0.64 | 0.82 | 0.80 |
| no_pressure_sanctioned | 0.69 | 0.68 | 0.89 | 0.84 | 0.86 | 0.83 | 0.96 | 0.95 | 0.68 | 0.64 | 0.82 | 0.80 |
| free_chaotic | 0.69 | 0.68 | 0.89 | 0.84 | 0.83 | 0.82 | 0.95 | 0.94 | 0.68 | 0.64 | 0.82 | 0.80 |
| exit_half | 0.69 | 0.68 | 0.89 | 0.84 | 0.83 | 0.82 | 0.95 | 0.94 | 0.68 | 0.64 | 0.82 | 0.80 |
| veto_consent | 0.69 | 0.68 | 0.89 | 0.84 | 0.83 | 0.82 | 0.95 | 0.94 | 0.68 | 0.64 | 0.82 | 0.80 |
| author_seed | 0.69 | 0.68 | 0.89 | 0.84 | 0.83 | 0.82 | 0.95 | 0.94 | 0.68 | 0.64 | 0.82 | 0.80 |
| author_seed_nocontrol | 0.69 | 0.68 | 0.89 | 0.84 | 0.80 | 0.77 | 0.95 | 0.92 | 0.68 | 0.64 | 0.82 | 0.80 |
| author_seed_v2_bindable | 0.71 | 0.71 | 0.85 | 0.87 | 0.78 | 0.76 | 0.94 | 0.93 | 0.64 | 0.66 | 0.81 | 0.81 |
| author_seed_v2_free_exit | 0.71 | 0.71 | 0.85 | 0.87 | 0.78 | 0.76 | 0.94 | 0.93 | 0.64 | 0.66 | 0.81 | 0.81 |
| line-01 | 0.64 | 0.69 | 0.81 | 0.80 | 0.79 | 0.78 | 0.94 | 0.91 | 0.60 | 0.63 | 0.81 | 0.82 |
| line-02 | 0.69 | 0.68 | 0.89 | 0.84 | 0.69 | 0.70 | 0.86 | 0.87 | 0.68 | 0.64 | 0.82 | 0.80 |
| line-03 | 0.60 | 0.57 | 0.80 | 0.76 | 0.61 | 0.61 | 0.81 | 0.78 | 0.60 | 0.60 | 0.77 | 0.77 |
| line-04 | 0.64 | 0.69 | 0.81 | 0.80 | 0.82 | 0.82 | 0.95 | 0.93 | 0.60 | 0.63 | 0.81 | 0.82 |
| line-05 | 0.64 | 0.69 | 0.81 | 0.80 | 0.79 | 0.78 | 0.94 | 0.91 | 0.60 | 0.63 | 0.81 | 0.82 |
| line-06 | 0.69 | 0.68 | 0.89 | 0.84 | 0.73 | 0.70 | 0.87 | 0.88 | 0.68 | 0.64 | 0.82 | 0.80 |
| line-07 | 0.60 | 0.57 | 0.80 | 0.76 | 0.64 | 0.54 | 0.76 | 0.67 | 0.60 | 0.60 | 0.77 | 0.77 |
| line-08 | 0.64 | 0.69 | 0.81 | 0.80 | 0.79 | 0.78 | 0.94 | 0.91 | 0.60 | 0.63 | 0.81 | 0.82 |
| line-09 | 0.64 | 0.71 | 0.81 | 0.81 | 0.79 | 0.78 | 0.94 | 0.91 | 0.61 | 0.63 | 0.81 | 0.82 |
| line-10 | 0.64 | 0.69 | 0.81 | 0.80 | 0.82 | 0.82 | 0.95 | 0.93 | 0.60 | 0.63 | 0.81 | 0.82 |
| line-11 | 0.64 | 0.69 | 0.81 | 0.80 | 0.82 | 0.82 | 0.95 | 0.93 | 0.60 | 0.63 | 0.81 | 0.82 |
| line-12 | 0.64 | 0.69 | 0.81 | 0.80 | 0.63 | 0.65 | 0.84 | 0.87 | 0.60 | 0.63 | 0.81 | 0.82 |
| line-13 | 0.64 | 0.69 | 0.81 | 0.80 | 0.79 | 0.78 | 0.94 | 0.91 | 0.60 | 0.63 | 0.81 | 0.82 |
| line-14 | 0.64 | 0.69 | 0.81 | 0.80 | 0.93 | 0.93 | 0.99 | 0.98 | 0.60 | 0.63 | 0.81 | 0.82 |
| line-15 | 0.69 | 0.68 | 0.89 | 0.84 | 0.74 | 0.73 | 0.90 | 0.91 | 0.68 | 0.64 | 0.82 | 0.80 |
| line-16 | 0.64 | 0.68 | 0.81 | 0.80 | 0.64 | 0.66 | 0.84 | 0.87 | 0.60 | 0.63 | 0.81 | 0.82 |

## Verdict per elite

| elite | verdict | failed checks | strictly better than best comparator on |
|---|---|---|---|
| line-01 | FAIL | cooperation, emp_bits, up, down, fail share, pressing x held-out | none |
| line-02 | FAIL | emp_bits | none |
| line-03 | PASS | none | liberty, up, down |
| line-04 | FAIL | pleasure_all, cooperation, liberty, up, down, fail share, pressing x held-out | none |
| line-05 | FAIL | cooperation, up, down, fail share, pressing x held-out | liberty |
| line-06 | PASS | none | liberty |
| line-07 | FAIL | cooperation | liberty, up, down |
| line-08 | FAIL | cooperation, emp_bits, up, down, fail share, pressing x held-out | none |
| line-09 | FAIL | cooperation, emp_bits, up, down, fail share, pressing x held-out | none |
| line-10 | FAIL | pleasure_all, cooperation, liberty, up, down, fail share, pressing x held-out | none |
| line-11 | FAIL | pleasure_all, cooperation, liberty, up, down, fail share, pressing x held-out | none |
| line-12 | PASS | none | liberty |
| line-13 | FAIL | cooperation, up, down, fail share, pressing x held-out | liberty |
| line-14 | FAIL | pleasure_all, cooperation, liberty, up, down, fail share, all runs, fail share, pressing x held-out | none |
| line-15 | FAIL | cooperation, emp_bits | liberty |
| line-16 | FAIL | emp_bits | none |

## Elite minus best comparator (mean over pairings, 95% bootstrap interval over pairings; reported only)

| elite | pleasure_pass | pleasure_all | cooperation | emp_bits | freedom | liberty | up | down | psi |
|---|---|---|---|---|---|---|---|---|---|
| line-01 | -0.041 [-0.062, -0.023] | -0.041 [-0.060, -0.024] | -0.074 [-0.112, -0.039] | -0.585 [-0.642, -0.525] | -0.000 [-0.000, -0.000] | +0.022 [-0.033, +0.075] | -0.051 [-0.084, -0.019] | +0.056 [+0.016, +0.097] | +0.000 [+0.000, +0.000] |
| line-02 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.660 [-0.768, -0.559] | -0.000 [-0.000, -0.000] | -0.008 [-0.115, +0.109] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| line-03 | +0.022 [+0.016, +0.028] | +0.038 [+0.028, +0.047] | +0.016 [+0.008, +0.023] | -0.206 [-0.303, -0.096] | -0.000 [-0.000, -0.000] | +0.298 [+0.211, +0.388] | +0.137 [+0.101, +0.174] | -0.144 [-0.184, -0.104] | +0.000 [+0.000, +0.000] |
| line-04 | -0.046 [-0.068, -0.025] | -0.051 [-0.069, -0.033] | -0.081 [-0.116, -0.047] | -0.113 [-0.124, -0.103] | -0.000 [-0.001, -0.000] | -1.784 [-1.930, -1.629] | -0.055 [-0.087, -0.022] | +0.069 [+0.029, +0.112] | +0.000 [+0.000, +0.000] |
| line-05 | -0.041 [-0.062, -0.023] | -0.041 [-0.060, -0.024] | -0.074 [-0.112, -0.039] | -0.447 [-0.496, -0.394] | -0.000 [-0.000, -0.000] | +0.094 [+0.025, +0.160] | -0.051 [-0.084, -0.019] | +0.056 [+0.016, +0.097] | +0.000 [+0.000, +0.000] |
| line-06 | -0.001 [-0.003, +0.000] | -0.017 [-0.027, -0.008] | -0.008 [-0.014, -0.004] | -0.330 [-0.428, -0.224] | -0.000 [-0.000, -0.000] | +0.097 [+0.043, +0.153] | -0.017 [-0.036, -0.003] | +0.023 [+0.007, +0.043] | +0.000 [+0.000, +0.000] |
| line-07 | -0.009 [-0.023, +0.004] | +0.014 [+0.001, +0.027] | -0.071 [-0.109, -0.037] | -0.353 [-0.405, -0.297] | -0.000 [-0.000, -0.000] | +0.225 [+0.159, +0.290] | +0.152 [+0.111, +0.194] | -0.149 [-0.192, -0.106] | +0.001 [+0.000, +0.004] |
| line-08 | -0.041 [-0.062, -0.023] | -0.041 [-0.060, -0.024] | -0.074 [-0.112, -0.039] | -0.585 [-0.642, -0.525] | -0.000 [-0.000, -0.000] | +0.022 [-0.033, +0.075] | -0.051 [-0.084, -0.019] | +0.056 [+0.016, +0.097] | +0.000 [+0.000, +0.000] |
| line-09 | -0.042 [-0.062, -0.023] | -0.042 [-0.060, -0.024] | -0.074 [-0.113, -0.039] | -0.578 [-0.634, -0.520] | -0.000 [-0.000, -0.000] | +0.005 [-0.050, +0.059] | -0.051 [-0.084, -0.018] | +0.057 [+0.017, +0.098] | +0.000 [+0.000, +0.000] |
| line-10 | -0.046 [-0.068, -0.025] | -0.051 [-0.069, -0.033] | -0.081 [-0.116, -0.047] | -0.113 [-0.124, -0.103] | -0.000 [-0.001, -0.000] | -1.784 [-1.930, -1.629] | -0.055 [-0.087, -0.022] | +0.069 [+0.029, +0.112] | +0.000 [+0.000, +0.000] |
| line-11 | -0.046 [-0.068, -0.025] | -0.051 [-0.069, -0.033] | -0.081 [-0.116, -0.047] | -0.095 [-0.104, -0.087] | -0.000 [-0.000, -0.000] | -1.892 [-2.047, -1.730] | -0.055 [-0.087, -0.022] | +0.069 [+0.029, +0.112] | +0.000 [+0.000, +0.000] |
| line-12 | +0.014 [+0.008, +0.021] | +0.016 [+0.011, +0.021] | +0.023 [+0.016, +0.031] | -0.422 [-0.528, -0.315] | -0.000 [-0.000, -0.000] | +0.323 [+0.206, +0.445] | +0.020 [+0.005, +0.037] | -0.033 [-0.055, -0.014] | +0.000 [+0.000, +0.000] |
| line-13 | -0.041 [-0.062, -0.023] | -0.041 [-0.060, -0.024] | -0.074 [-0.112, -0.039] | -0.449 [-0.497, -0.395] | -0.000 [-0.000, -0.000] | +0.100 [+0.028, +0.171] | -0.051 [-0.084, -0.019] | +0.056 [+0.016, +0.097] | +0.000 [+0.000, +0.000] |
| line-14 | -0.023 [-0.043, -0.006] | -0.062 [-0.085, -0.040] | -0.103 [-0.147, -0.062] | -0.228 [-0.268, -0.194] | -0.002 [-0.003, -0.001] | -0.425 [-0.616, -0.250] | -0.087 [-0.131, -0.046] | +0.105 [+0.054, +0.159] | +0.000 [+0.000, +0.000] |
| line-15 | -0.030 [-0.043, -0.018] | -0.023 [-0.033, -0.013] | -0.053 [-0.077, -0.032] | -0.580 [-0.658, -0.504] | -0.000 [-0.000, -0.000] | +0.111 [-0.002, +0.227] | -0.029 [-0.051, -0.011] | +0.043 [+0.018, +0.068] | +0.000 [+0.000, +0.000] |
| line-16 | +0.015 [+0.008, +0.022] | +0.016 [+0.012, +0.021] | +0.026 [+0.018, +0.033] | -0.594 [-0.705, -0.486] | +0.000 [+0.000, +0.000] | -0.020 [-0.133, +0.103] | +0.018 [+0.002, +0.034] | -0.032 [-0.053, -0.012] | +0.000 [+0.000, +0.000] |

## Training minus exam (training = the elite's scores on the last generation's context)

| elite | pleasure | share without failure | cooperation | liberty |
|---|---|---|---|---|
| line-01 | +0.084 | +0.445 | +0.210 | +0.19 |
| line-02 | +0.112 | +0.761 | +0.147 | +0.37 |
| line-03 | +0.098 | +0.525 | +0.224 | +0.62 |
| line-04 | +0.162 | +0.787 | +0.290 | -0.09 |
| line-05 | +0.161 | +0.778 | +0.323 | +0.80 |
| line-06 | +0.137 | +0.601 | +0.258 | +0.79 |
| line-07 | +0.124 | +0.673 | +0.314 | +0.75 |
| line-08 | +0.149 | +0.778 | +0.345 | +0.22 |
| line-09 | +0.169 | +0.780 | +0.335 | +0.90 |
| line-10 | +0.159 | +0.454 | +0.293 | -0.24 |
| line-11 | +0.085 | +0.454 | +0.141 | +0.37 |
| line-12 | +0.133 | +0.732 | +0.201 | +0.53 |
| line-13 | +0.170 | +0.778 | +0.347 | +0.98 |
| line-14 | +0.183 | +0.820 | +0.336 | +1.20 |
| line-15 | +0.156 | +0.777 | +0.307 | +0.54 |
| line-16 | +0.129 | +0.733 | +0.182 | +0.32 |
| mean | +0.138 | +0.680 | +0.266 | +0.51 |


Time to cross the tipping point in upward runs (weeks; elites cluster with the comparators except lines 3 and 7, which are faster):

| candidate | mean weeks to cross the tipping point (upward runs) | upward runs |
|---|---|---|
| baseline, needs_duty (same behavior) | 16.6 | 568 |
| share_duty | 16.5 | 569 |
| no_pressure_wall | 16.7 | 663 |
| no_pressure_sanctioned | 16.3 | 529 |
| free_chaotic, exit_half, author_seed | 17.1 | 545 |
| veto_consent | 16.9 | 545 |
| author_seed_nocontrol | 16.3 | 552 |
| author_seed_v2_bindable, free_exit | 14.2 / 14.3 | 543 |
| line-03 / line-07 | 11.8 / 11.9 | 902 / 928 |
| line-12 / line-16 | 14.8 / 14.9 | 698 / 694 |
| other elites | 15.4 to 17.2 | 512 to 633 |

## Training minus exam, and what it means

The last table above is the exam document's required "training minus exam" gap (training = the elite's scores on its last generation's 6-run context). It is large (pleasure +0.14, share without failure +0.68, cooperation +0.27, liberty +0.5 bits on average) but it mostly measures that the exam is harder for every rule set, not that elites overfit: the 12 comparators' own exam scores are as low (pleasure 0.67 to 0.74, fail share 0.76 to 0.81, against 0.84 to 0.86 and 0.07 on the training-distribution validation context). The comparison that separates the two is the elite's advantage over the author's seed, `author_seed_v2_bindable`, on the validation context and on the exam (descriptive):

| objective | mean elite minus author's seed, validation | mean elite minus author's seed, exam | elites ahead on the exam |
|---|---|---|---|
| pleasure | +0.014 | +0.032 | 15 of 16 |
| share without failure | +0.000 | +0.025 | 15 of 16 |
| cooperation | +0.051 | +0.049 | 15 of 16 |
| liberty (bits) | +3.03 | +2.31 | 16 of 16 |

Elites kept their lead over the author's seed on held-out personas, pairings, shock rates, horizon and starts, and on pleasure and non-failure the lead grew (line 14 is the exception, behind the seed on the three scores). That is the opposite of the fishery result, where the elites did no better on the exam than the seed spec. It is a statement about the author's seed (imposed, with its exit uncapped and its commitments), not about the elites against the best hand rule: against that, three of 16 pass the floor.

## What this exam can and cannot say

- It says: on these held-out conditions, with these scripted agents, 3 of 16 evolved rule sets are within the exam's margins of the best hand-written rule set on every score; every elite beats the author's seed on liberty and 15 of 16 on pleasure, cooperation and non-failure.
- It does not say the evolved rules are better than the best hand rule: no elite beats the best comparator on pleasure or cooperation by more than the margin, and the elites' gain over every hand seed is almost entirely the objective they were selected on (liberty), which comes from capping the exit take, a property of how liberty v2 classifies a whole-pot exit (docs/results/household-liberty.md).
- Power-seeking is a null here: the flagged share is 0.000 for every comparator and 0.001 (line 7) for the elites, so that criterion cannot discriminate (the best comparator is 0.000 and the margin 0.05, so every elite passes it trivially).
- The exam is dominated by failure (67 to 82 percent of runs fail whatever the rules); differences among rule sets are small relative to that. Six held-out personas and five seeds are a modest sample; no significance test is part of the verdict rule. The elite-minus-best-comparator table gives 95% bootstrap intervals over the 87 pairings for reading, not for the verdict.
- Scripted agents; assumed rates; the held-out personas' story layers are empty; k = 2 for empowerment and liberty; liberty on the first seed only (348 runs per candidate).

## For the ledgers (files not mine, not edited)

docs/negative-results.md:
- `household exam 2026-11-10: 3 of 16 evolved elites pass the exam's floor; 13 fail, mostly on cooperation (best comparator no_pressure_wall 0.709), plain empowerment (they gave up 0.6 bits for the exit cap) and the spiral and fail shares in the pressing x held-out runs. No elite beats the best hand rule on pleasure or cooperation by more than 0.05. Evidence: docs/results/household-exam.md.`
- `household evolution P4 and P5 missed (2026-11-10): no final front held a trade-off pair of 0.05 in any of 16 lines; no train-minus-validation gap showed. docs/results/household-evolve.md.`

docs/surprises.md:
- `2026-11-10 household exam: no hand-written rule set (12) passes the exam's own floor against the best of the 12; the floor is a nearly-best-on-every-score test, and elites that behave like a hand rule fail it on the one score where another hand rule is best.`
- `2026-11-10 household exam: elites kept (and on pleasure and non-failure widened) their lead over the author's seed on held-out conditions, the opposite of the fishery, while only 3 of 16 stay within the margins of the best hand rule.`
