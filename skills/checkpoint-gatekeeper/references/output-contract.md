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
- `profile`
- `verdict`
- `summary`
- `updated_at`
- `checklist_path`
- `attempts`
- `waiver`

## Optional Acceptance Fields
- `acceptance_target`
- `acceptance_gaps`
- `required_evidence`
- `evidence_path`
- `acceptance_review_path`

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
- `acceptance` profile must reuse the same verdict enum rather than inventing a second verdict surface.
- `acceptance` pass requires both validation success and a valid independent acceptance review artifact.
- Missing or malformed acceptance evidence or review artifacts must not silently pass; they should escalate as `needs_user_confirmation`.
