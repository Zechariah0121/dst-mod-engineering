# 船上装置与动力修改的开发入口

目标是给已有船放装置、加动力或制动。先让装置使用船体已有能力，再按功能增加自己的状态。以下依据 762172 的静态 Lua，接入选择属于工程建议。

## 按要做的功能选入口

| 开发任务 | 接入位置 | 装置持有的状态 |
|---|---|---|
| 船上工作台、开关或一次性推进器 | master业务入口查询 `inst:GetCurrentPlatform()`，取得该船 `boatphysics` | 功能本身的开关、消耗或冷却 |
| 修改已有帆的出力 | master帆组件 `SetSailForce`；容量配置由 `max_velocity` 单独消费 | 自己的配置来源，重建时重新应用 |
| 有持续耗能的推进设备 | 装置已有工作更新按 `dt` 提交推力 | 正在工作状态及这份更新的归属 |
| 拖网、阻尼板或降低帆效率的设备 | 装置配置 `boatdrag`，向原船成对 Add/Remove | 原登记船和自己的注册状态 |
| 船上临时停车装置 | 成对 Add/RemoveEmergencyBrakeSource | 原登记船、独立来源身份、功能开关 |
| 船创建且随船消失的外观附件 | `hull:AttachEntityToBoat`，按需要选择父子局部坐标或世界偏移 | 附件若有独立业务数据，明确其保存所有者 |

相关机制见 [EXP-OCEAN-001～003](../knowledge/research/native-mechanisms/ocean_devices_and_boat_motion-55813eecdb8b.json)，包含各入口的参数、返回值、端别、生命周期与来源。

## 船上位置由平台关系维护

原版船在common构造安装 `walkableplatform`，master再安装船体物理等组件。平台manager在服务器后更新中处理普通实体成员、玩家平台和玩家集合提交。船的Physics睡眠/唤醒还控制成员刷新与船体更新。普通无原生父实体的可部署装置沿这套关系跟船移动，装置的业务函数读取当前平台即可。`GetCurrentPlatform()` 返回的平台还可能属于其他平台类型，使用船动力时检查所需 `boatphysics`。来源为 OC-S01～OC-S11、OC-S13。

装置刚生成与平台关系刷新存在阶段差。一次性按钮在执行时现场取船；连续设备在自己的工作更新中取当前平台。固定装置只需在已知平台关联完成处接线。原版mast选择构造后的零延时查询，这提供了一个具体消费者，目标功能仍应依据自己的部署/加载入口安排接线。来源为 OC-S06、OC-S13、OC-S18。

`got_on_platform`、`got_off_platform` 位于本地玩家的非专服表现分支，可供本地镜头、音乐或显示使用。服务器装置直接读取自己的平台关系。`GetEntitiesOnPlatform()` 返回组件当前持有的成员表，需要遍历时把它作为只读集合使用。来源为 OC-S04、OC-S07。

船属外观可以采用Hull的现成所有权。`parent_to_boat=true` 使用原生父子关系和局部偏移，假分支由船安排一次零延时世界位置偏移。方法同时登记船移除时删除附件的回调。原版船唇另行登记platform follower，原版跳板采用父子分支。选择时明确附件是船所有，还是玩家独立部署的结构。业务根实体和视效子实体分别安排保存，沿已有父子/顶层实体保存合同接入。来源为 OC-S12、OC-S10，保存前提沿用 EXP-SAVE-001。

## 短促推进只需要一次船体调用

下面是放在master prefab或组件环境的原创接入片段。方向、每次输入和正的速度尺度由目标功能提供。

```lua
local function PushCurrentBoat(inst, direction_x, direction_z, impulse, speed_scale)
    local boat = inst:GetCurrentPlatform()
    local physics = boat and boat.components.boatphysics
    if physics == nil then
        return false
    end

    local x, z = VecUtil_NormalizeNoNaN(direction_x, direction_z)
    physics:ApplyRowForce(x, z, impulse, speed_scale)
    return true
end
```

这个辅助函数的真值表示已找到接收船并调用入口。原版 `ApplyRowForce` 自身正常返回nil，实际位移由后续船体更新和原生物理决定。Oar的真实消费者同样在划桨发生时取船，再提交一次输入。来源为 OC-S13、OC-S14、OC-S16。

`force` 在这个入口直接参与速度分量累加，函数没有 `dt`。持续设备可在自己的现有工作更新中传入 `strength * dt`，停工时停止这份更新。输入方向先归一能统一不同方向分支的量级。`max_velocity` 在ApplyRowForce中用于前向阻尼曲线，最终硬裁剪使用 `MAX_ALLOWED_VELOCITY`。这几项分别保留在接口参数和功能数值中。来源为 OC-S14。

已有帆的力与容量也分开设置。`SetSailForce` 写入的值仍受帆展开状态和进度比例影响；`max_velocity` 走独立容量计算。原版malbatross帆分别配置这两个字段。船体统一聚合帆、磁吸和阻力，最后写自己的motor。只改帆强度时，可以保留原帆交互、动画和更新接线；新推进器也可直接使用上面的入口。来源为 OC-S15～OC-S20。

## 制动装置只维护自己的贡献

渐进减速设备使用 `boatdrag` 的现成通道。`drag` 增加阻力，`max_velocity_mod` 参与容量乘算，`forcedampening` 降低外部推力响应，`sailforcemodifier` 参与帆力乘算。原版锚的prefab配置这些字段，SG进入相应状态时由anchor成对注册/移除。装置自己的值来自已有玩法要求。来源为 OC-S14～OC-S16、OC-S21～OC-S25。

暂时停车可以只持有一个来源身份和原船引用。开启时调用 `AddEmergencyBrakeSource(token)`，停止、移船或卸载时向原船调用 `RemoveEmergencyBrakeSource(token)`；接入新船前先释放旧船贡献。炮塔消费者使用带自身GUID的字符串，并在自身移除时向捕获的原船释放。这样普通开关装置可以用局部函数完成，无需采用锚的深度进度、多人拉拽与整套SG。来源为 OC-S26～OC-S28。

移除入口会按剩余来源重算 `halting`，全部来源退出后恢复原版船质量。急停的Lua分支将最终motor提交向量置零，内部速度仍有自己的更新与保存。功能需要的重新启动行为据此定义。原版 `SetHalting` 还负责平台处于不良几何位置时关闭所有帆，玩法停车使用来源化接口。来源为 OC-S16、OC-S21、OC-S26。

玩法要求跨读档保留时，再保存所需业务开关，并在平台关联完成后重新登记。原船引用和来源注册是运行期持有的状态，按当前实例重建。原版BoatPhysics保存方向、旋转偏移和速度分量，炮塔的postpass展示了业务方恢复来源的接线。停止时显式调用配对移除入口，使来源表、`halting` 和质量经同一方法更新。来源为 OC-S21、OC-S26～OC-S30。

## 验证实现时只看本次可见结果

一次推进核对服务器接收船、输入方向与船体速度变化；持续设备增加停工后的更新退出。制动装置核对自己的来源退出后其他制动仍保留。功能要求跨读档保留或本次改变了保存路径时，再验证保存重载后的业务状态和平台重新关联。只有做本地提示或交互时再检查对应客户端表现。SetPlatform、motor、碰撞和复制是这里的native边界，源码研究给出调用契约，运行结果由实际装置验证。
