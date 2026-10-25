# KB v0.1.1 Migration Report

本轮仅进行数据结构与可移植性修订。64 条 canonical knowledge 保持原有语义；未重新分析小穹源码，未重写历史报告，未进行任何 DST runtime validation，未继续 Case Study 002。

## Changed

| 修订项 | 结果 |
|---|---|
| Klei 一等 Source | KLEI-LOCAL-20260928 登记为 vanilla_source_snapshot；10 条 FACT 直接引用，报告保留补充解释角色 |
| 快照上下文 | available_in_package=false；Steam build、发行版本、整包 ZIP 哈希未知，为 null；保留已有文件指纹 |
| 可移植路径 | 3 份第 4–6 轮报告在冻结版原样放入；公开版提供脱敏派生副本于 review-support/reports；公开版仅保留包内路径和逻辑来源 ID；新元数据独立注册 |
| Typed relations | 9 种类型的 Schema 与目标检查；原 related 不变；图含 Source、Claim、知识三类节点，共 351 条边 |
| Failure 语义 | CASE 使用 static_failure_paths；4 个 Failure 明确 static_path_confirmed=true、runtime_reproduced=false、runtime_validation_status=not_runtime_reproduced |
| Scope | 保留原 scope，添加 scope_text 与 6 维 scope_structured；范围标签不构成运行证据 |
| Locator | 保留文本，并支持 report_section、source_lines、source_symbol、file；精度不超过既有证据 |
| CASE portable metadata | name/version/author/date/count/hash/测试状态从既有 CASE 提取，没有联网补查 |
| Correction | 保留 CORRECTION-CASE001-001；增加独立历史 CLAIM-CASE001-001，corrects / supersedes 精确指向旧判断 |
| 版本记录 | 新增 CHANGELOG、原 v0.1 数据与 Schema 归档；原 Review ZIP 保留 |
| Validator | Schema、跨文件关系、显式撤回证据、独立语义对比、指纹、包清单和反例回归一起检查 |

旧 Claim 的 E1 仅说明它来自单案例观察；status=superseded 明确撤回，不作为有效当前证据。REPORT-R5 整份报告未被撤回。

## Unchanged

- Canonical IDs、顺序、正文语义、旧来源记录、证据等级、置信度保持不变；校验器重新对照 history/v0.1，剔除允许的结构字段变化后比较，未只接受迁移脚本自报结果。
- 64 条：10 Fact、1 Case、4 Pattern、18 Rule、9 Anti-Pattern、5 Decision、4 Failure、1 Correction、11 Test、1 ARP。
- E3=10、E1=53、E0=1；无 E2/E4/E5。单案例 Pattern 不升级，E0 God Manager 风险不升级为既成故障。
- 四条 Failure 未实机复现；11 条业务 Test Candidates 保持 not_run；本轮 runtime 执行数为 0。
- 第 4–6 轮报告在冻结版按原字节复制；公开版为脱敏派生副本；第 1–3 轮独立报告仍缺失，未重建。旧错误判断保留在历史报告及独立 Claim。
- 参考项目与原版文件仅做已有指纹比对，未重新读取业务逻辑进行分析；参考项目不修改，原版/Mod 源码不打包。

## Backward Compatibility

新版 entries Schema 接受历史 v0.1 数据；scope、related、locator 保留。存在明确的局部 breaking change：0.1.1 的 CASE 输出字段改名为 static_failure_paths，旧严格消费者还可能拒绝新增字段。不能宣称旧程序无修改可读取新包。

新读取器可同时读取两版；旧消费者可继续使用 history/v0.1 下的原数据与 Schema，修改字段读取后再迁移。新 canonical 不保留容易误解的 confirmed_failure_cases，历史归档保留其原名。

## Verification

| 检查 | 验证方法与结果 |
|---|---|
| Schema validation | 当前 5 类 Schema + 旧 0.1 entries 输入，包内标准库检查器通过 |
| ID uniqueness | 知识、Source、Claim 分别唯一且命名空间不冲突 |
| Index consistency | ID、顺序、类型计数、检索字段、文档锚点一致 |
| Source integrity | 4 个包内来源的 SHA256；本机原报告、Mod 项目指纹及已有原版文件指纹比对通过 |
| Internal links | 包内链接和锚点全部可达；活动 Markdown 无本机绝对路径链接，原路径作为 provenance 保留 |
| Typed relation target existence | 351 条图边的类型与目标有效，原 related 及明确 typed edges 均已导出 |
| Correction target existence | corrects / supersedes 指向存在的历史 Claim；显式唯一撤回证据反例被拒绝 |
| Manifest SHA256 | 封包清单按文件名集合、字节数、SHA256 复核；清单自身不自引用 |
| Evidence level sanity | 分布保持 10/53/1；E2 单案例与无实测 E4 反例被拒绝 |
| Runtime validation sanity | Failure 不冒充实测；Test 不冒充已执行；反例均被拒绝 |
| 迁移语义 | 独立对比旧正文及旧来源记录，允许结构变化以外差异为 0 |
| 反例回归 | 12/12 检出；它们是知识库校验测试，不是 DST 业务测试 |
| 可移植性 | ZIP 在另一目录解压后，以默认模式重跑校验，不访问 original_path |

data/validation.json 为封包前检查快照，manifest=not_present 表示当时尚未生成清单。封包后以及搬迁后的实际结果输出到 ZIP 旁的 validation.json；包内内容不为写回最终结果而再次修改。实际链接数、清单文件数和 ZIP SHA256 见该最终记录。可执行 `python -B tools/validate.py` 自行复核。

## Remaining Limitations

1. Correction 防护针对显式 claim_id / historical 引用；自然语言改写或遗漏 claim_id 的隐含沿用不能自动识别。当前检查不冒充完整语义审核。
2. 外部 Klei / Mod 原源码未随包。可移植检查能核对登记和包内报告，不能独立重做源码验证；快照 Steam build 未知，不宣称最新版本适用。
3. 本机指纹比对是材料完整性检查，不是重新确认源码行为，也不升级 E1/E3 为 E4。
4. 标准库 Schema 检查器只支持当前使用的约束；没有运行第三方通用 Draft 2020-12 引擎。扩展 Schema 时应同步更新或接入通用实现。
5. Typed relations 只精确化语义明确部分，其余保留 related；六维 scope 是保守检索标签，未覆盖所有未来领域本体。
6. 搬迁验证在 Windows 不同目录进行；未宣称 Linux/macOS 或 DST Host/Client/Dedicated 的运行验证。
7. 历史第 1–3 轮独立报告缺失；未来补齐应登记真实来源，不能由现有摘要倒造原报告。

本轮交付止于 v0.1.1 的结构迁移与验证。

[公开发布注：以上迁移结论记录冻结版本地历史。此公开副本已经脱敏，报告与历史文件不再与冻结版逐字节相同；没有重新修订知识结论。]
