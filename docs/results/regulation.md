# Regulation results: attuning versus appeasing partners of pressing personas

Prereg: docs/results/regulation-prereg.md (committed before the confirmatory run; no threshold or test was changed after). Code: src/mar/regulation.py, tests/test_regulation.py, scripts/regulation_run.py. Raw rows: runs/regulation/results.json (not committed). Theory home: docs/theory.md. Scripted agents, levers off, no model calls, $0. Wording rule: agents feel nothing; "pleasure" and "load" are glosses for modeled quantities.

Design as preregistered: 36 pairings (3 pressing personas x 6 partners x 2 seatings), seeds 0..9, three partner conditions (BASELINE, APPEASE, ATTUNE), three rule sets (`author_seed_v2_free_exit` primary, `baseline`, `no_exit` control), 3240 runs. Unit of resampling: the pairing; paired tests, one-sided permutation, 95% BCa intervals, Holm over R1 to R4 at free_exit. Differences are APPEASE minus ATTUNE, in pleasure-weeks over 156 weeks, unless stated.

## Prereg versus actual (primary rule set, free_exit)

| ID | Predicted | Actual (estimate [95% interval]) | Raw p | Holm p | Status under the prereg verdict rule |
|---|---|---|---|---|---|
| R1 | presser's gain over partner larger against APPEASE | +5.75 [1.12, 10.37]; mean gain +5.33 vs -0.42 | 0.011 | 0.033 | DESCRIPTIVE (underpowered): consistent with the prediction |
| R2 | (a) APPEASE partner pleasure lower AND (b) fewer conflict episodes | (a) +1.11 [-3.64, 6.58], p 0.655, wrong direction; (b) refusal weeks -1.12 [-1.84, -0.44], p 0.002 | 0.655 (max) | 0.655 | DESCRIPTIVE: NOT consistent (clause a fails) |
| R3 | presser's own pleasure lower against ATTUNE | -6.86 [-12.87, -1.26]; 114.6 vs 121.5 | 0.013 | 0.033 | DESCRIPTIVE (underpowered): consistent with the prediction |
| R4 | more pressing acts borne by the partner under APPEASE | +23.9 [9.66, 40.16]; 56.0 vs 32.1 acts | 0.0005 | 0.0018 | CONFIRMATORY: holds robustly (Holm p < 0.05 and interval above 0) |

Cliff's delta over the 36 pairing values: gain +0.32, presser pleasure +0.22 (APPEASE higher), partner pleasure +0.07, pressing acts +0.19, refusal weeks -0.25.

Same tests, SECONDARY rule sets (raw one-sided p; estimate APPEASE minus ATTUNE):

| Rule set | R1 gain | R2 partner pleasure | R2 refusal weeks | R3 presser pleasure (ATTUNE minus APPEASE) | R4 pressing acts |
|---|---|---|---|---|---|
| baseline | +8.31 [2.81, 13.49], p 0.003 | +12.86 [6.71, 19.61], p 0.9998 (wrong way) | -1.07, p 0.001 | -21.17 [-26.32, -15.95], p 0.00005 | +43.5 [29.0, 58.6], p 0.00005 |
| no_exit | +22.90 [17.3, 29.2], p 0.00005 | -5.28 [-9.08, -1.83], p 0.004 | -2.02, p < 0.0001 | -17.63 [-21.06, -14.44], p 0.00005 | -2.58 [-3.92, -1.38], p 1.0 (wrong way) |

Descriptive means (pleasure-weeks of 156; presser / partner / pressing acts / share of partners who left / weeks both in the household):

| Rule set | BASELINE | APPEASE | ATTUNE |
|---|---|---|---|
| free_exit | 111.5 / 114.8 / 40.8 / 0.41 / 83 | 121.5 / 116.2 / 56.0 / 0.26 / 118 | 114.6 / 115.1 / 32.1 / 0.42 / 91 |
| baseline | 111.8 / 110.5 / 43.0 / 0.68 / 57 | 133.0 / 121.3 / 79.7 / 0.23 / 132 | 111.9 / 108.5 / 36.2 / 0.71 / 50 |
| no_exit | 98.6 / 99.8 / 106.2 / 0.00 / 156 | 125.1 / 103.4 / 61.2 / 0.00 / 156 | 107.5 / 108.6 / 63.8 / 0.00 / 156 |

