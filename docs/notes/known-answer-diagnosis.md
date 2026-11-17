# Known-answer diagnosis: PT-R T3, K1 and KO1 under the time-together versions

Wording rule: agents feel nothing; "pleasure", "value", "forecast", "held" and "worth it" are glosses for modeled numbers.

Written 2026-11-16 by an agent at the author's request ("diagnose, don't fix"). Measurement only: no model behaviour changed, no bar
changed, no parameter fitted. Scripted agents, no model calls. Code: scripts/known_answer_diagnosis.py. Rows: runs/diagnose-t3/
(queue.sh, status.log, k1-*.json, ko1-*.jsonl, ptr-*/rows.jsonl, analysis.json).

**Status: in progress.** PT-R is diagnosed from the rows already on disk; the flag runs for all three checks are queued.

## The three failures, as reported

| Check | A6 | TT (q 0.1) | TT2 (q 0.3) | Bar |
|---|---|---|---|---|
| PT-R T3 (the routine picks the action that is best one week ahead) | 0.953 | 0.898 | 0.869 | no more than 0.02 below v2's 0.947 |
| K1 (the trap's held share / the baseline's) | 0.128 / 0.000 | not run | 0.069 / 0.000 | ≥ 0.10 / ≤ 0.02 |
| KO1 (outside forecast's error, lived − forecast, bar exits in B) | +0.027 | +0.037 | +0.055 | mean within ±0.02, interval inside ±0.04 |

## PT-R T3

**Label: bar (the check), not bug, not mismatch. Confidence: high.**

**What T3 counts.** For each sampled decision, the agent's own top action (or idle, when nothing it values clears its action floor of
0.003) against the action whose one-week actual is best (or idle, when no action's actual is above 0). The two sides use different
floors: 0.003 for the agent, 0 for the actual (scripts/value_consistency.passtest). An action worth between 0 and 0.003 is one the agent
rightly leaves (by its own floor) and T3 counts as a miss.

**What changed.** Background time adds `together_event × together_bg` (0.11 under TT, 0.33 under TT2, times the substitution factor) to
weekly raw pleasure in every household week. Household raw pleasure already sat above the saturating scale's knee (0.8, ADR 0019), so
each action's marginal pleasure is squeezed. On the PT-R rows, a rest in a household:

| | raw pleasure gained | pleasure gained | pleasure / raw (the scale's slope) | own net gained |
|---|---|---|---|---|
| A6 | 0.0755 | 0.0131 | 0.174 | 0.0204 |
| TT | 0.0728 | 0.0066 | 0.091 | 0.0114 |
| TT2 | 0.0793 | 0.0027 | **0.033** | 0.0093 |

Time together shows the same squeeze (0.156 → 0.088 → 0.031). The best action's one-week actual falls into (0, 0.003] in 1.0% of
decisions under A6, 5.8% under TT and **10.2%** under TT2.

**The misses, by kind** (the PT-R rows on disk, 40 pairings, seed 0):

| | T3 | decisions | floor misses | together chosen, rest best (partner share) | other | T3 with one floor (0.003 both sides) |
|---|---|---|---|---|---|---|
| v2 (reference) | 0.947 | 453 | 2 | 6 | 16 | 0.949 |
| A6 | 0.953 | 382 | 4 | 4 | 10 | 0.963 |
| TT | 0.898 | 362 | 13 | 16 | 8 | 0.934 |
| TT2 | 0.869 | 373 | **34** | 10 | 5 | **0.954** |

In the floor misses the agent's value of the best action matches its one-week actual to within 0.00004 on average (TT2: perceived
0.00142, actual 0.00142). **The routine is not mis-valuing anything there; it is right that the action is under its floor.**

**The decisive check: a perfect valuer fails too.** Replace every perceived value with the one-week actual it is held to (the
prereg's own oracle, agent-recalibration-prereg.md, which scored 99.9% on the v1 rows) and keep the 0.003 floor:

| | agent T3 | oracle T3 | agent − oracle |
|---|---|---|---|
| v2 | 0.947 | 0.989 | −0.042 |
| A6 | 0.953 | 0.990 | −0.037 |
| TT | 0.898 | 0.942 | −0.044 |
| TT2 | 0.869 | **0.898** | **−0.030** |

Under TT2 an agent that knew every one-week value exactly would score 0.898, 0.049 under v2's 0.947, and fail PT-R's bar. The
routine's distance from that oracle is the same under every version (−0.03 to −0.04), and smallest under TT2. **All of T3's fall is
the check's ceiling falling, not the routine getting worse.**

**Two more things the T3 bar mixes in.**
- **The reference is from another world.** PT-R holds the hybrid's T3 to v2's T3 "on the same sample", but v2's rows
  (runs/value-consistency-v2-sat-world) were played without background time. Under TT and TT2 the comparison is across worlds.
- **The together misses (TT 16, TT2 10) are the partner share.** The agent values time together as its own net plus prosocial × the
  partner's; T3's "net" target counts only its own. Under T3's "social" target (the utility's own definition) T3 is 0.909 (TT) and
  0.879 (TT2). This was so under v2 and A6 too; it grows a little because own values shrink while the partner term stays.

Flag attribution: queued (below).
