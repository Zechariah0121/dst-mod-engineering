# 装备耐久、耗能与材料维修

来源与 API 合同：[机制研究](../knowledge/research/native-mechanisms/gear_fuel_durability-c8a320d3367f.json)。

按使用次数消耗的物品可用 `finiteuses`，按启用时间消耗的物品可用 `fueled`，按材料回复次数可用 `repairable` 与 `repairer`。护甲结算、冷却与装备槽位继续沿用已有[物品与维修](items-food-plants.md)、[战斗与冷却](combat-buffs-containers.md)中的入口。以下为 762172 / build 26474873 的静态接线说明，尚未运行游戏。

次数与燃料基础合同复用 `ID-C01` 至 `ID-C04`，攻击磨损复用 `NC-N004-FINAL-01`，普通维修的请求、拒绝与材料消费复用 `BTR-P01/P02`，各自历史 Scope 和更正继续适用。本轮 `EXP-GEAR-001` 补装备耗能的具名生命周期，`EXP-GEAR-002` 补有限次数维修效果与可修标签。

## 按次数扣耐久

在自有 prefab 的服务器分支中，分别设置上限与当前次数。以下示例从满次数开始，假设 `weapon` 已配置，常量和 `OnFinished` 由物品设计提供。

```lua
local uses = inst:AddComponent("finiteuses")
uses:SetMaxUses(MAX_USES)
uses:SetUses(MAX_USES)
uses:SetOnFinished(OnFinished)

inst.components.weapon.attackwear = ATTACK_COST
```

`SetMaxUses` 只改上限，`SetUses` 改当前次数。`Use(n)` 扣绝对次数，`SetPercent(p)` 设置 `total * p`，`p` 采用 0 到 1 的比例约定。有限次数组件本身允许超上限和负比例进入设置路径，项目提供的常量应符合自己的范围。`SetUses` 先通知百分比，再处理归零和耗尽回调。保存零次数后，加载也可能经过该回调，破损保留、删除或替换的政策应在构造时确定。来源 `GEAR-S01`、`GEAR-S03`、`GEAR-S04`、`GEAR-S09`。

| 实际使用入口 | 成本配置 | 回调时点 |
|---|---|---|
| 普通武器攻击 | `weapon.attackwear`，再乘攻击磨损和攻击者效率倍率 | `onattack` 与 `weapononattack` 先执行，随后进入默认磨损 |
| 普通工具动作 | `finiteuses:SetConsumption(action, cost)`，可用 `SetModifyUseConsumption` 调整 | 动作完成通知路径，工作与磨损先后沿用 `EXP-CRAFT-003` |
| 自有按钮、法术或其他操作 | 在功能已选定的成功/尝试阶段调用 `Use(cost)` | 按该功能的真实回调与返回合同确定 |

`SetModifyUseConsumption` 影响 `OnUsedAsItem` 的动作消费。武器攻击直接进入 `Use`，有独立的成本计算。动作消费回调返回 `0` 表示零成本，返回 `nil/false` 会由 `Use` 采用缺省的 1 次。普通武器已有磨损入口，附加攻击效果可专注自己的效果。来源 `GEAR-S02`、`GEAR-S04`、`GEAR-S06`、`GEAR-S10`。

所查普通 Combat 分支先调用主目标受击，再调用 Weapon。这个磨损点按攻击链执行，具体伤害还取决于抵挡、护甲与目标状态。若需求按实际伤害成功扣次数，应先选定能观察该结果的入口，再调整默认磨损。原版 `spear` 的 `OnFinished` 选择删除，保留破损物品的功能需要自行定义可用性与修复后的行为。来源 `GEAR-S07`、`GEAR-S08`、`GEAR-S09`。

## 装备期间耗燃料（EXP-GEAR-001）

`Fueled` 的容量与增减量都使用燃料单位。周期扣量为 `dt * rate * rate_modifiers:Get()`。仅在 `rate=1`、倍率为 1 时，容量数值才直接对应运行秒数。构造时可用 `InitializeFuelLevel(CAPACITY)` 建立满量容量，普通补扣用 `DoDelta(amount)`。来源 `GEAR-S13`、`GEAR-S17`、`GEAR-S18`。

在当前物品的装备回调调用 `StartConsuming()`，卸下回调调用 `StopConsuming()`，并保留已有换装与属性清理逻辑。`amulet.lua` 的 file-local 黄色护符函数展示了这一接线，同时处理装备到模型、卸下、物品移除时的灯清理。这些内部函数可作参考，新 prefab 使用自己的回调。装备回调参数和槽位时序继续复用 `EXP-ITEM-004`。来源 `GEAR-S19`、`GEAR-S20`、`GEAR-S21`、`GEAR-S27`。

重复 `StartConsuming` 会保留已有周期任务。`StopConsuming` 同时取消周期任务与待执行首期更新。`SetFirstPeriod` 配置的是额外的首期扣量时间，黄色护符使用它来设置启动消费。普通按时间耗能可按需求选择该配置。来源 `GEAR-S16`、`GEAR-S18`、`GEAR-S20`。

耗尽后要保留照明装备时，可接着查看 `prefabs/hats.lua` 的 minerhat：它分别安装耗尽关灯与补料回调。黄色护符的耗尽删除只代表该物品的选择。

### 段位用于分组

