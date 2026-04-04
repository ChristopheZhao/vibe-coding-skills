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
- For `acceptance`, also use:
  - `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-evidence.json`
  - `docs/checkpoints/<PLAN-ID>/CHK-<checkpoint>-acceptance-review.json`

## 3. Run Validation
- Execute checkpoint validation commands in repository root.
- Record command outputs and return codes.
- For `acceptance`, fill the evidence artifact with:
  - contract linkage
  - evidence references
  - changed artifact paths
  - negative cases or declared out-of-scope items when applicable
- Formal `acceptance` verification requires an independent review artifact. The review may be produced by a peer agent or human reviewer, but not by the executor's final self-check alone.

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
- `pass` or `auto_fixed_pass` require:
  - validation success
  - a valid evidence artifact
  - a valid independent acceptance review artifact with `review_verdict=accept`
- `needs_user_confirmation` is the fallback when acceptance artifacts are missing, malformed, or the independent review requests revision
- `fail` applies when the independent review blocks semantic closure
- the verdict still uses the same checkpoint verdict enum

## 6. Escalation Rules
- Escalate as `needs_user_confirmation` when:
  - output matches configured confirmation triggers
  - remediation would exceed current-checkpoint bounds
  - remediation policy or pass criteria would need to change
  - acceptance evidence or independent review artifacts are missing or ambiguous

## 7. No-Overlap Rules
- Do not update plan lifecycle state here.
- Do not archive or complete plans here.
- Do not silently convert `fail` into `waived`.
- Do not turn `acceptance` into a second owner surface outside the checkpoint gate.
- Do not treat executor self-check as the formal independent acceptance review.
