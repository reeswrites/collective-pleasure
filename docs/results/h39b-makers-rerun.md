# H39b makers rerun: results

Wording rule: agents feel nothing; "pleasure", "liking" and "wanting" are glosses for modeled values.

> **Note, 2026-11-11 (later): rerun under the recalibrated agents and bills that hurt** ([agent-recalibration.md](agent-recalibration.md), Amendment 2 of the prereg). Households almost never form under them (week-0 formation 0, weeks together 7% to 13%), so the crediting question is barely asked. The crediting nulls survive; the tally still raises making and still lowers unclipped pleasure a little; **"makers lower pleasure" reverses** (Z − M0 +0.003 [+0.001, +0.005], was −0.022). Cite the numbers below only as results of the v1 agents.

Status: run once on 2026-11-11, after the preregistration ([h39b-makers-rerun-prereg.md](h39b-makers-rerun-prereg.md), commit 27f8eb4; Amendment 1 and the code, commit fdd8b36). It reruns H39 ([h39-makers.md](h39-makers.md)) with the fitted time cost removed. 13 arms × 120 pairings × 4 seeds = 6,240 runs, 3,856 s on 3 workers. Scripted agents, no model calls, every number ASSUMED. By the power check the H39 and H20a verdicts are DESCRIPTIVE again.

## What changed from H39

The author asked "why are there any fitted time costs other than work and sleep". H39 charged a block of making twice: it used a time unit, and the maker's choice also subtracted 0.02 pleasure units, a number fitted so that makers-on matched makers-off. H39b:

