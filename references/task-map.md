# 开发任务地图

先选当前要交付的功能，再读对应指南和少量登记记录。跨组件问题继续沿“输入 → 权威状态 → 消费 → 退出与恢复”补齐关键合同，具体读取方法见[复杂任务读取](complex-task-reading.md)。

本地图基于当前 [CATALOG](../knowledge/CATALOG.json) 的302条记录整理，覆盖64条基础、13条 Native AI、110条 Native Core和115条机制研究。机制族424项 API 合同按登记记录的 `api_contracts` 计数；功能完成度与源码覆盖率尚无统一分母。每项列出的ID用于定向补读，可从[文件与命令入口](../docs/knowledge-integration.md)定位正文。未列出的主题可继续查目录，零命中时再核对目标源码。

默认 MCP 可直接使用 `get_entry(id=...)`，或先用 `lookup_api(symbol=...)` 再执行 `results[].followup`。命令行为 `run_kb.py review ID` / `run_kb.py review --api "符号"`，默认读取公共知识，无需准备来源。超预算时原样执行 `continuation`，也可按实际返回的 pointer 直接选对象。显式来源环境及证据展开按各自的来源校验要求执行。完整对象交付、来源核验、Coding 准入和游戏验证各按响应状态判断。

Native AI Coding 每任务最多五条并使用十字段投影。下列 Core 记录保留 Coding HOLD，`EXP-*` 机制研究保持 `research/restricted/hold`，默认公共读取使用 Reviewer。指南中的工程建议和示例按各自前提使用，研究材料的准入、Scope、证据版本及未知依赖继续按[检索策略](kb-retrieval.md)核对。

## 主动技能、法术与自定义资源条

- 普通手持法杖地面施法先读[黄杖主动技能链](chain-active-skill.md)，轮盘、自定义数值或其他选点形式继续读[法术与自定义数值](spells-and-custom-stats.md)，通用中断见[动作接入](action-lifecycle-architecture.md)。
- `EXP-CHAIN-SPELL-001` 连接普通鼠标空点CASTSPELL候选、预测发送、服务器执行帧、SpellCaster、末次次数消费和stafflight退出/组件恢复。通用接线仍参考 `NC-N002-FINAL-01`、`NC-N003-INT-03`、`EXP-ACT-001` / `EXP-ACT-002` 与 `AI-N001-10` 的各自Scope。
- 新链限yellowstaff、普通人形玩家、无活动物品/特殊右键覆盖的地面空点。手柄、CASTAOE、轮盘、地图选点、热/理智范围公式、原生预测和真实远端结果继续待查或待验。
- 项目需明确目标、范围、数值、失败/中断消费与死亡政策。下一步核对目标法术实际入口，重点验执行帧前中断、回调false/异常、末次物品移除、独立效果退出和磁盘恢复。

## 有期限效果、存档与生命周期恢复

- `EXP-CHAIN-EFFECT-001` 对照原版具名伤害 Buff 和自有世界装置的不同恢复入口。[有期限效果链](chain-timed-effect.md)包含可运行装置、目标、普通伤害计算、剩余时间恢复和到期清理。
- 指南从[有期限效果恢复](timed-effect-recovery.md)进入，通用引用接线与资源归属见[保存恢复](save-recovery-architecture.md)、[组件任务归属](component-task-ownership.md)。
- 已有 `EXP-SAVE-001` 的旧GUID/嵌套postpass、`EXP-SAVE-004` 的Timer加载、`EXP-SAVE-005` 的Tracker监听身份、`EXP-MOVE-001` 的来源修改器，以及 `EXP-LIFE-001` / `EXP-LIFE-005` / `EXP-LIFE-006` / `EXP-LIFE-008` 的监听、组件、任务与实体退出合同。
- 来源装置和目标实体示例已通过同分片真实存档重启。玩家 session、嵌套 Buff 的实际重启和跨分片引用各有单独验证范围。
- 项目需确定刷新/叠加、离线时间、死亡与缺目标政策。下一步核对宿主保存调用方，再验施加、换目标、取消、到期、组件卸载、来源/目标移除与独立进程读档。

