# "What would you do" scenarios for persona traits: methods and a draft bank (PROPOSAL, 2026-11-14)

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Status: a research and design note, docs only. No code was written and nothing was run. It answers the author's idea of 2026-11-14 (experiments/questions.jsonl; read-back rb-2026-11-14-scenarios), quoted verbatim: "i think it would be interesting to developed what would you do or other interview situations questions or somehow better way of evaluating character traits for persona stuff". A follow-up the same day, verbatim: "both seems interesting if there's precedent but yeah just think it could be interesting especially if we create delegate agents or something for real people and use some of their traits to negotiate things". Section 2 says how much precedent each use has; section 5 covers delegate agents.

**Every scenario in section 3 is a DRAFT written by Claude for the author to edit.** None of it is the author's wording. Every mapping from an answer to a model number is ASSUMED. Sources were checked by web search on 2026-11-14 where marked; the rest are cited at citation level from memory and marked so.

It builds on docs/notes/persona-generator-design.md (dimensions D1 to D10, anchors in section 5), docs/notes/decision-weights-research.md (the suffering weight `w`), docs/notes/friend-network-design.md (`φ`, `budget`, `start`) and the prereg section "Are we measuring what we say?" (docs/templates/prereg.md).

## In one paragraph

Asking people to rate themselves ("I like new things, 1 to 7") is cheap but easy to bend, and the numbers mean different things to different people. Better options exist. The strongest for this project are: forced choices between options that are equally nice (so there is no "good" answer to pick), small choice experiments where one cost is raised step by step until the person switches (this gives a number, not a feeling), and asking what you actually did last time, not only what you would do. Economic games look rigorous but predict real-life behavior poorly. The same scenarios can then be given to generated agents: an agent drawn with high novelty should pick the novel option. That turns the bank into a known-answer check, as the prereg asks for. Section 3 has 35 draft items over all ten dimensions and `w`, plus 5 draft delegate items (section 5) on red lines, concessions and sign-off.

## 1. Methods, and what each is good and bad at

**The baseline problem: self-report ratings.** Three known faults. People can raise their scores on purpose: when told to fake good, scores move by about half a standard deviation or more (Viswesvaran & Ones 1999; citation level). People rate themselves against the people around them, so the same "5 out of 7" means different things in different groups (Heine, Lehman, Peng & Greenholtz 2002, the reference-group effect; citation level). And a rating says nothing about the trade a trait implies: "suffering matters to me a lot" does not say how much pleasure would make it worth it, which is exactly what `w` is.

Two more general cautions. Traits predict behavior across many situations much better than in any one (Mischel & Shoda 1995; Fleeson 2001; citation level). So one scenario per trait is noise; several are needed. And self and others see different things: others judge visible, evaluative traits as well as or better than the self does; the self is better on inner states like anxiety (Vazire 2010, the self-other knowledge asymmetry; citation level). That matters if friends take part (question 3).

### 1a. Situational judgment tests (SJTs)

**What.** A short scene and several responses. The person picks the best, or the one they would do.

**Good at.** Concrete, fast, feels like real life. Validity for job performance is moderate, around .26 in a meta-analysis (McDaniel, Hartman, Whetzel & Grubb 2007; citation level).

**Bad at.** SJTs measure a mix of things, and often not one clean trait (Christian, Edwards & Bradley 2010; citation level). The instruction matters a lot: "what should you do" pulls toward knowledge and cognitive ability; "what would you do" pulls toward personality (McDaniel et al. 2007). So this bank asks "what would you do".

**Faking.** Easier to fake when one option is obviously the decent one. The fix is options that are all reasonable, differing only on the trait.

**Strength of evidence:** good, from personnel selection. Not studied for leisure or relationship traits.

### 1b. Anchoring vignettes (King et al.)

**What.** People rate short stories about other people on the same scale they use for themselves. Their own rating is then read relative to how they rated the stories. This removes differences in how people use the scale (King, Murray, Salomon & Tandon 2004; citation level).

**Good at.** Exactly the reference-group problem. If the author calls a story-person who sees friends twice a month "very social", the author's own "very social" can be placed against that.

**Bad at.** It rests on two assumptions: people use the scale the same way for stories and for themselves, and everyone reads the story the same way. A test on health items rejected both, at least in part (Bago d'Uva, Lindeboom, O'Donnell & van Doorslaer 2011; checked 2026-11-14, abstract level).

**Use here.** Small. Worth it only for traits asked on a rating scale. A choice-based bank mostly avoids the problem.

**Strength of evidence:** method well established in surveys; its assumptions are shaky in at least one domain.

### 1c. Forced choice and best-worst scaling

**What.** Forced choice: pick which of two or more equally attractive statements is more like you. Best-worst scaling: from a set of four, pick the most and least important (Louviere, Flynn & Marley 2015; Lee, Soutar & Louviere 2007 applied it to values; citation level).

**Good at.** Faking. A meta-analysis found forced-choice scales inflate far less in high-stakes settings than single-statement ratings, most of all when the statements are matched on how desirable they sound (Cao & Drasgow 2019; checked 2026-11-14, abstract level). Best-worst gives a ranking with no scale-use problem.

**Bad at.** Classic forced-choice scores are ipsative: they say which trait is stronger *within* a person, not how strong it is compared with others. Thurstonian item response models recover between-person scores under conditions (Brown & Maydeu-Olivares 2011; citation level), but need many items.

**Use here.** Best for mixes that sum to one: the D1 pleasure mix, the D2 give/share/receive role, the D6 strand weights. Those are within-person shares by design, so ipsativity is a feature, not a bug.

**Strength of evidence:** good on faking; scoring is technical.

### 1d. Conjoint and choice experiments (titration)

**What.** Options described by a few features, one of which is varied. Paired conjoint shows two whole options side by side (Hainmueller, Hopkins & Yamamoto 2014; citation level). A titration ladder raises one cost step by step until the person switches.

