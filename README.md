# DST Mod Engineering

`v2026.11.12.3` 面向《饥荒联机版》Mod 开发，提供按任务检索的知识、原版核查路径、开发辅助脚本与 MCP。[English](README.en.md)

当前共 **296 条登记知识：64 基础 + 13 Native AI + 110 Native Core + 109 机制研究**。本轮整理开发任务地图，补充简短查找与读取命令，改善检索开销，让 AI 更快找到相关依据并明确还需核查的部分。见[本轮内容](docs/phase14-usage-retrieval.md)。

机制研究族登记了 404 项 API 合同，计数范围为该族记录的 `api_contracts`。全库 API 总数与源码覆盖率尚无统一盘点。

已有复杂问题的渐进读取、有期限效果恢复和实用优化示例，帮助串联关键合同，减少重复查询、额外轮询与多余状态。前一阶段的专题扩展见[阶段 13](docs/phase13-practical-expansion.md)。

## 下载与开始使用

公开包从 [最新发行版](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest) 下载 [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest/download/dst-mod-engineering.zip)，对照同版 `SHA256SUMS.txt` 后完整解压；仓库中的新内容会分批发布。一个包包含 Skill、唯一 `knowledge/`、脚本、来源准备与 MCP；游戏 Lua、第三方可执行工具和私人项目不随包分发。

1. 将直接包含 `SKILL.md` 的完整目录放入 Agent 支持的技能位置，见[安装说明](docs/install-and-use.md)。
2. 调用 `dst-mod-engineering`，提供任务、Mod 目录和实际游戏源码；从 [Skill 专题表](SKILL.md) 选择入口。
3. 需要完整 MCP 时，用 Python 3.10+（含 SQLite FTS5）从包根执行：

```text
python -B -X utf8 run_kb.py update-sources ensure --source "<scripts.zip绝对路径>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

按客户端格式接入打印的配置，核对九工具与一次实际查询。绑定后，Skill 在实质查库前运行 `update-sources ensure` 检查同一路径；状态和重连流程见[更新助手](references/source-update-assist.md)。

没有 MCP 也可用 `run_kb.py find` / `read` 定位并审阅公开记录，命令见[知识文件入口](docs/knowledge-integration.md)。检索准入、预算和来源身份统一见[检索策略](references/kb-retrieval.md)，当前源码适配见[源码维护](docs/source-compatibility.md)。

## 按任务进入

| 任务 | 入口 |
|---|---|
| 从完整功能出发，找已有合同、局部覆盖、项目依赖与待验项 | [开发任务地图](references/task-map.md) |
| 角色、法术、装备、料理、UI 与资源 | [Skill 专题表](SKILL.md) |
| 模块职责、接口与失败恢复 | [复杂 Mod 架构](references/complex-mod-architecture.md) |
| 输入、预测、权威结算与取消退出 | [动作接入指南](references/action-lifecycle-architecture.md) |
| 静态检查、隔离专服与交付 | [测试与交付](references/testing-release.md) |
| 网页附件与云端交接 | [网页指南](references/web-chat.md) |

研究记录保留各自 Scope 和 Coding HOLD，按[准入规则](references/kb-retrieval.md)使用。本轮主要变化见[本轮说明](docs/phase14-usage-retrieval.md)。

项目自有材料使用[非商业 LICENSE](LICENSE)，商业用途需另获书面授权；第三方与有效历史 MIT 授权按各自条款处理。具体情形见[许可说明](docs/licensing.md)。
