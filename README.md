# DST Mod Engineering

面向《饥荒联机版》Mod 开发的工程 Skill 与知识库：按任务读取知识、核对当前源码，再设计、实现、审查和验证。[English README](README.en.md)

当前公开知识库位于 `knowledge/`，包含 **187 条记录：64 条基础知识、13 条 Native AI 知识、110 条 Native Core 知识**。Skill、独立技能包和网页阅读包均携带这些知识数据；完整包另含现代只读 MCP 服务。记录数量不代表全部可用于 Coding，原有 Scope、类型、版本、更正和 HOLD 仍有效。

## 下载

本版：[v2026.10.25.1](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.25.1)。首次使用建议下载完整包。

| 附件 | 包含内容与用途 |
|---|---|
| [dst-mod-engineering-full.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25.1/dst-mod-engineering-full.zip) | Skill、187 条公开知识、开发辅助脚本、来源准备工具和九工具 MCP 服务 `0.3.0`；适合本地完整接入 |
| [dst-mod-engineering.skill.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25.1/dst-mod-engineering.skill.zip) | 可安装 Skill、专题、187 条公开知识与三个开发辅助脚本；不含 MCP 服务与来源准备工具 |
| [web-reading.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25.1/web-reading.zip) | 网页与离线阅读材料、187 条公开知识；不含 MCP 服务与来源准备工具 |

下载后对照发行页的 `SHA256SUMS.txt`。包中不含游戏 Lua 原文、第三方可执行工具或私人 Mod 工程。

## 开始使用

1. 完整解压，找到直接包含 `SKILL.md` 的目录。把该目录完整放入 Agent 支持的技能位置，例如 Codex 的 `.agents/skills/dst-mod-engineering/`；其他安装位置见 [安装说明](docs/install-and-use.md)。
2. 调用 `dst-mod-engineering`，提供任务、Mod 目录、实际 DST 版本和合法本地 `scripts.zip` 位置。没有 MCP 也可按 [知识库接入](docs/knowledge-integration.md) 读取少量相关知识文件，不默认加载全库。
3. 使用完整包的 MCP 时，先在包根目录准备合法来源，再生成客户端配置：

```text
python -B -X utf8 prepare_sources.py --source "<759671 scripts.zip>" --source "<合法保留的756039 scripts.zip或源码目录>"
python -B -X utf8 run_kb.py mcp-config
```

需要 Python 3.10+ 与 SQLite FTS5。当前 `759671` ZIP 单独仍缺 13 种历史范围，涉及 9 个旧 Lua 文件；缺少历史来源时仍可文件阅读 187 条知识，但完整 MCP 尚未备妥。将打印配置按客户端要求接入后，入口为 `python -B -X utf8 run_kb.py serve`。配置打印不代表连接或查询成功，详见 [安装与验证](docs/install-and-use.md)。

准备生成的 `cache/runtime/` 含本地恢复的游戏源码片段，留在本地，不随公开包上传。JSON 中的 `$dst_source_payload_slot` 是待恢复的本地原文槽，不是已读源码或行为证据。

## 按任务使用

| 任务 | 入口 |
|---|---|
| 角色、法术、装备、料理、UI 与资源 | [SKILL.md](SKILL.md) 的专题索引 |
| 知识文件读取、MCP 查询、Scope 与准入 | [检索策略](references/kb-retrieval.md) |
| 联机、生命周期、存档、崩溃与兼容 | 核对实际定义、调用方、端别、初始化、退出和保存链路 |
| Lua 语法、部分 API 声明与隔离专服检查 | [测试与交付](references/testing-release.md) |
| 网页附件与云端交接 | [网页指南](references/web-chat.md) |

公开知识由经审材料生成必要的事实与证据片段，不包含原始研究档案。部分原有私有情境被明确隐藏为 `UNK`，不补写成通用结论。真实游戏、远端客户端、视觉、音频与全版本兼容均需单独验证，见 [能力与限制](docs/public-limits.md)。

## 许可

项目自有材料使用 [自定义非商业 LICENSE](LICENSE)，不是 MIT 或 OSI 开源许可。商业使用须另获书面授权；有效历史 MIT 授权与第三方权利仍按各自条款处理。见 [许可说明](docs/licensing.md)。
