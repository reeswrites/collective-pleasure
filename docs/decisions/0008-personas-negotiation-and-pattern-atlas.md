# 0008. Personas, negotiation-first households, and the pattern atlas

Status: accepted (2026-11-10, author decisions in conversation)

## Context

The author's household seed (docs/seeds/author-household-norms-2026-11-10.md) says nobody owes anyone anything day to day except what they negotiated, and that leaving is allowed any time and triggers exit conditions negotiated beforehand. The author added that negotiation is a heavy thing for people to do, and that modeling it could give good templates ("batteries not included ... let's create some off the shelf parts", the author's 2025 note). This ADR records the design that follows. Nothing here is a result.

## Decisions

1. **The household is negotiation-first.** It runs in phases. (1) Negotiate: the partners agree terms and exit conditions before living together, written as ADICO cards. This is a rule-about-rules phase, Ostrom's collective-choice level. (2) Proof-check: the agreed card set is checked for traps (conflicts, deadlock, no repair path, one-sided exit costs) before anyone lives under it. Verdicts state k. (3) Live: the existing household world, where nobody owes anything beyond what was agreed. (4) Exit: leaving is allowed any time and triggers the negotiated conditions.
2. **Personas have two layers.** The story layer is three principles and a short backstory in natural language. LLM agents play it. The profile layer is typed: weights in [0,1] for security, autonomy, togetherness, money and other_connections; a negotiation style (direct, accommodating, avoidant, competitive, collaborative); risk tolerance; free tags. Jev agents and analysis read the profile. Between them sit five axis positions (certainty vs openness, togetherness vs independence, security vs adventure, giving vs keeping, directness vs avoidance). The axes are editable. Code: src/mar/personas.py. Files: personas/<id>.yaml.
3. **Diversity is a grid plus a smaller share of free personas.** Grid personas come from axis combinations (2 levels on 5 axes gives 32). Their story layer starts as TODO and is filled later. Free personas are added later by an LLM generator, not now. Six hand-written personas span the axes and include a deliberately mismatched pair.
4. **Guardrails.** Principles and histories only. Never gender, race, religion, nationality or other group identities. No real people. Backstories are short and plausible. This follows the dual-use rule in CONTRIBUTING.md: no simulated populations stand in for real marginalized groups. The validator rejects persona text that uses a word from an explicit blocklist. The blocklist is a tripwire, not a proof, and a human reads every persona.
5. **Sameness is a finding.** LLM agents tend to play everyone as agreeable. If personas that should clash behave alike in runs, that is recorded in docs/negative-results.md or docs/surprises.md as a result about the agents. It is not hidden or tuned away.
6. **Tunability.** `vary(persona, field, value)` changes one principle, weight or axis and gives a new persona with a parent link. Rerun and compare to see what is load-bearing.
7. **Evolution can evolve negotiation templates, not only rules.** A template is a starting menu of terms (which cards are offered, with which defaults and exit conditions). Templates are scored across many persona pairings, mismatched ones included, on the freedom and cooperation frontier from ADR 0007. A good template does well across pairings, not just for one pair.
8. **Pattern atlas.** A pattern is a named kind of thing that happened in a run. Examples: stable mutual aid, quiet dominance, early exit, stalemate in negotiation, slow drift of the bargain. Each entry has a plain-English name, an example story, and the persona pairings and rules that lead to it. Runs are grouped later by a simple clustering over outcome features and say-vs-do gaps (typed reports against actions, ADR 0007 item 12). The author reads and names the clusters and checks them. Names come from the author, not from the clustering.

## Caveat

LLM agents are not people. Anything this produces is a tested starting point for human conversations, not proven advice. Claims stay about rule systems and simulated agents.

## Consequences

- The household agent owns the world code. What the world must expose for personas is listed in docs/results/personas.md.
- Slices still to do: a negotiation phase in the world, the LLM generator for free personas and grid story layers, template evolution, the atlas clustering.
- The hand personas are the author's to edit. Nothing in docs/claims.md is added here; predictions go there before runs.

## Status note 2026-11-10

For the negotiation protocol, see ADR 0013. For the author corrections, see `docs/seeds/author-household-norms-2026-11-10.md`.

## Status note 2026-11-10 (negotiation results)

Negotiation is built and run as ADR 0013 (scripted v1, v2 and v2.1, and a Haiku 5.5 pilot; docs/results/README.md rows 19 to 22). Predictions held 2 of 6, 0 of 8 and 3 of 5. The sign of the effect of real outside options flipped between v2 and v2.1 with the model of what a failed negotiation means, so the conclusions depend on assumed protocol choices. The proof filter caught one kind of trap in the menu, which the study's author defined. "Proof-checked for traps" here means checked to depth k = 3 within the compiled model.
