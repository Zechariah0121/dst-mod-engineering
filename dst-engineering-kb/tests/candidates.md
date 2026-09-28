# test_case · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="test-net-001"></a>

## TEST-NET-001 — Host vs Remote Client parity

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

发现本地快路径校验旁路。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

发现本地快路径校验旁路。

### Setup

同版本、同配置，Host 与远程玩家具备相同输入前置条件；分别测试合法/非法装备与状态。

### Action

分别发起同一业务意图。

### Expected Invariant

相同权威前置条件得到相同业务判定；传输差异不改变权限。

### Failure Signal

仅 Host 成功或参数检查不同且无设计依据。

### Applicable Patterns

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

### Evidence Source

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 4.3；5.2

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

未记录 / null

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

1. **type**：tests
   - **target**：[PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 4.3；5.2

### related

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

<a id="test-net-002"></a>

## TEST-NET-002 — Dedicated Server request flow

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

排除对 ThePlayer/HUD 等本地客户端对象的服务器依赖。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

排除对 ThePlayer/HUD 等本地客户端对象的服务器依赖。

### Setup

隔离专服与远程客户端，记录版本/配置/日志，服务端无本地玩家UI。

### Action

进入、初始化通道、发送业务命令、退出。

### Expected Invariant

服务端权威逻辑无需 HUD；客户端只经允许状态/结果更新。

### Failure Signal

专服 nil 错误、未创建通道或只有 Host 能使用。

### Applicable Patterns

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Evidence Source

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 3.3；9

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

未记录 / null

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

1. **type**：tests
   - **target**：[PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

2. **type**：tests
   - **target**：[PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 3.3；9

### related

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

<a id="test-shard-001"></a>

## TEST-SHARD-001 — Ground/Cave simultaneous modification

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

检查共享资源守恒。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

检查共享资源守恒。

### Setup

地面/洞穴同一逻辑资源，记录初始余额和物理物品数；同步控制两个请求时点。

### Action

跨分片并行存入/取出或其他写操作，等待通信稳定。

### Expected Invariant

在声明共享守恒的业务中，余额和实体变化符合合法串行/明确冲突语义，不超发。

### Failure Signal

分歧、丢更新或总量凭空变化。

### Applicable Patterns

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### Evidence Source

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7.3

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

未记录 / null

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

1. **type**：tests
   - **target**：[PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7.3

### related

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

<a id="test-life-001"></a>

## TEST-LIFE-001 — Player reconnect

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

检查重连重建与旧绑定资源回收。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

检查重连重建与旧绑定资源回收。

### Setup

记录每玩家 DB、任务、监听数量，准备可见状态。

### Action

多次退出/重连；必要时换 Shard；逐次核对实例身份。

### Expected Invariant

旧玩家绑定终止；新绑定拿到正确视图；任务数不随次数无界增长。

### Failure Signal

旧 owner 任务继续运行、重复回调或旧缓存显示。

### Applicable Patterns

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Evidence Source

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 16

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

未记录 / null

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

1. **type**：tests
   - **target**：[PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

2. **type**：tests
   - **target**：[PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 16

### related

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

<a id="test-life-002"></a>

## TEST-LIFE-002 — World save/load

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

区分真相保存与派生重建。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

区分真相保存与派生重建。

### Setup

记录真实物品/余额、用户选项及预期保存策略；正常保存。

### Action

重启同一存档并等初始化完成。

### Expected Invariant

真实状态符合保存点；派生 Registry 重建；被声明不保存的字段按约定重置。

### Failure Signal

双份注册、漏物品、把默认值误认作旧选择恢复。

### Applicable Patterns

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### Evidence Source

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7；15–16

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

未记录 / null

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

1. **type**：tests
   - **target**：[PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

2. **type**：tests
   - **target**：[PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7；15–16

### related

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

<a id="test-life-003"></a>

## TEST-LIFE-003 — Entity removed during query

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

检查失效候选和查询执行边界。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

检查失效候选和查询执行边界。

### Setup

注册容器并建立候选缓存；使用实际允许的事件/动作阶段注入移除，不假装逐行并发。

### Action

查询后、执行前或同步回调中删除实体/单独移除组件，再次请求。

### Expected Invariant

无失效引用崩溃；失败可解释；不得使用已失效实体或重复扣款。

### Failure Signal

nil/invalid Entity、旧计划执行、注销漏回调。

### Applicable Patterns

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Evidence Source

- [REPORT-R4](<../review-support/reports/sorachestmanager_DeepDive_20260928.txt>) · interpretation · 13–14

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

未记录 / null

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

1. **type**：tests
   - **target**：[PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### sources

- [REPORT-R4](<../review-support/reports/sorachestmanager_DeepDive_20260928.txt>) · interpretation · 13–14

### related

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

<a id="test-hook-001"></a>

## TEST-HOOK-001 — Wrapped function throws error

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

检查临时替换的异常恢复。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

检查临时替换的异常恢复。

### Setup

在隔离测试对象的 old 调用加入可控 error；外层捕获以检查后态。

### Action

进入 wrapper 触发异常，然后检查字段并执行第二次正常调用。

### Expected Invariant

自己的临时修改被清理；原始错误保留；不覆盖第三方新赋值。

### Failure Signal

wrapper/flag 残留或原错误被吞掉。

### Applicable Patterns

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Evidence Source

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 13

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

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

1. **type**：tests
   - **target**：[PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### sources

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 13

### related

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

<a id="test-hook-002"></a>

## TEST-HOOK-002 — Two Mods wrap same function

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

验证包装组合与 ownership。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

验证包装组合与 ownership。

### Setup

两个最小测试补丁分别包装同一目标，覆盖不同加载顺序及实例/类组合。

### Action

调用、让一方撤销或在回调中重装另一方。

### Expected Invariant

约定要保留的行为执行正确次数，撤销不抹掉别人包装，返回值契约保留。

### Failure Signal

双调用、丢调用、后装 wrapper 被旧恢复覆盖。

### Applicable Patterns

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Evidence Source

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 12–13

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

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

1. **type**：tests
   - **target**：[PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### sources

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 12–13

### related

- [PATTERN-FRAMEWORK-001](../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

<a id="test-resource-001"></a>

## TEST-RESOURCE-001 — Same Entity exposed by two resource providers

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

验证分配交集处理。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

验证分配交集处理。

### Setup

Provider A/B 返回同一 Stack；设真实可用量小于合并后的名义量。

### Action

执行不足和足够两组查询/制作，记录每实体分配及真实扣除。

### Expected Invariant

同一实体只消耗其实际可用预算；不足时拒绝或按声明的部分语义处理。

### Failure Signal

Has 通过但计划少扣、重复预算、覆盖数量。

### Applicable Patterns

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### Evidence Source

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 11.3

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

未记录 / null

### Needs More Cases

是

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- world
  - resources
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server

### Typed Relations

1. **type**：tests
   - **target**：[PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 11.3

### related

- [PATTERN-WORLD-001](../patterns/PATTERN-WORLD-001.md#pattern-world-001)

<a id="test-shard-002"></a>

## TEST-SHARD-002 — Shard disconnect / reconnect recovery

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

验证恢复来源与陈旧写策略。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

验证恢复来源与陈旧写策略。

### Setup

记录两个 Shard 状态，断开一个，另一边产生真实变更。

### Action

重连后读/写，并测试各分片保存再重启。

### Expected Invariant

恢复遵守声明的 authority/epoch/冲突策略；陈旧副本不能无条件覆写稀缺资源。

### Failure Signal

旧余额恢复、无追赶机制、把客户端 Sync 当作 Shard 恢复。

### Applicable Patterns

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### Evidence Source

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7.3

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

未记录 / null

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

1. **type**：tests
   - **target**：[PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 7.3

### related

- [PATTERN-SHARD-001](../patterns/PATTERN-SHARD-001.md#pattern-shard-001)

<a id="test-net-003"></a>

## TEST-NET-003 — Stale cache and optimistic UI

类型：Recommendation · Evidence：E1 · Confidence：Medium · Status：candidate · Version：0.1.1

验证 UI 与业务成功的边界。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Purpose

验证 UI 与业务成功的边界。

### Setup

延迟客户端状态更新或令材料变化；记录实际服务端数据。

### Action

打开UI、发起操作、等待状态刷新或服务器拒绝。

### Expected Invariant

客户端陈旧不导致越权；最终结果可解释；显示可尝试不被当作已成功。

### Failure Signal

UI 永久显示旧值、客户端数字直接写入权威、失败无反馈。

### Applicable Patterns

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

### Evidence Source

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 5.1；8.3；17

### Execution Status

not_run

### Applicability

仅在相关状态/机制存在时执行；不是每个小 Mod 的强制全量测试。

### Result

未记录 / null

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

1. **type**：tests
   - **target**：[PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 5.1；8.3；17

### related

- [PATTERN-NET-001](../patterns/PATTERN-NET-001.md#pattern-net-001)
