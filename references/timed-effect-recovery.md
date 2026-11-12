# 有期限目标效果的保存与恢复

由效果来源实体保存业务倍率，Timer持有剩余时间，EntityTracker保存目标引用。加载时先恢复这些值，在来源prefab的OnLoadPostPass接回modifier与运行监听。到期、主动结束和实体移除共用本功能的清理入口。

本篇示例为工程建议，沿762172 / build26474873静态Lua合同编写。既有研究各自的Scope、准入状态与HOLD保持原样。示例已通过Lua语法和替身检查，实际存档重启与联机行为仍待游戏验证。

## 明确这条示例的范围

示例用于一个可保存的世界装置，对另一个带combat的世界实体施加有期限的普通伤害倍率。来源和目标都进入同一分片的标准SaveGame / PopulateWorld路径。来源保留，效果结束后可再次使用。数值由项目传入。

本例选择以下政策，项目可按需求调整。

- 再次施加先结束旧效果，再使用新目标、倍率和完整时长。
- 读档从保存的剩余时间恢复，本例自行计算的时间仅来自Timer，停服的现实时间由项目另行定义。
- 目标缺失、缺combat或剩余时间已尽时结束效果。
- 目标或来源实体被Remove时结束效果。死亡后的处理取决于实际实体是否被移除，需要死亡即结束的功能再接自己的death出口。

背包嵌套物、Debuffable持有的Buff及玩家session有各自保存入口。EXP-SAVE-001指出Debuffable的具名恢复路径未传共享newents，玩家会话也有独立边界。采用这些载体时，先确认目标映射与postpass调用方。本例依赖的是上述同分片世界恢复路径。

## 数据与资源分别由谁持有

| 内容 | 所有者 | 保存与恢复 | 结束时处理 |
| --- | --- | --- | --- |
| 本次倍率 | 来源prefab的局部值 | prefab OnSave写入标量，OnLoad读回 | 清空本次值 |
| 目标身份 | 来源的entitytracker | name/GUID与refs，组件LoadPostPass查newents接线 | ForgetEntity本功能槽位 |
| 剩余时间 | 来源的timer | 组件保存timeleft等数据，OnLoad停止并重建保存名字 | StopTimer本功能名字 |
| modifier | 目标combat的来源列表 | 用新来源实体和同一key重新SetModifier | 按同source/key RemoveModifier |
| 目标移除监听与已施加目标缓存 | 来源prefab的运行闭包 | 每次构造并在施加时登记 | 用原fn和source解绑，清缓存 |

EntityTracker的refs参与映射接线，目标仍须符合实际保存路径的资格。保存表收集完成与磁盘持久化是后续不同阶段。源码依据为EXP-SAVE-001、004、005和EXP-MOVE-001。

## 在自有prefab直接接线

以下代码放在自有prefab的master分支，inst已创建。该prefab由此处配置timer、entitytracker以及所示回调。项目调用StartTimedEffect前校验业务参数，multiplier为有限非负倍率，duration为正秒数，目标具有combat。代码中的名字和key为本机制私有值。

```lua
inst:AddComponent("timer")
inst:AddComponent("entitytracker")

local TIMER = "my_mod_timed_effect"
local TARGET = "my_mod_effect_target"
local KEY = "my_mod_timed_damage"
local multiplier
local applied_target
local on_target_removed

local function StopEffect()
    local target = applied_target
    applied_target = nil
    if target ~= nil then
        inst:RemoveEventCallback("onremove", on_target_removed, target)
        if target.components.combat ~= nil then
            target.components.combat.externaldamagemultipliers:RemoveModifier(inst, KEY)
        end
    end
    on_target_removed = nil
    inst.components.timer:StopTimer(TIMER)
    inst.components.entitytracker:ForgetEntity(TARGET)
    multiplier = nil
end

local function ApplyEffect(target)
    applied_target = target
    on_target_removed = function(removed_target)
        if removed_target == applied_target then
            StopEffect()
        end
    end
    inst:ListenForEvent("onremove", on_target_removed, target)
    target.components.combat.externaldamagemultipliers:SetModifier(inst, multiplier, KEY)
end

function inst:StartTimedEffect(target, value, duration)
    if target == nil or not target:IsValid() or target.components.combat == nil then
        return false
    end
    StopEffect()
    multiplier = value
    self.components.entitytracker:TrackEntity(TARGET, target)
    self.components.timer:StartTimer(TIMER, duration)
    ApplyEffect(target)
    return true
end

inst.StopTimedEffect = StopEffect
inst:ListenForEvent("timerdone", function(_, data)
    if data.name == TIMER then
        StopEffect()
    end
end)
inst:ListenForEvent("onremove", StopEffect)

inst.OnSave = function(_, data)
    data.my_mod_effect_multiplier = multiplier
end
inst.OnLoad = function(_, data)
    multiplier = data and data.my_mod_effect_multiplier
end
inst.OnLoadPostPass = function()
    local target = inst.components.entitytracker:GetEntity(TARGET)
    local remaining = inst.components.timer:GetTimeLeft(TIMER)
    if multiplier ~= nil and remaining ~= nil and remaining > 0
        and target ~= nil and target:IsValid() and target.components.combat ~= nil then
        ApplyEffect(target)
    else
        StopEffect()
    end
end
```

