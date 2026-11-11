# Loop b counting preregistration (ADR 0015)

Status: written and committed before the counting script exists and before the second rater runs. Nothing here is a result. Agents: none. Model API calls: one small subagent as the second rater (it reads this rule and the two raw logs only). No paid runs.

Honest limit on blindness: the person who wrote this rule read every row of the logs while writing it. The rule is not blind to the data. The second rater is the check on that: it gets only the rule text below and the raw logs, never the primary counts.

**Can be about / cannot be about (required).** This result can be about one thing: how often one author corrected the formalizations Claude showed them, in one logged evening, under a written counting rule that someone else can apply. It cannot be about whether loop b converges in general, about other authors, or about the evaluator's quality. Limits in [docs/limits.md](../limits.md) that apply: 6 (one author, one couple of days, one model family: the author, the formalizations, the rule and both raters are one person and one model family) and 8 (a design can make a verdict impossible: handled below). Limits 1 to 5, 7, 9 and 10 are about the simulated world and are not touched; no world is run.

## Purpose and claim

Claim C2 in docs/claims.md (ADR 0005): the author's "not what I meant" moments fall toward a plateau, and a falling count must be told apart from author fatigue or a narrowing conversation. C2 has no counting rule, no unit of opportunity and no fatigue control (docs/reviews/2026-11-11-scope.md, top 5, item 4). This prereg supplies all three and applies them to the existing logs. What it could change: if the rule cannot be applied the same way by a second rater, loop b is not yet measurable and the product's half-claim needs a logging change first. If it can, the logs give a first descriptive curve.

## Data

