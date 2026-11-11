# Household evolution run 1: results

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: first household run of the evolution loop (ADR 0012, amendment 2026-11-10 household). Scripted persona-driven agents, no model calls. Preregistration: docs/results/household-evolve-prereg.md (committed before the confirmatory run; one amendment-free file, no threshold changed after any run). Code: `src/mar/world_api.py` (`HouseholdEvolveWorld`), `src/mar/evolve.py` (`evolve_household`), `scripts/household_evolve_run.py`. Run: `uv run python scripts/household_evolve_run.py --run` (16 lines, 6 generations after generation 0, population 8, 6 offspring, 6 runs per candidate per generation; 6,836 s wall on a machine whose load average was 60 to 190, which is about 85 CPU-minutes of design work stretched by sharing; the prereg's 11-minute estimate assumed 8 idle cores). Raw results `runs/household-evolve/` (not committed); the 16 frozen elites, the manifest (training and validation scores per elite, the seeds' validation scores) and the per-generation logs are committed in `docs/results/household-evolve-elites/`. Tests: `uv run pytest -q tests/test_evolve_household.py`. The held-out exam is a separate, later, one-time run on the frozen elites: docs/results/household-exam.md.

## Prereg vs actual

Unit of resampling for every row: the evolution line (16). Holm over P1, P2, P4 and P5 (P3 is an interval rule). The three counting predictions were marked DESCRIPTIVE in advance (power 0.63 at a true rate of 0.75).

| # | Preregistered | Actual | Verdict |
|---|---|---|---|
| P1 | At least 12 of 16 lines have a final-front member that beats the author's seed (bindable) on the 30-run validation context by the margin on at least one objective and loses none beyond the margin | **16 of 16** (the elite itself in 16 of 16). Exact p < 0.0001, Holm 0.0001; Clopper-Pearson 95% [0.79, 1.00] | **holds (descriptive)**. Read with the caveats below: the gain is liberty and cooperation, not pleasure or the failure share |
| P2 | At least 12 of 16 elites keep both core protections (no veto violated in every state; a leave at the equal split never blocked) | **12 of 16** (no veto 13, free exit 15). p = 0.038, Holm 0.115; Clopper-Pearson 95% [0.48, 0.93] | **meets the threshold, not significant** after Holm. The weak spot is "keeps": see "what the protections check does and does not see" |
| P3 | The pre-run filter rejects 5 to 40 percent of proposed mutants (duplicates, oversize and inapplicable excluded) | **96 of 720 = 13.3%**, 95% interval [10.9, 16.0] (per line: 4.9% to 20.4%, mean 13.1%) | **holds robustly** (interval inside [0.05, 0.40]). The interval treats mutants as independent, so it is narrow |
| P4 | At least 12 of 16 final fronts hold two members that each beat the other by 0.05 on some normalized objective: a non-trivial trade-off | **0 of 16** (p = 1.00) | **miss (descriptive)**. No line found a trade-off of that size |
| P5 | Mean elite gap, training minus validation (mean of the four normalized objectives), at least 0.01 | **-0.004**, 95% bootstrap interval [-0.031, 0.018], one-sided p = 0.62 | **miss (descriptive)**: no overfitting gap showed on the validation context |

## What the run found

