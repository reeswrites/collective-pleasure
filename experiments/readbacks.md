# Read-back log

Started 2026-11-11 at the author's word ("Log only"), after loop b counting found the rule not operational because the log never recorded what the author was shown (docs/results/loop-b-counting.md). The author declined planted test formalizations, so fatigue and convergence stay hard to separate; this log at least fixes the denominator.

One row per item shown to the author in `experiments/readbacks.jsonl`, whether or not the author answers. Written by Claude at the time of showing, and completed when the answer arrives.

Fields:
- `readback_id`: one id per batch shown together; `item_id`: one per point within it.
- `timestamp_shown`.
- `shown_text`: the formalization exactly as shown (or file plus commit).
- `in_force_before`: what the docs said before, or null for a new item.
- `who_found_mismatch`: author, claude, reviewer, or none.
- `answer_event`: the timestamp of the answer row in questions.jsonl or changes.jsonl, or null for silence.
- `outcome`: confirmed, rejected, revised, hedge_restored, default_reversed, unsure, or no_answer. Labeled at the time.
- `after_text`: the formalization after the answer.
- `typed_or_button`: typed, button, or unknown.
- `session_id`; `item_novelty`: first_showing or reshown.
