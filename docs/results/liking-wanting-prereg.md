# Liking vs wanting preregistration (ADR 0018 test 1, ADR 0015 template)

Status: written and committed before the confirmatory run (`scripts/liking_wanting_run.py`). Nothing here is a result. Scripted or model agents: scripted only (exact dynamic programming and two one-step rules). Model API calls: none.

Wording rule: agents feel nothing. "Pleasure", "liking" and "wanting" are glosses for modeled values (ADR 0010).

## Purpose and claim

ADR 0018 test 1 asks whether a rule set raises the pull toward more (wanting) without raising the payoff that counts (liking). The author's notes say wanting and liking "adapt differently" and that "overstimulating wanting burns out liking" (docs/notes/hedonic-technology-synthesis.md, M7 and M9). This study builds the model version 3 piece that splits the two values, the three measures the ADR names, and the flag. It then asks a comparative question, not an existence question. A loop built to diverge will diverge, so that proves nothing. The question is how much gap each environment and each rule allows: a cue-heavy, variable-reward environment against a plain one, with and without two rules that might protect against the gap (a closure ritual and a stopping rule). It also links to the horizon study (ADR 0017): acting on wanting is the greedy move, so we ask whether the lifetime optimizer avoids the trap, and how much of a wanting-greedy agent's loss is due to wanting rather than to being greedy.

What it changes: whether the evaluator can carry test 1 as a measure (ADR 0018), and which kind of rule (closure at the stop, or a dose cap) the household world should test first when the split is ported there. New claim ids are added with the results.

## Design

- **Model: `src/mar/wanting.py`, standalone.** Not the household world, for three reasons: the horizon link needs an exact solve and the household has no optimizer; other agents are editing `hedonic.py`; a new module leaves every existing result untouched by construction. Flag `WantParams.enabled`, default False. Off, wanting equals liking everywhere.
- **World.** One person, 28 days, 4 slots a day (112 steps). Each slot takes one unit of G (the cued activity: a feed, a game, a series), P (a plain activity: a book, a walk, cooking) or Q (quiet). Consecutive units of one activity form a session. Content has a natural stop every e = 2 units, the same in both environments. The day's end ends every session.
- **Liking (the payoff that counts).** G: bG x (1 - dl x hG) x (1 - ws x run). P the same with bP and hP. Q: bQ. Two clocks: within-session satiety (fast, resets each session) and tolerance h (slow: +1 at the end of a day with 2 or more units, -1 after a day with none, cap 4).
- **Wanting (drives choice for a wanting agent).** For G when a cue is present: liking + c x (1 + sig x s x (1 + variable)). Otherwise wanting equals liking. Sensitization s rises by one level per unit of G (fast) and falls by one level only after a day without G (slow decay), cap 12. Background, from memory, verify: Robinson and Berridge 1993 (incentive sensitization); Berridge and Robinson 1998; Fiorillo, Tobler and Schultz 2003 (reward uncertainty and dopamine, the reason for the variable-reward boost).
- **Environments differ only in wanting.** So liking, and therefore the lifetime optimizer, is identical in both (checked as P0).
  - plain: cue only mid-content (an unfinished episode). No cue to start a session, no cue at a natural stop, fixed reward (variable = 0).
  - heavy: cue to start (notifications), cue at natural stops too (autoplay), variable reward (variable = 1).
- **Rules that might protect.**
  - none.
  - closure: a closure ritual. The cue is removed at every natural stop (the episode is closed, no autoplay). Nothing else changes.
  - cap: a stopping rule. At most 2 units of G per day.
- **Agents.**
  - W, wanting-greedy: picks the action with the highest wanting each slot. This is acting on wanting, the greedy move.
  - L, liking-greedy: picks the highest immediate liking. This is the horizon study's greedy.
  - O, lifetime optimizer: exact backward induction on total liking over the 28 days, gamma = 1 (ADR 0017).
  - Ties go to the lowest action index (G, P, Q), declared now.
- **Measures (ADR 0018), per run.** A number that cannot be computed is reported as "not measurable here", never as zero.
  - Liking per unit of wanting-driven activity: mean liking over cued units. A cued unit is a chosen unit whose wanting exceeds its liking.
  - Liking-to-wanting ratio: total liking over total wanting of chosen units. Gap per unit: mean (wanting - liking).
  - Closure rate: the share of G sessions that the agent ended at a natural stop while the day still had time. A session the day's end cut off was ended by the clock, not at a natural stop.
  - Next-day verdict: the retrospective liking verdict on each G session, scored peak-end on liking only, (peak unit liking + last unit liking) / 2, averaged over G sessions. It never sees wanting. Peak-end: Kahneman et al. 1993, from memory, verify.
  - The flag: a run is flagged when wanting-driven activity rises while mean liking does not. "Rises" is against its matched twin, the same persona, environment, rule and agent with wanting set equal to liking. Activity is G units. Flagged iff G units > twin's G units and mean liking per slot <= twin's.
  - Divergence: mean gap per cued unit in the last week minus the first week (growth of the gap over time).
  - Liking loss: 100 x (O's lifetime liking under no rule - the run's lifetime liking) / O's. Wanting cost WC(env, rule) = loss of W - loss of L in the same cell: the part of the loss due to acting on wanting, beyond being greedy.