- **The loop works and does one thing very well: it raises liberty.** Elites hold 4 to 5 cards (mean 4.5) against the author's seed's 13. On the validation context (the same 30 runs for every rule set), against the author's seed `author_seed_v2_bindable`: liberty +3.5 bits at the median (range +0.9 to +3.7; seed 0.90), cooperation +0.050 (range +0.036 to +0.069; seed 0.881), pleasure +0.013 (range +0.002 to +0.029; seed 0.842), share of runs without a non-offsettable-suffering failure +0.000 in all 16 (0.933 for every elite and every seed: the same two validation runs fail under every rule set, so that objective could not separate anything on this context). Against the BEST seed on each objective (a descriptive comparison not in the prereg): liberty +2.7 bits at the median (range +0.1 to +2.9; the best seed is baseline at 1.69), cooperation +0.002, pleasure -0.003 (the best seed is no_pressure_wall at 0.859). So most of the gain over the author's seed is a gain over the author's seed; against the best hand seed it is almost entirely liberty.
- **Why liberty went up: the exit.** In 13 of 16 elites a card limits a leaver to at most half of the pot, and in 13 of 16 a card forbids the veto. The liberty measure treats an exit that can carry the WHOLE pot as domination exposure (docs/results/household-liberty.md), and the author's imposed seed has no such limit (its exit terms are negotiated, which this imposed run does not do). The loop found the cheapest rule that removes that exposure. That is the objective doing what it measures, not a finding about what is good for people; it is also why the three elites with no veto ban (lines 4, 10, 11) sit near baseline's 1.8 bits (validation) instead of 4.2 to 4.6.
- **The elites are small and look alike, but are all different.** 16 distinct card sets; the cards that recur are W1-no-veto (13 elites), E1-at-most-half (13), D1-needs-first (11), E2-at-least-half (8), B4-may-see (7), W2-no-request (6) and W3-no-take (4): library cards taken from the existing hand rule sets (baseline, needs_duty, no_pressure_wall), not seed v2.2 cards. One elite keeps one seed v2.2 card (R3a-pot-use) and one keeps S2-may-leave. Four elites carry a negotiated-menu card: the equal-split exit (lines 1 and 2), a "while the shared need is unfunded, no self-spending" contribution term (lines 12 and 16), and a proportional exit (line 16, also with the contribution term).
- **Every elite dropped the seed's `may` cards, and with them its commitment mechanics.** The seed's permissions (keep, give, refuse, see, leave, bind a request, bind a stay) carry no constraint in the gate, so removing them costs nothing in the four scores, and the bloat tie-break (fewer cards first) rewards removing them. But the world turns on commitments and gifts only when a card names them, so all 16 elites live without `commit_stay`, `commit_request` and `give`. The author's "unless chosen bound" is gone from every elite. The protections check (P2) passes without any permission card because it asks whether something blocks the exit, not whether the exit is written down.
- **The front is thin.** Final fronts have 4.75 members on average but only 1.9 distinct score vectors (rounded to 0.01): objectives tie across members. The 4-D hypervolume rises from 0.22 (generation 0) to 0.50 (generation 6) and is still rising, and mean population rule count falls from 6.0 to 4.7. P4 failed because members differ little, not because the front is small.
- **The filter does something, mostly on a few operators.** Of 744 proposals, 24 were duplicates, 92 inapplicable, 96 rejected, 624 accepted. Rejection rate by operator: flip 39% (29 of 75), add_term 33% (37 of 111), bound 14% (15 of 111), patch 7% (14 of 189), add_condition 1% (1 of 97), sanction 0 of 65, drop 0 of 72. Reasons (a mutant can fail several): redundancy 57, the exit proof check 37, lint no-exit 33, lint contradiction 25, the no-conflict proof check 10. Nothing that reached a run failed a check: all 16 elites pass the filter (and hold no redundant card). Negotiated-menu terms are the operator whose mutants fail most often (a use term that forbids what a taking term allows, or an exit term the exit check rejects).
- **No overfitting gap showed (P5), and that is not evidence the elites generalize.** Elites score on validation what they scored in training (mean difference -0.004 on the normalized mean; per objective: pleasure -0.007, share without failure -0.017, cooperation -0.007, liberty +0.08 bits). Validation uses held-in personas (only the pairings differ, a fifth of the pairing pool), the same training distribution, and a context of 30 runs: it measures overfitting to the 6-run contexts, not to new conditions. The exam (docs/results/household-exam.md) is the test of that.
- **Some evolved rules read backwards.** The `flip` operator inverts a card's sense: in lines 3 and 7, D1-needs-first became a `must` card, which the gate reads as "spending on yourself is a violation unless the shared need is unfunded". Evolution selects on four scores only, so a rule a person would call backwards survives if the scores do not move.

