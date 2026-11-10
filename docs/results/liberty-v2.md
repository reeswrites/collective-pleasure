# Liberty v2 (interference vs withdrawal): results (2026-11-10)

Prereg: `docs/results/liberty-v2-prereg.md` (committed before any v2 number, commit "Preregister liberty v2"). Code `src/mar/liberty.py` (`version=2` default, `version=1` the old path), run `uv run python scripts/liberty_run.py` (runs both versions, deterministic, no seeds, no model calls, about 3.5 min; output `runs/liberty/summary_v2.json`, not committed). Exact numbers, no cap hit. Scripted worlds, k = 2 (toy, fishery), 3 (VPGG), w = 1 assumed. Nothing here is about LLM agents or the household.

Author decision driving v2 (verbatim, 2026-11-10): "there is something being lost there literally in the world and also affects two people but idk if we can count of it as loss of freedom when technically it was only possible thru agreement in the first place". Freedom counts what is yours by right: your own actions and protection from veto, block or force. Another member's exit, abstention or refusal is not domination; the loss is real but booked to cooperation and the hedonic model.

## Prereg vs actual

| # | Prediction | Result |
|---|---|---|
| 1 | Toy: v2 = v1 exactly, ADO = 0 | **PASS.** All six cells equal; A liberty 0.585 (veto) vs 2.585 (wall), B 1.585 both; ADO 0. |
| 2.V1 | VPGG vol >= comp in all 15, strict in >= 8 | **FAIL.** Strict 11/15, ties DDLL, LLLL, REVERSED in 2: CCLL (2.585 vs 3.170) and CDLL (2.000 vs 3.000). |
| 2.V2 | D = 0 in all 30 cells | **PASS** (structural). |
| 2.V3 | Sum (vol - comp) liberty2 > 0, hand-made +1.0 | **PASS.** +5.263 bits (v1: -19.6). |
| 3.F1 | Fishery seamed months 1 to 4 all 0 | **PASS.** |
| 3.F2 | Patched > seamed in 16/16 | **FAIL.** 12/16: in patched, exploiter 1 has liberty2 0.000 (ado 8, D 2) so it is not above seamed 0.000 in months 1 to 4. |
| 3.F3 | v2 = v1 on the fishery, fishery ADO = 0 (F3 itself expected to fail again) | **FAIL (my claim of equality was wrong).** v2 differs from v1 in 12 of 40 agent-months (ADO nonzero in 12/40). F3 itself still fails: liberty spread 1.585 vs plain 0.341, 0/4 months. |
| 4 | Voluntary ADO > 0 in >= 8/15 compositions | **FAIL (narrowly).** 7/15 (CCCL, CCDL, CCLL, CDDL, CLLL, DDDL, DLLL) ; compulsory 4/15 (CDDD, CDDL, CDLL, CLLL, all via `join` = stop contributing). |
| 5 | Hand cases | **PASS** (unit tests: a veto counts, leaving does not, abstaining does not, an agreement-dependent option is excluded and reported). |
| 6 | No open, invariants hold | **PASS.** |

## v1 vs v2 side by side

VPGG, focal 0, k = 3. Liberty in bits (plain reach, c_all = compatible reach, ado = agreement-dependent options lost, c_own, D).

| others | vol v1 | vol v2 (plain c_all ado c_own D) | comp v1 | comp v2 (plain c_all ado c_own D) |
|---|---|---|---|---|
| CCCC | 1.193 | 4.000 (16 16 0 16 0) | 3.322 | 3.322 (10 10 0 10 0) |
| CCCD | 0.300 | 4.000 (16 16 0 16 0) | 3.322 | 3.322 (10 10 0 10 0) |
| CCCL | 4.000 | 3.700 (16 16 3 13 0) | 3.322 | 3.322 (10 10 0 10 0) |
| CCDD | 0.100 | 3.907 (15 15 0 15 0) | 3.170 | 3.170 (9 9 0 9 0) |
| CCDL | 3.907 | 3.322 (15 15 5 10 0) | 3.170 | 3.170 (9 9 0 9 0) |
| CCLL | 0.000 | 2.585 (7 7 1 6 0) | 3.170 | 3.170 (9 9 0 9 0) |
| CDDD | 0.000 | 3.807 (14 14 0 14 0) | 3.170 | 3.000 (9 9 1 8 0) |
| CDDL | 3.585 | 3.170 (12 12 3 9 0) | 3.170 | 3.000 (9 9 1 8 0) |
| CDLL | 0.000 | 2.000 (4 4 0 4 0) | 3.170 | 3.000 (9 9 1 8 0) |
| CLLL | 1.585 | 3.170 (12 12 3 9 0) | 3.170 | 3.000 (9 9 1 8 0) |
| DDDD | 0.737 | 3.322 (10 10 0 10 0) | 2.000 | 2.000 (4 4 0 4 0) |
| DDDL | 3.322 | 3.170 (10 10 1 9 0) | 2.000 | 2.000 (4 4 0 4 0) |
| DDLL | 0.000 | 2.000 (4 4 0 4 0) | 2.000 | 2.000 (4 4 0 4 0) |
| DLLL | 1.807 | 2.585 (7 7 1 6 0) | 2.000 | 2.000 (4 4 0 4 0) |
| LLLL | 2.000 | 2.000 (4 4 0 4 0) | 2.000 | 2.000 (4 4 0 4 0) |

