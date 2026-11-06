# 本地知识检索服务

服务读取完整发行包中唯一的 `knowledge/`。版本与计数见根目录 `RELEASE-MANIFEST.json`、`knowledge/CATALOG.json`；准入与工具参数统一见[检索策略](../references/kb-retrieval.md)。

从包根绑定合法来源并打印客户端配置：

```text
python -B -X utf8 run_kb.py update-sources ensure --source "<实际 scripts.zip>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

上面的绑定步骤也可用手动流程替代：

```text
python -B -X utf8 prepare_sources.py --source "<实际 scripts.zip>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

按配置接入客户端，核对九工具和一次实际查询。默认 auto 根据准备状态选择完整服务或两工具公开审阅；状态与重连见[安装说明](../docs/install-and-use.md)，来源身份及缺口处理见[源码维护](../docs/source-compatibility.md)。

`docs/mcp-tools.json` 由实际 `mcp_server.TOOLS` 生成。工具变更后从包根运行：

```text
python -B dst-kb-service/export_mcp_tools.py
python -B dst-kb-service/export_mcp_tools.py --check
```

服务测试逐字段比较发布 schema 与实际 tools/list。
