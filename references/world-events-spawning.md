# 世界阶段事件与既有袭击的接入

来源与 API 合同：[机制研究](../knowledge/research/native-mechanisms/world_events_spawning-d2f5ee439e9c.json)。

简单阶段事件可以直接监听所需WorldState键。调整现有猎犬或蠕虫波时，可复用world已有的hounded。两条路线按功能选择，本指南的配置示例把该分片既有袭击改为项目提供的数据。

本指南依据762172 / build26474873的静态源码，配套EXP-WEVENT-001～003。

## 简单阶段或周期事件

已有N006-READY-F03、EXP-WORLD-001、EXP-LIFE-001/006与NC-N004-FINAL-07分别提供Hook、世界状态、事件/任务和Timer合同。需要“以后每次入夜发送一次自有业务事件”时，可以从这个短入口开始。

```lua
AddPrefabPostInit("forest", function(world)
    if not world.ismastersim then
        return
    end

    world:WatchWorldState("isnight", function(inst, isnight)
        if isnight then
            inst:PushEvent("my_night_event")
        end
    end)
end)
```

项目自己的服务端消费者监听my_night_event并实施业务。WatchWorldState登记后等待后续变化。当前阶段初始化可读取world.state.isnight；首次绑定或读档时是否执行生成、奖励等一次性业务，应在功能需求里确定。状态初始化与产生一次副作用分别写入口，可以直接表达这项决定。以上片段选择后续入夜边沿触发。

按秒计时可沿普通Timer的StartTimer与timerdone完成消费，需要世界设置倍率时再选WorldSettingsTimer。后者先AddTimer登记，再StartTimer激活，所配完成callback存在时优先执行callback。任务句柄、具名计时或世界观察中，选择满足当前功能的一种即可。跨读档保留时间、次数或世界唯一标记，仅在需求涉及这些状态时实现。

## 改现有袭击的配置

forest master构造已有hounded。cave在AddComponent之后设置wormspawn，因此洞穴组件PostInit内的自定义表还会遇到这次覆盖。选择单一forest或cave prefab Hook更便于在原版配置之后接入。源码时点见WE05–WE08、WE32/33、WE39/40，完整合同见EXP-WEVENT-001。

项目先在modmain.lua中读取并定义cfg，再直接登记以下Hook。cfg包含prefab、period_seconds、warning_seconds、amount、warning_speech和warning_type。时间单位为秒，amount为个人基础数量，warning_speech为角色台词键，warning_type为HOUNDWARNINGTYPE中存在的键，例如LVL1。周期、数量和警告时长由项目决定。

```lua
AddPrefabPostInit("forest", function(world)
    if not world.ismastersim then
        return
    end

    local function GetDelay()
        return cfg.period_seconds, 0
    end

    local level = {
        warnduration = function(preupgraded)
            return cfg.warning_seconds
        end,
        numspawns = function()
            return cfg.amount
        end,
    }

    world.components.hounded:SetSpawnData({
        base_prefab = cfg.prefab,
        winter_prefab = cfg.prefab,
        summer_prefab = cfg.prefab,
        attack_levels = {
            intro = level,
            light = level,
            med = level,
            heavy = level,
            crazy = level,
        },
        attack_delays = {
            intro = GetDelay,
            light = GetDelay,
            med = GetDelay,
            heavy = GetDelay,
            crazy = GetDelay,
        },
        warning_speech = cfg.warning_speech,
        warning_sound_thresholds = {
            { time = cfg.warning_seconds, sound = cfg.warning_type },
        },
    })
    world.components.hounded:SpawnModeMed()
end)
```

这个示例给所有年龄档相同个人基础量，使用constant模式的med间隔，季节选择都指向cfg.prefab，升级字段按所需普通波配置省略。hounded原有的玩家资格、组总量、目标分配与逐个释放仍会继续执行。个人基础量还会经过组公式和目标分配，实际产出数量要沿EXP-WEVENT-002核对。

SetSpawnData整体替换表，delay/warn函数另外缓存。SpawnModeMed立即绑定新med函数，已有正数剩余时间可保留到自然到期，下次规划才产生新时间。确实需要立即重规划时，在项目确定的执行时点向已有world发送下述事件。它可能重置本轮warning，载入流程中的执行时点也应与业务要求相符。

