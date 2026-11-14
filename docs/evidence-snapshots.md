# 独立来源证据快照

`python -B -X utf8 prepare_sources.py --source <scripts.zip>` 保持原命令兼容。完整来源继续通过原水合、重绑定和校验流程建立 runtime；必需摘录失配时返回 `PARTIAL_EVIDENCE_PREPARED`，单独激活证据元数据，不启动或替换完整服务，不把模板 slots 送进服务。

快照在 `cache/evidence/snapshots/<sha256>.json`；内容先完整写入并核对，再原子替换 `cache/evidence/active.json`。旧快照和完整 runtime 均保留，失败的构建或激活不删除旧内容。该目录属于私有缓存，不发布。runtime 与证据有独立指针；证据快照从不宣称完整 runtime 已激活，完整运行入口继续核验自己的 manifest 与来源身份。

公共读取器调用 `dst_kb.evidence_snapshot.active_assessment(package_root)`。未激活返回 `None`；指针路径、内容哈希或 package 绑定错误抛出错误，不静默回退。返回 `snapshot_id`、`status`（`COMPLETE` / `PARTIAL`）、`sources`、逐条 `references`、待复核的 `affected_entry_ids` 及 `previous_comparison`。`COMPLETE` 仅表示所登记引用均恢复或匹配，不表示游戏运行验证。

引用状态：`EXACT_FILE_RANGE` 文件及范围匹配；`RANGE_ONLY` 原范围内容恢复但文件身份不同；`EXACT_FILE` 是 N001 仅文件哈希匹配，明确 `range_verified=false`；`CHANGED_UNKNOWN` 指定文件存在但内容无法恢复；`MISSING` 指定路径不存在；`UNKNOWN` 缺少可检查坐标、历史依赖 pointer 不可用，或尚无可执行来源检查覆盖该条目。机制引用沿用原验证器状态。范围恢复仍严格匹配原内容哈希；不将同名其他文件当作匹配。

依赖由目录 file/pointer、contract-map 显式 record ID、递归 artifact/pointer、N001 研究 map、机制条目的 `evidence_refs` 建立，不按关键词猜测。`unmapped_reference_ids` 明示无法归属条目的引用。无 slot 或 locator 检查覆盖的条目显式产生 `unassessed_registered_entry/UNKNOWN`；当前不少 Core 条目属于此类，不能把全局状态当作该条目已核对。新快照保留旧快照 ID、旧来源身份及引用状态变化。已有旧完整缓存的 `verified` 状态只属于旧来源，不能展示为新 partial 来源的验证结果。正文发现、阅读和原有三轴准入状态不由来源缺口改写。

ZIP 在全部源码读完后再核对整体哈希，期间改变会失败保旧。目录来源保留实际观察文件的哈希与逐引用结果，不宣称整个目录在同一时刻原子冻结。手动运行 `prepare_sources.py --source` 可独立激活 partial 证据快照；应读取实际准备状态与快照 ID，不将 partial 当作完整来源服务已替换。

单元验证：`python -B -m unittest discover -s tests -p test_evidence_snapshots.py`。使用真实水合与合成原始校验 stub，覆盖新安装 partial、旧完整缓存保留、原子替换失败、校验失败、篡改及 package 绑定；这不等于 DST 游戏运行测试。
