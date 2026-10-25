# rule · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="rule-persist-001"></a>

## RULE-PERSIST-001 — 可从真实实体重建的 Registry/Cache 通常不独立持久化。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

可从真实实体重建的 Registry/Cache 通常不独立持久化。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

可从真实实体重建的 Registry/Cache 通常不独立持久化。

### Why

保存两份关联需修复 GUID 与初始化顺序。

### Applies When

派生实体注册表、候选缓存。

### Does Not Mean

不能把用户选择/进度一律归类成缓存丢弃。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7；15–16

### Counterexample

适用边界示例（未作为独立项目证据）：跨重启必须保留的排程/租约需单独设计保存。

### Failure If Violated

读档遗留失效引用或丢失不可重建意图。

### Detection Questions

- 这是重算能等价恢复，还是只重置默认？

### Related Patterns

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Related Anti Patterns

- [ANTI-LIFE-001](../anti-patterns/case001.md#anti-life-001)

### Origin Round6 Rule

9

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- persistence
  - lifecycle
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-LIFE-001](../anti-patterns/case001.md#anti-life-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7；15–16

### related

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [ANTI-LIFE-001](../anti-patterns/case001.md#anti-life-001)
