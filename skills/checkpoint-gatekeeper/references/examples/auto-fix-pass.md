# Example: Auto-Fix Pass

## Scenario
- Validation fails because a checkpoint-local file or config is incomplete.
- The checklist includes one bounded remediation command that fixes the local issue.

## Expected Outcome
- Initial validation fails.
- Auto-fix runs once.
- Revalidation passes.
- Verdict becomes `auto_fixed_pass`.
