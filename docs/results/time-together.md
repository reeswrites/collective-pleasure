# Time together in two kinds: background time, chosen time, travel and substitution

Wording rule: agents feel nothing; "pleasure", "suffering", "value", "forecast" and "held" are glosses for modeled numbers.

**Model line (TT):** `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit · hybrid_tally=level · tally_half=13 · tally_line=0.02 · exit_grow=0.04 · hybrid_outside=lived · friend_satiety · fresh_return · together_bg=1.1 · lat_bg_keep=0.2 · lat_travel=0.33 · together_subst`, exit fallback F4 with items (F5 in the prenup and all-aids arms), corrected rule (ADR 0020). Compared with A6 (the same line without the last four flags).

Preregistration: [time-together-prereg.md](time-together-prereg.md) (commit bcbca70, before any code; Amendment 1 before any run). Evidence: [../notes/time-together-research.md](../notes/time-together-research.md). LAT attribution under A6: [lat-suffering.md](lat-suffering.md). Code 6464472. Run 2026-11-15 to 2026-11-16, scripted agents, no model calls, at most 4 workers under `caffeinate -i`. Rows in runs/time-together/ (queue.sh, analysis.json); PT-H and PT-R in runs/hybrid-passtest-tt/ and runs/value-consistency-hybrid-world-tt/; LAT attribution under TT in runs/lat-suffering/tt.jsonl.

## In one paragraph

