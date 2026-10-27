# 源码更新与局部复核

证据基线、目标游戏源码和派生缓存分别管理。`v2026.10.27.1` 保留唯一 `source_epoch=759671` 作为证据基线，以 760178 为本次核验的来源输入；不新增 760178 epoch，也不把历史 Scope 或全库结论升级为 760178。官方更新后，旧知识仍可按原 Scope 审阅，新 ZIP 可独立定位和比较。

## 本次目标与来源准备边界

| 身份 | 核验值 |
|---|---|
| 目标游戏版本 / Steam build | `760178 / 26230496` |
| 目标 `scripts.zip` SHA-256 | `fab1cab00a0d043e49917bf18adbe8199caf60f1523dcc2e998785f44037893a` |
| Lua 文件盘点 | 旧 4084、新 4091；3940 同字节、144 变化、7 新增、0 删除 |
| 知识目录与准入 | 210 条，保留旧 187 条身份；23 条机制研究仍为 `research/restricted/hold` |

上述盘点是归档与文件字节对照，不是 144 个文件的行为兼容审查，更不是游戏实测。合法持有该目标 ZIP 的使用者可按 [安装说明](install-and-use.md) 准备来源；未来其他 ZIP 仍需核对核心必需范围，不能由本次支持推导全部可完整准备。

本版将 4 个重复的必需传送来源槽从 `scripts/componentutil.lua:1320–1408` 收窄到 `1325–1408`。范围来自可信 759671 完整旧源码，移除不属于该传送契约、在目标中已变化的注册函数；保留的 84 行在旧、新输入中逐字一致。必要范围及派生哈希重新绑定，原始历史证据仍按原身份和 `metadata_only` 保留；这不是将旧文件整体哈希改写为新版，也不表示范围之外的消费者未变。

核心必需载荷槽仍严格校验，无法恢复时 `SOURCE_GAP` 不激活部分运行环境。独立机制研究的来源核验则按每条引用区分：

| 逐引用状态 | 可以据此确认与保留的边界 |
|---|---|
| `EXACT_FILE_RANGE` | 被引用文件及范围哈希匹配；不要求无关文件或整个 ZIP 相同，不等于游戏行为验证 |
| `RANGE_ONLY` | 文件整体已变，但找到唯一相同范围，可包含行号迁移；原文件身份未验证，文件其他部分及依赖影响仍需复核 |
| `CHANGED_UNKNOWN` | 找不到唯一相同范围、输入限制或信息不足；原 Scope 保留，目标证据未知 |
| `MISSING` | 目标中没有该引用文件；保留来源缺口，可用独立导航继续定位 |

报告保留证据归档身份与实际输入身份，返回逐引用结果及汇总，不返回游戏 Lua。某条机制引用变化或缺失不封锁其他研究条目的读取，不能把未知引用宣称为已恢复源码；无论匹配多少引用，都不解除 Coding HOLD。声称提供原证据归档却与其内部文件/范围承诺不符时，仍是完整性错误，不能按普通新版变化吞掉。

以下维护工具的 `source_status` 与上述准备回执状态分别使用各自枚举；它们用于不同输出，均不改变知识准入或原证据版本。

## 单一维护入口

```sh
python -B -X utf8 run_kb.py maintain-sources --help
python -B -X utf8 run_kb.py maintain-sources locate --target "<new scripts.zip>" --symbol "Brain:OnStart"
python -B -X utf8 run_kb.py maintain-sources assess --baseline "<evidence baseline scripts.zip>" --target "<new scripts.zip>" --candidate "<reviewed candidate.json>" --output "<new report.json>"
python -B -X utf8 run_kb.py maintain-sources legacy-inventory --knowledge-root knowledge --output "<new inventory.json>"
```

`--target` 必须明确指定；没有 epoch 白名单，不扫描其他游戏目录。`--target-label` 只记录用户标签，不是版本证明。`locate` 为屏蔽注释和字符串后的符号导航，不推导声明可见性、函数范围或调用图。可加 `--source-file scripts/brain.lua` 消歧。

候选引用中的 `symbols` 也可以是带参数的调用描述。评估会保留这些提示，但只用严格 Lua 标识符做词法定位；非标识符提示不影响文件与范围哈希判断，也不会被猜测改写为另一符号。

缺少旧源码时省略 `--baseline`：目标文件及范围与既有哈希完全相同，仍可确认该来源身份；已变化文件无法比较则报告 `unknown/missing_matching_old_source`。这时依然可以定位新版源码和阅读原版本知识。`--output` 只创建新文件，拒绝覆盖已有文件。工具不提取、输出或上传原版 Lua。

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

已有完整缓存不会因为游戏目录 ZIP 被官方更新就自动失效；启动校验的是缓存及包内承诺文件。本版核验的 760178 输入按前述范围准备；其他新 ZIP 仍可先使用公开审阅与独立源码导航。某一核心必需范围不能恢复时，`prepare_sources.py` 仍可能报 `SOURCE_GAP`，此时不激活部分来源，不篡改旧范围或旧版本。

工具返回 0 只表示评估完成。没有运行游戏，不得宣称新版运行通过；报告不解除 Core Coding HOLD。现有 187 条记录的 `legacy-inventory` 只做适配盘点：Legacy 的历史 locator、Native AI 的 research refs、Core 的 typed artifact refs 需要分别绑定到有完整 Scope 的来源单元，不能自动当成本轮候选或统一改写为新版本。


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
