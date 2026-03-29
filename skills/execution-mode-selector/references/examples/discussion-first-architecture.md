# Example: Discussion-First Architecture

## Task
Decide whether a new workflow should be governed by a standalone acceptance skill or stay under the existing checkpoint owner.

## Signals
- unresolved owner boundary
- architecture and product trade-off
- discussion outcome changes downstream implementation shape

## Verdict
- `discussion-first`

## Why
- Planning execution before resolving ownership would create rework and duplicated surfaces.
- The next owner should be `multi-agent-discussion-advisor`.
