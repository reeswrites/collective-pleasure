# References check (2026-11-10)

Nothing here is a result. This page checks the citations that today's docs made "from memory". Each entry gives the real reference, a verdict, and the claim as it should be stated.

Verdicts: yes (claim is accurate as used), partly (reference is real but the claim needs a fix), no (reference does not support the claim).

Basis: "searched" means I confirmed the bibliographic data against a web source this session. "recalled" means standard textbook knowledge that I did not re-fetch; treat the details as likely right but unchecked. No full texts were read. Abstracts and catalog records only.

Tally of the 19 requested items: 12 yes, 7 partly, 0 no.

## Items from the ADRs

### 1. Tinbergen's four questions. Verdict: partly (searched)
- Tinbergen, N. (1963). "On aims and methods of ethology." *Zeitschrift fuer Tierpsychologie* 20(4): 410-433.
- It sets out four questions: causation (mechanism), survival value (function), evolution (phylogeny), ontogeny (development). He took the first three from Huxley and added ontogeny.
- Fix: "proximate vs ultimate" is Mayr's split, not Tinbergen's. Mayr, E. (1961). "Cause and effect in biology." *Science* 134(3489): 1501-1506 (recalled). The ADR phrase "levels of explanation" is fine. Say pleasure is a proximate mechanism and fitness is the ultimate (function) explanation.

### 2. Butler against psychological hedonism; paradox of hedonism. Verdict: yes (recalled)
- Butler, J. (1726). *Fifteen Sermons Preached at the Rolls Chapel*, esp. Sermon XI. Pleasure comes from satisfying a prior desire for some object, so desire for pleasure cannot be the only desire.
- The "paradox of hedonism" (aiming straight at pleasure tends to defeat it) is a separate point. Sidgwick (1874), *The Methods of Ethics*, named it. Do not credit it to Butler.
- ADR 0011 cites only Butler's argument. That is accurate. Ethical hedonism and psychological hedonism are different claims, as the ADR says.

### 3. Berridge and Robinson, wanting vs liking. Verdict: yes (searched)
- Berridge, K. C., & Robinson, T. E. (1998). "What is the role of dopamine in reward: hedonic impact, reward learning, or incentive salience?" *Brain Research Reviews* 28(3): 309-369. doi:10.1016/S0165-0173(98)00019-8.
- Claim: dopamine systems drive motivational "wanting" (incentive salience), not hedonic "liking" or learning. Accurate.
- Useful companion for liking (recalled): Berridge, K. C., & Kringelbach, M. L. (2015). "Pleasure systems in the brain." *Neuron* 86(3): 646-664.

### 4. Schultz on reward prediction error. Verdict: yes (searched)
- Schultz, W., Dayan, P., & Montague, P. R. (1997). "A neural substrate of prediction and reward." *Science* 275(5306): 1593-1599. doi:10.1126/science.275.5306.1593.
- Claim: midbrain dopamine neuron activity tracks reward prediction errors. Accurate. Later work shows dopamine carries more than this one signal, so say "tracks" not "is".

### 5. Fredrickson, broaden-and-build. Verdict: yes (searched)
- Fredrickson, B. L. (2001). "The role of positive emotions in positive psychology: the broaden-and-build theory of positive emotions." *American Psychologist* 56(3): 218-226. doi:10.1037/0003-066X.56.3.218.
- Claim: positive emotions broaden momentary thought-action repertoires and build lasting resources. Accurate.
- Caution (recalled): the later "positivity ratio" of 2.9 (Fredrickson & Losada 2005) was criticized and partly withdrawn. Do not cite a ratio.

### 6. Poverty traps. Verdict: yes (searched)
- Azariadis, C., & Stachurski, J. (2005). "Poverty traps." In Aghion & Durlauf (eds.), *Handbook of Economic Growth*, vol. 1A, ch. 5, pp. 295-384. Elsevier.
- Canonical survey. Working definition: a self-reinforcing mechanism that makes poverty persist. Accurate for the spiral-with-tipping-point idea.
- Note (recalled): whether traps exist empirically is debated (Kraay & McKenzie 2014, *Journal of Economic Perspectives*). The model class is sound. The empirical claim is not settled.

### 7. Empowerment (Klyubin, Polani, Nehaniv; Salge). Verdict: partly (searched)
- Klyubin, A. S., Polani, D., & Nehaniv, C. L. (2005). "Empowerment: a universal agent-centric measure of control." *Proc. IEEE Congress on Evolutionary Computation*, pp. 128-135. doi:10.1109/CEC.2005.1554676.
- Salge, C., Glackin, C., & Polani, D. (2014). "Empowerment: an introduction." In *Guided Self-Organization: Inception*, Springer. arXiv:1310.1863 (posted 2013).
- Fix: empowerment is the channel capacity (maximum mutual information, in bits) between an agent's action sequences and its later sensor states. In a deterministic system it equals the log of the number of distinct reachable states. So "number of distinct futures" is right only for deterministic transitions. With noise, state "channel capacity", and note it discounts futures the agent cannot reliably steer to.

