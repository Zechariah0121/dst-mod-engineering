# failure_case · v0.1.1

本文件由 `data/entries.json` 生成；证据等级与推荐置信度互相独立。没有执行这里的测试候选。

<a id="fail-case001-001"></a>

## FAIL-CASE001-001 — Seed cross-shard lost update

类型：Case Observation · Evidence：E1 · Confidence：High · Status：needs_runtime_validation · Version：0.1.1

A 可为6，B可为15；任一合法串行存取后的余额应为11。实体转换已经发生。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Preconditions

- A/B 属于同一公共种子域，初始余额均为10
- 两边在接收对方更新前分别以旧值计算
- 采用已确认的完整值 Set 广播路径

### Steps

- A 存入5，删除实体后写15
- B 取出4，生成实体后写6
- 两条消息交叉到达，各副本用对方最终值覆盖本地值

### Result

A 可为6，B可为15；任一合法串行存取后的余额应为11。实体转换已经发生。

### Expected Correctness

若业务声明共享且守恒：最终可用余额应与合法操作总和一致，且不能通过旧副本合计超提。

### Evidence

M07 main/maindb.lua:774–786；M06 main/clientdbinit.lua:143–153；M12 soraseedcontainer.lua:121、157–218（REPORT-R6 编号）

### Verification Status

- Static Confirmed Path
- Not Runtime Reproduced

### Runtime Reproduced

否

### Limits

REPORT-R6 §7.3 的静态交错；是否出现这个到达顺序及玩家影响尚未实测。

### Static Path Confirmed

是

### Runtime Validation Status

