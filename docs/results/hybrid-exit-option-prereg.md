# Hybrid fixes: a reading for the member left alone, and forecasts with the option to leave (preregistration)

Wording rule: agents feel nothing; "pleasure", "suffering", "value", "forecast" and "held" are glosses for modeled numbers.

Status: written and committed before any code for either fix and before any run. Nothing here is a result. Scripted agents (the hybrid), no model calls. The author approved fixing both gaps before the many-agent world is built ("yes yes and AI assisted but from my idea", experiments/questions.jsonl, 2026-11-13T18:30:00Z; the gaps are the ones named in [h41-choice-aids.md](h41-choice-aids.md), "Is the hybrid ready for the many-agent world?"). Fix 1 is also recorded as Amendment 4 of the hybrid prereg ([hybrid-agent-prereg.md](hybrid-agent-prereg.md)). Fix 2 changes what every forecast means, so it gets this preregistration of its own, and the rerun of H41 is preregistered here with both.

Model before: `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world` (ADR 0020), the agent H41 ran on and the many-agent spec froze. Model after: the same plus `hybrid_lone=True · hybrid_exit=True`. Both new flags are off by default.

What I knew when writing this: H41's results and rows (runs/h41-choice-aids/rows.jsonl), the hybrid's Amendment 3 pass tests, the exact side model (`src/mar/h41_exact.py`) and its tables, which I reran today and quote below. I computed spreads of per-pairing differences from H41's rows for the power check. No code for either fix exists; nothing under either fix has run.

**Can be about / cannot be about (required).** This can be about whether the hybrid agent, given a reading when left alone in a household and forecasts that let its future selves leave, still passes its own known-answer checks, and how H41's arms move when it has both, in the formation check's two-person household. It cannot be about people, real exits, real prenups or housing, or about an agent that forecasts its future choices exactly (the in-future leave rule below is a stand-in). Limits that apply (docs/limits.md): 1 (scripted agents), 2 (small persona set), 4 (the outside option is the threat point), 9, 12 and 13. Not touched: the LLM limits.

## Purpose

Two gaps stand between the hybrid and the many-agent world (h41-choice-aids.md):

1. **A member left alone gets no reading.** The distress reading needs both members in; the return reading is for the one outside. In H41's story 4, a member left alone after a trial stayed from week 78 to week 156, suffering up to 1.11 a week with non-offsettable suffering at 0.50, and never considered leaving. In a many-agent world every agent will sometimes be the one left.
2. **Forecasts assume no leaving.** Every future the hybrid plays is a status quo in which nobody leaves. So it cannot value the option of leaving later, and any aid that works by making exit cheaper or safer cannot reach its choices. H41's claim "freedom to leave makes people more willing to commit" was never put to a fair test.

What would change a decision: if both fixes pass their known answers and the old checks, the many-agent world freezes the hybrid with both flags on (a new version under ADR 0020). If a check fails, it is reported and the spec says which version it freezes and why.

## Fix 1: the lone member's reading (`FixConfig.hybrid_lone`)

`False` (default): today's rule, bit for bit. `True`:

- **The same periodic reading.** While exactly one member is in the household, that member holds the reading a member of a pair holds: at every 13-week mark (where the return reading of the one outside runs now), and early on distress (the existing trigger: 4 low weeks, non-offsettable load at least 0.2, or trust below the leave line), at most every `hybrid_gap` = 4 weeks. Its arithmetic is the pair reading's: staying is the status quo over K = 4 sampled futures over the decision window (52 weeks), minus the trust penalty; the outside option is the member's own (alone or with Friend C) at the carry (money plus the 50% take), minus exit anticipation; the bar is the one in force (outside beats staying by more than `leave_margin` = 0.02 at `bar_runs` = 2 readings in a row). Past the bar, leave joins the member's menu at the simulated gain per week times the window, as for a pair. The reading runs in every harness that runs the hybrid's return reading (it is called from `hybrid.return_reading`) and, under `hybrid_readings="world"`, in worlds with no harness.
- **Re-deciding after the household empties.** When the lone member leaves and both are out (and the pair is not living apart together), the pair counts as apart from the next week, so the 13-week retry runs for it as for any pair that never formed: the household under each term against each member's outside option. Today such a pair stays apart for good.
- Nothing else changes: the routine, the yardstick, the bar, the numbers. No new parameter.

