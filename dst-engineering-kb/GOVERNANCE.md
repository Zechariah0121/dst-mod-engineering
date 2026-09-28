# 证据、状态与维护政策 v0.1

## 五类信息不可互相冒充

| knowledge_kind | 可以陈述什么 | 不能据此推出什么 |
|---|---|---|
| Klei Fact | 在指定源码快照、函数和分支中确认的 API 行为 | 官方推荐该架构、跨版本永久不变 |
| Case Observation | CASE-001 实际结构、调用路径、代码条件 | 所有 DST Mod 都必须如此 |
| Engineering Pattern Candidate | 从一个案例提取的条件性结构方案 | 已由多个独立项目验证 |
| Engineering Rule Candidate | 有 Why/Applies When/Does Not Mean 的规则候选 | 无例外的普遍铁律 |
| Recommendation | 决策方向、较安全替代、测试候选及推理流程 | Klei 官方事实或已执行结果 |

Anti-Pattern 是风险识别建议；其中 Case Evidence 才是案例观察。God Manager 只有风险候选。
Rule/Pattern 的 `sources` 可同时指向案例及相关 E3 Fact，但自身不会因引用 Fact 自动升级为 E3。
Case 条目中的 observations 单独标记 E1。失败路径的静态机制与实机后果分开记录。

## Evidence Level

| 级别 | 定义 | 升级所需证据 |
|---|---|---|
| E0 — Hypothesis | 推测/待验证风险 | 不能宣称实际发生；找直接代码/运行证据 |
| E1 — Single Mod Evidence | 在一个案例中有直接代码支持 | 同一项目的多轮报告仍只算一个案例 |
| E2 — Multiple Independent Mods | 多个互不依赖项目独立验证 | 确认没有复制同一实现、共享同一依赖导致假独立 |
| E3 — Klei Source Supported | 原版源码直接支持限定行为 | 保留文件、函数、分支、快照指纹与版本上下文 |
| E4 — Runtime Validated | 在明确记录的运行环境中验证 | 日志/步骤/版本/实际结果；只对已测环境成立 |
| E5 — Repeated Runtime Validation | 多环境、多项目长期反复运行验证 | 多次结果、差异、失败记录与复查周期 |

等级不是“E3 自动包含 E2/E4”的单一质量分数。来源广度、官方源码支持与实机验证是不同维度。
E4 若只测试一个 Dedicated 场景，不可写成 Host/Remote/所有专服均通过。
本版本只有 E0、E1、E3；所有运行测试候选均 `not_run`。

## Recommendation Confidence

| 等级 | 本库解释 |
|---|---|
| Experimental | 主要用于探索，连适用边界都尚不清楚 |
| Low | 有问题线索，但正反证不足或尚未证实 |
| Medium | 单案例支持且有合理适用边界，跨项目仍待验证 |
| High | 在明确条件下因果/失败机制清楚；不是“适合所有项目” |
| Very High | 限定快照内的直接 API 事实或明确的纠错证据；仍保留版本边界 |

Confidence 是对该条限定陈述/建议的把握，不是自动推荐在任何 Mod 采用的概率。
不对 Evidence 做数值平均；反例和不适用条件不能被支持来源数量淹没。

## Knowledge Status

允许：`candidate`、`validated_single_case`、`supported_by_klei`、`needs_runtime_validation`、`superseded`、`corrected`、`deprecated`。
不用 `universal` 或 `best_practice`。

- candidate：进入知识库供选择、讨论、反证；并不表示没有直接证据。
- validated_single_case：确认案例索引/观察，不代表运行通过。
- supported_by_klei：限定原版行为可定位；不表示推荐使用方式被 Klei 背书。
- needs_runtime_validation：明确静态失败机制或其它需实测条目。
- corrected：记录旧主张被什么证据纠正；旧主张在 Correction 中标记 superseded。
- superseded：保留历史，但检索默认先给替代结论。
- deprecated：适用条件/版本已过期，附退出或迁移说明；不是抹去来源。

## 冲突和 Correction 流程

1. 比较是否在讨论同一个版本、前提、分支；不同条件可以同时成立。
2. 对同一主张，本次以第六轮更完整调用证据优先；不是以后永远“日期较新就正确”。
3. 创建 Correction，定位旧报告章节/旧主张、后续证据、替代结论和影响范围。
4. 不修改原报告。当前 canonical 条目采用修正结论，并链接 Correction。
5. 检索到旧报告时，先返回关联 Correction；不要在向量库里只更新新块却让旧错误无标记继续命中。

本版本的 `CORRECTION-CASE001-001` 撤回的是未使用 local 的运行时因果和硬时序依赖；不是否认那行赋值存在。
因此旧报告关于环境共享的其他证据仍可使用；不能因为一处纠错就整体删除报告。

## 版本与来源缺口

`version` 是知识条目版本，`mod_version` 是样本版本，`schema_version` 是机器结构版本，三者不同。
原版发行 build 未记录则使用 null；以本机快照日期/文件指纹定位，不填猜测版本。
第1–3轮独立报告未找到，标为 missing source；第4–6轮可以支持其已复核内容，但不能补造丢失报告原话。
准确审读文件总数未知；项目文件总数、语法检查数、审读数分栏记录。

## RAG / Agent 使用契约

建议检索顺序：Case/版本上下文 → Fact → Pattern → Related Rule + Anti-Pattern → Decision → Test。
每个块必须携带 id、version、knowledge_kind、evidence_level、confidence、status、sources、scope。
按 ID 联接图，不把文件名或自然语言标题当稳定主键。
遇到 E0 或 `needs_more_cases` 时，在输出中保留未知项；未执行测试不得写“已验证”。
若需要新 API 事实，进入新的查证任务；本轮抽取不借机继续横向 Deep Dive。

## 新 Case 接入最低要求

独立来源与版本、快照、研究范围、端别、实际运行记录、正例/反例、Correction、与旧条目的关系。
先记录观察，再考虑是否支持/反驳既有候选；不要为了填满模板制造不存在的系统。
只有独立实现证据才考虑 E2；实际运行结果按场景记录后才能考虑 E4。
