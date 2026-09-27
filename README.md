# dst-mod-engineering

面向《饥荒联机版》（Don't Starve Together）的中文 AI 开发技能：用当前游戏源码核对实现，区分真实故障与玩法决策，并为修复保留可复核的验证证据。

[![Checks](https://github.com/zhuchengguang317-eng/dst-mod-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/zhuchengguang317-eng/dst-mod-engineering/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

适用于新功能、代码审查、崩溃排错、联机同步、存档生命周期、资源制作和发布前验证。可以作为支持 `SKILL.md` 的 AI 编程工具的技能，也可以直接阅读专题文档、单独运行辅助脚本。

## 内容

| 入口 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | 工作流程、关键约束、22 篇专题的按需导航 |
| [references/](references/) | Lua / Hook、Prefab / Component、RPC / Replica、动作 / UI、存档、战斗、物品、世界生成、动画、音频与测试 |
| [scripts/dst_zip_tool.py](scripts/dst_zip_tool.py) | 直接检索安装版 `scripts.zip`，不依赖旧解压缓存 |
| [scripts/check_api.py](scripts/check_api.py) | Lua 语法检查与组件 / replica 方法声明核对 |
| [scripts/dst_modtest.py](scripts/dst_modtest.py) | Windows 离线单分片专服测试，使用唯一副本、明确完成标记和证据清单 |
| [scripts/build_web_bundle.py](scripts/build_web_bundle.py) | 自动生成网页资料包，并检查与源文件的一致性 |
| [tests/](https://github.com/zhuchengguang317-eng/dst-mod-engineering/tree/main/tests) | 源码仓库中的自造夹具回归，不要求安装游戏 |

技能可独立使用，不需要安装历史 `dst-mod-development` 或 `dst-mod-devkit`。现有旧技能不会被本仓库自动覆盖。

料理、法术、自定义数值、角色外观、装备手持、GIF 动画和 FMOD 音效的旧专项流程已核验并并入本技能，按入口导航读取即可，无需同时安装旧专项技能。旧项目的配色、数值、绝对路径和固定同步目录不作为通用默认。各旧名称的内容去向见 [整合记录](docs/consolidation.md)。

## 网页 AI：下载后使用

无需本地 Agent 或 Python。按当前网页实际支持的功能选择文件，然后照 [网页使用指南](references/web-chat.md) 的启动提示词提供任务与材料：

| 用法 | 下载 |
|---|---|
| 平台提供原生“上传技能”入口 | [技能 ZIP](https://github.com/zhuchengguang317-eng/dst-mod-engineering/raw/refs/heads/main/dist/web/dst-mod-engineering.skill.zip)，内含单一 `dst-mod-engineering/` 根目录；它不是插件安装包 |
| 普通聊天，先确认材料和能力 | [入门 Markdown](https://github.com/zhuchengguang317-eng/dst-mod-engineering/raw/refs/heads/main/dist/web/web-starter.md) |
| 代码审查 / 修复 | [代码审查 Markdown](https://github.com/zhuchengguang317-eng/dst-mod-engineering/raw/refs/heads/main/dist/web/web-code-review.md) |
| 联机 / 存档 / UI | [联机 Markdown](https://github.com/zhuchengguang317-eng/dst-mod-engineering/raw/refs/heads/main/dist/web/web-networking.md) |
| 贴图 / 动画 / 音频工具 | [资源 Markdown](https://github.com/zhuchengguang317-eng/dst-mod-engineering/raw/refs/heads/main/dist/web/web-assets.md) |
| 世界生成 / 空间判定 | [世界生成 Markdown](https://github.com/zhuchengguang317-eng/dst-mod-engineering/raw/refs/heads/main/dist/web/web-worldgen.md) |
| 下载全部专题后自行选择 | [网页资料 ZIP](https://github.com/zhuchengguang317-eng/dst-mod-engineering/raw/refs/heads/main/dist/web/web-reading.zip)，解压后只上传本次需要的 Markdown |
| 明确需要全部文档且平台容量允许 | [完整 Markdown](https://github.com/zhuchengguang317-eng/dst-mod-engineering/raw/refs/heads/main/dist/web/web-full.md) |

通常选择一份专题即可，其中已包含共同入口。ZIP 作为普通附件上传，不代表平台一定会解压或注册技能；无法读取时改传单个 Markdown。若 Markdown 不被接受，可按指南分段粘贴必要文本。

平台的账号、工作区、上传和代码执行能力各不相同。资料包没有游戏源码或动画程序，也不会给予网页 AI 本机访问权限。需要本机编译或游戏测试时使用 [本机验证交接单](templates/local-validation.md)，把真实结果交回网页 AI 复核。各包的源文件指纹和输出哈希见 [bundle-index.json](https://github.com/zhuchengguang317-eng/dst-mod-engineering/raw/refs/heads/main/dist/web/bundle-index.json)。

## 安装技能

Claude Code、Cursor、GitHub Copilot 和 Codex 的安装目录、调用方式及首次加载检查见 [跨 Agent 接入指南](references/agent-setup.md)。文档按各产品官方说明核对；格式兼容不等于已经逐个实测所有 Agent。

克隆整个目录，保持文件夹名称为 `dst-mod-engineering`。例如，按 [Codex 当前官方说明](https://learn.chatgpt.com/docs/build-skills) 安装到用户技能目录，在 PowerShell 中运行：

```powershell
$skills = Join-Path $env:USERPROFILE '.agents/skills'
$destination = Join-Path $skills 'dst-mod-engineering'
if (Test-Path -LiteralPath $destination) { throw '目标已存在；请先核对和保存本地修改。' }
New-Item -ItemType Directory -Path $skills -Force | Out-Null
git clone https://github.com/zhuchengguang317-eng/dst-mod-engineering.git $destination
if ($LASTEXITCODE -ne 0) { throw '技能克隆失败，请检查 Git 输出。' }
```

已有旧目录安装时，先确认当前 Agent 实际加载的位置，不自动迁移或同时安装多个同名副本。不支持技能发现机制的 Agent 也可使用完整目录，并明确要求它读取文件：

> 请读取 `<技能目录>/SKILL.md`，按导航读取相关参考，然后审查这个 Mod。先核对当前游戏源码，再修复确定故障；玩法取舍先列出选项。分别报告静态检查、专服行为和客户端验收结果。

原生技能调用按 Agent 的命令选择；例如 Codex 使用 `$dst-mod-engineering`。只有聊天能力时可阅读和分析，执行脚本需要终端与文件权限，视觉验收还需可访问的客户端或人工反馈。Windows 专服测试器的系统限制与 Agent 品牌无关。

单纯阅读技能无需安装 Python 包。运行 `check_api.py` 和自动测试需要 Python 3.10+ 与 `luaparser`；建议为仓库单独创建虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 脚本快速开始

以下命令在仓库根目录执行。路径均为示例，需改成自己的合法游戏安装、Mod 源码和输出位置：

```powershell
$python = '.\.venv\Scripts\python.exe'
$dst = 'C:\Games\steamapps\common\DontStarveTogether'
$mod = 'C:\Mods\example_mod'

# 查看源码包指纹，再检索原版定义
& $python scripts/dst_zip_tool.py --dst $dst info
& $python scripts/dst_zip_tool.py --dst $dst grep 'AddModRPCHandler' --path 'modutil.lua'
& $python scripts/dst_zip_tool.py --dst $dst show 'scripts/components/weapon.lua' --start 1 --count 80

# 语法与方法声明检查
& $python scripts/check_api.py $mod --dst $dst --out 'api-report.json'

# Windows：运行隔离专服加载测试
& $python scripts/dst_modtest.py $mod --dst $dst --out 'test-evidence' --quiet
```

`dst_zip_tool.py` 也支持 `--zip` 指定单独的源码包；`check_api.py` 另支持 `--scripts-dir` 指定解压后的 `scripts` 目录。参数详情可运行各脚本的 `--help`。

`check_api.py` 的 `DECLARED` 仅表示查到方法声明，不证明参数、端别、时序或整个 Mod 正确；`NEEDS_REVIEW` 需要人工追踪。退出码 `0` 表示枚举到的直接调用均有声明，`1` 表示语法错误，`2` 表示待查、输入问题或无直接调用。

### 专服行为断言

将以下内容保存为自己的 `test.lua`，再通过 `--script test.lua` 传入测试器：

```lua
local item = SpawnPrefab("spear")
assert(item and item.components.weapon, "weapon did not spawn")
TEST.After(0.2, function()
    assert(item.components.weapon:GetDamage() > 0)
    item:Remove()
    TEST.Done("all assertions completed")
end)
```

行为脚本必须在所有目标断言完成后调用 `TEST.Done()`。普通返回不代表通过，异步任务使用 `TEST.After()` 捕获异常。测试器核对本轮加载、完成和错误标记，并在完成后的观察窗口内继续检查失败。

测试器会向游戏 `mods` 目录写入唯一测试副本，创建独立存档并启动、结束自己启动的专服进程。测试副本和证据保留，准确路径写入 `manifest.json`；清理前按清单确认归属。它支持 Windows 单分片离线测试，不适用于纯客户端 Mod，也不替代真实客户端的 UI、输入、预测、画面、音频或跨分片验收。更多参数与边界见 [测试与交付](references/testing-release.md)。

## 动画与音频工具

**本机没有动画工具也有接入流程**：按 [工具安装与首次验证](references/tool-bootstrap.md) 先识别任务，检查现有工具，再选择必需工具的官方或作者发布入口。Agent 应说明缺什么、从哪里获取、装到哪里及如何验证；已有安装授权就继续执行，没有授权时一次提出明确方案。不会因为安装了技能就无条件安装所有程序。

指南覆盖 DST Mod Tool、Klei Don't Starve Mod Tools、`ktech` / `krane`，并说明无 GUI、断网和平台不匹配时的处理。首次验证包括实际的小型转换或编译；仅能显示 `--help` 不算产物验证。本仓库不捆绑这些工具。音频任务的 FMOD 流程另见对应专题。

动画工作流见 [资源与动画](references/assets-animation.md) 和 [DST Mod Tool](references/dst-mod-tool.md)；音效见 [音频与粒子](references/audio-particles.md)。

## 验证与维护

以下命令供维护者在 **GitHub 源码仓库** 根目录运行；网页上传用技能 ZIP 不包含测试目录或 CI 配置。网页资料从同一份文档生成，禁止手工改生成文件：

```powershell
& $python -m unittest discover -s tests -v
& $python scripts/build_web_bundle.py
& $python scripts/build_web_bundle.py --check
```

生成器仅需 Python 标准库；它不会下载或安装工具。GitHub Actions 在 Windows / Linux 上执行无需游戏的回归检查，并检查提交的网页包是否与源码一致。修改输入文档或脚本后重新生成 `dist/web/` 再提交，避免上传版与技能正文漂移。游戏引擎实测由本地合法安装完成，不在 CI 中下载或运行游戏。

首轮整理日期为 **2026-09-27**；核验针对当时实际安装的源码快照，不宣称永远对应最新游戏版本。检查范围、源码指纹、已测结果和未测部分见 [验证记录](docs/validation.md)。游戏更新后，应重新核对相关实现与调用链。

改进建议请附触发条件、相关源码位置和可复现证据；报告中不要上传账号令牌、私人存档或完整游戏资源。

## 来源与许可

本技能整理了历史技能与开发教程，并结合实际安装源码和工具核验纠错；材料来源、纠错索引见 [来源说明](references/sources-and-corrections.md)。

仓库自有文档和脚本以 [MIT](LICENSE) 许可发布。DST 属于 Klei Entertainment；游戏源码、资源和第三方工具没有随仓库分发，其权利与许可归各自权利人所有。
