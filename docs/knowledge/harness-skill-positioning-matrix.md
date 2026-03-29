# Long-Running Harness Skill Positioning Matrix

## 1. 文档目的

本记录用于整理一轮围绕 Anthropic 文章
“Harness design for long-running application development”
（2026-03-24）的讨论结果，明确：

- 哪些新能力值得作为独立 skill 存在
- 哪些能力更适合先并入现有 skill 或作为 profile 演进
- 候选 skill 与现有 skill 的 ownership boundary 应如何切分

本记录是 skill 设计与评审基线，不是 runtime harness 设计稿。

## 2. 仓库前提

本仓库当前定位仍是 guidance-first 的可复用 skill 库，而不是长时 autonomous orchestrator。

因此新能力应优先满足：

- 可跨项目复用
- 解决高频高成本 workflow 痛点
- 输出可被后续任务直接消费的结构化产物
- 不引入第二套 lifecycle/status machine
- 不把 skill 演化成 runtime orchestration 模块

## 3. 三视角综合结论

本次讨论综合了三种视角：

- 产品价值：这个 skill 是否真的解决高频高成本痛点
- Harness 架构：这个 skill 是否与现有 owner 重叠或引入第二真相源
- Evaluator / review：这个 skill 是否改善阶段性审阅与验收，而不是重复 generic review

最终结论：

- 应独立新增的核心层：
  - `execution-mode-selector`
  - `execution-contract-designer`
- 应先并入现有 skill 的：
  - `preflight-plan-review`
  - `acceptance-review-gate`
- 应先作为共享支撑层的：
  - `evaluator-calibrator`
- 应合并而不是并排存在的：
  - `complexity-sprint-decider`
  - `harness-pattern-selector`

## 4. 候选 Skill 结论表

| 候选项 | 结论 | 核心价值 | 推荐形态 |
| --- | --- | --- | --- |
| `complexity-sprint-decider` | 合并 | 避免复杂任务默认 one-shot | 并入 `execution-mode-selector` |
| `harness-pattern-selector` | 合并 | 选择最小足够执行形态 | 并入 `execution-mode-selector` |
| `execution-mode-selector` | 保留 | 执行前拓扑选择：`one-shot / research-first / sprint-required / discussion-first` | 新独立 skill |
| `execution-contract-designer` | 保留 | 把 coarse sprint 变成可评估 contract | 新独立 skill |
| `preflight-plan-review` | 合并 | 执行前多角色 challenge 计划合理性 | `multi-agent-discussion-advisor` 的 `preflight` 模式 |
| `acceptance-review-gate` | 合并 | 交付后判断“任务是否真的完成” | `checkpoint-gatekeeper` 的 `acceptance` profile |
| `evaluator-calibrator` | 暂不独立 | 统一 rubric、threshold、examples、few-shot 校准 | 共享 `references/profile`，后续视复用再抽 skill |

## 5. Ownership Matrix

| 关注面 | 推荐 owner | 产物 | 明确不做什么 |
| --- | --- | --- | --- |
| 执行形态选择 | `execution-mode-selector` | mode verdict、why、粗粒度 sprint 拓扑 | 不写 plan lifecycle、不发 checkpoint verdict |
| sprint 合同设计 | `execution-contract-designer` | `what / why / done signal / evidence / negative cases / suggested checkpoints` | 不做验证执行、不改 plan 状态 |
| 执行前方案审阅 | `multi-agent-discussion-advisor` `preflight` 模式 | `approve / revise / block` 建议、角色分工、风险提示 | 不拥有 lifecycle truth、不替代 plan maintainer |
| plan lifecycle truth | `sdd-plan-maintainer` | plan status、completion/archive governance | 不负责前置模式选择、不负责 acceptance 验收 |
| checkpoint verdict artifacts | `checkpoint-gatekeeper` | checkpoint verdict、bounded remediation artifacts | 不拥有 plan lifecycle、不演化成通用 orchestrator |
| 交付/阶段验收 | `checkpoint-gatekeeper` `acceptance` profile | acceptance judgement、evidence-backed gap list | 不变成第二个 plan status machine |
| evaluator rubric / calibration | 共享 `evaluator-calibrator` profiles | rubric、threshold、examples、few-shot、FP/FN 对齐 | 不做执行、不做 plan/status ownership |
| continuity memory | `layered-project-memory` | 项目连续性语义记忆 | 不接管 lifecycle 或 evaluator verdict |
| session offload | `session-handoff` | 当前窗口 continuation pack | 不写 plan/memory/experience 真相 |
| reusable lessons | `experience-capture` | 经验卡、source retrospective | 不替代 calibration profile |

