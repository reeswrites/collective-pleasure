# Friendship: what the research says about depth, history, fading, needs and isolation (2026-11-13)

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Status: a research note, not a result. Part 1 of H42 (experiments/hypotheses.jsonl). It answers the author's confirmed read-back rb-2026-11-13-friends (experiments/readbacks.jsonl): friends come at different depths, meet different needs, old ones differ from new ones, ties fade and can be picked back up, and people differ in how much friends matter. The design that uses it is docs/notes/friend-network-design.md. Nothing here changes code.

Sources were checked on 2026-11-13. Every citation below was confirmed to exist by its DOI record (Crossref) or the publisher's page. How much of each was read is marked:

- "(read in part)": the full text was opened and the cited part read.
- "(abstract)": only the abstract, or the abstract plus a catalog record.
- "(secondary)": the claim comes from a press release, a review or another paper describing it, not from the paper.
- "(citation level)": only that the work exists and what it is about.

No number below was made up. Where a number is quoted, the read level next to it says where it came from.

## 0. Why friendship matters for this repo

**Friend contact is already the biggest pleasure lever in the household world.** Unbundled bonds alone raised pleasure by +0.043 (docs/results/pleasure-levers.md). Withdrawal from friends while paired lowered it under v1 (docs/results/formation-check-3.md).

**But the friend model is thin.** L-C gives each agent one to five external bonds with a quality `qx` that rises with visits and falls 5% a week (src/mar/hedonic.py, `LeverConfig`). A bond has no history. A friend of ten years and a friend of ten weeks fade and recover alike. Friends are not agents: nobody counts what the friend loses when someone withdraws.

**And withdrawal does something we cannot yet read.** In one formation-check story, withdrawal kept a member in who would otherwise have left (formation-check-3.md, story 2). The exact model cannot produce that, because its withdrawal only makes living together worse (docs/results/h38-exact-model.md). A friend network that can shrink is one way withdrawal could hold someone in: by shrinking the life they would leave to.

## 1. What the research says, by strand

### Depth comes in layers, roughly 5 / 15 / 50 / 150

**The layer claim.** Personal networks are said to form nested layers of about 5, 15, 50 and 150 people, each about three times the one inside it, with closeness and contact falling outward. Sutcliffe, Dunbar, Binder & Arrow (2012) state it this way and add a cost argument: at each layer the benefits level off while the time cost grows roughly in line with the number of ties (abstract). They also argue that different layers serve different functions.

**Where the numbers come from.** Zhou, Sornette, Hill & Dunbar (2005) found a discrete hierarchy of group sizes with a scaling ratio near three (abstract and secondary). Hill & Dunbar (2003) counted Christmas-card networks: a mean maximum network of 153.5 people, and 124.9 for those explicitly contacted (abstract, via secondary). Phone and online data show layers too. Mac Carron, Kaski & Dunbar (2016) found strong evidence of layers in call frequencies; the innermost and outermost matched earlier sizes, the middle layers varied a lot (abstract). Dunbar, Arnaboldi, Conti & Passarella (2015) found similar layers in Facebook and Twitter data from more than 185,000 egos (abstract, secondary).

**The 150 rests on a weak base.** The 150 was extrapolated from a primate regression of group size on neocortex size. Lindenfors, Wartel & Lind (2021) redid it with larger data and modern methods. Their preferred model gives 69.2 with a 95% interval of 3.8 to 292.0; other models in their main table range from 16.4 to 108.6, with intervals whose lower ends sit near 2 to 5 and upper ends reach 520. They conclude that no specific number can be derived this way (read in part: abstract and Table 1). de Ruiter, Weston & Lyon (2011) argue on cross-cultural grounds that brain size cannot explain human group size (abstract).

**What survives the critique.** The critique hits the brain-to-150 inference, not the observation that people sort ties into a few depths with fewer close ones than distant ones. The layer *shape* (few close, more medium, many distant) has independent support from cards, calls and posts. The exact *sizes* do not.

**Reading for the model.** Tiers are well supported as a shape. A model should let layer sizes come out of time budgets, not fix them at 5/15/50/150.

### New friends take real time: Hall's hours

