# 动画工具安装与首次验证

用于首次搭建环境，或当前任务缺少可用工具时。先查 [环境发现](environment-tools.md)，不要以“未找到”结束工作：提出能完成当前产物的最小安装方案；已有工具能通过同样验证时优先复用。本页不捆绑程序，也不要求一次装齐所有工具。

## 按任务选择最小工具

| 当前产物 | 优先选择 | 何时才增加其他工具 |
|---|---|---|
| 只改 Lua、复用已有图像 | 无新增动画工具 | 确实需要重建资源时再选 |
| PNG → TEX/XML、图集预览 | DMT 的当前可用打包功能，或 ktech，二选一 | 已选工具不能正确处理目标格式时再比较替代 |
| 动画编辑、预览、SCML → ZIP | DMT；先验证下载版本确有需要的编辑/打包能力 | 既有工程依赖官方编译流程，或 DMT 样本验证失败时，再用官方 `scml` |
| 已编译动画 → SCML | DMT 的当前解包功能，或 krane | 核对朝向、变换与图集保真，不能以“成功导出”结束 |
| 既有中间 XML/帧序列编译工程 | 工程匹配的官方 `buildanimation.py` 及依赖 | 任意 PNG ZIP 不能直接替代该工具要求的输入结构 |

“有 GUI”“有 CLI”“有 Lua 脚本接口”分别核对。DMT 能完成当前任务时，不再为同一产物强制安装 ktools 和官方旧编译器。音频工具另看 [audio-particles.md](audio-particles.md)。

## 发现、提议与授权

1. 读取项目配置，确认操作系统、CPU 架构、GUI/终端/联网能力、已有工具的绝对路径与版本。Windows 可用 `Get-Command ktech,krane -ErrorAction SilentlyContinue` 查 PATH；未命中不代表未安装，继续查用户指定目录和 Steam 库。macOS/Linux 可查 `uname -m`、`command -v ktech`。不根据当前 Agent 名称猜测宿主平台。
2. 对缺项一次说明：任务需要什么产物、候选工具和作者来源、实际包版本/平台/架构、目标目录、必要依赖、首次验证方法。只有具体功能需要时才建议安装；不要把整套工具清单变成前置条件。
3. **先检查已有安装授权。** 用户已经同意本任务的工具及必要依赖安装时，在该范围内继续下载、安装和验证，不逐个步骤重复提问；尚无授权时先让用户选择具体方案。仅要求“开发 Mod”或“补写安装文档”不自动等于同意新增软件。更换来源、增加未包含的系统依赖或改变安装范围时补充说明并取得相应授权。
4. 授权后从下表作者入口选择实际存在的包，记录页面、版本、平台/架构和下载文件 SHA-256。有作者校验值/签名时对照；自己计算的哈希仅作记录，不能冒充作者认证。版本号不明或平台不匹配时先解决，不拼接猜测的下载 URL。
5. 免安装 ZIP 解压到独立版本目录，例如 `C:\Tools\DST\工具名\版本\`；保留随包 DLL/配置，不覆盖已有版本，不改全局 PATH。安装器按已确认的范围执行；Steam 登录、验证码、账号授权和协议确认交由用户完成。安装完成后定位实际可执行文件，用绝对路径运行。

## 作者入口与安装路线

### DST Mod Tool（DMT）

[作者发布网站](https://msisunny.github.io/dst-mod-tool-publisher/)由[作者 Workshop 页面](https://steamcommunity.com/sharedfiles/filedetails/?id=3609167896)直接链接。访问网站，按当前操作系统选择下载；跳转目标应来自该页面实际链接。下载完整压缩包后先查看清单，解压到独立目录，再启动其中程序。macOS 按实际包中的 `.app` 布局放置；架构、系统最低版本和依赖若未标明，需要从包信息或作者说明核实，不能认为一个 Mac 包同时适合 Intel 和 Apple Silicon。

**2026-09-27 的公开页面核对：** 网站部署脚本显示 `1.0.5`，启用 Windows/macOS 下载按钮并指向作者 Gitee 发布空间；公开仓库同样如此，Linux 按钮被注释。这与本项目此前本机 `1.1.13` 快照不同，不能据此断言哪个下载包含本机那套 Lua API，也不能声称已有匹配的 Linux/ARM64 下载。来源可交叉查[作者网页源码](https://github.com/MSIsunny/dst-mod-tool-publisher/blob/main/src/App.js)和[版本元数据](https://github.com/MSIsunny/dst-mod-tool-publisher/blob/main/src/app-data.json)。实际安装时重新访问发布页，不把这些快照当固定版本要求。

取得程序后检查文件/应用版本和当前帮助；只有实际支持 `script --help` 时才采用 [DMT 脚本工作流](dst-mod-tool.md)。不支持时采用该版本 GUI 或它实际提供的 CLI；不要照搬隐藏在网页源码中的旧命令。若系统阻止启动，记录提示并按平台正常的应用信任流程处理，不把关闭系统保护或递归移除隔离标记列为自动安装步骤。

### Klei 官方 Don't Starve Mod Tools

在 **Steam 客户端 → 库 → 类型筛选勾选“工具 / Tools” → 搜索 `Don't Starve Mod Tools` → 安装**。这是官方工具项目名称，AppID 为 **245850**，与独立作者的 DMT 不同。旧版 Steam 菜单可能直接显示“库 → 工具”；官方论坛的[工具更新帖](https://kleiforums.com/forums/topic/126872-dont-starve-mod-tools-update-282021/)及[安装说明](https://kleiforums.com/forums/topic/50574-guide-modding-practices-before-beginning/)可用于核对入口，AppID 另经本机 Steam 安装元数据核对。库中没有该项目时由用户检查账号拥有的游戏和工具筛选，不换来历不明的转载包。

