# 可收起建筑的有限完整链

本篇补齐 `portabletent_item → portabletent → portabletent_item` 的具名消费者与耐久交接。原版在 `disassemble` 动画完成时才生成收起物，动画中的保存恢复有明确边界。来源为 762172 的限定 ZIP，研究状态保持 `research/restricted/hold`，`runtime_verified=false`。本篇按任务导航与当前项目独立源码核对使用。

## Scope 与读取顺序

限定普通未骑乘、非漂浮、没有 hungrybuilder/fastbuilder/slowbuilder 速度标签角色的 DEPLOY 与 DISMANTLE，以及 portabletent 的 HAMMER 消费者。完整链指本篇列出的输入、权威执行、交接、退出与恢复结论，范围中的未知会继续保留。

1. 先读放置指南及 `DC-C01` 的门禁，再读 `DC-C03` 的普通移交对象、`DC-C02` 的 Deploy 返回/事件合同。Core 的 Coding HOLD 保留。[放置与建筑](placement-buildings.md) · [物品、制作与采集](items-food-plants.md)
2. 读 `EXP-BUILD-001` 的预览与实际点，`EXP-BUILD-002` 的 kit/拆除对照。`EXP-BUILD-003` 只在项目需要累计施工时继续读。帐篷采用自己的部署回调。[放置与建筑](placement-buildings.md)
3. 显式 Reviewer 读取 `EXP-CHAIN-DEPLOY-001`，按目录 file/pointer 或登记文档进入。它新增本次具名收起交接，包含五个 API 原子与三十七处来源范围。[读取方法](kb-retrieval.md) · [EXP-CHAIN-DEPLOY-001 登记文档](../knowledge/research/native-mechanisms/stage3_deployable-dac1a9564775.json)
4. 涉及删除或存档时补读 `EXP-LIFE-008`、`EXP-SAVE-001`。各旧条目的原 Scope、版本与准入继续保留。[组件与任务归属](component-task-ownership.md) · [保存恢复](save-recovery-architecture.md)
5. 对目标 Mod 独立核对本版本 prefab、组件与动作消费者。本文研究 ID 用于定位待核查点。玩法数值、退款、焚毁、耗尽和第三方兼容按项目需求明确。[动作生命周期](action-lifecycle-architecture.md)

## 原版链与状态所有者

| 环节 | 实际行为与所有者 | 本次来源 |
| --- | --- | --- |
| 公共物品与预览 | item 公共构造带 portableitem，Pristine 后非 master 返回。master 装 inventoryitem、finiteuses、deployable。物品未装 stackable，restrictedtag 赋值为注释，部署模式沿默认 DEFAULT。独立导出 item_placer。 | DEP-S02、S35 |
| 本地输入 | PlayerController 对鼠标活动物或手柄光标物创建 placer，以 inventoryitem replica CanDeploy 做预览检查。POINT 菜单也查询该 replica。placer 命名沿 item prefab 加 `_placer`。取消预览删除 placer。 | DEP-S10～14 |
| 输入提交 | 鼠标发送动作、点和旋转，master 重选同 code/mod 的右键动作。手柄部署入口检查 GrandOwner，重建 BufferedAction。两端 DEPLOY handler 选普通 doshortaction，client preview 经 RemoteBufferedAction，server 第六帧执行 buffered action。原生 RPC 桥接内部及实际远端送达待验。 | DEP-S15、17、19、21、28～33 |
| 权威部署 | ACTIONS.DEPLOY 先 CanDeploy，取持有容器的 RemoveItem 结果，清 prevcontainer/prevslot，再由该对象 Deploy 复检。此 item 无堆叠，移交的是当前单件。生成成功时 OnDeploy 复制当前 uses 到结构，然后 Remove 移交物。 | DEP-S02、08、09、34 |
| 已部署状态 | 结构 master 拥有 finiteuses、sleepingbag、portablestructure 与 HAMMER workable，构造时装好业务。OnDeploy 播放 place，并未发 onbuilt，也未读取旋转。 | DEP-S01、02 |
| 收起入口 | SCENE 的右键入口选择 DISMANTLE。服务器拒绝燃烧和睡眠占用，检查 candismantle，再调用 PortableStructure。普通角色 dolongaction timeout 才执行。PortableStructure 只调用已绑定回调。 | DEP-S05～07、16、18、20、22 |
| 收起交接 | ChangeToItem 卸载 sleepingbag、portablestructure、workable，加 NOCLICK，播放 disassemble 并监听 animover。OnAnimOver 要求 AnimDone 且当前动画仍为 disassemble，随后读 uses、ReplacePrefab、写物品 uses。ReplacePrefab 本体只传位置并删除旧实体。 | DEP-S03、24、26 |
| 锤击与睡眠退出 | OnHit 唤醒当前睡眠者。sleepingbag 卸载也会 DoWakeUp，portabletent OnWake 解绑 onignite、停睡眠任务并 Use 一次。未烧毁锤完进入同一收起函数，烧毁锤完走掉落/FX/Remove。 | DEP-S01、03、04、23、25 |
| 耗尽与烧毁 | OnFinished 停睡眠声、播 destroy、animover 删除并设 persists=false。OnBurnt 调烧毁助手、去碰撞、卸载 portablestructure。烧毁助手的全部内部行为保留专题外边界。 | DEP-S03、04 |

