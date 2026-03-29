# Example: Refactor Contract

## Slice
Extend `checkpoint-gatekeeper` with an `acceptance` profile while preserving verdict ownership.

## Contract
- `what`:
  - Add acceptance semantics under the existing checkpoint owner without creating a new top-level verdict surface.
- `why`:
  - The repo needs semantic acceptance, but ownership should stay stable in phase 1.
- `done_signals`:
  - The `acceptance` profile is documented in `checkpoint-gatekeeper`.
  - Examples show how acceptance consumes evidence without becoming a new lifecycle owner.
- `evidence_checklist`:
  - updated `SKILL.md`
  - updated output contract
  - new examples
- `negative_cases`:
  - No second verdict owner is introduced.
  - Acceptance semantics do not mutate plan lifecycle state.
- `suggested_checkpoints`:
  - `owner-boundary-review`
  - `profile-smoke`
