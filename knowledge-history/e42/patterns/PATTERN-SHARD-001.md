# pattern · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="pattern-shard-001"></a>

## PATTERN-SHARD-001 — Shard Service Bus

类型：Engineering Pattern Candidate · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

把 Shard transport、服务路由和业务协议聚合；将 authority、复制与恢复作为显式契约。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Shard Service Bus

### Category

shard

### Problem

多个世界要交流共享业务状态或请求，散落的 Shard RPC 缺少统一路由和恢复语义。

### Context

共享状态确实超出单世界；必须先决定其唯一/多写权威。

### Forces

- 离线与重连
- 完整值与操作命令
- 消息顺序
- 共享稀缺资源正确性

### Core Idea

把 Shard transport、服务路由和业务协议聚合；将 authority、复制与恢复作为显式契约。

### Structure

Local Business → Shard Service → Transport → Remote Service → Authority/Replica；Persistence 跟随 Owner

### State Ownership

区分真实权威、可写副本、只读缓存；不要仅凭 DB 名称决定。

### Authority

由业务明确指定；总线本身不自动产生唯一权威。

### Lifecycle

世界创建服务；连接完成恢复协商；断开处理未完成工作；世界退出释放任务/引用。

### Networking

Shard RPC 可承载命令、事件或快照；每种有各自版本、幂等和恢复需求。

### Persistence

明确每 Shard 保存什么，以及副本重载后向谁收敛。

### Performance

按变化同步与按需快照；大桶完整复制可能扩大流量和冲突域。

### Benefits

- 收敛通信入口
- 统一诊断和协议边界

### Costs

- 协议与恢复复杂度
- 需要跨 Shard 测试

### Failure Modes

- 覆盖更新
- 失联后旧副本继续写
- 没有恢复来源
- 实体转换与账本不同步

### Use When

业务真的需要跨世界共享/协调。

### Avoid When

当前世界注册表或本地容器查询；原版已满足的迁移数据。

### Implementation Notes

先列不变量，再选择单写命令或其他一致性方案；revision/epoch 不是无条件必加清单。

### Dst Klei Basis

- [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)
- [FACT-DST-001](../facts/klei-lua.md#fact-dst-001)

### Case Evidence

REPORT-R6 §6–7：SeedDB/MainDB 的 Set 完整值广播、世界持久化、noSyn=1 与任务条件缺陷。

### Counter Evidence

该案例证明总线存在，也证明它不自动保证库存一致性；Case B 全局制作不需要该层。

### Related Rules

- [RULE-SHARD-001](../rules/shard.md#rule-shard-001)
- [RULE-STATE-001](../rules/state.md#rule-state-001)
- [RULE-STATE-004](../rules/state.md#rule-state-004)

### Related Anti Patterns

- [ANTI-SHARD-001](../anti-patterns/case001.md#anti-shard-001)
- [ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)

### Related Decision Trees

- [DECISION-SHARD-001](../decisions/candidates.md#decision-shard-001)

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

1. **type**：derived_from
   - **target**：[CASE-001](../cases/CASE-001-sora/README.md#case-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 6–7

### related

- [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)
- [FACT-DST-001](../facts/klei-lua.md#fact-dst-001)
- [RULE-SHARD-001](../rules/shard.md#rule-shard-001)
- [RULE-STATE-001](../rules/state.md#rule-state-001)
- [RULE-STATE-004](../rules/state.md#rule-state-004)
- [ANTI-SHARD-001](../anti-patterns/case001.md#anti-shard-001)
- [ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)
- [DECISION-SHARD-001](../decisions/candidates.md#decision-shard-001)
- [TEST-SHARD-001](../tests/candidates.md#test-shard-001)
- [TEST-LIFE-002](../tests/candidates.md#test-life-002)
- [TEST-SHARD-002](../tests/candidates.md#test-shard-002)
