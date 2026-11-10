# Plan

Status: pre-results. Milestones are from RATIONALE.md section 11.

## Milestones

- [ ] 1. Repeat the prior-art check: classic norm synthesis, SLEEC, and the last month of arXiv.
- [ ] 2. Minimal ADICO -> transition-system export for one tiny rule system (the GovSim fishery quota), cross-checked against philosophy-engine's reference engine (https://github.com/reeswrites/philosophy-engine).
- [ ] 3. Load it in mCRL2. Prove one invariant and find one counterexample.
- [ ] 4. A runtime `check_action` gate wired into a forked GovSim with a small open model.
- [ ] 5. Preregister S1, then run S1 (first experiment): one agent under the fishery-quota rules, free-text vs solver-gated.
- [ ] 6. Preregister E0 and E2, then run E2 (regimented vs regulated vs free text, multi-agent).

Single-agent is the base case of the same pipeline (n = 1); multi-agent adds peer sanctions, collusion, emergent norms and coordinated attacks (RATIONALE.md section 1a).

## Next task

1. **Milestone 1:** repeat the prior-art check before any write-up. Record dated findings and search terms.
2. **Milestone 2:** minimal ADICO -> LTS export for a GovSim-fishery-quota rule system, cross-checked against philosophy-engine's reference engine. Every rule gets a plain-English gloss and a source. Bounded verdicts state k.