**The study.** Hall (2019) asked how many hours it takes to make a friend. Study 1: 355 adults who had recently moved estimated time spent with a new acquaintance. Study 2: 112 first-year students reported hours with two new acquaintances three times over 9 weeks. Hours together predicted closeness; leisure time predicted it more than other time, and two kinds of everyday talk predicted changes (abstract).

**The numbers are press-release level.** The University of Kansas release gives, across both studies, about 40 to 60 hours for a casual friend, 80 to 100 hours for a friend, and more than 200 hours for a good friend (secondary). The release also says "roughly 50 hours" to casual friend and "90 hours" to friend, worded so that it is unclear whether 90 is cumulative. Other summaries online give different figures. The thresholds were not checked in the paper.

**Reading for the model.** New ties build over months of contact, not weeks. The ordering (casual well before friend, close far later) is solid; the exact hours are not. Time spent working together counts less than leisure.

### Ties fade without contact, friends faster than kin

**Roberts & Dunbar (2011).** Twenty-five students were followed for 18 months as they left school. The emotional intensity of friendships was more affected by falling contact and fewer shared activities than that of kin ties. The authors conclude that friendships cost much more to maintain than kin relations (abstract).

**The same data in more detail.** Roberts & Dunbar (2015) analyze 1,291 network members of those 25 students. Over 18 months, closeness to kin rose and closeness to friends fell. Of kin in the inner layer at the start, 70.3% (102 of 145) were still there at the end; of friends, 48.6% (69 of 142). Effort slowed friends' decline: for women more frequent contact did the most, for men shared activities (read in part).

**Other estimates point the same way.** High school best friendships declined in satisfaction and commitment in the first college year; the amount of communication, not distance, moderated the decline (Oswald & Clark 2003, abstract). Burt (2000) modeled the decay of colleague ties among bankers over four years (citation level; no rate taken from it). Saramäki et al. (2014) found that each person keeps a stable "social signature", a fixed way of spreading calls over contacts, even while the people in it change: new contacts took old ones' places (abstract and secondary).

**What no source here gives.** A weekly decay rate for a friend at a given depth. The studies show direction (friends fade without contact, contact slows it) and a rough size over 18 months for young people moving away. Any per-week rate in the model is ASSUMED.

### Old ties can be picked back up: dormant ties

**The study.** Levin, Walter & Murnighan (2011) asked 224 executives to reconnect with two people they had not talked to in at least three years, one formerly strong tie and one formerly weak; 129 completed both surveys. Reconnected dormant ties compared well with current ties as sources of useful knowledge. Formerly strong dormant ties took less time to consult than current strong ties and brought more novelty, while keeping trust and shared perspective (read in part).

**Strong ties keep most of their strength.** The authors read their data as strong ties retaining most of their strength years later, with "some" decay of trust and shared perspective against current strong ties (read in part). They quote Granovetter (1992): a reactivated relationship does not start from scratch. In follow-up analyses, ties dormant three years did not differ from ties dormant longer (read in part).

**Limits.** The executives chose whom to reconnect with, so these are hopeful picks, not a random draw. The outcome was work advice, not friendship or pleasure. A later paper by the same team found that people prefer to reconnect with those they spent much time with in the past, and that reconnecting can make people anxious (secondary).

**Reading for the model.** History is a separate stock from current closeness. Current closeness fades; history mostly stays and makes reactivation fast. That is the read-back's "easier to come back to after time apart", and it is the best-supported part of it.

### Different people for different needs

**Emotionships.** Cheung, Gardner & Anderson (2015) showed that people name distinct people for distinct emotions (who cheers them up when sad, who calms them when anxious). People who spread these needs across several specialized relationships had higher well-being than people with a similar number of close relationships who leaned on fewer, less specialized ones (abstract).

**Layers serve different functions.** Sutcliffe et al. (2012) make the same point at the network level: different layers do different jobs (abstract).

**What is not shown.** The emotionship finding is about emotion regulation, not about fun, advice or logistics, and it is correlational. That diversity *causes* well-being is not shown. The read-back's list of itches (fun, care, intimacy, advice, logistics) is the author's, not a measured taxonomy.

