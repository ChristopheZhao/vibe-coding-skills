# Regression Cases

## Case 1: 用户主动触发（应命中）
- Input:
  - 用户明确要求“把这次经验沉淀下来”。
- Expected:
  - 进入 `manual-explicit -> extract -> persist` 流程。
  - 在用户确认后创建经验卡。

## Case 1b: 显式中文短语触发（应强命中）
- Input:
  - 用户输入：“总结一下上面讨论的经验形成记录”。
- Expected:
  - 走 `manual-explicit` 路径，不被低打扰或冷却规则拦截。
  - 允许跳过建议询问，直接进入经验卡抽取与写入确认。

## Case 2: 系统建议触发（应命中，且只问一次）
- Input:
  - 多轮对齐后形成稳定可复用规则。
- Expected:
  - 仅一次建议保存询问。
  - 用户确认后写入；拒绝则不写入。

## Case 3: 用户拒绝后冷却（应抑制）
- Input:
  - 用户已拒绝当前主题的保存建议。
- Expected:
  - 冷却窗口内不重复询问（仅针对 suggest-once）。
  - 继续执行主任务，不中断流程。

## Case 4: 引用关联（应可追溯）
- Input:
  - 新建经验卡并链接 memory event 与文档。
- Expected:
  - `source_event_refs` 与 `doc_refs` 可追溯。
  - 不复制大段日志正文。
