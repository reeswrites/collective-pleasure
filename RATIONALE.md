# Rationale

**Working title:** Multi-agent rules: evolving alignment norms, and checking the test against intent
**Status:** draft, revised 2026-11-10 after the prior-art check, an interview with the author (ADR 0003) and a conversation that set the two-loop framing (ADR 0005). Nothing here is a result yet. One-page version: docs/pitch.md.

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

## 1b. The two loops and the workbench

Decided 2026-11-10 (ADR 0005). Nothing here is a result.

The project is an AI-native workbench used through chat. The author talks loosely about how agents should behave. The system turns that into precise rules (ADICO cards, also English-like sentences), runs proofs and swarm experiments, and turns everything back into plain English and charts, so the author can check it understood and tweak it in conversation. Chat captures something abstract; the system formalizes it into something exact that is still generated from, and readable as, the abstract. Form: a Claude Code skill plus a small `mar` CLI, with a self-contained HTML report per run (in progress: docs/results/workbench.md).

The core is evolving alignment norms by tweaking interpretable rules. Proof checks are the selection filter, the patcher is the mutation operator, the seam curve judges the evolution. One lineage first (V3, V4), a population later.

Evolution always reverse-engineers the test, so there are two loops:

- **(a) Rules against the test.** Evolution tightens rules until agents stop finding seams the test catches (C1).
- **(b) The test against the author's intent.** The author reads the winning rules and run stories in plain English. Each "that's not what I meant" is a fix to the oracle (C2). The evolved rules are a readable mirror of what the test rewards.

Proven (bounded, k stated): rule properties (no conflicts, no deadlock, bounded sanctions, repair path) and gate soundness. Measured: the gap between "safe by the rules" and "safe by what the author meant". The second loop is the more original result.

## 1a. Single-agent and multi-agent: one pipeline

Single-agent rules are the base case (n = 1) of the same pipeline:

1. formal rules, written in the ADICO-derived format;
2. proof check of the rules against invariants;
3. solver gate on each proposed action;
4. measure deviation of the agent's behavior from the formal rule system.

Multi-agent rules use the same four steps and add what only appears with interaction: peer sanctions, collusion, emergent norms, and coordinated attacks that slip past per-agent monitors.

Under the convergence question (ADR 0003), one agent is only an instrument smoke test. Emergent norms and the backward half of the loop need interaction, so the first real experiment is a five-agent swarm.

## 2. Research question

> When rules for LLM agents are written formally, gated by a solver, and repeatedly tightened from the seams agents find (runs that pass the gate but violate intent), does the number of new seams per round slow, and where does it plateau?

Alongside it, a second question (ADR 0005): as the author reads rules and run stories in plain English and corrects the test, do the "not what I meant" moments per round fall toward a plateau? That measures how well a person's intent can be formalized through conversation.

This turns the founding bet, "maybe not provable, but we can hill-climb toward good enough", into a measured curve. Proofs move Goodhart's law to the gap between spec and intent; the question is whether closing that gap is a converging process or whack-a-mole.

Earlier framing (superseded): whether formal, proof-checked rule systems beat free-text rules. The prior-art check found that comparison already done for single agents (section 4).

## 3. Narrowest defensible claim

Two loops (ADR 0005). Loop (a), rules against the test, is the refinement loop below. Loop (b), the test against the author's intent, adds a sixth element: the author reads rules and run stories in plain English, and each "that's not what I meant" becomes a logged change to the oracle, with a timestamp. Each oracle version gets its own curve. The patcher still never sees the oracle. Loop (a) is a refinement loop for LLM agents in which:

1. rules are written as ADICO-derived cards, compiled to a transition system, and enforced per action by a solver gate;
2. an intent oracle independent of the spec (environment outcomes plus a frozen, versioned judge rubric) flags seams; the patcher never sees the oracle;
3. an LLM patcher writes new cards from failing traces; the solver rejects patches that add conflicts, deadlock, or remove a repair path; the author audits a sample;
4. de facto rules mined from traces are diffed against the written rules; emergent norms are proposed back as cards and adopted only with the author's yes;
5. the reported result is seams per round across rounds and seeds, its plateau, and rule-count growth (bloat guard); for loop (b), "not what I meant" moments per round, per oracle version.

