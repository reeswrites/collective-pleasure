# A persona generator from the author's pleasure frameworks: design (PROPOSAL, 2026-11-13)

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Status: a design proposal, docs only. No code was written and nothing was run. It answers the author's question of 2026-11-13 (experiments/questions.jsonl): "why does real personas matter as opposed to a solid framework for generating interesting agents i have pleasure frameworks etc in my notion". **Every number below is ASSUMED unless a source is named next to it.** Named sources set directions, shapes or rough sizes at the level of human traits. None of them sets a number in model units.

## Why this exists

**The v2 retest win came from placeholder personas.** In docs/results/v2-retest.md the confirmatory win comes from the grid personas, 165 of 180 pairings, whose principles are TODO and whose weights come from an ASSUMED axis mapping. On the author's six hand personas alone the condition was not shown. So the current headline result rests on a population nobody designed.

**Hand personas cannot fix that.** Six or sixty hand-written personas are a sample of whatever their writer thought of. A generator makes the population an explicit object: what varies, by how much, what moves together. It can be read back, argued with and swept.

**The plan agreed with the author.** Dimensions come from the author's own pleasure frameworks. Spreads and correlations come from research where it exists, and are marked ASSUMED where it does not. Two or three anchor personas, elicited from the author, are known-answer checks on the generator, not the sample.

**What the author sets and what research sets.** The author's frameworks decide *what* varies between people. Research decides *how much* it varies and *what moves together*. The Big Five and attachment traits below are a scaffold for correlations only. They are not persona dimensions the author wrote.

## Attribution

The author has twice had AI-written text credited to them. Every Notion page and every line used here carries one of three labels:

- **author-written**: the author's own voice (lowercase drafts, typos, hedges, first-person thinking aloud);
- **likely AI-assisted**, with the reason;
- **unclear**.

Quotes are verbatim, typos included, and under 15 words. Hedges are kept. Personal details about other people and friends' names are left out. Notion was read only; nothing was changed there. Pages were read on 2026-11-13.

| Page (last edited) | Label | Reason |
|---|---|---|
| Pleasure Menu, page (2026-09-21) | Mixed. The lowercase "fav things to do" list is author-written. The "What do I want?" router and the "Upkeep" section are unclear, leaning AI-assisted | Router and upkeep are polished imperative prose ("Tap the line that fits"), unlike the list below them |
| Pleasure Menu, database schema (2026-09-17) | Unclear | Property descriptions are polished and terse ("No decisions."); the tags themselves may be the author's |
| Pleasure Identities (2026-08-31) | Author-written | Lowercase, hedged, thinking aloud ("I need to think more about this") |
| Orientation Toward Pleasure: Sex and Romance (2026-10-11) | Author-written | First person, hedges, own links; no chatbot markers |
| on pleasure (2026-08-31) | Author-written | Free notes, typos, first person |
| What should we be doing to maximize pleasure? (2026-08-30) | Author-written, except the longevity list at the end | The list is numbered, polished and cites cohort data without links (as docs/notes/pleasure-technology-and-makers.md already found) |
| Hedonism For Dummies (2026-09-21) | Short form author-written. Long form unclear | The long form sits in a quote block copied from another page and links an outside essay for "Create, consume, cavort, commune" |
| Optimal Stimulation and Hedonic Homeostasis (2026-09-19) | Mixed. A few lines are author-written; most of the page is AI | Two toggles are labelled "Gemi" and "gemini" and end with chatbot questions; many quoted lines sit in quotation marks with bracketed citations |
| Relationships as a Hedonic Technology (2026-11-10) | Author-written | First person essay draft, the author's own examples |
| What should I do right now? On Pleasure Scheduling (2026-09-18) | Author-written | The author's own examples and a typo ("beter") |
| Exploration Mapping: a taste expansion framework (2026-08-25) | Author-written | First person, lowercase asides |
| everything is taste (2026-09-30) | Mixed. Opening line author-written; most of the body is a pasted AI reply | Bracketed citation links and bold headings mid-page. Only the first line is used here |
| The Pleasure Plan: a framework for goals, routines, and menus (2026-10-02) | Likely AI-assisted | Callouts, mermaid diagrams, an evidence table and "All counts are starting defaults, not research findings" |
| Learning, pleasure, and the evaluator (2026-10-16) | Likely AI-assisted | Opens "Notes from a conversation", a one-line callout thesis, a formal source list |

Two earlier repo notes already label other pages: docs/notes/hedonic-technology-synthesis.md (with its 2026-11-11 correction) and docs/notes/pleasure-technology-and-makers.md. The three lines the author does not hold ("put it at the trigger", the next-day-verdict metrics list, "commitment converts present friction into recalled pleasure") are not used here.

