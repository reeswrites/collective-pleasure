# H39b makers rerun: preregistration

Wording rule: agents feel nothing; "pleasure", "liking" and "wanting" are glosses for modeled values.

Status: written and committed before any H39b code or run. Nothing here is a result. Scripted persona agents. Model API calls: none. H39b is a corrected rerun of H39 ([h39-makers-prereg.md](h39-makers-prereg.md), [h39-makers.md](h39-makers.md)). The pilot, the power check, the known-answer checks and the "Can every verdict happen?" results need code, so they come in Amendment 1, committed before the confirmatory run. Amendment 1 may not change a prediction, threshold, test or verdict rule; it may only mark predictions DESCRIPTIVE if the power check says so.

**Can be about / cannot be about (required).** This can be about what six crediting rules and negotiated protection of long projects do to scripted makers in the H38 household (F4, items V2) when making is chosen against the agent's own other uses of the time, with assumed numbers. Limits that apply ([docs/limits.md](../limits.md)): 1 (the partner is a script; makers follow a scripted weekly rule and never learn), 5 (every number is assumed; the per-block values and the credit motive above all), 6 (one author, one model family; the builder wrote the making model, the correction and the predictions), 10 (agents feel nothing; three seats; no market for made goods). Not touched: 2, 3, 7, 8, 9. Limit 4 applies weakly (C-agreed's disagreement rule). It cannot be about real domestic work, real makers, art or care, or whether crediting is fair.

## Why a rerun

The author asked "why are there any fitted time costs other than work and sleep" (experiments/questions.jsonl, 2026-11-11T17:10:50Z) and said "yes" to the fix (experiments/changes.jsonl, same time). Our review found:

1. **Time was counted twice.** A block of making already uses 1 of the agent's 10 weekly time units, so it already displaces something in the world's own terms. H39 also subtracted a flat 0.02 pleasure units per block inside the maker's choice.
2. **The 0.02 was fitted to an outcome.** Amendment 1 chose it as the point where 1 to 2 blocks a week leave pleasure about where makers-off has it. That is fitting a parameter so one arm matches another, and it biases the result toward null.
3. **It existed because the choice was incomplete.** `choose_blocks` added up a block's benefits and never compared them with the best other use of the time unit. Without a cost, makers over-made and crowded out paid work; the flat cost was a patch.
4. **The H39 headline rests on it.** "Makers lower pleasure" and "a running tally lowers pleasure" both run through this choice.
5. **The wanting trap was invisible.** In the H39 story check one receiver sat at full tolerance and full sensitization for two years while clipped pleasure read 1.00.

## What changes, and nothing else

**1. No flat time cost.** There is no fitted time cost anywhere in H39b. The `time_cost` field is not read.

**2. The making choice compares a block with the agent's best other use of the time.** For maker m in week w, while both partners live together:

