# Example: Handoff After an Older Plan Was Invalidated

## Trigger Reason
- The current window proved that an unfinished older plan was based on the wrong root-cause path.
- The user wants the next window to continue the same task without being pulled back into the old checklist.

## Expected Output Shape
- One Markdown handoff file in `docs/session-handoff/`.
- Includes:
  - the older plan marked as historical or reference-only
  - the new diagnosis entrypoint and code refs
  - an explicit first action for the next window
  - a concise `Before coding: create or refresh the implementation plan in sdd-plan-maintainer.` note
  - a note about what not to continue by default

## Why This Fits
- The main need is next-window continuation with corrected direction.
- The pack clarifies execution entrypoints without taking over plan lifecycle governance.