### 8. Turner et al., power-seeking. Verdict: partly (searched)
- Turner, A. M., Smith, L., Shah, R., Critch, A., & Tadepalli, P. (2021). "Optimal policies tend to seek power." *NeurIPS 34* (spotlight). arXiv:1912.01683.
- Result: in MDPs with certain symmetries, most reward functions make it optimal to keep options open (and avoid shutdown). Single-agent theory about optimal policies.
- Fix: the paper does not define power-seeking as grabbing options "at others' expense". That multi-agent reading is ours. Say: "power = ability to keep many futures available (Turner et al.); we add the cost to others as our own extension." The authors also warn optimal policies may not describe learned ones.

### 9. Leibo et al., appropriateness. Verdict: partly (searched)
- Leibo, J. Z., et al. (2024). "A theory of appropriateness with applications to generative artificial intelligence." arXiv:2412.19010 (Google DeepMind, 14 authors).
- Claim in the paper: appropriate behavior is context-dependent, partly arbitrary, often automatic, and maintained by sanctioning. It argues appropriateness is a better frame than alignment for governing AI.
- Fix: it is a theory of norms and cognition, not a motivation architecture. Using it as one axis of motivation (as ADR 0011 plans) is our design choice. A 2026 follow-up in Concordia exists: Cross, Grau-Moya, Cunningham, Vezhnevets, Leibo, arXiv:2603.13220 (status signaling). I did not read it.

### 10. Tronick, still-face, rupture and repair. Verdict: partly (searched, one point recalled)
- Tronick, E., Als, H., Adamson, L., Wise, S., & Brazelton, T. B. (1978). "The infant's response to entrapment between contradictory messages in face-to-face interaction." *Journal of the American Academy of Child Psychiatry* 17(1): 1-13. Sources disagree on page range in places; 1-13 is the most common.
- Fix: this paper is the still-face paradigm. It shows infants react to a suddenly unresponsive parent. It is not itself about repair. The repair claim belongs to Tronick & Gianino (1986), "Interactive mismatch and repair: challenges to the coping infant," *Zero to Three* 6(3): 1-6 (recalled). Normal parent-infant interaction has frequent mismatches that are repaired. The popular "70% mismatched" figure comes from this line of work (recalled); do not quote it without checking.

### 11. Gottman, repair attempts. Verdict: partly (searched, weak)
- Gottman, J. M., Coan, J., Carrere, S., & Swanson, C. (1998). "Predicting marital happiness and stability from newlywed interactions." *Journal of Marriage and the Family* 60(1): 5-22. 130 newlyweds, six years.
- I could not confirm from abstracts that this paper centers on repair. Its indexed predictors are acceptance of the wife's influence, soothing, and positive-to-negative affect balance. Repair attempts are a core idea in Gottman's clinical writing (Gottman & Silver 1999, *The Seven Principles for Making Marriage Work*; recalled). A critique argues the authors' recommendations went beyond their data.
- Fix: cite "repair attempts" as a concept from Gottman's research program and book, not as a single tested result. Read the full text before using it as evidence.

### 12. Dalrymple et al., Guaranteed Safe AI. Verdict: yes (searched)
- Dalrymple, D., Skalse, J., Bengio, Y., Russell, S., Tegmark, M., et al. (2024). "Towards guaranteed safe AI: a framework for ensuring robust and reliable AI systems." arXiv:2405.06624.
- Three parts: world model, safety specification, verifier. A position paper. ADR 0011 maps these correctly. Note Dalrymple is first author and Skalse second.

### 13. Bengio's Scientist AI. Verdict: unverified (recalled only)
- I believe this is Bengio et al. (2025), "Superintelligent agents pose catastrophic risks: can Scientist AI offer a safer path?" arXiv:2502.15657. Not searched. Check before use.

### 14. Dynabench, Kiela et al. 2021. Verdict: yes (searched)
- Kiela, D., Bartolo, M., Nie, Y., Kaushik, D., Geiger, A., Wu, Z., Vidgen, B., Prasad, G., Singh, A., Ringshia, P., Ma, Z., Thrush, T., Riedel, S., Waseem, Z., Stenetorp, P., Jia, R., Bansal, M., Potts, C., & Williams, A. (2021). "Dynabench: rethinking benchmarking in NLP." *Proc. NAACL 2021*, pp. 4110-4124. doi:10.18653/v1/2021.naacl-main.324. arXiv:2104.14337.
- Claim: human-and-model-in-the-loop dataset creation, where annotators try to fool a target model. Accurate. Author list above is from memory of the full list; the search confirmed 19 authors, Kiela first.