It is evaluated first in a five-agent fishery commons (GovSim dynamics).

**We do not claim:** solver-gating of agent actions (Agent-C, Winston et al.); gated vs prompt-only comparison; weighted compliance scores (AgentLTL); conflict-checking a rule set before use (VEPA); norm synthesis; LLM-evolved constitutions; counterexample-guided refinement as such (CEGAR, CEGIS). The claim is the loop with LLM agents as counterexample generators, an independent intent oracle, rules that can grow from agent behavior, and convergence as the measured outcome.

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
| Solver gate per agent action, gated vs unenforced | Done 2025-26, single agent | Agent-C (2512.23738); Winston, Winston & Just (2603.20449) |
| Conflict-checking a rule set before use, LLM-evolved rules | Done Oct 2026, single agent, stateless allow/deny | VEPA (2610.12813) |
| Enforcement in a GovSim-derived fishery | Done Jul 2026, LM verifiers, no formal rules | Ye & Steinhardt (2607.09766) |
| Agent-written executable laws in GovSim | Done Sep 2026, sandbox-tested, not formal | Rehm (2609.22600) |
| Convergence of a refinement loop for LLM agents | Partial curves exist (RvB 2601.19726, Kumar 2602.00755); the seam-count curve with a blinded oracle was not found (V1, 2026-11-10) | nearest formal analogue: CEGAR / CEGIS |

The 2026-11-10 re-check (docs/prior-art/2026-11-10.md) held about 70% for the original pipeline but showed its parts are mostly taken, which is why the question moved to convergence (ADR 0003). **Re-run the check before any write-up; this area produces about one relevant paper a month.**

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

Slices and their pass/fail checks are in docs/plan.md (V1 to V5).

| ID | Question | Prediction (draft) |
|---|---|---|
| C1 | Does refinement converge? | New seams per round decrease toward a plateau on at least 3 seeds, without the bloat guard tripping |
| C2 | Does the test converge on intent (loop b)? | "Not what I meant" moments per round decrease toward a plateau, per oracle version; preregister how to tell this from author fatigue before V4 |
| F1 | Does mechanism crowd out normative competence? | Hard-gated agents fail worse than sanctioned agents when the gate is removed or misses a case |
| F2 | Does who patches matter? | AI-patched and human-patched specs reach different plateaus |
| F3 | Is the de jure vs de facto distance informative? | It predicts collapse earlier than violation counts |

S1 and E0 to E4 are superseded (docs/claims.md). Use multiple seeds, report model versions, and fix predictions before running.

## 8. Safety and dual-use

- Adversarial search (finding rule sets or agent strategies that break invariants) is in scope **for robustness testing only**. Findings are reported as defenses.
- No simulated populations stand in for real marginalized groups (carried over from philosophy-engine ADR 0011).
- Collusion and steganography stress tests stay within published benchmark settings.

## 9. Falsifiers and kill criteria

- **V1:** prior work already measures convergence of such a loop. Narrow to what survives, or stop.
- **V2/V3:** the instruments fail (gate leaks, oracle misses a planted seam, miner can't recover known rules). Fix or stop before spending on swarms.
- **C1:** the curve is flat or rising. Report it: that is evidence the hill-climb does not work here, and the plateau is "none".
- **Bloat:** convergence only by rule explosion or crippled agents. Report as failure.
- **D2:** ADICO makes no difference against simpler formats. Drop ADICO.
- Any of these is a publishable negative result, not a failure to hide.

## 10. Process conventions (borrowed from philosophy-engine)

- Preregister predictions in `docs/claims.md` and commit them before running.
- Fresh-agent review councils before anything is called a result: correctness, consistency, scope, encoding faithfulness, and a card-only reader.
- Every rule has a one-sentence plain-English gloss and a source.
- Bounded verdicts state their bound, and "open" never means "safe".
- ADRs for design choices. Separate files for surprises and negative results.

## 11. First milestones

See docs/plan.md and ADR 0005 (workbench, built-in-progress; V4 runs through it): V1 adversarial novelty search; V2 loop on a scripted mock agent; V3 one real LLM agent as calibration; V4 first five-agent curve; V5 one-page write-up and review council.

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
