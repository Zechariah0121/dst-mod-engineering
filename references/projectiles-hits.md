# 自定义武器与投掷物的发射、命中和结束

来源与 API 合同：[机制研究](../knowledge/research/native-mechanisms/projectiles_impacts-8c22a47a44b1.json)。

本篇按 762172 / build 26474873 静态源码整理，配套 EXP-PROJ-001～003。下列接入选择属于工程建议，玩法数值、消耗阶段、阵营及环境影响由具体需求决定。游戏、专服与真实客户端效果尚待验证。

## 从实际命中需求选入口

| 需求 | 复用入口 | 本功能需要决定 |
|---|---|---|
| 发射一枚攻击指定实体的弹体 | weapon:SetProjectile + projectile | 跟踪方式、伤害来自哪里、射程和回收 |
| 投出手里的单件物品，飞到坐标或目标附近 | 现有 TOSS + complexprojectile | 弹道参数、落地后效果或留地 |
| 纯落地范围战斗效果 | complexprojectile 的 onhit + 选定 combat:DoAreaAttack | 中心实体、攻击者、倍率、盟友/PvP筛选 |
| 带工作量破坏、点火和世界事件的爆炸 | explosive:OnBurnt | 环境后果、栈数、伤害与仇恨归属 |
| 飞行中穿透或命中任意沿途对象 | 符合需求的原版消费者，或自有检测 | 查询条件、重复命中与终结策略 |

既有伤害、防御和回调阶段见[战斗与Buff](combat-buffs-containers.md)，普通物品创建、网络边界和动作注册见[物品与武器](items-food-plants.md)。对应知识为 NC-N004-FINAL-01/02/03，原来源范围继续保留。本篇补发射参数、具体 prefab 接线和落点后果。

## 一条可以照着接线的普通远程武器路径

猎犬牙吹管提供一个完整消费者。容器装弹后设置 projectile prefab、攻击距离及状态选择标签。服务器攻击进入 Combat:DoAttack，远程分支调用 Weapon:LaunchProjectile，生成独立的 houndstooth_proj，并调用 Throw。弹体自带 weapon、位面伤害和有限射程，普通 Hit 完成默认伤害，再由回调回收。原武器的发射后回调从容器移除一件弹药。

```text
已受理的 ATTACK
  → 对应服务端 SG 的效果时点
  → Combat:DoAttack
  → Weapon:LaunchProjectile
  → Projectile:Throw
  → 普通弹体目标/射程检测
  → Hit → 默认 DoAttack → 命中回调
  或 Miss → 未命中回调
```

新物品先沿自己的公共 prefab 初始化建立网络、物理、动画和必要 tag，再在 mastersim 分支配置组件。下段只展示两种 prefab 的服务端接线，`cfg` 中的速度、伤害和距离由玩法提供。

```lua
-- 发射器的 mastersim 初始化。
inst:AddComponent("weapon")
inst.components.weapon:SetDamage(cfg.melee_damage)
inst.components.weapon:SetRange(cfg.attack_range, cfg.hit_range)
inst.components.weapon:SetProjectile("my_projectile")

-- my_projectile 的 mastersim 初始化。
inst.persists = false
inst:AddComponent("weapon")
inst.components.weapon:SetDamage(cfg.projectile_damage)

inst:AddComponent("projectile")
local projectile = inst.components.projectile
projectile.has_damage_set = true
projectile:SetSpeed(cfg.projectile_speed)
projectile:SetHoming(cfg.homing)
projectile:SetRange(cfg.projectile_range)
projectile:SetHitDist(cfg.hit_distance)
projectile:SetOnHitFn(inst.Remove)
projectile:SetOnMissFn(inst.Remove)
```

这里把伤害放在弹体自身。公共初始化还需相应的 `weapon`、`projectile` 等 tag，以及所选攻击入口实际需要的物品/装备配置。普通远程攻击可以沿现有玩家动作和 SG，额外 SG 仅服务确实新增的时序或中断行为。原版吹管的 `blowpipe` 标签选择吹箭状态只是一个具体表现方案。

