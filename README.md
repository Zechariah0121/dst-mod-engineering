# DST Mod Engineering

当前版本 `v2026.10.31.3` 共 227 条登记记录：保留旧 187 条，另有 40 条 native_mechanism 研究（Brain、世界生成、料理/调味、成长/再生、温度/潮湿、冻结/火热交互、生存补充及表现机制）。数量由 `knowledge/FAMILY-REGISTRY.json` 生成 `CATALOG.counts`。研究族仅显式 Reviewer 审阅，保持 `research/restricted/hold`。详见 [机制研究族](docs/native-mechanisms.md)。

面向《饥荒联机版》Mod 开发的工程 Skill 与知识库：按任务读取知识、核对当前源码，再设计、实现、审查和验证。[English README](README.en.md)

公开知识库位于 `knowledge/`，包含 **227 条记录：64 条基础知识、13 条 Native AI 知识、110 条 Native Core 知识和 40 条独立机制研究**。同一完整发行包包含 Skill、当前知识、开发辅助脚本、来源准备工具与只读 MCP 服务。记录数量不代表全部可用于 Coding，原有 Scope、类型、版本、更正和 HOLD 仍有效。

## 下载

当前发行：[v2026.10.31.3](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.31.3)。下载唯一完整发行包即可安装 Skill、阅读知识或接入 MCP。历史 [v2026.10.25.4](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.25.4) 保留其 187 条发行身份。

| 附件 | 包含内容与用途 |
|---|---|
| [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.31.3/dst-mod-engineering.zip) | 完整 Skill、唯一 `knowledge/` 中的 227 条登记知识、开发辅助脚本、来源准备工具与 MCP 服务 |

下载后对照发行页的 `SHA256SUMS.txt`。包中不含游戏 Lua 原文、第三方可执行工具或私人 Mod 工程。

公开版提供 Skill 驱动的源码更新助手：首次绑定已明确的合法 `scripts.zip`，以后查库前自动检查同一路径，尝试适配可恢复的来源。变化部分由 AI 按当前任务核对；既有知识保留原适用范围，不因游戏更新关闭全库。详见 [更新助手](references/source-update-assist.md) 和 [能力与限制](docs/public-limits.md)。

## 开始使用

1. 完整解压，找到直接包含 `SKILL.md` 的目录。把该目录完整放入 Agent 支持的技能位置，例如 Codex 的 `.agents/skills/dst-mod-engineering/`；其他安装位置见 [安装说明](docs/install-and-use.md)。
2. 调用 `dst-mod-engineering`，提供任务、Mod 目录、实际 DST 版本和合法本地 `scripts.zip` 位置。没有 MCP 也可按 [知识库接入](docs/knowledge-integration.md) 读取少量相关知识文件，不默认加载全库。
3. 首次使用，在包根目录绑定明确的游戏源码并生成客户端配置：

```text
python -B -X utf8 run_kb.py update-sources ensure --source "<scripts.zip绝对路径>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

绑定后由 Skill 在查库前调用 `update-sources ensure`，无需重复给路径；相同输入已检查时快返。需要 Python 3.10+ 与 SQLite FTS5。将打印配置按客户端要求接入，并在客户端确认九工具与一次实际查询。已经连接目录模式的会话，准备成功后需重启才能切换工具集。配置打印不代表连接或查询成功，见 [安装与验证](docs/install-and-use.md)。

默认 `--mode auto` 在准备有效时启用完整模式；来源未准备或包升级造成 `PACKAGE_CHANGED` 时，校验公开知识清单后提供两工具审阅并报告原因。缓存损坏、无效激活和不可信公开文件仍报错。`--mode full` 保持严格，目录模式不提供 Coding 上下文或已恢复源码证据。新版源码导航及局部复核见 [源码维护](docs/source-compatibility.md)。

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

适配 761239，改善相关知识检索，补充火焰更新与特效挂接 API。详见[本阶段说明](docs/phase6-retrieval-fx.md)。
