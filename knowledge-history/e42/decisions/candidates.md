# decision · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="decision-state-owner-001"></a>

## DECISION-STATE-OWNER-001 — Prefab / Component / World Manager 如何选择？

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

按状态范围和协作需求分配，不按代码行数分层。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Question

Prefab / Component / World Manager 如何选择？

### Branches

1. **condition**：只是实体创建、资源和初始组件组装
   - **recommended_direction**：Prefab 构造承担；避免把长期协调逻辑塞进构造。
   - **evidence**：- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
     - [FACT-DST-007](../facts/klei-lua.md#fact-dst-007)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

2. **condition**：状态随单个实体生灭，行为基本自足
   - **recommended_direction**：实体 Component 持有状态和 API。
   - **evidence**：- [RULE-WORLD-001](../rules/world.md#rule-world-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

3. **condition**：多个实体共享成员查询、配额或调度
   - **recommended_direction**：World Manager 持有 Registry/协调；实体保留单体真相。
   - **evidence**：- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

4. **condition**：状态跨 World
   - **recommended_direction**：转交 Shard 决策树，不把单 World Manager 当跨世界服务。
   - **evidence**：- [DECISION-SHARD-001](candidates.md#decision-shard-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

### Recommended Direction

按状态范围和协作需求分配，不按代码行数分层。

### Exceptions

小业务可在 Prefab 上保持少量状态；没有强迫新增 Component。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 2；10；15

### Unknowns

尚未由独立技能/Boss/Buff 项目验证；World Manager 是否值得增加需看规模。

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

无 / 未建立

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 2；10；15

### related

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [RULE-WORLD-001](../rules/world.md#rule-world-001)
- [TEST-LIFE-003](../tests/candidates.md#test-life-003)
- [TEST-RESOURCE-001](../tests/candidates.md#test-resource-001)

<a id="decision-net-001"></a>

## DECISION-NET-001 — netvar / Replica / RPC / 原版 Action / Client View 如何判断？

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

先问要传意图还是状态，再考虑接口层和已有原版链。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Question

netvar / Replica / RPC / 原版 Action / Client View 如何判断？

### Branches

1. **condition**：原版 Action/Builder 已有对应权威请求链
   - **recommended_direction**：优先扩展原版链，不另造同义 RPC。
   - **evidence**：- [FACT-DST-009](../facts/klei-lua.md#fact-dst-009)
     - [RULE-NET-001](../rules/net.md#rule-net-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

2. **condition**：需要服务器向客户端展示小型持续状态
   - **recommended_direction**：考虑 netvar；按现有组件模型通过 Replica 提供读取 API。
   - **evidence**：- [FACT-DST-009](../facts/klei-lua.md#fact-dst-009)
     - [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
   - **exceptions**：Replica 是客户端接口/组织方式，不是与 netvar 互斥的传输协议。
   - **evidence_level**：E1
   - **needs_more_cases**：是

3. **condition**：额外一次性业务意图/返回结果
   - **recommended_direction**：考虑 Mod RPC；按需要设计关联ID、校验与错误结果。
   - **evidence**：- [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)
     - [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

4. **condition**：每玩家裁剪的较复杂数据视图
   - **recommended_direction**：考虑 Server View + Client Cache；需要明确初始同步和失效。
   - **evidence**：- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
     - [RULE-STATE-002](../rules/state.md#rule-state-002)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

5. **condition**：纯本地视觉/输入状态
   - **recommended_direction**：可保留本地；不得冒充服务器 gameplay 决策。
   - **evidence**：- [RULE-NET-001](../rules/net.md#rule-net-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

### Recommended Direction

先问要传意图还是状态，再考虑接口层和已有原版链。

### Exceptions

所有路径均需检查端别；不能把可写客户端缓存当服务端 API。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 3–9

### Unknowns

案例没有系统验证自定义 Replica 架构、预测回滚与高频流量阈值。

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

无 / 未建立

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 3–9

### related

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [RULE-NET-002](../rules/net.md#rule-net-002)
- [RULE-NET-003](../rules/net.md#rule-net-003)
- [TEST-NET-001](../tests/candidates.md#test-net-001)
- [TEST-NET-002](../tests/candidates.md#test-net-002)
- [TEST-NET-003](../tests/candidates.md#test-net-003)

<a id="decision-shard-001"></a>

## DECISION-SHARD-001 — 什么时候需要跨 Shard Service？

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

需求必须跨世界，且有明确的数据所有权，才引入服务。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Question

什么时候需要跨 Shard Service？

### Branches

1. **condition**：状态仅服务当前 World 的实体
   - **recommended_direction**：保留 World 服务，不加 Shard 层。
   - **evidence**：- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

2. **condition**：玩家迁移且原版已有适合的保存/迁移机制
   - **recommended_direction**：先确认原版契约，避免再复制一份状态。
   - **evidence**：- [RULE-PERSIST-001](../rules/persist.md#rule-persist-001)
   - **exceptions**：本案例没有完整迁移事实条目；此分支为待验证建议。
   - **evidence_level**：E0
   - **needs_more_cases**：是

3. **condition**：多个 Shard 必须共享同一稀缺资源
   - **recommended_direction**：先定义 authority、不变量与故障恢复，再选择服务协议。
   - **evidence**：- [RULE-SHARD-001](../rules/shard.md#rule-shard-001)
     - [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

4. **condition**：只需非关键的显示广播
   - **recommended_direction**：可以允许明确的陈旧/覆盖，不无条件加入事务。
   - **evidence**：- [ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

### Recommended Direction

需求必须跨世界，且有明确的数据所有权，才引入服务。

### Exceptions

单写、分区、多写都有适用边界；当前证据不证明一种机制普适。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7；12

### Unknowns

缺少成功运行的多 Shard 一致性独立案例和延迟/重连测量。

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

无 / 未建立

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7；12

### related

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)
- [RULE-STATE-001](../rules/state.md#rule-state-001)
- [TEST-SHARD-001](../tests/candidates.md#test-shard-001)
- [TEST-SHARD-002](../tests/candidates.md#test-shard-002)

<a id="decision-persist-001"></a>

## DECISION-PERSIST-001 — 哪些状态保存，哪些重建？

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

用“能否等价恢复”判定，不用字段是否容易序列化判定。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Question

哪些状态保存，哪些重建？

### Branches

1. **condition**：丢失会破坏资源/用户进度，且无法等价重算
   - **recommended_direction**：存真实 Owner 状态，给出 schema 和迁移/版本策略。
   - **evidence**：- [FACT-DST-001](../facts/klei-lua.md#fact-dst-001)
     - [FACT-DST-002](../facts/klei-lua.md#fact-dst-002)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

2. **condition**：可从加载后的实体完整恢复的 Registry/Index
   - **recommended_direction**：按生命周期重建，标注重建完成前的查询窗口。
   - **evidence**：- [RULE-PERSIST-001](../rules/persist.md#rule-persist-001)
     - [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

3. **condition**：Client View/Widget 显示副本
   - **recommended_direction**：初始同步或重读，不由它恢复服务器真相。
   - **evidence**：- [RULE-STATE-002](../rules/state.md#rule-state-002)
     - [RULE-STATE-003](../rules/state.md#rule-state-003)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

4. **condition**：暂停、选项、计时器、临时锁是否算用户意图不明确
   - **recommended_direction**：列出保存/重置后果交给项目决策，不套缓存口诀。
   - **evidence**：- [RULE-PERSIST-001](../rules/persist.md#rule-persist-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

### Recommended Direction

用“能否等价恢复”判定，不用字段是否容易序列化判定。

### Exceptions

某些缓存可为启动性能做可丢弃检查点，但不可反客为主。

### Evidence

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7；15–16

### Unknowns

schema 升级、跨版本读档和分片独立回档尚未验证。

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

无 / 未建立

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7；15–16

### related

- [RULE-PERSIST-001](../rules/persist.md#rule-persist-001)
- [FACT-DST-001](../facts/klei-lua.md#fact-dst-001)
- [TEST-LIFE-001](../tests/candidates.md#test-life-001)
- [TEST-LIFE-002](../tests/candidates.md#test-life-002)

<a id="decision-hook-001"></a>

## DECISION-HOOK-001 — PostInit / Instance Wrap / Class Patch / Upvalue Patch 如何选择？

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

最小足够作用域，不把方案列表当固定强制优先级。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Question

PostInit / Instance Wrap / Class Patch / Upvalue Patch 如何选择？

### Branches

1. **condition**：已有公开事件、回调或组件配置能完成需求
   - **recommended_direction**：使用既有扩展点；仍核对生命周期/端别。
   - **evidence**：- [FACT-DST-007](../facts/klei-lua.md#fact-dst-007)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

2. **condition**：仅新建特定实体/组件需要附加行为
   - **recommended_direction**：相应 PostInit；实例包装只影响目标实例。
   - **evidence**：- [FACT-DST-007](../facts/klei-lua.md#fact-dst-007)
     - [RULE-HOOK-003](../rules/hook.md#rule-hook-003)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

3. **condition**：确需共享类方法覆盖多实例
   - **recommended_direction**：明确实例自有方法遮蔽和已有引用，保留契约及兼容诊断。
   - **evidence**：- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
     - [RULE-HOOK-003](../rules/hook.md#rule-hook-003)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

4. **condition**：只能通过私有闭包/upvalue 接入
   - **recommended_direction**：隔离为版本敏感适配，能力检测、来源定位、失败降级和更新复核。
   - **evidence**：- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
     - [RULE-HOOK-003](../rules/hook.md#rule-hook-003)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

5. **condition**：打算调用前临时换函数再恢复
   - **recommended_direction**：优先考虑参数/上下文；若不可替代则加入异常/ownership 保护。
   - **evidence**：- [RULE-HOOK-002](../rules/hook.md#rule-hook-002)
     - [ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)
   - **exceptions**：需按本项目约束复核。
   - **evidence_level**：E1
   - **needs_more_cases**：是

### Recommended Direction

最小足够作用域，不把方案列表当固定强制优先级。

### Exceptions

会话级受控类扩展可合理；不因看到 monkey patch 就认定有错。

### Evidence

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 7–9；12–13

### Unknowns

尚无多 Mod 加载顺序与私有 API 升级的运行验收。

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

无 / 未建立

### sources

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 7–9；12–13

### related

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
- [RULE-HOOK-001](../rules/hook.md#rule-hook-001)
- [RULE-HOOK-002](../rules/hook.md#rule-hook-002)
- [TEST-HOOK-001](../tests/candidates.md#test-hook-001)
- [TEST-HOOK-002](../tests/candidates.md#test-hook-002)
