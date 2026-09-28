# DST Engineering Knowledge Base v0.1.1

本版只修订数据结构、证据溯源与可移植性。64 条知识的正文语义、证据等级、置信度及六轮历史结论不重新分析。没有运行 DST 测试，没有推进 Case Study 002。

## 阅读入口

- [迁移报告](KB-v0.1.1-Migration-Report.md)、[CHANGELOG](CHANGELOG.md)、[验证说明](VALIDATION.md)。
- [CASE-001](cases/CASE-001-sora/README.md)、[全部 64 条知识](INDEX.md)、[维护政策](GOVERNANCE.md)。
- [Source Registry](SOURCES.md)、[Schema 与兼容说明](schemas/README.md)、[关系图](RELATIONS.md)。
- [ARP-DST-001](playbooks/ARP-DST-001.md)、[CASE-002 既有选样建议](CASE-002-AGENDA.md)（本轮未执行）。
- [Correction](corrections/CASE-001.md)、[被撤回的历史 Claim](corrections/claims.md)。

## 证据边界

| 条目 | 数量 | 边界 |
|---|---:|---|
| Klei Fact | 10 | E3，限定既有本机快照，Steam build 未知 |
| Case | 1 | 单一项目观察 |
| Pattern / Rule | 4 / 18 | 单案例候选，不是通用最佳实践 |
| Anti-Pattern | 9 | 其中 1 条为 E0 风险候选 |
| Failure | 4 | 静态路径；runtime_reproduced 全 false |
| Correction | 1 | 保留历史错误并显式撤回 |
| Decision / Test / ARP | 5 / 11 / 1 | 11 项业务测试均 not_run |

合计 64；E3=10、E1=53、E0=1。独立历史 Claim 节点不计为第 65 条知识。数据校验器的反例测试不属于 DST runtime validation。

## 机器入口和打包布局

- `data/entries.json`：canonical knowledge；`data/index.json`：检索索引。
- `data/sources.json`：来源注册；`data/claims.json`：历史 Claim 与撤回状态。
- `data/relations.json`：知识、Source、Claim 节点与 typed edges；同时保留 related。
- `schemas/`：entries、sources、claims、relations、case-metadata 的 Schema。
- `review-support/reports/`：第 4–6 轮报告的公开脱敏派生副本；原始报告仍仅在本机冻结版保存。
- `review-support/case-metadata.json`：既有证据提取的 CASE 元数据。
- `review-support/source-map.json`：公开来源 ID 与包内文件映射。
- `history/v0.1/`：原 canonical 数据、Schema、验收结果，保留旧字段与历史。
- `PACKAGE-MANIFEST.json`：除自身和 Python 缓存外所有包内文件的 SHA256 与字节数。

artifact_path 均相对知识库根目录；original_path 只作 provenance。第 1–3 轮独立报告缺失，没有补写。Klei 和 Mod 源码均不随包；外部源码 artifact_path=null。10 条 FACT 直接引用 KLEI-LOCAL-20260928，报告作为 supplementary_interpretation。

## AI / RAG 使用

按 ID、scope_structured 的 domains/sides/cases/evidence_modes 检索。Pattern 扩展 Rule、Decision、Anti-Pattern、Test；不要只返回一段正文。遍历 Correction 和 supersedes，排除已撤回 Claim 的有效证据资格。supports 是明确来源支持关系，不代表跨版本、跨项目或运行验证。

保留 scope / locator / related 供旧客户端读取，新增字段承载结构化信息。runtime_environments=[] 表示未声明已验证运行环境，不代表所有环境可用。新 Schema 可读 v0.1；旧严格 Schema 对新数据不保证兼容，详见 CHANGELOG。

## 可复核命令

在解压后的知识库根目录，使用 Python 3.10+：

```text
python -B tools/validate.py
```

默认只访问包内材料，无需原电脑或网络。公开副本不支持 `--check-external`；外部源码不随包。`data/validation.json` 是冻结版封包前的历史检查快照；公开版 Manifest 可在本目录重新验证，读者重跑上述命令可独立检查密封包。

维护时先在工作副本修改 canonical 数据，执行 render，再重建 Manifest 与 ZIP；不要在已封包目录运行写入命令后继续使用旧 Manifest。公开副本不包含一次性抽取和迁移工具。

## 公开派生版说明

本目录由本机冻结版经路径与私人标识脱敏导出；冻结版原样保留。64 条知识的 ID、证据等级、置信度、Correction 关系与技术结论没有重新修订。报告和历史记录为脱敏派生副本，不能声称与冻结版逐字节相同。`PUBLICATION-PROVENANCE.json` 仅用知识库相对路径记录原始与公开文件哈希，不公开本机路径。`logical:`、`case-study/`、`vanilla-snapshot/` 和 `analysis-report-location/` 均为发布用逻辑定位符，不代表实际文件系统路径。
