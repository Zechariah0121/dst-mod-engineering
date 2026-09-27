# 图像、图集与动画

适用于库存图标、装备换符号、角色皮肤、SCML 与动画帧序列。先找到同类原版 prefab 的资源声明和调用，再确定要修改的资源层。只改 Lua 行为不必重编美术；改源图后要重建受影响产物。

角色拆件与装备接入流程见 [角色与装备美术](character-and-equipment-art.md)；GIF/WebP、旋转法阵和锚点制作见 [帧序列制作](animation-recipes.md)。这两篇补充制作步骤，名称、资源职责和验收边界仍以本页为准。

## 先分清名称与资源职责

| 对象 | 用途 | 核验位置 |
|---|---|---|
| ZIP 文件名 | 资源加载路径 | `Asset("ANIM", "anim/xxx.zip")` |
| Bank | 动作集合，决定可播放动画 | `anim.bin` 内的 bank/root；`SetBank` |
| Build | 图像、符号与符号帧集合 | `build.bin` 内部名称；`SetBuild` |
| Animation | bank 内的动作名称 | `PlayAnimation` / `PushAnimation` |
| Symbol | build 中可替换的图像通道 | `OverrideSymbol` 第三参 |
| Layer | 动画元素的绘制层 | `Hide` / `Show`；不是所有 layer 都与 symbol 同名 |

这些名称可以不同。原版 `spear.lua` 使用 bank `spear`、build `swap_spear`；原版 `sword_lunarplant.lua` 用 `OverrideSymbol("swap_object", "sword_lunarplant", "swap_sword_lunarplant")`。不能凭 ZIP 文件名推导全部名称，也不能从 `build.bin` 推导 bank。

资源完整性按用途检查：

- 同时提供新动作和新图像：需要对应 `anim.bin`、`build.bin` 和 build 引用的全部图集。
- 只提供换皮/装备符号：允许 build-only，即 `build.bin` 加引用图集。原版 `swap_spear.zip` 就没有 `anim.bin`。
- 只补动作、复用已有 build：允许 animation-only；原版 `player_idles_wilson.zip` 是此类资源。
- 不能为满足“三件套”补造无用动画，也不能无条件删除 `anim.bin`；先查哪些调用依赖它。

## 换符号与手持装备

```lua
owner.AnimState:OverrideSymbol("swap_object", "my_weapon_build", "my_weapon_symbol")
owner.AnimState:Show("ARM_carry")
owner.AnimState:Hide("ARM_normal")
```

第一参是目标角色动画里的符号；第二参是已加载 build；第三参是该 build 里的实际 symbol。帽子、护甲使用各自目标符号和显隐规则，参照同类原版装备，不要把武器的 `swap_object` 当成所有场景的固定参数。

- 純 build 的 `OverrideSymbol` 不会让角色播放 swap 文件内某个 `idle` 或 `BUILD` 动作；角色仍播放自己的动作。某些 SCML 编译模板用 `BUILD` 收集图像是工具约定，不是引擎要求所有 swap 都必须有该动作。
- 常见 SCML 管线以 folder 组织 symbol，以 entity/animation 组织 bank/动作；最终以产物为准。不要强制 folder、timeline、entity、文件名全部相同。
- 无贴图依次查：资源是否加载 → build/symbol 拼写 → 角色动画是否引用目标 symbol → 帧号/朝向 → pivot 与缩放 → 隐藏层和其他覆盖。不能仅凭 build 名出现几次判断正确。
- `AddOverrideBuild` 本身是合法 API，用途不同；只需一个符号时通常用 `OverrideSymbol`。不要写“新版禁止 AddOverrideBuild”。
- 解除效果时只清理本 Mod 拥有的覆盖/显隐；可能与其他装备、皮肤或变身竞争时保留原版恢复路径。

## 图像尺寸、透明与位置

64×64 库存图、128×128 modicon 是常见制作起点，230/256 大小的地面图、200 宽的手持图是项目经验，不是统一引擎下限或强制尺寸。源图尺寸、编译图集尺寸、symbol 几何范围、pivot、动画矩阵、实体缩放和镜头共同影响观感。