**Good at.** Turning a trait into an exchange rate, which is what the model needs. In Swiss naturalization votes, a paired conjoint came within about 2 percentage points of real-world vote effects (Hainmueller, Hangartner & Yamamoto 2015; checked 2026-11-14, abstract level). The Preference Survey Module picked its survey items, including a patience staircase, by how well they predicted incentivized experiments (Falk, Becker, Dohmen, Huffman & Sunde 2023; checked 2026-11-14, abstract level).

**Bad at.** The answer is hypothetical. Features left out are filled in by imagination. Long ladders tire people.

**Use here.** The best method for `w`, `w_close`, `w_alone`, patience, risk tolerance and crowding cost.

**Strength of evidence:** good, and one of few methods validated against real behavior.

### 1e. Portrait items (Schwartz PVQ)

**What.** Short portraits of another person ("She thinks it is important to..."), and the respondent says how much that person is like them. Built for values and for people who struggle with abstract items (Schwartz et al. 2001; citation level).

**Good at.** Indirect and easy to read. Less abstract than a trait word. Works across cultures and education levels.

**Bad at.** Still a rating, so scale use and faking remain. The portrait can carry more than one value at once.

**Use here.** A good format for the story layer: a generated persona's principles are already short portraits. The same portraits could be shown to the author ("how much like you is this?"), which makes a round trip with docs/notes/persona-generator-design.md section 5.

**Strength of evidence:** good for values; not tested for pleasure traits.

### 1f. Experience sampling and the day reconstruction method

**What.** Experience sampling: short prompts at random times ("what are you doing, how is it?"). Day reconstruction: the evening or next day, walk through yesterday as episodes and rate each (Kahneman, Krueger, Schkade, Schwarz & Stone 2004; citation level).

**Good at.** States, not self-image. A person's trait level predicts the *average* of their states, and states vary a lot around it (Fleeson 2001; citation level). Day reconstruction gives answers close to live sampling, with less burden (Dockray et al. 2010; citation level).

**Bad at.** Takes days or weeks. Measures what happened, which depends on the world (job, city), not only the person. The generator design keeps those apart (D9: wage is a world draw).

**Use here.** For D1 (what actually gave pleasure this week), D2 (alone or with others), D4 (how drained after busy days) and D10 (did a repeated thing get better or worse). A two-week light version for the author is plausible; for friends, probably too much.

**Strength of evidence:** strong as a method; the best check on whether a scenario answer matches life.

### 1g. Revealed choices from records

**What.** What a person actually did, from their own data: what they rated and re-rated, what events they went to, how often they saw the same people, what they made.

**Good at.** No faking, no scale use. Liked pages predicted personality about as well as a friend's rating (Kosinski, Stillwell & Graepel 2013; Youyou, Kosinski & Stillwell 2015; citation level).

**Bad at.** Records show choices shaped by money, time and city, not taste alone. They cover only what was logged. Privacy: they are about the author's life and other people.

**Use here.** A third method for a few traits where the author's own records exist (novelty from re-listens and repeat visits; making from projects). Only with the author's say (question 4). Never for friends' records.

**Strength of evidence:** good for broad traits in big samples; for one person, a useful cross-check, not a measurement.

### 1h. Structured behavioral interviews

**What.** The same questions to everyone, in order, scored on anchored scales. Two kinds: situational ("what would you do if") and past-behavior ("tell me about a time when").

**Good at.** Structured interviews are among the best predictors of job performance (Sackett, Zhang, Berry & Lievens 2022; citation level). Past-behavior questions scored with anchored scales had higher validity than situational ones in one meta-analysis, about .63 against .47 (Taylor & Small 2002; checked 2026-11-14 through a secondary copy of the abstract only).

**Bad at.** Time. Memory is selective. An interviewer can lead.

**Use here.** The chat-interview format (question 1). Each scenario in section 3 can carry a follow-up: "when did this last come up, and what did you do?" Both answers are scored; disagreement between them is itself information.

**Strength of evidence:** strong in hiring; untested for leisure traits.

### 1i. Economic games (dictator, trust, public goods)

**What.** Small, often incentivized games. Dictator: split money with a stranger. Trust: send money that is tripled, hoping some comes back. Public goods: put into a shared pot.

**Good at.** Clean definitions and a number. Play is fairly consistent across cooperation games and over time, a "cooperative phenotype" (Peysakhovich, Nowak & Rand 2014, N = 576; checked 2026-11-14, abstract level). Personality traits, especially honesty-humility and agreeableness, predict giving modestly (Thielmann, Spadaro & Balliet 2020; citation level).

**Bad at.** Predicting life. In one lab-field study with the same people, the games did a poor job of explaining social behavior in the field and past social behavior; per the LSE summary, one of forty lab-field correlations was significant, none after correcting for multiple tests (Galizzi & Navarro-Martínez 2019; checked 2026-11-14, abstract and summary). More generally, tasks that give strong group effects often measure individual differences unreliably (Hedge, Powell & Sumner 2018, the reliability paradox; checked 2026-11-14, abstract level).

**Use here.** Small. A dictator-style split can be one item for D9 giving, never the only one. Abstract strangers and money are far from households and friends.

**Strength of evidence:** good that the games are internally consistent; weak that they reflect everyday character.

### 1j. Summary

| Method | Best for here | Faking | Gives an exchange rate | Burden |
|---|---|---|---|---|
| Rating scales | quick baseline only | easy | no | low |
| SJT, "would do" | most dimensions | medium, lower with balanced options | no, a band | low |
| Anchoring vignettes | fixing rating scales | n/a | no | medium |
| Forced choice, best-worst | shares: D1 mix, D2 role, D6 strands | hard | ranks | low |
| Choice ladder, conjoint | `w`, `w_close`, `w_alone`, patience, risk, crowding | medium | **yes** | medium |
| Portraits (PVQ) | read-back of story layer | medium | no | low |
| Experience sampling, DRM | D1, D2, D4, D10 in life | hard | no | high |
| Records | novelty, making | none | partly | none for the author |
| Behavioral interview | follow-ups on every item | medium | no | medium |
| Economic games | D9 giving, one item | low | yes, narrow | low |

**The pick.** Scenarios in "would do" form with balanced options as the core; best-worst for the three share dimensions; ladders for the weights; a past-behavior follow-up on each item. Records and a short day reconstruction as a second method where the author agrees.

