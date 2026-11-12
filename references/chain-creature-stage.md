# 普通猪人的两态变形链

本指南覆盖普通 `pigman` 的 `normal ↔ werepig` 两态，以及触发、权威修改、Brain/SG 消费、回退、卸载与必要恢复。输入积累、等待任务和变形动画是两态转换过程中的临时状态。来源为冻结归档 `762172`，归档 SHA256 为 `733a0f7f97ace5a76aa5acee95405a6ec01697d93d844eeb4ecce7c001306980`。

## Scope 与读取顺序

适用于维护普通猪人变形，或研究同实体两态生物如何接线。范围排除 `pigguard`、`moonpig`、`frankenpig`、寄生复活、全部 Boss、技能树和世界生成。自有生物的阈值、持续时间、保血、死亡和取消政策需要按项目确定。

1. 从 `knowledge/CATALOG.json` 按 ID 的 `file` 和 `pointer` 读取 `EXP-CHAIN-STAGE-001`，先读 Scope、三轴状态、unknowns，再读 claims 和实际 API。该条保持 `research/restricted/hold`，显式 Reviewer 读取。
2. 涉及换树和行为抢占时，定向补读 `EXP-AI-001`、`EXP-AI-003`、`EXP-AI-008`。它们分别负责 Brain 安装/重建、Priority 重评和 combat 至攻击 SG 的通用部分。
3. 涉及动画中断、SG 实例或入态数据时补读 `NC-N003-INT-05`、`NC-N003-INT-07`。Core 保持原 Coding HOLD，历史 Scope 和来源版本继续保留。
4. 涉及组件卸载、任务和实体移除时补读 `EXP-LIFE-005`、`EXP-LIFE-006`、`EXP-LIFE-008`。涉及保存分发时补读 `EXP-SAVE-001`。
5. 本次另核对了 `EXP-GROW-001` / `EXP-GROW-002` 的 Scope。普通猪人的阶段 owner 是 `werebeast`，相关 Growable 阶段表和暂停原因合同仅提供比对导航。目标使用 Growable 时再定向读它们。

本链复用 9 条已有记录，新增 1 条具名链和 7 项 `WereBeast` API 合同。已有条目的版本、未知与更正以其正文为准。

按任务补读角色、Brain 与 SG、生物 AI、生命周期与保存，以及登记知识的检索规则。[角色、Brain 与 SG](characters-brains-stategraphs.md) · [生物 AI](creature-ai-practical.md) · [生命周期与保存](lifecycle-save.md) · [知识检索](kb-retrieval.md)

## 权威状态与实际消费者

| 内容 | 所有者与消费点 |
|---|---|
| 输入累计 | `werebeast.triggerlimit/triggeramount`，`TriggerDelta` 达阈值进入 were |
| 等待世界状态转换 | `werebeast._task`，由满月变更和 limbo 事件创建/取消 |
| 当前 were 判断与回退 | `werebeast._reverttask`，`IsInWereState` 只检查该字段非 nil |
| 阶段属性 | prefab 的文件局部 `SetNormalPig` / `SetWerePig` 配置同一个实体 |
| 行为 | `pigbrain` / `werepigbrain`，读取 combat、SG 标签及其他组件 |
| 动作与表现 | `SGpig` / `SGwerepig` 消费形态事件、doattack 和动画事件 |
| 保存 | werebeast 保存 `time`，prefab 保存 `build`，health 保存自身血量 |
| 退出 | 组件卸载释放自身任务/监听，整实体移除另由 EntityScript 总清理 |

`common()` 创建 Network、AnimState 和共享标签，在 `SetPristine` 后对客户端早退。werebeast、Brain、SG 与权威属性接线位于 master 分支。客户端可见动画与标签的实际送达效果仍需远端观察。来源范围为 `scripts/prefabs/pigman.lua:748–887、922–950`，引用 `STAGE-P5/P6`。

## 有限完整链

### 输入与受理

- 食用经 `Eater:Eat` 的接受分支到 `oneatfn`。pigman 的 `OnEat` 要求有 edible、食物类型为 MEAT、当前非 were，且该食物对猪人的 `GetHealth(inst) < 0`，随后 `TriggerDelta(1)`。原版配置阈值 4，未达阈值仅累积。相关来源为 `scripts/components/eater.lua:198–286`、`scripts/prefabs/pigman.lua:136–147、748–887` 和 `scripts/components/werebeast.lua:95–111`。
- 满月监听先取消旧待转任务。异态且非 limbo 时安排延迟转换，同态满月可延长回退时间。进入 limbo 取消待转任务，离开后延迟重新检查。haunt 另有普通、非 franken 与概率条件，按当日剩余时间调用 `SetWere(time)`。相关来源为 `scripts/components/werebeast.lua:1–85` 和 `scripts/prefabs/pigman.lua:736–743`。
- `SetWere` 和 `SetNormal` 都会重复执行回调。调用方若只允许一次变形，需要根据自己的入口与政策检查形态。回调直接调用，异常、移除或重入后的整体事务结果没有保证。

