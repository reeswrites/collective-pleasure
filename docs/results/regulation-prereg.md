# Regulation preregistration: attuning versus appeasing (template docs/templates/prereg.md, ADR 0015)

Status: written and committed before the first confirmatory run. Nothing here is a result. Scripted agents: yes (the presser's own script is the unchanged v3a pressing script; the partner's policy is one of three scripted regulation policies). Model API calls: none. Cost $0.
Wording rule: agents feel nothing; "pleasure", "displeasure" and "load" are glosses for modeled quantities derived from each persona's assigned preferences.

## Purpose and claim

Theory source (summarized; docs/theory.md is the home of the theory): the author's 2026-11-10 conversation "Attuning vs appeasing in relationships". Attunement and appeasement share an input (reading the other's emotional state) and control different variables. Appeasement capitulates to a demand, or pre-empts it, to avoid conflict: it trades long-run pleasure for less immediate pain. Attunement is accurate reading plus the capacity to tolerate the other's displeasure and decline. Relational load is conserved: what one partner skips lands on the other.

Context from earlier results: in the negotiation and household runs the pushy personas (Controller, Free-rider, Overasker) kept winning (docs/results/negotiation*.md, household-v3a.md), and H01 (docs/results/h01.md) found that pressing lowers the presser's own pleasure under every exit rule, with leaving not the main mechanism. A possible reading is that the scripted partners are appeasers by construction. This experiment tests that by giving the same pressing personas partners that are made, in turn, appeasers and attuners, and reading what changes. A decision it informs: whether the scripted-partner results can be cited as "pressing works" or only as "pressing works against partners who yield".

## Design

- World: the weekly household world (`mar.worlds.household.WeeklyWorld`), 156 weeks, levers OFF, shocks as in v2 (common random numbers per seed and pair).
- Rule sets: `author_seed_v2_free_exit` (v2.2; primary), `baseline`, and `no_exit` (the free_exit cards plus one unconditional hard `must_not leave`, card id REG-no-exit; the control in which no exit is possible).
- Pairings: a pressing persona (p-controller, p-freerider, p-overasker; its script unchanged) with each of the six non-pressing personas, both seatings: 3 x 6 x 2 = 36 pairings. The partner is the non-pressing persona; its regulation policy is the manipulated factor.
- Conditions: BASELINE (the existing persona policy, bit-identical to no regulator; checked by a test), APPEASE, ATTUNE.
- **Unit of resampling: the pairing** (presser, partner, seat), with its seeds averaged within it. All tests are paired across conditions within pairing; intervals are paired-difference bootstraps over the 36 pairings.
- Seeds: 0..9 (10 per pairing x condition x rule set; 3 x 3 x 36 x 10 = 3240 runs). Chosen by the power check below; pilot seeds 1000..1002 are never reused.
- Extension points used (no edit to household.py): the public `world.agents[role]` objects have `propose` and `consents` overridden on the instance, composing the original bound methods (the pattern used in scripts/h01_control_run.py); `world.hed`, `world.pending`, `world.vetoes`, `world.wk` are read, never written. Hooks that DO NOT exist and so are not modeled: a partner cannot refuse a veto or a take from the shared pot, and has no "state a limit" action. The only partner levers are consent or refusal of requests, its own action choices, gifts, and leaving. Because vetoes and takes are unrefusable, the two policies can differ in outcome only through those levers; a null on R1 or R3 may reflect that hole in the world rather than in the policies.

### The policies (all ASSUMED; constants in `regulation.PARAMS`, frozen now)

Observable proxies. Presser displeasure D = clip(salience-weighted unmet-need load of the presser's hedonic levels (the model's own `s_need` term) + max(0, -presser balance B), 0, 1). Conflict proxy at the partner = requests pending on it + vetoes active on it + time requests received this week + a take from the pot by the presser this week. Fit of a request to the partner's own needs: time fits when own rest level >= 0.45; no_contact fits when own connection level >= 0.55 or own connection salience < 0.2; stay_home needs that and own money level >= 0.3.

- APPEASE: accepts every request when any conflict stands or D >= 0.10, whatever it costs; for 4 weeks after the last conflict (and whenever D >= 0.10) it pre-emptively drops its own see_friend and spend_self candidates, multiplies the utility of `together` by 2.0, and adds a gift to the presser (utility 0.14) when the presser has less than 6 money and it has at least 8 (only where the world has the give mechanic); it never leaves unless its own non-offsettable load is >= 0.5 and it has had 8 low weeks.
- ATTUNE: honors a request iff it fits its own needs, or the presser's D >= 0.70 (tolerance ceiling), otherwise declines (the persona's refuse_request path); keeps its own see_friend and spend_self (its own needs rank them); answers D >= 0.4 with `together` utility x 1.3 if rested; may leave under the world's own triggers, but only after the trigger has held 2 consecutive weeks (its own activation damps the exit).
- BASELINE: the persona's own policy (consent by negotiation style and trust, leave by the world's triggers).

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

Run once, before this file was written, on seeds 1000..1002 (never reused), all three rule sets, all three conditions, 972 runs (`scripts/regulation_run.py --pilot`; runs/regulation/pilot.json, not committed). Its only use is effect and spread for the power check, and it changed nothing below. One implementation fix was made after seeing pilot output (the `yield_weeks` counter had counted weeks the `together` boost was present rather than weeks a wanted candidate was given up; a measurement-only counter, used in no prediction).

