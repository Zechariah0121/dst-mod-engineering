# 事件、生命周期与存档恢复

开发候选 `v2026.11.06.1`：240 条登记知识，其中 53 条机制研究；尚未公开发行。

- 适配 **762172 热修**，按具体引用维护源码变化，让知识库在游戏更新后继续提供有明确来源的研究。
- 新增 **9 条研究、24 个 API 契约**，补齐事件解绑、Replica 构造与附着、组件卸载、任务取消、GUID 接线和保存回调边界。
- 新增 **3 篇架构接入参考**，帮助 AI 把模块职责落实到资源归属、退出清理与读档恢复，减少重复监听、残留任务和恢复时重复触发副作用。

| 研究入口 | 用途 | 应用参考 |
|---|---|---|
| EXP-LIFE-001～003 | 订阅函数身份、整实体事件清理、Replica 重放与附着返回值 | [事件与 Replica](../references/event-replica-lifecycle.md) |
| EXP-LIFE-005～007 | 组件安装/卸载、更新停止、任务句柄与 SaltLicker 资源闭环 | [组件与任务归属](../references/component-task-ownership.md) |
| EXP-SAVE-001～003 | 旧 GUID 映射、嵌套 postpass、鱼人房屋三态恢复、保存委托 | [保存与恢复架构](../references/save-recovery-architecture.md) |

先从[复杂 Mod 架构指南](../references/complex-mod-architecture.md)确定职责，再按问题进入上表。专题是有条件的工程建议；研究保留 `research/restricted/hold`，不会自动进入 Coding 默认上下文。

## API 查询

`lookup_api` 显式使用 `family="native_mechanism"`、`projection="reviewer"`。例如查询 `EntityScript:ListenForEvent`、`EntityScript:RemoveEventCallback`、`EntityScript:ReplicateEntity`；较大契约可显式提高 `max_bytes`，上限 64000。完整参数与预算见[研究族说明](native-mechanisms.md)。

全局 `ReplicateEntity` 与实体方法不同，按符号和 `source_file` 消歧。`onload`、`HN_OnLoadPostPass` 是 `scripts/prefabs/mermhouse.lua` 的局部函数：可研究其完整契约，不能据此当成 Mod 的公共调用入口。

查到 Replica 不证明 classified、数据和 HUD 都已就绪；取消任务不撤回正在执行的 Lua 调用；完成 OnSave 不证明磁盘写入完成。这些判断仍需连同具体调用者、消费者和退出路径读取。源码身份与热修影响见[762172 适配记录](version-762172.md)；本阶段没有游戏运行验证，历史知识正文和 Scope 保持不变。
