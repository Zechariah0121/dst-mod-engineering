# 保存恢复接入：用配对涡流口贯穿状态、引用与任务

先明确谁保存权威值、谁创建实体与映射、何时接回引用、谁重建并取消任务。下面以原版配对涡流口说明接线，再给出工程建议。

来源为 762172/build26474873，ZIP SHA256 `733a0f7f97ace5a76aa5acee95405a6ec01697d93d844eeb4ecce7c001306980`。本篇为静态研究；符号、范围与摘要见[登记研究](../knowledge/research/native-mechanisms/persistence_recovery-c9ceaf8c5538.json)，准入按[检索策略](kb-retrieval.md)。

## 先界定已有知识与本次增量

组件分发顺序、默认缺键、Timer 通用合同沿用 `AI-N001-07`、`NC-N004-FINAL-07`；世界加载阶段沿用 `N006-READY-F03`；保存表不等于落盘、独立回滚不保证恰好一次沿用[生命周期](lifecycle-save.md)与[唯一物品提交边界](lulu-transactions-crafting.md)专题。本篇侧重 001 的旧 GUID 映射生产消费闭环、002 的 mermhouse 具体三态读档消费者，以及 003 的保存委托与 callback 续行合同。

## 贯穿例：bootleg 创建的两个 oceanwhirlportal

这是原版实际调用链，不是虚构 Mod 功能。`bootleg` 的 CreateOceanWhirlportal 创建入口/出口并分别 SetExit，两个方向显式设置（NSF；SAVE-S17）。oceanwhirlportal 在 master 分支添加 entitytracker、timer、timerdone 监听，启动 closewhirlportal 倒计时，并创建一份 _check_for_boats_task 周期巡检；客户端提前返回（NSF；SAVE-S18、SAVE-S20）。

| 数据/运行资源 | 当前所有者 | 保存和恢复来源 | 不能据此推出 |
|---|---|---|---|
| exit 与 blocker 引用 | 每个口的 entitytracker | name/GUID + refs，postpass 从旧 GUID 接新实例并重建 onremove 监听 | refs 会强制保存任意目标、跨 shard GUID 有效 |
| closewhirlportal 剩余时间、paused、initial_time | 每个口的 timer | OnSave 写值；OnLoad 对保存名字先 Stop 再 Start | task handle 被序列化、现实离线时间自动扣除 |
| timerdone 响应函数 | prefab 构造 | 新实例构造时重新注册 | 旧 closure/任务从磁盘恢复 |
| 船巡检周期任务 | prefab 的 _check_for_boats_task | 每次构造重新创建；没有在 Timer 保存表中 | 所有任意任务都会自动恢复、保存了精确巡检相位 |
| 声音循环和关闭动画 | prefab 运行表现 | 构造/关闭/移除回调组织 | 声音播放进度和动画帧被这些组件持久化 |

表中事实依据 SAVE-S11、SAVE-S14～S16、SAVE-S18～S20。任务初值和周期是原版配置；迁用到目标 Mod 时使用既有玩法约定，不从此例设定新数值。

### 从同一 shard 保存到恢复

