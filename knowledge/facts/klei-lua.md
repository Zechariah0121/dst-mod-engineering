# source_fact · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="fact-dst-001"></a>

## FACT-DST-001 — EntityScript 组件持久化遍历

类型：Klei Fact · Evidence：E3 · Confidence：Very High · Status：supported_by_klei · Version：0.1.1

保存遍历 components 中提供 OnSave 的对象；加载按组件键寻找当前对象并调用 OnLoad。对象不必因由 AddComponent 创建才获调用。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Api Mechanism

EntityScript 组件持久化遍历

### Observed Behaviour

保存遍历 components 中提供 OnSave 的对象；加载按组件键寻找当前对象并调用 OnLoad。对象不必因由 AddComponent 创建才获调用。

### Source File

- `vanilla-snapshot/scripts/entityscript.lua`（original provenance；不作为包内链接）

### Relevant Function

GetPersistData / SetPersistData

### Source Locator

1903–1980

### Version Context

KLEI-LOCAL-20260928；原版发行 build 未记录；前轮对照本机 scripts.zip，非最新版本承诺。

### Implication

手工挂入的服务对象可参与世界保存，但应遵守这些函数契约。

### Do Not Infer

不能推出组件加载有任意依赖顺序、任意对象都适合伪装成组件，或自动完成引用修复。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- persistence
  - lifecycle
- **evidence_modes**：- vanilla_source
  - static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

无 / 未建立

### sources

- KLEI-LOCAL-20260928（外部来源未随包） · direct_evidence · 1903–1980；GetPersistData / SetPersistData · 源文件身份为直接原版依据；既有报告记录了对照过程。本轮未重新解读源码，源文件不随包。
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · supplementary_interpretation · 7.1–7.2

### related

