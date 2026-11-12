# 放置、部署与施工的接线

普通建筑沿配方 BUILD 或库存物品 DEPLOY 接线。需要跨多次投料保存进度时，再接 ConstructionSite。预览坐标、套件初始化与拆除、累计投料的来源见 [EXP-BUILD-001～003](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json)。

本指南依据 762172 / build26474873 的指定源码 ZIP 静态核对。机制条目保留静态研究状态。示意代码用于已有 prefab 的对应位置，资源、注册和玩法参数由具体项目提供。

## 先选入口

| 功能 | 入口与实现位置 | 复用合同 |
| --- | --- | --- |
| 配方直接造建筑 | recipe 指定 placer，PlayerController 预览并提交，Builder 生成目标 | DC-C01、NC-N004-FINAL-08、EXP-CRAFT-002 |
| 背包套件放建筑 | 物品 deployable + 独立 placer + 目标 prefab，按需求采用 MakeDeployableKitItem | DC-C01～03、EXP-BUILD-002 |
| 挖起植物重新种植 | 复用种植物的部署模式、可种条件及短小 ondeploy | DC-C01～04 |
| 已建现场分次投料 | CONSTRUCTION_PLANS + constructionsite + 既有施工会话和容器 | EXP-BUILD-003 |

普通 DEPLOY 已有单件移交、提交复检和失败返还合同。Builder 和 Workable 的基础流程也已有覆盖，按现有条目接入即可。[物品与种植物](items-food-plants.md) · [动作生命周期](action-lifecycle-architecture.md)

## 让预览和实际落点使用同一几何规则

1. 在 prefab 模块按既有环境 `require "prefabutil"`，导出 `MakePlacer(...)` 返回的预览 Prefab。按 DC-C01 接配方 placer 名或物品部署 placer 名。该工厂提供本地非持久预览。
2. 配方预览的 testfn 调 builder replica 的 CanBuildAtPoint。物品预览的 testfn 调 inventoryitem replica 的 CanDeploy，同时接鼠标阻挡结果。主机部署再运行 Deployable:CanDeploy。
3. 常规显示变化放 MakePlacer 的 postinit_fn 与 placer 的既有回调。需要吸附时，在 onupdatetransform 更新预览位置，并给 override_build_point_fn 返回对应提交点。配方鼠标、手柄提交以及普通物品 DoAction 都有读取该 override 的消费者。
4. override_testfn(inst) 会取得测试选择权。项目若使用 CUSTOM 模式，应在公共区设置 _custom_candeploy_fn，让预览和主机访问各自可用的同一规则。需要 DEFAULT 的地面与占位条件时，按 DC-C01 的 Map 合同显式组合。以最终提交点执行权威检验。

TestCanBuild 透传 can_build、mouse_blocked。oncanbuild/oncannotbuild(inst, mouse_blocked) 执行后会结束当次 OnUpdate，自定义消费者因此承接默认颜色、显隐及随后辅助更新的职责。moon_device 的 file-local override 回调展示了吸附接线，并带有其任务进度特定的准入策略。[EXP-BUILD-001 的 BUILD-S03～12](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json)

GetDeployAction 会从当前 placer 位置创建动作并记录 selected_pos，成功回调清除此值。提交点 override 的消费发生在具体控制器路径，排查偏移时同时看创建动作与 DoAction 的实际位置写入。[EXP-BUILD-001-C03](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json)

## 范围圈随预览退出

LinkEntity 将实体纳入预览默认颜色与显隐联动。附属实体的生命周期另由实际所有者接线。已有本地范围圈需要随 placer 删除时，可在预览 postinit 中接入 Lua 子实体所有权。

```lua
-- helper 为此处已创建的本地范围表现实体。
inst:AddChild(helper)
inst.components.placer:LinkEntity(helper)
```

AddChild 记录 Lua children 并设置父级，父实体移除时会移除所记录子实体。LinkEntity 还会按参数设置 lightoverride。采用外部共享实体时，按共享所有权安排退出处理。firesuppressor 的具名消费者分别设置父级与显示关联，可作为表现参数参考。[EXP-BUILD-001-C05/C06，BUILD-S13/23/24](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json) · [任务与实体所有权](component-task-ownership.md)

## 套件放下后，业务组件接在目标构造中

MakeDeployableKitItem 可复用套件网络、库存、deployable 及默认生成逻辑。它返回套件 Prefab，另行提供目标与 placer 定义。参数顺序、默认值与公共/master hook 时序见 EXP-BUILD-002 的 API 合同。burnable 的启用值使用表，fuelvalue 是该表的可选字段。公共 custom_candeploy_fn 与选定 deploymode 配套。

目标 prefab 的通用业务组件、可交互状态、容器与 HAMMER Workable 在目标的 master 构造中配置。这样出生、读档和放下的实例都能走同一个正常构造入口。公共/master 环境接线沿已有约定。[EXP-BUILD-002-C01/C03](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json) · [Lua 环境与挂钩](core-lua-hooks.md)

