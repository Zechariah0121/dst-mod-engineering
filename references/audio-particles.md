# 音频与粒子特效

本页涵盖声音事件银行和 `VFXEffect` 粒子。动画帧序列见 [帧序列制作](animation-recipes.md)。使用当前项目已验证的音频管线，记录输入、工具版本、事件路径和产物；缺少工具时按 [工具安装与首次验证](tool-bootstrap.md) 检查官方 Mod Tools，不另装一整套无关动画工具。

## 音频资源与事件

已验证的 Designer 管线是素材 → FMOD FDP 工程 → FEV 事件元数据 + FSB 采样银行 → Asset 声明 → `SoundEmitter` 事件调用。`PlaySound` 接事件路径，不接任意 MP3/WAV 文件路径。

```lua
Assets = {
    Asset("SOUNDPACKAGE", "sound/my_project.fev"),
    Asset("SOUND", "sound/my_bank.fsb"),
}

-- 使用实际工程中的完整事件路径。
inst.SoundEmitter:PlaySound("my_project/my_group/hit")
```

项目名、事件组、事件名来自工程，银行文件名可以不同。一组 FEV 可以依赖多个 FSB，不能强制“每事件一对文件”或事件组必须叫 `sound`。声明所需依赖即可，不要求 modmain 和 prefab 两处重复声明。

播放器必须有对应 `SoundEmitter`。需要世界空间定位时使用有正确位置的实体，并配置事件的 3D 模式、距离曲线和参数；2D UI/背景音乐有自己的有效用途，不能一律禁止全局音乐播放器。

循环声音使用本 Mod 唯一的句柄，进入时避免重复启动，离开、实体移除、切换角色/世界时清理同一句柄：

```lua
local SOUND_HANDLE = "my_mod_ambient"
inst.SoundEmitter:PlaySound("my_project/ambient/loop", SOUND_HANDLE)
-- 停止该来源的循环。
inst.SoundEmitter:KillSound(SOUND_HANDLE)
```

监听只在需要的端安装。个人背景音乐由本地玩家的客户端生命周期管理；世界音效参照原版实体/状态机的发声端与网络行为，避免主客机重复播放。死亡事件回调签名是 `function(inst, data)`，原因和攻击者在 `data.cause` / `data.afflicter`；旧教程的 `function(cause, afflicter)` 命名会误导参数含义。

替换事件可使用 `RemapSoundEvent(old_event, new_event)`，先确认影响范围与撤销策略，不为单个角色的声音无意改掉全世界同类声音。

## 选择目标工具

2026-09-27 核验环境中，官方 Mod Tools 的 FMOD Designer CLI 自报 **4.44.7**，随附《FMOD Designer 2010》文档；以下命令针对这一管线。保留已有可工作的 FDP 工程，不因新工具名字就重做工程或升级版本。

工具包也确实包含 **FMOD Studio 1.10.10**、`Template/myDSTmod.fspro` 和 `DST_MOD_ConfigureMasterBank.js` / `DST_MOD_BuildBanks.js`。这些官方文件说明存在另一条候选制作路线，但不证明任意现代 Studio `.bank` 可由当前 DST Mod 直接加载。本轮未构建或加载 Studio 银行；选择它之前，要核对目标版本的 Mod 加载接口、示例工程、Master Bank 标识处理和客户端最小事件验证。官方配置脚本会改工程元数据、触发关闭 Studio；模板构建后批处理还包含复制银行，先审查并改为独立输出，不能盲跑到游戏目录。FEV/FSB 与 `.bank` 流程不可混写。

## 素材加工与响度

保留无损母带和加工参数，先读取文件声道、采样率、位深、时长，再决定裁剪、延迟、回声和增益。44.1 kHz / PCM 16-bit 是兼容排查起点，不是强制唯一格式；mono/stereo 选择按定位与素材设计决定，Designer 支持不同采样率、声道及重采样。

PowerShell 中 `$Ffmpeg`、`$Ffprobe`、`$SourceAudio`、`$ProcessedWav` 是已确认的绝对路径；新输出不能覆盖母版。以下转换仅示范已选定 44.1 kHz、16-bit PCM、双声道的情况：

```powershell
& $Ffprobe -v error -show_entries 'stream=codec_name,sample_rate,channels,bits_per_sample:format=duration' -of json $SourceAudio
& $Ffmpeg -hide_banner -nostdin -n -i $SourceAudio -ar 44100 -ac 2 -c:a pcm_s16le $ProcessedWav
if ($LASTEXITCODE -ne 0) { throw '音频转换失败' }
& $Ffmpeg -hide_banner -nostdin -i $ProcessedWav -af 'astats=metadata=1:reset=0' -f null -
```

直接调用 Windows 可执行文件时传 Windows 路径，由参数数组/调用运算符保持路径含空格的边界；Git Bash 是否转换 `/d/` 受环境影响，不把一次失败写成所有 Windows FFmpeg 的限制。