## Fix 2: forecasts with the option to leave later (`FixConfig.hybrid_exit`)

`False` (default): today's rule, bit for bit: in a forecast nobody leaves by a reading. `True`:

- **In-future readings.** In every future played for a big choice (the status quo at a reading, the household under each term at formation and retries, the trial's end, the return option, the lone reading, the week-0 commitments), every 13 weeks of the future (weeks w + 13, w + 26, w + 39 of a 52-week window), each member in the household holds an in-future reading. Its stay estimate is its own yardstick over the 13 future weeks just played (mean weekly pleasure − w × suffering, as the choice scores it, without the persona's horizon or discount traits), minus the trust penalty at that week. Its outside option is the one the choice itself compares against, **anchored** at the choice (at a reading: at the carry, minus exit anticipation; at formation: at the starting holdings), with its apart mode (alone or with Friend C). The bar is the lived bar (margin 0.02, two in a row), counted on from the lived counter. A member past the bar gets leave on its menu with the lived leave value, and the routine leaves as in a lived world: the gate, the exit fallback's settlement (F4 with items, or the F5 term), the pot carry and the apart mode all apply. The future then plays on: the leaver's remaining weeks are lived outside the household and count in its score. The one left alone holds in-future readings too only when `hybrid_lone` is on.
- **What this buys.** A household option is now worth its futures with their bad stretches cut short by leaving, at whatever leaving costs. A cheaper or safer exit raises that value; a costly one lowers it. That is the option value of exit, the thing the exact model's optimal chooser and planner see and its rollout chooser does not.
- **The stand-ins, declared (ASSUMED).** (a) The look-back: a future self judges staying by the 13 weeks it just lived, not by a forecast of its own (no nested forecast; a nested one would cost about K × 2 × 2 = 16 outside rollouts per in-future reading). (b) The anchor: the outside option is not re-valued at the future's money. (c) In-future readings run only on the 13-week grid of the future, not early on distress. (d) After an in-future exit nobody returns inside that future unless a return value was already set in the copied world. (e) Formation values that other harnesses compute (`negotiation.pot_baseline`, `baseline_value`; not used by H41 or the many-agent spec) are not covered. No new number: 13, 0.02 and 2 are the lived reading's own.
- **Held-out values** (the PT-H audit) play the same policy (same anchor) on 16 held-out futures, so PT-H measures sampling error of the new forecast, not whether the stand-in matches what lived agents do. The second measure below does that.

**Nothing is fitted.** No parameter is set from any outcome, in this prereg or later. No time cost or exit cost is introduced or tuned.

## Known-answer checks (pass tests; bars fixed now)

