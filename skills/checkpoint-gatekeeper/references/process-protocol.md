# Process Protocol

## 1. Confirm Gate Scope
- Confirm the target plan and checkpoint.
- Confirm that the gate is checkpoint-scoped, not a full-task autonomous loop.
- Confirm whether the profile is the default validation path or `acceptance`.

## 2. Create or Load Artifacts
- Checklist path: `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-checklist.md`
- Verdict path: `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-gate.json`
- The checklist is the editable operator surface.
- The gate JSON is the machine-readable verdict surface.

## 3. Run Validation
- Execute checkpoint validation commands in repository root.
- Record command outputs and return codes.
- For `acceptance`, also record whether contract closure and required evidence are present.

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

For `acceptance` profile:
- the summary should say whether semantic completion is satisfied or what gaps remain
- the verdict still uses the same checkpoint verdict enum

## 6. Escalation Rules
- Escalate as `needs_user_confirmation` when:
  - output matches configured confirmation triggers
  - remediation would exceed current-checkpoint bounds
  - remediation policy or pass criteria would need to change

## 7. No-Overlap Rules
- Do not update plan lifecycle state here.
- Do not archive or complete plans here.
- Do not silently convert `fail` into `waived`.
- Do not turn `acceptance` into a second owner surface outside the checkpoint gate.
