# 作者材料维护与离线重建

统一入口是 `python -B -X utf8 scripts/rebuild_knowledge.py`。它读取显式基线与修改副本，输出可审阅的派生物和机器可消费的待复核清单。默认不修改活动知识包；只有下述明确的已审阅身份修复选项会更新限定的活动映射和承诺。不安装或发布。

```powershell
python -B -X utf8 scripts/rebuild_knowledge.py `
  --root "D:/path/to/repository" `
  --baseline "D:/path/to/unchanged-knowledge" `
  --knowledge "D:/path/to/edited-knowledge" `
  --output "D:/path/to/new-review-output" `
  --private-generators "D:/path/to/private-history/work"
```

输出必须尚不存在，并在所有输入目录之外。`--private-generators` 可省略；省略时仍生成目录、正文索引和待复核清单，历史映射状态明确标为 `NOT_REQUESTED`。脚本也支持 `scripts.rebuild_knowledge.main(argv)` 供其他命令透传。退出成功表示维护过程完成；是否可以采纳须读取 receipt 和 `pending-review.json`，尤其是 `release_blocked`、`generator_gaps`，不能只看进程退出码。

## 可读取、可构建的标题候选

在同一命令追加 `--stage-candidate "D:/path/to/new-external-candidate"`，默认允许 Native Core 的 title-only 修订，生成独立公共包。技术改动默认阻止 staging，并保留待复核清单。

stage 先证明整条记录除标题外完全相等，再复制现有构建器的公开文件清单、作者文档和再生目录，并只更新相关记录指纹、正文文件承诺、登记当前指纹、映射顶层承诺、包manifest和epoch清单。原 `published_record_sha256` 保留来历；合同角色、范围、原子、证据、声明与来源身份不变。源码slots、recipe及严格来源manifest保持原字节。新目录在完成校验后才从临时目录切换，不覆盖旧包。

输出的 `staged-candidate.json` 给出具体同步文件、证明和候选路径。可直接运行：

```powershell
python -B -X utf8 "D:/path/to/new-external-candidate/run_kb.py" read NC-N002-FINAL-01 --pointer /title
python -B -X utf8 "D:/path/to/new-external-candidate/run_kb.py" read NC-N002-FINAL-01 --pointer /claims/0
python -B -X utf8 scripts/build_release.py --source "D:/path/to/new-external-candidate" --out "D:/path/to/new-build-output"
```

候选可读、构建通过均不代表新技术语义得到批准。

## 经人工复核的单条 NSF 修订

在显式提供已填写的审阅决定和实际源码 ZIP 时，现有入口可为一条 Core 记录中的一个既有 NSF statement 更正生成独立候选。需要一个已有的直接方法合同和一个原引用范围。Scope、声明类型、证据引用、合同角色、声明身份和三轴状态保持。若原有 `gate_a.original_fact_statement_preserved` 为 true，决定必须显式批准随正文改为 false。该标志已为 false 时，决定使用 null，原值保留。多方法、多源码范围、额外 owner/sample/facet/覆盖或投影依赖、证据变更及其他族的技术更正走各自复核流程。

```powershell
python -B -X utf8 scripts/rebuild_knowledge.py `
  --root "D:/path/to/repository" `
  --baseline "D:/path/to/unchanged-knowledge" `
  --knowledge "D:/path/to/edited-knowledge" `
  --output "D:/path/to/new-review-output" `
  --stage-candidate "D:/path/to/new-external-candidate" `
  --reviewed-technical-decision "D:/path/to/review-decision.json" `
  --source "D:/path/to/scripts.zip"
```

决定为 `dst-author-technical-stage-review/1` JSON，`decision` 值为 `APPROVE_ISOLATED_CANDIDATE`。填写 `reviewer`、`rationale`、`record_id`、`claim_pointer`（如 `/claims/1`）、`old_record_sha256`、`new_record_sha256` 及 `gate_a_original_fact_statement_preserved`（`{"before":true,"after":false}` 或 null）。

