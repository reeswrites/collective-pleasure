# Review: faithfulness of the 2026-11-11 formalizations (seat 4 of the council)

Reviewed commit: 11427cb (working tree read at that commit; the only uncommitted change in a reviewed file is one added line in docs/decisions/0018-hedonic-technology-tests.md, "Test 1 built", which is read as part of the review). Reviewer: fresh agent, no prior context. Read files and git only. No tests, no runs, no model calls. Nothing edited except this file.

Question: do today's formalizations of the author's words say what the author said, without stretching, narrowing or adding?

Sources of the author's words: experiments/questions.jsonl (31 rows dated 2026-11-11), experiments/changes.jsonl (rows with kind "decision" or a quote: rows 1 to 15), docs/seeds/author-household-norms-2026-11-10.md.

Formalizations checked: docs/notes/hedonic-technology-synthesis.md section 5; docs/results/seed-v2.3-readback.md; docs/results/household-fixes-design.md; docs/results/v2-retest-prereg-DRAFT.md; docs/theory.md (with the Sinhababu section); docs/one-pager.md; docs/decisions/0018-hedonic-technology-tests.md; experiments/hypotheses.jsonl H29 to H35.

Categories: (1) Claude's framing or a saved AI reply presented as the author's view; (2) a hedged answer turned into a firm rule; (3) a later answer superseded an earlier formalization that still stands; (4) a logged decision missing from the docs that should carry it.

Overall: the v2.3 read-back is the most careful document. It quotes each answer next to the rule and separates "settled by the author" from "Claude's interpretation", and its trust answer ("mostly actions" plus a test arm) is a model of how to carry a hedge. The weakest point is the retest verdict rule. It decides whether the author's condition is "met", and it rests on a hedged answer that it reads more widely than the author's condition. The next weakest is synthesis section 5. It was written at 02:04Z, before six later answers, and was never updated. It also claims read-backs that the log does not record.

## High

### F1. The verdict rule redefines the author's condition, on a hedged answer (categories 2 and 1)

Author, seed v2.2 condition (docs/seeds, 2026-11-10):
> yes as long as it can demonstrate pleasure in relationships hedonic technology

Seed doc's own gloss of it: "rules as a technology for producing pleasure in relationships, not only for preventing harm."

Author, on the retest score (changes.jsonl row 12, 02:22:46Z):
> pleasure minus suffering yeah i guess if that is what is commonly held

Formalization (v2-retest-prereg-DRAFT.md): "The condition is judged on pleasure minus suffering." Verdict rule: "The author's condition is met for v2.2 iff P1 holds robustly" (P1 is net wellbeing). Also: "If P1 holds and S1 fails, the report says so plainly: v2.2 leaves people better off by pleasure minus suffering, mainly by sparing suffering, not by adding pleasure." In that case the condition still counts as met. household-fixes-design.md: "The author has now settled both questions ... the condition is judged on pleasure minus suffering."

Problems:
- The answer is hedged twice ("i guess", "if that is what is commonly held"). It is conditional on a premise that no document checks. It became "settled".
- The answer picks a score. It does not say what passing means. The rule "met iff P1 is significant and the interval is above 0" is Claude's, but it is written as the meaning of the author's condition.
- With net wellbeing as the score, the condition can be "met" by sparing suffering alone. That is the "only preventing harm" reading which the seed doc's own gloss excludes.
- "In relationships": under changes.jsonl row 13 ("yes pairs should be allowed to not form a househodl"), people who never form a household count toward the score. A gain among people living apart is counted as "pleasure in relationships". The author agreed to let pairs decline. The author did not say their outcomes count toward the condition.

Fix: label the verdict rule as Claude's proposal. Before the run, ask the author two things: does a net-wellbeing win with no pleasure win meet the condition, and should non-formed pairs count toward it?

### F2. "Read back with no objection" is not in the record (category 1)

Synthesis section 5 header: "These are Claude's read-backs. The author confirmed the ones marked 'confirmed'. The rest were read back with no objection."