| 操作 | 可用参数与需要核对的地方 |
|---|---|
| 截取 | `-ss`、`-t` 按秒；切点检查不连续和咔哒声，淡化时长由素材决定，循环接缝不能随意淡空 |
| 回声 | `aecho=0.8:0.8:450\|900:0.4\|0.2` 的 delay 是毫秒；两段延迟/衰减数量对应。数值只是语法例 |
| 延迟 | `adelay=150\|150` 表示双声道各 150 ms；按实际声道数量或当前版本的 `all` 参数处理 |
| 多层混音 | `amix=inputs=2:duration=longest`；`normalize=0` 仅在已设计各路增益时选择，叠加后检查削波 |
| 响度/峰值 | `loudnorm`、`astats` 用于测量或有目标的处理；短音效不能只以综合响度判断听感 |
| 限幅 | 查看 `alimiter` 的自动电平设置；当前版本 `level` 默认开启，设置低 limit 后可能被自动补偿，不等于最终输出已经降低 |

表格中的 `\|` 是 Markdown 转义；传给 FFmpeg 的完整滤镜字符串应使用普通 `|` 并整体加引号。单位与选项依据 [FFmpeg 官方滤镜文档](https://ffmpeg.org/ffmpeg-filters.html#aecho)，执行前再看已安装版本帮助。

峰值目标、增益和回声层数按本次素材与游戏混音确定，不继承其他项目的固定值。过响时沿母带 → 滤镜 → 事件/分类增益 → 叠加声部 → 游戏混音查原因，可在合适层修正；不能禁止代码/事件层调音量，也不能每次一律降低 WAV。保留干净母版，避免重复烘焙游戏播放层的 volume/pitch 参数。

## FDP 工程与 3D 设置

优先使用官方示例或有复用许可且已经验证的工程。FDP 是 XML，但复制另一 Mod 的素材或模板仍要有权限；私人临时脚本与 Workshop 项目名不作为本技能依赖。

1. 在独立副本设置命名空间隔离的项目、事件组、事件、银行名，修正所有音频来源和构建输出路径；一个 FEV 可关联多个 FSB，银行名不必等于项目名。
2. 项目/事件标识符不能无差别逐次 uuid4 替换。需要迁移 GUID 时保持同一旧 ID 到同一新 ID 的映射及内部引用，优先由目标编辑器生成；官方 Studio 的 Master Bank 操作不等同于 Designer 的全 GUID 重写。
3. 声音事件组与混音分类不同。组不必叫 `sound`；分类需与游戏音量滑块路由匹配。事件路径变化后更新全部调用点。
4. 一次性事件在实际工程里核对 One-shot、触发条件和声部释放；循环还要检查 Sound Def 实例、事件时间轴、停止方式和代码句柄。`loopmode=1, loopcount2=-1` 只是旧模板片段，不能跳过字段语义检查。
5. 3D 声音同时需要正确的发声实体位置、事件模式、衰减方式及必要参数；把模板“两处 x_2d 改为 x_3d”不能覆盖所有工程。全局或 world 上的 emitter 不会因此把事件格式改成 2D，但其位置可能不符合预期。2D 同样受事件/分类/游戏增益控制，不代表全图恒定最大音量。

Designer 文档的 Min Distance 是开始距离衰减的位置，具体单位须由目标游戏的坐标和音频尺度确认；`mindistance=3` **不能译成“3 格地皮”**。Inverse 模式的 Max Distance 是停止继续衰减的位置，Linear/Linear Square 通常在最大距离衰减至静音，Custom 可忽略这两个值。按实际曲线做近、中、远距离客户端试听，不能仅填 `3/30` 就宣称有正确空间感。依据随工具文档第 141、376 页；One-shot/循环实例语义见第 144、379 页。

## 编译与交付

先读 CLI help，再检查项目的预/后构建命令。`-m` 列出依赖且不构建银行，`-l` 生成波形银行清单，`-k` / `-K` 禁用工程的预/后构建命令。只有明确需要且已审核的构建动作才另行启用。

```powershell
& $FmodDesignerCli -help
& $FmodDesignerCli -pc -k -K -m $ProjectFdp
if ($LASTEXITCODE -ne 0) { throw 'FMOD 工程依赖检查失败' }
New-Item -ItemType Directory -Path $OutputDirectory -ErrorAction Stop | Out-Null
& $FmodDesignerCli -pc -k -K -l -b $OutputDirectory $ProjectFdp
if ($LASTEXITCODE -ne 0) { throw '声音银行构建失败，请检查完整日志' }
Get-ChildItem -LiteralPath $OutputDirectory -File
```

`$OutputDirectory` 选择本次新的独立目录，`$ProjectFdp` 指向副本；若已有输出，先确认归属，不递归删除整个 sound 目录。实际 FEV 与银行文件名由工程决定，以依赖清单和输出为准，不能假定总是同名一对。修改 WAV 或事件配置后重新构建对应产物，核对其哈希与日志，再同步运行时。

```text
交付目录/
├── sound/             实际需要的 FEV 与全部 FSB
├── source/            可编辑 FDP、音频母版及处理后输入
└── integration.md     事件路径、Asset、循环/3D/混音参数、版本、验证记录
```

每项验收明确证据：

1. **文件与工程**：退出码、完整日志、真实输出路径、输入依赖、FEV 事件及银行引用、FSB 可解析的样本数量/编码/采样信息。`strings` 能找到名字只作线索，不能证明完整事件存在或可播放。
2. **编码**：压缩后大小不必接近 WAV PCM，头部标识也不说明 PCM。“192 字节必为空壳”“FSB5 必崩”均不可作判据。2026-09-27 再查当前 153 个原版 FSB 均为 FSB5，仅证明该容器存在；相同头不等于采样编码、FEV 配套和目标平台兼容。
3. **隔离运行**：专服 `nosound` 下打印 `PlaySound` 之后的标记只证明脚本执行到该处，不能声称事件查找、解码、混音和银行加载全部通过。按 [测试与发布](testing-release.md) 运行行为测试并正常关闭，不复制旧 `os.exit()` / 强杀共享进程的临时 harness。
4. **声音实测**：用目标工具试听作为中间检查，再到客户端检验第一次触发、循环/停止、近远距离、音量滑块、连续触发、多玩家观察和切世界。没有音频输出/客户端时保留这项待验收，不能用银行大小代替。
5. **回修**：记录实际事件、主客机、Mod 列表、输入与银行版本和失败日志。Lua 无异常但客户端退出时结合原生崩溃记录排查，不先认定一定是 WAV 参数或 FSB 版本；未经解析的 dump 也不能当成根因。

本轮核验了 Designer help、官方随附文档、Studio 模板/脚本存在及原版银行头，**没有编译或试听新声音银行，没有验证 Studio Mod 运行时接入**。交付记录应保留这些边界，不把工作流说明写成已完成的声音验收。

## 粒子系统与网络边界

粒子特效可以由 prefab 包装，但并非所有 FX 都是粒子：AnimState 动画、Light、贴地投影也各有机制。当前原版 `cane_candy_fx.lua` 是网络实体、客户端本地发射器的例子：

1. 创建 Transform、Network，添加 `FX` 标签，在共用初始化里 `SetPristine()`，`persists=false`。
2. 专服 `TheNet:IsDedicated()` 返回后不创建本地 `VFXEffect`；主机的可视客户端仍需要渲染，所以不能简单用 `not TheWorld.ismastersim` 取代该判断。
3. 客户端初始化一次命名空间隔离的颜色/缩放 envelope。
4. 建立 emitter，设置渲染资源、最大粒子数、最长寿命、blend mode、曲线、排序和需要的跟随规则。
5. `EmitterManager:AddEmitter` 根据 tick 时间和累积量发射；按实际场景拥有者移除实体/关闭发射，不能让临时特效永远挂着。

原版路径可以直接供渲染 API 使用；Mod 内相对资源路径需要按照加载环境用 `resolvefilepath` 解析，尤其 `SetRenderResources` 这类不替你定位 Mod 根的接口。不能据原版裸路径反过来删掉 Mod 的路径解析。

```lua
local TEXTURE = resolvefilepath("images/fx/my_mod_spark.tex")
local SHADER = "shaders/vfx_particle.ksh"
local assets = {
    Asset("IMAGE", TEXTURE),
    Asset("SHADER", SHADER),
}
```

此处是资源声明片段，完整 prefab 应从当前同类原版裁取，保留全部必需初始化。不要直接复制教程中的示例数值作为设计默认。

## 粒子参数与清理

- 世界空间位置是 x/y/z，其中 y 为高度。绑定父实体后重新确认位置使用局部还是世界坐标，移动拖尾与跟随粒子不一定相同。
- 颜色 envelope 使用归一化生命周期进度和颜色值；`IntColour` 输入通常是 0..255。教程 `IntColour(217,39,390,80)` 明显越界，不应原样继承。
- `AddRotatingParticle` 的 angle 参数不是 UV 坐标。教程变量叫 `uv_offset` 却传给 angle，是误命名/机制混淆；需要图集帧时参考 `AddRotatingParticleUV`、`SetUVFrameSize` 的配套用法。
- 粒子数量、寿命、发射频率一起决定负载。原版代码里的每 tick 随机倍率只代表具体效果，不等于严格的每秒目标数；要精确速率时先定义累积/抖动需求。
- 客户端随机装饰可以各自不同。影响伤害/命中的范围和时刻由服务器判定，不用粒子的位置反推游戏逻辑。
- `persists=false` 仅表示不存档，不代表自动在动画/计时结束时移除。父子关系、事件监听、延迟任务、EmitterManager 注册的清理都要核对；重复进入世界/复活要防止重复生成。
- 混合模式、泛光和 shader 需以当前资产及客户端效果验证；专服 PASS 不证明有画面。需要截图/视频验收时明确抽检的实例、时段和机位，不声称看过未播放素材。

核验依据：当前 `prefabs/cane_candy_fx.lua:16-42,49-65,68-131`、`components/health.lua:590`、`components/dynamicmusic.lua` 的绑定/解绑；核验环境中的 FMOD Designer help；随工具提供的《FMOD Designer 2010》80、142、152-157、205 页；该环境中的 FSB 文件头统计。现代 FMOD Studio 文档可帮助理解概念，不能替代这些 DST 目标版本证据。