### 跟踪、直飞和命中对象

`projectile` 默认跟踪传入的单一目标。`SetHoming(false)` 保留初始方向，普通组件仍只对传入目标做命中距离检查。需要穿过路径时攻击沿途其他实体，应选择相应检测消费者。

`range` 从发射起点计算，严格超过该距离才走 Miss。非跟踪模式在原目标失效时仍可继续飞行，因此有限射程在这种设计里有实际结束作用。猎犬牙弹体采用非跟踪加固定 range。物理碰撞形状、命中余量和高速表现按具体弹体验证。

### 谁是攻击者，谁提供伤害

`Weapon:LaunchProjectile(attacker,target)` 对普通弹体调用 `Throw(launcher,target,attacker)`。弹体保存 owner=launcher，命中时通过 launcher 当前 inventoryitem.owner 解析攻击者。`has_damage_set=true` 且弹体有 weapon 时选择弹体提供伤害，否则该分支使用发射武器。

另一条原版路径是直接投掷物品。Combat 从库存取出一件吹箭，调用 `Throw(attacker,target)`。此时 owner 是攻击者，伤害武器是投出的物品。需要发射器销毁后仍能命中的功能，可以在已经确定的权威发射点采用“生成自带 weapon 的弹体，再 Throw(attacker,target)”这条合同，发射实现只选择一个入口。

默认武器 owner 模式依赖发射器的后续持有关系。最后一次发射若立即删除发射器，成功脱离库存/装备时会清 inventoryitem.owner，后续 Hit 可得不到攻击者而跳过默认伤害。`has_damage_set` 只决定伤害武器，攻击者仍经过前述解析。发射时属性快照和攻击者消失后的规则则按具体玩法确定。

### 资源消耗按发射或命中选择

普通 Hit 后的 Combat 链会调用所选伤害武器的 Weapon:OnAttack，其 finiteuses 可在此扣减。

- 使用发射器伤害武器，并保留默认战斗磨损时，命中链承担该耐久消费。
- 自己在发射时消费同一发射器耐久时，按需求替代默认消费，或用该物品的 `finiteuses:SetIgnoreCombatDurabilityLoss(true)` 关闭默认战斗磨损。两处都扣属于另一种明确的玩法策略。
- 使用弹体自身 weapon 时，默认 OnAttack 随该伤害武器执行。发射器的按次弹药或耐久在其选定入口处理。猎犬牙吹管的实际策略是发射后消费容器弹药。

`onprojectilelaunched(item,attacker,target,proj)` 在 Spawn 返回 nil 时仍可调用，`proj` 因而可缺失。消耗是否要求实际生成弹体由该物品规则决定。若扣费可能删除发射器，还需采用上一节选定的归因方式。

### Hit、prehit 和 Miss

`SetOnPreHitFn` 的回调接收 `(projectile,attacker,target)`，发生在默认伤害之前。猎犬牙弹体在这里生成目标尚活着时的冲击特效。普通 `SetOnHitFn` 的同形回调位于默认伤害之后，伤害链若已移除弹体会跳过它。命中回调适合追加已明确的效果和回收。

Miss 先 Stop 再回调。Stop 清 owner、target 和更新，Hit/Catch 还明确停物理，实体回收由所选 prefab 负责。只销毁的一次性弹体可使用 `inst.Remove` 作为命中和未命中回调。可拾回、返回或落地保留的弹体则配置对应结束行为。

源码定位为 `components/weapon.lua:123–157`，`components/projectile.lua:160–301、367–489`，`components/combat.lua:1168–1242`，`prefabs/houndstooth_blowpipe.lua:69–96、198–232、279–312`，`prefabs/blowdart.lua:31–113、229–250`。

## 坐标抛射先复用默认落地链