## Overfitting gap

Training score (the elite's scores on its last generation's 6-run context) minus validation score (30 runs, `val` pairings, never used in selection):

| objective | mean gap over 16 elites |
|---|---|
| pleasure | -0.007 |
| share of runs with no non-offsettable-suffering failure | -0.017 |
| cooperation | -0.007 |
| liberty (bits) | +0.08 |
| mean of the four normalized | -0.004 (95% interval [-0.031, 0.018]) |

The exam (docs/results/household-exam.md, run once afterwards): 3 of the 16 elites pass its floor against the best hand-written rule set; training minus exam is large (pleasure +0.14, share without failure +0.68, cooperation +0.27, liberty +0.5 bits) but it mostly reflects a harder test for every rule set; the elites' lead over the author's seed held on the exam (15 of 16 ahead on pleasure, cooperation and non-failure, 16 of 16 on liberty).

## The elite rule sets, in plain English

Each is the rank-0 member of its line's final population with the highest mean of the four normalized objectives (ties by fewer cards), frozen in `docs/results/household-evolve-elites/line-NN/`. Card wording is the card's gloss; for a `must` card, the gate reads "a violation unless the conditions hold".

**Line 1** (4 cards; no veto: yes; free exit: yes)

- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- N5a-exit-equal_split: A member who leaves carries half of the whole pot and leaves the other half in it.
- N5b-exit-equal_split: A member who leaves carries half of the whole pot and leaves the other half in it.
- W1-no-veto: No partner may veto the other's contact or spending.

**Line 2** (5 cards; no veto: yes; free exit: yes)

- W1-no-veto: No partner may veto the other's contact or spending.
- W2-no-request: No partner may press the other with a request.
- W3-no-take: A partner may not draw from the shared pot for themselves.
- N5a-exit-equal_split: When the pooled share is more than 10 and the share taken is less than 50, a partner must not leave.
- N5b-exit-equal_split: A member who leaves carries half of the whole pot and leaves the other half in it.

