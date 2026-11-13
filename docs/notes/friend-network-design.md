# A friend network for the many-agent world: design (PROPOSAL, 2026-11-13)

Wording rule: agents feel nothing. "Pleasure" and "suffering" are glosses for a modeled hedonic state (ADR 0010).

Status: a design proposal, not a result. Part 2 of H42 (experiments/hypotheses.jsonl), from the author's confirmed read-back rb-2026-11-13-friends. The research behind it is docs/notes/friendship-research.md. No code was changed. **Every number below is ASSUMED unless a source is named next to it**, and named sources set directions or rough sizes, not inputs.

## In one paragraph

Extend L-C, do not replace it. Each bond gets two stocks: **closeness** `c`, which fades fast without contact, and **history** `h`, the hours spent together, which barely fades and caps how close the tie can be. Tiers (close, medium, acquaintance, dormant) are read off `c`, and each tier opens more strands. Old ties come back in weeks because their history is intact; new ties need months because theirs is not. Friends are agents: their pleasure is counted, so withdrawal costs them too. Isolation is measured as **exit support**: how much of a person's needs the ties they could reach within a month would cover if they left. It joins the stay test as a removable cost and sits beside liberty like the money runway. A breakup splits mutual friends by a declared rule. It all costs a few floats per bond per week.

## 1. What L-C already has, and what is new

| Piece | In L-C today (src/mar/hedonic.py, worlds/household.py) | This proposal |
|---|---|---|
| Strands a bond serves | `STRANDS` (care, affection, intimacy, logistics, commitment, desire); thick bonds 3, thin 2 (`strand_sets`) | Kept; add `fun` and `advice` from the read-back (author question 1) |
| Needs met by several bonds | `strand_cover`: 1 − product of (1 − supply) per strand | Kept as is. It already rewards spreading strands (Cheung et al. 2015) |
| Capacity dilution | `bond_capacity` 3.0: supply = quality × min(1, 3 / strands held) | Kept |
| Bond strength | `qx`: + `qx_visit` 0.30 per visit toward 1, × (1 − 0.05) a week | Replaced by `c` with a history-limited ceiling |
| History, old vs new | none | New: `h` per bond |
| Tiers | none (all bonds alike) | New: read off `c`; gate strands |
| Coordination cost | `coord_a` 0.2 × n^1.7 units a week | Kept, counted over close and medium ties only |
| Ruptures | `bond_shocks`: a bond goes to 0 for 6–20 weeks, 0.2 per bond-year | Kept as conflict ruptures; add a repair cost |
| Care floor | `care_suffer` when care cover < `care_ok` 0.3 | Kept |
| How many bonds a persona runs | `bond_policy`: 1 + round(3 × `other_connections`), at most 5 | Replaced by a time budget and three traits (section 5) |
| Friend closeness and longing | Fix 1 (`FixConfig.contact`): `cf`, `c_visit`, `c_decay`, tension `Tf` for Friend C | `c` replaces `cf` when both are on; tension kept |
| Withdrawal | H38 (`pairing.withdraw`): cuts the wish to see friends and declines visits while paired | Kept; now it starves `c` and `h`, and costs the friend |
| Friends as agents | Friend C is passive; nobody counts the friend's loss | New |
| Isolation measure | none | New: exit support (section 7) |
| Breakup split of friends | none | New (section 8) |
| Meeting new people | `new_connection_rate` 0.20 a year adds a glow, no tie | New ties (section 9) |

All of it goes behind one flag, `friends`, in a new `FriendConfig` block in hedonic.py, off by default. With it off, nothing new is read and runs stay bit-identical, as the repo's other flags do.

## 2. The bond

**One record per pair of people.** Closeness `c` and history `h` belong to the pair. Strands are per direction: what `j` does for `i` need not be what `i` does for `j` (the read-back: different people scratch different itches).

| Field | Meaning | Start (new tie) |
|---|---|---|
| `c` | current closeness, 0 to 1 | 0.05 |
| `h` | history: hours together so far | 0 |
| `S_ij`, `S_ji` | strands each side can serve | drawn at formation (section 4) |
| `last` | week of last contact | now |
| `origin` | who introduced them (self, partner, housemate, friend) | at formation |
| `down_until` | rupture end week, if ruptured | none |

**Hours per contact.** One visit counts 3 hours of history (ASSUMED; one evening). Contact at work or in a shared house counts less per week of contact, as Hall (2019) found leisure time counts more than work time.