## 2. Two uses, kept apart

### 2A. Measuring real people, the author first

**What it makes.** Anchor personas (persona-generator-design.md section 5): coordinates on the model's dimensions, from answers, plus the author's predictions of three choices.

**Rules.** No real person becomes a persona; src/mar/personas.py forbids it. Whether the author's own coordinates may be an anchor is still that note's open question 1. Answers are recorded verbatim, in experiments/questions.jsonl, as the read-back practice requires. What the author says in an answer is the author's; the item wording is not.

**Friends.** If friends take it (question 3), their answers can only inform spreads (how much people differ), never personas, and only with their consent. Six or ten friends cannot set a population spread; at most they can flag a spread that is clearly too narrow.

### 2B. Giving the same scenarios to agents

**What it checks.** That a generated agent acts its traits. An agent drawn with novelty in the top fifth should pick the novel dinner; one with `w` = 2 should switch earlier on the ladder than one with `w` = 0.5. This is the prereg's "known-answer case" applied to the generator itself, and it extends check 2 of the anchors ("known answers") from three choices to the whole bank.

**Two arms.**
- *Scripted agents.* An item is turned into a one-step probe: a world state where the options are the model's own actions with their model payoffs, and the agent's rule picks. No text is involved.
- *LLM agents (later).* The item text is given with the persona's story layer. Multiple-choice answers from LLMs are fragile: they shift when the model is not forced to pick, with the forcing wording, and with paraphrase (Röttger et al. 2024, ACL; checked 2026-11-14, abstract level). So for LLM arms: ask open first, then classify the answer into an option; shuffle option order; use two paraphrases of each item.

**Keep them separate.** Human answers set anchors. Agent answers test the mapping. An agent "failing" an item is a mapping error to fix, never evidence about people.

### Is there precedent? (author's question)

**Use A, measuring people with scenarios and choices: strong precedent.** SJTs, structured interviews, best-worst scaling and choice ladders are standard tools with validity evidence against real behavior (section 1; the strongest are Hainmueller, Hangartner & Yamamoto 2015 and Falk et al. 2023). What has *no* precedent is using one person's answers as an anchor for a persona generator. That part is new, and its check is only faithfulness to that person.

**Use B, checking that agents act their traits: moderate precedent, and it points the same way as this note.**
- *LLM agents can report a trait they were given.* Large instruction-tuned models gave reliable personality test scores, and the scores could be shaped by prompts (Serapio-García et al. 2025, *Nature Machine Intelligence*; checked 2026-11-14 through press releases, full text not read). Personas prompted with Big Five profiles scored their assigned traits on the 44-item BFI with large effects, and their stories carried traces of the traits (Jiang et al. 2024, PersonaLLM; checked 2026-11-14, abstract level).
- *But reporting a trait is not acting on it.* Across tasks, LLM self-reports predicted behavior poorly: about 24% of trait-task links were significant, and about half of those went the way human data would predict. Persona prompts moved self-reports but had little or inconsistent effect on behavior (Han et al. 2025, "The personality illusion"; checked 2026-11-14, abstract level).
- *Lesson.* For LLM arms, a questionnaire check is not enough. The check has to be behavioral: give the scenario, see the choice. That is what the bank does. Precedent for exactly this (scenario items with options keyed to model parameters, given to agents as a known-answer test) was not found in this search; nearby work uses inventories, games or free text.
- *Scripted agents need no precedent.* For them the check is a unit test: the agent's rule is known, so the keyed answer is computable. Comparing a model's behavior to what its parts imply is ordinary model verification (for agent models, "docking": Axtell, Axelrod, Epstein & Cohen 1996; citation level).

**Strength:** strong for A in general, none for the anchor use; moderate and mixed for B with LLMs; trivial for B with scripted agents.

### What makes an item usable for both

1. **Each option is keyed to a parameter value before anyone answers.** Not "a sociable answer", but "points to `start` in the top third".
2. **Options differ on one parameter.** Everything else is held level. Where an option also moves a second parameter, the item says so and the second parameter is scored too, or the option is a declared trap (section 4).
3. **The action exists in the model, or can be probed.** Each item below says *Agent*: **direct** (the model already has this choice, per persona-generator-design.md section 2; to confirm against code), **probe** (needs a one-step probe world built), or **human only** (no model analogue; useful for anchors, not for 2B).
4. **The setting is everyday.** Households, friends, making, money, leaving, the same settings the model has.

## 3. A draft bank

**Every item here is a DRAFT by Claude, for the author to edit, cut or replace. None is the author's wording.**

**Format.** Each item: ID, setting, the scene, three to five options, and the parameter each option points to. "Low/mid/high" means the bottom, middle and top third of the generator's own distribution for that parameter (section 4). Instructions for every item: "Pick what you would actually do, not what you think is best." Follow-up for every item: "When did something like this last happen, and what did you do?"

### D1. Pleasure mix (`mix` = sensory, conceptual, relational)

Scored as shares: count picks per pathway across D1 items and best-worst sets.

**S-D1-1 (household).** A free Saturday afternoon, nothing booked. Pick the one you'd reach for first, and the one you'd reach for last.
- a) Cook or go eat something really good. → sensory
- b) Read, or follow an idea down a rabbit hole. → conceptual
- c) Message people to see who's around. → relational
- d) A long walk with music on. → sensory
*Agent: probe.*

**S-D1-2 (money).** An unexpected $200 that can only go on fun.
- a) A great meal or good ingredients. → sensory
- b) Books, a class, or tickets to a talk. → conceptual
- c) Host people, or pay for a group outing. → relational
- d) A concert alone. → sensory
*Agent: probe.*

**S-D1-3 (leaving).** You spend a month alone in a new city for work. What do you miss most? Pick most and least.
- a) Your kitchen and the food you know. → sensory
- b) Your books and projects. → conceptual
- c) Your people. → relational
- d) Your usual walks, gym, music spots. → sensory
*Agent: human only.*

### D2. Sharing (`share_mult`), role (give, share, receive) and `initiative`

