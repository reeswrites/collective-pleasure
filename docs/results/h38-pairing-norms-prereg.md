# H38 pairing norms preregistration (template, ADR 0015)

Status: written and committed before the first run. Nothing here is a result. Scripted persona agents. Model API calls: none.

Design: [h38-pairing-norms-design.md](h38-pairing-norms-design.md). Hypothesis H38 in experiments/hypotheses.jsonl. The freeze on new hedonic hypotheses is lifted for H38 only (author, 2026-11-11).

**Can be about / cannot be about (required).** Using [docs/limits.md](../limits.md):

- **Can be about:** what a fixed, external pairing-pressure dial does to scripted persona agents in the v2-retest household world (baseline rules, may decline, fixes and levers on, exit fallback F4 with items in cell V2), in one parameter point per part; which of the four parts moves pleasure; who bears it, by an assigned values-pairing weight.
- **Cannot be about:**
  - people, or real romantic norms (limit 1: the partner is a script; limit 10: agents feel nothing, three seats, no network). The pressure here is a constant. It does not come from peers and does not respond to how many people pair.
  - a number as such (limit 5): every magnitude (0.02 per level, d = 0.15 per level, 26 weeks of exit stigma, 0.04 intrinsic) is ASSUMED. Only the shape of the dial and the sign of each part are informative, and only within this grid.
  - negotiation outcomes in general (limit 4): formation is judged against a stated outside option (a 26-week rollout living alone or with the friend). Pressure moves that outside option, which is the mechanism under test, so the result is conditional on it.
  - crowding out or internalized norms (limit 3): agents respond to pressure only through their own rollouts and one utility scale.
  - other authors or other models (limit 6).
- **Limits not touched:** limit 2 (the contact veto is not used: withdrawal acts on the agent's own wish to see friends, not on a veto); limit 7 (H32's judging rule); limit 9 (ladder rungs). Limit 8 is addressed by the reachability section, which must pass before the confirmatory run.
- **Known model limits carried in:** the pleasure cap (partly fixed: the unclipped value is recorded and shown); labor and care untracked (not fixed); stay-breach forfeit bypass under settling arms (not touched: the baseline has no stay commitment).

## Purpose and claim

H38: pressure to pair helps coordination and commitment but lowers total pleasure when everyone counts, through pushing would-decline pairs into households, harder exit, and dyadic withdrawal. Pleasure peaks at a low but nonzero pressure, and the harm falls mostly on agents who value pairing least. A result would change how the project treats pairing norms in rule design: whether a mild norm is a hedonic technology or only a cost.

## Design

- **World:** `negotiation.BaselineLived(decline=True)` on the baseline rule set, with `retest.FIXES_ON` and `retest.LEVERS`, exit fallback F4 with `strip_split=True`, items on (`exit_items.GRID["V2-split-loves"]`), 156 weeks.
- **Intrinsic values pairing:** v ∈ {0, 0.5, 1} per persona, assigned from a hash of the persona id; +0.04 × v pleasure per week while living with the partner, in every arm.
- **Arms (confirmatory):** dial levels L0, L0.5, L1, L2, L4. At level L: stigma = reward = exit stigma = 0.02 × L per week; withdrawal d = min(0.6, 0.15 × L); exit stigma lasts 26 weeks.
- **Arms (descriptive): each part alone** at L4 (S4 stigma, R4 reward, W4 withdrawal, X4 exit stigma) and at L1 (S1, R1, W1, X1).
- **Unit of resampling:** the pairing, with its seeds averaged first.
- **Pairings and seeds:** the 15 hand pairings plus 105 others drawn by `retest.sample(105, seed=38)` (120 pairings), seeds 0 to 3. The power check below may change the count before the confirmatory run, by a dated amendment.
- **Pilot pairings:** drawn with a different sample seed (900) and seeds 900 to 901. Excluded from the confirmatory data.
- Everything numeric is ASSUMED (design note).

## Exploratory pilot

To be run after the code lands and before the confirmatory run. Labeled EXPLORATORY, excluded. Results go in Amendment 1 below with the power table.

