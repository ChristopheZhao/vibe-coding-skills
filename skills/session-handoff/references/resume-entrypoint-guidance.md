# Resume Entrypoint Guidance

Use this note only when the next window should not move straight into coding.
The handoff pack remains the main artifact. This file only helps phrase one concise `Before coding` hint inside `Next Window Boot`.

## When No Extra Hint Is Needed
- The continuation is tiny, local, and already well-bounded.
- The current execution entrypoint is obvious from the handoff and does not need extra warning.

## When To Point To An Existing Plan
- A current valid implementation plan still exists and remains the right execution entrypoint.
- The next window should review that plan before coding because the session changed diagnosis, scope, or risk.

Preferred phrasing:
- `Before coding: review PLAN-... and confirm it still covers the current execution entrypoint.`

## When To Point To Plan Creation Or Refresh
- No current valid execution entrypoint exists.
- The previous plan is now only `historical` or `reference-only`.
- The next window must re-establish an implementation entrypoint before coding.

Preferred phrasing:
- `Before coding: create or refresh the implementation plan in sdd-plan-maintainer.`

## Anti-patterns
- Do not add abstract workflow labels such as `Planning posture`.
- Do not embed plan steps, acceptance criteria, or execution contracts into the handoff.
- Do not create a second plan-like artifact alongside the handoff just to carry this hint.