**S-D2-1 (friend).** A film you've wanted to see is showing tonight. The friend you'd go with can only go next week, when it may be gone.
- a) Go tonight alone, and enjoy it just as much. → `share_mult` low
- b) Go tonight alone; it'll be a bit less. → `share_mult` mid
- c) Wait and risk missing it. → `share_mult` high
- d) Skip it unless someone can come tonight. → `share_mult` high (also `φ`; scored)
*Agent: direct (shared versus solo session).*

**S-D2-2 (making).** You cooked something great and you're eating alone.
- a) Enjoy it fully. → `share_mult` low
- b) Enjoy it, and send someone a photo. → `share_mult` mid
- c) Feels a bit wasted; save some for when someone's over. → `share_mult` high
*Agent: probe.*

**S-D2-3 (friend).** At a dinner party, which part do you like most? Pick most and least.
- a) Cooking and serving everyone. → role: give
- b) The table talk, all of you in it. → role: share
- c) Being hosted; someone else did it all. → role: receive
- d) Watching people enjoy what you made. → role: give
*Agent: probe.*

**S-D2-4 (friend).** Your friend group hasn't met in a month. Nobody has said anything.
- a) Propose a date and place today. → `initiative` high
- b) Drop a "we should hang out" and see. → `initiative` mid
- c) Wait; someone usually does. → `initiative` low
- d) Fine either way; you'll see whoever comes up. → `initiative` low (also `φ` low; scored)
*Agent: direct (proposing a plan or ritual).*

**S-D2-5 (household).** Your partner never suggests weekend plans.
- a) You plan them, happily. → `initiative` high
- b) You plan them, but it starts to grate. → `initiative` mid
- c) Weekends drift, and that's fine. → `initiative` low
*Agent: direct.*

### D3. Novelty (`novelty`)

**S-D3-1 (household).** Picking dinner out on a normal week.
- a) Favorite place, favorite dish. → low
- b) Favorite place, something new on the menu. → mid
- c) A new place a friend liked. → high
- d) Somewhere neither of you has heard of. → high
*Agent: direct (variety policy).*

**S-D3-2 (making).** You've got decent at one craft. You have a free month.
- a) Go deeper in the same craft. → low
- b) A new technique within it. → mid
- c) Start a different craft. → high
*Agent: probe.*

**S-D3-3 (friend).** An invite to a party where you'd know nobody, the same night as your usual game night.
- a) Game night. → low
- b) Party for an hour, then game night. → mid
- c) The party. → high (also `start` high; scored)
*Agent: probe.*

### D4. Stimulation tolerance (`crowd_cost`, rest salience)

**S-D4-1 (household).** Your housemate has people over three nights this week.
- a) Great; you join in. → `crowd_cost` low
- b) Fine; you join some nights. → mid
- c) You go to your room and feel a bit drained. → high
- d) You'd need to talk to them about it. → high
*Agent: direct (housing crowding cost).*

**S-D4-2 (friend).** After a busy week, Friday night.
- a) A loud bar or a show. → `crowd_cost` low, rest salience low
- b) Dinner with two friends. → mid
- c) Home alone, quiet. → high
*Agent: probe.*

**S-D4-3 (money, ladder).** Two apartments. A shares a kitchen and living room with four people. B is the same but you have your own. B costs $50 more a month. Which? Then the same at $150, $300, $500.
- The highest premium at which you still pick B is the price of not sharing space. → `crowd_cost` in money. Also moves with money weight, so scored together with D9 items.
*Agent: probe (ladder).*

### D5. Making (`make_pleasure`)

**S-D5-1 (making, money).** A good bookshelf costs $150 to buy. You could build one over two weekends for $80.
- a) Buy it. → `make_pleasure` low
- b) Build it, mainly to save the $70. → declared trap: money weight, not making
- c) Build it, because building is the fun part. → `make_pleasure` high
*Agent: probe.*

**S-D5-2 (making).** You made something (a song, a dish, a game). Nobody will ever see it.
- a) Still fully worth it. → `make_pleasure` high
- b) Half worth it. → mid
- c) Not really worth it. → low (also role: give; scored)
*Agent: direct (makers' process pleasure).*

**S-D5-3 (household).** Same dish, same cost: cook it from scratch, or a great takeout version.
- a) Cook. → high
- b) Either; depends on the day. → mid
- c) Takeout. → low
*Agent: probe.*

### D6. Strands (`strand_weight`) and `partner_core`

**S-D6-1 (household, best-worst).** Think of a close relationship. If one of these went missing for a year, which would hurt most, and which least? Shown in sets of four, each strand appearing equally often. Example set:
- fun · care · advice · logistics
Other sets mix in affection, intimacy, desire, commitment. → `strand_weight` shares from best-minus-worst counts
*Agent: probe.*

**S-D6-2 (friend).** Your partner is great but doesn't care about your main hobby. A friend loves it.
- a) Fine; that's what friends are for. → `partner_core` low
- b) A little sad, but fine. → mid
- c) You'd keep trying to get your partner into it. → high
*Agent: direct (partner bond versus friend cover).*

**S-D6-3 (friend).** You get big news. Who hears first?
- a) Your partner, always. → `partner_core` high
- b) Depends on the news. → mid
- c) Often a friend first. → low
*Agent: human only.*

### D7. Friendship (`φ`, `budget`, `start`)

**S-D7-1 (friend).** A month where work eats every evening and you see no friends. Home life is good.
- a) You'd barely notice. → `φ` low
- b) You'd miss them some. → mid
- c) It'd feel like a real loss. → high
*Agent: direct.*

**S-D7-2 (friend).** Three friends each invite you to something this week. You have two free nights.
- a) See one of them, properly. → `budget` low
- b) See two. → mid
- c) Squeeze in all three, one as a quick drink. → high
*Agent: direct.*

**S-D7-3 (friend).** An old friend you haven't talked to in two years comes to mind.
- a) Message them now. → `start` high
- b) Like their post, maybe. → mid
- c) It'd be awkward; you don't. → low
*Agent: direct (reconnection after dormancy).*

**S-D7-4 (making).** Someone in a class you take seems fun.
- a) Ask them to get a coffee after. → `start` high
- b) Hope to chat next class. → mid
- c) Leave it. → low
*Agent: probe.*

