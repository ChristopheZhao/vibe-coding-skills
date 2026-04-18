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

## Deferred Constraints Applied (Optional)
- Source:
- Do not:
- Allowed now:
- Reopen trigger:

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

## Deferred Constraints Applied (Optional)
- Source:
- Do not:
- Allowed now:
- Reopen trigger:

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

## Companion Governance Docs

Use these templates when the repo needs a managed plan package instead of forcing all governance detail into the main plan body.
The main plan stays the only lifecycle-bearing asset.

### Validation Ledger Template

```markdown
# PLAN-<plan-id> Validation

- Plan ID: <plan-id>
- Recorded At: <timestamp>
- Status: <mirror of current lifecycle status, optional narrative mirror only>

## Purpose
- Record phase-by-phase verification for the main plan.
- Link review, test, and evidence surfaces without replacing their authoritative owner.

## Validation Matrix
### <Stage or Sprint Name>
- Status:
- Planned checks:
  - <review checkpoint>
  - <test checkpoint>
  - <regression checkpoint>
- Evidence:
  - <file or artifact ref>
  - <command result or review artifact ref>
- Results:
  - <pass/fail summary>

## Notes
- <timestamp> <short validation milestone summary>
```

### Stage Governance Freeze Template

```markdown
# Stage <A|B|C> <Title>: PLAN-<plan-id>

## Scope
- Freeze this stage before implementation or the next bounded slice begins.

## Review Conclusion
- <approve/revise/block summary>

## Exact Deliverables
- D1.
- D2.

## Verify Gate
- [ ] boundary review recorded
- [ ] targeted validation or evidence links recorded
- [ ] next-stage prerequisites are explicit

## Evidence Refs
- <main plan>
- <validation ledger>
- <supporting docs/tests/code>
```

### Stage Responsibility Inventory Template

```markdown
# Stage <A|B|C> Responsibility Inventory: PLAN-<plan-id>

## Scope
- Inventory current owner surfaces and unresolved authority conflicts for this stage.

## Inventory Table
| Surface | Current owner | Current write surface | Risk or drift | Keep / move / remove |
| --- | --- | --- | --- | --- |
| <surface> | <owner> | <writer> | <risk> | <decision> |

## Boundary Verdict
- <what remains with current owner>
- <what must move behind a tighter facade>
- <what is diagnostics-only>

## Evidence Refs
- <files or prior stage docs>
```

### Stage Bounded Slice Template

```markdown
# Stage <A|B|C> Bounded Slice: PLAN-<plan-id>

## Goal
- Define one bounded implementation slice after governance freeze and responsibility review.

## In Scope
- <target change area>

## Out of Scope
- <explicit non-goals>

## Target Files
- <file path>

## Validation Plan
- <targeted tests>
- <review checkpoints>
- <evidence refs>
```
