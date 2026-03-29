# Example: Feature Contract

## Slice
Add `execution-mode-selector` as a new standalone skill.

## Contract
- `what`:
  - Add one new skill that selects one-shot vs research-first vs discussion-first vs sprint-required before implementation begins.
- `why`:
  - Downstream planning and review surfaces should consume a stable execution-shape layer instead of reconstructing it.
- `done_signals`:
  - The new skill folder exists with required files.
  - Its smoke passes.
  - The public catalog includes the skill.
- `evidence_checklist`:
  - `skills/execution-mode-selector/SKILL.md`
  - `skills/execution-mode-selector/scripts/smoke.sh`
  - `docs/skills/INDEX.md`
- `negative_cases`:
  - The skill must not mutate lifecycle state.
  - The skill must not emit checkpoint verdicts.
- `suggested_checkpoints`:
  - `skill-contract-smoke`
  - `owner-boundary-review`
