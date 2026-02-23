# Plan Templates

## Feature Plan Template

Use this template for new capability development.

```markdown
# Plan: <title>
- Plan ID: <plan-id>
- Type: feature
- Status: draft
- Priority: <P0|P1|P2>
- Owner: <owner>
- Created At: <timestamp>

## 1. Requirement Analysis
- User intent:
- Scope in:
- Scope out:
- Acceptance criteria:

## 2. Functional Decomposition
- Module A:
- Module B:
- Module C:

## 3. Implementation Approach
- Data flow:
- API/contract changes:
- Migration or compatibility notes:

## 4. Technical Solution
- Key design choices:
- Trade-offs:
- Risks and mitigations:

## 5. Execution List (Priority Ordered)
- [ ] P0 Task 1
- [ ] P0 Task 2
- [ ] P1 Task 3

## 6. Test and Acceptance
- Unit tests:
- Integration tests:
- Manual verification:

## 7. Status Log
- <timestamp> draft created

## 8. Execution Handoff (Optional)
- Current focus:
- Blockers:
- Next resume action:
- Evidence pointers:
- Updated at:
```

## Fix/Refactor Plan Template

Use this template for bug fixes or refactor work.

```markdown
# Plan: <title>
- Plan ID: <plan-id>
- Type: fix
- Status: draft
- Priority: <P0|P1|P2>
- Owner: <owner>
- Created At: <timestamp>

## 1. Current Problem
- Symptom:
- Impact:
- Reproduction:

## 2. Deviation Analysis
- Expected behavior:
- Actual behavior:
- Root cause hypothesis:

## 3. Implementation Approach
- Patch strategy:
- Compatibility considerations:
- Rollback plan:

## 4. Execution Checklist
- [ ] Reproduce issue
- [ ] Implement fix/refactor
- [ ] Add or update tests
- [ ] Verify in target flow

## 5. Test and Validation
- Test cases:
- Regression checks:
- User-facing validation points:

## 6. Status Log
- <timestamp> draft created

## 7. Execution Handoff (Optional)
- Current focus:
- Blockers:
- Next resume action:
- Evidence pointers:
- Updated at:
```