## 6. 各候选项的价值、定位、边界

### 6.1 `execution-mode-selector`

#### 价值

- 解决“复杂任务默认 one-shot”这一前置误判
- 在执行前输出最小足够 harness 形态
- 让 sprint 化成为明确策略，而不是失败后的补救动作

#### 定位

执行前的 meta selector。

它回答的问题是：

- 这件事能否 `one-shot`
- 是否应 `research-first`
- 是否必须 `sprint-required`
- 是否应先 `discussion-first`

#### 边界

- 只负责 mode selection 与粗粒度 sprint 拓扑
- 不拥有 `docs/plans/PLAN_INDEX.json`
- 不发 checkpoint verdict
- 不做任务完成验收

### 6.2 `execution-contract-designer`

#### 价值

- 补上“plan”和“gate/evaluator”之间的空层
- 把一个 sprint 从“要做什么”变成“如何算通过”
- 为后续 checkpoint 与 acceptance 提供统一输入

#### 定位

从 coarse sprint 到 evaluable contract 的桥接层。

#### 边界

- 只产 contract
- contract 应包含：
  - `what`
  - `why`
  - `done signal`
  - `evidence checklist`
  - `negative cases`
  - `suggested checkpoints`
- 不改 lifecycle 状态
- 不执行验证
- 不输出最终验收 verdict

### 6.3 `preflight-plan-review`

#### 价值

- 在 generator / implementation 开始前挑战 scope、假设、风险与可验证性
- 避免 plan 在执行后期才暴露结构性错误

#### 定位

执行前方案审阅 gate。

#### 边界

- 先作为 `multi-agent-discussion-advisor` 的 `preflight` 模式
- 输出 `approve / revise / block` 建议
- 保持 discussion-phase 角色设计与收敛逻辑
- 不单独拥有 plan lifecycle 或 checkpoint artifact

### 6.4 `acceptance-review-gate`

#### 价值

- 补上“代码写了”与“任务真的完成了”之间的语义验收层
- generic review 无法替代任务特定 acceptance
- 适合在 sprint 结束或最终交付后使用

#### 定位

阶段性或最终交付后的 acceptance layer。

#### 边界

- v1 先作为 `checkpoint-gatekeeper` 的 `acceptance` profile
- 读取 checkpoint 证据、测试结果、contract 与用户目标
- 输出 acceptance judgement 与 gap list
- 不成为第二个 plan status machine

### 6.5 `evaluator-calibrator`

#### 价值

- 统一 evaluator 的 rubric、threshold 与 examples
- 减少 false-positive / false-negative 漂移
- 为不同阶段的 review / gate 提供共享 profile

#### 定位

review / evaluator 的配置与校准层。

#### 边界

- v1 先作为共享 `references/profile`
- 只产 profile，不直接执行 review / gate
- 不做 plan、不做执行、不做 memory truth
- 当至少有两个消费者稳定复用同一套 calibration contract 时，再考虑独立为 skill

## 7. 与现有 Skill 的硬边界

### 7.1 不可改变的 owner

- 只有 `sdd-plan-maintainer` 可以拥有 plan lifecycle truth
- 只有 `checkpoint-gatekeeper` 可以拥有 checkpoint verdict artifacts
- 只有 `layered-project-memory` 与 `session-handoff` 可以继续拥有 continuity surfaces

### 7.2 明确禁止的演化方向

