# <Experiment name> preregistration (template, ADR 0015)

Copy this file to `docs/results/<name>-prereg.md`, fill every field, and commit it BEFORE any run that could inform a prediction. Delete the guidance text in brackets. Do not edit a prediction after the first non-exploratory run starts; add a dated amendment instead. Results go in `docs/results/<name>.md` and the statistical reading in the retrofit table (`scripts/stats_retrofit.py`).

Status: written and committed before the first run. Nothing here is a result. Scripted or model agents: <which>. Model API calls: <none | list with a cost cap>.

**Can be about / cannot be about (required).** Name what this result can be about and what it cannot be about, using [docs/limits.md](../limits.md). List each limit there that applies, and say which are not touched.

## Purpose and claim

[One paragraph. Which claim id in docs/claims.md does this test? What would change a decision?]

## Design

- World, rule variants, agents, conditions: <fixed list>.
- **Unit of resampling** (what counts as one independent observation): <seed | run | pairing, with its seeds clustered together | persona>. If runs of the same pairing or rule set share structure, the pairing is the unit, not the seed.
- Fixed parameters and everything ASSUMED: <list, flagged>.
- Seeds: <list or range> chosen by the power check below.

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

[A small run used only to estimate effect and spread. State what was run, what you saw, and that it is excluded from the confirmatory data.]

| Quantity | Pilot effect | Pilot sd of the unit | Source file |
|---|---|---|---|
| <quantity> | <e> | <sd> | <path> |

## Power check (required)

Computed with `mar.stats.seeds_for_power(effect, sd, target=0.8, alpha=0.05, paired=<bool>)` (simulated), cross-checked with `seeds_for_margin`.

| Prediction | Margin | Spread used | Units for 80% power | Units chosen | Cost at that n |
|---|---|---|---|---|---|
| P1 | <m> | <sd> | <n> | <n> | <$ or minutes> |

If the units chosen are below the units needed, say so here and mark the prediction DESCRIPTIVE (no verdict wording), not confirmatory. LLM runs: seeds come from this table, not a default of 3.

## Predictions

Each row is one prediction. A prediction with several clauses holds only if every clause holds. Thresholds are numbers.

| ID | Quantity (formula) | Unit of resampling | Comparison and threshold or margin | Test | Alpha | Correction family | Interval reported |
|---|---|---|---|---|---|---|---|
| P1 | <e.g. mean cooperation, exit-allowed minus no-exit> | <pairing> | <>= -0.01> | <paired permutation, one-sided, exact if 2^n small> | 0.05 | <Holm across P1 to Pk> | <95% percentile bootstrap, clustered by pairing> |
| P2 | <e.g. share of runs where X happens> | <run> | <>= 0.6> | <exact binomial against 0.6, one-sided> | 0.05 | <same family> | <Clopper-Pearson 95%> |

Effect sizes reported for every comparison: difference with CI; Cliff's delta (or Cohen's d if the quantity is roughly normal); risk difference and ratio for rates.

## Can every verdict happen? (required)

[Fill this in and run it BEFORE any confirmatory run. A free check is enough: a mock agent, a scripted agent, or a brute-force search over the design. Paid or long runs may not start until this section shows a pass.]

- **Every verdict is reachable.** For each verdict the rule above can return, including "supported", name a free run (mock, scripted or brute force) that produces it in this design. If no input could produce a verdict, the design is broken: fix it before the run, or say plainly that the verdict cannot happen.
- **Every prediction clause can fail.** For each clause of each prediction, show an input under which it fails. A clause that holds whatever the agents do is a property of the code, not a result. Mark it "cannot fail" and give it no verdict weight.
- **Count the open cells.** If the verdict needs a pattern in k of n cells, count how many cells could show the pattern at all, given which arms ignore which parameters. If fewer than k are open, "supported" is unreachable.
- **The metric can see the mechanism.** For each predicted cost or gain, trace where it lands in the code (which field, which sum) and check that the outcome measure includes it.

| Verdict or clause | Free check that reaches it (or makes it fail) | Command or file | Result |
|---|---|---|---|
| <supported> | <mock or scripted run, or enumeration> | <path> | <reached / not reachable> |
| <P1 clause 1 fails> | <> | <> | <> |

Why this is required: ADR 0015, amendment 2026-11-11 (two cases where a verdict could not happen: IT1, and the H32 cell count).

## Verdict rule

[How the predictions combine, for example "rediscovered iff P1, P2 and P3 hold". State the statistical label that counts as a hold. Default: the point estimate meets the threshold AND the 95% interval lies inside it ("holds robustly"); "holds but CI crosses threshold" is reported as weak support and is not counted as a confirmed hold for any claim that would be cited.]

## Not testable by design

[List deterministic checks (proof verdicts, exhaustive enumerations, instrument round trips). They are reported as passes or failures, not given intervals.]

## Limits stated now

[Scripted agents, small persona set, single parameter point, single model version, and so on.]

## Amendments

[Dated. Each says what changed, that it was committed before the affected run, and that no threshold was moved after seeing data.]
