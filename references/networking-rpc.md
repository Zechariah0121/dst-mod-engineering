# 联机权威、Replica 与 RPC

适用：自定义数值、技能请求、HUD 数据、后加入同步、跨世界消息。先读本篇，再按涉及的退出/读档行为读 [lifecycle-save.md](lifecycle-save.md)。本篇按 2026-09-27 核验环境的游戏 Lua 源码核验，基线见 [environment-tools.md](environment-tools.md)；网络传输实现部分在引擎中，源码追踪不能替代远端客户端测试。

## 先画状态归属表

为状态写出：谁决定、谁读取、变化频率、初始同步、是否存档、退出如何解除。

| 需求 | 通常入口 | 不能据此推断 |
|---|---|---|
| 服务端计算血量、消耗、掉落 | 服务端 Component | 客户端也有同名 Component |
| 两端共享瞄准或轮盘逻辑 | 原版明确放在公共区的组件 | 所有 AddComponent 都只能放服务端 |
| 小型持续状态 | 类型合适的 netvar；需要接口时封装 Replica | 一次 dirty 能覆盖后来加入、HUD 重建 |
| 客户端申请行为 | 原版动作链，必要时 Mod RPC | 客户端传来的状态已经可信 |
| 一次性音效/表现 | net_event 或 Client RPC | 这是可恢复的状态 |
| 地表/洞穴通信 | Shard RPC、现有 shard 组件 | 客户端 RPC 自动跨 shard |

`inst.components.X` 和 `inst.replica.X` 的方法分别核对对应文件；扫描器不能把两个方法集合并。部分 Component 本来就在两端，不能用“客户端没有 components”概括。服务端 Lua 事件默认只在当前进程分发；只有原版或 Mod 显式复制后，另一端才有相应变化。

## netvar 与 Replica 的初始化

普通网络 prefab：`AddNetwork()` → 两端一致的直接 netvar/必要标签/公共组件 → `SetPristine()` → 非主模拟返回 → 服务端逻辑。`SetPristine` 不是一条“此后任何 netvar/组件/本地视觉都禁止”的规则。

自定义 Replica 在实体生成前用 `AddReplicableComponent("组件名")` 注册，文件为 `scripts/components/组件名_replica.lua`。当前 `EntityScript:AddComponent` 先 `ReplicateComponent(name)`，再构造服务器 Component，因此 Replica 内的 netvar 可以随服务端添加已注册组件而建立。参考 `entityscript.lua:AddComponent`、`entityreplica.lua:ReplicateComponent/ReplicateEntity`；不要因此在任意延迟任务里随便添加裸 netvar。

- 声明顺序、名称、类型必须在各端一致；不要按主客机条件跳过某个裸 netvar。
- `value()` 读；服务端 `set(v)` 同步。值变化的 dirty 事件会在服务端和客户端触发。
- `set_local(v)` 不同步、不触发 dirty；会令随后服务端 `set` 强制产生 dirty。只在了解原版预测/重复事件范式时使用。
- 同值 `set` 一般不触发 dirty。绑定 HUD、`OnEntityReplicated`、玩家激活/目标更换时主动读当前值；不是每个徽章都必须加每帧轮询。
- `net_string` 接收字符串，不能把 Lua table 直接 `set` 给它。数值和枚举用匹配类型；小结构优先拆字段，确需序列化时限制大小、频率和解码后的 schema。
- `net_entity` 保存实体引用，不是把 GUID 当作跨端通用 ID。未复制或已移除目标需要 nil 分支。
- `net_event` 用于瞬时通知；持续夜视、形态或激活状态用可重建的 netvar。

位宽以当前 `netvars.lua` 为准：tinybyte 0–7、smallbyte 0–63、byte 0–255、ushortint 0–65535；shortint -32767–32767、int -2147483647–2147483647；数组有长度及元素范围限制（当前 bytearray/smallbytearray/ushortarray 最大 31）。别把字符串当作所有类型的万能替代。

## RPC 注册与签名

