# Negative results

Experiments or checks that failed to show the predicted effect, reported as findings (see kill criteria in RATIONALE.md section 9). Purpose: negative results are recorded, not hidden.

## 2026-11-10 (V2)

- **First-run failure of the scripted patch.** Prediction 3 expected the per-month cap card to pass all four patch checks. As first written (single condition, no `catch > 0`), it failed no-deadlock (b) and repair path (d) at the stated bound, naming P1 (and F1 for d). Cause: a real bug in the card. Fixed and recorded; the prediction is left as written in docs/results/v2-prereg.md. See docs/results/v2.md.

## 2026-11-10 (V2b)

- **The SLEEC-style form did not carry over uniformly.** The "when <condition> then <obligation> unless <exception>" form fits only `must not`. `must` and `may` needed their own templates, `unless` and `or` could not be expressed, and arithmetic conditions read poorly. All four preregistered checks passed (docs/results/v2b.md); this is a naturalness limit, not a meaning loss. No claim yet that readers do better with it.

## 2026-11-10 (VPGG rediscovery)

- **Oscillation clause of prediction 3 failed.** In the voluntary public goods game (Hauert et al. 2002; N=5, r=3, sigma=1, 20 seeds) cooperator share held at 0.263 (paper's equilibrium 0.27) and payoff at 0.984 (about sigma), but its standard deviation over time was 0.013 to 0.020 against a preregistered floor of 0.05 in at least 18 seeds. By the committed verdict rule the pipeline did NOT rediscover the full result. Cause unknown: the amplitude floor was a guess, or the assumed update knobs (5-round payoff averaging, revision rate 0.1) damp the cycle, or the model does not cycle. Not retuned; see docs/results/vpgg.md.
