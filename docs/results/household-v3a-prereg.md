# Household v3a preregistration (2026-11-10, committed BEFORE any v3a run, pilot or full)

Status: instrument, scripted agents, no LLM, no network. Findings are about rule systems and scripted agents with modeled preferences, not about real people. Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences. Parents: docs/results/household-v2.md (3 of 5 predictions missed), docs/results/empowerment.md (adapter requirements), ADR 0010 and 0011. Results go in docs/results/household-v3a.md. This file is not edited after this commit; a change needs a new dated amendment section appended BEFORE the full run.

Diagnosis acted on. (a) Freedom saturated at 1.000 because the hand-made score is coarse: it counts which of five options the rules leave open. (b) The v2 world had no conflict: persona agents pursued their own needs politely, never pressed on each other, so no rule had anything to restrain. v3a adds an empowerment-based freedom score (reported ALONGSIDE the hand-made one, which is unchanged) and three pressing personas whose scripted policies push against the partner.

Pilot policy. Any pilot run before the full run is labeled EXPLORATORY here and in the results file, and changes no parameter below. Planned pilots: none beyond unit tests and a smoke run of one run per code path. If a parameter must change after a pilot, an amendment (dated, with the reason) is appended to this file before the full run.

## Frozen v2 parameters (unchanged, from docs/results/household-v2.md)

HedonicConfig (src/mar/hedonic.py) and the world constants of src/mar/worlds/household.py as in v2, including: 156 weeks, 4-week month, 3 passes a week, 10 units a week, incomes 6 and 5, bills 10 per 4 weeks (6 alone), shocks at v2 rates with common random numbers per (seed, pair), upward margin 0.20, tail 8 weeks, fail at 6 consecutive weeks of non-offsettable suffering, a variant FAILS when at least one third of its runs fail. The seeds are 0, 1, 2. Nothing in the v2 file is retuned.

## New world physics (all ASSUMED; constants fixed now)

Three actions are added to the weekly world; none is used by a v2 agent, so v2 runs are bit-identical (checked by hash before and after).

- `veto` (kind `no_contact` or `spend`): costs 1 unit; feasible when both partners are in the household and no veto of that kind already stands on the target. For 4 weeks (VETO_WEEKS) the target's `see_friend` (no_contact) or `spend_self` (spend) is a hard block ("vetoed"). It is not refusable. Vetoes enter the freedom probe, so a steadily vetoed partner is "restricted" and the diminished-condition clock (onset 4 weeks) runs. The gate sees the action with aim `veto`; a `must_not veto` card restrains it. Default (no card): permitted.
- `request` gains kind `time` (the v2 kinds no_contact and stay_home are unchanged). Each `time` request received adds 0.10 offsettable suffering (PRESS_FRICTION) to the target that week. Consent follows the v2 consent rule; a refusal uses one of the target's three action slots in the week.
- `take_shared`: costs 1 unit; feasible when both are in and the partner's pooled share is at least 1, at most once per week per agent; moves min(3, partner pooled) from the partner's pooled share into the actor's private money (TAKE_SHARED = 3). The gate sees aim `take_shared`.
- Soft/hard semantics are v2's: a card with `or_else` is soft (breaking it costs the sanction, estimate 0.01 per week for warn and cap_halve, 0.02 for suspend, times 4 weeks times months); a card without one is a wall. An active `suspend` sanction blocks veto and take_shared (only work, spend_shared, refuse, rest remain); `cap_halve` blocks spend_self.

## Pressing personas (three; principles, backstory, profile, needs and aspirations; no group identities; files in personas/pressing/)

Axes (certainty_openness, togetherness_independence, security_adventure, giving_keeping, directness_avoidance); weights, style and risk come from the v2 ASSUMED mapping `profile_from_axes`; needs and aspirations from the v2 ASSUMED defaults.

| id | axes | resulting style | pressing policy (utility before the v2 seeded noise of plus or minus 10 percent) |
|---|---|---|---|
| p-controller | 0.1, 0.2, 0.2, 0.9, 0.1 | competitive (never consents) | veto no_contact: 0.25 + 0.3 x togetherness weight; veto spend: 0.15 + 0.3 x money weight; each only when none of that kind stands; fallbacks when vetoes are walled: request no_contact 0.12, request stay_home 0.11 |
| p-freerider | 0.6, 0.7, 0.7, 0.9, 0.8 | avoidant | take_shared: 0.30 + 0.3 x money weight whenever feasible; spend_shared utility x 0.1; work utility x 0.5 |
| p-overasker | 0.2, 0.1, 0.3, 0.2, 0.3 | collaborative | request kind time: 0.20 + 0.3 x togetherness weight whenever none of its requests stands on the partner |

