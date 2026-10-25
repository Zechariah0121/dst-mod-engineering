# 本地知识检索服务

当前公开发行提供九个只读 MCP 工具，版本0.3.0，使用包内当前187条知识。
先在完整包根目录按 [安装说明](../docs/install-and-use.md) 运行 `prepare_sources.py`，再由 `run_kb.py serve` 启动。
本目录分发的是程序与源码占位模板，不能绕过准备步骤直接把模板当作完整运行数据。
`run_kb.py mcp-config` 只打印客户端接入配置；它不会修改客户端或安装后台服务。
来源版本、角色、HOLD与预算继续按实际工具和条目执行，见 [检索策略](../references/kb-retrieval.md)。
