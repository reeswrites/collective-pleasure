# How the hybrid decides to leave: a fading tally, lock-in, and an accurate outside forecast (preregistration)

Wording rule: agents feel nothing; "pleasure", "suffering", "value", "forecast", "tally", "rethink" and "held" are glosses for modeled numbers (ADR 0010).

Status: written and committed before any code for these changes and before any run. Nothing here is a result. Scripted agents (the hybrid), no model calls. Recorded as Amendment 5 of the hybrid prereg ([hybrid-agent-prereg.md](hybrid-agent-prereg.md)).

**What the author confirmed (binding wording).** Read-backs rb-2026-11-14-leaving and rb-2026-11-14-gaps (experiments/readbacks.jsonl), all answered "yes sounds good" or confirmed:

- lv-trigger: "A rethink fires when a fading running tally of how the relationship is going drops below a line (a level). A sharp drop (a slope) is tested as an arm. The decay rate and the line are assumed numbers set before runs and swept."
- lv-same: "The same tally drives the lived world and the agent's forecasts, so forecasts can differ from life only in what they predict, not when they look."
- lv-bias: "Agents stay accurate forecasters; the human tendency to overpredict the pain of leaving is a sensitivity arm only."
- lv-lockin: "The cost of leaving grows with time together (shared lease, stuff, pets), so the exit an agent prices when moving in is cheaper than the one it faces later. Used instead of a separate investments term."
- lv-paths: "Before changing the leave rule, measure whether lived exits come from suffering rising or from pleasure quietly fading; if the quiet path never shows up, that is a gap to fix."
- gap-after: "Hard life after leaving stays in the model as true to life. ... what changes is that agents forecast it accurately (as already decided), with a biased-forecast arm as a test."
- gap-leave-meaning-test: the KX2 question is now "does knowing you could leave later make people more willing to try living together?". The author's own prediction (hedged): it won't, "bc of sunk cost and lock in". It is tested here as a prediction, not assumed.

Background: [leaving-research.md](../notes/leaving-research.md) sections 6, 7 and 9; the last version's results [hybrid-exit-option.md](hybrid-exit-option.md) (KX2 failed in a fixture whose cost fell on staying; the in-future rule never leaves within 13 weeks; story 4's outside forecast said 0.80 where the lived life after leaving was about −0.09).

