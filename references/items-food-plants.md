# 物品、武器、料理与植物

用于修改物品机制、修复菜单、制作配方、锅料理或生长/种植。先读当前相近 prefab，再追组件和调用端。此页片段用于说明接口，不是含资产、数值、网络声明的完整 prefab。

新增独立锅料理的配方、调味变体、图标与台词交付流程见 [料理制作](cooker-dishes.md)。

## 物品与武器的实施顺序

1. 从最接近的原版物品确定：手持/穿戴槽、攻击类型、耐久类型、破损后删除还是保留、拾取堆叠、沉水/漂浮、资源名。
2. 公共区建立 Network、动画、客户端必要 tag/数据和浮水；`SetPristine()` 后分离服务端组件。完整边界见 `entities-components.md`。
3. 服务端用 `weapon`、`finiteuses`/`fueled`、`equippable` 等已有组件实现；`SetMaxUses` 设置上限，`SetUses` 设置当前值，二者不是同一个操作。
4. 回调把装备者作为明确参数处理；数值修改用可撤销的 source/key，不能覆盖其它装备的全局倍率。卸下、中断、死亡、存读档都需恢复一致。
5. 查明伤害入口和耐久消耗点，再决定是否需要自定义动作/SG；已有 `weapon`/`projectile` 能实现时不额外手动扣血。

`damagetypebonus:AddBonus(tag, source, multiplier, key)` 的第三参是乘数。`1.1` 表示增加 10%，`0.1` 表示原伤害的 10%，`1` 是不变。位面伤害走特殊伤害和位面防御链，不能表述为无条件忽略一切防御。使用 `planardamage:SetBaseDamage`/`AddBonus`/`AddMultiplier`，按数值需求选择，不猜对称 API 名。

`projectile.has_damage_set` 控制某些武器作为 owner 的情况下使用投射物自身 weapon，**不是防止重复伤害的开关**。`Projectile:Hit` 已会经 `combat:DoAttack` 攻击；自定义 `onhit` 再手工攻击可能重复结算。弧线落点用 `complexprojectile` 等相近原版；Physics 连续飞行和任务位移按命中语义选择，不能仅因旧 mod 用哪种便判优劣。

自定义投掷动作要完成“客户端选动作 → 发送目标/落点 → 客户端预览 SG → 服务端 SG → action.fn/发射 → 命中与移除”全链。`BufferedAction.pos` 是 `DynamicPosition`，用 `GetActionPoint()` 取得世界落点；`canforce` 涉及强制动作和范围处理，**不是保证坐标同步的必填开关**。当前服务端某些 canforce 分支还会重写动作点。旧 throw-chain 示例未给 `_my_target` 赋值，不能当完整模板。只在权威端发射和扣费，声音/画面同步逐个按所选实体与实际路径验证，不把“所有 SoundEmitter 都不跨端”当结论。玩家动作注册/中断参见 `characters-brains-stategraphs.md`。

## 修复机制：先选原版合同，再验证菜单

| 需求 | 当前入口 | 应检查的边界 |
|---|---|---|
| 按材料数值回复工作量/生命/新鲜度/耐久 | `repairable` + `repairer` | `MATERIALS`、材料 tag、可修状态 tag、服务端再次验证 |
| 原版套件式修满，破损保留并修复 | `MakeForgeRepairable` + `forgerepair` | `FORGEMATERIALS`、破损/修复回调、初始化/读档后的状态 |
| 赠送材料触发独特效果 | `trader` + 原版 GIVE 或限定的自定义动作 | 接受测试、消费数量、拥有者权限、失败原因 |

当前 forge 明确支持 `finiteuses`：`finiteuses` 的属性钩子更新 `forgerepairable`，`forgerepair:OnRepair` 调用 `finiteuses:SetPercent(1)`；原版 `sword_lunarplant` 和 `voidcloth_scythe` 正在使用。旧文档的“forge 废弃/永远不能修有限次数武器”错误。

