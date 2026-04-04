# Evaluator Calibration Profiles

## 1. Purpose

This document defines the shared evaluator calibration surface used in phase 1 by:

- `multi-agent-discussion-advisor` `preflight` mode
- `checkpoint-gatekeeper` `acceptance` profile

It is a repository-level support layer, not a standalone skill.

## 2. Why This Exists

The repository now has two review/gate consumers that both need sharper evaluation than generic review:

- pre-execution plan challenge
- post-implementation semantic acceptance

Without shared calibration, both surfaces risk drifting into:

- inconsistent thresholds
- high false positives
- vague or generic criteria

## 3. Calibration Rules

Apply these rules to every evaluator-style surface in this phase:

- Prefer task-specific criteria over reusable boilerplate.
- Require evidence-backed findings instead of intuition-only critique.
- Separate structural blockers from polish gaps.
- Bias toward `revise` or `needs_user_confirmation` when owner boundaries become ambiguous.
- Do not create a second lifecycle or verdict owner while calibrating strictness.

## 4. Consumer A: `preflight` Plan Review

### Goal

Challenge a proposed execution plan before implementation starts.

### Required Evidence

- proposed phase or sprint structure
- owner-boundary assumptions
- downstream review/gate expectations
- any existing matrix or decision record

### Evaluation Dimensions

- `boundary-clarity`
  - Are standalone skills, modes, profiles, and support layers clearly separated?
- `owner-integrity`
  - Does the plan preserve lifecycle truth and verdict ownership?
- `phase-soundness`
  - Are phase boundaries explicit and semantically justified?
- `evaluator-readiness`
  - Will later checkpoint or acceptance surfaces have explicit criteria to consume?

### Default Verdict Guidance

- `approve`
  - use when boundaries are clear, phases are explicit, and downstream evaluators have inputs
- `revise`
  - use when the direction is broadly correct but one or more boundaries or criteria are underspecified
- `block`
  - use when execution would likely create overlapping owners, hidden status machines, or major rework

### False-Positive Risks

- approving because the plan sounds organized even though owner boundaries are still fuzzy
- approving because examples exist, but no real downstream evaluation inputs are defined

### False-Negative Risks

- blocking a plan that is intentionally rough at the execution level but already sound at the boundary level
- treating deferred standalone extraction as weakness rather than deliberate scope control

## 5. Consumer B: `acceptance` Checkpoint Profile

### Goal

Assess whether a sprint or work slice is semantically complete while keeping verdict ownership under the existing checkpoint owner.

### Required Evidence

- execution contract for the slice
- smoke or regression outputs when applicable
- changed artifact paths
- example or documentation updates when they are part of the contract
- an independent acceptance review artifact for formal verification tasks

### Evaluation Dimensions

- `contract-closure`
  - Did the slice close the exact semantic scope it claimed?
- `evidence-sufficiency`
  - Is the required evidence present and consistent with the claim?
- `gap-severity`
  - Are remaining gaps cosmetic, or do they break semantic closure?
- `owner-preservation`
  - Did the work stay under checkpoint ownership without creating a new verdict surface?

### Default Verdict Guidance

- `pass`
  - contract closure is satisfied, evidence is sufficient, and independent review accepts the slice
- `auto_fixed_pass`
  - only when bounded remediation inside the checkpoint fixes the issue and the contract is then satisfied under independent review
- `fail`
  - semantic closure is not achieved within checkpoint bounds, or independent review blocks closure
- `needs_user_confirmation`
  - the checkpoint is close to done but acceptance depends on a risky standard change, ambiguous interpretation, or missing independent review evidence

### False-Positive Risks

- passing because tests are green while contract-specific negative cases still remain true
- passing because artifacts exist, but they do not prove semantic closure

### False-Negative Risks

- failing because the slice intentionally deferred out-of-scope work that is not part of the current contract
- failing because of minor polish gaps that do not break the slice's closure

## 6. Extraction Rule

Do not extract a standalone `evaluator-calibrator` skill yet.

Extraction becomes reasonable only when:

- at least two consumers are stable
- the profiles are reused across multiple tasks
- maintaining calibration inside repo-level knowledge becomes error-prone

## 7. Current Consumers

- `skills/multi-agent-discussion-advisor/`
- `skills/checkpoint-gatekeeper/`

## 8. Notes

This document is a shared repository asset for phase-1 calibration.
It is not a lifecycle owner, not a verdict surface, and not a runtime orchestrator.
