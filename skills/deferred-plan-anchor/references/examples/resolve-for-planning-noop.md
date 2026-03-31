# Example: Resolve for Planning No-op

## Situation
- A repository has an active deferred plan about authority boundaries in the backend.
- The current planning request is a docs-only cleanup with unrelated scope tags.

## Expected Result
- `resolve-for-planning` returns:
  - `enabled: true`
  - `active: true`
  - `applies: false`
  - no guardrails injected into planning

## Why
- The deferred plan exists, but it does not apply to the current planning scope.
