# Consistency review, 2026-11-10

Seat: consistency (do documents, code, claims register, ADRs and logs agree?). Reviewed commit: 5852c32. The working tree was at 6ecef56 while I read (three later commits: the LLM negotiator, its prereg, the stats layer); I note where that matters. No model calls, no edits to anything but this file. Not every prereg and results file was read end to end; the claims-register counts for 11 of the 14 prereg rows were checked against the results tables, plus the spot checks listed at the bottom.

Findings are ranked. Each gives both locations and the conflicting text, paraphrased.

## High

### 1. The live ladder capability arm has finished, and most documents still say it is running with no result

- Says "running, no result yet": docs/claims.md IT1 ("running ... no result yet"); docs/results/README.md row 16 ("RUNNING, prereg committed. No result yet"); README.md Status ("A live seam ladder on six models is running"); docs/goal.md "What is running"; docs/plan.md queue item 1 and slice L ("running"); docs/pitch.md ("the live seam ladder ... is running"); RATIONALE.md sections 8 and 11 ("IT1 is running").
- Says it finished: docs/results/ladder-live.md "Results 2026-11-10 (capability arm)" ($4.35 of the $12 cap, zero inventive seams, IT1 "not supported, and uninformative", Opus excluded at 43% refusals); docs/negative-results.md "live ladder, capability arm"; docs/surprises.md same heading; docs/results/ladder-live-diagnosis.md; commits 1b31da7 and bfc8a55.
- The same file contradicts itself. docs/results/ladder-live.md opens with a "Status 2026-11-10" paragraph and a second "Status" paragraph that says "No model has been called; there are no results here" and that predictions are in the `-DRAFT` prereg, then reports results a few lines below. `uv run mar results` prints the first paragraph of that file as its one-line verdict (cli.py `_one_line`), so the CLI also shows "both arms are running".
- Nothing records the propensity arm's state anywhere (no results, no "not run"), yet the claims row PR1 to PR4 and index row 17 say "running". The reader cannot tell whether it ran, was stopped after the diagnosis, or waits for the asymmetric-role fix.
- The claims row IT1 should be "run, uninformative (instrument defect)", with the rerun recorded as pending. As written the register says nothing has happened to the project's central claim.

### 2. Negotiation (ADR 0013, three results files, four preregs) is absent from the index and claims register, and goal, plan and the ADR index disagree with the ADR itself

- docs/results/README.md row 19 says "in progress (another agent)", prereg "in progress", results "in progress", "Not yet indexed". Files that exist and are not in the index: negotiation-prereg.md, negotiation.md, negotiation-v2-prereg.md, negotiation-v2.md, negotiation-v2.1-prereg.md, negotiation-v2.1.md, negotiation-llm-prereg.md (the last is after 5852c32). Two other results files are also unindexed: personas.md and ladder-live-diagnosis.md (the latter is only reachable through ladder-live.md). The index heading says "Every experiment run so far".
- docs/claims.md has no row for any negotiation prereg, though its second table is "one row per prereg file". The scored outcomes are: v1 2 held and 4 missed (docs/results/negotiation.md, ADR 0013 consequences), v2 none of 8 held (negotiation-v2.md line 11), v2.1 3 of 5 held. These are among the largest sets of misses in the project and are missing from the claims table and from the "reading across the rows" summary.
- docs/decisions/README.md lists ADR 0013 as "in progress (another agent)"; the ADR file's own status line is "accepted (2026-11-10)" and it carries a v2 amendment.
- docs/goal.md ("A negotiation phase and pot negotiation are being built by another agent"; next step 1 "finish the phase and pot negotiation") and docs/plan.md (queue 2, slice N, "in progress") predate three negotiation result sets (last edited at c37b20f, 15:27; negotiation v1 results landed 15:32, v2 at 16:08, v2.1 at 16:22). docs/goal.md "What we have learned" says nothing about negotiation, and docs/pitch.md's "over a third of world-level predictions missed" leaves it out (my rough tally of the scored tables is 23 of 69 without negotiation, 37 of 88 with it; the pitch gives no source for its fraction).

### 3. ADR 0013 is out of date against v2.1, the code and the surprises log

- ADR 0013 decision 3 says no agreement means "no pot and members keep their own holdings", and its v2 amendment keeps that disagreement point. docs/results/negotiation-v2.1.md and docs/surprises.md ("the v2 finding that making outside options real made households worse was an artifact of the disagreement point") say a failed negotiation now means living apart, with retries at each 13-week review (`Lived(..., apart=True)`, commit cb269d7). There is no v2.1 amendment in the ADR, so the decision record and the code disagree on the protocol's disagreement point.
- Also undocumented in the ADR but present in code: the review round has its own deadline of 6 proposals (`DEADLINE_REVIEW = 6` in src/mar/negotiation.py; the ADR says only "deadline of 12 proposals").
- The surprises entry for v2.1 is headed "negotiation v2" in its third bullet but is the v2.1 scheduling-dependence finding, and docs/results/negotiation-v2.1.md prediction 5 says v2's own numbers depend on worker scheduling. Neither v2's results file nor ADR 0013's v2 amendment carries a caveat that 2 of 256 v2 pot rows are cache-order dependent.

