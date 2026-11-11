# Housing forms: what the research says, and a housing dimension for the n-agent world (2026-11-11)

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Status: a research note, not a result. It answers the author's question, logged 2026-11-11: "is the solution for some of it cheaper inidivual housing like apts or more shared housing like a big house? what does reserarch of urban planning etc say". The author approved this note and adding housing regimes as a dimension of the shared n-agent world (experiments/changes.jsonl, 2026-11-11T16:06:39Z). Nothing here changes code. Every number in the proposal is ASSUMED unless a source is named next to it.

Sources were checked by web search on 2026-11-11. Most papers were read at abstract level, marked "(abstract)". A few were read in part, marked "(read in part)". Books were not read; what they argue is taken from the publisher, catalog records and reviews, marked "(citation level)". Rent figures come from HUD's Fair Market Rents as reproduced by third-party mirrors, because huduser.gov would not serve the files to a script that day.

## 0. Why housing matters for this repo

**Our own results point at housing without modeling it.** Contact with friends is the biggest pleasure lever in the household world. Withdrawing from friends while paired hurts: −0.017 under the corrected formation rule (docs/results/h38-formation-check.md). The pattern atlas found "held" stay readings, where a member would leave but stays (docs/results/pattern-atlas.md). In the exit fallbacks, every contested exit was conceded by the partner who ran short of money, and the exit rule decided who was held (docs/results/exit-fallbacks.md).

**All four of those run through housing.** Where you live sets how often you see people, what leaving costs, and who keeps the roof. The world today has one housing form: a lumped bill, `BILLS = {2: 10, 1: 6, 0: 0}` per 4-week month, so two people pay 1.67 times what one does.

**The question has two halves.** Cheaper solo housing makes leaving cheaper. Shared housing makes contact cheaper. The research below says something about each, and much less about how they trade off.

## 1. What the research says, by strand

### Supply and zoning

**Land-use rules raise prices in many expensive places.** Glaeser and Gyourko compare house prices with the cost of building. Where prices sit far above construction cost, they read the gap as an implicit tax from regulation. Their conclusion is hedged: the evidence "suggests, without definitively proving", that this tax is larger in many areas than any plausible harm from new building (Glaeser & Gyourko 2018, abstract). The lead holds, with that hedge.

**New market-rate buildings lower nearby rents a little.** Large new apartment buildings in low-income US neighborhoods cut nearby rents by about 6% relative to slightly farther units, and drew in more movers from low-income areas (Asquith, Mast & Reed 2023, abstract; working-paper versions give 5–7%). The authors read it as a supply effect: new buildings absorb high-income households.

**San Francisco shows the same, smaller, with a twist.** Using building fires as random variation in where construction lands, Pennington finds rents fall $22.77–$43.18 a month, about 1.2–2.3%, within 500 m of a new market-rate project, and displacement risk falls 17.14%. Parcels within 100 m are also 29.5% more likely to gentrify. 100% affordable projects showed no spillover (Pennington 2021, read in part). It is a working paper; no journal version was found.

**What this strand does not say.** These are local effects of one building on its neighbors. They do not give the city-wide rent drop from changing zoning, and none of them was checked here. A world that sets "cheap solo units" is assuming a supply regime, not reproducing a measured one.

### Single-room occupancy and micro-units

**Residential hotels once housed many single people cheaply.** Groth's history covers residential hotels from palace hotels down to cheap lodging houses (Groth 1994, citation level). The claim that SROs were "regulated away" is widely attributed to this literature. The book was not read, so the note does not lean on the mechanism.

**The losses were large; the national total is not verified.** Secondary sources put losses in the 1970s and 1980s at over a million units nationally, and cite city figures: New York lost 87% of its SRO units from 1970 to 1983, Chicago over 23,000 from 1973 to 1984. These come from encyclopedia and advocacy summaries, not a primary count, so they are not used as numbers here. The lead's "Hoch & Slayton" attribution for the national figure could not be confirmed.

**Micro-units are cheaper per month and dearer per square foot.** In more than 400 apartment communities built in 2012–13 in 35 US metros, micro-units (typically about 350 sq ft) rented for about 20–30% less a month than conventional units, at a high rent per square foot, with higher occupancy (Urban Land Institute 2014, via secondary summaries). This is an industry study of new buildings, not of who lives in them or how they fare.