Sum of (voluntary minus compulsory): v1 -19.6, v2 +5.263. Hand-made +1.0. The domination term that sank v1 (D = 12 or 13 in CCCD, CCDD, CDDD) is gone. The two reversals CCLL and CDLL are NOT caused by domination or ADO: in both, plain reach (and c_all) under voluntary is already lower than under compulsory (7 vs 9, 4 vs 9), so the cause is plain count-based empowerment (earlier result: voluntary higher in only 11 of 15). When several others abstain, the focal's holdings reach few distinct values because the pool pays little; compulsory forces them in, enlarging that count. That is the count metric registering a shared good that is smaller, i.e. the cooperation loss again, entering via the option count rather than via D or ADO.

Toy (A, B; plain, c_all, ado, c_own, D, liberty): veto-right A 2.585, 6, 0, 6, 3, 0.585; B 2.322, 3, 0, 3, 0, 1.585. Wall: A 2.585, 6, 0, 6, 0, 2.585; B 1.585, 3, 0, 3, 0, 1.585. Exercised: A 1.585, 3, 0, 3, 2, 0.000. Same as v1.

Hand world (`PartnerWorld`, k = 2, partner B may veto, leave or abstain; A's `joint` option needs B). v1 wall: D = 3, blocker (B, leave): the exit scored as domination, liberty 0.585. v2 wall: D = 0, ADO = 3 (the joint keys, reported), liberty log2 3 = 1.585. v2 with the veto: D = 2, liberty 0.000.

Fishery (k = 2). v1 and v2 agree in seamed months 1 to 4 (all 0) and in patched compliant agents (1.585 both). They differ for the exploiters: patched E0 v1 2.585, v2 1.585 (ADO 3, from compliant agent 1 catching 0); E1 v1 1.459, v2 0.000 (ADO 8, from agent 2 catching 0, plus D 2 from E0). Seamed month 0: compliant agents 2.585 (v1) vs 2.115 (v2; ADO 5). So catch 0 as a WITHDRAWAL does reduce counts of others' reach, because forcing a member to catch 0 changes pool and month-total keys and the count can drop. I have not diagnosed whether this is a genuine dependence (a member's catching is what the others' feasible catches track under the patched gate) or a count artifact; the fishery ADO should be read as unreliable until that is checked. The prereg claim "a member fishing less only enlarges the pool" ignored that keys include the month total, which also changes.

## Classification tables (ASSUMED; one-line rationale each; in code: `TOY_CLASS`, `VPGG_CLASS`, `PARTNER_CLASS`, `classify`)

| World | Action | Class | Rationale |
|---|---|---|---|
| Toy | A x | OWN | A's own contested option |
| Toy | A work | OWN | A's own work |
| Toy | A rest | WITHDRAWAL | restraint |
| Toy | B pass | WITHDRAWAL | restraint, B declines to act |
| Toy | B work | OWN | B's own work |
| Toy | B veto | INTERFERENCE | blocks A's option |
| VPGG | contribute | OWN | puts in own resources |
| VPGG | join | WITHDRAWAL | joins but declines to supply own resources |
| VPGG | abstain | WITHDRAWAL | leaves the pool |
| Fishery | catch 0 | WITHDRAWAL | restraint |
| Fishery | catch > 0 | INTERFERENCE | draws on a shared stock others' futures depend on (the v1 harm test then decides compatibility) |

## What the household adapter must expose

Besides v1's (`noop`, `force_policy`, a policy for every member index): a `classify(state, agent, action) -> INTERFERENCE | WITHDRAWAL | OWN` method, with a one-line rationale per action in a table. Proposed for the `HH_MENU` (read only here, to be confirmed by the household owner; judgment, ASSUMED): `veto` (no_contact, spend) INTERFERENCE (acts on the partner's own options); `take_shared` INTERFERENCE (takes from the joint pot); `request` INTERFERENCE only if a sanction or deadline attaches outside agreed terms, otherwise OWN (asking is not blocking; the partner can refuse); sanctions outside the contract INTERFERENCE; `refuse_request` WITHDRAWAL (declines to supply what was asked); `leave` (0, 50, 100) WITHDRAWAL (own exit, whatever the exit-cost split) but the settlement terms are a separate question: a leave that takes more than the agreed share is INTERFERENCE; `return` OWN; `work`, `spend_self`, `see_friend` OWN; `rest` WITHDRAWAL; `together` OWN; `spend_shared` OWN if within the agreed budget, INTERFERENCE if it exceeds it. Agreement-dependent options (joint trips, a shared budget, being asked at all) are those whose keys vanish when the partner refuses, leaves or rests. Keys must stay partner-relative. Contract-owed cooperation (a promise, a trap) is not modelled in v2 and must be judged by the hedonic layer.

