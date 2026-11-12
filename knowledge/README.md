# DST 工程知识库

包含300条登记知识，分为64条基础、13条 Native AI、110条 Native Core和113条机制研究。完整数量见 [CATALOG.json](CATALOG.json) 的 `counts`，登记文件见 [FAMILY-REGISTRY.json](FAMILY-REGISTRY.json)。机制研究族另有420项 `api_contracts`，全库 API 总数与源码覆盖率尚待独立盘点。

按完整功能找路可读[开发任务地图](../references/task-map.md)。完整服务用 `get_entry(purpose="review", projection="reviewer")` 或 `run_kb.py review ID` 按 ID 读对象，按 API 用 `lookup_api(family="all", projection="reviewer")` 或 `run_kb.py review --api "符号"` 导航后补读。pointer/cursor、continuation与环境要求见[接入说明](../docs/knowledge-integration.md)。公开目录仍可无需来源地用 `find/read`，或按目录 `file`/`pointer` 文件读取；`data/index.json` 和 [INDEX.md](INDEX.md) 保留基础64条的既有视图。条目三轴状态、NSF/RV/EI/REC/UNK分类、版本、Scope和Correction分别判断。110条 Core 保留 Coding HOLD，113条机制研究保持 research/restricted/hold，显式 Reviewer 读取；完整规则见[检索策略](../references/kb-retrieval.md)。

本轮四条具名功能链及自写示例见[统一读取与功能链](../docs/phase15-unified-chains.md)，范围限定各自输入、实际消费者、退出和必要恢复。具名示例的有限专服与独立进程恢复结果单独记录，研究准入与 `runtime_verified=false` 保留，真实客户端与跨分片仍待验。

公开证据为经审片段与新哈希，不等于全部原始研究公开。4项依赖私有情境的政策/推断公开隐去并保留UNK。
JSON中的 `$dst_source_payload_slot` 是待本地恢复的游戏源码片段，不是已读原文；文件阅读不能把该槽当成证据。
MCP使用完整包根目录的 `prepare_sources.py` 与 `run_kb.py`，见[接入说明](../docs/knowledge-integration.md)。本轮已核验的来源输入为762172 / Steam build26474873；其他合法目标源码按逐引用结果评估。服务环境参数仍仅接受 `source_epoch=759671`，各条知识保留自身证据版本与Scope。来源输入、服务环境和逐引用匹配的具体含义见[源码维护](../docs/source-compatibility.md)。历史比较节点保留原身份及 `metadata_only`，来源未准备时默认可用目录审阅。历史环境和旧目录可从Git历史取回。
项目自有内容采用随包LICENSE，游戏源码和私人原始资料不随包分发。

在本目录运行 `python -B tools/validate.py` 校验当前完整目录、三轴状态、证据引用、Correction和包内哈希。`data/legacy-integrity-baseline.json`只存64条基础知识及支持注册表的哈希，用于核对旧正文完整性。旧导出说明 `PUBLICATION-PROVENANCE.json` 是历史来源记录；当前文件集合以 `PACKAGE-MANIFEST.json` 为准。