默认套件部署顺序为 SpawnPrefab、设置位置、对目标 PushEvent("onbuilt", data)、删除当前移交套件对象。data 提供 builder、pos、rot、deployable。需要沿用预览朝向时，可在目标已安装的 onbuilt 消费者中应用 rot。

```lua
local function OnBuilt(inst, data)
    if data.rot ~= nil then
        inst.Transform:SetRotation(data.rot)
    end
end
-- 在目标的 master 构造中安装，可与已有 onbuilt 业务合并。
inst:ListenForEvent("onbuilt", OnBuilt)
```

配方 Builder 给结构定位与旋转后发 onbuilt，还执行 onBuild 和 EntityScript:OnBuilt。后者分发组件 OnBuilt 与实体 OnBuiltFn。选择套件路径时，按实际需要明确这些分发的调用者，避免将同一业务同时接入多个通知而重复执行。默认套件把旋转交在 payload，目标消费者自行使用。[EXP-BUILD-002-C02/C03/C06](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json)

自定义植物或短小建筑也可保留自己的 ondeploy。遵守普通 DEPLOY 的移交对象合同，在生成成功后定位、按项目需要初始化目标，再消费所接收的对象。DC-C04 的原版种植物有 stackable:Get():Remove() 与 OnTransplant 接法。默认套件则直接 Remove 当前移交对象，两者分别按自己的实例实现复用。[DC-C02～04；EXP-BUILD-002-C04](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json)

SpawnPrefab 返回 nil 时，默认套件跳过目标初始化和消费，外层 Deploy 仍可能发送事件并返回 true。项目若需要反馈产品生成失败，应在具体部署消费者中定义反馈，ondeploy 的返回值本身不会控制动作返还分支。[EXP-BUILD-002-C04](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json)

## 锤完后的掉落、内容物与主体退出

复用 Workable:SetWorkAction(ACTIONS.HAMMER)、SetWorkLeft、SetOnWorkCallback 与 SetOnFinishCallback。耐久数值和返还物由项目确定。普通工作和工具次数消费沿 EXP-CRAFT-003/004。

yotb_sewingmachine 的实际完成回调依次处理燃烧状态、容器 DropEverything、lootdropper:DropLoot、拆除 FX 与主体 Remove。新建筑按自己的内容和掉落约定接完成回调。套件生成帮助函数负责生成接线，目标的拆除内容由目标回调定义。若项目选择返还套件，核对 lootdropper 与手动生成的总产物，防止重复发放。[EXP-BUILD-002-C05，BUILD-S15/16](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json)

## 确需累计投料时接施工现场

1. 为现场 prefab 在 CONSTRUCTION_PLANS 中提供 Ingredient 的 type/amount 计划。该表由现场 prefab 名索引，在公共加载阶段登记；客户端 constructionsite replica 也会读取计划，不能只放在服务器分支。标准 UI 和 classified 都按四槽材料接线，更多类型需共同核对界面与计数载体。
2. 在现场 master 构造添加 constructionsite，调用 SetConstructionPrefab("construction_container") 与 SetOnConstructedFn。参考 moon_device 的具名接线。它的 OnConstructed 是 file-local 函数，复用其思路时在自己 prefab 定义项目回调。
3. 沿 ConstructionBuilder 的 StartConstruction、临时容器、APPLYCONSTRUCTION、FinishConstruction、SG 提交流程传入材料。由 OnFinishConstruction 调现场 OnConstruct，使用现有会话生命周期。
4. onconstructedfn(inst, doer) 每批提交都会运行。在回调中用现场 IsComplete 或项目阶段需求决定何时推进。moon_device 先核对需求，再 ReplacePrefab 下一阶段。

AddMaterial 只累计数字并返回余量。标准 OnConstruct 负责实物缩堆、返还余量或 Remove，然后清 builder、记录统计并执行回调。单独调用 AddMaterial 的业务要自行定义对应实物的处理，避免同一材料同时留在物品和现场计数中。[EXP-BUILD-003-C01～03](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json)

现场 OnSave/OnLoad 保存和恢复已累计数量，按当前计划重接槽，计划外旧材料保留为无 slot 数量。停止会话归还的是临时容器物品。项目要求拆除退还已投材料时，才在相应入口显式调用 DropAllMaterials，再按业务处理现场主体。该方法以数量生成返还物，随后主体移除由调用方负责。[EXP-BUILD-003-C04/C06](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json)

DropAllMaterials 先扣现场计数，再按 prefab 生成实物。使用前保持已存材料 prefab 有效。旧版本材料计划变更和生成失败的具体恢复策略尚待项目验证。[EXP-BUILD-003 的 API 合同](../knowledge/research/native-mechanisms/placement_construction-4cae4883e62c.json)

## 验证范围

按本次修改检查实际落点、部署单件数量和建筑交互；涉及累计施工或拆除返还时，再检查对应进度与物品去向。
