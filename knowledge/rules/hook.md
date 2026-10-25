# rule · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="rule-hook-001"></a>

## RULE-HOOK-001 — 先确认原版消费、保存和卸载契约，再扩展接口。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

先确认原版消费、保存和卸载契约，再扩展接口。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

先确认原版消费、保存和卸载契约，再扩展接口。

### Why

名称与示意图不能代表真实顺序。

### Applies When

接入已有 API。

### Does Not Mean

不是永远禁止自定义实现。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 9–11；16

### Counterexample

适用边界示例（未作为独立项目证据）：原版确实缺少机制时应写明缺口。

### Failure If Violated

依赖错序、访问已清空组件、材料计划不兼容。

### Detection Questions

- 被调用方如何处理参数/所有权/返回值？

### Related Patterns

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Related Anti Patterns

- [ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)

### Origin Round6 Rule

14

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- hooks
  - compatibility
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 9–11；16

### related

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
- [ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)

<a id="rule-hook-002"></a>

## RULE-HOOK-002 — 临时替换必须在异常退出时恢复，并避免覆盖后来的拥有者。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

临时替换必须在异常退出时恢复，并避免覆盖后来的拥有者。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

临时替换必须在异常退出时恢复，并避免覆盖后来的拥有者。

### Why

old(...) 抛错会跳过普通赋值恢复。

### Applies When

绕现有调用临时改方法/上下文。

### Does Not Mean

不是每个一次性启动赋值都要可热卸载。

### Evidence

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 12–13

### Counterexample

适用边界示例（未作为独立项目证据）：会话级固定替换可显式声明不可卸载，并仍审查异常。

### Failure If Violated

替换残留、其他 Mod 包装被抹掉。

### Detection Questions

- 恢复时目标仍等于自己装的 wrapper 吗？

### Related Patterns

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Related Anti Patterns

- [ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)

### Origin Round6 Rule

未记录 / null

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- hooks
  - compatibility
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)

### sources

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 12–13

### related

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
- [ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)

<a id="rule-hook-003"></a>

## RULE-HOOK-003 — 选择最小足够作用域的接入点，并保存原契约。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

选择最小足够作用域的接入点，并保存原契约。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

选择最小足够作用域的接入点，并保存原契约。

### Why

类、实例、闭包共享状态的影响范围不同。

### Applies When

PostInit、实例包装、类改写或私有 patch。

### Does Not Mean

不是私有 upvalue 一律禁止。

### Evidence

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 7–9；12–13

### Counterexample

适用边界示例（未作为独立项目证据）：没有公开接入点且能版本检测、失败降级时可审慎采用。

### Failure If Violated

污染所有实例或丢失原始清理/返回值。

### Detection Questions

- 该改动影响旧实例还是新实例？能否回退？

### Related Patterns

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Related Anti Patterns

- [ANTI-HOOK-002](../anti-patterns/case001.md#anti-hook-002)

### Origin Round6 Rule

未记录 / null

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- hooks
  - compatibility
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-HOOK-002](../anti-patterns/case001.md#anti-hook-002)

### sources

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 7–9；12–13

### related

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
- [ANTI-HOOK-002](../anti-patterns/case001.md#anti-hook-002)