## 1. The dimensions of a person, from the author's frameworks

Ten dimensions. Each says where it comes from and how sure the attribution is. A short "state, not trait" note follows them.

### D1. Sources of pleasure and their weights

**What it is.** Which kinds of things give a person pleasure, and in what proportion.

**From the author.** Identity is pleasure: "so we are organizing around what we like: what gives us pleasure." (Pleasure Identities, author-written). People differ: "what works for them will not necessarily work for you" (Hedonism For Dummies, short form, author-written). Preferences are like taste in food: "these are just preferences just as we like certain kinds of foods or music" (Orientation, author-written).

**The categories.** The Pleasure Menu database groups items by ten pleasures (beauty and awe, laugh, make people laugh, think deeply, story, calm and everyday, taste, make someone happy, make something, body and rhythm) and by three pathways (sensory, conceptual, relational). The tags are labelled **AI-assisted from the author's idea** (the author, 2026-11-13: "AI assisted but from my idea"). The idea of grouping is the author's; the wording of the groups and pathways is not quoted as theirs. The author-written list on the menu page is concrete and overlaps the tags: "making someone else happy", "riffing with someone else to create a series of jokes", eating something "fatty sweet or mildly spicy and a bit acidic".

**For the generator.** Use the three pathways as the coarse mix, because the model can act on them. The ten groups are too fine for a world with four need clocks. This is a choice to confirm with the author (question 2).

### D2. Sharing need and give, share or receive

**What it is.** Whether a pleasure counts for more when shared, and which role a person prefers.

**From the author.** "Some people don’t share pleasure with others, other people almost need to share" (Relationships as a Hedonic Technology, author-written). The same page sorts styles into give, share and receive, and the author's self-assessment wants "an initiator with strong visions of their own" (author-written). The menu database's "With" field (alone, partner, friends, crowd) is **unclear**.

**Split in two.** A sharing multiplier (how much a shared session beats the same thing alone) and a role mix (give, share, receive), plus an initiative trait (who proposes plans). The author named the missing initiator, so initiative is worth its own parameter.

### D3. Novelty seeking versus depth (explore versus exploit)

**What it is.** Appetite for new things against returning to known good ones.

**From the author.** "Do (Explore/Exploit)" is a step in Hedonism For Dummies (short form, author-written). "Taste provides short and long through explore (Taste Expansion) and exploit" (Pleasure Scheduling, author-written). "Finding new things is a way to find more things to enjoy." (What should we be doing, author-written). The author frames growth as breadth or depth: "diversify or deepen their bags" (Exploration Mapping, author-written).

**AI-assisted reading, not used as the author's.** Learning, pleasure, and the evaluator splits pleasure into explore (surprise) and exploit (fluency). That page is likely AI-assisted.

### D4. Stimulation tolerance (optimal arousal)

**What it is.** How much stimulation a person can take before it costs them, and how much they need before boredom costs them.

**From the author.** "too much or too little stimulation is heavily felt and penalized" and "if you’re bored you want more but if you need focus you need less" (Optimal Stimulation, author-written lines). The author also writes that people carve out quiet spaces and that this "social atomization of space keeps us apart" (author-written).

**Not the author's.** The same page says introverts have higher baseline arousal and need quiet. That line sits in quotation marks next to two Gemini replies, so it is **likely AI-assisted**. It was not checked against research here and is not used.

**Why it is separate from D3.** D3 is about *what* (new or known). D4 is about *how much* (intensity and crowding). A person can seek new books and still need a quiet house.

### D5. Making versus consuming

**What it is.** How much pleasure a person gets from making things (food, art, games, care) against consuming what others make.

**From the author.** "pleasure in work is pleasure over time" (on pleasure, author-written). The author's earlier line "I have always liked the creation side more" (Why code?, author-written, already in docs/notes/pleasure-technology-and-makers.md). "Make something" and "Make someone happy" are menu groups (unclear). "Create, consume, cavort, commune" is in the Hedonism For Dummies long form (unclear; it links an outside essay).

### D6. Romance, intimacy and the strand profile

**What it is.** How much each strand of closeness matters to a person: care, affection, intimacy, desire, commitment, logistics, and the two strands the author added, fun and advice.

**From the author.** Romance "as a preference for" "shared pleasures", "desire" (hedged: "but is this too sexual?"), "being seen or heard" and "being complete" (Pleasure Identities, author-written; the author marks the last with a question mark). On sex: "it isn’t really that important unless you really like sex" (same page). On fixedness: "some things do stay largely crystallized as well." (Orientation, author-written). The strand list itself comes from "unbundling love" (author-written per the synthesis) and the friend read-back (author confirmed "go with those", 2026-11-13).