## 装备效果、耐久、耗能与修理

- 带持续效果的装备先读[Molehat装备链](chain-equipment.md)，耗能/修理细节见[装备耗能与修理](gear-fuel-repair.md)，防御继续读[战斗与Buff](combat-buffs-containers.md)。
- `EXP-CHAIN-GEAR-001` 连接HEAD装备成员、classified事件、PlayerVision、表现提交、耗能、卸下与正燃料记录恢复。已有 `EXP-ITEM-004`、`EXP-GEAR-001` / `EXP-GEAR-002`、`EXP-COMBAT-001` / `EXP-COMBAT-002` 继续支持各自装备、维修和防御范围。
- 新链限定molehat普通HEAD和正燃料保存记录，视野止于原生表现调用。异常零燃料存活记录的产品政策、所有夜视组合、死亡/换角/session/跨分片与画面结果仍需核查；forge、缝纫和护甲修理另查实际组件。
- 项目需确定容量、消耗、维修材料/权限、破损和卸装政策。下一步验首次快照、换装后重算、耗尽清槽、卸装停耗、正燃料重载与其他夜视来源保留，再观察实际远端画面。

## 远程武器、抛射与范围命中

- 指南从[投射物与命中](projectiles-hits.md)进入，伤害通道继续读[战斗与Buff](combat-buffs-containers.md)。
- 已有 `EXP-PROJ-001` 的Weapon/Projectile发射、`EXP-PROJ-002` 的ComplexProjectile与自定义更新、`EXP-PROJ-003` 的爆炸环境后果；基础归因和伤害入口见 `NC-N004-FINAL-01` / `NC-N004-FINAL-02` / `NC-N004-FINAL-03`。
- 静态链覆盖普通弹体、具名抛物线与落地消费者。高速物理、平台速度继承的实际表现、离屏结果及完整TOSS客户端链仍待验。
- 项目需确定追踪/穿透、多目标、PvP、地形破坏与属性快照政策。下一步核对选定命中回调的实际效果，再验目标失效、射程、落点、友军、归因和弹体清理。

## 可部署建筑与累计施工

- 可收起物先读[Portabletent部署/收起链](chain-deployable.md)，套件和累计施工读[放置与建筑](placement-buildings.md)，材料/工作回调见[物品、制作与采集](items-food-plants.md)。
- `EXP-CHAIN-DEPLOY-001` 连接非堆叠portabletent_item的预览、普通DEPLOY/DISMANTLE、HAMMER、动画转换、uses交接与稳定形态保存。既有 `DC-C01` / `DC-C02` / `DC-C03`、`EXP-BUILD-001` / `EXP-BUILD-002` / `EXP-BUILD-003` 及 `EXP-CRAFT-002` 保留各自门禁、套件、施工和制作范围。
- 新链只迁移具名uses，并明确收起动画中的保存记录缺少续行状态。皮肤/wetness/额外组件与GUID迁移、完整燃烧、施工蓝图转换和第三方放置兼容仍需定向研究或实际验收。
- 项目需确定退款、回收物、进度、占用与拆除政策。下一步验生成失败后的实际物品归属、提交前取消、睡眠唤醒/锤击、动画与移除并发，以及稳定形态和动画中独立进程读档。

## 生物AI、巢穴与种群

