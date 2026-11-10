# Contributing

- **Preregister.** Commit predictions to `docs/claims.md` before runs.
- **A prediction is a quantity, not a sentence** (ADR 0015). Each preregistered prediction names: the quantity, the unit of resampling (seed, run, or pairing with its seeds clustered), the test, alpha (0.05 unless stated), the correction family (Holm across the predictions of one experiment), and the threshold or margin. Use `docs/templates/prereg.md`.
- **Power check before choosing seeds.** Run a small pilot labeled EXPLORATORY (not a result, changes no threshold), take its effect and spread, and compute the seeds for 80% power with `mar.stats.seeds_for_power`. Record the pilot, the numbers and the chosen n in the prereg. LLM runs take their seeds from this check, never a default of 3. If the cap cannot pay for the n, say so and downgrade the claim to descriptive.
- **Report effect sizes with intervals.** Every comparison reports the difference (or risk difference and ratio for rates) with a 95% CI, plus Cliff's delta or Cohen's d, from `mar.stats`. A p-value alone is not a result. Rates are exact (Clopper-Pearson).
- **Verdicts carry a statistical label** beside held or missed: holds robustly, holds but CI crosses threshold, miss robust, miss but CI crosses threshold, not testable (deterministic, n too small, or outputs not saved). Save per-run outputs so this can be computed. Use `scripts/stats_retrofit.py` as the pattern.
- **Seeds, not reruns, are the sample.** Do not read a deterministic enumeration as a sample; say "not testable" for it. Do not add seeds after seeing a result to move a CI.
- **Bounded verdicts state k.** A check to depth k says so. "Open" never means "safe".
- **Every rule has a plain-English gloss and a source.**
- **ADRs for design choices** in `docs/decisions/`. Record surprises in `docs/surprises.md` and negative results in `docs/negative-results.md`.
- **Reviews** follow `docs/reviews/README.md` before anything is called a result.
- **Dual-use.** Adversarial search (finding rule sets or agent strategies that break invariants) is in scope for robustness testing only; report findings as defenses. No simulated populations stand in for real marginalized groups. Collusion and steganography stress tests stay within published benchmark settings.
