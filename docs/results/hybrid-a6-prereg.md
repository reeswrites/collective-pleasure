# Two hybrid bugs fixed before the freeze: friend visits at the world's satiety, and no stale return values (preregistration)

Wording rule: agents feel nothing; "pleasure", "suffering", "value", "forecast", "tally" and "held" are glosses for modeled numbers (ADR 0010).

Status: written and committed before any code for these changes and before any run. Nothing here is a result. Scripted agents (the hybrid), no model calls. Recorded as Amendment 6 of the hybrid prereg ([hybrid-agent-prereg.md](hybrid-agent-prereg.md)).

**The author's choice.** "Fix the two hybrid bugs found in Amendment 5, rerun, then the freeze decision is made" (logged at 199aa1b). Both bugs are named in [hybrid-leaving.md](hybrid-leaving.md) ("New gaps") and its prereg's amendment. Neither fix sets a number: each makes one part of the code read what the world already computes.

**Model versions (ADR 0020).**
- Old: `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world` (Amendment 3; frozen as `hybrid-N/1`).
- A4: old plus `hybrid_lone · hybrid_exit`.
- A5: A4 plus `hybrid_tally=level · tally_half=13 · tally_line=0.02 · exit_grow=0.04 · hybrid_outside=lived`.
- **A6 (new): A5 plus `friend_satiety · fresh_return`.** Both new flags off by default.