- **drops the flat time cost.** No time cost is read anywhere.
- **chooses making against the agent's own week.** A block is made only if it is worth more than what the agent's own planned week loses when that unit is taken. The week is planned with the agent's own action utilities (work, rest, friends, time together, spending, bills), updated after each planned action as the world's would be, with the partner's planned together sessions counted (they use the maker's units too).
- **lets enjoyment of making be negative** ({−1, 0, +1}, a third each; same ranks as H39's {0, 0.5, 1}). Effort enters there.
- **adds two wanting-trap measures:** lifetime liking lost to tolerance, and the share of person-weeks at tolerance ≥ 3 of 4 and sensitization ≥ 9 of 12.

Everything else is H39's: arms, pairings, seeds, F4 with items V2, the suffering weight w, the credit rules, and the Amendment 1 values. H39's choice is still there, bit-identical, as `choice="flat_cost"`.

The planner changed twice on pilot runs before the confirmatory run (Amendment 1 says why, with all three pilots). The final version was checked against what the world's own agents do in makers-off weeks. It matches their actions exactly in 40% of partner-weeks; holding utilities fixed matched 6%. It plans 0.34 more units a week than the agents use.

## In one paragraph

**Without the fitted cost, H39's crediting findings mostly fade to nulls on the main measure. "Makers lower pleasure" survives and gets bigger. The wanting trap is now visible, and it is common.**

- **Crediting with a running tally no longer clearly lowers clipped pleasure.** BP − Z is −0.0027 [−0.0055, +0.0002] (H39: −0.005, interval below 0). The unclipped line still says lower (−0.007 [−0.012, −0.002]). The exit split alone is still nothing (G − Z −0.0003).
- **Makers on, nothing credited, sit 0.022 below makers off** [−0.028, −0.017] (H39: −0.014). That is not an artifact of the fitted cost. Week-0 formation falls from 0.52 to 0.33, and weeks together from 0.55 to 0.32.
- **The wanting trap is common and still invisible to clipped pleasure.** 9% of person-weeks are in a full trap with makers on (12% in pairings with an extractive maker, 0 without). About a quarter of all liking from made goods is lost to tolerance. Of the persons trapped in at least a quarter of their weeks, 58% average clipped pleasure of 0.95 or more.
- **Negotiated protection now starts more long projects** (+0.15 per pair-seed [+0.06, +0.25]), but below the preregistered +0.20. Projects paid and pleasure do not move. H20a's commitment clause is still not supported.
- **The suffering-weight rule still forms far fewer households** than w = 0 (P7: −0.44).

H39: **not supported** (descriptive). H20a commitment clause: **not supported** (descriptive). Extractive question: **no answer** (P5b weak, descriptive).

## Headline numbers per arm, against H39

Means over 120 pairings × 4 seeds. H39's numbers are from [h39-makers.md](h39-makers.md); H39's rows are no longer on disk, so the two are compared as estimates, not paired.

| | M0 | Z | H | P | BP | G | A |
|---|---|---|---|---|---|---|---|
| pleasure, H39b | 0.933 | 0.911 | 0.908 | 0.910 | 0.908 | 0.911 | 0.908 |
| pleasure, H39 | 0.933 | 0.919 | 0.913 | 0.914 | 0.914 | 0.919 | 0.913 |
| unclipped, H39b | 1.009 | 0.962 | 0.955 | 0.960 | 0.955 | 0.961 | 0.955 |
| net, H39b | 0.744 | 0.703 | 0.704 | 0.704 | 0.701 | 0.703 | 0.704 |
| formed at week 0, H39b (H39) | 0.52 (0.52) | 0.33 (0.47) | 0.30 (0.45) | 0.32 (0.43) | 0.30 (0.43) | 0.33 (0.47) | 0.29 (0.42) |
| weeks together, H39b (H39) | 0.55 (0.55) | 0.32 (0.38) | 0.29 (0.34) | 0.31 (0.35) | 0.29 (0.35) | 0.31 (0.38) | 0.29 (0.35) |
| blocks per partner-week, H39b (H39) | – | 1.87 (1.20) | 2.01 (1.42) | 1.94 (1.41) | 2.00 (1.39) | 1.88 (1.18) | 2.01 (1.42) |
| liking lost to tolerance, per pair-seed | – | 1.45 | 1.48 | 1.50 | 1.45 | 1.41 | 1.46 |
| share of liking lost | – | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 |
| person-weeks in a full trap | – | 0.093 | 0.087 | 0.092 | 0.086 | 0.092 | 0.087 |

Each arm against C-zero, paired by pairing, 95% bootstrap interval (Holm over the five, one-sided "greater"; every Holm p is 1.0):

| Arm − Z | Pleasure, H39b | Pleasure, H39 | Unclipped, H39b | Weeks together | Blocks per partner-week |
|---|---|---|---|---|---|
| BP | −0.0027 [−0.0055, +0.0002] | −0.005 [−0.0075, −0.0026] | −0.007 [−0.012, −0.002] | −0.032 | +0.125 [+0.096, +0.156] |
| H | −0.0025 [−0.0053, +0.0002] | −0.006 [−0.009, −0.004] | −0.007 [−0.013, −0.002] | −0.034 | +0.129 |
| P | −0.0005 [−0.0030, +0.0019] | −0.005 [−0.008, −0.002] | −0.002 [−0.006, +0.002] | −0.010 | +0.071 |
| G | −0.0003 [−0.0016, +0.0010] | −0.0004 [−0.0016, +0.0007] | −0.001 | −0.008 | +0.003 |
| A | −0.0025 [−0.0053, +0.0003] | −0.006 [−0.009, −0.004] | −0.007 [−0.012, −0.002] | −0.035 | +0.121 |

The decomposition: the exit split alone (G − Z) −0.0003 [−0.0016, +0.0010], nothing, as in H39. The tally's pull on behaviour (BP − G) is −0.0024 [−0.0052, +0.0004] on clipped pleasure (H39: −0.0045, interval below 0) and −0.006 [−0.011, −0.002] unclipped. The tally still adds 0.12 blocks a partner-week.

Under the other decision rules, the tally's harm is still there with its interval below 0. BP − Z is −0.0033 [−0.0058, −0.0008] with w = 0 (H39: −0.004) and −0.0035 [−0.0064, −0.0009] under the old net rule (H39: −0.004). So "a running tally lowers pleasure a little" holds in two of three rules and in the unclipped line, and is borderline in the main one. It is fragile, not gone.

## Which H39 findings survive

By the rule fixed in the prereg (an H39 interval that excluded 0 survives if H39b's excludes 0 with the same sign; an H39 null survives if H39b's interval includes 0):

| H39 finding | H39 | H39b | Verdict |
|---|---|---|---|
| Tally rules lower pleasure (BP − Z) | −0.005 [−0.0075, −0.0026] | −0.0027 [−0.0055, +0.0002] | **does not survive** (unclipped and the w = 0 and net rules still below 0) |
| H − Z, A − Z | −0.006, −0.006 | −0.0025, −0.0025 (intervals reach +0.0002, +0.0003) | **do not survive** |
| P − Z | −0.005 [−0.008, −0.002] | −0.0005 [−0.003, +0.002] | **does not survive**; artifact of the fitted cost |
| The tally's pull (BP − G) | −0.0045 [−0.0070, −0.0021] | −0.0024 [−0.0052, +0.0004] | **does not survive** on clipped; survives unclipped |
| Exit split alone (G − Z) null | −0.0004, null | −0.0003, null | **survives** |
| Makers lower pleasure (Z − M0) | −0.014 [−0.020, −0.009] | −0.022 [−0.028, −0.017] | **survives, larger** |
| ... also without an extractive partner | −0.016 [−0.026, −0.007] | −0.013 [−0.020, −0.007] | **survives** |
| The tally raises making (P2) | +0.19 to +0.23 | +0.07 to +0.13 | **survives, smaller** |
| Fewer weeks together under tally rules | −0.039 | −0.032 | survives |
| P3: hours do not draw in partners who dislike making | −0.037 [−0.081, +0.002] | +0.012 [+0.002, +0.022] | **does not survive**; now a small move the predicted way, below the +0.03 threshold |
| P4: imbalances almost never even out (1% to 3%) | holds, trivially | 7% (Z) to 18% (H); BP − Z +0.097 [+0.007, +0.192] | **does not survive**; making is now two-sided more often, and a tally evens it out more |
| P5: volume crediting does not favour extractive makers | −0.026, null | −0.034 [−0.071, +0.006], null | **survives** |
| H20a: protection does nothing (projects started) | −0.01 [−0.15, +0.12] | +0.155 [+0.056, +0.25] | **reverses**, but below the +0.20 threshold |
| Protection never compensates | 0 of 52 | paid in 0.09 runs per pair-seed | **does not survive** |
| P7: w forms fewer households | −0.35 | −0.44 | **survives** |

In short: **the fitted cost made the crediting results look sharper than they are, and made the cost of making look smaller than it is.** With making chosen against the agent's own week, makers make more (1.9 blocks a partner-week against 1.2), and households form and last less.

## Why makers still lower pleasure

Week-0 formation falls from 0.52 to 0.33, and fewer pairs ever live together. The observer sample (first 20 confirmatory pairings, seed 0; every run reproduces its stored row) splits the formation reading for members who block formation. Each number is the household's edge over the outside option:

| Part (blocking members) | M0 | Z | BP |
|---|---|---|---|
| members blocking (of 40) | 10 | 18 | 16 |
| money | −0.108 | −0.135 | −0.130 |
| rest | −0.018 | −0.041 | −0.039 |
| friends | −0.070 | −0.089 | −0.097 |
| time with the partner | +0.127 | +0.115 | +0.101 |
| other (making lands here) | +0.003 | +0.035 | +0.035 |

What making gives in the rollout (+0.03) is less than it takes from money, rest and friends (about −0.07 together). The making-decision decomposition (all Z runs) says something different. A block's value to its maker is +0.019 (care for the receiver 0.014, own share of a piece 0.006, enjoyment −0.001). The agent's own plan prices the time at 0.002 a block, and puts 78% of blocks into units it planned to leave idle. When the plan does see a cost, work (6 per 100 blocks), rest (2) and friends (1) are what it says would go.

So **by the agent's own valuation, making is nearly free. By the world's pleasure over 52 weeks, it costs rest, money and friends.** Two readings, not separated by this run:

1. The agent's start-of-week utilities price rest, work and friends below what they are worth in the hedonic model, because need levels carry over weeks. Making looks cheap to an agent that undervalues its own rest.
2. The planner's "idle" units are not idle in the played week (noise, requests, the partner's units). The fidelity check says the plan uses more units than the agent, not fewer, which argues against this one.

