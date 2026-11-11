# Household replay viewer

Written 2026-11-11, for the author's question "Is there any way to visualize a running simulation or anything like that?". Code: `src/mar/watch.py` (data) and `src/mar/watch_page.html` (the page). Tests: `tests/test_watch.py`. Sample page: `docs/viewer/household-replay.html`.

Wording rule (ADR 0010): agents feel nothing. "Lonely", "content", "distress" and "mood" are plain-word readings of modeled states, and the page says so.

## Use

```
uv run mar watch h38 "L0|g-10000|g-10011|0"                                  one run
uv run mar watch h38 "L0|g-10011|g-11011|0" --compare "L4|g-10011|g-11011|0"  the same pairing under two arms, one shared slider
uv run mar watch ef "F0|author_seed_v23_bindable|21"                         an exit-fallbacks household (the atlas key, with its
                                                                             trailing |0, works too)
uv run mar watch --sample                                                    rebuild docs/viewer/household-replay.html
```

Run keys are the observer's (runs/observer-demo) and, apart from the exit-fallbacks trailing seed, the pattern atlas's:

| family | key | what it replays |
|---|---|---|
| h38 | `<arm>\|<persona A>\|<persona B>\|<seed>` | H38 pairing norms (any arm in `scripts/h38_pairing_run.py`: L0 to L8, the parts-alone arms), with the stay readings every 13 weeks |
| ef | `<arm>\|<rule set>\|<validation run>` | exit fallbacks slice 2, items on, cell V2-split-loves (arms F0 to F5) |

The page reads `runs/watch/obs/<key>.jsonl.gz`, else `runs/observer-demo/obs/<key>.jsonl.gz`. If neither exists it re-runs the household with the observer on (`ObsConfig(replay_rate=0.05, replay_window=13, replay_leaves=True, replay_pressure=True)`, the demo's) and writes the file to `runs/watch/obs/`. A re-run is free (scripted agents) and gives the same outcomes as the original run (the observer guarantee, docs/notes/observer-schema.md). An H38 run takes 1 to 3 s, an exit-fallbacks run under 1 s. Pages for one run go to `runs/watch/pages/` unless `--out` says otherwise.

## What the page shows

- **Controls.** A week slider (0 to 155), play and pause, a speed control (1 to 20 weeks a second). Arrow keys step a week.
- **The two of them.** Per member: a one-line mood, five bars (below), money, friend visits this week against the member's own friends-per-week target, out of work or ill. The two panels sit side by side and stack on narrow screens.
- **The household.** Living together, apart, or only one at home; the shared pot; time together this week; who holds the home, the pet and the collection; what is being made (H39 makers; off in every family the viewer replays today).
- **Over time.** Pleasure per member, with the weeks together shaded; and who put more money into the household over the last 13 weeks (bills, pot, gifts to the partner, minus draws from the pot), from -1 (B put in everything) to 1 (A did). A line marks the current week.
- **Big decisions.** One card per formation (week 0 and each retry), per 13-week stay reading, and per executed leave, shown once the slider reaches its week. Formation and reading cards give each member's two values (living together vs apart, or staying vs leaving), the margin, the part that tipped the verdict, the four biggest parts with the side each pushes toward, and, at readings, the stay test (worth, leave, or held: would leave without the pairing pressure). Leave cards give why (from the observer's `leave_ctx`), the options on the menu with their scores, the margin over the next best option, the amount carried out of the pot, and the "if they had stayed" line from the stay replay.
- **What happened.** The event feed up to the current week, newest first; the current week is highlighted. Routine events (bills, safety net, friend invitations turned down under pairing pressure) are hidden unless "show routine events" is ticked.
- **Compare.** An entry with two runs shows them side by side (stacked below 900 px) under one slider.

## Mood mapping

Every bar is a state the model already keeps; the viewer adds no measure. From the observer's `state` row for the member that week (S1, S2) and the persona in the `run` row.

