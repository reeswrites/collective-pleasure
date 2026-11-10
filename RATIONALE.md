# Rationale

**Working title:** Multi-agent rules: proof-gated rule search for AI agent groups
**Status:** draft, 2026-11-10. Nothing here is a result yet.

---

## 1. Why this project

These are the commitments behind the project, in the author's words where possible.

The project started from the question "can unethical behavior be made impossible by mechanism rather than training?" It chose the multi-agent setting because sanctions, collusion and emergent norms only appear when several agents interact, and because the prior-art gap is clearest there.

The subject is formally specified rule systems (rules, norms, sanctions) governing groups of AI agents. Human institutions are a source of hypotheses and vocabulary, not the subject.

- **Mechanism, not only training.** Can some unwanted behaviors be made *impossible by design* rather than unlikely through training? Mechanisms can only rule out what can be specified. So the project focuses on the part of alignment that can be specified: the rules, permissions and sanctions that govern agents.
- **Good enough and improving.** Full proof of alignment isn't possible. But rule systems can be hill-climbed and checked, and they get better as AI reasoning and proof tools scale.
- **Rules and formalization are the interesting part.** The scarce work is writing and owning the spec. Generating code and checking proofs are getting cheap.
- **Learnings should generalize, and parallels should be provable.** A result about one rule system should carry over to another by a checkable argument, not by analogy.
- **No novelty for its own sake.** Every component must either already exist (and be reused) or earn its place by measuring something the simpler alternatives can't.

## 1a. Single-agent and multi-agent: one pipeline

Single-agent rules are the base case (n = 1) of the same pipeline:

1. formal rules, written in the ADICO-derived format;
2. proof check of the rules against invariants;
3. solver gate on each proposed action;
4. measure deviation of the agent's behavior from the formal rule system.

Multi-agent rules use the same four steps and add what only appears with interaction: peer sanctions, collusion, emergent norms, and coordinated attacks that slip past per-agent monitors.

So the first experiment is single-agent (S1: one agent under the fishery-quota rules, free-text vs solver-gated). It is cheaper, isolates the gate and the translation from interaction effects, and the multi-agent experiments then test what interaction adds.

## 2. Research question

> When LLM agents, alone or in groups, act under a rule system (rules, norms and sanctions), does specifying and proof-checking that rule system formally lead to better or more robust outcomes than free-text rules or hand-built governance? And can we measure precisely where agent behavior departs from the formal rule system?

## 3. Narrowest defensible claim

A pipeline that:

1. searches over rule systems written in an executable grammar derived from ADICO, the statement format of Institutional Grammar (IG);
2. gates candidates with solver-checked invariants: no deadlock, no rule conflicts, bounded sanctions, and a reachable exit or repair path;
3. reports a quantitative deviation of LLM-agent traces from the resulting formal transition system.

It is evaluated against two baselines: ungated evolution (Kumar et al. 2026) and runtime governance graphs (Institutional AI, 2026). The settings are one or two Ostrom-style games: a common-pool resource and/or a Cournot market.

This connects gaps that existing work names but leaves open:

- *Institutional AI* (arXiv 2601.10599) says governance graphs should be checked for coverage, deterministic transitions and incentive compatibility, but gives no toolchain.
- The LLM negotiation mechanism-design paper (arXiv 2608.14613) says ATL* model checking has not been connected to LLM conformance.

**We do not claim:**

- formal verification of normative systems (old; social laws, ATL synthesis);
- norm synthesis (old; IRON, SENSE, LION);
- LLM-driven evolution of constitutions (done 2026);
- runtime enforcement for agents (done 2026);
- LTL compliance scoring of agent traces (done; AgentLTL, Agent-C).

## 4. Prior art

