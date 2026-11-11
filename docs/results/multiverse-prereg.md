# Multiverse sensitivity sweep preregistration

Status: written and committed before the first sweep run. Nothing here is a result. Scripted agents and exact solves only. Model API calls: none. Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state (ADR 0010).

Only one kind of run happened before this file: timing calls at the default settings (one horizon table, one friend-gap curve), which reproduce numbers already published in docs/results/horizon.md. No point off the defaults was run.

## Purpose

Almost every result in docs/results/ rests on parameters marked ASSUMED in the code. This sweep asks, for eight headline conclusions, whether the conclusion survives when those parameters move across a plausible range, and if not, which parameter flips it. It changes no committed verdict. It adds a robustness label next to the claims (docs/claims.md) that turn out fragile. The author asked for it on 2026-11-10 ("Yes, start both", experiments/changes.jsonl).

## Method

- Code: `src/mar/multiverse.py` (new) and `scripts/multiverse_run.py` (new). Existing modules are imported read-only. Parameters are varied only through dataclass fields, function arguments, or module globals that the code reads at call time (patched in memory, in each worker process). A parameter that can only change by editing a module is recorded as "not sweepable without a code change" and is not varied.
- Two designs per conclusion.
  1. **One at a time (OAT).** Each parameter is set to the low and the high end of its range, everything else at the default. This names single parameters that flip the conclusion.
  2. **Latin hypercube (LHS).** N points over all the conclusion's parameters at once, seeded (seed 20261110). Ranges marked "log" are sampled uniformly on a log scale; integer sets are sampled uniformly over the set. This gives the share of the multiverse where the conclusion holds.
- **Flipping parameter.** Any OAT endpoint where the conclusion fails is named. From the LHS, the parameter with the largest absolute Spearman rank correlation with the conclusion's margin (the quantity minus its threshold, signed so positive means it holds) is also named.
- **Default range rule.** Half to double the default, log scale, unless a reason is given. Literature bounds are marked "from memory, verify". Structural integers (caps) move by one step each way.
- **Household runs are stochastic.** Their conclusions use point estimates at each multiverse point, with fewer seeds than the original runs, to keep the sweep cheap. The seed noise at the default point is reported beside each household row, so a point that "fails" by less than two standard errors is flagged as noise, not as a flip.

## Labels (the robustness criterion)

For each conclusion:

- **robust**: holds in at least 90% of LHS points, and no OAT endpoint flips it.
- **fragile**: holds in 50% to 90% of LHS points, or in at least 90% but at least one OAT endpoint flips it.
- **flips**: holds in fewer than 50% of LHS points.

If the default point itself does not reproduce the published conclusion at the current code (HEAD), the row is labeled **not reproduced at HEAD** and the sweep for it is reported as descriptive.

## The eight conclusions, quantities and criteria

### C1. Horizon: greedy loses materially (docs/results/horizon.md section 3)

- Claim: greedy play loses a large share of lifetime pleasure for a patient planner; "large" was declared as 10% of optimal; up to about 29% at gamma 1 over 52 weeks.
- Quantity: greedy loss, percent of optimal, from START, 26 weeks, gamma 0.95 (`horizon.greedy_loss`).
- Holds if: loss at least 10%. Reported beside it, no verdict: loss at gamma 1 over 52 weeks (the "29%").
- LHS: 128 points. Parameters shared with C2 (below).

### C2. Horizon: the concert is negative weekly and positive spaced, boundary about 3 weeks (P5)

- Quantity: net carryover of a concert every m weeks, 26 weeks, gamma 0.95 (`horizon.concert_gain`, recomputed with the same public building blocks, `Table`, `schedule_value`, `constrained_value`, so the four tables per point are built once).
- Holds if: net carryover at m = 1 is below 0 AND at m = 4 is above 0. Secondary (reported, labeled the same way): the boundary m* (smallest m in 1 to 8 with net carryover above 0) is 2, 3 or 4.

