# rule · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="rule-state-001"></a>

## RULE-STATE-001 — 每个状态写清“相对于谁权威”。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

每个状态写清“相对于谁权威”。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

每个状态写清“相对于谁权威”。

### Why

客户端权威边界不等于 Shard 间一致性。

### Applies When

多端或多分片状态。

### Does Not Mean

不是所有数据都需要主世界集中持有。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 3；7

### Counterexample

适用边界示例（未作为独立项目证据）：互不共享的每世界天气配置可各自权威。

### Failure If Violated

把多个可写副本误当唯一账本。

### Detection Questions

- 谁能写？离线副本还能写吗？

### Related Patterns

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### Related Anti Patterns

- [ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)

### Origin Round6 Rule

2

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- state
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 3；7

### related

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)
- [ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)

<a id="rule-state-002"></a>

## RULE-STATE-002 — 分别记录 Owner、Server View、Client Cache 和 Display。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

分别记录 Owner、Server View、Client Cache 和 Display。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

分别记录 Owner、Server View、Client Cache 和 Display。

### Why

相同键名不代表相同存储职责。

### Applies When

有映射/缓存/界面的业务。

### Does Not Mean

不是强迫每层各建一个类或复制一份数据。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 3；5

### Counterexample

适用边界示例（未作为独立项目证据）：小业务可直接读取已有 Replica。

### Failure If Violated

UI 或副本被当作保存真相。

### Detection Questions

- View 是函数还是一份副本？

### Related Patterns

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

### Related Anti Patterns

- [ANTI-FRAMEWORK-001](../anti-patterns/case001.md#anti-framework-001)

### Origin Round6 Rule

3

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- state
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-FRAMEWORK-001](../anti-patterns/case001.md#anti-framework-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 3；5

### related

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [ANTI-FRAMEWORK-001](../anti-patterns/case001.md#anti-framework-001)

<a id="rule-state-003"></a>

## RULE-STATE-003 — 缓存可重建只说明恢复来源，不说明来源正确。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

缓存可重建只说明恢复来源，不说明来源正确。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

缓存可重建只说明恢复来源，不说明来源正确。

### Why

同步陈旧服务器仍会得到陈旧值。

### Applies When

缓存依赖分布式/异步 Owner。

### Does Not Mean

不是要求所有缓存强一致。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7.3；17

### Counterexample

适用边界示例（未作为独立项目证据）：非关键统计允许明确的延迟误差。

### Failure If Violated

客户端看似刷新却掩盖服务器分歧。

### Detection Questions

- 恢复时向谁取值？该源如何保证正确？

### Related Patterns

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### Related Anti Patterns

- [ANTI-SHARD-001](../anti-patterns/case001.md#anti-shard-001)

### Origin Round6 Rule

4

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- state
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-SHARD-001](../anti-patterns/case001.md#anti-shard-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7.3；17

### related

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)
- [ANTI-SHARD-001](../anti-patterns/case001.md#anti-shard-001)

<a id="rule-state-004"></a>

## RULE-STATE-004 — 实体与账本互换必须定义提交及失败补偿边界。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

实体与账本互换必须定义提交及失败补偿边界。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

实体与账本互换必须定义提交及失败补偿边界。

### Why

Remove/Spawn 与数字修改并非一个原子操作。

### Applies When

物理物品转为计数、积分或共享资源。

### Does Not Mean

不要求所有普通容器操作实现分布式事务。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 4.4；5.2；7.3

### Counterexample

适用边界示例（未作为独立项目证据）：无价值、可丢弃视觉实体无需账本守恒。

### Failure If Violated

物品已删未记账或已生成未可靠扣款。

### Detection Questions

- 第几步失败时，实体和余额如何保持不变量？

### Related Patterns

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### Related Anti Patterns

- [ANTI-SHARD-001](../anti-patterns/case001.md#anti-shard-001)

### Origin Round6 Rule

6

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- state
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-SHARD-001](../anti-patterns/case001.md#anti-shard-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 4.4；5.2；7.3

### related

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)
- [ANTI-SHARD-001](../anti-patterns/case001.md#anti-shard-001)
