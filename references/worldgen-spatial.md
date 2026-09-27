# 世界生成、地形与空间可视化

用于 room/task/taskset、静态布局、自然生成、地皮、放置范围和运行时地形改动。旧教程提供概念路径；真实参数、枚举和生命周期以当前安装源码为准。世界生成与运行中的世界是不同入口，不直接互抄对象和全局变量。

## 先确定改的是哪一层

| 需求 | 优先入口 | 不足以证明完成的检查 |
|---|---|---|
| 新世界的地貌、资源数量 | `modworldgenmain.lua` + Room/Task/TaskSet hook | 只启动一个旧存档 |
| 固定建筑群、岛屿/奇遇 | static layout + 对应 taskset/setpiece 注册 | 只有 Tiled Lua 能解析 |
| 自定义地皮 | 模组环境 `AddTile`，运行与生成两端一致注册 | 单独改某个数值 ID |
| 种植/建筑可放置范围 | deployable/replica/placer/helper | 只有服务器能成功放置 |
| 运行时填海/室内 | 当前相近原版机制及明确项目约束 | 仅看到一块地皮颜色改变 |

世界生成 hook 不给已有存档自动补内容。若需求包含旧档迁移，要另设版本标记和幂等迁移，并验证生成失败/回滚，不擅自重置世界。桌面测试总用隔离副本与新生成世界。

## Room → Task → TaskSet 与数量

从当前相近 `map/rooms`、`map/tasks`、`map/tasksets` 复制最小结构，使用模组 `AddRoom`、`AddTask` 和限定的 `Add*PreInit` 接入，不替换整张原版定义表。

- Room 描述地块、标签与内容，Task 组织房间/锁钥/连接，TaskSet 选择任务；它们不是运行时 prefab。
- `countprefabs` 是每个对应生成节点的目标数量，值可为数字或接收 `(area, prefab, scratchpad)` 的函数。多个相同 room 会各自处理，不能直接宣称全世界精确 N 个。
- 点数不足、过滤条件和放置失败可能阻止满足数量。先检查世界生成日志，再扫描最终世界/存档核实数量。
- `distributeprefabs` 是权重分布，`distributepercent` 控制密度；不能把目标绝对数量填进权重并期待严格计数。
- 选择所有房间的 postinit 会扩大作用范围；只修改已确认的 room/task，初始化缺失子表并保留无关项。
- `ExitPiece` 是拓扑生成标签，不能用它触发月岛启蒙。当前玩家区域处理检查 `lunacyarea`，经 `sanity:EnableLunacy` 启用；标签语义由消费者定义。

下面仅展示向指定房间登记已确认数量的方式；调用前决定命名、数量和哪些房间应出现：

```lua
local function AddRoomPrefabCount(room_name, prefab_name, count)
    AddRoomPreInit(room_name, function(room)
        room.contents = room.contents or {}
        room.contents.countprefabs = room.contents.countprefabs or {}
        room.contents.countprefabs[prefab_name] = count
    end)
end
```

原版 `areaaware` 每帧检查移动距离阈值，变化到不同节点时才发 `changearea`；不是每帧都广播区域事件。需要更精细边界时先找现有精度接口，避免无条件扫描全部实体/拓扑。

## 静态布局与 Tiled

1. 从当前 `map/static_layouts` 选择相近例子，保留版本与来源。确认地面层 `BG_TILES`、对象层 `FG_OBJECTS`、对象 prefab/type 与属性结构。
2. 通过 `map/static_layout.lua` 的 `Get` 转成 layout，使用唯一 layout 名，接入合适的 setpiece 容器。`map/layouts.lua` 和 `map/object_layout.lua` 是查布局选项与消费者的入口。
3. **Tiled 地面数据是 tileset 索引，不等于运行时 WORLD_TILES 数值。** 当前 `static_layout.lua` 的 `GROUND_TYPES` 执行映射；不要拿旧教程 GROUND ID 表直接填 Tiled layer。
4. 核对 tilewidth、尺寸、对象坐标转换、中心/旋转、可放置地块、预留空间、拓扑属性。不是所有新 Tiled 导出格式都会被旧形状的 loader 自动理解。
5. 检查布局依赖 prefab 和资产，然后多种 seed/世界尺寸实际生成，核实数量、碰撞、海岸通路、客户端小地图。

`ocean_prefill_setpieces` 当前可接受数字、`{ count = n }` 或函数形式的 count；旧教程的 `= 1` **不是类型错误**，源码明确兼容。表形式通常更清晰，不能把风格偏好报告为 bug。`Ocean_PlaceSetPieces` 会记录计划数与放置成功数；数量配置不保证每个布局成功落位。

不要把改变 `OceanRough.value` 为陆地类型视为通用“控制隐士岛离岸距离”API。当前布局有 `min_dist_from_land`，但其效果仍依赖 Ocean 生成阶段、地形空间与布局；按最小隔离实验验证，不用教程给出的全局地块替换捷径。

## 新地皮与运行时地形

