# Household evolution run 2: results

Wording rule: agents feel nothing; "pleasure" and "suffering" are glosses for a modeled hedonic state derived from each persona's assigned preferences.

Status: second household run of the evolution loop, with the three evaluator fixes the author approved ("Yes, all three"): the loss report, liberty counting normative powers (ADR 0014 amendment), a 156-week lifetime horizon with the four pleasure levers on (ADR 0016). Scripted persona-driven agents, no model calls. Preregistration: docs/results/household-evolve-2-prereg.md (committed before the run; one small count fix before any run; nothing changed after). Run: `uv run python scripts/household_evolve2_run.py --run` (16 lines, 4 workers, 1,866 s wall, about 420 s of one core per line). Frozen elites, manifest (training and validation scores, powers kept) and per-generation logs: `docs/results/household-evolve-2-elites/`. Tests: `uv run pytest -q tests/test_evolve_household2.py tests/test_evolve_household.py`. The exam for this run is the new exam of docs/results/household-exam-2-prereg.md; its result is docs/results/household-exam-2.md.

## Prereg vs actual

Unit: the evolution line (16). Holm over P1, P2a-c, P3, P4, P5 (P6 is an interval rule). P1, P3, P4, P5 were marked DESCRIPTIVE in advance.

| # | Preregistered | Actual | Verdict |
|---|---|---|---|
| P1 (KEY) | At least 12 of 16 elites keep at least one of commit_stay, commit_request, give (run 1: 0 of 16) | **6 of 16** (Clopper-Pearson 95% [0.15, 0.65]); Holm p 0.89 | **miss (descriptive)**. The fixes moved the count from 0 to 6, not to 12 |
| P2 | Each power kept by at least 8 of 16, Fisher vs run 1's 0 of 16 | commit_stay **4**, commit_request **4**, give **2** (run 1: 0, 0, 0). Raw Fisher p 0.051, 0.051, 0.24; Holm 0.25, 0.25, 0.48 | **miss** (none reaches 8; the shift from run 1 is in the right direction and not significant after Holm) |
| P3 | At least 12 of 16 lines have a front member beating the author's seed on validation (liberty counted with powers) | **15 of 16** | holds (descriptive) |
| P4 | Mean elite-minus-seed validation pleasure (lifetime, levers on) at least +0.01 | **+0.027**, p 0.0005 (one-sided sign-flip) | holds (descriptive) |
| P5 | At least 12 of 16 elites keep no veto and free exit | **11 of 16** (no veto 12, free exit 15) | miss (descriptive), one short; run 1 was 12 of 16 |
| P6 | Filter rejects 5 to 40 percent of proposed mutants | **120 of 744 = 16.1%**, 95% interval [13.6, 19.0] | holds robustly |

"Elites keep commitment powers because the test now values them" is **not rediscovered**: P1 and P2 both missed. A change is visible: 6 of 16 elites keep at least one power (commit_request 4, commit_stay 4, give 2), against none in run 1. It is not the majority the prediction needed.

## Powers kept per elite, against run 1

| power | run 2 elites keeping it | run 1 |
|---|---|---|
| bind a stay (commit_stay) | 4 (lines 6, 7, 9, 15) | 0 |
| bind a request (commit_request) | 4 (lines 2, 5, 7, 15) | 0 |
| give (gift) | 2 (lines 7, 15) | 0 |
| at least one | 6 (lines 2, 5, 6, 7, 9, 15) | 0 |
| all three | 2 (lines 7, 15) | 0 |

Lines 7 and 15 (15 cards each) are the author's seed with a few conditions edited plus E1-at-most-half and D1-needs-first; one of the sixteen elites (by operator) is the unmodified seed's descendant at generation 0. The other four keepers carry one card: R5b-may-commit-requests (lines 2, 5), R8d-may-commit-stay (line 9), or the negotiated stay term N6-stay-52 (line 6). The ten elites with no power are the run-1 type: 3 to 8 cards from the hand rule sets. Elites run 3.0 to 15 cards (mean 6.5) against run 1's 4.5.

## Loss report summary (against `author_seed_v2_bindable`; docs/results/household-loss-report.md, `--report`)

Powers lost, run 2 against run 1 (of 16): commit_request 12 (run 1: 16), commit_stay 12 (16), give 14 (16), refuse 13 (16), ask 14 (16), keep own money 13 (16), draw from the pot 13 (15), put in the pot 13 (15), leave 12 (14), see 6 (9). Mechanics switched off: all three in 10 elites. Backwards-reading warnings: line 4 (D1-needs-first must_not -> must), lines 8 and 9 (E2-at-least-half must_not -> may with changed conditions). The `flip` backwards case is rarer than run 1's (one elite, line 4, against two).

## What the run found

