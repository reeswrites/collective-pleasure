# Liberty v2 in the household: adapter and a descriptive check (2026-11-10)

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: DESCRIPTIVE check run. There is no preregistered prediction here, no verdict, and no threshold; it is a measurement that makes the household usable by the evolution run (slice 1). Scripted persona-driven agents, no model calls. Code: `src/mar/empowerment.py` (`HH_CLASS`, `hh_class`, `HouseholdWorld.classify / noop / force_policy`), `src/mar/liberty.py` (`household_liberty`, `household_run_liberty`). Run: `uv run python scripts/household_liberty_check.py` (170 s on 8 cores, 855 runs; rows in `runs/household-liberty/rows.json`, not committed). Tests: `uv run pytest -q tests/test_liberty.py`.

## The classification table (ASSUMED; the household owner has not confirmed it)

This implements the table proposed in docs/results/liberty-v2.md ("What the household adapter must expose") for the actions the empowerment menu actually has. Interference acts on another member's own options; withdrawal declines to act or leaves with one's own share (ADR 0014 decision 3: the loss from withdrawal is real but is booked to cooperation and the hedonic model, not to freedom).

| Action | Class | Rationale |
|---|---|---|
| veto (no_contact), veto (spend) | interference | blocks the other's own contact or own spending: acts on the other's options |
| take_shared | interference | draws on the one pot the other's futures depend on; the harm test then decides whether it is compatible |
| leave, take 100 | interference | carries the other's half of the pot out: takes what is the other's own |
| leave, take 0 or 50 | withdrawal | own exit carrying no more than the equal split |
| rest | withdrawal | restraint, declines to act |
| refuse_request | withdrawal | declines to supply what was asked |
| work, spend_self, see_friend, return | own | own labour, own money, own contact, own re-entry |
| spend_shared | own | puts one's own money into the shared pot or bills |
| together | own | joint time. It needs the partner's time (the model charges the partner's units), so it is agreement-dependent in spirit; the adapter does not exclude it as an agreement-dependent option |
| request (no_contact, stay_home, time) | own | asking is not blocking: the partner can refuse. A request with an outside sanction would be interference, and the menu has none |

Not modeled (stated, as the v2 results file already said): gifts, request commitments, `commit_stay` and its breach. A stay commitment is honored as a hard block on leaving (HouseholdWorld.decide); contract-owed cooperation is left to the hedonic layer.

Other choices (ASSUMED): horizon k = 2 passes (plain empowerment in v3a used k = 3; liberty at k = 3 is much more expensive); snapshots at weeks 0, 52, 104; the scripted others are the persona's script (cooperator, controller, freerider, overasker); a partner's liberty is the lower of the two partners' liberty, averaged over snapshots; weight w = 1. Plain empowerment in the table is at the same k = 2 so the columns compare (the v3a numbers at k = 3 are 0.5 to 1 bit higher).

## Result (57 pairings x 1 seed x 156 weeks; mean over runs)

