# Trigger-Boundary Regression Cases

## Should Trigger
1. User asks whether AI PRD discussion needs algorithm and architecture roles.
2. Architecture trade-off is repeatedly disputed and no consensus is reached.
3. Existing solution path failed multiple times and user asks for role-based reframing.
4. User asks: "评估下当前项目的产品功能，技术架构设计方案" and expects multi-role discussion recommendations.
5. User asks: "开多个agent评审这个项目，然后给一个统一结论".

## Should Not Trigger
1. User asks to split implementation tasks and schedule milestones.
2. User asks to implement a feature directly in code.
3. User asks to debug a deterministic local test failure.

## Boundary Assertions
- If request includes execution decomposition verbs ("拆任务", "排期", "执行步骤"), do not stay in this skill.
- If request is purely discussion strategy ("需要哪些角色讨论"), this skill should trigger with high priority.
- If user explicitly asks real multi-agent review, the response must include delegated sub-agent results, not role-play-only text.
