# The value of a background hour (q): what the evidence says

Research note, 2026-11-16. Written for the time-together model (prereg: [../results/time-together-prereg.md](../results/time-together-prereg.md); results: [../results/time-together.md](../results/time-together.md); earlier evidence: [time-together-research.md](time-together-research.md)). Not a result. Nothing in the model changes here. Wording rule: agents feel nothing; "pleasure" is a gloss for modeled numbers.

**The number in question.** `together_bg` = 33 shared waking hours a week × q ÷ a 3-hour planned evening. The 33 hours are sourced (Flood and Genadek 2016). q is not. q is the value of one hour of just being around a partner, relative to one hour of a planned evening together. TT uses q = 0.1 (`together_bg` 1.1). The sweeps showed q sets the size of every time-together effect.

**How this note was written.** I chose the translation and the range from the sources below, before and without asking which q makes any result come out a given way. I had read the TT sweeps (that is the reason for the task). Nothing here is fitted to them.

Strength labels, as in the earlier note: **strong** (large or repeated studies, not in dispute), **moderate** (one good study, or several with caveats), **weak** (small, old, cross-sectional or contested), **citation level** (read only through abstracts or summaries; numbers not checked against the source).

## What q has to mean

In the code, a chosen session adds `together_event` to the week's pleasure, on top of everything else. Background time adds `together_event × together_bg` in the same way. Both are add-ons. So q is a ratio of two *lifts*, not of two levels:

- **B**: how much better an ordinary hour is because the partner is there (the same activity, partner present against absent).
- **C**: how much better a planned evening with the partner is than the evening the person would otherwise have had.
- **q = B ÷ C**, per hour.

Comparing levels instead would be wrong. An hour of chores with a partner present is still mostly an hour of chores. Only the partner's share of it is background value.

## Findings

### B: the lift from a partner being present

**1. Activities with a spouse present are rated about 0.4 points happier on a 0–6 scale.** Flood and Genadek (2016), ATUS Well-Being Module 2010, Table 5. Mean "happy": men 4.62 with the spouse against 4.19 without; women 4.64 against 4.26. Mean stress falls by about 0.4 (men 1.05 against 1.43; women 1.17 against 1.57). Adjusted odds of "very happy" with the spouse: 1.81 within person (fixed effects, controls for seven activity types), 1.46 in the activity-level model (Table 6). The raw odds ratio implied by Table 5 (62% against 49% very happy) is about 1.7, between the two. So the adjusted lift is about the raw one: **roughly +0.4 on happiness, and about +0.8 if the stress drop is counted too.** **Moderate.** Large national sample and a within-person check. But only three sampled activities per person, the fixed-effects sample is selected, and no split by activity type is reported. The authors do not split exclusive time from time with others too.

**2. The same lift appears in the DRM: about +0.6 net affect with a spouse against alone.** Kahneman, Krueger, Schkade, Schwarz and Stone (2004), Table 1, 909 employed women in Texas. Spouse/partner: positive affect 4.11, negative 0.79, so net 3.32. Alone: positive 3.41, negative 0.69, net 2.72. Difference **+0.60**. **Moderate for the numbers, weak as an estimate of B.** It does not hold the activity fixed: "alone" includes commuting and work breaks, which drags the alone figure down and makes the lift look bigger. A later DRM wave (Krueger and Schkade 2007, Table 6) gives spouse/partner net affect 3.10 and 3.18 across two sessions, close to the 2004 figure, so the pattern is reliable. That table has no "alone" row.

**3. The "with spouse" hours include chosen time.** Flood and Genadek's 33 hours count every non-work, non-sleep activity with the spouse present. That includes dinners out and planned evenings, which the model counts as chosen sessions. So the +0.4 is an average over background *and* chosen hours. Background-only lift is smaller. A rough split: if chosen time is about 4.5 of the 33 hours with a lift of about 1.0, the other 28.5 hours have a lift of about (33 × 0.4 − 4.5 × 1.0) ÷ 28.5 ≈ **0.3**. **Arithmetic on ASSUMED shares**, not a measurement.

**4. Some studies find routine family time close to neutral.** Experience-sampling work with older adults found affect with a spouse or children at or below the person's own average, and above it with friends (Larson and colleagues 1986, as summarized by Chui et al. 2014). In older couples' daily life, partner presence alone did not predict affect contagion (Weber and Hülür 2021); in one of two samples it predicted cortisol synchrony, while positive *interaction* mattered more (Pauly et al., cortisol synchrony study). **Weak / citation level.** This is the evidence that B for plain co-presence could be near zero.

