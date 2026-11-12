# 巢穴种群、回巢与应急放出

来源与 API 合同：[机制研究](../knowledge/research/native-mechanisms/nests_and_child_population-6cf14996d5ae.json)。

`EXP-NEST-001` 补普通库存与放出，`EXP-NEST-002` 补成员资格和入巢终态，`EXP-NEST-003` 补应急预算。来源为 762172 / build 26474873 的静态 Lua，尚未运行游戏。已有 [Brain、SG 与 GOHOME 接线](creature-ai-practical.md)和[保存与引用恢复](save-recovery-architecture.md)继续复用其各自范围。

## 固定种群可以直接使用 ChildSpawner

自有巢穴在 master 构造中建立组件，孩子 prefab 提供自身的移动、Brain 和 SG。下面选择初始满库存、普通固定物种和组件内置时钟。`cfg` 与可选生成回调由具体玩法提供。

```lua
local population = inst:AddComponent("childspawner")
population.childname = cfg.child_prefab
population:SetMaxChildren(cfg.capacity)
population:SetSpawnPeriod(cfg.release_period, cfg.release_variance)
population:SetRegenPeriod(cfg.regen_period, cfg.regen_variance)
population:SetSpawnedFn(OnChildSpawned)
population:StartSpawning()
```

高脚鸟巢使用了这一类内置时钟接线。蜂巢、蜂箱则安装原版 WorldSettings 的两个时钟适配。修改现有巢穴时保留它已有的时钟与启停入口。只改子代类型、容量或补充速度时，直接在对应配置位置调整即可。来源 `NEST-S20`、`NEST-S24`、`NEST-S27`、`NEST-S38`、`NEST-S39`。

普通总量是巢内数量加外部登记数量。`SetMaxChildren(n)` 会立即把巢内库存重算为容量减当前有效外部数量。它适合构造或确实要重算库存的升级。补充开关默认开启，`DoRegen` 在总量未满时补一个巢内名额。放出开关则由 `StartSpawning/StopSpawning` 管理，停止周期放出后仍可补充。需要停止补充时使用 `StopRegen`。来源 `NEST-S02` 至 `NEST-S07`。

内置时钟用随机 5 到 10 秒的更新步长检查倒计时。`StartSpawning` 把放出倒计时设为 0，实际生成在后续更新进行。`LongUpdate(dt)` 只推进一次更新，所查方法每次最多补各池一个、普通放出一个。需要不同的离线种群政策时，再按玩法选择，原版这一调用本身没有逐周期追赶。来源 `NEST-S04`、`NEST-S05`、`NEST-S19`。

`SpawnChild(target, prefab, radius)` 可用于明确的手工放出，返回本次新实体或 nil。它检查当前库存、落点、巢是否有效/存活，以及醒着或允许离屏等条件。周期放出在睡眠时可排队等待唤醒。普通 `spawning` 开关控制调度，手工生成的资格由 `CanSpawn` 决定。来源 `NEST-S11` 至 `NEST-S13`、`NEST-S16`。

### 额外补给按实际空位增加

`AddChildrenInside(count)` 只限制巢内数量的上界。若玩法要求补给后的总量服从容量，可按实际空位限制本次增加。下面的 `granted_children` 是本次已决定的补给数量。

```lua
local room = population.maxchildren - population:NumChildren()
local count = math.min(granted_children, room)
if count > 0 then
    population:AddChildrenInside(count)
end
```

`onoccupied` 在旧巢内数量为 0 时先执行，随后才加量。`onaddchild(nest, count)` 收到请求数量，发生在加量及钳制之后。业务若要展示实际新增量，可读取调用前后的数量差。来源 `NEST-S19`。

## home、成员资格与回巢分别接线

普通 `SpawnChild` 已负责 TakeOwnership，接回 home、可选家位置记忆和退出监听。`onspawned(nest, child)` 此时发生在这些接线之前，需要巢信息时直接使用第一个参数。`ontakeownership(nest, child)` 发生在 home 和监听接好之后，普通外部成员表尚待加入。来源 `NEST-S10`、`NEST-S11`、`NEST-S13`。

单独 `homeseeker:SetHome` 建立家引用。ChildSpawner 的成员表决定是否受理入巢，直接接管已有生物时还要处理旧巢登记和本次容量。`TakeOwnership` 会增加外部成员，巢内库存由调用方的实际操作决定。正常生成与读档接回已经调用过它时，继续使用所得关系即可。来源 `NEST-S01`、`NEST-S10`、`NEST-S36`，以及已有 `EXP-AI-009`。

