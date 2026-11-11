# 农田与作物的接入选择

先按需要的玩法选择入口。给现有农田加水、做自动照料或改变一种收获规则，都可以沿现有调用点完成。完整农作物才需要阶段压力、巨型、种子、研究册与对应资产一起接线。

本篇依据 762172 / build 26474873 的静态 Lua，具体事实见[农作机制与来源](../knowledge/research/native-mechanisms/farming_crops-f18058848c00.json)。以下实现选择为工程建议，原版数值用于说明现有行为。

## 先选需要接入的部分

| 当前开发需求 | 可以从这里实现 |
|---|---|
| 给现有田格补水、加三类营养 | master 业务回调调用现有 farming_manager |
| 给现有作物自动照料 | 对目标 farmplanttendable 调 TendTo，沿作物阶段重新开放资格 |
| 种子入土长成一个自定义植物 | 种子 master 初始化配置 farmplantable.plant，目标 prefab 实现所需生长和采摘 |
| 完整参与原版水肥、邻居、季节压力和巨型收获 | 接农作物组件集合、定义数据及其阶段结算 |
| 固定时间长成、固定产物、采后再长的普通植物 | 自己的 prefab 配 Growable 与 Pickable，使用本地阶段与采摘回调 |

最后两种选择取决于玩法。只做生长和采摘时，一份阶段表与明确的采后入口通常足够。阶段设置、重新计时、睡眠和保存的已有合同继续查 EXP-GROW-001/002 与 [物品与普通植物](items-food-plants.md)，本轮补充农作的实际消费者。[EXP-FARM-002、003](../knowledge/research/native-mechanisms/farming_crops-f18058848c00.json)

## 加水和施肥写共享田格

世界 master 安装 farming_manager，地图尺寸事件后创建格数据。营养和水分由世界保存，同一田格内的多株作物共同影响它们。每株作物另外记录阶段内湿润/干燥时长，用于自己的干旱压力。

两个常用接口的坐标不同。

- `AddSoilMoistureAtPoint(x, y, z, delta)` 接世界点，要求中心格已有农田 overlay，正常返回 nil。原版水分受世界 wetness 下限和土壤上限约束。
- `AddTileNutrients(tx, ty, n1, n2, n3)` 接格坐标，各项增量后钳到 0～100，正常返回 true。该方法自身接受格数据写入，农田准入由调用者决定。

下面的原创示意用于已经进入 master 的效果回调。增量由项目需求传入。

```lua
local function AddFarmNutrientsAtPoint(x, y, z, n1, n2, n3)
    local map = TheWorld.Map
    if not map:IsFarmableSoilAtPoint(x, y, z) then
        return false
    end
    local tx, ty = map:GetTileCoordsAtPoint(x, y, z)
    return TheWorld.components.farming_manager:AddTileNutrients(
        tx, ty, n1, n2, n3
    )
end
```

普通肥料物品可以复用 `MakeDeployableFertilizerPristine` 的公共放置查询和 master 侧的 `MakeDeployableFertilizer`。原版消费者把世界点转为格坐标、加营养，然后通过 `Fertilizer:OnApplied` 消耗次数或物品。法术若只需要改变田格，可在自身已有消费合同内直接调用管理器。

原版 WateryProtection 对半径内实体施加保护，同时只给中心格加一次土壤水分。若需求是多格灌溉，按受影响田格调用加水入口即可。按植株逐个写入同一格，会让该格收到多份增量。[EXP-FARM-001，FARM-S01～S08、S24～S27](../knowledge/research/native-mechanisms/farming_crops-f18058848c00.json)

`CycleNutrientsAtPoint(..., consume, restore, test_only)` 是作物营养周转入口。返回 true 表示缺少足量营养或没有农田 overlay。真实执行即使营养不足，也会扣掉可用部分并按已消费总量恢复指定类型。`test_only=true` 用于检查需求，实际阶段转换才应用消费。仅需施肥时，直接使用加营养接口更容易表达目的。[EXP-FARM-001，FARM-S07、S14、S32](../knowledge/research/native-mechanisms/farming_crops-f18058848c00.json)

## 自定义农作物需要接好每株用水历史

farmsoildrinker 的两个回调分别提供有符号用水率和湿润状态变化处理。原版作物的用水率取自 plant_def，生长暂停时返回 0。湿润状态过零时，作物回调调用 `UpdateMoistureTime(cur, prev)`，把刚结束的一段时间记到旧状态。阶段结束再计算湿润占比并 Reset，开始下一阶段统计。