| Component | Status | Closest work |
|---|---|---|
| Model-checking rule sets against invariants | Standard | van der Hoek, Roberts & Wooldridge 2007 (social laws in ATL); Ågotnes et al. 2007–08; IJCAI 2026 social-law synthesis |
| Equilibrium and incentive design under temporal goals | Standard | Gutierrez, Najib, Perelli & Wooldridge; EVE tool |
| Norm synthesis by simulation | Standard | Morales & López-Sánchez: IRON, SENSE, LION |
| IG/ADICO encoding and tooling | Exists, no solver semantics found | Frantz et al., IG 2.0 and IG Parser (2025) |
| Institutions (human-style) as executable logic | Exists | InstAL (answer-set programming); King, PARAGon (2016) |
| LLM evolution of constitutions | Done 2026, no formal checks | Kumar et al. (ICML 2026); Niranjani et al. (May 2026) |
| Runtime governance graphs for LLM agents | Done 2026, no formal checks | Institutional AI (Bracale Syrnikov et al., Jan 2026) |
| Normative rules plus LLM, checked formally | Partial | SLEEC-LLM (York, 2025); the LLM explains counterexamples, it isn't a simulated agent |
| Agent trace compliance | Done | Agent-C, AgentLTL, MANTRA |
| Bisimulation *between* rule systems | Not found | (low-confidence absence) |

Confidence that nobody has published the full pipeline: about 70%, from a single search pass. **Repeat the prior-art check before any write-up.**

## 5. Why nobody has combined these (and whether that is a warning)

**Plausible reasons:**

- **Separate communities.** Formal multi-agent researchers (AAMAS, KR) don't run LLM simulations. LLM-society researchers use free-text rules and empirical scores. IG/ADICO lives in policy science.
- **The translation loses information.** Proofs hold about the formal model, not the running agents' behavior.
- **The gate might prune little.** If most candidates are consistent anyway, gating adds cost but not value.
- **LLMs don't conform.** Corruption, collusion and charter-injection results show partial compliance at best.
- **Evolved rules overfit.** Niranjani et al. found that evolved constitutions became the *worst* performers when the incentive multiplier changed.

**The strongest objection.** "Your proofs hold for idealized agents. Your LLM agents don't conform, so the guarantee is vacuous. And measuring deviation just reinvents violation-rate evaluation with a heavy front end."

**How the design answers it.** The project is built to test this objection, not to assume it away (see experiments E1 and E3):

- Gating must change outcomes. Gated search has to produce rule systems that are more robust under parameter shift than ungated search.
- The deviation measure must tell us something a violation counter doesn't.
- If either fails, we say so (section 9).

**Where the author's contribution comes from.** The insight isn't any one piece. It is a background spanning all three communities:

- data-quality engineering: rules over schemas, labeled failures, drift checks;
- philosophy, plus a working IG/ADICO-to-Z3 engine (philosophy-engine);
- preregistration and independent review habits, with a willingness to report negative results.

## 6. Design decisions

**D1. New repo. philosophy-engine is an input, not the core.**

philosophy-engine's reference semantics are deliberately limited to tiny rule systems, and its checks are bounded to depth *k*. Its repo rules don't fit this project: work is paused pending its "worth-it" slice, and ADR 0011 forbids adversarial search, which robustness testing needs.

So we reuse its ADICO schema and possibly its reference engine as a check that our translation is correct. We don't build inside it.

**D2. ADICO/IG is the authoring and comparison layer and has to earn its place.**

ADICO comes from Ostrom's work on human institutions (Crawford & Ostrom; Frantz et al.). We borrow it only as a human-readable format for writing rules. The project's subject is AI agent groups, not human institutions.

It gives us:

- the split between rules, norms (no sanction) and shared strategies (no must/may);
- the sanction and the sanctioner as explicit fields;
- Ostrom's levels of rules about changing rules;
- comparability with human institutions already coded in the grammar, as a source of hypotheses;
- rule cards readable by non-programmers.

It is not a logic, and it compiles to one. **Kill criterion:** if ADICO-derived arms produce no difference from Cedar or LTL-only arms on any preregistered measure, drop ADICO and use the simpler format.

