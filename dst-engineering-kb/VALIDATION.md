# v0.1.1 验证边界与复核

执行 `python -B tools/validate.py`：检查 Schema、ID 唯一性、Index 一致性、Source 文件哈希、内部链接、typed relation 目标、Correction 目标、Manifest SHA256、Evidence 等级及 Runtime 状态。额外对比归档 v0.1 的正文与旧 SourceRef，去除允许的结构变化后应完全相同。

本公开副本只运行包内校验：`python -B tools/validate.py`。外部源码与原始报告均未随包，`--check-external` 不适用。冻结版历史校验结果保留为已脱敏的历史记录。

## 12 项反例回归

缺失字段、非法 status、无实机记录却标 E4、typed target 不存在、非法关系类型、Correction 目标缺失、推荐仅使用已撤回 Claim、Failure 虚标 runtime、Test 虚标执行成功、反向行号、FACT 缺直接 Klei 来源、单案例冒充 E2：均应被拒绝。

## 没有验证的事项

- 未运行 DST、Host/Client/Dedicated 测试；业务 Test Candidates 保持 not_run。
- 未重新分析参考 Mod；本机外部材料只做文件指纹比对。
- 未验证未附包的源码在其他机器上的内容、最新 Steam build 或跨版本 API。
- 未自动理解所有自然语言的隐含旧 Claim；显式 claim_id 以外仍需人工审核。
- 不宣称 Linux/macOS 实测；不同目录解压复核验证的是包内相对路径和无原路径依赖。
- 第三方通用 JSON Schema 验证器未运行；本包标准库检查器覆盖当前使用的约束。

原 v0.1 的 624 个链接与 8 项反例结果保存在 history/v0.1/data/validation.json。新版本因来源、Claim、typed relations 和文档增加，链接数会变化；应以本版实际执行输出核对，不能沿用旧数字。
