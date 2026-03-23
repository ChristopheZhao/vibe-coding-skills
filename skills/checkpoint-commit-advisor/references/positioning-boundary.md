# Checkpoint Commit Advisor: Positioning and Boundary

## Positioning
- Goal: decide whether a dirty worktree should be frozen as one or more checkpoint commits before work continues.
- Value: reduce diff noise, improve rollback and handoff quality, and separate old experiments from the next implementation phase.
- Nature: a commit-strategy advisory skill, not a lifecycle owner and not a validation gate.

## In Scope
- dirty-tree inspection
- checkpoint commit recommendation or defer recommendation
- commit layering such as:
  - governance anchor
  - known-bad implementation snapshot
  - optional supporting-docs or archive/import snapshot
- suggested commit messages and confirmation points

## Out of Scope
- plan lifecycle ownership
- checkpoint pass/fail verdicts
- session continuation pack generation
- generic git history manipulation
- silent staging or committing

## Layer Split
- `plan`: define and track lifecycle
- `gate`: validate phase output
- `commit-advisor`: decide whether and how to freeze current worktree state
- `handoff`: carry continuation context across windows

## Boundary Rule
- `checkpoint-commit-advisor` decides strategy, not truth.
- It may suggest commit anchors for other skills to reference later, but it does not own those other artifacts.
