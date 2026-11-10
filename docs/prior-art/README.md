# Prior-art checks: index and confidence

Three checks, all on 2026-11-10. All are search-snippet and abstract-level reviews. Absences are search results, not proofs. Re-run before any write-up. This area produces about one relevant paper a month.

| File | What it checked | How it was read | Confidence in an absence |
|---|---|---|---|
| 2026-11-10.md | Is the full pipeline (rules, solver gate, LLM agents, loop) already published? | Abstracts and snippets. Only part of arXiv 2601.11369 was read in full text | About 70 percent that the original pipeline is unpublished. Its parts are mostly taken |
| 2026-11-10-v1-convergence.md | Does any work measure convergence of a rule-refinement loop for LLM agents? | Snippets and abstracts. Only Rehm (2609.22600) was read in part. RvB through an AI overview | Full combination about 70 percent unpublished, per-round seam curve about 80, de jure versus de facto diff about 85. "LLM patches rules, solver rejects conflicts" alone about 35 percent (VEPA, AutoCedar) |
| 2026-11-10-v2-framing.md | Capability thresholds, empowerment, delegates, relationship models, bisimulation, manipulation | Search snippets and summaries only. No hit was read in full | Not rated. Weak evidence of absence |

## What this does and does not support

- We found no study of the per-round rate of new gate-passing seams under an independent oracle. Partial per-round curves exist (RvB, Kumar et al.).
- VEPA patches its rules with a verifier, so it is not a fixed-spec paper. It is the closest work on mechanism.
- No query covered loop (b), eliciting or formalizing a person's intent through conversation. We make no originality claim for it.
- Items still to read in full: VEPA's longer-horizon figure, RvB, and the "ATL* not connected to LLM conformance" line from Albayaydh and Zhao (seen only in a snippet).
