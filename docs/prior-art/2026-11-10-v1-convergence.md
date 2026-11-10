# V1: adversarial novelty search on the convergence loop, 2026-11-10

Slice V1 (docs/plan.md). Tries to find prior work that already measures how a rule-refinement loop for LLM agents converges.

**Limits.** This was a search-snippet and abstract-level review. Only Rehm (2609.22600) was read in part (about 60% of the text). RvB was read via an AI overview only. Everything else was judged from abstracts or snippets. Absences are search results, not proofs.

## Verdict

- **PASS with a narrower claim.** No paper found pre-empts the full design.
- Every threat below is PARTIAL. Each covers the loop, or a per-round curve, or a solver check, but never the combination.
- Reviewer confidence that the full combination is unpublished: about 70%.

## Narrowest surviving claim

We measure the per-round rate of new gate-passing intent violations ("seams") in a solver-checked, LLM-patched rule loop for a multi-agent LLM commons, with the patcher blinded to an independent environment-plus-frozen-judge oracle, and diff the written rules against rules mined from traces.

| Part of the claim | Unpublished, by reviewer confidence |
|---|---|
| Full combination | about 70% |
| De jure vs de facto diff with norm adoption | about 85% |
| Per-round seam curve | about 80% |
| "LLM patches rules, solver rejects conflicts" alone | about 35% (VEPA and AutoCedar do it) |

## Threats

| Work | What it does | What it lacks | Overlap |
|---|---|---|---|
| Nguyen et al. (incl. Dvijotham, Bansal, Pfister, Le), *VEPA*, arXiv 2610.12813, Oct 2026 | LLM patches symbolic guardrail rules; a deterministic verifier accepts only well-formed, conflict-free patches; evidence gate on activation | No solver named, no deadlock or repair-path check, no independent intent oracle, single agent, no de jure/de facto diff, no bloat guard, no per-round new-failure curve in the abstract | PARTIAL. Closest on mechanism. Its "longer horizons" experiment may hold a failure-over-time curve: full text needed |
| Huang et al., *RvB: Automating AI System Hardening via Iterative Red-Blue Games*, arXiv 2601.19726, 2026 | Red finds exploits, blue patches rules; defense success rate per iteration (about 90% by iteration 5); convergence bounds listed as future work | Curve is of defense rate, not new seams. No solver, no independent oracle, no mining | PARTIAL. Read via an AI overview only |
| Kumar et al., arXiv 2602.00755 (ICML 2026) | Evolves natural-language constitutions in a 6-agent grid world; fitness from an environment stability score; up to 30 iterations | No solver; an optimizer, not a seam finder; no new-violations-per-round; no de facto diff; bloat not measured | PARTIAL. Closest on multi-agent, environment oracle, iterated rules |
| Rehm, arXiv 2609.22600 | 5 GovSim agents propose and vote on Python laws; sandbox dry run with up to 2 repairs; survival, Gini, overshoot | No convergence analysis, no external patcher, no oracle separation, no solver | PARTIAL. About 60% of text read |
| Cho et al., *Automata from Agent Traces*, arXiv 2608.23670 | Merges agent traces into one FSM for next-step and failure prediction, vs process-mining baselines | No comparison to written rules | PARTIAL. Mining half only. Also ATLAS 2608.14352 (snippet) |
| *IterAlign*, NAACL 2024, arXiv 2403.18341 | Red-team, then an LLM proposes constitution principles; iterated; harmlessness gains over cycles | No seam curve, solver, multi-agent setting or independent oracle | PARTIAL. Loop only |
| Counterexample-guided LLM repair: AutoCedar 2607.03656 (nearest), Neurosymbolic Auditing 2605.13817, AutoSafeLTL 2503.15840, 2607.15854, REx 2405.17503, LTLGuard 2603.05728 | SMT or model-checker counterexamples drive LLM policy or spec repair | Not agent norms, no oracle, no per-round discovery | PARTIAL. Solver-in-loop patching only. Snippet level |
| Normative MAS: IRON, online IRON, DDNR (Morales et al., JAIR 2022), AAMAS 2023 agent-directed norm synthesis | Non-LLM online norm revision in traffic simulations; online IRON reports stability and compactness (bloat-like) | Not LLM agents, no solver gate, no intent oracle separation | PARTIAL. Check primary sources before claiming convergence or compactness measurement is new |
| DARWIN 2607.19829, AGrail, LiSA, EvoDefense, 2606.24496 | Co-evolving jailbreak and guardrail loops | DARWIN shows no convergence | PARTIAL. Loop only |
| Reward-hacking whack-a-mole | No measured new-exploits-per-patch study found | n/a | none found |

## Not found

- ADICO or IG with LLM agents and a solver.
- A de jure vs de facto diff on LLM-agent traces.
- A per-round seam metric (gate passes but intent is violated).
- A bloat guard in any LLM rule loop.

## Still to read before any write-up

1. VEPA full text, especially the longer-horizon figure.
2. RvB full paper.
3. Online IRON and DDNR primary sources.
4. arXiv listings for Oct to Nov 2026.

## Search queries

- VEPA guardrail evolution
- Automata from Agent Traces
- GovSim agents write and revise laws Rehm
- iterative red-team patch loop constitution refinement convergence
- counterexample-guided refinement LLM agent policy CEGAR spec repair Z3
- reward hacking whack-a-mole new exploits per iteration
- de facto vs de jure rules LLM traces process mining ADICO
- norm synthesis IRON SENSE LION online revision convergence
- LLM norm synthesis loophole verified SMT commons emergent norms
- seams guardrail passes but violates intent independent oracle plateau
- LLM-generated formal spec iterative refinement from violation traces multi-agent mined rules
