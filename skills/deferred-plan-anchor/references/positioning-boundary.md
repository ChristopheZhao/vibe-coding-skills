# Deferred Plan Anchor: Positioning and Boundary

## Positioning
- Goal: preserve a deferred technical direction as an active planning guardrail until a dedicated migration plan takes over.
- Value: stop short-term implementation from silently deepening temporary architecture debt.
- Nature: a deferred-guardrail owner, not an execution-plan owner.

## In Scope
- deferred-plan artifact ownership under `docs/deferred-plans/`
- independent status truth and archive behavior
- concise "current guardrail" summary generation
- planning applicability resolution through a narrow adapter

## Out of Scope
- concrete execution-plan creation
- general roadmap or backlog management
- architecture debate before a direction is chosen
- project continuity memory
- reusable lesson capture

## Layer Split
- `discussion`: choose or challenge the direction
- `deferred-plan-anchor`: freeze deferred but active guardrails
- `plan`: define and track immediate execution
- `memory`: preserve continuity context

## Boundary Rule
- `deferred-plan-anchor` decides whether a deferred guardrail applies to current planning.
- It does not own execution-plan lifecycle, planning status, or runtime orchestration.
