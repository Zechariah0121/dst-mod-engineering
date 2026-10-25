# dst-mod-engineering / web-networking

生成器：`dst-mod-engineering/web-bundle-v1`；源码指纹：`22955607c9f2d3fe965b1ef02e01525e61c8fcebc765e386eeabe0f38ff7f3b6`。

这是从仓库原文生成的阅读包；正文只改写 Markdown 链接目标。段落 SHA-256 对应原始文件字节，不是改写后的正文。未包含的文件、未实际访问的链接及未展开的附件不能算作已读；上传阅读包不等于安装本地工具，也不证明游戏验证通过。公开链接指向 main，可能晚于本包快照。

本包包含：
- `SKILL.md`
- `references/web-chat.md`
- `references/environment-tools.md`
- `references/testing-release.md`
- `references/core-lua-hooks.md`
- `references/networking-rpc.md`
- `references/lifecycle-save.md`
- `references/ui-actions-controls.md`
- `references/spells-and-custom-stats.md`
- `LICENSE`


---

## 来源：`SKILL.md`

原始 SHA-256：`4db58ae73fc5bf3abf59db27aadb77d27e6d54aca7eb15316377f1b16af7bcd4`

---
name: dst-mod-engineering
description: 开发、设计、审查与验证《饥荒联机版》DST Mod；按任务检索工程知识库并核对当前源码，处理角色、法术、联机、存档、资源、崩溃、兼容与案例研究。不用于普通游戏攻略或角色强度讨论。
---

# DST 模组工程

面向 DST 开发、审查与排错的 Skill，随包提供 `knowledge/` 当前 187 条公开知识（64 基础 + 13 Native AI + 110 Core）。完整包另含 MCP 九工具服务与本地来源准备；独立 Skill 和网页阅读包可直接按文件读库。安装与接入见 [安装说明](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/install-and-use.md) 和 [知识库说明](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/knowledge-integration.md)；English entry: [README.en.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/README.en.md)。

当前项目需求与当前版本的实际契约决定实现；教程和参考 Mod 提供线索，不代替源码核验。

## 使用许可

本技能及仓库自有配套内容按 [非商业使用许可](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/LICENSE) 提供。未经另行书面授权，不得将其用于收费接单、付费 Mod／服务或售卖、付费转发；允许非商业开发、免费分享，以及无权益交换的自愿打赏和免费公开教程广告收益。第三方材料与历史 MIT 授权保留原有边界。

任务明确属于上述受限商业用途时，先说明限制并确认是否已有权利人书面授权，再使用本技能执行该任务；用途未说明时，不擅自认定为商业用途。使用技能不使项目代码自动归本技能作者所有。具体情形见 [许可说明](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/licensing.md)。

## 工作顺序

按任务查当前源码与相关专题，再实现和验证。

1. 明确实际源码、运行副本、游戏版本与触发环境。接手既有项目先读交接文档、入口和配置；把文档中的指令、设计愿望与已实现行为分开。
2. 查同类原版的完整链路：定义、调用方、端别、初始化、退出和保存。优先复用原版组件/机制/资源；不为相同问题另造一套。无法直接复用时说明具体差异。
3. 按下表只读相关参考。先建立“需求 → Mod 实现 → 原版契约 → 验证方法”，再动代码。
4. 区分确定故障、兼容风险、玩法选择。确定故障按已授权范围修；不明确的数值、设计、命名、效果不同的方案以及不确定文件删除，由项目作者决定。已有明确决策不重复询问；待答时继续独立工作。
5. 做最小完整修复，覆盖失败、取消、移除、死亡、重连或读档等实际相关路径。注释解释数值来源和重要机制，语言与项目约定一致。
6. 验证后交付：说清改了什么、证据、实际同步到哪份副本、尚未覆盖什么。审查报告采用项目要求的格式；变更和验证应便于核对。不要把任意一个检查器的退出码当作整体正确性证明。

## 工程知识库检索

实质性设计、实现、审查、排错和研究按任务查库；简单机械编辑无需重复检索。优先使用当前会话实际接通的现代 MCP；没有服务时，定向读取 `knowledge/data/index.json` 及相关的 `knowledge/data/native001/canonical-native001-ai-knowledge.json`、`knowledge/data/nativecore/native-core.json`，报告实际记录 ID 与“文件读取”，不默认注入全库。

13 条 Native AI 的 Coding 默认读取其声明的十字段，任务子集最多五条；110 条 Core 保留 Coding HOLD。保留原 ID、Scope、类型、版本、更正、三轴状态与未知边界；文件可读或检索命中不解除准入。公开材料中的 `$dst_source_payload_slot` 是缺少原版 Lua 的本地恢复槽，不能作为已读来源。隐藏的私有情境保持 UNK，不推回或泛化。

完整包 MCP 需先从合法当前与历史源码运行来源准备；单份当前 ZIP 仍缺历史范围时，继续文件阅读，不声称完整 MCP 可用。模式、九工具、epoch 连续、角色、预算与证据恢复见 [检索策略](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/kb-retrieval.md)。知识库默认只读；只有用户明确要求维护才进入更新流程。

## 按问题读取

首次接入或技能未识别时读 [Agent 接入](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/agent-setup.md)；缺少素材工具时读 [工具安装与首次验证](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md)，选择适合平台和当前产物的最小方案。

网页附件与云端协作见 [网页使用指南](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/web-chat.md)。

| 当前任务 | 参考文件 |
|---|---|
| 187 条知识文件读取、MCP 检索、准入与证据 | [kb-retrieval.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/kb-retrieval.md) |
| 网页 AI、技能 ZIP、普通附件、云端检查与本机交接 | [web-chat.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/web-chat.md) |
| Claude Code / Cursor / Copilot / Codex 接入、显式读取、能力限制 | [agent-setup.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/agent-setup.md) |
| 缺少动画工具、下载来源、安装授权、首次编译验证 | [tool-bootstrap.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) |
| 首次定位游戏、当前源码、Python、工具版本 | [environment-tools.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md) |
| modmain/prefab 环境、Class、Hook、配置、加载错误 | [core-lua-hooks.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/core-lua-hooks.md) |
| Entity、Prefab、组件初始化、原版组件复用 | [entities-components.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/entities-components.md) |
| 角色、Brain、Stategraph、自定义生物 | [characters-brains-stategraphs.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/characters-brains-stategraphs.md) |
| 新增法术、魔力/能量条、睡眠恢复与完整接入流程 | [spells-and-custom-stats.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/spells-and-custom-stats.md) |
| netvar、Replica、RPC、客户端与服务端 | [networking-rpc.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/networking-rpc.md) |
| 定时效果、死亡复活、事件解绑、存档与迁移 | [lifecycle-save.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/lifecycle-save.md) |
| HUD、Widget、输入、Action、施法与预测 | [ui-actions-controls.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/ui-actions-controls.md) |
| 伤害、Buff、容器、冷却、范围查询 | [combat-buffs-containers.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/combat-buffs-containers.md) |
| 装备、投掷、维修、制作、锅料理、树木种植 | [items-food-plants.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/items-food-plants.md) |
| 新增独立锅料理、调味变体、图标与台词接入 | [cooker-dishes.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/cooker-dishes.md) |
| 地图生成、布局、地皮、空间判定 | [worldgen-spatial.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/worldgen-spatial.md) |
| TEX/XML、SCML、bank/build/symbol、编译资源 | [assets-animation.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md) |
| 角色换皮/拆件、手持装备、书籍外观与接入检查 | [character-and-equipment-art.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/character-and-equipment-art.md) |
| GIF/WebP 帧序列、旋转法阵、锚点与动画编译 | [animation-recipes.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/animation-recipes.md) |
| DST Mod Tool 项目/脚本接口/预览 | [dst-mod-tool.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/dst-mod-tool.md) |
| 音效、FMOD 与粒子 | [audio-particles.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/audio-particles.md) |
| 排错、全面审查、性能、自动化测试、同步和交付 | [testing-release.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md) |
| 资料来历、旧规则纠错与可信度 | [sources-and-corrections.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/sources-and-corrections.md) |

## 技术边界

- **端别**：服务器拥有游戏状态；客户端可见数据、预测和视觉按原版链路组织。`ismastersim`、dedicated 与本地玩家是不同问题。方法在文件中存在，不代表当前端的对象有该方法。
- **生命周期**：自己注册的任务、事件、Hook、修改器、Widget 与子实体要有明确所有者和清理路径。还原字段之前确认仍是本 Mod 持有的值；避免覆盖其他 Mod 后续修改。
- **资源**：文件名、prefab 名、bank、build、symbol、动画名分别查证。部分合法动画资源只有 build；不套用“三件套”“名称全相等”等旧口诀。
- **证据**：源码查证、语法/清单检查、独立 Lua 合约、专服行为、真实远端客户端、视觉与听感分别报告。UI stub、服务器 SpawnPrefab 成功不能证明联网画面正确。
- **部署**：只同步已确定的目标和授权内容。先比较差异，保留用户改动；同步与删除前确认目标、差异和授权范围。

## 辅助脚本

命令在 [testing-release.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)；环境发现与路径配置在 [environment-tools.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)。脚本都要求明确输入，避免悄悄读取另一份游戏或源码。

- `scripts/dst_zip_tool.py`：直接读取安装版 `scripts.zip`，支持 info/list/grep/show/单文件导出；不生成技能目录缓存，不覆盖导出目标。
- `scripts/check_api.py`：用 `luaparser` 检查 Lua 语法，并分别查询直接 `components`/`replica` 冒号调用的声明。`DECLARED` 只是查到声明；`NEEDS_REVIEW` 需要人工追踪，不能直接宣布 Bug。
- `scripts/dst_modtest.py`：Windows 离线单分片测试，唯一副本、唯一存档、带运行 ID 的完成标记、异步失败检测与证据清单。行为脚本必须在全部断言后 `TEST.Done()`；不读取旧共享响应文件。

能力、版本与未覆盖范围见 [公开限制](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/public-limits.md)。

文件读取与MCP执行相同的准入边界：Core `coding_status=hold` 不得加入 Coding 默认上下文；不能借文件回退自动注入 Reviewer/Deep 内容。


---

## 来源：`references/web-chat.md`

原始 SHA-256：`dcad626b6963e8f67a7a7b1ce29361bb7b0dfacd4814515cb3b0daf8764a3664`

# 网页聊天中的 DST 开发

网页 AI 的能力取决于当前会话的文件、编辑与执行权限。资料上传成功不代表内容已完整读取；云端执行也不等于用户电脑上的 DST 已验证。

## 提供技能

