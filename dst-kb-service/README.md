# 本地知识检索服务

当前服务版本0.3.2，使用包内唯一187条知识。正常完整使用，在完整包根目录用一份合法持有、匹配支持快照 `759671` 的 `scripts.zip` 准备来源：

```text
python -B -X utf8 prepare_sources.py --source "<759671 scripts.zip>"
python -B -X utf8 run_kb.py mcp-config --mode full
```

不要求旧版源码。将输出配置接入客户端，核对九工具及一次实际查询；`mcp-config` 只打印配置，不修改客户端或安装后台服务。历史比较节点以 `metadata_only` 保留原来源信息，不当作已读当前源码证据；当前证据范围仍严格校验。未来版本需要另做源码对照。

默认 `auto` 在准备有效时提供九工具，仅在来源未准备时提供两工具目录模式；缓存损坏或包版本变化时明确报错。显式 `catalog` 只支持导航和公开审阅，不交付 Coding 上下文、不验证源码契约。工具集在启动时固定，已连接目录模式的会话在准备后需重启，详见 [安装说明](../docs/install-and-use.md)。不能绕过准备步骤把源码占位模板当作完整运行数据。
来源版本、角色、HOLD与预算继续按实际工具和条目执行，见 [检索策略](../references/kb-retrieval.md)。

`docs/mcp-tools.json` 由完整服务的实际 `mcp_server.TOOLS` 生成。修改工具后运行
`python -B dst-kb-service/export_mcp_tools.py`（在包根目录）；加 `--check` 可检查一致性，
服务测试也会逐字段核对发布 schema 与实际 `tools/list`。
