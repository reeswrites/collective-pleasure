# 0011. Two modes, world-model framing, and why agents stay

Status: accepted (2026-11-10)

## Context

The author's conversation of 2026-11-10 settled several framings. The questions are recorded verbatim in experiments/questions.jsonl (topics shocks-as-misalignment, rupture-repair, staying-post, world-model-alignment, and earlier ones on moral standing and modes). The hedonic model itself is ADR 0010, owned elsewhere; this ADR only references it. Overview: docs/goal.md. Nothing here is a result. Anything cited from memory is marked "from memory, verify".

## Decisions

1. **Grounding.** Pleasure is the good (ethical hedonism). Agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled state derived from persona preferences. There are two kinds of suffering: offsettable and non-offsettable. Spirals run around a tipping point. Details are in ADR 0010. Motivation (why agents act: needs, aspirations) stays separate from evaluation (what makes outcomes good). Evolutionary theory explains behavior through fitness, with pleasure as a proximate and gameable proxy (Tinbergen's levels of explanation; Butler's argument against psychological hedonism; from memory, verify). The author's view is ethical hedonism, not psychological hedonism.
2. **Freedom as empowerment.** Empowerment is the number of distinct futures an agent can still reach, computed from the transition system (Klyubin, Salge and Polani; from memory, verify). It is reported alongside the hand-made freedom score first. Power-seeking is one agent grabbing options at others' expense (Turner et al.; from memory, verify). The motivation architecture is an experimental axis for later: wanting vs liking, homeostasis, empowerment-seeking, and appropriateness (Leibo; from memory, verify).
3. **Two modes, question left open.** Delegates: AI agents serve human principals. Humans' welfare counts. Agents are bound by rules at least as strict as anyone's. This is the direct alignment setting. Peers: every member's modeled welfare counts equally. It models human life, and keeps open a future where AI agents count as members. The author does not settle in advance whether AI agents have welfare. Agents may not value things the way humans do, so serving may be fine. The author does not want to settle it before experiments. Experiments cannot settle the metaphysics. They can show whether it matters. We report norms that win in both modes (robust to moral uncertainty) and where the modes split. Equal constraints (safety) are distinct from equal claims (welfare). Role-swap symmetry is checked by bisimulation: between humans in both modes, and between humans and AI in peer mode only.
4. **Shocks.** Exogenous shocks are misalignment in the wider system (economy, workplace, health), not random fate. They are kept rare and tunable. Version 3 adds endogenous ruptures. Tension accumulates from mismatches and a rupture fires at a threshold. Each rupture is traced to the rule that allowed it. That trace is a seam.
5. **World-model framing.** In small, the project has the Guaranteed Safe AI shape (Dalrymple, Bengio, Russell et al. 2024; from memory, verify). The world model is the household sim with counterfactuals. The specification is pleasure, non-offsettable suffering, empowerment and norms. The verifier is the proof checks, the seam ladder and the evaluator. There are two alignments. Value alignment: norms produce good lives. Epistemic alignment: agents' appraisals match reality. A delegate-mode failure to test: a delegate that exploits its principal's appraisal biases (sunk cost, creeping normality) to keep them in place. That is manipulation through the person's world model, and a candidate inventive seam. Prediction alignment is measurable because counterfactual lives can be simulated (cf. Bengio's Scientist AI; from memory, verify). Limit: the household is our world model. Predictions about real people are hypotheses until the household reproduces known real-world findings. That is fidelity, checked through the simple-models ladder (ADR 0009).

## Why agents stay (version 3)

6. **Source and split.** The base is the author's post https://reeswrites.com/posts/staying-in-bad-relationships/. It separates appraisal from actual quality. Staying in a bad relationship comes from misappraisal or risk aversion: valid but unsound premises.
   - Actual quality is computed by counterfactual runs: the same persona alone, or with another partner, from the same start. "Clearly better off elsewhere" is a preregistered gap.
   - Appraisal is each agent's belief. The agent acts on it.
   - Misappraisal is the gap between the two. It is measurable.
   - The post's mechanisms become switchable appraisal biases: creeping normality (the reference point slides), sunk cost, risk aversion about alternatives, overestimated detachment cost, hedonic treadmill (highs erase lows), charitable attribution of a partner's behavior, plus self-esteem and imagination limits.
   - Rupture and repair is the good side. The post does not cover repair. Secure relationships repair ruptures rather than avoid them (Tronick; Gottman's repair attempts; from memory, verify). This links to the author's 2025 note that relationships built on certainty and control are brittle. The original "repair path exists" invariant gains a relational meaning.
   - The "why they stay" diagnostic sorts reasons. Good reasons: actual pleasure, trust in repair. Bad reasons: trapped, wanting what stopped being good, misappraisal. Norms are judged by which reasons their households run on, from measured quality, not self-report.
   - Prediction to preregister later: the author's seed norms ("see anyone freely", "exit conditions negotiated before", "request is never about control") show less misappraisal than norms without those features.
   - Appraisal accuracy becomes a third score alongside freedom and pleasure.

## Consequences

- Order of work: hedonic build (ADR 0010), empowerment, two modes, then version 3.
- The rediscovery test's missing cycles (ADR 0009, docs/negative-results.md) stay logged as a negative result and are deferred.
- Claims MU1, AP1 and DM1 are drafted in docs/claims.md. None is finalized.
- Version 3 scope is in docs/plan.md.

## Amendment 2026-11-10

Freedom is now defined in ADR 0014: equal liberty minus a domination penalty, where withdrawal does not count as domination. Plain empowerment is now one of three reported freedom measures, not the main one. Predictions MU1, AP1 and DM1 are still draft predictions.


## Amendment 2026-11-10 (fidelity wording, per the scope review S4)

The simple-models ladder checks the pipeline and its algebra against closed forms and published equilibria (VPGG, bargaining). It does not establish that the household is a faithful model of real households. Household fidelity needs its own battery of known real-world findings, which is in the backlog (docs/plan.md). The Guaranteed Safe AI reference is verified in docs/references.md.
