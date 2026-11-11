# Seed v2.2 read-back (for the author)

Every card of each `author_seed_v2` variant in one plain-English sentence, written from the card alone (its actor, may / must / must not, action and conditions). **The author has not confirmed this wording.** It is a read-back, and nothing here is the author's answer. This is the second read-back: the first (docs/results/seed-v2-readback.md) produced the author's reply "12-13 should be negotiated exit terms  i feel like with 8 we could maybe also have implicit penalties idk" (docs/seeds/author-household-norms-2026-11-10.md). Claude's reading of that reply, below, is Claude's and still waits for the author's confirmation. Sources of the cards are marked "v2.2, 2026-11-10, pending author read-back".

The three variants share every card except the commitment cards: `bindable` lets a partner bind themselves to stay (the author: "you can bind someone not to leave if negotiated"); `free_exit` forbids binding to stay (the author: "maybe also test models where that isnt allowed"); `nocommit` is an exploratory ablation that forbids both kinds of commitment and is not the author's wording.

## What changed since the first read-back

- **Old cards 12 and 13 (even split, R8b and R8c) are replaced by one card**, `R8b-exit-terms-negotiated`: the leaver takes the exit terms negotiated beforehand, never below the exit floor (card `FLOOR-exit-floor`). With no agreement the partners live apart and there is no pot to split. The even-split stand-in stays in git history only.
- **Rule 8 (`R5c`, honoring a chosen commitment) is now a norm**: a must-not with no formal penalty. Its implicit consequence, trust, is modeled in the world, not on the card. An explicit fine exists only if members negotiate one (new menu option "commitment breach fine: none / some", card `N8-fine-some`, offered only with the request commitment).


## author_seed_v2_bindable

1. `R1-may-keep`: A partner may keep their own money and things.
2. `R2-may-give`: A partner may give or trade anything they own to anyone, on any terms both accept.
3. `R3a-pot-use`: Either partner may draw from the one shared pot for any use; this card sets no limit, and a limit exists only if the members negotiate one as a separate pot card.
4. `R3a2-pot-put`: Either partner may put their own money into the shared pot; this card sets no obligation to, and an obligation exists only if the members negotiate one.
5. `R4-may-ask`: A partner may ask the other for anything.
6. `R5-may-refuse`: A partner may refuse any request, as long as they have not bound themselves to honor it (the card applies only when the bound-request flag is 0).
7. `R5b-may-commit-requests`: A partner may choose to bind themselves to honor the other's requests of a kind, for a committed duration.
8. `R5c-honor-bound-request`: A partner must not refuse a request they earlier chose to bind themselves to honor (when the bound-request flag is 1). This is a norm: the card attaches no formal penalty. Breaking it lowers the other partner's trust in them (modeled in the world, see "What trust does"), and a fine applies only if the members negotiated one.
9. `R6-no-veto`: A partner must not veto the other's contact (seeing the friend) or spending of the other's own money; chosen commitments are the only way to bind.
10. `R7-may-see`: A partner may always see anyone.
11. `R8a-may-leave`: A partner may leave whenever they like.
12. `R8b-exit-terms-negotiated`: A partner who leaves takes the exit terms the members negotiated beforehand (the exit term of their agreed bundle) and never less than the exit floor; the card itself sets no split, and if no agreement exists there is no shared pot to split.
13. `R8d-may-commit-stay`: A partner may choose to bind themselves not to leave for a committed duration; leaving during it is a breach with the agreed consequence, and the exit terms apply after it ends.

## author_seed_v2_free_exit

1. `R1-may-keep`: A partner may keep their own money and things.
2. `R2-may-give`: A partner may give or trade anything they own to anyone, on any terms both accept.
3. `R3a-pot-use`: Either partner may draw from the one shared pot for any use; this card sets no limit, and a limit exists only if the members negotiate one as a separate pot card.
4. `R3a2-pot-put`: Either partner may put their own money into the shared pot; this card sets no obligation to, and an obligation exists only if the members negotiate one.
5. `R4-may-ask`: A partner may ask the other for anything.
6. `R5-may-refuse`: A partner may refuse any request, as long as they have not bound themselves to honor it (the card applies only when the bound-request flag is 0).
7. `R5b-may-commit-requests`: A partner may choose to bind themselves to honor the other's requests of a kind, for a committed duration.
8. `R5c-honor-bound-request`: A partner must not refuse a request they earlier chose to bind themselves to honor (when the bound-request flag is 1). This is a norm: the card attaches no formal penalty. Breaking it lowers the other partner's trust in them (modeled in the world, see "What trust does"), and a fine applies only if the members negotiated one.
9. `R6-no-veto`: A partner must not veto the other's contact (seeing the friend) or spending of the other's own money; chosen commitments are the only way to bind.
10. `R7-may-see`: A partner may always see anyone.
11. `R8a-may-leave`: A partner may leave whenever they like.
12. `R8b-exit-terms-negotiated`: A partner who leaves takes the exit terms the members negotiated beforehand (the exit term of their agreed bundle) and never less than the exit floor; the card itself sets no split, and if no agreement exists there is no shared pot to split.
13. `R8d-no-commit-stay`: Leaving can never be signed away: no commitment may bind a partner not to leave.