- **Unit of resampling: the persona.** 80 personas drawn uniformly from an ASSUMED box around the defaults (bG 6 to 10, bP 5 to 8, bQ 2 to 4, dl 0.10 to 0.20, ws 0.10 to 0.25, c 1.0 to 2.5, sig 0.05 to 0.20), seed 20261110. Every persona is run in every cell, so all comparisons are paired by persona. The solve for one persona is exact and deterministic. The interval therefore describes spread over the assumed parameter box, not sampling of people.
- **Fixed parameters, all ASSUMED** (`WantParams` defaults): bG 8, bP 7, bQ 3, dl 0.15, H 4, dose 2, ws 0.2, rcap 3, e 2, c 1.5, sig 0.12, S 12, gamma 1, cap 2 G units a day, variable 1 in heavy.
- **Descriptive extras, no verdict:** the default parameter point solved alone (deterministic table); O at gamma 0.9; a sweep of sig, c and variable at the default point; the sensitization-off losses.

## Exploratory pilot (labeled EXPLORATORY; not a result; changes no threshold after this commit)

Toy fixtures only: 7 days x 3 slots (one default persona), then 7 days x 4 slots and 14 days x 4 slots with 12 personas, persona seed 999. The confirmatory config (28 days, 80 personas, seed 20261110) was not run before this commit. Disclosure: the model was changed after looking at toy output, in three ways, all before any prediction was written.
1. Sensitization was saturating in under two days, so its cap went from 8 to 12 and sig from 0.25 to 0.12 (box 0.05 to 0.20).
2. The first flag compared the last week with the first. In the heavy toy runs the wanting agent was at full use from day one, so "rises over time" never fired. The flag now compares against the matched liking twin.
3. A session cut off by the day's end at a length of 2 or 4 was counted as closed. It is now "ended by the clock".

What the 14-day toy showed (12 personas, mean and sd of the paired quantity):

| Quantity | Pilot mean | Pilot sd | Source |
|---|---|---|---|
| WC heavy - WC plain (no rule), points | 16.5 | 8.6 | scratchpad toy, not kept |
| WC heavy none - WC heavy closure | 19.6 | 7.5 | same |
| WC heavy closure - WC plain none | -3.2 | 5.6 | same |
| W loss heavy cap - W loss heavy closure | 14.5 | 4.5 | same |
| O loss under cap | 8.4 | 2.2 | same |
| W loss heavy none - W loss heavy cap | 5.2 | 7.7 | same |
| W loss heavy none | 44.0 | 9.3 | same |
| wanting share of W's loss, heavy | 0.34 | 0.15 | same |
| O cued units / W cued units, heavy | 0.47 | 0.06 | same |
| WC plain none | -0.8 | 0.9 | same |
| closure rate plain W - heavy W | 0.50 | 0.09 | same |
| next-day verdict plain W - heavy W | 1.37 | 0.68 | same |
| closure rate heavy W, closure - none | 0.47 | 0.03 | same |

The toy is half as long as the confirmatory run, so these are guides to spread, not effect estimates.

## Power check

Computed with `seeds_for_margin(sd, effect - margin)` (closed form, two-sided 0.05, 80% power) from the pilot, where the effect beyond the margin is what the test must detect. Each test is a one-sided paired permutation test of (quantity - margin) against 0.

| Prediction | Margin | Pilot effect beyond margin | Pilot sd | Personas for 80% power | Personas chosen |
|---|---|---|---|---|---|
| P3 | 5 | 11.5 | 8.6 | 5 | 80 |
| P4a | 10 | 9.6 | 7.5 | 5 | 80 |
| P4b | 3 (upper) | 6.2 | 5.6 | 7 | 80 |
| P5a | 5 | 9.5 | 4.5 | 2 | 80 |
| P5b | 2 | 6.4 | 2.2 | 2 | 80 |
| P5c | 2 | 3.2 | 7.7 | 46 | 80 |
| P6a | 20 | 24.0 | 9.3 | 2 | 80 |
| P6b | 0.2 | 0.14 | 0.15 | 10 | 80 |
| P6c | 0.7 (upper) | 0.23 | 0.06 | 2 | 80 |
| P6d | 3 (upper) | 3.8 | 0.9 | 2 | 80 |
| P7a, P7b, P7c | 0.2, 0.5, 0.2 | 0.30, 0.87, 0.27 | 0.09, 0.68, 0.03 | 2 to 5 | 80 |

80 personas covers the hardest row (P5c, 46) with room for a smaller effect at 28 days. Cost: about 10 minutes of CPU, no money. The solve is exact; the only randomness is the persona draw.

## Predictions

