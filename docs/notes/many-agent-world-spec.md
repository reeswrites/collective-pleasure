# The many-agent world: one spec (PROPOSAL, 2026-11-13)

Wording rule: agents feel nothing. "Pleasure", "suffering" and "value" are glosses for a modeled hedonic state (ADR 0010).

Status: a design spec, not a result. Written by an agent at the author's request ("one spec for the many-agent world", experiments/changes.jsonl, 2026-11-13T17:48:39Z), while H41 runs in the pair world. No code was changed and nothing was run. **Every number below is ASSUMED unless a source is named next to it.** Cost figures are orders of magnitude worked from measured pair-world timings (docs/notes/performance.md, docs/results/hybrid-agent.md, docs/results/formation-check-3.md), not measurements of a world that does not exist yet.

Sources read: docs/notes/step-back-review.md, friend-network-design.md, friendship-research.md, housing-research.md, economy-calibration.md, debt-left-ideas.md, decision-weights-research.md, performance.md, observer-schema.md; ADRs 0019 and 0020; docs/results/hybrid-agent.md, formation-check-3.md, h38-exact-model.md, h41-choice-aids-prereg.md; hypotheses H36, H37, H38b, H39, H40, H41, H42, H43; src/mar/worlds/household.py, hedonic.py, hybrid.py, agent_values.py, negotiation.py, observe.py, liberty.py; docs/limits.md. Two notes were written in parallel and landed while this was being drafted: docs/notes/amenities-research.md (section 5 fits its amenity layer into a slot) and docs/notes/persona-generator-design.md (section 2 names the plug). Both were read in their design sections; where they and this spec differ, it is said.

## In one paragraph

One world of **24 agents** (a village, not a city), stepped **weekly** for 156 weeks, with households, jobs, housing units, amenities and a lender as plain records, not agents. Every agent is the **hybrid**: v2's one-week values for the routine, sampled futures for big choices. Two changes make it scale. First, a big choice is played forward in a **local sub-world** (the chooser's households and the people the option touches), with the rest of the world held as a background of rates, so a rollout costs the same at N = 24 as at N = 2. Second, partners and housemates are **shortlisted** by a closed-form one-week value of the match, and only the top three are simulated, so the cost grows with N, not N². Relationships are bonds (H42) plus **contracts**: explicit records with parties, terms as ADICO cards, and exit terms, checked for consistency across everything one agent holds. The world is built in seven layers, each with known-answer checks that must pass before the next starts. A full-stack run should cost about 20 to 60 minutes; most hypotheses need only some layers and cost 5 to 20. The biggest risks are the frozen background in rollouts, the shortlist's blind spots, and H36, which can be run only in a narrowed form.

## 1. The world

### Population: 24 agents

**Why not 4 to 6, as the friend and H38b notes assumed.** Those notes sized the world before anyone priced it. At 6 agents:

- partner choice is choosing among 2 to 5 people, and exclusivity can block at most a handful of bonds, so H38b's "blocking bonds agents would value" barely has room to happen;
- a 4-person shared house (regime C) is most of the world (housing-research.md, section 4, says this itself);
- 6 wage draws cannot show a 90/10 ratio, and at a 1% monthly layoff rate the world sees about one layoff a year;
- a commons of 6 is a household with a garden.

**Why not 100.** Cost (section 8) grows about linearly in N once rollouts are local, so 100 agents is about 4 times 24. More important, nothing in the hypotheses needs a town. The questions are about bonds, households and exits, which a village holds.

**Why 24.** It gives each agent about 10 to 15 people it could plausibly meet, 3 or 4 friend clusters, houses of 3 or 4 without the house being the world, about 3 layoffs a year, and room for 2 or 3 multi-partner networks. At about 5 minutes a run for layer (a) it is affordable (section 8).

**Two other sizes, both declared.** N = 2 plus Friend C is the **port configuration**, used only to reproduce the pair world (layer a). N = 6 is the **small configuration** for pilots and for any hypothesis an exact model is written beside. N = 48 is a scaling sensitivity arm, never a default.

### Time step and calendar

**One week**, as now. The hedonic model, the need clocks, the 13-week reading cadence and every calibrated weekly hazard are written in weeks; changing the step would change every one of them.

A **month** is 4 weeks: rent, bills, loan payments, the basic income and the tax settle at month end. A **run** is 156 weeks, the verdict span the pair world uses. Before week 0, a **bond-only burn-in** of 52 weeks runs the friend network alone (decay and contact, no hedonic close, no choices) so that ties do not all start at week-0 values. It costs almost nothing and is excluded from every measure.

Each agent has **10 time units a week**, as now. A full-time job takes 4, part-time 2 (economy-calibration.md, item 2).

### What a week looks like

1. **Shocks.** Layoffs, illness, job offers, housing vacancies and meetings are drawn from the world's own seeded streams.
2. **Routine.** Agents act in a seeded random order, two passes, as the pair world's calls do. Each picks actions by v2 one-week values: work (hours are set by the job), rest, visit a named friend, time together with a partner, make, use an amenity, spend, and the propose-only actions (request, refuse, veto, give, take). **Anything that needs two people is an invitation:** the visit happens only if the other agent accepts with its own time unit, on its own v2 value. That is how a friend's time budget binds.
3. **Month end** (every fourth week). Rent, bill agreements, loan service, basic income and tax move as standing transfers. Nobody chooses them weekly.
4. **Close.** Each agent's hedonic close on the saturating scale (ADR 0019). Bonds update (H42: closeness, history, tiers).
5. **Big choices.** Agents whose reading is due, or whose trigger fired, choose by sampled futures (section 2).
6. **Observer.** If attached, it records; it never writes anything the world reads.

### Entities

| Entity | What it is | Agent or record |
|---|---|---|
| Agent | a persona plus state: needs, B, N, money, savings, job, bonds, contracts | agent |
| Household | the people under one roof: a housing unit, a co-residence contract, a bill agreement, a shared pot (optional), a card set | record |
| Bond | one per pair of people who have met: closeness `c`, history `h`, strands per direction (H42) | record |
| Contract | parties, kind, terms as cards, exit terms, reading schedule (section 3) | record |
| Job | wage per unit, hours, enjoyment `e`, a layoff hazard | record; employers are not modeled |
| Housing unit | rooms, regime, rent, tenure (rented or owned), vacancy | record; the landlord is a rule (rent, rent capture) |
| Amenity | section 5 | record |
| Lender | a rule: interest, limit, minimum payment, jubilee schedule | record; never an agent |
| Treasury | basic income out, flat tax in, balanced yearly | record |
| Stub friend | a background friend: a bond and a time pool, no hedonic state (H42, section 6) | record |

