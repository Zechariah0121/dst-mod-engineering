# rule · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="rule-framework-001"></a>

## RULE-FRAMEWORK-001 — 共享 API 应有可追溯的有限出口和初始化条件。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

共享 API 应有可追溯的有限出口和初始化条件。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

共享 API 应有可追溯的有限出口和初始化条件。

### Why

整个可写环境作为 API 会隐藏依赖与覆盖。

### Applies When

模块增多或多人维护。

### Does Not Mean

不是禁止共享工具表或要求引入依赖注入容器。

### Evidence

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 2–5；14–15

### Counterexample

适用边界示例（未作为独立项目证据）：少量稳定、只读式公共工具可简单共享。

### Failure If Violated

顺序依赖、同名覆盖、接口面无控制增长。

### Detection Questions

- 符号在哪里定义，何时可用，谁能写？

### Related Patterns

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Related Anti Patterns

- [ANTI-FRAMEWORK-001](../anti-patterns/case001.md#anti-framework-001)

### Origin Round6 Rule

未记录 / null

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

1. **type**：mitigates
   - **target**：[ANTI-FRAMEWORK-001](../anti-patterns/case001.md#anti-framework-001)

### sources

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 2–5；14–15

### related

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
- [ANTI-FRAMEWORK-001](../anti-patterns/case001.md#anti-framework-001)
