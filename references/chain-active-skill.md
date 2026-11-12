# 黄杖普通地面施法完整链

## 读取范围与顺序

本篇适用于开发或审查“手持法杖、地面选点、起手可中断、服务器执行帧提交”的有限主动技能。具名原版样本为 `yellowstaff` 的普通鼠标地面空点 `CASTSPELL`，无活动物品和其他右键覆盖。来源为冻结归档 `762172`，ZIP SHA256 为 `733a0f7f97ace5a76aa5acee95405a6ec01697d93d844eeb4ecce7c001306980`，已与本次安装的游戏归档核对一致。研究登记保持 `runtime_verified=false`；末节分别列出静态、替身与有限专服验证。

1. 先确认本次玩法契约与服务器结算，再读可取消动作的接入流程。[法术与自定义数值](spells-and-custom-stats.md) · [动作接入](action-lifecycle-architecture.md)
2. 从目录按 `file` 和 `pointer` 读取 `EXP-ACT-001`、`EXP-ACT-002`、`EXP-ACT-003`，用于定位通用预演、权威执行和重入问题。普通 PICK 的具名 Scope 继续保留，右键施法的实际差异沿本篇来源核对。[知识目录](../knowledge/CATALOG.json)
3. 本轮新增 `EXP-CHAIN-SPELL-001`，完整读取其 Scope、claims、两个 `SpellCaster` API、步骤与 unknowns。三轴状态保持 `research/restricted/hold`，这些 ID 用于 Reviewer 研究导航。
4. 涉及耗尽移除、星体恢复时补读 `EXP-LIFE-008`、`EXP-SAVE-004`、`EXP-GEAR-002`。仍按原 ID 的具名消费者、来源和边界使用。[组件与任务归属](component-task-ownership.md) · [保存恢复](save-recovery-architecture.md)
5. 接入实际 Mod 前，独立核对目标源码及项目约定的持有权、费用、距离、取消、死亡、保存与冷却政策。研究登记本身没有授予 Coding 准入。[读取与准入](kb-retrieval.md)

## 从右键到执行帧

| 阶段 | 实际调用与所有者 | 本 Scope 的结果 |
|---|---|---|
| 构造 | `staff.lua` 的 `commonfn` / `yellow`，`staff_common.lua` 的 `fns.yellow_client` / `fns.yellow` | 两端有 reticule，权威 spellcaster、次数、库存与装备组件在 master 分支。 |
| 候选 | `playeractionpicker:GetRightClickActions` → `GetPointActions` → `POINT.spellcaster` → `SortActionList` | 从手装备、资格标签与地图条件收集 `CASTSPELL`，生成带物品/位置的 BufferedAction。 |
| 输入 | controller 缓存 `RMBaction`，SECONDARY → `OnRightClick` | 预测路径在 `preview_cb` 发完整请求，无 locomotor 路径使用 `non_preview_cb`。全 nil 请求只报告控制按下。 |
| 客户端预演 | `SGwilson_client.castspell` | `PerformPreviewBufferedAction` 发送请求并等待状态，超时清动作。此处没有权威效果写入。 |
| master 接收 | `RightClick` RPC → `OnRemoteRightClick` | 验消息/坐标边界，重新收集候选并匹配动作 code/mod_name 后 `DoAction`。 |
| 服务器起手 | `SGwilson.castspell` | 暂停移动与 controller，持有本态 FX/灯。第53帧 `PerformBufferedAction`。 |
| 结算 | `ACTIONS.CASTSPELL.fn` → `CanCast` → `CastSpell` → file-local `createlight` | 执行帧复验，生成独立 `stafflight`，消费次数，后置读取 owner 处理理智。 |
| 退出 | SG statemem、法杖 finiteuses、星体 timer 各自持有资源 | 本态表现、耗尽法杖与独立星体各走自己的退出。 |
| 恢复 | finiteuses 与星体 timer 的保存数据 | 恢复次数和剩余计时，无需重放点击或重新扣费。 |

定位分别为 `scripts/prefabs/staff.lua:13–124,204–229`，`scripts/prefabs/staff_common.lua:788–853`，`scripts/componentactions.lua:2193–2222`，`scripts/components/playeractionpicker.lua:84–107,207–223,388–489`，`scripts/components/playercontroller.lua:4981–5123`，`scripts/networkclientrpc.lua:113–161`，`scripts/actions.lua:3441–3473`，`scripts/stategraphs/SGwilson.lua:16170–16287`，`scripts/stategraphs/SGwilson_client.lua:4045–4073`。逐文件原字节 hash 和 UTF-8 splitlines/LF 无尾换行范围 hash，可按目录定位 `EXP-CHAIN-SPELL-001` 所属文档的 `source_references` 读取。[知识目录](../knowledge/CATALOG.json)