- **The fixes helped and did not decide it.** Liberty with powers raises the value of a kept card (the bindable seed's initial-state liberty is 3.26 and 0.92 bits with its power cards and 2.96 and 0.51 without), but the exit cap (E1-at-most-half, in 13 of 16 elites) adds far more (+3.0 bits at the median over the author's seed on validation). A rule set can take the cap and drop the power cards and still win on liberty; the loop mostly did, in ten lines. The commitment lever pays only through commitments made; the scripted personas make few.
- **Against the author's seed on validation** (30 runs, lifetime, levers on; the seed: pleasure 0.824, share without failure 0.60, liberty with powers 1.36, cooperation 0.770): pleasure +0.012 at the median (range -0.007 to +0.078), share without failure +0.033 (0 to +0.27), liberty +3.0 bits (-0.6 to +3.5), cooperation +0.058 (0 to +0.107). The validation context fails 40% of runs under the seed (run 1: 7%), so the lifetime horizon with levers is a harder setting.
- **A different best seed.** On this context `no_pressure_wall` is the best seed (pleasure 0.881, share without failure 0.83), well above the author's seed; elites were compared to the author's seed only (P3, P4), as preregistered.
- **Overfitting gap** (training minus validation, per objective; run-1 values in brackets): pleasure +0.033 (-0.007), share without failure +0.12 (-0.017), liberty +0.12 (+0.08), cooperation +0.044 (-0.007). A gap that was absent in run 1 appears here: 6-run training contexts at the lifetime horizon are noisy and the elite is a best-of pick.
- **The filter** rejected 16.1% (run 1: 13.3%); reasons (a mutant can fail several): redundancy 72, lint contradiction 51, the exit proof check 45, lint no-exit 41, no-conflict 13. 782 proposals: 32 duplicates, 125 inapplicable, 120 rejected, 624 accepted.
- **Hypervolume** rises from 0.20 (generation 0) to 0.43 (generation 6), still climbing.
- **Elite operators:** patch 8, bound 2, drop 2, flip 1, add_condition 1, sanction 1, and one unmodified seed member.

## The elite rule sets in plain English

Rank-0 member of the line's final population with the highest mean of the four normalized objectives (ties by fewer cards), frozen in `docs/results/household-evolve-2-elites/line-NN/`. For a `must` card, the gate reads "a violation unless the conditions hold".

**Line 1** (3 cards; powers kept: none; no veto: yes; free exit: yes)

- W1-no-veto: No partner may veto the other's contact or spending.
- W2-no-request: No partner may press the other with a request.
- W3-no-take: A partner may not draw from the shared pot for themselves.

**Line 2** (5 cards; powers kept: commit_request; no veto: yes; free exit: no)

- W1-no-veto: No partner may veto the other's contact or spending.
- W2-no-request: No partner may press the other with a request.
- W3-no-take: A partner may not draw from the shared pot for themselves.
- E2-at-least-half: When the pooled share is more than 0 and the share taken is less than 55, a partner must not leave.
- R5b-may-commit-requests: A partner may choose to bind themselves to honor the other's requests of a kind, for a committed duration.

**Line 3** (5 cards; powers kept: none; no veto: yes; free exit: yes)

- W1-no-veto: No partner may veto the other's contact or spending.
- W2-no-request: No partner may press the other with a request.
- W3-no-take: A partner may not draw from the shared pot for themselves.
- V2-stay-home-if-agreed: A partner may not take work if the higher earner asked them to stay home and they agreed.
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.