同一 RPC 的注册名及顺序在参与端一致。ID 由当前命名空间中的注册次序产生；不要把注册本身放进不一致的主客机分支。回调执行时再检查运行环境。

| 方向 | 注册 | 发送 | 回调的隐式参数 |
|---|---|---|---|
| 客户端→服务器 | `AddModRPCHandler(ns, name, fn)` | `SendModRPCToServer(GetModRPC(ns, name), ...)` | 通常第一个是请求玩家；特殊 userid RPC 另查原版 |
| 服务器→客户端 | `AddClientModRPCHandler(ns, name, fn)` | `SendModRPCToClient(GetClientModRPC(ns, name), userid, ...)` | 只有显式 payload；收件 userid 不变成 player 参数 |
| shard→shard | `AddShardModRPCHandler(ns, name, fn)` | `SendModRPCToShard(GetShardModRPC(ns, name), shardid, ...)` | 发送 shard 标识，再接 payload |

发送给单个玩家时使用其有效 `userid`。不要把这个常用用法概括成“所有 Client RPC 第二参只能是单个 userid”，群发形态应另查当前引擎契约。`MOD_RPC` 等旧表仍存在，但 `modutil.lua` 注释推荐 `GetModRPC/GetClientModRPC/GetShardModRPC`。

namespace 来自注册时传入的字符串；只有选用 `modname` 时才随实际 Mod 目录名改变。测试副本改目录时要检查调用方使用的 namespace，不能无条件写“namespace 就是文件夹名”。

短例子（只展示签名，不是完整玩法）：

```lua
local NS = "my_mod"
AddClientModRPCHandler(NS, "notice", function(message)
    if type(message) ~= "string" then return end
    -- 本地提示应另判 ThePlayer/HUD 是否已建立。
end)
-- 服务端已有合法 player 时：
-- SendModRPCToClient(GetClientModRPC(NS, "notice"), player.userid, "完成")
```

不要照教程承诺任意 table/function 可直接跨网络传输。Lua 包装层把参数交给 TheNet，无法由“函数接受 ...”证明序列化支持。使用原版有例证的简单值/网络实体；结构数据显式编码后仍要检验长度和解码 schema。完整支持类型若无当前文档或引擎实验，标记待验证。

## 服务端必须重新验请求

先查类型，再索引实体；数值先查有限性（`n == n` 排除 NaN、排除正负无穷）、范围和整数/枚举要求。随后按行为检查：请求玩家有效且允许操作、目标与物品有效、距离、持有权、平台坐标、PvP/权限、资源、冷却、重复请求。只在成功路径扣费/生成；失败返回明确结果。引擎总 RPC 限流不替代技能自身冷却或防重入。

客户端只传意图，不能让其自由指定要生成的 prefab、伤害、消耗、世界时间倍率或受控玩家。世界管理 RPC 必须校验服务端授予的管理权限。客户端按键门禁只是体验层，不能作为服务器授权依据。

刚发 RPC 不立即读 Replica 当返回值；用结果事件/状态变化更新 UI。刚生成的实体可能尚未复制，固定延时不构成可靠确认。旧请求抵达时目标已删除、切 shard、死亡、丢物，都必须可拒绝。

## 最小验证与检索

静态检查两端声明及调用签名；契约测试检查 handler 输入、拒绝路径和一次扣费；专服检查实际权威组件；最后用真实远端客户端覆盖正常请求、恶意/过期参数、延迟、重连、后来加入及按需跨 shard。直接在 Lua 中调用 handler 不证明 RPC 传输、实体映射或 UI。

当前源码检索入口（相对已核对的 scripts 根目录）：

- `netvars.lua:29-79`：声明一致、dirty 双端、set_local、状态与事件。
- `entityscript.lua:610-645`；`entityreplica.lua:34-83`：主组件/Replica 构造及复制回调。
- `networkclientrpc.lua:1725-1768,1834-1977`：队列、签名、注册 ID、namespace、发送封装。
- `modutil.lua:852-916`：Mod API 注入和 legacy 表说明。
- `prefabs/player_classified.lua:815-823,1208,1314`：dirty 加初始同步的原版例子。
