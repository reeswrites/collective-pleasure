# Contributing

- **Preregister.** Commit predictions to `docs/claims.md` before runs.
- **Bounded verdicts state k.** A check to depth k says so. "Open" never means "safe".
- **Every rule has a plain-English gloss and a source.**
- **ADRs for design choices** in `docs/decisions/`. Record surprises in `docs/surprises.md` and negative results in `docs/negative-results.md`.
- **Reviews** follow `docs/reviews/README.md` before anything is called a result.
- **Dual-use.** Adversarial search (finding rule sets or agent strategies that break invariants) is in scope for robustness testing only; report findings as defenses. No simulated populations stand in for real marginalized groups. Collusion and steganography stress tests stay within published benchmark settings.