- `source` 包含 `archive_sha256`、原 claim 自有的直接 `reference`（`artifact_path`、`sha256`、`pointer`）和 `range`（`path`、历史 `file_sha256`、`range_sha256`、`line_start`、`line_end`）。ZIP SHA-256 必须在包的来源承诺中，按原精确坐标验证已有 LF 范围；当前整文件允许与历史整文件不同。归档校验把审核绑定到实际来源输入，不改变历史来源范围。
- `maps` 以两个合同映射的包内路径为键，即默认 epoch 和 service 各一份。每个值包含原合同文件的 `contract_sha256`、原 `contract_symbol`、该 symbol 规格的 `contract_spec_sha256`、对应 `identity_path` 和原身份文件的 `identity_sha256`，以及 `identity_rows` 对象。该对象以 `/bindings/<索引>` 为键，以原行摘要为值，须覆盖改动 claim 的全部已有声明身份行。
- 文件哈希按原始字节计算。记录、合同规格、身份行和回执的 `canonical_decision_sha256` 按 UTF-8 JSON 计算，排序对象键、保留 Unicode 原字、使用紧凑分隔符（`maintenance_support.digest`）。审阅人和理由记载人工决定，哈希只绑定输入，不验证签名、权限或事实正确性。

成功时回执为 `STAGED_FOR_REVIEW`，`staged-candidate.json` 记录决定、验证来源和两套实际绑定。此时 `pending-review.json` 仍保留原发现，`release_blocked=true`、候选 `release_approved=false`。决定过期、错 ZIP、遗漏依赖或超出范围时输出 `candidate-stage-error.json`，不生成候选。技术 staging 与 `--repair-retired-private-identities` 分开执行。历史生成器可省略，提供时仅作诊断，发现额外未审依赖会阻止 staging。

`NC-N003-INT-03 /claims/1` 的首次采纳明确了 `PreviewAction` 的回退前提。只有 `sg.actionhandlers` 表存在、表中缺少当前动作的 handler，且动作非 instant 时，才请求进入 `previewaction`。表缺失会直接调用 `PerformPreviewBufferedAction`，条件失败和目标状态返回 nil 分别提前退出。该更正复核了 762172 中与历史引用字节一致的 `scripts/stategraph.lua:405–461`，并保留原历史 Scope 和引用。

## 输入边界

| 材料 | 性质和维护方式 |
|---|---|
| `knowledge/data/entries.json`、Native AI、Core 和注册机制文档的 `entries` | 作者正文。可在副本修改现有记录；保留 ID、文档成员及顺序。Core state_registry、source_artifacts 等文档元数据变化需另走明确审阅。 |
| `knowledge/FAMILY-REGISTRY.json` | 登记与审阅决定，包含文档成员、`published_record_sha256`、机制 `review` 及依赖。不会为通过校验自动刷新；新增/删除/移动 ID 走已有显式登记流程。 |
| `epoch-assets/*/contract_map.json` | 混合人工判断与推导。`contracts` 的指针、`pointer_roles`、`source_bindings`、`facet_scopes`、`claim_reference_bindings`、`owner_registry.basis`、`sample_rules` 等必须保留原决定或具体复核，不能从正文哈希恢复。 |
| `source_identity_map.json` | 原摘录与声明身份的派生结果，依赖确切源码字节及历史扩展。经人工复核的技术候选可重绑定已有引用，验证声明行和当前来源范围。身份不是行为证明，也不表示从新源码重新提取全部声明。 |
| 证据 JSON、review 文件、范围承诺、覆盖账本和发布元数据 | 本入口视为不可变输入；变动会明确拒绝，避免把证据修订伪装成正文纠错。 |
| `CATALOG.json` | 可从登记文档正文及状态再生；调用现有 `family_registry.catalog_rows/counts`。候选目录允许展示修改后正文，不修改正式登记承诺。 |
| `cache`、SQLite、来源摘录运行快照 | 本入口不扫描、不复制、不重建。仍由来源维护和索引流程管理。 |

内容哈希继续表示确切内容身份。默认临时正文指纹只用于目录、索引候选和不变原子证明。显式 staging 只在候选副本同步本次范围内的当前承诺，保留原始发布指纹。

## 输出与审阅

- `derived/CATALOG.json`：按现有四族登记成员重建，标题纠错直接反映在这里。
- `derived/author-record-index.json`：300 条完整作者记录、文件定位和内容哈希；用于离线检查修改后正文，**不是服务运行索引**。
- `pending-review.json`：具体 ID、修改 JSON pointer、技术分类、合同 symbol/atom/字段、身份映射行及 owner basis。只有 `/title` 修改被识别为标题文案；claim 中的任何文字变化都保守地要求技术复核。
- `preserved/`：当前合同映射和身份映射的原始字节，供比较和恢复，不冒充新语义产物。
- `candidates/`、`historical-receipt.json`：选择历史生成器后产生的未批准候选、规则审计、不变原子证明、丢弃对象、生成器指纹及与发布产物的结构比较。
- `maintenance-receipt.json` / `historical-error.json`：阶段状态与失败原因。显式 facet scope 等检查阻止历史生成时，目录和 pending 仍可供作者审阅，旧映射保留。

