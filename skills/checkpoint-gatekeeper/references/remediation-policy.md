# Remediation Policy

## Default Policy
- Prefer automatic validation first.
- Allow automatic remediation only when the checklist explicitly provides remediation commands.
- Keep remediation checkpoint-bounded and retry-bounded.

## Allowed Auto-Remediation
- deterministic edits or commands scoped to the current checkpoint
- low-risk follow-up fixes that do not alter plan scope or gate criteria
- immediate revalidation after remediation

## Disallowed Auto-Remediation
- changing checkpoint definitions
- modifying pass criteria
- introducing waivers without explicit operator action
- broad replanning or cross-stage refactors

## Escalate To User When
- outputs match explicit confirmation triggers
- the failure suggests a scope or architectural change
- remediation would exceed the current checkpoint boundary
- repeated remediation still leaves the checkpoint ambiguous
