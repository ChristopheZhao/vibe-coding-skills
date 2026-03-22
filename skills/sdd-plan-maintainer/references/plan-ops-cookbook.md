# Plan Ops Cookbook

## Command Style
Use this argument order:
- `uv run --active python scripts/plan_ops.py <subcommand> --root <repo-root> ...`

`--root` must be placed after the subcommand.

## 1. Initialize Structure
```bash
uv run --active python scripts/plan_ops.py ensure --root .
```
Creates:
- `docs/plans/active/`
- `docs/plans/archive/`
- `docs/plans/PLAN_INDEX.json`

## 2. Create Plan
Feature:
```bash
uv run --active python scripts/plan_ops.py create --root . --id PLAN-20260214-001 --title "MAS outline confirmation flow" --kind feature --priority P0
```

Fix:
```bash
uv run --active python scripts/plan_ops.py create --root . --id PLAN-20260214-002 --title "Router misclassification repair" --kind fix --priority P1
```

## 3. Move Status by Milestone
```bash
uv run --active python scripts/plan_ops.py status --root . --id PLAN-20260214-001 --status in_progress --note "Started implementation"
uv run --active python scripts/plan_ops.py status --root . --id PLAN-20260214-001 --status testing --note "Core tests running"
uv run --active python scripts/plan_ops.py status --root . --id PLAN-20260214-001 --status awaiting_user_confirmation --note "All tests passed"
uv run --active python scripts/plan_ops.py status --root . --id PLAN-20260214-001 --status superseded --note "Superseded by newer diagnosis in SHO-20260321-0001; stop executing this checklist"
```

## 4. Complete with User Confirmation
```bash
uv run --active python scripts/plan_ops.py status --root . --id PLAN-20260214-001 --status completed --confirmed-by-user --note "User approved after test report"
```

## 5. Archive Closed Plan
```bash
uv run --active python scripts/plan_ops.py archive --root . --id PLAN-20260214-001 --confirmed-by-user
```

`archive` is for already closed plans. In the current lifecycle, that means `completed` or `superseded`.

## 6. Query Progress
```bash
uv run --active python scripts/plan_ops.py list --root .
uv run --active python scripts/plan_ops.py list --root . --status in_progress
uv run --active python scripts/plan_ops.py list --root . --json
```

## 7. Sync Markdown Status from Index
Use index status as the source of truth and sync plan markdown header:

```bash
uv run --active python scripts/plan_ops.py sync-doc --root .
uv run --active python scripts/plan_ops.py sync-doc --root . --id PLAN-20260214-001
```

## 8. Consistency Doctor
Run consistency checks for index, plan file path, and doc status drift:

```bash
uv run --active python scripts/plan_ops.py doctor --root .
uv run --active python scripts/plan_ops.py doctor --root . --fix
uv run --active python scripts/plan_ops.py doctor --root . --json
```

## 9. Generate Status Dashboard
Generate a human-readable status dashboard:

```bash
uv run --active python scripts/plan_ops.py dashboard --root .
uv run --active python scripts/plan_ops.py dashboard --root . --output docs/plans/views/dashboard.md
```

## 10. Manual Fallback (When Script Is Not Used)
Use manual updates only for one-off drafts.
Required constraints:
- Keep folder layout and index location unchanged.
- Keep status values in the defined lifecycle.
- Do not mark completed without test evidence and user confirmation.
- Do not mark blocked or superseded without a note that explains why execution paused or stopped.
- Do not archive without moving file path and updating index path together.
- Treat `docs/plans/PLAN_INDEX.json` as status source of truth.

## 11. Harness Integration (Optional)
When using an external long-running harness:
- Keep lifecycle status changes in `plan_ops.py` only.
- Store per-session recovery details in the plan file's `Execution Handoff` section.
- Keep handoff notes free of lifecycle status fields to avoid overlap.

## 12. Compare-File Review (Recommended)
For each meaningful status milestone, review diffs in this order:

```bash
git diff -- docs/plans/PLAN_INDEX.json
git diff -- docs/plans/active docs/plans/archive
```

Checkpoints:
- Index status transition is correct.
- Plan markdown status/log is aligned when edited.
- Archive move is visible when plan is closed.

For optional parallel execution context, see `references/status-diff-worktree-guide.md`.
