# Surprises

Unexpected observations, each dated and with its evidence. Purpose: keep results that contradict expectations visible.

## 2026-11-10 (V2)

- **A natural cap card deadlocks itself.** The patch "combined catch above 40 in a month is forbidden", written as the single condition `month_total + catch > 40`, also forbids catch 0 once the month total is over 40, so the no-deadlock check (b) failed it. The solver caught a bug I had written into the "obvious" patch. Evidence: first V2 run; test_naive_cap_without_catch_gt_zero_is_a_deadlock. Implication for V3/V4: LLM patchers will likely make this mistake; check (b) earns its place.
- **Exploiters stop at the pool, not only at the rules.** Under the seamed spec, once the pool is below 10 the exploiter's 10-fish proposals are rejected by F2 (catch above pool), so not every exploiter proposal passes the gate; the seam is still every *executed* action passing. Evidence: tests/test_oracle.py.
- **Explorer coverage of the state machine is thin under the patched spec.** The patch keeps the pool high, so the explorer rarely reaches low-pool cells: 7 of 21 de jure edges seen. Bounds were still mined exactly. Coverage of rare cells will need targeted probes in V4.

## 2026-11-10 (V2b)

- **`must` reads backwards in the SLEEC trigger form.** Under the card semantics the conditions of a `must` are what compliance requires, not a trigger, so "when X, must" would misstate C1. The surface needed a separate template ("must ... only when"). Evidence: src/mar/english.py, tests/test_english.py.
- **The gloss already is the natural English.** The sentence, gloss and source together are long, and the gloss says the same thing more loosely. The F-EN reader-test advantage over ADICO YAML depends on whether the reader sees the gloss (ADR 0004 caveat).
- **The conflicting patch C1 also fails the repair-path check (d)** naming F1 (its sanction leaves no allowed action when C1 is present), in both YAML and English authoring. V2 only predicted (a) and (b).

## 2026-11-10: "seam" check is trivially true per action

Executed actions are by construction allowed, so "every executed action passed the gate" holds for any gated run. A seam is therefore any oracle failure of a gated run. In the V2 exploiter fixture, 278 of 288 proposals were blocked (all by F2, asking for more than the pool held), and the collapse came from the 10 allowed catches. The workbench verdict text now says this instead of implying no action was blocked. Evidence: workbench agent report, commit 6b362c2.
