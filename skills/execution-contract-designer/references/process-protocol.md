# Process Protocol

## 1. Frame the Slice
Capture:
- work-slice title
- what it closes
- why this boundary exists
- downstream owners

## 2. Define Semantic Closure
Describe the concrete before/after difference this slice should produce.

## 3. Author the Contract
Produce:
- `what`
- `why`
- `done signals`
- `evidence checklist`
- `negative cases`

## 4. Map Suggested Checkpoints
Suggest which later checkpoint or acceptance surfaces should consume this contract.

## 5. Hand Off Cleanly
- planning updates next -> `sdd-plan-maintainer`
- checkpoint consumption next -> `checkpoint-gatekeeper`

Do not mutate lifecycle state or emit verdicts inside this skill.