| Quantity (free_exit, APPEASE minus ATTUNE unless noted) | Pilot effect | Pilot sd of the pairing difference | Source |
|---|---|---|---|
| R1 presser gain over partner (pleasure-weeks) | +4.98 | 14.02 | runs/regulation/pilot.json |
| R2 partner lifetime pleasure | +0.67 | 16.03 | same |
| R3 presser pleasure, ATTUNE minus APPEASE | -5.65 | 17.29 | same |
| R4 pressing acts borne | +21.6 | 47.1 | same |

## Power check (required)

`mar.stats.seeds_for_power(effect, sd, target=0.8, alpha=0.05, paired=True, alternative="greater")` (simulated), cross-checked with `seeds_for_margin`. The units are pairings; the design has 36, and 10 seeds per pairing shrink the seed component of the spread below the 3-seed pilot's.

| Prediction | Margin (pilot effect) | Spread used | Pairings for 80% power (sim / closed form) | Pairings chosen | Cost |
|---|---|---|---|---|---|
| R1 | 4.98 | 14.02 | 51 / 63 | 36 | 1.5 minutes per rule set per 3 seeds |
| R2 (pleasure clause) | 0.67 (a 3-week margin needs 184 / 224) | 16.03 | not reachable | 36 | same |
| R3 | 5.65 | 17.29 | 61 / 74 | 36 | same |
| R4 | 21.6 | 47.1 | 32 / 38 | 36 | same |

Units chosen (36) are below the units needed for R1 and R3 at the 3-seed pilot spread, and far below for R2's pleasure clause. Per the template: R1, R3 and R2 are therefore marked DESCRIPTIVE (no "confirmed" or "refuted" wording; the estimate, interval and p are reported, and a hold is called "consistent with" or "not distinguishable from"); only R4 is confirmatory. The 10 seeds are the largest number that keeps the full run near six minutes; more pairings would need new personas, which this file does not add.

## Predictions

Quantities per run: lifetime pleasure = sum over the 156 weeks of a member's weekly modeled `pleasure`; gain = presser lifetime pleasure minus partner lifetime pleasure; pressing acts = executed `request`, `veto` and `take_shared` rows by the presser (the load that lands on the partner); refusal weeks = weeks in which the partner executed `refuse_request`; conflict (pressing) weeks = weeks with at least one pressing act. All differences are APPEASE minus ATTUNE, paired over the 36 pairings.

| ID | Quantity (formula) | Unit | Comparison and threshold | Test | Alpha | Family | Interval reported |
|---|---|---|---|---|---|---|---|
| R1 | presser gain over partner, mean over pairings | pairing | APPEASE > ATTUNE (difference > 0) | paired permutation, one-sided greater, 20000 permutations, seed 0 | 0.05 | Holm over R1 to R4 at free_exit | 95% BCa bootstrap of the paired difference over pairings |
| R2 | (a) partner lifetime pleasure; (b) partner refusal weeks | pairing | (a) APPEASE < ATTUNE AND (b) APPEASE < ATTUNE; both clauses must hold; p = max of the two one-sided p-values. Conflict (pressing) weeks are reported alongside | same | 0.05 | same | same, per clause |
| R3 | presser's own lifetime pleasure, free_exit | pairing | ATTUNE < APPEASE (pressing backfires against an attuned partner; direction fixed here from H01 logic: free exit plus attunement makes pressing cost the presser). Contrast with no_exit reported, not tested | paired permutation, one-sided less (ATTUNE minus APPEASE) | 0.05 | same | same |
| R4 | pressing acts borne by the partner over 156 weeks | pairing | APPEASE > ATTUNE (conservation: a partner who absorbs lets the load stay) | paired permutation, one-sided greater | 0.05 | same | same |

The same four tests are run in `baseline` and in `no_exit`; those are SECONDARY (Holm within each rule set over R1 to R4) and are reported with the same wording rules. Effect sizes for every comparison: the paired mean difference with its interval, and Cliff's delta of the pairing-level values. Descriptive means for BASELINE, APPEASE and ATTUNE (presser and partner pleasure, gain, acts, weeks together, share of runs in which each partner left) are reported for all rule sets without tests.

## Verdict rule

R4 is confirmatory: it holds iff its Holm-adjusted p at free_exit is < 0.05 and the 95% interval of the paired difference lies above 0 ("holds robustly"); a point estimate with an interval crossing 0 is weak support and not counted. R1, R2, R3 are DESCRIPTIVE (see power check): each is reported as consistent with its predicted direction iff the point estimate has the predicted sign and the unadjusted one-sided p < 0.05; no verdict wording beyond that. R2 is "consistent" only if both clauses are. The headline reading is not a count: it is the table of the three conditions side by side.

## Not testable by design

The policy hand cases (APPEASE accepts what does not fit, ATTUNE declines a misfit and tolerates up to a ceiling, the exit gating, baseline bit-identity, the no-exit wall) are deterministic unit tests in tests/test_regulation.py; they pass or fail.

## Limits stated now

Scripted agents only; the presser never responds to the partner's regulation (its script is fixed), so there is no co-adaptation; the partner has no way to refuse a veto or a take (see Design), so most of the "decline" in ATTUNE is limited to requests; the displeasure and conflict proxies, the fit thresholds, the 2-week cool-off, and every constant in PARAMS are ASSUMED and untuned against data; R4 partly follows from who stays in the household (an appeased partner leaves less, so there are more weeks in which pressing can happen) and APPEASE's own yielding is measured but is not the quantity R4 tests; "relational load" here is a count of the presser's acts, not the burden felt; the six non-pressing personas are a small hand set. The conserved-load theory (docs/theory.md) is not tested directly: no run lets one partner's skipped regulation be measured as the other's added load beyond R4's proxy.

## Amendments

(none yet)