The log says otherwise. Every row behind Q2, Q4, Q6, Q7, Q8, Q9 and Q10 has led_to ending "(pending read-back)". For example:
> reliance is fine its the guilt and scorekeeping i dont like like this seems to be abou specializaion and having to allocate roles etc

was logged as "Q2: ... (pending read-back)". No row records a read-back of these items or a lack of objection. This is the same pattern the 2026-11-10 review flagged ("read back and accepted"): silence, or no record, is reported as assent. Only Q12 has a logged confirmation ("yeah", 02:04:09Z). Q11 ("yeah i like your rec") and the v2.3 points are logged too.

Fix: replace the sentence with "Not yet read back: Q2, Q4, Q6, Q7, Q8, Q9, Q10."

### F3. Synthesis section 5 and the one-pager still hold answers that later answers replaced (category 3)

Section 5 was committed at e01d702 (21:04:09 local, 02:04:09Z). These later answers never reached it:

| Section 5 still says | Later author words | Where the later answer is carried |
|---|---|---|
| Q5: "open." | 02:05:59Z essay excerpt: "At the very least we owe politeness and common decency if we are both on common ground." 02:38:17Z: "all three feel right, common ground is anyone you interact with" | seed-v2.3-readback rule 18 |
| Q2: "trust updates from actions, not words." | 02:33:56Z: "maybe we have to test? but my intutions is mostly actions" | read-back (default "mostly", three-arm test) |
| Q2: "Guilt, scorekeeping and penalties are the objection." | 02:34:43Z, on fines for lapsed roles: "allowed only by mutual choice i think". The author named only "guilt and scorekeeping"; "penalties" was added and is now contradicted. | read-back rule 17, fix 4 |
| Q2: "This is a candidate for seed v2.3." | v2.3 read-back confirmed on four points (02:33Z to 02:38Z) | read-back status line |
| Q12: "Cheap novelty is all spike." The novelty model is "a fast spike of wanting that habituates". | 02:04:45Z: "well a nwe thing is exicitng unto itself also when you like it as well there is no replacable thing of being suprrised or exp smth for first time" | H33 only |

The same 02:04:45Z answer settles the question that H29's note still leaves open. H29 says: "Open: does novelty raise liking or only wanting (test 1)?" The author says novelty is exciting "also when you like it as well". That is a claim about liking. It can still be tested, but it is no longer an open question for the author.

docs/one-pager.md (committed 02:17Z) says "Seed v2.3 is a candidate from the author's answer on reliance and role lapses". It also describes the v2.2 shortfall only in mean pleasure. Both were replaced within 20 minutes: v2.3 is confirmed, and the retest's primary measure is now net wellbeing (row 12).

Fix: add a dated "later answers" block to section 5. Update the H29 note and the two one-pager lines.

## Medium

### F4. Q13 provenance rule broken in theory.md's Sinhababu section (category 1)

Synthesis Q13 rule: the note bodies "are saved AI replies, not the author's prose. Do not quote them as the author's words." Its last line: "Open, for the author: the 'thermometer' reading implies a standard beyond pleasure, while the author's current position is that pleasure is the good."

theory.md: Sinhababu's argument "also answers the 'thermometer, not temperature' worry in the author's saved note 'pleasure as the detector of value'".

The thermometer image and the worry come from the AI reply. The synthesis calls it a tension for the author to resolve, not a worry the author holds. "The author's saved note" lets a reader assign the worry to the author. Also, theory.md says "The author asked what Neil Sinhababu argues and asked for both points to be added". The logged words are only:
> yeah add both

which accepts Claude's offer. Whether the author first asked about Sinhababu is not logged.

A smaller blur in synthesis Q13 itself: "**Delivery schedule** (the author's thesis; the AI elaboration was saved): flourishing comes from spacing, contrast and effort more than from content." The author's own line is only "human flourishing is just the right delivery schedule for a unique...". "Spacing, contrast and effort more than content" reads as the elaboration, but it sits after "the author's thesis:".

Fix: "the 'thermometer' reading in a saved AI reply under the author's note title". In Q13, put the author's line after the colon and the AI gloss in its own sentence.

### F5. A paraphrase quoted as the author's words (category 1)

