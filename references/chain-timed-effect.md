# 有期限攻击倍率与同分片存档恢复

可保存的世界装置对另一个同分片世界实体施加有期限的普通攻击倍率。来源装置保存倍率，Timer保存剩余时间，EntityTracker恢复目标引用。装置在本宿主组件的postpass完成后，才向目标的Combat列表写回本次来源项。效果到期后装置仍可再次使用。

本篇限定762172 / Steam build26474873，权威入口在服务器。原版研究以具名 `buff_attack`、普通未骑乘无武器伤害及顶层世界保存路径为范围，登记 `EXP-CHAIN-EFFECT-001` 保持 `research/restricted/hold` 与 `runtime_verified=false`。自写示例的隔离专服结果见下文。

## 按载体选择恢复入口

| 载体 | 状态与恢复入口 |
| --- | --- |
| 自有顶层世界装置 | 来源装置的prefab保存倍率，Timer保存剩余时间，Tracker保存name/GUID及refs。世界先重建实体，再按旧GUID接回Tracker。来源的prefab postpass写入自己的source/key。 |
| 原版辣味食物的 `buff_attack` | 食用者的Debuffable持有具名buff。首次施加由buff Attach在食用者有Combat时写入来源倍率，同名重施由Extend重开 `buffover`。食用者保存嵌套buff记录，加载时不传共享newents，生成并加载Timer后，RegisterDebuff把当前持有者直接交给Attach。到期或食用者death经Stop、Detach，仍有Combat时撤销倍率，随后移除buff。 |

世界 `SaveGame` 先筛选符合资格的实体，再给已入表的refs目标补旧ID。运行中仍存在但 `persists=false` 的目标可在重启后缺映射。玩家session、背包嵌套和跨分片交接分别沿其自身入口判断可用映射、执行阶段与失联政策。[保存恢复](save-recovery-architecture.md)

攻击倍率写在被施加实体的 `combat.externaldamagemultipliers`。当它随后作为攻击者调用普通无武器 `Combat:CalcDamage` 时，来源列表的聚合值乘入普通伤害主体，加法bonus和特殊伤害各有自己的路径。无武器骑乘分支可能切换到坐骑列表，`alwaysblock` 在倍率前返回0。实际受击还经过后续交战结算。[战斗与Buff](combat-buffs-containers.md)

## 装置状态如何闭合

1. master构造装好Timer、EntityTracker及回调。合法施加先释放旧应用，再追踪新目标、开启新时长、登记目标移除回调，并向目标列表写入本次来源键。参数或目标被拒绝时，旧应用继续运行。
2. 来源保存倍率标量。Timer保存 `timeleft`、暂停标记和初始时长，Tracker保存name/GUID并返回refs。列表项及Lua回调由载体重建。
3. `SetPersistData` 在按标记补建组件后执行来源的 `OnPreLoad`，随后分发组件 `OnLoad`，最后调用prefab的 `OnLoad`。示例在 `OnPreLoad` 结束旧效果，以便自有恢复入口可以配对重放整次加载。实际世界恢复发生在新构造实例上。
4. `PopulateWorld` 在重建实体后调各自的 `LoadPostPass`。本宿主的Tracker先查映射，来源的 `OnLoadPostPass` 再读取目标及剩余时间。合法时直接应用倍率，计时继续走已加载的Timer。缺映射、缺Combat、非正剩余时间、暂停计时或无合法倍率时，示例结束该效果。
5. Timer到期先删除本名字，再发 `timerdone`。到期、主动取消、重施及来源或目标Remove共用一个结束入口，释放本次监听、原列表上的本键、Timer名字、Tracker槽和倍率。

清理需要记住实际施加的目标、列表和函数。目标Remove时Tracker的回调可能已清空槽。若项目主动换掉目标Combat，旧列表仍由本次施加持有，结束时应从旧列表撤键。原版事件先复制回调再派发，当前移除事件中的Tracker回调即使随后继续执行，也只清这个已结束的槽。

