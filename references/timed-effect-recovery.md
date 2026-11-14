# 有期限目标效果的保存与恢复

可保存的世界装置对同分片的世界实体施加倍率时，由来源装置保存业务值，Timer 保存剩余时间，EntityTracker 保存目标引用。宿主组件完成 postpass 后，再在来源 prefab 接回运行监听和 modifier。完整接线、可安装示例及隔离专服重启结果见[有期限效果链](chain-timed-effect.md)。

选择实现前，确定重施是刷新、叠加还是替换，目标缺失如何处理，死亡是否结束效果，以及停服期间是否计时。自有世界装置、Debuffable 持有的嵌套 Buff 和玩家 session 走各自的恢复入口。核对目标映射与实际调用方，再决定何时重接运行状态。

结束效果时，用当初登记的函数、目标、来源与键解除本次监听和 modifier。若效果由组件持有，组件卸载也要进入结束路径。依赖 Timer 或 EntityTracker 的实现，在单独拆除组件前先结束它们承载的效果。

装备用例也沿同一职责划分。`EXP-GEAR-001` 中 Fueled 保存燃料，装备和卸下入口启停消耗并处理灯。恢复后根据当前装备资格重建任务和表现。[装备效果链](chain-equipment.md)

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