| rule set | hand-made freedom | plain empowerment (bits, k=2) | liberty v2 (bits, k=2) | domination exposure d | agreement-dependent options | cooperation | pleasure | fail share |
|---|---|---|---|---|---|---|---|---|
| baseline | 0.999 | 5.05 | 2.09 | 2.72 | 3.64 | 0.725 | 0.745 | 0.35 |
| needs_duty | 1.000 | 5.35 | 1.14 | 8.60 | 4.41 | 0.725 | 0.745 | 0.35 |
| share_duty | 1.000 | 5.33 | 1.11 | 9.07 | 4.83 | 0.723 | 0.748 | 0.33 |
| no_pressure_wall | 1.000 | 5.10 | 0.83 | 6.93 | 4.31 | 0.860 | 0.850 | 0.12 |
| no_pressure_sanctioned | 0.998 | 5.14 | 1.00 | 12.68 | 8.65 | 0.596 | 0.717 | 0.39 |
| free_chaotic | 1.000 | 5.27 | 0.93 | 9.26 | 4.70 | 0.704 | 0.721 | 0.39 |
| exit_half | 0.999 | 4.98 | 2.08 | 2.68 | 3.45 | 0.704 | 0.721 | 0.39 |
| veto_consent | 0.999 | 5.27 | 0.93 | 9.44 | 4.90 | 0.704 | 0.721 | 0.39 |
| author_seed | 0.999 | 4.98 | 2.08 | 2.68 | 3.45 | 0.704 | 0.721 | 0.39 |
| author_seed_nocontrol | 1.000 | 4.59 | 3.64 | 0.61 | 3.08 | 0.747 | 0.750 | 0.35 |
| author_seed_v2_bindable | 0.955 | 4.85 | 1.46 | 7.98 | 3.44 | 0.720 | 0.748 | 0.35 |
| author_seed_v2_free_exit | 1.000 | 4.95 | 1.03 | 9.34 | 4.03 | 0.727 | 0.748 | 0.35 |
| author_seed_v2_nocommit | 1.000 | 4.95 | 1.03 | 9.35 | 4.04 | 0.727 | 0.748 | 0.35 |
| trap (control) | 0.815 | 4.78 | 1.81 | 2.94 | 3.57 | 0.569 | 0.647 | 1.00 |
| contact_free (control) | 0.817 | 4.79 | 1.81 | 2.93 | 3.52 | 0.568 | 0.647 | 1.00 |

No snapshot hit the expansion cap (0 open of 2,565).

## What it shows

- **The three freedom readings disagree, as ADR 0014 said they could.** Across the 15 rule sets, the rank correlation of liberty with the hand-made freedom score is -0.34 and with plain empowerment -0.52 (Spearman over 15 variant means; descriptive, n = 15). The hand-made score is about 1.0 for every rule set except the two exit-trap controls (0.82) and the bindable variant (0.955); it does not separate the rest. Liberty ranges from 0.83 to 3.64 bits; plain empowerment from 4.59 to 5.35.
- **Largest driver: an exit that may carry the whole pot.** In every rule set with no card limiting the take on leaving, the main domination exposure is the other partner's `leave` at take 100 (a withdrawal that is not a withdrawal: it takes the other's half). Those sets have d about 7 to 13 and liberty about 0.8 to 1.5 bits (needs_duty, share_duty, no_pressure_*, free_chaotic, veto_consent, both v2 seed variants). The sets with an exit-split wall (baseline E1 and E2, exit_half, author_seed's S3a and S3b) have d about 2.7 and liberty about 2.1. author_seed_nocontrol is highest (3.64, d 0.61). This is the ADR's rule applied to a world where the seed's imposed variants have no negotiated exit term (seed v2 in the negotiated protocol compiles one; imposed here, as in household v2 runs). It is a statement about these imposed rule sets, not about the author's negotiated agreements.
- **Free exit is cheap in plain empowerment and costly in liberty.** Plain empowerment is highest for the permissive sets (5.3 to 5.35) and lowest for the nocontrol set; liberty is the reverse.
- **It does not see the trap.** The two controls built to trap a partner score liberty 1.81, above both v2 seed variants (1.0 to 1.5), and plain empowerment 4.78. The window is k = 2 passes, one week; the trap works over months (an exit lock with a waiting time), which the window cannot reach. The hand-made score (0.82) and the fail share (1.00) do see it. So liberty at this horizon is not a trap detector and must not be the only freedom objective.
- **Liberty and the hedonic scores are nearly unrelated.** Spearman with pleasure -0.13 and with cooperation -0.08 (n = 15). That is what keeps it a real objective in the evolution run rather than a restatement of pleasure.
- **Pressing pairs read higher than control pairs** (1.66 vs 1.17 bits): in the pressing cohort the scripted other is a controller, freerider or overasker, whose scripted moves change which interference exists at a snapshot. Descriptive only.

## Limits

First-step blocking and a count-based harm test (as in liberty v2); k = 2 and three snapshots; scripted others fixed at the persona's script; the classification table is ASSUMED and judged against ADR 0014, not validated; one seed per pairing and unit-level intervals were not computed because nothing here is a test. The `together` action charges the partner's time units and is classed `own`: if the household owner prefers `interference`, `HH_CLASS["together"]` is the one line to change.