**5. More time with a spouse goes with higher life satisfaction, with shrinking returns.** Hamermesh (2020), ATUS Well-Being Module: moving 100 minutes from time alone to time with the spouse raises the chance of a high life-ladder score (8+) by 2.1 points (mean 56%). A quadratic term shows the value of an extra minute falls as time with the spouse grows, turning negative for about 6% of the sample. **Moderate** for the sign and the shrinking returns. It is a life-evaluation measure, not hourly affect, so it cannot be turned into B directly. It does warn that the 33rd hour is worth less than the first.

**6. One well-known claim should not be used.** A claim that married people are happier only when the spouse is in the room rested on misreading an ATUS category, and its author withdrew it (Institute for Family Studies blog, 2019). **Citation level.** Noted so it is not picked up later.

### C: the lift of a planned evening together

**7. Planned-evening activities sit about 1 to 1.3 net-affect points above time alone.** Kahneman et al. (2004), Table 1, net affect (positive minus negative): socializing 4.02, relaxing 3.91, eating 3.75, intimate relations 4.74, watching TV 3.61, alone 2.72. Kahneman and Krueger (2006), Table 2, from the same data: socializing after work 4.15, dinner 3.94, relaxing 3.96, intimate relations 4.83, watching TV 3.65. A planned evening (dinner plus socializing or relaxing, sometimes intimacy) is about 4.0–4.3. **Moderate** for the numbers. These are averages over whoever was there, not evenings with the partner specifically.

**8. The size of C depends on what the evening is compared with.** Against time alone in general (2.72), C is about 1.3–1.6. Against an ordinary evening at home of TV or relaxing (3.6–3.9), C is only about 0.2–0.7. Those home-evening numbers already include partner presence for many respondents, so they overstate the alternative for someone alone. A middle comparison, an ordinary evening mixing TV, chores and screen time mostly alone (about 3.0–3.4), gives **C ≈ 0.6–1.3, centre about 0.9.** **Weak**: the comparison point is a judgment, and no study measures "planned evening with partner" against "the evening otherwise".

**9. Doing things together helps only when both enjoy them.** Crawford, Houts, Huston and George (2002), a decade-long panel of married couples: shared leisure goes with marital satisfaction only when it suits both partners' tastes; leisure only the husband liked brought no gain. Johnson, Zabriskie and Hill (2006) and the older joint/parallel/individual split (Orthner 1975) point the same way: joint activity counts more than parallel activity. **Citation level.** It supports C > B (planned, chosen time beats being in the same room), but gives no number.

### Sleep

**10. Nothing usable.** No study found gives co-sleeping an affect value per hour. The 33 hours exclude sleep anyway. **None.**

## Translating into q

| Route | B | C | q = B ÷ C |
|---|---|---|---|
| A. ATUS lift, background share (findings 1, 3) against the middle C (finding 8) | 0.3 | 0.9 | **0.33** |
| B. DRM only, both against "alone", chosen share removed (findings 2, 3, 7) | 3.21 − 2.72 = 0.49 | 4.02 − 2.72 = 1.30 | **0.38** (biased upward, see below) |
| C. Low end: plain co-presence near neutral (finding 4), generous C | 0.1 | 1.3 | **0.08** |
| D. High end: full ATUS lift, small C | 0.4 | 0.6 | **0.67** |

Route B's background figure: spouse-present net affect 3.32 is a mix of chosen hours (about 14%, at 4.02) and background hours, so background = (3.32 − 0.14 × 4.02) ÷ 0.86 ≈ 3.21. Using the same low "alone" figure on both sides pushes the ratio toward 1, so 0.38 is an upper-leaning value.

Two more pulls, neither quantified:
- **Selection pushes q down.** People spend time with a partner when things are going well. Fixed effects remove stable differences between people, not good days. So B is likely overstated.
- **Shrinking returns push q down** (finding 5). The model values all 33 hours alike. If the later hours are worth less, the average per hour is lower than the lift measured on a typical sampled hour. This matters less, since diary samples already average over hours.

**Assumptions the translation needs** (each is ASSUMED):
1. **Affect maps onto the model's pleasure linearly and by duration.** An hour at +0.3 is worth a tenth of three hours at +1.0. This is the DRM's own "duration-weighted" convention (Kahneman and Krueger 2006). Peak-and-end memory effects are ignored.
2. **The model's pleasure is closer to momentary affect than to life evaluation.** If it were closer to life satisfaction, Hamermesh's numbers would apply instead, and they cannot be converted.
3. **One scale across sources.** Routes A, C and D mix the ATUS 0–6 happiness item with DRM net affect. Both are 0–6 but not the same construct. Route B stays inside one source.
4. **C is measured against an ordinary evening without the partner.** For a couple who live together, the real alternative to a planned evening is often a background evening with the partner. That would shrink C and raise q. The model gives a session the same value in or out of a shared home, so this note uses the without-partner comparison.
5. **The chosen share of the 33 hours is about 4.5 hours with a lift of about 1.0.** Changing it within reason (3–6 hours) moves background B by less than 0.05.
6. **The samples generalize.** DRM: employed women in Texas. ATUS: the US, 2010. Model personas are neither.

