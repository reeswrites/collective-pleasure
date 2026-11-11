# Decision weights: how much suffering counts when agents choose (2026-11-11)

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Status: a research note, not a result. It grounds one modeling choice: the per-persona weight `w` in the decision score `pleasure − w × suffering`, used when agents decide to form a household, retry and stay. `w = 0` is the corrected rule from the H38 formation check (own pleasure only). `w = 1` is the old net rule (pleasure minus both kinds of suffering, `s_off + s_non`). Every number proposed below is ASSUMED unless a source is given for it.

Why it matters: in the H38 formation check ([h38-formation-check.md](../results/h38-formation-check.md)), deciding on pleasure formed 84% of pairs at week 0; deciding on net wellbeing formed 51%. The decision was logged in experiments/changes.jsonl (2026-11-11): the decision rule is a persona trait, because people differ in their sources of pleasure and suffering and in how much suffering weighs in their choices.

Sources were checked by web search on 2026-11-11 (title, authors, venue and DOI or a stable URL). Most were read at abstract level, not in full. Where a claim rests on a secondary summary, it says so.

## 1. What the research says

**Reward and punishment sensitivity are two separate, continuous traits.** Gray's reinforcement sensitivity theory says behavior is steered by a reward system (BAS) and a punishment or inhibition system (BIS) (Corr 2004). Carver and White (1994) built the standard self-report scales and showed that high-BIS people grew more nervous when expecting punishment, and high-BAS people happier when expecting reward. Community norms exist (Jorm et al. 1999, N = 2,725). The scales are treated as continuous dimensions with no natural cut points. This is the cleanest support for the claim that people differ in how much anticipated suffering weighs. It gives no exchange rate between the two.

**Loss aversion is real on average, but its size and even its direction vary a lot between people.** A meta-analysis of 607 estimates puts the mean loss-aversion coefficient at about 1.96, 95% interval about 1.82 to 2.10 (Brown, Imai, Vieider & Camerer 2024). That is the "losses loom about twice as large" figure. But in three representative US samples (combined N about 3,000), roughly half of people were loss tolerant, not loss averse (Chapman, Snowberg, Wang & Camerer 2025). Lab and student samples mostly drive the classic number. Individual-level estimates show "substantial heterogeneity" and are fairly consistent across riskless and risky tasks (Gächter, Johnson & Herrmann 2022). Some argue the effect is smaller and more context-bound than its reputation (Gal & Rucker 2018). All of this is about money gambles and trades, not relationships.

**Neuroticism predicts worse relationship outcomes, modestly, and mostly through satisfaction.** In the longest study, neuroticism rated before marriage was the strongest personality predictor of later divorce or unhappy marriage over about 45 years (Kelly & Conley 1987; findings as summarized by later reviews). Karney and Bradbury (1995) reviewed 115 longitudinal studies and placed personality among "enduring vulnerabilities". Meta-analytic links between the Big Five and relationship satisfaction are real but small (Malouff et al. 2010; secondary summaries give |r| of roughly 0.06 to 0.22). In a nationally representative couples sample, personality predicted divorce mainly through lower satisfaction (Solomon & Jackson 2014). So neuroticism is evidence that some people experience more suffering in relationships. It is weaker evidence that they weigh anticipated suffering more when deciding.

**Attachment avoidance pushes away from commitment; attachment anxiety pulls toward staying.** Avoidance is linked to expecting relationships to fail and to "commitment aversion" (Birnie, McClure, Lydon & Holmberg 2009). Attachment style predicts later relationship stability even after controlling for prior duration and commitment (Kirkpatrick & Davis 1994). Anxiety is linked to endorsing more reasons both to stay and to leave (Joel, MacDonald & Page-Gould 2018). Fear of being single, which overlaps with but is distinct from anxiety, predicts staying in less satisfying relationships and settling for less responsive partners (Spielmann et al. 2013). Attachment is dimensional, not a set of types (Fraley, Hudson, Heffernan & Segal 2015). The lesson for `w`: what counts as "suffering" depends on the person. For an avoidant person, closeness itself is a cost. For an anxious person, being alone is the cost. A single weight on one suffering total hides that.

