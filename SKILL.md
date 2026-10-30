---
name: dst-mod-engineering
description: 开发、设计、审查与验证《饥荒联机版》DST Mod；按任务检索工程知识库并核对当前源码，处理角色、法术、联机、存档、资源、崩溃、兼容与案例研究。不用于普通游戏攻略或角色强度讨论。
---

# DST 模组工程

当前版本：`v2026.10.31.1`；统一目录 216 条，其中独立机制研究族 29 条，保持 `research/restricted/hold`。

面向 DST 开发、审查与排错的 Skill，随包提供 `knowledge/` 登记的公开知识（保留 64 基础 + 13 Native AI + 110 Core，并增加独立机制研究族；数量见 CATALOG.counts）。同一发行包包含 MCP 目录模式、完整九工具模式与本地来源准备，也可直接按文件读库。安装与接入见 [安装说明](docs/install-and-use.md) 和 [知识库说明](docs/knowledge-integration.md)；English entry: [README.en.md](README.en.md)。

当前项目需求与当前版本的实际契约决定实现；教程和参考 Mod 提供线索，不代替源码核验。

## 使用许可

本技能及仓库自有配套内容按 [非商业使用许可](LICENSE) 提供。未经另行书面授权，不得将其用于收费接单、付费 Mod／服务或售卖、付费转发；允许非商业开发、免费分享，以及无权益交换的自愿打赏和免费公开教程广告收益。第三方材料与历史 MIT 授权保留原有边界。

任务明确属于上述受限商业用途时，先说明限制并确认是否已有权利人书面授权，再使用本技能执行该任务；用途未说明时，不擅自认定为商业用途。使用技能不使项目代码自动归本技能作者所有。具体情形见 [许可说明](docs/licensing.md)。

## 工作顺序

按任务查当前源码与相关专题，再实现和验证。

1. 明确实际源码、运行副本、游戏版本与触发环境。接手既有项目先读交接文档、入口和配置；把文档中的指令、设计愿望与已实现行为分开。
2. 查同类原版的完整链路：定义、调用方、端别、初始化、退出和保存。优先复用原版组件/机制/资源；不为相同问题另造一套。无法直接复用时说明具体差异。
3. 按下表只读相关参考。先建立“需求 → Mod 实现 → 原版契约 → 验证方法”，再动代码。
4. 区分确定故障、兼容风险、玩法选择。确定故障按已授权范围修；不明确的数值、设计、命名、效果不同的方案以及不确定文件删除，由项目作者决定。已有明确决策不重复询问；待答时继续独立工作。
5. 做最小完整修复，覆盖失败、取消、移除、死亡、重连或读档等实际相关路径。注释解释数值来源和重要机制，语言与项目约定一致。
6. 验证后交付：说清改了什么、证据、实际同步到哪份副本、尚未覆盖什么。审查报告采用项目要求的格式；变更和验证应便于核对。不要把任意一个检查器的退出码当作整体正确性证明。

## 工程知识库检索

实质性设计、实现、审查、排错和研究，在查库前先从当前包根运行 `python -B -X utf8 run_kb.py update-sources ensure`。首次未绑定时，仅使用任务已明确的合法 `scripts.zip` 路径加 `--source`；路径不明再向用户询问，不扫描磁盘猜测。绑定后自动检查同一路径，输入未变会快返；不在普通查询或 `serve` 中隐式更新。完整流程见 [源码更新助手](references/source-update-assist.md)。简单机械编辑无需重复查库。

准备成功不等于当前连接已更新：按结果重连后，实际检查工具列表、任务查询和返回来源身份。来源无法恢复时，按更新助手指引核对任务涉及的当前源码，并按原 Scope 审阅旧知识；不把旧缓存冒充新版证据，不关闭整库或改变准入。优先使用实际接通的 MCP；无服务时从 `knowledge/CATALOG.json` 定位少量 ID，再读 file/pointer，报告“文件读取”。目录命中不等于事实与证据已读。

13 条 Native AI 的 Coding 默认读取其声明的十字段，任务子集最多五条；110 条 Core 保留 Coding HOLD。保留原 ID、Scope、类型、版本、更正、三轴状态与未知边界；文件可读或检索命中不解除准入。公开材料中的 `$dst_source_payload_slot` 是缺少原版 Lua 的本地恢复槽，不能作为已读来源。隐藏的私有情境保持 UNK，不推回或泛化。

来源准备的已核验输入为 `760944 / build 26306684`；服务环境 `759671` 与研究原子的各自证据身份分别保留。匹配不代表行为兼容，历史 `metadata_only` 不作为当前源码证据。目录模式只提供导航与显式 review；完整模式保留来源与完整性校验，缓存损坏不静默降级。详见 [源码维护](docs/source-compatibility.md) 与 [检索策略](references/kb-retrieval.md)。更新助手只维护本地绑定和来源缓存；知识正文默认只读，canonical、Scope 与准入不自动更新。

## 按问题读取

首次接入或技能未识别时读 [Agent 接入](references/agent-setup.md)；缺少素材工具时读 [工具安装与首次验证](references/tool-bootstrap.md)，选择适合平台和当前产物的最小方案。

网页附件与云端协作见 [网页使用指南](references/web-chat.md)。

