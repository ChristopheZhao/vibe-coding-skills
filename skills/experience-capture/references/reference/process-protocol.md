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

4. `persist`
- 在用户确认写入后，调用 `exp_ops.py create` 写入经验卡。
- 调用 `exp_ops.py link` 关联 `source_event_refs` 或 `doc_refs`。

5. `reuse`
- 后续遇到相似场景时，通过 `exp_ops.py list` 按签名/标签检索。
- 引用卡片中的 `review_checklist` 与 `decision_rules` 进行引导。

## 对话提示建议
- 显式触发命中（无需建议询问）：
  - "我将按经验卡格式沉淀本次结论，并写入可复用记录。"
- 建议保存提问（一次，仅 suggest-once）：
  - "这次我们已经形成可复用的方法，是否要沉淀为经验卡，供后续类似问题直接复用？"
- 拒绝后回应：
  - "已记录本轮不保存经验，当前主题暂不再提醒。"

## 故障回退
- 任何字段缺失或引用为空时，停止写入并提示补全。
- 存储初始化缺失时，先执行 `exp_ops.py init`。
