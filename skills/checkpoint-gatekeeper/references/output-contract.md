# Output Contract

## Gate Verdicts
- `pending`: artifacts exist, checkpoint not yet checked
- `pass`: validation succeeded directly
- `auto_fixed_pass`: validation failed, bounded remediation succeeded, revalidation passed
- `fail`: validation remains failed inside current checkpoint bounds
- `needs_user_confirmation`: the checkpoint is blocked on explicit human decision
- `waived`: explicit override with recorded reason

## Gate JSON Fields
- `plan_id`
- `checkpoint`
- `title`
- `verdict`
- `summary`
- `updated_at`
- `checklist_path`
- `attempts`
- `waiver`

## Attempt Record Fields
- `attempt`
- `started_at`
- `finished_at`
- `validation_results`
- `auto_fix_rounds`
- `matched_user_confirmation_triggers`

## CLI Quality Bar
- `status` must show the current verdict without mutating artifacts.
- `check` must write deterministic evidence to the gate JSON.
- Non-passing verdicts must return a non-zero exit code.