### 进入、消费与动画中断

`SetWere` 依次取消待转任务、调用 were 回调、发 `transformwere`、重置累计、替换回退任务。`SetNormal` 依次取消待转任务、调用 normal 回调、发 `transformnormal`、重置累计、取消并清回退字段。首次 were 回调与事件期间，`IsInWereState()` 仍可为 false，normal 回调与事件期间仍可为 true。来源为 `scripts/components/werebeast.lua:113–149`。

阶段回调立即切换 Brain、SG、build、速度、伤害、攻击周期、生命上限、索敌、睡眠和掉落，且清当前 combat target。were 还会关闭交易、移除旧跟随领袖并静默 talker，normal 重新开启交易和 talker。旧领袖没有自动恢复语句。`Health:SetMaxHealth` 同时写满当前血量。来源为 `scripts/prefabs/pigman.lua:338–371、557–588` 和 `scripts/components/health.lua:503–507`。

两种 Brain 各自消费阶段属性。pigbrain 有追击和冷却逃跑分支，werepigbrain 的 jumping 持续门槛包住 panic、SafeToEat、追击和漫游。combat 的 `TryAttack` 发 `doattack`，SG 接受后在攻击时间线调用 `DoAttack`。普通猪使用 `13 * FRAMES`，werepig 使用 `FrameEvent(16)`，werepig 攻击退出在 jumping 仍存在时清 motor override。来源为 `scripts/brains/pigbrain.lua:382–423`、`scripts/brains/werepigbrain.lua:11–59`、`scripts/components/combat.lua:829–843`、`scripts/stategraphs/commonstates.lua:351–363` 及两种 SG 的攻击范围。

阶段回调先安装新 SG，再发布形态事件。were 变形态退出设置 werepig build，受击可转 hit。normal 变形态借用五个转换符号，退出恢复普通 build 并清符号，正常动画结束转睡眠。动画中断会执行相应态的表现退出，阶段回调此前已提交的属性变化继续保留。来源为 `scripts/stategraphs/SGwerepig.lua:24–28、94–124` 和 `scripts/stategraphs/SGpig.lua:60–64、214–247`。

### 到期、取消、死亡与移除

- 显式取消可通过权威 `SetNormal()` 进入 normal 回调与事件。它会按原版 normal 配置重设生命上限和当前血量，原版在此没有保血政策。
- 到期 `OnRevert` 要求 were 字段非 nil 且 SG 无 transform 标签。transform 期间到期会跳过 `SetNormal`，该分支没有重排或清句柄语句。任务字段和调度器活动身份需要分别检查。来源为 `scripts/components/werebeast.lua:10–14`。
- 组件卸载钩子 `OnRemoveFromEntity` 取消并清两类任务，停止满月监听，解绑 limbo 事件。该钩子没有恢复 normal 属性。整实体 `Remove` 会清 worldstate、事件与 pendingtasks，再调用各组件的 `OnRemoveEntity`。来源为 `scripts/components/werebeast.lua:73–85` 和 `scripts/entityscript.lua:1730–1797`。
- health 的正血到死亡路径发布 `death`，两种 SG 均有实际死亡消费者。werebeast 没有死亡监听，内部阶段回调和 setter 也没有存活守卫。死亡后到实体移除前的阶段计时、补血和换 SG 交互仍需运行验证。来源为 `scripts/components/health.lua:565–611`、`scripts/stategraphs/commonstates.lua:372–385` 及两种 SG 的 death 态。

### 保存与恢复

werebeast 保存待转或回退时间，取整且回退余量只有正值才产出。待转任务存在时优先按满月状态选择保存 `floor(weretime)` 或 nil。触发累计、任务句柄和动画进度没有保存字段。`OnLoad` 在 `data.time` 存在时执行 `SetWere(max(0,time))`，重新应用整个阶段回调与事件。pigman 的 PreLoad 恢复 build，prefab OnLoad 在当前非 were 时恢复普通 build。来源为 `scripts/components/werebeast.lua:151–164` 和 `scripts/prefabs/pigman.lua:702–728`。

`EntityScript:SetPersistData` 的组件分发使用 `pairs`，werebeast 与 health 没有固定加载顺序。were 回调的 `SetMaxHealth` 会补满血，health 加载又会写保存血量，因此受伤 werepig 的血量恢复仍需实际磁盘验证。原版这条链可用于理解顺序风险，自有保血需求需要明确恢复政策并检查正常入口。来源为 `scripts/entityscript.lua:1928–2014` 和 `scripts/components/health.lua:154–185、503–507`。

## 最小 Lua 示例

