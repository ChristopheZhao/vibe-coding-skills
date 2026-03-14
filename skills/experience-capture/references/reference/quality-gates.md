# Quality Gates

## Gate A: 定位正确
- 条目是否属于“可复用经验”，而非项目状态日志。
- 是否避免与 `layered-project-memory` 职责重叠。

## Gate B: 触发低打扰
- 是否由主动触发或建议触发硬条件命中。
- 是否遵守“单节点最多询问一次”。
- 拒绝后是否进入冷却。

## Gate C: 内容可复用
- 是否包含明确 `problem_signature`。
- 是否包含可执行 `decision_rules` 与 `review_checklist`。
- 是否包含至少一个证据引用。

## Gate D: 可追溯
- 是否能回溯到来源节点（memory 事件或文档）。
- 引用是否是 pointer-first，避免复制大段日志。

## Gate E: 可检索
- 标签是否足够区分主题。
- 标题与签名是否可用于后续 list/filter。

## Gate F: 复杂场景产物完整
- 若任务存在明显多轮转折，且经验卡不足以解释 lesson 是如何形成的，是否补了简洁 source retrospective note。
- source retrospective note 是否只保留解释经验所需的最小过程脉络，而不是 session handoff 或完整过程日志。

## 失败处理
- 任一 gate 失败：不写入经验卡，提示补充信息。
- 若反复 gate 失败：建议改为普通总结，不进入经验库。
