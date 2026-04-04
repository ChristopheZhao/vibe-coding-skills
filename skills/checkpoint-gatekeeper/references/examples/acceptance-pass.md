# Example: Acceptance Profile Pass

## Situation
- A sprint contract already exists.
- The checkpoint owner should assess semantic completion without creating a second verdict owner.
- Required evidence is present and contract closure is satisfied.
- An independent reviewer has produced `CHK-<checkpoint>-acceptance-review.json`.

## Profile
- `acceptance`

## Expected Verdict
- `pass`

## Why
- Acceptance remains under checkpoint ownership.
- No lifecycle state is mutated here.
- The output should summarize semantic completion and evidence sufficiency.
- Executor self-check may help build `CHK-<checkpoint>-evidence.json`, but formal acceptance pass depends on an independent review artifact.
