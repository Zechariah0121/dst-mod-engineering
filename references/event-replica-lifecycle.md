# 事件订阅与 Replica 生命周期应用参考

本篇补充[模块架构](complex-mod-architecture.md)中的订阅身份和清理责任，依据 762172/build26474873 静态 Lua。精确引用及 SHA 见[登记研究](../knowledge/research/native-mechanisms/event_replica_lifecycle-d095aaa0a869.json)，准入按[检索策略](kb-retrieval.md)。

## 订阅归谁，解绑就由谁持有身份

**源码事实。** `listener:ListenForEvent(event, fn, source)` 同时把关系记到 source 的监听者表和 listener 的订阅表；source 省略时为 listener。没有订阅句柄，正常返回 nil。回调收到 source 与 data，不能凭第一个参数认定自己是 listener。（EL-S01、05；完整派发合同复用 EXP-ARCH-001。）

**工程建议。** 为需要退出或重新绑定的订阅保存 listener、event、原 fn 和 source。另建一个看起来相同的闭包不能解绑原函数。解除时用原身份调用 RemoveEventCallback；不要把临时创建的函数当取消令牌。

**源码事实。** 重复绑定会重复追加；RemoveEventCallback 经 RemoveByValue 删除同一归属列表内全部相同 fn。无匹配时正常返回 nil，没有“删除成功”布尔值；fn 缺失或不是函数会断言失败。对已经形成的派发快照，解绑不会撤销本轮回调。（EL-S01–03、05。）

因此，防止重复登记应放在自己的绑定入口；若设计真的需要多次独立登记，必须自己定义身份和次数规则，不能借原版解绑次数实现引用计数。原版 container 保存 ondetachclassified 闭包，再以原 classified 为 source 解绑，是一个可追踪身份的局部实例；不要顺便重放其槽初始化。（EL-S08；EXP-ARCH-004。）

## 局部解绑与整实体析构分开

**源码事实。** RemoveAllEventCallbacks 同时清本实体对别人的订阅，以及别人对本实体的订阅。它不是“只移除本模块监听”的工具，也不取消任务、关闭任意资源或永久禁止重新登记。（EL-S04。）

EntityScript:Remove 的 Lua 顺序是全局 Lua OnRemoveEntity → onremove → watcher 清理 → 整事件清理 → pending tasks 取消 → component / 底层 replica 的 OnRemoveEntity → 后续实体清理。onremove 抛错可能阻断后续步骤；不能由整事件清理可重复推出完整 Remove 可重入或幂等。（EL-S05–07、22–23。）

**工程建议。** 普通模块停止时只释放自己持有的订阅、任务和表现。把“卸载组件”“隐藏复制视图”“移除实体”列成不同阶段，按实际调用链决定谁释放资源。

## 世界状态按字段派发

762172 的[世界状态研究 EXP-WORLD-001](../knowledge/research/native-mechanisms/world_shard-452de4ff6dd7.json)表明，地表 `phasechanged` handler 依次处理 phase、isday、isdusk、isnight 和月相布尔值；每个键的新值非 nil 且与旧值不同时，写入后立即派发。读取组合状态的监听者应按实际键与派发时点判断，不能把一次 phasechanged 当成全部派生字段已更新。

派发中 `RemoveWatcher` 修改原数组，整宿主 `StopAll` 删除组映射；二者对已进入的派发影响不同。不要套用 EntityScript 事件快照的解绑语义。

## Replica 存在、可见、附着与退出分别审查

| 入口 | 冻结源码的关键边界 | 工程含义 |
|---|---|---|
| 全局 ReplicateEntity(guid) | 缺 GUID 无 nil 保护；seamless 目标临时改 ThePlayer，只在保存旧值 truthy 时恢复，异常无恢复保护 | 不把它作为通用手动刷新入口 |
| EntityScript:ReplicateEntity() | pairs 选取注册标签，正常完成后调用 OnEntityReplicated；重复执行没有幂等门 | 后置回调不能当跨实体或全部字段 ready 屏障 |
| ReplicateComponent(name) | master 的 __ 标签分支复用并早退；其余已有 raw 对象只警告后仍构造替换；先构造再写 raw | 重放可能遗留旧对象资源；构造期间不能保证实际 component 已写入 |
| UnreplicateComponent(name) | master 且有 raw 对象时改标签；不删除底层对象、不调用其卸载钩子 | 公有访问消失不等于资源析构，完整实体 Remove 仍遍历 raw replica |
| TryAttachClassifiedToReplicaComponent(classified,name) | 直接查 raw；存在时调用 AttachClassified，正常返回即 true，丢弃 callee 返回值；异常不转 false | true 不是业务成功或数据 fresh；pending 与重试由具体调用者负责 |

上述事实见 EL-S09–18。container 的 pending 保存/消费和槽初始化异常边界继续复用 EXP-ARCH-004；本批只绑定它们作为 helper 的 caller/callee/cleanup。raw 容器是机制证据，不是推荐的常规 Mod 读写入口。NC-N002-FINAL-04 与 AI-N001-10 的分层视图结论及原 Scope 保持原样。

复制重放、构造/Attach 异常、seamless swap 与原生到达顺序仍需运行验证；当前具名服务器事件覆盖见[阶段 9](../docs/phase9-action-closure.md)。按具体消费者判断就绪与重试条件。