Why employers, landlords and lenders are rules: the calibration notes all say the world has no firms, prices, land market or credit supply response, and that general-equilibrium effects can only be sensitivity arms with stated sizes. Making them agents would claim more than the model can carry.

## 2. Agents

### The decision model: the hybrid, frozen

**The hybrid, as of Amendment 3, with both new flags on**: `hybrid · sat · bills · satiety=world · hybrid_w=persona · hybrid_readings=world`. That is the agent H41 is running now.

Why this one:

- **It is the only agent that passes both pass tests.** PT-H: forecasts match 16 held-out futures (H1 +0.006, rank correlation 0.93, agreement 92% under the persona weight). PT-R: the routine agrees with the model at one week about as well as v2 (T1 0.952 against 0.955).
- **It lands where the exact model puts it.** In the third formation check, pressure's effect under the hybrid was +0.011 against the exact model's +0.011.
- **It puts the cost where the consequences are.** The headline moves in H38 came from forming and staying, not from Tuesdays. Simulating only those choices costs about 4 times v2b, not 150 times (step-back review, section 1).
- **Its known answer is only partly met, and that is stated.** K1 fails: in the trap fixture every household ends, because leaving pays. The many-agent world inherits that label for held share until a fixture exists where leaving is costly and the hybrid is asked.

**Use `hybrid_w=persona`, not the pleasure-only yardstick.** The third formation check found held members suffering three times as much under the pleasure-only hybrid, and one member staying through two years of non-offsettable suffering. In a world built to measure holding, a chooser blind to suffering would make held share mean something different.

**Freeze it.** The agent is decided once, here, as `hybrid-N/1`. Any change after layer (a) is a new version under ADR 0020, with its own pins and a "Findings this could move" list. No patch is made to make a later check pass (section 9).

### Routine choices: v2 values

Every weekly action is valued by the close's own arithmetic over one week (`agent_values`), as now. New routine actions get the same treatment:

- **visit a named friend**: the one-week close with that bond's strands covered, as `strand_cover` would compute it;
- **make**, and **use an amenity**: the one-week close with the action's hedonic parts;
- **sanction** (layer g) and the propose-only actions: by the hybrid's one-week fork against idle, own net plus the prosocial share of the other's.

No action is ranked by a fixed constant. That is the "mixed units" rule (section 9), and it is checked by a grep test like household-exam-grep-check.txt.

### Big choices: sampled futures

| Choice | Options | When |
|---|---|---|
| Form or join a household | stay as is; each shortlisted household or person (at most 3) | a reading, or a trigger |
| Leave a household | stay; leave alone; leave to a shortlisted option | a reading, a distress trigger |
| Move house | stay; up to 2 vacant units | a reading, a vacancy trigger |
| Take a job, quit | accept or not; quit or not | an offer; a reading |
| Enter, renew or exit a contract | the terms on the table; none | at formation; at the contract's reading |
| Open a credit line | open with terms; not | a shortfall trigger (layer c) |
| Adopt a rule in a commons | adopt; not | a proposal (layer g) |

**Readings** run every 13 weeks per agent, staggered by agent so they do not all land in the same week. **Triggers** (distress as `hybrid_readings=world` now defines it, a layoff, a vacancy, a new candidate passing the shortlist bar, a proposal) run an early reading. All choices use K = 4 sampled futures with resampled shocks on every side, over the persona's forecast horizon (52 weeks by default), scored on `pleasure − w × suffering`.

### Local rollouts: the change that makes N affordable

**The problem.** Today a rollout deep-copies the whole world. At N = 24 that is 12 times the work per simulated week, for every future of every option of every choice.

