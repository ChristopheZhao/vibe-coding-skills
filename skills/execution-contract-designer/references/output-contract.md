# Output Contract

## Required Fields
- `slice_title`
- `what`
- `why`
- `done_signals`
- `evidence_checklist`
- `negative_cases`
- `suggested_checkpoints`
- `next_owner`

## Field Quality Bar
- `what` must describe one semantic closure, not a whole roadmap.
- `why` must explain why this boundary exists now.
- `done_signals` must be observable.
- `evidence_checklist` must point to artifacts or verification surfaces.
- `negative_cases` must be task-specific.
- `suggested_checkpoints` must remain suggestions, not verdicts.

## JSON Shape (Reference)
```json
{
  "slice_title": "Standalone execution-mode-selector contract",
  "what": "Introduce one new skill that decides one-shot vs research vs discussion vs sprint mode before implementation starts",
  "why": "Later preflight and acceptance extensions should consume a stable execution-shape surface instead of re-deriving it",
  "done_signals": [
    "A new skill folder exists with SKILL.md, references, agents/openai.yaml, and smoke coverage",
    "The public skill catalog includes the new skill"
  ],
  "evidence_checklist": [
    "skills/execution-mode-selector/SKILL.md",
    "skills/execution-mode-selector/scripts/smoke.sh",
    "docs/skills/INDEX.md"
  ],
  "negative_cases": [
    "The new skill should not mutate plan lifecycle state",
    "The new skill should not emit checkpoint verdicts"
  ],
  "suggested_checkpoints": [
    "skill-contract-smoke",
    "owner-boundary-review"
  ],
  "next_owner": "checkpoint-gatekeeper"
}
```
