# Pleasure levers preregistration (ADR 0015 template; ADR 0016)

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Status: written and committed before the first run of any lever. Nothing here is a result. Scripted persona-driven agents; no model calls. Parameters below are ASSUMED and are frozen at this commit; the confirmatory run uses exactly them. The only thing a later amendment may add is the seed count (from the power check on an exploratory pilot) and the pilot table.

Source of the theory: docs/notes/hedonic-technology-synthesis.md (a reading of the author's own notes; every mechanism names its note below). The author's condition for seed v2.2 (docs/seeds/author-household-norms-2026-11-10.md, verbatim): "yes as long as it can demonstrate pleasure in relationships hedonic technology". The previous demonstration (docs/results/pleasure-demo.md) found rules mostly protect: relational pleasure came from persona weights, trust never moved, most households made no commitment, and for the 15 hand-persona pairings seed v2.2 was lower than the imposed baseline (0.836 vs 0.864). This run asks whether three mechanisms the author's notes name, once they exist in the model, make rules produce pleasure.

## Purpose and claim

Three levers, each behind a flag that defaults OFF (flags off reproduces every earlier result bit for bit; checked by a pinned fingerprint test):

- **L-A adaptation and scheduled anticipation** (synthesis M1 and M3; sources: "Optimal Stimulation and Hedonic Homeostasis", "Engineering On-Demand Pleasure Technology", "Relationships as a Hedonic Technology" on rituals). Repeated pleasures satiate (fast) and build tolerance (slow); spacing and rotating among variants restore them; a ritual is a recurring scheduled shared activity that pays anticipation before it happens.
- **L-B commitment as a converter** (M4; source "Commitment Is a Pleasure Technology"). A chosen commitment costs a little each week it is honored (chosen friction) and builds a slowly compounding relational payoff (shared history and reliance). Enforcement stays what seed v2.2 says: a breach costs trust and resets part of the payoff; no fine unless negotiated.
- **L-C unbundled networks** (M5; source "unbundling love"). Agents hold a thick core (the partner) plus several thin bonds. Six strands (care, affection, intimacy, logistics, commitment, desire) are supplied by whichever bonds hold them; a bond carrying too many strands supplies each less well; a coordination cost grows convexly with the number of bonds; shocks hit one bond at a time.

Claims tested (docs/claims.md ids to be added after the run): the synthesis predictions P1, P3, P4, P5, P8, and the headline, the author's condition: **with the levers ON, seed v2.2 beats the imposed baseline on mean pleasure among the 15 non-pressing (hand-persona) pairings, which it did not before** (docs/results/pleasure-demo.md: -0.028). A decision this changes: whether the household rule vocabulary should grow producing cards (rituals, commitments by timescale) and whether commitments and bonds belong in the world.

## Design

World: the weekly household world (156 weeks), `WeeklyWorld`, persona-driven agents. Levers live in `LeverConfig` (src/mar/hedonic.py, one block). All lever code is guarded by the flags.

Two kinds of run.

1. **Controlled mechanism runs** (LA, LB, LC claims). Fixed cards `author_seed_v2_bindable`, deal `{"pot": true, "commits": []}` unless the arm says otherwise (open shared pot, no negotiation, so the lever is the only thing that differs between arms). 57 pairings (the 15 hand-persona pairs and the 42 ordered pairs containing a pressing persona, as in the pleasure demo). Arms differ by lever settings only; shock schedules are common random numbers across arms (depend on seed and pairing only).
2. **Headline runs** (H1, H2). The pleasure-demo protocol: negotiation v2.1 (`fair_default`, one shared pot with open use, exit floor on, a failed negotiation means living apart, reviews every 13 weeks), the 15 hand-persona pairings only (the non-pressing cohort), arms: seed v2.2 bindable (`author_seed_v2_bindable`) and the imposed `baseline`, each with all levers OFF and with all levers ON; plus ablations of v2.2 with each lever alone and with the ritual lever off.

**Unit of resampling: the pairing**, with its seeds clustered together (seeds within a pairing share the pairing's structure). All pairing-level quantities are the mean over that pairing's seeds of the mean over both partners and all weeks of modeled pleasure, unless a window is named.

**Seeds** are 0 to S-1 with S fixed by the power check (Amendment 1), capped at 8 for controlled arms and 15 for headline arms. Exploratory pilot seeds are 900 to 902, excluded from every confirmatory number.

### Persona policies (documented mapping; ASSUMED)

Persona agents use the levers where their principles fit (src/mar/personas.py, `lever_policy`):

| Lever | Persona fit (profile weights and axes) |
|---|---|
| L-A variety | a persona that values openness (certainty_openness >= 0.5) or adventure (security_adventure >= 0.5) rotates variants; others repeat the best one. The `adaptive` policy (spacing: utility of an action falls with its habituation) is used by personas with risk tolerance >= 0.5. Controlled runs force one policy for everyone. |
| L-A ritual | proposed by personas with togetherness >= 0.5 and security >= 0.4 (they want a fixed time); accepted by personas with autonomy < 0.6. Both conditions must hold for a negotiated ritual (like `commitment_proposal`). A `must` ritual card imposes it. |
| L-B commitment | the existing `commitment_proposal`/`accepts_commitment` (security >= 0.6, autonomy < 0.4, togetherness >= 0.5 propose a 52-week mutual stay). Controlled runs force a mutual 52-week stay for every pairing. |
| L-C bonds | friends other than the partner: `1 + round(3 * other_connections)` external bonds, at most 5 (a persona who values other connections holds more); the first `round(togetherness)` external bonds are thick (3 strands) when the persona values togetherness at 0.8 or more. Controlled runs force the count. |

### Mechanisms and ASSUMED parameters (frozen)

L-A (M1, M3):

| Parameter | Value | Meaning |
|---|---|---|
| n_variants | 3 | variants of a time-together activity (dinner, outing, home), each with its own satiety |
| hab_rate | 0.30 | satiety of a variant rises by this share of (1 - h) per session |
| hab_recover | 0.15 | satiety falls by this share of h each week |
| tol_rate, tol_recover, tol_cap | 0.02, 0.01, 0.4 | slow tolerance t in [0, 1] (shared across variants of an activity): the scale on a session is (1 - h) x (1 - tol_cap x t) |
| switch_cost | 0.05 | share of a session's scale lost when it uses a different variant than the last (low-tax micro-novelty) |
| antic_gain | 0.04 | weekly pleasure from a scheduled ritual, times the share of the next `antic_horizon` weeks that hold a scheduled slot, times reliability (the share of the last 8 slots kept, 1.0 at start) |
| antic_horizon | 4 | weeks |
| event_boost, prep_units | 0.0, 0 | richer prepared event and its prep cost: exist for sensitivity, OFF here so the ritual test isolates anticipation |
| ritual period | 1 | weekly; both partners reserve 2 units at the start of the week; a slot is cancelled if either is ill, moved, out of the household or short of units |

L-B (M4):

| Parameter | Value | Meaning |
|---|---|---|
| commit_friction | 0.02 | offsettable suffering per week per commitment the agent is bound by and is honoring (chosen friction, not non-offsettable) |
| k_rate, k_decay | 0.02, 0.004 | payoff stock K in [0, 1]: K rises by k_rate x (1 - K) in a week when a commitment stands unbroken, falls by k_decay x K otherwise (half-life about 170 weeks) |
| k_pay | 0.10 | weekly pleasure added to each partner, times K |
| breach_loss | 0.5 | share of K lost on a breach (trust loss is the existing 0.3) |

L-C (M5):

| Parameter | Value | Meaning |
|---|---|---|
| strands, weights | care .25, affection .20, intimacy .20, logistics .15, commitment .10, desire .10 | share of the strand pleasure each strand carries |
| bond_capacity | 3 | strands a bond carries at full effectiveness; supply per strand = quality x min(1, 3 / strands held) |
| strand cover | 1 - product over holding bonds of (1 - supply) | redundancy raises coverage |
| strand_pay | 0.20 | weekly pleasure when every strand is fully covered |
| care_suffer | 0.15 | offsettable suffering scaled by how far care cover is below 0.3 |
| partner bond | holds all 6 strands (the thick core); quality: +0.03 (1 - q) each week together under one roof, +0.15 (1 - q) per time-together session, decay 0.06 |
| thin bond | holds 2 shareable strands (care, affection, logistics, intimacy cycle); thick bond 3; quality +0.30 (1 - q) per visit to it, decay 0.05; visits rotate to the weakest bond |
| coordination | 0.2 x n_ext^1.7 units per week per partner (n_ext external bonds: 1 -> 0.2, 2 -> 0.65, 3 -> 1.3, 5 -> 3.1, 7 -> 5.6, of a 10-unit week) |
| bond shocks | 0.20 per bond-year, 6 to 20 weeks (rupture: that bond supplies nothing); the partner-bond rupture also adds 0.15 per week connection penalty; shocks use common random numbers across bond counts |

Everything above is ASSUMED. The synthesis's rules of thumb (50 to 70 percent reward, stop at 80 percent) came from an AI passage in the author's note and are not used. Sensitivity sweeps are reported for k_pay, antic_gain, hab_rate and coord exponent (secondary, descriptive).

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold)

To be run after slices 1 and 2 and before the confirmatory run, on seeds 900 to 902 and 12 pairings, only to estimate effect and spread for the power check. Its numbers and the resulting seed count go in Amendment 1, committed before the confirmatory run. If the pilot shows a mechanism is inert because of a bug, the bug is fixed and noted in an amendment; no parameter value above is changed after seeing outcomes.

## Power check (required)

`mar.stats.seeds_for_power(effect, sd, target=0.8, alpha=0.05, paired=True)` on the pilot's pairing-level effects and spreads, cross-checked with `seeds_for_margin`; recorded in Amendment 1. Seeds per pairing are what the helper returns, capped as above. Any prediction whose units chosen fall short is marked DESCRIPTIVE (no verdict wording). The number of pairings (57 controlled, 15 headline) is fixed by the cohort, not chosen.

## Predictions

Holm family (alpha 0.05, one-sided tests, 11 tests): LA1, LA2a, LA2b, LB1, LB2, LC1a, LC1b, LC2, LC3, H1, H2. "D" means difference of pairing means. "Share" rows use the exact binomial test of the stated null and the Clopper-Pearson 95% interval; "D" rows use a paired sign-flip permutation test on pairing means (exact when 15 pairings, 20000 draws otherwise) and a 95% percentile bootstrap clustered by pairing.

| ID | Quantity (synthesis source) | Unit | Threshold | Test |
|---|---|---|---|---|
| LA1 | (P1) share of pairings whose mean pleasure is higher when everyone rotates variants than when everyone repeats the best one, adaptation ON | pairing | share >= 0.70 | exact binomial, H0 share <= 0.70 |
| LA1c (descriptive, outside the family) | same share with adaptation OFF for repeat-beats-rotate | pairing | reported, expected > 0.50 | none |
| LA2a | (P3) D ritual minus ad hoc at equal dose (one forced untagged together session per week), adaptation OFF | pairing | D > +0.01 | permutation |
| LA2b | (P3) gap with adaptation ON minus gap with adaptation OFF | pairing | > 0 | permutation |
| LB1 | (P4) share of pairings with committed pleasure below uncommitted in weeks 0 to 25 (mutual 52-week stay forced vs none, both L-B ON) | pairing | share >= 0.60 | exact binomial, H0 share <= 0.60 |
| LB2 | (P4) share of pairings with committed above uncommitted in weeks 52 to 155 | pairing | share >= 0.60 | exact binomial, H0 share <= 0.60 |
| LC1a | (P5) D mean pleasure, 3 bonds (partner and 2 others) minus 1 bond (partner only), same time budget | pairing | D > 0 | permutation |
| LC1b | (P5) D share of partner-weeks in non-offsettable suffering, 1 bond minus 3 bonds | pairing | D > 0 | permutation |
| LC2 | (P5) over bond counts {1,2,3,4,5,6,8}: the mean-pleasure maximum is at 3, 4 or 5 bonds AND pleasure at 8 bonds is below the maximum | pairing | argmax in {3,4,5}; D (max minus 8 bonds) > 0 | permutation on the D clause |
| LC3 | (P5) shock loss (no-bond-shock minus bond-shock pleasure), 1 bond minus 3 bonds | pairing | > 0 | permutation |
| H1 | (headline, author's condition) D seed v2.2 minus imposed baseline, all levers ON, mean pleasure over the 15 hand-persona pairings | pairing | D > 0 | exact sign-flip permutation (2^15) |
| H2 | (P8) D v2.2 with the ritual lever ON minus v2.2 with it OFF, other levers ON, 15 hand pairings | pairing | D > +0.03 | exact sign-flip permutation |

Reported but not tested (descriptive): the break-even k_pay (the smallest value in {0, .02, .04, .06, .08, .10, .15, .20} at which weeks 52 to 155 committed exceeds uncommitted in at least 60 percent of pairings); lifetime cumulative pleasure difference for committed vs uncommitted; the headline repeated with levers OFF (the earlier -0.028, re-measured on these seeds); H1 for plain v2.2 vs the v2.2 ablations (A only, B only, C only); the three-way decomposition of the gap; sensitivity sweeps; per-lever pleasure by source. Effect sizes for every D: difference with CI and Cohen's dz.

Not predicted and not tested: P2, P6, P7, P9 (synthesis); P4b and the timescale-versus-behavior sub-claim; P5b (care-first ordering); the care-floor toggle exists in the config and is off.

## Verdict rule

A claim holds robustly iff its point estimate meets the threshold AND the 95% interval lies on the right side of it AND its Holm-adjusted p < 0.05. "Holds but CI crosses threshold" is weak support and is not cited as a hold. LC2 and LB (the crossover) are joint claims: both clauses must hold. The author's condition is met in this model, by the headline, iff H1 holds robustly; it is met with attribution iff H1 and H2 hold robustly. If H1 does not hold the report says the condition is not met by these levers, and by which cohort.

## Not testable by design

Flags-off identity (pinned fingerprints, `tests/test_levers_regression.py`); dose equality of the ritual and ad hoc arms (realized sessions per week reported, the arms must agree within 2 percent or the LA2 pairings with a gap are dropped and the drop reported); the instrument identity (lever terms add to the weekly pleasure exactly).

## Limits stated now

Modeled gloss: the lever payoffs are written into the model, so LA2, LB2 and LC1 are partly true by construction when a parameter is nonzero; what these runs can show is sizes, crossings, break-evens and what happens to the headline, not that the mechanisms exist in people. Scripted agents; one persona set; one parameter point per claim (plus sweeps); the ritual is a week-0 stub agreement in the negotiated runs, not a term inside the negotiation bundle (negotiation.py is not extended); L-C partner-bond quality is a modeled stock, not measured closeness; the headline compares 15 pairings, so its power is low for small effects.

## Amendments

[Dated. None yet.]
