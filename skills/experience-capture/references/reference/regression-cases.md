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

## Case 5: 复杂多轮经验沉淀（应双产物）
- Input:
  - 用户要求“认真总结一下，需要有一些简单过程记录，然后做经验总结”。
  - 背景是复杂多轮纠偏，但当前主目标仍是沉淀可复用 lessons，而不是给下个窗口做 handoff。
- Expected:
  - 命中 `manual-explicit`。
  - 输出 `experience card + source retrospective note`，而不是只有经验卡。
  - source retrospective note 写入 `docs/experience/sources/` 并被经验卡锚点引用。

## Case 6: 当前窗口交接 / 下个窗口续做（不应由 experience-capture 覆盖）
- Input:
  - 用户要求整理当前窗口做了什么、还剩什么、下个窗口先读什么。
  - 主目标是把同一任务安全移交到新窗口继续。
- Expected:
  - 不应继续扩张 `experience-capture`。
  - 推荐使用 `session-handoff`。
  - 若其中存在明确可复用 lessons，再额外提炼经验卡。

## Case 7: 完整 continuity / 项目状态恢复（应转 layered-project-memory）
- Input:
  - 用户要求为下个窗口恢复完整现场、保留项目状态、避免继续丢上下文。
- Expected:
  - 识别该需求主目标是 continuity / handoff。
  - 推荐使用 `layered-project-memory`。
  - 若其中存在明确可复用 lessons，再提炼为经验卡。
