# rule · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="rule-net-001"></a>

## RULE-NET-001 — Client 提交 Intent，服务端决定权威数量/材料。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

Client 提交 Intent，服务端决定权威数量/材料。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

Client 提交 Intent，服务端决定权威数量/材料。

### Why

伪造最终余额会跳过合法性检查。

### Applies When

客户端请求影响 gameplay。

### Does Not Mean

不要求所有操作自建 RPC；可复用原版 Action/Builder/Replica。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 4–5；9

### Counterexample

适用边界示例（未作为独立项目证据）：纯本地光效可由客户端决定。

### Failure If Violated

客户端越权设置结果。

### Detection Questions

- 谁根据当前真实状态计算结果？

### Related Patterns

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

### Related Anti Patterns

- [ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)

### Origin Round6 Rule

1

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- networking
  - UI
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server
  - client

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 4–5；9

### related

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)

<a id="rule-net-002"></a>

## RULE-NET-002 — Host 快路径应保留与 Remote 相同的业务验证。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

Host 快路径应保留与 Remote 相同的业务验证。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

Host 快路径应保留与 Remote 相同的业务验证。

### Why

优化 transport 容易一起绕过 Adapter。

### Applies When

本地直调与远程 Handler 并存。

### Does Not Mean

不是禁止 Host 直调或要求回环网络包。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 4.3；8.1；9

### Counterexample

适用边界示例（未作为独立项目证据）：纯本地 UI 不涉及服务端权限。

### Failure If Violated

Host 正常而 Remote 拒绝，或权限条件不同。

### Detection Questions

- 两条路径在哪里汇合验证？

### Related Patterns

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

### Related Anti Patterns

- [ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)

### Origin Round6 Rule

5

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- networking
  - UI
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server
  - client

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 4.3；8.1；9

### related

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)

<a id="rule-net-003"></a>

## RULE-NET-003 — 乐观 UI 应与服务端最终可用性区分。

类型：Engineering Rule Candidate · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

乐观 UI 应与服务端最终可用性区分。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Statement

乐观 UI 应与服务端最终可用性区分。

### Why

显示可尝试不代表客户端知道所有材料。

### Applies When

客户端没有完整权威库存。

### Does Not Mean

不要求复制全世界库存才能显示按钮。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 8.3；9

### Counterexample

适用边界示例（未作为独立项目证据）：局部完整 Replica 足以给精确提示时不必乐观。

### Failure If Violated

把界面可点误当成业务已成功。

### Detection Questions

- 失败由谁反馈？何时重查？

### Related Patterns

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

### Related Anti Patterns

- [ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)

### Origin Round6 Rule

12

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- networking
  - UI
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server
  - client

### Typed Relations

1. **type**：mitigates
   - **target**：[ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 8.3；9

### related

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)
