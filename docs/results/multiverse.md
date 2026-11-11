# Multiverse sensitivity sweep (results)

> **Correction (2026-11-11, correctness review).** A fresh review (docs/reviews/2026-11-11-correctness.md, finding 11 and the low items) checked this sweep. The labels reproduce. The original text is kept unchanged below this block.
>
> - **C5 is "robust" only under a one-sided noise rule.** The prereg counts a failure within 2 standard errors as noise, but counts a hold within 2 standard errors as clean. C5's D2a, with one seed, is only 1.1, 1.8 and 1.8 standard errors above zero at three points (lhs:3, lhs:7, and the one-at-a-time point denied_below 0.075). Read C5 as: the sign held at every point, and 3 points cannot be told apart from zero. C5b rests on 2 to 7 qualifying households at some points.
> - C4's one-at-a-time points FLOOR=13 and BREACH_N 0.1 and 0.4 (and C5's BREACH_N 0.1) give output identical to the default. "Robust to BREACH_N" is empty, because the parameter has no path to the quantity.
> - C6 can barely fail: 1 to 19 of 171 runs differ at all. C7 holds at two points exactly on its threshold. C8's failures sit just above 0.05 with 3 seeds.

Status: results of the sweep preregistered in docs/results/multiverse-prereg.md (committed first, commit 258ecff; Amendment 1 cut the household design for compute before those runs started). Scripted agents and exact solves only. No model calls. Agents feel nothing; "pleasure" is a gloss for a modeled hedonic state (ADR 0010). Every number below is about models with assumed parameters, not about people.

Code: `src/mar/multiverse.py`, `tests/test_multiverse.py`, `scripts/multiverse_run.py`. Existing modules were imported read-only; parameters were moved in memory only. Raw outputs: `runs/multiverse/` (git-ignored). Kept copy: `experiments/kept/multiverse-2026-11-10/` (`results.json`, `report.html`).

## How to read the table

Each conclusion was checked at many parameter settings. "Holds in" is the share of Latin hypercube points (or of the full grid, for C7) where it still holds. A conclusion is **robust** if it holds in at least 90% of points and no single parameter at the end of its range flips it. It is **fragile** if it holds in 50% to 90%, or a single parameter flips it. It **flips** if it holds in under half. "Flipped by" lists single parameters, set to one end of their range with everything else at default, that make it fail. "Driver" is the parameter whose value tracks the result most closely across the hypercube (Spearman rank correlation with the margin).

## Summary table