- 指南从[生物AI](creature-ai-practical.md)和[巢穴种群](nests-population.md)进入，需要节点调度与SG时再读[角色、Brain与StateGraph](characters-brains-stategraphs.md)。
- 已有 `EXP-AI-003` 的PriorityNode、`EXP-AI-006` 的DoAction、`EXP-AI-008` / `EXP-AI-009` / `EXP-AI-010` 的追击/回位/逃跑，以及 `EXP-NEST-001` / `EXP-NEST-002` / `EXP-NEST-003` 的种群开关、外部所有权与应急配额。
- 普通固定物种计数、具名猎犬/兔/猪/蜂巢消费者已有局部链。原生寻路、混合稀有池、全部物种分支和巢内逐个体状态恢复仍需定向核查。
- 项目需确定种群容量、个体身份、转家/回巢政策和行为优先级。下一步追目标Brain与SG消费者，再验丢失目标、拥堵逃跑、入巢、孩子死亡、家被移除、sleep/wake与读档补员。

## 角色形态、技能树与Boss阶段

- 同实体两态生物先读[普通猪人阶段链](chain-creature-stage.md)，角色与其他SG见[角色与StateGraph](characters-brains-stategraphs.md)，美术切换见[角色与装备美术](character-and-equipment-art.md)。
- `EXP-CHAIN-STAGE-001` 连接普通pigman的触发、WereBeast、阶段属性、Brain/SG消费者、回退、卸载与恢复字段。已有 `STUI-P01` / `STUI-P02` / `STUI-P03` / `STUI-P04` 支持技能树UI局部入口，`NC-N003-INT-05` / `NC-N003-INT-07`、`AI-N001-13` 保留SG与换角/死亡/迁移的原范围。
- 新链限normal/werepig，排除特殊猪变体。玩家变形的装备/组件交接、技能解锁至效果与完整Boss阶段仍需补研；transform期间到期、死亡到移除间任务和受伤形态读档顺序保留待验边界。
- 项目需明确阶段条件、可逆性、保血、技能/领袖保留和死亡政策。下一步核对目标阶段所有者，再验重复请求、攻击/变形中断、到期、显式回退、组件卸载与受伤状态独立重载。

## 锅料理、调味与农作

- 料理从[独立锅料理](cooker-dishes.md)进入，农田与作物从[农作指南](farming-crops.md)进入。
- 已有 `EXP-COOK-001` / `EXP-COOK-002` 的注册与候选、`EXP-COOK-005` / `EXP-COOK-006` / `EXP-COOK-007` 的保存/调味/真实变体；农作见 `EXP-FARM-001` / `EXP-FARM-002` / `EXP-FARM-003`，通用生长见 `EXP-GROW-001` / `EXP-GROW-002`。
- 料理链限具名cookpot/spicer消费者，调味Buff细节要继续查目标Buff。农作限固定位置的普通作物，移动植株重索引、全部魔法催长、研究册与完整客户端显示保留缺口。
- 项目需确定配方优先级、效果、成长阶段、产物与水肥数值。下一步分别验候选冲突、成品资源、调味食用、断料/变质，以及种子单件、每格灌溉、阶段压力、收获和独立重启恢复。

## 自定义弹窗、HUD与资源表现

- `EXP-CHAIN-SKILL-HUD-001` 定位背包动作、服务器扣费和 owner 定向复制的依据。[资源与 HUD 链](chain-skill-resource-hud.md)包含可运行示例、界面重建与客户端验收步骤。
- 输入与HUD从[Screen与控件](ui-screen-input.md)进入，资产接线读[动画资源](assets-animation.md)，声音/粒子读[音效与粒子](audio-particles.md)。
- 已有 `EXP-UI-001` / `EXP-UI-002` / `EXP-UI-003` 的Screen栈、control消费与Controls重建，`AI-N001-10` 的分层视图，以及 `EXP-PRES-001` / `EXP-PRES-002` / `EXP-PRES-003` 的具名动画、声音和FX退出样本。
- 本地控件静态合同与少量具名FX已有研究。具体SCML/build/symbol、分辨率、焦点、音效与粒子效果需读取项目资产并实际查看；HUD业务数据就绪和服务器权限要另接目标功能。
- 项目需提供资产、布局、受众和输入方案。下一步验首次快照、dirty更新、HUD重建、幽灵切换、隐藏/关闭、按放配对、手柄与远端表现，并检查重复打开后的监听和声音退出。

