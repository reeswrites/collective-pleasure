# Superseded household cards (2026-11-10)

Kept unchanged so the runs made under them can be reproduced and read; do not use them for new work.

| Card | Where | Why superseded |
| --- | --- | --- |
| S4-may-refuse | `author_seed`, `author_seed_nocontrol` | Seed v1's reading of "request is never about control" as a `may refuse` permission. A permission binds nothing, so it did not say what the author meant. The author flagged it at the seed read-back (experiments/changes.jsonl, first entry). Replaced by R4, R5, R6 in `author_seed_v2_*`. |
| S5-may-share | `author_seed`, `author_seed_nocontrol` | Seed v1's "sharing is open, never required", the reading the author rejected ("everything shared always" is the shared pot). Replaced by R3a (and R3a2) after the author's choice `1` on the pot (docs/seeds/author-household-norms-2026-11-10.md). |
| `fair_default` bundle with fixed contributions, needs-only use, taking forbidden | `negotiation.FAIR_DEFAULT_V1` | An imposed reading of the pot (the rejected R3b in another form). The fair default is now one shared pot, open use, no required contributions, equal exit split, no commitments, unanimous change. |
| Per-person pooled shares (the weekly world before the pot fix) | git history, commits before "Slice 1: the household pot is one shared balance" | The pot is one balance both may draw from. Results before that commit used the old world; see the correction sections in docs/results/household-seed-v2.md and the negotiation results. |
| R3a's old gloss ("either may use it for shared needs; neither may block the other's use") | `author_seed_v2_*` before the pot fix | Claude's restriction, withdrawn. |
| R6's old gloss ("contact, money or time, except through a commitment the other chose") | `author_seed_v2_*` before 2026-11-10 | Added "time" (the world cannot veto time) and an exception no card condition encodes. |

The cards W3, W3s (take_shared) carry a post-fix note in their sources: they now restrict drawing from the one shared pot.
