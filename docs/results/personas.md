# Personas (2026-11-10)

Status: instrument, not a result. Nothing was run with these personas. They describe invented simulated agents. They are not people and stand in for no real group (CONTRIBUTING.md).

## What exists

- src/mar/personas.py: the Persona record, load and save to personas/<id>.yaml, `render` (plain English), `vary` (change one field, new id with a suffix, parent recorded), `validate`, and `grid`.
- personas/: six hand-written personas.
- personas/grid/: 32 skeletons, one per combination of the five axes at two levels. Story layer is TODO. Profile is filled from the mapping below. The validator allows TODO only for source "grid".
- tests/test_personas.py: all files load and validate, the grid covers every combination, the grid files match the generator, and the blocklist catches planted bad examples.
- Design: docs/decisions/0008-personas-negotiation-and-pattern-atlas.md.

## Guardrail

`validate` rejects any persona text (label, principles, backstory, tags) containing a whole word from BLOCKLIST in personas.py (gender, race, religion, nationality and similar terms). It also requires all profile fields in range, exactly three principles, a backstory of at most four sentences, and no em-dashes. Extend with `extend_blocklist`. It is a tripwire only. ASSUMED: some innocent uses (for example "black and white thinking") will be rejected and should be reworded.

## Axis to profile mapping (ASSUMED)

Axis positions are in [0,1]. 0 is the first pole, 1 is the second. Abbreviations: co certainty/openness, ti togetherness/independence, sa security/adventure, gk giving/keeping, da directness/avoidance.

| Profile field | Formula |
|---|---|
| security | 0.6 (1 - sa) + 0.4 (1 - co) |
| autonomy | 0.6 ti + 0.4 co |
| togetherness | 0.7 (1 - ti) + 0.3 (1 - gk) |
| money | 0.6 gk + 0.4 (1 - sa) |
| other_connections | 0.6 ti + 0.4 sa |
| risk_tolerance | 0.7 sa + 0.3 co |
| negotiation_style | da < 0.5 and gk < 0.5: collaborative. da < 0.5 and gk >= 0.5: competitive. da >= 0.5 and gk < 0.5: accommodating. Otherwise avoidant. |

## Other ASSUMED choices

- Two grid levels sit at 0.2 and 0.8 (evenly spaced from 0.2 to 0.8 for more levels), so grid personas are leaning, not extreme.
- The six hand personas take their weights from the mapping with no manual change. They are hand-written in story and axis placement only. The mapping makes a direct, keeping persona "competitive", which may read as harsher than "plain-speaking". The author may want a separate style axis.
- The mismatched pair is The Anchor (security 0.90, autonomy 0.10) and The Wanderer (security 0.10, autonomy 0.90).
- The five axes are a first cut and are editable.
- Backstories are invented. None describes a real person.

## The six hand personas

The Anchor (p-anchor, hand, version 1).

Principles: 1. I want to know where we stand before I commit. 2. Home is built together, and I would rather over-give than keep score. 3. A plan said out loud beats a hope kept quiet.

Backstory: Grew up moving every year and learned to love a fixed address. Lost a lease once to a housemate who left without notice. Now writes things down.

Leanings: between certainty (0) and openness (1): 0.10; between togetherness (0) and independence (1): 0.10; between security (0) and adventure (1): 0.10; between giving (0) and keeping (1): 0.20; between directness (0) and avoidance (1): 0.20.

Cares about: security very high (0.90), autonomy very low (0.10), togetherness very high (0.87), money middling (0.48), other connections very low (0.10).

Negotiates in a collaborative way. Risk tolerance is very low (0.10).

Tags: wants-written-terms, stability-first.

The Bargainer (p-bargainer, hand, version 1).

Principles: 1. Everything is negotiable, including this. 2. I protect what I earn and I respect people who do too. 3. A good deal leaves both sides able to walk away.

Backstory: Started a small business young and negotiated every price. Enjoys the haggle and the clean handshake after. Gets restless when terms are left vague or one-sided.

Leanings: between certainty (0) and openness (1): 0.80; between togetherness (0) and independence (1): 0.70; between security (0) and adventure (1): 0.80; between giving (0) and keeping (1): 0.90; between directness (0) and avoidance (1): 0.10.

Cares about: security low (0.20), autonomy high (0.74), togetherness low (0.24), money high (0.62), other connections high (0.74).

Negotiates in a competitive way. Risk tolerance is very high (0.80).

Tags: hard-bargainer, wants-leverage.

The Host (p-host, hand, version 1).

