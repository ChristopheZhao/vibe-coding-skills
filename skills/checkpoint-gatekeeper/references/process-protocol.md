# Process Protocol

## 1. Confirm Gate Scope
- Confirm the target plan and checkpoint.
- Confirm that the gate is checkpoint-scoped, not a full-task autonomous loop.

## 2. Create or Load Artifacts
- Checklist path: `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-checklist.md`
- Verdict path: `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-gate.json`
- The checklist is the editable operator surface.
- The gate JSON is the machine-readable verdict surface.

## 3. Run Validation
- Execute checkpoint validation commands in repository root.
- Record command outputs and return codes.

## 4. Attempt Bounded Remediation
- If validation fails and the checklist allows auto-fix, run remediation commands.
- Re-run validation after remediation.
- Stop after the configured max remediation rounds.

## 5. Emit Verdict
- `pass`: validation succeeded with no remediation.
- `auto_fixed_pass`: validation failed, remediation succeeded, revalidation passed.
- `fail`: validation remains failed within current checkpoint bounds.
- `needs_user_confirmation`: risky, ambiguous, or standard-changing failure mode detected.
- `waived`: explicit operator override with recorded reason.

## 6. Escalation Rules
- Escalate as `needs_user_confirmation` when:
  - output matches configured confirmation triggers
  - remediation would exceed current-checkpoint bounds
  - remediation policy or pass criteria would need to change

## 7. No-Overlap Rules
- Do not update plan lifecycle state here.
- Do not archive or complete plans here.
- Do not silently convert `fail` into `waived`.
