# Seed v2.3 read-back (candidate, for the author)

**Status: candidate. The author has not confirmed any of this.** Nothing runs on v2.3 until the author confirms it. Seed v2.2 is the author's confirmed seed and is not changed: the `author_seed_v2_*` directories stay as they are. If confirmed, v2.3 will live in a new directory, `rules/household/author_seed_v23_bindable`.

Wording rule: agents feel nothing. "Pleasure" is a gloss for a modeled hedonic state (ADR 0010).

Sources. The author's exact words come from experiments/questions.jsonl, rows dated 2026-11-11 (topics open-question-Q2, Q4 and Q5). The read-backs of those answers are in docs/notes/hedonic-technology-synthesis.md, section 5. The decision to build this came from the author's answer "yes fix then retest if that is best course of aciotn" (experiments/changes.jsonl, 2026-11-11T02:06:55Z).

## What v2.3 is

Seed v2.3 is seed v2.2 (bindable) plus new rules. The 13 cards of `author_seed_v2_bindable` stay word for word as read back in docs/results/seed-v2.2-readback.md. Trust, the exit floor and the 13-week reviews stay as they are. The new parts are:

- rules 14 to 17 (roles, and the response to a lapsed role);
- rule 18 (the decency floor);
- one change to how trust moves (from actions, not words);
- one evaluator flag that is not a rule (chosen versus slid-into sacrifice).

Each part below gives the rule in plain English, then the author's exact words, then what is Claude's interpretation. Anything under "Claude's interpretation" is a guess about what the author meant, made so the rule can run in the model.

## Rules 14 to 17: roles and the lapse ladder

### Rule 14. `R9-may-agree-roles`

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

**Plain English.** When a partner does not do a role they agreed to, the other partner's first response is a soft check-in. A check-in is a question ("is this still working for you?"). It is not a complaint, a fine or a penalty. It costs both partners a little time.

### Rule 16. `R10b-renegotiate-second`

**Plain English.** If the role lapses again within 8 weeks after a check-in, either partner may reopen that role early. They do not have to wait for the 13-week review. The renegotiation can keep the role, move it to the other partner, share it, or drop it.

### Rule 17. `R10c-no-penalty-exit-last`

**Plain English.** A lapsed role never carries a fine, a sanction or a forfeit, even if the partners would like one. Leaving over lapsed roles is the last step, after a check-in and a renegotiation. This rule is about how a partner responds to a lapse. It does not limit leaving: rule 11 (a partner may leave whenever they like) still holds in full.

**The author's words (rules 15 to 17).**

> renegotiate or a soft check in i think not leaving right away but utlimtaly what the person does is the sterongest signal

> reliance is fine its the guilt and scorekeeping i dont like

**Claude's interpretation (rules 15 to 17).**
- The order. The author wrote "renegotiate or a soft check in". Claude put the check-in first because it is the softer step. The author may have meant either one, in any order.
- The 8-week window for "again". ASSUMED.
- "Not leaving right away" became "exit last". Claude kept leaving always allowed (rule 11), so exit last is a policy of the persona agents, not a ban on leaving. An agent will consider leaving over lapses only after a renegotiation has failed or lapses continue after it. It may still leave earlier for other reasons (distress, low trust), as in v2.2.
- "No penalty, even if both would like one" is Claude's reading of "the guilt and scorekeeping i dont like". It is a strong reading. The author may want a fine allowed when both partners choose it. See question 3 below.
- The check-in cost (a small amount of time) is ASSUMED. A check-in that costs nothing would be free to repeat, which reads as nagging.

## Trust from actions, not words (a mechanism, not a card)

**Plain English.** Trust changes only because of what a partner does. Keeping a role or a commitment raises the other's trust a little each week. Lapsing a role lowers it a little. Breaking a chosen commitment lowers it a lot, as in v2.2. What a partner says does not move trust: agreeing to terms, answering a check-in, or promising to do better changes nothing until the actions follow.

**The author's words.**

> utlimtaly what the person does is the sterongest signal