| ID | Conclusion (source) | Holds in | Label | Flipped by (one parameter at a range end) | Driver | Plain-English verdict |
|---|---|---|---|---|---|---|
| C1 | Greedy loses at least 10% of optimal at gamma .95 over 26 weeks (horizon.md section 3) | 98 of 128 (0.77) | **fragile** | ritual base bS = 12; commitment payoff beta = 0.75 | beta (+0.64), bS (-0.63) | Greedy loses something almost everywhere (127 of 128). How much is set by the commitment payoff and the ritual's value. The "up to 29%" figure is one point in a range from 8% to 96% |
| C2 | Concert: net carryover negative weekly and positive every 4 weeks (P5) | 38 of 128 (0.30) | **flips** | W = 2, bS = 12, bX = 8, beta = 0.75, muz = 2, nuD = 4 | bX (+0.27), weak | Do not state. Whether a weekly concert costs or pays, and whether a monthly one pays, depends on several assumed numbers |
| C2b | Concert boundary m* is 2 to 4 weeks ("about 3 weeks") | 42 of 128 (0.33) | **flips** | bS = 12, bX = 8, muz = 2, nuD = 4 | none strong | Do not state. m* ranged from 1 week to never; "positive at some spacing" held in 108 of 128 |
| C3 | Best friend-contact gap at most 14 days at overlap 0.7, every half-life (amendment A1b) | 115 of 128 (0.898) | **fragile** (one point under the line) | none | per-contact cost (-0.45), tau_w (-0.41) | "Weekly or so" mostly survives. Median of the worst half-life's gap 6 days; it breaks when contact is costly |
| C3b | Best gap at most 7 days (the "4 to 7 days" headline) | 93 of 128 (0.73) | **fragile** | per-contact cost 24 or 28.8; A = 0.5; activity value x0.5; tau_s = 6 | per-contact cost (-0.45) | The specific "4 to 7 days" leans on the per-contact cost set after the smoke run. At the old meeting cost (24) it is 8 to 11 days |
| C3c | Sharing shortens the gap against the reunion-only control by at least a day (A1c) | 62 of 128 (0.48) | **flips** | nine parameters, including m_scale = 0.6, rel = 3, tau_w = 3.5, thr = 3, per-contact cost 0 or 1.8 | m_scale (-0.40) | Do not state. Most of the drop to "weekly" comes from shrinking the reunion layer, as the amendment already said; whether sharing adds to it is a coin flip over the ranges |
| C4 | Negotiation v2.1: living apart beats cohabiting with no pot on non-offsettable suffering by at least 0.02 | 8 of 8 (1.00); all 16 one-at-a-time points | **robust** | none | weekly connection decay (+0.93), living cost (+0.81) | The direction is safe to state: apart beats cohabiting with no pot by 0.06 to 0.26 at every setting tried. The size moves a lot with the need-clock and living-cost assumptions |
| C5 | Pleasure demo D2a: seed v2.2 beats the imposed baseline on pleasure | 8 of 8 (1.00); all 14 one-at-a-time points | **robust** (small edge) | none | living cost (+0.71) | The sign holds everywhere tried, but the edge stays small (+0.014 to +0.090, default +0.030). At 2 of 8 points it is within 2 standard errors of zero with one seed |
| C5b | Pleasure demo D3: relational share of v2.2 households above 0.40 | 8 of 8 (1.00); all 14 one-at-a-time points | **robust** | none | together-event value (+0.93) | Holds (0.41 to 0.53), but it is set by the assumed value of time together, as the demo already said; at some points only 2 to 7 households qualify |
| C6 | Seed v2: binding a stay commitment changes non-offsettable suffering by less than 0.02 (the null) | 16 of 16 (1.00); all 12 one-at-a-time points | **robust** | none | none strong (largest 0.29) | The null survives, including a breach load four times the default (difference 0.0098). It is still a null about a threshold breach rule, which cannot be swept without a code change |
| C7 | VPGG: voluntary beats compulsory on liberty v2 and on empowerment (sum above 0, at least 8 of 15 compositions) | 54 of 54 grid points (1.00) | **robust** | none | n/a (grid) | Holds everywhere tried. The exact count (11 of 15) is not stable: it runs from 8 to 14 with r |
| C8 | VPGG: no oscillation (cooperator-share std below 0.05 in all 3 seeds) | 21 of 24 (0.875) | **fragile** | revision = 0.4 | mutation (+0.61), sigma share (-0.61) | The miss mostly stands, but low mutation or fast revision push the std just over the floor (0.056 to 0.089). Even then the fluctuations are small |

## What to stop saying confidently

Stop stating these as findings, or state them only with "under the assumed parameters, and it moves":

1. **The concert boundary of about 3 weeks** (horizon P5). It flips: weekly-negative and monthly-positive hold together in 30% of settings, and the boundary ran from 1 week to never.
2. **"Greedy loses up to about 29%."** Greedy loses something almost everywhere, but the size ran from 8% to 96% (median 34%) at gamma 1 over 52 weeks. Quote a range or no number.
3. **"The best friend-contact gap is 4 to 7 days."** It holds in 73% of settings and moves with the per-contact cost that was set after the smoke run (8 to 11 days at the old meeting cost). "About weekly rather than monthly" holds in 90% and is the safer wording.
4. **"Sharing itself makes contact more frequent."** It flips (48%). Most of the move to "weekly" comes from the smaller reunion layer.
5. **"No VPGG oscillation"** is fragile, not robust: slower mutation pushes it just over the floor.

These held across the ranges and can be stated with their usual caveats: greedy loses something whenever state carries over; VPGG voluntary beats compulsory on both freedom measures (the sign, not the 11 of 15 count); in negotiation, living apart beats cohabiting with no pot (direction, not size); the seed v2 binding null (as a fact about the threshold rule); and seed v2.2's pleasure edge over baseline and its relational share (both small or assumption-set, as the demo said).

