# Test 3, security vs checking: design (ADR 0018)

Wording rule: agents feel nothing. "Security", "pleasure" and "suffering" are glosses for modeled numbers (ADR 0010).

Status: design only, 2026-11-13. Nothing here has been built or run. No code was changed. The prereg draft is [test3-security-checking-prereg-DRAFT.md](test3-security-checking-prereg-DRAFT.md). The author asked for this as docs-only parallel work: "yeah do research for that and the other tasks or whatever too we can parallel" (experiments/changes.jsonl, 2026-11-13T17:48:39Z). Test 3 was queued after H39 and real personas on 2026-11-11 ("yeah sounds good to me", experiments/changes.jsonl, 13:30:08Z).

Hypothesis: H28 in docs/hypotheses.md. Model version it would run under (ADR 0020): `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world · checking=<arm>`, with the v2.3 seed's ladders on where named.

## The question in one paragraph

Test 2 asks why a pair stays: because it is worth it, or because leaving costs too much. Test 3 asks why a partner feels settled: because the history of the relationship has earned it, or because they keep checking. A secure partner trusts on the record and does not monitor. A checking partner asks for reassurance, looks at the other's phone or location, or keeps score, and each check helps for a while. The test should tell the two apart the way test 2 tells "worth it" from "held". Then it should say what checking costs in pleasure and time, who pays, whether it holds anyone in, and whether some kinds of checking are domination.

## Where the ideas come from

Attribution follows docs/theory.md. **Author** means the author's logged words. **Claude** means a framing Claude proposed that the author has not confirmed.

- **Author.** Reassurance seeking was raised by the author in the 2026-11-10 claude.ai conversation "Attuning vs appeasing in relationships" (not archived in the repo, so not quoted here). The loop wording in ADR 0018 ("relief keeps it running and the fear is never tested") is Claude's paraphrase from that conversation.
- **Author**, on scorekeeping: "reliance is fine its the guilt and scorekeeping i dont like like this seems to be abou specializaion and having to allocate roles etc" (experiments/questions.jsonl, 2026-11-11T01:46:05Z).
- **Author**, on trust: "maybe we have to test? but my intutions is mostly actions" (experiments/questions.jsonl, 2026-11-11T02:33:56Z).
- **Author**, on check-ins: "check in first for general unhappiness too" (experiments/questions.jsonl, 2026-11-11T02:37:30Z).
- **Author**, on fines for a lapsed role: "allowed only by mutual choice i think" (experiments/questions.jsonl, 2026-11-11T02:34:43Z).
- **Author**, on protecting long projects: "its all about negoitation and trust again" (experiments/questions.jsonl, 2026-11-11T13:17:30Z).
- **Claude.** The four construct cards, the counterfactual measure, the threshold loop's parameters, and the classing of monitoring as possible domination.

## What the research says (checked 2026-11-13)

Each source below was checked to exist by web search and Crossref on 2026-11-13. The summaries are Claude's, from abstracts and secondary records. Read the primary text before citing a detail.

