# DST KB Service

本地、只读的 DST 工程知识检索服务。Python 3.10+ 标准库与 SQLite FTS5，无需 API Key；不依赖特定模型。完整仓库中的 `../dst-engineering-kb` 是经过脱敏的 v0.1.1 公开派生包，不是 Mod 源码。

## 快速验证

在本目录执行，`python` 换成自己的 Python 3.10+：

```text
python -B dst_kb_cli.py --config config.example.json validate
python -B dst_kb_cli.py --config config.example.json status
python -B dst_kb_cli.py --config config.example.json call --tool get_entry --arguments "{\"id\":\"PATTERN-WORLD-001\"}"
python -B -m unittest discover -s tests -v
```

最后一条查询示例适用于常见终端；终端对 JSON 引号的处理可能不同，也可以通过 MCP 使用同一个工具。`validate` 验证知识数据，不执行游戏测试。`status` 会按需创建派生 SQLite 索引；索引在本目录 `cache/`，不会写入知识库。`config.example.json` 的相对路径以配置文件位置解析。

## 接入 Agent 的 stdio MCP

使用完整仓库；只下载技能 ZIP 不包含知识库和服务。将以下通用配置转换为客户端实际支持的格式。替换为本机绝对路径，保留参数数组，不把整个命令塞成一个字符串：

```json
{
  "mcpServers": {
    "dst_kb": {
      "command": "/absolute/path/to/python",
      "args": [
        "-B", "/absolute/path/to/dst-mod-engineering/dst-kb-service/dst_kb_cli.py",
        "--config", "/absolute/path/to/dst-mod-engineering/dst-kb-service/config.example.json",
        "serve"
      ]
    }
  }
}
```

Windows 路径可在 JSON 内使用正斜线；不要原样使用示例占位路径。Codex 使用 TOML `mcp_servers.dst_kb` 表及相同的 `command`、`args`；其他客户端可能使用上述 JSON，也可能有专用界面，以它实际接受的格式为准。这里的示例不会替用户改全局配置。

服务由 MCP 客户端启动，不提供 HTTP 端点，不暴露网络监听端口。网页聊天上传资料也不会因此获得本机 MCP 访问能力。

连接后先确认工具列表，再调用 `get_entry`，参数为 `{"id":"PATTERN-WORLD-001"}`。工具可见、查询成功、Agent 在真实任务中主动选择工具是不同检查，不能互相替代。

## 工具与边界

| 工具 | 用途 |
|---|---|
| `search_kb` | 关键词与结构化条件检索摘要 |
| `get_entry` | 读取完整条目、来源和纠错警告 |
| `get_related` | 按方向遍历 typed relations |
| `get_klei_facts` | 仅检索原版源码事实；仍受快照范围限制 |
| `get_tests` | 返回测试候选，不代表执行通过 |
| `get_context_bundle` | 按设计、实现、审查、排错等模式组装有限上下文 |
| `validate_kb` | 数据完整性维护检查，不应每次开发都运行 |

完整参数见 [工具定义](docs/mcp-tools.json)，使用策略见 [Skill 检索专题](../references/kb-retrieval.md)。

服务使用关键词、中文相邻字组合、领域别名、类型偏好及关系辅助排序；没有向量模型或自动语义证明。词语相近可能产生无关结果，Agent 必须筛选适用范围；非空结果不证明某个领域已经覆盖。失败模式是提出排查假设的依据，不是对新项目 Bug 的直接证明。

Schema 校验实现当前数据契约所需的子集，未知关键字会拒绝；不是完整 JSON Schema 引擎。Correction 检查可追踪显式 Claim 引用，无法自动判定所有自然语言是否沿用了旧错误。服务不执行知识包自带的 Python 校验器，不提供 canonical 写入接口。

更换知识库时设置 `DST_KB_PATH` 或另建配置；索引位置可用 `DST_KB_INDEX` 覆盖。运行中知识变更会拒绝继续返回过期结果，需要重新建立索引并连接。索引是可重建缓存，不应提交到 Git。
