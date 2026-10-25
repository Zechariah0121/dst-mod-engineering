# pattern · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="pattern-framework-001"></a>

## PATTERN-FRAMEWORK-001 — Mod Framework / Integration Layer

类型：Engineering Pattern Candidate · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

用显式启动阶段、有限服务出口和可追踪适配器连接业务与原版。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Mod Framework / Integration Layer

### Category

framework

### Problem

大型 Mod 多模块需要接入原版生命周期与共享能力，隐式顺序和补丁叠加容易失控。

### Context

模块数量和接入点已经使显式组织有收益；不意味着要另建通用框架产品。

### Forces

- 加载期与运行期分离
- 接口可追溯
- 最窄 Hook 作用域
- 多 Mod 共存

### Core Idea

用显式启动阶段、有限服务出口和可追踪适配器连接业务与原版。

### Structure

Bootstrap → Services → Registration；Vanilla Lifecycle → Adapter → Business → State Owner

### State Ownership

业务状态归业务 Owner；框架只拥有注册信息、适配上下文和自身生命周期。

### Authority

框架不能代替业务做资源/身份决策；Hook 作用域需明确实例或共享类。

### Lifecycle

区分注册与执行；设计重入、重复初始化、卸载和错误恢复。

### Networking

复用原版 Action/Replica/传输；仅对真实缺口建立适配。

### Persistence

不自动保存环境表或函数；持久化由业务数据 schema 决定。

### Performance

检查全实体 PostInit 成本、每实例闭包、共享 hook 链和频繁运行的包装。

### Benefits

- 接入位置集中
- 依赖可定位
- 复用原版行为

### Costs

- 包装链复杂
- 环境隐式依赖
- 版本敏感私有接口

### Failure Modes

- 临时补丁未恢复
- 覆盖别人的 Hook
- 共享命名冲突
- 过期私有 upvalue

### Use When

多模块、多原版接入点，需要清晰启动和兼容边界。

### Avoid When

少量自足 Prefab；无需引入共享可写环境才能完成的普通模块。

### Implementation Notes

显式模块导出优先；共享服务应有限且可查；私有 Patch 需能力检测和失败降级。

### Dst Klei Basis

- [FACT-DST-007](../facts/klei-lua.md#fact-dst-007)
- [FACT-DST-008](../facts/klei-lua.md#fact-dst-008)

### Case Evidence

REPORT-R5 §1–14、20–24：SoraEnv/SoraAPI/多种 Hook；REPORT-R6 §13–14 展示两业务组合。

### Counter Evidence

案例不是统一注册/卸载框架；局部 Hook helper 的能力不能推成全项目通用保证。

### Related Rules

- [RULE-HOOK-001](../rules/hook.md#rule-hook-001)
- [RULE-HOOK-002](../rules/hook.md#rule-hook-002)
- [RULE-HOOK-003](../rules/hook.md#rule-hook-003)
- [RULE-FRAMEWORK-001](../rules/framework.md#rule-framework-001)

### Related Anti Patterns

- [ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)
- [ANTI-HOOK-002](../anti-patterns/case001.md#anti-hook-002)
- [ANTI-FRAMEWORK-001](../anti-patterns/case001.md#anti-framework-001)

### Related Decision Trees

- [DECISION-HOOK-001](../decisions/candidates.md#decision-hook-001)

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- framework
  - hooks
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：derived_from
   - **target**：[CASE-001](../cases/CASE-001-sora/README.md#case-001)

### sources

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 1–14；20–24
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 13–14

### related

- [FACT-DST-007](../facts/klei-lua.md#fact-dst-007)
- [FACT-DST-008](../facts/klei-lua.md#fact-dst-008)
- [RULE-HOOK-001](../rules/hook.md#rule-hook-001)
- [RULE-HOOK-002](../rules/hook.md#rule-hook-002)
- [RULE-HOOK-003](../rules/hook.md#rule-hook-003)
- [RULE-FRAMEWORK-001](../rules/framework.md#rule-framework-001)
- [ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)
- [ANTI-HOOK-002](../anti-patterns/case001.md#anti-hook-002)
- [ANTI-FRAMEWORK-001](../anti-patterns/case001.md#anti-framework-001)
- [DECISION-HOOK-001](../decisions/candidates.md#decision-hook-001)
- [TEST-NET-002](../tests/candidates.md#test-net-002)
- [TEST-HOOK-001](../tests/candidates.md#test-hook-001)
- [TEST-HOOK-002](../tests/candidates.md#test-hook-002)
