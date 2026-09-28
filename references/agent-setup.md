# 不同 Agent 的安装、调用与能力边界

官方文档核验日期：**2026-09-27**。下述发现路径和调用方式来自官方文档；本次未实际执行这些安装命令，也没有在 Claude Code、Cursor 或 GitHub Copilot 中实测本技能。格式受支持、技能被加载、脚本能执行、DST 功能验收通过，是四件不同的事。

本仓库采用带 `name`、`description` 的 `SKILL.md`，配套 `references/` 和 `scripts/`，符合 [Agent Skills 公开格式](https://agentskills.io/specification) 的组织方式。安装时保留完整目录，不能只复制入口；产品仍需有权读取相关文件，运行脚本时还需相应环境。标准不保证所有 Agent 的发现路径、命令和权限行为一致。

## 放在哪里、怎样调用

下表中的 `~` 表示运行 Agent 的那台机器上的用户目录；项目路径相对于当前项目根目录。每个目录下再放一个完整的 `dst-mod-engineering/` 文件夹。

| Agent | 项目级技能目录 | 个人技能目录 | 明确调用或确认加载 |
|---|---|---|---|
| Codex | `.agents/skills/` | `~/.agents/skills/` | CLI / IDE 中用 `$dst-mod-engineering`，或通过 `/skills` 选择。见 [OpenAI 文档](https://learn.chatgpt.com/docs/build-skills)。 |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` | 输入 `/dst-mod-engineering`。见 [Claude Code 文档](https://code.claude.com/docs/en/skills)。 |
| Cursor | `.cursor/skills/`，也支持 `.agents/skills/` | `~/.cursor/skills/`，也支持 `~/.agents/skills/` | 在 Agent 聊天中输入 `/` 并选技能；该调用附着于当前消息。见 [Cursor 文档](https://cursor.com/docs/skills)。 |
| GitHub Copilot | `.github/skills/`，也支持 `.agents/skills/`、`.claude/skills/` | `~/.copilot/skills/`，也支持 `~/.agents/skills/` | CLI 可在提示中写 `/dst-mod-engineering`；其他界面用明确命名的请求，并确认实际读取的文件。见 [Copilot 安装说明](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) 和 [CLI 调用说明](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)。 |

优先选一个安装位置，避免同名副本漂移。已有技能能被当前版本识别时，先查实际来源再决定是否迁移；本指南不会自动移动旧目录、覆盖配置或关闭产品的权限检查。表中 Codex 路径采用当前官方文档，不把某个历史安装中的 `.codex/skills/` 当成所有用户的默认路径。

个人目录不等于云端目录。Claude Code 的本地个人技能不会由该路径直接进入云端会话；Cursor 的本地技能也需要它支持的同步或远端部署方式。项目技能要实际存在于远端工作区才可用。见 [Claude Code 云端范围](https://code.claude.com/docs/en/skills#use-skills-in-cowork-and-cloud-sessions) 与 [Cursor 云端范围](https://cursor.com/help/customization/skills#are-user-level-skills-available-on-cloud-agents-and-remote-workers)。技能同步不会安装 DST，也不会给予云端访问本机游戏目录的能力。

## 首次安装示例

不需要为安装技能专门安装 Git。没有 Git 时，打开 [本仓库](https://github.com/Zechariah0121/dst-mod-engineering)，选择 **Code → Download ZIP**；也可用 Agent 已有的文件下载能力取得同一仓库的源码压缩包。该流程见 [GitHub 官方说明](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives)。

将压缩包解压到新的临时目录，找到**直接包含 `SKILL.md` 的那一层**（下载时通常带分支名后缀），将这一层目录命名为 `dst-mod-engineering`，再复制到上表选定的技能父目录。复制前确认目标不存在，避免覆盖已有技能。最终结构应是 `<技能父目录>/dst-mod-engineering/SKILL.md`，而不是在 `dst-mod-engineering` 里又套一层 `dst-mod-engineering-main`。保留其参考文档、脚本、依赖说明和许可证。

已有 Git 时也可使用以下首次安装命令；目标已存在即停止，先比较已有内容。命令不会更新、覆盖或删除旧技能，也不安装软件。

Windows PowerShell 示例默认采用 Codex 的个人目录。使用其他 Agent 时，只修改 `$skillParent` 的末段：Claude Code 用 `.claude/skills`，Cursor 用 `.cursor/skills`，Copilot 用 `.copilot/skills`。

```powershell
$skillParent = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.agents/skills'
$skillTarget = Join-Path $skillParent 'dst-mod-engineering'
if (Test-Path -LiteralPath $skillTarget) {
    throw "目标已存在，请先核对已有技能：$skillTarget"
}
Get-Command git -ErrorAction Stop | Out-Null
New-Item -ItemType Directory -Path $skillParent -Force | Out-Null
git clone -- https://github.com/Zechariah0121/dst-mod-engineering.git $skillTarget
if ($LASTEXITCODE -ne 0) { throw '克隆失败；检查原因，不要覆盖重试。' }
foreach ($relative in @('SKILL.md', 'references', 'scripts', 'docs', 'requirements.txt', 'LICENSE')) {
    if (-not (Test-Path -LiteralPath (Join-Path $skillTarget $relative))) {
        throw "技能内容缺失：$relative"
    }
}
Get-Content -LiteralPath (Join-Path $skillTarget 'SKILL.md') -TotalCount 8
```

macOS / Linux 的 Bash 或 Zsh 示例同样默认采用 `.agents/skills`；按上表修改 `skill_parent` 即可。此处允许安装和阅读技能，不表示随附专服启动器支持这些平台。

```sh
(
    set -eu
    skill_parent="$HOME/.agents/skills"
    skill_target="$skill_parent/dst-mod-engineering"
    if [ -e "$skill_target" ] || [ -L "$skill_target" ]; then
        printf '%s\n' "目标已存在，请先核对已有技能：$skill_target" >&2
        exit 1
    fi
    command -v git >/dev/null
    mkdir -p "$skill_parent"
    git clone -- https://github.com/Zechariah0121/dst-mod-engineering.git "$skill_target"
    test -f "$skill_target/SKILL.md"
    test -d "$skill_target/references"
    test -d "$skill_target/scripts"
    test -d "$skill_target/docs"
    test -f "$skill_target/requirements.txt"
    test -f "$skill_target/LICENSE"
)
```

也可把已经取得的完整目录复制到所选位置，保留 `SKILL.md`、`references/`、`scripts/`、`docs/`、依赖说明和许可证。项目级安装如果需要随项目提交，可复制普通文件；不要把另一个仓库的 `.git` 目录作为普通文件一起提交。没有明确的共享需求时无需修改项目配置文件。

## 最小读入检查

先让 Agent 只读检查，不启动游戏、不安装依赖、不编辑 Mod：

> 使用 dst-mod-engineering。先报告你实际读取的 SKILL.md 路径，再读取 references/environment-tools.md 和 references/testing-release.md，说明三个辅助脚本各自能验证什么、不能验证什么。列出当前环境已找到和缺少的工具，但先不要安装、编译或运行游戏。

根据产品确认技能被发现：

- Codex：从技能选择器选中；更新后仍看不到时重启会话。自动匹配依赖任务与描述，不能把没自动触发解释为文件必然无效。[官方加载说明](https://learn.chatgpt.com/docs/build-skills)
- Claude Code：使用上表的 `/dst-mod-engineering`，核对实际来源路径，避免同名个人/项目技能混淆。[官方技能说明](https://code.claude.com/docs/en/skills)
- Cursor：在 `/` 菜单选择技能，也可到 Customize → Skills 查看已发现的条目。[官方技能说明](https://cursor.com/docs/skills)
- Copilot CLI：已启动会话可用 `/skills reload`，再用 `/skills info dst-mod-engineering` 确认位置；其他 Copilot 界面不照搬 CLI 命令。[官方 CLI 说明](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)

技能被发现后，还要验证它确实读到了参考文件。合格的只读结果应能区分声明检查、服务器行为和真实客户端验收，并指出专服测试器只支持 Windows。它自述“已加载技能”本身不够，结合产品的读取记录和文件路径核对。

若要进一步检查脚本入口，在技能根目录、已有合适 Python 的前提下，分别执行 `python scripts/dst_zip_tool.py --help`、`python scripts/check_api.py --help` 和 `python scripts/dst_modtest.py --help`；`python` 应替换为已确认的解释器路径。帮助成功只证明命令入口可运行；`check_api.py --help` 不会验证 `luaparser` 已安装，游戏测试也还没有发生。依赖准备与真实命令见 [环境与工具准备](environment-tools.md) 和 [测试与交付](testing-release.md)。

## 没有 Skills 自动加载的 Agent

只用网页聊天、只能上传附件，或需要原生技能 ZIP 时，使用 [网页使用指南](web-chat.md) 和仓库提供的自动生成资料包；下面的本地路径方式仅适用于实际能读取该路径的 Agent。

只要能够读取工作区文件，也可以显式使用本技能。把完整目录放在它可访问的位置，然后发送下列请求，并将路径换成实际位置：

> 请先读取 `<技能绝对目录>/SKILL.md`，按当前任务读取其中链接的参考文件。脚本和文档的相对路径以技能目录为准；待修改的 Mod 是 `<Mod 绝对目录>`。以当前原版源码为依据完成任务，区分确定故障与玩法选择，并说明实际执行了哪些验证。不要因未注册 Skills 就跳过该目录，也不要只读 README 代替技能入口。

这里的“完整目录”指文件可访问，不是每轮把所有参考文档一次塞进上下文。不能读取本地文件的聊天工具需要用户提供相关材料；它只能分析实际收到的内容，不能声称检查了未提供的源码、运行了本地脚本或进入游戏验收。上传后的材料读取确认、按需补充及本机结果回传，按 [网页流程](web-chat.md) 执行。

## 按任务准备能力

| 能力 | 可完成的工作 | 缺少时的实际边界 |
|---|---|---|
| 读取和检索文件 | 读技能、追踪 Mod 与合法安装的原版源码 | 只有对话文本时，只能讨论已提供的片段 |
| 编辑文件 | 修改已授权的项目并生成报告 | 只能提供补丁建议，由使用者应用 |
| 终端 / 进程执行 | 执行 Python、资源工具和定向测试 | 可以审查命令与代码，不能报告“运行通过” |
| 网络读取 | 获取本仓库、核对官方文档与版本、取得所需工具 | 已有完整本地材料仍可使用；未联网核对的版本明确标注 |
| Windows 本地游戏环境与进程权限 | 运行随附 `dst_modtest.py`，写唯一测试副本和隔离存档 | Linux CI、云端推理或另一品牌 Agent 不会自动具备该环境 |
| 查看图像、试听音频、操作 GUI 与真实客户端 | 检查动画、输入、HUD、声音和实际联机效果；需要时由用户参与 | 导出文件或专服日志不能代替画面、听感和多人验收 |

这些是能力要求，不指定任何 Agent 独有工具名。读取参考文档不要求拥有 GUI；服务器行为测试也不因换用 Claude、Cursor 或 Copilot 就失效，关键是执行它的主机、游戏版本、权限和依赖。没有相应能力时完成可验证部分并列出待验项，不能用产品名称代替证据。

安装技能不会自动安装 Python、`luaparser`、DST、DMT、ktools 或 FMOD。新增工具只按当前任务需要准备；先检查已有工具与版本，再按用户授权安装，配置和验收方法见 [缺失工具的准备与安装](tool-bootstrap.md)。历史游戏实测与产品适配声明的边界见 [验证记录](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/validation.md)。