**A guardrail this dimension must keep.** src/mar/personas.py forbids group identities, including sexual orientation and gender, and real people. So this dimension is *how much each strand matters*, never *who* a person is drawn to. The author's own notes support that move: they treat orientation labels as too broad and preferences as the real unit.

### D7. Friendship traits

**What it is.** The three traits the author confirmed on 2026-11-13 (docs/notes/friend-network-design.md, section 5): how much friends matter (`φ`), how many ties a person runs (`budget`), and how readily they start and restart ties (`start`).

**Attribution.** The split into three is Claude's proposal from research (docs/notes/friendship-research.md), confirmed by the author ("go with those"). The list of itches friends scratch (fun, care, intimacy, advice, logistics) is the author's, from the read-back. Label: author-confirmed, Claude-proposed.

### D8. Suffering weight, and suffering by kind

**What it is.** How much anticipated suffering counts against pleasure in big choices (`w`), and, later, separate weights for different kinds of suffering.

**From the author.** "If either of your pleasure is at the explicit suffering of another" then reconsider (Relationships, author-written). The author made the decision rule a persona trait: "persona trait in that people have different sources of pleasure and suffering" (experiments/changes.jsonl, 2026-11-11). The read-back rb-2026-11-11-w confirmed one `w` for H39, then "split by kind when eliciting real personas".

**The split.** Closeness and lost autonomy cost more for some people; being alone costs more for others (docs/notes/decision-weights-research.md, section 3). So: `w_close` and `w_alone`, around the existing `w`.

### D9. Money and security values

**What it is.** How much a person values money, a security buffer and risk, and how they hold surplus.

**From the author.** "If you’re with someone purely for stability reasons" you should ask whether you could build that stability yourself (Relationships, author-written; the quote is the first clause). On surplus, hedged with "I think": "if you have a surplus of resources then it does make sense" that you have "a duty of sorts to share" (same page). The seeds: everything shared "for now", own things "but choose to give" them (docs/seeds/author-household-norms-2026-11-10.md, author-written).

**Disposition, not circumstance.** Wage, savings and job enjoyment are world draws in docs/notes/economy-calibration.md, not persona taste. The generator owns only how a persona *values* money and security. Mixing the two would let a persona's taste set its income.

### D10. Taste development (how plastic a person's likes are)

**What it is.** Whether repeated exposure makes a person like something more (an acquired taste) or only less (habituation), and how fast.

**From the author.** "you have to like something to stick with it" and "learn how to like them overtime" (on pleasure, author-written). "I resist the terms development or refinement." (Exploration Mapping, author-written). From the Hedonism For Dummies long form, which is unclear: "your evaluations of stimuli/how you process them is fluid".

**Why it matters for norms.** The model today only habituates (`LeverConfig.hab_rate`, tolerance). If some people come to like a shared ritual more over time, rituals and commitments pay differently for them. That is a persona difference the norms under study would act on.

### State, not trait: capacity

**The menu's "Capacity" field** (sharp, wants input, low, restless, social, directionless; unclear) describes a person's state in the moment, not who they are. It belongs to the world's weekly state (rest and connection clocks), not to the generator. It is listed so nobody adds it as a persona trait by mistake.

## 2. How each dimension maps onto model parameters

**Two layers, as now.** The profile layer (typed numbers) is what scripted agents read. The story layer (three principles and a backstory) is what LLM agents read. The generator fills both, with `source="generated"`, which `SOURCES` in src/mar/personas.py already allows.

**What becomes per-persona.** Several parameters are global today and would become persona fields: rest salience (0.5 for everyone), the strand weights, the habituation rate, and the three held-condition intensities. Each stays at today's global value when the generator is off, so old runs stay bit-identical, as the repo's other flags do.