## 成功、拒绝与取消

- `ACTIONS.CASTSPELL.fn` 在调用 `CastSpell` 正常返回后独立返回 true。`SpellCaster:CastSpell` 忽略 spell 回调的返回值，继续调用 `onspellcast` 并推同名事件。回调返回 false 无法把该原版 Action 改为失败。回调抛错会中止该 Lua 栈后续阶段，已写入的副作用保留。
- `CanCast` 的黄杖点分支检查 spell、可选施法类型与自定义资格、地图可用和阻挡。持有权检查还涉及 BufferedAction 创建时是否记录 `doerownsobject` 与最终 `IsValid`。需要的资源、权限、距离和冷却必须逐项追实际消费者。
- 第53帧前转态且不再执行该帧时，本次 `createlight` 尚未运行。服务器 `castspell.onexit` 恢复 controller，移除仍持有的表现引用。本状态没有声明统一清动作槽或退款。具体哪些输入、受击或死亡实际触发转态，仍需对应角色与游戏验证。
- 第53帧先清 SG 的 stafffx/stafflight 取消引用，随后执行业务。释放引用后的 `staffcastfx` 由动画结束移除，`staff_castinglight` 由自身任务结束后延迟移除。后续切态不会撤销独立星体或恢复已消费资源。
- 松开右键的所选入口只释放控制位，预演超时、松键与服务器业务拒绝各有自己的阶段证据。

## 末次次数与状态所有者

`createlight` 的顺序为生成星体、定位、`finiteuses:Use(1)`、读取 `inventoryitem.owner`、处理理智。普通装备黄杖最后一次会同步走 finiteuses 的 onfinished、法杖 Remove、inventoryitem 的移除钩子、inventory 的 equipslots 移除、`OnRemoved` 与 `ClearOwner`。这些钩子正常返回时，后置 owner 可已经为 nil，从而跳过该次理智分支。Lua 替身核对了实际 frozen spellcaster、Action、finiteuses、owner 清理方法体，外层实体移除与原生接口使用替身。

这个差异由副作用顺序决定。自有功能的收费对象、先后顺序和末次是否收费应按项目政策明确。读取组件方法名或把 doer 传给原版 CastSpell 不能改变 `createlight` 实际读取 owner 的方式。

## 星体退出与保存

`stafflight` 独立拥有网络灯、pulse 任务、热/理智组件与 `extinguish` timer。timer 到期先停止并清自己的 timer 项，再发 `timerdone`。星体回调进入 `kill_light`，推 `onstarkilled`、播放退出动画、在 `animover` 停循环声、安排1秒后移除，并立即置 `persists=false`。`ForceExtinguish` 在 timer 存在时走同一退出。宿主移除的普通监听/任务释放沿 `EXP-LIFE-008` 的有限合同核对。

黄杖次数由 finiteuses 保存，满次数可以不写 uses。星体由构造重新装配效果与 timer，再由 Timer 加载逐名停止构造计时并按保存的 timeleft/paused/initial_time 重建。已处于退出阶段的星体设为不保存。复用 `EXP-SAVE-004`，真实磁盘落盘、重启恢复及离线 LongUpdate 的宿主路径仍待验证。

定位为 `scripts/components/finiteuses.lua:48–87`，`scripts/components/inventoryitem.lua:285–291,369–376,485–499`，`scripts/components/inventory.lua:1390–1432`，`scripts/prefabs/stafflight.lua:5–22,54–64,79–205`，`scripts/components/timer.lua:27–66,122–142`，`scripts/prefabs/staffcastfx.lua:27–66`，`scripts/prefabs/staff_castinglight.lua:1–67`。

## 自写最小结算示例

下面的完整模块可保存为 Mod 的 `scripts/stage3_active_spell_example.lua`。模块返回 `TryCast(staff, doer, pos)`。在自有服务器 `Action.fn` 的执行入口使用 `local TryCast = require("stage3_active_spell_example")`，并直接 `return TryCast(act.invobject, act.doer, act:GetActionPoint())`。自有动作的 POINT collector 和两端 ActionHandler 应按项目载体接线，本模块交付范围为同步结算边界。它依赖游戏中的 `stafflight`、标准 inventoryitem/finiteuses/sanity/health 以及地图接口。

