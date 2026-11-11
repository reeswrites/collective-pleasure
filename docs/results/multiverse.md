# Multiverse sensitivity sweep (results)

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
| C4 | Negotiation v2.1: living apart beats cohabiting with no pot on non-offsettable suffering by at least 0.02 | running | | | | (household sweep in progress; this row will be filled when it finishes) | |
| C5 | Pleasure demo D2a: seed v2.2 beats the imposed baseline on pleasure | running | | | | (household sweep in progress; this row will be filled when it finishes) | |
| C5b | Pleasure demo D3: relational share of v2.2 households above 0.40 | running | | | | (household sweep in progress; this row will be filled when it finishes) | |
| C6 | Seed v2: binding a stay commitment changes non-offsettable suffering by less than 0.02 (the null) | running | | | | (household sweep in progress; this row will be filled when it finishes) | |
| C7 | VPGG: voluntary beats compulsory on liberty v2 and on empowerment (sum above 0, at least 8 of 15 compositions) | 54 of 54 grid points (1.00) | **robust** | none | n/a (grid) | Holds everywhere tried. The exact count (11 of 15) is not stable: it runs from 8 to 14 with r |
| C8 | VPGG: no oscillation (cooperator-share std below 0.05 in all 3 seeds) | 21 of 24 (0.875) | **fragile** | revision = 0.4 | mutation (+0.61), sigma share (-0.61) | The miss mostly stands, but low mutation or fast revision push the std just over the floor (0.056 to 0.089). Even then the fluctuations are small |

## What to stop saying confidently

Filled in when the household rows finish. From the exact rows so far: the concert boundary (about 3 weeks), the specific "about 29%" greedy loss, the specific "4 to 7 days" friend gap, and the claim that sharing itself (rather than the smaller reunion layer) makes contact more frequent.

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

### C4 to C6: household rows

Running (Amendment 1 design). This section is filled in when they finish.


## Limits

- Ranges are judgment, mostly half to double. Robust here means robust to these ranges and these parameters. The model structure (state layout, decision rules, leave rule, breach rule) was not varied; where it is hardcoded, the prereg lists it as not sweepable without a code change.
- The labels are mechanical. C3 is labeled fragile at 115 of 128 points (0.898), one point below the line.
- Household rows used one or two seeds per point (the originals used 3 to 15) and 8 hypercube points, so their shares are coarse. The default-point seed noise is reported beside each.
- The household code has changed since negotiation v2.1 and seed v2 ran, so their default points are recomputed at HEAD and differ from the published numbers.
- Deterministic sweeps are exhaustive at each point but the points are a sample of the parameter space. No interval is given for a share (ADR 0015 point 4 applies to the exact rows).

## Reproduce

`uv run python scripts/multiverse_run.py <part>` for part in horizon, gap, vpggfree, vpggosc, seedv2, negotiation, pleasure, then `summary`. The exact parts take about 7 minutes on a loaded 8-core machine; the household parts take hours there. `uv run pytest tests/test_multiverse.py` checks that each default point reproduces the published number.