| bar | value (0 to 1) | words |
|---|---|---|
| Content | `pl`, the week's pleasure | content at 0.9 or more; okay at 0.75 or more; unhappy below |
| Lonely | 1 - `levels.connection` (the connection need is one pool: friends, partner and living together all fill it) | lonely at 0.5 or more; a bit lonely at 0.25 or more; not lonely below. Shown beside it: friend visits this week (`wk.friends`) against the persona's `targets.friends_per_week` |
| Money worry | 1 - mean(`levels.money`, `levels.security`) | stressed about money at 0.5 or more; a little worried at 0.25 or more; not worried below |
| Trust in the other | `trust` | trusts at 0.6 or more; unsure of at 0.4 or more; does not trust below (the leave-below threshold is lower still) |
| Distress | `N` / 0.4, capped at 1 (`N` is the non-offsettable load; a member at `N` >= 0.2 is in distress and may leave) | in distress at `N` >= 0.2; some lasting hurt at `N` > 0; no lasting hurt. Then the denied-need streak (`cond_run.denied`, weeks a need has been below 0.15) with the needs below 0.15 now, and the low streak (`low`) at 2 weeks or more |
| Wanting trap | max(tolerance, sensitization), when a state row carries them | in a wanting trap at 0.5 or more; wanting more than liking at 0.25 or more. **Not shown today**: the observer does not record makers or wanting state (below) |

Bar colours: for lonely, money worry and distress, green below 0.25, amber to 0.5, red above; for content and trust, green at 0.6 or more (content and trust bars use the same cut), amber to 0.4, red below.

The household's names are neutral made-up names, fixed by persona id, so the same pairing has the same names under every arm. The persona ids are in the page data.

## Event wording

| source (observer table) | wording |
|---|---|
| reading `formation0` / harness `formed` | "Kit and Hollis moved in together"; "They chose to live apart; Hollis said no" |
| reading `retry`, not formed | "They talked about moving in; Kit said not yet" |
| week `exits` (+ `events` leave_bar, or the leave decision's `leave_ctx`, + the `leave` flow) | "Ellis moved out (the outside option looked better), taking 24 from the shared pot"; "Drew moved out (distress: rest unmet for 4 weeks), ..." |
| decision, `return` chosen | "Kit moved back in" |
| consent | "Kit asked Hollis for time together; Hollis said no"; "... said yes (an earlier agreement bound them)" |
| flow `give_partner`, `give_friend`, `take_shared` | "Ash gave Ellis 3", "Ash gave a friend 2", "Kit took 5 from the shared pot" |
| flow `spend_shared` (routine) | "Ash covered the bill (3)" when one member paid that week; "Both paid toward the bills (...)" otherwise; "The bills came out of the shared pot" |
| week `shocks` | "Kit lost their job (for 8 weeks)", "Hollis fell ill", "Kit made a new friend" |
| item | "The home stayed with Kit; the pet stayed with Hollis" |
| stay | "Check-in: Kit wants to stay; Hollis would rather leave" (or "would leave without the pairing pressure", the held verdict) |
| trust, veto, sanction, commit, word, friend `blocked` | trust falls after a breach, vetoes, rule penalties, promises made and broken, words taken back, a rule keeping a member from a friend |

## What tipped a verdict

At a formation or reading the observer splits each member's household value W and outside value O into the same groups (`W_parts`, `O_parts`). The margin W - O is the sum of the per-group differences (plus the H38 exit stigma, which is subtracted from O outside the rollout). A part **tipped** the verdict when removing its difference alone flips the sign of the margin; the largest such part is named. When no single part flips it, the card says "no single part; several together". This is the additive reading the observer demo uses: it ignores how parts interact through the rollout (observer-schema.md, "Not recorded").

A leave is not a weighed choice in the same way. A leave on the bar follows two 13-week readings in a row where the outside option won; a distress leave is a fixed rule of thumb (leave scores 0.9 whenever the member is in distress). The card says which, and the scores of the options on the menu show how far ahead leaving was.

## Observer data the viewer does not use

- **Makers and the wanting trap.** The observer records neither H39 maker state (projects, what is being made, credit) nor liking-wanting tolerance and sensitization, and the families the viewer replays run with makers off. The page hooks are there (a `makers` field in the run row, a `want` dict with `tol` and `sens` in a state row) and show nothing until the observer records them. `cond_run.trapped` is the "trapped in the household" condition, not a wanting trap, and is not shown.
- **Swap and pressure-off replays.** Only stay replays feed a card ("if they had stayed"). Swap replays (one ordinary weekly choice replayed with the runner-up) and pressure-off replays are counted in the page data but not shown.
- **Per-candidate parts of ordinary weekly choices** (work, rest, friends, together), rule firings, permits and the gate signature: summarised in the event feed only where something happened (a refusal, a block, a breach).
- **Negotiation rows** (v2 retest, F5 prenups): not shown. The v2 retest family is not replayable yet (`mar watch` knows h38 and ef only).
- **Part groups inside a week** (`g`, `parts`): the mood uses the need levels and pleasure, not the per-group split.
