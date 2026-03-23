# Regression Cases

## Trigger Cases
- A large dirty worktree mixes plan or handoff governance files with implementation files before a new phase begins.
- A user wants to open a successor plan or new window without carrying a huge dirty tree forward.
- A worktree needs a `known-bad snapshot` before boundary refactor or large cleanup work starts.

## Non-Trigger Cases
- One or two obvious code edits do not justify a checkpoint strategy discussion.
- The user only asks to update a plan or run a checkpoint gate.
- The task is PR cleanup or git history surgery.

## Boundary Assertions
- The skill must not mutate `docs/plans/PLAN_INDEX.json`.
- The skill must not emit checkpoint validation verdicts.
- The skill must not silently run `git add` or `git commit`.
- The skill must clearly distinguish `wrong but explainable snapshot` from `corrupted worktree state`.

## Verification Assertions
- Large mixed worktrees can produce `two-layer` or `three-layer` recommendations.
- Small clean worktrees can produce `defer`.
- Corrupted or diff-check-failing worktrees must produce `defer` with blocking health signals.
