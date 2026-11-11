# Economy calibration: a market world and a UBI world (2026-11-11)

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Status: a research note, not a result. It grounds H40 (experiments/hypotheses.jsonl), logged from the author's request: "i think we should try to accurately model a more capitalist society and then maybe a more UBI society". Nothing here changes code. Every number in the proposed design is ASSUMED unless a source is given next to it.

Sources were checked by web search on 2026-11-11. BLS figures were pulled from the public BLS API the same day; the series IDs are given so the numbers can be re-pulled. Most papers were read at abstract level. Where a figure comes from a secondary summary, it says so.

## 0. What the world has now

**Work is a flat money pump.** In the weekly household world (src/mar/worlds/household.py, the v2 block), `work` costs 4 of 10 weekly time units and pays 6 to partner A and 5 to partner B (`V2_INCOME`, ASSUMED). There is no wage distribution, no job, no hours choice, and no pleasure or suffering from working itself.

**Costs are one lumped bill.** `BILLS = {2: 10, 1: 6, 0: 0}` per 4-week month: 10 when both live in, 6 for one. There is no rent as such, no food or other necessities split out, no debt, and no savings beyond the shared pot (`POT_PUT = 45` each at week 0).

**Job loss is the one market shock.** About 1% a month (the JOLTS layoff rate, which is right; see below), lasting a uniform 8 to 26 weeks (ASSUMED).

**So giving is mostly bill-paying.** The pattern atlas found 93% of all gifts, bill payments and accepted requests are "reliance": paying the household's bills when there is a gap (docs/results/pattern-atlas.md). With one flat wage and one bill, money can only move one way, and the only reason to move it is the bill.

**Two things already look off against the data below.** The 6:5 wage split puts every couple in Pew's "egalitarian" band (each earns 40 to 60%), which holds for only 29% of US marriages. And the bill is small: one work block a week pays the couple's bill about twice over, while half of US renters spend more than 30% of income on housing.

## 1. Market economy calibration

### Wages

**Hourly wages are roughly lognormal, with a squeezed bottom and a fat top.** BLS OEWS, May 2025, all occupations (155.5 million jobs): 10th percentile $15.00, 25th $18.07, median $24.51, 75th $38.71, 90th $61.81; mean $33.54 an hour, $69,770 a year (BLS API series OEUN0000000000000000000{06,07,08,09,10,03,04}).

**A lognormal fit gives sigma about 0.55.** With mu = ln(24.51) = 3.20, the 90/10 ratio gives sigma = 0.552 and the 75/25 ratio gives 0.565. But the two halves differ: the bottom half alone implies sigma 0.38 (a wage floor), the top half 0.72. A single lognormal with sigma 0.55 predicts a mean of about $28.50, well under the real $33.54. For a small world this does not matter much; the 90/10 ratio of about 4.1 is the number to keep.

**OEWS is per job and excludes the self-employed.** Weekly earnings of full-time wage and salary workers give a cross-check: median $1,232 a week in Q3 2026 (CPS, series LEU0252881500).

### Hours

**Average weekly hours are about 34 for all private employees.** 34.4 in October 2026 (CES, series CES0500000002). This average mixes full-time and part-time. Employed people worked 8.05 hours on days worked if full-time and 5.35 if part-time (ATUS 2024).

**About 17% of workers are part-time.** 28.5 million usually part-time against 135.1 million full-time in October 2026 (CPS, LNS12600000 and LNS12500000).

**About 3% of all workers are part-time but want full-time.** 4.84 million part-time for economic reasons in October 2026 (LNS12032194): about 3.0% of the employed and about 17% of part-timers.

**Hours constraints run both ways, and wanting fewer hours is common too.** About 7% of US workers said they were overemployed (would take fewer hours for less pay) in a 2001 survey, about the same as in 1985 (Golden & Gebreselassie 2007). Reynolds (2003) found mismatches between actual and preferred hours common in the US, with the wish for fewer hours more common than the wish for more (as summarized by later work; read at citation level). The model reading: hours are mostly set by the job, not chosen week to week.

### Job loss and job finding

**About 1% of jobs end in a layoff each month.** JOLTS layoffs and discharges ran 1.0 to 1.2% of employment a month from August 2025 to September 2026 (JTS000000000000000LDR). Quits ran 1.9 to 2.1% and hires 3.1 to 3.5% (QUR, HIR). The world's ~1% monthly job-loss rate matches.

**Monthly flows say the same.** In October 2026, 1.56 million people moved from employed to unemployed, about 0.95% of the 163.6 million employed (LNS17400000, LNS12000000).