Every comparison is paired by persona. "Test" is a one-sided paired permutation test (Monte Carlo, 20000 sign flips, seed 0) of the stated quantity minus its margin. Interval: 95% percentile bootstrap over personas (10000 resamples, seed 0). Rates get a Clopper-Pearson interval. Correction family: Holm across every row with a test (P3 to P8b, 15 tests), alpha 0.05.

| ID | Quantity | Comparison and threshold | Test |
|---|---|---|---|
| P0 | O's lifetime liking in plain/none, plain/closure, heavy/none and heavy/closure | identical for every persona (the environments and the closure ritual change only wanting) | deterministic check |
| P1 | Control: wanting set equal to liking (c = 0) | for every persona, environment and rule: gap per unit exactly 0, liking-to-wanting ratio exactly 1, cued units 0 (so liking per cued unit is "not measurable here"), and W's plan identical to L's | deterministic check |
| P1b | Control: flag off (`enabled = False`) | the same as P1; and on the horizon study's default table, `wanting_greedy_policy` with no wanting table gives the same plan and value as `horizon.greedy_policy` for gamma in {0.5, 0.9, 1} and horizons {4, 26} | deterministic check (test) |
| P2 | Control: sensitization off (sig = 0, cue on) | divergence within 1e-9 of 0 for every persona, agent W and O, both environments, where measurable | deterministic check |
| P3 | Environment: WC(heavy, none) - WC(plain, none), points | mean >= 5 | permutation |
| P4a | Closure ritual: WC(heavy, none) - WC(heavy, closure) | mean >= 10 | permutation |
| P4b | Closure ritual brings heavy back to plain: WC(heavy, closure) - WC(plain, none) | mean <= 3 | permutation (lower side) |
| P5a | Stopping rule protects less than closure: W loss(heavy, cap) - W loss(heavy, closure) | mean >= 5 | permutation |
| P5b | The stopping rule costs the optimizer: O loss(heavy, cap) | mean >= 2 | permutation |
| P5c | The stopping rule still helps the wanting agent: W loss(heavy, none) - W loss(heavy, cap) | mean >= 2 | permutation |
| P6a | Horizon link, size of the trap: W loss(heavy, none) | mean >= 20 | permutation |
| P6b | Horizon link, wanting share: WC(heavy, none) / W loss(heavy, none), per persona | mean >= 0.2 | permutation |
| P6c | Horizon link, the optimizer avoids the pull: O cued units / W cued units, heavy, none | mean <= 0.7 | permutation (lower side) |
| P6d | In the plain environment the loss is myopia, not wanting: WC(plain, none) | mean <= 3 | permutation (lower side) |
| P7a | Closure rate, W: plain/none - heavy/none | mean >= 0.2 | permutation |
| P7b | Next-day verdict, W: plain/none - heavy/none | mean >= 0.5 | permutation |
| P7c | Closure rate, W in heavy: closure - none | mean >= 0.2 | permutation |
| P8a | Flag rate, W, heavy/none | >= 0.8 | exact binomial against 0.8, one-sided; Clopper-Pearson |
| P8b | Flag rate, W, heavy: none minus closure | >= 0.4 | permutation on the paired 0/1 differences minus 0.4 |

P6b drops a persona whose W loss is 0 or less (share not measurable) and reports how many were dropped. A test whose quantity is "not measurable here" for every persona is reported as such and scored missed.

Effect sizes reported for every comparison: mean difference with interval and Cohen's d of the paired differences.

## Verdict rule

A row holds robustly when the point estimate meets the threshold, the 95% interval lies inside it, and the Holm-adjusted p is at most 0.05. A row whose point meets the threshold but whose interval crosses it, or whose adjusted p is above 0.05, is "holds but CI crosses threshold": weak support, not a confirmed hold. P0, P1, P1b and P2 are pass or fail.

Reading. If P3 and P4a hold, the cue-heavy environment allows a gap that the plain one does not, and closing the stop removes most of it. If P5a holds, a dose cap is a worse protection than a closure ritual in this model, because it also takes liking from those who do not need protecting. If P6a to P6c hold, the lifetime optimizer avoids the wanting trap and a sizable share of the wanting agent's loss is the wanting, not the greed.

## Not testable by design

P0, P1, P1b, P2 (deterministic checks). The default-point table, the gamma 0.9 run and the sensitivity sweep (descriptive).

## Limits stated now

- One person, one cued technology, one plain alternative, one quiet option. No partner, no household, no money.
- Every parameter is assumed. The persona box is assumed. Intervals describe spread over that box, not sampling of people.
- Wanting is modeled as liking plus a cue term. Real incentive salience is not additive to liking, and sensitization in the literature is about drugs and cues over weeks, not a feed over days.
- The environments differ in three things at once (trigger cue, autoplay, variable reward). The study does not separate them; the descriptive sweep varies variable alone.
- The wanting agent is fully greedy on wanting. Real people mix wanting and liking. A mixed agent is not tested.
- The next-day verdict uses peak-end on liking. That is one choice of a lagged liking check; the ADR does not fix it.
- The cap rule sets the cap equal to one content unit (2), so its closure rate is close to definitional. Closure under cap is reported but not predicted.

## Amendments

None yet.
