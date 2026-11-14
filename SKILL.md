---
name: dst-mod-engineering
description: 开发、设计、审查与验证《饥荒联机版》DST Mod；按任务检索工程知识库并核对当前源码，处理角色、法术、联机、存档、资源、崩溃、兼容与案例研究。不用于普通游戏攻略或角色强度讨论。
---

# DST 模组工程

`v2026.11.13.4`：302 条登记知识（64 基础 + 13 Native AI + 110 Core + 115 机制研究），配套开发脚本、来源准备工具与只读 MCP。默认发现并读取公共知识；当前来源按相关证据独立核对，维护更正由统一入口生成候选。[安装](docs/install-and-use.md) · [公共读取](docs/public-reader.md) · [English](README.en.md)

## 工作顺序

1. 确认任务、实际 Mod 副本、源码版本和触发环境；接手项目先读入口、配置与交接说明。
2. 按问题查库；多组件任务按状态归属、消费和恢复分开补读完整合同，再核对当前原版的定义、调用方、端别、初始化、退出和保存。源码用于确认实际行为与接入合同；符合需求的机制直接复用，自有实现按当前需求简化，独立判断其结构与写法是否值得沿用。
3. 先建立“需求 → Mod 实现 → 原版契约 → 验证方法”，优先用现有入口、直接调用和局部函数完成。新增抽象或防护需对应当前依赖、合法缺省或可达时序。玩法数值、效果与补偿取舍按项目约定；已有授权的必要步骤继续执行。
4. 覆盖本次涉及的取消、移除、死亡、重连和读档路径，保留协作者改动。验证后交付文件、依据、实际结果和待验项。

## 查库与来源

默认 MCP 检索和公共材料阅读无需准备来源或索要源码路径。需要当前源码支持的实质性开发、审查或研究前，从实际包根运行：

```text
python -B -X utf8 prepare_sources.py --source "<scripts.zip绝对路径>"
```

来源准备仅由维护任务显式触发；源码路径必须明确，准备和重连见[源码维护](docs/source-compatibility.md)。简单机械编辑无需重复查库。

优先使用已连接 MCP 的 `search_kb(query=...)` 或 `get_context_bundle(task_description=...)`，默认 Reviewer 可发现四族知识与任务指南，并返回相关完整正文对象；没有 `objects` 的命中仍只是导航。无服务时，用 `python -B -X utf8 run_kb.py find "任务或符号"` 定位，再用 `run_kb.py read ID` 审阅，或从 `knowledge/CATALOG.json` 按 file/pointer 读取。保留 Scope、类型、版本、更正和三轴状态；公共可读不授予 Coding 准入。Native AI Coding 使用十字段、每任务最多五条；Core 保持 Coding HOLD，机制研究保持 research/restricted/hold。完整规则见[检索策略](references/kb-retrieval.md)。

公共审阅使用 `get_entry(id=...)`，按符号定位用 `lookup_api(symbol=...)` 并执行返回的 `results[].followup`；默认分别为 Reviewer 和全部登记族。命令行可用 `run_kb.py review ID` / `run_kb.py review --api "符号"`，均无需完整来源；对象超预算时原样执行 `continuation`。pointer/cursor、完整 owner 与预算见[公共读取](docs/public-reader.md)。显式 Coding、历史来源环境和证据展开仍走原有来源与准入校验。

局部来源变化不阻断历史公共正文；按[独立证据快照](docs/evidence-snapshots.md)区分精确匹配、变化、缺失和未评估，不以旧缓存冒充新来源核验。维护知识库时使用[作者维护入口](docs/author-maintenance.md)生成更正候选，文本重建不代表语义审批或游戏验证。

## 按问题读取

首次接入或技能未识别时读 [Agent 接入](references/agent-setup.md)；缺少素材工具时读 [工具安装与首次验证](references/tool-bootstrap.md)，选择适合平台和当前产物的最小方案。

网页附件与云端协作见 [网页使用指南](references/web-chat.md)。

