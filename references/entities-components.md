# 实体、Prefab 与组件

适用于新增物品/生物骨架、自定义组件、生命周期及存档排错。本文对照 2026-09-27 核验环境的原版脚本；网络协议和资源编译按入口中的对应专题展开，源码基线见 [environment-tools.md](environment-tools.md)。

## 区分文件、定义与实例

`Prefab(name, fn, assets, deps)` 是注册信息，`fn()` 创建的是 EntityScript 实例，通常变量名为 `inst`。一个文件可返回多个 Prefab；临时 UI 或本地实体也可通过 `CreateEntity` 创建，不必拥有可持久化 Prefab。

`PrefabFiles = { "my_mod_items" }` 对应 `scripts/prefabs/my_mod_items.lua`。该文件可以返回 `Prefab("my_mod_item_a", ...)`、`Prefab("my_mod_item_b", ...)`。文件名和注册名没有“三者必须相同”的约束；错误日志 `Error loading file prefabs/...` 首先检查文件路径、大小写、语法及加载链。

`assets` 是这个定义依赖的资源；`deps` 是它依赖的 Prefab 名称列表。明确声明自己的 `local prefabs = {...}`，没有依赖就省略或传 nil。游戏为了兼容错误旧模组而保留的全局 `prefabs = nil` 不是可复用依赖表。

模组公共/前端资产和 Prefab 私有资产可分别放顶层 `Assets` 与本地 `assets`，不必把所有资源重复塞进 modmain。检查被依赖的动态生成对象和资源实际会被加载，不能推论“原版 prefab 总能随时生成，所以无需检查依赖”。

## 网络实体的公共区与服务端区

以当前原版同类实体为骨架：常见网络物品先添加引擎对象、公共动画与动作所需标签、netvar、两端组件，然后 `SetPristine()`，客机返回后再加权威玩法组件。**不是所有 `AddComponent` 都属于服务端**；`floater`、`aoetargeting` 等有公共初始化需求。

以下只展示普通可拾取物的结构，使用原版长矛资源；它尚未添加武器、装备、配方与字符串功能：

```lua
local assets = {
    Asset("ANIM", "anim/spear.zip"),
    Asset("ANIM", "anim/swap_spear.zip"),
}

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    MakeInventoryPhysics(inst)
    inst.AnimState:SetBank("spear")
    inst.AnimState:SetBuild("swap_spear")
    inst.AnimState:PlayAnimation("idle")
    MakeInventoryFloatable(inst, "med", 0.05, {1.1, 0.5, 1.1}, true, -9)

    inst.entity:SetPristine()
    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.imagename = "spear"
    return inst
end

return Prefab("my_mod_example_item", fn, assets)
```

纯本地 FX、服务端控制实体、classified 子实体有各自的生命周期和网络策略，不强塞这一模板。`Transform`、`AnimState`、`Light`、`SoundEmitter` 是 `entity:Add...` 创建的引擎对象；它们与 `inst:AddComponent("name")` 加载的 Lua 组件不是同一层。没有原版 `components/light.lua`，不能用 `AddComponent("light")` 修复灯光。

客户端需要的函数/初始 netvar 必须能在客户端创建阶段获得；“写在 SetPristine 之前”不是同步所有 Lua 字段或所有渲染调用的魔法。动态视觉由网络状态驱动客户端回调；具体引擎方法是否同步要查同类原版使用并实测。

## 添加组件与 API 审核

`inst:AddComponent("my_mod_counter")` 会 `require("components/my_mod_counter")` 并实例化。返回 Class 即可，不必把组件加到 PrefabFiles。组件构造器执行时 `self.inst.components.my_mod_counter` 还未写入，且其他依赖组件不一定已添加；使用 `self` 或在明确的初始化阶段连接依赖。

修改前分别查 `components/x.lua` 与 `components/x_replica.lua`。当前例子：`hunger.current` 是服务端字段；`hunger_replica:GetCurrent()` 是另一接口；`stackable.maxsize` 是属性代理；`equippable` 提供 `SetOnEquip` / `SetOnUnequip`，不能凭对称猜出带 `Fn` 的版本。对动态别名要继续跟踪赋值语句。

新组件的最小持久化片段：