theory.md section 1: "**Author**, in the notes: wanting (prediction error) and liking adapt differently, and 'overstimulating wanting burns out liking.'" docs/results/liking-wanting-prereg.md uses the same quotation marks.

The source, synthesis section 1, has the phrase unquoted in a summary bullet ("Overstimulating wanting burns out liking."). The same bullet ends: "These come from an AI-generated passage inside the note, not from the author's own claim." It is unclear whether "these" covers only the rules of thumb or the whole bullet. Either way, nothing in the repo shows the author wrote these words.

Fix: drop the quotation marks and mark it as the synthesis's paraphrase, until the note's own text is checked for authorship.

### F6. "author's theory" labels on hypotheses from Claude's turns or Claude's summaries (category 1)

In experiments/hypotheses.jsonl, all of H29 to H35 have group "author's theory". For four of them the source is not the author's own words:
- H30 and H31: the motivation is "Dunbar/valence chat (cited, not archived)", a claude.ai conversation. The questions row says only that the author "shared a prior chat" with the path as the quote. The claims (layers in a 3x ratio, vigilance raising bonding cost, Cacioppo) may come from Claude's turns in that chat. The Q13 rule applies by analogy: the author shared it, so it is not necessarily the author's view.
- H34: built on theory.md's Sinhababu section, which theory.md itself calls "Claude's summaries". The author's words are "yeah add both".
- H35: the claim (care grows with amplified shared weeks; threshold spirals) is Claude's proposal, built on H32 results. The author's words: "yeah add the spiral as the next hypothesis". The note's "Author asked to add this" is accurate. The group label is not.
- H32: "the author's essay thesis that egoistic hedonists and hedonistic utilitarians alike must attend to others' pleasure" comes from an excerpt that was not archived ("excerpt not archived"). The thesis is normative. H32 tests a stronger, positive claim: egoist and utilitarian optima converge under free exit. Free exit as the mechanism is Claude's. H32 is now "not supported", so the label "author's theory" invites the reading that the author's thesis failed. docs/results/h32.md handles this well ("supports a narrower form of it"). The register entry does not.

Fix: use a group such as "from the author's prompt, Claude's mechanism" for H30, H31, H34 and H35. In H32, say the convergence mechanism is Claude's operationalization.

### F7. "Confirmed" covers more than the four answered points (categories 1 and 2)

seed-v2.3-readback.md status: "CONFIRMED BY THE AUTHOR ... The rules below are the confirmed wording." The author answered four points:
> maybe we have to test? but my intutions is mostly actions
> allowed only by mutual choice i think
> check in first for general unhappiness too
> all three feel right, common ground is anyone you interact with

None of these touches rule 14 (roles). Rule 14's content is Claude's interpretation, and the document says so:
- jobs limited to earning, bills and planning;
- specialization saves 25 percent;
- "reliance is fine" means the other partner may stop doing the job.

Open questions 1 and 3 also show that rule 14 and the slid-into flag are unsettled. Yet household-fixes-design.md and the prereg cite "Seed v2.3 (confirmed by the author 2026-11-11, with changes)" without that limit.

Ladder order. Original words:
> renegotiate or a soft check in i think not leaving right away

"Check in first" is now settled. "Then renegotiate" as a required second rung before exit is not; the author wrote "or". The "Settled by the author" list nevertheless says: "check-in first, then renegotiate, then leaving last." This matters for the results. H32b found that renegotiation "undid" the convergence that withdrawal produced. A fixed check-in, renegotiate, exit order builds in the step the author left optional.

Fix: change the status line to "Points 1 to 4 confirmed; rule 14 and the evaluator flag are Claude's drafts, not yet read back." Mark renegotiation as Claude's ordering.

### F8. Hedges made firm (category 2)

