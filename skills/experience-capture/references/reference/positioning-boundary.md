# Experience Capture: 定位与边界

## 定位
- 目标：把高价值讨论或难题攻坚过程，沉淀为可复用经验卡。
- 价值：减少重复踩坑、提升对齐效率、提供跨项目可迁移的决策模板。
- 本质：先验知识与经验工作流 skill，不是业务运行时模块。

## In Scope
- 经验条目抽取：问题签名、关键决策、反模式、检查清单。
- 用户确认后写入经验库。
- 与项目文档/记忆节点建立引用关系。
- 按标签或问题签名检索经验。

## Out of Scope
- 不做运行时编排决策引擎。
- 不做系统级监听器。
- 不存储整段对话或完整日志镜像。
- 不替代 Git 与 `layered-project-memory`。

## 与 layered-project-memory 的关系
- `layered-project-memory`：面向项目连续性，记录状态与关键事件。
- `experience-capture`：面向跨任务复用，提炼“可复用经验规则”。
- 关系：可关联，不重叠。
  - 经验卡可引用 memory 事件 ID。
  - 不复制 memory 正文。