**Claude's interpretation.**
- "Strongest signal" became "the only signal". The author said strongest, not only. Words could count a little. Claude made them count zero because the model's agents cannot lie or mean things, so a "word" in the model carries no information anyway.
- New ASSUMED numbers beside the v2.2 trust block: a kept role week adds 0.002, a lapsed role costs 0.05 (a broken commitment still costs 0.3). A lapse costs less than a breach because a role is a habit the partners chose, not a promise about a specific request. That ranking is Claude's.

## Rule 18. `R11-decency-floor`

**Plain English.** Everyone on common ground treats each other with politeness and common decency. "On common ground" means the two partners, and the friend when the friend shares the home or the pot. In this world decency means three things:

1. No one acts only to lower another person's pleasure.
2. No one repeats a request the other has just refused, for 4 weeks.
3. A refusal or a check-in is given openly, never by silence.

Beyond this floor, nobody owes anybody anything except what they negotiated (as in v2.2).

**The author's words.**

> At the very least we owe politeness and common decency if we are both on common ground. However beyond that I feel like it becomes tricky. Each person's internal calculus will be different but I think it's most helpful to think that you can't complain about doing things for friends

And from the original seed (2026-11-10):

> no one owes anyone anything day to day except for what they have negotirated

**Claude's interpretation.**
- The three parts are Claude's translation of "politeness and common decency" into actions the model has. The model has no speech, so politeness can only show up as what people do.
- Part 1 already holds in v2.2 for contact and spending (rule 9, no vetoes). It adds nothing for the hand personas. It matters only for pressing personas.
- Part 2 is the one new constraint. It stops pressing (asking again and again after a no). The 4 weeks are ASSUMED.
- Part 3 changes nothing in the code. The world already makes every refusal explicit. It is listed so the author can see it is there.
- "Common ground" as "the home or the pot" is Claude's reading. The author may mean any shared space, or shared values.
- "You can't complain about doing things for friends" is not turned into a rule. Claude reads it as: what you chose to do for a friend is not a debt. That fits "no scorekeeping" and the evaluator flag below.

## Evaluator flag (not a rule): chosen versus slid-into sacrifice

**Plain English.** The evaluator watches each partner over time. It raises a flag when one partner, for a long stretch, gets less from the household than they would get living apart, while the other partner gets more, and the first partner never chose this. "Chose" means the partner did something that set it up: proposed or accepted a term, made a commitment, gave a gift, took on a role, or kept the terms after a check-in. If they did choose it, the evaluator records it as a chosen sacrifice and does not flag it.

The flag changes nothing in the run. It is a line in the report, like the freedom score.

**The author's words.**

> You can choose to give a part of yourself, but you have to be okay with that and actively choose it, not have it be chosen for you or just slid into.

> lopsided is normal for a while as long as it evens out

> idk if they need similkar gains but i guess they just need to be better off within the rleatiniship maybe?

**Claude's interpretation.**
- "Be okay with that" cannot be measured: agents feel nothing. Claude uses a recorded choice event as the stand-in.
- "A long stretch" is 26 weeks (ASSUMED), because the author said lopsided is normal "for a while".
- "One-way" is measured against each partner's own outside option (the value of living apart), following the Q4 answer "better off within the relationship". Equal gains are not required.
- The pleasure of giving (Q8) is counted in the partner's pleasure when the model has it. Today it does not, so a generous partner may be flagged too often.

## Open questions for the author

1. Roles: is "a negotiated term about who does which recurring job" what you meant by allocating roles? Are the three jobs (earning, paying bills, planning time together) enough to start?
2. The ladder: check-in first, then renegotiate, then leaving last. Is that order right?
3. Penalties: should a fine on a lapsed role be impossible (as written), or allowed when both partners choose it?
4. Trust: should words count for nothing, or for a little?
5. Decency: are the three parts what you mean by "politeness and common decency"? Is "common ground" the shared home and pot?
6. The flag: is a recorded choice a fair stand-in for "actively choose it"? Is 26 weeks a fair "for a while"?
7. Variants: v2.2 has bindable and free-exit variants. Should v2.3 also have both? This draft has only bindable, because the v2.2 headline used bindable.

## What is not a card

Trust, the exit floor, the 13-week reviews, the check-in cost and the specialization saving are mechanisms in the world. The slid-into flag is in the evaluator. None of them is a rule card. Their numbers are ASSUMED and listed in docs/results/household-fixes-design.md.