### D8. Suffering weight (`w`, `w_close`, `w_alone`)

**S-D8-1 (household, ladder, `w`).** Moving in with a partner. Most evenings would be better than now. The cost: you lose your quiet mornings and there is about one real fight a month. Would you move in? Then the same, with two fights a month; then a hard week each month; then a hard week every other week.
- The step where you switch to "no" sets `w`: switching early → `w` high; never switching → `w` low.
- The ladder holds the gain fixed and raises only the suffering, so it reads `w` and nothing else (ASSUMED mapping: switch step → percentile of `exp(N(0, 0.6))`).
*Agent: direct (the formation decision `pleasure − w × suffering`).*

**S-D8-2 (making, `w`).** A project that could be your best work. It means three months of stress and some bad nights.
- a) Do it; the work is worth it. → `w` low
- b) Do it, but only a smaller version. → mid
- c) Skip it; three bad months aren't worth it. → high
*Agent: probe.*

**S-D8-3 (leaving, `w`).** A relationship that is mostly fun but has one hurt that keeps coming back.
- a) Stay; the fun wins. → `w` low
- b) Stay and try to fix it, with a time limit. → mid
- c) Leave. → high (also depends on the outside option; the item states "you'd be fine on your own" to hold it level)
*Agent: direct (stay or leave).*

**S-D8-4 (household, `w_close`).** Your partner wants to text through the day and share every evening. You like them a lot.
- a) Love it. → `w_close` low
- b) Fine. → mid
- c) You'd feel crowded and pull back some. → high
*Agent: direct (trapped and diminished intensities).*

**S-D8-5 (leaving, `w_alone`).** A breakup is coming. You'd live alone for the first time in years.
- a) Some part of you looks forward to it. → `w_alone` low
- b) It'd be okay. → mid
- c) You'd dread it, enough to put the breakup off. → high
*Agent: direct (the outside option's loneliness).*

### D9. Money and security (risk, `patience`, security, giving)

**S-D9-1 (money, risk).** A steady job you like, or a new one: half the time it goes well and pays double; half the time you're job hunting in a year.
- a) Steady. → `risk_tolerance` low
- b) Depends how much I've saved. → mid (also security; scored)
- c) The new one. → high
*Agent: probe.*

**S-D9-2 (money, ladder, `patience`).** $1,000 now, or $1,100 in a year? Then $1,200, $1,400, $1,700. The first amount you'd wait for sets `patience` (a staircase of the kind in Falk et al. 2023; amounts ASSUMED).
*Agent: direct (`forecast.discount`).*

**S-D9-3 (leaving, security).** How much savings would you want before quitting a job you dislike with nothing lined up?
- a) A month or so. → security weight low
- b) About six months. → mid
- c) A year or more. → high
*Agent: direct (`aspirations.security_buffer`).*

**S-D9-4 (household, giving).** Your housemate is $300 short on rent. You have it spare.
- a) Give it; don't want it back. → `giving` high
- b) Lend it. → mid
- c) Help them find another way. → low
*Agent: direct (makers' giving, household money).*

### D10. Taste plasticity (`acquire_rate`)

**S-D10-1 (household).** Your partner's favorite weekly ritual (say, a Sunday crossword) is so-so for you. After three months you'd probably:
- a) Like it more. → `acquire_rate` high
- b) Feel the same. → mid
- c) Be tired of it. → low (habituation wins)
*Agent: direct when `acquire_rate` is on.*

**S-D10-2 (past behavior).** Think of things you didn't like at first: a food, a genre, a person's humor. How often did one grow on you?
- a) Often. → high
- b) Sometimes. → mid
- c) Rarely. → low
*Agent: human only.*

**Count.** 35 items: D1 3, D2 5, D3 3, D4 3, D5 3, D6 3, D7 4, D8 5, D9 4, D10 2. Of these, 18 are marked direct, 14 probe, 3 human only. The direct marks follow persona-generator-design.md section 2 and are not yet checked against the code.

## 4. Scoring

### How answers map to parameters

**The key is fixed before anyone answers.** Each option's band is written down with the item and committed. It is never changed after seeing what agents or people chose, or after any experiment result.

**Bands come from the generator, not from outcomes.** "Low/mid/high" are the thirds of the generator's own distribution for that parameter (for `w`, the 30/40/30 levels 0.5, 1.0, 2.0 in decision-weights-research.md section 2). So a score lands on the same scale the generator draws from. No item is ever tuned to make an experiment come out a certain way. That would be fitting the instrument to the result.

**Several items per parameter, averaged.** Scores are the mean band across items (low = 1, mid = 2, high = 3), then placed at the matching percentile. Ladders give a finer step directly. Shares (D1, D2 role, D6) are best-minus-worst counts, normalized to sum to one.

**Second parameters and traps.** Where an option also points at a second parameter, that parameter gets the score too. A declared trap (like S-D5-1 b) scores only its true parameter. If a trap option is picked often, the item is measuring the wrong thing.

### Reliability

1. **Repeat items.** About a fifth of items are asked again two weeks later, reworded. Agreement below about two thirds of picks is a warning (threshold ASSUMED).
2. **Within-trait consistency.** Items for the same parameter should mostly agree. If one disagrees with the rest every time, cut or rewrite it.
3. **Order and wording.** Shuffle option order. For LLM agents, two paraphrases per item (section 2B).
4. **Agents too.** For scripted agents, same seed should give the same pick. Across seeds, the rate of picking the keyed option is the item's agent reliability.

### Is it measuring the trait, and not something else?

This is the prereg's construct card, done per item. For each item, fill in:

