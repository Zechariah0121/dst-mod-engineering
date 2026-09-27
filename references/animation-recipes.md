# 帧序列、锚点与旋转动画

用于 GIF/WebP/PNG 序列转运行时动画，以及静态图制作旋转效果。资源类型、bank/build、库存图和客户端检查先见 [图像与动画](assets-animation.md)；缺工具按 [工具安装与首次验证](tool-bootstrap.md) 推进，已有 SCML 或可编辑 DMT 工程优先保留，不强制改成逐帧烘焙。

## 先确定输入和时间轴

1. 登记源文件哈希、画布、逐帧时长、透明方式、循环次数、目标锚点和用途。已有手改 PNG 时以明确选定的输入为准，不用旧 GIF 再导出覆盖。
2. 解码 GIF/WebP 时处理帧间合成和 disposal，导出完整 RGBA 帧并保留时长清单；只读取局部更新矩形会丢掉上一帧内容。抽检首尾、透明边缘和帧数。
3. GIF 的透明索引不能保存连续 alpha；需要柔边时保留 PNG/WebP 母版，GIF 只作预览。预览播放器的时长取整不代表引擎实际帧率。
4. 本页所核验的 `buildanimation.py` 对 XML `framerate` 调用 `int()`，再写入二进制 float；因此这条管线需要正整数 FPS，不能据此宣称所有 DST 动画只支持整数 FPS。

每帧原时长为 `d_i` 时，总时长是 `T = sum(d_i)`。固定 FPS 输出有 N 个时间轴帧，其时长约为 `N/FPS`。非均匀时长要按累计时间重采样，允许重复引用同一张 PNG；不可仅用第一帧时长推算整个动画。把 33.33 直接截成 33 会改变时长，是否接受、降帧或改节奏属于设计选择。循环时间轴通常避免把首帧作为末帧再停一次；非循环动画保留完整尾部。

## 透明、缩放与视觉锚点

- 已有 alpha 就保留。黑底发光素材可试 `alpha=max(R,G,B)`，并在非零 alpha 上反算颜色以消除黑底污染；这是特定合成假设，不是通用抠图。黑色主体和阴影可能被删掉，先在黑、灰、白背景预览。
- 白底淡彩图也不能简单反亮度后当成正确 alpha。JPEG 噪声、高光和白色主体都需要检查；固定阈值、gamma、增强倍数只属于具体素材，不写成默认配方。影响观感的“保留淡色/增强颜色”先出对比供用户选择。
- 保留直通 alpha 的源 PNG，并核对编译器是否做 premultiply；已预乘图像再预乘会使边缘发黑。本页工具的 `textureconverter.Convert` 默认给转换器传 `--premultiply`。
- 尽量从母版一次缩放，保持长宽比。`AnimState:SetScale` 只能放大已有细节；图像分辨率、几何尺寸、矩阵、实体缩放和镜头一起决定观感，没有“1 格恒等于 200 动画单位”的通用换算。

对宽 W、高 H 的帧，若目标原点在原 PNG 左上角坐标系的 `(cx,cy)`，本页中间 build XML 可设置：

```text
x = W/2 - cx
y = H/2 - cy
顶点左上角 = (x-W/2, y-H/2) = (-cx,-cy)
```

因此底边中心锚点是 `x=0, y=-H/2`；居中锚点为 `x=0, y=0`。同时缩图和几何时，W/H 与 x/y 同比例变化。先区分“画布中心”“实际落点”“动画矩阵平移”，避免重复补偿。

环形落点的自动定位只是辅助：行宽峰值可避开竖直光柱对整图质心的污染，但非对称环、火花、厚环都可能误判。限定合理区域后检查宽度分布；多行接近峰值时可求加权中心。若各帧内容没有真实位移，采用经确认的常量锚点；只有真实位移才逐帧修正。把所有帧按最终坐标叠到固定原点预览，排除计算造成的抖动，再用 DMT/客户端核对落点。

## 中间 ZIP 与坐标

