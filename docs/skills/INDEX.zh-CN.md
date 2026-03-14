[English](INDEX.md) | 简体中文

# Skills 目录

这个目录页提供本仓库当前公开 skills 的统一入口。
每个 skill 的语义真相仍以对应的 `skills/<slug>/SKILL.md` 为准。

| Skill | 核心价值 | 典型产出 | 适用场景 | 边界说明 | 阅读入口 |
| --- | --- | --- | --- | --- | --- |
| `sdd-plan-maintainer` | 让复杂编码任务变得可执行、可治理 | 具体计划 + 生命周期状态更新 | 用户要求具体功能/修复计划、进度跟踪或计划收口时 | 负责 plan lifecycle，不负责 runtime orchestration | [SKILL.md](../../skills/sdd-plan-maintainer/SKILL.md) |
| `session-handoff` | 为新窗口续做卸载当前 session 上下文 | session continuation pack | 当前窗口需要在继续同一任务前，先总结进展、阻碍和下一步 | 负责 session 级聚合，不拥有 plan/memory/experience 真相 | [SKILL.md](../../skills/session-handoff/SKILL.md) |
| `layered-project-memory` | 保持中断工作后的项目连续性 | 分层记忆记录 + 聚焦上下文包 | 用户需要持久项目状态、关键事件、重复尝试记忆或 resume/debug/release 上下文时 | 负责 continuity memory，不负责经验卡持久化 | [SKILL.md](../../skills/layered-project-memory/SKILL.md) |
| `experience-capture` | 将高价值经验沉淀为可复用指导 | 经验卡片 | 用户要求总结可复用 lessons、决策规则或 review checklist 时 | 负责跨任务经验，不负责下个窗口 handoff | [SKILL.md](../../skills/experience-capture/SKILL.md) |
| `knowledge-refresh` | 用外部证据降低过时假设带来的风险 | 基于来源的结论判定 | 技术判断需要校验、官方新鲜度或更强证据后再决策时 | 依赖权威外部来源，不替代本地代码调试 | [SKILL.md](../../skills/knowledge-refresh/SKILL.md) |
| `multi-agent-discussion-advisor` | 在执行前提升复杂讨论质量 | discussion advisory card + 启动说明 | 高不确定性的产品/需求/架构讨论需要真实多角色综合判断时 | 只做 advisory，不直接做实现或 runtime orchestration | [SKILL.md](../../skills/multi-agent-discussion-advisor/SKILL.md) |

## 说明

- 本页是公开目录，不是技能语义真相源。
- 具体 workflow、触发规则、反目标以各 skill 的 `SKILL.md` 为准。
- 仓库结构与跨工具发布规则继续见 [README.zh-CN.md](../../README.zh-CN.md) 和 [docs/compatibility/skills-matrix.md](../compatibility/skills-matrix.md)。
