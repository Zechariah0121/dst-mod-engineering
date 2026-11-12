# 海钓钓具与新鱼接入

来源与 API 合同：[机制研究](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)。

新增鱼饵可沿原版竿的第二槽接入。新浮标接投掷参数和指定 projectile。新海鱼还需要水中、收获库存及所需群体定义。本轮 EXP-FISH-001～003 分别覆盖钓具、钓获实体交接和鱼群生成，依据 762172 / build26474873 的源码整理。

## 选择实际入口

| 要做的功能 | 最短接线 |
| --- | --- |
| 给原竿增加鱼饵 | 公共 oceanfishing_lure 标签 + master oceanfishingtackle:SetupLure，进入第二槽 |
| 新浮标物品 | 公共 oceanfishing_bobber 标签 + SetCastingData，按需求复用现成 projectile |
| 新竿 | 正常网络/装备/两槽容器 + oceanfishingrod 的默认数据、取钓具与阶段回调 |
| 新海鱼 | 水中鱼组件/Brain/SG + 投掷落地消费者 + 库存形态 |
| 加入普通游动鱼群 | 上述鱼定义 + schoolherd 定义 + fish/school 数据接线 |
| 固定补员鱼点 | 为自己的固定点配置 childspawner，选定水中鱼 prefab |

船上平台归属沿 EXP-OCEAN-001～003。普通动作执行、容器移交、任务与实体退出沿既有合同。[船上装置](boats-platforms.md) · [动作生命周期](action-lifecycle-architecture.md) · [物品与植物](items-food-plants.md)

## 鱼饵从槽位到咬钩

1. 正常物品 prefab 在公共区、SetPristine 前加 oceanfishing_lure 标签，提供网络和可用动画/库存资源。
2. master 构造添加 oceanfishingtackle 并 SetupLure。下例用原版完整日间勺形饵数据说明接线，具体强度与消耗政策由项目选择。

```lua
local setup = {
    lure_data = deepcopy(TUNING.OCEANFISHING_LURE.SPOON_DAY),
}
inst:AddComponent("oceanfishingtackle")
inst.components.oceanfishingtackle:SetupLure(setup)
```