| Dimension | Existing parameters it sets | New parameters (proposed) |
|---|---|---|
| D1 pleasure sources | `weights.togetherness` and `weights.other_connections` (relational share); `needs.connection` salience | `mix = (sensory, conceptual, relational)`, shares summing to 1. Sensory share scales the habituation rate (sensory pleasures satiate faster). Conceptual share sets a solo pleasure term the model lacks today (reading, thinking), so a low-relational persona is not simply starved |
| D2 sharing and role | `HedonicConfig.together_event` value per persona; makers' giving pleasure | `share_mult` (shared session over solo, ≥ 1); `role = (give, share, receive)`; `initiative` (chance of proposing a plan or ritual each week) |
| D3 novelty vs depth | `variety_policy` (repeat, rotate, adaptive), today derived from risk tolerance and two axes; `LeverConfig.switch_cost` | `novelty` in [0,1]; drives variety policy directly and the appetite for new ties (feeds `start` in D7) |
| D4 stimulation tolerance | `needs.rest` salience (today 0.5 for all); `work_fatigue` sensitivity | `crowd_cost` (housing: the per-week privacy or conflict cost of sharing space, docs/notes/housing-research.md regimes B to D) |
| D5 making | `makers.traits`: `kind` (cook, artist, carer) and `enjoy` rank, today drawn uniformly from the persona id | `make_pleasure` (process pleasure per making unit), replacing the uniform draw; kind drawn with the D1 mix (sensory leans cook, conceptual leans artist, relational leans carer; ASSUMED) |
| D6 strands | `LeverConfig.strand_weight` (global today) | per-persona `strand_weight` over the eight strands; `partner_core` (how much a persona wants one bond to hold many strands; "bundle thickly, never solely") |
| D7 friendship | `weights.other_connections`, `aspirations.friends_per_week`, `bond_policy` | `φ`, `budget`, `start`, as in friend-network-design.md section 5 |
| D8 suffering weight | `makers.suffering_weight` (`w`), used by the weighted and hybrid decision rules | `w_close` multiplies `trapped_intensity` and `diminished_intensity`; `w_alone` multiplies `denied_intensity` on the connection need and the outside option's loneliness. Both default to `w` |
| D9 money and security | `weights.security`, `weights.money`, `aspirations.security_buffer`, `aspirations.savings_per_week`, `risk_tolerance`, `axes.giving_keeping`, `forecast.discount` | `patience` (sets `forecast.discount` and savings target); H40 reads money weight and patience; the world, not the persona, draws wage and savings |
| D10 taste plasticity | `LeverConfig.hab_rate`, `tol_rate` | `acquire_rate`: liking of a repeated shared activity rises toward a ceiling before habituation wins. Off by default |

**What the old axes become.** The five axes (certainty-openness and so on) are kept only as a readable summary computed from the new dimensions, so `render()` and old tooling still work. They stop being the source of the weights. The ASSUMED `profile_from_axes` mapping retires for generated personas.

**The five value weights.** They are derived, not drawn: togetherness from the relational share, sharing need and low avoidance; other connections from the friend budget; autonomy from avoidance and novelty; security and money from D9. Each formula is ASSUMED and lives in one function with its own docstring, as `profile_from_axes` does now.

**Negotiation style.** No author framework speaks to it, and the read found no research mapping in model terms. Proposal: keep the five styles, drawn from agreeableness and the directness axis, marked ASSUMED, with "style fixed to collaborative" as a sensitivity arm.

**The story layer.** Principles and a backstory are rendered from the dimension bands by templates, then checked by `validate()` (blocklist, no em-dashes, at most four sentences). Templates, not free LLM writing, so the text cannot carry traits the numbers lack. A human still reads every generated persona before it runs with LLM agents, as personas.py requires.

**What H40 and housing need, and get.** H40 (docs/notes/economy-calibration.md) needs each persona's money weight, patience, risk tolerance and how it trades hours for income; the generator supplies all four. Housing (docs/notes/housing-research.md) needs a crowding cost and a tolerance for living alone; D4 and `w_alone` supply them. Wage, savings, job enjoyment and rent stay world draws.

## 3. Spreads

**The rule for this section.** "Grounded" means a named, checked source supports the shape, direction or size *at the level of human traits*. Every mapping from a human trait to a model number is ASSUMED. Sources were checked by web search on 2026-11-13 for author, year, venue and DOI or URL; read depth is given per source.

### 3a. The latent scaffold (grounded)

**Seven latent traits carry the correlations.** Neuroticism (N), extraversion (E), openness (O), agreeableness (A), conscientiousness (C), attachment anxiety (Anx) and attachment avoidance (Avo). Each is a standard normal. Their correlations are taken from one large table: Noftle & Shaver (2006), Study 1, Table 2, N = 8,136 to 8,318 undergraduates, BFI and ECR. The table was read from the full text.

| | N | E | O | A | C | Anx | Avo |
|---|---|---|---|---|---|---|---|
| N | 1 | | | | | | |
| E | −.26 | 1 | | | | | |
| O | −.10 | .26 | 1 | | | | |
| A | −.28 | .13 | .13 | 1 | | | |
| C | −.18 | .18 | .10 | .30 | 1 | | |
| Anx | .42 | −.15 | −.07 | −.19 | −.23 | 1 | |
| Avo | .14 | −.21 | −.09 | −.22 | −.20 | .22 | 1 |

