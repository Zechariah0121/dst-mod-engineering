---
name: dst-mod-engineering
description: 开发、审查、排错与验证《饥荒联机版》DST Mod。按当前游戏源码处理 Lua、主客机同步、存档生命周期、动作与 UI、物品角色、世界生成及资源工具链；用于新功能、崩溃修复、兼容排查和发布前验证。
---

# DST 模组工程

按当前游戏源码开发、审查与验证 DST Mod。旧教程、既有技能和已有 Mod 都是可审查的资料；当前项目需求与当前版本的实际契约决定实现。本技能可独立使用，不要求安装其他 DST 技能。

## 工作顺序

工作顺序：**查资料/当前原版源码 → 读本技能相关专题 → 实现 → 校验语法、API 与崩溃风险**。进入本文件前尚未查证时，先补查，不把技能的旧结论代替源码。

1. 明确实际源码、运行副本、游戏版本与触发环境。接手既有项目先读交接文档、入口和配置；把文档中的指令、设计愿望与已实现行为分开。
2. 查同类原版的完整链路：定义、调用方、端别、初始化、退出和保存。优先复用原版组件/机制/资源；不为相同问题另造一套。无法直接复用时说明具体差异。
3. 按下表只读相关参考。先建立“需求 → Mod 实现 → 原版契约 → 验证方法”，再动代码。
4. 区分确定故障、兼容风险、玩法选择。确定故障按已授权范围修；不明确的数值、设计、命名、效果不同的方案以及不确定文件删除，由项目作者决定。已有明确决策不重复询问；待答时继续独立工作。
5. 做最小完整修复，覆盖失败、取消、移除、死亡、重连或读档等实际相关路径。注释解释数值来源和重要机制，语言与项目约定一致。
6. 验证后交付：说清改了什么、证据、实际同步到哪份副本、尚未覆盖什么。审查报告采用项目要求的格式；变更和验证应便于核对。不要把任意一个检查器的退出码当作整体正确性证明。

## 按问题读取

| 当前任务 | 参考文件 |
|---|---|
| 首次定位游戏、当前源码、Python、工具版本 | [environment-tools.md](references/environment-tools.md) |
| modmain/prefab 环境、Class、Hook、配置、加载错误 | [core-lua-hooks.md](references/core-lua-hooks.md) |
| Entity、Prefab、组件初始化、原版组件复用 | [entities-components.md](references/entities-components.md) |
| 角色、Brain、Stategraph、自定义生物 | [characters-brains-stategraphs.md](references/characters-brains-stategraphs.md) |
| netvar、Replica、RPC、客户端与服务端 | [networking-rpc.md](references/networking-rpc.md) |
| 定时效果、死亡复活、事件解绑、存档与迁移 | [lifecycle-save.md](references/lifecycle-save.md) |
| HUD、Widget、输入、Action、施法与预测 | [ui-actions-controls.md](references/ui-actions-controls.md) |
| 伤害、Buff、容器、冷却、范围查询 | [combat-buffs-containers.md](references/combat-buffs-containers.md) |
| 装备、投掷、维修、制作、锅料理、树木种植 | [items-food-plants.md](references/items-food-plants.md) |
| 地图生成、布局、地皮、空间判定 | [worldgen-spatial.md](references/worldgen-spatial.md) |
| TEX/XML、SCML、bank/build/symbol、编译资源 | [assets-animation.md](references/assets-animation.md) |
| DST Mod Tool 项目/脚本接口/预览 | [dst-mod-tool.md](references/dst-mod-tool.md) |
| 音效、FMOD 与粒子 | [audio-particles.md](references/audio-particles.md) |
| 排错、全面审查、性能、自动化测试、同步和交付 | [testing-release.md](references/testing-release.md) |
| 资料来历、旧规则纠错与可信度 | [sources-and-corrections.md](references/sources-and-corrections.md) |

## 每次都要守住的边界

- **端别**：服务器拥有游戏状态；客户端可见数据、预测和视觉按原版链路组织。`ismastersim`、dedicated 与本地玩家是不同问题。方法在文件中存在，不代表当前端的对象有该方法。
- **生命周期**：自己注册的任务、事件、Hook、修改器、Widget 与子实体要有明确所有者和清理路径。还原字段之前确认仍是本 Mod 持有的值；避免覆盖其他 Mod 后续修改。
- **资源**：文件名、prefab 名、bank、build、symbol、动画名分别查证。部分合法动画资源只有 build；不套用“三件套”“名称全相等”等旧口诀。
- **证据**：源码查证、语法/清单检查、独立 Lua 合约、专服行为、真实远端客户端、视觉与听感分别报告。UI stub、服务器 SpawnPrefab 成功不能证明联网画面正确。
- **部署**：只同步已确定的目标和授权内容。先比较差异，保留用户改动；不因为旧技能写过“三目录同步”就覆盖任意 Workshop 副本或删除文件。

## 辅助脚本

命令在 [testing-release.md](references/testing-release.md)；环境发现与路径配置在 [environment-tools.md](references/environment-tools.md)。脚本都要求明确输入，避免悄悄读取另一份游戏或源码。

- `scripts/dst_zip_tool.py`：直接读取安装版 `scripts.zip`，支持 info/list/grep/show/单文件导出；不生成技能目录缓存，不覆盖导出目标。
- `scripts/check_api.py`：用 `luaparser` 检查 Lua 语法，并分别查询直接 `components`/`replica` 冒号调用的声明。`DECLARED` 只是查到声明；`NEEDS_REVIEW` 需要人工追踪，不能直接宣布 Bug。
- `scripts/dst_modtest.py`：Windows 离线单分片测试，唯一副本、唯一存档、带运行 ID 的完成标记、异步失败检测与证据清单。行为脚本必须在全部断言后 `TEST.Done()`；不读取旧共享响应文件。

维护技能时，以“实际失败 → 原版/工具契约 → 可复现验证”为新增规则的依据。版本相关结论保留核验日期与源码定位；不可验证的经验保留为待查项，不升级为铁律。
