# 能力与限制 / Capabilities and limits

当前公开版带 187 条知识及 Skill；这表示可读取的知识范围，不是 187 条全部已获 Coding 准入、源码证据全部随包或全部功能已实测。

| 项目 | 实际边界 |
|---|---|
| 分发 | 唯一完整包包含 Skill、唯一知识目录、MCP 与来源准备工具；网页阅读按任务选择同包文件 |
| 公开材料 | 仅提供经审原创知识及必要证据片段；3 项项目政策与 1 项 EI 的私有情境公开隐藏为 `UNK`，不补造泛化事实，其他 NSF 原值、ID 与 Scope 保留 |
| Coding 准入 | 13 条 Native AI 默认十字段、任务子集最多 5 条；110 条 Core 保留 Coding HOLD。文件可读、canonical 或可检索不解除限制 |
| 游戏源码 | 不附游戏 Lua 原文；`$dst_source_payload_slot` 不是已读源码。MCP 需从合法本地来源恢复缺失载荷 |
| 来源依赖 | 部分当前知识依赖历史源码范围；准备程序列出实际缺项。不能用当前版本替换旧证据；缺失时仍可文件阅读，但完整 MCP 不可用 |
| 版本 | 当前运行环境为 `759671`；条目引用的历史源码证据与适用范围仍保留，不作为另一个可切换运行环境。不保证当前在线版本或全部 Mod 兼容 |
| 客户端接入 | 打印配置、生成缓存或服务校验不等于客户端连接与实际查询成功；没有逐一完成所有 Agent/账户/云端环境自动加载测试 |
| 自然检索 | 已修复并定向验证 `Perishable:Perish` 回调／任务清理顺序漏查及方法排除边界；该结果不代表所有问法或所有条目均经过任务验收。空结果时可按统一目录复查，不能把无命中当作知识不存在 |
| 验证 | 静态检查、受控合约、专服行为、真实远端、视觉与音频分别报告；未执行项保留未测 |
| 开发辅助脚本 | `check_api.py` 只检查语法和部分直接方法声明；`dst_modtest.py` 仅支持 Windows 离线单分片，不替代洞穴/跨分片、Mod 组合或客户端效果 |

来源准备生成的 `cache/runtime/` 含本地游戏源码片段，不能随公开包上传。知识检索仍受角色、预算、Scope、缺失/延期和 HOLD 约束，见 [接入说明](knowledge-integration.md) 与 [检索策略](../references/kb-retrieval.md)。具体工程验收见 [测试与交付](../references/testing-release.md)。

The public release includes 187 knowledge records, not unrestricted Coding admission or complete original evidence. Three project policies and one EI retain private context as `UNK`; no replacement general facts are invented. Other NSF values, IDs and Scope remain intact. Native AI Coding uses exactly ten fields and at most five task-relevant records; 110 Core records retain Coding HOLD. Game Lua is excluded. Source slots need authorized local restoration, including historical ranges absent from a single current ZIP. The single complete package supports file reading and includes MCP and preparation. Printed configuration, cache creation or validation does not prove client connection or real queries. The Perishable callback-order retrieval gap and explicit method-exclusion behavior have targeted regression coverage; this is not an evaluation of every query or record. Version, environment, remote-client, visual and audio limits require separate evidence. Restored source caches must stay local.