**Why this table.** It is one observed matrix, so it is internally consistent (a valid correlation matrix), and it holds the Big Five and both attachment dimensions together. Its limits: students at one university, self-report, one inventory.

**It agrees in shape with the meta-analysis.** van der Linden, te Nijenhuis & Bakker (2010) pooled 212 samples of Big Five intercorrelations and found two higher factors, stability (N reversed, A, C) and plasticity (E, O) (abstract level). The table above has the same pattern: A, C and low N cluster; E and O cluster.

**Attachment is dimensional.** Anxiety and avoidance are continuous, not types (Fraley et al. 2015; Fraley, Waller & Brennan 2000 built the item-level measure). So both are drawn as continuous traits.

### 3b. Each dimension's spread

| Dimension | Shape | Correlates with (latent) | Grounding |
|---|---|---|---|
| D1 mix | Dirichlet over three shares, concentration 3 (each share mostly 0.1 to 0.6) | relational share: E (+), Avo (−) | **ASSUMED** shape and size. Signs follow Pollet et al. 2011 (extraverts run larger networks, r .20 to .23) and Gillath et al. 2017 (avoidance, fewer ties) |
| D2 share_mult | log-normal, median 1.3, clipped [1, 2.5] | A (+), Anx (+) | **ASSUMED**. No source measures "pleasure amplified by sharing" |
| D2 role, initiative | role Dirichlet; initiative Beta | initiative: E (+), C (+) | **ASSUMED** |
| D3 novelty | Beta, mean 0.5 | sensation seeking, which overlaps E's excitement-seeking facet and O (Aluja et al. 2003) | Direction **grounded**: Aluja et al. 2003 (N = 1,006) found sensation seeking mostly carried by excitement seeking, with openness to actions and fantasy (abstract level). Sensation seeking is a continuous trait with a standard scale (Zuckerman, Eysenck & Eysenck 1978) and broad behavioral correlates (Roberti 2004, abstract level). Loadings (0.5 on E, 0.3 on O) **ASSUMED** |
| D4 stimulation tolerance | Beta, mean 0.5 | N (−), E (+) | **ASSUMED**. The introvert-arousal claim in the author's Notion is AI text and was not checked |
| D5 make_pleasure | three levels as now (0, 0.5, 1) or Beta | O (+) for artist kind | Direction **grounded** for art only: openness predicts creative achievement in the arts (Kaufman et al. 2016, four samples, N = 1,035; abstract level). Size **ASSUMED**. Care and cooking: **ASSUMED** |
| D6 strand weights | Dirichlet centred on today's global weights, concentration 20 | desire weight: an independent residual; commitment: Anx (+) | Spread of desire **grounded** in kind: desire splits into dyadic and solitary dimensions that people differ on (Spector, Carey & Steinberg 1996). Everything else **ASSUMED** |
| D7 `φ`, `budget`, `start` | as in friend-network-design.md: `φ = exp(N(0, 0.4))`, `start = exp(N(0, 0.3))` | `budget`: E (+, about 0.2); `start`: Avo (−); `φ`: Anx (+) | Directions **grounded** (Pollet et al. 2011; Gillath et al. 2017; Leary et al. 2013 for the existence of spread in need to belong). Sizes **ASSUMED** |
| D8 `w` | `exp(N(0, 0.6))`, clipped [0, 4], as accepted 2026-11-11 | **independent** of everything | Spread **grounded** in kind, not size: loss aversion varies a lot between people, and about half of representative samples are loss tolerant (Brown et al. 2024; Chapman et al. 2025, in decision-weights-research.md). Independence follows that note (BIS and BAS roughly independent; Carver & White 1994) |
| D8 `w_close`, `w_alone` | `w` × `exp(N(0, 0.3))` each | `w_close`: Avo (+); `w_alone`: Anx (+) | Directions **grounded**: avoidance and commitment aversion (Birnie et al. 2009); fear of being single and settling (Spielmann et al. 2013). Sizes **ASSUMED** |
| D9 risk tolerance | Beta, mean 0.5 | novelty (+), N (−) | Spread and a general factor **grounded**: a single general risk question predicts risky behavior across domains, and willingness varies continuously (Dohmen et al. 2011). Loadings **ASSUMED** |
| D9 patience, giving | Beta each | giving: A (+) | Within-country spread **grounded**: patience, risk, altruism and trust vary more within countries than between them (Falk et al. 2018, abstract level). Loadings **ASSUMED** |
| D9 security, money weights | Beta each | security: N (+), novelty (−) | **ASSUMED** |
| D10 acquire_rate | Beta, mean low (0.2) | O (+) | **ASSUMED**. No source was checked for acquired liking |