**Model versions (ADR 0020).**
- Old: `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world` (Amendment 3; H41's rows; the version the many-agent spec freezes as `hybrid-N/1`).
- A4: the same plus `hybrid_lone · hybrid_exit` (rows in runs/h41-exit-option/).
- New (A5): A4 plus `hybrid_tally=level · tally_half=13 · tally_line=0.02 · exit_grow=0.04 · hybrid_outside=lived`. All new flags off by default.

What I knew when writing this: everything in the two results docs above and their rows, the exact side model, the leaving research note. I computed per-pairing spreads of A4 − old from the saved rows for the power check (below). No code for any change exists; nothing under any of them has run; the step-5 measurement has not run.

**Can be about / cannot be about (required).** This can be about whether the hybrid, given a fading tally that sets when it rethinks (in life and in its forecasts), an exit cost that grows with time together, and an outside forecast played in its own lived world, passes its known-answer checks, and how H41's arms move in the formation check's two-person household under it, beside the two earlier versions. It cannot be about people, real breakups, real leases or pets, how people actually time their exits, sunk-cost reasoning (the agent has none; see the construct card), or the many-agent world. Limits that apply ([limits.md](../limits.md)): 1, 2, 4, 5 (every new number is ASSUMED), 6, 12 and 13. Not touched: the LLM limits, 2, 3, 7 to 9.

## Purpose

Five confirmed leans become five slices, in this order (slice (a) is this file):

- (b) **Measure first** how lived exits come about today (suffering rising, or pleasure fading at flat suffering), with no rule change. Also measure how far the outside forecast at the deciding reading is from the life the leaver then lives.
- (c) **KX2 with a pure exit cost**: a fixture in which leaving costs something only when one leaves (as `h41_exact.Aids.exit_cost`), and KX2 rerun there.
- (d) **The fading tally** sets when a member rethinks, in the lived world and inside forecasts alike.
- (e) **Lock-in**: the cost of leaving grows with weeks together.
- (f) **An accurate outside forecast** for a member in a household, and a biased-forecast arm.
- (g) **Rerun** the known-answer checks and H41's arms, side by side with the old and A4 versions under the stop rule.

What would change a decision: if every check below passes, the many-agent spec names A5 as the `hybrid-N/2` candidate and says whether it is ready to freeze. If a check fails, it is reported, nothing is patched to make it pass, and the spec keeps the last version that passed.

## Slice (b): how lived exits come about (no rule change)

**Runs.** H41's harness and confirmatory pairings (120, seed 0), with every week's hedonic row and each member's in-household flag kept: arms B, trial and P2 under A4 (the current candidate), and arm B under the old version. Descriptive, no bar. Rows in runs/hybrid-leaving/paths-*.jsonl.

**Each lived exit** (a member leaving a household it was in) is classed from the leaver's own weekly yardstick y = pleasure − w × (offsettable + non-offsettable suffering), w its persona's weight, compared between two 13-week windows:

- Primary: the 13 weeks before the exit (late) against the first 13 weeks of that household spell (early). Needs a spell of at least 26 weeks; shorter spells are classed **short spell** (a household planned or tried briefly).
- Second operationalization (required "one other way"): the 13 weeks before the exit against the 13 weeks before those.

With Δp = mean pleasure(late) − mean pleasure(early), Δs = the same for suffering (both kinds), the fall in pleasure c_p = −Δp and the rise in weighted suffering c_s = w × Δs:

- **no fall**: c_p + c_s ≤ 0 (the yardstick did not fall; the exit came from the outside option or a reading's forecast, not from the life getting worse).
- **suffering path**: c_s ≥ c_p (suffering rising carries at least half the fall).
- **quiet path**: c_p > c_s and |c_s| ≤ 0.25 × c_p (pleasure fell; suffering moved by less than a quarter of that, "flat"). 0.25 is ASSUMED.
- **mixed**: the rest (pleasure carries most of the fall, but suffering rose too).

**Reported**: counts per class, per arm and version, under both operationalizations; the suffering kinds that rose on the suffering path (offsettable, non-offsettable); and the leaver's partner's class over the same windows (option E of the research note, descriptive).

**Verdict (descriptive).** If the quiet path has zero exits under both operationalizations in every arm and version, that is reported as **a gap** (lv-paths: "that is a gap to fix"), and the fix is not made in this prereg (no design for it is written before seeing why). If it appears, the counts are reported and nothing changes.

**Outside-forecast error (the measure slice (f) targets).** For every lived exit on the bar (a reading put leave on the menu), O = the outside option the leaver's deciding reading used (the last reading before the exit, from `bar_log`), and L = the leaver's mean weekly yardstick over the weeks after it left (up to 52, at least 13 weeks of room). Error = L − O, mean and 95% bootstrap interval over exits (resampled by pairing). Story 4 says this can be −0.9; how large it is on average is not known.

## Slice (c): KX2 with a pure exit cost

**The fixture.** `FixConfig.exit_fixed` = c (default 0): for 13 weeks after a member leaves a household, its raw weekly pleasure is lower by c (added to the week's extra pleasure, as pressure's exit stigma is). Paid only by a leaver, only after leaving; nothing changes while it stays. This is `h41_exact.Aids.exit_cost` (0.04 a week for one 13-week block, ASSUMED there) in the hybrid's world. c = 0.04.

**Accurate pricing.** A forecast that has a future self leave makes it pay the cost inside the future (it is part of the world the future plays). The in-future reading's outside option is lowered by the cost's mean over the decision window (c × 13 / 52), the same anticipation pressure's exit stigma already gets at lived readings. A lived reading's outside option is lowered the same way.

**KX2 (rerun).** The stay test's baseline fixture (no trap card), the 12 control pairings and seed 900 of K1, hybrid under A4's flags. One week-0 forecast per member: the household's status quo over K = 4 futures, 52 weeks (`hybrid.forecast`); and the member's outside option. D = V(c = 0) − V(c = 0.04), per member, with `hybrid_exit` off and on.

KX2 passes iff (i) mean over members of D(on) − D(off) > 0 with its 95% pairing-bootstrap interval above 0; (ii) the share of members whose household value beats the outside option is not lower with c = 0 than with c = 0.04 (flag on); (iii) in-future exits happen in the flag-on futures of both fixtures (at least one each), else "cannot fail".

Can it fail: D(off) is 0 by construction (nobody leaves in a flag-off forecast, so the cost is never paid), so (i) reduces to D(on) > 0 with its interval. It fails if in-future exits are rare (interval reaches 0), or if the cost deters exits that were bad for the leaver (D(on) < 0: future selves who leave on the look-back into a worse life). The exact model says it should pass (removing an exit cost never lowers the value of forming, and raises it for a chooser who values exit).

KX2 is run under A4 at slice (c) and under A5 at slice (g).

**The author's question, as a prediction (P-AUTH).** "Does knowing you could leave later make people more willing to try living together?" In the H41 harness (B arm, 120 pairings, seed 0) under A5, formed at week 0 and weeks together with `hybrid_exit` on against the same version with `hybrid_exit` off (the exit option removed from forecasts; the lived world keeps its tally readings and exit cost). The author predicts no: the difference in formed at week 0 is not "+" by H41's class rule (margin 0.01, pairing-bootstrap 95% interval clear of 0). Reported as held or missed. Also reported beside it: the same difference under A4 (from its decomposition rows: exit alone on B formed 0.82 against 0.75), so the reader sees whether lock-in changes the answer. Construct note: the model has lock-in (the growing exit cost) but no sunk-cost reasoning: agents forecast forward only, and weeks already spent never enter a value. So a "held" here can come from lock-in alone.

## Slice (d): the fading tally (`FixConfig.hybrid_tally`)

`None` (default): the old rule, bit for bit. `"level"` (main), `"slope"` or `"both"` (arms):

- **The tally.** Each member in a household keeps τ, updated at the end of every week it is in: τ ← a × τ + (1 − a) × (y − O), with y its yardstick that week (pleasure − w × suffering, the row the forecasts score), O its outside option as last valued (at formation, a retry, its last reading, or in a forecast the choice's anchor), and a = 2^(−1/h), h = `tally_half` weeks. τ starts at 0 when a member's household spell starts (formation, return) and is dropped when it leaves. τ is "how the relationship is going against what is outside, with old weeks fading".
- **The trigger.** level: τ < −`tally_line`. slope: τ fell by more than `tally_line` over the last `hybrid_gap` = 4 weeks. both: either. A triggered member flags a rethink.
- **In the lived world** a rethink is a reading, exactly the reading a distress flag already calls (the pair reading if both are in, the lone reading if one is): same forecast, same outside option, same bar (outside beats staying by more than 0.02 at two readings in a row), at most every `hybrid_gap` = 4 weeks. 13-week readings and the distress flag are unchanged.
- **Inside forecasts** (requires `hybrid_exit`): a future holds an in-future reading when a lived world would: at its 13-week marks, and, at least 4 weeks after its last reading, when a member's tally triggers or its distress flag is up. The copy carries the lived tally as it stands; its reference O is the choice's anchor. The in-future reading's arithmetic is A4's look-back (the last 13 future weeks against the anchor), unchanged. So forecasts and life look at the same moments by the same rule, and differ only in what they compute when they look (lv-same).
- **Thinking is reversible** (option C) at no extra cost: τ climbs back when good weeks return, and a reading that finds staying better does not move the bar counter.
- **Numbers, ASSUMED, set now.** `tally_half` = 13 weeks (the reading period: a week a quarter old counts half). `tally_line` = 0.02 (the leave margin: the same distance the bar uses). Swept one at a time around this centre on the B arm (slice g): half-life 4 and 26; line 0 and 0.05; the slope and both arms at the centre. Neither number has a source in our units (research note section 7A). Neither is chosen or changed from any outcome.

## Slice (e): lock-in (`FixConfig.exit_grow`)

`0.0` (default): no exit cost. `g > 0`: a member that leaves after n weeks in its household spell pays, for the next 13 weeks, a weekly pleasure cost of `exit_fixed` + g × n / 52 (with `exit_fixed` = 0 outside the KX2 fixture). g = 0.04: one year together makes the exit cost the exact model's 0.04 a week for one block; at formation an exit at week 26 inside a forecast is priced at 0.02 a week, while a member who has lived together three years faces 0.12. Lived readings, in-future readings and the outside forecast all price the cost at the weeks the leaver would have in at that moment (so the forecast at formation is accurate about the later, dearer exit). It replaces an investments term (lv-lockin); nothing is added to the value of staying. ASSUMED; swept at g = 0.02 and 0.08, and g = 0 (no lock-in) as a decomposition arm.

## Slice (f): an accurate outside forecast (`FixConfig.hybrid_outside`) and the bias arm (`FixConfig.leave_bias`)

`"solo"` (default): the old rule, bit for bit: a member's outside option is a rollout of a fresh solo world (alone, or with Friend C) from its holdings and hedonic state. `"lived"`: for a member **in a household** (pair readings, the lone reading, the trial's end, the anchors of in-future readings, and H38's stay lens, which must read what the agent reads), the outside option is the lived world itself played forward over K = 4 futures (the status quo's own future seeds) with that member leaving now (take 50, as the reading assumes; its money set to the holdings the caller values), and living in the arrangement (alone or with Friend C) the old solo rollouts rank higher. Its yardstick over the decision window is the value. The member's later life, the partner, the exit settlement, the exit cost and pressure's exit stigma all play out in it, so nothing is subtracted afterwards. Members already out (retries, week 0, returns) keep the old rollout.

- Why this is accurate without fitting anything: the forecast plays the same simulator the lived leaver will live in, from the same state. No number is set from an outcome. Stand-ins (declared): which arrangement is ranked by the old rollouts; nobody holds in-future readings inside these outside futures; a lived leaver may return later, the outside futures only if a return was already valued.
- **Hard life after leaving stays.** If the routine starves rest and connection after leaving (story 4), the accurate forecast now sees it; the routine itself is not changed. Whether the starvation is a routine bug (an arithmetic or bookkeeping error in the code) or the model's honest consequence of living alone is diagnosed and reported, not fixed here (gap-after).
- **Bias arm.** `leave_bias` = b subtracts b from every outside option of a member in a household (the agent overpredicts the pain of leaving, as people tend to; Eastwick et al. 2008, abstract level). Not in the held-out audit. Sizes, ASSUMED, set now: b = 0.02 and 0.05 on the B arm (slice g). Never the main version.

## Known-answer checks (pass tests; bars fixed now)

| ID | What | Passes iff | Where |
|---|---|---|---|
| PIN | Old results reproduce | every new flag at its default: all slow pin tests reproduce byte for byte | `uv run pytest -m slow` |
| KT0 | The tally changes nothing it should not (unit) | tally on with a line no tally reaches: the lived world is identical to the tally off; forecasts hold in-future readings only at 13-week marks and distress weeks | tests/test_hybrid_tally.py |
| KT1 | The tally fires (unit) | a fixture with y − O far below the line: the lived member gets a reading within the week τ crosses (gap allowing) and every 4 weeks after while below; inside a forecast an in-future reading fires before week 13 of the future, and a member can leave there | tests/test_hybrid_tally.py |
| KT2 | Reversible, level vs slope (unit, synthetic tallies) | τ recovers above the line after good weeks; a slow drift to the same level fires level and not slope; a sharp drop fires slope | tests/test_hybrid_tally.py |
| KC1 | The exit cost lands where it says (unit) | paid only by the leaver, only for 13 weeks after leaving, at `exit_fixed` + g × n / 52; zero with both off; at formation an in-future exit at week 26 is priced lower than a lived exit at week 104 | tests/test_hybrid_xcost.py |
| KX2 | The exact model's answer, pure exit cost | (i) to (iii) above | `scripts/hybrid_leaving.py --kx2` |
| KO0 | The lived outside option is the world's own (unit) | `hybrid_outside="lived"` for a member in: equals a hand-built forecast of the copy with that member leaving; for a member out: equals the old value exactly | tests/test_hybrid_outside.py |
| KO1 | The outside forecast is accurate | B arm under A5: mean outside-forecast error over lived bar exits (L − O, slice b's measure) within ±0.02, with its 95% interval inside ±0.04 | `scripts/hybrid_leaving.py --analyze` |
| KL2 | Story 4 (rerun) | under A5: no stretch of more than 26 weeks in which a member alone stays though its outside option beat staying by more than the margin at every lone reading | `--story` |
| K1 | The trap's held share (rerun, reported) | ≥ 0.10 in the trap, ≤ 0.02 in the baseline; failed under Amendment 3 and A4 and expected to fail | `scripts/hybrid_fix_check.py --trap --a5` |
| PT-H | Forecasts against held-out futures (rerun) | A1's sample, A5 flags: H1 mean F − R within ±0.010 with its interval inside ±0.015; H2 Spearman ≥ 0.80; H3 choice agreement ≥ 80% | `scripts/hybrid_passtest.py --a5 --audit`, `--analyze` |
| PT-R | The routine at one week (rerun) | the 40-life value check, A5 flags: T1 to T4 no more than 0.02 below v2 on the same sample; T5 in 0.8 to 1.25; T6 holds | `scripts/value_consistency.py --hybrid --world --a5 --run` |
| KW | The suffering weight (rerun) | w = 2 declines the 0.02-more-pleasure, 0.10-more-suffering household, w = 0 forms, with A5's flags | tests/test_hybrid_fix.py |

## The second measures, and the story check (required)

- **Timing (lv-same).** In B, per reading status quo with room: the share of futures in which a member leaves within 13 and within 52 weeks, against the lived world's (A4: forecast 0% and 13.4%, lived 4.5% and 14.8%). Reported for old, A4 and A5. **Not a target**: no number is tuned toward the lived 4.5% (lv-trigger). A gap above 0.10 at 52 weeks is reported as a weakness.
- **Rethinks.** Lived tally readings per run and the share that end in leaving within 13 weeks; the share of members whose tally crossed the line and later came back above it without leaving (Hawkins et al. 2017's shape, compared as a story, not a fit).
- **Paths again.** Slice (b)'s classes on A5's B arm, beside A4's.
- **Story check.** After the run, read four lives week by week: story 4; one B life where a tally rethink led to an exit; one where a tally crossed and came back; one P2 life (pressure with lock-in). Say whether each looks like what the measures say. A mismatch is a finding.

## Construct card

- **Tally** = an exponentially fading mean of how this week's yardstick compares with the outside option as last valued. Not encoded: rumination, talking it over, the partner noticing, fluctuation (option B, not built).
- **Rethink** = a reading (a forecast and a comparison) the tally calls early. It is not a decision to leave: leaving still needs the bar.
- **Exit cost** = weekly pleasure lost for 13 weeks after leaving, larger the longer one lived in. It stands for the lease, the stuff and the pets in the author's words. It is not money, not stigma (pressure's is separate), not sunk cost: weeks already spent never enter any value, only the cost they make for a later exit.
- **Accurate outside forecast** = the lived world played on with the member gone. It is not a guess about people's forecasts; the bias arm is that.
- **Willing to try living together** (P-AUTH) = formed at week 0 and weeks together, as in H41.
- **Weeks together, held share, liberty, lived pleasure, formed at week 0** = as in H41.

## The H41 rerun under A5

**Design.** H41's design unchanged (step-3 world, F4 with items, F5 in the prenup arm, corrected rule, 156 weeks, 11 arms, 120 confirmatory pairings, seed 0) with A5's flags. 1,320 runs, at most 4 workers, under `caffeinate -i`. Rows in runs/hybrid-leaving/rows.jsonl. Analysis: H41's own code (`h41_choice_aids.analyze_rows`), the A4 script's sign classes (`hybrid_exit_option.vs_b`) and stop rule, applied to three versions.

**Also run (descriptive):** the B arm under A5 with `hybrid_exit` off (P-AUTH, 120 pairings); the sweeps of slice (d), (e), (f) on the B arm, one number at a time around the centre: tally half-life 4, 26; line 0, 0.05; slope; both; exit growth 0, 0.02, 0.08; outside "solo"; bias 0.02, 0.05. Sweeps run on every second confirmatory pairing (60) to keep cost in bounds; if A5's B arm costs more than 60 s a run, they drop to every fourth (30), decided from timing alone before any sweep row is read.

**Unit of resampling.** The pairing.

**Power check.** From A4 − old, paired by pairing (runs/h41-exit-option/rows.jsonl against runs/h41-choice-aids/rows.jsonl, computed 2026-11-14): sd of the per-pairing difference in B is 0.089 (weeks together), 0.25 (formed at week 0), 0.0063 (pleasure), 0.32 (liberty). With 120 pairings (fixed by H41; paired, 80%, α 0.05, `mar.stats.seeds_for_power` approximately (z₀.₉₇₅ + z₀.₈)² × (sd/effect)²): weeks together differences of 0.023 and up are resolved; formed at week 0 of 0.064 and up; pleasure 0.0016 and up; liberty 0.08 and up. P-AUTH's formation clause is therefore DESCRIPTIVE below about 0.065 (A4's exit-option effect, +0.067, sat just at that line). Sweeps on 60 pairings resolve about 1.4 times larger effects and are DESCRIPTIVE throughout.

**Expectations written before the run** (not bars; reported held or missed):

| ID | Expected | Why |
|---|---|---|
| E1 | Pressure still raises weeks together and holds people in (held > 0 at P1 to P4) | Holds under every version so far |
| E2 | Forecasts now leave within 13 weeks in some futures (> 0), and the lived 13-week rate stays above 0 | the tally triggers inside forecasts |
| E3 | Lived exits per run in B rise (A5 > A4) without lock-in, and lock-in pulls them back down (g = 0.04 below g = 0) | rethinks are earlier; exits get dearer with time |
| E4 | KO1 passes, and the outside-forecast error moves toward 0 from A4 to A5 | the forecast plays the lived world |
| E5 | B's formed at week 0 under A5 is no higher than under A4 | lock-in makes the later exit dearer, so the exit option is worth less at formation |
| E6 | P-AUTH holds (the exit option does not raise formation) | the author's prediction; lock-in |
| E7 | The bias arms leave less (fewer exits in B as b rises) and hold more members below their outside option | overpredicting exit pain keeps people in |

## Verdict rule

**For the version (the many-agent world's question).** A5 is **ready to freeze** iff PIN, KT0, KT1, KT2, KC1, KX2, KO0, KO1, KL2, PT-H, PT-R and KW all pass. K1 is reported (expected to fail, as twice before). If any other check fails, it is reported as failed; the design changes only where a check shows the code disagrees with this prereg (a bug), with numbers before and after, and never to move an H41 outcome; and the spec freezes the last version that passed.

**For H41 under A5.** H41's verdict functions, unchanged: pleasure AND freedom together. An aid is a win only if it raises pleasure without raising domination (held share by either lens, liberty down); one up and one down is a **trade-off**, never a win. H41 for an aid is supported iff it raises weeks together, wins against no pressure, and beats matched pressure.

**Three versions (ADR 0020, stop rule).** For every arm and key (weeks together, formed at week 0, held, held wide, liberty, pleasure, lived, non-offsettable suffering, worse-off), the sign class against B is compared across old, A4 and A5. Same class in all three: **holds across versions (three)**. Otherwise **version-dependent**, with the versions that differ named, and **not patched**.

## Can every verdict happen? (run before the confirmatory run; result added as a dated note here)

- Ready / not ready: each check can fail (unit tests fail if a flag is a no-op or always on; KX2 by clause iii and the sign of D(on); KO1 by the error's size).
- Step-5 "gap" and "no gap": synthetic exits (a planted suffering rise, a planted pleasure fade) must be classed suffering and quiet by the classifier (`--reach`), so both outcomes are reachable.
- Three-version labels: synthetic sign flips in one of three row sets read "version-dependent", none read "holds across versions" (`--reach`).
- P-AUTH held and missed: a synthetic formed-at-week-0 difference of +0.10 (missed) and 0 (held) through the same classifier.
- The metric sees the mechanism: tally readings land in `world.tally_log` and the bar log; in-future exits in the forecast's exit log (second measure); the exit cost in the week's `fix` breakdown and so in pleasure and lived pleasure; the outside value in the bar log (KO1).

## Are we measuring what we say? (required)

- **Construct card**: above.
- **Known-answer cases**: KX2 (the exact model, pure exit cost); KO0 and KO1 (the outside forecast against the world it forecasts); KT0 to KT2 (planted tallies); K1 (the trap).
- **One other way to measure it**: step-5 classes on two window pairs (spell start, and the 13 weeks before); timing over 13 and 52 weeks; held share by H38's lens and the wide lens; formation as formed at week 0 and as weeks together.
- **Story spot-check**: four lives (above).

## Findings this could move (ADR 0020)

From the results index:
- **Row 55, hybrid fixes (A4)**: its KX2 fail is retested with a pure exit cost (slice c); its open gaps (late in-future leaving, starved routine after leaving, outside forecast) are addressed or re-measured here.
- **Row 54, H41**: rerun under A5; label set by the three-version stop rule.
- **Row 52, hybrid pass tests** (PT-H, PT-R, KW, K1): rerun with A5's flags.
- **Row 53, the third formation check's hybrid column**: not rerun (ran on the old version; cost); it keeps its label and the many-agent spec's layer a2 must port against the frozen version's own formation check.
- **Row 50, the exact model**: not affected (it is the known answer).
- **docs/limits.md limit 13**: updated after the results. **The many-agent spec's freeze note**: updated to say which version is the `hybrid-N/2` candidate and whether it is ready.

## Not testable by design

- Whether people time leaving by a fading tally (the tally is a declared rule; its numbers are assumed).
- Sunk-cost reasoning (not in the agent).
- H38's held lens in aid arms (0 by construction, as in H41).

## Limits stated now

Scripted agents; one persona sample; one seed per pairing; one parameter point for everything but the swept numbers; the in-future reading is still A4's look-back; the outside futures hold no in-future readings and rank the arrangement by the old rollouts; the tally's reference O is the outside option as last valued, not revalued weekly; K1 expected to fail; cost measured, not assumed.

## Amendments

**Note 2026-11-14, before the A5 confirmatory runs (no threshold moved).** Code at 3b11009; with every new flag off the 50 slow pins reproduce byte for byte and the fast suite passes. Two clarifications of how checks are run, neither informed by an outcome: (1) KT0's lived clause ("the lived world is identical to the tally off") is tested with `hybrid_exit` off, because with it on the tally rule also adds in-future readings on distress weeks (lv-same), which are meant to change forecasts and so may change lived choices; KT0's forecast clause tests that timing directly. (2) A bug found while timing one A5 life before any confirmatory run: the lived outside option's futures (which force the member's exit at week 0 of the future) were being logged as forecast exits in the timing measure; they are now excluded (`hybrid.lived_outside`). This touched only the measure. Free checks before the run: `--reach` reaches every step-5 class, both three-version labels and both P-AUTH outcomes; KL2 under A5 passes (story 4: both leave at the trial's end at week 78, as in A4; no member is ever alone).

**Amendment 2026-11-14, during the A5 confirmatory run (a bug; no threshold moved; the run restarted).** Reading one B life with four exits (p-host with p-peacekeeper) while the run was a fifth done, the lived outside option of p-peacekeeper at week 130 was −0.20 against a life after leaving of +0.77. Cause, traced: the world keeps `ret_value` (the value of returning, set at a return reading) after the member has returned. The counterfactual leaver in `lived_outside` inherited a value set 78 weeks earlier and walked straight back into the household in every outside future (52 of 52 weeks in), so "the outside option" was "leave and return at once". This disagrees with the prereg's own stand-in ("the outside futures [return] only if a return was already valued": a value from an earlier spell is not a valuation of this exit), so it is a bug under the verdict rule. Fix: the counterfactual leaver's stale return value is dropped inside the outside futures only (`hybrid.lived_outside`; test `test_the_lived_outside_does_not_return_on_a_stale_return_value`); the lived world is untouched. Numbers before the fix, on the 256 runs done (kept in runs/hybrid-leaving/rows-stale-return.jsonl, not used for any verdict): KO1 on the 23 B runs done: +0.065 [−0.014, +0.162] over 18 bar exits (FAIL as it stood). The confirmatory A5 run restarted from zero with the fix. The same stale value exists in the lived world and inside A4's forecasts (a member who leaves can return at once on a value from an earlier spell); that is reported as a pre-existing gap, not changed (it would change the old and A4 versions).