| 方式 | 操作 |
|---|---|
| 平台支持原生技能导入 | 上传完整 `dst-mod-engineering/` 技能包并启用，确认 `SKILL.md` 和所需参考可读 |
| 普通附件或项目资料 | 提供 `SKILL.md`、当前任务相关专题、Mod 文件和必要原版片段 |
| 离线阅读包 | 解压 `web-reading.zip` 后选择对应专题；需要原始 Skill 文件时另取 `dst-mod-engineering.skill.zip` |

不支持 ZIP 解压时，上传相关文本文件。附上任务、期望行为、复现步骤、实际版本、运行端别和文件原相对路径；完整文件与截取范围要分清。无需上传整个游戏或私人存档。

Claude 的技能入口与账户要求见 [使用说明](https://support.claude.com/en/articles/12512180-use-skills-in-claude)，ZIP 顶层应为直接包含 `SKILL.md` 的 `dst-mod-engineering/`，见 [打包说明](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)。ChatGPT 可使用普通附件或 [Projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)；原生导入仅在账户提供相应入口时使用，见 [Skills 说明](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)。文件限制以 [上传说明](https://help.openai.com/en/articles/8555545-file-uploads-faq) 和当前界面为准。普通附件不是技能安装包，技能包也不是插件包。

## 按问题提供最少材料

| 问题 | 相关专题 | 首批项目材料 |
|---|---|---|
| 加载失败、崩溃 | [Lua 与 Hook](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/core-lua-hooks.md)、[实体与组件](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/entities-components.md) | 第一处错误与完整堆栈，相关入口、Prefab、组件与配置 |
| 主客机不一致、HUD | [网络与 RPC](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/networking-rpc.md)、[界面与动作](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/ui-actions-controls.md) | 两端代码、观察者身份、复现位置与日志 |
| Buff、死亡、读档 | [生命周期](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/lifecycle-save.md)、[战斗与 Buff](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/combat-buffs-containers.md) | 应用、移除、保存代码及复现顺序 |
| 贴图、动画、编译 | [图像与动画](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md)、[工具安装](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) | Lua 引用、文件清单、XML/SCML、必要样本及工具日志 |
| 制作、料理、植物 | [物品与料理](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/items-food-plants.md) | 配方、Prefab、组件、注册代码与配置 |
| 世界生成 | [世界生成](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/worldgen-spatial.md) | worldgen 入口、room/task/layout、种子与生成日志 |

核对原版时，先定位所需文件、函数与调用方，再从合法安装提供必要片段和版本依据。缺少初始化、端别或调用上下文时补齐；无法补齐时保留候选原因和成立条件。

同名附件可把路径编码为 `scripts__components__my_component.lua` 并说明映射。文本副本需注明原扩展名，执行前恢复正确路径。TEX、动画与压缩包仍需相应解析工具，改成 `.txt` 不会使二进制可读。

## 执行与本机交接

具备 Python 和完整输入的云端可做 [静态检查](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)；依赖、编辑、联网下载与执行权限分别确认。仅有片段时记录检查范围。随附专服测试器需要 Windows DST 环境，不能访问用户电脑盘符的云端沙盒无法替用户运行。

缺少工具时按 [工具安装](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) 提供作者来源、平台、最小依赖和样本验证方法。有本机执行连接且已获授权时继续；否则交付具体命令和输入，由本机执行者完成。

交付应包含：

- 修改文件相对于 Mod 根目录的路径，以及完整文件或补丁；注明所依据的版本，实际取得哈希时再记录哈希。
- 改动原因、已执行检查及证据、待本机验证项；静态、模拟、专服与真实客户端结果分别说明。
- 在目标副本应用前的差异核对和冲突处理；云端产物不会自动同步到运行副本或 Workshop。

本机回传实际加载副本、配置、复现步骤、完整堆栈、日志或截图，以及未测项；可用 [验证结果清单](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/templates/local-validation.md) 记录。日志中的令牌、密码和无关私人内容用占位符替换。证据等级见 [测试与交付](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)。


---

## 来源：`references/environment-tools.md`

原始 SHA-256：`db750b76856694ab177e82e91ef98f17a439ee9e3badbeab509a14d6d6ab5b12`

# 环境发现与来源定位

先发现当前项目实际使用的游戏、源码与工具，再配置绝对路径。本技能不绑定固定安装目录，也不随仓库分发游戏源码、编译器或第三方可执行程序。

缺少当前任务所需工具时，按 [工具安装](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) 选择最小方案；Agent 的加载路径与能力见 [接入说明](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/agent-setup.md)。

远端执行环境需核对文件、解释器和工具所属主机；本机资料交接见 [网页指南](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/web-chat.md)。

| 用途 | 发现与核对方法 |
|---|---|
| 游戏根目录 `$dst` | 从 Steam 的本地文件浏览入口或已知安装位置确认；检查该目录的游戏文件和版本，不假设固定盘符 |
| 当前打包源码 | `$dst` 下的 `data/databundles/scripts.zip`；记录 SHA-256 后查阅 |
| 已解压源码（可选） | 项目指定的只读副本；先与安装包的相关条目比较字节或哈希，避免陈旧副本 |
| Python `$python` | 用当前 shell 的命令发现功能或项目环境配置定位，执行 `--version`；静态工具另需 `luaparser` |
| 官方 Don't Starve Mod Tools | 从 Steam Tools 的已安装项目定位，检查 `scml.exe`、Python 脚本及其实际帮助；不同工具包版本的内容可能不同 |
| DST Mod Tool `$DmtExe` | 从已安装应用或用户提供的位置定位，检查文件版本及 `script --help`；缺少时检查已有替代管线，否则进入安装引导 |
| ktech / krane | 从已安装 ktools 位置定位，分别检查 `--help`；不要把文件夹名当成工具版本 |
| Mod 源码与运行副本 `$mod` | 从当前项目配置或作者说明确定；分别记录路径和哈希，不能只看同名文件夹 |

环境路径保存在项目本地配置或会话变量中；用实际文件确认源码与运行副本，不能只凭同名目录。

## 查阅当前源码

使用解压副本前，核对它与当前安装包的相关条目是否一致。游戏更新或哈希改变后，重新比较相关文件与行号。专题中的版本范围见 [能力与版本限制](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/public-limits.md)。

源码先用 `rg --files`/`rg -n` 定位。没找到按 prefab 命名的文件时，查合并返回多个 Prefab 的文件、工厂函数、调用链；如帽子集中在 `prefabs/hats.lua`。Lua 中没定义的引擎方法可能来自 C++，不能凭一次搜索判不存在。

无需解压时，在技能目录用 PowerShell 调用（先将 `$python`、`$dst` 赋为已发现并核对的绝对路径）：

```powershell
& $python scripts/dst_zip_tool.py --dst $dst info
& $python scripts/dst_zip_tool.py --dst $dst grep 'SetMaxHealth' --path components/health.lua
& $python scripts/dst_zip_tool.py --dst $dst show components/health.lua --start 1 --count 100
```

全局参数 `--dst`/`--zip` 放子命令前；`extract MEMBER --out EXACT_NEW_FILE` 只导出单文件且拒绝覆盖。

## 工具采用原则

读取已安装程序的 metadata/`--help`，在副本上运行所需操作，再检查输出产物。以程序自报版本为准，不用目录名推断版本。DMT 脚本接口见 [dst-mod-tool.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/dst-mod-tool.md)。

历史教程附带的可执行文件不作为默认工具；先做压缩包清单/文本源码审查。需要换工具时先比较现有工具能否完成同一产物，再按用户授权处理安装。

不同 shell 的 stdout、编码、引号与路径行为用实际调用确认。含复杂字符串的操作优先使用脚本文件，清理文件在同一 shell 中用明确路径执行。随附测试器的引擎存档路径要求 ASCII，以避开 Windows 中文路径兼容问题；报告目录可位于中文工作区。

## 随附测试器的特殊边界

- 默认引擎存档位于系统临时目录 `dst_mod_engineering/<运行ID>/DME/Cluster`；可传 `--storage-root ASCII_DIRECTORY`。命令同时传 `-persistent_storage_root`、`-conf_dir`、`-cluster`、`-shard`，不依赖当前账户的真实存档。
- LAN 测试端口按引擎日志允许的范围选择。工具先查空闲端口，但查完到启动仍可能竞争；端口冲突时换用空闲端口，不终止无关服务器。
- runner 只终止自己 `Popen` 创建的进程。每轮保留日志、manifest、唯一 staged Mod 与存档，便于排查；清理时先核对 manifest、绝对路径归属与进程状态，勿通配删除真实 `mods`/Klei 目录。
- 唯一测试目录会改变 `modname`。依赖 Workshop ID、硬编码文件夹名、跨 Mod 名称探测的场景必须单独验证配置映射与真实安装环境。

存档路径参数依据 Klei 开发者 [Dedicated Server Command Line Options Guide](https://kleiforums.com/forums/topic/64743-dedicated-server-command-line-options-guide/)。测试范围见 [测试与交付](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)。


---

## 来源：`references/testing-release.md`

原始 SHA-256：`62d42c048a3daa1275430ce7ab513dff77efc4b973fe83b9a7c8868fdfc31a79`

# 审查、排错、测试与交付

## 从症状到证据

先确认实际运行副本、配置、主机/远端/专服/洞穴位置、复现步骤和首次报错日志。有堆栈时追查调用方与目标对象构造，再判断原因。

全面审查沿入口 → Hook → Prefab → Component/Replica → Action/SG/Brain → RPC/UI → 保存路径展开。优先检查崩溃、存档损坏与非法客户端写入，再看初始同步、任务/事件清理、退出与旧档路径，最后检查资源、本地化和性能。记录文件位置、触发条件、影响、证据、修复与验证；玩法和样式选择单列。

性能问题先建立可重复场景，区分 tick、渲染和网络开销，再定位高频更新、查询范围、重复 dirty/RPC 或 Widget/FX 泄漏。优化幅度需有测量依据；事件、降频、查询筛选与缓存按实测采用，保持权威端别正确。

## 验证等级

| 证据 | 能证明 | 不能替代 |
|---|---|---|
| 当前原版源码 | 定义、调用链、端别与契约 | 引擎实际行为、用户配置 |
| Lua 语法/静态资源清单 | 可解析、声明/路径/结构等局部性质 | API 签名、客户端结果 |
| 独立 Lua 合约（含 stub） | 被模拟对象下的逻辑 | 真实引擎、复制、渲染 |
| 专服启动 | 此配置加载/世界初始化路径 | 没触发的 prefab 或功能 |
| 专服定向行为 | 实际服务器断言通过 | 真实客户端输入/UI/预测/音频 |
| 独立客户端 + 主机/专服 | 实际复制、动作、交互 | 未测 Mod 组合、未测资源 |
| 客户端视觉/听感 | 测过的外观、pivot、声音效果 | 所有分辨率、所有设备 |

存档测试需实际保存并重启同一隔离存档；手调 `OnSave/OnLoad` 只算合约检查。记录玩家生成方式，合成实体不能代替真人重连。死亡/SG 测试先确认演员已激活、未睡眠、出生无敌已处理且满足死亡条件，排除测试夹具错误。

## 静态脚本

在技能目录运行，`$mod` 为明确的 Mod 根目录：

```powershell
& $python scripts/check_api.py $mod --dst $dst --out $report
```

需要已有 `luaparser`。报告包含全部 Lua 语法错误和直接 `对象.components.xxx:方法()` / `对象.replica.xxx:方法()` 调用；自定义 `scripts/components/` 优先，服务端和 replica 分开。

- `DECLARED`：该侧源码中查到方法声明，仍需检查参数、初始化条件、权限和返回值。
- `NEEDS_REVIEW`：可能是拼错，也可能由继承、注入、别名或工厂定义；人工追完整链路再判。
- 退出 1：有语法错误。退出 2：输入/依赖错误、待查方法或没有直接调用。退出 0：所枚举的直接调用均匹配声明；不是 Mod 整体 PASS。
- 不能枚举的别名、点调用与动态调用不自动变成“已检查”；审查报告要覆盖这些路径。

## 实际专服测试

随附测试器仅支持 Windows，需指定输入与证据目录。纯客户端 Mod 不适用，测试器会拒绝；强制装入专服也不能替代客户端测试。

```powershell
& $python scripts/dst_modtest.py $mod --dst $dst --out $evidence --quiet
& $python scripts/dst_modtest.py $mod --dst $dst --out $evidence --script $test --timeout 240 --quiet
```

可在 Mod 参数后列依赖源码目录；各输入使用唯一快照。`--config options.json` 按零起始源码序号配置，例如 `{"0":{"enabled_feature":true}}`；不传时采用 Mod 默认值，测非默认分支需显式传入。测试器不负责真实多层服务器运维。

行为脚本可使用 GLOBAL 中的原版对象，并得到 `TEST`：

```lua
local item = SpawnPrefab("spear")
assert(item and item.components.weapon, "weapon did not spawn")
TEST.After(0.2, function()
    assert(item.components.weapon:GetDamage() > 0)
    item:Remove()
    TEST.Done("all assertions completed")
end)
```

- `TEST.After(seconds, callback)` 捕获该回调错误并报告失败。嵌套异步也用它；普通返回或打印 `SCRIPT_OK` 不代表完成。
- `TEST.Fail(reason)` 显式失败；`TEST.Done(detail)` 只在所有目标断言结束后调用一次。
- 仅匹配本轮 ID 的 READY/DONE，且 Lua 加载成功、无错误、通过 `--grace` 观察窗时才通过。失败优先，旧轮标记不参与。
- 观察窗只捕获窗内日志；晚触发行为需在目标阶段结束后再 Done。默认 `grace=3` 不代表机制寿命。
- manifest 记录快照与源码包哈希、命令、配置、PID、结果和日志位置；核对结果与关键断言后报告。工具终止进程造成的非零退出码本身不算失败。
- 失败时查看完整日志。无头 nosound/nullrenderer 不能证明客户端正确解码贴图、bank 或声音事件，仍需产物检查与客户端实测。

## 同步与发布

区分源码、运行副本、美术源与编译产物。同步授权目标前比较差异并备份覆盖内容，之后按相对路径与 SHA-256 核对变动和残留，确认当前进程加载的是目标副本。

PNG/SCML 改动需重编译对应产物，Lua 改动本身不要求重编译美术。按实际缓存层选择重进世界、重载 Mod 或重启客户端，并验证变更已加载。

发布前按改动检查 modinfo/配置、注册路径、生命周期与存档、资源引用、界面/联网和本地化。角色清单取自当前源码；modicon 与库存图标按实际消费者和资源契约检查。保留发布所需的 `mod.manifest` 与 Workshop 内容。

测试通过不自动授权发布或上传。交付列出修改、待作者决定项、未测项与证据路径。

## 版本维护

游戏更新后记录 scripts.zip 哈希、相关文件变动和完整调用链差异。哈希变动只是复核线索；区分符号/签名破坏、时序/端别改变、默认值变化与未使用内部变化。保留旧快照至相关验证完成；API 工具与技能也按同样方法回归。


---

## 来源：`references/core-lua-hooks.md`

原始 SHA-256：`0ec9f36c59eb5d690ac8e24aa7bac83bbd4e653584276b1e4b6e2feaea588092`

# Lua 环境、配置与 Hook

适用于加载失败、全局变量错误、组件或原版函数补丁。先确定**谁加载这段代码、在哪一端、哪个阶段运行**，再决定变量和 API 的写法。本文对照 2026-09-27 核验环境的原版脚本；引擎更新后按末尾入口复核，源码基线见 [environment-tools.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)。

## 加载环境决定可见变量

| 入口 | 实际机制 | 开发时的选择 |
|---|---|---|
| `modmain.lua` / `modworldgenmain.lua` | `mods.lua:CreateEnvironment` 创建模组环境；`modutil.InsertPostInitFunctions` 注入该阶段的 API | `AddPrefabPostInit` 等使用环境提供的函数；引擎对象用明确的 `GLOBAL` 引用 |
| `modimport("scripts/my_mod/setup.lua")` | 执行脚本前 `setfenv(chunk, env.env)` | 同一模组环境共享 `modname` 和注入函数；每次调用都会执行，不把它当缓存模块 |
| 通常的 `require("my_mod/config")` | 通过 Lua loader 加载模块，并按模块名缓存返回值 | 返回表或函数作为接口；文件夹命名空间避免与其他模组共享同一缓存键 |
| PrefabFiles 指定的文件 | `LoadPrefabFile` 加载并收集 chunk 的多个返回值 | 正常使用游戏全局；不能假设拥有 modmain 环境的 `GLOBAL`、`modname` 或自定义变量 |

“`scripts/` 下禁止某个变量”不是语言规则。文件路径不能决定环境；同一文件被 `modimport`、`require` 或自定义 loader 加载时，结论可能不同。`local GLOBAL = _G` 也是合法局部别名。跨模块通信优先返回接口、函数参数或闭包；不必为了传值把所有内容放进 `TUNING`、`STRINGS` 或 `_G`。

一个明确且无需环境代理的 modmain 片段：

```lua
local G = GLOBAL
local STRINGS = G.STRINGS
local TECH = G.TECH

AddPrefabPostInit("spear", function(inst)
    if not G.TheWorld.ismastersim then
        return
    end
    -- 此处才访问服务端组件。
end)
```

给 `env` 加 `__index` 回落到 `_G` 是可选风格，不是必须步骤，也不能创造不存在的 `SCIENCE` 常量。检查已有元表再决定是否改动，避免覆盖其他初始化逻辑。区分 `env.AddRecipe2`、`GLOBAL.TECH.SCIENCE_TWO` 与并不存在的裸 `SCIENCE`。

`modmain` 通常先于世界实例创建：顶层注册回调可以，顶层立即访问 `TheWorld.components` 不可以。需要世界对象时在世界初始化或运行时回调内取；不要顶层 `local world = G.TheWorld` 把当时的 nil 永久捕获。专服没有本地玩家 HUD，`ThePlayer` 也不能当服务器上的“当前施法者”。

## Lua 函数并非被统一禁用

默认模组环境只直接注入一部分 Lua 名称，所以裸 `pcall` 可能是 nil；原版全局中仍使用 `pcall`、`xpcall`、`loadstring`。不能从一次裸名报错推出整个游戏禁用了它们，更不能删除注释中的这些字样作为校验。

需要受保护调用时，检查真实环境中的函数引用及错误处理目的。保护调用不能修复错参、吞掉行为失败或代替输入校验；加载不可信字符串也不是处理配置的办法。`require` 不强制接返回值：模块可能返回接口，也可能有初始化副作用；先看该模块实现。`modrequire` 不是标准模组 API，只有项目自己定义时才可用。

## 配置与最小元信息

`modinfo.lua` 顶层是赋值语句，**不是表构造器**，赋值行之间不加逗号。短引号字符串换行需 `\n`，长括号字符串 `[[...]]` 可以包含真实换行。下面是可解析的内容模组元信息片段；名字与数值只是示例：

```lua
name = "Example Content"
description = "Example content mod"
author = "Example"
version = "0.1.0"
api_version = 10
dst_compatible = true
client_only_mod = false
all_clients_require_mod = true

configuration_options = {
    {
        name = "enabled",
        label = "启用功能",
        options = {
            { description = "开启", data = true },
            { description = "关闭", data = false },
        },
        default = true,
    },
}
```

纯本地界面功能可用客户端模组；只在服务端改变已有逻辑且不要求新资源、客户端动作或协议的功能可能不需要所有客户端安装。新增网络实体、角色或双方动作一般需要全客户端内容。按实际依赖选标志，不从“用了 AddPrefabPostInit”直接推出安装策略。

环境版 `GetModConfigData(optionname, get_local_config)` 的第二参是**是否强制本地配置**，不是默认值。`false` 配置不能被 `or default` 覆盖：

```lua
local enabled = GetModConfigData("enabled")
if enabled == nil then
    enabled = true
end
```

modimport 内也可使用环境版函数。原版还存在要求显式 `modname` 的全局三参数实现；新代码优先在模组环境读取，再通过自己模块的接口传入。不要在普通模块里无参猜测当前模组名，也不要把同一配置在服务端、客机和前端各读出不同来源后混用。

## Class 只保留会影响实现的规则

- `Class(ctor)` / `Class(Base, ctor)` 返回类表；`Type(...)` 才生成实例。派生构造函数需要时显式调用 `Base._ctor(self, ...)`。
- 当前实现浅拷贝父类成员：之后替换父类方法，不保证已经创建的子类会跟着更新。修改类表还可能影响全部该类实例。
- 第三参是属性 setter 表。被代理字段保存在实例的内部 `_` 表中；普通赋值会调用 setter，包括构造期间以及相同值赋值。setter 内不要给同一字段递归赋值。
- 不是所有字段、所有 table 修改都会经过 `__newindex`。例如 `self.options.x = 1` 不等于重赋 `self.options`；`rawset` 会绕开代理，不用它绕过组件同步。
- 不复制教程的简化 `Class` 替换游戏实现；它省略了继承身份、热重载等机制。

```lua
local function OnValueChanged(self, value, oldvalue)
    if self.onchanged ~= nil then
        self.onchanged(self.inst, value, oldvalue)
    end
end

local Counter = Class(function(self, inst)
    self.inst = inst
    self.value = 0
end, nil, { value = OnValueChanged })

return Counter
```

## Hook 选入口与保留原行为

先沿“触发事件 → 调用者 → 被调函数 → 结果”读一条完整链，再选择最窄的扩展点。优先组件提供的配置/回调、实体事件与官方 PostInit；只有扩展点不足时才替换方法或修改上值。

| 入口 | 回调拿到什么 | 常见边界 |
|---|---|---|
| `AddPrefabPostInit` / `AddPlayerPostInit` | 新创建的实体 | 两端都可能执行；不是“玩家已激活且 HUD 已就绪” |
| `AddComponentPostInit` | 构造完成的组件实例、实体 | 不等于改全局类；其它组件未必已挂载 |
| `AddClassPostConstruct` | 类构造完成后的 `self, ...` | 返回类表的模块适用；注意影响所有未来实例 |
| `AddBrainPostInit` | 已运行 `OnStart` 的 brain 实例 | 每次重启可再次执行；见角色与 AI 专题 |
| `AddStategraphPostInit` | StateGraph 定义表 | 它不是某个实体的 `inst.sg`；补丁影响共用此 SG 的实体 |

实例方法包装必须保留接收者、可变参数和返回值。是否传 `self` 取决于函数签名和调用方式，不取决于函数体里有没有写出 `self` 这个词：

```lua
AddComponentPostInit("trader", function(self)
    local old = self.AcceptGift
    self.AcceptGift = function(component, giver, item, count, ...)
        -- 在此添加已确认的局部条件；其它路径保持原返回值。
        return old(component, giver, item, count, ...)
    end
end)
```

需要后处理时要保留多返回值和 nil 空洞，不能随手 `{old(...)}` 后 `unpack`。仅为了打印或防错，不要无必要地包装高频全局函数。安装可重复的补丁应对实际被修改对象做幂等判断；卸载时仅在当前字段仍等于自己的包装函数时还原，避免抹掉后来模组的修改。

## 原版检索入口与验收

- `mods.lua:CreateEnvironment` / `InitializeModMain`，`modutil.lua:InsertPostInitFunctions`、`GetModConfigData`、`DoAddClassPostConstruct`：查环境、签名和装载阶段。
- `main.lua:loadfn`、`mainfunctions.lua:LoadPrefabFile`，`strict.lua`：查 loader 和未声明全局错误；不要只按目录判环境。
- `class.lua:Class`、`__index`、`__newindex`：查继承与属性代理。
- API 检查至少核对对象类型、主组件/replica、定义及调用者。Lua 中搜不到定义可能是引擎绑定、方法别名或动态注入，不能直接判“不存在”。
- 验收配置缺省、显式 false/0、只启用本模组、重复加载/初始化、原方法的返回值和其他分支。语法通过不能证明 Hook 被调用。


---

## 来源：`references/networking-rpc.md`

原始 SHA-256：`6feec131bc56dd9e55e6e01bb9afb98fd8a5a7a4fafe2ec506dc0a20874d9991`

# 联机权威、Replica 与 RPC

适用：自定义数值、技能请求、HUD 数据、后加入同步、跨世界消息。先读本篇，再按涉及的退出/读档行为读 [lifecycle-save.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/lifecycle-save.md)。本篇按 2026-09-27 核验环境的游戏 Lua 源码核验，基线见 [environment-tools.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)；网络传输实现部分在引擎中，源码追踪不能替代远端客户端测试。

## 先画状态归属表

为状态写出：谁决定、谁读取、变化频率、初始同步、是否存档、退出如何解除。

| 需求 | 通常入口 | 不能据此推断 |
|---|---|---|
| 服务端计算血量、消耗、掉落 | 服务端 Component | 客户端也有同名 Component |
| 两端共享瞄准或轮盘逻辑 | 原版明确放在公共区的组件 | 所有 AddComponent 都只能放服务端 |
| 小型持续状态 | 类型合适的 netvar；需要接口时封装 Replica | 一次 dirty 能覆盖后来加入、HUD 重建 |
| 客户端申请行为 | 原版动作链，必要时 Mod RPC | 客户端传来的状态已经可信 |
| 一次性音效/表现 | net_event 或 Client RPC | 这是可恢复的状态 |
| 地表/洞穴通信 | Shard RPC、现有 shard 组件 | 客户端 RPC 自动跨 shard |

`inst.components.X` 和 `inst.replica.X` 的方法分别核对对应文件；扫描器不能把两个方法集合并。部分 Component 本来就在两端，不能用“客户端没有 components”概括。服务端 Lua 事件默认只在当前进程分发；只有原版或 Mod 显式复制后，另一端才有相应变化。

## netvar 与 Replica 的初始化

普通网络 prefab：`AddNetwork()` → 两端一致的直接 netvar/必要标签/公共组件 → `SetPristine()` → 非主模拟返回 → 服务端逻辑。`SetPristine` 不是一条“此后任何 netvar/组件/本地视觉都禁止”的规则。

自定义 Replica 在实体生成前用 `AddReplicableComponent("组件名")` 注册，文件为 `scripts/components/组件名_replica.lua`。当前 `EntityScript:AddComponent` 先 `ReplicateComponent(name)`，再构造服务器 Component，因此 Replica 内的 netvar 可以随服务端添加已注册组件而建立。参考 `entityscript.lua:AddComponent`、`entityreplica.lua:ReplicateComponent/ReplicateEntity`；不要因此在任意延迟任务里随便添加裸 netvar。

- 声明顺序、名称、类型必须在各端一致；不要按主客机条件跳过某个裸 netvar。
- `value()` 读；服务端 `set(v)` 同步。值变化的 dirty 事件会在服务端和客户端触发。
- `set_local(v)` 不同步、不触发 dirty；会令随后服务端 `set` 强制产生 dirty。只在了解原版预测/重复事件范式时使用。
- 同值 `set` 一般不触发 dirty。绑定 HUD、`OnEntityReplicated`、玩家激活/目标更换时主动读当前值；不是每个徽章都必须加每帧轮询。
- `net_string` 接收字符串，不能把 Lua table 直接 `set` 给它。数值和枚举用匹配类型；小结构优先拆字段，确需序列化时限制大小、频率和解码后的 schema。
- `net_entity` 保存实体引用，不是把 GUID 当作跨端通用 ID。未复制或已移除目标需要 nil 分支。
- `net_event` 用于瞬时通知；持续夜视、形态或激活状态用可重建的 netvar。

位宽以当前 `netvars.lua` 为准：tinybyte 0–7、smallbyte 0–63、byte 0–255、ushortint 0–65535；shortint -32767–32767、int -2147483647–2147483647；数组有长度及元素范围限制（当前 bytearray/smallbytearray/ushortarray 最大 31）。别把字符串当作所有类型的万能替代。

## RPC 注册与签名

同一 RPC 的注册名及顺序在参与端一致。ID 由当前命名空间中的注册次序产生；不要把注册本身放进不一致的主客机分支。回调执行时再检查运行环境。

| 方向 | 注册 | 发送 | 回调的隐式参数 |
|---|---|---|---|
| 客户端→服务器 | `AddModRPCHandler(ns, name, fn)` | `SendModRPCToServer(GetModRPC(ns, name), ...)` | 通常第一个是请求玩家；特殊 userid RPC 另查原版 |
| 服务器→客户端 | `AddClientModRPCHandler(ns, name, fn)` | `SendModRPCToClient(GetClientModRPC(ns, name), userid, ...)` | 只有显式 payload；收件 userid 不变成 player 参数 |
| shard→shard | `AddShardModRPCHandler(ns, name, fn)` | `SendModRPCToShard(GetShardModRPC(ns, name), shardid, ...)` | 发送 shard 标识，再接 payload |

发送给单个玩家时使用其有效 `userid`。不要把这个常用用法概括成“所有 Client RPC 第二参只能是单个 userid”，群发形态应另查当前引擎契约。`MOD_RPC` 等旧表仍存在，但 `modutil.lua` 注释推荐 `GetModRPC/GetClientModRPC/GetShardModRPC`。

namespace 来自注册时传入的字符串；只有选用 `modname` 时才随实际 Mod 目录名改变。测试副本改目录时要检查调用方使用的 namespace，不能无条件写“namespace 就是文件夹名”。

短例子（只展示签名，不是完整玩法）：

```lua
local NS = "my_mod"
AddClientModRPCHandler(NS, "notice", function(message)
    if type(message) ~= "string" then return end
    -- 本地提示应另判 ThePlayer/HUD 是否已建立。
end)
-- 服务端已有合法 player 时：
-- SendModRPCToClient(GetClientModRPC(NS, "notice"), player.userid, "完成")
```

不要照教程承诺任意 table/function 可直接跨网络传输。Lua 包装层把参数交给 TheNet，无法由“函数接受 ...”证明序列化支持。使用原版有例证的简单值/网络实体；结构数据显式编码后仍要检验长度和解码 schema。完整支持类型若无当前文档或引擎实验，标记待验证。

## 服务端必须重新验请求

先查类型，再索引实体；数值先查有限性（`n == n` 排除 NaN、排除正负无穷）、范围和整数/枚举要求。随后按行为检查：请求玩家有效且允许操作、目标与物品有效、距离、持有权、平台坐标、PvP/权限、资源、冷却、重复请求。只在成功路径扣费/生成；失败返回明确结果。引擎总 RPC 限流不替代技能自身冷却或防重入。

客户端只传意图，不能让其自由指定要生成的 prefab、伤害、消耗、世界时间倍率或受控玩家。世界管理 RPC 必须校验服务端授予的管理权限。客户端按键门禁只是体验层，不能作为服务器授权依据。

刚发 RPC 不立即读 Replica 当返回值；用结果事件/状态变化更新 UI。刚生成的实体可能尚未复制，固定延时不构成可靠确认。旧请求抵达时目标已删除、切 shard、死亡、丢物，都必须可拒绝。

## 最小验证与检索

静态检查两端声明及调用签名；契约测试检查 handler 输入、拒绝路径和一次扣费；专服检查实际权威组件；最后用真实远端客户端覆盖正常请求、恶意/过期参数、延迟、重连、后来加入及按需跨 shard。直接在 Lua 中调用 handler 不证明 RPC 传输、实体映射或 UI。

当前源码检索入口（相对已核对的 scripts 根目录）：

- `netvars.lua:29-79`：声明一致、dirty 双端、set_local、状态与事件。
- `entityscript.lua:610-645`；`entityreplica.lua:34-83`：主组件/Replica 构造及复制回调。
- `networkclientrpc.lua:1725-1768,1834-1977`：队列、签名、注册 ID、namespace、发送封装。
- `modutil.lua:852-916`：Mod API 注入和 legacy 表说明。
- `prefabs/player_classified.lua:815-823,1208,1314`：dirty 加初始同步的原版例子。

## 759671：玩家 classified 上的吞食声音状态

吞食声音从旧玩家 `_wormdigestionsound` 搬到 `player.player_classified.wormdigestionsound`。新 `prefabs/player_classified.lua:1088–1104,1274,1650–1651` 定义 dirty 处理、监听与 net_bool；生产方为 `worm_boss_util.lua:290–296`，SGwilson `:14814–14816` 退出清理。使用时处理 classified 尚未附着/已经移除，事件监听对象及声音/DSP恢复按新链核对；客户端分支需要 parent 与 HUD。沿用当前原版角色工厂和SG时不必自行重建该 netvar。这一迁移不代表所有 Mod RPC 或 netvar 契约改变。


---

## 来源：`references/lifecycle-save.md`

原始 SHA-256：`94c7ddc7e2a294fc2650e42797fbee1a2051a3a3f170f11c218cd4402fd137fb`

# 生命周期、存档与恢复

适用：长期 Buff、形态、传送、父子实体、跨实体监听、存档迁移、组件移除。网络边界见 [networking-rpc.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/networking-rpc.md)。以当前 `entityscript.lua` 的调用顺序为准，不把项目经验写成所有组件通用的固定顺序。

## 每项机制先列进入和退出

至少考虑重复施加、刷新、主动取消、到期、死亡、幽灵、复活、目标/来源移除、丢弃/卸下、组件移除、睡眠/唤醒、保存重载；涉及玩家时加断线与切 shard。只测试正常到期不足以确认清理完整。

死亡后继续计时、暂停还是清除，以及重启后是否保留，都是玩法决策；从项目已有约定取值，不把原版某一种 Buff 的规则强加给所有 Buff。例如“死亡继续计时、复活保留剩余效果”可以是某个项目的要求，但不是本技能的默认规则；重启策略另外核对该项目设计与保存实现。

## 所有权与对称清理

| 申请/注册 | 对称解除 | 注意 |
|---|---|---|
| `listener:ListenForEvent(event, fn, source)` | 同 listener、event、fn、source 的 `RemoveEventCallback` | 匿名函数若要提前移除，应先保存引用 |
| `WatchWorldState` | `StopWatchingWorldState` | 初次绑定主动读状态 |
| task 字段 | `Cancel()` 并清空字段 | 刷新前取消；回调运行后清空；防止旧回调结束新一轮效果 |
| `SetModifier(source, value, key)` | 同 source/key 的 `RemoveModifier` | 不恢复成硬编码 1，不清其他来源 |
| 替换函数/标量 | 仅仍为自己写入值时恢复 | 保留原函数参数、返回值；共享布尔需要明确多来源策略 |
| 全局输入 handler | 保存返回 handle，`handle:Remove()` | Widget/玩家失效不会自动移除所有全局注册 |
| SG 临时状态 | `onexit` 撤销本状态拥有的变化 | 中断、死亡、超时也会退出，不盲目覆写新形态 |

实体 `Remove()` 已有 `RemoveAllEventCallbacks`、`CancelAllPendingTasks` 以及组件 `OnRemoveEntity` 通知。不要虚构“实体销毁不会清理任何监听/任务”。但 Buff 提前停止且实体还在、组件单独移除、把任务挂在玩家而不是 Buff、全局表保存回调等情况，仍需显式解除。`RemoveComponent` 调 `OnRemoveFromEntity`，不等于移除宿主实体。

单个周期任务每次刷新只应有一份。延迟创建 FX 的任务也要登记：取消/移除发生后，不得稍后重新生成旧 FX。清理函数尽量幂等；外部直接删除 Buff/目标时也能移除来源并清空宿主缓存引用，下一次施加可重新建立。

父子关系要区分 `EntityScript:AddChild` 跟踪与 `entity:SetParent` 引擎父级。检查实际使用路径，不能只见 parent 就宣称所有 Lua 自持引用和外部任务都会自动清除。

## 保存签名与加载顺序

| 层 | 保存 | 加载 | 引用修复 |
|---|---|---|---|
| Component | `OnSave()` 返回 `data, refs` | `OnLoad(data, newents)`，多数只需 data | `LoadPostPass(newents, data)` |
| Prefab | `inst.OnSave(inst, data)` 写入传入 data，可返回 refs | `inst.OnPreLoad(inst, data, newents)` / `inst.OnLoad(inst, data, newents)` | `inst.OnLoadPostPass(inst, newents, data)` |

`EntityScript:SetPersistData` 当前顺序：按需要补组件 → prefab `OnPreLoad` → 用 `pairs(data)` 调各 Component 的 `OnLoad` → prefab `OnLoad`。**组件之间没有可依赖的固定加载顺序。** 后续 `LoadPostPass` 再分别调组件及 prefab 的 postpass。

若形态组件改变血量上限：保存足够恢复的数据（比例/合法基准等），`OnPreLoad` 提取迁移输入，在全部相关组件加载后统一恢复。不要依赖形态一定先于 health 加载，也不要为了刷新 HUD 给零血尸体正向 `DoDelta`。是否保存形态、死亡记录如何迁移按玩法和原版死亡流程决定。

保存纯数据，不保存 EntityScript、Component、function、task、userdata 或循环表。跨实体引用保存记录 GUID 并返回 refs；postpass 用 `newents[saved_guid].entity` 解析，缺失目标须安全降级。`entitytracker`、`teleporter` 是可检索范例；跨端 GUID 与存档 GUID 映射不是同一协议。

Buff 的 `persists=false` 不等于一定不存档：当前 `debuffable:OnSave` 会把所持 Buff 的 `GetSaveRecord()` 嵌套保存；`keepondespawn` 管理 `RemoveOnDespawn` 的保留策略。二者都不能直接等同“死亡保留”或“离线继续计时”。

存档 schema 有缺字段默认值；大改结构时加版本，逐版幂等迁移。遇到未知未来版本不要静默覆盖成旧结构。任务保存剩余时间并重建；读档可能先产生构造期任务，必须防双份。

## Sleep、时间和回滚

游戏时间任务、静态时间任务、组件更新、实体睡眠、玩家离线是不同概念。先读组件的 `OnEntitySleep/OnEntityWake/LongUpdate`，再决定计时是否继续。`SetCanSleep(false)` 不能当作已睡实体必然已唤醒的证明；测试应读取状态并通过实际有效操作建立前提。

`LongUpdate(dt)` 是引擎按场景调用的时间补算，不等于自动按现实离线秒数推进所有 Buff。不要对同段时间同时正常更新和补算两遍。回滚会重放存档后事件，奖励、消费、生成和旧世界补刷需要幂等设计；承诺“恰好一次”必须说明提交边界和可回滚范围。

## 传送关闭必须等待抵达完成

`Teleporter:Target(other)` 只建立方向，双向虫洞需要两边建立。控制台跨次调用的临时变量与 Mod 的局部变量作用域不同；不能推广为“Mod 变量不可 local”。管理员控制台必须确认在服务器执行。

临时出口可能持有玩家抵达、镜头恢复等任务。到期时先关闭新入口，再按原版 `pocketwatch_portal.CloseExit`：`IsBusy()` 为 false 才删除出口，否则只登记一次 `doneteleporting` 监听继续等待。直接 Remove 出口会取消其 pending tasks。配对入口删除、超时关闭和外部删除均要纳入测试。

## 验证证据分层

- 纯 Lua/替身：迁移、函数签名、幂等和清理；不能证明引擎保存或渲染。
- 专服真实实体：组件加载、Buff/传送/死亡调用链；假玩家没有账号，不证明真实重连。
- 同一隔离世界两次独立进程：实际 SaveGame 回调、保存文件、再次启动后的值与引用，才是磁盘重启验证。
- 真实账号、远端客户端、跨 shard、预测与延迟：单独执行并报告；未做就列待验。

测试先断言前提：实体有效且已初始化、确实 awake、实际进入指定形态、已离开无敌出生状态、健康组件确实死亡，再断言结果。不能把夹具未触发流程的失败算成产品 bug，也不能用“没有异常”替代目标断言。

## 当前源码检索入口

- `entityscript.lua:648-662,1188-1261,1470-1529,1705-1771,1894-1988,2026-2036`：组件退出、事件/任务、保存和顺序。
- `components/debuff.lua:28-56`；`components/debuffable.lua:39-48,72-149`：刷新、detach、despawn、嵌套存档。
- `util/sourcemodifierlist.lua:64-121`：按 source/key 管理、实体来源移除的自动清理。
- `components/teleporter.lua:325-347,349-423`；`prefabs/pocketwatch_portal.lua:157-163`：在途计数、配对和保存、延后关闭。
- `components/timer.lua`、`components/entitytracker.lua`：剩余时间及存档引用范例。


---

## 来源：`references/ui-actions-controls.md`

原始 SHA-256：`83a2b5d424ce557339b5a48329f2792a8ed9e53f60d436f65d353f0e8def86c2`

# HUD、输入、动作与状态图

适用：徽章、面板、快捷键、拖拽、法术轮盘、角色动作和预测。专服无客户端 UI；组件的权威执行与客户端展示分别核验。保存/清理见 [lifecycle-save.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/lifecycle-save.md)，RPC 见 [networking-rpc.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/networking-rpc.md)。

## 复用 Widget 与 Screen

基础类由 `require("widgets/widget")` 等返回；继承后调用父类构造。Screen、Widget、TextEdit、ImageButton 都显式引入需要的模块，不依赖教程省略的全局。面板优先检索 `widgets/redux/templates.lua` 的 `RectangleWindow/ScrollingGrid/StandardButton`，核对当前参数与原版调用者。

`Widget` **有 `self.inst`**，构造时创建带 UITransform 的 EntityScript。`self.inst:DoPeriodicTask` 可以使用；Widget 默认把这些任务切到静态时间，暂停时是否更新由 `UpdateWhilePaused` 控制，游戏逻辑计时则用其 `DoSimTaskInTime/DoSimPeriodicTask` 或适当的玩法实体。

教程为了更新时钟单独 `CreateEntity()` 且不保存/移除，不适合可重建 HUD。任务挂所属 Widget 的 inst，并在功能提前停用时取消；Widget `Kill` 会停止更新、移除子控件和自己的实体。挂在 player 上的任务不能靠 `img.parent == nil` 判断已 Kill：当前 Kill 不保证将 parent 字段置 nil。

面板打开保持单例，重复打开先聚焦或复用；关闭走自己的 Close/PopScreen 路径，清空 HUD 引用、输入 handle、拖拽及监听。不要通过覆盖整个 `CreateOverlays/OnControl` 抹掉原版；窄包装并保留参数、原函数返回值和事件是否已消费的含义。

颜色常用 0–1 分量；不要照抄 `{255,0,0,1}` 当成标准 UI 色值。资源 XML/tex 路径先结构校验，再实机看字形、缩放和布局。

## 徽章初次同步、死亡与复活

绑定数据源时主动刷新一次，再监听 dirty。owner、Replica、classified 或网络引用可能分阶段就绪，按其实际初始化事件补绑定；不默认用每帧轮询隐藏初始化错误。`Badge:SetPercent(percent, max)` 传入实际最大值，核对数字显示与百分比。

幽灵 HUD 走原版链：`player_classified.isghostmode` → `OnGhostModeDirty` → 玩家 `SetGhostMode` → Controls/StatusDisplays。自定义三维条可以窄包装 `StatusDisplays:SetGhostMode`，在调用旧方法后按 `self.isghostmode` 切换，再补初次刷新。不能只在远端监听服务端 `ms_becameghost/respawnfromghost` 就期待自动收到事件。

初始快照还有一个时序细节：StatusDisplays 构造时先 `SetGhostMode(false)`，而 PostConstruct hook 在构造后才安装。首次刷新不能盲信这个临时 false；从本地 owner 已就绪的 `player_classified.isghostmode:value()` 读当前复制值，再结合自己的业务状态显示。classified 尚未就绪时按原版实际就绪链补绑定，避免永久误显示。这里指远端客户端上的本地玩家 HUD；观察其他玩家时，不能假设他们的私有 classified 对观察者同样可读，需要另查可见数据来源。

`respawnfromghost` 是复活请求/流程入口，不是死亡事件。复活按钮涉及双方代码，不能称“只服务端安装就有客户端按钮”；还必须校验玩家状态、可用次数/消耗/权限，并处理 HUD 尚未建立和服务器拒绝。不需要为原版已经同步的 ghost 状态再另造一套广播 RPC。

区分请求与完成：当前 `player_common_extensions.lua:427-430` 的成功流程写入 ghost 状态并发 `ms_respawnedfromghost`。需要“复活完成后”结算时追这条服务端链；完成事件仍不自动跨网，客户端显示继续读复制状态。

## 快捷键和控制器

- 使用当前 `constants.lua` 的 `KEY_*`、`CONTROL_*`，避免维护一份裸数字表。
- 客户端注册前排除 dedicated；回调检查本地玩家、HUD、有效玩法 Screen、聊天/输入框/控制禁用和角色状态，按功能决定是否吞键。
- ESC/取消仅在自己面板或瞄准状态活跃时消费，其他情况交回原版；未按下与抬起两阶段不能混淆。
- 保存 `TheInput:AddKey*Handler/AddControlHandler` 返回值，按所属 HUD/功能生命周期移除；反复激活不叠加注册。
- 键盘外还有手柄焦点流、确认/返回、断开手柄和鼠标拖拽，涉及这些入口时须实测。
- 输入限制不替代服务端 RPC/动作校验。

## 坐标与拖拽

先记录 Screen 像素坐标、Widget 父级局部坐标、anchor、比例缩放、父级变换与 HUD scale。`GetScale()` 返回累计缩放的 **Vector3**；`GetLooseScale()` 返回自身三个数值。

当前 `Widget:FollowMouse` 直接把屏幕坐标喂给 `UpdatePosition`，只适用于坐标系匹配的挂载方式。嵌套且缩放的控件需在自己的控件里做坐标变换，不能全局替换所有 Widget 的 FollowMouse/anchor 方法。简单未另设 anchor 的子控件可从“屏幕点减父级原点，再除父级累计缩放”推导；有其他锚点、变换时另验，不宣称一个公式通用。

`widget.OnMouseButton = function(self, button, down, x, y)` 中第一参是 self，不是 StandardButton 额外传入的文本。只处理自己消费的拖拽按键，其余调用旧处理；在松键、失焦、关闭与 Kill 时结束拖拽。保持按下时的鼠标偏移，避免控件突然跳中心；按要求保存归一化/局部位置，换分辨率时夹回可视区。

`TheSim:GetScreenPos` 的输出能否直接 SetPosition 取决于挂载层坐标。旧 skill 断言“任何情况下都无需换算”和“原版减半屏一定错”均不成立。不同 anchor 的原版公式可能各自正确；实测窗口比例、HUD scale、镜头/实体移动和边缘位置。

## 动作完整调用链

组件动作收集 → BufferedAction → 角色 ActionHandler → SG 状态 → 客户端 `PerformPreviewBufferedAction`/服务器 `PerformBufferedAction` → Action.fn → 组件业务。逐段查源，不只改菜单或 Action.fn。

客户端用 tag、Replica、公共组件决定显示/预测；服务端在真正执行帧检查目标、距离、资源、冷却和持有关系并结算一次。进入预测状态前不能清空仍需发往服务器的 buffered action。主机同进程能执行不代表远端路径已走通。

`busy` 是供调用者查询的状态标签，不是不可被打断的绝对屏障。SG 事件、死亡、取消、强制切状态都可能中断；`onexit` 只能撤销本状态拥有的物理、控制、模型、音效和临时 tag，不能把刚恢复的人形又改回旧 Boss build。

## 轮盘与 CASTAOE

以当前 `prefabs/abigail_flower.lua`、`prefabs/pocketwatch.lua` 等最近似物品为起点：`spellbook` 与 `aoetargeting` 在公共区；花的 `aoespell` 在服务器区。客户端组件动作由引擎复制注册信息，不要求在客户端构造服务器业务组件。

`aoespell:SetSpellFn` 签名是 **`function(item, doer, pos)`**。当前 `CanCast` 对有 spellbook 的载体检查：inventoryitem 的 GrandOwner；或 isplayer 且自身就是 doer；其余无物品、非玩家的 spellbook 载体返回 unsupported。不能照旧 skill 声称任意隐形 FX 法典原生可用。

`spellbook:SelectSpell` 的 onselect 参数是书/载体本身，不是玩家；客户端从合法本地 owner 上下文取玩家，服务器按请求者/持有关系取，不在共享服务端代码里盲用 ThePlayer。

当前 `GetGroundUseAction` 对 reticule.inst 是否为玩家有特殊分支。先追传入 position、鼠标/手柄分支和 BufferedAction 创建点，再设计载体；“reticule 必须永远挂非玩家”不是完整规则。

施法距离跟踪 aoetargeting 的 range 与 picker 传给 BufferedAction 的实际 distance，不只改 `ACTIONS.CASTAOE.distance`。圈合法性、海面/平台、落点、业务范围应一致；`SetAlwaysValid(true)` 只是原版地图检查参数之一，不代表资源/权限或最终技能目标总合法。

## 窄 hook 与上值

优先公开回调、组件属性/方法或限定 prefab 的 postinit。包装时保留 self、全部参数、全部返回值及原副作用的先后顺序；同一实例/树重建要有正确幂等依据，不永久布尔挡住新对象。

upvalue 是函数捕获的词法局部变量，可能是数据而不只是函数。仅当公开扩展点不足且当前源码可证时使用 `debug.getupvalue/setupvalue`；查找循环遇到 name=nil 必须结束，找不到则禁用该补丁并报告。不得无限查找一个原版可能改名的上值，也不按固定索引盲改共享闭包。

## 当前源码检索入口与验证

- `widgets/widget.lua:1-44,56-62,325-342,530-558`：inst、时间、Kill、跟随鼠标和缩放。
- `widgets/statusdisplays.lua:SetGhostMode`；`prefabs/player_classified.lua:OnGhostModeDirty`；`prefabs/player_common.lua:SetGhostMode`：ghost HUD。
- `input.lua:AddKeyDownHandler/AddControlHandler`；`widgets/redux/templates.lua`：输入与模板。
- `entityscript.lua:PerformPreviewBufferedAction/PerformBufferedAction`；`components/playercontroller.lua:GetGroundUseAction/RemoteBufferedAction`；`stategraphs/SGwilson_client.lua`：预测链。
- `prefabs/abigail_flower.lua:311-358`；`components/aoespell.lua:11-70`；`components/spellbook.lua:80-105`；`componentactions.lua:1990-2017`：轮盘、权限和动作注册。

Lua 契约测试可验证调用顺序、清理和 preview 回调次数；不能证明实际传输或动画。发布前按改动覆盖主机/远端、预测开关、重连/幽灵进入、鼠标/手柄、窗口与 HUD scale、目标在动画中被删、服务器拒绝和重复打开关闭。


---

## 来源：`references/spells-and-custom-stats.md`

原始 SHA-256：`1779c377451d378dc073f29edda76ef40d96e6cc2bdc57e79839027a677113b8`

# 法术、资源数值与徽章

适用：新增轮盘法术、地面或地图选点、魔力/能量等自定义数值、徽章和睡眠恢复。按 2026-09-27 核验环境的安装版源码整理，版本基线见 [environment-tools.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)。本篇是任务流程；组件、网络、生命周期、战斗和 UI 的通用契约链接到已有专题，不另维护一套。

## 先写出本次玩法契约

| 要明确的内容 | 实现前需要的答案 |
|---|---|
| 入口与施法者 | 自身、地面、地图；物品还是玩家载体；鼠标/手柄；骑乘能否施法 |
| 目标与范围 | 施法距离、效果半径、地形/平台、阵营/PvP、是否允许空放、未探索地图是否可选 |
| 资源与结算 | 值域与精度、消耗公式、目标排序、整次拒绝或部分生效、失败与中断是否消费 |
| 长期状态 | 刷新/叠层、死亡、幽灵、断线、切世界、重启的保留规则 |
| 反馈与验证 | 提示/动画/徽章、明确的成功结果、服务器拒绝路径与客户端验收场景 |

已有项目决策直接沿用；缺少的数值和玩法由作者决定。以当前原版相近机制确定技术路径，再写“输入 → 校验 → 效果 → 消费/冷却 → 退出”流程。配置保持单一来源，但不强制所有项目把数值写在 `modmain.lua`。

## 自定义数值：从服务端到 HUD

1. **确定权威与可见范围。** 服务端组件拥有数值；netvar/Replica 提供客户端读取。角色公共 `common_postinit` 可声明直接 netvar；若只有拥有者需要数据，先评估 classified 的接收范围和生命周期，不能把普通角色字段当成私有数据。详细步骤见 [networking-rpc.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/networking-rpc.md)。
2. **先建复制字段，再构造权威组件。** 使用项目命名空间命名组件、字段和事件；类型/顺序/名称在两端一致，按 `netvars.lua` 选择范围和精度。声明的 dirty 名必须与监听完全对应，并不要求它由字段名机械拼接；当前类型不止旧教程列出的十种。
3. **建立统一修改入口。** 定义读取、增减、设置上限和百分比接口；所有输入检查类型、有限性与业务范围。上限变化时明确保持绝对值、比例或重置，统一规范化当前值；允许零上限时给百分比和 UI 定义禁用行为，不直接除零。编码的取整/缩放和溢出处理应与玩法精度一致。
4. **初始化与同步。** `Class` 第三参属性 setter 是可选的原版范式；集中方法中显式同步也可行。setter 在构造赋值时已经运行，先设置 `self.inst` 和依赖；同值赋值也调用 setter，内部不要递归给自己赋值。`AddComponent` 在构造返回后才写入 `inst.components[name]`，构造期间使用 `self`，不要从该字段取回自己。其他组件可能尚未创建，跨组件依赖放在明确的装配阶段。参见 [core-lua-hooks.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/core-lua-hooks.md)、[entities-components.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/entities-components.md)。
5. **保存与恢复。** `OnSave()` 返回纯数据；`OnLoad(data)` 容忍缺字段并校验非法/旧版本值。先恢复合法基准/上限，再规范化当前值，即使存档未带 current 也不能留下越界值。配置派生的上限是否保存由恢复策略决定；跨组件加载无固定顺序，需要协调阶段。任务保存剩余时间后重建，细节见 [lifecycle-save.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/lifecycle-save.md)。
6. **接入本地徽章。** 以 `Badge`/`StatusDisplays` 为起点；绑定后主动读快照，同时监听 current 和 max 的变化，处理数据源稍后到达和 HUD 重建。徽章数字与百分比使用同一合法最大值；初次幽灵状态与后续切换走已复制的 ghost/HUD 链，不能只监听服务器的死亡/复活事件。绑定、解绑及布局见 [ui-actions-controls.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/ui-actions-controls.md)。

`Badge` 的 `iconbuild=nil` 有源码守卫，但资源是否含目标 symbol/frame 必须检查实际 build。旧结论“status_meter 一定没有 icon”没有足够资源证据，不作为规则。`dont_animate_circleframe` 只决定框是否跟百分比取帧；是否需要它取决于所用资源。独立 `Image` 可作为替代，明确设置所需注册点并实机检查，不能由 Lua 构造器猜引擎的默认锚点。换 build 仍需与复用的 bank/动画兼容，参见 [assets-animation.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md)。

## 睡眠恢复：复用任务，重新检查资格

`sleepingbaguser:DoSleep` 建立周期任务，`DoWakeUp` 取消并清空 `sleeptask`。需要与床具 tick 同步的恢复可窄包装 `SleepTick`，无须再建一个独立周期任务；床卷、帐篷及其他支持床具以组件实际关系判断，不靠单个 SG 标签猜“正在睡觉”。

当前 `SleepTick` 会扣饥饿、处理理智/生命/温度，并可能因饥饿调用床具 `DoWakeUp`。因此“先调旧函数，随后无条件回魔”不成立。包装前确认宿主、原床具和组件有效；调用原函数后，再确认同一睡眠会话仍有效、床具仍属于该玩家、`sleeptask` 未取消，以及设计要求的非饥饿/存活等条件，然后才恢复。若设计允许最后一次唤醒 tick 恢复，单独明确该规则。

保留旧函数的参数、返回值和副作用；避免重复安装包装，组件被移除后仍需清理本 Mod 自持的监听/引用。不要把 `self.bed ~= nil` 当成完整睡眠证明：当前 `SleepingBagUser:DoWakeUp` 取消任务，但不负责把该字段清空。额外的自然恢复、进食或战斗恢复各自追事件生产端，核验 data、调用时机、来源与清理，不能用一个睡眠 hook 代替所有恢复生命周期。

## 法术接线与选中状态

| 交互 | 当前原版入口 | 必须继续追踪的部分 |
|---|---|---|
| 地面选点 | `aoetargeting` → `CASTAOE` → `aoespell` | 本地瞄准、动作构造、两端 SG、服务器 CanCast 与结算 |
| 轮盘直接执行 | `spellbook:SetSpellFn` / 指定动作 | `CAST_SPELLBOOK` 或该动作的实际执行链，不等于在 UI 回调中直接改数值 |
| 地图选点 | `playercontroller:PullUpMap` 与地图 Action | owner、地图动作收集、预测/RPC、服务器落点复验 |

从当前 `waxwelljournal`、`abigail_flower` 读完整构造：轮盘和瞄准所需公共组件先准备，权威 `aoespell` 放服务端。不是“所有 SetPristine 之后的组件都只在服务器”，端别取决于执行分支和组件契约。

`spellbook:SelectSpell(id)` 把**载体**交给 `onselect`，不是把玩家交给它。公共回调只配置该法术的瞄准/动作；服务端在依赖已装配时绑定结算函数。不同法术共用组件时，切换到新项要清除旧项独有的重复施法、地形允许、range、reticule、spell action 和备用 spellfn 状态；原版 journal 在两种结算组件间切换时也清空另一种 spellfn。

`aoespell` 回调签名为 `(item, doer, pos)`；`spellbook` 直接回调为 `(item, user)`。`aoespell:CastSpell` 对无返回值的回调有默认成功处理，**返回 false 不会撤销已经发生的扣费或效果**。要显式表达预期结果。函数应在被捕获前定义或正确前置声明 `local`；不要保留旧模板中只有注释的 local 声明，却把 `function NewSpellFn` 写成全局。

原版 `CASTAOE` 的 `book` tag 用于选择书本动作动画，另有其他分支及兜底；它不是所有施法物品必需的 tag。`aoetargeting` 当前 enabled 初始为 true，禁用/冷却策略仍由机制负责。连续施法是玩法选项，不因模板存在 `SetShouldRepeatCastFn` 就默认开启。

指示圈的视觉、落点搜索、施法距离、实际效果范围分别核验。`reticuleaoe.lua` 的 scale 常量不能独立证明任意美术资源的世界半径；圈大小须对照资源和客户端边缘命中验证。targetfn 的搜索策略应符合设计范围，但不存在“搜索上限必须等于 range”的通用 API 契约。轮盘布局由条目数据计算，条目多时仍需验证文字、焦点、嵌套、分辨率和手柄，不能用“没有固定上限”承诺任意数量都可用。

## 服务器结算、伤害与范围效果

执行帧重新检查施法者、载体及持有权、技能选择、资源、冷却、地形与目标权限；不要只依赖打开轮盘时的检查。固定消费、总量消费、按有效目标部分消费是不同设计。部分消费需确定目标排序、单位成本合法性、失效目标处理及成功计数，不能未经检查计算 `floor(resource / cost)`。

先准备和验证可完成的操作，再按约定的提交点应用效果、消费与冷却，防重入/重复请求。同步事件也可能改变资源或目标；跨帧效果必须定义取消、失败及补偿。不要声称任意 Lua 效果能自动事务回滚，也不能把“回调最后返回 false”当退款机制。

- **电伤**：当前 `Combat:DoAttack` 在满足电 stimuli、且目标不满足 `IsEntityElectricImmune` 的条件下，按武器配置或 TUNING 和 `GetWetMultiplier()` 计算倍率，再交 `CalcDamage`。直接 `GetAttacked(..., "electric")` 不自动补这一倍率；选择与技能相符的原版攻击链，避免预乘后再走带倍率链导致重复增伤。普通/特殊伤害、防御、来源和阵营见 [combat-buffs-containers.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/combat-buffs-containers.md)。
- **触电反应**：有 `electrocute` 状态不等于事件一定进入它。当前处理还检查绝缘、死亡、状态标签、`sg.mem.noelectrocute` 和恢复间隔；受击链本身也可能触发电反应。不要对所有命中目标无条件再推一次事件。火花可查 `SpawnElectricHitSparks`/`nightstick`，是否额外播放按当前链路决定，不写固定 SG 数量或“全部 Boss 都支持”。
- **灌溉**：`AddSoilMoistureAtPoint` 先把世界点转为 tile index，然后给这一格累加。按世界坐标密集采样会重复加同一格；先以 tile 坐标去重，明确按格心/相交等哪种边界选格，再对每格调用一次。剂量由设计提供，不能把原版壶数值当所有法术默认值。`SetSoilMoisture` 还会将结果钳制到世界湿度与湿度上限之间；剂量不一定等于最终净增量，饱和可能掩盖重复调用，因此要同时验证每格调用次数。`wateryprotection:SpreadProtectionAtPoint` 的实体保护范围不等于会逐格给整片土壤加水。
- **临时属性**：火伤优先查 `health.externalfiredamagemultipliers` 的来源接口；速度用 locomotor 来源倍率。`vigorbuff` 只改变查到它的原版消费者，当前装备减速分支也是有限补偿，未必完全免疫。温度伤害率、腐烂倍率等共享标量若必须替换，明确多来源策略，并只在仍持有该值时恢复；接口存在不代表叠加安全。

天气、设备充能、燃烧与潮湿应先查对应组件及调用方，再写目标资格和副作用。复用带 aura/combat 的原版 FX 时先审伤害范围；复制所需过滤表，不能改共享常量。坐标 API 的三个返回值与 Vector3 不混用。现代农田使用 farming_manager；旧式 `slow_farmplot`/`fast_farmplot` 是另一系统，不把它们当作现代农田的通用测试替身。

## Buff 与 SG 的补充边界

可刷新效果优先走 [combat-buffs-containers.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/combat-buffs-containers.md) 的 debuff/timer 和来源修改器，再按 [lifecycle-save.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/lifecycle-save.md) 完成所有出口。旧“target[key] 有任务就只续期”的模板不能证明属性/FX 仍在；提前移除、外部删实体、读档或回调错误都可能使缓存失真。用私有键、幂等 Ensure/Apply/Remove、有效对象检查和任务归属判断，避免旧回调清掉新效果；死亡政策仍由项目决定。

`AddStategraphPostInit` 拿到的是定义表，states/events 按名称索引；只改 `wilson` 不会同时改 `wilson_client`。在受击 `onenter` 里直接跳 idle 可能跳过或打乱原状态副作用，先找窄事件/免疫入口并分别评估预测端。共享的 `sg.mem.noelectrocute` 也需所有权与恢复策略，不能把它写成永久通用免疫开关。

`EntityScript:PushEvent` 先同步调用普通监听，再按条件给 SG 缓冲事件，并交 brain；不是所有事件都在下一帧执行。测试普通监听可立即断言；测试 SG 要追当前调度与状态转移，使用有期限的条件/行为标记，固定延时不能证明效果。全局 `XXX_HOOKED=true` 只表示某段注册代码运行，不能代替实际受击链、未受保护对象及中断测试。

## 地图选点与临时传送门

优先沿原版地图动作链扩展，避免为单一法术覆盖整个 `MapScreen:OnControl`。`PullUpMap` 在合法的本地玩家 HUD 上下文调用；只判断“不是 dedicated”不能证明当前实体是本地玩家。`onselect` 的书本不能直接作为 `MapScreen` 的 owner。

按当前相近 Action 核对 `map_action`、`map_only`、`closes_map`、`customarrivecheck`、`instant` 和 `map_works_on_unexplored`。后者表示绕过可见性检查，是玩法选项；并非每个 `_MAP` 动作都设置 `map_action=true`，也并非每个地图动作都需要到达检查。载体的 `action_pulls_up_map` / `valid_map_actions` 按选用入口配置，不盲目堆叠所有字段。

确需自定义 Screen/RPC 时，完整处理按下/抬起、取消、重复打开、手柄、角色失效与服务器拒绝。当前 MapScreen 在 MAP/CANCEL **抬起**时关闭；旧骨架按 down 清标记不能当通用关闭流程。坐标返回 `x, 0, z`；客户端只提交意图，服务端按 [networking-rpc.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/networking-rpc.md) 重验有限坐标、地形/洞边/平台、允许距离/探索规则、玩家/物品、资源与请求次数。`IsPassableAtPoint` 不传 allow_water 也可能接受视觉地面延伸或船上平台，不等于“严格陆地”；按设计另验实际 tile 与平台。

相近的临时门可复用 `pocketwatch_portal_entrance:SpawnExit(worldid, x, y, z)`；nil 或当前 shard ID 是本地出口，其他 ID 进入原版迁移分支，跨 shard 需另验目标有效与迁移条件。复用机制不等于已经做完目标校验。确认生成和配对成功后才按约定提交消费，处理生成失败留下的半对门；关闭、外部移除和正在抵达的玩家按原版 CloseExit 流程收尾，见 [lifecycle-save.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/lifecycle-save.md)。

## 交付与原版检索

按 [testing-release.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md) 使用隔离副本并记录实际加载版本；无加载记录有多种原因，不直接断言为存档根错误。客户端正在运行并不等于隔离专服必然不能启动。部署只同步已授权目标，保留用户改动；删除临时调试注入，保留项目需要的正常诊断日志。

| 检查层 | 本任务至少关注 |
|---|---|
| 语法/API/结构 | 函数作用域、两端组件装配、字段范围、回调签名、资源依赖和保存 schema |
| 独立契约/专服（具备条件时） | 初值与上限变化、拒绝不误消费、重复施法/切换、目标失效、每格只浇一次、Buff 刷新/移除、睡眠最后 tick |
| 实际存档 | 保存退出后另进程加载，缺字段/旧档、死亡规则、任务与效果不重复 |
| 主机与真实远端客户端 | 后加入/重连、徽章 ghost 状态、鼠标/手柄、地图取消、预测与服务器拒绝、圈边缘和 HUD 资源 |

未执行的检查明确列待验；解析通过不证明真实联网、图标或动画。旧项目的参数、私有组件接口和已测结论不随技能迁移为新项目承诺。本篇刻意不给“改四处即可”的成品法术模板：先完成玩法契约与对应原版链路，再生成项目内可验证实现。

当前源码定位（相对 scripts 根目录；游戏更新后重新搜索函数）：

- `class.lua:28-44,181-193`；`entityscript.lua:610-645,1286-1323`：属性 setter、组件装配和事件时序。
- `prefabs/player_common.lua:2547-2549,2623-2627,2936-2938`；`components/health.lua:9-26,80-81,105-114`；`netvars.lua`：公共/权威初始化与数值同步。
- `components/sleepingbaguser.lua:40-68,79-108`；`components/sleepingbag.lua:74-93`：周期任务、饥饿唤醒和床具退出。
- `components/spellbook.lua:97-105,124-150`；`components/aoespell.lua`；`prefabs/waxwelljournal.lua:240-340,638-690`：选中与双结算组件切换。
- `actions.lua:4516-4524`；`stategraphs/SGwilson.lua:1251-1266`；`stategraphs/SGwilson_client.lua:580-595`：CASTAOE 动作与两端动画选择。
- `components/combat.lua:568-713,1170-1193`；`componentutil.lua:22-32,982-1009`；`stategraphs/commonstates.lua:325-345`：受击、电倍率和触电条件。
- `components/farming_manager.lua:96-110,461-474`；`components/wateryprotection.lua:43-51`：按格灌溉、湿度钳制与范围保护的区别。
- `widgets/badge.lua:6-104,127-146`；`widgets/statusdisplays.lua:SetGhostMode`；`prefabs/player_classified.lua:OnGhostModeDirty`：徽章资源与幽灵 HUD。
- `actions.lua:344-348,690,719-724`；`components/playercontroller.lua:424-460,5272-5319`；`screens/mapscreen.lua:1298-1380`；`prefabs/pocketwatch_portal.lua:157-219`：地图动作与传送门生命周期。

## 759671 核验补充

`DoAttack` 的电倍率仍在 `components/combat.lua:1195–1213` 计算，公共/内部受击方法不自动补该倍率；`GetWetMultiplier:748–769` 的 wet、moistureimmunity、inventoryitem 与 moisture 分支需独立看，不能把受击入口拆分当电倍率更改。SGwilson `attacked:1847–1944` 中 nointerrupt+canelectrocute 仍有触电分支，其余分支还受绝缘、noelectrocute、恢复窗口等限制。没有据此保证所有角色/Boss响应一致；见 [759671范围](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/public-limits.md)。


---

## 来源：`LICENSE`

原始 SHA-256：`61ab35cf1a8484c5e8951f4df13748ccdb25e4d72369c08eef6b25f511b4f891`

DST Mod Engineering 非商业使用许可
Non-Commercial Use License
2026-10-13

Copyright (c) 2026 zhuchengguang317-eng (GitHub: Zechariah0121)

1. 适用范围
本许可适用于从本次许可变更提交开始发布、且权利人有权许可的仓库自有
内容，包括 Skill 文档、示例、配套脚本、知识库原创分析和 MCP 检索服务。
本许可是自定义的非商业许可，不是 MIT，也不应标为 OSI 开源许可。
第三方材料、历史已授许可及法定权利按第 5、6 条处理。

2. 允许的使用
在遵守本许可的前提下，允许为非商业目的阅读、使用、复制、修改并免费
分发本材料，包括个人学习、研究、制作及免费分享自己的 DST Mod，以及
非商业合作开发、修复和技术交流。向 AI Agent 提供本材料也属于使用。
复制或分发本材料或其实质性部分时，应保留版权声明、本许可及原有来源
和第三方声明；修改过的分发版本应说明已作修改，不得冒充原作者发布。

3. 未经另行书面授权禁止的使用
不得将本材料用于收费接单、受偿定制开发、付费 Mod、付费功能或付费服务；
不得售卖、付费转发本材料，或将其改名、打包、嵌入收费产品、订阅、课程、
托管 Agent / MCP 服务等方式获取报酬。成品最终免费发布，不豁免收费接单。
不得以“赞助”“打赏”“会员”等名称规避付费解锁、访问限制或有偿交付。
其他主要为商业利益或金钱报酬而进行的使用，也须事先取得权利人的书面
授权，第 4 条明确允许的情形除外。

4. 打赏、赞助与公开教程例外
允许免费公开作品接受自愿打赏或赞助，前提是没有权益交换：不以付款换取
访问、提前获取、专属功能、定制开发、优先服务或其他回报。
允许免费公开的使用教程获得广告收益，前提是教程及所需使用资料不设
付费门槛，不借教程售卖本材料。支付通用模型、网络或托管基础设施费用，
本身不使一个非商业使用场景变为商业使用；收费代用本材料提供服务则不适用。

5. 第三方和生成成果的权利边界
Klei、参考 Mod 作者、外部工具及其他第三方保留各自权利；其材料仍按原
许可或适用法律处理。本许可不代表第三方授权、认可或背书，也不授予其
商标、游戏源码、素材等权利。
使用本材料辅助产生的 Mod 或代码，不因此自动归本项目所有，也不因此
整体继承本许可；其中实际复制的本材料片段和第三方材料仍须遵守各自
适用的许可。第 3 条约束对本材料的商业使用，不以本项目拥有全部输出
版权为前提。不把相同功能、通用设计思想或原版 API 用法视为使用本材料
的充分证据。本许可不限制依法无须许可的独立创作、事实、思想或使用。

6. 历史 MIT 授权
本次变更不追溯撤销先前已经有效授予的 MIT 权利。变更前的版本仍按当时
的许可处理；此前按 MIT 发布的相同材料，不因被重新收录而丧失原授权。
历史参考提交：ef682cb95f4b4e2171f3c2c634c88ddecefe75de。
随后仅修改 README 的提交 7c1f177a0632883c4c08d25956c07a939dc73d2e
仍保留 MIT LICENSE；本许可不声称该次 README 修改已撤销 MIT 授权。
在仍适用 MIT 的材料中，应保留原 MIT 版权及许可文本；可从对应历史提交
的 LICENSE 取得。新规则不能作为对历史合规使用追溯追责的依据。

7. 授权联系与责任限制
需要本许可之外的商业使用时，请事先联系权利人取得明确书面授权：
https://github.com/Zechariah0121/dst-mod-engineering/issues
仅提交申请、未收到答复或保留署名，均不等于已获商业授权。
本材料按“原样”提供，不保证准确、适用、不侵权或无缺陷；使用者应核对
自己的游戏版本、源码和实际测试结果。在适用法律允许的范围内，作者及
权利人不对因本材料使用产生的损失承担责任。

English summary (the Chinese terms above control this new license):
Project-owned materials in this release are offered for non-commercial use,
modification, and free redistribution with notices retained. Paid commissions,
paid mods/features/services, resale, and paid redistribution require separate
written permission. Unconditional voluntary donations/sponsorship and ad revenue
from freely accessible tutorials are allowed as specified above. Third-party
rights and valid prior MIT grants are preserved. Generated output does not
automatically become project property or inherit this license. This license
does not claim exclusive rights over facts, ideas, or independent work.
The materials are provided as is, without warranty, to the extent permitted
by applicable law. This is a custom non-commercial license, not MIT.
