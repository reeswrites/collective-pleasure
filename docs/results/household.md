# Household world results: two scores and their trade-off

Status: instrument calibration with scripted agents. No LLM, no network. Findings are about rule systems and scripted agents, not about real people. Predictions: docs/results/household-prereg.md (committed before the household code ran, not edited since). Run: `uv run python scripts/household_run.py` (about 5 minutes, 15 s without `--no-ladder`), `uv run pytest tests/test_household*.py tests/test_frontier.py tests/test_seam_depth.py`. Report page: runs/household/frontier.html (not committed; regenerate).

## Table: actual vs preregistered

| # | Preregistered | Actual | Detail |
|---|---|---|---|
| 1a | trap fails the proof checks as "no exit within k"; a, b, c pass; d passes | PASS | check e fails for trap (card T1-forfeit) at k = 3, witness state has pooled assets above 0; a to d pass. contact_free (trap minus the contact veto) fails e too |
| 1b | trap freedom below 0.45, and below free_chaotic, exit_half, veto_consent | FAIL on the threshold, PASS on the ordering | trap freedom 0.487 (lowest of the seven, as predicted); the 0.45 line was missed. In mixes with a controller it is 0.29, without one 0.61 to 0.85 |
| 2 | free_chaotic freedom at least 0.85, cooperation below 0.55 and below baseline's | FAIL | freedom 0.995 (passes); cooperation 0.765, equal to baseline's, not below 0.55 |
| 3 | at least 2 variants non-dominated; free_chaotic on the frontier; trap not | PASS literally, but the frontier is trivial | frontier = free_chaotic and exit_half, which tie (0.995, 0.765). trap is dominated. There is no trade-off in this world: nothing sits at higher cooperation than 0.765 |
| 4 | gate, English round trip, mined-vs-written carry over from V2 | PASS | gate: 0 mismatches vs a plain-Python reference on every point of a grid per variant (pytest); all 20 household cards round-trip unchanged; mined rules agree with the written gate on every visited signature (143 to 253 per variant, 0 disagreements). Unvisited signatures: 704 per variant, 0 disagreements except veto_consent (16, a coverage gap: the explorer never reached those consent states) |

Mean (freedom, cooperation) over 6 mixes x 3 seeds: trap (0.487, 0.639); contact_free (0.552, 0.704); veto_consent (0.975, 0.681); needs_duty (0.989, 0.765); baseline (0.989, 0.765); free_chaotic (0.995, 0.765); exit_half (0.995, 0.765).

## What the failures say (not edited into the prereg)

Cooperation does not separate the rule systems that leave exit and contact alone. The cause is structural: a gate only forbids actions, so "shared-needs duty" (needs_duty, baseline) cannot make an independent agent fund the need; independents simply never contribute, in every variant, and cooperators always do. Cooperation in this world is driven by who the agents are, not by the free-versus-duty rules. Only the controller-and-veto rules move it (trap 0.47 in the controller mixes against 0.97 for free_chaotic with a cooperative partner). So the world as built shows a one-sided effect (bad rules cost both scores) but no frontier trade-off. A real trade-off would need rules that can bind contributions (obligations with enforced sanctions, or an exit cost that persists), which sanctions-not-enforced (below) rules out. Recorded as a negative result for the author to read before the evolution loop is pointed at these scores.

## Formulas (frozen in the prereg; implemented in src/mar/household_oracle.py)

FREEDOM per partner and month = 0.5 * (open options / 5) + 0.5 * min(1, exit_retained / 0.5); options: work, spend, see friend, refuse, leave; leave open iff exit_retained >= 0.25. COOPERATION per month = 0.35 * needs met + 0.25 * both partners in + 0.20 * (partners contributing / 2) + 0.20 * (1 - friend's blocked share). Both are means over months, then over mixes and seeds. Weights are the builder's choice (ASSUMED) and are not tuned.

## Proof checks (k = 3)

a no conflict, b no deadlock, c bounded sanctions (patch_check.check_sanctions reused), d repair path under warn / cap_halve / suspend, e exit within k (some leave carrying at least 25 percent of the pooled share is permitted in every state, now or after waiting up to k months). Bound: pooled 0..100, money 0..100, months_in 0..36, need_gap 0..10, flags 0..1, leave take 0..100. A unit test shows a 6-month lock-in fails e at k = 3 and passes at k = 6. Verdicts hold within the bound only.

## ASSUMED choices

- compile.py, gate.py, patch_check.py, english.py are fishery-specific. Adapter in src/mar/worlds/household.py: reuses cards.py, compile.violation, english.render and english.parse by swapping the variable names in temporarily (restored on exit); gate and checks a, b, d, e re-implemented over household variables with V2's semantics. english.explain_verdict and explain_trace are fishery-only, so household verdicts and stories use fallback narrators (explain_verdict, scripts/household_run.py story).
- Sanctions are declared and checked, not enforced. suspend allows only work, spend_shared, refuse_request; cap_halve bars spend_self.
- Exit check uses take >= 25 as a sufficient proxy for retaining 25 percent (ignores private money).
- Incomes A 8 and B 6 per work, need 10 a month (6 for a one-person household), 8 free hours; scripted agent rules in household.py. Controller issues one request a month; consent to a request is a scripted attribute of the target.
- Friend harm = blocked contact attempts only (one attempt a month, alternating partners).
- Scripted agents are single-script; seeds only vary the cooperators' choice of see friend or spend on self.

## What the CLI integration will need (cli.py belongs to the other agent)

- `mar.worlds.household.load_variant(name) -> list[Card]`, `VARIANTS`, `MIXES`, `make_agents(mix) -> dict`
- `household.check_spec(cards, k=3) -> list[verdict]`; `household.explain_verdict(verdict, cards) -> str`; `household.render_card(card) -> str`, `parse_card(text) -> Card`
- `household.run_household(cards, agents, seed=0, months=12) -> Run(trace, outcomes, final)`
- `mar.household_oracle.score(outcomes) -> {"freedom", "cooperation", "months"}`
- `mar.frontier.pareto(points) -> list[str]`, `aggregate(points)`, `frontier_chart(points, theme) -> svg string`
- `mar.seam_depth.classify_seam(run, rules, k=3) -> {"kind": "predicted"|"inventive"|"open"|"none", ...}`, `search(cards, k)`, `ladder_table() -> (rows, inventive)`, `ladder_score(rows, agent, inventive)`
- `scripts/household_run.py:main(ladder=True)` builds everything and the page; a CLI command could call it.
