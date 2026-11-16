# TT2: gifts between partners living apart, and the sourced value of a background hour (preregistration)

Wording rule: agents feel nothing; "pleasure", "suffering", "gift", "value", "forecast" and "held" are glosses for modeled numbers (ADR 0010).

Status: written and committed before any code for the gift flag and before any run of TT2. Nothing here is a result. Scripted agents (the hybrid), no model calls, no paid API runs. One world change (gifts) and one number (q), together as one model version, so there is one rerun.

**The author's decisions, verbatim.** Gifts: "yes LAT partners should be able to give money". q: "Yes, use 0.3" (read-back rb-2026-11-16-bgvalue; [../notes/background-time-value.md](../notes/background-time-value.md): q = 0.3, range 0.05 to 0.6).

**Why.** [lat-suffering.md](lat-suffering.md) found LAT's extra non-offsettable suffering is all denied money: a member who loses its job while living apart has no shared pot to fall back on and sits at money 0. Not missing the partner, not two rents. Under TT it is +0.0003 [+0.0000, +0.0009] against B, in 2 pairings: 0.00011 of it in LAT weeks and 0.00019 in apart-not-LAT weeks (between LAT spells or after LAT ends), 0.00004 in households (runs/lat-suffering/tt.json). [time-together.md](time-together.md) found q sets the size of every time-together effect; TT used q = 0.1 (unsourced); the research note sources q = 0.3.

## Model line (ADR 0020)

- TT (previous): `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit · hybrid_tally=level · tally_half=13 · tally_line=0.02 · exit_grow=0.04 · hybrid_outside=lived · friend_satiety · fresh_return · together_bg=1.1 · lat_bg_keep=0.2 · lat_travel=0.33 · together_subst`, exit fallback F4 with items (F5 in the prenup and all-aids arms), corrected rule.
- **TT2 (new): TT with `together_bg=3.3` (q = 0.3) and `lat_gifts`.** `lat_gifts` is a new flag on `FixConfig`, default False; with it off every run is as before (pins).
- `together_bg` = 33 shared waking hours × q ÷ a 3-hour evening = 11 q. q = 0.05, 0.1, 0.3, 0.6 give 0.55, 1.1, 3.3, 6.6. The 33 hours and the 3-hour evening are TT's; nothing else in TT changes.

## The gift flag: how a gift is decided, from the model's existing logic

The model already has voluntary money giving. It is the `give` action (src/mar/worlds/household.py), built for seed v2:
- **Amount:** `GIVE` = 3 money units per gift, costing the giver one time unit (`V2_COST["give"] = 1`). Feasible only if the giver holds at least `GIVE + 1`.
- **Who proposes it:** the persona's gift policy (seed v2, ASSUMED there): a member with `prosocial ≥ 0.5` proposes a gift to the partner when the partner holds less than 4 and it holds at least 8. `prosocial` = 0.5 × (1 − giving_keeping) + 0.5 × togetherness, from the persona file (19 of the 38 personas are at or above 0.5).
- **Whether it is chosen (the hybrid):** `give` is one of the hybrid's propose-only actions (`hybrid.FORK_ACTS`). Its score is replaced by a one-week simulation in the lived world: the week replayed with the gift forced against idle, own net plus `prosocial` × the partner's net (`hybrid.rescore`). It is executed only if that value is above the action floor (0.003) and ranks first among feasible actions at that call. A member can give at most once per agent call (three calls a week), and the policy stops once the partner holds 4 or more, so in practice at most two gifts (6 units) a week to a partner at 0.
- **Today:** a gift to the partner needs both in the household (`feasible`), and the policy fires only when the partner is in the household and the card set carries a seed v2 aim (`mech`), which H41's baseline cards do not. So in H41 nobody ever gives; money help is only the pot's automatic safety net, and LAT has no pot.

**`lat_gifts` changes exactly two gates, and only under living apart together (`world.lat_on()`):** (1) a gift to the partner is feasible under LAT, not only when both are in the household; (2) a LAT member's propose list carries the same gift candidate under the same policy (prosocial ≥ 0.5, partner < 4, own ≥ 8). Under the hybrid the candidate's score is the fork value, as for every propose-only action; the policy's noise draw is not taken under the hybrid (its score is discarded there), so the random streams of a life where no gift is given do not move. Nothing else changes: the amount (3), the policy thresholds, the fork's yardstick and the prosocial share are the existing ones, chosen before any LAT result and not tuned here.

