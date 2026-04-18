# Harness Fusion Pattern

Use this guide when integrating `sdd-plan-maintainer` with a long-running execution harness.

## 1. Goal
Preserve plan-governance rigor while enabling resilient execution recovery across turns.

## 2. Layer Split
- Governance layer:
  - Owns plan lifecycle status and transition rules.
  - Owns completion/archive gates.
  - Owns `docs/plans/PLAN_INDEX.json` consistency.
- Execution layer:
  - Owns short-lived session context.
  - Owns rapid progress snapshots between governance milestones.

## 3. Canonical Data Surfaces
- `docs/plans/active/<plan>.md`: authoritative lifecycle-bearing plan narrative and checklist.
- `docs/plans/active/<plan>-validation.md` or `docs/plans/active/<plan>-stage-*.md`: optional companion governance docs for review/test evidence and stage-freeze detail.
- `docs/plans/PLAN_INDEX.json`: authoritative lifecycle metadata and status source of truth.

Shared memory is the persistent plan documentation system itself. Do not create a second lifecycle store.

## 4. Suggested Handoff Block (In Plan File)
```markdown
## Execution Handoff (Optional)
- Current focus: Implement router status transition validation
- Blockers: Need fixture for archived plan edge case
- Next resume action: Add transition regression test for completed -> in_progress reopen path
- Evidence pointers: tests/test_plan_ops.py:142
- Updated at: 2026-02-15T10:30:00Z
```

## 5. Anti-Overlap Rules
- No second status machine outside `docs/plans/PLAN_INDEX.json` (plan header is mirror-only).
- No completion claim in handoff notes.
- No archive action outside governance layer.
- No companion governance doc may claim lifecycle truth that conflicts with the main plan or `PLAN_INDEX.json`.

## 6. Milestone Sync Pattern
1. Start: load plan file and index as the shared memory baseline.
2. Execute: update handoff notes in the plan file when session context changes.
3. Milestone: update governance status once per meaningful checkpoint.
4. Close: enforce completion gates, then optional archive.
