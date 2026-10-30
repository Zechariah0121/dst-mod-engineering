# 760944 来源适配

本版 `v2026.10.30.1` 核验 DST **760944 / Steam build 26306684**。官方来源：[760944 更新公告](https://kleiforums.com/game-updates/dst/760944-r2829/)；[Steam 官方公告](https://steamcommunity.com/games/322330/announcements/detail/710038961706239761)。目标 `scripts.zip` SHA256：`abdbd017ad25e5020d74a401f76476ffe9e8cc5066159d499bec261f0ab1b51e`。

| 核对对象 | 结果 |
|---|---|
| Lua 文件 | 4095 个；相对 760178，4021 个字节相同、70 个变化、4 个新增、0 个删除 |
| 核心来源准备 | 253 个必需槽全部可恢复；2485 槽共恢复 2405，80 个可选 identity_range_cache 缺口保留 |
| 23 条登记机制研究、247 个引用 | 198 个文件及范围一致、47 个只确认范围、2 个旧范围变化、0 个缺失 |
| 新增待核验范围 | `AI-S043`：猪人 `SetNormalPig` 增加事件回调清理；状态从 `RANGE_ONLY` 改为 `CHANGED_UNKNOWN` |
| 延续待核验范围 | `AI-S045`：旧猪人 `normal` 初始化范围继续为 `CHANGED_UNKNOWN` |
| 传送来源 | `componentutil.lua` 与 760178 整文件一致，沿用上轮审核过的必要范围 |

本次仅登记新来源身份、更新使用说明与生成本机派生缓存，不改写知识正文、原证据版本、Scope、来源槽或准入规则。`source_epoch=759671` 仍表示历史证据基线；真实输入通过 `source_input_assessment` 标识为 760944。旧 760178 输入登记与[适配记录](version-760178.md)保留。

猪人的当前普通初始化仍在服务器分支调用 `SetNormalPig`，其中仍设置 `normalbrain` 与 `SGpig`；但本版还加入万圣夜转换路径，可异步调用 `MakeFrankenPig` 并切换 `frankenpigbrain`。因此普通初始化的局部核对不能扩大为整个生命周期始终使用同一 Brain，历史引用也不能自动改称新版已验证。相关未知随 `EXP-AI-001` 的来源评估暴露，原研究 HOLD 保留。

247 个引用的计数只涵盖已登记机制族；不把未登记候选一并计入已发布覆盖。范围字节相同与自动恢复成功都不证明依赖、游戏行为、联机或视觉兼容。本次未运行游戏。既有已准备缓存继续可用；新 ZIP 单独准备，不需要旧 ZIP，不放宽必需来源校验。