- **Value of block k**, as in H39 without the time cost: `v_k = e × proc + care × g_k + own_k + motive_k`. `e` is the persona's enjoyment of making; `care` its togetherness weight; `g_k` the receiver's liking (safe aim) or wanting (extractive aim) of block k; `own_k` the artist's own share of a piece; `motive_k = κ × money weight × credit of block k`, only under a rule with a running tally.
- **Enjoyment can be negative.** The author's logged reason for the fix says effort "enters as per-persona enjoyment of making, which can be negative". The same hash that drew H39's three levels {0, 0.5, 1} now draws {−1, 0, +1}, a third each (ASSUMED: dislike it, indifferent, enjoy it; mean 0, so making is not assumed enjoyable on average). Each persona keeps its rank: H39's e = 0 personas are H39b's e = −1. A negative `e × proc` is a chore cost to the maker, in the decision and in the maker's weekly pleasure.
- **The alternative is the agent's own planned week.** At the start of the week the world already values every use of time for the agent's weekly choice (`PersonaAgent.utilities`): work, rest, seeing friends, time together, spending on itself, paying into shared bills, each with its unit cost (4, 2, 2, 2, 1, 1). H39b reuses those numbers, without the choice's ±10% noise, and plans the week the way the world plays it: 3 passes, each taking the highest-utility action above the agent's own 0.003 floor that still fits in the units left. `V(b)` is the summed utility of that plan with b units. The cost of n blocks is `V(B) − V(B − n)`, B the units the agent has at the start of the week.
- **The choice:** n = the number of blocks (0 to 3) that maximizes `Σ_{k≤n} v_k − [V(B) − V(B − n)]`, ties to fewer. This is "make block k only if it beats the best other use of that time unit", made exact for actions that come in 2- and 4-unit lumps (two blocks can displace one together session). Blocks that fit in units the plan leaves idle cost nothing.
- **Bills and work.** The world has no fixed "bills first" order. Paying into bills has a utility that rises with the unpaid gap and at month end; work's utility rises as money falls. Both sit in the planned week by those utilities, so making displaces them only when the agent's own valuation says a block is worth more. Making still happens at the start of the week (as in H39), before the passes, but only in units whose planned use is worth less.
- **Scale.** The utilities are the agent's own estimate of an action's hedonic change, in the hedonic model's units; the making values are weekly pleasure in the same model. Nothing is rescaled. That the two are commensurate is ASSUMED and is the construct card's main caveat.
- **Long projects** are unchanged: an artist with a running project puts in at least one block a week even when the choice says 0.

**3. Two measures that can see the wanting trap**, beside clipped and unclipped pleasure:

- **Lifetime liking lost to tolerance** (the liking side of ADR 0018 test 1): for every block received, the liking it would give at tolerance 0 minus the liking it gave, summed over the receiver's 156 weeks and over both partners. Also as a share of the liking at tolerance 0.
- **Share of person-weeks in a full wanting trap:** person-weeks (2 × 156 per pair-seed) in which the person's tolerance is at least 3 of 4 and their sensitization at least 9 of 12. Only extractive goods sensitize, so this is 0 without an extractive partner, by construction.

Also reported, descriptive: the liking-to-wanting ratio of blocks received (ADR 0018 test 1), and a decomposition of every making decision (value parts, alternative cost, blocks made in idle units, which planned actions were displaced).

**4. Everything else is H39 as run.** The same 13 arms, the 120 H38 pairings, seeds 0 to 3, F4 with items V2, the per-persona suffering weight w, the six crediting rules, C-agreed's bargain, protection, and every number in H39 Amendment 1's calibrated table other than the time cost (block 1 unit; meal 0.03; care 0.02 or 0.03; piece 0.003 a week for 8 weeks; proc 0.005; replacement value 1.375; typical block 0.025; κ 0.007; cue 0.01; craving 0.025; boost 0.2; project 32 blocks; the tolerance and sensitization clocks from `wanting.WantParams`). Two of these were set beside the fitted time cost: κ ("about half the time cost at money weight 1") and the per-block values ("about 1.2 times its time cost"). They are carried over unchanged so the comparison is clean, not refitted; they are ASSUMED numbers whose original anchor is gone, and that is a limit. BP − G still measures the motive at this κ and scales with it. No parameter in H39b is chosen by looking at any arm's outcome; the pilot is used only for the power check.

**5. H39 stays reproducible.** `MakerConfig(choice="flat_cost")` (the default) is H39's choice; `choice="opportunity"` is H39b's. Fingerprints of H39 runs (4 arms × 4 cells, from commit 2b8a100) are pinned in `tests/data/makers_flatcost_fingerprints.json` before any change, beside the makers-off fingerprints.

## Purpose and claim

The same as H39: H39 (crediting making raises total pleasure against making counting for nothing), H20a's commitment clause (negotiated protection lets long projects run long enough to pay), and the extractive question (does crediting by volume reward extractive makers more than crediting by pleasure given?). Plus: which H39 findings were artifacts of the fitted cost.

What would change a decision: if crediting now raises pleasure, the household seed could carry a making-credit term. If makers-on now beats makers-off, H39's "making costs more time together than it gives back" was an artifact and the docs must say so.

## Design

