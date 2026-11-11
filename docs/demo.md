# Five-minute demo

You talk in Claude Code; the rules-lab skill drives `mar`. Scripted agents only: no model calls, no cost. Each step below is something you can say, the command it becomes, and what you should see. `uv run python scripts/demo_check.py` runs the same five steps non-interactively (about 20 seconds) against a scratch copy of the rules.

| You say | Becomes | You see |
|---|---|---|
| 1. "Show me my seed rules." | `mar household show --variant author_seed_v2_bindable` | Every rule in plain English with its gloss, and the lint verdict (PASS). |
| 2. "Run my seed with the Anchor and the Wanderer." | `mar household run --variant author_seed_v2_bindable --pair anchor,wanderer` | A report opens in the side panel, then 2-3 sentences: spiral, pleasure, offsettable vs non-offsettable suffering, trust, freedom, how many runs ended apart. |
| 3. "Try this: the shared pot can only be used for shared needs unless both agree." | `mar household card add --variant <new name> --base author_seed_v2_bindable --id R9-... --attribute partner --deontic must_not --aim take_shared --cond consented:eq:0 --gloss ... --quote "<your words, verbatim>"` | The new card read back in plain English, lint passes, a new variant directory (your seed is untouched), and a change row holding your exact words. If lint fails, nothing is written and you are told why. |
| 4. "Compare my seed with that variant across all pairings." | `mar household compare --variants author_seed_v2_bindable,<new name> --pairs hand` | Means with 95% CIs per variant, paired differences with permutation p and Holm p, and a one-line verdict. A report opens. |
| 5. "How did we get here?" | `mar timeline` | One page of your questions, decisions, rule changes (with your quote from step 3), runs and commits. |

Notes
- Say "all pairings" and the skill passes `--pairs hand` (15 pairs) or `--pairs all` (57, slower, with the pressing personas). More seeds (`--seeds 5`) tighten the CIs.
- Step 3's card uses the `consented` flag as "both agree". Read the read-back: the engine's words are blunter than yours ("when the consent flag is exactly 0, a partner must not take_shared"). If it is not what you meant, say so and the skill records that as a "not what I meant" change.
- Expect small or zero differences in lived outcomes when the pot is negotiated at week 0: negotiated pot terms can override a base card. That is a result, not a bug; the freedom score still moves.
- Everything is scripted persona policy with assumed parameters. Findings are about rule systems, not people.
