# V2b preregistration (committed before any V2b code runs)

Status: feasibility test, not the format experiment (ADR 0004). Nothing here is a research result. No LLM, no network. V2b asks one question: can an English-like surface in the style of SLEEC rules ("when <condition> then <obligation or prohibition> unless <exception>", with "otherwise <sanction>" for ADICO's or-else) sit on top of the existing ADICO cards without losing meaning?

## Setup (fixed now)

- Cards under test: the V2 seamed spec F1 to F4 (rules/fishery/), the scripted patch P1 (from `propose_patch` on the exploiter trace), and the conflicting patch C1.
- Surface: a small strict controlled grammar, `render(card) -> str` and `parse(str) -> card` in src/mar/english.py. Cards and the gate are unchanged. The English surface is a view of the card, not a new semantics.
- Grid for prediction 2: the full V2 grid (13 x 13 x 17 states and catches, plus the five fixed points) over both the seamed and the patched spec, as in scripts/v2_run.py (5756 points).
- Stories (prediction 4): the seam trace (exploiters under the seamed spec, seed 0), the exploiter trace under seamed plus P1, and every failing verdict from the patch checks on seamed plus C1 and on seamed plus the naive cap card (the V2 first-run failure, without `catch > 0`).

## Predictions

1. **Round trip: PASS.** Every V2 card (F1 to F4, P1, C1) renders to one English-like sentence and `parse(render(card))` equals the card exactly (all eight fields, conditions and sanction included). 6 of 6 cards.
2. **Gate agreement: PASS.** The gate built from parsed-back cards gives the same allowed flag and the same reason ids as the gate built from the original cards on every point of the full V2 grid: 0 mismatches, for both specs.
3. **Conflict still caught: PASS.** The conflicting rule set authored in the English surface (F1 to F4 plus C1 as sentences, parsed) fails the patch checks with the same card ids as the YAML-authored set: check (a) fails naming C1, F1 and F2, check (b) fails. The English-authored P1 passes all four checks.
4. **Stories: PASS on a mechanical test only.** Every counterexample and the seam trace renders to a plain-English story. Mechanical test: no code identifiers (`month_total`, `pool_before`, braces, `==`), every failing card id in the verdict is named with its gloss, and the trace story states the oracle finding and that every executed action passed the gate. Whether a reader can follow it "without the code" is a judgment; V2b does not run a fresh-reader test, so this prediction cannot confirm it. A fresh-reader test belongs to the format run (ADR 0004 measure 5).

## Honest risk: features with no natural English form

Expected before coding, in rough order of confidence:

- **`must` reads backwards in the SLEEC trigger form.** In this card semantics `must` with conditions means the action is a violation unless all conditions hold. "When the catch is at least 20, a fisher must harvest" would read as a conditional duty and misstate C1. I expect `must` and `may` to need their own template ("only when", "when") instead of the "when ... then" template, so the surface is not uniform. This is the most likely place for meaning to leak.
- **`may` with conditions.** The gate ignores a `may` card, but "a fisher may harvest when the catch is at least 0" suggests the condition restricts the permission. Round trip will pass; the English will mislead a reader.
- **Sanctioner and sanction kind.** "Otherwise the monitor halves their cap for 2 months" works only through a fixed three-verb table I invent (warn, cap_halve, suspend). Any other kind or a sanction with extra fields has no form.
- **Conditions are a bare conjunction.** SLEEC "unless" (exceptions), "or", and nested conditions have no ADICO counterpart in these cards. I expect `unless` to be unrepresentable except as a negated extra condition for one predicate, and I will not add it.
- **Arithmetic expressions.** "The catch minus the pool is more than 0" is correct but not natural; F2 is the card I expect to read worst.

If more than the listed features fail to round trip, or any of these leaks meaning in a way a test can show, it is reported in docs/results/v2b.md as a result.

Overall wall time under 60 seconds for the V2b script plus tests. If any prediction fails, it stays failed here; the result is reported in docs/results/v2b.md, not edited into this file.
