# 0002. ADICO as authoring layer

Status: accepted, conditional on the kill criterion (2026-11-10)

## Context

ADICO (Attribute, Deontic, aIm, Conditions, Or else) is the statement format of Institutional Grammar, borrowed from Ostrom's work on human institutions. This project's subject is rule systems for AI agent groups; human institutions are a source of hypotheses only.

## Decision

D2: Use ADICO as the human-readable authoring and comparison layer. It is not a logic; it compiles to a labeled transition system (ADR 0001). It gives: the split between rules, norms (no sanction) and shared strategies (no must/may); explicit sanction and sanctioner; levels of rules about changing rules; comparability with human institutions already coded in the grammar; rule cards readable by non-programmers.

**Kill criterion:** if ADICO-derived arms produce no difference from Cedar or LTL-only arms on any preregistered measure, drop ADICO and use the simpler format.

## Consequences

- Every rule carries an ADICO form, a plain-English gloss and a source.
- The compile step ADICO -> LTS is a trusted translation and must be cross-checked (milestone 2).
- Experiments need Cedar or LTL-only comparison arms so the kill criterion can be evaluated.
