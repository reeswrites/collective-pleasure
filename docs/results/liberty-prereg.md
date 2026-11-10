# Liberty (equal liberty plus non-domination): preregistration (2026-11-10)

Status: written and committed BEFORE any liberty number is computed. Never edited after. Results go in `docs/results/liberty.md`. Nothing here is a result. Module `src/mar/liberty.py`, built on the adapter interface of `src/mar/empowerment.py`.

Author decision (2026-11-10): the main freedom score combines (1) EQUAL LIBERTY, an agent's options count only if compatible with every other member having equal options (the author: only options that do not shrink someone else's), cf. Kant's universal principle of right, Rawls's first principle, Mill's harm principle; and (2) a DOMINATION PENALTY, subtract every option an agent has that another member could block at will, whether or not they ever do (Pettit, freedom as non-domination; the "kind master"). Relational autonomy is a later check (needs household v3). It is reported ALONGSIDE the hand-made score and plain empowerment. Philosophical sources are recalled until verified in `docs/references.md`.

## Definitions (all choices ASSUMED, fixed now)

Setting: world adapter with `n_agents, actions, step, key, is_terminal` (as empowerment), a scripted `policy_of_others(obs_or_state, i)` defined for EVERY agent index (the script is each member's default behaviour), horizon k, a gate/spec. Extra adapter hooks (new): `noop(state, agent)` = the restraint action; `force_policy(policy, j, action)` = the same script except j plays `action` this step. Fishery noop = catch 0; VPGG noop = abstain (a request; the gate may turn it into join); toy noop = rest / pass.

- Plain reach F_i(s) = distinct keys i can reach within k steps (empowerment's set, i free, others scripted). |F_i| = `reachable`.
- Harm test. Let s_a = step(s, i plays a, others scripted) and s_0 = the same with i playing noop. Action a is COMPATIBLE for i at s iff for every other member j: |F_j(s_a)| >= |F_j(s_0)| (no member is left with fewer reachable futures than under i's restraint). The noop is compatible by construction.
- Compatible futures C_i(s) = keys reachable by i within k steps along paths in which EVERY move is compatible at the state where it is made (start key included, so |C_i| >= 1). C_i is a subset of F_i. bits_C = log2 |C_i|.
- Blockability. For another member j and an action b of j: C_i^(j,b) = the same compatible-paths reach with j forced to play b at the first step only (others scripted; the gate decides whether b takes effect, so a wall removes the power). Reduction R_ij = max over b of ( |C_i^(j, noop_j)| - |C_i^(j, b)| ), floored at 0.
- Domination exposure D_i = max over j != i of R_ij, capped at |C_i| - 1 (a lower bound on the union over blockers; counts of compatible futures i holds at the sufferance of someone). It counts capability, not exercise: j's script never needs to block. bits_D = log2(1 + D_i).
- LIBERTY_i = bits_C - w * bits_D, w = 1 ASSUMED (so w = 1 gives log2( |C_i| / (1 + D_i) ), 0 when everything is held at another's sufferance). Both parts are always reported. w in {0.5, 1, 2} sensitivity reported; headline w = 1.
- Invariants (tests, not predictions): 0 <= bits_C <= plain bits; D_i = 0 with one member; liberty <= plain bits when w >= 0.
- Exact bounded enumeration with the empowerment cap (20000 expansions per BFS call); a hit gives "open", never a number to compare.

Limits stated now: first-step blocking only (a veto available only later is invisible at s); the harm test is count-based (it cannot see shifts in which futures); compatibility is judged against i's own restraint, not against a baseline of equal shares; i's key holds i's own holdings (as in empowerment).

## Settings

- k: toy 2; VPGG 3 (as empowerment); fishery 2 (the compatible-path search multiplies calls; plain empowerment is re-reported at k = 2 for comparison, not copied from the k = 3 result).
- Toy veto world (in the module): partners A (0), B (1); each step B acts first, then A. A's menu x (the contested option), work, rest; B's menu pass, work, veto. A's `x` counts nx unless a veto is in force; `veto` (B) sets the veto only if spec.veto_right. Keys: A (nx, nw); B (nw_B, veto placed). Scripts: A rests, B passes (a kind master). Specs: veto_right True (the veto granted, never used) or False (the wall).
- VPGG: N = 5, r = 3, c = 1, sigma = 1, regimes voluntary and compulsory, the 15 compositions of the others, focal agent 0, as empowerment.
- Fishery: as empowerment (4 agents E, E, C, C; seamed rules/fishery; patched = + scripted P1); measured at month starts 0 to 4 on the actual trajectory, all four agents.

## Predictions (numeric, committed before any run)

T. Toy veto world (hand-computed, k = 2). A: |F| = 6, so plain 2.585 bits both specs. B: |F| = 5 with the right (keys (bw 0..2, veto) minus unreachable), 3 under the wall.
 - T1. Granting an unexercised veto: A's plain bits unchanged (2.585 vs 2.585, exact); A's liberty lowers: bits_C = 2.585, D_A = 3 (the three keys with x done), liberty = 2.585 - 2 = 0.585 with the veto vs 2.585 without. PASS = A liberty(veto) < liberty(wall) by 1.9 to 2.1 bits and plain bits equal to 1e-9.
 - T2. The wall: A liberty rises (0.585 to 2.585, as T1); B's liberty does not fall (veto futures are incompatible, so |C_B| = 3 in both specs: liberty 1.585 both, D_B = 0), while B's plain bits DO fall (2.322 to 1.585). PASS = B liberty equal across specs to 1e-9 and B plain bits lower under the wall.
 - T2'. For contrast: when B's script exercises the veto at step 1 under the veto-granted spec, A's plain bits fall below the unexercised value (prediction: to 1.585 = log2 3).
V. VPGG, 15 compositions, k = 3 (my confidence about 50 percent; the empowerment result failed here, and the same mechanism, a lone abstainer collapsing the focal's futures, can reappear as domination under voluntary, since any member can abstain at will).
 - V1. Liberty of voluntary > compulsory, strict, for at least 13 of 15 compositions, none reversed (liberty_vol < liberty_comp - 1e-9). PASS needs both. A reversal in even one composition is a FAIL of V1.
 - V2. The sum over compositions of (voluntary minus compulsory) liberty is positive, agreeing in sign with the hand-made score (1.0 vs 0.0). PASS = positive sum.
F. Fishery, k = 2, months 1 to 4 (month-start states).
 - F1. Seamed: all four agents have exactly liberty 0 and plain bits 0 (one reachable key, pool stays 0).
 - F2. Patched: every agent's liberty > 0 in months 1 to 4, so patched > seamed in all 16 agent-months, agreeing in sign with plain bits and the option fraction (5/6 vs 1/6) in all 16.
 - F3. Equal liberty flattens seat order: spread (max minus min over the four agents) of liberty at patched month starts is smaller than the spread of plain bits (at the same k) in at least 3 of the 4 months.
S. Sanity. No open verdicts; invariants hold in every run (liberty <= plain bits, bits_C <= plain bits).

## What counts as the result

Each prediction pass or fail with numbers; the prereg is not edited. These are statements about deterministic scripted worlds, one menu and one parameter point; w = 1 is an assumption and compatibility/blockability are count-based. They say nothing about LLM agents or the household, and say nothing about relational autonomy.
