# 网页聊天中的 DST 开发协作

本页说明网页中的资料传递与协作流程，DST 技术规则见 [技能入口](../SKILL.md) 及相关专题。平台入口按 **2026-09-27** 核验的官方文档列出，尚未经过网页导入与执行的端到端实测。

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
| 加载失败 / 崩溃 | [Lua 与 Hook](core-lua-hooks.md)、[实体与组件](entities-components.md) | 第一处错误及完整堆栈、相关入口/Prefab/组件、对应配置 |
| 主客机不一致 / HUD | [网络与 RPC](networking-rpc.md)、[界面与动作](ui-actions-controls.md) | 服务端与客户端相关代码、观察者身份、复现位置、相关日志 |
| Buff / 死亡 / 读档 | [生命周期](lifecycle-save.md)、[战斗与 Buff](combat-buffs-containers.md) | 应用/移除/保存代码、已确定的玩法规则、复现顺序 |
| 贴图 / 动画 / 编译 | [图像与动画](assets-animation.md)、[工具准备](tool-bootstrap.md) | Lua 资源引用、文件清单、相关 XML/SCML、小型输入样本、实际工具版本/日志 |
| 制作 / 料理 / 植物 | [物品、食物与植物](items-food-plants.md) | 配方/Prefab/组件及相关注册代码、实际配置 |
| 世界生成 / 地形 | [世界生成](worldgen-spatial.md) | worldgen 入口、相关 room/task/layout、种子和生成日志 |

核对原版时，由 AI 指定文件、函数及调用方，用户从合法安装中取得必要片段，并记录游戏版本或 `scripts.zip` 指纹。缺少初始化或端别上下文时继续补齐。

粘贴或上传时注明原相对路径、完整文件或片段范围、版本依据。同名附件可编码路径，如 `scripts__components__my_component.lua`，并附映射。

平台不接收文本后缀时，可上传内容不变的文本副本并注明原扩展名；执行前恢复路径和文件类型。二进制动画、TEX 或压缩包需使用相应解析工具，不能靠改名 `.txt` 读取。

无法补齐源码时，给出候选原因、成立条件和检查方法；涉及 API、顺序或端别的修复标为待确认。

## 云端能运行时，怎样使用脚本

先确认脚本、输入、依赖和执行权限，记录实际环境。有 Python 不代表可以安装包、联网下载或运行 Windows EXE。

- 已有 Python / `luaparser` 且输入完整时，可做 [静态检查](testing-release.md)；没有实际运行就交付命令，不编造输出。
- 只有部分源码片段时，记录检查范围；`check_api.py` 需要它支持的原版源码输入布局，不能拿不完整摘要冒充完整目录。
- PNG/XML/ZIP 结构检查与模拟测试可在具备相应能力的环境执行，但不等于引擎解码、真实 UI 或联机通过。
- 随附专服启动器需要其支持的 Windows 游戏环境。普通云端沙盒不能使用用户电脑的盘符，也不能由云端 Python 的成功结果推断本机专服通过。
- 若会话另有明确授权的本机执行连接，先核对实际主机、路径和权限；只有相应调用记录才能报告本机执行。

云端产物需确认可下载且完整，再应用到 Mod 源目录或游戏运行副本；不会自动同步或发布到 Workshop。

## 缺工具与安装授权

按 [工具安装与首次验证](tool-bootstrap.md) 准备当前任务所需工具。缺项时说明官方/作者来源、适用平台、必要依赖、安装目录与样本验证步骤。

有执行连接与已有授权时继续执行；缺少本机连接时，提供方案和命令，由用户或本机 Agent 运行。只为尚未授权的操作或未决定的效果请求确认。

## 交付和本机回传

交付须能对应明确的原文件：

1. 列出每个新增/修改文件相对于 **Mod 根目录** 的路径，说明交付的是完整文件还是补丁；不要提供云端绝对路径作为用户安装目标。
2. 记录适用的原提交/版本与原文件 SHA-256（确实取得时）。只有粘贴文本时不得声称知道本机原文件哈希；文本副本哈希需标明编码/换行范围。
3. 给出改动原因、影响和剩余玩法决策；原文件版本不匹配时先重新比较，不能强行覆盖后来的修改。
4. 分开列已执行的检查、命令/环境/证据与待用户执行步骤；“静态通过”“云端模拟通过”“专服通过”“客户端通过”分别记。
5. 在副本上应用并比较差异，保留私人存档；发布需单独授权。
6. 用 [本机验证回传模板](../templates/local-validation.md) 收集对应副本、结果和未测项，再根据新证据继续修复。

回传日志保留错误前后文、堆栈、版本和测试标记；令牌、密码及无关私人内容用占位符替换，注明删改字段。原始日志留在本机。

证据等级见 [测试与交付](testing-release.md)，已测范围见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。
