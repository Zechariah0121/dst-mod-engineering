# 使用入口、任务地图与检索改进

`v2026.11.12.3` 增加任务地图和简短阅读命令，并减少复杂检索中的重复计算，让 AI 更容易从开发问题找到已有依据。

- [任务地图](../references/task-map.md)按常见功能连接指南、登记 ID 和项目所需信息，减少从目录猜入口的步骤。
- [研究使用说明](../references/kb-retrieval.md#研究记录怎样支持当前开发)连接研究结论、当前源码核查和目标 Mod 的适用条件。
- `find` / `read` 可直接阅读包内公开材料，无需先配置 MCP 或准备源码。
- 同一次请求复用相同文本的主题和导航词项分析，减少复杂任务装包的重复计算。

在包根运行：

```text
python -B -X utf8 run_kb.py find "OceanFishingTackle:SetupLure"
python -B -X utf8 run_kb.py read EXP-FISH-001 --pointer /api_contracts/2 --max-bytes 24000
```

读取命令保留所选记录的适用范围和来源状态；详细参数见[知识读取](knowledge-integration.md)。后续增加的跨族统一审阅、续读与功能示例见[最新更新](phase15-unified-chains.md)。
