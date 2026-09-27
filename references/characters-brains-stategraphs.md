# 角色、Brain 与 StateGraph

适用于角色创建、动物亲和、定制生物、形态变化与动作状态排错。以 2026-09-27 核验环境的原版脚本为基线，详见 [environment-tools.md](environment-tools.md)。美术、网络变量与客户端界面细节按技能入口中的对应专题展开。

角色外观和选人资源接入见 [角色与装备美术](character-and-equipment-art.md)；魔力/能量条与恢复流程见 [法术与自定义数值](spells-and-custom-stats.md)。

## 角色工厂与生命周期

注册 `PrefabFiles` 和 `AddModCharacter(name, gender, modes)`，角色 Prefab 使用 `require("prefabs/player_common")` 返回的工厂。性别参数是语法/代词分类；`PLURAL` 是复数类别，不是“双性”，`SECRET` 也不是原版建议的性别枚举。

```lua
local MakePlayerCharacter = require("prefabs/player_common")

local function common_postinit(inst)
    inst:AddTag("my_mod_character")
    -- 双端需要的字段/netvar 在这里定义。
end

local function master_postinit(inst)
    inst.soundsname = "wilson"
    -- 在这里配置权威数值、专属组件与服务端事件。
end

return MakePlayerCharacter("my_mod_character", nil, nil,
    common_postinit, master_postinit)
```

这只是工厂用法，不是包含选人资源、造型、台词和完整玩法的成品角色。复用现有模组时先查已有初始化代码，避免重复覆盖。

- 工厂在 `SetPristine` 前调用 common，客机早退后才调用 master。玩家默认依赖 `wilson` bank 与通用玩家组件，通常使用 `SGwilson` / `SGwilson_client`，不是每个角色名对应一个 SG。
- 工厂默认尝试使用角色名 build，后续 skinner 负责皮肤/造型。build 与角色名相同是便利约定，**不是引擎要求二者永远相等**。自定义映射要一并核对调试生成、换肤、幽灵和形态还原。
- 在 master 内设置 `inst.OnSave` 等回调时，工厂会保存为 `_OnSave` 等再包入玩家默认流程；在后续 PostInit 直接覆盖则必须保留当前函数。不要为自定义资源丢掉原版玩家存档逻辑。
- 选人菜单展示的三维读取 `TUNING[string.upper(character .. "_HEALTH")]` 等，与出生后的组件值是两条配置链，缺一边就可能出现问号或数值不一致。
- `AddPlayerPostInit` 不代表本地玩家已激活、HUD 已创建或已进入正常人形。客户端表现要处理首次进入、幽灵进入、复活、重连与分片切换；服务端 `makeplayerghost` / `respawnfromghost` 事件不会自动传到远程 HUD。

幽灵 UI 应接实际客户端状态链：原版 `player_classified.isghostmode` dirty → 玩家 `SetGhostMode` → HUD / `StatusDisplays:SetGhostMode`。初始化主动刷新一次，并在真实状态变更时刷新；不能用“dirty没变化”作为所有 HUD 都必须每帧轮询的理由。

## 台词与角色专属数值

台词结构按消费者需要填写：普通条目是字符串；分支条目用原版期待的状态键；随机候选是数组。`ANNOUNCE_X = { ANNOUNCE_X = "..." }` 并不等价于 `ANNOUNCE_X = "..."`，无 modifier 时消费者查 `GENERIC` 或数组，写错会静默回退。

注册 `STRINGS.CHARACTERS.MY_MOD_CHARACTER` 后保留需要的结构。`GetString` 有 GENERIC fallback，但不是所有直接读取字符串表的代码都经过它；不把“必须抄整份 Wilson 文件”和“只写任意几个键就绝对够用”当通用规则。原版语气和翻译查当前 `speech_*.lua` 与对应语言 PO，不冻结角色数量。

自定义资源：先确定取值范围、精度、上限变化、耗费失败规则、死亡/复活、保存重启。再选择组件 + replica/netvar + HUD；Class 属性代理是一种同步入口，也可用集中 setter，只要所有写入路径一致。普通 table 赋值本身不联网。死亡时是否保留增益、离线是否继续计时都是玩法决定。

## 从行为到动作结果的调用链

```text
Brain 的行为节点选择目标
  → BufferedAction(doer, target, action, invobject, pos, ...)
  → locomotor/实体接收并推进动作
  → SG ActionHandler 选择状态
  → onenter / timeline / event 控制时机
  → PerformBufferedAction → BufferedAction:Do → action.fn
```

`invobject` 是参与动作的物品，不是泛指代理对象。StateGraph 是状态机实现，除了动画还负责输入限制、时序、动作执行、物理和网络预测；“SG只管动画、Brain加SG才算状态机”会误导排错。

对玩家动作，还要追客户端 action picker、预览 BufferedAction、`SGwilson_client`、RPC/远程动作发送和服务端校验。客户端提前 `ClearBufferedAction` 可能令后续预览发送没有动作；服务端施法逻辑成功不能证明远程玩家能触发它。最终资源扣费与效果只由权威端结算一次。

## StateGraph 修改要点

