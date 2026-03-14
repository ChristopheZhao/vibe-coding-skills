# Process Protocol

## 标准流程
1. `detect`
- 先判断是否为 `manual-explicit`（用户明确要求经验沉淀/形成记录）。
- 若不是显式触发，再判断是否满足 `suggest-once` 硬条件。

2. `ask`
- `manual-explicit` 路径：可跳过“建议询问”，直接进入抽取。
- `suggest-once` 路径：使用一次性确认问题，是否将本次经验沉淀为可复用经验卡。
- 若 `suggest-once` 被拒绝，记录拒绝事实并进入冷却，不继续抽取。

3. `extract`
- 从已对齐内容抽取最小经验卡字段：
  - `problem_signature`
  - `decision_rules`
  - `anti_patterns`
  - `review_checklist`

4. `shape`
- 默认使用 `card-only`。
- 当满足任一条件时，升级为 `dual-output`：
  - 用户明确要“补简单过程记录”，但主目标仍是经验提炼。
  - 任务是复杂多轮纠偏，且仅写经验卡会丢失 1-2 个关键转折或根因判断。
  - 本次产物仍聚焦一个主要 lesson cluster，而不是 session 交接或完整项目复盘。
- 如果需求已经变成“为下个窗口提供 continuation / 做 context offload / 恢复完整现场”，不要继续扩张本 skill；改用 `session-handoff` 或 `layered-project-memory`，并在需要时从其产物中提炼经验卡。

5. `source-note`（仅 `dual-output`）
- 在 `docs/experience/sources/` 写一份简洁 source retrospective note。
- 建议包含：
  - 背景与原目标
  - 关键转折 / root cause
  - 与该经验直接相关的已完成成果
  - 为什么该经验重要
- 不写成逐轮流水账，不复制大段对话，不包含 next-window boot / handoff 指令。

6. `persist`
- 在用户确认写入后，调用 `exp_ops.py create` 写入经验卡。
- `dual-output` 优先把 source retrospective note 的锚点写入 `source_event_refs`。
- 调用 `exp_ops.py link` 关联补充的 `source_event_refs` 或 `doc_refs`。

7. `reuse`
- 后续遇到相似场景时，通过 `exp_ops.py list` 按签名/标签检索。
- 引用卡片中的 `review_checklist` 与 `decision_rules` 进行引导。

## 对话提示建议
- 显式触发命中（无需建议询问）：
  - "我将按经验卡格式沉淀本次结论，并写入可复用记录。"
  - 若判断为复杂场景，可补一句："这次过程本身也有复用价值，我会同时补一份简洁复盘来源文档，作为经验卡证据。"
- 建议保存提问（一次，仅 suggest-once）：
  - "这次我们已经形成可复用的方法，是否要沉淀为经验卡，供后续类似问题直接复用？"
- 拒绝后回应：
  - "已记录本轮不保存经验，当前主题暂不再提醒。"

## 故障回退
- 任何字段缺失或引用为空时，停止写入并提示补全。
- 存储初始化缺失时，先执行 `exp_ops.py init`。
