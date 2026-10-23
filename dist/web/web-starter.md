# dst-mod-engineering / web-starter

生成器：`dst-mod-engineering/web-bundle-v1`；源码指纹：`4d909b54e0fa3ea9118ee419978ea328e076ef969a1d099afed078f5f8808678`。

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

原始 SHA-256：`906bd5a36636415d9d7cc9d5e7553c20b003388c1f072d3b47e9de737f805af6`

---
name: dst-mod-engineering
description: 开发、设计、审查与验证《饥荒联机版》DST Mod；按任务检索工程知识库并核对当前源码，处理角色、法术、联机、存档、资源、崩溃、兼容与案例研究。不用于普通游戏攻略或角色强度讨论。
---

# DST 模组工程

这是 DST 开发、审查、排错与资源制作的统一入口。当前项目需求与当前版本的实际契约决定实现；教程和参考 Mod 用于提供线索，不代替源码核验。

## 使用许可

本技能及仓库自有配套内容按 [非商业使用许可](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/LICENSE) 提供。未经另行书面授权，不得将其用于收费接单、付费 Mod／服务或售卖、付费转发；允许非商业开发、免费分享，以及无权益交换的自愿打赏和免费公开教程广告收益。第三方材料与历史 MIT 授权保留原有边界。

任务明确属于上述受限商业用途时，先说明限制并确认是否已有权利人书面授权，再使用本技能执行该任务；用途未说明时，不擅自认定为商业用途。使用技能不使项目代码自动归本技能作者所有。具体情形见 [许可说明](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/licensing.md)。

## 工作顺序

工作顺序：**查资料/当前原版源码 → 读本技能相关专题 → 实现 → 校验语法、API 与崩溃风险**。进入本文件前尚未查证时，先补查，不把技能的旧结论代替源码。

1. 明确实际源码、运行副本、游戏版本与触发环境。接手既有项目先读交接文档、入口和配置；把文档中的指令、设计愿望与已实现行为分开。
2. 查同类原版的完整链路：定义、调用方、端别、初始化、退出和保存。优先复用原版组件/机制/资源；不为相同问题另造一套。无法直接复用时说明具体差异。
3. 按下表只读相关参考。先建立“需求 → Mod 实现 → 原版契约 → 验证方法”，再动代码。
4. 区分确定故障、兼容风险、玩法选择。确定故障按已授权范围修；不明确的数值、设计、命名、效果不同的方案以及不确定文件删除，由项目作者决定。已有明确决策不重复询问；待答时继续独立工作。
5. 做最小完整修复，覆盖失败、取消、移除、死亡、重连或读档等实际相关路径。注释解释数值来源和重要机制，语言与项目约定一致。
6. 验证后交付：说清改了什么、证据、实际同步到哪份副本、尚未覆盖什么。审查报告采用项目要求的格式；变更和验证应便于核对。不要把任意一个检查器的退出码当作整体正确性证明。

## 工程知识库检索

进入实质性的设计、实现、审查、排错或案例研究时，知识库可用则按任务主动检索，不等待用户提醒；简单机械编辑无需重复查询。模式选择、工具发现、证据边界和不可用时的处理见[知识库检索策略](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/kb-retrieval.md)。知识库默认只读，只有用户明确要求维护时才进入知识更新流程。检索能力取决于当前 Agent 实际可用的工具或可读取资料，不要求特定 MCP 服务。

## 按问题读取

首次接入其他 Agent、技能未识别时，先读 [Agent 接入](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/agent-setup.md)。缺少当前任务必需的动画工具时，先读 [工具安装与首次验证](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md)：主动查明来源、平台和最小依赖，给出可执行的安装方案；获得相应安装授权后继续下载、配置和产物验证。已有授权不重复询问，也不能只报告“工具不存在”后停下。

网页聊天、上传附件或云端执行环境先读 [网页使用指南](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/web-chat.md)：确认实际可读的材料和执行位置，按任务补充资料；不能把上传成功当作完整读取，也不能把云端脚本运行当成本机 DST 验收。

