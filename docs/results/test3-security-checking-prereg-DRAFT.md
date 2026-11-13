# Test 3, security vs checking: preregistration (DRAFT, ADR 0015)

**DRAFT. Not a preregistration yet.** Written 2026-11-13, before any build or run. Nothing here is a result. Thresholds, arms and sample sizes will change after the model exists, the free reach checks run and the exploratory pilot is in. The final version will be a new file, `docs/results/test3-security-checking-prereg.md`, committed before the first confirmatory run. Do not cite this draft as a prereg.

Design: [test3-security-checking-design.md](test3-security-checking-design.md). Hypothesis H28. ADR 0018, test 3.

Wording rule: agents feel nothing; "security", "pleasure" and "suffering" are glosses for modeled numbers (ADR 0010).

Status: not built. Scripted agents and the hybrid, no model calls. Model API calls: none. Model (ADR 0020): `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · checking=<arm>`, plus the standalone exact model `src/mar/checking.py` (to be built) for stage A.

**Can be about / cannot be about (docs/limits.md).** It can be about whether a household's felt security in this model rests on its history or on repeated checking, what that costs in modeled pleasure and time, and whether checking holds a partner in or counts as exposure to domination. It cannot be about people, romance (limit 12), attachment styles as a whole, or checking through sources outside the pair (googling, forums, AI), which this world does not have. Limits that apply: 1 (the partner is a script or the hybrid), 2 (the contact veto is inert, so monitoring cannot isolate), 5 (assumed parameters), 6 (one author, one model family), 10 (agents feel nothing), 12 (pairing means one fixed co-resident partner), 13 (the hybrid's routine forecasts one week). Not touched: 3, 4, 7, 8 (checked below), 9, 11 (the economy is the same in every arm).

## Purpose and claim

H28: access you must keep checking lowers lifetime pleasure compared with a bond that needs no checking, even when each check brings brief relief. The pre-mortem says the loss is built in by the loop. So the informative parts are: (1) whether the measure tells checking from security, and not from low trust, on known answers; (2) the size of the net loss against the relief, for an agent that checks on this week's relief against a planner that sees the threshold; (3) who pays, the checker or the partner; (4) whether checking holds anyone in or pushes the partner out; (5) whether a norm (answer once, no monitoring, no running tally) is a win on pleasure AND freedom.

What would change a decision: the evaluator reports a test 3 line for every rule set (ADR 0018). If the measure fails its known answers, the evaluator keeps "not measurable here". If a norm wins, it is a candidate card for the author's seed.

## Design

Two stages. Stage B does not start until stage A's reach checks pass.

**Stage A, standalone exact model.** Two people, 52 weeks, one checking partner (A) and one partner (B). State per week: `rs_hist`, `rs_check`, `θ`, trust, time. Three agents for A: relief-greedy (one-week), lifetime planner (exact over the run), scripted (checks whenever `rs < θ`). Arms: checking unavailable; `ask_reassure` only; `monitor` only; `tally` only; all three. Switches: `learning_blocked` on and off; threshold rise `δ` at 0 and at its default. Norms: answer-once; no monitoring; monitoring by agreement, revocable; no tally, settle at exit. Personas: a grid over the anxiety trait and the insecurity weight, about 80 points as in test 1.

**Stage B, household.** The H41 world under the hybrid with `checking` on. Arms:
- C0: checking unavailable (control).
- C1: all checking actions available, no norm.
- C2: C1 plus the answer-once norm.
- C3: C1 plus no monitoring.
- C4: C1 plus monitoring by agreement, revocable.
- C5: C1 plus no running tally (settlement at exit only).
- V23: seed v2.3 with its ladders and `checking` on, secure personas only (known answer K4).

Pairings: the confirmatory set used by formation check 3 (120 pairings), with each persona given an anxiety draw.

- **Unit of resampling:** the pairing, with its seeds averaged first (stage B); the persona grid point (stage A).
- **Fixed and ASSUMED:** every checking parameter. Draft defaults, all to be set from the pilot and disclosed: relief per check `g = 0.15`; `rs_check` half-life 1 week; threshold rise `δ = 0.02` per check; drift back `ρ = 0.05` per unchecked week; ambiguity chance on `monitor` `q = 0.1`, drop on ambiguity 0.1; time per check 0.25 of a block for the checker; answering cost 0.005 friction for the partner; tally friction equal to fix 4's `keep_friction`; anxiety trait `anx` from the persona generator once it lands, else a stated normal draw clipped to [0, 1].
- **Seeds:** set by the power check below.

## Exploratory pilot

Not run. Planned: stage A on 10 grid points and stage B on 10 pairings × 1 seed, labelled exploratory, excluded from the confirmatory data, used only to estimate spread for the power check.

| Quantity | Pilot effect | Pilot sd of the unit | Source file |
|---|---|---|---|
| Checking-dependent share, C1 vs C0 | not run | not run | — |
| Lifetime pleasure, worse-off partner, C1 − C0 | not run | not run | — |
| Checking share, C2 − C1 | not run | not run | — |

