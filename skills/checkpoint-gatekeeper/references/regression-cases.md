# Regression Cases

## Trigger Cases
- User says a stage must not continue until the current stage is verified.
- A plan checkpoint needs validation and bounded auto-remediation.
- The team wants explicit gate verdicts separate from plan lifecycle states.

## Non-Trigger Cases
- User only asks to create or update a plan.
- A simple local test run has no checkpoint semantics.
- The task needs a full long-running orchestrator rather than checkpoint gating.

## Boundary Assertions
- Gate artifacts must be stored under `docs/checkpoints/`, not `docs/plans/`.
- Gate verdicts must not mutate `docs/plans/PLAN_INDEX.json`.
- Auto-remediation must stay within current-checkpoint bounds.
- Waivers must require an explicit operator action and reason.

## Verification Assertions
- A passing checkpoint returns `pass` or `auto_fixed_pass`.
- A risky or ambiguous checkpoint returns `needs_user_confirmation`.
- A failed checkpoint must not silently advance.
