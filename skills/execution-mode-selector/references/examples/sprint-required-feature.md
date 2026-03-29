# Example: Sprint-Required Feature

## Task
Add a new harness-aware execution workflow that introduces a new skill, extends two existing skills, and adds shared evaluator profiles.

## Signals
- cross-skill coupling
- staged validation needed
- owner-boundary risk
- late failure would be expensive

## Verdict
- `sprint-required`

## Coarse Sprints
- Sprint 1: new standalone contracts
  - Why this boundary exists: downstream extensions should not start before the new contracts stabilize.
- Sprint 2: extend existing owner surfaces
  - Why this boundary exists: owner boundaries can be reviewed after the new contracts exist.
- Sprint 3: shared calibration layer
  - Why this boundary exists: calibration should only be added after concrete consumers exist.