Either way, this is a finding about the model's agents, not a calibration choice. No number was fitted to get it.

**It runs through the suffering-weight rule.** Under w = 0, makers-on forms 0.75 at week 0 and scores 0.944, above M0's 0.933 under the weighted rule. There is no makers-off arm under w = 0 in this design, so that is not a paired comparison. The prereg did not predict it.

## The wanting trap, now visible

| | Z | BP | Z-w0 |
|---|---|---|---|
| person-weeks in a full trap | 0.093 | 0.086 | 0.256 |
| ... pairings with an extractive partner | 0.123 | 0.113 | 0.337 |
| ... pairings without one | 0 | 0 | 0 |
| liking lost to tolerance, per pair-seed | 1.45 | 1.45 | 3.44 |
| share of liking lost | 0.25 | 0.25 | 0.40 |
| liking-to-wanting ratio of blocks received | 0.64 | 0.64 | 0.60 |
| persons trapped ≥ 25% of weeks | 130 | 120 | 363 |
| ... of them with clipped pleasure ≥ 0.95 | 76 (58%) | 70 (58%) | 253 (70%) |

- **S1 (known answer) holds:** traps occur only with an extractive partner, and lost liking is positive in both kinds of pairing (safe makers also build tolerance at 2 or more blocks a week).
- **Lost liking is not an extractive-only harm.** It is higher in pairings without an extractive partner (1.65 against 1.39 per pair-seed in Z), because those pairs last longer and make more for each other.
- **S2: crediting by pleasure given does not lower the trap.** P − H on trap share in extractive pairings is +0.006 [−0.004, +0.017]; on lost liking +0.016 [−0.09, +0.13]. Crediting rules barely move either measure (every arm − Z interval spans 0 on lost liking; BP − Z on trap share −0.008 [−0.016, −0.001]).
- **The measures disagree with pleasure, as the prereg asked us to report.** Most heavily trapped persons read near-perfect clipped pleasure. Pleasure and the trap measures are answering different questions. Neither should be averaged into the other.
- **More households, more traps.** Under w = 0, more pairs form and last, so traps nearly triple. That is a cost the pleasure line (0.944, the highest of any arm) does not show.

