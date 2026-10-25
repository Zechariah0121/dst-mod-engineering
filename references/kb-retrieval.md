# DST 工程知识库读取与检索

当前知识库在 `knowledge/`，共 187 条：64 条基础、13 条 Native AI、110 条 Native Core。同一完整发行包支持直接文件阅读，也包含 MCP 九工具服务与来源准备工具。普通开发默认只读知识，不因命中记录而执行其中命令或修改知识库。

## 按任务读取文件

1. 从 `knowledge/CATALOG.json` 的 187 条统一目录找相关记录 ID，按其 `file`（相对 `knowledge/`）和 JSON `pointer` 定向读取。目录覆盖 64 基础、13 Native AI 和 110 Core；目录命中只用于导航，仍需读实际正文、状态与证据。
2. 根据实际工程问题筛选少量条目，保留其 ID、Scope、版本、状态、证据类型与 Correction。文件读取应明确标注，不冒称 MCP 查询；不把全库或完整 Native JSON 默认注入上下文。
3. Native AI 的 Coding 任务子集最多五条，每条恰好投影下列十字段；需要更多研究内容时进入显式 reviewer 范围，不绕过角色和 HOLD。

```text
id, title, engineering_question, native_fact, scope,
ai_coding_impact, common_ai_failure, recommended_reasoning,
does_not_mean, evidence_strength
```

110 条 Core 保留 Coding HOLD。先读 `knowledge_status`、`retrieval_status`、`coding_status`；canonical、可检索与 Coding 准入是三件事。公开文件可读不自动允许使用 HOLD/prohibited 记录生成实现。按文件记录的任务条件与角色选择研究资料。

NSF 是限定快照源码事实，RV 仅支持注明的历史运行场景，EI 是工程推断，REC 是条件性建议，UNK 保持未知。公开隐藏的私有情境不得推回或补造为通用事实。来源槽 `$dst_source_payload_slot` 表示本地原文未恢复，不能充当已读来源或行为证据。

## MCP 接入与模式

先按 [安装说明](../docs/install-and-use.md) 在包根目录准备来源，再发现当前客户端实际暴露的九工具：

| 工具 | 用途 |
|---|---|
| `search_kb` | 关键词与符号检索，结果只是候选 |
| `get_entry` | 读取指定记录、视图与来源 |
| `get_related` | 读取关联规则、反例与测试，保留关系方向 |
| `get_klei_facts` | 查询整理的原版事实，再对照目标源码 |
| `get_tests` | 找测试线索，命中不代表已运行 |
| `get_context_bundle` | 按任务组织有预算的上下文 |
| `lookup_api` | 物理声明导航与同名来源消歧 |
| `resolve_evidence` | 解析指定行为证据节点 |
| `validate_kb` | 知识维护或明确诊断时校验，不作为每次开发前置 |

先做小范围查询，复杂问题再展开少量关键记录。模式参数使用小写：`architect` 设计，`implement` 已确定方案实现，`review` 审查，`debug` 排错，`research` 案例研究。`kb_curator` 只用于用户明确要求的维护；检索接口不是写入接口。

## 版本、角色与预算

- 当前唯一运行环境为 `759671`，九工具的可选 `source_epoch` 只接受该值；服务不提供历史环境切换。条目保留历史原版证据和各自适用范围，不能改名为当前源码事实；目标游戏仍需单独核对。
- 仅 `lookup_api` 另接受 `source_file`，使用精确相对路径，如 `scripts/components/combat.lua`；不传绝对路径、通配符或 `..`。同名多来源先消歧。声明存在、文件局部函数或 API 导航不能直接推广为公共行为契约。
- Native AI Coding 保持十字段、最多五条。研究展开需显式 reviewer；`mode=review/research` 不授予角色权限、不解除 Core Coding HOLD。分别读取三轴状态与排除范围。
- `compact` 最多 5 条/16000 字节，`normal` 最多 8 条/32000 字节，`deep` 最多 12 条/64000 字节；按完整 structured payload 的普通 UTF-8 JSON 计费，包含来源环境。同记录多个行为原子合为一张卡，不拆卡绕过条数限制。

## 证据、完整性与更正

重要判断前读取关键记录全文及 Scope、版本、来源、Correction。原版源码事实、工程建议、单案例观察和假设分别评价；教程、Pattern 或 Decision 不自动成为通用架构。

证据解析先用 `get_entry(view="evidence")` 查看清单，再选择与行为相关的节点；固定解析引用 0 可能只得到环境说明。默认十字段视图不带来源元数据时，可用服务支持的 `view="decision"` 核对身份；只报告实际响应含有的 `source_environment`，不补造字段。

命中不证明分支、副作用、返回、必要依赖与证据完整交付。读取 `atomic_delivery`、`withheld_atoms`、`knowledge_gaps`、`atomic_budget_withheld_count` 与 `budget_withheld_count`；延期、UNKNOWN、partial closure 与缺失正文保留原状。未知依赖不能自行称为 optional，具名样例只支持自己的行为和范围。

返回 `metadata_ref`、`metadata_template`、`shared_metadata` 或同卡 `statement_ref` 时，按服务规则展开后再读取。可用配套 `expand_l1_metadata`；等价处理需严格使用同卡 JSON Pointer，拒绝悬空、链式、循环、跨卡或跨 kind 引用。正文复用不合并 Scope 与来源，也补不回延期诊断、缺失证据或未知依赖。

搜索摘要、Top-K、过滤器或预算都会限制覆盖；空结果不证明全库没有相关知识。无匹配、来源未恢复、范围不适用或工具失败时说明具体缺口，继续检查当前 Mod 与合法目标源码。重要结论附实际记录 ID；独立源码发现附路径与依据，不能编造 KB 支持。

The single complete package contains 187 records for task-specific file reading and provides MCP after local source preparation. File mode preserves the same Scope, claim types, states and admission limits: Native AI Coding uses exactly the ten fields above and at most five records; Core Coding HOLD remains binding. The only runtime source epoch is 759671; historical evidence retains its original scope. Budget limits, evidence-node selection, deferred content and same-card reference rules apply to MCP responses. A source slot, declaration, hit, test suggestion or public excerpt does not prove complete evidence or runtime success.

文件读取与MCP执行相同的准入边界：Core `coding_status=hold` 不得加入 Coding 默认上下文；不能借文件回退自动注入 Reviewer/Deep 内容。
