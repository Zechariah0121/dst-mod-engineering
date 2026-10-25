# Agent 安装与能力

本技能采用 [Agent Skills 格式](https://agentskills.io/specification)。完整安装步骤与路径表见 [安装与使用](../docs/install-and-use.md)；下面的官方资料用于核对各产品当前入口。技能可被发现、脚本可执行与 DST 功能通过验收是不同结果。

## 官方入口

| Agent | 官方说明 | 加载后确认 |
|---|---|---|
| Codex | [Build skills](https://learn.chatgpt.com/docs/build-skills) | 用 `$dst-mod-engineering` 或技能选择器，核对实际文件路径 |
| Claude Code | [Skills](https://code.claude.com/docs/en/skills) | 用 `/dst-mod-engineering`；同名个人/项目技能需核对来源 |
| Cursor | [Agent Skills](https://cursor.com/docs/skills) | 在 Agent 聊天的 `/` 菜单选择，或到 Customize → Skills 查看 |
| GitHub Copilot | [安装技能](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)、[CLI 技能](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills) | 使用所用界面的技能入口；CLI 命令不套用到其他界面 |

让 Agent 确认实际读到的 `SKILL.md` 和当前任务相关参考。没有 Skills 自动发现能力时，提供其绝对路径并显式读取即可。只有对话文本、没有文件访问时，使用 [网页附件方式](web-chat.md)。本 Skill 未逐一完成所有产品的端到端安装与执行测试。

## 本地与云端

安装路径属于运行 Agent 的主机。云端工作区不能直接读取用户电脑上的 DST、Mod 或工具：

- Claude 的本地个人技能不会自动成为 Cowork/云端会话技能；按 [官方云端说明](https://code.claude.com/docs/en/skills#use-skills-in-cowork-and-cloud-sessions) 使用账户技能或该环境支持的部署方式。
- Cursor 的个人技能同步需另行启用，且只同步其支持的位置；项目技能与远端工作区也要实际可读。见 [官方同步说明](https://cursor.com/docs/skills#use-personal-skills-with-cloud-agents)。

## 按任务确认能力

| 能力 | 可完成的工作 | 缺少时 |
|---|---|---|
| 读写、检索文件 | 读取 Skill、Mod 和原版源码，修改授权项目 | 仅分析已提供片段或交付补丁 |
| 终端与进程权限 | 运行 Python、资源工具与定向测试 | 提供命令，运行结果保持未验证 |
| 网络读取 | 核对官方文档、版本和工具来源 | 使用已有材料并注明版本未联网核对 |
| Windows DST 环境 | 运行随附隔离专服测试器 | Linux/云端不因此具备本机游戏测试能力 |
| 图像、音频、GUI 与真实客户端 | 检查动画、HUD、输入、声音与联机效果 | 由具备相应能力的执行者验收 |

脚本入口可用 `python scripts/<脚本名>.py --help` 检查。帮助成功只证明入口可运行，不证明依赖齐全或游戏功能通过。Python、`luaparser` 和素材工具按任务准备，见 [环境发现](environment-tools.md)、[工具安装](tool-bootstrap.md) 与 [测试](testing-release.md)。