As H39 (see its prereg): world, decision rule `decide_on="weighted"`, `decide_weeks=52`, pairings `H38.pairings(H38.CONFIRM)`, **unit of resampling the pairing**, seeds 0 to 3 averaged first. Arms: confirmatory Z, H, P, BP, G, A, BP-PN; descriptive BP-PI, M0, Z-w0, BP-w0, Z-net, BP-net. All with `choice="opportunity"` and enjoyment {−1, 0, +1}.

## Exploratory pilot

In Amendment 1: the H38 pilot pairings (`H38.PILOT`), seeds 900 and 901, arms Z, H, P, BP, BP-PN and M0, excluded from the confirmatory data. Used only for the power check and the free checks. Nothing is calibrated on it.

## Power check (required)

In Amendment 1, as H39: `mar.stats.seeds_for_power` on the pilot's per-pairing spread for P1, P3, P5, P5b, P6a, P6b, P6c. Pairings (120) and seeds (4) are fixed by the comparison with H39; the check only marks a prediction DESCRIPTIVE when 120 pairings (or its open cells) are short of 80% power.

## Predictions

H39's predictions, unchanged in quantity, threshold, test and direction. P3's group is the lowest-enjoyment third (H39: e = 0; H39b: e = −1; the same personas).

| ID | Quantity | Unit | Direction and threshold | Test | Alpha | Family | Interval |
|---|---|---|---|---|---|---|---|
| P1 | pleasure, BP − Z | pairing | up: ≥ +0.003, CI above 0 | paired sign-flip, one-sided greater | 0.05 | Holm over BP, H, P, G, A − Z | 95% bootstrap over pairings |
| P1b | unclipped pleasure, BP − Z | pairing | same sign as P1 | sign agreement | – | – | 95% bootstrap |
| P2 | blocks per partner-week while together, H, P, BP − Z | pairing | up: each ≥ +0.10 | paired sign-flip, greater | 0.05 | Holm over the three | 95% bootstrap |
| P3 | share of blocks made by lowest-enjoyment partners, H − Z | pairing (with such a partner) | up: ≥ +0.03 | paired sign-flip, greater | 0.05 | none | 95% bootstrap |
| P4 | share of long-together pair-seeds whose imbalance evens out, BP − Z | pair-seed | no change: within ±0.10 | CI inside ±0.10 | 0.05 | none | Newcombe 95% |
| P5 | extractive partner's credit share, H − P | pairing (exactly one extractive) | up: ≥ +0.05 | paired sign-flip, greater | 0.05 | Holm over P5, P5b | 95% bootstrap |
| P5b | pleasure, P − H, pairings with an extractive partner | pairing | up: > 0, CI above 0 | paired sign-flip, greater | 0.05 | same | 95% bootstrap |
| P6a | long projects started per pair-seed, BP-PN − BP | pairing (with an artist) | up: ≥ +0.20 | paired sign-flip, greater | 0.05 | Holm over P6a, P6b, P6c | 95% bootstrap |
| P6b | projects paid per pair-seed, BP-PN − BP | same | up: ≥ +0.10 | same | 0.05 | same | 95% bootstrap |
| P6c | pleasure, BP-PN − BP | same | not worse: estimate > 0 and CI lower ≥ −0.002 | same | 0.05 | same | 95% bootstrap |
| P7 | week-0 formation, BP − BP-w0 | pairing | down: ≤ −0.10 | paired sign-flip, less | 0.05 | none | 95% bootstrap |

Notes, as in H39: P2 is a manipulation check (no verdict weight); P5 is close to built in (little weight); P5b carries the extractive question; P7 is the research note's consequence, not a test of H39.

**Secondary outcomes (descriptive, no verdict weight), with the direction we expect stated now:**

- S1. Lost liking and trap share are higher in pairings with an extractive partner than without (expected: yes, by construction of the cue; a known-answer check of the measures, not a finding).
- S2. Lost liking and trap share, P − H in pairings with an extractive partner (expected: P lower, if crediting by pleasure given pulls volume away from tolerated blocks; no threshold).
- S3. Makers on (Z) − makers off (M0) on pleasure (expected: not negative once making is chosen against its alternatives; no threshold). This is the H39 finding most likely to be an artifact.

