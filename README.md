# DST Mod Engineering

`v2026.11.12.4` 面向《饥荒联机版》Mod 开发，提供按任务检索的知识、原版核查路径、开发辅助脚本与 MCP。[English](README.en.md)

当前共 **300 条登记知识：64 基础 + 13 Native AI + 110 Native Core + 113 机制研究**。本轮增加按 ID/API 的统一审阅与完整对象续读，并补充主动技能、装备效果、可收起建筑和两态生物四条具名功能链，连接输入、权威执行、消费者、退出与必要恢复。见[本轮内容](docs/phase15-unified-chains.md)。

机制研究族登记了 420 项 API 合同，计数范围为该族记录的 `api_contracts`。全库 API 总数与源码覆盖率尚无统一盘点。

四条链分别限定黄杖普通地面施法、Molehat 夜视、Portabletent 部署/收起与普通猪人两态转换，附自写最小示例和各自未知范围。示例已完成有限专服验证，其中装备、建筑和生物示例完成同一隔离存档的进程重启检查；真实客户端与跨分片仍待验。实际范围见[本轮验证](docs/phase15-unified-chains.md#验证状态)。已有任务地图和渐进读取见[阶段 14](docs/phase14-usage-retrieval.md)。

## 下载与开始使用

公开包从 [最新发行版](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest) 下载 [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest/download/dst-mod-engineering.zip)，对照同版 `SHA256SUMS.txt` 后完整解压；仓库中的新内容会分批发布。一个包包含 Skill、唯一 `knowledge/`、脚本、来源准备与 MCP；游戏 Lua、第三方可执行工具和私人项目不随包分发。

1. 将直接包含 `SKILL.md` 的完整目录放入 Agent 支持的技能位置，见[安装说明](docs/install-and-use.md)。
2. 调用 `dst-mod-engineering`，提供任务、Mod 目录和实际游戏源码；从 [Skill 专题表](SKILL.md) 选择入口。
3. 需要完整 MCP 时，用 Python 3.10+（含 SQLite FTS5）从包根执行：

```text
python -B -X utf8 run_kb.py update-sources ensure --source "<scripts.zip绝对路径>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

按客户端格式接入打印的配置，核对九工具与一次实际查询。需要当前源码支持的开发、审查或研究前，Skill 用 `update-sources ensure` 检查已绑定路径；状态和重连流程见[更新助手](references/source-update-assist.md)。

没有 MCP 也可用 `run_kb.py find` / `read` 定位并审阅公开记录，命令见[知识文件入口](docs/knowledge-integration.md)。检索准入、预算和来源身份统一见[检索策略](references/kb-retrieval.md)，当前源码适配见[源码维护](docs/source-compatibility.md)。

统一审阅使用 `get_entry` 的显式 Reviewer/purpose 或 `lookup_api(family="all")`，命令行入口为 `run_kb.py review ID` / `run_kb.py review --api "符号"`，均要求已准备完整来源。预算不足时按响应中的 `continuation` 续读完整对象，具体参数见[知识读取](docs/knowledge-integration.md)。

## 按任务进入

| 任务 | 入口 |
|---|---|
| 从完整功能出发，找已有合同、局部覆盖、项目依赖与待验项 | [开发任务地图](references/task-map.md) |
| 黄杖普通地面施法的输入、执行帧与星体退出 | [主动技能链](references/chain-active-skill.md) |
| Molehat 装备成员、夜视消费者、耗能与恢复 | [装备效果链](references/chain-equipment.md) |
| Portabletent 部署、收起与耐久交接 | [可收起建筑链](references/chain-deployable.md) |
| 普通猪人 normal/werepig 两态与恢复 | [阶段生物链](references/chain-creature-stage.md) |
| 角色、法术、装备、料理、UI 与资源 | [Skill 专题表](SKILL.md) |
| 模块职责、接口与失败恢复 | [复杂 Mod 架构](references/complex-mod-architecture.md) |
| 输入、预测、权威结算与取消退出 | [动作接入指南](references/action-lifecycle-architecture.md) |
| 静态检查、隔离专服与交付 | [测试与交付](references/testing-release.md) |
| 网页附件与云端交接 | [网页指南](references/web-chat.md) |

研究记录保留各自 Scope 和 Coding HOLD，按[准入规则](references/kb-retrieval.md)使用。本轮主要变化见[本轮说明](docs/phase15-unified-chains.md)。

项目自有材料使用[非商业 LICENSE](LICENSE)，商业用途需另获书面授权；第三方与有效历史 MIT 授权按各自条款处理。具体情形见[许可说明](docs/licensing.md)。