可投掷物添加 `complexprojectile` 后，可由现有 TOSS 动作取得实际物品并拆出单件。TOSS 有实体目标时取目标位置并设置 targetoffset.y=1.5，否则取 BufferedAction:GetActionPoint，然后 `Launch(pos,doer)`。普通服务端 throw 状态的时间线执行该动作，其他角色和特殊投掷状态按实际入口选择。

典型配置是速度、重力、起点偏移、`SetOnLaunch(fn)` 与 `SetOnHit(fn)`。月亮炸弹在 launch 回调切换飞行物理/动画，在 hit 回调安排爆炸。只需落地效果时可以保留默认更新。

`Launch(targetPos,attacker,owningweapon)` 保存攻击者和可选武器身份，缺省 owningweapon 为弹体自身。它会改写传入的 `targetPos.y`，调用方需要保留原坐标时传入独立位置值。配置名 horizontalSpeed 参与发射角与速度计算，`usehigharc` 选高/低解；速度不足时存在 30 度回退，所以 Launch 的 nil 返回值无法说明落点是否可达。需要按距离选速度时可使用现有最小速度计算入口，并提供实际参数。

默认更新在下降且高度不高于 0.05 时调用 `Hit()`，回调因此可能收到 nil target。回调实际参数是 `(projectile,attacker,target)`，武器身份从 `projectile.components.complexprojectile.owningweapon` 读取。Hit 先 Cancel，停止速度与更新，再由回调安排伤害、FX和删除/留地。

需要额外飞行检测时才配置 `SetOnUpdate(fn)`。它只传 projectile，truthy 返回接管本轮默认运动、重力和落地处理，nil/false 则继续。炮弹的飞行扫描服务穿透和海面对象等需求，普通落地炸弹可以使用较短的默认路径。

源码定位为 `actions.lua:3953–3999`，`components/complexprojectile.lua:44–84、85–211`，`prefabs/bomb_lunarplant.lua:15–50、138–163、180–249`，`prefabs/cannonballs.lua:142–177、243–268`。

## 落点范围效果选择谁来结算

只需要战斗范围效果，可以在落地回调中以仍有效的弹体作为 DoAreaAttack 的中心。首参 target 提供中心位置，查询分支会排除中心实体和调用 combat 的攻击者。`validfn(candidate,attacker)` 接实际敌我/PvP规则。

- 调用角色的 combat 时，伤害与归因沿该角色的 CalcDamage，武器参数可指定弹体自身的 weapon。该入口还读取当前 combat.areahitdamagepercent，倍率应与本功能预期一致。
- 调用弹体自身的 combat 时，来源就是弹体。原版炮弹以这种方式配置默认伤害和范围倍率，再在 OnHit 调用 `inst.components.combat:DoAreaAttack(inst,...)`。

如果需要建筑工作量、点火、栈数放大、dock损伤、相机与世界 explosion 事件，再使用 explosive。`OnBurnt(target)` 可只处理指定目标，外围相机、dock和世界事件仍按方法执行。它最终删除爆炸物，后续 FX 可像月亮炸弹提前缓存位置。

`SetAttacker` 或 `SetPvpAttacker` 保存的实体用于仇恨建议及所列 PvP 分支，实际伤害仍以爆炸物作为 GetAttacked 的攻击者。月亮炸弹按发射者标签选择 pvpattacker，其他玩家被该伤害分支过滤，自己及非玩家仍可符合条件。这个组件的环境后果和归因需要逐项符合需求，单纯范围技能可直接选择前面的 combat 路径。

源码定位为 `components/combat.lua:1312–1340`，`components/explosive.lua:1–158`，`prefabs/cannonballs.lua:53–140、243–268`。

## 按本次改变检查

静态接线先核对实际 owner/attacker/伤害武器、callback 参数与结束消费者。更改按次消耗时重点看默认命中磨损及最后一次发射，更改飞行时看目标退出或有限射程，更改落点效果时看阵营、范围倍率和所选环境副作用。涉及真实玩家输入、预测或网络表现时，再检查相应客户端路径。已有未改变的伤害链和基础动作证据可以直接复用。
