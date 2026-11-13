# Formation check, third run: four agent sets side by side

Wording rule: agents feel nothing; "pleasure", "suffering" and "value" are glosses for modeled numbers.

Status: run on 2026-11-12 to 13, after the preregistration ([formation-check-3-prereg.md](formation-check-3-prereg.md), commit 9ed02ba) and its Amendment 1 (commit cfa6c7a: the time-together fix carried by v2, v2b and the hybrid; the analysis details; the reach checks). Step 3 of the step-back plan. Scripted agents, no model calls, every number ASSUMED. 5,760 runs (4 agent sets × 3 arms × 120 pairings × seeds 0 to 3), 17,817 s on 4 workers, kept awake with `caffeinate -i`. Rows in runs/formation-check-3/.

## In one paragraph

**Pressure held people in under every agent set, and that is the only answer that held across the four.** The share of stay readings where a member stays only because the pressure is counted is above 0 under v1, v2, v2b and the hybrid (0.05 to 0.36). Everything else is **agent-dependent** by the stop rule. Liberty narrows under three sets and not under v1. Pleasure is within the margin under v1, lower under v2, and higher under v2b and the hybrid. Withdrawal alone lowers pleasure under v1, does nothing measurable under v2 and the hybrid, and raises it under v2b. **No agent set gives a win.** The verdicts are: v1 not a win (pleasure not raised), v2 harm, v2b trade-off, hybrid trade-off. Under the hybrid, the agent the step-back plan built to be the fair test, pressure raises pleasure by +0.011. Almost all of that is the reward being paid: lived pleasure, with the reward and stigma taken out, falls by 0.001, and liberty narrows. That is close to what the exact model predicts for a household worth having.

## The table per agent set

Pressure is G-L4 against G-L0, and withdrawal alone is G-W4 against G-L0, paired by pairing with seeds averaged first. Intervals are 95% bootstrap by pairing. Pleasure is on the saturating scale (ADR 0019).

| | **v1** | **v2** | **v2b** | **hybrid** |
|---|---|---|---|---|
| Formed at week 0, no pressure (G-L0) | 0.93 | 0.22 | 0.66 | 0.91 |
| Weeks together, G-L0 / G-L4 | 0.90 / 0.92 | 0.28 / 0.56 | 0.55 / 0.86 | 0.92 / 1.00 |
| Formed households that end, G-L0 / G-L4 | 0.25 / 0.20 | 0.92 / 0.81 | 0.71 / 0.33 | 0.07 / 0.00 |
| **P1 held share at G-L4** (bar ≥ 0.10, interval above 0.05) | **0.061** [0.043, 0.082] | **0.364** [0.320, 0.409] | **0.155** [0.119, 0.191] | **0.055** [0.033, 0.081] |
| holds? | no (above 0, below the bar) | yes | yes | no (above 0, below the bar) |
| **P2 liberty, L4 − L0** (lower partner) | −0.019 [−0.053, +0.015] | **−0.454** [−0.537, −0.370] | **−0.385** [−0.470, −0.303] | **−0.087** [−0.147, −0.033] |
| holds? | no | yes | yes | yes |
| **P3 pleasure, L4 − L0** | +0.004 [−0.002, +0.009] | **−0.019** [−0.024, −0.014] | **+0.010** [+0.007, +0.013] | **+0.011** [+0.011, +0.012] |
| outcome | within margin | lowers | raises | raises |
| **Lived pleasure** (reward and stigma out), L4 − L0 | −0.012 [−0.016, −0.009] | −0.006 [−0.009, −0.003] | **+0.003** [+0.001, +0.006] | −0.001 [−0.002, −0.000] |
| **P4 withdrawal alone, W4 − L0** | **−0.014** [−0.018, −0.010] | +0.002 [−0.001, +0.004] | **+0.006** [+0.003, +0.008] | −0.001 [−0.002, +0.000] |
| holds? | yes | no | no (opposite sign) | no |
| Worse-off partner, L4 − L0 | +0.007 [−0.002, +0.014] | −0.029 [−0.037, −0.022] | +0.012 [+0.007, +0.017] | +0.013 [+0.012, +0.015] |
| Weeks near the top (≥ 0.95), L4 − L0 | +0.089 | +0.083 | +0.211 | +0.099 |
| Old capped line, L4 − L0 | +0.000 [−0.006, +0.006] | −0.032 [−0.037, −0.027] | −0.003 [−0.006, +0.001] | +0.001 [+0.000, +0.002] |
| Suffering (both kinds), L4 − L0 | +0.006 [−0.003, +0.015] | +0.043 [+0.030, +0.057] | −0.014 [−0.024, −0.004] | −0.003 [−0.009, +0.003] |
| Suffering in the block after a reading: held / worth | 0.165 / 0.156 | 0.160 / 0.165 | 0.138 / 0.087 | **0.242 / 0.086** |
| **Verdict** (pleasure AND freedom) | **not a win** (pleasure not raised) | **harm** | **trade-off** | **trade-off** |

