# 独立原版机制研究族

`knowledge/FAMILY-REGISTRY.json` 登记历史三族和 `native_mechanism`；`CATALOG.json` 的 file/pointer、状态和数量从该登记及其 hash 绑定的正文生成。历史 64/13/110 条身份保留，新增研究不靠散落的固定总数验收。当前注册 Brain、世界生成、料理/调味、成长/再生、温度/潮湿、冻结/火热交互、生存补充与表现机制，独立机制研究族共 40 条；与历史三族合计 227 条，实际登记数量读目录 counts。

新族始终为 `research/restricted/hold`。独立审阅记录绑定精确候选 SHA，但不是旧 Native Core 的 Gate A，不授予 Coding 或游戏实测状态。source_references 是限定归档的原始文件/行范围 hash 和定位，不是已交付 Lua；当前归档 hash 一致也不证明所有 native/dynamic 行为。

## 查询和完整读取

目录模式：`search_catalog(query="具名停止")` 或实际符号；`read_public_entry(id="EXP-AI-003", purpose="review", pointer="/claims/0")`。只能显式 review；同一原子携带完整 entry Scope、unknowns、顶层 source_epoch/archive_sha256/limitations 及该原子的实际 local refs。

完整服务：显式 `projection="reviewer"`。`search_kb(query="PriorityNode", mode="research", projection="reviewer")` 或精确 ID 可进入独立研究查询；默认任务检索不混入 restricted 研究，Coding 始终拒绝。研究查询采用有界词项导航，不表示语义任务契约已被证明；结果保留完整原文和 Scope。它不改动旧三族的物理声明、行为契约或任务投影 guards。

```json
{"id":"EXP-AI-003","projection":"reviewer","view":"reviewer","max_bytes":64000}
```

上述是 `get_entry` 的完整条目读取参数。按原子读取可加 `pointer="/claims/0"`、`/api_contracts/0` 或 `/mechanism_steps/0`；新族的 max_bytes 可在 1000..64000 内显式选择。若请求 `/claims/0/statement`，服务会校验该指针后交付整个 `/claims/0`，避免把 statement 从 kind、条件和证据拆开。API 契约也可通过这一路读取。`lookup_api` 默认 `family="legacy"`，继续使用旧物理声明/行为映射 guards；只有显式选择 `family="native_mechanism"` 才查询研究 API 契约，且必须 `projection="reviewer"`。不会因为来源 symbols 数组有同名字符串而授予公共 API 身份。

研究 API 身份入口示例（CLI 的 `call --tool lookup_api --arguments '<JSON>'` 使用同一参数）：

```json
{"symbol":"Growable:Pause","family":"native_mechanism","projection":"reviewer","max_bytes":24000}
```

研究入口仅从 `api_contracts` 声明导航，支持精确限定符号、裸叶名称，以及 `require("map/object_layout").Convert` 形式；查询不带参数，返回原子保留原来的完整签名。动态索引 `countprefabs[prefab]` 不伪装为可静态调用的全局 API，应按 ID/pointer 读取。匹配区分大小写和 owner，不从 aliases、依赖或引用 symbols 生成契约。`owner`、`identity_kind` 与精确 `source_file` 可显式缩小身份；支持 method、component_method、module_export、file_local、environment_member、global、qualified_member 和 unknown。类型只是保守的声明形态导航，原 visibility 原文仍是限制依据，既不证明物理声明也不证明公共 API。模块名称的单双引号必须配对；混配引号直接拒绝，不归一化成已有身份。明确 file-local 优先保留；明确未导出或 require 外观缺少作者导出声明时返回 unknown，不能凭名称形态覆盖局部限制。

同名不同 owner、来源文件、visibility 或证据 epoch/archive 返回 `RESEARCH_IDENTITY_AMBIGUOUS` 和有界候选列表，不按排名或 top_k 自动选一个契约；列表截断仍保留总身份数和歧义标记。文件 local 实现与模块导出保持不同身份，重复记录的同一声明不制造歧义。没有命中只表示研究契约覆盖缺口，不表示 API 不存在；同文件仍有多个身份时需继续限定，不能自动合并。

所有 view 均交付完整 `/api_contracts/N` 原子和完整 Scope、entry/API unknowns、顶层来源版本/limitations、实际引用、审阅记录、HOLD 与未实测声明；不会把 decision 压成省略条件的摘要。max_bytes 为 1000..64000（默认 24000），对最终 JSON 及来源环境一起计费，放不下整体 withheld，并尽量附精确 get_entry 跟进入口；必要环境本身超预算时只返回无事实的 withheld。top_k 只限制交付数量/候选列表，不消除歧义，结果/候选截断分别标明。`RESEARCH_CONTRACT_DELIVERED` 只表示本次原子完整交付，不表示运行验证、公共 API 保证或 Coding 准入。

