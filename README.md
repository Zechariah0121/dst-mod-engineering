# dst-mod-engineering

面向《饥荒联机版》（Don't Starve Together）的中文 AI 开发技能：用当前游戏源码核对实现，区分真实故障与玩法决策，并为修复保留可复核的验证证据。

[![Checks](https://github.com/zhuchengguang317-eng/dst-mod-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/zhuchengguang317-eng/dst-mod-engineering/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

适用于新功能、代码审查、崩溃排错、联机同步、存档生命周期、资源制作和发布前验证。可以作为支持 `SKILL.md` 的 AI 编程工具的技能，也可以直接阅读专题文档、单独运行辅助脚本。

## 内容

| 入口 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | 工作流程、关键约束、15 篇专题的按需导航 |
| [references/](references/) | Lua / Hook、Prefab / Component、RPC / Replica、动作 / UI、存档、战斗、物品、世界生成、动画、音频与测试 |
| [scripts/dst_zip_tool.py](scripts/dst_zip_tool.py) | 直接检索安装版 `scripts.zip`，不依赖旧解压缓存 |
| [scripts/check_api.py](scripts/check_api.py) | Lua 语法检查与组件 / replica 方法声明核对 |
| [scripts/dst_modtest.py](scripts/dst_modtest.py) | Windows 离线单分片专服测试，使用唯一副本、明确完成标记和证据清单 |
| [tests/](tests/) | 使用自造夹具的自动回归，不要求安装游戏 |

技能可独立使用，不需要安装历史 `dst-mod-development` 或 `dst-mod-devkit`。现有旧技能不会被本仓库自动覆盖。

## 安装技能

克隆到所用 AI 工具的技能目录，保持文件夹名称为 `dst-mod-engineering`。例如使用 `$CODEX_HOME/skills` 的 Codex 配置，在 PowerShell 中运行：

```powershell
$skills = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
git clone https://github.com/zhuchengguang317-eng/dst-mod-engineering.git (Join-Path $skills 'dst-mod-engineering')
```

如果目标目录已有技能，先比较并保存本地修改，再选择安装位置。其他工具按其技能发现规则放置整个目录。重新打开会话后可明确调用：

> 使用 `$dst-mod-engineering` 审查这个 Mod。先核对当前游戏源码，再修复确定故障；玩法取舍先列出选项。分别报告静态检查、专服行为和客户端验收结果。

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

按任务选用 DST Mod Tool、Klei Mod Tools、`ktech`、`krane` 与 FMOD 工具；具体版本、能力和输入输出先在自己的环境核对。本仓库不捆绑这些程序，也不要求执行旧教程附件。

动画工作流见 [资源与动画](references/assets-animation.md) 和 [DST Mod Tool](references/dst-mod-tool.md)；音效见 [音频与粒子](references/audio-particles.md)。

## 验证与维护

```powershell
& $python -m unittest discover -s tests -v
```

GitHub Actions 在 Windows / Linux 上执行无需游戏的回归检查。游戏引擎实测由本地合法安装完成，不在 CI 中下载或运行游戏。

首轮整理日期为 **2026-09-27**；核验针对当时实际安装的源码快照，不宣称永远对应最新游戏版本。检查范围、源码指纹、已测结果和未测部分见 [验证记录](docs/validation.md)。游戏更新后，应重新核对相关实现与调用链。

改进建议请附触发条件、相关源码位置和可复现证据；报告中不要上传账号令牌、私人存档或完整游戏资源。

## 来源与许可

本技能整理了历史技能与开发教程，并结合实际安装源码和工具核验纠错；材料来源、纠错索引见 [来源说明](references/sources-and-corrections.md)。

仓库自有文档和脚本以 [MIT](LICENSE) 许可发布。DST 属于 Klei Entertainment；游戏源码、资源和第三方工具没有随仓库分发，其权利与许可归各自权利人所有。
