# Limits of the model world

One screen. Read it before you cite any result. Agents feel nothing: "pleasure" and "suffering" are glosses for a modeled state. Source: finding 6 of [reviews/2026-11-11-scope.md](reviews/2026-11-11-scope.md).

## The limits

**1. The partner is a script.** Fixed breach load (0.2), fixed leave rule, and a partner leaves only on distress (stay-test). Personas never learn, deceive or bargain.
Results cannot be about people, LLM delegates, or whether a norm survives a partner who adapts.
Fix: breach-cost agent (H05) and one adaptive partner, before the next rule-set comparison is cited. See [reviews/2026-11-11-scope.md](reviews/2026-11-11-scope.md), [results/stay-test.md](results/stay-test.md).

**2. The contact veto is inert.** The trap and contact_free arms give identical weeks.
Results cannot be about isolation as the cause of the trap's harm.
Fix: none planned. See [results/fidelity.md](results/fidelity.md) (P5).

**3. There is no crowding-out channel.** Defaults act only as threat points.
Results cannot be about rules whose risk is crowding out, so not the "rules versus training" contrast, and not a behavioral default effect.
Fix: none planned. See [results/fidelity.md](results/fidelity.md).

**4. The disagreement point sets negotiation signs.** v2 versus v2.1 flipped one.
Results cannot be about negotiation outcomes in general, only given the stated threat point.
Fix: none planned. See [results/fidelity.md](results/fidelity.md).

**5. Parameters are assumed.** About a third of multiverse conclusions are fragile or flip (the 3-week concert boundary does).
Results cannot be about a number, only about a pattern marked robust.
Fix: the multiverse check is required for any cited number. See [results/multiverse.md](results/multiverse.md).

**6. One author, one couple of days, one model family.** The data, the corrections and the parameter choices come from one person. The model, prereg, run and review come from one model family. Passing predictions about the builder's own equations (15 of 15) are code checks.
Results cannot be about other people, other labs or other models.
Fix: none planned. See [reviews/2026-11-11-scope.md](reviews/2026-11-11-scope.md).

**7. H32 depends on how the partner judges.** With a partner who averages over 4 weeks, 0 pattern cells. With one who judges week by week, 9.
Results cannot be about "exit moves the egoist" without naming the partner's judging rule.
Fix: reported as a band, not fixed. See [results/h32-v2.md](results/h32-v2.md).

**8. Designs can make a verdict impossible.** On ladder rungs L1 to L4 the formal model already reaches every harm kind, so no run could be classed inventive. H32 had too few open cells for "supported". Some classifier checks hold by construction. (A separate, earlier flaw: the first live ladder run had no victim, because one model drove both partners.)
Results cannot be about a clause that cannot fail.
Fix: the required "Can every verdict happen?" section in [templates/prereg.md](templates/prereg.md). See [negative-results.md](negative-results.md).

**9. The formal model reaches every harm on the old rungs.** On L1 to L4 the checker sees every harm those rules allow, so no agent can be inventive against them.
Results from those rungs cannot be about inventiveness. The IT1 rerun uses rungs where an inventive, paying seam is reachable (checked by a free gate) and is running now.
Fix: a deliberately narrower model, ladder only. See [plans/inventive-seam-next.md](plans/inventive-seam-next.md).

**10. Agents feel nothing, and the cast is three seats.** No scale, no network.
Results cannot be about felt experience, welfare of real beings, or scaling.
Fix: none planned. See [goal.md](goal.md).

**11. The household economy is a toy, and it overcharges couples.** Work is a flat money pump with near-equal pay (6 vs 5); one lumped bill; no job market, rent burden or savings buffer; and a couple pays 1.67 times a single person's bill, where HUD rents suggest about 1.03 to 1.15. Moving in looks costlier than it is, which may add to the under-forming found in [results/h38-formation-check.md](results/h38-formation-check.md).
Results cannot be about earnings gaps, rent burden, or how cost shapes who lives together.
Fix: a calibrated economy and housing regimes in the many-agent world (H40; [notes/economy-calibration.md](notes/economy-calibration.md), [notes/housing-research.md](notes/housing-research.md)).