**The fix.** A big choice is played in a **sub-world**: the chooser, the members of every household the option touches (the current one, the candidate's), and nothing else. Everyone outside it is **background**:

- friends outside the sub-world are bonds with their current `c` and `h`, accepting visits at the rate their recent weeks show;
- the job and housing markets are hazards (layoff, finding, vacancy) drawn fresh in each future;
- other agents' big choices are not replayed; a partner outside the sub-world leaves at the base rate of the world's own past year.

So a rollout costs what the household's does, whatever N is. The price is that the background does not react to the option. Whether that matters is a pass test (layer a, check a4), not a hope.

**No future is the real one.** The sub-world draws its own shocks, vacancies, meetings and outside departures. It never reads the lived world's schedule, and never replays what the other agents will actually do (section 9).

### Shortlisting partners and housemates

**The problem.** A rollout per candidate per reading grows with N² (step-back review). At N = 24 that is 23 candidates × K futures × 2 options per agent per reading.

**The fix: a cheap value of the match, then simulate the top three.** For each agent `j` that `i` has met (a bond with `c ≥ 0.1`) and who is available under the world's norms (exclusivity, capacity, housing), compute `m(i, j)`: the one-week projected close for `i` of living with `j` (or partnering with `j`, without co-residence where nesting is optional), from the v2 arithmetic at the current state. It is v2's own value, so it is in the same units as everything else. It reads the bond's strands, the pair's wage and rent under the regime, and each persona's values and aspirations.

- Only candidates whose `m` beats `i`'s status quo by a margin (0.005 a week) enter, and at most the top 3. Most readings have none, and the reading is then the old stay-or-leave choice.
- A candidate is simulated from `i`'s side only. If `i` would propose, the candidate runs its own reading with `i` as its one extra option. Forming needs both yeses, as now.
- Cost: O(N × 3) rollouts per round of readings, not O(N²).

**What the shortlist cannot see.** `m` is one week, so it misses matches that pay only later, the same blind spot v2 has for households. That is why it only shortlists and never decides. Its recall is a pass test (check a5): on an audited sample, roll out every candidate, and report how often the best by rollout was outside the top 3 and what that cost.

### Misforecasting

**One home: the big-choice forecast.** The routine stays accurate. "People misjudge commitments more than Tuesdays" stays the default (step-back review). Traits are persona fields, neutral by default:

- the existing three: `horizon`, `discount`, `outside_bias`;
- one new: `match_bias`, added to the forecast of life with a new partner or housemate (optimism about someone new);
- **what agents know about a candidate.** In the port (layer a), the chooser simulates the candidate's true persona, as the pair world does. From layer (f) on, the default is a **signal that sharpens with history**: the forecast uses the candidate's true traits with weight `h / (h + 50)` and the population mean otherwise (ASSUMED). H41's "better information" aid is then a world dial, not a code path. This is question 5.

Each bias is measured against the model's own answer: PT-H with the trait on must fail by about the trait's size (the planted-bias check already does this for `outside_bias`).

### Where the persona generator plugs in

docs/notes/persona-generator-design.md proposes one function with two modes: **population mode** (correlated draws through a latent scaffold) and **design mode** (a Latin hypercube, for finding which dimensions drive a result). Every persona is drawn from a hash of its id, a salt and a generator version, so the same id always gives the same persona, and two or three anchor personas from the author are known-answer checks. The world calls it as `generate(n, seed, mode)` and states the mode and generator version in the model tag (section 6). Hypothesis runs use population mode; design mode is for sensitivity runs.

The world reads these fields. Most already exist; the generator proposes the rest:

| Field group | Fields | Where they come from |
|---|---|---|
| Hedonic | need salience, aspiration targets and weights, value weights, prosocial; the pleasure mix (sensory, conceptual, relational), `share_mult`, habituation | personas.py today; generator D1, D2, D10 |
| Big-choice taste | `w`, and its split `w_close`, `w_alone` | makers.suffering_weight today; generator D8 |
| Friendship | `φ`, `budget`, `start` | friend-network-design.md, section 5; generator D7 |
| Strands | per-persona `strand_weight` over the eight strands; `partner_core` | generator D6 |
| Crowding | `crowd_cost` (the per-person version of the housing regimes' conflict cost) | generator D4 |
| Making | maker kind, `make_pleasure`, aim | h39-makers-design.md; generator D5 |
| Money | money and security weights, `patience` (sets the forecast discount and savings target) | generator D9 |
| Forecast | `horizon`, `discount`, `outside_bias`, `match_bias` | hybrid.traits; `match_bias` is new here |
| Romance | wants a partner at all; wants more than one; wants to nest | **not in the generator yet.** H38b and H37 need them; D6's `partner_core` is the nearest field. A request to the generator, not a world draw |

**One overlap to settle.** The housing note puts a conflict cost `k × (h − 1)` on each regime; the generator puts `crowd_cost` on each person. Proposal: the regime sets `k`, and each person's cost is `k × (h − 1) × crowd_cost / mean(crowd_cost)`, so the regime's mean is unchanged and people differ around it.

**Tastes come from the generator; circumstances come from the world.** Wage draw, starting savings, job, starting housing and starting friend graph are drawn by the world from the calibrated distributions, seeded per world, independent of the persona. Otherwise a generator that ties taste to income would bake in a finding.

## 3. Relationships

### Bonds

The H42 bond, unchanged: one record per pair with `c`, `h`, strands per direction (eight strands: the six from L-C plus fun and advice, as the author confirmed), `origin`, `last`, `down_until`. Agent friends are other agents; background friends are stubs, 4 per agent at N = 24 (8 at N = 6, as the design says). Stub pleasure is reported beside the everyone-counts total, as decided.

A bond carries **no rights**. Rights and duties live in contracts.

### Contracts

A contract is one record:

| Field | Meaning |
|---|---|
| `parties` | two or more agent ids |
| `kind` | partner, co-residence, bill agreement, prenup, care, credit (layer c), commons membership (layer g) |
| `cards` | the terms, as ADICO cards compiled by the existing compiler (src/mar/compile.py), so the gate, the lint and the English surface all work on them |
| `exit` | notice weeks; the fallback for the pot and items (F0 to F5); who keeps the unit; how joint debt splits; what a leaver owes or is owed |
| `schedule` | its reading cadence (13 weeks by default) and any trial window (H41's `h41_trial`) |
| `depends` | other contracts this one assumes (for example, a care contract that assumes co-residence) |

**A household is three contracts and a unit:** co-residence (who lives there, exit terms), a bill agreement (the hybrid's agreement generalized to `n` shares: proportional to income, equal, or a negotiated split), and optionally a shared pot. A **prenup** is the exit block of a partner or co-residence contract, agreed at formation. **Bill agreements** are standing transfers, as the hybrid's are now: they need no foresight and take no time unit.

**Multi-partner networks (H37).** An agent may hold several partner contracts, in different households or none. Two things are new:

- **Consistency across contracts.** At formation and at every amendment, the gate checks the agent's whole set of contracts together, with z3, as it checks one card set now: no two contracts claim the same time unit or the same money, no exit term is unpayable once another exit has fired. This is H37's "checked for consistency across contracts", made a step anyone can run.
- **Spillover.** When a contract ends, every contract that `depends` on it is read at once, as a triggered reading for its parties. That is where H37 expects isolated contracts to fail, so it must be reachable: a planted network where it fires is a check (f3).

### Households of many

Nothing in the pair world's machinery is two-person by necessity except roles A and B. They become agent ids. Bills are shares over members. Formation of a household of more than two is a sequence of joins: an existing household admits a new member only if every member says yes (unanimity, as now; a majority rule is a world dial for H37 and H36, not a default).

### The romance-norm dials (H38b)

Three dials, set world-wide, tested one at a time:

| Dial | Off | On |
|---|---|---|
| **Nesting** | partners may live apart (LAT is an ordinary option) | a partner contract carries a co-residence term |
| **Romantic priority** | a partner's invitation and a friend's compete on value | a partner's invitation for a time unit is accepted before any friend's, and a friend's visit yields when they clash |
| **Exclusivity** | an agent may hold several partner contracts | at most one |

All three on, with N = 2, is the pair world's "pairing". Each dial is a **rule** (a card the gate enforces) by default. H38's dial of **pressure** (stigma, reward, withdrawal, exit stigma) stays a separate dial that can sit on top. Whether the romance norms should also be modeled as pressure instead of rules is question 3.

## 4. The economy and housing

### The minimal economy (economy-calibration.md, section 7)

| # | Parameter | Value | Source |
|---|---|---|---|
| 1 | Wage per unit | `exp(z)`, `z ~ N(0, 0.55)`, clipped below at 0.61; median 1 | BLS OEWS May 2025 (fit ours) |
| 2 | Hours | full-time 4 units, part-time 2; 17% of jobs part-time; hours change only by changing jobs | BLS CPS |
| 3 | Layoff | 0.0023 a week | JOLTS |
| 4 | Job finding while searching | 0.06 a week (median spell about 11 weeks) | CPS flows |
| 5 | Quit | an agent may quit, then search | design |
| 6 | Unemployment insurance | 40% of lost pay for 26 weeks, to 30% of job losers | Minneapolis Fed; NELP |
| 7 | Rent | solo unit `R1` = 30% of median full-time pay; other necessities `0.9 × R1` a person | JCHS target; BLS CEX |
| 8 | Savings at start | 37% near zero (under a third of a week); the rest lognormal, median 5 weeks of own pay | Fed SHED, SCF |
| 9 | Work enjoyment | 31% of jobs mildly positive, 52% mildly negative, 17% clearly negative; sizes ASSUMED | Gallup shares; Bryson & MacKerron direction |
| 10 | Basic income `T` | 19% of median full-time pay a week, to each adult, no work test | Hoynes & Rothstein level |
| 11 | Flat tax `τ` | balances the treasury each year (about 29% before hours change) | our arithmetic |

**One correction carried over.** The couple's place costs **1.15 × R1**, from HUD's two-bedroom against studio, not the economy note's 1.5 or the pair world's 1.67 (housing-research.md, section 2; limit 11). 1.67 stays as a sensitivity arm so old results can be set beside new ones.

**Sensitivity arms for H40:** rent capture `c` in {0, 0.5, 0.78}; unfunded `T` with `τ` = 0; `T` paid into the household pot.

**Runway** is measured, never set: weeks an agent could live alone on own pay, UI, savings and basic income, minus debt service, before missing a bill. "Held by money" uses threshold `k` = 8 weeks (ASSUMED).

### Debt (debt-left-ideas.md, section 4)

| Regime | Parameters | Default |
|---|---|---|
| D0 no borrowing | none | the H40 market arm |
| D1 market credit | interest `r`; limit `L = m × weekly income`; minimum payment `p` | `r` 20% a year (300% sensitivity), `m` 4, `p` 2% a week |
| D2 credit plus jubilee | D1's, plus period `J`; anticipation on or off; the limit shrinks over the last `J/4` | `J` 364 weeks (104 sensitivity) |
| D3 mutual credit or time bank | floor `−L` per member; no interest; unit money or time | `L` 4 weeks of the median bill |
| D4 debtors' union | D1's, plus threshold `q`; concession `c` | `q` 0.3; interest halved or 20% written down |
| D5 no accounts among friends | givers give only above `g` weeks of their own runway; radius the friend graph | `g` 8 |

**How borrowing fits the hybrid.** The debt note's prerequisite was agents that plan past one week. The hybrid meets it only for big choices, so borrowing is one: **opening a credit line** (amount, terms) is chosen by sampled futures. Once open, a shortfall draws on it automatically and repayment is a standing transfer, like the bill agreement. The routine never chooses to borrow. This follows the review's rule: long-horizon money lives in agreements, not in a one-week agent's foresight.

Joint debt splits at exit by the contract's exit terms. Every arm reports the debt a leaver carries out.

Order, as the note suggests: D0, D1 and D5 first; D2 to D4 as variations on D1.

### Housing (housing-research.md, section 3)

**Four regimes, each set world-wide**, each with four parameters:

| Regime | Cost per person | Contact from housing | Privacy or conflict | Exit |
|---|---|---|---|---|
| A costly solo | solo `R1`; couple `1.15 × R1` total | none | none alone | new solo unit at `R1`; moving cost one month's rent; 0 to 4 weeks to find |
| B cheap solo | micro-unit `0.75 × R1`; couples as A | none | small space cost `s` a week (0 as a side arm) | as A at `0.75 × R1` |
| C shared houses | a room at `0.48 × R1` (3 people) or `0.43 × R1` (4) | 2 free contact chances a week with each housemate | `k × (h − 1)` a week | another room, same or other house; moving cost one week's room rent |
| D cohousing | unit `0.75 × R1` plus common `0.10 × R1` | 1 chance a week with each resident; shared meals | low; one meeting a month | rented: like B, vacancy 5%; owned: sell at a cost and a delay |

**Housing stock.** The world holds a fixed set of units, sized so the regime's forms are available and about 5% stand vacant (ASSUMED). Vacancies are a trigger for movers. In regime C, housemates are **chosen** through the shortlist where possible, and vacancies left unfilled after 4 weeks are filled by the world from searchers (strangers). That answers the housing note's first question with both, chosen first; it is a default the author can change.

**Housemates are not friends by default.** A housemate tie is an H42 bond like any other; free contact chances only make building it cheap (housing check 6).

## 5. Amenities (H43)

docs/notes/amenities-research.md landed while this spec was being drafted. Its layer fits the slot below, which was written first as an interface so that the research could fill values without changing the world. What follows is the interface, then what the note puts in it, then the two places they need settling.

### The interface

**An amenity is a record:**

| Field | Meaning | In the amenities note |
|---|---|---|
| `kind` | what it is | Green, Library, Table, Workshop, Hall; Common house in housing regime D |
| `access` | open; members (a commons-membership contract); fee | open by default; members for the Common house |
| `capacity` | uses a week before congestion | `K`: 6 seats, 3 benches, 8 or 10 places |
| `serves` | the hedonic parts one use supplies | `v_a` 0.02 to 0.04 a use; amplified by `1 + α` (0.2) when a medium or close tie is there |
| `contact` | meeting chances per use, and incidental encounters with existing ties | `m_a` 0.2 to 0.6 added to H42's meeting rate; `h += 1` for ties present together; faster early bonding at Hall and Table |
| `making` | whether it lowers the cost of making | Library and Workshop halve the tool cost |
| `runway` | whether use lowers living costs | Table 10%, Library 3% of the other-necessities line |
| `cost` | who pays | M1 public levy, M2 dues and rota, M3 voluntary |
| `stock` | condition, worn by use and restored by maintenance | `Q_a` in [0, 1]; wear `ω` per user; closes below 0.3 |
| `cards` | governance | booking, cleanup share, contribution log, graduated sanctions, monthly meeting, as options |

**Four calls:**

- `offer(agent, week)`: the routine actions it makes available this week, valued by v2's one-week arithmetic like any other action;
- `use(agent, action)`: the hedonic parts, the contact events, the wear;
- `maintain(agent, amount)`: restores stock; a routine action, valued the same way;
- `close_week()`: congestion, wear, stock; returns its measures (uses, unique users, contacts made, stock, who maintained).

### What the layer must do (layer e checks)

The amenities note's ten checks (section 3 there), of which 5, 7, 8 and 9 can fail. Two of them matter most for the evaluator: check 9 (held stays fall through runway and own ties, and do not fall with both channels off) and check 8 (at the highest capitalization `κ`, the poorest can lose while users gain). Plus one from this spec: contact through an amenity reaches the friend network only through H42's bond update, never as a free friendship (the note's check 2 says the same in its own terms).

### Two things to settle

- **Capacity was sized for 4 to 6 agents.** The note's Green is "effectively unlimited for 4–6 agents", and Library has 6 seats. At 24 agents those capacities make every amenity congested from week 0. Proposal: scale every `K` by N / 6 (ASSUMED), so congestion means the same share of the population at any N, and keep the note's values as the N = 6 configuration.
- **Ties that follow their origin.** The note gives ties formed at an amenity `origin` = amenity, and in the breakup split such a tie follows the partner who met it there. That is a change to H42's split rule (which goes by history and by who introduced whom). It belongs in layer (e) behind the amenity flag, so that layer (b)'s checks do not move.

## 6. Measurement

### What the evaluator needs

The README's rule: pleasure and freedom together; a trade-off is not a win. Every result reports both sides, for **every agent** (everyone counts), with stubs in their own column.

**Pleasure side**

- **Pleasure** on the saturating scale (ADR 0019, knee 0.8): per agent-week, mean over agents and weeks. The old capped line beside it while ADR 0019's one round lasts.
- **Lived pleasure**: the same with every term a norm pays by fiat taken out (H38's reward, stigma and exit stigma; any reward or stigma a later dial adds). The third formation check showed why: under the hybrid, pressure's +0.011 was almost all reward paid.
- **Suffering**: offsettable and non-offsettable, each clipped to [0, 1] as now.
- **Distributions**: per-agent lifetime means, their 10th, 50th and 90th percentiles; the share of person-weeks at or above 0.95; and **the worse-off**: the lowest agent in each world, the bottom fifth, and the lower member of each household (ADR 0019, item 6, generalized).

**Freedom side**

- **Held share**: the stay test, generalized. At every reading of every co-residence or partner contract, for each removable exit cost, would the agent leave with it removed? A reading is held by pressure, by money (runway under `k`), by isolation (the shadow network of H42), by debt, by housing lock-in (owned units), or by contract exit terms. Reported per cause and in total. By the author's decision, staying for lack of anywhere to go counts toward held share.
- **Liberty with powers**, computed **per household, pairwise**: for each member, the compatible futures over `k` = 2 steps with the other members' moves enumerated one at a time and everyone else at their policy. A world-wide enumeration grows as actions to the power of N and cannot run. Snapshots at weeks 0, 52 and 104 on 8 sampled agents per world (cost, section 8). By the author's decision, a partner shrinking someone's network (a contact veto, pressure to drop a friend) counts as interference; self-chosen withdrawal does not.
- **Exit support** `E_i`, its companions `N_i` and `E_care`, and the isolated share (H42, section 7).
- **Runway** per agent at every reading; the share under `k`.
- **Holdout leverage**, generalized to contracts of many: per contract, the largest share any party can force by a no-deal exit minus its contribution share, over the pot and items (exit-fallbacks-design.md). Mean over contract-weeks, and the maximum per world.
- **Domination by network loss**: the closeness an agent lost to a partner's interference, from the shadow network.

**Statistical unit.** A world-seed, not an agent: agents in one world are not independent. Paired comparisons across arms use the same population and seed (common random numbers). Intervals are bootstrapped by world-seed.

### The observer, extended

Schema `mar.observer/2`. Same switch, same guarantee (reads only, makes no draw, writes nothing the world reads; pinned fingerprints with it on and off). The changes:

- **Roles become agent ids** (`a00` to `a23`; stubs `s00-0` and so on). `pair_key` becomes `world_key`: population hash, seed, arm-invariant, so paired arms line up.
- **Kept, re-keyed**: run, week, decision, consent, state, friend, trust, word, flow, together, item, rule, sanction, commit, veto, replay, stay, end.
- **`reading` becomes `bigchoice`**: kind, chooser, options with each future's value, the chosen, the yardstick, the sub-world's members, and under audit the held-out full-world values.
- **New tables**: `bond` (on change: `c`, `h`, tier, origin), `household` (membership changes, unit, contracts), `contract` (made, amended, read, breached, ended; parties, cards, exit terms; consistency-check result), `job` (hire, layoff, quit, offer, hours), `housing` (vacancy, search, move), `credit` (open, draw, pay, arrears, jubilee, write-down), `amenity` (use, congestion, wear, maintenance), `shortlist` (candidates with `m`, the top 3, and under audit every candidate's rollout value), `norm` (layer g: proposals, votes, adoptions, mined de facto rules), `measure` (held per cause, liberty, exit support, runway, leverage, per snapshot).
- **Size.** `state` is 24 × 156 = 3,744 rows a run. `decision` rows grow with N and are sampled: all agents on 10% of weeks by default.

### Model versions (ADR 0020)

Every result names its version on one line, with one tag per layer:

`model: nworld/1 · hybrid-N/1 · sat · w=persona · N=24 · gen=pop/v1 · friends · econ=market|ubi · debt=D0 · housing=A · amen=none · romance=nest1,prio1,excl1 · pressure=L0`

- Each layer is behind its own flag, off by default; with a layer off, every pin of the layers below reproduces byte for byte.
- Each layer's design note carries a "Findings this could move" list.
- Pair-world findings reproduced in layer (a) are run under two versions (pair world and `nworld/1`), so they can earn "holds across versions". Everything first run in the many-agent world starts as "single-version".

## 7. Build order

Each layer has known-answer checks. **A layer's checks must pass before the next layer starts**, and before any hypothesis it unlocks is preregistered. A check that fails is reported as a failure; the design changes only where the check shows it disagrees with what the design says (as the hybrid prereg allows), never to tune a number until it passes.

### (a) The pair world ported to N agents

What it builds: agent ids for roles; households as sets; bill agreements with `n` shares; local sub-world rollouts; staggered readings and triggers; the shortlist; liberty per household, pairwise; observer schema 2; the timing probe.

| # | Check | Passes if |
|---|---|---|
| a1 | **Port, exact.** N = 2 plus Friend C, fixed pair, v1 agents | every pinned pair-world fingerprint reproduces byte for byte (a compatibility mode that maps roles to ids and keeps stream order) |
| a2 | **Port, statistical.** The same, hybrid agents, the third formation check's 120 pairings × 4 seeds, G-L0 and G-L4 | formation, weeks together, P1 to P3 inside the published intervals |
| a3 | **No interaction, no change.** N = 24 as 12 pairs with no cross-pair contact | each pair's outcomes have the same distribution as 12 pair-world runs |
| a4 | **Local rollouts are faithful.** PT-H with held-out futures played in the full world | H1 within ±0.010 a week, H2 ≥ 0.80, H3 ≥ 80% |
| a5 | **Shortlist recall.** Audited readings with every candidate rolled out | the rollout's best is in the top 3 in ≥ 90% of readings where it matters (margin ≥ 0.010), and the mean loss is ≤ 0.002 a week |
| a6 | **PT-R** on the N-world's routine | within 0.02 of v2 on T1 to T4; T5 in 0.8 to 1.25 |
| a7 | **Timing probe** | per agent-year and per run, against section 8 |

Unlocks: no new hypothesis. Reruns of the third formation check and H41 in the port configuration, so their findings can be labelled across versions.

### (b) The friend network (H42)

What it builds: the friend-network design's five steps, with agent friends and stubs at N = 24.

Checks: the design's twelve (friend-network-design.md, section 10), of which 4, 6, 9 and 10 can fail; plus (b13) with `friends` off, every layer-(a) pin reproduces; plus (b14) the `+10%` cost bar.

Unlocks: **H42**. H38's withdrawal rerun with friends as agents (the question the third formation check left open: does withdrawal only lower pleasure when the friends' loss is counted?).

### (c) The economy, makers and debt

What it builds: jobs, wages, UI, rent under regime A, savings, the treasury; makers (the H39 module, ported: making competes with paid work for time units); credit lines and D0 to D5.

| # | Check | Target (direction or rough size, not a fit) |
|---|---|---|
| c1 | job finding from unemployment | about a quarter a month |
| c2 | unemployment spells | median about 11 weeks, a long tail |
| c3 | rent burden under regime A | about half of single agents over 30% of income |
| c4 | near-zero buffers | about a third of agents, at start (an input) and still at week 104 (a check) |
| c5 | UBI arm, no capture | hours down a few percent, participation down a few points, partners' hours down about as much (ORUS) |
| c6 | couple earnings split | report the shares against Pew's; no target is imposed, and a large miss is noted |
| c7 | D0 reproduces the market arm exactly; D1 with `m` = 0 equals D0; D3 balances sum to zero every week | exact |
| c8 | D1 with `r` = 0 and a shock that reverses: pleasure at least D0's; at payday `r` with a permanent shortfall: debt-to-income ratchets up | directions (Karlan & Zinman; Melzer) |
| c9 | D2: cancelling dead debt changes nothing; cancelling serviced debt raises later runway | directions (Kluender et al.; Dobbie & Song) |
| c10 | makers off reproduces the economy pins; makers on with work enjoyment set to 0 reproduces H39b-style time trade-offs in the port configuration | exact; descriptive |

Unlocks: **H40** (market against funded UBI, with the narrowed claims the author approved). The **debt regimes** as H40 sub-arms. **H39b-N** (makers when making costs paid work), crediting rules as plain rules for now.

### (d) Housing

What it builds: the housing stock, the four regimes, vacancies and search, owned tenure, housemate shortlists.

Checks: the housing note's seven (rent burden; cost drives co-residence from B to A; owned cohousing ends fewer pairings than rented; living alone is not isolation once contact is controlled; crowding distress rises with `h` without collapsing pleasure; housemates are not automatic friends; cheaper exit, fewer held), plus (d8) regime A at 1.67 reproduces layer (c) with the old couple bill.

Unlocks: the **housing comparison** (four regimes, same agents and seeds), and **H41-N** for its housing aids (cheap solo housing, basic income as an exit aid).

### (e) Amenities

What it builds: the amenity layer of section 5, with the amenities note's values, capacities scaled by N / 6, funding regimes M1 to M3 with fixed protecting norms (no adoption yet), and the capitalization arm.

Checks: the amenities note's ten, plus (e11) with `amenities` off, every layer-(d) pin reproduces.

Unlocks: **H43**, its pleasure, contact and exit half, with maintenance norms fixed per run (the note's M1 to M3). Its "whether they last" half, with norms adopted by the users, waits for (g).

### (f) Contracts and romance norms

What it builds: contracts as records with cards and exit terms; consistency across one agent's contracts; dependent-contract readings; multi-partner contracts; the three romance dials; LAT; prenups and crediting rules as contract terms.

| # | Check | Passes if |
|---|---|---|
| f1 | all three dials on, N = 2, fixed partner | reproduces layer (a)'s port |
| f2 | nobody wants more than one partner | exclusivity on and off give identical worlds (it can bind nothing) |
| f3 | a planted network where one exit breaks a dependent contract | the dependent contract is read at once; with consistency checking on, the planted inconsistency is refused at formation |
| f4 | a planted pair of contracts claiming the same time unit | the gate refuses the second |
| f5 | LAT under nesting off | chosen by some pairs whose rollout says it beats both co-residence and apart; never under nesting on |
| f6 | prenup terms | reproduce the pair world's F5 behaviour in the port (exit-fallbacks.md: a prenup mostly filters who forms) |

Unlocks: **H38b** (each dial alone), **H37** (contract networks, isolated against cross-checked), **H41-N** in full (LAT, prenups, trial periods, better information with partner choice), **H39** crediting rules as contract terms.

### (g) Norm emergence

What it builds: rule proposals from a fixed, declared grammar of candidate cards; adoption by members' big choices on shared futures; sanctions as routine actions; beliefs about each other's compliance (section 9); the miner over N-world traces.

| # | Check | Passes if |
|---|---|---|
| g1 | an exact toy commons (N = 3 to 4, two candidate rules, Bayesian compliance beliefs) | the simulation's adoption shares and stock paths match the exact solve in sign and order |
| g2 | beliefs frozen | the stage detector's signals differ from beliefs on; if they do not, emergence is not about learning (section 9) |
| g3 | an imposed seed, no proposals | reproduces layer (e) with those cards |
| g4 | the stage detector on a planted series with known stages, and on a shuffled null | finds the planted stages; finds none in the null at its stated rate |
| g5 | mined de facto rules on a world with known imposed cards | the miner recovers them (as the V2 instrument calibration does now) |

Unlocks: **H36**, in the narrowed form of section 9. **H43**, its "whether they last" half.

### What is runnable after each layer

| After | Newly runnable |
|---|---|
| (a) | reruns of the formation check and H41 across versions |
| (b) | H42; H38 withdrawal with friends as agents |
| (c) | H40 (market against UBI); debt arms; H39b-N |
| (d) | housing regimes; H41-N housing aids |
| (e) | H43 (pleasure and contact) |
| (f) | H38b; H37; H41-N in full; H39 crediting as contracts |
| (g) | H36 (narrowed); H43 (commons durability) |

Layers (c) and (d) do not depend on (b) in code, and could be built in parallel once (a) passes. Every hypothesis runs with only the layers it needs on: H40 does not need romance dials.

## 8. Cost

### The baseline

From the pair world: the hybrid costs about 20 s for a 156-week, two-person run without audits, about 34 s with liberty (hybrid-agent.md, formation-check-3.md). That is about **3.4 s per agent-year**, nearly all of it in rollouts. One simulated week of a two-person household costs about 1.4 ms (v2b; the hybrid's routine is v2). A world copy without its log costs about 0.6 ms.

Working it for one agent in the many-agent world, layer (a): 4 readings a year, about 2.5 options each (stay, leave, sometimes a shortlisted candidate), K = 4 futures of 52 weeks in a sub-world of about 2.5 agents at about 0.7 ms per agent-week. That is about 0.9 s a reading, about **3.6 s per agent-year**, in line with the measured 3.4 s. The lived world itself is small: 24 agents × 0.7 ms × 52 weeks is under a second a year.

**One run, N = 24, 156 weeks** (72 agent-years): about **4 to 5 minutes** without audits. Liberty snapshots on 8 agents at 3 weeks add about a minute.

**One experiment**: 40 world-seeds × 5 arms = 200 runs, about 15 to 20 CPU-hours, so **4 to 5 hours on 4 workers**. The world-seed is the unit, and 24 agents per world give far more units of behaviour than one pair, so 40 seeds is a reasonable first guess; each prereg's power check sets the real number.

### Per layer

| Layer | Multiplier on (a) | Why | Run, N = 24 | 200-run experiment, 4 workers |
|---|---|---|---|---|
| (a) port | 1.0 | readings with local rollouts | 4 to 5 min | 4 to 5 h |
| (b) friends | 1.1 to 1.2 | bond updates; the design's 10% bar | 5 to 6 min | 5 to 6 h |
| (c) economy, makers, debt | 1.4 to 1.7 on (b) | job offers and quits as big choices (about 2 more a year), credit lines | 7 to 10 min | 6 to 9 h |
| (d) housing | 1.5 to 2 on (c) | moves as options; regime C's sub-worlds are 3 to 4 agents | 11 to 20 min | 9 to 17 h |
| (e) amenities | 1.05 | routine actions and a weekly stock update; no rollouts (the amenities note's own estimate) | about the same | about the same |
| (f) contracts, romance | 1.5 to 3 on (d) | multi-partner agents' sub-worlds span 2 households (6 to 8 agents); more contracts to read | 17 to 60 min | 14 to 50 h |
| (g) norms | +2 to 3 min a run | a proposal's futures are played once, in the whole commons, and every member reads its own outcome from them | full stack 20 to 60 min | 17 to 50 h |

Audits are extra and one-off: PT-H in layer (a) with held-out full-world futures costs about 45 s per audited choice (16 futures × 3 options × about 1 s for a full 24-agent year), so 200 audited choices are about 2.5 hours.

Most hypotheses do not need the full stack. H40 runs at (c) cost; the housing comparison at (d); H38b and H37 need (f), but at N = 6 for pilots they cost a quarter.

### What would make it infeasible

- **Local rollouts fail check a4.** Then rollouts need the whole world, about 10 times the cost at N = 24: about an hour a run at layer (a), 10 days an experiment. Fallbacks, in order: a larger sub-world (two steps of neighbours), K = 2 (PT-H re-passed), N = 12.
- **The shortlist fails check a5.** Rolling out more candidates costs linearly in how many: top 6 doubles the reading cost.
- **Contract networks connect.** If multi-partner chains link most of the world, a sub-world grows toward N. Cap it at the chooser's households and their direct partners, with the rest as background, and test the cap like a4.
- **Liberty.** A full per-household enumeration grows as actions to the power of members. Pairwise, as in section 6, is required, not optional.
- **The bar.** A confirmatory experiment should fit in about a day on 4 workers (about 100 CPU-hours). If the layers a hypothesis needs cost more than about 30 minutes a run, cut N to 12 for that hypothesis and say so, rather than cut seeds below the power check.

## 9. Risks, against the step-back review's avoid-list

### Another patch cycle

**The risk.** Seven layers, dozens of checks, and every failed check tempts a fix that moves the next result. That is how H38 went +0.021, −0.046, −0.003.

**The guard.**
- The agent is frozen at layer (a) as `hybrid-N/1` (section 2). A change to it is a new version, with every finding it could move listed and rerun side by side under the stop rule.
- Each layer's free parameters are fixed in its design note **before** its checks run. Inputs taken from data (hazards, wage spread) are inputs; targets the world should hit (rent burden, spells, layer checks) are checks. A missed check is reported and the layer is labelled "misses X"; it is not tuned until it hits.
- One declared calibration pass is allowed per layer, on named free parameters only (for example, a contact rate with no source), written up before any hypothesis run, and then frozen.
- Every hypothesis gets its exact toy model first. The world has to agree with it, or the disagreement is explained, as the third formation check did.

### Rollouts that see the real future

**The risk is bigger here than in the pair world**, because there are more futures to leak.

| Leak | Guard |
|---|---|
| The shock schedule | every future resamples shocks (as the hybrid does now) |
| Other agents' actual future choices | never replayed: outside the sub-world they are base rates; inside it they choose in the future by their own policy, on the sampled future |
| Market events (vacancies, offers) | drawn fresh per future from the rates, not from the lived world's list |
| A candidate's true traits | from layer (f), a signal that sharpens with history (section 2) |
| Commons compliance (layer g) | others' compliance is sampled from the chooser's beliefs, not from their true policy |

A test for each: a rollout built from a world whose lived schedule has been replaced with a different one must give the same forecast distribution.

### Mixed units

**The risk.** Every new action (visit a named friend, make, use an amenity, sanction, propose a rule) is a chance to write a constant. The pair world's propose-only scores (leave 0.9, gift 0.12) did exactly this.

**The guard.** Every ranked score is v2's one-week value or the hybrid's one-week fork. The shortlist's `m` is v2's own close. A grep test fails the build if a literal utility appears in agent code.

### Norm emergence from scripted heuristics (H36)

**The risk, stated plainly.** H36 claims norms emerge in stages, and that a storming phase makes them more durable. If the stages come from hand-written adaptation rules, they are those rules' properties. The step-back review said H36 needs agents whose behaviour changes with experience, measured against the model's own answers.

**What the hybrid gives, and what it does not.** The hybrid's behaviour already responds to state (trust, closeness, needs, the commons stock), and its big choices respond to sampled futures. But it does not learn: nothing it believes about other people changes with what they do, except trust. A "conflict spike then repair" in such a world would come from the stock and the trust rule, which are hand-written.

**A proposal for a narrowed H36.**

1. **One learning component, declared and exact.** Each agent holds a belief about each other agent's compliance with each adopted card: a Beta count, updated by what it observes. That is the only experience-dependent state added. It is standard and has a known answer.
2. **Rules come from a fixed grammar, not from agents writing them.** Candidate cards are a declared list of ADICO cards (use limits, maintenance duties, sanctions, who may use). Any member may propose one at a reading; adoption is a big choice by every member on shared sampled futures in which others' compliance is drawn from the voter's beliefs; the rule passes by a declared vote (majority by default, unanimity as an arm).
3. **Sanctions are routine actions** valued by the one-week fork, so whether anyone sanctions is the model's arithmetic, not a script.
4. **The exact toy model first** (check g1): a commons of 3 or 4 Bayesian agents with two candidate rules, solved exactly. The world must match it.
5. **The decisive control** (check g2): rerun with beliefs frozen at their prior. Whatever pattern appears in both is not emergence from experience; it comes from the grammar, the vote rule and the hedonic arithmetic.

**What this can test.** Which rules a group of these agents adopts in a commons; whether adopted sets survive a shock (a layoff wave, a funding cut to an amenity); whether groups whose beliefs started further from the truth adopt rules later and keep them longer. Those are claims about the model's arithmetic, a declared grammar and Bayesian updating, which is what they should be.

**What it cannot test, and I think should not claim.** That norms emerge "in stages", or that "storming" causes durability. A stage detector can be run as a descriptive, against Tuckman and punctuated-equilibrium patterns as the hypothesis row asks. But any stage it finds in this world is a property of Beta updating and a vote rule, and the storming arm (an imposed seed that suppresses storming) changes the rules, not only the storming. With scripted agents, I do not see a version of the storming claim that is not circular. H36 as written belongs with LLM agents with memory, its own later arm, and on the AI agents track's terms. This is question 4.

### Two risks not on the avoid-list

- **The frozen background** (section 2) is a new kind of misforecast: the world does not react to the option in the rollout. Check a4 measures it. If it passes only for some choices (likely: moves and partner changes touch more people than staying), the per-kind numbers are reported, and choices that fail are labelled.
- **Selection, in housing and romance.** If agents choose their regime or their norms, the comparison mixes who chose with what it does (housing-research.md, section 4). Regimes and dials are set world-wide, never chosen, except as a declared arm.

## 10. What a small model can and cannot claim

**It can show mechanisms.** For example: if a basic income lifts the poorer partner's runway above the hold threshold, fewer readings are held by money, given these agents and costs. Or: if exclusivity blocks a bond two agents would value, and that bond covered strands nobody else covers, exclusivity lowers pleasure with everyone counted, given these strands.

**It can compare rules inside itself.** Same population, same seeds, one dial changed, judged on pleasure and freedom together. These are its strongest claims.

**It can check itself against known directions.** Every layer's checks. A layer that misses its known directions should not be read.

**It can say whether a pair-world finding survives other people.** Layer (a)'s reruns, and every hypothesis rerun in the many-agent world, give findings a second version, so "holds across versions" can mean something.

**It cannot say anything about real people, real economies or real romance.** 24 scripted agents with assumed preferences are a village in a model. Every welfare number is a property of the model (limits 1, 5, 6, 10).

**It cannot test general-equilibrium effects.** No firms, no prices, no land market, no credit supply response. Rent capture, employer responses and lender behaviour are rules with stated sizes, run as sensitivity arms.

**It cannot settle funding.** A world of 24 can balance a flat tax inside itself. That says nothing about whether a country can.

**It cannot say what is typical.** The population comes from a generator with stated spreads, not from a sample of anyone. Shares (of held households, of multi-partner agents) are shares in this population.

**It cannot speak to abuse.** Exit support and runway are motivated by research on coercive control and on leaving. The model has no coercion beyond holding, vetoes and pressure.

**Its emergence claims are about its own arithmetic.** See section 9.

## 11. Questions for the author

1. **Population.** 24 agents by default, 6 for pilots and exact-model cross-checks, 48 only as a scaling arm. Earlier notes assumed 4 to 6. Is 24 right, or do you want a bigger world at about 4 times the cost per 100 agents?
2. **Romance norms: rules or pressure?** Should nesting, romantic priority and exclusivity be **rules** (the gate blocks a second partner) or **social pressure** (a cost, like H38's dial, that a person can pay and break)? They test different things: rules test the norm's content, pressure tests holding. The spec makes them rules, with H38's pressure as a separate dial on top.
3. **What agents know about a new partner.** The pair world gives full information. The proposal makes it a signal that sharpens with time spent together, so H41's "better information" aid becomes a dial. Is that the default you want?
4. **H36.** Accept the narrowed version (rule adoption and durability among agents that learn about each other's compliance; stages only as a descriptive), and move the storming claim to an LLM arm later? Or keep it as written and wait?
5. **Debt first.** The debt note asks which debt comes first. This spec follows its suggested order: no credit, market credit, and no accounts among friends (D0, D1, D5). Is debt between people who know each other (Graeber's tally, linked to H39) the one you most want, or debt to an outside lender?