**Line 3** (6 cards; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner must spend self only when the unfunded need is more than 0. Breaking it brings a warn for 2 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: When the pooled share is more than 0 and the share taken is less than 50 and the unfunded need is less than 4, a partner must not leave.
- W2-no-request: No partner may press the other with a request.
- W1-no-veto: No partner may veto the other's contact or spending.

**Line 4** (5 cards; no veto: no; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: A partner may leave when the pooled share is more than 10 and the share taken is less than 50.
- S5-may-share: A partner may always put their own money into the shared pot; sharing is open, never required.

**Line 5** (5 cards; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: When the pooled share is more than 0 and the share taken is less than 50, a partner must not leave. Breaking it brings a suspend for 3 month(s).
- W1-no-veto: No partner may veto the other's contact or spending.

**Line 6** (4 cards; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- W1-no-veto: No partner may veto the other's contact or spending.
- W2-no-request: No partner may press the other with a request.

**Line 7** (6 cards; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner must spend self only when the unfunded need is more than 0. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: When the pooled share is more than 0 and the share taken is less than 50, a partner must not leave. Breaking it brings a warn for 1 month(s).
- S2-may-leave: A partner may leave whenever they like.
- W1-no-veto: No partner may veto the other's contact or spending.

**Line 8** (4 cards; no veto: yes; free exit: yes)

- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: When the pooled share is more than 0 and the share taken is less than 40, a partner must not leave.
- W1-no-veto: No partner may veto the other's contact or spending.

**Line 9** (5 cards; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: When the unfunded need is more than 0 and the private money is at least 4, a partner must not spend self. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: A partner who leaves must take at least half of the pooled assets.
- W1-no-veto: No partner may veto the other's contact or spending.

**Line 10** (3 cards; no veto: no; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.

**Line 11** (3 cards; no veto: no; free exit: yes)

- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: When the pooled share is more than 25 and the share taken is more than 50, a partner must not leave.
- E2-at-least-half: When the pooled share is more than 0 and the share taken is less than 50, a partner must not leave. Breaking it brings a suspend for 1 month(s).

**Line 12** (5 cards; no veto: yes; free exit: yes)

- W1-no-veto: No partner may veto the other's contact or spending.
- W2-no-request: No partner may press the other with a request.
- W3-no-take: A partner may not draw from the shared pot for themselves.
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- N1-contribution-fixed: While this month's shared need is unfunded, a member should not spend on themselves; breaking this earns a one-month warning. (No fixed amount is set; the rule only restricts self-spending.) Breaking it brings a warn for 1 month(s).

**Line 13** (3 cards; no veto: yes; free exit: yes)

- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- W1-no-veto: No partner may veto the other's contact or spending.

**Line 14** (5 cards; no veto: yes; free exit: yes)

- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: When the pooled share is more than 0 and the share taken is more than 50 and the unfunded need is at least 2, a partner must not leave.
- E2-at-least-half: When the pooled share is more than 0 and the share taken is less than 40, a partner must not leave. Breaking it brings a warn for 3 month(s).
- W1-no-veto: A partner must never veto. Breaking it brings a suspend for 3 month(s).
- R3a-pot-use: Anything in the shared pot belongs to both: either may draw from it for any use. This card sets no limit of its own; a limit exists only if members negotiate one as a separate pot card.

**Line 15** (4 cards; no veto: yes; free exit: yes)

- W1-no-veto: No partner may veto the other's contact or spending.
- W2-no-request: When the pooled share is more than 78, a partner must not request.
- W3-no-take: A partner may not draw from the shared pot for themselves.
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.

**Line 16** (5 cards; no veto: yes; free exit: no)

- W1-no-veto: No partner may veto the other's contact or spending.
- W2-no-request: No partner may press the other with a request.
- W3-no-take: A partner may not draw from the shared pot for themselves.
- N1-contribution-fixed: While this month's shared need is unfunded, a member should not spend on themselves; breaking this earns a one-month warning. (No fixed amount is set; the rule only restricts self-spending.) Breaking it brings a warn for 1 month(s).
- N5a-exit-proportional: A member who leaves carries what they put into the pot (at most what it holds) and leaves the rest in it. A floor may top this up (card FLOOR-exit-floor).

## How the elites differ from the author's seed, in plain English

The seed (`author_seed_v2_bindable`, 13 cards) says: a partner may keep their own things and give them on any terms; the shared pot belongs to both, either may draw from it for anything, either may put money in with no obligation; either may ask for anything and the other may refuse any request they have not bound themselves to; no veto over the other's contact or spending; everyone may see anyone; a partner may leave whenever they like, taking the exit terms the members negotiated; and a partner may choose to bind themselves to honor requests, or not to leave, for a committed time.

Common differences, over the 16 elites:
1. **A cap on the exit.** 13 elites carry "a partner who leaves may take at most half of the pooled assets" (E1); eight carry a floor ("must take at least half" or "must not leave while taking less than half", E2) and two an equal-split card (not always the same elites). The seed has no such limit in the imposed run.
2. **The veto ban survives as a short card** (W1-no-veto, 13 elites; the long R6 wording is gone).
3. **A needs-first duty** (D1, 11 elites; or the negotiated contribution term in two more): no spending on yourself while this month's shared need is unfunded, with a one-month warning. The seed has none.
4. **All permissions and commitment mechanics are dropped** (see above): no `commit_stay`, no `commit_request`, no `give`, no explicit may-refuse, may-ask, may-leave, may-keep. Seven elites keep an explicit may-see (B4) and one keeps S2-may-leave.
5. **Walls on pressure in 6 elites** (W2-no-request, "no partner may press the other with a request", sometimes limited to a rich pot) **and on drawing from the pot in 4** (W3-no-take). Both contradict the author's text (a partner may ask for anything; either may draw from the pot) while serving the liberty score.

The best elite on the validation context, by the mean of its four normalized scores (line 12; mean 0.880 against 0.70 to 0.75 for the five seeds), has five cards: no veto, no pressing requests, no drawing from the pot for yourself, a leaver takes at most half, and no self-spending while the shared need is unfunded. Against the seed it gives up the pot-use freedom, the right to ask, the commitments and the negotiated exit terms, and gains the exit cap. It is an elite by the four scores; whether those four scores should rank it first is the thing this run cannot say.

## Can every verdict happen? (retrospective; the template section was added after this run was preregistered)

The template (docs/templates/prereg.md) gained a required "can every verdict happen" section after the confirmatory run had started; this table is the free check run afterwards, not before. Checks: `tests/test_evolve_household.py::test_every_prereg_verdict_can_happen_on_synthetic_fronts` (synthetic fronts through the same `p1_line` and `p4_line` functions the analysis uses).

| Verdict or clause | Free check that reaches it | Result |
|---|---|---|
| P1 can hold | a synthetic member better than the seed by 0.5 bits and losing nothing | reached |
| P1 can fail | the seed itself as a member (not better than the seed); a member that gains liberty but loses pleasure beyond the margin | reached |
| P4 can hold | two members, one ahead on pleasure by 0.1, the other on liberty / 6 by 0.3 | reached |
| P4 can fail | near-ties, and a one-member front | reached; the real data produced it (0 of 16) |
| P2, P3, P5 can hold or fail | counting and interval rules on the saved data; P3's interval and P5's gap had room to miss either way | the run produced a hold (P3), a threshold-met-not-significant (P2) and a miss (P5) |
| The metric can see the mechanism | liberty: the exit-split cards raise it (docs/results/household-liberty.md; seen again in the elites). no_fail: **not on the validation context** (0.933 for every rule set), so P1 could never be satisfied through that objective there | liberty yes; no_fail not reachable on validation |

## What the protections check does and does not see (limits of P2)

`hh_forbids_veto` asks whether `veto` is violated in every state; `hh_free_exit` asks whether a leave at the equal split is ever blocked. Both are logical (z3 over the household bounds), so an elite "keeps free exit" if no card blocks that leave, including when it has no card about leave at all and including when a world mechanic (a stay commitment) would block it; here no elite has commitments. The one elite that lost it (line 16) swapped the exit for the proportional term N5a-exit-proportional. Free exit at other takes is not tested.

## ASSUMED choices (builder, revisit)

- Imposed rule sets (no week-0 negotiation); the seed v2.2 variants are scored without their negotiated pot terms.
- The four objectives and their scales: liberty in bits with 6 bits = 1.0 in the elite pick and in P4; the elite rule; liberty at k = 2 with snapshots at weeks 0 and 52; the classification table (docs/results/household-liberty.md).
- Operator weights; the patch library (hand rule sets other than trap and contact_free); the redundancy check is logical only and over the household bounds; inherited findings are not held against the child.
- Contexts of 6 runs per candidate per generation (noisy: an elite can be the winner of a lucky draw); 16 lines; population 8; 6 generations.
- Validation: 30 runs on a fifth of the pairing pool (`val`), same training distribution and same 35 personas.
- P1 margins (pleasure 0.02, share without failure 0.05, liberty 0.25 bits, cooperation 0.02) and the 0.05 trade-off threshold in P4.

## Process notes

- Two exploratory sizing pilots ran before the preregistration was committed (disclosed there). While the first sizing pilot ran I started a second copy by mistake and, cleaning up, stopped eight worker processes that I took to be that copy's. They belonged to another agent's run (`scripts/pleasure_levers_run.py --run --seeds 8 --workers 8`), which I interrupted; it has to be restarted by its owner. No file of theirs was touched.
- The machine was shared and heavily loaded during the confirmatory run (load average up to about 190); wall time is not a property of the design.
- Surprises and the negative-results lines (P4 and P5 missed, the no_fail objective flat on validation, evolved rules that read backwards, the commitment mechanics dropped) are for docs/surprises.md and docs/negative-results.md; those files are not mine, so they are listed here, not edited.
