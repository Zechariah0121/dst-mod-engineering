# 能力与版本限制 / Capabilities and limits

独立公开 Skill 提供工程工作方法、专题参考和三个 Python 辅助脚本；不提供完整 KB/MCP、游戏源码或第三方工具。可选 KB 以实际接入服务的版本、工具与记录范围为准，见 [接入说明](knowledge-integration.md)。

| 项目 | 实际边界 |
|---|---|
| 游戏版本 | 专题中标注的 `756039`、`759671` 等是保存源码快照。只适用于注明的函数、链路与条件；行号可能随更新变化，不代表全部专题已按同一版本复核 |
| Agent | 安装路径参考各产品官方文档；没有逐一完成所有产品、账户和云端环境的端到端安装测试 |
| 源码读取 | 需使用者提供合法可读的本地源码或必要片段；缺少材料时只能给出条件性判断 |
| 静态检查 | `check_api.py` 检查语法和部分直接方法声明，不能证明签名、时序、端别或运行结果 |
| 游戏测试 | `dst_modtest.py` 仅支持 Windows 离线单分片；不替代真实远端客户端、洞穴/跨分片、Mod 组合、UI/预测、视觉或音频验收 |
| 动画与音频 | 工具接口按安装版本确认；导出成功或无头专服通过不代表引擎解码与实际效果通过 |

具体 Mod 应分别记录实际源码版本、检查范围、测试环境与未测项。游戏更新后重新核对相关定义与调用链；历史样例、方法存在或单处调用不能直接推广为通用契约。验证方法见 [测试与交付](../references/testing-release.md)。

The standalone Skill provides guidance, references and three Python helpers. It does not supply the full KB/MCP, game source or third-party tools. Versioned notes describe bounded source snapshots, not blanket compatibility with the latest game. Agent installation paths follow official documentation; not every product, account or cloud environment has been tested end to end. Static declaration checks do not prove runtime behavior. The server helper is Windows-only and single-shard; real remote-client, cross-shard, UI, prediction, visual and audio behavior needs separate validation for each mod. Record the actual version, environment, evidence and untested scope.
