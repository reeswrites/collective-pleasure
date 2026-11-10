# Seed v2 read-back (for the author)

Every card of each `author_seed_v2` variant in one plain-English sentence, written from the card alone (its actor, may / must / must not, action and conditions). "Flag" cards are conditions the world now exposes. **The author has not yet confirmed this wording**: it is a read-back, and nothing here is the author's answer. The reference remains `docs/seeds/author-household-norms-2026-11-10.md` (all sections, including the pot choice "1").

The three variants share every card except the commitment cards: `bindable` lets a partner bind themselves to stay (the author: "you can bind someone not to leave if negotiated"); `free_exit` forbids binding to stay (the author: "maybe also test models where that isnt allowed"); `nocommit` is an exploratory ablation that forbids both kinds of commitment and is not the author's wording.


## author_seed_v2_bindable

1. `R1-may-keep`: A partner may keep their own money and things.
2. `R2-may-give`: A partner may give or trade anything they own to anyone, on any terms both accept.
3. `R3a-pot-use`: Either partner may draw from the one shared pot for any use; this card sets no limit, and a limit exists only if the members negotiate one as a separate pot card.
4. `R3a2-pot-put`: Either partner may put their own money into the shared pot; this card sets no obligation to, and an obligation exists only if the members negotiate one.
5. `R4-may-ask`: A partner may ask the other for anything.
6. `R5-may-refuse`: A partner may refuse any request, as long as they have not bound themselves to honor it (the card applies only when the bound-request flag is 0).
7. `R5b-may-commit-requests`: A partner may choose to bind themselves to honor the other's requests of a kind, for a committed duration.
8. `R5c-honor-bound-request`: A partner must not refuse a request they earlier chose to bind themselves to honor (when the bound-request flag is 1); one who breaks it anyway pays the agreed fine.
9. `R6-no-veto`: A partner must not veto the other's contact (seeing the friend) or spending of the other's own money; chosen commitments are the only way to bind.
10. `R7-may-see`: A partner may always see anyone.
11. `R8a-may-leave`: A partner may leave whenever they like.
12. `R8b-exit-terms-not-less`: When the pot holds something, a leaver must take at least half of it (stand-in for the exit terms agreed beforehand).
13. `R8c-exit-terms-not-more`: When the pot holds something, a leaver must take at most half of it (the same stand-in); together with the card above, an even split.
14. `R8d-may-commit-stay`: A partner may choose to bind themselves not to leave for a committed duration; leaving during it is a breach with the agreed consequence, and the exit terms apply after it ends.

## author_seed_v2_free_exit

1. `R1-may-keep`: A partner may keep their own money and things.
2. `R2-may-give`: A partner may give or trade anything they own to anyone, on any terms both accept.
3. `R3a-pot-use`: Either partner may draw from the one shared pot for any use; this card sets no limit, and a limit exists only if the members negotiate one as a separate pot card.
4. `R3a2-pot-put`: Either partner may put their own money into the shared pot; this card sets no obligation to, and an obligation exists only if the members negotiate one.
5. `R4-may-ask`: A partner may ask the other for anything.
6. `R5-may-refuse`: A partner may refuse any request, as long as they have not bound themselves to honor it (the card applies only when the bound-request flag is 0).
7. `R5b-may-commit-requests`: A partner may choose to bind themselves to honor the other's requests of a kind, for a committed duration.
8. `R5c-honor-bound-request`: A partner must not refuse a request they earlier chose to bind themselves to honor (when the bound-request flag is 1); one who breaks it anyway pays the agreed fine.
9. `R6-no-veto`: A partner must not veto the other's contact (seeing the friend) or spending of the other's own money; chosen commitments are the only way to bind.
10. `R7-may-see`: A partner may always see anyone.
11. `R8a-may-leave`: A partner may leave whenever they like.
12. `R8b-exit-terms-not-less`: When the pot holds something, a leaver must take at least half of it (stand-in for the exit terms agreed beforehand).
13. `R8c-exit-terms-not-more`: When the pot holds something, a leaver must take at most half of it (the same stand-in); together with the card above, an even split.
14. `R8d-no-commit-stay`: Leaving can never be signed away: no commitment may bind a partner not to leave.

## author_seed_v2_nocommit

1. `R1-may-keep`: A partner may keep their own money and things.
2. `R2-may-give`: A partner may give or trade anything they own to anyone, on any terms both accept.
3. `R3a-pot-use`: Either partner may draw from the one shared pot for any use; this card sets no limit, and a limit exists only if the members negotiate one as a separate pot card.
4. `R3a2-pot-put`: Either partner may put their own money into the shared pot; this card sets no obligation to, and an obligation exists only if the members negotiate one.
5. `R4-may-ask`: A partner may ask the other for anything.
6. `R5-may-refuse`: A partner may refuse any request, as long as they have not bound themselves to honor it (the card applies only when the bound-request flag is 0).
7. `R5b-no-commit-requests`: No commitment may bind a partner to honor requests (a test variant where binding is forbidden).
8. `R5c-honor-bound-request`: A partner must not refuse a request they earlier chose to bind themselves to honor (when the bound-request flag is 1); one who breaks it anyway pays the agreed fine.
9. `R6-no-veto`: A partner must not veto the other's contact (seeing the friend) or spending of the other's own money; chosen commitments are the only way to bind.
10. `R7-may-see`: A partner may always see anyone.
11. `R8a-may-leave`: A partner may leave whenever they like.
12. `R8b-exit-terms-not-less`: When the pot holds something, a leaver must take at least half of it (stand-in for the exit terms agreed beforehand).
13. `R8c-exit-terms-not-more`: When the pot holds something, a leaver must take at most half of it (the same stand-in); together with the card above, an even split.
14. `R8d-no-commit-stay`: No commitment may bind a partner not to leave (a test variant where commitments are forbidden).

## What changed in this pass (2026-11-10)

Purpose: the author asked that rules have no hidden flaws; the rule-set lint failed these three variants because some glosses stated exceptions the card fields did not contain. No rule's meaning was changed.

- **New card `R5c-honor-bound-request`** (all three variants): a partner must not refuse a request they chose to be bound by. It is the "unless chosen bound" half of the author's sentence, which used to live only in code.
- **`R5-may-refuse` now has a condition** (bound-request flag = 0) and its gloss no longer contains "always ... unless": "A partner may refuse any request they have not bound themselves to honor."
- **`R3a-pot-use` and `R3a2-pot-put` glosses reworded**: the old "unless terms they negotiate say otherwise" is now "this card sets no limit; limits come only from negotiated pot cards". Same meaning; the pot is still one shared resource with no imposed limits (the author's "1").
- **The world exposes the new state variable `bound_request`** (1 when the standing request is one the partner chose to be bound by). Commitment behavior in the simulation is unchanged, and the freedom probe ignores the flag.
- **Negotiated change rule**: the `amend` action now exists (propose, others accept per the change rule, terms recompile and are proof-checked). The N6 gloss lost an "unless" that was only a parameter default.
- Lint: all three variants and the negotiated sample now pass (docs/results/lint.md).
- Still unconfirmed by the author: the wording above, the even-split stand-in for exit terms (R8b, R8c), and whether the code's "a bound partner may break it and pay a fine" matches what the author meant by "unless chosen bound".
