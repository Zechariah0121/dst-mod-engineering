# 开发任务地图

先选当前要交付的功能，再读对应指南和少量登记记录。跨组件问题继续沿“输入 → 权威状态 → 消费 → 退出与恢复”补齐关键合同，具体读取方法见[复杂任务读取](complex-task-reading.md)。

本地图基于当前 [CATALOG](../knowledge/CATALOG.json) 的296条记录整理，覆盖64条基础、13条 Native AI、110条 Native Core和109条机制研究。机制族404项 API 合同按登记记录的 `api_contracts` 计数；功能完成度与源码覆盖率尚无统一分母。每项列出的ID用于定向补读，可从[文件与命令入口](../docs/knowledge-integration.md)定位正文。未列出的主题可继续查目录，零命中时再核对目标源码。

Native AI Coding 每任务最多五条并使用十字段投影。下列 Core 记录保留 Coding HOLD，`EXP-*` 机制研究保持 `research/restricted/hold`，需显式 Reviewer 读取。指南中的工程建议和示例按各自前提使用，研究材料的准入、Scope、证据版本及未知依赖继续按[检索策略](kb-retrieval.md)核对。

## 主动技能、法术与自定义资源条

- 指南从[法术与自定义数值](spells-and-custom-stats.md)进入，涉及鼠标/手柄、预测或中断时补读[动作接入](action-lifecycle-architecture.md)。
- 已有登记入口包括 `NC-N002-FINAL-01` 的Action/RPC选择、`NC-N003-INT-03` 的两端SG接线、`EXP-ACT-001` / `EXP-ACT-002` 的普通PICK输入与权威执行样本，以及 `AI-N001-10` 的Replica/Classified/HUD分层。
- 局部覆盖集中于通用动作和具名消费者。目标法术的选中状态、资源消费、冷却与施法效果仍需追实际入口；普通PICK样本之外的动作分支和原生预测内部保留待核查。
- 项目需明确目标、范围、数值、失败/中断消费与死亡政策。下一步沿选定原版法术核对定义和消费点，再验拒绝、取消、重复请求、资源不足及真实远端输入。

## 有期限效果、存档与生命周期恢复

- 指南从[有期限效果恢复](timed-effect-recovery.md)进入，通用引用接线与资源归属见[保存恢复](save-recovery-architecture.md)、[组件任务归属](component-task-ownership.md)。
- 已有 `EXP-SAVE-001` 的旧GUID/嵌套postpass、`EXP-SAVE-004` 的Timer加载、`EXP-SAVE-005` 的Tracker监听身份、`EXP-MOVE-001` 的来源修改器，以及 `EXP-LIFE-001` / `EXP-LIFE-005` / `EXP-LIFE-006` / `EXP-LIFE-008` 的监听、组件、任务与实体退出合同。
- 恢复示例限同分片世界保存路径中的来源装置与目标实体。玩家session、Debuffable嵌套载体和跨分片引用需继续核查，各保存路径的映射能力保留差别；实际磁盘重启和联机结果待验。
- 项目需确定刷新/叠加、离线时间、死亡与缺目标政策。下一步核对宿主保存调用方，再验施加、换目标、取消、到期、组件卸载、来源/目标移除与独立进程读档。

## 装备效果、耐久、耗能与修理

- 指南从[装备耗能与修理](gear-fuel-repair.md)进入，防御和临时贡献补读[战斗与Buff](combat-buffs-containers.md)。
- 已有 `EXP-ITEM-004` 的装备替换与回调阶段、`EXP-GEAR-001` 的耗能/补燃料、`EXP-GEAR-002` 的次数耐久维修，以及 `EXP-COMBAT-001` / `EXP-COMBAT-002` 的护甲与Resistance具名链。
- 普通Fueled和Repairable接线已有研究；forge修理、缝纫、护甲修理需按实际组件另查。骨甲短护盾样本的作用范围、多个防御来源和远端菜单仍需目标场景核对。
- 项目需确定容量、消耗、维修材料/权限、破损和卸装政策。下一步追选定物品的装备/卸下消费者，再验换装、耗尽、补料、修理、重载、破损和其他来源效果保留。

## 远程武器、抛射与范围命中

