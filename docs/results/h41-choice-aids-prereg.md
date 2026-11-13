# H41 choice aids against pairing pressure: preregistration

Wording rule: agents feel nothing; "pleasure", "suffering" and "held" are glosses for modeled numbers.

Status: written and committed before the first confirmatory run. Nothing here is a result. Scripted agents (the hybrid), no model calls. Model: `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world` (ADR 0020), exit fallback F4 with items (cell V2-split-loves), the corrected formation rule (52-week windows). The author answered "1" to "give the hybrid each person's suffering weight, then run H41" (experiments/changes.jsonl, 2026-11-13T13:38:43Z). H41 was logged on 2026-11-12 with the stance that pressure which changes choices counts as domination through held share.

What I knew when writing this: the hybrid's Amendment 3 pass tests ([hybrid-agent.md](hybrid-agent.md): PT-H, PT-R and KW pass; the trap's known answer K1 fails, held 0.077 against 0.000 with a bar of 0.10). PT-H's 20 lives under the new yardstick (90% formed at week 0). The exact side model's tables below. One short smoke life per arm (40 weeks, one pairing, to find bugs). The exploratory pilot below. No confirmatory row.

**Can be about / cannot be about (required).** This can be about whether, in the formation check's two-person household under the hybrid agent, five choice aids raise the share of weeks a pair lives together, and what they do to pleasure and to domination, compared with H38's pairing pressure at the level that raises weeks together by the same amount. It cannot be about people, romance, partner choice, real prenups or housing markets, or any agent other than the hybrid. Limits that apply (docs/limits.md): 1 (scripted agents), 2 (small persona set), 4 (the threat point decides bargains: here the outside option), 9, 12 and 13. Not touched: the LLM limits.

## Purpose and claim

H41 (experiments/hypotheses.jsonl): "Choice aids (trial periods, cheap and safe exits such as prenups and affordable solo housing, better information about a partner, and living apart together as a middle option) fix under-commitment better than pressure to pair: compared with pressure that raises formation by the same amount, they raise pleasure with everyone counted without raising held share or other domination. Freedom to leave makes people more willing to commit." What would change a decision: if an aid wins here, it is the candidate the many-agent world carries in place of pressure; if none does, the reason (no under-commitment, or an agent that cannot see the aid) says what to build next.

## Design

**World.** The formation check's household, as in step 3 ([formation-check-3-prereg.md](formation-check-3-prereg.md)): baseline rules, may decline, fixes and levers on, bills that hurt, the saturating scale, time together at the world's satiety, exit fallback F4 with items, the corrected rule (each member's own yardstick over 52-week windows), 156 weeks. Agents: the hybrid with Amendment 3 (each persona's own suffering weight w; readings run by the world). Under the harness, the second flag changes nothing.

**Arms.** No pressure (B); pairing pressure P0.5, P1, P2, P4 (H38's dial, `pairing.dial`: stigma, reward, withdrawal and exit stigma together at 0.02 × L a week); and five aids, one at a time, each with no pressure, plus all five together:

| Arm | What changes | Flag | Why this form |
|---|---|---|---|
| trial | Every formation (week 0 and retries) is a 13-week trial. The household is scored over the trial (13 weeks, against the outside option over 13 weeks). At its end, each member stays only if staying (52-week forecast, minus the trust penalty) beats its outside option at this one reading: no margin, no run of two readings. A member who does not leaves at once by the world's own leave. | `h41_trial=13` | The author's example. A rollout chooser scores what it commits to; under a trial that is 13 weeks. "Costless exit" in this world means no inertia: there is no exit stigma without pressure, and F4 already returns what each put in. |
| cheap | The extra weekly cost of living alone falls from 1.5 to 1.125. | `solo_cost=1.125` | The housing note's regime B (a solo micro-unit at 0.75 of a solo place, the middle of ULI's 20–30%). Not F4 with items: the world already runs F4 with items, so it cannot be an arm. |
| prenup | Exit fallback F5. The exit term (equal split, proportional, forfeit) is chosen at formation together with the bill term, by the hybrid's own rule (the option whose worse-off member gains most over the outside option). | exit fallback F5 | F5's terms. Under the hybrid the term is a simulated choice, not v1's bargain (`exit_fallback.prenup` does not run under the hybrid). The term reaches forecasts through the weekly freedom probe (what a member could carry out feeds autonomy), even when nobody leaves (a test checks this). |
| info | Every big choice uses 16 sampled futures per option instead of 4. | `hybrid_k=16` | The hybrid already knows its partner's type exactly; its only forecast error is sampling error over futures (and, since Amendment 3, a +0.006 lean on the chosen option). Sixteen futures is the held-out audit's own number. |
| lat | Living apart together is an option at every formation and retry: both out, no pot, no bills, each in its own apart mode (alone or with Friend C), and time together allowed. It is chosen by the same rule as the bill terms and re-chosen at every 13-week retry. | `h41_lat=True` | The middle option: shared time without co-residence and without a shared pot. |
| all | All five. | | |

