# Household v2 preregistration (committed before any v2 run)

Status: instrument, scripted agents, no LLM, no network. Findings are about rule systems and scripted agents with modeled preferences, not about real people. Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences. Parent docs: docs/results/household.md (v1; its prereg is untouched), docs/decisions/0010-hedonic-model.md (written after the runs, slice 4).

## What changes from v1 (author decisions, 2026-11-10)

Weekly step (156 weeks, money settles every 4 weeks; ASSUMED simplification of the month). Agents have goals: needs that decay on real clocks (rest, connection, money, security) and aspirations from persona weights. Rare shocks. Two hedonic channels (pleasure; suffering as offsettable or non-offsettable). Spiral dynamics around a tipping point. Sanctions (`or_else`) are enforced: a card with a sanction is a soft rule (an agent may break it and pays the sanction); a card without one is a hard wall. Agents are driven by their persona's needs and aspirations through a simple utility policy over the hedonic model. v1 monthly world and the seam ladder code are untouched.

## Frozen definitions

- Runs: 8 variants (the 7 of v1 plus `author_seed`) x 15 unordered pairs of the 6 hand personas (lower id plays Partner A, who earns more) x seeds 0, 1, 2 = 360 runs. Shocks use common random numbers per (pair, seed), identical across variants. Mismatched pair = p-anchor with p-wanderer.
- Agent upward spiral: hedonic position B at the last week >= tipping point + 0.20, and no non-offsettable suffering in the last 8 weeks. Downward: B <= tipping point - 0.20. Otherwise stalled. Tipping point 0.0.
- Pairing (one run) is UPWARD when both partners are upward. Variant upward share = mean over its 45 runs.
- Time to cross = first week after which B stays on the upward side of the tipping point to the end; undefined if never.
- Automatic FAIL of a run: any partner has 6 or more consecutive weeks of non-offsettable suffering. A variant FAILS when at least one third of its runs fail. Average pleasure is computed over passing runs only.
- Freedom and cooperation: the v1 formulas, unchanged, over weekly rows (cooperation's "mutual aid" is a contribution in the 4-week month).
- Non-trivial trade-off: the (freedom, cooperation) frontier over variant means has at least 2 variants, and two of them differ by at least 0.05 in freedom and by at least 0.05 in cooperation in opposite directions.

## Parameter block (ASSUMED, exposed as HedonicConfig in src/mar/hedonic.py; changed only by a recorded deviation)

tipping point 0.0, start position 0.0, flow gain eta 0.30, upward feedback 0.05 per unit above the tip, downward feedback 0.08 per unit below (suffering compounds slightly faster), capacity = clip(1 + 0.6 (B - tip), 0.5, 1.3) times (1 - 0.5 N). Need clocks per week: rest decay 0.50 with base refill 0.40 and rest action +0.30, work block -0.10; connection decay 0.30, cohabitation refill 0.10, see friend or time together +0.35 or +0.30, friend-initiated contact +0.15; money level = money / 8, living cost 2 per week, bills 10 per 4 weeks (6 alone); security decay 0.02, refill 0.03 x clip(assets / 60). Non-offsettable onset: a condition (need level below 0.15, no real exit, steadily restricted options) held 4 consecutive weeks. Intensities: trapped 0.5, need denied 0.5, diminished 0.4. Non-offsettable load N decays 0.25 per week only when no such condition is active. Pleasure = 0.5 needs satisfied + 0.5 aspirations met + events; offsettable suffering = need deficits + 0.3 x aspirations unmet.

Shock rates per person-year: job loss 0.12 (BLS JOLTS layoffs and discharges rate about 1.0 to 1.1 percent of employment per month, bls.gov/news.release/jolts.htm; duration 8 to 26 weeks ASSUMED), illness 0.08 (ASSUMED; 3 to 8 weeks), new connection 0.20 (ASSUMED), move 0.087 per household-year (Census CPS 2022 mover rate 8.7 percent, census.gov geographic mobility release CB23-TPS.87; secondary-source reading, not opened). Loneliness is the motivation for the connection clock (US Surgeon General advisory 2023: about half of US adults report loneliness; from news coverage). Time-use proportions (rest, work, leisure) are ASSUMED, not taken from the American Time Use Survey.

Spiral motivation: upward loop, Fredrickson 2001, American Psychologist 56(3):218-226, and Fredrickson and Joiner 2002, Psychological Science 13(2):172-175 (both verified by search). Downward loop: Mani, Mullainathan, Shafir and Zhao 2013, Science 341:976-980 (scarcity impedes cognitive function, verified by search); poverty-trap models (Carter and Barrett 2006, J. Development Studies 42(2), named from memory, unverified).

## Predictions

1. With goals and enforced sanctions a non-trivial trade-off appears (definition above).
2. The `trap` variant FAILS: in at least 8 of the 15 pairings (seed-majority) at least one partner has 6 or more consecutive weeks of non-offsettable suffering; no other variant fails except possibly `contact_free`.
3. `author_seed` (negotiation stubbed as fixed exit terms: leave with exactly half) has an upward share at least 0.10 above `baseline`'s, and does not fail.
4. The Anchor/Wanderer pair has the lowest mean of (lower partner's B at the end) among the 15 pairings in at least 5 of the 8 variants.
5. The seam ladder table (depth, agents, status per seam) is identical to the v1 run, since seam_depth.py and the v1 world are unchanged, and tests/test_seam_depth.py still passes.

If a prediction fails it stays failed here; results go to docs/results/household-v2.md.
