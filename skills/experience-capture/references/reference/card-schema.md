# Experience Card Schema

## 最小字段（必填）
- `id`: 唯一 ID（例如 `EXP-20260306-0001`）
- `created_at`: UTC 时间戳
- `title`: 经验标题
- `problem_signature`: 问题签名（可复用场景描述）
- `decision_rules`: 决策规则列表
- `review_checklist`: 复用检查清单
- `source_event_refs`: 来源事件引用（至少 1 个）
- `doc_refs`: 相关文档引用（可选但推荐）
- `tags`: 标签

## 扩展字段（可选）
- `context_constraints`: 适用约束
- `anti_patterns`: 常见误区
- `outcome`: 效果摘要
- `confidence`: `low|medium|high`
- `owner`: 记录者
- `updated_at`: 更新时间
- `capture_meta`: 触发与确认审计元数据

## 系统派生字段（可选）
- `problem_signature_norm`: `problem_signature` 的标准化文本（用于检索/去重）

## capture_meta 建议结构
- `trigger_mode`: `manual-explicit` | `suggest-once`
- `confirmed_by_user`: `true|false`
- `confirmed_at`: UTC 时间戳
- `confirmation_note`: 确认说明

## JSON 示例
```json
{
  "id": "EXP-20260306-0001",
  "created_at": "2026-03-06T12:20:00Z",
  "title": "避免把编排决策退化为布尔开关",
  "problem_signature": "多 agent 编排中出现 run_xxx/use_xxx 布尔字段膨胀",
  "decision_rules": [
    "将编排决策表达为 plan.actions，而非全局布尔路由",
    "fallback 作为运行时重编排行为，不作为预定义模式名"
  ],
  "review_checklist": [
    "模式名与实际行为是否一致",
    "是否存在跨 agent 布尔耦合",
    "是否可由单一全局变量等价替代"
  ],
  "source_event_refs": [
    "MEM-EVT-20260306-0012"
  ],
  "doc_refs": [
    "docs/knowledge/experience-skill-alignment-record.md"
  ],
  "tags": ["orchestrator", "design", "anti-hardcode"],
  "context_constraints": [
    "适用于多 agent 编排系统"
  ],
  "anti_patterns": [
    "将策略枚举直接映射为执行布尔变量"
  ],
  "outcome": "降低配置语义与运行行为脱节风险",
  "confidence": "high",
  "owner": "codex"
}
```

## 质量约束
- `decision_rules` 至少 2 条。
- `review_checklist` 至少 3 条。
- `source_event_refs` 至少 1 条。
- `source_event_refs` 建议使用 `MEM-EVT-*` 或 `相对路径#锚点`。
- 对复杂多轮任务，优先引用 `docs/experience/sources/*.md#anchor` 中的 source retrospective note。
- `doc_refs` 应使用 repo-relative 路径（避免绝对路径）。
- 禁止只写“过程流水”，必须包含可复用规则。