## Per conclusion

### C1 and C2: the horizon model (exact dynamic programming)

18 parameters of `HorizonParams`, 128 hypercube points plus 36 one-at-a-time points, table sizes 3247 to 23724 states. The default reproduces the published numbers exactly (15.5% loss; concert -5.6 weekly, +2.2 every 4 weeks, m* = 3; tested).

- **Greedy loses something: robust.** Loss above zero in 127 of 128 points (the exception has loss exactly 0). Above 5% in 117 of 128.
- **"Large" (10% at gamma .95): fragile.** Median 22%. The two single flips are a weaker commitment payoff (beta 0.75 gives 2.9%, because the optimal plan no longer takes on the commitment) and a richer ritual (bS 12 gives 9.7%). The published jump between gamma 0.9 and 0.95 was already traced to the commitment; the sweep confirms the size of the loss is mostly the commitment's.
- **The "about 29%" number: not stable.** Loss at gamma 1 over 52 weeks has median 34%, middle half 23% to 50%, range 8% to 96%. Say "a substantial share, size set by assumed payoffs", not a percent.
- **The concert: flips.** Weekly concerts were net negative in 84 of 128 points and four-weekly ones net positive in 79, but both together only in 38. The smallest spacing at which a concert pays (m*) was: never 20, 1 week 44, 2 weeks 23, 3 weeks 15, 4 weeks 4, 5 weeks 12, 6 to 8 weeks 10. The qualitative answer "it depends on the dose" survives in the weak sense that the sign changes with spacing in most points; the specific boundary does not.

### C3: the friend-contact gap with shared activities

16 parameters, 128 hypercube points plus 34 one-at-a-time points (including the per-contact cost at 0 and at 24, the old meeting cost). The default reproduces the amendment exactly (4, 5, 6, 7 days; control 6, 7, 10, 12; tested).

- **Per-contact cost, alone (everything else default):** worst-case best gap 4 days at cost 0, 5 at 1.8, 7 at 5.4 to 10.8, 8 at 14.4, 10 at 21.6, 11 at 24, 12 at 28.8, and at 43.2 the half-life 10 friendship is never worth a contact (best gap 200, the search limit). So the tuned value 7.2 sits at the low end of where "4 to 7" holds. At the unscaled old cost the answer is "every 8 to 11 days".
- **"About weekly, not monthly":** holds in 115 of 128 points (median worst-case gap 6 days, 90th percentile about 15). That is the part worth keeping.
- **"Sharing itself shortens the rhythm":** flips. The reunion-only control is as short or shorter in 66 of 128 points. A bigger reunion layer (m_scale 0.6), a bigger release (rel 3), or a lower pain threshold (thr 3) all bring the control down to 4 to 6 days on its own.

### C7: VPGG freedom measures

Full grid: r in {2, 2.5, 3, 3.5, 4, 4.5}, sigma share in {0.25, 0.5, 0.75}, horizon k in {2, 3, 4}. Voluntary beat compulsory on both measures at all 54 points (sum above 0 and at least 8 of 15). Wins on liberty v2: 8 to 14; on empowerment: 9 to 14. Half-integer r gives 13 or 14 wins and integer r gives 8 to 12, which points to the state count (holdings rounded to a key) rather than to anything about freedom: the count is an artifact of how distinct payoffs are, the sign is not. The default reproduces +5.263 bits and 11 of 15 (tested). Caveats from liberty-v2.md stand: the VPGG domination term is zero by construction and the class table was chosen after the v1 failure, so robustness to r, sigma and k says nothing about that choice.

### C8: VPGG oscillation

6 parameters, 24 hypercube points plus 12 one-at-a-time points, 3 seeds each (111 runs, 3000 generations). The default reproduces std 0.016 to 0.019 and shares 0.262, 0.280, 0.457. Three hypercube points exceed the 0.05 floor in at least one seed (max std 0.057 to 0.089), all with mutation at or below 0.0008 (one also with a large sigma share); one-at-a-time, revision 0.4 gives 0.056 in one seed. Even there the amplitude is small. Reading: "the cycles did not appear" holds for the assumed update knobs and most nearby ones; lower mutation is where to look if anyone tries again. The shares match Hauert et al. only at the published point, as before (they move with r and sigma, as they should).