Counting background time from a shared home makes households worth more, and that now drives most of what H41 shows. **In every arm, pleasure rises by about +0.012 and liberty falls by 0.07 to 0.28, because more pairs form (B: 0.80 → 0.95 at week 0) and stay in households, where liberty is lower.** LAT is chosen half as often (46 → 24 of 120 at week 0; LAT weeks 0.148 → 0.053). Against B, LAT keeps its A6 signs: weeks together −, liberty +, pleasure flat (−0.0011, inside the margin). By the verdict rule that is a **trade-off, not a win**, as before, at about 60% of A6's sizes. LAT's extra non-offsettable suffering drops from + under A6 to 0 under TT (+0.0003 [+0.0000, +0.0009]). It is still all denied money while apart with no pot; fewer pairs are apart. All aids now costs pleasure beyond the margin (−0.0032), so it is a trade-off with a pleasure cost. H41 is still not supported. **Two checks fail: PT-R (the routine's best-action share T3 is 0.898, 4.9 points below v2's 0.947; the bar is 2 points) and KO1 (+0.037 [+0.019, +0.055], worse than A6's +0.027).** PIN, KX2, PT-H, KW and the four new unit checks pass. **By the prereg's rule TT is not usable as the time-together version, and the hybrid is not ready to freeze with these flags.** The sweeps show that the one unsourced number, the value of a background hour (q = 0.1, giving `together_bg` 1.1), sets how big every effect is. The signs of LAT's trade-off hold at every sweep end.

## Known-answer checks

| ID | Result | Bar | |
|---|---|---|---|
| PIN | 50 slow pins byte for byte with the four new flags at their defaults (runs/time-together/pins.log); fast suite 984 passed | byte for byte | **PASS** |
| KB1, KB2, KT1, KS1 | background time in a shared home (at 1/3 it equals the old `conn_cohabit` at full capacity); LAT keeps background only in a week with a session; travel costs 2.33 units a member under LAT and 2 in a home; substitution factor mean 1.00 over 38 personas, the same factor in world and routine (tests/test_time_together.py) | | **PASS** |
| KW | w = 2 declines, w = 0 forms, with TT's flags | | **PASS** |
| KX2 | DiD **+0.0079 [+0.0053, +0.0114]**; clauses i–iii hold; 46 forecast futures with an exit, first at about week 21 (runs/time-together/kx2-tt.json). A6: +0.020 | DiD > 0, interval above 0 | **PASS** |
| PT-H | H1 **+0.0035** [+0.0011, +0.0059]; H2 **0.951** (1,180 option-units); H3 **97.2%** (458); 564 choice-units | ±0.010 (interval inside ±0.015); ≥ 0.80; ≥ 80% | **PASS** |
| PT-R | T1 0.952 (v2 0.955), T2 0.963 (0.973), **T3 0.898 (0.947)**, T4 0.940 (0.959), T5 1.05; T6 holds (see_friend gap 0.0009, rest 0.0011; together has 85 rows, under the 100 needed for a bar) | each no more than 0.02 below v2 | **FAIL** (T3, by 0.049) |
| KO1 | **+0.037 [+0.019, +0.055]**, 66 bar exits in B (A6 +0.027 [+0.004, +0.048]) | mean within ±0.02, interval inside ±0.04 | **FAIL** (mean and interval) |

**Usable / ready to freeze? No.** The prereg's rule needs PIN, the unit checks, KX2, PT-H, PT-R and KW to pass. PT-R fails. KO1 failed under A6 already and is worse now. Nothing was changed to make either pass.

**What the PT-R miss means.** Under TT the routine picks the action that is actually best one week ahead in 89.8% of decisions, against 94.7% for v2 on the same sample and 95.3% under A6. The per-action value gaps (T6) stay small, so values are close but the ranking near the top is less often right. **The cause was not diagnosed in this slice.** The likely place is where the routine's one-week projection and the world now differ: background time enters connection and pleasure, and the routine sees it through `agent_values.snapshot`. That is a hypothesis to test, not a finding.

**What the KO1 miss means.** Outside futures have no partner and so no background time. Lived leavers re-form and get it back. The forecast of leaving is now more pessimistic than the life lived after leaving, by more than under A6. This is the same stand-in error A6 named, made larger because households are now worth more.

## H41 under TT beside A6

**Per arm, A6 → TT** (means over 120 pairings):

| Arm | Weeks together | Formed at week 0 | Liberty | Pleasure | Non-offsettable suffering | LAT weeks |
|---|---|---|---|---|---|---|
| B | 0.886 → **0.929** | 0.80 → **0.95** | 2.017 → **1.907** | 0.9635 → **0.9765** | 0.0010 → 0.0007 | 0 |
| lat | 0.758 → **0.876** | 0.575 → **0.767** | 2.299 → **2.075** | 0.9625 → **0.9754** | 0.0018 → **0.0011** | 0.148 → **0.053** |
| all | 0.616 → **0.781** | 0.508 → **0.750** | 2.440 → **2.163** | 0.9608 → **0.9733** | 0.0033 → **0.0022** | 0.257 → **0.110** |

TT − A6, paired, is + for weeks together, formation and pleasure and − for liberty in **every** arm (pleasure +0.011 to +0.013, intervals clear of 0; liberty −0.07 to −0.28). So **the new background pleasure is a level shift for anyone in a household. It is the main thing these runs show.** Lived pleasure moves with it: the gain is not a reward paid.

**LAT and all aids against B:**

| | Weeks together | Formed | Liberty (freedom) | Pleasure | Non-offsettable suffering | Verdict |
|---|---|---|---|---|---|---|
| LAT, A6 | −0.128 [−0.179, −0.081] − | −0.225 − | **+0.282** [+0.198, +0.375] + | −0.0010 [−0.0018, −0.0003] 0 | **+0.0008** [+0.0002, +0.0016] + | trade-off |
| LAT, TT | −0.053 [−0.083, −0.027] − | −0.183 − | **+0.169** [+0.106, +0.238] + | −0.0011 [−0.0018, −0.0005] 0 | **+0.0003** [+0.0000, +0.0009] 0 | trade-off |
| all, A6 | −0.270 − | −0.292 − | +0.423 + | −0.0027 0 | +0.0023 + | trade-off |
| all, TT | −0.148 [−0.203, −0.096] − | −0.200 − | +0.257 [+0.161, +0.361] + | **−0.0032** [−0.0045, −0.0019] **−** | +0.0015 [+0.0006, +0.0025] + | trade-off with a pleasure cost |

**H41 under TT: not supported** (no aid raises weeks together). Judged on pleasure AND freedom together, no aid is a win. LAT and all aids still buy freedom with a little pleasure.

**Stop rule (A6 against TT; sign classes against B).** The same class under both:
- pressure holds people in at every level;
- P4 raises pleasure;
- the trial lowers weeks together and raises liberty;
- LAT and all aids lower weeks together and formation and raise liberty;
- cheap housing changes nothing;
- H41 is not supported.

**Depends on how time together is modeled** (A6 class → TT class, not patched):
- LAT's non-offsettable suffering: + → 0.
- All aids' pleasure and lived pleasure: 0 → −.
- Pressure's formation at week 0: + → 0 at P0.5, P1, P2 and P4 (B already forms 0.95, so there is little left to add).
- P2: weeks together 0 → +, pleasure + → 0.
- P1's worse-off partner: + → 0.
- Better information: weeks together 0 → +, suffering + → 0.
- The prenup's suffering: 0 → +.
- The trial's formation: 0 → −.

## The predictions

| ID | Expected | Actual | |
|---|---|---|---|
| TT1 | B forms at least as often | 0.80 → 0.95 (+0.150 [+0.092, +0.217]) | holds |
| TT2 | fewer pairs choose LAT; LAT weeks fall | 46 → 24 of 120; 0.148 → 0.053 | holds |
| TT3 | LAT vs B: weeks together −, liberty +, pleasure 0 or −; a trade-off | −0.053, +0.169, −0.0011 (0) | holds |
| TT4 | members with a higher partner share lose more under LAT (negative slope); with substitution off, the slope is closer to 0 | slope **−0.0017 [−0.0040, +0.0002]** (A6 −0.0052 [−0.0084, −0.0023]); with substitution off (60 pairings) −0.0019; by tercile of s: −0.0009, −0.0011, −0.0013. Within-life measure (LAT weeks minus household weeks, 50 members): −0.026 per unit s (A6, 48 members: −0.041) | **misses**: the slope weakened instead of strengthening, and turning substitution off did not move it |
| TT5 | LAT's suffering: no direction | + → 0; still all denied money while apart, now in 2 pairings (+0.00033 [+0.00000, +0.00093]) | descriptive |
| TT6 | H41 not supported | not supported | holds |

**TT4, plainly: the author's "a varied life is hit less" does not show up more strongly under the substitution flag.** In A6, a member whose social weight is mostly on the partner already loses more pleasure under LAT, through the togetherness aspiration. Under TT the slope is about a third of A6's, and its interval reaches 0. The likely reason is that fewer and different pairs choose LAT under TT. The paired arm contrast mixes "who chooses LAT" with "what LAT costs". The within-life measure keeps a negative slope under both. Either way, scaling the together event by s/0.5 did not add a visible substitution effect beyond what the persona weights already do.

## Sweeps (descriptive; B and LAT arms; every second pairing, 60 pairings; one number at a time from TT)

LAT against B, and LAT's take-up. The centre, TT on the same 60 pairings: weeks together −0.039, liberty +0.150, pleasure −0.0008, suffering +0.0001; LAT at week 0 12 of 60; TT4 slope −0.0017.

| Sweep | Weeks together | Liberty | Pleasure | Suffering | LAT at week 0 | LAT weeks | TT4 slope |
|---|---|---|---|---|---|---|---|
| `together_bg` 0.33 (q ≈ 0.03) | −0.101 | +0.245 | −0.0015 | **+0.0009 (+)** | 18 | 0.089 | −0.0028 |
| **centre 1.1 (q = 0.1)** | −0.039 | +0.150 | −0.0008 | +0.0001 (0) | 12 | 0.044 | −0.0017 |
| `together_bg` 2.2 (q = 0.2) | −0.015 | +0.127 | −0.0002 | 0 | 11 | 0.022 | −0.0003 |
| `lat_travel` 0.17 | −0.028 | +0.152 | −0.0005 | 0 | 12 | 0.032 | −0.0016 |
| `lat_travel` 0.67 | −0.035 | +0.101 | −0.0008 | 0 | 7 | 0.038 | +0.0001 |
| `lat_bg_keep` 0 | −0.043 | +0.141 | −0.0010 | +0.0003 (0) | 9 | 0.046 | −0.0017 |
| `lat_bg_keep` 0.4 | −0.037 | +0.154 | −0.0006 | +0.0001 (0) | 13 | 0.042 | −0.0015 |
| substitution off | −0.026 | +0.129 | −0.0005 | 0 | 11 | 0.033 | −0.0019 |

**The 0.1 value of a background hour is the number that matters.** Moving it from about 0.03 to 0.2 changes LAT's weeks-together cost by about seven times (−0.101 to −0.015) and its liberty gain by about two times. It also decides whether LAT's extra suffering is + (at 0.33) or 0 (centre and above), and how strong TT4's slope is. **No sweep end changes the sign class of LAT's weeks together, liberty or pleasure.** "LAT is a trade-off of weeks together for freedom at a small pleasure cost" is robust to every swept number. Its size is not. Travel and the share of background time LAT keeps matter much less. An hour of travel each way cuts LAT take-up (7 against 12 of 60) and its liberty gain (+0.101), and changes no class. Turning substitution off changes no class.

## Does time together still drive the results?

**Yes, more than before.** Under A6, time together was one session action plus 0.10 connection, and LAT cost nothing in time. Under TT, a shared home carries an automatic pleasure term. That term:
- raises pleasure in every arm;
- pulls pairs into households (B forms 95% at week 0);
- costs liberty everywhere;
- halves LAT's take-up.

Every size depends on q, which has no source. The hours (33 a week) are sourced; their value is not. H41's verdict and the signs of LAT's trade-off survive the change and every sweep. Anything stated as a size (how much liberty LAT buys, how much more people form) is now a statement about q.

## Story check

Not done in this slice. The prereg named four lives to read (a pair that kept LAT under TT, one that switched from LAT to a household, a high-s and a low-s LAT member, one B pair). They remain owed and are listed as a gap.

## New gaps

- **PT-R fails on T3.** The routine's top action is right less often under TT (89.8% against 94.7% for v2). The cause is not diagnosed. The next step is to compare the routine's one-week projection with the world's close in households with background time.
- **KO1 is worse** (+0.037). Outside futures have no background time and never re-form, so the forecast undervalues leaving more now that households are worth more.
- **q has no source.** It sets the size of every TT effect. A source for the value of everyday co-presence against a planned evening (an experience-sampling or DRM contrast within couples) would replace an ASSUMED number with a measured one.
- **The substitution flag did nothing visible.** Scaling the together event by the persona's partner share did not strengthen "a varied life is hit less". The persona weights already did that through the togetherness aspiration under A6.
- **Liberty falls whenever households get better.** Liberty is lower inside a household, so any term that makes households more attractive lowers measured freedom. That is a property of the measure. It is worth stating beside any freedom result.
- **No money help without a shared home** (from [lat-suffering.md](lat-suffering.md)). Under TT it is still the whole of LAT's extra suffering. The author has decided that partners living apart should be able to give money; that is the next change, as its own prereg.
- **The story check is owed.**

## Can be about / cannot be about

This can be about how H41's choice aids, and LAT in particular, and the hybrid's known-answer checks move when the formation check's household counts background time from a shared home (valued at an ASSUMED tenth of a planned evening per hour), charges LAT partners travel time, and scales partner-time pleasure by each persona's weights. It cannot be about real couples, the real value of time with a partner, sleep, meals or travel, or the many-agent world. Limits 1, 4, 5 (most of all: q), 6, 10, 11, 12 and 13 apply.

## Reproduction

`zsh runs/time-together/queue.sh` (pins, reach, KX2, PT-H, PT-R, the core arms, the LAT attribution, sweeps, the other arms; about 20 hours on 4 workers). `uv run python scripts/time_together.py --analyze`; `uv run python scripts/lat_suffering.py --analyze --version tt`; `uv run python scripts/hybrid_passtest.py --tt --analyze`. Tests: `uv run pytest tests/test_time_together.py`; pins `uv run pytest -m slow`.
