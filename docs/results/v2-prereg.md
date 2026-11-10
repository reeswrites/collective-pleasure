# V2 preregistration (committed before any V2 code runs)

Status: predictions for instrument calibration. Nothing here is a research result. All agents are scripted mocks; no LLM, no network at run time, no GovSim.

## Setup (fixed now)

- Fishery (ASSUMED in-repo harness, ADR 0003): pool starts 100, capacity 100; at month end the remaining stock doubles, capped at 100 (GovSim-style dynamics, Piatti et al. 2024, arXiv 2404.16698). N = 4 agents, M = 6 months, up to 12 sub-rounds per month; in each sub-round each agent may submit one harvest action, so an agent can submit several actions per month. Seeds 0 to 49 for mining.
- Planted seam: per-action cap (no single harvest above 10) with NO per-month total cap.
- Written (de jure) seamed spec: F1 no catch above 10 per action; F2 no catch above the pool; F3 no negative catch; F4 may harvest (permission, no constraint).
- Scripted patch P1: no combined catch above 40 fish in a month (month_total + catch <= 40).
- Deliberately conflicting patch C1: "must catch at least 20 per action", added beside F1.
- Oracle thresholds (frozen now): pool collapse = pool below 5 at any month end (after regrowth); starvation = an agent with zero catch for 2 or more consecutive months while at least one other agent has a positive catch in those months; inequality = Gini of per-agent total catch above 0.4.
- Patch-check bound: k = 3 sanction months for the repair path; state ranges pool 0..100, month_total 0..100 with pool + month_total <= 100, catch 0..100; sanction duration at most 6 months and kind in {warn, cap_halve, suspend}.

## Predictions

1. **Gate correctness: PASS.** On an exhaustive grid of small states and catches (including negative and above-pool), the Z3 gate agrees with an independent plain-Python reference on every point: 0 mismatches, every disallowed action blocked, every allowed action allowed.
2. **Oracle flags the planted seam: PASS.** Four exploiter agents under the seamed spec: every executed action passed the gate, and the oracle fails the run for pool collapse, first at month 1 (pool is driven to 0). Starvation and inequality are not flagged (the take is spread near evenly; Gini well under 0.4). Four compliant agents (one catch of 5 per month) are not flagged under either spec.
3. **Patch closes the seam and the conflicting patch is rejected: PASS.** P1 passes all four patch checks at the stated bounds (conflict, deadlock, bounded sanctions, repair path all "pass", none "open"). Re-running the exploiters under seamed spec plus P1, the oracle passes (no collapse, no starvation, Gini under 0.4). C1 is rejected: check (a) no-conflict fails naming C1 and F1 (and F2, for states with pool below 20), and check (b) no-deadlock fails too.
4. **Mined de facto rules equal the written rules: PASS.** From gated explorer traces over seeds 0..49: seamed spec gives per-action max 10, min 0, per-month cap none; patched spec gives per-action max 10, min 0, per-month cap 40. The mined state machine's permitted edges are a subset of the de jure machine's (the de jure machine may have edges the explorer never took; those are reported, not counted as failures).

Overall wall time under 60 seconds for the whole V2 script plus tests. If any prediction fails, it stays failed here; the result is reported in docs/results/v2.md, not edited into this file.