`buildanimation.py` 输入是中间 XML/PNG ZIP，运行时 ZIP 是另一种内容。完整新动画的最小布局：

```text
my_fx_stage.zip
├── build.xml
├── animation.xml
└── frame_000.png
```

```xml
<Build name="my_fx_build">
  <Symbol name="my_fx_symbol">
    <Frame framenum="0" duration="1" w="32" h="24" x="0" y="-12" image="frame_000"/>
  </Symbol>
</Build>
```

```xml
<animations>
  <anim name="idle" root="my_fx_bank" framerate="30">
    <frame x="0" y="-12" w="32" h="24">
      <element name="my_fx_symbol" frame="0" layername="my_fx_layer" m_a="1" m_b="0" m_c="0" m_d="1" m_tx="0" m_ty="0" z_index="0"/>
    </frame>
  </anim>
</animations>
```

这是说明字段的单帧样例，32×24 和 30 FPS 不是设计默认。多帧时逐项对应 symbol 帧号和时间轴；`duration` 表示 build symbol 帧覆盖范围，不等于 GIF 毫秒时长。`image` 写 ZIP 内 PNG 路径去掉 `.png`；标签及 `animation.xml` 文件名区分大小写。当前编译器把 build、symbol、图像、动画、root 等名称编码为 ASCII，名称使用 ASCII；这不等于所有工具的外部文件路径都禁止中文。

- `SetBank("my_fx_bank")` 取自动画的 `root`，`SetBuild("my_fx_build")` 取自 Build.name；ZIP 文件名可不同。原版 spear 的 bank/build 也不同。
- 矩阵排列为 `x'=m_a*x+m_c*y+m_tx`、`y'=m_b*x+m_d*y+m_ty`；不要交换 b/c，或把图片向下的 Y 直接当世界高度。先用单位矩阵和不对称测试图确认方向，再引入旋转/缩放。
- build 的 x/y 是图像中心偏移。动画 frame 的 x/y/w/h 是包围框信息，不能用其代替 element 平移。旧记录把动画 x/y 固定解释成左上角并归因于裁剪，证据不足：公开官方 SCML 导出代码将包围中心写入 position。本样例采用该约定，复杂变换优先保留当前导出器计算的框，并核对四角变换后的范围，不沿用未经验证的“左上角”修复。
- 动画名的 `_up`、`_down`、`_side` 等后缀会被本编译器识别为朝向并从动作名中拆掉；无意使用保留后缀会改变查找结果。z_index 决定导出排序，不是世界 Z 高度。

