# Negative results

Experiments or checks that failed to show the predicted effect, reported as findings (see kill criteria in RATIONALE.md section 9). Purpose: negative results are recorded, not hidden.

## 2026-11-10 (V2)

- **First-run failure of the scripted patch.** Prediction 3 expected the per-month cap card to pass all four patch checks. As first written (single condition, no `catch > 0`), it failed no-deadlock (b) and repair path (d) at the stated bound, naming P1 (and F1 for d). Cause: a real bug in the card. Fixed and recorded; the prediction is left as written in docs/results/v2-prereg.md. See docs/results/v2.md.