同名换目标要先 `ForgetEntity` 再 `TrackEntity`，原版Tracker直接覆盖同名记录会留下旧闭包。上面的 `OnPreLoad` 只约束完整的加载和postpass配对，单独重复调用postpass仍有覆盖风险。本例的组件数据来自正常保存，损坏的Timer数据可能在组件加载阶段出错。若项目要支持Timer或Tracker单独卸载，应先结束效果。目标死亡且实体继续存在时，按项目政策另接death。多个效果之间要用各自的key和Timer名字。[组件与任务归属](component-task-ownership.md)

## 最小可安装示例

示例使用两个无美术、无交互的网络prefab，伤害目标基础值10。把示例目录放入隔离游戏的mods目录并启用。运行时通过服务器入口创建和调用。项目接入时，把下面的施加调用放在已有的权威动作或事件内，并传入项目决定的倍率和时长。源码可直接查看。[Mod信息](../examples/stage4-timed-effect/modinfo.lua) · [登记入口](../examples/stage4-timed-effect/modmain.lua) · [两个prefab](../examples/stage4-timed-effect/scripts/prefabs/stage4_timed_damage.lua) · [完整效果逻辑](../examples/stage4-timed-effect/scripts/stage4_timed_damage.lua)

在隔离世界的服务器Lua控制台运行下面一行，可看到普通伤害从15恢复到10。60秒和1.5为演示值。手动提前取消可调用 `source:StopTimedEffect()`。

```lua
local source = assert(SpawnPrefab("stage4_timed_damage_source")); local attacker = assert(SpawnPrefab("stage4_timed_damage_target")); local victim = assert(SpawnPrefab("stage4_timed_damage_target")); assert(source:StartTimedEffect(attacker, 1.5, 60)); print(attacker.components.combat:CalcDamage(victim)); TheWorld:DoTaskInTime(61, function() print(attacker.components.combat:CalcDamage(victim)); source:Remove(); attacker:Remove(); victim:Remove() end)
```

要手动验重启，可把三个实例分别放到不同坐标以便重载定位，施加较长时长并在结束前用隔离世界正常保存、退出、重启。重启后通过 `Ents` 按prefab和位置找到来源、攻击者与独立受击者，核对下面三个读取点，再等效果结束确认伤害恢复。另建一组令被施加实体 `persists=false` 后保存，重启后只会恢复该组来源，来源应清掉本次Timer和倍率。

```lua
print(source.components.entitytracker:GetEntity("stage4_timed_damage_target") == attacker)
print(source.components.timer:GetTimeLeft("stage4_timed_damage"))
print(attacker.components.combat:CalcDamage(victim))
```

## 验证与来源

示例通过两次独立单分片专服进程。第一阶段验证施加、刷新、无效参数拒绝、换目标及旧目标移除、主动取消、两端实体移除，并通过真实 `CalcDamage` 验证不同来源及同一来源其他键可共存。原始时长120秒，保存前将剩余设为25秒。第二阶段从同一份隔离世界存档重启，脚本读取剩余约16.93秒、伤害17.5，非持久目标缺映射时清理效果。随后原版Timer到期恰好一次，伤害回到10，不相关计时继续保留，已清理的来源可再次施加。两个进程均正常退出。验证边界为该自写Mod的服务器计算与隔离重启，原版食品的实机重启、真实客户端与跨分片待验。

精确源码以登记 `EXP-CHAIN-EFFECT-001` 的 `source_references` 为准。旧映射和生命周期分别参考 `EXP-SAVE-001/004/005`、`EXP-LIFE-001/005/006/008`，来源列表参考 `EXP-MOVE-001`，调味入口参考 `EXP-COOK-006`。原版归档SHA256为 `733a0f7f97ace5a76aa5acee95405a6ec01697d93d844eeb4ecce7c001306980`。[Reviewer读取方法](kb-retrieval.md)
