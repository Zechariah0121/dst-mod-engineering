# rule · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="rule-life-001"></a>

## RULE-LIFE-001 — Task、Listener、临时状态和 Hook 都要有可追踪的生命周期 Owner。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

Task、Listener、临时状态和 Hook 都要有可追踪的生命周期 Owner。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

Task、Listener、临时状态和 Hook 都要有可追踪的生命周期 Owner。

### Why

短命对象注销不自动清理挂在长命实体上的资源。

### Applies When

绑定玩家、UI、世界服务。

### Does Not Mean

不是实体正常 Remove 后仍需重复手动清所有引擎资源。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 16–17

### Counterexample

适用边界示例（未作为独立项目证据）：任务本来就属于整世界时可持续运行。

### Failure If Violated

旧闭包、旧监听或临时字段继续影响会话。

### Detection Questions

- 注销谁时应取消哪一个句柄？

### Related Patterns

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

### Related Anti Patterns

- [ANTI-LIFE-001](../anti-patterns/case001.md#anti-life-001)

### Origin Round6 Rule

13

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- lifecycle
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-LIFE-001](../anti-patterns/case001.md#anti-life-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 16–17

### related

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [ANTI-LIFE-001](../anti-patterns/case001.md#anti-life-001)
