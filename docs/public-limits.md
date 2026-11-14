# 能力与适用范围

`v2026.11.13.4` 提供 302 条登记知识及开发工具，数量由 [CATALOG](../knowledge/CATALOG.json) 记录，分为 64 基础、13 Native AI、110 Native Core 和 115 机制研究。具体准入集中在[检索策略](../references/kb-retrieval.md)，按功能定位已有资料和缺口见[开发任务地图](../references/task-map.md)。

| 项目 | 适用范围 |
|---|---|
| 公开知识 | 保留经审正文与必要证据；3 项项目政策和 1 项 EI 的私有情境仍为 UNK，其余 NSF 原值、ID 和 Scope 保留 |
| Coding 准入 | Native AI 用十字段、每任务最多 5 条；110 条 Core 保留 Coding HOLD，115 条机制研究保持 research/restricted/hold；默认公共 Reviewer 读取不授予 Coding 准入 |
| 数量与覆盖 | 424 项 API 合同来自机制研究族的 api_contracts 数组；全库 API 总数、功能链完整性与源码覆盖率需另行盘点 |
| 文件与目录审阅 | 默认 auto 提供 11 工具，无源码可发现和读取正文；显式 catalog 保留两工具，源码证据需独立准备 |
| 统一审阅 | 默认 get_entry / lookup_api 按公共 Reviewer 路径统一读取，无需准备源码；full 仅在启动时额外要求完整来源。完整对象与必需上下文共同计入预算，身份歧义、来源缺口和 HOLD 保留，见[知识读取](knowledge-integration.md) |
| 功能示例 | 黄杖、Molehat、Portabletent 与普通猪人见[四条功能链](phase15-unified-chains.md)。同分片定时伤害倍率与技能资源见[效果恢复与资源 HUD](phase16-effect-and-resource.md) |
| 来源与更新 | 按维护任务显式准备来源和本地缓存，partial 快照不阻断正文；旧完整缓存不代表新输入已验证，未检查项明确 UNKNOWN。目标身份、逐引用状态、完整性错误与服务环境见[源码维护](source-compatibility.md) |
| 客户端接入 | 按实际会话检查工具和任务响应；各 Agent/账户/云端环境分别验收 |
| 自然检索 | 结果受问法、过滤与预算影响，遗漏时按 ID 或完整对象续读；本轮统一入口与有限链见[本轮说明](phase15-unified-chains.md) |
| 运行证据 | [历史四条示例](phase15-unified-chains.md#验证状态)与[效果恢复和资源 HUD](phase16-effect-and-resource.md)各自列出专服、存档及客户端验收范围 |
| 开发脚本 | `check_api.py` 检查语法和部分直接方法声明；`dst_modtest.py` 支持 Windows 隔离单分片专服，客户端和跨分片另验 |
| 随包材料 | `examples/` 内包含明确列入分发清单的自写示例 Mod。原版 Lua、私人项目与原始私人研究留在本地，恢复源码与本机状态位于 cache/ |

具体 Mod 按其目标与改动选择验证，区分源码核查、工具/合同测试、服务器行为、客户端视觉和听感，见[测试与交付](../references/testing-release.md)。
