# 做一只可靠追击、回家和逃跑的生物

本指南依据 762172 / build 26474873 的静态 Lua，配套 [EXP-AI-008～010](../knowledge/research/native-mechanisms/creature_ai_practical-7dcbb84f4dfc.json)。接入取舍属于工程建议；游戏表现按目标实现确认。

## 先选改动入口

| 实际需求 | 最小接入 | 需要再承担的工作 |
|---|---|---|
| 原版生物只换敌人种类或索敌范围 | master 的 combat 获取/保持回调 | 对照原有回调保留阵营、领袖和特殊形态约束 |
| 保留攻击方式，只改变逃跑/返航优先级 | 局部调整当前 Brain 树中的相应节点 | 对当前树处理重建幂等，保留其他分支和 parent 关系 |
| 新生物使用普通近战 | combat 配置 + ChaseAndAttack + 自身 SG 的 doattack | SG 的攻击起手、命中时点、退出和资源清理 |
| 回到领地坐标附近继续活动 | Leash + 稳定的家位置 getter | 领地半径、回位半径与优先级 |
| 进入巢穴并由巢穴管理实体 | 对应家组件所有权 + GOHOME + SG handler | 选定 spawner/childspawner/hideout 的收纳与再次放出生命周期 |
| 按已有标签或指定对象逃跑 | RunAway 参数或局部节点插入 | 入场条件、持续条件与退出后的运动接手 |
| 固定总战斗时限 | 本功能持有截止时间 + 持续条件组合现有追击节点 | 按玩法确定开始/重置时机，即时截断当前攻击时接 SG 退出 |
| 确定性逃跑终点、多威胁规划，或需要独立状态/取消生命周期 | 自有行为节点 | 自己持有目标/计时/运动意图，并定义取消和完成 |

原版改动优先保留现有 Brain。`AddBrainPostInit` 每次树重建都可能再次运行，按当前树或当前目标节点做幂等，并核对定位唯一性。新物种需求简单时可写紧凑的专有 Brain。既有 EXP-AI-001、003、004 提供安装、重建与持续条件语义。

## 追击先接目标，再接攻击

`combat:SetRetargetFunction(period, fn)` 用于周期获取目标。`fn(inst)` 返回候选，可用第二返回值 `forcechange` 请求替换已有目标。普通路径主要在当前无目标时建议目标，旧目标为建筑而新候选非建筑另有换源分支。返回 nil 会保留当前目标。

`combat:SetKeepTargetFunction(fn)` 的 `fn(inst, target)` 决定持续保留条件。原版会在组件更新中累计检查周期，再结合目标有效性、目标 combat 和 CanBeAttacked 处理。这个 setter 只赋值，适合在初始化时配置。已有目标后临时安装它时，还需核对原目标的更新登记状态。

领地需求应写成两条对应条件。

- 获取候选时，检查生物和候选相对家位置的允许范围，以及阵营/领袖等业务条件。
- 保持目标时，检查当前目标仍满足可攻击性和保留范围。保持检查按累计约一秒的节奏进行，已进入的攻击 SG 还可沿缓存目标继续。严格或即时停止需求按实际要求主动接手返航运动，并处理当前攻击 SG 退出。

通过 `combat:SetTarget(target)` 改目标，受理结果读 `combat.target`。它维护目标监听和事件。`SuggestTarget` 的 true 来自建议分支，后续仍会经过 SetTarget 条件。

`ChaseAndAttack(inst, max_chase_time, give_up_dist, max_attacks, findnewtargetfn, walk, distance_from_ocean_target)` 的几个参数尤其容易选错。

