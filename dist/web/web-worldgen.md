# dst-mod-engineering / web-worldgen

生成器：`dst-mod-engineering/web-bundle-v1`；源码指纹：`57176ee32b06f7673d42b57ce35d93e9baf47751ffd34e093dcf6e900bef5098`。

这是从仓库原文生成的阅读包；正文只改写 Markdown 链接目标。段落 SHA-256 对应原始文件字节，不是改写后的正文。未包含的文件、未实际访问的链接及未展开的附件不能算作已读；上传阅读包不等于安装本地工具，也不证明游戏验证通过。公开链接指向 main，可能晚于本包快照。

本包包含：
- `SKILL.md`
- `references/web-chat.md`
- `references/environment-tools.md`
- `references/testing-release.md`
- `references/core-lua-hooks.md`
- `references/entities-components.md`
- `references/worldgen-spatial.md`
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

## 来源：`references/entities-components.md`

原始 SHA-256：`fc02c099b51c5be036980feb1b57938f200c4b64c4198520ead800c8eef9918a`

# 实体、Prefab 与组件

适用于新增物品/生物骨架、自定义组件、生命周期及存档排错。本文对照 2026-09-27 核验环境的原版脚本；网络协议和资源编译按入口中的对应专题展开，源码基线见 [environment-tools.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)。

## 区分文件、定义与实例

`Prefab(name, fn, assets, deps)` 是注册信息，`fn()` 创建的是 EntityScript 实例，通常变量名为 `inst`。一个文件可返回多个 Prefab；临时 UI 或本地实体也可通过 `CreateEntity` 创建，不必拥有可持久化 Prefab。

`PrefabFiles = { "my_mod_items" }` 对应 `scripts/prefabs/my_mod_items.lua`。该文件可以返回 `Prefab("my_mod_item_a", ...)`、`Prefab("my_mod_item_b", ...)`。文件名和注册名没有“三者必须相同”的约束；错误日志 `Error loading file prefabs/...` 首先检查文件路径、大小写、语法及加载链。

`assets` 是这个定义依赖的资源；`deps` 是它依赖的 Prefab 名称列表。明确声明自己的 `local prefabs = {...}`，没有依赖就省略或传 nil。游戏为了兼容错误旧模组而保留的全局 `prefabs = nil` 不是可复用依赖表。

模组公共/前端资产和 Prefab 私有资产可分别放顶层 `Assets` 与本地 `assets`，不必把所有资源重复塞进 modmain。检查被依赖的动态生成对象和资源实际会被加载，不能推论“原版 prefab 总能随时生成，所以无需检查依赖”。

## 网络实体的公共区与服务端区

以当前原版同类实体为骨架：常见网络物品先添加引擎对象、公共动画与动作所需标签、netvar、两端组件，然后 `SetPristine()`，客机返回后再加权威玩法组件。**不是所有 `AddComponent` 都属于服务端**；`floater`、`aoetargeting` 等有公共初始化需求。

以下只展示普通可拾取物的结构，使用原版长矛资源；它尚未添加武器、装备、配方与字符串功能：

```lua
local assets = {
    Asset("ANIM", "anim/spear.zip"),
    Asset("ANIM", "anim/swap_spear.zip"),
}

local function fn()
    local inst = CreateEntity()
    inst.entity:AddTransform()
    inst.entity:AddAnimState()
    inst.entity:AddNetwork()
    MakeInventoryPhysics(inst)
    inst.AnimState:SetBank("spear")
    inst.AnimState:SetBuild("swap_spear")
    inst.AnimState:PlayAnimation("idle")
    MakeInventoryFloatable(inst, "med", 0.05, {1.1, 0.5, 1.1}, true, -9)

    inst.entity:SetPristine()
    if not TheWorld.ismastersim then
        return inst
    end

    inst:AddComponent("inspectable")
    inst:AddComponent("inventoryitem")
    inst.components.inventoryitem.imagename = "spear"
    return inst
end

return Prefab("my_mod_example_item", fn, assets)
```

纯本地 FX、服务端控制实体、classified 子实体有各自的生命周期和网络策略，不强塞这一模板。`Transform`、`AnimState`、`Light`、`SoundEmitter` 是 `entity:Add...` 创建的引擎对象；它们与 `inst:AddComponent("name")` 加载的 Lua 组件不是同一层。没有原版 `components/light.lua`，不能用 `AddComponent("light")` 修复灯光。