## Lines for the ledgers (to be added by the owner; I did not edit those files)

docs/negative-results.md:
- `liberty v2 VPGG V1 (2026-11-10): FAIL. Interference/withdrawal removed the domination term (v1 sum -19.6 bits to v2 +5.263), strict 11/15, but vol < comp reversed in CCLL (2.585 vs 3.170) and CDLL (2.000 vs 3.000). Cause: plain count-based reach is already lower under voluntary in both (7 vs 9, 4 vs 9), not domination or ADO. Prereg docs/results/liberty-v2-prereg.md; results docs/results/liberty-v2.md.`
- `liberty v2 fishery F2/F3 and prediction 4 (2026-11-10): F2 FAIL 12/16 (patched exploiter 1 is 0.000, not above seamed 0.000); F3 equality-with-v1 claim FAIL (12/40 agent-months differ, ADO from catch 0); prediction 4 FAIL 7/15 vs threshold 8 (compulsory 4/15).`

docs/surprises.md:
- `2026-11-10 liberty v2: "a member fishing less only enlarges the pool" was wrong as a count claim: forcing a member to catch 0 lowers others' reach counts by 3 to 8 keys in the patched fishery (keys include the month total). A WITHDRAWAL can shrink another's count even where no cooperation is owed. Undiagnosed: genuine dependence vs count artifact.`
- `2026-11-10 liberty v2: the remaining VPGG voluntary-below-compulsory cases come from plain empowerment (shared good smaller when others abstain), the cooperation loss entering through the option count, not through domination. The exclusion step (ADO) is first-step and count-based, so it can miss or mis-book that loss.`

## Reading

v2 does what the author asked in the cases it was built for: a veto counts, an exit or abstention does not, the agreement-dependent loss stays visible in its own column, and the toy kind-master result is untouched. In VPGG it flips the sign of the aggregate, but not cleanly (two reversals, both from the underlying count). It also exposes a new hole in the fishery: treating catch 0 as a withdrawal books count changes there as agreement-dependent loss, and I have not shown they are. Limits as in the prereg: scripted worlds, count-based, first-step, classification assumed.

## Correction 2026-11-10 (what the VPGG pass and the fishery counts do and do not show)

- **The VPGG domination term is zero by construction.** In VPGG every action is `OWN` or `WITHDRAWAL` under the classification table (src/mar/liberty.py, `classify`); there is no `INTERFERENCE` action in that world, so the harm test cannot fire. `c_all` equals plain reach in all 30 cells and D = 0 everywhere (the document's "PASS (structural)" on 2.V2 is correct). It follows that VPGG liberty2 is log2(plain reach minus ADO), and the V3 pass (sum -19.6 to +5.263, recomputed 46.738 minus 41.476) is mostly the classification table removing the domination term, not the construct discovering the right sign. The informative VPGG result is the V1 failure (two reversals). The VPGG pass cannot be cited as "the measure is repaired"; a world with interference actions would be needed to exercise the non-domination component.
- **The fishery cells are four values repeated, not 16 or 40 measurements.** Every patched month 0 to 4 has the identical vector (v1 [2.585, 1.459, 1.585, 1.585]; v2 [1.585, 0.0, 1.585, 1.585]) and seamed months 1 to 4 are all 0. So "F2 12/16", "F3 0/4 months" and "12 of 40 agent-months differ" count 3 to 4 agent-values 4 or 5 times each; they are not sample sizes. The verdicts (F2 fail, F3 fail) are unaffected.
- **A mislabelled agent.** The fishery paragraph says exploiter E0's ADO of 3 comes "from compliant agent 1 catching 0". The saved `ado_by` is [1, 0], and agent 1 is the second exploiter E1 (the world is E, E, C, C), not a compliant agent. E1's ADO of 8 comes from agent 2, which is compliant. The fishery ADO is still flagged by this document as undiagnosed.
