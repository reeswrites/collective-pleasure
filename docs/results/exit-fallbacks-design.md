# Exit no-deal fallbacks: design note

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Status: design for slice 1, which covers the money pot only. Code: `src/mar/exit_fallback.py`, with hooks in `src/mar/worlds/household.py` (PyGate, carry_out, the F3 contest, the F5 prenup) and `src/mar/stay_test.py` (`exit_cost`, the bar lens). Tests: `tests/test_exit_fallback.py`. Preregistration: [exit-fallbacks-prereg.md](exit-fallbacks-prereg.md). Results: [exit-fallbacks.md](exit-fallbacks.md). This note replaces the earlier "renegotiable half-cap default" design, which only ever existed as uncommitted work.

## Why this exists

In household evolution run 2, the imposed exit cap E1-at-most-half ("a partner who leaves may take at most half of the pooled assets") was in 13 of 16 elites and added about +3.0 bits of liberty over the author's seed ([household-evolve-2.md](household-evolve-2.md)). The author first made the cap a renegotiable default (quote "1", commit 089803c). Then they revised it:

- "idk if it makes sense to say it as half but also that no one is ever entitled to anything it should be negotiated" (commit 43412d0). Exits are often about physical assets, not only money.
- "i think it depends on what you put in and what you value yeah not entitlement and not just what you brought or hold but yeah we might have to test diff approaches for outcomes bc idk" (commit dea6b8c).
- On a prenup arm: "yes and yes", and they are "very pro pre nup".

So the question is no longer which cap to use. It is what happens at exit when the pair has not agreed, with several answers tested side by side.

## The switch

`mar.exit_fallback.use_exit_fallback(arm)` takes one of six arms. It is off by default, and off is the same as F0. Negotiated exit terms (an N5 card from `negotiation.compile_bundle`) are left as they are: a pair with its own exit term never gets a fallback.

| Arm | At exit, with no agreed exit term | Where it lives |
|---|---|---|
| F0 current | the rule set's own cards as written; with no cap, a leaver may claim up to the whole pot | nothing changes (the reproduction arm) |
| F1 half cap | a leaver may claim at most half the pot (E1 as a default for every pair) | a gate card |
| F2 keep what you brought | a leaver carries their share of the pot in proportion to what they put **into the pot** | `carry_out` settles; the claim does not matter |
| F3 contested and costly | the pot is frozen. Both partners bear 0.10 offsettable friction a week. It settles at an equal split after 13 weeks, unless one partner runs short of money first (under 4 units) and walks away empty-handed | world: escrow, weekly tick, friction |
| F4 contribution weighted (the author's lean) | a leaver carries their share in proportion to **everything** they put into the household: the pot and the bills. Labor and care count 0, because the world does not track them | `carry_out` settles |
| F5 prenup | at formation the pair bargains the exit term with the existing machinery: `negotiate_v2`, with `nash_terms` on, over the exit term only, each partner against their outside option at formation. The agreed term (equal split, carry what you put in, or forfeit) sets the carry. If they don't agree, they decline to form: they live apart with no pot | `WeeklyWorld.__init__` calls `exit_fallback.prenup` |

Under F1 to F5, an imposed E1-at-most-half card (evolved variants included) is removed, because the fallback now decides the no-deal exit. Every arm from F1 to F5 also refuses a claim over half the pot. For F1 that refusal is the rule itself. For F2 to F5 the settlement sets the carry whatever is claimed, so the refusal only changes which claim gets made. It also lets the liberty adapter see that nobody can carry the other's half at will. That adapter knows the pot but not who put what in, which is a stated limit: **liberty cannot tell F1 to F5 apart, by construction.** It can only tell them from F0.

## Where each piece lives, and why both world and evaluator

- **World.** A fallback is a fact about how exit works, so it lives where exits are executed (`carry_out`, `apply` on leave) and where rules are assembled (`PyGate`). Liberty reads the same gate and needs no change.
- **Evaluator: the stay test.** `exit_cost(world, r, w)` is what r put in (their share of the pot on the F4 basis, pot plus bills) minus the most they can carry by leaving now. It charges any exit rule that withholds a member's own contribution: a cap, a forfeit term, a contested pot, or a stay bind's forfeit. With the switch on, the bar lens's "costs removed" holdings include what the member put in. A bigger contributor whose status quo sits between the two outside options then reads "held" (hard to leave), not "worth it". With the switch off, the bar lens is unchanged.
- **Evaluator: holdout leverage.** For each partner, take what they can force by a no-deal exit (walking out with their largest permitted claim, the settlement, or holding out in a contest), minus their contribution share. Divide by the pot, clip at 0, and take the larger of the two partners. 1 means one partner can take the whole pot without having put anything in; 0 means nobody can force more than their own share. It measures capability, not exercise.

The reference for both measures is the F4 basis, so **F4 is 0 on both by construction.** That is a choice, and it favours the author's lean. The prereg marks those cells "cannot fail".

## What the world does that matters (found while building)

- The world never adds to `put` after week 0 in the runs inspected. Contributions go to the bills first, and the pot surplus rarely grows. So F2 behaves like an equal split, and **F2 cannot differ from F1** except by integer rounding. The bills are where contributions diverge, and only F4 reads them.
- The pot drains over a lifetime (take_shared, bills, pressing free-riders), and many exits meet an empty pot. A fallback can only change anything in a run where an exit meets a non-empty pot. The prereg counts those runs.
- The existing "proportional" exit term carries `min(pool, put)`. Once the pot falls below 45, the first to leave carries all of it.
- The seed v2's week-0 stub binds both partners to a 52-week stay with the whole carry forfeited on a breach. `exit_cost` charges that bind too.

## Slice 2 (not built)

Indivisible items (home, pet, stuff) with per-person values, some sentimental (valued above price). Under F4, each item goes to whoever values it more, with money paid to the other. That gets built only if slice 1 lands cleanly.

## Limits

This is the imposed world, where rule sets are imposed as in evolution and the exams. Nobody renegotiates, except F5's single bargain at formation. The agents are scripted, the world is money only, labor and care are untracked, and every number is ASSUMED.
