# Process Protocol

## 1. Confirm Same-Task Continuation
- Verify that the next window will continue the same unfinished task.
- Verify the current window still has the needed context to summarize itself.

## 2. Collect Current-Session Surfaces
- Find the related plan, memory, experience, and process refs.
- Prefer refs already linked from existing docs over broad repo scanning.

## 3. Draft One Continuation Pack
- Write to `docs/session-handoff/SHO-YYYYMMDD-NNNN.md`.
- Keep it pointer-first and session-scoped.
- If the session spans multiple subtasks, represent them under `Subtask Snapshots`.

## 4. Required Markdown Sections
- `Session ID`
- `Generated At`
- `Offload Reason`
- `Session Goal`
- `Overview`
- `Related Refs`
- `Subtask Snapshots`
- `Avoid Repeat`
- `Next Window Boot`
- `Source of Truth`

## 5. Section Guidance
- `Overview`
  - Summarize what this session actually accomplished and what remains unresolved.
- `Related Refs`
  - Group refs by `plans`, `memory`, `experience`, and `process/evidence`.
- `Subtask Snapshots`
  - For each subtask: goal, completed summary, remaining summary, blockers, next action, and evidence refs.
- `Avoid Repeat`
  - Keep only 1-3 high-signal lessons or anti-patterns.
- `Next Window Boot`
  - State exactly what to read first and what the first action should be.
- `Source of Truth`
  - State that plan, memory, and experience docs remain authoritative.

## 6. New-Window Consumption Order
1. Read `Offload Reason` and `Overview`.
2. Read `Subtask Snapshots`.
3. Read related plan refs.
4. Read related memory refs.
5. Read related experience refs and `Avoid Repeat`.
6. Start new planning after the above is understood.

## 7. MVP Guardrails
- Explicit trigger only.
- One Markdown pack only.
- No `.json` sidecar.
- No `SESSION_INDEX.json`.
- No automatic write-back to other docs.