**Why this mechanism and not a pot.** The author's words are "able to give", a choice; the model's choice-of-giving mechanism is `give`. The pot's safety net is automatic and belongs to a shared home; copying it to LAT would make living apart a shared purse, which the author did not say. **Not covered by design:** pairs apart but not under LAT (between LAT spells, after LAT ends, after an exit): they are not a LAT couple in the model, so no gift. Under TT that is 0.00019 of LAT's 0.00033. Households are unchanged (the pot as before; no gifts since `mech` is off).

**Forecasts do not see gifts.** The hybrid makes no forks inside a forecast (a declared simplification of the hybrid: forecasts assume no request, refusal, veto, gift or take). So gifts change lived lives only: the week-0 choice, LAT take-up at a reading's forecast, and outside options are forecast without gifts. A reading after a gift sees a different lived state, so later choices can differ.

## Findings this could move (ADR 0020 rule 2)

- Row 59 (time together, TT) and row 54 (H41), row 57 (A6): LAT's trade-off (weeks together −, liberty +, pleasure 0), LAT's non-offsettable suffering (+ under A4–A6, 0 under TT), all aids (trade-off with a pleasure cost under TT), LAT take-up (24 of 120 under TT), B's formation at week 0 (0.95 under TT), H41 not supported.
- [lat-suffering.md](lat-suffering.md): "all of LAT's extra suffering is denied money with no shared pot".
- The pressure findings that TT moved (P2, P1's worse-off partner, better information, the prenup's suffering, the trial's formation, pressure's formation): rerun as part of the 11 arms.
- KO1 (outside forecast error; worse under TT), PT-R T3 (failed under TT), K1, KX2.
- Limit 11 (moving in looks costlier than it is) and "liberty falls whenever households get better" (a larger q makes households better).
- The many-agent spec's freeze (pending, not decided).

## Design

**Run settings.** Scripted agents, no model calls. At most **6 workers** (the author raised the cap from 4 to 6 on 2026-11-16, "Go to 6"), every queue under `caffeinate -s`, tasks ordered longest first (arms `all` and `info` before the others; a harness order change only, rows are keyed by arm and pairing). Rows in runs/tt2/ (git-ignored). Unit of resampling: the pairing (paired bootstrap, 2,000 resamples), as H41.

### Screening run (EXPLORATORY; no claims)

- **What:** TT2 on H41's pilot sample (`A.PILOT`: sample seed 900, 10 pairings, seed 900; 1 pairing overlaps the confirming sample), arms B, lat and all (30 lives), rows in runs/tt2/screen.jsonl; plus the new unit tests.
- **What I look at, and only this:** crashes; gift counts and the mode of the giver's week (gifts must happen only in LAT weeks); money conservation across each gift; week-0 terms against the same lives with gifts off (they must match, since forecasts see no gifts). No outcome (pleasure, liberty, suffering, take-up) is read, tabled or reported.
- **What it may change:** only a bug (code disagreeing with this text), fixed with an amendment and numbers before and after. Never a number, a threshold, the design below, or the predictions.

**The confirming design below is fixed now, before the screening run.**

### Confirming run (the only run that supports claims)

| Item | Configuration | Arms × pairings (seed 0, `A.CONFIRM`) | Lives |
|---|---|---|---|
| C1 TT2 | q = 0.3 + gifts | all 11 arms × 120 | 1,320 |
| C2 gifts alone | q = 0.1 + gifts (`tt2_q01`), against TT's rows | B, lat, all × 120 | 360 |
| C3 q sweep | q = 0.05 (`tt2_q005`), q = 0.6 (`tt2_q06`), gifts on | B, lat × 120 each | 480 |
| C4 LAT attribution | scripts/lat_suffering.py under `tt2` and `tt2_q01` | B, lat × 120 each | 480 |
| C5 checks | PIN, fast suite, KW, KG1–KG3 (units); KX2, K1, KL2, PT-H, PT-R under TT2; KO1 and KG4 from rows | | |

The q sweep's four points are q = 0.05, 0.1 (C2), 0.3 (C1) and 0.6, all with gifts on, all on the full 120 pairings (TT's sweeps used 60). q = 0.3 is the headline. TT's rows (runs/time-together/rows.jsonl) are reused as the TT side; nothing of TT is rerun.

**Decomposition.** TT → C2 changes gifts only (same q). C2 → C1 changes q only (same gifts). TT → C1 is the version change the stop rule reads.