| 当前任务 | 参考文件 |
|---|---|
| 常见开发任务已有依据、局部缺口与项目所需信息 | [task-map.md](references/task-map.md) |
| 黄杖普通鼠标地面施法、执行帧、末次消费与星体退出 | [chain-active-skill.md](references/chain-active-skill.md) |
| Molehat 装备标签、夜视消费者、耗能与正燃料恢复 | [chain-equipment.md](references/chain-equipment.md) |
| Portabletent 部署/收起、耐久交接与稳定形态保存 | [chain-deployable.md](references/chain-deployable.md) |
| 普通猪人两态、Brain/SG消费者、回退与恢复边界 | [chain-creature-stage.md](references/chain-creature-stage.md) |
| 有期限伤害倍率、同分片目标重连与剩余时间恢复 | [chain-timed-effect.md](references/chain-timed-effect.md) |
| 背包动作、服务器扣费、资源同步和 HUD 重建 | [chain-skill-resource-hud.md](references/chain-skill-resource-hud.md) |
| 跨组件问题、首读与条件化补读、预算不足后的读取 | [complex-task-reading.md](references/complex-task-reading.md) |
| 登记知识文件读取、MCP 检索、准入与证据 | [kb-retrieval.md](references/kb-retrieval.md) |
| 网页 AI、技能 ZIP、普通附件、云端检查与本机交接 | [web-chat.md](references/web-chat.md) |
| Claude Code / Cursor / Copilot / Codex 接入、显式读取、能力限制 | [agent-setup.md](references/agent-setup.md) |
| 缺少动画工具、下载来源、安装授权、首次编译验证 | [tool-bootstrap.md](references/tool-bootstrap.md) |
| 首次定位游戏、当前源码、Python、工具版本 | [environment-tools.md](references/environment-tools.md) |
| 入口封装、架构简化、复杂 Mod 分层、状态归属与失败恢复 | [complex-mod-architecture.md](references/complex-mod-architecture.md) |
| 可取消交互的输入、预测、权威结算与表现退出 | [action-lifecycle-architecture.md](references/action-lifecycle-architecture.md) |
| 事件订阅身份、解绑、Replica 构造/附着/移除 | [event-replica-lifecycle.md](references/event-replica-lifecycle.md) |
| 组件安装/卸载、更新登记、定时任务与资源归属 | [component-task-ownership.md](references/component-task-ownership.md) |
| GUID 引用、嵌套保存、postpass、读档副作用与任务恢复 | [save-recovery-architecture.md](references/save-recovery-architecture.md) |
| modmain/prefab 环境、Class、Hook、配置、加载错误 | [core-lua-hooks.md](references/core-lua-hooks.md) |
| Entity、Prefab、组件初始化、原版组件复用 | [entities-components.md](references/entities-components.md) |
| 角色、自定义生物、Brain、Stategraph、移速、跟随与骑乘 | [characters-brains-stategraphs.md](references/characters-brains-stategraphs.md) |
| 生物索敌、追击、逃跑、回到领地与入巢 | [creature-ai-practical.md](references/creature-ai-practical.md) |
| 巢穴种群、生成补员、回巢与个体身份 | [nests-population.md](references/nests-population.md) |
| 新增法术、魔力/能量条、睡眠恢复与完整接入流程 | [spells-and-custom-stats.md](references/spells-and-custom-stats.md) |
| netvar、Replica、RPC、Shard RPC、客户端与服务端 | [networking-rpc.md](references/networking-rpc.md) |
| 有期限目标效果、Timer/Tracker 与来源 modifier 恢复 | [timed-effect-recovery.md](references/timed-effect-recovery.md) |
| 定时效果、死亡复活、事件解绑、存档与迁移 | [lifecycle-save.md](references/lifecycle-save.md) |
| HUD、Widget、输入、Action、施法与预测 | [ui-actions-controls.md](references/ui-actions-controls.md) |
| 自定义弹窗、焦点、按键消费与本地 HUD 挂载 | [ui-screen-input.md](references/ui-screen-input.md) |
| 伤害、Buff、容器、冷却、范围查询 | [combat-buffs-containers.md](references/combat-buffs-containers.md) |
| 物品转移与堆叠、装备、投掷、维修、制作采集、锅料理、树木种植 | [items-food-plants.md](references/items-food-plants.md) |
| 装备耐久、持续耗能、补燃料与材料修理 | [gear-fuel-repair.md](references/gear-fuel-repair.md) |
| 远程武器、投射物、坐标抛射与范围命中 | [projectiles-hits.md](references/projectiles-hits.md) |
| 建筑预览、套件部署、锤击拆除与累计施工 | [placement-buildings.md](references/placement-buildings.md) |
| 新增独立锅料理、调味变体、图标与台词接入 | [cooker-dishes.md](references/cooker-dishes.md) |
| 农田水肥、照料、阶段压力、种子与作物收获 | [farming-crops.md](references/farming-crops.md) |
| 船上装置、平台归属、推力、帆与制动 | [boats-platforms.md](references/boats-platforms.md) |
| 世界阶段事件、袭击波、预警与暂停恢复 | [world-events-spawning.md](references/world-events-spawning.md) |
| 海钓钓具、新鱼、收获形态与鱼群生成 | [ocean-fishing.md](references/ocean-fishing.md) |
| 地图生成、布局、地皮、空间判定 | [worldgen-spatial.md](references/worldgen-spatial.md) |
| TEX/XML、SCML、bank/build/symbol、编译资源 | [assets-animation.md](references/assets-animation.md) |
| 角色换皮/拆件、手持装备、书籍外观与接入检查 | [character-and-equipment-art.md](references/character-and-equipment-art.md) |
| GIF/WebP 帧序列、旋转法阵、锚点与动画编译 | [animation-recipes.md](references/animation-recipes.md) |
| DST Mod Tool 项目/脚本接口/预览 | [dst-mod-tool.md](references/dst-mod-tool.md) |
| 音效、FMOD 与粒子 | [audio-particles.md](references/audio-particles.md) |
| 重复查询、轮询任务、组件计数与缓存失效的实际优化 | [practical-optimization.md](references/practical-optimization.md) |
| 排错、全面审查、性能、自动化测试、同步和交付 | [testing-release.md](references/testing-release.md) |
| 资料来历、旧规则纠错与可信度 | [sources-and-corrections.md](references/sources-and-corrections.md) |

