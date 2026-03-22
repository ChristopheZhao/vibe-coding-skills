# Activation Regression Cases

Use this file to sanity-check trigger scope. The goal is high precision without overfitting to asset keywords.

## Should Activate

1) Specific plan refinement request
Prompt:
- `请重新按需求规划一个更具体、有针对性的修复计划。`
Expected:
- Activate `sdd-plan-maintainer`.
- Produce a concrete fix plan with modules, priority, execution checklist, and validation items.
- Planning mode is acceptable if persistent files were not requested.

2) Explicit plan governance start
Prompt:
- `请给这个重构创建一个长期计划文档，放到 docs/plans，并生成 Plan ID。`
Expected:
- Activate `sdd-plan-maintainer`.
- Ensure `docs/plans` structure and `PLAN_INDEX.json`.
- Create a plan artifact and register it.

3) Status governance update
Prompt:
- `请把 PLAN-20260214-003 更新到 testing，并补一条测试证据说明。`
Expected:
- Activate `sdd-plan-maintainer`.
- Update lifecycle status with note.
- Keep index and artifact state consistent.

4) Invalidated plan governance update
Prompt:
- `这个计划方向错了，帮我把 PLAN-20260214-003 标记成 superseded，并写清楚替代判断。`
Expected:
- Activate `sdd-plan-maintainer`.
- Update lifecycle status to `superseded` with a note that records why the plan stopped and what replaced it.
- Keep the old plan available as history without letting it remain an active execution target.

5) Completion plus archive governance
Prompt:
- `我这边已经确认了，帮我把 PLAN-20260214-003 归档。`
Expected:
- Activate `sdd-plan-maintainer`.
- Verify completion and confirmation gates.
- Archive under `docs/plans/archive/YYYY-MM/` and sync index.

## Should Not Activate

1) Generic coding task with no planning intent
Prompt:
- `给这个接口加一个分页参数并补上测试。`
Expected:
- Do not activate `sdd-plan-maintainer`.
- Use default Codex planning and execution.

2) Brainstorming only
Prompt:
- `帮我想一下这个模块怎么拆分比较好。`
Expected:
- Do not activate `sdd-plan-maintainer`.
- Provide normal analysis without entering plan governance.

3) Long-running implementation only
Prompt:
- `按你的方案把这个功能完整实现完。`
Expected:
- Do not keep `sdd-plan-maintainer` active for full execution.
- Use default Codex execution loop.
- Re-enter this skill only if plan governance milestones are requested.

4) Handoff sync without governance intent
Prompt:
- `把当前执行上下文写进计划文档的 Execution Handoff 段，先别改计划状态。`
Expected:
- If already in managed plan flow, update execution handoff only.
- Do not change lifecycle status unless user asks for governance transition.

## Drift Signals

If any signal appears, tighten or rebalance activation wording:
- Skill does not trigger for explicit plan refinement requests.
- Skill triggers on ordinary coding asks without planning intent.
- Skill stays active across full implementation instead of milestone governance.
- User reports unexpected plan or index writes.
- Execution handoff notes start carrying lifecycle status fields.
- Invalidated plans keep showing up as active execution targets because they were not moved out of open status semantics.

## Maintenance Rule

When updating trigger text, rerun these cases and record pass or fail notes before release.