材料和目标的权威组件通常在服务端添加；动作组件登记与网络 tag 让客户端挑选动作。菜单缺失应逐层查 `RegisterComponentActions`、材料枚举、tag、骑乘/持重等条件，不能把 `repairer` 无条件移到两端。`USEITEM` 回调不能依赖客户端不存在的 `target.components.trader`；客户端用实际同步的信息筛选，服务端 `CanAccept`/`Repair` 再决定是否成功。

不要为了一个武器把原版 `nightmarefuel.components.repairer.repairmaterial` 改成独占自定义值，这会改变原本修复对象。优先复用既有材料合同，或使用独立材料/限定动作。材料枚举和名称属于设计选择，未约定时询问。

`SetUses` 在归零路径可能先发出负百分比再钳到 0；需要保留破损物品并且观察到 UI 残留时，可在自己的破损处理末尾再次同步 0。不要把此项目修复扩大成所有物品都必须重复 `SetUses(0)` 的规则。消费堆叠材料只取单件，不能 `inst:Remove()` 删整组。

## 制作配方与蓝图

当前环境版签名为 `AddRecipe2(name, ingredients, tech, config, filters)`；可选项放 `config`，不是旧 `Recipe` 的位置参数。以下函数只展示已获批准的数据如何接入：

```lua
local function RegisterItemRecipe(name, ingredients, tech, atlas, image, builder_tag)
    return AddRecipe2(name, ingredients, tech, {
        atlas = atlas,
        image = image,
        builder_tag = builder_tag,
    }, { "WEAPONS" })
end
```

- `builder_tag`、技能限制、`nounlock`、`product`、`numtogive`、placer、过滤器分别核对当前 `recipe.lua`/`builder` 消费者；更改 tag 后必要时更新制作菜单。
- 科技值查 `constants.lua` 中 `TECH` 和相应 prototyper，不能把相似枚举一概解释成同一个科技站。`TECH.LOST` 是高科技门槛，不自动决定蓝图从哪掉落。
- `blueprint.lua` 只为满足 `CanBlueprintSpecificRecipe` 的配方创建具体蓝图；`nounlock` 或 `builder_tag` 会排除，至少一个科技值大于 0 只是另一条件。先确认具体蓝图已注册再加掉落。
- 改解锁方式时追踪旧掉落、teacher 与存档已学配方，不能机械删除所有旧代码；是否迁移由项目设计决定。
- Inventory `imagename`、配方 `image`、XML Element 名与注册接口对 `.tex` 的约定不同。逐处追消费者；图标可映射到不同图集，不要求所有文件名完全相同。

## 锅料理：配方数据与可食实体是两层

注册 `AddCookerRecipe("cookpot", recipe)` 只提供烹饪规则，不替代产品 prefab。按需求为其它锅分别注册；环境版已经标记为 mod food，第三个 `true` 参数不是必要开关。

1. 定义 ingredient tags，复核 `AddIngredientValues` 会替换该名字原有 tags；修改原版食材时不能不知情覆盖全部属性。
2. `recipe.test(cooker, names, tags)`：`names` 为具体食材计数，`tags` 为累计食材值，允许字段缺失。准确数量用比较而不是仅判断真值。
3. `priority` 决定候选最高档；同档按 `weight` 选择。根据用户想保留的原版料理测试组合，不能一律 `priority >= 30` 抢优先级。
4. 明确写入正数 `weight`。当前排序/总和部分虽有 `or 1`，实际抽取减法仍直接使用 `weight`；遗漏项被选中处理时可能报错。
5. 产品 prefab 有完整 Network/Pristine 分界、edible、perishable、inventoryitem/stackable、名称台词、资产和实际饮食分类。
6. `preparedfood` 是原版调味链使用的协议。若允许调味，还需对应调味配方和产品 prefab；仅加 tag 不完成接入。`FOODTYPE` 当前无 FISH，鱼类食材 tag 与 `edible.foodtype` 不是同一集合，按实际饮食设计选有效枚举。

下面只定义一个“精确三类食材计数”测试器，数量和合法 ingredient key 由已确认设计提供；这避免教程“想要 1 蛋 2 灰 1 硝石，代码却仅检测存在”的偏差：

