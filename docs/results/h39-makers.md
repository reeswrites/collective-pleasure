# H39 makers: results

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Status: run once on 2026-11-11, after the preregistration ([h39-makers-prereg.md](h39-makers-prereg.md), commit a6314a7; Amendment 1, commit fefb085) and the code (823e43a). Design: [h39-makers-design.md](h39-makers-design.md). 13 arms × 120 pairings × 4 seeds = 6,240 runs, 2,779 s on 3 workers. Scripted agents, no model calls, every number ASSUMED. By the power check the H39 and H20a verdicts are DESCRIPTIVE: the verdict rules are applied below, but the runs were too few to carry verdict wording for the headline comparisons.

## In one paragraph

**Crediting making did not raise pleasure here. It lowered it a little, and the model's making itself lowered it more.**

- **Every crediting rule with a running tally lowers pleasure** by 0.005 to 0.006 against making counting for nothing (C-zero). The cause is the tally's pull on behaviour, not the exit split: counting making only at exit (C-gift-at-exit) changes pleasure by −0.0004.
- **Makers on, with nothing credited, sit 0.014 below makers off.** Fewer pairs form (0.47 against 0.52 at week 0) and pairs spend fewer weeks together (0.38 against 0.55). Making as modeled costs more time together than it gives back.
- **Negotiated protection of long projects did nothing measurable** (H20a's commitment clause): projects started −0.01 per pair-seed, paid −0.04.
- **Crediting by volume did not reward extractive makers more than crediting by pleasure given** (H − P extractive credit share −0.026). P5 missed.
- **The suffering-weight rule forms far fewer households than deciding on pleasure alone** (0.43 against 0.78 at week 0), as the research note predicted.

So H39's claim is **not supported** in this model, with the H39 verdict marked descriptive (P1 was underpowered for a +0.003 margin; the estimate is negative with its interval below 0, so more runs would not have turned it).

## Headline numbers per crediting arm

Means over 120 pairings × 4 seeds. Pleasure is clipped weekly pleasure over both partners and 156 weeks.

| | M0 (makers off) | Z C-zero | H C-hours | P C-pleasure | BP C-base+pleasure | G C-gift-at-exit | A C-agreed |
|---|---|---|---|---|---|---|---|
| pleasure (primary) | 0.933 | 0.919 | 0.913 | 0.914 | 0.914 | 0.919 | 0.913 |
| unclipped pleasure | 1.009 | 0.983 | 0.970 | 0.972 | 0.971 | 0.982 | 0.969 |
| net | 0.744 | 0.709 | 0.697 | 0.703 | 0.700 | 0.708 | 0.698 |
| formed at week 0 | 0.52 | 0.47 | 0.45 | 0.43 | 0.43 | 0.47 | 0.42 |
| share of weeks together | 0.55 | 0.38 | 0.34 | 0.35 | 0.35 | 0.38 | 0.35 |
| blocks per partner-week together | – | 1.20 | 1.42 | 1.41 | 1.39 | 1.18 | 1.42 |
| F4 share moved by credit ≥ 0.05 | – | 0 | 0.52 | 0.50 | 0.53 | 0.54 | 0.50 |

Each arm against C-zero, paired by pairing, 95% bootstrap interval (Holm over the five, one-sided "greater"):

| Arm − Z | Pleasure | Unclipped | Weeks together | Blocks per partner-week |
|---|---|---|---|---|
| BP (the author's lean) | **−0.005 [−0.0075, −0.0026]** | −0.012 [−0.017, −0.007] | −0.039 | +0.19 [+0.13, +0.26] |
| H | −0.006 [−0.009, −0.004] | −0.013 | −0.041 | +0.23 |
| P | −0.005 [−0.008, −0.002] | −0.011 | −0.036 | +0.20 |
| G | −0.0004 [−0.0016, +0.0007] | −0.0007 | −0.001 | −0.003 |
| A | −0.006 [−0.009, −0.004] | −0.014 | −0.039 | +0.23 |

Every Holm p for "greater" is 1.0. Cliff's delta for BP − Z is −0.06: small, but consistent in sign across both measures.

**The decomposition the design built in.** C-gift-at-exit is C-base+pleasure with the motive off. So:

- the exit split alone (G − Z): −0.0004 [−0.0016, +0.0007], nothing;
- the running tally's pull on behaviour (BP − G): −0.0045 [−0.0070, −0.0021].

The tally makes partners make about 0.2 more blocks a week, and those blocks cost more than they give. The extra time comes out of work and time together. The observer sample (below) shows both.

**The same sign under every decision rule.** BP − Z is −0.004 with w = 0 for everyone and −0.004 under the old net rule. It does not depend on the suffering weight.

**C-agreed.** Of the 337 pair-seeds that ever lived together, 225 agreed on base+pleasure, 63 on hours and 49 on pleasure. It behaves like the tally rules.

## Why makers lower pleasure here

Makers on with nothing credited (Z) against makers off (M0): **−0.014 [−0.020, −0.009]**, unclipped −0.026. It holds in pairings with no extractive partner too (−0.016 [−0.026, −0.007], 29 pairings), so it is not only extractive makers.

Most of it is fewer and shorter households: week-0 formation falls from 0.52 to 0.47 and weeks together from 0.55 to 0.38. The observer's formation decomposition, on the first 20 pairings at seed 0 (every run reproduces its stored row), says what the rollouts see. For members who block formation, the household's edge over the outside option on time with the partner falls from +0.127 (M0) to +0.098 (Z) to +0.087 (BP). What making adds, in the observer's "other" group (where maker pleasure and craving land), rises only from +0.003 to +0.019 to +0.023. A block of making is time a partner is not spending with the other one, and the world values that time more than our making values replace.

This is mostly a calibration fact, not a finding about making. Amendment 1 set the time cost of a block at the point where 1 to 2 blocks a week leave pleasure near makers-off, on 15 pilot pairings. On the 120 confirmatory pairings, many makers go beyond that point: artists and extractive makers make up to 3 blocks a week. A different calibration could reverse the sign. What this run can say is narrower: **when making costs real time, a rule that pays people to make more lowers pleasure, and paying only at exit is neutral.**

## Who makes, and whether it evens out

- **Who makes is mostly fixed by traits.** In every arm, 80% to 99% of long-together pair-seeds end with the bigger maker doing over 60% of the making.
- **Imbalances almost never even out** (the bigger maker's share falls by 0.02 or more between week 52 and the end): 1% of long-together pair-seeds under C-zero, 2% to 3% under the tally rules, 3% with w = 0. P4 ("crediting does not change it") holds: BP − Z +0.013 [−0.037, +0.072]. It holds because almost nothing evens out anywhere.
- **Crediting makes the less-making partner join in, a little.** The share of long-together pair-seeds that end lopsided falls from 0.99 (Z) to 0.85 (BP) and 0.81 (H).
- **P3 missed, in the wrong direction.** Crediting by hours did not draw in partners who do not enjoy making: their share of making moved −0.037 [−0.081, +0.002] (84 pairings with such a partner; descriptive by the power check).

## Safe and extractive makers

- **P5 missed.** In the 59 pairings with exactly one extractive partner (47 with credit to compare), that partner's share of credit is not higher under C-hours than under C-pleasure: −0.026 [−0.082, +0.018]. The extractive maker already makes the most it can under every rule (3 blocks a week; see the stories), so the volume rule cannot pull more out of them, and their receivers' liking stays high because the boost offsets tolerance. Under this calibration the volume and pleasure rules see nearly the same thing.
- **P5b: holds but its interval crosses 0** (weak, descriptive). Pleasure under C-pleasure minus C-hours is +0.001 [−0.001, +0.003] in pairings with an extractive partner, and +0.003 [−0.002, +0.008] in those without.
- **The harm extractive making does is mostly invisible to clipped pleasure.** In the first story below, the receiver sits at full tolerance and full sensitization for two years and still reads pleasure 1.00.

So the answer to "does crediting by volume reward extractive makers more than crediting by pleasure given?" is: **not here**, because the extractive maker's volume does not respond to credit, and liking per block does not fall enough to separate the two rules.

## H20a: negotiated protection of long projects

Among the 63 pairings with at least one artist (BP-PN against BP; P6a confirmatory, P6b and P6c descriptive):

| | BP-PN − BP | BP-PI (imposed) − BP |
|---|---|---|
| projects started per pair-seed | −0.01 [−0.15, +0.12] | +0.08 [−0.07, +0.22] |
| projects completed | −0.09 [−0.21, +0.03] | −0.10 [−0.21, +0.02] |
| projects paid (13 weeks together after) | −0.04 [−0.15, +0.06] | −0.03 [−0.14, +0.07] |
| pleasure | −0.0009 [−0.0028, +0.0012] | −0.0007 [−0.0027, +0.0014] |
| weeks together | −0.020 [−0.035, −0.007] | −0.017 [−0.033, −0.004] |

**H20a's commitment clause is not supported here**: P6a, P6b and P6c all miss.

Why, from the counts:

- **Protection is rarely needed and rarely asked for.** Artists ask in 0.17 runs per pair-seed and partners agree in 0.11. Most projects start unprotected, because the artist's perceived hazard is low in a household with no past leave.
- **When it is used, it does not keep anyone.** No compensation was ever paid under negotiated protection (0 of 52 agreed projects). Under imposed protection it was paid 0.22 per pair-seed. Protection pays only when the partner who promised is the one who leaves; in the run where it was agreed, the artist left (story 3).
- **Weeks together fall a little with protection.** We do not know why. A first guess is that the imposed exit cost changes F4 carry-outs at readings, but that was not traced.

"Having a goal matters more than achieving it" is an input in this model (the goal term), so the run says nothing about it.

## The decision rule

**P7 holds**: with the per-persona suffering weight, week-0 formation is 0.35 lower than with w = 0 (BP 0.43 against BP-w0 0.78; −0.35 [−0.41, −0.29]). That was the research note's preregistered consequence. Pleasure is 0.02 higher under w = 0 (0.939 against 0.919 for Z), mostly because more pairs live together. The old net rule forms 0.43 and scores 0.915.

## Story spot-check

Five runs read as 13-week stories with the atlas recorder, plus a makers line per block (`--stories`; every run reproduces its stored row exactly; `runs/h39-makers/stories.json`).

1. **Z, p-anchor with p-bargainer, seed 0 (both extractive; a cook and a carer).** p-anchor cooks 3 blocks every week for 117 weeks; p-bargainer makes nothing. p-bargainer sits at tolerance 4 and sensitization 12 the whole time, and both read pleasure 1.00. Then p-anchor leaves, and p-bargainer's pleasure falls to 0.81. **Mismatch:** the story is a wanting trap; the measure reads a perfect household. Clipped pleasure cannot see it, and the unclipped line barely helps, because the boost keeps liking up.
2. **BP, the same pair and seed.** The identical life, week for week. Credit climbs to 360 against 0, and nobody's choices change. Crediting is inert for a maker already at the cap, as P5 found.
3. **BP-PN, g-11011 (safe artist) with p-host (safe carer), seed 0.** g-11011 does all the making (38 blocks a quarter), finishes two projects in half a year, asks for protection for a third, p-host agrees, and in that same week g-11011 leaves. Nothing is compensated, because the promise was p-host's. p-host, who made nothing, lives alone with falling pleasure (0.55 by the end). **Mismatch:** protection is meant to shelter the maker from the partner leaving; here the maker was the one who left.
4. **BP, g-00010 (carer, safe) with p-host (carer, safe), seed 0.** One block of care a week for three years, both partners at 0.96 to 1.00, credit 193 against 0. This one looks like what the measures claim: steady, lopsided, never evens out, and nobody minds.
5. **A, g-00001 (safe cook) with p-anchor (extractive cook), seed 0.** The pair agree on C-hours. p-anchor cooks 3 a week, g-00001 1 a week; the volume rule credits p-anchor 111 against 40. g-00001, at full tolerance and sensitization, leaves at week 26; p-anchor leaves the empty home at week 47 and ends at pleasure 0.51. Here the volume rule did reward the extractive maker, and the household broke. The averages (P5) hide this kind of pair.

Read together: the measures match the steady safe household (4). They miss the wanting trap (1) and misread protection (3). This supports the prereg's warning that clipped pleasure hides what makers give and what extractive makers take.

## Prereg vs actual

| ID | Prediction | Actual | Verdict |
|---|---|---|---|
| P1 | BP − Z ≥ +0.003, CI above 0 | −0.005 [−0.0075, −0.0026] | misses (descriptive by power) |
| P1b | unclipped agrees in sign | −0.012 | holds (both negative) |
| P2 | blocks per partner-week up ≥ 0.10 under H, P, BP | +0.23, +0.20, +0.19, Holm p 0.0003 | holds (manipulation check, no weight) |
| P3 | enjoyment-0 share up ≥ 0.03 under H | −0.037 [−0.081, +0.002] | misses (descriptive) |
| P4 | evening-out within ±0.10, BP − Z | +0.013 [−0.037, +0.072] | holds, because nothing evens out (descriptive) |
| P5 | extractive credit share H − P ≥ +0.05 | −0.026 [−0.082, +0.018] | misses |
| P5b | pleasure P − H > 0 in extractive pairings | +0.001 [−0.001, +0.003] | weak (CI crosses 0; descriptive) |
| P6a | projects started +0.20 with negotiated protection | −0.01 [−0.15, +0.12] | misses |
| P6b | projects paid +0.10 | −0.04 [−0.15, +0.06] | misses (descriptive) |
| P6c | pleasure not lower | −0.0009 [−0.0028, +0.0012] | misses (estimate not above 0; descriptive) |
| P7 | formation BP − BP-w0 ≤ −0.10 | −0.35 [−0.41, −0.29] | holds |

H39: **not supported** (descriptive). H20a, the commitment clause: **not supported** (descriptive). Extractive question: **no**, by P5 and P5b.

## Surprises

- **Paying for making makes people make more, and that lowers pleasure.** The author's lean (base plus pleasure) is no better than counting hours or pleasure alone. The only rule that does no harm is the one with no running tally.
- **Makers themselves lower pleasure, even safe ones.** The model's household already runs near its pleasure cap, and the time making takes comes out of time together.
- **The extractive maker is insensitive to every crediting rule**, because it already makes the most it can.
- **The protection story's first real use was the maker leaving.**

## Misses and weaknesses, plainly

- The making calibration was fitted on 15 pilot pairings; on the confirmatory pairings makers lowered pleasure at it. All conclusions about the level of making are conditional on that one point.
- Pleasure is clipped at 1 and most person-weeks sit near it. The wanting trap in story 1 is invisible to the primary measure.
- Credit pays only at exit, through F4, and most exits meet a small estate. The exit split alone did nothing measurable.
- The credit motive is in the making rule by construction; its size (κ) is a guess. The harm from the tally scales with it.
- Protection rests on a trust value that never moves in this world. The negotiation reduces to the partner's own stay reading.

## Can be about / cannot be about

This can be about what six crediting rules and negotiated project protection do to scripted makers in the H38 household (F4, items V2), at one calibration, with the per-persona suffering-weight decision rule.

It cannot be about:

- real domestic work, real makers, art or care, or whether crediting them is fair;
- making in general: one calibration of time cost and value, chosen on a pilot, and makers lowered pleasure at it;
- "having a goal matters more than achieving it" (an input here);
- extractive pleasure technology in markets: there is no market, no price and no outside maker;
- people. Agents feel nothing, and the partner is a script.

## Recommendation

Do not add a making-credit term to the household seed on this evidence. The useful finding is the decomposition: counting making at exit is neutral, and a running tally that pulls behaviour is what costs. Before a rerun, two things matter more than more seeds:

1. **Make the time cost of making real, not fitted.** Let a block displace a chosen activity (rest or leisure first), not whatever the week's units would have funded.
2. **Give the wanting trap a measure that sees it.** Liking lost to tolerance, measured directly, beside clipped pleasure (ADR 0018's lifetime liking).

## Reproduction

`uv run python scripts/h39_makers_run.py --pilot`, `--power`, `--reach`, `--run --seeds 4`, `--analyze`, `--observe`, and `--stories "Z|p-anchor|p-bargainer|0;BP|p-anchor|p-bargainer|0;BP-PN|g-11011|p-host|0;BP|g-00010|p-host|0;A|g-00001|p-anchor|0"`. Tests: `uv run pytest tests/test_makers.py -m ""`. Rows in runs/h39-makers/ (not committed).