**Reading for the model.** L-C's strand cover already rewards spreading strands across bonds. The research supports keeping that, at the size of a correlational finding.

### Weak ties count too

**Granovetter (1973).** The strength of a tie tracks how much two people's friendship networks overlap; weak ties bridge between groups and carry information that close ties do not (abstract).

**Sandstrom & Dunn (2014).** On days when students talked with more classmates than usual, they reported more happiness and belonging. Across all daily interactions, weak-tie interactions were related to social and emotional well-being (abstract). Correlational.

**Reading for the model.** Acquaintances are not worthless. They give a small belonging and mood term and new information. They do not supply care.

### Pairing and friend networks: dyadic withdrawal

**The hypothesis.** Johnson & Leslie (1982) named the "dyadic withdrawal hypothesis": as a couple becomes more involved, its members withdraw from wider networks (citation level; the title is checked, the findings were not read). Milardo (1982) studied converging and diverging friend networks in developing relationships (citation level).

**Survey evidence.** Kalmijn (2003), with Dutch survey data on each partner's five best friends, found friendship networks shrink over the life course, mainly when people start dating and when they marry, and that shared friends become more tied together once couples live together (abstract, secondary). Kalmijn (2012), on 12 years of Swiss panel data, found that parenthood shifts ties toward neighbors and away from friends, and that divorce and widowhood go with more contact and support (abstract, secondary).

**Singles are more connected, not less.** Sarkisian & Gerstel (2016), with US survey data, found single people more likely than married people to stay in touch with, help and be helped by parents, siblings, neighbors and friends. Much of the gap remained after structural controls. The gap was larger for the never-married than the previously married, which they read as marriage reaching past its own end (abstract).

**A cost in numbers.** Burton-Chellew & Dunbar (2015), with 540 internet respondents, found smaller support networks for people in a romantic relationship. Net of gaining the partner, the cost was the loss of nearly two members; children cut networks further for people under 36 (abstract, via the Oxford record and secondary).

**Reading for the model.** Pairing goes with fewer friends and more overlap with the partner's friends. These are associations, not causes: people who pair may differ. The direction is consistent across four sources.

### Breakups and who keeps the friends

**Divorce reshapes networks, in both directions.** Kalmijn & Broese van Groenou (2005) found divorced people had more friend contact and more participation in some groups than married people, but lower social integration overall; the effects were weaker than commonly believed (abstract, secondary). Later work cites them for divorce disrupting joint, couple-based ties (secondary).

**Losses depend on the breakup.** Terhell, Broese van Groenou & van Tilburg (2004) followed 104 people for 12 years after divorce. They found distinct patterns of network-size change, partly explained by attitude toward the divorce and conflict with the ex-partner (abstract). A secondary source says most lost members soon after, and about half never made up the loss; that was not checked.

**Divorce clusters in friend networks.** McDermott, Fowler & Christakis (2013), with Framingham data, found divorce spreads between friends up to two degrees, and divorcées have denser networks (abstract).

**Who keeps the mutual friends: no good evidence found.** No study found here measures how shared friends divide between two ex-partners. Figures circulating online (for example a share who stay friends with both) could not be traced to a checked source and are not used.

**Reading for the model.** A breakup should cost shared ties, more with conflict, and some ties should stay with both. How they divide is an ASSUMED rule.

### People differ in how much they value friends

**Need to belong.** Baumeister & Leary (1995) argue that the need to belong is a fundamental, pervasive motive (abstract). Leary, Kelly, Cottrell & Schreindorfer (2013) validated a scale for individual differences in it, and found that how much someone needs to belong is distinct from how well that need is met (abstract).

**Extraversion: bigger layers, not closer ones.** Pollet, Roberts & Dunbar (2011), with 117 people, found extraverts had larger networks at every layer, with small correlations (r between .20 and .23), but were not emotionally closer to anyone (abstract, secondary). A review finds agreeableness has the most consistent effects on friendship and romance, then neuroticism; effects of extraversion are inconsistent (Harris & Vazire 2016, abstract).

**Attachment.** Gillath, Karantzas & Selçuk (2017) found people high on attachment avoidance were less likely to start and keep ties and more likely to end them; priming security made people more likely to start ties and less likely to end them (abstract, secondary for details).

