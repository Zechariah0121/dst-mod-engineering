# 安装与使用 / Installation and use

## 安装独立 Skill

从 [发行页](https://github.com/Zechariah0121/dst-mod-engineering/releases) 下载 `dst-mod-engineering.skill.zip` 并完整解压。目录应为 `dst-mod-engineering/SKILL.md`，同时保留 `references/`、`docs/`、`scripts/`、`templates/`、`requirements.txt` 与 `LICENSE`。`web-reading.zip` 只提供阅读材料，不是可安装的 Skill。不要只复制 `SKILL.md`。

选一个安装位置，每种产品的目标路径中都包含 `dst-mod-engineering/`：

| Agent | 项目安装位置 | 个人安装位置 | 调用 |
|---|---|---|---|
| Codex | `.agents/skills/dst-mod-engineering/` | `~/.agents/skills/dst-mod-engineering/` | `$dst-mod-engineering` 或技能选择器 |
| Claude Code | `.claude/skills/dst-mod-engineering/` | `~/.claude/skills/dst-mod-engineering/` | `/dst-mod-engineering` |
| Cursor | `.cursor/skills/dst-mod-engineering/` 或 `.agents/skills/dst-mod-engineering/` | `~/.cursor/skills/dst-mod-engineering/` 或 `~/.agents/skills/dst-mod-engineering/` | Agent 聊天中输入 `/` 并选择技能 |
| GitHub Copilot | `.github/skills/dst-mod-engineering/`；也支持 `.agents/skills/`、`.claude/skills/` | `~/.copilot/skills/dst-mod-engineering/` 或 `~/.agents/skills/dst-mod-engineering/` | 按所用界面选择或明确命名技能 |

`~` 是运行 Agent 的主机的用户目录。Windows 可用用户目录下的对应文件夹。以上位置来自各产品官方文档；官方来源、云端差异与能力要求见 [Agent 接入](../references/agent-setup.md)。

安装后刷新技能列表或重新开始会话，确认实际读取的 `SKILL.md` 路径和相关专题。未自动发现时，直接让 Agent 读取该文件的绝对路径。更新前比较同名目录，保存定制版；回退时恢复旧目录，并确认加载路径。

Download and fully extract the standalone Skill. Copy the complete `dst-mod-engineering/` directory to one supported project or personal location above. `~` means the home directory on the agent's host. Preserve custom copies, refresh discovery, and verify the loaded file and relevant references. Explicit file reading works when automatic discovery is unavailable.

## 提供 Mod 与当前源码

给 Agent 提供任务、Mod 根目录、实际游戏版本，以及自己合法安装的 DST 中的 `data/databundles/scripts.zip`。在 Skill 根目录运行：

```text
python -B scripts/dst_zip_tool.py --zip "<scripts.zip>" info
python -B scripts/dst_zip_tool.py --zip "<scripts.zip>" show scripts/components/combat.lua --start 1 --count 80
```

这两条命令只需 Python 3.10+ 标准库，不修改游戏。若要检查 Mod 的 Lua 语法和部分直接 API 调用，在自己的虚拟环境安装依赖后运行：

```text
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -B scripts/check_api.py "<Mod目录>" --zip "<scripts.zip>"
```

上例为 Windows；macOS/Linux 使用 `.venv/bin/python`。用实际路径替换占位符。`DECLARED` 只是查到声明，`NEEDS_REVIEW` 需要追踪源码；均不是运行正确性证明。隔离专服检查的 Windows 环境、参数与限制见 [测试与交付](../references/testing-release.md)。

Provide your task, mod root, actual game version and authorized `data/databundles/scripts.zip`. Run the first commands from the Skill root with Python 3.10+. The checker additionally needs `luaparser`; use a virtual environment and replace `.venv/Scripts/python` with `.venv/bin/python` on macOS/Linux. Declaration matches do not prove runtime correctness.

## 可选 KB 与故障排查

本独立 Skill 不包含完整 KB/MCP。已有服务时，按 [接入说明](knowledge-integration.md) 检查其实际工具、版本和一次查询结果；没有时说明 `KB unavailable`，继续本地源码工作。

| 现象 | 处理 |
|---|---|
| 找不到 Skill | 检查目录层级、发现位置和会话刷新；用绝对路径显式读取 |
| 只能读 README | 保留完整目录，读取 `SKILL.md` 及相关专题 |
| 找不到源码或组件 | 检查路径、实际游戏版本和 ZIP 成员，不静默换用旧源码 |
| 缺少 Python / luaparser | 确认实际解释器与所需依赖；准备方法见上文 |
| 网页 AI 无本地权限 | 按 [网页指南](../references/web-chat.md) 提供有权共享的必要材料 |
| MCP 已配置却无响应 | 在服务主机检查启动命令、解释器、路径、stderr 和客户端连接 |

This standalone Skill has no complete KB/MCP. Connect an existing authorized service only after checking its real tools, version and a query result. Otherwise report `KB unavailable` and continue source-based work.
