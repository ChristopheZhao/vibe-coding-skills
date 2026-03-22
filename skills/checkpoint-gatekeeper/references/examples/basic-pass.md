# Example: Basic Pass

## Scenario
- A phase boundary has one focused validation command.
- The command passes immediately.

## Expected Outcome
- Checklist and gate artifacts exist under `docs/checkpoints/<PLAN-ID>/`.
- `gate check` writes verdict `pass`.
- No remediation commands run.
