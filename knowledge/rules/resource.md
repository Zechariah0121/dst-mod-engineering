# rule · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="rule-resource-001"></a>

## RULE-RESOURCE-001 — 多个资源 Provider 必须按实体身份和剩余预算组合。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

多个资源 Provider 必须按实体身份和剩余预算组合。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

多个资源 Provider 必须按实体身份和剩余预算组合。

### Why

同一实体可以从多个来源被发现。

### Applies When

合并多个 Entity→amount 查询结果。

### Does Not Mean

不是简单把重复项改成相加就修好。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 11.3

### Counterexample

适用边界示例（未作为独立项目证据）：证明来源集合互斥时可直接组合。

### Failure If Violated

重复预算或覆盖已分配数量而少扣材料。

### Detection Questions

- Provider B 知道 A 已分配哪些实体多少吗？

### Related Patterns

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Related Anti Patterns

- [ANTI-RESOURCE-001](../anti-patterns/case001.md#anti-resource-001)

### Origin Round6 Rule

10

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- world
  - resources
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-RESOURCE-001](../anti-patterns/case001.md#anti-resource-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 11.3

### related

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [ANTI-RESOURCE-001](../anti-patterns/case001.md#anti-resource-001)

<a id="rule-resource-002"></a>

## RULE-RESOURCE-002 — Query/分配建议不等于 reservation 或扣款。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

Query/分配建议不等于 reservation 或扣款。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

Query/分配建议不等于 reservation 或扣款。

### Why

查询到执行之间可以有排队和同步回调。

### Applies When

延后执行、回调可变或共享资源。

### Does Not Mean

不是断言 Lua 每行会被其他任务抢占。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 10.3；11.4

### Counterexample

适用边界示例（未作为独立项目证据）：无回调、无让出且立即执行的小操作可保持简单。

### Failure If Violated

旧计划被当作承诺，扣款失败无补偿。

### Detection Questions

- 执行前还有哪些状态变化点？

### Related Patterns

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Related Anti Patterns

- [ANTI-RESOURCE-001](../anti-patterns/case001.md#anti-resource-001)

### Origin Round6 Rule

11

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- world
  - resources
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-RESOURCE-001](../anti-patterns/case001.md#anti-resource-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 10.3；11.4

### related

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [ANTI-RESOURCE-001](../anti-patterns/case001.md#anti-resource-001)