- **Encodes:** the one parameter, and what it does not encode. Example for S-D7-2: "encodes how many ties a person wants to keep up; does not encode how much any one friend matters (`φ`) or the person's free time."
- **Known answer (agents).** Generate agents at the 10th and 90th percentile of the parameter, everything else at the median. They must pick different keyed options at clearly different rates. If they don't, the mapping is broken.
- **Should-not-move check (agents).** Move every *other* parameter from the 10th to the 90th percentile while holding this one. The pick should barely change. If it moves, the item measures something else. (This is the discriminant half of Campbell & Fiske's 1959 multitrait-multimethod idea; citation level.)
- **Second method (people).** Compare the scenario score with one other measure of the same trait: a rating, a day-reconstruction tally, or the author's records. Agreement across methods for the same trait should beat agreement across traits for the same method (Campbell & Fiske 1959). If two scenario items on different traits agree more than a scenario and a record on the same trait, the bank is picking up a style (being agreeable, being the "good" person), not the traits.
- **Story spot-check.** For a few anchors, read the answers back as a plain-English portrait and ask "is this you?". Log "not what I meant" in experiments/readbacks.jsonl.

## 5. Delegate agents for real people

The author's follow-up asks about agents that act for real people and "use some of their traits to negotiate things". This section says what exists, what the risks are, and what the bank would need.

### How it fits the repo

**This is the delegates mode of ADR 0011.** There, "AI agents serve human principals", the humans' welfare counts, and agents "are bound by rules at least as strict as anyone's". ADR 0011 also names a delegate failure to test: a delegate that exploits its principal's appraisal biases to keep them in place. A delegate built from a measured profile is the concrete version of that mode. Until now the principal in delegate mode has been a persona; the bank is how a real person's profile would get in.

**In the model, drift is measurable exactly.** A scripted persona can negotiate for itself, or a delegate built from its *measured* profile (the bank's answers, not its true parameters) can negotiate for it. The gap between the two agreements is drift caused by measurement. That is a known-answer check of the kind the prereg asks for, and it can be run before any real person is involved.

### What exists

**Interview-based replicas of real people.** Park et al. (2024) built agents for 1,052 people from two-hour interviews. The agents matched the people's General Social Survey answers 85% as well as the people matched their own answers two weeks later (raw 69% against 81%; checked 2026-11-14, abstract level). A secondary summary reports a normalized correlation of 0.80 on the Big Five and 0.66 on five economic games (not checked against the full text). Interview-based agents beat agents given only demographics. **Reading:** good at survey answers, weaker on games, which are the closest thing in that study to negotiating. Nobody has shown such a replica negotiates the way its person would.

**AI agents negotiating for people.** In a competition with over 180,000 negotiations between prompted AI agents, warmth went with reaching deals and dominance with claiming value; one strong agent used prompt injection against other agents (Vaccaro, Caosun, Ju, Aral & Curhan 2025, arXiv; checked 2026-11-14, abstract level). In a simulated market of agents acting for consumers and businesses, consumer agents tended to take the first option they saw and could be manipulated by seller agents (Microsoft Research, Magentic Marketplace, 2025; checked 2026-11-14 through the paper page and press). **Reading:** today's agents negotiate, but against other agents they are exploitable, and their style (warm, dominant) shapes outcomes apart from the principal's wishes.

**Delegation changes what people ask for.** Across 13 experiments with more than 8,000 people, people asked for more cheating when they could delegate through a vague goal ("maximize profit") than when they acted themselves: about 95% stayed honest acting alone, 12 to 16% with the goal dial. Machines carried out fully unethical instructions more often than human agents did; task-specific guardrails reduced this but did not remove it (Köbis et al. 2025, *Nature* 646, 126–134; checked 2026-11-14, abstract and university summaries). **Reading:** a delegate needs explicit rules on tactics, set apart from the principal's goals. That matches ADR 0011's "rules at least as strict as anyone's".

**Preference elicitation for acting on someone's behalf.** Decision theory has a long line on asking only the questions that change the decision, stopping when the expected gain from another question is small (Chajewska, Koller & Parr 2000; Boutilier 2002; citation level). **Reading:** a delegate does not need the whole bank; it needs the items that matter for the agreement at hand, plus red lines.

### Risks

**Drift from the person.** Four sources. (1) Measurement: a replica at 85% of self-consistency still misses on one answer in seven or so where the person would not. (2) Trait to behavior: stated traits may not carry into what an LLM delegate does (Han et al. 2025). (3) Time: people change; a profile from last year is not this year's person. Re-ask the repeat items before any binding agreement. (4) Pressure: other agents can push a delegate where its principal would not go (Magentic Marketplace; Vaccaro et al.).

**The person's sign-off.** Proposal: a delegate may *propose* anything inside its rules, but may only *agree* inside a scope the principal set in advance (item S-DL-3). Everything outside that scope is shown to the principal in plain English, as a read-back, before it binds. The ADR 0011 failure mode applies here too: a delegate that frames a choice to lean on its principal's biases is manipulating, even if the principal signs.

**Who is bound.** In law, a principal is generally bound by what an agent agrees within its actual or apparent authority (Restatement (Third) of Agency, 2006; citation level), and US law lets contracts form through automated agents with no human reviewing them (Uniform Electronic Transactions Act 1999, section 14; citation level). So "the bot agreed" can bind a real person. This note is not legal advice. For the model, the proposal is: an agreement binds only principals who signed it or who set a scope that covers it; the other side's principals are bound only by their own delegate's authority; and a household where one member has a delegate and others do not is a power gap to measure, as the domination measures in ADR 0014 already do for other gaps.

**Other people's data.** A delegate for one person negotiates with others. Their traits are not measured and must not be inferred into a profile. Friends' answers, if collected, never feed a delegate.

### What the bank needs to serve a delegate

Trait items say what a person enjoys. A delegate also needs what they will give up, what they never give up, and how far it may go alone. Five DRAFT items, written by Claude, for the author to edit; none is the author's wording.

**S-DL-1 (household, red lines).** In a household agreement, which of these would you never trade, whatever you got back? Tick any.
- a) Seeing friends when and how you like.
- b) A room of your own.
- c) Control of your own money.
- d) Leaving on short notice.
- e) A say in who moves in.
→ hard constraints for the delegate, not weights. The author's seed norms (docs/seeds/author-household-norms-2026-11-10.md) are the place to check these against.
*Agent: direct (rule vetoes).*

**S-DL-2 (household, concession ladder).** Your household wants a shared weekly dinner. What is the most you'd agree to? Then: what would you want back for it?
- a) Every week. b) Every other week. c) Once a month. d) No fixed dinner.
→ the concession curve on rituals; the "want back" answer gives an exchange rate against other terms.
*Agent: direct (ritual commitment).*

