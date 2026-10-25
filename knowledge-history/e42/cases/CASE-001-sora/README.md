# CASE-001 — 小穹 v13.80

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="case-001"></a>

## CASE-001 — 小穹 v13.80

类型：Case Observation · Evidence：E1 · Confidence：High · Status：validated_single_case · Version：0.1.1

以玩家业务通道、分片共享状态、世界容器 Manager 和接入框架为主要研究面的一份静态案例。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Case Id

[CASE-001](README.md#case-001)

### Name

小穹

### Mod Version

13.80

### Author

- **declared**：FL
- **source**：modinfo.lua author 字段；本轮仅核对元数据，未执行文件。

### Analysis Date

2026-09-28（本地第4–6轮报告日期；前3轮独立时间未恢复）

### Project Size

- **files**：949
- **lua_files**：186
- **bytes**：68623081

### Domains

- 玩家业务通信/客户端视图
- 分片共享数据
- 容器注册/物流/制作整合
- 环境/Hook/模块接入

### Research Rounds

1. **round**：1
   - **topic**：Architecture Recon
   - **availability**：completed_per_user; standalone_report_not_located

2. **round**：2
   - **topic**：ClientDB
   - **availability**：completed_per_user; standalone_report_not_located

3. **round**：3
   - **topic**：MainDB
   - **availability**：completed_per_user; standalone_report_not_located

4. **round**：4
   - **topic**：sorachestmanager
   - **availability**：available_report

5. **round**：5
   - **topic**：SoraEnv + SoraAPI + Hook Framework
   - **availability**：available_report

6. **round**：6
   - **topic**：种子/全局制作端到端组合验证
   - **availability**：available_report

### Analysis File Count

- **unique_mod_total**：未记录 / null
- **confirmed_mod_lower_bound**：17
- **count_note**：第6轮17个关键Mod文件有审读与语法记录；第5轮10个关键文件另有语法记录。不能相加视为六轮去重阅读总量。
- **project_lua_count_is_not_analysis_count**：是

### Runtime Tested

否

### Dedicated Tested

否

### Vanilla Context

- **source_context_id**：KLEI-LOCAL-20260928
- **release_build**：未记录 / null
- **note**：第6轮18份、第5轮13份原版文件分别对照本机游戏 scripts.zip；未在线确认最新发行版；不把两批相加当去重总数。

### Project Hash

52c1cbe65297d77ae006613c33955199f87b835a04fea9fe27427ac1c0361f71

### Hash Algorithm

对按完整路径排序的文件：依次 hash.update(relative_posix_path.encode(UTF8)); hash.update(SHA256(file_bytes).digest())。

### Architecture Summary

- 玩家通道把业务意图、服务器View和客户端Cache组织起来。
- 共享种子计数在各Shard本地可写并传播完整值；没有自动获得唯一权威。
- 世界Manager持有实体注册/候选；真实物品仍在Container/Stackable。
- 框架提供启动顺序、共享环境与多类Hook；并非统一可卸载的通用框架产品。

### Observations

1. **claim**：种子服务器 ClientDB 为 View，客户端 SeedCDB 为缓存。
   - **knowledge_kind**：Case Observation
   - **evidence_level**：E1
   - **source**：[REPORT-R6](<../../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 3–6

2. **claim**：全局制作使用当前Shard的注册容器，不经MainDB跨世界取材。
   - **knowledge_kind**：Case Observation
   - **evidence_level**：E1
   - **source**：[REPORT-R6](<../../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 8–11

3. **claim**：Manager有候选缓存和活动集合，但不是数量总账，也未消除全部扫描。
   - **knowledge_kind**：Case Observation
   - **evidence_level**：E1
   - **source**：[REPORT-R4](<../../review-support/reports/sorachestmanager_DeepDive_20260928.txt>) · interpretation · 6；8；15

4. **claim**：SoraAPI 为 env 别名，共享环境隐藏部分依赖。
   - **knowledge_kind**：Case Observation
   - **evidence_level**：E1
   - **source**：[REPORT-R5](<../../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 2–5

### Identified Patterns

- [PATTERN-NET-001](../../patterns/PATTERN-NET-001.md#pattern-net-001)
- [PATTERN-SHARD-001](../../patterns/PATTERN-SHARD-001.md#pattern-shard-001)
- [PATTERN-WORLD-001](../../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [PATTERN-FRAMEWORK-001](../../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)

### Identified Anti Patterns

- [ANTI-NET-001](../../anti-patterns/case001.md#anti-net-001)
- [ANTI-SHARD-001](../../anti-patterns/case001.md#anti-shard-001)
- [ANTI-SHARD-002](../../anti-patterns/case001.md#anti-shard-002)
- [ANTI-RESOURCE-001](../../anti-patterns/case001.md#anti-resource-001)
- [ANTI-HOOK-001](../../anti-patterns/case001.md#anti-hook-001)
- [ANTI-HOOK-002](../../anti-patterns/case001.md#anti-hook-002)
- [ANTI-LIFE-001](../../anti-patterns/case001.md#anti-life-001)
- [ANTI-WORLD-001](../../anti-patterns/case001.md#anti-world-001)
- [ANTI-FRAMEWORK-001](../../anti-patterns/case001.md#anti-framework-001)

### Unverified

- 所有Host/Remote/Dedicated运行结论
- 跨Shard并发/离线恢复实际时序
- 多Mod兼容与异常注入
- 大规模性能/长期泄漏测量
- 六轮准确去重审读文件总数及原版发行build

### Corrections

- [CORRECTION-CASE001-001](../../corrections/CASE-001.md#correction-case001-001)

### Exclusions

1. **topic**：Persisting / Treating Derived Runtime State As Truth
   - **reason**：本案例有Registry/Cache重建正例；没有足够证据将错误保存派生状态登记为已发生反模式。可作未来检索问题。

2. **topic**：God Manager
   - **reason**：已建 E0 风险候选，未宣称案例达到 God Object。

### Availability Limit

前三轮独立报告未在工作区发现；本次采用第4–6轮已保留的交叉证据，不补造前三轮原文或发现。

### Static Failure Paths

- [FAIL-CASE001-001](../../failures/case001.md#fail-case001-001)
- [FAIL-CASE001-002](../../failures/case001.md#fail-case001-002)
- [FAIL-CASE001-003](../../failures/case001.md#fail-case001-003)
- [FAIL-CASE001-004](../../failures/case001.md#fail-case001-004)

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](README.md#case-001)
- **domains**：- networking
  - shard
  - world
  - UI
  - lifecycle
  - framework
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：- server
  - client
  - shard

### Typed Relations

无 / 未建立

### sources

- META-MODINFO（外部来源未随包） · interpretation · author/version/name 字段
- [REPORT-R4](<../../review-support/reports/sorachestmanager_DeepDive_20260928.txt>) · interpretation · 全文索引
- [REPORT-R5](<../../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 全文索引
- [REPORT-R6](<../../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 全文索引

### related

- [PATTERN-NET-001](../../patterns/PATTERN-NET-001.md#pattern-net-001)
- [PATTERN-SHARD-001](../../patterns/PATTERN-SHARD-001.md#pattern-shard-001)
- [PATTERN-WORLD-001](../../patterns/PATTERN-WORLD-001.md#pattern-world-001)
- [PATTERN-FRAMEWORK-001](../../patterns/PATTERN-FRAMEWORK-001.md#pattern-framework-001)
- [CORRECTION-CASE001-001](../../corrections/CASE-001.md#correction-case001-001)
