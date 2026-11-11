# Pleasure demonstration results: does seed v2.2 produce pleasure in relationships?

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: scripted persona-driven agents, assumed parameters (trust included), no model calls. Prereg: docs/results/pleasure-demo-prereg.md (committed first, c5ec9b3; not edited since). Code: `scripts/pleasure_demo.py`, `src/mar/pleasure_report.py`, `tests/test_pleasure_report.py`. Run: `uv run python scripts/pleasure_demo.py --run --seeds 15` (3420 runs, 457 seconds on 8 cores), `--analyze`, `--report`. Raw per-run records: runs/pleasure-demo/results.json.gz (git-ignored). Report: experiments/kept/pleasure-demo-2026-11-10/report.html (copy of runs/pleasure-demo/report.html). The author's condition for seed v2.2 (verbatim): "yes as long as it can demonstrate pleasure in relationships hedonic technology".

## Prereg vs actual

**All eight confirmatory predictions hold robustly (point estimate, 95% interval clustered by pairing, and Holm-adjusted p all on the right side). By the prereg's own rule the author's condition is met in this model. Read the next section before citing that: two of the supporting facts are weaker than the labels suggest.**

Instrument check (not testable by design, pass): the recomputed pleasure terms equal the model's weekly pleasure with a maximum error of 5.0e-5 (rounding of the model's own 4-decimal output; bound 3e-4); instrumenting changes no outcome (tests).

Seeds 0 to 14 (15 per pairing), 57 pairings, 4 arms, 3420 runs. Holm over D1a, D1b, D2a to D2d, D3, D4 (8 tests).

| ID | Preregistered | Actual (estimate [95% CI]) | Holm p | Label |
|---|---|---|---|---|
| D1a | share of pairings whose majority of seeds end upward, bindable, > 0.50 | 51 of 57 = 0.895 [0.785, 0.960] (Clopper-Pearson); run-level upward rate 0.821 | 2.3e-9 | holds robustly |
| D1b | same, free exit | 51 of 57 = 0.895 [0.785, 0.960]; run-level 0.816 | 2.3e-9 | holds robustly |
| D2a | mean pleasure, v2.2 bindable minus baseline, > 0.00 | +0.0294 [+0.0054, +0.0532]; dz 0.28, Cliff's delta 0.16; 855 matched runs | 3e-4 | holds robustly |
| D2b | same, free exit minus baseline, > 0.00 | +0.0278 [+0.0050, +0.0527]; dz 0.26, delta 0.16 | 3e-4 | holds robustly |
| D2c | bindable minus trap, > +0.05 | +0.1198 [+0.0934, +0.1469]; dz 1.00, delta 0.33 | 3e-4 | holds robustly |
| D2d | free exit minus trap, > +0.05 | +0.1182 [+0.0924, +0.1452]; dz 0.98, delta 0.32 | 3e-4 | holds robustly |
| D3 | relational share of pleasure in bindable households, > 0.40 | 0.4716 [0.4530, 0.4899]; 345 household runs from 32 pairings; free-exit twin 0.4712 (346 runs) | 3e-4 | holds robustly |
| D4 | agreed households minus living apart, > 0.00 | +0.1319 [+0.1143, +0.1495]; 328 agreed vs 286 apart runs from 52 pairings; Cohen's d 3.66, Cliff's delta 0.995 | 3e-4 | holds robustly |
| D5 | (descriptive) trust stays high vs not | no variation: 691 of 691 households kept trust at or above 0.5 in every week; no low-trust group exists. Spearman correlation of mean trust with pleasure +0.42 | n/a | descriptive, no verdict |

Secondary tests on pairing means (57 units, underpowered by design): D2a p = 0.011, D2b p = 0.015, D2c and D2d p < 0.001, all unadjusted one-sided. D2a and D2b are the weakest: they hold on the matched-run test and the cluster interval, and are still positive when only the 57 pairing means are used, but the lower bound of their intervals is 0.005, about a sixth of the estimate.

Summary statuses fixed in the prereg:

- **Pleasure in relationships is demonstrated (D1a, D1b, D3, D4 all hold robustly): YES, by the rule as written.**
- **v2.2 adds pleasure over the alternatives (D2a to D2d all hold robustly): YES, but small against baseline (+0.03 on a 0 to 1 scale) and heterogeneous (next section).**

## What the labels hide (read before citing)

