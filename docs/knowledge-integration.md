# Skill 与知识库接入 / Skill and KB integration

版本 `v2026.10.30.2` 将 Skill 与 216 条登记知识（旧 187 条 + 29 条独立机制研究）串联分发，默认知识目录为 `knowledge/`。同一发行包包含来源准备工具与 MCP 的目录模式、完整九工具模式；文件读取和 MCP 使用唯一 `knowledge/`，旧版由 Git 历史保留。

## 不运行 MCP：按文件读取

先用 `knowledge/CATALOG.json` 的 **统一登记目录**定位相关 ID，再按每条的 `file`（相对 `knowledge/`）与 JSON `pointer` 读取少量实际记录。目录保留三个历史知识范围，并增添独立机制研究族，是导航而非已交付事实：

| 知识范围 | 文件入口 | 读取方式 |
|---|---|---|
| 64 条基础知识 | `knowledge/data/entries.json` | 按统一目录的 `file`、`pointer` 读取指定条目及相关更正 |
| 13 条 Native AI 知识 | `knowledge/data/native001/canonical-native001-ai-knowledge.json` | 按问题选择最多 5 条，Coding 默认只投影文件声明的十字段 |
| 110 条 Native Core 知识及状态 | `knowledge/data/nativecore/native-core.json` | 先核对三轴状态与 Scope；保留 Core Coding HOLD，不当作可直接实现的通用契约 |
| 29 条独立机制研究 | `knowledge/FAMILY-REGISTRY.json` 的 native_mechanism 登记 | 按目录 file/pointer 显式 Reviewer 审阅，保持 research/restricted/hold |

用 JSON 解析或定向读取提取所需记录，报告“知识文件读取”及实际记录 ID，不把它写成 MCP 查询。不要把完整 JSON 或全库加入默认提示词。原条目的 NSF、RV、EI、REC、UNK 类型分别读取；公开隐藏的私有情境仍为 `UNK`，不能由标题或关联推回正文。

公开证据只保留必要、经审的片段，并绑定公开路径与新哈希；不表示原始研究全部公开。`$dst_source_payload_slot` 是原版 Lua 的本地恢复槽，遇到它应记录来源缺口，继续用自己合法持有的当前源码核对，不能称为已解析证据。

## 运行 MCP：目录审阅与完整检索

正常完整使用按 [安装说明](install-and-use.md) 运行 `prepare_sources.py --source "<760944 scripts.zip>"`，再用 `run_kb.py mcp-config --mode full` 生成九工具配置。本版核验目标为 `760944 / build 26306684`；一份合法源码即可准备，不需要旧版源码。`source_epoch=759671` 保留为证据基线，不将全部结论升级为目标版本。核心必需来源槽继续严格校验；机制研究按引用报告匹配与缺口，缺口保留未知且不解除 HOLD。历史比较节点显式标记为 `metadata_only`，保留原快照、哈希、行范围与上游引用，不作为已读当前源码证据。准备只写 `cache/runtime/`，恢复的游戏 Lua 片段不属于公开再分发内容。

在包根目录运行 `python -B -X utf8 run_kb.py mcp-config`，把输出配置接入客户端。默认 `--mode auto` 对来源未准备或 `PACKAGE_CHANGED`，先核验公开文件清单再启动公开目录模式并报告原因：`search_catalog` 导航全部登记记录，`read_public_entry` 仅以 `purpose="review"` 审阅公开材料。目录命中不是正文已读；读取预算不足时不截断正文，应选择返回提示中的 JSON Pointer 继续定向阅读。

目录模式不提供 Coding 上下文、已恢复源码证据或原版 Source/Identity Guards，不表示任何运行验证，Core Coding HOLD 不变。已准备缓存损坏、无效激活及公开文件不可信时，`auto` 明确报错；`full` 保持严格。任意新版 ZIP 的独立定位及局部复核见 [源码维护](source-compatibility.md)。

服务的工具集在启动时固定。准备成功后重启 MCP 会话，默认 `auto` 才会切换到九工具；`mcp-config --mode full` 可生成锁定完整模式的配置。实际工具发现与一次任务查询仍需在客户端验证。工具、版本与预算见 [检索策略](../references/kb-retrieval.md)。

## 证据与维护

当前 Mod 与目标游戏源码仍是工程判断依据。保留来源 epoch、Scope、版本、Correction、缺失/延期与 Coding HOLD；检索命中、声明存在或文件可读都不等于完整行为已交付。仅在用户明确要求维护知识库时写库，检索服务本身是只读接口。

The single complete distribution includes the registered public records in one `knowledge/` tree, source preparation and MCP. For full use, this version targets one authorized `760944 / build 26306684 scripts.zip`; older source is not required. `source_epoch=759671` remains the evidence baseline, without upgrading every claim. Required core ranges remain strict; mechanism references report matching or unknown/missing source separately, without granting Coding admission. Historical comparisons retain original metadata as `metadata_only`, not restored current-source evidence. File reading follows selected catalog `file` and JSON `pointer` values and reports record IDs as file access. Default `auto` permits two public review tools after manifest validation for missing preparation or PACKAGE_CHANGED, with a visible reason; damaged cache, invalid activation and untrusted public data remain errors. Explicit `catalog` enables public review without Coding context, restored source evidence or original Source/Identity Guards. Restart a connected catalog session after preparation to obtain nine tools. Native AI Coding uses the declared ten-field projection and at most five records; Core Coding HOLD remains binding. Preserve Scope, types, versions, corrections, gaps and admission limits. Source slots are not evidence already read; restored source stays local in `cache/runtime/`. Future game versions need separate source comparison.

文件读取与MCP执行相同的准入边界：Core `coding_status=hold` 不得加入 Coding 默认上下文；不能借文件回退自动注入 Reviewer/Deep 内容。

独立原版机制研究族使用 `research/restricted/hold`，仅显式 Reviewer 研究请求或 ID 展开；Coding/default restricted 路径不注入。原子读取保留完整 Scope、顶层来源身份/limitations 与局部证据闭合，超过预算整体 withheld。登记、来源验证及参数见 [机制研究族](native-mechanisms.md)。