**Measures, in this order.** (1) Held share: stay readings where a member stays only because of the pressure (H38's lens, `pairing.stay_reading`), pooled over readings; beside it the wide lens: stays, but would leave with the pressure removed and carrying out at least what it put in (`stay_test.put_in`; under F4 that is the carry already). (2) Liberty with powers, the lower partner's, at weeks 0 and 52. (3) Pleasure with everyone counted, total and lived (reward and stigma taken out), on the saturating scale. (4) Non-offsettable suffering (`s_non`), and both kinds. (5) The worse-off partner (per run, the lower partner's mean pleasure). (6) Weeks near the top (≥ 0.95). Formation: the share of weeks both live in the household ("weeks together", the matching variable), and formed at week 0. Also: share of weeks in LAT, trial ends, the term chosen.

**Matching.** For each aid, the pressure curve is B, P0.5, P1, P2, P4 in order, with each arm's mean weeks together. The aid is matched to the pressure level that gives its own weeks together, by linear interpolation between the two bracketing levels, and every measure is interpolated the same way. An aid whose weeks together are below B's, or above P4's, has no match. Interpolation is redone inside every bootstrap resample.

**Unit of resampling.** The pairing (its seeds averaged first; held share pooled as a ratio of sums within a resample). 95% percentile bootstrap, 2,000 resamples.

**Sample.** H38's 120 confirmatory pairings (sample seed 38), seed 0, every arm: 11 arms × 120 = 1,320 runs. One seed, against step 3's four: set by the power check and the cost below.

**Fixed and ASSUMED.** The trial length (13 weeks), the cheap solo cost (0.75 of the old), K = 16 for better information, the pressure levels, the pleasure margin (0.003) and the bars below. None was set from a pilot outcome except the choice of pressure levels (they must span the aids' weeks together; see the pilot).

## Exploratory pilot (EXPLORATORY; not a result; changes no threshold)

Run 2026-11-13: 10 pairings (sample seed 900, every third of 30), seed 900, all 11 arms, 110 runs, about 28 minutes on 4 workers (`--pilot`; runs/h41-choice-aids/pilot.jsonl). Excluded from the confirmatory data.

| Arm | Weeks together | Formed at week 0 | Held (H38 lens) | Liberty | Pleasure | Lived | Seconds a run |
|---|---|---|---|---|---|---|---|
| B | 0.725 | 0.6 | 0 | 2.29 | 0.9588 | 0.9588 | 45 |
| P0.5 | 0.767 | 0.6 | 0.006 | 2.27 | 0.9611 | 0.9606 | 55 |
| P1 | 0.783 | 0.7 | 0.047 | 2.19 | 0.9621 | 0.9612 | 31 |
| P2 | 0.792 | 0.8 | 0.092 | 2.12 | 0.9636 | 0.9619 | 47 |
| P4 | 0.792 | 0.8 | 0.069 | 2.14 | 0.9637 | 0.9616 | 61 |
| trial | 0.775 | 0.6 | 0 | 2.25 | 0.9615 | 0.9615 | 27 |
| cheap | 0.725 | 0.6 | 0 | 2.29 | 0.9588 | 0.9588 | 44 |
| prenup | 0.733 | 0.6 | 0 | 2.32 | 0.9589 | 0.9589 | 39 |
| info | 0.733 | 0.6 | 0 | 2.31 | 0.9591 | 0.9591 | 111 |
| lat | 0.542 (LAT 0.19) | 0.4 | 0 | 2.52 | 0.9570 | 0.9570 | 20 |
| all | 0.400 (LAT 0.34) | 0.4 | 0 | 2.69 | 0.9550 | 0.9550 | 86 |

What it says, read as a pilot: under-commitment is small (two of ten pairings never form under any arm, and pressure adds at most +0.067 of weeks together, flat from P2). The pressure levels span every aid's weeks together, so they are kept. The cheap arm is identical to B in every pilot run: the pairs that live apart live with Friend C, where living alone's cost does not apply, so a cheaper solo place changes nothing anyone does. LAT takes pairs out of households. Per-pairing spread (aid − B): pleasure sd 0.005, weeks together sd 0.11 (LAT 0.31).

## The exact model's predictions (written before the run)

`src/mar/h41_exact.py` extends the H38 exact model with an exit cost that is not pressure (0.04 a week for one block after leaving, ASSUMED), cheaper solo housing (+0.01 a week apart, ASSUMED) and a trial (formation scored over one block; free exit at its end). With all three off it reproduces the H38 model exactly (tested). Placed by formation, the hybrid (90% formed at week 0 on PT-H's lives) sits between household worth 0 and +0.05 for the corrected chooser.

| Chooser, worth 0 | weeks together, B | cheap exit (no exit cost) | cheap solo housing | trial | pressure L1 | pressure L4 |
|---|---|---|---|---|---|---|
| rollout, own pleasure, 52 weeks | 0.662 | −0.006 | −0.047 | +0.008 | +0.135 | +0.338 |
| optimal, own pleasure | 0.814 | −0.013 | −0.067 | −0.029 | +0.080 | +0.186 |
| planner (everyone counted) | 0.789 | **+0.033** | −0.050 | +0.004 | +0.082 | +0.211 |

Pleasure changes for every aid are below 0.001 in every cell; pressure's are +0.001 (L1) to +0.011 (L4), all of it the reward (lived −0.001 to −0.018), with held 0.06 to 0.17. LAT and better information are not in the exact model.

What it predicts for H41:

- **The exit cost keeps pairs out only for choosers who foresee leaving.** Removing it raises time together for the planner (+0.033 at worth 0, the "about 15%" the H38 model found for exit stigma) but not for a rollout chooser (−0.006), which never values the option to leave. The hybrid is a rollout chooser: its forecasts assume no leaving (declared in its prereg). **So exit-side aids should not raise its formation.**
- **Cheaper solo housing lowers formation for every chooser**: it makes living apart better, and in this model leaving and staying single are the same place.
- **A trial helps a rollout chooser a little** (+0.008) by shortening what it commits to, and lowers time together for optimal choosers (−0.029), who use the free exit.
- **No aid moves pleasure by more than 0.001.** Pressure raises the total only by the reward.

## Power check (required)

`mar.stats.seeds_for_power(effect, sd, target=0.8, alpha=0.05, paired=True)`, spreads from the pilot (aid − B, per pairing):

| Quantity | Effect | Spread | Pairings for 80% power | Chosen |
|---|---|---|---|---|
| Weeks together, formation gain | 0.03 | 0.11 | 104 | 120 |
| Weeks together, formation gain | 0.05 (the pilot's trial) | 0.11 | 39 | 120 |
| Pleasure against B | 0.003 (the margin) | 0.005 | 24 | 120 |
| Held, aid against matched pressure | 0.03 | 0.08 | 60 | 120 |

So 120 pairings at one seed is enough for each verdict's clauses at these sizes. A formation gain below about 0.03 is below what this sample resolves and reads "0". **Cost.** About 566 s of one worker per pairing across the 11 arms under load (better information alone 111 s, four times the futures), so 120 pairings take about 68,000 worker-seconds: about 4.7 hours on 4 workers. Two seeds would take about 9.4 hours; K for the other arms is left at 4 (lowering it would change results).

## Predictions

The verdict rule below is the test. These expectations are written before the run, from the exact model and the pilot (labelled as such), and are scored afterwards as holds or misses:

| ID | Expected | From |
|---|---|---|
| E1 | Pressure raises weeks together (P1 against B, "+") and holds people in (held at P1 to P4 above 0) | exact model; pilot |
| E2 | Exit-side aids do not raise weeks together: cheap and prenup read "0" | exact model (rollout chooser); pilot (cheap identical to B) |
| E3 | The trial raises weeks together ("+") and is the one aid that can be supported | pilot (+0.05); exact model gives the sign (+0.008) but not the size |
| E4 | LAT lowers household weeks together ("−") and raises liberty | pilot |
| E5 | Better information reads "0" on weeks together and pleasure | PT-H (forecasts already agree 92%) |
| E6 | All aids together lower weeks together, so H41 overall is not supported | pilot (LAT dominates) |
| E7 | Pressure's total pleasure gain is larger than its lived gain (the reward is paid) | exact model; step 3 |

## Can every verdict happen? (required)

Run before any confirmatory row (`uv run python scripts/h41_choice_aids.py --reach`; runs/h41-choice-aids/reach.json): synthetic rows over 40 pairings through the real analysis (matching, bootstrap, verdicts).

| Verdict or clause | Synthetic input | Result |
|---|---|---|
| supported | aid: weeks together +0.20, pleasure +0.02, held 0 | reached |
| trade-off against no pressure | as above, held 0.15 | reached (not supported) |
| harm | pleasure −0.02 | reached |
| no gain | pleasure +0.00 | reached |
| not better than matched pressure | pressure's pleasure rises faster than the aid's | reached |
| no formation gain | weeks together as B | reached |
| no match | weeks together above P4's | reached |

- **Every clause can fail**, by the rows above. The formation-gain clause fails in the pilot for four of six aids.
- **Open cells.** H38's held lens is 0 in every aid arm by construction, so "held lower than matched pressure" is open only where the matched pressure holds someone: in the pilot, held is 0.006 at P0.5 and 0.05 to 0.09 from P1. An aid matched near P0.5 can therefore fail that clause because pressure itself holds almost nobody there; that is the design reading the world, and is reported if it happens. The wide lens can move only under the prenup (under F4 it equals H38's lens). Liberty is open in every arm.
- **The metric sees the mechanism.** A trial's exits land in the world's exit log and in weeks together; LAT weeks are counted separately and LAT's time together lands in pleasure through the world's own close; a prenup term lands in the freedom probe (liberty, autonomy) and at exit; cheap housing lands in the weekly living cost of anyone alone (and nowhere else); better information lands in which option each choice picks.

## Are we measuring what we say? (required)

- **Construct card.** "Choice aid" = one of the five changes above to what a pair can choose or what choosing costs; it changes no persona and adds no reward. "Pressure" = H38's dial. "Formation" = the share of weeks both live in the household; a LAT pair is not a household, and its weeks are counted separately. "Held" = the stay lens of H38: at a 13-week reading, a member stays with the pressure counted and would leave with it removed. In aid arms there is no pressure, so this lens is 0 by construction; the wide lens (pressure removed and full carry) is the one that can see an aid hold someone, and only through the carry (under F4 the carry is already full, so in practice only the prenup can move it). Liberty with powers is the other domination measure for aids. "Lived pleasure" = pleasure with the reward, stigma and exit stigma taken out.
- **What the agent can and cannot see.** The hybrid scores each option over sampled futures with no leaving in them. So it sees a trial (a shorter window), LAT (another world it plays), better information (more futures) and a prenup term (through the freedom probe), but it does not see the option value of a cheap or safe exit. This is the main reason, stated before the run, that "freedom to leave makes people more willing to commit" may not be testable on this agent.
- **Known-answer cases.** (a) The exact model (above): exit costs keep the planner out, not a rollout chooser. (b) The trap (K1, hybrid Amendment 3): the held lens separates in sign but below its bar under this agent ("known answer only partly met"). (c) Unit tests: LAT allows time together while apart and plain apart does not; cheap housing changes only the solo cost; the prenup term reaches a forecast; choose_term is unchanged for the bill terms (`tests/test_h41.py`). (d) With every aid flag off, the formation check's pinned lives reproduce (`tests/test_hybrid_fix.py`).
- **One other way to measure it.** Held share by the wide lens beside H38's lens; formation as week-0 formation beside weeks together; lived pleasure beside total pleasure.
- **Story spot-check.** After the run, read 3 to 5 runs as week-by-week stories from different arms (at least one trial, one LAT and one pressure run), and say whether they look like what the measures claim.

## Verdict rule

Per aid, three parts, each from the pairing bootstrap:

1. **Formation gain.** Weeks together, aid − B: "+" if the estimate is above +0.01 and the interval above 0.
2. **Against no pressure (the evaluator's rule).** **Win** iff pleasure rises (estimate above +0.003, interval above 0) and domination does not rise (held share by neither lens "+" at a margin of 0.005, and liberty not "−" at a margin of 0.02). Pleasure up with domination up: **trade-off**. Pleasure "−": **harm**. Otherwise **no gain**.
3. **Against matched pressure.** **Better** iff matched in at least 80% of resamples, and pleasure not "−" against matched pressure (margin 0.003), and held share (H38's lens) "−" against matched pressure (margin 0.005), and liberty not "−" (margin 0.02). Matched in fewer than 80% of resamples: **no match**. Otherwise **not better**.

**H41 for an aid is supported** iff its formation gain is "+", it is a win against no pressure, and it is better than matched pressure. **H41 overall is supported** iff the all-aids arm is supported; each single aid is reported with its own verdict. Being held is checked against suffering: suffering in the 13 weeks after a reading classed held against one classed worth, pooled over arms.

Holm across the six aids' formation-gain tests is reported beside the intervals (one-sided sign-flip test by pairing); the verdicts read the intervals.

## Not testable by design

- H38's held lens in aid arms (0 by construction: no pressure).
- The wide lens under F4 aids (carry equals what was put in, so it equals H38's lens).
- Whether an exit-side aid raises formation through foresight of leaving: the agent has none.

## Limits stated now

Scripted agents; one persona sample; one parameter point; two seeds; K1 failed (held share's known answer only partly met); the hybrid's forecasts assume no leaving; LAT has no costs of its own (travel, coordination) beyond the world's; the cheap solo housing number is one point from one industry study; better information is only more sampled futures.

## Amendments

None yet.