**Summary of grounding.** Grounded: the latent correlations (one large table), the dimensional nature of attachment, the existence and continuity of spread in sensation seeking, risk, loss attitude, need to belong, desire and economic preferences, and the signs of eight links. Assumed: every shape and size in model units, every loading's size, and five dimensions entirely (D1 shape, D2, D4, most of D5 and D6, D10).

**No mass on types.** Every dimension is continuous. The research is consistent on this for every trait it covers, and the author's notes resist labels ("asexuality as a bad frame", Orientation, author-written).

## 4. Sampling

**One function, two modes.** Population mode draws personas that hang together the way people do. Design mode spreads personas evenly over the space, to find out which dimensions drive results. Every run states its mode.

### 4a. Population mode (correlated draws)

**Step 1.** Draw the seven latents from a multivariate normal with the table in 3a.

**Step 2.** For each model dimension, form `x = λ·z + sqrt(1 − |λ|²)·ε`, with `ε` its own independent normal and `λ` its loadings from 3b. This is a Gaussian copula: correlations come only through the loadings, and `x` stays standard normal.

**Step 3.** Turn `x` into a uniform with the normal CDF, then into the dimension's own scale with that dimension's inverse CDF (log-normal for `w`, Beta for weights, gamma draws normalized for the Dirichlet mixes).

**Step 4.** Derive the five value weights, needs, aspirations and lever policies (section 2), render the story layer, and validate.

**Reproducible per persona.** Every draw comes from a hash of the persona id and a salt, as `makers._u` does now, plus a generator version. The same id always gives the same persona under the same version (ADR 0020 handles version changes).

**No curation.** Nothing is rejected for being dull or extreme, except by `validate()`. "Interesting agents" should come from covering the space, including its corners, not from picking. Picking would bias every result.

### 4b. Design mode (space-filling, for sensitivity)

**Latin hypercube.** Draw `n` points in the unit cube of the model dimensions so that each dimension's range is cut into `n` equal slices and each slice is used once (McKay, Beckman & Conover 1979). That covers each dimension evenly with far fewer runs than a grid. The old 2^5 grid used 32 personas for 5 axes at 2 levels; a hypercube of 64 covers 12 dimensions at 64 levels each.

**Independent by default, correlated as a check.** The plain hypercube treats dimensions as independent, so every combination is equally likely, including ones people rarely show. A second design imposes the population rank correlations on the same hypercube with the Iman & Conover (1982) method, which keeps each dimension's marginal exactly. If a finding holds under one design and not the other, it depends on which combinations exist, and that is itself worth reporting.

**Which dimensions matter.** On a hypercube sample, rank regression of each outcome on the dimensions gives a cheap first ranking. Variance-based indices (Saltelli et al. 2008) cost many more runs and are kept for the two or three dimensions that the first pass flags. Run cost matters here: the H41 power check alone is about 4.7 hours.

**Size (ASSUMED).** About 10 points per dimension: 120 personas for 12 dimensions. Not a sourced rule; a starting point to check by whether rankings stay stable when `n` doubles.

### 4c. Pairs and households

**Pairing is a separate choice.** Most results are about pairs. Default: pair at random within the generated population. Arm: pair by similarity on D1 and D9, since the author holds that compatibility beats attraction ("attractive is easier to find/make than compat tho", Relationships archive, author-written). Whether real couples match on these traits was not checked here, so the arm is a design probe, not realism.

### 4d. What happens to the old personas

**The grid and the six hand personas stay as legacy arms.** Re-running the v2 retest condition on a generated population is the first check of whether the headline survives a designed population. That is a future preregistration, not part of this note.

## 5. Anchor personas

**What an anchor is for.** A persona the author describes in their own words, with behavior the author can predict. The generator is checked against it. An anchor is never part of the sample.

**No real people.** src/mar/personas.py rules out real people. So anchors are archetypes the author describes, not portraits of friends. Whether one anchor may be the author's own leanings is question 1.

**Three proposed anchors, as questions to put to the author.** Each set is short and in the author's terms. Answers are recorded verbatim.

**Anchor A, the maker-giver.**
- When you have a free evening, which of these would they pick first: make something, share a meal, watch something alone, go somewhere new?
- Do they enjoy making something even if nobody uses it, or only when it is for someone?
- If a partner never proposed plans, would that cost them a little, a lot, or nothing?

**Anchor B, the security-led homebody.**
- How much savings would they want before they felt settled: a month, six months, a year?
- Would they rather eat their favorite dish again or try a new place, most weeks?
- If their partner wanted a standing weekly ritual, would they welcome it, accept it, or resist it?

