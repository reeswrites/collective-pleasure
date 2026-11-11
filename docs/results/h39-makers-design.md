# H39 makers: design

Wording rule: agents feel nothing; "pleasure" is a gloss for a modeled hedonic state.

Status: design, written before any H39 code or run. Nothing here is a result. Every number is ASSUMED unless a source is given. The prereg is [h39-makers-prereg.md](h39-makers-prereg.md). Background: [pleasure-technology-and-makers.md](../notes/pleasure-technology-and-makers.md) (section 6 has the author's answers) and [decision-weights-research.md](../notes/decision-weights-research.md).

## Why

Today pleasure in the household comes from persona weights and need levels. Nobody makes it. The README says so: labor and care count 0, a known gap. The author: "someone has to create art games food etc the things that give you pleasure".

H39 adds makers. Some agents spend time making food, art and games, or giving care. What they make gives the receiver pleasure. And making counts, in the exit split, under one of six crediting rules. The author's view of how it should count: "i think it certainly counts its like valuing domestic work but yeah we might have to think more sophisticated", and "pleasure is certianly a consideration too".

## The world

The H38 household, unchanged: two partners and a friend, the baseline rule set, may decline to form, fixes and levers on, exit fallback F4 with items on (home, pet, collection; valuation cell V2), pairing dial 0, 156 weeks. Same 120 pairings as H38.

Formation and stay decisions use the corrected rule with a per-persona suffering weight (below). Makers are a new module, `src/mar/makers.py`, OFF by default. With it off, every earlier run is bit-identical (pinned fingerprints, `tests/data/makers_off_fingerprints.json`).

## Makers

**Every persona gets four traits, drawn from a hash of its id** (so they are fixed per persona and independent of each other and of the persona's other fields):

| Trait | Values | Share |
|---|---|---|
| maker kind | cook, artist (art and games), carer | 1/3 each |
| enjoyment of making e | 0, 0.5, 1 | 1/3 each |
| aim | safe, extractive | 2/3, 1/3 |
| suffering weight w | exp(z), z ~ N(0, 0.6), clipped to [0, 4] | continuous, median 1 |

Every persona can make. Whether and how much they make is decided each week.

**Making takes time.** One block of making costs 2 of the week's 10 time units, the same as resting or a together session. A partner makes up to 3 blocks a week, only while both partners live together. Time spent making is time not spent working, resting, seeing friends or being together. That is the cost, and it lands in the world's own pleasure terms.

**What each kind makes** (per block, fresh, for the partner who receives it):

| Kind | What it is | Pleasure to the receiver |
|---|---|---|
| cook | a meal: perishable, eaten once, this week only | 0.03 once |
| carer | care: exists only in the moment | 0.02 once, 0.03 when the receiver is struggling (low mood, ill or out of work) |
| artist | a piece: durable and shared, both partners enjoy it | 0.004 a week to each partner for 8 weeks |

The per-block totals are set close to each other on purpose (about 0.03 to the receiver), so kinds differ in shape, not size.

**Within a week, each extra block is worth less** (by 20% a block, the within-session satiety `ws` of src/mar/wanting.py). **Across weeks, tolerance builds.** A receiver who gets 2 or more blocks from the same maker in a week gains one tolerance level (up to 4). Each level takes 15% off the pleasure of a block. A week with none recovers one level. These are the liking side of ADR 0018 test 1, with `dl`, `H`, `dose` and `ws` taken from `wanting.WantParams`, ported from days to weeks.

**Making is itself pleasure for the maker.** A maker gets e × 0.01 per block. That does not lower their credit. It counts as their own pleasure (author, q2).

**Long projects (artists only).** An artist can start a long project instead of single pieces: 16 blocks, at least one a week. While it runs, the artist gets 0.01 a week from having it (the author's "having a goal"). On completion it becomes a lasting work worth 0.02 a week to each partner while they live together; the artist keeps it if they split. If either partner leaves before it is done, the project is lost.

An artist starts a project at a 13-week review if its expected value beats making the same blocks as pieces. The expected value uses the artist's estimate that the household lasts long enough, which falls with each past leave in this household and when a reading has said either partner would rather be apart.

**Protecting a project is negotiated** (author, q5: "its all about negoitation and trust again"). In the protection arms, an artist who would not start a project unprotected, but would start it protected, asks the partner. The protection is a promise: if the partner leaves before the project is done, the project's blocks so far count for the artist at the exit split, at replacement value, on top of the crediting rule. The artist believes the promise as far as they trust the partner, so the project's expected completion rises. The partner agrees only if their trust in the artist is at least 0.4 (the world's `commit_min`) and their last reading did not say they would rather leave. Nothing is imposed. A descriptive arm imposes protection on every project, as a contrast.

Note on trust: in this world (baseline rules, no commitment mechanics) trust stays at its start value of 0.7. So agreement here comes down to the partner's own stay reading. That is the construct, and the prereg says so.

## Safe and extractive makers

A safe maker aims at the receiver's liking. An extractive maker aims at the receiver's wanting (author, q3: goods that raise wanting without liking; motive is not modeled).

An extractive maker's goods carry a cue. For the receiver, wanting = liking + 0.02 × (1 + 0.12 × s), where s is a sensitization level that rises by one per block received (up to 12) and falls by one after a week with none (`sig`, `S` from `wanting.WantParams`). The first blocks are also a little more liked (+20%, hyperpalatable). A receiver who has been sensitized and gets nothing in a week carries a craving cost of 0.05 × s / 12 as offsettable suffering.

The mechanism, in plain words: the extractive maker keeps making because the receiver keeps wanting, tolerance builds, and liking per block falls. A safe maker stops when the next block is not liked enough to be worth the time.

## The weekly making choice (scripted)

Each week, for each block k = 1, 2, 3, a partner makes block k if

`e × 0.01 + care × g_k + κ × money_weight × c_k − 0.012 > 0`

- `care` is the persona's togetherness weight; `g_k` is what block k gives the partner (their liking, for a safe maker; their wanting, for an extractive one). For an artist's piece, the artist's own share of it counts too.
- `0.012` is the time cost of a block in pleasure units (ASSUMED).
- `c_k` is the credit block k earns under a rule with a running tally, in money units; `κ = 0.004` per money unit (ASSUMED) turns it into a motive, scaled by how much the persona values money. Under C-zero and C-gift-at-exit there is no running tally, so `c_k = 0`: making is a gift while living together.

So crediting changes how much is made only through this motive, by construction. What the run can show is the rest: who makes, whether pleasure rises once time costs and tolerance are counted, whether imbalances even out, and how exits change.

## Crediting arms

Credit is counted in money units and added to what each partner put in (pot and bills), the F4 basis. So under F4 a leaver's share of the pot and items is (money put in + making credit) over both partners' totals. One block at replacement value is 2.75 (the wage for the same 2 time units).

| Arm | How a block counts | Running tally? |
|---|---|---|
| C-zero | 0 (as today) | no |
| C-hours | 2.75 per block (hours, or replacement cost) | yes |
| C-pleasure | 2.75 / 0.03 = 91.7 per unit of pleasure the partner received from it | yes |
| C-base+pleasure (author's lean) | the replacement value, adjusted up or down by half of how far the pleasure given is above or below a typical block's: 0.5 × 2.75 + 0.5 × 91.7 × pleasure given | yes |
| C-gift-at-exit | nothing during; at exit the household counts everything made, as C-base+pleasure | no |
| C-agreed | at the first week together, the pair picks one of the four rules above | yes, if the chosen rule has one |

"Pleasure given" is the receiver's liking from the block: how much better off they are than if they had fended for themselves. Without a maker, the receiver gets nothing extra in this world, so the two are the same.

C-gift-at-exit equals C-base+pleasure with the motive switched off. So BP minus G is the effect of the running tally on behaviour, and G minus Z is the effect of the exit split alone.

**C-agreed, how the pair agrees.** Each partner projects their own share of credit under each rule, from their own and the partner's traits at a fresh start. If both prefer the same rule, it is used. If not, they take the rule whose projected shares are closest to equal (the largest product of shares). It is a simple bargain, stated so it can be read and changed.

## Decision rule: per-persona suffering weight

Formation, retries and stay readings score `pleasure − w × (s_off + s_non)` over 52-week rollouts, accurate forecasting, unanimity, w per persona from the table above (drawn independently of risk tolerance). This is `FixConfig(decide_on="weighted", decide_weeks=52)`. Sensitivity arms: w = 0 for everyone (`decide_on="pleasure"`, the H38 corrected rule) and the old net rule (w = 1, 26 weeks). Overprediction of suffering is not in H39's arms.

The research note expects this rule to form fewer pairs than w = 0, likely near the old rule's 51%. That is preregistered.

## Hooks in shared files

All H39 logic is in `src/mar/makers.py`. The hooks are small and off by default:

- `worlds/household.py`: build the makers state at world creation; one call at the start of each week (choices, time); one call when the week closes (pleasure and craving terms added to the existing extra-pleasure and friction inputs).
- `exit_fallback.contribution_share`: the "all" basis adds making credit when makers are on.
- `negotiation.wellbeing`: a "weighted" branch with the persona's w; call sites pass the persona.

## What this cannot be about

Making is a scripted weekly choice with assumed numbers. Goods are three stylized kinds. Credit matters only at exit, through F4. Pleasure is clipped at 1 and most person-weeks sit near it, which hides part of what makers give; the unclipped line is reported beside it. The "having a goal matters more than achieving it" clause of H20a is an input here (the goal term), not something the run can find.