**12. "Pairing" means only moving in with one fixed partner.** No romance, romantic priority, exclusivity or partner choice.
Results cannot be about amatonormativity or monogamy.
Fix: H38b in the many-agent world. See [results/h38-pairing-norms.md](results/h38-pairing-norms.md).

**13. Agents choose on one yardstick and are scored on another (partly resolved 2026-11-11; bill horizon tried 2026-11-12; resolved for the hybrid agent 2026-11-13).** The default agents (`agent_values="v1"`) agree with the hedonic model's own answer only loosely (rank correlation 0.43 over a week, 0.19 over a year). The recalibrated agents (`agent_values="v2"`, with `bills_hurt`) agree over one week almost exactly (0.99; best action right in 97% of decisions) and better over a year (0.68), but forecast one week, so a monthly bill is paid late, the pot drains, and few households form (16% of decisions inside a household, against 61%). The bill horizon (`agent_values="v2b"`, a payment credited by the settlement it feeds) fails its 4-week pass test the other way (over-values a payment by 0.03: it assumes nobody pays later) and brings households about halfway back (49% of decisions; G-L0 week-0 formation 0.42 against v1 0.84). Measured at 1, 4, 13 and 52 weeks, money, rest and bonds carry over little; the shared pot carries the long run (+0.72 of a bill payment's +1.00 over a year; +0.13 of work's +0.23 once households last).
Results run on v1 agents cannot be about how agents spend their weeks without this caveat. Results run on v2 or v2b cannot be about anything a forward-looking agent would do differently over months (bills, saving, forming a household); across v1, v2 and v2b, H38's old-rule effect of pressure went +0.021, −0.046, −0.003.
Fix: a month plan for the bill (the household sets each member's share once a month; tested by the same 4-week check), then a pot runway term (13-week check). Not a general planning horizon.
**Update 2026-11-13.** The hybrid agent (`agent_values="hybrid"`, with `satiety_expect="world"`) closes this for its big choices. It forms, stays, leaves and returns on the evaluator's own measure (mean pleasure on the saturating scale) over sampled futures, and bills are a household agreement. Its forecasts match held-out futures, and its one-week routine passes the value check. In the formation check's third run its households form at 0.91 and 7% end, and its pressure effect lands where the exact model puts it ([results/formation-check-3.md](results/formation-check-3.md)). Two parts remain open. First, its yardstick leaves out suffering by declaration, and held members suffer about three times as much. Second, results under v1, v2 or v2b keep the caveat above. Across the four sets, H38's pleasure sign is agent-dependent; only "pressure holds people in" holds under all of them. See [results/agent-bill-horizon.md](results/agent-bill-horizon.md), [results/agent-recalibration.md](results/agent-recalibration.md) and [results/value-consistency.md](results/value-consistency.md).

**Update 2026-11-13, later.** The hybrid can now weigh each person's suffering in its big choices (`hybrid_w="persona"`, hybrid prereg Amendment 3), and H41 ran with it ([results/h41-choice-aids.md](results/h41-choice-aids.md)). Two limits remain on this agent: its forecasts assume no leaving, so it cannot value an exit option, and a member left alone in the household has no reading to leave.

**Update 2026-11-13, Amendment 4.** Both now have a fix behind a flag ([results/hybrid-exit-option.md](results/hybrid-exit-option.md)): `hybrid_lone` gives the member left alone the pair's reading, and `hybrid_exit` lets future selves leave inside forecasts (a 13-week look-back against the outside option anchored at the choice). Under them the old checks pass, but the exit option's known answer (KX2, from the exact model) failed in its fixture, the in-future rule never leaves within 13 weeks (so trials cannot see it), and a new gap appeared: the routine can starve rest and connection, and no forecast sees it. Results on this version cannot be about an agent that values the option to leave the way the exact model's optimal chooser does.

## What results here CAN be about

- What a rule system does to scripted agents in a stated toy world.
- Exact, checkable facts: proofs, enumerations, what a model's equations imply.
- Patterns marked robust in the multiverse.
- Which designs and measures are broken, and why (the negative results).
- Where an idea would need a better model before it can be tested.