Parameters for C1 and C2 (`HorizonParams`, every field ASSUMED in the code). bF stays at 10 (it sets the scale). bK is tied to bX (the code's own rule: with no carryover a concert is worth exactly a free treat).

| Parameter | Default | Range | Reason |
|---|---|---|---|
| delta (adaptation per tolerance level) | 0.2 | 0.1 to 0.4, log | half to double |
| rho (anticipation per week of spacing) | 0.25 | 0.125 to 0.5, log | half to double |
| nuD (cost of a starved need) | 2 | 1 to 4, log | half to double |
| beta (commitment payoff) | 1.5 | 0.75 to 3, log | half to double |
| f (commitment friction) | 3 | 1.5 to 6, log | half to double |
| mu (good-memory payoff) | 0.5 | 0.25 to 1, log | half to double |
| muz (rumination cost) | 1 | 0.5 to 2, log | half to double |
| theta (acquired taste gain) | 0.1 | 0.05 to 0.2, log | half to double |
| kappa (bond gain) | 0.5 | 0.25 to 1, log | half to double |
| bR (alternative, fresh) | 7 | 5 to 9, linear | must stay below the favorite (10) to keep its meaning |
| bS (ritual base) | 6 | 3 to 12, log | half to double |
| bX = bK (treat, concert base) | 12 | 8 to 16, linear | half to double would make the treat worth less than saving or far above everything; two thirds to four thirds instead |
| bV (saving comfort) | 1 | 0.5 to 2, log | half to double |
| A (tolerance cap) | 4 | 3, 4, 5 | one step |
| W (anticipation cap) | 3 | 2, 3, 4 | one step |
| C (commitment length) | 3 | 2, 3, 4 | one step |
| kcontrast (tolerance a concert adds) | 1 | 0, 1, 2 | one step |
| vK (concert vividness) | 2 | 1, 2, 3 | one step |

Not varied: the state layout and transition rules (hardcoded in `step`, not sweepable without a code change), M, T, B, Z, P caps, vS, kcost, ritual_rest (kept at default to bound the table size), gamma and horizon (they are the conditions of the claim, not assumptions).

### C3. Horizon amendment: with shared activities, the best friend-contact gap is about weekly (A1)

- Claim: with shared-experience amplification the best days between contacts is 4 to 7 at overlap 0.7 (against 19 to 139 before). The per-contact cost (7.2) was set after a smoke look, so it is stressed hardest.
- Quantity: best gap (`horizon.amp_best`, gmax 200) at overlap 0.7 for friendship half-lives H = 10, 20, 45, 90 days; and the same with the reunion-only control (`AmpParams(activities=())`).
- Holds if: the largest best gap over the four H is at most 14 days (A1b's line). Secondary 1: at most 7 days (the "4 to 7" headline). Secondary 2: shared activities shorten the best gap against the control by at least 1 day for every H (A1c).
- LHS: 128 points. OAT adds two extra points for the per-contact cost: 24 (the old special-meeting cost, unscaled) and 0.

| Parameter | Default | Range | Reason |
|---|---|---|---|
| cost_sess (logistics per contact) | 7.2 | 1.8 to 28.8, log | quarter to four times: tuned after the smoke run, stressed hardest |
| cost_occ (logistics per shared occasion) | 0.8 | 0.4 to 1.6, log | half to double |
| A (amplification strength) | 1 | 0.5 to 2, log | half to double. Boothby, Clark and Bargh 2014 report amplification but give no number we can map (from memory, verify) |
| kappa (penalty for low overlap) | 0.5 | 0.25 to 1, log | half to double |
| tau_s (habituation days) | 3 | 1.5 to 6, log | half to double |
| amp_bad (amplification of bad occasions) | 1 | 0.5 to 2, log | half to double |
| m_scale (size of the reunion layer) | 0.3 | 0.15 to 0.6, log | half to double |
| activity base scale (all `Activity.base` times this) | 1 | 0.5 to 2, log | half to double |
| sociability excess scale (soc = 1 + s x (soc_default - 1)) | 1 | 0.5 to 2, log | half to double of how far each activity is from neutral |
| GapParams tau_w | 7 | 3.5 to 14, log | half to double |
| GapParams tau_a | 60 | 30 to 120, log | half to double |
| GapParams reset | 0.6 | 0.3 to 0.9, linear | must stay a share |
| GapParams thr | 6 | 3 to 12, log | half to double |
| GapParams rel | 1.5 | 0.75 to 3, log | half to double |
| SelfParams nu (memory weight) | 0.01 | 0.005 to 0.02, log | half to double |
| SelfParams tau_m (memory decay, days) | 45 | 22.5 to 90, log | half to double |

Not varied: the activity list itself (rates and caps), the functional form of the multiplier, the "choose" rule (both are structural; choose = False was reported in the amendment as A3b).

### C4. Negotiation v2.1: the disagreement point decides the sign (NG3)

- Claim: when a failed negotiation means living apart, the households that failed to agree have much less non-offsettable suffering than when it means sharing a house with no pot (0.0315 against 0.159).
- Quantity: for the same week-0 negotiations, mean s_non of no-pot households played the v2 way (cohabiting, no pot) minus mean s_non of the same households played the v2.1 way (apart). One seed (0), 57 pairings, the three arms (`NG.ARMS`), each played both ways, base cards `author_seed_v2_bindable` at HEAD, floor on.
- Holds if: the difference is at least 0.02 (apart is lower by at least 0.02).
- LHS: 16 points. OAT on every parameter.

| Parameter | Default | Range | Reason |
|---|---|---|---|
| OUT_WEEKS (outside-option rollout length) | 26 | 13, 26, 52 | half to double |
| FLOOR (exit floor, money) | 26 | 13 to 52, log | half to double |
| NO_POT_MONEY (holdings with no pot) | 55 | 40 to 70, linear | plus or minus about a quarter: it is pot money plus private money |
| BREACH_N (load at which a bound partner breaks) | 0.2 | 0.1 to 0.4, log | half to double |
| HedonicConfig living_cost | 2 | 1 to 4, log | half to double |
| HedonicConfig denied_below | 0.15 | 0.075 to 0.3, log | half to double |
| HedonicConfig conn_decay | 0.3 | 0.15 to 0.6, log | half to double |
| HedonicConfig onset_weeks | 4 | 2, 4, 8 | half to double |

Not sweepable without a code change: the extra weekly cost of living alone (1.5, hardcoded in `worlds/household.py`), the leave rule (4 low weeks or load 0.2, hardcoded), the breach and fine coefficients and term-value table in `negotiation.py`, the alone versus Friend C rule.

### C5. Pleasure demo: seed v2.2 beats the imposed baseline, and the relational share is above 0.40 (PD D2a, D3)

- Quantity D2a: mean pleasure, `v22_bindable` minus `baseline`, matched on pairing and seed. Quantity D3: mean relational share of `v22_bindable` households (together at least 90% of weeks). Seeds 0 and 1 (the original used 15), 57 pairings, run exactly as `scripts/pleasure_demo.py::run_task` does.
- Holds if: D2a above 0. D3 is reported with its own label: above 0.40.
- LHS: 16 points. OAT on every parameter.

| Parameter | Default | Range | Reason |
|---|---|---|---|
| HedonicConfig living_cost | 2 | 1 to 4, log | half to double |
| HedonicConfig conn_decay | 0.3 | 0.15 to 0.6, log | half to double |
| HedonicConfig conn_together | 0.3 | 0.15 to 0.6, log | half to double |
| HedonicConfig together_event | 0.1 | 0.05 to 0.2, log | half to double |
| HedonicConfig denied_below | 0.15 | 0.075 to 0.3, log | half to double |
| HedonicConfig eta (spiral speed) | 0.3 | 0.15 to 0.6, log | half to double |
| BREACH_N | 0.2 | 0.1 to 0.4, log | half to double |

Not sweepable without a code change: persona weights are data files, not parameters, and are not varied here (they are the pairings); the leave rule; the relational source list in `pleasure_report.RELATIONAL` (a definition, not an assumption).

### C6. Author seed v2: binding a stay commitment changes nothing (SV2, the null)

- Claim: bindable and free-exit variants give the same non-offsettable suffering (difference 0.0003), because the scripted agent breaks a stay commitment at a fixed load.
- Quantity: mean s_non, `author_seed_v2_bindable` minus `author_seed_v2_free_exit` (cards at HEAD, imposed, no negotiation), matched on pairing and seed, over 57 pairings and seeds 0 to 2.
- Holds (the null holds) if: the absolute difference is below 0.02 (the original prediction's margin).
- LHS: 16 points. OAT on every parameter.

| Parameter | Default | Range | Reason |
|---|---|---|---|
| BREACH_N | 0.2 | 0.05 to 0.8, log | quarter to four times: this is the parameter the null is said to come from, so stressed hardest |
| HedonicConfig denied_below | 0.15 | 0.075 to 0.3, log | half to double |
| HedonicConfig onset_weeks | 4 | 2, 4, 8 | half to double |
| HedonicConfig conn_decay | 0.3 | 0.15 to 0.6, log | half to double |
| HedonicConfig living_cost | 2 | 1 to 4, log | half to double |
| HedonicConfig trapped_intensity | 0.5 | 0.25 to 1, log | half to double |

Not sweepable without a code change: the breach decision rule itself (a threshold, not a cost comparison). That is the real reason given for the null, so this row can only show whether the threshold's value matters, not whether a cost-sensitive agent would be held.

### C7. VPGG freedom: voluntary beats compulsory on liberty v2 and on empowerment (LB2, EM1)

- Quantities: over the 15 compositions of four others, (a) liberty v2 voluntary minus compulsory, summed, and the number of compositions where voluntary is strictly higher; (b) the same for empowerment (bits).
- Holds if: for both measures the sum is above 0 AND voluntary is strictly higher in at least 8 of 15. The published values are 11 of 15 for both (+5.263 bits for liberty).
- Full grid, not LHS (it is cheap and exact): r in {2, 2.5, 3, 3.5, 4, 4.5}, sigma as a share of (r - 1)c in {0.25, 0.5, 0.75}, horizon k in {2, 3, 4}, c = 1, N = 5. 54 points. Range reason: the model requires 1 < r < N and 0 < sigma < (r - 1)c; the grid covers that space evenly. The default is r = 3, sigma = 1 (share 0.5), k = 3. OAT is the grid's own rows through the default.

Not sweepable without a code change: N (the 15 compositions assume four others), the class table is a definition and is not varied, the state key (holdings rounded) and the fallback action.

### C8. VPGG: no oscillation (RD-VPGG, the robust miss)

- Claim: the cycles of Hauert et al. 2002 did not appear; the cooperator share's standard deviation after burn-in is about 0.015 against a floor of 0.05.
- Quantity: `std_c` from `mar.games.vpgg.run`, voluntary regime, 3 seeds per point (0, 1, 2), 3000 generations, burn-in 500.
- Holds (no oscillation) if: std_c is below 0.05 in all three seeds.
- LHS: 24 points. OAT on every parameter.

| Parameter | Default | Range | Reason |
|---|---|---|---|
| revision (share revising per generation) | 0.1 | 0.05 to 0.4, log | half to four times: the update knob most likely to matter for cycles |
| mutation | 0.002 | 0.0005 to 0.008, log | quarter to four times: noise damps cycles |
| pop | 5000 | 1000 to 10000, log | a fifth to double (larger is slower) |
| rounds (games per generation) | 5 | 1 to 10, integer | averaging over rounds smooths payoffs |
| r | 3 | 2.2 to 4.5, linear | must be between 1 and N = 5 |
| sigma share of (r - 1)c | 0.5 | 0.25 to 0.75, linear | must be between 0 and 1 |

Not sweepable without a code change: the imitation rule (proportional, one random model), group formation, uniform mutation. These are the "update knobs" the VPGG results file says were assumed; only their rates can move.

### Not included, and why

- Bargaining: the Rubinstein and outside-option checks are closed forms, an implementation check with no assumed behavioral parameter; clause 4b is already a miss whose interval crosses its slack.
- Evolution, ladder and live-model rows: not cheap or not scripted.

## Limits stated now

Ranges are judgment, mostly half to double. A conclusion robust here is robust to these ranges and these parameters, not to the model's structure. Household rows use fewer seeds than the original runs. The household code has changed since negotiation v2.1 and seed v2 ran, so their default points are recomputed at HEAD and may differ from the published numbers. Parameters are patched in memory, never in files.

## Amendments

None yet.