坐标依据：[官方 SCML 导出代码](https://github.com/kleientertainment/ds_mod_tools/blob/master/src/app/scml/main.cpp) 的 `export_element`、`extend_bounding_box`、`export_animation_frame`；再对照实际安装版本的 `buildanimation.py`。公开源代码与已安装二进制不自动视为相同版本。

## 图集预算与编译

预算同时考虑独立图像数量、尺寸、透明占用、mipmap、元素数和并发实例。总像素面积只是下界；当前 `klei/atlas.py` 有面积排序、4 像素对齐和空位搜索，不是可用“每行张数×行数”精确预测的纯货架模型。要知道图集数量就运行实际打包器并检查输出。

当前 `buildanimation.py` 默认最大图集边长 2048、带 alpha 默认 bc3；它允许多个 atlas，并在顶点第六个 float 保存 sampler。`atlas.py` 默认还会在空间允许时缩为非正方形。`--square` 是可选布局开关，不是多图集必需修复；“单 symbol 绝不能跨 atlas”不是已证实的引擎限制。出现某管线色块应保留可复现资产，查图集引用、UV、premultiply、几何和客户端效果。

PowerShell：先把变量设为已确认的绝对路径，输出目录选择本次隔离工作区。这里不需要改全局 PATH，也不需要把原工程迁入工具目录。

```powershell
$Compiler = Join-Path $ModTools 'tools/scripts/buildanimation.py'
$Python27 = Join-Path $ModTools 'buildtools/windows/Python27/python.exe'
& $Python27 -B $Compiler --help
if ($LASTEXITCODE -ne 0) { throw '编译环境不可用' }
$CompileArgs = @('-B', $Compiler, $StageZip, '--force', '--outputdir', $OutputRoot)
& $Python27 @CompileArgs
if ($LASTEXITCODE -ne 0) { throw '动画编译失败，请检查完整日志' }
$ResultZip = Join-Path $OutputRoot ('anim/' + [IO.Path]::GetFileNameWithoutExtension($StageZip) + '.zip')
if (-not (Test-Path -LiteralPath $ResultZip -PathType Leaf)) { throw '未生成预期动画 ZIP' }
```

使用随工具的 Python 2.7 和依赖，不用系统 Python 3 执行这份 Python 2 脚本。该版本绝对路径调用已在工具目录外成功；“cwd 必须 tools/scripts”不是固定要求。相对 `--outputdir` 会按输入路径的上级解析，明确绝对路径能避免找错产物。命令成功还要检查日志及二进制，`--ignoreexceptions` 会改变失败处理，不作为日常成功判据；`sitecustomize` 警告也不能仅凭退出码一概忽略。

遇到路径错误先记录工具版本、原路径和编码；必要时在本次独立 ASCII 路径副本重现，不移动原素材。ktech 应按当前 help 使用位置参数及明确 `.png` 输出，不能把无扩展名文件盲当固定 2048² 裸 RGBA。

## 静态图制作旋转效果

先确认是一整层旋转还是内外层独立运动。若现有动画工程能够用多 symbol 和矩阵表达，优先沿用；只有需要逐帧烘焙或工具限制时，才把各层合成为帧序列，不为旧“单 symbol”推断强行合并。

1. 在母版标明环心，必要时查看径向 alpha 分布选择内外层分界。低 alpha 区可减少接缝，但不保证硬切永远无痕；检查旋转后缝隙。
2. 画布需覆盖绕锚点旋转的最远可见点，并留滤波边界。百分位去噪可能切掉合法装饰，不能代替人工检查。每一帧从母版旋转，避免上一帧接着旋转造成累积损失。
3. 按目标时间轴生成角度；不同库正角方向不同，以不对称标记预览确认。双层反向旋转属于设计选择，不自动采用。
4. 抽检全角度裁边、中心漂移、半透明接缝、循环首尾速度和颜色。图集预算不足时比较分辨率、图层复用、帧率和分段加载的代价；拆 bank/build 还要检查切换时机与资源可用性，不直接改变时长。

## 验收与证据范围

按 [资源交付检查](assets-animation.md#交付检查) 分层验证：ZIP CRC；BILD/ANIM 版本与名字；symbol/帧号/朝向；顶点区间、UV 和 sampler；所有图集存在且能解码；时长与原点预览；真实客户端和远端观察。KTEX 用工具读取头和 mip 信息，不把固定字节偏移当成所有版本的通用格式。

FX 公共初始化中的 AnimState 视觉配置参照当前同类原版，保持客户端可见；后续动态变化使用正确的同步或客户端更新路径。`SetPristine()` 不是“所有属性之后永远不能变”的边界。循环动画需明确停止和清理，单次动画用匹配的完成事件/状态回收。泛光 shader 和 Light 照明不同，不能靠泛光掩盖缩放模糊。

2026-09-27 的证据：合成 32×24 PNG 经原装 Python 2.7/compiler 在工具目录外生成 201 时间轴帧的 BILD6/ANIM4/KTEX ZIP，源 ZIP 哈希不变；小图集函数探针产生两个 atlas（64×64、64×32）和 sampler 0/1。原版 `alterguardian_phase1_lunar.zip` 的 `spawn_lunar` 另有 215 帧。这些排除编译器的“60/149 帧硬上限”说法，**不证明任意 201 张大图或跨图集资产已通过客户端渲染**。

本轮未启动游戏、未做真实素材视觉验收；声音制作转到 [音频与粒子](audio-particles.md)，不在此重复维护第二份 FMOD 流程。