**Anchor C, the novelty-led connector.**
- How many friends would they see in a normal month?
- If a household asked them to see friends less, would they negotiate, comply, or leave?
- Would a quiet month alone feel like rest or like a loss?

**Behavior predictions.** For each anchor, the author also predicts three choices in model terms: does this persona propose a ritual, does it accept a commitment to stay, and does it leave when a partner withdraws from friends. These are the known answers.

**How the generator is checked.**
1. **Inside the support.** Each anchor's elicited dimensions are coded onto the model scales. Each must fall inside the generator's range, and not past the 1st or 99th percentile on any dimension. An anchor in the far tail means the spread is too narrow.
2. **Known answers.** A persona generated at the anchor's coordinates must make the three predicted choices in a short run. A miss is a mapping error (section 2), and it is fixed before any experiment uses the generator.
3. **Round trip.** The generated persona at those coordinates is rendered in plain English and read back. "Not what I meant" is logged, as the read-back practice requires.
4. **Local stability.** Small moves around each anchor (a tenth of each range) should not flip the three choices. If they do, the result near that anchor is fragile and is reported as such.

## 6. What the read-back to the author should contain

**The dimension list.** Ten dimensions in one line each, with the page each came from and its attribution label. The author confirms which lines they hold, especially the Pleasure Menu tags, the three pathways and the Pleasure Plan's classes, which are unclear or likely AI-assisted.

**The mapping, in plain sentences.** One sentence per dimension: "a persona who gets more pleasure from sharing gets more from each shared evening". No formulas in the read-back.

**What is grounded and what is guessed.** The two lists from the end of section 3, in plain words.

**Three generated personas,** rendered in plain English, drawn at random in population mode. Not chosen to look good.

**One side-by-side.** An old grid persona next to a generated persona with similar values, so the author sees what changed.

**The anchor questions** from section 5, with room for verbatim answers.

**What could move.** Under ADR 0020, the findings that rest on the grid personas (the v2 retest and anything built on it) are listed as "could move" until rerun on a generated population.

**Logging.** Everything shown is appended to experiments/readbacks.jsonl, and answers to experiments/questions.jsonl, verbatim.

## 7. What a small model can and cannot claim

**It can claim** that a finding holds, or fails, across a designed and stated population of agents rather than a handful of hand-picked ones. It can say which persona dimensions a finding depends on, and whether a norm wins everywhere in the space or only in one region. It can show whether results depend on which trait combinations exist (correlated versus independent designs).

**It cannot claim** anything about how many real people are like any persona, or what real people would do. The correlations come from one undergraduate sample; the spreads in model units are guesses; the mappings from traits to parameters are guesses.

**It cannot validate the generator against people.** The anchors check the generator against the author's intuitions, which is a check of faithfulness to the author's frameworks, not of realism.

**It cannot turn the author's frameworks into evidence.** The frameworks set what varies. They are one person's view of pleasure, and the model inherits it. That is the point of the project, and also its limit.

**The LLM story layer adds its own gap.** Text rendered from numbers may be read by an LLM agent in ways the numbers do not imply. Scripted and LLM agents on the same generated personas should be compared before any LLM result is read.

## 8. Questions for the author

1. Anchors: should one anchor be your own leanings, as written in your notes, or should all three be archetypes you describe? The persona rules say no real people.
2. Pleasure sources: do you hold the Pleasure Menu's ten groups and three pathways (sensory, conceptual, relational) as your own? **Answered 2026-11-13:** "AI assisted but from my idea". Used as dimensions; not quoted as the author's words.
3. Default draws: population-like (traits correlated as in personality research) or space-filling (every combination equally likely), with the other as a check?

## Sources

### Notion (the author's workspace, read-only, 2026-11-13)

Pleasure Menu (page and database); Pleasure Identities; Orientation Toward Pleasure: Sex and Romance; on pleasure; What should we be doing to maximize pleasure?; Hedonism For Dummies; Optimal Stimulation and Hedonic Homeostasis; Relationships as a Hedonic Technology; What should I do right now? On Pleasure Scheduling and Time Structuring; Exploration Mapping: A taste expansion application framework; everything is taste; The Pleasure Plan; Learning, pleasure, and the evaluator. Labels in the attribution table above.

### Research checked this session (2026-11-13)

