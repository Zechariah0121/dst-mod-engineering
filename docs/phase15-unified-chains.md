# 统一知识读取与完整功能示例

`v2026.11.12.5` 提供 300 条登记知识、420 项机制 API 合同。统一的 ID/API 审阅入口和功能示例，让 AI 更容易找到依据、接通功能并处理退出与恢复。

- **统一读取**：按 ID 自动识别知识族，按 API 符号跨族查找，减少手动选择入口。
- **完整对象续读**：内容超过当前预算时返回下一步调用，继续读取完整合同；修复小预算下续读入口丢失的问题。
- **任务导航**：从[任务地图](../references/task-map.md)找到对应指南、已有合同和需要核对的项目入口。
- **四条功能示例**：把分散的组件合同串成具体接线，帮助 AI 少造多余状态和封装。

## 通过 ID 或 API 读取

在已准备来源的完整包根运行：

```text
python -B -X utf8 run_kb.py review EXP-CHAIN-SPELL-001
python -B -X utf8 run_kb.py review --api "SpellCaster:CanCast"
```

MCP 对应 `get_entry(id=..., projection="reviewer", purpose="review")` 和 `lookup_api(symbol=..., projection="reviewer", family="all")`。有 `continuation` 时执行返回的工具与参数；API 导航通过 `results[].followup` 展开。更多参数见[知识读取](knowledge-integration.md)。无需准备来源的公开材料阅读仍可使用 `find` / `read`。

## 四条功能链

| 示例 | 帮助解决的问题 |
|---|---|
| [黄杖地面施法](../references/chain-active-skill.md) | 串起输入、权威执行帧、消费与生成效果的退出 |
| [鼹鼠帽夜视与耗能](../references/chain-equipment.md) | 接通装备成员、夜视表现、耗能、卸下与燃料恢复 |
| [便携帐篷部署与收起](../references/chain-deployable.md) | 处理物品与建筑形态切换、耐久交接和稳定形态保存 |
| [普通猪人两态转换](../references/chain-creature-stage.md) | 连接转换输入、属性、Brain/SG、回退与恢复 |

指南附自写最小示例。玩法数值和失败处理按目标项目选择；具体接入条件与变体边界见各指南。

## 验证状态

四个示例完成了对应的专服检查，装备、建筑和生物示例还经过存档重启检查。真实客户端、跨分片及各指南列出的特殊分支仍待验证。研究记录保留原来源范围与准入状态；源码更新维护见[源码维护](source-compatibility.md)。