## 3. History, decay and repair

**History caps closeness.** The ceiling a tie can reach is `f(h) = h / (h + K)`, with `K` = 120 hours (ASSUMED). It is set so the tier lines fall near Hall's press-release hours: about 50 hours to cross into medium (`f(50)` = 0.29) and about 180 to 200 hours to cross into close (`f(180)` = 0.60, `f(200)` = 0.63). Hall's figures are secondary, so this is a rough fit, not a calibration.

**Contact pulls closeness toward the ceiling.** Each visit: `h += 3`, then `c += g × (f(h) − c)`, with `g` = 0.35 (ASSUMED). A new tie is held down by its small `f(h)`; an old one jumps back toward its high ceiling.

**Every week, closeness fades.** `c ×= 1 − d(h)`, with `d(h) = d0 / (1 + h / Kh)`, `d0` = 0.02 a week and `Kh` = 200 hours (ASSUMED). Deep ties fade more slowly. Roberts & Dunbar (2011, 2015) give the direction (friends fade without contact; contact slows it), not a rate.

**History barely fades.** `h ×= 1 − 0.0013` a week, a half-life of about 10 years (ASSUMED). This carries Levin, Walter & Murnighan (2011): strong ties dormant three years or more kept most of their strength. In a 156-week run it hardly moves.

**What these numbers give** (worked from the formulas in a scratch script; checks in section 10):
- A medium tie (`c` 0.45, `h` 100) with no contact for a year ends at `c` 0.22: an acquaintance.
- A close tie (`c` 0.70, `h` 300) with no contact for a year ends at 0.46 (medium); after two years 0.30.
- An old close friend gone quiet (`c` 0.2, `h` 300) is close again after 4 weekly visits. A new tie at one visit a week reaches medium in about 21 weeks and close in about 67 weeks (about 200 hours).
- Keeping a close tie close takes about one visit a month; a medium tie, about one every two months. That is each tier's maintenance cost.

**Reconnecting costs something.** The first contact after 26 or more weeks without one costs one extra time unit (ASSUMED). Levin et al.'s follow-up found reconnecting can make people anxious (secondary), so a persona with high start-up reluctance (section 5) may skip it.

**Friends move on.** While a tie is dormant, the friend fills the time with others: the chance they accept a reconnection is `exp(−weeks_dormant / 104)` (ASSUMED). This follows Saramäki et al. (2014): people keep a stable pattern of contact while its members change. For agent friends, their own time budget decides instead. This is one way withdrawal's harm can outlast the relationship (author question 2 in the research note).

**Repair after a rupture.** L-C's ruptures stay: a ruptured bond supplies nothing for 6 to 20 weeks. Leaving it, `c` restarts at half its value before the rupture, and the first visit costs one extra unit. `h` is untouched.

## 4. Tiers and strands

**Tiers are read off closeness, not stored.** Close `c ≥ 0.6`; medium 0.3 to 0.6; acquaintance 0.1 to 0.3; dormant below 0.1 (with history it can come back). Thresholds ASSUMED.

**Each tier opens more strands.** This carries Sutcliffe et al. (2012): layers serve different functions.

| Tier | Strands it can serve | Payoff | Maintenance |
|---|---|---|---|
| Close | care, intimacy, advice, fun, logistics, affection | full strand supply | about one visit a month; counts toward coordination cost |
| Medium | advice, fun, logistics, affection | strand supply | about one visit every two months; counts toward coordination cost |
| Acquaintance | fun | a belonging term per encounter (below) | none planned; incidental encounters |
| Dormant | none | none now; counts toward exit support (section 7) | none |

**Weak ties pay a little.** Each acquaintance encounter adds 0.01 pleasure, at most 0.03 a week (ASSUMED). Sandstrom & Dunn (2014) found more classmate interactions on a day went with more happiness and belonging; the size here is free. Acquaintances never supply care.

**Which strands a friend can serve.** At formation, each side's strands are drawn from the tier list, two or three per side (as L-C's thin and thick bonds), weighted by the other person's traits (ASSUMED: a sociable persona leans to fun, a high-competence one to advice). A strand is served only when the tier opens it: a new friend drawn with care starts serving care only once close.

**The partner core is unchanged.** The partner bond `q0` keeps holding every strand, as in L-C. Friends cover what the partner does not, and the cover formula already gives diminishing returns.

