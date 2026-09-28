# Skill、知识库与检索服务

三个目录职责不同：根目录 `SKILL.md` 与 `references/` 保存工作策略；`dst-engineering-kb/` 保存知识；`dst-kb-service/` 只读检索，SQLite 索引位于知识库以外。知识条目不是代码模板，也不是让 Agent 无条件执行的指令。

参考案例为“小穹”v13.80，既有元数据记录作者为 FL。保留案例名称与符号用于研究归属和定位，不代表原作者背书本知识库。仓库 MIT 许可适用于本仓库自行编写的工具与文档，不对第三方 Mod 或 Klei 游戏源码重新授予许可；本包不包含这些原始源码与素材。

## 从任务到证据

| 实际制作问题 | 模式 | 可作为起点的条目 | 仍要确认 |
|---|---|---|---|
| 按钮消耗资源释放技能 | architect | `DECISION-NET-001`、`RULE-NET-001` | 原版 Action 是否足够、Host/远端共同校验 |
| 重连后效果重复或残留 | debug | `RULE-LIFE-001`、`ANTI-LIFE-001` | 实际任务和监听归属；相似案例不直接证明根因 |
| 自动收纳与箱子制作供料 | architect | `PATTERN-WORLD-001`、`FACT-DST-003` | 真实物品归属、查询与扣除边界、注册/注销 |
| 地面洞穴共享仓库 | architect | `RULE-SHARD-001`、`PATTERN-SHARD-001` | 写入权威、重复请求、断线恢复 |
| 自定义数值存档与 HUD | implement | `FACT-DST-001`、`DECISION-PERSIST-001` | 真实状态保存、显示重建、首次同步 |
| 两个 Mod 包装同一函数 | review | `RULE-HOOK-002`、`TEST-HOOK-002` | 加载顺序、异常恢复、撤销时不覆盖别人 |

以上 ID 可在 [索引](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-engineering-kb/INDEX.md) 查询。重要决策读取完整条目，再沿明确关系找到反例与测试；不要仅凭摘要或相关性排名作结论。

例如自动收纳任务：检索候选模式 → 读取适用/不适用条件 → 决定状态 Owner → 查当前 Container/Builder 原版链路 → 实现注册与查询 → 执行本任务能覆盖的验证。World Manager 不替代单体 Component，也不能由“减少扫描”推断所有查询都是常数复杂度。

## 覆盖与回退

当前知识集中在状态归属、联机、分片、生命周期、存档、Hook 和世界协调。Skill 的制作专题覆盖更广；动画、音效等问题应继续读取相应专题和工具契约。检索使用词语匹配，非空结果可能不相关；无匹配也不能证明整个领域不存在知识。

检测到实际 MCP 工具后主动按需使用，不把配置存在当成已连接。没有 MCP 但能读文件时，读取 `data/index.json`、相关文档或 `data/entries.json` 中指定条目，说明使用了文件读取。没有任何可访问知识时，说明 `KB unavailable` 并继续能做的源码工作。不得虚报查询或测试成功。

普通开发不会自动修改知识库。发现新证据或知识缺口时在任务报告记录，只有明确维护请求才进入知识更新与 Correction 流程。来源事实、单案例观察和建议分别看待；历史撤回 Claim 只能作为历史。

## 获取与验收

- 完整仓库包含三层；网页技能 ZIP 只包含技能与辅助资料，不包含知识库和服务。
- [服务接入](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-kb-service/README.md) 使用 Python 3.10+，不需要第三方 Python 包或 API Key。
- [知识库入口](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-engineering-kb/README.md) 说明证据范围；公开材料已脱敏，不能声称等于未修改的本机原始报告。
- 数据校验、服务回归、Agent 真正按任务自动检索、DST 实机验证是四种不同验收。

## 维护公开派生包

维护者使用 `scripts/build_public_kb.py` 的帮助查看显式输入/输出参数。输入是合法持有的知识资料副本，不能以本机 Skill 安装目录代替公开发布源。公开导出后核对来源/公开哈希、Schema、链接、Correction 与敏感内容，再重建网页资料包。原始冻结资料不应被导出流程覆盖；公开脱敏不提升证据等级或置信度。
