# Skill 驱动的源码更新

在实质性设计、实现、审查、排错或研究查库前，由 Agent 从实际使用的包根调用助手。它检查并适配可恢复的来源；变化部分由 AI 按当前任务核对，不保证任意更新全自动兼容。仅使用已明确、合法持有的来源，不自动下载或搜索其他游戏安装。

## 首次绑定与后续检查

需要 Python 3.10+。任务已经给出 `scripts.zip` 时首次执行：

```text
python -B -X utf8 run_kb.py update-sources ensure --source "<已明确的scripts.zip绝对路径>"
```

后续任务使用同一包的已记忆绑定：

```text
python -B -X utf8 run_kb.py update-sources ensure
python -B -X utf8 run_kb.py update-sources status
```

`status` 只查看绑定与上次尝试，不代替 `ensure` 检查当前 ZIP。未绑定、路径不可用或任务明确换了安装时，先确认实际目标；用新的明确 `--source` 更新绑定。不要从旧聊天路径猜测，不为没有本地文件权限的网页或云端会话伪造检查成功。

助手记住来源位置并核对来源、包和助手版本。相同输入已成功时返回 `UNCHANGED`，仍进行必要的哈希与完整性检查；相同失败或中断输入返回 `RETRY_SUPPRESSED`，避免每次查库重复重建。只有原因已处理、且确有重试需要时显式运行一次 `ensure --retry`；失败不原样循环。

绑定、状态和本地复核结果位于 `cache/source-update/`，恢复构建位于 `cache/runtime/`。这些内容含本机路径或游戏来源，只留本地，不放入公开包。助手不改游戏、存档、客户端配置、知识正文或已连接进程；不由 `serve` 隐式调用。

## 成功后的连接验证

`PREPARED` 表示严格准备成功；新准备改变激活时，按 `reconnect_required` 重连。`UNCHANGED` 表示匹配输入的有效准备未变，不要求每次重连；当前会话已核验相同来源时可直接继续。它们均不表示游戏实测。

需要重连时，重连后在客户端实际检查完整模式九工具、执行一次任务相关查询，并核对返回的 `source_input_assessment` 与实际 ZIP 哈希。`UNCHANGED` 时若当前连接来源尚未核验，也先检查实际响应，不由助手快返推断会话身份。服务环境 `source_epoch=759671` 保留历史运行环境；原子仍各自保留 759671 或 760944 等证据身份，不改标全库。新准备要求重连而尚未完成时，只能如实报告“来源已准备，当前连接未验证”。助手不会替用户重启会话。

若返回 `INPUT_CHANGED_AFTER_PREPARATION`，来源或包在准备后又变了；不要把该快照当作当前输入，重新核对并再运行 `ensure`。工具列表、缓存或配置打印成功不能代替实际查询。

## 来源变化时继续当前任务

`SOURCE_REVIEW_REQUIRED` / `SOURCE_GAP` 不是要求停用知识库或等待作者更新。核心范围不能恢复时，不激活部分构建；旧有效缓存若保留，只代表旧输入。先确认本次目标 ZIP 与返回的来源哈希，读取失败信息中的 `source_gaps` 和可用的局部复核结果，定位与当前任务有关的文件及范围。

选择任务中已知的实际符号，不猜造缺失 symbol：

```text
python -B -X utf8 run_kb.py maintain-sources locate --target "<当前scripts.zip>" --symbol "<任务中的实际符号>" --source-file scripts/components/example.lua
```

若原文件缺失或限定文件后零命中，去掉 `--source-file` 在同一明确 ZIP 中寻找搬迁位置。定位只是线索；再读取命中源码及必要上下文：

```text
python -B scripts/dst_zip_tool.py --zip "<当前scripts.zip>" show scripts/components/example.lua --start 1 --count 80
```

将文件、行号和读取范围替换为实际命中结果，追踪定义、消费者、端别、初始化、退出和保存链路。不能由同名符号、相同范围或 locator 命中直接推导行为兼容。

当前源码的新结论独立记录目标 ZIP 哈希、文件/范围、任务条件与未验证部分；不冒充历史 KB 已有证据，不写回 canonical。旧知识按原 Scope、版本、更正和 HOLD 继续审阅；公开清单有效时可用目录与 `purpose="review"` 读取，Coding 准入不改变。无法核实的部分保留未知，并说明对本次任务的影响。

`PREPARATION_FAILED`、来源不可用、缓存损坏或公开清单失配须分别按错误处理；不把完整性错误包装成正常目录降级。缺少可信知识输入时仍可独立核对明确的当前源码，但不能声称已完成查库或来源准备。手动准备、批量评估与回退边界见 [源码维护](../docs/source-compatibility.md)。
