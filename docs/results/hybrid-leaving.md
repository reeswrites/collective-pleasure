# How the hybrid decides to leave: a fading tally, lock-in, and an accurate outside forecast

Wording rule: agents feel nothing; "pleasure", "suffering", "value", "forecast", "tally", "rethink" and "held" are glosses for modeled numbers.

Model: slice (b) ran on A4 (`hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit`) and on the old version (Amendment 3, the same without the last two flags). Later slices name their version where they report. Preregistration: [hybrid-leaving-prereg.md](hybrid-leaving-prereg.md) (commit 8a291b0, before any code or run).

Status: run on 2026-11-14 after the preregistration (8a291b0; code 3b11009, one bug fix at 1affe34 before the confirmatory run restarted). Scripted agents, no model calls, every number ASSUMED. Label for H41 under ADR 0020: three versions now (old, A4, A5), see "Three versions".

**Note 2026-11-15.** Both bugs named under "New gaps" (friend-visit valuation, stale return values) are fixed behind flags in Amendment 6 ([hybrid-a6.md](hybrid-a6.md)). The fixes change few lives. KO1 still fails under A6 (+0.027 [+0.004, +0.048]), now leaning pessimistic about leaving. Neither A5 nor A6 is ready to freeze.

## In one paragraph

**Measured first: in this model people leave because suffering rises, almost never because the good quietly fades** (0 of 242 exits on the primary windows; 2 on the second), so the quiet path is close to a gap. **Then built, behind flags, all off by default (pins byte for byte):** a fading tally that calls a rethink in life and inside forecasts by the same rule; an exit cost that grows with weeks together; and an outside option played in the lived world itself. **KX2, with a pure exit cost, now passes** under A4 and A5 (DiD +0.019 and +0.015, intervals above 0): A4's failure was its fixture. K1 passes for the first time (0.128, thinly). PT-H, PT-R, KW and the unit checks pass. **KO1 fails narrowly**: the outside forecast's mean error is +0.016 but its interval reaches +0.044 (bar ±0.04); the story-4-sized misses (−0.8 to −0.96) are gone (worst −0.31). So **A5 is not ready to freeze** by its own rule. Forecasts now look when life looks, and leave too often (52-week rate 42% against 22% lived in B). **H41 stays not supported** in all three versions; pressure still holds people in under all three, but its gain in weeks together is now version-dependent (0 under A5). The author's prediction holds for moving in (the exit option raises week-0 formation by +0.050 [0.000, +0.100], not clear of 0) but not for time together (+0.047 [+0.017, +0.088]). Lock-in at the swept sizes barely changes anyone's choices. The starved rest and connection of story 4 is a routine valuation error (friend visits valued without the world's habituation), reported, not fixed.

## Slice (b): how lived exits come about (measured before any rule change)

Runs: H41's harness, 120 confirmatory pairings, seed 0. A4 on arms B, trial and P2 (360 runs); old on B (120 runs). Rows in runs/hybrid-leaving/paths-*.jsonl, table in paths.json (`scripts/hybrid_leaving.py --paths`, `--paths-analyze`). The step-5 code was committed at 80ee386 before any Amendment 5 code existed; the old version's 120 runs started after that code was written, with every new flag off (the 50 pinned fingerprint tests reproduce byte for byte on that code, so the runs are the old model).

Each lived exit is classed from the leaver's own weekly yardstick (pleasure − w × suffering), late window (13 weeks before the exit) against early (the first 13 weeks of the spell), and, as the second operationalization, against the 13 weeks before the late window.

| Version: arm | Exits | Suffering path | Quiet path | Mixed | No fall | Short spell | Second windows: quiet |
|---|---|---|---|---|---|---|---|
| A4: B | 60 | 49 | **0** | 3 | 8 | 0 | 0 |
| A4: P2 | 30 | 26 | **0** | 2 | 2 | 0 | 0 |
| A4: trial | 99 (52 at the trial's end) | 35 | **0** | 5 | 6 | 53 | 2 |
| old: B | 53 | 45 | **0** | 2 | 5 | 1 | 0 |

- **The quiet path (pleasure fading at flat suffering) almost never happens.** Zero of 242 exits under the primary windows, in every arm and both versions; 2 of 242 under the second windows, both in the trial arm. By the preregistered rule ("a gap iff zero under both operationalizations in every arm and version") it is **not** formally a gap, because of those two trial exits. Read plainly, it is close to one: in this model people leave because suffering rises (offsettable suffering rose in every one of the 155 suffering-path exits; non-offsettable in 30), not because the good fades. The research note's section 6 says about half of human divorces come from low-distress marriages, and the good fading predicts later divorce better than conflict. The model does not produce that path. Not fixed here (the prereg writes no fix before seeing why); see "New gaps".
- Why, as far as can be seen: weekly pleasure on the saturating scale sits near its top (about 0.96) and moves little, so a fall in the yardstick large enough to cross the leave bar almost always needs suffering. The "no fall" exits (8 to 12 per 60 in B) leave with a flat or rising yardstick: the outside option rose (money saved) or the reading's forecast said so.
- **The left partner** is on the suffering path itself in most exits (A4 B: 40 of 60), so most leavings are not one-sided in this model (option E).

**The outside forecast's error** (the deciding reading's outside option O against the leaver's mean yardstick L over the up to 52 weeks it then lived; bar exits with at least 13 weeks of room):

| Version: arm | Exits | Mean L − O [95% interval, by pairing] | Worst |
|---|---|---|---|
| A4: B | 54 | +0.044 [+0.002, +0.086] | −0.81 |
| A4: P2 | 23 | +0.051 [−0.062, +0.127] | −0.83 |
| A4: trial | 41 | −0.027 [−0.162, +0.087] | −0.92 |
| old: B | 48 | +0.014 [−0.042, +0.066] | −0.96 |

On average the old forecast is not far off (and A4's B leavers lived slightly better than forecast), but the tail is long: in every arm a few leavers live about 0.8 to 0.96 a week below what their forecast promised. Story 4 (A4 notes: 0.80 forecast, about −0.09 lived) is one of those, not an oddity.

**Why the tail happens (diagnosed for story 4, the lone-only life).** After its partner left, the member alone (p-peacekeeper) spent all three action units each week on seeing a friend (works 0, rests 0) and later, after leaving, one on work and two on friends; it never rested. Rest fell to 0 by week 100 and connection to 0 by week 106, although it saw a friend two or three times a week, because the world habituates repeated visits to the same friend (the `adapt` lever: each visit's strength falls with satiety), while the routine values one more visit at full strength. That is the routine's own arithmetic disagreeing with the world's: `agent_values.expected_scales` values time together at the world's satiety since Amendment 2, but "seeing a friend keeps the persona rule" (only an adaptive persona expects satiety). So **the starved rest and connection are a routine valuation error of the same kind Amendment 2 fixed for time together, not hard life after leaving as such**. The solo outside rollout misses it because it starts a fresh world, with fresh friend satiety, so its visits restore connection. Reported, not fixed (gap-after: hard life after leaving stays; fixing the routine is the author's call).

## Slice (c): KX2 with a pure exit cost

Fixture: `FixConfig.exit_fixed` = 0.04 (a leaver's raw weekly pleasure lower by 0.04 for the 13 weeks after it leaves; nothing while it stays), the stay test's baseline fixture, 12 control pairings, seed 900, one week-0 forecast per member (`scripts/hybrid_leaving.py --kx2 --flags a4`, runs/hybrid-leaving/kx2-a4.json, 38 s).

**KX2 under A4: PASS.**

| | Value |
|---|---|
| D(off) = V(no cost) − V(cost), exit option off | 0.000 (exactly, by construction: nobody leaves in a flag-off forecast) |
| D(on), exit option on | +0.019 |
| (i) DiD | **+0.019 [+0.005, +0.036]** (11 of 12 pairings above 0) |
| (ii) share whose household beats the outside option, no cost vs cost (flag on) | 0.083 vs 0.083 (not lower) |
| (iii) futures with an in-future exit (flag on) | 45 of 48 with no cost, 45 of 48 with the cost; first exit at week 29.5 vs 30.6 on average |

So with a cost paid only on leaving, the exit option behaves as the exact model says: a cheaper exit raises the value of forming only for the chooser that values exit. A4's failure in the trap fixture was the fixture (its cost fell on staying), not the exit option. Two things to read with it: the cost barely changes who would form (clause ii is met by equality), and with the exit option on fewer members beat their outside option than with it off (0.083 against 0.125), so in this fixture the option to leave lowered the value of forming: future selves leave at about week 29 into an outside life the solo rollout overrates (slice b's tail).

**KX2 under A5: PASS** (runs/hybrid-leaving/kx2-a5.json): D(off) 0, D(on) +0.015, DiD **+0.015 [+0.007, +0.028]** (11 of 12 pairings above 0); share beating the outside option 0.375 with no exit cost against 0.292 with it (here the cheaper exit does raise formation); in-future exits in 48 of 48 futures each, first at week 17 to 18 (the tally reads earlier than A4's 13-week grid). Unlike A4, with the exit option on more members beat their outside option than with it off (0.375 against 0.125): with an outside forecast played in the lived world, the option to leave adds value at formation instead of subtracting it.

## Slices (d), (e), (f): what was built

All behind new flags, off by default (code 3b11009; with every new flag off the 50 slow pin tests reproduce byte for byte and the fast suite passes).

- **(d) The fading tally** (`hybrid_tally`, `tally_half` 13, `tally_line` 0.02). Each member in a household keeps τ ← a τ + (1 − a)(y − O), O its outside option as last valued; a level trigger (τ < −0.02) or, as arms, a slope or either. A triggered member gets a lived reading (pair or lone, same arithmetic and bar, at most every 4 weeks); inside forecasts an in-future reading fires by the same rule (13-week marks, tally, distress), so forecasts and life look at the same moments. Unit tests KT0 to KT2 pass (tests/test_hybrid_tally.py): an unreachable line leaves the lived world identical; forecasts then read only at marks and distress weeks; a planted low O calls a lived reading the week after the tally crosses and every 4 weeks after; inside a forecast a member can now leave before week 13 (A4: never before week 26); τ recovers when good weeks return; a slow drift fires the level trigger and not the slope, a sharp drop fires the slope.
- **(e) Lock-in** (`exit_grow` 0.04): a leaver loses 0.04 × (weeks in)/52 of raw weekly pleasure for 13 weeks after leaving. KC1 passes (tests/test_hybrid_xcost.py): only the leaver pays, 13 weeks, at the size its weeks in set; an exit at week 26 is priced at 0.02 a week, one at week 104 at 0.08; an in-future reading prices the cost at its own week, not the choice's.
- **(f) The lived outside option** (`hybrid_outside="lived"`) and the bias arm (`leave_bias`). KO0 passes (tests/test_hybrid_outside.py): for a member in, the value equals a hand-built forecast of the world with that member gone (plus the stigma its callers subtract); for a member out, the old value exactly; the bias lowers only members in.

## Slice (g): H41 under A5, beside the old and A4 versions

Model (A5): `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit · hybrid_tally=level · tally_half=13 · tally_line=0.02 · exit_grow=0.04 · hybrid_outside=lived`, exit fallback F4 with items (F5 in the prenup arm), corrected rule. 1,320 runs (11 arms × 120 pairings × seed 0) on 4 workers under `caffeinate -i`, about 48 s a run in B (A4: 18 s). Rows in runs/hybrid-leaving/rows.jsonl; analysis.json. The run was restarted once after the stale-return bug (prereg amendment); the rows here are all from the fixed code.

**The table per arm, old > A4 > A5** (means over 120 pairings):

| Arm | Weeks together | Formed at week 0 | Held (H38 lens) | Liberty | Pleasure | Lived | Ended |
|---|---|---|---|---|---|---|---|
| B | 0.841 > 0.865 > **0.891** | 0.75 > 0.82 > **0.80** | 0 > 0 > 0 | 2.094 > 2.000 > 2.017 | 0.9624 > 0.9640 > 0.9634 | 0.9624 > 0.9640 > 0.9634 | 0.08 > 0.13 > 0.09 |
| P0.5 | 0.863 > 0.898 > 0.901 | 0.78 > 0.85 > 0.83 | 0.027 > 0.035 > 0.042 | 2.074 > 1.957 > 1.988 | 0.9637 > 0.9653 > 0.9645 | 0.9629 > 0.9643 > 0.9636 | 0.10 |
| P1 | 0.876 > 0.923 > 0.903 | 0.82 > 0.87 > 0.86 | 0.058 > 0.071 > 0.066 | 2.014 > 1.937 > 1.987 | 0.9649 > 0.9671 > 0.9660 | 0.9633 > 0.9649 > 0.9641 | 0.08 |
| P2 | 0.901 > 0.933 > 0.914 | 0.87 > 0.89 > 0.90 | 0.084 > 0.087 > 0.086 | 1.968 > 1.922 > 1.932 | 0.9670 > 0.9690 > 0.9681 | 0.9634 > 0.9646 > 0.9644 | 0.11 |
| P4 | 0.903 > 0.945 > 0.922 | 0.89 > 0.91 > 0.91 | 0.092 > 0.099 > 0.093 | 1.976 > 1.922 > 1.941 | 0.9687 > 0.9713 > 0.9697 | 0.9622 > 0.9623 > 0.9624 | 0.08 |
| trial | 0.844 > 0.856 > 0.840 | 0.74 > 0.74 > 0.74 | 0 | 2.073 > 2.085 > 2.105 | 0.9633 > 0.9644 > 0.9642 | same | 0.15 |
| cheap | identical to B in every version | | | | | | |
| prenup | 0.841 > 0.869 > 0.893 | 0.75 > 0.82 > 0.81 | 0 | 2.095 > 1.962 > 2.014 | 0.9622 > 0.9640 > 0.9634 | same | 0.12 |
| info | 0.843 > 0.884 > 0.898 | 0.77 > 0.82 > 0.86 | 0 | 2.085 > 1.984 > 1.963 | 0.9622 > 0.9637 > 0.9634 | same | 0.09 |
| lat | 0.706 > 0.727 > 0.769 | 0.58 > 0.59 > 0.58 | 0 | 2.330 > 2.286 > 2.293 | 0.9610 > 0.9623 > 0.9624 | same | 0.08 |
| all | 0.606 > 0.625 > 0.619 | 0.51 > 0.51 > 0.51 | 0 | 2.429 > 2.423 > 2.439 | 0.9597 > 0.9609 > 0.9607 | same | 0.07 |

**The version change in B** (paired by pairing, 95% bootstrap). A5 − A4: weeks together +0.026 [−0.001, +0.059], formed at week 0 −0.017 [−0.058, +0.017], liberty +0.017 [−0.029, +0.070], pleasure and lived **−0.0007 [−0.0013, −0.0001]**. A5 − old: weeks together +0.050 [+0.017, +0.092], formed +0.050 [0.000, +0.100], liberty −0.078 [−0.153, −0.010], pleasure +0.0010 [−0.0000, +0.0022]. Lived exits per B run: 0.75 (A4 0.50); each B run has 3.7 tally rethinks.

**Each arm against B under A5, and H41's verdicts.** Classes as H41's (margins: weeks together and formation 0.01, held 0.005, liberty 0.02, pleasure 0.003):

| Aid / level | Weeks together | Formed at week 0 | Held | Liberty | Pleasure | Lived | H41 |
|---|---|---|---|---|---|---|---|
| P0.5 | +0.010 [−0.017, +0.034] 0 | **+0.033** + | **+0.042** + | −0.029 0 | +0.0012 0 | +0.0002 0 | (pressure) |
| P1 | +0.012 [−0.014, +0.036] 0 | **+0.058** + | **+0.066** + | −0.029 0 | +0.0026 0 | +0.0008 0 | (pressure) |
| P2 | +0.023 [−0.008, +0.055] 0 | **+0.100** + | **+0.086** + | **−0.085** − | **+0.0047** + | +0.0010 0 | (pressure) |
| P4 | +0.031 [−0.007, +0.069] 0 | **+0.108** + | **+0.093** + | −0.075 0 | **+0.0063** + | −0.0009 0 | (pressure) |
| trial | **−0.051** [−0.085, −0.022] − | −0.058 0 | 0 | **+0.089** + | +0.0008 0 | +0.0008 0 | not supported |
| cheap | 0 (identical) | 0 | 0 | 0 | 0 | 0 | not supported |
| prenup | +0.002 0 | +0.008 0 | 0 | −0.003 0 | 0 | 0 | not supported |
| info | +0.007 0 | **+0.058** + | 0 | **−0.054** − | 0 | 0 | not supported |
| lat | **−0.122** − | **−0.225** − | 0 | **+0.276** + | −0.0010 0 | −0.0010 0 | not supported |
| all | **−0.272** − | **−0.292** − | 0 | **+0.423** + | −0.0027 0 | −0.0027 0 | not supported |

**H41 under A5: not supported** (no aid raises weeks together). On pleasure AND freedom together, no aid is a win: LAT and all aids raise liberty and cost a little pleasure (inside the margin now; under A4 all aids was harm), a trade-off; the trial raises liberty and lowers weeks together with no pleasure change; better information forms more pairs at week 0 and narrows liberty with no pleasure gain. Pressure P2 and P4 raise pleasure while holding people in and (P2) narrowing liberty: **trade-off**, as in both earlier versions; lived pleasure is flat, so the gain is the reward paid.

**Three versions (stop rule).** Same class in old, A4 and A5 (**holds across versions, three**): pressure holds people in at every level (held +); P2 and P4 raise pleasure; living apart together and all aids lower weeks together and formation and raise liberty; the prenup and cheap housing change nothing; H41 is not supported. **Version-dependent** (not patched):

- **Pressure raises weeks together**: + in old and A4 at every level, **0 in A5** at every level (point estimates +0.010 to +0.031, intervals reach below 0). The finding that held across versions so far now holds only in direction. Under A5, B itself sits at 0.89 weeks together, so there is less room; and pressure still raises formation at week 0 (+ at every level in A5).
- Formation at week 0 under pressure (old 0/+, A4 +/0, A5 + at every level); liberty under pressure (P1 old −, A4 −, A5 0; P4 old −, A4 0, A5 0); pleasure at P1 (old 0, A4 +, A5 0).
- The trial: weeks together 0, 0, **−**; formed 0, −, 0; liberty 0, +, +.
- Better information: weeks together 0, +, 0; formed 0, 0, +; liberty 0, 0, −.
- All aids: pleasure, lived and the worse-off partner 0, −, 0 (A4's "harm" does not hold).
- The prenup's liberty: 0, −, 0. LAT's non-offsettable suffering: 0, +, +.

## P-AUTH: does knowing you could leave later make people more willing to try living together?

B arm under A5, with the exit option in forecasts against without it (`hybrid_exit` off, all else A5; 120 pairings; runs/hybrid-leaving/a5_noexit.jsonl):

- Formed at week 0: **+0.050 [0.000, +0.100]**, class 0 (the interval touches 0). **P-AUTH held** by its preregistered rule: the exit option does not raise week-0 formation beyond the margin with an interval clear of 0. It is DESCRIPTIVE (the power check resolves formation effects of about 0.065 and up), and the point estimate leans toward "yes, a little".
- Weeks together: **+0.047 [+0.017, +0.088]**, class +. With the exit option the pairs spend more weeks together: more form, and they re-form more after leaving.
- Under A4 (no lock-in, solo outside), the same comparison was formed +0.067 [+0.025, +0.117] (+) and weeks together +0.012 [+0.002, +0.024].

So with lock-in, the author's prediction holds for the moment of moving in (the formation gain shrinks from +0.067 to +0.050 and its interval reaches 0), but not for time together. What this can say: in this model, lock-in (an exit that gets dearer with time) takes some, not all, of the option value of exit at formation. What it cannot say: anything about sunk cost, which the agent does not have.

## The outside forecast under A5 (KO1)

B arm, bar exits with at least 13 weeks of room: mean L − O = **+0.016 [−0.010, +0.044]** over 79 exits. The bar was |mean| ≤ 0.02 with the interval inside ±0.04: the mean meets it, the interval's upper end (0.044) does not. **KO1: FAIL** (narrowly). In P2: +0.040 [+0.019, +0.064] (the forecast is somewhat too pessimistic under pressure).

What the lived outside option did change is the tail:

| Version (B) | Bar exits | Mean L − O | Mean abs error | Worst | Share below −0.2 |
|---|---|---|---|---|---|
| old | 48 | +0.014 | 0.109 | −0.96 | 0.06 |
| A4 | 54 | +0.044 | 0.094 | −0.81 | 0.02 |
| A5 | 79 | +0.016 | **0.076** | **−0.31** | 0.05 |
| A5 with the solo outside (sweep, 60 pairings) | 26 | −0.010 | 0.089 | −0.25 | 0.08 |

So playing the outside option in the lived world removes the story-4-sized misses (−0.8 to −0.96) and lowers the mean absolute error, but leaves a small optimistic-for-staying bias and a fat-ish tail. The remaining error is not fitted away (nothing may be). Known reasons it cannot be exact: the outside futures hold no in-future readings and no re-formation (a retry is a harness step, never inside a forecast), while lived leavers re-form (15 re-formations in B); the arrangement is ranked by the old solo rollouts; a lived leaver's own later choices follow the lived rule.

## The second measures

**Timing (lv-same; not a target).** Share of reading status quos whose forecast had a member leave, against the lived world:

| Arm | Within 13 weeks: forecast / lived | Within 52 weeks: forecast / lived |
|---|---|---|
| B, A4 | 0% / 4.5% | 13.4% / 14.8% |
| B, A5 | **28.6% / 9.4%** | **42.0% / 22.3%** |
| P1, A5 | 21.6% / 9.4% | 34.3% / 20.7% |
| trial, A5 | 13.3% / 14.2% | 29.5% / 25.2% |
| prenup, A5 | 29.0% / 10.6% | 42.2% / 23.4% |

Forecasts now look when life looks, and they now leave early, but **too often**: in B the 52-week gap is 0.20 (the prereg calls anything over 0.10 a weakness of the stand-in). The cause is the stand-in's arithmetic, not the timing: an in-future reading judges staying by a look-back over the last 13 future weeks against the anchor, while the lived reading forecasts 52 weeks ahead; a short bad stretch inside a future (now read at once by the tally) clears the bar on a look-back far more easily than on a forecast. Readings themselves are more frequent too: a status quo is logged at every rethink (1,592 in B against 842 under A4).

**Rethinks.** Each B run has 3.7 lived rethinks on average (readings the tally called). Grouped into episodes per member (rethinks no more than 13 weeks apart; counted from the lived rethink log, `hybrid_leaving.episodes`): 96 episodes in B, of which **41 (43%) ended in leaving** within 13 weeks of the last rethink, **38 (40%) came back** without leaving, and 17 were still open when the run ended (P2: 68 episodes, 37 left, 25 back). Thinking about leaving is common and often reversible here, but far more often ends in leaving than in Hawkins et al. (2017) (about one in ten thinkers separate within a year); a story comparison only. (The per-week instrumentation first used for this, `spells`, also counted the solo rollout worlds of outside options and is not used; it was caught before reporting.)

**Paths again (A5, B):** of 90 lived exits, suffering path 54, quiet path **1**, mixed 6, no fall 15, short spell 14 (second windows: quiet 1). P2: suffering 44, quiet 0. The tally does not create the quiet path.

**Lone weeks (A5).** B 3.1% of weeks, no run with a lone stretch over 26 weeks in serious suffering (longest 5 weeks); 75 lone readings, 10 put a member past the bar; 15 emptied households re-formed.

## The swept assumed numbers (B arm, 60 pairings, one number at a time; DESCRIPTIVE)

Centre (A5 on the same 60 pairings): weeks together 0.901, formed at week 0 0.833, lived exits 0.73 a run, 2.5 rethinks a run (on these pairings), forecast/lived leaving within 13 weeks 20.7% / 9.7%; rethink episodes 41 (19 left, 16 back). Episodes per arm (left / back): half-life 4: 100 (32 / 62); 26: 31 (20 / 10); line 0: 73 (30 / 38); line 0.05: 29 (20 / 8); slope 101 (36 / 58); both 97 (36 / 50); growth 0: 42 (23 / 14); 0.02: 41 (21 / 15); 0.08: 42 (19 / 17); solo outside 40 (13 / 22); bias 0.02: 36 (11 / 21); bias 0.05: 32 (7 / 21).

| Arm | Weeks together (vs centre) | Formed | Exits/run | Rethinks/run | Leave within 13 wk: forecast / lived | Pleasure vs centre | KO1 mean [interval] |
|---|---|---|---|---|---|---|---|
| half-life 4 | +0.002 | 0.867 | 0.82 | 4.2 | 26% / 11% | +0.0006 (0) | +0.013 [−0.017, +0.038] |
| half-life 26 | **−0.011** [−0.027, −0.001] | 0.833 | 0.70 | 1.8 | 16% / 9% | 0 | +0.030 |
| line 0 | +0.002 | 0.883 | 1.05 | 5.3 | 24% / 13% | +0.0008 (0) | +0.032 |
| line 0.05 | −0.010 | 0.833 | 0.70 | 1.6 | 15% / 10% | 0 | +0.045 |
| slope | −0.006 | 0.867 | 1.00 | 2.5 | **15% / 14%** | +0.0006 | +0.044 |
| both | −0.002 | 0.867 | 0.87 | 4.5 | 26% / 11% | 0 | +0.040 |
| exit growth 0 (no lock-in) | 0.000 | 0.833 | 0.80 | 2.7 | 21% / 11% | **+0.0005** [+0.0003, +0.0008] | +0.024 |
| exit growth 0.02 | −0.001 | 0.833 | 0.75 | 2.5 | 21% / 10% | +0.0002 | +0.025 |
| exit growth 0.08 | +0.007 | 0.833 | 0.77 | 2.6 | 22% / 10% | **−0.0007** [−0.0012, −0.0003] | +0.026 |
| solo outside (no slice f) | +0.008 | 0.833 | **0.48** | 3.1 | 19% / 8% | 0 | −0.010 [−0.049, +0.026] |
| bias 0.02 | **+0.015** [+0.002, +0.032] | 0.833 | 0.45 | 3.2 | 22% / 7% | −0.0002 | +0.018 |
| bias 0.05 | **+0.025** [+0.012, +0.041] | 0.833 | 0.30 | 2.9 | 20% / 4% | −0.0006 (0) | +0.088 |

What the numbers did:
- **The tally's numbers** move how often agents rethink (1.6 to 5.3 a run) and how often they leave (0.70 to 1.05 a run) far more than they move weeks together (within ±0.011) or pleasure (within the margin). A lower line or a shorter memory means more rethinks and more exits. **The slope arm is the only one whose forecasts leave within 13 weeks about as often as lived agents do** (15% against 14%); this is a second measure, not a target, and no number is changed for it.
- **Lock-in** (exit growth 0 to 0.08) barely moves who forms, who stays or how often anyone leaves (0.80 to 0.75 to 0.77 exits a run, not monotonic); its only resolved effect is the cost itself, paid by leavers: pleasure +0.0005 without it, −0.0007 at double it. In this two-person world the growing exit cost is too small against the reasons people leave to change the decision, at these sizes.
- **The lived outside option** (against solo) raises lived exits from 0.48 to 0.73 a run without changing weeks together or pleasure: the solo rollout's misses ran both ways, and correcting them sends more members out (more of them re-form).
- **The bias arm** (agents overpredict the pain of leaving) does what E7 expected: fewer exits (0.45, 0.30 a run), more weeks together (+0.015, +0.025), no pleasure change inside the margin, and a forecast now more pessimistic about leaving than life is (KO1 +0.088 at b = 0.05). It holds members in without making them better off: by the verdict rule's lens it is staying more without pleasure, not a win.

## K1 under A5

The trap's held share **0.128** (16 held of 125 staying member-weeks; 3 of 12 pairings carry all of it), baseline 0.000 (224 weeks): **PASS** for the first time (Amendment 3 and A4: 0.077). Read with care: every run in both fixtures ended (all 24 households), staying weeks are few, and the pass rests on three pairings (runs/hybrid-fix/trap-a5.json). A likely reason, not checked run by run: with the lived outside option, a member in the trap now forecasts leaving with nothing as it would live it.

## Known-answer checks (A5)

| ID | Result | Bar | |
|---|---|---|---|
| PIN | all 50 slow pin tests byte for byte with every new flag off (code 3b11009; the fix at 1affe34 touches only `hybrid_outside="lived"`) | byte for byte | **PASS** |
| KT0, KT1, KT2 | 8 tests (tests/test_hybrid_tally.py) | | **PASS** |
| KC1 | 5 tests (tests/test_hybrid_xcost.py) | | **PASS** |
| KO0 | 6 tests incl. the stale-return regression (tests/test_hybrid_outside.py) | | **PASS** |
| KX2 (pure exit cost) | A4: DiD +0.019 [+0.005, +0.036]; A5: +0.015 [+0.007, +0.028]; formation not lower; exits in 45/48 and 48/48 futures | DiD > 0, interval above 0 | **PASS** (both) |
| KO1 | +0.016 [−0.010, +0.044], 79 bar exits in B | ±0.02, interval inside ±0.04 | **FAIL** (interval) |
| KL2 | story 4 under A5: both leave at the trial's end (week 78), nobody is ever alone | no stuck stretch over 26 weeks | **PASS** (trivially: no lone weeks) |
| K1 | trap 0.128, baseline 0.000 | ≥ 0.10 / ≤ 0.02 | **PASS** (first time; 3 pairings carry it) |
| PT-R | T1 0.953 (v2 0.955), T2 0.966 (0.973), T3 95.0% (94.7%), T4 98.1% (95.9%), T5 1.05, T6 holds (see_friend gap 0.0005) | no more than 0.02 below v2; T5 in 0.8–1.25 | **PASS** |
| KW | w = 2 declines, w = 0 forms, with A5's flags (tests/test_hybrid_tally.py) | | **PASS** |
| PT-H | A1's sample (20 lives), A5 flags: H1 **+0.0048** [+0.0022, +0.0074]; H2 **0.949** (1,240 option-units); H3 **93.9%** (455); 593 choice-units incl. 526 readings (+0.0043) and 5 lone (−0.0021); runs/hybrid-passtest-a5/ | ±0.010 (interval in ±0.015); ≥ 0.80; ≥ 80% | **PASS** |

**Ready to freeze? No.** The prereg's rule needs every check but K1 to pass; KO1 fails. Nothing was changed to make it pass.

## Expectations written before the run

| ID | Expected | Actual | |
|---|---|---|---|
| E1 | Pressure raises weeks together and holds people in | held + at every level; weeks together +0.010 to +0.031, intervals reach 0 | **misses** (half) |
| E2 | Forecasts leave within 13 weeks (> 0); lived 13-week rate > 0 | 28.6% and 9.4% in B | holds |
| E3 | Exits rise A5 > A4; lock-in pulls them down | 0.75 vs 0.50 a run in B (holds); growth 0 / 0.02 / 0.04 / 0.08: 0.80 / 0.75 / 0.73 / 0.77 (60 pairings) | holds in part (lock-in effect small, not monotonic) |
| E4 | KO1 passes and the error moves toward 0 | KO1 fails on its interval; mean abs error 0.094 → 0.076, worst −0.81 → −0.31 | **misses** (the bar), holds (the direction) |
| E5 | B's formation under A5 ≤ A4 | 0.80 vs 0.82 | holds |
| E6 | P-AUTH holds | held on formation (+0.050, interval touches 0); weeks together + | holds as preregistered |
| E7 | Bias arms leave less and hold more members below their outside option | exits 0.73 → 0.45 → 0.30 a run; weeks together +0.015, +0.025 | holds |

## Story check (four lives)

1. **Story 4 (trial, p-peacekeeper with p-wanderer).** As under A4: both leave at the trial's end; nobody is left alone; the bad spiral never starts. Matches.
2. **B, p-host with p-peacekeeper.** B's tally crosses at week 44 and calls a rethink; A leaves on the bar that week; B, alone, rethinks at 48 and leaves at 52; they re-form; at 130 both leave. Reading this life found the stale-return bug (the outside forecast said −0.20; B lived +0.77): fixed before the confirmatory run.
3. **B, g-01110 with g-11011 (a rethink that came back).** From week 78 a shock raises B's suffering (0.07 → 0.45 a week); its tally falls to −0.12 and it rethinks every 4 weeks from week 95; every forecast says stay (the 52-week future includes recovery); suffering returns to 0.07 by week 117 and the tally climbs back above 0. Matches "thinking about leaving is reversible".
4. **P2, p-bargainer with p-wanderer (pressure with lock-in).** B (p-wanderer) suffers 0.3 to 0.45 a week for most of the run; its tally sits at −0.2 to −0.3 for about 120 weeks and calls a rethink every 4 weeks (about 30), and it never leaves; the stay lens marks it held. Matches the measures (pressure holds people in); also a mismatch worth naming: in this model a member can "think about leaving" every month for two years with nothing changing, because each rethink is a fresh forecast that says staying (with the reward) beats leaving.

## New gaps

- **The quiet path is close to absent** (slice b; A5 the same: 1 of 90). People here leave on rising suffering. Not fixed: the saturating pleasure scale leaves little room for the good to fade.
- **The routine misvalues repeated friend visits** (story 4): it values one more visit at full strength while the world habituates it, so a member alone can spend every unit on visits that no longer restore connection, and rest starves. Same class as Amendment 2's time-together fix. Not fixed (the author's call; it is the routine, not the leave rule). PT-R does not see it (population gap 0.0005): it bites in long same-friend streaks.
- **Stale return values in the lived world and in A4's forecasts.** `world.ret_value` survives a return, so a member who leaves later can walk straight back on a value from an earlier spell. Fixed only inside the lived outside option; elsewhere reported, not changed.
- **The in-future look-back leaves too often** now that it reads when life reads (52-week rate 42% vs 22% in B). The stand-in judges 13 weeks back where life forecasts 52 ahead.
- **Re-formation is invisible to every forecast** (a retry is a harness step), one reason the outside forecast stays a little pessimistic about leaving.
- **Lock-in at these sizes does not bite** in the two-person world: exits, formation and weeks together barely move between growth 0 and 0.08.

## Can be about / cannot be about

This can be about how the hybrid's leaving behaves in the formation check's two-person household when a fading tally sets when it rethinks, exits get dearer with time and the outside option is played in the lived world, and how H41's arms move under that version beside two earlier ones. It cannot be about people, how people time their exits, sunk cost (not in the agent), real leases or pets, or the many-agent world.

## Reproduction

`uv run python scripts/hybrid_leaving.py --paths`, `--paths-analyze` (slice b); `--kx2 --flags a4|a5`; `--story`; `--run a5` (about 6 hours on 4 workers); `--run a5_noexit --arms B`; `--run half4,half26,line0,line05,slope,both,grow0,grow02,grow08,solo,bias02,bias05 --arms B --every 2`; `--analyze`; `--life ARM A B`; `--reach`. `uv run python scripts/hybrid_fix_check.py --trap --a5`; `uv run python scripts/value_consistency.py --hybrid --world --a5 --run`; `uv run python scripts/hybrid_passtest.py --a5 --audit`, `--a5 --analyze`. Tests: `uv run pytest tests/test_hybrid_tally.py tests/test_hybrid_xcost.py tests/test_hybrid_outside.py`; pins `uv run pytest -m slow`. The run queue is runs/hybrid-leaving/queue.sh.
