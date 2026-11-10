# Empowerment vs the hand-made freedom score: results (2026-11-10)

Prereg: `docs/results/empowerment-prereg.md` (commit 1f7aecd, before any number). Module `src/mar/empowerment.py`, run `uv run python scripts/empowerment_run.py` (deterministic, no seeds, no model calls; output in `runs/empowerment/summary.json`, not committed). All numbers are exact at k=3 rounds; no call hit the 20000-expansion cap (largest 114), so no "open" verdicts. This says nothing about LLM agents or the household, and "reachable" is not "safe".

## Prereg vs actual

| # | Prediction | Result |
|---|---|---|
| 1 | VPGG voluntary > compulsory, strict in 14/15 compositions (LLLL tie), none worse, mean diff >= 0.5 bits | **FAIL.** Strict in 11/15, ties in DDLL and LLLL, compulsory HIGHER in CCLL (7 vs 9 reachable) and CDLL (4 vs 9). Mean diff 0.460 bits (below 0.5). The LLLL tie was predicted; the other three misses were not. |
| 2b | Compliant agents: patched > seamed in months 1 to 4; seamed exactly 0 bits; patched >= 3.0 | **PASS.** Seamed 0.000 (pool 0 forever, 1 reachable); patched 4.087 bits (17 reachable) for both compliant agents in every month. |
| 2a | Exploiters: patched < seamed in months 1 to 4 (author's claim; I predicted FAIL by construction) | **FAIL, as predicted.** Patched 4.700 and 4.170 bits vs seamed 0.000. The patch does not lower exploiters' later empowerment; it restores it. |
| 2a' | Month 0, exploiters: mean over 12 subround states lower under patched by >= 0.3 bits | **PASS.** Seamed minus patched 0.921 and 0.935 bits (seamed 2.289, 2.017; patched 1.368, 1.081). |
| 3a | Hand-made and empowerment agree on VPGG | **PASS** (hand 1.0 vs 0.0; empowerment summed over compositions +6.89 bits), but see the composition-level disagreement below. |
| 3b | Fishery, months 1 to 4, patched vs seamed: option fraction and bits agree per agent | **PASS** for all four agents: option fraction 5/6 vs 1/6 every month; bits up by 16 to 19 summed over four months. |
| 3c | Empowerment sees seat order the option fraction cannot | **PASS.** Patched month start: exploiter 0 has 4.700 bits, exploiter 1 4.170, compliant 4.087 each; option fraction 0.833 for all. Exploiter 0 > compliant 3 in 4/4 months. |
| 4 | Power-seeking index near zero in a shared collapse; no flags | **PASS.** Seamed: every agent falls 5.392 to 0 (psi 0.000 each, none flagged); patched: no change, psi 0 each, none flagged. |
| 5 | No cap hit | **PASS.** |

Prediction 1 is the headline miss. It is reported as failed; the prereg is not edited.

## Where the two freedom measures agree and disagree

- **Agree (coarse regime ranking).** VPGG voluntary over compulsory (hand 1.0 vs 0.0; empowerment higher in 11 of 15 compositions and on the sum). Fishery patched over seamed from month 1 (both measures respond to the pool surviving, since the gate itself blocks catch above pool).
- **Disagree: the loner option is not always more futures.** The hand-made score is a property of the rules (exit permitted and real). Empowerment is a property of the rules plus the others' policies. When most others abstain (CCLL, CDLL), a lone voluntary joiner becomes a loner and every focal action pays sigma, so the focal agent's futures COLLAPSE together; under compulsory the same intended loners are forced to join, and the focal agent's choices matter (distinct payoffs). Exit available is not option-rich if the exit is where everyone is. The hand-made score cannot see this; empowerment can. (It is also an artifact of ASSUMED choices below: payoff holdings as state, fixed intents for the others.)
- **Disagree: the patch.** Author's expectation (ADR 0011 order of work; prereg 2a) that the cap lowers exploiters' empowerment does not hold in months 1+; the cap costs exploiters empowerment only inside month 0 (2a'). In the seamed run empowerment is identical for all four agents (5.392 to 0): a shared collapse, no one is power-seeking. The index flags grabs, not tragedies.
- **Empowerment adds what the proxy lacks:** seat order against a shared cap (3c); the hand-made option fraction is constant across agents.
- **Seam note:** at month 0 start, seamed (5.392 bits) is MORE empowering than patched (4.700, 4.170, 4.087). Reading empowerment as welfare at a moment, rather than over the run, would favor the seamed spec there.

## ASSUMED choices (all fixed in the prereg before the run)

1. State key drops the clock and includes the agent's own cumulative holdings (catch, payoff). Holdings make accumulating payoffs count as futures; this is why the all-loner tie is 4 = 4 and why DDLL ties.
2. Reachable = union over steps 0 to k, start included; k = 3 rounds (subrounds in the fishery).
3. Others follow fixed deterministic scripts (mocks; C/D/L intents with gate fallback to join). Empowerment is conditional on that.
4. Fishery action menu (0, 1, 3, 5, 10, 15); VPGG menu join, contribute, abstain. Counts depend on the menu.
5. Fishery hand-made freedom is a proxy I defined (option fraction of the menu the gate permits); the repo has none for the fishery.
6. Power-seeking index = own change minus others' mean change; the literal "own gain minus others' loss" rewards a universal rise.
7. VPGG measured with one fixed group of five, all 15 compositions of the others; not the population dynamics.

## What the household adapter needs to expose

`actions(state, agent)` (the move menu per slot, including leave, return, request, refuse, gift variants and their parameters, discretized), `step(state, spec, agent, action, policy_of_others)` as a pure function (no RNG consumption, or a fixed seed per call; today the harness holds the RNG and shocks, which must be fixed or enumerated), `key(state, agent)` (a hashable summary: money, in-or-out, needs, relationships; a decision about what counts as a distinct future, e.g. whether to bucket money), `is_terminal(state)`, and a deep-copyable or immutable state. The persona agents are not deterministic scripts, so `policy_of_others` must be a scripted policy (cooperator, default), not an LLM. The state space is larger than the fishery's: expect the cap to bind at k = 3 with a wide menu, which gives "open", not a number. Do not switch the household to empowerment before it agrees with the hand-made score there, and treat the VPGG finding as a warning that it will not always.