not_runtime_reproduced

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- architecture
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：illustrates
   - **target**：[ANTI-SHARD-001](../anti-patterns/case001.md#anti-shard-001)

2. **type**：illustrates
   - **target**：[ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 4–7

### related

- [ANTI-SHARD-001](../anti-patterns/case001.md#anti-shard-001)
- [ANTI-SHARD-002](../anti-patterns/case001.md#anti-shard-002)
- [RULE-SHARD-001](../rules/shard.md#rule-shard-001)
- [TEST-SHARD-001](../tests/candidates.md#test-shard-001)

<a id="fail-case001-002"></a>

## FAIL-CASE001-002 — Duplicate Material Provider Allocation

类型：Case Observation · Evidence：E1 · Confidence：High · Status：needs_runtime_validation · Version：0.1.1

最终材料计划只有 E=2，检查/分配层未保证总需求6。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Preconditions

- 同一已打开且注册的容器 Stack E=4
- 实际配方需要6，其他来源为空
- 全局制作已启用且 Manager 分类、距离条件成立

### Steps

- 原版查询返回 E=4
- Manager 按同一实体保留1后可用3，足以补名义缺口2
- 返回 E=2，Adapter 用 finds[E]=2 覆盖4
- need 按补齐计算完成，原版消耗接收到的表

### Result

最终材料计划只有 E=2，检查/分配层未保证总需求6。

### Expected Correctness

来源重叠不应制造额外资源；总可用4时应拒绝需要6的制作，且最终计划不应静默覆盖。

### Evidence

main/hook.lua:1510–1566；sorachestmanager.lua:1182–1236；原版 Inventory:GetCraftingIngredient 和 Builder:RemoveIngredients。

### Verification Status

- Static Confirmed Path
- Not Runtime Reproduced

### Runtime Reproduced

否

### Limits

REPORT-R4 §9 已确认，REPORT-R6 §11.3 将其定位为 Provider/Builder Adapter 集成边界；非缓存故障。

### Static Path Confirmed

是

### Runtime Validation Status

not_runtime_reproduced

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- architecture
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：illustrates
   - **target**：[ANTI-RESOURCE-001](../anti-patterns/case001.md#anti-resource-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 11.3

### related

- [ANTI-RESOURCE-001](../anti-patterns/case001.md#anti-resource-001)
- [RULE-RESOURCE-001](../rules/resource.md#rule-resource-001)
- [TEST-RESOURCE-001](../tests/candidates.md#test-resource-001)

<a id="fail-case001-003"></a>

## FAIL-CASE001-003 — Unsafe temporary patch remains after error

类型：Case Observation · Evidence：E1 · Confidence：High · Status：needs_runtime_validation · Version：0.1.1

恢复路径未执行；若会话继续且对象仍在，字段可保留临时 wrapper。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Preconditions

- 进入 Builder/UI 的临时方法替换分支
- 被包装的 old 调用抛出 Lua error
- 若讨论会话后续污染，还需外层捕获错误并继续运行

### Steps

- 保存 oldhas
- 安装临时 Has
- 调用 old 期间抛错
- 控制流跳过 restore 赋值

### Result

恢复路径未执行；若会话继续且对象仍在，字段可保留临时 wrapper。

### Expected Correctness

操作无论成功或失败，都应按所有权规则恢复临时修改，并保留原错误。

### Evidence

main/hook.lua:1446–1458、1516–1535、1544–1566。

### Verification Status

- Static Confirmed Path
- Not Runtime Reproduced

### Runtime Reproduced

否

### Limits

静态确认异常分支缺少恢复保证；未注入异常，未声称正常游玩已发生持续污染。

### Static Path Confirmed

是

### Runtime Validation Status

not_runtime_reproduced

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- architecture
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：illustrates
   - **target**：[ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)

### sources

- [REPORT-R5](<../review-support/reports/SoraFramework_DeepDive_20260928.txt>) · interpretation · 13
- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 17

### related

- [ANTI-HOOK-001](../anti-patterns/case001.md#anti-hook-001)
- [RULE-HOOK-002](../rules/hook.md#rule-hook-002)
- [TEST-HOOK-001](../tests/candidates.md#test-hook-001)

<a id="fail-case001-004"></a>

## FAIL-CASE001-004 — ClientDB owner task lifetime exceeds DB lifetime

类型：Case Observation · Evidence：E1 · Confidence：High · Status：needs_runtime_validation · Version：0.1.1

任务与闭包仍可存活到 World 清理；Send 的 Inited 检查阻止正常发包，但不是取消任务。

**Scope**：CASE-001 静态证据及其原版快照；迁移到其他 Mod/游戏版本须重新确认适用条件。

### Preconditions

- 为玩家创建 seed 服务端 View，World 上建立 UpdateOwnerKeyTask
- 该玩家断开触发 ClientDB:UnInit
- World 仍继续运行

### Steps

- 模板 serverfn 创建每3秒任务，闭包捕获 DB/玩家上下文
- UnInit 调 bind.Remove，只解除两个 MainDB 监听
- 移除 DB 注册并设置 Inited=false
- 没有取消对应 World Task

### Result

任务与闭包仍可存活到 World 清理；Send 的 Inited 检查阻止正常发包，但不是取消任务。

### Expected Correctness

与该玩家 DB 同生命周期的任务应在 DB 注销时终止；世界级任务若继续须不保留过期玩家绑定。

### Evidence

main/clientdbinit.lua:178–186、227–230；main/clientdb.lua:151–175、184–187。

### Verification Status

- Static Confirmed Path
- Not Runtime Reproduced

### Runtime Reproduced

否

### Limits

源码路径确认；未做重复重连的内存/任务数量测量。

### Static Path Confirmed

是

### Runtime Validation Status

not_runtime_reproduced

### Structured Scope

- **game**：Don't Starve Together
- **cases**：- [CASE-001](../cases/CASE-001-sora/README.md#case-001)
- **domains**：- architecture
- **evidence_modes**：- static_analysis
- **runtime_environments**：无 / 未建立
- **sides**：无 / 未建立

### Typed Relations

1. **type**：illustrates
   - **target**：[ANTI-LIFE-001](../anti-patterns/case001.md#anti-life-001)

### sources

- [REPORT-R6](<../review-support/reports/SoraBusinessIntegration_20260928.txt>) · interpretation · 16

### related

- [ANTI-LIFE-001](../anti-patterns/case001.md#anti-life-001)
- [RULE-LIFE-001](../rules/life.md#rule-life-001)
- [TEST-LIFE-001](../tests/candidates.md#test-life-001)