- `inst:SetStateGraph("SGwilson")` 使用加载文件名；`AddStategraphState("wilson", state)` 使用返回的 `StateGraph("wilson", ...)` 的内部 name。客机常是 `wilson_client`。逐一查看实际返回值，不遍历角色名猜 SG 名。
- SG 定义表会被共用；通过 `inst` 的 prefab/tag/组件限定新增分支，未命中分支返回原 handler 结果。加独立动作使用 `AddStategraphActionHandler`；改现有动作先检查并包装已有 `.deststate`，避免覆盖其他武器分支。
- `TimeEvent(time, fn)` 的时间单位是秒，通常 `TimeEvent(6 * FRAMES, fn)`；`FrameEvent(6, fn)` 才直接接帧数。`SetTimeout` 也是时间，不是自动触发所有 timeline 的终点。
- `busy` 是被调用方检查的状态标签，**不是不可打断保证**。死亡、冻结、传送或直接 `GoToState` 仍可能切走；自定义状态必须有中断清理。
- `sg.statemem` 每次切状态清空，`sg.mem` 跨状态保留。临时无敌、碰撞、移动速度、监听、持续 FX 要在 `onexit` 对称清理，并考虑是否向下一状态有意交接。
- SG 状态事件和全局事件可能都执行；当前状态 handler 返回真才阻止继续走 SG 全局 handler。不要仅用“已定义同名事件”假设覆盖成功。
- `animover` 适合单次动画完成，循环动画或排队动画需核对正确事件与退出条件；动画存在性查当前 bank，不能从另一生物的动画名推断。

形态系统先定义权威状态和明确转移，再绑定动画。进入中途取消、受击、死亡、读档恢复都必须有路径；状态退出代码恢复外观前检查当前形态，避免已经还原后又被旧状态写回 boss build。保存残血形态时处理组件加载顺序，不能把 `SetMaxHealth` 的满血副作用当作读档成功。

## Brain：保留已有行为与处理重建

先选与需求接近的现有 brain，定位新增行为在逃跑、追击、回家、觅食、闲逛之间的优先级。读当前 `behaviourtree.lua`，不要套用其他引擎同名节点的语义：

| 节点 | 对实现有用的区别 |
|---|---|
| `PriorityNode` | 按子节点顺序评估，选成功或运行中的节点，并周期重评；不是概率优先级 |
| `SequenceNode` / `SelectorNode` | 分别按成功继续/失败继续推进，RUNNING 保留进行中的子行为 |
| `WhileNode` | 用并行条件节点持续约束子行为，可因条件变化而中断 |
| `IfNode` | 进入时通过条件后继续子行为，不在子行为运行途中重查该条件 |
| `DoAction` | 负责发起并观察 BufferedAction 的成功失败；先确认动作在该生物 SG 有 handler |

修改原版生物优先评估 `AddBrainPostInit` 的局部修改；全复制 brain 是需要维护官方更新的分叉，只有替换整套 AI 才这样做。教程自定义青蛙还全局修改了 `frog` SG，影响所有使用它的青蛙；仅定制一个物种时选择条件分支或专有 SG。

`Brain:_Start_Internal` 每次启动先调用 `OnStart`，再执行 `modpostinitfns`。`StopBrain` / `RestartBrain` 会重走这条链，休眠唤醒还可能换一个 brain 实例。因此：

- 插入节点或包现有节点时对**当前树根/当前节点**做幂等标记，不用一个永不清除的实例布尔值跳过所有未来重建。
- 不假定 `children[3]` 永远是某个行为；读当前结构，并通过节点类型、名称、位置上下文验证目标唯一且正确。
- 暂停/恢复自己的 AI 干预可使用成对的 `StopBrain(reason)` / `RestartBrain(reason)`，保留同一个有命名空间的 reason，避免与其他停止原因相互解除。
- 测试要保证实体醒着且在可活动地形；休眠实体没动不能证明 AI 补丁失败。至少验证正常启动、停止重启、休眠唤醒和目标移除。

## 原版检索入口与验收

- `prefabs/player_common.lua:MakePlayerCharacter`、`prefabs/player_common_extensions.lua`、`components/skinner.lua`：角色初始化、存档包装、幽灵与造型。
- `widgets/redux/characterbio.lua` → `widgets/redux/templates.lua:MakeUIStatusBadge`、`widgets/statusdisplays.lua:SetGhostMode`、`prefabs/player_classified.lua:OnGhostModeDirty`：菜单数值与客户端生命周期。
- `stringutil.lua:getmodifiedstring` / `GetString` / `GetDescription`：台词真实选择规则。
- `stategraph.lua:StateGraph` / `StateGraphInstance:HandleEvent` / `GoToState`，`stategraphs/SGwilson.lua`、`SGwilson_client.lua`：注册名、分支、状态退出与预测。
- `entityscript.lua:PerformBufferedAction` / `PerformPreviewBufferedAction`，`bufferedaction.lua:Do`，`behaviours/doaction.lua`：动作结果是否真的执行。
- `brain.lua:_Start_Internal`、`entityscript.lua:StopBrain` / `RestartBrain` / `SetBrain`、`behaviourtree.lua:PriorityNode:Visit`：树重建与优先级。
- 服务端自动测试覆盖动作结算、形态中断、存档与重建；真实客户端另验输入、动画、幽灵 HUD、远程预测和双人互相观察。未运行的层级在报告中明确列出。