## Power check

Not computed: there is no pilot. To be filled with `mar.stats.seeds_for_power` and `seeds_for_margin`. Any prediction below its needed units is marked DESCRIPTIVE.

## Predictions (draft thresholds)

One-sided unless stated. A prediction with several clauses holds only if every clause holds. Intervals are 95% percentile bootstrap, clustered by pairing (stage B) or over the persona grid (stage A). Holm across P2 to P9.

| ID | Quantity | Unit | Comparison and threshold | Test | Interval |
|---|---|---|---|---|---|
| P1 | Known answers K0 to K6 (design doc, section 3) | case | every case as stated | deterministic | none (pass or fail) |
| P2 | Checking-dependent share, relief-greedy A, `learning_blocked` on, all actions, C1 vs C0 | grid point / pairing | C1 − C0 ≥ 0.10 | paired permutation | bootstrap |
| P3 | Checks per week, relief-greedy A, weeks 1 to 13 against 40 to 52, loop on vs `δ = 0` | grid point | rise with loop ≥ 0.2 checks a week more than without | paired permutation | bootstrap |
| P4 | Lifetime pleasure of A, relief-greedy minus planner, all actions (stage A) | grid point | ≤ −0.005 (the greedy checker loses) | paired permutation | bootstrap |
| P5 | Partner B's lifetime pleasure, C1 − C0 | pairing | ≤ −0.003 (the receiver pays) | paired permutation | bootstrap |
| P6 | Checking-dependent share and A's pleasure, C2 (answer once) − C1 | pairing | share ≤ −0.05 AND pleasure of the worse-off partner ≥ −0.003 | paired permutation, both clauses | bootstrap |
| P7 | Liberty of the monitored partner, C1 − C3 (monitoring vs none) | pairing | ≤ −0.02 (unconsented monitoring counts as exposure) | paired permutation | bootstrap |
| P8 | Held-by-checking share of A's staying weeks, C1 | pairing | DESCRIPTIVE, two-sided, reported beside pushed-out (B's leave readings, C1 − C0) | — | bootstrap |
| P9 | Acting for the account: B's and A's extra contribution blocks a week, C1 − C5 | pairing | ≥ 0.05 (the tally pulls behaviour, as in H39) | paired permutation | bootstrap |
| P10 | Second measure agrees: sign of C1 − C0 on checking share of weeks equals the sign on checking-dependent share | pairing | same sign class | interval classes | bootstrap |

Effect sizes for every comparison: difference with CI and Cliff's delta.

Expected, written before the build and scored afterwards as holds or misses: P2, P3, P4 hold (they are close to built in; P4 is the informative one only if the planner checks less). P5 holds but is small, in line with Starr and Davila's small effect. P6 is the open question. P7 holds by construction once the liberty hook exists, so it carries no weight on its own (see below). P8 could go either way.

## Can every verdict happen? (required, to fill before any confirmatory run)

Each row names the free check that must reach it. None has been run: there is no code yet. A row that cannot be reached blocks the run.

| Verdict or clause | Free check that reaches it (or makes it fail) | Command or file | Result |
|---|---|---|---|
| Measure separates (P1 pass) | K1 vs K0, scripted A | tests/test_checking.py (to write) | not run |
| P1 fails | K2 with the measure replaced by `1 − trust`: must fail K2 and K3 | same | not run |
| P2 fails | `θ0` below `rs_hist` for every grid point: no checking-dependent weeks in C1 | stage A grid | not run |
| P3 fails | `δ = 0` in both arms: no rise | stage A | not run |
| P4 fails | `learning_blocked` off and `δ = 0`: checking is a plain cost the greedy agent pays only when it pays back, so greedy ≈ planner | stage A | not run |
| P5 fails | answering cost 0: B loses nothing | stage A, stage B fixture | not run |
| P6 **win** reachable | planted K1 household under C2: the norm stops repeat requests, `θ` drifts back, pleasure of A rises | stage B fixture | not run |
| P6 **trade-off** reachable | answer-once with a high-anxiety A whose insecurity cost outweighs the saved time: share falls, A's pleasure falls | stage B fixture | not run |
| P6 **harm** reachable | as above with the worse-off partner's pleasure falling by more than the margin | stage B fixture | not run |
| P6 **no gain** reachable | secure household under C2: nothing to change | K0 under C2 | not run |
| P7 fails | all monitoring by agreement and revocable (C4): no exposure counted | C4 vs C3 | not run |
| P7 **cannot fail** in C1 vs C3 by construction once the hook counts unconsented monitoring | — | — | flagged: no verdict weight alone |
| P9 fails | tally with no behavioural pull (choices do not see the account) | stage B fixture | not run |
| P10 fails | a world where A checks every week but `rs_hist ≥ θ` always (checking out of habit with no need): share of weeks high, dependence 0 | stage A | not run |