将下列完整代码作为隔离测试 Mod 的 `modmain.lua`。前提为无节日、无寄生、普通 `pigman`，保留其原版 Prefab 初始化。示例沿原有 werebeast、Brain、SG、属性和保存链运行，新增两个服务器事件入口。阈值 2、直接请求持续 15 秒，以及沿用原版补满血/清领袖行为，均为演示夹具选择。

`modmain.lua` 使用 Mod 环境。示例的两个全局入口分别为 ModUtil 注入的 `AddPrefabPostInit` 和 CreateEnvironment 提供的 `GLOBAL`。回调执行时通过 `GLOBAL.TheWorld` 读取当时的世界实例，世界引用的读取时点位于 Prefab 初始化回调内。环境定义与注入位置为 `scripts/mods.lua:258–320`、`scripts/modutil.lua:592–599`，版本与归档 SHA 沿本篇来源身份。

在服务端对明确选择的普通猪实例调用 `pig:PushEvent("stage_fixture_were")` 或 `pig:PushEvent("stage_fixture_normal")`。已死亡请求被拒绝，同态请求跳过。食物阈值输入仍走原版 `OnEat`，它按组件默认 `weretime` 计时。存档由原版组件负责，新增事件监听在 Prefab 初始化时重新建立。

下列代码可直接提取为 `modmain.lua`，与维护工作区的 `example.lua` 精确绑定，SHA256 为 `e891f9e9ef763a3d3994d4864a2fb15d85ac7bbe82a6dd785fa7b508f87b5520`。

```lua
-- Demonstration fixture for ordinary pigman in a non-event test world.
-- Fixture policy: threshold 2, duration 15 seconds, native health/leader reset.
-- Use as modmain.lua in an isolated test mod. No new state is persisted.
AddPrefabPostInit("pigman", function(inst)
    if not GLOBAL.TheWorld.ismastersim then
        return
    end

    inst.components.werebeast:SetTriggerLimit(2)

    inst:ListenForEvent("stage_fixture_were", function(inst)
        if not inst.components.health:IsDead()
            and not inst.components.werebeast:IsInWereState() then
            inst.components.werebeast:SetWere(15)
        end
    end)

    inst:ListenForEvent("stage_fixture_normal", function(inst)
        if not inst.components.health:IsDead()
            and inst.components.werebeast:IsInWereState() then
            inst.components.werebeast:SetNormal()
        end
    end)
end)
```

## 已验与待验

静态检查通过当前登记 schema、归档 SHA、23 项文件/范围 hash 及 Lua 5.1 编译。12 项 Lua 5.1 替身检查执行了归档内 werebeast 与本例的请求/取消、客户端早退、阈值、正常到期、重复替换、transform 到期跳过、满月/limbo、存取整与组件卸载。

其中两项回归从冻结归档在内存中加载实际 CreateEnvironment 与 ModUtil，经 `setfenv` 在实际 Mod 环境注册并调用 PrefabPostInit。环境保持原生的显式成员集合，世界在注册之后建立，另以替换世界实例检查回调读取时点。回归同时重现旧版直接读取 `TheWorld` 的失败，并验证修改后的服务端事件和客户端早退。任务、worldstate、实体、health、SG 及环境依赖模块使用报告中列出的替身。`checks.json` 与 `source-audit.json` 是本轮工作区维护证据，使用本指南可直接提取上面的完整代码。

修正后的本篇代码已原样作为 `modmain.lua` 在真实Mod环境的独立单分片专服运行。普通pigman的阈值2、were事件后的原生标签/生命上限/伤害/回退任务、重复were请求不替换任务、normal事件恢复属性并清任务字段均通过；另一个实体卸载WereBeast后，两类任务字段已取消并清空。同一隔离存档重启恢复were形态、回退任务、生命上限及示例阈值，随后normal请求成功。最终两次退出码均为0，测试实体和临时Mod已清理。概况见[本轮说明](../docs/phase15-unified-chains.md)。

旧示例在Mod环境直接读取 `TheWorld` 的通过结论已撤回，当前内嵌代码使用回调时的 `GLOBAL.TheWorld`，与实际运行文件SHA绑定。研究登记继续为 `runtime_verified=false`。远端显示、原生动画/物理观察、死亡、满月、transform期间到期、跨分片及第三方组合仍待验；本次恢复检查不证明受伤werepig在所有组件加载顺序下保血，也不覆盖攻击中换SG的motor清理。

每项来源的文件 SHA、行范围和按 UTF-8 `splitlines` 后 LF 拼接且无尾换行计算的范围 SHA，均随最终登记记录 `EXP-CHAIN-STAGE-001` 的 `source_references` 保存。通过包内 `knowledge/CATALOG.json` 中该 ID 的 `file` 和 `pointer` 可到达这些公开来源定位。静态研究结论和替身结果各按本节范围使用。
