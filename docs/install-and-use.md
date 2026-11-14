# 安装与使用 / Installation and use

当前包的版本与登记数量分别见 RELEASE-MANIFEST、FAMILY-REGISTRY 和 CATALOG。

## 下载与解压

从[最新发行版](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest)下载 [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/latest/download/dst-mod-engineering.zip)：一个完整包包含 Skill、知识、开发脚本、来源准备与 MCP。网页和离线阅读使用同一包，具体版本与数量以下载包内的清单为准。

对照同版 `SHA256SUMS.txt` 后完整解压。ZIP 顶层只有 `dst-mod-engineering/`，直接包含 `SKILL.md`。安装时保留整个目录，包括知识、MCP 服务、来源准备文件和许可证；不要只复制入口文件。包内 `RELEASE-MANIFEST.json` 记录逐文件 SHA-256 与相应登记目录计数；历史 [v2026.10.25.4](https://github.com/Zechariah0121/dst-mod-engineering/releases/tag/v2026.10.25.4) 仍为 187 条，不与本版混用。

## 安装 Skill

选一个位置放入完整 `dst-mod-engineering/` 目录：

| Agent | 项目位置 | 个人位置 | 调用 |
|---|---|---|---|
| Codex | `.agents/skills/dst-mod-engineering/` | `~/.agents/skills/dst-mod-engineering/` | `$dst-mod-engineering` 或技能选择器 |
| Claude Code | `.claude/skills/dst-mod-engineering/` | `~/.claude/skills/dst-mod-engineering/` | `/dst-mod-engineering` |
| Cursor | `.cursor/skills/dst-mod-engineering/` 或 `.agents/skills/dst-mod-engineering/` | `~/.cursor/skills/dst-mod-engineering/` 或 `~/.agents/skills/dst-mod-engineering/` | Agent 聊天的 `/` 菜单 |
| GitHub Copilot | `.github/skills/dst-mod-engineering/`；也支持 `.agents/skills/`、`.claude/skills/` | `~/.copilot/skills/dst-mod-engineering/` 或 `~/.agents/skills/dst-mod-engineering/` | 所用界面的技能入口 |

`~` 属于运行 Agent 的主机。刷新技能列表或重启会话后，确认实际读取的 `SKILL.md`、相关专题和 `knowledge/`。不能自动发现时直接读取其绝对路径。官方来源及云端差异见 [Agent 接入](../references/agent-setup.md)。更新前保存定制版，避免同名副本混淆。

提供任务、Mod 根目录与实际 DST 版本；核对当前源码时再提供合法本地 `data/databundles/scripts.zip`。没有 MCP 时按 [知识文件入口](knowledge-integration.md) 选少量相关条目，报告文件读取，不需要安装或启动服务。

## 默认知识读取与显式来源维护

默认 MCP 无需源码准备。在包根运行 `python -B -X utf8 run_kb.py mcp-config`，将配置接入客户端；默认 `auto` 提供 11 个工具。自然问题、按 ID 或 API 读取均走公共知识入口，`review ID` / `review --api` 也无需源码。显式 Coding、来源 epoch 与证据展开仍使用原有来源和准入守卫。

来源证据仅按维护任务显式准备；使用下面的手动命令，核对来源身份和逐引用状态。准备状态、失败处理与重连见[源码维护](source-compatibility.md)。

## 手动来源准备与严格完整模式

需要 Python 3.10+ 与 SQLite FTS5，MCP 与来源准备使用标准库。当前核验目标及证据环境见[源码维护](source-compatibility.md)。在包根运行手动准备：

```text
python -B -X utf8 prepare_sources.py --source "<762172 scripts.zip>"
python -B -X utf8 run_kb.py status --mode full
python -B -X utf8 run_kb.py mcp-config --mode full
```

`--source` 接受 ZIP、以 scripts/ 为根的源码目录，或直接包含 Lua 相对路径的目录。只需一份合法目标来源，逐引用匹配与缺口解释见[源码维护](source-compatibility.md)。

`mcp-config` 是位置子命令，只打印当前 Python 与入口路径，不修改客户端配置。把输出按客户端支持格式接入；上例生成 `serve --mode full`，要求完整来源准备。直接启动也可用：

```text
python -B -X utf8 run_kb.py serve --mode full
```

这是等待 MCP 输入的 stdio 服务，不提供网页或监听端口。在客户端确认实际 `tools/list` 有 11 个工具，再执行一次任务相关查询并检查响应与来源身份；打印配置或 `validate` 成功不能代替实际连接和查询。`full` 同样默认读取公共知识；其启动额外要求完整来源准备。已经连接显式 `catalog` 模式的会话改用 `auto` 后须重启，才能使用 11 个工具。

完整运行环境位于本地 `cache/runtime/`；独立证据快照位于 `cache/evidence/`。来源局部缺口可激活 partial 证据快照，旧完整环境保留原来源身份；公共发现与正文读取继续可用，详见[证据快照](evidence-snapshots.md)。恢复 Lua 留在本地。损坏构建会隔离保留，修复后重新准备；进程退出自动释放准备锁。

命令行查询使用 `call`；只有它接受 `--tool`、`--arguments-file` 与 `--source-epoch`：

```text
python -B -X utf8 run_kb.py call --mode full --tool get_context_bundle --arguments-file examples/review.json
```

其他位置子命令为 `status`、`validate`、`reindex`。工具参数、当前环境与实际准入见 [检索策略](../references/kb-retrieval.md)。

## 启动模式与公开目录审阅

普通知识读取无需准备来源；维护来源证据或使用严格完整模式时，按任务显式手动准备。`--mode` 可用于 `run_kb.py` 各位置子命令，支持：

| 启动选项 | 行为 |
|---|---|
| `--mode auto`（默认） | 默认提供 11 工具的公共知识发现和正文读取，无需来源；公开清单与正文身份仍严格核验，显式 Coding、epoch 和证据请求沿用原来源守卫 |
| `--mode catalog` | 保留旧两工具目录导航与公开材料审阅，无需游戏来源 |
| `--mode full` | 启动要求完整来源准备及 SQLite FTS5，默认发现和正文仍为 11 工具公共入口；显式 Coding/证据保留原守卫，来源缺口不得伪装已核对 |

目录模式的 `search_catalog` 和 `read_public_entry` 用于导航与显式 `purpose="review"` 审阅。角色、读取预算与完整模式差异统一见[检索策略](../references/kb-retrieval.md)。

不加 `--mode` 的 `mcp-config` 仍输出默认 `auto` 配置；显式使用 `mcp-config --mode catalog` 可只做公开审阅。

## 开发辅助脚本

在包根目录，用 Python 3.10+ 读取本地源码：

```text
python -B scripts/dst_zip_tool.py --zip "<scripts.zip>" info
python -B scripts/dst_zip_tool.py --zip "<scripts.zip>" show scripts/components/combat.lua --start 1 --count 80
```

检查 Mod 语法与部分 API 声明另需 `luaparser`，可用虚拟环境：

```text
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -B scripts/check_api.py "<Mod目录>" --zip "<scripts.zip>"
```

上例为 Windows；macOS/Linux 用 `.venv/bin/python`。`DECLARED` 只说明找到声明，`NEEDS_REVIEW` 需追踪源码，都不证明运行正确。隔离专服辅助程序仅支持 Windows，见 [测试与交付](../references/testing-release.md)。

## 常见问题

| 现象 | 处理 |
|---|---|
| 找不到 Skill 或知识文件 | 检查目录层级、完整解压和实际加载路径；不要只复制 `SKILL.md` |
| 找不到 `prepare_sources.py` / `run_kb.py` | 检查是否完整解压当前 `dst-mod-engineering.zip`，并在含 `SKILL.md` 的包根目录操作 |
| 来源出现局部缺口 | 核对输入、逐引用状态及 affected_entry_ids；partial 快照不替换旧完整环境，公共正文仍可读；来源身份匹配不等于游戏行为验证 |
| 来源缓存损坏或包已升级 | 默认公共正文仍按当前公开清单核验；显式来源操作须先修复或重建相应缓存，不把旧缓存作为新来源证据 |
| 仍只有两工具 | 检查是否显式使用 `--mode catalog`；改为默认 `auto` 并重启 MCP 会话 |
| MCP 已配置但无工具或查询失败 | 核对当前 Python、包路径、启动模式、准备状态、stderr 与客户端会话 |
| 网页 AI 无本地权限 | 提供必要材料；云端不能直接读取用户电脑的游戏和缓存 |

English setup and common usage rules: [README.en.md](../README.en.md).