| 当前任务 | 参考文件 |
|---|---|
| 工程知识库检索、模式选择、证据边界与维护 | [kb-retrieval.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/kb-retrieval.md) |
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


---

## 来源：`references/web-chat.md`

原始 SHA-256：`1d45198d89ea366b7e19546a73d2326b0ad1713dd7f2795591927d2ce045b4ae`

# 网页聊天中的 DST 开发协作

本页说明网页中的资料传递与协作流程，DST 技术规则见 [技能入口](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/SKILL.md) 及相关专题。平台入口按 **2026-09-27** 核验的官方文档列出，尚未经过网页导入与执行的端到端实测。

## 先选当前会话实际具备的模式

| 模式 | 怎么提供技能 | 能力需要怎样确认 |
|---|---|---|
| 原生技能上传 | 平台确有技能导入入口时，按其要求上传完整技能包并启用 | 确认技能名称、入口内容和所需参考确实可读；启用不代表所有脚本已运行 |
| 普通附件 / 项目资料 | 上传入口或选题说明，再按当前任务补充专题和源码 | 要求列出实际读取的文件/片段；附件出现不代表全文已被检索 |
| 可用的云端执行环境 | 在前两种模式基础上，让 AI 检查实际工作区、解释器与可执行工具 | 只有执行记录证明运行过；云端文件、进程和路径不是用户电脑上的文件、进程和路径 |

没有原生技能入口时使用附件模式；不支持 ZIP 解压时，上传相关文本或粘贴带路径的片段。链接只用于定位，需确认内容实际可读。

## 下载哪一份