### Living alone is not the same as isolation

**More people live alone than ever.** 38.5 million US households, 29%, were one person in 2024, against 19% in 1974 (US Census Bureau 2024).

**Living alone and loneliness are different things.** Klinenberg argues that most people who live alone are socially and civically engaged, and that living alone is distinct from being isolated or lonely (Klinenberg 2012, citation level; critics said the picture is rosy). The lead holds as a description of the book.

**The mortality data agree, roughly.** In 70 studies (over 3 million people), the mortality odds ratio was 1.29 for social isolation, 1.26 for loneliness and 1.32 for living alone (Holt-Lunstad et al. 2015, abstract). In the earlier 148-study review, stronger social relationships went with an odds ratio of 1.50 for survival. The binary "living alone versus with others" measure was the weakest predictor, 1.19 with an interval that crosses 1 (0.99 to 1.44); complex measures of social integration were strongest, 1.91 (Holt-Lunstad, Smith & Layton 2010, abstract). Nearly all of these studies are observational.

**Most of the living-alone link runs through loneliness.** In English survey data on 20,500 adults aged 16–64, living alone went with higher odds of common mental disorders in each of three survey years (odds ratios 1.63 to 1.88). Loneliness accounted for 84% of that association (Jacob, Haro & Koyanagi 2019, abstract). Cross-sectional, so not causal.

**The model reading.** What matters is contact, not the address. A solo dweller who sees friends is not the isolated person in the mortality tables. That matches our own finding that friend contact is the main lever.

### Crowding and doubling up

**Crowding at home raises distress.** Residential crowding, measured as people per room, elevates psychological distress but does not produce serious mental illness (Evans 2003, abstract). The built environment also works indirectly, through personal control, social support and restoration from stress.

**The harm does not vary by culture.** Across 464 US residents of Anglo, African, Vietnamese and Mexican background, groups perceived crowding differently, but all showed similar distress from high-density housing, independent of income (Evans, Lepore & Allen 2000, abstract).

**Involuntary doubling-up costs both sides, the guest more.** Interviews with 60 parents in shared households found doubling up helped families meet daily needs, at a cost in time, energy and attention spent managing shared space and relationships, especially for guests (Harvey 2025, citation level). Qualitative and small. The lead's "Gary Evans" attribution covers crowding; for doubling up, Harvey is the better source.

### Shared housing: contact, conflict and privacy

**Proximity makes friends.** In the Westgate student housing project, friendships formed more often the closer people lived, sometimes by a few yards (Festinger, Schachter & Back 1950, citation level). This is the classic basis for "shared space creates contact". Old, one site, a homogeneous population.

**Sharing with unrelated housemates brings company and friction together.** In an Irish online survey, 71% of people sharing rented housing with unrelated housemates said they enjoy the company, 51% said they lack privacy (57% of women, 44% of men), and 49% sometimes or often disagree about chores (CSO Ireland 2021). The sample was self-selected (10,454 responses overall); the CSO says it cannot be generalized.

**Sharing does not reliably protect against loneliness.** Among 1,908 Australian private renters in mid-2020, people in shared housing were the most likely to report COVID-related worry (58.8%) and loneliness (47.7%), above people living alone (46.5% and 44.0%) and couples (Veeroja et al. 2023, read in part). Lockdown, and shared renters are younger and poorer, so this is not a clean comparison. It does rule out treating housemates as automatic contact.

### Cohousing

**Cohousing goes with more support and community, on weak evidence.** A scoping review kept 25 studies covering 77 cohousing projects, all in high-income countries. Eight of 10 studies on health or wellbeing found a positive association, and most of 22 studies on social support and sense of community did too. The authors rate the evidence quality as low: mostly cross-sectional or qualitative, no causal reading (Carrere et al. 2020, abstract).

**A second review finds the same.** 37 studies showed cohousing building ties within the group, and less so ties outward. Few studies had a non-cohousing comparison group (Warner, Sutton & Andrews 2020, abstract).

**Design or selection: not separated.** Williams asks how much design drives interaction in cohousing, against formal social structures, informal social factors and residents' own traits, and treats design as one factor among several (Williams 2005, abstract). No study found here compares cohousing residents with similar people who wanted cohousing and did not get it. People who choose cohousing want community. So the honest reading is: design plus selection plus governance, in unknown shares. The lead holds.

