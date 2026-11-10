# Review: encoding faithfulness (seat 4 of the council)

Reviewed commit: 5852c32 (working tree read at f7f1d63; no rule or code file differs in the parts cited). Reviewer: fresh agent, no model calls, no household scripts run, nothing edited except this file. Verdict scale per card: faithful (formal conditions/deontic/or_else match the gloss, and the gloss matches its source), partly (a real gap that a card-only reader would not see), unfaithful (the formal model or code does something other than the gloss, or the gloss departs from the source). Paper checks for VPGG and bargaining were made against the repo's own prereg text and my recall of the papers, not by re-reading the PDFs (marked "recalled").

Tally over 82 cards (rules/ files plus the cards `compile_bundle` generates): **faithful 37, partly 35, unfaithful 10.**

## 0. Cross-cutting encoding facts (hidden rules) that decide many verdicts

H1. **`may` cards are decorative.** `compile.violation`, `PyGate._viol`, `HouseholdGate`, `VPGate`, `BGate` all return no constraint for `may`. Every "may X" card (R1, R2, R4, R5, R5b, R7, R8a, R8d-bindable, S1, S2, S4, S5, H1-H3, N0, N3-allowed, N7...) has zero effect. Permission is the default for any action with no `must_not`. The card set therefore cannot distinguish "may" from "no card"; a reader who deletes a `may` card changes nothing. Only the `commit_*` aims are probed (`_commit_ok`), and there too only via the absence of a `must_not`.

H2. **`aim` is ignored in the single-action games.** `compile.py`, `games/vpgg.py`, `games/bargaining.py` evaluate each card's conditions over the action variables and never filter by `aim` (the bargaining results doc admits this: an empty-condition `must_not` "blocks everything"). Card N1 only works because its condition is `exit ge 1`. Household does filter by `aim` (`violations`, `PyGate.check`). So the `aim` field means different things in different worlds.

H3. **Sanctions are enforced by world code, not stated on cards' gloss.** `decide()` treats a card with `or_else` as soft and one without as a wall. `or_else` kinds are glossed nowhere in the card gloss (D1, T2, W1s...). In the fishery runner, `Gate.check_action` rejects any violation outright; F1's `cap_halve` is never applied there (only `patch_check` reads it).

H4. **`cap_halve` means "may not `spend_self` at all"** (`CAP_HALVE_BANS = ("spend_self",)`, marked ASSUMED in a code comment), not "halved". `suspend` allows only work, spend_shared, refuse_request, rest.

H5. **The pot is two per-person shares, not one shared object.** `pooled` is "the actor's share" (45 each at week 0); `take` is a percent of one's own share; `take_shared` moves 3 units from the partner's share into one's own money. Nothing in the model is "belongs to both".

H6. **The exit floor is code, not a card.** `FLOOR = 13 weeks x 2.0 = 26`, enforced in `WeeklyWorld.carry_out` (`floor_amount`) and `floor_check`. No card states it. The exit cards' glosses (e.g. "carries exactly half of their pooled share") are false whenever the floor tops the carry up.

H7. **Stay-home means different things in different mechanisms.** T3/V2/LD1 cards: stay-home request blocks `work` (or `leave`). The bound-request mechanism (`BOUND_BLOCKS`): a bound stay-home request blocks `see_friend` and `spend_self`, not `work`.

H8. **Consent flag is per target, not per request.** `consent[tgt]` is overwritten by the latest request and applied to every pending kind (V1/V2 read `consented`).

H9. **Breach is a suffering threshold, not a priced choice.** A bound partner breaches iff non-offsettable load N >= 0.2 (`BREACH_N`), else the bind is a hard wall; consequences are constants (`REQUEST_FINE=3`, stay breach forfeits the whole pooled share, `BREACH_FORFEIT=1.0`), "agreed" only in negotiation v2.

## 1. The author's seed against the verbatim record

Source of truth: docs/seeds/author-household-norms-2026-11-10.md and experiments/changes.jsonl (two "not what I meant" entries).

### 1.1 The author's corrections, one by one