涉及回调重入、动作时钟、消费后的声音收尾、唯一物品事务、配料域或 UI 重建时，按 [工程案例索引](references/lulu-case-index.md) 选择相关专题。按案例说明的项目条件和证据范围使用。

## 实施要点

- **实现复杂度**：一次性注册先用直接登记；返回接口、跨环境复用按真实消费者选择。简化时追到最终执行点，删除无用转发、状态及旧路径；判断是否保留按[真实边界](references/core-lua-hooks.md#判断写在真实边界)核对。结构收益与性能收益按[优化验收](references/testing-release.md#架构简化与性能优化)分别验证。
- **端别与状态**：权威状态由服务器决定，客户端输入、预测和显示沿实际链路接入；分别核对 Component、Replica 与本地玩家上下文。
- **资源归属**：任务、监听、修改器、Widget 和子实体各有所有者与退出入口；恢复共享字段前确认仍由本功能持有。
- **资产接线**：分别核对文件、prefab、bank、build、symbol 与动画名，按实际资产类型检查依赖。
- **验证与部署**：按[测试与交付](references/testing-release.md)选择检查，分别报告静态、专服和客户端结果；同步前比较目标副本与已有修改。

## 辅助脚本

命令与参数见[测试与交付](references/testing-release.md)，环境定位见[环境与工具](references/environment-tools.md)。

- `scripts/dst_zip_tool.py`：只读 ZIP 的 info/list/grep/show 与单文件导出。
- `scripts/check_api.py`：Lua 语法和部分 Component/Replica 直接调用的声明检查；DECLARED 后仍需核对合同，NEEDS_REVIEW 项继续追源。
- `scripts/dst_modtest.py`：Windows 隔离单分片专服，独立副本、存档、运行 ID 与证据清单；所有断言结束后调用 `TEST.Done()`。

## 使用许可

项目自有材料按[非商业 LICENSE](LICENSE)使用，具体情形见[许可说明](docs/licensing.md)。任务明确涉及收费接单、付费 Mod/服务或售卖材料时，先确认已有权利人书面授权；用途未说明时不推定为商业用途。第三方与有效历史授权按各自条款处理。