来源编号在 `EXP-CHAIN-DEPLOY-001` 所在登记文档的 `source_references` 中展开为 scripts 路径、符号、行号与 hash。编号 `DEP-S10～14` 表示同前缀的连续来源。[完整来源定位与 hash](../knowledge/research/native-mechanisms/stage3_deployable-dac1a9564775.json)

## 成功、失败与取消

- 预检查拒绝发生在 RemoveItem 之前。Deploy 内复检返回 false 时，普通动作尝试 GiveItem 返还。具体落回库存、溢出或落地需按实际 GiveItem 消费者与空间验证。
- 原版帐篷 SpawnPrefab 返回 nil 时，OnDeploy 留下移交物。外层 Deploy 继续发 deployitem 并返回 true，普通动作跳过 false 返还分支。最终产物与物品归属需要独立检查。
- PortableStructure:Dismantle 忽略回调返回。ACTIONS.DISMANTLE 调过组件后返回 true，此时原版仍可能在等 disassemble 动画。
- server 短/长动作提前退出按缓冲身份及 lastheldaction 条件清缓冲，ClearBufferedAction 调 Fail。提交之前停止动作时，交接回调尚未运行。提交之后结构上的 animover 转换由结构承接，玩家动作退出没有在本 prefab 中安装回滚操作。
- 原版 ReplacePrefab 对 nil 生成没有 guard。替身观察到它在访问目标 Transform 时出错，原实体 Remove 尚未执行。发生异常后的完整游戏状态和重试行为待验。

## 保存与恢复的明确边界

稳定库存物和稳定结构都在构造中初始化 finiteuses。非满 uses 由组件 OnSave 保存，有字段时 OnLoad 通过 SetUses 恢复。满值没有该字段时沿构造默认值。prefab OnSave/OnLoad 另处理 burnt，组件数据由 EntityScript 汇总和分发。

原版 ChangeToItem 没有把主体设为非持久，也没有保存“正在收起”标记。收起动画中的保存仍是 portabletent 记录，已卸载组件没有 payload。普通重建会重新装 sleepingbag、portablestructure、workable，本 prefab OnLoad 没有恢复 disassemble 和其监听的分支。这是本次静态发现的恢复边界。实际磁盘快照及重启仍待验证，不能将动画中重载记为收起续行通过。

只复制 uses 无法给额外 Mod 状态提供迁移承诺。需要保留皮肤、wetness、其他组件或外部 GUID 引用时，逐项核对目标功能的真实消费者和保存调用方。[保存恢复](save-recovery-architecture.md) · [本条来源定位与 hash](../knowledge/research/native-mechanisms/stage3_deployable-dac1a9564775.json)

## 最小独立示例

示例是两个已登记 prefab 的回调模块。它独立编写，采用同步收起，并在部署生成失败时显式尝试 GiveItem 返还移交物，收起生成失败时保留结构供再次操作。该政策及下文容量 7 是演示夹具选择。原版动画收起的事实与本示例政策分别按上文适用。

将下方完整代码保存为项目 `scripts/portable_chain_callbacks.lua`。它与本专题 `example.lua` 的 UTF-8/LF 字节绑定为 `d2190128ca4aab9fc1c430aeffac8ec07f043d76c1ff8340e805afcd6b8731ba`，复制时保留结尾换行。

