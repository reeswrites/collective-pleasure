# Household final exam 2 (run-2 evolution): preregistration

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: defined and committed 2026-11-10, before any run-2 evolution code, config or run exists. Nothing here is a result. Exam 1 (docs/results/household-exam-prereg.md, docs/results/household-exam.md) is SPENT: its prereg says that if evolution is repeated after the exam, a new exam must be defined and committed first. This is that exam, for run 2 (docs/results/household-evolve-2-prereg.md): the same evolution loop with liberty counting normative powers, and a lifetime horizon with the pleasure levers on. Scripted persona-driven agents only; no model calls. Process claim FX2 (docs/claims.md): run once, after run-2 evolution finishes, and reported whatever it is.

**Can be about / cannot be about.** Can be about: what a rule system does to scripted agents in a stated toy world on conditions the evolution never saw. Cannot be about people, LLM delegates, or a partner who adapts (docs/limits.md limit 1: the partner is a script); about isolation as the cause of any harm (limit 2); about crowding out (limit 3); about a number as such, since parameters are assumed (limit 5: only patterns count); about other authors or models (limit 6); about felt experience (limit 10). Limits 4, 7, 8 and 9 do not touch this exam (no negotiation, no exit-moves-the-egoist cell, no ladder rungs); limit 8 is addressed by the free check in the run-2 prereg.

## 1. Held-out conditions (never used in training or design of run 2)

Everything below is excluded from training, mutation, the patcher and every design choice of run 2. The run-2 evolution code may contain the two persona denylists (exam 1's six ids, already published in exam 1's document, and exam 2's six below) and nothing else from this section.

**Held-out grid personas (a mechanical rule).** SHA-256 of the id string as UTF-8, first byte as an integer 0 to 255; held out iff the integer is in [48, 96) (that is, at least 48 and below 96). Exam 1 held out those below 48, so the sets are disjoint. Computed now, the set is exactly six ids:

| id | first byte |
|---|---|
| g-00011 | 48 |
| g-10100 | 62 |
| g-01101 | 77 |
| g-11111 | 86 |
| g-10101 | 91 |
| g-00010 | 93 |

**Held-out pairings.** Lower id is Partner A. H x H: all 15 pairs among the six. Pressing x held-out: each of p-controller, p-freerider, p-overasker with each held-out id, both orders (36). Hand x held-out: each of the six hand personas with each held-out id (36 pairs). Total 87 pairings.

**Shock rates outside the training range** (training draws at most 1.5x the defaults, new-connection 0.15 to 0.30):
- shock-A: job loss 0.30, illness 0.20, move 0.218, new connection 0.08.
- shock-B: job loss 0.48, illness 0.32, move 0.348, new connection 0.04.

**Horizon.** 208 weeks (run-2 training is fixed at 156).

**Starts.** Start position -0.20 for both partners, and start position +0.20 for both. (Training: [-0.1, 0.1].)

**Levers.** All four pleasure levers of ADR 0016 ON (adaptation, ritual, commitment, network) with the LeverConfig defaults, as in training for run 2.

**Seeds.** 9101 and 9102. Training may not use any seed from 9000 to 9999.

**Size.** 87 pairings x 2 shock settings x 2 starts x 2 seeds = 696 runs per candidate. Common random numbers across candidates.

## 2. Scores reported

As exam 1 (pleasure over passing runs and over all runs; fail share and mean non-offsettable level; spiral shares; time to cross; dissolved share; hand-made freedom; plain empowerment at k = 2; cooperation), plus: **liberty v2 with normative powers counted** (ADR 0014 amendment; the primary liberty score here), liberty v2 without powers (reported), measured at weeks 0 and 104 on the FIRST seed's runs only (k = 2). The **power-seeking index is dropped** (it was 0.000 for every comparator in exam 1 and cannot discriminate; it also doubles the run cost); appraisal accuracy is not available. For each elite, its run-2 training score on the same measures is reported against its exam score, and the loss report (docs/results/household-loss-report.md) is printed for every elite.

## 3. Verdict rule

As exam 1 section 3, with these differences only. **Comparator set (frozen now):** the same 12 hand-written variants (baseline, needs_duty, share_duty, no_pressure_wall, no_pressure_sanctioned, free_chaotic, exit_half, veto_consent, author_seed, author_seed_nocontrol, author_seed_v2_bindable, author_seed_v2_free_exit); run-1 elites are scored and reported but are not comparators. **Primary scores and margins:** pleasure over passing runs 0.05; pleasure over all runs 0.05; cooperation 0.05; plain empowerment 0.5 bits; hand-made freedom 0.05; liberty with powers 0.05 bits; upward share 0.05; downward share 0.05 (lower is better). **Non-offsettable-suffering rule:** the elite's fail share at most the best comparator's plus 0.05 over all exam runs and over the pressing x held-out runs alone; and no cell (pair type x shock x start) at fail share 1.00 while any comparator is below 1.00. **Pass:** every primary score and the non-offsettable rule; "pass" is a floor, not superiority; an elite strictly better than the best comparator by more than a margin on at least one score is reported separately. The headline is the number of elites that pass out of the number run. **Which elite:** the final elite named by the run-2 evolution code's documented rule (`evolve.pick_elite_h`, written before this exam is run). Margins are fixed here.

## 4. Process

- Run once, at the end, after the run-2 elites are written and frozen (committed). The exam script (scripts/household_exam2_run.py) reads every condition from THIS document, is written after run-2 evolution finishes, and is not run, imported or smoke-tested on exam conditions before the freeze (a smoke test uses training conditions).
- Before the run, a recorded grep of the run-2 evolution code, configs, logs and training data for the exam-2 seeds, the shock values, the horizon 208, the starts, and the held-out pairing lists is committed with the exam script. Exam-1 values appear in earlier code legitimately and are not part of this grep.
- Nothing from the exam output feeds back into selection, tuning, operators, margins or comparators.
- If a crash forces a rerun, the same conditions are used, the first full result is reported and the rerun disclosed.

## 5. What would invalidate the exam

Any design choice of run 2 motivated by an exam-2 result or by a run on exam-2 conditions (a smoke test included); any exam-2 condition beyond the denylist readable by the run-2 evolution code; a held-out persona in run-2 training; more than one run with a changed setup; an elite picked after seeing exam scores; margins or comparators changed after this commit.

Known limits: scripted agents; assumed rates and lever parameters; the held-out grid personas have empty story layers (only the typed profile counts); six personas and two seeds give a modest sample; liberty on the first seed only; one rule set's exam 1 result is not evidence for this one.