## H20a: negotiated protection

Among the 63 pairings with an artist:

| | BP-PN − BP | BP-PI (imposed) − BP |
|---|---|---|
| projects started per pair-seed | +0.155 [+0.056, +0.250], Holm p 0.005 | +0.234 [+0.123, +0.345] |
| projects completed | +0.056 [−0.040, +0.147] | +0.063 [−0.040, +0.159] |
| projects paid | +0.032 [−0.071, +0.123] | +0.040 [−0.071, +0.135] |
| pleasure | −0.0005 [−0.0020, +0.0009] | −0.0006 [−0.0025, +0.0012] |

Artists asked in 0.14 runs per pair-seed and partners agreed in 0.10. Compensation was paid in 0.09 (H39: never). Protection now does what it is for at the start: more projects begin. The extra projects are mostly lost to splits (abandoned 0.08 against 0.03), so few more finish or pay, and pleasure does not move. P6a misses its threshold, though the effect is real and positive. P6b and P6c miss. **H20a's commitment clause: not supported (descriptive).**

## Story spot-check

The same five picks as H39 (`runs/h39b-makers/stories.json`; every run reproduces its stored row).

1. **Z, p-anchor with p-bargainer, seed 0 (both extractive).** They decline at week 0 and move in at week 64. Then both make: p-anchor cooks 3 a week, and p-bargainer (who enjoys making now) gives care. p-bargainer is trapped in 13 of every 13 weeks from week 65, and by the end both are, while both read pleasure 0.98 to 1.00. **The trap measure sees it now. Clipped pleasure still does not.** Mismatch with pleasure, match with the new measure.
2. **BP, the same pair.** Now a different life from Z (in H39 it was identical). They form at week 0, both are trapped within half a year (13 of 13 weeks), and p-anchor leaves at week 39. p-bargainer, out of the trap, lives alone at 0.82 to 0.89. Credit 100 against 69.
3. **BP-PN, g-11011 (safe artist) with p-host (safe carer), seed 0.** Both dislike making (enjoyment −1) and both still make about 2 blocks a week, for care. The artist finishes four long projects in two years. The receivers sit at tolerance 3 to 4 and lose liking (about 0.2 a quarter), but neither is ever trapped (no cue). Both leave at week 104. Protection is never asked. Looks like what the measures say: lost liking without a trap. A mismatch with the story H20a tells, because protection plays no part.
4. **BP, g-00010 with p-host (both safe carers).** Steady for three years, now two-sided (21 against 18 blocks a quarter; H39 had it lopsided), both partners at tolerance 3 to 4, losing 0.1 to 0.3 liking a quarter each, pleasure 0.94 to 1.00. Steady and nobody minds, but the receivers' care is a quarter less liked than it would be fresh. The new measure adds something true that pleasure hides.
5. **A, g-00001 (safe cook) with p-anchor (extractive cook).** They agree on hours. g-00001 is trapped by p-anchor's cooking in 9 to 12 of 13 weeks while reading pleasure 0.98 to 1.00, and leaves at week 39. p-anchor ends alone at 0.56. As in H39, the volume rule rewarded the extractive maker (100 against 70) and the household broke.

