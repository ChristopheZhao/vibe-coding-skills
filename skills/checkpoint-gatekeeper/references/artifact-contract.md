# Artifact Contract

## Directory Layout
- All checkpoint artifacts live under `docs/checkpoints/<PLAN-ID>/`.
- One checkpoint produces:
  - `CHK-<checkpoint>-checklist.md`
  - `CHK-<checkpoint>-gate.json`

## Checklist File
- Path: `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-checklist.md`
- The file is Markdown and contains one required embedded JSON spec block:

```markdown
<!-- checkpoint-gatekeeper:spec
{
  "plan_id": "PLAN-20260322-001",
  "checkpoint": "CHK-A",
  "title": "Checkpoint A",
  "allow_auto_fix": true,
  "max_auto_fix_rounds": 1,
  "validation_commands": [
    "python3 -m unittest -q tests.test_gate"
  ],
  "auto_fix_commands": [
    "python3 scripts/fix_small_issue.py"
  ],
  "user_confirmation_triggers": [
    "MANUAL_REVIEW_REQUIRED",
    "SCOPE_CHANGE_REQUIRED",
    "NEEDS_USER_CONFIRMATION"
  ]
}
-->
```

## Checklist Editing Rule
- Human-readable sections may be edited freely.
- The embedded JSON spec block is the machine-readable source of truth for commands and gate policy.

## Gate Verdict File
- Path: `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-gate.json`
- Holds:
  - plan/checkpoint linkage
  - current verdict
  - summary
  - attempt records
  - waiver metadata when present