- `experiments/questions.jsonl`, rows with `backfilled` false (the author's words in `quote`; `topic`, `led_to` and `source` say what was shown and what changed).
- `experiments/changes.jsonl`, all rows (`quote`, `reason`, `kind`, `not_what_i_meant`).
- Nothing else is counted. Author words quoted only in a document and missing from both logs are listed as a sensitivity line, not counted (rule T5).
- Times are UTC in the logs. Local time is UTC minus 5 hours (the repo's commit times are -0500).

## The counting rule (this section is given verbatim to the second rater)

**Event.** One row of `experiments/questions.jsonl` with `backfilled` false, or one row of `experiments/changes.jsonl`. Two rows with the same `quote` less than 10 seconds apart are one event (keep the changes row). The author's words are the `quote`. The other fields say what Claude had shown and what changed afterwards.

**Step 1. Is the event an opportunity?** An opportunity is an answer to a formalization Claude showed the author. A formalization is any of these: a rule card or its plain-English read-back; a score or model term the evaluator uses to judge outcomes; a verdict rule; a written reading of the author's own earlier words (for example the synthesis entries Q1 to Q13); a stated default the author is asked to keep or change. Signs in the context fields: "read-back", "read back", "confirm", "draft", "default", "stand-in", "Claude offered", "options", a review finding put to the author, or `not_what_i_meant` true. These are NOT opportunities: the author's own questions; a first answer to an open question where no formalization of that point existed yet; an approval to start, build, run or add work; a choice about experiment method.

**Step 2. Items.** An opportunity covers one item, unless the author's words address separately numbered or named points (for example "12-13 ... with 8 ...", "yes and yes" after two questions, "renegotiating directly ..., q4 ..."). Then it covers one item per point.

**Step 3. Kind.** Give each item one kind. Take the first that fits.

Loop b corrections (counted):
- **B1 rejected.** The author says the shown formalization is wrong, or replaces it outright. `not_what_i_meant` true is B1 unless the context shows the author only approved a fix that Claude or a reviewer proposed.
- **B2 revised.** The author keeps the formalization but changes its content: widens it, narrows it, adds another allowed path or an exception, or changes what a term covers.
- **B3 hedge restored.** The author puts back a degree word or an uncertainty that the formalization had dropped (for example "only" becomes "mostly").
- **B4 default reversed.** Offered options, or asked whether to keep a default, the author picks something other than the formalization in force or Claude's draft.

Not loop b by the author (counted as opportunities, not as corrections):
- **R reviewer-caught.** Claude or a review found the mismatch and proposed the fix. The author only approves it.
- **U unsure.** The author says they are not sure, and nothing changes.
- **C confirmed.** The author accepts what was shown. This includes "yes", choosing Claude's recommended option, and accepting with a new condition that leaves the shown content as it was.

Not opportunities:
- **S new specification or scope growth.** A new requirement, aim, hypothesis or idea, or a first answer to an open question.
- **D method or design.** How experiments run, statistics, prompt framing, or how the world behaves when the scoring is unchanged.
- **G go-ahead.** Approve, start, build, run, add.
- **Q question or curiosity.**

**Tie-breaks.**
- T1. A change beats an addition. If one item both changes a shown formalization and adds something new, it is B.
- T2. Who found it. If the author's words alone carry the mismatch, it is B. If Claude or a reviewer found it and the author chooses between options, it is B4 only when the choice differs from the formalization in force or Claude's draft. Otherwise it is R (Claude proposed the change) or C (Claude proposed keeping it).
- T3. Confirm then revise. A "yes" followed by a separate row that revises the same point counts twice: C, then B2.
- T4. Hedged corrections still count. "idk" or "i think" does not turn a correction into a confirmation.
- T5. Words that appear only in a document, not in either log, are not counted.
- T6. Test versus world. Changes to what the evaluator counts as good or forbidden (rules, scores, hedonic terms, verdict rules, readings of the author's views) are about the test. Changes to how the world works, with the scoring unchanged, are D.
- T7. B or C. When unsure, use B only if the context fields show the formalization changed after the answer.

**Outputs.** Corrections = items of kind B1 to B4. Opportunity items = items of kind B1 to B4, R, U or C. Correction rate = corrections / opportunity items.

## Design

- **Unit of opportunity.** One answered item (Step 2). A falling count means nothing unless it is per formalization shown. The logs record only answered read-backs. A read-back shown and met with silence leaves no row, so the denominator is "answered items", not "items shown". Silence is not counted as assent (faithfulness review F2). This is the main gap the results file will address.
- **Unit of resampling.** The item. Items from one author on one evening are not independent; any interval is optimistic.
- **Order.** Items sorted by timestamp; items within one row keep their order in the quote.
- **Halves.** First half = the first floor(n/2) items in time order; second half = the rest.
- **Sessions.** A new session starts after a gap of more than 60 minutes between consecutive events (all events, not only opportunities).
- **Pass.** Each item gets a topic key (for example "seed exit terms", "Q8"). Pass = how many opportunities on that topic came before it, plus one. Pass 2 or more means the item was shown again after an earlier answer on it. This is the primary rater's label only; it feeds the fatigue section and no verdict.
- ASSUMED: the 60-minute session gap; the 0.20 margins; the 0.7 length ratio; the bare-confirmation word list below.

## Fatigue control

Corrections could fall because the author tires, not because the formalizations get closer. Proxies, all computed on opportunity events:

1. **Answer length.** Words in the quote. Fatigue shows as shorter answers in the second half while the rate falls.
2. **Bare confirmations.** A quote is bare if, lowercased and stripped of punctuation, it has at most 4 words and every word is in {yes, yeah, yep, ok, okay, sure, and, that, matches, 1, 2, 3}. Fatigue shows as a rising share of bare answers.
3. **Time of day.** Local hour of each item. Reported only. In a single evening, time of day and order are the same variable, so this proxy cannot separate fatigue from convergence. Said now.
4. **Within versus across sessions.** Rate in the first and second half of each session. Fatigue predicts a fall within a session and a rebound after a break. Convergence predicts that the next session starts lower than the last one started, with no rebound.
5. **Harder or easier items.** Share of pass-2-or-more items in each half, and the rate among pass-1 items only. If the second half is mostly re-shown items, a falling rate is partly items getting easier (which is itself a kind of convergence on those items), not a general improvement. If the rate falls among pass-1 items too, formalizations of new material are improving.

How fatigue is told from convergence: convergence is a falling rate with answer length and bare-confirmation share flat (P2), and ideally a falling rate among pass-1 items (P3). A falling rate with shorter answers and more bare "yes" answers is "fatigue not excluded". With one evening of data, proxies 3 and 4 cannot do this job, and the results file must say so.

## Exploratory pilot

None run. The person writing the rule has read the rows (see the blindness limit at the top), so a rough size of the data is known: about 30 to 40 opportunity items in all, so about 15 to 20 per half, and two sessions by the 60-minute rule. No correction count is used below.

## Power check (required)

Exact power of the P1 test (one-sided Fisher exact at alpha 0.05, plus a drop of at least 0.20), by enumeration with `mar.stats.fisher_exact_p`, equal halves:

| True rates (first, second half) | n per half: 10 | 15 | 18 | 25 | 30 | 40 | 50 |
|---|---|---|---|---|---|---|---|
| 0.6, 0.3 | 0.25 | 0.36 | 0.49 | 0.62 | 0.67 | 0.80 | 0.86 |
| 0.6, 0.2 | 0.42 | 0.60 | 0.74 | 0.87 | 0.91 | 0.97 | 0.99 |
| 0.5, 0.3 | 0.13 | 0.18 | 0.26 | 0.33 | 0.36 | 0.46 | 0.52 |

| Prediction | Margin | Spread used | Units for 80% power | Units available | Cost |
|---|---|---|---|---|---|
| P1 | drop >= 0.20 | binomial at 0.6 vs 0.3 | 40 items per half | about 15 to 20 per half | free |

Units available are below units needed. **P1, P2 and P3 are DESCRIPTIVE.** The expected primary verdict is "descriptive only, underpowered", whatever the counts show. Only P0 (rater agreement) is a check with a pass or fail.

## Predictions

| ID | Quantity | Unit | Threshold | Test | Alpha | Family | Interval |
|---|---|---|---|---|---|---|---|
| P0a | Cohen's kappa, primary vs second rater, on "event is an opportunity", all events | event | >= 0.6 | point estimate | n/a | none | bootstrap 95% over events |
| P0b | Cohen's kappa on "event holds at least one correction", events either rater marked an opportunity | event | >= 0.6 | point estimate | n/a | none | bootstrap 95% over events |
| P1 | correction rate, first half minus second half | item | >= 0.20 and p < 0.05 | Fisher exact, one-sided | 0.05 | Holm over P1, P3 | Newcombe 95% |
| P2a | median words per opportunity answer, second half / first half | event | >= 0.7 | point estimate | n/a | none | none |
| P2b | bare-confirmation share, second half minus first half | event | < 0.20 | point estimate | n/a | none | Newcombe 95% |
| P3 | correction rate among pass-1 items, first half minus second half | item | >= 0.20 | Fisher exact, one-sided | 0.05 | Holm over P1, P3 | Newcombe 95% |

Effect sizes reported: rate difference with interval, rate ratio.

## Verdict rule

Applied in this order:
1. **"rule not operational"** if P0a or P0b fails. Then no count is cited, and the rule must be fixed.
2. **"descriptive only, underpowered"** if either half has fewer than 40 items. The results file then reports the direction in words only: "falling" (drop >= 0.20), "rising" (rise >= 0.20) or "flat", plus the fatigue proxies.
3. Otherwise: **"converging"** if P1 and P2a and P2b hold. **"falling, fatigue not excluded"** if P1 holds and P2a or P2b fails. **"not converging"** if P1 fails.

P3 is reported beside the verdict and does not change it.

## Can every verdict happen? (required)

Free checks on synthetic logs, written as tests in tests/test_loop_b_count.py and run before the real logs are counted. Each fixture is a list of labeled items built in code (no model).

| Verdict or clause | Synthetic input | Expected |
|---|---|---|
| converging | 50 items per half, rate 0.6 then 0.1, equal lengths, no bare answers | "converging" reached |
| not converging | 50 per half, rate 0.4 then 0.4 | "not converging" reached |
| falling, fatigue not excluded | 50 per half, rate 0.6 then 0.1, second-half answers one word and bare | reached |
| descriptive only, underpowered | 10 per half, any rates | reached |
| rule not operational | second rater flips half the opportunity labels | reached |
| P1 fails on the margin | 50 per half, 0.5 then 0.35 (drop 0.15) | P1 false |
| P1 fails on the test | 12 per half, 6 then 3 corrections (drop 0.25, p >= 0.05) | P1 false with drop >= 0.20 |
| P2a fails | second-half answers under 0.7 of first-half length | P2a false |
| P2b fails | bare share rises by 0.3 | P2b false |
| P3 fails | the whole fall comes from pass-2 items | P3 false while P1 true |
| P0a, P0b fail | rater disagreement | false |

Open cells: the verdict needs no pattern across cells; every clause above has a failing input. The metric can see the mechanism: a correction lands in the count only through its item kind, and the rate's denominator is the same item list, so a fall in shown-and-answered items cannot hide in the numerator alone.

## Not testable by design

- Whether silence after a read-back was assent. No row exists for it.
- Time of day apart from order (one evening).
- Whether the author's intent itself moved (a new wish) rather than the test getting closer. S rows are counted apart for this reason, but the line between "a new wish" and "a correction" is a judgment the second rater checks.

## Limits stated now

One author, one evening (about 11:45 am to 10:45 pm local on 2026-11-10, which spans two UTC dates). The formalizations, the rule, the primary count and the second rater are all one model family. The logs were written by Claude agents during the work, so their `led_to` and `reason` fields are Claude's summaries, not the author's. Button-label quotes ("Yes, start both") may not be the author's typed words (faithfulness review F11); they are G rows and do not enter the rate.

## Amendments

None yet.
