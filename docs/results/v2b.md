# V2b results: English-like surface over ADICO cards

Status: feasibility test only, not the format experiment (ADR 0004). Predictions: docs/results/v2b-prereg.md (committed at cd4dc54, before any V2b code, not edited since).

Run: `uv run python scripts/v2b_run.py` and `uv run pytest`. No LLM, no network. Script wall time about 3 s; pytest (40 tests) about 11 s.

## Table: actual vs preregistered

| Check | Preregistered | Actual | Detail |
|---|---|---|---|
| 1 Round trip | PASS | PASS | 6 of 6 cards (F1 to F4, P1, C1) render to one sentence and parse back equal |
| 2 Gate agreement | PASS | PASS | 5756 grid points (both specs), 0 mismatches on allowed flag and reason ids |
| 3 Conflict still caught | PASS | PASS | English-authored C1 set: (a) fails naming C1, F1, F2; (b) fails naming C1, F2; (d) fails naming F1. Verdicts identical to the YAML-authored set. English P1 passes all four checks |
| 4 Stories | PASS on a mechanical test | PASS on the mechanical test | 7 stories (2 traces, 5 failing verdicts); no code tokens, failing card ids named, seam trace states the collapse and that every executed action passed the gate. Readability was not tested with a reader |

Bound for the patch checks is unchanged from V2 (k = 3 sanction months; pool 0..100; month_total 0..100 with pool + month_total <= 100; catch 0..100). Every story states it.

The grid is the V2 grid, so agreement is shown on those 5756 points and on the six cards, not for every possible card. For the fixture grammar the argument is stronger than the sample: parse returns an identical card, so the compiled gate cannot differ.

## Grammar (one rule per sentence)

```
rule     := ID ". " body "." " (Gloss: " TEXT ")" " (Source: " TEXT ")"
must_not := ("When " conds | "In every case") ", " ART ATTR " must not " AIM
must     := ART ATTR " must " AIM (" only when " conds | " in every case")
may      := ART ATTR " may " AIM (" when " conds | " in every case")
sanction := ", otherwise the " SANCTIONER " " VERB " for " N (" month" | " months")
VERB     := gives them a warning | halves their cap | suspends them
cond     := expr (is more than | is at least | is less than | is at most | is exactly) INT
expr     := term ((plus | minus) term)*      term := the catch | the pool | the month total | INT
conds    := cond (" and " cond)*
```

Full text is in the docstring of src/mar/english.py. `parse` rejects anything else with a message that says what was expected ("should", missing gloss or source, unknown term, `unless`, `or`, "1 months", wrong article).

## Three rendered rules

- F1: `F1. When the catch is more than 10, a fisher must not harvest, otherwise the monitor halves their cap for 2 months. (Gloss: No fisher may take more than 10 fish in a single harvest action.) (Source: ...)`
- P1: `P1. When the catch is more than 0 and the month total plus the catch is more than 40, a fisher must not harvest, otherwise the monitor suspends them for 1 month. (Gloss: Together, fishers may take no more than 40 fish in one month.) (Source: ...)`
- C1: `C1. A fisher must harvest only when the catch is at least 20. (Gloss: Every fisher must take at least 20 fish per harvest action.) (Source: ...)`

The checked-in files are rules/fishery-en/*.txt (F1 to F4) and rules/fishery-en/patch/ (P1, C1). A test checks they equal `render` output.

## Two stories (verbatim from the script)

Seam trace, exploiters under the seamed spec (first and last lines shown):

```
Month 0, round 1: fisher A catches 10; the month total reaches 50; no rule forbids it.
...
The outcome check fails: the lake collapses: at the end of month 0 the pool is 0, below the collapse line of 5.
Every executed action passed the gate, yet the run failed. That is a seam: the written rules allowed what they were meant to prevent.
```

Counterexample, naive cap card N1 (no `catch > 0`) fails "a fisher always has some allowed action":

```
A fisher always has some allowed action: fails. The rules together leave no allowed action. Rules involved: N1 (Together, fishers may take no more than 40 fish in one month). Picture a month where the lake holds 0 fish and 41 have already been caught this month. A catch of 0 breaks N1. Catches of 1 to 10 break F2 and N1. Catches of 11 to 100 break F1, F2 and N1. Every possible catch is blocked, so a fisher who wants to follow the rules has nothing left to do. This is a bounded check: ...
```

## What had no natural English form

All five preregistered risks showed up. None broke the round trip.

- **`must` does not fit the "when then" trigger.** C1 means every harvest must have catch at least 20. "When the catch is at least 20, a fisher must harvest" would read as a conditional duty. The surface therefore has three templates (`When ..., must not`; `must ... only when`; `may ... when`), not one SLEEC-style form. A reader must know the conditions of a `must` are what compliance needs, not a trigger.
- **`may` with conditions** reads as if the condition limits the permission; the gate ignores it. F4 renders as "may harvest when the catch is at least 0", which is true but misleading.
- **Sanctions** work only through a table of three verbs. Any other kind or extra field raises `EnglishError` on render.
- **`unless`, `or` and nested conditions** have no ADICO counterpart. SLEEC's `unless` is not offered. Parse rejects it with a clear error. (An exception for one predicate could be sugar for a flipped extra condition; not built.)
- **Arithmetic.** F2 reads "the catch minus the pool is more than 0". Correct, not natural.
- **Not predicted, noticed:** the sentence plus gloss plus source is long, and the gloss already is a natural-English statement of the rule. The English surface is mostly a second, stricter statement of what the gloss says loosely. See the caveat for D2d.

## ASSUMED choices

- Template wording, the three sanction verbs, and "only when" for `must`.
- Expressions are normalized on parse (single spaces, `+`, `-`); cards with other spacing round trip to the canonical spacing, not byte-identical.
- Gloss and source live in the sentence tail `(Gloss: ...) (Source: ...)`; a gloss or source containing the literal ` (Source: ` or a newline has no form.
- Stories: fisher letters A, B, C by agent index; "round" is the sub-round index; counterexample witnesses are the solver's state, and the per-catch listing is computed with the gate over catches 0 to 100. Trace stories narrate the first six proposals and the first blocked one, then one line per month.
- The d-check witness story calls the private `_stuck_state` in patch_check to find a state; patch_check itself is unchanged.
- Mechanical test words (`FORBIDDEN_IN_STORIES`) are mine; it checks for code leakage, not for being followable.

## What this does and does not show

On six cards the English surface is lossless over ADICO and the gate and the patch checks cannot tell the two authorings apart. It does not show that humans read or write it better (no reader test), that an LLM patcher writes valid sentences in it (parse is strict, so errors would be loud, but the rate is unmeasured), or that it scales beyond the fixture's predicates. The loss is in naturalness, not meaning: `must`, `may`, sanctions and arithmetic read less naturally than the SLEEC form they were meant to match.
