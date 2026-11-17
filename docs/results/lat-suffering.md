# Where living apart together's non-offsettable suffering comes from

> **Note 2026-11-16:** see [tt2.md](tt2.md). With gifts allowed between LAT partners (existing `give` rule) at TT's q, LAT's extra suffering falls +0.00033 → +0.00013; at q = 0.3 (TT2) it is +0.00004 [0, +0.00012] with no gift given, because few pairs choose LAT. The rest is still denied money, now in LAT weeks beside a partner the gift rule does not let give (prosocial 0.41 < 0.5). The text below is as run.

Wording rule: agents feel nothing; "suffering", "denied" and "money" are glosses for modeled numbers.

## 2026-11-15: attribution under A6 (no model change)

**Model line (A6):** `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit · hybrid_tally=level · tally_half=13 · tally_line=0.02 · exit_grow=0.04 · hybrid_outside=lived · friend_satiety · fresh_return`, exit fallback F4 with items (F5 in the all-aids arm), corrected rule (ADR 0020). H41's harness, 120 confirmatory pairings, seed 0.

**What was run.** An instrumented rerun of H41's B and LAT arms under A6 (240 runs; 32 all-aids runs before that arm was stopped to save time). The instrument (scripts/lat_suffering.py) reads the lived world after each week: where each member lives, its unrounded need levels, which needs are under the denied line (level below 0.15 with salience at least 0.12), and how much non-offsettable suffering each condition adds once past its 4-week onset. Nothing in the model changed. **Check:** the recomputed suffering matches the A6 rows' `snon` in 120 of 120 B runs, 120 of 120 LAT runs and 32 of 32 all-aids runs, with 0 week-level mismatches. Rows in runs/lat-suffering/a6.jsonl; tables in runs/lat-suffering/a6.json.

**The number being explained.** LAT minus B under A6: **+0.00079 [+0.00016, +0.00160]** non-offsettable suffering per member-week (LAT 0.00178, B 0.00099; pairing bootstrap). It is small: at the denied intensity of 0.5, it is about one extra member-week in 600. (The 0.0027 vs 0.0023 quoted in h41-choice-aids.md is the first H41 run, on the older hybrid; this note explains A6's.)

### The answer, plainly

**It is money, and it is the missing shared pot, not the second rent and not missing the partner.** All of it is the "denied" condition, and all of that is the money need (LAT 0.00172 of 0.00178; the rest, 0.00005, is security). Connection and rest are never denied, in any arm, in any week. Trapped and diminished never fire under LAT (both need a member in a household).

The mechanism, read from the weeks: a member who **loses their job** (the world's jobless shock) while **living apart with no shared pot** runs its money to 0 and stays there for the jobless stretch. In a household the same shock is absorbed: an overdrawn member draws from the pot (the pot's safety-net rule keeps money at 2 or more, money level 0.25, above the line). Of the 125 denied member-weeks in the LAT arm that carry the full instrument (86 of the 120 runs; the first 34 ran before work and shocks were recorded), 121 have money 0 and no work, and 104 are in a jobless stretch (most of the rest are the week the jobless count runs out). Only 8 are in a household, and those are households whose pot had run dry.

It is not two rents: in this world a member apart with Friend C pays no extra living cost (the 1.5 solo cost applies only to living alone, and nobody lives alone; H41 found the same). It is not "security from losing the pot" in the model's security need: security is denied in 4 member-weeks out of 37,440. The pot's loss shows up in the money need, as an empty purse during job loss.

### Breakdown

**By need** (per member-week, all non-offsettable suffering):

| Arm | Total | Money | Security | Connection | Rest |
|---|---|---|---|---|---|
| B | 0.00099 | 0.00099 | 0 | 0 | 0 |
| LAT | 0.00178 | 0.00172 | 0.00005 | 0 | 0 |
| all aids (32 of 120 pairings) | 0.00411 | 0.00411 | 0 | 0 | 0 |

**By where the member lives** (LAT arm; share of member-weeks, suffering contributed, and suffering per week spent there):

| Mode | Share of weeks | Contributes | Per week in mode |
|---|---|---|---|
| household (both in) | 0.760 | 0.00013 | 0.00018 |
| apart with Friend C, not LAT (between LAT spells, or after an exit) | 0.082 | 0.00128 | 0.01559 |
| LAT, with Friend C | 0.148 | 0.00029 | 0.00199 |
| alone in the household (lone member) | 0.010 | 0.00007 | 0.00656 |
| LAT alone, apart alone | 0 | 0 | |

Every LAT member in these runs lives with Friend C; nobody lives alone (so "alone vs with Friend C" has only one side). **The difference from B, paired by pairing:** apart with Friend C +0.00048, LAT with Friend C +0.00029, lone member +0.00001, household 0.

**By pairing:** only **6 of 120 pairings** differ at all, all upward. In each, the pair is in a household in B and apart (LAT, or apart between LAT spells) under the LAT arm when a jobless shock arrives. Example: g-00100 with g-01100 lives in a household all 156 weeks under B. Under LAT it is LAT for 104 weeks, apart for 13, LAT for 26, apart for 13; B's member is jobless at the end and has 12 weeks of denied money (weeks 144 to 155).

**By persona** (LAT minus B): g-11110 +0.00028, g-01100 +0.00020, g-00111 +0.00017, g-11100 +0.00011, g-11111 +0.00003; every other persona 0. These are the members whose job loss fell in an apart stretch; the persona traits matter less than when the shock lands.

**Lone members** (one member in the household alone): 1.0% of LAT-arm weeks and 1.7% of B weeks; they add 0.00007 and 0.00005. Not the source.

**Before or after a household:** of LAT's 0.00178, 0.00111 falls on members who had lived in a household earlier in the run (after an exit or between spells) and 0.00067 on members who never had.

### What this means for the time-together redesign

The model's LAT suffering is not about time together at all. LAT pairs keep their chosen sessions at no extra cost, and the connection need is never short. So the author's question ("losing time together") had no hook in A6's non-offsettable suffering. It is a money-buffer effect: living apart means no shared pot to fall back on when a job is lost. Real LAT couples may pool money or help each other without a shared home; this model gives them no way to, which is a gap (below). The redesign ([time-together-prereg.md](time-together-prereg.md)) changes time together and travel; it does not touch the pot, so it should not change this mechanism, except through who chooses LAT.

### Can be about / cannot be about

This can be about which modeled need and which living arrangement produce the non-offsettable suffering of H41's LAT arm under A6. It cannot be about real couples living apart, their money, or job loss (the jobless shock schedule is ASSUMED; limits 5, 6, 10, 11).

### New gaps

- **No money help without a shared home.** A LAT partner cannot draw on, or be given, the other's money through a pot. In this world `give` to the partner needs both in the household. That is the whole source of LAT's extra non-offsettable suffering.
- **The suffering is concentrated in 6 pairings.** The interval is clear of 0, but it rests on when 6 job losses land.
- **The all-aids arm was attributed on 32 of 120 pairings only** (stopped for time). Its 0.00411 is also all money.

Reproduction: `uv run python scripts/lat_suffering.py --run --arms B,lat` (about 30 minutes on 4 workers), then `--analyze`.