**Reading for the model.** Variation is real and has three parts that need not move together: how much friends matter (need to belong), how many ties a person runs (extraversion, small), and how readily they start and keep ties (attachment). None of these sources gives a distribution in model units.

### Loneliness is not the number of friends

**Quality over count.** A meta-analysis of older adults found loneliness tracks the quality of the network more than its size, and contact with friends and neighbors more than contact with family (Pinquart & Sörensen 2001, abstract via secondary).

**Number of close friends, then satisfaction.** In a US life-span sample, the number of close friends was the main network driver of well-being, but well-being tracked satisfaction with relationships more than the count (Bruine de Bruin, Parker & Strough 2020, abstract).

**Size still matters a bit.** In a Chicago sample aged 50 to 68, small networks, no spousal confidant and poor-quality relationships were each independent risk factors for loneliness (Hawkley et al. 2008, abstract). For young adults, network size and having a close other predicted social loneliness; for older adults, the average closeness of the network did (Green et al. 2001, abstract). Emotional loneliness tracked having a romantic partner in both groups.

**Reading for the model.** Pleasure from friends should depend on depth and on needs being met, not on a count. A count is a weak proxy.

### Isolation in coercive control (kept short)

**Isolation is a named tactic.** Stark (2007) describes coercive control as a pattern that includes cutting a partner off from friends, family and other support, alongside intimidation and control of resources (citation level). UK statutory guidance for the controlling or coercive behaviour offence (Serious Crime Act 2015, section 76) lists "Isolating the victim from family, friends, colleagues and professionals" among restrictive behaviours (Home Office 2023, read in part).

**An association with violence, narrowly.** Using US survey data, Lanier & Maume (2009) found some measures of social isolation predicted intimate partner violence, only in rural counties (abstract).

**Reading for the model.** Isolation is recognized as a means of control. That motivates measuring how many ties a person could turn to if they left. It does not license any claim about abuse from a model that has none.

## 2. What the research gives the model, in one table

| Model piece | Support | Strength |
|---|---|---|
| Tiers of depth, few close and many distant | Sutcliffe 2012; Zhou 2005; Mac Carron 2016; Dunbar 2015 | Solid as a shape; sizes not |
| Layer sizes 5/15/50/150 | Hill & Dunbar 2003; critique Lindenfors 2021, de Ruiter 2011 | Weak; do not fix them |
| New ties take months (tens to hundreds of hours) | Hall 2019 | Ordering solid; hour figures press-release level |
| Friends fade without contact; contact slows it | Roberts & Dunbar 2011, 2015; Oswald & Clark 2003 | Direction solid; no weekly rate |
| Friends fade faster than kin | Roberts & Dunbar 2011, 2015 | Solid, small young sample |
| History persists; old strong ties reactivate fast | Levin et al. 2011 | Moderate; chosen ties, work outcomes |
| Different people for different needs | Cheung et al. 2015; Sutcliffe 2012 | Moderate; correlational |
| Weak ties add a little | Sandstrom & Dunn 2014; Granovetter 1973 | Moderate; correlational |
| Pairing shrinks friend networks | Kalmijn 2003; Burton-Chellew & Dunbar 2015; Sarkisian & Gerstel 2016 | Direction consistent; not causal |
| Breakups cost shared ties, more with conflict | Kalmijn & Broese van Groenou 2005; Terhell 2004 | Moderate |
| How mutual friends split | none found | Gap; ASSUMED rule |
| People differ in how much friends matter | Leary 2013; Pollet 2011; Gillath 2017; Harris & Vazire 2016 | Real; no distribution in model units |
| Loneliness tracks quality more than count | Pinquart & Sörensen 2001; Bruine de Bruin 2020; Hawkley 2008 | Moderate to solid |
| Isolation as a means of control | Stark 2007; Home Office 2023 | Recognized; not a model claim |

## 3. What a small model can and cannot claim

**It can show mechanisms.** For example: if old ties keep a history stock and new ties need months, then a member who withdraws for two years leaves with fewer reachable friends than they entered with, given these rates. That is a statement about the model.