**Pleasure from friends.** Unchanged in form from L-C: `strand_pay × Σ w_s × cover_s`. The friend part of it is scaled by the persona's friend weight `φ` (section 5): pay = partner-only part + `φ` × (cover with friends − cover from the partner alone). The connection need clock (`conn_friend` per visit) is kept as is in the first slice.

## 5. How much people value friends

**Three traits, not one.** The research separates them (friendship-research.md): how much friends matter (need to belong; Leary et al. 2013), how many ties someone runs (extraversion, small effect; Pollet et al. 2011), and how readily they start and keep ties (attachment avoidance; Gillath et al. 2017).

| Trait | Meaning | Default distribution | Grounding |
|---|---|---|---|
| `φ` friend weight | scales the friend part of strand pay | `exp(z)`, `z ~ N(0, 0.4)`, clipped to [0.25, 2.5] | ASSUMED; the existence of spread is sourced, its size is not |
| `budget` | time units a week for friends | from the persona's existing `other_connections` weight, as `friends_per_week` uses it today (1.5 × weight visits) | existing persona code |
| `start` | rate of starting new ties and of reconnecting | `exp(z)`, `z ~ N(0, 0.3)`, weakly tied to `budget` (correlation 0.2) | ASSUMED; 0.2 echoes Pollet et al.'s small r, as a pattern not a measure |

**Drawn like the suffering weight.** As `makers.suffering_weight` does, each trait is drawn from the persona id alone, so it is fixed per persona and reproducible.

**A low-`φ` persona is not lonely by design.** With `φ` near 0.25, friend strands add little and missing them costs little. That is "people differ in how much they value friends at all", and it keeps the model from assuming everyone wants many friends.

## 6. Friends are agents

**Everyone counts.** A friend's loss when someone withdraws is a loss in the welfare sum, not a side effect.

**Two kinds of friend.** The many-agent world has 4 to 6 agents, and a person's network is larger than that (friendship-research.md, layers). So:

- **Agent friends** are the other agents. Their bond with `i` is one shared record; each reads its own direction's strands into its own hedonic close. Their time budget, their withdrawal and their pleasure are already modeled.
- **Background friends** are light stubs, 8 per agent (ASSUMED). A stub has a bond, strands toward `i`, and a fixed number of other ties of its own. It has no hedonic state. Its pleasure from `i` is computed by the same strand formula, from its side of the bond, with stub weights equal to the default strand weights.

**How they are counted.** Total pleasure with everyone counted = agents' pleasure + stubs' bond pleasure. Stubs are reported as their own column ("friends' pleasure"), so a result can be read with and without them. Whether stubs count fully is author question 2.

**What this changes.** Under H38 withdrawal, the friend now loses strand cover and its tie fades. That is the second clause of H42 ("costs the friends themselves"), made measurable.

## 7. Isolation as a freedom measure: exit support

**The question it answers.** If this person left their household this week, how much of their needs could the ties they can reach cover within a month?

**Reach.** For each of `i`'s ties `j` other than the partner, `reach_ij` is the closeness the tie would have after 4 weeks of one visit a week, from its current `c` and `h` (four steps of the section 3 update; a closed loop, no rollout). A dormant old friend has high reach; a new acquaintance has low reach. Ruptured ties and stubs that would refuse (section 3) get reach 0.

**Keep.** `p_keep_ij` is the chance `j` stays with `i` after a breakup, from the split rule (section 8). It is 1 for ties that are only `i`'s.

**Exit support.** `E_i = Σ_s w_s × [1 − Π_j (1 − p_keep_ij × reach_ij × open_s(reach_ij) × min(1, cap / |S_ji|))]`, summed over strands `s` with the strand weights, where `open_s` is 1 if the tier at `reach_ij` opens strand `s`. It is the strand cover the reachable network would give, from 0 (no one to turn to) to 1.

**Two companions.** `N_i`, the expected number of ties that would be close within a month (Σ `p_keep_ij` over ties with `reach_ij ≥ 0.6`). And `E_care,i`, the care cover alone.

