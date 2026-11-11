# 0016. Pleasure levers: adaptation and anticipation, commitment as a converter, unbundled networks

Status: accepted (2026-11-10)

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

## Context

The author confirmed seed v2.2 on one condition: it "can demonstrate pleasure in relationships hedonic technology" (docs/seeds/author-household-norms-2026-11-10.md). The first demonstration (docs/results/pleasure-demo.md) met the preregistered rule but found rules mostly protect: relational pleasure came from persona weights, trust never moved, 212 of 328 agreed households made no commitment, and for the 15 hand-persona pairings seed v2.2 was lower than the imposed baseline (0.836 vs 0.864). The synthesis of the author's own notes (docs/notes/hedonic-technology-synthesis.md) traced this to missing mechanisms: no adaptation, no anticipation, commitment modeled as a constraint rather than a converter, one partner carrying every strand.

## Decision

Build the three levers with the strongest support in the notes, each behind a flag that defaults OFF, with every number ASSUMED in one config block (`hedonic.LeverConfig`) and the source note named beside each group.

1. **L-A adaptation and scheduled anticipation** (synthesis M1, M3). Satiety per variant of a repeated pleasure (fast, restored by time away and rotation), tolerance (slow, restored only by spacing), a small switch cost. A ritual is a recurring scheduled shared slot: it pays anticipation before the slot (scaled by how many slots lie ahead and by the share of recent slots kept), is cancelled if either partner cannot attend, and can be created by a negotiated week-0 stub (personas.ritual_proposal / accepts_ritual) or imposed by a `must` card with aim `ritual`; a `must_not` card forbids it. New rule variant `author_seed_v2_ritual_card` (seed v2.2 bindable plus a `may` ritual permission; the author-confirmed seed directories are untouched).
2. **L-B commitment as a converter** (M4). An honored commitment costs offsettable chosen friction each week and builds a compounding stock K that adds pleasure; a breach resets part of K and costs trust as before; no fine unless negotiated. Enforcement and reliance are separate quantities.
3. **L-C unbundled networks** (M5). Six strands, a thick core partner and thin or thick external bonds; supply per strand falls when a bond carries more strands than its capacity; cover is redundant across bonds; coordination cost is convex in the number of bonds; bond shocks hit one bond at a time with common random numbers.

Persona policies use the levers where principles fit (personas.lever_policy; mapping in the preregistration). Flags: `WeeklyWorld(levers=LeverConfig(...))`, or `with hedonic.use_levers(cfg):` so the worlds negotiation builds are covered too.

## Backward-compatibility contract

Additive only: no existing function signature changes except a trailing optional `levers=None` on `WeeklyWorld` and `run_weekly` and an optional `extra_pleasure=0.0` on `Hedonic.close_week`; `"ritual"` joins `EXTRA_ACTIONS` so cards with that aim lint (no existing card uses it). With every flag off nothing lever-related is read and runs are bit-identical: `tests/test_levers_regression.py` pins sha256 fingerprints of 10 runs (8 weekly rule sets including seed v2 and the pressing personas, 2 negotiated lived households), computed before the levers existed. Lever-only keys (`hedonic[r]["lever"]`, `Run.lever`, `obs["lever"]`) appear only when a flag is on.

## Evidence

Preregistration (committed before any lever run): docs/results/pleasure-levers-prereg.md. Results: docs/results/pleasure-levers.md. Read the results file for what held; the decision above is to keep the levers in the model, not a finding that they matter in people.

## Next levers (recorded, not built)

Per the author's steers on 2026-11-10, in priority order. Each would be a new default-off flag, preceded by a dated prereg amendment before any affected run, with parameters ASSUMED in the same config block.

- **Contact frequency, release and mismatched optimal gaps** (source: the author's 2026-09-10 claude.ai conversation on the optimal time between seeing someone, not archived in the repo; described to us by the author). (1) Contact frequency as a negotiable term or ritual: how often partners or friends see each other (a card or term, like the weekly ritual with a period). (2) Release as a pleasure source: missing builds tension while apart (closeness times want-to-see, with baseline adaptation to absence) and releases at reunion, so gaps add pleasure up to a point and then subtract as closeness decays. (3) Mismatched optimal gaps between two people (persona-dependent): the person with the shorter optimum experiences "slow fade" as a harm (offsettable suffering unless prolonged). Prediction to preregister: negotiated contact frequency reduces mismatch harm relative to unnegotiated. The ritual period parameter and the bond quality stock in L-C are the natural hooks.
- **Memory** (the author, 2026-11-10, verbatim: "i think the experieicing self is the remembering self and depends onf vividness of memory etc"). Experiences leave memory traces with vividness (intensity or peak, ending, novelty, being shared, emotion; decaying); each week's pleasure includes re-experienced memories weighted by vividness; painful vivid memories re-cost (rumination after a betrayal or bad ending); anticipation of scheduled events is already in L-A; lifetime pleasure is the sum of weekly totals including memory. Predictions to preregister: rituals and reunions with good endings raise lifetime pleasure beyond equal time spread thin; vivid breaches keep costing, linking to trust (which never moved in the first demonstration because no breach occurred). The weekly `lever` row and the commitment stock K are where a recall term would attach.
- **Shared-experience amplification** (the author, 2026-11-10, recorded verbatim in experiments/changes.jsonl: "if you like eating with others then it makes sense that it could amplify or channel pleasure with eating with another person or if you like watching movies and it would be cooler to share and watch with someone else"). Activities (eat, watch, walk, concert, rest, read) can be done alone or together; together multiplies the activity's pleasure by a factor of closeness (the L-C bond quality), taste overlap between the two personas for that activity, and the activity's sociability; some activities have factor below 1 (better alone); shared bad experiences are amplified too (Boothby, Clark and Bargh 2014, "Shared experiences are amplified", cited from memory, to verify before use). Personas choose which activities to share and with whom (partner or friends), which gives unbundling love a concrete meaning: different bonds amplify different activities. Predictions to preregister: under amplification close pairs share more ordinary activities and relational pleasure rises with taste overlap; mismatched tastes reduce or invert amplification. Hooks: the L-A variants (activity types) and L-C bond quality q and strand holdings. Parameters ASSUMED in the lever block; default-off flag; dated prereg amendment before any affected run.
- Also left: optimal-stimulation curve (M2), give/share/receive roles (M6), wanting versus liking (M7), producing-versus-protecting card tags and attribution report (M8), metrics from the author's list (M9), and adding the ritual as a term inside the negotiation bundle (negotiation.py was not extended; the ritual is a week-0 stub).

## Consequences

- Seed v2.2 can now be evaluated with and without levers on the same seeds; the report states which lever moved what.
- The model is more parameterized. Lever payoffs are written in, so "the lever raises pleasure" is partly true by construction; what the runs can show is sizes, crossings, break-evens, and whether the rules produce pleasure that the baseline lacks.
- The lint vocabulary now includes `ritual`; any future change to EXTRA_ACTIONS should check adapter code.
