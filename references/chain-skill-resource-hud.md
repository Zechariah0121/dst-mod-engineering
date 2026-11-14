# 背包技能、玩家资源与本地 HUD

这个可运行示例从主背包格右键发动 **Pulse Stone**，在服务器长动作执行点放出一团原版烟雾并扣除角色资源。本地 HUD 显示同一角色的余额。示例设定为上限 12、每次扣 4、无自动恢复，数值仅用于复现。组件把余额写入角色保存记录，真人会话恢复仍待验证。死亡进入幽灵模式时隐藏 HUD，复活后读取原余额。范围限普通 Wilson 人形状态、主背包格、没有活动物品及修饰键的鼠标右键。

- [完整示例 Mod](../examples/stage4-skill-resource-hud/)

## 从点击到扣费

| 阶段 | 本例沿用的入口 | 验收时观察 |
|---|---|---|
| 鼠标输入 | `InvSlot:OnControl` → `InvSlot:UseItem` → inventory Replica | 主背包格右键按下触发。Tooltip 里显示动作名称与实际发请求是两个调用路径。 |
| 动作选择 | `GetInventoryActions` → `CollectActions("INVENTORY")` → 排序、过滤并构造 BufferedAction | 候选函数通过 Replica 只接受示例石头与主背包格。石头没有吃、装备或施法书等竞争候选。 |
| 远端请求 | `inventory_classified` → `RemoteUseItemFromInvTile` → 原版 RPC | 有 locomotor 且通过原版预测门禁时，`wilson_client.dolongaction` 先预演，再由 `preview_cb` 发请求。无 locomotor 时，本例走直接发送分支。两条路径均由服务器结算。 |
| 权威接收 | RPC → `inventory:UseItemFromInvTile` → 重收候选 → 匹配 code / mod_name | 原版 `CanAccessItem` 也允许打开的可写容器。示例在执行点另外确认石头仍在玩家自己的主背包格。 |
| 执行或取消 | `wilson.dolongaction` 默认一秒超时 → `PerformBufferedAction` → `BufferedAction:Do` → `S4HUD_PULSE.fn` | 余额不足时 Action 返回 `false, "NOCHARGE"`。若在服务器提交前切态并清掉当前缓冲，烟雾和扣费都不会发生。 |
| 提交 | 当前 Action 实例、玩家存活、未骑乘、实际持有者、槽位和余额都有效 → 生成并定位 `small_puff` → 标记已提交、扣费一次 | 已提交的同一缓冲对象无法再次扣费。不同的成功点击各自收费。烟雾动画、声音与生命周期由原版 FX 管理。 |

前一阶段黄杖的 `CASTSPELL` 是另一条地面空点链。其 `SpellCaster` 回调返回值无法将原版 Action 改为失败。本例的扣费拒绝由自定义 `Action.fn` 返回，沿用原版库存格消息与长动作。

[入口、注册和执行点](../examples/stage4-skill-resource-hud/modmain.lua) · [扣费与保存](../examples/stage4-skill-resource-hud/scripts/components/s4hud_charge.lua)

## 余额怎么到 HUD

服务器在玩家 PostInit 加组件。组件生成独立的 `CLASSIFIED` 子实体，将目标先指向分类实体自身，在玩家 `setowner` 时定向到玩家。已分配 userid 的装配路径直接定向。字段在自有 Prefab 的 `SetPristine` 之前由两端同序声明。这采用了原版 inventory/player classified 的具名父实体及定向做法。

- 服务器组件存整数 `0..12`，用一个 `net_smallbyte` 投影 `余额 + 1`。编码 0 代表未就绪。真实余额 0 编码为 1，可以独立显示。示例上限固定，由两端共享 Lua 配置。
- 客户端分类实体的 `OnEntityReplicated` 读原生 parent，挂接到对应玩家后发本地更新事件。字段变化用 dirty 通知同一个玩家。旧实体退出只清除自己仍持有的引用，避免覆盖新实例的快照。没有 parent 时本示例保持未就绪，沿用原版具名路径的附着边界。
- 每个 `Controls` 实例向自己的 `top_root` 加一行 Text，先让文本实体订阅玩家事件，再立即读取当前值。联机主机可以从本地权威组件读取。HUD 先建时显示 `Charge: ...`，收到附着或 dirty 后重读。若分类实体先到，新 HUD 会直接显示当前值。
- 初始幽灵状态从原版玩家 classified 读取，缺失时用玩家标签。后续 `Controls:SetGhostMode` 调用会刷新显示。关闭 HUD 时，`PlayerHud` 销毁子树，文本实例随 `Widget:Kill` 移除，事件订阅随实体清理。新 Controls 自己订阅并读取，旧文本实例无法继续更新。换角与无缝替身的余额转移仍需另行定义。
- `OnSave` 只保存 `{ current = ... }`。`OnLoad` 校验数字有限并取整、钳位，再同步字段。旧档缺字段时保留组件初值。分类实体自身不写盘，读档时由组件重建。第三方 spawn hook 同步清槽时，示例复验后移除试建 FX 并拒绝收费。第三方回调抛错不属于事务保证，已发生的副作用不会自动撤回。

