# rule · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="rule-world-001"></a>

## RULE-WORLD-001 — 真实物品留给 Container/Item；Manager 可持有成员和候选。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

真实物品留给 Container/Item；Manager 可持有成员和候选。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

真实物品留给 Container/Item；Manager 可持有成员和候选。

### Why

重复库存账本增加一致性责任。

### Applies When

世界级实体查询和协调。

### Does Not Mean

不是禁止经测量后维护数量索引。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 10.2–10.4

### Counterexample

适用边界示例（未作为独立项目证据）：大量高频聚合可用有明确失效协议的索引。

### Failure If Violated

Manager 数字与实际实体分离。

### Detection Questions

- 查询读的是当前 Stack 还是另存的数量？

### Related Patterns

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Related Anti Patterns

- [ANTI-WORLD-001](../anti-patterns/case001.md#anti-world-001)

### Origin Round6 Rule

8

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

1. **type**：mitigates
   - **target**：[ANTI-WORLD-001](../anti-patterns/case001.md#anti-world-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 10.2–10.4

### related

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [ANTI-WORLD-001](../anti-patterns/case001.md#anti-world-001)

<a id="rule-world-002"></a>

## RULE-WORLD-002 — 注册与失效管理先正确，再按测量选择 Active Set/索引。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

注册与失效管理先正确，再按测量选择 Active Set/索引。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

注册与失效管理先正确，再按测量选择 Active Set/索引。

### Why

一个 Manager 仍可能每秒遍历全部对象。

### Applies When

多个实体参与周期工作。

### Does Not Mean

不是一定需要任务队列或把所有查询变 O(1)。

### Evidence

- [REPORT-R4](<../review-support/reports/sorachestmanager_DeepDive_20260928.txt>) · interpretation · 6；8；13；15

### Counterexample

适用边界示例（未作为独立项目证据）：小规模稀疏工作保持简单遍历更易维护。

### Failure If Violated

优化了任务数量，却仍有高扫描成本或漏注册。

### Detection Questions

- 空闲时扫描什么？注销是否使缓存失效？

### Related Patterns

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Related Anti Patterns

- [ANTI-WORLD-001](../anti-patterns/case001.md#anti-world-001)

### Origin Round6 Rule

未记录 / null

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

1. **type**：mitigates
   - **target**：[ANTI-WORLD-001](../anti-patterns/case001.md#anti-world-001)

### sources

- [REPORT-R4](<../review-support/reports/sorachestmanager_DeepDive_20260928.txt>) · interpretation · 6；8；13；15

### related

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [ANTI-WORLD-001](../anti-patterns/case001.md#anti-world-001)
