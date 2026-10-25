# dst-mod-engineering / web-assets

生成器：`dst-mod-engineering/web-bundle-v1`；源码指纹：`57176ee32b06f7673d42b57ce35d93e9baf47751ffd34e093dcf6e900bef5098`。

这是从仓库原文生成的阅读包；正文只改写 Markdown 链接目标。段落 SHA-256 对应原始文件字节，不是改写后的正文。未包含的文件、未实际访问的链接及未展开的附件不能算作已读；上传阅读包不等于安装本地工具，也不证明游戏验证通过。公开链接指向 main，可能晚于本包快照。

本包包含：
- `SKILL.md`
- `references/web-chat.md`
- `references/environment-tools.md`
- `references/testing-release.md`
- `references/tool-bootstrap.md`
- `references/assets-animation.md`
- `references/dst-mod-tool.md`
- `references/audio-particles.md`
- `references/animation-recipes.md`
- `references/character-and-equipment-art.md`
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

## 来源：`references/assets-animation.md`

原始 SHA-256：`a4f1511a05cb0b7334eb681f1cbf0758546a77e886a7a08d6b64cf494bb9b13f`

# 图像、图集与动画

适用于库存图标、装备换符号、角色皮肤、SCML 与动画帧序列。先找到同类原版 prefab 的资源声明和调用，再确定要修改的资源层。只改 Lua 行为不必重编美术；改源图后要重建受影响产物。

角色拆件与装备接入流程见 [角色与装备美术](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/character-and-equipment-art.md)；GIF/WebP、旋转法阵和锚点制作见 [帧序列制作](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/animation-recipes.md)。这两篇补充制作步骤，名称、资源职责和验收边界仍以本页为准。

## 先分清名称与资源职责

| 对象 | 用途 | 核验位置 |
|---|---|---|
| ZIP 文件名 | 资源加载路径 | `Asset("ANIM", "anim/xxx.zip")` |
| Bank | 动作集合，决定可播放动画 | `anim.bin` 内的 bank/root；`SetBank` |
| Build | 图像、符号与符号帧集合 | `build.bin` 内部名称；`SetBuild` |
| Animation | bank 内的动作名称 | `PlayAnimation` / `PushAnimation` |
| Symbol | build 中可替换的图像通道 | `OverrideSymbol` 第三参 |
| Layer | 动画元素的绘制层 | `Hide` / `Show`；不是所有 layer 都与 symbol 同名 |

这些名称可以不同。原版 `spear.lua` 使用 bank `spear`、build `swap_spear`；原版 `sword_lunarplant.lua` 用 `OverrideSymbol("swap_object", "sword_lunarplant", "swap_sword_lunarplant")`。不能凭 ZIP 文件名推导全部名称，也不能从 `build.bin` 推导 bank。

资源完整性按用途检查：

- 同时提供新动作和新图像：需要对应 `anim.bin`、`build.bin` 和 build 引用的全部图集。
- 只提供换皮/装备符号：允许 build-only，即 `build.bin` 加引用图集。原版 `swap_spear.zip` 就没有 `anim.bin`。
- 只补动作、复用已有 build：允许 animation-only；原版 `player_idles_wilson.zip` 是此类资源。
- 不能为满足“三件套”补造无用动画，也不能无条件删除 `anim.bin`；先查哪些调用依赖它。

## 换符号与手持装备

```lua
owner.AnimState:OverrideSymbol("swap_object", "my_weapon_build", "my_weapon_symbol")
owner.AnimState:Show("ARM_carry")
owner.AnimState:Hide("ARM_normal")
```

第一参是目标角色动画里的符号；第二参是已加载 build；第三参是该 build 里的实际 symbol。帽子、护甲使用各自目标符号和显隐规则，参照同类原版装备，不要把武器的 `swap_object` 当成所有场景的固定参数。

- 純 build 的 `OverrideSymbol` 不会让角色播放 swap 文件内某个 `idle` 或 `BUILD` 动作；角色仍播放自己的动作。某些 SCML 编译模板用 `BUILD` 收集图像是工具约定，不是引擎要求所有 swap 都必须有该动作。
- 常见 SCML 管线以 folder 组织 symbol，以 entity/animation 组织 bank/动作；最终以产物为准。不要强制 folder、timeline、entity、文件名全部相同。
- 无贴图依次查：资源是否加载 → build/symbol 拼写 → 角色动画是否引用目标 symbol → 帧号/朝向 → pivot 与缩放 → 隐藏层和其他覆盖。不能仅凭 build 名出现几次判断正确。
- `AddOverrideBuild` 本身是合法 API，用途不同；只需一个符号时通常用 `OverrideSymbol`。不要写“新版禁止 AddOverrideBuild”。
- 解除效果时只清理本 Mod 拥有的覆盖/显隐；可能与其他装备、皮肤或变身竞争时保留原版恢复路径。

## 图像尺寸、透明与位置

64×64 库存图、128×128 modicon 可作制作起点，具体尺寸参照原版同类资产和项目需求。源图尺寸、编译图集尺寸、symbol 几何范围、pivot、动画矩阵、实体缩放和镜头共同影响观感。

- 加载失败先检查资源与图集引用；画布留白和实际显示大小通过原版同类资产及客户端预览确定。
- 区分源 PNG 与打包后的图集。工具可把非 2 次幂源图打包/扩边到图集；不要强制每张源图都是 2 次幂，也不要擅自改变已有编译管线的尺寸政策。
- 透明背景保留 alpha。抠图时保护白色主体与高光，检查透明边缘和预乘 alpha，避免白边/黑边。
- pivot 表示锚点，不等于画布中心。先在原图标注握持点/落点，导出预览后再调整；不同工具的 Y 方向和归一化约定需核对。
- 缩放和旋转保持长宽比，尽量从原图一次生成结果，避免多轮重采样。图像坐标的正方向、SCML pivot 和世界坐标不同；用简单可视样本确认变换方向。
- 灯光 `inst.entity:AddLight()` 和渲染亮度/泛光是不同机制；只看图片发亮不能证明实体照亮周围。
- `MakeInventoryFloatable(inst, size, offset, scale, swap_bank, float_index, swap_data)` 创建水面漂浮表现；offset 是视觉垂直偏移、scale 控制浮水效果缩放，不是向上推力/阻力，也不负责陆地悬浮。

## 库存图集与 modicon

检查链条：PNG → TEX → XML Texture 路径 → XML Element 名 → 使用者传入的 image 名。XML Element 是图集区域名称，**不必等于 Texture 文件名**，但必须与调用者一致。

通常库存图片使用以下组合：

```xml
<Atlas>
    <Texture filename="my_item.tex" />
    <Elements>
        <Element name="my_item.tex" u1="0" u2="1" v1="0" v2="1" />
    </Elements>
</Atlas>
```