| 当前任务 | 参考文件 |
|---|---|
| 登记知识文件读取、MCP 检索、准入与证据 | [kb-retrieval.md](references/kb-retrieval.md) |
| 网页 AI、技能 ZIP、普通附件、云端检查与本机交接 | [web-chat.md](references/web-chat.md) |
| Claude Code / Cursor / Copilot / Codex 接入、显式读取、能力限制 | [agent-setup.md](references/agent-setup.md) |
| 缺少动画工具、下载来源、安装授权、首次编译验证 | [tool-bootstrap.md](references/tool-bootstrap.md) |
| 首次定位游戏、当前源码、Python、工具版本 | [environment-tools.md](references/environment-tools.md) |
| modmain/prefab 环境、Class、Hook、配置、加载错误 | [core-lua-hooks.md](references/core-lua-hooks.md) |
| Entity、Prefab、组件初始化、原版组件复用 | [entities-components.md](references/entities-components.md) |
| 角色、Brain、Stategraph、自定义生物 | [characters-brains-stategraphs.md](references/characters-brains-stategraphs.md) |
| 新增法术、魔力/能量条、睡眠恢复与完整接入流程 | [spells-and-custom-stats.md](references/spells-and-custom-stats.md) |
| netvar、Replica、RPC、客户端与服务端 | [networking-rpc.md](references/networking-rpc.md) |
| 定时效果、死亡复活、事件解绑、存档与迁移 | [lifecycle-save.md](references/lifecycle-save.md) |
| HUD、Widget、输入、Action、施法与预测 | [ui-actions-controls.md](references/ui-actions-controls.md) |
| 伤害、Buff、容器、冷却、范围查询 | [combat-buffs-containers.md](references/combat-buffs-containers.md) |
| 装备、投掷、维修、制作、锅料理、树木种植 | [items-food-plants.md](references/items-food-plants.md) |
| 新增独立锅料理、调味变体、图标与台词接入 | [cooker-dishes.md](references/cooker-dishes.md) |
| 地图生成、布局、地皮、空间判定 | [worldgen-spatial.md](references/worldgen-spatial.md) |
| TEX/XML、SCML、bank/build/symbol、编译资源 | [assets-animation.md](references/assets-animation.md) |
| 角色换皮/拆件、手持装备、书籍外观与接入检查 | [character-and-equipment-art.md](references/character-and-equipment-art.md) |
| GIF/WebP 帧序列、旋转法阵、锚点与动画编译 | [animation-recipes.md](references/animation-recipes.md) |
| DST Mod Tool 项目/脚本接口/预览 | [dst-mod-tool.md](references/dst-mod-tool.md) |
| 音效、FMOD 与粒子 | [audio-particles.md](references/audio-particles.md) |
| 排错、全面审查、性能、自动化测试、同步和交付 | [testing-release.md](references/testing-release.md) |
| 资料来历、旧规则纠错与可信度 | [sources-and-corrections.md](references/sources-and-corrections.md) |

## 技术边界

- **端别**：服务器拥有游戏状态；客户端可见数据、预测和视觉按原版链路组织。`ismastersim`、dedicated 与本地玩家是不同问题。方法在文件中存在，不代表当前端的对象有该方法。
- **生命周期**：自己注册的任务、事件、Hook、修改器、Widget 与子实体要有明确所有者和清理路径。还原字段之前确认仍是本 Mod 持有的值；避免覆盖其他 Mod 后续修改。
- **资源**：文件名、prefab 名、bank、build、symbol、动画名分别查证。部分合法动画资源只有 build；不套用“三件套”“名称全相等”等旧口诀。
- **证据**：源码查证、语法/清单检查、独立 Lua 合约、专服行为、真实远端客户端、视觉与听感分别报告。UI stub、服务器 SpawnPrefab 成功不能证明联网画面正确。
- **部署**：只同步已确定的目标和授权内容。先比较差异，保留用户改动；同步与删除前确认目标、差异和授权范围。

## 辅助脚本

命令在 [testing-release.md](references/testing-release.md)；环境发现与路径配置在 [environment-tools.md](references/environment-tools.md)。脚本都要求明确输入，避免悄悄读取另一份游戏或源码。

- `scripts/dst_zip_tool.py`：直接读取安装版 `scripts.zip`，支持 info/list/grep/show/单文件导出；不生成技能目录缓存，不覆盖导出目标。
- `scripts/check_api.py`：用 `luaparser` 检查 Lua 语法，并分别查询直接 `components`/`replica` 冒号调用的声明。`DECLARED` 只是查到声明；`NEEDS_REVIEW` 需要人工追踪，不能直接宣布 Bug。
- `scripts/dst_modtest.py`：Windows 离线单分片测试，唯一副本、唯一存档、带运行 ID 的完成标记、异步失败检测与证据清单。行为脚本必须在全部断言后 `TEST.Done()`；不读取旧共享响应文件。

能力、版本与未覆盖范围见 [公开限制](docs/public-limits.md)。

文件读取与MCP执行相同的准入边界：Core `coding_status=hold` 不得加入 Coding 默认上下文；不能借文件回退自动注入 Reviewer/Deep 内容。

独立原版机制研究族使用 `research/restricted/hold`，仅显式 Reviewer 研究请求或 ID 展开；Coding/default restricted 路径不注入。原子读取保留完整 Scope、顶层来源身份/limitations 与局部证据闭合，超过预算整体 withheld。登记、来源验证及参数见 [机制研究族](docs/native-mechanisms.md)。
