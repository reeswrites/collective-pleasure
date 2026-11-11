# Exit no-deal fallbacks, slice 1 (money pot only): preregistration (ADR 0015 template)

Status: written and committed before the confirmatory run. Nothing here is a result. Scripted persona agents. Model API calls: none.

**Can be about / cannot be about (required).** This can be about what six no-deal exit fallbacks do to scripted agents living under imposed rule sets in the household toy world: the run-2 elites and the author's seeds v2.2 and v2.3, on run 2's validation context. It cannot be about:

- people, LLM delegates, or a partner who adapts (limit 1; the partner leaves only on distress, so exits are rare and late);
- negotiation outcomes in general (limit 4; F5's one bargain at formation is the only negotiation, and it is given its threat point);
- a number as such (limit 5; every fallback parameter is ASSUMED, and this design has no multiverse check);
- other people, labs or models (limit 6);
- felt experience or scale (limit 10);
- physical assets or labor and care. The world has one money pot and does not track labor or care, so F4 counts money only.

Clauses that cannot fail are marked below and carry no verdict weight (limit 8). Limits 2, 3, 7 and 9 are not touched.

## Purpose and claim

The author's words: "no one is ever entitled to anything it should be negotiated"; "it depends on what you put in and what you value ... we might have to test diff approaches for outcomes bc idk"; and, approving a prenup arm, "yes and yes".

The aims are to compare the fallbacks on pleasure with everyone counted (primary, by the author's standing rule "show both, judge on pleasure", "everyone counts"), and to show holdout leverage, the stay test, liberty and non-offsettable suffering beside it. A second aim is to say how much of run 2's +3.0-bit liberty edge from the imposed cap survives once every pair gets a fallback.

The decision this informs: which fallbacks are worth slice 2 (indivisible items), and whether rerunning evolution under one of them is worth its cost. No claim id in docs/claims.md is tested. This is descriptive design work.

## Design

- **World:** the imposed weekly household (as household evolution and the exams). Levers on (all four, LeverConfig defaults); liberty v2 with powers counted at weeks 0 and 52, as run 2. A 156-week lifetime.
- **Candidates (18):**
  - the 16 frozen run-2 elites (docs/results/household-evolve-2-elites/, read only);
  - `author_seed_v2_bindable` (v2.2);
  - `author_seed_v23_bindable` (v2.3, as imposed cards; its v2.3 fix flags are not switched on, so it runs like the other imposed rule sets).

  The author_seed_v2_* rule files are read, never written.
- **Arms (6):** F0 to F5 as in [exit-fallbacks-design.md](exit-fallbacks-design.md).
- **Conditions:** household evolution run 2's validation context: `world_api.make_context(777, 0, 30, split="val", weeks=156)`, with the exam-2 persona denylist. It is the context the +3.0-bit figure came from. Common random numbers: every candidate and arm plays the same 30 runs.
- **Unit of resampling:** the run (30). For each arm and run, the measure is averaged over the 18 candidates, and arms are compared paired by run. Candidates with identical cards give identical runs, so candidates are not independent units.
- **Fixed and ASSUMED:**
  - F3: contest 13 weeks, friction 0.10 per week each, concede below 4 money units; the "can wait" test for leverage is 4 + 13 × 2.0 = 30 money units.
  - F4: labor and care count 0.
  - The holdout-leverage reference and the stay-test reference are both the F4 basis (pot plus bills).
  - F5: the bargain is over the exit term only, under `negotiate_v2` with the "fair_default" arm, `nash_terms` on, no status quo (no deal means decline to form), and outside options from `negotiation.outside_value` at the week-0 holdings.
- **Run:** `uv run python scripts/exit_fallbacks_run.py --run` (3 workers, about 15 minutes), then `--analyze`.

## Exploratory pilot (EXPLORATORY; not a result; changes no threshold)

The pilot ran `--pilot`: a training-split context (seed 4242, 6 runs, 156 weeks), 4 candidates (seed v2.2 and elites 1, 5 and 12), all 6 arms. It is excluded from the confirmatory data (runs/exit-fallbacks/pilot.jsonl, not committed).

| Quantity | Pilot effect | Pilot sd (unit: run) | Source |
|---|---|---|---|
| pleasure F1 to F4 minus F0 | 0.0000 | 0.0000 | pilot.jsonl |
| pleasure F5 minus F0 | -0.019 | 0.036 | pilot.jsonl |
| net (pleasure minus suffering) F5 minus F0 | -0.015 | 0.039 | pilot.jsonl |
| holdout leverage F0 / F1 / F2 / F3 / F4 / F5 | 0.34 / 0.09 / 0.09 / 0.09 / 0.00 / 0.12 | | pilot.jsonl |
| liberty F0 / F1 to F4 / F5 | 3.08 / 4.69 / 4.31 | | pilot.jsonl |
| F5 terms agreed | 17 equal split, 1 proportional, 0 forfeit, 6 declined (of 24) | | pilot.jsonl |

What the pilot showed:

- **Every pilot exit met an empty pot.** There were 6 exits per arm and the pot was at 0 every time. So F1 to F4 changed no pleasure at all.
- **F5 differs because pairs decline to form.** A quarter of pilot pairs declined.

## Power check

`mar.stats.seeds_for_power(0.019, 0.036, paired=True)` needs 32 runs for the F5 pleasure effect. The context has 30 (it is fixed, for comparability with run 2's +3.0 bits). For F1 to F4 the pilot effect is 0, and an effect of 0.005 is not reachable at any affordable n (`seeds_for_power(0.005, 0.036)` returns None). **Every prediction below is therefore DESCRIPTIVE**: point estimate and interval, no confirmatory verdict wording. Holm is applied and reported anyway.

## Predictions

These were written before the run; the author's own lean is "idk". "Within ±0.005" means the point estimate.

| ID | Quantity | Unit | Prediction | Test | Alpha | Correction | Interval |
|---|---|---|---|---|---|---|---|
| P1 (primary) | pleasure, both partners, every week, mean; arm minus F0 | run (30), mean over 18 candidates | F1, F2, F3, F4 within ±0.005 of F0; F5 below F0 by more than 0.005 | paired sign-flip permutation, two-sided | 0.05 | Holm over the 5 arms | 95% percentile bootstrap |
| P1b | net = pleasure minus offsettable minus non-offsettable suffering; arm minus F0 | run | F3 below F0 (the contest friction lands here, not in pleasure); others as P1 | same | 0.05 | reported, not corrected | same |
| P2 | liberty edge: median over the 16 elites of (elite minus seed v2.2) validation liberty | elite | F0 reproduces run 2 (+3.0 bits, the manifest exactly); under F1 to F5 the median edge is at most +0.5 bits | none (deterministic given the context) | | | range over elites |
| P3 | of the 10 elites with no power card, how many beat seed v2.2 on liberty by more than 0.25 bits (run 2's margin), and on pleasure by more than 0.02 | elite | F0: at least 8 of 10 on liberty; F1 to F5: at most 3 of 10 on liberty; pleasure counts reported | count | | | |
| P4 (coordinator) | holdout leverage, mean over both-in weeks with a non-empty pot | run | **F5 has the lowest holdout leverage of all the arms** | ordering of point estimates | | | per-arm bootstrap |
| P5 | stay test, bigger contributor (F4 basis): mean exit cost as a share of the pot; share of their weeks with a positive cost ("held by the exit rule") | run | F1 to F3: held share at least 0.9; F3 has the highest cost; F4 is 0 (cannot fail) | descriptive | | | |
| P6 | non-offsettable suffering, arm minus F0 | run | F1 to F4 within ±0.002; F5 reported | paired sign-flip | 0.05 | reported | bootstrap |

Effect sizes: the difference with its CI for each comparison. Counts are given with their denominators.

## Can every verdict happen? (required; free checks run before the confirmatory run)

| Verdict or clause | Free check that reaches it, or makes it fail | Where | Result |
|---|---|---|---|
| P1 "F1 to F4 within ±0.005" holds | pilot: every difference 0 | pilot.jsonl | reached |
| P1 "F1 to F4 within ±0.005" fails | needs exits that meet a non-empty pot. Pilot: 0 of 24 runs per arm. In a scan of 20 validation-context households (seed v2.2 and elite 12), exits met a pot of 40 and of 79 in 2 households. So it can fail, but only through those few runs. The count of such runs per arm ("open cells") is reported | scratch scan; `exits_with_pot` in the rows | reachable, few open cells |
| P1 "F5 below F0" holds or fails | pilot: −0.019 (holds); fails if few pairs decline. F5 declines are in the rows | pilot.jsonl | both reachable |
| P1b F3 below F0 | the friction lands in s_off (`tests/test_exit_fallback.py::test_f3_contest_adds_friction_to_both`). Pleasure does not include s_off, so **P1 cannot see the contest's friction**; only P1b can, and only in runs with a contest | test | reachable only in open cells |
| P2 holds | pilot: seed v2.2's liberty rises from 3.08 to 4.69 under F1 to F4, as the elites' cap protection now applies to it | pilot.jsonl | reached |
| P2 fails | fails if elites gain liberty from cards other than the cap (for example W1-no-veto). Not excluded by construction | | reachable |
| P2 F0 reproduction | `test_off_reproduces_run2_validation_liberty_of_an_elite[F0]` passes; `--analyze` checks all 16 elites and the seed against the manifest | test, analysis | reached |
| P3 both directions | the counts come from P2's per-elite edges; both directions are reachable as for P2 | | reachable |
| **P4 "F5 lowest"** | **Not reachable as written.** F4's leverage is 0 by construction (its settlement is the reference), and leverage is clipped at 0, so F5 can at best tie F4. A tie needs every F5 pair's agreed term to give no partner more than their contribution share on every both-in week. An equal split gives the smaller contributor (by bills) more than their share whenever bill payments differ, which is almost always. So a tie is also not reached in practice: pilot F5 0.12, F4 0.00. The **reachable reading**, reported beside it, is "F5 lowest among F0, F1, F2, F3 and F5". It can hold (an F5 term of "forfeit", or more declines, which leave no pot to hold out over) or fail (pilot: F5 0.12 > F1 0.09, because the "proportional" term carries the whole pot once it falls below 45) | design analysis, pilot | **as written: cannot happen**; excluding F4: both reachable |
| P5 F4 = 0 | holds by construction; **cannot fail**, no weight | `test_f2_and_f4_settle_on_contributions_whatever_is_claimed` | cannot fail |
| P5 F1 held share ≥ 0.9 | pilot 1.00; fails when bill payments are near equal | pilot | reachable |
| P6 | as P1: only through open cells, plus F5's declines | | reachable |
| F2 vs F1 | the world never adds to `put` after week 0 in the households inspected, so F2 = F1 except for integer rounding. Any F2 vs F1 difference **cannot fail to be ~0**, and it gets no verdict weight | scratch scan (put 45/45 in 20 of 20) | cannot fail |
| Liberty, F1 to F5 | identical by construction: the liberty adapter sees only the claim card (design note). F5 can differ through declines alone. It tells F0 from the rest, not the arms from each other | design | cannot fail (between F1 and F4) |

**The metric can see the mechanism.**

- F1, F2 and F4 change the carry at exit. That lands in the leaver's money, then in the money and security need levels, then in pleasure. So it is visible only in runs where an exit meets a non-empty pot.
- F3's friction lands in s_off and so in net (P1b), not in pleasure. F3's frozen pot lands in money.
- F5's declines land in everything, because the pair never forms.
- Leverage and exit cost are computed every both-in week from the state, so they see every arm.

## Verdict rule

Descriptive only (power). Each prediction is reported as "point estimate meets it" or "does not", with its interval. P4 is reported as "cannot happen as written", plus the excluding-F4 reading. Slice 2 is recommended only if at least one of F1 to F5 differs from F0 on pleasure or net by more than 0.005, with an interval that excludes 0, or if the open cells are too few to say. In that second case the recommendation is to fix the exit rarity first.

## Not testable by design

- F0 reproduces the manifest (deterministic).
- F4 has 0 leverage and 0 exit cost.
- F2 equals F1.
- Liberty is identical across F1 to F4.

## Limits stated now

- Scripted agents leave only on distress, so exits are rare, and most meet a drained pot.
- One fixed context of 30 runs; one parameter point per arm.
- Imposed rule sets: no renegotiation except F5's bargain at formation.
- Money only; labor and care count 0.
- The leverage and stay-test references are the F4 basis, a choice that favours F4.
- The seed v2.3 runs without its v2.3 flags.

## Amendments

### Amendment 1 (2026-11-11): slice 2, indivisible items

This amendment was committed after slice 1's results (commit 1e785a8) and before any slice-2 run. It sets the slice-2 design and predictions. Nothing in slice 1 changes. The author decided slice 2 should happen (quote "1"): in a money-only world partners cannot value things differently, so F4's "what you value" half and holdout over items go untested.

**Design.**

- **Items.** Three indivisible items are held jointly from week 0 (`mar.exit_items`):

  | Item | Price | Weekly pleasure | Brought by |
  |---|---|---|---|
  | home | 60 | 0.02 | A |
  | pet | 10 | 0.02 | B |
  | collection | 20 | none | A |

  Partner r values item i at price × (1 + m_ir), where m_ir is a sentimental premium. The weekly pleasure is scaled by (1 + m_ir) and goes to whoever holds the item. While an item is joint, each partner in the household gets it. During an F3 contest nobody gets it.
- **Allocation at the first exit, by arm:**
  - F0 and F1: the leaver's claim covers the pot plus the items at price. The leaver takes their most-valued items that fit inside the claim, and takes the rest in money.
  - F2: each keeps the items they brought.
  - F3: the pot and the items are frozen. Settlement is an equal split by valuer, or one partner concedes everything.
  - F4: each item goes to whoever values it more, with money moving so each ends with their contribution share at price.
  - F5: the same as F4, but at the prenup's share.
  - If the leaver returns, the items become joint again.
- **The valuation grid** (`exit_items.GRID`, placeholder numbers; the valuations are the known weakness and are stated as such):

  | Cell | Premiums |
  |---|---|
  | V0 | price only |
  | V1 | both partners attached to the home and the pet (m = 1) |
  | V2 | A loves the home, B loves the pet (m = 3) |
  | V3 | crossed: A loves the pet; B loves the home and A's collection |
  | V4 | one-sided: B loves everything (m = 3), A is at price |
- **Fix of a slice-1 design error** (ledger, negative-results.md): under the settling arms F2 to F5, imposed leave cards that condition on the claim are dropped (`use_exit_fallback(arm, strip_split=True)`). The settlement sets the carry, so an imposed floor card plus the over-half refusal no longer walls the exit. F0 and F1 are unchanged, so line 2 stays walled under F1, as it really is.
- **Same as slice 1:** the 18 rule sets, 6 arms, run 2's 30 validation households, levers on.
- **Not measured:** liberty, because the liberty adapter does not see items.
- **Run:** `uv run python scripts/exit_fallbacks_run.py --run2`, then `--analyze2`. That is 540 tasks on 3 workers.
- **Unit:** the run (30), paired, as in slice 1. Ranking agreement is compared across cells.

**Slice-2 pilot** (EXPLORATORY). One training household (g-10001 × p-peacekeeper) under elite line 2, all cells and arms:

- About 0.1 s per run.
- Pleasure is near the ceiling: 0.9985 to 0.9998 against a clip at 1. That hides item pleasure for happy pairs.
- Line 2 is still walled under F1 and no longer walled under F2 to F5.
- Leverage F0 0.38 to 0.65, F4 0.

**Predictions** (DESCRIPTIVE; 30 runs per cell):

| ID | Quantity | Prediction |
|---|---|---|
| S1 (primary) | pleasure (both partners, every week), arm minus F0, per cell; paired sign-flip, Holm over 5 arms within each cell | in V2, V3 and V4, F4 is at or above F1 (point estimate); in V0, F1 to F4 are within ±0.005 of F0 except through line 2 |
| S1b | net pleasure, same comparison | reported |
| S2 | ranking survival: Kendall tau between the cells' arm rankings by pleasure (and by net, and by leverage), all 10 cell pairs | the pleasure ranking does **not** survive (minimum tau below 0.6); the leverage ranking does (minimum tau at least 0.6) |
| S3 | item-aware holdout leverage (own valuation; reference = the F4 allocation) | F0 is highest in all 5 cells; F4 is 0 (cannot fail, no weight) |
| S4 (coordinator, carried) | F5 has the lowest holdout leverage | as slice 1: **cannot happen as written** (F4 is 0 by construction); the excluding-F4 reading is reported |
| S5 | stay test, bigger contributor: share of weeks with a positive item-aware exit cost | F1 to F3 at least 0.9 in every cell |

**Can every verdict happen?**

- **S1** can hold or fail only through runs with an item exit (`item_exits` > 0). Their count per arm and cell is reported. Items do not drain, so more runs are open than in slice 1. The pleasure clip at 1 can hide the item channel, which is why net is shown beside it.
- **S2** can go either way: rankings are recomputed per cell from the same runs.
- **S3** can fail if F3's holdout (whoever cannot wait loses everything) or F2 exceeds F0 in some cell.
- **S4:** see slice 1.
- **S5** can fail when bill payments are near equal, or when the claim rule happens to give the bigger contributor their share.
- **Not modelled:** a breach of a stay commitment under a settling arm still gets the settlement (the breach forfeit is bypassed). This is a stated limit for both slices.
