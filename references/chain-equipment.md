# 装备效果完整链 · Molehat 夜视

本篇供 Skill 按“装备效果、耗能、卸下、恢复”任务定向读取。结论限定 762172 冻结归档中的 `molehat`、普通 HEAD 装备与正燃料保存记录。新增研究 `EXP-CHAIN-GEAR-001` 保持 `research/restricted/hold`，仅供显式 Reviewer 审阅。研究登记为 `runtime_verified=false`，静态、Lua替身与自写示例的有限专服验证分别列于末节。

## 先读与复用

1. 先读装备耗能与修理指南，再从 CATALOG 的 file/pointer 读 `EXP-GEAR-001`，核对 Fueled 单位、首期消费、补料拒绝、材料消费与保存范围。[装备耗能与修理](gear-fuel-repair.md)
2. 读 `EXP-ITEM-004`，核对装备输入、服务器门禁、旧装备去向、回调早于最终写槽、卸下先回调再清槽，以及客户端预测请求边界。
3. 读 `EXP-CHAIN-GEAR-001` 的 Scope、claims 与 mechanism_steps，沿本篇下表追到实际夜视消费者。[Molehat 机制研究](../knowledge/research/native-mechanisms/stage3_equipment-1e3795ce754f.json)
4. 需要清理责任时按条件读 `EXP-LIFE-001`、`EXP-LIFE-006`、`EXP-LIFE-008`，核对监听身份、任务与实体删除阶段。组件卸载同时核对资源归属。[组件与任务归属](component-task-ownership.md)
5. 防御需求继续读 `EXP-COMBAT-001/002` 及战斗指南。`EXP-GEAR-002` 的次数维修属于相邻材料。[战斗与 Buff](combat-buffs-containers.md)

共复用 5 条现有机制登记，新增 1 条具名链、2 个 PlayerVision API 合同。上述相邻条目只记录已审阅范围，不增加本链覆盖数。研究 ID 用于定位，项目实施仍需对自己的版本、入口及政策逐项核对。

## 有限范围与状态所有者

| 对象 | 持有的状态与资源 | 消费者和出口 |
|---|---|---|
| 帽子实体 | 双端预置 `nightvision` 标签，master 的 Equippable 与 Fueled 数值/句柄 | 玩家装备成员决定标签是否生效，装备回调启耗，卸下或模型回调停耗 |
| owner Inventory | 权威 `equipslots` 与物品归属 | 槽提交后发 `equip`，清槽后发 `unequip` |
| inventory classified | 装备 `net_entity` 与客户端预览 | replica 标签查询、装备 dirty 到本地玩家事件 |
| 玩家 PlayerVision | 派生 `nightvision`、独立 `forcenightvision`、当前色表 | 初始化快照及装备变化重算，`HasNightVision` 汇合两种夜视状态 |
| 本地世界表现组件 | 激活玩家监听、环境色和色表混合 | ambientlighting 到 TheSim，colourcube 到 PostProcessor |

视野效果的存在由当前装备表中的标签决定。Fueled 持有时间消费，标签效果没有另设轮询任务或保存布尔。多个带标签的装备会由当前表重新查询，强制夜视来源继续由 PlayerVision 自身入口管理。

## 完整执行链

