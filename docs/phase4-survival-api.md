# 生存状态与 API 入口扩展

`v2026.10.30.2` 在原 210 条基础上增加 6 条有独立静态审阅的研究，合计 216 条；其中机制研究 29 条，全部保留 `research/restricted/hold`。

| 新增记录 | 研究范围 |
|---|---|
| `EXP-TEMP-001` | 温度权威更新、湿度影响、保存恢复、客户端可见边界及移除风险 |
| `EXP-WET-001` | 降雨/装备/外部来源、热源与局部环境干燥、湿布尔与消费者 |
| `EXP-WET-002` | 多来源 ForceDry、死亡复活、读档/转移及 classified/replica 边界 |
| `EXP-FREEZE-001` | 冻结三态、抗性/寒冷、SG 事件消费、有限保存与移除清理 |
| `EXP-FIRE-001` | 传播热量与直接解冻、融化事件及蜂蜡消费者 |
| `EXP-FREEZE-002` | 红蓝法杖攻击入口的显式熄火、加寒冷与解冻次序 |

新研究直接核对 760944 / Steam build 26306684，保留各自文档的证据版本。历史 23 条机制研究及旧三族不改写为新版；服务运行环境参数 `source_epoch=759671` 与原子的证据版本分别表达不同身份。范围哈希、归档身份与实际输入评估仍逐项保留，不能由字节相同推导运行兼容。

## 显式研究 API 查询

```json
{"symbol":"Freezable:AddColdness","family":"native_mechanism","projection":"reviewer","max_bytes":24000}
```

对 `lookup_api` 显式选择 `family="native_mechanism"`，可按 `source_file`、`owner`、`identity_kind` 缩小研究契约身份。省略 family 沿用历史物理声明入口；该工具默认 Reviewer，Coding 不能使用研究入口。原子完整保留参数、返回、前提、副作用、生命周期、Scope、未知和引用。预算不足时整原子 withheld，同名不同身份不会由排名代选。

身份来自作者契约中的名字和可见性，是审阅导航，不是新建立的物理声明/公共导出证明。明确 local 保留 local；无导出依据或互相冲突时保守为 unknown。动态索引等不可静态识别写法仍需按 ID 与 JSON Pointer 展开，不能猜成全局函数。

## 登记驱动的批量源码评估

```sh
python -B run_kb.py maintain-sources assess-registered --knowledge-root knowledge --target "<scripts.zip>" --output "<knowledge目录外的新JSON>"
```

入口校验登记、清单、候选/审阅哈希与目录身份，只评估已登记的机制族。可选 `--baseline` 提供一份旧归档；缺少匹配旧源码时保留 unknown。输出逐主题、引用、声明、API 和机制步骤及局部复核清单；不改知识正文、不解除准入、不要求目标版本白名单。输出拒绝覆盖和写入知识根，完整临时文件通过硬链接原子发布，因此目标文件系统需支持硬链接。

批量维护中的 `unknown/missing_matching_old_source` 与准备回执的 `RANGE_ONLY` 属于不同证据条件和枚举，不应混加成同一覆盖率。批量报告含本机来源路径，仅用于本地维护；公开附件需要单独制作去除本机路径的派生版本。

本轮不运行 DST、专服或远端客户端，不声称动画、音效、native 行为和任意 Mod 组合已经验证。局部源码中观察到的清理风险仍保留前提与动态注入未知；建议不等于游戏中已重现故障。

## 已知检索边界

完整服务的研究搜索沿用机制专路；有机制候选时，旧族结果可能未同时展示。独立对照确认该行为在上一版也存在。跨族发现可先查统一目录；已知 Core 目标可显式限定 `families=["core"]` 或按 ID 读取，不能从一次未命中推断没有知识。

较大的条目会在搜索预算内整项 withheld，并提供读取入口；应按 claim/API/step 指针展开，必要时将 `get_entry.max_bytes` 提高至 64000。单引用 `resolve_evidence` 仍可能因所需上下文超过其预算而 withheld；相关原子读取保留完整定位元数据。后续将改进跨族导航和引用响应的预算使用。部分 local 回调尚无研究 API 契约，同名消歧只覆盖已经声明的身份。
