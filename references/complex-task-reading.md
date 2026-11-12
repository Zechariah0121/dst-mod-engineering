# 复杂开发问题的渐进读取

先把问题写成实际行为链，再读决定当前实现的合同。已经明确的条件、交接与退出可在所选记录内闭合时，就回到目标 Mod 核对接线。出现版本差异、排除范围或缺少真实消费者时，沿缺口追局部源码。

以下五类问题展示首读与条件化补读。条目自身的 Scope、证据类型、状态和更正继续生效；实际目录与文件指针从当前 CATALOG 获取。

## 怎样拆开并读完整

先在项目中找到触发入口、权威执行者、状态/实体所有者、产物或属性消费者，以及停止和恢复入口。依据本次需求，明确哪些数据要跨读档、哪些结果要等最终产物或状态确认。自定义 Mod 的实际文件与回调决定后续补读方向。

目录用于找候选。选中记录后读取完整 claim 或 API 对象，连同 Scope、状态、unknowns、compatibility、顶层来源/limitations 和实际 evidence refs。API 要读参数、返回、前提、副作用、生命周期与 visibility。文件读取也可一次读所选条目全文，再按其本文件引用定位证据。Core 的 correction_refs 与历史来源沿原文展开。[检索规则](kb-retrieval.md) · [机制族合同](../docs/native-mechanisms.md)

- 机制族完整 MCP 可用 `get_entry(id="EXP-FISH-001", projection="reviewer", view="reviewer", pointer="/api_contracts/2", max_bytes=24000)`。API 查找用无参数符号，例如 OceanFishingTackle:SetupLure，并显式选择 native_mechanism/reviewer。
- Core 的逐 claim 可用目录 `read_public_entry(id="DC-C01", purpose="review", pointer="/claims/1", max_bytes=24000)`。完整模式可用 `get_entry(id="NC-N004-FINAL-07", projection="reviewer", view="reviewer")`，再按实际 typed_atoms/record_pointer 展开。Core 的 get_entry 调用省略 pointer 与自定义 max_bytes。
- 预算出现 withheld 或 whole_value_delivered=false 时，按返回提示续读完整原子并展开引用。完整模式与目录模式按当前会话实际工具集选择。file-local 事件处理器按其登记事件接入，公开方法按原文接收者调用。

## 巢穴昼间放出、夜晚回巢，结算与读档数量正确

先找巢构造、孩子 Brain/SG 与回巢结算点。需要知道 inside/outside 容量、放出和补员各自的开关，生成与接管回调的时点，以及孩子删除前能读取什么。

| 顺序与补读条件 | 完整读取对象 | 得到的开发判断 |
| --- | --- | --- |
| 初读库存与放出 | EXP-NEST-001，claims 0～5，API 0～4 | SetMaxChildren 会重算 inside，普通放出、手工 SpawnChild 与补充分别受自己的条件约束 |
| 接回巢结算 | EXP-NEST-002，claims 0～5，API 0～2 | TakeOwnership、GoHome 与 OnChildKilled 的成员/监听顺序，childgoinghome/ongohome 的 Remove 前窗口 |
| 按昼夜控制 | N006-READY-F02 的初次应用/receiver合同，再读 EXP-WORLD-001 的 WatchWorldState/StopWatchingWorldState | 在依赖就绪阶段应用当前状态，后续变化由相同函数身份处理和解除 |
| 本题要求存读档 | EXP-SAVE-002，claims 0～5 | 组件 postpass 接外部孩子，本宿主 prefab postpass 随后执行，组件可能已因烧毁移除 |
| 孩子尚无入巢动作 | EXP-AI-009，claims 2～6 与 HomeSeeker:SetHome/GoHome | 将移动、home 引用和目标的收纳消费者连起来 |

普通数量库存与回巢前结算已有合同，按这些行为核对 Mod 即可。要求保持每只孩子生命/装备、换家容量、特殊混合池或外部计时模式时，再查所选收纳与生成消费者。巢的现有数量保存合同可沿原组件使用。[巢穴接线](nests-population.md)

## 冬季增强洞穴袭击，活动暂停并支持恢复

先确认修改既有 hounded 的最终 Hook 阶段，以及保留当前倒计时还是立即重规划。接着确定活动要求影响已警告波、延迟玩家波还是后续规划。

| 顺序与补读条件 | 完整读取对象 | 得到的开发判断 |
| --- | --- | --- |
| 初读配置与预警 | EXP-WEVENT-001，完整 claims/API | SetSpawnData 整体替换，cave 后续覆盖、模式/缓存与重规划各有实际时序 |
| 接活动暂停和读档 | EXP-WEVENT-003，完整 claims/API | pause/unpause 的 source/reason、SpawnModeNever、玩家 missing 状态和保存结构 |
| 冬季由观察驱动 | N006-READY-F02 与 EXP-WORLD-001 | 首次应用和观察的接收者、时点、解绑责任 |
| 要准确生成数或自定目标 | EXP-WEVENT-002，完整 claims/API | 配额先扣的时点、SummonSpawn 的返回实体、ForceReleaseSpawn 的调用与返回边界 |

ForcePlanNewAttack、OnPauseHounded 与 OnUnpauseHounded 是构造闭包里的 local 事件处理器。其 API 原子说明 world 事件和 payload，项目通过对应事件接入。暂停和禁用已有完整静态合同，先据此确定玩法需要的效果。[世界事件与袭击](world-events-spawning.md)

762172 延迟波的保存/还原数组形状差异已有 NSF 与 EI。若产品要求精确恢复这部分，沿目标版本的 delayed/missing 实际消费链设计修复并验证。已有源码结构证据可用于定位问题，额外重试或管理框架由具体结果要求决定。[袭击恢复边界](world-events-spawning.md)