从 GitHub 的 [dist/web 目录](https://github.com/Zechariah0121/dst-mod-engineering/tree/main/dist/web) 或下表直链下载。普通聊天按任务选 **一份**阅读材料即可，无需安装 Git；保存 Markdown 原文，不要上传 GitHub 的 HTML 页面。

| 文件 | 使用场景 |
|---|---|
| [web-starter.md](https://raw.githubusercontent.com/Zechariah0121/dst-mod-engineering/main/dist/web/web-starter.md) | 不确定从哪开始：通用入口、能力确认和材料选择 |
| [web-code-review.md](https://raw.githubusercontent.com/Zechariah0121/dst-mod-engineering/main/dist/web/web-code-review.md) | 代码审查、确定故障修复与验证 |
| [web-networking.md](https://raw.githubusercontent.com/Zechariah0121/dst-mod-engineering/main/dist/web/web-networking.md) | 主客机同步、RPC、UI、生命周期 |
| [web-assets.md](https://raw.githubusercontent.com/Zechariah0121/dst-mod-engineering/main/dist/web/web-assets.md) | 贴图、动画、音效与工具准备 |
| [web-worldgen.md](https://raw.githubusercontent.com/Zechariah0121/dst-mod-engineering/main/dist/web/web-worldgen.md) | 世界生成与空间判定 |
| [web-full.md](https://raw.githubusercontent.com/Zechariah0121/dst-mod-engineering/main/dist/web/web-full.md) | 可选完整阅读版；不是首次使用的默认选项 |
| [dst-mod-engineering.skill.zip](https://raw.githubusercontent.com/Zechariah0121/dst-mod-engineering/main/dist/web/dst-mod-engineering.skill.zip) | 原生技能导入器使用的完整目录包，**不是插件 ZIP** |
| [web-reading.zip](https://raw.githubusercontent.com/Zechariah0121/dst-mod-engineering/main/dist/web/web-reading.zip) | 一次取得阅读资料与本机回传模板；先在本机解压，再按任务选择上传 |
| [bundle-index.json](https://raw.githubusercontent.com/Zechariah0121/dst-mod-engineering/main/dist/web/bundle-index.json) | 核对来源指纹、源文件与产物哈希；阅读 ZIP 内另附 `reading-index.json`，原生技能 ZIP 的文件哈希在此索引中核对 |

专题版已含共同说明，无需叠加 starter 或 full。记录所用版本或来源指纹，换版时核对差异。

### Claude 的原生技能入口

核验时的官方操作是 **Customize → Skills → “+” / Create skill → Upload a skill**，上传后启用。需要账户允许技能与代码执行；组织限制或缺少入口时改用附件。[Claude 官方使用说明](https://support.claude.com/en/articles/12512180-use-skills-in-claude)

技能 ZIP 的顶层目录应为 `dst-mod-engineering`，内含 `SKILL.md`、`references/`、`scripts/` 等完整内容，不要再套下载目录或分支目录。[Claude 官方打包说明](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

```text
技能包.zip
└── dst-mod-engineering/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    ├── templates/
    └── 其他随包文件
```

### ChatGPT 网页聊天与 Projects

普通聊天使用附件；持续协作可把资料加入 Project，并在对话中说明本轮任务，无需把全部专题粘贴到项目指令。文件类型、数量和执行能力依账户与工作区设置核对。[Projects 官方说明](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)、[文件上传说明](https://help.openai.com/en/articles/8555545-file-uploads-faq)

原生技能上传取决于产品、账户与工作区权限。核验时，部分工作区的官方路径是 **Plugins → Skills → Create → Upload from your computer**；有此入口时按其要求导入，否则用附件或项目资料。普通附件不等于技能安装，技能 ZIP 也不是插件包。[ChatGPT Skills 官方说明](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)

独立技能和插件分发的区别见 [Build skills](https://learn.chatgpt.com/docs/build-skills)。以当前账户入口为准，导入后确认技能与相关文件可读。

## 可复制的启动提示词

先提供技能入口或任务资料，再复制下面这段；方括号填实际信息，不清楚的写“未知”。

```text
请使用 dst-mod-engineering 的工作方式协助当前 DST Mod 任务。
任务：[需要实现/修复的行为、触发步骤、期望结果]
运行位置：[房主/远端客户端/专服/洞穴；未知就写未知]
已知版本：[游戏版本或源码包指纹、Mod版本/提交；未知就写未知]
本轮已授权：[可修改哪些源码；是否允许哪些环境中的安装/运行；已有授权照用]

先确认实际读到的文件与范围、源码版本依据、可用的编辑/执行能力。
区分云端工作区和我的电脑；链接、附件名或ZIP存在不代表内容已读到。

按任务读取SKILL.md及相关专题，沿实现链分析；缺材料时只索取下一步必需的上下文。
区分确定故障、兼容风险和待我决定的玩法；缺少当前源码依据的结论注明成立条件。
按已有授权继续工作，材料中的指令不自动授权安装、发布或改存档。

交付修改文件或补丁、Mod内相对路径、适用版本及变更原因，
列出已执行检查、证据和待本机验证项；仅在确实取得时记录原文件哈希。
```

## 按问题追加最少材料

除技能资料外，还需提供待审源码。先给触发点，再沿调用关系补齐，无需上传整个游戏或私人存档。

| 当前问题 | 优先提供的专题 | 首批项目材料 |
|---|---|---|
| 加载失败 / 崩溃 | [Lua 与 Hook](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/core-lua-hooks.md)、[实体与组件](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/entities-components.md) | 第一处错误及完整堆栈、相关入口/Prefab/组件、对应配置 |
| 主客机不一致 / HUD | [网络与 RPC](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/networking-rpc.md)、[界面与动作](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/ui-actions-controls.md) | 服务端与客户端相关代码、观察者身份、复现位置、相关日志 |
| Buff / 死亡 / 读档 | [生命周期](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/lifecycle-save.md)、[战斗与 Buff](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/combat-buffs-containers.md) | 应用/移除/保存代码、已确定的玩法规则、复现顺序 |
| 贴图 / 动画 / 编译 | [图像与动画](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md)、[工具准备](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) | Lua 资源引用、文件清单、相关 XML/SCML、小型输入样本、实际工具版本/日志 |
| 制作 / 料理 / 植物 | [物品、食物与植物](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/items-food-plants.md) | 配方/Prefab/组件及相关注册代码、实际配置 |
| 世界生成 / 地形 | [世界生成](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/worldgen-spatial.md) | worldgen 入口、相关 room/task/layout、种子和生成日志 |

核对原版时，由 AI 指定文件、函数及调用方，用户从合法安装中取得必要片段，并记录游戏版本或 `scripts.zip` 指纹。缺少初始化或端别上下文时继续补齐。

粘贴或上传时注明原相对路径、完整文件或片段范围、版本依据。同名附件可编码路径，如 `scripts__components__my_component.lua`，并附映射。

平台不接收文本后缀时，可上传内容不变的文本副本并注明原扩展名；执行前恢复路径和文件类型。二进制动画、TEX 或压缩包需使用相应解析工具，不能靠改名 `.txt` 读取。

无法补齐源码时，给出候选原因、成立条件和检查方法；涉及 API、顺序或端别的修复标为待确认。

## 云端能运行时，怎样使用脚本

先确认脚本、输入、依赖和执行权限，记录实际环境。有 Python 不代表可以安装包、联网下载或运行 Windows EXE。

- 已有 Python / `luaparser` 且输入完整时，可做 [静态检查](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)；没有实际运行就交付命令，不编造输出。
- 只有部分源码片段时，记录检查范围；`check_api.py` 需要它支持的原版源码输入布局，不能拿不完整摘要冒充完整目录。
- PNG/XML/ZIP 结构检查与模拟测试可在具备相应能力的环境执行，但不等于引擎解码、真实 UI 或联机通过。
- 随附专服启动器需要其支持的 Windows 游戏环境。普通云端沙盒不能使用用户电脑的盘符，也不能由云端 Python 的成功结果推断本机专服通过。
- 若会话另有明确授权的本机执行连接，先核对实际主机、路径和权限；只有相应调用记录才能报告本机执行。

云端产物需确认可下载且完整，再应用到 Mod 源目录或游戏运行副本；不会自动同步或发布到 Workshop。

## 缺工具与安装授权

按 [工具安装与首次验证](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) 准备当前任务所需工具。缺项时说明官方/作者来源、适用平台、必要依赖、安装目录与样本验证步骤。

有执行连接与已有授权时继续执行；缺少本机连接时，提供方案和命令，由用户或本机 Agent 运行。只为尚未授权的操作或未决定的效果请求确认。

## 交付和本机回传

交付须能对应明确的原文件：

1. 列出每个新增/修改文件相对于 **Mod 根目录** 的路径，说明交付的是完整文件还是补丁；不要提供云端绝对路径作为用户安装目标。
2. 记录适用的原提交/版本与原文件 SHA-256（确实取得时）。只有粘贴文本时不得声称知道本机原文件哈希；文本副本哈希需标明编码/换行范围。
3. 给出改动原因、影响和剩余玩法决策；原文件版本不匹配时先重新比较，不能强行覆盖后来的修改。
4. 分开列已执行的检查、命令/环境/证据与待用户执行步骤；“静态通过”“云端模拟通过”“专服通过”“客户端通过”分别记。
5. 在副本上应用并比较差异，保留私人存档；发布需单独授权。
6. 用 [本机验证回传模板](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/templates/local-validation.md) 收集对应副本、结果和未测项，再根据新证据继续修复。

回传日志保留错误前后文、堆栈、版本和测试标记；令牌、密码及无关私人内容用占位符替换，注明删改字段。原始日志留在本机。

证据等级见 [测试与交付](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)，已测范围见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。


---

## 来源：`references/environment-tools.md`

原始 SHA-256：`c35440d8954037f75cae2916b928db934f9f783555a2bf7281e1a52cf9000186`

# 环境发现与来源定位

先发现当前项目实际使用的游戏、源码与工具，再配置绝对路径。本技能不绑定固定安装目录，也不随仓库分发游戏源码、编译器或第三方可执行程序。

当前任务缺少工具时，按 [工具安装与首次验证](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) 给出来源、平台、最小安装方案和验收方法；授权后继续执行。其他 Agent 的加载路径与能力检查见 [Agent 接入](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/agent-setup.md)。

在网页或远端执行环境中，先区分文件、解释器和工具属于哪台主机。上传文件不会暴露用户的本机盘符；云端下载或安装 DMT 也不等于用户电脑已安装。按 [网页使用指南](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/web-chat.md) 确认实际能力，需要本机执行时交付具体步骤并等待真实日志。

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

接手项目时读取该项目的约定、交接文档与当前配置。历史报告不证明今天的副本相同。环境路径应保存在项目自己的本地配置或会话变量中，避免把开发者用户名和绝对目录写入可公开的技能。

## 查阅当前源码

使用解压副本前，核对它与当前安装包的相关条目是否一致。游戏更新或哈希改变后，重新比较相关文件与行号。历史源码指纹与核验范围见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。

源码先用 `rg --files`/`rg -n` 定位。没找到按 prefab 命名的文件时，查合并返回多个 Prefab 的文件、工厂函数、调用链；如帽子集中在 `prefabs/hats.lua`。Lua 中没定义的引擎方法可能来自 C++，不能凭一次搜索判不存在。

无需解压时，在技能目录用 PowerShell 调用（先将 `$python`、`$dst` 赋为已发现并核对的绝对路径）：

```powershell
& $python scripts/dst_zip_tool.py --dst $dst info
& $python scripts/dst_zip_tool.py --dst $dst grep 'SetMaxHealth' --path components/health.lua
& $python scripts/dst_zip_tool.py --dst $dst show components/health.lua --start 1 --count 100
```

`$python`、`$dst` 由当前已验证路径赋值。全局参数 `--dst`/`--zip` 放子命令前；`extract MEMBER --out EXACT_NEW_FILE` 只导出单文件且拒绝覆盖。

## 工具采用原则

读取已安装程序的 metadata/`--help`，在副本上运行所需操作，再检查输出产物。以程序自报版本为准，不用目录名推断版本。DMT 脚本接口见 [dst-mod-tool.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/dst-mod-tool.md)。

历史教程附带的可执行文件不作为默认工具；先做压缩包清单/文本源码审查。需要换工具时先比较现有工具能否完成同一产物，再按用户授权处理安装。

不同 shell 的 stdout、编码、引号与路径行为用实际调用确认。含复杂字符串的操作优先使用脚本文件，清理文件在同一 shell 中用明确路径执行。随附测试器使用独立 ASCII 引擎存档路径，以避开已遇到的 Windows 中文存档路径兼容问题；报告目录可位于中文工作区。解释器能读取中文源码，不代表引擎也能处理同一路径。

## 随附测试器的特殊边界

- 默认引擎存档位于系统临时目录 `dst_mod_engineering/<运行ID>/DME/Cluster`；可传 `--storage-root ASCII_DIRECTORY`。命令同时传 `-persistent_storage_root`、`-conf_dir`、`-cluster`、`-shard`，不依赖当前账户的真实存档。
- LAN 测试端口按引擎日志允许的范围选择。工具先查空闲端口，但查完到启动仍可能竞争；端口冲突时换用空闲端口，不终止无关服务器。
- runner 只终止自己 `Popen` 创建的进程。每轮保留日志、manifest、唯一 staged Mod 与存档，便于排查；清理时先核对 manifest、绝对路径归属与进程状态，勿通配删除真实 `mods`/Klei 目录。
- 唯一测试目录会改变 `modname`。依赖 Workshop ID、硬编码文件夹名、跨 Mod 名称探测的场景必须单独验证配置映射与真实安装环境。

存档路径参数依据 Klei 开发者 [Dedicated Server Command Line Options Guide](https://kleiforums.com/forums/topic/64743-dedicated-server-command-line-options-guide/)。历史实测环境及范围见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。


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

原始 SHA-256：`a91b023002f6a69491597a3cbf33c5f3954866ddadf997745cbc546a6668aa19`

# 不同 Agent 的安装、调用与能力边界

安装路径与调用方式按 **2026-09-27** 核验的官方文档列出；尚未经各产品端到端实测。技能加载、脚本执行和 DST 功能验收需分别确认。

本仓库采用 [Agent Skills 公开格式](https://agentskills.io/specification)。安装时保留完整目录，不能只复制 `SKILL.md`；Agent 需能读取参考文件，执行脚本还需相应环境。各产品的发现路径、命令和权限可能不同。

## 放在哪里、怎样调用

下表中的 `~` 表示运行 Agent 的那台机器上的用户目录；项目路径相对于当前项目根目录。每个目录下再放一个完整的 `dst-mod-engineering/` 文件夹。

| Agent | 项目级技能目录 | 个人技能目录 | 明确调用或确认加载 |
|---|---|---|---|
| Codex | `.agents/skills/` | `~/.agents/skills/` | CLI / IDE 中用 `$dst-mod-engineering`，或通过 `/skills` 选择。见 [OpenAI 文档](https://learn.chatgpt.com/docs/build-skills)。 |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | 输入 `/dst-mod-engineering`。见 [Claude Code 文档](https://code.claude.com/docs/en/skills)。 |
| Cursor | `.cursor/skills/`，也支持 `.agents/skills/` | `~/.cursor/skills/`，也支持 `~/.agents/skills/` | 在 Agent 聊天中输入 `/` 并选技能；该调用附着于当前消息。见 [Cursor 文档](https://cursor.com/docs/skills)。 |
| GitHub Copilot | `.github/skills/`，也支持 `.agents/skills/`、`.claude/skills/` | `~/.copilot/skills/`，也支持 `~/.agents/skills/` | CLI 可在提示中写 `/dst-mod-engineering`；其他界面用明确命名的请求，并确认实际读取的文件。见 [Copilot 安装说明](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) 和 [CLI 调用说明](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)。 |

优先选一个安装位置，避免同名副本混淆；已有安装先核对实际加载路径，再决定是否迁移。

云端会话需另行确认文件可用性：Claude Code 的本地个人技能不会由该路径直接进入云端；Cursor 需使用其支持的同步或远端部署方式；项目技能须存在于远端工作区。见 [Claude Code 云端范围](https://code.claude.com/docs/en/skills#use-skills-in-cowork-and-cloud-sessions) 与 [Cursor 云端范围](https://cursor.com/help/customization/skills#are-user-level-skills-available-on-cloud-agents-and-remote-workers)。技能同步不包含 DST，也不提供本机游戏目录访问权。

## 首次安装示例

没有 Git 时，打开 [本仓库](https://github.com/Zechariah0121/dst-mod-engineering)，选择 **Code → Download ZIP**。见 [GitHub 官方说明](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives)。

解压后，将**直接包含 `SKILL.md` 的完整目录**命名为 `dst-mod-engineering`，复制到上表选定的技能父目录。先确认目标不存在；最终结构应是 `<技能父目录>/dst-mod-engineering/SKILL.md`，不要多套分支目录。

已有 Git 时可使用以下首次安装命令；目标已存在会停止，需先比较已有内容。

Windows PowerShell 示例默认采用 Codex 的个人目录。使用其他 Agent 时，只修改 `$skillParent` 的末段：Claude Code 用 `.claude/skills`，Cursor 用 `.cursor/skills`，Copilot 用 `.copilot/skills`。

```powershell
$skillParent = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.agents/skills'
$skillTarget = Join-Path $skillParent 'dst-mod-engineering'
if (Test-Path -LiteralPath $skillTarget) {
    throw "目标已存在，请先核对已有技能：$skillTarget"
}
Get-Command git -ErrorAction Stop | Out-Null
New-Item -ItemType Directory -Path $skillParent -Force | Out-Null
git clone -- https://github.com/Zechariah0121/dst-mod-engineering.git $skillTarget
if ($LASTEXITCODE -ne 0) { throw '克隆失败；检查原因，不要覆盖重试。' }
foreach ($relative in @('SKILL.md', 'references', 'scripts', 'docs', 'requirements.txt', 'LICENSE')) {
    if (-not (Test-Path -LiteralPath (Join-Path $skillTarget $relative))) {
        throw "技能内容缺失：$relative"
    }
}
Get-Content -LiteralPath (Join-Path $skillTarget 'SKILL.md') -TotalCount 8
```

macOS / Linux 的 Bash 或 Zsh 示例同样默认采用 `.agents/skills`；按上表修改 `skill_parent` 即可。此处允许安装和阅读技能，不表示随附专服启动器支持这些平台。

```sh
(
    set -eu
    skill_parent="$HOME/.agents/skills"
    skill_target="$skill_parent/dst-mod-engineering"
    if [ -e "$skill_target" ] || [ -L "$skill_target" ]; then
        printf '%s\n' "目标已存在，请先核对已有技能：$skill_target" >&2
        exit 1
    fi
    command -v git >/dev/null
    mkdir -p "$skill_parent"
    git clone -- https://github.com/Zechariah0121/dst-mod-engineering.git "$skill_target"
    test -f "$skill_target/SKILL.md"
    test -d "$skill_target/references"
    test -d "$skill_target/scripts"
    test -d "$skill_target/docs"
    test -f "$skill_target/requirements.txt"
    test -f "$skill_target/LICENSE"
)
```

项目级安装需随项目提交时，复制完整技能文件，保留依赖说明和许可证；不要一并提交来源仓库的 `.git` 目录。

## 最小读入检查

先让 Agent 只读检查，不启动游戏、不安装依赖、不编辑 Mod：

> 使用 dst-mod-engineering。先报告你实际读取的 SKILL.md 路径，再读取 references/environment-tools.md 和 references/testing-release.md，说明三个辅助脚本各自能验证什么、不能验证什么。列出当前环境已找到和缺少的工具，但先不要安装、编译或运行游戏。

根据产品确认技能被发现：

- Codex：从技能选择器选中；更新后仍看不到时重启会话。自动匹配依赖任务与描述，不能把没自动触发解释为文件必然无效。[官方加载说明](https://learn.chatgpt.com/docs/build-skills)
- Claude Code：使用上表的 `/dst-mod-engineering`，核对实际来源路径，避免同名个人/项目技能混淆。[官方技能说明](https://code.claude.com/docs/en/skills)
- Cursor：在 `/` 菜单选择技能，也可到 Customize → Skills 查看已发现的条目。[官方技能说明](https://cursor.com/docs/skills)
- Copilot CLI：已启动会话可用 `/skills reload`，再用 `/skills info dst-mod-engineering` 确认位置；其他 Copilot 界面不照搬 CLI 命令。[官方 CLI 说明](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)

结合文件路径与读取记录确认参考文件可读。只读检查应能区分声明检查、服务器行为和真实客户端验收，并指出专服测试器只支持 Windows。

已有合适 Python 时，可在技能根目录分别运行 `python scripts/dst_zip_tool.py --help`、`python scripts/check_api.py --help` 和 `python scripts/dst_modtest.py --help`；用实际解释器路径替换 `python`。帮助成功只证明入口可运行，不能确认 `luaparser` 已安装或游戏测试通过。依赖与运行命令见 [环境与工具准备](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md) 和 [测试与交付](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)。

## 没有 Skills 自动加载的 Agent

网页聊天、附件或原生技能 ZIP 的用法见 [网页使用指南](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/web-chat.md)。能读取工作区文件的 Agent 也可显式读取技能，无需自动加载：

把完整目录放在可访问的位置，将下列路径换成实际位置：

> 请先读取 `<技能绝对目录>/SKILL.md`，按当前任务读取其中链接的参考文件。脚本和文档的相对路径以技能目录为准；待修改的 Mod 是 `<Mod 绝对目录>`。以当前原版源码为依据完成任务，区分确定故障与玩法选择，并说明实际执行了哪些验证。不要因未注册 Skills 就跳过该目录，也不要只读 README 代替技能入口。

参考文档按任务读取，无需每轮全部载入。不能读取本地文件时，由用户提供相关材料；分析和验证结论限于实际取得的内容与执行记录。

## 按任务准备能力

| 能力 | 可完成的工作 | 缺少时的实际边界 |
|---|---|---|
| 读取和检索文件 | 读技能、追踪 Mod 与合法安装的原版源码 | 只有对话文本时，只能讨论已提供的片段 |
| 编辑文件 | 修改已授权的项目并生成报告 | 只能提供补丁建议，由使用者应用 |
| 终端 / 进程执行 | 执行 Python、资源工具和定向测试 | 可以审查命令与代码，不能报告“运行通过” |
| 网络读取 | 获取本仓库、核对官方文档与版本、取得所需工具 | 已有完整本地材料仍可使用；未联网核对的版本明确标注 |
| Windows 本地游戏环境与进程权限 | 运行随附 `dst_modtest.py`，写唯一测试副本和隔离存档 | Linux CI、云端推理或另一品牌 Agent 不会自动具备该环境 |
| 查看图像、试听音频、操作 GUI 与真实客户端 | 检查动画、输入、HUD、声音和实际联机效果；需要时由用户参与 | 导出文件或专服日志不能代替画面、听感和多人验收 |

按实际主机、游戏版本、权限和依赖判断能力。缺少能力时完成可验证部分，列出待验项。

Python、`luaparser`、DST、DMT、ktools 和 FMOD 需按任务另行准备；先检查已有工具与版本。安装和验收见 [缺失工具的准备与安装](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md)，已测范围见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。


---

## 来源：`references/tool-bootstrap.md`

原始 SHA-256：`910a0a84e148c55d70e082319d152ce6351081131d35153920baaf0acbb05159`

# 动画工具安装与首次验证

用于首次搭建环境，或当前任务缺少可用工具时。先查 [环境发现](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)，不要以“未找到”结束工作：提出能完成当前产物的最小安装方案；已有工具能通过同样验证时优先复用。本页不捆绑程序，也不要求一次装齐所有工具。

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
3. **先检查已有安装授权。** 用户已经同意本任务的工具及必要依赖安装时，在该范围内继续下载、安装和验证，不逐个步骤重复提问；尚无授权时先让用户选择具体方案。仅要求“开发 Mod”或“补写安装文档”不自动等于同意新增软件。更换来源、增加未包含的系统依赖或改变安装范围时补充说明并取得相应授权。
4. 授权后从下表作者入口选择实际存在的包，记录页面、版本、平台/架构和下载文件 SHA-256。有作者校验值/签名时对照；自己计算的哈希仅作记录，不能冒充作者认证。版本号不明或平台不匹配时先解决，不拼接猜测的下载 URL。
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
- 需要从源码构建时，按所选分支 README 确定编译器、CMake、ImageMagick 开发库，按需使用 libzip；两分支依赖版本可能不同。先说明新增依赖和构建范围，再执行授权的安装/构建；输出保留在独立目录，不默认 `sudo make install`。已有 Docker 环境可评估维护分支作者提供的容器路线；不要为一次图片转换默认引入 Docker 或整套编译环境。

## 首次验证：得到产物才算工具可用

在自有临时目录放入一张小型 RGBA PNG，含透明边缘和非对称图案；动画任务再放入一份图片引用完整的极简 SCML 副本。记录输入哈希、工具版本、命令、输出及日志。不对现有工程直接运行会预处理原图的自动编译器。

下面是 PowerShell 示例：将路径替换为**实际已安装且获准运行**的工具和自有输入。先创建本轮输出目录，再仅运行已选择的那条管线；不覆盖素材。

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