## 船上装置与海钓

- 船体与装置从[船与平台](boats-platforms.md)进入，新增钓具或鱼种从[海钓指南](ocean-fishing.md)进入。
- 已有 `EXP-OCEAN-001` / `EXP-OCEAN-002` / `EXP-OCEAN-003` 的平台成员、推力与制动，`EXP-FISH-001` / `EXP-FISH-002` / `EXP-FISH-003` 的竿饵、收获形态交接与鱼群生成。
- 原生平台/碰撞、实际航速、落船与网络显示待验。固定鱼点完整补员/存档、海钓进行中的恢复、全部自定义船型与虚拟海洋实现需继续核查。
- 项目需确定动力/耗能、制动组合、鱼饵数值、鱼种注入与生成时序。下一步验上下船、装置移除、动力叠加、存档恢复，以及抛竿取消、鱼挣脱、停止海钓、收获归属和新鱼Prefab预加载。

## 世界袭击、阶段事件与迁移

- 世界周期从[世界事件与生成](world-events-spawning.md)进入，跨分片交接补读[网络与RPC](networking-rpc.md)和[保存恢复](save-recovery-architecture.md)。
- 已有 `EXP-WEVENT-001` / `EXP-WEVENT-002` / `EXP-WEVENT-003` 的袭击配置、玩家配额和暂停恢复，`EXP-WORLD-001` 的WorldState，`EXP-WORLD-002` 的Shard RPC处理器身份，以及 `EXP-WORLD-003` / `EXP-WORLD-004` 的玩家迁移Lua交接。
- hounded具名研究限所列消费者。其他世界事件、全部暂停监听者、组件运行中移除/重装、跨分片交付和原生会话写入均需任务级补读与验证。
- 项目需确定波次、玩家资格、预警、暂停与持久化政策。下一步验玩家退出/加入、海洋/洞穴落点、暂停再恢复、读档、重复登记，以及本次涉及的跨分片失败路径。

## 世界生成、布局、地皮与空间查询

- 生成与地形从[世界生成与空间](worldgen-spatial.md)进入，注册/加载问题补读[Lua与Hook](core-lua-hooks.md)。
- 已有 `EXP-WG-001` / `EXP-WG-002` / `EXP-WG-003` / `EXP-WG-004` / `EXP-WG-005` 的worldgen环境、Room/Task、节点填充、静态布局与地皮；空间查询见 `SPATIAL-CODE-RELATIVE-ABSOLUTE` / `SPATIAL-CODE-WALK-CHECKS` / `SPATIAL-CODE-FAILURE-POLICY`。
- 生成研究覆盖选定Lua链，native连通、所有seed、海洋/洞穴专用分支、运行时填海、旧档地皮映射与室内系统尚需专项核查。
- 项目需明确世界类型、布局数量、地皮资产、旧档和兼容目标。下一步核对实际生成入口，再按目标世界尺寸与多seed验落位、数量、通路、资源、小地图、存档和远端通行。

## 开始实施与交付前

跨任务公共入口包括 `FACT-DST-007` 的PostInit时点、`AI-N001-03` / `AI-N001-04` 的依赖就绪/构造阶段，以及 `AI-N001-09` 的资源Owner。先读本次真正涉及的记录，Native AI Coding 的五条预算按整个任务计算。来源变化时按[源码维护](../docs/source-compatibility.md)定位和逐引用复核，继续保留各记录原Scope。

兼容目标要落实到具体Mod、版本和共享入口；当前地图未完成跨Mod组合盘点。性能问题沿[实用优化](practical-optimization.md)测实际热点。按[测试与交付](testing-release.md)区分静态检查、服务器行为、真实客户端与存档结果，命中的测试线索保留“尚待执行”状态，待目标项目实际运行后再记录结果。
