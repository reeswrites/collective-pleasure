# Time together in two kinds: background time from a shared home, chosen time, travel, and substitution (preregistration)

Wording rule: agents feel nothing; "pleasure", "suffering", "value", "forecast" and "held" are glosses for modeled numbers (ADR 0010).

Status: written and committed before any code for these changes and before any run of them. Nothing here is a result. Scripted agents (the hybrid), no model calls, no paid API runs. A world change, not a change to the hybrid's decision rules.

**The author's question, verbatim (typos lightly fixed):** "shouldnt a person with a varied life not be hit as much as losing time together obviously its a good but how is it valued and suffered compared to other things that person could be doing and if they want to hang out they can and also how is time together measured like is sleeping or working together and other stuff transit dinner etc"

**The confirmed design** (read-back rb-2026-11-15-together in experiments/readbacks.jsonl, confirmed "Yes, both"; this wording is binding): "Time together comes in two kinds: background time from sharing a home (sleeping, dinner, errands, being in the same room) and chosen time (planned hangouts). Living apart keeps chosen time but loses most background time and adds travel. A person with many other sources of pleasure and friends is hit less by losing either."

**Evidence:** [../notes/time-together-research.md](../notes/time-together-research.md). **Attribution of LAT's suffering before this change:** [lat-suffering.md](lat-suffering.md) (no model change).

**Model versions (ADR 0020).**
- A6 (current best hybrid): `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · hybrid_lone · hybrid_exit · hybrid_tally=level · tally_half=13 · tally_line=0.02 · exit_grow=0.04 · hybrid_outside=lived · friend_satiety · fresh_return` ([hybrid-a6.md](hybrid-a6.md)).
- **TT (new): A6 plus `together_bg=1.1 · lat_bg_keep=0.2 · lat_travel=0.33 · together_subst`.** All four new flags off by default (`together_bg=0`, `lat_travel=0`, `together_subst=False`; `lat_bg_keep` acts only when `together_bg>0`).

What I knew when writing this: A6's results and rows; the evidence note; the attribution script's first 36 runs (an instrument check: the recomputed suffering matched the A6 rows in every run). No code for these flags exists; nothing has run under TT.

**Can be about / cannot be about.** This can be about how H41's living-apart-together result and the hybrid's known-answer checks move when the household world counts background time from a shared home, charges travel to partners who live apart, and lets each persona's own weights set how much partner time matters, in the formation check's two-person household. It cannot be about people, real couples' time use or LAT couples, the value of an hour with a partner, sleep, meals or commuting, or the many-agent world. Limits that apply ([limits.md](../limits.md)): 1, 4, 5, 6, 10, 11, 12, 13. Limit 5 bites hardest: the per-hour value of background time is ASSUMED with no source.

## The change (four flags, `FixConfig`)

**1. Background time (`together_bg`, sessions a week; default 0 = off).** A member who lives with the partner (both in the household) gets, every week, an automatic co-presence worth `together_bg` chosen sessions. It enters:
- the connection need as `conn_together × together_bg` (times capacity, as a session does). It **replaces** `conn_cohabit` (0.10) for living with the partner, so it is not counted twice. Living with Friend C keeps `conn_cohabit` unchanged.
- weekly pleasure as `together_event × together_bg` (times the substitution factor below when that flag is on). Today living together adds no pleasure of its own.

It does **not** enter the "together per week" aspiration (that counts chosen sessions, as the persona's target is written), the contact fix's partner amplification, or the world's together satiety (background time is not a session and does not tire the next session). One term, not separate meals/sleep/errands terms: the evidence note found no distinct effects to separate.

Its number, derived (each step labeled):
- 33 waking hours a week shared by couples without children (Flood and Genadek 2016, ATUS; sleep, work and personal care excluded). **Sourced.**
- A chosen session is one evening, about 3 hours (friend-network design, ASSUMED there).
- A background hour is worth q = 0.1 of a chosen hour. **ASSUMED (no source).**
- `together_bg` = 33 × 0.1 / 3 = **1.1** sessions a week. **Swept: 0.33 and 2.2.** At 0.33 the connection gain equals today's `conn_cohabit` exactly (0.30 × 1/3 = 0.10), so the low end differs from A6 only by the pleasure term.

**2. LAT keeps a little background time (`lat_bg_keep`, default 0.2).** Under living apart together, in a week with at least one chosen session, each member gets `lat_bg_keep × together_bg` background time (staying over). In a week with no session, none. **ASSUMED** from "loses most" (the read-back) and "most LATs live close and meet often" (Duncan et al. 2014, citation level). **Swept: 0 and 0.4.**

**3. Travel (`lat_travel`, time units per member per chosen session; default 0).** Under LAT a chosen session costs each member `2 + lat_travel` units instead of 2. 30 minutes each way, hosts taking turns: 0.5 hours a member a session, 1/6 of a 3-hour session, so **0.33** units (sessions cost 2). ASSUMED from "short-distance LAT is under an hour" (Krapf 2018, citation level). **Swept: 0.17 (15 minutes) and 0.67 (an hour).** Travel costs time only; its well-being cost is contested for commuting and unstudied for partner visits, so none is added. The world checks the full cost (both members need `2 + lat_travel` units); the routine sees it only through the units left.

**4. Substitution (`together_subst`, default False).** Each member's pleasure from time together (chosen sessions and background) is scaled by `k = s / s̄`, where `s = togetherness / (togetherness + other_connections)` from the persona's own weights, and `s̄ = 0.50` is the mean of `s` over the 38 personas of H41's sample (0.499, computed from the persona file, not from any outcome). So k runs from 0.40 (a persona whose social weight is mostly on friends) to 1.80; its mean over the persona set is 1. The routine values a session with the same k (it reads the same `together_event` term). Friends already substitute in the connection need (a visit gives 0.35, a session 0.30, and the need is capped), so the connection need is not scaled. ASSUMED form (no study measures felt loss against friend richness; the evidence note's substitution finding is about time and ties). **Swept: off.**