| 参数 | 实际含义 | 开发取舍 |
|---|---|---|
| max_chase_time | 运行计时超过阈值后放弃，攻击或落空事件会重置这段计时 | 固定总交战时长由独立业务计时承担 |
| give_up_dist | 使用当前计算的距离，达到阈值即放弃。普通分支为追击者到目标的距离；海面接近点调整分支重算为追击者到接近点的距离 | 家的边界放在领地条件中 |
| max_attacks | 统计 onattackother 与 onmissother 两种事件 | 命中次数需求另接实际命中语义 |
| findnewtargetfn | READY 验证后仍无目标时调用 | 已有周期索敌时通常可省略 |
| walk | GoToPoint 使用走路意图 | 按物种移动方式配置 |
| distance_from_ocean_target | 目标在无效地面且超出攻击范围时调整接近点，可用 fn(inst,target) | 水陆行为按该物种真实寻路能力确定 |

海面接近点调整在 `distance_from_ocean_target` 配置非 nil、原始距离超出攻击范围且目标不在有效地面时触发，后续 give_up_dist 读取重算的 dsq。固定总交战时限可先由本功能保存截止时间，在外层持续条件中控制现有追击节点，于后续条件评估时限制继续追击和新攻击发起。开始和重置时机按玩法确定。需要即时截断已进入的攻击时间线时，再接 SG 退出。现有组合难以表达独立状态或取消生命周期时，使用自有行为节点。

普通猎犬的实际链路是 `houndbrain → ChaseAndAttack → combat:TryAttack → doattack → SGhound.attack → DoAttack`。SG 缓存攻击目标并在时间线执行伤害。排查“贴近却不攻击”时，依次看 combat.target、攻击距离/冷却、SG 对 doattack 的门槛、攻击状态和命中时间线。TryAttack 在已处于 attack 标签时也会返回 true。

自定义 SG 需要自己的 `doattack` handler、攻击状态和 locomote handler，或经过条件核验复用原有 SG。实际动作类交互如入巢、吃东西则沿 BufferedAction 和 ActionHandler 接线，完整通用链路见 EXP-AI-007。

源码定位为 `components/combat.lua:230–400、473–496、780–843`，`behaviours/chaseandattack.lua:1–120`，`prefabs/hound.lua:174–215、512–559`，`brains/houndbrain.lua:222–226`，`stategraphs/SGhound.lua:41–47、221–251`。

## 回位与入巢按需求接线

巢内数量、放出补员、捕获及回巢后的个体去向，接着读[巢穴与种群](nests-population.md)。

只需回家附近时，给 Leash 提供现有位置 getter 即可。四项配置 `homelocation/max_dist/inner_return_dist/running` 均可用函数接收 inst，位置也可直接给 Point。无家位置时该分支 FAILED，让后续闲逛等分支继续选择。

Leash 在 READY 出界时先 Stop 并进入 RUNNING，下次 Visit 才更新 GoToPoint。距离严格小于 max_dist 才算内侧，距离小于等于 inner_return_dist 即完成。希望形成清晰的回位滞回时，配置 `inner_return_dist < max_dist`。家位置 getter 同次 Visit 可被多次调用，应返回一致的位置。

Leash 完成与丢失 home 的分支仅改变节点状态。如果玩法要求到内圈精确停步，或家消失后立即停步，应由接手分支或自有行为明确发出停止并处理 SG，结合实际运动方式验证。

需要入巢时，先让家组件取得生物所有权。兔洞用 `spawner:Configure("rabbit", ...)`，Spawner 的取得所有权流程维护 child、家位置和 homeseeker。单独 `homeseeker:SetHome(home)` 只建立家引用及移除监听。`GOHOME` 执行时交给目标的 spawner、childspawner 或 hideout。Spawner 成功会保留 child 身份、挂到家下并移出场景，后续放出由该组件管理。

接入自有家类型前要明确 GOHOME 目标的执行结果。当前通用 GOHOME 对缺少上述三类组件的目标会发送 onwenthome 并移除执行者。仅传 pos 的分支也移除执行者。需要普通坐标返航时可直接选 Leash。

兔子的可追踪消费者为 `RabbitBrain.GoHomeAction → DoAction → GOHOME → SGrabbit.action → PerformBufferedAction → Spawner:GoHome`。本轮新增的是家组件、所有权与兔 SG 合同，DoAction 观察和通用分发沿既有 EXP-AI-006/007。