- 不新增第二套 lifecycle/status machine
- 不把新 skill 做成长时 autonomous orchestrator
- 不让 `execution-mode-selector` 侵入 plan 或 gate ownership
- 不让 `evaluator-calibrator` 取代实际 review / acceptance surface

## 8. 推荐落地顺序

1. 新增 `execution-mode-selector`
2. 新增 `execution-contract-designer`
3. 为 `multi-agent-discussion-advisor` 增加 `preflight` 模式
4. 为 `checkpoint-gatekeeper` 增加 `acceptance` profile
5. 整理共享 `evaluator-calibrator` profiles
6. 视使用频率再决定：
   - 是否将 `acceptance-review-gate` 独立
   - 是否将 `evaluator-calibrator` 独立

## 9. 后续行动建议

如果继续向实现推进，建议下一步按以下顺序进行：

1. 先写 `execution-mode-selector` 的 `SKILL.md`
2. 再写 `execution-contract-designer` 的 `SKILL.md`
3. 给 `multi-agent-discussion-advisor` 补 `preflight` 模式说明
4. 给 `checkpoint-gatekeeper` 补 `acceptance` profile 约束
5. 最后再抽出 evaluator calibration 的共享 contract

## 10. 半期路线判断

当前这组 phase-1 harness 增量，适合作为一个技术优化路线图的半期落点，而不是继续向更重的 orchestrator 或 standalone evaluator 系统推进。

### 当前阶段建议

- 将现有实现视为 phase-1 基线能力：
  - `execution-mode-selector`
  - `execution-contract-designer`
  - `multi-agent-discussion-advisor` `preflight`
  - `checkpoint-gatekeeper` `acceptance`
  - 共享 `evaluator-calibration` knowledge layer
- 先通过真实 vibe coding 使用场景验证这些能力是否足够覆盖中等复杂度、多阶段、需要阶段验收的任务。
- 不为了理论完备性继续前推 standalone `acceptance-review-gate`、standalone `evaluator-calibrator` 或更重的 long-running orchestrator。

### 后续是否继续扩展的判断信号

仅当实践中重复出现以下稳定缺口时，再进入下一阶段优化：

- `acceptance` profile 反复因为语义判断不足而需要大量人工补充
- sprint 之间仍频繁出现边界漂移、阶段目标失真或未显式 closure
- `preflight` 讨论在多个任务里重复出现同类评审结构，值得进一步模板化或抽 skill
- evaluator calibration 在多个 review/gate 消费方之间开始明显漂移
- continuity memory 与 session handoff 无法支撑实际多窗口长任务

### 路线原则

- 优先补高频高成本、跨项目可复用的缺口
- 只在真实使用验证后再提升抽象层级
- 保持 guidance-first，不把 skill 仓库演化为业务 runtime orchestration 模块

## 10. 来源

- Anthropic, “Harness design for long-running application development” (2026-03-24): https://www.anthropic.com/engineering/harness-design-long-running-apps

## 11. 合理性复核（结合社区实践）

本节用于回答一个额外问题：

当前结论是否只是在内部讨论中“看起来合理”，还是也得到了主流 coding agent / vibe coding 社区实践的支持。

复核结论：

- 整体方向合理
- 其中最稳的两层是：
  - `execution-mode-selector`
  - `execution-contract-designer`
- `preflight-plan-review`、`acceptance-review-gate`、`evaluator-calibrator` 的需求本身成立
- 但它们在 v1 是否应独立成顶层 skill，需要更保守

### 11.1 哪些结论被外部实践强支撑

#### A. 不应默认 solo 一次性完成复杂任务

这一点被多类实践支持：

- Anthropic 在 long-running harness 文章中强调：当任务跨度、上下文压力、跨阶段验证需求升高时，需要引入 sprint contract、阶段切换与 evaluator，而不是默认单次 rollout 覆盖全部复杂度。
- Aider 的使用建议强调复杂任务应拆成 bite-sized steps，而不是一次性塞给模型。
- 多 agent / subagent 文档也普遍强调 focused context 和 scoped tasks，而不是让单 agent 持续承载所有不确定性。

