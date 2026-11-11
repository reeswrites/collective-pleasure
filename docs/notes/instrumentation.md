# Instrumentation gap list (household world)

Written 2026-11-11 while building the pattern atlas (docs/results/pattern-atlas.md). Every item below is something the atlas wanted to measure and could not, or could only guess at. It is the build list for an opt-in observer layer on the household world. That layer must be bit-identical when off: no extra random draws, no change to iteration order, nothing written to world state that the world reads.

What the atlas could already read, with no change to the world: `run.trace` (one row per proposal the world considered: role, action, kind, take, allowed or blocked, soft, breach, the gate's reasons, the gate state, the chosen utility `u`), `run.outcomes` (weekly hedonic rows; with fixes on, the H38 pressure terms), `world.events` (check-ins, review requests, new terms, leaves with a reason, lapses), `world.exit_log`, the pot and each member's money, `put` and `money_in`, trust, pending requests and the consent flag, bound requests, and the harness's own decision logs (`BaselineLived.week0`, `.retries`, `.log`; `world.bar_log`). The atlas recorder (`src/mar/atlas.Recorder`) reads these through `WeeklyWorld.hook` at the start of each week and writes one compact row per week.

Each entry: what the measurement is, why it is missing, and what the world would need to record. "Why" uses four reasons: **not recorded** (the value exists for a moment and is thrown away), **only aggregated** (a sum or mean survives, the parts do not), **needs a counterfactual replay** (the value is "what would have happened otherwise"), **not modeled** (nothing in the world computes it).

## 1. Decision points

| # | Measurement | Why missing | What to record |
|---|---|---|---|
| D1 | The deciding margin of each weekly action choice: the chosen action's utility against the runner-up | Not recorded. `PersonaAgent.propose` returns the ranked list; `step_agent` keeps only the executed row (and blocked rows) | Per `step_agent` call: the full scored candidate list after the soft-sanction adjustment (`scored`), the chosen index, and the reason each higher-ranked candidate was skipped (hard block, infeasible, below threshold) |
| D2 | The parts of each action's utility (money, rest, connection via friends, connection via together, security, savings aspiration, autonomy, prosociality, the H38 withdrawal factor, the lever spacing factor, the noise draw) | Only aggregated. `utilities()` sums the parts into one number per action and multiplies by noise | `utilities()` returns a dict of named parts per action alongside the total. The observer copies it; the agent keeps using the total. The noise factor is recorded as its own part (it is a draw already made, so recording it adds no draw) |
| D3 | Why a request was accepted or refused: the style rule, the autonomy threshold, the avoidant coin flip, the trust scaling of a yes | Not recorded. `consents()` returns a bool; the coin flip and the trust draw are consumed silently | Per `consents()` call: style, autonomy, the would-be answer before trust (`_consents`), trust and the trust draw if made, final answer, and whether a commitment (`req_commit`) overrode it |
| D4 | Why a leave fired: low-week streak, the N >= 0.2 non-offsettable threshold, trust below `leave_below`, the bar, the unhappy ladder stage | Partly recorded. With fixes on, the event says "distress" or "bar"; which distress condition fired is not kept. Without fixes nothing is kept | In `propose`, when `distress` is true: the three conditions as separate booleans with their values (`low_weeks`, `h.N`, `trust`), and the ladder stage. The leave `take` options offered and the one chosen |
| D5 | The parts of a stay, form or review decision: household value against outside value, split into money, friend contact, items, pressure (stigma, reward, exit stigma), partner's pleasure, intrinsic pairing | Only aggregated. `forward_values` and `outside_value` return one wellbeing number each. The H38 stay reading separates only the pressure part (with and without pressure) | `NG.wellbeing` returns the per-term sums over the rollout (pleasure from each source, s_off, s_non, the pressure terms, item pleasure). `outside_value` returns the same split for the outside rollout. The observer stores both splits at each reading, retry and review |
| D6 | Negotiation and renegotiation: which terms were on the table, each member's value for each, which term decided an agreement or a stalemate | Not recorded at week level. `negotiate_v2` returns the final bundle and status | Per negotiation round: the offer, each member's value and threshold, accept or reject, and the term with the largest value gap. Stalemate as its own outcome |
| D7 | Gift decisions: why a prosocial give fired or did not (partner money below 4, own money at least 8, prosociality) | Not recorded (the condition is checked inline) | The three inputs and the result per week per member where `mech` is on |

## 2. Weekly internal state

| # | Measurement | Why missing | What to record |
|---|---|---|---|
| S1 | Need levels and salience per clock (rest, connection, money, security), capacity, the hedonic B and N accumulators | Not recorded. `hed[r].level`, `.B`, `.N` change every week; the outcome row keeps pleasure, s_off and s_non only | The full `HedonicState` snapshot per member per week (a dozen floats) |
| S2 | Weekly pleasure split by source: together, friends, rest, money, items, the pressure terms, levers, fixes | Only aggregated. `close_week` adds `extra_pleasure` and friction into one pleasure number; only the H38 terms and lever terms are kept when those switches are on | `close_week` returns the additive parts it already computes (aspiration satisfaction per aspiration, extra pleasure per source, friction per source). Item pleasure (`_ITEMS.weekly_pleasure`) is computed and then discarded |
| S3 | Friend contact turned down under H38 withdrawal, week by week | Only aggregated (`pstats["friend_declined"]` is a run total) | The week and member of each declined friend attempt |
| S4 | Trust changes with their cause | Partly recorded: `trust_log` keeps non-"kept" moves; the slow "kept" recoveries are not logged | Every trust move with its cause, or the weekly sum per cause |
| S5 | Words given and taken back (say vs do for scripted agents) | Only aggregated: `fstats["words"]` and `["words_revoked"]` are run totals; `world.words` keeps live words only and drops revoked ones | Each word (week, speaker, kind: check-in answer or agreed terms) and, if revoked, the week and the lapse or breach that revoked it |
| S6 | Typed reports against actions (ADR 0007 item 12) | Not modeled for scripted agents. Typed reports exist only for LLM agents, and no LLM household run is in the atlas sample | A scripted "report" channel is a design question, not instrumentation. For LLM runs: store the typed report next to the week's actions so the atlas can compute the gap directly |
| S7 | Scorekeeping: whether a member is tracking who gave what | Not modeled. Nothing in the agent reads a ledger of past gives; trust is the only running account, and it moves on breaches and honored requests, not on gives | Not an instrumentation gap: the world would need a scorekeeping agent before there is anything to observe. Logged here because the author's line ("reliance is fine; guilt and scorekeeping are not") cannot be checked without it |
| S8 | Guilt: a give or yes made to avoid feeling bad | Not modeled | As S7. The atlas classes "yes" by style (accommodating, avoidant) as conflict avoidance; that is a reading of the style, not of a modeled state |

## 3. Flows

| # | Measurement | Why missing | What to record |
|---|---|---|---|
| F1 | Every money movement with its source and sink (income, living cost, bills, pot surplus, safety-net draw from the pot, gifts, take_shared, fines, exit carry-out, item settlement) | Partly recorded. Executed actions are in the trace; the safety-net draw, bill payment from the pot, fines and item settlement are applied inline and only their effect on balances survives | A flow ledger: (week, from, to, amount, cause). The safety net and the bills-from-pot step are the two that most change who carried the household |
| F2 | Time flows: together sessions initiated by whom, accepted by whom | Partly recorded. `together` appears in the trace for the initiator; the partner's unit cost is applied silently | The initiator, the partner, and whether the partner accepted (`partner_accepts`) |
| F3 | Item custody over time (home, pet, collection): who holds what each week, contests | Only at the end (`holders`) and in `item_log` for exits | Holder per item per week, and each change with cause |

## 4. Rule firings

| # | Measurement | Why missing | What to record |
|---|---|---|---|
| R1 | Each card's firings: which card blocked, sanctioned, or permitted an action, at which state | Partly recorded. The trace keeps the gate's `reasons` strings for considered proposals; matching card ids in strings is fragile, and actions never proposed never touch the gate | `decide()` returns structured firings: card id, deontic, verdict (hard, soft, breach, permit), the state signature. The observer keeps them per week |
| R2 | Sanctions applied and served (warn, suspend, cap_halve), with the card | Partly recorded: the count per week (`sanctioned`); the kind, card and duration are dropped when they expire | Each sanction at start and end: member, kind, card, weeks |
| R3 | Commitments made, kept, breached, renewed | Partly recorded (`commit_report` at the end) | Each commitment's life: made (week, by, to, kind), each week it bound an action, breach week, renewal |
| R4 | Vetoes laid and the actions they stopped | Partly recorded (hard blocks carry "veto: kind" in reasons) | Each veto: who, on whom, kind, until; and each action it stopped |

## 5. Counterfactual replays

| # | Measurement | Why missing | What to record |
|---|---|---|---|
| C1 | Was a give, a yes or a stay pressured: would it have happened without the pressure (H38 terms, a bound request, a ladder step, a sanction)? | Needs a counterfactual replay. The H38 stay reading does this for staying only, every 13 weeks, with 26-week rollouts | Sampled replays at decision points: copy the world (with the hook detached, as `pairing._forward` does), switch one lever off, replay the same week's decision with the same draws, and record whether the choice changes. Needs a draw-preserving replay: the agent's RNG state saved before the choice |
| C2 | What tipped a formation, stay or leave decision: the smallest part whose removal flips it | Needs a counterfactual replay per part (D5 gives the parts; the flip needs replays because parts interact through the rollout) | For a sample of readings: one replay per part with that part zeroed, recording the flipped verdict |
| C3 | Did an imbalance even out because of the rules or despite them? | Needs a counterfactual replay (same pair, rules off) | Paired runs exist across arms already; the observer would only need a stable run key so paired weeks line up |

## Notes for the builder

- The recorder in `src/mar/atlas.py` shows the off-by-default pattern: it attaches through `WeeklyWorld.hook`, reads only, and ignores any world that is not the one it was attached to, because `copy.deepcopy` copies the hook into rollout copies. An observer that wraps methods instead of using the hook must guard against the same thing: a deep-copied bound method still points at the original world.
- The hook runs after the week's scratch counters (`world.wk`) reset, so anything kept only in `wk` (friend visits initiated, pressed requests, contributions) is gone by the time the hook sees it. The observer needs a second call point at the end of `step_week`, or `wk` copied into the outcome row.
- Bit-identical when off: D2, D3 and S2 ask functions to return parts they already compute. Returning them through a side dict that is only filled when the observer is on keeps the arithmetic and the draw order unchanged. Check with the existing fingerprints (`tests/h38_fingerprint.py`, `tests/levers_fingerprint.py`).