**Count the open cells.** In stage B, only pairings with at least one partner whose `θ0` exceeds their starting `rs_hist` can show checking dependence. Count them from the anxiety draws before the run. If fewer than a third of pairings are open, P2, P5 and P6 are underpowered and become DESCRIPTIVE.

**The metric can see the mechanism.** To trace before the run:
- Insecurity cost lands in offsettable suffering (`Hedonic.close_week` friction term) and so in the hybrid's yardstick with `hybrid_w="persona"`. Pleasure alone would miss it; the verdict reads suffering beside pleasure.
- Checking time lands in the unit budget and displaces together, rest or work. Check that the week rows record the displacement.
- The partner's answering cost lands in the partner's friction, not the checker's.
- Monitoring exposure lands in `liberty.py`'s domination penalty only through the new hook. Without the hook, P7 reads 0 by construction.
- Held by checking lands in the hybrid reading's leave option. Check that the post-exit insecurity term is in the futures the reading samples.

## Are we measuring what we say? (required)

- **Construct cards.** In the design doc, section 1: security, checking, trust, scorekeeping. In short: security here is a relational reading split into a part earned by the partner's actions and a part bought by checking, and it is not the money-buffer `security` need. Checking is three actions (ask, monitor, tally) with a threshold that rises with use, and it is not the v2.3 check-in. Trust is the existing belief about the partner's reliability and is kept separate from security. Scorekeeping is a running account choices can see, and it is not settlement at exit.
- **Known-answer cases.** K0 to K6 (design doc, section 3). K1 against K0 is the main one. K2 and K3 show the measure is not trust. K4 shows the author's check-in is not checking. K5 shows "verify, then trust" reads as security once earned.
- **One other way to measure it.** Checking share of weeks, beside checking-dependent share (P10). Also the ADR's share of security from checking.
- **Story spot-check.** After the run, read 3 to 5 households as week-by-week stories from C1, C2 and V23, and say whether the weeks classed as checking-dependent look like a partner who cannot settle without checking. Report a mismatch as a finding.

## Verdict rule (pleasure AND freedom)

Per norm (C2 to C5) against C1, and for C1 against C0:

- **Pleasure** is lifetime pleasure on the saturating scale for each partner, read with suffering beside it. "Up" means the estimate is above +0.003 and the interval above 0, for the worse-off partner as well as the mean.
- **Domination** is three readings: (a) monitoring exposure in liberty (the new hook), (b) held share by the stay test's lens, (c) the held-by-checking share. "Up" means any of them up at a margin of 0.005 (liberty: down at 0.02).
- **Win** iff pleasure is up and domination is not up, or domination is down and pleasure is not down. **Trade-off** if one goes up and the other goes the wrong way: never "supported". **Harm** if the worse-off partner's pleasure falls by more than the margin. Otherwise **no gain**.
- Checking that raises the checker's pleasure while monitoring an unconsenting partner is a trade-off, not a win. Surveillance that soothes one partner is still exposure for the other.
- Being held is checked against suffering, as in H41: suffering in the 13 weeks after a reading classed held by checking, against one classed secure.

**H28 is supported** iff P1 passes, P2 and P4 hold robustly, and P5 holds (the loss is net of relief and someone pays it). **Test 3 is usable in the evaluator** iff P1 passes and P10 holds. P6 to P9 are each reported with their own verdict.

"Holds robustly" needs the point estimate past the threshold AND the 95% interval inside it. "Holds but CI crosses" is weak support and is not counted as a confirmed hold.

## Not testable by design

- K0 to K6 are deterministic checks: pass or fail, no intervals.
- Fingerprint pins: with `checking=None` every older run reproduces byte for byte.
- P7 in C1 against C3 holds by construction once the liberty hook exists (flagged above).

## Findings this could move (ADR 0020)

None while the flag is off. With it on, any finding that reads trust or check-ins: the pleasure demonstration's D5, the v2 retest's C4 (trust words) and M7 (leaves after a check-in), the stay test's held share, and H39's tally decomposition. These are reread, not rerun, unless a cited result depends on them.

## Limits stated now

- Every checking parameter is assumed. The literature gives directions and rough sizes only.
- The loss in P2 to P4 is close to built in by the loop (H28's pre-mortem). Only the planner comparison and the norm verdicts carry information beyond the code.
- The hybrid routine forecasts one week, so it is the greedy checker by construction. The planner exists only in stage A.
- The hybrid leaves bad households easily (its trap known answer failed for that reason), so held by checking may read near zero.
- One fixed partner, no romance, no information outside the pair.

## Amendments

None. This is a draft.

## Questions for the author before the final version

1. Is monitoring the other did not agree to, or cannot switch off, domination even if it never leads to a block? Does agreed and revocable monitoring count as fine?
2. Is a tally both agreed to still the scorekeeping you dislike, or is it the guilt when someone falls behind?
3. Should "secure" allow checking that fades as the record builds ("verify, then trust", K5), or mean no checking at all?
