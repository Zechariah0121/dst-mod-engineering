# 安装与使用 / Installation and use

## 下载与解压

下载唯一发行包 [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.25.3/dst-mod-engineering.zip)：包含完整 Skill、唯一 `knowledge/` 中的 187 条公开知识、开发辅助脚本、来源准备工具与 MCP 服务。网页或离线阅读也使用同一包，按任务选择文件。

对照同版 `SHA256SUMS.txt` 后完整解压。ZIP 顶层只有 `dst-mod-engineering/`，直接包含 `SKILL.md`。安装时保留整个目录，包括知识、MCP 服务、来源准备文件和许可证；不要只复制入口文件。包内 `RELEASE-MANIFEST.json` 记录逐文件 SHA-256 与 187 条知识目录计数。

## 安装 Skill

选一个位置放入完整 `dst-mod-engineering/` 目录：

| Agent | 项目位置 | 个人位置 | 调用 |
|---|---|---|---|
| Codex | `.agents/skills/dst-mod-engineering/` | `~/.agents/skills/dst-mod-engineering/` | `$dst-mod-engineering` 或技能选择器 |
| Claude Code | `.claude/skills/dst-mod-engineering/` | `~/.claude/skills/dst-mod-engineering/` | `/dst-mod-engineering` |
| Cursor | `.cursor/skills/dst-mod-engineering/` 或 `.agents/skills/dst-mod-engineering/` | `~/.cursor/skills/dst-mod-engineering/` 或 `~/.agents/skills/dst-mod-engineering/` | Agent 聊天的 `/` 菜单 |
| GitHub Copilot | `.github/skills/dst-mod-engineering/`；也支持 `.agents/skills/`、`.claude/skills/` | `~/.copilot/skills/dst-mod-engineering/` 或 `~/.agents/skills/dst-mod-engineering/` | 所用界面的技能入口 |

`~` 属于运行 Agent 的主机。刷新技能列表或重启会话后，确认实际读取的 `SKILL.md`、相关专题和 `knowledge/`。不能自动发现时直接读取其绝对路径。官方来源及云端差异见 [Agent 接入](../references/agent-setup.md)。更新前保存定制版，避免同名副本混淆。

提供任务、Mod 根目录、实际 DST 版本与合法本地 `data/databundles/scripts.zip`。没有 MCP 时按 [知识文件入口](knowledge-integration.md) 选少量相关条目，报告文件读取，不需要安装或启动服务。

## 接入 MCP：先使用公开目录

需要 Python 3.10+；MCP 与来源准备使用标准库，无需安装 `luaparser`。在包根目录生成配置：

```text
python -B -X utf8 run_kb.py mcp-config
```

`mcp-config` 是位置子命令，只打印当前 Python 与入口路径，不修改客户端配置。把输出按客户端支持格式接入；默认生成 `serve --mode auto`。直接启动也可用：

```text
python -B -X utf8 run_kb.py serve
```

这是等待 MCP 输入的 stdio 服务，不提供网页或监听端口。`--mode` 可用于 `run_kb.py` 各位置子命令，支持：

| 启动选项 | 行为 |
|---|---|
| `--mode auto`（默认） | 来源未准备（`SOURCES_NOT_PREPARED`）时进入两工具目录模式；准备有效时进入完整模式。已准备缓存损坏或包版本变化时明确报错 |
| `--mode catalog` | 显式选择目录导航与公开材料审阅，无需游戏来源 |
| `--mode full` | 要求完整来源准备及 SQLite FTS5；任何缺失或校验失败均报错 |

目录模式只有 `search_catalog` 与 `read_public_entry`。它可以导航全部 187 条记录，但读取正文只允许 `purpose="review"`，不提供 Coding 上下文、已恢复源码证据或原版 Source/Identity Guards，也不证明运行验证。Core Coding HOLD 不变。参数与读取预算见 [检索策略](../references/kb-retrieval.md)。

## 准备来源并启用完整模式

在包根目录运行，替换为自己合法持有的来源：

```text
python -B -X utf8 prepare_sources.py --source "<759671 scripts.zip>" --source "<合法保留的756039 scripts.zip或源码目录>"
python -B -X utf8 run_kb.py status --mode full
python -B -X utf8 run_kb.py mcp-config --mode full
```

`--source` 可重复，可传 ZIP 或以 `scripts/` 为根、或直接包含 Lua 相对目录的源码文件夹。部分当前知识依赖历史源码范围；缺项时程序列出实际所需文件、哈希与行范围。不要用不匹配的当前片段替代历史证据。缺少历史来源时仍可使用目录模式或文件阅读，完整模式不能启动。

准备读取显式来源，只写 `cache/runtime/`，不改游戏、分发模板或客户端配置。恢复范围按哈希和长度核对；缓存含游戏 Lua 原文，留在本地，不公开上传。已损坏的恢复构建会被隔离保留；修复或更新包后重新准备。准备进程退出会自动释放锁。

服务的工具集在启动时固定。准备成功后重启 MCP 会话，再确认实际 `tools/list` 从两工具切换为九工具。上面的配置命令以 `--mode full` 锁定完整模式；继续使用默认 `auto` 也可以。在客户端执行一次任务相关查询并检查响应与来源身份；打印配置或 `validate` 成功不能代替实际连接和查询。

命令行查询使用 `call`；只有它接受 `--tool`、`--arguments-file` 与 `--source-epoch`：

```text
python -B -X utf8 run_kb.py call --mode full --tool get_context_bundle --arguments-file examples/review.json
```

其他位置子命令为 `status`、`validate`、`reindex`。工具参数、当前环境与实际准入见 [检索策略](../references/kb-retrieval.md)。

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
| 来源准备缺少旧范围 | 按输出提供合法保留来源；可先目录审阅或文件阅读，不把部分缓存当完整服务 |
| `auto` 报缓存损坏或包版本变化 | 修复来源准备；仅需公开审阅时显式使用 `--mode catalog` |
| 准备成功后仍只有两工具 | 重启 MCP 会话，工具集不会在已连接会话中自动切换 |
| MCP 已配置但无工具或查询失败 | 核对当前 Python、包路径、启动模式、准备状态、stderr 与客户端会话 |
| 网页 AI 无本地权限 | 提供必要材料；云端不能直接读取用户电脑的游戏和缓存 |

The single complete distribution includes the Skill, 187 public records, MCP and source preparation. MCP needs Python 3.10+; full mode also needs SQLite FTS5. The default `auto` starts two catalog tools only when sources are unprepared (`SOURCES_NOT_PREPARED`); a damaged prepared cache or changed package version causes an error. Explicit `catalog` supports navigation and public review, with no Coding context, restored Lua evidence or original Source/Identity Guards. Core Coding HOLD remains binding. Full mode requires all authorized current and historical source ranges. After preparation, restart the MCP session to obtain nine tools; tools are fixed at startup. `mcp-config --mode full` prints configuration that requires full mode. Verify actual tools and a real query in your client. Restored Lua stays local; damaged builds are retained in isolation, and process locks release on exit. Development syntax checks separately require `luaparser`; the game-server helper supports Windows only.
