# correction · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="correction-case001-001"></a>

## CORRECTION-CASE001-001 — 撤回未使用 SeedCDB 顶层 local 的初始化故障判断

类型：Case Observation · Evidence：E1 · Confidence：Very High · Status：corrected · Version：0.1.1

旧变量确实在顶层捕获，但未被使用；不能据此建立 UI 的运行时初始化依赖。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Previous Claim

soraseed.lua 顶层捕获 SeedCDB，因此 clientfn 必须在首次 require 前创建它，否则导致 UI 初始化 nil 问题。

### Target Claims

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · historical · §1.3：clientfn→soraseed 首次 require；§3：soraseed 隐式依赖行

### Subsequent Evidence

REPORT-R6：local DB 全文未被使用；实际数量读取经过 soraseedcontainer:GetDB 动态选择后端。

### Result

撤回“该 local 导致初始化故障”以及“该 local 必须有值”的硬依赖结论。

### Replacement

分析符号的真实使用点，而非仅发现一次赋值；其他实际依赖仍分别验证。

### Superseded Claim Status

superseded

### Correction Scope

只替换该因果判断，不否认赋值存在，也不宣布种子全部初始化路径无风险。

### History Policy

保留原报告，不改写历史；检索旧报告该结论时必须附本 Correction。

### Target Claim Ids

- [CLAIM-CASE001-001](claims.md#claim-case001-001)

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- architecture
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：corrects
   - **target**：[CLAIM-CASE001-001](claims.md#claim-case001-001)

2. **type**：supersedes
   - **target**：[CLAIM-CASE001-001](claims.md#claim-case001-001)

### sources

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · historical · 1.3；3
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 0；5.1

### related

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
- [RULE-FRAMEWORK-001](../rules/framework.md#rule-framework-001)