**How strong is the whole thing?** The inputs are moderate (two large diary sources agree that partner presence lifts affect by roughly half a point). The translation is weak: the size of C rests on a judged comparison point, and no study measures B for routine co-presence apart from shared leisure. **Overall: weak, but much better than no source.** The direction is clear: the sources put q above 0.1, not below.

## Proposed q — DRAFT, for the author to confirm

- **Point: q = 0.3** (routes A and B, rounded down slightly for selection).
- **Range: 0.05 to 0.6** (routes C and D, rounded).
- In model terms, with 33 hours and a 3-hour evening: `together_bg` = **3.3** at the point, **0.55 to 6.6** over the range. If the chosen hours are taken out of the 33 (about 28.5 left), the point becomes 2.85.
- **Is 0.1 inside the sourced range? Yes, but near the bottom.** 0.1 needs routine co-presence to be close to neutral (finding 4). The two main diary sources point to about three times that.
- **What TT's sweep covered.** TT swept q ≈ 0.03 to 0.2. The low end (0.03) is below this range. The proposed point (0.3) and most of the range lie above the sweep's high end. A sweep matching this note would be q = 0.05, 0.1, 0.3 and 0.6.
- **Not done here:** any rerun, any change to TT's prereg numbers, or any claim about what the results would be at 0.3. Changing q is the author's call and would need its own prereg or amendment.

**Most useful next source.** A within-couple experience-sampling or DRM study that codes, for the same people, (a) routine time with the partner present, (b) planned time together and (c) the same activities alone. That would measure B and C on one scale and replace routes A–D.

## Sources

- Chui, H., Hoppmann, C. A., Gerstorf, D., Walker, R., & Luszcz, M. A. (2014). Social partners and momentary affect in the oldest-old: The presence of others benefits affect depending on who we are and who we are with. (journal details not checked). https://acuresearchbank.acu.edu.au/item/87w88/ (citation level; source of the Larson et al. 1986 summary)
- Crawford, D. W., Houts, R. M., Huston, T. L., & George, L. J. (2002). Compatibility, leisure, and satisfaction in marital relationships. *Journal of Marriage and Family*, 64(2), 433–449. (citation level)
- Flood, S. M., & Genadek, K. R. (2016). Time for each other: Work and family constraints among couples. *Journal of Marriage and Family*, 78(1), 142–164. https://pmc.ncbi.nlm.nih.gov/articles/PMC4712716 (Tables 5 and 6 read)
- Hamermesh, D. S. (2020). Lock-downs, loneliness and life satisfaction. NBER Working Paper 27018. https://www.nber.org/papers/w27018 (results section read)
- Institute for Family Studies (2019). Are married people still happier? (blog). https://ifstudies.org/blog/are-married-people-still-happier (citation level)
- Johnson, H. A., Zabriskie, R. B., & Hill, B. (2006). The contribution of couple leisure involvement, leisure time, and leisure satisfaction to marital satisfaction. *Marriage & Family Review*, 40(1), 69–91. (citation level)
- Kahneman, D., Krueger, A. B., Schkade, D. A., Schwarz, N., & Stone, A. A. (2004). A survey method for characterizing daily life experience: The day reconstruction method. *Science*, 306(5702), 1776–1780. https://pdodds.w3.uvm.edu/files/papers/others/2004/kahneman2004a.pdf (Table 1 read)
- Kahneman, D., & Krueger, A. B. (2006). Developments in the measurement of subjective well-being. *Journal of Economic Perspectives*, 20(1), 3–24. https://inequality.stanford.edu/sites/default/files/media/_media/pdf/Reference%20Media/Kahneman_2006_Measurement.pdf (Table 2 read)
- Krueger, A. B., & Schkade, D. A. (2007). The reliability of subjective well-being measures. NBER Working Paper 13027. https://www.nber.org/papers/w13027 (Table 6 read)
- Larson, R., Mannell, R., & Zuzanek, J. (1986). Daily well-being of older adults with friends and family. *Psychology and Aging*, 1(2), 117–126. (citation level, through Chui et al. 2014)
- Orthner, D. K. (1975). Leisure activity patterns and marital satisfaction over the marital career. *Journal of Marriage and the Family*, 37(1), 91–102. (citation level)
- Pauly, T., et al. (c. 2020). Cortisol synchrony in older couples: Daily socioemotional correlates and interpersonal differences. (citation level; journal details not checked)
- Weber, C., & Hülür, G. (2021). Interpersonal affect contagion in older couples' daily life. (citation level; partner presence unrelated to affect contagion, 152 couples)