开始入口按本例政策刷新完整时长，返回true表示这段施加流程正常完成，参数不合格的目标返回false并保留现有效果。主动取消可调用inst:StopTimedEffect()。这里改的是combat.externaldamagemultipliers所参与的普通攻击伤害通道，具体伤害仍经过Combat结算。

StopEffect使用applied_target清理实际施加的对象。目标onremove时，EntityTracker可能已经先清空名字槽，单靠GetEntity查当前槽无法承担这一清理责任。更换目标前先Forget旧关系，避免TrackEntity同名覆盖遗留旧闭包。原版Tracker并未在TrackEntity内部代办这一步。

## 加载时的实际先后

1. 新来源prefab构造组件和业务回调，暂时没有活动计时或modifier。
2. SetPersistData按pairs恢复组件。Timer依据保存的剩余值重建调度，随后prefab OnLoad读回倍率。
3. 标准PopulateWorld完成实体重建后安排LoadPostPass。EntityTracker使用旧GUID映射接回目标及自己的移除监听。
4. 本宿主组件postpass完成后，prefab OnLoadPostPass读取目标和剩余时间，满足本例条件才重建modifier及业务监听。
5. Timer到期先删除计时名字，再发timerdone。本功能只消费自己的名字，并调用StopEffect撤销来源项、目标关系和缓存。

本例恢复时直接ApplyEffect，保留Timer已恢复的剩余值。StartTimedEffect属于新施加入口，会按所传duration重开完整时间，因此恢复回调采用自己的状态应用路径。

同一宿主的组件OnLoad、组件LoadPostPass都由pairs遍历。这里使用的是明确的“本宿主组件postpass完成后再执行prefab回调”关系。目标所需的combat来源列表已在目标构造时建立。若实际效果还依赖目标另一个组件的postpass结果，需要定点查明该依赖的真实阶段。

## 退出与适用边界

提前结束时由StopEffect释放本功能拥有的Timer名字、Tracker槽和目标监听，并只移除自己的modifier键。SourceModifierList还会监听实体source的onremove来清该来源项，整实体Remove也会清本宿主事件和pendingtasks。显式结束入口覆盖了来源仍存活时的取消、刷新与目标更换。

若把业务搬进自定义组件，组件的OnRemoveFromEntity应调用自己的结束方法。RemoveComponent与整个来源Remove走不同清理入口。若保留本示例的prefab组织方式，就在现有生命周期回调中直接处理这些资源。本例使用的timer与entitytracker随装置保留；项目若要单独拆除其中一个依赖，先调用StopTimedEffect结束它们承载的效果。

装备用例也沿同一职责划分。EXP-GEAR-001中Fueled保存燃料值，装备/卸下消费者启停消费并处理灯，任务和灯对象在构造及运行入口重建。持续时间、燃料数值和当前装备资格各由相应所有者恢复，再决定是否运行。

## 精确补读

| 开发问题 | 研究与位置 | API或回调 |
| --- | --- | --- |
| 保存映射与本宿主恢复阶段 | EXP-SAVE-001的SAVE-001-C03～C06，api_contracts[1～3] | SpawnSaveRecord(saved,newents)，SetPersistData(data,newents)，LoadPostPass(newents,savedata) |
| 剩余时间和重放 | EXP-SAVE-004-C01～C03，api_contracts[0]，NC-N004-FINAL-07的Timer claims[0～3] | Timer:StartTimer / StopTimer / GetTimeLeft / OnSave / OnLoad |
| 目标接回及换目标 | EXP-SAVE-005-C01～C05，api_contracts[0～2] | TrackEntity(name,target)，ForgetEntity(name)，GetEntity(name)，LoadPostPass(ents,data) |
| 来源项重建与释放 | EXP-MOVE-001-C01～C03，api_contracts[0～1] | SetModifier(source,value,key)，RemoveModifier(source,key) |
| 生命周期身份与删除 | EXP-LIFE-001、005、006、008 | ListenForEvent / RemoveEventCallback，OnRemoveFromEntity，EntityScript:Remove |
| 装备数值与运行资源 | EXP-GEAR-001-C04～C05、C08，EXP-ITEM-004-C02～C03 | Fueled:StartConsuming / StopConsuming，装备及卸下回调 |

直接源码定位为entityscript.lua 1928～2013行，components/timer.lua 27～146行，components/entitytracker.lua 20～63行，util/sourcemodifierlist.lua 64～121行，以及components/combat.lua 65～66、938～945行。来源归档SHA256为`733a0f7f97ace5a76aa5acee95405a6ec01697d93d844eeb4ecce7c001306980`。

继续查表与案例时，可接着读保存恢复、组件资源和装备指南。相应记录保持各自原Scope。[保存恢复架构](save-recovery-architecture.md) · [组件任务归属](component-task-ownership.md) · [装备耗能](gear-fuel-repair.md)

实际接入后应核对施加/刷新/换目标、提前取消、正常到期、目标及来源移除，以及保存后重启时目标、倍率和剩余时间。目标缺映射和零剩余值按本例所选政策结束；其他来源modifier应继续保留。已有代码若另有回调，合并到其既有入口并保留原行为。
