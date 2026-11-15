# Taste expansion: how the taste menu could enter the model (draft)

Status: DRAFT by Claude, 2026-11-15, for the author to confirm (read-backs rb-2026-11-15-taste in experiments/readbacks.jsonl). Nothing here is built. Quotes are the author's, verbatim, from the Notion page "Exploration Mapping: A taste expansion application framework" (2026-08-25, labelled author-written in docs/notes/persona-generator-design.md). Everything not in quotation marks is Claude's drafting, not the author's words. Updated 2026-11-15: the open questions are replaced by DRAFT proposed conclusions, with research evidence and more author quotes from the Notion pages labelled in the last section.

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

Evidence strength uses three words. **Strong**: many studies agree, including reviews or meta-analyses. **Moderate**: several studies, some mixed. **Weak**: few studies, anecdote, or a long step from the lab to this model.

### 1. Can a try hurt? Yes, but rarely, and mostly for sensory things.

**Conclusion (DRAFT).** Most failed tries are just a dull hour. A few leave a dislike that makes the next try less likely to land. This happens most with food and bodily things, and when the try is too far from what the person already likes.

**Evidence.**
- One bad pairing can make a lasting aversion. Garcia and Koelling (1966) showed one-trial taste aversion in rats. Bernstein (1978) found children on chemotherapy turned against a new ice cream after one pairing. Surveys of adults (Logue and colleagues, 1981) find many people hold an aversion from a single illness, often for years, even when they know the food did not cause it. **Strong for food and illness. Weak for other domains:** there is little direct evidence that one bad film or album sets up a lasting aversion.
- Too much novelty is unpleasant. Berlyne's inverted U says liking rises with novelty and complexity up to a point, then falls. **Moderate:** the shape often shows up, but where the peak sits varies by person and by how well they can make sense of the thing (Silvia, 2005).

**For the model.** A try has three outcomes: it joins the menu, nothing happens, or it leaves an aversion. An aversion lowers the join chance for that source on later tries. It is not a ban. Aversion odds are higher for sensory sources and for tries far from the current menu. ASSUMED: aversion chance per failed try 0.05 for sensory sources and 0.01 for others; an aversion halves later join chance.

### 2. Does depth come from understanding as well as returning? Yes. Returning saturates; understanding raises the ceiling.

**Conclusion (DRAFT).** Depth has two sources. Returning to a thing raises liking up to a point and then wears off. Understanding it (noticing more, knowing what to listen or look for) raises how high liking can go, and pushes back the point where it wears off. Understanding matters most for complex things.

**Evidence.**
- Mere exposure is real but modest. Zajonc (1968) found repeated exposure raises liking. Bornstein's meta-analysis (1989, about 200 experiments) found a reliable but modest effect that peaks after a number of exposures and then declines, and is weaker for complex stimuli. **Strong that it exists; moderate on its shape.**
- Food needs several tries. Children often need around 8 to 15 tastes before a new food is accepted (Birch and Marlin, 1982; Wardle and colleagues, 2003). **Strong for children; moderate for adults.**
- Music follows an inverted U. With focused listening, liking rises then falls with repeats (Szpunar, Schellenberg and Pliner, 2004; review by Chmiel and Schubert, 2017). **Moderate.**
- Understanding raises interest. Silvia's appraisal work finds interest depends on novelty and on feeling able to understand; giving people a way into hard art raises their interest in it (Silvia, 2005, 2008). Experts perceive more differences in wine and art (Leder and colleagues' model of aesthetic experience, 2004). **Moderate for interest and appreciation; weak for plain liking**, since information sometimes raises understanding without raising liking.

**For the model.** Each source in a menu carries two values: familiarity (from returns) and understanding (from effort spent learning about it). Liking from returns follows an inverted U on familiarity. Understanding lifts the peak and moves it later, more for complex sources. Understanding costs time, like a try. This fits the existing habituation: habituation is the falling side of the curve, understanding is how a person climbs past it. ASSUMED: peak at 10 returns for simple sources and 20 for complex ones; understanding can raise the peak by up to 50%.

### 3. Do domains connect? Yes, but near, not far.

**Conclusion (DRAFT).** Liking one thing makes nearby things easier to like. "Nearby" means sharing features (a rhythm, a flavour, a warmth), not sharing a domain label. Some people are open across the board, and that is a persona trait. Far jumps (cooking to jazz) get no direct boost unless the two share a feature.