技术变化后，先审阅 pending 指出的具体对象，回到原证据与当前来源核实角色、范围及含义，再按已有登记/审阅流程采纳。候选即使生成成功也没有自动获得行为证明或发布资格。机制研究文档还需为新候选重新取得绑定确切候选字节的独立 review；本入口不会重绑旧 review 来绕过要求。

## 已接通的私有生成器范围

历史目录 `native-core-product-release-v27-natural-repair-20261025/work` 的原生成器未改动。适配器先导入当前公共服务模块，再调用历史函数，避免历史脚本默认导入旧 candidate 服务：

1. `build_map_v24.rebase_contract_map` → `build` → `preserve_verified_old_atoms`：确实执行原证据导航和语法角色推导，再保留有完整不变原子证明的旧人工决定。覆盖 187 条历史三族记录，不生成 113 条机制研究的人工审阅映射。
2. `build_source_identity.rebase_identity`：按完整 claim、引用、证据节点承诺检查并保留不变身份行；没有显式完整源码时不调用 `build/steam_declaration_rows` 宣称重新提取声明，也不重造历史 augmentation。

当前材料的两次基线运行完全重复。合同映射最终与发布原字节相同，但纯语法审计阶段行为绑定从 629 降到 596（另有 3 availability、116 未绑定）；保留阶段恢复已有审阅决定。因此这证明可重复审计并保留已有映射，**不证明能丢弃 seed 后从零再生全部映射**。

首次基线发现 5 个过期行：`NC-N003-INT-05 /claims/16` 的 `StateGraphInstance:GoToState`，原位置 `/bindings/1226..1230`。该公开claim已变成不含私有政策的UNK保留位，而5行仍绑定旧EI statement及旧自有引用。全库没有匹配旧statement的公开claim。真实授权762172源码仍在 `scripts/stategraph.lua:529` 声明此方法；过期的是与已撤下claim的绑定，不能因此否认API声明，也不能自动移绑其他claim或恢复私有正文。

已依据独立复核与明确授权，通过统一入口的 `--repair-retired-private-identities` 采纳 `MAINT-IDENTITY-CLAIM16-01`：精确备份并删除两份映射中的这5个绑定，保留其余5317行、范围及声明资料，自动更新source-epochs中的映射承诺。该选项只适用于这个已审阅修复，不是通用清理开关；数量、claim类型或身份不符合限定时拒绝。备份、前后SHA和精确行身份写入 `approved-identity-repair/repair-audit.json`。没有修改300条正文。修复后的基线生成保留5317行、0 gap，身份与合同候选均与当前输入结构相同。

## 实际隔离演练

证据位于工作区 `05-research-history/reader-evidence-maintenance-20261112/implementation/round3/`。`final-exact-rehearsal/` 保留修复前双基线和纠错演练；`identity-repair-adopted/` 保存修复备份、审计、源码核查与修复后0 gap基线；`baseline-repaired-repeat/` 保存修复后重复构建；`stage-title-verified/` 保存最终可读/可构建标题候选的元数据及实际读取结果；`stage-technical-final/` 保存拒绝技术stage和1个确切身份gap的演练。`exercise.py` 可对一个新输出目录复跑离线演练。

- 文案：`NC-N002-FINAL-01.title` 中 `Action意图链` 改成 `Action 意图链`。一次入口更新目录和完整正文索引；技术原子不变，保留映射有原子级证明，登记和旧 review 不被批量更新。
- 技术：同一记录 `/claims/0/statement` 将“按追加顺序生成 code”改成“不保证按追加顺序生成 code”。这是**未批准的含义变更模拟**，不是已核实的游戏事实。pending 指明 `AddAction`、`SetClientRequestedAction` 的 `/claims/0` 合同、相应身份行和 owner basis。历史 rebase 确实丢弃旧原子绑定并运行语法推导；技术候选仍待复核，旧映射字节完整保留。修复前有6个身份gap，修复后的演练仅此变更原子的1行待核。`--stage-candidate` 对技术改动明确返回BLOCKED，不生成可误认为完整的公共候选。

验证包括离线生成、重复字节比较和专属测试，不包含 DST 客户端、专服实际运行或新事实的语义验收。
