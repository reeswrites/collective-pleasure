# Repo split map: does the code support engine + social + alignment?

Written 2026-11-11. Analysis only. No code was moved. The import graph was computed with a short `ast` script kept outside the repo (it follows lazy imports inside functions too). Another agent is editing `exit_fallback.py`, `exit_items.py` and their tests, so treat their numbers as a snapshot.

## Short answer

The three-way split is **messy, and not worth doing**. The reason is one fact. The alignment track does not run on its own world. IT1, the live ladder and seam depth all run inside the household world, and they import the household world, the household oracle and the personas. Those are the social repo's core.

So the repo shape is not three peers. It is one engine, a large social application, and a thin alignment layer that sits on top of social. Alignment is about 2,400 of 19,200 lines (12%), 6 of 41 indexed experiments, and 4 of 38 hypotheses.

Recommendation: keep one repo and add track folders and track tags. Revisit a split only if the audiences actually diverge.

## 1. Every module in src/mar

Sizes are lines. "Used by" is evidence from scripts/ and tests/ (counts of files that import the module).

Totals by side: social about 9,200 lines, engine about 6,500, alignment about 2,400, cli about 1,000 (mixed).

### Engine

| Module | Reason |
|---|---|
| cards.py (59) | ADICO card type and loader. Imported by 14 modules, 14 scripts, 21 tests. Imports nothing. |
| compile.py (51), gate.py (32) | Z3 gate. Imports only each other. Used by every world. |
| patch_check.py, redundancy.py, patcher.py | Solver checks, redundancy pruning, patch proposals. Imports only engine modules. |
| english.py | Cards to plain English. Engine only, with a few fishery strings. |
| oracle.py | The fishery outcome oracle. Imports nothing (a test enforces it). Engine reference oracle. |
| log.py, timeline.py, stats.py, viz.py, frontier.py | Experiment logs, timeline page, statistics layer (17 scripts use stats), charts. Generic. Frontier plots freedom against cooperation, which are household scores, but it only imports viz. |
| agents/* (10 files) | LLM and Jev backends, ledger, budget, parser. Imports nothing from mar. Used by alignment (it1, ladder_live) and social (negotiation_llm). Neutral. |
| empowerment.py, liberty.py | The evaluator. Core code is generic, but each carries a household adapter (see cross-edges). |
| lint.py | Rule-set lint. Generic checks plus household-only checks b and c. Leans on the household world (see cross-edges). |
| world_api.py, evolve.py | Evolution loop. evolve.py imports only world_api. world_api is two files in one (see cross-edges). |
| fishery.py, mocks.py, miner.py, report.py | The original fishery MVP stack (V1 to V2). Self-contained. Nothing in alignment uses it anymore. Engine reference world, but see "Unclear". |
| games/vpgg.py | Public-goods game used by the evaluator tests and multiverse. Engine reference game. |

### Social

| Module | Reason |
|---|---|
| worlds/household.py (2,129) | The household world. The largest file. 24 tests and 13 scripts use it. |
| hedonic.py | Pleasure and suffering model. 6 scripts, 8 tests. |
| negotiation.py (1,199), negotiation_llm.py | Pot and term negotiation, and the LLM negotiators. |
| personas.py | Persona layer. 21 tests use it. Alignment also uses it. |
| household_oracle.py | Freedom and cooperation scores from household outcomes. Alignment also uses it. |
| pleasure_report.py, horizon.py, convergence.py, care.py, wanting.py, regulation.py | The hedonic tests and H32 to H35 models. Pure social. |
| fidelity.py, retest.py, stay_test.py, loss_report.py | Social evaluator tests and reports built on the household. |
| exit_fallback.py, exit_items.py | Exit fallbacks (under active edit). They form a cycle with worlds/household.py. |
| multiverse.py | Sweep over eight conclusions. Seven are household or hedonic, two are VPGG or horizon. Social. |
| games/bargaining.py | Rubinstein rung. Engine-style toy, but it only feeds negotiation work. Leans social. |

### Alignment

| Module | Reason |
|---|---|
| it1.py (709) | IT1 profit cells. Imports ladder_live, seam_depth, household_oracle and the household world. |
| ladder_live.py (1,445) | The live seam ladder on the household world. Imports lint and personas too. |
| seam_depth.py (239) | Seam depth model. Imports only household_oracle and the household world. |

### Unclear

- **cli.py (999).** One CLI for all of it: fishery run, loop, household, personas, ladder, lint, evolve, game, empower. It imports 21 modules across all three sides. It would have to be split into three CLIs.
- **The fishery stack (fishery, report, miner, mocks, oracle, viz).** Engine reference code, but it is also the original alignment story (the planted-seam fishery). Alignment no longer touches it. It would stay with the engine as the example world.
- **household_oracle, personas, worlds/household.** Social code that alignment cannot live without. If you want alignment as a separate repo, these decide the shape (see the verdict).

## 2. Cross-edges that would break a three-way split

The graph has 42 module-level edges that cross a side. Direction and count:

- alignment imports engine: 10 (fine, expected)
- social imports engine: 16 (fine, expected)
- engine imports social: 9 (bad)
- alignment imports social: 7 (bad for a peer split)
- social imports alignment: 0
- alignment imports social through the world only. No module-to-module import among the three alignment files crosses a boundary.

**A. Engine imports social (9 edges). Hardest for the engine repo.**

1. `world_api.py` holds two adapters in one file. Lines 1 to 413 are the fishery adapter (engine). Lines 413 to 948 are the household evolution world. The second half imports empowerment, household_oracle, hedonic, lint, liberty, negotiation, personas and the household world at module level. **Cut: easy and mechanical.** Split the file at line 413 and move the household half into social as `household_evolve_world.py`. About half a day. Test impact: `test_evolve_household*.py` and 7 scripts change an import.
2. `lint.py` imports the household world at module level (`from .worlds import household as H`), and `negotiation` lazily. Its household-only checks (no partner without a legal exit, gloss versus fields) are mixed with the generic checks. **Cut: medium.** Needs a plug-in point so each world registers its own checks. The ladder also calls lint (ladder_live line 1315), so alignment needs it too.
3. `empowerment.py` (line 196) has a lazy household adapter. `liberty.py` (line 335) lazily reads `hedonic.DEFAULT`. **Cut: easy** for the imports (move the adapters to social). **Hard** for the tests: `test_empowerment` and `test_liberty` use household personas and worlds, and the evaluator's credibility rests on those household checks.
4. `lint.py`, `empowerment.py` and `liberty.py` are the evaluator the author says is the product. Cutting the household out of them cuts the part that has been validated.

**B. Alignment imports social (7 edges). Cannot be cut without changing the design.**

1. `it1`, `ladder_live` and `seam_depth` all import the household world (`worlds/household.py`) and `household_oracle`. `ladder_live` also imports `personas`.
2. A seam is defined by the household oracle (`household_oracle.seam_flag`: victim freedom drop or friend shut-out). The seam depth model is a model of the household's own moves. **Cut: not possible without moving the household world.**
3. Options: (a) alignment depends on social (not peers); (b) lift worlds/household.py, household_oracle.py and personas.py into the engine repo (the engine then holds about 2,900 more lines and the household becomes "the reference world"); (c) give alignment its own world (a rewrite, and the whole IT1 result is tied to the household).

**C. Cycle inside social.** `worlds/household.py` imports `exit_fallback` and `exit_items`. `exit_fallback` imports `worlds.household` (lazily), `hedonic` and `negotiation`. `exit_items` imports `exit_fallback`. All three are in social, so a split does not break it, but it means those three files must move together. They are under active edit.

**D. Social and alignment do not import each other in the code.** They share only the household world. That is the clean part.

## 3. Tests, scripts and rules

### Scripts (41)

- **Engine (about 11):** `empowerment_run`, `evolve_run`, `evolve_v2_run`, `liberty_run`, `lint_rules`, `loop_b_count`, `stats_retrofit`, `v2_run`, `v2b_run`, `vpgg_run`, and `hypotheses.py` (log tool).
- **Alignment (6):** `it1_run`, `it1_gate`, `it1_analyze`, `it1_seam_exists`, `ladder_live_run`, `ladder_live_analyze`. Four of these also import household_oracle or the household world.
- **Social (about 22):** the `h01`, `h09`, `h32`, `h32b`, `h32v2`, `h35` runs, `horizon_run`, `fidelity_run`, `bargaining_run`, `exit_fallbacks_run`, all `household_*` scripts, `liking_wanting_run`, `multiverse_run`, `negotiation_llm_run`, `pleasure_*`, `regulation_run`, `stay_test_run`, `v2_retest_run`.
- **Mixed (2):** `demo_check.py` (goes through the CLI), `household_run.py` (imports seam_depth).

### Tests (about 62 files)

- **Engine (about 22):** `agents`, `english`, `evolve`, `fishery`, `gate`, `lint`, `miner`, `oracle`, `patch`, `redundancy`, `stats`, `viz`, `vpgg`, `log`, `changes`, `claude`, `backend_runs`, `questions`, `timeline`, `frontier`, and a few more. About half of these also import the CLI.
- **Alignment (4):** `test_it1`, `test_ladder_live`, `test_ladder_pin`, `test_seam_depth`. All four build the household world.
- **Social (about 35):** all `test_household_*`, `test_negotiation*`, `test_hedonic`, `test_horizon`, `test_convergence`, `test_care`, `test_wanting`, `test_regulation`, `test_stay_test`, `test_exit_*`, `test_pleasure_report`, `test_personas`, `test_levers*`, `test_multiverse`, `test_fidelity`, `test_h01_h09`, `test_trust_v22`, and others.
- **Mixed:** `test_cli.py`, `test_rules_readme.py` (reads rules/README.md plus household worlds), and `test_empowerment`, `test_liberty` (engine tests that need household).
- Slow tests list (`tests/slow_tests.txt`) and `tests/data` (ladder pin, lever fingerprints) follow their owners: ladder pin to alignment, lever fingerprints to social.

### rules/ and personas/

- **rules/household/ (18 variants), rules/bargaining/, personas/ (8 files):** social.
- **rules/fishery/, rules/fishery-en/, rules/vpgg/:** engine (reference worlds).
- **rules/README.md:** explains how cards read in every world, so it is engine documentation that quotes household behaviour. `test_rules_readme.py` ties it to the household code.
- **Alignment has no rules of its own.** Its ladder rule sets are the `ladder` variants inside `rules/household/`.

## 4. The logs in experiments/

The rows carry no track tag, so a split needs a hand-made classification. These counts are from reading each row's id, kind or topic. They are judgement calls at the edges.

| File | Rows | Social | Alignment | Engine or mixed |
|---|---|---|---|---|
| hypotheses.jsonl | 38 | 31 | 4 (H10 to H13, group "ladder") | 3 (H14 to H16, evolution tested on the household) |
| questions.jsonl | 93 | 64 | 8 (ladder, seams, win framing, network-alignment, cognition price) | 21 (14 founding and framing, 7 that straddle) |
| changes.jsonl | 29 | 20 (4 rule, 1 oracle, 15 decisions) | 2 (both IT1 decisions) | 7 (README, scope review, council, read-back log, loop b, split) |
| log.jsonl | 11 | 7 | 4 (all `it1_*`) | 0 |
| readbacks.jsonl | 5 | 5 (all exit fallbacks) | 0 | 0 |

Also under experiments/: `kept/` has 16 run folders (10 social, 6 alignment: the ladder runs and it1), and `timelines/` is generated from all of the above.

How they could split. Four rows in five are social. The mixed rows are the founding questions (the alignment framing of the whole project) and the repo-level decisions. If the repo splits, the practical choice is: social keeps the full logs as history, alignment gets a copy of its 4 + 8 + 2 + 4 rows with a `home` note, and the founding rows are duplicated into both. A cleaner split would break `mar log`, `mar change`, `mar question` and `mar timeline`, which read fixed paths and merge all files in time order. In one repo, the cheaper fix is a `track` field on each row (about 220 rows, 1 to 2 hours by hand plus a script), which makes any later split a filter.

## 5. Docs

| Doc | Side |
|---|---|
| README.md | Mixed by design. It frames the project as alignment, with relationships as the testbed. About half of the "what we found" list is alignment-relevant by its own argument. Would need two rewrites. |
| RATIONALE.md, docs/goal.md, docs/theory.md, docs/pitch.md, docs/one-pager.md | Mixed. The founding question is alignment. theory.md and most of goal.md are social. |
| docs/claims.md, docs/limits.md, docs/plan.md, docs/negative-results.md, docs/surprises.md, docs/hypotheses.md | Mixed. Each interleaves tracks (the plan queue puts IT1 at item 1 and household evolution at item 2). Splitting means splitting each file in two. |
| docs/decisions (ADRs 0001 to 0018) | Engine or founding: 0001 to 0005, 0009, 0012, 0014, 0015. Alignment: 0006 (stand-in study), 0007 (inventive seams). Social: 0008, 0010, 0011, 0013, 0016, 0017, 0018. |
| docs/results/ (111 files) | By file: social 56, alignment 16 (ladder, seam-ladder, it1), engine 25, evolution-on-household 14. By the 41-row results index: social 25, engine 10, alignment 6. |
| docs/notes, docs/seeds, docs/templates | Social (the hedonic synthesis, the author's household seed). Templates are engine. |
| docs/reviews, docs/prior-art, docs/conversations, docs/plans | Mixed. docs/plans/inventive-seam-next.md is alignment. |
| docs/demo.md | Social (household demo). |

Most of the writing that would be hardest to split is the mixed top-level set: README, claims, limits, plan, goal. Those are also what a reader sees first.

## 6. Verdict

**A three-way split is messy and not worth it.** It is doable, but the result is worse than the starting point.

Reasons, in order:

1. Alignment is not a peer. It runs on the household world, so "alignment depends on social" is the only honest dependency. A split into three repos would have alignment importing both of the others, with the household world as the hinge.
2. The engine is not yet clean. `world_api.py`, `lint.py`, `empowerment.py` and `liberty.py` all reach into the household. The evaluator is the part the author calls the product, and its validation is household-based.
3. Alignment is small: about 2,400 lines, 6 of 41 experiments, 4 of 38 hypotheses, and its central claim (inventive seams) is still untested. A repo for it would be a thin layer on two others, with its own pin, CI and docs.
4. The docs that matter most (README, claims, plan, limits) are mixed and would each need splitting.

### Options compared

| Option | What it is | Effort | Cost and risk |
|---|---|---|---|
| **One repo, clearer track folders (recommended)** | Add a `track` tag to log rows and docs rows. Group docs/results and scripts by track in the index. Optionally split `world_api.py` at line 413 and add a lint plug-in point, so the engine stops importing social. | 0.5 to 1 day for tags and indexes. Plus 0.5 to 1 day for the world_api split and lint hook. | Low. Nothing breaks. Keeps the founding framing intact. Does not give separate repos. |
| **Two-way: social keeps the engine, alignment depends on it** | Move it1, ladder_live, seam_depth, their 6 scripts, 4 tests, 16 results docs, ADRs 0006 and 0007, and about 22 log rows into a new repo that pins the first. | 2 to 3 days. Includes a package pin, a copy of the rows, an updated CLI (`ladder` command), and duplicated founding docs. | Medium. The alignment repo would still import the household world, the oracle and the personas, so any change to those is a breaking change for it. Two repos to keep in step for a 2,400-line layer. Reasonable only if alignment gets its own audience or a model-cost budget that needs isolation. |
| **Three-way: engine, social, alignment** | Lift the engine out, with household code split off from world_api, lint, empowerment and liberty. Social and alignment both depend on engine. Alignment also depends on social, or the household world moves into engine. | 1 to 2 weeks. Rewriting the evaluator's household hooks, splitting the CLI into three, splitting the mixed docs and logs, re-homing about 60 tests, and a pin for each edge. | High. The engine would be small (about 6,500 lines) and its validation would live in social. The household world either bloats the engine or stays outside it, forcing alignment to depend on social anyway. Same pin-and-sync cost as the earlier exo split, twice over. |

### What would change this verdict

- If alignment gets a world of its own that does not use the household (for example a return to fishery-style games or an external benchmark), it becomes a real peer and the two-way split gets cheaper.
- If the engine gets a stable world interface that `evolve`, `lint`, `empowerment` and `liberty` use without importing any world, the engine becomes a clean extraction. The first step toward that (splitting world_api and adding a lint hook) is useful in the one-repo option too, so it is not wasted work.
- If the exit-fallback work settles, the cycle between the household world and `exit_fallback` / `exit_items` stops being a moving target.

### Cheap first moves, whichever way this goes

1. Split `world_api.py` at line 413.
2. Move the household adapters out of `empowerment.py`, `liberty.py` and `lint.py` behind a registration call.
3. Add a `track` field to the log rows.
4. Tag docs/results/README.md rows by track.

None of these needs to wait for the exit-fallback edits to finish, except moving the household adapters if they touch `exit_fallback`.
