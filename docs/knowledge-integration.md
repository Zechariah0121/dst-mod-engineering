# Skill 与知识库接入 / Skill and KB integration

本版将 Skill 与当前 **187 条公开知识**串联分发，默认知识目录为 `knowledge/`。完整包、独立 Skill ZIP 与网页阅读 ZIP 都带知识文件；完整包另含来源准备工具与现代 MCP 九工具服务 `0.3.0`。仓库中的旧版兼容目录不作为当前 KB 入口。

## 不运行 MCP：按文件读取

先读 `knowledge/data/index.json` 的基础记录索引，再按任务定位：

| 知识范围 | 文件入口 | 读取方式 |
|---|---|---|
| 64 条基础知识 | `knowledge/data/index.json` | 按索引的 `path`、`anchor` 读取指定条目及相关更正 |
| 13 条 Native AI 知识 | `knowledge/data/native001/canonical-native001-ai-knowledge.json` | 按问题选择最多 5 条，Coding 默认只投影文件声明的十字段 |
| 110 条 Native Core 知识及状态 | `knowledge/data/nativecore/native-core.json` | 先核对三轴状态与 Scope；保留 Core Coding HOLD，不当作可直接实现的通用契约 |

用 JSON 解析或定向读取提取所需记录，报告“知识文件读取”及实际记录 ID，不把它写成 MCP 查询。不要把完整 JSON 或全库加入默认提示词。原条目的 NSF、RV、EI、REC、UNK 类型分别读取；公开隐藏的私有情境仍为 `UNK`，不能由标题或关联推回正文。

公开证据只保留必要、经审的片段，并绑定公开路径与新哈希；不表示原始研究全部公开。`$dst_source_payload_slot` 是原版 Lua 的本地恢复槽，遇到它应记录来源缺口，继续用自己合法持有的当前源码核对，不能称为已解析证据。

## 运行 MCP：先准备来源

按 [安装说明](install-and-use.md) 在完整包根目录运行 `prepare_sources.py`，提供合法持有的 `759671` 及所需历史源码。当前单份 `759671 scripts.zip` 仍缺 13 种旧范围，涉及 9 个文件。缺少必需来源时不启动部分库，也不放松原准入；此时仍可按上述方法阅读公开知识。

准备只写 `cache/runtime/`；其中恢复的游戏 Lua 片段不属于公开再分发内容。完成准备后，用 `run_kb.py mcp-config` 生成客户端配置，在实际客户端验证工具发现与一次任务查询。九工具、版本与预算见 [检索策略](../references/kb-retrieval.md)。

## 证据与维护

当前 Mod 与目标游戏源码仍是工程判断依据。保留来源 epoch、Scope、版本、Correction、缺失/延期与 Coding HOLD；检索命中、声明存在或文件可读都不等于完整行为已交付。仅在用户明确要求维护知识库时写库，检索服务本身是只读接口。

All three distributions include the current 187 public records in `knowledge/`; only the full package adds source preparation and the modern nine-tool MCP service. File mode reads a task-specific subset from the three entries above and reports record IDs as file access. Native AI Coding uses the declared ten-field projection and at most five records; Native Core Coding HOLD remains in force. Public evidence is limited to reviewed excerpts. Source slots are missing local Lua payloads, not evidence already read. MCP requires authorized current and historical sources first; one current ZIP is insufficient. Restored source stays in `cache/runtime/` and must not be publicly redistributed. Preserve Scope, claim types, versions, corrections, gaps and admission limits in either mode.

文件读取与MCP执行相同的准入边界：Core `coding_status=hold` 不得加入 Coding 默认上下文；不能借文件回退自动注入 Reviewer/Deep 内容。
