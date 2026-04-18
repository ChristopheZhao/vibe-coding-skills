# Checkpoint Gatekeeper Examples

- `basic-pass.md`: direct validation pass with no remediation.
- `auto-fix-pass.md`: bounded remediation converts a local failure into `auto_fixed_pass`.
- `acceptance-pass.md`: semantic completion stays under checkpoint ownership through an `acceptance` profile.
- `non-example.md`: plan-only governance request that should stay in `sdd-plan-maintainer`.

If the repo also keeps `docs/plans/*-validation.md`, treat it as a governance-side summary mirror.
The authoritative checkpoint artifacts remain under `docs/checkpoints/<PLAN-ID>/`.