```lua
-- Independent callback fixture for two registered, non-stackable prefabs.
-- Both prefab master constructors own a finiteuses component.
-- Demonstration policy: synchronous packing and explicit deployment refund.
-- Spawn failure leaves the original object available for retry.
local function OnDeploy(inst, point, deployer)
    local structure = SpawnPrefab("chain_demo_structure")
    if structure == nil then
        deployer.components.inventory:GiveItem(inst)
        return
    end

    structure.Transform:SetPosition(point.x, 0, point.z)
    structure.components.finiteuses:SetUses(inst.components.finiteuses:GetUses())
    inst:Remove()
end

local function OnDismantle(inst)
    local item = SpawnPrefab("chain_demo_item")
    if item == nil then
        return
    end

    item.Transform:SetPosition(inst.Transform:GetWorldPosition())
    item.components.finiteuses:SetUses(inst.components.finiteuses:GetUses())
    inst:Remove()
end

return {
    OnDeploy = OnDeploy,
    OnDismantle = OnDismantle,
}
```

在项目正常 prefab 构造入口中接线。

- 两个 prefab 在公共区完成 Network、必要 tags、动画/物理并调用 SetPristine，非 master 返回。独立提供 `chain_demo_item_placer`，预览沿标准 DEFAULT 地面规则。
- 在两个 master 构造里添加 finiteuses，依次 SetMaxUses(7)、SetUses(7)。项目需要消费次数时明确其消费点与 OnFinished 政策。本文夹具只测试正剩余次数的跨形态交接。
- item 的 master 添加 inventoryitem、deployable，`local callbacks = require("portable_chain_callbacks")` 后把 `callbacks.OnDeploy` 赋给 deployable.ondeploy。item 使用普通非堆叠移交分支。
- structure 的 master 添加 portablestructure，把 `callbacks.OnDismantle` 交给 SetOnDismantleFn。保持构造默认完整，保存 uses 由 finiteuses 自己承担。
- prefab、placer、资产、图标、动画和游戏入口由所在项目正常登记。本交付的可独立执行对象是回调模块与 Lua 替身检查，实际游戏 Mod 接线仍需结合项目资源。

同步收起在单次 Lua 回调里完成“生成、定位、uses 复制、旧实体删除”，示例没有跨帧待保存字段。提交前取消沿正常 SG。示例的部署生成失败仍可能得到通用动作 true，GiveItem 尝试返还与最终送达需要分别检查。异常抛错、回调重入与第三方变更超出该夹具的正向与 nil 生成测试条件。

## 检查与待验

本次维护在只读 ZIP 上核对全部文件/范围 hash、当前 mechanism contract，再以 `lupa.lua51` 编译并执行本示例和内存读取的原版局部函数。十二项替身检查涵盖单件部署、复检失败返还、原版 nil 生成、动画门禁、uses 交接、ReplacePrefab nil 异常、保存 payload，以及示例失败保留/重试。取消只做提交前模型，SG 中断清理按源码静态审阅。保存只检查内存组件 payload。审计与检查脚本/JSON 保存在维护工作区，下载包正文已内嵌完整示例，公开来源定位与 hash 可从登记文档读取。[EXP-CHAIN-DEPLOY-001 登记文档](../knowledge/research/native-mechanisms/stage3_deployable-dac1a9564775.json)

本篇原样回调模块已接入测试专用最小网络prefab，在独立单分片专服通过实际 `ACTIONS.DEPLOY` 与 `PortableStructure:Dismantle` 验证：合法点部署、收起、再次部署均保持uses=5并删除旧形态；同一隔离存档重启后仅恢复一个uses=5的稳定结构，恢复的收起回调继续保持次数。最终两次进程退出码均为0，临时Mod和测试实体已清理。容量7、余量5及长矛占位美术仅为夹具选择。概况见[本轮说明](../docs/phase15-unified-chains.md)。

该运行没有执行原版portabletent的收起动画及动画中存档路径。鼠标/手柄取消、远端展示、多人同时操作、睡眠唤醒的末次耐久、燃烧与动画并发、客户端放置表现、原生生成失败、库存满时返还、收起中移除及跨分片仍待验证。研究登记保持 `runtime_verified=false`。