## 新鱼在指定海域出现，专用鱼饵能钓并上岸

将鱼种选择、Prefab 加载、鱼饵生效、上钩和产物交接分别放到其实际消费者。先读生成，再读钓具，最后串完整钓获链。

| 顺序与补读条件 | 完整读取对象 | 得到的开发判断 |
| --- | --- | --- |
| 初读鱼种与生成 | EXP-FISH-003，claims 0～4、6～7，API 0～1 | 季节/地皮权重指向鱼种，水中/库存/schoolherd 定义需在实际加载入口可解析 |
| 接专用鱼饵 | EXP-FISH-001，完整 claims 与 SetupLure、Cast API | 公共第二槽标签到完整 lure_data，再到缓存、落水 hook 和兴趣计算 |
| 接咬钩到产物 | EXP-FISH-002，完整 claims/API | SetRod 换目标、提钩、张力/体力、单次鱼饵、StopFishing 与 CatchFish 的先后 |
| 需求选择固定补员鱼点 | EXP-FISH-003 的固定 shoal 消费者，再读 EXP-NEST-001 | childspawner 的补员与放出规则可直接复用 |
| 奖励必须进玩家库存 | EXP-ITEM-001 的 GiveItem 完整合同 | 处理并堆、满库存与掉落对应的最终 owner/槽位 |

这些条目已贯穿原竿正常钓获。fishcaught 后还有投掷落地与库存形态交接，奖励按目标终点接消费者。新 Mod 的动画、Prefab 加载时序或新 projectile 缺字段时，先查自己的定义和回调，再沿对应局部消费者追源。自定义 SG、完整虚拟海洋、拖网或海钓中途保存另按需求补读。[海钓接线](ocean-fishing.md)

## Timer、Tracker 与来源 modifier 恢复异常

先在项目中标出 Timer 宿主/名字、Tracker 槽/目标、贡献列表/source/key，以及实际 OnLoad/postpass 次数。效果持续时间的离线政策由项目决定。

| 顺序与补读条件 | 完整读取对象 | 得到的开发判断 |
| --- | --- | --- |
| 初读时长变化 | EXP-SAVE-004，完整 claims 与 Timer:OnLoad API | 同一 timeleft 重放会按本次 GetTime 重算截止时间，同名替换与独立任务分别核对 |
| 旧目标删除影响新引用 | EXP-SAVE-005，完整 claims/API | TrackEntity 新闭包覆盖槽，ForgetEntity 能释放当前记录所持身份，旧监听按真实关系追踪 |
| 需等引用接回 | EXP-SAVE-001，完整 claims/API | refs、逐渐形成的 newents、本宿主组件与 prefab postpass 的分发 |
| 重施与到期解除贡献 | EXP-MOVE-001，claims 0～2、5，SourceModifierList:SetModifier/RemoveModifier/Reset API | 确认聚合与 dirtycb，再按自己的 source/key 解除贡献 |
| 涉及暂停、长更新、玩家换身或 buff 宿主 | NC-N004-FINAL-07 的所需完整 claim | 普通 Timer、WorldSettingsTimer、buff 和玩家各自有不同恢复入口 |
| 实际采用保温来源 buff | EXP-SURV-004，claims 2～6 与保温 API | 借鉴有限保存后 Attach 重施来源的具名消费者，保留其760944版本范围 |

上述常见恢复边界已有合同。先将自己的调用链与这些时点对齐。跨分片引用、其他实体恢复总序、未确定的属性消费者或当前游戏版本差异，才沿受影响入口追局部源码。贡献数值与恢复业务条件按本功能保留，运行期句柄按实际所有者重建。[有期限效果的恢复示例](timed-effect-recovery.md)

## 吸附放置储物套件，读档可用，锤毁释放物品

先选择库存 DEPLOY 或配方 BUILD，然后定位预览提交点、目标 master 构造、onbuilt 和 HAMMER 回调。

| 顺序与补读条件 | 完整读取对象 | 得到的开发判断 |
| --- | --- | --- |
| 初读吸附 | EXP-BUILD-001，完整 claims/API | 预览变换、override 测试、实际提交点与附属表现所有者 |
| 接套件与目标 | EXP-BUILD-002，完整 claims/API | MakeDeployableKitItem 参数、onbuilt payload/旋转、目标业务构造和具体 HAMMER 清理 |
| 核对部署基础 | DC-C01～03 的所需完整 claim | CUSTOM 公共 predicate、主机复检、普通单件移交和动作结果 |
| 本题涉及容器与读档 | EXP-ITEM-002 完整合同，EXP-SAVE-001 的 Container 嵌套恢复链 | 物品归容器，实际来源、槽位、共享映射与业务标量按各自合同处理 |
| 多个掉落回调或组件替换 | EXP-CRAFT-004 完整合同 | 旧/新 workable 身份、onwork/onfinish/workfinished 的产物责任 |

常规接线已有来源。读档所需业务组件放在正常构造入口，摆放效果沿其事件接线。新增收起建筑保留状态、特殊地图几何、第三方放置改写或完整燃烧要求时，再追对应状态迁移或具体消费者。[建筑接线](placement-buildings.md)

## 什么时候结束补读

能对本次需求说明入口和参数、当前消费对象、关键回调/副作用、停止责任与必要恢复阶段，且相关未知项已明确时，就回到项目实施或给出范围内结论。问题只涉及现成拟饵时，首读钓具合同即可，鱼群生成和库存奖励按新增需求展开。
