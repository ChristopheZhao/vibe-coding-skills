# Artifact Contract

## Repository Root

Deferred-plan artifacts live under:

```text
docs/
  deferred-plans/
    CURRENT.md
    DEFERRED_PLAN_INDEX.json
    active/
      DP-YYYYMMDD-NNN.md
    archive/
      YYYY-MM/
        DP-YYYYMMDD-NNN.md
```

## State Truth
- `DEFERRED_PLAN_INDEX.json` is the status truth.
- `CURRENT.md` is a derived summary, not an independent source of truth.
- Individual `DP-*.md` files are human-readable source artifacts aligned with the index entry.

## Allowed Statuses
- `draft`
- `active`
- `superseded`
- `completed`
- `archived`

Only `active` affects `CURRENT.md` or planning resolution.

## Required Fields Per Plan
- `id`
- `title`
- `status`
- `owner`
- `file_path`
- `scope_tags`
- `topic_tags`
- `plan_kinds`
- `goal`
- `why_not_now`
- `current_deviation`
- `do_not`
- `allowed_now`
- `reopen_trigger`
- `created_at`
- `updated_at`

## Summary Shape
`CURRENT.md` should stay concise and include:
- active plan id and title
- scope/topic applicability hints
- goal
- why not now
- do-not guardrails
- allowed-now actions
- reopen trigger
- source path

When no active plan exists, `CURRENT.md` must say so explicitly.