蜜蜂的实际链是 BeeBrain 选择回巢分支，调用模块导出的 `beecommon.GoHomeAction`，经 DoAction、GOHOME 和 SGbee 的 action 状态执行，再进入 ChildSpawner。该动作生成函数检查家有效、有 childspawner 且未燃烧。新生物按自己的 Brain 优先级选回巢条件，并安装对应 SG 动作入口。来源 `NEST-S28` 至 `NEST-S33`、`NEST-S40`。

入巢成功的先后如下。

1. 巢收到 `childgoinghome`，孩子收到 `goinghome`，随后执行 `ongohome(nest, child)`。
2. 撤掉外部成员并移除孩子实体。
3. 对应普通或应急巢内数量加一。

蜂箱在第一步读取蜜蜂的授粉进度，满足条件就增加蜂蜜。需要结算携带信息时，这个阶段仍能访问本次孩子。数量返还由组件完成，反馈回调处理自己的业务效果即可。来源 `NEST-S15`、`NEST-S19`、`NEST-S26`、`NEST-S27`。

后续放出会创建新的实体。普通计数库存适合可互换的生物。需要保持某个个体的生命、装备或专有进度时，先选择符合该身份寿命的收纳与保存合同。原版可选异种库存只额外记录物种数量。来源 `NEST-S11`、`NEST-S15`。

### 捕获与家退出

`OnChildKilled` 同时处理死亡、移除、捕获和 `detachchild`。捕网完成时，蜜蜂先发 detachchild，再把同一实体交给操作者库存，因此这个处理器也用于仍存活孩子的脱离。它撤外部登记，之后补充机制按总数缺口工作。来源 `NEST-S01`、`NEST-S17`、`NEST-S34`、`NEST-S35`。

单独移除 ChildSpawner 会撤其监听并取消保存于 `self.task` 的周期任务，孩子实体和它们的 home 引用还有各自生命周期。整个家被移除时，HomeSeeker 的家移除监听再清关系。需要运行中撤组件并保留巢实体的功能，按自己的退出政策处理剩余孩子，并核对唤醒时已排队的零延迟工作。来源 `NEST-S03`、`NEST-S12`、`NEST-S23`、`NEST-S36`。

## 应急防御使用独立库存

原版蜂巢给普通池与应急池分别配置数量、每玩家额度和检测半径，受击时调用 `ReleaseAllChildren(attacker, "killerbee")`。这会先尝试普通池，再重算附近玩家预算并尝试应急池，成功结果以数组返回。已经在外面的成员不在这个返回数组中，本方法也没有统一改变它们的目标。来源 `NEST-S18`、`NEST-S23` 至 `NEST-S25`。

只需尝试一个应急孩子时可用 `TrySpawnEmergencyChild(target)`，它先更新预算。应急提交量按 `maxemergencychildren - emergencychildreninside` 计算，只有严格低于本次玩家预算才继续。死亡减少外部数量，补充回巢内名额后才释放这一提交额度，因此可分别控制首次应对规模和持续补充速度。来源 `NEST-S04`、`NEST-S13`、`NEST-S14`、`NEST-S16`、`NEST-S17`。

普通周期暂停、手工防御可用性和补充停止是不同政策。`CanEmergencySpawn` 检查 `canemergencyspawn` 及自身库存/预算等条件。普通 `canspawnfn` 和 `spawning` 的值在这条检查中没有承担门禁。需求简单的巢穴可以只配置普通池。来源 `NEST-S06`、`NEST-S16`、`NEST-S24`。

## 保存沿用既有组件合同

外部孩子按 GUID 和 refs 保存，巢内保存数量，postpass 接回外部实体的 home 和监听，完整阶段复用 `EXP-SAVE-002`。回巢后的旧孩子已经移除，额外保存其表现对象、任务或闭包无法由这条计数合同自动恢复。来源 `NEST-S08`、`NEST-S10`，以及[保存与引用恢复](save-recovery-architecture.md)。

当前 OnLoad 用 `saved_value or current_value` 恢复 spawning、regening 等标志。若某个自有可保存开关要求已存 false 覆盖构造 true，应在该功能真实的加载入口明确应用这个值。普通固定政策按当前场景重新启停即可，是否持久化开关由需求决定。来源 `NEST-S09`。

实际接入后核对总数、生成返回、回巢一次返还、捕获后的外部撤回和所选应急预算。改变保存政策或运行中拆组件时，再覆盖对应恢复/退出路径。本轮只完成静态来源及合同核对，实际落点、动作抵达和客户端表现待目标实现验证。
