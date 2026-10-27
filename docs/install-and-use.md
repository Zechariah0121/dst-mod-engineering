# 安装与使用 / Installation and use

当前版本为 `v2026.10.27.1`，包含 210 条登记记录（旧 187 条 + 23 条机制研究）。新研究保持 `research/restricted/hold`；版本和数量以 `RELEASE-MANIFEST`、`FAMILY-REGISTRY` 和 `CATALOG` 为准。

## 下载与解压

下载唯一发行包 [dst-mod-engineering.zip](https://github.com/Zechariah0121/dst-mod-engineering/releases/download/v2026.10.27.1/dst-mod-engineering.zip)：包含完整 Skill、唯一 `knowledge/` 中的 210 条登记知识、开发辅助脚本、来源准备工具与 MCP 服务。网页或离线阅读也使用同一包，按任务选择文件。

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

提供任务、Mod 根目录、实际 DST 版本与合法本地 `data/databundles/scripts.zip`。没有 MCP 时按 [知识文件入口](knowledge-integration.md) 选少量相关条目，报告文件读取，不需要安装或启动服务。

## 用当前源码启用完整九工具 MCP

需要 Python 3.10+ 与 SQLite FTS5；MCP 与来源准备使用标准库，无需安装 `luaparser`。在包根目录运行，替换为自己合法持有的 `760178 / Steam build 26230496` 来源。本版保留 `source_epoch=759671` 作为证据基线：

```text
python -B -X utf8 prepare_sources.py --source "<760178 scripts.zip>"
python -B -X utf8 run_kb.py status --mode full
python -B -X utf8 run_kb.py mcp-config --mode full
```

本版面向上述单份目标 ZIP 准备完整服务，不需要旧版源码。`--source` 也接受以 `scripts/` 为根、或直接包含 Lua 相对目录的源码文件夹。核心必需来源槽仍按精确范围哈希校验；独立机制研究另按引用报告文件/范围匹配、变化或缺失，来源缺口保留未知，不封锁其他研究条目的阅读。保留证据基线不等于将目标源码或全部事实标成 759671；本次支持也不保证任意未来 ZIP 都能完整准备。来源身份与维护边界见 [源码维护](source-compatibility.md)。

`mcp-config` 是位置子命令，只打印当前 Python 与入口路径，不修改客户端配置。把输出按客户端支持格式接入；上例生成 `serve --mode full`，要求完整来源准备。直接启动也可用：

```text
python -B -X utf8 run_kb.py serve --mode full
```

这是等待 MCP 输入的 stdio 服务，不提供网页或监听端口。在客户端确认实际 `tools/list` 有九工具，再执行一次任务相关查询并检查响应与来源身份；打印配置或 `validate` 成功不能代替实际连接和查询。服务工具集在启动时固定，已经连接目录模式的会话必须在准备成功后重启。

准备读取显式来源，只写 `cache/runtime/`，不改游戏、分发模板或客户端配置。恢复范围按哈希和长度核对；缓存含游戏 Lua 原文，留在本地，不公开上传。历史比较节点保留原快照、哈希、行范围与引用，显式作为 `metadata_only` 使用，不要求旧源码，也不当作已读的当前源码证据。已损坏的恢复构建会被隔离保留；修复或更新包后重新准备。准备进程退出会自动释放锁。

命令行查询使用 `call`；只有它接受 `--tool`、`--arguments-file` 与 `--source-epoch`：

```text
python -B -X utf8 run_kb.py call --mode full --tool get_context_bundle --arguments-file examples/review.json
```

其他位置子命令为 `status`、`validate`、`reindex`。工具参数、当前环境与实际准入见 [检索策略](../references/kb-retrieval.md)。

## 启动模式与公开目录审阅

正常完整使用按上面的单份当前源码流程准备。`--mode` 可用于 `run_kb.py` 各位置子命令，支持：

| 启动选项 | 行为 |
|---|---|
| `--mode auto`（默认） | 准备有效时进入完整九工具模式；来源未准备或 `PACKAGE_CHANGED` 时，核验公开清单后提供两工具审阅并报告原因；缓存损坏、无效激活及公开文件失配仍报错 |
| `--mode catalog` | 显式选择目录导航与公开材料审阅，无需游戏来源 |
| `--mode full` | 要求完整来源准备及 SQLite FTS5；核心必需来源缺失、缓存损坏或完整性校验失败均报错；机制研究逐引用缺口保留未知 |

目录模式只有 `search_catalog` 与 `read_public_entry`。它可以导航全部登记记录，数量以 `knowledge/CATALOG.json` 为准，但读取正文只允许 `purpose="review"`，不提供 Coding 上下文、已恢复源码证据或原版 Source/Identity Guards，也不证明运行验证。Core Coding HOLD 不变。参数与读取预算见 [检索策略](../references/kb-retrieval.md)。

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
| 单份当前源码准备失败 | 核对输入是否为本版核验的 `760178 / build 26230496`、ZIP 是否完整及输出的必需范围/哈希要求；其他目标先做局部复核，旧版源码不是启动前提 |
| `auto` 报缓存损坏，或报告包升级降级审阅 | 缓存损坏仍须修复；包升级可先用已校验公开资料审阅，再按 [源码维护](source-compatibility.md) 局部复核新版源码 |
| 准备成功后仍只有两工具 | 重启 MCP 会话，工具集不会在已连接会话中自动切换 |
| MCP 已配置但无工具或查询失败 | 核对当前 Python、包路径、启动模式、准备状态、stderr 与客户端会话 |
| 网页 AI 无本地权限 | 提供必要材料；云端不能直接读取用户电脑的游戏和缓存 |

Version `v2026.10.27.1` includes the Skill, 210 registered public records, MCP and source preparation. Use one authorized `760178 / Steam build 26230496 scripts.zip`, then `mcp-config --mode full`; older source is not required. `source_epoch=759671` remains the evidence baseline, without relabeling historical claims or the new archive. Required core payload ranges stay strict. Mechanism research tracks exact file/range matches, range-only matches, changed/unknown or missing references; a research source gap does not block every other research record or grant Coding admission. Full mode needs Python 3.10+ and SQLite FTS5; verify nine tools and a real query in your client. Historical comparisons remain `metadata_only`. Restart connected catalog sessions after preparation. Default `auto` allows public review after manifest validation for missing preparation or PACKAGE_CHANGED; cache damage and untrusted public inputs remain errors. Restored Lua stays local. Source preparation and static checks do not prove game behavior; future archives, remote clients, visuals and audio require separate verification.