Read together: the trap measure now matches what the stories show in 1, 2 and 5, where clipped pleasure missed it. Lost liking shows the slow cost of steady safe making (3, 4). Protection still plays no visible part in its story (3).

## Prereg vs actual

| ID | Prediction | Actual | Verdict |
|---|---|---|---|
| P1 | BP − Z ≥ +0.003, CI above 0 | −0.0027 [−0.0055, +0.0002] | misses (descriptive) |
| P1b | unclipped agrees in sign | −0.007 | holds |
| P2 | blocks per partner-week ≥ +0.10 under H, P, BP | +0.129, +0.071, +0.125 (Holm p 0.0003 each) | 2 of 3 (P misses); manipulation check |
| P3 | lowest-enjoyment share ≥ +0.03 under H | +0.012 [+0.002, +0.022] | misses (right direction) |
| P4 | evening out within ±0.10, BP − Z | +0.097 [+0.007, +0.192] | misses (descriptive) |
| P5 | extractive credit share H − P ≥ +0.05 | −0.034 [−0.071, +0.006] | misses |
| P5b | pleasure P − H > 0 in extractive pairings | +0.0004 [−0.0026, +0.0033] | weak (descriptive) |
| P6a | projects started ≥ +0.20 | +0.155 [+0.056, +0.250] | misses (descriptive) |
| P6b | projects paid ≥ +0.10 | +0.032 [−0.071, +0.123] | misses (descriptive) |
| P6c | pleasure not lower | −0.0005 [−0.0020, +0.0009] | misses (descriptive) |
| P7 | formation BP − BP-w0 ≤ −0.10 | −0.44 [−0.50, −0.38] | holds |

Scorecard: 3 hold (P1b, P2 counted as held for H and BP, P7), 1 weak (P5b), 7 miss (P1, P3, P4, P5, P6a, P6b, P6c). H39: not supported. H20a: not supported. Extractive question: no answer.

## Surprises

- **Removing the fitted cost made makers worse, not better.** The fitted cost had been holding making down. Without it, making by the agent's own lights is almost free, and the household pays for it in rest, money and friends.
- **Protection began to work at its first step** (more projects started, compensation paid) once making was not taxed. It still does not get projects finished.
- **Safe makers lose their partners a quarter of the liking too.** Tolerance is not only an extractive harm.
- **The suffering weight decides how much making does.** Under w = 0, makers-on is the highest-pleasure arm and has nearly three times the traps.

## Misses and weaknesses, plainly

- **The planner changed twice after pilot runs.** Each change was to match the world's own week, and was checked against agents' actual actions, not against any arm's outcome. But it was found by looking at pilot outcomes, and a reader should weigh that. All three pilots are in the prereg's Amendment 1.
- **The scale assumption is untested.** A utility of 0.03 and a pleasure of 0.03 are treated as the same thing. The formation decomposition suggests they are not: the agents treat as cheap what the hedonic model counts as costly.
- κ (the credit motive) and the per-block values were set beside the removed time cost in H39 and carried over. The tally effect scales with κ.
- The planner matches the played week exactly in 40% of partner-weeks.
- H39's rows were not on disk, so H39 against H39b is by estimates, not paired by pairing.
- Pleasure is clipped at 1. Most trapped persons sit near the cap.

## Can be about / cannot be about

This can be about what six crediting rules and negotiated project protection do to scripted makers in the H38 household (F4, items V2) when making is chosen against the agent's own other uses of time, at one set of assumed values, with the per-persona suffering weight.

It cannot be about real domestic work, makers, art or care, or about whether crediting is fair. It cannot be about markets for pleasure goods (there are none). It cannot be about people.

## Recommendation

Do not add a making-credit term on this evidence. The useful findings:

1. **The cost of making in this model is real, not a fitted artifact.** But it comes from a gap between the agent's utilities and the hedonic model, and that gap should be measured before more making experiments. Next: a known-answer check of `PersonaAgent.utilities` against the realized 52-week pleasure change of each action, in makers-off worlds.
2. **Report the wanting-trap share and lost liking beside pleasure in every makers run.** They see what pleasure does not.

## Reproduction

`uv run python scripts/h39b_makers_rerun.py --fidelity`, `--pilot`, `--power`, `--reach`, `--run --seeds 4`, `--analyze`, `--observe`, `--stories`. Tests: `uv run pytest tests/test_makers.py -m ""`. Rows in runs/h39b-makers/ (not committed). H39 itself: `scripts/h39_makers_run.py`, with `choice="flat_cost"` (the default).