客户端需要的函数/初始 netvar 必须能在客户端创建阶段获得；“写在 SetPristine 之前”不是同步所有 Lua 字段或所有渲染调用的魔法。动态视觉由网络状态驱动客户端回调；具体引擎方法是否同步要查同类原版使用并实测。

## 添加组件与 API 审核

`inst:AddComponent("my_mod_counter")` 会 `require("components/my_mod_counter")` 并实例化。返回 Class 即可，不必把组件加到 PrefabFiles。组件构造器执行时 `self.inst.components.my_mod_counter` 还未写入，且其他依赖组件不一定已添加；使用 `self` 或在明确的初始化阶段连接依赖。

修改前分别查 `components/x.lua` 与 `components/x_replica.lua`。当前例子：`hunger.current` 是服务端字段；`hunger_replica:GetCurrent()` 是另一接口；`stackable.maxsize` 是属性代理；`equippable` 提供 `SetOnEquip` / `SetOnUnequip`，不能凭对称猜出带 `Fn` 的版本。对动态别名要继续跟踪赋值语句。

新组件的最小持久化片段：

```lua
local Counter = Class(function(self, inst)
    self.inst = inst
    self.value = 0
end)

function Counter:OnSave()
    return { value = self.value }
end

function Counter:OnLoad(data)
    if data ~= nil and type(data.value) == "number" then
        self.value = math.max(0, data.value)
    end
end

return Counter
```

实际项目补充范围、旧存档版本与副作用恢复规则；这里的非负约束仅是示例，不是所有资源数值的默认设计。

## 事件、定时任务与移除

先找事件生产端的 `PushEvent`。回调收到的是**事件源实体与原样 data**，data 可以是 nil、标量、实体或表。

| 生产代码 | 回调第二参 |
|---|---|
| `inventoryitem` 的 `PushEvent("onputininventory", owner)` | owner 实体 |
| `equippable` 的 `PushEvent("equipped", { owner = owner })` | 表，访问 `data.owner` |
| `equippable` 的 `PushEvent("unequipped", { owner = owner })` | 仍含 owner；不要误称所有卸下回调都取不到 owner |
| `TheWorld:PushEvent("playeractivated", player)` | player 实体 |

`listener:ListenForEvent(event, fn, source)` 的 source 默认 listener。移除须用相同 `event, fn, source`；临时效果结束时不要 `RemoveAllEventCallbacks()` 清掉其他系统的监听。`WatchWorldState` 也要保留原回调引用并配对清理。

`DoTaskInTime` 和 `DoPeriodicTask` 返回可取消的任务。刷新效果先取消旧任务；所有结束路径都清自己的句柄、外部事件、速度/伤害 modifier、FX 引用。移除 Lua 组件时用 `OnRemoveFromEntity`，实体移除通知有 `OnRemoveEntity`；若二者都需要清理，写一个可重复调用的清理函数再挂到两条路径。跨实体任务不能只依赖施法者移除会自动处理。

实体标签、SG 状态标签、烹饪食材 tags 是不同机制。`CLASSIFIED` 不是“完全不联网”标签：原版 `player_classified` 本身有 Network，配合目标客户端、父实体和专用数据同步。`INLIMBO` 表示从正常场景交互中隐藏/移出，不应只解释成“物品已进背包”。取用现有 tag 前查所有关键消费者；自定义 tag 使用项目命名空间。

## 存档时序与派生数值

- 组件 `OnSave()` **返回** `data, refs`；实体 `inst.OnSave(inst, data)` **填写传入的聚合 data** 并可返回 refs。两种签名不能混用。
- `SetPersistData` 顺序是实体 `OnPreLoad` → 用 `pairs` 加载各组件 → 实体 `OnLoad`。组件之间没有可依赖的固定顺序；跨组件恢复应有明确协调阶段。
- 保存 GUID 引用需要 `refs` 并在 `LoadPostPass` / `OnLoadPostPass` 用 `newents` 恢复；普通 Lua 实体引用不能直接序列化。
- 教程等级示例每次用“当前最大血量 × 等级倍率”，重复升级和读档会累计膨胀。保存独立等级与基准，用可重复计算的派生公式；上限、死亡重置/保留由设计确定。
- `health:SetMaxHealth` 会同时改变当前血量。动态换上限要明确保持绝对值还是比例；死亡状态不可借恢复比例制造复活。原版 health 默认保存当前值，只有 `save_maxhealth` 才保存 max；形态跨档需恢复依据，不能只在 OnLoad 再变身。

