# Time together: what the evidence says, and what it lets the model say

Research note, 2026-11-15. Written for the redesign of time together in the household world (prereg: [../results/time-together-prereg.md](../results/time-together-prereg.md)). Not a result. Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for modeled numbers.

**The question that started it (the author's, typos lightly fixed).** "shouldnt a person with a varied life not be hit as much as losing time together obviously its a good but how is it valued and suffered compared to other things that person could be doing and if they want to hang out they can and also how is time together measured like is sleeping or working together and other stuff transit dinner etc"

**The design the author confirmed** (read-back rb-2026-11-15-together, binding): "Time together comes in two kinds: background time from sharing a home (sleeping, dinner, errands, being in the same room) and chosen time (planned hangouts). Living apart keeps chosen time but loses most background time and adds travel. A person with many other sources of pleasure and friends is hit less by losing either."

**How the model does it today.** "together" is one abstract action: 2 of a member's 10 weekly time units, needing both partners. Living with the partner adds 0.10 a week to the connection need (`conn_cohabit`), against 0.30 for one chosen session (`conn_together`). Sleep, dinner, chores and transit are not modeled. Living apart together (LAT, H41) keeps the chosen action at the same cost, with no travel.

Strength labels: **strong** (large or repeated studies, the finding is not in dispute), **moderate** (one good study, or several with caveats), **weak** (small, old, cross-sectional or contested), **citation level** (read only through abstracts or later papers that cite it; the number has not been checked against the source).

## 1. How much time couples spend together, and what kind

**Couples without children share about 33 waking hours a week, most of it with nobody else there.** Flood and Genadek (2016) used the American Time Use Survey 2003–2010 (N = 46,883). They counted minutes in any activity that is not work, sleep or personal care, with the spouse present. Nonparents: 221 minutes on a weekday and about 440 on a weekend day (men 443, women 435). Of that, "exclusive" time (the spouse the only other person there) was 183 and 323 minutes. Parents: 197 / 411 total, but only 80 / 123 exclusive. Over a week that is about 33 hours for nonparents, of which about 26 are just the two. **Strong** for the amounts (a large national diary sample). The definition matters: it is co-presence, not a shared activity, and it leaves out sleep, work and personal care, because the survey does not ask who was there during those.

**Sleep and work are not in the standard measure at all.** ATUS does not record who is present during sleep or grooming, so no national figure says how much "sleeping together" there is or what it is worth. Small sleep studies find that bed-sharing changes sleep structure (for example more REM sleep in one lab study of 12 couples, Drews et al. 2020), and reviews describe couples' sleep as shaped by each other (Troxel 2010). **Weak** for any well-being effect, and nothing gives a number the model could use.

**Two-earner couples spend somewhat less time together, by about half an hour a day.** Kingston and Nock (1987) found this in a small 1981 sample; couples whose work schedules did not overlap spent less time together but shared housework more equally. Flood and Genadek (2016) found full-time dual earners about equal to breadwinner-homemaker couples on weekdays once the day's work hours are accounted for. **Moderate** for "work schedules, not job status, set the time".

**"Parallel" versus "companionship" time.** The leisure literature splits a couple's time into individual, parallel (same place, separate activities) and joint activities (Orthner 1975), and finds joint activity goes with marital satisfaction. **Citation level** (the original was not read). Survey diaries mostly cannot tell parallel from joint time: ATUS records who was present, not whether they were doing the thing together.

**No source separates "chosen" from "background" time.** Diaries record what and with whom, not whether the time was planned. The split the author confirmed is a modeling choice that the evidence neither confirms nor contradicts. The closest proxy is exclusive versus total time, and that is not the same thing (a couple watching TV alone together is exclusive and still background).

## 2. Which shared time matters for well-being

**Activities done with a spouse are rated happier, more meaningful and less stressful than the same person's activities without.** Flood and Genadek (2016), the ATUS Well-Being Module, three randomly chosen activities per respondent. Within the same person: odds of "very happy" 1.81 times higher with the spouse present, "very meaningful" 1.52, "any stress" 0.79. About 62–63% of activities with the spouse were rated very happy against about 49–51% without. **Moderate**: a large sample and within-person comparison, but only three activities a person, and the authors flag selection into the fixed-effects sample. It is a lift for *co-presence during ordinary activities*, which is what background time is.

**Commuting is the least pleasant activity of the day; intimate relations the most.** Kahneman, Krueger, Schkade, Schwarz and Stone (2004), the Day Reconstruction Method, 909 employed women in Texas: of 28 activity types, commuting rated lowest and intimate relations highest; housework, work and childcare were also near the bottom. Who one is with had a large effect on how an episode felt. **Moderate** (one convenience sample, but the method has been validated against experience sampling). The ranking of partner against friends in that paper was not checked here; this note does not rely on it.

**Meals and errands as distinct effects: no evidence that could be used.** The family-meal literature is mostly about children. Nothing found gives couples' shared meals, errands or sleep a separate well-being effect beyond "being with the spouse during the activity". So the model has no basis to split background time into meals, sleep and errands with different weights. **Decision: one background term.**

## 3. Living apart together

**LAT is a mixed group: mostly people who live apart for practical reasons, a minority who prefer it.** Levin (2004) defined LAT as a couple with an intimate relationship at two addresses, and described the preference form as having both intimacy and independence (keeping one's own home and networks). Duncan, Carter, Phillips, Roseneil and Stoilova (2013), a nationally representative British survey plus 2011 interviews: most live apart because of circumstances (jobs, money, children, "too early"), a minority by preference; LAT is both new and a continuation of older patterns. In Britain in 2011 about 9% of adults had a partner they did not live with (British Social Attitudes). In a 2006 British survey about 40% of LATs said they were "not ready" to live together. **Moderate.**

**Most LATs live near their partners and see them often.** Duncan, Phillips, Carter, Roseneil and Stoilova (2014). **Citation level for the figures**: the abstract says most live close with frequent contact; the distance bands in the paper's tables were not read. Krapf (2018), German panel data, called LAT "short distance" if the partners live under an hour apart and found long-distance couples less likely to move in together. **Citation level.**

**Travel costs time and, possibly, well-being.** Stutzer and Frey (2008), German panel: one standard deviation more commuting (18 minutes one way) lowers life satisfaction by 0.086 on 0–10, about an eighth of the effect of becoming unemployed, and higher pay or better housing did not offset it. A later UK study with fixed effects found no such link (Dickerson, Hole and Munford 2014). **Contested** for the well-being cost; **strong** that travel takes time. Commuting to work is not travelling to a partner, so this is an analogy.

**What LAT loses, in the terms of the confirmed design.** Background time needs a shared home. A LAT couple who see each other often may stay over, so some background time survives (an evening becomes a night and a breakfast). No source found gives that share.

## 4. Do friends and other pleasures substitute for a partner?

**Married people keep fewer ties with friends, neighbors and kin than single people.** Sarkisian and Gerstel (2016), US surveys (NSFH 1992–94; GSS 2000–2012): single people are more likely to stay in frequent touch with, and to give and get help from, parents, siblings, neighbors and friends; the gap is largest for the never married and survives structural controls. Gerstel and Sarkisian (2006) call this the "greedy" marriage. Kalmijn (2012), Dutch panel data, found that entering a union lowers contact with friends. **Moderate**: the US work is cross-sectional (cannot say marriage causes it), the panel evidence points the same way.

**This is substitution in the direction the author named.** People with a partner see friends less; people without one see friends more. It says that time and ties move between partner and friends. It does not say that a person rich in friends feels a lost partner less, which is the author's claim. Nothing found measures that directly. **The author's claim is plausible and unmeasured: ASSUMED.**

## What this lets the model do

| Design question | What the evidence supports | Strength | Model consequence |
|---|---|---|---|
| Split background time into meals, sleep, errands? | No distinct effects found; sleep is not even in the diaries | weak / none | **One background term** |
| How large is background time? | ~33 waking hours a week for couples without children, mostly just the two | strong | The hours are sourced; their value per hour is not |
| Is time with a partner better than time apart? | Yes, during ordinary activities: very happy 62% vs 50% | moderate | Background time counts as pleasure, not only connection |
| Value of a background hour against a chosen hour | Nothing found | none | **ASSUMED, swept** |
| Does LAT keep any background time? | Most LATs live close and meet often | citation level | **ASSUMED** small share kept, swept |
| LAT travel | Short-distance LAT is under an hour; travel takes time | moderate | Travel cost per chosen session, in time units, **ASSUMED** from "under an hour", swept |
| Does a varied life soften the loss? | Partnered people see friends less (substitution of time); no measure of felt loss | moderate / none | Routed through each persona's own weights (togetherness against other connections); **ASSUMED** form |

**The derivation used in the prereg** (every step is labeled there too):

1. Background hours, nonparent couples: 33 waking hours a week (Flood and Genadek 2016). Sourced.
2. A chosen session is one evening, about 3 hours (the friend-network design's ASSUMED visit length, docs/notes/friend-network-design.md). ASSUMED.
3. A background hour is worth q of a chosen hour. q = 0.1 (ASSUMED; no source). It is set so that the whole background week is worth about one chosen evening. Swept at a third and double.
4. Background, in chosen-session equivalents: 33 × 0.1 / 3 = **1.1 sessions a week**. Sweep: 0.33 (exactly the current `conn_cohabit` in connection terms, 0.10 / 0.30) and 2.2.

The model's time units are not hours in a consistent way: work is 4 units for about 34–40 hours a week (economy note), while a 2-unit visit is about 3 hours (friend-network note). This note therefore states travel relative to a chosen session, not in hours per unit: a 30-minute trip each way is 1 hour for the one who travels, 0.5 hours per member on average if they take turns hosting, which is 1/6 of a 3-hour session, or **0.33 time units per member per LAT session** (sessions cost 2 units). ASSUMED from "short distance is under an hour"; swept at 15 minutes (0.17) and an hour (0.67) each way.

## Open, not settled by anything here

- Whether chosen and background time are separate goods at all. The diaries cannot tell.
- The value of a background hour (q). The single most influential number, and unsourced.
- Whether co-sleeping is a pleasure, a cost or neither.
- Whether a person with many friends feels the loss of a partner's company less (the confirmed design says yes; no study found measures it).
- Travel's well-being cost beyond time (contested for commuting; not studied for partner visits).

## Sources

- Dickerson, A., Hole, A. R., & Munford, L. A. (2014). The relationship between well-being and commuting revisited: Does the choice of methodology matter? *Regional Science and Urban Economics*, 49, 321–329. (citation level)
- Drews, H. J., et al. (2020). Bed-sharing in couples is associated with increased and stabilized REM sleep and sleep-stage synchronization. *Frontiers in Psychiatry*, 11, 583. (citation level)
- Duncan, S., Carter, J., Phillips, M., Roseneil, S., & Stoilova, M. (2013). Why do people live apart together? *Families, Relationships and Societies*, 2(3), 323–338. https://uwe-repository.worktribe.com/output/931170
- Duncan, S., Phillips, M., Carter, J., Roseneil, S., & Stoilova, M. (2014). Practices and perceptions of living apart together. *Family Science*, 5(1), 1–10. https://doi.org/10.1080/19424620.2014.927382
- Flood, S. M., & Genadek, K. R. (2016). Time for each other: Work and family constraints among couples. *Journal of Marriage and Family*, 78(1), 142–164. https://pmc.ncbi.nlm.nih.gov/articles/PMC4712716
- Genadek, K. R., Flood, S. M., & Moen, P. (2019). For better or worse? Couples' time together in encore adulthood. *Journals of Gerontology: Series B*. (citation level)
- Gerstel, N., & Sarkisian, N. (2006). Marriage: The good, the bad, and the greedy. *Contexts*, 5(4), 16–21. (citation level)
- Kahneman, D., Krueger, A. B., Schkade, D. A., Schwarz, N., & Stone, A. A. (2004). A survey method for characterizing daily life experience: The day reconstruction method. *Science*, 306(5702), 1776–1780.
- Kalmijn, M. (2012). Longitudinal analyses of the effects of age, marriage, and parenthood on social contacts and support. *Advances in Life Course Research*, 17(4), 177–190. (citation level)
- Kingston, P. W., & Nock, S. L. (1987). Time together among dual-earner couples. *American Sociological Review*, 52(3), 391–400. (citation level)
- Krapf, S. (2018). Moving in or breaking up? The role of distance in the development of romantic relationships. *European Journal of Population*, 34, 313–336. https://link.springer.com/content/pdf/10.1007%2Fs10680-017-9428-2.pdf (citation level)
- Levin, I. (2004). Living apart together: A new family form. *Current Sociology*, 52(2), 223–240.
- Orthner, D. K. (1975). Leisure activity patterns and marital satisfaction over the marital career. *Journal of Marriage and the Family*, 37(1), 91–102. (citation level)
- Sarkisian, N., & Gerstel, N. (2016). Does singlehood isolate or integrate? Examining the link between marital status and ties to kin, friends, and neighbors. *Journal of Social and Personal Relationships*, 33(3), 361–384.
- Stutzer, A., & Frey, B. S. (2008). Stress that doesn't pay: The commuting paradox. *Scandinavian Journal of Economics*, 110(2), 339–366.
- Troxel, W. M. (2010). It's more than sex: Exploring the dyadic nature of sleep and implications for health. *Psychosomatic Medicine*, 72(6), 578–586. (citation level)