- [ARP-DST-001](../playbooks/ARP-DST-001.md#arp-dst-001)

<a id="fact-dst-002"></a>

## FACT-DST-002 — Container 的物品存档

类型：Klei Fact · Evidence：E3 · Confidence：Very High · Status：supported_by_klei · Version：0.1.1

有效且可持久化的槽位物品以 GetSaveRecord 记录；加载通过 SpawnSaveRecord 重建并 GiveItem 到槽位。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Api Mechanism

Container 的物品存档

### Observed Behaviour

有效且可持久化的槽位物品以 GetSaveRecord 记录；加载通过 SpawnSaveRecord 重建并 GiveItem 到槽位。

### Source File

- `vanilla-snapshot/scripts/components/container.lua`（original provenance；不作为包内链接）

### Relevant Function

OnSave / OnLoad

### Source Locator

979–1007

### Version Context

KLEI-LOCAL-20260928；原版发行 build 未记录；前轮对照本机 scripts.zip，非最新版本承诺。

### Implication

真实物品可沿原版容器保存，注册表不必重复保存同一批物品。

### Do Not Infer

不能推出所有 runtime metadata、暂停/进度或玩家选择都自动保存。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- persistence
  - resources
- **evidence_modes**：- vanilla_source
  - static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server

### Typed Relations

无 / 未建立

### sources

- KLEI-LOCAL-20260928（外部来源未随包） · direct_evidence · 979–1007；OnSave / OnLoad · 源文件身份为直接原版依据；既有报告记录了对照过程。本轮未重新解读源码，源文件不随包。
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · supplementary_interpretation · 16

### related

- [ARP-DST-001](../playbooks/ARP-DST-001.md#arp-dst-001)

<a id="fact-dst-003"></a>

## FACT-DST-003 — Builder 查询与消耗边界

类型：Klei Fact · Evidence：E3 · Confidence：Very High · Status：supported_by_klei · Version：0.1.1

检查、形成材料实体分配表、消耗分别在不同函数中；普通库存产品分支先 SpawnPrefab，后 RemoveIngredients，再交付，manufactured 分支不同。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Api Mechanism

Builder 查询与消耗边界

### Observed Behaviour

检查、形成材料实体分配表、消耗分别在不同函数中；普通库存产品分支先 SpawnPrefab，后 RemoveIngredients，再交付，manufactured 分支不同。

### Source File

- `vanilla-snapshot/scripts/components/builder.lua`（original provenance；不作为包内链接）

### Relevant Function

HasIngredients / GetIngredients / RemoveIngredients / DoBuild

### Source Locator

500–583；657–755

### Version Context

KLEI-LOCAL-20260928；原版发行 build 未记录；前轮对照本机 scripts.zip，非最新版本承诺。

### Implication

新增材料来源必须匹配原版分配表及真实执行顺序。

### Do Not Infer

不能推出查询即预留、整个过程是事务，或所有配方都先生成产物。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- resources
  - world
- **evidence_modes**：- vanilla_source
  - static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server

### Typed Relations

无 / 未建立

### sources

- KLEI-LOCAL-20260928（外部来源未随包） · direct_evidence · 500–583；657–755；HasIngredients / GetIngredients / RemoveIngredients / DoBuild · 源文件身份为直接原版依据；既有报告记录了对照过程。本轮未重新解读源码，源文件不随包。
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · supplementary_interpretation · 9–11

### related

- [ARP-DST-001](../playbooks/ARP-DST-001.md#arp-dst-001)

<a id="fact-dst-004"></a>

## FACT-DST-004 — InventoryItem 的 Owner 清理

类型：Klei Fact · Evidence：E3 · Confidence：Very High · Status：supported_by_klei · Version：0.1.1

物品销毁时，若仍有 owner，按其 Inventory 或 Container 移除该物品，并发送世界 forgetinventoryitem 事件。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Api Mechanism

InventoryItem 的 Owner 清理

### Observed Behaviour

物品销毁时，若仍有 owner，按其 Inventory 或 Container 移除该物品，并发送世界 forgetinventoryitem 事件。

### Source File

- `vanilla-snapshot/scripts/components/inventoryitem.lua`（original provenance；不作为包内链接）

### Relevant Function

OnRemoveEntity

### Source Locator

478–491

### Version Context

KLEI-LOCAL-20260928；原版发行 build 未记录；前轮对照本机 scripts.zip，非最新版本承诺。

### Implication

物品所有权清理与管理器索引清理是两项不同职责。

### Do Not Infer

不能推出失效引用会被任意业务缓存自动删除。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- lifecycle
- **evidence_modes**：- vanilla_source
  - static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

无 / 未建立

### sources

- KLEI-LOCAL-20260928（外部来源未随包） · direct_evidence · 478–491；OnRemoveEntity · 源文件身份为直接原版依据；既有报告记录了对照过程。本轮未重新解读源码，源文件不随包。
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · supplementary_interpretation · 11.2

### related

- [ARP-DST-001](../playbooks/ARP-DST-001.md#arp-dst-001)

<a id="fact-dst-005"></a>

## FACT-DST-005 — Stackable 拆分

类型：Klei Fact · Evidence：E3 · Confidence：Very High · Status：supported_by_klei · Version：0.1.1

堆叠拆分会产生分离物品并调整原堆叠数量；数量可由 Stackable 自身保存/恢复。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Api Mechanism

Stackable 拆分

### Observed Behaviour

堆叠拆分会产生分离物品并调整原堆叠数量；数量可由 Stackable 自身保存/恢复。

### Source File

- `vanilla-snapshot/scripts/components/stackable.lua`（original provenance；不作为包内链接）

### Relevant Function

Get / SetStackSize / OnSave / OnLoad

### Source Locator

88–109 起

### Version Context

KLEI-LOCAL-20260928；原版发行 build 未记录；前轮对照本机 scripts.zip，非最新版本承诺。

### Implication

查询者引用一个 Stack 不代表获得独占权；消耗者须对照拆分行为。

### Do Not Infer

不能推出跨容器/跨玩家分配自动去重，也不能认为拆分是一项跨系统事务。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- resources
- **evidence_modes**：- vanilla_source
  - static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server

### Typed Relations

无 / 未建立

### sources

- KLEI-LOCAL-20260928（外部来源未随包） · direct_evidence · 88–109 起；Get / SetStackSize / OnSave / OnLoad · 源文件身份为直接原版依据；既有报告记录了对照过程。本轮未重新解读源码，源文件不随包。
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · supplementary_interpretation · 11.2

### related

- [ARP-DST-001](../playbooks/ARP-DST-001.md#arp-dst-001)

<a id="fact-dst-006"></a>

## FACT-DST-006 — Mod RPC / Shard RPC 的 Lua 边界

类型：Klei Fact · Evidence：E3 · Confidence：Very High · Status：supported_by_klei · Version：0.1.1

Lua 包装校验已注册的 namespace/id，并把参数交给 TheNet；Shard 接收回调被放入 RPC_Shard_Queue。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Api Mechanism

Mod RPC / Shard RPC 的 Lua 边界

### Observed Behaviour

Lua 包装校验已注册的 namespace/id，并把参数交给 TheNet；Shard 接收回调被放入 RPC_Shard_Queue。

### Source File

- `vanilla-snapshot/scripts/networkclientrpc.lua`（original provenance；不作为包内链接）

### Relevant Function

SendModRPCToServer / SendModRPCToClient / SendModRPCToShard / HandleShardModRPC

### Source Locator

1881–1893；1943–1953

### Version Context

KLEI-LOCAL-20260928；原版发行 build 未记录；前轮对照本机 scripts.zip，非最新版本承诺。

### Implication

可把业务编码/路由与传输边界分开记录。

### Do Not Infer

不能从这些 Lua 包装推出可靠投递、恰好一次、业务 ACK、事务或自动补偿。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- networking
  - shard
- **evidence_modes**：- vanilla_source
  - static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server
  - client
  - shard

### Typed Relations

无 / 未建立

### sources

- KLEI-LOCAL-20260928（外部来源未随包） · direct_evidence · 1881–1893；1943–1953；SendModRPCToServer / SendModRPCToClient / SendModRPCToShard / HandleShardModRPC · 源文件身份为直接原版依据；既有报告记录了对照过程。本轮未重新解读源码，源文件不随包。
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · supplementary_interpretation · 4.1；6

### related

- [ARP-DST-001](../playbooks/ARP-DST-001.md#arp-dst-001)

<a id="fact-dst-007"></a>

## FACT-DST-007 — Prefab / Component / Class PostInit 时机

类型：Klei Fact · Evidence：E3 · Confidence：Very High · Status：supported_by_klei · Version：0.1.1

Prefab PostInit 在构造后应用；Component PostInit 在组件构造并挂入后应用；Class PostConstruct 包装构造器影响后续实例。不是注册时遍历回补旧实例。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Api Mechanism

Prefab / Component / Class PostInit 时机

### Observed Behaviour

Prefab PostInit 在构造后应用；Component PostInit 在组件构造并挂入后应用；Class PostConstruct 包装构造器影响后续实例。不是注册时遍历回补旧实例。

### Source File

- `vanilla-snapshot/scripts/modutil.lua`（original provenance；不作为包内链接）
- `vanilla-snapshot/scripts/entityscript.lua`（original provenance；不作为包内链接）
- `vanilla-snapshot/scripts/mainfunctions.lua`（original provenance；不作为包内链接）

### Relevant Function

AddPrefabPostInit / AddComponentPostInit / AddClassPostConstruct / AddComponent / SpawnPrefab

### Source Locator

modutil:153–175,566–599；entityscript:610–645；mainfunctions:347–391

### Version Context

KLEI-LOCAL-20260928；原版发行 build 未记录；前轮对照本机 scripts.zip，非最新版本承诺。

### Implication

需区分模块加载、注册回调、实体产生三个时点。

### Do Not Infer

不能推出回调自动只在 Server 运行、任意回调顺序稳定，或存在通用自动卸载接口。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- lifecycle
  - hooks
- **evidence_modes**：- vanilla_source
  - static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

无 / 未建立

### sources

- KLEI-LOCAL-20260928（外部来源未随包） · direct_evidence · modutil:153–175,566–599；entityscript:610–645；mainfunctions:347–391；AddPrefabPostInit / AddComponentPostInit / AddClassPostConstruct / AddComponent / SpawnPrefab · 源文件身份为直接原版依据；既有报告记录了对照过程。本轮未重新解读源码，源文件不随包。
- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · supplementary_interpretation · 7 Hook Mechanism Table；原版定位列表

### related

- [ARP-DST-001](../playbooks/ARP-DST-001.md#arp-dst-001)

<a id="fact-dst-008"></a>

## FACT-DST-008 — 实体删除与组件单独卸载不同

类型：Klei Fact · Evidence：E3 · Confidence：Very High · Status：supported_by_klei · Version：0.1.1

Entity Remove 清监听、world state watcher、pending tasks；RemoveComponent 先从 components 清键，再调用旧组件的 OnRemoveFromEntity。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Api Mechanism

实体删除与组件单独卸载不同

### Observed Behaviour

Entity Remove 清监听、world state watcher、pending tasks；RemoveComponent 先从 components 清键，再调用旧组件的 OnRemoveFromEntity。

### Source File

- `vanilla-snapshot/scripts/entityscript.lua`（original provenance；不作为包内链接）

### Relevant Function

Remove / RemoveComponent

### Source Locator

648 起；1705–1726

### Version Context

KLEI-LOCAL-20260928；原版发行 build 未记录；前轮对照本机 scripts.zip，非最新版本承诺。

### Implication

卸载回调应使用自身引用，不能假定 inst.components[name] 仍在；长命 Owner 的任务不会随短命业务对象自动取消。

### Do Not Infer

不能把完整世界销毁的清理外推为任意独立服务注销均安全。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- lifecycle
- **evidence_modes**：- vanilla_source
  - static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

无 / 未建立

### sources

- KLEI-LOCAL-20260928（外部来源未随包） · direct_evidence · 648 起；1705–1726；Remove / RemoveComponent · 源文件身份为直接原版依据；既有报告记录了对照过程。本轮未重新解读源码，源文件不随包。
- [REPORT-R4](<../review-support/reports/sorachestmanager_DeepDive_20260928.txt>) · supplementary_interpretation · 13 注销、重复注册与清理

### related

- [ARP-DST-001](../playbooks/ARP-DST-001.md#arp-dst-001)

<a id="fact-dst-009"></a>

## FACT-DST-009 — 原版制作 Host / Remote 汇合

类型：Klei Fact · Evidence：E3 · Confidence：Very High · Status：supported_by_klei · Version：0.1.1

有服务端 builder 的本地对象可直接调用；远程端经 PlayerController 和原版 RPC 到服务端 Builder，预测路径还涉及 BufferedAction。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Api Mechanism

原版制作 Host / Remote 汇合

### Observed Behaviour

有服务端 builder 的本地对象可直接调用；远程端经 PlayerController 和原版 RPC 到服务端 Builder，预测路径还涉及 BufferedAction。

### Source File

- `vanilla-snapshot/scripts/components/builder_replica.lua`（original provenance；不作为包内链接）
- `vanilla-snapshot/scripts/components/playercontroller.lua`（original provenance；不作为包内链接）
- `vanilla-snapshot/scripts/networkclientrpc.lua`（original provenance；不作为包内链接）

### Relevant Function

MakeRecipeFromMenu / RemoteMakeRecipeFromMenu / RPC.MakeRecipeFromMenu

### Source Locator

builder_replica:424；playercontroller:5709；networkclientrpc:937

### Version Context

KLEI-LOCAL-20260928；原版发行 build 未记录；前轮对照本机 scripts.zip，非最新版本承诺。

### Implication

有现成原版业务协议时，可以扩展它而不另造 Mod RPC。

### Do Not Infer

不能把该分支外推为所有 Host 业务都会绕开 RPC。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- networking
- **evidence_modes**：- vanilla_source
  - static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server
  - client

### Typed Relations

无 / 未建立

### sources

- KLEI-LOCAL-20260928（外部来源未随包） · direct_evidence · builder_replica:424；playercontroller:5709；networkclientrpc:937；MakeRecipeFromMenu / RemoteMakeRecipeFromMenu / RPC.MakeRecipeFromMenu · 源文件身份为直接原版依据；既有报告记录了对照过程。本轮未重新解读源码，源文件不随包。
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · supplementary_interpretation · 9

### related

- [ARP-DST-001](../playbooks/ARP-DST-001.md#arp-dst-001)

<a id="fact-dst-010"></a>

## FACT-DST-010 — 原版材料来源与堆叠移除

类型：Klei Fact · Evidence：E3 · Confidence：Very High · Status：supported_by_klei · Version：0.1.1

GetCraftingIngredient 先查合规打开容器，再主槽、overflow、active；RemoveItem 对部分堆叠请求可先走 Stackable:Get，再进行常规来源搜索。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Api Mechanism

原版材料来源与堆叠移除

### Observed Behaviour

GetCraftingIngredient 先查合规打开容器，再主槽、overflow、active；RemoveItem 对部分堆叠请求可先走 Stackable:Get，再进行常规来源搜索。

### Source File

- `vanilla-snapshot/scripts/components/inventory.lua`（original provenance；不作为包内链接）

### Relevant Function

GetCraftingIngredient / RemoveItem

### Source Locator

1697 起；1390 起

### Version Context

KLEI-LOCAL-20260928；原版发行 build 未记录；前轮对照本机 scripts.zip，非最新版本承诺。

### Implication

扩展来源时必须按实体身份去重，并审查原版与新来源的访问规则。

### Do Not Infer

不能推出 Inventory API 自动验证额外 Provider 的所有权或与它合并资源预算。

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- resources
- **evidence_modes**：- vanilla_source
  - static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server

### Typed Relations

无 / 未建立

### sources

- KLEI-LOCAL-20260928（外部来源未随包） · direct_evidence · 1697 起；1390 起；GetCraftingIngredient / RemoveItem · 源文件身份为直接原版依据；既有报告记录了对照过程。本轮未重新解读源码，源文件不随包。
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · supplementary_interpretation · 10–11

### related

- [ARP-DST-001](../playbooks/ARP-DST-001.md#arp-dst-001)