1. **生成与使用**（NSF）：SetExit 只用 entitytracker 建立该方向的 exit。巡检先处理自己 blocker，再取 exit；exit 为 nil 立即返回，出口有 blocker 也返回。不要把单向 SetExit 当双向自动配对（SAVE-S17～S18）。
2. **收集内存记录**（NSF）：每个顶层口若满足 SaveGame 保存资格，GetSaveRecord 收集 timer 和 entitytracker 数据。tracker 返回另一口/船 GUID；第二返回非 nil 时，SaveGame 将保存者自身 GUID 和 refs 都加入 references，空 refs 表也满足条件。GetPersistData 只要有非空数据就返回该表，因此有自身保存数据的顶层实体即便无外部引用也可能得到 id。最后只对已经进入 saved_ents 的目标标记 record.id。目标本轮没被顶层保存时打印缺引用，不会沿 refs 自动把它保存下来。GetSaveRecord 本身不自动保存自己的 GUID（SAVE-S01～S02、SAVE-S06～S08、SAVE-S11、SAVE-S16）。
3. **交给原生写入**（NSF/UNK）：SaveGame 先把表转字符串，再由 SerializeWorldSession 委托 TheNet。原生 callback 后还走 override/index/timefile 回调，最后 EndWorldSave 和 cb()。这些 Lua 路径不定义 fsync 或断电 durability；OnSave 结束只证明表收集阶段走过（SAVE-S22～S24）。
4. **构造新实例**（NSF）：PopulateWorld 把同一个 newents 交给每次 SpawnSaveRecord。新 prefab 先建立组件、监听、默认关闭 timer 和周期巡检；SpawnSaveRecord 在当前实例 SetPersistData 之前登记旧 id→{entity,data}，无 id 用 inst table 当键。此时另一口可能尚未创建，不能在 OnLoad 假设共享图已完成（SAVE-S03、SAVE-S05、SAVE-S10、SAVE-S20）。
5. **恢复权威值**（NSF）：Timer 对保存的 closewhirlportal 名字取消构造期同名计时再重建，保存状态覆盖该名字。未保存的名字不由这段循环统一清掉；示例没有保存 task handle。若把类似任务写在自定义组件，必须按自己的持有资源处理构造期任务，不能仅凭 Timer 的行为推断（SAVE-S15～S16）。
6. **接回出口**（NSF）：本路径全部 SpawnSaveRecord 完成后，映射中的实体才依次 LoadPostPass。EntityTracker 用保存旧 GUID 查映射，有则 TrackEntity 接线与注册移除监听，缺则跳过。每个宿主的组件 postpass 先于其 prefab postpass；不同实体之间没有固定先后保证（SAVE-S04、SAVE-S10～S11）。
7. **恢复后的运行和清理**（NSF）：到期时 Timer 先 StopTimer，再发 timerdone。该 prefab 只消费 closewhirlportal：取消/清空巡检任务、设 persists=false、播放关闭动画并等 animqueueover Remove。外部移除目标时 tracker 的监听清引用；实体 Remove 自有 CancelAllPendingTasks 等清理。组件单独移除时 Timer 的 OnRemoveFromEntity 负责取消自己的 timer 任务（SAVE-S11、SAVE-S14～S15、SAVE-S19、SAVE-S21）。

**推导边界（EI）**：该例能展示“保存值→重建任务→引用接线→关闭清理”，不能据静态 Lua 承诺第一轮巡检一定晚于全部加载副作用，或恢复了精确原任务相位。若自定义口在缺 exit 时会生成替代出口，就增加了原版没有的副作用；须按目标业务单独证明重试与取消，不能用“原版缺映射直接返回”的证据为补发背书。缺 exit 也不证明另一个 shard 上没有对应对象。

## 嵌套物品接入时，沿保存调用方追到 postpass

Container 与 Debuffable 都会手工保存子实体，但协议不同（NSF；SAVE-S12～S13）：Container 汇总 refs，并向 SpawnSaveRecord 传 shared newents；Debuffable 丢弃第二返回、不给 newents。SpawnSaveRecord 不自行 postpass。前者在这里可使嵌套项以 inst-key 进入世界后续遍历，即便没有旧 id；这并不使其他实体保存的旧 GUID 能反查到它。SaveGame 的 id 标记只查顶层 saved_ents（SAVE-S05～S08、SAVE-S10）。

**建议（REC）**：若目标 Mod 的“任务物品”放入容器后仍需跨实体引用，先验证记录是否真的带旧 id、目标是否进入映射、所属调用路径是否有 postpass，或项目是否已有稳定身份协议。不要同时在世界注册表和容器各保存一份同一实体；也不要给所有嵌套系统统一假定 Container 的能力。玩家 session 又是另一个协议：SerializeUserSession 明确忽略 refs；具名 ResumeExistingUserSession/RestoreSnapshotUserSession 没有传世界映射或在函数内调 postpass（SAVE-S22、SAVE-S25～S26）。

## 当前热修消费者：构造默认值不覆盖已存 false

mermhouse 的 master 构造可随机设置 ismummyhouse。当前保存函数在该字段非 nil 时明确保存最终 false；加载用 ~=nil 区分字段存在与缺失：有字段走保存值恢复；缺字段且当前随机为真才安装 HN_OnLoadPostPass（NSF；SAVE-S27～S28）。旧字段转换另在 OnPreLoad 调 WorldSettings_ChildSpawner_PreLoad，然后正常进入组件加载（SAVE-S29、SAVE-S38）。

ChildSpawner 保存外部孩子 GUID+refs，OnLoad 恢复数量/计时，LoadPostPass 再 TakeOwnership，把 home/监听接回（NSF；SAVE-S30～S32）。EntityScript 的本宿主阶段关系使 HN prefab postpass 可以检查已经接回的普通孩子。它检查当前 childspawner 是否仍存在，并通过有效普通孩子有装备这一条件清除 mummyhouse 标记；不扫描 emergency 子表，不生成替代孩子（SAVE-S04、SAVE-S27、SAVE-S33、SAVE-S39）。

