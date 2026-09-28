# dst-mod-engineering

面向《饥荒联机版》（Don't Starve Together）的中文 AI 开发技能，覆盖功能开发、代码审查、崩溃排错、联机、存档和资源制作。

[![Checks](https://github.com/Zechariah0121/dst-mod-engineering/actions/workflows/ci.yml/badge.svg)](https://github.com/Zechariah0121/dst-mod-engineering/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 快速开始

| 使用方式 | 入口 |
|---|---|
| Codex、Claude Code、Cursor 等 Agent | 下载仓库，按 [接入指南](references/agent-setup.md) 安装并加载 `SKILL.md` |
| 网页 AI | 上传 [技能 ZIP](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/dst-mod-engineering.skill.zip)，或使用下方专题 Markdown |
| 阅读工程知识 | [知识库索引](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-engineering-kb/INDEX.md) |
| 为 Agent 启用知识检索 | [MCP 服务接入](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/dst-kb-service/README.md) |
| 获取全部内容 | [完整仓库 ZIP](https://github.com/Zechariah0121/dst-mod-engineering/archive/refs/heads/main.zip) |

不支持自动发现技能的 Agent，也可以直接使用：

> 请读取 `dst-mod-engineering/SKILL.md`，按相关专题处理我的 DST Mod 任务。先核对当前原版源码，再实现或修复；玩法取舍先确认，分别报告静态检查和实际游戏测试结果。

技能 ZIP 包含使用指南和开发辅助脚本；知识库与 MCP 服务需下载完整仓库。普通网页附件是否能解压、注册技能，取决于平台能力，详见 [网页使用指南](references/web-chat.md)。

## Skill 与知识库

Skill 负责开发流程和按需导航；知识库提供可追溯的事实、模式、反例与测试候选；可选 MCP 服务负责检索。设计、实现、审查和排错使用不同的检索重点，简单机械修改不必重复查询。

知识库 v0.1.1 包含 **64 条条目**，来自一个参考案例及限定的原版源码快照。模式和规则仍是候选，11 项游戏测试候选尚未执行。使用时仍须核对当前项目和游戏版本。具体任务示例见 [知识库使用说明](docs/knowledge-integration.md)。

## 网页阅读资料

通常选择与任务相关的一份即可：

| 任务 | 下载 |
|---|---|
| 初次使用 | [入门](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-starter.md) |
| 代码审查与修复 | [代码专题](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-code-review.md) |
| 联机、存档与 UI | [联机专题](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-networking.md) |
| 贴图、动画与音频 | [资源专题](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-assets.md) |
| 世界生成 | [世界生成专题](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-worldgen.md) |
| 全部专题 | [阅读 ZIP](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-reading.zip) · [完整 Markdown](https://github.com/Zechariah0121/dst-mod-engineering/raw/refs/heads/main/dist/web/web-full.md) |

## 开发工具

| 工具 | 用途 |
|---|---|
| `scripts/dst_zip_tool.py` | 检索游戏安装目录中的 `scripts.zip` |
| `scripts/check_api.py` | Lua 语法及组件／Replica 方法声明检查 |
| `scripts/dst_modtest.py` | Windows 隔离专服测试，记录加载与行为断言结果 |

脚本需要 Python 3.10+；语法检查器还需 `luaparser`，可用 `python -m pip install -r requirements.txt` 安装。参数通过各脚本的 `--help` 查看，操作示例及限制见 [测试与交付](references/testing-release.md)。静态检查和专服测试不能替代真实客户端的 UI、预测、画面与音频验收。

动画与音频工具按任务选择，见 [工具安装](references/tool-bootstrap.md)、[动画制作](references/assets-animation.md) 和 [音频制作](references/audio-particles.md)。

## 来源与许可

仓库自有文档和脚本采用 [MIT](LICENSE)。参考案例“小穹”的作者为 FL；研究引用不代表其背书，也不重新授权原 Mod。游戏、Mod 源码和素材未随本仓库分发，其权利仍归原权利人。资料来源见 [来源说明](references/sources-and-corrections.md)，知识证据与版本限制见知识库各条目。

需要贡献内容或重建发布包时，阅读 [维护指南](https://github.com/Zechariah0121/dst-mod-engineering/blob/main/docs/maintainers.md)。
