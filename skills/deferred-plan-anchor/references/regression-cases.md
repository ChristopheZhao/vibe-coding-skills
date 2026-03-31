# Regression Cases

## Positive Cases
1. A long-term migration direction is accepted, but the user explicitly says not to execute it now and wants current planning guardrails.
2. A temporary dual-write surface must stop expanding until a later cleanup plan exists.
3. The host workflow asks whether current planning should inherit an active deferred plan.

## Negative Cases
1. The user only asks for a concrete feature or fix plan.
2. The request is still architecture discussion with no deferred-but-binding decision.
3. The request is generic backlog, roadmap, or prioritization work.

## Safety Cases
1. No `docs/deferred-plans/` root exists.
   - Expected: `resolve-for-planning` no-ops and does not fail.
2. Multiple deferred plans become `active`.
   - Expected: `doctor` reports an issue and `resolve-for-planning` refuses to apply guardrails.
3. A deferred plan is `superseded` or `completed`.
   - Expected: it stops affecting `CURRENT.md` and planning resolution before archive movement.
4. Scope/topic tags do not match the current planning context.
   - Expected: no-op planning result, not forced guardrail application.