```lua
local Counter = Class(function(self, inst)
    self.inst = inst
    self.value = 0
end)

function Counter:OnSave()
    return { value = self.value }
end

function Counter:OnLoad(data)
    if data ~= nil and type(data.value) == "number" then
        self.value = math.max(0, data.value)
    end
end

return Counter
```

实际项目补充范围、旧存档版本与副作用恢复规则；这里的非负约束仅是示例，不是所有资源数值的默认设计。

## 事件、定时任务与移除

先找事件生产端的 `PushEvent`。回调收到的是**事件源实体与原样 data**，data 可以是 nil、标量、实体或表。

| 生产代码 | 回调第二参 |
|---|---|
| `inventoryitem` 的 `PushEvent("onputininventory", owner)` | owner 实体 |
| `equippable` 的 `PushEvent("equipped", { owner = owner })` | 表，访问 `data.owner` |
| `equippable` 的 `PushEvent("unequipped", { owner = owner })` | 仍含 owner；不要误称所有卸下回调都取不到 owner |
| `TheWorld:PushEvent("playeractivated", player)` | player 实体 |

`listener:ListenForEvent(event, fn, source)` 的 source 默认 listener。移除须用相同 `event, fn, source`；临时效果结束时不要 `RemoveAllEventCallbacks()` 清掉其他系统的监听。`WatchWorldState` 也要保留原回调引用并配对清理。

`DoTaskInTime` 和 `DoPeriodicTask` 返回可取消的任务。刷新效果先取消旧任务；所有结束路径都清自己的句柄、外部事件、速度/伤害 modifier、FX 引用。移除 Lua 组件时用 `OnRemoveFromEntity`，实体移除通知有 `OnRemoveEntity`；若二者都需要清理，写一个可重复调用的清理函数再挂到两条路径。跨实体任务不能只依赖施法者移除会自动处理。

实体标签、SG 状态标签、烹饪食材 tags 是不同机制。`CLASSIFIED` 不是“完全不联网”标签：原版 `player_classified` 本身有 Network，配合目标客户端、父实体和专用数据同步。`INLIMBO` 表示从正常场景交互中隐藏/移出，不应只解释成“物品已进背包”。取用现有 tag 前查所有关键消费者；自定义 tag 使用项目命名空间。

## 存档时序与派生数值

- 组件 `OnSave()` **返回** `data, refs`；实体 `inst.OnSave(inst, data)` **填写传入的聚合 data** 并可返回 refs。两种签名不能混用。
- `SetPersistData` 顺序是实体 `OnPreLoad` → 用 `pairs` 加载各组件 → 实体 `OnLoad`。组件之间没有可依赖的固定顺序；跨组件恢复应有明确协调阶段。
- 保存 GUID 引用需要 `refs` 并在 `LoadPostPass` / `OnLoadPostPass` 用 `newents` 恢复；普通 Lua 实体引用不能直接序列化。
- 教程等级示例每次用“当前最大血量 × 等级倍率”，重复升级和读档会累计膨胀。保存独立等级与基准，用可重复计算的派生公式；上限、死亡重置/保留由设计确定。
- `health:SetMaxHealth` 会同时改变当前血量。动态换上限要明确保持绝对值还是比例；死亡状态不可借恢复比例制造复活。原版 health 默认保存当前值，只有 `save_maxhealth` 才保存 max；形态跨档需恢复依据，不能只在 OnLoad 再变身。

## 原版检索入口与验收

- `mainfunctions.lua:LoadPrefabFile`、`mods.lua:RegisterPrefabs`、`prefabs/axe.lua`：文件加载与多个 Prefab 返回值。
- `entityscript.lua:LoadComponent`、`AddComponent`、`RemoveComponent`、`Remove`、`GetPersistData`、`SetPersistData`、`LoadPostPass`：组件生命周期与存档实际调用者。
- `entityscript.lua:ListenForEvent` / `PushEvent_Internal` / `RemoveEventCallback`：事件源和清理契约。
- `prefabs/spear.lua`、`standardcomponents.lua:MakeInventoryFloatable`、`prefabs/player_classified.lua`：公共区及网络实体例外。
- 验收首次生成、物品栏/地面切换、重复添加/移除效果、实体移除、保存重启、旧存档缺字段。组件恢复测试应覆盖不同初始化顺序；真正的网络表现需要客机验收。