安装后从该项目的“管理 / 属性 → 浏览本地文件”定位 `mod_tools`，确认本平台实际包含的 `scml`、脚本与依赖。不要因为 Steam 显示整个工具项目已安装，就认为每个子工具都能运行。保留官方目录布局：Windows 历史包带有自己的 Python/库；旧 `buildanimation.py` 可能需要 Python 2.7，不能直接交给本技能静态检查使用的 Python 3。非 Windows 子工具是否齐全、能否在当前系统运行，需要单独验证；[Klei 源码仓库](https://github.com/kleientertainment/ds_mod_tools)说明了编译与运行依赖，但旧仓库说明不保证今天的 Steam 包布局相同。

### ktools：ktech / krane

原作者为 [nsimplex/ktools](https://github.com/nsimplex/ktools)，后续分支为 [dstmodders/ktools](https://github.com/dstmodders/ktools)。先查作者的 [4.4.0 源码标签](https://github.com/nsimplex/ktools/tree/4.4.0)、[原作者 Klei 下载页](https://kleiforums.com/files/file/583-ktools-cross-platform-modding-tools-for-dont-starve/)和[维护分支 Releases](https://github.com/dstmodders/ktools/releases)，区分源码包与带 `ktech`/`krane` 可执行文件的发行包。

- 原作者下载页说明历史 Windows 包名以 `-win32` 结尾，需要 **VC++ 2013 x86** 运行库，且该二进制包不含 ZIP 输入支持；因此先解压动画 ZIP 再传目录。运行库确实缺失时，从[Microsoft 官方入口](https://www.microsoft.com/en-us/download/details.aspx?id=40784)按已批准的依赖范围处理，不从 DLL 下载站补文件。此要求针对该历史构建，不套用到所有 ktools 构建。
- 截至上述核对日期，`nsimplex` GitHub Releases API 未列出发行记录；维护分支当前 release 为 **v4.5.1（2021-09-15）**，附加二进制 assets 为空。页面上的自动 `Source code` 压缩包不是免安装程序。原作者论坛附件本次未实际下载，能否取得及其具体文件版本需在安装时确认；找不到匹配二进制时明确告知用户。
- 需要从源码构建时，按所选分支 README 确定编译器、CMake、ImageMagick 开发库，按需使用 libzip；两分支依赖版本可能不同。先说明新增依赖和构建范围，再执行授权的安装/构建；输出保留在独立目录，不默认 `sudo make install`。已有 Docker 环境可评估维护分支作者提供的容器路线；不要为一次图片转换默认引入 Docker 或整套编译环境。

## 首次验证：得到产物才算工具可用

在自有临时目录放入一张小型 RGBA PNG，含透明边缘和非对称图案；动画任务再放入一份图片引用完整的极简 SCML 副本。记录输入哈希、工具版本、命令、输出及日志。不对现有工程直接运行会预处理原图的自动编译器。

下面是 PowerShell 示例：将路径替换为**实际已安装且获准运行**的工具和自有输入。先创建本轮输出目录，再仅运行已选择的那条管线；不覆盖素材。

```powershell
$ProbeOut = Join-Path ([IO.Path]::GetTempPath()) ('dst-tool-probe-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $ProbeOut | Out-Null
```

ktech 路线：

```powershell
$Ktech = (Resolve-Path -LiteralPath 'C:\Tools\DST\ktools\selected-version\ktech.exe').Path
$ProbePng = (Resolve-Path -LiteralPath 'C:\DSTWork\probe\input.png').Path
$Before = (Get-FileHash -LiteralPath $ProbePng -Algorithm SHA256).Hash
$ProbeTex = Join-Path $ProbeOut 'probe.tex'
$ProbeXml = Join-Path $ProbeOut 'probe.xml'
& $Ktech --version
& $Ktech --help
# 仅在当前 help 确认 --atlas 参数时执行此行。
& $Ktech --atlas $ProbeXml $ProbePng $ProbeTex
if ($LASTEXITCODE -ne 0) { throw 'ktech conversion failed' }
if (!(Test-Path -LiteralPath $ProbeTex) -or !(Test-Path -LiteralPath $ProbeXml)) { throw 'Missing TEX/XML' }
& $Ktech -i $ProbeTex
if ($LASTEXITCODE -ne 0) { throw 'TEX inspection failed' }
& $Ktech $ProbeTex (Join-Path $ProbeOut 'roundtrip.png')
if ($LASTEXITCODE -ne 0) { throw 'TEX decode failed' }
if ((Get-FileHash -LiteralPath $ProbePng -Algorithm SHA256).Hash -ne $Before) { throw 'Input PNG changed' }
[xml]$Atlas = Get-Content -LiteralPath $ProbeXml -Raw
$Atlas.Atlas.Texture
$Atlas.Atlas.Elements.Element
```

随后实际打开 `roundtrip.png`，检查尺寸、方向、透明和边缘；核对 XML 的 Texture 路径与 Element 名对应产物。压缩和预乘 alpha 可能使回读像素不同，不能要求有损格式逐字节还原。DMT 路线也必须用实际支持的功能完成 PNG → TEX/XML → 重新读取/预览这一闭环，不能仅显示帮助就宣布安装成功。

官方 SCML 路线示例（单独选择，`$ProbeOut` 为上面创建的本轮目录）：

```powershell
$ModTools = (Resolve-Path -LiteralPath 'C:\SteamLibrary\steamapps\common\Don''t Starve Mod Tools\mod_tools').Path
$Scml = (Resolve-Path -LiteralPath (Join-Path $ModTools 'scml.exe')).Path
$InputScml = (Resolve-Path -LiteralPath 'C:\DSTWork\probe\source\probe.scml').Path
$TestMod = Join-Path $ProbeOut 'test-mod'
New-Item -ItemType Directory -Path $TestMod | Out-Null
Push-Location -LiteralPath $ModTools
try {
    & $Scml $InputScml $TestMod
    if ($LASTEXITCODE -ne 0) { throw 'SCML compile failed' }
} finally { Pop-Location }
Get-ChildItem -LiteralPath $TestMod -Recurse -File
```

`scml` 的第二参按该官方实现是**目标 Mod 目录**，在其 `anim/` 下生成 ZIP，不是输出 ZIP 文件名；见 [Klei 使用说明](https://github.com/kleientertainment/ds_mod_tools/blob/master/README.md#usage)及[参数处理源码](https://github.com/kleientertainment/ds_mod_tools/blob/master/src/app/scml/main.cpp#L2586-L2589)。还需核对日志、ZIP CRC、bank/build/symbol、动画和图集引用，用 DMT 或另一条可用读取路径重新打开并导出预览。DMT 编译路线同样要得到并重新读取真正的游戏 ZIP。只有反编译任务才另外用 krane 对小型样本执行 `--check-animation-fidelity`，检查 SCML、图片、帧/朝向与偏移；不把无报错等同完全保真。资源用途与验收规则见 [assets-animation.md](assets-animation.md)。

## 无法安装或无法完整操作时

- **无匹配系统/架构包**：先查同一任务已有替代工具；再给出源码构建、受支持主机完成编译、暂交源工程三种适用选择。不要悄悄安装兼容层或把 Windows 命令称为跨平台已测。
- **断网或作者下载不可用**：可以继续用有来源记录的本地包核验；否则保留素材、工程、参数和具体待完成步骤，明确编译尚未完成，不转到随机网盘执行程序。
- **无 GUI/Agent 不能操作桌面**：优先验证当前程序实际提供的 CLI；若只能 GUI，准备可复现输入与操作说明供用户执行，同时继续独立的源码和资源结构检查。不虚构点击、预览或保存成功。
- **依赖、登录或权限阻塞**：给出准确缺项及恢复位置；已有授权范围内解决常规路径和参数问题。需要用户完成的账号/协议步骤不代答，完成后继续验收。

交付区分四层：**来源/版本已核对 → 程序可启动且接口存在 → 指定样本产物通过检查 → 真实游戏效果已验收**。本页新增时只进行了来源和既有文档核对，没有下载/安装上述包，也没有据此新增编译或游戏通过记录。