```lua
Assets = {
    Asset("ATLAS", "images/inventoryimages/my_item.xml"),
    Asset("IMAGE", "images/inventoryimages/my_item.tex"),
}
RegisterInventoryItemAtlas("images/inventoryimages/my_item.xml", "my_item.tex")
```

`inventoryitem.imagename` 常写不带后缀的 `my_item`，其 replica 再组成 `.tex` image 名；`RegisterInventoryItemAtlas` 的键应与实际查询名一致，通常带 `.tex`。不要统一要求 XML/注册键去掉 `.tex`。如复用现有图集或使用自定义 image，沿完整调用链核对。

上面的 UV 是整图示意。打包器可能生成半像素内缩坐标；保留其生成结果，避免挨着其他 region 时漏色。图集 Texture 的相对路径要从 XML 所在位置核对，避免重复 `images/` 路径。

`modinfo.lua` 的 `icon_atlas` 指向图集，`icon` 指向图集里的 Element 名。教程把文件拷到根目录是一个有效布局，不是唯一布局。添加图标不需要改变 `client_only_mod` / `all_clients_require_mod`。

## 工具选择与编译

先发现实际安装路径、程序自报版本和 help。缺少必需工具时进入 [工具安装与首次验证](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md)，按当前任务和已有授权处理下载安装。

| 任务 | 合适工具 | 边界 |
|---|---|---|
| 动画层级、符号、批量编辑与 PNG/GIF 预览 | DST Mod Tool | 先读 [DMT 工作流](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/dst-mod-tool.md)，先取当前 `script --help` |
| SCML 工程 → 运行时 ZIP | 官方 `scml.exe` | 独立临时输出，检查日志、产物和客户端效果 |
| TEX ↔ PNG、TEX 信息、简单 atlas | 已安装 ktech | 只承诺当前 help/实测格式；不能泛称支持所有新 KTEX 压缩格式 |
| 编译资源 → SCML 学习工程 | krane | 反编译不保证完全保真；用 `--check-animation-fidelity` 并抽检 |
| 已有帧序列/中间 XML ZIP → 运行时 ZIP | 官方 `buildanimation.py` | 使用其依赖环境和实际 XML 结构；不是任意 PNG ZIP 都能输入 |
| 遗留图像编译 | 官方 `image_build.py` | 使用匹配的 Python/klei 库，先在临时目录探测路径行为 |

PowerShell 示例（先把变量设为当前环境中已确认的绝对路径）：

```powershell
& $Ktech --help
& $Ktech -i $Tex
& $Ktech $Png $OutputTex
& $Ktech --atlas $OutputXml $Png $OutputTex
& $Krane --help
& $Krane $UnpackedAnimDirectory $OutputScmlDirectory
```

转换后重新读取 TEX/XML，检查透明、方向及输入哈希；样本转换通过不能代替游戏验收。`krane` 的 BIN、目录和 ZIP 输入能力按已安装版本的 help 核对。

官方 SCML 编译通常从 `mod_tools` 工作目录调用：

```powershell
& $Scml $InputScml $TemporaryOutput
```

具体输出位置以该版本实际结果为准。源 SCML 引用图片路径必须可解析；保留源工程和输出之间的映射。

自动编译流程可能包含原图重采样、缓存或清理；已查阅的官方 `scripts/resize.py` 会重采样并保存目标 PNG。先核对所用脚本，在隔离副本运行并比较输入哈希，或选择单资源编译器。强制更新时只处理确认属于本轮的缓存与产物。

## 帧序列与性能

- 不以 60 或 149 帧作为通用硬上限：已核验的原版 `alterguardian_phase1_lunar.zip` 的 `spawn_lunar` 有 215 帧，`archive_lockbox.zip` 的 `activation` 有 196 帧。这不代表任意大图序列都能承受相同帧数。
- 时间轴帧数不等于独立贴图数量。内存与解码成本还取决于独立图像、图集面积、mipmap、元素数、并发实例和加载时机。
- 先查资源有效性和负载，再按视觉质量预算优化；降帧时同时核对时长与节奏。
- “同一 symbol 绝不能跨图集”也未建立为通用限制；由支持该格式的打包器生成并检查 build 中的引用，遇到特定管线问题保留最小复现。
- `FRAMES = 1/30` 秒，约 0.033333 秒；动画资源自身 FPS 可以不同。制作端降 FPS 会改变时长，除非同步调整取帧与时间轴；不能把两者混为一谈。
- `AnimState:SetScale` 可以大于 1，原版有 `SetScale(2, 2)`。属性在哪些端设置以同类原版和实机同步为准，不把“SetPristine 前设置”当成所有后续变化的唯一方法。
- `PlayAnimation` 开始播放新动作，`PushAnimation` 接队列。结束回收应对照原版的事件与 `AnimDone()` 用法；循环动画不能靠普通完成事件清理。

## 交付检查

1. 明确是完整动画、build-only 还是 animation-only，核查依赖都已加载。
2. ZIP CRC、BILD/ANIM 版本、图集引用、TEX 格式/尺寸、XML 路径和 Element 名逐项检查；不能以 ZIP 大小或可打印字符串次数代替解析。
3. 用现成工具读 KTEX，不猜固定字段。mip 层数要读头；DXT 块最小尺寸导致尾部 mip 不满足简单 `w*h` 字节公式。
4. 查看原图/导出预览的方向、pivot、透明、层级、朝向、时间轴；角色衣服的“第几张图用于哪动作”是具体 build 的映射，不是全局编号表。
5. 加载/无头运行验证与真实客户端视觉验收分开记录。客户端检查装备、卸下、皮肤/变身、运动方向、特效结束和远程观察。
6. 修改范围内同步 source/runtime，逐文件哈希；保留可重编的源素材和工具参数。资源删减要先查所有引用再隔离测试。