源码定位为 `behaviours/leash.lua:1–61`，`components/homeseeker.lua:1–55`，`brains/rabbitbrain.lua:20–68`，`stategraphs/SGrabbit.lua:3–7、108–120`，`actions.lua:2956–2976`，`components/spawner.lua:186–224、295–322`。

## 逃跑区分获取条件和持续条件

RunAway 支持两种常用入口。

```lua
-- 指定已经选好的威胁，getfn 只在 READY 阶段取值。
RunAway(inst, { getfn = GetThreat }, cfg.see_dist, cfg.safe_dist)

-- 按标签查询，fn 的参数顺序为 hunter, inst。
RunAway(inst, {
    tags = cfg.threat_tags,
    notags = cfg.excluded_tags,
    fn = IsThreat,
}, cfg.see_dist, cfg.safe_dist)
```

getfn 返回者仍须有效且在 see_dist 内。第五参数 shouldrunfn 同样接收 `(hunter, inst)`，用于 READY 入场过滤。RUNNING 保存当前 hunter，直到失效、成功或父分支改选。需要持续检查“仍低血”“仍在冷却”“目标仍属敌对”时，把这个业务条件放在外层 While，参考猪人的冷却躲避分支。

see_dist 决定开始看见谁，safe_dist 决定方向逃跑什么时候成功，成功采用严格大于。`safe_point_fn(inst)` 影响角度偏向，完成仍依据与 hunter 的距离。`runhome=true` 会转为反复提交回巢动作，退出交给巢穴和动作生命周期，适合已接好收纳的生物。

方向逃跑调用 locomotor 方向入口，清该组件原有动作、目的地和路径，再经 locomote 交给 SG。兔 SG 仅在 idle/moving 等对应条件下选择移动状态，因此节点 RUNNING 与实际位移需要分别观察。偏移搜索最终失败时，RunAway 仍可能使用初始方向。对地图障碍下的确定性抵达，采用持有明确目的地和失败处理的行为更合适。

源码定位为 `behaviours/runaway.lua:1–185`，`brains/pigbrain.lua:267–277、395–408`，`brains/rabbitbrain.lua:47–66`，`components/locomotor.lua:1116–1146`，`stategraphs/SGrabbit.lua:24–42`。

## 一个紧凑的连接示意

下段用于自有 Brain 的 OnStart，依赖已配置好的 combat/locomotor/SG，以及调用方提供的 cfg、GetThreat、ShouldFlee、GetHomePos、IdleBehaviour。示例选用“逃跑优先，其次返航，最后追击”的取舍，具体顺序和阈值由生物玩法确定。

```lua
local inst = self.inst
local root = PriorityNode({
    WhileNode(function() return ShouldFlee(inst) end, "flee",
        RunAway(inst, { getfn = GetThreat }, cfg.see_dist, cfg.safe_dist)),
    Leash(inst, GetHomePos, cfg.home_outer, cfg.home_inner, true),
    ChaseAndAttack(inst, cfg.chase_timeout, cfg.target_give_up_dist),
    IdleBehaviour,
}, cfg.reevaluate_period)
self.bt = BT(inst, root)
```

这里复用现有节点承接普通移动与攻击。若“退出逃跑必须立即停步”或“返航途中禁止旧攻击命中”属于明确需求，应把运动/攻击状态退出接到相应所有者，或为该模式实现有清理入口的自有行为。While 条件改变后，当前 SG 的时间线仍按其状态生命周期运行。ChaseAndAttack 构造时注册监听，移除该节点时沿其 OnStop 清理，并在树重建时构造新节点。

实现验收按本次改动选择，并优先复用已有检查和证据。索敌改动核对获取、保持和目标退出；返航改动核对回位、阈值及失家处理；逃跑改动核对所改条件及运动接手。入巢、树重建和客户端表现的检查由实际涉及的所有权、重建或同步改动决定。需要游戏验证时选择相关场景，按实际执行的专服或真实客户端层级记录结果。