| 阶段 | 本帽的实际接线 | 可复核位置 |
|---|---|---|
| 输入与拒绝 | 普通 EQUIP/客户端库存入口进入服务器 Inventory，限制与旧槽处理复用 `EXP-ITEM-004`。拒绝停在原入口，回调阶段尚未进入 | 既有 `EXP-ITEM-004` 完整原子 |
| 构造与端别 | `simple(mole_custom_init)` 在 SetPristine 前加 nightvision，master 安装 HEAD Equippable；本帽 master 再配 WORMLIGHT Fueled | `hats.lua` 188–235、1817–1839 |
| 成功安装 | `mole_onequip` 调通用帽回调，开始燃料消费并播放启动声。Inventory 随后写槽、发 equip | `hats.lua` 30–114、1797–1805；`inventory.lua` 1364–1388 |
| 装备复制 | master replica 监听 equip/unequip，写 classified 装备 net_entity。客户端 dirty 安排 static 回调，发布玩家装备事件，并安排刷新 | `inventory_replica.lua` 9–34；`inventory_classified.lua` 41–51、499–510、565–588、1573–1602 |
| 真实效果消费 | PlayerVision 初始化登记事件并立即读装备快照，随后按 replica:EquipHasTag 重算 nightvision，更新色表和事件 | `playervision.lua` 9–144、175–220；`inventory_replica.lua` 248–258 |
| 画面提交 | 激活玩家时表现组件读取已有快照并监听变化。色表最终到 PostProcessor，环境视觉色最终到 TheSim:SetVisualAmbientColour | `colourcube.lua` 129–211、281–368、450–477；`ambientlighting.lua` 115–194、226–246 |
| 持续耗能 | master Fueled 按 dt × rate × 来源倍率扣燃料。首期配置沿本帽实际设置，任务与取消合同复用 `EXP-GEAR-001` | `hats.lua` 1831–1836；`fueled.lua` 265–349 |
| 卸下与替换 | 帽回调先停止消费，Inventory 清槽后发 unequip。PlayerVision 重新检查剩余标签和强制状态 | `hats.lua` 77–114、1802–1805；`inventory.lua` 1219–1248 |
| 耗尽或外部移除 | `mole_perish` 播关闭声并 Remove。InventoryItem 移除钩子到 Inventory:RemoveItem，装备成员强制 Unequip 后清槽，效果依事件重算 | `hats.lua` 1807–1815；`inventoryitem.lua` 485–499；`inventory.lua` 1390–1432 |
| 补料与恢复 | 尚存实体使用 WORMLIGHT 补料。Fuel 保存非满数值，普通 Inventory 保存装备记录并在加载重建物品后重新 Equip，正燃料装备重建消费，视野从当前成员派生 | `fueled.lua` 133–143、153–230；`inventory.lua` 192–229、293–325 |

以上路径中的 `hats.lua` 是 `scripts/prefabs/hats.lua`，组件文件位于 `scripts/components/`，`inventory_classified.lua` 位于 `scripts/prefabs/`。32 个精确范围的文件 SHA256、范围 SHA256 与符号见 `EXP-CHAIN-GEAR-001` 所在登记文档的 `source_references`。范围算法采用 UTF-8 解码后的 splitlines，LF 连接且没有尾换行。[来源与范围哈希](../knowledge/research/native-mechanisms/stage3_equipment-1e3795ce754f.json)

普通换装与卸下承担退出。输入拒绝、动作中断是否到达 Equip 继续按实际输入链及 `EXP-ITEM-004` 观察。本帽没有额外施法事务或“取消后退款”状态。回调异常仍受已有阶段合同约束，不能从这条静态链推导整链回滚。

## 恢复边界

- 正常耗尽会删除帽子，燃料恢复针对耗尽前仍存在的物品。
- Fueled 的 OnLoad 初始化不重放 depleted。外部构造 `fuel=0` 的存活帽子后重新装备，可出现消费停止而装备标签仍生效的状态。Lua 替身已验证这条局部路径。本篇将正常保存闭包限定为正燃料记录，项目需自行决定异常记录的处理政策。
- 耗尽函数和卸下函数各有关闭声入口，声音次数需按实际调用链观察。
- 普通 Inventory OnSave/OnLoad 已追踪。玩家 session 外部读写、死亡掉落模式、重连与跨分片恢复继续待验。
- 色表选择包含 ghostvision、overridecctable、nightvision 与 nightmarevision 的优先级。全组合、真实远端复制纠正、原生渲染与客户端画面继续待验。

## 独立最小示例

下列代码为本专题独立编写的 prefab 夹具。演示政策采用容量 60、rate 默认 1、WORMLIGHT 补料、耗尽删除，沿用 Fueled 数值保存。示例省略原版的首期额外扣量，数值、启动成本和删除政策均由实际 Mod 确认。源码研究保持 HOLD，示例依据本次对冻结 ZIP 的独立核对编写。

