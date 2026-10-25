# DST 工程知识库

本目录包含187条公开知识：64条基础知识、13条 Native AI、110条 NativeCore。
按 [完整目录](CATALOG.json) 的 file/pointer 定向读取条目；`data/index.json`只索引基础64条。
不要整库注入默认提示词。条目三轴状态、NSF/RV/EI/REC/UNK分类、版本、Scope和Correction分别判断，Core Coding HOLD保留。

公开证据为经审片段与新哈希，不等于全部原始研究公开。4项依赖私有情境的政策/推断公开隐去并保留UNK。
JSON中的 `$dst_source_payload_slot` 是待本地恢复的游戏源码片段，不是已读原文；文件阅读不能把该槽当成证据。
MCP使用完整包根目录的 `prepare_sources.py` 与 `run_kb.py`，见 [接入说明](https://github.com/Zechariah0121/dst-mod-engineering/blob/v2026.10.25.1/docs/knowledge-integration.md)。
当前包仅提供759671运行环境；每条知识仍保留原来源范围，不能据此推断所有条目均适配759671。历史环境和旧目录可从Git历史取回。
项目自有内容采用随包LICENSE，游戏源码和私人原始资料不随包分发。

运行 `python -B tools/validate.py` 校验完整187条目录、三轴状态、证据引用、Correction和包内哈希。`data/legacy-integrity-baseline.json`只存64条基础知识及支持注册表的哈希，用于证明本次目录合并没有改写旧正文。旧导出说明 `PUBLICATION-PROVENANCE.json` 是历史来源记录；当前文件集合以 `PACKAGE-MANIFEST.json` 为准。