## Known-answer checks

| ID | What | Passes iff | Where |
|---|---|---|---|
| PIN | Old results reproduce | `lat_gifts` off: all 50 slow pins byte for byte; fast suite passes | `uv run pytest -m slow`, `uv run pytest` |
| KG1 | The gift (unit) | flag off: a LAT member's gift to the partner is infeasible and never proposed. Flag on, LAT: feasible with money ≥ 4; proposed iff prosocial ≥ 0.5, partner < 4, own ≥ 8; executing it moves exactly 3 from giver to partner (total money unchanged) | tests/test_tt2_gifts.py |
| KG2 | Only under LAT (unit) | flag on, apart but not LAT: infeasible and not proposed; both in the household: the proposal rule is the old one (needs `mech`) | same |
| KG3 | Forecasts unchanged (unit) | a LAT world's `hybrid.forecast` values are equal exactly with the flag on and off | same |
| KG4 | Lived-only effect (run) | C2 against TT: the week-0 term matches in every pairing and arm; every C2 life with no gift executed has TT's outcomes (weeks together, formed0, liberty, pleasure, snon) exactly | `tt2.py --analyze` |
| KW | The suffering weight | w = 2 declines, w = 0 forms, with TT2's flags | tests/test_tt2_gifts.py |
| KB1, KB2, KT1, KS1, KF1, KR1, KT0–KT2, KC1, KO0, KL1, KX0, KX1 | earlier unit checks | fast suite passes (flags off, as each was written) | fast suite |
| KX2 | Pure exit cost | A5's clauses under TT2 (DiD > 0, interval above 0; formation not lower; in-future exits) | `hybrid_leaving.py --kx2 --flags tt2` |
| K1 | The trap | held share ≥ 0.10 in the trap, ≤ 0.02 in the baseline, TT2 flags | `hybrid_fix_check.py --trap --tt2` |
| KL2 | Story 4 | no stuck stretch over 26 weeks | `hybrid_leaving.py --story --version tt2` |
| PT-H | Forecasts against held-out futures | H1 within ±0.010 (interval inside ±0.015); H2 ≥ 0.80; H3 ≥ 80% | `hybrid_passtest.py --tt2` |
| PT-R | The routine at one week | T1–T4 no more than 0.02 below v2 on the same sample; T5 in 0.8–1.25; T6 holds | `value_consistency.py --hybrid --world --tt2 --run` |
| KO1 | Outside forecast accuracy | B arm: mean L − O over lived bar exits within ±0.02, interval inside ±0.04 (reported; failed under A6 and TT) | `tt2.py --analyze` |

