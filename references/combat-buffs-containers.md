# 战斗、Buff、容器与冷却

适用：范围攻击、位面伤害、击退、附加属性、料理 Buff、物品冷却和自定义容器。数值与玩法先按项目约定；本篇提供机制选择和核验路径，不替项目决定倍率/半径/死亡政策。

## 范围伤害和位面伤害

原版已有 `combat:DoAreaAttack(target, range, weapon, validfn, stimuli, excludetags, onlyontarget)`。它排除普通范围分支中的主目标和攻击者，检查目标、发 `onareaattackother`、通过 `CalcDamage` 同时取得普通及特殊伤害并调用 `GetAttacked`。现成路径符合需求时优先复用；自定义形状须保留完整结算链。

教程火腿棒例子直接替换 `weapon.onattack`、硬编码满新鲜伤害且遗漏特殊伤害；不能当可直接复用模板。叠加效果应保存原回调并按正确签名调用，检查空 target、目标有效性和组件。`IsValidTarget` 也不自动表达设计上的“不伤盟友/随从/同类”；将 PvP、阵营、随从、主目标重复伤害明确列入筛选。

自定义攻击不要为省事直接 `health:DoDelta(-damage)` 绕过护甲、位面防御、受击事件、仇恨和击杀归属。`planardamage` 提供基础值和来源倍率/加值，不提供 `DoDelta`；设置 weapon/projectile 的 planardamage，由 `SpDamageUtil` 与 combat 结算。已有 projectile/aoeweapon 命中流程后又手动伤害可能重复扣血。

`damagetypebonus:AddBonus(tag, source, multiplier, key)` 的参数是乘数：1 无增伤，2 才表示增加 100%。目标 tag 须查 prefab 的真实标签，不把显示阵营名或另一个 Mod 的 tag 当原版通用规范。位面伤害仍会经过位面防御，不能描述成无条件真实伤害。

冲刺优先查当前 `prefabs/spear_wathgrithr.lua`、`components/aoeweapon_lunge.lua` 及基类。reticule 的回调配置位置按原版 `aoetargeting.reticule` 核对；`aoespell` 回调顺序为 item、doer、pos。命中回调只补额外行为，不未经核对再次结算完整伤害。

## 击退、睡眠与飞行不是单行开关

`target:PushEvent("knockback", {knocker=source, radius=..., strengthmult=...})` 需要目标状态机支持。radius 参与按距离计算推力，不是会搜索所有目标的 AOE 半径；不要照抄 200。保留攻击原回调，按服务端与目标类型添加，验重型、骑乘、平台、死亡和碰撞。

`heavybody` 的行为取决于对应状态机，不能承诺完全免疫。仅屏蔽 `yawn` 不会覆盖直接 `grogginess:AddGrogginess`、`knockedout` 和其他睡眠路径。当前 grogginess 有按来源免疫接口，优先查 `AddImmunitySource/RemoveImmunitySource`；仍需定义要免疫的是昏睡、哈欠、减速还是所有睡眠。不要为“霸体”全局吞掉角色所有 SG 事件。

教程飞行只提供旧实现思路：强行改 y 速度、清碰撞、把 drownable.enabled 写 false，缺保存/死亡/取消/睡眠清理，延迟云可能在落地后生成，客户端预测也未证明。保留作审查反例；新机制先查原版可比形态、状态/碰撞/骑乘与溺水接口，明确跨地形能力，完整列出退出恢复及网络策略后再实现。纯视觉悬浮通常用动画/FX，不必改变玩法物理。

## 附近玩家触发的悬浮

天体宝球 `moonrockseed` 的动画/光效可作视觉参考，但 `prototyper` 承担科技站选择；即使 trees 为空也可能占据玩家当前科技站位置，不适合为了纯装饰随意添加。`builder:EvaluateTechTrees` 只查当前研究距离，旧文“全图最近”是错误表述。

纯靠近/远离效果先查 `playerprox` 的 AnyPlayer 模式和 `SetDist(near, far)`，利用迟滞避免边缘抖动；有复杂目标筛选再做受控周期查询，避免每件物品每帧扫描。捡起/落地事件按真实 inventoryitem 推送名核对，`ondropped` 不是被捡起。光效淡入淡出任务仅在过渡时运行，达目标即停；视觉状态按客户端可见性设计。

## 可刷新的 Buff

优先使用 `debuffable:AddDebuff(name, prefab, data)` + Buff prefab 的 `debuff`/`timer`。同 name 再施加调用 Extend，附加/延期/解除分别为 `SetAttachedFn/SetExtendedFn/SetDetachedFn`。普通食物 Buff 可以非网络服务端 prefab；需要客户端夜视/滤镜/标志时，另设计复制状态或网络表现实体，不能只设置服务器 playervision。

每个 Buff 写清：来源标识、应用和移除、重复是叠层还是刷新、到期、死亡、despawn、重启、外部删除。原版 foodbuffs 默认监听 death 停止，仅是其规则。用户要求死亡继续计时就调整本机制所有出口，不能只删除一个地方又在 ghost 回调重置。

用来源列表维护属性，例子（运行于已验证 target 的服务端）：

```lua
-- source 是本 Buff 实体，key 为本机制私有键；MULT 由设计提供。
target.components.combat.externaldamagemultipliers:SetModifier(source, MULT, "my_buff")
-- 正常解除及必要的异常出口：
target.components.combat.externaldamagemultipliers:RemoveModifier(source, "my_buff")
```

