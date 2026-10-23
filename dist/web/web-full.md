# dst-mod-engineering / web-full

生成器：`dst-mod-engineering/web-bundle-v1`；源码指纹：`4d909b54e0fa3ea9118ee419978ea328e076ef969a1d099afed078f5f8808678`。

这是从仓库原文生成的阅读包；正文只改写 Markdown 链接目标。段落 SHA-256 对应原始文件字节，不是改写后的正文。未包含的文件、未实际访问的链接及未展开的附件不能算作已读；上传阅读包不等于安装本地工具，也不证明游戏验证通过。公开链接指向 main，可能晚于本包快照。

本包包含：
- `SKILL.md`
- `references/web-chat.md`
- `references/environment-tools.md`
- `references/testing-release.md`
- `README.md`
- `docs/knowledge-integration.md`
- `docs/licensing.md`
- `references/agent-setup.md`
- `references/animation-recipes.md`
- `references/assets-animation.md`
- `references/audio-particles.md`
- `references/character-and-equipment-art.md`
- `references/characters-brains-stategraphs.md`
- `references/combat-buffs-containers.md`
- `references/cooker-dishes.md`
- `references/core-lua-hooks.md`
- `references/dst-mod-tool.md`
- `references/entities-components.md`
- `references/items-food-plants.md`
- `references/kb-retrieval.md`
- `references/lifecycle-save.md`
- `references/networking-rpc.md`
- `references/sources-and-corrections.md`
- `references/spells-and-custom-stats.md`
- `references/tool-bootstrap.md`
- `references/ui-actions-controls.md`
- `references/worldgen-spatial.md`
- `templates/local-validation.md`
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

## 来源：`README.md`

原始 SHA-256：`435a0a08f7a6d1c10acc952700c3e83b82a1aa02bca02008a21dd70343857f69`

# dst-mod-engineering

面向《饥荒联机版》（Don't Starve Together）的中文 AI 开发技能，覆盖功能开发、代码审查、崩溃排错、联机、存档和资源制作。

**非商业使用**：允许学习、研究、非商业合作和免费制作、分享 Mod；未经另行书面授权，不得用于收费接单、付费 Mod／服务，也不得售卖或付费转发本项目。允许无权益交换的自愿打赏、赞助及免费公开教程的广告收益。完整边界见 [使用许可](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/LICENSE) 和 [常见情形](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/licensing.md)。