What I knew when writing this: everything in hybrid-leaving.md and its rows (A5's checks, KO1 +0.016 [−0.010, +0.044], forecast vs lived leaving 42% vs 22% at 52 weeks in B, the quiet path 1 of 90). No code for either fix exists; nothing has run under A6.

**Can be about / cannot be about.** This can be about whether the hybrid, with both bugs fixed, passes the same known-answer checks A5 was held to, and how H41's arms and the author's exit-option prediction move under it beside old, A4 and A5. It cannot be about people, friendship, habituation in real life, or the many-agent world. Limits that apply ([limits.md](../limits.md)): 1, 2, 4, 5, 6, 12, 13 (every number is still ASSUMED; none is added).

## The two fixes

**Bug 1, friend visits (`FixConfig.friend_satiety`, default False).** The routine (`agent_values.expected_scales`) values one more visit to a friend at full strength (scale 1) unless the persona's variety policy is "adaptive", while the world plays every visit at that friend's satiety scale (`WeeklyWorld._lever_visit`: `Satiety.use`). Amendment 2 fixed the same error for time together (`satiety_expect="world"`) and left this clause. Effect seen in story 4 (A4): a member alone spent every unit on visits that no longer restored connection, and rest starved. Fix: with the flag on, the routine values one more visit at the scale the world would give that visit now (the bond the visit would go to, its satiety, read without changing anything; with one variant per friend this equals `Satiety.use`'s return). It is read wherever `expected_scales` is read (the weekly utilities and the week planner), as Amendment 2's together clause is. No number is set.

**Bug 2, stale return values (`FixConfig.fresh_return`, default False).** A return reading sets `world.ret_value[r]`, the value of returning for the member out. It survives the return, so a member who later leaves again carries a value from an earlier spell and may walk straight back in on it. A5 dropped it only inside the lived outside option's futures. It remains in the lived world and inside every forecast copy (A4's in-future exits, A5's tally readings). Fix: with the flag on, when a member leaves a household its return value is dropped (in the world's own leave step, so the lived world, every forecast copy and every outside future get the same rule). A new return needs a new return reading. A5's narrower drop stays as it is (with the flag on it changes nothing).

## Known-answer checks (bars are A5's, unchanged)

| ID | What | Passes iff | Where |
|---|---|---|---|
| PIN | Old results reproduce | both new flags off: every slow pin test reproduces byte for byte, and A5's unit tests pass | `uv run pytest -m slow`, fast suite |
| KF1 | Bug 1 shown, then fixed (unit) | flag off: in a life where satiety bites, the routine's own term for a visit equals one at scale 1 (non-adaptive persona) while the world records a lower scale for that visit (the bug); flag on: the own term equals one at exactly the scale the world records for a visit played at that call | tests/test_hybrid_a6.py |
| KR1 | Bug 2 shown, then fixed (unit) | flag off: a member that returned on a value and later leaves again sees a return value above 0 the week it leaves, in the lived world and in a forecast copy (the bug); flag on: 0 until a new return reading sets one | tests/test_hybrid_a6.py |
| KT0–KT2, KC1, KO0 | A5's unit checks | pass with A6's flags where they take a version | tests/test_hybrid_tally.py, _xcost.py, _outside.py |
| KX2 | Pure exit cost | A5's clauses (i) to (iii) under A6 | `hybrid_leaving.py --kx2 --flags a6` |
| KO1 | The outside forecast is accurate | B arm under A6: mean L − O over lived bar exits within ±0.02, 95% interval inside ±0.04 | `--analyze` |
| KL2 | Story 4 | no stretch of more than 26 weeks in which a member alone stays though its outside option beat staying at every lone reading | `--story --version a6` |
| K1 | The trap (reported) | ≥ 0.10 trap, ≤ 0.02 baseline | `hybrid_fix_check.py --trap --a6` |
| PT-H | Forecasts against held-out futures | A1's sample, A6 flags: H1 within ±0.010 (interval inside ±0.015); H2 ≥ 0.80; H3 ≥ 80% | `hybrid_passtest.py --a6` |
| PT-R | The routine at one week | the 40-life value check, A6 flags: T1–T4 no more than 0.02 below v2 on the same sample (the reference stays `value-consistency-v2-sat-world`, as for A5, so the bar does not move); T5 in 0.8–1.25; T6 holds | `value_consistency.py --hybrid --world --a6 --run` |
| KW | The suffering weight | w = 2 declines, w = 0 forms, with A6's flags | tests/test_hybrid_a6.py |

## Measures (descriptive, as in A5; nothing is a target)

- **Step-5 exit paths again** (slice b's classifier, both window pairs) on A6's B, P2 and trial arms, beside A5's. The question: does the quiet path (pleasure fading at flat suffering) appear now? A5's diagnosis put the cause in the saturating scale, not in these bugs, so I expect it still rare. If it is still near 0, that stays a gap.
- **Forecast vs lived leaving** (share of reading status quos with a member leaving within 13 and 52 weeks, forecast against lived), B, P1, trial, prenup, beside A5 (B: 28.6% / 9.4% and 42.0% / 22.3%). A gap above 0.10 at 52 weeks is a weakness, as before. The in-future look-back is unchanged, so I expect the gap to stay.
- **Rethink episodes**, lone weeks, lived exits per run, as in A5.

## H41 under A6 and the author's exit-option prediction

- **Design**: A5's, unchanged (11 arms × 120 confirmatory pairings, seed 0, 1,320 runs, at most 4 workers, `caffeinate -i`), A6's flags. Rows in runs/hybrid-a6/rows.jsonl. No sweeps.
- **Four versions, stop rule (ADR 0020)**: per arm and key, the sign class against B under old, A4, A5 and A6. Same class in all four: holds across versions (four); else version-dependent with the versions named; never patched.
- **H41's verdict functions unchanged**: pleasure AND freedom together; one up and one down is a trade-off, never a win.
- **P-AUTH (the author's prediction)**: B arm under A6 with `hybrid_exit` off against on (120 pairings). The exit option does not raise formation at week 0 by H41's class rule (margin 0.01, interval clear of 0): held or missed. Weeks together reported beside. Shown beside A4 (+0.067 formed, + class) and A5 (+0.050 [0, +0.100], held). DESCRIPTIVE below about 0.065 (A5's power check).

**Expectations (not bars):** F1 the friend fix moves units from visits to rest for members who see the same friend often, and lowers non-offsettable suffering a little in long lone or post-exit stretches; F2 fewer immediate re-entries after a lived exit (fresh return), so lived exits last longer; F3 KO1's tail does not grow; F4 pressure still holds people in (held + at every level).

## Verdict rule

A6 is **ready to freeze as `hybrid-N/2`** iff PIN, KF1, KR1, KT0–KT2, KC1, KO0, KX2, KO1, KL2, PT-H, PT-R and KW all pass. K1 is reported. If a check fails, it is reported as failed and not patched; the design changes only where a check shows the code disagrees with this prereg (a bug), with numbers before and after, and never to move an H41 outcome. If A6 is not ready, the spec says which version is the best candidate and why, and keeps `hybrid-N/1`.

## Can every verdict happen?

- KF1 and KR1 are written to fail on the flag-off code (each test asserts the bug first), so both "bug" and "fixed" are reached.
- Ready / not ready: every check can fail as in A5; KO1 failed under A5.
- Four-version labels and P-AUTH held/missed: A5's `--reach` synthetic checks, run with four row sets.
- The metric sees the mechanism: the friend fix lands in the routine's utilities (so in actions, the hedonic rows, and every forecast's later weeks); the return fix lands in `obs["return_value"]` and so in `propose`, in the lived world and in forecast copies.

## Are we measuring what we say?

- **Construct card.** Friend visit value = the routine's projected change to this week's close from one more visit, now at the satiety the world will apply; it does not encode choosing a different friend. Fresh return = a return needs a valuation made during this out-spell; it does not encode reconciliation, memory or regret. Everything else as A5's card.
- **Known-answer cases**: KF1, KR1 (each shows the bug, then the fix), KX2 (exact model), KO1 (the forecast against the life lived), K1 (the trap).
- **One other way to measure it**: step-5 classes on two window pairs; leaving timing at 13 and 52 weeks; held by H38's lens and wide; formation as formed at week 0 and weeks together.
- **Story spot-check**: after the run, read story 4 (trial), one B life with a lived exit and no return, one life with a long same-friend streak, one P2 life; say whether each matches the measures.

## Findings this could move (ADR 0020)

- **Row 56, Amendment 5**: its freeze verdict (not ready, KO1) is retested; its "new gaps" on friend visits and stale returns are addressed.
- **Row 55, Amendment 4**: not rerun as its own version; A6 is shown beside it.
- **Row 54, H41**: rerun under A6; label set by the four-version stop rule.
- **Row 52, hybrid pass tests** (PT-H, PT-R, KW, K1): rerun with A6's flags.
- **Row 53, formation check 3's hybrid column**: not rerun (cost); keeps its label; layer a2 ports against the frozen version's own formation check.
- **Rows 48, 49, 51 (v2, v2b, the saturating scale)**: not affected (the flags are off in every v2 and v2b run; the friend fix would change the v2 routine if turned on there, which no run here does).
- **limits.md 13** and **the many-agent spec's freeze note**: updated after the results.

## Not testable by design

Whether people misjudge habituation to friends; whether people go back to an ex on an old feeling (not modeled: the fix removes it, it does not test it).

## Limits stated now

Scripted agents; one persona sample; one seed per pairing; one parameter point (no sweeps); the in-future look-back, outside futures without re-formation, and every assumed number are A5's.
