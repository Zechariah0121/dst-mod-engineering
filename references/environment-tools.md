# 环境发现与来源定位

先发现当前项目实际使用的游戏、源码与工具，再配置绝对路径。本技能不绑定某台机器的目录，也不随仓库分发游戏源码、编译器或第三方可执行程序。不要根据历史环境快照自动安装、更新或迁移工具。

| 用途 | 发现与核对方法 |
|---|---|
| 游戏根目录 `$dst` | 从 Steam 的本地文件浏览入口或已知安装位置确认；检查该目录的游戏文件和版本，不假设固定盘符 |
| 当前打包源码 | `$dst` 下的 `data/databundles/scripts.zip`；记录 SHA-256 后查阅 |
| 已解压源码（可选） | 项目指定的只读副本；先与安装包的相关条目比较字节或哈希，避免陈旧副本 |
| Python `$python` | 用当前 shell 的命令发现功能或项目环境配置定位，执行 `--version`；静态工具另需 `luaparser` |
| 官方 Don't Starve Mod Tools | 从 Steam Tools 的已安装项目定位，检查 `scml.exe`、Python 脚本及其实际帮助；不同工具包版本的内容可能不同 |
| DST Mod Tool `$DmtExe` | 从已安装应用或用户提供的位置定位，检查文件版本及 `script --help`；没有该工具时按现有已验证管线处理 |
| ktech / krane | 从已安装 ktools 位置定位，分别检查 `--help`；不要把文件夹名当成工具版本 |
| Mod 源码与运行副本 `$mod` | 从当前项目配置或作者说明确定；分别记录路径和哈希，不能只看同名文件夹 |

接手项目时读取该项目的约定、交接文档与当前配置。历史报告不证明今天的副本相同。环境路径应保存在项目自己的本地配置或会话变量中，避免把开发者用户名和绝对目录写入可公开的技能。

## 已记录的源码基线

2026-09-27 的 Windows 核验环境：安装包内 4030 个 Lua 与当时的解压副本逐字节相同，无缺失、无漂移。该次 `scripts.zip` SHA-256：

`85d6aa0e24a290d81745f1fd18bd0769d6b82011a3ba5aba02b87389b62f41c8`

这证明当时的解压副本匹配该安装版本，不证明它是读者当前版本，也不证明 Steam 上没有更新。游戏更新或哈希改变后，重新比较相关文件，不能继续沿用旧行号。验证范围见 [验证记录](../docs/validation.md)。

源码先用 `rg --files`/`rg -n` 定位。没找到按 prefab 命名的文件时，查合并返回多个 Prefab 的文件、工厂函数、调用链；如帽子集中在 `prefabs/hats.lua`。Lua 中没定义的引擎方法可能来自 C++，不能凭一次搜索判不存在。

无需解压时，在技能目录用 PowerShell 调用（先将 `$python`、`$dst` 赋为已发现并核对的绝对路径）：

```powershell
& $python scripts/dst_zip_tool.py --dst $dst info
& $python scripts/dst_zip_tool.py --dst $dst grep 'SetMaxHealth' --path components/health.lua
& $python scripts/dst_zip_tool.py --dst $dst show components/health.lua --start 1 --count 100
```

`$python`、`$dst` 由当前已验证路径赋值。全局参数 `--dst`/`--zip` 放子命令前；`extract MEMBER --out EXACT_NEW_FILE` 只导出单文件且拒绝覆盖。

## 工具采用原则

“新”不是正确性的证据。读取已安装程序的 metadata/`--help`，在副本上运行相关操作，再检查输出产物。2026-09-27 核验环境中，ktech 自报 `4.4.0`，DMT 文件版本为 `1.1.13`；目录名称曾与 ktech 实际版本不同。它们是历史快照，不是固定依赖版本；具体 DMT 脚本接口看 [dst-mod-tool.md](dst-mod-tool.md)。

历史教程附带的可执行文件不作为默认工具；先做压缩包清单/文本源码审查。需要换工具时先比较现有工具能否完成同一产物，再按用户授权处理安装。

不同 shell 的 stdout、编码、引号与路径行为用当前实际调用确认；旧机器经验不能当作永久不可用声明。含复杂字符串的操作优先使用脚本文件，清理文件始终在同一 shell 中用明确路径执行。核验环境中 Python 可以读取中文源码，但 Windows 引擎无法从被测中文存档根路径读取配置/保存，测试器因此要求独立 ASCII 引擎存档路径；报告目录可位于中文工作区。这是已测路径的兼容性记录，不是所有平台和字符组合的结论。

## 随附测试器的特殊边界

- 默认引擎存档位于系统临时目录 `dst_mod_engineering/<运行ID>/DME/Cluster`；可传 `--storage-root ASCII_DIRECTORY`。命令同时传 `-persistent_storage_root`、`-conf_dir`、`-cluster`、`-shard`，不依赖当前账户的真实存档。
- 核验环境的离线 LAN 日志声明允许端口 `10998..11018`，实测 `11018` 有效；工具先查空闲端口，但查完到启动仍可能竞争。换游戏版本后先核对引擎日志。端口冲突是环境故障，不能为释放端口杀无关服务器。
- runner 只终止自己 `Popen` 创建的进程。每轮保留日志、manifest、唯一 staged Mod 与存档，便于排查；清理时先核对 manifest、绝对路径归属与进程状态，勿通配删除真实 `mods`/Klei 目录。
- 唯一测试目录会改变 `modname`。依赖 Workshop ID、硬编码文件夹名、跨 Mod 名称探测的场景必须单独验证配置映射与真实安装环境。

存档路径参数依据 Klei 开发者 [Dedicated Server Command Line Options Guide](https://kleiforums.com/forums/topic/64743-dedicated-server-command-line-options-guide/)，上述路径/端口行为另经核验环境的实际引擎日志验证。