`GetPercent()` 给总量比例。`GetCurrentSection()` 空时为 0，非空时按 `floor(percent * sections) + 1` 计算并以上限 `sections` 钳制。`GetSectionPercent()` 给段内比例，空燃料时会得到 1。显示空量可先按 `IsEmpty` 或段位 0 处理，进度条读总量时直接使用 `GetPercent`。精确扣量用 `DoDelta`，`ChangeSection(n)` 的实际增减量包含 `-1` 偏移。来源 `GEAR-S14` 至 `GEAR-S17`。

初始化段位变化可调用 `sectionfn(new, old, inst)`。普通 `DoDelta` 的段位回调还接收 `doer`，之后才判断是否执行 `depleted(inst)`，最后发送百分比事件。段位回调若改变燃料，最终百分比按之后的实际状态计算。只为切换几个档位效果时，直接在这个回调使用当前对象即可。来源 `GEAR-S17`。

### 通过原版动作补燃料

目标的 `fueltype`、可选 `secondaryfueltype` 与材料 `fuel.fueltype` 匹配，目标 `accepting=true` 时使用现成补料动作。普通 ADDFUEL 会先从库存取单件，再交给 `TakeFuelItem`，正常拒绝时走原动作的返还路径。直接把整叠实体交给 `TakeFuelItem` 会让其 Remove 整个传入实体。来源 `GEAR-S12`、`GEAR-S15`、`GEAR-S22` 至 `GEAR-S25`。

`TakeFuelItem` 的 `fuelvalue` 是乘完材料、湿度、目标倍率与操作者倍率后的投入量。容量钳制后，实际增加量可以更小。需要禁止满量补料的自有物品，可使用现成允许回调。

```lua
inst.components.fueled:SetCanTakeFuelItemFn(function(item, fuel_item, doer)
    return not item.components.fueled:IsFull()
end)
```

该片段用于此前没有自定义接受规则的物品。已有接受规则时保留其判断。`ontakefuelitemfn(inst, item, fuelvalue, doer)` 在材料 Remove 前执行，`ontakefuelfn(inst, fuelvalue)` 在它之后执行。补料后是否恢复运行按装备或开关的当前政策决定。来源 `GEAR-S15`、`GEAR-S25`、`GEAR-S26`。

### 保存数值，构造运行资源

Fueled 在非满时保存当前燃料值，加载用初始化入口恢复。该记录省略 `consuming`、周期任务、速率和表现对象。配置继续由 prefab 构造，装备或开关消费者决定运行状态。恢复零燃料会更新耗尽标签，但加载入口直接采用初始化语义，耗尽回调不会在这里重放。FiniteUses 的零值加载则经过 `SetUses` 的耗尽转换。按各自合同接线即可。来源 `GEAR-S03`、`GEAR-S14`、`GEAR-S17`、`GEAR-S19`。

## 按材料回复次数（EXP-GEAR-002）

次数修复量用 `repairer.finiteusesrepairvalue` 的绝对次数。选择项目已确认的 `MATERIALS` 类型，并为自有材料配置对应值。目标 `repairable.repairmaterial` 使用同一类型。原版橙色护符和噩梦燃料展示了这种匹配。来源 `GEAR-S28`、`GEAR-S31`、`GEAR-S34`、`GEAR-S35`。

```lua
-- 自有维修材料的服务器构造部分。
local repairer = inst:AddComponent("repairer")
repairer.repairmaterial = REPAIR_MATERIAL
repairer.finiteusesrepairvalue = REPAIR_USES
```

目标有限次数变化会更新 `finiteusesrepairable` 标签。如果给一个已经受损的现有物品后添加 repairable，可在这个接入点同步一次 `SetFiniteUsesRepairable(finiteuses:GetPercent() < 1)`。后续继续由有限次数属性变化驱动。新 prefab 也可在设置当前次数前完成 repairable 配置。来源 `GEAR-S01`、`GEAR-S28`。

菜单按材料、可修状态及操作者姿态选择动作，服务器 `Repair` 再检查类型和自定义材料规则。`testvalidrepairfn` 与 `checkmaterialfn` 接收目标和材料，`doer` 只传入后续 `onrepaired`。功能若涉及操作者权限，应在拥有该参数的实际请求入口落实。来源 `GEAR-S30`、`GEAR-S32`、`GEAR-S33`。

修复按 health、workable、perishable、finiteuses 的顺序选择适用分支。给兼具多种状态的目标使用多用途材料时，应确认实际选中哪一种。`NeedsRepairs` 的 95% 门槛用于维修提示文案，实际次数修复检查是否满量。来源 `GEAR-S29`、`GEAR-S37`。

`Repair` 成功路径先修复数值，再消费一件材料，最后调用 `onrepaired(target, doer, original_material)`。多件堆叠消费拆出的单件，单件材料则可能已移除。反馈通常可直接使用目标和操作者，材料信息按实际生存期读取。继续使用有限次数组件的保存数据即可。套件式破损保留与修满沿用已有 forge 接线。来源 `GEAR-S03`、`GEAR-S30`、`GEAR-S36`，以及[物品与维修](items-food-plants.md)。

接入验收围绕本次需求观察扣量、耗尽去向、卸下停止、补料单件数量及维修后耐久。改到保存初值或保留破损状态时，再检查该状态的恢复。涉及菜单与表现的结果需在目标客户端确认。本轮已完成定义、具名消费者与来源位置的静态核对。
