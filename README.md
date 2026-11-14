# DST Mod Engineering

`v2026.11.13.4` 面向《饥荒联机版》Mod 开发，提供按任务检索的知识、原版核查路径、开发辅助脚本与 MCP。[English](README.en.md)

当前共 **302 条登记知识：64 基础 + 13 Native AI + 110 Native Core + 115 机制研究**。默认检索现在直接发现并读取公共知识和任务指南；来源变化单独评估相关证据，作者更正由统一维护入口生成候选。见[公共读取](docs/public-reader.md)、[证据快照](docs/evidence-snapshots.md)和[作者维护](docs/author-maintenance.md)。

机制研究族包含 424 项 API 合同。

附主动技能、耗能装备、部署收起、两态生物、有期限效果和技能资源 HUD 的最小示例。任务入口见[任务地图](references/task-map.md)，本轮示例见[效果恢复与资源 HUD](docs/phase16-effect-and-resource.md)。

## 下载与开始使用

公开包从 [最新发行版](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest) 下载 [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest/download/dst-mod-engineering.zip)，对照同版 `SHA256SUMS.txt` 后完整解压。包内包含 Skill、唯一 `knowledge/`、开发脚本、自写示例、来源准备与 MCP。仓库内容分批发布，随包材料范围见[能力与适用范围](docs/public-limits.md)。

1. 将直接包含 `SKILL.md` 的完整目录放入 Agent 支持的技能位置，见[安装说明](docs/install-and-use.md)。
2. 调用 `dst-mod-engineering`，提供任务和 Mod 目录；需要核对当前行为时提供实际游戏源码；从 [Skill 专题表](SKILL.md) 选择入口。
3. 使用 Python 3.10+ 从包根生成默认公共 MCP 配置，无需先准备来源：

```text
python -B -X utf8 run_kb.py mcp-config
```

按客户端格式接入打印的配置，核对实际工具与一次默认查询及正文。公共阅读无需准备来源；需要当前证据时，按维护任务显式运行 `python -B -X utf8 prepare_sources.py --source "<scripts.zip绝对路径>"`。完整旧来源服务另需 SQLite FTS5；变更和重连见[源码维护](docs/source-compatibility.md)。

没有 MCP 也可用 `run_kb.py find` / `read` 定位并审阅公开记录，命令见[知识文件入口](docs/knowledge-integration.md)。检索准入、预算和来源身份统一见[检索策略](references/kb-retrieval.md)，当前源码适配见[源码维护](docs/source-compatibility.md)。

默认 `search_kb` 和 `get_context_bundle` 返回相关完整正文；`get_entry` 按 ID 阅读，`lookup_api` 按声明身份导航。命令行入口为 `run_kb.py review ID` / `run_kb.py review --api "符号"`，无需准备来源。预算不足时按 `continuation` 续读；公共阅读不授予 Coding 准入，详见[公共读取](docs/public-reader.md)。

## 按任务进入

| 任务 | 入口 |
|---|---|
| 从完整功能出发，找已有合同、局部覆盖、项目依赖与待验项 | [开发任务地图](references/task-map.md) |
| 黄杖普通地面施法的输入、执行帧与星体退出 | [主动技能链](references/chain-active-skill.md) |
| Molehat 装备成员、夜视消费者、耗能与恢复 | [装备效果链](references/chain-equipment.md) |
| Portabletent 部署、收起与耐久交接 | [可收起建筑链](references/chain-deployable.md) |
| 普通猪人 normal/werepig 两态与恢复 | [阶段生物链](references/chain-creature-stage.md) |
| 有期限伤害倍率、同分片存档与到期撤销 | [有期限效果链](references/chain-timed-effect.md) |
| 背包动作、服务器扣费、资源同步与 HUD 重建 | [技能资源与 HUD](references/chain-skill-resource-hud.md) |
| 角色、法术、装备、料理、UI 与资源 | [Skill 专题表](SKILL.md) |
| 模块职责、接口与失败恢复 | [复杂 Mod 架构](references/complex-mod-architecture.md) |
| 输入、预测、权威结算与取消退出 | [动作接入指南](references/action-lifecycle-architecture.md) |
| 静态检查、隔离专服与交付 | [测试与交付](references/testing-release.md) |
| 网页附件与云端交接 | [网页指南](references/web-chat.md) |

研究记录保留各自 Scope 和 Coding HOLD，按[准入规则](references/kb-retrieval.md)使用。源码匹配状态与知识准入分别保留，文本重建不等于语义审批。

项目自有材料使用[非商业 LICENSE](LICENSE)，商业用途需另获书面授权；第三方与有效历史 MIT 授权按各自条款处理。具体情形见[许可说明](docs/licensing.md)。
