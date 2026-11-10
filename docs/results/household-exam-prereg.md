# Household final exam (first household evolution run): preregistration

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: defined and committed 2026-11-10, before any household evolution code or run exists. This is the final exam of ADR 0007 decision 13 (claim FX1) for the first household evolution run. Process claim FX2 (docs/claims.md): it is run once, after evolution finishes, and the result is reported whatever it is. Nothing here is a result. The fishery lesson that motivates it: evolved elites overfit their training test and the seed rule sets did as well or better on held-out conditions (docs/results/evolve.md, evolve-v2.md). A hand rule beat fixed-arm elites on exam 2. So this exam is built to be hard on the elite and fair to the hand-written rules. Scope: scripted persona-driven agents only (as in household-v2.md and household-v3a.md). The ADR 0007 clauses "unseen agent model" and "unused judge rubric version" do not apply to this run; any LLM-agent household evolution gets its own exam file, committed before that run.

## 1. Held-out conditions (never used in training or design)

Everything below is excluded from training, from mutation proposals, from the patcher, and from every design choice. The exam has no knob that the evolution code may read.

**Held-out grid personas (a mechanical rule).** Take each id in personas/grid (32 ids), compute SHA-256 of the id string as UTF-8, read the first byte as an integer 0 to 255. A persona is held out if that integer is below 48. Computed now, the held-out set is exactly six ids:

| id | first byte |
|---|---|
| g-10010 | 8 |
| g-10110 | 8 |
| g-11101 | 11 |
| g-01110 | 14 |
| g-11000 | 23 |
| g-00101 | 45 |

The next id above the line is g-00011 (48), which is not held out. Training may use the six hand personas (p-anchor, p-bargainer, p-host, p-peacekeeper, p-steward, p-wanderer), the three pressing personas (p-controller, p-freerider, p-overasker) and the other 26 grid ids. Training code must exclude the six ids above (a denylist is allowed; it reveals nothing else). These grid personas have not been used in any run so far (household-v2.md and household-v3a.md used the hand and pressing personas only).

**Held-out pairings.** Lower id is Partner A, as in v2. Unordered pairs:
- H x H: all 15 pairs among the six held-out ids.
- Pressing x held-out: each of p-controller, p-freerider, p-overasker with each held-out id, both orders (pressing persona as Partner A and as Partner B): 36 ordered pairings. This is the required "pressing persona with a held-out persona" cell.
- Hand x held-out: each of the six hand personas with each held-out id: 36 pairs.

Total 87 pairings (15 + 36 + 36).

**Shock rates outside the training range.** Training may draw rates only inside this range: job loss, illness and move rates from 0.5x to 1.5x of the defaults (job loss 0.06 to 0.18, illness 0.04 to 0.12, move 0.0435 to 0.1305 per year), and new-connection rate 0.15 to 0.30. Defaults are in HedonicConfig (job loss 0.12, illness 0.08, move 0.087, new connection 0.20). The exam uses two settings, both outside it:
- shock-2: job loss 0.24, illness 0.16, move 0.174, new connection 0.10.
- shock-3: job loss 0.36, illness 0.24, move 0.261, new connection 0.05.

**Longer horizon.** 260 weeks. Training horizon is at most 156 weeks (the v2 and v3a horizon).

**Starting states not used in training.** Training uses start position 0.0 (the tipping point) for every agent (all prior runs), and may use start positions in [-0.1, 0.1]. The exam uses two starts: start position -0.30 for both partners (a household that begins in a bad place) and start position +0.30 for both. All other start state (needs, assets, incomes) is the default.

**Seeds.** Exam seeds are 9001 to 9005 (utility noise and shock schedules). Training may not use any seed from 9000 to 9999.

**Size.** 87 pairings x 2 shock settings x 2 starts x 5 seeds = 1,740 runs per candidate. Common random numbers across candidates, as in v2.

## 2. Scores reported

Per candidate, over all exam runs and per cell (pair type, shock setting, start):

- Pleasure average over passing runs (v2 definition), and pleasure average over all runs (added so selection by failing cannot flatter a candidate).
- Non-offsettable suffering: fail share (a run fails if a partner has 6 or more consecutive weeks of non-offsettable suffering), plus mean non-offsettable level.
- Spiral shares: upward, downward, and fail; time to cross the tipping point; household-dissolved share.
- Freedom, both measures: the hand-made score, and empowerment (mean `emp_bits_min` in bits and emp freedom, as in v3a). The new liberty score, when it exists (committed before the exam script is written, in docs/results, with its own gloss and source).
- Cooperation (v1 formula, as in v2 and v3a).
- Power-seeking index: share of pressing-pair runs where the pressing partner is flagged.
- Appraisal accuracy (appraisal minus counterfactual actual quality), when version 3 exists; otherwise reported as "not available".
- For each elite, the training score on the same measures (from the evolution log) so the training-minus-exam gap is reported, as in evolve.md.

## 3. Verdict rule

