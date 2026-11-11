# H39 makers: preregistration

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Status: written and committed before any H39 code or run. Nothing here is a result. Scripted persona agents. Model API calls: none. Design: [h39-makers-design.md](h39-makers-design.md). The pilot, the power check and the "Can every verdict happen?" results need code, so they are added as Amendment 1, committed before the first confirmatory run. No prediction or threshold below may change in that amendment; it may only set the number of seeds and mark predictions DESCRIPTIVE if the power check says so.

**Can be about / cannot be about (required).** This can be about what six crediting rules, and negotiated protection of long projects, do to scripted agents who make food, art and care in the H38 household (F4, items V2), with assumed numbers. Limits that apply ([docs/limits.md](../limits.md)): 1 (the partner is a script; makers follow a scripted weekly rule and never learn), 5 (every number is assumed; the making values, time cost and credit motive above all), 6 (one author, one model family; the builder wrote the making model and the predictions), 10 (agents feel nothing; three seats; no market for made goods, no outside makers). Limits not touched: 2, 3, 7, 8 and 9 (no contact veto, crowding out, H32 judging rule or ladder rung is involved). Limit 4 applies weakly: the C-agreed bargain has a stated disagreement rule. It cannot be about real domestic work, real makers, art or care, or about whether crediting is fair; only about what these rules do here.

## Purpose and claim

H39 in experiments/hypotheses.jsonl: norms that credit making (counting labor and care as contribution) raise total pleasure when everyone counts, compared with making counting for nothing; and the exit-fallback results change once making counts. H20a (author-confirmed): commitment matters because it lets long projects run long enough to pay; it is negotiated and rests on trust. A third question: does crediting by volume reward extractive makers more than crediting by pleasure given?

What would change a decision: if crediting raises pleasure, the household seed should carry a making-credit term, and the author's lean (base plus pleasure) is a candidate default. If not, making stays a gift and the exit split stays on money.

## Design

- World: the H38 household (`scripts/h38_pairing_run.py play`, pairing dial 0): baseline rules, may decline, `retest.FIXES_ON` and `retest.LEVERS`, F4 with `strip_split`, items in cell V2, 156 weeks. Makers on (design table) unless the arm says off.
- Decision rule: `decide_on="weighted"`, `decide_weeks=52` (per-persona w), unless the arm says otherwise.
- Pairings: the 120 H38 pairings (`H38.pairings(H38.CONFIRM)`). Seeds: 0 to n−1, n from the power check (at least 2).
- **Unit of resampling: the pairing**, seeds averaged first.

**Confirmatory arms** (protection off unless named):

