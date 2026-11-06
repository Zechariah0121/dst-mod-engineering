# 保存恢复接入：用配对涡流口贯穿状态、引用与任务

结论：复杂 Mod 应先找清楚“谁保存权威值、谁创建实体、谁提供映射、谁在何阶段消费引用、谁重建并取消任务”。原版具名路径提供这些接线，但没有自动把所有状态变成磁盘事务。本专题是工程接入说明与静态推导，不是可直接宣称已运行的框架或实现。

本批来源：762172 / build 26474873；冻结 ZIP SHA256 `733a0f7f97ace5a76aa5acee95405a6ec01697d93d844eeb4ecce7c001306980`。版本是任务给定来源身份，已核对 ZIP 字节；未启动游戏。事实（NSF）、推导（EI）、建议（REC）分别标识，所有条目保持 research/restricted/hold，runtime_verified=false。准确证据符号、范围及 raw/range SHA 全部位于 [登记研究](../knowledge/research/native-mechanisms/persistence_recovery-c9ceaf8c5538.json) 的 source_references；本文不含原版 Lua。

## 先界定已有知识与本次增量

组件分发顺序、默认缺键、Timer 通用合同沿用 `AI-N001-07`、`NC-N004-FINAL-07`；世界加载阶段沿用 `N006-READY-F03`；保存表不等于落盘、独立回滚不保证恰好一次沿用生命周期/露露事务专题。它们各自历史 Scope 与 HOLD 不变。本批增量是 001 的旧 GUID 映射生产消费闭环、002 的 mermhouse 具体三态读档消费者，以及 003 的保存委托与 callback 续行合同，已有条目保留原身份与范围。

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

## 未闭合的失败边界与应做的验证

| 边界 | 当前能确定 | 仍需独立验证/决策 |
|---|---|---|
| 保存目标缺失 | refs 不强制保存；tracker/ChildSpawner 对缺映射跳过 | 目标业务该阻止、降级、人工处理还是补偿；缺失不是销毁证明 |
| 子组件在加载时移除 | burnt 可移除 ChildSpawner，当前回调检查存在 | 第三方 Hook 又添加/移除组件、异常中断后的状态 |
| 零剩余时间/构造任务 | Timer 保存名字先取消同名再重建 | 调度 tick、首轮巡检与加载后业务时序；暂停/离线政策由项目选定 |
| 嵌套/玩家 session | 是否透传映射和安排 postpass 由调用方决定 | 实际持有路径切换、账号重连、跨 shard 迁移 |
| Spawn/OnLoad 抛错 | Lua 分发无逐组件原子保护；映射可已登记 | 部分实体/引用/资源如何回收，不能宣称原生自动回滚 |
| 磁盘保存 | 表、原生接口、callback 后续层次可查 | 两次独立进程验证真实值/引用/任务，进程中断/断电写盘保证 |
| 跨 shard 与独立回滚 | 本地表和 GUID 协议不提供共同提交证明 | 真实双 shard 乱序、断线、单侧回滚；不能照搬 lulu journal 名字即声称 exactly-once |

以上是待验方案，未运行。对目标 Mod 的最小验收应先断言测试前提，再覆盖同 shard 保存→退出→独立进程恢复：两口互引、缺一口、不存在 prefab、任务到期/暂停/组件移除，以及旧缺字段/显式 false/burnt 数据。涉及账号和 shard 时另建隔离场景，报告每份保存与运行身份。纯表回调替身即使通过，也只能验证本地逻辑，不能替代这些引擎、磁盘或网络结果。

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

所有编号都可在 [登记研究](../knowledge/research/native-mechanisms/persistence_recovery-c9ceaf8c5538.json) 独立定位到精确 ZIP member、符号和范围摘要；引用链不是运行结果。