需要在钩上显示自己的鱼饵时，给 setup 的 build、symbol 填对应资源。single_use 位于 setup 顶层，可选 fns.charm_mod_fn(fish) 也位于 setup.fns。lure_data 提供 charm、reel_charm、radius、style、timeofday，以及需要的 weather、dist_max、stamina_drain。[EXP-FISH-001 API 合同](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

SetupLure 保存传入引用。Cast 选中该鱼饵的完整 lure_data，hook 按自己的读取表达式处理各字段。先从适合目标行为的完整数据结构定义参数，再作项目所需改动。缺少 timeofday 会使该倍率为0，charm/reel_charm/radius则参与直接计算。对共享 TUNING 表的本地改动先取得自己的数据副本。[EXP-FISH-001-C02/C06](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

原竿容器第二槽按标签准入，GetTackle 读该槽。itemget/itemlose 刷新显示用最大距离，下一次 Cast 缓存鱼饵。投掷物落水后把 lure_data 与 fns 交给 oceanfishinghook，鱼 Brain 用其兴趣值选择靠近、轻啄和 EAT。single_use 在竿目标成为非 projectile 且无 hook 组件的目标时由原竿消费者移除。[EXP-FISH-001/002](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

## 浮标与新竿

浮标物品用 oceanfishing_bobber 标签进第一槽，master 调 SetCastingData(casting_data, projectile_prefab)。casting_data 是相对竿基础投掷参数的加成。仅改变距离或精度时，可指定现成浮标 projectile；需要新的投掷/落水表现时，才补自己的 projectile/floater 定义及资源。

原版浮标投掷物在海洋或虚拟海洋落点生成 floater。floater 的 oceanfishable:SetRod 连竿，oceanfishinghook 接鱼饵数据。原投掷物随交接移除，floater 在解除竿时由自身回调移除。相关构造与落地回调均是原文件的 local 函数，自己的新 prefab 按所需行为直接实现对应回调。[EXP-FISH-001-C03/C05](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

新增竿在 common 建网络/必要标签与本地 reticule，在 master 接 oceanfishingrod、inventoryitem、equippable 和 container。使用原两槽协议时，容器采用 oceanfishingrod 布局，设置 accepts_oceanfishingtackle 标签，并按装备/卸装开关容器。换钓具动作读取已打开容器与槽位准入。

竿组件 SetDefaults 后提供 gettackledatafn(inst)，返回 {bobber=..., lure=...}。按本功能接 oncastfn、onnewtargetfn、ondonefishing。原版 oncast 关容器，onnewtarget 处理单次消耗，ondone 在 lost_tackle 为真时销毁所装钓具，满足条件再重开容器。复用其中一份消费责任即可。[EXP-FISH-001 的具名竿消费者](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

人物 SG 在抛竿指定帧提交 CAST，竿按基础参数加钓具同名字段计算本次数据。精度随机乘法发生在名义最大距离裁剪之后。普通张力交互沿已有 REEL/STOP/CATCH 动作，具体触发与回调签名见合同。[EXP-FISH-001/002](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

## 新海鱼从水中到可拾取产物

水中实体提供 fish_def、海鱼公共标签/动画/物理，以及 master 的 locomotor、oceanfishable、eater、knownlocations 和所需称重/群成员组件。沿原版 oceanfishbrain 与 SGoceanfish 时，共同提供所读字段和状态动画。fish_def 中的 lures 控制对 style 的偏好，set_hook_time 决定等待玩家提钩的超时窗口，stamina 控制体力与挣扎阶段。StrugglingSetup 接基础速度和完整 stamina 表。[EXP-FISH-002-C01/C03](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

Brain 选 EAT，鱼 SG 提交动作。双 oceanfishable 分支使鱼接上钩所属的竿，SetTarget 让旧钩退出。onsetrodfn 加 partiallyhooked 后，首次收线的 onreelinginfn 完成提钩并 ResetStruggling。此后复用张力/体力与挣扎 BT。原版 OnSetRod、OnReelingIn 和 OnMakeProjectile 为 file-local，按实际需求在自己的 prefab 中接回调。[EXP-FISH-002-C02/C03](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

需要原版收获方式时，makeprojectilefn 安装并配置 complexprojectile，转换表现和 Brain 状态，返回待抛实体。CatchFish 会把它抛向玩家附近，随后发 fishcaught 并解除竿目标。落地回调在可通行地面生成库存形态、复制所需重量/owner，再移除水中实体。落水分支恢复游动态并安排离开。自己的库存形态独立配置物品、可食用/腐坏等功能。[EXP-FISH-002-C06](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

fishcaught 的时点在投掷之后，库存形态的产生和拾取继续由后继消费者推进。奖励若要求上岸或收入库存，就接对应的实际终点。脱钩时 StopFishing 先通知结束回调和角色/目标，再解绑，原版鱼沿停止事件进入 leaving 行为。[EXP-FISH-002-C04/C07](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

## 新鱼加入游动群或固定鱼点

普通森林 master 已有 schoolspawner。正常玩家入场后，其延时尝试在玩家附近查海面比例、鱼数和 blocker，选出生点后 SpawnSchool。它依当前季节与海域地皮读取 `require("prefabs/oceanfishdef").school` 权重，再通过 `.fish[key]` 取得鱼种定义。

给新鱼接普通游动群时，在自己的正常 Prefab 登记中提供水中实体、库存实体及 `schoolherd_<鱼prefab名>` 群体。共享 fish 表以实际鱼 prefab 名作 key，季节/地皮权重指向同一 key。群体所需字段包括 schoolmin/max/range、群寿命、导航范围与等待时间。每个需要出现的季节/海域分别接权重，原版季节表在模块执行时已经 deepcopy。[EXP-FISH-003-C01/C02/C08](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

原版 MakeFish 与 makeschool 都是 local 工厂，在各自模块执行时按当时的数据导出 Prefab。新 Mod 需使自己的三类定义在实际加载入口可解析，并让权重消费者读到对应数据。核对登记结果后再验证出生，避免依赖已完成导出循环自动再执行。[EXP-FISH-003-C05/C07](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json) · [Prefab 与组件](entities-components.md)

SpawnSchool 返回的 count 包含已排程、尚未生成的鱼。群导航与 lifetime 由 schoolherd 处理，个体按群目标移动。全体成员休眠可回收群，个体休眠则按自身有效 home、leaving 与 persists 判断回巢或删除。需要沿用这些效果时复用对应成员、timer 与退出接线，玩法参数单独决定。[EXP-FISH-003-C03/C04](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

固定补员鱼点沿 oceanfish_shoalspawner 的 childspawner 接线，自己的点设置所需 childname、wateronly、补员/放出周期与 Wake/Sleep 任务。它向世界登记的 ms_registerfishshoal 还会被原版其他海洋业务观察，是否采用这项世界交互由目标功能决定。fishschool 组件的实际消费者是 antchovies_group，按网捕事件与数量等级工作。[EXP-FISH-003-C06](../knowledge/research/native-mechanisms/ocean_fishing-98c6b94f692d.json)

## 接入检查

按本次功能检查装槽与参数生效、提钩和断线、收获形态及鱼群出生。新增水中鱼、库存鱼和群体时，核对各自加载入口、动画与退出行为；实际表现需在具体 Mod 中确认。
