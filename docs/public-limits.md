# 能力与限制 / Capabilities and limits

当前版本 `v2026.10.31.3` 带 227 条登记知识及 Skill（旧 187 条 + 40 条独立机制研究）。这表示可读取的知识范围，不代表全部已获 Coding 准入、源码证据全部随包或功能已实测；历史 187 条发行保留其原身份。

| 项目 | 实际边界 |
|---|---|
| 分发 | 唯一完整包包含 Skill、唯一知识目录、MCP 与来源准备工具；网页阅读按任务选择同包文件 |
| 公开材料 | 仅提供经审原创知识及必要证据片段；3 项项目政策与 1 项 EI 的私有情境公开隐藏为 `UNK`，不补造泛化事实，其他 NSF 原值、ID 与 Scope 保留 |
| Coding 准入 | 13 条 Native AI 默认十字段、任务子集最多 5 条；110 条 Core 与 40 条独立机制研究保留 Coding HOLD。文件可读、canonical 或可检索不解除限制 |
| 目录模式 | 两工具只做全部登记记录（当前版本 227 条）的目录导航与公开材料审阅；正文读取只允许 `purpose="review"`，不提供 Coding 上下文、已恢复源码证据或原版 Source/Identity Guards，不表示运行验证。预算不足时不截断正文，应按提示选择 JSON Pointer |
| 更新助手 | Skill 查库前检查一次明确绑定的 ZIP，尝试严格来源准备；相同输入快返、失败抑制重复尝试。不改游戏、客户端配置或现有连接，不保证任意更新兼容；失败后按当前任务核对新源码，旧知识按原 Scope 审阅 |
| 游戏源码 | 不附游戏 Lua 原文；`$dst_source_payload_slot` 不是已读源码。完整模式需从合法本地来源恢复缺失载荷 |
| 来源依赖 | 本版来源准备面向合法持有的 `761239 / build 26335394 scripts.zip`，不要求旧版源码；核心必需来源槽严格校验。机制研究按引用报告匹配、变化或缺失，缺口保留未知，不封锁其他研究条目或解除 HOLD。历史比较节点以 `metadata_only` 保留原来源信息 |
| 启动与缓存 | `auto` 对来源未准备或 `PACKAGE_CHANGED` 核验公开文件清单后进入审阅并报告原因；缓存损坏、无效激活及公开文件不可信仍报错。显式 `--mode catalog` 可审阅公开材料；来源准备完成后须重启 MCP 会话才能切换为九工具 |
| 版本 | 服务环境参数仅接受 `source_epoch=759671`，实际输入为 761239。原 23 条机制研究保留 759671、14 条保留 760944，本次新增 3 条保留 761239 证据身份；不提供服务环境切换。条目保留各自 Scope，不表示全库事实升级或游戏行为通过；不保证未来 ZIP 均可完整准备 |
| 客户端接入 | 打印配置、生成缓存或服务校验不等于客户端连接与实际查询成功；没有逐一完成所有 Agent/账户/云端环境自动加载测试 |
| 自然检索 | 已修复并定向验证 `Perishable:Perish` 回调／任务清理顺序漏查及方法排除边界；该结果不代表所有问法或所有条目均经过任务验收。空结果时可按统一目录复查，不能把无命中当作知识不存在 |
| 验证 | 静态检查、受控合约、专服行为、真实远端、视觉与音频分别报告；未执行项保留未测 |
| 开发辅助脚本 | `check_api.py` 只检查语法和部分直接方法声明；`dst_modtest.py` 仅支持 Windows 离线单分片，不替代洞穴/跨分片、Mod 组合或客户端效果 |

来源准备生成的 `cache/runtime/` 含本地游戏源码片段，不能随公开包上传。知识检索仍受角色、预算、Scope、缺失/延期和 HOLD 约束，见 [接入说明](knowledge-integration.md) 与 [检索策略](../references/kb-retrieval.md)。具体工程验收见 [测试与交付](../references/testing-release.md)。

Version `v2026.10.31.3` includes 227 registered records (historical 187 plus 40 restricted mechanism research records), without unrestricted Coding admission or complete original evidence. Published historical releases retain their own identity. Three project policies and one EI retain private context as `UNK`; other NSF values, IDs and Scope remain intact. Native AI Coding uses exactly ten fields and at most five records; 110 Core records retain Coding HOLD. Source preparation targets an authorized `761239 / build 26335394 scripts.zip` without older source. `source_epoch=759671` remains the evidence baseline. Required core ranges stay strict; mechanism references report exact/range-only matches or unknown/missing source without blocking every other research record or granting Coding admission; historical comparisons retain original metadata as `metadata_only`, not restored current-source evidence. This does not upgrade every knowledge claim to current-version validation. Two catalog tools support public review without Coding context or restored source evidence. Default `auto` permits public review after manifest validation for missing preparation or PACKAGE_CHANGED with a visible reason; cache damage, invalid activation and untrusted public data remain errors. Restart a connected catalog session after preparation. Game Lua is excluded and restored caches stay local. Printed configuration or validation does not prove client connection or real queries. Future versions, remote clients, visuals and audio need separate evidence.

更新助手的绑定、缓存与复核 sidecar 均留本地。准备成功后仍须重连并验证实际工具/来源；来源缺口不能由旧缓存补成当前版本证明。步骤见 [更新助手](../references/source-update-assist.md)。

本轮检索改进和新增特效研究范围见[阶段说明](phase6-retrieval-fx.md)。