- “64×64 atlas 必定加载失败”“长枪宽度必须填满画布”“1024 px 恒等于 1.7 块地皮”不能作为规则。先查资源/图集引用和原版同类资产，再测实际大小。
- 区分源 PNG 与打包后的图集。工具可把非 2 次幂源图打包/扩边到图集；不要强制每张源图都是 2 次幂，也不要擅自改变已有编译管线的尺寸政策。
- 透明背景保留 alpha。白色主体、白色高光不能直接用全局白色阈值删除；检查透明边缘和预乘 alpha，避免白边/黑边。抠图是按需操作，不是每张图都必须执行的三步仪式。
- pivot 表示锚点，不等于画布中心。先在原图标注握持点/落点，导出预览后再调整；不同工具的 Y 方向和归一化约定需核对。
- 缩放和旋转保持长宽比，尽量从原图一次生成结果，避免多轮重采样。图像坐标的正方向、SCML pivot 和世界坐标不同；用简单可视样本确认变换方向。
- 灯光 `inst.entity:AddLight()` 和渲染亮度/泛光是不同机制；只看图片发亮不能证明实体照亮周围。
- `MakeInventoryFloatable(inst, size, offset, scale, swap_bank, float_index, swap_data)` 创建水面漂浮表现；offset 是视觉垂直偏移、scale 控制浮水效果缩放，不是向上推力/阻力，也不负责陆地悬浮。

## 库存图集与 modicon

检查链条：PNG → TEX → XML Texture 路径 → XML Element 名 → 使用者传入的 image 名。XML Element 是图集区域名称，**不必等于 Texture 文件名**，但必须与调用者一致。

通常库存图片使用以下组合：

```xml
<Atlas>
    <Texture filename="my_item.tex" />
    <Elements>
        <Element name="my_item.tex" u1="0" u2="1" v1="0" v2="1" />
    </Elements>
</Atlas>
```

```lua
Assets = {
    Asset("ATLAS", "images/inventoryimages/my_item.xml"),
    Asset("IMAGE", "images/inventoryimages/my_item.tex"),
}
RegisterInventoryItemAtlas("images/inventoryimages/my_item.xml", "my_item.tex")
```

`inventoryitem.imagename` 常写不带后缀的 `my_item`，其 replica 再组成 `.tex` image 名；`RegisterInventoryItemAtlas` 的键应与实际查询名一致，通常带 `.tex`。不要统一要求 XML/注册键去掉 `.tex`。如复用现有图集或使用自定义 image，沿完整调用链核对。

上面的 UV 是整图示意。打包器可能生成半像素内缩坐标；保留其生成结果，避免挨着其他 region 时漏色。图集 Texture 的相对路径要从 XML 所在位置核对，避免重复 `images/` 路径。

`modinfo.lua` 的 `icon_atlas` 指向图集，`icon` 指向图集里的 Element 名。教程把文件拷到根目录是一个有效布局，不是唯一布局。添加图标不需要改变 `client_only_mod` / `all_clients_require_mod`。

## 工具选择与编译

先发现实际安装路径、版本和 help，不用资料夹名当版本。2026-09-27 核验环境快照：DMT 1.1.13；ktech 自报 4.4.0；官方 Mod Tools 有 `scml.exe`、`buildanimation.py`、`image_build.py` 和 Python 2.7。这些是历史快照，不是固定依赖版本；换机器/工具后重新发现。缺少必需工具时进入 [工具安装与首次验证](tool-bootstrap.md)，按实际任务和已有授权处理下载安装，不依据旧版本号自行升级。

| 任务 | 合适工具 | 边界 |
|---|---|---|
| 动画层级、符号、批量编辑与 PNG/GIF 预览 | DST Mod Tool | 先读 [DMT 工作流](dst-mod-tool.md)，先取当前 `script --help` |
| SCML 工程 → 运行时 ZIP | 官方 `scml.exe` | 独立临时输出，检查日志和产物；本次技能重建未重编真实项目 |
| TEX ↔ PNG、TEX 信息、简单 atlas | 已安装 ktech | 只承诺当前 help/实测格式；不能泛称支持所有新 KTEX 压缩格式 |
| 编译资源 → SCML 学习工程 | krane | 反编译不保证完全保真；用 `--check-animation-fidelity` 并抽检 |
| 已有帧序列/中间 XML ZIP → 运行时 ZIP | 官方 `buildanimation.py` | 使用其依赖环境和实际 XML 结构；不是任意 PNG ZIP 都能输入 |
| 遗留图像编译 | 官方 `image_build.py` | 使用匹配的 Python/klei 库，先在临时目录探测路径行为 |