**Which H39 findings survive** (rule fixed now): an H39 finding with a 95% interval that excluded 0 survives if the H39b estimate has the same sign and its interval also excludes 0; it **reverses** if the H39b interval excludes 0 with the opposite sign; otherwise it **does not survive** (H39b interval includes 0). An H39 null (interval including 0) survives if the H39b interval also includes 0. H39's per-pairing rows are not on disk any more, so the comparison is between the two runs' estimates and intervals, not a paired H39b − H39 difference.

## Can every verdict happen? (required)

In Amendment 1, from free checks before the confirmatory run: H39's relabelled-pilot checks rerun on H39b pilot rows (supported, not supported, inconclusive, P5b both ways, P6 both ways, nobody agrees to protect, P1b disagreeing), the open-cell counts (unchanged: the traits other than enjoyment's level are the same hashes), and:

| Clause | Free check |
|---|---|
| making can be zero | known answer K1 below |
| making can be full | known answer K2 below |
| the cost can bind | known answer K3 below |
| trap share can be 0 and above 0 | K5 below |
| lost liking can be 0 and above 0 | K6 below |
| metric sees the mechanism | trace: block values → `makers.week_terms` → `close_week(extra_pleasure)` → `pl`; lost liking and trap counted in `makers.week_start` from the same `block_like` and receiver clocks the pleasure uses |

## Are we measuring what we say? (required)

**Construct cards.**

- **Making** = a partner spending 1 of their 10 weekly time units on a block that gives the other partner (and, for art, both) a fixed amount of modeled liking, while both live together, chosen when its value beats what the agent's own week plan would lose. It does NOT encode skill, learning, quality that varies by maker, buying vs making, making for friends or strangers, co-made activities, or chores that only avoid suffering. Negative enjoyment stands in for effort; it does not encode fatigue or burnout that builds over weeks.
- **Opportunity cost** = the drop in the agent's own summed action utilities for the week when n units are taken away, with the week planned as the world plays it (3 passes, the agent's floor, unit costs), utilities fixed at their start-of-week values. It does NOT encode within-week changes in those utilities after an action, the partner's time (a together session also uses the partner's units; each maker values only their own), the friend's invitations, or requests and gifts (not time uses in this world). It assumes the agent's utilities and the making values are on one scale; they are both the hedonic model's numbers, but nobody checked that a utility of 0.03 and a pleasure of 0.03 mean the same thing. If that assumption is off by a factor, making is over- or under-chosen by that factor.
- **Credit** = money units added to a partner's contribution in the F4 exit split. It does NOT encode thanks, status, guilt or scorekeeping friction, and never pays during the household. "Running tally" means only that the maker's choice sees the credit.
- **Extractive** = a maker whose goods carry a cue that raises the receiver's wanting above liking and sensitizes it, and who decides by the receiver's wanting. It does NOT encode profit, intent, deception or a market.
- **Wanting trap** = a person-week at tolerance ≥ 3 of 4 and sensitization ≥ 9 of 12: the liking of each block is cut by at least 45% and the cue is near full strength. It does NOT encode compulsion, distress, or the person's own verdict; it is a state of the two clocks. **Lost liking** = liking the tolerance clock took away; it does NOT count craving (reported separately as suffering) or time spent.
- **Long project, pleasure given, protection**: as H39's cards.

**Known-answer cases** (tests, before the run):

- K1. A maker with enjoyment 0 and togetherness (care) 0, safe aim, no tally, never makes, whatever the free time.
- K2. A maker with enjoyment +1 and a week with idle units makes at least one block.
- K3. A maker whose every planned unit is worth more than any block (all units booked with high-utility actions) makes nothing under `opportunity`, and makes under `flat_cost` with the same values (the flat cost cannot see what is displaced).
- K4. When the month's bills are unpaid at month end, the planned week keeps paying into bills; making does not take that unit unless a block is worth more by the agent's own valuation.
- K5. A receiver whose extractive partner makes 3 blocks every week reaches the trap state; a receiver of a safe maker never does.
- K6. Lost liking is 0 while the receiver's tolerance stays 0 (one block a week, below the dose of 2), and positive once it rises.
- The four H39 known answers still pass under `flat_cost`.