[分类实体](../examples/stage4-skill-resource-hud/scripts/prefabs/s4hud_charge_classified.lua) · [本地文本控件](../examples/stage4-skill-resource-hud/scripts/s4hud_hud.lua)

## 原版来源和已知边界

来源为安装归档 `762172`（Steam build `26474873`），`scripts.zip` SHA256 `733a0f7f97ace5a76aa5acee95405a6ec01697d93d844eeb4ecce7c001306980`。

- 鼠标输入和服务器重建位于 `widgets/invslot.lua:10–61,396–403`、`components/inventory_replica.lua:482–490`、`prefabs/inventory_classified.lua:901–922`、`components/playercontroller.lua:5565–5586,5753–5766`、`networkclientrpc.lua:725–740`、`components/inventory.lua:2259–2303`。
- 动作提交和取消位于 `stategraphs/SGwilson_client.lua:3184–3233`、`stategraphs/SGwilson.lua:8359–8429`、`entityscript.lua:1588–1593,1679–1712` 与 `bufferedaction.lua:22–50`。
- 附着、Ghost 和销毁位于 `components/inventory_replica.lua:9–34,145–161`、`prefabs/inventory_classified.lua:79–87`、`prefabs/player_common.lua:955–964,1001–1017`、`prefabs/player_classified.lua:247–262,815–822,1305–1339`、`screens/playerhud.lua:928–962`、`widgets/widget.lua:291–334`、`entityscript.lua:1730–1747`。
- 玩家保存链位于 `networking.lua:303–320`、`entityscript.lua:308–316,1928–1947,1979–2014`、`mainfunctions.lua:2101–2107`。机制记录 `EXP-CHAIN-SKILL-HUD-001` 按文件及范围保留哈希，三轴为 `research/restricted/hold`。历史 `EXP-CHAIN-SPELL-001`、`EXP-ACT-001/002`、`EXP-UI-003`、`EXP-LIFE-001`、`N005-UI-C02` 和 `EXP-WORLD-003` 继续适用各自 Scope。

## 本机验证与复现

Lua 5.1 编译检查通过。替身检查执行实际示例 Lua，覆盖正常扣费、重复与取消、余额不足、所有权、生成失败、同步回调取消、保存读回，以及 HUD 就绪、零值、dirty、幽灵、销毁后重建和分类实体替换。替身的 Entity、netvar 和 Widget 由测试提供。

Windows 隔离专服实际通过 `Inventory:UseItemFromInvTile`、服务器候选、长动作执行、扣费与失败断言。测试用无真人连接的 Wilson，补装 picker/controller，从服务器入口传动作 code 与 mod_name。另一个独立进程用同一世界档读回测试夹具余额 5，服务器新分类实体编码值为 6。该测试临时令无 userid 的 Wilson 参与世界存档，真人玩家 session 的保存和重连仍待验证。

专服和离线夹具保存在研究工作区。下节可用公开示例独立复现客户端用例。

## 客户端手动验收

实际鼠标输入、远端复制和画面尚未运行。使用全新单分片隔离世界，两台客户端启用相同示例 Mod，选 Wilson。用一块燧石在 Mods 制作分类合成 Pulse Stone，或在该隔离世界的服务器控制台向测试角色生成 `s4hud_pulse_stone`。

1. 检查首次加入显示 `12 / 12`。把石头放主背包普通格，清空鼠标活动物品，无修饰键右击一次。起手期间余额保持 12，长动作完成后恰好显示 `8 / 12` 并出现一团烟雾。分别在开启和关闭移动预测时重复。
2. 起手后在一秒窗口内用方向键移动，确认服务器确实转态且清槽。本次无烟雾或扣费。连续三次成功后观察 `0 / 12`，再尝试一次并确认余额和烟雾不变。
3. 同场另一玩家的 HUD 余额应保持自己的数值。请在非 owner 客户端的本地控制台核对另一玩家实体的 `_s4hud_classified` 未附着，切换到 owner 客户端确认其 `ThePlayer._s4hud_classified` 已附着。两者必须查看各自客户端的本地 Lua 环境。
4. 保留同一角色，记下非初始余额，死亡成幽灵后文字隐藏，复活显示原余额。正常离开后重新加入，再重启隔离服务器后加入，分别观察新 HUD 首次显示最新余额。每次重建应只有一行文字，后续每次成功均更新当前 HUD。记录实际客户端日志、端别、预测开关、是否观察到未就绪占位，以及真人角色恢复结果。