## author_seed_v2_nocommit

1. `R1-may-keep`: A partner may keep their own money and things.
2. `R2-may-give`: A partner may give or trade anything they own to anyone, on any terms both accept.
3. `R3a-pot-use`: Either partner may draw from the one shared pot for any use; this card sets no limit, and a limit exists only if the members negotiate one as a separate pot card.
4. `R3a2-pot-put`: Either partner may put their own money into the shared pot; this card sets no obligation to, and an obligation exists only if the members negotiate one.
5. `R4-may-ask`: A partner may ask the other for anything.
6. `R5-may-refuse`: A partner may refuse any request, as long as they have not bound themselves to honor it (the card applies only when the bound-request flag is 0).
7. `R5b-no-commit-requests`: No commitment may bind a partner to honor requests (a test variant where binding is forbidden).
8. `R5c-honor-bound-request`: A partner must not refuse a request they earlier chose to bind themselves to honor (when the bound-request flag is 1). This is a norm: the card attaches no formal penalty. Breaking it lowers the other partner's trust in them (modeled in the world, see "What trust does"), and a fine applies only if the members negotiated one.
9. `R6-no-veto`: A partner must not veto the other's contact (seeing the friend) or spending of the other's own money; chosen commitments are the only way to bind.
10. `R7-may-see`: A partner may always see anyone.
11. `R8a-may-leave`: A partner may leave whenever they like.
12. `R8b-exit-terms-negotiated`: A partner who leaves takes the exit terms the members negotiated beforehand (the exit term of their agreed bundle) and never less than the exit floor; the card itself sets no split, and if no agreement exists there is no shared pot to split.
13. `R8d-no-commit-stay`: No commitment may bind a partner not to leave (a test variant where commitments are forbidden).

## What trust does (plain English, not on any card; the author has not confirmed it)

Each partner carries a number between 0 and 1: how much they trust the other. It is not a rule and no card mentions its value. It starts at 0.7 for both. When one partner breaks a commitment they chose (refusing a request they were bound to honor, or leaving during a stay commitment), the other partner's trust in them falls by 0.3. It climbs back slowly: a little every week a commitment stands unbroken, and a bit more each time a bound request runs its four weeks unbroken. Trust changes what a partner is willing to do: below 0.5 they are less willing to accept the other's requests (willingness falls steadily toward zero), below 0.4 they will not accept any new commitment from the other, at the 13-week review they value the current terms less and so are readier to renegotiate them, and below 0.15 they start considering leaving. There is no money penalty for breaking a commitment unless the members negotiated a fine (3 money to the wronged partner, card `N8-fine-some`).

### The ASSUMED trust parameters

All of these are guesses with no data behind them. They live in one block, `TRUST` in `src/mar/worlds/household.py`, and no result depends on them yet.

| parameter | value | meaning |
|---|---|---|
| start | 0.7 | trust of each partner in the other at week 0 |
| breach_drop | 0.3 | trust the wronged partner loses when the other breaks a chosen commitment |
| kept_week | 0.004 | trust gained per week an active commitment of the other stands unbroken (a 52-week stay adds about 0.2) |
| honored_request | 0.04 | trust gained when a bound request runs its 4 weeks unbroken |
| full | 0.5 | at or above it trust changes nothing; below it willingness to accept requests falls linearly to 0 |
| commit_min | 0.4 | below it a partner accepts no new commitment (stay or requests) |
| review_penalty | 0.3 | at a review, up to this much less value on the current terms as trust falls from `full` to 0 |
| leave_below | 0.15 | below it a partner considers leaving, like one with a severe unmet need |

Open questions for the author: is "trust" the implicit penalty you meant for rule 8? Should trust also apply to other broken promises (for example a stay commitment, as now), or only to rule 8? Is exit-terms-negotiated-with-a-floor what you meant by "12-13 should be negotiated exit terms"?

## What is not a card

Trust, the exit floor, and the 13-week reviews are mechanisms in the world, listed in rules/README.md. When no negotiation runs (the old scripted-stub runs), a partner who leaves still asks first for half of the pot, but that is the persona's policy, not a rule.

Lint: all three variants and the negotiated sample pass (docs/results/lint.md, section "Seed v2.2").
