# Trigger Rules

## Should Trigger
1. A long-term architecture or migration direction is accepted, but implementation should wait.
2. Near-term planning must stop expanding a temporary workaround, dual-write surface, or stale authority path.
3. The user wants a durable technical guardrail that future planning can reference.
4. A host workflow explicitly asks whether current planning should inherit deferred guardrails.

## Should Not Trigger
1. The user only wants an immediate feature/fix plan.
2. The task is still discussion-only and has not chosen a deferred-but-binding direction.
3. The request is generic roadmap or backlog prioritization.
4. The request belongs to project memory, handoff, or experience capture.

## Guardrails
- Trigger on deferred-but-binding technical direction, not on every design note.
- Prefer not triggering over over-triggering when the request is ordinary planning.
- If no deferred-plan system is enabled in the repository, `resolve-for-planning` should no-op rather than fabricate a guardrail.
