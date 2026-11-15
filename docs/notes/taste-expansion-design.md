# Taste expansion: how the taste menu could enter the model (draft)

Status: conclusions confirmed by the author 2026-11-15 (rb-2026-11-15-taste-conclusions); numbers still ASSUMED; not built. Was: DRAFT by Claude, 2026-11-15, for the author to confirm (read-backs rb-2026-11-15-taste in experiments/readbacks.jsonl). Nothing here is built. Quotes are the author's, verbatim, from the Notion page "Exploration Mapping: A taste expansion application framework" (2026-08-25, labelled author-written in docs/notes/persona-generator-design.md). Everything not in quotation marks is Claude's drafting, not the author's words. Updated 2026-11-15: the open questions are replaced by DRAFT proposed conclusions, grounded first in the author's Hedonic Expansionism doc (AI-assisted, author confirmed 2026-11-15; paraphrased), then in research, then in Notion pages labelled in the last section.

## Why

The author's floor / menu / exit message (experiments/questions.jsonl, 2026-11-15) names a menu of "real, visible alternatives". The author then added that the menu also covers taste expansion. So the menu has two layers: a social menu (ways of living you can see others live) and a taste menu (the pleasures you are able to enjoy). Today the model can only shrink a pleasure (habituation, tolerance); nothing is ever liked more with time (persona design, dimension D10).

## What the author's page says

- Taste is "the things that bring you pleasure: both actions and items".
- The aim is "expanding the depth and/or breadth of taste".
- "I resist the terms development or refinement. We are trying to expand outward in a multi dimensional space."
- "My goal is certainly not to quantify taste either." "I don’t particularly want to gamify taste".
- "sample or try somewhere don’t always have to buy buy buy, i don’t want to encourage overconsumption either".
- "we can start to see crosss domain connections between hubs".
- "pref modeling doesn’t really work but having hard constraints does".
- Three timescales: past (what you tried and liked or not), present (breadth, depth, "% exploration"), future (backlog, "candidate pool").

## Draft design