## 原版检索入口与验收

- `mainfunctions.lua:LoadPrefabFile`、`mods.lua:RegisterPrefabs`、`prefabs/axe.lua`：文件加载与多个 Prefab 返回值。
- `entityscript.lua:LoadComponent`、`AddComponent`、`RemoveComponent`、`Remove`、`GetPersistData`、`SetPersistData`、`LoadPostPass`：组件生命周期与存档实际调用者。
- `entityscript.lua:ListenForEvent` / `PushEvent_Internal` / `RemoveEventCallback`：事件源和清理契约。
- `prefabs/spear.lua`、`standardcomponents.lua:MakeInventoryFloatable`、`prefabs/player_classified.lua`：公共区及网络实体例外。
- 验收首次生成、物品栏/地面切换、重复添加/移除效果、实体移除、保存重启、旧存档缺字段。组件恢复测试应覆盖不同初始化顺序；真正的网络表现需要客机验收。


---

## 来源：`references/worldgen-spatial.md`

原始 SHA-256：`2e14b0ce9ba8f7db85c286b10be68b76c60156657e9b7a962a25bb1039a2b8f8`

# 世界生成、地形与空间可视化

用于 room/task/taskset、静态布局、自然生成、地皮、放置范围和运行时地形改动。旧教程提供概念路径；真实参数、枚举和生命周期以当前安装源码为准。世界生成与运行中的世界是不同入口，不直接互抄对象和全局变量。

## 先确定改的是哪一层

| 需求 | 优先入口 | 不足以证明完成的检查 |
|---|---|---|
| 新世界的地貌、资源数量 | `modworldgenmain.lua` + Room/Task/TaskSet hook | 只启动一个旧存档 |
| 固定建筑群、岛屿/奇遇 | static layout + 对应 taskset/setpiece 注册 | 只有 Tiled Lua 能解析 |
| 自定义地皮 | 模组环境 `AddTile`，运行与生成两端一致注册 | 单独改某个数值 ID |
| 种植/建筑可放置范围 | deployable/replica/placer/helper | 只有服务器能成功放置 |
| 运行时填海/室内 | 当前相近原版机制及明确项目约束 | 仅看到一块地皮颜色改变 |

世界生成 hook 不给已有存档自动补内容。若需求包含旧档迁移，要另设版本标记和幂等迁移，并验证生成失败/回滚，不擅自重置世界。桌面测试总用隔离副本与新生成世界。

## Room → Task → TaskSet 与数量

从当前相近 `map/rooms`、`map/tasks`、`map/tasksets` 复制最小结构，使用模组 `AddRoom`、`AddTask` 和限定的 `Add*PreInit` 接入，不替换整张原版定义表。

- Room 描述地块、标签与内容，Task 组织房间/锁钥/连接，TaskSet 选择任务；它们不是运行时 prefab。
- `countprefabs` 是每个对应生成节点的目标数量，值可为数字或接收 `(area, prefab, scratchpad)` 的函数。多个相同 room 会各自处理，不能直接宣称全世界精确 N 个。
- 点数不足、过滤条件和放置失败可能阻止满足数量。先检查世界生成日志，再扫描最终世界/存档核实数量。
- `distributeprefabs` 是权重分布，`distributepercent` 控制密度；不能把目标绝对数量填进权重并期待严格计数。
- 选择所有房间的 postinit 会扩大作用范围；只修改已确认的 room/task，初始化缺失子表并保留无关项。
- `ExitPiece` 是拓扑生成标签，不能用它触发月岛启蒙。当前玩家区域处理检查 `lunacyarea`，经 `sanity:EnableLunacy` 启用；标签语义由消费者定义。

下面仅展示向指定房间登记已确认数量的方式；调用前决定命名、数量和哪些房间应出现：

