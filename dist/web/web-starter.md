# dst-mod-engineering / web-starter

生成器：`dst-mod-engineering/web-bundle-v1`；源码指纹：`57176ee32b06f7673d42b57ce35d93e9baf47751ffd34e093dcf6e900bef5098`。

这是从仓库原文生成的阅读包；正文只改写 Markdown 链接目标。段落 SHA-256 对应原始文件字节，不是改写后的正文。未包含的文件、未实际访问的链接及未展开的附件不能算作已读；上传阅读包不等于安装本地工具，也不证明游戏验证通过。公开链接指向 main，可能晚于本包快照。

本包包含：
- `SKILL.md`
- `references/web-chat.md`
- `references/environment-tools.md`
- `references/testing-release.md`
- `references/agent-setup.md`
- `references/tool-bootstrap.md`
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

## 来源：`references/agent-setup.md`

原始 SHA-256：`9ac1f15b3de150075c95dd9f1059aa67110ca24804230fc92ed24c83b917a482`

# Agent 安装与能力

本技能采用 [Agent Skills 格式](https://agentskills.io/specification)。完整安装步骤与路径表见 [安装与使用](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/install-and-use.md)；下面的官方资料用于核对各产品当前入口。技能可被发现、脚本可执行与 DST 功能通过验收是不同结果。

## 官方入口

| Agent | 官方说明 | 加载后确认 |
|---|---|---|
| Codex | [Build skills](https://learn.chatgpt.com/docs/build-skills) | 用 `$dst-mod-engineering` 或技能选择器，核对实际文件路径 |
| Claude Code | [Skills](https://code.claude.com/docs/en/skills) | 用 `/dst-mod-engineering`；同名个人/项目技能需核对来源 |
| Cursor | [Agent Skills](https://cursor.com/docs/skills) | 在 Agent 聊天的 `/` 菜单选择，或到 Customize → Skills 查看 |
| GitHub Copilot | [安装技能](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)、[CLI 技能](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) | 使用所用界面的技能入口；CLI 命令不套用到其他界面 |

让 Agent 确认实际读到的 `SKILL.md` 和当前任务相关参考。没有 Skills 自动发现能力时，提供其绝对路径并显式读取即可。只有对话文本、没有文件访问时，使用 [网页附件方式](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/web-chat.md)。本 Skill 未逐一完成所有产品的端到端安装与执行测试。

## 本地与云端

安装路径属于运行 Agent 的主机。云端工作区不能直接读取用户电脑上的 DST、Mod 或工具：

- Claude 的本地个人技能不会自动成为 Cowork/云端会话技能；按 [官方云端说明](https://code.claude.com/docs/en/skills#use-skills-in-cowork-and-cloud-sessions) 使用账户技能或该环境支持的部署方式。
- Cursor 的个人技能同步需另行启用，且只同步其支持的位置；项目技能与远端工作区也要实际可读。见 [官方同步说明](https://cursor.com/docs/skills#use-personal-skills-with-cloud-agents)。

## 按任务确认能力

| 能力 | 可完成的工作 | 缺少时 |
|---|---|---|
| 读写、检索文件 | 读取 Skill、Mod 和原版源码，修改授权项目 | 仅分析已提供片段或交付补丁 |
| 终端与进程权限 | 运行 Python、资源工具与定向测试 | 提供命令，运行结果保持未验证 |
| 网络读取 | 核对官方文档、版本和工具来源 | 使用已有材料并注明版本未联网核对 |
| Windows DST 环境 | 运行随附隔离专服测试器 | Linux/云端不因此具备本机游戏测试能力 |
| 图像、音频、GUI 与真实客户端 | 检查动画、HUD、输入、声音与联机效果 | 由具备相应能力的执行者验收 |

脚本入口可用 `python scripts/<脚本名>.py --help` 检查。帮助成功只证明入口可运行，不证明依赖齐全或游戏功能通过。Python、`luaparser` 和素材工具按任务准备，见 [环境发现](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)、[工具安装](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) 与 [测试](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)。


---

## 来源：`references/tool-bootstrap.md`

原始 SHA-256：`4a51c21075856e61f7cf30dd563095c7f138158c9c2c66084194ac2dd8a365d1`

# 动画工具安装与首次验证

首次搭建或缺少工具时，先查 [已有环境](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)，选择能完成当前产物的最小方案。本页不捆绑程序，已有工具通过相同验证时可继续使用。

## 按任务选择最小工具

| 当前产物 | 优先选择 | 何时才增加其他工具 |
|---|---|---|
| 只改 Lua、复用已有图像 | 无新增动画工具 | 确实需要重建资源时再选 |
| PNG → TEX/XML、图集预览 | DMT 的当前可用打包功能，或 ktech，二选一 | 已选工具不能正确处理目标格式时再比较替代 |
| 动画编辑、预览、SCML → ZIP | DMT；先验证下载版本确有需要的编辑/打包能力 | 既有工程依赖官方编译流程，或 DMT 样本验证失败时，再用官方 `scml` |
| 已编译动画 → SCML | DMT 的当前解包功能，或 krane | 核对朝向、变换与图集保真，不能以“成功导出”结束 |
| 既有中间 XML/帧序列编译工程 | 工程匹配的官方 `buildanimation.py` 及依赖 | 任意 PNG ZIP 不能直接替代该工具要求的输入结构 |

“有 GUI”“有 CLI”“有 Lua 脚本接口”分别核对。DMT 能完成当前任务时，不再为同一产物强制安装 ktools 和官方旧编译器。音频工具另看 [audio-particles.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/audio-particles.md)。

## 发现、提议与授权

1. 读取项目配置，确认操作系统、CPU 架构、GUI/终端/联网能力、已有工具的绝对路径与版本。Windows 可用 `Get-Command ktech,krane -ErrorAction SilentlyContinue` 查 PATH；未命中不代表未安装，继续查用户指定目录和 Steam 库。macOS/Linux 可查 `uname -m`、`command -v ktech`。不根据当前 Agent 名称猜测宿主平台。
2. 对缺项一次说明：任务需要什么产物、候选工具和作者来源、实际包版本/平台/架构、目标目录、必要依赖、首次验证方法。只有具体功能需要时才建议安装；不要把整套工具清单变成前置条件。
3. 按用户已有授权安装；新增软件、系统依赖或改变安装范围尚未授权时，说明具体方案并确认。
4. 从下表作者入口选择匹配平台/架构的实际发行包，记录版本与下载文件 SHA-256。有作者校验值/签名时对照；自算哈希只标识文件，不证明来源。
5. 免安装 ZIP 解压到独立版本目录，例如 `C:\Tools\DST\工具名\版本\`；保留随包 DLL/配置，不覆盖已有版本，不改全局 PATH。安装器按已确认的范围执行；Steam 登录、验证码、账号授权和协议确认交由用户完成。安装完成后定位实际可执行文件，用绝对路径运行。

## 作者入口与安装路线

### DST Mod Tool（DMT）

[作者发布网站](https://msisunny.github.io/dst-mod-tool-publisher/)由[作者 Workshop 页面](https://steamcommunity.com/sharedfiles/filedetails/?id=3609167896)直接链接。访问网站，按当前操作系统选择下载；跳转目标应来自该页面实际链接。下载完整压缩包后先查看清单，解压到独立目录，再启动其中程序。macOS 按实际包中的 `.app` 布局放置；架构、系统最低版本和依赖若未标明，需要从包信息或作者说明核实，不能认为一个 Mac 包同时适合 Intel 和 Apple Silicon。

取得程序后检查文件/应用版本和当前帮助；只有实际支持 `script --help` 时才采用 [DMT 脚本工作流](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/dst-mod-tool.md)。不支持时采用该版本 GUI 或它实际提供的 CLI；不要照搬隐藏在网页源码中的旧命令。若系统阻止启动，记录提示并按平台正常的应用信任流程处理，不把关闭系统保护或递归移除隔离标记列为自动安装步骤。

### Klei 官方 Don't Starve Mod Tools

在 **Steam 客户端 → 库 → 类型筛选勾选“工具 / Tools” → 搜索 `Don't Starve Mod Tools` → 安装**。这是 Klei 官方工具，与独立作者的 DMT 不同。旧版 Steam 菜单可能直接显示“库 → 工具”；入口可参考官方论坛的[工具更新帖](https://kleiforums.com/forums/topic/126872-dont-starve-mod-tools-update-282021/)及[安装说明](https://kleiforums.com/forums/topic/50574-guide-modding-practices-before-beginning/)。库中没有该项目时，检查账号拥有的游戏和工具筛选。

安装后从该项目的“管理 / 属性 → 浏览本地文件”定位 `mod_tools`，确认本平台实际包含的 `scml`、脚本与依赖。不要因为 Steam 显示整个工具项目已安装，就认为每个子工具都能运行。保留官方目录布局：Windows 历史包带有自己的 Python/库；旧 `buildanimation.py` 可能需要 Python 2.7，不能直接交给本技能静态检查使用的 Python 3。非 Windows 子工具是否齐全、能否在当前系统运行，需要单独验证；[Klei 源码仓库](https://github.com/kleientertainment/ds_mod_tools)说明了编译与运行依赖，但旧仓库说明不保证今天的 Steam 包布局相同。

### ktools：ktech / krane

原作者为 [nsimplex/ktools](https://github.com/nsimplex/ktools)，后续分支为 [dstmodders/ktools](https://github.com/dstmodders/ktools)。从[原作者 Klei 下载页](https://kleiforums.com/files/file/583-ktools-cross-platform-modding-tools-for-dont-starve/)或[维护分支 Releases](https://github.com/dstmodders/ktools/releases)查找匹配系统的发行包，区分源码包与带 `ktech`/`krane` 可执行文件的包。

- 原作者下载页说明历史 Windows 包名以 `-win32` 结尾，需要 **VC++ 2013 x86** 运行库，且该二进制包不含 ZIP 输入支持；因此先解压动画 ZIP 再传目录。运行库确实缺失时，从[Microsoft 官方入口](https://www.microsoft.com/en-us/download/details.aspx?id=40784)按已批准的依赖范围处理，不从 DLL 下载站补文件。此要求针对该历史构建，不套用到所有 ktools 构建。
- GitHub 自动生成的 `Source code` 压缩包不是免安装程序。下载前查看实际附件清单；没有匹配二进制时，再评估源码构建或其他工具。
- 需要从源码构建时，按所选分支 README 确定编译器、CMake、ImageMagick 开发库，按需使用 libzip；两分支依赖版本可能不同。构建依赖纳入安装范围；输出保留在独立目录，不默认 `sudo make install`。已有 Docker 环境可评估维护分支作者提供的容器路线；不要为一次图片转换默认引入 Docker 或整套编译环境。

## 首次验证：得到产物才算工具可用

在自有临时目录放入一张小型 RGBA PNG，含透明边缘和非对称图案；动画任务再放入一份图片引用完整的极简 SCML 副本。记录输入哈希、工具版本、命令、输出及日志。不对现有工程直接运行会预处理原图的自动编译器。

下面是 PowerShell 示例：将路径替换为实际工具和自有输入，创建独立输出目录，只运行所选管线。

```powershell
$ProbeOut = Join-Path ([IO.Path]::GetTempPath()) ('dst-tool-probe-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $ProbeOut | Out-Null
```

ktech 路线：

```powershell
$Ktech = (Resolve-Path -LiteralPath 'C:\Tools\DST\ktools\selected-version\ktech.exe').Path
$ProbePng = (Resolve-Path -LiteralPath 'C:\DSTWork\probe\input.png').Path
$Before = (Get-FileHash -LiteralPath $ProbePng -Algorithm SHA256).Hash
$ProbeTex = Join-Path $ProbeOut 'probe.tex'
$ProbeXml = Join-Path $ProbeOut 'probe.xml'
& $Ktech --version
& $Ktech --help
# 仅在当前 help 确认 --atlas 参数时执行此行。
& $Ktech --atlas $ProbeXml $ProbePng $ProbeTex
if ($LASTEXITCODE -ne 0) { throw 'ktech conversion failed' }
if (!(Test-Path -LiteralPath $ProbeTex) -or !(Test-Path -LiteralPath $ProbeXml)) { throw 'Missing TEX/XML' }
& $Ktech -i $ProbeTex
if ($LASTEXITCODE -ne 0) { throw 'TEX inspection failed' }
& $Ktech $ProbeTex (Join-Path $ProbeOut 'roundtrip.png')
if ($LASTEXITCODE -ne 0) { throw 'TEX decode failed' }
if ((Get-FileHash -LiteralPath $ProbePng -Algorithm SHA256).Hash -ne $Before) { throw 'Input PNG changed' }
[xml]$Atlas = Get-Content -LiteralPath $ProbeXml -Raw
$Atlas.Atlas.Texture
$Atlas.Atlas.Elements.Element
```

随后实际打开 `roundtrip.png`，检查尺寸、方向、透明和边缘；核对 XML 的 Texture 路径与 Element 名对应产物。压缩和预乘 alpha 可能使回读像素不同，不能要求有损格式逐字节还原。DMT 路线也必须用实际支持的功能完成 PNG → TEX/XML → 重新读取/预览这一闭环，不能仅显示帮助就宣布安装成功。

官方 SCML 路线示例（单独选择，`$ProbeOut` 为上面创建的本轮目录）：

```powershell
$ModTools = (Resolve-Path -LiteralPath 'C:\SteamLibrary\steamapps\common\Don''t Starve Mod Tools\mod_tools').Path
$Scml = (Resolve-Path -LiteralPath (Join-Path $ModTools 'scml.exe')).Path
$InputScml = (Resolve-Path -LiteralPath 'C:\DSTWork\probe\source\probe.scml').Path
$TestMod = Join-Path $ProbeOut 'test-mod'
New-Item -ItemType Directory -Path $TestMod | Out-Null
Push-Location -LiteralPath $ModTools
try {
    & $Scml $InputScml $TestMod
    if ($LASTEXITCODE -ne 0) { throw 'SCML compile failed' }
} finally { Pop-Location }
Get-ChildItem -LiteralPath $TestMod -Recurse -File
```

`scml` 的第二参按该官方实现是**目标 Mod 目录**，在其 `anim/` 下生成 ZIP，不是输出 ZIP 文件名；见 [Klei 使用说明](https://github.com/kleientertainment/ds_mod_tools/blob/master/README.md#usage)及[参数处理源码](https://github.com/kleientertainment/ds_mod_tools/blob/master/src/app/scml/main.cpp#L2586-L2589)。还需核对日志、ZIP CRC、bank/build/symbol、动画和图集引用，用 DMT 或另一条可用读取路径重新打开并导出预览。DMT 编译路线同样要得到并重新读取真正的游戏 ZIP。只有反编译任务才另外用 krane 对小型样本执行 `--check-animation-fidelity`，检查 SCML、图片、帧/朝向与偏移；不把无报错等同完全保真。资源用途与验收规则见 [assets-animation.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md)。

## 无法安装或无法完整操作时

- **无匹配系统/架构包**：先查同一任务已有替代工具；再给出源码构建、受支持主机完成编译、暂交源工程三种适用选择。不要悄悄安装兼容层或把 Windows 命令称为跨平台已测。
- **断网或作者下载不可用**：可以继续用有来源记录的本地包核验；否则保留素材、工程、参数和具体待完成步骤，明确编译尚未完成，不转到随机网盘执行程序。
- **无 GUI/Agent 不能操作桌面**：优先验证当前程序实际提供的 CLI；若只能 GUI，准备可复现输入与操作说明供用户执行，同时继续独立的源码和资源结构检查。不虚构点击、预览或保存成功。
- **依赖、登录或权限阻塞**：给出准确缺项及恢复位置；已有授权范围内解决常规路径和参数问题。需要用户完成的账号/协议步骤不代答，完成后继续验收。

交付区分四层：**来源/版本已核对 → 程序可启动且接口存在 → 指定样本产物通过检查 → 真实游戏效果已验收**。本页提供安装与验证步骤，不代表所列发行包已在读者环境中通过验证。


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