因此，给自定义植物安装组件后，还要为其实际需求绑定 `getdrinkratefn` 和 `onsoilmoisturestatechangefn`。只需要一次浇水改变生长速度的普通植物，可以在自己的业务入口完成该变化。固定位置作物可复用原版登记路径，涉及移动时要核对格索引的归属，因为登记与注销都按当时位置定位。[EXP-FARM-001，FARM-S04、S05、S12～S14、S22、S39](../knowledge/research/native-mechanisms/farming_crops-f18058848c00.json)

## 照料在当前阶段生效，产物有自己的读取时点

普通作物进入 sprout、small、med 和 full 前执行压力检查点。它重新检查邻居、拥挤、季节、水分和营养，照料则通过动作回调改变当前阶段 happiness。检查点累计受压项后，把各项标记恢复成下一阶段的初始受压状态。

自动照料现有作物时，调用其 `farmplanttendable:TendTo(doer)`。原版成功回调清除 happiness，组件随后关闭本阶段照料资格，下一生长阶段再开放。若只是想按当前规则照料，直接使用该入口即可。[EXP-FARM-002，FARM-S13～S19、S28](../knowledge/research/native-mechanisms/farming_crops-f18058848c00.json)

产量相关改动需要区分三个时点。

1. 进入 full 前完成最后检查点，计算最终压力，并结合 `force_oversized`、`no_oversized` 写巨型标记。
2. 成熟阶段开启 Pickable。实际生成采集产物时，LootDropper 的 `lootsetupfn` 再读取巨型、腐烂和最终压力，配置产品与种子。
3. Pickable 先生成这次产物，再调用 `onpickedfn`，最后按 `remove_when_picked` 移除作物。

想改变巨型资格，应在成熟决策之前落实条件。想调整现有作物的收获规则，沿最终 `lootsetupfn` 的数据选择处理。采后回调适合采后效果。普通阶段链中，成熟后补水或照料不会重新累计前面各阶段的压力。原版腐烂后还有压力重置、普通作物回生及巨型停止生长的分支，只有需求涉及它们时再接入。[EXP-FARM-002，FARM-S15、S19～S21、S34～S36](../knowledge/research/native-mechanisms/farming_crops-f18058848c00.json)

## 种子入土可接到自己的小型植物 prefab

自定义种子的 master 初始化可以先明确目标。

```lua
inst:AddComponent("farmplantable")
inst.components.farmplantable.plant = "my_crop"
```

这是入口示意，目标 prefab 的网络、资产和导出仍由项目实现。标准 PLANTSOIL 动作先从背包取出本次种子对象，再调用 Plant。正常失败会返还该对象。直接从自定义代码调用组件时，本次要消费的实体和数量由该调用方准备。

`Plant` 把带 soil 标签的土堆替换成目标植物，发 `on_planted`，携带 `doer=planter`、`seed=self.inst` 与 `in_soil=true`，然后消费传入种子实体。该实现先移除土堆再创建植物，因此应配置已注册、可创建的目标。若项目明确要求创建失败时保留土堆，可以在自己的窄入口先确认新实例创建成功，再进行位置和材料交接。后续回调产生的副作用仍沿该项目业务约定处理。[EXP-FARM-003，FARM-S29～S31、S38](../knowledge/research/native-mechanisms/farming_crops-f18058848c00.json)

原版完整作物的 `MakePlant` 是 `farm_plants.lua` 文件局部工厂，模块遍历当时的 PLANT_DEFS 返回 prefab。定义表又由同品种实例直接引用。新增一张定义后，仍需确保目标 prefab 真正进入创建与资产接线；只给一株改变水分需求时，明确修改的数据属于该株还是共享品种定义。

若目标只是固定阶段、一个成熟动画和固定采收，自己的小 prefab 可以只配置 Growable 的阶段时间、阶段状态函数和 Pickable。需要反复收获时，在本功能采后入口处理阶段与下一轮计时。需要完整农作互动时，再接水肥历史、压力检查点、巨型和研究数据。原版实现提供了这些功能之间的真实合同，也允许项目选择更小的组合。[EXP-FARM-003，FARM-S20、S22、S23、S33](../knowledge/research/native-mechanisms/farming_crops-f18058848c00.json)

## 验证所改的实际路径

- 水肥改动关注同格多株、不同格和不足时的真实营养变化，改保存路径时再检查重启结果。
- 压力或产量改动观察一次完整的阶段结算、成熟和收获，确认修改落在对应读取节点。
- 新种子观察堆叠数量、土堆替换和目标创建，涉及放置与动作显示时使用真实客户端核对。

尚未运行游戏，本篇的工程选择和具名边界仍需在目标实现中验证。