| Arm | Crediting | Protection |
|---|---|---|
| Z | C-zero | off |
| H | C-hours | off |
| P | C-pleasure | off |
| BP | C-base+pleasure (the author's lean) | off |
| G | C-gift-at-exit | off |
| A | C-agreed | off |
| BP-PN | C-base+pleasure | negotiated |

**Descriptive arms:** BP-PI (protection imposed on every project), M0 (makers off, same decision rule), Z-w0 and BP-w0 (w = 0 for everyone), Z-net and BP-net (the old rule: net wellbeing, 26 weeks).

**Fixed and ASSUMED:** everything in the design's tables: the trait shares, per-block pleasures, time cost 0.012, credit motive κ = 0.004, replacement value 2.75 per block, tolerance and sensitization numbers (from `wanting.WantParams`), the project size (16 blocks), goal term 0.01 and work value 0.02 a week, the protection trust threshold 0.4, w's distribution.

**Measures.**

- **pleasure** (primary): mean clipped weekly pleasure over both partners and 156 weeks, the H38 `pl`.
- **unclipped pleasure** (the second measure): the same with the raw, unclipped weekly value (`p_raw`).
- **net**: pleasure minus both kinds of suffering. Shown, not judged on.
- **making**: blocks per partner-week while living together; share made by partners with enjoyment 0; share by kind.
- **imbalance**: among pair-seeds together at least 104 weeks, the bigger maker's share of cumulative blocks at week 52 and at the end; "evens out" if it falls by at least 0.02.
- **extractive credit share**: in pairings with exactly one extractive partner, that partner's share of the pair's making credit at the end.
- **projects**: per pair-seed, long projects started, completed, and paid (completed, with the household together at least 13 weeks after completion).
- **exit split**: at each executed exit, the leaver's F4 share with making credit and without it.
- **formation**: share of pair-seeds formed at week 0.

## Exploratory pilot

To be run before Amendment 1 on pilot pairings (`H38.PILOT`, its own sample seed 900) and seeds 900 and 901, and excluded from the confirmatory data. Reported in Amendment 1.

## Power check (required)

In Amendment 1: `mar.stats.seeds_for_power` on the pilot's per-pairing spread of BP − Z (P1), BP-PN − BP (P6) and P − H in extractive pairings (P5b). The pairings are fixed at 120; the check sets seeds per pairing (2 or 4). A prediction short of 80% power at the chosen n is marked DESCRIPTIVE.

## Predictions

| ID | Quantity (formula) | Unit | Comparison and threshold | Test | Alpha | Family | Interval |
|---|---|---|---|---|---|---|---|
| P1 | pleasure, BP − Z | pairing | ≥ +0.003, CI above 0 | paired sign-flip, one-sided greater | 0.05 | Holm over P1, H−Z, P−Z, G−Z, A−Z (each one-sided greater) | 95% bootstrap over pairings |
| P1b | unclipped pleasure, BP − Z | pairing | same sign as P1's estimate | sign agreement | – | – | 95% bootstrap |
| P2 | blocks per partner-week while together, H − Z, P − Z, BP − Z | pairing | each ≥ +0.10 | paired sign-flip, greater | 0.05 | Holm over the three | 95% bootstrap |
| P3 | share of all blocks made by enjoyment-0 partners, H − Z | pairing (pairings with an e = 0 partner) | ≥ +0.03 | paired sign-flip, greater | 0.05 | none | 95% bootstrap |
| P4 | share of long-together pair-seeds whose imbalance evens out, BP − Z | pair-seed | within ±0.10 (crediting does not change whether imbalances even out) | equivalence by CI inside ±0.10 | 0.05 | none | Newcombe 95% for the difference |
| P5 | extractive partner's credit share, H − P | pairing (exactly one extractive partner) | ≥ +0.05 | paired sign-flip, greater | 0.05 | Holm over P5, P5b | 95% bootstrap |
| P5b | pleasure, P − H, pairings with at least one extractive partner | pairing | > 0, CI above 0 | paired sign-flip, greater | 0.05 | same | 95% bootstrap |
| P6a | long projects started per pair-seed, BP-PN − BP | pairing (at least one artist) | ≥ +0.20 | paired sign-flip, greater | 0.05 | Holm over P6a, P6b, P6c | 95% bootstrap |
| P6b | projects paid per pair-seed, BP-PN − BP | same | ≥ +0.10 | same | 0.05 | same | 95% bootstrap |
| P6c | pleasure, BP-PN − BP | same | estimate > 0 and CI lower bound ≥ −0.002 (not worse) | paired sign-flip, greater | 0.05 | same | 95% bootstrap |
| P7 | week-0 formation, BP − BP-w0 | pairing | ≤ −0.10 | paired sign-flip, less | 0.05 | none | 95% bootstrap |

Effect sizes for every comparison: the difference with its interval, and Cliff's delta over pairings.

Notes on what each prediction can carry:

- **P2 is a manipulation check.** The credit motive is in the making rule by construction. It can still fail (time cost and tolerance can swamp the motive), but it gets no verdict weight.
- **P5 is close to built in.** An extractive maker makes more blocks that are liked less, so a volume rule must credit them more than a pleasure rule, unless the motive changes who makes. It is reported, with little weight. **P5b carries the extractive question**: does crediting by pleasure given protect total pleasure when an extractive maker is present?
- **P3 and P4** are the "who makes" and "does it even out" questions. P4 predicts no change.
- **P7** is the research note's preregistered consequence, not a test of H39.

## Verdict rule

- **H39: supported** iff P1 holds robustly (estimate ≥ +0.003, CI above 0, Holm p < 0.05) and P1b agrees in sign. **Not supported** iff the BP − Z estimate is below +0.003 and the CI's upper end is below +0.006, or the estimate is ≤ 0. Otherwise **inconclusive**. The other crediting arms are reported against Z in the same family, as descriptive comparisons.
- **H20a (the commitment part): supported** iff P6a, P6b and P6c all hold. The "having a goal matters more than achieving it" clause is not testable here (it is an input).
- **Extractive question:** answered by P5b.
- "Holds but CI crosses threshold" is weak support, not a confirmed hold.

## Can every verdict happen? (required)

To be filled in Amendment 1 from free checks, before any confirmatory run. Planned checks:

| Verdict or clause | Free check that reaches it (or makes it fail) |
|---|---|
| H39 supported | the analysis on synthetic rows: the Z rows with +0.01 added to BP |
| H39 not supported | the analysis with BP rows copied from Z (no difference) |
| H39 inconclusive | the analysis with BP = Z + 0.004 plus alternating ±0.08 per pairing |
| P5 fails | extractive cue 0 and boost 0 (extractive = safe) on a few pairings: credit shares match |
| P5b fails | the analysis with H and P rows swapped |
| P6a/P6b fail | protection agreement threshold above 1 (nobody agrees): BP-PN = BP |
| P7 fails | the analysis with BP-w0 rows copied into BP |
| open cells | count pairings with exactly one extractive partner (P5), at least one extractive (P5b), at least one artist (P6), an e = 0 partner (P3) |
| metric sees the mechanism | trace: maker pleasure → `close_week(extra_pleasure)` → `pleasure` → `pl`; credit → `contribution_share` → `settlement` → `carry_out` → exit money and the outside option at readings |

## Are we measuring what we say? (required)

**Construct cards.**

- **Making** = a partner spending 2 of their 10 weekly time units on a block that gives the other partner (and, for art, both) a fixed amount of modeled pleasure, while both live together. It does NOT encode skill, learning, quality that varies by maker, buying vs making, making for the friend or for strangers, co-made activities (games played together, sex, improv), or shared chores that only avoid suffering (cleaning). Care here is a pleasure, not relief from suffering.
- **Credit** = a number in money units added to a partner's contribution in the F4 exit split. It does NOT encode thanks, status, guilt or scorekeeping friction, and it never pays anything while the household lasts. "Running tally" only means the maker's weekly choice sees the credit; there is no ledger cost.
- **Extractive** = a maker whose goods carry a cue that raises the receiver's wanting above liking and sensitizes it, and who decides by the receiver's wanting. It does NOT encode profit, intent, deception, or a market. Its harm in the model is lost liking from tolerance, extra time spent and a small craving cost.
- **Long project** = 16 blocks of an artist's time, lost if the household splits first, then a lasting shared work. It does NOT encode a relationship or a personal goal, risk of failure other than a split, or projects by cooks or carers. "Having a goal" is a fixed weekly term (an input).
- **Pleasure given** = the receiver's modeled liking from a block, which equals how much better off they are than fending for themselves, because fending for themselves gives nothing extra here. It does NOT encode the receiver's own judgment of the gift.
- **Protection** = a promise that if the partner leaves before the project is done, its blocks count for the artist at exit. It does NOT stop anyone leaving. Trust is flat at 0.7 in this world, so agreement rests on the partner's own stay reading.

A reader should see from these that H39 here is about time-costly goods credited at exit, not about the value of domestic work in general.

**Known-answer cases** (checked by tests before the run):

1. Free, enjoyed making: with time cost 0 and a caring persona, making must add pleasure to the receiver over makers off.
2. No making: with makers on but every block's value 0, nothing is made, and runs equal makers-off on pleasure.
3. Credit is inert without exits: in a run where nobody leaves, the crediting rule can change pleasure only through the motive; with κ = 0, C-zero and C-hours are identical.
4. Extractive vs safe: for the same receiver, an extractive maker's blocks per week are higher and liking per block lower than a safe maker's.

**Second operationalization of the main measure:** unclipped pleasure (P1b). Pleasure is capped at 1 and much of the household sits near the cap, so the clipped measure can hide what makers give. If the two disagree, the conclusion is fragile and says so.

**Story spot-check (after the run):** read 3 to 5 runs as week-by-week stories with the pattern-atlas recorder (src/mar/atlas.py), from different arms (at least Z, BP, BP-PN and one pairing with an extractive maker), with each 13-week block also showing blocks made, credit and project state. Say whether the stories look like what the measures claim. A mismatch is reported as a finding. If the observer layer has landed, a sample of runs also gets its decision decomposition.

## Not testable by design

The bit-identical reproduction with makers off (a pass/fail test). The four known-answer cases (tests). C-gift-at-exit equals C-base+pleasure at exit with the motive off (by construction).

## Limits stated now

Scripted makers on a fixed rule. Three kinds, one value point each. Credit only at exit, only through F4. Pleasure is clipped. One world, 120 pairings, assumed numbers throughout. The builder wrote the making model and the predictions, so passing predictions check the model more than the world.

## Amendments

(none yet)