| ID | What | Passes iff | Command |
|---|---|---|---|
| PIN | Old results reproduce | With both new flags at their defaults, every pinned fingerprint file in tests/data reproduces byte for byte (h41_off, satiety_off, scale_off, agent_values, levers, makers, observer, h38 pins) | `uv run pytest -m ""` |
| KL1 | Fix 1 runs where it says (unit) | In a fixture with one member out: flag off, the member in never gets a reading (its bar counter never moves); flag on, it gets one at each 13-week mark and on distress at most every 4 weeks, never inside a forecast; with an outside option above staying by more than the margin twice, it leaves; after it leaves, the harness marks the pair apart | tests/test_hybrid_lone.py |
| KL2 | Story 4 (the known case) | H41's trial arm, p-peacekeeper with p-wanderer, seed 0, `hybrid_lone` alone on: the life is identical to H41's until the partner leaves (week 78); after it, the member left alone holds lone readings, and it does not stay alone through a run of more than 26 weeks in which its outside option beats staying by more than the margin at every lone reading (two readings then the bar) | `scripts/hybrid_exit_option.py --story` |
| KX0 | Fix 2 changes nothing when no future self would leave (unit) | Flag on with an anchor no future reaches gives forecasts equal to flag off, exactly | tests/test_hybrid_exit.py |
| KX1 | Fix 2 leaves when it should (unit) | Flag on with an anchor every future beats by far: a member leaves inside the future at the second in-future reading (w + 26), the future still plays all its weeks, and the leaver's last 26 weeks are lived outside | tests/test_hybrid_exit.py |
| KX2 | **The exact model's answer**: exit aids help only a chooser who values the exit option | See below | `scripts/hybrid_exit_option.py --kx2` |
| K1 | The trap's known answer (rerun) | With all four hybrid flags on (w, world readings, lone, exit): held share ≥ 0.10 in the trap and ≤ 0.02 in the baseline, as in Amendment 3 | `scripts/hybrid_fix_check.py --trap --a4` |
| PT-H | Forecasts against held-out futures (rerun) | Amendment 1's sample (G-L0, every sixth pairing, seed 0), all four flags on: H1 mean F − R on the chosen option within ±0.010 with its interval inside ±0.015; H2 Spearman ≥ 0.80; H3 choice agreement ≥ 80% (held-out margin ≥ 0.010). Lone readings enter the audit as their own kind | `scripts/hybrid_passtest.py --a4 --audit`, `--a4 --analyze` |
| PT-R | The routine at one week (rerun) | The 40-life value check with all four flags on: T1 to T4 no more than 0.02 below v2 on the same sample (Amendment 2's reference rows), T5 in 0.8 to 1.25, T6 per-action gaps hold | `scripts/value_consistency.py --hybrid --world --a4 --run` |
| KW | The suffering weight's known answer (rerun) | As in Amendment 3, with both new flags on in the FixConfig: w = 2 declines the 0.02-more-pleasure, 0.10-more-suffering household, w = 0 forms | tests/test_hybrid_fix.py |

**KX2 in full.** The exact model (h41_exact, rerun 2026-11-13 before this prereg) says that removing an exit cost raises week-0 formation only for a chooser that values the exit option: for the rollout chooser on its own pleasure, formed at week 0 moves by +0.000 at household worth 0, −0.05 and −0.10 (and the net rollout chooser never forms); for the planner by +0.022, +0.044, +0.044; for the optimal chooser on pleasure − suffering (w = 1) by +0.111 at every worth; for the optimal chooser on pleasure, 0 to +0.022. It never lowers it for any chooser. In the hybrid world the cost of an exit is what a leaver can carry out. The stay test's two fixtures differ by exactly that: the trap is the baseline plus a card that forbids carrying anything out of the pot. So:

- Setting: the trap and baseline fixtures under the hybrid in the step-3 world with Amendment 3's flags, the 12 control pairings and seed 900 of K1, `hybrid_lone` on in both arms; one week-0 forecast per fixture and member: the household's status quo over the K = 4 futures and the 52-week window (`hybrid.forecast`), and the member's outside option at its holdings.
- Quantity: D = V(baseline) − V(trap), per member (the value of the household when exit is cheap minus when it is costly). The flag-off D carries only the freedom probe's channel (what a member could carry out feeds autonomy every week); the flag-on D adds the exit option.
- **KX2 passes iff** (i) the mean over members of D(exit on) − D(exit off) is above 0 with its 95% pairing-bootstrap interval above 0, and (ii) the share of members whose household value beats their outside option is not lower in the baseline than in the trap with the flag on (formation never falls when exit gets cheaper), and (iii) in-future exits occur in the flag-on futures (at least one per fixture, else the check could not fail and is marked "cannot fail").
- Can it fail? Yes: if in-future exits are rare or carry little, D(on) ≈ D(off) and (i) fails; if the exit option lowers the cheap-exit household's value (a leaver who leaves too early), (i) can go negative.

## The second measure, and the story check (required)

- **Second measure for Fix 2: the stand-in against the lived.** For every reading in the H41 rerun's B arm (both members in), the share of futures in which the forecast had a member leave within the next 13 weeks, against whether a member did leave in the lived world in those 13 weeks; and over 52 weeks. Reported as two rates per arm and their difference. A forecast that leaves far more or far less than the lived agents do is a misforecast the PT-H audit cannot see. DESCRIPTIVE (no bar), but a gap of more than 0.10 in the 52-week rate is reported as a weakness of the stand-in.
- **Second measure for Fix 1:** lone member-weeks (exactly one member in) in two forms: their share of all weeks, and the longest stretch per run in which the member alone has suffering (both kinds) ≥ 0.5. Both reported old against new.
- **Story check.** After the run, read four lives week by week (pattern atlas): story 4 again under both fixes; one B-arm life where an in-future exit option changed a formation or reading (forecast value with the option above the value without by the most); one trial life; one prenup life. Say whether each looks like what the measures say; a mismatch is a finding.

## Construct card

- **Lone reading** = a member alone in the household compares staying alone (paying the whole bill, the pot to itself) with its outside option, on the same schedule and bar as a pair. It does not encode grief, the partner's absence as a loss of its own, or a search for a new partner.
- **Option to leave in a forecast** = a future self that leaves when the last 13 weeks fell short of the outside option anchored at the choice. It does not encode planning, learning, or a forecast of the future self's own forecast. "Values the exit option" means only this.
- **Exit cost** (KX2) = what a leaver may carry out of the pot. Not moving costs, not stigma (no pressure in KX2), not legal cost.
- **Weeks together, held share, liberty, lived pleasure** = as in H41.

## The H41 rerun with both fixes

**Design.** H41's design unchanged: the formation check's household (step-3 world, F4 with items, the corrected rule, 156 weeks), the 11 arms (B, P0.5, P1, P2, P4, trial, cheap, prenup, info, lat, all), H38's 120 confirmatory pairings, seed 0, with `hybrid_lone=True` and `hybrid_exit=True` on top of H41's flags. 1,320 runs, at most 4 workers, under `caffeinate -i`. Rows in runs/h41-exit-option/rows.jsonl. The analysis is H41's own code (`h41_choice_aids.analyze_rows`): measures, matching, bootstrap, margins, verdict functions, all unchanged.

**Also run (descriptive):**
- The old version (both new flags off) on arms B, trial and all, with the new record (lone weeks): its rows must equal H41's rows on every old field (a reproduction check; any difference is reported as a failure of PIN), and it gives the old lone-week numbers.
- Each fix alone, to say which moves what: `hybrid_lone` only on B and trial; `hybrid_exit` only on B and prenup.

**Unit of resampling.** The pairing (as in H41).

**Power check.** From H41's rows (2026-11-13): per-pairing sd of an arm's difference from B in weeks together is 0.143 (trial), 0.019 (prenup), 0.128 (P1), 0.279 (lat); in formed at week 0, 0.30 (trial), 0 (prenup). With 120 pairings (fixed by H41; `mar.stats.seeds_for_power`, paired, 80%, α 0.05): a weeks-together difference of 0.05 at sd 0.143 needs 66 (met); 0.03 needs 186 (not met); a formed-at-week-0 difference of 0.06 at sd 0.30 needs 206 (not met). So weeks-together effects of about 0.04 and up are resolved; formation effects below about 0.08 are not. Old-against-new comparisons are paired by pairing (the same 120 pairings and seed), with the same unit. Formation at week 0 is DESCRIPTIVE.

**Expectations written before the run** (not bars; reported held or missed):

| ID | Expected | Why |
|---|---|---|
| E1 | Pressure still raises weeks together and holds people in (held share > 0 at P1 to P4, interval above 0) | Holds under every version so far |
| E2 | Lone weeks fall in every arm where they were above 0.01 in the old version, and no run has a lone stretch of more than 26 weeks at suffering ≥ 0.5 in which the lone member's outside option beat staying at every lone reading | Fix 1 |
| E3 | Formed at week 0 in B rises (new ≥ old) | Futures with bad stretches are worth more when they can be cut short |
| E4 | No exit-side aid (trial, prenup, cheap) gets a "+" formation gain in weeks together at the +0.01 bar; H41 stays not supported | The exact model: for choosers that value exit, removing an exit cost moves weeks together by −0.013 to +0.037 and the trial by −0.029 to +0.007; more exits offset more forming |
| E5 | The prenup's and the trial's formed-at-week-0 gain against B is ≥ 0 (point estimate) | The exact model: removing an exit cost never lowers formation for any chooser |
| E6 | Cheap solo housing is still identical to B in every run | Nobody lives alone: members apart live with Friend C; lone members who leave go to the better of alone and Friend C, which may now bite (if E6 misses, that is why) |
| E7 | Non-offsettable suffering falls in the trial and all-aids arms (new < old) | Story 4's member was part of their excess |

## Verdict rule

**For the fixes (the many-agent world's question).** The hybrid with both fixes is **ready to freeze** iff PIN, KL1, KL2, KX0, KX1, KX2, PT-H, PT-R and KW all pass. K1 is reported; it failed in Amendment 3 and is expected to fail again (the hybrid can pay to leave the trap); if it fails, held share under this agent keeps the label "known answer only partly met". If any other check fails, it is reported as failed, the design changes only where the check shows the code disagrees with what this prereg says (a bug), with numbers before and after, and never to move an H41 outcome; and the many-agent spec freezes the last version that passed, with the failure named.

**For H41 under the new version.** H41's verdict functions, unchanged: pleasure AND freedom together. An aid is a **win** only if it raises pleasure without raising domination (held share by either lens, liberty down); raising one and lowering the other is a **trade-off**, never a win. H41 for an aid is supported iff it raises weeks together ("+"), wins against no pressure, and beats matched pressure.

**Old against new (ADR 0020, stop rule).** For every arm and for weeks together, held share, liberty, pleasure and lived pleasure, the sign class against B ("+", "0", "−", as H41 classes them) is compared between the old version (H41's rows) and the new. Same class: the finding **holds across versions** (two versions). Different class: **version-dependent**, reported with both versions named, and **not patched**. The H41 index row's label is set from this.

## Can every verdict happen? (to be run before the confirmatory run; the result is added as a dated note here before it starts)

- Ready to freeze / not ready: reachable by construction (each check can fail: see each row; KL1, KX0 and KX1 are unit tests that fail if the flag is a no-op or always on).
- KX2 pass and fail: the free check is KX2 itself (minutes); its clause (iii) says whether it could fail.
- H41's verdicts: reached by H41's `--reach` (synthetic rows), unchanged code.
- Holds across versions / version-dependent: both reachable (synthetic: a sign flip between two row sets), checked in the analysis script's own test.
- The metric can see the mechanism: a lone member's exit lands in `exit_log` and the per-week in-household flags (lone weeks); an in-future exit lands in the forecast's own rows (`STATS["future_exits"]`, counted per run) and so in every value a choice compares.

## Findings this could move (ADR 0020)

From the results index:
- **Row 52, hybrid pass tests** (PT-H, PT-R, KW, K1): rerun here with the new flags.
- **Row 54, H41**: rerun here; label set by the stop rule.
- **Row 53, the third formation check's hybrid column** (formation 0.91, held share 0.05, pleasure L4 − L0 +0.011): cited in docs/limits.md (limit 13) and built on by the many-agent spec (layer a2 ports it). Not rerun here (cost: 120 pairings × 4 seeds × 3 arms). It keeps its label and gets a dated note: it ran on the version before these fixes. The many-agent spec's a2 check must compare against the frozen version's own formation check, so a rerun of row 53's hybrid column under the new version is required before layer a2 and is listed there.
- **Row 50, the exact model**: not affected (it is the known answer).
- **docs/limits.md limit 13** (the two open limits on the hybrid): updated after the results.

## Not testable by design

- Whether the stand-in's leave rule is how a person would decide later (it is a declared rule).
- H38's held lens in aid arms (0 by construction, as in H41).

## Limits stated now

Scripted agents; one persona sample; one seed per pairing; one parameter point; the in-future rule is a look-back stand-in with an anchored outside option, not a nested forecast; PT-H compares the model with itself; K1 failed before and is expected to fail again; cost of the new forecasts is measured, not assumed (reported per arm against H41's seconds per run).

## Amendments

None yet.
