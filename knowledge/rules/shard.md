# rule · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="rule-shard-001"></a>

## RULE-SHARD-001 — 跨 Shard 稀缺资源应先定义写入权威和冲突语义。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

跨 Shard 稀缺资源应先定义写入权威和冲突语义。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

跨 Shard 稀缺资源应先定义写入权威和冲突语义。

### Why

基于同一旧值的完整 Set 会覆盖并行修改。

### Applies When

共享库存、积分等需要守恒。

### Does Not Mean

不等于任何广播完整值都错误。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 6–7

### Counterexample

适用边界示例（未作为独立项目证据）：唯一写者广播可覆盖的显示配置通常合理。

### Failure If Violated

丢更新、余额分歧、合计超提。

### Detection Questions

- 操作是 delta 还是最终值？谁能拒绝旧写？

### Related Patterns

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### Related Anti Patterns

- [ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)

### Origin Round6 Rule

7

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- shard
  - networking
  - state
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server
  - client
  - shard

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 6–7

### related

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)
- [ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)
