# Examples

## Example 1: Latest capability question
- User request:
  - "这个库最新版本支持这个参数吗？给官方依据。"
- Why trigger:
  - Requires current external facts and official confirmation.
- Expected output:
  - `claim`, source-backed `verdict`, and decision impact.

## Example 2: Disputed technical point
- User request:
  - "你前后说法不一致，麻烦查一下官方文档到底怎么写。"
- Why trigger:
  - Multi-round conflict on one technical claim with weak evidence.
- Expected output:
  - Resolve or acknowledge conflict with explicit sources.

## Example 3: Policy/standard dependency
- User request:
  - "这个实现是否符合最新标准版本要求？"
- Why trigger:
  - Depends on external standards and freshness.
- Expected output:
  - Standard reference, version/date, and implementation impact.

## Example 4: AI model selection with version mismatch risk
- User request:
  - "用千问还是用 Kimi？"
- Why trigger:
  - Model capabilities iterate quickly; comparisons are invalid if versions and release windows are not aligned.
- Expected output:
  - Version-aligned comparison with model names, release dates, and source-backed conclusion.

## Example 5: MAS landing-status validation
- User request:
  - "multi-agent 现在落地现状如何？"
- Why trigger:
  - Ecosystem adoption changes fast; stale snapshots (for example, one year ago) can mislead architecture decisions.
- Expected output:
  - Recent source-backed landscape summary with explicit timeframe and confidence.

## Non-Example 1: Local failing test
- User request:
  - "这个单测为什么失败？"
- Why not trigger:
  - Should use local code/test debugging flow, not external verification first.

## Non-Example 2: Pure design brainstorm
- User request:
  - "给我几个架构方向，不用查资料。"
- Why not trigger:
  - No requirement for external authoritative verification.
