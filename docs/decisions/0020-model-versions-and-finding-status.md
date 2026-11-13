# 0020. Model versions and the status of findings

Status: accepted (2026-11-13). The author asked "when we update the model what happens to old findings?" and answered "1" to writing this policy down (experiments/questions.jsonl).

## Context

The household model keeps changing, for good reasons: the value check, the agent recalibration, the bill horizon, the saturating scale (ADR 0019), the hybrid agent, the satiety fix. Each change has moved some findings. H38's headline went +0.021, −0.046, −0.003 across three agent sets before the third formation check settled what holds.

Three habits already protect old results:

- Every model change goes behind a flag that is off by default. Pinned fingerprints (tests/data/*fingerprints*.json) prove old runs reproduce byte for byte with the flags off.
- When a later change undercuts a result, the original doc gets a dated note at the top and the hypothesis status changes. The original text stays.
- Central claims are rerun across model versions side by side, under a stop rule: a sign that differs across versions is reported as version-dependent and not patched (docs/results/formation-check-3-prereg.md).

What is missing: no single place records which model version produced a result, there is no rule for when a model change triggers reruns, and the results index does not show how far each finding can be trusted. The step-back review sorted 54 findings by hand (docs/notes/step-back-review.md, section 3).

## Decision

1. **Every result names its model version.** A results doc states, near the top, the flags it ran under: agent values (v1, v2, v2b, hybrid), pleasure scale (clip or saturating), bills, satiety expectation, levers and fixes, world family. Short form, e.g. `model: hybrid · sat · bills · satiety=world`. Older docs get this line when they are next touched; it is not backfilled in one pass.

2. **Every model change lists what it could affect.** The prereg or design note for a model change includes a short "Findings this could move" list, drawn from the results index. A change that touches how agents decide, the pleasure scale, or the world's economics lists every finding that runs through those parts.

3. **Each finding carries one of three labels** in the results index:
   - **holds across versions:** the claim keeps its sign class under every model version it has been run on (at least two). Example: pairing pressure holds people in.
   - **version-dependent:** the sign class differs across versions. It is reported with the versions named and is not patched to rescue it.
   - **superseded:** a known bug or a fitted parameter produced it. It stays on record as history, with a pointer to what replaced it.

   A finding run under one version only is labelled **single-version** until it is rerun.

4. **When reruns happen.** A model change that could move a finding on the "Findings this could move" list triggers a rerun only for findings that are cited as current (in the README, claims or one-pager) or that a planned experiment builds on. Others keep their label and a note. Reruns put the old and new versions side by side and use the stop rule.

5. **Old results are never edited in place.** Numbers, verdicts and text in a results doc stay as run. Changes go in dated notes at the top, in the index label, and in the hypothesis status.

## Consequences

- The results index gains a label column. It is filled from the step-back review's ledger and the third formation check, and kept current by whoever writes the next result.
- Preregs gain a "Findings this could move" line for model changes, next to "Are we measuring what we say?".
- Citing a finding means citing its label. "Holds across versions" is the only label that should appear without a qualifier in the README.
- Cost: reruns are expensive (performance.md). Rule 4 limits them to findings that are cited or built on.