[![Checks](https://github.com/Zechariah0121/dst-mod-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/Zechariah0121/dst-mod-engineering/actions/workflows/ci.yml)
[![License: Non-Commercial](https://img.shields.io/badge/License-Non--Commercial-orange.svg)](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/LICENSE)

## 快速开始

| 使用方式 | 入口 |
|---|---|
| Codex、Claude Code、Cursor 等 Agent | 下载仓库，按 [接入指南](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/agent-setup.md) 安装并加载 `SKILL.md` |
| 网页 AI | 上传 [技能 ZIP](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest/download/dst-mod-engineering.skill.zip)，或使用下方专题 Markdown |
| 阅读工程知识 | [知识库索引](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-engineering-kb/INDEX.md) |
| 为 Agent 启用知识检索 | [MCP 服务接入](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-kb-service/README.md) |
| 获取全部内容 | [完整发行包](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest/download/dst-mod-engineering-full.zip)（Skill、知识库、MCP） |

[发行页](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest)提供版本说明和下载校验文件；需要尚未发行的改动时可下载 [main 分支 ZIP](https://github.com/Zechariah0121/dst-mod-engineering/archive/refs/heads/main.zip)。

不支持自动发现技能的 Agent，也可以直接使用：

> 请读取 `dst-mod-engineering/SKILL.md`，按相关专题处理我的 DST Mod 任务。先核对当前原版源码，再实现或修复；玩法取舍先确认，分别报告静态检查和实际游戏测试结果。

技能 ZIP 包含使用指南和开发辅助脚本；知识库与 MCP 服务需下载完整仓库。普通网页附件是否能解压、注册技能，取决于平台能力，详见 [网页使用指南](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/web-chat.md)。

## Skill 与知识库

Skill 负责开发流程和按需导航；知识库提供可追溯的事实、模式、反例与测试候选；可选 MCP 服务负责检索。设计、实现、审查和排错使用不同的检索重点，简单机械修改不必重复查询。

知识库 v0.1.1 包含 **64 条条目**，来自一个参考案例及限定的原版源码快照。模式和规则仍是候选，11 项游戏测试候选尚未执行。使用时仍须核对当前项目和游戏版本。具体任务示例见 [知识库使用说明](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/knowledge-integration.md)。

## 网页阅读资料

通常选择与任务相关的一份即可：

| 任务 | 下载 |
|---|---|
| 初次使用 | [入门](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-starter.md) |
| 代码审查与修复 | [代码专题](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-code-review.md) |
| 联机、存档与 UI | [联机专题](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-networking.md) |
| 贴图、动画与音频 | [资源专题](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-assets.md) |
| 世界生成 | [世界生成专题](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-worldgen.md) |
| 全部专题 | [阅读 ZIP](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest/download/web-reading.zip) · [完整 Markdown](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-full.md) |

## 开发工具

| 工具 | 用途 |
|---|---|
| `scripts/dst_zip_tool.py` | 检索游戏安装目录中的 `scripts.zip` |
| `scripts/check_api.py` | Lua 语法及组件／Replica 方法声明检查 |
| `scripts/dst_modtest.py` | Windows 隔离专服测试，记录加载与行为断言结果 |

脚本需要 Python 3.10+；语法检查器还需 `luaparser`，可用 `python -m pip install -r requirements.txt` 安装。参数通过各脚本的 `--help` 查看，操作示例及限制见 [测试与交付](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)。静态检查和专服测试不能替代真实客户端的 UI、预测、画面与音频验收。

动画与音频工具按任务选择，见 [工具安装](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md)、[动画制作](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md) 和 [音频制作](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/audio-particles.md)。

## 来源与许可

仓库自有内容采用 [自定义非商业使用许可](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/LICENSE)，不是 MIT 或 OSI 开源许可；第三方材料与历史有效 MIT 授权的边界见 [许可说明](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/licensing.md)。

知识库参考风铃（FL）的“穹”Mod，公开内容为架构分析与技术评论，不代表原作者背书，也不重新授权原 Mod。游戏、Mod 原始源码及素材未随本仓库分发，其权利仍归原权利人。资料来源见 [来源说明](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/sources-and-corrections.md)，证据与版本范围见各知识条目。

需要贡献内容或重建发布包时，阅读 [维护指南](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/maintainers.md)。


---

## 来源：`docs/knowledge-integration.md`

原始 SHA-256：`44163b50d41a67aed76230b06efaa6c6936cb2089b754df3b8e0ec45cd2f1760`

# Skill、知识库与检索服务

三个目录职责不同：根目录 `SKILL.md` 与 `references/` 保存工作策略；`dst-engineering-kb/` 保存知识；`dst-kb-service/` 只读检索，SQLite 索引位于知识库以外。知识条目不是代码模板，也不是让 Agent 无条件执行的指令。

参考案例为“小穹”v13.80，既有元数据记录作者为 FL。保留案例名称与符号用于研究归属和定位，不代表原作者背书本知识库。本仓库自行编写的工具与文档适用 [非商业使用许可](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/LICENSE)，历史有效 MIT 授权不追溯撤销；不对第三方 Mod 或 Klei 游戏源码重新授予许可，本包不包含这些原始源码与素材。

## 从任务到证据

| 实际制作问题 | 模式 | 可作为起点的条目 | 仍要确认 |
|---|---|---|---|
| 按钮消耗资源释放技能 | architect | `DECISION-NET-001`、`RULE-NET-001` | 原版 Action 是否足够、Host/远端共同校验 |
| 重连后效果重复或残留 | debug | `RULE-LIFE-001`、`ANTI-LIFE-001` | 实际任务和监听归属；相似案例不直接证明根因 |
| 自动收纳与箱子制作供料 | architect | `PATTERN-WORLD-001`、`FACT-DST-003` | 真实物品归属、查询与扣除边界、注册/注销 |
| 地面洞穴共享仓库 | architect | `RULE-SHARD-001`、`PATTERN-SHARD-001` | 写入权威、重复请求、断线恢复 |
| 自定义数值存档与 HUD | implement | `FACT-DST-001`、`DECISION-PERSIST-001` | 真实状态保存、显示重建、首次同步 |
| 两个 Mod 包装同一函数 | review | `RULE-HOOK-002`、`TEST-HOOK-002` | 加载顺序、异常恢复、撤销时不覆盖别人 |

以上 ID 可在 [索引](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-engineering-kb/INDEX.md) 查询。重要决策读取完整条目，再沿明确关系找到反例与测试；不要仅凭摘要或相关性排名作结论。

例如自动收纳任务：检索候选模式 → 读取适用/不适用条件 → 决定状态 Owner → 查当前 Container/Builder 原版链路 → 实现注册与查询 → 执行本任务能覆盖的验证。World Manager 不替代单体 Component，也不能由“减少扫描”推断所有查询都是常数复杂度。

## 覆盖与回退

当前知识集中在状态归属、联机、分片、生命周期、存档、Hook 和世界协调。Skill 的制作专题覆盖更广；动画、音效等问题应继续读取相应专题和工具契约。检索使用词语匹配，非空结果可能不相关；无匹配也不能证明整个领域不存在知识。

检测到实际 MCP 工具后主动按需使用，不把配置存在当成已连接。没有 MCP 但能读文件时，读取 `data/index.json`、相关文档或 `data/entries.json` 中指定条目，说明使用了文件读取。没有任何可访问知识时，说明 `KB unavailable` 并继续能做的源码工作。不得虚报查询或测试成功。

普通开发不会自动修改知识库。发现新证据或知识缺口时在任务报告记录，只有明确维护请求才进入知识更新与 Correction 流程。来源事实、单案例观察和建议分别看待；历史撤回 Claim 只能作为历史。

## 获取与验收

- 完整仓库包含三层；网页技能 ZIP 只包含技能与辅助资料，不包含知识库和服务。
- [服务接入](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-kb-service/README.md) 使用 Python 3.10+，不需要第三方 Python 包或 API Key。
- [知识库入口](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-engineering-kb/README.md) 说明条目的来源、证据等级和版本范围。
- 数据校验、服务回归、Agent 真正按任务自动检索、DST 实机验证是四种不同验收。


---

## 来源：`docs/licensing.md`

原始 SHA-256：`2a8bb5f84c8a68fd48b1c7a2c5f168e7f439f94a4ad0bc711f98249caad4c7c3`

# 使用许可与常见情形

本次许可变更发布于 2026-10-13，完整条款以仓库根目录的 [LICENSE](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/LICENSE) 为准。覆盖仓库自有的 Skill、脚本、知识库原创分析和 MCP 服务；第三方材料不在重新授权范围内。

| 情形 | 本次许可的处理 |
|---|---|
| 学习、研究，个人或合作制作免费 Mod | 允许 |
| 免费分享或修改本项目材料 | 允许；保留版权、许可及来源，修改版注明修改 |
| 免费作品接受不附带任何权益的自愿打赏、赞助 | 允许 |
| 免费公开的使用教程获得广告收益 | 允许；不得借此设置资料付费门槛或售卖本项目 |
| 支付通用 AI 模型或服务器费用来制作非商业 Mod | 允许；支付基础设施费用本身不是商业使用 |
| 收费接单、付费 Mod、付费解锁或收费技术服务 | 须事先获得权利人书面授权；最终 Mod 免费不豁免接单行为 |
| 售卖或付费转发 Skill／知识库，包装成收费课程、Agent 或 MCP 服务 | 须事先获得权利人书面授权 |
| 用“赞助”换提前体验、专属功能、定制开发或优先服务 | 属于权益交换，不能使用无条件打赏例外 |

## 历史版本与第三方

原项目曾按 MIT 发布。新许可不追溯撤销有效的历史授权，也不能阻止他人依原 MIT 条款继续使用已获许可的旧材料。此前已按 MIT 发布的相同内容不会因本次重新打包而失去原授权。

- [历史 MIT LICENSE](https://github.com/Zechariah0121/dst-mod-engineering/blob/ef682cb95f4b4e2171f3c2c634c88ddecefe75de/LICENSE)
- [2026-10-13 的 README 单独修改](https://github.com/Zechariah0121/dst-mod-engineering/commit/7c1f177a0632883c4c08d25956c07a939dc73d2e)：该次提交仍保留 MIT LICENSE；后续本次提交才统一许可文本与分发包。

Klei、参考 Mod 和工具作者保留各自权利。署名、研究引用或本项目许可不等于获得其商业使用授权；本项目也不代表他们背书。

## 生成代码归谁

仅因使用本 Skill，产出的 Mod 或代码不会自动归本项目所有，也不会自动整体继承本许可。实际复制的本项目片段、第三方代码和素材，仍按各自适用条款处理。使用本材料辅助收费接单等行为，仍受 LICENSE 的用途限制。

通用思想、原版 API 用法和相似代码风格，不能单独证明使用过本 Skill。许可是使用条件，不是技术防复制措施；争议中的效力与举证仍取决于具体事实和适用法律。

需要另行商业授权时，可通过 [仓库 Issues](https://github.com/Zechariah0121/dst-mod-engineering/issues) 联系权利人；提交申请或未收到回复不等于获得授权。


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

## 来源：`references/animation-recipes.md`

原始 SHA-256：`649e2bc455ab30d6e86b51bb2070405277795583b4a1ba7bf3ebe744f1551eb7`

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

历史验证仅覆盖合成小图编译、多个 atlas/sampler 输出及部分原版资源解析，**未覆盖真实大图序列或跨图集资产的客户端渲染**；详见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。按本页制作的素材仍需完成上述客户端验收。

声音制作见 [音频与粒子](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/audio-particles.md)。


---

## 来源：`references/assets-animation.md`

原始 SHA-256：`48b75f47b613a11b3e219a239a91097b6986520c6444c3de5e1e1901152fb952`

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

源码核对入口：`spear.lua`、`sword_lunarplant.lua`、`simutil.lua`、`standardcomponents.lua`、`constants.lua`，以及官方 `buildanimation.py`；按 [环境发现](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md) 定位当前版本。工具分工见 [ktools 作者说明](https://github.com/nsimplex/ktools/blob/master/README.md)，历史样本和原版 ZIP 检查范围见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。


---

## 来源：`references/audio-particles.md`

原始 SHA-256：`35e88ac3a0595c917a8e90287d66efd6d1bed1de8a4520bc1de7f84701125121`

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

本页提供制作与排错流程；新声音银行仍需编译、客户端加载和试听验收。已核验范围见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。

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

核验依据：当前 `prefabs/cane_candy_fx.lua:16-42,49-65,68-131`、`components/health.lua:590`、`components/dynamicmusic.lua` 的绑定/解绑；核验环境中的 FMOD Designer help；随工具提供的《FMOD Designer 2010》80、142、152-157、205 页；该环境中的 FSB 文件头统计。现代 FMOD Studio 文档可帮助理解概念，不能替代这些 DST 目标版本证据。


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

## 来源：`references/characters-brains-stategraphs.md`

原始 SHA-256：`18ba0f1cbd645885ea1aae4bf9db4ab779e94123e507ee4ec884909b6639775f`

# 角色、Brain 与 StateGraph

适用于角色创建、动物亲和、定制生物、形态变化与动作状态排错。以 2026-09-27 核验环境的原版脚本为基线，详见 [environment-tools.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)。美术、网络变量与客户端界面细节按技能入口中的对应专题展开。

角色外观和选人资源接入见 [角色与装备美术](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/character-and-equipment-art.md)；魔力/能量条与恢复流程见 [法术与自定义数值](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/spells-and-custom-stats.md)。

## 角色工厂与生命周期

注册 `PrefabFiles` 和 `AddModCharacter(name, gender, modes)`，角色 Prefab 使用 `require("prefabs/player_common")` 返回的工厂。性别参数是语法/代词分类；`PLURAL` 是复数类别，不是“双性”，`SECRET` 也不是原版建议的性别枚举。

```lua
local MakePlayerCharacter = require("prefabs/player_common")

local function common_postinit(inst)
    inst:AddTag("my_mod_character")
    -- 双端需要的字段/netvar 在这里定义。
end

local function master_postinit(inst)
    inst.soundsname = "wilson"
    -- 在这里配置权威数值、专属组件与服务端事件。
end

return MakePlayerCharacter("my_mod_character", nil, nil,
    common_postinit, master_postinit)
```

这只是工厂用法，不是包含选人资源、造型、台词和完整玩法的成品角色。复用现有模组时先查已有初始化代码，避免重复覆盖。

- 工厂在 `SetPristine` 前调用 common，客机早退后才调用 master。玩家默认依赖 `wilson` bank 与通用玩家组件，通常使用 `SGwilson` / `SGwilson_client`，不是每个角色名对应一个 SG。
- 工厂默认尝试使用角色名 build，后续 skinner 负责皮肤/造型。build 与角色名相同是便利约定，**不是引擎要求二者永远相等**。自定义映射要一并核对调试生成、换肤、幽灵和形态还原。
- 在 master 内设置 `inst.OnSave` 等回调时，工厂会保存为 `_OnSave` 等再包入玩家默认流程；在后续 PostInit 直接覆盖则必须保留当前函数。不要为自定义资源丢掉原版玩家存档逻辑。
- 选人菜单展示的三维读取 `TUNING[string.upper(character .. "_HEALTH")]` 等，与出生后的组件值是两条配置链，缺一边就可能出现问号或数值不一致。
- `AddPlayerPostInit` 不代表本地玩家已激活、HUD 已创建或已进入正常人形。客户端表现要处理首次进入、幽灵进入、复活、重连与分片切换；服务端 `makeplayerghost` / `respawnfromghost` 事件不会自动传到远程 HUD。

幽灵 UI 应接实际客户端状态链：原版 `player_classified.isghostmode` dirty → 玩家 `SetGhostMode` → HUD / `StatusDisplays:SetGhostMode`。初始化主动刷新一次，并在真实状态变更时刷新；不能用“dirty没变化”作为所有 HUD 都必须每帧轮询的理由。

## 台词与角色专属数值

台词结构按消费者需要填写：普通条目是字符串；分支条目用原版期待的状态键；随机候选是数组。`ANNOUNCE_X = { ANNOUNCE_X = "..." }` 并不等价于 `ANNOUNCE_X = "..."`，无 modifier 时消费者查 `GENERIC` 或数组，写错会静默回退。

注册 `STRINGS.CHARACTERS.MY_MOD_CHARACTER` 后保留需要的结构。`GetString` 有 GENERIC fallback，但不是所有直接读取字符串表的代码都经过它；不把“必须抄整份 Wilson 文件”和“只写任意几个键就绝对够用”当通用规则。原版语气和翻译查当前 `speech_*.lua` 与对应语言 PO，不冻结角色数量。

自定义资源：先确定取值范围、精度、上限变化、耗费失败规则、死亡/复活、保存重启。再选择组件 + replica/netvar + HUD；Class 属性代理是一种同步入口，也可用集中 setter，只要所有写入路径一致。普通 table 赋值本身不联网。死亡时是否保留增益、离线是否继续计时都是玩法决定。

## 从行为到动作结果的调用链

```text
Brain 的行为节点选择目标
  → BufferedAction(doer, target, action, invobject, pos, ...)
  → locomotor/实体接收并推进动作
  → SG ActionHandler 选择状态
  → onenter / timeline / event 控制时机
  → PerformBufferedAction → BufferedAction:Do → action.fn
```

`invobject` 是参与动作的物品，不是泛指代理对象。StateGraph 是状态机实现，除了动画还负责输入限制、时序、动作执行、物理和网络预测；“SG只管动画、Brain加SG才算状态机”会误导排错。

对玩家动作，还要追客户端 action picker、预览 BufferedAction、`SGwilson_client`、RPC/远程动作发送和服务端校验。客户端提前 `ClearBufferedAction` 可能令后续预览发送没有动作；服务端施法逻辑成功不能证明远程玩家能触发它。最终资源扣费与效果只由权威端结算一次。

## StateGraph 修改要点

- `inst:SetStateGraph("SGwilson")` 使用加载文件名；`AddStategraphState("wilson", state)` 使用返回的 `StateGraph("wilson", ...)` 的内部 name。客机常是 `wilson_client`。逐一查看实际返回值，不遍历角色名猜 SG 名。
- SG 定义表会被共用；通过 `inst` 的 prefab/tag/组件限定新增分支，未命中分支返回原 handler 结果。加独立动作使用 `AddStategraphActionHandler`；改现有动作先检查并包装已有 `.deststate`，避免覆盖其他武器分支。
- `TimeEvent(time, fn)` 的时间单位是秒，通常 `TimeEvent(6 * FRAMES, fn)`；`FrameEvent(6, fn)` 才直接接帧数。`SetTimeout` 也是时间，不是自动触发所有 timeline 的终点。
- `busy` 是被调用方检查的状态标签，**不是不可打断保证**。死亡、冻结、传送或直接 `GoToState` 仍可能切走；自定义状态必须有中断清理。
- `sg.statemem` 每次切状态清空，`sg.mem` 跨状态保留。临时无敌、碰撞、移动速度、监听、持续 FX 要在 `onexit` 对称清理，并考虑是否向下一状态有意交接。
- SG 状态事件和全局事件可能都执行；当前状态 handler 返回真才阻止继续走 SG 全局 handler。不要仅用“已定义同名事件”假设覆盖成功。
- `animover` 适合单次动画完成，循环动画或排队动画需核对正确事件与退出条件；动画存在性查当前 bank，不能从另一生物的动画名推断。

形态系统先定义权威状态和明确转移，再绑定动画。进入中途取消、受击、死亡、读档恢复都必须有路径；状态退出代码恢复外观前检查当前形态，避免已经还原后又被旧状态写回 boss build。保存残血形态时处理组件加载顺序，不能把 `SetMaxHealth` 的满血副作用当作读档成功。

## Brain：保留已有行为与处理重建

先选与需求接近的现有 brain，定位新增行为在逃跑、追击、回家、觅食、闲逛之间的优先级。读当前 `behaviourtree.lua`，不要套用其他引擎同名节点的语义：

| 节点 | 对实现有用的区别 |
|---|---|
| `PriorityNode` | 按子节点顺序评估，选成功或运行中的节点，并周期重评；不是概率优先级 |
| `SequenceNode` / `SelectorNode` | 分别按成功继续/失败继续推进，RUNNING 保留进行中的子行为 |
| `WhileNode` | 用并行条件节点持续约束子行为，可因条件变化而中断 |
| `IfNode` | 进入时通过条件后继续子行为，不在子行为运行途中重查该条件 |
| `DoAction` | 负责发起并观察 BufferedAction 的成功失败；先确认动作在该生物 SG 有 handler |

修改原版生物优先评估 `AddBrainPostInit` 的局部修改；全复制 brain 是需要维护官方更新的分叉，只有替换整套 AI 才这样做。教程自定义青蛙还全局修改了 `frog` SG，影响所有使用它的青蛙；仅定制一个物种时选择条件分支或专有 SG。

`Brain:_Start_Internal` 每次启动先调用 `OnStart`，再执行 `modpostinitfns`。`StopBrain` / `RestartBrain` 会重走这条链，休眠唤醒还可能换一个 brain 实例。因此：

- 插入节点或包现有节点时对**当前树根/当前节点**做幂等标记，不用一个永不清除的实例布尔值跳过所有未来重建。
- 不假定 `children[3]` 永远是某个行为；读当前结构，并通过节点类型、名称、位置上下文验证目标唯一且正确。
- 暂停/恢复自己的 AI 干预可使用成对的 `StopBrain(reason)` / `RestartBrain(reason)`，保留同一个有命名空间的 reason，避免与其他停止原因相互解除。
- 测试要保证实体醒着且在可活动地形；休眠实体没动不能证明 AI 补丁失败。至少验证正常启动、停止重启、休眠唤醒和目标移除。

## 原版检索入口与验收

- `prefabs/player_common.lua:MakePlayerCharacter`、`prefabs/player_common_extensions.lua`、`components/skinner.lua`：角色初始化、存档包装、幽灵与造型。
- `widgets/redux/characterbio.lua` → `widgets/redux/templates.lua:MakeUIStatusBadge`、`widgets/statusdisplays.lua:SetGhostMode`、`prefabs/player_classified.lua:OnGhostModeDirty`：菜单数值与客户端生命周期。
- `stringutil.lua:getmodifiedstring` / `GetString` / `GetDescription`：台词真实选择规则。
- `stategraph.lua:StateGraph` / `StateGraphInstance:HandleEvent` / `GoToState`，`stategraphs/SGwilson.lua`、`SGwilson_client.lua`：注册名、分支、状态退出与预测。
- `entityscript.lua:PerformBufferedAction` / `PerformPreviewBufferedAction`，`bufferedaction.lua:Do`，`behaviours/doaction.lua`：动作结果是否真的执行。
- `brain.lua:_Start_Internal`、`entityscript.lua:StopBrain` / `RestartBrain` / `SetBrain`、`behaviourtree.lua:PriorityNode:Visit`：树重建与优先级。
- 服务端自动测试覆盖动作结算、形态中断、存档与重建；真实客户端另验输入、动画、幽灵 HUD、远程预测和双人互相观察。未运行的层级在报告中明确列出。


---

## 来源：`references/combat-buffs-containers.md`

原始 SHA-256：`e56f20c3525c0ec546b8835bfe5ab281297498286057e5110265664188dacf44`

# 战斗、Buff、容器与冷却

适用：范围攻击、位面伤害、击退、附加属性、料理 Buff、物品冷却和自定义容器。数值与玩法先按项目约定；本篇提供机制选择和核验路径，不替项目决定倍率/半径/死亡政策。

## 范围伤害和位面伤害

原版已有 `combat:DoAreaAttack(target, range, weapon, validfn, stimuli, excludetags, onlyontarget)`。它排除普通范围分支中的主目标和攻击者，检查目标、发 `onareaattackother`、通过 `CalcDamage` 同时取得普通及特殊伤害并调用 `GetAttacked`。现成路径符合需求时优先复用；自定义形状须保留完整结算链。

教程火腿棒例子直接替换 `weapon.onattack`、硬编码满新鲜伤害且遗漏特殊伤害；不能当可直接复用模板。叠加效果应保存原回调并按正确签名调用，检查空 target、目标有效性和组件。`IsValidTarget` 也不自动表达设计上的“不伤盟友/随从/同类”；将 PvP、阵营、随从、主目标重复伤害明确列入筛选。

自定义攻击不要为省事直接 `health:DoDelta(-damage)` 绕过护甲、位面防御、受击事件、仇恨和击杀归属。`planardamage` 提供基础值和来源倍率/加值，不提供 `DoDelta`；设置 weapon/projectile 的 planardamage，由 `SpDamageUtil` 与 combat 结算。已有 projectile/aoeweapon 命中流程后又手动伤害可能重复扣血。

`damagetypebonus:AddBonus(tag, source, multiplier, key)` 的参数是乘数：1 无增伤，2 才表示增加 100%。目标 tag 须查 prefab 的真实标签，不把显示阵营名或另一个 Mod 的 tag 当原版通用规范。位面伤害仍会经过位面防御，不能描述成无条件真实伤害。

冲刺优先查当前 `prefabs/spear_wathgrithr.lua`、`components/aoeweapon_lunge.lua` 及基类。reticule 的回调配置位置按原版 `aoetargeting.reticule` 核对；`aoespell` 回调顺序为 item、doer、pos。命中回调只补额外行为，不未经核对再次结算完整伤害。

## 击退、睡眠与飞行不是单行开关

`target:PushEvent("knockback", {knocker=source, radius=..., strengthmult=...})` 需要目标状态机支持。radius 参与按距离计算推力，不是会搜索所有目标的 AOE 半径；不要照抄 200。保留攻击原回调，按服务端与目标类型添加，验重型、骑乘、平台、死亡和碰撞。

`heavybody` 的行为取决于对应状态机，不能承诺完全免疫。仅屏蔽 `yawn` 不会覆盖直接 `grogginess:AddGrogginess`、`knockedout` 和其他睡眠路径。当前 grogginess 有按来源免疫接口，优先查 `AddImmunitySource/RemoveImmunitySource`；仍需定义要免疫的是昏睡、哈欠、减速还是所有睡眠。不要为“霸体”全局吞掉角色所有 SG 事件。

教程飞行只提供旧实现思路：强行改 y 速度、清碰撞、把 drownable.enabled 写 false，缺保存/死亡/取消/睡眠清理，延迟云可能在落地后生成，客户端预测也未证明。保留作审查反例；新机制先查原版可比形态、状态/碰撞/骑乘与溺水接口，明确跨地形能力，完整列出退出恢复及网络策略后再实现。纯视觉悬浮通常用动画/FX，不必改变玩法物理。

## 附近玩家触发的悬浮

天体宝球 `moonrockseed` 的动画/光效可作视觉参考，但 `prototyper` 承担科技站选择；即使 trees 为空也可能占据玩家当前科技站位置，不适合为了纯装饰随意添加。`builder:EvaluateTechTrees` 只查当前研究距离，旧文“全图最近”是错误表述。

纯靠近/远离效果先查 `playerprox` 的 AnyPlayer 模式和 `SetDist(near, far)`，利用迟滞避免边缘抖动；有复杂目标筛选再做受控周期查询，避免每件物品每帧扫描。捡起/落地事件按真实 inventoryitem 推送名核对，`ondropped` 不是被捡起。光效淡入淡出任务仅在过渡时运行，达目标即停；视觉状态按客户端可见性设计。

## 可刷新的 Buff

优先使用 `debuffable:AddDebuff(name, prefab, data)` + Buff prefab 的 `debuff`/`timer`。同 name 再施加调用 Extend，附加/延期/解除分别为 `SetAttachedFn/SetExtendedFn/SetDetachedFn`。普通食物 Buff 可以非网络服务端 prefab；需要客户端夜视/滤镜/标志时，另设计复制状态或网络表现实体，不能只设置服务器 playervision。

每个 Buff 写清：来源标识、应用和移除、重复是叠层还是刷新、到期、死亡、despawn、重启、外部删除。原版 foodbuffs 默认监听 death 停止，仅是其规则。用户要求死亡继续计时就调整本机制所有出口，不能只删除一个地方又在 ghost 回调重置。

用来源列表维护属性，例子（运行于已验证 target 的服务端）：

```lua
-- source 是本 Buff 实体，key 为本机制私有键；MULT 由设计提供。
target.components.combat.externaldamagemultipliers:SetModifier(source, MULT, "my_buff")
-- 正常解除及必要的异常出口：
target.components.combat.externaldamagemultipliers:RemoveModifier(source, "my_buff")
```

实体 source 在其移除时有 SourceModifierList 自动清理，但提前解除仍应主动移除；字符串 source 没有实体 onremove 自动清理。速度用 `SetExternalSpeedMultiplier/RemoveExternalSpeedMultiplier`。不把当前值除回倍率、直接改回 1 或清空整个列表。

夜视用 `playervision:PushForcedNightVision(source, ...)/PopForcedNightVision(source)`；在本地玩家建立和网络目标可用后施加，目标改变时先撤旧来源，实例被外部删除时也清理。显示保护 goggles 等不同系统可能是共享标量，不能用单个布尔擅自覆盖其他 Mod；能力已是多来源 API 时直接复用。

计时器存在不代表效果仍存在：外部移除网络 Buff 后，宿主残留 task/引用可能使再次施加只刷新到期而不重新应用。用幂等 Ensure/Apply 路径同时核查实体、来源与任务，或在其 onremove 清空缓存。重连/初次复制不能仅等 dirty。

## 冷却组件

使用游戏自带 `rechargeable`，不携带教程的同名旧组件覆盖原版。`Discharge(seconds)` 开始充能，`IsCharged()` 校验当前状态；需要时用 `SetOnChargedFn/SetOnDischargedFn` 配合 aoetargeting 显示。

背包进度显示不是禁止使用。服务端行为执行前必须检查 charged，失败不能刷新/扣费；成功后再放电。包装 spellcaster/spellfn 保留全部参数与返回值，不能不管原法术失败就进入冷却。组件原有 OnSave/OnLoad 保存剩余进度；需测试旧档、读档重复初始化和特殊冷却政策。

## 容器

在双方加载的代码中注册私有 `containers.params[widget_name]`，复用合适的原版 UI，明确 numslots/slotpos、type、itemtestfn。服务端添加 container、`WidgetSetup`；客户端确保 Replica 使用相同配置，先查看 `container_replica` 是否按 prefab 自动初始化，只有名称不同/特殊生命周期时按原版 OnEntityReplicated 模式补一次，不能一概要求重复设置。

`openlimit` 控制**同一容器实例同时有多少打开者**，不是全世界同类型只能打开几个。Widget 的 pos 是 UI 布局参数，不是容器实体世界坐标。参数在 require 后追加时，确认 MAXITEMSLOTS 对该容器槽数足够；不缩小其他 Mod 已扩大的值。

权限在服务端检查，itemtestfn 应兼容实际调用方数据；防自嵌套/循环嵌套并确认装备容器、打包容器和物品归还路径。给宠物加容器不能只监听 death：召回、收起、变身、despawn、移除、断线、重启分别决定掉落/转移/保存，防物品丢失或复制。不要擅改原版同名 params 影响其他实体。

`stackable.maxsize` 是主组件属性（有 setter），不是主组件 `SetMaxSize` 方法。当前 Replica 的最大堆叠档位表与数量编码是两个限制：档位使用 TUNING 五项，实际数量用两个 6-bit 字段，不能把最大默认档位 120 说成网络数量上限。任意 maxsize 仍可能因档位查不到而崩。不要将“全局占用 code=5”作为安全通用补丁，其他 Mod 可能使用同一编码；优先使用原版档位，自定义协议需双方一致及组合兼容验证。

## Mod 兼容检测

按用户指定的稳定 Mod ID 精确比较适当的启用列表/当前 ModManager 状态；显示名可能变化，本地目录与 workshop ID 也不同。教程 `string.match(name)` 同时匹配目录和显示名会出现 Lua 模式注入/子串误判，不能用作能力判定。优先检查所需 API 能力，只有具体已知冲突才按 ID 走适配；检查时机要在目标 Mod 完成加载之后。

## 当前源码检索入口与验证

- `components/combat.lua:CalcDamage/DoAreaAttack/GetAttacked`；`components/aoeweapon_base.lua:OnHit`；`components/weapon.lua:GetDamage`；`components/spdamageutil.lua`。
- `components/planardamage.lua`；`components/damagetypebonus.lua:AddBonus/GetBonus`：数值语义。
- `stategraphs/SGwilson.lua:knockback/knockedout/yawn`；`components/grogginess.lua:AddGrogginess/AddImmunitySource/RemoveImmunitySource`。
- `prefabs/foodbuffs.lua:150-208`；`components/debuffable.lua:95-149`；`util/sourcemodifierlist.lua:64-121`；`components/playervision.lua:226-261`。
- `components/rechargeable.lua:108-174`；`components/container.lua:86-96,728-736`；`components/container_replica.lua`；`containers.lua:widgetsetup`。
- `components/stackable_replica.lua:1-9,24-35,47-63,98-111`；`modindex.lua:GetModsToLoad/IsModEnabled`；`mods.lua:GetEnabledModNames`。
- `prefabs/moonrockseed.lua`；`components/builder.lua:235-301`；`components/playerprox.lua:44-59,165-180`：科技选择与纯邻近触发。

伤害测试需比较普通/位面/护甲/PvP、主目标不重复、范围边缘和叠加来源；Buff 测重复/到期/移除/死亡/读档；容器测多人打开、转移、召回与磁盘重启。网络展示、真实玩家输入和第三方 Mod 组合另做客户端验收。


---

## 来源：`references/cooker-dishes.md`

原始 SHA-256：`6e6c74d0e0753f84985c3d57cd7834607ec65bbceec2d0ad63d3a812e9cfd004`

# 新增与维护锅料理

用于完成一道料理从设计、注册、调味、图像到验证的全过程。先读当前 `cooking.lua`、相近配方和 `prefabs/preparedfoods.lua`；料理判定基础见 [物品与料理](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/items-food-plants.md)，实体骨架见 [Prefab 与组件](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/entities-components.md)。本页不规定料理数值、画风、项目目录或角色台词数量。

## 1. 建立料理合同与变更清单

一次确认未决定的项目：内部名称与显示名；允许的锅；原料数量及生/熟/干替代；优先级与同档竞争；三维、食物主/副类型、特殊食用效果；烹饪和腐烂时间；是否支持调味；语言与图像表现。已有明确需求不重复询问。

先列正例、反例和应保留的竞争配方，分别在普通锅与便携锅判断。`names` 使用 `cooking.lua` 规范化后的食材名，`tags` 是累计值；具体食材个数与标签值不是同一个条件。未出现的字段可能为 nil。`AddIngredientValues` 会替换已有食材标签，不能为了新料理顺手清掉原版属性。

盘点项目实际模块，不要求固定文件名或调味模块布局。项目自定义的配方包装函数、料理数据表、图集分组与台词表**不是原版公共接口**；先读实际定义、调用方和初始化顺序，确认最终如何接入原版 `AddCookerRecipe` 等接口，不能搬名称就假定可用。

尽量以一份已确认的数据定义基础料理，供配方和 prefab 构造读取，再派生调味数据。既有项目必须多表维护时，逐字段核对并记录映射，避免只改配方提示而没有改变实体数值。生成变体时复制所需嵌套表，避免意外修改基础数据。

## 2. 配方注册与实际消费者

在 Mod 环境中调用 `AddCookerRecipe(cooker_name, recipe)`。这个包装已传入 mod 标记；不要绕过它，把料理伪装成官方食物。按需求分别注册 `cookpot`、`portablecookpot` 等真实锅名；是否参与 `archive_cookpot` 需明确。注册配方不会替你创建产品 prefab。

| 数据 | 必须核对的行为 |
|---|---|
| `name` | 与实际注册的产品 prefab 对应；只有项目 helper 明确处理时，表键才能代替此字段 |
| `test(cooker, names, tags)` | 返回此配方是否进入候选；读懂原料别名、缺失字段、准确数量和排除条件 |
| `priority`、`weight` | 先保留最高 priority，再按 weight 抽取；明确给正数 weight，不能靠缺省分支兜底 |
| `cooktime` | 是 `TUNING.BASE_COOK_TIME` 的倍率，实际还乘锅的 `cooktimemult`，不是直接秒数 |
| `perishtime` | 配方影响烹饪的新鲜度计算和锅内变质；实体的 perishable 也必须读取相应设计 |
| `cookpot_perishtime` | 锅中成品变质时间的可选覆盖；不自动改变取出后实体的保鲜时长 |
| `health`、`hunger`、`sanity`、`foodtype` 等 | 配方与图鉴数据不会自动写入任意自定义 prefab，需由该 prefab 构造实际应用 |
| `overridebuild`、`overridesymbolname`、`potlevel` | 供锅内成品显示；独立检查拾取后实体的 bank/build/symbol，不能以锅内显示正常代替 |
| `cookbook_atlas`、`cookbook_tex`、`no_cookbook` | 按实际图鉴需求配置；默认图像名为产品名加 `.tex`，图集可回退库存注册 |

原版数据文件最后会补齐 `name`、`weight` 等字段；`AddCookerRecipe` 本身没有替任意 Mod 配方做同样的补齐。当前抽取分支直接使用 `candidate.weight`，省略它可能运行时报错。

腐烂时长按已批准的天数使用当前 `TUNING.TOTAL_DAY_TIME` 或适当的 TUNING 常量，不继承其他项目的天数与硬编码日长。当前 `FOODTYPE` 不只有 VEGGIE/MEAT/GOODIES，也没有 FISH；食材 `fish` 标签不等于可食组件枚举。怪物副类型是否保留属于饮食设计，不能为消除某角色限制擅自改掉。

## 3. 产品实体与资源接线

以当前 `prefabs/preparedfoods.lua` 的构造顺序为参照：公共动画、必要 tag、网络与浮水设置 → `SetPristine()` → 主客端分离 → 权威端的 edible、inventoryitem、stackable、perishable 等。实际用途决定是否保留可燃、交易、诱饵等原版行为。`MakePreparedFood` 是该文件内部局部函数，不能当成可从 Mod 直接调用的导出接口。

`PrefabFiles` 填实际 prefab 模块路径；一个模块也可返回多个 prefab，不必强制每道菜及每种调味各建一个文件。声明并加载新增动画、图集与 TEX；沿引用检查依赖，不机械要求所有资源同时在 `modmain.Assets` 与 prefab 中重复声明。

**独立图集是资源组织选择，不是新增料理的引擎要求。** 保留“不要破坏已发布共享资源”的经验：先识别该资源的使用者，保留可重编源工程；选择扩展共享 build 或新增 build 后，验证受影响的旧菜。只有项目明确冻结共享包时才保留该项目限制。

- 复用原版 `cook_pot_food` 的 bank/idle 与换符号路径时，新资源可只提供 build 和图集；不强行制造 `anim.bin`。如果料理确实有独立动作，则检查相应 bank、animation 与完整依赖。
- 普通锅/便携锅使用 `recipe.overridebuild` 和 `recipe.overridesymbolname or product` 覆盖 `swap_cooked`。用自定义 symbol 名时，这个字段只解决锅的调用；自己 prefab 的 `OverrideSymbol` 仍要对应真实符号。原版食物构造默认使用 `basename or name`，没有自动消费该覆盖字段。
- 库存图标链条为 TEX/XML Element → `RegisterInventoryItemAtlas(atlas, image_with_tex)` → inventoryitem/replica 查询；XML Texture 文件名不必等于 Element 名。图鉴默认也查询此注册，避免只给实例设置 atlas 而遗漏静态图鉴路径。
- 库存与地面源图的画布、内容范围、缩放和颜色倍率按目标资源与美术需求确定，不继承其他项目的固定参数。保持 alpha，不能直接按白色阈值删除白色主体与高光。

图像处理、当前工具发现、DMT 预览和 ZIP 校验沿 [图像与动画](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/assets-animation.md)、[DMT 工作流](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/dst-mod-tool.md)、[工具安装](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/tool-bootstrap.md) 执行。没有强制的 ComfyUI 模型、端口或出图后处理流水线。官方编译器报缺少 `animation.xml` 时，应定位输入工程、导出日志与当前工具契约；旧文档“第一次故意失败→手写固定矩阵 XML→再编译”的补丁不作为通用流程。也不要为了改变时间戳或压缩算法无条件重写已有效的 ZIP。

## 4. 调味是单独的完整链路

需要支持调味时，同时完成：调味站接受食物 → 变体配方 → 变体 prefab → 食用效果 → 图像和名称。只添加 `preparedfood` tag 不足以完成这条链；当前调味站以该 tag 和非 `spicedfood` 判断基础菜准入。

对照 `spicedfoods.lua` 与 `prefabs/preparedfoods.lua` 的分工：

1. 为所支持的香料派生变体数据，包含独立 `name`、基础菜 `basename`、香料 `spice` 与判定；注册到 `portablespicer`，并确保产品 prefab 已存在。默认原版生成循环仅处理其列出的基础表，不会自动扫描任意 Mod 菜。
2. 保留基础菜数值、食用回调、依赖和图像引用，再按相应香料语义叠加。蒜/糖/辣椒的 buff、辣椒温度变化及盐的读取链以当前原版为准；不能把所有香料都当成直接乘三维，也不能用香料回调覆盖基础菜效果。
3. 变体沿原版添加 `spicedfood`，设置 edible 的 `spice`，使用基础菜标识处理检查描述和食谱记录。需要餐桌等显示兼容时同时追踪 `food_basename`、`food_symbol_build` 的消费者。
4. 图像通常复用基础菜库存图作为 `inv_image_bg`，叠加香料图标；地面表现复用 `plate_food`、`spices` 和基础菜符号。注册基础图集并在两端检查，不能为每个变体盲目复制一份相同 TEX。
5. 名称沿原版香料名称模板组合基础菜显示名；验证各语言的组合结果和基础菜台词回退。

`GenerateSpicedFoods` 虽在原版模块中定义，但会写入该模块持有的全局调味结果表，且生成过程带官方数据假设；它不是 `modutil` 暴露的独立注册工厂。读清副作用后再决定项目接入方式，不靠改原版表、全局函数或硬编码“料理总数”完成新增。

## 5. 名称、描述与语言

- 显示名使用 `STRINGS.NAMES[upper_prefab]`。
- 检查台词使用 `STRINGS.CHARACTERS.<角色表>.DESCRIBE[upper_prefab]`，默认回退 `GENERIC`。`STRINGS.DESCRIBE` 不是这条原版检查链的入口；若旧项目通过 helper 转写它，要保留实际转写证据。
- `STRINGS.RECIPE_DESC` 服务制作配方说明；只有锅料理并不因此必须新增制作菜单描述。本篇“图鉴”指食谱图鉴（Cookbook）；先确认项目所指系统，若还要求 Scrapbook，另查其注册与发现链，不能把食谱图鉴接通当作所有图鉴都已支持。图鉴消费的数据应沿其 UI 查证。
- 2026-09-27 基线中 `DST_CHARACTERLIST` 有 19 项（含隐藏 `wonkey`），而 `STRINGS.CHARACTERS` 有 17 个基础台词表（GENERIC 加 16 专属）。GENERIC 来自 Wilson 台词，Wes 走哑剧特殊处理；**台词表项数不是角色总数**。
- 按当前版本的已加载台词表、项目支持范围和实际语言补齐。不要为凑固定数量造不存在的表，不覆盖第三方角色自己的台词；补缺失项时保留已有值。中英双语是支持范围选择，不能仅因旧案例写过就改动项目语言策略。

## 6. 按链路验证并交付

| 层次 | 本次改菜后需要证明的事项 |
|---|---|
| 静态 | Lua 可解析；调用与字段真实存在；所有配方产品可注册；基础/调味数据一致；名称、XML、图像、build/symbol 引用完整 |
| 判定与服务端 | 各锅的正反例、边界食材数量和优先级竞争；同档候选/权重符合设计；真正烹饪、取出、食用、堆叠、腐烂与保存重载 |
| 调味 | 每种承诺支持的香料都能产出实体；基础效果和香料效果各按原版链结算；调味后不会继续作为未调味食物重复进入 |
| 客户端 | 主机与真实远端看到锅内成品、地面、库存、图鉴、名称与台词；有相关行为时检查浮水、餐桌和饮食限制 |
| 发布与同步 | 比较已授权的源码/运行副本，保留用户改动并逐文件核对哈希；版本与变更说明按项目发布策略更新 |

概率判定的测试检查候选与权重本身，单次抽到预期菜不能证明同档竞争正确。语法检查、构造 prefab 成功或无头运行都不能代替客户端画面与远端图鉴验收。完整命令和证据分级见 [测试与交付](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)。

同步目标由当前项目与用户授权确定；不预设固定三份目录，不默认覆盖 Workshop 下载副本。交付列出料理合同、改动文件、资源、实际同步目标、验证证据和未验边界，审查结论按项目约定写 `.txt`。没有发生实际发布时，不声称已经更新玩家订阅内容。

## 核验依据

以下为 2026-09-27 当前安装版源码定位；相应文件已逐字节核对安装包，基线见 [环境与源码](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)。后续版本仍需重查定义与消费者。

| 主题 | 源码入口 |
|---|---|
| 配方注册、食材别名、候选 | `modutil.lua:636-653`；`cooking.lua:9-29,46-68,178-228,238-287`；`preparedfoods.lua:1098-1104` |
| 时间、新鲜度、保存与产出 | `components/stewer.lua:75-99,130-177,203-261,276`；`tuning.lua` 的 `BASE_COOK_TIME` / `TOTAL_DAY_TIME` |
| prefab 与调味 | `prefabs/preparedfoods.lua:7-179`；`spicedfoods.lua:17-83`；`containers.lua:425-429` |
| 香料与基础食用效果 | `components/edible.lua:88-142,184-197`；`tuning.lua` 的 `SPICE_MULTIPLIERS`；`prefabs/player_common_extensions.lua:919` |
| 锅内符号、调味站符号 | `prefabs/cookpot.lua:105-125`；`prefabs/portablecookpot.lua:120-139`；`prefabs/portablespicer.lua:135-156` |
| 图集与图鉴 | `simutil.lua:658-699`；`modutil.lua:954-957`；`widgets/redux/cookbookpage_crockpot.lua:497-522` |
| 台词与角色范围 | `strings.lua:15579-15598`；`stringutil.lua:364-413`；`constants.lua:442-463,2022-2043` |

上述依据为源码核验；新增料理仍需完成美术编译、配方产出和客户端表现测试。


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

## 来源：`references/dst-mod-tool.md`

原始 SHA-256：`500c05f3cb84d7851266ca0737dbcca93ddbdd3e2195bad1bd262de66a189926`

# DST Mod Tool：文档编辑、脚本接口与视觉验收

这是 DMT 的 Lua 脚本工作流参考页，适用于提供下述 `script --help` 接口的版本。先读取已安装程序的帮助，核对 API、参数和支持格式后再执行示例。

适用：`.dmt` 工作区、SCML/ZIP 资源导入、符号和动作批量编辑、PNG/GIF 预览。接口说明不代表各格式导入、导出或编译均已实测；资源加载与联机效果仍需在游戏中验收。历史接口核对范围见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。

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

## 来源：`references/items-food-plants.md`

原始 SHA-256：`52dc5f24f5c5b94d03089837d69094d1e246564e0541053cda32af92262415be`

# 物品、武器、料理与植物

用于修改物品机制、修复菜单、制作配方、锅料理或生长/种植。先读当前相近 prefab，再追组件和调用端。此页片段用于说明接口，不是含资产、数值、网络声明的完整 prefab。

新增独立锅料理的配方、调味变体、图标与台词交付流程见 [料理制作](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/cooker-dishes.md)。

## 物品与武器的实施顺序

1. 从最接近的原版物品确定：手持/穿戴槽、攻击类型、耐久类型、破损后删除还是保留、拾取堆叠、沉水/漂浮、资源名。
2. 公共区建立 Network、动画、客户端必要 tag/数据和浮水；`SetPristine()` 后分离服务端组件。完整边界见 `entities-components.md`。
3. 服务端用 `weapon`、`finiteuses`/`fueled`、`equippable` 等已有组件实现；`SetMaxUses` 设置上限，`SetUses` 设置当前值，二者不是同一个操作。
4. 回调把装备者作为明确参数处理；数值修改用可撤销的 source/key，不能覆盖其它装备的全局倍率。卸下、中断、死亡、存读档都需恢复一致。
5. 查明伤害入口和耐久消耗点，再决定是否需要自定义动作/SG；已有 `weapon`/`projectile` 能实现时不额外手动扣血。

`damagetypebonus:AddBonus(tag, source, multiplier, key)` 的第三参是乘数。`1.1` 表示增加 10%，`0.1` 表示原伤害的 10%，`1` 是不变。位面伤害走特殊伤害和位面防御链，不能表述为无条件忽略一切防御。使用 `planardamage:SetBaseDamage`/`AddBonus`/`AddMultiplier`，按数值需求选择，不猜对称 API 名。

`projectile.has_damage_set` 控制某些武器作为 owner 的情况下使用投射物自身 weapon，**不是防止重复伤害的开关**。`Projectile:Hit` 已会经 `combat:DoAttack` 攻击；自定义 `onhit` 再手工攻击可能重复结算。弧线落点用 `complexprojectile` 等相近原版；Physics 连续飞行和任务位移按命中语义选择，不能仅因旧 mod 用哪种便判优劣。

自定义投掷动作要完成“客户端选动作 → 发送目标/落点 → 客户端预览 SG → 服务端 SG → action.fn/发射 → 命中与移除”全链。`BufferedAction.pos` 是 `DynamicPosition`，用 `GetActionPoint()` 取得世界落点；`canforce` 涉及强制动作和范围处理，**不是保证坐标同步的必填开关**。当前服务端某些 canforce 分支还会重写动作点。旧 throw-chain 示例未给 `_my_target` 赋值，不能当完整模板。只在权威端发射和扣费，声音/画面同步逐个按所选实体与实际路径验证，不把“所有 SoundEmitter 都不跨端”当结论。玩家动作注册/中断参见 `characters-brains-stategraphs.md`。

## 修复机制：先选原版合同，再验证菜单

| 需求 | 当前入口 | 应检查的边界 |
|---|---|---|
| 按材料数值回复工作量/生命/新鲜度/耐久 | `repairable` + `repairer` | `MATERIALS`、材料 tag、可修状态 tag、服务端再次验证 |
| 原版套件式修满，破损保留并修复 | `MakeForgeRepairable` + `forgerepair` | `FORGEMATERIALS`、破损/修复回调、初始化/读档后的状态 |
| 赠送材料触发独特效果 | `trader` + 原版 GIVE 或限定的自定义动作 | 接受测试、消费数量、拥有者权限、失败原因 |

当前 forge 明确支持 `finiteuses`：`finiteuses` 的属性钩子更新 `forgerepairable`，`forgerepair:OnRepair` 调用 `finiteuses:SetPercent(1)`；原版 `sword_lunarplant` 和 `voidcloth_scythe` 正在使用。旧文档的“forge 废弃/永远不能修有限次数武器”错误。

材料和目标的权威组件通常在服务端添加；动作组件登记与网络 tag 让客户端挑选动作。菜单缺失应逐层查 `RegisterComponentActions`、材料枚举、tag、骑乘/持重等条件，不能把 `repairer` 无条件移到两端。`USEITEM` 回调不能依赖客户端不存在的 `target.components.trader`；客户端用实际同步的信息筛选，服务端 `CanAccept`/`Repair` 再决定是否成功。

不要为了一个武器把原版 `nightmarefuel.components.repairer.repairmaterial` 改成独占自定义值，这会改变原本修复对象。优先复用既有材料合同，或使用独立材料/限定动作。材料枚举和名称属于设计选择，未约定时询问。

`SetUses` 在归零路径可能先发出负百分比再钳到 0；需要保留破损物品并且观察到 UI 残留时，可在自己的破损处理末尾再次同步 0。不要把此项目修复扩大成所有物品都必须重复 `SetUses(0)` 的规则。消费堆叠材料只取单件，不能 `inst:Remove()` 删整组。

## 制作配方与蓝图

当前环境版签名为 `AddRecipe2(name, ingredients, tech, config, filters)`；可选项放 `config`，不是旧 `Recipe` 的位置参数。以下函数只展示已获批准的数据如何接入：

```lua
local function RegisterItemRecipe(name, ingredients, tech, atlas, image, builder_tag)
    return AddRecipe2(name, ingredients, tech, {
        atlas = atlas,
        image = image,
        builder_tag = builder_tag,
    }, { "WEAPONS" })
end
```

- `builder_tag`、技能限制、`nounlock`、`product`、`numtogive`、placer、过滤器分别核对当前 `recipe.lua`/`builder` 消费者；更改 tag 后必要时更新制作菜单。
- 科技值查 `constants.lua` 中 `TECH` 和相应 prototyper，不能把相似枚举一概解释成同一个科技站。`TECH.LOST` 是高科技门槛，不自动决定蓝图从哪掉落。
- `blueprint.lua` 只为满足 `CanBlueprintSpecificRecipe` 的配方创建具体蓝图；`nounlock` 或 `builder_tag` 会排除，至少一个科技值大于 0 只是另一条件。先确认具体蓝图已注册再加掉落。
- 改解锁方式时追踪旧掉落、teacher 与存档已学配方，不能机械删除所有旧代码；是否迁移由项目设计决定。
- Inventory `imagename`、配方 `image`、XML Element 名与注册接口对 `.tex` 的约定不同。逐处追消费者；图标可映射到不同图集，不要求所有文件名完全相同。

## 锅料理：配方数据与可食实体是两层

注册 `AddCookerRecipe("cookpot", recipe)` 只提供烹饪规则，不替代产品 prefab。按需求为其它锅分别注册；环境版已经标记为 mod food，第三个 `true` 参数不是必要开关。

1. 定义 ingredient tags，复核 `AddIngredientValues` 会替换该名字原有 tags；修改原版食材时不能不知情覆盖全部属性。
2. `recipe.test(cooker, names, tags)`：`names` 为具体食材计数，`tags` 为累计食材值，允许字段缺失。准确数量用比较而不是仅判断真值。
3. `priority` 决定候选最高档；同档按 `weight` 选择。根据用户想保留的原版料理测试组合，不能一律 `priority >= 30` 抢优先级。
4. 明确写入正数 `weight`。当前排序/总和部分虽有 `or 1`，实际抽取减法仍直接使用 `weight`；遗漏项被选中处理时可能报错。
5. 产品 prefab 有完整 Network/Pristine 分界、edible、perishable、inventoryitem/stackable、名称台词、资产和实际饮食分类。
6. `preparedfood` 是原版调味链使用的协议。若允许调味，还需对应调味配方和产品 prefab；仅加 tag 不完成接入。`FOODTYPE` 当前无 FISH，鱼类食材 tag 与 `edible.foodtype` 不是同一集合，按实际饮食设计选有效枚举。

下面只定义一个“精确三类食材计数”测试器，数量和合法 ingredient key 由已确认设计提供；这避免教程“想要 1 蛋 2 灰 1 硝石，代码却仅检测存在”的偏差：

```lua
local function MakeExactIngredientTest(expected)
    return function(cooker, names, tags)
        for name, count in pairs(expected) do
            if (names[name] or 0) ~= count then
                return false
            end
        end
        for name, count in pairs(names) do
            if count > 0 and expected[name] == nil then
                return false
            end
        end
        return true
    end
end
```

## 植物、生长与种植

`growable` 的 stages 至少区分：`fn` 应用某阶段静态状态，`time` 函数给该阶段剩余生长时间，目标阶段 `pregrowfn`/`growfn` 在转移时执行。`SetStage` 本身不代表设置新计时，应检查当前任务是否需重启。

**`time = nil` 不表示暂停：缺少 time 函数会回退 10 秒。** 停止用 `StopGrowing()`，或给 `time` 提供返回 nil 的函数；自然转移到非循环最后阶段时组件会停止，但手工在最后阶段 `StartGrowing()` 仍不能据此假定不建任务。`growonly`、`loopstages`、休眠/离线追赶、魔法生长各有独立语义。

```lua
local function NoFurtherGrowth(inst, stage, stagedata)
    return nil
end

local function ConsumeOneSeed(inst)
    local item = inst.components.stackable ~= nil
        and inst.components.stackable:Get() or inst
    item:Remove()
end
```

种植流程先验证并成功创建树苗，再消费一颗种子；失败不要消耗整叠。选 `DEPLOYMODE.PLANT`/DEFAULT/CUSTOM 时读两端实现：当前 `deployable:CanDeploy` 与 `inventoryitem_replica:CanDeploy` 都支持实体字段 `_custom_candeploy_fn`，需要自定义时将纯查询函数放公共初始化，并设置 CUSTOM。无需默认 monkey-patch 整个 replica。客户端显示可种，服务器仍需重新校验。

树木还要核对：各阶段动画是否真实存在、砍伐/挖树桩、燃烧/烧焦、掉落、风摆/物理、季节/魔法增长、守卫生成、自然生成与种植初始阶段、存读档。洞穴 0.75 倍、四阶段、默认高大等均是某项目设计，不能成为所有植物的硬规则。

## 证据与验证入口

在当前原版 scripts 下按函数名检索；行号仅为 2026-09-27 核验环境的快照定位，源码基线见 [environment-tools.md](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/environment-tools.md)：

| 主题 | 定义与调用链 |
|---|---|
| 物品骨架、装备 | `prefabs/spear.lua`；`components/equippable.lua:68-122` |
| 伤害、投射物 | `components/damagetypebonus.lua:10-53`；`components/planardamage.lua`；`components/spdamageutil.lua:23-30,99-119`；`components/projectile.lua:225-251` |
| 投掷落点与强制动作 | `bufferedaction.lua:2-9,90-96`；`components/playercontroller.lua:5068,5107-5113`；`actions.lua:310-320` |
| 修复菜单与结果 | `componentactions.lua:1279-1299,1679-1699` → `components/repairable.lua:106-182` / `forgerepair.lua:28-60`；`standardcomponents.lua:1851-1884`；`finiteuses.lua:1-7,64-78` |
| 配方与蓝图 | `modutil.lua:732-749` → `recipe.lua:229-234`；`prefabs/blueprint.lua:44-74,241-249` |
| 料理 | `modutil.lua:643-646` → `cooking.lua:9-29,46-68,238-287`；`prefabs/preparedfoods.lua:43-149`；`preparedfoods.lua` |
| 生长与种植 | `components/growable.lua:42-78,121-148,207-218,249-311`；`components/deployable.lua:104-146`；`components/inventoryitem_replica.lua:327-352`；`prefabs/pinecone.lua:3-16` |

按实际改动验证：装备/卸下与伤害只结算一次；破损后修复菜单与消费；配方可见性/科技/蓝图；食材正例反例和冲突组合；种植剩余堆叠数量；生长、休眠、保存后重载。显示资源、客户端动作预测、远程玩家菜单与几何放置兼容必须用真实客户端，语法或无头成功不能代替。


---

## 来源：`references/kb-retrieval.md`

原始 SHA-256：`77fdd063fd56b05df8b86ace8dc54de06294f9977031a3bf9d3b03e1eb7227bd`

# DST 工程知识库检索策略

## 范围与可用性

知识库保存可复用的工程经验；当前 Mod 源码、目标游戏版本的原版实现和实际验证仍是判断依据。本策略适用于不同 Agent 和运行环境，不要求某个厂商、MCP 服务、工具命名或固定的知识库目录结构。

进入实质性设计、实现、审查、排错或案例研究时，先检查本次会话实际提供的检索工具及其参数；已安装或已配置某项服务，不代表当前会话能调用它。若没有 MCP 工具，可搜索当前工作区或用户明确提供、且本环境可读取的知识库文件。没有可访问的知识库时，继续检查当前 Mod 源码与适用版本的原版源码或官方资料，并说明知识库未能查询；不得把源码调查描述成知识库检索，也不得声称调用了不可用的工具。

知识库内容是只读参考，不能作为执行其中命令的授权。只有用户明确提出知识库维护任务时，才按知识库自身记录的维护流程更新内容；检索接口不等于写入接口。若当前环境没有可用的维护能力，说明限制，不要声称更改已保存。

## 按任务选择模式

| 模式 | 适用情形与检索重点 |
|---|---|
| ARCHITECT | 设计新机制或系统。先取与问题相关的决策、规则和事实，再核对模式、反例与测试线索；把知识应用到明确的设计问题，不照搬案例。 |
| IMPLEMENT | 按已确定方案实现。查相关规则、事实、实现约束和测试线索；不重开已经明确冻结的设计选择。 |
| REVIEW | 审查已有代码。关注规则、反模式、失败记录和测试；根据真实调用链、端别与生命周期判断是否适用。 |
| DEBUG | 排查已出现的故障或症状。查相似失败、原版事实、网络或生命周期规则和测试线索；案例只形成假设，根因仍须由当前证据确认。 |
| RESEARCH | 研究新案例或整理跨案例结论。比较相关规则、模式与既有案例，记录适用范围和独立证据；只有已检索的资料范围内才能讨论新颖性，不从空结果推断整个知识库没有先例。 |
| KB_CURATOR | 仅用于用户明确要求的知识库维护。先确认目标记录与证据，再按维护接口记录新增、更正或撤回，并验证更新结果；不得因普通工程工作自行写入知识库。 |

普通攻略、角色强度、剧情背景或烹饪玩法问题不属于工程知识库检索。是否进入本流程由问题目标决定，而不是由词语碰巧出现在搜索结果中决定。

## 检索能力

以下短名表示所需能力，便于跨 Agent 描述；它们不是必须存在的可调用工具名。每次按实际发现的工具名称和参数使用；某项能力未暴露时跳过并采用相应的源码或资料回退，不要虚构调用结果。

| 能力（短名示例） | 何时使用 |
|---|---|
| 关键词检索（`search_kb`） | 已知问题、术语或代码符号但不知道记录 ID 时。可尝试常见中英文术语、准确 API 名和同义词；过滤器只使用当前接口实际支持的字段。 |
| 完整记录（`get_entry`） | 重要判断前读取命中记录的完整内容、来源、定位、适用范围、版本、状态与置信度。已知准确 ID 时可直接读取。 |
| 关联记录（`get_related`） | 补充某条记录关联的规则、反例、决策或测试。保留关联关系的方向；存在链接本身不表示两条记录互相支持。 |
| 原版事实查询（`get_klei_facts`） | 查询知识库中已整理的原版 API 或机制事实。若该能力不可用或未找到事实，直接查适用版本的原版源码或官方资料，不用 Mod 案例代替原版契约。 |
| 测试线索查询（`get_tests`） | 找到可能适用于该问题的测试和环境要求。命中测试条目只表示候选；只有实际执行并记录结果后才能报告测试通过。 |
| 任务上下文包（`get_context_bundle`） | 需要多个知识类别协同的复杂任务。用当前接口支持的模式和预算；摘要不足时再读取少量关键记录全文，不追求填满上限。 |
| 知识库校验（`validate_kb`） | 知识库维护或明确的可用性诊断。普通开发、审查和排错无需每次全库校验。 |

本仓库可选服务的实际参数见 [工具定义](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-kb-service/docs/mcp-tools.json)：模式参数使用小写（如 `architect`、`debug`），上下文预算为 `compact`、`normal`、`deep`。复杂设计命中相关 ARP 时读取完整条目，再围绕实际问题选择决策、规则、事实、模式、反例与测试；不要对每个小函数重跑整个流程。

## 命中筛选与检索范围

- 搜索结果只是一组候选。逐条检查其主题、记录类型、状态、适用范围、版本、来源定位及检索词的真实含义；把同词异义、仅有标签关联或不覆盖当前端别与环境的结果排除或标成弱相关。
- 关键词可能需要中英文变体、精确符号和领域同义词。过滤器或索引会限制结果，空结果或未命中不证明整个知识库没有相关记录。
- Top-K、摘要或上下文包未返回某类记录，不代表该类别不存在。搜索量不等于覆盖度；只对实际读到的范围下结论。
- 如果记录的 Scope 不覆盖当前 Mod、游戏版本、端别或运行环境，将它作为背景而非直接结论，并说明范围差异。空白的测试环境声明不保证其他环境通过。

## 证据、状态与更正

- 读取重要记录的类型、状态、Scope、证据、来源定位、版本与关联更正。区分直接原版事实、跨案例证据、单案例观察和待验证假设；检索排序或记录的置信度不能替代对当前问题的判断。
- Decision 表达特定情境下的选择，不自动成为强制架构；Pattern 不是普遍最佳实践；Anti-Pattern 表示需要警惕的做法，不证明每次使用都必然失败。
- 已被 superseded 的主张只作历史资料，读取并采用其对应的 Correction。若报告中的单个主张被更正或撤回，其他独立主张仍需分别评估，不随之自动失效。没有明确 claim ID 的自然语言概括要回到原文和当前证据核对。
- 重要设计结论与知识库支持的发现应标出可读记录 ID。独立从当前代码或原版源码得到的发现，应说明实际路径和证据并标为独立发现；不得捏造知识库记录来增强结论。
- 原版快照或旧版本记录不自动代表用户正在运行的版本。记录中的测试建议与已执行测试分开陈述，并写清实际覆盖的环境。

## 缺口与故障回退

知识库无匹配、范围不覆盖或检索工具不可用时，将相应结论记作 Knowledge Gap 或说明 KB unavailable，并写明具体原因和可确认的检索范围。然后继续用当前项目代码与适用版本的原版源码、官方资料完成可做的调查。检索失败不能升级成“知识不存在”；未成功调用不能写成“已查询知识库”。


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

## 来源：`references/networking-rpc.md`

原始 SHA-256：`0cea2f07b471708f091215b419b73dfe21859c7f8579fb909967fe26853f2848`

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


---

## 来源：`references/sources-and-corrections.md`

原始 SHA-256：`eb6d798e34697104413cfb3dfdc50de7940cc041b65d19b464b8dcd6b2eba1e8`

# 来源、可信度与纠错范围

开发资料参考 [atjiu/dstmod-tutorial](https://github.com/atjiu/dstmod-tutorial)；教程用于提供线索，接口与行为以当前游戏实现为准。

辅助脚本实现 ZIP 读取、AST 声明检查与隔离专服测试。当前专服测试工具入口为 [scripts/dst_modtest.py](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/scripts/dst_modtest.py)，历史来源包括 [dst-ai-scripting](https://github.com/lw-0x4eb1a/dst-ai-scripting)。具体检查能力见 [测试与交付](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/references/testing-release.md)。

技术事实优先核对合法安装的游戏与官方 Mod Tools；本仓库不分发它们的源码、资源或二进制。工具与参数的公开参考包括 [ktools 作者说明](https://github.com/nsimplex/ktools/blob/master/README.md)、[Klei 专服命令行说明](https://kleiforums.com/forums/topic/64743-dedicated-server-command-line-options-guide/) 和 [FFmpeg 滤镜文档](https://ffmpeg.org/ffmpeg-filters.html)。具体调用以当前安装版本的帮助和相关游戏实现为准。

## 怎样判断资料

| 情况 | 采用方式 | 例子 |
|---|---|---|
| 概念仍适用 | 核对当前实现与适用边界 | Component/Replica 分工、WorldGen 的 room/task/layout |
| 签名、端别或时序有误 | 追查原版定义与调用方 | Client RPC 没有隐式 player；实体与组件 OnSave 不同 |
| 存在多种实现 | 按适用条件、维护成本与实测结果选择 | 局部控件拖拽与全局 FollowMouse 覆盖 |
| 尚无运行证据 | 保留待验证标记与验证方法 | 旧工具兼容、引擎接口、客户端画面与听感 |

Lua 源码或工具文档中未找到的引擎绑定，不能直接判为不存在。教程截图仅作步骤示意；附件的清单、结构或语法检查不能证明旧 EXE/DLL 可运行，也不能代替游戏验收。

## 高影响纠错索引

| 常见误区 | 参考专题 |
|---|---|
| env 代理必须、pcall 全禁、scripts 下 GLOBAL 一律错 | core-lua-hooks.md |
| modinfo 赋值末尾逗号、GetModConfigData 第二参是默认值 | core-lua-hooks.md |
| PrefabFiles/文件/prefab 名三者必须相等 | entities-components.md |
| 主组件与 replica 方法混查、net_string 可以 set table | networking-rpc.md |
| Client RPC 回调首参 player、namespace 必然等于目录 | networking-rpc.md |
| 保存固定组件顺序、所有 OnSave 签名一样 | lifecycle-save.md |
| Widget 无 inst、吞全部 ESC、全局修改 FollowMouse | ui-actions-controls.md |
| aoespell 一定放两端、任意隐形 FX 能当 spellbook 载体 | ui-actions-controls.md |
| 伤害 bonus 的 1.0 表示 +100%、planardamage:DoDelta | combat-buffs-containers.md |
| bank=build=symbol、anim ZIP 必须三件齐全 | assets-animation.md |
| 64×64 atlas 必坏、149 帧必崩、任何动画不超过60帧 | assets-animation.md |
| ktech 不能生成 XML、autocompiler 全面禁用 | assets-animation.md |
| 固定采样率/声道/压缩才兼容、FSB5 一定不能用 | audio-particles.md |
| 同名 Mod 可直接复用、脚本 return 就可判成功 | testing-release.md、三个 scripts |
| 离线端口永远10999、用猜测端口配置后杀别的进程 | environment-tools.md |
| PushEvent 全部下一帧、GetAttacked 传 electric 自动加倍率 | spells-and-custom-stats.md |
| 每隔 1 世界单位灌溉即每格加一次、睡眠原函数后无条件恢复 | spells-and-custom-stats.md |
| 自定义属性必须使用 Class setter、构造中从 components 取回自身 | spells-and-custom-stats.md |
| 项目料理 helper 当原版 API、AddCookerRecipe 自动建实体和调味 | cooker-dishes.md |
| 17 个台词表等于全部角色、强制三目录或固定图集 | cooker-dishes.md |
| 手持必须 BUILD_90s_90s、整包搜哈希就证明符号存在 | character-and-equipment-art.md |
| 固定模板帧数/画布适合所有角色、删除整个 anim 强制编译 | character-and-equipment-art.md |
| 多图集必须正方形、所有素材可用同一抠图与锚点算法 | animation-recipes.md |
| 专服打印即音效通过、全部 GUID 可无差别替换 | audio-particles.md |

检查范围、工具回归结果与未覆盖内容见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。各专题提供源码文件/函数定位、适用条件和验证边界，供读者复核。

源码定位使用相对文件名与函数名，行号仅对应引用快照；源码哈希见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。游戏更新后需重新核对相关实现。

专题中的项目案例用于说明机制，数值与美术效果需由当前项目决定。


---

## 来源：`references/spells-and-custom-stats.md`

原始 SHA-256：`2c7e56534b8a8893baac5fd13b32534c80044cf9c9b45b1215be1f93071a147e`

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

## 来源：`references/worldgen-spatial.md`

原始 SHA-256：`a007921c4c23575c1866053961522b665fd8d0d648e22503c5bf6d39662dc622`

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


---

## 来源：`templates/local-validation.md`

原始 SHA-256：`3117ea62a892340c4128a4cd3e82cb61bb88ca7c7ef715adcd80ebf3013352e9`

# 本机验证回传

复制填写；不知道写“未知”，未执行写“未执行”。仅回传相关证据，原始日志与私人存档留在本机。

## 任务与环境

- 任务 / 补丁编号 / 验证时间：
- 期望结果 / 实际结果：
- 操作系统 / 架构 / 执行者（本人或本机 Agent）：
- 场景：房主 / 远端客户端 / 专服；地表 / 洞穴；单人 / 多人：
- 游戏版本 / scripts.zip SHA-256（已取得才填）：
- Mod 版本 / 提交 / 配置 / 同时启用的相关 Mod：
- 源码副本 / 游戏运行副本（可用本地别名，说明对应关系）：
- 本轮实际加载的 Mod 路径或标识 / 判定依据：
- 使用的工具、版本与路径别名：
- 本轮授权范围 / 未授权或不可执行的步骤：

## 文件与应用结果

| Mod 相对路径 | 原文件 SHA-256 / 版本 | 应用后 SHA-256 | 新增/修改 | 应用结果 |
|---|---|---|---|---|
| 待填写 | 未知 | 未执行 | 待填写 | 待填写 |

- 补丁是否与原版本匹配 / 冲突处理：
- 是否在独立副本应用 / 源码与运行副本差异：
- 存档保护方式（不得覆盖私人存档） / 回退位置：

## 执行证据

| 检查层级 | 工作目录别名与完整命令 / 手工步骤 | 退出码 | 本轮 ID / 完成或失败标记 | 日志/截图/产物 |
|---|---|---|---|---|
| 语法/API/资源结构 | 未执行 | 不适用 | 不适用 | 无 |
| 专服行为/保存重启 | 未执行 | 不适用 | 不适用 | 无 |
| 房主+远端客户端/视觉/听感 | 未执行 | 不适用 | 不适用 | 无 |

- 复现步骤 / 第一个失败点 / 错误前后文与完整堆栈：
- 专服实际断言 / 观察窗 / 保存与重启是否发生：
- 截图观察者、动作与时间点 / 声音实际试听结果：
- 日志剔除字段（令牌/密码/无关私人内容；保留结构占位）：
- 已确认结论 / 条件性结论 / 仍待决定的玩法：
- 未测项、原因与下一步：

退出码、标记和日志应结合判断；记录命令不表示已执行。不要用模拟或专服结果替代真实客户端验收。


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
