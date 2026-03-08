# Trigger Signals

## 1. Activation Signals
Trigger when at least one signal is true:
- Requirement ambiguity is high and needs multi-perspective clarification.
- User asks for project-level product-function and technical-architecture assessment with cross-role viewpoints.
- User explicitly asks for multi-role synthesis and final recommendation (for example: "评估下当前项目的产品功能，技术架构设计方案", "需要多角色综合分析确定方案").
- User explicitly asks to run real multi-agent discussion/review (for example: "开多个agent评审", "用多agent讨论后给结论").
- Technical feasibility is disputed across rounds.
- A major trade-off spans product, architecture, algorithm, or delivery concerns.
- Current solution path is blocked and needs reframing.
- User explicitly asks for collaboration strategy or role suggestions.

## 2. Non-activation Signals
Do not trigger when any signal is true:
- Request is direct execution planning, decomposition, or milestone tracking.
- Request is implementation or local debugging with direct evidence in code/logs/tests.
- Issue is a small one-off change with low uncertainty and no cross-role trade-off.

## 3. Priority Rule
1. User explicit ask for discussion strategy or multi-agent review -> trigger immediately (highest priority).
2. If uncertainty/conflict signals are high, trigger even without user-provided role list.
3. If request shifts into execution planning -> hand off to execution planning skill.
4. Keep this skill as advisory guidance only.

## 4. Anti-pattern Signals
- Forcing multi-role collaboration where single-role reasoning is sufficient.
- Recommending role sets without mapping each role to a concrete uncertainty.
- Treating examples as rigid routing rules.
