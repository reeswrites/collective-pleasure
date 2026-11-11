# Household world fixes: design (phase 1, no code yet)

Status: design only. No code in src/mar/worlds/, hedonic.py, negotiation.py or personas.py has been changed for this. Another agent (household evolution) is still editing household code; implementation (phase 2) starts after that work lands. Approved plan: the author's "yes fix then retest if that is best course of aciotn" (experiments/changes.jsonl, 2026-11-11T02:06:55Z). Retest preregistration: docs/results/v2-retest-prereg-DRAFT.md. Seed v2.3 (confirmed by the author 2026-11-11, with changes): docs/results/seed-v2.3-readback.md.

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010). Every number below is ASSUMED unless a source is named.

## Why these fixes

docs/results/fidelity.md found that four of six facts do not reproduce in the household: the contact veto is inert (P5), there are no money fines and no crowd-out (P4), outside options change whether a household forms but not its terms (P1a), and nothing adapts with the levers off (P6). The author's Q9 answer adds a fifth problem: money and security count for every persona, whatever they value. docs/results/pleasure-levers.md found seed v2.2 still below the imposed baseline with all levers on: D = -0.019 [-0.051, +0.009].

Adaptation (P6) needs no new fix. The L-A lever already adds it, and every retest arm runs with the levers on.

## What phase 1 found (read-only diagnostics, scratch scripts, no code changed)

Two findings shape the design. Both come from running the current code read-only.

1. **Why the contact veto is inert.** In 45 `trap` runs (15 hand pairings, seeds 0 to 2) the higher earner (Partner A) never asked Partner B for no contact. A made 10 requests, all "stay home". B made 10 "no contact" requests, but card T2 only binds requests from the higher earner, so they bind nothing. No friend visit was ever blocked (0 of 11,951 visits). Requests are rare because a persona asks only when its own connection is below 0.5, its partner is busy, and its autonomy weight is below 0.6. So the veto is inert for two reasons: nobody who could use it does, and a blocked visit would cost little anyway. Making contact pleasurable fixes the second reason only.
2. **Where the v2.2 gap comes from.** The gap is concentrated in pairings that do not form a household under v2.2 and live apart. At week 0 (seeds 0 to 3), bargainer-steward, bargainer-wanderer and steward-wanderer never formed (0 of 4 each); host-wanderer formed 2 of 4. The three largest per-pairing gaps in the levers-on headline are bargainer pairings: -0.151 (peacekeeper), -0.118 (steward), -0.088 (host). The imposed baseline never lets a pair decline to form. Also, the negotiation decides on net wellbeing (pleasure minus suffering, over 26 weeks), while the headline scores mean pleasure only. A pair can rationally choose to live apart to avoid suffering and still score lower on pleasure.

Finding 2 matters for every prediction below. The fixes make life apart and life together more realistic. They do not remove the structural fact that v2.2 lets pairs decline and the baseline does not.

## Ground rules for all fixes

- **One config block.** A new frozen dataclass `FixConfig` in `src/mar/hedonic.py`, next to `LeverConfig`, with every flag default False and every number in one place. A context manager `use_fixes(cfg)` works like `use_levers`, so worlds built inside negotiation are covered. `WeeklyWorld` gets one trailing optional argument, `fixes=None`.
- **Additive only.** No existing signature changes except trailing optional arguments. No existing constant changes value.
- **Nothing read when off.** When a flag is off its code path is not entered. No random draw is made. No new key appears in any output, trace row or gate state.
- **New gate variables stay hidden when off.** The decency card needs a new condition variable, `refused_recently`. It joins `OPTIONAL_VARS` with default 0 and is added to the gate state only when the `decency` flag is on, so trace rows (which are fingerprinted) do not change.

## Regression guarantee (applies to every fix)

With all fix flags off, the existing sha256 fingerprints in tests/test_levers_regression.py (tests/data/levers_off_fingerprints.json, 10 runs) must reproduce exactly. Phase 2 adds, without touching the pinned file:

- `test_all_fix_flags_off_is_the_same_as_none`: `with use_fixes(FixConfig()):` the same 10 fingerprints.
- `test_fixes_off_reproduces_levers_headline`: with fixes off and levers on (`ALL`), 6 fixed cells of the pleasure-levers headline (arms v22_on and base_on, 3 pairings, seed 0) reproduce the per-run pleasure saved in runs/pleasure-levers/headline.json.gz to 1e-12. If that file is missing on the machine, the test is skipped and says so. This covers the levers-on path, which the pinned fingerprints do not.
- If the household-evolution agent's changes alter the pinned fingerprints, that is their regression to resolve first. Phase 2 does not repin.

## Fix 1. Contact matters (flags `contact` and `contact_motive`)

**Goal.** Seeing friends produces pleasure through amplification and release, so losing contact costs something and the contact veto can bite.

**Mechanism.** Built from the horizon study (docs/results/horizon.md, section 4 and the amplification amendment in section 5), moved from days to weeks.

- *Closeness stock per bond.* Each partner has a closeness c in [0, 1] with Friend C (and with each external bond when L-C `network` is on, where the existing bond quality q is reused as c). Closeness rises with each visit and decays every week apart.
- *Amplification.* A friend visit or a together session is a shared activity. Its pleasure is multiplied by 1 + a_max x c x overlap x sociability. Overlap is the taste overlap of the two personas (1 minus the mean absolute difference of their five axes; Friend C uses the persona's own axes, so overlap with C is a persona parameter, ASSUMED 0.6). Sociability is a fixed factor for a social session. Shared bad weeks are amplified too (horizon A5).
- *Release.* While apart from a bond, tension builds: tension += c x want x (1 - tension / t_cap) each week, where want falls as absence becomes normal (half-life h_abs). At a visit, release = k_rel x tension is added to pleasure and tension resets. Tension above t_pain adds offsettable suffering (missing someone hurts).
- *A blocked visit.* When a veto or a bound request blocks a visit the partner wanted, the visit's amplified pleasure is lost, tension keeps building, and the existing `restricted` condition is set (diminished, non-offsettable after 4 weeks). Phase 2 must check whether `restricted` is already wired to contact blocks in the weekly world, and wire it only under this flag if not.
- *Sub-flag `contact_motive` (behavioral, separate so its effect can be told apart).* A persona asks its partner for no contact when the partner saw a friend this week, its own together aspiration was unmet, and its togetherness weight is at least its other-connections weight. This gives the veto a user among non-pressing personas. It is a behavioral assumption about jealousy, not something the author said.

**Parameters (all ASSUMED; horizon values scaled to weeks).**

| name | value | meaning |
|---|---|---|
| a_max | 0.5 | largest amplification of a shared session |
| sociability | 0.8 | social sessions (a solo activity would be 0) |
| c_visit | 0.15 | closeness gained per visit |
| c_decay | 0.03 | closeness lost per week apart (half-life about 23 weeks) |
| c_start | 0.5 | closeness at week 0 |
| overlap_C | 0.6 | taste overlap with Friend C |
| want_half | 6 | weeks for want-to-see to halve while apart |
| t_cap | 1.0 | tension ceiling |
| k_rel | 0.05 | pleasure per unit of tension released |
| t_pain | 0.6 | tension above which missing costs suffering |
| pain_rate | 0.05 | offsettable suffering per unit of tension above t_pain |
| motive_p | 0.3 | weekly chance a qualifying persona asks for no contact (contact_motive) |

**Manipulation check (before any retest number is read).** The fidelity P5 check rerun with `contact` on: `trap` versus `contact_free`, with the pressing-controller cohort (the pressing controller already vetoes) and with `contact_motive` on for the hand cohort. Pass means the runs differ and the restricted partner's mean pleasure is lower under `trap`. With `contact` on and `contact_motive` off, the hand cohort is expected to stay identical. That is the honest expectation, not a failure of the fix.

## Fix 2. Money and security count only as each persona values them (flag `valued_money`)

**Goal.** The author's Q9 answer: "security and money only count to the extent that the person values those things inherently or as a means to theri pleasure".

**What the model does now.** Money and security enter pleasure three ways. (a) As needs, with salience from `persona.needs`, normalized across the four needs. Money's need salience is 0.37 to 0.70 for every hand persona, so money is about a fifth to a quarter of need pleasure for everyone. The Host's money weight is 0.14 but its money need salience is 0.37. (b) As aspirations (savings per week, security buffer), weighted by `persona.weights`. This channel already follows Q9. (c) Through the "denied" condition when the money level falls below 0.15.

**Mechanism under the flag.**

- *Subsistence counts for everyone.* Money below the living cost (2 per week) is a means problem for every pleasure. The shortfall still adds suffering, and "denied" still applies. This keeps poverty harmful for a persona who does not care about money.
- *Above subsistence, intrinsic value follows the persona's weight.* The money need's pleasure term becomes w_m x (1 - exp(-surplus / m_half)), where w_m = persona.weights.money and surplus is money above 4 weeks of living cost. Security's need pleasure becomes w_s x level, with w_s = persona.weights.security. Diminishing returns come from the exponential.
- *Instrumental value comes only through what money buys.* `spend_self` pays pleasure k_buy x (1 - exp(-spend / s_half)) in the week of spending. With `contact` on, shared sessions can cost money too. A persona that values money only as a means then gets its money pleasure only by spending it.
- *The persona agent's utilities* use the same terms, so agents stop working for money they do not value.

**Parameters (all ASSUMED).**

| name | value | meaning |
|---|---|---|
| subsist_weeks | 4 | weeks of living cost treated as subsistence |
| m_half | 6.0 | surplus money at which intrinsic value reaches 63 percent of its ceiling |
| k_buy | 0.06 | ceiling of weekly pleasure from spending |
| s_half | 2.0 | spend at which bought pleasure reaches 63 percent of its ceiling |
| w_ref | 1.0 | divisor on persona weights (weights are already in [0, 1]) |

**Earlier results this could flip.** Any result whose effect runs through money. These are candidates for a rerun, not known flips.

- The v2.2 vs baseline gap itself (pleasure-demo, pleasure-levers H1): living apart costs an extra 1.5 per week; personas with low money weight lose less from it.
- Pleasure-levers LC2 (the 3-to-4 bond ceiling): coordination units come out of work and money, so the ceiling may move for low-money personas. The report already noted that many bonds cost "mostly through money and rest".
- Household v3a and liberty results on the freerider: the harm of `take_shared` is monetary.
- Trap and forfeit results (household v1, v2, liberty): the trap's forfeit harm is monetary.
- The exit floor (26 money) and every negotiation result where exit terms decided acceptance (negotiation v2, v2.1, fidelity P1a and P3).
- Test 2 of ADR 0018 (stay_test.py): the bar lens values exit holdings, so the stay-worth-it share can change.
- Household seed v2 binding results, where breach forfeits are money.

## Fix 3. Negotiation tied to real outside options (flags `real_outside` and `nash_terms`)

**Goal.** The disagreement point should be what each person would actually get living apart, including their other bonds. Better outside options should get better terms, not only decide whether a household forms (fidelity P1a).

**What the model does now.** `negotiation.outside_value` already runs a 26-week rollout of living alone and of living with Friend C and takes the better one. The bar is max(outside option, status quo value). Proposals maximize the proposer's own value, minus a concession penalty when the other falls short of their bar. So the other's outside option only matters when it binds, which is why terms barely move.

**Mechanism under `real_outside`.**

- The rollout runs with every active lever and fix, so living apart includes the partner's external bonds (L-C), friend contact pleasure and release (fix 1), and persona-valued money (fix 2). Phase 2 checks that `use_levers` and `use_fixes` both reach the rollout world.
- The rollout horizon matches the review cycle (26 weeks, unchanged) and its value is cached as now.
- The outside option is recomputed at each 13-week review from the partner's current holdings and hedonic state (already done) and, new, current closeness to friends.

**Mechanism under `nash_terms`.** Among the bundles above both bars, each proposer picks the bundle that maximizes the Nash product (U_me - d_me) x (U_other - d_other), where d is the disagreement point. A better outside option raises d, which shifts the chosen terms toward that person. Negotiation styles keep their current concession speeds. Bargaining power is symmetric (exponent 0.5 each, ASSUMED).

**Parameters.** None new beyond the exponent (0.5, ASSUMED). The rollout length (26 weeks) and caching stay.

**Manipulation check.** Fidelity P1a rerun with both flags on: U_A with outside option +0.15 minus baseline, among formed pairs, at least +0.02. Report the change in the share of pairs that form (no_pot) too.

**Risk stated now.** More accurate outside options may make more pairs decline to form. That would widen the pleasure gap even if every person is better off by their own net wellbeing.

## Fix 4. Money fines as an opt-in negotiable term (flags `fines` and `fine_crowdout`)

**Goal.** A money fine exists only when partners choose it. It is never a default. The author dislikes guilt and scorekeeping (Q2: "reliance is fine its the guilt and scorekeeping i dont like").

**What the model does now.** Seed v2.2 already has one opt-in fine: the menu option `fine: some` (card `N8-fine-some`), 3 money to the wronged partner on a request-commitment breach. It is offered only with a request commitment. Fidelity P4 could not test a money fine because no household rule set outside the negotiated v2.2 cards has one.

**Mechanism under `fines`.**

- The `fine` term widens: scope {request breach, stay breach, role lapse} x amount {3, 6}. `none` stays the fair default. The role-lapse scope is offered only when `roles` is on and a role is agreed. The author confirmed (2026-11-11, "allowed only by mutual choice i think") that a fine on a lapsed role exists only by explicit mutual choice, and v2.3 rule 17 now says so. "Mutual" means both partners accept the fine term in the negotiation; neither can impose it, and it is never part of the fair default.
- Who proposes: personas with security weight at least 0.6 and autonomy below 0.5 (ASSUMED). Acceptance follows each persona's value of the bundle, as for every term.
- Scorekeeping cost: while a fine term stands, each partner pays a small offsettable friction each week, scaled by (1 - security weight). A fine is never free, and it costs most to a persona who does not want enforcement.

**Mechanism under `fine_crowdout` (sub-flag, for fidelity P4 only).** With a fine standing, a breach that is paid costs less trust (the drop is multiplied by 1 - crowd), and the breach load at which a bound partner breaks falls (a price replaces a norm). This makes crowd-out testable. It is off in the retest.

**Parameters (all ASSUMED).**

| name | value | meaning |
|---|---|---|
| fine_amounts | (3, 6) | money per breach |
| keep_friction | 0.005 | weekly scorekeeping friction at security weight 0 |
| crowd | 0.5 | share of the trust drop a paid fine removes (crowd-out only) |
| breach_n_paid | 0.12 | breach load with a fine standing (0.2 without; crowd-out only) |

**Manipulation check.** In fixes-on v2.2 runs, a fine term appears only in households where someone proposed it. Count households with each fine scope. Fidelity P4 rerun with `fine_crowdout` on, reported descriptively.

## Seed v2.3 support (flags `roles`, `lapse_ladder`, `unhappy_ladder`, `trust_words`, `decency`; evaluator `slid_flag`)

These implement the rules in docs/results/seed-v2.3-readback.md. The author confirmed v2.3 on 2026-11-11 with four changes; the flags below include them.

- **`roles`.** New negotiation term `roles`: none | earner_planner (A earns and pays bills, B plans together time) | swapped | shared. Card aim `role` joins `EXTRA_ACTIONS` (as `ritual` did). A role holder's cost for that job falls by spec_gain after a ramp. A role is "due" each week (earn: at least one work block; bills: the gap funded by month end; plan: at least one together session or a kept ritual). A lapse is a due role not done in a week when it was feasible.
- **`lapse_ladder`.** First lapse: a check-in event (small friction to both). Second lapse within 8 weeks after a check-in: an early review of the roles term through `negotiate_v2(review=True)`. Leaving over lapses only after a failed renegotiation or lapses after it. No fine, sanction or forfeit on a lapse unless both chose a role-lapse fine (fix 4). Trust: +role_kept per kept role week, -role_lapse per lapse.
- **`unhappy_ladder` (new, from the author's "check in first for general unhappiness too").** The same ladder for general unhappiness. Today a distressed persona (4 or more low weeks, non-offsettable load N at least 0.2, or trust below `leave_below`) puts `leave` on its menu at once. Under this flag, the first distress signal triggers a check-in instead; if distress continues within 8 weeks, an early review of all terms; `leave` joins the menu only after that review fails to end the distress, or at once if N reaches `skip_n` (severe distress skips the ladder; whether it may is still open with the author). Leaving is never blocked by a card; this changes the agent's policy only. Rule 11 (free exit) is unchanged.
- **`trust_words` (new, from the author's "mostly actions", value not flag).** A setting with three values: `"actions"` (words move trust 0), `"mostly"` (the v2.3 default; a word moves trust +word_gain), `"words"` (words count until tested; a word moves trust +word_gain_tested). A "word" is an event: agreeing to terms at a review, answering a check-in, or a stated promise to resume a role. A word's gain is removed if a lapse or breach by the same partner follows within word_window weeks. Off (the setting `None`) reproduces v2.2 trust exactly.
- **`decency`.** State variable `refused_recently` (1 for 4 weeks after the other refused this kind of request). Card `R11-decency-floor`: an agent must not `request` when `refused_recently` is 1. The author widened common ground to "anyone you interact with", so the card's actor is any agent (partners, Friend C, external bonds), not only partners. Today only partners can make requests, so in practice it binds partners; phase 2 checks whether any other agent can request or refuse and, if so, gives it the same condition. The other two parts of the floor need no code (see the read-back).
- **`slid_flag` (evaluator only).** Reads finished runs. For each partner and each 26-week window: one-way if their mean wellbeing is below their outside option while the other's is above it. Slid-into if one-way and no choice event by them in the window (proposed or accepted a term, made a commitment, gave a gift, took a role, or kept terms after a check-in). Reports the share of partner-windows flagged. It never changes a run, so it carries no regression risk.

| name | value | meaning |
|---|---|---|
| spec_gain | 0.25 | cost saving of a role holder after the ramp |
| spec_ramp | 8 | weeks to reach the full saving |
| checkin_cost | 0.01 | offsettable friction to each partner per check-in |
| ladder_window | 8 | weeks within which a second lapse triggers renegotiation |
| role_kept | 0.002 | trust gain per kept role week |
| role_lapse | 0.05 | trust loss per lapse |
| decency_weeks | 4 | weeks a refused request may not be repeated |
| slid_window | 26 | weeks for the one-way test |
| word_gain | 0.01 | trust gain per word, `trust_words="mostly"` |
| word_gain_tested | 0.05 | trust gain per word, `trust_words="words"` (as much as a lapse costs) |
| word_window | 8 | weeks within which a lapse or breach removes a word's gain |
| unhappy_window | 8 | weeks of continued distress after a check-in before an early review |
| skip_n | 0.4 | non-offsettable load at which a partner skips the ladder and may leave at once |

## Retest support (flag `baseline_may_decline`; scoring change)

From the author's two retest decisions (experiments/changes.jsonl, 2026-11-11T02:22:46Z and 02:23:24Z).

- **`baseline_may_decline` (harness flag, in the retest script, not in the world).** "yes pairs should be allowed to not form a househodl". Today the imposed baseline always starts the pair living together. Under this flag, at week 0 each partner compares the value of living under the baseline cards (a 26-week rollout, the same `pot_baseline` style rollout the negotiation uses, with the baseline cards) with their outside option (`negotiation.outside_value`, with every active lever and fix). If either partner's outside option is higher, the pair does not form and both live apart, exactly as a v2.2 pair with no pot does (same `apart` protocol, same apart modes). The baseline's terms are still imposed, not negotiated: the only new choice is whether to form. Same formation rule for both arms, so v2.2 and the baseline compare like with like.
- **Scoring.** "pleasure minus suffering yeah i guess if that is what is commonly held". Each person is scored at their actual outcome, living apart included: mean over 156 weeks of pleasure minus offsettable minus non-offsettable suffering (the `negotiation.wellbeing` quantity, already the one the negotiation uses). Non-offsettable suffering is reported on its own line as well. This is a change in the analysis only and needs no world flag.
- **Effect on the predictions in the table below.** Both decisions remove most of the structural mismatch named in the last section. With the baseline also allowed to decline, the bargainer and steward-wanderer pairings that drove the gap can live apart in both arms. My guess (made before any run): the levers-on, fixes-off gap in net wellbeing moves from about -0.02 to between -0.01 and +0.01, before any fix. The fixes' own effects are as in the table.

Regression: `baseline_may_decline` off reproduces the pleasure-levers baseline arm exactly; the scoring change does not touch runs.

## Predicted effect of each fix on the v2.2 vs baseline gap (levers on)

Guesses made before any run, for the record. The gap is D = v2.2 minus baseline, mean pleasure, now -0.019.

| Fix | Predicted change in D | Why |
|---|---|---|
| 1 contact | +0.005 to +0.015 | Partners who live apart under v2.2 see Friend C more, so they gain most from amplification and release. Both arms gain something. |
| 2 valued money | 0 to +0.010 | Living apart costs money; low-money personas lose less from it. The bargainer (money weight 0.62) keeps most of its loss, and it drives the gap. |
| 3 real outside options | -0.010 to +0.005 | Nash terms help formed pairs a little. Richer outside options may push more pairs apart, which lowers measured pleasure while raising their own net wellbeing. |
| 4 opt-in fines | about 0 (within 0.003) | Few households will choose a fine, and those that do pay scorekeeping friction. This is a fidelity fix, not a pleasure fix. |
| v2.3 rules (separate arm) | +0.005 to +0.020 over v2.2 | Specialization saves effort by construction where roles are taken; the ladder replaces some trust collapse with renegotiation. The decency floor should change nothing for non-pressing personas. |
| all four fixes together | about +0.005 to +0.020 | D ends near zero. Not confident it turns positive. |

## Fixes I expect not to help the gap

- **Fix 4 (fines).** It makes the model more faithful (fidelity P4) but should not raise pleasure. By the author's own view, a fine adds scorekeeping.
- **Fix 3 (outside options).** It may widen the pleasure gap, for the reason in finding 2. It should still be built, because without it terms-level claims cannot be cited (fidelity P1a).
- **The decency floor.** No effect expected with the hand or grid cohorts; it matters only where someone presses.
- **None of the four fixes addresses the structural cause.** v2.2 lets a pair decline to form; the imposed baseline did not. A pair that chooses apart because it is better off by net wellbeing could still score lower on mean pleasure. The author has now settled both questions this raised (2026-11-11): the baseline may also decline to form (`baseline_may_decline`), and the condition is judged on pleasure minus suffering. See "Retest support" above.

## Phase 2 plan (after the household-evolution agent finishes)

1. Rebase on their work; run tests/test_levers_regression.py first and confirm it still passes untouched.
2. `FixConfig` and `use_fixes` in hedonic.py; regression tests above. Commit.
3. Fix 1 (contact, then contact_motive) with unit tests and the P5 manipulation check. Commit.
4. Fix 2 with unit tests (a money-weight-0 persona gains no pleasure from surplus money; subsistence still hurts). Commit.
5. Fix 3 with the P1a manipulation check. Commit.
6. Fix 4 with the P4 check. Commit.
7. v2.3 support (roles, both ladders, trust_words, decency, slid flag) behind flags; the v2.3 rule directory `rules/household/author_seed_v23_bindable` from the confirmed read-back. Then `baseline_may_decline` and the net-wellbeing scoring in the retest script.
8. Pilot, power check, then Amendment 1 to the retest prereg, committed before any confirmatory run.

Each step: lint the rule sets touched (docs/results/lint.md conventions) and keep the regression tests green.
