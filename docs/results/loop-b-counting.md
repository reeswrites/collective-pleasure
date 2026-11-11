# Loop b counting: results

Prereg: [loop-b-counting-prereg.md](loop-b-counting-prereg.md) (committed fef17e0, before the script and the second rater). Script: `scripts/loop_b_count.py`. Tests: `tests/test_loop_b_count.py` (17 pass, including every synthetic reachability fixture). Second rater's labels: [loop-b-rater2.json](loop-b-rater2.json). No model calls except the second rater (one small subagent, given only the rule text and the two raw logs).

Reproduce: `uv run python scripts/loop_b_count.py --rater2 docs/results/loop-b-rater2.json`

## Verdict

**Rule not operational** (verdict rule step 1). The two raters agree well on which rows are answers to a shown formalization (P0a, kappa 0.92). They do not agree well enough on which of those answers are corrections (P0b, kappa 0.45, 95% interval 0.13 to 0.74, threshold 0.6). By the prereg, no count below is cited as a C2 result. The counts are reported so the next version of the rule and the log can be built on them.

Had P0b passed, the verdict would have been "descriptive only, underpowered" in any case: each half holds 17 items, and the power check needs 40.

## Counts

95 author events (73 question rows that are not backfilled, after one duplicate is merged, plus 22 change rows). They give 100 items, of which 34 are answers to a formalization the author was shown (opportunity items).

By kind, primary rater, all items:

| Kind | Count | Counted as a loop b correction? |
|---|---|---|
| B1 rejected | 5 | yes |
| B2 revised | 7 | yes |
| B3 hedge restored | 1 | yes |
| B4 default reversed | 2 | yes |
| R reviewer-caught, author approves | 1 | no (opportunity) |
| U unsure | 2 | no (opportunity) |
| C confirmed | 16 | no (opportunity) |
| S new specification or scope growth | 36 | no |
| D method or design | 6 | no |
| G go-ahead | 17 | no |
| Q question | 7 | no |

So 15 corrections in 34 opportunity items. The second rater found 11 in 31.

By session (a gap of more than 60 minutes starts a new one; local time is UTC minus 5):

| Session | Local time, 2026-11-10 | Events | Opportunity items | Corrections | Rate |
|---|---|---|---|---|---|
| 1 | 1:17 pm to 5:03 pm | 36 | 6 | 4 | 0.67 |
| 2 | 6:44 pm to 10:45 pm | 59 | 28 | 11 | 0.39 |

Most of session 1 is the author asking questions and setting aims (19 S rows, 7 Q rows). Almost all read-backs come in session 2.

## Rate per read-back

| | First half (items 1 to 17) | Second half (items 18 to 34) | Difference |
|---|---|---|---|
| Primary rater | 9 of 17 (0.53) | 6 of 17 (0.35) | 0.18, Newcombe 95% [-0.14, 0.45], one-sided Fisher p = 0.25 |
| Second rater | 7 of 15 (0.47) | 4 of 16 (0.25) | 0.22 |
| Among first-showings only (pass 1, primary) | 6 of 11 | 5 of 13 | 0.16, p = 0.35 |

P1 (drop of at least 0.20 with p < 0.05) does not hold. In words, the primary count is "flat" (a drop of 0.18, under the 0.20 margin) and the second rater's is "falling" (0.22). The two raters do not even agree on the direction word. P3 does not hold either.

Sensitivity (rule T5, not counted): the synthesis records a Q10 revision the author prompted, "why narrowing into a partners world particular versus just in general". It is in docs/notes/hedonic-technology-synthesis.md and in neither log. With it, the count is 16 of 35, and it falls in the second half.

## Fatigue proxies

| Proxy | First half | Second half | Reading |
|---|---|---|---|
| Median words per answer | 15.5 | 7.0 | ratio 0.45, below the 0.7 bar. P2a fails: a fatigue sign |
| Share of bare confirmations | 0.19 | 0.21 | flat. P2b holds |
| Share of items shown again (pass 2 or more) | 0.35 | 0.24 | later items were not easier re-reads; if anything they were newer |

Within and across sessions. Session 1: 2 of 3, then 2 of 3. Session 2: 8 of 14 in its first half, then 3 of 14 in its second. Session 2 started at 0.57, a little below where session 1 started (0.67). The fall happens inside the evening session, not across the break. That fits fatigue at least as well as convergence.

Time of day. By local hour: 9 pm, 7 corrections in 16 items; 10 pm, 1 in 7. The 10 pm hour is the Q6 to Q10 read-backs, with answers like "yes and yes" and "yes that matches". On one evening, time of day and order are the same variable, so this proxy cannot separate the two readings, as the prereg said.

So: the late read-backs got shorter answers and fewer corrections, inside one long session, late in the evening. The items were not easier. The data cannot tell fatigue from convergence, and the length proxy leans toward fatigue.

## Second-rater agreement

