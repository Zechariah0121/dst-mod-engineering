# 能力与适用范围

`v2026.11.12.3` 提供 296 条登记知识及开发工具，数量由 [CATALOG](../knowledge/CATALOG.json) 记录，分为 64 基础、13 Native AI、110 Native Core 和 109 机制研究。具体准入集中在[检索策略](../references/kb-retrieval.md)，按功能定位已有资料和缺口见[开发任务地图](../references/task-map.md)。

| 项目 | 适用范围 |
|---|---|
| 公开知识 | 保留经审正文与必要证据；3 项项目政策和 1 项 EI 的私有情境仍为 UNK，其余 NSF 原值、ID 和 Scope 保留 |
| Coding 准入 | Native AI 用十字段、每任务最多 5 条；110 条 Core 保留 Coding HOLD，109 条机制研究保持 research/restricted/hold，显式 Reviewer 读取 |
| 数量与覆盖 | 404 项 API 合同来自机制研究族的 api_contracts 数组；全库 API 总数、功能链完整性与源码覆盖率需另行盘点 |
| 文件与目录审阅 | 从目录定位再读正文；两工具模式用于显式 review，完整源码证据需本地准备 |
| 来源与更新 | 更新助手维护明确绑定和本地缓存；目标身份、逐引用状态、完整性错误与服务环境见[源码维护](source-compatibility.md) |
| 客户端接入 | 按实际会话检查工具和任务响应；各 Agent/账户/云端环境分别验收 |
| 自然检索 | 结果受问法、过滤与预算影响，遗漏时按目录 ID/原子指针继续读取；渐进读取与本轮扩展见[本轮说明](phase14-usage-retrieval.md) |
| 运行证据 | 连续专服重启与部分失败恢复见[阶段 11](phase11-native-expansion.md)，客户端与临时 Mod 清理见[阶段 10](phase10-recovery-delivery.md)；按具名场景使用，本轮未新增游戏运行验证 |
| 开发脚本 | `check_api.py` 检查语法和部分直接方法声明；`dst_modtest.py` 支持 Windows 隔离单分片专服，客户端和跨分片另验 |
| 游戏与私人材料 | 发行包不含游戏 Lua、私人项目或原始私人研究；恢复源码与本机状态留在本地 cache/ |

具体 Mod 按其目标与改动选择验证，区分源码核查、工具/合同测试、服务器行为、客户端视觉和听感，见[测试与交付](../references/testing-release.md)。
