# Experience Capture: 定位与边界

## 定位
- 目标：把高价值讨论或难题攻坚过程，沉淀为可复用经验卡。
- 价值：减少重复踩坑、提升对齐效率、提供跨项目可迁移的决策模板。
- 本质：先验知识与经验工作流 skill，不是业务运行时模块。

## In Scope
- 经验条目抽取：问题签名、关键决策、反模式、检查清单。
- 对复杂任务补一份简洁的 source retrospective note，作为经验卡的证据上下文。
- 对复杂多轮任务，用一份简洁 source note 概括产生该经验的 1-2 个关键转折。
- 用户确认后写入经验库。
- 与项目文档/记忆节点建立引用关系。
- 按标签或问题签名检索经验。

## Out of Scope
- 不做运行时编排决策引擎。
- 不做系统级监听器。
- 不存储整段对话或完整日志镜像。
- 不替代 Git 与 `layered-project-memory`。
- 不做 session-level handoff / context offload。
- 不把 source retrospective note 写成项目全量过程日志。
- 不拥有面向后续恢复现场的完整研发过程归档与 continuity 记忆。

## 与其他 skill 的关系
- `session-handoff`：面向当前窗口收口与下个窗口续做。
- `layered-project-memory`：面向项目连续性，记录状态与关键事件。
- `experience-capture`：面向跨任务复用，提炼“可复用经验规则”；复杂场景下可补一份简洁 source retrospective note 作为经验证据。
- 关系：可关联，不重叠。
  - 经验卡可引用 memory 事件 ID。
  - source retrospective note 只保留本次经验所需的最小过程脉络，不复制 memory 正文。
  - 如果目标是当前窗口交接、恢复同一任务、为下个窗口准备上下文，应使用 `session-handoff`。
  - 如果目标是长期 continuity 记忆或恢复完整项目状态，应使用 `layered-project-memory`。