burnt onload 会经构造绑定的 DefaultBurntStructureFn 移除 ChildSpawner，所以 postpass 重新检查组件存在是具体必要条件。另一个 merm prefab 新绑定的 postpass 会对 mummy 调 DropEquipped，说明“恢复”也可能产生装备状态副作用，不只是赋字段（NSF；SAVE-S27～S28、SAVE-S34～S37、SAVE-S40）。本宿主组件→prefab 的屏障不提供所有房屋与孩子之间的 postpass 总序。具体而言，房屋 HasAnyEquipment 与另一个 merm 实体 DropEquipped 的先后未证明，不能声称房屋必然看到卸装前或卸装后的装备状态。

**建议（REC）**：目标 Mod 若有同类问题，只为其真实三态字段与依赖补最小恢复步骤：构造给新建默认值；有保存值则读回；缺字段且满足旧档识别条件时修正；依赖引用的修正在本宿主相应阶段组织。不要在恢复路径调用有消费、奖励、随机生成的“新建一次”入口来代替状态应用。这里不默认创建统一迁移框架，也不替用户决定旧档应否保留、重置或补发。

新旧 761239/762172 比较仅作为增量定位；本批候选引用全部绑定当前字节。公告所说 reload 重复生成和烧毁房屋崩溃提供研究线索，不证明任一 Lua 分支的唯一根因，也不是运行验证。热修范围见[适配记录](../docs/version-762172.md)。

## 失败与重复恢复时，按已发生的业务事实继续

下表把既有源码阶段与目标 Mod 的恢复建议分开。工程建议仅用于本次功能实际可达的失败或重复入口。恢复方法的返回值、业务完成状态和保存回调分别记录其含义。

| 已经过的阶段 | 已登记的源码事实 | 目标 Mod 的处理建议（REC） |
|---|---|---|
| 实例构造、登记映射 | SpawnSaveRecord 构造实例，传入 newents 时在 SetPersistData 前登记映射。构造已可能创建任务，后续 OnLoad 可抛错（SAVE-S03、SAVE-S05、SAVE-S20） | 失败处先核对当前实例、映射和自持资源。重试是否复用实例、回收后重建或保留未决，由实际调用方与业务约定决定 |
| 应用保存值 | SetPersistData 按 pairs 分发，各组件之间没有逐项异常隔离。Timer 对保存名字先停再建（SAVE-S03、SAVE-S16） | 应用保存事实时沿用资源修改与任务管理接口。若重复入口确实存在，检查同名任务或同一资源的现存句柄，避免再扣初始费用、再给奖励或叠加任务 |
| 接回引用、执行 postpass | 映射中的宿主进入 postpass，引用消费者接回监听。merm 的装备回调还能改变装备状态（SAVE-S04、SAVE-S10～S11、SAVE-S32～S34） | 引用已接回与整项业务完成分别判断。重试前查看已改变的对象及当前所有者，按该功能的结果状态继续，缺引用时执行已约定的等待、拒绝或降级 |
| 后续运行、实体生成与交付 | 唯一物品案例中，生成实体后交付失败仍保留占用。普通 Remove 也可能来自卸载（LULU-09） | 将已生成实体身份、已消费资源、已完成交付各自作为事实。对结果未知的生成调用保留未决，补发或退款需要既定业务依据 |
| 收集保存表、回调续行 | SaveGame 经原生写入接口后继续 override/index/timefile 回调。传入用户 cb 时，最终服务端以无参数 cb() 续行（SAVE-S22～S24） | 说明自己观察到的阶段。需跨重启恢复的业务事实由对应保存所有者纳入记录，并通过独立进程恢复验证 |

这里的“业务提交点”按操作的可见效果界定。扣费、生成、交付和持久化各自可能先后完成，某一步返回 false 或捕获异常时，要向调用方暴露已发生的结果与剩余未决事项。原生映射登记和 OnLoad 分发本身未建立补偿协议。唯一物品的具体占用取舍及证据见[提交边界案例](lulu-transactions-crafting.md)。