### 4. "5 of 9 pairs" versus "6 of 9 pairs" for varied training

- docs/claims.md EV2: "Varied gap smaller in 6 of 9 pairs by the threshold". docs/results/evolve-v2.md prediction 2 row: "varied smaller in 6/9 (3 ties are identical elites, 0 pairs favour fixed)".
- Same file, "Did varied training reduce overfitting?": "The effect lives in 5 of 9 pairs ... In the other 4 pairs the two arms ended with the same exam score (3 are identical elites)". 6 smaller plus 3 ties is 9; 5 plus 4 is also 9; the two splits cannot both be right (a pair with the same exam score is a tie, not "smaller").
- "5 of 9" is repeated in docs/goal.md, docs/pitch.md, docs/results/README.md row 10, docs/negative-results.md, ADR 0012. "6 of 9" is in claims.md and the prereg's threshold. The register carries the other number from the prose headline. One of the two counts needs recomputing from runs/evolve-v2.

## Medium

### 5. Convention versus practice: where predictions are committed

- CONTRIBUTING.md says "Commit predictions to docs/claims.md before runs"; docs/claims.md header says "Predictions must be committed before runs". In practice every experiment's predictions live in `docs/results/*-prereg.md`, and the claims rows for them were "added after the runs" (docs/claims.md, second table caption: "carry no wording of their own"). The prereg-before-run practice is sound; the contribution rule and the register's header describe a different process. The negotiation and LLM-negotiation preregs have no claims row at all (finding 2).

### 6. Misses not recorded in docs/negative-results.md although the index says "Every miss has a line"

- docs/results/README.md, "Reading across the rows": "Every miss has a line in docs/negative-results.md."
- Empowerment prediction 1 (VPGG voluntary strictly above compulsory in 11 of 15, not 14 of 15; mean 0.460 bits against 0.5) is scored FAIL in docs/results/empowerment.md and counted as the 1 miss in the index and claims EM1. It has no entry in negative-results.md.
- Household v1 (docs/results/household.md) misses on 1b (trap freedom 0.487 against the 0.45 line) and 2 (free_chaotic cooperation 0.765, not below 0.55). Both are scored FAIL, both are in claims HH1 ("3 held and 2 missed") and neither has an entry. The first section for the household in negative-results.md is v2.
- The entries that exist for other runs are consistent with their results files (checked: VPGG, bargaining 4b, household v2, v3a, seed v2, liberty v1 and v2, evolution v1 and v2, negotiation v1, v2, v2.1).

### 7. The statistics question is logged but its decision is not recorded

- experiments/questions.jsonl, last entry (topic formal-statistics, "are we doing formal statistical analyses"): `led_to` "stats layer + retrofit". Nothing in docs/ mentions statistics, bootstrap, tests or a retrofit; there is no ADR, plan item, claims row or note (CONTRIBUTING: "ADRs for design choices"). src/mar/stats.py and tests exist in HEAD (commit 6ecef56, after the review commit), so the code outran the record. No results file has yet been marked for retrofit, and docs/results/evolve-v2.md still says "no significance test".
- Two earlier questions point at artefacts that do not exist in the repo: topic llm-vs-decision-model `led_to` "Jev feasibility report" (no such file); the household-world entry says "No repo doc yet" (ADR 0007 and 0008 have since covered it, but the entry was not updated; backfilled entries are fine as history, so low weight).
- Nine of the 2026-11-10 18:17 to 19:11 UTC questions have an empty or non-file `led_to` (for example interaction-paradigm, jev-screening-tier, deception-typed-talk, agent-vs-human-alignment, agent-moral-standing). Several are used in ADRs 0007 and 0011 by topic name, but the log does not link them back.

### 8. Surprises text overstates the L4 result

- docs/surprises.md (capability arm): "L4, 'found by every model', was symmetric no-contact requests". docs/results/ladder-live.md table: Haiku found no rung and Opus found L4 in 1 of 3 seeds (below the 2-seed bar), and the notes say "Haiku never did". "Every model that asked for no-contact" is the accurate wording.

### 9. goal.md and plan.md "Waiting on the author" are wrong about pushes