**A second measure.** For the main outcome, unclipped pleasure beside clipped (as H39). For the wanting trap, two: lifetime liking lost to tolerance and the trap share. If clipped pleasure and the trap measures disagree in a pairing (pleasure near 1 with a high trap share), that is reported, not averaged away.

**Story spot-check (after the run).** Five runs read as 13-week stories with the atlas recorder plus a makers line (blocks, credit, tolerance, sensitization, and now lost liking and trap weeks): Z and BP for p-anchor with p-bargainer at seed 0 (H39's story 1 and 2, the invisible trap), BP-PN for g-11011 with p-host (H39's story 3), BP for g-00010 with p-host (story 4), and A for g-00001 with p-anchor (story 5). Same picks as H39 so the stories compare one to one. Say whether each looks like what the measures claim; a mismatch is a finding. Each must reproduce its stored row.

**Observer sample.** The observer layer on the first 20 confirmatory pairings at seed 0 in M0, Z and BP: the formation decomposition (as H39) plus the making-decision decomposition (value parts against alternative cost, what was displaced).

## Verdict rule

As H39. **H39: supported** iff P1 holds robustly and P1b agrees in sign; **not supported** iff the BP − Z estimate is below +0.003 with the CI's upper end below +0.006, or the estimate is ≤ 0; otherwise inconclusive. **H20a (commitment clause): supported** iff P6a, P6b and P6c all hold. **Extractive question:** P5b. "Holds but CI crosses threshold" is weak support, not a confirmed hold. Predictions marked DESCRIPTIVE in Amendment 1 carry no verdict wording in the summary.

## Not testable by design

Makers-off reproduction and H39 (`flat_cost`) reproduction (pass/fail). K1 to K6. C-gift-at-exit equals C-base+pleasure at exit with the motive off (by construction). S1 for the trap share (0 without an extractive partner by construction).

## Limits stated now

Scripted makers on a fixed rule; three kinds, one value point each; credit only at exit, through F4; one world; the builder wrote the correction and the predictions. The opportunity cost uses start-of-week utilities and one maker's own time. κ and the per-block values were set beside the removed time cost and are carried over, not re-derived.

## Amendments

### Amendment 1 (2026-11-11): the planner, the pilot, power, known answers, "Can every verdict happen?"

Committed before the confirmatory run. No prediction, threshold, test, verdict rule or number in the design changed. Code: `src/mar/makers.py` (`choice="opportunity"`, `WeekPlanner`, `plan_week`, `plan_value`, `opportunity`), `scripts/h39b_makers_rerun.py`, tests in `tests/test_makers.py`.

**The planner changed twice after pilot runs, stated plainly.** Both changes make the plan match how the world actually plays a week; neither touches a number, and neither was chosen by an arm's outcome. They were found by looking at why the pilot did what it did, so they are reported with all three pilots' numbers.

1. *First pilot (`runs/h39b-makers/pilot-naive-plan.jsonl`).* The plan as first written ignored that a together session the partner starts also uses this agent's units. Units the plan called idle were the ones the partner's sessions would use. Fix: the partner's own planned sessions come first in the maker's plan, each worth the maker's own utility of time together (known answer K7).
2. *Second pilot (`pilot-partner-sessions.jsonl`).* The plan held start-of-week utilities fixed, so it planned the same top action three times (three friend visits, three bill payments) and saw 4 to 7 idle units. In the world, the next observation moves after each action (friends and together counts, the week's net income, the bill gap), and the agent picks something else. Fix: `WeekPlanner` recomputes the agent's utilities after each planned action the way the world's next observation would, and drops a spending action when the money for it is gone.

**Known-answer check of the planner against the world itself** (`--fidelity`, `runs/h39b-makers/fidelity.json`; makers off, 10 pilot pairings, seed 900, 52 weeks, 998 partner-weeks together, rollout worlds included). At each week's start we plan each partner's week and compare with the time actions the agent then executes. Fixed utilities: the planned actions match exactly in 6% of partner-weeks. `WeekPlanner` with the partner's sessions: 40%, and it plans 0.34 more units a week than the agent uses. The rest is the choice's ±10% noise, passes spent on requests or gifts, and the partner's units. So the plan slightly overstates what making displaces, which biases H39b toward less making, not more. This is a calibration to an external target (what the world's own agents do), not to any arm.

