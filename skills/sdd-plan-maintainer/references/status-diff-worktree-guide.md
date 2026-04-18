# Status Visibility, Diff Tracking, and Worktree Context

This guide adds lightweight operational clarity without changing the existing lifecycle model.

## 1. What Can Be Read from `docs/plans/`

- `docs/plans/PLAN_INDEX.json` is the machine-readable source for current lifecycle state.
- `docs/plans/active/` shows non-archived main plans; companion governance docs may live beside those plans.
- `docs/plans/archive/YYYY-MM/` shows closed plans and may also contain archived companion governance docs beside the archived main plan.

For quick project-level status, read the index first, then open specific plan files for details.

## 2. Recommended Status Read Order

1. Check `PLAN_INDEX.json` for each plan `status`, `updated_at`, `archived_at`, and latest `notes`.
2. Open the corresponding plan markdown for narrative context and checklist details.
3. If present, open companion governance docs such as `-validation.md` or `-stage-*.md` for review/test evidence and stage-freeze context.
4. If index status and plan header status differ, treat index as authoritative and record a sync task.

## 3. Diff-Based Tracking (Git)

Use git diff to make lifecycle changes auditable:

```bash
git diff -- docs/plans/PLAN_INDEX.json
git diff -- docs/plans/active docs/plans/archive
```

Recommended review pattern:

1. Confirm lifecycle transition in `PLAN_INDEX.json`.
2. Confirm plan markdown status/log update (if performed in this change).
3. Confirm companion governance docs do not introduce conflicting lifecycle truth.
4. Confirm archive path movement when status reaches `archived`.

## 4. Compare-File Checklist for Milestones

Before and after milestone status updates:

1. Compare `PLAN_INDEX.json` diff.
2. Compare plan markdown diff (`Status` header + `Status Log` section).
3. Compare companion governance doc diffs when stage validation or governance freezes changed.
4. Compare archive movement diff when closing plans.

This gives a deterministic "state before/after" view for both humans and tooling.

## 5. Optional Worktree Context for Parallel Plans

When multiple long-running plans execute in parallel, keep one optional context block in the plan file (or execution handoff section):

- `Worktree`: path or identifier
- `Branch`: current branch name
- `Base Commit`: starting commit
- `Head Commit`: latest verified commit

This metadata supports recovery and ownership clarity, but it is not a second lifecycle status source.

## 6. Guardrails

- Keep lifecycle ownership in `PLAN_INDEX.json`.
- Do not introduce status folders like `testing/` or `blocked/` as state carriers.
- Use folder semantics only for `active` vs `archive`.
- Treat companion governance docs as supporting artifacts only; they may mirror evidence but they must not become a second plan-status ledger.