## Design

- **World and agents:** H41's harness under A6 (`hybrid_leaving.py --run`), 11 arms × 120 confirmatory pairings × seed 0 (1,320 runs), plus TT. At most 4 workers, `caffeinate -i`. Rows in runs/time-together/.
- **Unit of resampling:** the pairing (paired bootstrap, 2,000 resamples), as H41.
- **Sweeps (descriptive, one at a time from TT; B and LAT arms only; 120 pairings):** `together_bg` 0.33 and 2.2; `lat_travel` 0.17 and 0.67; `lat_bg_keep` 0 and 0.4; `together_subst` off. Seven configurations.
- **LAT suffering under TT:** the attribution script (scripts/lat_suffering.py) rerun on B, LAT and all aids under TT.
- **Everything new is ASSUMED, sourced or swept and set here**, before any run. No number will be changed after seeing an outcome. If a check shows the code disagrees with this text (a bug), it is fixed with numbers before and after and an amendment; never to move an H41 outcome.

## Known-answer checks (bars are A6's, unchanged)

| ID | What | Passes iff | Where |
|---|---|---|---|
| PIN | Old results reproduce | all four new flags at their defaults: every slow pin test reproduces byte for byte; the fast suite passes | `uv run pytest -m slow`, fast suite |
| KB1 | Background time (unit) | a member living with the partner, `together_bg=b`: the week's connection gain from living together is `conn_together × b × capacity` and pleasure carries `together_event × b` more than with `b=0` (all else equal); at `b=1/3` the connection level equals the flag-off world's exactly | tests/test_time_together.py |
| KB2 | LAT background (unit) | under LAT, a week with no session gives 0 background; a week with one gives `lat_bg_keep × together_bg`; a member living with Friend C keeps `conn_cohabit` | same |
| KT1 | Travel (unit) | under LAT, a session costs each member `2 + lat_travel` units; it is not feasible if either has fewer; in a shared household the cost stays 2 | same |
| KS1 | Substitution (unit) | `k` = s / 0.50 per persona; the mean over the 38 personas is 1 within 0.01; a session's pleasure term is `k × together_event` in the world and in the routine's valuation | same |
| KX2 | Pure exit cost | A5's clauses under TT | `hybrid_leaving.py --kx2 --flags tt` |
| KO1 | The outside forecast is accurate | B arm under TT: mean L − O over lived bar exits within ±0.02, interval inside ±0.04 (A6 failed it: +0.027 [+0.004, +0.048]) | `--analyze` |
| PT-H | Forecasts against held-out futures | A1's sample, TT flags: H1 within ±0.010 (interval inside ±0.015); H2 ≥ 0.80; H3 ≥ 80% | `hybrid_passtest.py --tt` |
| PT-R | The routine at one week | the 40-life value check, TT flags: T1–T4 no more than 0.02 below v2 on the same sample (reference `value-consistency-v2-sat-world`); T5 in 0.8–1.25; T6 holds | `value_consistency.py --hybrid --world --tt --run` |
| KW | The suffering weight | w = 2 declines, w = 0 forms, with TT's flags | tests/test_time_together.py |

## Predictions and expectations (written before any run)

All against A6 on the same 120 pairings (paired), H41's class rule (weeks together and formation margin 0.01; liberty 0.02; pleasure 0.003; interval clear of 0). Weeks together is reported, never judged a good.

| ID | Expected | Kind |
|---|---|---|
| TT1 | In B, households form at least as often at week 0 under TT as under A6 (formed0 TT − A6 ≥ 0) | expectation |
| TT2 | In the LAT arm, fewer pairs choose LAT at week 0 under TT than under A6 (A6: 46 of 120), and LAT weeks fall (A6: 0.148) | expectation |
| TT3 | LAT against B under TT: weeks together −, liberty +, pleasure 0 or −; the verdict is a trade-off or harm, not a win | expectation |
| TT4 | Under TT, the LAT arm's pleasure loss against B (per member, paired) is larger for members with higher s (partner share): a negative slope of (LAT − B) on s. With `together_subst` off the slope is closer to 0 | descriptive |
| TT5 | LAT's non-offsettable suffering against B: no direction predicted; attributed again by need and mode | descriptive |
| TT6 | H41 is still not supported under TT | expectation |

