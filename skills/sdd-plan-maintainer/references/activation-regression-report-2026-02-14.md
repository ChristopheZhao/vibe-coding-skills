# Activation Regression Report (2026-02-14)

## Method
Evaluate six regression prompts against the current activation gate in `SKILL.md`.
Gate requires both:
1. explicit plan-governance intent, and
2. durable plan-asset intent under `docs/plans/`.

## Results

1) Explicit plan governance start
- Prompt: `为这个重构创建一个长期计划文档，放到 docs/plans，并给出 Plan ID。`
- Expected: Activate
- Actual: Activate
- Verdict: PASS
- Reason: Contains explicit plan-doc governance and explicit durable target path `docs/plans`.

2) Status governance update
- Prompt: `把 PLAN-20260214-003 更新到 testing，并记录测试证据说明。`
- Expected: Activate
- Actual: Activate
- Verdict: PASS
- Reason: Contains plan ID and status-management intent.

3) Completion + archive governance
- Prompt: `这个计划用户已确认，帮我把 PLAN-20260214-003 归档。`
- Expected: Activate
- Actual: Activate
- Verdict: PASS
- Reason: Contains explicit archive governance for a plan ID.

4) Generic coding task with no durable plan assets
- Prompt: `给这个接口加一个分页参数并补上测试。`
- Expected: Do not activate
- Actual: Do not activate
- Verdict: PASS
- Reason: No plan-governance or durable-plan-asset intent.

5) Brainstorming only
- Prompt: `帮我想一下这个模块怎么拆分比较好。`
- Expected: Do not activate
- Actual: Do not activate
- Verdict: PASS
- Reason: Exploration-only request with no plan-asset governance intent.

6) Long-running execution request without governance intent
- Prompt: `按你的方案把这个功能完整实现完。`
- Expected: Do not activate
- Actual: Do not activate
- Verdict: PASS
- Reason: Implementation execution request; governance skill should stay out unless milestones require plan-state operations.

## Summary
- Passed: 6/6
- Failed: 0/6
- Drift observed: None

## Notes
This report validates trigger-policy conformance against the skill definition.
If runtime trigger behavior in the host product deviates, update `description` and rerun this suite.
