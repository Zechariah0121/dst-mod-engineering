# 维护与构建

当前工作版本 `v2026.11.13.4` 分发唯一 dst-mod-engineering.zip 与 SHA256SUMS.txt，302 条知识与 MCP 共用 knowledge/，机制族登记424项 API 合同。当前默认公共读取见[知识读取](knowledge-integration.md)，四条有限链的历史实现见[阶段 15](phase15-unified-chains.md)，用户入口见[README](../README.md)，来源维护见[专页](source-compatibility.md)。

```text
python -B -m unittest discover -s tests -v
python -B -m unittest discover -s dst-kb-service/tests -v
python -B -m unittest discover -s knowledge/tests -v
python -B scripts/build_release.py
python -B scripts/build_release.py --check
```

生成器核对 `knowledge/PACKAGE-MANIFEST.json` 的每个文件、FAMILY-REGISTRY 生成的目录计数（当前 64 + 13 + 110 + 115 = 302 个唯一记录）及单一证据环境，再从明确允许的文件构建 `dist/release/`。ZIP 内 `RELEASE-MANIFEST.json` 提供版本、记录计数和逐文件哈希。固定路径顺序、时间和 ZIP 元数据，并使用 DEFLATE 压缩。相同 Python 与压缩库下，同一源文件得到相同字节。跨压缩库比较时以包内逐文件哈希为准。`build_web_bundle.py` 是同一命令的兼容入口。

公开发行的冻结版 ZIP 保留了根目录的原始发行清单和来源记录。常规构建会重新生成清单，打包文件的内容与冻结版相同。

构建排除缓存、游戏源码、本地客户端配置、测试夹具、旧知识副本和构建产物。`dist/` 只放发行 ZIP 与校验文件，不复制源码树。不要把含本地恢复 Lua 的 `cache/` 提交或上传。已有生成物被修改或目录中有未知文件时，构建器拒绝覆盖；应先检查差异，或选择新的输出目录。

修改知识或证据必须保留事实、Scope、角色、类型、版本、更正与来源边界，重新绑定公开证据的真实哈希。来源槽必须由用户合法来源恢复；不能绕过原校验器或 Coding HOLD。更新来源另做版本差异维护，不能把历史证据改名为当前来源。

新研究的登记需绑定确切候选与独立审阅哈希，并核对来源引用与已有记录身份。构建后核对指南链接、实际登记 ID，以及 `MOD_EXAMPLES` 列出的自写 Lua 与实测示例的字节。示例数值用于演示。研究正文保持静态证据身份，游戏结果按测试的功能与环境分别记录。[本轮示例](phase16-effect-and-resource.md)

默认 auto 与 full 统一提供 11 工具公共发现和正文读取，无源码也可审阅；full 启动仍要求完整来源，显式 catalog 保留旧两工具。Coding、epoch 与证据操作保留原守卫。维护时兼顾原调用形状、Native AI Coding十字段/五条限制、Core与机制HOLD、四族完整对象、API消歧、总字节预算、失效cursor、来源缺口与更正，具体协议见[检索策略](../references/kb-retrieval.md#四族完整对象审阅)。

检索性能定位可使用仓库中的 `scripts/profile_retrieval.py`（维护脚本，不随运行包分发）。`--runtime-root` 选择来源准备返回的 `runtime_build` 目录，而非未恢复来源的公开包根；`--code-root` 选择待测实现，`--output` 保存隔离索引、计时及响应。先通过 `--help` 查看请求文件格式与选项，同一输入分别测基线和候选；全量追踪有额外开销，用户可见耗时另用 `--no-profile` 比较。优化需要同时核对返回内容、预算、权限与失效行为，不能用仅看文件时间戳的缓存代替内容完整性检查。

来源身份、逐引用状态与缺口处理统一见[源码维护](source-compatibility.md)。

知识正文有技术更正时，先用[作者维护入口](author-maintenance.md)列出受影响的声明和引用。对已有来源足以支撑的窄范围更正，可提交绑定具体记录和依赖的审阅决定，生成供读取、复核和构建的候选包。

目录/完整模式、错误处理与会话切换见[安装说明](install-and-use.md)。恢复缓存的隔离材料和准备锁均为本地维护状态，打包时排除 cache/。

发布前核对数据、协议、链接与逐文件清单，并按[验证记录](validation.md)报告游戏覆盖范围。
