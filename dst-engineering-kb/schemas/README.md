# Schema v0.1.1 与兼容策略

[entries.schema.json](entries.schema.json) 接受 0.1 / 0.1.1。附属注册表使用 [sources](sources.schema.json)、[claims](claims.schema.json)、[relations](relations.schema.json)、[case metadata](case-metadata.schema.json) 的独立 Schema。声明格式为 JSON Schema Draft 2020-12。

## 字段约定

| 字段 | 0.1.1 语义 |
|---|---|
| scope、scope_text | 保留原自然语言；两者相等 |
| scope_structured | game、cases、domains、evidence_modes、runtime_environments、sides；是适用范围/检索标签，不是实测记录 |
| sources[].locator | 保留原文本 |
| sources[].locator_structured | file、source_symbol、source_lines、report_section；已知起始行可单独记录，不虚构结束行 |
| sources[].role | direct_evidence / interpretation / supplementary_interpretation / historical |
| sources[].claim_id | 可选：把一条引用绑定到具体主张，支持撤回检查 |
| related | 旧 ID 数组，不删不重解释 |
| typed_relations | type + target；只精确化已明确关系 |
| CASE.details.static_failure_paths | 替代新写出的 confirmed_failure_cases |
| Failure 三字段 | static_path_confirmed、runtime_reproduced、runtime_validation_status，静态和实机严格分开 |
| Source.original_path / artifact_path | 前者追溯来源，后者为包内根相对路径；未打包外部源码后者为 null |

九种关系：supports、derived_from、illustrates、counterexample_of、mitigates、tests、corrects、supersedes、related。支持某种关系不代表本案例必有该种关系实例。source_lines 行号基于既有证据；本轮未重新阅读源码获取新定位。

## 向后兼容的方向

新版 Schema 接受归档 v0.1 数据，保留旧 scope、locator、related。0.1.1 写入要求结构化字段；CASE 新写入必须使用 static_failure_paths，旧字段仅用于读取历史。**这是对写死旧字段的消费者的局部 breaking change**，不是双向无损协议承诺。原严格 Schema 还可能拒绝新增字段；旧消费者可继续读取 history/v0.1/data/entries.json 并迁移后再切换新版。

## Source 与 Claim

KLEI-LOCAL-20260928 的 type=vanilla_source_snapshot，available_in_package=false；Steam build 等未知字段为 null。来源登记不等于源码已附包，也不代表新执行了原版对照。

REPORT-R5 整份报告没有失效；只有 CLAIM-CASE001-001 的指定旧因果判断 superseded。CORRECTION-CASE001-001 指向该 Claim，不删除旧报告或把同报告的其他证据一起否定。

校验器能拒绝 canonical 推荐仅由显式 superseded claim_id / historical 引用支撑。它不能识别任意自然语言改写、未标注 claim_id 的隐含沿用，不能证明报告的每句话都被语义审计。该限制是已知边界。

## 校验引擎

包内校验器用 Python 标准库实现当前 Schema 使用的约束子集，并做跨文件语义检查，不是通用 JSON Schema 实现。没有把第三方验证器未执行写成已执行。扩展 Schema 时需同步扩展校验器；其他系统也可使用 Draft 2020-12 引擎复核。