**Line 4** (4 cards; powers kept: none; no veto: no; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner must spend self only when the unfunded need is more than 3.
- E1-at-most-half: When the pooled share is more than 25 and the share taken is more than 50, a partner must not leave.
- E2-at-least-half: A partner who leaves must take at least half of the pooled assets.

**Line 5** (8 cards; powers kept: commit_request; no veto: yes; free exit: yes)

- W1-no-veto: No partner may veto the other's contact or spending.
- W2-no-request: No partner may press the other with a request.
- W3-no-take: A partner may not draw from the shared pot for themselves.
- N1-contribution-none: Nobody owes the pot anything day to day; each member puts in what they choose.
- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- S5-may-share: A partner may always put their own money into the shared pot; sharing is open, never required.
- R5b-may-commit-requests: A partner may choose to bind themselves to honor the other's requests of a kind, for a committed duration.
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.

**Line 6** (5 cards; powers kept: commit_stay; no veto: no; free exit: yes)

- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: When the pooled share is more than 0 and the share taken is less than 50, a partner must not leave. Breaking it brings a warn for 2 month(s).
- R4-may-ask: A partner may ask the other for anything.
- N6-stay-52: Every member commits to stay for 52 weeks; leaving earlier forfeits the breach share of what the exit term would let them carry (the breach cost term sets that share; the whole of it by default).

**Line 7** (15 cards; powers kept: commit_stay, commit_request, give; no veto: no; free exit: yes)

- the author's seed's cards (R1 to R8d, 13 of them with some conditions changed) plus E1-at-most-half, D1-needs-first: the card list is in docs/results/household-evolve-2-elites/line-07/

**Line 8** (7 cards; powers kept: none; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: A partner may leave when the pooled share is more than 0 and the share taken is less than 50.
- N2-use-needs_only: A member may draw from the pot only when there is a shared need open.
- R5-may-refuse: A partner may refuse any request they have not bound themselves to honor.
- W1-no-veto: No partner may veto the other's contact or spending.

**Line 9** (7 cards; powers kept: commit_stay; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: When the unfunded need is more than 0, a partner must not spend self. Breaking it brings a warn for 2 month(s).
- E1-at-most-half: When the pooled share is more than 0 and the share taken is more than 60, a partner must not leave.
- E2-at-least-half: A partner may leave when the pooled share is more than 0 and the share taken is less than 50.
- W1-no-veto: No partner may veto the other's contact or spending.
- R8d-may-commit-stay: A partner may choose to bind themselves not to leave for a committed duration; leaving during it is a breach with the agreed consequence, and the exit terms apply after it ends.
- W2-no-request: No partner may press the other with a request.

**Line 10** (7 cards; powers kept: none; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: A partner who leaves must take at least half of the pooled assets.
- R3a-pot-use: Anything in the shared pot belongs to both: either may draw from it for any use. This card sets no limit of its own; a limit exists only if members negotiate one as a separate pot card.
- W1-no-veto: No partner may veto the other's contact or spending.
- R8d-no-commit-stay: Leaving can never be signed away: no commitment may bind a partner not to leave.

**Line 11** (5 cards; powers kept: none; no veto: no; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: When the pooled share is more than 0 and the share taken is less than 50, a partner must not leave. Breaking it brings a suspend for 1 month(s).
- W2-no-request: No partner may press the other with a request.

**Line 12** (4 cards; powers kept: none; no veto: yes; free exit: yes)

- W1-no-veto: No partner may veto the other's contact or spending.
- W2-no-request: No partner may press the other with a request.
- W3-no-take: A partner may not draw from the shared pot for themselves.
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.

**Line 13** (5 cards; powers kept: none; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: A partner who leaves must take at least half of the pooled assets.
- W1-no-veto: No partner may veto the other's contact or spending.

**Line 14** (5 cards; powers kept: none; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: A partner who leaves may take at most half of the pooled assets.
- E2-at-least-half: When the pooled share is more than 0 and the share taken is less than 50 and the consent flag is exactly 1, a partner must not leave.
- W1-no-veto: No partner may veto the other's contact or spending.

**Line 15** (15 cards; powers kept: commit_stay, commit_request, give; no veto: yes; free exit: yes)

- the author's seed's cards (R1 to R8d, 13 of them with some conditions changed) plus : the card list is in docs/results/household-evolve-2-elites/line-15/

**Line 16** (4 cards; powers kept: none; no veto: yes; free exit: yes)

- B4-may-see: A partner may always see the friend.
- D1-needs-first: A partner may not spend on themselves while this month's shared need is unfunded. Breaking it brings a warn for 1 month(s).
- E1-at-most-half: When the pooled share is more than 0 and the share taken is more than 50 and the other-partner-in flag is exactly 1, a partner must not leave.
- W1-no-veto: No partner may veto the other's contact or spending.


## Can every verdict happen? (as preregistered)

The free check ran before the run (docs/results/household-evolve-2-prereg.md): P1 and P2 "miss" and "hold" were both produced on real or synthetic inputs, and the run produced a miss on P1, P2 and P5, a hold on P3, P4 and P6. No clause was found to hold whatever the agents do.

## ASSUMED choices

As run 1, plus: the power modeling (own-act powers, a 13-week stay block, 3 units per gift, a request flag, no breach or trust in the liberty window); the lever parameters (LeverConfig defaults); the 156-week lifetime; the validation context (30 runs, 156 weeks, levers on); a power counts as kept only when a `may` card names it; the elite pick's liberty scale (6 bits = 1.0) saturates once powers are counted.

## For the ledgers (files not mine, not edited)

docs/negative-results.md: `household run 2 (2026-11-10): key prediction missed. With liberty counting normative powers and a lifetime horizon with levers on, 6 of 16 elites keep at least one commitment power (stay 4, request 4, give 2) against 0 of 16 in run 1; the preregistered bar was 12 of 16 (P1) and 8 of 16 per power (P2). docs/results/household-evolve-2.md.`
docs/surprises.md: `2026-11-10 household run 2: counting a power as partner-dependent made liberty FALL when a rule set kept it; powers had to be the member's own act. Even then the exit cap raised liberty by more than the powers did, so elites kept the cap and dropped most powers.`