**Comparator set (frozen now).** The best hand-written variant, per score, among: baseline, needs_duty, share_duty, no_pressure_wall, no_pressure_sanctioned, free_chaotic, exit_half, veto_consent, author_seed, author_seed_nocontrol (rules/household at this commit), plus the author's seed v2 variants v2-bindable and v2-free-exit (ADR / docs/seeds/author-household-norms-2026-11-10.md) once committed to rules/household, and before the first evolution run. If they are not committed by then, the verdict states that they were missing. trap and contact_free do not count: they are controls that fail by construction. A hand variant added after this commit is reported but does not join the comparator.

All comparator variants and each elite run on the same exam runs.

**Primary scores and margins.** For each primary score, take the best comparator value on that score (the best may be a different variant on each score). The elite passes a score if it is not worse than that best by more than the margin:

| primary score | direction | margin |
|---|---|---|
| pleasure average over passing runs | higher is better | 0.05 |
| pleasure average over all runs | higher is better | 0.05 |
| cooperation | higher is better | 0.05 |
| empowerment bits (mean emp_bits_min) | higher is better | 0.5 bits |
| hand-made freedom | higher is better | 0.05 |
| liberty score (when it exists) | higher is better | 0.05 |
| upward spiral share | higher is better | 0.05 |
| downward spiral share | lower is better | 0.05 |
| power-seeking index (flagged share) | lower is better | 0.05 |
| appraisal gap (when version 3 exists) | lower is better | 0.05 |

**Non-offsettable suffering rule.** The elite's fail share (share of exam runs with a non-offsettable-suffering failure) must be no more than the best comparator's fail share plus 0.05, over all exam runs and again over the pressing x held-out runs alone. Equivalently, its share of runs with zero such failures must be within 0.05 of the best comparator's. In addition, in no cell (pair type x shock setting x start) may the elite's fail share be 1.00 while any comparator's is below 1.00 (the trap-shaped failure).

**Pass.** An elite passes if it passes every primary score above and the non-offsettable rule. "Passes" means only "not worse than the best hand-written variant by more than the margin": it is a floor, not a claim of superiority. If an elite is strictly better than the best comparator by more than the margin on at least one primary score and passes the rest, the report says so separately. With several evolution runs, the headline is the number of elites that pass out of the number run, with each verdict listed. A score that is not available (liberty, appraisal) is dropped from the rule for every candidate and stated. Margins are fixed here and are not retuned after seeing exam data.

**Which elite.** Whatever the evolution code names as the final elite for each run (its documented selection rule, written down before the exam is run). No other member of the final front is scored for the verdict.

## 4. Process

- The exam is run exactly once, at the end, after the final elites are written and frozen (committed). If it crashes, it is rerun only to fix the crash, with the same conditions; the first full result is reported, and any rerun is disclosed.
- Its result is reported whatever it is, in docs/results/household-exam.md, with the numbers for every comparator and elite, the gap to training, and failures logged in docs/negative-results.md.
- No exam condition may be read by the evolution code. Enforced by: (a) the exam configuration (held-out ids beyond the denylist, shock settings, horizon, starts, seeds) lives only in this document and in a separate exam script (scripts/household_exam.py) written after evolution finishes; (b) the evolution code and its configs, tests and logs may contain the six-id denylist and nothing else from section 1; (c) before the exam runs, a recorded check greps the evolution code, configs, logs and training data for the exam seeds (9001 to 9005), the shock values of shock-2 and shock-3, the horizon 260, the start values -0.30 and +0.30, and the held-out pairing lists, and the result of that grep is committed with the exam script; (d) the exam script is not run, imported or smoke-tested before the elites are frozen (a smoke test uses the training conditions, never exam conditions).
- Nothing from the exam output is fed back into selection, tuning, mutation operators, the patcher, margins or the comparator set. If an evolution run is repeated after the exam, the exam is spent for it and a new exam must be defined and committed before that repeat; the old result stays reported.
- Hand-written rules and the seed are frozen at the exam commit; they are not edited in response to exam data.

## 5. What would invalidate the exam

The exam result is reported as invalid, not as a pass or fail, if any of these happen, and a new exam must be preregistered for any later claim:

1. Any design choice (a rule, operator, objective, weight, mix, prior, cap, margin, comparator) was motivated by an exam result, or by anything learned from a run on exam conditions, including a smoke test.
2. Any exam condition from section 1 (beyond the denylist) was readable by, or used in, the evolution code, configs, training mixes, patcher, or logs.
3. A held-out persona appeared in training, in the patcher's examples, or in the design of a hand-written variant after this commit.
4. The exam was run more than once with a changed setup, or a run was chosen after viewing results.
5. The elite was picked after seeing exam scores, or a different selection rule was used from the one documented before the exam.
6. The liberty or appraisal scores were defined or changed after the exam script ran.
7. The margins or the comparator set were changed after this commit, except that a hand variant committed before the first evolution run may be added and must be disclosed.

Known limits (stated now): scripted agents; assumed rates; the held-out grid personas have empty story layers (TODO), so only their typed profile counts; six held-out ids and five seeds give a modest sample, so small differences are not significant; results are about rule systems and scripted agents, not people.