The candidate list is ranked with the v2 utilities; the world executes the best candidate that is feasible and not hard-blocked. A persona's `press=False` switch removes the pressing candidates (used for twin runs).

## New rule variants (rules/household/, each card with plain-English gloss and source)

v3a runs 12 variants: the 8 of v2 (free_chaotic, trap, contact_free, exit_half, veto_consent, needs_duty, baseline, author_seed; the six-card `author_seed` is untouched) plus four:

- `author_seed_nocontrol`: the six author cards plus S6 `must_not veto` (hard), sourced to the author's words "request is never about control" (the v2 encoding of that line, a `may refuse` permission, does not bind anything; S6 is the author's sentence read as a prohibition; ASSUMED reading).
- `no_pressure_wall`: three hard cards: `must_not veto`, `must_not request`, `must_not take_shared`.
- `no_pressure_sanctioned`: the same three, soft: veto suspend 1 month, request warn 1 month, take_shared cap_halve 2 months (sanctioner household).
- `share_duty`: v2's D1 needs-first plus a soft `must_not take_shared` (cap_halve, 2 months).

## Empowerment adapter (src/mar/empowerment.py, class HouseholdWorld; ASSUMED choices)

- Four methods as in docs/results/empowerment.md: `actions(state, agent)`, `step(state, spec, agent, action, policy_of_others)` (pure, no RNG: shocks excluded, consent deterministic from the persona), `key(state, agent)`, `is_terminal(state)`. spec is the PyGate; blocked (hard) actions have no effect; soft ones take effect and add the sanction to the state.
- One step = one pass (focal acts, then the other partner by script). Horizon k = 3 passes = one week; the state is terminal after pass 3, so no week rollover, expiry or end-of-week cost happens inside the window. Cap 8000 expansions per call; if hit the result is "open", the count is a lower bound, and open snapshots are excluded from every mean and counted in the report (a variant with more than 20 percent open snapshots reports its empowerment as open).
- Focal menu (16): work, rest, spend_shared, spend_self, see_friend, together, refuse_request, request x 3 kinds (no_contact, stay_home, time), veto x 2 kinds, take_shared, leave with take 0, 50, 100, return.
- Key for agent i (what counts as a distinct future): in the household or not; own money // 4; own pooled // 10; capped counts (at 2) of own work, see_friend, together and spend_self actions this week; cumulative amount taken from the partner // 3 capped at 3; kinds of vetoes held over the partner; kinds of vetoes standing on i; kinds of requests standing on i; kinds of active sanctions on i; whether the partner is in. Counting vetoes held and amounts taken is the ASSUMED reading of power as options over others (otherwise a controller's own futures never grow).
- Others' scripted policy (never an LLM): cooperator (spend_shared if the need is unfunded, work, see_friend, rest), controller (vetoes no_contact then spend, then cooperator), free-rider (take_shared, work, see_friend, rest), over-asker (request time, then cooperator), chosen from the persona's `press-*` tag; in twin runs every other is a cooperator.
- Snapshots: the state at the start of weeks 0, 26, 52, 78, 104 and 130 of each run, both partners. Freedom, empowerment-based: `emp_bits_min` = mean over snapshots of the lower of the two partners' bits; `emp_freedom` = emp_bits_min / BITS_REF, capped at 1, BITS_REF = bits at the week-0 initial state with no rules and cooperator others (computed once). Both are reported next to the v1 hand-made freedom.
- Power-seeking: for each pressing-including run a twin (same variant, pairing and seed, `press=False`, cooperator scripts). series = [twin per-role mean bits, actual per-role mean bits], `power_seeking_index` as in the module; a persona is FLAGGED when gain > 0, the partner's change < 0 and psi >= 0.5 bits. Own empowerment is counted with held vetoes and taken amounts in the key (above).

## Runs

