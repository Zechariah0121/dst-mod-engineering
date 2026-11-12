# 少做重复工作，沿用已有状态与生命周期

先确定本次要减少的查询、任务或遍历，再保留原来的执行端、采样条件和副作用顺序。下面四个场景给出工程建议，所用接口已按 762172 / build 26474873 定点核对。收益只描述代码结构和调用数量，实际帧耗尚未测量。[性能验收](testing-release.md#架构简化与性能优化) · [直接实现与模块边界](complex-mod-architecture.md)

引用记录保留各自的来源范围与 `coding_status=hold` 等准入状态。空间查询两条记录的原证据限定于历史提交，本次另查 762172 源码中的 Lua 调用形态；原生排序与并列规则仍待对应证据。

## 同次刷新共享同一份查询结果

附近对象的数量提示与预览列表，若约定使用同一轮候选，可以共享查询。示例中的坐标、半径和标签不变，两次查询之间没有执行会改变世界状态的回调，`UpdateCount` 与 `UpdatePreview` 是现有显示函数。

原写法每次刷新查询两次。

```lua
local count = #TheSim:FindEntities(x, y, z, radius, must_tags, cant_tags)
local candidates = TheSim:FindEntities(x, y, z, radius, must_tags, cant_tags)
UpdateCount(count)
UpdatePreview(candidates)
```

同次刷新只查询一次。

```lua
local candidates = TheSim:FindEntities(x, y, z, radius, must_tags, cant_tags)
UpdateCount(#candidates)
UpdatePreview(candidates)
```

这样静态减少一次原生查询入口调用和一份返回列表。原有高度、半径、标签、可见性与业务谓词继续保持。原逻辑若在两次查询间执行工作、移除对象或发出可改变状态的事件，后一次查询就有重新采样的作用，应按实际时点保留。最近目标的选择也继续沿用原来的距离比较与并列规则。依据为 `SPATIAL-CODE-FILTER-CALLBACK`、`SPATIAL-CODE-NEAREST-ORDER`，当前调用形态另核于 `simutil.lua` 31–42 行。[空间查询边界](worldgen-spatial.md)

## 靠近设备只在状态转换时应用表现

自有设备若只要求“任一符合条件的玩家进入近圈时开启，全员离开远圈时关闭”，可以复用 PlayerProx 的 AnyPlayer 模式。

| 原流程 | 调整后流程 |
| --- | --- |
| 自写周期查询，再维护近/远状态，并反复调用同一表现设置 | PlayerProx 维护近/远状态，转换时调用设备已有的表现函数 |

以下用于尚未安装 PlayerProx 的自有设备 master 构造。`ApplyNear`、`ApplyFar` 只应用当前表现，`cfg.near/far/period/alive_mode` 沿用项目的距离、采样间隔与玩家资格规则。

```lua
local prox = inst:AddComponent("playerprox")
prox:SetDist(cfg.near, cfg.far)
prox:SetPlayerAliveMode(cfg.alive_mode)
prox:SetOnPlayerNear(ApplyNear)
prox:SetOnPlayerFar(ApplyFar)
ApplyFar(inst)
prox:Schedule(cfg.period)
prox:ForceUpdate()
```

默认 AnyPlayer 的近回调接收 `(inst, player)`，远回调接收 `inst`。先设置初始关闭表现，再 ForceUpdate，可让当前已有近玩家时立刻进入开启表现。原版 archive_chandelier 的 master 接线也把近/远回调直接连到设备的光照更新函数。组件负责自身查询任务的休眠、唤醒和移除，派生灯、音效或其他任务仍按该功能已有出口清理。依据为 `playerprox.lua` 44–60、127–222 行及 `archive_chandelier.lua` 380–408、541 行。

PlayerProx 继续周期检查玩家位置。这里减少自写任务管理、重复状态和反复应用表现的调用。额外阵营谓词、逐玩家效果或严格即时触发，应先确认其现有模式能否完整表达。采样间隔沿用既定值；需要降频时，明确可接受的响应窗口及短暂进出是否允许漏检。近远阈值的滞回也按原规则保留。PlayerProx 的查询次数与耗时变化需实测。[靠近设备的既有选择](combat-buffs-containers.md#附近玩家触发的悬浮)

## 装备回调启停已有耗能组件

若某件装备已经有 Fueled，额外常驻任务仅用来读取装备状态、保存上次状态并切换消费，可以把这部分接回物品已有的生命周期。

| 原流程 | 调整后流程 |
| --- | --- |
| 常驻任务 → 读取 IsEquipped → 对照上次状态 → 启停 Fueled | 原有 OnEquip → StartConsuming，原有 OnUnequip/对应模型出口 → StopConsuming |

黄色护符已经使用这条接线。StartConsuming 只在缺少消费任务时创建，StopConsuming 取消周期任务及待执行的首期更新。保留物品原来的 `period`、`rate`、倍率、首期扣量配置和耗尽处理，以及换装、属性、灯与模型回调。静态收益是移除额外状态检查任务及其上次装备状态字段，Fueled 活动期间的正常计时继续运行。依据为 `EXP-GEAR-001`。[装备耗能与补料](gear-fuel-repair.md)

回调会跟随实际装备时点执行。只有这个时点符合既定启停规则时才合并；若原先的采样延迟或跨卸装计时属于玩法，应继续维护该时序。给已存在的装备追加功能时，按真实接入入口初读当前装备状态，再接后续回调。已经完成这些接线的物品沿用现状即可。涉及执行中取消的合同继续见 `EXP-LIFE-006`。[任务归属](component-task-ownership.md)

## 重用组件已维护的成员计数

服务器巢穴统计若需要普通池总量，直接读取 ChildSpawner 已维护的数量。以下假设外部表始终由该组件登记和撤回。

原写法每次统计遍历普通外部表。

```lua
local outside_count = 0
for _ in pairs(population.childrenoutside) do
    outside_count = outside_count + 1
end
local total = population.childreninside + outside_count
```

同样的普通池总量可直接读取。

```lua
local total = population:NumChildren()
```

成员加入和撤回时，组件已有路径更新 `numchildrenoutside`，NumChildren 相加巢内数与该计数。每次读取省去一轮 O(n) 外部表遍历；成员变动时原组件维护计数的成本继续存在。需要有效外部孩子或自定义过滤时，继续用 `CountChildrenOutside(fn)`，因为该方法还会检查有效性与谓词。普通池总量、应急池和“附近有多少同类”各有实际消费者。依据为 `EXP-NEST-001/002`。[巢穴库存与所有权](nests-population.md)

跨 tick 缓存动态空间候选时，先找真实失效来源。实体移动、范围变化、新候选出现、移除和资格改变都可能使旧答案过期。IsValid 只检查当前引用的有效性。没有覆盖这些变化的现成登记或事件时，保留合适频率的空间采样。只用于一次调用的候选直接留在局部变量中；已有组件维护的成员状态直接读取，可避免另建一份缓存和失效协议。依据为 `RULE-WORLD-002` 与现有性能原则。[缓存与更新的验收条件](testing-release.md#架构简化与性能优化)

## 记录本次减少了什么

交付时说明实际删掉的查询、任务、循环或重复状态，以及对应输出、作用域和时点如何保持。行为检查覆盖本次涉及的采样、状态转换、退出或成员变动即可。确有运行热点时，再在可重复场景记录调用次数、遍历规模和耗时。
