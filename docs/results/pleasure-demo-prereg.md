# Pleasure demonstration preregistration (template, ADR 0015)

Status: written and committed before the first confirmatory run. Nothing here is a result. Scripted agents: the persona-driven household agents of ADR 0010 (no model). Model API calls: none.

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

## Purpose and claim

The author confirmed seed v2.2 on one condition, verbatim: "yes as long as it can demonstrate pleasure in relationships hedonic technology" (docs/seeds/author-household-norms-2026-11-10.md, "Confirmation of seed v2.2"). The condition reads as: rules, as a technology for producing pleasure, must produce pleasure in relationships and not only prevent harm. This experiment asks whether, in the household world, seed v2.2 does that, and where the pleasure comes from. It does not test the seed's wording (the author confirmed that) and it does not test whether the model's pleasure is real pleasure (it is a modeled gloss).

What would change a decision: if the households that agree under v2.2 do not end in the upward spiral, or if their pleasure comes only from individual needs, or if living with the partner produces no more pleasure than living apart, then "demonstrates pleasure in relationships" is not supported in this model and the seed's confirmation stays conditional. If v2.2 does not beat the imposed baseline (D2), the demonstration stands only as "does not lose pleasure to the protections it adds", which this page will say plainly.

## Design

- World: the weekly household world (`src/mar/worlds/household.py`), 156 weeks, shocks from the common-random-number schedule (same shocks in every arm for a given pairing and seed). Hedonic model of ADR 0010, unchanged. Read-only use.
- Arms: (1) `v22_bindable` and (2) `v22_free_exit`: seed v2.2 variants, negotiation v2.1 protocol (`NG.week0` then `NG.Lived(..., apart=True)`): fair-default-v2 start (one shared pot, open use, `FAIR_DEFAULT`), exit floor ON, a failed negotiation means living apart, reviews and retries every 13 weeks; (3) `baseline` and (4) `trap` (control): the imposed household v2 rule sets run with `run_weekly` (no negotiation).
- Pairings: all 57 of negotiation v2.1: the 15 unordered pairs of the six hand personas (Anchor, Bargainer, Host, Peacekeeper, Steward, Wanderer) and the 42 ordered pairs that include a pressing persona (Controller, Free-rider, Overasker). The 57 are an enumeration of every pairing of this persona set, not a sample of pairings.
- **Unit of resampling.** Primary tests (D2, D3): the run, i.e. one pairing x seed, matched across arms (same pairing, same seed, same shocks), with the 95% intervals resampling WHOLE PAIRINGS (cluster bootstrap), which is the stricter reading that treats the 57 pairings as a sample. Each of D2 and D3 also reports the same test on pairing means as a secondary line. D1: the pairing (its seeds clustered into one yes/no). D4: the run, unpaired, interval clustered by pairing. D5: descriptive.
- Fixed parameters and everything ASSUMED: every constant of the hedonic model and the household world (ADR 0010, `HedonicConfig`, `TRUST` block in the world). **Trust parameters are assumed with no data behind them** (start 0.7, breach drop 0.3, recovery rates, thresholds). Persona needs, aspirations and weights are assigned. Detection and compliance are perfect. Negotiation values are the closed-form proxies of negotiation v2.
- Seeds: 0 to 14 (15 seeds per pairing), from the power check below. The pilot seeds (900, 901, 902) are not in the confirmatory data. Total 57 x 4 x 15 = 3420 runs.
- Determinism: each run clears the negotiation rollout caches first, so its result does not depend on which runs a worker executed earlier (the scheduling dependence recorded in negotiation v2.1, prediction 5). This is a deliberate difference from the v2.1 script.
- Instrument: the hedonic model does not expose its pleasure terms. `mar.pleasure_report.RecHedonic` recomputes them each week from the model's own state (needs met, aspirations satisfied, time-together events, new-connection glow) and checks that they add up to the model's pleasure (max error recorded; must be under 3e-4). The model itself is not modified; a test checks that instrumenting changes no outcome.

### Pleasure by source (defined here, before any confirmatory run)

The model's weekly pleasure flow is 0.5 x (needs met: rest, connection, money, security) + 0.5 x (aspirations satisfied: security buffer, time together, friends, savings, autonomy) + 0.10 x time-together sessions + the glow of a new connection. Each term is a source:

- **Individual:** the rest, money and security needs; the security-buffer, savings and autonomy aspirations.
- **Relational:** time together (the time-together aspiration and the time-together events), connection (the connection need, fed only by living with a partner, time together, friends and friend-initiated contact), friends (the friends aspiration), new connections (the glow). Of these, **time together** is the partner-specific source.
- Honored requests, kept commitments and shared-pot use have no pleasure term of their own in the model. They can only act through trust, through what the partners are allowed to do, and through the actions the partners take. They are reported as descriptive counts (pathways), never as a share of pleasure.

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

Run: seeds 900, 901, 902; 12 pairings (the first 6 and last 6 of the 57); all four arms; 144 runs, 10 seconds (0.07 s per run on 8 cores). Command: `uv run python scripts/pleasure_demo.py --pilot`. Excluded from the confirmatory data. All thresholds and margins below were written down before the pilot output was read; the pilot changed none of them.