**Evidence.**
- Openness is a general trait. Openness to experience predicts liking for complex and unfamiliar music (Rentfrow and Gosling, 2003), and food neophobia is lower in open people (Pliner and Hobden, 1992). **Strong that a general trait exists.**
- Variety spills over to new items. Infants fed a variety of vegetables accept a new food more readily (Gerrish and Mennella, 2001). Children who taste several new foods become more willing to try other new foods (Loewen and Pliner, 1999). **Moderate, mostly food and mostly children.**
- Spillover is strongest between similar items. Exposure effects generalize to items that resemble the exposed ones (Gordon and Holyoak, 1983). **Moderate.** Evidence for far transfer across unrelated domains is **weak**.

**For the model.** Each source carries a few feature tags. The join chance for a new source rises with how many features it shares with sources already on the menu. This is the author's "paths into" a thing rather than trying it cold. Openness stays a persona trait (D3, D10). A successful try gives a small, fading lift to openness, so breadth compounds a little. ASSUMED: join chance multiplied by 1 + 0.5 x (share of features matched); openness lift 0.02 per successful try, fading over 8 weeks.

### 4. No never-lists. Plasticity varies by kind instead.

**Conclusion (DRAFT).** No persona has a list of things it will never like. Instead, each kind of source has a plasticity level: how much tries, returns and understanding can move it. Raw sensory signals and a few early-wired traits move least. Learned meaning moves most. A low-plasticity source can still join the menu; it is just slow and risky. The things that truly do not move (sexual orientation is the clearest case) are not on the taste menu at all, so the model never treats them as something to expand.

**Evidence.**
- Some defaults are inborn. Newborns accept sweet and reject bitter (Steiner, 1973). **Strong.** Yet adults learn to love bitter coffee and beer, so the default is a starting point, not a wall.
- Sensing is partly genetic; liking much less so. Sensitivity to the bitter compound PROP (non-tasters and supertasters, Bartoshuk) is set by genes, but its link to what people actually like to eat is modest and inconsistent (reviews by Tepper). One gene variant near the smell receptor OR6A2 is linked to finding cilantro soapy, but it explains only a small part of who dislikes it (Eriksson and colleagues, 2012). **Strong for sensing; weak to moderate for liking.**
- Pain can become pleasure. Chili burns every time, yet people learn to love it through repeated, social exposure (Rozin and Schiller, 1980), what Rozin calls benign masochism. Twin studies find liking for chili is partly heritable (Törnwall and colleagues, 2012). **Strong that it is learnable; moderate on how much is inherited.**
- Fear of new food is highly heritable. Twin studies put the heritability of food neophobia at about two thirds or more, in children and in adults (Cooke and colleagues, 2007; Knaapila and colleagues, 2007). **Strong.** This supports openness as a persona trait, not a fitted number.
- Early windows matter. Flavours met in the womb and in breast milk are liked more later (Mennella and colleagues, 2001). Music taste tends to settle in early adulthood (Holbrook and Schindler, 1989). Adults can still change, but it takes attention, not background exposure. **Strong for early effects; moderate for adult change.**
- Sexual orientation is very stable, and efforts to change it fail and do harm (American Psychological Association task force, 2009). **Strong.**

**For the model.** Use the three pathways from the persona design (D1) as plasticity kinds, so no new taxonomy is needed. Sensory sources: low plasticity, higher aversion risk. Relational sources: middle. Conceptual sources: high. A persona also has a sensory sensitivity trait that lowers sensory plasticity further (high sensitivity is like a supertaster, or someone easily overloaded). This replaces "hard constraints" with something closer to the author's view: hard to move, not never. ASSUMED: plasticity multipliers 0.2 sensory, 0.6 relational, 1.0 conceptual, applied to join chance and to depth gain.

### What changes in the draft design

- Step 2 (expansion by trying) gains the aversion outcome and the feature-share boost.
- Step 3 (depth by return) becomes depth by return and understanding.
- The "hard constraints" idea is replaced by plasticity by kind. Nothing is ever impossible inside the taste menu.

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
| sexual arousal as a kind of taste (2026-08-28) | Author-written | One lowercase question | Not used; it asks whether expanding that kind of taste is in your interest. Conclusion 4 keeps orientation off the taste menu, for the author to confirm |
| Optimal Stimulation and Hedonic Homeostasis (2026-09-19) | Mixed, mostly AI (as already labelled) | Unchanged | Not re-read or used |

**What the author's own pages say, in sum (Claude's reading).** The author treats taste as mostly learnable ("this is mostly exposure"), favours ways into a thing over trying cold, values understanding and noticing as part of liking, and wonders whether some preferences are more hardwired than we think. That matches the proposed plasticity by kind: most taste moves, sensory and early-wired things move least.

The author wants evolution to inform practice, not to explain taste away. So inborn defaults enter the model only as starting points and slow kinds, never as reasons a pleasure is fixed.