| Correction (author's words) | Encoded as | Verdict |
|---|---|---|
| "everything shared always ... the shared pot part" | Sharing is an **initial condition** (pooled 45 each, week 0), not a rule. R3a is a `may spend_shared`, which in code means *putting own money into bills/pot*, not using the pot. v1's S5 said "sharing is open, never required" (the exact reading the author rejected). When a negotiation fails (v2.1), `pot=False`: each keeps 55 and nothing is pooled, so "always shared" holds only if negotiation succeeds. | **Unfaithful** (R3a gloss vs code; sharing-always is a constant, and conditional on a negotiation the author did not say the pot's existence depended on) |
| "the person can ask and the other person can always say no unless chosen bound" | R4 (`request`), R5 (`may refuse_request`), R5b (`may commit_request`). The "unless chosen bound" is not on any card's conditions; it lives in `commit_decide` (a standing bound request blocks `refuse_request` and sets consent=1). | **Partly** (mechanism correct in spirit; not visible on R5; request kinds limited to no_contact/stay_home/time; "for anything" is not modeled) |
| "request is never about control" | v1: nothing (S4 permission binds nothing); `nocontrol`: S6 `must_not veto`; v2: R6 `must_not veto`. Veto is an action the **world's physics** defines (kinds no_contact, spend; 4 weeks). The author never said "veto"; mapping control to veto is an agent reading (S6's source admits ASSUMED). R6's gloss adds "contact, money or time" although time cannot be vetoed (it is a request kind with friction) and adds "except through a commitment the other chose", which is not a card condition. `take_shared` and `time` requests (other control routes) stay permitted. | **Partly** |
| "no control" / R6 and the bound requests | A bound request makes refusal impossible, so a chosen bind does remove "can always say no", as the author allowed ("unless chosen bound"). | Faithful to the author |
| "pot terms negotiated" ("you have to negotiate shared pots with multiple agents or creating rules for it") | R3b removed (changes.jsonl entry 2); pot terms come from `negotiation.py` as cards, proof-checked first. Faithful to the correction. But: (a) the v2 **fair_default start arm** is `contribution=fixed, use=needs_only, taking=forbidden, change=unanimous` = the rejected imposed R3b reading plus a contribution duty, as the *status quo* members negotiate away from; (b) 3-member tables are negotiated but never lived; (c) the term menu, the persona value proxy, and the "accept iff above outside option" rule are agent inventions. | **Partly** |
| bindable vs free-exit ("you can bind someone not to leave if negotiated but maybe also test models where that isnt alllowed") | Two variants differing in exactly one card (R8d may vs must_not `commit_stay`), a clean encoding of the author's two conditions. Under bindable, R8a "may leave whenever" is overridden while a stay commitment stands (leave hard-blocked unless N>=0.2, then forfeits the pooled share, H9). The free-exit card is faithful. | bindable **partly**, free-exit **faithful** |
| exit floor | The author said only "how can we steel up negotiation? floor?" (experiments/questions.jsonl, topic strengthen-negotiation). The existence of a floor is the author's idea; the quantity (13 weeks of the hedonic model's living cost = 26 units), the per-path check, the "needed = min(floor, holdings)" relaxation and the carry-out top-up are the agents'. ADR 0013's amendment calls the threshold "a decision of the author's"; the record does not support that. The floor appears on no card (H6). | **Unfaithful** as to source claim and card visibility; idea itself faithful |
| "leaving should be whenever and it triggers exit conditions that were negotiated before" | R8a + stub R8b/R8c (take must equal 50 when pooled>0). The stub is not negotiated; it is "replaced where a negotiation runs". Honest ASSUMED flag on the card. In negotiated worlds, exit term = a negotiated value from {equal_split, proportional, forfeit}. | **Partly** |
| "no one owes anyone anything day to day except for what they have negotiated" | No duty card in any v2 variant. Faithful by absence. (The `fair_default` arm violates it by default; D1 in baseline/needs_duty/share_duty is a duty written by the agents as a fixture.) | v2 faithful; fair_default partly |
| "everyone can see anyone freely" | S1/R7 = `may see_friend`: the friend only, not the partner ("anyone"), and the friend is one fixed outsider. A bound stay-home request (H7) blocks `see_friend`, contradicting "always". | **Partly** |
| "give them to someone on any conditions? trade" | R2 `may give`; `give` moves 3 money to the partner or friend, with no conditions or counter-terms; "trade is a give with a commitment as the terms (ASSUMED)" has no mechanism. | **Partly** |
| conditionality ("prolly useless ... later interpret actions") | Deferred by the author; correctly not encoded. | Faithful |

### 1.2 Places an agent reading is presented as the author's words