What it showed (for powering only): `v22_bindable` and `v22_free_exit` gave identical pleasure in all 36 matched runs (commitments to stay are rarely negotiated and change nothing when they are; 3 of 36 negotiated bundles had a stay term). Mean pleasure 0.792 (v2.2) vs 0.800 (baseline) vs 0.725 (trap). Households upward 0.89 (v2.2), 0.81 (baseline), 0.31 (trap). The agreed households had mean pleasure 0.877 and the living-apart ones 0.726. Relational share of pleasure 0.41 to 0.44 in every arm. No household's trust fell below 0.5 (D5 has no variation in the pilot).

| Quantity | Pilot effect over margin | Pilot sd of the unit | Source file |
|---|---|---|---|
| D2 v2.2 minus baseline (matched runs, n=36) | -0.0077 | 0.0787 | runs/pleasure-demo/pilot.json.gz |
| D2 v2.2 minus trap, over its 0.05 margin (n=36) | +0.0176 | 0.1140 | same |
| D3 relational share of v2.2 households minus 0.40 (n=15) | +0.0675 | 0.0552 | same |
| D4 agreed minus apart (14 and 12 runs) | +0.151 | 0.0397 (pooled) | same |
| D1 pairing-majority upward, v2.2 | 12/12 pairings | n/a | same |

The pilot is small: 12 pairings, and the effect of D2 against baseline is about a tenth of its own spread. The power numbers are only as good as these estimates.

## Power check (required)

Computed with `mar.stats.seeds_for_power(effect, sd, target=0.8, alpha=0.05, paired=True, alternative="greater")` (simulated, 150 simulations per step), cross-checked with `mar.stats.seeds_for_margin`. Unit = pairing x seed run, so seeds per pairing = units / 57. A pilot effect at or below its margin cannot be powered for a hold; for those the check was run on the absolute effect (the units that would resolve the pilot's own estimate as a robust miss).

| Prediction | Margin | Spread used | Units for 80% power (simulated / closed form) | Seeds per pairing | Units chosen | Cost at that n |
|---|---|---|---|---|---|---|
| D2a, D2b (v2.2 vs baseline) | > 0 | 0.0787 | 691 / 830 for \|effect\| 0.0077 | 13 / 15 | 855 (15 seeds) | 3420 runs, about 5 minutes |
| D2c, D2d (v2.2 vs trap) | > +0.05 | 0.1140 | 244 / 331 for +0.0176 | 5 / 6 | 855 | same |
| D3 | > 0.40 | 0.0552 | 6 / 6 for +0.0675 | 1 | 855 | same |
| D4 | > 0 | 0.0397 | 4 per arm / 4 per arm for +0.151 | n/a (needs a few agreed and apart runs of each) | about 15 to 30 per arm expected | same |
| D1a, D1b | > 0.5 share of pairings | binomial | exact power at 57 pairings: 0.99 if the true share is 0.8; 0.66 if 0.7 | 15 (odd, so a majority is defined) | 57 pairings | same |

Chosen: 15 seeds per pairing for every arm. The tightest requirement is D2 against baseline (15 by the closed form, 13 by simulation); that comparison can resolve a difference of about 0.0065 in mean pleasure at 855 matched runs per arm. The between-pairing spread of the D2-trap difference does not shrink with seeds; the pairing-level secondary tests use only 57 units and are underpowered for D2 (stated, not hidden). If a result row needs more than this to be read as confirmatory it is marked DESCRIPTIVE in the results page.

## Predictions

Eight confirmatory predictions form one Holm family (alpha 0.05, Holm-adjusted p one-sided). D5 is descriptive and outside the family. Each prediction names its quantity; a prediction with several clauses holds only if every clause holds. "Pleasure" of a run is the mean over weeks and both partners of the model's weekly pleasure flow.

| ID | Quantity (formula) | Unit of resampling | Comparison and threshold or margin | Test | Alpha | Correction family | Interval reported |
|---|---|---|---|---|---|---|---|
| D1a | Share of the 57 pairings in which a majority of the 15 seeds end with BOTH partners in the upward spiral (oracle `spiral_class`: position at least 0.20 above the tipping point and no non-offsettable suffering in the last 8 weeks), `v22_bindable`. Run-level upward rate also reported. | pairing (seeds clustered) | share > 0.50 | exact one-sided binomial against 0.5 (`sign_test`) | 0.05 | Holm across D1a, D1b, D2a to D2d, D3, D4 | Clopper-Pearson 95% |
| D1b | Same, `v22_free_exit` | pairing | share > 0.50 | same | 0.05 | same | same |
| D2a | Mean pleasure, `v22_bindable` minus `baseline`, matched on pairing and seed | run (pairing x seed), CI clusters pairings | difference > 0.00 | paired sign-flip permutation over runs, one-sided (20,000 draws) | 0.05 | same | percentile cluster bootstrap 95% by pairing; Cohen's dz; Cliff's delta |
| D2b | Same, `v22_free_exit` minus `baseline` | same | > 0.00 | same | 0.05 | same | same |
| D2c | Mean pleasure, `v22_bindable` minus `trap`, matched | same | > +0.05 | same, against trap + 0.05 | 0.05 | same | same |
| D2d | Same, `v22_free_exit` minus `trap` | same | > +0.05 | same | 0.05 | same | same |
| D3 | Relational share of a run's pleasure = (time together + connection + friends + new connections) / total pleasure, in `v22_bindable` households (those living together at least 90% of the 156 weeks); free-exit is identical in the pilot and is reported beside it, not pooled (pooling identical runs would count them twice) | run, CI clusters pairings | mean share > 0.40 (substantial: two fifths or more of pleasure is relational, in a model where relational sources are 5 of 11 terms) | one-sample sign-flip permutation of (share - 0.40) | 0.05 | same | percentile cluster bootstrap 95% |
| D4 | Mean pleasure of runs that ended as an agreed household (pot at week 0, both partners still in at week 156) minus runs that never agreed and stayed apart for all 156 weeks, `v22_bindable` | run, unpaired; CI clusters pairings | difference > 0.00 | two-arm one-sided permutation (`permutation_test`) | 0.05 | same | percentile cluster bootstrap 95%; Cohen's d; Cliff's delta |
| D5 (descriptive) | Mean pleasure of v2.2 households (together at least 90% of weeks) in which neither partner's trust ever fell below 0.5 (the model's "full" level), minus the households in which it did | run, CI clusters pairings | none (no verdict wording) | none | n/a | outside the family | cluster bootstrap 95%; Cliff's delta; Spearman correlation of mean trust with pleasure |