| Check | Value | Bar | Holds |
|---|---|---|---|
| P0a: kappa on "is an opportunity", 95 events | 0.92 [0.83, 1.00] (raw agreement 0.97) | 0.6 | yes |
| P0b: kappa on "holds a correction", 30 events either rater marked an opportunity | 0.45 [0.13, 0.74] (raw agreement 0.73) | 0.6 | no |
| Exact match on the full kind list, 95 events | 0.81 | none | reported |

Where the raters split on corrections (8 events):

| Event | Author's words | Primary | Second | Why they split |
|---|---|---|---|---|
| c2 21:32Z | "1" | B4 | R | The log does not say the coded pot was per-person shares, or that option 1 differed from it |
| c17 02:51Z | "show both, judge on pleasure" | B4 | R | The log does not say the draft verdict rule judged on net wellbeing |
| q73 02:33Z | "maybe we have to test? but my intutions is mostly actions" | B3 | C | The log does not say the draft said "only actions" |
| q74 02:34Z | "allowed only by mutual choice i think" | B2 | C | The log does not say the draft had a default fine |
| q65 02:01Z | "i think that theres a differnt better way of thiknkng about it if you zoom out and thikn about pleasures more broadly" | B1 | S | Was "safe vs spicy" a formalization or an open question? |
| q81 03:39Z | "i think you can enjoy giving into a void (dom sub etc) so the pleasure does not have to be real but it depends on the persons reasons for giving pleasure" | B2 | S | Read-back answer or new idea? |
| q78 02:56Z | "i think uneveness should be a problem? or i guess not inherently" | U | B2 | Unsure, or a revision with hedges? |
| c19 02:57Z | "yeah first one mostly, and yes do all three" | C | B3 | Choosing Claude's option, or adding "mostly"? |

Four of the eight splits (c2, c17, q73, q74) have one cause: the log records what the author said and what changed, but not what the author was shown. The primary rater knew the drafts from the documents. The second rater had only the logs, as the rule intends, and could not see that the answer differed from the draft. The other four are real judgment calls in the rule (open question versus formalization; unsure versus hedged revision).

Both raters agree on the clear cases: all five rows flagged `not_what_i_meant` except c2 are corrections (c0, c1, c3 counted twice, c4), and so are q38 (the liberty answer the scope review said was left out), q69, q75 and q77.

## What this says about loop b, in plain English

Loop b is the author telling the system "that's not what I meant". On this one evening, the author corrected about 4 in 10 of the formalizations they answered (15 of 34, or 11 of 31 by the second rater). That rate fell a little over the evening, but not by enough to tell from chance, and the two raters disagree on whether it fell at all. The answers also got about half as long, inside one long session that ended at 10:45 pm. So a falling count here could be the author tiring as easily as the formalizations getting closer.

The bigger finding is about the log, not the author. A second reader, given only the log, cannot reliably tell a correction from a confirmation, because the log never says what the author was shown. And silence leaves no row at all: the seed v2 read-back showed 14 cards per variant, and only the 2 points the author spoke about appear in the log. The 15 corrections are real. The rate cannot yet be measured.

The four hand-logged corrections in claims.md are all counted here. So is the liberty answer ("idk if we can count of it as loss of freedom when technically it was only possible thru agreement"). The rule adds 10 more, mostly read-back answers that narrowed, widened or re-hedged a formalization without the `not_what_i_meant` flag.

## Recommendation: logging that would make loop b measurable

Log each read-back offered, not only each answer. One row per item shown, in a new `experiments/readbacks.jsonl`:

| Field | Why |
|---|---|
| `readback_id`, `item_id`, `timestamp_shown` | the denominator: every item shown counts, answered or not |
| `shown_text` (or file plus commit) | lets a second rater see what the answer differs from. This alone would have settled 4 of the 8 splits |
| `in_force_before` | the formalization or default the answer could reverse (B4) |
| `who_found_mismatch`: author, Claude, reviewer, none | separates loop b by the author from R |
| `answer_event` (the questions or changes row), or `null` for silence | silence is recorded, not read as assent |
| `outcome`: confirmed, revised, rejected, hedge restored, default reversed, unsure, no answer | labeled at the time, by the agent that showed it; a second rater checks a sample |
| `after_text` | what changed, so T7 is mechanical |
| `typed_or_button` | button labels written by Claude are not the author's words (faithfulness review F11) |
| `session_id` and `item_novelty` (first showing or re-show) | the fatigue controls |

Also: quote every author line in the log, including prompts like the Q10 one that now lives only in the synthesis. And to separate fatigue from convergence, show a few fixed probe formalizations (already-confirmed items, re-worded) early and late in each session. If the author still catches a planted error late in a session, a low correction rate means the formalizations are good, not that the author stopped reading. ADR 0005 already suggested fresh probes; this makes them planted.

The rule itself needs two fixes before the next count: say how to tell an open question from a formalization (q65), and how to tell "unsure" from a hedged revision (q78). Both are noted for the next prereg; no threshold here is changed.