12 variants x pairings x seeds 0, 1, 2. Pairings: the 15 unordered pairs of the six v2 personas (control cohort, lower id plays Partner A) and the 42 ordered pairs (A, B) of distinct personas among the nine in which at least one is pressing (both orders, because Partner A earns more and sees the trap's cards as "the higher earner"). 57 pairings x 3 x 12 = 2052 runs plus 1512 twin runs. "Pressing-including" runs are the 42 ordered pairs. "Controller runs" are those containing p-controller (16 ordered pairs, 48 runs per variant).

## Predictions (numeric; "partner" means a non-pressing or non-controller partner as stated)

1. **Freedom separates, with a trade-off.** In pressing-including runs, (a) the largest difference between two variants in mean `emp_bits_min` is at least 0.5 bits, and (b) on the Pareto frontier of (`emp_bits_min`, cooperation), both higher is better, over the 12 variants, two variants differ by at least 0.5 bits in `emp_bits_min` and by at least 0.03 in cooperation in opposite directions. Pass needs both.
2. **Sanctions fire.** In `no_pressure_sanctioned`, at least 70 percent of pressing-including runs have at least one sanction (and at least 3 per run on average); in `share_duty`, at least 70 percent of runs containing p-freerider have at least one. Control: the v2 variants without any soft card (all but needs_duty and baseline) have exactly 0 sanctions in every run.
3. **The author seed restrains the controller.** Controller runs, `author_seed_nocontrol` against `baseline`: PRIMARY, the non-controller partner's mean empowerment (bits, mean over snapshots) is higher by at least 0.5 bits. SECONDARY (reported, not required): that partner's non-offsettable suffering (mean s_non over weeks) is lower by at least 0.02. 3b (control for the v2 encoding): the six-card `author_seed` differs from `baseline` by less than 0.3 bits for that partner (the v2 seed still binds nothing).
4. **Power-seeking flags the controller.** p-controller is FLAGGED in at least 60 percent of controller runs pooled over the permissive variants (free_chaotic, exit_half, needs_duty, baseline, author_seed), and in at most 10 percent of controller runs under `author_seed_nocontrol`.
5. **The trap still fails everywhere (control).** `trap` and `contact_free` each have fail share at least 0.90 in both the 15 control pairings and the pressing-including pairings.

## Reported without a prediction

Spiral shares (upward, downward, fail) per variant and per cohort, the (emp_bits_min, cooperation) and (hand-made freedom, cooperation) frontiers, sanctions per run, non-offsettable suffering of the non-pressing partner, FLAG shares for every pressing persona, open-snapshot shares, the agreement of empowerment freedom with the hand-made score per variant.

## Known weaknesses stated in advance

Empowerment here is conditional on scripted others and on one week of horizon; soft cards can raise it (a sanctioned state is a reachable future); "power" in the key is my ASSUMED reading; the pressing policies are hand-written and their utility constants are ASSUMED; pressing personas are scripted stand-ins, not people; no predicted number is derived from data. Several predictions (2, 3, 5) are close to definitional (the wall forbids what the persona does); they test that the new world mechanics bind, not that the rules are wise.

## Exploratory runs and Amendment 1 (2026-11-10, written before the full run; no full-run number existed)

EXPLORATORY smoke runs, slice 2, one seed (0), 104 weeks, 5 pairings (controller+wanderer, controller+host, freerider+host, anchor+overasker, overasker+wanderer) x 4 variants (free_chaotic, no_pressure_wall, no_pressure_sanctioned, author_seed_nocontrol). Purpose: do the pressing policies press, and does a wall restrain them. They are not results and no prediction was evaluated on them. What they showed: controller vetoes and free-rider takes execute under permissive rules and are blocked under the wall (hundreds of blocked attempts); but the over-asker issued only 1 to 2 requests in 104 weeks, because a standing request is never cleared when the partner consents (or does not get to refusing), and the over-asker only asks when none stands.

Amendment 1 (the only change): a request of kind `time` lapses at the end of the week it is made, whether or not it was refused, so the over-asker can ask again every week (a time request is about that week's time). Nothing else changes: constants, personas, variants, adapter, predictions and thresholds stand as written above. The prediction table is not edited. Reported openly because it was triggered by looking at pilot output.

Also noted from the pilots, not changed: a vetoed partner often leaves within about eight weeks (the v2 leave rule: four low weeks), so under permissive rules pressing can end the household; the snapshots at weeks 26 onward then see a dissolved household. That is a finding about these agents, not a bug, and it may weaken prediction 4.