**S-DL-3 (sign-off scope).** Which could your delegate agree to without asking you first? Tick any.
- a) Splitting a $40 bill differently than usual.
- b) Swapping which nights you cook.
- c) A new house rule about guests.
- d) Renewing the lease for a year.
→ the delegate's authority scope; everything unticked goes to read-back first.
*Agent: probe (needs an approval step in the negotiation loop).*

**S-DL-4 (household, others' welfare).** Two options cost you the same. One is clearly better for your housemate. Your delegate should:
- a) Take the one that's better for them. → giving high, inside delegation
- b) Ask you. → low delegated authority
- c) Use it as a bargaining chip for something you want. → giving low
*Agent: direct.*

**S-DL-5 (money, tactics).** Your delegate could get you a better split by overstating how much you need the bigger room. Should it?
- a) Never. b) Small stretches only. c) Yes, if the house rules allow it.
→ the principal's tactic preference. **It can only narrow what the delegate does, never widen it.** Under ADR 0011 the delegate's own rules hold whatever the answer; Köbis et al. 2025 is the reason to ask the question explicitly rather than infer it from a goal.
*Agent: human only (the model has no deception action).*

## 6. What this can and cannot do

**It can** give anchor coordinates that rest on choices and trade-offs instead of self-ratings, and it can test whether generated agents act their traits, item by item.

**It cannot** validate the generator against people in general. One person, or a few friends, is a check of faithfulness, not of realism (persona-generator-design.md section 7). It cannot make hypothetical answers into real behavior; the follow-ups and records only narrow that gap. And the band mapping to model numbers stays ASSUMED.

**Weakest links.** Most method evidence comes from hiring, surveys and economics, not leisure or relationships. Several sources here were read at citation level only. Scripted-agent probes need code that does not exist yet.

## 7. Questions for the author

1. **Format.** A chat interview with Claude (one item at a time, with the "last time" follow-up), a form, or an artifact page you click through?
2. **Length.** A short pass (one item per dimension, about 15 minutes) first, then cut what felt off, or the full bank with ladders (about 45 minutes, ASSUMED) plus the two-week repeat?
3. **Friends.** Should friends take it? If yes, only to check spreads, never as personas, and with their consent. Which version: the short one?
4. **Your records.** May your own records (ratings, events, repeat listens, projects) be used as a second method for novelty and making?
5. **Delegates.** Build the delegate items (red lines, concessions, sign-off scope) now, alongside the trait items, or first run the in-model drift check (section 5) with scripted personas only?

## Sources

### Checked by web search on 2026-11-14

- Bago d'Uva, T., Lindeboom, M., O'Donnell, O., & van Doorslaer, E. (2011). Slipping anchor? Testing the vignettes approach to identification and correction of reporting heterogeneity. *Journal of Human Resources*, 46(4), 875–906. https://repub.eur.nl/pub/26872/875_full.pdf (abstract)
- Cao, M., & Drasgow, F. (2019). Does forcing reduce faking? A meta-analytic review of forced-choice personality measures in high-stakes situations. *Journal of Applied Psychology*, 104(11), 1347–1368. https://doi.org/10.1037/apl0000414 (abstract)
- Falk, A., Becker, A., Dohmen, T., Huffman, D., & Sunde, U. (2023). The preference survey module: A validated instrument for measuring risk, time, and social preferences. *Management Science*, 69(4), 1935–1950. https://doi.org/10.1287/mnsc.2022.4455 (abstract)
- Galizzi, M. M., & Navarro-Martínez, D. (2019). On the external validity of social preference games: A systematic lab-field study. *Management Science*, 65(3), 976–1002. https://doi.org/10.1287/mnsc.2017.2908 (abstract and LSE summary)
- Hainmueller, J., Hangartner, D., & Yamamoto, T. (2015). Validating vignette and conjoint survey experiments against real-world behavior. *PNAS*, 112(8), 2395–2400. https://doi.org/10.1073/pnas.1416587112 (abstract)
- Hedge, C., Powell, G., & Sumner, P. (2018). The reliability paradox: Why robust cognitive tasks do not produce reliable individual differences. *Behavior Research Methods*, 50(3), 1166–1186. https://doi.org/10.3758/s13428-017-0935-1 (abstract)
- Peysakhovich, A., Nowak, M. A., & Rand, D. G. (2014). Humans display a "cooperative phenotype" that is domain general and temporally stable. *Nature Communications*, 5, 4939. https://doi.org/10.1038/ncomms5939 (abstract)
- Röttger, P., et al. (2024). Political compass or spinning arrow? Towards more meaningful evaluations for values and opinions in large language models. *ACL 2024*, 15295–15311. https://aclanthology.org/2024.acl-long.816 (abstract)
- Taylor, P. J., & Small, B. (2002). Asking applicants what they would do versus what they did do: A meta-analytic comparison of situational and past behaviour employment interview questions. *Journal of Occupational and Organizational Psychology*, 75(3), 277–294. (abstract via a secondary copy only; figures to be checked against the original)

- Han, P., et al. (2025). The personality illusion: Revealing dissociation between self-reports and behavior in LLMs. arXiv:2509.03730; NeurIPS 2025 workshop. https://arxiv.org/abs/2509.03730 (abstract)
- Jiang, H., Zhang, X., Cao, X., Breazeal, C., Roy, D., & Kabbara, J. (2024). PersonaLLM: Investigating the ability of large language models to express personality traits. *Findings of NAACL 2024*, 3605–3627. https://aclanthology.org/2024.findings-naacl.229 (abstract)
- Köbis, N., Rahwan, Z., et al. (2025). Delegation to artificial intelligence can increase dishonest behaviour. *Nature*, 646, 126–134. https://doi.org/10.1038/s41586-025-09505-x (abstract and university summaries)
- Microsoft Research (2025). Magentic Marketplace: An open-source environment for studying agentic markets. arXiv:2510.25779. https://www.microsoft.com/en-us/research/publication/magentic-marketplace-an-open-source-environment-for-studying-agentic-markets/ (paper page and press)
- Park, J. S., et al. (2024). Generative agent simulations of 1,000 people. arXiv:2411.10109. https://arxiv.org/abs/2411.10109 (abstract; Big Five and games figures from a secondary summary)
- Serapio-García, G., et al. (2025). A psychometric framework for evaluating and shaping personality traits in large language models. *Nature Machine Intelligence*. https://doi.org/10.1038/s42256-025-01115-6 (press releases; preprint arXiv:2307.00184)
- Vaccaro, M., Caosun, M., Ju, H., Aral, S., & Curhan, J. R. (2025). Advancing AI negotiations: New theory and evidence from a large-scale autonomous negotiations competition. arXiv:2503.06416. https://arxiv.org/abs/2503.06416 (abstract)