在已存在的 Mod 中将代码放入 `scripts/prefabs/stage3_nightgear_fixture.lua`，并在 `modmain.lua` 的既有 `PrefabFiles` 列表加入 `"stage3_nightgear_fixture"`。测试入口为隔离世界服务器生成该 prefab 后，使用普通库存装备和 WORMLIGHT 材料补料。示例有落地动画与库存图标，穿戴外观、配方和台词由集成项目接入。已完成的有限专服检查见末节，客户端画面仍待验。

下列完整代码与工作区维护用 `example.lua` 逐字匹配，其 UTF-8 文件 SHA256 为 `3d491ff3a0876ea6c25ac042245306706433d43909ab38bd5aacde72a868dd20`，可直接从本篇提取。

```lua
-- Independent fixture, source-verified against 762172.
-- Demonstration policy: 60 fuel units, rate 1, WORMLIGHT refuel,
-- depletion removes the item. Normal saved items have positive fuel.
-- Hat rendering, recipes and strings belong to the integrating project.

local assets = {
    Asset("ANIM", "anim/hat_mole.zip"),
}

local function OnEquip(inst, owner)
    inst.components.fueled:StartConsuming()
end

local function OnUnequip(inst, owner)
    inst.components.fueled:StopConsuming()
end

local function OnEquipToModel(inst, owner)
    inst.components.fueled:StopConsuming()
end

local function OnDepleted(inst)
    inst:Remove()
end

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    MakeInventoryPhysics(inst)
    inst.AnimState:SetBank("molehat")
    inst.AnimState:SetBuild("hat_mole")
    inst.AnimState:PlayAnimation("anim")
    inst:AddTag("nightvision")
    inst.entity:SetPristine()

    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem:ChangeImageName("molehat")
    inst:AddComponent("equippable")
    inst.components.equippable.equipslot = EQUIPSLOTS.HEAD
    inst.components.equippable:SetOnEquip(OnEquip)
    inst.components.equippable:SetOnUnequip(OnUnequip)
    inst.components.equippable:SetOnEquipToModel(OnEquipToModel)
    inst:AddComponent("fueled")
    inst.components.fueled.fueltype = FUELTYPE.WORMLIGHT
    inst.components.fueled:InitializeFuelLevel(60)
    inst.components.fueled.accepting = true
    inst.components.fueled:SetDepletedFn(OnDepleted)
    return inst
end

return Prefab("stage3_nightgear_fixture", fn, assets)
```

## 验证与待验

工作区维护证据 `source-audit.json`、`check.py` 与 `checks.json` 记录来源核对、检查命令及断言。检查涵盖机制 schema、归档 SHA、全部文件与范围 SHA、Lua 5.1 编译和指南代码一致性，并在内存中加载冻结归档的实际 Fueled 与 PlayerVision，使用自有 Entity、Inventory 成员、任务、事件及网络/动画接口替身验证 23 条断言。

维护者可在专题目录运行 `python -B -X utf8 check.py`，复核依赖工作区冻结 ZIP 与已有的 `lupa.lua51`。下载技能已包含本篇完整示例及登记研究中的来源哈希。

替身保存检查是 Fueled 的内存表恢复加显式模拟重新装备。另以本篇原样prefab在独立单分片专服验证实际库存装备、周期耗能、卸装取消与停耗稳定、耗尽删除、装备成员与派生夜视清理，以及独立强制夜视来源保留。同一隔离存档重启恢复燃料值30且未装备时不消费；最终两次进程退出码均为0，临时Mod已清理。早期一次运行虽通过行为断言，却发生原生文件写线程退出断言，未计为正常退出；最终运行采用测试脚手架保存回调后等待3秒再关闭。验证概况见[本轮说明](../docs/phase15-unified-chains.md)。

角色为合成服务器wilson，未运行真实客户端、原生色表/画面/声音或远端复制断言。真实玩家重连、死亡模式、session、跨分片及第三方 Mod 组合均待验，研究登记继续为 `runtime_verified=false`。