```lua
local function MakeExactIngredientTest(expected)
    return function(cooker, names, tags)
        for name, count in pairs(expected) do
            if (names[name] or 0) ~= count then
                return false
            end
        end
        for name, count in pairs(names) do
            if count > 0 and expected[name] == nil then
                return false
            end
        end
        return true
    end
end
```

## 植物、生长与种植

`growable` 的 stages 至少区分：`fn` 应用某阶段静态状态，`time` 函数给该阶段剩余生长时间，目标阶段 `pregrowfn`/`growfn` 在转移时执行。`SetStage` 本身不代表设置新计时，应检查当前任务是否需重启。

**`time = nil` 不表示暂停：缺少 time 函数会回退 10 秒。** 停止用 `StopGrowing()`，或给 `time` 提供返回 nil 的函数；自然转移到非循环最后阶段时组件会停止，但手工在最后阶段 `StartGrowing()` 仍不能据此假定不建任务。`growonly`、`loopstages`、休眠/离线追赶、魔法生长各有独立语义。

```lua
local function NoFurtherGrowth(inst, stage, stagedata)
    return nil
end

local function ConsumeOneSeed(inst)
    local item = inst.components.stackable ~= nil
        and inst.components.stackable:Get() or inst
    item:Remove()
end
```

种植流程先验证并成功创建树苗，再消费一颗种子；失败不要消耗整叠。选 `DEPLOYMODE.PLANT`/DEFAULT/CUSTOM 时读两端实现：当前 `deployable:CanDeploy` 与 `inventoryitem_replica:CanDeploy` 都支持实体字段 `_custom_candeploy_fn`，需要自定义时将纯查询函数放公共初始化，并设置 CUSTOM。无需默认 monkey-patch 整个 replica。客户端显示可种，服务器仍需重新校验。

树木还要核对：各阶段动画是否真实存在、砍伐/挖树桩、燃烧/烧焦、掉落、风摆/物理、季节/魔法增长、守卫生成、自然生成与种植初始阶段、存读档。洞穴 0.75 倍、四阶段、默认高大等均是某项目设计，不能成为所有植物的硬规则。

## 证据与验证入口

在当前原版 scripts 下按函数名检索；行号仅为 2026-09-27 核验环境的快照定位，源码基线见 [environment-tools.md](environment-tools.md)：

| 主题 | 定义与调用链 |
|---|---|
| 物品骨架、装备 | `prefabs/spear.lua`；`components/equippable.lua:68-122` |
| 伤害、投射物 | `components/damagetypebonus.lua:10-53`；`components/planardamage.lua`；`components/spdamageutil.lua:23-30,99-119`；`components/projectile.lua:225-251` |
| 投掷落点与强制动作 | `bufferedaction.lua:2-9,90-96`；`components/playercontroller.lua:5068,5107-5113`；`actions.lua:310-320` |
| 修复菜单与结果 | `componentactions.lua:1279-1299,1679-1699` → `components/repairable.lua:106-182` / `forgerepair.lua:28-60`；`standardcomponents.lua:1851-1884`；`finiteuses.lua:1-7,64-78` |
| 配方与蓝图 | `modutil.lua:732-749` → `recipe.lua:229-234`；`prefabs/blueprint.lua:44-74,241-249` |
| 料理 | `modutil.lua:643-646` → `cooking.lua:9-29,46-68,238-287`；`prefabs/preparedfoods.lua:43-149`；`preparedfoods.lua` |
| 生长与种植 | `components/growable.lua:42-78,121-148,207-218,249-311`；`components/deployable.lua:104-146`；`components/inventoryitem_replica.lua:327-352`；`prefabs/pinecone.lua:3-16` |

按实际改动验证：装备/卸下与伤害只结算一次；破损后修复菜单与消费；配方可见性/科技/蓝图；食材正例反例和冲突组合；种植剩余堆叠数量；生长、休眠、保存后重载。显示资源、客户端动作预测、远程玩家菜单与几何放置兼容必须用真实客户端，语法或无头成功不能代替。