```lua
local function AddRoomPrefabCount(room_name, prefab_name, count)
    AddRoomPreInit(room_name, function(room)
        room.contents = room.contents or {}
        room.contents.countprefabs = room.contents.countprefabs or {}
        room.contents.countprefabs[prefab_name] = count
    end)
end
```

原版 `areaaware` 每帧检查移动距离阈值，变化到不同节点时才发 `changearea`；不是每帧都广播区域事件。需要更精细边界时先找现有精度接口，避免无条件扫描全部实体/拓扑。

## 静态布局与 Tiled

1. 从当前 `map/static_layouts` 选择相近例子，保留版本与来源。确认地面层 `BG_TILES`、对象层 `FG_OBJECTS`、对象 prefab/type 与属性结构。
2. 通过 `map/static_layout.lua` 的 `Get` 转成 layout，使用唯一 layout 名，接入合适的 setpiece 容器。`map/layouts.lua` 和 `map/object_layout.lua` 是查布局选项与消费者的入口。
3. **Tiled 地面数据是 tileset 索引，不等于运行时 WORLD_TILES 数值。** 当前 `static_layout.lua` 的 `GROUND_TYPES` 执行映射；不要拿旧教程 GROUND ID 表直接填 Tiled layer。
4. 核对 tilewidth、尺寸、对象坐标转换、中心/旋转、可放置地块、预留空间、拓扑属性。不是所有新 Tiled 导出格式都会被旧形状的 loader 自动理解。
5. 检查布局依赖 prefab 和资产，然后多种 seed/世界尺寸实际生成，核实数量、碰撞、海岸通路、客户端小地图。

`ocean_prefill_setpieces` 当前可接受数字、`{ count = n }` 或函数形式的 count；旧教程的 `= 1` **不是类型错误**，源码明确兼容。表形式通常更清晰，不能把风格偏好报告为 bug。`Ocean_PlaceSetPieces` 会记录计划数与放置成功数；数量配置不保证每个布局成功落位。

不要把改变 `OceanRough.value` 为陆地类型视为通用“控制隐士岛离岸距离”API。当前布局有 `min_dist_from_land`，但其效果仍依赖 Ocean 生成阶段、地形空间与布局；按最小隔离实验验证，不用教程给出的全局地块替换捷径。

## 新地皮与运行时地形

当前 `constants.lua` 明确将 `GROUND` 标为 deprecated。新代码使用 `WORLD_TILES.<NAME>`；新地皮走模组环境 `AddTile(tile_name, tile_range, tile_data, ground_tile_def, minimap_tile_def, turf_def)`，由 TileManager 分配 ID。不要占用旧文档所谓 70–89 公共区间，或硬编码客户端/服务器的 ID。

原版 `TileRanges` 是 `tiledefs.lua` 的局部表，不是 `GLOBAL.TileRanges`。注册范围可用已有字符串 `"LAND"`/`"NOISE"`/`"OCEAN"`/`"IMPASSABLE"` 或通过 `RegisterTileRange` 注册的名字。`AddTile` 会把 tile 名转成大写，随后读取 `WORLD_TILES.MYTURF`，不是小写字段。

模组环境 `AddTile` 会在调用内管理 TileManager 保护标记。直接 `require("tilemanager").AddTile` 可能命中保护断言；不要修改全局保护开关或把代码硬塞进 `tiledefs.lua` 的初始化窗口。注册要在客户端、服务器及 worldgen 需要的入口保持一致；可用公共 modimport 文件避免漂移，并注意同一环境不要重复登记。

定义参数需从 `tilemanager.lua` 的 Validate 函数和当前 `tiledefs.lua` 的相近地皮读取：地面/边缘噪声、脚步声、小地图、turf、挖掘/铺设/临时地皮标记是不同职责。是否需要自有纹理、旧档 ID 映射、移除模组后表现均按实际需求验证。

`d_ground("DIRT")` 当前是调试捷径：在位置取 tile 坐标后调用 `Map:SetTile`。使用字符串能避开旧数值，但该函数不构成完整填海系统。运行时 wrapper 会发 `onterraform`；原版 terraformer 还处理原地皮、undertile 与掉落。不要把调用 `SetTile(x, y, tile)` 自动等同于清除 undertile，它有单独的 `ClearTileUnderneath` 接口。填海需逐一验证水陆通行、船/平台、海岸与小地图、实体位置、拓扑/区域、存档及远程客户端。不能把“保存重进看起来正常”推导为全部成立，也不默认伪造拓扑。