## Verdict rule

Pleasure AND freedom (liberty with powers, and held share) together. A win raises one without lowering the other. One up and one down is a trade-off, never a win. A rise in weeks together is not a gain on either.

**TT is usable as the time-together version** iff PIN, KB1, KB2, KT1, KS1, KX2, PT-H, PT-R and KW pass. KO1 is reported against A6's (it already fails). If a check fails it is reported as failed and not patched.

**Stop rule (ADR 0020), A6 against TT.** Per arm and key, the sign class against B under A6 and under TT. Same class: holds across both. Different: depends on how time together is modeled, named as such, never patched. Sweeps label a TT class "fragile to X" if it changes at either end of X's sweep.

## Can every verdict happen?

- **TT1, TT2 can fail**: if the background pleasure is too small to move a forecast, formation and LAT choice stay put (the 0.33 sweep is close to that); a free check runs B and LAT on 6 pairings with `together_bg` 0 and 3.0 and shows formation and LAT choice can move both ways before the confirmatory run (reported in the results).
- **TT3 trade-off, harm, and win are reachable**: H41's `--reach` synthetic checks already reach every class; under TT the same function is used.
- **TT4**: the slope can be positive, zero or negative; with `together_subst` off and on it is computed the same way.
- **Usable / not usable**: each unit check is written to fail on the flag-off code (KB1, KB2, KT1, KS1 assert the flag-off values first); KX2, KO1, PT-H, PT-R can fail as under A6.
- **The metric sees the mechanism**: background time lands in `Hedonic.tick` (connection) and `close_week` (the together event), so in weekly pleasure, every forecast's weeks and the outside option's futures (where a member alone gets none); travel lands in the world's unit ledger, so in what else a member does that week; substitution lands in the together event in the world and in `agent_values.week_net`.

## Are we measuring what we say?

- **Construct card.** Background time = an automatic weekly amount of partner co-presence from sharing a home, valued at a fixed share of a chosen evening; it does not encode sleep, meals, errands or chores as separate goods, conflict from sharing space, or how much a particular pair likes being in the same room. Chosen time = the existing together action. Travel = time units a LAT session takes beyond itself; it does not encode distance, money or the unpleasantness of travel. Substitution = the share of a persona's social weight on its partner rather than friends sets how much partner time pleases it; it does not encode a person's actual friends or other pleasures, and it changes value, not time.
- **Known-answer cases**: KB1 at `together_bg=1/3` (connection equals the old world exactly); KT1 (cost arithmetic); KS1 (mean factor 1); plus A6's KX2, KO1, PT-H, PT-R, KW.
- **One other way to measure it**: TT4 by the member's own weeks (pleasure in LAT weeks against household weeks within one life) beside the paired arm contrast; LAT's suffering by need and by mode beside the total.
- **Story spot-check**: after the run, read a LAT pair that kept LAT under TT, a pair that switched from LAT (A6) to a household (TT), a high-s and a low-s member in the LAT arm, and one B pair; say whether each matches the measures.

## Findings this could move

- **Row 54 (H41) and row 57 (A6)**: LAT's trade-off (weeks together −0.128, liberty +0.282, pleasure −0.0010 under A6), its non-offsettable suffering (+ under A4, A5, A6), all aids (−0.270, +0.423, −0.0027), and "LAT is the aid people take" (46 of 120 at week 0).
- **H41's "little under-commitment to fix"** (B forms 0.80 at week 0 under A6): background pleasure may raise it.
- **Pressure's weeks-together gain** (version-dependent across four versions) and **P-AUTH** (held on formation under A5, A6): not rerun as such; P-AUTH's B arms run under TT only if time allows (named here so a missing rerun is visible).
- **KO1** (A6: +0.027): outside futures have no partner and so no background time; if lived households now gain more, the forecast's error may move.
- **Limit 11** (moving in looks costlier than it is): background pleasure is a gain on the other side of that ledger.
- **The many-agent spec's freeze**: this is a pending item, not a decision (the author has not decided the freeze).

## Not testable by design

The unit checks KB1, KB2, KT1, KS1 (deterministic arithmetic) are passes or failures, not intervals.

## Limits stated now

One persona sample (38 personas, 120 pairings, one seed); scripted agents; every new number ASSUMED except the 33 hours; q (the value of a background hour) is the most influential and has no source; the model's time units are not hours (work 4 units ≈ 34–40 hours, a visit 2 units ≈ 3 hours), so travel is set relative to a session; no well-being cost of travel; background time is the same for every pair.

## Amendments

(none yet)
