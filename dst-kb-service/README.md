# 本地知识检索服务

当前服务版本0.3.1，使用包内唯一187条知识。在完整包根目录运行 `run_kb.py serve`：未准备来源时提供两个公开目录工具；合法来源准备完成并核验后提供完整九工具。工具集在启动时确定，准备后需重启会话，详见 [安装说明](../docs/install-and-use.md)。
公开目录模式只支持导航和显式审阅，不交付 Coding 上下文、不验证源码契约。完整模式需运行 `prepare_sources.py`，不能绕过准备步骤把源码占位模板当作完整运行数据。
`run_kb.py mcp-config` 只打印客户端接入配置；它不会修改客户端或安装后台服务。
来源版本、角色、HOLD与预算继续按实际工具和条目执行，见 [检索策略](../references/kb-retrieval.md)。

`docs/mcp-tools.json` 由完整服务的实际 `mcp_server.TOOLS` 生成。修改工具后运行
`python -B dst-kb-service/export_mcp_tools.py`（在包根目录）；加 `--check` 可检查一致性，
服务测试也会逐字段核对发布 schema 与实际 `tools/list`。