**Regulatory focus describes the same split as a motivational orientation.** Higgins (1997) separates a promotion focus (gains, aspirations) from a prevention focus (safety, avoiding losses), as two independent orientations. In couples, promotion-focused people saw partners as more supportive and handled conflict more creatively; prevention-focused people saw partners as more distant (Winterheld & Simpson 2011). This supports the idea of a pleasure-led and a suffering-led chooser. It gives no numbers that map to `w`.

**People overpredict how much bad events will hurt, including breakups, but the size of the bias is disputed.** People overestimated the distress they would feel after a romantic breakup; the error came from overestimating how intense it would be at first, not from misjudging how fast it fades (Eastwick, Finkel, Krishnamurti & Loewenstein 2008, a small sample of 26 people who broke up). Earlier work found people neglect their own coping and overestimate how long negative feelings last, with relationship dissolution among the events tested (Gilbert et al. 1998). Levine et al. (2012) argue much of this "impact bias" is a measurement artifact: when the question is made clear, forecasts are fairly accurate. The safe reading is that forecasts of suffering tend to run high, by an unknown amount. Agents here forecast 52 weeks ahead from simulated rollouts, which carry no such bias.

**On cohabitation itself, there is little about risk weighting and much about drift.** People move in mostly to spend more time together, then for finances and convenience; about 14% name testing the relationship as their top reason, and testing is linked to worse relationship quality and more attachment insecurity (Rhoades, Stanley & Markman 2009). Interviews suggest moving in is often fast and driven by housing and money, not a weighed decision (Sassler 2004). The "sliding versus deciding" account says cohabitation raises inertia to stay regardless of fit (Stanley, Rhoades & Markman 2006). The best-established predictors of nonmarital breakup are relationship variables such as commitment, not individual traits (Le, Dove, Agnew, Korn & Mutso 2010; for commitment's own roots see Le & Agnew 2003). We found no study that estimates how much anticipated costs weigh against anticipated benefits in a cohabitation decision.

## 2. A proposed default distribution for w

**No source maps to `w` directly.** Loss-aversion coefficients are ratios on money outcomes measured from a reference point. Our `w` trades modeled suffering units against modeled pleasure units, on scales that are themselves ASSUMED (pleasure is capped at 1; suffering in H38 decisions ran about 0.11 to 0.17 per week). Everything below is our assumption, informed by the shape of the evidence, not its numbers.

**What the evidence does license.** (a) People differ, a lot, and on continuous dimensions, not types (BIS/BAS, attachment, loss aversion). (b) The middle of the population weighs anticipated losses somewhere around, or above, equal to gains; lab estimates say about 2, representative samples say about half are below 1. (c) Nobody in this literature weighs anticipated costs at zero as a stable trait. (d) Forecasts of suffering tend to run high, which pushes human decision weights up, not down.

**Proposal (ASSUMED).** Draw each persona's weight from a log-normal with median 1:

`w = exp(z)`, `z ~ Normal(0, 0.6)`, clipped to [0, 4].

That puts the middle 68% of personas between about 0.55 and 1.8, and the middle 95% between about 0.3 and 3.2. The reasoning:

- **Median 1.** It is the point where a unit of suffering costs a unit of pleasure, which is the old net rule. The two strongest loss-aversion sources pull in opposite directions (about 2 in the meta-analysis, about half below 1 in representative samples), so we do not move the median off the model's own neutral point.
- **Log scale.** Loss aversion is a ratio, and "half as much" and "twice as much" should be equally far from neutral.
- **Spread of 0.6.** Chosen so that the high end reaches the classic coefficient of about 2 at roughly the 87th percentile, and the low end includes clear pleasure-led choosers near 0.5. The spread is not estimated from any study.
- **No mass at 0.** The pure-pleasure rule stays a sensitivity arm, not a persona type.

**A 3-level version for analysis and readable arms (ASSUMED).** Where a continuous draw is awkward, use:

| Level | w | Share | Reads as |
|---|---|---|---|
| low (pleasure-led) | 0.5 | 30% | high reward sensitivity, promotion focus, loss tolerant |
| mid | 1.0 | 40% | suffering and pleasure count equally |
| high (suffering-led) | 2.0 | 30% | high punishment sensitivity, prevention focus, the classic loss-aversion coefficient |

Each value is roughly the middle of one third of the log-normal, rounded (about 0.52, 1.0 and 1.92). The 30/40/30 split is a design choice for balance, not a population estimate.

**Expect this default to form fewer pairs than the corrected rule.** H38 showed that the weight is the biggest lever on formation (84% at `w = 0`, 51% at `w = 1`). With a median of 1 and unanimity, the more suffering-led member of each pair decides, so formation will likely sit near or below the old rule's 51%. This is a consequence to preregister, not a side effect to discover.

**Keep two sensitivity arms.** `w = 0` for every persona (the corrected rule) and `w = 1` for every persona (the old rule). The default distribution sits between them on the median, and beyond them in its tails.

## 3. Other individual differences that bear on "different sources of pleasure and suffering"

**What the model already varies per persona.** Five value weights (security, autonomy, togetherness, money, other connections), need salience for four need clocks (rest, connection, money, security), five aspiration targets, risk tolerance and negotiation style (src/mar/personas.py). Pleasure and ordinary hardship (`s_off`) already come from these, so "different sources of pleasure" is partly built in. Risk tolerance exists but, as far as this read found, enters only the closed-form rule evaluation in negotiation.py, not the hedonic decisions.

**What is global today but varies in people.**

- **Non-offsettable suffering intensities.** Being trapped, a need denied, being restricted (`trapped_intensity`, `denied_intensity`, `diminished_intensity` in HedonicConfig, 0.4 to 0.5 for everyone). Attachment research says these differ by person: closeness and lost autonomy cost avoidant people more; being alone costs anxious people more. Per-persona multipliers on these three would be the most research-backed addition.
- **Suffering from being apart, not only from being together.** The decision compares living together against the outside option. Fear of being single (Spielmann et al. 2013) is suffering on the outside-option side. A high `w` raises the cost of both sides, so its effect on formation depends on which side carries more suffering. In H38 the blockers expected more suffering together (0.169 vs 0.113), so high `w` blocks there; it need not always.
- **Separate weights for `s_off` and `s_non`.** One `w` treats ordinary hardship and conditions held past onset alike. The theory in ADR 0010 already says they differ in kind.
- **Weight on forming versus leaving.** Inertia and "sliding" (Stanley et al. 2006) suggest people need a bigger reason to leave than to stay. A stay bonus or a leave threshold per persona would model that; today forming and staying use the same score.
- **Forecast horizon and forecasting bias.** `decide_weeks` is global (52). People differ in how far ahead they look, and forecasts of suffering run high on average (Section 1). A per-persona forecast inflation on suffering is possible but rests on disputed evidence.
- **Recovery speed.** `onset_weeks` and `n_decay` are global. Breakup recovery is faster than people predict, and plausibly varies by person.

**Ties between `w` and existing fields are not established.** It is tempting to derive `w` from `risk_tolerance` or the security weight. The evidence treats loss attitudes and risk attitudes as distinct (Chapman et al. 2025 report better out-of-survey prediction from gain-loss attitudes than from risk aversion), and BIS and BAS as roughly independent. So the default should draw `w` independently. A version where `w` rises as risk tolerance falls is a reasonable sensitivity arm, marked ASSUMED.

## 4. What this can and cannot justify

**It can justify** making `w` a per-persona trait, drawing it from a spread distribution rather than a point, keeping the spread continuous rather than as types, putting the classic coefficient of about 2 inside the range, and keeping `w = 0` and `w = 1` as sensitivity arms.

**It cannot justify** any particular median, spread or shares. These are our assumptions. It cannot justify carrying money-gamble coefficients over to modeled relationship suffering, since the scales differ. It cannot say whether agents should carry human forecasting biases or decide like accurate forecasters; that is a design choice, not a finding. And it cannot say anything about real people's decisions from runs with these agents.

**The weakest links.** The breakup-forecasting study has 26 people who broke up. Neuroticism effects are small and run mostly through satisfaction, not through how decisions are weighed. Cohabitation research is about reasons and drift, not about weighing. Most sources here were read at abstract level.

## 5. Questions for the author

1. Should agents decide like accurate forecasters (the rollout is the forecast, `w` is pure taste), or carry the human tendency to overpredict suffering (which would push `w` up)?
2. Is a median of 1, which likely forms about as few pairs as the old rule, acceptable as the default, or should the default sit lower (say a median of 0.7) on the grounds that half of representative samples are loss tolerant?
3. Should suffering split into kinds with their own weights per persona (closeness costs versus being-alone costs, ordinary hardship versus held conditions), or is one `w` enough for H39?

## Sources

- Birnie, C., McClure, M. J., Lydon, J. E., & Holmberg, D. (2009). Attachment avoidance and commitment aversion: A script for relationship failure. *Personal Relationships*, 16, 79–97. https://doi.org/10.1111/j.1475-6811.2009.01211.x
- Brown, A. L., Imai, T., Vieider, F. M., & Camerer, C. F. (2024). Meta-analysis of empirical estimates of loss aversion. *Journal of Economic Literature*, 62(2), 485–516. https://doi.org/10.1257/jel.20221698
- Carver, C. S., & White, T. L. (1994). Behavioral inhibition, behavioral activation, and affective responses to impending reward and punishment: The BIS/BAS scales. *Journal of Personality and Social Psychology*, 67(2), 319–333. https://doi.org/10.1037/0022-3514.67.2.319
- Chapman, J., Snowberg, E., Wang, S., & Camerer, C. (2025). Looming large or seeming small? Attitudes towards losses in a representative sample. *Review of Economic Studies*, 92(5), 2893–2922. Working paper: NBER WP 30243 (2022). https://www.restud.com/looming-large-or-seeming-small-attitudes-towards-losses-in-a-representative-sample/
- Corr, P. J. (2004). Reinforcement sensitivity theory and personality. *Neuroscience and Biobehavioral Reviews*, 28(3), 317–332. https://doi.org/10.1016/j.neubiorev.2004.01.005
- Eastwick, P. W., Finkel, E. J., Krishnamurti, T., & Loewenstein, G. (2008). Mispredicting distress following romantic breakup: Revealing the time course of the affective forecasting error. *Journal of Experimental Social Psychology*, 44, 800–807. https://www.cmu.edu/dietrich/sds/docs/loewenstein/MispredictingDistress.pdf
- Fraley, R. C., Hudson, N. W., Heffernan, M. E., & Segal, N. (2015). Are adult attachment styles categorical or dimensional? A taxometric analysis of general and relationship-specific attachment orientations. *Journal of Personality and Social Psychology*, 109(2), 354–368. https://doi.org/10.1037/pspp0000027
- Gächter, S., Johnson, E. J., & Herrmann, A. (2022). Individual-level loss aversion in riskless and risky choices. *Theory and Decision*, 92, 599–624. https://doi.org/10.1007/s11238-021-09839-8
- Gal, D., & Rucker, D. D. (2018). The loss of loss aversion: Will it loom larger than its gain? *Journal of Consumer Psychology*, 28(3), 497–516. https://doi.org/10.1002/jcpy.1047 (not re-checked by search this session)
- Gilbert, D. T., Pinel, E. C., Wilson, T. D., Blumberg, S. J., & Wheatley, T. P. (1998). Immune neglect: A source of durability bias in affective forecasting. *Journal of Personality and Social Psychology*, 75(3), 617–638. https://pubmed.ncbi.nlm.nih.gov/9781405/
- Higgins, E. T. (1997). Beyond pleasure and pain. *American Psychologist*, 52(12), 1280–1300. https://doi.org/10.1037/0003-066X.52.12.1280
- Joel, S., MacDonald, G., & Page-Gould, E. (2018). Wanting to stay and wanting to go: Unpacking the content and structure of relationship stay/leave decision processes. *Social Psychological and Personality Science*, 9, 631–644. https://doi.org/10.1177/1948550617722834
- Jorm, A. F., et al. (1999). Using the BIS/BAS scales to measure behavioural inhibition and behavioural activation: Factor structure, validity and norms in a large community sample. *Personality and Individual Differences*, 26(1), 49–58. https://researchportalplus.anu.edu.au/en/publications/using-the-bisbas-scales-to-measure-behavioural-inhibition-and-beh/
- Karney, B. R., & Bradbury, T. N. (1995). The longitudinal course of marital quality and stability: A review of theory, method, and research. *Psychological Bulletin*, 118(1), 3–34. https://doi.org/10.1037/0033-2909.118.1.3
- Kelly, E. L., & Conley, J. J. (1987). Personality and compatibility: A prospective analysis of marital stability and marital satisfaction. *Journal of Personality and Social Psychology*, 52(1), 27–40. https://doi.org/10.1037/0022-3514.52.1.27
- Kirkpatrick, L. A., & Davis, K. E. (1994). Attachment style, gender, and relationship stability: A longitudinal analysis. *Journal of Personality and Social Psychology*, 66(3), 502–512. https://doi.org/10.1037/0022-3514.66.3.502
- Le, B., & Agnew, C. R. (2003). Commitment and its theorized determinants: A meta-analysis of the Investment Model. *Personal Relationships*, 10(1), 37–57. https://doi.org/10.1111/1475-6811.00035 (title and venue checked; DOI not re-checked)
- Le, B., Dove, N. L., Agnew, C. R., Korn, M. S., & Mutso, A. A. (2010). Predicting nonmarital romantic relationship dissolution: A meta-analytic synthesis. *Personal Relationships*, 17(3), 377–390. https://doi.org/10.1111/j.1475-6811.2010.01285.x
- Levine, L. J., Lench, H. C., Kaplan, R. L., & Safer, M. A. (2012). Accuracy and artifact: Reexamining the intensity bias in affective forecasting. *Journal of Personality and Social Psychology*, 103(4), 584–605. https://doi.org/10.1037/a0029544
- Malouff, J. M., Thorsteinsson, E. B., Schutte, N. S., Bhullar, N., & Rooke, S. E. (2010). The Five-Factor Model of personality and relationship satisfaction of intimate partners: A meta-analysis. *Journal of Research in Personality*, 44, 124–127. https://doi.org/10.1016/j.jrp.2009.09.004
- Rhoades, G. K., Stanley, S. M., & Markman, H. J. (2009). Couples' reasons for cohabitation: Associations with individual well-being and relationship quality. *Journal of Family Issues*, 30(2), 233–258. https://pmc.ncbi.nlm.nih.gov/articles/PMC2743430
- Sassler, S. (2004). The process of entering into cohabiting unions. *Journal of Marriage and Family*, 66(2), 491–505. https://doi.org/10.1111/j.1741-3737.2004.00033.x
- Solomon, B. C., & Jackson, J. J. (2014). Why do personality traits predict divorce? Multiple pathways through satisfaction. *Journal of Personality and Social Psychology*, 106(6), 978–996. https://doi.org/10.1037/a0036190
- Spielmann, S. S., MacDonald, G., Maxwell, J. A., Joel, S., Peragine, D., Muise, A., & Impett, E. A. (2013). Settling for less out of fear of being single. *Journal of Personality and Social Psychology*, 105(6), 1049–1073. https://doi.org/10.1037/a0034628
- Stanley, S. M., Rhoades, G. K., & Markman, H. J. (2006). Sliding versus deciding: Inertia and the premarital cohabitation effect. *Family Relations*, 55(4), 499–509. https://doi.org/10.1111/j.1741-3729.2006.00418.x
- Winterheld, H. A., & Simpson, J. A. (2011). Seeking security or growth: A regulatory focus perspective on motivations in romantic relationships. *Journal of Personality and Social Psychology*, 101(5), 935–954. https://experts.umn.edu/en/publications/seeking-security-or-growth-a-regulatory-focus-perspective-on-moti/