### Co-living

**There is little peer-reviewed evidence on commercial co-living.** Searches found industry blogs, policy commentary and one repository record of a Malaysian study whose review process could not be confirmed. The Australian shared-housing result above is the nearest peer-reviewed evidence, and it is not encouraging. The lead is corrected: it is not that the evidence is "commercial and young-adult"; it is that there is almost none.

### Housing costs and household formation

**High housing costs keep young adults with their parents.** Declining affordability explains up to a quarter of the 9-point rise in 18–29-year-olds living with parents from 2000 to 2021, with the effect strongest in the least affordable metros and only after 2000 (Acolin, Lin & Wachter 2024, abstract). Young adults in high house-price-growth areas in the 1997 cohort were about 15 points more likely to live with parents at 23 than the 1979 cohort in low-growth areas; housing costs and business-cycle conditions together explain up to 70% of the cohort gap in household formation (Cooper & Luengo-Prado 2016, abstract). The lead holds.

### Housing costs and splitting up

**House-price busts lowered divorce where people own, and raised it where they rent.** Across US metros, 1991–2010, falling prices went with lower divorce where homeownership was common and higher divorce where renting was common. The authors read this as owners being locked in by the cost of selling in a down market (Farnham, Schmidt & Sevak 2011, abstract). The lead is corrected: "busts lowered divorce" holds for owners only.

**For this repo, that is exit cost at work.** A cost of leaving that is tied to the home holds couples together. It does not say whether the held couples are better off.

### Living apart together

**A third of US adults who live without a partner have one.** Roughly one in three US adults who are neither married nor cohabiting are in a living-apart-together relationship and would be counted as single by household surveys. LAT partners reported similar emotional support but less practical support than cohabiters (Strohm et al. 2009, abstract). The lead holds.

**For this repo, LAT is pairing without nesting.** It is the arm H38b needs: a bond that does not share a roof, so leaving costs nothing in housing.

### Leaving abusive relationships