| Source | What it gives this design |
|---|---|
| Joiner, Metalsky, Katz & Beach (1999). Depression and excessive reassurance-seeking. *Psychological Inquiry* 10(4), 269–278. doi:10.1207/S15327965PLI1004_1 | Reassurance seeking that repeats because the answer is doubted as soon as it is given. It wears on the partner and invites rejection. This is the receiver cost and the "push out" channel. |
| Starr & Davila (2008). Excessive reassurance seeking, depression, and interpersonal rejection: a meta-analytic review. *Journal of Abnormal Psychology* 117(4), 762–775. doi:10.1037/a0013866 | Reassurance seeking is linked to rejection by others, with a small effect. A guide to size: the partner's cost should be small, not dramatic. |
| Rachman (2002). A cognitive theory of compulsive checking. *Behaviour Research and Therapy* 40, 625–639. doi:10.1016/S0005-7967(01)00028-6 | Checking as a self-perpetuating cycle: checking lowers confidence in memory and raises the felt need to check again. The source for the rising threshold. Note: it is about OCD checking, not partners. |
| Rempel, Holmes & Zanna (1985). Trust in close relationships. *Journal of Personality and Social Psychology* 49(1), 95–112. doi:10.1037/0022-3514.49.1.95 | Trust has three parts: predictability, dependability and faith. Faith goes beyond the evidence. The source for "security earned by history" against "security that must be verified". |
| Murray, Holmes & Collins (2006). Optimizing assurance: the risk regulation system in relationships. *Psychological Bulletin* 132(5), 641–666. doi:10.1037/0033-2909.132.5.641 | People balance the wish to be close against the fear of rejection, and doubt about the partner's regard makes them guard themselves. A model of why the same partner can be secure or checking. |
| Mikulincer & Shaver (2003). The attachment behavioral system in adulthood: activation, psychodynamics, and interpersonal processes. *Advances in Experimental Social Psychology* 35, 53–152. doi:10.1016/S0065-2601(03)01002-5 | Anxious attachment "hyperactivates": vigilance, seeking proximity and reassurance. Secure attachment rests on a felt base that does not need constant testing. The source for a per-persona anxiety trait. |
| Knee, Canevello, Bush & Cook (2008). Relationship-contingent self-esteem and the ups and downs of romantic relationships. *JPSP* 95(3), 608–627. doi:10.1037/0022-3514.95.3.608 | Self-worth that rides on the relationship swings with daily events, and those with more of it feel worse on bad days. The source for "held by checking": leaving would cost the checker their footing. |
| Tokunaga (2011). Social networking site or social surveillance site? Understanding the use of interpersonal electronic surveillance in romantic relationships. *Computers in Human Behavior* 27(2), 705–713. doi:10.1016/j.chb.2010.08.014 | Partner monitoring as its own behavior, separate from asking. The source for a "monitor" action distinct from a reassurance request. |
| Muise, Christofides & Desmarais (2009). More information than you ever wanted: does Facebook bring out the green-eyed monster of jealousy? *CyberPsychology & Behavior* 12(4), 441–444. doi:10.1089/cpb.2008.0263 | A loop: jealousy drives monitoring, and monitoring turns up ambiguous information that feeds jealousy. Cross-sectional, so the direction is open. The source for "a check can make it worse". |
| Clark & Mills (1979). Interpersonal attraction in exchange and communal relationships. *JPSP* 37(1), 12–24. doi:10.1037/0022-3514.37.1.12 | Communal relationships give in response to need. Exchange relationships give in response to benefits received. A prompt repayment lowers liking when a communal relationship was wanted. |
| Clark, Mills & Powell (1986). Keeping track of needs in communal and exchange relationships. *JPSP* 51(2), 333–338. doi:10.1037/0022-3514.51.2.333 | People in communal relationships keep track of needs. In exchange relationships they keep track of inputs. Tracking needs is care. Tracking inputs is the tally. This splits "noticing" from "scorekeeping". |
| Stark (2007). *Coercive Control: How Men Entrap Women in Personal Life*. Oxford University Press (2nd edn 2023, https://academic.oup.com/book/55149). | Monitoring as a tactic of control. The source for the claim that some checking is domination, not only anxiety. |

What the literature does not give: numbers for this model. Every rate below is ASSUMED. The literature sets directions and rough sizes only (Starr and Davila's effect is small).

## 1. Construct cards

Each card says what the quantity encodes in this model and what it does not, as the prereg template requires.

### Security

**Encodes.** A new per-partner reading, *relational security* `rs` in [0, 1], separate from the existing `security` need. It has two parts. `rs_hist` is earned by the partner's observed actions: kept commitments, kept roles, honored requests, weeks with no lapse. These are the same events that move trust today. `rs_check` is a short-lived boost from checking that decays within about a week. A partner whose `rs` is below their own threshold `θ` carries an insecurity cost as offsettable suffering, scaled by a persona anxiety trait.

**Does not encode.** The existing `security` need in src/mar/hedonic.py. That one is a money buffer: it refills with assets (`sec_refill × assets / sec_assets`) and has nothing to do with the partner. Test 3 must not read it. Also not encoded: attachment style as a whole, childhood history, jealousy as an emotion, or security from friends and family. The reading is about one partner only.

**Why two parts.** Rempel, Holmes and Zanna separate trust built on a record from faith beyond it. The design needs to ask where a partner's security comes from, so the source must be kept apart in the state.

### Checking

**Encodes.** Three new actions a partner can take in a week, each costing time:
- `ask_reassure`: ask the partner for reassurance. Costs the asker a little time and the partner a little time and an answering cost. Adds to `rs_check`.
- `monitor`: look at the partner's information (location, messages, accounts) without asking. Costs only the checker's time. Adds to `rs_check`. With some chance it finds something ambiguous, and then `rs_check` falls instead (the Muise loop).
- `tally`: update a running account of who gave what, visible to both. Adds to `rs_check` when the account looks even. Costs both a scorekeeping friction, like fix 4's `keep_friction`.

The loop (ADR 0018, after Rachman): each check raises the checker's threshold `θ` a little, so the next week they need more to feel settled. Weeks with no checking let `θ` drift back toward the persona's baseline. A switch, `learning_blocked`, sets whether a checked week still teaches `rs_hist` anything. With it on, the fear is "never tested", in the ADR's paraphrase. With it off, checking is just a cost. Both are run, because the loss in the loop is otherwise built in (H28's pre-mortem).

**Does not encode.** The v2.3 check-in. A check-in in the current code (`HouseholdWorld._checkin`) fires once, when a partner is unhappy or a role lapses, and starts the ladder toward a review. The author wants it: "check in first for general unhappiness too". It is a repair step after an event, not checking. The measure must read it as zero checking unless it repeats with no event behind it (see known answer K4). Also not encoded: asking friends, googling or asking an AI. Those were the author's examples, but they involve no partner, and this world has no information sources outside the pair.

### Trust

**Encodes.** The existing `trust[r]` in household.py: r's trust in the other, starting at 0.7, falling 0.3 on a breach, rising slowly on kept commitments and honored requests, and on words if `trust_words` is set. It scales willingness to accept requests below 0.5, blocks new commitments below 0.4, and counts as distress below 0.15.

**Does not encode.** How settled a partner feels. Trust is a belief about the other's reliability. Security is the partner's own state. They can come apart, and the test depends on that: an anxious partner can trust fully and still check (Mikulincer and Shaver's hyperactivation), and an avoidant one can trust little and never check. The design keeps trust as it is and uses it as the stock that security is read against. It also notes a known gap: trust never fell in the pleasure demonstration (0 breaches in 691 household runs, docs/results/pleasure-demo.md). If trust never moves, "security built by history" is untested. The test needs worlds where breaches and lapses happen.

### Scorekeeping

**Encodes.** A running account between partners that each one's weekly choices can see, and that charges both a small friction while it runs. It pulls behavior: partners act partly for the account. This is H39's "running tally" (the maker's choice sees its credit) plus fix 4's scorekeeping friction (`keep_friction × (1 − security weight)` while fines are on).

**Does not encode.** Settling up at exit. H39 found that crediting only at exit did nothing (G − Z −0.0004), and the author's exit terms rely on it. Splitting at the door is not scorekeeping. Also not encoded: guilt as a feeling, or the partner's moral judgment. Clark, Mills and Powell's split holds here: keeping track of needs is care, and keeping track of inputs is the tally. Only the second is scorekeeping.

## 2. The measure

The lead measure follows test 2's method: replay with the mechanism removed and see what changes.

**Checking dependence (lead).** For each partner-week inside a household, recompute `rs` with that week's `rs_check` set to zero. Class the week:
- **secure:** `rs_hist ≥ θ`. History alone is enough.
- **held up by checking:** `rs_hist < θ ≤ rs_hist + rs_check`. Only the checking keeps the partner above their threshold.
- **insecure:** `rs < θ` even with checking.

Report the share of each, per household and per partner, with the ADR 0015 interval resampling whole pairings. The test 3 line in the evaluator is "checking-dependent share" beside "secure share".

**Checking share of weeks (second measure, the template's "one other way").** The share of partner-weeks with at least one checking action (`ask_reassure`, `monitor` or a `tally` update). Simple and visible, but it counts a single anxious week the same as a habit, and it calls any check "checking" whatever the security behind it. If the two measures disagree, the conclusion is fragile and must say so.

**The ADR's original line, kept.** Share of security from checking: the mean over weeks of `rs_check / rs`. Reported beside, since ADR 0018 names it.

**Against the trust stock.** Each line is reported beside mean trust, and the correlation across households is reported. If checking dependence is just low trust renamed, the correlation will be near −1 and the known answers K2 and K3 will fail. That is a finding against the measure, not a nuisance.

**What checking costs.** All in the existing pleasure scale (ADR 0019, saturating), as lifetime pleasure (ADR 0017):
- *Time.* Checking blocks per week, and what they displaced (together, rest, work), from the week rows.
- *The checker's pleasure.* The same household with checking unavailable, against with it, paired by pairing and seed. The informative number is the net: relief bought against time spent and threshold raised.
- *The partner's pleasure.* The answering cost and the partner's own friction from being asked or tallied. This is the receiver side in docs/theory.md and the rejection channel in Joiner et al. Reported separately, since the evaluator's verdict reads the worse-off partner.

**Does checking hold people in?** Two lenses, both readings, not the stay rule itself.
- *Held by anticipated insecurity.* At each hybrid reading, the checker compares staying with leaving over sampled futures. Replay the reading with the post-exit insecurity term removed (leaving resets `rs_hist` and keeps the raised `θ`, so a checker expects to feel unsettled alone). A staying week that turns into a leave is "held by checking". This is Knee et al.'s contingent self-worth as an exit cost.
- *Pushed out.* The partner of a checker carries the answering cost. Count the partner's leaves and readings that say leave, against the matched secure household. Joiner et al. and Starr and Davila predict a small push.

The two can cancel. Both are reported. Neither is assumed to win.

**Is checking domination?** Under ADR 0014, freedom counts blocks on another's options, and withdrawal is not domination. A check is not a block, so the current liberty measure cannot see it. The design adds one thing: a `monitor` capacity that the monitored partner did not agree to, or cannot switch off, counts as exposure in the domination penalty, whether or not it is used. This is Pettit's "the kind master is still a master", which ADR 0014 already adopts. Monitoring that both agreed to and either can end is agreement-dependent and is not counted. `ask_reassure` is never domination: the partner can refuse. The tally is not domination by itself. This classing is Claude's and is question 1 for the author.

## 3. Known-answer cases

Each must come out right before any real run. All are scripted, cheap and free.

| ID | World | Known answer |
|---|---|---|
| K1 | **Planted checking household.** Partner A: anxiety trait high, threshold `θ0` above A's starting `rs_hist`, scripted to check whenever `rs < θ`, `learning_blocked` on. Partner B: secure. Same economy, same trust start, no breaches. | A's checking-dependent share ≥ 0.5. B's ≤ 0.02. A's checking share of weeks ≥ 0.5. |
| K0 | **Secure household.** Both partners' `θ0` below the starting `rs_hist`. Checking available. | Checking-dependent share ≤ 0.02 for both, checking share of weeks 0. |
| K2 | **High trust, still checking.** As K1, but A's trust pinned at 1.0. | A still reads checking-dependent ≥ 0.3. Shows the measure is not trust. |
| K3 | **Low trust, no checking.** Both secure by trait, but B breaches twice early, so A's trust falls to about 0.3. A never checks (avoidant script). | A reads insecure or secure, never checking-dependent. Shows low trust alone does not read as checking. |
| K4 | **The author's check-in.** Seed v2.3 with its ladders, secure personas, a role lapse at week 20. | The lapse's one check-in reads as zero checking-dependent weeks. A rule set the author wants must not fail test 3 for a repair step. |
| K5 | **Verify, then trust.** A starts below threshold and checks, `learning_blocked` off, no breaches. | Checking-dependent share falls over time and the late-run share is ≤ 0.05. Shows the measure sees security being earned (Rempel et al.'s predictability turning into faith). |
| K6 | **Loop control.** As K1 with the threshold rise set to 0. | A's checks per week do not rise over the run. Shows the rising-checks pattern comes from the loop and not from the measure. |

K1 against K0 is the main separation, as the trap against the baseline was for test 2. K2 and K3 are the cases that make it a test of security and not of trust.

## 4. What the model needs that it does not have

Everything below is new, behind a flag that is off by default (`FixConfig.checking = None`), with fingerprints pinned before the change so old runs reproduce byte for byte (ADR 0020).

1. **Relational security state.** `rs_hist`, `rs_check`, `θ` per partner, in the world beside `trust`. Updated from the events that already move trust (kept, honored, lapse, breach), so no new event source is needed.
2. **A persona anxiety trait.** `anx` per persona, drawn from a stated distribution (the parallel persona-generator design is the natural home). It sets `θ0`, the insecurity weight, and how readily a partner checks. Mikulincer and Shaver ground the direction, not the numbers.
3. **Three checking actions.** `ask_reassure`, `monitor`, `tally` in the household's extra actions (`EXTRA_ACTIONS`), with time costs in the unit budget and the partner's answering cost in their friction. The `monitor` action needs an ambiguity draw with probability `q`.
4. **The threshold loop and its switches.** `θ` rises by `δ` per check and decays by `ρ` per unchecked week. `learning_blocked` on or off.
5. **A tally visible to agents.** A running account both partners' weekly choices can see, with fix 4's scorekeeping friction. H39 built a one-sided version for makers; this needs it for all contributions.
6. **Norms to test.** An answer-once norm (the partner answers the first request in a window, then declines kindly, and the asker's `θ` decays); a no-monitoring card; a monitoring-by-agreement card that either partner can end; a no-tally card with settlement only at exit.
7. **The evaluator lines.** Checking-dependent share, secure share, checking share of weeks, share of security from checking, checking time, net pleasure after checking for both partners, held by checking, pushed out.
8. **A liberty hook.** Unconsented or unrevocable monitoring counts as an exposure item in src/mar/liberty.py's domination penalty.
9. **Observer rows.** `rs`, `θ`, checks and their kind in the week rows and the pattern atlas, so stories can be read for the spot-check.

Suggested order, after test 1's example: build a standalone exact model first (`src/mar/checking.py`, two people, a few dozen weeks), get K0 to K6 and the agent comparison there, and only then port to the household. Test 1 is still not in the household world. Doing the cheap version first keeps that from happening here too.

## 5. Existing results it could reinterpret

None of these changes as a result of this design. Each is a place the test 3 lens would read differently.

- **H39 and H39b, the running tally.** The tally's pull on behavior lowered pleasure a little (BP − G −0.0045 in H39, "fragile, not gone" in H39b), and crediting only at exit did nothing. Under test 3 this is the scorekeeping card's first data point, and the gift-at-exit rule is the secure version. H39's credit did not encode scorekeeping friction (its construct card says so), so test 3's tally is a stronger version.
- **Fix 4's scorekeeping friction.** Fines already carry `keep_friction`, scaled down for personas who value security. Test 3 would read it as a tally cost and ask whether it ever buys security.
- **The v2.3 check-in ladder.** In the v2 retest, 537 of 774 leaves under v2.3 came after a check-in and an early review (M7). Test 3 reads those check-ins as repair, not checking (K4). If a rule set made check-ins repeat with no event, the measure should flag it.
- **trust_words (v2 retest, C4).** "Words count until tested" kept trust higher (lowest trust 0.86 against 0.76 for actions only) and barely moved pleasure. Under test 3, trust from words is reassurance-based security and trust from actions is security built by history. The author's "mostly actions" is the secure setting.
- **The pleasure demonstration, D5.** Trust never fell, so "security built by history" has never been tested. The test 3 worlds must include lapses and breaches, or K5 and K3 cannot run.
- **Test 2's blind spot.** The stay test found "held by isolation: not measurable here" because the contact veto is inert (limit 2). Monitoring is the information side of the same control. Test 3's held-by-checking lens and the monitoring exposure give a partial view of what test 2 cannot see.
- **Test 1, liking vs wanting.** The checking loop is the same shape as wanting without liking: relief pulls the next check while the felt security does not grow. The closure ritual helped there. The answer-once norm is the relationship version of a closure, and test 3 can check whether it works the same way.

## 6. Which agent model it needs

**For the household run: the hybrid, as in H41.** `agent_values="hybrid"`, saturating scale, bills that hurt, `satiety_expect="world"`, `hybrid_w="persona"`, `hybrid_readings="world"`. It is the only agent whose big choices (form, stay, leave) pass a forecast test against held-out futures, and the suffering weight matters here, since insecurity is suffering (docs/results/hybrid-agent.md, Amendment 3; docs/results/formation-check-3.md).

**The weekly checking choice needs care.** Checking is a routine action, so the hybrid's one-week routine decides it. A one-week routine values a check at its relief this week and never sees the threshold it raises. That is the greedy agent the loop catches, and so the loss is in by construction. Test 1 handled the same problem with three agents side by side, and test 3 should too:
- **Relief-greedy:** the hybrid routine as it is. Checks when this week's relief beats the time.
- **Lifetime planner:** in the standalone exact model only, an optimizer over the whole run that sees the threshold. If it still checks, checking is worth it in this model.
- **Scripted checker:** checks whenever `rs < θ`. Used for the known answers.

The headline compares relief-greedy against the planner and against checking unavailable. "Checking costs pleasure" is only informative where the planner does not check and the greedy agent does.

**Persona caveat.** The hybrid's known answer K1 for the trap failed as preregistered, because it pays to get out of the trap (hybrid-agent.md). An agent that leaves bad households easily may also leave a checking partner easily. That is a result, not a bug, but it means "held by checking" may read near zero for this agent.

## Open choices for the author

1. Is monitoring that the other partner did not agree to, or cannot switch off, domination even when it never leads to a block? Should agreed and revocable monitoring (say, shared locations) count as fine?
2. Is a tally that both partners agreed to still the scorekeeping you dislike, or is it the guilt that comes with it? The model can charge friction for the tally itself, or only when a partner falls behind on it.
3. Should "secure" mean the partner never checks, or that checking fades as the record builds (K5)? The first calls every new relationship insecure. The second lets "verify, then trust" pass.

## Limits stated now

- Agents feel nothing. Relational security, anxiety and relief are modeled numbers with ASSUMED rates. The literature gives directions only.
- "Partner" means one fixed co-resident partner (limit 12). The attachment and monitoring research is mostly about romantic couples, and romance is not modeled.
- No information exists outside the pair, so the author's own examples (googling, Reddit, AI) are not modeled.
- The contact veto is inert (limit 2), so monitoring cannot lead to isolation here. Its domination is counted as exposure, not seen in outcomes.
- The partner is a script or the hybrid (limit 1). Nobody learns that checking does not help, unless `learning_blocked` is off.
- One author and one model family (limit 6).