### C4: negotiation v2.1, the disagreement point

Amendment 1 design: arm `fair_default`, seed 0, 57 pairings, each failed week-0 negotiation played both ways (cohabiting with no pot, and apart), 16 one-at-a-time points and 8 hypercube points (1425 runs). Default at HEAD: 26 no-pot households, s_non 0.181 cohabiting against 0.022 apart, difference 0.159 (seed noise: standard error 0.027). The published figures (0.159 against 0.0315, three arms, older code) differ in level but not in direction.

The difference stayed between 0.063 and 0.260 at every point. Living cost (1 to 4 per week) and the connection-need decay (0.15 to 0.6) move it most, because they set how bad cohabiting with no pot is. The outside-option rollout length, the exit floor, the no-pot holdings and the breach load barely move it (the breach load not at all). Caveats that the sweep cannot touch: the extra cost of living alone (1.5 a week) is hardcoded, and "apart scores well" is partly circular, since apart is the outside option the member chose under the same valuation.

### C5: the pleasure demo

Amendment 1 design: arms `v22_bindable` and `baseline`, seed 0, 57 pairings, 14 one-at-a-time points and 8 hypercube points (2622 runs). Default at HEAD: D2a +0.030 (standard error 0.014 with one seed; published +0.03 with 15 seeds), D3 0.477 over 22 households (published 0.47).

D2a stayed positive everywhere: +0.014 to +0.090. It is largest when connection decays fast (0.6: +0.089) and smallest at low points in the hypercube (+0.014, +0.019), where it is within about 1.5 standard errors of zero. So "v2.2 does better than baseline" survives the sweep in sign, but the edge never becomes large; the original caveat (by only +0.03, and it loses on the hand personas) still applies. D3 stayed between 0.41 and 0.53 and tracks the assumed pleasure of a together event almost one for one (Spearman +0.93); at a living cost of 4 only 2 households qualify, so that point says little.

### C6: seed v2, the binding null

`author_seed_v2_bindable` against `author_seed_v2_free_exit` (cards at HEAD), imposed, 57 pairings, seeds 0 to 2, 12 one-at-a-time points and 16 hypercube points (9918 runs). Default at HEAD: difference 0.00036 (published 0.0003). The largest difference anywhere was 0.0098, at a breach load of 0.8 (four times the default), where 6 of 171 runs differ at all. So raising the threshold does start to let a bind hold someone, slowly, and never near the 0.02 margin within the range. The null is robust to the threshold's value; it is not evidence about commitments, for the reason already given in household-seed-v2.md (a threshold rule, not a cost comparison).


## Limits

- Ranges are judgment, mostly half to double. Robust here means robust to these ranges and these parameters. The model structure (state layout, decision rules, leave rule, breach rule) was not varied; where it is hardcoded, the prereg lists it as not sweepable without a code change.
- The labels are mechanical. C3 is labeled fragile at 115 of 128 points (0.898), one point below the line.
- Household rows used one to three seeds per point (the originals used 3 to 15) and 8 (C4, C5) or 16 (C6) hypercube points, so their shares are coarse and lean on the one-at-a-time points. The default-point seed noise is reported beside each.
- The household code has changed since negotiation v2.1 and seed v2 ran, so their default points are recomputed at HEAD and differ from the published numbers.
- Deterministic sweeps are exhaustive at each point but the points are a sample of the parameter space. No interval is given for a share (ADR 0015 point 4 applies to the exact rows).

## Reproduce

`uv run python scripts/multiverse_run.py <part>` for part in horizon, gap, vpggfree, vpggosc, seedv2, negotiation, pleasure, then `summary`. The exact parts take about 7 minutes on a loaded 8-core machine; the household parts take hours there. `uv run pytest tests/test_multiverse.py` checks that each default point reproduces the published number.