**Housing and money keep people in abusive relationships.** Among 164 survivors in US domestic violence programs, 73% said they stayed longer than they wanted or went back for economic reasons; 59% said the partner had hurt their credit, which blocked housing and loans (Hess & Del Rosario 2018). Not a representative sample. A UK survey report finds housing fears a significant barrier to leaving (Women's Aid 2020). Advocacy sources, small samples.

**After leaving, housing problems are common.** Of 110 women recruited through welfare agencies, shelters and the courts, a quarter to a half reported housing problems after separating, as later work summarizes it; problems were more likely after severe violence and with less support (Baker, Cook & Norris 2003, abstract and secondary citations).

**Housing help after leaving improves stability and safety.** In a quasi-experimental study of 406 homeless or unstably housed survivors in Washington State (344 in the 24-month analysis), the Domestic Violence Housing First model (advocacy plus flexible funds) improved housing stability, safety and mental health over services as usual, within six months and lasting to 24 months. It did not improve financial stability (Sullivan et al. 2023, abstract). Not randomized.

**The model reading, kept narrow.** Cheap, available housing is part of what makes exit possible for a dependent partner. That supports measuring exit power by runway, as the economy note proposes. It does not license any claim about abuse from a model with no abuse in it.

## 2. Cost per person and contact by housing form

Rents are HUD Fair Market Rents, FY2026, Washington-Arlington-Alexandria DC-VA-MD: the 40th percentile of gross rent (rent plus utilities) for standard units, monthly. Per-person figures divide by one person per bedroom, two for a couple in one room; that division is ours. One metro, one year. FY2027 rents took effect on 2026-10-01 and were not checked.

| Form | Monthly cost per person | Ratio to studio | Contact at home | Main costs | Sources |
|---|---|---|---|---|---|
| Studio, alone (costly solo) | $1,953 | 1.00 | None at home; contact depends on going out | Highest cost; no one to share with | HUD FMR FY2026 |
| One-bedroom, alone | $2,015 | 1.03 | None at home | As above | HUD FMR FY2026 |
| Micro-unit, alone | No direct figure; 20–30% below a conventional unit, so about 0.70–0.80 of a studio (our arithmetic) | ≈ 0.70–0.80 | None at home | Less space; high cost per sq ft | ULI 2014 (secondary) |
| SRO room | No data (no current comparable rents found) | — | Shared halls and baths; contact not measured | Shared facilities; little privacy | Groth 1994 (citation level) |
| Couple, one-bedroom | $1,008 | 0.52 | Partner daily | Exit means a new lease | HUD FMR FY2026 |
| Couple, two-bedroom | $1,123 | 0.58 | Partner daily | As above | HUD FMR FY2026 |
| Shared house, 3 bedrooms, 3 people | $945 | 0.48 | Housemates daily; quality varies | Privacy, chores, conflict | HUD FMR FY2026; CSO Ireland 2021 |
| Shared house, 4 bedrooms, 4 people | $833 | 0.43 | As above | As above, more | HUD FMR FY2026; CSO Ireland 2021 |
| Doubled-up family | No data | — | Constant | Crowding distress; guest bears more | Evans 2003; Harvey 2025 |
| Cohousing (private unit + common house) | No data found | — | More support and community, low-quality evidence | Buy-in, meetings, self-selection | Carrere et al. 2020; Warner et al. 2020 |
| Commercial co-living | No data (industry claims only) | — | Not measured in peer-reviewed work | — | — |

**Two things to take from the table.** First, sharing is the big saving. A four-person house costs each person 43% of a studio, far more than any supply effect measured above (1–7% locally). Second, the world's bill is off for couples. HUD's rents put a couple in a one-bedroom at about 1.03 times one person's studio, and a two-bedroom at 1.15. The world's 10:6 bills give 1.67. The economy note proposed 1.5; the data say lower.

## 3. A housing dimension for the n-agent world (PROPOSAL)

**Everything in this section is a proposal.** Each value is ASSUMED unless a source is named, and named sources set targets, not exact inputs. Units follow the economy note: `R1` is one person's weekly rent for a solo place, set at 30% of median full-time pay (docs/notes/economy-calibration.md, item 6).

**Each regime is set world-wide.** The world runs once per regime, same agents and seeds. Agents choose where to live within the regime's options.

**Four parameters per regime.**
1. Cost per person, as a multiple of `R1`.
2. Contact chances: free contact events per week with co-residents, on top of friend visits, which keep their time cost.
3. Privacy or conflict cost: a weekly suffering term that grows with the number sharing a space.
4. Exit: what leaving costs, who keeps the place, and how fast a new place is found.

### Regime A: costly solo (today)

- **Cost.** Solo place `R1`. A couple's place `1.15 × R1` total (HUD two-bedroom against studio), or the world's current 1.67 as a sensitivity arm.
- **Contact.** None from housing. All contact is friend visits, which cost time.
- **Privacy or conflict.** None alone; the partner's existing conflict terms when paired.
- **Exit.** The leaver needs a new solo place at `R1` plus a moving cost of one month's rent (ASSUMED). Who keeps the place follows the exit rule already in the world (the fallbacks F0–F5). Finding a place takes 0–4 weeks (ASSUMED). Runway, as in the economy note, decides whether the poorer partner is held.

### Regime B: cheap solo units

- **Cost.** Solo micro-unit `0.75 × R1` (the middle of ULI's 20–30% discount). Couples' places as in A.
- **Contact.** None from housing.
- **Privacy or conflict.** A small space cost, `s` per week while living alone in a micro-unit (ASSUMED, small); zero as a side arm.
- **Exit.** As in A, but at `0.75 × R1`, so runway is longer for everyone and longest, relatively, for the poorer partner. Living apart together is cheaper, so more pairs may choose it.

### Regime C: big shared houses

- **Cost.** A room in a house of `h` people at `(cost of an h-bedroom place) / h`. With HUD's ratios: `0.48 × R1` at `h` = 3, `0.43 × R1` at `h` = 4. A couple sharing one room in the house pays one room.
- **Contact.** `c` free contact chances a week with each housemate (ASSUMED, say 2). Housemates are not friends by default; a housemate tie must be built like any other.
- **Privacy or conflict.** A weekly conflict cost that rises with `h`, of the form `k × (h − 1)` (ASSUMED). The shape is from the crowding work (Evans 2003); the size is free. The CSO's 49% with chore disagreements is a rough target for how often conflict events fire.
- **Exit.** Rooms are leased one by one, so leaving a partner can mean moving to another room in the same house (if one is free) or to another house, at a moving cost of one week's room rent (ASSUMED). Nobody "keeps the house"; the house stays. The leaver loses housemate contact if they move out.

### Regime D: cohousing (private units plus a common house)

- **Cost.** A private unit at `0.75 × R1` plus a common-house share `0.10 × R1` (both ASSUMED; no cost data found).
- **Contact.** `c_common` contact chances a week with every resident (ASSUMED, below `c` in C, say 1), plus shared meals as events.
- **Privacy or conflict.** Low: a private unit removes daily friction. A small governance cost: one meeting a month, costing time (ASSUMED).
- **Exit.** Two versions, because the literature does not settle which is typical. Rented: like B, and the leaver can take a vacant unit in the same community if one exists (vacancy rate ASSUMED, say 5%), keeping common-house contact. Owned: the leaver must sell, at a cost of `x` weeks of income and a delay; this is the Farnham lock-in, and it should hold more couples.

### Known-answer checks the world should hit

These are checks on the world before any result is read, not results.

1. **Rent burden.** Under A, about half of single agents spend more than 30% of income on housing (JCHS 2025, via the economy note).
2. **Cost drives co-residence.** Moving from B to A should raise the share of agents not living alone, in the direction of Acolin et al. 2024 and Cooper & Luengo-Prado 2016. The size will not match; the sign must.
3. **Lock-in.** Owned cohousing (D-owned) should end fewer pairings than D-rented, in the direction of Farnham et al. 2011.
4. **Living alone is not isolation.** In B, the pleasure gap between solo and co-resident agents should mostly disappear once friend contact is controlled for (Holt-Lunstad et al. 2010: the binary living-alone measure is weak; Jacob et al. 2019: 84% runs through loneliness). If living alone carries a large penalty by itself, the world has hard-coded it.
5. **Crowding.** In C, distress per agent should rise with `h`, without collapsing pleasure (Evans 2003: distress, not serious illness).
6. **Housemates are not automatic friends.** In C, some agents should be lonelier than solo agents who visit friends (Veeroja et al. 2023). If every housemate counts as a friend, the check fails.
7. **Cheaper exit, fewer held.** The share of held stay readings should fall from A to B (direction only; consistent with Hess & Del Rosario 2018 and Sullivan et al. 2023, which are not about this model).

## 4. What a small model can and cannot claim

**It can show mechanisms.** For example: if cheaper solo units raise the poorer partner's runway above the hold threshold, fewer stay readings are held, given these agents and these costs. Or: if shared houses add contact but also conflict, there is an `h` past which pleasure falls. Both are statements about the model.

**It can compare regimes inside itself.** Same agents, same seeds, four regimes, judged on pleasure with everyone counted, on liberty minus domination, and on friend contact. Those comparisons are the strongest claims it can make.

**It can check itself against known directions.** The seven checks above. If it misses on direction, its comparisons are suspect.

**It cannot say what zoning would do.** The world sets rents; it has no builders, no land market and no supply response. "Cheap solo units" is a regime the world assumes, not one it produces.

**It cannot settle design versus selection in cohousing.** The real literature has not. The world's agents are placed in a regime; they do not self-select into it unless we make them, and then selection is ours.

**It cannot say anything about abuse.** The world has no violence and no coercion beyond holding. The exit evidence motivates measuring runway; it is not something the model tests.

**It cannot give numbers for people.** Agents are scripted personas with ASSUMED preferences. Contact chances, conflict costs and moving costs are free parameters. Any welfare number is a property of the model.

**With 4–6 agents, a shared house is most of the world.** In a regime-C world, the house and the social world nearly coincide. That says something about small communities, and little about a city.

## 5. Questions for the author

1. In shared houses, who are the housemates: strangers assigned by the world, or friends who choose to live together? Friends-as-housemates is closer to your question and to our friend-contact lever, but it bakes the contact in.
2. Should cohousing be rented or owned? Owned brings the Farnham lock-in, which lowers exit power; rented does not. The proposal runs both, but which is "cohousing" as you mean it?
3. Is "cheap solo" cheap because there is more supply (everyone's rent falls a little) or because units are smaller (a space cost)? The local evidence supports only small rent drops from supply; micro-units give the bigger saving, at a cost in space.

## Sources

### Official statistics

- U.S. Census Bureau (2024). Census Bureau Releases New Estimates on America's Families and Living Arrangements. Press release CB24-TPS-110, November 12, 2024. https://www.census.gov/newsroom/press-releases/2024/families-and-living-arrangements.html
- U.S. Department of Housing and Urban Development. FY2026 Fair Market Rents, Washington-Arlington-Alexandria, DC-VA-MD HUD Metro FMR Area: studio $1,953, 1BR $2,015, 2BR $2,246, 3BR $2,835, 4BR $3,332. Official home: https://www.huduser.gov/portal/datasets/fmr.html ; figures as reproduced by https://hud-rents.pages.dev/state/district-of-columbia/ and https://section8hq.pages.dev/fair-market-rent/virginia/fairfax-city/ (two mirrors agree; not checked on huduser.gov). Methodology: https://www.huduser.gov/portal/datasets/fmr/fmr2026/FY26-Public-FMR-Methodology.pdf
- Central Statistics Office, Ireland (2021). Pulse Survey — Life at Home 2021: Respondents who share rented accommodation with unrelated housemates. https://www.cso.ie/en/releasesandpublications/fp/fp-pslhrlpla/pulsesurvey-lifeathome2021rentersloneparentsandadultslivingaloneorwithaparent/respondentswhosharerentedaccommodationwithunrelatedhousemates

### Supply, SROs, micro-units

- Asquith, B. J., Mast, E., & Reed, D. (2023). Local effects of large new apartment buildings in low-income areas. *Review of Economics and Statistics*, 105(2), 359–375. https://doi.org/10.1162/rest_a_01055
- Glaeser, E., & Gyourko, J. (2018). The economic implications of housing supply. *Journal of Economic Perspectives*, 32(1), 3–30. https://doi.org/10.1257/jep.32.1.3
- Groth, P. (1994). *Living Downtown: The History of Residential Hotels in the United States*. University of California Press. https://publishing.cdlib.org/ucpressebooks/public/book/living-downtown-the-history-of-residential-hotels-in-the-united-states.html (citation level)
- Pennington, K. (2021). Does building new housing cause displacement? The supply and demand effects of construction in San Francisco. Working paper, UC Berkeley, August 9, 2021. https://gwern.net/doc/economics/georgism/2021-pennington.pdf (read in part: abstract and introduction)
- Urban Land Institute (2014). *The Macro View on Micro Units*. Summary: https://abag.ca.gov/technical-assistance/macro-view-micro-units ; coverage: https://www.bdcnetwork.com/home/news/55159046/uli-report-looks-at-growing-appeal-of-micro-unit-apartments (secondary summaries)

### Living alone, isolation, crowding

- Evans, G. W. (2003). The built environment and mental health. *Journal of Urban Health*, 80(4), 536–555. https://doi.org/10.1093/jurban/jtg063
- Evans, G. W., Lepore, S. J., & Allen, K. M. (2000). Cross-cultural differences in tolerance for crowding: Fact or fiction? *Journal of Personality and Social Psychology*, 79(2), 204–210. https://profiles.foxchase.org/en/publications/cross-cultural-differences-in-tolerance-for-crowding-fact-or-fict/
- Harvey, H. (2025). *Doubled Up: Shared Households and the Precarious Lives of Families*. Princeton University Press. https://press.princeton.edu/node/61893 (citation level)
- Holt-Lunstad, J., Smith, T. B., & Layton, J. B. (2010). Social relationships and mortality risk: A meta-analytic review. *PLoS Medicine*, 7(7), e1000316. https://doi.org/10.1371/journal.pmed.1000316
- Holt-Lunstad, J., Smith, T. B., Baker, M., Harris, T., & Stephenson, D. (2015). Loneliness and social isolation as risk factors for mortality: A meta-analytic review. *Perspectives on Psychological Science*, 10(2), 227–237. https://doi.org/10.1177/1745691614568352
- Jacob, L., Haro, J. M., & Koyanagi, A. (2019). Relationship between living alone and common mental disorders in the 1993, 2000 and 2007 National Psychiatric Morbidity Surveys. *PLoS ONE*, 14(5), e0215182. https://doi.org/10.1371/journal.pone.0215182
- Klinenberg, E. (2012). *Going Solo: The Extraordinary Rise and Surprising Appeal of Living Alone*. Penguin Press. https://casbs.stanford.edu/going-solo-extraordinary-rise-and-surprising-appeal-living-alone (citation level)

### Shared housing, cohousing, co-living

- Carrere, J., Reyes, A., Oliveras, L., Fernández, A., Peralta, A., Novoa, A. M., Pérez, K., & Borrell, C. (2020). The effects of cohousing model on people's health and wellbeing: A scoping review. *Public Health Reviews*, 41, 22. https://doi.org/10.1186/s40985-020-00138-1
- Festinger, L., Schachter, S., & Back, K. (1950). *Social Pressures in Informal Groups: A Study of Human Factors in Housing*. 1950; Stanford University Press reprint 1963. https://www.cambridge.org/core/books/personal-networks/from-leon-festinger-stanley-schachter-and-kurt-back-social-pressures-in-informal-groups/972AC3CBD43A5A6B66110393CA14C9DB (citation level)
- Veeroja, P., et al. (2023). Private renters in shared housing: Investigating housing conditions and mental well-being in Australia during COVID-19. *Journal of Housing and the Built Environment*, 38, 2285–2306. https://doi.org/10.1007/s10901-023-10038-w
- Warner, E., Sutton, E., & Andrews, F. (2020). Cohousing as a model for social health: A scoping review. *Cities & Health*, 107–119 (online 29 October 2020). https://doi.org/10.1080/23748834.2020.1838225
- Williams, J. (2005). Designing neighbourhoods for social interaction: The case of cohousing. *Journal of Urban Design*, 10(2), 195–227. https://doi.org/10.1080/13574800500086998

### Household formation, dissolution, LAT

- Acolin, A., Lin, D., & Wachter, S. (2024). Why do young adults coreside with their parents? *Real Estate Economics*, 52(1), 7–44. https://econpapers.repec.org/RePEc:bla:reesec:v:52:y:2024:i:1:p:7-44
- Cooper, D. H., & Luengo-Prado, M. J. (2016). Household formation over time: Evidence from two cohorts of young adults. Federal Reserve Bank of Boston Working Paper 16-17. https://www.bostonfed.org/publications/research-department-working-paper/2016/household-formation-over-time-evidence-from-two-cohorts-of-young-adults.aspx
- Farnham, M., Schmidt, L., & Sevak, P. (2011). House prices and marital stability. *American Economic Review*, 101(3), 615–619. https://ideas.repec.org/a/aea/aecrev/v101y2011i3p615-19.html
- Strohm, C. Q., Seltzer, J. A., Cochran, S. D., & Mays, V. M. (2009). "Living apart together" relationships in the United States. *Demographic Research*, 21(7), 177–214. https://www.demographic-research.org/volumes/vol21/7

### Leaving abusive relationships

- Baker, C. K., Cook, S. L., & Norris, F. H. (2003). Domestic violence and housing problems: A contextual analysis of women's help-seeking, received informal support, and formal system response. *Violence Against Women*, 9(7), 754–783. https://doi.org/10.1177/1077801203009007002
- Hess, C., & Del Rosario, A. (2018). *Dreams Deferred: A Survey on the Impact of Intimate Partner Violence on Survivors' Education, Careers, and Economic Security*. Institute for Women's Policy Research. https://iwpr.org/dreams-deferred-survey-release/
- Sullivan, C. M., et al. (2023). Domestic Violence Housing First: 24-month findings of a comparative effectiveness study. *JAMA Network Open* (title paraphrased; see the full text). Full text: https://wscadv.org/wp-content/uploads/2023/07/Sullivan-et-al-2023-DVHF-24-mo-findings-JAMA-Network-Open.pdf ; 12-month findings in *Journal of Interpersonal Violence* (2023): https://krimdok.uni-tuebingen.de/Record/1835662617
- Women's Aid (2020). *The Domestic Abuse Report 2020: The Hidden Housing Crisis*. https://www.womensaid.org.uk/wp-content/uploads/2020/06/The-Domestic-Abuse-Report-2020-The-Hidden-Housing-Crisis.pdf
