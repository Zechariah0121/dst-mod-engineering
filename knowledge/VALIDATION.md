# 187条统一知识库验证边界与复核

执行 `python -B tools/validate.py`：检查完整187条CATALOG的ID、file/pointer、标题、三轴状态与家族计数，检查三套知识Schema、Native证据引用的包内路径/哈希/JSON pointer，并保留基础64条的Index、Source、内部链接、typed relation、Correction、Evidence及Runtime检查。Manifest覆盖唯一knowledge目录。

基础64条正文、来源/Claim/关系注册表、旧Index与支持Schema通过 `data/legacy-integrity-baseline.json` 的SHA256核对；基线只存哈希，不复制旧知识正文。移除重复快照前，原v0.1与当前64条的独立 `semantic_migration_diff` 实跑为空；该结果作为历史比较记录，不宣称本次仍读取已删除的快照。历史数据与Schema可从Git历史恢复。

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

旧v0.1的链接与反例结果留在Git历史。当前实际检查数量以本次运行输出为准，不沿用历史数字。