Secondary and descriptive lines (no verdicts): the same D2 and D3 tests on pairing means; the free-exit twin of every `v22_bindable` number; D4 companion (each apart run minus the same pairing and seed living together under the imposed baseline); the spiral shares of all four arms (up, stalled, down); pleasure by source for all four arms; descriptive counts of honored requests, commitments made and kept, shared-pot draws and contributions, gifts, time-together sessions and new-connection events in agreed households; the model's own fail rate (6 or more consecutive weeks of non-offsettable suffering). D4 is confounded by who the pairing is (apart households come mostly from particular pairings); the companion line is the paired check, and the results page will say which way they agree.

Effect sizes reported for every comparison: difference with CI; Cliff's delta (and Cohen's d where roughly normal); rate intervals exact.

## Verdict rule

Label for each prediction (all clauses must hold): **holds robustly** = the point estimate meets the threshold AND the 95% interval lies inside it AND the Holm-adjusted p is at most 0.05; **holds but CI crosses threshold** = the point estimate meets it but one of those fails (weak support, not counted as confirmed); **miss robust** = the point estimate misses and the interval lies wholly outside the threshold; **miss but CI crosses threshold** otherwise. D1a, D1b, D2a to D2d, D3, D4 take a label; D5 takes none.

Two summary statuses, fixed now:

- **Pleasure in relationships is demonstrated (the author's condition)** iff D1a, D1b, D3 and D4 all hold robustly: households agree into the upward spiral, much of their pleasure is relational, and living together produces more pleasure than living apart.
- **v2.2 adds pleasure over the alternatives** iff D2a and D2b hold robustly (beats baseline) and D2c and D2d hold robustly (beats the trap control). This is a stronger, comparative claim and is reported separately; a miss on D2 does not by itself fail the demonstration, but the results page states it as a finding.

If `v22_bindable` and `v22_free_exit` are again identical run for run, D1a/D1b (and D2a/D2b, D2c/D2d) are one observation reported twice, the Holm family counts them as two (conservative), and the results page says so and does not read agreement between them as replication.

## Not testable by design

The instrument round trip (recomputed terms equal the model's pleasure; instrumenting changes no outcome) is a deterministic check reported as pass or fail with the maximum error, not given an interval.

## Limits stated now

- Pleasure here is a modeled gloss; agents feel nothing. Scripted persona-driven agents with assigned preferences; the persona weights decide which sources can matter, so a relational share is partly built in by the assigned weights and the connection clock, not discovered.
- The hedonic model, the world constants and the trust parameters are assumed (trust: no data). Trust is a modeled consequence of breaking a chosen commitment; in the pilot it almost never moved, so D5 may have no low-trust households and will then say so.
- Honored requests, kept commitments and shared-pot use are reported only as counts because the model has no pleasure term for them; the pilot found negotiated commitments in only 3 of 36 bundles.
- 57 pairings of one persona set; one parameter point; the pairings are an enumeration, so intervals that treat them as a sample are conservative and intervals that treat only seeds as random are not.
- D4 compares different runs of mostly different pairings; the paired companion is descriptive.
- A household "apart" for 156 weeks is the world's solo mode (alone or with Friend C), designed as an outside-option valuation, not as a life.
- The baseline and trap sets are imposed rule sets without negotiation, so a D2 difference mixes the rules' content with the presence of negotiation and of living apart.

## Amendments

None yet.