PT-R T3 and KO1 failed under TT. **Expectation: both still fail** (nothing here touches the routine's projection or the outside futures; a larger q makes households worth more, which widened both under TT). They are reported, not fixed; diagnosing T3 is a separate task.

## Predictions and expectations (written before any run)

Classes are H41's: weeks together and formation margin 0.01; liberty 0.02; pleasure 0.003; suffering 0; interval clear of 0. Weeks together is reported, never judged a good.

| ID | Expected | Kind |
|---|---|---|
| G1 | Gifts are given in C1's and C2's LAT arms (at least one), and only in LAT weeks (none elsewhere) | expectation; the second clause is a property check |
| G2 | Gifts alone (C2 against TT, same pairings, LAT arm): LAT's extra non-offsettable suffering in **LAT weeks** (attribution, modes `lat_*`, against B) falls; the apart-not-LAT part is not touched by design and stays about as under TT, so the total LAT − B falls but **need not reach 0** | expectation (direction); size descriptive |
| G3 | TT2: LAT − B non-offsettable suffering class 0, mean at or below TT's +0.0003; whatever remains is denied money in apart-not-LAT or household weeks | expectation |
| G4 | Gifts alone do not change week-0 choices (KG4) | known answer |
| Q1 | TT2 against TT: fewer or as many pairs choose LAT at week 0 (TT 24 of 120), LAT weeks ≤ 0.053 | expectation (q up makes households worth more; TT's sweep went this way to q = 0.2) |
| Q2 | TT2 against TT: B forms at least as often at week 0 (TT 0.95); pleasure + and liberty − in every arm (a larger version of TT's level shift) | expectation |
| L1 | TT2, LAT against B: liberty +; pleasure 0 or −; weeks together − or 0 | expectation |
| L2 | TT2, LAT's verdict: trade-off (liberty up, pleasure interval below 0). A win is reachable if gifts and fewer LAT pairs lift LAT's pleasure interval off 0 | expectation, low confidence |
| L3 | TT2, all aids against B: liberty +, pleasure −: trade-off with a pleasure cost, as TT | expectation |
| H | H41 not supported under TT2 | expectation |
| S | q sweep (0.05, 0.1, 0.3, 0.6; B and LAT): sizes of LAT − B shrink as q rises; sign classes of liberty and pleasure keep TT's; weeks together may go to 0 at high q; suffering may be + at q = 0.05 | descriptive |

## Verdict rule

Pleasure AND freedom together (freedom: liberty with powers; held share where measured). **A win raises one without lowering the other. One up and one down is a trade-off, never a win.** "Lowering" pleasure here means the paired interval lies wholly below 0, even inside the 0.003 margin, as the H41 and TT write-ups read "costs a little pleasure"; H41's own verdict function is reported beside it. **Weeks together is not one of the two goods**: a rise in weeks together is a gain on neither.

**TT2 is usable as the time-together version** iff PIN, KG1–KG4, KW, KX2, K1, PT-H and PT-R pass. KO1 and KL2 are reported. If a check fails it is reported as failed and not patched. Since PT-R failed under TT and is expected to fail again, I expect TT2 not to be usable or ready to freeze; the results are still reported under that label, as TT's were.

**Stop rule (ADR 0020).** Per arm and key, the sign class against B under TT and under TT2 (and A6 where it was run). Same class: holds across versions. Different: version-dependent, named as such, **never patched**. A sign that differs across q in the sweep is labelled "fragile to q". Gifts alone (C2 against TT) and q alone (C1 against C2) are reported so a change can be traced to one of the two.

## Can every verdict happen?

- **G1, G2 can fail:** if no LAT member ever has a solvent prosocial partner when broke, or the fork values a gift at or below the floor, no gift is given and G2's change is 0. The screening run's gift count is the free check that gifts can happen at all (bug check only).
- **G3, L1, L2, L3:** H41's `--reach` synthetic checks reach win, trade-off, harm and no gain; the same functions are used.
- **KG4 can fail:** if the gift candidate's presence moved a random stream, or forks leaked into forecasts, week-0 terms or no-gift lives would differ.
- **The metric sees the mechanism:** a gift moves money between members inside the lived week; money sets the money need's level; a level under 0.15 with salience ≥ 0.12 for 4 weeks is denied non-offsettable suffering (`Hedonic.close_week`), which is `snon` in the rows and the attribution's `denied` by need and mode. The giver's loss lands in its own money need the same way.

## Are we measuring what we say?

- **Construct card.** Gift = 3 money units a LAT member chooses to hand its partner, when the partner is nearly broke and it is not, if the member's one-week simulation with its prosocial share says so. It does not encode pooling, loans, repayment, a standing allowance, gifts to a former partner, or the meaning of money between partners. q = the value of an hour of plain co-presence over an hour of a planned evening, from diary studies (weak overall, research note).
- **Known-answer cases:** KG1–KG4 (above). KG4 is the strongest: a gift-free life must be TT's life exactly.
- **One other way to measure it:** LAT's suffering as the total `snon` contrast and as the attribution by need and mode (C4); gift effect as C2 − TT and as the LAT-week attribution.
- **Story spot-check:** after the run, read two lives with gifts (one where a gift ended a denied-money stretch, one where a prosocial partner could have given and did not), one LAT pair's suffering in an apart-not-LAT stretch, and one B pair; say whether each matches the measures.

## Not testable by design

KG1, KG2, KG3, KW, the earlier unit checks and KG4 are deterministic and reported as pass or fail.

## Limits stated now

One persona sample (38 personas, 120 pairings, one seed); scripted agents; gift policy and amount ASSUMED (seed v2's), reused not sourced; forecasts do not see gifts (a hybrid simplification), so gifts cannot make LAT more attractive at a choice; apart-not-LAT pairs get no gifts; q sourced weakly (research note); limits 1, 4, 5, 6, 10, 11, 12, 13 apply ([limits.md](../limits.md)). Can be about: how H41's LAT result, its suffering and the hybrid's checks move when LAT partners can hand each other money by the model's existing gift rule and a background hour is valued at the sourced 0.3. Cannot be about real couples, their money, job loss, or the many-agent world.

## Amendments

None yet.