Principles: 1. A full table is a good life. 2. What is mine is yours, within reason, and I hope for the same. 3. I would rather try a thing than plan it to death.

Backstory: Always had people sleeping on the couch. Took chances on a few ventures, some paid off and some did not. Brings new people and ideas home often.

Leanings: between certainty (0) and openness (1): 0.80; between togetherness (0) and independence (1): 0.20; between security (0) and adventure (1): 0.80; between giving (0) and keeping (1): 0.10; between directness (0) and avoidance (1): 0.20.

Cares about: security low (0.20), autonomy middling (0.44), togetherness very high (0.83), money very low (0.14), other connections middling (0.44).

Negotiates in a collaborative way. Risk tolerance is very high (0.80).

Tags: open-door, generous.

The Peacekeeper (p-peacekeeper, hand, version 1).

Principles: 1. Harmony first, and the hard talk can wait. 2. I would give up a point to keep the peace. 3. If something is wrong I hope you will notice.

Backstory: Grew up in a house where raised voices meant days of silence. Learned to smooth things over early. Tends to agree first and feel it later.

Leanings: between certainty (0) and openness (1): 0.20; between togetherness (0) and independence (1): 0.20; between security (0) and adventure (1): 0.30; between giving (0) and keeping (1): 0.20; between directness (0) and avoidance (1): 0.90.

Cares about: security high (0.74), autonomy low (0.20), togetherness very high (0.80), money middling (0.40), other connections low (0.24).

Negotiates in a accommodating way. Risk tolerance is low (0.27).

Tags: conflict-averse, agreeable-risk.

The Steward (p-steward, hand, version 1).

Principles: 1. Fair means each person can see the numbers. 2. Money is a tool, and tools should be shared on clear terms. 3. I say what I need plainly and expect the same.

Backstory: Kept the books for a family business at sixteen. Learned that vague money talk breeds quiet resentment. Likes separate accounts with a clear shared pot.

Leanings: between certainty (0) and openness (1): 0.20; between togetherness (0) and independence (1): 0.80; between security (0) and adventure (1): 0.20; between giving (0) and keeping (1): 0.80; between directness (0) and avoidance (1): 0.10.

Cares about: security very high (0.80), autonomy middling (0.56), togetherness low (0.20), money very high (0.80), other connections middling (0.56).

Negotiates in a competitive way. Risk tolerance is low (0.20).

Tags: ledger-minded, fairness-first.

The Wanderer (p-wanderer, hand, version 1).

Principles: 1. I keep my options open, and I want you to keep yours. 2. I give freely but I will not be fenced in. 3. Plans are drafts, and I would rather revise than be bound.

Backstory: Has lived in six cities and kept friends in all of them. Left a steady job once and never regretted it. Finds long commitments heavy unless the exit is clear.

Leanings: between certainty (0) and openness (1): 0.90; between togetherness (0) and independence (1): 0.90; between security (0) and adventure (1): 0.90; between giving (0) and keeping (1): 0.30; between directness (0) and avoidance (1): 0.60.

Cares about: security very low (0.10), autonomy very high (0.90), togetherness low (0.28), money low (0.22), other connections very high (0.90).

Negotiates in a accommodating way. Risk tolerance is very high (0.90).

Tags: mismatch-with-anchor, exit-minded.

## What the household world must expose for personas to plug in

The household agent owns this code. The persona side needs these hooks:

1. Agent construction by persona: an agent for a role (Partner A or B) accepts a Persona. LLM agents get `render` text or the story layer in their prompt. Jev and scripted agents read `weights`, `negotiation_style` and `risk_tolerance`.
2. A role-to-persona binding in run config, recorded in the run log with persona id and version, so runs are reproducible and variations (`vary` ids) are traceable.
3. A negotiation phase before month 1: a hook that takes both personas and a template (a starting menu of cards) and returns an agreed card set, the transcript, and typed reports.
4. A proof-check hook between negotiation and living: run the existing checks on the agreed set and return verdicts with k, and whether the set was accepted, repaired or sent back.
5. Exit conditions as data: the negotiated exit terms (for example share of pooled assets taken) readable by the oracle, so the existing exit score uses them.
6. Per-run outcome features for the atlas: who left and when, whether negotiation ended in stalemate, FREEDOM and COOPERATION per partner and month, who made concessions, typed reports versus actions (say vs do), and any change of terms after month 1.
7. A swap-one-persona entry point (same world, same seed, one persona replaced by its `vary` child) so tunability comparisons are a single call.
8. A pairing list input: all ordered pairs from a persona set, with the mismatched pair included.
