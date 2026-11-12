# 能力与适用范围

`v2026.11.12.5` 提供 300 条登记知识及开发工具，数量由 [CATALOG](../knowledge/CATALOG.json) 记录，分为 64 基础、13 Native AI、110 Native Core 和 113 机制研究。具体准入集中在[检索策略](../references/kb-retrieval.md)，按功能定位已有资料和缺口见[开发任务地图](../references/task-map.md)。

| 项目 | 适用范围 |
|---|---|
| 公开知识 | 保留经审正文与必要证据；3 项项目政策和 1 项 EI 的私有情境仍为 UNK，其余 NSF 原值、ID 和 Scope 保留 |
| Coding 准入 | Native AI 用十字段、每任务最多 5 条；110 条 Core 保留 Coding HOLD，113 条机制研究保持 research/restricted/hold，显式 Reviewer 读取 |
| 数量与覆盖 | 420 项 API 合同来自机制研究族的 api_contracts 数组；全库 API 总数、功能链完整性与源码覆盖率需另行盘点 |
| 文件与目录审阅 | 从目录定位再读正文；两工具模式用于显式 review，完整源码证据需本地准备 |
| 统一审阅 | 已准备完整服务中，显式 get_entry purpose=review / projection=reviewer 按 ID 读取，lookup_api family=all 统一导航后补读；完整对象与必需上下文共同计入预算，身份歧义、来源缺口和 HOLD 保留，见[知识读取](knowledge-integration.md) |
| 四条功能链 | 黄杖普通鼠标地面施法、Molehat 夜视正燃料记录、Portabletent 部署/收起与稳定形态、普通猪人两态各有有限链；链外变体和原生内部仍按各指南未知范围补查，见[本轮说明](phase15-unified-chains.md) |
| 来源与更新 | 更新助手维护明确绑定和本地缓存；目标身份、逐引用状态、完整性错误与服务环境见[源码维护](source-compatibility.md) |
| 客户端接入 | 按实际会话检查工具和任务响应；各 Agent/账户/云端环境分别验收 |
| 自然检索 | 结果受问法、过滤与预算影响，遗漏时按 ID 或完整对象续读；本轮统一入口与有限链见[本轮说明](phase15-unified-chains.md) |
| 运行证据 | 历史专服与客户端证据分别见[阶段 11](phase11-native-expansion.md)及[阶段 10](phase10-recovery-delivery.md)；四个新示例完成对应专服检查，其中三类完成存档重启。真实客户端与跨分片仍待验，范围见[本轮说明](phase15-unified-chains.md#验证状态) |
| 开发脚本 | `check_api.py` 检查语法和部分直接方法声明；`dst_modtest.py` 支持 Windows 隔离单分片专服，客户端和跨分片另验 |
| 游戏与私人材料 | 发行包不含游戏 Lua、私人项目或原始私人研究；恢复源码与本机状态留在本地 cache/ |

具体 Mod 按其目标与改动选择验证，区分源码核查、工具/合同测试、服务器行为、客户端视觉和听感，见[测试与交付](../references/testing-release.md)。