### 15. Dafoe et al., Open Problems in Cooperative AI. Verdict: yes (searched)
- Dafoe, A., Hughes, E., Bachrach, Y., Collins, T., McKee, K. R., Leibo, J. Z., Larson, K., & Graepel, T. (2020). "Open problems in cooperative AI." arXiv:2012.08630 (NeurIPS 2020 Cooperative AI workshop).
- Claim: defines the field as AI that helps humans and machines improve joint welfare. Accurate. It also discusses downsides such as exclusion and coercion.

### 16. Rubinstein bargaining (ADR 0009). Verdict: yes (recalled)
- Rubinstein, A. (1982). "Perfect equilibrium in a bargaining model." *Econometrica* 50(1): 97-109. doi:10.2307/1912531.
- Claim: alternating offers with discounting have a unique subgame-perfect equilibrium. Accurate (for the standard infinite-horizon model).

## Items requested beyond the "from memory" lines

### 17. Nozick's experience machine. Verdict: yes (recalled)
- Nozick, R. (1974). *Anarchy, State, and Utopia*, pp. 42-45. Basic Books.
- Claim: most people would refuse a perfect simulated pleasure machine, so pleasure is not all we value. Accurate as Nozick's intuition. Empirical caution: De Brigard (2010), "If you like it, does it matter if it's real?" *Philosophical Psychology* 23(1): 43-57, argues status quo bias explains part of the refusal (recalled).

### 18. Loss aversion about 2x. Verdict: partly (searched)
- Tversky, A., & Kahneman, D. (1992). "Advances in prospect theory: cumulative representation of uncertainty." *Journal of Risk and Uncertainty* 5(4): 297-323. Median lambda 2.25 in a small student sample. Earlier: Kahneman & Tversky (1979), *Econometrica* 47(2): 263-291; Tversky & Kahneman (1991), *QJE* 106(4): 1039-1061.
- Better current figure: Brown, Imai, Vieider & Camerer (2024). "Meta-analysis of empirical estimates of loss aversion." *Journal of Economic Literature* 62(2): 485-516. Mean 1.955 (95% interval 1.82 to 2.10) across 607 estimates from 150 articles.
- Fix: "about 2x" is fine, but cite the meta-analysis, and say it varies by domain and stakes. Do not cite 2.25 as a universal constant.

### 19. Axelrod's tournaments. Verdict: yes (searched)
- Axelrod, R. (1980). "Effective choice in the prisoner's dilemma." *Journal of Conflict Resolution* 24(1): 3-25. doi:10.1177/002200278002400101. A companion paper, "More effective choice in the prisoner's dilemma," is in 24(3): 379-403.
- Axelrod, R., & Hamilton, W. D. (1981). "The evolution of cooperation." *Science* 211(4489): 1390-1396. doi:10.1126/science.7466396. Book: Axelrod (1984), *The Evolution of Cooperation*.
- Claim: tit-for-tat won two round-robin tournaments. Accurate. Caution (recalled): with noise, more forgiving strategies do better (Nowak & Sigmund 1993, *Nature* 364: 56-58).

### 20. Fehr and Gaechter, punishment. Verdict: yes (searched)
- Fehr, E., & Gaechter, S. (2002). "Altruistic punishment in humans." *Nature* 415: 137-140. doi:10.1038/415137a.
- Claim: cooperation holds when participants can pay to punish defectors and collapses without it. Accurate. A 2005 reply (Fowler et al., *Nature*) argues egalitarian motives matter. Anti-social punishment exists in some cultures (Herrmann, Thoeni & Gaechter 2008, *Science*; recalled).

### 21. Hirschman, Exit, Voice, and Loyalty. Verdict: yes (recalled)
- Hirschman, A. O. (1970). *Exit, Voice, and Loyalty: Responses to Decline in Firms, Organizations, and States.* Harvard University Press.
- Claim: members facing decline can leave (exit) or complain (voice), and loyalty slows exit. Accurate and a good fit for "freedom means anyone can leave".

### 22. Sen and Nussbaum, capability approach. Verdict: yes (recalled)
- Sen, A. (1985). *Commodities and Capabilities.* North-Holland. Sen, A. (1999). *Development as Freedom.* Knopf. Sen (1980), "Equality of what?" (Tanner Lecture).
- Nussbaum, M. C. (2000). *Women and Human Development.* Cambridge University Press. Nussbaum (2011), *Creating Capabilities.* Harvard University Press.
- Claim: well-being is what people can do and be (real options), not only what they hold. Accurate. Difference: Nussbaum proposes a fixed list of central capabilities; Sen declines to. Empowerment and capability both measure real options, but capability is normative and plural, empowerment is information-theoretic.

## Counts

- Requested 19 items (Tinbergen, Butler, Berridge, Schultz, Fredrickson, poverty traps, empowerment, Turner, Leibo, Tronick, Gottman, Sen and Nussbaum, Dynabench, Dafoe, Nozick, loss aversion, Axelrod, Fehr and Gaechter, Hirschman): 12 yes, 7 partly, 0 no.
- Extra items found in the ADRs: GSAI yes, Rubinstein yes, Scientist AI unverified.