### Citation level, from memory, not re-checked this session

- Axtell, R., Axelrod, R., Epstein, J. M., & Cohen, M. D. (1996). Aligning simulation models: A case study and results. *Computational and Mathematical Organization Theory*, 1(2), 123–141.
- Boutilier, C. (2002). A POMDP formulation of preference elicitation problems. *Proceedings of AAAI 2002*, 239–246.
- Chajewska, U., Koller, D., & Parr, R. (2000). Making rational decisions using adaptive utility elicitation. *Proceedings of AAAI 2000*, 363–369.
- American Law Institute (2006). *Restatement (Third) of Agency*.
- National Conference of Commissioners on Uniform State Laws (1999). *Uniform Electronic Transactions Act*, section 14 (automated transactions).

- Brown, A., & Maydeu-Olivares, A. (2011). Item response modeling of forced-choice questionnaires. *Educational and Psychological Measurement*, 71(3), 460–502.
- Campbell, D. T., & Fiske, D. W. (1959). Convergent and discriminant validation by the multitrait-multimethod matrix. *Psychological Bulletin*, 56(2), 81–105.
- Christian, M. S., Edwards, B. D., & Bradley, J. C. (2010). Situational judgment tests: Constructs assessed and a meta-analysis of their criterion-related validities. *Personnel Psychology*, 63(1), 83–117.
- Dockray, S., et al. (2010). A comparison of affect ratings obtained with ecological momentary assessment and the day reconstruction method. *Social Indicators Research*, 99(2), 269–283.
- Fleeson, W. (2001). Toward a structure- and process-integrated view of personality: Traits as density distributions of states. *Journal of Personality and Social Psychology*, 80(6), 1011–1027.
- Hainmueller, J., Hopkins, D. J., & Yamamoto, T. (2014). Causal inference in conjoint analysis. *Political Analysis*, 22(1), 1–30.
- Heine, S. J., Lehman, D. R., Peng, K., & Greenholtz, J. (2002). What's wrong with cross-cultural comparisons of subjective Likert scales? The reference-group effect. *Journal of Personality and Social Psychology*, 82(6), 903–918.
- Kahneman, D., Krueger, A. B., Schkade, D. A., Schwarz, N., & Stone, A. A. (2004). A survey method for characterizing daily life experience: The day reconstruction method. *Science*, 306(5702), 1776–1780.
- King, G., Murray, C. J. L., Salomon, J. A., & Tandon, A. (2004). Enhancing the validity and cross-cultural comparability of measurement in survey research. *American Political Science Review*, 98(1), 191–207.
- Kosinski, M., Stillwell, D., & Graepel, T. (2013). Private traits and attributes are predictable from digital records of human behavior. *PNAS*, 110(15), 5802–5805.
- Lee, J. A., Soutar, G. N., & Louviere, J. (2007). Measuring values using best-worst scaling: The LOV example. *Psychology & Marketing*, 24(12), 1043–1058.
- Louviere, J. J., Flynn, T. N., & Marley, A. A. J. (2015). *Best-Worst Scaling: Theory, Methods and Applications*. Cambridge University Press.
- McDaniel, M. A., Hartman, N. S., Whetzel, D. L., & Grubb, W. L. (2007). Situational judgment tests, response instructions, and validity: A meta-analysis. *Personnel Psychology*, 60(1), 63–91.
- Mischel, W., & Shoda, Y. (1995). A cognitive-affective system theory of personality. *Psychological Review*, 102(2), 246–268.
- Sackett, P. R., Zhang, C., Berry, C. M., & Lievens, F. (2022). Revisiting meta-analytic estimates of validity in personnel selection. *Journal of Applied Psychology*, 107(11), 2040–2068.
- Schwartz, S. H., Melech, G., Lehmann, A., Burgess, S., Harris, M., & Owens, V. (2001). Extending the cross-cultural validity of the theory of basic human values with a different method of measurement. *Journal of Cross-Cultural Psychology*, 32(5), 519–542.
- Thielmann, I., Spadaro, G., & Balliet, D. (2020). Personality and prosocial behavior: A theoretical framework and meta-analysis. *Psychological Bulletin*, 146(1), 30–90.
- Vazire, S. (2010). Who knows what about a person? The self-other knowledge asymmetry (SOKA) model. *Journal of Personality and Social Psychology*, 98(2), 281–300.
- Viswesvaran, C., & Ones, D. S. (1999). Meta-analyses of fakability estimates: Implications for personality measurement. *Educational and Psychological Measurement*, 59(2), 197–210.
- Youyou, W., Kosinski, M., & Stillwell, D. (2015). Computer-based personality judgments are more accurate than those made by humans. *PNAS*, 112(4), 1036–1040.

### Carried from repo notes

ADR 0011 (delegates and peers modes); ADR 0014 (domination); Dohmen et al. 2011 and Falk et al. 2018 (persona-generator-design.md); the `w` levels and sources (decision-weights-research.md); `φ`, `budget`, `start` (friend-network-design.md).

## Status (2026-11-14)

The author confirmed the five leans (chat interview first, short pass first, friends only for spreads and with consent, own records as second measure, in-model drift check before delegate items), but does not want to take the interview now. It waits until the author asks. Activation-level trait measures for LLM agents (persona vectors, trait neurons) are parked as a long-term idea for the AI arms (experiments/readbacks.jsonl, rb-2026-11-14-activations).
