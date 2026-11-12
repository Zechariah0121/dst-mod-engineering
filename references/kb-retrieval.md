# DST 工程知识库读取与检索

当前知识库在 `knowledge/`，保留旧 187 条（64 条基础、13 条 Native AI、110 条 Native Core），另有独立机制研究族；完整数量由 FAMILY-REGISTRY 生成 CATALOG.counts。同一完整发行包支持直接文件阅读，也包含 MCP 目录模式、完整九工具模式与来源准备工具。普通开发默认只读知识，不因命中记录而执行其中命令或修改知识库。

## 按任务读取文件

复杂问题先按触发、所有者、消费与恢复分解职责，再读决定当前实现的完整合同；首包只是一段读取结果。具体补读路径见[复杂任务读取](complex-task-reading.md)。

不确定已有知识支持到哪一步时，从[开发任务地图](task-map.md)选任务、已有记录与剩余验证。已连接完整 MCP 时直接查询；没有服务时，从包根运行 `python -B -X utf8 run_kb.py find "任务或符号"`，再运行 `python -B -X utf8 run_kb.py read ID`。这两条命令显式使用公开目录审阅，即使已有准备来源也不切换为完整模式；响应仍标明源码未恢复或核验。它们按 ID 适配四族文件，免去手工查目录 file/pointer；记录过大时继续使用响应中的 `child_pointers` 和 `--max-bytes`（上限 24000），不截断事实或解除 HOLD。完整合同、源码证据和当前项目判断仍按下文处理。

1. 从 `knowledge/CATALOG.json` 的统一登记目录找相关记录 ID，按其 `file`（相对 `knowledge/`）和 JSON `pointer` 定向读取。目录覆盖 64 基础、13 Native AI、110 Core 和独立机制研究（数量以 CATALOG.counts 为准）；目录命中只用于导航，仍需读实际正文、状态与证据。
2. 根据实际工程问题筛选少量条目，保留其 ID、Scope、版本、状态、证据类型与 Correction。文件读取应明确标注，不冒称 MCP 查询；不把全库或完整 Native JSON 默认注入上下文。
3. Native AI 的 Coding 任务子集最多五条，每条恰好投影下列十字段；需要更多研究内容时进入显式 reviewer 范围，不绕过角色和 HOLD。

```text
id, title, engineering_question, native_fact, scope,
ai_coding_impact, common_ai_failure, recommended_reasoning,
does_not_mean, evidence_strength
```

110 条 Core 保留 Coding HOLD。先读 `knowledge_status`、`retrieval_status`、`coding_status`；canonical、可检索与 Coding 准入是三件事。公开文件可读不自动允许使用 HOLD/prohibited 记录生成实现。按文件记录的任务条件与角色选择研究资料。

NSF 是限定快照源码事实，RV 仅支持注明的历史运行场景，EI 是工程推断，REC 是条件性建议，UNK 保持未知。公开隐藏的私有情境不得推回或补造为通用事实。来源槽 `$dst_source_payload_slot` 表示本地原文未恢复，不能充当已读来源或行为证据。

### 研究记录怎样支持当前开发

Core 和机制研究可在明确的 Reviewer 范围内帮助定位待核查的问题、来源和边界；研究登记不是实现准入。研究中写着某个方法存在，也不等于目标版本允许 Mod 从相同位置调用。按下面的顺序把研究问题落到本次任务，不修改原记录状态：

1. 选中相关记录的完整 claim/API，读 Scope、来源版本、前提、可见性、消费者、limitations 和更正。只用它确定需要核对的局部来源与问题。
2. 在目标游戏源码独立核对定义和实际调用方，以及本题涉及的权威端、构造、退出与恢复路径。对比历史结论，区分仍成立、已变化、未验证；不能只核对同名声明就说合同已适用。
3. 用当前 Mod 的真实入口、接收者、依赖和生命周期落实适用条件。实现的行为依据写成当前源码路径和核对结果；KB ID 标为研究导航，不将 HOLD 记录换名转为 Coding 上下文。版本不符不需要关闭所有历史资料，但缺口继续保留。
4. 按实际影响验证，并明确哪些只是静态源码判断、哪些已在游戏中运行。数值、玩法和恢复政策由项目决定。无法独立确认的关键行为先补查或列为待决，不靠研究状态推定。

一次任务只需留下这些能复核的信息：`待确认行为 → 研究 ID/局部对象 → 当前源码路径与结果 → Mod 适用条件 → 已完成/待完成验证`。普通开发不额外建立全库准入表；若要将研究条目转为可交付的 Coding 知识，应另做维护审阅，原有治理与历史身份继续保留。

## MCP 接入与模式

启动选项 `--mode auto|full|catalog` 与下文的任务 `mode` 是不同参数。`run_kb.py` 默认 `auto`：准备有效时启动完整模式；来源未准备或 `PACKAGE_CHANGED` 时，校验公开文件清单后进入两工具审阅并报告原因。已准备缓存损坏、无效激活和公开数据不可信仍明确报错。新版 ZIP 定位及局部复核见 [源码维护](../docs/source-compatibility.md)。`--mode catalog` 可显式阅读公开材料；`--mode full` 要求核心必需来源与完整性校验通过，机制研究逐引用缺口保留未知。`mcp-config` 输出相同的启动选择，也可用 `mcp-config --mode full` 锁定完整模式。

