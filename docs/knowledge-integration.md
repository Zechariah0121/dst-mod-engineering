# Skill 与知识库接入

`v2026.11.12.5` 的 Skill、文件阅读和 MCP 共用唯一 `knowledge/`，共 300 条登记记录。Skill 按工程问题选专题，目录与服务负责定位知识。从完整功能找入口时，先读[开发任务地图](../references/task-map.md)中相应任务的已有合同、局部边界、项目依赖和下一步验证。

## 按文件读取

从 `knowledge/CATALOG.json` 找相关 ID，再按 `file`（相对 knowledge 根）与 JSON `pointer` 读取实际记录。报告所读 ID 和“文件读取”。

也可在包根使用简短命令，先找记录，再读具体正文或合同原子。

```text
python -B -X utf8 run_kb.py find "装备 耗能" --limit 5
python -B -X utf8 run_kb.py read EXP-GEAR-001
python -B -X utf8 run_kb.py read EXP-GEAR-001 --pointer /api_contracts/2 --max-bytes 24000
```

这两个命令调用公开目录审阅入口，使用包内材料，无需准备游戏源码。响应保留 Scope、来源缺口与 HOLD；超预算时按提示选择较小指针继续读。源码准备与完整 MCP 的证据读取按下文接入。

| 知识范围 | 文件入口 |
|---|---|
| 64 条基础 | `knowledge/data/entries.json` |
| 13 条 Native AI | `knowledge/data/native001/canonical-native001-ai-knowledge.json` |
| 110 条 Native Core | `knowledge/data/nativecore/native-core.json` |
| 113 条机制研究 | 由 `knowledge/FAMILY-REGISTRY.json` 的 native_mechanism 登记定位 |

正文的类型、Scope、版本、更正与状态和事实一起读取。Coding 投影、Reviewer 研究及预算统一按[检索策略](../references/kb-retrieval.md)执行，文件读取采用同一准入规则。

机制研究族共有 420 项 `api_contracts`。这一数量按登记记录内的合同项计数，全库 API 盘点和源码覆盖率仍需独立确定。

## 通过 MCP 读取

按[安装说明](install-and-use.md)绑定来源并接入客户端。完整模式有九工具；目录模式提供 `search_catalog` 导航和显式 `purpose="review"` 的 `read_public_entry`。超预算时按提示选择较小的原子指针；来源准备改变激活后按助手提示重连，再检查实际工具、来源与一次查询。

完整九工具新增显式统一审阅选择。按 ID 调用 `get_entry(id=..., projection="reviewer", purpose="review")`，按 API 调用 `lookup_api(symbol=..., projection="reviewer", family="all")`，使用返回的 `results[].followup` 读取完整对象。调用方无需先选择知识族或查底层登记文件。现有默认 Coding、旧调用形状和 HOLD 继续约束各自路径。

```text
python -B -X utf8 run_kb.py review EXP-FISH-001
python -B -X utf8 run_kb.py review --api "Moisture:ForceDry" --max-bytes 24000
python -B -X utf8 run_kb.py review EXP-FISH-001 --pointer /api_contracts/2 --max-bytes 64000
```

读取响应中的 `objects`、`complete`、`whole_value_delivered` 和 `withheld_reason`。有 `continuation` 时原样执行其中的工具与参数，完整对象、Scope 和证据导航按同一总字节预算交付。cursor 为绑定记录与环境的无状态页位置，也可直接指定 pointer 读取完整 owner。64 KB 上限仍无法交付时转为完整文件阅读。具体字段、API 歧义和旧接口兼容见[四族完整对象审阅](../references/kb-retrieval.md#四族完整对象审阅)。

`review ID`、`review --api` 和绑定 cursor 均要求已准备的完整来源环境，准备不可用时明确报错。原 `find/read` 继续提供独立的公开目录入口及其来源边界。

源码身份、逐引用匹配和缺口处理集中见[源码维护](source-compatibility.md)。普通使用只读知识；维护正文须有明确任务授权。

## 工程参考

[复杂 Mod 架构](../references/complex-mod-architecture.md)连接模块职责，[动作接入](../references/action-lifecycle-architecture.md)贯穿输入到退出；[工程案例索引](../references/lulu-case-index.md)提供条件化反例与验证线索，LULU 编号属于文稿导航，不传给 MCP。

[阶段 8](phase8-lifecycle-persistence.md)介绍事件、任务和恢复，[阶段 9](phase9-action-closure.md)介绍实体移除与动作执行；[阶段 10](phase10-recovery-delivery.md)补充重复恢复和测试清理；[阶段 11](phase11-native-expansion.md)扩展五类常用原版机制；[阶段 12](phase12-practical-native.md)补充 UI、生物 AI、农作与船体开发；[阶段 13](phase13-practical-expansion.md)扩展装备、投射物、建筑、巢穴、世界事件与海钓，并补充渐进读取、效果恢复和优化指南；[本轮更新](phase14-usage-retrieval.md)整理任务地图、简短读取入口与检索开销。

[统一读取与四条有限功能链](phase15-unified-chains.md)介绍本次 ID/API 审阅入口、完整对象续读，以及主动技能、装备效果、可部署建筑和阶段生物的具名有限链。