PowerShell 示例（先把变量设为当前环境中已确认的绝对路径）：

```powershell
& $Ktech --help
& $Ktech -i $Tex
& $Ktech $Png $OutputTex
& $Ktech --atlas $OutputXml $Png $OutputTex
& $Krane --help
& $Krane $UnpackedAnimDirectory $OutputScmlDirectory
```

本次对合成 16×8 PNG 的 ktech 检查确认：中文路径可用、TEX 与 XML 都生成、DXT5/5 层 mip、输入 PNG 哈希不变。它证明该安装版本的这条路径，不能推导所有工具/编码/路径都兼容，也不能代替游戏验收。`krane` 当前 help 支持输入 BIN 文件或目录；ZIP 支持按版本验证，不要假定。

官方 SCML 编译通常从 `mod_tools` 工作目录调用：

```powershell
& $Scml $InputScml $TemporaryOutput
```

具体输出位置以该版本实际结果为准。源 SCML 引用图片路径必须可解析；保留源工程和输出之间的映射。

自动编译器不是一概不可用。核验环境的官方 `scripts/resize.py` 确实会对目标 PNG 重采样并保存，整套工具可能运行额外预处理、缓存或清理。需要保护原素材时在隔离副本运行、前后比较哈希，或明确调用单资源编译器。不能据一次事故断言所有 autocompiler 必然破坏透明度/姿态；也不能为强制更新直接删除整个 `anim/`。

## 帧序列与性能

- 没有“所有动画最多 60 帧、149 帧必崩”的通用结论。当前原版 `alterguardian_phase1_lunar.zip` 的 `spawn_lunar` 有 215 帧，`archive_lockbox.zip` 的 `activation` 有 196 帧。
- 时间轴帧数不等于独立贴图数量。内存与解码成本还取决于独立图像、图集面积、mipmap、元素数、并发实例和加载时机。
- 某项目把大图序列重采样到 60 帧后恢复，只能记录为该资产的缓解办法。查清资源有效性和负载，再按视觉质量预算优化，不预先改用户动画时长。
- “同一 symbol 绝不能跨图集”也未建立为通用限制；由支持该格式的打包器生成并检查 build 中的引用，遇到特定管线问题保留最小复现。
- `FRAMES = 1/30` 秒，约 0.033333 秒；动画资源自身 FPS 可以不同。制作端降 FPS 会改变时长，除非同步调整取帧与时间轴；不能把两者混为一谈。
- `AnimState:SetScale` 可以大于 1，原版有 `SetScale(2, 2)`。属性在哪些端设置以同类原版和实机同步为准，不把“SetPristine 前设置”当成所有后续变化的唯一方法。
- `PlayAnimation` 开始播放新动作，`PushAnimation` 接队列。结束回收应对照原版的事件与 `AnimDone()` 用法；循环动画不能靠普通完成事件清理。

## 交付检查

1. 明确是完整动画、build-only 还是 animation-only，核查依赖都已加载。
2. ZIP CRC、BILD/ANIM 版本、图集引用、TEX 格式/尺寸、XML 路径和 Element 名逐项检查；不能以 ZIP 大小或可打印字符串次数代替解析。
3. 用现成工具读 KTEX，不猜固定字段。mip 层数要读头；DXT 块最小尺寸导致尾部 mip 不满足简单 `w*h` 字节公式。
4. 查看原图/导出预览的方向、pivot、透明、层级、朝向、时间轴；角色衣服的“第几张图用于哪动作”是具体 build 的映射，不是全局编号表。
5. 加载/无头运行验证与真实客户端视觉验收分开记录。客户端检查装备、卸下、皮肤/变身、运动方向、特效结束和远程观察。
6. 修改范围内同步 source/runtime，逐文件哈希；保留可重编的源素材和工具参数。资源删减要先查所有引用再隔离测试。

核验依据：当前 `spear.lua:13,37-38`、`sword_lunarplant.lua:115`、`simutil.lua:658-699`、`standardcomponents.lua:1772-1791`、`constants.lua:16`；官方 `buildanimation.py:101-105,168-173,406-422`；核验环境的原版 ZIP 解析与 ktech 探针。工具分工另见 [ktools 作者说明](https://github.com/nsimplex/ktools/blob/master/README.md)，其说明也要求以当前 help 为准。旧教程保留制作思路，具体 API 表与工具命令以这些证据重新核对。
