# 本地知识检索服务

服务读取完整发行包中唯一的 `knowledge/`。版本与登记计数见根目录 `RELEASE-MANIFEST.json`、`knowledge/CATALOG.json`；准入与工具参数见[检索策略](../references/kb-retrieval.md)。指南以独立身份参加发现，登记知识仍为 300 条。

从包根打印默认客户端配置即可发现和阅读公共知识，无需准备游戏源码：

```text
python -B -X utf8 run_kb.py mcp-config
```

默认 `auto` 使用当前包的共享公共读取器，提供 11 工具。`search_kb`、`get_entry` 和 `lookup_api` 默认读取公共材料，工具 schema 的 projection 默认值为 `reviewer`。显式 `projection=coding`、`mode=coding`、`source_epoch` 及来源证据工具继续走原来源完整路径与准入守卫。`get_entry` 返回完整对象及其 Scope，预算不足时原样调用 `continuation`。`--mode catalog` 保留原两工具目录模式。

需要完整来源证据时，先绑定合法来源，再打印严格完整模式配置：

```text
python -B -X utf8 prepare_sources.py --source "<实际 scripts.zip>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

手动准备可用 `prepare_sources.py --source "<实际 scripts.zip>"`。`full` 启动仍要求有效完整 runtime，其默认发现也使用公共读取器。局部失配可建立独立 partial 证据快照，保留旧 runtime；逐引用状态、未核对项与旧来源身份分别记录。公共可读不授予 Coding 准入或当前来源验证。

接入后核对实际工具清单与一次自然问题查询。工具为 `search_kb`、`lookup_api`、`get_entry`、`resolve_evidence`、`get_related`、`get_klei_facts`、`get_tests`、`get_context_bundle`、`validate_kb`、`search_catalog`、`read_public_entry`。状态与重连见[安装说明](../docs/install-and-use.md)，来源身份及缺口见[源码维护](../docs/source-compatibility.md)。

`docs/mcp-tools.json` 由实际默认服务的 `public_reader.TOOLS` 生成。工具变更后从包根运行：

```text
python -B dst-kb-service/export_mcp_tools.py
python -B dst-kb-service/export_mcp_tools.py --check
```

服务测试逐字段比较发布 schema 与实际 `tools/list`。