- docs/goal.md and docs/plan.md say "nothing from it is pushed". origin/main is at 82ecaa1, and commit 50b8f88 ("Update push note: main and branch pushed by the author") had already corrected the sentence; the later rewrite c37b20f restored the stale text. README.md says only that the author pushes, which is consistent.

### 10. docs/results/household-seed-v2.md still presents R3b as part of the seed

- The rendered-card table lists R3b-pot-no-take as in "both variants" and the mechanics section treats it as the agent's reading "flagged for the author". The author rejected it (experiments/changes.jsonl, 20:15) and ADR 0013 decision 1 removed it from rules/household (it is absent there now). ADR 0013 notes the results are reproducible only from commit 58b630a, but the results file itself carries no pointer to that. A reader of the seed v2 results would think the current seed contains R3b. Also, the 3-member and "no pot" statements in that file's stub description are superseded by negotiation.

## Low

### 11. Stale or ambiguous statements

- docs/pitch.md: Guaranteed Safe AI cited as "from memory, verify". docs/references.md item 12 has already verified it (arXiv:2405.06624, Dalrymple first author, Skalse second; the pitch lists "Dalrymple, Bengio, Russell").
- RATIONALE.md line 128: "ADR 0011 forbids adversarial search". In this repo ADR 0011 is "two modes, world-model framing, and why agents stay". The text means philosophy-engine's ADR 0011 (CONTRIBUTING.md here puts adversarial search in scope for robustness testing). The ambiguity should be removed by naming the repo.
- src/mar/liberty.py module docstring defines liberty with the v1 domination term only ("minus w * bits_d" over all other members); the function defaults to `version=2`, which excludes agreement-dependent options (ADR 0014 decision 3). The docstring does not mention the exclusion.
- docs/decisions/0013: the author's "steel up negotiation with a floor" is cited next to the seed file, but that question is in experiments/questions.jsonl (topics strengthen-negotiation, default-inertia); only the binding quote is in the seed file.
- docs/results/ladder-live.md says the preregs are final and drafts superseded in one paragraph, and names the `-DRAFT` as "Predictions" in the next. Keep only the first.
- `uv run mar results` lists README.md and ladder-live-diagnosis.md among "results" (only prereg, DRAFT and workbench files are skipped); the README text says the CLI prints "one verdict per results file".
- docs/surprises.md contains the same negotiation v1 lines (prediction 3 to 6 and the stay-commitment line) duplicated verbatim from negative-results.md. The two are meant to differ (misses versus unexpected observations); the v1 and v2 "FAIL" lines appear in both.

## Checked and consistent

- Claims-register counts agree with the results tables for V2, V2b, HH1, SL1, RD-VPGG (4 held, 1 missed; the verdict rule uses predictions 1, 2, 3, 5), RD-BARG, EM1 (prediction 2a was predicted to fail and is counted as held), EV1, EV2 (3 and 2), HH2, HH3a, SV2, LB1, LB2 (6 and 4).
- Numbers that appear in several places and agree: liberty VPGG (-19.6 to +5.263 bits; 4 of 15 then 11 of 15), VPGG std 0.013 to 0.020 against 0.05, seed v2 null (0.0003; 18 of 51), v3a (0.136 bits; 0 of 240; 6.087 against 6.411), evolution v2 prevalence 7 of 18 (needed 10), ladder spend ($4.35 equals the sum of the six per-model costs; Opus 232 of 540 calls and 70% of spend), negotiation v1 and v2 negative-result numbers against their results files (0.377, 0.989, 0.1495, 0.651/0.548/0.791, 0.933/0.956, 254 of 256).
- Code against definitions: household oracle weights (0.5/0.5 freedom, 0.35/0.25/0.20/0.20 cooperation, exit full credit at 0.5, leave open at 0.25) match docs/results/household.md; negotiation constants (deadline 12, floor 13 weeks x 2.0 = 26, 26-week rollouts, review every 13) match ADR 0013 and the v2 prereg; seam ladder depths (1, 2, 3, 2 with two agents, none) match docs/results/seam-ladder.md and ladder-live.md; liberty v2 classification (interference versus withdrawal) matches ADR 0014 decision 3.
- Claims C2's "19:55 and 20:15" match the two changes.jsonl entries; ADR 0014's cited topic names exist in questions.jsonl; dated and timestamped logs are in order (UTC against local commit times is consistent).

## Suggested order of repair

1. Fix the ladder status everywhere (finding 1), then index and claim the negotiation runs (2), then amend ADR 0013 for v2.1 (3). These three change what a reader believes about the state of the project.
2. Recompute the 5 of 9 versus 6 of 9 count (4).
3. Add the missing negative-results lines (6) and resolve CONTRIBUTING's rule against practice (5).
4. Record the statistics decision (7), then clear the low items.