**It can compare rules inside itself.** Same agents, same seeds, with and without withdrawal, with and without a breakup rule, judged on pleasure with friends counted, on freedom and on the isolation measure.

**It can check itself against directions.** Friends fade without contact; old ties come back faster than new ones form; pairing shrinks friend contact; singles see more friends. If the model misses a direction, its comparisons are suspect.

**It cannot give rates for people.** No source gives a weekly decay rate, a reactivation speed in weeks or a split rule for mutual friends. Those are ASSUMED. Hall's hours are a rough calibration of formation time, from a press release.

**It cannot say how many friends a person has.** The 150 is not a constant. In a world of 4 to 6 agents, most of anyone's network has to be background friends, not agents.

**It cannot say anything about abuse.** The world has no coercion beyond holding and withdrawal. The isolation evidence motivates a measure; it is not tested.

**It cannot settle cause.** Most of the pairing and loneliness evidence is cross-sectional or correlational. The model builds a causal story in; it does not discover one.

## 4. Questions for the author

1. Your list of itches is fun, care, intimacy, advice and logistics. L-C's strands are care, affection, intimacy, logistics, commitment and desire. Is "fun" what affection meant, or a new strand? Is "advice" new?
2. The read-back says old friends are easy to come back to; H42 says withdrawal's harm outlasts the relationship because old ties are slow to rebuild. The research supports the first for strong old ties. Should the harm come instead from new ties never made and from friends who moved on, which the research also supports?
3. Should "how much someone values friends" be one number, or should it be split as the research splits it: how much friends matter, how many ties someone runs, and how readily they start and keep them?

## Sources

### Layers and network size

- de Ruiter, J., Weston, G., & Lyon, S. M. (2011). Dunbar's number: Group size and brain physiology in humans reexamined. *American Anthropologist*, 113(4), 557–568. https://doi.org/10.1111/j.1548-1433.2011.01369.x (abstract)
- Dunbar, R. I. M., Arnaboldi, V., Conti, M., & Passarella, A. (2015). The structure of online social networks mirrors those in the offline world. *Social Networks*, 43, 39–47. https://doi.org/10.1016/j.socnet.2015.04.005 (abstract, secondary)
- Hill, R. A., & Dunbar, R. I. M. (2003). Social network size in humans. *Human Nature*, 14(1), 53–72. https://doi.org/10.1007/s12110-003-1016-y (abstract via secondary)
- Lindenfors, P., Wartel, A., & Lind, J. (2021). 'Dunbar's number' deconstructed. *Biology Letters*, 17(5), 20210158. https://doi.org/10.1098/rsbl.2021.0158 (read in part)
- Mac Carron, P., Kaski, K., & Dunbar, R. (2016). Calling Dunbar's numbers. *Social Networks*, 47, 151–155. https://doi.org/10.1016/j.socnet.2016.06.003 (abstract)
- Sutcliffe, A., Dunbar, R., Binder, J., & Arrow, H. (2012). Relationships and the social brain: Integrating psychological and evolutionary perspectives. *British Journal of Psychology*, 103(2), 149–168. https://doi.org/10.1111/j.2044-8295.2011.02061.x (abstract)
- Zhou, W.-X., Sornette, D., Hill, R. A., & Dunbar, R. I. M. (2005). Discrete hierarchical organization of social group sizes. *Proceedings of the Royal Society B*, 272(1561), 439–444. https://doi.org/10.1098/rspb.2004.2970 (abstract, secondary)

### Formation, decay and reconnection