Conflict (pressing) weeks, free_exit: APPEASE 55.8, ATTUNE 30.6 (difference +25.3 [10.2, 42.2]). Refusal weeks: APPEASE 0.0 by construction, ATTUNE 1.1, BASELINE 1.5.

## Plain-English reading

What held. Against a yielding partner the presser does better, both absolutely and relative to the partner, and its pressing acts keep landing: pressing is about 24 acts a run heavier on an appeasing partner than on an attuned one, and the presser ends 7 pleasure-weeks ahead. Against the attuned partner the presser's advantage over its partner disappears (gain -0.4 under free exit), which is the direction the theory says. The load-conservation proxy (R4) is the one confirmatory result.

What did not hold, and the more interesting part. The appeaser was not worse off in this model. In free_exit its lifetime pleasure is the same as the attuned partner's (116.2 vs 115.1), and in `baseline` it is clearly higher (121.3 vs 108.5), because appeasing partners almost never leave (23 percent against 71 percent) and a household that stays together keeps the connection and security a leaver loses. Only with no exit is the appeaser worse (103.4 vs 108.6, the one place the predicted cost shows). So in this world "appeasement trades long-run pleasure for short-run pain" is not visible: the model has no long-run cost of resentment, suppressed needs or eroded trust beyond the needs the policy itself drops, and APPEASE's pre-emptive yielding includes extra time together, which is itself pleasant for both. Conflict also did not fall under APPEASE. Open refusals fell (R2b holds, trivially: APPEASE never refuses), but the presser's pressing weeks nearly doubled (55.8 vs 30.6), consistent with conservation: the load the appeaser absorbs is load the presser stops having to economize.

Pressing paid off less than the earlier results suggested in one more respect. The earlier finding that pushy personas keep winning is, in this model, a finding about partners who yield: with an attuned partner the same scripts yield a gain of about zero in free_exit and baseline, and a loss against attune relative to appease in every rule set (R3: -6.9, -21.2, -17.6). That fits H01 (pressing is costly to the presser even with no exit) and adds that the cost is larger the less the partner yields. It does not by itself show that the scripted partners in earlier runs were appeasers; it shows they could be read that way.

## Limits

- The presser never responds to its partner's regulation; there is no co-adaptation and no learning on either side.
- A partner cannot refuse a veto or a take from the shared pot (no such action exists in household.py and it was not edited). Most of ATTUNE's "decline" is therefore limited to requests, whose effect in this world is small; the two policies differ mainly through gifts, `together` time, giving up friend and spending actions, and when each leaves. R1 and R3 are consistent with the prediction, but an R1 null would have had this hole as a candidate explanation; the positive result may be carried largely by APPEASE's extra `together` time and by who stays, which the run does not separate. The per-presser means show the R4 gap is carried by the over-asker (about 141 vs 70 acts per run; controller 2 vs 2; free-rider 25 vs 25); why is not isolated here.
- R1, R2 and R3 were marked DESCRIPTIVE in the prereg (36 pairings is below the pairings needed at the pilot spread); "consistent" is the strongest wording they get. R4 was the only confirmatory test.
- Displeasure and conflict proxies, the fit thresholds, the 2-week cool-off, the 0.70 tolerance ceiling and every constant in `regulation.PARAMS` are ASSUMED and untuned. A different reading of "attune" (for example, one that also withholds `together` time when it does not fit) would likely change R1 and R2.
- "Relational load" is a count of presser acts received, not a felt burden; the conserved-load theory (docs/theory.md) is tested here only through that proxy.
- Six hand-written partner personas; scripted presser; one parameter point; findings about these agents, not people.

## Checks

tests/test_regulation.py: 10 hand-case tests (proxy monotonicity, APPEASE accepts a misfit request, ATTUNE honors a fit, declines a misfit and grants past the tolerance ceiling, APPEASE drops see_friend and spend_self, exit gating for both, BASELINE bit-identical to no regulator, determinism, no-exit wall, 36 pairings). Pilot (EXPLORATORY, seeds 1000..1002) gave the same signs on all twelve prediction-by-rule-set cells.
