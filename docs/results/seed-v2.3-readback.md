# Seed v2.3 read-back (for the author)

**Status: PARTLY CONFIRMED (2026-11-11).** The author answered four points (experiments/questions.jsonl, topics `seed-v2.3-readback-1` to `-4`, 2026-11-11T02:33:56Z to 02:38:17Z). The whole wording is not confirmed. Only the four answered points are.

**Answered by the author:**
1. Trust: "maybe we have to test? but my intutions is mostly actions".
2. Fines on lapsed roles: "allowed only by mutual choice i think".
3. Exit last, plus general unhappiness: "check in first for general unhappiness too".
4. The decency floor: "all three feel right, common ground is anyone you interact with".

**Never read back (Claude's drafts):**
- Rule 14 (roles): the three jobs, the specialization saving, and "the other partner stops doing the job".
- The slid-into evaluator flag.
- The fixed order check-in, then renegotiate, then exit. The author's words were "renegotiate or a soft check in". "Check in first" is the author's. Renegotiation as a required second step is Claude's ordering.
- The severe-distress skip (a partner at a non-offsettable load of 0.4 or more may leave without the ladder). The first wording is kept in git history (commit 21ff48c). Seed v2.2 is not changed: the `author_seed_v2_*` directories stay as they are. v2.3 will live in a new directory, `rules/household/author_seed_v23_bindable`, built in phase 2.

## The author's answers (verbatim) and what changed

| Point | The author's words | Change to v2.3 |
|---|---|---|
| 1. Trust | "maybe we have to test? but my intutions is mostly actions" | Default is "mostly actions": actions move trust a lot, words a little. The retest adds a descriptive arm comparing three versions: only actions, mostly actions, and words count until tested. |
| 2. Fines on lapsed roles | "allowed only by mutual choice i think" | Rule 17 changes: no fine by default. A fine on a lapsed role exists only if both partners explicitly choose it, and the scorekeeping cost then applies (as in fix 4). |
| 3. Exit last | "check in first for general unhappiness too" | Check-in first and exit last are confirmed as how agents behave, not a ban; free exit (rule 11) stands. New: the ladder covers any unhappiness, not only lapsed roles. The renegotiate step in between is Claude's (see rule 16). |
| 4. Decency floor | "all three feel right, common ground is anyone you interact with" | All three parts confirmed. "Common ground" now means anyone the agent interacts with. |

Two retest decisions came at the same time (experiments/changes.jsonl, 2026-11-11T02:22:46Z and 02:23:24Z): "pleasure minus suffering yeah i guess if that is what is commonly held" and "yes pairs should be allowed to not form a househodl". They change the retest, not the seed (docs/results/v2-retest-prereg-DRAFT.md).

Wording rule: agents feel nothing. "Pleasure" is a gloss for a modeled hedonic state (ADR 0010).

Sources. The author's exact words come from experiments/questions.jsonl, rows dated 2026-11-11 (topics open-question-Q2, Q4 and Q5). The read-backs of those answers are in docs/notes/hedonic-technology-synthesis.md, section 5. The decision to build this came from the author's answer "yes fix then retest if that is best course of aciotn" (experiments/changes.jsonl, 2026-11-11T02:06:55Z).

## What v2.3 is

Seed v2.3 is seed v2.2 (bindable) plus new rules. The 13 cards of `author_seed_v2_bindable` stay word for word as read back in docs/results/seed-v2.2-readback.md. Trust, the exit floor and the 13-week reviews stay as they are. The new parts are:

- rules 14 to 17 (roles, and the response to unhappiness, including a lapsed role);
- rule 18 (the decency floor);
- one change to how trust moves (mostly from actions, a little from words);
- one evaluator flag that is not a rule (chosen versus slid-into sacrifice).

Each part below gives the rule in plain English, then the author's exact words, then what is Claude's interpretation. Anything under "Claude's interpretation" is a guess about what the author meant, made so the rule can run in the model.

## Rules 14 to 17: roles and the lapse ladder

### Rule 14. `R9-may-agree-roles`

**Status: Claude's draft, never read back.** The author did not answer anything about this rule.

**Plain English.** Partners may agree roles. A role says who usually does a recurring job for the household. A role exists only if both partners agreed to it. Partners can agree no roles at all. A role is a negotiated term, like the exit terms, and can be changed at any review.

The jobs a role can cover in the model are: earning (working), paying the shared bills, and planning time together. The partner who holds a role gets better at it over time, so the job costs them less than it would cost the other. The other partner stops spending effort on it.

**The author's words.**

> reliance is fine its the guilt and scorekeeping i dont like like this seems to be abou specializaion and having to allocate roles etc

**Claude's interpretation.**
- That "allocate roles" means a negotiated term, not an imposed division. The author did not say who allocates.
- The list of three jobs. The model only has these actions, so a role can only cover what the world can do. Real roles (cooking, care, planning trips) are richer.
- That specialization pays: the role holder does the job at lower cost. This is a classic economics idea (comparative advantage). The author said "specializaion" but did not say it saves effort. The size of the saving (25 percent after 8 weeks) is ASSUMED.
- That "reliance is fine" means the other partner may stop doing the job at all. It could instead mean only that leaning on someone is not shameful.

### Rule 15. `R10a-check-in-first`

**Plain English (confirmed).** When a partner is unhappy, the first response is a soft check-in. This holds for any unhappiness: a role the other partner agreed to and did not do, or a general sense that things are not working. A check-in is a question ("is this still working for you?"). It is not a complaint, a fine or a penalty. It costs both partners a little time.

In the model, "general unhappiness" means a partner's own distress signal: several low weeks in a row, or rising non-offsettable load, or trust falling below a threshold. These are the same signals that today put "leave" on a persona's menu.

### Rule 16. `R10b-renegotiate-second`

**Status: Claude's ordering, not read back.** The author wrote "renegotiate or a soft check in", with "or". Later the author said "check in first". Renegotiation as a fixed second step is Claude's. This matters: in H32b, renegotiation undid most of what withdrawal did (docs/results/h32b.md).

**Plain English.** If the unhappiness continues within 8 weeks after a check-in (the role lapses again, or the partner is still distressed), either partner may reopen the terms early. They do not have to wait for the 13-week review. For a role, the renegotiation can keep it, move it to the other partner, share it, or drop it. For general unhappiness, any term can be reopened.

### Rule 17. `R10c-no-default-penalty-exit-last`

**Plain English (fines and exit-last confirmed, with the author's "i think"; the renegotiation step is Claude's).** A lapsed role carries no fine, sanction or forfeit by default. A fine on a lapsed role exists only if both partners explicitly choose it as a negotiated term (the author: "allowed only by mutual choice i think"). While such a fine stands, both partners pay a small scorekeeping cost each week. Leaving because of unhappiness is the last step, after a check-in and, in Claude's draft, a renegotiation. This is how a partner responds, not a limit on leaving: rule 11 (a partner may leave whenever they like) still holds in full.

**The author's words (rules 15 to 17).**

> renegotiate or a soft check in i think not leaving right away but utlimtaly what the person does is the sterongest signal

> reliance is fine its the guilt and scorekeeping i dont like

> check in first for general unhappiness too

> allowed only by mutual choice i think

**Answered by the author.** Check-in comes first (the author's "check in first"). Exit last is how agents behave, not a ban, and free exit stands. The ladder covers general unhappiness too. A fine on a lapsed role is allowed only by mutual choice ("i think"). Not answered: whether renegotiation must come between check-in and exit. The first draft's "no fine, even if both would like one" was too strong and is withdrawn.

**Still Claude's interpretation (rules 15 to 17).**
- The 8-week window for "again". ASSUMED.
- What counts as "general unhappiness" in the model (the existing distress signals, listed under rule 15).
- The renegotiate rung and its place in the order. The author wrote "or"; the fixed order is Claude's.
- Leaving over unhappiness comes only after a failed renegotiation or continued distress after it. A severe case (non-offsettable load of 0.4 or more, ASSUMED) may still skip the ladder. This severe-distress skip was never read back; see the open questions.
- The check-in cost (a small amount of time) is ASSUMED. A check-in that costs nothing would be free to repeat, which reads as nagging.
- That the scorekeeping cost on a chosen fine is the same one as in fix 4 (scaled by how little the persona values security).

## Trust mostly from actions (a mechanism, not a card)

**Plain English (confirmed, changed).** Trust moves mostly because of what a partner does. Keeping a role or a commitment raises the other's trust a little each week. Lapsing a role lowers it a little. Breaking a chosen commitment lowers it a lot, as in v2.2. What a partner says moves trust a little: answering a check-in or promising to do better gives a small gain that is taken back if the next actions do not follow.

**The author's words.**

> utlimtaly what the person does is the sterongest signal

> maybe we have to test? but my intutions is mostly actions

**Answered by the author.** "Mostly actions" is the default, as the author's intuition ("my intutions is mostly actions"), with "maybe we have to test?". The first draft's "only actions" is withdrawn as the default. Because the author said "maybe we have to test", the retest compares three versions in a descriptive arm: only actions, mostly actions (the default), and words count until tested (a promise moves trust as much as an action until a later action contradicts it).

**Still Claude's interpretation.**
- What a "word" is in the model. Agents cannot lie or mean things, so a word is an event: agreeing to terms, answering a check-in, or a stated promise to resume a role.
- ASSUMED numbers beside the v2.2 trust block: a kept role week adds 0.002, a lapsed role costs 0.05, a broken commitment still costs 0.3. A word adds 0.01 in "mostly actions" (a fifth of a lapse), 0 in "only actions", and 0.05 in "words count until tested". A word's gain is removed if a lapse or breach follows within 8 weeks.
- A lapse costs less than a breach because a role is a habit the partners chose, not a promise about a specific request. That ranking is Claude's.

## Rule 18. `R11-decency-floor`

**Plain English (confirmed, changed).** Everyone treats everyone they interact with with politeness and common decency. "On common ground" means anyone the agent interacts with: the partner, the friend, and in the network lever every external bond. In this world decency means three things:

1. No one acts only to lower another person's pleasure.
2. No one repeats a request the other has just refused, for 4 weeks.
3. A refusal or a check-in is given openly, never by silence.

Beyond this floor, the model's default is that nobody owes anybody anything except what they negotiated (as in v2.2). That default is Claude's. The author called this region "tricky" and said "Each person's internal calculus will be different". It is open, not settled at zero.

**The author's words.**

> At the very least we owe politeness and common decency if we are both on common ground. However beyond that I feel like it becomes tricky. Each person's internal calculus will be different but I think it's most helpful to think that you can't complain about doing things for friends

And from the original seed (2026-11-10):

> no one owes anyone anything day to day except for what they have negotirated

> all three feel right, common ground is anyone you interact with

**Answered by the author.** All three parts "feel right". "Common ground" is anyone you interact with, not only the shared home or pot. The author did not answer what is owed beyond the floor.

**Still Claude's interpretation.**
- The model has no speech, so politeness can only show up as what people do.
- Part 1 already holds in v2.2 for contact and spending (rule 9, no vetoes). It adds nothing for the hand personas. It matters only for pressing personas.
- Part 2 is the one new constraint. It stops pressing (asking again and again after a no). The 4 weeks are ASSUMED. In this world only the partners make requests, so widening common ground changes the code only where Friend C or an external bond can refuse something (today they cannot; phase 2 checks).
- Part 3 changes nothing in the code. The world already makes every refusal explicit.
- "You can't complain about doing things for friends" is not turned into a rule. Claude reads it as: what you chose to do for a friend is not a debt. That fits "no scorekeeping" and the evaluator flag below.

## Evaluator flag (not a rule): chosen versus slid-into sacrifice

**Status: Claude's draft, never read back.**

**Plain English.** The evaluator watches each partner over time. It raises a flag when one partner, for a long stretch, gets less from the household than they would get living apart, while the other partner gets more, and the first partner never chose this. "Chose" means the partner did something that set it up: proposed or accepted a term, made a commitment, gave a gift, took on a role, or kept the terms after a check-in. If they did choose it, the evaluator records it as a chosen sacrifice and does not flag it.

The flag changes nothing in the run. It is a line in the report, like the freedom score.

**The author's words.**

> You can choose to give a part of yourself, but you have to be okay with that and actively choose it, not have it be chosen for you or just slid into.

> lopsided is normal for a while as long as it evens out

> idk if they need similkar gains but i guess they just need to be better off within the rleatiniship maybe?

**Claude's interpretation.**
- "Be okay with that" cannot be measured: agents feel nothing. Claude uses a recorded choice event as the stand-in.
- "A long stretch" is 26 weeks (ASSUMED), because the author said lopsided is normal "for a while".
- "One-way" is measured against each partner's own outside option (the value of living apart), following the Q4 answer "better off within the relationship". The author hedged that answer ("i guess", "maybe?") and it was never read back. Equal gains may not be required.
- The pleasure of giving (Q8) is counted in the partner's pleasure when the model has it. Today it does not, so a generous partner may be flagged too often.

## Questions: settled and still open

Answered by the author on 2026-11-11 (the author's hedges kept):

- The ladder: check-in first and leaving last, as agent behavior and not a ban. Free exit stands. It covers general unhappiness too. The renegotiate step in between is Claude's ordering, not the author's.
- Fines on lapsed roles: "allowed only by mutual choice i think", with the scorekeeping cost (the cost is Claude's).
- Trust: "mostly actions" as the author's intuition, "maybe we have to test?"; the three versions are compared in the retest.
- Decency: all three parts; common ground is anyone you interact with.

Never read back: rule 14 (roles), the slid-into flag, the fixed check-in, renegotiate, exit order, and the severe-distress skip.

Still open. These do not block the retest; until answered, v2.3 runs with Claude's defaults, named here.

1. Roles: are the three jobs (earning, paying bills, planning time together) enough to start? Default: yes.
2. The ladder: may a partner in severe distress skip straight to leaving? Default: yes, at a non-offsettable load of 0.4 or more (ASSUMED).
3. The flag: is a recorded choice a fair stand-in for "actively choose it"? Is 26 weeks a fair "for a while"? Default: yes, 26 weeks.
4. Variants: should v2.3 also have a free-exit variant (no binding stay commitments)? Default: bindable only, because the v2.2 headline used bindable.
5. The ladder order: must renegotiation come between check-in and leaving? Default: yes (Claude's). The author wrote "renegotiate or a soft check in".
6. Beyond the decency floor: what is owed? Default: only what was negotiated (Claude's). The author called it "tricky" and person-specific.
7. Rule 14: does "reliance is fine" mean the other partner may stop doing the job, or only that leaning on someone is not shameful? Default: the first (Claude's).

## What is not a card

Trust, the exit floor, the 13-week reviews, the check-in cost and the specialization saving are mechanisms in the world. The slid-into flag is in the evaluator. None of them is a rule card. Their numbers are ASSUMED and listed in docs/results/household-fixes-design.md.
