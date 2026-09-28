# playbook · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="arp-dst-001"></a>

## ARP-DST-001 — DST Architecture Reasoning Process v0.1

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

按需求、状态、权威与生命周期逐步选择结构，检索事实/反例后再决定模式。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Process Version

0.1

### Steps

1. **order**：1
   - **name**：Requirement Decomposition
   - **ai_should_ask**：哪些玩家行为必须发生，什么不变量不能破坏？
   - **expected_output**：需求/非目标/验收场景列表。
   - **common_errors**：从一个案例直接选架构，不先确认需求。
   - **retrieve_entry_types**：- case
     - rule
     - failure_case
   - **entry_ids**：- [RULE-NET-001](../rules/net.md#rule-net-001)
     - [RULE-STATE-004](../rules/state.md#rule-state-004)

2. **order**：2
   - **name**：State Inventory
   - **ai_should_ask**：每个数字、实体关联、开关、视图和缓存是什么？
   - **expected_output**：状态清单，区分真实/派生/短时上下文。
   - **common_errors**：只列组件名，不列状态。
   - **retrieve_entry_types**：- case
     - source_fact
   - **entry_ids**：- [RULE-STATE-002](../rules/state.md#rule-state-002)

3. **order**：3
   - **name**：State Ownership
   - **ai_should_ask**：谁持有、写入和读取每项状态？
   - **expected_output**：State | Owner | Writer | Reader | Replicated | Persisted | Rebuildable 矩阵。
   - **common_errors**：把 View、Cache、Widget 都当 Owner。
   - **retrieve_entry_types**：- rule
     - decision
   - **entry_ids**：- [DECISION-STATE-OWNER-001](../decisions/candidates.md#decision-state-owner-001)
     - [RULE-STATE-002](../rules/state.md#rule-state-002)

4. **order**：4
   - **name**：Scope
   - **ai_should_ask**：状态属于单实体、玩家、World 还是多个 Shard？
   - **expected_output**：范围及依赖图，列出不存在的层。
   - **common_errors**：为了图完整加 Manager/Shard 层。
   - **retrieve_entry_types**：- pattern
     - decision
   - **entry_ids**：- [DECISION-STATE-OWNER-001](../decisions/candidates.md#decision-state-owner-001)
     - [DECISION-SHARD-001](../decisions/candidates.md#decision-shard-001)

5. **order**：5
   - **name**：Authority
   - **ai_should_ask**：对客户端、其他玩家、其他 Shard 分别谁能决定结果？
   - **expected_output**：写入权威表及冲突/恢复语义。
   - **common_errors**：使用 Server 一词掩盖多 Server 可写。
   - **retrieve_entry_types**：- rule
     - anti_pattern
     - failure_case
   - **entry_ids**：- [RULE-STATE-001](../rules/state.md#rule-state-001)
     - [FAIL-CASE001-001](../failures/case001.md#fail-case001-001)

6. **order**：6
   - **name**：Lifecycle
   - **ai_should_ask**：对象何时建、绑定、暂停、注销？任务实际挂谁？
   - **expected_output**：创建/加入/退出/移除/重载矩阵及 cleanup owner。
   - **common_errors**：以世界销毁会清理代替玩家注销清理。
   - **retrieve_entry_types**：- rule
     - failure_case
     - source_fact
   - **entry_ids**：- [RULE-LIFE-001](../rules/life.md#rule-life-001)
     - [FACT-DST-008](../facts/klei-lua.md#fact-dst-008)

7. **order**：7
   - **name**：Networking
   - **ai_should_ask**：传 Intent 还是 State？原版是否已有链？
   - **expected_output**：Host/Remote/Dedicated 请求和返回图，校验、超时/重试语义。
   - **common_errors**：所有请求套自定义 RPC；把缓存更新当逐请求 ACK。
   - **retrieve_entry_types**：- decision
     - pattern
     - source_fact
   - **entry_ids**：- [DECISION-NET-001](../decisions/candidates.md#decision-net-001)
     - [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)

8. **order**：8
   - **name**：Persistence
   - **ai_should_ask**：重启后哪些信息无法等价重算？
   - **expected_output**：保存 schema、重建来源、初始化完成条件和升级/回档问题。
   - **common_errors**：把能序列化等同应该保存。
   - **retrieve_entry_types**：- decision
     - source_fact
   - **entry_ids**：- [DECISION-PERSIST-001](../decisions/candidates.md#decision-persist-001)
     - [FACT-DST-001](../facts/klei-lua.md#fact-dst-001)

9. **order**：9
   - **name**：Coordination
   - **ai_should_ask**：多实体/来源有交集吗？Query 到执行之间会变化吗？
   - **expected_output**：资源分配图、预算/提交边界及失败补偿。
   - **common_errors**：单线程就没有逻辑竞争；相同实体按来源重复预算。
   - **retrieve_entry_types**：- rule
     - anti_pattern
     - failure_case
   - **entry_ids**：- [RULE-RESOURCE-001](../rules/resource.md#rule-resource-001)
     - [RULE-RESOURCE-002](../rules/resource.md#rule-resource-002)

10. **order**：10
   - **name**：Performance
   - **ai_should_ask**：多少任务/监听/扫描？空闲也扫描吗？
   - **expected_output**：复杂度估计、规模变量、测量计划；先不捏造 benchmark。
   - **common_errors**：Manager 等于高性能；提前引入重型索引。
   - **retrieve_entry_types**：- pattern
     - rule
     - test_case
   - **entry_ids**：- [RULE-WORLD-002](../rules/world.md#rule-world-002)

11. **order**：11
   - **name**：Hook / Compatibility
   - **ai_should_ask**：改实例、类还是闭包？异常/重装会怎样？
   - **expected_output**：Hook 目标表、owner、前驱、恢复和私有接口版本边界。
   - **common_errors**：仅正常返回保留 oldfn 就称兼容安全。
   - **retrieve_entry_types**：- decision
     - anti_pattern
     - source_fact
   - **entry_ids**：- [DECISION-HOOK-001](../decisions/candidates.md#decision-hook-001)
     - [RULE-HOOK-002](../rules/hook.md#rule-hook-002)

12. **order**：12
   - **name**：Validation Matrix
   - **ai_should_ask**：每条主张需要哪种证据？哪些测试实际执行？
   - **expected_output**：需求→代码事实→测试候选→执行环境→结果矩阵；明确待验证。
   - **common_errors**：语法通过就升级 E4；测试候选写成执行记录。
   - **retrieve_entry_types**：- test_case
     - source_fact
     - correction
   - **entry_ids**：- [TEST-NET-001](../tests/candidates.md#test-net-001)
     - [TEST-NET-002](../tests/candidates.md#test-net-002)
     - [CORRECTION-CASE001-001](../corrections/CASE-001.md#correction-case001-001)

### Retrieval Policy

- 先读取 status 和 Corrections；过期/撤回主张不可直接用于建议。
- 读取 Pattern 时同时取 Related Rule/Anti-Pattern/Decision/Test；不要只取支持它的正例。
- 给建议标注适用条件、证据等级、置信度和未测项；同一案例的多报告不是 E2。
- E3 事实引用快照与函数；Recommendation 不因引用 E3 而自动变成 Klei Fact。

### Stop Conditions

不明确的玩法/数值/用户意图列出选项；只在有证据的工程边界自主选择。

### Revision Policy

CASE-002+ 提供独立证据后修订；保留旧 version 与 Correction/Deprecated 状态。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- architecture
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

无 / 未建立

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 2；12–19
- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 7–15

### related

- [RULE-NET-001](../rules/net.md#rule-net-001)
- [RULE-STATE-004](../rules/state.md#rule-state-004)
- [RULE-STATE-002](../rules/state.md#rule-state-002)
- [DECISION-STATE-OWNER-001](../decisions/candidates.md#decision-state-owner-001)
- [DECISION-SHARD-001](../decisions/candidates.md#decision-shard-001)
- [RULE-STATE-001](../rules/state.md#rule-state-001)
- [FAIL-CASE001-001](../failures/case001.md#fail-case001-001)
- [RULE-LIFE-001](../rules/life.md#rule-life-001)
- [FACT-DST-008](../facts/klei-lua.md#fact-dst-008)
- [DECISION-NET-001](../decisions/candidates.md#decision-net-001)
- [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)
- [DECISION-PERSIST-001](../decisions/candidates.md#decision-persist-001)
- [FACT-DST-001](../facts/klei-lua.md#fact-dst-001)
- [RULE-RESOURCE-001](../rules/resource.md#rule-resource-001)
- [RULE-RESOURCE-002](../rules/resource.md#rule-resource-002)
- [RULE-WORLD-002](../rules/world.md#rule-world-002)
- [DECISION-HOOK-001](../decisions/candidates.md#decision-hook-001)
- [RULE-HOOK-002](../rules/hook.md#rule-hook-002)
- [TEST-NET-001](../tests/candidates.md#test-net-001)
- [TEST-NET-002](../tests/candidates.md#test-net-002)
- [CORRECTION-CASE001-001](../corrections/CASE-001.md#correction-case001-001)
