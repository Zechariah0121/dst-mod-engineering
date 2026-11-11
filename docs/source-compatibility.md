# 源码更新与局部复核

证据基线、目标游戏源码和派生缓存分别管理。`v2026.11.12` 的服务环境参数仍仅接受 `source_epoch=759671`，本次核验的来源输入为 762172。研究原子保留自身证据身份：23 条为 759671、14 条为 760944、7 条为 761239、36 条为 762172。目标输入标签不构成整包版本白名单，不切换服务环境或改写历史 Scope。官方更新后，旧知识仍可按原 Scope 审阅，新 ZIP 可独立定位和比较。

## Skill 自动检查入口

实质查库前由 Skill 执行 `run_kb.py update-sources ensure`。首次用 `ensure --source "<明确的scripts.zip绝对路径>"` 绑定；以后检查记忆路径，不扫描其他安装，也不在 `serve` 中隐式运行。相同成功输入快返，相同失败输入抑制自动重试；只有处理原因后确需重试时显式 `--retry`。

助手尝试适配可恢复来源，不改知识正文或历史证据身份。准备改变激活时按 reconnect_required 重连，再核对工具、任务响应和来源；失败后以明确目标 ZIP 与哈希继续核对本次任务的定义、消费者、端别和生命周期，不关闭整库或把新结论写成 canonical。遇文件缺失或限定符号零命中时，去掉原文件限定寻找搬迁。完整命令与状态处理集中在 [源码更新助手](../references/source-update-assist.md)。

下面的手动准备、`maintain-sources`、逐引用状态和缓存完整性契约继续适用。

## 本次目标与来源准备边界

| 身份 | 核验值 |
|---|---|
| 目标游戏版本 / Steam build | `762172 / 26474873` |
| 目标 `scripts.zip` SHA-256 | `733a0f7f97ace5a76aa5acee95405a6ec01697d93d844eeb4ecce7c001306980` |
| Lua 文件盘点 | 见 [762172 适配记录](version-762172.md) 的逐文件差异 |
| 知识目录与准入 | 267 条，保留旧 187 条身份；80 条机制研究仍为 `research/restricted/hold` |

上述为来源字节盘点。使用者按[安装说明](install-and-use.md)准备合法来源；其他 ZIP 可独立导航和评估，完整模式仍检查必需范围。

前版 760178 适配已将 4 个重复的必需传送来源槽从 `scripts/componentutil.lua:1320–1408` 收窄到 `1325–1408`。范围来自可信 759671 完整旧源码，移除不属于该传送契约、在目标中已变化的注册函数；保留的 84 行在旧、新输入中逐字一致。必要范围及派生哈希重新绑定，原始历史证据仍按原身份和 `metadata_only` 保留；760944 的 componentutil.lua 与 760178 整文件一致，本轮沿用该范围，不改变证据和校验器。具体对照见 [760944 适配记录](version-760944.md)。这不是将旧文件整体哈希改写为新版，也不表示其他消费者未变。

核心必需载荷槽仍严格校验，无法恢复时 `SOURCE_GAP` 不激活部分运行环境。独立机制研究的来源核验则按每条引用区分：

| 逐引用状态 | 可以据此确认与保留的边界 |
|---|---|
| `EXACT_FILE_RANGE` | 被引用文件及范围哈希匹配；不要求无关文件或整个 ZIP 相同，不等于游戏行为验证 |
| `RANGE_ONLY` | 文件整体已变，但找到唯一相同范围，可包含行号迁移；原文件身份未验证，文件其他部分及依赖影响仍需复核 |
| `CHANGED_UNKNOWN` | 找不到唯一相同范围、输入限制或信息不足；原 Scope 保留，目标证据未知 |
| `MISSING` | 目标中没有该引用文件；保留来源缺口，可用独立导航继续定位 |

报告并列证据归档与实际输入身份，局部缺口只影响对应研究；准入规则见[检索策略](../references/kb-retrieval.md)。若输入声称为原证据归档却违背其文件/范围承诺，按完整性错误处理。

以下维护工具的 `source_status` 与上述准备回执状态分别使用各自枚举；它们用于不同输出，均不改变知识准入或原证据版本。