**About a quarter of the unemployed find work each month.** 1.87 million moved from unemployed to employed in October 2026, about 26% of the 7.07 million unemployed (LNS17100000, LNS13000000). Unemployment was 4.1% (LNS14000000).

**Spells are skewed: median about 11 to 12 weeks, mean about 25.** Median duration 11.9 weeks, mean 27.1 weeks in October 2026; over the past year the median ran 9.8 to 11.9 and the mean 23 to 27 (LNS13008276, LNS13008275). 27.6% of the unemployed had been out 27 weeks or more (LNS13025703). The world's uniform 8 to 26 weeks gets the middle about right and misses the long tail.

### Unemployment insurance

**UI replaces about 40% of prior wages for those who get it, and most of the unemployed do not.** Across all states, UI replaced 43% of average weekly wages for recipients in 2023, and 29% of the unemployed received benefits (Minneapolis Fed 2025, from DOL data). NELP puts recipiency at 27% in 2024 and replacement at under 40% (NELP 2025; an advocacy source). The DOL's own replacement-rate report normalizes wages to a 40-hour week. Benefits usually last up to 26 weeks; some states pay fewer (standard, not re-checked this session).

### Rent and other costs

**Half of renters are cost-burdened.** In 2023, 22.6 million renter households, 50% of renters, spent more than 30% of income on housing and utilities, a record; 12.1 million (27%) spent more than half (Harvard JCHS, State of the Nation's Housing 2025, via its press release and secondary coverage). 83% of renters earning under $30,000 were burdened.

**Housing is a third of spending for the average household.** BLS Consumer Expenditure Survey 2024: average spending $78,535; housing 33.4%, transportation 17.0%, food 12.9% (BLS 2025 release; TED article). The 2025 survey, released October 2026, gives housing 33.9%, transportation 16.5%, food 13.0% (secondary summary of the release table). These shares include homeowners.

### Savings and buffers

**The typical family holds about five weeks of income in the bank.** SCF 2025: median balance in transaction accounts (checking, savings, money market) $8,200; median family income $82,200; median net worth $215,900 (Federal Reserve 2026, "Changes in U.S. Family Finances from 2022 to 2025", Table 3). $8,200 against $82,200 a year is about 5.2 weeks of income. The bottom fifth by income has a median net worth of about $14,400.

**More than a third could not cover $400 with cash.** 63% of adults would pay a $400 emergency expense with cash or its equivalent, unchanged since 2022 and down from 68% in 2021 (Fed SHED, survey of October 2025, published 2026). $400 is about a third of a week of median full-time pay. So roughly 37% of adults have a buffer close to zero.

**Being behind is rising.** The 2025 SCF reports families were more likely to be behind on their obligations than at any point since 2010.

### Couples

**Half of married couples have two earners; a quarter have one.** In 2024, both spouses were employed in 49.6% of married-couple families, and only one in 23.4% (BLS, Employment Characteristics of Families). The rest have neither employed, mostly retirees.

**Most couples are unequal earners.** Among opposite-sex marriages in 2022: husband sole earner 23%, husband primary 31%, egalitarian (each 40 to 60%) 29%, wife primary 10%, wife sole 6% (Pew 2023, from CPS). Even in egalitarian marriages, wives did more caregiving (6.9 vs about 5 hours a week) and housework (4.6 vs about 2).

### Unpaid work

**Women do about 40% more housework and 50% more care of young children.** ATUS 2024: household activities 2.34 hours a day for women vs 1.67 for men; in households with a child under 6, primary childcare 2.96 vs 1.95. Men had more leisure (5.48 vs 4.67 hours a day).

### What work feels like

**In the moment, paid work is one of the worst things people do.** In the Mappiness experience-sampling data (UK, over a million responses), paid work ranked below every other of 40 activities except being sick in bed, about 7 to 8% lower happiness than other activities, with person fixed effects (Bryson & MacKerron 2017). In the Day Reconstruction Method study of 909 working women in Texas, commuting was the least enjoyed activity, and working was near the bottom with housework (Kahneman et al. 2004).

**But work is not only a cost.** Bryson and MacKerron note that work contributes substantially to overall life satisfaction, a different measure from momentary happiness. The model has no evaluative channel today, so this is noted, not used.

**Jobs differ a lot.** Gallup: 31% of US employees were engaged at work in 2025, and 17% actively disengaged (May 2026 indicator); the rest are "not engaged". This is a spread of how jobs feel, not a measure of pleasure.

## 2. Parameter table

| Quantity | Value or distribution | Source | Quality |
|---|---|---|---|
| Hourly wage | lognormal, median $24.51, sigma ≈ 0.55 (90/10 ≈ 4.1); bottom squeezed (σ ≈ 0.38), top fat (σ ≈ 0.72) | BLS OEWS May 2025 | High (official; fit is ours) |
| Full-time weekly earnings | median $1,232 | BLS CPS Q3 2026 | High |
| Average weekly hours | 34.4 (all private employees) | BLS CES Oct 2026 | High |
| Part-time share | ≈ 17% | BLS CPS Oct 2026 | High |
| Involuntary part-time | ≈ 3% of employed, ≈ 17% of part-timers | BLS CPS Oct 2026 | High |
| Want fewer hours for less pay | ≈ 7% | Golden & Gebreselassie 2007 (2001 data) | Medium (old) |
| Layoff rate | 1.0–1.2% a month | BLS JOLTS 2025–26 | High |
| Quit rate | 1.9–2.1% a month | BLS JOLTS 2025–26 | High |
| Job finding from unemployment | ≈ 26% a month | BLS CPS flows Oct 2026 | High (flows are noisy month to month) |
| Unemployment duration | median ≈ 11–12 weeks, mean ≈ 25; 28% over 26 weeks | BLS CPS 2025–26 | High |
| UI replacement | ≈ 40–43% of prior wage, for recipients only | Minneapolis Fed 2025; NELP 2025 | Medium |
| UI recipiency | 27–29% of unemployed | Minneapolis Fed 2025; NELP 2025 | Medium |
| Renters cost-burdened | 50% over 30% of income; 27% over 50% | Harvard JCHS 2025 (2023 data) | High (read via secondary coverage) |
| Spending shares | housing 33%, transport 17%, food 13% | BLS CEX 2024 | High |
| Liquid buffer | median $8,200 ≈ 5 weeks of median income | Fed SCF 2025 | High |
| Can't cover $400 from cash | 37% of adults | Fed SHED 2025 | High |
| Dual-earner married couples | 49.6% both employed; 23.4% one | BLS 2024 | High |
| Couple earnings split | 29% egalitarian; 54% husband primary or sole; 16% wife | Pew 2023 (2022 CPS) | High |
| Housework | women 2.34 h/day, men 1.67 | BLS ATUS 2024 | High |
| Childcare (child under 6) | women 2.96 h/day, men 1.95 | BLS ATUS 2024 | High |
| Momentary happiness at work | ranked 39th of 40 activities; ≈ 7–8% below others | Bryson & MacKerron 2017 (UK) | Medium-high (UK, app users) |
| Job engagement | 31% engaged, 17% actively disengaged | Gallup 2025–26 | Medium (proprietary index) |

## 3. UBI and unconditional cash: the evidence

**OpenResearch (ORUS), Illinois and Texas, 2020–2023.** 1,000 low-income adults got $1,000 a month for three years; 2,000 controls got $50 a month. Preregistered RCT. Work: labor market participation fell 4.2 points, hours fell 1 to 2 a week, and partners cut their hours by about as much. Per dollar received, household income excluding the transfer fell about 28 cents (16 for the recipient alone). The freed time went mostly to leisure; the authors can rule out even small gains in job quality, job search, childcare or self-improvement time (Vivalt et al. 2024, revised 2026; NBER lists a published version in the QJE, 2026). Wellbeing: higher in year one, back to control levels after (same paper). Health: no detectable effect on physical health, and no mental-health gain after year one (Miller et al. 2024). Relationships: no effect on aggregate household stability; suggestive gains in relationship quality and trust; some intimate partner violence indicators fell, mainly for women, but most lost significance after multiple-testing correction; partners were less likely to be promoted or move to a better job (Rhodes et al. 2026).

**This is the best single study for H40, and it cuts against part of the claim.** H40 expects UBI to free time "for making and care". ORUS found the time went to leisure, not care or self-improvement. H40 expects better exit options; ORUS found no better jobs and no change in household stability. Leisure is not nothing for a pleasure model. But the "power to say no" to a bad job did not show up as better jobs.

**Stockton SEED, California, 2019–2021.** 125 recipients got $500 a month for 24 months, randomized against a control group. In the first year, full-time employment rose from 28% to 40% among recipients and from 32% to 37% among controls (SEED first-year results, 2021). Researchers reported less anxiety and depression. Small sample, a single first-year report, and a pandemic in the middle. Treat as suggestive.

**Finland, 2017–2018.** 2,000 randomly chosen unemployed people got €560 a month, net, with no work test. No employment effect in year one; about six more days of work in year two, which a 2018 activation reform makes hard to attribute. Recipients reported clearly higher life satisfaction and less mental strain, but there was no baseline survey, so the wellbeing gap cannot be pinned on the payment (Kangas et al. 2020; University of Helsinki 2020). It tested a partial income for the unemployed, not a universal one.

**GiveDirectly, Kenya.** One-time and monthly transfers raised consumption and produced large gains in psychological wellbeing, with no rise in conflict (Haushofer & Shapiro 2016). Transfers averaging $709 to women cut physical and sexual violence by about 0.2 to 0.26 standard deviations; transfers to men cut physical violence (Haushofer et al. 2019, working paper). Across 653 villages, transfers worth over 15% of local GDP produced a local multiplier of 2.5 and minimal price inflation (Egger et al. 2022). In the 12-year UBI trial, total labor supply did not change at two years but shifted from wage work to self-employment (Banerjee et al. 2023, working paper). Robust for consumption and wellbeing; the setting (rural Kenya, very low incomes) is far from a US market world.

**Alaska Permanent Fund Dividend.** A universal, permanent payment of roughly $1,000 to $2,000 a person a year. Synthetic-control estimates find no effect on employment and a 1.8-point (17%) rise in part-time work (Jones & Marinescu 2022). The authors read this as local demand offsetting individual work cuts. One state, a small payment, and no control group by design.

**Negative income tax experiments (US, 1968–1982).** Consensus estimates: husbands cut work by about two weeks of full-time work a year, wives and single mothers by about three, youth by about four (Robins 1985; per-group percentages from secondary summaries are about 5% for husbands and over 20% for wives). Marital dissolution: the Seattle-Denver analysis reported large increases in breakups (Hannan, Tuma & Groeneveld 1977). A reanalysis that handled timing, attrition and reconciliations found no effect "of any practical or statistical significance" (Cain & Wissoker 1990). Labor effects are robust and moderate; the breakup finding is contested and the later reading is null.

**Mincome, Dauphin, Manitoba, 1974–1979.** The saturation site where every resident was eligible. One analysis found an 11.3-point drop in labor market participation, about 30% of it a "community" effect, driven by single-headed households (Calnitsky & Latner 2017). Forget (2011) reported hospitalizations fell by about 8.5% relative to controls; Green's reanalysis found pre-trends and concluded the data do not support a health effect (Green 2022, with a reply by Forget). Old data, recovered decades later; contested.

### UBI evidence table

| Study | Design, size | Payment | Work | Wellbeing | Relationships, exit, bargaining | How solid |
|---|---|---|---|---|---|---|
| ORUS (Vivalt, Miller, Rhodes et al.) | RCT, 1,000 T / 2,000 C, IL & TX, 2020–23 | $1,000/month, 3 years | −4.2 pp participation; −1–2 h/week; partners similar; leisure up; no job quality gain | Up in year 1, then no difference; no health effect | No aggregate stability effect; suggestive trust gains; IPV down for women, not robust; partners' careers worse | High (large, preregistered RCT) |
| Stockton SEED | RCT, 125 T, 2019–21 | $500/month, 2 years | Full-time 28→40% vs 32→37% (year 1) | Less anxiety, depression reported | Not measured as such | Low–medium (small, COVID) |
| Finland | Randomized, 2,000 unemployed, 2017–18 | €560/month | 0 in year 1; +6 days year 2 (confounded) | Higher life satisfaction, less strain | Not measured | Medium for work; low for wellbeing (no baseline) |
| GiveDirectly Kenya | RCTs, thousands of households | ~$700–1,000 lump or monthly | No change in total work; shift to self-employment | Large wellbeing gains | IPV down after transfers to women and men | High in context; low transfer to US |
| Alaska PFD (Jones & Marinescu) | Synthetic control, one state | ~$1,000–2,000/person/year | Employment 0; part-time +1.8 pp | Not studied | Not studied | Medium |
| NIT (SIME/DIME and others) | Four RCTs, 1968–82 | Guarantee with phase-out | Husbands −2 weeks/yr, wives −3, youth −4 | Not central | Breakups up (1977) → null on reanalysis (1990) | Work: high; breakups: contested, lean null |
| Mincome | Saturation site, 1974–79 | Guarantee with phase-out | −11.3 pp participation (one analysis) | Hospitalization −8.5% claimed | Not robust | Low (contested reanalyses) |

**The pattern that holds up.** Unconditional cash cuts paid work modestly: a few percent of hours, a few points of participation, more among second earners and young people. It raises consumption. Wellbeing gains are clear in poor settings and short-lived in the best US trial. Effects on relationships are mostly null or fragile, with intimate partner violence the most promising and least settled.

## 4. Funding and second-order effects

**A real UBI is very expensive.** $12,000 a year to every US adult, about the single-adult poverty line, would cost about $3 trillion a year, about 75% of all federal spending; without other cuts it would roughly double federal tax revenue (Hoynes & Rothstein 2019). Folding in existing transfer programs covers only a small part (secondary summaries say about a fifth; not checked in the paper).

**Our own rough arithmetic gives a flat tax near 29%.** OEWS mean pay is $69,770 a year, and 59.3% of adults are employed (CPS, LNS12300000, October 2026). That is about $41,400 of earnings per adult, so $12,000 per adult needs about a 29% flat tax on earnings, before any fall in hours. This mixes years and ignores capital income and existing programs; it is an order-of-magnitude check, not an estimate.

**General price inflation from cash looks small where it has been tested.** In Mexico, cash transfers had a positive but negligible effect on local prices, unlike food delivered in kind, which lowered them; effects were larger in remote villages (Cunha, De Giorgi & Jayachandran 2019). In Kenya, price effects were under 1% even at peak (Egger et al. 2022). Neither is a rich economy with a permanent, nationwide UBI.

**Rent capture is the worry with the most behind it, and the least direct evidence.** When France extended housing benefits, about 78 cents of each euro went into higher rents for new claimants, which the author ties to very inelastic housing supply (Fack 2006). That is a benefit tied to rent, not unconditional cash. No study measures how much of a universal payment landlords capture in a supply-constrained US housing market.

**Where the evidence is thin.** No country has run a permanent, universal, full-size UBI. Every experiment either gave cash to a few people in a large economy (so no effects on prices, rents or employers) or ran small and short. Effects on the tax side, on rents, and on what employers offer are model assumptions, not findings.

## 5. Freedom and domination

**The philosophical case is that a basic income is exit power.** Widerquist argues that freedom is "the power to say no": effective control over one's life requires being able to refuse any offer, from employers or anyone else, which in a market economy needs an unconditional income (Widerquist 2013). Pettit argues from republican non-domination: a universal right to an income lets people stand on their own feet without depending on others' goodwill, and being universal it does not mark recipients as a dependent class (Pettit 2007).

**This maps cleanly onto H40's mechanism.** Domination in the household world is a partner with no acceptable outside option. A basic income paid to individuals raises the poorer partner's outside option the most.

**The empirical test of this mechanism is so far weak.** ORUS's null on job quality and household stability is the closest direct check, and it did not find exit power being used. The Kenya violence results fit the mechanism. The NIT breakup result, which would have been the strongest sign of exit, did not survive reanalysis.

## 6. What a small model can and cannot claim

**It can show mechanisms.** For example: if a basic income raises the poorer partner's runway alone above some threshold, held households become rarer, given these agents and these costs. That is a statement about the model.

**It can check itself against known magnitudes.** The world should reproduce, without being tuned to them: a few percent fewer hours under the payment, about a quarter of jobless agents finding work each month, about half of renters over the 30% line, about a third with almost no buffer. If it misses these by a lot, its other outputs are suspect.

**It cannot estimate real effects.** Agents are scripted personas with ASSUMED preferences. The world has no firms, no prices that respond, no housing supply, no state. Any welfare number is a property of the model.

**It cannot settle the funding question.** A world of two to a few dozen agents can balance a flat tax inside itself. It cannot say whether a real economy can.

**It cannot test general-equilibrium effects** such as rent capture, local multipliers or employer responses. It can only run them as sensitivity arms with stated sizes.

**Its strongest claims will be comparisons within the model.** Same agents, same seeds, market world against UBI world, with the cost side included.

## 7. Proposed minimal design (PROPOSAL)

**The aim is the fewest parameters that carry seven mechanisms:** wage inequality, hours, job loss, rent, savings buffer, work enjoyment and exit power. Everything below is a proposal. Each value is ASSUMED except where a source is named, and those sources set targets, not exact inputs, because the world's units are abstract.

### Shared by both worlds

1. **Wage per work unit.** Each agent draws a wage `w = exp(z)`, `z ~ Normal(0, 0.55)`, clipped below at 0.61 (the OEWS 10th-to-median ratio). Median 1, scaled to the world's money unit. One parameter: sigma.
2. **Hours come with the job.** A job is full-time (4 units a week, the current `work` cost) or part-time (2 units). 17% of jobs are part-time (CPS). An agent can change hours only by changing jobs. This makes hours constraints emerge without a separate parameter.
3. **Job loss and finding.** Weekly layoff hazard 0.0023 (1% a month, JOLTS). While jobless and searching, weekly finding hazard 0.06, which gives a median spell of about 11 weeks and 23% finding work a month (CPS). This replaces the uniform 8–26 weeks. A new job keeps the agent's wage draw and re-draws its enjoyment.
4. **Quitting.** An agent can quit a job, then searches as above. This is the market world's only exit from a bad job, and it costs income.
5. **Unemployment insurance.** 40% of lost pay for up to 26 weeks, for 30% of job losers (Minneapolis Fed, NELP). Two parameters, kept because the market world's exit power depends on them.
6. **Rent, separate from other needs.** A one-person place costs `R1` a week; a two-person place costs `1.5 × R1` (ASSUMED economy of scale; the current bills use 10:6). Set `R1` to 30% of median full-time pay. Other necessities (food, transport) cost `0.9 × R1` per person, from the CEX ratio of non-housing necessities to housing. Validation target: about half of single agents over the 30% line (JCHS).
7. **Savings buffer.** Each agent starts with private savings in weeks of own pay: 37% near zero (under a third of a week, SHED), the rest lognormal with median 5 weeks (SCF). No borrowing: an unpaid bill is a missed bill, which adds suffering. The shared pot stays as it is.
8. **Work enjoyment.** Each job carries a per-unit hedonic value `e`: 31% of jobs mildly positive, 52% mildly negative, 17% clearly negative (Gallup shares). Average below rest (Bryson & MacKerron: work is among the worst moments). Sizes are ASSUMED in the units of src/mar/hedonic.py.
9. **Exit power, measured not set.** For each partner, runway = weeks they could live alone on their own pay, UI, savings and any basic income, before missing a bill. A household is "held" when the poorer partner's runway is under a threshold `k` weeks (ASSUMED, say 8).

**Not modeled, on purpose:** firms, wage bargaining, price or rent responses, credit, taxes other than the one below, gender. The couple earnings gap and the housework split should emerge from wage draws and choices, and be checked against Pew and ATUS, not imposed.

### The UBI world adds two numbers

10. **A basic income `T` per adult per week, paid to the individual,** not the household, with no work test. Default `T` = 19% of median full-time pay: that is what $12,000 a year (the Hoynes-Rothstein poverty-line level, and about ORUS's $1,000 a month) is against median full-time earnings of about $64,000.
11. **A flat tax `τ` on earnings that balances the budget inside the world** each year. With today's numbers that comes to roughly 29% before any change in hours. Both worlds are run; the market world has `T = 0`, `τ = 0`.

### Sensitivity arms

- **Rent capture:** rent rises by `c × T` with `c` in {0, 0.5, 0.78}; 0.78 is Fack's French housing-benefit figure, an upper bound for a rent-tied benefit.
- **Unfunded:** `T` with `τ = 0`, to separate the gift from the tax.
- **Household UBI:** `T` paid into the shared pot, to test whether individual payment is what carries exit power.

### What the worlds should reproduce before anyone reads results

Under the UBI arm with no capture: hours down a few percent, participation down a few points, partners' hours down about as much (ORUS). In both worlds: job finding near a quarter a month, about half of singles rent-burdened, about a third near zero savings. These are checks on the world, not results.

## 8. Questions for the author

1. Should the basic income be funded inside the world (a flat tax that balances, so richer agents pay for it), or a gift from outside? The proposal runs both, but which one is "the UBI society" you mean?
2. Is a job market in scope for H40 (jobs with their own wage, hours and enjoyment; quitting and searching), or should jobs stay a fixed trait with only loss and re-finding? The job market is what makes "the power to say no" testable outside the household.
3. ORUS, the strongest study, found the freed time went to leisure, not to care or making, and found no gain in household stability. Should H40's claim be narrowed before it is preregistered, or kept as written and tested?

## Sources

### Official statistics

- U.S. Bureau of Labor Statistics. Occupational Employment and Wage Statistics, May 2025, national, all occupations. BLS public API, series OEUN000000000000000000001, …03, …04, …06–…10, pulled 2026-11-11. https://www.bls.gov/oes/
- U.S. Bureau of Labor Statistics. Current Population Survey series LEU0252881500, LNS12000000, LNS12032194, LNS12300000, LNS12500000, LNS12600000, LNS13000000, LNS13008275, LNS13008276, LNS13025703, LNS14000000, LNS17100000, LNS17400000; Current Employment Statistics CES0500000002; JOLTS JTS000000000000000LDR, …QUR, …HIR. BLS public API, pulled 2026-11-11. https://www.bls.gov/cps/ , https://www.bls.gov/jlt/
- U.S. Bureau of Labor Statistics (2025). American Time Use Survey — 2024 Results. News release, June 26, 2025. https://www.bls.gov/news.release/archives/atus_06262025.htm
- U.S. Bureau of Labor Statistics (2025). Employment Characteristics of Families — 2024. News release, April 23, 2025. https://www.bls.gov/news.release/archives/famee_04232025.htm
- U.S. Bureau of Labor Statistics (2026). Housing and transportation accounted for 50 percent of household spending in 2024. The Economics Daily. https://www.bls.gov/opub/ted/2026/housing-and-transportation-accounted-for-50-percent-of-household-spending-in-2024.htm ; Consumer Expenditures in 2024 report: https://www.bls.gov/opub/reports/consumer-expenditures/2024/
- Board of Governors of the Federal Reserve System (2026). Changes in U.S. Family Finances from 2022 to 2025: Evidence from the Survey of Consumer Finances. https://www.federalreserve.gov/publications/files/scf26.pdf
- Board of Governors of the Federal Reserve System (2026). Economic Well-Being of U.S. Households in 2025 (SHED), executive summary. https://www.federalreserve.gov/publications/2026-economic-well-being-of-us-households-in-2025-executive-summary.htm
- Joint Center for Housing Studies of Harvard University (2025). The State of the Nation's Housing 2025. Press release: https://www.jchs.harvard.edu/press-releases/new-report-highlights-unease-housing-market-amid-worsening-affordability-crisis
- Federal Reserve Bank of Minneapolis (2025). How unemployment insurance access and benefits vary by state. https://www.minneapolisfed.org/article/2025/how-unemployment-insurance-access-and-benefits-vary-by-state
- U.S. Department of Labor, Employment and Training Administration. UI Replacement Rates Report (definitions). https://oui.doleta.gov/unemploy/ui_replacement_rates.asp
- National Employment Law Project (2025). Boosting Economic Resilience: Seven Ways States Can Support More Workers with Unemployment Insurance. https://www.nelp.org/insights-research/boosting-economic-resilience-seven-ways-states-can-support-more-workers-with-unemployment-insurance/

### Work, hours, couples

- Bryson, A., & MacKerron, G. (2017). Are you happy while you work? *Economic Journal*, 127(599), 106–125. https://sro.sussex.ac.uk/id/eprint/59345/
- Gallup. Indicator: Employee Engagement (2025–2026 readings). https://www.gallup.com/394373/indicator-employee-engagement.aspx
- Golden, L., & Gebreselassie, T. (2007). Overemployment mismatches: the preference for fewer work hours. *Monthly Labor Review*, April 2007, 18–37. https://www.bls.gov/opub/mlr/2007/04/art2full.pdf
- Kahneman, D., Krueger, A. B., Schkade, D. A., Schwarz, N., & Stone, A. A. (2004). A survey method for characterizing daily life experience: The Day Reconstruction Method. *Science*, 306(5702), 1776–1780. https://doi.org/10.1126/science.1103572
- Pew Research Center (2023). In a Growing Share of U.S. Marriages, Husbands and Wives Earn About the Same. https://www.pewresearch.org/social-trends/2023/04/13/in-a-growing-share-of-u-s-marriages-husbands-and-wives-earn-about-the-same/
- Reynolds, J. (2003). You can't always get the hours you want: Mismatches between actual and preferred work hours in the United States. *Social Forces*, 81(4), 1171–1199. https://muse.jhu.edu/issue/2756 (read at citation level)

### Unconditional cash and UBI

- Banerjee, A., Faye, M., Krueger, A., Niehaus, P., & Suri, T. (2023). Universal basic income: Short-term results from a long-term experiment in Kenya. Working paper. https://conference.nber.org/conf_papers/f192616.pdf
- Cain, G. G., & Wissoker, D. A. (1990). A reanalysis of marital stability in the Seattle-Denver Income-Maintenance Experiment. *American Journal of Sociology*, 95(5), 1235–1269. https://doi.org/10.1086/229428
- Calnitsky, D., & Latner, J. P. (2017). Basic income in a small town: Understanding the elusive effects on work. *Social Problems*, 64(3), 373–397. https://users.ssc.wisc.edu/~dcalnits/wp-content/uploads/2014/07/Calnitsky_Latner_Social_Problems_BI_in_a_small_town.pdf
- Egger, D., Haushofer, J., Miguel, E., Niehaus, P., & Walker, M. (2022). General equilibrium effects of cash transfers: Experimental evidence from Kenya. *Econometrica*, 90(6), 2603–2643. https://doi.org/10.3982/ECTA17945
- Forget, E. L. (2011). The town with no poverty: The health effects of a Canadian guaranteed annual income field experiment. *Canadian Public Policy*, 37(3), 283–305. https://econpapers.repec.org/RePEc:cpp:issued:v:37:y:2011:i:3:p:283-305
- Green, D. A. (2022). A reanalysis of "The Town with No Poverty: The Health Effects of a Canadian Guaranteed Annual Income Field Experiment". *Canadian Public Policy*, 48(4), 539–548 (Forget replies in the same issue). https://econpapers.repec.org/RePEc:cpp:issued:v:48:y:2022:i:4:p:539-548 ; working version: https://economics.ubc.ca/wp-content/uploads/sites/38/2021/03/forget-cpp-reanalysis.pdf
- Hannan, M. T., Tuma, N. B., & Groeneveld, L. P. (1977). Income and marital events: Evidence from an income-maintenance experiment. *American Journal of Sociology*, 82, 1186–1211. Not read; its finding is as described by Cain & Wissoker: https://www.irp.wisc.edu/publications/dps/pdfs/dp85788.pdf
- Haushofer, J., Ringdal, C., Shapiro, J. P., & Wang, X. Y. (2019). Income changes and intimate partner violence: Evidence from unconditional cash transfers in Kenya. NBER Working Paper 25627. https://www.nber.org/papers/w25627
- Haushofer, J., & Shapiro, J. (2016). The short-term impact of unconditional cash transfers to the poor: Experimental evidence from Kenya. *Quarterly Journal of Economics*, 131(4), 1973–2042. https://ideas.repec.org/a/oup/qjecon/v131y2016i4p1973-2042..html
- Jones, D., & Marinescu, I. (2022). The labor market impacts of universal and permanent cash transfers: Evidence from the Alaska Permanent Fund. *American Economic Journal: Economic Policy*, 14(2), 315–340. https://www.nber.org/papers/w24312
- Kangas, O., Jauhiainen, S., Simanainen, M., & Ylikännö, M. (Eds.) (2020). Suomen perustulokokeilun arviointi [Evaluation of the Finnish basic income experiment]. Sosiaali- ja terveysministeriön raportteja ja muistioita 2020:15. Ministry of Social Affairs and Health. English summary: https://toolbox.finland.fi/wp-content/uploads/sites/2/2018/04/basic_income_experiment_2017-2018_results_2020.pdf
- Miller, S., Rhodes, E., Bartik, A. W., Broockman, D. E., Krause, P. K., & Vivalt, E. (2024). Does income affect health? Evidence from a randomized controlled trial of a guaranteed income. NBER Working Paper 32711. https://www.nber.org/papers/w32711
- Rhodes, E., Broockman, D. E., Vivalt, E., Krause, P. K., Miller, S., & Bartik, A. W. (2026). Income shocks and intrahousehold dynamics: Evidence from a guaranteed income experiment. NBER Working Paper 35589. https://www.nber.org/papers/w35589
- Robins, P. K. (1985). A comparison of the labor supply findings from the four negative income tax experiments. *Journal of Human Resources*, 20(4), 567–582. https://ideas.repec.org/a/uwp/jhriss/v20y1985i4p567-582.html
- Stockton Economic Empowerment Demonstration (2021). First-year results: employment. https://www.stocktondemonstration.org/employment ; Penn SP2 summary: https://sp2.upenn.edu/guaranteed-income-increases-employment-improves-financial-and-physical-health/
- University of Helsinki (2020). The basic income experiment in Finland yields surprising results. https://www.helsinki.fi/en/news/fair-society/basic-income-experiment-finland-yields-surprising-results
- Vivalt, E., Rhodes, E., Bartik, A. W., Broockman, D. E., Krause, P., & Miller, S. (2024, revised 2026). The employment effects of a guaranteed income: Experimental evidence from two U.S. states. NBER Working Paper 32719; the NBER page lists a version in the *Quarterly Journal of Economics* 141(4), 2026. https://doi.org/10.3386/w32719

### Funding, prices, rents

- Cunha, J. M., De Giorgi, G., & Jayachandran, S. (2019). The price effects of cash versus in-kind transfers. *Review of Economic Studies*, 86(1), 240–281. https://doi.org/10.1093/restud/rdy018
- Fack, G. (2006). Are housing benefit an effective way to redistribute income? Evidence from a natural experiment in France. *Labour Economics*, 13(6), 747–771. https://ideas.repec.org/p/hal/journl/hal-00813573.html
- Hoynes, H., & Rothstein, J. (2019). Universal basic income in the United States and advanced countries. *Annual Review of Economics*, 11, 929–958. https://www.nber.org/papers/w25538

### Freedom and domination

- Pettit, P. (2007). A republican right to basic income? *Basic Income Studies*, 2(2). https://doi.org/10.2202/1932-0183.1082
- Widerquist, K. (2013). *Independence, Propertylessness, and Basic Income: A Theory of Freedom as the Power to Say No*. Palgrave Macmillan. https://basicincome.org/?p=1878
