# Liberty (equal liberty plus non-domination): results (2026-11-10)

Prereg: `docs/results/liberty-prereg.md` (committed before any number). Module `src/mar/liberty.py`, run `uv run python scripts/liberty_run.py` (deterministic, no seeds, no model calls, 96 s; output `runs/liberty/summary.json`, not committed). All numbers exact (no cap hit). Scripted worlds, k = 2 (toy, fishery) and 3 (VPGG), w = 1 assumed. Nothing here is about LLM agents, the household, or relational autonomy.

## Prereg vs actual

| # | Prediction | Result |
|---|---|---|
| T1 | Unexercised veto: A plain bits unchanged; A liberty falls by 1.9 to 2.1 | **PASS.** A plain 2.585 both; liberty 0.585 (veto) vs 2.585 (wall); D = 3. |
| T2 | Wall: B liberty unchanged, B plain bits fall | **PASS.** B liberty 1.585 both (veto path is incompatible, |C| = 3); B plain 2.322 to 1.585. |
| T2' | Exercised veto: A plain bits fall to log2 3 | **PASS** (1.585). |
| V1 | VPGG liberty voluntary > compulsory strict in >= 13/15, none reversed | **FAIL, badly.** Strict 4/15, reversed 10/15, tie LLLL. |
| V2 | Sum (vol - comp) liberty > 0, agreeing with hand-made +1.0 | **FAIL.** Sum -19.6 bits (w = 0.5: -6.4; w = 2: -46.1; negative at every weight). |
| F1 | Fishery seamed months 1 to 4: liberty and plain exactly 0 | **PASS.** |
| F2 | Patched liberty > 0 and > seamed in all 16 agent-months | **PASS** (16/16). |
| F3 | Liberty spread across the four agents smaller than plain spread in >= 3/4 months | **FAIL.** Liberty spread 1.126 vs plain 0.341, 0/4 months. |
| S | No open, invariants hold | **PASS.** |

V1 was flagged as 50 percent in the prereg; it failed the stated way (the lone-abstainer mechanism reappears as domination).

## Where liberty, plain empowerment and the hand-made score agree or disagree

- **Toy kind master (the point of the measure).** Granting the veto leaves A's empowerment untouched and cuts A's liberty by 2 bits; the wall restores it. B's plain empowerment falls under the wall (2.322 to 1.585, the household v3a pattern, a wall reads as lost freedom) but B's liberty does not, because B's veto futures were never compatible. Liberty separates "a loss of a power over someone" from "a loss of freedom".
- **VPGG: the hand-made score, liberty and plain empowerment do not agree.** Hand-made says voluntary 1.0, compulsory 0.0. Plain empowerment says voluntary higher in 11 of 15 (earlier result). Liberty says compulsory higher in 10 of 15. Cause: under voluntary, any member can abstain at will, which can shrink the focal's count of futures (D = 12 or 13 of 16 in CCCD, CCDD, CDDD), while under compulsory D = 0 everywhere (everyone is forced to join; a forced action changes payoffs but not how many distinct futures the focal has). The count-based test cannot tell a member leaving from a member blocking, so exit-at-will is scored as domination. That is a limit of the construction (prereg limit: count-based), not evidence that compulsion is freer; the author's intuition (an exit right is freedom) and Pettit's (a power that others hold over you is domination) pull apart here, and the measure follows Pettit literally.
- **Fishery.** Seamed collapses to 0 from month 1 on every measure (agree). Patched: liberty, plain bits and option fraction all above seamed (agree, 16/16). Seat order: the hand-made option fraction is flat (0.833); plain bits give exploiter 0 an edge (4.248 vs 3.907 at k = 2); liberty amplifies it (E0 2.585, E1 1.459, compliant 1.585 each) because E1 is dominated by E0, who acts first and can take what E1's futures depend on (D = 3), and E0's own greed is incompatible less than its position helps. Prediction F3 (equal liberty flattens the order) failed: non-domination, not equal liberty, drives the spread. At month 0 seamed, exploiters score LOWER liberty (1.322) than compliant agents (2.585) because their overfishing is incompatible and they are dominated by each other, the one place liberty ranks as a norm-minded reader would.

## What the household adapter must expose

Beyond empowerment's four methods and a scripted policy defined for EVERY member index (the script is each member's default): `noop(state, agent)` (the restraint action, e.g. rest), and `force_policy(policy, j, action)` (the script with j playing one given action this pass). Also: the gate must be what decides whether a forced action (a veto, a request) takes effect, so a wall removes the power (HouseholdWorld already routes through `decide`); keys must be partner-relative as in v3a. Open design points the household will raise: blocking is first-pass only (a veto that appears later is invisible), the test is count-based, and `noop` for the household is a choice ("rest"). Consent-dependent requests are deterministic by persona, so the blocker's available actions are the same menu for every state. Cost: compatible-path search multiplies calls (fishery at k = 3 was not attempted; k = 2 took about 95 s for all runs), so expect the household to need a lower cap or k = 2.