实体 source 在其移除时有 SourceModifierList 自动清理，但提前解除仍应主动移除；字符串 source 没有实体 onremove 自动清理。速度用 `SetExternalSpeedMultiplier/RemoveExternalSpeedMultiplier`。不把当前值除回倍率、直接改回 1 或清空整个列表。

夜视用 `playervision:PushForcedNightVision(source, ...)/PopForcedNightVision(source)`；在本地玩家建立和网络目标可用后施加，目标改变时先撤旧来源，实例被外部删除时也清理。显示保护 goggles 等不同系统可能是共享标量，不能用单个布尔擅自覆盖其他 Mod；能力已是多来源 API 时直接复用。

计时器存在不代表效果仍存在：外部移除网络 Buff 后，宿主残留 task/引用可能使再次施加只刷新到期而不重新应用。用幂等 Ensure/Apply 路径同时核查实体、来源与任务，或在其 onremove 清空缓存。重连/初次复制不能仅等 dirty。

## 冷却组件

使用游戏自带 `rechargeable`，不携带教程的同名旧组件覆盖原版。`Discharge(seconds)` 开始充能，`IsCharged()` 校验当前状态；需要时用 `SetOnChargedFn/SetOnDischargedFn` 配合 aoetargeting 显示。

背包进度显示不是禁止使用。服务端行为执行前必须检查 charged，失败不能刷新/扣费；成功后再放电。包装 spellcaster/spellfn 保留全部参数与返回值，不能不管原法术失败就进入冷却。组件原有 OnSave/OnLoad 保存剩余进度；需测试旧档、读档重复初始化和特殊冷却政策。

## 容器

在双方加载的代码中注册私有 `containers.params[widget_name]`，复用合适的原版 UI，明确 numslots/slotpos、type、itemtestfn。服务端添加 container、`WidgetSetup`；客户端确保 Replica 使用相同配置，先查看 `container_replica` 是否按 prefab 自动初始化，只有名称不同/特殊生命周期时按原版 OnEntityReplicated 模式补一次，不能一概要求重复设置。

`openlimit` 控制**同一容器实例同时有多少打开者**，不是全世界同类型只能打开几个。Widget 的 pos 是 UI 布局参数，不是容器实体世界坐标。参数在 require 后追加时，确认 MAXITEMSLOTS 对该容器槽数足够；不缩小其他 Mod 已扩大的值。

权限在服务端检查，itemtestfn 应兼容实际调用方数据；防自嵌套/循环嵌套并确认装备容器、打包容器和物品归还路径。给宠物加容器不能只监听 death：召回、收起、变身、despawn、移除、断线、重启分别决定掉落/转移/保存，防物品丢失或复制。不要擅改原版同名 params 影响其他实体。

`stackable.maxsize` 是主组件属性（有 setter），不是主组件 `SetMaxSize` 方法。当前 Replica 的最大堆叠档位表与数量编码是两个限制：档位使用 TUNING 五项，实际数量用两个 6-bit 字段，不能把最大默认档位 120 说成网络数量上限。任意 maxsize 仍可能因档位查不到而崩。不要将“全局占用 code=5”作为安全通用补丁，其他 Mod 可能使用同一编码；优先使用原版档位，自定义协议需双方一致及组合兼容验证。

## Mod 兼容检测

按用户指定的稳定 Mod ID 精确比较适当的启用列表/当前 ModManager 状态；显示名可能变化，本地目录与 workshop ID 也不同。教程 `string.match(name)` 同时匹配目录和显示名会出现 Lua 模式注入/子串误判，不能用作能力判定。优先检查所需 API 能力，只有具体已知冲突才按 ID 走适配；检查时机要在目标 Mod 完成加载之后。

## 当前源码检索入口与验证

- `components/combat.lua:CalcDamage/DoAreaAttack/GetAttacked`；`components/aoeweapon_base.lua:OnHit`；`components/weapon.lua:GetDamage`；`components/spdamageutil.lua`。
- `components/planardamage.lua`；`components/damagetypebonus.lua:AddBonus/GetBonus`：数值语义。
- `stategraphs/SGwilson.lua:knockback/knockedout/yawn`；`components/grogginess.lua:AddGrogginess/AddImmunitySource/RemoveImmunitySource`。
- `prefabs/foodbuffs.lua:150-208`；`components/debuffable.lua:95-149`；`util/sourcemodifierlist.lua:64-121`；`components/playervision.lua:226-261`。
- `components/rechargeable.lua:108-174`；`components/container.lua:86-96,728-736`；`components/container_replica.lua`；`containers.lua:widgetsetup`。
- `components/stackable_replica.lua:1-9,24-35,47-63,98-111`；`modindex.lua:GetModsToLoad/IsModEnabled`；`mods.lua:GetEnabledModNames`。
- `prefabs/moonrockseed.lua`；`components/builder.lua:235-301`；`components/playerprox.lua:44-59,165-180`：科技选择与纯邻近触发。

伤害测试需比较普通/位面/护甲/PvP、主目标不重复、范围边缘和叠加来源；Buff 测重复/到期/移除/死亡/读档；容器测多人打开、转移、召回与磁盘重启。网络展示、真实玩家输入和第三方 Mod 组合另做客户端验收。
