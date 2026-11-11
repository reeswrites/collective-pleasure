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

### Amendment 1 (2026-11-11): calibration, pilot, power, "Can every verdict happen?"

Committed before any confirmatory run. No prediction, threshold, test or verdict rule changed. Code: commit 823e43a (`src/mar/makers.py`, `scripts/h39_makers_run.py`).

**Calibration before the pilot (parameters changed, stated plainly).** The design's first numbers broke the household. With 2-unit blocks and a 0.012 time cost, makers spent up to 6 of their 10 weekly units and displaced paid work. On 8 to 15 pilot pairings (sample seed 900, excluded from the confirmatory data) pleasure fell from 0.967 (makers off) to 0.86 and half the pairs stopped forming. A second problem: at the next setting, safe cooks and carers never made anything (a block was worth less than its time to every persona), so all making was by artists and extractive makers. The calibrated point, chosen on those pilot pairings only:

| Parameter | Design | Now |
|---|---|---|
| time units per block | 2 | 1 |
| time cost per block | 0.012 | 0.02 |
| a meal; care (struggling receiver) | 0.03; 0.02 (0.03) | 0.03; 0.02 (0.03), now per 1-unit block |
| a piece, per partner-week for 8 weeks | 0.004 | 0.003 |
| process pleasure at enjoyment 1 | 0.01 | 0.005 |
| replacement value per block | 2.75 | 1.375 (the wage for 1 unit) |
| a typical block (C-pleasure rate = replacement / typical) | 0.03 | 0.025 |
| credit motive κ | 0.004 | 0.007 (about half the time cost at money weight 1) |
| extractive cue; craving | 0.02; 0.05 | 0.01; 0.025 |
| long project | 16 blocks | 32 blocks (the same time), 2 blocks a week expected |

So a block now gives about 1.2 times its time cost to a receiver, and a caring partner (togetherness weight above about 0.6) makes. The time cost of 0.02 is the point where 1 to 2 blocks a week leave average pleasure about where makers-off has it; it is a fitted number, not a measured one.

**Pilot (EXPLORATORY; 30 pilot pairings, seeds 900 and 901, arms Z, H, P, BP, BP-PN; excluded from the confirmatory data).**

| Quantity | Pilot effect | Pilot sd of the pairing | Source |
|---|---|---|---|
| P1 pleasure, BP − Z | +0.0002 | 0.021 | runs/h39-makers/pilot-analysis.json |
| P2 blocks per partner-week, BP − Z | +0.20 | 0.30 | same |
| P3 enjoyment-0 share, H − Z | −0.015 | 0.10 | same |
| P5 extractive credit share, H − P | +0.014 | 0.12 | same |
| P5b pleasure, P − H, extractive pairings | −0.007 | 0.028 | same |
| P6a projects started, BP-PN − BP | +0.16 | 0.51 | same |
| P6b projects paid, BP-PN − BP | +0.09 | 0.49 | same |
| P6c pleasure, BP-PN − BP | −0.0007 | 0.006 | same |

What I saw: makers on, at this calibration, sits near makers off on pleasure; crediting raises making (+0.2 blocks per partner-week) but not pleasure; imbalances never evened out in any arm (0 of 10 to 14 long-together pair-seeds); protection was asked for in about 0.2 runs per pair-seed and agreed in 0.17.

**Power check** (`seeds_for_power`, paired, 80%, alpha 0.05, on the pilot's 2-seed spreads; `runs/h39-makers/power.json`). Open cells in the 120 confirmatory pairings: 59 with exactly one extractive partner, 91 with at least one, 63 with at least one artist, 84 with an enjoyment-0 partner.

| Prediction | Margin or effect | Spread | Units for 80% | Units available | Status |
|---|---|---|---|---|---|
| P1 | 0.003 | 0.021 | over 300 | 120 | **DESCRIPTIVE** |
| P2 | 0.10 | 0.30 | about 75 | 120 | confirmatory (manipulation check, no verdict weight) |
| P3 | 0.03 | 0.10 | about 90 | 84 | **DESCRIPTIVE** |
| P5 | 0.05 | 0.12 | about 46 | 59 | confirmatory (little weight, see above) |
| P5b | 0.007 | 0.028 | 110 | 91 | **DESCRIPTIVE** |
| P6a | 0.20 | 0.51 | 52 | 63 | confirmatory |
| P6b | 0.10 | 0.49 | 199 | 63 | **DESCRIPTIVE** |
| P6c | pilot effect 0.0007 | 0.006 | over 300 | 63 | **DESCRIPTIVE** |
| P4, P7 | – | – | no pilot (P4 had 10 to 14 pair-seeds per arm; P7's arms were not piloted) | – | P4 DESCRIPTIVE; P7 confirmatory |

Seeds: 4 per pairing (0 to 3), the most the run budget allows (13 arms × 120 pairings × 4 seeds, about 45 minutes on 3 workers). Four seeds lower the per-pairing spread, so the table above is conservative, but it does not close P1's gap. **So the H39 verdict and the H20a verdict are DESCRIPTIVE**: the verdict rules are applied and reported, without verdict wording in the summary.

**Can every verdict happen?** (`scripts/h39_makers_run.py --reach`, `runs/h39-makers/reach.json`; the analysis code run on relabelled or shifted pilot rows, plus small parameter flips on 10 pilot pairings.)

| Verdict or clause | Free check | Result |
|---|---|---|
| H39 supported | BP = Z + 0.01 | reached (P1 holds, P1b holds) |
| H39 not supported | BP = Z | reached |
| H39 inconclusive | BP = Z + 0.004 ± 0.08 by pairing | reached |
| P5b fails / holds | the pilot (P − H = −0.007) fails; H and P swapped gives a positive estimate | both reached |
| P5 fails | extractive = safe (cue, boost and craving 0): extractive share 0.50 under H, 0.63 under P (H − P negative) | reached |
| P6 (H20a) supported | BP-PN = BP plus one more project started and paid, +0.003 pleasure | reached |
| P6 fails | BP-PN = BP | reached |
| nobody agrees to protect | trust threshold 2 | agreed 0 (the negotiation can say no) |
| P1b can disagree | the inconclusive case | reached (P1b misses) |
| metric sees the mechanism | `makers.week_terms` → `close_week(extra_pleasure)` → weekly `pleasure` → `pl`; credit → `exit_fallback.contribution_share` → `settlement` → `carry_out` (exit money and the outside option at readings); unit test `test_contribution_share_includes_credit_and_protected_project` | traced |

P4 ("imbalances even out") can fail in both directions on the analysis, but the pilot shows 0 evening out in every arm, so P4's "within ±0.10" may hold only because nothing evens out anywhere. That is reported as such.

Observer layer: it landed (commits 218ee4a and before) before this run. Maker pleasure and craving reach its decision decomposition inside the "other" group (the observer has no makers group); a sample of runs is read with it after the run.