## 单一维护入口

```sh
python -B -X utf8 run_kb.py maintain-sources --help
python -B -X utf8 run_kb.py maintain-sources locate --target "<new scripts.zip>" --symbol "Brain:OnStart"
python -B -X utf8 run_kb.py maintain-sources assess --baseline "<evidence baseline scripts.zip>" --target "<new scripts.zip>" --candidate "<reviewed candidate.json>" --output "<new report.json>"
python -B -X utf8 run_kb.py maintain-sources assess-registered --knowledge-root knowledge --target "<new scripts.zip>" --baseline "<optional evidence baseline scripts.zip>" --output "<new report outside knowledge root.json>"
python -B -X utf8 run_kb.py maintain-sources legacy-inventory --knowledge-root knowledge --output "<new inventory.json>"
```

`--target` 必须明确指定；没有 epoch 白名单，不扫描其他游戏目录。`--target-label` 只记录用户标签，不是版本证明。`locate` 为屏蔽注释和字符串后的符号导航，不推导声明可见性、函数范围或调用图。可加 `--source-file scripts/brain.lua` 消歧。

候选引用中的 `symbols` 也可以是带参数的调用描述。评估会保留这些提示，但只用严格 Lua 标识符做词法定位；非标识符提示不影响文件与范围哈希判断，也不会被猜测改写为另一符号。

缺少旧源码时省略 `--baseline`：目标文件及范围与既有哈希完全相同，仍可确认该来源身份；已变化文件无法比较则报告 `unknown/missing_matching_old_source`。这时依然可以定位新版源码和阅读原版本知识。`--output` 只创建新文件，拒绝覆盖已有文件。工具不提取、输出或上传原版 Lua。

### 按登记批量评估

`assess-registered` 只读取 `FAMILY-REGISTRY.json` 中 `native_mechanism` 的候选，
不扫描候选目录，也不把未登记文件加入结果。它核对包清单对 registry、CATALOG、
候选、review 及 review dependencies 的 SHA-256 承诺，检查候选格式、entry 顺序及
record hash，并要求 CATALOG 的机制研究条目与登记闭合。路径必须留在明确的 knowledge
根目录内；登记损坏、漏项或 hash 不符会使本次评估失败，不生成部分报告。
这些检查证明输入相对本地清单自洽，不是外部签名或新来源版本证明。

输出是 `dst-registered-source-compatibility/1` JSON sidecar，包含逐候选、逐引用、
claim / API contract / mechanism step 结果、`topic_summary` 与 `difference_summary`；
保留原 Scope、unknowns、limitations、review 身份与三轴状态。登记 topic 短名与候选的
`authored_topic` 描述分别保留。`archive_delta` 在提供旧 ZIP 时列出新增、删除、变化文件，
不含 Lua 文本；缺旧 ZIP 时为 null，不据此宣称没有变化。

`--output` 必填且必须在 knowledge 根目录外；完整评估及序列化成功后，工具在输出目录
暂存并以不覆盖的原子硬链接发布新文件。文件系统不支持硬链接、发布失败或目标已存在时
报错并清理暂存文件，不回退为部分写入。此命令不准备或安装来源、不改旧知识及 Scope，
也不限制目标 ZIP 的版本。`--baseline` 可省略；单次只接受一份旧 ZIP，多归档候选中与其
不匹配的引用保留 unknown，不猜测来源身份。匹配字节不消除动态/native/未枚举依赖的
unknown，也不解除 Coding HOLD 或代表游戏行为验证。

## 报告的含义

| source_status | 含义与维护动作 |
|---|---|
| `byte_identical` | 原引用文件和范围哈希完全相同，可沿用该来源身份；不等于整包或行为兼容 |
| `relocation_required` | 同文件发现唯一相同范围，但行号移动；提供候选新坐标，人工复核后另外记录，不自动改证据 |
| `review_required` | 引用内容变化，或原范围未变但文件其他部分变化；复核相关声明、消费者和依赖 |
| `missing` | 原引用路径在目标 ZIP 缺失；另用符号导航寻找新位置 |
| `unknown` | 缺匹配旧基线、引用不一致、匹配不唯一或信息不足；明确保留未知 |