## Power check

To be filled in Amendment 1 from the pilot, with `mar.stats.seeds_for_power`. If the units chosen are below the units needed for a prediction, that prediction is marked DESCRIPTIVE.

## Predictions

Mean weekly pleasure is over both members and every week of the 156 (everyone counts). Differences are paired by pairing.

| ID | Quantity | Comparison and threshold | Test | Correction | Interval |
|---|---|---|---|---|---|
| P1 (peak low) | Mean pleasure per dial level; L* = the level with the highest mean | L* ∈ {L0.5, L1}, AND pleasure(L*) − pleasure(L0) > 0 | the second clause: paired sign-flip permutation, one-sided | Holm across P1 to P4 | 95% percentile bootstrap, clustered by pairing |
| P2 (high hurts) | pleasure(L4) − pleasure(L0) | < 0 | same, one-sided | Holm | same |
| P3 (helps coordination and commitment) | (a) share of weeks lived together, L4 − L0; (b) share of households that end, among those that ever form, L4 − L0 | (a) > 0, AND (b) < 0 | (a) paired sign-flip, one-sided; (b) same on per-pairing shares | Holm (as one family member: both p must pass) | same |
| P4 (harm on low valuers) | Δ = pleasure(L4) − pleasure(L0) per agent; Δ for v = 0 agents minus Δ for v = 1 agents | < 0 | cluster bootstrap by pairing, one-sided p from the bootstrap | Holm | same |

Shown beside the primary (no verdict weight unless named):

- **S1 (would-decline pairs pushed in):** share of pair-seeds formed at week 0, by level. Among pair-seeds that decline at L0 but form at week 0 at L4, their mean pleasure at L4 minus at L0. Expected: negative.
- **S2 (harder exit):** share of partner-readings "held by pressure", by level. Expected: rises with L; 0 at L0 by construction (cannot fail at L0).
- **S3 (withdrawal):** friend visits per week while living together, L4 vs L0, and W4 vs L0. Expected: lower. This is close to built in (W scales the wish to see friends), so it is a manipulation check, not a finding.
- **S4 (net):** pleasure minus suffering, every level and part.
- **S5 (non-offsettable suffering):** every level and part.
- **S6 (which part):** pleasure, part alone minus L0, at L4 and L1. Expected before the run: stigma does the most harm (it hits everyone who is single, the majority of weeks in this world); reward helps; withdrawal hurts a little; exit stigma hurts a little.
- **S7 (decomposition and cap):** pleasure without the direct pressure terms, by level; unclipped pleasure and share of clipped person-weeks.
- **S8 (liberty with powers):** subsample (the 15 hand pairings, seed 0), L0 and L4.
- **S9 (split by v):** pleasure, net, share of weeks together, for v = 0, 0.5, 1, every level.

## Can every verdict happen?

To be filled and run in Amendment 1, before any confirmatory run. It must show, with free scripted runs or enumeration:

- that P1's verdict and its negation are both reachable (a peak at L0.5 or L1, and a peak at L0 or L2 or L4);
- that each clause of P2 to P4 can fail;
- that each pressure term lands in the pleasure row the primary averages.

## Verdict rule

- **Supported** iff P1, P2, P3 and P4 all hold robustly (point estimate meets the threshold and the 95% interval lies inside it, and the Holm-corrected p < 0.05).
- **Partly supported** iff P2 holds robustly and at least one of P3 or P4 holds robustly, but P1 does not.
- **Not supported** otherwise.
- A clause that holds with the interval crossing its threshold is "weak", not a hold.

## Not testable by design

- Bit-for-bit reproduction: with `pairing=None`, every earlier number is unchanged (test).
- Under L0 no reading can be "held by pressure".

## Limits stated now

Scripted agents; 38 personas, 32 of them grid personas with placeholder principles; one parameter point per part; reward and stigma equal by choice; exit stigma does not deter leaving on distress; one rule set, one exit fallback, one item valuation cell; values pairing is assigned, not elicited.

## Amendments

(none yet)
