# pattern · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="pattern-world-001"></a>

## PATTERN-WORLD-001 — World Manager

类型：Engineering Pattern Candidate · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

集中维护成员关系与跨实体协调，保留实体自身的真实状态和生命周期。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

World Manager

### Category

world

### Problem

多个实体需要共享查询、预算或调度，逐实体扫描造成重复工作和分散生命周期。

### Context

协作范围是一个 World，实体仍有各自 Component 状态。

### Forces

- 注册与实体存在期一致
- 查询实时性与索引成本
- 局部行为与集中调度边界

### Core Idea

集中维护成员关系与跨实体协调，保留实体自身的真实状态和生命周期。

### Structure

Prefab/Component → Registry；Consumer → Query → registered entities；Events/Tasks → Coordination

### State Ownership

Registry/派生索引归 Manager；真实物品、生命、单体计时等仍归相应实体组件。

### Authority

需要权威 gameplay 的 Manager 放服务器世界；客户端只复制必要结果。

### Lifecycle

World 创建 → 类型/实例注册 → 事件/调度 → 注销；重复注册和独立卸载需明确。

### Networking

不必有 Replica；只在客户端确需 Manager 状态时定义最小视图。

### Persistence

实体真实数据保存；能从重建实体恢复的 Registry 通常不独立保存。

### Performance

候选缓存不等于数量索引；活跃集合/分批处理须以实际工作量选择。

### Benefits

- 减少重复发现
- 集中查询契约
- 跨实体工作可统一计量

### Costs

- 注册和失效管理
- 集中层可能增长过度

### Failure Modes

- 失效引用
- 重复注册
- 遗漏 cleanup
- Query 与资源占用混为一谈

### Use When

确有跨实体配额、查询或协同调度。

### Avoid When

单体自足行为；为整齐把所有实体逻辑移进一个巨型对象。

### Implementation Notes

优先显式注册、有效性检查和可观测计数；有性能证据再升级索引/任务队列。

### Dst Klei Basis

- [FACT-DST-002](../facts/klei-lua.md#fact-dst-002)
- [FACT-DST-008](../facts/klei-lua.md#fact-dst-008)
- [FACT-DST-010](../facts/klei-lua.md#fact-dst-010)

### Case Evidence

REPORT-R4 §3–8、12–15；REPORT-R6 §10–11：sorachestmanager 的 RegType/RegByType、候选缓存、HasItem/GetIngredients。

### Counter Evidence

案例仍有注册表全遍历和空间检测；未测 10/100/1000 箱性能；不能称为恒定时间或证明 God Object 已发生。

### Related Rules

- [RULE-WORLD-001](../rules/world.md#rule-world-001)
- [RULE-WORLD-002](../rules/world.md#rule-world-002)
- [RULE-PERSIST-001](../rules/persist.md#rule-persist-001)
- [RULE-RESOURCE-001](../rules/resource.md#rule-resource-001)

### Related Anti Patterns

- [ANTI-RESOURCE-001](../anti-patterns/case001.md#anti-resource-001)
- [ANTI-WORLD-001](../anti-patterns/case001.md#anti-world-001)

### Related Decision Trees

- [DECISION-STATE-OWNER-001](../decisions/candidates.md#decision-state-owner-001)

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- world
  - lifecycle
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server

### Typed Relations

1. **type**：derived_from
   - **target**：[CASE-001](../cases/CASE-001-sora/README.md#case-001)

### sources

- [REPORT-R4](<../review-support/reports/sorachestmanager_DeepDive_20260928.txt>) · interpretation · 3–8；12–15
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 10–11

### related

- [FACT-DST-002](../facts/klei-lua.md#fact-dst-002)
- [FACT-DST-008](../facts/klei-lua.md#fact-dst-008)
- [FACT-DST-010](../facts/klei-lua.md#fact-dst-010)
- [RULE-WORLD-001](../rules/world.md#rule-world-001)
- [RULE-WORLD-002](../rules/world.md#rule-world-002)
- [RULE-PERSIST-001](../rules/persist.md#rule-persist-001)
- [RULE-RESOURCE-001](../rules/resource.md#rule-resource-001)
- [ANTI-RESOURCE-001](../anti-patterns/case001.md#anti-resource-001)
- [ANTI-WORLD-001](../anti-patterns/case001.md#anti-world-001)
- [DECISION-STATE-OWNER-001](../decisions/candidates.md#decision-state-owner-001)
- [TEST-LIFE-001](../tests/candidates.md#test-life-001)
- [TEST-LIFE-002](../tests/candidates.md#test-life-002)
- [TEST-LIFE-003](../tests/candidates.md#test-life-003)
- [TEST-RESOURCE-001](../tests/candidates.md#test-resource-001)
