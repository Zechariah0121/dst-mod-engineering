# 装备、生态与复杂开发问题

`v2026.11.12.2`：296 条登记知识，其中 109 条机制研究。本阶段新增 17 条研究、50 项 API 合同和 9 篇实用指南。

| 更新内容 | 有什么用 |
|---|---|
| [装备耗能与修理](../references/gear-fuel-repair.md) | 接通启停、补料和维修，分清扣费与材料消费 |
| [投射物与命中](../references/projectiles-hits.md) | 选择追踪、抛射和范围效果，处理伤害归属与回收 |
| [建筑与施工](../references/placement-buildings.md) | 接入预览落点、套件部署、拆除和累计投料 |
| [巢穴与种群](../references/nests-population.md) | 管理生成、补员和回巢，按需求保留个体或数量 |
| [世界事件与袭击](../references/world-events-spawning.md) | 制作阶段事件或调整原版袭击，理解预警、暂停与恢复 |
| [海钓与鱼群](../references/ocean-fishing.md) | 接入拟饵、新鱼和鱼群，串起咬钩、收获与库存形态 |
| [复杂任务读取](../references/complex-task-reading.md) | 按实际职责补读完整合同，减少多组件开发中的遗漏 |
| [有期限效果恢复](../references/timed-effect-recovery.md) | 连接 Timer、Tracker 和来源 modifier，恢复剩余时间并正确退出 |
| [实用优化示例](../references/practical-optimization.md) | 减少重复查询、额外轮询和重复状态，保留必要的采样与失效处理 |

Skill 将这些内容接到具体开发任务。示例优先使用直接注册、局部回调与已有组件，让 AI 更容易写出完整且适合当前需求的实现。检索按 API 所属组件判断主要主题，减少“维修材料”等标题词对制作查询的干扰。
