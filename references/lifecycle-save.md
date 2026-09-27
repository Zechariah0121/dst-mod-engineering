# 生命周期、存档与恢复

适用：长期 Buff、形态、传送、父子实体、跨实体监听、存档迁移、组件移除。网络边界见 [networking-rpc.md](networking-rpc.md)。以当前 `entityscript.lua` 的调用顺序为准，不把项目经验写成所有组件通用的固定顺序。

## 每项机制先列进入和退出

至少考虑重复施加、刷新、主动取消、到期、死亡、幽灵、复活、目标/来源移除、丢弃/卸下、组件移除、睡眠/唤醒、保存重载；涉及玩家时加断线与切 shard。只测试正常到期不足以确认清理完整。

死亡后继续计时、暂停还是清除，以及重启后是否保留，都是玩法决策；从项目已有约定取值，不把原版某一种 Buff 的规则强加给所有 Buff。例如“死亡继续计时、复活保留剩余效果”可以是某个项目的要求，但不是本技能的默认规则；重启策略另外核对该项目设计与保存实现。

## 所有权与对称清理

| 申请/注册 | 对称解除 | 注意 |
|---|---|---|
| `listener:ListenForEvent(event, fn, source)` | 同 listener、event、fn、source 的 `RemoveEventCallback` | 匿名函数若要提前移除，应先保存引用 |
| `WatchWorldState` | `StopWatchingWorldState` | 初次绑定主动读状态 |
| task 字段 | `Cancel()` 并清空字段 | 刷新前取消；回调运行后清空；防止旧回调结束新一轮效果 |
| `SetModifier(source, value, key)` | 同 source/key 的 `RemoveModifier` | 不恢复成硬编码 1，不清其他来源 |
| 替换函数/标量 | 仅仍为自己写入值时恢复 | 保留原函数参数、返回值；共享布尔需要明确多来源策略 |
| 全局输入 handler | 保存返回 handle，`handle:Remove()` | Widget/玩家失效不会自动移除所有全局注册 |
| SG 临时状态 | `onexit` 撤销本状态拥有的变化 | 中断、死亡、超时也会退出，不盲目覆写新形态 |

实体 `Remove()` 已有 `RemoveAllEventCallbacks`、`CancelAllPendingTasks` 以及组件 `OnRemoveEntity` 通知。不要虚构“实体销毁不会清理任何监听/任务”。但 Buff 提前停止且实体还在、组件单独移除、把任务挂在玩家而不是 Buff、全局表保存回调等情况，仍需显式解除。`RemoveComponent` 调 `OnRemoveFromEntity`，不等于移除宿主实体。

单个周期任务每次刷新只应有一份。延迟创建 FX 的任务也要登记：取消/移除发生后，不得稍后重新生成旧 FX。清理函数尽量幂等；外部直接删除 Buff/目标时也能移除来源并清空宿主缓存引用，下一次施加可重新建立。

父子关系要区分 `EntityScript:AddChild` 跟踪与 `entity:SetParent` 引擎父级。检查实际使用路径，不能只见 parent 就宣称所有 Lua 自持引用和外部任务都会自动清除。

## 保存签名与加载顺序

| 层 | 保存 | 加载 | 引用修复 |
|---|---|---|---|
| Component | `OnSave()` 返回 `data, refs` | `OnLoad(data, newents)`，多数只需 data | `LoadPostPass(newents, data)` |
| Prefab | `inst.OnSave(inst, data)` 写入传入 data，可返回 refs | `inst.OnPreLoad(inst, data, newents)` / `inst.OnLoad(inst, data, newents)` | `inst.OnLoadPostPass(inst, newents, data)` |

`EntityScript:SetPersistData` 当前顺序：按需要补组件 → prefab `OnPreLoad` → 用 `pairs(data)` 调各 Component 的 `OnLoad` → prefab `OnLoad`。**组件之间没有可依赖的固定加载顺序。** 后续 `LoadPostPass` 再分别调组件及 prefab 的 postpass。