**D3. Shared semantic core: labeled transition systems.**

Candidate tool: **mCRL2**. It supports building transition systems, reduction and comparison up to several bisimulation equivalences, and modal mu-calculus model checking. Alternatives to evaluate: nuXmv, TLA+/Apalache, InstAL for institution-native ASP.

We don't reimplement bisimulation or model checking.

**D4. Main experimental variable: regimented vs regulated vs free text.**

This distinction is established in the normative multi-agent literature:

- **regimented:** violation is impossible; the solver gate blocks the action;
- **regulated:** violation is possible but sanctioned;
- **free-text:** the rules appear only in the prompt.

It is also the original mechanism-versus-training question in experimental form.

**D5. The deviation measure starts simple.**

- **Baseline:** violation rate, and LTL monitor verdicts in the AgentLTL style.
- **Candidate:** a simulation or approximate-bisimulation distance between the observed trace system and the formal rule system. Stochastic LLM behavior likely needs a probabilistic or approximate variant.
- It must beat the baseline (E3) or it is dropped.

**D6. Testbed.**

- Fork **GovSim** (common pool, MIT licence, supports open models). Optionally add a Cournot market to compare with Institutional AI.
- Cheap open models (Qwen, DeepSeek via OpenRouter or local) for most runs; Claude for comparison runs, paid with API credits.
- Gating pattern borrowed from **Agent-C**: Z3 checks each proposed action.

**D7. Bisimulation between rule systems is optional and comes later.**

There is no evidence of precedent and no evidence of value yet. It is worth pursuing only if it produces a falsifiable prediction, for example: "rule systems that are bisimilar after abstraction show the same collapse rate with LLM agents."

**D8. Out of scope for now: using swarms to model *human* norms.**

