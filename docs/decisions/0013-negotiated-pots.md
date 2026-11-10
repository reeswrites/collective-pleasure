# 0013. Pot terms are negotiated, then proof-checked, then lived

Status: accepted (2026-11-10)

## Context

Seed v2 (docs/seeds/author-household-norms-2026-11-10.md) put "everything shared always" into a shared pot, and an agent added rule R3b ("taking the other's share of the pot is not use for shared needs") to make the pot safe. At read-back the author rejected that reading (experiments/changes.jsonl, second "not what I meant"). The author's words: "i think you have to negotiate shared pots with multiple agents or creating rules for it". The same seed already says exit conditions are "negotiated before" and that "no one owes anyone anything day to day except for what they have negotiated", and the stub that stood in for negotiation (a fixed function of the persona, ADR 0008's negotiation phase not built) was found in seed v2 to negotiate nothing.

## Decision

1. **The seed does not impose pot terms.** R3b is removed from the seed v2 variants (the card stays in git history, commit 58b630a); the remaining cards are marked v2.1 in their sources. The stub exit terms R8b and R8c stay in the card files only for runs with no negotiation; a negotiation replaces them with the negotiated exit term.
2. **Everyone who shares a pot negotiates its terms**, two or more members (a household plus Friend C is a 3-member table). A finite terms menu (src/mar/negotiation.py): contribution (none, fixed, proportional), use (shared needs only, any use, per-member caps), taking another's share (allowed, forbidden, allowed with repayment), change rule (unanimous, any member proposes and others accept, frozen), exit terms (equal split, contribution-proportional, forfeit), and the optional commitments of seed v2 (stay for 52 weeks, request acceptance) where the base rules permit them.
3. **Protocol.** Alternating offers generalized to N members with a deadline of 12 proposals; members propose in a seeded order; a member accepts a bundle only if its persona-based value of living under it beats its outside option (what it gets by not forming or joining the pot); no agreement means no pot and members keep their own holdings. The evaluation and the outside option are closed-form proxies of the persona weights (ASSUMED; documented in the prereg; not validated against rollouts).
4. **Agreement becomes rule cards, and the proof checks run before living.** The agreed bundle compiles to ADICO cards with a plain gloss and the source "negotiated, week 0, members X,Y,Z". The five household checks (no conflict, no deadlock, bounded sanctions, repair path, exit within k) plus one negotiation check (a frozen pot with no exit is unrepairable) run at k = 3 months; an agreement that fails or is not shown to pass is rejected, logged with its reasons, and the members ban the failing combination and carry on. This is the same proof filter used for hand-written rules, applied to real negotiated deals.
5. **The weekly world takes the deal at week 0.** `WeeklyWorld(..., deal=...)` replaces the commitment stub; with no pot the partners start with their own holdings (55 private money, nothing pooled). `deal=None` is the old behaviour, bit for bit (checked: the seed v2 reference replicates its published numbers). 3-member agreements are negotiated and proof-checked but not lived (limit).
6. **Breach is reported, not changed.** The breach rule (a bound partner breaks a commitment at non-offsettable load 0.2) is unchanged. A breach-forfeit sweep (0 to 1.0) exists as an exploratory option (`breach_forfeit`, default 1.0) and supports no preregistered claim.

## Consequences

- The author's correction is built in: no agent decides what the pot's rules are; the people at the table do, and the proof filter, not the agent, guards against traps.
- What is learned is conditional on the proxy. In docs/results/negotiation.md the closed-form outside option almost never bound (0.971 agreement), so "accept only if better than the outside option" did not protect a weak partner: Free-rider households agreed taking-allowed in 34 of 48 negotiations and the partner's non-offsettable level rose from 0.104 to 0.186. Four of six preregistered predictions failed (3 to 6); two passed (1, 2). The next step is to calibrate the proxy against short rollouts, not to tune constants after the fact.
- The proof filter caught one kind of trap (a forfeit exit, 114 of 513 negotiations) and every rejection was recoverable; the other checks are exercised only by planted traps in tests/test_negotiation.py.
- Old results that used the imposed R3b (docs/results/household-seed-v2.md) are reproducible only from commit 58b630a or through scripts/household_run.py --negotiate, which restores the card from git for its reference runs.

## Alternatives considered

- Keep R3b and ask the author again: the author has answered; the answer is negotiation.
- Negotiate by short rollouts of each bundle: up to 2916 bundles per member per round, too slow for 57 pairings x 3 seeds x 3 variants; recorded as the calibration to do.
- Impose a default pot rule and let members opt out: that is the rejected reading with an exit.
- Let a negotiation exclude a member of a 3-member table: not in v1 (a 3-member table forms a 3-member pot or none).