| Author (verbatim) | Formalization |
|---|---|
| "allowed only by mutual choice i think" | read-back: "Settled by the author ... A fine on a lapsed role is allowed only by mutual choice"; fixes design: "The author confirmed" |
| "idk if they need similkar gains but i guess they just need to be better off within the rleatiniship maybe?" | synthesis Q4: "Each partner must end up better off within the relationship than outside it"; this becomes the slid-into flag's threshold. The read-back labels it as Claude's interpretation; the synthesis does not. |
| "yeah why wouldnt an agent choose their partner?" then "i mean maybe we test different strategies" | synthesis Q7 and the H26 note: "agents should choose partners". The questions row itself says "author leans toward". |
| "i think the experieicing self is the remembering self and depends onf vividness of memory etc" | theory.md section 4 and synthesis Q1: stated as the author's settled position, without "i think" |
| "lifetime pleasure seems obvious to me ... not be greedy but idk if we can prove that somehow" | theory.md section 4: "The horizon study proves the author's hunch". It proves a model result with a condition: greedy is optimal exactly when actions leave no trace. That is narrower than the hunch. |

The first two matter most: one sets a fine rule, the other sets an evaluator threshold. The last three are wording issues.

### F9. "Beyond the floor, nobody owes anything" narrows "it becomes tricky" (categories 3 and 2)

Author, 02:05:59Z:
> At the very least we owe politeness and common decency if we are both on common ground. However beyond that I feel like it becomes tricky. Each person's internal calculus will be different but I think it's most helpful to think that you can't complain about doing things for friends

Rule 18: "Beyond this floor, nobody owes anybody anything except what they negotiated (as in v2.2)."

The rule falls back on the 2026-11-10 seed ("no one owes anyone anything day to day except for what they have negotirated"). The later answer qualifies that seed: beyond the floor the answer is "tricky" and differs by person. That is not the same as zero. The questions row's led_to has it right ("beyond that personal"). The rule does not.

Fix: keep zero as the model default, but say the author called this region "tricky" and person-specific, and list it as open.

### F10. The seed document does not carry the v2.3 confirmation or the retest decisions (category 4)

docs/seeds/author-household-norms-2026-11-10.md says: "Do not edit the quotes; add later answers as new dated entries below." Its last entry is the v2.2 confirmation (commit 3cd60fd, 2026-11-10 19:07 local). Not entered:
- the four v2.3 read-back answers;
- changes.jsonl rows 10, 12 and 13 ("yes fix then retest if that is best course of aciotn", "pleasure minus suffering yeah i guess if that is what is commonly held", "yes pairs should be allowed to not form a househodl").

Rows 12 and 13 change how the seed's own condition is judged (F1). The seed doc is the reference for "not what I meant" checks, so a later reader comparing against it will not see them.

## Low

### F11. Some decision "quotes" look like Claude-written button labels (category 1, unverified)

Rows 6 to 9, 11 and 15 have quotes "Yes, test 2 first", "Yes, start test 1", "Yes, start both", "Yes, start H32", "Yes, build fixes" and "Yes, start both". Unlike every typed answer, they use capitals and correct spelling. They are probably labels Claude drafted on reply buttons, which the author clicked. The click is the author's decision; the words are not the author's. ADR 0018 says "The author answered 'Yes, test 2 first'". If that was a button, one click both accepted the ADR and set the build order, as a bundle Claude wrote. I cannot verify this from the repo. Suggest a field such as "via": "button" | "typed".

### F12. ADR 0018 does not record "Yes, start test 1" (category 4)

Row 7 (01:27:04Z), reason: "Author asks to start building ADR 0018 test 1 ... now, in parallel with test 2". The ADR still says "Build order decided by the author: test 2 first". The uncommitted line "Test 1 built (2026-11-10)" records the build but not the author's decision to run both at once.

### F13. Q9 narrowed for security (category 2 in reverse: a narrowing)

Author:
> security and money only count to the extent that the person values those things inherently or as a means to theri pleasure

Fix 2: money gets both routes (w_m intrinsic, plus k_buy through spending). Security gets only "w_s x level", the intrinsic route; there is no instrumental route. A persona with security weight 0 then gets nothing from security, even where security is a means to pleasure. A related point: "subsistence counts for everyone" is Claude's addition. It is defensible as the "means" route, but it should be labeled as Claude's reading of Q9.

