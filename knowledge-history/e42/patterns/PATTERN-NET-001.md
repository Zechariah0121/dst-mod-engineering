# pattern · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="pattern-net-001"></a>

## PATTERN-NET-001 — Player Business Channel

类型：Engineering Pattern Candidate · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

用玩家绑定的业务通道集中路由意图；服务端生成 View，客户端保存可重建 Cache。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Player Business Channel

### Category

network

### Problem

多个玩家 UI 各自重复定义 RPC、身份路由和缓存更新，容易混淆请求与权威结果。

### Context

多个相关业务需要玩家级命令和定向视图；原版 Action/Replica 不能完整承载额外视图。

### Forces

- Host 快路径与远程验证一致
- 请求意图与状态同步不同
- 每玩家隔离与广播成本
- 断线时资源释放

### Core Idea

用玩家绑定的业务通道集中路由意图；服务端生成 View，客户端保存可重建 Cache。

### Structure

Widget → Client Service → Transport → Identity/Business Adapter → State Owner；Owner notification → View → Cache → Widget

### State Ownership

Owner 保存真实业务状态；View 可是函数映射；Client Cache 和展示均为派生。

### Authority

引擎玩家身份进入 Handler；业务仍校验参数、权限和当前状态。

### Lifecycle

认证/连接创建绑定，玩家生成关联，退出解除监听并取消属于绑定的任务。

### Networking

可用统一 RPC 分发业务命令；netvar/原版 Action 不应因引入通道而全部替换。

### Persistence

保存业务 Owner；视图与客户端缓存通常由登录同步重建。

### Performance

按业务/玩家裁剪更新；完整快照与键级更新需分别计算成本。

### Benefits

- 身份与路由复用
- 同一视图供多个界面使用

### Costs

- 通道成为额外协议
- 初始化和生命周期责任增加

### Failure Modes

- Host 验证旁路
- 缓存误当权威
- 无 ACK 却按已完成反馈
- 长命任务泄漏

### Use When

多个 UI/业务确有玩家视图与统一路由需求。

### Avoid When

一个已有原版 Action 已完整解决的按钮；纯本地视觉。

### Implementation Notes

命令与通知分开命名；业务 Handler 返回可解释结果；只在需要时加入请求关联与超时。

### Dst Klei Basis

- [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)
- [FACT-DST-009](../facts/klei-lua.md#fact-dst-009)

### Case Evidence

REPORT-R6 §3–6：ClientDB 的 seed 模板、BindRootFn、GetSeeds/CollectAllSeeds；Host 直调与 Remote 路由并存。

### Counter Evidence

同一案例的全局制作只用统一业务通道传开关，真正制作走原版 RPC；不是所有交互都需要通道。

### Related Rules

- [RULE-NET-001](../rules/net.md#rule-net-001)
- [RULE-NET-002](../rules/net.md#rule-net-002)
- [RULE-STATE-002](../rules/state.md#rule-state-002)

### Related Anti Patterns

- [ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)
- [ANTI-LIFE-001](../anti-patterns/case001.md#anti-life-001)

### Related Decision Trees

- [DECISION-NET-001](../decisions/candidates.md#decision-net-001)

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

1. **type**：derived_from
   - **target**：[CASE-001](../cases/CASE-001-sora/README.md#case-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 3–6；8–9

### related

- [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)
- [FACT-DST-009](../facts/klei-lua.md#fact-dst-009)
- [RULE-NET-001](../rules/net.md#rule-net-001)
- [RULE-NET-002](../rules/net.md#rule-net-002)
- [RULE-STATE-002](../rules/state.md#rule-state-002)
- [ANTI-NET-001](../anti-patterns/case001.md#anti-net-001)
- [ANTI-LIFE-001](../anti-patterns/case001.md#anti-life-001)
- [DECISION-NET-001](../decisions/candidates.md#decision-net-001)
- [TEST-NET-001](../tests/candidates.md#test-net-001)
- [TEST-NET-002](../tests/candidates.md#test-net-002)
- [TEST-LIFE-001](../tests/candidates.md#test-life-001)
- [TEST-NET-003](../tests/candidates.md#test-net-003)