- 指南从[投射物与命中](projectiles-hits.md)进入，伤害通道继续读[战斗与Buff](combat-buffs-containers.md)。
- 已有 `EXP-PROJ-001` 的Weapon/Projectile发射、`EXP-PROJ-002` 的ComplexProjectile与自定义更新、`EXP-PROJ-003` 的爆炸环境后果；基础归因和伤害入口见 `NC-N004-FINAL-01` / `NC-N004-FINAL-02` / `NC-N004-FINAL-03`。
- 静态链覆盖普通弹体、具名抛物线与落地消费者。高速物理、平台速度继承的实际表现、离屏结果及完整TOSS客户端链仍待验。
- 项目需确定追踪/穿透、多目标、PvP、地形破坏与属性快照政策。下一步核对选定命中回调的实际效果，再验目标失效、射程、落点、友军、归因和弹体清理。

## 可部署建筑与累计施工

- 指南从[放置与建筑](placement-buildings.md)进入，材料和工作回调继续读[物品、制作与采集](items-food-plants.md)。
- 已有 `DC-C01` / `DC-C02` / `DC-C03` 的部署门禁/单件交接、`EXP-BUILD-001` 的预览与附属表现、`EXP-BUILD-002` 的套件/拆除、`EXP-BUILD-003` 的施工累计投料；制作初始化见 `EXP-CRAFT-002`。
- moon_device、firesuppressor和套件是具名样本。施工蓝图转换、可收起建筑状态迁移、更多材料类型和完整施工客户端链需继续研究；第三方放置Mod兼容尚需实际验收。
- 项目需确定退款、回收套件、业务进度、占用与拆除政策。下一步分别核对预览与服务器门禁，再验部署失败返还、旋转、多人投料、中断、锤击、保存重载和远端显示。

## 生物AI、巢穴与种群

- 指南从[生物AI](creature-ai-practical.md)和[巢穴种群](nests-population.md)进入，需要节点调度与SG时再读[角色、Brain与StateGraph](characters-brains-stategraphs.md)。
- 已有 `EXP-AI-003` 的PriorityNode、`EXP-AI-006` 的DoAction、`EXP-AI-008` / `EXP-AI-009` / `EXP-AI-010` 的追击/回位/逃跑，以及 `EXP-NEST-001` / `EXP-NEST-002` / `EXP-NEST-003` 的种群开关、外部所有权与应急配额。
- 普通固定物种计数、具名猎犬/兔/猪/蜂巢消费者已有局部链。原生寻路、混合稀有池、全部物种分支和巢内逐个体状态恢复仍需定向核查。
- 项目需确定种群容量、个体身份、转家/回巢政策和行为优先级。下一步追目标Brain与SG消费者，再验丢失目标、拥堵逃跑、入巢、孩子死亡、家被移除、sleep/wake与读档补员。

## 角色形态、技能树与Boss阶段

- 导航从[角色与StateGraph](characters-brains-stategraphs.md)进入，美术切换见[角色与装备美术](character-and-equipment-art.md)。
- 已有 `STUI-P01` / `STUI-P02` / `STUI-P03` / `STUI-P04` 的技能树UI登记与布局、`NC-N003-INT-05` / `NC-N003-INT-07` 的SG时点/内存归属，以及 `AI-N001-13` 的换角、死亡与迁移边界。
- 当前地图仅确认这些局部入口。角色变形的组件/装备/存档交接、技能解锁到实际效果、完整Boss阶段转换与退出链尚未在此建立合同闭包，需选定原版对象补研。
- 项目需明确阶段条件、可逆性、技能保留、死亡/重连与动画资源。下一步先画目标功能的状态与所有者，再定点核对阶段进入/退出、取消、重入、死亡、读档及远端表现。

## 锅料理、调味与农作

- 料理从[独立锅料理](cooker-dishes.md)进入，农田与作物从[农作指南](farming-crops.md)进入。
- 已有 `EXP-COOK-001` / `EXP-COOK-002` 的注册与候选、`EXP-COOK-005` / `EXP-COOK-006` / `EXP-COOK-007` 的保存/调味/真实变体；农作见 `EXP-FARM-001` / `EXP-FARM-002` / `EXP-FARM-003`，通用生长见 `EXP-GROW-001` / `EXP-GROW-002`。
- 料理链限具名cookpot/spicer消费者，调味Buff细节要继续查目标Buff。农作限固定位置的普通作物，移动植株重索引、全部魔法催长、研究册与完整客户端显示保留缺口。
- 项目需确定配方优先级、效果、成长阶段、产物与水肥数值。下一步分别验候选冲突、成品资源、调味食用、断料/变质，以及种子单件、每格灌溉、阶段压力、收获和独立重启恢复。

## 自定义弹窗、HUD与资源表现

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
