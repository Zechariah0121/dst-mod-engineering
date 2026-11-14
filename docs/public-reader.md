# 公共知识读取

默认 `run_kb.py serve` 与 MCP 的 `Server.call` 从当前包的公共目录读取知识，不要求先准备游戏源码。302 条登记知识的身份仍由 `knowledge/CATALOG.json` 管理；从 `SKILL.md` 实际链接发现的 `references/`、`docs/` 指南使用 `guide:相对路径` 身份，单独计数，不成为新的 canonical 条目。

```text
python -B -X utf8 run_kb.py find "夜视 耗燃料 帽子"
python -B -X utf8 run_kb.py read EXP-CHAIN-GEAR-001 --pointer /claims/0
python -B -X utf8 run_kb.py review --api "Fueled:TakeFuelItem"
```

MCP 的默认投影为 `reviewer`。`search_kb(query=...)`、`get_context_bundle(task_description=...)` 按共享公共排名发现四族知识和任务指南，并在 `results[].reading.objects` 交付相关完整原子及其 Scope、更正、三轴状态和证据状态。`search_catalog` / CLI `find` 只提供导航，limit 默认 5、最大 30（显式旧 catalog 模式仍最大 20）。搜索总响应上限 64000 字节，无法放入的正文保留 gap 和可执行 `followup`；有命中但没有 objects 不代表已读正文。

公共查询执行 families、entry_types、statuses、knowledge_statuses、retrieval_statuses、coding_statuses、tags 及其 scope_logic；其他旧过滤维度明确返回 `UNSUPPORTED_PUBLIC_FILTER`，可显式指定来源环境使用旧合同。mode 只改变旧路径任务优先级，不授予准入；显式 mode=coding 同样保留旧 Coding 路径。

`get_entry(id=...)` 和 `read_public_entry` 使用相同读取器。`pointer` 为记录内 JSON Pointer；claim/API/step 子字段自动回到完整 owner，基础族同时携带完整 `details` 适用条件和测试执行状态。`max_bytes` 范围 1000–64000，整个普通 UTF-8 JSON 响应计入预算。大记录按完整对象续读，原样执行 `continuation.tool/arguments`。游标绑定内容、上下文、对象身份与所选 pointer，不能跨条目、改选字段或复用过期内容。

`lookup_api` 默认 `family=all`，只使用实际声明的身份字段，不从正文提及推断 API。支持完整 owner 身份和 `require("module").field`。裸名结果按 symbol、owner、精确 source_file、visibility、identity_kind 分组，各组保留记录级 followup。文件局部函数不提升为公开 API。`source_file` 仅接受精确 `scripts/...lua` 相对身份；错误 owner/file 返回空匹配，不借用同名叶子。结果为导航，继续读取具体合同。整个响应按 max_bytes 扣费，超预算只暂扣完整组。

公共文件仍核对 manifest 哈希；当前会话的文件变化、非法 pointer、错对象/过期 cursor 都报错。指南只能读实际登记的白名单文件，不能将任意路径作为 ID；其内容哈希也参与续读绑定。公共读取不会恢复私有源码槽，不授予 Coding 准入，不证明当前源码适用或游戏运行通过。

独立证据快照通过 `active_assessment(package_root)` 提供来源状态。每次阅读只附相关引用的 `reference_id/status` 摘要和 snapshot 身份。来源交付 archive_sha256、类型、输入序号，以及 observed_files 细表的数量/内容指纹、来源记录指纹和 snapshot 内 pointer；完整细表保留在已绑定快照，避免每个正文响应重复文件清单挤占预算。同一请求完整校验一次并冻结该快照，下个请求重新校验。未评估为 `NOT_ASSESSED`，损坏或包绑定失配为 `UNAVAILABLE` 且拒绝该证据展开。此时公共知识仍可读。公共正文的历史来源与独立当前检查分别呈现，不把历史运行缓存的 verified 状态贴到新来源。

显式 `projection="coding"` 通过旧来源完整性与准入适配；Core HOLD、研究限制、Native AI 十字段及最多五条规则保持原状。`resolve_evidence`、旧关系/测试/事实和维护工具仍通过来源校验服务，来源不可用时报机器错误。显式 `source_epoch` 也走旧证据环境，绝不把其 cursor 用于当前公共记录。`--mode full` 仍要求已准备的完整来源，但启动后默认查询也是当前公共读取；它不等同 Coding 投影。`--mode catalog` 保留旧两工具目录协议作为兼容入口。

实现复用 `PublicCatalog` 的公共清单校验/四族注册/排名，以及 `review_reader` 的完整 owner 与续读协议；未重写知识格式。旧 `Service` 的显式 Coding 逻辑保持独立，内部适配使用 `Server(config, public_default=False)`。

搜索索引在该进程第一次搜索时建立，后续查询共用。按 ID 或 API 读取可直接使用已经校验的目录和身份索引。