因此，把：

- `complexity-sprint-decider`
- `harness-pattern-selector`

合并为一个前置 `execution-mode-selector`，是合理且符合社区经验的。

#### B. 在 plan 与 verification 之间补一层 contract bridge

这点是当前结论里最稳的一项。

外部实践表明：

- 高层计划本身并不等于可验证执行单元
- evaluator / acceptance 需要 task-specific criteria
- 如果没有显式 contract，后续 review 往往只能退化成 generic review

因此新增 `execution-contract-designer` 是合理的，而且应优先于更复杂的 review/evaluator 技术层。

### 11.2 哪些结论成立，但更适合先做 mode / profile / support layer

#### A. `preflight-plan-review`

社区实践支持“执行前先 challenge 方案”这一需求，但常见形态通常是：

- `ask`
- `architect`
- dedicated reviewer agent
- preflight discussion mode

而不是一个单独的顶层 lifecycle owner。

因此将其先并入 `multi-agent-discussion-advisor` 的 `preflight` 模式，比直接独立成 skill 更稳妥。

#### B. `acceptance-review-gate`

社区实践也支持“实现完成后专门验收”这一层。

但从系统形态看，更常见的是：

- 作为 gate profile
- 作为 task-specific evaluation pass
- 作为 completion review stage

而不是立刻新增第二套 verdict owner。

因此，v1 先将其做成 `checkpoint-gatekeeper` 的 `acceptance` profile，是合理的折中。

#### C. `evaluator-calibrator`

外部实践一致支持 evaluator 必须校准：

- 需要 task-specific rubric
- 需要 examples / few-shot
- 需要根据 false-positive / false-negative 持续调节
- 需要 human feedback 校正 automated scoring

但这些实践并不强支持它在早期一定要成为用户直接触发的顶层 skill。

更常见的做法是先形成共享 calibration surface，再在复用足够稳定后抽象为独立系统。

因此，先把 `evaluator-calibrator` 作为共享 `references/profile` 层，而不是直接立项为顶层 skill，是更稳的路线。

### 11.3 对当前结论的修正

复核后建议将原结论理解为：

1. `execution-mode-selector`
   - 合理
   - 应优先独立

2. `execution-contract-designer`
   - 合理
   - 应优先独立

3. `preflight-plan-review`
   - 合理
   - 但优先作为 `multi-agent-discussion-advisor` 的 mode

4. `acceptance-review-gate`
   - 合理
   - 但优先作为 `checkpoint-gatekeeper` 的 profile

5. `evaluator-calibrator`
   - 合理
   - 但优先作为共享 support layer，而不是顶层 skill

### 11.4 最终复核判断

因此，本记录前文的 matrix 结论可以保留，但应明确理解为：

- 当前推荐的是“独立 skill + mode + profile + support layer”的组合演进路线
- 而不是“把所有合理能力都立刻做成顶层独立 skill”

这既符合：

- 本仓库 guidance-first 的定位
- 当前已有 owner boundary
- 也符合主流 coding agent / vibe coding 社区的工程实践

### 11.5 外部参考

- Anthropic, “Harness design for long-running application development” (2026-03-24): https://www.anthropic.com/engineering/harness-design-long-running-apps
- OpenAI, “Evaluation best practices”: https://developers.openai.com/api/docs/guides/evaluation-best-practices
- Anthropic, “Create custom subagents”: https://code.claude.com/docs/en/sub-agents
- Aider, “Tips”: https://aider.chat/docs/usage/tips.html
- Aider, “Chat modes”: https://aider.chat/docs/usage/modes.html
- Aider, “Separating code reasoning and editing” (2024-09-26): https://aider.chat/2024/09/26/architect.html
- Cursor, “Building a better Bugbot” (2026-01-15): https://cursor.com/blog/building-bugbot
- Cursor, “Bugbot”: https://cursor.com/bugbot

---

本记录是“skill 设计与边界对齐基线”，用于指导后续是否立项为独立 skill、mode 或 profile，不直接等同于实现计划。