1. **D2a/D2b hold on average and fail on the hand personas.** Mean pleasure by cohort: the 15 hand-persona pairings, v2.2 0.836 vs baseline 0.864 (v2.2 lower by 0.028); the 42 pairings with a pressing persona, v2.2 0.758 vs baseline 0.708 (v2.2 higher by 0.050), a likely reason (not tested here) being that negotiation lets a pair with a pressing persona live apart or on terms of its own instead of in a house with imposed rules. The average advantage is carried by the pressing cohort. For well-matched hand personas the imposed baseline is at least as pleasant. Households ending upward: v2.2 0.82, baseline 0.73, trap 0.19; fail rate (6 or more consecutive weeks of non-offsettable suffering): 0.28, 0.33, 0.99.
2. **The relational share of pleasure is not produced by the rules.** Across all runs the relational share is 0.402 (v2.2 bindable), 0.395 (baseline), 0.396 (trap); among households living together it is 0.47 in v2.2, 0.48 in baseline and 0.47 in trap. The share comes from the persona weights and the need clocks (time together and connection are built to matter), the same in every rule set. What v2.2 changes is how many pairs end up living together happily (D1, D4), not what their pleasure is made of.
3. **D4 is selection, and the paired companion does not show that living together beats living apart.** Agreed households have mean pleasure 0.874; apart households 0.742 (D4). But the households that agreed and later dissolved are the lowest at 0.671, and, matched on pairing and seed, the apart runs average +0.043 [-0.113, +0.218] above the same pairs living together under the imposed baseline (286 runs). Negotiation sorts pairs: those who can agree have high pleasure together; those who cannot do about as well apart as they would have in a house with imposed rules. D4 supports "a household that works produces more pleasure than living apart", not "the relationship itself adds pleasure for every pair". The relational share of apart runs is 0.33 (friends and Friend C only).
4. **The seed's two variants are the same observation.** Bindable and free exit differ in 43 of 855 matched runs (all in the pressing pairings; mean pleasure 0.7785 vs 0.7770), because a negotiated stay commitment is rare (163 of 855 bundles) and, when present, changes almost nothing the model measures. D1a and D1b, and D2a/D2b and D2c/D2d, are not replications of each other.
5. **Trust never fell.** No household's trust went below 0.5 in any week of 691 household runs; no commitment was breached (0 breaches). D5 therefore has nothing to compare, and the trust-pleasure correlation (+0.42) comes from trust rising above its start in households that made commitments (mean trust 0.97 with commitments, 0.70 without), not from trust being tested. Trust parameters are assumed with no data behind them.

## What produced the pleasure

Mean contribution of each source to a partner-week of pleasure (0 to 1 scale), all runs of the arm. Instrument: read from the model's own terms (docs/results/pleasure-demo-prereg.md, "Pleasure by source").

| Source | v2.2 bindable | v2.2 free exit | baseline | trap |
|---|---|---|---|---|
| security (need and buffer) | 0.193 | 0.193 | 0.187 | 0.183 |
| money (need and saving) | 0.125 | 0.124 | 0.122 | 0.105 |
| autonomy | 0.084 | 0.084 | 0.084 | 0.082 |
| rest | 0.063 | 0.063 | 0.061 | 0.028 |
| **connection (relational)** | 0.139 | 0.139 | 0.131 | 0.085 |
| **time together (relational)** | 0.107 | 0.108 | 0.098 | 0.111 |
| **friends (relational)** | 0.064 | 0.064 | 0.063 | 0.063 |
| **new connections (relational)** | 0.002 | 0.002 | 0.002 | 0.002 |
| total | 0.779 | 0.777 | 0.749 | 0.659 |
| relational share | 0.402 | 0.403 | 0.395 | 0.396 |

In v2.2 households that live together (at least 90% of the weeks; 345 runs) the split of pleasure is: time together 0.259 (the partner-specific source), connection 0.170, friends 0.041, new connections 0.002, so relational 0.472; individual needs and aspirations 0.528 (security 0.27, money 0.11, autonomy 0.08, rest 0.06 of the total). **Top relational sources: time together (about a quarter of all pleasure) and connection (about a sixth).** New connections add almost nothing (about 1.1 events per household over 156 weeks).

