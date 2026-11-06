# 本地知识检索服务

本服务使用完整包内唯一的 `knowledge/`。版本与记录数分别见根目录 `RELEASE-MANIFEST.json` 和 `knowledge/CATALOG.json`；机制研究保持 `research/restricted/hold`。当前已核验输入及逐引用状态见[源码维护](../docs/source-compatibility.md)。正常完整使用，在完整包根目录用自己合法持有的源码准备：

```text
python -B -X utf8 prepare_sources.py --source "<实际 scripts.zip>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

不要求旧版源码。`source_epoch=759671` 仍为保留的证据基线，不把目标输入或全库结论改标为同一个证据版本。核心必需来源槽严格校验；机制研究按引用报告文件/范围匹配、变化或缺失，缺口保留未知，不封锁其他研究条目或解除 Coding HOLD。将输出配置接入客户端，核对九工具及一次实际查询；`mcp-config` 只打印配置，不修改客户端或安装后台服务。历史比较节点以 `metadata_only` 保留原来源信息。未来版本另做源码对照，见 [源码维护](../docs/source-compatibility.md)。

默认 `auto` 在准备有效时提供九工具；来源未准备或 `PACKAGE_CHANGED` 时，先校验公开文件清单再提供两工具审阅并报告原因。缓存损坏、无效激活或公开文件不可信仍报错。显式 `catalog` 只支持导航和公开审阅，不交付 Coding 上下文或已恢复源码证据。工具集在启动时固定，已连接目录模式的会话在准备后需重启，详见 [安装说明](../docs/install-and-use.md)。不能把源码占位模板当作完整运行数据。

`docs/mcp-tools.json` 由完整服务的实际 `mcp_server.TOOLS` 生成。修改工具后运行
`python -B dst-kb-service/export_mcp_tools.py`（在包根目录）；加 `--check` 可检查一致性，
服务测试也会逐字段核对发布 schema 与实际 `tools/list`。