若形态组件改变血量上限：保存足够恢复的数据（比例/合法基准等），`OnPreLoad` 提取迁移输入，在全部相关组件加载后统一恢复。不要依赖形态一定先于 health 加载，也不要为了刷新 HUD 给零血尸体正向 `DoDelta`。是否保存形态、死亡记录如何迁移按玩法和原版死亡流程决定。

保存纯数据，不保存 EntityScript、Component、function、task、userdata 或循环表。跨实体引用保存记录 GUID 并返回 refs；postpass 用 `newents[saved_guid].entity` 解析，缺失目标须安全降级。`entitytracker`、`teleporter` 是可检索范例；跨端 GUID 与存档 GUID 映射不是同一协议。

Buff 的 `persists=false` 不等于一定不存档：当前 `debuffable:OnSave` 会把所持 Buff 的 `GetSaveRecord()` 嵌套保存；`keepondespawn` 管理 `RemoveOnDespawn` 的保留策略。二者都不能直接等同“死亡保留”或“离线继续计时”。

存档 schema 有缺字段默认值；大改结构时加版本，逐版幂等迁移。遇到未知未来版本不要静默覆盖成旧结构。任务保存剩余时间并重建；读档可能先产生构造期任务，必须防双份。

## Sleep、时间和回滚

游戏时间任务、静态时间任务、组件更新、实体睡眠、玩家离线是不同概念。先读组件的 `OnEntitySleep/OnEntityWake/LongUpdate`，再决定计时是否继续。`SetCanSleep(false)` 不能当作已睡实体必然已唤醒的证明；测试应读取状态并通过实际有效操作建立前提。

`LongUpdate(dt)` 是引擎按场景调用的时间补算，不等于自动按现实离线秒数推进所有 Buff。不要对同段时间同时正常更新和补算两遍。回滚会重放存档后事件，奖励、消费、生成和旧世界补刷需要幂等设计；承诺“恰好一次”必须说明提交边界和可回滚范围。

## 传送关闭必须等待抵达完成

`Teleporter:Target(other)` 只建立方向，双向虫洞需要两边建立。控制台跨次调用的临时变量与 Mod 的局部变量作用域不同；不能推广为“Mod 变量不可 local”。管理员控制台必须确认在服务器执行。

临时出口可能持有玩家抵达、镜头恢复等任务。到期时先关闭新入口，再按原版 `pocketwatch_portal.CloseExit`：`IsBusy()` 为 false 才删除出口，否则只登记一次 `doneteleporting` 监听继续等待。直接 Remove 出口会取消其 pending tasks。配对入口删除、超时关闭和外部删除均要纳入测试。

## 验证证据分层

- 纯 Lua/替身：迁移、函数签名、幂等和清理；不能证明引擎保存或渲染。
- 专服真实实体：组件加载、Buff/传送/死亡调用链；假玩家没有账号，不证明真实重连。
- 同一隔离世界两次独立进程：实际 SaveGame 回调、保存文件、再次启动后的值与引用，才是磁盘重启验证。
- 真实账号、远端客户端、跨 shard、预测与延迟：单独执行并报告；未做就列待验。

测试先断言前提：实体有效且已初始化、确实 awake、实际进入指定形态、已离开无敌出生状态、健康组件确实死亡，再断言结果。不能把夹具未触发流程的失败算成产品 bug，也不能用“没有异常”替代目标断言。

## 当前源码检索入口

- `entityscript.lua:648-662,1188-1261,1470-1529,1705-1771,1894-1988,2026-2036`：组件退出、事件/任务、保存和顺序。
- `components/debuff.lua:28-56`；`components/debuffable.lua:39-48,72-149`：刷新、detach、despawn、嵌套存档。
- `util/sourcemodifierlist.lua:64-121`：按 source/key 管理、实体来源移除的自动清理。
- `components/teleporter.lua:325-347,349-423`；`prefabs/pocketwatch_portal.lua:157-163`：在途计数、配对和保存、延后关闭。
- `components/timer.lua`、`components/entitytracker.lua`：剩余时间及存档引用范例。