Holm-adjusted p within each set: v1 P1 0.42, P2 0.42, P3 0.42, P4 0.0004; v2 0.0006, 0.0004, 0.0006, 0.88; v2b 0.0006, 0.0004, 0.0006, 1.0; hybrid 0.36, 0.005, 0.0008, 0.09.

## The stop rule

| Claim | v1 | v2 | v2b | hybrid | Reading |
|---|---|---|---|---|---|
| P1 held share (class by interval) | + | + | + | + | **holds across the four sets: pressure holds people in** |
| P2 liberty | 0 | − | − | − | **agent-dependent** |
| P3 pleasure | within margin | lowers | raises | raises | **agent-dependent** |
| P4 withdrawal alone | − | 0 | + | 0 | **agent-dependent** |
| Verdict | not a win | harm | trade-off | trade-off | **agent-dependent, but never a win** |

As preregistered, nothing was patched, no set was changed, and no arm was dropped. Read against its 0.10 bar, P1 holds only under v2 and v2b. As a sign, though, held is above 0 under all four sets, and the stop rule reads the sign.

## Reading it

**Freedom first.** Pressure holds someone in under every agent set. It holds fewest where households are worth having (v1 6%, hybrid 5% of readings) and most where they are not (v2 36%). Liberty with powers falls under v2, v2b and the hybrid. That is mostly a change of state, not of rules: the dial changes no card, but it puts more people in households, where the baseline rules give a member fewer options than living apart does (v2's G-L0 liberty is 2.67, with most members apart). Under v1, households form at 0.93 with or without pressure, so liberty barely moves.

**Pleasure next.** The sign of pressure's effect on pleasure moves with where each agent set's households sit, as the exact model said it would. Where households are worth little (v2), pressure pushes pairs in, the households break (81% still end), and the members then pay stigma while living apart: pleasure falls by 0.019 and the worse-off partner loses 0.029. Where they are worth having (the hybrid, v1), the total is near or above the margin, and **lived pleasure falls under both**. The gain is the reward, paid to people who were mostly together anyway. On the old capped line the hybrid's gain disappears (+0.001), because the cap hid exactly that reward.

**v2b is the one set where pressure helps how people live** (lived +0.003). It is also the set that under-forms most where forming would help: v2b forms 0.66, and 71% of its households end. Pressure pushes 32 points more pairs in at week 0 and cuts endings from 71% to 33%. That is the exact model's one route by which pressure can help lived pleasure: choosers who under-form. It is still a trade-off, because 15% of readings are held and liberty falls.

**Withdrawal.** Under v1, withdrawal lowers pleasure (−0.014), as before. Under v2b it raises pleasure, which the exact model says cannot happen. The story spot-check below shows how. Without withdrawal, one member sees friends one and a half times a week, rates the outside option above staying, and leaves at week 39, and the partner's life apart falls to about 0.5 pleasure with non-offsettable suffering of 0.5. With withdrawal, the wish to see friends is cut, the leaver stays, and both do better. Withdrawal is working as a brake on one member leaving at the other's cost, the "one who leaves does not count the partner" case in the exact model's notes. The exact model's withdrawal never holds anyone because its choosers already count everything. This one is left open, not patched.

**Being held goes with suffering under the hybrid.** Members in readings classed held had nearly three times the suffering in the following 13 weeks (0.24 against 0.09). Under v2b the ratio is 1.6; under v1 and v2 there is no difference. The hybrid's yardstick is pleasure only (declared in its prereg), so pressure can keep a member in while their suffering is high: see the first story.

## Against the exact model

Each set is placed on the household-worth axis by its own G-L0 week-0 formation, then read against the exact model's saturating-scale sign map for the corrected chooser.

| Set | Formed at G-L0 | Placed at worth | Expected P3 | Exact L4 − L0 | Simulated | Exact held | Simulated held | Lived lower? (exact: yes) | Withdrawal lowers? (exact: yes) |
|---|---|---|---|---|---|---|---|---|---|
| v1 | 0.93 | 0 | within margin or raises | +0.011 | +0.004, within margin | 0.19 | 0.06 | yes | **yes** |
| v2 | 0.22 | −0.15 | within margin or lowers | −0.016 | −0.019, lowers | 0.40 | 0.36 | yes | no (0) |
| v2b | 0.66 | −0.04 | within margin or raises | +0.007 | +0.010, raises | 0.31 | 0.15 | **no (+0.003)** | **no (+0.006)** |
| hybrid | 0.91 | 0 | within margin or raises | +0.011 | +0.011, raises | 0.19 | 0.05 | yes | no (0) |

- **Signs of the total agree for all four sets**, and so does their order: hybrid ≥ v2b > v1 > v2 on the simulation's side against hybrid = v1 > v2b > v2 on the exact one, with only v1 and v2b out of place. The sizes are close for v2, v2b and the hybrid; v1 runs below.
- **Held is above 0 under every set, as the exact model says.** The simulation holds fewer people than the exact model wherever households are worth having (0.05 to 0.06 against 0.19). Its choosers are close to the planner in those worlds.
- **Lived pleasure is lower under three sets, as expected.** v2b is the exception, and it is the exception the exact model allows: an under-forming chooser.
- **Withdrawal disagrees.** It lowers pleasure only under v1. Under v2 and the hybrid the effect is 0; under v2b it is positive. The exact model has no member who leaves at the partner's cost without counting it, so it cannot produce this.

## Story spot-check (three lives, read week by week)

1. **Hybrid, G-L4, g-00000 with g-11111, seed 1.** Together all 156 weeks. Member A is classed held at 3 of the first 5 readings, and B at all 5. From about week 40, A carries non-offsettable suffering of 0.5 for a hundred weeks, while pleasure stays 0.85 to 0.95 on the curve. A's outside option falls (0.84 to 0.47 by week 52), so later readings read "worth". This matches the held/suffering split above. It is the hybrid's pleasure-only yardstick at work, not a bug.
2. **v2b, G-L0 against G-W4, g-01011 with p-anchor, seed 2.** Described under "Withdrawal" above. Without pressure, A leaves after week 39 and B falls to about 0.5. With withdrawal, A is held at two readings, then stays as "worth", and both live at about 0.95. Matches the numbers.
3. **v2, G-L4, g-10011 with g-10111, seed 2.** Pressure forms a household that would not have formed. A is held at weeks 13 and 26. Suffering climbs with the bills, B leaves at week 49 and A at 63, and both then live apart paying stigma and exit stigma (−0.08 to −0.16 a week), at 0.6 to 0.7. This is v2's harm: pushed in, broken, charged for being apart.

No mismatch with the numbers was found. The second story is the finding.

## The known-answer cases (from the amendment, run before)

The stay test's built trap separates under v1, v2 and v2b (held 0.82, 0.73, 0.70 against 0). It does not separate under the hybrid (0 against 0): the imposed fixture never asks the hybrid to leave, so the hybrid's held share is reported with "known answer only partly met". A supplementary check of the lens itself (an exit-stigma wall, formation forced) read 0 without pressure and above 0 with it under v2, v2b and the hybrid.

## Is the hybrid ready to be the default for H41 and the many-agent world?

**For H41, yes, with one condition.** It passes both pass tests with the time-together fix, and its big-choice forecasts match held-out futures (H1 −0.00002). Its households form like v1's and last (7% end). In this run it lands where the exact model puts it, in sign and in size (+0.011 against +0.011). The condition: its yardstick ignores suffering by declaration, and this run shows that matters. Held members suffer three times as much, and one member stayed through two years of non-offsettable suffering. H41 counts pressure as domination, so that is visible there; it should be reported beside every hybrid result, not discovered later.

**For the many-agent world, not yet.** Two things have to come first:
- **Wire in its readings.** The hybrid leaves and returns only through the harness's readings. In a world that does not run them, it never leaves; the trap fixture showed exactly that.
- **Measure its cost.** It costs about 34 s a run here, liberty included, against about 5 s for the other sets. That will not scale to many agents without a cost probe first.

## Misses and weaknesses, plainly

- **Expected, written before the run: "P1 holds under every set."** It held as a sign, not at its bar: v1 and the hybrid are at 0.06 and 0.05, below 0.10.
- **Expected: "P4 holds under v1 and is unclear under the others."** v1 yes. v2 and the hybrid are 0. v2b is the opposite sign, which "unclear" did not cover.
- **The hybrid's known answer is only partly met** (above).
- **The satiety fix passes narrowly** (time together's gap +0.013 against a bar of 0.015). The remainder is mostly sessions the partner would have held anyway.
- **Liberty with powers moves through state, not cards.** "Narrows liberty" here means "more people in households, where options are fewer". That is a real loss of options, but it is not the norm changing the rules.
- **One world, one knee, the H38 persona sample.** The 0.007 margin was set on the clipped scale and carried over unchanged.
- **The exact model's placement reads formation shares from the capped-scale chooser** as an approximation, as the prereg said.

## Can be about / cannot be about

This can be about whether H38's pairing pressure holds people in, narrows liberty and changes modeled pleasure, in the formation check's household with bills that hurt on the saturating scale, under four scripted agent sets, and whether those answers agree across the sets. It cannot be about romance, partner choice or people (limit 1), or about agent sets outside the four.

## Reproduction

`uv run python scripts/formation_check_3.py --reach` (about 8 minutes), `--run` (about 5 hours on 4 workers), `--analyze` (writes runs/formation-check-3/analysis.json). Tests: `uv run pytest tests/test_satiety_expect.py -m ""`.
