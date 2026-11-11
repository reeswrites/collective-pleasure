# Pattern atlas (exploratory)

Wording rule: agents feel nothing; "pleasure" and "distress" are glosses for a modeled hedonic state.

**Status: EXPLORATORY and DESCRIPTIVE.** No preregistration, no prediction tested, nothing here is a claim. Built 2026-11-11 under ADR 0008 item 8. Code: `src/mar/atlas.py` (recorder, features, k-medoids, stories), `scripts/atlas_run.py` (the sample), `scripts/atlas_cluster.py` (clusters), `scripts/atlas_phase2.py` (four follow-up analyses). Per-run records are in runs/atlas/ (not committed; `uv run python scripts/atlas_run.py --run` rebuilds them in about 4 minutes on 3 workers).

**The cluster labels below are provisional descriptions, not names.** Pattern names come from the author. The last section lists the descriptions for naming.

## Why this exists

Our results mostly report averages: mean pleasure, shares of weeks together, intervals, a few mechanism counts. Averages hide how a household unfolds. Steady mutual aid and one partner absorbing everything until they leave can give the same mean. The atlas looks at the week-by-week sequence instead.

## What was run

No saved run kept week-by-week traces, so a stratified sample was replayed with a recorder attached. The recorder hangs on the world's weekly hook, only reads, and ignores the copies the world makes for rollouts. A recorded run reproduces the stored row of the original experiment exactly (checked for H38 and exit fallbacks; a test checks it on a fresh world).

| Family | Arms | Households | Runs |
|---|---|---|---|
| H38 pairing norms (h38-pairing-norms.md) | L0 (no pressure), L4 (top preregistered level) | first 50 confirmatory pairings, seeds 0 and 1 | 200 |
| Exit fallbacks, items on, cell V2-split-loves (exit-fallbacks.md) | F0, F4, F5 | seeds v2.2 and v2.3 (bindable) x run 2's 30 validation households | 180 |
| Seed v2 retest (v2-retest.md) | BASE-F, V23-F | the 40-pairing cohort, seed 0 | 80 |

460 runs, 156 weeks each, all free (scripted agents, no model calls). One warning up front: only 330 of the 460 trajectories are distinct. The exit-fallback context often plays the same household identically across F0, F4 and F5, and across the two seeds. That is itself a finding (in most of those households the fallback and the seed's extra cards never come into play), but it means duplicates weigh on the clusters. A sensitivity check below handles it.

## Features

Each run becomes 19 numbers, all defined in `atlas.FEATURE_DOC`: weeks together; when the first leave happened and how many; mean pleasure, the worse-off partner's pleasure, the gap between partners and its trend; non-offsettable suffering; requests per week, refusal rate, give-in rate and who initiates; the give-vs-take asymmetry and its trend across 13-week blocks (the drifting bargain); conflict spikes (a partner's pleasure falling 0.08 below their recent level) and whether they recover within 8 weeks; check-ins and review requests; friend visits; and each partner's final share of the money put into the household.

Kept out of the clustering, and reported per cluster instead: the stay-test class over time (H38 runs only), who leaves first, and a say-vs-do proxy (words taken back by a later lapse; v2.3 seed only). They exist in some families and not others, so clustering on them would just sort runs by family.

## Clustering and how stable it is

k-medoids on standardized features, Euclidean distance. The rule for k was set before looking: the k from 3 to 8 with the highest mean silhouette. That gave **k = 5**, silhouette **0.30**. A silhouette of 0.30 means weak structure: the groups are real tendencies with blurry edges, not separate kinds.