源码核对入口：`spear.lua`、`sword_lunarplant.lua`、`simutil.lua`、`standardcomponents.lua`、`constants.lua`，以及官方 `buildanimation.py`；按 [环境发现](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md) 定位当前版本。工具分工见 [ktools 作者说明](https://github.com/nsimplex/ktools/blob/master/README.md)，验证边界见 [公开限制](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/public-limits.md)。


---

## 来源：`references/dst-mod-tool.md`

原始 SHA-256：`54d9c2333c48ea483a6a64e7c79d4fd8904b3261c75d05be08e1f89a175137aa`

# DST Mod Tool：文档编辑、脚本接口与视觉验收

这是 DMT 的 Lua 脚本工作流参考页，适用于提供下述 `script --help` 接口的版本。先读取已安装程序的帮助，核对 API、参数和支持格式后再执行示例。

适用：`.dmt` 工作区、SCML/ZIP 资源导入、符号和动作批量编辑、PNG/GIF 预览。接口说明不代表各格式导入、导出或编译均已实测；资源加载与联机效果仍需在游戏中验收。使用前核对当前版本的实际帮助；没有实际执行的格式与功能保持未验证。

尚未安装 DMT 时，先按 [工具安装与首次验证](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) 选择匹配系统的作者发行包并验证所需功能。

## 每次操作先获取接口与状态

```powershell
& $DmtExe script --help
& $DmtExe script --file $AbsoluteLuaFile
```

Windows GUI 子系统程序的输出可能需要重定向捕获。启动后台辅助进程时隐藏窗口；现有用户工作区不得擅自替换。`--file` / `--stdin` / `--text` 三种来源只选一种，复杂内容优先文件。文件路径用绝对路径，Lua Windows 路径用 `[[C:\path\file]]`。

先运行只读脚本：

```lua
print("revision", tool.document_revision)
print("path", tool.document_path)
print("builds", #doc.builds)
print("banks", #doc.banks)
for _, bank in ipairs(doc.banks) do
    print("bank", bank.name, "animations", #bank.animations)
end
local selected = tool.selection.animation
if selected then
    print("selected", selected.name, #selected.frames)
end
```

名称不确定时输出候选，确认目标后用 `find` 和 `assert`。不要凭文件名、集合位置或旧导入的 ID 猜对象。

## 文档与集合

```text
doc.builds → Build.symbols → Symbol.frames → SymbolFrame
doc.banks  → Bank.animations → Animation.frames → AnimFrame.elements → Element
```

- 集合是从 1 开始的只读有序视图，支持 `ipairs` 和 `#`，不支持 `pairs` 或 `collection[i]=...`。
- 结构修改走 `add`、`remove`、`move_to`、`move_to_parent`。名称 `find` 不区分大小写；symbol frame 的 `find(num)` 查帧编号，不是下标。
- 节点 ID 在当前 DMT 文档保存/加载、编辑、撤销中稳定；导出/重新导入 SCML/BIN 后不能当作同一 ID。
- 删除或移动集合项时用倒序索引；对象删除后不能再访问。
- Symbol 按名称、SymbolFrame 按 num 排序，重命名/改编号后位置可能改变。需要对象时保留 handle 或重新 `find`。

| 对象 | 例举操作 |
|---|---|
| Build | name、hidden、clone、move_to、remove_unused_symbols |
| Symbol | name、hidden、clone、move_to_parent、remove_unused_frames |
| SymbolFrame | num、duration、pivot_x/y、replace_image、export_png |
| Bank | name、clone、move_to、transform、anti_follow |
| Animation | name、frame_rate、clone、move_to、reverse、append、crop、transform |
| AnimFrame | set_bounds、clone、move_to、transform、export_png |
| Element | set_reference、set_layer、set_transform、绘制顺序方法 |

这里只列用途；参数/选项范围先查该版本帮助。Element 的 `draw_index==1` 是最前方，`place_above` / `place_below` 要求在同一 AnimFrame。

## 事务与失败处理

- 一次成功 Lua 运行中的 Document 修改作为一次撤销提交；语法/运行/资源/限额错误发生在提交前时不应用修改。
- `tool` 控制、保存、图片导出是延迟命令，在 Document 提交后按顺序执行。失败后停止后续命令，**不会回滚已经提交的文档和此前成功的命令**。
- `tool:undo()` / `redo()` 单独运行，不能与 Document 修改混合。
- `tool:open_document(path)` 替换工作区，是终止型命令，单独调用。它不是 `doc:import_resources`。
- `tool` 的部分字段在脚本里反映排队命令的本地投影；返回的 `report.final_tool_state` 存在时才代表这些命令执行后的真实 App 状态。只读运行通常没有该字段。
- 同时只运行一个请求。遇 `busy` 等待后重试；超时不代表操作未执行，不盲目重放会叠加的编辑。先读状态和报告。

所有外部请求至少检查：

1. `response.type == "script"`；否则是 IPC 层错误。
2. `report.ok`、`report.error`。
3. `report.output` 是否符合预期对象与数量。
4. `report.document.changed`、前后 revision。
5. 每条 `report.tool_results` 的 `ok`；必要时 `final_tool_state`。

不要仅凭退出码、revision 变化或一句“成功”断言保存/导出完成。

## 受控导入与编辑

```lua
local bank = assert(doc.banks:find("my_bank"), "Bank not found")
local animation = assert(bank.animations:find("idle"), "Animation not found")
doc:set_label("调整 idle 的播放速度")
animation.frame_rate = 24
```

该代码仅示范 API，24 不是默认设计值。修改动作时长、画面比例和循环方式需要依据用户要求。

`doc:import_resources({absolute_paths}, options)` 支持该版本帮助列出的 ZIP、DYN、BIN、SCML、GIF、PNG、Spine JSON、PSD，返回新建 build/bank handle。不扫描目录、不接收 `.dmt`。Spine 颜色采用 `spine_colors="bake"` 或 `"ignore"` 时要明确选择；不要依赖不可见弹窗。

需要覆盖 `SymbolFrame` 图像用 `replace_image`。批量替换符号/层用 `doc:search_replace_elements`，按 help 提供 scope/rule。正则模式需要的字段不同，不凭普通搜索示例扩展参数。

变换后的动画 bounds 可以通过 `doc:recalculate_collision` 重算；这里是动画文档中的边界数据，**不能当成已修改游戏实体 Physics 碰撞体**。实际碰撞仍需回到 prefab/Physics 核对。

DMT 脚本的 `doc`/`tool`、沙箱权限和 `pcall` 不属于 DST Mod 运行时。不要把 DMT 文件桥或环境用法复制到 modmain/prefab/widget；也不要从外部直接改 `.dmt` 或手改运行时二进制来替代受控工具。

## 预览与图像验收

```lua
local animation = assert(tool.selection.animation, "Select an Animation first")
local frame = assert(animation.frames[1], "Animation has no frames")
frame:export_png([[D:\preview\first.png]], { max_dimension = 1024 })
```

先导出一张限制尺寸的图并查看；运动连续性需要时再导出序列/GIF。`scale` 与 `max_dimension` 二选一；序列输出要求全新、尚不存在的目录。单帧导出可能原子替换同名文件，使用自有输出路径避免覆盖用户图。

```lua
tool:set_hide_layer("shadow", true)
tool:set_override_symbol("swap_object", "swap_spear")
tool:select_animation(animation)
tool:select_frame(animation.frames[1])
```

这些是预览状态，不是文档修改；DMT 的符号预览映射也不是 DST 三参数 `OverrideSymbol` 原样接口。`select_frame` 传 AnimFrame handle 并暂停；`tool.playback.frame_index` 从 0 开始，集合索引从 1 开始。

取得对应 `tool_results` 成功后，实际打开 PNG 检查朝向、pivot、透明边缘、层级与缩放。生成图像成功不等于画面正确；只看单帧不能声称全部动画连续性合格。

交付资源回到 [图像与动画检查](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md)：按完整/build-only/animation-only 类型检查依赖，核对 Lua 中真实 bank/build/symbol/animation，再做客户端验收。DMT 能播放不能证明游戏加载、玩家输入或多人同步正确。


---

## 来源：`references/audio-particles.md`

原始 SHA-256：`d81aac5c170f5c36722472b686ffdee755ec3d243a370abfca603ecb2feb69c7`

# 音频与粒子特效

本页涵盖声音事件银行和 `VFXEffect` 粒子。动画帧序列见 [帧序列制作](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/animation-recipes.md)。使用当前项目已验证的音频管线，记录输入、工具版本、事件路径和产物；缺少工具时按 [工具安装与首次验证](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) 检查官方 Mod Tools，不另装一整套无关动画工具。

## 音频资源与事件

已验证的 Designer 管线是素材 → FMOD FDP 工程 → FEV 事件元数据 + FSB 采样银行 → Asset 声明 → `SoundEmitter` 事件调用。`PlaySound` 接事件路径，不接任意 MP3/WAV 文件路径。

```lua
Assets = {
    Asset("SOUNDPACKAGE", "sound/my_project.fev"),
    Asset("SOUND", "sound/my_bank.fsb"),
}

-- 使用实际工程中的完整事件路径。
inst.SoundEmitter:PlaySound("my_project/my_group/hit")
```

项目名、事件组、事件名来自工程，银行文件名可以不同。一组 FEV 可以依赖多个 FSB，不能强制“每事件一对文件”或事件组必须叫 `sound`。声明所需依赖即可，不要求 modmain 和 prefab 两处重复声明。

播放器必须有对应 `SoundEmitter`。需要世界空间定位时使用有正确位置的实体，并配置事件的 3D 模式、距离曲线和参数；2D UI/背景音乐有自己的有效用途，不能一律禁止全局音乐播放器。

循环声音使用本 Mod 唯一的句柄，进入时避免重复启动，离开、实体移除、切换角色/世界时清理同一句柄：

```lua
local SOUND_HANDLE = "my_mod_ambient"
inst.SoundEmitter:PlaySound("my_project/ambient/loop", SOUND_HANDLE)
-- 停止该来源的循环。
inst.SoundEmitter:KillSound(SOUND_HANDLE)
```

监听只在需要的端安装。个人背景音乐由本地玩家的客户端生命周期管理；世界音效参照原版实体/状态机的发声端与网络行为，避免主客机重复播放。死亡事件回调签名是 `function(inst, data)`，原因和攻击者在 `data.cause` / `data.afflicter`；旧教程的 `function(cause, afflicter)` 命名会误导参数含义。

替换事件可使用 `RemapSoundEvent(old_event, new_event)`，先确认影响范围与撤销策略，不为单个角色的声音无意改掉全世界同类声音。

## 选择目标工具

以下命令针对 **FMOD Designer 4.44.7 / FEV + FSB** 管线。使用其他版本时先核对 CLI 帮助与工程兼容性；保留已有可工作的 FDP 工程。

如果所用 Mod Tools 包提供 Studio 模板 `Template/myDSTmod.fspro` 和 `DST_MOD_ConfigureMasterBank.js` / `DST_MOD_BuildBanks.js`，将它作为另一条候选管线。该路线尚未完成本技能的运行时接入验证，不能推断任意现代 Studio `.bank` 均可直接加载。使用前核对目标版本的加载接口、Master Bank 标识和客户端最小事件。配置脚本可能修改工程元数据、关闭 Studio，构建批处理还可能复制银行；先检查脚本并设置独立输出。FEV/FSB 与 `.bank` 流程不可混写。

## 素材加工与响度

保留无损母带和加工参数，先读取文件声道、采样率、位深、时长，再决定裁剪、延迟、回声和增益。44.1 kHz / PCM 16-bit 是兼容排查起点，不是强制唯一格式；mono/stereo 选择按定位与素材设计决定，Designer 支持不同采样率、声道及重采样。

PowerShell 中 `$Ffmpeg`、`$Ffprobe`、`$SourceAudio`、`$ProcessedWav` 是已确认的绝对路径；新输出不能覆盖母版。以下转换仅示范已选定 44.1 kHz、16-bit PCM、双声道的情况：

```powershell
& $Ffprobe -v error -show_entries 'stream=codec_name,sample_rate,channels,bits_per_sample:format=duration' -of json $SourceAudio
& $Ffmpeg -hide_banner -nostdin -n -i $SourceAudio -ar 44100 -ac 2 -c:a pcm_s16le $ProcessedWav
if ($LASTEXITCODE -ne 0) { throw '音频转换失败' }
& $Ffmpeg -hide_banner -nostdin -i $ProcessedWav -af 'astats=metadata=1:reset=0' -f null -
```

直接调用 Windows 可执行文件时传 Windows 路径，由参数数组/调用运算符保持路径含空格的边界；Git Bash 是否转换 `/d/` 受环境影响，不把一次失败写成所有 Windows FFmpeg 的限制。

| 操作 | 可用参数与需要核对的地方 |
|---|---|
| 截取 | `-ss`、`-t` 按秒；切点检查不连续和咔哒声，淡化时长由素材决定，循环接缝不能随意淡空 |
| 回声 | `aecho=0.8:0.8:450\|900:0.4\|0.2` 的 delay 是毫秒；两段延迟/衰减数量对应。数值只是语法例 |
| 延迟 | `adelay=150\|150` 表示双声道各 150 ms；按实际声道数量或当前版本的 `all` 参数处理 |
| 多层混音 | `amix=inputs=2:duration=longest`；`normalize=0` 仅在已设计各路增益时选择，叠加后检查削波 |
| 响度/峰值 | `loudnorm`、`astats` 用于测量或有目标的处理；短音效不能只以综合响度判断听感 |
| 限幅 | 查看 `alimiter` 的自动电平设置；当前版本 `level` 默认开启，设置低 limit 后可能被自动补偿，不等于最终输出已经降低 |

表格中的 `\|` 是 Markdown 转义；传给 FFmpeg 的完整滤镜字符串应使用普通 `|` 并整体加引号。单位与选项依据 [FFmpeg 官方滤镜文档](https://ffmpeg.org/ffmpeg-filters.html#aecho)，执行前再看已安装版本帮助。

峰值目标、增益和回声层数按本次素材与游戏混音确定，不继承其他项目的固定值。过响时沿母带 → 滤镜 → 事件/分类增益 → 叠加声部 → 游戏混音查原因，可在合适层修正；不能禁止代码/事件层调音量，也不能每次一律降低 WAV。保留干净母版，避免重复烘焙游戏播放层的 volume/pitch 参数。

## FDP 工程与 3D 设置

优先使用官方示例或有复用许可且已经验证的工程。FDP 是 XML，但复制另一 Mod 的素材或模板仍要有权限；私人临时脚本与 Workshop 项目名不作为本技能依赖。

1. 在独立副本设置命名空间隔离的项目、事件组、事件、银行名，修正所有音频来源和构建输出路径；一个 FEV 可关联多个 FSB，银行名不必等于项目名。
2. 项目/事件标识符不能无差别逐次 uuid4 替换。需要迁移 GUID 时保持同一旧 ID 到同一新 ID 的映射及内部引用，优先由目标编辑器生成；官方 Studio 的 Master Bank 操作不等同于 Designer 的全 GUID 重写。
3. 声音事件组与混音分类不同。组不必叫 `sound`；分类需与游戏音量滑块路由匹配。事件路径变化后更新全部调用点。
4. 一次性事件在实际工程里核对 One-shot、触发条件和声部释放；循环还要检查 Sound Def 实例、事件时间轴、停止方式和代码句柄。`loopmode=1, loopcount2=-1` 只是旧模板片段，不能跳过字段语义检查。
5. 3D 声音同时需要正确的发声实体位置、事件模式、衰减方式及必要参数；把模板“两处 x_2d 改为 x_3d”不能覆盖所有工程。全局或 world 上的 emitter 不会因此把事件格式改成 2D，但其位置可能不符合预期。2D 同样受事件/分类/游戏增益控制，不代表全图恒定最大音量。

Designer 文档的 Min Distance 是开始距离衰减的位置，具体单位须由目标游戏的坐标和音频尺度确认；`mindistance=3` **不能译成“3 格地皮”**。Inverse 模式的 Max Distance 是停止继续衰减的位置，Linear/Linear Square 通常在最大距离衰减至静音，Custom 可忽略这两个值。按实际曲线做近、中、远距离客户端试听，不能仅填 `3/30` 就宣称有正确空间感。依据随工具文档第 141、376 页；One-shot/循环实例语义见第 144、379 页。

## 编译与交付

先读 CLI help，再检查项目的预/后构建命令。`-m` 列出依赖且不构建银行，`-l` 生成波形银行清单，`-k` / `-K` 禁用工程的预/后构建命令。只有明确需要且已审核的构建动作才另行启用。

```powershell
& $FmodDesignerCli -help
& $FmodDesignerCli -pc -k -K -m $ProjectFdp
if ($LASTEXITCODE -ne 0) { throw 'FMOD 工程依赖检查失败' }
New-Item -ItemType Directory -Path $OutputDirectory -ErrorAction Stop | Out-Null
& $FmodDesignerCli -pc -k -K -l -b $OutputDirectory $ProjectFdp
if ($LASTEXITCODE -ne 0) { throw '声音银行构建失败，请检查完整日志' }
Get-ChildItem -LiteralPath $OutputDirectory -File
```

`$OutputDirectory` 选择本次新的独立目录，`$ProjectFdp` 指向副本；若已有输出，先确认归属，不递归删除整个 sound 目录。实际 FEV 与银行文件名由工程决定，以依赖清单和输出为准，不能假定总是同名一对。修改 WAV 或事件配置后重新构建对应产物，核对其哈希与日志，再同步运行时。

```text
交付目录/
├── sound/             实际需要的 FEV 与全部 FSB
├── source/            可编辑 FDP、音频母版及处理后输入
└── integration.md     事件路径、Asset、循环/3D/混音参数、版本、验证记录
```

每项验收明确证据：

1. **文件与工程**：退出码、完整日志、真实输出路径、输入依赖、FEV 事件及银行引用、FSB 可解析的样本数量/编码/采样信息。`strings` 能找到名字只作线索，不能证明完整事件存在或可播放。
2. **编码**：压缩后大小不必接近 WAV PCM，头部标识也不说明 PCM。“192 字节必为空壳”“FSB5 必崩”均不可作判据。2026-09-27 再查当前 153 个原版 FSB 均为 FSB5，仅证明该容器存在；相同头不等于采样编码、FEV 配套和目标平台兼容。
3. **隔离运行**：专服 `nosound` 下打印 `PlaySound` 之后的标记只证明脚本执行到该处，不能声称事件查找、解码、混音和银行加载全部通过。按 [测试与发布](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md) 运行行为测试并正常关闭，不复制旧 `os.exit()` / 强杀共享进程的临时 harness。
4. **声音实测**：用目标工具试听作为中间检查，再到客户端检验第一次触发、循环/停止、近远距离、音量滑块、连续触发、多玩家观察和切世界。没有音频输出/客户端时保留这项待验收，不能用银行大小代替。
5. **回修**：记录实际事件、主客机、Mod 列表、输入与银行版本和失败日志。Lua 无异常但客户端退出时结合原生崩溃记录排查，不先认定一定是 WAV 参数或 FSB 版本；未经解析的 dump 也不能当成根因。

本页提供制作与排错流程；新声音银行仍需编译、客户端加载和试听验收。验证边界见 [公开限制](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/public-limits.md)。

## 粒子系统与网络边界

粒子特效可以由 prefab 包装，但并非所有 FX 都是粒子：AnimState 动画、Light、贴地投影也各有机制。当前原版 `cane_candy_fx.lua` 是网络实体、客户端本地发射器的例子：

1. 创建 Transform、Network，添加 `FX` 标签，在共用初始化里 `SetPristine()`，`persists=false`。
2. 专服 `TheNet:IsDedicated()` 返回后不创建本地 `VFXEffect`；主机的可视客户端仍需要渲染，所以不能简单用 `not TheWorld.ismastersim` 取代该判断。
3. 客户端初始化一次命名空间隔离的颜色/缩放 envelope。
4. 建立 emitter，设置渲染资源、最大粒子数、最长寿命、blend mode、曲线、排序和需要的跟随规则。
5. `EmitterManager:AddEmitter` 根据 tick 时间和累积量发射；按实际场景拥有者移除实体/关闭发射，不能让临时特效永远挂着。

原版路径可以直接供渲染 API 使用；Mod 内相对资源路径需要按照加载环境用 `resolvefilepath` 解析，尤其 `SetRenderResources` 这类不替你定位 Mod 根的接口。不能据原版裸路径反过来删掉 Mod 的路径解析。

```lua
local TEXTURE = resolvefilepath("images/fx/my_mod_spark.tex")
local SHADER = "shaders/vfx_particle.ksh"
local assets = {
    Asset("IMAGE", TEXTURE),
    Asset("SHADER", SHADER),
}
```

此处是资源声明片段，完整 prefab 应从当前同类原版裁取，保留全部必需初始化。不要直接复制教程中的示例数值作为设计默认。

## 粒子参数与清理

- 世界空间位置是 x/y/z，其中 y 为高度。绑定父实体后重新确认位置使用局部还是世界坐标，移动拖尾与跟随粒子不一定相同。
- 颜色 envelope 使用归一化生命周期进度和颜色值；`IntColour` 输入通常是 0..255。教程 `IntColour(217,39,390,80)` 明显越界，不应原样继承。
- `AddRotatingParticle` 的 angle 参数不是 UV 坐标。教程变量叫 `uv_offset` 却传给 angle，是误命名/机制混淆；需要图集帧时参考 `AddRotatingParticleUV`、`SetUVFrameSize` 的配套用法。
- 粒子数量、寿命、发射频率一起决定负载。原版代码里的每 tick 随机倍率只代表具体效果，不等于严格的每秒目标数；要精确速率时先定义累积/抖动需求。
- 客户端随机装饰可以各自不同。影响伤害/命中的范围和时刻由服务器判定，不用粒子的位置反推游戏逻辑。
- `persists=false` 仅表示不存档，不代表自动在动画/计时结束时移除。父子关系、事件监听、延迟任务、EmitterManager 注册的清理都要核对；重复进入世界/复活要防止重复生成。
- 混合模式、泛光和 shader 需以当前资产及客户端效果验证；专服 PASS 不证明有画面。需要截图/视频验收时明确抽检的实例、时段和机位，不声称看过未播放素材。

源码核对入口：`prefabs/cane_candy_fx.lua:16-42,49-65,68-131`、`components/health.lua:590`、`components/dynamicmusic.lua` 的绑定/解绑；参数参考随工具提供的《FMOD Designer 2010》80、142、152-157、205 页。行号与工具文档有各自版本范围；现代 FMOD Studio 文档可帮助理解概念，不能代替目标 DST 版本的实际验证。


---

## 来源：`references/animation-recipes.md`

原始 SHA-256：`94801522bc7b4a3dd4023d8b688e1078a5edc1c550550144cbd7bb2c7427f936`

# 帧序列、锚点与旋转动画

用于 GIF/WebP/PNG 序列转运行时动画，以及静态图制作旋转效果。资源类型、bank/build、库存图和客户端检查先见 [图像与动画](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md)；缺工具按 [工具安装与首次验证](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) 推进，已有 SCML 或可编辑 DMT 工程优先保留，不强制改成逐帧烘焙。

## 先确定输入和时间轴

1. 登记源文件哈希、画布、逐帧时长、透明方式、循环次数、目标锚点和用途。已有手改 PNG 时以明确选定的输入为准，不用旧 GIF 再导出覆盖。
2. 解码 GIF/WebP 时处理帧间合成和 disposal，导出完整 RGBA 帧并保留时长清单；只读取局部更新矩形会丢掉上一帧内容。抽检首尾、透明边缘和帧数。
3. GIF 的透明索引不能保存连续 alpha；需要柔边时保留 PNG/WebP 母版，GIF 只作预览。预览播放器的时长取整不代表引擎实际帧率。
4. 本页所核验的 `buildanimation.py` 对 XML `framerate` 调用 `int()`，再写入二进制 float；因此这条管线需要正整数 FPS，不能据此宣称所有 DST 动画只支持整数 FPS。

每帧原时长为 `d_i` 时，总时长是 `T = sum(d_i)`。固定 FPS 输出有 N 个时间轴帧，其时长约为 `N/FPS`。非均匀时长要按累计时间重采样，允许重复引用同一张 PNG；不可仅用第一帧时长推算整个动画。把 33.33 直接截成 33 会改变时长，是否接受、降帧或改节奏属于设计选择。循环时间轴通常避免把首帧作为末帧再停一次；非循环动画保留完整尾部。

## 透明、缩放与视觉锚点

- 已有 alpha 就保留。黑底发光素材可试 `alpha=max(R,G,B)`，并在非零 alpha 上反算颜色以消除黑底污染；这是特定合成假设，不是通用抠图。黑色主体和阴影可能被删掉，先在黑、灰、白背景预览。
- 白底淡彩图也不能简单反亮度后当成正确 alpha。JPEG 噪声、高光和白色主体都需要检查；固定阈值、gamma、增强倍数只属于具体素材，不写成默认配方。影响观感的“保留淡色/增强颜色”先出对比供用户选择。
- 保留直通 alpha 的源 PNG，并核对编译器是否做 premultiply；已预乘图像再预乘会使边缘发黑。本页工具的 `textureconverter.Convert` 默认给转换器传 `--premultiply`。
- 尽量从母版一次缩放，保持长宽比。`AnimState:SetScale` 只能放大已有细节；图像分辨率、几何尺寸、矩阵、实体缩放和镜头一起决定观感，没有“1 格恒等于 200 动画单位”的通用换算。

对宽 W、高 H 的帧，若目标原点在原 PNG 左上角坐标系的 `(cx,cy)`，本页中间 build XML 可设置：

```text
x = W/2 - cx
y = H/2 - cy
顶点左上角 = (x-W/2, y-H/2) = (-cx,-cy)
```

因此底边中心锚点是 `x=0, y=-H/2`；居中锚点为 `x=0, y=0`。同时缩图和几何时，W/H 与 x/y 同比例变化。先区分“画布中心”“实际落点”“动画矩阵平移”，避免重复补偿。

环形落点的自动定位只是辅助：行宽峰值可避开竖直光柱对整图质心的污染，但非对称环、火花、厚环都可能误判。限定合理区域后检查宽度分布；多行接近峰值时可求加权中心。若各帧内容没有真实位移，采用经确认的常量锚点；只有真实位移才逐帧修正。把所有帧按最终坐标叠到固定原点预览，排除计算造成的抖动，再用 DMT/客户端核对落点。

## 中间 ZIP 与坐标

`buildanimation.py` 输入是中间 XML/PNG ZIP，运行时 ZIP 是另一种内容。完整新动画的最小布局：

```text
my_fx_stage.zip
├── build.xml
├── animation.xml
└── frame_000.png
```

```xml
<Build name="my_fx_build">
  <Symbol name="my_fx_symbol">
    <Frame framenum="0" duration="1" w="32" h="24" x="0" y="-12" image="frame_000"/>
  </Symbol>
</Build>
```

```xml
<animations>
  <anim name="idle" root="my_fx_bank" framerate="30">
    <frame x="0" y="-12" w="32" h="24">
      <element name="my_fx_symbol" frame="0" layername="my_fx_layer" m_a="1" m_b="0" m_c="0" m_d="1" m_tx="0" m_ty="0" z_index="0"/>
    </frame>
  </anim>
</animations>
```

这是说明字段的单帧样例，32×24 和 30 FPS 不是设计默认。多帧时逐项对应 symbol 帧号和时间轴；`duration` 表示 build symbol 帧覆盖范围，不等于 GIF 毫秒时长。`image` 写 ZIP 内 PNG 路径去掉 `.png`；标签及 `animation.xml` 文件名区分大小写。本页核验的编译器把 build、symbol、图像、动画、root 等名称编码为 ASCII，名称使用 ASCII；外部文件路径的编码支持另行核对。

- `SetBank("my_fx_bank")` 取自动画的 `root`，`SetBuild("my_fx_build")` 取自 Build.name；ZIP 文件名可不同。原版 spear 的 bank/build 也不同。
- 矩阵排列为 `x'=m_a*x+m_c*y+m_tx`、`y'=m_b*x+m_d*y+m_ty`；不要交换 b/c，或把图片向下的 Y 直接当世界高度。先用单位矩阵和不对称测试图确认方向，再引入旋转/缩放。
- build 的 x/y 是图像中心偏移；动画 frame 的 x/y/w/h 是包围框信息，element 平移由矩阵决定。公开官方 SCML 导出代码将包围中心写入 position，本样例采用该约定。复杂变换保留所用导出器计算的框，并核对四角变换后的范围。
- 动画名的 `_up`、`_down`、`_side` 等后缀会被本编译器识别为朝向并从动作名中拆掉；无意使用保留后缀会改变查找结果。z_index 决定导出排序，不是世界 Z 高度。

坐标依据：[官方 SCML 导出代码](https://github.com/kleientertainment/ds_mod_tools/blob/master/src/app/scml/main.cpp) 的 `export_element`、`extend_bounding_box`、`export_animation_frame`；再对照实际安装版本的 `buildanimation.py`。公开源代码与已安装二进制不自动视为相同版本。

## 图集预算与编译

预算同时考虑独立图像数量、尺寸、透明占用、mipmap、元素数和并发实例。总像素面积只是下界；本页核验的 `klei/atlas.py` 使用面积排序、4 像素对齐和空位搜索。图集数量应以实际打包器输出为准。

本页核验的 `buildanimation.py` 默认最大图集边长 2048、带 alpha 默认 bc3；它允许多个 atlas，并在顶点第六个 float 保存 sampler。`atlas.py` 默认还会在空间允许时缩为非正方形。`--square` 是可选布局开关，不是多图集必需修复；“单 symbol 绝不能跨 atlas”不是已证实的引擎限制。出现某管线色块应保留可复现资产，查图集引用、UV、premultiply、几何和客户端效果。

PowerShell：把变量设为已确认的绝对路径，输出目录选择独立工作区。

```powershell
$Compiler = Join-Path $ModTools 'tools/scripts/buildanimation.py'
$Python27 = Join-Path $ModTools 'buildtools/windows/Python27/python.exe'
& $Python27 -B $Compiler --help
if ($LASTEXITCODE -ne 0) { throw '编译环境不可用' }
$CompileArgs = @('-B', $Compiler, $StageZip, '--force', '--outputdir', $OutputRoot)
& $Python27 @CompileArgs
if ($LASTEXITCODE -ne 0) { throw '动画编译失败，请检查完整日志' }
$ResultZip = Join-Path $OutputRoot ('anim/' + [IO.Path]::GetFileNameWithoutExtension($StageZip) + '.zip')
if (-not (Test-Path -LiteralPath $ResultZip -PathType Leaf)) { throw '未生成预期动画 ZIP' }
```

该示例针对随工具提供的 Python 2 脚本，使用其匹配的 Python 2.7 和依赖。已核验版本可从工具目录外用绝对路径调用；相对 `--outputdir` 按输入路径的上级解析，因此建议明确绝对输出路径。检查日志及二进制；`--ignoreexceptions` 会改变失败处理，`sitecustomize` 警告也需核对原因。

遇到路径错误先记录工具版本、原路径和编码；必要时在本次独立 ASCII 路径副本重现，不移动原素材。ktech 应按当前 help 使用位置参数及明确 `.png` 输出，不能把无扩展名文件盲当固定 2048² 裸 RGBA。

## 静态图制作旋转效果

先确认是一整层旋转还是内外层独立运动。现有动画工程能用多 symbol 和矩阵表达时优先沿用；需要逐帧烘焙或受工具限制时，再把各层合成为帧序列。

1. 在母版标明环心，必要时查看径向 alpha 分布选择内外层分界。低 alpha 区可减少接缝，但不保证硬切永远无痕；检查旋转后缝隙。
2. 画布需覆盖绕锚点旋转的最远可见点，并留滤波边界。百分位去噪可能切掉合法装饰，不能代替人工检查。每一帧从母版旋转，避免上一帧接着旋转造成累积损失。
3. 按目标时间轴生成角度；不同库正角方向不同，以不对称标记预览确认。双层反向旋转属于设计选择，不自动采用。
4. 抽检全角度裁边、中心漂移、半透明接缝、循环首尾速度和颜色。图集预算不足时比较分辨率、图层复用、帧率和分段加载的代价；拆 bank/build 还要检查切换时机与资源可用性，不直接改变时长。

## 验收与证据范围

按 [资源交付检查](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md#交付检查) 分层验证：ZIP CRC；BILD/ANIM 版本与名字；symbol/帧号/朝向；顶点区间、UV 和 sampler；所有图集存在且能解码；时长与原点预览；真实客户端和远端观察。KTEX 用工具读取头和 mip 信息，不把固定字节偏移当成所有版本的通用格式。

FX 公共初始化中的 AnimState 视觉配置参照当前同类原版，保持客户端可见；后续动态变化使用正确的同步或客户端更新路径。`SetPristine()` 不是“所有属性之后永远不能变”的边界。循环动画需明确停止和清理，单次动画用匹配的完成事件/状态回收。泛光 shader 和 Light 照明不同，不能靠泛光掩盖缩放模糊。

小图编译、atlas/sampler 结构与资源解析检查不能代替真实大图序列、跨图集资产的客户端渲染验收。按本页制作的素材仍需完成上述客户端检查。

声音制作见 [音频与粒子](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/audio-particles.md)。


---

## 来源：`references/character-and-equipment-art.md`

原始 SHA-256：`b2c59789d2c0623ec4a9c3b5a84365f5f3f016f70f53cf8b146c47d8d3967b5c`

# 角色外观与装备手持资源

用于角色换皮、全新角色部件、手持装备和施法书外观。资源层级、图集、编译工具和通用验收先见 [图像与动画](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md)；角色注册与生命周期见 [角色机制](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/characters-brains-stategraphs.md)。仅更换已有角色的造型通常复用其动作；自定义骨架、特殊形态或新增动作仍需要对应动画，不能概括为“所有角色永远只做 build”。

## 角色外观：从参考到部件

1. 先区分改色、局部重绘、全新造型与改变动作。记录原角色的 bank/build、符号帧、朝向、画布和 pivot，保留可回退的原工程。不要把某个模板的符号数、帧数或画布尺寸当成全角色标准。
2. 选择当前角色兼容的模板或原有工程。仅改色/换图时保留既有帧编号与锚点可降低风险；改变轮廓或画布时可以调整 pivot 和位置，但必须同步坐标映射并检查完整动作。不能用“画布永远不准改”限制所有新角色。
3. 三视图是拆件参考，不能直接当成可播放 build。按实际符号拆头、脸、头发、身体、手脚等，核对同一方向的遮挡关系、连接处和动作所需帧。表达式/头部位置取本角色测量值，不继承历史人物的像素偏移。
4. 调色和重绘从未加工源文件生成，避免重复映射、反复重采样。已有透明图保留 alpha；白底素材有白色衣物/高光时，不能全局删白。检查边缘、半透明发丝与深浅背景下的颜色。
5. 工具由当前可用能力决定，不固定某个本地生成模型、端口、工作流节点或去背阈值。若使用图像生成工具，仍需逐部件检查轮廓、朝向、设计一致性及原图授权。

[Extended Sample Character 作者仓库](https://github.com/DragonWolfLeo/extendedsamplecharacter-dontstarvetogether)可作为模板来源和工程说明。其默认 SCML 使用方式不等于所有管线的格式限制；先核对所取版本、许可与当前游戏，再选择复用范围。本技能不捆绑模板素材或私人角色工程。

## 编译与预览

- 在独立输出目录编译受影响工程，记录输入与产物清单。仅改 ZIP 文件名不会改内部 build；重命名需沿资源声明、编译源、内部名称与调用方核对。缓存提示异常时先核对依赖和实际输出，不删除整个 `anim/` 强迫重编。
- 解析实际 build 的符号、帧号、图集引用；需要动作时解析 anim 的 bank/动作/朝向。`krane` 导出与 DST Mod Tool 预览有助于交叉检查，但一个工具能打开不等于全部游戏行为通过。
- 角色预览应组合真实动作和本角色 build。`BUILD_PLAYER` 等零件陈列动作只适合检查部件存在性，不能替代站立、跑动、受击与装备姿态。
- 软件预览必须使用本工程的 pivot、矩阵、图层和朝向规则。不要把一份 krane/SCML 转换器的“反序绘制”或 Y 翻转公式无条件套到另一格式。用非对称小样本确认上下左右、旋转方向、锚点及遮挡后再批量渲染。
- 模板 build 缺少某些原版符号时，检查目标动画是否真的引用、是否应该隐藏或复用；软件渲染器简单跳过缺符号只能作为诊断，不能作为游戏资源验收。

## 新角色 Mod 的资源接入

按实际工程建立映射表：角色 prefab → 注册名称/字符串键 → 皮肤定义/build → 选人、头像、小地图与幽灵资源 → XML Element 名及 TEX 路径。只改文本和目录不能改变二进制内部名称；只改 PNG 也不会自动更新 TEX/ZIP。

`MakePlayerCharacter` 默认设置 `wilson` bank，并为调试生成设置默认 build，随后还有 skinner 路径。测试普通出生、调试生成、换肤和幽灵/复活时都需检查最终 build，不能只在初始化末尾强行 `SetBuild` 掩盖映射问题。

角色专属组件先查工厂和相近角色是否添加。当前 `wes.lua` 在使用 `efficientuser` 前判空添加；`wickerbottom.lua` 自己添加 `reader`。组件不存在时不能直接调方法，也不能为所有角色无条件加同一组件。

名称缺失先对照真实 prefab、`STRINGS.NAMES` 和对应消费者；台词的状态表/角色键另按 [角色机制](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/characters-brains-stategraphs.md)核查，不把所有字符串表都写成同一种结构。Lua 字符串可使用合法长字符串或转义换行，不需要一律禁止多行描述。

新角色测试应实际生成角色并检查关键组件和出生路径，单纯启动世界不覆盖 `master_postinit`。使用 [当前测试器](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)的 `TEST.After` / `TEST.Done` 完成协议；旧共享测试目录、打印标记、强杀占端口进程与私人存档路径不作为默认流程。

## 手持装备：按引用链排错

先分别列出 ZIP 路径、内部 build、源 symbol 和角色的目标 symbol。装备不显示时按以下顺序检查，而不是把所有名字统一后反复改动画名：

1. 资源已加载，build 名与实际产物一致。
2. `OverrideSymbol(目标, build, 源符号)` 的源符号存在，并有该动作所需的帧/朝向；原版 `sword_lunarplant.lua` 的 build 和源符号名称就不同。
3. 装备回调确实执行，目标符号和 `ARM_carry` / `ARM_normal` 等显隐与同类原版一致；皮肤分支可能使用 `OverrideItemSkinSymbol`。
4. 检查源图、pivot、矩阵、缩放、透明区域以及后续皮肤/变身/另一装备的覆盖。手持并不存在统一“必须填满 200 像素画布”的规则。
5. 卸下或换装备时沿原版恢复路径处理本 Mod 拥有的外观。不能延迟无条件清空 `swap_object`，从而擦掉后来装备的覆盖。

纯换符号可使用 build-only。当前原版 `swap_spear.zip` 无 `anim.bin`；角色不会为了显示手持物去播放该包的 `BUILD_90s_90s`。旧 SCML 模板的编译入口动画可以保留，但不要把它当成引擎显示条件。

符号核验要读取 BILD 对应版本的符号记录及名称表；散扫明文或在整个二进制中搜索某个四字节哈希都可能误判。当前官方 `buildanimation.py` 的符号哈希逐字符转小写，再按 32 位 SDBM 累积；仅匹配字节串不证明它位于符号表、拥有所需帧或没有碰撞。

## 书籍、灯光与验收

使用原版 `book` 状态时，查 `SGwilson` 的 `book2` 和物品定义。当前路径支持 `book.swap_build` 与 `book.swap_prefix`（默认 `book`），用 `<prefix>_open` / `<prefix>_closed` 源符号覆盖角色的 `book_open` / `book_closed`。书本 FX、骑乘与皮肤是另行处理的分支，不要用挂在人物原点的整张大书图替代这些机制。法术与地图动作见 [法术与数值](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/spells-and-custom-stats.md)。

灯光是引擎 `Light` 接口，原版使用 `inst.entity:AddLight()` 及 `inst.Light`；不能从“找不到 RemoveLight”推导应新增一个名为 `light` 的 Lua 组件。需要关闭/回收时沿同类原版的 `Light:Enable` 或独立灯光实体生命周期；发光贴图、Bloom 与照亮环境是不同效果。

交付至少核对：源工程可追踪、内部名称和图集引用、目标动作与朝向预览、装备/卸下/换装、皮肤与形态变化、幽灵/复活、主机和远端观察者。静态检查、软件预览、专服加载和真实客户端视觉分别报告；不以字符数、文件大小或软件截图替代实际客户端结果。

核验基线：2026-09-27 安装源码的 `prefabs/player_common.lua:MakePlayerCharacter`、`prefabs/wes.lua`、`prefabs/wickerbottom.lua`、`prefabs/spear.lua`、`prefabs/sword_lunarplant.lua`、`stategraphs/SGwilson.lua:book2`，实际 `data/anim/swap_spear.zip`，以及安装版 `mod_tools/tools/scripts/buildanimation.py:strhash/ExportBuild`。源码指纹见 [环境与来源](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)。


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