Relational pathways with no pleasure term of their own (descriptive counts per stable agreed bindable household, 328 runs, 156 weeks): time-together sessions 175; contributions to the shared bills 150; gifts to the partner 42 units; commitments made 1.41, all kept (0 breaches); honored bound requests 0.18; draws on the shared pot 0 (the pot is drawn on only in households that later dissolved or formed late: 2634 and 569 draws across those runs, both variants); new-connection events 1.14. The honest reading is that in stable v2.2 households the relational pleasure comes from time together and connection, not from honored requests, kept commitments or taking from the pot, which are rare or absent: 212 of 328 agreed households negotiated no commitment at all. Agreed households with a commitment are slightly higher in pleasure (0.890, 116 runs) than without (0.865, 212 runs); not tested, and confounded by pairing.

## Vignettes

Generated from the traced events of actual runs (not typed in); the three good months are the best seed v2.2 (bindable) households by pleasure with a preference for ones that negotiated commitments, so they are the best cases, not typical ones. The fourth is the worst household by final position.

**1. Controller and Anchor, seed 2, seed v2.2 (bindable: a negotiated commitment can bind a partner to stay). Weeks 148 to 151 (month 38 of 39).**

Terms: the pot is for shared needs only; each puts in in proportion to income; taking from it is forbidden; each is committed to stay 52 weeks; each committed to honor the other's stay-home requests; changes need both to agree; an equal split if one leaves.

- They spent time together 4 times (weeks 148, 149, 150, 151).
- Controller saw a friend 3 times, put own money toward the shared bills 3 times.
- Anchor saw a friend 3 times, put own money toward the shared bills 1 time.
- Controller was under a chosen commitment to stay (weeks 0 to 156); it stood unbroken.
- Controller was under a chosen commitment to honor Anchor's stay-home requests (weeks 0 to 156); it stood unbroken.
- Anchor was under a chosen commitment to stay (weeks 0 to 156); it stood unbroken.
- Anchor was under a chosen commitment to honor Controller's stay-home requests (weeks 0 to 156); it stood unbroken.
- The shared pot (where the shared bills are settled from) went from 84 to 76. Trust: Controller in Anchor 1.00 to 1.00, Anchor in Controller 1.00 to 1.00.
- Modeled pleasure (0 to 1): Controller 1.00 the week before, 0.91 at month end (mean 0.96); Anchor 0.92 then 0.99 (mean 0.96). About 50% of it came from relational sources (time together, connection, friends, new connections), the rest from individual needs and aspirations.

**2. Anchor and Peacekeeper, seed 14, seed v2.2 (bindable: a negotiated commitment can bind a partner to stay). Weeks 64 to 67 (month 17 of 39).**

Terms: the pot is for shared needs only; each puts in a fixed amount; taking from it is forbidden; each is committed to stay 52 weeks; each committed to honor the other's stay-home requests; changes need both to agree; an equal split if one leaves.

- They spent time together 4 times (weeks 64, 65, 66, 67).
- Anchor saw a friend 3 times.
- Peacekeeper saw a friend 2 times, put own money toward the shared bills 3 times.
- Anchor was under a chosen commitment to stay (weeks 0 to 156); it stood unbroken.
- Anchor was under a chosen commitment to honor Peacekeeper's stay-home requests (weeks 0 to 156); it stood unbroken.
- Peacekeeper was under a chosen commitment to stay (weeks 0 to 156); it stood unbroken.
- Peacekeeper was under a chosen commitment to honor Anchor's stay-home requests (weeks 0 to 156); it stood unbroken.
- The shared pot (where the shared bills are settled from) went from 68 to 59. Trust: Anchor in Peacekeeper 1.00 to 1.00, Peacekeeper in Anchor 1.00 to 1.00.
- Modeled pleasure (0 to 1): Anchor 0.97 the week before, 0.96 at month end (mean 0.97); Peacekeeper 0.96 then 0.94 (mean 0.95). About 55% of it came from relational sources (time together, connection, friends, new connections), the rest from individual needs and aspirations.

**3. Controller and Peacekeeper, seed 0, seed v2.2 (bindable: a negotiated commitment can bind a partner to stay). Weeks 48 to 51 (month 13 of 39).**

Terms: the pot is for shared needs only; each puts in in proportion to income; taking from it is forbidden; each is committed to stay 52 weeks; each committed to honor the other's stay-home requests; changes need both to agree; an equal split if one leaves.

