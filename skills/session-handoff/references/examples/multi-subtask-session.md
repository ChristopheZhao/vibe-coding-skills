# Example: Multi-Subtask Session Handoff

## Trigger Reason
- The current window has attempted a complex refactor across multiple subtasks.
- The task is still unfinished, and the user wants a pack for the next window to continue directly.

## Expected Output Shape
- One Markdown handoff file in `docs/session-handoff/`.
- Includes:
  - related plan refs
  - related memory refs
  - 1-3 avoid-repeat items
  - per-subtask next actions

## Why This Fits
- The main need is same-task next-window continuation.
- The output is session-scoped, not a reusable experience card or plan-status update.