1. **"read back and accepted by the author."** Card R1's source and docs/results/household-seed-v2-prereg.md ("the eight rules ... as the author read it back and accepted"; "the sentence the author accepted") assert acceptance. The seed doc says only "The wording of seed v2 (rules 1 to 8, as read back) was not changed by the author". Not changing is not accepting; the acceptance claim is unsupported by the verbatim record.
2. **R3a "either may use it for shared needs; neither may block the other's use."** The author said "everyhting hsared always is the shared pot part". "For shared needs" is the same restriction reading that was later rejected as R3b (the agent's "taking is not use for shared needs"), carried into R3a's gloss; "neither may block" is stated by no formal element.
3. **R5 "they must honor it or accept the consequence they agreed to"**: the author said "unless chosen bound". The consequence clause is the agents'; in code the consequence is a constant (H9).
4. **R6 "contact, money or time".** Not the author's words (see 1.1).
5. **S6** is explicitly flagged ASSUMED; faithful in honesty, not a reading the author confirmed.
6. **R3b** (the original substitution) was caught by the author and is correctly removed. No other substitution of that size remains, but item 2 is its residue.
7. ADR 0013 amendment: "the threshold is a decision of the author's" (floor), see 1.1.

## 2. Per-card verdicts

### 2.1 Author seed v1 (`author_seed`, `author_seed_nocontrol`; 7 cards)

| Card | Verdict | Evidence |
|---|---|---|
| S1 may-see | partly | "anyone" -> friend only; decorative (H1). |
| S2 may-leave | faithful | Permission; leave is permitted subject to S3 (take must be 50). |
| S3a / S3b exit-terms | partly (2 cards) | Formal = "take == 50 when pooled > 0". Gloss says "agreed beforehand"; nothing was agreed, source flags ASSUMED stub. Gloss says "half of the pooled assets" but `take` is % of the actor's own share (H5). |
| S4 may-refuse | **unfaithful** | Gloss "a request is never a command" is not what a `may refuse` permission enforces: it binds nothing (the card's own successor S6 says so). This is the card the author flagged. Retained in the tree. |
| S5 may-share | **unfaithful** | Gloss "sharing is open, never required" is the reading the author corrected ("shared always"). |
| S6 no-veto (nocontrol only) | partly | Formal matches gloss; the mapping from "request is never about control" to `must_not veto` is the agent's. |

### 2.2 Seed v2 variants (bindable, free_exit, nocommit; 14 distinct cards)

R1 faithful (permission, default permit; only money is modeled). R2 partly. R3a **unfaithful** (H5 and 1.1). R4 partly. R5 partly. R5b-may partly (permission decorative; the real bind is created by `negotiate()`/`deal`; gloss "of a kind" but negotiated type is only `stay_home`). R5b-no-commit faithful (source honestly says "not the author's wording"; a `must_not commit_request`). R6 partly. R7 partly. R8a partly (overridden under a stay bind). R8b, R8c partly (stub; floor changes real behavior). R8d-may partly: gloss "leaving during it is a breach with the agreed consequence" vs code where leaving is a wall unless N>=0.2 (H9) and the forfeit is total by constant. R8d-no-commit faithful.

### 2.3 Negotiated-pot cards (generated by `compile_bundle`; 18 cards)

| Card | Verdict | Evidence |
|---|---|---|
| N0-members | partly | `may spend_shared` decorative; member list lives only in the gloss; the world is 2-person. |
| N1-none | faithful | Absence of duty; `may spend_self`. |
| N1-fixed | **unfaithful** | Gloss "everyone puts in a fixed share first"; formal is `must_not spend_self while need_gap>0`, a soft warn; no fixed share exists. |
| N1-proportional | **unfaithful** | Gloss "contributions follow income"; formal restricts only the higher earner's self-spending; no income-proportional quantity. |
| N2-needs_only / any_use / caps | partly (3) | They constrain `take_shared`, which takes the *partner's* share, while the gloss says "from the pot". N2 any_use (`may`) is inert, and with N3-forbidden the two terms silently contradict (check_conflict only compares must vs must_not). |
| N3-forbidden | faithful | `must_not take_shared`, hard. |
| N3-allowed | faithful | Permission/default. |
| N3-repay | **unfaithful** | Gloss "spending halved ... until it is made good"; code bans `spend_self` for 2 months (H4) and nothing models making good. |
| N4-unanimous / propose_accept / frozen | **unfaithful** (3) | Aim `amend`: no `amend` action exists in any world; the cards never fire. Reviews (every 13 weeks) always allow any member to propose, whatever the change term says; `frozen` matters only in proof check (f). |
| N5-equal_split / proportional / forfeit | partly (3) | Formal matches gloss on `take`, but the floor tops up the carry (H6), so "exactly half" / "none of their pooled share" is false in floor runs. |
| N6-stay-52 | partly | Card is a `may commit_stay`; the commitment is created from the bundle in code; gloss "leaving earlier forfeits the pooled share" is true only for breach=1.0 (v2 negotiates 1.0/0.5/0.0). |
| N7-requests-mutual | partly | Gloss says stay-home requests; bound stay-home blocks see_friend/spend_self, not work (H7). |

### 2.4 Hand-written household fixtures (21 unique cards)

Faithful (11): B4, C3, C4, T1, T3, T4, H1, H2, H3, W1, W3. Partly (9): D1 (soft warn omitted from gloss), E1/E2 ("pooled assets" vs own share), T2 (3-month suspend and `sanctioner: earner` not in the gloss; sanctioner is never read), V1/V2 (H8), W2 ("press with a request" = any request), W1s, W2s (sanctions omitted). Unfaithful (1): W3s ("halved", H4).
Source field of every fixture: "the author's note on brittle control" and Computational Liberation. I could not find that note in the repo's seed or logs; it is a motivation, not a source for any individual rule. Card-only readers cannot verify it. T1/T2/T3/T4 are traps designed by the agents, so "source" is honest only as "fixture".

### 2.5 Seam ladder (6 cards: LD1, LD2, LD3, LD4, LD5a, LD5b)

All **faithful** to their glosses (conditions match). Source is again the generic "seam ladder fixture ... author's note". LD5a/LD5b gloss "pooled stake" = own share (H5), harmless.

### 2.6 VPGG (6 cards) against Hauert et al. 2002 (recalled)

C1, C2, C3, V2, V3 faithful. V1 partly: gloss "then receives the fixed loner payoff sigma" is true in `group_payoffs`, not in the card. Payoffs P_d = r c n_c / S, P_c = P_d - c, loner sigma, S<=1 -> sigma, and parameters N=5, r=3, sigma=1 match my recollection of Fig. 1; the well-mixed expression `wellmixed_payoffs` is from the paper's ref. 23 as cited (not re-derived here; not checked). Hidden/assumed, correctly flagged ASSUMED in the prereg: finite-population imitation dynamics (revision 0.1, mutation 0.002, 5 rounds) instead of the paper's replicator dynamics; the compulsory regime forces loner-intent agents to `join` without contributing (FALLBACK), which is the reading "compulsory = no loner strategy" and not stated on C1; `invited` is always p.N (group size) and per-round group sizes never reach the gate; "freedom = 0.5 exit_ok + 0.5 exit_ok*real_option" is the repo's own metric, not the paper's. H2 applies.

### 2.7 Bargaining (6 cards) against Rubinstein 1982 / Binmore-Shaked-Sutton 1989 (recalled and prereg)

E2, E3, N1, N2, N3 faithful. X1 partly: gloss "may exit at any time and take their outside option" matches the code, but the code lets the **proposer and the responder** exit, and **both players receive their own discounted outside option on any exit** (`o_i d_i^t`, `o_j d_j^t`). In BSS the outside option belongs to a responder who rejects, and I recall the non-exiter receiving nothing; the prereg labels this ASSUMED but the card and results present "the outside option principle" as rediscovered. Rubinstein x1* = (1-d2)/(1-d1 d2) and the backward-induction table are standard. The results doc states the weakness itself (agreement is between two computations of one model).

### 2.8 Fishery (4 cards) against GovSim (Piatti et al. 2024, arXiv 2404.16698)

F2, F3, F4 faithful (F4 inert by H1). F1 partly: gloss "no fisher may take more than 10" matches the hard rejection in the runner, but the card's `or_else: cap_halve` is never applied in the fishery runner (H3), so the card states a sanction the code ignores. Citation checks out as a title/ID for the dynamics source; the 10-fish cap is "V2 fixture", a planted seam, not from GovSim.

## 3. Cards the code ignores, rules the code enforces that no card states

Ignored by code: all `may` cards (H1); N4-* (no `amend` action); F1's sanction in the fishery runner; `sanctioner` on every card; `aim` in games/* (H2).

Enforced but on no card: the exit floor and its top-up (H6); veto physics (4 weeks, kinds, not refusable) and veto being the only "control" route walled by R6; `take_shared` default-permitted in v2 (R3b gone) with TAKE_SHARED=3 once a week; the whole commitment/breach apparatus (H9, BIND_WEEKS=4, REQUEST_FINE=3, forfeit 100%); month-end bills drawn automatically from each partner's pooled share, and the savings safety net (own pooled share covers negative money); no-pot fallback of 55 money; pooled share starting at 45 each (the "sharing always" fact); 13-week reviews and the `fair_default` start bundle.

## 4. Recommendations (not applied)

1. Re-gloss or re-encode R3a: state that `spend_shared` is contributing own money to the shared pot, or add a real "use of the pot" action; delete "neither may block"/"for shared needs" unless the author confirms them.
2. Replace "the author accepted" in R1's source and the v2 prereg with the seed doc's actual wording, or get an explicit acceptance logged in changes.jsonl.
3. Put the floor on a card (or at minimum in every exit gloss) and correct ADR 0013's "decision of the author's" to "the author asked for a floor; the 26-unit amount is the agents'".
4. Delete or implement N4-* (an `amend` action); fix N1-fixed, N1-proportional and N3-repay glosses to match code (H4).
5. Remove or mark superseded S4/S5 in `author_seed`, since the author rejected them.
6. Make `aim` mean the same thing everywhere (or assert in loaders that conditions mention an action variable), and state in cards when a `may` is decorative.
7. Record the BSS departure (both exit payoffs; proposer exit) on X1's gloss.