只在真实重复路径上补去重。稳定字段优先直接恢复，任务按当前句柄替换。接回监听前核对已有关系和回调身份，换目标时先释放当前旧关系。确需记录已处理结果时，其身份、保存位置和可回滚范围应来自现有业务合同。初始化布尔、全局锁或新增 Manager 本身无法证明这些事实。原生加载函数也未承诺对同一实例反复调用整段 OnLoad/postpass 都等价，具体入口需单独核对。[简化与恢复原则](complex-mod-architecture.md#保存的是可恢复事实失败政策要由业务明确)

## 重复恢复的具体边界

EXP-SAVE-004～006 补充以下三条恢复路径，沿用本篇的静态来源范围与准入规则。下文区分源码事实（NSF）、工程推导（EI）和建议（REC）；完整合同、引用和未知项见[重复恢复研究](../knowledge/research/native-mechanisms/recovery_replay-ec70042afbff.json)。

### Timer 重放会按本次时间重建截止点

**NSF。** Timer:OnLoad 对保存名字逐一 StopTimer，再 StartTimer。StartTimer 以本次 GetTime 加保存的 timeleft 计算 end_time。暂停记录也先创建任务，再由 PauseTimer 取消新句柄并保留计时记录。保存表未列出的当前名字继续保留，涡流口构造的独立周期巡检也由自己的字段持有。（EXP-SAVE-004-C01、C04，REC-S01～S06）

**EI。** 时间推进后再应用同一份运行计时记录，会从该保存剩余值重新计时。StopTimer 已经释放旧名字后，读取新记录字段或建立新调度仍可能抛错，此前完成的名字替换沿所查路径保留。pairs 没有固定名字先后，需按实际状态判断部分替换结果。（EXP-SAVE-004-C02～C03，REC-S02～S04、REC-S07、REC-S09）

**REC。** 排查真实重复恢复入口时，比较本次 payload、当前截止时间、任务句柄、未保存的构造名字和独立任务。需要保留原截止点还是重新应用剩余值，沿用该功能的时间政策。修正重复应用来源后，再验证暂停、零剩余时间和中途失败。

### Tracker 同名覆盖会遗留旧监听身份

**NSF。** EntityTracker:LoadPostPass 对映射中存在的对象调用 TrackEntity。每次 TrackEntity 新建 onremove 闭包，覆盖名字槽位后登记监听。闭包只按 name 清空槽位。ForgetEntity 与组件 OnRemoveFromEntity 按当前记录保存的目标和函数身份解绑，宿主整实体删除还有按实体归属清理两向事件索引的路径。（EXP-SAVE-005-C01、C03，REC-S11～S18、REC-S31）

**EI。** 同名槽从 A 覆盖为 B，若 A 的旧闭包仍在且随后被其 onremove 派发，它会清掉当前槽，即使该槽已指向 B。重复同一 postpass 也会生成不同闭包，当前记录只保留最后一次的身份，因而不能靠随后 ForgetEntity 找回此前所有闭包。此处是具名覆盖序列的静态推导，实际原版调用者能否到达该序列需逐一核对。（EXP-SAVE-005-C02～C03，REC-S11、REC-S15～S19）

**REC。** 确需更换已追踪目标时，先按当前槽释放旧关系再接入新对象。已发生覆盖时，还需核对旧目标上的残留订阅。验证当前功能实际支持的同名换目标、重复 postpass、旧目标移除、组件卸载与缺 GUID 映射。检查执行中的回调还要沿用同步事件的既有合同。

### 奖励队列从恢复到交付有多个写入点

**NSF。** Friendlevels:OnLoad 读回等级和 queuedrewards，非空队列同步发布 friend_task_complete，任务 complete 标志随后在组件 LoadPostPass 按数组索引恢复。hermitcrab 的 master 构造配置奖励回调与监听，onTaskComplete 按 giverewardstask 是否存在建立周期任务。任务在 ishome 或附近无玩家时返回并保留，满足条件才进入 rewardcheck。（EXP-SAVE-006-C01～C02，REC-S21～S24、REC-S30）

**NSF。** DoRewards 逐条执行奖励函数并拼接物品，处理 specifictaskreward 后才换空 queuedrewards。rewardcheck 接到返回数组后维护 itemstotoss，再逐个调用 inventory:GiveItem。消费者继续完成后续计时与对话逻辑，走到尾部才取消并清空 giverewardstask。createbundle 还能创建礼包、包装礼物、移除临时礼物，并按独立 pearlgiven 等条件生成珍珠。pearlgiven 另由 prefab 保存和恢复。（EXP-SAVE-006-C03、C05，REC-S21、REC-S23、REC-S25～S29）

**EI。** 后续奖励函数或数组拼接抛错时，前面已经产生的副作用保留，尾部清队列尚未执行。正常完成后组件换空队列，旧 payload 持有的原队列引用仍可被再次 OnLoad 接回。若异常发生在清队列后的库存调用或后续消费者逻辑，队列已经清空，任务清理却可能尚未到达。各类奖励还受独立业务字段影响，需要沿具名回调核对重复结果。（EXP-SAVE-006-C04、C06，REC-S21、REC-S23、REC-S26、REC-S29）

**REC。** 为实际允许重试的业务分别核对待处理记录、已生成对象、交付结果、消费者任务和后续保存状态，再按项目约定处理部分失败与旧 payload 重放。giverewardstask 只反映当前消费者任务的建立状态。提交身份和补偿政策按该业务的真实需要设计，保存后的恢复效果另做独立进程验证。

以下为关键源码定位；重复应用、异常注入和奖励交付的运行验证见后文待验项。

| 研究与证据 | ZIP member 与范围 |
|---|---|
| EXP-SAVE-004，REC-S02～S03 | `scripts/components/timer.lua`，27～114、122～142 行 |
| EXP-SAVE-005，REC-S11 | `scripts/components/entitytracker.lua`，1～66 行 |
| EXP-SAVE-006，REC-S21 | `scripts/components/friendlevels.lua`，1～119 行 |
| EXP-SAVE-006，REC-S23、REC-S26 | `scripts/prefabs/hermitcrab.lua`，673～776、805～847 行 |

## 未闭合的失败边界与应做的验证

| 边界 | 当前能确定 | 仍需独立验证/决策 |
|---|---|---|
| 保存目标缺失 | refs 不强制保存；tracker/ChildSpawner 对缺映射跳过 | 目标业务该阻止、降级、人工处理还是补偿；缺失不是销毁证明 |
| 子组件在加载时移除 | burnt 可移除 ChildSpawner，当前回调检查存在 | 第三方 Hook 又添加/移除组件、异常中断后的状态 |
| 零剩余时间/构造任务 | 已登记同名替换。EXP-SAVE-004 补充相对截止时间重放与逐名部分替换 | 调度 tick、首轮巡检、重复应用后的截止点与异常状态，暂停/离线政策由项目选定 |
| 嵌套/玩家 session | 是否透传映射和安排 postpass 由调用方决定 | 实际持有路径切换、账号重连、跨 shard 迁移 |
| Spawn/OnLoad 抛错 | Lua 分发无逐组件原子保护，映射可已登记 | 按失败位置核对部分实体、引用、任务与已发生的业务副作用，再按政策恢复 |
| Tracker 重复接回 | EXP-SAVE-005 推导同名覆盖后旧闭包清当前槽 | 当前调用者的可达序列、旧目标移除和组件卸载后的监听身份 |
| 奖励队列重放与交付 | EXP-SAVE-006 区分回调副作用、清队列、库存调用与任务清理 | 中途失败、独立业务字段、旧 payload 重放，以及成功交付后再次保存和独立进程恢复 |
| 磁盘保存 | 表、原生接口、callback 后续层次可查 | 两次独立进程验证真实值/引用/任务，进程中断/断电写盘保证 |
| 跨 shard 与独立回滚 | 本地表和 GUID 协议不提供共同提交证明 | 真实双 shard 乱序、断线、单侧回滚；需要验证实际保存、重试与去重协议，再界定可承诺的重复语义 |

本篇涡流口与鱼人示例未运行。目标 Mod 按实际保存合同选择互引、缺目标/prefab、任务到期/暂停/移除，以及缺字段/显式 false/burnt 数据等恢复场景，先确认前提，再用同 shard 独立进程验证。涉及账号或跨 shard 时另验对应路径，当前有界服务器恢复观察见[阶段 9](../docs/phase9-action-closure.md)。

## 证据导航

| 编号 | 主题 |
|---|---|
| SAVE-S01～S05 | 记录、保存聚合、加载分发、postpass、实例映射定义 |
| SAVE-S06～S10 | 世界保存资格/id 标记与世界恢复调用方 |
| SAVE-S11～S13 | EntityTracker 引用消费与两个嵌套调用方 |
| SAVE-S14～S16 | Timer 清理、完成事件、剩余值保存恢复 |
| SAVE-S17～S21 | bootleg/oceanwhirlportal 实例构造、运行、退出与实体任务清理 |
| SAVE-S22～S26 | 原生写入桥接、SaveGame 续行、玩家恢复对照 |
| SAVE-S27～S33 | Mermhouse 三态、ChildSpawner 保存/标量恢复/引用接回 |
| SAVE-S34～S40 | Merm 装备 postpass、烧毁组件移除、旧 timer 转换与装备消费者 |
| SAVE-S41～S46 | 房屋最终工厂、孩子监听建立/移除、postpass 更新生命周期、组件移除分发与烧毁包装接线 |

上表 SAVE-S 编号均可在 [登记研究](../knowledge/research/native-mechanisms/persistence_recovery-c9ceaf8c5538.json) 独立定位到精确 ZIP member、符号和范围摘要。
