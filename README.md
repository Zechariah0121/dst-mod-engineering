# DST Mod Engineering

面向《饥荒联机版》Mod 开发的 AI 工程 Skill：核对当前源码，再设计、实现、审查和验证。适合借助 AI 制作角色、物品、法术和资源，也适合排查联机、存档与兼容问题。[English README](README.en.md)

本独立 Skill 包含工作方法、专题参考和三个辅助脚本，**不附完整工程知识库、MCP 服务、游戏源码或私人 Mod 工程**。没有额外 KB 时，仍可配合你合法取得的本地源码工作。

## 下载

本版：[Public Beta 1 发行页](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.25)。

| 附件 | 适用方式 |
|---|---|
| [dst-mod-engineering.skill.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25/dst-mod-engineering.skill.zip) | Agent 安装；完整 Skill、专题与三个开发辅助脚本 |
| [web-reading.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25/web-reading.zip) | 网页 AI 或离线阅读；按任务选择专题 |
| [dst-mod-engineering-full.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25/dst-mod-engineering-full.zip) | 完整公开仓库；另含64条早期参考知识及其只读 MCP 服务 |

下载校验见发行页的 `SHA256SUMS.txt`。完整公开仓库不包含另行私用的完整版知识库或私人研究材料。

## 安装与开始使用

1. 从 [仓库发行页](https://github.com/Zechariah0121/dst-mod-engineering/releases) 下载独立 Skill 附件并完整解压，找到直接含 `SKILL.md` 的 `dst-mod-engineering/` 文件夹。
2. 把完整目录放入 Agent 支持的技能目录。例如项目内的 `.agents/skills/dst-mod-engineering/`（Codex），或 `.claude/skills/dst-mod-engineering/`（Claude Code）。其他产品与个人安装位置见 [安装说明](docs/install-and-use.md)。已有同名目录时先保留定制内容。
3. 调用 `dst-mod-engineering`，提供任务、Mod 目录、实际 DST 版本和本地 `scripts.zip` 位置。确认 Agent 能读取 `SKILL.md` 及相关专题；没有自动发现能力时，直接指定该文件的实际路径。

网页聊天使用附件或平台支持的技能导入，见 [网页使用指南](references/web-chat.md)。大部分专题为中文；英文 README 不代表全部内容已翻译。

## 按任务使用

| 目标 | 起点 |
|---|---|
| 实现角色、法术、装备、配方、UI 或资源 | [SKILL.md](SKILL.md) 的专题索引；提供期望效果与触发条件 |
| 源码研究、崩溃、联机与存档故障 | 追踪定义、调用方、端别、初始化、退出和保存链路 |
| 语法、API 声明或隔离专服检查 | [测试与交付](references/testing-release.md) |
| 接入已有 KB | [可选知识库](docs/knowledge-integration.md)，以实际可用服务及其版本为准 |

脚本需 Python 3.10+；语法检查另需 `requirements.txt` 中的 `luaparser`。随附专服测试器仅支持 Windows。读取 Skill 无需运行脚本，动画和音频工具按任务另行准备，来源与首次验证见 [工具安装](references/tool-bootstrap.md)。

专题中的版本、样例与源码定位有各自适用范围，不保证当前在线版本或所有 Mod 兼容。静态检查、专服行为、真实远端客户端、视觉与音频分别验证，见 [能力与版本限制](docs/public-limits.md)。

## 可选公开参考知识库

完整公开仓库保留 **v0.1.1、64条**参考知识和只读检索服务，内容范围与该版本的来源说明保持不变。
需要时阅读 [知识库入口](https://github.com/Zechariah0121/dst-mod-engineering/blob/v2026.10.25/dst-engineering-kb/README.md) 和 [MCP 接入](https://github.com/Zechariah0121/dst-mod-engineering/blob/v2026.10.25/dst-kb-service/README.md)；独立 Skill ZIP 未携带它们。
这是可选参考资料，不是最新全量游戏知识；具体条目的状态、版本、证据与未执行测试仍须分别读取。

## 许可

项目自有材料使用 [自定义非商业 LICENSE](LICENSE)，不是 MIT 或 OSI 开源许可。商业使用须另获书面授权；有效历史 MIT 授权与第三方权利仍按各自条款处理。见 [许可说明](docs/licensing.md)。
