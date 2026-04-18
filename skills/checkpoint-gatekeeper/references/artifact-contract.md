# Artifact Contract

## Directory Layout
- All checkpoint artifacts live under `docs/checkpoints/<PLAN-ID>/`.
- One checkpoint produces:
  - `CHK-<checkpoint>-checklist.md`
  - `CHK-<checkpoint>-gate.json`
- `acceptance` checkpoints also produce or consume:
  - `CHK-<checkpoint>-evidence.json`
  - `CHK-<checkpoint>-acceptance-review.json`

## Checklist File
- Path: `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-checklist.md`
- The file is Markdown and contains one required embedded JSON spec block:

```markdown
<!-- checkpoint-gatekeeper:spec
{
  "plan_id": "PLAN-20260322-001",
  "checkpoint": "CHK-A",
  "title": "Checkpoint A",
  "profile": "acceptance",
  "acceptance_target": "semantic closure for checkpoint A",
  "required_evidence": [
    "smoke output linked",
    "changed artifacts listed"
  ],
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
  - for `acceptance`, evidence and review artifact paths plus acceptance gap list

## Acceptance Evidence File
- Path: `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-evidence.json`
- Required fields:
  - `plan_id`
  - `checkpoint`
  - `acceptance_target`
  - `contract_ref`
  - `evidence_refs`
  - `changed_artifact_paths`
  - `negative_cases`
  - `declared_out_of_scope`
  - `executor_summary`

## Acceptance Review File
- Path: `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-acceptance-review.json`
- Produced by an independent reviewer for formal `acceptance` verification.
- Required fields:
  - `plan_id`
  - `checkpoint`
  - `reviewer_kind`
  - `review_verdict`
  - `contract_closure`
  - `evidence_sufficiency`
  - `gap_severity`
  - `gaps`
  - `cited_evidence`
  - `summary`

## Plan-Side Validation Ledger Handshake
- Authoritative checkpoint artifacts remain under `docs/checkpoints/<PLAN-ID>/`.
- A repo may also keep a governance-side mirror such as `docs/plans/active/PLAN-<plan-id>-validation.md`.
- That plan-side ledger may summarize:
  - checkpoint id
  - verdict
  - review artifact refs
  - test command refs
  - evidence links
- The plan-side ledger is not written or owned by `checkpoint-gatekeeper`.
- The plan-side ledger must not replace or contradict the authoritative gate verdict files under `docs/checkpoints/<PLAN-ID>/`.