**Isolated.** A member is isolated when `N_i < 1` and `E_care,i < care_ok` (0.3, L-C's care floor). Threshold ASSUMED.

**How it joins liberty.** ADR 0014 books withdrawal (declining to act) outside freedom, and this proposal keeps that. Exit support is a state measure, read like the money runway in docs/notes/economy-calibration.md (item 9): it says how real the `leave` option is, not who blocked it.

- **In the stay test.** Add "isolation" to the removable exit costs. The counterfactual replaces the network with a **shadow network**: the same bonds updated as if every contact that withdrawal or a partner's veto removed had happened. A stay reading is *held by isolation* if the member stays with the actual network and would leave with the shadow one. This is the held-versus-worth lens of formation-check-3.md, applied to the friend network.
- **Beside liberty.** Report `E_i`, `N_i` and the isolated share for every member at every liberty snapshot, as columns next to liberty with powers and domination exposure.
- **Interference stays where it is.** A partner's veto or block on seeing a friend is already interference and already counts in liberty. Exit support shows its lasting effect on top.

**Why this shape.** Isolation is recognized as a means of control (Stark 2007; Home Office 2023). Loneliness tracks the quality of ties more than their count (Pinquart & Sörensen 2001; Bruine de Bruin et al. 2020). So the measure counts depth and needs covered, not heads. The model has no abuse in it, and the measure makes no claim about abuse.

## 8. Breakups and mutual friends

**Who is mutual.** A friend `j` with `c ≥ 0.1` to both partners.

**The split rule** (ASSUMED throughout; no study measured how mutual friends divide, friendship-research.md):
1. `j` stays with both with chance `0.5 × (1 − conflict)`, where `conflict` is 1 if the household ended in a rupture or with an unpaid exit term, 0.5 if one partner left against the other's wish, else 0. This carries Terhell et al. (2004): network loss depends on conflict with the ex.
2. Otherwise `j` sides with the partner `x` with the larger `h_jx × (1.5 if x introduced j else 1)`. Who knew `j` first and longer keeps `j`.
3. The other partner's tie to `j` drops to `c` = 0.05 and `j` refuses reconnection with chance 0.7 for 52 weeks. `h` is kept, so it can come back later.

**Why it matters.** Couples' networks overlap more the longer they live together (Kalmijn 2003). With withdrawal, a member's own ties fade and the shared ones, often from the partner's side, grow. At a breakup the shared ones split by history and origin, so the withdrawn member keeps less. That is how the harm can outlast the relationship without assuming old ties are slow to rebuild.

## 9. Meeting new people

**Rate.** Each agent meets a new person with chance `λ = 0.1 × start_i × (1 + housing contact)` a week (ASSUMED, about five new acquaintances a year at `start` 1). Housing contact is the housing note's free contact chances (docs/notes/housing-research.md, regimes C and D).

**From where.** Half from friends of friends (Granovetter 1973: ties cluster), the rest from the other agents and a fresh stub pool (ASSUMED shares). A paired member also meets the partner's friends: each partner's medium or close friend becomes an acquaintance of the other with chance 0.1 a week while they live together, `origin` = partner (ASSUMED; the direction is Kalmijn 2003).

**Where they go.** A new tie starts as an acquaintance (`c` 0.05, `h` 0) and grows only with time spent (section 3). When an agent's live ties exceed what its time budget can maintain, the least recently seen fade on their own. No hard cap on network size; layer sizes come out of budgets.

**The old glow event.** With `friends` on, `new_connection_rate` stops adding glow and makes a tie instead.

## 10. Known-answer checks the module must pass

These are checks on the module before any H42 result is read, not results. Each is a unit test on the bond update or a short scripted run.

1. **A year of silence demotes a medium tie.** `c` 0.45, `h` 100, no contact for 52 weeks: ends below 0.3 (acquaintance). Formula: 0.22.
2. **An old close friend comes back faster than a new one forms.** At one visit a week, an old tie (`c` 0.2, `h` 300) reaches close in at most 6 weeks; a new tie (`h` 0) takes at least 52. Formula: 4 and 67.
3. **Hall's order.** At one visit a week from zero, the weeks to medium are fewer than to close, and close takes at least 180 hours of history.
4. **Withdrawal with no friends left raises the held share.** Same household, H38 withdrawal at L4 for 104 weeks, against no withdrawal: the share of stay readings held by isolation is higher, and it is 0 when withdrawal is off.
5. **Isolation measure, ends and order.** No ties: `E` = 0 and isolated. Adding a dormant old close friend raises `E` more than adding a new acquaintance.
6. **Withdrawal costs the friend.** A friend's pleasure (agent or stub) is lower when `i` withdraws than when not, in the same seeds.
7. **Diversity beats concentration** (Cheung et al. 2015, direction). Three close friends serving distinct strands give more cover than three serving the same strands.
8. **Weak ties never supply care.** Any number of acquaintances leaves `E_care` and care cover unchanged.
9. **Layers come out tapered.** Under default budgets, after 156 weeks each agent has more acquaintances than medium ties and more medium than close (shape only; not 5/15/50/150, Lindenfors et al. 2021).
10. **Pairing shrinks friend contact, singles see more friends** (Kalmijn 2003; Sarkisian & Gerstel 2016, direction). Paired agents with withdrawal on have less friend contact than single agents on the same seeds.
11. **Low `φ` personas are not hurt by few friends.** At `φ` 0.25, removing every friend lowers pleasure by less than a quarter of what it costs at `φ` 1. (The care floor's suffering is not scaled by `φ` in this proposal; if that makes low-`φ` personas suffer from missing care, it is a finding about the floor, to report, not to patch.)
12. **Off is off.** With `friends` off, every pinned fingerprint in tests/data matches.

Checks 1, 2, 3 and 7 are partly true by construction; they guard the code, not the claim (docs/limits.md, limit 6). Checks 4, 6, 9 and 10 can fail.

## 11. Cost: keep it light

**Per bond, per week:** two multiplies and a compare for decay; a few more per visit. About 15 bonds per agent (up to 5 agent friends, 8 stubs, a few new ties) and 6 agents: about 90 bond updates a week. Today's weekly step is dominated by gate checks and the agents' own arithmetic (docs/notes/performance.md), so this is small.

**Cache strand cover per agent per week.** `strand_cover` was already 4% of a v2b run, because v2b agents call it for every candidate action. Cover only changes at the week's end, so compute it once a week and read it.

**No new rollouts.** Reach and exit support are a four-step loop on two numbers per tie, computed only at readings (every 13 weeks). Partner choice and reconnection choice use `c` and `h` as a cheap value-of-match, so there are no rollouts per candidate pair. The step-back review warned that rollouts per pair grow with the square of the population.

**The shadow network** doubles bond updates only when withdrawal or a contact veto is on, and only for the affected member's ties.

**Cheap copies.** Store bonds as flat lists of floats per agent, not objects with logs, so a rollout's deep copy stays small. docs/notes/performance.md measured a whole-world deep copy at about 15 ms; the bonds add hundreds of floats to it.

**The bar.** Before any H42 run, a timing probe like performance.md's: one run with `friends` on and off, same seeds. If `friends` adds more than 10% to a run, cut stubs or cache more before running.

## 12. Order of building

1. The bond (`c`, `h`, decay, contact, tiers) with checks 1, 2, 3, 12. Pure functions in hedonic.py, no world change.
2. Strands by tier and the friend weight `φ`, with checks 7, 8, 11.
3. Exit support and the shadow network, with check 5.
4. Friends as agents and stubs in the many-agent world, with checks 6, 9, 10.
5. The stay-test "isolation" cost and the breakup rule, with check 4. Then H42's prereg.

## 13. What a small model can and cannot claim

**It can show mechanisms.** For example: if withdrawal starves history and the partner's friends side with the partner at a breakup, then exit support falls over a relationship and some stay readings become held by isolation, given these rates. That is a statement about the model.

**It can compare rules inside itself.** Same agents and seeds, with and without withdrawal, with and without the split rule, judged on pleasure with friends counted, on liberty, and on exit support.

**It can check directions.** The checks above. If a direction fails, the comparisons are suspect.

**It cannot give rates for people.** The decay rate, the reactivation speed, the split rule and the meeting rate are ASSUMED. Only Hall's hours touch a number, and those are from a press release.

**It cannot say what friendship is like.** Strands, tiers and a closeness number are a sketch of what the read-back named, not a measurement of anyone's friends.

**It cannot say anything about abuse.** Exit support measures what a member could turn to. It is motivated by research on coercive control, but the world has no coercion beyond holding, withdrawal and vetoes.

**Stubs are a compromise.** Background friends have no lives of their own beyond a bond and a time pool. Results that depend on them should be read with and without their column.

## 14. Questions for the author

1. Should the strands be extended to eight (adding fun and advice), or should fun replace affection? This decides what a friend can do for someone that a partner already does.
2. Background friends are stubs with no hedonic state of their own. Should their pleasure count fully in "everyone counts", count at a discount, or be reported only beside the total?
3. Exit support sits beside liberty and enters the stay test as a removable cost, keeping ADR 0014's rule that withdrawal is not domination. Is that where you want isolation, or should a partner's role in shrinking someone's network count as domination too?
