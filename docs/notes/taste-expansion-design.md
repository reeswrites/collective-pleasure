# Taste expansion: how the taste menu could enter the model (draft)

Status: DRAFT by Claude, 2026-11-15, for the author to confirm (read-backs rb-2026-11-15-taste in experiments/readbacks.jsonl). Nothing here is built. Quotes are the author's, verbatim, from the Notion page "Exploration Mapping: A taste expansion application framework" (2026-08-25, labelled author-written in docs/notes/persona-generator-design.md). Everything not in quotation marks is Claude's drafting, not the author's words.

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

## Open questions for the author

1. Is a try mainly a time cost, or can it hurt (a bad experience)?
2. Does depth come only from returning to a thing, or also from understanding it (learning about it)?
3. Do domains connect, so trying one widens a neighbouring one ("cross domain connections")?
4. Should hard constraints (things a person will never try) be part of a persona, following "pref modeling doesn’t really work but having hard constraints does"?

Every number this needs (try cost, join chance, depth gain) would be marked ASSUMED, sourced where possible from research on exposure and acquired taste, set before runs and swept.
