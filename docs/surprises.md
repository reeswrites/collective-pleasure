# Surprises

Unexpected observations, each dated and with its evidence. Purpose: keep results that contradict expectations visible.

## 2026-11-10 (V2)

- **A natural cap card deadlocks itself.** The patch "combined catch above 40 in a month is forbidden", written as the single condition `month_total + catch > 40`, also forbids catch 0 once the month total is over 40, so the no-deadlock check (b) failed it. The solver caught a bug I had written into the "obvious" patch. Evidence: first V2 run; test_naive_cap_without_catch_gt_zero_is_a_deadlock. Implication for V3/V4: LLM patchers will likely make this mistake; check (b) earns its place.
- **Exploiters stop at the pool, not only at the rules.** Under the seamed spec, once the pool is below 10 the exploiter's 10-fish proposals are rejected by F2 (catch above pool), so not every exploiter proposal passes the gate; the seam is still every *executed* action passing. Evidence: tests/test_oracle.py.
- **Explorer coverage of the state machine is thin under the patched spec.** The patch keeps the pool high, so the explorer rarely reaches low-pool cells: 7 of 21 de jure edges seen. Bounds were still mined exactly. Coverage of rare cells will need targeted probes in V4.