Human institutions remain a source of hypotheses (for example, Ostrom's design principles), not the subject. We test those hypotheses on AI agent groups only.

LLM agents aren't independent samples of humans. They have read the textbook results, they are homogeneous within a provider, and they are tuned to be agreeable. Revisit only with calibration: the setup must first rediscover known human patterns.

## 7. Experiments (draft, to preregister)

| ID | Question | Prediction (draft) | Baseline |
|---|---|---|---|
| S1 | Single agent: does a solver gate beat free-text rules? | A single agent under the fishery-quota rules violates them less, and deviates less from the formal rule system, when solver-gated than with free-text rules | Free-text rules in the prompt |
| E0 | Does the gate prune anything? | A non-trivial share of evolved candidate rule systems (≥ 20%) fail at least one invariant | — |
| E1 | Does gating improve robustness? | Gated-evolved rule systems degrade less under incentive or parameter shift than ungated ones | Kumar / Niranjani-style ungated evolution |
| E2 | Regimented vs regulated vs free text | Collapse rate: free text > regulated > regimented; regulated shows norm drift | GovSim's prompt-only rules (43/45 collapsed) |
| E3 | Is the deviation measure informative? | It predicts collapse or collusion earlier, or better, than violation counts | Violation rate, AgentLTL-style monitors |
| E4 (optional) | Do bisimilar rule systems behave alike? | Abstraction-bisimilar rule systems have statistically indistinguishable outcomes | Non-bisimilar matched pairs |

Use multiple seeds, report model versions, and fix the predictions before running.

## 8. Safety and dual-use

- Adversarial search (finding rule sets or agent strategies that break invariants) is in scope **for robustness testing only**. Findings are reported as defenses.
- No simulated populations stand in for real marginalized groups (carried over from philosophy-engine ADR 0011).
- Collusion and steganography stress tests stay within published benchmark settings.

## 9. Falsifiers and kill criteria

- **E0:** the gate rejects almost nothing, so gating is decorative. Narrow the claim to the deviation measure.
- **E1:** gated and ungated search are equally robust, so formal gating adds no value. Report the negative result.
- **E3:** the deviation measure adds nothing over violation counts. Drop it.
- **D2:** ADICO makes no difference against simpler formats. Drop ADICO.
- Any of these is a publishable negative result, not a failure to hide.

## 10. Process conventions (borrowed from philosophy-engine)

- Preregister predictions in `docs/claims.md` and commit them before running.
- Fresh-agent review councils before anything is called a result: correctness, consistency, scope, encoding faithfulness, and a card-only reader.
- Every rule has a one-sentence plain-English gloss and a source.
- Bounded verdicts state their bound, and "open" never means "safe".
- ADRs for design choices. Separate files for surprises and negative results.

## 11. First milestones

1. Repeat the prior-art check: classic norm synthesis, SLEEC, and the last month of arXiv.
2. Minimal ADICO → transition-system export for one tiny rule system (the GovSim fishery quota), cross-checked against philosophy-engine's reference engine.
3. Load it in mCRL2. Prove one invariant and find one counterexample.
4. A runtime `check_action` gate wired into a forked GovSim with a small open model.
5. Preregister S1, then run S1: one agent under the fishery-quota rules, free-text vs solver-gated (first experiment).
6. Preregister E0 and E2, then run E2 (cheapest and most legible multi-agent experiment).

## 12. Open questions

- mCRL2 vs nuXmv vs InstAL: which handles sanctions and obligations most naturally?
- What abstraction maps natural-language LLM actions onto formal actions, and how lossy is it?
- Which approximate or probabilistic bisimulation variant suits stochastic LLM traces?
- Should this live under an organization or fiscal sponsor later (for Cooperative AI or Coefficient funding)?

## References (starting set)

- Kumar et al., Evolving Interpretable Constitutions for Multi-Agent Coordination, ICML 2026: https://arxiv.org/abs/2602.00755
- Bracale Syrnikov et al., Institutional AI (Cournot collusion), 2026: https://arxiv.org/abs/2601.11369; framework paper: https://arxiv.org/abs/2601.10599
- Fei, Guo & Xiao, When Agents Evolve, Institutions Follow, 2026: https://arxiv.org/abs/2604.27691
- Albayaydh & Zhao, mechanism-design framework for LLM negotiation, 2026: https://arxiv.org/abs/2608.14613
- Tewolde et al., CoopEval, 2026: https://arxiv.org/abs/2604.15267
- Gupta et al., social learning and norm formation in LLM multi-agent systems, AAMAS 2026: https://arxiv.org/abs/2510.14401
- Piatti et al., GovSim: https://arxiv.org/abs/2404.16698 and https://github.com/giorgiopiatti/GovSim
- Agent-C: https://arxiv.org/abs/2512.23738
- Kleijwegt, Getir Yaman & Calinescu, SLEEC-LLM, 2025: https://arxiv.org/abs/2507.05504
- Frantz et al., IG 2.0: https://arxiv.org/abs/2008.08937; IG Parser: https://arxiv.org/abs/2505.13393
- van der Hoek, Roberts & Wooldridge, Social Laws in Alternating Time, Synthese 2007: https://link.springer.com/doi/10.1007/s11229-006-9072-6
- Ågotnes, van der Hoek & Wooldridge, Normative System Games, AAMAS 2007: https://www.ifaamas.org/Proceedings/aamas07/html/pdf/AAMAS07_0042_3a31772ad28b437feed4e14c8c07a40f.pdf
- Morales et al., IRON: https://abdn.elsevierpure.com/en/publications/iron-a-machine-for-the-automated-synthesis-of-normative-systems/
- EVE (rational verification): https://arxiv.org/abs/2008.05638
- InstAL: https://github.com/instsuite/instal-stable
- King, Governing Governance (PARAGon), 2016: https://arxiv.org/abs/1704.06654
- Hadfield, Trivedi & Hadfield-Menell, Building AI for the Democratic Matrix, 2026: https://knightcolumbia.org/content/building-ai-for-the-democratic-matrix-a-technical-research-agenda-for-normative-competence-and-normative-institutions-1