### F14. A Claude design choice listed among the author's answers (category 1)

Synthesis Q4: "The evaluator reports the size of the gap between partners' gains as information, not as a failure." The author said "idk if they need similkar gains". The reporting decision is Claude's, and the prereg (C7, "Q4: reported as information, not as a failure") cites it as the author's. Mark it as Claude's.

### F15. A conditional approval recorded as unconditional (category 2)

Author, row 10:
> yes fix then retest if that is best course of aciotn

The fixes design and prereg cite this as "Approved plan". But the design's own finding 2 says the gap comes mostly from the baseline never declining, and it says: "None of the four fixes addresses the structural cause." That finding bears directly on the author's "if that is best course". It was resolved by row 13, not by the fixes, and the author was not told this re-ordering bears on the condition. No change needed if the author has seen finding 2; worth one line in the next read-back.

### F16. A logged led_to that no document carries (category 4)

The 02:05:59Z row lists "persona trait: capacity to regard the other's pleasure". It comes from the author's essay excerpt:
> Some people you are in a relationship may not have the abilities to consider or take seriously your pleasure

No persona, design or hypothesis has this trait. The nearest is H32's "partly blind partner" robustness check. Add it to the fixes design or the hypothesis register as a queued item.

### F17. Smaller items

- docs/results/h32b.md (outside the listed scope) quotes the author with corrected spelling ("ultimately ... strongest signal") and no mark. The verbatim is "utlimtaly ... sterongest". Either quote it exactly or mark it as cleaned up.
- The prereg says the run decides "whether v2.3 replaces v2.2 as the working seed". The author did not say v2.3 would replace v2.2. The read-back says "Seed v2.2 is not changed". Mark this as Claude's proposed decision rule.
- The synthesis Q13 records the author's own hedged line "the value is our end to reproduce i guess: our telos is evolution" beside the statement that "the author's current position is that pleasure is the good". No formalization uses the telos line. Flag it for the author rather than letting either reading stand silently.

## What is faithful

- **Trust read-back.** "maybe we have to test? but my intutions is mostly actions" became a "mostly actions" default plus a descriptive three-arm comparison. That is the right way to carry a hedge.
- **Fines.** "Allowed only by mutual choice" (allowing for F8's hedge) is carried the same way in rule 17, fix 4, prereg M4 and the arms table.
- **Decency floor.** The three parts, and "common ground = anyone you interact with", match the answer. The 4 weeks is marked ASSUMED.
- **Q10 and H29.** Narrowing is acceptable "if the deepening means that you can experience more totla pleasure". Broadening is expected to win ("but that seems unliekly to me vs broadening").
- **Q6.** "valid persona but i think it would score lower".
- **Q11.** Sweep centers, which the author explicitly accepted ("yeah i like your rec").
- **Q12 three lenses and the biology model.** Confirmed ("all three for sure", "yeah"), apart from the later firsts answer (F3).
- **H33.** Its motivation quotes the firsts answer accurately.
- **Baseline may decline.** "yes pairs should be allowed to not form a househodl" is carried accurately into the design and the prereg.
- **theory.md attribution marks.** The Author / Claude-added marks are used well in sections 2 and 3.
- **ADR 0018.** States plainly that grouping the tests is Claude's framing.

## Recommendations (not applied)

1. Before Amendment 1, ask the author whether the condition is met by a net-wellbeing win with no pleasure win, and whether non-formed pairs count (F1). Until then, label the verdict rule as Claude's.
2. Replace "read back with no objection" with the list of items not yet read back. Add a dated "later answers" block to synthesis section 5 (F2, F3).
3. Fix the Q13 breach and the quoted paraphrase in theory.md (F4, F5).
4. Relabel the group on H30, H31, H34 and H35. Mark H32's mechanism as Claude's (F6).
5. Narrow the v2.3 "confirmed" status to points 1 to 4. Mark the renegotiate rung as Claude's ordering (F7).
6. Append the v2.3 answers and changes.jsonl rows 10, 12 and 13 to the seed document, as dated entries (F10).
7. Record in changes.jsonl whether a decision quote was typed or a button (F11).