当前 `constants.lua` 明确将 `GROUND` 标为 deprecated。新代码使用 `WORLD_TILES.<NAME>`；新地皮走模组环境 `AddTile(tile_name, tile_range, tile_data, ground_tile_def, minimap_tile_def, turf_def)`，由 TileManager 分配 ID。不要占用旧文档所谓 70–89 公共区间，或硬编码客户端/服务器的 ID。

原版 `TileRanges` 是 `tiledefs.lua` 的局部表，不是 `GLOBAL.TileRanges`。注册范围可用已有字符串 `"LAND"`/`"NOISE"`/`"OCEAN"`/`"IMPASSABLE"` 或通过 `RegisterTileRange` 注册的名字。`AddTile` 会把 tile 名转成大写，随后读取 `WORLD_TILES.MYTURF`，不是小写字段。

模组环境 `AddTile` 会在调用内管理 TileManager 保护标记。直接 `require("tilemanager").AddTile` 可能命中保护断言；不要修改全局保护开关或把代码硬塞进 `tiledefs.lua` 的初始化窗口。注册要在客户端、服务器及 worldgen 需要的入口保持一致；可用公共 modimport 文件避免漂移，并注意同一环境不要重复登记。

定义参数需从 `tilemanager.lua` 的 Validate 函数和当前 `tiledefs.lua` 的相近地皮读取：地面/边缘噪声、脚步声、小地图、turf、挖掘/铺设/临时地皮标记是不同职责。是否需要自有纹理、旧档 ID 映射、移除模组后表现均按实际需求验证。

`d_ground("DIRT")` 当前是调试捷径：在位置取 tile 坐标后调用 `Map:SetTile`。使用字符串能避开旧数值，但该函数不构成完整填海系统。运行时 wrapper 会发 `onterraform`；原版 terraformer 还处理原地皮、undertile 与掉落。不要把调用 `SetTile(x, y, tile)` 自动等同于清除 undertile，它有单独的 `ClearTileUnderneath` 接口。填海需逐一验证水陆通行、船/平台、海岸与小地图、实体位置、拓扑/区域、存档及远程客户端。不能把“保存重进看起来正常”推导为全部成立，也不默认伪造拓扑。

## 放置范围与局部提示

当前 `firesuppressor` 仍使用非 dedicated 端 `deployhelper`、本地不联网的 helper 实体，以及 placer 的 `LinkEntity`。教程的这个结构可保留。

- helper 可使用 `CLASSIFIED`/`NOCLICK`/`placer`、`persists=false`、父子实体关系，但这些 tag 不是通用网络权限机制。
- helper 启用时创建，关闭时删除；重复开关必须幂等，不能累积圈或更新任务。
- 显示缩放值受原图/动画坐标影响，教程 `1.78` 或原版 flingo 的 `1.55` 不是“米→缩放”的通用换算。以服务端实际半径核对圈边界，考虑父实体缩放。
- placer 的 `LinkEntity` 用于关联附属预览表现；tooltip/范围圈只负责表达，不改变服务器可部署条件。
- 种植自定义规则优先共用 `_custom_candeploy_fn` 与 CUSTOM 模式，见 `items-food-plants.md`。几何放置等 mod 必须用当前版本实际验证，不能仅声明兼容。

## 小房子与室内方案的边界

旧 `sample-smallhouse.md` 只是问题列表和外部 mod 链接，没有完整实现。不能当作已经验证的 DST 室内框架，也不能将“屏蔽全部世界状态”“移去远处”照搬成安全默认。

真正实施前集中确认：独立分片还是同世界离场区域、入口/出口与返回点、多人共享/独占、死亡/下线/迁移、季节天气/光照、地图可见性、寻路/相机、空间分配和存档生命周期。然后检查当前类似机制，制作最小可进入/退出/重载/第二玩家加入原型。视觉隔离和服务器实体隔离分别验证。外部方案未取得源码或未运行的部分写“待证”，不要靠旧链接背书。

## 当前原版检索入口

| 主题 | 已核验入口，行号以 2026-09-27 核验环境快照为准 |
|---|---|
| 新地皮与旧 ID | `constants.lua:681-802,805-834`；`modutil.lua:356-375` → `tilemanager.lua:118-209`；`tiledefs.lua` |
| 房间内容数量 | `map/graphnode.lua:340-403`；`map/rooms`、`map/tasks`、`map/tasksets/forest.lua` |
| 海洋布局 | `map/forest_map.lua:877-886` → `map/ocean_gen.lua:616-657`；`map/tasksets/forest.lua:61-66` |
| Tiled 解析 | `map/static_layout.lua:27-95` → `map/object_layout.lua`；`map/layouts.lua` |
| 区域与启蒙 | `components/areaaware.lua:45-90` → `prefabs/player_common.lua:581-584`；`map/storygen.lua:123-139` |
| 地形改动 | `debugcommands.lua:1010-1019`；`components/map.lua:3-8`；`components/terraformer.lua:16-32` |
| 范围预览 | `prefabs/firesuppressor.lua:239-273,308-312,460-490`；`components/deployhelper.lua`；`components/placer.lua` |

验证报告分开记录：Lua/数据结构检查、新地图生成结果、服务器运行与存读档、真实客户端视觉和多人行为。单个固定 seed 成功不能证明所有生成条件可用。