**The three pilots** (30 pilot pairings, seeds 900 and 901; EXPLORATORY, excluded from the confirmatory data):

| Plan | Z pleasure | M0 pleasure | Z formed at week 0 | M0 formed | blocks per partner-week | blocks in planned-idle units |
|---|---|---|---|---|---|---|
| fixed utilities, partner ignored | 0.896 | 0.942 | 0.10 | 0.55 | 2.25 | 97% |
| plus the partner's sessions | 0.902 | 0.942 | 0.18 | 0.55 | 1.69 | 94% |
| `WeekPlanner` (as run) | 0.909 | 0.942 | 0.23 | 0.55 | 1.90 | 78% |

What I saw, plainly: at every version, makers on sits well below makers off, mainly because far fewer pairs form (0.23 against 0.55). It is lower than H39's fitted point (H39's Z − M0 was −0.014; here −0.033 on the pilot). The observer decomposition of one declined pair (g-11000 with p-wanderer, both safe cooks) shows the household rollout losing rest, friends and money to making. We stop changing the choice here, whatever the confirmatory run shows.

**Known answers** (tests, all pass): K1 to K7 in `tests/test_makers.py`, the four H39 known answers under `flat_cost`, makers-off fingerprints, and H39 `flat_cost` fingerprints (`tests/data/makers_flatcost_fingerprints.json`, pinned from commit 2b8a100 before any change).

**Pilot effects and the power check** (`seeds_for_power`, paired, 80%, alpha 0.05, n_max 256; `runs/h39b-makers/power.json`). Open cells in the 120 confirmatory pairings, unchanged from H39: 59 with exactly one extractive partner, 91 with at least one, 63 with an artist, 84 with a lowest-enjoyment partner.

| Prediction | Pilot effect | Pilot sd | Effect used | Units for 80% | Units available | Status |
|---|---|---|---|---|---|---|
| P1 | −0.0007 | 0.028 | 0.003 | over 256 | 120 | **DESCRIPTIVE** |
| P3 | +0.025 | 0.059 | 0.03 | 33 | 84 | confirmatory |
| P5 | −0.087 | 0.126 | 0.05 | 52 | 59 | confirmatory (little weight) |
| P5b | +0.002 | 0.024 | pilot | over 256 | 91 | **DESCRIPTIVE** |
| P6a | −0.06 | 0.60 | 0.20 | 73 | 63 | **DESCRIPTIVE** |
| P6b | −0.16 | 0.54 | 0.10 | 242 | 63 | **DESCRIPTIVE** |
| P6c | −0.003 | 0.014 | pilot | 172 | 63 | **DESCRIPTIVE** |
| P2, P7 | – | – | – | – | – | confirmatory (P2 a manipulation check); P4 DESCRIPTIVE as in H39 |

Seeds stay 0 to 3 (fixed by the comparison with H39). **So the H39 verdict and the H20a verdict are DESCRIPTIVE again.**

**Can every verdict happen?** (`--reach`, `runs/h39b-makers/reach.json`, on H39b pilot rows.) Reached: H39 supported, not supported and inconclusive; P1b disagreeing; P5b missing (H and P swapped; the pilot itself is weak); P6 and H20a supported (synthetic) and failing (BP-PN = BP); nobody agreeing to protect (trust threshold 2: 0 agreed); P5 failing when extractive = safe (extractive share 0.48 under H, 0.56 under P). H39b measures on the 300 pilot maker runs: 115 made nothing, the most made was 2.4 blocks per partner-week; trap share 0 in 180 runs and above 0 in 120 (never without an extractive partner); lost liking 0 in 117 and above 0 in 183. Metric sees the mechanism: traced as in the prereg table.