演示夹具政策为一次成功消耗1次耐久与5点理智、距离12、地面可用点、生成失败不扣费、每次受理独立收费、执行前取消不调用入口、死亡拒绝。这里选择直接 Action 返回值，使拒绝能交给动作调用方。将该函数直接当成原版 `SpellCaster:SetSpellFn` 回调时，仍会遇到上述原版忽略返回值的合同，需要另行适配。演示没有跨帧任务或自建持久状态，星体与次数由各自组件管理。标准同步方法正常返回是夹具前提，任一提交中回调抛错或重入后的业务补偿仍需实际项目定义。

example.lua 的 UTF-8/LF SHA256 为 `22885dafa658ca9dae66b4d6356ee89a05d876b42c61cb24f60d42a7094e2bb3`。

```lua
-- Demonstration fixture only. One use and five sanity per accepted cast.
-- The owner is captured before finiteuses can synchronously remove the item.
-- This module is called by a server Action.fn and returns its action result.
local function TryCast(staff, doer, pos)
    if not TheWorld.ismastersim then
        return false, "SERVER_ONLY"
    end
    if staff == nil or not staff:IsValid() or doer == nil or not doer:IsValid() then
        return false, "INVALID_ENTITY"
    end
    if pos == nil then
        return false, "INVALID_POINT"
    end

    local inventoryitem = staff.components.inventoryitem
    local uses = staff.components.finiteuses
    local sanity = doer.components.sanity
    if inventoryitem == nil or inventoryitem.owner ~= doer then
        return false, "NOT_OWNER"
    end
    if doer.components.health == nil or doer.components.health:IsDead() then
        return false, "DEAD"
    end
    if uses == nil or uses:GetUses() < 1 or sanity == nil or sanity.current < 5 then
        return false, "NO_RESOURCE"
    end

    local x, y, z = pos:Get()
    if type(x) ~= "number" or type(y) ~= "number" or type(z) ~= "number"
        or x ~= x or y ~= y or z ~= z
        or math.abs(x) == math.huge or math.abs(y) == math.huge or math.abs(z) == math.huge then
        return false, "INVALID_POINT"
    end
    if doer:GetDistanceSqToPoint(x, y, z) > 12 * 12 then
        return false, "OUT_OF_RANGE"
    end
    if not TheWorld.Map:IsAboveGroundAtPoint(x, y, z, false)
        or TheWorld.Map:IsGroundTargetBlocked(pos) then
        return false, "BLOCKED"
    end

    local light = SpawnPrefab("stafflight")
    if light == nil then
        return false, "SPAWN_FAILED"
    end
    light.Transform:SetPosition(x, y, z)
    -- Commit after successful spawn. No asynchronous continuation is owned here.
    -- This demonstration assumes these standard synchronous methods return normally.
    sanity:DoDelta(-5)
    uses:Use(1)
    return true
end

return TryCast
```

## 检查与尚未验证

维护工作区的 `check.py` 使用现有 `lupa.lua51`，在专题目录运行 `python -B -X utf8 check.py`。它依赖维护工作区布局、同专题自写检查夹具与指定冻结 ZIP，读取 ZIP 仅在内存中加载选定方法，不写出原版源码。下载包可直接使用本篇已内嵌的完整自写示例。

维护证据 `checks.json` 与 `source-audit.json` 保留在工作区，公开研究证据由登记文档的引用到达。已完成候选 schema、所有引用 hash、原版回调 false/异常/拒绝、末次 owner 清理、finiteuses/Timer 内存保存加载、自写示例拒绝/末次成功/连续受理及 Lua 5.1 语法检查。替身检查的调度、原生地图、网络、实体 Retire 和真实资产使用替身。

独立单分片专服通过测试专用 Action.fn 调用本篇原样模块，并使用实际 `SGwilson.castspell` 与 BufferedAction：0.25秒时中断未到第53帧，未结算且两项起手表现已清理；两次提交各消费1次耐久与5点理智，末次同步删除物品并清装备成员；生成的两颗原版星体均具有退出计时。进程退出码为0，测试实体与临时Mod已清理。测试角色为合成服务器wilson，动作接线属于夹具，未验证原版黄杖完整右键入口。验证概况见[本轮说明](../docs/phase15-unified-chains.md)。

远端客户端预测、鼠标/手柄体验、late join、受击/死亡中断、星体磁盘退出后独立进程恢复、玩家 session 与跨分片均尚未验证。手柄、幽灵 haunt 施法、king cane 共享函数、opalstaff、技能树、地图选点与 CASTAOE 均在本篇 Scope 之外。热扩散、烹饪和理智范围公式只记录装配，需按目标效果继续查消费者。