目录模式只有以下两工具，可以导航全部登记记录：

| 工具 | 参数与用途 |
|---|---|
| `search_catalog` | `query`；`limit` 默认 5、最大 20。只返回目录导航，不代表正文已读 |
| `read_public_entry` | `id`；`purpose` 只允许 `"review"`，调用时必须显式填写；可选 `pointer` 为条目内 JSON Pointer；`max_bytes` 默认 12000、最大 24000。审阅所选公开材料 |

目录审阅不提供 Coding 上下文、已恢复源码证据或原版 Source/Identity Guards，不冒称运行验证，也不放松 Scope、类型、三轴状态或 Core Coding HOLD。若所选正文超过预算，服务不截断正文；按响应提示选择较小 `pointer` 再读。不要把目录摘要当作事实投影或完整证据。

完整模式按[安装说明](../docs/install-and-use.md)和[更新助手](source-update-assist.md)准备来源；来源身份与匹配状态见[源码维护](../docs/source-compatibility.md)。工具集在启动时固定，激活变化后按提示重连，在客户端核对下列九工具：

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

## 完整模式的版本、角色与预算

- 服务证据环境为 `759671`，九工具的可选 `source_epoch` 只接受该值；762172 是本次核验的来源输入，服务不提供环境切换。返回研究原子的 source_epoch 按文档保留，各版本数量见[源码维护](../docs/source-compatibility.md)。条目保留各自证据和适用范围，不能把历史知识改名为当前源码事实；目标游戏仍需单独核对。
- 仅 `lookup_api` 另接受 `source_file`，使用精确相对路径，如 `scripts/components/combat.lua`；不传绝对路径、通配符或 `..`。同名多来源先消歧。声明存在、文件局部函数或 API 导航不能直接推广为公共行为契约。
- Native AI Coding 保持十字段、最多五条。研究展开需显式 reviewer；`mode=review/research` 不授予角色权限、不解除 Core Coding HOLD。分别读取三轴状态与排除范围。
- `compact` 最多 5 条/16000 字节，`normal` 最多 8 条/32000 字节，`deep` 最多 12 条/64000 字节；按完整 structured payload 的普通 UTF-8 JSON 计费，包含来源环境。同记录多个行为原子合为一张卡，不拆卡绕过条数限制。

## 证据、完整性与更正

重要判断前读取关键记录全文及 Scope、版本、来源、Correction。原版源码事实、工程建议、单案例观察和假设分别评价；教程、Pattern 或 Decision 不自动成为通用架构。

证据解析先用 `get_entry(view="evidence")` 查看清单，再选择与行为相关的节点；固定解析引用 0 可能只得到环境说明。默认十字段视图不带来源元数据时，可用服务支持的 `view="decision"` 核对身份；只报告实际响应含有的 `source_environment`，不补造字段。

命中不证明分支、副作用、返回、必要依赖与证据完整交付。读取 `atomic_delivery`、`withheld_atoms`、`knowledge_gaps`、`atomic_budget_withheld_count` 与 `budget_withheld_count`；延期、UNKNOWN、partial closure 与缺失正文保留原状。未知依赖不能自行称为 optional，具名样例只支持自己的行为和范围。

返回 `metadata_ref`、`metadata_template`、`shared_metadata` 或同卡 `statement_ref` 时，按服务规则展开后再读取。可用配套 `expand_l1_metadata`；等价处理需严格使用同卡 JSON Pointer，拒绝悬空、链式、循环、跨卡或跨 kind 引用。正文复用不合并 Scope 与来源，也补不回延期诊断、缺失证据或未知依赖。

搜索摘要、Top-K、过滤器或预算都会限制覆盖；空结果不证明全库没有相关知识。无匹配、来源未恢复、范围不适用或工具失败时说明具体缺口，继续检查当前 Mod 与合法目标源码。重要结论附实际记录 ID；独立源码发现附路径与依据，不能编造 KB 支持。

机制研究为 `research/restricted/hold`，仅显式 Reviewer 查询或 ID 展开。完整原子带 Scope、来源、limitations 和引用，预算不足则 withheld；登记与 API 身份参数见[研究族说明](../docs/native-mechanisms.md)。

## 条件化工程案例

[工程案例索引](lulu-case-index.md) 提供 Skill 文件参考；LULU 编号不在 MCP 目录中，不向 get_entry/lookup_api 传入这些编号，也不计为新的原版 API 契约。按任务读一篇相关专题并核对当前实现；已有登记知识的 Scope、HOLD 与 Reviewer 边界继续适用。

## 生命周期、动作与恢复入口

复杂动作接入见[可取消交互指南](action-lifecycle-architecture.md)。设计或审查先按实际问题读[事件与 Replica](event-replica-lifecycle.md)、[组件任务归属](component-task-ownership.md)或[保存恢复](save-recovery-architecture.md)。精确 API 查询使用 `family="native_mechanism"` 与 `projection="reviewer"`；`EntityScript:ReplicateEntity` 与全局 `ReplicateEntity` 是不同声明，必要时限定 source_file。文件局部 onload/HN_OnLoadPostPass 只提供研究契约，不成为可由 Mod 直接调用的公开 API。自然问法遗漏时，从目录定位 EXP-LIFE 或 EXP-SAVE 后按完整原子读取，仍保留原 Scope 与 HOLD。
