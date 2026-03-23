# Process Protocol

## 1. Confirm the Decision Surface
- Clarify whether the user is deciding about checkpoint commits, not generic git history management.
- Capture any known context such as current plan id, new phase, or new-window handoff intent.

## 2. Inspect the Dirty Worktree
- Read:
  - `git status --short`
  - `git diff --stat`
  - `git diff --check`
- Optionally inspect path clusters and top-level directory spread.

## 3. Check Worktree Health
- If conflict markers, diff-check failures, or similarly corrupted states exist, recommend `defer`.
- If the dirty tree is tiny and clearly scoped, recommend `defer` unless the user explicitly wants a checkpoint commit.

## 4. Propose Commit Strategy
- `single-snapshot`: one commit is enough.
- `two-layer`: typically `governance anchor` plus `implementation snapshot`.
- `three-layer`: split governance, implementation, and supporting-doc or archive/import surfaces.

## 5. Emit Advisory Output
- Decision: `commit_now` or `defer`
- Strategy
- File buckets
- Suggested commit messages
- Risks
- Confirmation points

## 6. Respect the Execution Boundary
- Do not stage or commit automatically.
- If the user confirms execution, the host agent may translate the proposal into real git commands outside this skill’s default advisory loop.
