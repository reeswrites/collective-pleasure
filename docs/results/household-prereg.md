# Household world preregistration (committed before any household code runs)

Status: instrument calibration on a scripted world. Findings are about rule systems and scripted AI agents, not about real people or groups. Abstract roles only: Partner A, Partner B, Friend C (outside the household). Roles have no gender and no historical group meaning; "earner" just means Partner A has the higher income in the fixture. All agents are scripted; no LLM, no network.

Decided by the author on 2026-11-10: the household is the main scenario; the alignment objective is two scores, FREEDOM and COOPERATION, and evolution is meant to map the trade-off between them (a Pareto frontier), not maximize one number.

## Setup (fixed now)

- World: monthly steps, 12 months, 3 action slots per role per month, 8 free hours per month (work costs 4, see friend 2, spend 1). Partners: work, spend_shared, spend_self, see_friend, refuse_request, request, leave, return. Friend C has a reduced set (work, spend_self, see_friend, refuse_request). Dynamics are deterministic code; scripted agents use a seeded rng only for small choices.
- Seven hand-written variants (ADICO cards in rules/household/): free_chaotic (permissions only), trap (pooled-asset forfeit on exit, earner veto on the other partner's outside contact and work, no refusing a standing request), contact_free (trap minus the contact veto), exit_half (exit with half the pooled assets, nothing else), veto_consent (earner request binds only if the other partner has not refused), needs_duty (no self-spending while the shared need is unfunded, with a warn sanction), baseline (exit with half, contact never vetoed, needs duty).
- Scripted agent mixes (A and B): cooperator/cooperator, controller/cooperator, controller/leaver, independent/independent, cooperator/leaver, controller/independent. Seeds 0, 1, 2. A variant's point is the mean over mixes and seeds.
- Bounds for every proof verdict: k = 3 months (sanction repair path, as V2; exit wait). State ranges: pooled 0..100, money 0..100, months_in 0..36, need_gap 0..10, flags 0..1, leave take 0..100. "Open" never means safe.
- Meaningful exit: leaving with at least 25 percent of net worth. Probed take values: 0, 10, 25, 50, 75, 100.

## Scores (formulas frozen now; the oracle reads outcomes only, never the rules)

FREEDOM, per partner and month: 0.5 * (open options / 5) + 0.5 * min(1, exit_retained / 0.5). Options: work, spend (shared or self), see friend, refuse, leave. Open means the rules permit it and it is physically possible; leave counts as open only if exit_retained >= 0.25. exit_retained = best fraction of net worth the partner could leave with now (0 if leave is not permitted); a partner who has left keeps the fraction retained at departure. Mean over partners and months.

COOPERATION, per month: 0.35 needs met + 0.25 household persists (both partners in) + 0.20 mutual aid (partners in the household making a shared contribution, divided by 2) + 0.20 no harm to C (1 minus the share of C's contact attempts that were blocked). Mean over months. Stability lives inside cooperation.

## Predictions

1. **The trap fails the proof checks and has low freedom.** Check e (exit within k: in every state some leave retaining at least 25 percent is permitted, now or within k = 3 months) fails for the trap, with a witness state where pooled assets are above 0. Checks a (conflict), b (deadlock) and c (bounded sanctions) pass; d (repair path) passes. Trap freedom is below 0.45 and strictly lower than free_chaotic, exit_half and veto_consent.
2. **free_chaotic is free but not cooperative.** Freedom at least 0.85, cooperation below 0.55 and below baseline's cooperation.
3. **A non-trivial frontier exists.** At least 2 of the 7 variants are non-dominated on (freedom, cooperation); free_chaotic is one of them; trap is not.
4. **The V2 instrument checks carry over.** Gate agrees with an independent plain-Python reference on every point of an exhaustive grid (0 mismatches); every household card round-trips through the English form unchanged; mined rules agree with the written gate on every state signature the explorer visited (coverage of the full signature grid reported, not required).

If a prediction fails it stays failed here; results go in docs/results/household.md. Dual-use: no population stands in for a real group; adversarial agents (controller, leaver) test rule systems only, and findings are reported as defenses.
