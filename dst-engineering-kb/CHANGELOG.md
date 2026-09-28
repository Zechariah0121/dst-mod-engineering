# CHANGELOG

## v0.1.1 — 2026-09-28

- First-class Klei provenance：加入 `KLEI-LOCAL-20260928`；10 条 FACT 直接引用原版快照，报告保留为补充解释。
- Portable artifact paths：打包的报告同时保留 original_path 与 artifact_path；外部源码 artifact_path 为 null。
- Typed relation support：新增九种关系；保留 related，不强行精确化不确定关系。
- Failure-case semantic cleanup：CASE 输出改为 static_failure_paths；四个 Failure 均保留 runtime_reproduced=false。
- Structured scope/locator support：增加结构化检索范围和定位，保留旧文本。
- Portable CASE-001 metadata：既有证据提取，未重新查版本、未重新分析源码。
- 保留历史 Claim，并连接 CORRECTION-CASE001-001 的 corrects / supersedes；增加显式被撤回证据检查。
- Schema、索引、关系图、校验器和可移植 Review ZIP 一起更新。

兼容性：新版 entries Schema 可读 0.1 和 0.1.1；related、scope、locator 继续存在。**存在局部破坏性写入变化**：CASE 的 confirmed_failure_cases 改名为 static_failure_paths；旧版严格 Schema/消费者不能保证读取新版新字段。原版 canonical 数据及 Schema 保存在 history/v0.1，旧消费者可用旧快照过渡。未承诺双向兼容。

## v0.1 — 初始验收版本

- CASE-001 initial extraction。
- 64 canonical entries；E3=10、E1=53、E0=1。
- 单案例模式候选；静态证据、原版源码事实与建议分层。
- Correction 保留后轮推翻前轮判断；测试候选未执行。
