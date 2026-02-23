# Process Protocol

## 1. Role Boundary
Use this skill for project-level planning and lifecycle governance.
Do not use it as a replacement for full coding orchestration.

## 2. Activation Policy
Run this two-step check.

Step A: planning or governance intent exists.
Accepted signals:
- User asks for a concrete plan or a more specific plan.
- User asks for phased execution tracking or status updates.
- User asks for completion confirmation or archive handling.

Step B: select persistence mode.
- Temporary planning mode: response-level plan only, no plan files.
- Managed planning mode: persistent artifacts under `docs/plans/` with index synchronization.
- Governance action mode: status transition and archive on managed plans.

Default guidance:
- Plan refinement requests may stay temporary unless durable tracking is requested.
- New long-running or multi-turn plans should be managed.
- Status update and archive requests must be managed.

## 3. Long-Run Safety
Do not keep this skill active for the entire implementation lifecycle.
Use it at planning or governance milestones only:
- define or refine plan,
- status transition,
- completion confirmation,
- archive.
Return to default Codex behavior between milestones.

## 4. Work Modes
- `feature`: new capability development.
- `fix`: bug fix or refactor.
- `execution`: continue an existing plan with status and evidence updates.

## 5. Status Definitions
- `draft`: plan skeleton exists, execution not started.
- `in_progress`: implementation ongoing.
- `testing`: implementation done, verification ongoing.
- `awaiting_user_confirmation`: tests pass and waiting for user acceptance.
- `completed`: implementation done, tests pass, user confirmed.
- `blocked`: work paused by unresolved blocker.
- `archived`: closed plan moved to archive path.

## 6. Transition Rules
Allowed transitions:
- `draft` -> `in_progress` or `blocked`
- `in_progress` -> `testing`, `awaiting_user_confirmation`, or `blocked`
- `testing` -> `in_progress`, `awaiting_user_confirmation`, `completed`, or `blocked`
- `awaiting_user_confirmation` -> `completed`, `in_progress`, or `blocked`
- `blocked` -> `in_progress`
- `completed` -> `in_progress` (reopen only with new evidence)

Never set `archived` through status update. Use archive operation only.

## 7. Completion and Archive Gates
Set `completed` only when all are true:
- Implementation is done.
- Tests passed with evidence.
- User explicitly confirms result.

Archive only when all are true:
- Current status is `completed`.
- User confirmation is present.
- Plan file is moved from `docs/plans/active/` to `docs/plans/archive/YYYY-MM/`.

## 8. Decide Whether Script Is Needed
Use `scripts/plan_ops.py` when consistency and auditability matter:
- Multiple managed plans are maintained in parallel.
- Status transitions must be enforced.
- `PLAN_INDEX.json` must stay schema-consistent.
- Archive movement must stay synchronized with index updates.

Script can be skipped for temporary planning outputs with no lifecycle tracking.
When skipped, manually follow the same status model and gate rules.

## 9. Harness Fusion Architecture
When a long-running execution harness is present, keep a strict two-layer split.

Governance layer responsibilities:
- Plan scope and acceptance criteria.
- Lifecycle status transitions and status notes.
- Completion and archive gates.
- `docs/plans/PLAN_INDEX.json` and plan file consistency.

Execution layer responsibilities:
- Session-level focus and immediate next action.
- Temporary blocker details for recovery.
- Evidence pointers produced during execution loops.

## 10. Ownership Contract (No Overlap)
Use these single-owner rules:
- Lifecycle status owner: governance layer only (`docs/plans/PLAN_INDEX.json` is the status source of truth; plan header is mirror-only).
- Completion confirmation owner: governance layer only.
- Session recovery context owner: execution layer only.

Disallowed overlap:
- Execution layer keeps a second lifecycle status field.
- Governance layer stores full step-by-step execution transcripts.
- Completion is inferred from execution progress without explicit gate checks.

## 11. Synchronization Contract
If both layers are active, synchronize at milestones only:
1. Start loop: read plan + index, then load execution context.
2. During loop: update execution context freely.
3. Milestone reached: write governance status/evidence via managed flow.
4. Completion: enforce implementation + tests + user confirmation before `completed`.
