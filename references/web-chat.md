# 网页聊天中的 DST 开发

网页 AI 的能力取决于当前会话的文件、编辑与执行权限。资料上传成功不代表内容已完整读取；云端执行也不等于用户电脑上的 DST 已验证。

## 提供技能

| 方式 | 操作 |
|---|---|
| 平台支持原生技能导入 | 上传完整 `dst-mod-engineering/` 技能包并启用，确认 `SKILL.md` 和所需参考可读 |
| 普通附件或项目资料 | 提供 `SKILL.md`、当前任务相关专题、Mod 文件和必要原版片段 |
| 离线阅读 | 解压同一 `dst-mod-engineering.zip`，从 `references/` 与 `knowledge/` 选择任务所需文件 |

不支持 ZIP 解压时，上传相关文本文件。附上任务、期望行为、复现步骤、实际版本、运行端别和文件原相对路径；完整文件与截取范围要分清。无需上传整个游戏或私人存档。

Claude 的技能入口与账户要求见 [使用说明](https://support.claude.com/en/articles/12512180-use-skills-in-claude)，ZIP 顶层应为直接包含 `SKILL.md` 的 `dst-mod-engineering/`，见 [打包说明](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)。ChatGPT 可使用普通附件或 [Projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)；原生导入仅在账户提供相应入口时使用，见 [Skills 说明](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)。文件限制以 [上传说明](https://help.openai.com/en/articles/8555545-file-uploads-faq) 和当前界面为准。普通附件不是技能安装包，技能包也不是插件包。

## 按问题提供最少材料

| 问题 | 相关专题 | 首批项目材料 |
|---|---|---|
| 加载失败、崩溃 | [Lua 与 Hook](core-lua-hooks.md)、[实体与组件](entities-components.md) | 第一处错误与完整堆栈，相关入口、Prefab、组件与配置 |
| 主客机不一致、HUD | [网络与 RPC](networking-rpc.md)、[界面与动作](ui-actions-controls.md) | 两端代码、观察者身份、复现位置与日志 |
| Buff、死亡、读档 | [生命周期](lifecycle-save.md)、[战斗与 Buff](combat-buffs-containers.md) | 应用、移除、保存代码及复现顺序 |
| 贴图、动画、编译 | [图像与动画](assets-animation.md)、[工具安装](tool-bootstrap.md) | Lua 引用、文件清单、XML/SCML、必要样本及工具日志 |
| 制作、料理、植物 | [物品与料理](items-food-plants.md) | 配方、Prefab、组件、注册代码与配置 |
| 世界生成 | [世界生成](worldgen-spatial.md) | worldgen 入口、room/task/layout、种子与生成日志 |

核对原版时，先定位所需文件、函数与调用方，再从合法安装提供必要片段和版本依据。缺少初始化、端别或调用上下文时补齐；无法补齐时保留候选原因和成立条件。

同名附件可把路径编码为 `scripts__components__my_component.lua` 并说明映射。文本副本需注明原扩展名，执行前恢复正确路径。TEX、动画与压缩包仍需相应解析工具，改成 `.txt` 不会使二进制可读。

## 执行与本机交接

具备 Python 和完整输入的云端可做 [静态检查](testing-release.md)；依赖、编辑、联网下载与执行权限分别确认。仅有片段时记录检查范围。随附专服测试器需要 Windows DST 环境，不能访问用户电脑盘符的云端沙盒无法替用户运行。

缺少工具时按 [工具安装](tool-bootstrap.md) 提供作者来源、平台、最小依赖和样本验证方法。有本机执行连接且已获授权时继续；否则交付具体命令和输入，由本机执行者完成。

交付应包含：

- 修改文件相对于 Mod 根目录的路径，以及完整文件或补丁；注明所依据的版本，实际取得哈希时再记录哈希。
- 改动原因、已执行检查及证据、待本机验证项；静态、模拟、专服与真实客户端结果分别说明。
- 在目标副本应用前的差异核对和冲突处理；云端产物不会自动同步到运行副本或 Workshop。

本机回传实际加载副本、配置、复现步骤、完整堆栈、日志或截图，以及未测项；可用 [验证结果清单](../templates/local-validation.md) 记录。日志中的令牌、密码和无关私人内容用占位符替换。证据等级见 [测试与交付](testing-release.md)。