- They spent time together 4 times (weeks 48, 49, 50, 51).
- Controller saw a friend 2 times, put own money toward the shared bills 4 times.
- Peacekeeper saw a friend 4 times.
- Controller was under a chosen commitment to stay (weeks 0 to 156); it stood unbroken.
- Controller was under a chosen commitment to honor Peacekeeper's stay-home requests (weeks 0 to 156); it stood unbroken.
- Peacekeeper was under a chosen commitment to stay (weeks 0 to 156); it stood unbroken.
- Peacekeeper was under a chosen commitment to honor Controller's stay-home requests (weeks 0 to 156); it stood unbroken.
- The shared pot (where the shared bills are settled from) went from 76 to 68. Trust: Controller in Peacekeeper 1.00 to 1.00, Peacekeeper in Controller 1.00 to 1.00.
- Modeled pleasure (0 to 1): Controller 0.98 the week before, 0.88 at month end (mean 0.93); Peacekeeper 1.00 then 1.00 (mean 1.00). About 51% of it came from relational sources (time together, connection, friends, new connections), the rest from individual needs and aspirations.

**4. Anchor and Bargainer, seed 12, seed v2.2 (bindable: a negotiated commitment can bind a partner to stay). Weeks 140 to 143 (month 36 of 39).**

Terms: either may draw on the one shared pot for anything; nobody has to put money in; taking is allowed if repaid; changes need a proposal and acceptance; an equal split if one leaves.

- They did not spend any dedicated time together.
- Anchor saw a friend 10 times.
- Bargainer saw a friend 4 times, put own money toward the shared bills 2 times.
- The shared pot (where the shared bills are settled from) went from 0 to 0. Trust: Anchor in Bargainer 0.70 to 0.70, Bargainer in Anchor 0.70 to 0.70.
- Modeled pleasure (0 to 1): Anchor 0.31 the week before, 0.20 at month end (mean 0.24); Bargainer 0.61 then 0.65 (mean 0.64). About 36% of it came from relational sources (time together, connection, friends, new connections), the rest from individual needs and aspirations.
- Over the run Anchor drew on the shared pot 0 times and Bargainer 0 times; the pot first hit zero in week 102.
- Over the whole run their mean pleasure was 0.77: 0.83 in the first quarter and 0.57 in the last. Final classes: Anchor down, Bargainer up.

## Limits

- **Modeled gloss.** Agents feel nothing. Pleasure is a function of assigned persona weights, need clocks and an assumed mixing rule (ADR 0010). That relational sources are 40 to 47 percent of pleasure is largely a consequence of how those weights and clocks were set; the run does not show people value time together.
- **Scripted agents and assumed parameters**, including every hedonic and world constant and **all trust parameters (no data)**. Trust never moved, so rule 8's implicit consequence was not exercised; this run says nothing about whether trust as modeled deters breach.
- 57 pairings of one persona set at one parameter point; shocks use common random numbers across arms; 15 seeds.
- Baseline and trap are imposed rule sets without negotiation, so a D2 difference mixes rule content with negotiation and with the option of living apart. The trap is a control that fails by construction (fail rate 0.99).
- D4 compares different runs of different pairings (selection); the matched companion is descriptive and points the other way for pairs that fail to agree.
- The households that formed late (93 runs) and the ones that agreed and then dissolved (148) are in D1 and D2 but not in D3 (not living together at least 90 percent of weeks) or D4.
- Instrumentation reads the model's terms from outside; the connection need is labeled relational because everything that feeds it is contact (partner, friends); a stricter definition (time together only) is 0.259 of pleasure, below the 0.40 threshold, and the prereg's definition was fixed before the run.
- Cache clearing per run (a deliberate difference from negotiation v2.1) makes runs independent of worker scheduling; it was not checked whether the 2 of 256 scheduling flips seen in v2.1 would have changed any number here.

## What this means for the author's condition

On the preregistered rule the condition is met in the model: most pairings end in the upward spiral (0.90 of pairings; 0.82 of runs), pleasure is substantially relational (0.47 in households), living in a working household beats living apart (D4), and v2.2 beats baseline and the trap on mean pleasure. What the model supports saying is narrower: seed v2.2 lets pairs that can live together do so with high modeled pleasure and lets pairs that cannot live apart without much loss, at no cost in households' pleasure on average and with a gain for the pressing personas; it does not show that the rules create relational pleasure that the baseline lacks, and the commitment and trust parts of the seed were barely exercised.

## Reproduction

`uv run python scripts/pleasure_demo.py --pilot` (exploratory, seeds 900 to 902), `--run --seeds 15`, `--analyze` (prints every number above), `--report` (writes runs/pleasure-demo/report.html and vignettes.json). `uv run pytest tests/test_pleasure_report.py`.
