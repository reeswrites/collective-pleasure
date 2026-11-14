# How the hybrid decides to leave: a fading tally, lock-in, and an accurate outside forecast

Wording rule: agents feel nothing; "pleasure", "suffering", "value", "forecast", "tally", "rethink" and "held" are glosses for modeled numbers.

Model: slice (b) ran on A4 (`hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit`) and on the old version (Amendment 3, the same without the last two flags). Later slices name their version where they report. Preregistration: [hybrid-leaving-prereg.md](hybrid-leaving-prereg.md) (commit 8a291b0, before any code or run).

Status: in progress, written slice by slice. Scripted agents, no model calls, every number ASSUMED.

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

KX2 under A5 is reported with slice (g).
