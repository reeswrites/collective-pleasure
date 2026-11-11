# Observer schema (household world)

Written 2026-11-11. The observer layer is the build list in docs/notes/instrumentation.md, made. Code: `src/mar/observe.py`. Tests: `tests/test_observer.py`, `tests/test_atlas_observer.py`. Demo: `scripts/observer_demo.py`.

Schema version: `mar.observer/1` (the `schema` field of every file's `run` row and of every manifest).

## The switch

Off by default. Two ways to turn it on:

- Explicit: build the harness inside `observe.collecting()`, then `Observer(world, cfg, run_key=..., meta=..., harness=lived)`. `harness` drains the week-0 formation decision, which happens before an observer can be attached. Call `ob.finish()` after the last week.
- Blanket: every `WeeklyWorld` built inside `with observe.use_observer(cfg):` carries an observer, rollout worlds included. The tests use this to check the strictest case.

`ObsConfig` fields: `replay_rate` (share of weeks sampled for a swap replay, 0 = none), `replay_window` (weeks a replay runs, 13), `replay_leaves` (every executed leave gets a stay replay), `replay_pressure` (with the H38 pairing switch on, a sampled week also gets a pressure-off replay), `replay_seed`, `max_replays` (per run, 60), and `decisions`, `state`, `flows` to switch the biggest tables off.

## What the guarantee is, and how it is checked

With the observer off, every run is bit-identical to before. With it on, every run is still bit-identical: the observer reads, it makes no draw from any stream the world uses, and it writes nothing the world reads.

- `tests/data/observer_off_fingerprints.json` was pinned before any of this code existed: H38 L0 and L4 (two pairings, 156 weeks, with retries and bar readings), exit fallbacks F0, F4 and F5 with items (two validation runs each), the v2 retest BASE-F and V23-F (with week-0 negotiation, retries and reviews), and household evolution (`score_runs` on two seeds, two validation runs each). A fingerprint hashes the outcomes, the trace, the final state, the meta, the exit log and the pot (or the summary dict the family's harness returns).
- `test_off_reproduces_pinned_runs`: the families with no observer match the pins.
- `test_on_reproduces_pinned_runs`: the same families inside `use_observer(ObsConfig(replay_rate=0.25, replay_window=4))` match the pins. Every world built carries an observer, and every observer runs swap, stay and pressure-off replays.
- `test_explicit_attach_changes_no_outcome`: an explicitly attached observer with replays gives the same run digest as no observer.
- The existing pins (`tests/data/h38_pairing_off_fingerprints.json`, `levers_off_fingerprints.json`) still pass.

How the hooks keep it: the world calls the observer only through `if ob is not None` branches. Parts that the model sums into one number (D2, D5, S2) are computed beside the model's own arithmetic from the same pure functions, never in place of it. Utility noise is recorded by drawing it in the same order the old dict comprehension did. `Hedonic` copies start with no recorded parts. A deep copy of a world (rollouts, replays) drops its observer: `Observer.__deepcopy__` returns None, so copies never record and never write into the live run's rows.

## Files

One gzipped JSONL file per run: `runs/<experiment>/obs/<run_key>.jsonl.gz`. One row per line; every row has `t`, its table. `runs/<experiment>/obs/manifest.json` holds the schema version, the experiment name, the observer config, a note, and per run the file, its size in bytes and its row counts by table. Write with `observe.write_run(ob, exp_dir)` and `observe.write_manifest(exp_dir, entries, experiment, cfg)`; read with `observe.read(path)` -> `{table: [rows]}`.

Conventions: `w` is the week (0-based; -1 is the state at attach). `r` is a role, "A" or "B". Floats are rounded to 6 places. Money moves are in the world's money units. Roles in rows are roles, never persona ids, except in negotiation rows (the negotiation code works by persona id).

## Tables

### run (one row)
`schema`, `run_key`, `pair_key` (persona A id | persona B id | seed: the same across arms, so paired runs line up, C3), `seed`, `weeks`, `meta` (caller's), `personas` (per role: id, style, weights, need salience `sal`, aspiration `targets` and weights `asp_w`, `prosocial`, agent class), `cards`, `fixes`, `levers` (repr or null), `mech`, `pot`, `items`, `cfg`, `bal0` (balances at attach: A, B, pot, bills, escrow).

### week (one row a week, at the end of the week)
`pool`, `both_in`, `need_met`, `settle` (bill settlement week), `pre_events` (harness events between the previous week and this one: formed, terms), `events` (the world's choice and ladder events this week), `exits` (exit log entries), `shocks`, `busy`, `c_blocked`.

### decision (D1, D2, D4, D7; one row per step_agent call)
`w`, `r`, `k` (the call: pass 0, 1 or 2), `in`, `partner_accepts`, `chosen` (index into `cands`, or null when nothing ran), `runner` (index of the runner-up: the next candidate the world would have executed had the chosen one been absent), `margin` (chosen utility minus the runner-up's), `sig` (the gate state as atlas signature bits), `cands`.

Each candidate: `a`, `u` (after the soft-sanction adjustment, as the world ranked it), `dec` (ok, soft, hard, breach), `st` (chosen; below the 0.003 threshold; infeasible; blocked; skipped; open = viable but ranked after the chosen one), `tr` (1 if it has a row in `run.trace`), `kind`, `take`, `why`, `motive` when set, `reasons` (card ids, or "sanction ...", "veto: ...", "commitment: ..."), and `parts`, which sum to `u`:

| part | meaning |
|---|---|
| money | the money need (income, or the cost of a spend) |
| savings | the savings aspiration |
| rest | the rest need (rest, or work fatigue) |
| connection | the connection need (one pool: friends, partner and living together all fill it) |
| friends | the friends-per-week aspiration |
| together | the together-per-week aspiration |
| partner | the prosocial term for the partner's connection deficit (the partner's pleasure, as the agent weighs it) |
| autonomy | the autonomy aspiration and the spend_self constant |
| bills, security, household | spend_shared: the bill gap, the security need under the pot threat, the prosocial share |
| pressure_withdraw | H38 dyadic withdrawal (see_friend scaled by 1 - d) |
| lever_spacing | an adaptive agent's satiety scaling (pleasure levers) |
| noise | the seeded noise factor (a draw already made) |
| sanction | minus the agent's estimate of a soft rule's sanction |
| policy | a candidate that is a fixed rule of thumb (leave 0.9, refuse 0.12, request 0.06, give, press), or a pressing agent's rescaling |

`leave_ctx` (D4), when the member is distressed, past the bar, or offered a leave: `low_weeks`, `N`, `trust`, the three distress conditions as booleans (`low`: 4+ low weeks; `n_high`: N >= 0.2; `trust_low`: trust < leave_below), `bar`, `open` (the v2.3 ladder lets leave on the menu), `takes`, `cond_run` (streaks of the trapped, denied and diminished conditions: which one built N), `ladder` stage.

`gift_ctx` (D7), where seed v2 mechanics are on and the partner is in: `prosocial`, `partner_money`, `own_money`, `fires`.

`consent` (D3, the refuse decision): the member's answer to what stands on them, as in the consent table.

### consent (D3; one row per request answered)
`asker`, `receiver`, `kind`, `style`, `autonomy`, `would` (the style's answer before trust), `coin` (the avoidant style's draw), `trust`, `draw` (the trust draw, made only when trust < 0.5 and the style would say yes), `answer`, `final` (the consent flag after a commitment), `bound` (a request commitment overrode the answer), `motive`.

### reading (D5; formation, retry, 13-week reading, review)
`kind` (formation0, retry, reading, review), `w`, and `m` per role: `W` (household value: rollout mean of pleasure - s_off - s_non, or of pleasure under `decide_on="pleasure"`), `O` (outside value), `margin` = W - O, `O_alone_friend`, `mode`, and `W_parts`, `O_parts`: the two rollouts' means by group (below). `W` = sum(`W_parts`); `O` = sum(`O_parts`) minus `exit_anticipation` (H38 exit stigma, subtracted outside the rollout). Kind-specific fields: `formed`, `modes`, `trust_pen` (the trust penalty a reading subtracts from the household side), `bar_out`, `bar_runs`, `status`, `changed`, `bundle`. Parts are null where the value came from a cache filled before recording began.

### negotiation (D6; one row per round)
`w`, `kind`, `k`, `proposer`, `bundle`, `accepted_by`, `rejected_by`, `outcome`, and `members` per persona id: `U` (the offer's value), `bar` (max of the outside option and the status quo), `theta` (acceptance threshold; null for the proposer), `terms` (per-term value difference against the reference terms); `gap_term`: the term on which the two members' differences are furthest apart.

### state (S1, S2; one row per member per week)
`in`, `money`, `put`, `money_in`, `B`, `N`, `glow`, `cap`, `levels` (rest, connection, money, security), `cond_run`, `low`, `trust`, `pending`, `consent`, `bound`, `vetoes`, `sanctions`, `jobless`, `ill`, `bar_out`, `ladder`, `pl`, `s_off`, `s_non`, `wk` (the week's scratch counters: works, rests, friends, friend_initiated, together, contrib, pressed, took, spent_self, sanctioned, checkin), `g` (the week's groups) and `parts` (the raw parts: `p_need`, `p_asp`, `s_need`, `s_asp`, `pre_onset`, `s_non`, `together_event`, `glow`, `extra`, `friction`, clip terms, and `x`, the world's split of extra pleasure and friction).

Groups (`observe.GROUPS`), each pleasure minus suffering from that source, summing to pleasure - s_off - s_non: money (need, savings, bought pleasure), security, rest, connection (the need), partner (together aspiration, together events, fix-1 partner amplification), friends (aspiration, fix-1 friend amplification), items, pressure (H38 reward minus stigma minus exit stigma), intrinsic (H38 values-pairing), autonomy, levers, friction (warn, pressed, contest, check-ins, scorekeeping, missing pain), conditions (trapped, denied, diminished, before and after onset), other (glow, fix-1 release), clip (what the [0, 1] clips took off).

### friend (S3)
Every friend invitation: `r`, `outcome` (met, blocked, declined), `d` (the withdrawal that declined it), `dec`, `reasons`.

### trust (S4)
Every trust move: `r` (whose trust), `why` (kept, honored, breach, word, word_revoked, role_lapse), `d`, `v`.

### word (S5)
`speaker`, `receiver`, `gain`, `event` (said, revoked), `said` (the week of a revoked word).

### flow (F1)
`src`, `dst` (A, B, pot, bills, escrow, outside), `amt`, `cause`, `actor`. Causes: the action (work, spend_shared, spend_self, give_partner, give_friend, take_shared, leave), living_cost, safety_net, bills_from_pot, move_cost, breach_fine, fine_role, contest, formation. A flow computed from a balance change pairs sources with sinks greedily. Balance at attach plus flows equals the balance at the end, for each member and the pot (`test_flows_balance_the_money`).

### together (F2)
`initiator` (A, B, or ritual/adhoc for lever sessions), `partner`, `accepted`. A together session the partner would not accept is never on the menu; that case is the decision row's `partner_accepts: false`.

### item (F3)
Custody at attach and at every change: `holders`, `prev`, `cause`.

### rule (R1)
`r`, `a`, `src` (card, sanction, veto, commitment), `card`, `verdict` (hard, soft, breach; or permit: the list of cards checked for an executed action), `deontic`, `acted`, `sig`.

### sanction (R2), commit (R3), veto (R4)
Sanction `start` and `end` with `kind`, `card`, `until`. Commitments `made`, `renewed`, `ended`, `changed`, `breach_counted`, `dropped`, `breach` (with the action), each with `when` (week, or harness for a change made between weeks). Vetoes laid (`by`, `on`, `kind`, `until`) and ended. The actions a veto or commitment stopped are rule rows.

### replay (C1, C3)
From a deep copy of the world taken at the start of the week (without its run log and without any harness hook), with the agents' random streams copied as they stood:

- `swap`: one decision of a sampled week (sampler: its own `random.Random` keyed by `replay_seed`, `pair_key` and the week) replayed with the runner-up put first. `info` holds the chosen action, the alternative and the margin.
- `stay`: every executed leave, replayed with leave removed from that member's menu for the window ("if they had stayed").
- `pressure_off`: a sampled week replayed with the H38 pressure parts off (intrinsic kept); `changed` per role says whether that week's executed actions differ.

Each has `fact` and `alt` (per role: mean net and pleasure over the window, weeks in, money, B, N, trust; both-in weeks, the pot, exits), `diff` (alt minus fact), `faithful` (the factual copy's actions in week `w` equal the live run's: the copy reproduces the run), and `applied` (the swap found its candidate).

### stay, end
`stay`: an H38 stay reading (pairing.stay_reading) when the harness passes it. `end`: weeks, exits, pot, trust, replay count.

## Cost

Measured on the demo's 40 runs (H38 L0 and L4, exit fallbacks F4 with items; replay rate 0.05, window 13, every leave replayed): 108 kB a run on disk (gzipped JSONL; 101 kB for exit fallbacks, 113 to 117 kB for H38), about 2,850 rows a run (936 decisions, 685 flows, 473 rule rows, 312 state rows, 156 week rows, the rest small). Wall time: an H38 run takes 1.9 to 2.3 s without the observer and 2.6 to 3.0 s with it; an exit-fallbacks run 0.1 to 0.2 s without and 0.3 s with.

## Not recorded, and why

- S6 typed reports, S7 scorekeeping, S8 guilt: not modeled for scripted agents (instrumentation.md says why). The LLM harnesses (negotiation_llm, ladder_live) and the monthly world are not hooked.
- C2, the smallest part whose removal flips a verdict, by replay: the parts are sums the model computes, not switches it has, so there is no way to zero one part in a rollout without changing the model. The demo uses the additive version instead (removing a part's difference from the margin), which ignores how parts interact through the rollout.
- C1 is replayed for the H38 pairing pressure only. Switching off a bound request, a ladder step or a sanction in a copy is possible but not built; the same-draws property holds for the agents' streams as long as the switch does not change how many candidates draw noise, which is true of the pairing parts.
- Replays step the world only. The harness's 13-week readings, retries, reviews and stay readings do not run inside a replay window, so a 13-week replay that crosses a reading week leaves the bar and the terms where they were.
- The connection need is one pool and is not split by source (D2, S2). Where fix 1 is on, its amplification is split into friend and partner shares.
- Reading parts are missing (null) for values served from a cache filled before recording began. The demo clears the caches per run, so none are missing there.
- R1 permit rows cover executed actions only. Actions nobody proposed never touch the gate, and scanning the full menu every week would add a few hundred rows a run for little.
- The atlas port reads each week at its end; the hook read it at the next week's start. Pool, money, put and trust can differ on weeks whose next start moved them (a harness formation, the slow trust recovery), and in the week before a harness formation the hook already reads both members in.

## Demo (EXPLORATORY)

`scripts/observer_demo.py --run` then `--analyze`. 40 runs: H38 arms L0 and L4 on the first 10 confirmatory pairings, seed 0, with the stay readings; exit fallbacks arm F4 with items (cell V2-split-loves, the author's seed v2.2), validation runs 0 to 19. No prereg, no prediction tested, small samples: these are readings of what the new tables make possible, not results. Wording rule (ADR 0010): agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

**1. What tipped formation and leave decisions.** For each member at each formation and retry, the margin W - O is split by group (household rollout minus outside rollout). A part "tipped" the member's verdict when removing that part's difference alone flips the sign of the margin; of those, the largest is counted. "none-alone" means no single part flips it.

| decision | arm | members | tipping part |
|---|---|---|---|
| wants to form | H38 L0 | 25 | partner 18, items 6, none alone 1 |
| wants to form | H38 L4 | 21 | partner 10, pressure 7, none alone 4 |
| does not want to form | H38 L0 | 15 | none alone 8, money 5, friends 2 |
| outside beat staying at a 13-week reading | H38 L0 | 20 | money 9, friends 6, clip 3, none alone 2 |
| outside beat staying at a 13-week reading | H38 L4 | 15 | none alone 9, money 5, connection 1 |

Time with the partner is what tips most members into a household. At L4 the pairing pressure alone tips 7 of 21. When the outside option beats staying at L0 it is mostly money or friends; at L4 more often no single part does it. Leaves: every exit-fallbacks leave (20) and 11 of the 18 H38 leaves were distress leaves driven by the non-offsettable load (N >= 0.2), alone or with a low streak; the other 7 were bar leaves. All 31 N-driven leaves had a `denied` streak (a need below 0.15 for 4+ weeks) and no trapped or diminished streak. Which need differs by family: money and security in exit fallbacks, rest at H38 L4. The atlas could only say "distress".

**2. Do lopsided stretches even out, in 13-week blocks.** Each member's net money into the household per block (gifts to the partner, bill and pot contributions, minus draws from the pot), and the together sessions each started, weeks both in. A block is lopsided at |imbalance| >= 0.30 (the atlas's threshold).

| family | flow | lopsided blocks | reversed within 2 blocks | evened within 2 blocks | stayed lopsided the same way | no later block |
|---|---|---|---|---|---|---|
| exit fallbacks F4 | money | 110 | 16 | 11 | 66 | 17 |
| H38 L0 | money | 57 | 9 | 2 | 39 | 7 |
| H38 L4 | money | 54 | 7 | 5 | 37 | 5 |
| exit fallbacks F4 | time | 109 | 6 | 6 | 77 | 20 |
| H38 L0 | time | 75 | 1 | 3 | 63 | 8 |
| H38 L4 | time | 81 | 6 | 5 | 61 | 9 |

At 13-week resolution most lopsided stretches do not even out within half a year: a fifth to a quarter of the lopsided money blocks reverse or even out within two blocks (27 of 110, 11 of 57, 12 of 54), and a tenth or less of the time blocks (12 of 109, 4 of 75, 11 of 81). Read the time row with care: the world steps A before B in every pass, so A starts most together sessions whenever both would; who "initiated" is partly turn order, not motive. That is a model fact the old trace could not show, since it logged together only for the actor.

**3. If they had stayed.** At each leave, a copy of the world from the start of that week is replayed for 13 weeks with leave taken off the leaver's menu. Difference in mean weekly net (pleasure - s_off - s_non), stayed minus left:

| family | leave | n | leaver, mean (median) | better for the leaver | partner, mean | nobody left in the window |
|---|---|---|---|---|---|---|
| exit fallbacks F4 | distress | 20 | +0.001 (+0.036) | 12 of 20 | -0.051 | 5 of 20 |
| H38 L0 | bar | 4 | +0.058 (+0.090) | 3 of 4 | +0.268 | 4 of 4 |
| H38 L0 | distress | 3 | +0.003 (+0.031) | 2 of 3 | +0.022 | 3 of 3 |
| H38 L4 | bar | 3 | -0.141 (-0.254) | 1 of 3 | +0.070 | 1 of 3 |
| H38 L4 | distress | 8 | +0.321 (+0.142) | 6 of 8 | +0.245 | 5 of 8 |

Every factual replay reproduced its live run. In most cells the 13 weeks after a leave would have gone a little better for the leaver had they stayed, and often for the partner too; the H38 L4 bar leaves are the exception. The replay window does not include the harness's readings, and n is small; this shows the measurement works, not what leaving is worth. One pattern the replays surfaced (a stay replay was missing until the observer also copied weeks where a member out could return): in two exit-fallbacks runs and one H38 L4 run a member left, then every 8 or 9 weeks returned and left again within the same week, 10 such re-leaves in all.