- Burt, R. S. (2000). Decay functions. *Social Networks*, 22(1), 1–28. https://doi.org/10.1016/S0378-8733(99)00015-5 (citation level)
- Hall, J. A. (2019). How many hours does it take to make a friend? *Journal of Social and Personal Relationships*, 36(4), 1278–1296. https://doi.org/10.1177/0265407518761225 (abstract; hour figures from the University of Kansas release, https://news.ku.edu/news/article/2018/03/06/study-reveals-number-hours-it-takes-make-friend, secondary)
- Levin, D. Z., Walter, J., & Murnighan, J. K. (2011). Dormant ties: The value of reconnecting. *Organization Science*, 22(4), 923–939. https://doi.org/10.1287/orsc.1100.0576 (read in part)
- Oswald, D. L., & Clark, E. M. (2003). Best friends forever? High school best friendships and the transition to college. *Personal Relationships*, 10(2), 187–196. https://doi.org/10.1111/1475-6811.00045 (abstract)
- Roberts, S. G. B., & Dunbar, R. I. M. (2011). The costs of family and friends: An 18-month longitudinal study of relationship maintenance and decay. *Evolution and Human Behavior*, 32(3), 186–197. https://doi.org/10.1016/j.evolhumbehav.2010.08.005 (abstract)
- Roberts, S. G. B., & Dunbar, R. I. M. (2011). Communication in social networks: Effects of kinship, network size, and emotional closeness. *Personal Relationships*, 18(3), 439–452. https://doi.org/10.1111/j.1475-6811.2010.01310.x (citation level)
- Roberts, S. G. B., & Dunbar, R. I. M. (2015). Managing relationship decay: Network, gender, and contextual effects. *Human Nature*, 26(4), 426–450. https://doi.org/10.1007/s12110-015-9242-7 (read in part, open access: https://pmc.ncbi.nlm.nih.gov/articles/PMC4626528)
- Saramäki, J., Leicht, E. A., López, E., Roberts, S. G. B., Reed-Tsochas, F., & Dunbar, R. I. M. (2014). Persistence of social signatures in human communication. *PNAS*, 111(3), 942–947. https://doi.org/10.1073/pnas.1308540110 (abstract, secondary)

### Needs, weak ties and loneliness

- Bruine de Bruin, W., Parker, A. M., & Strough, J. (2020). Age differences in reported social networks and well-being. *Psychology and Aging*, 35(2), 159–168. https://doi.org/10.1037/pag0000415 (abstract)
- Cheung, E. O., Gardner, W. L., & Anderson, J. F. (2015). Emotionships: Examining people's emotion-regulation relationships and their consequences for well-being. *Social Psychological and Personality Science*, 6(4), 407–414. https://doi.org/10.1177/1948550614564223 (abstract)
- Granovetter, M. S. (1973). The strength of weak ties. *American Journal of Sociology*, 78(6), 1360–1380. https://doi.org/10.1086/225469 (abstract)
- Green, L. R., Richardson, D. S., Lago, T., & Schatten-Jones, E. C. (2001). Network correlates of social and emotional loneliness in young and older adults. *Personality and Social Psychology Bulletin*, 27(3), 281–288. https://doi.org/10.1177/0146167201273002 (abstract)
- Hawkley, L. C., Hughes, M. E., Waite, L. J., Masi, C. M., Thisted, R. A., & Cacioppo, J. T. (2008). From social structural factors to perceptions of relationship quality and loneliness: The Chicago Health, Aging, and Social Relations Study. *Journals of Gerontology: Series B*, 63(6), S375–S384. https://doi.org/10.1093/geronb/63.6.S375 (abstract)
- Pinquart, M., & Sörensen, S. (2001). Influences on loneliness in older adults: A meta-analysis. *Basic and Applied Social Psychology*, 23(4), 245–266. https://doi.org/10.1207/S15324834BASP2304_2 (abstract via secondary)
- Sandstrom, G. M., & Dunn, E. W. (2014). Social interactions and well-being: The surprising power of weak ties. *Personality and Social Psychology Bulletin*, 40(7), 910–922. https://doi.org/10.1177/0146167214529799 (abstract)

### Pairing, breakups and networks

