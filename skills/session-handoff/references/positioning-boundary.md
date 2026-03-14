# Session Handoff: Positioning and Boundary

## Positioning
- Goal: offload the current session into a continuation pack for the next window of the same unfinished task.
- Value: reduce manual context reconstruction when the current window is no longer reliable due to context rot.
- Nature: a session-level workflow skill, not a truth-owning storage system.

## In Scope
- Session-level aggregation of current progress, blockers, next action, and avoid-repeat guidance.
- Pointer-first references to related plan, memory, experience, and process docs.
- One continuation pack per explicit handoff trigger.

## Out of Scope
- Plan lifecycle ownership.
- Reusable experience-card persistence.
- Long-term project memory truth.
- Full transcript archival.
- Bulk regeneration of related docs.

## Layer Split
- `session`: current window closeout and next-window continuation pack.
- `plan`: subtask/plan lifecycle and completion truth.
- `experience`: reusable cross-task lessons.
- `memory`: continuity facts and recovery state.

## Boundary Rule
- Read canonical artifact surfaces under `docs/` rather than depending on a specific skill implementation.
- The handoff pack must not become a second source of truth for plan, memory, or experience state.