1. **Taste menu per agent.** Each agent has a set of pleasure sources it can enjoy (breadth) and how much each gives (depth). Sources are grouped into domains (the Pleasure Menu groups can serve, credited as AI-assisted from the author's idea).
2. **Expansion by trying.** An agent can spend time trying a source it does not yet enjoy. A try costs time and may be a dull week. With some chance, set by the persona's openness to new things, the source joins the menu.
3. **Depth by return, for some.** Repeated engagement can raise depth for persona types the author describes ("learn how to like them overtime"), alongside the habituation the model already has. How plastic a person is stays a persona trait (D10), not a fitted number.
4. **Social path.** Friends, neighbours and makers bring sources to an agent's attention: the menu is widened by people living their tastes nearby, not by being told.
5. **Sampling, not buying.** Trying is mostly time, not money, so expansion does not reward consumption.
6. **Not a score.** The model tracks breadth and depth as measures for the researchers; agents are not given them as targets (no gamifying).

## What it lets us test

- **Floor and menu together.** Does a floor raise exploration? People without security may stick to known pleasures (exploit) rather than try (explore). If so, a floor widens the taste menu over time, not only now.
- **Menu and exit.** A wider taste menu makes the outside option richer, so exit means more.
- **Makers.** Part of what making is worth is widening other people's menus.
- **Measures.** Breadth and depth of each agent's taste menu over a run; share of time spent trying; the counterfactual from the floor/menu/exit measure (likings that vanish once there is a floor or exit).

## Proposed conclusions (DRAFT, for the author)

The author asked to settle the four open questions, with no never-lists, but with some kinds of taste harder to move than others ("sensory stuff maybe or acutla hardiwring", chat, 2026-11-15). Each conclusion below is a DRAFT proposal by Claude, not the author's view until confirmed. Every new number is ASSUMED, to be set before runs and swept.

**Sources, in order of weight.** First, the author's Hedonic Expansionism doc ("Hedonic Expansionism: Thesis, Defense, Open Problems", 2026-11-15, https://claude.ai/artifact/DAjLTLBkdCZGegukBQrbEM). Label: the author's doc (AI-assisted, author confirmed 2026-11-15). Its ideas are cited as the author's doc and paraphrased below; its wording is never quoted as the author's words, and it is not copied into the repo. Second, the research literature. Third, the author's Notion notes (last section).

Evidence strength uses three words. **Strong**: many studies agree, including reviews or meta-analyses. **Moderate**: several studies, some mixed. **Weak**: few studies, anecdote, or a long step from the lab to this model.

### 1. Can a try hurt? Yes. A try needs a small dose and a safe person, or it teaches nothing or teaches dislike.

**Conclusion (DRAFT).** Most failed tries are just a dull hour. But a try only teaches when the dose is manageable and the person feels safe enough to stay with it. A try made under threat (unmet basic needs, distress, pressure) teaches nothing and can leave a dislike. A few things are gates, not tastes: disgust and closeness do not give way to tries at all. And some things that feel bad are bad: real harm is not an acquired taste.

**From the author's Hedonic Expansionism doc (paraphrased).** Surprise updates taste the way exposure updates fear: a prediction of dislike meets a better outcome, and the gap teaches. That needs a manageable dose, enough safety and repetition. Exploration switches on only when threat is quiet, and threat shuts taste learning down. Disgust works as a gate that decides what gets close; it relaxes for valued people, opens rather than flips into liking, fades slowly and can return under stress. Benign masochism needs the benign part; liking real danger is misjudging it as safe. Expansion under pressure does not count, and "I don't like this" stays final in the moment.

**Literature.**
- One bad pairing can make a lasting aversion: one-trial taste aversion (Garcia and Koelling, 1966); children on chemotherapy turned against a new ice cream after one pairing (Bernstein, 1978); adults report aversions from single illnesses that last for years (Logue and colleagues, 1981). **Strong for food and illness. Weak for other domains.**
- Too much novelty is unpleasant: Berlyne's inverted U, with the peak set partly by how well a person can make sense of the thing (Silvia, 2005). **Moderate.**
- Exploration needs a secure base (attachment work, Mikulincer and Shaver, 2003). **Moderate to strong** for the general link; **weak** for taste learning in particular.

**For the model.** A try has three outcomes: it joins the menu, nothing happens, or it leaves an aversion. An aversion lowers later join chance; it is not a ban. Join chance is scaled by the agent's security that week, so an agent below the floor (unmet needs, distress) learns almost nothing from a try and risks more aversion. A try can be dropped mid-way at no extra cost (stopping is final in the moment). Gates are handled in conclusion 4. ASSUMED: aversion chance per failed try 0.05 for reversal sources (bitter, spicy, scary) and 0.01 for others, doubled under distress; join chance times the security reading (0 to 1); an aversion halves later join chance.

### 2. Does depth come from understanding as well as returning? Yes. Attention is the mechanism, and depth counts as expansion.

**Conclusion (DRAFT).** Depth has three routes: returning, understanding (knowledge and vocabulary) and making. All three work by giving attention more to notice. Returning alone raises liking up to a point and then wears off. Understanding and making raise how high liking can go and slow the wear-off, most for complex things. Finer liking of a familiar thing is expansion in its own right, not a lesser kind.

**From the author's Hedonic Expansionism doc (paraphrased).** Attention is the mechanism and pleasure the value: noticing more parts of an experience gives more to like (a second viewing moves from plot to craft). Knowledge and framing change how a thing tastes; naming parts sharpens discrimination; making a thing deepens how you receive it, and this is where skill slope comes from. Sharper discrimination within something you like counts as expansion. Skilled pleasures renew on return; cheap novelty depletes. The doc also cites Stigler and Becker's consumption capital: appreciation as a stock built by past consumption.

**Literature.**
- Mere exposure is real but modest, peaks after a number of exposures and then declines, and is weaker for complex stimuli (Zajonc, 1968; Bornstein's 1989 meta-analysis of about 200 experiments). **Strong that it exists; moderate on its shape.**
- Food needs several tries: often 8 to 15 for children (Birch and Marlin, 1982; Wardle and colleagues, 2003). **Strong for children; moderate for adults.**
- Music liking follows an inverted U with focused listening (Szpunar, Schellenberg and Pliner, 2004; Chmiel and Schubert, 2017). **Moderate.**
- Feeling able to understand raises interest in hard art (Silvia, 2005, 2008); experts perceive more (Leder and colleagues, 2004). **Moderate for interest; weak for plain liking.**

**For the model.** Each source on a menu carries familiarity (from returns) and understanding (a stock built by learning about it or making it). Liking from returns follows an inverted U on familiarity, which is the model's existing habituation on its falling side. Understanding lifts the peak and slows the fall, more for complex sources and for sources with a skill slope. Learning and making cost time, like a try. Depth gains count in the breadth-and-depth measure. This links to H39 makers: making could raise the maker's own understanding, not only the other person's pleasure. ASSUMED: peak at 10 returns for simple sources and 20 for complex ones; understanding raises the peak by up to 50%; making builds understanding at twice the rate of learning about.

### 3. Do domains connect? Yes, through anchors and stacked routes, and other people reach farther.

**Conclusion (DRAFT).** A new thing is easiest to like when you enter through a part that connects to something you already like (an anchor). Several routes at once (a friend plus the history) beat one route. Alone, people explore near what they already like. Other people carry them farther, into things they would never wander to. Openness is a general persona trait. Far jumps get no boost by themselves, only through a shared feature or a person.

**From the author's Hedonic Expansionism doc (paraphrased).** Enter through the part that already connects (for jazz, the bass lines), then widen. Routes stack, so two at once beat either alone. Gateways work near what you already like. Other people bring a whole history of liking and lead you beyond your habits; love is a faster route to new liking than repetition. In Rozin's chili study, children came to love chili through repeated, socially supported exposure.

**Literature.**
- Openness to experience is a general trait that predicts liking for complex music (Rentfrow and Gosling, 2003) and lower food neophobia (Pliner and Hobden, 1992). **Strong.**
- Variety spills over to new items (Gerrish and Mennella, 2001; Loewen and Pliner, 1999). **Moderate, mostly food and children.**
- Exposure effects spread to similar items (Gordon and Holyoak, 1983). **Moderate.** Far transfer across unrelated domains: **weak**.
- Social exposure drives acquired tastes such as chili (Rozin and Schiller, 1980). **Moderate to strong.**

**For the model.** Each source carries a few feature tags. Join chance rises with the share of its features already on the menu (the anchor). Each extra active route (a friend who loves it, understanding, an anchor) multiplies join chance. Solo tries draw candidates near the menu; a friend, partner or maker can offer candidates from their own menu at any distance, with the person as the anchor. Openness stays a persona trait (D3, D10), with a small, fading lift after each successful try. ASSUMED: join chance times (1 + 0.5 x feature share); each extra route times 1.5; openness lift 0.02 per successful try, fading over 8 weeks.

### 4. No never-lists. Plasticity varies by kind, and the rule is add, don't erase.

**Conclusion (DRAFT).** No persona has a list of things it will never like. Each kind of source has a plasticity class instead:

- **Open** (activities, contexts, genres, cuisines, aesthetic and sensual tastes): high yield, low cost. Tries, returns and understanding all work.
- **Reversal** (bitter, spicy, sour, scary): learnable with dose and safety. The signal stays unpleasant; what changes is how it is read.
- **Gates** (disgust, closeness, sociability): tries do not open them. They open slowly as a side effect of valued relationships, open rather than flip into liking, and can close again under stress.
- **Fixed core** (the senses themselves, core sexual taste): never removed or retrained. New likings can be added on top. Whether adding to sexual taste belongs on the taste menu at all is left open for the author (see below).

The senses differ between people (a supertaster's coffee is not your coffee), so the same source can sit in a different class for different personas.

**From the author's Hedonic Expansionism doc (paraphrased).** The senses are largely fixed; expansion happens in how the brain evaluates and attends. Genes change the experience itself (bitterness strength, soapy cilantro): people can learn to like such foods, but the experience stays different. Disgust is a gate, not a brake. New associations can be learned on top of old ones; attempts to remove core preferences, as in conversion therapy, fail and harm. Return on investment differs: activities, contexts, sensual and aesthetic tastes, genres and cuisines are high yield and low cost; core disgust and deep aversions are low yield and high cost. Whether sexual taste can be expanded by adding is one of the doc's open problems.

**Open for the author: sexual orientation and sexual taste.** Removing or retraining core sexual taste is ruled out, by the doc and by strong evidence. Whether the model should let agents add to sexual taste, or keep it off the taste menu entirely, is not decided here. Until the author decides, the model leaves it out.

**Literature.**
- Inborn sweet acceptance and bitter rejection (Steiner, 1973), yet adults learn bitter coffee and beer. **Strong.**
- Sensing is partly genetic, liking much less: PROP taster status (Bartoshuk; reviews by Tepper) has a modest, inconsistent link to food liking; a variant near OR6A2 explains a small part of cilantro dislike (Eriksson and colleagues, 2012). **Strong for sensing; weak to moderate for liking.**
- Chili is learned through repeated, social exposure (Rozin and Schiller, 1980); benign masochism (Rozin and colleagues, 2013); chili liking partly heritable (Törnwall and colleagues, 2012). **Strong that it is learnable.**
- Food neophobia is about two-thirds heritable or more (Cooke and colleagues, 2007; Knaapila and colleagues, 2007). **Strong.** Supports openness as a trait.
- Early windows: flavours met before and after birth are liked more later (Mennella and colleagues, 2001); music taste settles in early adulthood (Holbrook and Schindler, 1989). **Strong for early effects; moderate for adult change.**
- Disgust relaxes for one's own group (Reicher and colleagues, 2016) and serves to keep things at a distance (Tybur and colleagues, 2013). **Moderate.**
- Sexual orientation is very stable, and efforts to change it fail and harm (American Psychological Association task force, 2009). **Strong.**

**For the model.** Each source has a class. Plasticity multiplies join chance and depth gain. Gates take no tries; they open a little with time spent with a valued person and close a little under distress. Fixed-core sources are never removed or retrained. Personas carry a sensory sensitivity trait that moves some sources from open to reversal. This replaces "hard constraints" with hard to move, not never. ASSUMED: plasticity 1.0 open, 0.4 reversal, 0 by tries for gates (gate opening 0.01 per week with a valued person, closing 0.02 per distressed week), fixed core never lowered or retrained.

### What changes in the draft design

- Step 2 (expansion by trying) gains the aversion outcome, the security scaling, the anchor and the route multiplier.
- Step 3 (depth by return) becomes depth by return, understanding and making.
- Step 4 (social path) gains reach: people offer far candidates, not only near ones.
- The "hard constraints" idea is replaced by the four plasticity classes.

## How the Hedonic Expansionism doc maps onto this model (DRAFT)

Claude's mapping, for the author to confirm. Paraphrase only.

- **The floor.** The doc puts safety and basic needs first: material security comes before taste work, and threat shuts taste learning down. In this model that is the floor. It gives a sharp test already listed above: a floor should raise exploration and join chance, not only pleasure now.
- **The survival-liking measure.** The doc's sour-grapes test (Elster): a liking that only appears once better options are gone is adaptation, not expansion. This is the existing measure of likings that vanish once there is a floor or exit. Expansion counts only likings that survive the floor and exit.
- **The menu.** The doc's social carry (others carry you through; Scitovsky's taught consumption skills; a partner brings a whole history of liking) is the menu. Friends, partners and makers widen what an agent can reach.
- **Relationships: redesign versus expand.** The doc sorts relationship friction into five kinds, each with its own move:
  - *Tying* (a convention that bundles things and produces nothing): unbundle. This is H38b, which separates nesting, romantic priority and exclusivity, and H22 on unbundling love.
  - *Rival inputs* (one bed, one kitchen, one evening): logistics. Living apart together is already a modelled option; separate bedrooms would be a second rival-input fix, not yet modelled. Both are design moves, not taste moves.
  - *Cheap taste gap* (a partner's music or cuisine): learn to like it. This is the taste menu's social path between partners.
  - *Gate or temperament* (disgust, core sexual taste, sociability): do not train it; share roles across people or treat it as a dealbreaker. This maps to unbundled networks and to exit.
  - *Fairness* (an unequal share of chores or mental load): always redesign, never learn to like it. So the taste mechanism must never apply to an agent's share of chores. H39b models disliked making as a chore cost; that cost should only fall by changing the arrangement, never by the agent coming to like it. The doc's test is who pays: if one person quietly absorbs the cost, it is appeasement.
- **Liking versus wanting.** The doc's line is that the good is expanding liking, and expanding wanting is the failure mode. One of its falsifiers is expansion dragging wanting up with it. This is test 1 of the hedonic-technology tests (ADR 0018). Once version 3 splits wanting from liking, the taste menu should be checked by it: expansion that raises wanting-driven activity without raising liking is flagged, not counted.

## From the author's Notion

Read on 2026-11-15, read only; nothing was changed in Notion. Labels follow the rule in docs/notes/persona-generator-design.md. Quotes are verbatim, typos kept, under 15 words, and only from parts labelled author-written.

| Page (date) | Label | Reason | Used for |
|---|---|---|---|
| What should we be doing to maximize pleasure? (2026-08-30) | Author-written, except the longevity list (as already labelled) | Unchanged from the earlier label | Q2: try things, then "come back to them over time to see if you have changed". Also lists "Appreciation training?" as a way to expand taste |
| how to find something in everything (2026-10-09) | Author-written | Lowercase, typos ("pleasur etechnology"), question marks | Q3: "find paths into and not try cold ?" Rotation: "increasing novelty and diversity of pleasures allows for rotation" |
| liking things (2026-09-08) | Author-written | Lowercase fragments | Q1: disliking is "draining", "painful" or "boring/uninteresting"; draining includes "not familiar" |
| taste & aesthetic sensibilities (2026-10-04) | Author-written | Lowercase, typos ("who you wre") | Q2: "spend time with things manipulate them think of them perceive them" |
| taste != discernment (2026-08-15) | Author-written | Two lowercase lines | Q2: "noticing details is first step to taste?" |
| Food, in the archived essay "And That's Okay" (archived 2026-08-20) | Author-written | Lowercase first-person essay | Q2: "i like learning new things, and food is a world of untapped knowledge" |
| Why I Got Into Beer (draft, 2025) | Author-written | First-person blog draft | Q1 and the social path: "Beer is absolutely an acquired taste", learned in "a low risk environment" with family around it |
| electronic music (2026-10-16) | Author-written | Lowercase notes | Q4: on not leaning to folk, "this is mostly exposure" |
| taste development (2026-08-09) | Author-written | Four-word fragments | Q2 and Q4 topics only ("repeated exposure", "drenching? fatigue"); no claim drawn |
| Orientation Toward Pleasure: Sex and Romance (2026-10-11) | Author-written (as already labelled) | Unchanged | Q4: preferences "may be more hardwired than we think?" |
| everything is taste (2026-09-30) | Mixed. The lowercase notes are author-written; the bold block with Google citation links is a pasted AI answer | Bracketed citation links, bold headings, each paragraph duplicated | Q4, from the author-written notes only: "sensory input preferences dicate how you feel good or bad", and on attraction, "strong aversions that maybe can’t go away?" The AI block is not used |
| evolutionary science in art theory (2026-07-14) | Mixed. The opening paragraph and the bullet list are a pasted AI answer; two first-person lines are author-written | Bracketed citation numbers and polished bold headings around plain first-person lines | Framing: "I don’t want evolutionary explanations of why we do art/like art." "I want evolution to inform our practices as artists." |
| Expanding What You Like (2026-08-17) | Likely AI-assisted | Numbered bold rules, "That's the design.", a "one-line version" summary | Not quoted. Its claims (about eight tries; genes fix receptors, not evaluation) match the literature above, which is cited directly instead |
| Engineering On-Demand Pleasure Technology (2026-09-25) | Likely AI-assisted (seen in search only) | Opens a reply with "Yes, you have hit on a brilliant evolutionary concept" | Not used |
| sexual arousal as a kind of taste (2026-08-28) | Author-written | One lowercase question | Not used; it asks whether expanding that kind of taste is in your interest. Conclusion 4 leaves this question open for the author |
| Optimal Stimulation and Hedonic Homeostasis (2026-09-19) | Mixed, mostly AI (as already labelled) | Unchanged | Not re-read or used |

**What the author's own pages say, in sum (Claude's reading).** The author treats taste as mostly learnable ("this is mostly exposure"), favours ways into a thing over trying cold, values understanding and noticing as part of liking, and wonders whether some preferences are more hardwired than we think. That matches the proposed plasticity by kind: most taste moves, sensory and early-wired things move least.

The author wants evolution to inform practice, not to explain taste away. So inborn defaults enter the model only as starting points and slow kinds, never as reasons a pleasure is fixed.
