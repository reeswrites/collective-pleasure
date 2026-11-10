# 0001. New repo and stack

Status: accepted (2026-11-10)

## Context

philosophy-engine has an ADICO schema and a reference engine, but its reference semantics are limited to tiny rule systems and its checks are bounded to depth k. Its repo rules also pause work pending a "worth-it" slice, and its ADR 0011 forbids adversarial search, which robustness testing here needs. Separately, bisimulation and model checking are mature problems with existing tools.

## Decision

- D1: Start a new repo. philosophy-engine is an input (ADICO schema; reference engine as a translation cross-check), not the core.
- D3: The shared semantic core is labeled transition systems. mCRL2 is the candidate tool (transition systems, reduction and comparison up to bisimulation equivalences, modal mu-calculus model checking). Alternatives to evaluate: nuXmv, TLA+/Apalache, InstAL. We do not reimplement bisimulation or model checking.

## Consequences

- No dependency on philosophy-engine's governance; cross-checks are one-way comparisons.
- We take on a tool dependency (mCRL2 or alternative) and must evaluate fit for sanctions and obligations.
- Stack choice stays revisable until milestone 3 shows a working invariant proof and counterexample.