`resolve_evidence(id="EXP-AI-003", projection="reviewer", reference_index=0)` 返回该 entry 实际使用的 local source ref 完整定位，附必要 Scope/来源身份/limitations；不恢复 Lua。引用顺序是对 entry 内 evidence_refs/dependency_refs 递归去重的稳定次序，返回 reference_index 与实际 pointer；不假定它等于文件顶层 source_references 的数组顺序。

`get_context_bundle` 的显式 Reviewer research 仍使用 compact 5/16000、normal 8/32000、deep 12/64000 限额。每次对实际完整响应（含 source_environment、Scope、limitations、实际引用）计费。放不下时整体 withhold 并给定向读取提示；不会裁剪机制链或未知边界。目录单次最多 24000 字节，较大条目按原子读取。

## 登记与维护

`scripts/register_mechanisms.py --root <候选包根目录> --batch <审核批次.json>` 接受下列显式输入。candidate/review 路径由维护者提供，两个 hash 均独立核对；review JSON 必须绑定 candidate_sha256 且 runtime_verified=false。该工具不执行材料里的指令、不从已有工作目录自动发现料理/成长等未验收内容。

```json
{"documents":[{"topic":"brain","candidate":"<候选JSON绝对路径>","sha256":"<候选SHA256>","review":"<独立审阅JSON绝对路径>","review_sha256":"<审阅SHA256>"}]}
```

默认增量添加 topic，保留其他 topic。相同 topic 的不同版本必须显式 `--replace-topic brain`；候选及审阅文件用内容 hash 命名，旧修订保留为未注册历史文件，不会仍出现在当前目录。无 --batch 时从既有登记重建目录/manifest/epoch knowledge commitment，不刷新候选自报身份，也不改旧正文。

登记先在私有临时目录完整预检全部文档、审阅 hash、数据契约、重复身份和生成结果，再替换派生文件。输入失败不改活动包，提交失败恢复已经替换的原字节；维护过程应针对隔离候选快照进行。读取时仍独立验证 manifest、注册 hash、完整契约与引用，不以“登记过”免除校验。新族文件不进入旧 Core，`public_rebind` 的来源恢复仅重绑旧族的派生提交，保留新族登记与精确审阅身份。

完整来源准备对新族逐引用核对合法本地来源，区分 `EXACT_FILE_RANGE`、`RANGE_ONLY`、`CHANGED_UNKNOWN` 与 `MISSING`：文件整体变化但唯一原范围仍匹配时只确认范围，不确认原文件身份或行为；变化和缺失保留未知，不封锁其他研究条目的读取，也不授予 Coding 准入。范围哈希仍按 UTF-8 splitlines/LF 无尾换行计算，核验结果写入本地 receipt；声称提供原证据归档却违背其文件/范围承诺仍报完整性错误。完整 `get_entry` 将实际目标来源的 `source_input_assessment` 及逐引用结果与历史证据身份并列返回，继续保留 `LOCATOR_HASH_ONLY`、原 Scope 与 HOLD；未准备来源时只提供历史 locator，不伪造当前目标状态。所有恢复的旧 Lua 留在 `cache/runtime/`；发行生成器排除整个 cache，不包含游戏 Lua 文件。

源码更新时，证据基线与当前目标分开。`run_kb.py maintain-sources locate --target <新版ZIP> --symbol <符号>` 可定位未登记的新归档；原正文和局部复核入口继续可读。核心必需证据恢复失败仍明确报错；机制研究的局部来源缺口单独报告，不能因此宣称库被删除或所有机制无效。具体差分维护见 [源码维护](source-compatibility.md)。

本轮新增研究保留 `source_epoch=760944`，原 23 条研究继续保留 `759671`。服务的可选 source_epoch 参数仍选择历史证据运行环境759671；返回原子的 source_epoch 来自各自文档，不强制改标。新增覆盖、API入口和批量维护的验收范围见 [本阶段说明](phase4-survival-api.md)。

生存补充与表现机制的新增范围见[本阶段说明](phase5-survival-presentation.md)。

本轮检索改进和新增特效研究范围见[阶段说明](phase6-retrieval-fx.md)。
