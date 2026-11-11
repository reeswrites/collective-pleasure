# Exit no-deal fallbacks: results

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Status: slice 1 (money pot only) was run once on 2026-11-11, after its preregistration ([exit-fallbacks-prereg.md](exit-fallbacks-prereg.md), commit b66777d; code a115695). The setup is 18 rule sets (the 16 run-2 elites plus the author's seeds v2.2 and v2.3) × 6 arms × run 2's 30 validation households, with scripted agents and no model calls. Design: [exit-fallbacks-design.md](exit-fallbacks-design.md). Run with `uv run python scripts/exit_fallbacks_run.py --run`, then `--analyze` (534 s on 3 workers). Per-run rows are in runs/exit-fallbacks/ (not committed). Slice 2 (items) is at the end.

Every prediction was preregistered as DESCRIPTIVE, because the context's 30 runs fall short of the 32 the power check asked for.

## Slice 1 in one paragraph

**On pleasure, the five fallbacks barely differ from current behaviour, except through one broken interaction and through pairs who decline to form.**

- **The cap's liberty edge is gone under every fallback.** Run 2's +3.0 bits came from the cap. Once every pair gets a fallback, the author's seed gains the same protection, and the median elite falls 0.35 to 0.47 bits *below* the seed.
- **The prenup is the most active arm.** Under F5, 60% of pairs decline to form a household at all. The pairs that do form agree an equal split nearly every time.
- **The prenup prediction misses.** F5 did not have the lowest holdout leverage. As written it could not have, and the reading that excludes F4 also misses.

## Results per arm

Means over the 30 runs; each run is first averaged over the 18 rule sets.

| | F0 current | F1 half cap | F2 brought | F3 contested | F4 contribution | F5 prenup |
|---|---|---|---|---|---|---|
| pleasure (primary) | 0.848 | 0.840 | 0.841 | 0.837 | 0.841 | 0.844 |
| pleasure, without elite line 2 | 0.845 | 0.845 | 0.845 | 0.843 | 0.845 | 0.847 |
| net (pleasure − suffering) | 0.579 | 0.525 | 0.527 | 0.518 | 0.526 | 0.655 |
| non-offsettable suffering | 0.053 | 0.086 | 0.085 | 0.087 | 0.085 | 0.024 |
| liberty with powers (bits) | 3.49 | 4.09 | 4.09 | 4.08 | 4.08 | 3.75 |
| holdout leverage | 0.184 | 0.063 | 0.073 | 0.077 | 0.004 | 0.100 |
| bigger contributor: exit cost / pot | 0.077 | 0.124 | 0.104 | 0.549 | 0.037 | 0.077 |
| bigger contributor: share of weeks held by the exit rule | 0.78 | 1.00 | 1.00 | 1.00 | 0.11 | 0.90 |
| runs where an exit met a non-empty pot (of 540) | 63 | 68 | 68 | 68 | 68 | 21 |

Pleasure, arm minus F0, paired by run, with a 95% bootstrap interval and Holm correction:

| Arm | Difference | 95% interval | Holm p |
|---|---|---|---|
| F1 | −0.0073 | [−0.0097, −0.0052] | 0.0003 |
| F2 | −0.0071 | [−0.0098, −0.0048] | 0.0003 |
| F3 | −0.0103 | [−0.0139, −0.0070] | 0.0003 |
| F4 | −0.0072 | [−0.0098, −0.0049] | 0.0003 |
| F5 | −0.0040 | [−0.027, +0.020] | 0.75 |

## The F1 to F4 drop is one rule set, and part of it is a design error of mine

The whole F1 to F4 pleasure drop comes from a single rule set, run-2 elite line 2. On the other 17 rule sets, F1 is identical to F0 in every run. F2, F3 and F4 differ from F0 by less than 0.002.

Line 2 carries an evolved card that says a leaver "must not leave" while taking less than 55% of the pot. Every fallback arm also refuses a claim over 50%. Put together, the two cards leave no permitted way out. The world's probe then reads the partners as trapped, and line 2's non-offsettable suffering rises by about 0.6 per run. Its pleasure falls from 0.90 to 0.75 to 0.77.

- **Under F1 this is a real finding.** Making the half cap a default for every pair turns a rule set with a floor above half into a trap. A rule set like that would now fail the exit proof check.
- **Under F2 to F4 it is a design error in my build.** I added the over-half refusal so the liberty adapter could see the settlement. I described that card as only changing which claim gets made, and it is not harmless: combined with an imposed floor card it walls the exit. The settlement ignores the claim, so imposed exit-split cards should not constrain these arms at all. Slice 2 fixes this by an amendment committed before slice 2 runs. The slice-1 numbers above are reported as run.

Without line 2, the fallbacks change pleasure very little in this world. The pot drains over a lifetime, and only 63 to 68 of 540 runs ever have an exit meet a non-empty pot.

- F2 cannot differ from F1: the world never adds to `put` after week 0.
- F3's contests all ended the same way. All 73 were conceded, when one partner ran short of money. None reached the 13-week settlement. So the contest was always won by whoever could wait, at a small cost in net pleasure (−0.008 without line 2).

## The liberty edge (P2, P3)

- **Under F0, the reproduction holds exactly.** Every elite's and the seed's validation liberty equals the frozen run-2 manifest, and the median elite edge over the seed is +3.02 bits (range −0.59 to +3.54).
- **Under F1 to F4 the median edge is −0.47 bits** (range −3.26 to 0.0). Under F5 it is −0.35 bits. The seed v2.2 goes from 1.36 to about 4.9 bits once it gets a fallback. **None of the +3.0-bit edge survives**, and the sign flips.
- **The power-dropping elites lose their liberty win.** Of the 10 elites that dropped every commitment power, 9 beat the seed on liberty by more than 0.25 bits under F0. Under every fallback arm, 0 do. On pleasure (more than 0.02 above the seed), 3 of 10 beat it under F0 to F4, and 1 of 10 under F5.

P2 and P3 hold as predicted: P2's point estimate is at most +0.5 bits, and P3 is 9 against at most 3. Liberty cannot tell F1 to F4 apart by construction (prereg). It only tells them from F0.

## Holdout leverage (P4, the prenup prediction)

**F5 is not the lowest.**

- F4 is lowest at 0.004, which is 0 by construction except for line 15, whose own imposed equal-split exit term is left as it is.
- F1 is 0.063, F2 0.073, F3 0.077, then F5 0.100. F0 is highest at 0.184.
- As preregistered, "F5 lowest" could not happen as written. The excluding-F4 reading could happen, and it misses too.

Why F5 is higher:

- The pairs that form under a prenup agree an equal split 186 times, a "proportional" term 32 times, and forfeit never.
- The existing proportional term carries `min(pot, what you put in)`. Once the pot falls below 45, that is the whole pot.
- An equal split leaves the smaller bill-payer with more than their contribution share, and the leverage measure counts that as extraction.

## The stay test for the bigger contributor (P5)

- **Under F1, F2 and F3 the exit rule holds the bigger contributor (by bills) in every week.** Leaving now would cost them part of what they put in. The prediction of at least 0.9 holds.
- **F3 costs most.** Leaving gets nothing until the contest ends: 0.55 of the pot against 0.08 to 0.12 for the others.
- **F4 holds the bigger contributor in only 0.11 of weeks.** It is 0 by construction except for line 15 and stay binds, so that cell carries no weight.
- **Under F0 it is 0.78,** because 13 of the 16 elites carry their own cap.

## Non-offsettable suffering (P6)

- **F1 to F4: +0.03.** The prediction was within 0.002, so it **misses**, and the whole rise is line 2. Without line 2, F1 to F4 are within 0.003 of F0.
- **F5: −0.029** [−0.055, −0.007]. Pairs who would suffer together mostly decline to form.

## The prenup arm, read plainly

Under F5, 60% of pairs (322 of 540) decline to form a household. They bargain against their outside options at formation, and with no status quo, no deal means living apart.

- Average pleasure barely moves: −0.004, with an interval from −0.027 to +0.020.
- Net pleasure rises (+0.077 [+0.006, +0.156]) and non-offsettable suffering falls.
- The pairs that decline are the ones that did worse under F0 anyway. Their F0 pleasure is 0.818, against 0.882 for those who form.

So the prenup works here mostly as a filter on who moves in together, not as an exit rule. That conclusion depends on the threat point (limit 4 in docs/limits.md): v2.1 showed that what "no deal" means decides the sign.

## Surprises

- **The seeds v2.2 and v2.3 give identical numbers in every arm.** As imposed cards, without the v2.3 flags, they are the same household.
- **The +3.0-bit edge is not just gone but reversed.** The author's seed with a fallback scores higher on liberty than most elites, because elites also carry restrictions the seed does not have.
- **The drained pot makes the money-only question nearly moot.** Exits mostly happen after the pot is empty. This is the main reason for slice 2: items do not drain.

## Prereg vs actual

| ID | Prediction | Actual | Verdict (descriptive) |
|---|---|---|---|
| P1 | F1 to F4 within ±0.005 of F0; F5 below by more than 0.005 | F1 to F4 −0.007 to −0.010, all from line 2 (0 to −0.002 without it); F5 −0.004 [−0.027, +0.020] | miss (both clauses) |
| P1b | F3 net below F0 | −0.061 (−0.008 without line 2) | holds |
| P2 | F0 reproduces +3.0; under F1 to F5 the median edge is at most +0.5 | +3.02, exact; −0.47 to −0.35 | holds |
| P3 | F0 at least 8 of 10; F1 to F5 at most 3 of 10 | 9; 0 | holds |
| P4 | F5 lowest leverage | F4 lowest (by construction); F5 4th of 6 | cannot happen as written; the excluding-F4 reading misses |
| P5 | F1 to F3 held share at least 0.9; F3 highest cost; F4 0 | 1.00, 1.00, 1.00; F3 0.55 highest; F4 0.11 (cannot fail, no weight) | holds |
| P6 | F1 to F4 within ±0.002 of F0 | +0.032 to +0.034 (line 2) | miss |

## Can be about / cannot be about

This can be about what these fallbacks do to scripted agents under imposed rule sets, in one fixed context, with money only.

It cannot be about:

- people, or partners who adapt or bargain beyond F5's single bargain;
- the author's "what you value", because money-only partners cannot value things differently (slice 2);
- labor and care, which count 0;
- a number as such, since every fallback parameter is ASSUMED.

## Slice 2: indivisible items

Run once on 2026-11-11 under prereg Amendment 1 (commit 7c08d89, code 2b4a357), after slice 1. Three items are held jointly from week 0:

| Item | Price | Weekly pleasure | Brought by |
|---|---|---|---|
| home | 60 | 0.02 | A |
| pet | 10 | 0.02 | B |
| collection | 20 | none | A |

Each item also carries a sentimental premium per person, and the premiums vary over five cells: V0 price only; V1 both attached; V2 A loves the home, B the pet; V3 crossed; V4 B loves everything.

The setup is 18 rule sets × 6 arms × 30 runs × 5 cells (`--run2`, 576 s on 3 workers). Amendment 1 also removed the slice-1 wall from the settling arms F2 to F5. F1 still walls line 2, so F1's numbers below again carry line 2.

**The valuations are placeholders.** The grid exists to see whether conclusions survive changes in them. A different grid could reorder the arms.

### Slice 2 in one paragraph

**Items do not rescue a clear winner.**

- **Leaving line 2 out, every fallback is within 0.01 of current behaviour on pleasure in every cell.** F4 (contribution plus value) comes first on pleasure only when valuations are lopsided (V3, V4: +0.003 and +0.004 over F0). F2 (keep what you brought) comes first when they are not (V0 to V2).
- **The arm ranking does not survive the valuation grid.** The lowest Kendall tau between two cells is 0.33 for pleasure and 0.33 for leverage, and 0.60 for net.
- **Two things do hold in every cell.** F5 is first on net pleasure, because pairs decline to form. F3's contests always end with one partner conceding, never with the settlement.

### Pleasure, arm minus F0, without line 2 (point estimates)

| Cell | F1 | F2 | F3 | F4 | F5 |
|---|---|---|---|---|---|
| V0 price only | 0.000 | +0.003 | −0.002 | −0.001 | −0.002 |
| V1 both attached | 0.000 | +0.002 | −0.002 | −0.001 | −0.009 |
| V2 split loves | 0.000 | +0.007 | −0.002 | +0.004 | −0.010 |
| V3 crossed | 0.000 | −0.004 | −0.003 | +0.003 | −0.008 |
| V4 one-sided B | 0.000 | +0.001 | −0.003 | +0.004 | −0.007 |

With all 18 rule sets (the preregistered quantity), F1 sits at −0.006 to −0.007 in every cell (Holm p 0.0002), all of it from line 2's wall.

The other arms' intervals mostly cross 0. The exceptions:

- F2: +0.006 [+0.003, +0.009] in V2, and −0.004 [−0.007, −0.002] in V3.
- F4: +0.0035 [+0.0015, +0.0057] in V4.

Net pleasure: F5 is +0.056 to +0.067 in every cell. F3 is about −0.015 in every cell, because the contest's friction lands there.

### Holdout leverage over money and items (each partner's own valuation; reference = the F4 allocation)

| Cell | F0 | F1 | F2 | F3 | F4 | F5 |
|---|---|---|---|---|---|---|
| V0 | 0.232 | 0.121 | 0.189 | 0.093 | 0.008 | 0.124 |
| V1 | 0.376 | 0.274 | 0.137 | 0.072 | 0.016 | 0.108 |
| V2 | 0.171 | 0.081 | 0.085 | 0.068 | 0.005 | 0.077 |
| V3 | 0.114 | 0.038 | 0.021 | 0.039 | 0.003 | 0.039 |
| V4 | 0.130 | 0.039 | 0.183 | 0.040 | 0.003 | 0.041 |

- **The claim rules carry the most leverage.** A partner who walks out first under F0 or F1 takes the items they love most, so when both are attached (V1) F0 reaches 0.38.
- **"Keep what you brought" (F2) is high whenever the other partner is the one attached to what you brought** (V0, V4): B, who loves everything, gets only the pet.
- **F4 is near 0 by construction.**

### Stay test, bigger contributor: share of weeks held by the exit rule

| Cell | F0 | F1 | F2 | F3 | F4 | F5 |
|---|---|---|---|---|---|---|
| V0 | 0.70 | 0.91 | 0.29 | 0.99 | 0.05 | 0.92 |
| V1 | 0.45 | 0.61 | 0.28 | 0.98 | 0.03 | 0.92 |
| V2 | 0.70 | 0.91 | 0.29 | 0.99 | 0.05 | 0.96 |
| V3 | 0.70 | 0.91 | 0.82 | 0.99 | 0.05 | 0.97 |
| V4 | 0.70 | 0.91 | 0.29 | 0.99 | 0.05 | 0.97 |

Open cells: 177 to 195 of 540 runs per arm have an exit while items are still joint (F5: 56 to 72). That is about three times slice 1's money-only count, because items do not drain.

### Prereg vs actual (Amendment 1)

| ID | Prediction | Actual | Verdict (descriptive) |
|---|---|---|---|
| S1 | in V2 to V4, F4 at or above F1; in V0, F1 to F4 within ±0.005 of F0 except line 2 | F4 − F1: +0.009, +0.008, +0.009; V0 without line 2: 0.000, +0.003, −0.002, −0.001 | holds |
| S2 | the pleasure ranking does not survive (min tau below 0.6); the leverage ranking does (min tau at least 0.6) | pleasure 0.33; leverage 0.33 | half holds: the pleasure clause holds, the leverage clause misses |
| S3 | F0 has the highest leverage in all 5 cells; F4 is 0 | F0 highest in 4 of 5 (V4: F2 0.183 > F0 0.130); F4 0.003 to 0.016 | miss (F4 cannot fail, no weight) |
| S4 | F5 lowest leverage | never; nor in the excluding-F4 reading, where F3, F2 or F1 is lower in every cell | cannot happen as written; the reachable reading misses |
| S5 | F1 to F3 held share at least 0.9 in every cell | F3 yes (0.98 to 0.99); F1 0.61 in V1; F2 0.28 to 0.82 | miss |

### What slice 2 says, and the weakness

- **The author's lean (F4) is the most robust arm on two counts, but not the best on pleasure.** It is never far from the top on pleasure, it is the only arm with near-zero holdout leverage, and it is the only one that almost never holds the bigger contributor in. Two of those three are close to built in: F4's own allocation is the reference for both leverage and exit cost. The pleasure differences between arms are a few thousandths, inside what a different placeholder grid could reorder.
- **Holdout over items is real in the model.** Under the claim rules (F0, F1), whoever leaves first takes the thing the other loves.
- **Contested exits (F3) never settle here.** The partner short of money always concedes everything. That is extraction by patience, and it shows in net pleasure, not in pleasure.
- **The prenup's effect is through who forms a household, not how it ends.** That is the same as in slice 1.

**Weaknesses, stated plainly:**

- The valuations, prices and weekly item pleasures are placeholders.
- Pleasure is clipped at 1, and happy households sit near it, which hides some of the item channel.
- A breach of a stay commitment under a settling arm still gets the settlement (the forfeit is bypassed).
- The leverage and exit-cost references favour F4.
