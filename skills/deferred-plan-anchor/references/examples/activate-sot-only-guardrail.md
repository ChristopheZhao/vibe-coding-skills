# Example: Activate a SoT-only Guardrail

## Situation
- The team agrees the long-term target is a single authority surface.
- The current system still has a temporary dual-write path.
- Immediate migration would be too large for the current work slice.

## Why This Skill Fits
- The direction is chosen.
- Execution is deferred.
- Near-term planning still needs a hard "do not expand the temporary surface" rule.

## Expected Artifact Shape
- Create a deferred plan with:
  - goal: converge to the single authority surface
  - why not now: migration cost too high for the current slice
  - do_not: do not add new authority semantics on the temporary surface
  - allowed_now: compatibility-only reads
  - reopen_trigger: create a dedicated migration plan before touching the boundary
