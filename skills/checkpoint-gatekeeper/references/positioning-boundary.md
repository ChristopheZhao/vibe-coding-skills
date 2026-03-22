# Checkpoint Gatekeeper: Positioning and Boundary

## Positioning
- Goal: enforce checkpoint-level verification before complex work advances to the next stage.
- Value: reduce stage-to-stage error propagation by adding a deterministic gate loop around validation and bounded remediation.
- Nature: a checkpoint-scoped verification skill, not a plan-lifecycle or full orchestration skill.

## In Scope
- checkpoint checklist and gate artifact creation
- deterministic validation command execution
- bounded current-checkpoint remediation and revalidation
- explicit verdict emission

## Out of Scope
- plan lifecycle ownership
- successor-plan creation
- session handoff aggregation
- full long-running Ralph-style loop orchestration
- silent waiver or silent pass-standard changes

## Layer Split
- `plan`: define checkpoints and lifecycle states
- `gate`: validate one checkpoint and emit a verdict
- `handoff`: carry unresolved gate results across windows when needed

## Boundary Rule
- `checkpoint-gatekeeper` may block progression, but it does not redefine plan status truth.
- Verification artifacts live under `docs/checkpoints/`, not `docs/plans/`.