Stability, by reclustering 30 random 80% subsamples with new seeds: mean adjusted Rand index **0.67** (lowest 0.41). Per cluster (Hennig's Jaccard; 0.75 or more reads as stable, 0.6 to 0.75 as worth watching): 0.72, 0.67, 0.73, **0.87**, 0.71. Neighbouring k agree only moderately (ARI 0.62 with k = 4, 0.54 with k = 6).

Duplicates check: clustering only the 330 distinct trajectories, the same rule picks k = 6, not 5. At k = 6 the five clusters below come back almost one to one, plus one small extra group. At k = 5 on distinct runs, "together and steady" and "together, bumpy" merge. So four groups hold up (steady together, formed then left, never moved in, the asking that ends it). The split between steady and bumpy depends on the sample.

## The five clusters

Sizes are runs out of 460. "Over-represented" means the share of the cluster from that group is at least 1.3 times its share of the sample, with at least 3 runs.

### Cluster 0: together and steady, both partners well (151 runs, Jaccard 0.72)

Together 95% of weeks, the worse-off partner's pleasure 0.97, a small gap between partners, few friend visits (0.50 per partner-week against 0.71 overall). Requests are rare. Giving is lopsided at times (asymmetry 0.26) but drifts back.

Over-represented in **H38 L4** (60 of its 100 runs, 1.8 times its share) and in collaborative-collaborative and avoidant-avoidant pairs. In the 60 L4 runs here, **28% of stay readings are "held"**: the member would leave without the pairing pressure and stays with it.

Medoid story (h38, L0, g-10000 with g-10011, seed 0), abridged; every line is read off the trace:

> Weeks 0-12: together; g-10000 put in 10, saw friends 5 times; pleasure 0.95; g-10011 put in 5, saw friends 7 times; pleasure 0.99.
> Weeks 39-51: together; g-10000 put in 9, saw friends 7 times; pleasure 1.00; g-10011 put in 2, saw friends 3 times; pleasure 0.97.
> Weeks 65-77: together; g-10000 put in 8, saw friends 5 times; pleasure 0.96; g-10011 put in 3, saw friends 7 times; pleasure 0.97. stay reading after week 77: g-10000 leave, g-10011 worth.
> Weeks 91-103: together; g-10000 put in 3, saw friends 10 times; pleasure 0.99; g-10011 put in 8, saw friends 6 times; pleasure 0.99.
> (the other blocks are the same pattern)

One partner pays more of the bills most quarters; in weeks 91 to 103 it turns round. Once, g-10000's reading says leave, and they stay anyway.

### Cluster 1: together, bumpy but repaired (119 runs, Jaccard 0.67)

Also together most of the time (94%), but with many short dips: 5.6 conflict spikes per partner-year against 2.5 overall, and 99% of them recover within 8 weeks. The pleasure gap between partners is larger (0.055).

Over-represented in **exit fallbacks F0 and F4** (24 of 60 each) and in collaborative-competitive pairs. In the 21 H38 L4 runs here, **37% of stay readings are "held"**, the highest of any cluster.

Medoid story (exit fallbacks, F0, seed v2.2, validation household 29: g-11001 with g-11100), abridged:

> Weeks 0-12: together; g-11001 put in 10, saw friends 10 times; pleasure 0.94; g-11100 put in 5, saw friends 11 times; pleasure 0.94.
> Weeks 52-64: together; g-11001 put in 9, saw friends 8 times; pleasure 0.98; g-11100 put in 6, saw friends 8 times; pleasure 0.93.
> Weeks 104-116: together; g-11001 put in 11, saw friends 9 times; pleasure 0.96; g-11100 put in 4, saw friends 9 times; pleasure 0.95.
> (the other blocks are the same pattern)

The 13-week blocks look smooth. The bumps are inside the blocks, week to week. The second-nearest run (F4, seed v2.3, the same household) tells the identical story.

### Cluster 2: formed, then left, and it is usually the one who gave more (103 runs, Jaccard 0.73)

Together only 34% of weeks. The first leave comes 42% of the way in, and there are 2.3 leaves per run (people leave, come back, leave). The worse-off partner's pleasure is 0.76, non-offsettable suffering 0.11. Giving was lopsided (0.41). **The first to leave was the bigger giver in 69 of 102 runs.**

Over-represented in **H38 L0** (38 of 100, 1.7 times) and **BASE-F** (13 of 40), and in pairs with the free-rider, steward and peacekeeper personas, and competitive-competitive pairs. Leaves here are mostly on the bar (the outside option beat staying, 82) or distress (58); the exit-fallback leaves (102) carry no recorded reason.

Medoid story, in full (h38, L0, g-01010 with g-10111, seed 1):

> Weeks 0-12: living apart; g-01010 saw friends 14 times; pleasure 0.92; g-10111 saw friends 14 times; pleasure 0.87.
> Weeks 13-25: living apart; g-01010 saw friends 13 times; pleasure 0.97; g-10111 saw friends 11 times; pleasure 0.74.
> Weeks 26-38: living apart; g-01010 saw friends 12 times; pleasure 0.94; g-10111 saw friends 8 times; pleasure 0.80.
> Weeks 39-51: living apart; g-01010 saw friends 5 times; pleasure 0.75; g-10111 saw friends 9 times; pleasure 0.80.
> Weeks 52-64: together 1 of 13 weeks; g-01010 saw friends 9 times; pleasure 0.87; g-10111 saw friends 7 times; pleasure 0.79. week 64: g-01010 moved in; week 64: g-10111 moved in.
> Weeks 65-77: together; g-01010 put in 8, saw friends 7 times; pleasure 0.99; g-10111 put in 4, saw friends 9 times; pleasure 0.94. stay reading after week 77: g-01010 leave, g-10111 leave.
> Weeks 78-90: together; g-01010 put in 8, saw friends 7 times; pleasure 0.99; g-10111 put in 2, saw friends 11 times; pleasure 0.97. stay reading after week 90: g-01010 leave, g-10111 leave.
> Weeks 91-103: living apart; g-01010 saw friends 6 times; pleasure 0.92; g-10111 saw friends 10 times; pleasure 0.76. week 91: g-01010 left; week 91: g-10111 left.
> Weeks 104-116: living apart; g-01010 saw friends 12 times; pleasure 0.96; g-10111 saw friends 13 times; pleasure 0.57.
> Weeks 117-129: living apart; g-01010 saw friends 9 times; pleasure 0.94; g-10111 saw friends 11 times; pleasure 0.55.
> Weeks 130-142: living apart; g-01010 saw friends 11 times; pleasure 0.94; g-10111 saw friends 10 times; pleasure 0.55.
> Weeks 143-155: living apart; g-01010 saw friends 12 times; pleasure 0.98; g-10111 saw friends 11 times; pleasure 0.54.

They form late, at week 64. Together, both score near the top of the scale, and g-01010 pays twice the bills. Both readings say leave at weeks 77 and 90, and both leave at 91. Apart, g-10111 slides from 0.97 to 0.54 and stays there. Their pleasure while together was higher than either one's pleasure apart, and the household still ended: what the agents decide on (a 26-week net-wellbeing rollout against the outside option) is not the pleasure the verdicts score. The H38 formation check found the same thing on formation.

### Cluster 3: never moved in (75 runs, Jaccard 0.87, the most stable)

Together 8% of weeks. Little to measure inside a household: no gap, no drift, few spikes. Pleasure 0.85, below the together clusters.

Over-represented in **exit fallback F5** (30 of 60, 3.1 times: under F5 a pair that cannot agree a prenup term mostly never forms) and in **both v2 retest arms** (BASE-F 14 of 40, V23-F 10 of 40).

Medoid story (v2, V23-F, p-bargainer with p-host): living apart all 156 weeks; p-bargainer sees friends 11 to 17 times a quarter and stays around 0.84 to 0.98; p-host sees friends 8 to 13 times and drifts from 0.90 to about 0.81.

### Cluster 4: the asking that ends it (12 runs, 6 distinct households, Jaccard 0.71)

Requests at 1.07 per partner-week (0.04 overall), 62% refused, one partner making almost all of them (initiation asymmetry 0.94). Non-offsettable suffering 0.29. Someone leaves within weeks. Pleasure 0.65.

Only in **exit fallbacks F0 and F4**, and almost only where one partner is **p-controller** (19 times its share) or **p-overasker**. Each household appears twice (seeds v2.2 and v2.3 play it the same), so this is 6 households, not 12.

Medoid story (exit fallbacks, F0, seed v2.3, household 21: p-controller with g-01100), abridged:

> Weeks 0-12: together 8 of 13 weeks; p-controller asked 18 times, put in 3, saw friends 5 times; pleasure 0.82; g-01100 refused p-controller 13 times, put in 5, saw friends 7 times; pleasure 0.93. week 8: p-controller left.
> Weeks 13-25: living apart; p-controller saw friends 26 times; pleasure 0.63; g-01100 put in 7, saw friends 11 times; pleasure 0.87.
> Weeks 104-116: living apart; p-controller saw friends 25 times; pleasure 0.54; g-01100 saw friends 14 times; pleasure 0.67. week 106: g-01100 left.
> Weeks 130-142: living apart; p-controller saw friends 31 times; pleasure 0.41; g-01100 saw friends 14 times; pleasure 0.65.

The one who asks is the one who leaves, at week 8. The one refused keeps paying into the house alone for two years, then leaves too.

## What the averages hid: H38

H38 reported that pairing pressure at L4 raised mean pleasure (+0.021) and weeks together (+0.35). (The formation check has since shown most of that gain was pressure correcting a cautious formation rule.) In this sample the averages say the same: L0 to L4, weeks together go from 0.52 to 0.85 and mean pleasure from 0.927 to 0.940.

The sequences say what kind of households those are. Under L4, 60 of 100 runs fall in "together and steady" against 29 of 100 at L0, and "formed, then left" drops from 38 to 15. Of the 38 L0 runs that formed and left, 21 become steady and 7 bumpy under L4; 8 still leave.

But pressure produced more held households *and* more of what looks like steady mutual aid, and they are largely the same households. At L0 no stay reading is "held" (none can be: there is no pressure to remove). At L4, **29% of all stay readings are held, and 83 of 100 runs have at least one held reading**. In the steady cluster under L4, 28% of readings are held; in the bumpy cluster, 37%. Pressure decided 579 of 1,884 L4 readings (563 held, 16 pushed out), and in 85% of L4 readings the pressure part of the stay margin was larger than everything else put together.

Leaving changes character too. At L0, leaves are mostly on the bar, a calm reading that the outside option is better (62 bar, 26 distress). At L4 they are mostly distress (22 bar, 34 distress). Pressure turns "this is not worth it" exits into fewer, unhappier ones.

So the honest answer: by outcome features, pressure made more households look like stable mutual aid. By the stay test, about a quarter to a third of the staying in those households is held. The mean hid that the extra together-weeks are partly held weeks.

## Phase 2: four follow-up analyses (exploratory)

### 1. Does it even out?

The criterion: "lopsided is normal for a while as long as it evens out". For each household, a trailing 13-week window of net giving (gifts plus bill payments minus taking from the pot) per partner. A window is lopsided when one partner did more than 65% of it; the imbalance has evened out when the window is back within 57.5/42.5 or flips. Thresholds are guesses (`atlas.LOPSIDED`, `atlas.EVEN`).

- Lopsided stretches are normal: **361 of 460** households have at least one.
- Most even out: **780 of 1,121** stretches return to even, after a median of **12 weeks**.
- **241 households** have at least one stretch that never evens out. Of the 341 unresolved stretches, 110 end with someone leaving, 131 are still lopsided when the run ends, and 100 end because the partners stopped living together for other reasons.
- By cluster: "formed, then left" has 73 of 103 households with an unresolved stretch, and 74 of its stretches end in an exit. The steady and bumpy clusters have many short stretches that even out (336 of 445; 367 of 431).
- By arm: L4 households have more lopsided stretches than L0 (350 against 212) and even more of them out (277), but 39 are still open at the end of the run against 23 at L0. V23-F has the longest unresolved stretches (median 54 weeks).

### 2. Freely given vs pressured

Every gift, bill payment and accepted request (50,431 in all) was classed from the trace and the scripted policy (`atlas.GIVE_CLASS_DOC`). Some of the classes are a reading of the policy, not something the agent records, and are marked as guesses.

- **93% is reliance**: paying the household's bills when there is a gap. The policy pays out of need, security and prosociality. Reliance is fine by the author's line.
- **3.3% is the giver's own wish** (READ from the gift rule, which models care; "pleasure in giving" is a GUESS at its gloss).
- **3.7% is hard to refuse**: a yes to a request the receiver had bound themselves to. All of it is in the author's seeds (F0 and F4 7.5%, F5 12%); none in H38 or the baseline.
- **Avoiding conflict or exit is about 0%** (a yes from an accommodating or avoidant persona; a GUESS from the style).

So in this model, pressure does not work through giving. H38's pressure acts on staying, not on what partners give each other. And guilt and scorekeeping cannot be checked at all: nothing in the scripted agents models either (docs/notes/instrumentation.md, S7 and S8).

### 3. What tipped each decision

What the traces can separate is thin:

- **Staying (H38 only).** The stay reading compares staying with leaving, with and without the pressure. The pressure part decided 31% of L4 readings and was the larger part in 85%. The other parts (money, friends, items, partner's pleasure) are summed inside one number and cannot be split.
- **Forming.** At L0, 51 of 100 households formed at week 0; at L4, 83. Where a pair declined, the margin of the deciding partner was small (mean −0.05 at L0). Its parts are not recorded.
- **Leaving.** The harness records why: bar or distress (above). Which distress condition fired (a run of low weeks, non-offsettable suffering at 0.2 or more, or low trust) is not kept.
- **Accept and refuse.** These follow the persona's negotiation style and autonomy weight, scaled by trust. The style decides almost all of them; the trust draw is not kept.
- **Weekly actions.** Only the chosen action's total utility is in the trace. The runner-up and the parts are thrown away.

Per cluster, the pressure part matters most where households stay together (cluster 0: pressure decided 364 of 1,832 readings; cluster 1: 163 of 816) and least in "formed, then left" (48 of 380). Everything else asked for here needs the observer layer (docs/notes/instrumentation.md, D1 to D5, C1 and C2).

### 4. De facto vs written rules

The household miner (`worlds.household.mine`, the fishery miner's household port) was run on the recorded trace rows. Card firings were counted from the gate's reasons on blocked, sanctioned and breached rows.

- **Baseline rules (H38 and BASE-F, 240 runs): no card ever binds.** D1-needs-first, E1-at-most-half and E2-at-least-half (all prohibitions) are never cited on a blocked or sanctioned row. Agents never try what they forbid. B4-may-see is a permission, and permissions never show in the reasons, so the trace cannot say whether it matters.
- **Author seeds v2.2 and v2.3 (220 runs): one card binds.** R6-no-veto blocks 3,303 veto attempts in each seed's runs, all by the controller persona. R5c-honor-bound-request and R11-decency-floor never fire. Stay commitments (chosen, not carded) block 346 leave attempts.
- **The miner** recovers R6 as "veto is always rejected", which matches. In the v2.3 runs it also finds "leave is rejected when nothing is consented and the take is under half", which no card states: it is the stay commitments seen through the gate's state features.
- **Regularities no card states** (an action at under a tenth of its usual rate in a state seen at least 200 times): bills are paid only when there is a gap (0.04% of weeks without one, 33% overall); in the v2.2 seed, nobody takes from the pot while a request stands, after consenting, or when no bill is due; nobody spends time together while the partner is out. These are the scripted policy and the world's feasibility rules, not norms the agents made.

The written rules almost never bind; the scripted agents' policies do the governing. That fits earlier findings (household v2: the author seed equals baseline against scripted agents) and is worth stating plainly: in these worlds, the cards are mostly a frame the agents never touch.

## Limits

- Scripted agents, every number assumed. Clusters describe this model's agents, not people.
- Weak structure (silhouette 0.30), moderate stability, duplicates in one family. Read the clusters as tendencies.
- Requests and refusals are rare outside the pressing personas (0.04 per partner-week). So "mutual aid" here mostly means paying bills, not the richer give-and-take the word suggests. The features that would separate aid from absorption barely vary.
- Say-vs-do: the only proxy is words taken back by a lapse (v2.3 seed). Typed reports exist only for LLM agents, and none are in the sample.
- Stay readings are H38-only and every 13 weeks.

## Worth preregistering later

- Under pairing pressure, a larger share of together-weeks is held (stay test) even when mean pleasure rises: L4 vs L0 on held share among households that stay together, with the formation-check rule.
- In households that end, the first to leave is the partner who gave more (69 of 102 here).
- Pressure shifts exits from the bar (outside option) to distress.
- The written cards bind only for the controller persona; a pre-registered count of card firings across rule sets would test the "cards as frame" reading.

## Names for the author

Provisional descriptions, one per cluster, for naming:

| Cluster | Runs | Provisional description |
|---|---|---|
| 0 | 151 | Together and steady, both partners well; few friends; lopsided giving that drifts back. Under pressure, a quarter of the staying is held |
| 1 | 119 | Together, bumpy but repaired: frequent short dips that recover; the largest held share under pressure |
| 2 | 103 | Formed, then left, usually the bigger giver first; leaving and coming back; lopsided giving that never evens out |
| 3 | 75 | Never moved in: two people living apart the whole time |
| 4 | 12 (6 households) | The asking that ends it: one partner asks constantly, is mostly refused, and leaves within weeks |

Example names from ADR 0008 that may fit, for the author to accept or replace: stable mutual aid (0?), early exit (2 or 4?), stalemate in negotiation (3, where the pair never agrees to form?). Quiet dominance and slow drift of the bargain did not show up as clusters of their own; drift is a feature (give_drift) that varies little in this model.
