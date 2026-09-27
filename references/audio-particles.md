# 音频与粒子特效

本页涵盖声音事件银行和 `VFXEffect` 粒子。动画帧序列见 [图像与动画](assets-animation.md)。新工具名称不能替代兼容性验证；使用当前项目已验证的管线，并记录输入、工具版本、事件路径和产物。

## 音频资源与事件

标准 Mod 声音路径是素材 → FMOD 工程 → FEV 事件元数据 + FSB 采样银行 → Asset 声明 → `SoundEmitter` 事件调用。`PlaySound` 接事件路径，不接任意 MP3/WAV 文件路径。

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

## 编译和音质检查

2026-09-27 核验环境中，官方 Mod Tools 的 FMOD Designer CLI 自报 **4.44.7**。目录中同时存在 FMOD Studio，并不能证明任意 Studio 新版产物可直接替换 DST 的已验证银行；先对照目标引擎和官方示例。不自动下载安装旧教程附件或新版本。

先读取当前 CLI help。已安装 Designer 的只读 help 列出 `-pc`、`-b` 输出目录、`-m` 依赖清单、`-l` 银行列表，以及 `-k` / `-K` 禁用工程的构建前/后命令。接手第三方 FDP 先审查其路径、事件和构建命令。

```powershell
& $FmodDesignerCli -help
# 实际编译前先创建独立输出目录，确认工程和素材路径。
& $FmodDesignerCli -pc -k -K -b $OutputDirectory $ProjectFdp
```

本次技能重建只验证了 CLI 帮助、官方文档和现有原版银行头，**没有重编/试听新的声音银行**。上述编译参数来自当前 help；真实工程仍需按下列步骤验收。

- 保留无损母带。44.1 kHz / PCM 16-bit 是可选工作起点，不是 DST 只能接受的唯一采样率/位深；声道选择取决于空间定位和素材。Designer 官方文档支持多种采样率、mono/stereo/多声道及重采样设置。
- 压缩格式不是必须 MP3。选择目标工具/平台支持的设置，检查循环接缝和音质。大小不可能对所有压缩方式都接近 WAV PCM 字节数。
- 声音事件组与混音分类不同：自定义组名可命名空间隔离；分类需要与目标游戏音量滑块路由一致，参照当前官方样例/工程，不能从旧截图推导任意固定名字。
- 音量取决于素材响度、事件增益、叠加声部、衰减与游戏混音；`peak=-10 dBFS` 是旧项目经验，不能一刀切。记录峰值/响度并在游戏里与同类音效对比。
- 裁剪避免接缝爆音，淡入淡出应按内容设计；循环素材不能随意把首尾都淡掉。混音是否 `normalize=0` 取决于增益设计，必须检查削波，不把它列为强制参数。
- ffmpeg 的 `aecho` delay 单位是毫秒；要 450 ms 回声应写 `450`，不能把 `.45` 当 0.45 秒。参见 [FFmpeg 官方滤镜文档](https://ffmpeg.org/ffmpeg-filters.html#aecho)，执行前核对已安装版本帮助。
- 复制 FDP 模板时检查项目/事件/银行唯一性、素材路径和标识符。不要无差别替换所有 GUID 后假定内部引用仍正确。
- 2D/3D 与距离衰减在实际事件和关联设置中核对；不能保证把模板中“两处 x_2d 改成 x_3d”就适配所有工程。

构建检查分层记录：

1. 日志、实际输出路径、输入依赖、FEV 中事件名与银行引用、FSB 头和可解析的样本信息。
2. 极小银行可能提示遗漏采样，但“192 字节就是静默空壳”和“只看文件大小”不是格式规范。
3. 当前原版 153 个本地 FSB 的头均为 `FSB5`；因此不能仅凭 FSB5 判定不兼容。同为 FSB5 也不能证明编码、FEV 配套和运行时都兼容。
4. 专服中 `PlaySound` 后出现打印最多证明脚本走到了该处；无声后端可能不完成客户端解码/混音。不能把打印当成银行、事件和听感全部通过。
5. 客户端实际播放，检查第一次触发、循环/停止、近远距离、多人观察、音量滑块、连续触发和切世界。保留失败日志，避免把所有播放崩溃先归因于 WAV 参数。

交付包含：运行时 FEV/FSB、可编辑工程与母带、事件完整路径、分类/3D/循环参数、工具版本、验证记录及未测范围。未经用户要求不调整游戏音量/声音设计。

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
- `persist=false` 仅表示不存档，不代表自动在动画/计时结束时移除。父子关系、事件监听、延迟任务、EmitterManager 注册的清理都要核对；重复进入世界/复活要防止重复生成。
- 混合模式、泛光和 shader 需以当前资产及客户端效果验证；专服 PASS 不证明有画面。需要截图/视频验收时明确抽检的实例、时段和机位，不声称看过未播放素材。

核验依据：当前 `prefabs/cane_candy_fx.lua:16-42,49-65,68-131`、`components/health.lua:590`、`components/dynamicmusic.lua` 的绑定/解绑；核验环境中的 FMOD Designer help；随工具提供的《FMOD Designer 2010》80、142、152-157、205 页；该环境中的 FSB 文件头统计。现代 FMOD Studio 文档可帮助理解概念，不能替代这些 DST 目标版本证据。