```lua
world:PushEvent("hounded_forceplannewattack")
```

该事件还支持multtimetoattack与choosemintime。没有活动玩家时，其1秒重试只保留force，额外data会丢失。实际袭击强度的自动升级使用活动玩家平均年龄，GetWorldEscalationLevel按world cycles返回的表另有消费者用途。

## 从预警到实际产出

EXP-WEVENT-001/002的闭合路径如下。

1. PlanNextAttack选择间隔与警告函数并设置剩余时间。
2. OnUpdate进入警告窗口，玩家talker消费台词键，houndwarning事件经player_classified的net_smallbyte与本地dirty处理生成预警声音。
3. 到期时筛选符合年龄和入场时间的玩家，形成距离分组并计算配额。houndedtarget参与权重与额外偷取配额。
4. 每个组按自己的释放间隔选玩家。实体在候选位置生成后可用hounded_overridelocation调整位置，再定位、朝向、淡入并向combat建议目标。
5. 组配额完成后进入下一周期。

只调整吸引目标关系时，可参考Wes及LuckUser对houndedtarget.target_weight_mult和hound_thief_sources的具名source/key修改。效果退出时撤回自己对应项。精确调用形态见WE23–WE25。

单次生成的两个公开方法各有用途。

| 接口 | 输入与返回 | 实际消费 |
| --- | --- | --- |
| SummonSpawn(pt,radius_override) | 中心Vector3与可选半径，返回实体或nil | 按当前配置选prefab，找点、生成与定位 |
| ForceReleaseSpawn(target) | 目标实体，Lua返回nil | 地点缓存允许时生成，再combat:SuggestTarget |

两者直接进入辅助生成路径。整波的warning、never模式和pause检查位于OnUpdate中，调用这些方法时需按自己的功能条件决定时点。需要确切实体返回值和自定目标时，可取得SummonSpawn返回实体后再实施所需行为，生成物须具备所调用的组件。

原版HandleSpawnInfoRec先扣配额再尝试ReleaseSpawn，其返回值被忽略。找点或生成失败仍可能消耗本次配额。自有事件可按结果决定记数或重试，使用自己的SpawnPrefab与位置逻辑也能满足指定prefab、指定点位等需求。证据见WE18–WE22。

## 暂停、禁用与恢复

EXP-WEVENT-003记录了具名atrium_gate的pausehounded/unpausehounded消费者。

```lua
world:PushEvent("pausehounded", { source = activity, reason = "my_event" })
-- 活动结束时
world:PushEvent("unpausehounded", { source = activity, reason = "my_event" })
```

source与reason表示本活动自己的修改项。OnUpdate先推进延迟波，再扣全局时间，之后才进入带条件的暂停分支。全局警告、待释放波次和逐玩家延迟波都有各自继续推进的条件。需要停止该组件全部OnUpdate推进时，SpawnModeNever在入口生效。恢复时根据项目选择SpawnModeNormal或所需constant模式，并核对保留的剩余时间。

保存时hounded记录警告时间、userid进度与升级字段。模式、配置和暂停来源由构造及活动生命周期重新建立。已planned且保存时间小于warning时长的读档路径会将时间改成warnduration+5。762172的个人延迟配额在保存/还原与更新消费之间存在数据形态不一致，可能影响剩余配额恢复。项目依赖精确延迟补发时，应核对EXP-WEVENT-003-C06/C07并做退出重入及读档验证。该问题目前仅完成静态核查。

## 复用位置与本轮范围

以下基础合同按各自版本Scope使用。

- N006-READY-F03提供Hook和world加载阶段，EXP-WORLD-001提供WorldState逐键观察。
- EXP-LIFE-001/006提供事件身份、任务句柄和清理入口。自有组件的退出按其实际监听和句柄处理。
- NC-N004-FINAL-07提供Timer与WorldSettingsTimer选用合同。
- EXP-GROW-003/004已有资源再生与父实体繁殖，保留原759671范围。实际需要这些机制时再核当前分支。

数值、初次/载入补发、跨分片范围和失败补偿政策留给具体功能确定。实际联机、声音、地图落点、玩家离场及恢复验证仍待后续实施。