## 放置范围与局部提示

当前 `firesuppressor` 仍使用非 dedicated 端 `deployhelper`、本地不联网的 helper 实体，以及 placer 的 `LinkEntity`。教程的这个结构可保留。

- helper 可使用 `CLASSIFIED`/`NOCLICK`/`placer`、`persists=false`、父子实体关系，但这些 tag 不是通用网络权限机制。
- helper 启用时创建，关闭时删除；重复开关必须幂等，不能累积圈或更新任务。
- 显示缩放值受原图/动画坐标影响，教程 `1.78` 或原版 flingo 的 `1.55` 不是“米→缩放”的通用换算。以服务端实际半径核对圈边界，考虑父实体缩放。
- placer 的 `LinkEntity` 用于关联附属预览表现；tooltip/范围圈只负责表达，不改变服务器可部署条件。
- 种植自定义规则优先共用 `_custom_candeploy_fn` 与 CUSTOM 模式，见 `items-food-plants.md`。几何放置等 mod 必须用当前版本实际验证，不能仅声明兼容。

## 小房子与室内方案的边界

旧 `sample-smallhouse.md` 只是问题列表和外部 mod 链接，没有完整实现。不能当作已经验证的 DST 室内框架，也不能将“屏蔽全部世界状态”“移去远处”照搬成安全默认。

真正实施前集中确认：独立分片还是同世界离场区域、入口/出口与返回点、多人共享/独占、死亡/下线/迁移、季节天气/光照、地图可见性、寻路/相机、空间分配和存档生命周期。然后检查当前类似机制，制作最小可进入/退出/重载/第二玩家加入原型。视觉隔离和服务器实体隔离分别验证。外部方案未取得源码或未运行的部分写“待证”，不要靠旧链接背书。

## 当前原版检索入口

| 主题 | 已核验入口，行号以 2026-09-27 核验环境快照为准 |
|---|---|
| 新地皮与旧 ID | `constants.lua:681-802,805-834`；`modutil.lua:356-375` → `tilemanager.lua:118-209`；`tiledefs.lua` |
| 房间内容数量 | `map/graphnode.lua:340-403`；`map/rooms`、`map/tasks`、`map/tasksets/forest.lua` |
| 海洋布局 | `map/forest_map.lua:877-886` → `map/ocean_gen.lua:616-657`；`map/tasksets/forest.lua:61-66` |
| Tiled 解析 | `map/static_layout.lua:27-95` → `map/object_layout.lua`；`map/layouts.lua` |
| 区域与启蒙 | `components/areaaware.lua:45-90` → `prefabs/player_common.lua:581-584`；`map/storygen.lua:123-139` |
| 地形改动 | `debugcommands.lua:1010-1019`；`components/map.lua:3-8`；`components/terraformer.lua:16-32` |
| 范围预览 | `prefabs/firesuppressor.lua:239-273,308-312,460-490`；`components/deployhelper.lua`；`components/placer.lua` |

验证报告分开记录：Lua/数据结构检查、新地图生成结果、服务器运行与存读档、真实客户端视觉和多人行为。单个固定 seed 成功不能证明所有生成条件可用。

## 759671：虚拟房间集合与瞬移

该快照中的旧 Vault helper 已由 VirtualRoomSet（VRS）链替代；不要继续访问 `world.net.components.vault_floor_helper` 或依赖旧传送器世界事件。`components/map.lua` 的 Vault 公共包装改用 VRS 查询；其底层引擎实现与复制不能仅靠 Lua 读取证明。

`componentutil.lua:1344–1435` 对瞬移检查集合进入/离开、大厅及同集合寻路；`IsVisibleRespectingVRSFromPointToPoint` 共享边界判断但忽略同集合寻路，不是瞬移权限的等价别名。自定义 Blink/传送不能仅检查 tile passable。玩家读档安全点也按 VRS 寻找，不保证一律搬到大厅中心。见 [版本核验范围](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/public-limits.md)；Lua 源码检查不能代替专服与远端行为验证。


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
