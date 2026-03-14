# Example: Complex Refactor Dual Output

## Trigger reason
- User asks for reusable lessons and also needs a simple process note to explain where those lessons came from.
- Work is complex enough that a card alone would hide one or two key turning points, but the main lesson cluster is still singular.
- The capture still focuses on one lesson cluster and the turning points that produced it, not on session handoff or full project archival.

## Expected output shape
- Experience card:
  - captures reusable decision rules, anti-patterns, and review checklist.
- Source retrospective note:
  - captures the minimum process context needed to explain why those rules were formed.
  - lives under `docs/experience/sources/` and is referenced by the card via anchored `source_event_refs`.

## Suggested source retrospective sections
- original intent
- key turning points
- what was achieved that matters to the lesson
- why the lesson matters

## Suggested tags
- `architecture`
- `source-note`
- `retrospective`
- `complex-refactor`