- Burton-Chellew, M. N., & Dunbar, R. I. M. (2015). Romance and reproduction are socially costly. *Evolutionary Behavioral Sciences*, 9(4), 229–241. https://doi.org/10.1037/ebs0000046 (abstract via the Oxford record, secondary)
- Johnson, M. P., & Leslie, L. (1982). Couple involvement and network structure: A test of the dyadic withdrawal hypothesis. *Social Psychology Quarterly*, 45(1), 34–43. https://doi.org/10.2307/3033672 (citation level)
- Kalmijn, M. (2003). Shared friendship networks and the life course: An analysis of survey data on married and cohabiting couples. *Social Networks*, 25(3), 231–249. https://doi.org/10.1016/S0378-8733(03)00010-8 (abstract via secondary)
- Kalmijn, M. (2012). Longitudinal analyses of the effects of age, marriage, and parenthood on social contacts and support. *Advances in Life Course Research*, 17(4), 177–190. https://doi.org/10.1016/j.alcr.2012.08.002 (abstract via secondary)
- Kalmijn, M., & Broese van Groenou, M. (2005). Differential effects of divorce on social integration. *Journal of Social and Personal Relationships*, 22(4), 455–476. https://doi.org/10.1177/0265407505054516 (abstract via secondary)
- McDermott, R., Fowler, J. H., & Christakis, N. A. (2013). Breaking up is hard to do, unless everyone else is doing it too: Social network effects on divorce in a longitudinal sample. *Social Forces*, 92(2), 491–519. https://doi.org/10.1093/sf/sot096 (abstract)
- Milardo, R. M. (1982). Friendship networks in developing relationships: Converging and diverging social environments. *Social Psychology Quarterly*, 45(3), 162–172. https://doi.org/10.2307/3033649 (citation level)
- Sarkisian, N., & Gerstel, N. (2016). Does singlehood isolate or integrate? Examining the link between marital status and ties to kin, friends, and neighbors. *Journal of Social and Personal Relationships*, 33(3), 361–384. https://doi.org/10.1177/0265407515597564 (abstract)
- Terhell, E. L., Broese van Groenou, M. I., & van Tilburg, T. (2004). Network dynamics in the long-term period after divorce. *Journal of Social and Personal Relationships*, 21(6), 719–738. https://doi.org/10.1177/0265407504047833 (abstract)

### Individual differences

- Baumeister, R. F., & Leary, M. R. (1995). The need to belong: Desire for interpersonal attachments as a fundamental human motivation. *Psychological Bulletin*, 117(3), 497–529. https://doi.org/10.1037/0033-2909.117.3.497 (abstract)
- Gillath, O., Karantzas, G. C., & Selçuk, E. (2017). A net of friends: Investigating friendship by integrating attachment theory and social network analysis. *Personality and Social Psychology Bulletin*, 43(11), 1546–1565. https://doi.org/10.1177/0146167217719731 (abstract; details secondary)
- Harris, K., & Vazire, S. (2016). On friendship development and the Big Five personality traits. *Social and Personality Psychology Compass*, 10(11), 647–667. https://doi.org/10.1111/spc3.12287 (abstract)
- Leary, M. R., Kelly, K. M., Cottrell, C. A., & Schreindorfer, L. S. (2013). Construct validity of the Need to Belong Scale: Mapping the nomological network. *Journal of Personality Assessment*, 95(6), 610–624. https://doi.org/10.1080/00223891.2013.819511 (abstract)
- Pollet, T. V., Roberts, S. G. B., & Dunbar, R. I. M. (2011). Extraverts have larger social network layers but do not feel emotionally closer to individuals at any layer. *Journal of Individual Differences*, 32(3), 161–169. https://doi.org/10.1027/1614-0001/a000048 (abstract, secondary)
- Wrzus, C., Hänel, M., Wagner, J., & Neyer, F. J. (2013). Social network changes and life events across the life span: A meta-analysis. *Psychological Bulletin*, 139(1), 53–80. https://doi.org/10.1037/a0028601 (abstract via secondary; friendship networks shrink across adulthood. Not cited above; kept as the meta-analysis to read next)

### Coercive control

- Home Office (2023). *Controlling or Coercive Behaviour Statutory Guidance Framework* (Serious Crime Act 2015, section 77). https://www.gov.uk/government/publications/controlling-or-coercive-behaviour-statutory-guidance-framework (read in part: the list of restrictive behaviours)
- Lanier, C., & Maume, M. O. (2009). Intimate partner violence and social isolation across the rural/urban divide. *Violence Against Women*, 15(11), 1311–1330. https://doi.org/10.1177/1077801209346711 (abstract)
- Stark, E. (2007). *Coercive Control: How Men Entrap Women in Personal Life*. Oxford University Press. (citation level)
