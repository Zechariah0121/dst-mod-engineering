# anti_pattern · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="anti-net-001"></a>

## ANTI-NET-001 — Client / Host Divergent Validation

类型：Recommendation · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

Host 直接调用业务方法，Remote 先经过校验 Adapter。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Client / Host Divergent Validation

### Symptoms

Host 直接调用业务方法，Remote 先经过校验 Adapter。

### Why It Happens

把本地 transport 优化与验证入口一起绕过。

### Why It Is Dangerous

同一功能出现不同条件或权限；只测试 Host 容易漏远端错误。

### When It Is Actually Acceptable

两条路径最终共享同一校验，或差异仅涉及本地视觉且明确设计时。

### Failure Modes

- Host 成功而 Remote 失败
- 校验遗漏

### Detection

比较两条调用链进入 State Owner 前的检查集合。

### Safer Alternatives

- 共用服务器业务验证入口，仅省略传输
- 以端别对照测试确认预期差异

### Case Evidence

REPORT-R6 §4.3、5.2：种子 Host 直调 Handle 方法，Remote 经过手持组件 Adapter。

### Klei Basis

- [FACT-DST-009](../facts/klei-lua.md#fact-dst-009)

### Related Rule

- [RULE-NET-001](../rules/net.md#rule-net-001)
- [RULE-NET-002](../rules/net.md#rule-net-002)

### Related Pattern

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

### Assessment

observed_structure

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

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 4.3；5.2

### related

- [FACT-DST-009](../facts/klei-lua.md#fact-dst-009)
- [RULE-NET-001](../rules/net.md#rule-net-001)
- [RULE-NET-002](../rules/net.md#rule-net-002)
- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [DECISION-NET-001](../decisions/candidates.md#decision-net-001)

<a id="anti-shard-001"></a>

## ANTI-SHARD-001 — Writable Replica Read-Modify-Write

类型：Recommendation · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

多个副本基于旧余额各自计算新余额。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Writable Replica Read-Modify-Write

### Symptoms

多个副本基于旧余额各自计算新余额。

### Why It Happens

本地 Get/Set 接口掩盖了分布式写入。

### Why It Is Dangerous

各自操作合理，但合并不守恒。

### When It Is Actually Acceptable

状态独立分区、不要求合并，或已有可证明的冲突处理协议。

### Failure Modes

- 丢更新
- 旧副本覆写
- 超提

### Detection

查同一 key 是否多写者，值是操作还是读旧值后的结果。

### Safer Alternatives

- 单写 authority 接受操作意图
- 有需求时设计带版本的条件提交与补偿

### Case Evidence

REPORT-R6 §7.3：SeedDB 两 Shard 基于同一个旧数值写回完整值。

### Klei Basis

- [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)

### Related Rule

- [RULE-SHARD-001](../rules/shard.md#rule-shard-001)
- [RULE-STATE-004](../rules/state.md#rule-state-004)

### Related Pattern

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### Assessment

observed_structure

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

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7.3

### related

- [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)
- [RULE-SHARD-001](../rules/shard.md#rule-shard-001)
- [RULE-STATE-004](../rules/state.md#rule-state-004)
- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)
- [DECISION-SHARD-001](../decisions/candidates.md#decision-shard-001)
- [FAIL-CASE001-001](../failures/case001.md#fail-case001-001)

<a id="anti-shard-002"></a>

## ANTI-SHARD-002 — Broadcast Final Value Without Authority

类型：Recommendation · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

广播完整最终值，却未声明谁能写、过期写如何判断。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Broadcast Final Value Without Authority

### Symptoms

广播完整最终值，却未声明谁能写、过期写如何判断。

### Why It Happens

把复制机制当作一致性策略。

### Why It Is Dangerous

到达顺序替代业务顺序；重连和重启不知向谁恢复。

### When It Is Actually Acceptable

唯一写者的配置/展示值广播，或明确允许最后到达覆盖的非关键状态。

### Failure Modes

- 副本分歧
- 重连恢复错误

### Detection

记录 writer、revision 和恢复源；不要仅检查是否用了 Shard RPC。

### Safer Alternatives

- 在协议前声明 authority
- 只为必要场景增加 revision/epoch/重新同步

### Case Evidence

REPORT-R6 §6–7：种子任意 Shard Set 广播，且 noSyn=1 使本业务缺少自动恢复。

### Klei Basis

- [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)

### Related Rule

- [RULE-STATE-001](../rules/state.md#rule-state-001)
- [RULE-SHARD-001](../rules/shard.md#rule-shard-001)

### Related Pattern

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### Assessment

observed_structure

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

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 6–7

### related

- [FACT-DST-006](../facts/klei-lua.md#fact-dst-006)
- [RULE-STATE-001](../rules/state.md#rule-state-001)
- [RULE-SHARD-001](../rules/shard.md#rule-shard-001)
- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)
- [DECISION-SHARD-001](../decisions/candidates.md#decision-shard-001)
- [FAIL-CASE001-001](../failures/case001.md#fail-case001-001)

<a id="anti-resource-001"></a>

## ANTI-RESOURCE-001 — Duplicate Resource Provider Allocation

类型：Recommendation · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

不同 Provider 返回同一 Item 实体，合并时当成独立数量或直接覆盖。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Duplicate Resource Provider Allocation

### Symptoms

不同 Provider 返回同一 Item 实体，合并时当成独立数量或直接覆盖。

### Why It Happens

按来源名区分资源，却未按实体身份计算交集。

### Why It Is Dangerous

Has 通过但计划不足，或同一 Stack 被重复预算。

### When It Is Actually Acceptable

来源集合已证明互斥，或合并器按剩余预算统一分配。

### Failure Modes

- 少扣材料
- 重复扣同一资源
- 虚假充足判断

### Detection

构造一个同时出现在两个来源中的实体，检查最终每实体数量和总需求。

### Safer Alternatives

- 统一资源身份与排除/剩余预算
- 提交前验证计划总量与各实体可用量

### Case Evidence

REPORT-R6 §11.3：原版打开容器与 Manager 同指 E，finds[E]=2 覆盖原版的 4。

### Klei Basis

- [FACT-DST-003](../facts/klei-lua.md#fact-dst-003)
- [FACT-DST-010](../facts/klei-lua.md#fact-dst-010)

### Related Rule

- [RULE-RESOURCE-001](../rules/resource.md#rule-resource-001)
- [RULE-RESOURCE-002](../rules/resource.md#rule-resource-002)

### Related Pattern

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Assessment

observed_failure_path

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- world
  - resources
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server

### Typed Relations

无 / 未建立

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 11.3

### related

- [FACT-DST-003](../facts/klei-lua.md#fact-dst-003)
- [FACT-DST-010](../facts/klei-lua.md#fact-dst-010)
- [RULE-RESOURCE-001](../rules/resource.md#rule-resource-001)
- [RULE-RESOURCE-002](../rules/resource.md#rule-resource-002)
- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [DECISION-STATE-OWNER-001](../decisions/candidates.md#decision-state-owner-001)
- [FAIL-CASE001-002](../failures/case001.md#fail-case001-002)

<a id="anti-hook-001"></a>

## ANTI-HOOK-001 — Unsafe Temporary Monkey Patch

类型：Recommendation · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

保存旧方法 → 临时替换 → 调用 → 正常返回后恢复，缺少异常恢复。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Unsafe Temporary Monkey Patch

### Symptoms

保存旧方法 → 临时替换 → 调用 → 正常返回后恢复，缺少异常恢复。

### Why It Happens

只为正常调用设计 around 包装。

### Why It Is Dangerous

异常使后续调用读到临时状态；恢复也可能覆盖回调期间的新赋值。

### When It Is Actually Acceptable

可靠限定无异常/无重入的内部范围，或有异常安全且有所有权检查的恢复；须给出依据。

### Failure Modes

- 临时函数残留
- 状态 flag 泄漏
- 返回值契约丢失

### Detection

检查 error、嵌套调用、允许 yield 的边界和替换期间第三方赋值。

### Safer Alternatives

- 显式上下文参数优先
- 确需替换时保留错误与完整返回值，并执行受 ownership 保护的清理

### Case Evidence

REPORT-R5 §13；REPORT-R6 §17：inventory.Has/GetCraftingIngredient 临时替换后仅正常路径恢复。

### Klei Basis

- [FACT-DST-003](../facts/klei-lua.md#fact-dst-003)

### Related Rule

- [RULE-HOOK-002](../rules/hook.md#rule-hook-002)
- [RULE-LIFE-001](../rules/life.md#rule-life-001)

### Related Pattern

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Assessment

observed_failure_path

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

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 13
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 17

### related

- [FACT-DST-003](../facts/klei-lua.md#fact-dst-003)
- [RULE-HOOK-002](../rules/hook.md#rule-hook-002)
- [RULE-LIFE-001](../rules/life.md#rule-life-001)
- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
- [DECISION-HOOK-001](../decisions/candidates.md#decision-hook-001)
- [FAIL-CASE001-003](../failures/case001.md#fail-case001-003)

<a id="anti-hook-002"></a>

## ANTI-HOOK-002 — Hook Without Ownership

类型：Recommendation · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

卸载直接写回旧指针，或替换清理回调却未保留原职责。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Hook Without Ownership

### Symptoms

卸载直接写回旧指针，或替换清理回调却未保留原职责。

### Why It Happens

把函数槽当作自己独占的字段。

### Why It Is Dangerous

覆盖别的 Mod 后来安装的包装，或截断原版清理。

### When It Is Actually Acceptable

显式独占、不可卸载的会话级替换；仍需承认对其他 Mod 的影响。

### Failure Modes

- 卸载别人包装
- 漏 Close/cleanup
- 重装叠加

### Detection

记录目标、前驱、自己 wrapper；退出前确认当前字段归属。

### Safer Alternatives

- 明确 wrapper ownership
- 保持原回调契约
- 限制到必要实例并提供诊断

### Case Evidence

REPORT-R5 §12–13：恢复无 ownership 检查；REPORT-R4 §13：Container 卸载 oldfn 保存后未调用。

### Klei Basis

- [FACT-DST-008](../facts/klei-lua.md#fact-dst-008)

### Related Rule

- [RULE-HOOK-002](../rules/hook.md#rule-hook-002)
- [RULE-HOOK-003](../rules/hook.md#rule-hook-003)

### Related Pattern

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Assessment

observed_structure

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

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 12–13
- [REPORT-R4](<../review-support/reports/sorachestmanager_DeepDive_20260928.txt>) · interpretation · 13

### related

- [FACT-DST-008](../facts/klei-lua.md#fact-dst-008)
- [RULE-HOOK-002](../rules/hook.md#rule-hook-002)
- [RULE-HOOK-003](../rules/hook.md#rule-hook-003)
- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
- [DECISION-HOOK-001](../decisions/candidates.md#decision-hook-001)

<a id="anti-life-001"></a>

## ANTI-LIFE-001 — Lifecycle Owner Mismatch

类型：Recommendation · Evidence：E1 · Confidence：High · Status：candidate · Version：0.1.1

短命 DB/UI 关闭，挂在长命 World 的 Task/Listener 仍持有它。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Lifecycle Owner Mismatch

### Symptoms

短命 DB/UI 关闭，挂在长命 World 的 Task/Listener 仍持有它。

### Why It Happens

用调度宿主代替业务所有者，注销只删注册表。

### Why It Is Dangerous

旧对象保活、重复任务或对旧身份继续计算。

### When It Is Actually Acceptable

任务确实服务整世界，并不捕获已退出用户上下文。

### Failure Modes

- Task 残留
- Listener 残留
- 重连后旧闭包并存

### Detection

比较创建者、scheduler owner 和应该终止它的业务事件。

### Safer Alternatives

- 绑定清理句柄到业务生命周期
- 在注销入口统一取消自己的任务与监听

### Case Evidence

REPORT-R6 §16：UpdateOwnerKeyTask 挂 World，ClientDB UnInit 未取消。

### Klei Basis

- [FACT-DST-008](../facts/klei-lua.md#fact-dst-008)

### Related Rule

- [RULE-LIFE-001](../rules/life.md#rule-life-001)

### Related Pattern

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Assessment

observed_failure_path

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- lifecycle
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

无 / 未建立

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 16

### related

- [FACT-DST-008](../facts/klei-lua.md#fact-dst-008)
- [RULE-LIFE-001](../rules/life.md#rule-life-001)
- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [DECISION-PERSIST-001](../decisions/candidates.md#decision-persist-001)
- [DECISION-STATE-OWNER-001](../decisions/candidates.md#decision-state-owner-001)
- [FAIL-CASE001-004](../failures/case001.md#fail-case001-004)

<a id="anti-world-001"></a>

## ANTI-WORLD-001 — God Manager — risk candidate

类型：Recommendation · Evidence：E0 · Confidence：Low · Status：candidate · Version：0.1.1

候选征兆：查询、调度、资源真相、UI、联网及保存策略逐步集中进同一 Manager。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

God Manager — risk candidate

### Symptoms

候选征兆：查询、调度、资源真相、UI、联网及保存策略逐步集中进同一 Manager。

### Why It Happens

把集中协调误解成集中所有实体行为。

### Why It Is Dangerous

跨领域耦合和测试面增长，局部变更需要理解全部系统。

### When It Is Actually Acceptable

职责相邻、规模受控的领域 Manager 可同时协调查询和物流；行数多不直接证明 God Object。

### Failure Modes

- 潜在改动扩散
- 潜在共享故障面

### Detection

检查职责变化原因、依赖方向及是否拥有本该归实体的状态；不能只数函数。

### Safer Alternatives

- 先观察变化耦合和性能再拆分
- 让单体状态留在 Component

### Case Evidence

REPORT-R4 §17–20 证明多职责领域 Manager；不足以断言已经达到 God Object。仅登记待验证风险。

### Klei Basis

无 / 未建立

### Related Rule

- [RULE-WORLD-001](../rules/world.md#rule-world-001)
- [RULE-WORLD-002](../rules/world.md#rule-world-002)

### Related Pattern

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Assessment

risk_candidate_not_established

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- world
  - lifecycle
- **evidence_modes**：- hypothesis
- **runtime_environments**：无 / 未建立
- **sides**：- server

### Typed Relations

无 / 未建立

### sources

- [REPORT-R4](<../review-support/reports/sorachestmanager_DeepDive_20260928.txt>) · interpretation · 17–20

### related

- [RULE-WORLD-001](../rules/world.md#rule-world-001)
- [RULE-WORLD-002](../rules/world.md#rule-world-002)
- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [DECISION-STATE-OWNER-001](../decisions/candidates.md#decision-state-owner-001)

<a id="anti-framework-001"></a>

## ANTI-FRAMEWORK-001 — Unlimited Ambient Dependency / Shared Namespace Growth

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

整个可写环境作为公共 API，模块裸符号依赖难从 require 图看出。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Name

Unlimited Ambient Dependency / Shared Namespace Growth

### Symptoms

整个可写环境作为公共 API，模块裸符号依赖难从 require 图看出。

### Why It Happens

便捷访问不断扩展到工具、业务对象和临时状态。

### Why It Is Dangerous

初始化顺序、覆盖和跨模块写入变成隐含契约。

### When It Is Actually Acceptable

少量稳定公共能力、命名和写入责任明确、依赖可追溯时可采用共享表。

### Failure Modes

- 错误时序
- 命名冲突风险
- API 面不可控

### Detection

为消费符号追定义、首次可用时点和全部写者；不能仅统计 require。

### Safer Alternatives

- 有限服务出口
- 显式模块返回值
- 记录启动阶段和可选能力

### Case Evidence

REPORT-R5 §2–5、14：SoraAPI 为 env 别名，soraenv 共享查找；未证明所有潜在冲突已实际发生。

### Klei Basis

- [FACT-DST-007](../facts/klei-lua.md#fact-dst-007)

### Related Rule

- [RULE-FRAMEWORK-001](../rules/framework.md#rule-framework-001)

### Related Pattern

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Assessment

observed_structure

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- framework
  - hooks
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

无 / 未建立

### sources

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 2–5；14

### related

- [FACT-DST-007](../facts/klei-lua.md#fact-dst-007)
- [RULE-FRAMEWORK-001](../rules/framework.md#rule-framework-001)
- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
- [DECISION-HOOK-001](../decisions/candidates.md#decision-hook-001)