- Aluja, A., García, Ó., & García, L. F. (2003). Relationships among extraversion, openness to experience, and sensation seeking. *Personality and Individual Differences*, 35(3), 671–680. https://abacus.universidadeuropea.com/entities/publication/0112fa0b-30f9-475b-9ae7-d2ac4b6a351f (abstract)
- Dohmen, T., Falk, A., Huffman, D., Sunde, U., Schupp, J., & Wagner, G. G. (2011). Individual risk attitudes: Measurement, determinants, and behavioral consequences. *Journal of the European Economic Association*, 9(3), 522–550. https://doi.org/10.1111/j.1542-4774.2011.01015.x (abstract)
- Falk, A., Becker, A., Dohmen, T., Enke, B., Huffman, D., & Sunde, U. (2018). Global evidence on economic preferences. *Quarterly Journal of Economics*, 133(4), 1645–1692. https://doi.org/10.1093/qje/qjy013 (abstract)
- Fraley, R. C., Waller, N. G., & Brennan, K. A. (2000). An item response theory analysis of self-report measures of adult attachment. *Journal of Personality and Social Psychology*, 78(2), 350–365. https://core.ac.uk/download/280124172.pdf (abstract)
- Iman, R. L., & Conover, W. J. (1982). A distribution-free approach to inducing rank correlation among input variables. *Communications in Statistics: Simulation and Computation*, 11(3), 311–334. https://doi.org/10.1080/03610918208812265 (abstract)
- Kaufman, S. B., Quilty, L. C., Grazioplene, R. G., Hirsh, J. B., Gray, J. R., Peterson, J. B., & DeYoung, C. G. (2016). Openness to experience and intellect differentially predict creative achievement in the arts and sciences. *Journal of Personality*, 84(2), 248–258. https://scottbarrykaufman.com/openness-to-experience-and-intellect-differentially-predict-creative-achievement-in-the-arts-and-sciences (abstract)
- McKay, M. D., Beckman, R. J., & Conover, W. J. (1979). A comparison of three methods for selecting values of input variables in the analysis of output from a computer code. *Technometrics*, 21(2), 239–245. https://doi.org/10.2307/1268522 (abstract and summaries)
- Noftle, E. E., & Shaver, P. R. (2006). Attachment dimensions and the Big Five personality traits: Associations and comparative ability to predict relationship quality. *Journal of Research in Personality*, 40(2), 179–208. https://adultattachment.faculty.ucdavis.edu/wp-content/uploads/sites/66/2015/09/Noftle_2006_Attachment-dimensions-and-the-big-five-personality-traits.pdf (full text; Study 1, Table 2 used)
- Roberti, J. W. (2004). A review of behavioral and biological correlates of sensation seeking. *Journal of Research in Personality*, 38(3), 256–279. https://doi.org/10.1016/S0092-6566(03)00067-9 (abstract)
- Saltelli, A., Ratto, M., Andres, T., Campolongo, F., Cariboni, J., Gatelli, D., Saisana, M., & Tarantola, S. (2008). *Global Sensitivity Analysis: The Primer*. Wiley. ISBN 978-0-470-05997-5. https://en.wikipedia.org/wiki/Global_Sensitivity_Analysis._The_Primer (bibliographic)
- Spector, I. P., Carey, M. P., & Steinberg, L. (1996). The Sexual Desire Inventory: Development, factor structure, and evidence of reliability. *Journal of Sex & Marital Therapy*, 22(3), 175–190. https://read.qxmd.com/read/8880651/the-sexual-desire-inventory-development-factor-structure-and-evidence-of-reliability (abstract)
- van der Linden, D., te Nijenhuis, J., & Bakker, A. B. (2010). The General Factor of Personality: A meta-analysis of Big Five intercorrelations and a criterion-related validity study. *Journal of Research in Personality*, 44(3), 315–327. https://doi.org/10.1016/j.jrp.2010.03.003 (abstract; the abstract gives N = 144,117, a later citing report gives 114,117)
- Zuckerman, M., Eysenck, S. B. G., & Eysenck, H. J. (1978). Sensation seeking in England and America: Cross-cultural, age, and sex comparisons. *Journal of Consulting and Clinical Psychology*, 46(1), 139–149. https://dlab.sauder.ubc.ca/sjdm/dmidi/Sensation%20Seeking%20Scale.html (citation level)

### Research carried from earlier repo notes (checked there)

From docs/notes/decision-weights-research.md: Birnie et al. 2009; Brown, Imai, Vieider & Camerer 2024; Carver & White 1994; Chapman, Snowberg, Wang & Camerer 2025; Fraley, Hudson, Heffernan & Segal 2015; Spielmann et al. 2013. From docs/notes/friendship-research.md: Gillath, Karantzas & Selçuk 2017; Leary, Kelly, Cottrell & Schreindorfer 2013; Pollet, Roberts & Dunbar 2011. Full references are in those notes.
