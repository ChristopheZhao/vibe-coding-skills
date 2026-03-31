# Output Contract

## Deferred Plan Summary

Human-facing summaries should stay concise and operational:
- Goal
- Why not now
- Do not
- Allowed now
- Reopen trigger
- Source

Avoid long historical narratives in current summaries.

## Adapter Contract

`resolve-for-planning` should be able to return JSON like:

```json
{
  "enabled": true,
  "active": true,
  "applies": true,
  "stale": false,
  "deferred_plan_id": "DP-20260331-001",
  "title": "Converge to single authority surface",
  "goal": "Converge to only-A authority",
  "do_not": [
    "Do not add new authority semantics on B"
  ],
  "allowed_now": [
    "Compatibility reads only"
  ],
  "reopen_trigger": [
    "Create a dedicated migration plan before touching the authority boundary"
  ],
  "source": "docs/deferred-plans/active/DP-20260331-001.md",
  "reason": "active deferred plan matches provided scope and topic tags"
}
```

## No-op Contract

When the deferred-plan system is absent, inactive, stale, or out of scope, return a no-op structure instead of failing:

```json
{
  "enabled": false,
  "active": false,
  "applies": false,
  "stale": false,
  "deferred_plan_id": null,
  "title": null,
  "goal": null,
  "do_not": [],
  "allowed_now": [],
  "reopen_trigger": [],
  "source": null,
  "reason": "deferred-plan root not enabled"
}
```