结果按 claim、API contract 和 mechanism step 分别列出状态，并生成 `local_review_checklist`。定义未变而已登记消费者变化，会进入局部复核。`dependency_status` 始终保留动态、native 及未枚举消费者为 `unknown`；工具不建立完整行为兼容证明。只增加无关文件不会让所有旧知识失效。

候选采用 `dst-mechanism-research/1`，来源引用 ID 在单个候选内解析。先使用相应 intake 工具核验证据与候选格式。可选依赖元数据不要求旧候选返工：

```json
{
  "compatibility": {
    "dependency_coverage": "enumerated_static",
    "dependency_refs": [{"ref": "consumer-ref-id", "role": "调用方", "claim_ids": ["claim-id"]}],
    "unknowns": ["动态调用与 native 行为未建立依赖闭包"]
  }
}
```

`ref` 必须指向本候选的 `source_references`；`claim_ids` 如填写，只能为本 entry 的真实 claim ID。不写 `claim_ids` 时关联整个 entry 的源码单元，空列表时不关联任何 claim。`dependency_coverage` 仅允许 `unknown` / `enumerated_static`，不填默认未知；它不授予动态闭包完成状态。`unknowns` 是字符串列表。

## 读取旧知识与准备完整模式

`--mode full` 仍严格要求核心必需载荷、公开数据与身份 guards 全部通过；机制研究的逐引用缺口按上表保留，不等同整个完整服务无法启动。`--mode auto` 在未准备来源，或包升级造成 `PACKAGE_CHANGED` 时，先核验当前公开知识清单，再提供两工具审阅；状态及 MCP initialize 指令中报告 `availability_fallback.reason_code`。损坏缓存、无效激活、非法路径或不可信公开知识仍报错。

已有完整缓存不会因为游戏目录 ZIP 被官方更新就自动失效；启动校验的是缓存及包内承诺文件。本版核验的 762172 输入按当前适配记录准备；其他新 ZIP 仍可先使用公开审阅与独立源码导航。某一核心必需范围不能恢复时，`prepare_sources.py` 仍可能报 `SOURCE_GAP`，此时不激活部分来源，不篡改旧范围或旧版本。

维护命令退出 0 表示评估完成。旧 187 条记录的 legacy-inventory 只盘点来源：Legacy locator、Native AI research refs 和 Core typed artifact refs 分别绑定原 Scope，不统一改标。


## 旧三族的逐原子维护

`legacy-inventory` 只盘点目录。`legacy-assess` 从 Legacy、Native AI、Native Core 的
原记录、typed 引用及原始 Scope 定位生成独立 sidecar；新研究族另用 `assess`。

```powershell
python -B -X utf8 run_kb.py maintain-sources legacy-assess --knowledge-root knowledge --target "<明确的新 scripts.zip>" --baseline "<可选的旧 scripts.zip>" --output "<新 sidecar.json.gz>"
```

`--baseline` 可重复，也可省略。`--target` 省略时仅派生关联。输出必须是新文件，
`.gz` 为压缩 JSON。无需先准备完整服务；统一入口使用随包 helper，不依赖客户端 cwd。
可把 `--knowledge-root` 显式指向已准备 runtime 的 knowledge，以比较恢复后的引用；
不要把公开模板的 slot 当成已恢复源码。报告保留输入文档、record、atom、Scope 和引用指纹，
不改正文、三轴状态或客户端配置，也不包含完整游戏 Lua。

旧文件/行段字节承诺缺失、没有匹配旧归档、历史 metadata_only、来源冲突、动态/native
依赖都保留未知或历史身份。源码名称、当前行号、相同字节不自动构成当前行为证据。
Scope 字段定位可追溯，但不证明语义穷尽。`same` 只表示列出的来源身份匹配，
不表示新版本游戏行为兼容，也不授予 Coding 准入。官方更新不关闭其他条目的阅读或新 ZIP 导航。

此前 761239 的变化见[历史适配记录](version-761239.md)；当前输入与局部影响见[762172 适配记录](version-762172.md)。历史研究证据身份保持不变。
